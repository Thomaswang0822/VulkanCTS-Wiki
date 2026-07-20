# Understanding Brief: rasterization.depth_bias_control / vktRasterizationDepthBiasControlTests.cpp

This brief prepares the rewrite of the `rasterization.depth_bias_control` Level-3 wiki page. It is
explanation-first and treats the CTS source as the primary authority.

Note: the `external/vulkan-docs/src/chapters/` directory was not present in this checkout, so the
Background Knowledge and Failure Cause Mapping below are grounded in CTS source comments plus the
`VK_EXT_depth_bias_control` extension semantics as observed in the test. Any spec wording should be
cross-checked against the canonical spec when it is restored.

## One-Sentence Test Purpose

This test checks whether `VK_EXT_depth_bias_control` produces a depth-buffer value equal to the
vertex sample depth plus the clamped target bias, across static and dynamic set mechanisms, with
and without depth-bias representation info, and across the supported depth/stencil attachment
formats.

Core question: **does the implementation apply the depth bias, the optional representation info,
and the depth-bias clamp such that the rendered depth falls within the format-sensitive threshold
of `sampleDepth + min(targetBias, depthBiasClamp)`?**

## Background Knowledge

### Classic depth bias and where it falls short

The unextended Vulkan depth-bias equation, set through `vkCmdSetDepthBias` or through
`VkPipelineRasterizationStateCreateInfo`, combines a slope factor, a constant factor, and a clamp.
The constant factor is specified in a format-dependent unit: the spec calls it a multiple of the
minimum resolvable difference `r` for the depth attachment format. That coupling makes the same
constant factor produce different effective biases on different formats and forces the
implementation to choose how to round.

Why it matters here:

- `VK_EXT_depth_bias_control` decouples the representation of the constant factor from the format
  by introducing a `VkDepthBiasRepresentationInfoEXT` pNext that selects one of three
  representations: `LEAST_REPRESENTABLE_VALUE_FORMAT_EXT`, `LEAST_REPRESENTABLE_VALUE_FORCE_UNORM_EXT`,
  or `FLOAT_EXT`.
- A `depthBiasExact` flag further requests that the implementation apply the constant factor with
  no extra rounding slack.
- The test chooses factors so that the requested bias, after clamping, lands at a known target
  depth; it then compares the rendered depth with a threshold derived from the same minimum
  resolvable difference math the spec uses.

### Minimum resolvable difference `r`

`r` is the smallest bias step the format can express. The test mirrors the spec rules in
[`calcMinResolvableDiff()`](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L121-L183):

| Representation | Fixed-point channel class | Floating-point channel class |
|----------------|---------------------------|------------------------------|
| `LEAST_REPRESENTABLE_VALUE_FORMAT_EXT` | `r` up to `2 * 2^(-n)` where `n` is the bit width; `exact` removes the factor of 2 | `r = 2^(e-n)` where `e` is the value exponent and `n` is the mantissa bit count |
| `LEAST_REPRESENTABLE_VALUE_FORCE_UNORM_EXT` | same as above using the format bit width | `r` up to `2 * 2^(-(mantissa_bits + 1))`; `exact` removes the factor of 2 |
| `FLOAT_EXT` | `r = 1.0` always | `r = 1.0` always |

Why it matters here:

- The host computes a `[r.first, r.second]` pair, where `r.first` is the most precise value and
  `r.second` is the least precise value the spec allows.
- The constant factor is computed against `r.first` so that the requested target bias is reached
  when the implementation uses the most precise representation.
- The depth threshold absorbs the slack between `r.first` and `r.second`, plus the format's own
  depth representation error.

### Set mechanisms and representation-info compatibility

Three set mechanisms are exercised, each corresponding to a different Vulkan entry point
[`SetMechanism`](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L202-L207):

| Mechanism | Entry point | Representation info? |
|-----------|-------------|----------------------|
| `STATIC` | `VkPipelineRasterizationStateCreateInfo` pNext | Optional, chained at pipeline creation |
| `DYNAMIC_1` | `vkCmdSetDepthBias` | Not allowed; the classic command has no pNext |
| `DYNAMIC_2` | `vkCmdSetDepthBias2EXT` with `VkDepthBiasInfoEXT` | Optional, chained through the info struct's pNext |

Why it matters here:

- `DYNAMIC_1` has no pNext chain, so any case that combines a non-empty `VkDepthBiasRepresentationInfoEXT`
  with `DYNAMIC_1` is invalid. The registration loop skips those combinations
  [vktRasterizationDepthBiasControlTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L832-L837).
