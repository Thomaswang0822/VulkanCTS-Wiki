# vktRayTracingBarycentricCoordinatesTests

This registered implementation file registers `barycentric_coordinates` under `ray_tracing_pipeline`. The group construction is evidenced in [vktRayTracingBarycentricCoordinatesTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBarycentricCoordinatesTests.cpp#L498-L502).

## Source Files

| Role | Link |
|------|------|
| Registration and implementation | [vktRayTracingBarycentricCoordinatesTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBarycentricCoordinatesTests.cpp#L498-L518) |

## Registration Hierarchy

```text
ray_tracing_pipeline.barycentric_coordinates
├── ahit
├── ahitTerminate
└── chit
```

## Test Families

### barycentric_coordinates — Registered branch

Barycentric-coordinate tests register closest-hit, any-hit, and terminating any-hit cases with deterministic seeds. The registered group name is created in [vktRayTracingBarycentricCoordinatesTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBarycentricCoordinatesTests.cpp#L503-L506). Direct children observed in mustpass/source include `ahit`, `ahitTerminate`, `chit`.

## Parameter Dimensions

| Dimension | Observed values | Evidence |
|-----------|-----------------|----------|
| `barycentric_coordinates` direct children | `ahit`, `ahitTerminate`, `chit` | [vktRayTracingBarycentricCoordinatesTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBarycentricCoordinatesTests.cpp#L503-L523) |

## Support / Feature Requirements

Support checks are implemented by the file's test cases; common ray tracing pipeline tests require `VK_KHR_ray_tracing_pipeline` and, where acceleration structures are used, `VK_KHR_acceleration_structure`, as illustrated by [vktRayTracingBuildTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L186-L205).

## Verification Methods

Verification is implemented in the generated test instances for this file; recurring methods include creating ray tracing pipelines/SBTs and comparing shader-visible outputs, with representative pipeline/SBT setup shown in [vktRayTracingBuildTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L437-L450).

## Test Principles

The file registers focused ray tracing pipeline scenarios and varies only the dimensions visible in its registration loops or child-group construction. Claims above are limited to inspected registration code and mustpass-observed path components.

## Notes
