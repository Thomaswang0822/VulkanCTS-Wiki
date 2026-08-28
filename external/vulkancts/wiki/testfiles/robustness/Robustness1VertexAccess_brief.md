# Understanding Brief: robustness1 vertex access

## One-Sentence Test Purpose

This test checks whether Vulkan robust vertex input access handles out-of-range attribute fetches correctly across zero-stride, shared-allocation, padded, and separate-buffer layouts.

## Background Knowledge

### Vertex input bindings and attributes

A vertex input attribute names a format, byte offset, and binding. The binding supplies the stride and input rate used to locate the attribute for each vertex; changing the binding size or offset changes which fetches are inside the valid range [Vertex Input Description](../../../../vulkan-docs/src/chapters/fxvertex.adoc#L12-L24).

### Robust out-of-range results

With `robustBufferAccess` enabled, an out-of-range vertex input access is constrained by Vulkan robust buffer access rules, but it is not required to return one single sentinel. A value from the bound memory range or an allowed zero form may be observable [Robust Buffer Access](../../../../vulkan-docs/src/chapters/shaders.adoc#L1925-L2030).

## One Concrete Example

Conceptually, the test builds a 3-by-3 tile grid with sixteen logical vertices, then marks logical vertices `5`, `6`, `9`, and `10` as invalid. `GenerateTriangles()` moves those invalid logical vertices to the end of the generated allocation while retaining their original positions in the index mapping [mesh generation](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L396-L456).

One representative layout uses a `Vertex` structure containing `position`, `color1`, `color2`, and unused fields. Both bindings use `sizeof(Vertex)` stride, but the second binding's supplied data is shortened before `color2` for the invalid vertices. The shader receives three `vec4` inputs and writes green only when the fetched colors belong to the accepted valid or invalid sets [single-buffer case](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L252-L293), [generated shader](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L887-L932).

## End-to-End Test Flow

```text
[host] choose one registered leaf and create a 3-by-3 indexed triangle grid
[host] allocate padded or shortened vertex data according to the leaf's stride/layout pattern
[host] create a dedicated device with robustBufferAccess enabled
[host] create vertex/index buffers, render pass, framebuffer, descriptors, and graphics pipeline
[host] generate vertex and fragment GLSL programs
[host] bind the buffers and submit vkCmdDrawIndexed
[device] fetch vertex attributes, classify valid and out-of-range colors, and emit the vertex result
[device] rasterize the result through the fragment shader into a 12 x 12 color attachment
[host] wait, read the color attachment, and compare every pixel with vec4(0, 1, 0, 1)
[host] pass only if no pixel differs; otherwise log the image and fail
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `Robustness1AccessTest::initPrograms()` generates a vertex shader with `in_position`, `in_color0`, and `in_color1`. `in_position.z` distinguishes valid generated vertices from invalid ones; the shader accepts `expectedColor` and `unusedColor` for valid vertices and the broader `invalidColors` set for invalid vertices [shader generation](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L887-L932).
- A minimal fragment shader copies the vertex result to its color output [fragment shader](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L932-L940).
- No verified shader-analyzer or disassembler artifact is available for an exact registered path in this task, so this brief does not reconstruct GLSL or SPIR-V beyond the source-backed behavior above.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Vertex buffers | yes | yes | read by vertex input | no | Hold positions and color attributes, with leaf-specific stride, offsets, padding, and shortened valid ranges. |
| Index buffer | yes | yes | read by indexed draw | no | Selects the generated vertex records, including the invalid logical indices. |
| Descriptor sets | yes | yes | used by the graphics pipeline | no | The common setup allocates uniform-buffer bindings for each input binding; the tested vertex inputs come from vertex buffers. |
| Color attachment | yes | yes | written by the render pass | yes | Carries green or non-green classification to the host image check. |

`PaddedAlloc` is a host-side arrangement copied into vertex buffers; its padding is not a separate Vulkan resource. In the separate-buffer leaf, padding uses `unusedColor` because an out-of-range fetch may legally return a value from within the bound range [allocation helper](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L136-L193), [separate-buffer setup](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L347-L389).

## What Is Checked

- Valid generated vertices must fetch `expectedColor` or `unusedColor` for their color attributes.
- Invalid/out-of-range vertices may fetch `expectedColor`, `unusedColor`, `vec4(0.0)`, or `vec4(0.0, 0.0, 0.0, 1.0)`, matching the source's accepted `invalidColors` set [color sets](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L123-L130).
- The vertex shader emits `vec4(0,1,0,1)` when the classification is valid; otherwise it forwards `in_color0` [validation shader](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L922-L931).
- The host reads the `VK_FORMAT_R8G8B8A8_UNORM` color attachment and requires every `12 x 12` pixel to equal the green vector [host check](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L761-L779).

## Behavior Parameter Identification

> **Behavior parameter:** registered test case leaf
>
> **Candidate values:** `out_of_bounds_stride_0`, `out_of_bounds_stride_16_single_buffer`, `out_of_bounds_stride_30_middle_of_buffer`, `out_of_bounds_stride_8_middle_of_buffer_separate`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `out_of_bounds_stride_0` | Incorrect bounds handling for a zero-stride binding or shortened structure binding. |
| `out_of_bounds_stride_16_single_buffer` | Incorrect bounds handling when two bindings address one allocation and one ends inside a record. |
| `out_of_bounds_stride_30_middle_of_buffer` | Incorrect bounds or offset handling for a padded allocation and shortened middle binding. |
| `out_of_bounds_stride_8_middle_of_buffer_separate` | Incorrect robust result handling for separate padded position and color buffers, or rejection of an allowed in-range padding value. |

## Important Variations and Special Cases

- `out_of_bounds_stride_0` combines a zero-stride color binding with a shortened structure binding.
- `out_of_bounds_stride_16_single_buffer` makes two bindings address one `Vertex` allocation and shortens only the second binding's data.
- `out_of_bounds_stride_30_middle_of_buffer` applies offsets into padded data and shortens the second binding by the invalid-vertex count.
- `out_of_bounds_stride_8_middle_of_buffer_separate` separates positions and colors and initializes padding with `unusedColor`, an important exception to the otherwise recognizable `outOfRangeColor` sentinel design [four leaves](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L202-L389).
- The registered name `out_of_bounds_stride_30_middle_of_buffer` is preserved exactly. The inspected implementation uses `sizeof(Vertex)` as its binding stride; no source-backed explanation for the historical `30` token was found.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Registered leaves and input layouts | [`robustness1Tests`](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L195-L389) | Defines the four exact identifiers, buffers, attributes, strides, and invalid indices. |
| Padded data arrangement | [`PaddedAlloc`](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L136-L193) | Explains the recognizable data before and after the valid range. |
| Mesh and index mapping | [`GenerateTriangles()`](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L391-L456) | Establishes the 3-by-3 grid and invalid logical vertices. |
| Device, pipeline, draw, and image check | [`robustness1TestFn()`](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L480-L779) | Supplies the host/device timeline and final pass condition. |
| Shader classification | [`Robustness1AccessTest::initPrograms()`](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L887-L940) | Defines accepted colors and green output. |
| Robust device creation | [`createRobustBufferAccessDevice()`](../../../modules/vulkan/robustness/vktRobustnessUtil.cpp#L53-L87) | Shows that `robustBufferAccess` is enabled. |
| Registered paths | [`robustness.txt`](../../../mustpass/main/vk-default/robustness.txt#L15026-L15029) | Confirms the four default-profile leaves. |

## Questions / Risk Points for User Audit

- Is the registered test case leaf the correct primary behavioral axis?
- Is the distinction between valid colors, accepted invalid colors, and the rejected `outOfRangeColor` clear?
- Is the source-backed limitation on shader walkthrough reconstruction explicit enough?
- Does the concrete single-buffer example accurately convey how a shortened binding crosses a record boundary?
- Should any additional Vulkan specification detail be added after a dedicated shader-analysis pass?

## Conversion Notes for Final Wiki Rewrite

- Keep the final page's `Background Knowledge` to the two prerequisite concepts: vertex-input addressing and robust out-of-range results.
- Preserve the four-leaf registration tree and exact identifiers.
- Carry the behavior-axis conclusion and copy the `### Failure Cause Mapping` table directly into `## Failure Meaning`.
- Distill the concrete single-buffer example into the behavior-parameter subsection rather than copying the beginner scaffolding verbatim.
- Keep the shader limitation explicit unless a verified shader-analyzer/disassembler output is produced; do not invent reconstructed GLSL or SPIR-V.
- Use the source mapping as the final appendix, not as the main narrative.
