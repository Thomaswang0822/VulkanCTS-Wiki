# vktRayTracingBuildIndirectTests

This registered implementation file registers `indirect_acceleration_structure` under `ray_tracing_pipeline`. The group construction is evidenced in [vktRayTracingBuildIndirectTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1254-L1258).

## Source Files

| Role | Link |
|------|------|
| Registration and implementation | [vktRayTracingBuildIndirectTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1254-L1274) |

## Registration Hierarchy

```text
ray_tracing_pipeline.indirect_acceleration_structure
├── build
└── update
```

## Test Families

### indirect_acceleration_structure — Registered branch

Indirect acceleration-structure tests vary build/update mode and indirect count/offset fields for triangles, AABBs, and instances. The registered group name is created in [vktRayTracingBuildIndirectTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1390-L1393). Direct children observed in mustpass/source include `build`, `update`.

## Parameter Dimensions

| Dimension | Observed values | Evidence |
|-----------|-----------------|----------|
| `indirect_acceleration_structure` direct children | `build`, `update` | [vktRayTracingBuildIndirectTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1390-L1410) |

## Support Requirements

Support checks are implemented by the file's test cases; common ray tracing pipeline tests require `VK_KHR_ray_tracing_pipeline` and, where acceleration structures are used, `VK_KHR_acceleration_structure`, as illustrated by [vktRayTracingBuildTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L186-L205).

## Verification Methods

Verification is implemented in the generated test instances for this file; recurring methods include creating ray tracing pipelines/SBTs and comparing shader-visible outputs, with representative pipeline/SBT setup shown in [vktRayTracingBuildTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L437-L450).

## Test Principles

The file registers focused ray tracing pipeline scenarios and varies only the dimensions visible in its registration loops or child-group construction. Claims above are limited to inspected registration code and mustpass-observed path components.

## Notes

The API test plan provides general CTS framework context but no ray-tracing-pipeline-specific family breakdown in the inspected file.
