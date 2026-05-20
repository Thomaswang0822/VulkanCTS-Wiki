# vktSubgroupsBallotTests.cpp

## Overview

[`vktSubgroupsBallotTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsBallotTests.cpp#L1) documents the [`subgroups.ballot`](../../../modules/vulkan/subgroups/vktSubgroupsBallotTests.cpp#L1021) branch. It covers ballot operations and legacy `VK_EXT_shader_subgroup_ballot` variants.

## Role

Implementation file that registers tests under the verified group name [`ballot`](../../../modules/vulkan/subgroups/vktSubgroupsBallotTests.cpp#L1021).

## Source Code

- Primary source: [`vktSubgroupsBallotTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsBallotTests.cpp#L1)
- Related helper source: [`vktSubgroupsTestsUtils.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L2429-L2638)
- Related helper declarations: [`vktSubgroupsTestsUtils.hpp`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.hpp#L58-L63)

## Registration Hierarchy

```text
subgroups.ballot
├── graphics
├── compute
├── framebuffer
├── ray_tracing (non-VulkanSC only)
├── mesh (non-VulkanSC only)
└── ext_shader_subgroup_ballot
```

## Test Families

### graphics

Registered direct child of `ballot`; generated leaves and parameter matrices are summarized from the source registration loops.
### compute

Registered direct child of `ballot`; generated leaves and parameter matrices are summarized from the source registration loops.
### framebuffer

Registered direct child of `ballot`; generated leaves and parameter matrices are summarized from the source registration loops.
### ray_tracing

Registered direct child of `ballot`; generated leaves and parameter matrices are summarized from the source registration loops.
### mesh

Registered direct child of `ballot`; generated leaves and parameter matrices are summarized from the source registration loops.
### ext_shader_subgroup_ballot

Registered direct child of `ballot`; generated leaves and parameter matrices are summarized from the source registration loops.

## Parameter Dimensions

- ballot operation type, shader stage family, framebuffer stages, mesh stages, and extension variant, observed in [`vktSubgroupsBallotTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsBallotTests.cpp#L1021-L1157).
- Shared subgroup harness dimensions include framebuffer, compute, mesh, and ray-tracing execution helpers where a child group registers those stage families. The helper callback interfaces carry width/height/workgroup/local-size and `subgroupSize` data through [`CheckResult` declarations](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.hpp#L58-L63).

## Support / Feature Requirements

Subgroup support, `VK_SUBGROUP_FEATURE_BALLOT_BIT`, subgroup-size-control, ray tracing, mesh, and stage support, with support code starting at [`vktSubgroupsBallotTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsBallotTests.cpp#L831) when this file defines a local check. Shared stage support is delegated to utilities such as [`supportedCheckShader()`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L979-L996).

## Verification Methods

The checks compare shader output bitmasks through framebuffer and compute-like helper callbacks, evidenced by local verification or test execution code in [`vktSubgroupsBallotTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsBallotTests.cpp#L931-L975) and by common helper pass/fail logic in [`vktSubgroupsTestsUtils.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L2622-L2637).

## Test Principles Observed

- The file registers a stable direct-child tree and generates deeper leaves from loops, enum values, arrays, or case lists.
- Compute-like tests generally read back SSBO/image data and call a result callback with the observed subgroup size.
- Graphics, framebuffer, mesh, and ray-tracing branches reuse common helpers so the same operation semantics are checked across supported shader stages.

## Notes / Uncertainties

- The hierarchy tree intentionally lists only direct children of `subgroups.ballot`. Deeper generated leaf names are summarized rather than expanded.
- Claims are limited to inspected source under `external/vulkancts/modules/vulkan/subgroups/`; [`apitests.adoc`](../../../../../doc/testspecs/VK/apitests.adoc#L8-L12) gives only general API-test-plan context for this category.