- For `STATIC`, the representation info is chained into the rasterization state create info only
  when it is present, and the constant factor / clamp / slope factor are baked into the pipeline.
- For `DYNAMIC_2`, the representation info is chained into `VkDepthBiasInfoEXT` when present, and
  the bias factors are set at record time.

### Secondary command-buffer inheritance

A small subset of cases record the draw into a secondary command buffer
[`secondaryCmdBufferCases[]`](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L791-L802).
The three secondary variants are:

- `_secondary_cmd_buffer`: the secondary buffer is recorded with the render pass and framebuffer
  objects passed in.
- `_secondary_cmd_buffer_inherit_renderpass`: the secondary buffer inherits the render pass via
  `VkCommandBufferInheritanceInfo` and also receives the framebuffer object.
- `_secondary_cmd_buffer_unspecified_fb`: the secondary buffer inherits the render pass but the
  framebuffer handle is `VK_NULL_HANDLE`.

Why it matters here:

- These variants exist to make sure the depth-bias state set in a secondary command buffer takes
  effect when the buffer is executed inside a primary render pass.
- The pruning rules limit secondary-command-buffer cases to a small representative subset so the
  matrix stays manageable.

## One Concrete Example

Representative test name from mustpass:

```text
dEQP-VK.rasterization.depth_bias_control.d16_unorm.format_exact.constant.constant_depth_0_25.target_bias_0_125.static_no_clamp
```

Simplified behavior for this case:

1. Attachment format is `VK_FORMAT_D16_UNORM`. `d16_unorm` is a fixed-point format with bit width 16.
2. Representation info selects `LEAST_REPRESENTABLE_VALUE_FORMAT_EXT` with `depthBiasExact = TRUE`.
3. Used factor is `CONSTANT`, so geometry is generated with a constant depth of 0.25 and the slope
   factor is forced to 0 by geometry (M = 0).
4. The sample depth at the single framebuffer pixel is 0.25.
5. For an exact, fixed-point, format representation, `r.first = r.second = 2^(-16)`.
6. The host sets `depthBiasConstantFactor = targetBias / r.first = 0.125 / 2^(-16) = 8192`.
7. Clamp is 0, so the expected depth is `sampleDepth + targetBias = 0.25 + 0.125 = 0.375`.
8. The depth threshold is `(r.second - r.first) * depthBiasConstantFactor + formatDepthError`,
   which is 0 for the exact case plus the D16 representation error around the expected depth.
9. The test renders a 1x1 framebuffer, copies the depth buffer back, and compares with
   `tcu::dsThresholdCompare()`. It also checks the color buffer is the solid `(0, 0, 1, 1)` with
   `tcu::floatThresholdCompare()` and a zero threshold.

Conceptual host-side pseudo-code, reconstructed from the source:

```text
sampleDepth      = constantDepth          // 0.25
r                = calcMinResolvableDiff(format, repr, exact, sampleDepth)   // (2^-16, 2^-16)
constFactor      = targetBias / r.first   // 8192
slopeFactor      = 0                      // usedFactor == CONSTANT
depthBiasClamp   = 0                      // ClampCase::ZERO
clampedBias      = min(targetBias, depthBiasClamp == 0 ? targetBias : depthBiasClamp)
expectedDepth    = sampleDepth + clampedBias   // 0.375
threshold        = (constFactor * r.second - constFactor * r.first)
                 + getDepthErrorThreshold(format, expectedDepth)
```

Important simplifications:

- The host always renders into a 1x1 framebuffer, so there is exactly one depth sample to compare.
- The fragment shader writes a solid color, so color validation is exact and format-independent.

## End-to-End Test Flow

