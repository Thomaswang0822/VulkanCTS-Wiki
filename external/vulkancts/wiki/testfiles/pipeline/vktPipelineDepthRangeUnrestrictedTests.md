# vktPipelineDepthRangeUnrestrictedTests.cpp

## Overview

[`vktPipelineDepthRangeUnrestrictedTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineDepthRangeUnrestrictedTests.cpp#L1) implements the [`depth_range_unrestricted`](../../../modules/vulkan/pipeline/vktPipelineDepthRangeUnrestrictedTests.cpp#L1378) topic group. It verifies VK_EXT_depth_range_unrestricted functionality, testing that depth range values outside [0,1] are correctly handled.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineDepthRangeUnrestrictedTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineDepthRangeUnrestrictedTests.cpp#L1)
- Header: [`vktPipelineDepthRangeUnrestrictedTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineDepthRangeUnrestrictedTests.hpp#L1)

## Registration Path

[`createDepthRangeUnrestrictedTests()`](../../../modules/vulkan/pipeline/vktPipelineDepthRangeUnrestrictedTests.cpp#L1377) returns the `depth_range_unrestricted` group, attached under each variant root by `createChildren()`.

**Variant coverage**: All variants, VK only.

## Test Hierarchy

```text
depth_range_unrestricted
└── {test_case}
```

## Test Families

| Family | Description |
|---|---|
| DepthRangeUnrestrictedTest | Verifies depth range values outside [0,1] produce correct depth buffer values |

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
