# Understanding Brief: `texture.mipmap`

## One-Sentence Test Purpose

This test checks whether sampled 2D, cube, and 3D images select and filter mip levels correctly when derivatives, shader bias, sampler LOD clamps, image-view level ranges, and image-view minimum LOD affect the lookup.

## Background Knowledge

### LOD and mip-level selection

A mipmapped image stores progressively smaller levels. For an implicit-LOD sample, Vulkan derives a scale factor from coordinate derivatives and converts it to the LOD value. A shader-supplied bias can shift that value. Sampler `minLod` and `maxLod` then clamp it. The sampler mipmap mode either chooses one level or blends two adjacent levels.

Why it matters here:
- The same lookup can reach different colored levels when coordinates, bias, sampler limits, or view limits change.
- Nearest mipmap filtering permits one selected level, while linear mipmap filtering permits a weighted result from adjacent levels.

### Image-view level restrictions

An image view exposes a contiguous mip-level range through `baseMipLevel` and `levelCount`. `VK_EXT_image_view_min_lod` adds a floating-point lower bound to image-level selection. The specification permits preferred and alternative rounding at boundaries, so the verifier may need to accept either result.

Why it matters here:
- `base_level`, `max_level`, and `image_view_min_lod` alter the levels visible to a lookup through different Vulkan state.
- Integer-coordinate fetch and gather operations have separate rules when the requested level is below the image-view minimum.

## One Concrete Example

Consider `dEQP-VK.texture.mipmap.2d.basic.linear_linear_clamp`. The host creates an `R8G8B8A8_UNORM` 2D image and fills every mip level with a distinct solid color. It divides a render target into a 4 by 4 grid and assigns each cell different texture coordinates. The fragment shader samples a `sampler2D` with implicit LOD:

```glsl
// Simplified reconstruction of the generated fragment lookup.
vec4 sampled = texture(u_sampler, v_texCoord);
outColor = sampled * u_colorScale + u_colorBias;
```

The coordinate rate across a cell controls the derivatives, which control LOD. `linear_linear` selects linear filtering within a level and linear filtering between adjacent levels. The host computes an ideal image, then accepts each pixel only if it is valid under the configured coordinate, color, derivative, and LOD precision allowances.

## End-to-End Test Flow

