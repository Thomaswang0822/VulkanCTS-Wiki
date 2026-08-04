# Understanding Brief: `pipeline.sampler`

## One-Sentence Test Purpose

This test checks whether a Vulkan implementation applies sampler filtering, addressing, coordinate, and level-of-detail state correctly when shaders sample images.

## Background Knowledge

### A sampler separates image data from sampling state

A combined image sampler supplies an image view and a `VkSampler`. The view selects image subresources and component mapping; the sampler supplies filtering, mipmap, address, LOD, and border-color state. [`VkSamplerCreateInfo`](../../../../vulkan-docs/src/chapters/samplers.adoc#L67-L140) defines these controls.

Why it matters here:

- The same sampled image can produce different results solely because sampler state changes.
- `unnormalizedCoordinates` has restrictions on filtering, mipmapping, LOD, addressing, and image-view shape, so it is deliberately a smaller test space.

### LOD selection has several inputs

The texture operations combine the implicit or explicit shader LOD with sampler bias and clamps; an image view may impose a minimum LOD. The specification gives this sequence in the [level-of-detail operation](../../../../vulkan-docs/src/chapters/textures.adoc#L1638-L1782). `maxSamplerLodBias` bounds the contribution from `mipLodBias` and shader bias ([limits](../../../../vulkan-docs/src/chapters/limits.adoc#L554-L566)).

Why it matters here:

- The five `max_sampler_lod_bias` values place the same maximum bias at a different point in that calculation.
- A distinct color in each mip level makes the selected level observable.

## One Concrete Example

The representative test case `dEQP-VK.pipeline.monolithic.sampler.max_sampler_lod_bias.shader_lod_compute` samples a 2D texture in a one-invocation compute shader. The host clears every mip level to a different deterministic color, passes `maxSamplerLodBias` as `pc.lodLevel`, and expects the color from the rounded, available level. The source chooses `textureLod` for `SHADER_LOD` and writes the result to a storage image ([`MaxSamplerLodBiasCase::initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineSamplerTests.cpp#L2385-L2455)).

## End-to-End Test Flow

```text
[host] select a registered sampler family and create the image, view, sampler, descriptor set, and pipeline
[host] fill source image data or per-mip colors, then transition it for shader reads
[host] render a quad or dispatch compute work that samples the combined image sampler
[device] apply the selected sampler state and write sampled output
[host] copy or read the output, build the matching reference, and compare
[host] report pass only when every compared sample is within that family's rule
```

For `max_sampler_lod_bias`, the host reads the physical-device limit, fills all mip levels with different colors, and samples a 1-by-1 output. The implementation uses an exact expected mip level and a `0.005` comparison threshold ([`MaxSamplerLodBiasInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineSamplerTests.cpp#L2462-L2783)).

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

`SamplerTest::initPrograms()` generates graphics shaders or a compute shader from the selected view type, format, coordinate form, and explicit-LOD choice ([source](../../../modules/vulkan/pipeline/vktPipelineSamplerTests.cpp#L375-L508)). `MaxSamplerLodBiasCase::initPrograms()` separately generates the LOD-limit shaders.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|---|---:|---:|---:|---:|---|
| Sampled image and image view | yes | yes | read | no | Supplies formatted texels and visible mip levels. |
| `VkSampler` | yes | yes | read as descriptor state | no | Selects filter, address, LOD, and coordinate behavior. |
| Combined image-sampler descriptor | yes | yes | read | no | Joins the view and sampler at shader binding 0. |
| Color attachment or storage image | yes | yes | written | yes | Captures the sampled result. |
| Push constants in LOD-limit tests | yes | yes | read | no | Carry `lodLevel`, `fbWidth`, and `fbHeight`. |

## What Is Checked

- `view_type` and `separate_stencil_usage` compare textured output with a format-aware reference produced by `ImageSamplingInstance`.
- `exact_sampling` uses nearest sampling at center and edge-adjacent coordinates and checks exact pixel values.
- `max_sampler_lod_bias` checks that the output color identifies the mip level predicted by the selected bias mechanism.
- `border_swizzle` is implemented by [`vktPipelineSamplerBorderSwizzleTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineSamplerBorderSwizzleTests.cpp#L1), not this source file.

## Behavior Parameter Identification

> **Behavior parameter:** intermediate node under `pipeline.monolithic.sampler`
>
> **Candidate values:** `view_type`, `exact_sampling`, `separate_stencil_usage`, `border_swizzle`, `max_sampler_lod_bias`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `view_type` | Filter, reduction, mipmap, address, image-view, coordinate, or format conversion behavior differs from the reference. |
| `exact_sampling` | Nearest texel selection or edge-coordinate handling differs from the exact expected texel. |
| `separate_stencil_usage` | The separate-stencil image-view usage or sampling path is not honored. |
| `border_swizzle` | `VK_EXT_border_color_swizzle` handling differs from its delegated test's expected border result. |
| `max_sampler_lod_bias` | A sampler, shader, or image-view LOD contribution does not select the expected mip level. |

## Important Variations and Special Cases

- `view_type` is generated only for monolithic and `shader_object_unlinked_spirv` construction. The same construction gate also controls `border_swizzle`.
- `exact_sampling`, `separate_stencil_usage`, and `max_sampler_lod_bias` are registered for the other pipeline-construction roots as well; compute variants are generated only for monolithic and `shader_object_unlinked_spirv`.
- Compressed formats skip selected minification and reduction cases because their noise can make those reference comparisons unsuitable. Cube and cube-array view types do not receive address-mode cases.
- `VIEW_MINLOD` requires `VK_EXT_image_view_min_lod` and is omitted in Vulkan SC builds.

## Source Mapping

| Topic | Source link | Why it matters |
|---|---|---|
| Test-family registration | [`createSamplerTests()`](../../../modules/vulkan/pipeline/vktPipelineSamplerTests.cpp#L3174-L3202) | Creates the five direct intermediate nodes and their construction gating. |
| Generic sampler setup and shader generation | [`SamplerTest`](../../../modules/vulkan/pipeline/vktPipelineSamplerTests.cpp#L289-L508) | Builds the sampling parameters and emitted shaders. |
| Exact sampling matrix | [`createExactSamplingTests()`](../../../modules/vulkan/pipeline/vktPipelineSamplerTests.cpp#L3040-L3139) | Enumerates formats, coordinate forms, image content, and edge positions. |
| LOD-limit runtime | [`MaxSamplerLodBiasInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineSamplerTests.cpp#L2462-L2783) | Initializes mip colors, configures state, and checks the selected level. |

## Questions / Risk Points for User Audit

- Is the distinction between the broad reference-comparison families and the dedicated LOD-limit check clear?
- Does the direct-intermediate-node behavioral axis make the failure mapping useful?
- Are the construction-type and Vulkan SC exclusions visible without obscuring the core sampler behavior?

## Conversion Notes for Final Wiki Rewrite

Distill the sampler and LOD prerequisites into short final-page bullets. Preserve this failure-cause table byte-for-byte under the final page's `### Failure Cause Mapping`. Keep the compute `shader_lod_compute` case as the one representative shader walkthrough because it directly exposes the LOD mechanism and its output resource.
