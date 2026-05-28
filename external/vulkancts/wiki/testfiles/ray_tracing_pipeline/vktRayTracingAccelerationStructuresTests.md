# vktRayTracingAccelerationStructuresTests

This registered implementation file registers `acceleration_structures` under `ray_tracing_pipeline`. The group construction is evidenced in [vktRayTracingAccelerationStructuresTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L7738-L7742).

## Source Files

| Role | Link |
|------|------|
| Registration and implementation | [vktRayTracingAccelerationStructuresTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L7738-L7758) |

## Registration Hierarchy

```text
ray_tracing_pipeline.acceleration_structures
├── complex_geometry
├── copy_within_pipeline
├── device_compability_khr
├── dynamic_indexing
├── empty
├── flags
├── format
├── function_argument
├── header_bottom_address
├── host_threading
├── instance_index
├── instance_triangle_culling
├── instance_update
├── operations
├── query_pool_results
├── ray_cull_mask
└── update
```

## Test Families

### acceleration_structures — Registered branch

Acceleration-structure tests cover flags, formats, operations, host threading, function arguments, instance indexing/culling/update, dynamic indexing, empty structures, query results, and pipeline-stage use. The registered group name is created in [vktRayTracingAccelerationStructuresTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L7740-L7743). Direct children observed in mustpass/source include `complex_geometry`, `copy_within_pipeline`, `device_compability_khr`, `dynamic_indexing`, `empty`, `flags`, `format`, `function_argument` and additional direct children.

## Parameter Dimensions

| Dimension | Observed values | Evidence |
|-----------|-----------------|----------|
| `acceleration_structures` direct children | `complex_geometry`, `copy_within_pipeline`, `device_compability_khr`, `dynamic_indexing`, `empty`, `flags`, `format`, `function_argument`, `header_bottom_address`, `host_threading`, `instance_index`, `instance_triangle_culling` ... | [vktRayTracingAccelerationStructuresTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L7740-L7760) |

## Support / Feature Requirements

Support checks are implemented by the file's test cases; common ray tracing pipeline tests require `VK_KHR_ray_tracing_pipeline` and, where acceleration structures are used, `VK_KHR_acceleration_structure`, as illustrated by [vktRayTracingBuildTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L186-L205).

## Verification Methods

Verification is implemented in the generated test instances for this file; recurring methods include creating ray tracing pipelines/SBTs and comparing shader-visible outputs, with representative pipeline/SBT setup shown in [vktRayTracingBuildTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L437-L450).

## Test Principles

The file registers focused ray tracing pipeline scenarios and varies only the dimensions visible in its registration loops or child-group construction. Claims above are limited to inspected registration code and mustpass-observed path components.

## Notes
