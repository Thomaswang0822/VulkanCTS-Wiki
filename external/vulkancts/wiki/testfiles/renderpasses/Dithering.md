## Overview

**Core question:** When `VK_EXT_legacy_dithering` is enabled, does the implementation modify color output by at most one ULP (or four ULP for additive blending), and does it leave depth and stencil untouched?

- [vktRenderPassDitheringTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp) implements the `dithering` test family under the `renderpasses` test category, covering `VK_EXT_legacy_dithering`.
- The entry point [`createRenderPassDitheringTests`](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L1356-L1365) attaches the family under every rendering root (`renderpass1`, `renderpass2`, and each `dynamic_rendering.*` command-buffer variant).
- The core test idea is a side-by-side comparison: the same draw is rendered twice with identical inputs, once without dithering and once with dithering enabled. The dithered color output must stay within a tight ULP threshold of the non-dithered reference, while depth and stencil must match exactly.
- Three behavioral groups exercise this property under different fixed-function conditions: plain color output, depth/stencil interaction, and blending. A revision dimension (`v1`, `v2`) distinguishes the two extension spec versions, since revision 2 added the pipeline create flag used with dynamic rendering.

## Background Knowledge

- **`VK_EXT_legacy_dithering`.** This extension exposes a hardware feature that some vendors use to implement OpenGL dithering, so that OpenGL-over-Vulkan translation layers can reach the same hardware path. It lets the implementation modify the color output value of a subpass by at most one ULP, and the modification may only depend on the framebuffer coordinates and the color value itself ([interfaces-legacy-dithering](../../../../vulkan-docs/src/chapters/interfaces.adoc#interfaces-legacy-dithering)).
- **Dithering enable points.** Dithering is enabled differently depending on the rendering model. For render-pass-based rendering, the `VK_SUBPASS_DESCRIPTION_ENABLE_LEGACY_DITHERING_BIT_EXT` flag is set on the subpass description. For dynamic rendering with revision 2, the `VK_RENDERING_ENABLE_LEGACY_DITHERING_BIT_EXT` flag is set on `VkRenderingInfo` and the pipeline must be created with `VK_PIPELINE_CREATE_2_ENABLE_LEGACY_DITHERING_BIT_EXT` ([renderpass.adoc](../../../../vulkan-docs/src/chapters/renderpass.adoc), [pipelines.adoc](../../../../vulkan-docs/src/chapters/pipelines.adoc)).
- **ULP comparison.** One ULP (unit in the last place) is a single-bit difference in the representation of a color value. Because the dithering contract allows at most a one-ULP modification, the test compares the dithered and non-dithered images with an integer threshold of one bit per channel using `tcu::intThresholdCompare`.

## Registration Hierarchy

```text
renderpasses.renderpass1.dithering
└── v1
```

The tree shows the `renderpass1` representative scope. The same `dithering.v1` subtree is registered under `renderpasses.renderpass2.dithering` and under every `renderpasses.dynamic_rendering.*.dithering` path. Under dynamic rendering only, an additional `v2` child is added by [`createDitheringRevision2GroupTests`](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L1350-L1354). Both revisions build the same three behavioral groups (`base`, `depth_stencil`, `blend`) through the shared [`createChildren`](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L1152-L1334) function, differing only in the `revision2` parameter that selects the pipeline create flag path.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Color format | `r8g8b8a8_unorm`, `r5g6b5_unorm_pack16`, `r4g4b4a4_unorm_pack16`, `r5g5b5a1_unorm_pack16` | Selects low-precision UNORM and packed formats where dithering is observable. One ULP in these formats is a larger visible step than in high-precision formats. | [testFormats](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L1160-L1161) |
| Format combinations | singles, pairs, triples | Exercises one, two, or three simultaneous color attachments, each independently dithered. Names use `_and_` separators. | [base group loops](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L1223-L1253) |
| Render area | full image, edge-snapped, corner-snapped, random odd-offset | Changes the viewport position and size to test dithering at different framebuffer coordinate offsets, since the dither pattern depends on coordinates. | [render area setup](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L1177-L1221) |
| Stencil clear value | `0x80`, `0x82`, `0x81` | Three stencil values around the pipeline reference `0x81`, exercising stencil compare equal at below, above, and exactly the reference. | [stencilValues](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L1267) |
| Depth clear value | one ULP less, one ULP more, base `0.125f` | Three depth clear values within one ULP of the rendered depth, exercising depth compare at less, greater, and equal. | [depthValues](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L1269-L1272) |
| Depth compare op | `LESS`, `GREATER` | Two compare ops that interact with the near-equal depth values to test whether dithering corrupts depth results. | [compareOps](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L1274) |
| Blend mode | `srcAlpha`, `additive` | Source-alpha blending and additive blending, both with `VK_BLEND_OP_ADD`. Additive blending uses a four-ULP threshold because per-draw dithering can accumulate. | [blend group setup](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L1310-L1333) |
| Revision | `v1`, `v2` | Selects extension spec version 1 (subpass flag only) or spec version 2 (adds pipeline create flag for dynamic rendering). `v2` exists only under dynamic rendering and requires `VK_KHR_maintenance5`. | [revision gate](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L1361-L1362), [checkSupport](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L301-L312) |

## Behavior Parameters

The primary behavioral axis is the subgroup under each revision: `base`, `depth_stencil`, and `blend`. Each subgroup tests a distinct interaction surface of the dithering feature. The revision dimension (`v1` versus `v2`) is a secondary axis that changes only the enable mechanism, not the tested property.

### base: plain color dithering

This subgroup verifies the fundamental dithering contract: when dithering is enabled, the color output stays within one ULP of the non-dithered output. Each test case renders a colored quad into one, two, or three color attachments of the selected format combination, using multiple render areas that cover full-image, edge-snapped, corner-snapped, and random-offset viewports ([base group creation](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L1180-L1256)). The render area variation matters because the dithering modification may depend on framebuffer coordinates.

### depth_stencil: dithering with depth and stencil

This subgroup verifies that dithering affects color output but does not disturb depth or stencil values. Each case attaches a `VK_FORMAT_D24_UNORM_S8_UINT` depth/stencil image alongside one color attachment, clears it to a value near the rendered depth and stencil reference, and enables both depth testing (with `VK_COMPARE_OP_LESS` or `VK_COMPARE_OP_GREATER`) and stencil testing (with `VK_COMPARE_OP_EQUAL`) ([depth/stencil group creation](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L1262-L1306)). The depth clear values are chosen within one ULP of the rendered geometry depth so that depth compare results are sensitive to any spurious modification. The stencil clear values bracket the pipeline reference `0x81`.

### blend: dithering with blending

This subgroup verifies that dithering cooperates with framebuffer blending. Each case enables blending and draws a quad with an override color, using either source-alpha blending (`VK_BLEND_FACTOR_SRC_ALPHA` / `VK_BLEND_FACTOR_ONE_MINUS_SRC_ALPHA`) or additive blending (`VK_BLEND_FACTOR_ONE` / `VK_BLEND_FACTOR_ONE`) ([blend group creation](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L1308-L1333)). Additive blending draws the quad four times into a green-cleared target, which lets per-draw dithering accumulate. The comparison threshold is widened to four ULP for additive cases to accommodate this accumulation; all other cases keep the strict one-ULP threshold.

### v1 and v2: revision dimension

`v1` covers extension spec version 1, where dithering is enabled through the subpass description flag for render-pass-based rendering, or through the rendering info flag for dynamic rendering without the pipeline create flag. `v2` covers spec version 2, which added the `VK_PIPELINE_CREATE_2_ENABLE_LEGACY_DITHERING_BIT_EXT` pipeline create flag for dynamic rendering ([spec version history](../../../../vulkan-docs/src/appendices/VK_EXT_legacy_dithering.adoc)). The `v2` group is registered only under dynamic rendering and requires `VK_KHR_maintenance5` plus extension spec version at least 2. Both revisions generate the same three subgroups with the same parameter matrices.

## Shader Analysis

The shaders are trivial passthrough and are not part of the tested behavior. The vertex shader ([source](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L252-L261)) copies `position` to `gl_Position` and passes `color` to the fragment stage. The fragment shader ([source](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L263-L274)) writes the interpolated vertex color to up to three color attachments. The dithering modification happens in fixed-function hardware after the fragment shader, so a representative walkthrough would not add information beyond the source listing.

## Runtime Execution and Result Checking

Each test case instance builds two complete sets of draw resources: one without dithering (`m_drawResources[0]`) and one with dithering (`m_drawResources[1]`) ([constructor](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L356-L365)). Both sets use identical image formats, clear values, vertex data, and pipeline state. The only difference is whether the dithering enable flag is set on the subpass description, the rendering info, or the pipeline create flags.

The per-viewport iteration ([iterate](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L371-L483)) performs the following for each render area:

- Clears the color attachment images to black (or green for blending cases) and transitions them to `VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL`. When depth/stencil is present, clears it to the configured depth and stencil values ([clear setup](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L497-L525)).
- Renders the quad into both resource sets, once with dithering disabled and once with dithering enabled. For additive blending, the quad is drawn four times per render ([draw count](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L538)).
- Reads back each color attachment from both resource sets using `pipeline::readColorAttachment` ([color readback](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L392-L410)).
- Compares the non-dithered and dithered color images with `tcu::intThresholdCompare` using a per-channel threshold of one ULP, or four ULP for additive blending ([threshold selection](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L416-L421)).
- When depth/stencil is present, reads back the depth aspect with `pipeline::readDepthAttachment` and the stencil aspect with `pipeline::readStencilAttachment` from both resource sets, and compares them with `tcu::dsThresholdCompare` at a zero threshold ([depth check](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L430-L453), [stencil check](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L455-L478)).

The test passes only if every render area, every color attachment, and every depth/stencil aspect passes its threshold comparison. Any single mismatch fails the case.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `base` | Dithering modifies color output by more than one ULP, or is not applied when the enable flag is set |
| `depth_stencil` | Dithering corrupts depth or stencil values, or color dithering exceeds one ULP when depth/stencil testing is active |
| `blend` | Dithering exceeds the allowed threshold under blending, or the blending equation interacts incorrectly with dithered values |
| `v2` (dynamic rendering only) | The pipeline create flag path for dithering is not handled, or the rendering info flag is ignored when the pipeline flag is expected |
| Shared infrastructure | The non-dithered reference render itself is wrong, or the readback and comparison helpers produce incorrect results |

### Cause Analysis

#### Excessive dithering modification

**Possible failure symptoms:** The color comparison between the dithered and non-dithered images fails the one-ULP (or four-ULP for additive blending) integer threshold. The test log from `tcu::intThresholdCompare` shows pixel positions where the difference exceeds the threshold.

**Possible implementation causes:** The implementation applies a dithering algorithm whose per-pixel modification exceeds one ULP, or applies dithering in a way that depends on more than framebuffer coordinates and color value (for example, depending on depth, which would vary across render areas). For additive blending, the driver may apply dithering per draw rather than once for the final framebuffer value, causing the four accumulated draws to exceed even the relaxed four-ULP threshold.

#### Depth or stencil corruption

**Possible failure symptoms:** The depth or stencil comparison between the dithered and non-dithered images fails the zero threshold. The `tcu::dsThresholdCompare` log shows pixel positions where depth or stencil differs.

**Possible implementation causes:** The dithering hardware path writes to or interferes with the depth/stencil buffer. Because the depth clear values are chosen within one ULP of the rendered geometry depth, even a small spurious depth modification can flip a `LESS` or `GREATER` compare result, making this failure mode observable.

#### Enable flag not honored

**Possible failure symptoms:** The dithered and non-dithered images are pixel-identical, and the one-ULP comparison passes trivially. This is not a hard failure (the threshold comparison passes), but it indicates that dithering was never applied. The test cannot distinguish this from a correct sub-ULP dither, so a driver that silently ignores the flag would pass without exercising the feature.

**Possible implementation causes:** The implementation does not read the `VK_SUBPASS_DESCRIPTION_ENABLE_LEGACY_DITHERING_BIT_EXT` flag, the `VK_RENDERING_ENABLE_LEGACY_DITHERING_BIT_EXT` flag, or the `VK_PIPELINE_CREATE_2_ENABLE_LEGACY_DITHERING_BIT_EXT` pipeline create flag, so the dithering hardware path is never activated. Source-level investigation of the driver flag handling would be needed to confirm this.

#### Revision 2 pipeline flag path

**Possible failure symptoms:** A `v2` case under dynamic rendering fails validation (VUID error) or produces incorrect results, while the corresponding `v1` case passes.

**Possible implementation causes:** The `VK_PIPELINE_CREATE_2_ENABLE_LEGACY_DITHERING_BIT_EXT` pipeline create flag (added in spec revision 2) is rejected or ignored when used with dynamic rendering. The VUID `VUID-vkCmdDraw-None-09642` requires the pipeline to be created with this flag when `VK_RENDERING_ENABLE_LEGACY_DITHERING_BIT_EXT` is set, so a driver that does not recognize it may emit a validation error or fail to enable dithering.

## Case Pruning

### Requirement-based pruning

- `VK_EXT_legacy_dithering` is required for every case. Cases are skipped (`NotSupportedError`) if the extension is not supported ([checkSupport](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L287)).
- Extension spec version gating: `v1` cases require spec version at most 1, and `v2` cases require spec version at least 2. A device advertising spec version 2 skips all `v1` cases, and a device at spec version 1 skips all `v2` cases ([spec version check](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L301-L312)).
- `v2` cases additionally require `VK_KHR_maintenance5` ([maintenance5 gate](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L303)).
- `renderpass2` cases require `VK_KHR_create_renderpass2`; dynamic rendering cases require `VK_KHR_dynamic_rendering` ([extension checks](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L280-L285)).
- Each color format must pass `getPhysicalDeviceImageFormatProperties` for color attachment and transfer usage. Each depth/stencil format must pass for depth/stencil attachment usage. Unsupported formats are skipped ([format support checks](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L314-L348)).

### Design-based pruning

- The blend group uses only single-format cases (no multi-attachment combinations), because the blending behavior under test is per-attachment and multi-attachment coverage would add no new behavioral information ([blend loop](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L1313-L1329)).
- The depth/stencil group uses only `VK_FORMAT_D24_UNORM_S8_UINT` and single color attachments, because the test targets the depth/stencil interaction rather than format breadth ([depth/stencil setup](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L1277)).
- The `v2` revision is registered only under dynamic rendering, because the pipeline create flag it tests is meaningful only in the dynamic rendering path ([v2 gate](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L1361-L1362)).

## Key Takeaways

- The test checks the `VK_EXT_legacy_dithering` contract by comparing identical renders with and without dithering, not by comparing against a software reference image. The non-dithered render is the reference.
- The allowed color modification is one ULP for most cases and four ULP for additive blending, because per-draw dithering can accumulate across the four additive draws.
- Depth and stencil must be completely unaffected by dithering, verified at a zero threshold. The near-equal depth clear values make this check sensitive to even small corruption.
- The revision dimension (`v1`, `v2`) tests the two extension spec versions. Revision 2 added the pipeline create flag for dynamic rendering and requires `VK_KHR_maintenance5`.
- A driver that silently ignores the dithering enable flag would pass the threshold comparison without exercising the feature, since identical images trivially satisfy the one-ULP bound.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `createRenderPassDitheringTests` | [vktRenderPassDitheringTests.cpp#L1356-L1365](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L1356-L1365) | Category entry point that creates the `dithering` group and attaches `v1` (always) and `v2` (dynamic rendering only). |
| `createChildren` | [vktRenderPassDitheringTests.cpp#L1152-L1334](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L1152-L1334) | Shared builder that creates the `base`, `depth_stencil`, and `blend` subgroups for both revisions. |
| `DitheringTest::checkSupport` | [vktRenderPassDitheringTests.cpp#L277-L349](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L277-L349) | Extension, spec version, and format support gating. |
| `DitheringTest::initPrograms` | [vktRenderPassDitheringTests.cpp#L250-L275](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L250-L275) | Trivial vertex and fragment shader sources. |
| `DitheringTestInstance::iterate` | [vktRenderPassDitheringTests.cpp#L371-L483](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L371-L483) | Main test loop: dual render, color readback, ULP threshold compare, depth/stencil zero-threshold compare. |
| `DitheringTestInstance::render` | [vktRenderPassDitheringTests.cpp#L485-L661](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L485-L661) | Per-viewport render path handling render-pass, render-pass-2, and dynamic rendering begin/end, including the `VK_RENDERING_ENABLE_LEGACY_DITHERING_BIT_EXT` flag. |
| `createRenderPassFramebuffer` | [vktRenderPassDitheringTests.cpp#L1030-L1148](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L1030-L1148) | Render pass and framebuffer creation with the `VK_SUBPASS_DESCRIPTION_ENABLE_LEGACY_DITHERING_BIT_EXT` subpass flag. |
| Pipeline creation | [vktRenderPassDitheringTests.cpp#L857-L1028](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L857-L1028) | Graphics pipeline creation including the `VK_PIPELINE_CREATE_2_ENABLE_LEGACY_DITHERING_BIT_EXT` flag for revision 2 dynamic rendering. |
| Legacy Dithering spec | [interfaces-legacy-dithering](../../../../vulkan-docs/src/chapters/interfaces.adoc#interfaces-legacy-dithering) | Specification of the one-ULP dithering contract. |
| Extension appendix | [VK_EXT_legacy_dithering.adoc](../../../../vulkan-docs/src/appendices/VK_EXT_legacy_dithering.adoc) | Extension description and version history. |
