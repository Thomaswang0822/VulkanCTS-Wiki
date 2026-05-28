# vktRayTracingBuildLargeTests

This registered implementation file registers `large_shader_set` under `ray_tracing_pipeline`. The group construction is evidenced in [vktRayTracingBuildLargeTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L571-L575).

## Source Files

| Role | Link |
|------|------|
| Registration and implementation | [vktRayTracingBuildLargeTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L571-L591) |

## Registration Hierarchy

```text
ray_tracing_pipeline.large_shader_set
├── cpu_ht
├── cpu_ht_1
├── cpu_ht_2
├── cpu_ht_3
├── cpu_ht_4
├── cpu_ht_8
├── cpu_ht_max
└── gpu
```

## Test Families

### large_shader_set — Registered branch

Large shader-set tests vary GPU and host-threaded CPU build modes and square sizes to exercise many callable groups. The registered group name is created in [vktRayTracingBuildLargeTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L574-L577). Direct children observed in mustpass/source include `cpu_ht`, `cpu_ht_1`, `cpu_ht_2`, `cpu_ht_3`, `cpu_ht_4`, `cpu_ht_8`, `cpu_ht_max`, `gpu`.

## Parameter Dimensions

| Dimension | Observed values | Evidence |
|-----------|-----------------|----------|
| `large_shader_set` direct children | `cpu_ht`, `cpu_ht_1`, `cpu_ht_2`, `cpu_ht_3`, `cpu_ht_4`, `cpu_ht_8`, `cpu_ht_max`, `gpu` | [vktRayTracingBuildLargeTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L574-L594) |

## Support / Feature Requirements

Support is checked in this file; observed gates include ray tracing pipeline and related feature/extension checks at [vktRayTracingBuildLargeTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L191-L205).

## Verification Methods

The inspected implementation creates a large ray tracing pipeline while watchdog timing is managed, then creates the SBT in [vktRayTracingBuildLargeTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L385-L395).

## Test Principles

The file registers focused ray tracing pipeline scenarios and varies only the dimensions visible in its registration loops or child-group construction. Claims above are limited to inspected registration code and mustpass-observed path components.

## Notes
