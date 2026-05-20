# vktSubgroupUniformControlFlowTests.cpp

## Overview

[`vktSubgroupUniformControlFlowTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupUniformControlFlowTests.cpp#L1) documents the [`subgroups.subgroup_uniform_control_flow`](../../../modules/vulkan/subgroups/vktSubgroupUniformControlFlowTests.cpp#L224) branch. It covers uniform-control-flow and reconvergence shader cases loaded from Amber files.

## Role

Implementation file that registers tests under the verified group name [`subgroup_uniform_control_flow`](../../../modules/vulkan/subgroups/vktSubgroupUniformControlFlowTests.cpp#L224).

## Source Code

- Primary source: [`vktSubgroupUniformControlFlowTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupUniformControlFlowTests.cpp#L1)
- Uses Amber test-case infrastructure via [`vktAmberTestCase.hpp`](../../../modules/vulkan/amber/vktAmberTestCase.hpp#L1)

## Registration Hierarchy

```text
subgroups.subgroup_uniform_control_flow
├── large_full
├── large_full_control
├── small_full
├── small_full_control
└── discard
```

## Test Families

### large_full

Source registers this full-subgroup child from the large-workgroup loop; it is present in mustpass coverage.
### large_full_control

Source registers this full-subgroup, subgroup-size-control child from the large-workgroup loop; it is present in mustpass coverage.
### large_partial

Source registers this partial-subgroup child at [`vktSubgroupUniformControlFlowTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupUniformControlFlowTests.cpp#L289-L336), but `dEQP-VK.subgroups.subgroup_uniform_control_flow.*partial*` is excluded by [`test-issues.txt`](../../../mustpass/main/src/test-issues.txt#L23-L24), so it is not listed in the parseable hierarchy tree.
### large_partial_control

Source registers this partial-subgroup, subgroup-size-control child at [`vktSubgroupUniformControlFlowTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupUniformControlFlowTests.cpp#L289-L336), but it is covered by the same mustpass exclusion.
### small_full

Source registers this full-subgroup child from the small-workgroup loop; it is present in mustpass coverage.
### small_full_control

Source registers this full-subgroup, subgroup-size-control child from the small-workgroup loop; it is present in mustpass coverage.
### small_partial

Source registers this partial-subgroup child at [`vktSubgroupUniformControlFlowTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupUniformControlFlowTests.cpp#L394-L441), but it is covered by the `*partial*` mustpass exclusion.
### small_partial_control

Source registers this partial-subgroup, subgroup-size-control child at [`vktSubgroupUniformControlFlowTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupUniformControlFlowTests.cpp#L394-L441), but it is covered by the `*partial*` mustpass exclusion.
### discard

Source registers this fragment-stage discard child at [`vktSubgroupUniformControlFlowTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupUniformControlFlowTests.cpp#L444-L449), and it is present in mustpass coverage.

## Parameter Dimensions

- large/small workgroups, full/partial subgroups, subgroup-size-control variants, discard, and many named reconvergence Amber programs, observed in [`createSubgroupUniformControlFlowTests()`](../../../modules/vulkan/subgroups/vktSubgroupUniformControlFlowTests.cpp#L224-L451).
- The full and partial compute groups are generated separately from `CaseGroup` data; full group registration is visible for large cases at [`vktSubgroupUniformControlFlowTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupUniformControlFlowTests.cpp#L236-L287), while partial group registration is visible at [`vktSubgroupUniformControlFlowTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupUniformControlFlowTests.cpp#L289-L336).

## Support / Feature Requirements

Requires `VK_KHR_shader_subgroup_uniform_control_flow`; control variants require `VK_EXT_subgroup_size_control` and its `computeFullSubgroups`/`subgroupSizeControl` features, with support code in [`initCaseGroup()`](../../../modules/vulkan/subgroups/vktSubgroupUniformControlFlowTests.cpp#L99-L116).

## Verification Methods

The Amber-backed test cases rely on generated requirements and shader execution expectations from the referenced Amber files, evidenced by the local Amber test creation path in [`addTestsForAmberFiles()`](../../../modules/vulkan/subgroups/vktSubgroupUniformControlFlowTests.cpp#L175-L199).

## Test Principles Observed

- The file registers direct children from explicit `CaseGroup` construction rather than the shared operation-family helpers used by many other subgroup operation files.
- The reconvergence cases are mainly compute-stage Amber programs, with a separate fragment-stage discard case registered at [`vktSubgroupUniformControlFlowTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupUniformControlFlowTests.cpp#L444-L449).

## Notes / Uncertainties

- The hierarchy tree intentionally lists only direct children of `subgroups.subgroup_uniform_control_flow`. Deeper generated leaf names are summarized rather than expanded.
- Claims are limited to inspected source under `external/vulkancts/modules/vulkan/subgroups/`; [`apitests.adoc`](../../../../../doc/testspecs/VK/apitests.adoc#L8-L12) gives only general API-test-plan context for this category.
