## Overview

**Core question:** does the implementation apply `VK_EXT_depth_bias_control` depth-bias factors, the
optional depth-bias representation info, and the depth-bias clamp so that the rendered depth falls
within a format-sensitive threshold of `sampleDepth + min(targetBias, depthBiasClamp)`?

- [vktRasterizationDepthBiasControlTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp)
  implements the `rasterization.depth_bias_control` test family registered by
  [`createDepthBiasControlTests()`](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L700-L910).
- The family builds a single matrix over six depth/stencil attachment formats, seven representation-info
  variants, two used factors, six constant-depth cases, three target biases, three set mechanisms, three
  clamp cases, and four secondary-command-buffer modes.
- The core test renders a 1x1 framebuffer with depth bias enabled, copies the depth and color buffers
  back, and compares the depth against `sampleDepth + clampedBias` with a threshold derived from the
  minimum resolvable difference `r` and the format depth error.
- The set mechanism is the primary behavioral axis: it changes which Vulkan entry point carries the
  bias parameters and whether representation info can be expressed at all. The attachment format is a
  configuration dimension that changes the threshold math, not the mechanism under test.

## Background Knowledge

For the shared concept depth bias, see [Background Knowledge](../../categories/rasterization.md#background-knowledge) of the `rasterization` page.

- **`VK_EXT_depth_bias_control` decouples the format coupling.** The constant factor is a multiple of the minimum resolvable difference `r` for the depth attachment format, so the same factor produces different effective biases on different formats and forces the implementation to choose how to round; `VK_EXT_depth_bias_control` decouples this coupling.
- **`VK_EXT_depth_bias_control` representation info.** A `VkDepthBiasRepresentationInfoEXT` pNext
  decouples the constant factor's representation from the format by selecting
  `LEAST_REPRESENTABLE_VALUE_FORMAT_EXT`, `LEAST_REPRESENTABLE_VALUE_FORCE_UNORM_EXT`, or `FLOAT_EXT`.
  A `depthBiasExact` flag requests the tightest rounding the spec allows. The test chains this struct
  into the pipeline (`STATIC`), into `VkDepthBiasInfoEXT` (`DYNAMIC_2`), or omits it (`DYNAMIC_1` and
  the `no_repr_info` variant).
- **Minimum resolvable difference `r`.** `r` is the smallest bias step the format can express. The host
  mirrors the spec rules in [`calcMinResolvableDiff()`](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L121-L183)
  and computes a `[r.first, r.second]` pair, where `r.first` is the most precise value and `r.second` is
  the least precise value the spec allows. The constant factor is computed against `r.first` so the
  requested target bias is reached when the implementation uses the most precise representation; the
  depth threshold absorbs the slack between `r.first` and `r.second`.
- **Set-mechanism compatibility.** `vkCmdSetDepthBias` has no pNext chain, so representation info cannot
  be expressed through it. `vkCmdSetDepthBias2EXT` accepts a `VkDepthBiasInfoEXT` whose pNext can carry
  the representation info. The static pipeline path chains the representation info into
  `VkPipelineRasterizationStateCreateInfo`. This compatibility rule drives both the registration skip
  and the behavioral axis.
- **Secondary command-buffer inheritance.** A small subset of cases record the draw into a secondary
  command buffer to confirm the bias state set there takes effect when the buffer is executed inside a
  primary render pass. The three secondary variants differ in whether the render pass and framebuffer
  are passed explicitly or inherited through `VkCommandBufferInheritanceInfo`.

## Registration Hierarchy

```text
rasterization.depth_bias_control
├── d16_unorm
├── x8_d24_unorm_pack32
├── d32_sfloat
├── d16_unorm_s8_uint
├── d24_unorm_s8_uint
└── d32_sfloat_s8_uint
```

Each direct child is one of the six attachment formats in
[`attachmentFormats`](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L704-L707).
Beneath each format, the registration loop nests representation-info, used-factor, constant-depth,
target-bias, and leaf test case levels. Leaf test case names are composed from the set mechanism, the
clamp suffix, and the optional secondary-command-buffer suffix
[vktRasterizationDepthBiasControlTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L877-L889).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Attachment format | `d16_unorm`, `x8_d24_unorm_pack32`, `d32_sfloat`, `d16_unorm_s8_uint`, `d24_unorm_s8_uint`, `d32_sfloat_s8_uint` | Changes the depth buffer precision, the channel class (fixed-point or floating-point), and the threshold math. Configuration dimension, not the behavioral axis. | [attachmentFormats](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L704-L707) |
| Representation info | `no_repr_info`, `format_inexact`, `format_exact`, `force_unorm_inexact`, `force_unorm_exact`, `float_inexact`, `float_exact` | Selects the constant-factor representation and whether `depthBiasExact` is requested. Drives the `r` computation and the threshold slack. | [reprInfoCases](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L718-L734) |
| Used factor | `slope`, `constant` | Picks whether `depthBiasSlopeFactor` or `depthBiasConstantFactor` carries the target bias. The slope path uses M = 1 geometry and sample depth 0.5; the constant path uses M = 0 geometry and a chosen constant depth. | [usedFactorCases](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L709-L716) |
| Constant depth | `slope_depth_1_0` (slope placeholder), `constant_depth_0_25`, `constant_depth_0_3125`, `constant_depth_close_to_0_5`, `constant_depth_0_625`, `constant_depth_0_125` | The slope placeholder is unused for the slope path. The five constant values exercise different exponents of the floating-point sample depth, which changes `r` for the format representation on floating-point depth formats. | [constantDepthConstantCases](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L743-L753) |
| Target bias | `target_bias_0_0625`, `target_bias_0_125`, `target_bias_0_25` | The desired pre-clamp bias. The host computes factors so the rendered depth lands at `sampleDepth + clampedBias`. | [targetBiasCases](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L755-L763) |
| Set mechanism | `static`, `dynamic_set_1`, `dynamic_set_2` | The primary behavioral axis. Selects the pipeline-baked path, `vkCmdSetDepthBias`, or `vkCmdSetDepthBias2EXT`. | [setMechanismCases](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L765-L773) |
| Clamp case | `_no_clamp`, `_no_effective_clamp`, `_clamp_to_half` | Sets `depthBiasClamp` to 0, `2 * targetBias`, or `0.5 * targetBias`. The first two leave `clampedBias = targetBias`; the third clamps to half. | [clampValueCases](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L781-L789) |
| Secondary command buffer | ``, `_secondary_cmd_buffer`, `_secondary_cmd_buffer_inherit_renderpass`, `_secondary_cmd_buffer_unspecified_fb` | Records the draw into a secondary command buffer with explicit, inherited, or framebuffer-unspecified inheritance. Reduction-filtered to a representative subset. | [secondaryCmdBufferCases](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L791-L802) |

## Behavior Parameters

The primary behavioral axis is the **set mechanism**. It changes which Vulkan entry point carries the
bias parameters and whether representation info can be expressed. The attachment format is a
configuration dimension because the same mechanism is exercised across all six formats; it changes
the threshold math, not the mechanism under test. The candidate values are `static`,
`dynamic_set_1`, and `dynamic_set_2`.

### static — pipeline-baked bias state with optional representation info

`static` bakes the depth-bias factors, the clamp, and the optional `VkDepthBiasRepresentationInfoEXT`
pNext into [`VkPipelineRasterizationStateCreateInfo`](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L487-L501)
at pipeline creation time. The pipeline enables `depthBiasEnable = VK_TRUE` and uses
`depthCompareOp = LESS_OR_EQUAL`. The representation info is chained into the rasterization state
create info only when present
[vktRasterizationDepthBiasControlTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L485).
Because the state is static, the dynamic-state list is empty and no `vkCmdSetDepthBias*` command is
recorded. This value exercises the implementation's handling of representation info and `depthBiasExact`
in the pipeline create path.

### dynamic_set_1 — `vkCmdSetDepthBias` without representation info

`dynamic_set_1` adds `VK_DYNAMIC_STATE_DEPTH_BIAS` to the pipeline and records
[`vkCmdSetDepthBias`](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L573-L577)
with the computed factors and clamp. The classic command has no pNext chain, so representation info
cannot be expressed. The registration loop skips any case that combines a non-empty representation
info with `dynamic_set_1`
[vktRasterizationDepthBiasControlTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L832-L837),
so this value only covers the `no_repr_info` representation variant. It exercises the legacy dynamic
state path. Secondary-command-buffer inheritance is not exercised by this value because the
registration reduction filters `dynamic_set_1` out of secondary variants
[vktRasterizationDepthBiasControlTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L858-L875)
(see `## Case Pruning`).

### dynamic_set_2 — `vkCmdSetDepthBias2EXT` with optional representation info

`dynamic_set_2` adds `VK_DYNAMIC_STATE_DEPTH_BIAS` to the pipeline and records
[`vkCmdSetDepthBias2EXT`](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L578-L590)
with a `VkDepthBiasInfoEXT` whose pNext carries the `VkDepthBiasRepresentationInfoEXT` when present.
This value is the dynamic counterpart of `static` for representation-info coverage: it exercises the
extended dynamic command, its pNext chain handling, the representation selection, and the
`depthBiasExact` flag. Secondary-command-buffer inheritance cases are reduced to this mechanism and
`static` because `dynamic_set_1` cannot carry representation info.

## Shader Analysis

Shader code is not part of the tested behavior. The vertex shader is a pass-through that copies
`inPos` to `gl_Position`, and the fragment shader writes the constant `kOutColor = (0, 0, 1, 1)`. The
depth value comes from the vertex `z` and the fixed-function depth-bias unit; no shader participates
in the bias computation or the pass/fail decision. Both shaders are emitted by
[`DepthBiasControlCase::initPrograms()`](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L350-L367)
and are identical across every case in the matrix. No representative shader walkthrough is needed, and
`shader-analyzer` is not invoked.

## Runtime Execution and Result Checking

- **Resource setup.** The host creates a 1x1 `R8G8B8A8_UNORM` color image and a 1x1 depth image of the
  selected format, each backed by a host-visible buffer for readback
  [vktRasterizationDepthBiasControlTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L388-L401).
  A vertex buffer holds four vertices forming a triangle strip that covers the single pixel. The
  left-side vertices use depth 0 and the right-side vertices use depth 1 for the slope path, or all
  vertices use the chosen constant depth for the constant path
  [vktRasterizationDepthBiasControlTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L421-L427).
- **Sample depth.** The sample depth is 0.5 for the slope path (M = 1) and `constantDepth` for the
  constant path (M = 0).
- **Factor computation.** The host computes `r.first` and `r.second` from the format, the
  representation, the `depthBiasExact` flag, and the sample depth
  [`calcMinResolvableDiff()`](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L121-L183).
  For the constant path, `depthBiasConstantFactor = targetBias / r.first` and
  `depthBiasSlopeFactor = 0`. For the slope path, `depthBiasSlopeFactor = targetBias` (M = 1 by
  construction) and `depthBiasConstantFactor = 0`.
- **Clamp computation.** The clamp value comes from the clamp case: 0 for `_no_clamp`,
  `2 * targetBias` for `_no_effective_clamp`, and `0.5 * targetBias` for `_clamp_to_half`
  [vktRasterizationDepthBiasControlTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L839-L856).
- **Pipeline and bias recording.** The graphics pipeline enables `depthBiasEnable` and
  `depthCompareOp = LESS_OR_EQUAL`. For `static`, the factors, the clamp, and the optional repr-info
  pNext are baked into the rasterization state. For `dynamic_set_1` and `dynamic_set_2`, the pipeline
  lists `VK_DYNAMIC_STATE_DEPTH_BIAS` and the bias is recorded via `vkCmdSetDepthBias` or
  `vkCmdSetDepthBias2EXT` respectively
  [vktRasterizationDepthBiasControlTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L521-L593).
- **Secondary command buffer.** When a secondary variant is selected, the bind and draw are recorded
  into a secondary command buffer that is executed by `vkCmdExecuteCommands` inside the primary render
  pass. The three secondary variants differ in whether the render pass and framebuffer are passed
  explicitly or inherited through `VkCommandBufferInheritanceInfo`
  [vktRasterizationDepthBiasControlTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L543-L566).
- **Render.** The host begins the render pass, binds the pipeline and vertex buffer, records the bias
  command when dynamic, draws the triangle strip, and ends the render pass
  [vktRasterizationDepthBiasControlTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L559-L601).
- **Copyback.** The host transitions the color and depth images to `TRANSFER_SRC_OPTIMAL`, copies them
  to their backing buffers, and inserts a transfer-to-host barrier
  [vktRasterizationDepthBiasControlTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L604-L632).
  After submission, it invalidates the host-visible allocations.
- **Expected depth.** `clampedBias = min(targetBias, depthBiasClamp == 0 ? targetBias : depthBiasClamp)`
  and `expectedDepth = sampleDepth + clampedBias`
  [vktRasterizationDepthBiasControlTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L644-L647).
  A zero clamp is treated as "no clamp", not "clamp to zero".
- **Depth threshold.** `constantBiasMin = depthBiasConstantFactor * r.first`,
  `constantBiasMax = depthBiasConstantFactor * r.second`,
  `constantBiasErrorThres = constantBiasMax - constantBiasMin`, and
  `depthThreshold = constantBiasErrorThres + getDepthErrorThreshold(format, expectedDepth)`
  [vktRasterizationDepthBiasControlTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L649-L657).
  The threshold absorbs both the representation-info slack and the format depth representation error.
- **Pass/fail.** Depth is compared with
  [`tcu::dsThresholdCompare()`](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L677-L683)
  against a reference level cleared to `expectedDepth`. Color is compared with
  [`tcu::floatThresholdCompare()`](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L685-L690)
  against `(0, 0, 1, 1)` with a zero threshold. The case passes only when both comparisons succeed.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `static` | The pipeline-baked depth-bias factors, clamp, or chained `VkDepthBiasRepresentationInfoEXT` were not applied correctly at rasterization time, including the representation-selection and `depthBiasExact` semantics. |
| `dynamic_set_1` | The `vkCmdSetDepthBias` dynamic state was not recorded, inherited, or applied with the correct factors and clamp; representation info is not exercised by this value. |
| `dynamic_set_2` | The `vkCmdSetDepthBias2EXT` command, its `VkDepthBiasInfoEXT` pNext chain, the representation info, or the `depthBiasExact` flag was not applied or inherited correctly, including secondary-command-buffer execution paths. |

All three values share the same host-side verification path: the depth comparison fails if the
rendered depth leaves the `[expectedDepth - threshold, expectedDepth + threshold]` band, and the color
comparison fails if the fragment shader output is not exactly `(0, 0, 1, 1)`.

### Cause Analysis

#### Static bias state or representation info misapplied

**Possible failure symptoms:** A `static` case fails the depth comparison. The rendered depth is
outside the `[expectedDepth - threshold, expectedDepth + threshold]` band, and the log reports the
expected depth, the threshold, and the found depth. Color comparison succeeds because the fragment
shader is unchanged.

**Possible implementation causes:** The static path chains the representation info into
`VkPipelineRasterizationStateCreateInfo` and bakes the factors and clamp at pipeline creation. A
grounded investigation should check whether the implementation honors the chained
`VkDepthBiasRepresentationInfoEXT` when the pipeline is created, whether `depthBiasExact` tightens the
rounding as the spec requires, and whether the constant factor is interpreted in the selected
representation unit rather than the legacy format-coupled unit. The format-coupled legacy unit and the
new representation-selected unit can produce different effective biases for the same factor, so a
silent fallback to the legacy interpretation would land outside the threshold. Source-level
investigation is needed for cases where the representation info is present but the threshold is
narrow (the `exact` variants).

#### `vkCmdSetDepthBias` dynamic state mishandled

**Possible failure symptoms:** A `dynamic_set_1` case fails the depth comparison. Because this value
only covers the `no_repr_info` variant, a failure here isolates the legacy dynamic command from
representation-info handling.

**Possible implementation causes:** The pipeline lists `VK_DYNAMIC_STATE_DEPTH_BIAS` and the host
records `vkCmdSetDepthBias` with the computed factors and clamp. A grounded investigation should check
whether the dynamic state was recorded at the right command-buffer level, whether it was inherited
correctly when a secondary command buffer is used (the `no_repr_info` path is the only dynamic path
that could exercise secondary command buffers for `dynamic_set_1`, but the registration reduction
filters secondary variants out of `dynamic_set_1`), and whether the clamp was applied as "no clamp
when zero" rather than "clamp to zero". A driver that applies the clamp literally when the value is
zero would clamp the bias to zero and produce a depth equal to `sampleDepth`, which is outside the
threshold for any nonzero target bias.

#### `vkCmdSetDepthBias2EXT` or its pNext chain mishandled

**Possible failure symptoms:** A `dynamic_set_2` case fails the depth comparison. The rendered depth
is outside the threshold band. Failures that appear only when representation info is present point to
the pNext chain; failures that also appear in the `no_repr_info` variant point to the base command.

**Possible implementation causes:** The host records `vkCmdSetDepthBias2EXT` with a
`VkDepthBiasInfoEXT` whose pNext carries the representation info when present. A grounded investigation
should check whether the implementation reads the pNext chain of `VkDepthBiasInfoEXT`, whether the
representation selection and `depthBiasExact` flag are honored, and whether the command's effect is
preserved when it is recorded into a secondary command buffer and executed via
`vkCmdExecuteCommands`. The three secondary-command-buffer variants differ in inheritance shape, so a
failure specific to `_secondary_cmd_buffer_unspecified_fb` would point to framebuffer-handle
inheritance rather than the bias command itself. Source-level investigation is needed to distinguish a
representation-info handling defect from a secondary-command-buffer inheritance defect when both are
present in the same case.

#### Color comparison failure

**Possible failure symptoms:** The color comparison fails. The host reports that the color buffer was
not exactly `(0, 0, 1, 1)`.

**Possible implementation causes:** The fragment shader writes a constant color and the color
threshold is zero, so a color failure cannot be caused by the depth-bias logic. A grounded
investigation should look at the fragment shader execution, the color attachment layout transitions,
and the copyback path. This cause is independent of the behavioral axis and would affect all cases
that share the affected pipeline or copyback state.

## Case Pruning

### Requirement-based pruning

- Every case requires `VK_EXT_depth_bias_control`
  [`DepthBiasControlCase::checkSupport()`](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L305-L307).
- Cases that set `depthBiasExact = TRUE` require the `depthBiasExact` feature
  [vktRasterizationDepthBiasControlTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L314-L315).
- Cases that select `LEAST_REPRESENTABLE_VALUE_FORCE_UNORM_EXT` require the
  `leastRepresentableValueForceUnormRepresentation` feature
  [vktRasterizationDepthBiasControlTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L317-L322).
- Cases that select `FLOAT_EXT` require the `floatRepresentation` feature
  [vktRasterizationDepthBiasControlTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L324-L326).
- The selected depth attachment format must support depth-stencil attachment and transfer-source
  usage; otherwise the case is reported as `NotSupportedError`
  [vktRasterizationDepthBiasControlTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L329-L342).

### Design-based pruning

- Representation-info variants combined with `DYNAMIC_1` are skipped because `vkCmdSetDepthBias` has
  no pNext chain and cannot carry `VkDepthBiasRepresentationInfoEXT`
  [vktRasterizationDepthBiasControlTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L832-L837).
- Secondary-command-buffer variants are reduced to a representative subset: they are limited to the
  `CONSTANT` used factor, a non-`DYNAMIC_1` set mechanism, the `_no_clamp` clamp case, and a non-empty
  representation info. Direct (non-secondary) cases cover the rest of the matrix
  [vktRasterizationDepthBiasControlTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L858-L875).

## Key Takeaways

- The set mechanism is the behavioral axis. `static` and `dynamic_set_2` cover representation info;
  `dynamic_set_1` covers only the legacy `no_repr_info` path because `vkCmdSetDepthBias` has no pNext
  chain.
- The host computes the constant factor against the most precise `r` (`r.first`) so the rendered depth
  lands at `sampleDepth + clampedBias` when the implementation uses the most precise representation.
  The threshold absorbs the slack up to `r.second` plus the format depth error.
- `clampedBias = min(targetBias, depthBiasClamp == 0 ? targetBias : depthBiasClamp)` treats a zero
  clamp as "no clamp", not "clamp to zero". A literal clamp-to-zero interpretation would fail every
  `_no_clamp` case with a nonzero target bias.
- The depth and color comparisons are independent. A depth failure points at the bias pipeline; a
  color failure points at the fragment shader or copyback path and is independent of the behavioral
  axis.
- Secondary-command-buffer variants are reduced to a representative subset that still exercises the
  three inheritance shapes (explicit, inherited with framebuffer, inherited without framebuffer) for
  the bias state set in a secondary buffer.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Minimum resolvable difference math | [calcMinResolvableDiff()](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L121-L183) | Mirrors the spec rules for `r` per representation and channel class; drives factor and threshold computation. |
| Depth error threshold | [getDepthErrorThreshold()](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L187-L192) | Adds the format's own depth representation error to the bias slack. |
| Channel class helper | [getChannelClass()](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L110-L116) | Maps the texture format to a channel class, with a fix for `VK_FORMAT_X8_D24_UNORM_PACK32`. |
| Set mechanism enum | [SetMechanism](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L202-L207) | Defines the three values that form the primary behavioral axis. |
| Test parameters | [TestParams](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L227-L263) | Carries the format, repr info, mechanism, target bias, used factor, constant depth, clamp, and secondary-command-buffer flags. |
| Support checks | [checkSupport()](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L305-L343) | Gates on `VK_EXT_depth_bias_control`, `depthBiasExact`, force-UNORM, float representation, and format support. |
| Shader generation | [initPrograms()](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L350-L367) | Emits the trivial vertex/fragment pair; confirms shaders are not part of the tested behavior. |
| Pipeline and bias setup | [iterate()](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L460-L593) | Computes factors, builds the pipeline, and records the bias command for each mechanism. |
| Result verification | [iterate()](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L637-L695) | Computes `expectedDepth`, the depth threshold, and runs `tcu::dsThresholdCompare()` plus `tcu::floatThresholdCompare()`. |
| Matrix registration and pruning | [createDepthBiasControlTests()](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L700-L910) | Builds the six-format tree and applies the representation-info + `DYNAMIC_1` skip and the secondary-command-buffer reduction. |
| Header declaration | [vktRasterizationDepthBiasControlTests.hpp#L35](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.hpp#L35) | Declares `createDepthBiasControlTests`. |
| Mustpass examples | [rasterization.txt#L400-L411](../../../mustpass/main/vk-default/rasterization.txt#L400-L411) | Confirms the registered case names and the six-format hierarchy. |
