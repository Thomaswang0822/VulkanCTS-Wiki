# Understanding Brief: YCbCr filtering

## One-Sentence Test Purpose

This test checks whether sampler YCbCr conversion reconstructs downsampled chroma correctly while applying linear texture filtering to supported 4:2:0 formats in graphics and compute execution.

## Background Knowledge

### Sampler YCbCr conversion and chroma reconstruction

A multi-planar 4:2:0 image stores luma at full resolution and chroma at lower horizontal and vertical resolution. A `VkSamplerYcbcrConversion` describes how a sampler reconstructs the chroma components when a shader samples the image. Its `chromaFilter` selects nearest-neighbour reconstruction with `VK_FILTER_NEAREST` or interpolation with `VK_FILTER_LINEAR`; the ordinary texture `minFilter` and `magFilter` control filtering at the sampled image level.

Why it matters here:
- The test holds image sampling at `VK_FILTER_LINEAR` and changes `chromaFilter` between `VK_FILTER_NEAREST` and `VK_FILTER_LINEAR`.
- The conversion uses `VK_CHROMA_LOCATION_MIDPOINT`, so the reference bounds account for the selected chroma sample location.
- The conversion uses `VK_SAMPLER_YCBCR_MODEL_CONVERSION_RGB_IDENTITY` and `VK_SAMPLER_YCBCR_RANGE_ITU_FULL`, so the expected values are based on identity model conversion and full-range encoded components.

### Graphics and compute shader outputs

The same sampled color can be observed through two host execution paths. The graphics path maps a full-screen quad to normalized texture coordinates and writes the sample through a fragment shader. The compute path maps one invocation to one output-image texel and writes the sample with `imageStore`.

Why it matters here:
- Both paths use the same `texture(u_sampler, uv)` operation and the same pixel-center coordinate rule.
- The output representation differs: the graphics path returns a rendered `VK_FORMAT_R32G32B32A32_SFLOAT` image, while compute writes that format to a storage image before copyback.

## One Concrete Example

Consider `dEQP-VK.ycbcr.filtering.linear_sampler_g8_b8r8_2plane_420_unorm_graphics`. The host creates a `VK_FORMAT_G8_B8R8_2PLANE_420_UNORM` image, fills its available planes with component gradients from `0.0` to `1.0`, and creates a sampler conversion with `chromaFilter = VK_FILTER_NEAREST`. The sampler itself has `minFilter = VK_FILTER_LINEAR` and `magFilter = VK_FILTER_LINEAR`.

The fragment shader receives `v_texCoord` and samples the combined image sampler:

```glsl
// Conceptual reconstruction of the source-generated fragment shader.
#version 450
precision mediump int; precision highp float;
layout(location = 0) in vec2 v_texCoord;
layout(location = 0) out mediump vec4 dEQP_FragColor;
layout (set=0, binding=0) uniform sampler2D u_sampler;
void main (void)
{
    dEQP_FragColor = vec4(texture(u_sampler, v_texCoord));
}
```

The full-screen vertices map `(-1,-1)` through `(1,1)` to `(0,0)` through `(1,1)`. For a `64 x 64` render target, the host reference uses the center of each output pixel, `((x + 0.5) / 64, (y + 0.5) / 64)`, as the corresponding texture coordinate.

## End-to-End Test Flow

