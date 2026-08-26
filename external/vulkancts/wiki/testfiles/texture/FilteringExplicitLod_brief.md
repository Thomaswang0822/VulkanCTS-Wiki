# Understanding Brief: `texture.explicit_lod`

## One-Sentence Test Purpose

This test checks whether explicit LOD and explicit gradient texture operations select and filter 2D mipmap data within Vulkan's permitted coordinate, LOD, and texel-value precision.

## Background Knowledge

### Explicit LOD and explicit gradients

A filtered texture lookup first determines an LOD, selects one or two mipmap levels, finds neighboring texels, and applies the sampler's filters. An explicit LOD operation supplies the LOD value directly. An explicit gradient operation supplies coordinate derivatives, and the implementation derives the LOD from their footprint in texel space. Vulkan permits bounded implementation choices in the derivative scale calculation and quantizes LOD with `mipmapPrecisionBits`.

Why it matters here:

- `textureLod` isolates sampling with a caller-supplied LOD.
- `textureGrad` also exercises derivative-to-LOD calculation before using the same level-selection and filtering machinery.

### A range is the correct reference result

Filtering does not always have one exact reference value. Coordinate conversion snaps to a grid controlled by `subTexelPrecisionBits`; mipmap interpolation snaps according to `mipmapPrecisionBits`; format conversion and filtering arithmetic have representable-value bounds. The verifier therefore computes an acceptable interval for each output component and accepts a GPU result that lies within one permitted combination.

Why it matters here:

- A simple exact comparison could reject a conformant implementation.
- Testing coordinates at half-texel spacing stresses boundaries where coordinate rounding, address mode, texel selection, or mipmap selection can change the legal result.

The relevant rules are in the Vulkan specification's [LOD and image-level selection](../../../../vulkan-docs/src/chapters/textures.adoc#L1525-L1531), [explicit LOD operation](../../../../vulkan-docs/src/chapters/textures.adoc#L1654-L1702), and [mipmap filtering](../../../../vulkan-docs/src/chapters/textures.adoc#L1705-L1802) sections. The device precision limits are defined in [Physical Device Limits](../../../../vulkan-docs/src/chapters/limits.adoc#L534-L545).

## One Concrete Example

Consider `dEQP-VK.texture.explicit_lod.2d.formats.r8g8b8a8_unorm_linear`.

The host creates a 32 by 32 `VK_FORMAT_R8G8B8A8_UNORM` image with a complete mip chain. Every mip level receives component gradients. For every coordinate on a 65 by 65 half-texel grid, the case executes seven lookups with LOD values `-1.0`, `-0.5`, `0.0`, `0.5`, `1.0`, `1.5`, and `2.0`. Its generated fragment operation is conceptually:

```glsl
/// The explicit lod argument controls level selection.
result = textureLod(testSampler, vec2(coord), lod);
```

The verifier receives the same coordinate and LOD. It determines the candidate level or adjacent levels, applies repeat addressing, computes the legal linear-filtered intervals, and checks the returned `vec4` component by component. This case performs 29,575 sample checks, so it covers texel and mipmap boundaries rather than checking a single image point.

## End-to-End Test Flow