```text
1. [host] register the matrix
   1.1 create the `depth_bias_control` root
   1.2 for each of the six attachment formats, build the nested repr-info / used-factor /
       constant-depth / target-bias / set-mechanism / clamp / secondary-command-buffer tree
   1.3 skip representation-info + DYNAMIC_1 combinations and the secondary-command-buffer
       reduction filters

2. [host] check support
   2.1 require `VK_EXT_depth_bias_control`
   2.2 require `depthBiasExact` for exact representation cases
   2.3 require `leastRepresentableValueForceUnormRepresentation` for force-UNORM cases
   2.4 require `floatRepresentation` for float cases
   2.5 require the selected depth attachment format to support depth-stencil attachment and
       transfer-source usage

3. [host] generate shader artifacts
   3.1 emit a trivial vertex shader that copies `inPos` to `gl_Position`
   3.2 emit a trivial fragment shader that writes a constant `(0, 0, 1, 1)` color

4. [host] set up resources
   4.1 create a 1x1 `R8G8B8A8_UNORM` color image with a backing host-visible buffer
   4.2 create a 1x1 depth image of the selected format with a backing host-visible buffer
   4.3 upload the vertex buffer; vertices form a triangle strip covering the framebuffer with
       depth chosen so that the sample depth is `constantDepth` (CONSTANT factor) or 0.5 (SLOPE)
   4.4 build a render pass with the color and depth attachments, a framebuffer, and a graphics
       pipeline with `depthBiasEnable = VK_TRUE` and `depthCompareOp = LESS_OR_EQUAL`

5. [host] compute bias parameters and record commands
   5.1 compute `r.first` and `r.second` from the format, representation, exact flag, and sample
       depth
   5.2 compute `depthBiasConstantFactor = targetBias / r.first` for the CONSTANT path or
       `depthBiasSlopeFactor = targetBias` for the SLOPE path (M = 1 by construction)
   5.3 compute `depthBiasClamp` from the clamp case (0, 2x target, or 0.5x target)
   5.4 for STATIC, bake the factors and optional repr-info pNext into the pipeline
   5.5 for DYNAMIC_1, set the factors via `vkCmdSetDepthBias` (no repr info)
   5.6 for DYNAMIC_2, set the factors and optional repr-info pNext via `vkCmdSetDepthBias2EXT`
   5.7 optionally record the draw into a secondary command buffer and execute it inside the
       primary render pass

6. [device] rasterize one triangle strip covering the single pixel
   6.1 vertex shader passes the position through
   6.2 fixed-function depth bias applies the configured factors, representation info, and clamp
   6.3 fragment shader writes the solid color
   6.4 depth test writes the biased depth

7. [host] copy back and verify
   7.1 transition color and depth images to transfer-source and copy them to their backing buffers
   7.2 invalidate the host-visible allocations
   7.3 build a reference depth level cleared to `expectedDepth = sampleDepth + clampedBias`
   7.4 compute the depth threshold from the constant-factor slack plus the format depth error
   7.5 compare depth with `tcu::dsThresholdCompare()`
   7.6 compare color with `tcu::floatThresholdCompare()` against `(0, 0, 1, 1)` with zero threshold
   7.7 fail the case if either comparison fails
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

| Artifact | Generated/loaded where | Role |
|----------|------------------------|------|
| Vertex shader | [`DepthBiasControlCase::initPrograms()`](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L350-L367) | Trivial: `gl_Position = inPos`. Depth comes from the vertex `z`; the shader does not compute bias. |
| Fragment shader | same | Trivial: writes the constant `kOutColor = (0, 0, 1, 1)`. Used only to produce a verifiable color output. |
| Pipeline state | [`iterate()`](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L487-L536) | Bakes `depthBiasEnable`, the static factors, the clamp, and the optional repr-info pNext when STATIC is selected. |
| Render pass and framebuffer | [`iterate()`](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L439-L448) | One color attachment, one depth attachment, 1x1 extent. |

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Color image (`R8G8B8A8_UNORM`) | Yes, 1x1, color-attachment + transfer-source usage | Yes, color attachment | Written by fragment shader | Copied to backing buffer | Verifies the fragment shader ran and produced the expected solid color. |
| Depth image (selected format) | Yes, 1x1, depth-stencil-attachment + transfer-source usage | Yes, depth attachment | Written by depth test after bias | Copied to backing buffer | The primary check target; carries the biased depth value. |
| Color backing buffer | Yes, host-visible | Transfer destination | Receives copied color image | Yes, invalidated then read | Lets the host run `tcu::floatThresholdCompare()`. |
| Depth backing buffer | Yes, host-visible | Transfer destination | Receives copied depth image | Yes, invalidated then read | Lets the host run `tcu::dsThresholdCompare()`. |
| Vertex buffer | Yes, host-visible | Vertex buffer at binding 0 | Read by vertex shader | No | Four vertices forming a triangle strip covering the 1x1 framebuffer; the `z` values encode the sample depth. |
| Render pass | Yes | Bound at `vkCmdBeginRenderPass` | Drives the color/depth attachment layout transitions | No | One color plus one depth attachment, single subpass. |
| Framebuffer | Yes | Bound at `vkCmdBeginRenderPass` | References the color and depth image views | No | 1x1 extent, matches the rendered region. |
| Graphics pipeline | Yes | Bound at `vkCmdBindPipeline` | Holds the static bias state when STATIC is selected | No | Carries the rasterization, depth-stencil, and dynamic-state create info. |
| Optional secondary command buffer | Yes, when a secondary variant is selected | Executed by `vkCmdExecuteCommands` | Records the bind/draw | No | Exercises secondary-command-buffer inheritance paths. |

## What Is Checked

### Device-side checks

There are no shader-side pass/fail decisions. The fragment shader writes a constant color; the
depth test writes the biased depth. All checks are host-side.

### Host-side checks

| Check | Reference | Threshold | Comparator |
|-------|-----------|-----------|------------|
| Depth buffer | `sampleDepth + clampedBias` cleared into a reference level | `(depthBiasConstantFactor * (r.second - r.first)) + getDepthErrorThreshold(format, expectedDepth)` | `tcu::dsThresholdCompare()` |
| Color buffer | `kOutColor = (0, 0, 1, 1)` | `(0, 0, 0, 0)` | `tcu::floatThresholdCompare()` |

The clamp behavior is encoded in `clampedBias = min(targetBias, depthBiasClamp == 0 ? targetBias : depthBiasClamp)`
[vktRasterizationDepthBiasControlTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L644-L646).
A case passes only when both comparisons succeed.

## Behavior Parameter Identification

> **Behavior parameter:** set mechanism / depth-bias representation-info path
>
> **Candidate values:** `static` (pipeline-baked state with optional repr-info pNext),
> `dynamic_set_1` (`vkCmdSetDepthBias`, never carries repr info), `dynamic_set_2`
> (`vkCmdSetDepthBias2EXT` with optional repr-info pNext via `VkDepthBiasInfoEXT`).

The attachment format is treated as a configuration dimension, not the behavioral axis. The set
mechanism is the axis because it changes which Vulkan entry point carries the bias parameters and
whether representation info can be expressed at all.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `static` | The pipeline-baked depth-bias factors, clamp, or chained `VkDepthBiasRepresentationInfoEXT` were not applied correctly at rasterization time, including the representation-selection and `depthBiasExact` semantics. |
| `dynamic_set_1` | The `vkCmdSetDepthBias` dynamic state was not recorded, inherited, or applied with the correct factors and clamp; representation info is not exercised by this value. |
| `dynamic_set_2` | The `vkCmdSetDepthBias2EXT` command, its `VkDepthBiasInfoEXT` pNext chain, the representation info, or the `depthBiasExact` flag was not applied or inherited correctly, including secondary-command-buffer execution paths. |

All three values share the same host-side verification path: the depth comparison fails if the
rendered depth leaves the `[expectedDepth - threshold, expectedDepth + threshold]` band, and the
color comparison fails if the fragment shader output is not exactly `(0, 0, 1, 1)`.

## Important Variations and Special Cases

### Representation info variations

Seven representation-info variants are registered
[`reprInfoCases[]`](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L718-L734):

| Variant | Representation | `depthBiasExact` |
|---------|----------------|------------------|
| `no_repr_info` | absent | absent |
| `format_inexact` | `LEAST_REPRESENTABLE_VALUE_FORMAT_EXT` | FALSE |
| `format_exact` | `LEAST_REPRESENTABLE_VALUE_FORMAT_EXT` | TRUE |
| `force_unorm_inexact` | `LEAST_REPRESENTABLE_VALUE_FORCE_UNORM_EXT` | FALSE |
| `force_unorm_exact` | `LEAST_REPRESENTABLE_VALUE_FORCE_UNORM_EXT` | TRUE |
| `float_inexact` | `FLOAT_EXT` | FALSE |
| `float_exact` | `FLOAT_EXT` | TRUE |

`no_repr_info` is the legacy behavior; the host still computes `r` using the format representation
so the constant factor lands at the target bias, but the implementation is free to use the legacy
rounding rules. The `exact` variants request the tightest rounding the spec allows; the inexact
variants allow up to a factor of 2 of slack, which the threshold absorbs.

### Used factor and constant depth

The matrix picks which factor carries the bias
[`usedFactorCases[]`](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L709-L716):

- `slope`: geometry has depths 0 and 1 so the maximum depth slope M is 1, `depthBiasSlopeFactor`
  is set directly to `targetBias`, and `depthBiasConstantFactor` is 0. The sample depth is 0.5.
- `constant`: geometry uses a constant depth, M is 0, `depthBiasSlopeFactor` is 0, and
  `depthBiasConstantFactor = targetBias / r.first`. The sample depth equals that constant depth.

The `constant` path uses five constant depths (`0.25`, `0.3125`, near `0.5`, `0.625`, `0.125`)
[`constantDepthConstantCases`](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L747-L753)
to exercise different exponents of the floating-point sample depth, which changes `r` for the
format representation on floating-point depth formats.

### Clamp cases

Three clamp cases are registered
[`clampValueCases[]`](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L781-L789):

| Clamp case | `depthBiasClamp` | Effect on `clampedBias` |
|------------|------------------|-------------------------|
| `_no_clamp` | 0 | No clamp; `clampedBias = targetBias` |
| `_no_effective_clamp` | `2 * targetBias` | Above the target; `clampedBias = targetBias` |
| `_clamp_to_half` | `0.5 * targetBias` | Below the target; `clampedBias = 0.5 * targetBias` |

### Secondary command-buffer reduction

To keep the matrix manageable, secondary-command-buffer variants are restricted by
[`vktRasterizationDepthBiasControlTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L858-L875)
to cases that use the `CONSTANT` factor, a non-`DYNAMIC_1` mechanism, the `_no_clamp` clamp case,
and a non-empty representation info. Direct (non-secondary) cases cover the rest of the matrix.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Minimum resolvable difference math | [calcMinResolvableDiff()](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L121-L183) | Mirrors the spec rules for `r` per representation and channel class; drives factor and threshold computation. |
| Depth error threshold | [getDepthErrorThreshold()](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L187-L192) | Adds the format's own depth representation error to the bias slack. |
| Set mechanism enum | [SetMechanism](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L202-L207) | Defines the three values that form the primary behavioral axis. |
| Test parameters | [TestParams](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L227-L263) | Carries the format, repr info, mechanism, target bias, used factor, constant depth, clamp, and secondary-command-buffer flags. |
| Support checks | [checkSupport()](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L305-L343) | Gates on `VK_EXT_depth_bias_control`, `depthBiasExact`, force-UNORM, float representation, and format support. |
| Shader generation | [initPrograms()](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L350-L367) | Emits the trivial vertex/fragment pair; confirms shaders are not part of the tested behavior. |
| Pipeline and bias setup | [iterate()](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L460-L593) | Computes factors, builds the pipeline, and records the bias command for each mechanism. |
| Result verification | [iterate()](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L637-L695) | Computes `expectedDepth`, the depth threshold, and runs `tcu::dsThresholdCompare()` plus `tcu::floatThresholdCompare()`. |
| Matrix registration and pruning | [createDepthBiasControlTests()](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L700-L910) | Builds the six-format tree and applies the representation-info + DYNAMIC_1 skip and the secondary-command-buffer reduction. |
| Mustpass examples | [rasterization.txt](../../../mustpass/main/vk-default/rasterization.txt#L400-L411) | Confirms the registered case names and hierarchy. |

## Questions / Risk Points for User Audit

- [x] The primary behavioral axis is the set mechanism, not the attachment format. The format is a
  configuration dimension because the same mechanism is exercised across all six formats.
- [x] Shader code is not part of the tested behavior. The vertex shader is a pass-through and the
  fragment shader writes a constant color; no shader walkthrough is needed in the final page.
- [x] The `clampedBias` formula uses `min(targetBias, depthBiasClamp == 0 ? targetBias : depthBiasClamp)`,
  which treats a zero clamp as "no clamp" rather than "clamp to zero". This matches the source at
  [vktRasterizationDepthBiasControlTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L644-L646).
- [x] The depth threshold absorbs both the representation-info slack and the format depth error, so
  an inexact representation can pass as long as the rendered depth falls inside the widened band.
- [x] The `external/vulkan-docs/src/chapters/` directory was missing from this checkout; the brief
  grounds spec claims in CTS source comments and the visible `VK_EXT_depth_bias_control` data.
  Spec wording should be cross-checked when the spec tree is restored.

## Conversion Notes for Final Wiki Rewrite

- Carry the set-mechanism axis into `## Behavior Parameters` with three subsections: `static`,
  `dynamic_set_1`, `dynamic_set_2`.
- Distill the background into a compact prerequisite list: classic depth bias and its
  format-coupled constant factor, minimum resolvable difference `r`, representation info and
  `depthBiasExact`, set-mechanism compatibility, and secondary-command-buffer inheritance.
- State briefly in `## Shader Analysis` that the shaders are trivial and not part of the tested
  behavior; do not create walkthrough subsections and do not invoke `shader-analyzer`.
- Preserve the resource table in a more formal final-wiki style because the depth and color
  backing buffers are the verification path.
- Keep the clamp-case, used-factor, and representation-info tables as parameter-dimension
  evidence rather than narrative.
- Move detailed pruning rules and feature gates into `## Case Pruning`.
- Copy the `### Failure Cause Mapping` table directly into the final page; write
  `### Cause Analysis` fresh during the rewrite.
- Do not copy the beginner-focused prose verbatim into the final page; convert it to the Level-3
  wiki style.
