# Understanding Brief: Protected-memory YCbCr conversion

## One-Sentence Test Purpose

This test checks whether a protected sampled image applies the selected sampler YCbCr reconstruction, range, and color-model conversion and produces values within source-computed bounds in compute and fragment paths.

## Background Knowledge

### Sampler YCbCr conversion

`VkSamplerYcbcrConversionCreateInfo` fixes the image format, component mapping, encoded range, conversion model, chroma sample locations, reconstruction filter, and explicit-reconstruction choice. The same conversion object is attached to the sampler and image view. A shader still calls `texture()` on a `sampler2D`; the conversion takes place as part of that sampling operation.

Why it matters here:

- Chroma location and subsampling determine which chroma samples contribute to a luma-resolution lookup.
- Full and narrow range use different range expansion, while `rgb_identity`, `ycbcr_identity`, `ycbcr_709`, `ycbcr_601`, and `ycbcr_2020` select different conversion behavior.
- Multi-planar formats may consume more than one combined-image-sampler descriptor even though the shader declares one combined sampler.

### Protected resources and observable results

Protected device memory is device-visible but not host-visible. Protected command buffers execute protected queue operations on a protected-capable queue. The test therefore checks converted values on the device instead of copying protected image contents to the host.

Why it matters here:

- The source YCbCr image, graphics color target, helper storage buffer, and command buffers used for protected work preserve the protected execution path.
- Host-visible buffers carry input plane data before upload, coordinates, and reference bounds; the test does not read protected image contents back to the host.
- A mismatch is made observable by preventing a protected validation dispatch from completing before its timeout.

## One Concrete Example

Consider this executable case:

```text
dEQP-VK.protected_memory.interaction.ycbcr.g8_b8r8_2plane_420_unorm.compute.ycbcr_709.itu_full.tiling_optimal_cosited_disjoint
```

The host creates a protected, disjoint two-plane 4:2:0 image. It fills the luma and chroma channels with deterministic gradients, computes acceptable converted-value bounds for every generated coordinate, uploads each plane, and binds an immutable YCbCr conversion sampler configured for BT.709, full range, nearest filtering, and cosited chroma.

The compute validator dispatches 50 invocations. Each invocation samples the protected image at one coordinate and compares the converted `vec4` against the matching minimum and maximum bounds with a `0.01` component threshold. A mismatch enters a loop whose increment comes from a protected helper field reset to zero, causing the submission to time out.

## End-to-End Test Flow

