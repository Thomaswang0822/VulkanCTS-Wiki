# Understanding Brief: ycbcr.format

## One-Sentence Test Purpose

This test checks whether Vulkan can create and sample each registered YCbCr format through a sampler conversion across supported image layouts, shader stages, array-layer modes, and descriptor paths.

## Background Knowledge

### Multi-planar YCbCr images

A multi-planar format stores luma and chroma components in separate planes. In 4:2:0 formats, the chroma planes have half the width and height of the luma plane; in 4:2:2 formats, they have half the width. A two-plane format packs the chroma components together, while a three-plane format keeps them separate. The sampler conversion presents these planes through one combined image sampler.

Why it matters here:
- The format controls plane count, component depth, subsampling, and the dimensions accepted by the image.
- `VK_IMAGE_CREATE_DISJOINT_BIT` changes memory binding for multi-planar images, but it does not change the shader declaration.

### Sampler YCbCr conversion

`VkSamplerYcbcrConversionCreateInfo` associates the image format with a component mapping, range, chroma locations, reconstruction filter, and color model. This test uses `VK_SAMPLER_YCBCR_MODEL_CONVERSION_RGB_IDENTITY`, `VK_SAMPLER_YCBCR_RANGE_ITU_FULL`, midpoint chroma locations, nearest chroma reconstruction, and no forced explicit reconstruction. With the identity model, the conversion does not apply a YCbCr-to-RGB matrix.

Why it matters here:
- The image view and sampler must carry matching conversion state before the shader calls `texture()`.
- Midpoint chroma support is required because the test requests `VK_CHROMA_LOCATION_MIDPOINT` for both axes.

## One Concrete Example

Consider `dEQP-VK.ycbcr.format.g8_b8_r8_3plane_420_unorm.compute_linear`. The host uses a 66 by 32 three-plane 8-bit 4:2:0 image. It fills the planes with a gradient, creates a nearest sampler conversion, and binds the converted image view as `u_image` at set 1, binding 0. The compute shader receives one normalized coordinate per invocation and stores the sampled `vec4` in an output buffer.

The reference uses one `tcu::Texture2DView` for each present channel. Missing RGB channels become zero, and the alpha reference becomes one. The host compares the sampled output with the reference at every coordinate using a per-component threshold of `0.02f`.

## End-to-End Test Flow

