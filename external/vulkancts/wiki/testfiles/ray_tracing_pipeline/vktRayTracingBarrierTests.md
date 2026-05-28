# vktRayTracingBarrierTests

This registered implementation file registers `barrier` under `ray_tracing_pipeline`. The group construction is evidenced in [vktRayTracingBarrierTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBarrierTests.cpp#L1750-L1754).

## Source Files

| Role | Link |
|------|------|
| Registration and implementation | [vktRayTracingBarrierTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBarrierTests.cpp#L1750-L1770) |

## Registration Hierarchy

```text
ray_tracing_pipeline.barrier
├── simg
├── ssbo
└── ubo
```

## Test Families

### barrier — Registered branch

Barrier tests cross resource types, barrier types, and writer/reader stages involving ray tracing stages. The registered group name is created in [vktRayTracingBarrierTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBarrierTests.cpp#L1753-L1756). Direct children observed in mustpass/source include `simg`, `ssbo`, `ubo`.

## Parameter Dimensions

| Dimension | Observed values | Evidence |
|-----------|-----------------|----------|
| `barrier` direct children | `simg`, `ssbo`, `ubo` | [vktRayTracingBarrierTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBarrierTests.cpp#L1753-L1773) |

## Support / Feature Requirements

Support checks are implemented by the file's test cases; common ray tracing pipeline tests require `VK_KHR_ray_tracing_pipeline` and, where acceleration structures are used, `VK_KHR_acceleration_structure`, as illustrated by [vktRayTracingBuildTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L186-L205).

## Verification Methods

Verification is implemented in the generated test instances for this file; recurring methods include creating ray tracing pipelines/SBTs and comparing shader-visible outputs, with representative pipeline/SBT setup shown in [vktRayTracingBuildTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L437-L450).

## Test Principles

The file registers focused ray tracing pipeline scenarios and varies only the dimensions visible in its registration loops or child-group construction. Claims above are limited to inspected registration code and mustpass-observed path components.

## Notes
