# vktSubgroupsBallotMasksTests.cpp

## Overview

[`vktSubgroupsBallotMasksTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsBallotMasksTests.cpp#L1) documents the [`subgroups.ballot_mask`](../../../modules/vulkan/subgroups/vktSubgroupsBallotMasksTests.cpp#L1417) branch. It covers legacy ballot mask built-ins under `VK_EXT_shader_subgroup_ballot`.

## Role

Implementation file that registers tests under the verified group name [`ballot_mask`](../../../modules/vulkan/subgroups/vktSubgroupsBallotMasksTests.cpp#L1417).

## Source Code

- Primary source: [`vktSubgroupsBallotMasksTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsBallotMasksTests.cpp#L1)
- Related helper source: [`vktSubgroupsTestsUtils.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L2429-L2638)
- Related helper declarations: [`vktSubgroupsTestsUtils.hpp`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.hpp#L58-L63)

## Registration Hierarchy

```text
subgroups.ballot_mask
└── ext_shader_subgroup_ballot
```

## Test Families

### ext_shader_subgroup_ballot

Registered direct child of `ballot_mask`; generated leaves and parameter matrices are summarized from the source registration loops.

## Parameter Dimensions

- mask type, shader stage family, framebuffer stages, mesh stages, and subgroup-size-control sweep capped for 64-bit masks, observed in [`vktSubgroupsBallotMasksTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsBallotMasksTests.cpp#L1417-L1525).
- Shared subgroup harness dimensions include framebuffer, compute, mesh, and ray-tracing execution helpers where a child group registers those stage families. The helper callback interfaces carry width/height/workgroup/local-size and `subgroupSize` data through [`CheckResult` declarations](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.hpp#L58-L63).

## Support / Feature Requirements

Subgroup support, `VK_EXT_shader_subgroup_ballot`, ballot feature, subgroup-size-control, ray tracing, mesh, and stage support, with support code starting at [`vktSubgroupsBallotMasksTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsBallotMasksTests.cpp#L1265) when this file defines a local check. Shared stage support is delegated to utilities such as [`supportedCheckShader()`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L979-L996).

## Verification Methods

Callbacks validate generated mask values; required-size testing caps the maximum subgroup size at 64 because the mask built-ins are 64-bit, evidenced by local verification or test execution code in [`vktSubgroupsBallotMasksTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsBallotMasksTests.cpp#L1351-L1389) and by common helper pass/fail logic in [`vktSubgroupsTestsUtils.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L2622-L2637).

## Test Principles Observed

- The file registers a stable direct-child tree and generates deeper leaves from loops, enum values, arrays, or case lists.
- Compute-like tests generally read back SSBO/image data and call a result callback with the observed subgroup size.
- Graphics, framebuffer, mesh, and ray-tracing branches reuse common helpers so the same operation semantics are checked across supported shader stages.

## Notes / Uncertainties

- The hierarchy tree intentionally lists only direct children of `subgroups.ballot_mask`. Deeper generated leaf names are summarized rather than expanded.
- Claims are limited to inspected source under `external/vulkancts/modules/vulkan/subgroups/`; [`apitests.adoc`](../../../../../doc/testspecs/VK/apitests.adoc#L8-L12) gives only general API-test-plan context for this category.