```text
[host] choose a format and one combination of shader stage, tiling, array-layer mode, and descriptor mode
[host] check sampler YCbCr conversion, format, tiling, array, shader-stage, and descriptor support
[host] create a 66 by 32, one-mip-level 2D image and allocate image memory
[host] create a sampler conversion with RGB identity, ITU full range, midpoint chroma locations, and nearest filtering
[host] create a converted image view and a clamp-to-edge nearest sampler
[host] query combinedImageSamplerDescriptorCount and configure the selected descriptor path
[host] fill the active image layer with a gradient and clear an unused array layer when present
[host] generate the selected shader stage and submit work through the shader executor
[device] sample the converted image at one coordinate per executor value
[device] write each sampled vec4 to the executor output buffer
[host] build channel references with tcu::Texture2DView and fill absent channels with zero or one
[host] compare every result component with the reference using a 0.02f threshold and report pass or failure
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `getShaderSpec()` generates one input, `texCoord`, of type `vec2`, one output, `result`, of type `vec4`, and a `texture()` assignment. The array-layer branch changes the sampler type to `sampler2DArray` and appends layer 1 to the lookup coordinate.
- `generateSources()` selects the executor for the registered shader stage. Compute produces one GLSL compute shader. Vertex, geometry, tessellation, and fragment paths add the executor's stage-specific plumbing.
- The source does not set an explicit `ShaderBuildOptions` target. The shader collection therefore uses the baseline SPIR-V target when it compiles generated GLSL.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| YCbCr `VkImage` | yes | yes | read as a sampled image | no | Stores the format-specific planes and layout. |
| `VkSamplerYcbcrConversion` and `VkSampler` | yes | yes, through the sampler descriptor | used by sampling | no | Supplies conversion, chroma location, reconstruction, and filtering state. |
| Converted `VkImageView` | yes | yes | sampled | no | Exposes the image to the combined image sampler. |
| Input buffer | yes | yes | read by the executor shader | no | Carries generated texture coordinates. |
| Output buffer | yes | yes | written by the executor shader | yes | Carries one `vec4` result per coordinate. |
| Linear mapped image memory | yes, only for linear mapped cases | yes | read by the device | indirectly | Tests host-filled linear image memory instead of a staging upload. |

`MultiPlaneImageData` is host-side reference and upload storage, not a shader-visible resource. The GLSL `sampler2D` or `sampler2DArray` hides the individual planes after the image view and sampler conversion are configured.

## What Is Checked

- `checkSupport()` requires sampler YCbCr conversion and a format feature for midpoint or cosited chroma samples. The case-specific path additionally checks array support, vertex-pipeline stores and atomics, or descriptor extensions.
- `vkGetPhysicalDeviceImageFormatProperties2` must succeed and report `combinedImageSamplerDescriptorCount >= 1`.
- The test samples every generated coordinate. For each channel present in the format, the host samples the corresponding reference plane with the same nearest, clamp-to-edge sampler state. Absent channels must be zero except alpha, which must be one.
- A result fails when any component differs from its reference by at least `0.02f`. The test logs the coordinate, result, and reference, then returns `Got invalid results`.

## Behavior Parameter Identification

> **Behavior parameter:** format test family value, represented by the registered format child
>
> **Candidate values:** `b10x6g10x6r10x6g10x6_422_unorm_4pack16`, `b12x4g12x4r12x4g12x4_422_unorm_4pack16`, `b16g16r16g16_422_unorm`, `b8g8r8g8_422_unorm`, `g10x6_b10x6_r10x6_3plane_420_unorm_3pack16`, `g10x6_b10x6_r10x6_3plane_422_unorm_3pack16`, `g10x6_b10x6_r10x6_3plane_444_unorm_3pack16`, `g10x6_b10x6r10x6_2plane_420_unorm_3pack16`, `g10x6_b10x6r10x6_2plane_422_unorm_3pack16`, `g10x6_b10x6r10x6_2plane_444_unorm_3pack16`, `g10x6b10x6g10x6r10x6_422_unorm_4pack16`, `g12x4_b12x4_r12x4_3plane_420_unorm_3pack16`, `g12x4_b12x4_r12x4_3plane_422_unorm_3pack16`, `g12x4_b12x4_r12x4_3plane_444_unorm_3pack16`, `g12x4_b12x4r12x4_2plane_420_unorm_3pack16`, `g12x4_b12x4r12x4_2plane_422_unorm_3pack16`, `g12x4_b12x4r12x4_2plane_444_unorm_3pack16`, `g12x4b12x4g12x4r12x4_422_unorm_4pack16`, `g16_b16_r16_3plane_420_unorm`, `g16_b16_r16_3plane_422_unorm`, `g16_b16_r16_3plane_444_unorm`, `g16_b16r16_2plane_420_unorm`, `g16_b16r16_2plane_422_unorm`, `g16_b16r16_2plane_444_unorm`, `g16b16g16r16_422_unorm`, `g8_b8_r8_3plane_420_unorm`, `g8_b8_r8_3plane_422_unorm`, `g8_b8_r8_3plane_444_unorm`, `g8_b8r8_2plane_420_unorm`, `g8_b8r8_2plane_422_unorm`, `g8_b8r8_2plane_444_unorm`, `g8b8g8r8_422_unorm`, `r10x6_unorm_pack16`, `r10x6g10x6_unorm_2pack16`, `r10x6g10x6b10x6a10x6_unorm_4pack16`, `r12x4_unorm_pack16`, `r12x4g12x4_unorm_2pack16`, `r12x4g12x4b12x4a12x4_unorm_4pack16`

The format child is the primary behavioral axis because it changes the image's component storage, plane structure, subsampling, and reference interpretation. Shader stage, tiling, array layers, mapped memory, disjoint memory, and descriptor mode provide coverage around that axis.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| Any registered format child | Format-specific plane interpretation, image creation or binding, sampler conversion, shader sampling, descriptor setup, reference construction, or result comparison failed. |

## Important Variations and Special Cases

- Formats with `_420` or `_422` suffixes use reduced chroma dimensions and require an image width, or width and height, compatible with the format's block rules. `_444` formats keep full chroma dimensions.
- Multi-planar formats receive `_disjoint` cases. Linear tiling also receives `_mapped` cases, and multi-planar linear cases can combine both suffixes.
- Descriptor-set mode is available to all executor-supported shader stages. Descriptor-buffer and descriptor-heap modes are generated only for fragment execution because `executorSupported()` restricts those modes to `SHADERTYPE_FRAGMENT`.
- Array cases use two layers and sample array layer 1. They require `VK_EXT_ycbcr_image_arrays` and an image-format limit of at least two array layers.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Format group registration | [`populateFormatGroup()`](../../../modules/vulkan/ycbcr/vktYCbCrFormatTests.cpp#L712-L729) | Enumerates the registered format children. |
| Per-format matrix | [`populatePerFormatGroup()`](../../../modules/vulkan/ycbcr/vktYCbCrFormatTests.cpp#L640-L710) | Defines shader, tiling, array, disjoint, mapped, and descriptor variants. |
| Shader specification | [`getShaderSpec()`](../../../modules/vulkan/ycbcr/vktYCbCrFormatTests.cpp#L291-L310) | Defines the sampled image declaration and lookup expression. |
| Case execution | [`testFormat()`](../../../modules/vulkan/ycbcr/vktYCbCrFormatTests.cpp#L353-L631) | Creates resources, samples, builds references, and checks results. |
| Common image support | [`checkImageSupport()`](../../../modules/vulkan/ycbcr/vktYCbCrUtil.cpp#L176-L204) | Checks conversion and plane feature support. |
| Generated compute wrapper | [`ComputeShaderExecutor::generateComputeShader()`](../../../modules/vulkan/shaderexecutor/vktShaderExecutor.cpp#L3061-L3110) | Adds buffers, invocation indexing, and the generated operation. |
| Buffer declarations and I/O | [`declareBufferBlocks()` and `generateExecBufferIo()`](../../../modules/vulkan/shaderexecutor/vktShaderExecutor.cpp#L2034-L2130) | Defines executor input/output resources and transfers values. |
| Multi-planar format semantics | [`formats.adoc`](../../../../vulkan-docs/src/chapters/formats.adoc#L901-L965) | Defines plane components and subsampling. |
| Sampler conversion semantics | [`samplers.adoc`](../../../../vulkan-docs/src/chapters/samplers.adoc#L773-L1045) | Defines conversion state, midpoint locations, and reconstruction. |

## Questions / Risk Points for User Audit

- Is the format child, rather than shader stage or descriptor mode, the correct primary behavioral axis?
- Does the concrete 66 by 32 4:2:0 example make the plane and reference relationship clear?
- Should the final page show a second walkthrough for the fragment descriptor-buffer or descriptor-heap path?
- Is the distinction between host-side `MultiPlaneImageData` and the shader-visible combined image sampler clear?
- Does the page preserve enough detail about feature filtering without presenting the generated source matrix as an exact device-executed count?

## Conversion Notes for Final Wiki Rewrite

- Keep `## Background Knowledge` to the multi-planar image and sampler-conversion concepts; move concrete setup and checks into their later sections.
- Use `dEQP-VK.ycbcr.format.g8_b8_r8_3plane_420_unorm.compute_linear` as the representative shader path.
- Keep one compute walkthrough. The generated compute wrapper is the useful shader mechanism; vertex, tessellation, geometry, and fragment wrappers differ mainly in executor plumbing.
- Copy the `### Failure Cause Mapping` row into the final page unchanged. Write `### Cause Analysis` separately.
- Preserve the format names exactly in the registration tree and parameter values.
