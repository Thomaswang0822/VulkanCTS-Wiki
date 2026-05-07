# vktPipelineRobustnessCacheTests.cpp

## Overview

[`vktPipelineRobustnessCacheTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineRobustnessCacheTests.cpp#L1) implements the [`pipeline_cache`](../../../modules/vulkan/pipeline/vktPipelineRobustnessCacheTests.cpp#L817) topic group. It verifies pipeline cache robustness with VK_EXT_pipeline_robustness, testing that pipelines with robustness properties interact correctly with pipeline caches.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineRobustnessCacheTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineRobustnessCacheTests.cpp#L1)
- Header: [`vktPipelineRobustnessCacheTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineRobustnessCacheTests.hpp#L1)

## Registration Path

[`createRobustnessCacheTests()`](../../../modules/vulkan/pipeline/vktPipelineRobustnessCacheTests.cpp#L1) returns the `pipeline_cache` group, attached under each variant root by `createChildren()`.

**Variant coverage**: Not shader-object, VK only.

## Test Hierarchy

```text
pipeline_cache
└── robustness
    └── {pipeline_type}
        └── {robustness_test}
```

## Test Families

| Family | Description |
|---|---|
| PipelineCacheTestCase | Verifies pipeline cache behavior with robustness properties |

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| PipelineConstructionType | Parameter | Non-shader-object variant types |
| Pipeline type | Enum | Graphics, compute |
| Robustness feature | Enum | Buffer access, image access |

## Support/Feature Requirements

| Requirement | Context |
|---|---|
| `VK_EXT_pipeline_robustness` | Primary extension for all tests |
| `VK_KHR_robustness2` or `VK_EXT_robustness2` | Required as alternative robustness support |

## Verification Methods

- **Cache consistency verification**: Verify that pipelines with robustness properties produce consistent cache entries
- **Robustness behavior verification**: Verify that robustness properties are correctly applied after cache retrieval

## Notes

- The group name `pipeline_cache` is used for robustness-cache interaction tests, distinct from the `cache` group in `vktPipelineCacheTests.cpp`
- Excluded from shader-object variants
- VK only (guarded by `CTS_USES_VULKANSC` exclusion)