```text
[host] choose the sizes, formats, or derivatives intermediate node and construct one sampler/pipeline test case
[host] generate every mip level with known component gradients and generate sample arguments on a half-texel coordinate grid
[host] create the sampled image, upload all mip levels, create the image view and sampler, and bind them as a combined image sampler
[host] generate ShaderExecutor programs containing textureLod or textureGrad
[host] pack coordinates, LODs, and derivatives into ShaderExecutor inputs and execute all sample invocations
[device] perform each explicit image sample and return the sampled vec4 plus the coordinate used
[host] read the ShaderExecutor outputs
[host] verify every sample against mathematically derived acceptable intervals using device precision limits
[host] return fail for any rejected sample, quality warning when only the documented relaxed value precision passes, or pass otherwise
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- [`initSpec`](../../../modules/vulkan/texture/vktTextureFilteringExplicitLodTests.cpp#L940-L959) builds a `ShaderSpec` whose operation is either `textureLod` or `textureGrad` and declares a `sampler2D` in descriptor set 1, binding 0.
- [`generateSources`](../../../modules/vulkan/shaderexecutor/vktShaderExecutor.cpp#L4199-L4220) turns that specification into a fragment or compute program. The graphics and compute variants run the same sampling expression through different ShaderExecutor paths.
- [`Generator::getSampleArgs`](../../../modules/vulkan/texture/vktTextureFilteringExplicitLodTests.cpp#L1083-L1138) creates the coordinate grid and attaches either seven LOD values or five derivative pairs to each coordinate.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Mipmapped 2D image | yes | yes | read | no | Contains known gradients at every mip level, which lets the verifier derive legal filtered values. |
| `sampler2D testSampler` | yes | yes, set 1 binding 0 | read | no | Carries minification, magnification, mipmap, and address modes into the tested lookup. |
| ShaderExecutor input storage | yes | yes | read | no | Supplies each invocation's coordinate, LOD, and derivative values. |
| ShaderExecutor result storage | yes | yes | written | yes | Returns the sampled `vec4` for per-sample host verification. |
| Host-side mip-level pixel data | yes | no | no | yes, directly by host | Supplies exact texels to both image upload and the software verifier. |

## What Is Checked

For every generated sample, [`SampleVerifier::verifySample`](../../../modules/vulkan/texture/vktSampleVerifier.cpp#L855-L860) checks whether all four returned components fit at least one legal result interval. The calculation covers:

- explicit LOD or derivative-derived LOD bounds;
- legal mipmap level selection and mipmap interpolation weights;
- normalized-coordinate conversion using the selected level dimensions;
- nearest or linear texel filtering with repeat or clamp-to-edge addressing;
- format conversion and filtering precision.

The strict verifier uses the format's normal precision model. Linear filtering of half-float or signed normalized 8-bit data may use a second, relaxed filtering-precision model. A sample that passes only that second model contributes a quality warning. Any sample that fails the available model or models fails the test case.

## Behavior Parameter Identification

> **Behavior parameter:** intermediate node below `texture.explicit_lod.2d`
>
> **Candidate values:** `sizes`, `formats`, `derivatives`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `sizes` | Incorrect explicit LOD level selection, texel addressing, or filtering for an image-size, filter, mipmap, address-mode, or pipeline combination. |
| `formats` | Incorrect explicit LOD sampling, format conversion, or filtering precision for the affected sampled format and pipeline. |
| `derivatives` | Incorrect explicit-gradient footprint-to-LOD calculation, level selection, or filtering for the affected gradient, sampler, or pipeline combination. |

A failure in any value can also come from incorrect image upload, descriptor binding, ShaderExecutor input/output transport, or host/device visibility, because those mechanisms are shared by every case.

## Important Variations and Special Cases

- `sizes` varies nine power-of-two and non-power-of-two extents, all minification and magnification filter pairs, both mipmap modes, repeat and clamp-to-edge addressing, and graphics versus compute execution. It keeps the format fixed at `VK_FORMAT_R8G8B8A8_UNORM`.
- `formats` fixes the size at 32 by 32 and uses matched nearest settings or matched linear settings across 19 normalized and floating-point formats. It uses repeat addressing and runs graphics and compute variants.
- `derivatives` fixes a 16 by 16 `VK_FORMAT_R8G8B8A8_UNORM` image and clamp-to-edge addressing. Five derivative pairs cover a point footprint, symmetric footprints, one-axis footprints, and a larger symmetric footprint. All minification, magnification, and mipmap filter combinations run in both pipelines.
- The image format must support sampled-image use and, when any selected filter is linear, linear sampled-image filtering. Unsupported cases raise `NotSupportedError`.
- Vulkan SC avoids the costly in-process verification in the main process. The subprocess performs verification, so this control path must not be interpreted as removal of the conformance check.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Category registration | [`createTextureTests`](../../../modules/vulkan/texture/vktTextureTests.cpp#L46-L69) | Attaches the `explicit_lod` test family directly under `texture`. |
| Family and intermediate-node registration | [`createExplicitLodTests` and `create2DTests`](../../../modules/vulkan/texture/vktTextureFilteringExplicitLodTests.cpp#L1398-L1418) | Establishes `texture.explicit_lod.2d` and its `sizes`, `formats`, and `derivatives` descendants. |
| Shader operation construction | [`genLookupCode`](../../../modules/vulkan/texture/vktTextureFilteringExplicitLodTests.cpp#L158-L287) and [`initSpec`](../../../modules/vulkan/texture/vktTextureFilteringExplicitLodTests.cpp#L940-L959) | Selects `textureLod` or `textureGrad` and wires its operands. |
| Image and sampler setup | [`genTestCaseData`](../../../modules/vulkan/texture/vktTextureFilteringExplicitLodTests.cpp#L986-L1020) | Defines the full mip chain, sampler limits, address modes, and shader stage. |
| Test data generation | [`Generator`](../../../modules/vulkan/texture/vktTextureFilteringExplicitLodTests.cpp#L1032-L1138) | Builds gradient mip levels and per-sample coordinates, LODs, or gradients. |
| Matrix construction | [`create2DFormatTests`, `create2DDerivTests`, and `create2DSizeTests`](../../../modules/vulkan/texture/vktTextureFilteringExplicitLodTests.cpp#L1150-L1396) | Defines every registered dimension and leaf name. |
| Runtime resources and execution | [`runTest`, `execute`, and `createResources`](../../../modules/vulkan/texture/vktTextureFilteringExplicitLodTests.cpp#L575-L872) | Connects generated samples to the image, sampler, shader, readback, and final status. |
| Per-sample result policy | [`TextureFilteringTestInstance::verify`](../../../modules/vulkan/texture/vktTextureFilteringExplicitLodTests.cpp#L615-L685) | Applies strict and conditional relaxed verification and assigns pass, warning, or fail. |
| Mathematical sample verification | [`SampleVerifier`](../../../modules/vulkan/texture/vktSampleVerifier.cpp#L417-L763) | Computes acceptable texel, mipmap, and filtered-value intervals. |
| LOD and coordinate utilities | [`vktSampleVerifierUtil.cpp`](../../../modules/vulkan/texture/vktSampleVerifierUtil.cpp#L63-L285) | Implements level bounds, LOD bounds, coordinate ranges, and precision-grid calculations. |

## Questions / Risk Points for User Audit

- Is the distinction between direct LOD input and derivative-derived LOD clear enough to support the two representative shader walkthroughs?
- Does the acceptable-interval explanation make clear why the test cannot use an exact reference image comparison?
- Is `sizes`, `formats`, and `derivatives` the most useful behavior axis for failure diagnosis?
- The source stores `sampledCoord` but the final pass/fail loop checks only `m_resultSamples`. Should the final page mention that output only as ShaderExecutor plumbing rather than a validated result?

No unresolved source ambiguity changes the planned page semantics. The `sampledCoord` output will be described as returned plumbing, not as a separately checked conformance value.

## Conversion Notes for Final Wiki Rewrite

- Keep explicit-versus-gradient LOD and precision-grid concepts as concise Background Knowledge bullets.
- Use one `textureLod` graphics case and one `textureGrad` graphics case as representative walkthroughs. Their generated SPIR-V should expose the `Lod` and `Grad` operands of `OpImageSampleExplicitLod`.
- Preserve the runtime resource and per-sample verification model, but shorten the learning-oriented timeline.
- Copy the `### Failure Cause Mapping` table unchanged into the final page.
- Carry `sizes`, `formats`, and `derivatives` into `## Behavior Parameters` as the primary axis.
- Move source navigation into the final appendix and omit helper details that do not affect behavior.
