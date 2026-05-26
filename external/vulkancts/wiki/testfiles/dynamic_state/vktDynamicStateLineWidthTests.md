# vktDynamicStateLineWidthTests.cpp

## Overview

[`vktDynamicStateLineWidthTests.cpp`](../../../modules/vulkan/dynamic_state/vktDynamicStateLineWidthTests.cpp#L1) implements the [`line_width`](../../../modules/vulkan/dynamic_state/vktDynamicStateLineWidthTests.cpp#L478) subgroup of the dynamic_state category. It tests dynamic line width state via `vkCmdSetLineWidth`, verifying that different line widths are correctly applied when drawing lines with both static and dynamic pipelines in a two-subpass render pass.

## Role

Implementation file.

## Source Code

- Primary source: [`vktDynamicStateLineWidthTests.cpp`](../../../modules/vulkan/dynamic_state/vktDynamicStateLineWidthTests.cpp#L1)
- Shared base: [`DynamicStateBaseClass`](../../../modules/vulkan/dynamic_state/vktDynamicStateBaseClass.hpp#L43)

## Registration Hierarchy

```text
dynamic_state.monolithic.line_width
├── dyna_static
└── static_dyna
```

Source: [`DynamicStateLWTests::init()`](../../../modules/vulkan/dynamic_state/vktDynamicStateLineWidthTests.cpp#L508).

## Test Families

### dyna_static — Dynamic pipeline first, static pipeline second

The [`dyna_static`](../../../modules/vulkan/dynamic_state/vktDynamicStateLineWidthTests.cpp#L523) subgroup contains tests where the dynamic pipeline draws first (subpass 0) and the static pipeline draws second (subpass 1). Case names follow [`TestLineWidthParams::rep()`](../../../modules/vulkan/dynamic_state/vktDynamicStateLineWidthTests.cpp#L484): dynamic-first cases encode `<dynamicTopology><dynamicWidth>_<staticTopology><staticWidth>`. The four leaf tests are `strip2_list1`, `list6_list5`, `list10_strip9`, and `strip14_strip13`.

### static_dyna — Static pipeline first, dynamic pipeline second

The [`static_dyna`](../../../modules/vulkan/dynamic_state/vktDynamicStateLineWidthTests.cpp#L524) subgroup contains tests where the static pipeline draws first (subpass 0) and the dynamic pipeline draws second (subpass 1). Static-first cases encode `<staticTopology><staticWidth>_<dynamicTopology><dynamicWidth>`. The four leaf tests are `list3_strip4`, `list7_list8`, `strip11_list12`, and `strip15_strip16`.

## Parameter Dimensions

| Parameter | Observed values / source |
|---|---|
| Pipeline construction type | Passed from parent group |
| Static topology | `VK_PRIMITIVE_TOPOLOGY_LINE_LIST` or `VK_PRIMITIVE_TOPOLOGY_LINE_STRIP` |
| Dynamic topology | `VK_PRIMITIVE_TOPOLOGY_LINE_LIST` or `VK_PRIMITIVE_TOPOLOGY_LINE_STRIP` |
| Static line width | Odd values 1, 3, 5, 7, 9, 11, 13, 15 assigned by the registration loop |
| Dynamic line width | Even values 2, 4, 6, 8, 10, 12, 14, 16 assigned immediately after the static width |
| Draw order | Dynamic-first (`dyna_static`) or static-first (`static_dyna`); this also controls name-component order |
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
