# vktRayTracingWatertightnessTests

This registered implementation file registers `watertightness` under `ray_tracing_pipeline`. The group construction is evidenced in [vktRayTracingWatertightnessTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingWatertightnessTests.cpp#L872-L876).

## Source Files

| Role | Link |
|------|------|
| Registration and implementation | [vktRayTracingWatertightnessTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingWatertightnessTests.cpp#L872-L892) |

## Registration Hierarchy

```text
ray_tracing_pipeline.watertightness
├── 0
├── 1
├── 2
├── 3
├── 4
├── 5
├── 6
├── 7
├── 8
├── 9
├── closedFan
└── closedFan2
```

## Test Families

### watertightness — Registered branch

Watertightness tests generate fan and closed-fan triangle arrangements and check no-miss/single-hit consistency. The registered group name is created in [vktRayTracingWatertightnessTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingWatertightnessTests.cpp#L875-L878). Direct children observed in mustpass/source include `0`, `1`, `2`, `3`, `4`, `5`, `6`, `7` and additional direct children.

## Parameter Dimensions

| Dimension | Observed values | Evidence |
|-----------|-----------------|----------|
| `watertightness` direct children | `0`, `1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`, `9`, `closedFan`, `closedFan2` | [vktRayTracingWatertightnessTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingWatertightnessTests.cpp#L875-L895) |

## Support Requirements

Support checks are implemented by the file's test cases; common ray tracing pipeline tests require `VK_KHR_ray_tracing_pipeline` and, where acceleration structures are used, `VK_KHR_acceleration_structure`, as illustrated by [vktRayTracingBuildTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L186-L205).

## Verification Methods

Verification is implemented in the generated test instances for this file; recurring methods include creating ray tracing pipelines/SBTs and comparing shader-visible outputs, with representative pipeline/SBT setup shown in [vktRayTracingBuildTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L437-L450).

## Test Principles

The file registers focused ray tracing pipeline scenarios and varies only the dimensions visible in its registration loops or child-group construction. Claims above are limited to inspected registration code and mustpass-observed path components.

## Notes

The API test plan provides general CTS framework context but no ray-tracing-pipeline-specific family breakdown in the inspected file.
