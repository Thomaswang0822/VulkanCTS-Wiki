# vktSubgroupsArithmeticTests.cpp

## Overview

[`vktSubgroupsArithmeticTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsArithmeticTests.cpp#L1) documents the [`subgroups.arithmetic`](../../../modules/vulkan/subgroups/vktSubgroupsArithmeticTests.cpp#L477) branch. It covers arithmetic subgroup reductions and scans.

## Role

Implementation file that registers tests under the verified group name [`arithmetic`](../../../modules/vulkan/subgroups/vktSubgroupsArithmeticTests.cpp#L477).

## Source Code

- Primary source: [`vktSubgroupsArithmeticTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsArithmeticTests.cpp#L1)
- Related helper source: [`vktSubgroupsTestsUtils.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L2429-L2638)
- Related helper declarations: [`vktSubgroupsTestsUtils.hpp`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.hpp#L58-L63)

## Registration Hierarchy

```text
subgroups.arithmetic
├── graphics
├── compute
├── framebuffer
├── ray_tracing (non-VulkanSC only)
└── mesh (non-VulkanSC only)
```

## Test Families

### graphics

Registered direct child of `arithmetic`; generated leaves and parameter matrices are summarized from the source registration loops.
### compute

Registered direct child of `arithmetic`; generated leaves and parameter matrices are summarized from the source registration loops.
### framebuffer

Registered direct child of `arithmetic`; generated leaves and parameter matrices are summarized from the source registration loops.
### ray_tracing

Registered direct child of `arithmetic`; generated leaves and parameter matrices are summarized from the source registration loops.
### mesh

Registered direct child of `arithmetic`; generated leaves and parameter matrices are summarized from the source registration loops.

## Parameter Dimensions

- operator, scan type, data format, shader stage family, framebuffer stages, mesh stages, and required subgroup size sweep, observed in [`vktSubgroupsArithmeticTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsArithmeticTests.cpp#L477-L662).
- Shared subgroup harness dimensions include framebuffer, compute, mesh, and ray-tracing execution helpers where a child group registers those stage families. The helper callback interfaces carry width/height/workgroup/local-size and `subgroupSize` data through [`CheckResult` declarations](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.hpp#L58-L63).

## Support / Feature Requirements

Subgroup support, `VK_SUBGROUP_FEATURE_ARITHMETIC_BIT`, subgroup-size-control, ray tracing, mesh, and stage support, with support code starting at [`vktSubgroupsArithmeticTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsArithmeticTests.cpp#L279) when this file defines a local check. Shared stage support is delegated to utilities such as [`supportedCheckShader()`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L979-L996).

## Verification Methods

Callbacks validate operation results against reference arithmetic reductions/scans stored in result buffers, evidenced by local verification or test execution code in [`vktSubgroupsArithmeticTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsArithmeticTests.cpp#L387-L430) and by common helper pass/fail logic in [`vktSubgroupsTestsUtils.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L2622-L2637).

## Test Principles Observed

- The file registers a stable direct-child tree and generates deeper leaves from loops, enum values, arrays, or case lists.
- Compute-like tests generally read back SSBO/image data and call a result callback with the observed subgroup size.
- Graphics, framebuffer, mesh, and ray-tracing branches reuse common helpers so the same operation semantics are checked across supported shader stages.

## Notes / Uncertainties

- The hierarchy tree intentionally lists only direct children of `subgroups.arithmetic`. Deeper generated leaf names are summarized rather than expanded.
- Claims are limited to inspected source under `external/vulkancts/modules/vulkan/subgroups/`; [`apitests.adoc`](../../../../../doc/testspecs/VK/apitests.adoc#L8-L12) gives only general API-test-plan context for this category.
