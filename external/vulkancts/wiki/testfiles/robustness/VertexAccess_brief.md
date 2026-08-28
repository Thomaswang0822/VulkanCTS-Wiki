# Understanding Brief: `robustness.vertex_access`

## One-Sentence Test Purpose

This test checks whether robust vertex input fetches preserve in-range attributes and return only permitted values when vertex-rate or instance-rate fetches extend beyond a bound vertex buffer.

## Background Knowledge

### Vertex input addressing

A graphics pipeline maps shader input locations to vertex input bindings. Each binding supplies a stride and an input rate. `VK_VERTEX_INPUT_RATE_VERTEX` selects an element from the vertex index, while `VK_VERTEX_INPUT_RATE_INSTANCE` selects one from the instance index. An attribute description adds a format and a byte offset within that element.

Why it matters here:
- Locations 0 and 1 share one vertex-rate binding, so one invocation fetches two adjacent attributes from the same record.
- Location 2 uses an instance-rate binding, which lets the same shader expose out-of-range instance fetches.
- The selected `VkFormat` determines component count, conversion, and the permitted four-component fallback pattern.

### Robust vertex input reads

When `robustBufferAccess` applies, vertex input reads are checked against the bound vertex buffer range. An out-of-range read may return a value from the memory range bound to that buffer, zero, or the permitted `(0,0,0,x)` pattern for a four-component result. If one vertex input read is out of range, other reads through the same binding in the same invocation may also behave as out of range.

Why it matters here:
- An out-of-range result is not required to be one fixed zero value.
- In-range fetches must still match the populated input data unless the same-binding rule permits them to be treated as out of range.
- The host checker must account for input format conversion, including packed normalized values.

## One Concrete Example

Consider `dEQP-VK.robustness.vertex_access.r32_uint.draw.vertex_out_of_bounds`.

- Binding 0 contains six vertex records. Each record has two `uint` attributes at locations 0 and 1.
- The draw requests nine vertices, so the final three vertex indices address records beyond the logical vertex buffer range.
- Binding 1 supplies one in-range instance-rate `uint` at location 2.
- Binding 2 supplies a separate `vertexNum` value used only to place each invocation's observations in the output buffer.
- The vertex shader writes all three fetched attributes into a storage buffer. It does not use them to position geometry; `gl_Position` is fixed.
- The host expects exact populated values for in-range fetches. For out-of-range fetches it accepts the values permitted by robust vertex input semantics.

## End-to-End Test Flow

