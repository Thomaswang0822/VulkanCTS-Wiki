# vktPipelineCacheTests.cpp

## Overview

[`vktPipelineCacheTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineCacheTests.cpp#L1) implements the [`cache`](../../../modules/vulkan/pipeline/vktPipelineCacheTests.cpp#L2457) topic group. It verifies pipeline cache functionality including cache creation, merging, header validation, and blob serialization/deserialization across graphics and compute pipelines.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineCacheTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineCacheTests.cpp#L1)
- Header: [`vktPipelineCacheTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineCacheTests.hpp#L1)

## Registration Hierarchy

```text
pipeline.monolithic.cache
├── graphics_tests
├── pipeline_from_get_data
├── pipeline_from_incomplete_get_data
├── compute_tests (monolithic only)
├── merge
└── misc_tests
```

## Test Families

### graphics_tests — Graphics pipeline cache tests

Verifies pipeline cache with graphics pipelines. Contains individual test cases for different shader stage combinations (vertex+fragment, vertex+geometry+fragment, vertex+tessellation+fragment) with and without `VK_PIPELINE_CACHE_CREATE_EXTERNALLY_SYNCHRONIZED_BIT`.

### pipeline_from_get_data — Pipeline from cached data tests

Verifies creating pipelines from cached blob data retrieved via `vkGetPipelineCacheData`. Contains test cases for vertex+fragment, vertex+geometry+fragment, and vertex+tessellation+fragment shader stage combinations.

### pipeline_from_incomplete_get_data — Pipeline from incomplete cached data tests

Verifies creating pipelines from incomplete cache blob data. Contains test cases for the same shader stage combinations as `pipeline_from_get_data`. Only present in cache mode (not pipeline binary mode).

### compute_tests — Compute pipeline cache tests

Verifies pipeline cache with compute pipelines. Contains test cases for compute shader cache behavior. Only present for monolithic pipeline construction type.

### merge — Cache merge tests

Verifies pipeline cache merge operations. Contains subgroups per shader stage combination, each with test cases for various source and destination cache type combinations (empty, populated, etc.).

### misc_tests — Miscellaneous cache tests

Contains individual test cases for cache header validation, invalid size handling, zero-size cache handling, invalid blob handling, and internally synchronized cache access. The `internally_synchronized_test` is only added for monolithic pipeline construction type.

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| PipelineConstructionType | Parameter | All variant types |
| Cache merge stages | Enum | Graphics, compute, mixed |
| Cache validity | Enum | Valid, invalid, zero-size, incomplete |

## Support/Feature Requirements

| Requirement | Context |
|---|---|
| `VK_KHR_maintenance8` | Required for some maintenance8-related tests |

## Verification Methods

- **Cache hit verification**: Verify that pipeline creation from cache produces identical pipelines
- **Merge verification**: Verify that merged caches contain entries from all source caches
- **Header validation**: Verify cache header format matches specification
- **Error handling**: Verify appropriate errors for invalid cache data

## Notes

- Pipeline cache tests are VK only (guarded by `CTS_USES_VULKANSC` exclusion)
- The `internally_synchronized_test` is only added for monolithic pipeline construction type
