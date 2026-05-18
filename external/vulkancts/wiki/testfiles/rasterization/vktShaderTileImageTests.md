# vktShaderTileImageTests.cpp

## Overview

[`vktShaderTileImageTests.cpp`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L1) implements the non-VulkanSC `shader_tile_image` subgroup for `VK_EXT_shader_tile_image`. The group is registered by [`createShaderTileImageTests()`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L2193-L2200), which delegates case generation to [`createShaderTileImageTestVariations()`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L1968-L2189).

## Role

Implementation file.

## Source Code

- Primary source: [`vktShaderTileImageTests.cpp`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L1)
- Header: [`vktShaderTileImageTests.hpp`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.hpp#L35)

## Registration Hierarchy

```text
rasterization.shader_tile_image
├── coherent
└── non_coherent
```

## Test Families

### coherent — Coherent tile-image reads

The `coherent` direct child is the first value from `coherentParams` at [`vktShaderTileImageTests.cpp`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L1988-L1989). Beneath it, the file registers test-type groups `color`, `mrt`, `mrt_dynamic_index`, `msaa_sample_mask`, `helper_class_color`, `helper_class_depth`, `helper_class_stencil`, `depth`, and `stencil` at [`testTypeParams`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L1990-L2000), then sample-count, single/multiple-draw, single/multiple-patch, and format leaves through [`createShaderTileImageTestVariations()`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L2062-L2188).

### non_coherent — Non-coherent tile-image reads

The `non_coherent` direct child is the second value from `coherentParams` at [`vktShaderTileImageTests.cpp`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L1988-L1989). It uses the same test-type, sample-count, draw-count, patch-count, and format dimensions as `coherent`, except multiple-patch cases are skipped when `coherentParam.value` is false at [`vktShaderTileImageTests.cpp`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L2101-L2106).

## Parameter Dimensions

| Dimension | Observed values / source |
|---|---|
| Coherency | `coherent` and `non_coherent` at [`coherentParams`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L1988-L1989) |
| Test type | Color, MRT, dynamic-index MRT, MSAA sample mask, helper-class color/depth/stencil, depth, and stencil at [`testTypeParams`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L1990-L2000) |
| Sample count | 1, 2, 4, 8, 16, and 32 at [`sampleCountParams`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L2002-L2006), with MSAA sample-mask skipping sample 1 and helper-class tests restricted to sample 1 at [`vktShaderTileImageTests.cpp`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L2073-L2084) |
| Draw count | `single_draw` and `multi_draws` at [`multiDrawsParams`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L2008), with helper-class multi-draw skipped at [`vktShaderTileImageTests.cpp`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L2089-L2095) |
| Patch count | `single_patch` and `multi_patches` at [`multiPatchParams`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L2010), with non-coherent and helper-class multiple-patch skips at [`vktShaderTileImageTests.cpp`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L2101-L2111) |
| Formats | Color and depth/stencil formats listed in [`formats`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L2012-L2056), filtered by depth/stencil/color compatibility at [`vktShaderTileImageTests.cpp`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L2117-L2177) |

## Support / Feature Requirements

Every case requires `VK_KHR_dynamic_rendering` and `VK_EXT_shader_tile_image` at [`ShaderTileImageTestCase::checkSupport()`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L951-L961). The support check requires color read access for all cases at [`vktShaderTileImageTests.cpp`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L974-L977), depth read access for depth/helper-depth cases at [`vktShaderTileImageTests.cpp`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L978-L986), and stencil read access for stencil/helper-stencil cases at [`vktShaderTileImageTests.cpp`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L987-L993). It also rejects unsupported multisample pixel-rate sample reads for `msaa_sample_mask` at [`vktShaderTileImageTests.cpp`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L1017-L1026) and unsupported helper-invocation reads for helper-class tests at [`vktShaderTileImageTests.cpp`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L1029-L1034).

## Verification Methods

The inspected portions show shader generation for vertex, fragment, and compute programs at [`ShaderTileImageTestCase::initPrograms()`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L941-L943) and the large parameterized registration matrix at [`createShaderTileImageTestVariations()`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L1968-L2189). The detailed result-comparison logic is earlier in the same source file and was not exhaustively inspected for this page; therefore this page limits verification claims to the visible support checks, shader setup, and registered parameter matrix.

## Test Principles Observed

- **Tile-image feature slicing**: color, depth, stencil, MSAA sample-mask, MRT, dynamic-index MRT, and helper-class read cases are registered as separate test-type groups.
- **Format filtering**: color formats and depth/stencil formats are selected according to the active test type and texture channel characteristics.
- **Coherency contrast**: coherent and non-coherent modes are direct children, with non-coherent multi-patch cases skipped because the code comments that guarantee cannot be made.

## Notes / Uncertainties

- Verification details beyond shader setup and support checks were not fully inspected in this run; claims here intentionally avoid asserting a specific comparison algorithm for final images or buffers.
