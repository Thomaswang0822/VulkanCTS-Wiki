# vktFragmentShadingRateTests.cpp

This page documents the root dispatcher and miscellaneous property tests in the Vulkan CTS `fragment_shading_rate` category.

## Overview

[`vktFragmentShadingRateTests.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateTests.cpp#L1) creates the category root, registers render-pass and dynamic-rendering top-level branches, and dispatches shared branch builders for basic, attachment-rate, misc, and pixel-consistency tests. The root `createTests()` function constructs `renderpass2` unconditionally and `dynamic_rendering` outside Vulkan SC builds at [`vktFragmentShadingRateTests.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateTests.cpp#L629-L650).

## Role of File

- Root registration / dispatcher file.
- Also provides the `misc.limits` and `misc.shading_rates` function tests when the current permutation is renderpass2, non-secondary-command-buffer, and monolithic pipeline at [`vktFragmentShadingRateTests.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateTests.cpp#L514-L531).

## Registration Hierarchy

```text
fragment_shading_rate
├── renderpass2
└── dynamic_rendering (non-VulkanSC only)
```

## Test Families

### renderpass2 — Render pass object permutations

The `renderpass2` group uses render-pass objects and starts pipeline-construction permutations with `monolithic`, and outside Vulkan SC also `pipeline_library` and `fast_linked_library` at [`vktFragmentShadingRateTests.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateTests.cpp#L634-L642) and [`vktFragmentShadingRateTests.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateTests.cpp#L559-L592).

### dynamic_rendering — Dynamic rendering permutations

The non-Vulkan SC `dynamic_rendering` group creates `primary_cmd_buff`, `partial_secondary_cmd_buff`, and `complete_secondary_cmd_buff` descendants at [`vktFragmentShadingRateTests.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateTests.cpp#L594-L623). The shared parameters record whether dynamic rendering and secondary command buffers are in use.

## Parameter Dimensions

| Dimension | Observed values / source |
|---|---|
| Rendering path | `renderpass2` and non-Vulkan SC `dynamic_rendering` at [`vktFragmentShadingRateTests.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateTests.cpp#L629-L648) |
| Pipeline construction type | `monolithic`, non-Vulkan SC `pipeline_library`, and non-Vulkan SC `fast_linked_library` at [`vktFragmentShadingRateTests.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateTests.cpp#L573-L591) |
| Dynamic-rendering command-buffer mode | `primary_cmd_buff`, `partial_secondary_cmd_buff`, `complete_secondary_cmd_buff` at [`vktFragmentShadingRateTests.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateTests.cpp#L610-L623) |
| Shared group parameters | The `GroupParams` structure records dynamic rendering, secondary command buffer, complete secondary dynamic-renderpass, and pipeline construction fields at [`vktFragmentShadingRateGroupParams.hpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateGroupParams.hpp#L34-L50) |

## Support / Feature Requirements

The category-level property tests require `VK_KHR_fragment_shading_rate` at [`checkSupport()`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateTests.cpp#L509-L512). The root dispatcher does not gate registration; implementation files perform per-case checks.

## Verification Methods

`testLimits()` logs and fails when fragment-shading-rate property relationships violate expected constraints, returning pass only if all checks remain true at [`vktFragmentShadingRateTests.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateTests.cpp#L280-L300). `testShadingRates()` queries `vkGetPhysicalDeviceFragmentShadingRatesKHR` and validates rate dimensions, sample counts, coverage limits, and ordering conditions at [`vktFragmentShadingRateTests.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateTests.cpp#L303-L425).

## Test Principles

This file separates high-level registration permutations from branch-specific generators and uses `SharedGroupParams` to pass rendering and pipeline-construction context to lower-level files.

## Notes / Uncertainties

`dynamic_rendering`, pipeline-library roots, and fast-linked-library roots are excluded from Vulkan SC by preprocessor guards in the inspected file.
