# Understanding Brief: pipeline.misc

## One-Sentence Test Purpose

This test family checks that several graphics-pipeline boundary conditions, including built-in interface values, descriptor-set binding order, compatible layouts, attachment-free rendering, and disabled color writes, produce the required observable result or successfully complete submission.

## Background Knowledge

### Pipeline layout and descriptor-set indices

A `VkPipelineLayout` describes the descriptor-set layouts that commands can bind by set number. A command may bind a descriptor set at a selected first-set index, so set indices need not be populated or bound in ascending order. A pipeline uses only descriptors reached by the shader interface, but the application must still supply the layout and descriptors required by that use.

Why it matters here:
- The `descriptor_bind_test_*` leaves bind four uniform-buffer sets in reverse order, with gaps, or both, then use the accessed sets to produce a green image.
- `identically_defined_layout` creates distinct objects with matching definitions. The pipeline uses one layout while the descriptor-set bind command uses the other.

### Fragment-stage built-ins and side effects

`PrimitiveId` identifies the primitive processed by an invocation. In a fragment shader, Vulkan defines it as the geometry-shader value when geometry is present, or as the value that geometry would have received when it is absent. A color output and a storage-buffer write are independent observable effects: a zero color-write mask suppresses color attachment writes but does not suppress fragment shader execution or storage-buffer stores.

Why it matters here:
- The primitive-ID leaves render two primitives and select red or green from `gl_PrimitiveID`.
- `color_write_mask_none` relies on a fragment-store side effect instead of the deliberately disabled color output.

## One Concrete Example

In `dEQP-VK.pipeline.monolithic.misc.descriptor_bind_test_backwards_holes`, the host creates four descriptor-set layouts and four one-word uniform buffers. It updates the sets in descending set order, then binds set 3 and set 0 while leaving set 2 and set 1 unbound. The fragment program reads only the bound resources and returns green. The host copies the 2 x 2 color image to a host-visible buffer and compares every pixel with green.

## End-to-End Test Flow

