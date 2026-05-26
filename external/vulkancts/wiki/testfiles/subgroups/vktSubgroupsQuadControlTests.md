# vktSubgroupsQuadControlTests.cpp

## Overview

[`vktSubgroupsQuadControlTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsQuadControlTests.cpp#L1) documents the [`subgroups.shader_quad_control`](../../../modules/vulkan/subgroups/vktSubgroupsQuadControlTests.cpp#L807) branch. It covers `VK_KHR_shader_quad_control` draw tests. The entire branch is non-VulkanSC-only because the dispatcher includes this file only inside `#ifndef CTS_USES_VULKANSC` and registers `createSubgroupsQuadControlTests()` only inside the same guard in [`vktSubgroupsTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsTests.cpp#L40-L45) and [`vktSubgroupsTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsTests.cpp#L77-L81).

## Role

Implementation file that registers tests under the verified group name [`shader_quad_control`](../../../modules/vulkan/subgroups/vktSubgroupsQuadControlTests.cpp#L807). The group is attached to `subgroups` only for non-VulkanSC builds by the dispatcher guard in [`vktSubgroupsTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsTests.cpp#L77-L81).

## Source Code

- Primary source: [`vktSubgroupsQuadControlTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsQuadControlTests.cpp#L1)
- Dispatcher guard: [`vktSubgroupsTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsTests.cpp#L40-L45) and [`vktSubgroupsTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsTests.cpp#L77-L81)

## Registration Hierarchy

The entire `subgroups.shader_quad_control` Level-3 branch is non-VulkanSC-only.

```text
subgroups.shader_quad_control
├── quad_derivatives
├── require_full_quads
├── divergent_condition
└── terminated_invocation
```

## Test Families

### quad_derivatives

Registered direct child of `shader_quad_control`; generated leaves and parameter matrices are summarized from the source registration loops.
### require_full_quads

Registered direct child of `shader_quad_control`; generated leaves and parameter matrices are summarized from the source registration loops.
### divergent_condition

Registered direct child of `shader_quad_control`; generated leaves and parameter matrices are summarized from the source registration loops.
### terminated_invocation

Registered direct child of `shader_quad_control`; generated leaves and parameter matrices are summarized from the source registration loops.

## Parameter Dimensions

- test mode selected from four direct child cases, observed in [`createSubgroupsQuadControlTests()`](../../../modules/vulkan/subgroups/vktSubgroupsQuadControlTests.cpp#L807-L820).
- The four modes map to `quad_derivatives`, `require_full_quads`, `divergent_condition`, and `terminated_invocation` test cases in the registration function.

## Support / Feature Requirements

Requires `VK_KHR_shader_quad_control`. Terminated-invocation mode also requires `VK_KHR_shader_terminate_invocation` and at least one of `VK_KHR_shader_maximal_reconvergence` or `VK_KHR_shader_subgroup_uniform_control_flow`, with support checks in [`DrawWithQuadControlTestCase::checkSupport()`](../../../modules/vulkan/subgroups/vktSubgroupsQuadControlTests.cpp#L621-L633).

## Verification Methods

The draw test returns pass when `isResultCorrect()` accepts the output image/buffer access, evidenced by result-checking code in [`isResultCorrect()`](../../../modules/vulkan/subgroups/vktSubgroupsQuadControlTests.cpp#L569-L576) and the test iteration path that calls it in [`DrawWithQuadControlTestInstance::iterate()`](../../../modules/vulkan/subgroups/vktSubgroupsQuadControlTests.cpp#L331-L336).

## Test Principles Observed

- This file registers four direct child draw tests for `VK_KHR_shader_quad_control` behavior.
- The implementation is draw-oriented; it is not a shared compute/mesh/ray-tracing subgroup-helper matrix like many operation files in this category.

## Notes / Uncertainties

- The hierarchy tree intentionally lists only direct children of `subgroups.shader_quad_control`. Deeper generated leaf names are summarized rather than expanded.
- Claims are limited to inspected source under `external/vulkancts/modules/vulkan/subgroups/`.