```text
[host] choose image type, coordinate behavior, filtering, wrapping, size, LOD control, and graphics or compute path
[host] create all mip levels and fill each level with a distinct color
[host] create the sampled image, image view, sampler, descriptors, output target, and generated shader programs
[host] divide the output into cells and assign coordinates or LOD controls per cell
[host] submit drawing or compute dispatches
[device] interpolate or reconstruct coordinates, obtain implicit or explicit level information, sample or gather, and write the output
[host] read the rendered or storage-image result
[host] build a software reference and validate lookup results with precision-aware LOD bounds, or compare the gather result with its exact expected color
[host] pass only when no disallowed pixel or gather component remains
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `TextureTestCase::initPrograms` delegates ordinary cases to `initializePrograms`, which specializes shared GLSL templates for 2D, cube, or 3D sampling and emits both graphics and compute programs.
- Ordinary graphics cases use a pass-through vertex shader and a fragment shader containing `texture(...)`. Bias cases add the shader bias operand.
- Ordinary compute cases reconstruct perspective-correct coordinates, approximate neighboring derivatives, and use `textureGrad(...)`; bias cases adjust the explicit LOD or gradients.
- Integer-coordinate image-view-minimum-LOD cases generate `texelFetch(...)` shaders directly.
- `min_lod_gather` generates a full-screen triangle and a fragment shader containing `textureGather(...)` with a selected component.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Mipmapped sampled image | yes | yes | read | no | Each level has a distinct color, so the sampled color reveals level selection and blending. |
| Image view | yes | yes | read through descriptor | no | Its base level, level count, and optional minimum LOD restrict accessible levels. |
| Sampler | yes | yes | read through descriptor | no | It supplies within-level filtering, mipmap mode, wrapping, bias, and LOD clamps. |
| Uniform parameters | yes | yes | read | no | They carry bias, color scale and bias, output size, and explicit fetch LOD where applicable. |
| Geometry or coordinate data | yes | yes | read | no | Graphics interpolation or compute reconstruction produces the derivatives used for level selection. |
| Render target or storage image | yes | yes | written | copied or read | It contains the implementation's sampled result. |
| Host software texture and reference image | yes | no | no | yes | They model valid lookup results and record the error mask. |
| Gather verification buffer | yes | yes | written by image copy | yes | It exposes the single-pixel gather result to the host. |

## What Is Checked

- Ordinary 2D, cube, and 3D cases first compare against an ideal software image. A pixel outside the direct color threshold is checked again against the set of results allowed by coordinate precision and bounded derivative and LOD precision.
- Every cell must contain zero invalid pixels. On failure, the test logs the rendered image, reference image, and error mask.
- Image-view-minimum-LOD cases retry the software comparison with the specification's alternative rounding mode if the preferred interpretation fails.
- `min_lod_gather.minlod_0_1` expects the selected component from mip level 0. `minlod_1_1` uses `robustImageAccess2` and expects zero because gathering from the base level lies below the integer image-view minimum.

## Behavior Parameter Identification

> **Behavior parameter:** direct child below the `texture.mipmap` test-family root
>
> **Candidate values:** `2d`, `cubemap`, `3d`, `min_lod_gather`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `2d` | Incorrect 2D derivative-based LOD, filtering, wrapping, bias or clamp handling, image-view level restriction, or explicit fetch behavior. |
| `cubemap` | Incorrect cube face or seamless coordinate handling, cube derivative-based LOD, filtering, bias or clamp handling, or image-view level restriction. |
| `3d` | Incorrect three-coordinate derivative-based LOD, 3D filtering and wrapping, bias or clamp handling, image-view level restriction, or explicit fetch behavior. |
| `min_lod_gather` | Incorrect gather component selection, image-view minimum-LOD interpretation, or robust zero result below the permitted level. |

## Important Variations and Special Cases

- The four minification names combine nearest or linear filtering within a level with nearest or linear selection between mip levels.
- `basic`, `affine`, and `projected` change how derivatives arise. `bias` supplies a shader LOD bias. Separate `min_lod`, `max_lod`, `base_level`, `max_level`, and `image_view_min_lod` paths isolate state that constrains level selection.
- Graphics and compute cases target the same lookup contract. Compute shaders reconstruct interpolation and supply explicit gradients because compute execution has no rasterizer-provided fragment derivatives.
- Cube projected and bias cases omit compute variants because the source marks the compute-side calculations as insufficiently accurate for those combinations.
- `image_view_min_lod` and `min_lod_gather` are absent from Vulkan SC builds. Integer-coordinate and robust gather cases add stronger extension and feature requirements.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Main execution and precision-aware checking | [`Texture2DMipmapTestInstance::iterate`](../../../modules/vulkan/texture/vktTextureMipmapTests.cpp#L246-L401), [`TextureCubeMipmapTestInstance::iterate`](../../../modules/vulkan/texture/vktTextureMipmapTests.cpp#L513-L665), [`Texture3DMipmapTestInstance::iterate`](../../../modules/vulkan/texture/vktTextureMipmapTests.cpp#L824-L984) | Shows the cell layouts, reference parameters, precision values, lookup-difference checks, and pass condition. |
| LOD-control execution | [2D LOD control](../../../modules/vulkan/texture/vktTextureMipmapTests.cpp#L1013-L1265), [cube LOD control](../../../modules/vulkan/texture/vktTextureMipmapTests.cpp#L1293-L1554), [3D LOD control](../../../modules/vulkan/texture/vktTextureMipmapTests.cpp#L1780-L2042) | Shows sampler clamps, image-view ranges, per-cell controls, and shared verification. |
| Integer-coordinate image-view minimum LOD | [2D shader and support path](../../../modules/vulkan/texture/vktTextureMipmapTests.cpp#L2232-L2441), [3D shader and support path](../../../modules/vulkan/texture/vktTextureMipmapTests.cpp#L2443-L2653) | Shows explicit `texelFetch` shader generation and required features. |
| Gather special case | [`GatherParams` and gather implementation](../../../modules/vulkan/texture/vktTextureMipmapTests.cpp#L2661-L3100) | Defines the two minimum-LOD values, generated gather shader, robust behavior, and exact host comparison. |
| Case generation | [`populateTextureMipmappingTests`](../../../modules/vulkan/texture/vktTextureMipmapTests.cpp#L3343-L4196) | Defines direct children, parameter matrices, graphics and compute variants, and exclusions. |
| Shared shader generator | [`initializePrograms`](../../../modules/vulkan/texture/vktTextureTestUtil.cpp#L210-L760) | Specializes the graphics and compute GLSL used by ordinary cases. |
| Lookup verifier | [`computeTextureLookupDiff` for 2D](../../../../../framework/opengl/gluTextureTestUtil.cpp#L1550-L1699) | Demonstrates the ideal fast path and precision-aware set-of-valid-results fallback. |
| Vulkan LOD and level selection | [Textures chapter](../../../../vulkan-docs/src/chapters/textures.adoc#L1524-L1802) | Defines implicit and explicit LOD, bias and clamps, image-view minimum LOD, and nearest or linear mip-level selection. |
| Vulkan gather semantics | [Texel Gathering](../../../../vulkan-docs/src/chapters/textures.adoc#L2122-L2190) | Defines component gathering and robust behavior below image-view minimum LOD. |

## Questions / Risk Points for User Audit

- Is the direct-child behavior axis the most useful failure split for a page that contains several deeper LOD-control mechanisms?
- Does the ordinary 2D example make the lookup-difference verifier clear without implying that it accepts arbitrary color error?
- Is the distinction between sampler LOD clamps, image-view level ranges, and image-view minimum LOD clear?
- Is the gather path clearly separated from ordinary filtered sampling?
- Source-level risk: `TextureGatherMinLodTest::initDeviceCapabilities` requests `robustBufferAccess2` and core `robustBufferAccess`, but the `minlod_1_1` path checks and relies on `robustImageAccess2`. Source inspection does not establish that the custom device enables `robustImageAccess2`; this requires source-owner investigation and does not change the documented expected result.

The final page should retain the direct-child behavior axis and explain deeper structures in prose rather than expanding the registration tree.

## Conversion Notes for Final Wiki Rewrite

- Distill the LOD and image-view explanations into a short prerequisite list.
- Use `dEQP-VK.texture.mipmap.2d.basic.linear_linear_clamp` for the representative generated-shader walkthrough.
- Keep one walkthrough. Explain bias, compute, integer fetch, cube derivative, and gather shader differences in the variation summary and surrounding prose.
- Preserve the resource model in compact runtime bullets rather than copying the full brief table.
- Copy the Failure Cause Mapping table unchanged.
- Keep source navigation in the final appendix.
