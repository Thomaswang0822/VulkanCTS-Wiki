# Understanding Brief: MaxVaryings

## One-Sentence Test Purpose

This test checks whether graphics pipelines can pass a device-limit-sized array of four-component values between shader stages and preserve those values through rasterization.

## Background Knowledge

Vulkan shader interfaces assign user-defined variables to locations, and each location provides four 32-bit component slots. Stage-specific limits bound the available input and output interface space. The `max_*Components` limits therefore describe a budget for interface data, not a number of arbitrary GLSL variables. See the Vulkan specification's [Location and Component Assignment](../../../../vulkan-docs/src/chapters/interfaces.adoc#interfaces-iointerfaces-locations) section and [interface limits table](../../../../vulkan-docs/src/chapters/interfaces.adoc#interfaces-iointerfaces-limits).

The test uses a producer stage and a fragment consumer. Built-in position data also consumes output capacity, so the producer-side array is one `vec4` smaller than the raw output-component limit. The case can run only when the producer's usable output and the fragment stage's input capacity are compatible.

## Concrete Example

For a vertex-to-fragment case, the generated vertex shader writes `outputData[i] = ivec4(i)` for every element of a specialization-sized output array. The fragment shader reads the matching input array and emits green only when every element equals its expected index. The test uses this same data pattern for vertex, tessellation-evaluation, and geometry producers; tessellation and geometry passthrough stages carry position data without becoming the stressed interface.

## End-to-End Test Flow

