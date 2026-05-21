# vktConditionalDrawAndClearTests.cpp

## Overview

This file registers the `draw_clear` group. It has two direct children: `clear`, which contains color and depth clear tests, and `draw`, which contains draw/update-buffer interactions with conditional rendering.

## Role and Source

| Item | Evidence |
|---|---|
| Source file | [vktConditionalDrawAndClearTests.cpp](../../../modules/vulkan/conditional_rendering/vktConditionalDrawAndClearTests.cpp) |
| Registered group and children | [vktConditionalDrawAndClearTests.cpp registration](../../../modules/vulkan/conditional_rendering/vktConditionalDrawAndClearTests.cpp#L1698-L1767) |
| Shared condition-data table | [vktConditionalRenderingTestUtil.hpp](../../../modules/vulkan/conditional_rendering/vktConditionalRenderingTestUtil.hpp#L44-L144) |
| Shared capability helper | [checkConditionalRenderingCapabilities()](../../../modules/vulkan/conditional_rendering/vktConditionalRenderingTestUtil.cpp#L36-L58) |

## Registration Hierarchy

```text
conditional_rendering.draw_clear
├── clear
└── draw
```

## Test Families

### Direct registered children

The `clear` child contains `color` and `depth` subgroups populated from clear-parameter grids. The `draw` child contains generated draw cases, non-VulkanSC maintenance5 and device-address-command variants, and update-buffer-with-draw cases.

## Parameter Dimensions

Clear names encode discard/no-discard, invert/no-invert, partial/full clear, offset/no-offset, and host/local memory. Draw names encode generated case index and memory type; additional variants toggle maintenance5 and device-address-command paths where registered.

## Support Requirements

The base support check requires `VK_EXT_conditional_rendering`. Draw cases also check triangle-fan portability-subset support where relevant; maintenance5 and device-address-command variants require `VK_KHR_maintenance5` and `VK_KHR_device_address_commands`, respectively. The update-buffer-with-draw support path also checks vertex pipeline stores and atomics.

## Verification Methods

The clear and draw test instances compare rendered results against reference images using `tcu::floatThresholdCompare()` with `tcu::Vec4(0.01f)` thresholds.

## Test Principles

The implementation varies whether the conditional-rendering predicate should execute or suppress work, then verifies externally visible image, buffer, or transform-feedback results rather than relying only on successful command submission.

## Notes and Uncertainties

The hierarchy tree lists only one direct level below `conditional_rendering.draw_clear` as required by the wiki registration contract. Deeper generated leaves are described in prose because they are registered below those direct children.
