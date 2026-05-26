# rasterization

## Overview

The [`rasterization`](../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L10455) category covers Vulkan rasterization behavior observed in the inspected source files: primitive rasterization, line and point rules, fill rules, culling, rasterizer discard, interpolation and flat shading, multisampling, conservative rasterization, depth bias, provoking vertex behavior, fragment shader side effects, rasterization-order attachment access, shader tile-image reads, and selected maintenance5 line behavior. The root registration file is [`vktRasterizationTests.cpp`](../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L1), with sibling registered implementation groups included from the root include section at [`vktRasterizationTests.cpp`](../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L29-L62).


## Registration Entry Point

The category entry point is [`createTests()`](../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L10455-L10458), which builds the root group through `createTestGroup()` and [`createRasterizationTests()`](../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L9019). The direct children registered under `rasterization` are:

```text
rasterization
├── primitives
├── primitive_size
├── polygon_as_large_points (non-VulkanSC only)
├── fill_rules
├── culling
├── discard
├── conservative
├── interpolation
├── flatshading
├── primitives_multisample_2_bit
├── fill_rules_multisample_2_bit
├── interpolation_multisample_2_bit
├── primitives_multisample_4_bit
├── fill_rules_multisample_4_bit
├── interpolation_multisample_4_bit
├── primitives_multisample_8_bit
├── fill_rules_multisample_8_bit
├── interpolation_multisample_8_bit
├── primitives_multisample_16_bit
├── fill_rules_multisample_16_bit
├── interpolation_multisample_16_bit
├── primitives_multisample_32_bit
├── fill_rules_multisample_32_bit
├── interpolation_multisample_32_bit
├── primitives_multisample_64_bit
├── fill_rules_multisample_64_bit
├── interpolation_multisample_64_bit
├── provoking_vertex (non-VulkanSC only)
├── line_continuity (non-VulkanSC only)
├── depth_bias (non-VulkanSC only)
├── depth_bias_control (non-VulkanSC only)
├── frag_side_effects
├── rasterization_order_attachment_access (non-VulkanSC only)
├── shader_tile_image (non-VulkanSC only)
└── maintenance5 (non-VulkanSC only)
```

Source: [`createRasterizationTests()`](../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L9019-L10451).

## File Inventory

