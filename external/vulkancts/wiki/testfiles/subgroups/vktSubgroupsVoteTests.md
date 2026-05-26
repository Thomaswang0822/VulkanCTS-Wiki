# vktSubgroupsVoteTests.cpp

## Overview

[`vktSubgroupsVoteTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsVoteTests.cpp#L1) documents the [`subgroups.vote`](../../../modules/vulkan/subgroups/vktSubgroupsVoteTests.cpp#L547) branch. It covers vote operations and legacy `VK_EXT_shader_subgroup_vote` variants.

## Role

Implementation file that registers tests under the verified group name [`vote`](../../../modules/vulkan/subgroups/vktSubgroupsVoteTests.cpp#L547).

## Source Code

- Primary source: [`vktSubgroupsVoteTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsVoteTests.cpp#L1)
- Related helper source: [`vktSubgroupsTestsUtils.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L2429-L2638)
- Related helper declarations: [`vktSubgroupsTestsUtils.hpp`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.hpp#L58-L63)

## Registration Hierarchy

```text
subgroups.vote
├── graphics
├── compute
├── framebuffer
├── frag_helper
├── ray_tracing (non-VulkanSC only)
├── mesh (non-VulkanSC only)
└── ext_shader_subgroup_vote
```

## Test Families

### graphics

Registered direct child of `vote`; generated leaves and parameter matrices are summarized from the source registration loops.
### compute

Registered direct child of `vote`; generated leaves and parameter matrices are summarized from the source registration loops.
### framebuffer

Registered direct child of `vote`; generated leaves and parameter matrices are summarized from the source registration loops.
### frag_helper

Registered direct child of `vote`; generated leaves and parameter matrices are summarized from the source registration loops.
### ray_tracing

Registered direct child of `vote`; generated leaves and parameter matrices are summarized from the source registration loops.
### mesh

Registered direct child of `vote`; generated leaves and parameter matrices are summarized from the source registration loops.
### ext_shader_subgroup_vote

Registered direct child of `vote`; generated leaves and parameter matrices are summarized from the source registration loops.

## Parameter Dimensions

- vote op type, bool input value, shader stage family, format, and extension variant, observed in [`vktSubgroupsVoteTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsVoteTests.cpp#L547-L765).
- Shared subgroup harness dimensions include framebuffer, compute, mesh, and ray-tracing execution helpers where a child group registers those stage families. The helper callback interfaces carry width/height/workgroup/local-size and `subgroupSize` data through [`CheckResult` declarations](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.hpp#L58-L63).

## Support / Feature Requirements

Subgroup support, `VK_SUBGROUP_FEATURE_VOTE_BIT`, `VK_EXT_shader_subgroup_vote` for extension branches, subgroup-size-control, ray tracing, mesh, and stage support, with support code starting at [`vktSubgroupsVoteTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsVoteTests.cpp#L323) when this file defines a local check. Shared stage support is delegated to utilities such as [`supportedCheckShader()`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L979-L996).

## Verification Methods

Callbacks validate vote results in vertex/fragment/compute-like paths, with common helpers checking buffer contents, evidenced by local verification or test execution code in [`vktSubgroupsVoteTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsVoteTests.cpp#L459-L502) and by common helper pass/fail logic in [`vktSubgroupsTestsUtils.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L2622-L2637).

## Test Principles Observed

- The file registers a stable direct-child tree and generates deeper leaves from loops, enum values, arrays, or case lists.
- Compute-like tests generally read back SSBO/image data and call a result callback with the observed subgroup size.
- Graphics, framebuffer, mesh, and ray-tracing branches reuse common helpers so the same operation semantics are checked across supported shader stages.

## Notes / Uncertainties

- The hierarchy tree intentionally lists only direct children of `subgroups.vote`. Deeper generated leaf names are summarized rather than expanded.
- Claims are limited to inspected source under `external/vulkancts/modules/vulkan/subgroups/`.
