# vktPipelineDepthRangeUnrestrictedTests.cpp

## Overview

[`vktPipelineDepthRangeUnrestrictedTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineDepthRangeUnrestrictedTests.cpp#L1) implements the [`depth_range_unrestricted`](../../../modules/vulkan/pipeline/vktPipelineDepthRangeUnrestrictedTests.cpp#L1378) topic group. It verifies VK_EXT_depth_range_unrestricted functionality, testing that depth range values outside [0,1] are correctly handled.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineDepthRangeUnrestrictedTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineDepthRangeUnrestrictedTests.cpp#L1)
- Header: [`vktPipelineDepthRangeUnrestrictedTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineDepthRangeUnrestrictedTests.hpp#L1)

## Registration Hierarchy

```text
pipeline.monolithic.depth_range_unrestricted
├── clear_value
├── viewport
├── depthbounds
└── depthclampingdisabled
```

## Test Families

### clear_value — Depth clear values outside [0,1]

Tests that depth buffer clear values outside the standard [0,1] range are correctly handled when VK_EXT_depth_range_unrestricted is enabled. Parameterized by depth format (D32_SFLOAT, D24_UNORM_S8_UINT, D16_UNORM) and clear value (2.0, -3.0, 6.0, -7.0).

### viewport — Viewport depth range outside [0,1]

Tests that viewport min/max depth values outside [0,1] are correctly handled. Parameterized by depth format, compare operation, clear value, and viewport depth range values. Tests both static and dynamic viewport modes.

### depthbounds — Depth bounds range outside [0,1]

Tests that depth bounds min/max values outside [0,1] are correctly handled when depth bounds testing is enabled. Parameterized by depth format, compare operation, clear value, viewport depth range, and depth bounds values. Tests static viewport, dynamic depth bounds, and combined dynamic viewport+depth bounds modes.

### depthclampingdisabled — Depth clamping disabled with unrestricted range

Tests unrestricted depth range behavior when depth clamping is disabled. Parameterized by depth format, compare operation, clear value, viewport depth range, and W coordinate (wc) values. Uses static viewport/depth bounds mode only.

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| Depth range min | Float | Values outside [0,1] |
| Depth range max | Float | Values outside [0,1] |
| Depth format | Enum | D16_UNORM, D24_UNORM_S8_UINT, D32_SFLOAT, etc. |
| PipelineConstructionType | Parameter | All variant types |

## Support/Feature Requirements

| Requirement | Context |
|---|---|
| `VK_EXT_depth_range_unrestricted` | Primary extension for all tests |

## Verification Methods

- **Depth buffer comparison**: Render with unrestricted depth range, read back depth buffer, compare against expected values
- **Clamping verification**: Verify that depth values are correctly clamped or unclamped based on the extension

## Notes

- VK only (guarded by `CTS_USES_VULKANSC` exclusion)
