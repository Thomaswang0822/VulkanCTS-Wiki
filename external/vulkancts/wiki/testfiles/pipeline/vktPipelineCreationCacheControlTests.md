# vktPipelineCreationCacheControlTests.cpp

## Overview

[`vktPipelineCreationCacheControlTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineCreationCacheControlTests.cpp#L1) implements the [`creation_cache_control`](../../../modules/vulkan/pipeline/vktPipelineCreationCacheControlTests.cpp#L1351) topic group. It verifies VK_EXT_pipeline_creation_cache_control functionality, testing pipeline creation control flags that allow applications to disable cache and pipeline binary interactions.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineCreationCacheControlTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineCreationCacheControlTests.cpp#L1)
- Header: [`vktPipelineCreationCacheControlTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineCreationCacheControlTests.hpp#L1)

## Registration Path

[`createCreationCacheControlTests()`](../../../modules/vulkan/pipeline/vktPipelineCreationCacheControlTests.cpp#L1350) returns the `creation_cache_control` group, attached under each variant root by `createChildren()`.

**Variant coverage**: Monolithic only, VK only. Timing-sensitive creation tests not repeated across construction types.

## Test Hierarchy

```text
creation_cache_control
└── {test_case}
```

## Test Families

| Family | Description |
|---|---|
| Cache control test | Verifies pipeline creation cache control flags disable caching as expected |

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| PipelineConstructionType | Parameter | Monolithic only |
| Cache control flags | Bitfield | DISABLE_OPTIMIZATION, DISABLE_CACHING |

## Support/Feature Requirements

| Requirement | Context |
|---|---|
| `VK_EXT_pipeline_creation_cache_control` | Primary extension for all tests |
| `VK_KHR_maintenance5` | Required for some maintenance5-related tests |

## Verification Methods

- **Cache disable verification**: Verify that `DISABLE_CACHING` flag prevents cache storage
- **Optimization disable verification**: Verify that `DISABLE_OPTIMIZATION` flag affects pipeline creation
- **Feedback flag check**: Verify creation feedback flags reflect cache control settings

## Notes

- Only registered for monolithic pipeline construction type due to timing-sensitive behavior
- VK only (guarded by `CTS_USES_VULKANSC` exclusion)
