# vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp

## Overview

[`vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L1) documents the [`subgroups.multiple_dispatches`](../../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L304) branch. It covers multiple dispatches using uniform subgroup size.

## Role

Implementation file that registers tests under the verified group name [`multiple_dispatches`](../../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L304).

## Source Code

- Primary source: [`vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L1)

## Registration Hierarchy

```text
subgroups.multiple_dispatches
└── uniform_subgroup_size
```

## Test Families

### uniform_subgroup_size

Registered direct child of `multiple_dispatches`; generated leaves and parameter matrices are summarized from the source registration loops.

## Parameter Dimensions

- single child case `uniform_subgroup_size`, observed in [`vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L304-L306).
- The shader records one subgroup size value per elected subgroup invocation into an SSBO indexed by workgroup and subgroup id, observed in [`initPrograms()`](../../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L270-L291).

## Support / Feature Requirements

Requires subgroup-size-control support through [`MultipleDispatchesUniformSubgroupSize::checkSupport()`](../../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L262-L268).

## Verification Methods

The local compute execution clears the result buffer, dispatches each power-of-two local-size pipeline, reads back elected subgroup records, and fails if nonzero recorded subgroup sizes differ within a dispatch or if the recorded subgroup count does not match the local size rounded up by the observed subgroup size. The shader-side writes are generated in [`initPrograms()`](../../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L270-L291), and the host validation loop is in [`MultipleDispatchesUniformSubgroupSizeInstance::iterate()`](../../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L196-L243).

## Test Principles Observed

- This file registers one direct child test case.
- The test is compute-only and focuses on subgroup-size consistency across multiple dispatches.

## Notes / Uncertainties

- The hierarchy tree intentionally lists only direct children of `subgroups.multiple_dispatches`. Deeper generated leaf names are summarized rather than expanded.
- Claims are limited to inspected source under `external/vulkancts/modules/vulkan/subgroups/`.
