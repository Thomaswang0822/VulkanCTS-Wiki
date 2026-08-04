# Understanding Brief: `pipeline.monolithic.dynamic_vertex_attribute`

## One-sentence test purpose

This test checks whether dynamic vertex-input descriptions can supply color data to sparse vertex-shader input locations when two draws use different locations.

## Background knowledge

### Dynamic vertex input

A graphics pipeline can declare `VK_DYNAMIC_STATE_VERTEX_INPUT_EXT` and leave its static `VkPipelineVertexInputStateCreateInfo` empty. Before a draw, `vkCmdSetVertexInputEXT` supplies binding descriptions and attribute descriptions. Each attribute maps a shader `location` to a buffer binding, format, and byte offset; the binding supplies the stride and input rate. Vulkan defines the command and its dynamic-state requirement in [Dynamic Vertex Input](../../../../vulkan-docs/src/chapters/fxvertex.adoc#L258-L270) and the resulting fetch address calculation in [Vertex Input Address Calculation](../../../../vulkan-docs/src/chapters/fxvertex.adoc#L1076-L1130).

### Sparse locations

A shader input location does not encode a byte offset. The active vertex-input description selects the location and maps it to bytes in the bound vertex buffer. This case keeps position at location 0 and changes the color attribute between locations 1 and 7, with the same `vec4` format and offset. The vertex shader for each draw declares the matching color location.

## One concrete example

The registered `nonsequential` case creates two pipelines, both with dynamic vertex input. The first vertex shader reads color at location 1 and renders green geometry. The second reads color at location 7 and renders red geometry. Before each draw, the command buffer binds the corresponding vertex buffer and calls `vkCmdSetVertexInputEXT` with location 0 for position plus the draw-specific color location. Both vertex records place position at byte offset 0 and color at byte offset 16.

## End-to-end test flow

```text
[host] create two vertex shaders with color inputs at locations 1 and 7
[host] create pipelines with VK_DYNAMIC_STATE_VERTEX_INPUT_EXT and empty static vertex-input state
[host] fill two host-visible vertex buffers with six position/color records and flush them
[host] bind pipeline 0 and buffer 0; set dynamic descriptions for locations 0 and 1; draw
[host] bind pipeline 1 and buffer 1; set dynamic descriptions for locations 0 and 7; draw
[device] fetch position and color, run vertex and fragment shaders, and write the color attachment
[host] copy the 32x32 attachment to a host-visible buffer, invalidate it, and compare it with the reference
```

## Generated test artifacts and bound resources

| Resource or artifact | Host setup | Device use | Host readback | Purpose |
|---|---:|---:|---:|---|
| `vert_0` and `vert_1` | generated from locations 1 and 7 | vertex stage | no | Read position and the draw-specific color input. |
| `frag` | generated once | fragment stage | no | Copies interpolated color to the attachment. |
| Two vertex buffers | populated and flushed | vertex fetch | no | Hold six `VertexInfo` records each. |
| Dynamic descriptions | recorded before each draw | vertex fetch | no | Map locations 0 plus 1 or 7 to the record fields. |
| `VK_FORMAT_R8G8B8A8_UNORM` color image | created and cleared | attachment write | yes | Holds the composited draw result. |

## What is checked

The source clears a 32x32 image, draws the green geometry, then draws the red geometry over the central segment. It copies the attachment to a host-visible transfer-destination buffer after the render pass, invalidates that allocation, and calls `tcu::floatThresholdCompare` with threshold `(0.01, 0.01, 0.01, 0.01)`. The reference contains the clear color except for the centered red segment. A pass requires that comparison to succeed.

## Behavior parameter identification

> **Behavior parameter:** test case leaf
>
> **Candidate value:** `nonsequential`

## What failure means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `nonsequential` | Dynamic vertex-input state may map a sparse shader location to the wrong attribute, retain the preceding draw's description, use an incorrect record offset or stride, or transfer fetched color incorrectly through the shader interface. |

## Important variations and special cases

- The factory registers one leaf with fixed `numInstances = 16u` and attribute locations `{1u, 7u}`.
- The test runs under the pipeline construction types registered by the pipeline dispatcher: monolithic, pipeline-library, fast-linked-library, and the shader-object variants.
- Support requires `VK_EXT_extended_dynamic_state`, `VK_EXT_vertex_input_dynamic_state`, and `VK_EXT_extended_dynamic_state2`, plus the construction-type requirements. Library construction requests `VK_EXT_graphics_pipeline_library`; shader-object construction requests dynamic rendering and shader-object support.

## Source mapping

| Topic | Source link | Why it matters |
|---|---|---|
| Dynamic attribute and binding descriptions | [`NonSequentialInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineDynamicVertexAttributeTests.cpp#L165-L186) | Leaves static vertex input empty and creates location-specific dynamic descriptions. |
| Pipeline construction and dynamic state | [`NonSequentialInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineDynamicVertexAttributeTests.cpp#L263-L314) | Declares `VK_DYNAMIC_STATE_VERTEX_INPUT_EXT` for both pipelines. |
| Vertex data, commands, and readback | [`NonSequentialInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineDynamicVertexAttributeTests.cpp#L316-L420) | Populates buffers, issues both draws, and checks the image. |
| Generated GLSL | [`NonSequentialCase::initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineDynamicVertexAttributeTests.cpp#L476-L516) | Builds the two vertex shaders and shared fragment shader. |
| Support and registration | [`NonSequentialCase::checkSupport()` and `createDynamicVertexAttributeTests()`](../../../modules/vulkan/pipeline/vktPipelineDynamicVertexAttributeTests.cpp#L461-L474) | Requires the extensions and registers `nonsequential`. |

## Questions / risk points for user audit

- The image comparison observes the combined result of vertex fetch, shader interfaces, rasterization, attachment writes, copyback, and host comparison. It does not isolate one implementation layer.
- The representative shader uses location 1. The second generated vertex shader differs only by declaring `inColor` at location 7.

## Conversion notes for final wiki rewrite

Keep the Failure Cause Mapping table byte-for-byte identical in the final page. Include the location-1 vertex shader and its fresh SPIR-V disassembly, then explain the location-7 shader as the same program with its input declaration changed.
