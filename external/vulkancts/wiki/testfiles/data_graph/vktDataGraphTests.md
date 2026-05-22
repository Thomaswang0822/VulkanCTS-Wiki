# vktDataGraphTests

This page documents the root registration file for the Vulkan CTS `data_graph` category.

## Overview

`vktDataGraphTests.cpp` is the category dispatcher for `dEQP-VK.data_graph`. The root package adds the category with the registered name `data_graph`, and this file attaches three direct child groups: `basic`, `cache`, and `properties`.

## Role of File

- **Registration file:** yes. It creates the category-level `TestCaseGroup` and delegates implementation to three group builder functions.
- **Implementation file:** no. It does not create Vulkan data-graph objects directly; the implementation work is in the child files documented below.

## Source Code Links

| Item | Evidence |
|------|----------|
| Package root registers `data_graph` | [vktTestPackage.cpp](../../../modules/vulkan/vktTestPackage.cpp#L1398-L1400) |
| Root group creation and direct children | [vktDataGraphTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphTests.cpp#L39-L47) |
| Included child headers | [vktDataGraphTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphTests.cpp#L28-L31) |

## Registration Hierarchy

```text
data_graph
├── basic
├── cache
└── properties
```

## Test Families

### basic — Basic pipeline creation and dispatch

The root file registers `basic` by calling `createTestGroup(testCtx, "basic", basicTestsGroup)`. The target group is implemented in [vktDataGraphBasicTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphBasicTests.cpp#L423-L427) and has Level-3 documentation in [vktDataGraphBasicTests](vktDataGraphBasicTests.md).

### cache — Data graph pipeline cache behavior

The root file registers `cache` by calling `createTestGroup(testCtx, "cache", cacheTestsGroup)`. The target group is implemented in [vktDataGraphPipelineCacheTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L851-L855) and has Level-3 documentation in [vktDataGraphPipelineCacheTests](vktDataGraphPipelineCacheTests.md).

### properties — Data graph pipeline property queries

The root file registers `properties` by calling `createTestGroup(testCtx, "properties", propertiesTestsGroup)`. The target group is implemented in [vktDataGraphPropertiesTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L547-L551) and has Level-3 documentation in [vktDataGraphPropertiesTests](vktDataGraphPropertiesTests.md).

## Parameter Dimensions

The root dispatcher does not define test parameters. The direct children use shared `TestParams` generation from [vktDataGraphTestUtil.cpp](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.cpp#L175-L220), including instruction set, session-memory usage, resource cardinalities, stride modes, binding order, tensor tiling, sparse constants, and provider-selected format strings.

## Support and Feature Requirements

The root dispatcher does not perform support checks. Shared `TestParams::checkSupport()` requires `VK_ARM_data_graph`, `VK_ARM_tensors`, the `dataGraph`, `dataGraphShaderModule`, `tensors`, and `shaderTensorAccess` features, and conditionally requires `tensorNonPacked` when non-packed resources are requested [vktDataGraphTestUtil.hpp](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.hpp#L220-L256).

## Verification Methods

No Vulkan verification is performed in the dispatcher. Verification is delegated to the registered child groups.

## Test Principles

- Keep category registration small and explicit: each direct child is registered by name in one place [vktDataGraphTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphTests.cpp#L39-L47).
- Separate dispatch from implementation so that pipeline construction, cache behavior, and property queries are documented in their own Level-3 pages.

## Notes and Uncertainties

The Vulkan API test plan inspected for this task did not contain a `data_graph` section, so this page relies on source and mustpass evidence rather than test-plan prose.