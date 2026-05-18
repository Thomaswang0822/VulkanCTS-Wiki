# vktFragmentOperationsOcclusionQueryTests.cpp

## Overview

[`vktFragmentOperationsOcclusionQueryTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L1) implements the displayed `occlusion_query` subgroup under [`fragment_operations`](../../categories/fragment_operations.md). The file verifies occlusion-query results while varying scissor use, depth clears, depth writes, stencil clears, stencil writes, and an aggregated `test_all` mode, with both conservative and precise query variants.

## Role

Registration and implementation file. It owns the user-visible `occlusion_query` subgroup and includes query-pool creation, render setup, optional depth-stencil paths, query-result retrieval, and pass/fail evaluation.

## Source Code

- Primary source: [`vktFragmentOperationsOcclusionQueryTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L1)
- Header: [`vktFragmentOperationsOcclusionQueryTests.hpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.hpp)

## Registration Hierarchy

```text
fragment_operations.occlusion_query
├── conservative*_test_scissors_*
├── conservative*_test_depth_*
├── conservative*_test_stencil_*
├── conservative*_test_all
├── precise*_test_scissors_*
├── precise*_test_depth_*
├── precise*_test_stencil_*
└── precise*_test_all
```

Source: [`createOcclusionQueryTests()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L706-L767).

## Test Families

### Conservative variants

[`createOcclusionQueryTests()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L755-L758) prefixes every case-table name with `conservative`. These variants begin the query without `VK_QUERY_CONTROL_PRECISE_BIT` at [`vktFragmentOperationsOcclusionQueryTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L480-L485) and later accept any non-zero sample count as success in [`vktFragmentOperationsOcclusionQueryTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L572-L573).

### Precise variants

[`createOcclusionQueryTests()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L760-L763) prefixes every case-table name with `precise` and adds [`TEST_PRECISE_BIT`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L226-L236). These variants begin the query with `VK_QUERY_CONTROL_PRECISE_BIT` at [`vktFragmentOperationsOcclusionQueryTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L480-L482) and later require an exact expected sample count in [`vktFragmentOperationsOcclusionQueryTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L572-L573).

### Case-table dimensions

The case table in [`vktFragmentOperationsOcclusionQueryTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L710-L753) combines the following named behaviors:

- scissor-only color path: `_test_scissors_clear_color`
- scissor plus depth clear and-or depth write paths
- scissor plus stencil clear and-or stencil write paths
- mixed depth and stencil clear-write combinations
- `*_test_all` aggregate cases
- matching non-scissor cases such as `_test_clear_color`, `_test_depth_clear`, `_test_stencil_write`, and `_test_test_all`

The names are evidence-backed directly by the case table at [`vktFragmentOperationsOcclusionQueryTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L716-L753).

## Parameter Dimensions

| Dimension | Observed values / source |
|---|---|
| Query precision mode | Conservative versus precise from the two registration loops at [`vktFragmentOperationsOcclusionQueryTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L755-L763) |
| Modifier flags | `TEST_SCISSOR`, `TEST_DEPTH_WRITE`, `TEST_DEPTH_CLEAR`, `TEST_STENCIL_WRITE`, `TEST_STENCIL_CLEAR`, `TEST_ALL`, `TEST_PRECISE_BIT` in [`Flags`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L226-L236) |
| Render size | `32 x 32` in the constructor arguments at [`vktFragmentOperationsOcclusionQueryTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L758-L763) |
| Depth-stencil format selection | Combined DS formats, stencil-only `VK_FORMAT_S8_UINT`, or depth-only format path selected around [`vktFragmentOperationsOcclusionQueryTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L315-L320) and helper selection in [`pickSupportedDepthStencilFormat()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L211-L224) |
| Scissor rectangle behavior | Full render area versus central inset area in [`makeGraphicsPipeline()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L101-L106) |

## Support Requirements

[`OcclusionQueryTest::checkSupport()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L675-L701) validates that the selected test format is supported and throws `NotSupportedError` when no compatible format exists at [`vktFragmentOperationsOcclusionQueryTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L700-L701). For precise variants, it explicitly checks `occlusionQueryPrecise` against `VK_QUERY_CONTROL_PRECISE_BIT` at [`vktFragmentOperationsOcclusionQueryTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L690-L694).

## Verification Methods

The test creates a query pool of type `VK_QUERY_TYPE_OCCLUSION` at [`vktFragmentOperationsOcclusionQueryTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L288-L299), resets it before use at [`vktFragmentOperationsOcclusionQueryTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L445-L447), wraps the draw with `cmdBeginQuery` and `cmdEndQuery` at [`vktFragmentOperationsOcclusionQueryTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L480-L489), and reads back results with [`vk.getQueryPoolResults()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L557-L558).

The pass rule is explicit in [`vktFragmentOperationsOcclusionQueryTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L572-L573): precise mode requires `sampleCounts[0] == expResult`, while conservative mode requires `sampleCounts[0] > 0`. The file also logs both the observed sample count and expected result at [`vktFragmentOperationsOcclusionQueryTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L563-L565).

## Notes / Uncertainties

- This file is implementation-heavy even though its registration shape is a flat direct-child list of generated case names.
- The parseable hierarchy intentionally groups generated names by prefix pattern instead of exhaustively listing all direct children, because the file registers dozens of concrete names from one case table.