```text
[host] select one of eight registered 4:2:0 formats, one chroma filter, and graphics or compute execution
[host] check VK_KHR_sampler_ycbcr_conversion, samplerYcbcrConversion, format filtering, midpoint samples, and the selected chroma-filter feature
[host] create a 2D optimal-tiled sampled image and fill its available planes with component gradients
[host] create VkSamplerYcbcrConversion with RGB identity, ITU full range, midpoint chroma locations, and the selected chromaFilter
[host] create a combined image sampler with the conversion attached and bind the sampled image view
[host] generate vert, frag, and comp GLSL programs
[host] submit a full-screen graphics draw or a compute dispatch with an 8 x 8 local workgroup
[device] execute texture(u_sampler, uv) using linear texture filtering and the conversion's chroma reconstruction rule
[device] write the sampled color to the graphics framebuffer or compute storage image
[host] obtain the graphics pixels or transition, copy, and download the compute output image
[host] calculate per-pixel minimum and maximum bounds from the source planes and compare each result component with those bounds
[host] pass when every sampled result stays inside its corresponding bounds; otherwise fail with the first 30 detailed mismatches logged
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `vert`, `frag`, and `comp` are inline GLSL strings emitted by `LinearFilteringTestCase::initPrograms()`. The vertex shader maps positions to normalized coordinates, the fragment shader samples the combined sampler, and the compute shader writes each in-range invocation's sample to a storage image.
- The source collection has no explicit `vk::ShaderBuildOptions` for these programs, so the normal source-collection baseline determines the compiler target. The final page's representative SPIR-V artifact records the target used for that generated walkthrough.
- `MultiPlaneImageData` stores the CPU reference planes. `fillGradient()` creates a component gradient separately for each plane at that plane's extent.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Multi-planar sampled image | yes | yes, through an image view and combined sampler | read by `texture()` | no | Supplies the luma and downsampled chroma data. |
| `VkSamplerYcbcrConversion` and immutable sampler | yes | yes | used by sampler conversion | no | Fixes the format, sample locations, color model, range, and `chromaFilter`. |
| Graphics framebuffer | yes | yes | written by fragment output | yes, through renderer pixels | Captures graphics samples in `VK_FORMAT_R32G32B32A32_SFLOAT`. |
| Compute output image | yes | yes, as a storage image | written by `imageStore` | yes, after transfer and download | Captures compute samples for the same reference comparison. |
| Descriptor set | yes | yes | supplies sampled image and compute output bindings | no | Binding 0 is the combined image sampler; compute binding 1 is the storage image. |

`v_texCoord`, `gl_GlobalInvocationID`, and `imageSize()` are shader inputs or built-ins, not host-created resources. The reference-side `MultiPlaneImageData` is not itself a GPU resource.

## What Is Checked

- `verifyFilteringResult()` calls `calculateBounds()` with the source planes, format bit depth, filtering and conversion precision, midpoint chroma locations, identity conversion, full range, the selected chroma filter, and clamp-to-edge addressing.
- The host checks each output component against its per-pixel `minBound` and `maxBound`. A value below the minimum or above the maximum records a mismatch.
- Graphics checks use the renderer's color pixels. Compute checks use the downloaded first plane of the `VK_FORMAT_R32G32B32A32_SFLOAT` output image.
- The test runs two size pairs in each instance: image `8 x 8` to output `64 x 64`, and image `64 x 32` to output `32 x 64`.

## Behavior Parameter Identification

> **Behavior parameter:** chroma reconstruction filter
>
> **Candidate values:** `VK_FILTER_NEAREST`, `VK_FILTER_LINEAR`

The graphics/compute choice, format, and size pair are important matrix dimensions, but `chromaFilter` is the primary behavioral axis because it changes how downsampled chroma is reconstructed.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `VK_FILTER_NEAREST` | Incorrect nearest-neighbour chroma reconstruction, sampler conversion state, format handling, or result transfer. |
| `VK_FILTER_LINEAR` | Incorrect interpolated chroma reconstruction, unsupported or mishandled linear chroma filtering, sampler conversion state, or result transfer. |

## Important Variations and Special Cases

- The eight registered format values cover 2-plane and 3-plane 4:2:0 UNORM formats at 8, 10, 12, and 16 bits. The local `ycbcrFormats` vector does not enumerate every YCbCr format.
- Each format has four cases: nearest chroma filtering in graphics and compute, and linear chroma filtering in graphics and compute.
- The graphics and compute paths use the same two image/output size pairs. Compute rounds dispatch dimensions up to 8 x 8 workgroups and guards invocations whose coordinates fall outside the output extent.
- The feature checks prune cases when the device lacks midpoint chroma samples, linear sampled-image filtering, separate reconstruction filtering for the nearest-chroma cases, or linear YCbCr conversion filtering for the linear-chroma cases.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Case registration | [`createFilteringTests()`](../../../modules/vulkan/ycbcr/vktYCbCrFilteringTests.cpp#L787-L838) | Defines the eight formats, two chroma filters, and graphics/compute cases. |
| Conversion and sampler setup | [`createYCbCrConversion()`](../../../modules/vulkan/ycbcr/vktYCbCrFilteringTests.cpp#L135-L157) and [`getSamplerInfo()`](../../../modules/vulkan/ycbcr/vktYCbCrFilteringTests.cpp#L62-L84) | Defines conversion parameters and linear texture sampler state. |
| Graphics execution | [`LinearFilteringTestInstance::iterate()`](../../../modules/vulkan/ycbcr/vktYCbCrFilteringTests.cpp#L389-L488) | Creates resources, renders the full-screen quad, generates pixel-center coordinates, and checks results. |
| Compute execution | [`LinearFilteringComputeTestInstance::iterate()`](../../../modules/vulkan/ycbcr/vktYCbCrFilteringTests.cpp#L526-L676) | Dispatches the compute shader, copies the output image, downloads it, and checks results. |
| Shader generation | [`LinearFilteringTestCase::initPrograms()`](../../../modules/vulkan/ycbcr/vktYCbCrFilteringTests.cpp#L740-L782) | Emits the vertex, fragment, and compute shader sources. |
| Feature gates | [`LinearFilteringTestCase::checkSupport()`](../../../modules/vulkan/ycbcr/vktYCbCrFilteringTests.cpp#L704-L730) | Defines support requirements and pruning behavior. |
| Shared reference setup | [`fillGradient()`](../../../modules/vulkan/ycbcr/vktYCbCrUtil.cpp#L364-L388) and [`uploadImage()`](../../../modules/vulkan/ycbcr/vktYCbCrUtil.cpp#L420-L454) | Builds per-plane gradient data and uploads it into the image. |
| Bounds calculation | [`calculateBounds()`](../../../modules/vulkan/ycbcr/vktYCbCrUtil.cpp#L1625-L1665) | Produces the expected interval for each sampled pixel. |

The relevant Vulkan semantics are described in the Vulkan specification's [`Sampler YCbCr Conversion`](../../../vulkan-docs/src/chapters/samplers.adoc#samplers-YCbCr-conversion) and [`Image Operations`](../../../vulkan-docs/src/chapters/textures.adoc#textures-sampler-YCbCr-conversion) sections.

## Questions / Risk Points for User Audit

- Does the distinction between linear texture filtering and the selected chroma reconstruction filter remain clear?
- Is the graphics versus compute observation path easy to follow?
- Does the resource table distinguish the CPU reference planes from GPU images?
- Does the bounds-based comparison explain the pass condition without implying exact floating-point equality?
- Should a final page include a second walkthrough for the compute shader, or is the fragment shader walkthrough enough with a variation summary?

## Conversion Notes for Final Wiki Rewrite

- Use the `chromaFilter` value as the primary behavior axis, with `VK_FILTER_NEAREST` and `VK_FILTER_LINEAR` subsections.
- Keep the format, execution path, and image/output size pairs in a compact parameter table.
- Turn the fragment shader example into the representative graphics walkthrough. Describe the compute shader in `Parameter Variation Summary` and `Additional Info` only if it is not shown as a second stage.
- Distill the sampler conversion prerequisite into a short Level-3 Background Knowledge list; keep concrete setup in runtime sections.
- Copy the `### Failure Cause Mapping` table directly into the final page. Write `### Cause Analysis` fresh.
- Keep the implementation links in the final Source Reference Appendix, not in the main narrative.
