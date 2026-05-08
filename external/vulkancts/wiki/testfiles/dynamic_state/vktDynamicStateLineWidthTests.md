# vktDynamicStateLineWidthTests.cpp

## Overview

[`vktDynamicStateLineWidthTests.cpp`](../../../modules/vulkan/dynamic_state/vktDynamicStateLineWidthTests.cpp#L1) implements the [`line_width`](../../../modules/vulkan/dynamic_state/vktDynamicStateLineWidthTests.cpp#L478) subgroup of the dynamic_state category. It tests dynamic line width state via `vkCmdSetLineWidth`, verifying that different line widths are correctly applied when drawing lines with both static and dynamic pipelines in a two-subpass render pass.

## Role

Implementation file.

## Source Code

- Primary source: [`vktDynamicStateLineWidthTests.cpp`](../../../modules/vulkan/dynamic_state/vktDynamicStateLineWidthTests.cpp#L1)
- Shared base: [`DynamicStateBaseClass`](../../../modules/vulkan/dynamic_state/vktDynamicStateBaseClass.hpp#L43)

## Registration Path

This file contributes the [`DynamicStateLWTests`](../../../modules/vulkan/dynamic_state/vktDynamicStateLineWidthTests.cpp#L477) group (named `"line_width"`), which is attached under each pipeline construction type subgroup by [`createChildren()`](../../../modules/vulkan/dynamic_state/vktDynamicStateTests.cpp#L57).

## Test Hierarchy

```text
line_width
├── dyna_static
│   ├── strip2_list1
│   ├── strip4_list3
│   ├── list6_strip5
│   └── strip14_strip13
└── static_dyna
    ├── list1_strip2
    ├── list3_strip4
    ├── strip5_list6
    └── strip15_strip16
```

Source: [`DynamicStateLWTests::init()`](../../../modules/vulkan/dynamic_state/vktDynamicStateLineWidthTests.cpp#L508).

## Test Families

### 1. Dynamic-first (dyna_static)

The [`dyna_static`](../../../modules/vulkan/dynamic_state/vktDynamicStateLineWidthTests.cpp#L523) subgroup contains tests where the dynamic pipeline draws first (subpass 0) and the static pipeline draws second (subpass 1). Each test uses a different combination of line topology and width values.

### 2. Static-first (static_dyna)

The [`static_dyna`](../../../modules/vulkan/dynamic_state/vktDynamicStateLineWidthTests.cpp#L524) subgroup contains tests where the static pipeline draws first (subpass 0) and the dynamic pipeline draws second (subpass 1).

## Parameter Dimensions

| Parameter | Observed values / source |
|---|---|
| Pipeline construction type | Passed from parent group |
| Static topology | `VK_PRIMITIVE_TOPOLOGY_LINE_LIST` or `VK_PRIMITIVE_TOPOLOGY_LINE_STRIP` |
| Dynamic topology | `VK_PRIMITIVE_TOPOLOGY_LINE_LIST` or `VK_PRIMITIVE_TOPOLOGY_LINE_STRIP` |
| Static line width | 1-16 (incremented per test case) |
| Dynamic line width | 1-16 (incremented per test case) |
| Draw order | Dynamic-first (`dyna_static`) or Static-first (`static_dyna`) |
| Color format | `VK_FORMAT_R32G32B32A32_SFLOAT` |
| Render dimensions | 128x128 |

All 4 topology pair combinations × 2 draw-order variants = **8 total test cases**.

## Support / Feature Requirements

| Requirement | Check Location |
|---|---|
| `wideLines` core feature | [`LineWidthCase::checkSupport()`](../../../modules/vulkan/dynamic_state/vktDynamicStateLineWidthTests.cpp#L466) |
| Line widths within `lineWidthRange` | [`LineWidthCase::checkSupport()`](../../../modules/vulkan/dynamic_state/vktDynamicStateLineWidthTests.cpp#L457) |
| Pipeline construction requirements | [`LineWidthCase::checkSupport()`](../../../modules/vulkan/dynamic_state/vktDynamicStateLineWidthTests.cpp#L455) |

## Verification Methods

**Pixel-counting verification** via [`LineWidthInstance::verifyResults()`](../../../modules/vulkan/dynamic_state/vktDynamicStateLineWidthTests.cpp#L282):

1. The dynamic pipeline draws a horizontal line at x=0 with the dynamic width.
2. The static pipeline draws a vertical line at y=0 with the static width.
3. Count pixels in the first column (x=0) matching the dynamic color (magenta: `1,0,1,1`). The count must equal `dynamicWidth`.
4. Count pixels in the first row (y=0) matching the static color (green: `0,1,0,1`). The count must equal `staticWidth`.
5. Pass condition: `dynamicWidth == resultDynamicWidth && staticWidth == resultStaticWidth`.

Colors are pushed via push constants to distinguish dynamic vs. static line pixels.

## Test Principles Observed

- **Dynamic vs. static line width**: Tests compare rendering with dynamically set line widths against statically set line widths in the same framebuffer.
- **Draw order independence**: Both dynamic-first and static-first orderings are tested to verify the result is independent of draw order.
- **Topology combination coverage**: All 4 combinations of LINE_LIST and LINE_STRIP topologies are tested for both static and dynamic pipelines.
- **Pixel-counting precision**: The verification counts exact pixel widths rather than using fuzzy comparison, providing precise validation of line width values.

## Notes / Uncertainties

- The test requires the `wideLines` feature and line widths within the device's supported range.
- Test names encode the topology and width values (e.g., `strip2_list1` means LINE_STRIP with width 2 + LINE_LIST with width 1).
