# vktPipelineCacheTests.cpp

## Overview

[`vktPipelineCacheTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineCacheTests.cpp#L1) implements the [`cache`](../../../modules/vulkan/pipeline/vktPipelineCacheTests.cpp#L2457) topic group. It verifies pipeline cache functionality including cache creation, merging, header validation, and blob serialization/deserialization across graphics and compute pipelines.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineCacheTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineCacheTests.cpp#L1)
- Header: [`vktPipelineCacheTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineCacheTests.hpp#L1)

## Registration Path

[`createCacheTests()`](../../../modules/vulkan/pipeline/vktPipelineCacheTests.cpp#L2455) returns the `cache` group, attached under each variant root by `createChildren()`.

**Variant coverage**: All variants, VK only.

## Test Hierarchy

```text
cache
└── blob_tests
    ├── graphics
    │   └── {test_param}
    ├── pipeline_from_blobs
    │   └── {test_param}
    ├── pipeline_from_incomplete_blobs
    │   └── {test_param}
    ├── compute
    │   └── {test_param}
    ├── merge
    │   └── {merge_stages}
    │       └── {merge_test}
    └── misc
        ├── cache_header_test
        ├── invalid_size_test
        ├── zero_size_test
        ├── invalid_blob_test
        └── internally_synchronized_test
```

## Test Families

| Family | Description |
|---|---|
| GraphicsTest | Verifies pipeline cache with graphics pipelines |
| PipelineFromBlobsTest | Verifies creating pipelines from cached blobs |
| PipelineFromIncompleteBlobsTest | Verifies creating pipelines from incomplete cache blobs |
| ComputeTest | Verifies pipeline cache with compute pipelines |
| MergeTest | Verifies pipeline cache merge operations |
| CacheHeaderTest | Verifies pipeline cache header format |
| InvalidSizeTest | Verifies behavior with invalid cache size |
| ZeroSizeTest | Verifies behavior with zero-size cache |
| InvalidBlobTest | Verifies behavior with invalid cache data |
| InternallySynchronizedTest | Verifies internally synchronized cache access |

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
