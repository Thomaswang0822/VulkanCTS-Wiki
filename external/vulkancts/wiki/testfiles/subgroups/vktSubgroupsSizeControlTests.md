# vktSubgroupsSizeControlTests.cpp

## Overview

[`vktSubgroupsSizeControlTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsSizeControlTests.cpp#L1) documents the [`subgroups.size_control`](../../../modules/vulkan/subgroups/vktSubgroupsSizeControlTests.cpp#L1015) branch. It covers subgroup size control properties, allow-varying-size, require-full-subgroups, and required subgroup size paths.

## Role

Implementation file that registers tests under the verified group name [`size_control`](../../../modules/vulkan/subgroups/vktSubgroupsSizeControlTests.cpp#L1015).

## Source Code

- Primary source: [`vktSubgroupsSizeControlTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsSizeControlTests.cpp#L1)
- Related helper source: [`vktSubgroupsTestsUtils.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L2429-L2638)
- Related helper declarations: [`vktSubgroupsTestsUtils.hpp`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.hpp#L58-L63)

## Registration Hierarchy

```text
subgroups.size_control
├── generic
├── graphics
├── compute
├── framebuffer
├── ray_tracing (non-VulkanSC only)
└── mesh (non-VulkanSC only)
```

## Test Families

### generic

Registered direct child of `size_control`; generated leaves and parameter matrices are summarized from the source registration loops.
### graphics

Registered direct child of `size_control`; generated leaves and parameter matrices are summarized from the source registration loops.
### compute

Registered direct child of `size_control`; generated leaves and parameter matrices are summarized from the source registration loops.
### framebuffer

Registered direct child of `size_control`; generated leaves and parameter matrices are summarized from the source registration loops.
### ray_tracing

Registered direct child of `size_control`; generated leaves and parameter matrices are summarized from the source registration loops.
### mesh

Registered direct child of `size_control`; generated leaves and parameter matrices are summarized from the source registration loops.

## Parameter Dimensions

- required subgroup size mode, SPIR-V version, shader-stage flags, allow-varying/full-subgroups flags, min/max required size, and local size matrices, observed in [`vktSubgroupsSizeControlTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsSizeControlTests.cpp#L1015-L1251).
- Shared subgroup harness dimensions include framebuffer, compute, mesh, and ray-tracing execution helpers where a child group registers those stage families. The helper callback interfaces carry width/height/workgroup/local-size and `subgroupSize` data through [`CheckResult` declarations](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.hpp#L58-L63).

## Support / Feature Requirements

Requires subgroup support and `VK_EXT_subgroup_size_control`; additionally checks ballot, required-size stages, full subgroup support, ray tracing, mesh, and stage support, with support code starting at [`vktSubgroupsSizeControlTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsSizeControlTests.cpp#L506) when this file defines a local check. Shared stage support is delegated to utilities such as [`supportedCheckShader()`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L979-L996).

## Verification Methods

Checks confirm `gl_SubgroupSize` is inside advertised min/max limits and equals required sizes when requested, evidenced by local verification or test execution code in [`vktSubgroupsSizeControlTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsSizeControlTests.cpp#L127-L283) and by common helper pass/fail logic in [`vktSubgroupsTestsUtils.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L2622-L2637).

## Test Principles Observed

- The file registers a stable direct-child tree and generates deeper leaves from loops, enum values, arrays, or case lists.
- Compute-like tests generally read back SSBO/image data and call a result callback with the observed subgroup size.
- Graphics, framebuffer, mesh, and ray-tracing branches reuse common helpers so the same operation semantics are checked across supported shader stages.

## Notes / Uncertainties

- The hierarchy tree intentionally lists only direct children of `subgroups.size_control`. Deeper generated leaf names are summarized rather than expanded.
- Claims are limited to inspected source under `external/vulkancts/modules/vulkan/subgroups/`.
