# depth_bias

## Overview

Depth bias tests that verify correct application of depth bias values when rendering geometry with different polygon modes and primitive topologies. The tests exercise depth bias with triangle lists and patch lists across fill, line, and point polygon modes.

## Role

Validates that the Vulkan depth bias state (depthBiasConstantFactor, depthBiasClamp, depthBiasSlopeFactor) is correctly applied during rasterization. Covers the three polygon modes (fill, line, point) and two primitive topologies (triangle list, patch list with tessellation), ensuring that depth offset calculations produce the expected results for each combination.

## Source Code

- [vktDrawDepthBiasTests.cpp](../../../modules/vulkan/draw/vktDrawDepthBiasTests.cpp)

## Registration Hierarchy

```text
draw.renderpass.depth_bias
├── depth_bias_triangle_list_fill
├── depth_bias_triangle_list_line
├── depth_bias_triangle_list_point
├── depth_bias_patch_list_tri_fill
├── depth_bias_patch_list_tri_line
└── depth_bias_patch_list_tri_point
```

## Test Families

### depth_bias_triangle_list_fill — Depth bias with triangle list and fill mode

Tests depth bias application when rendering a triangle list with `VK_POLYGON_MODE_FILL`. No additional feature requirements beyond the base Vulkan spec.

Source: [vktDrawDepthBiasTests.cpp#L52](../../../modules/vulkan/draw/vktDrawDepthBiasTests.cpp#L52)

### depth_bias_triangle_list_line — Depth bias with triangle list and line mode

Tests depth bias application when rendering a triangle list with `VK_POLYGON_MODE_LINE`. Requires `fillModeNonSolid` feature.

Source: [vktDrawDepthBiasTests.cpp#L53](../../../modules/vulkan/draw/vktDrawDepthBiasTests.cpp#L53)

### depth_bias_triangle_list_point — Depth bias with triangle list and point mode

Tests depth bias application when rendering a triangle list with `VK_POLYGON_MODE_POINT`. Requires `fillModeNonSolid` feature.

Source: [vktDrawDepthBiasTests.cpp#L54](../../../modules/vulkan/draw/vktDrawDepthBiasTests.cpp#L54)

### depth_bias_patch_list_tri_fill — Depth bias with patch list and fill mode

Tests depth bias application when rendering a patch list (tessellation) with `VK_POLYGON_MODE_FILL`. Requires `tessellationShader` feature.

Source: [vktDrawDepthBiasTests.cpp#L55](../../../modules/vulkan/draw/vktDrawDepthBiasTests.cpp#L55)

### depth_bias_patch_list_tri_line — Depth bias with patch list and line mode

Tests depth bias application when rendering a patch list (tessellation) with `VK_POLYGON_MODE_LINE`. Requires both `tessellationShader` and `fillModeNonSolid` features.

Source: [vktDrawDepthBiasTests.cpp#L56](../../../modules/vulkan/draw/vktDrawDepthBiasTests.cpp#L56)

### depth_bias_patch_list_tri_point — Depth bias with patch list and point mode

Tests depth bias application when rendering a patch list (tessellation) with `VK_POLYGON_MODE_POINT`. Requires both `tessellationShader` and `fillModeNonSolid` features.

Source: [vktDrawDepthBiasTests.cpp#L57](../../../modules/vulkan/draw/vktDrawDepthBiasTests.cpp#L57)

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Primitive topology | triangle_list, patch_list | The input assembly primitive topology |
| Polygon mode | fill, line, point | The rasterization polygon mode |

## Support Requirements

| Requirement | Condition | Details |
|-------------|-----------|---------|
| Vulkan only | Implicit | No Vulkan SC guard in the source, but registered under `#ifndef CTS_USES_VULKANSC` in the parent module ([vktDrawTests.cpp#L103](../../../modules/vulkan/draw/vktDrawTests.cpp#L103)) |
| Renderpass only | `!useDynamicRendering` | Not added to dynamic rendering variants ([vktDrawTests.cpp#L106-L110](../../../modules/vulkan/draw/vktDrawTests.cpp#L106-L110)) |
| fillModeNonSolid | `Features.fillModeNonSolid` | Required for line and point polygon modes (amber requirement) |
| tessellationShader | `Features.tessellationShader` | Required for patch list primitive topology (amber requirement) |

## Verification Methods

| Method | Description |
|--------|-------------|
| Amber comparison | All test cases are amber-based; the amber framework performs rendering and image comparison internally against expected results defined in the amber scripts |

## Notes

- All test cases are amber-based and rely on external `.amber` script files located in the `draw/depth_bias` data directory.
- The test requirements are passed directly to the amber test case constructor as feature requirement strings, which the amber framework uses to check device support before execution.
- The combination of tessellation and non-fill polygon modes requires both `tessellationShader` and `fillModeNonSolid` features simultaneously.
