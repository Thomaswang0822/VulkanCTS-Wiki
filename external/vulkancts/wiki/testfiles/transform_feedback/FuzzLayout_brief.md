# Understanding Brief: transform-feedback fuzz interface-block layouts

## One-Sentence Test Purpose

This test checks whether Vulkan transform feedback preserves values from generated GLSL interface blocks when their types, arrays, structures, offsets, and buffer assignments vary.

## Background Knowledge

### Transform feedback layout

The last pre-rasterization shader stage can write selected outputs to transform-feedback buffers. `XfbBuffer`, `Offset`, and `XfbStride` identify the destination buffer, byte position within one captured vertex, and per-vertex reservation. Arrays and structures expand into tightly packed leaves; matrices are captured as column vectors. The Vulkan transform-feedback rules describe this packing and the all-or-nothing handling of a primitive when a buffer has insufficient remaining space.

Why it matters here:
- The test computes a host-side reference layout before it emits the interface-block declarations.
- A layout error can move a value without changing the shader's source-level assignment.

### GLSL interface blocks

An output interface block groups shader outputs and may have a named instance or an instance array. Unused members remain in the declaration in some cases but do not provide a value that the test should compare. Geometry-stage cases use a pass-through vertex shader and a one-point geometry shader that emits one point.

Why it matters here:
- The same layout walker handles scalar, vector, matrix, array, and nested-structure leaves.
- The active leaves, their alignment, and their generated assignments determine which bytes the host validates.

## One Concrete Example

A representative deterministic case is `dEQP-VK.transform_feedback.fuzz.single_basic_type.lowp.float.vertex`. It declares one output block containing a low-precision `float`, assigns the generated reference value in the vertex shader, captures one point, and compares the captured bytes with the reference value at the computed transform-feedback offset. The exact generated value comes from the fixed reference generator, not from a fixed literal in the registration name.

## End-to-End Test Flow

