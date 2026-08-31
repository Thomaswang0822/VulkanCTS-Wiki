# Understanding Brief: `ycbcr.plane_view`

## One-Sentence Test Purpose

This test checks whether Vulkan exposes each plane of a multi-planar YCbCr image through a compatible single-plane view, including a view backed by an aliased disjoint image, without changing the sampled plane data.

## Background Knowledge

### Multi-planar images and plane views

A multi-planar image stores its components in separate planes. A single-plane image view selects one plane with `VK_IMAGE_ASPECT_PLANE_0_BIT`, `VK_IMAGE_ASPECT_PLANE_1_BIT`, or `VK_IMAGE_ASPECT_PLANE_2_BIT`, and uses the plane's compatible single-plane format. The view dimensions follow that plane's extent, which can differ from the full image for subsampled formats.

Why it matters here:

- The whole-image view samples the YCbCr image through a `VkSamplerYcbcrConversion`; the plane view samples the selected plane directly without conversion.
- A compatible view can reinterpret the same bit pattern with a compatible format. The test therefore compares the plane result in a common format rather than assuming every compatible format has identical channel interpretation.

### Disjoint memory and image aliasing

A disjoint multi-planar image can bind each plane separately. A single-plane image can alias one of those plane allocations when both images use `VK_IMAGE_CREATE_DISJOINT_BIT`, `VK_IMAGE_CREATE_ALIAS_BIT`, compatible formats, matching bindings, and dimensions derived from the selected plane. This is a memory relationship between two Vulkan images, not a second copy of the plane data.

### Sampled-image descriptors

The generated shader receives two combined image samplers. Binding `0` refers to the plane view and binding `1` refers to the whole-image view with an immutable YCbCr conversion sampler. Descriptor sets are the baseline path; descriptor buffers and descriptor heaps exercise alternate descriptor transport when the corresponding extension is available.

## One Concrete Example

The mustpass list contains this representative compute case:

```text
dEQP-VK.ycbcr.plane_view.image_view.g8_b8r8_2plane_444_unorm_disjoint_plane_0_compute
```

For this case, the host creates a 32 by 58 `VK_FORMAT_G8_B8R8_2PLANE_444_UNORM` image with mutable and disjoint flags, selects plane `0`, and creates a plane view using its plane-compatible format. The shader samples the full image at binding `1` and the selected plane at binding `0` at the same coordinate.

Conceptual shader body reconstructed from `getShaderSpec()`:

```glsl
result0 = texture(u_image, texCoord);
result1 = vec4(texture(u_planeView, texCoord));
```

The actual `result1` type and sampler type follow the selected plane-compatible format: `sampler2D`/`vec4`, `isampler2D`/`ivec4`, or `usampler2D`/`uvec4`.

## End-to-End Test Flow

