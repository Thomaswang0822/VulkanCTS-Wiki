# vktPipelineBinaryTests.cpp

## Overview

[`vktPipelineBinaryTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineBinaryTests.cpp#L1) implements the [`pipeline_binary`](../../../modules/vulkan/pipeline/vktPipelineBinaryTests.cpp#L1470) topic group. It verifies VK_KHR_pipeline_binary functionality, testing pipeline binary creation, serialization, and deserialization. Pipeline binaries are an alternative to pipeline caches for storing compiled pipeline data.

## Role

Implementation file. Uses `addPipelineBinaryDedicatedTests()` to add dedicated binary tests to the `pipeline_binary` group created in `vktPipelineTests.cpp`.

## Source Code

- Primary source: [`vktPipelineBinaryTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineBinaryTests.cpp#L1)
- Header: [`vktPipelineBinaryTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineBinaryTests.hpp#L1)
- Basic tests source: [`vktPipelineCacheTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineCacheTests.cpp#L1)
- Creation feedback source: [`vktPipelineCreationFeedbackTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineCreationFeedbackTests.cpp#L1)

## Registration Hierarchy

The `pipeline_binary` group is created in [`vktPipelineTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L152) and populated by three functions: `addPipelineBinaryBasicTests()`, `addPipelineBinaryCreationFeedbackTests()`, and `addPipelineBinaryDedicatedTests()`, attached under each variant root by `createChildren()`.

**Variant coverage**: Not shader-object, VK only.

```text
pipeline.monolithic.pipeline_binary
├── graphics_tests
├── pipeline_from_get_data
├── compute_tests (monolithic only)
├── creation_feedback
└── dedicated
```

## Test Families

### graphics_tests — Graphics pipeline binary tests

Basic graphics pipeline binary round-trip tests. Creates a graphics pipeline with various shader stage combinations (vert+frag, vert+geom+frag, vert+tess+frag), serializes the binary, deserializes, and verifies pipeline creation succeeds. Implemented in [`vktPipelineCacheTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineCacheTests.cpp#L2299) via `createPipelineBlobTestsInternal()` with `TestMode::BINARY`.

### pipeline_from_get_data — Pipeline from retrieved binary data

Tests creating a pipeline from previously retrieved binary data. Uses `PipelineFromBlobsTest` instances with vert+frag, vert+geom+frag, and vert+tess+frag stage combinations. Implemented in [`vktPipelineCacheTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineCacheTests.cpp#L2327) via `createPipelineBlobTestsInternal()` with `TestMode::BINARY`.

### compute_tests — Compute pipeline binary tests (monolithic only)

Compute pipeline binary round-trip tests. Only added for `PIPELINE_CONSTRUCTION_TYPE_MONOLITHIC`. Includes tests with and without zero binary count. Implemented in [`vktPipelineCacheTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineCacheTests.cpp#L2362) via `createPipelineBlobTestsInternal()` with `TestMode::BINARY`.

### creation_feedback — Pipeline binary creation feedback tests

Tests pipeline creation feedback combined with pipeline binary functionality. Contains `graphics_tests` and `compute_tests` (monolithic only) sub-groups that exercise creation feedback with binary mode. Implemented in [`vktPipelineCreationFeedbackTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineCreationFeedbackTests.cpp#L1513) via `addPipelineBinaryCreationFeedbackTests()`.

### dedicated — Dedicated pipeline binary tests

Tests specific to pipeline binary operations that do not overlap with cache or creation-feedback tests. Implemented in [`vktPipelineBinaryTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineBinaryTests.cpp#L1470) via `addPipelineBinaryDedicatedTests()`.

Always-present leaf tests:
- `unique_key_pairs` — Verifies that different pipelines produce unique binary key pairs
- `graphics_pipeline_from_internal_cache` — Verifies graphics pipeline binary creation from internal cache
- `valid_key` — Verifies that binary keys are valid

Monolithic-only leaf tests:
- `create_incomplete` — Verifies behavior when binary creation is incomplete
- `not_enough_space` — Verifies behavior when insufficient space is provided
- `destroy_null_binary` — Verifies destroying a null binary handle
- `compute_pipeline_with_zero_binary_count` — Verifies compute pipeline with zero binary count
- `compute_pipeline_from_internal_cache` — Verifies compute pipeline binary from internal cache
- `graphics_pipeline_with_zero_binary_count` — Verifies graphics pipeline with zero binary count
- `ray_tracing_pipeline_from_internal_cache` — Verifies ray tracing pipeline binary from internal cache
- `ray_tracing_pipeline_from_pipeline` — Verifies ray tracing pipeline binary from pipeline
- `ray_tracing_pipeline_from_binary_data` — Verifies ray tracing pipeline binary from serialized data
- `ray_tracing_pipeline_library_from_internal_cache` — Verifies ray tracing pipeline library binary from internal cache
- `ray_tracing_pipeline_library_from_pipeline` — Verifies ray tracing pipeline library binary from pipeline
- `ray_tracing_pipeline_library_from_binary_data` — Verifies ray tracing pipeline library binary from serialized data
- `ray_tracing_pipeline_with_zero_binary_count` — Verifies ray tracing pipeline with zero binary count

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| PipelineConstructionType | Parameter | Non-shader-object variant types |
| Binary creation method | Enum | From data, from key, from cache |

## Support/Feature Requirements

| Requirement | Context |
|---|---|
| `VK_KHR_pipeline_binary` | Primary extension for all tests |
| `VK_KHR_acceleration_structure` | Required for ray tracing binary tests |
| `VK_KHR_ray_tracing_pipeline` | Required for ray tracing binary tests |
| `VK_KHR_pipeline_library` | Required for ray tracing binary tests |
| `VK_KHR_maintenance8` | Required for some maintenance8-related tests |
| `geometryShader` | Required for geometry shader binary tests |
| `tessellationShader` | Required for tessellation shader binary tests |

## Verification Methods

- **Binary round trip**: Create pipeline, serialize binary, deserialize, verify pipeline creation succeeds
- **Key/data consistency**: Verify that binary keys and data are consistent across operations
- **Error handling**: Verify appropriate errors for invalid binary operations

## Notes

- The `pipeline_binary` group aggregates basic (from cache tests), creation feedback, and dedicated tests
- Pipeline binary tests are excluded from shader-object variants
