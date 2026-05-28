# vktRayTracingProceduralGeometryTests

This registered implementation file registers `procedural_geometry` under `ray_tracing_pipeline`. The group construction is evidenced in [vktRayTracingProceduralGeometryTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingProceduralGeometryTests.cpp#L611-L615).

## Source Files

| Role | Link |
|------|------|
| Registration and implementation | [vktRayTracingProceduralGeometryTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingProceduralGeometryTests.cpp#L611-L631) |

## Registration Hierarchy

```text
ray_tracing_pipeline.procedural_geometry
├── object_behind_bounding_boxes
└── triangle_in_between
```

## Test Families

### procedural_geometry — Registered branch

Procedural-geometry tests register explicit AABB arrangements for objects behind bounding boxes and triangles between boxes. The registered group name is created in [vktRayTracingProceduralGeometryTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingProceduralGeometryTests.cpp#L614-L617). Direct children observed in mustpass/source include `object_behind_bounding_boxes`, `triangle_in_between`.

## Parameter Dimensions

| Dimension | Observed values | Evidence |
|-----------|-----------------|----------|
| `procedural_geometry` direct children | `object_behind_bounding_boxes`, `triangle_in_between` | [vktRayTracingProceduralGeometryTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingProceduralGeometryTests.cpp#L614-L634) |

## Support / Feature Requirements

Support checks are implemented by the file's test cases; common ray tracing pipeline tests require `VK_KHR_ray_tracing_pipeline` and, where acceleration structures are used, `VK_KHR_acceleration_structure`, as illustrated by [vktRayTracingBuildTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L186-L205).

## Verification Methods

Verification is implemented in the generated test instances for this file; recurring methods include creating ray tracing pipelines/SBTs and comparing shader-visible outputs, with representative pipeline/SBT setup shown in [vktRayTracingBuildTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L437-L450).

## Test Principles

The file registers focused ray tracing pipeline scenarios and varies only the dimensions visible in its registration loops or child-group construction. Claims above are limited to inspected registration code and mustpass-observed path components.

## Notes