```text
[host] choose a pipeline construction type and one misc test case leaf
[host] check construction, feature, extension, or sample-count requirements for that leaf
[host] create shader modules, pipeline layout, pipeline state, and the images or buffers used by the leaf
[host] create descriptors or dynamic-rendering attachments when the leaf needs them
[host] record a draw, including descriptor binds and image-layout barriers where applicable
[device] execute the graphics pipeline and write a color image, a storage buffer, or only completion status
[host] submit and wait; then compare copied pixels or invalidated buffer data when the leaf has an oracle
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The source generates small GLSL programs for the direct C++ leaves. The monolithic Amber leaves load `position_to_ssbo.amber`, `primitive_id_from_tess.amber`, and `layer_read_from_frag.amber`. Program behavior varies by leaf: some shaders encode the oracle in a color image, while `color_write_mask_none` writes `uvec3(2, 3, 4)` through a buffer reference.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Color image and readback buffer | selected leaves | framebuffer and transfer commands | color attachment write | yes | Supports pixel comparisons for primitive-ID, descriptor, interface, and layout leaves. |
| Uniform-buffer descriptor sets | descriptor-binding leaves | graphics bind point | fragment reads selected sets | no | Exposes whether reverse and sparse set binding selects the intended resources. |
| Sampled image and combined-image-sampler set | `identically_defined_layout` | fragment shader | fragment read | indirectly through color image | Couples pipeline creation with one layout to descriptor binding with an independently created matching layout. |
| Storage buffer and payload buffer | `color_write_mask_none` | descriptor set and buffer device address | fragment write | yes | Makes fragment execution observable when color writes are masked off. |
| Dynamic-rendering color attachment | `no_rendering_unused_attachment` only | `VkRenderingInfoKHR` | no required result check | no | Exercises the unused-attachment feature path. |

## What Is Checked

- Image-oracle leaves compare the copied result against an exact or thresholded reference: red/green split, uniform green, or `vec4(0.30, 0.90, 0.60, 1.0)`.
- `identically_defined_layout` uploads a 4 x 4 byte pattern to a sampled image, renders through a separately created but matching layout, and requires the copied color image to match the source bytes exactly.
- `color_write_mask_none` requires the payload buffer's first three 32-bit values to be `2`, `3`, and `4`; the color attachment itself is not the oracle because its `colorWriteMask` is zero.
- `no_rendering` and `no_rendering_unused_attachment` submit their draws and pass after successful completion. They do not read image contents.

## Behavior Parameter Identification

> **Behavior parameter:** behavioral group of test case leaves
>
> **Candidate values:** `amber_builtin_and_storage_cases`; `implicit_primitive_id*`; `array_of_structs_interface`; `descriptor_bind_test_*`; `pipeline_library_misc_cases`; `identically_defined_layout`; `no_rendering*`; `color_write_mask_none`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `amber_builtin_and_storage_cases` | Amber program execution, required-stage built-in handling, or vertex-stage storage writes. |
| `implicit_primitive_id*` | `PrimitiveId` propagation to fragment execution, geometry/tessellation stage handling, or image readback. |
| `array_of_structs_interface` | Shader interface matching, varying transport, or color-output comparison. |
| `descriptor_bind_test_*` | Descriptor-set index handling, sparse/reverse bind state, or shader descriptor access. |
| `pipeline_library_misc_cases` | Pipeline-library linking, dynamic-rendering state, interpolation, or sample-location validation. |
| `identically_defined_layout` | Matching-layout recognition, descriptor binding compatibility, sampled-image access, or image comparison. |
| `no_rendering*` | Dynamic-rendering pipeline creation or execution with zero or unused color attachments. |
| `color_write_mask_none` | Color-write-mask application, fragment-stage execution, buffer device address access, or storage-buffer visibility. |

## Important Variations and Special Cases

- The canonical monolithic root has 13 leaves. Three are Amber cases, and `identically_defined_layout` is monolithic-only.
- Library construction adds `compatible_render_pass`; fast linked library also adds `interpolate_at_sample_no_sample_shading` and four `frag_lib_varying_samples_<N>` leaves for 2, 4, 8, and 16 samples.
- `no_rendering*` is excluded from shader-object construction. The unused-attachment form requires `VK_EXT_dynamic_rendering_unused_attachments` feature `dynamicRenderingUnusedAttachments`.
- Vulkan SC excludes the C++ no-rendering and library-only paths through `CTS_USES_VULKANSC`; the source still has monolithic Amber registration guards for that build.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Registration | [`createMiscTests()`](../../../modules/vulkan/pipeline/vktPipelineMiscTests.cpp#L2543-L2622) | Defines the construction-dependent test case leaves. |
| Primitive ID case | [`ImplicitPrimitiveIDPassthroughCase`](../../../modules/vulkan/pipeline/vktPipelineMiscTests.cpp#L133-L435) | Generates the red/green primitive-ID shaders and validates the image. |
| Descriptor binding case | [`PipelineLayoutBindingTestInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineMiscTests.cpp#L903-L1115) | Constructs, binds, renders, and compares the reverse/sparse descriptor variants. |
| Library interpolation case | [`PipelineLibraryInterpolateAtSampleTestInstance`](../../../modules/vulkan/pipeline/vktPipelineMiscTests.cpp#L439-L783) | Runs monolithic and fast-linked pipelines and compares observed interpolation data. |
| No-rendering case | [`PipelineNoRenderingTestInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineMiscTests.cpp#L1860-L1975) | Builds a dynamic-rendering pipeline with zero or unused attachments. |
| Matching-layout case | [`IdenticallyDefinedLayoutTestInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineMiscTests.cpp#L2051-L2217) | Binds a set with a separately created matching layout and compares output bytes. |
| Masked-color case | [`PipelineColorWriteMaskNoneTestInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineMiscTests.cpp#L2282-L2461) | Uses storage writes as the oracle when `colorWriteMask` is zero. |
| Primitive ID contract | [`PrimitiveId`](../../../../vulkan-docs/src/chapters/interfaces.adoc#interfaces-builtin-variables-primitiveid) | Defines fragment-stage `PrimitiveId` values and stage requirements. |

## Questions / Risk Points for User Audit

- Does the grouping distinguish concrete image or buffer oracles from completion-only no-rendering leaves?
- Does the page make clear that `color_write_mask_none` validates a storage side effect, not the attachment color?
- Does the pipeline-library grouping remain concise without flattening its separate interpolation and varying-sample behaviors?

## Conversion Notes for Final Wiki Rewrite

- Retain the behavior parameter and failure-mapping table verbatim.
- Put the complete canonical monolithic registration tree in the final page and describe construction-specific additions outside that tree.
- Keep the direct shader discussion limited to the distinct observable mechanisms rather than reconstructing every generated GLSL program.