```text
[host] choose a registered deterministic or random layout case
[host] compute interface offsets, strides, buffer assignments, and locations
[host] generate reference scalar/vector/matrix values
[host] generate GLSL output blocks and assignments
[host] create shader modules, a point-list graphics pipeline, and host-visible transform-feedback storage
[host] bind the storage and begin transform feedback
[device] execute one vertex, and for geometry cases pass through and emit one point
[device] capture the declared output values
[host] end transform feedback, make transform-feedback writes visible to the host, and invalidate mapped memory
[host] compare every active captured component with the generated reference
[host] return pass or a mismatch diagnostic
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- GLSL 4.50 vertex source is generated for vertex cases. Geometry cases use a pass-through vertex source plus generated GLSL 4.50 geometry source.
- The generated interface declarations carry `layout(location)`, `xfb_buffer`, `xfb_offset`, and `xfb_stride` where requested, plus precision qualifiers.
- Deterministic cases use fixed structural definitions. Random cases use a seed derived from the group name, the command-line base seed, and the case index.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Transform-feedback buffer | yes | yes | written | yes | Holds captured interface-block bytes |
| Reference byte array | yes | no | no | yes | Supplies generated values and expected layout |
| Graphics pipeline | yes | yes | executes | no | Runs the vertex or geometry path |
| Render pass/framebuffer with no color attachment | yes | yes | used by draw | no | Supplies the graphics draw context |

The host binds the same Vulkan buffer handle for each required transform-feedback binding, with per-binding offsets and sizes selecting the logical regions computed by the layout code.

## What Is Checked

- Every active scalar component is compared at its computed byte offset.
- `int` and `uint` values require exact equality.
- `float` and `double` values pass when the absolute difference is at most `0.05`.
- Missing or unassigned fields are excluded from the expected-value mask and do not cause a direct comparison.
- The first mismatch reports the interface entry, block, byte offset, expected value, received value, and element/vector/component indices.

## Behavior Parameter Identification

> **Behavior parameter:** registered test family
>
> **Candidate values:** `2_level_array`, `3_level_array`, `2_level_struct_array`, `single_basic_type`, `single_basic_array`, `single_struct`, `single_struct_array`, `single_nested_struct`, `single_nested_struct_array`, `instance_array_basic_type`, `multi_basic_types`, `multi_nested_struct`, `various_buffers`, `random_vertex`, `random_geometry`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `2_level_array` | Incorrect nested-array declaration, offset, array stride, or captured component order |
| `3_level_array` | Incorrect three-level array expansion, alignment, or matrix/array packing |
| `2_level_struct_array` | Incorrect structure-array or interface-block instance-array layout |
| `single_basic_type` | Incorrect scalar/vector/matrix type, precision declaration, or basic transform-feedback packing |
| `single_basic_array` | Incorrect array element offsets, stride, or capture order |
| `single_struct` | Incorrect structure-member traversal, alignment, or inactive-member handling |
| `single_struct_array` | Incorrect structure-array packing or block instance handling |
| `single_nested_struct` | Incorrect nested-structure traversal or alignment |
| `single_nested_struct_array` | Incorrect combined nested-structure and array layout |
| `instance_array_basic_type` | Incorrect interface-block instance-array expansion or per-instance transform-feedback buffer placement |
| `multi_basic_types` | Incorrect layout when multiple output blocks share a capture configuration |
| `multi_nested_struct` | Incorrect layout across multiple blocks containing nested structures |
| `various_buffers` | Incorrect `xfb_buffer` routing or per-buffer stride/offset handling |
| `random_vertex` | Incorrect handling of a generated vertex-stage layout combination |
| `random_geometry` | Incorrect handling of a generated geometry-stage layout combination |

## Important Variations and Special Cases

- Deterministic cases use the fixed type table, exact array lengths, fixed structures, and `LAYOUT_XFBBUFFER | LAYOUT_XFBOFFSET`.
- Deterministic matrices use full-matrix assignment. The random generator also uses full-matrix assignment.
- Geometry cases require a geometry shader and declare `layout(points) in` and `layout(points, max_vertices = 1) out`.
- Double-containing layouts require the core `shaderFloat64` feature.
- Random cases use up to three interface blocks, three block members, three structure members, structure depth two, array length four, and instance-array length three. The random generator uses feature bits to enable vectors, matrices, doubles, arrays, structures, instance arrays, missing or unassigned members, and out-of-order offsets.
- The random groups contain 50 cases for the first nine feature sets and 100 cases for the four `all_*` feature sets. Each case seed is `deStringHash(groupName) + baseSeed + case index`.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Deterministic registration and matrices | [`InterfaceBlockTests::init()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackFuzzLayoutTests.cpp#L372-L738) | Defines exact groups, values, stages, and random case counts |
| Layout model | [`computeXfbLayout()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackFuzzLayoutCase.cpp#L554-L912) | Computes alignment, offsets, strides, locations, and active leaves |
| Shader declarations | [`generateDeclaration()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackFuzzLayoutCase.cpp#L1002-L1234) | Emits interface blocks and transform-feedback layout qualifiers |
| Shader assignments | [`generateAssignment()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackFuzzLayoutCase.cpp#L1237-L1559) | Writes generated values into active leaves |
| Runtime capture | [`InterfaceBlockCaseInstance::iterate()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackFuzzLayoutCase.cpp#L1788-L1860) | Creates the pipeline, binds capture buffers, draws, barriers, and reads back |
| Result checking | [`validateValues()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackFuzzLayoutCase.cpp#L1863-L1999) | Compares captured values and emits mismatch diagnostics |
| Random generation | [`RandomInterfaceBlockCase`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackRandomLayoutCase.cpp#L56-L260) | Defines seeds, limits, feature bits, and generated type/layout choices |
| Vulkan transform feedback semantics | [`Transform Feedback`](../../../../../external/vulkan-docs/src/chapters/vertexpostproc.adoc#vertexpostproc-transform-feedback) | Defines capture activation, packing, stride, offsets, and buffer limits |
| Vulkan shader execution | [`Shaders`](../../../../../external/vulkan-docs/src/chapters/shaders.adoc#shaders) | Defines the shader-stage context used by the generated programs |

## Questions / Risk Points for User Audit

- Does the distinction between registered test family and generated leaf case remain clear?
- Is the host reference-layout model separated from Vulkan's transform-feedback packing rules?
- Are the random-case limits and 50/100 case counts presented as source-observed values rather than universal Vulkan limits?
- Should the final page include one generated shader walkthrough or document the generated family without reproducing a full shader?
- Are missing and unassigned members described with the correct validation consequence?

## Conversion Notes for Final Wiki Rewrite

- Keep the explanation centered on the reference-layout versus captured-buffer comparison.
- Put exact deterministic group children in the registration tree and move generated type names and random feature sets into parameter tables.
- Use one representative vertex shader walkthrough for `single_basic_type.lowp.float.vertex`; cover geometry as a parameter variation instead of adding a second walkthrough.
- Distill the background section to transform-feedback packing and interface-block traversal.
- Copy the failure-cause mapping table into the final page unchanged. Write the detailed cause analysis separately.
- Keep source navigation in the final appendix, with the Vulkan specification links supporting semantics rather than replacing source evidence.