```text
[host] select one registered shader-stage pairing and query VkPhysicalDeviceProperties
[host] compute the usable producer and fragment interface sizes and choose their minimum
[host] generate the SPIR-V modules, with SpecId 0 controlling the array length
[host] create a 32x32 color attachment, host-visible copy buffer, vertex buffer, render pass, and graphics pipeline
[host] attach the specialization data to the producer and fragment stages
[host] draw two triangles, transition the color image, copy it to the host-visible buffer, and wait for completion
[host] compare the copied image with an all-green reference using a 0.02 per-channel threshold
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- Inline SPIR-V assembly is generated for vertex, tessellation-control, tessellation-evaluation, geometry, and fragment modules in [`initPrograms`](../../../modules/vulkan/pipeline/vktPipelineMaxVaryingsTests.cpp#L98-L702). The producer and fragment modules use `SpecId 0` for the array length.
- The vertex, tessellation-evaluation, and geometry producer shaders fill an integer `vec4` array with its element index. The fragment shader checks the array and writes the pass or fail color.
- Tessellation-control, vertex passthrough, and geometry stages are present only to form the selected graphics-stage chain; the stressed interface is selected by `stageToStressIO`.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|---|---|---|---|---|---|
| Vertex buffer | yes | yes | read by vertex stage | no | Supplies two screen-covering triangles. |
| 32x32 `VK_FORMAT_R8G8B8A8_UNORM` color image | yes | framebuffer attachment | written by fragment output | copied | Carries the visible pass/fail result. |
| Host-visible color buffer | yes | transfer destination | written by image-to-buffer copy | yes | Provides the image used by host validation. |
| Specialization data | yes | pipeline shader state | consumed when modules are specialized | no | Sets the interface array length to the common supported size. |

## What Is Checked

The fragment shader checks every element of its input array against the integer vector formed from that element's index. A successful shader check produces green for the rendered image. The host invalidates the copied color buffer and compares all 32x32 pixels with an all-green reference using `tcu::floatThresholdCompare` and `tcu::Vec4(0.02f)` in [`test`](../../../modules/vulkan/pipeline/vktPipelineMaxVaryingsTests.cpp#L950-L1130).

## Behavior Parameter Identification

> **Behavior parameter:** `stageToStressIO`
>
> **Candidate values:** `VK_SHADER_STAGE_VERTEX_BIT`, `VK_SHADER_STAGE_FRAGMENT_BIT`, `VK_SHADER_STAGE_TESSELLATION_EVALUATION_BIT`, `VK_SHADER_STAGE_GEOMETRY_BIT`

These values select which side of the cross-stage interface is filled and checked at its limit. The registered leaves pair them with the corresponding pipeline chain, as shown by [`createMaxVaryingsTests`](../../../modules/vulkan/pipeline/vktPipelineMaxVaryingsTests.cpp#L1133-L1158).

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `VK_SHADER_STAGE_VERTEX_BIT` | Vertex output interface sizing, specialization, or vertex-to-fragment interpolation/consumption. |
| `VK_SHADER_STAGE_FRAGMENT_BIT` in the vertex-fragment family | Fragment input interface sizing or matching against vertex outputs. |
| `VK_SHADER_STAGE_TESSELLATION_EVALUATION_BIT` | Tessellation-evaluation output interface sizing, tessellation-stage plumbing, or its fragment consumer. |
| `VK_SHADER_STAGE_FRAGMENT_BIT` in the tessellation family | Fragment input interface sizing or matching across the tessellation chain. |
| `VK_SHADER_STAGE_GEOMETRY_BIT` | Geometry output interface sizing, emitted primitive data, or its fragment consumer. |
| `VK_SHADER_STAGE_FRAGMENT_BIT` in the geometry family | Fragment input interface sizing or matching across the geometry chain. |

## Important Variations and Special Cases

- The six leaves cover three producer chains and two stressed sides per chain: vertex/fragment, tessellation-evaluation/fragment, and geometry/fragment.
- Tessellation cases require `tessellationShader`; geometry cases require `geometryShader`. The support check also rejects a case when the producer's usable output is smaller than the fragment input capacity, or vice versa.
- Each construction variant receives the same six leaves. The mustpass files cover monolithic, pipeline-library, fast-linked-library, and four shader-object variants, with six entries in each file.

## Source Mapping

| Topic | Source link | Why it matters |
|---|---|---|
| Test parameter and leaf naming | [`MaxVaryingsParam` and `generateTestName`](../../../modules/vulkan/pipeline/vktPipelineMaxVaryingsTests.cpp#L57-L96) | Defines the construction type, stage pairing, and registered names. |
| Generated SPIR-V | [`initPrograms`](../../../modules/vulkan/pipeline/vktPipelineMaxVaryingsTests.cpp#L98-L702) | Shows specialization arrays, passthrough stages, and fragment checking inputs. |
| Support and limit checks | [`supportedCheck`](../../../modules/vulkan/pipeline/vktPipelineMaxVaryingsTests.cpp#L704-L798) | Applies feature and cross-stage compatibility gates. |
| Limit-to-array conversion | [`getMaxIOComponents`](../../../modules/vulkan/pipeline/vktPipelineMaxVaryingsTests.cpp#L915-L948) | Converts component limits to `vec4` array lengths and reserves position capacity. |
| Pipeline, draw, and image validation | [`test`](../../../modules/vulkan/pipeline/vktPipelineMaxVaryingsTests.cpp#L950-L1130) | Shows specialization, pipeline construction, copyback, and green-image comparison. |
| Registration | [`createMaxVaryingsTests`](../../../modules/vulkan/pipeline/vktPipelineMaxVaryingsTests.cpp#L1133-L1158) | Registers the six test case leaves under `max_varyings`. |
| Vulkan interface semantics | [Vulkan interface locations and limits](../../../../vulkan-docs/src/chapters/interfaces.adoc#interfaces-iointerfaces-locations) | Defines four-component location accounting and stage limits. |

## Questions / Risk Points for User Audit

- Is the distinction between the stressed producer/fragment side and the passthrough stages clear?
- Should the final page include a full SPIR-V walkthrough, or is the source-linked artifact summary sufficient for this small family?
- Is the `stageToStressIO` mapping clear for the two different leaves that share `VK_SHADER_STAGE_FRAGMENT_BIT`?

## Conversion Notes for Final Wiki Rewrite

- Keep the final page explanation-first and use the six registered leaves as the behavior values.
- Retain the exact failure mapping table above in `## Failure Meaning`.
- Explain the specialization-sized `ivec4` arrays and the reserved `gl_Position` capacity in the parameter and shader sections.
- Keep the runtime section focused on the 32x32 render, image-to-buffer copy, host invalidation, and all-green comparison.
- A full generated SPIR-V listing would obscure the common mechanism; summarize the generated modules and link to `initPrograms` instead.
