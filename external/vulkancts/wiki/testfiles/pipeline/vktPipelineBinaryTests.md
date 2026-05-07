# vktPipelineBinaryTests.cpp

## Overview

[`vktPipelineBinaryTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineBinaryTests.cpp#L1) implements the [`pipeline_binary`](../../../modules/vulkan/pipeline/vktPipelineBinaryTests.cpp#L1470) topic group. It verifies VK_KHR_pipeline_binary functionality, testing pipeline binary creation, serialization, and deserialization. Pipeline binaries are an alternative to pipeline caches for storing compiled pipeline data.

## Role

Implementation file. Uses `addPipelineBinaryDedicatedTests()` to add dedicated binary tests to the `pipeline_binary` group created in `vktPipelineTests.cpp`.

## Source Code

- Primary source: [`vktPipelineBinaryTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineBinaryTests.cpp#L1)
- Header: [`vktPipelineBinaryTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineBinaryTests.hpp#L1)

## Registration Path

The `pipeline_binary` group is created in [`vktPipelineTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L152) and populated by [`addPipelineBinaryDedicatedTests()`](../../../modules/vulkan/pipeline/vktPipelineBinaryTests.cpp#L1470), attached under each variant root by `createChildren()`.

**Variant coverage**: Not shader-object, VK only.

## Test Hierarchy

```text
pipeline_binary
└── dedicated
    ├── create_incomplete
    ├── not_enough_space
    ├── destroy_null_binary
    ├── create_from_binary_data
    ├── create_from_binary_key
    ├── create_from_pipeline_cache
    ├── get_binary_data
    ├── get_binary_key
    ├── release_binary_data
    ├── serialized_data_round_trip
    ├── binary_data_with_different_keys
    └── binary_key_with_different_data
```

## Test Families

| Family | Description |
|---|---|
| BaseTestCase | Verifies basic pipeline binary creation and retrieval operations |
| Create incomplete test | Verifies behavior when binary creation is incomplete |
| Not enough space test | Verifies behavior when insufficient space is provided |
| Destroy null binary test | Verifies destroying a null binary handle |
| Create from binary data | Verifies creating a pipeline binary from serialized data |
| Create from binary key | Verifies creating a pipeline binary from a key |
| Create from pipeline cache | Verifies creating a pipeline binary from pipeline cache |
| Get binary data | Verifies retrieving binary data |
| Get binary key | Verifies retrieving binary key |
| Release binary data | Verifies releasing binary data |
| Serialized data round trip | Verifies serialization and deserialization round trip |

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

- The `pipeline_binary` group aggregates binary, creation feedback, and dedicated tests
- Pipeline binary tests are excluded from shader-object variants