```text
[host] select format, shader path, model, range, chroma location, and disjoint mode
[host] reject unsupported format-feature combinations
[host] create a protected sampled image and matching conversion, sampler, and image view
[host] generate deterministic plane values and acceptable conversion bounds
[host] upload every plane and transition the image for shader sampling
[host] create host-visible reference data and protected validation resources
[device] compute path: sample and validate 50 converted values directly
[device] fragment path: sample every generated coordinate and render green or red points to a protected color image
[device] fragment path: compute validator samples 50 color-image points and checks for green
[host] treat a validation timeout as failure and a completed validation submission as pass
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `testShaders()` always emits `ResetSSBO` and `ImageValidator` compute programs. `ImageValidator` performs the conversion-bearing `texture()` call in compute cases and validates the intermediate color image in fragment cases.
- Fragment cases also emit a pass-through vertex shader and a fragment shader that samples the protected YCbCr image, compares against the host bounds, and writes green for a match or red for a mismatch.
- The shader collection uses its default target because this source supplies no explicit `ShaderBuildOptions`; the baseline target is SPIR-V 1.0.
- Host-side code generates one source image and per-coordinate minimum and maximum bounds with `ycbcr::calculateBounds()`.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Protected source image | yes | yes | transfer writes, shader reads | no | Holds packed or multi-planar source values whose sampled conversion is under test. |
| Per-plane staging buffers | yes | yes | transfer reads | host writes only | Upload deterministic source bytes into each image plane. |
| YCbCr conversion sampler and image view | yes | yes | sampling state | no | Fix the reconstruction, range, model, component mapping, and chroma-location behavior. |
| Host-visible reference uniform | yes | yes | shader reads | host writes only | Supplies coordinates and acceptable minimum/maximum converted values. |
| Protected helper storage buffer | yes | yes | compute shaders reset, read, and atomically update it | no | Turns a comparison mismatch into a validation timeout. |
| Protected RGBA8 color image, fragment path | yes | yes | fragment writes, compute validator reads | no | Converts per-point comparison results into green or red pixels for second-stage validation. |
| Host-visible vertex buffer, fragment path | yes | yes | vertex shader reads | host writes only | Places one point at each output pixel. |

## What Is Checked

- Compute cases validate 50 sampled converted values directly against host-computed bounds.
- Fragment cases draw one point for every generated coordinate into a protected RGBA8 image. The test then checks 50 positions for green values in `[0.0, 0.9, 0.0, 1.0]` through `[0.0, 1.0, 0.0, 1.0]`.
- Both checks apply a `0.01` per-component threshold in the validator shader.
- The reference calculation accounts for format bit depth, filtering and conversion precision, sub-texel precision, address mode, color model, encoded range, chroma reconstruction, component mapping, and permitted implicit nearest-cosited behavior.
- A completed validation submission passes. `VK_TIMEOUT` fails. Other queue errors propagate through `VK_CHECK`.

## Behavior Parameter Identification

> **Behavior parameter:** color model intermediate node
>
> **Candidate values:** `rgb_identity`, `ycbcr_identity`, `ycbcr_709`, `ycbcr_601`, `ycbcr_2020`

Format, shader path, encoded range, chroma location, and disjoint binding are secondary dimensions. They change representation and execution coverage around the conversion selected by the color-model value.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `rgb_identity` | Protected sampling, component interpretation, filtering or reconstruction, descriptor setup, or bounds validation failed while source values should remain in the RGB model. |
| `ycbcr_identity` | Protected sampling, YCbCr range expansion, component interpretation, reconstruction, descriptor setup, or bounds validation failed without a YCbCr-to-RGB matrix conversion. |
| `ycbcr_709` | Protected sampling, BT.709 range/model conversion, chroma reconstruction, descriptor setup, or bounds validation failed. |
| `ycbcr_601` | Protected sampling, BT.601 range/model conversion, chroma reconstruction, descriptor setup, or bounds validation failed. |
| `ycbcr_2020` | Protected sampling, BT.2020 range/model conversion, chroma reconstruction, descriptor setup, or bounds validation failed. |

## Important Variations and Special Cases

- The Vulkan mustpass list contains 4,000 executable leaves across 64 formats. The Vulkan SC list contains 3,952 leaves.
- `compute` samples and validates the YCbCr image in one compute dispatch. `fragment` samples during a point-list draw and validates the protected RGBA8 result in a later compute dispatch.
- Registration fixes image tiling to `tiling_optimal`, texture and chroma filtering to nearest, both address modes to clamp-to-edge, and component mapping to identity.
- The leaf varies `cosited` or `midpoint`, with optional `_disjoint`. The same location is used for X and Y.
- Non-identity models are not registered for formats with fewer than three channels. `itu_narrow` is omitted when any of the first three component bit depths is below eight.
- `checkSupport()` prunes unsupported sampling, YCbCr conversion, chroma location, explicit-reconstruction, and disjoint combinations from execution.
- If the format requires explicit reconstruction, runtime setup forces it even though registration initializes the flag to false.
- For nearest implicit reconstruction with a cosited coordinate, the reference bounds also admit midpoint behavior permitted by the conversion rules.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Configuration and support pruning | [`TestConfig` and `checkSupport()`](../../../modules/vulkan/protected_memory/vktProtectedMemYCbCrConversionTests.cpp#L100-L217) | Defines the matrix fields and rejects unsupported format-feature combinations. |
| Conversion, sampler, and image view | [`createSampler()`, `createImageView()`, and `createConversion()`](../../../modules/vulkan/protected_memory/vktProtectedMemYCbCrConversionTests.cpp#L219-L297) | Attaches one conversion object consistently to the sampler and view. |
| Plane upload and image visibility | [`uploadYCbCrImage()`](../../../modules/vulkan/protected_memory/vktProtectedMemYCbCrConversionTests.cpp#L299-L414) | Copies every plane and transitions it for shader reads. |
| Device-side validator and result | [`validateImage()`](../../../modules/vulkan/protected_memory/vktProtectedMemYCbCrConversionTests.cpp#L458-L583) | Builds validation resources, dispatches 50 invocations, and turns timeout into failure. |
| Generated shaders | [`testShaders()`](../../../modules/vulkan/protected_memory/vktProtectedMemYCbCrConversionTests.cpp#L585-L738) | Emits the conversion-bearing compute and fragment shader paths. |
| Protected graphics path | [`renderYCbCrToColor()`](../../../modules/vulkan/protected_memory/vktProtectedMemYCbCrConversionTests.cpp#L781-L932) | Draws comparison results into the protected color image. |
| Source data and reference bounds | [`generateYCbCrImage()`](../../../modules/vulkan/protected_memory/vktProtectedMemYCbCrConversionTests.cpp#L934-L1092) | Generates plane gradients and permitted converted-value intervals. |
| End-to-end case | [`conversionTest()`](../../../modules/vulkan/protected_memory/vktProtectedMemYCbCrConversionTests.cpp#L1094-L1226) | Creates protected resources and selects compute or fragment validation. |
| Registration matrix | [`createYCbCrConversionTests()`](../../../modules/vulkan/protected_memory/vktProtectedMemYCbCrConversionTests.cpp#L1230-L1353) | Registers format, shader, model, range, chroma-location, and disjoint dimensions. |
| Protected-memory rules | [`memory.adoc`](../../../../vulkan-docs/src/chapters/memory.adoc#L5564-L5653) | Defines protected memory visibility and protected queue-operation constraints. |
| Sampler YCbCr conversion | [`samplers.adoc`](../../../../vulkan-docs/src/chapters/samplers.adoc#L773-L1049) | Defines conversion attachment and the create-info fields used by the test. |
| Conversion model meanings | [`VkSamplerYcbcrModelConversion`](../../../../vulkan-docs/src/chapters/samplers.adoc#L1052-L1095) | Defines identity, BT.709, BT.601, and BT.2020 behavior. |
| Descriptor count | [`VkSamplerYcbcrConversionImageFormatProperties`](../../../../vulkan-docs/src/chapters/capabilities.adoc#L935-L971) | Explains why one shader sampler can consume multiple descriptors. |
| Vulkan mustpass cases | [`vk-default/protected-memory.txt`](../../../mustpass/main/vk-default/protected-memory.txt) | Lists 4,000 executable Vulkan leaves. |
| Vulkan SC mustpass cases | [`vksc-default/protected-memory.txt`](../../../mustpass/main/vksc-default/protected-memory.txt) | Lists 3,952 executable Vulkan SC leaves. |

## Questions / Risk Points for User Audit

- Is the color-model intermediate node the right primary behavioral axis, with shader path and image representation treated as secondary dimensions?
- Is the two-stage fragment path clearly distinguished from direct compute validation?
- Does the description make clear that conversion occurs inside the sampled-image operation rather than in explicit shader arithmetic?
- Are the 50 checked coordinates described narrowly enough to avoid implying that fragment validation checks every rendered pixel?

## Conversion Notes for Final Wiki Rewrite

- Distill YCbCr conversion state, protected execution, and bound-based validation into short prerequisite bullets.
- Use the color-model values as `## Behavior Parameters` and copy the failure mapping table unchanged.
- Keep one auto-mode shader walkthrough for the direct compute case above. It exposes the conversion-bearing `texture()` call and timeout signal with less supporting graphics machinery than the fragment path.
- Put the complete parameter matrix in a compact table and explain fixed choices alongside generated values.
- Keep the protected upload, reference-bound calculation, compute/fragment split, and timeout result in runtime order.
- Move source navigation and spec grounding to the appendix.
