# vktRayTracingBuildTests

This registered implementation file registers `build` under `ray_tracing_pipeline`. The group construction is evidenced in [vktRayTracingBuildTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L753-L757).

## Source Files

| Role | Link |
|------|------|
| Registration and implementation | [vktRayTracingBuildTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L753-L773) |

## Registration Hierarchy

```text
ray_tracing_pipeline.build
├── cpu
├── cpuht_1
├── cpuht_2
├── cpuht_3
├── cpuht_4
├── cpuht_8
├── cpuht_max
└── gpu
```

## Test Families

### build — Registered branch

Build tests compare ray tracing results when acceleration structures are built on GPU, CPU, and CPU host-threaded paths. The registered group name is created in [vktRayTracingBuildTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L756-L759). Direct children observed in mustpass/source include `cpu`, `cpuht_1`, `cpuht_2`, `cpuht_3`, `cpuht_4`, `cpuht_8`, `cpuht_max`, `gpu`.

## Parameter Dimensions

| Dimension | Observed values | Evidence |
|-----------|-----------------|----------|
| `build` direct children | `cpu`, `cpuht_1`, `cpuht_2`, `cpuht_3`, `cpuht_4`, `cpuht_8`, `cpuht_max`, `gpu` | [vktRayTracingBuildTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L756-L776) |

## Support Requirements

Support is checked in this file; observed gates include ray tracing pipeline and related feature/extension checks at [vktRayTracingBuildTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L186-L205).

## Verification Methods

The inspected implementation creates ray tracing shaders, pipeline, and shader binding tables before dispatching and checking results in [vktRayTracingBuildTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L437-L450).

## Test Principles

The file registers focused ray tracing pipeline scenarios and varies only the dimensions visible in its registration loops or child-group construction. Claims above are limited to inspected registration code and mustpass-observed path components.

## Notes

The API test plan provides general CTS framework context but no ray-tracing-pipeline-specific family breakdown in the inspected file.