```text
[host] select one input format, draw mode, and behavior leaf
[host] create a dedicated device with robustBufferAccess enabled
[host] generate the format-specific vertex shader and fixed fragment shader
[host] create and populate vertex-rate, instance-rate, vertex-number, optional index, and output buffers
[host] build a graphics pipeline with two tested attribute bindings plus the vertex-number binding
[host] record vkCmdDraw or vkCmdDrawIndexed inside a render pass
[host] initialize the vertex-number buffer so each executed invocation selects its output slot
[host] submit the command buffer and wait for its fence
[device] fetch vertex and instance attributes, including deliberately out-of-range fetches
[device] write the fetched scalar components to the storage output buffer
[host] invalidate the output allocation and classify each observed scalar as in-range or out-of-range
[host] compare in-range values exactly and check out-of-range values against the permitted robust results
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `VertexAccessTest::initPrograms()` emits a vertex shader whose input scalar or vector type follows the selected `VkFormat`.
- The generator declares three tested attributes: locations 0 and 1 use the selected format through the vertex-rate binding, and location 2 uses that format through the instance-rate binding.
- Location 3 is a fixed `int vertexNum` input. It controls the output index and is not one of the robustness results being judged.
- The output SSBO element type is `uint`, `int`, `float`, `uint64_t`, or `int64_t` according to the format. The array size follows vertex count, instance count, channel count, and the three tested attributes.
- The fragment shader writes constant white. The test does not read the color attachment to decide pass or fail.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Vertex-rate buffer, binding 0 | yes | yes | read | host retains mapped input for comparison | Holds two adjacent attributes per vertex and is deliberately too short for some fetches. |
| Instance-rate buffer, binding 1 | yes | yes | read | host retains mapped input for comparison | Holds location 2 and is deliberately too short in `instance_out_of_bounds`. |
| Vertex-number buffer, binding 2 | yes | yes | read | no | Maps executed vertices, including indexed vertices, to stable output slots. |
| Index buffer | yes for `draw_indexed` | yes for `draw_indexed` | read | no | Selects valid and deliberately large vertex indices. |
| Output storage buffer, descriptor set 0 binding 0 | yes | yes | written by vertex shader | yes | Captures every fetched scalar for the actual verdict. |
| Color attachment | yes | yes | written by the graphics pipeline | no | Provides a valid render-pass target; its pixels are not the validation result. |

## What Is Checked

- Every output scalar is mapped back to one of the three shader attributes and to its expected vertex-rate or instance-rate source index.
- An in-range result must equal the populated source value after the selected format's input extraction. Integer, floating-point, 64-bit, and packed `A2B10G10R10_UNORM_PACK32` values have format-specific checks.
- An out-of-range result may be zero or a value found within the memory range bound to the relevant vertex buffer. A four-component result may also match `(0,0,0,x)`, with the permitted `x` value for the component type.
- The checker accounts for an incomplete multi-component attribute and for the rule that another read through the same binding in the same invocation may behave as out of range.
- The case passes only when every scalar written to the output buffer meets the applicable rule.

## Behavior Parameter Identification

> **Behavior parameter:** test case leaf
>
> **Candidate values:** `vertex_out_of_bounds`, `vertex_incomplete`, `instance_out_of_bounds`, `last_index_out_of_bounds`, `indices_out_of_bounds`, `triangle_out_of_bounds`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `vertex_out_of_bounds` | Incorrect robust handling when sequential non-indexed vertex fetches pass the end of the vertex-rate buffer. |
| `vertex_incomplete` | Incorrect bounds handling or input extraction when only part of a vertex record or attribute is available. |
| `instance_out_of_bounds` | Incorrect robust handling of instance-rate attributes when later instances exceed the instance buffer. |
| `last_index_out_of_bounds` | Incorrect robust indexed fetch behavior when the final submitted index selects a vertex outside the vertex-rate buffer. |
| `indices_out_of_bounds` | Incorrect robust indexed fetch behavior for several noncontiguous out-of-range indices mixed with valid indices. |
| `triangle_out_of_bounds` | Incorrect robust indexed fetch behavior when one complete primitive uses out-of-range vertex indices. |

All six values can also expose incorrect vertex format conversion, shader capture, or host classification for the selected format.

## Important Variations and Special Cases

- The matrix repeats every behavior leaf for 15 formats: 32-bit scalar and vector unsigned, signed, and floating-point formats; two 64-bit scalar integer formats; and `a2b10g10r10_unorm_pack32`.
- `draw` changes buffer length, vertex count, or instance count. `draw_indexed` keeps one instance and uses explicit index patterns containing `100`, `101`, and `102`.
- `vertex_incomplete` is different from merely selecting a later missing record. The buffer contains only half of the two-attribute vertex record, so the boundary can split the logical fetch set.
- The packed normalized format needs a dedicated host comparison because one packed 32-bit word becomes four floating-point shader components.
- The 64-bit cases use GLSL 4.40 with `GL_EXT_shader_explicit_arithmetic_types_int64`; the source also requires `VK_EXT_shader_image_atomic_int64` and vertex-buffer format support before running them.
- The vertex stage must support storage writes because the test records fetched attributes in an SSBO.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Shader generation | [`VertexAccessTest::initPrograms()`](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L263-L366) | Generates format-specific inputs and writes the fetched values to the output SSBO. |
| Indexed patterns | [`DrawIndexedAccessTest::s_indexConfigs`](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L421-L435) | Defines the three arrangements of valid and out-of-range indices. |
| Vertex input and resources | [`VertexAccessInstance`](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L493-L800) | Creates bindings, attributes, buffers, the descriptor, and draw configuration. |
| Submission and verdict | [`iterate()` and `verifyResult()`](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L806-L1003) | Runs the draw, reads the SSBO, and applies the robust-value rules. |
| Format-sensitive checks | [`isValueWithinVertexBufferOrZero()` and `isExpectedValueFromVertexBuffer()`](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L1005-L1097) | Handles packed, integer, float, and 64-bit comparisons. |
| Non-indexed registration | [`createDrawTests()`](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L1190-L1225) | Defines the three direct-draw behavior leaves. |
| Indexed registration | [`createDrawIndexedTests()`](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L1227-L1256) | Defines the three indexed behavior leaves. |
| Format matrix and test family root | [`addVertexFormatTests()` and `createVertexAccessTests()`](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L1258-L1297) | Registers 15 format children under `robustness.vertex_access`. |
| Robust buffer semantics | [Vulkan specification: Robust Buffer Access](../../../../vulkan-docs/src/chapters/shaders.adoc#L1925-L2030) | Defines bounds and permitted results for robust vertex input reads. |
| Vertex input state | [Vulkan specification: Vertex Input Description](../../../../vulkan-docs/src/chapters/fxvertex.adoc#L257-L409) | Defines binding stride, input rate, attribute format, and attribute offset. |
| Mustpass inventory | [`robustness.txt`](../../../mustpass/main/vk-default/robustness.txt#L96874-L96963) | Confirms 90 leaves: 15 formats, two draw modes, and three leaves per mode. |

## Questions / Risk Points for User Audit

- Is the distinction between the vertex-rate robustness input and the separate `vertexNum` bookkeeping input clear?
- Is it clear that the color attachment is not read for the verdict?
- Does the explanation of permitted out-of-range values avoid implying that zero is the only valid result?
- Is `test case leaf` the right behavioral axis for comparing the six failure mechanisms?
- Does the same-binding allowance for locations 0 and 1 need more detail in the final page?

No unresolved source ambiguity affects the selected walkthrough, behavior parameter, or pass/fail description.

## Conversion Notes for Final Wiki Rewrite

- Use `dEQP-VK.robustness.vertex_access.r32_uint.draw.vertex_out_of_bounds` for the representative shader walkthrough. It shows both adjacent vertex-rate attributes, the instance-rate attribute, and the output SSBO without 64-bit or packed-format syntax obscuring the mechanism.
- Keep vertex input addressing and robust-read result choices as short Background Knowledge bullets.
- Put the six registered leaves under `Behavior Parameters`; keep the 15 formats and two draw modes in the parameter table.
- Copy the `### Failure Cause Mapping` table unchanged into the final page.
- Explain the color attachment only as graphics setup, and state that the output SSBO supplies the verdict.
- Move source navigation to the final appendix.
