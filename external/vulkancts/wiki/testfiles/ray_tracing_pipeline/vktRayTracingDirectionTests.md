# vktRayTracingDirectionTests

This registered implementation file with multiple root groups registers `direction_length`, `inside_aabbs` under `ray_tracing_pipeline`. The group construction is evidenced in [vktRayTracingDirectionTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingDirectionTests.cpp#L681-L685).

## Source Files

| Role | Link |
|------|------|
| Registration and implementation | [vktRayTracingDirectionTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingDirectionTests.cpp#L681-L701) |

## Registration Hierarchy

```text
ray_tracing_pipeline
├── direction_length
└── inside_aabbs
```

## Test Families

### direction_length — Registered branch

Direction-length tests vary hit/intersection stages, geometry, scaling factors, and rotation angles. The registered group name is created in [vktRayTracingDirectionTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingDirectionTests.cpp#L684-L687). Direct children observed in mustpass/source include `ahit`, `chit`, `isec`.

### inside_aabbs — Registered branch

Inside-AABB tests vary stages, ray-end choices, scaling factors, and rotation angles for rays starting inside AABBs. The registered group name is created in [vktRayTracingDirectionTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingDirectionTests.cpp#L778-L781). Direct children observed in mustpass/source include `ahit`, `chit`, `isec`.

## Parameter Dimensions

| Dimension | Observed values | Evidence |
|-----------|-----------------|----------|
| `direction_length` direct children | `ahit`, `chit`, `isec` | [vktRayTracingDirectionTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingDirectionTests.cpp#L684-L704) |
| `inside_aabbs` direct children | `ahit`, `chit`, `isec` | [vktRayTracingDirectionTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingDirectionTests.cpp#L778-L798) |

## Support Requirements

Support checks are implemented by the file's test cases; common ray tracing pipeline tests require `VK_KHR_ray_tracing_pipeline` and, where acceleration structures are used, `VK_KHR_acceleration_structure`, as illustrated by [vktRayTracingBuildTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L186-L205).

## Verification Methods

Verification is implemented in the generated test instances for this file; recurring methods include creating ray tracing pipelines/SBTs and comparing shader-visible outputs, with representative pipeline/SBT setup shown in [vktRayTracingBuildTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L437-L450).

## Test Principles

The file registers focused ray tracing pipeline scenarios and varies only the dimensions visible in its registration loops or child-group construction. Claims above are limited to inspected registration code and mustpass-observed path components.

## Notes