| File | Role | Registered group(s) / notes |
|---|---|---|
| [`vktRasterizationTests.cpp`](../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L1) | Root registration + implementation | Root `rasterization` dispatcher and many built-in rasterization families |
| [`vktRasterizationFragShaderSideEffectsTests.cpp`](../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.cpp#L684) | Implementation | `frag_side_effects` |
| [`vktRasterizationProvokingVertexTests.cpp`](../../modules/vulkan/rasterization/vktRasterizationProvokingVertexTests.cpp#L1156) | Implementation | `provoking_vertex` (non-VulkanSC parent registration) |
| [`vktRasterizationDepthBiasControlTests.cpp`](../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L700) | Implementation | `depth_bias_control` (non-VulkanSC parent registration) |
| [`vktRasterizationOrderAttachmentAccessTests.cpp`](../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L1831) | Implementation | `rasterization_order_attachment_access` (non-VulkanSC parent registration) |
| [`vktShaderTileImageTests.cpp`](../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L2193) | Implementation | `shader_tile_image` (non-VulkanSC parent registration) |

## Level-3 Documents

| Source file | Wiki document |
|---|---|
| [`vktRasterizationTests.cpp`](../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L1) | [`vktRasterizationTests.md`](../testfiles/rasterization/vktRasterizationTests.md) |
| [`vktRasterizationFragShaderSideEffectsTests.cpp`](../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.cpp#L1) | [`vktRasterizationFragShaderSideEffectsTests.md`](../testfiles/rasterization/vktRasterizationFragShaderSideEffectsTests.md) |
| [`vktRasterizationProvokingVertexTests.cpp`](../../modules/vulkan/rasterization/vktRasterizationProvokingVertexTests.cpp#L1) | [`vktRasterizationProvokingVertexTests.md`](../testfiles/rasterization/vktRasterizationProvokingVertexTests.md) |
| [`vktRasterizationDepthBiasControlTests.cpp`](../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L1) | [`vktRasterizationDepthBiasControlTests.md`](../testfiles/rasterization/vktRasterizationDepthBiasControlTests.md) |
| [`vktRasterizationOrderAttachmentAccessTests.cpp`](../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L1) | [`vktRasterizationOrderAttachmentAccessTests.md`](../testfiles/rasterization/vktRasterizationOrderAttachmentAccessTests.md) |
| [`vktShaderTileImageTests.cpp`](../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L1) | [`vktShaderTileImageTests.md`](../testfiles/rasterization/vktShaderTileImageTests.md) |

## Subgroup Structure and Major Themes

### Core primitive, line, point, and fill behavior

The root file registers `primitives`, `primitive_size`, `fill_rules`, `culling`, `discard`, `interpolation`, `flatshading`, and multisample repeats directly in [`createRasterizationTests()`](../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L9035-L10292). These families vary primitive topologies, line stipple modes, line rasterization modes, wide-line and large-point support, fill-rule case types, cull modes, rasterizer-discard query usage, interpolation flags, and sample counts.

### Conservative rasterization

The `conservative` subtree is generated in [`vktRasterizationTests.cpp`](../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L9650-L9886). It separates overestimate and underestimate modes, sample counts 1 through 64, primitive classes triangles/lines/points, normal versus degenerate primitives, extra overestimation sizes, line widths, and point sizes.

### Extension-backed registered groups

Four separately meaningful registered files are linked from the root registration:

- `depth_bias_control` requires `VK_EXT_depth_bias_control` and varies attachment format, representation info, set mechanism, clamp value, and selected secondary-command-buffer modes at [`vktRasterizationDepthBiasControlTests.cpp`](../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L700-L910).
- `provoking_vertex` varies draw versus transform-feedback behavior, provoking mode, and primitive topology at [`vktRasterizationProvokingVertexTests.cpp`](../../modules/vulkan/rasterization/vktRasterizationProvokingVertexTests.cpp#L1069-L1159).
- `rasterization_order_attachment_access` separates float/integer color formats, depth, and stencil attachment paths, with sample-count and overlap-pattern sweeps at [`vktRasterizationOrderAttachmentAccessTests.cpp`](../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L1703-L1851).
- `shader_tile_image` separates coherent and non-coherent tile-image read paths and expands test type, sample count, draw count, patch count, and format dimensions at [`vktShaderTileImageTests.cpp`](../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L1968-L2200).

### Fragment shader side effects

The `frag_side_effects` registered file creates `color_at_beginning` and `color_at_end` branches and cases for kill, demote, terminate invocation, sample mask, stencil/depth failure, alpha coverage, and depth bounds at [`vktRasterizationFragShaderSideEffectsTests.cpp`](../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.cpp#L684-L776).

### Amber-backed non-VulkanSC cases

The root file uses Amber tests for `line_continuity` at [`vktRasterizationTests.cpp`](../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L10301-L10332) and `depth_bias` at [`vktRasterizationTests.cpp`](../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L10336-L10405). These are meaningful registered groups but not separate source files, so they are documented inside [`vktRasterizationTests.md`](../testfiles/rasterization/vktRasterizationTests.md).

## Recurring Parameter Dimensions

| Dimension | Observed examples |
|---|---|
| Primitive topology | Triangle, line, point, adjacency, and fan variants in root primitive registration at [`vktRasterizationTests.cpp`](../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L9086-L9169) and provoking-vertex topology table at [`vktRasterizationProvokingVertexTests.cpp`](../../modules/vulkan/rasterization/vktRasterizationProvokingVertexTests.cpp#L1095-L1108) |
| Line behavior | Stipple modes from [`LineStipple`](../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L126-L134), strictness from [`PrimitiveStrictness`](../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L146-L153), and line rasterization modes in primitive registration at [`vktRasterizationTests.cpp`](../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L9202-L9372) |
| Sample count | Multisample root groups use 2 through 64 samples at [`vktRasterizationTests.cpp`](../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L10096-L10292); conservative and attachment-order tests also include 1 sample at [`vktRasterizationTests.cpp`](../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L9683-L9685) and [`vktRasterizationOrderAttachmentAccessTests.cpp`](../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L1759-L1763) |
| Formats | Depth-bias-control formats at [`vktRasterizationDepthBiasControlTests.cpp`](../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L704-L707), shader-tile-image color/depth/stencil formats at [`vktShaderTileImageTests.cpp`](../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L2012-L2056), and Amber depth-bias formats at [`vktRasterizationTests.cpp`](../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L10342-L10373) |
| Extension modes | Conservative over/underestimate at [`vktRasterizationTests.cpp`](../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L9720-L9727), provoking-vertex modes at [`vktRasterizationProvokingVertexTests.cpp`](../../modules/vulkan/rasterization/vktRasterizationProvokingVertexTests.cpp#L1073-L1093), and shader-tile-image coherent modes at [`vktShaderTileImageTests.cpp`](../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L1988-L1989) |

## Recurring Support Requirements

Observed gates include large points, wide lines, tessellation shader, geometry shader, shader tessellation/geometry point size, pipeline statistics query, `VK_EXT_conservative_rasterization`, `VK_KHR_maintenance5`, `VK_EXT_depth_bias_control`, `VK_EXT_provoking_vertex`, `VK_EXT_transform_feedback`, `VK_ARM_rasterization_order_attachment_access` or `VK_EXT_rasterization_order_attachment_access`, `VK_KHR_dynamic_rendering`, and `VK_EXT_shader_tile_image`. Representative checks are visible in [`vktRasterizationTests.cpp`](../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L2512-L2516), [`vktRasterizationTests.cpp`](../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L3446-L3450), [`vktRasterizationDepthBiasControlTests.cpp`](../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L305-L315), [`vktRasterizationProvokingVertexTests.cpp`](../../modules/vulkan/rasterization/vktRasterizationProvokingVertexTests.cpp#L202-L232), [`vktRasterizationOrderAttachmentAccessTests.cpp`](../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L832-L841), and [`vktShaderTileImageTests.cpp`](../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L951-L1034).

## Recurring Verification Methods

Observed verification approaches include:

- reference rasterization through [`verifyTriangleGroupRasterization()`](../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L1503-L1520), [`verifyLineGroupRasterization()`](../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L1907-L1954), and [`verifyPointGroupRasterization()`](../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L2408-L2427)
- interpolation-specific checks through [`verifyTriangleGroupInterpolation()`](../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L7266-L7292) and triangulated-line interpolation helpers at [`vktRasterizationTests.cpp`](../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L7573-L7627)
- exact or thresholded image / buffer comparisons through [`tcu::floatThresholdCompare()`](../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L8272-L8274), [`tcu::dsThresholdCompare()`](../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L675-L678), and SSBO/color attachment inspection in [`vktRasterizationFragShaderSideEffectsTests.cpp`](../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.cpp#L622-L676)
- transform-feedback buffer verification and exact framebuffer comparison in [`vktRasterizationProvokingVertexTests.cpp`](../../modules/vulkan/rasterization/vktRasterizationProvokingVertexTests.cpp#L951-L1002)

## Notes / Uncertainties

- This category page intentionally creates Level-3 pages only for registered source files or separately meaningful registered group files. Amber-only `line_continuity` and `depth_bias` are documented in the root-file page rather than as separate pages.
- Verification details for `rasterization_order_attachment_access` and `shader_tile_image` were not exhaustively inspected beyond visible support, registration, shader setup, and case-construction code; the Level-3 pages avoid more specific verification claims for those files.
