# vktSubgroupsPartitionedTests.cpp

## Overview

[`vktSubgroupsPartitionedTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsPartitionedTests.cpp#L1) documents the [`subgroups.partitioned`](../../../modules/vulkan/subgroups/vktSubgroupsPartitionedTests.cpp#L528) branch. It covers NV partitioned subgroup operations. The entire branch is non-VulkanSC-only because the dispatcher includes this file only inside `#ifndef CTS_USES_VULKANSC` and registers `createSubgroupsPartitionedTests()` only inside the same guard in [`vktSubgroupsTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsTests.cpp#L40-L45) and [`vktSubgroupsTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsTests.cpp#L68-L70).

## Role

Implementation file that registers tests under the verified group name [`partitioned`](../../../modules/vulkan/subgroups/vktSubgroupsPartitionedTests.cpp#L528). The group is attached to `subgroups` only for non-VulkanSC builds by the root dispatcher guard in [`vktSubgroupsTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsTests.cpp#L68-L70).

## Source Code

- Primary source: [`vktSubgroupsPartitionedTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsPartitionedTests.cpp#L1)
- Dispatcher guard: [`vktSubgroupsTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsTests.cpp#L40-L45) and [`vktSubgroupsTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsTests.cpp#L68-L70)
- Related helper source: [`vktSubgroupsTestsUtils.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L2429-L2638)
- Related helper declarations: [`vktSubgroupsTestsUtils.hpp`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.hpp#L58-L63)

## Registration Hierarchy

The entire `subgroups.partitioned` Level-3 branch is non-VulkanSC-only.

```text
subgroups.partitioned
├── graphics
├── compute
├── framebuffer
├── ray_tracing
└── mesh
```

## Test Families

### graphics

Registered direct child of `partitioned`; generated leaves and parameter matrices are summarized from the source registration loops.
### compute

Registered direct child of `partitioned`; generated leaves and parameter matrices are summarized from the source registration loops.
### framebuffer

Registered direct child of `partitioned`; generated leaves and parameter matrices are summarized from the source registration loops.
### ray_tracing

Registered direct child of `partitioned`; generated leaves and parameter matrices are summarized from the source registration loops.
### mesh

Registered direct child of `partitioned`; generated leaves and parameter matrices are summarized from the source registration loops.

## Parameter Dimensions

- partitioned operator, scan type, data format, shader stage family, framebuffer stages, mesh stages, and required subgroup size sweep, observed in [`vktSubgroupsPartitionedTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsPartitionedTests.cpp#L528-L702).
- Shared subgroup harness dimensions include framebuffer, compute, mesh, and ray-tracing execution helpers where a child group registers those stage families. The helper callback interfaces carry width/height/workgroup/local-size and `subgroupSize` data through [`CheckResult` declarations](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.hpp#L58-L63).

## Support / Feature Requirements

Subgroup support, `VK_SUBGROUP_FEATURE_PARTITIONED_BIT_NV`, subgroup-size-control, ray tracing, mesh, and stage support, with support code starting at [`vktSubgroupsPartitionedTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsPartitionedTests.cpp#L335) when this file defines a local check. Shared stage support is delegated to utilities such as [`supportedCheckShader()`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L979-L996).

## Verification Methods

Callbacks compare partitioned results with non-partitioned references over generated partitions, evidenced by local verification or test execution code in [`vktSubgroupsPartitionedTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsPartitionedTests.cpp#L439-L483) and by common helper pass/fail logic in [`vktSubgroupsTestsUtils.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L2622-L2637).

## Test Principles Observed

- The file registers a stable direct-child tree and generates deeper leaves from loops, enum values, arrays, or case lists.
- Compute-like tests generally read back SSBO/image data and call a result callback with the observed subgroup size.
- Graphics, framebuffer, mesh, and ray-tracing branches reuse common helpers so the same operation semantics are checked across supported shader stages.

## Notes / Uncertainties

- The hierarchy tree intentionally lists only direct children of `subgroups.partitioned`. Deeper generated leaf names are summarized rather than expanded.
- Claims are limited to inspected source under `external/vulkancts/modules/vulkan/subgroups/`.