```text
[host] choose a multi-planar format, plane index, compatible format, shader stage, view type, image flags, and descriptor mode
[host] create the 32 by 58 multi-planar image with sampled-image and transfer-destination usage
[host] for `memory_alias`, create a plane-sized single-plane image and bind it to the selected disjoint plane allocation
[host] create the whole-image `VkImageView` with `VkSamplerYcbcrConversion` and the selected plane view without conversion
[host] create descriptor-set, descriptor-buffer, or descriptor-heap resources for both combined image samplers
[host] fill the multi-planar image with deterministic random channel data and transition resources to shader-read-only layout
[host] generate the compute or fragment shader and submit 500 coordinate samples through `ShaderExecutor`
[device] sample the whole image through YCbCr conversion and the selected plane through the compatible view
[device] return the two shader outputs through the executor's output buffers
[host] sample software references at the same coordinates, repack plane results using the compatible format, and choose the comparison format when padding bits differ
[host] fail if any whole-image or plane sample differs from its reference by at least `0.02f`; otherwise return pass
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `getShaderSpec()` generates the sampler declarations and two texture operations. `ShaderExecutor` wraps that specification in a compute or fragment execution path.
- `generateLookupCoordinates()` produces 500 texel-center coordinates from the seeded random generator.
- The host creates the image views, sampler objects, and descriptor transport selected by the test parameters.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Multi-planar image | yes | yes, through the whole-image view | sampled | no | Source for converted sampling and backing memory for alias cases. |
| Whole-image view and conversion sampler | yes | yes, descriptor binding `1` in set `1` | sampled | no | Applies the fixed `VkSamplerYcbcrConversion`. |
| Plane view | yes | yes, descriptor binding `0` in set `1` | sampled | no | Exposes one plane without YCbCr conversion. |
| Plane alias image | only for `memory_alias` | yes, through the plane view | sampled | no | Reuses the selected disjoint plane allocation. |
| Executor input/output buffers | yes, inside `ShaderExecutor` | yes, executor bindings | input coordinates read, results written | yes, by the executor | Carries 500 coordinates and the two shader outputs. |

GLSL sampler variables are shader declarations, not host resources. The `memory_alias` image is a second image object, but it does not contain an independently uploaded copy of the selected plane.

## What Is Checked

- The whole-image result is compared with per-channel `tcu::Texture2DView::sample()` references. Missing channels use `0.0`, except alpha, which uses `1.0`.
- The plane result is reinterpreted through the compatible format. `chooseComparisonFormat()` uses a padded format when needed because padding bits are not required to survive reinterpretation.
- Each of the 500 samples must stay below the component-wise `0.02f` threshold for both views.

## Behavior Parameter Identification

> **Behavior parameter:** view family
>
> **Candidate values:** `image_view`, `memory_alias`

The view family is the primary behavioral axis because it selects whether the plane is exposed by an aspect-qualified view of the original image or by a separate compatible image alias. Format, plane, shader, descriptor mode, and flags configure the same comparison around that choice.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `image_view` | Incorrect single-plane aspect view, plane-compatible format reinterpretation, or whole-image versus plane sampling behavior. |
| `memory_alias` | Incorrect disjoint plane binding or image-alias consistency, in addition to the plane-view and sampling causes covered by `image_view`. |

## Important Variations and Special Cases

- The generator covers multi-planar formats from `VK_YCBCR_FORMAT_FIRST` through `VK_YCBCR_FORMAT_LAST` and the `VK_EXT_ycbcr_2plane_444_formats` range up to, but not including, `VK_FORMAT_G16_B16R16_2PLANE_444_UNORM_EXT`.
- Single-plane formats are skipped because they have no plane view. `memory_alias` cases are generated only with `VK_IMAGE_CREATE_DISJOINT_BIT`.
- The native plane-compatible format is always tested. Additional formats are selected only when their pixel size makes them compatible.
- Both fragment and compute shader paths are generated. Descriptor-buffer and descriptor-heap paths are omitted when the executor does not support that combination or the required extension is unavailable.
- The whole-image conversion uses `VK_SAMPLER_YCBCR_MODEL_CONVERSION_RGB_IDENTITY`, `VK_SAMPLER_YCBCR_RANGE_ITU_FULL`, midpoint chroma locations, nearest filtering, and no forced explicit reconstruction.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Registration and matrix generation | [populateViewGroup()](../../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L983-L1077) | Registers `image_view` and `memory_alias` and expands formats, planes, flags, shader stages, and descriptor modes. |
| Shader specification | [getShaderSpec()](../../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L441-L459) | Defines both sampler declarations and the two sampled outputs. |
| Support checks | [checkSupport()](../../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L477-L501) | Requires image, format, shader, and descriptor-mode support. |
| Image and view setup | [testPlaneView()](../../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L595-L675) | Creates the original image, optional alias, conversion, whole-image view, and plane view. |
| Descriptor transport | [testPlaneView()](../../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L718-L842) | Builds descriptor sets, descriptor buffers, or descriptor heaps and executes the shader. |
| Reference and comparison logic | [testPlaneView()](../../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L845-L943) | Samples references, handles format padding, compares 500 values, and returns pass/fail. |
| Plane-view semantics | [Vulkan image views](../../../../vulkan-docs/src/chapters/resources.adoc#L5848-L5865) | Defines compatible view formats and plane-derived dimensions. |
| Plane alias semantics | [Vulkan plane aliasing](../../../../vulkan-docs/src/chapters/resources.adoc#L11994-L12015) | Defines the disjoint, compatible-format, matching-binding, and dimension conditions. |

## Questions / Risk Points for User Audit

- Does the distinction between an aspect-qualified plane view and a separate aliased image remain clear?
- Is the reason for comparing through a common padded format understandable?
- Is the executor's internal input/output transport sufficiently distinguished from the YCbCr image resources?
- Do the descriptor-buffer and descriptor-heap variants need more implementation detail?
- Is one representative shader walkthrough enough for the shared shader body used by compute and fragment execution?

## Conversion Notes for Final Wiki Rewrite

- Keep `image_view` and `memory_alias` as the behavior parameter values and copy the failure mapping table directly into `View.md`.
- Distill the plane-view, compatible-format, disjoint-memory, and aliasing concepts into short page-local prerequisites.
- Use the compute case `dEQP-VK.ycbcr.plane_view.image_view.g8_b8r8_2plane_444_unorm_disjoint_plane_0_compute` for the representative walkthrough.
- Show the generated sampler declarations and texture operations, then include the compiler-produced SPIR-V artifact for that reconstructed compute shader.
- Keep the 500-sample comparison and padding-format handling in runtime and failure sections, not in Background Knowledge.
