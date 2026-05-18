# vktRasterizationDepthBiasControlTests.cpp

## Overview

[`vktRasterizationDepthBiasControlTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L1) implements the non-VulkanSC `depth_bias_control` subgroup for `VK_EXT_depth_bias_control`. The subgroup is registered by [`createDepthBiasControlTests()`](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L700) and builds a multi-level matrix over attachment formats, depth-bias representation info, used factor, constant depth, target bias, static/dynamic setting mechanisms, clamp behavior, and selected secondary-command-buffer modes.

## Role

Implementation file.

## Source Code

- Primary source: [`vktRasterizationDepthBiasControlTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L1)
- Header: [`vktRasterizationDepthBiasControlTests.hpp`](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.hpp#L35)

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

## Test Families

### d16_unorm — D16 depth format

`d16_unorm` is one of six attachment-format groups created from `attachmentFormats` at [`vktRasterizationDepthBiasControlTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L704-L710). Beneath each format, the file registers representation-info groups, slope/constant factor groups, constant-depth groups, target-bias groups, and leaf cases named from set mechanism, clamp case, and selected secondary-command-buffer suffixes at [`vktRasterizationDepthBiasControlTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L812-L889).

### x8_d24_unorm_pack32 — X8 D24 depth format

`x8_d24_unorm_pack32` follows the same registration matrix as `d16_unorm`, using the second entry in `attachmentFormats` at [`vktRasterizationDepthBiasControlTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L704-L707).

### d32_sfloat — D32 floating-point depth format

`d32_sfloat` follows the same representation, used-factor, target-bias, clamp, and command-buffer matrix, using the third entry in `attachmentFormats` at [`vktRasterizationDepthBiasControlTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L704-L707).

### d16_unorm_s8_uint — D16/S8 depth-stencil format

`d16_unorm_s8_uint` follows the same matrix, using the fourth attachment-format entry at [`vktRasterizationDepthBiasControlTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L704-L707).

### d24_unorm_s8_uint — D24/S8 depth-stencil format

`d24_unorm_s8_uint` follows the same matrix, using the fifth attachment-format entry at [`vktRasterizationDepthBiasControlTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L704-L707).

### d32_sfloat_s8_uint — D32/S8 depth-stencil format

`d32_sfloat_s8_uint` follows the same matrix, using the sixth attachment-format entry at [`vktRasterizationDepthBiasControlTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L704-L707).

## Parameter Dimensions

| Dimension | Observed values / source |
|---|---|
| Attachment format | Six formats in [`attachmentFormats`](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L704-L707) |
| Used factor | `slope` and `constant` at [`usedFactorCases[]`](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L709-L716) |
| Representation info | `no_repr_info`, format inexact/exact, force-UNORM inexact/exact, and float inexact/exact at [`reprInfoCases[]`](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L718-L734) |
| Constant depth | Slope placeholder `slope_depth_1_0` and constant-depth values 0.25, 0.3125, near 0.5, 0.625, and 0.125 at [`vktRasterizationDepthBiasControlTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L736-L753) |
| Target bias | 0.0625, 0.125, and 0.25 at [`targetBiasCases[]`](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L755-L763) |
| Set mechanism | `static`, `dynamic_set_1`, and `dynamic_set_2` at [`setMechanismCases[]`](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L765-L773) |
| Clamp case | no clamp, large no-effective clamp, and clamp-to-half at [`clampValueCases[]`](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L775-L789) |
| Secondary command buffer | direct plus three secondary-command-buffer suffixes at [`secondaryCmdBufferCases[]`](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L791-L802), with reduction filters at [`vktRasterizationDepthBiasControlTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L858-L875) |

## Support / Feature Requirements

All cases require `VK_EXT_depth_bias_control` at [`DepthBiasControlCase::checkSupport()`](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L305-L307). Cases using exact representation info require the `depthBiasExact` feature at [`vktRasterizationDepthBiasControlTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L309-L315). The registration logic skips representation-info combinations with `DYNAMIC_1` because representation info cannot be used with `vkCmdSetDepthBias` at [`vktRasterizationDepthBiasControlTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L832-L837).

## Verification Methods

After rendering, the test invalidates the depth and color buffers at [`vktRasterizationDepthBiasControlTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L637-L640). It computes expected depth as vertex sample depth plus clamped target bias at [`vktRasterizationDepthBiasControlTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L641-L647), calculates a depth threshold from the constant-bias range plus format depth threshold at [`vktRasterizationDepthBiasControlTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L649-L657), then uses `tcu::dsThresholdCompare()` for depth and `tcu::floatThresholdCompare()` for exact color at [`vktRasterizationDepthBiasControlTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp#L675-L690).

## Test Principles Observed

- **Format-sensitive depth expectations**: the verification accounts for depth-format precision and minimum resolvable depth-bias intervals.
- **API-path variation**: static and dynamic depth-bias setting paths are both represented, with invalid representation-info / dynamic-set combinations skipped.
- **Command-buffer inheritance coverage**: selected combinations exercise secondary command buffers with and without inherited render pass / framebuffer data.

## Notes / Uncertainties

- The direct child names shown here are inferred from `getFormatSimpleName(format)` applied to the visible `VkFormat` list; validation against mustpass paths is required for the exact displayed spelling.
