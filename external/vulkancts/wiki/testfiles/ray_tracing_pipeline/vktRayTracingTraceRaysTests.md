# vktRayTracingTraceRaysTests

This registered implementation file with multiple root groups registers `trace_rays_cmds`, `trace_rays_cmds_maintenance_1`, `trace_rays_indirect2` under `ray_tracing_pipeline`. The group construction is evidenced in [vktRayTracingTraceRaysTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L1459-L1463).

## Source Files

| Role | Link |
|------|------|
| Registration and implementation | [vktRayTracingTraceRaysTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L1459-L1479) |

## Registration Hierarchy

```text
ray_tracing_pipeline
├── trace_rays_cmds
├── trace_rays_cmds_maintenance_1
└── trace_rays_indirect2
```

## Test Families

### trace_rays_cmds — Registered branch

Trace-rays command tests cover direct and indirect CPU/GPU buffer-source paths for `vkCmdTraceRays*` style dispatch. The registered group name is created in [vktRayTracingTraceRaysTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L1462-L1465). Direct children observed in mustpass/source include `direct`, `indirect_cpu`, `indirect_gpu`.

### trace_rays_cmds_maintenance_1 — Registered branch

Maintenance1 trace-rays command tests cover indirect2 CPU and GPU buffer-source paths. The registered group name is created in [vktRayTracingTraceRaysTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L1507-L1510). Direct children observed in mustpass/source include `indirect2_cpu`, `indirect2_gpu`.

### trace_rays_indirect2 — Registered branch

Indirect2 trace-rays tests vary indirect CPU/GPU buffer source, copy style, queue submission path, and dimensions. The registered group name is created in [vktRayTracingTraceRaysTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L1553-L1556). Direct children observed in mustpass/source include `indirect_cpu`, `indirect_gpu`.

## Parameter Dimensions

| Dimension | Observed values | Evidence |
|-----------|-----------------|----------|
| `trace_rays_cmds` direct children | `direct`, `indirect_cpu`, `indirect_gpu` | [vktRayTracingTraceRaysTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L1462-L1482) |
| `trace_rays_cmds_maintenance_1` direct children | `indirect2_cpu`, `indirect2_gpu` | [vktRayTracingTraceRaysTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L1507-L1527) |
| `trace_rays_indirect2` direct children | `indirect_cpu`, `indirect_gpu` | [vktRayTracingTraceRaysTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L1553-L1573) |

## Support Requirements

Trace-rays indirect support requires acceleration structure and ray tracing pipeline, checks `rayTracingPipelineTraceRaysIndirect`, and conditionally requires ray-tracing maintenance1/indirect2 features for maintenance1 paths [vktRayTracingTraceRaysTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L254-L283). The separate indirect2 cases require acceleration structure, ray-tracing maintenance1, indirect2 support, and the requested queue family [vktRayTracingTraceRaysTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L898-L927).

## Verification Methods

Verification checks each output pixel against clear, hit, or miss color values and fails with a failure count when mismatches are found [vktRayTracingTraceRaysTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L827-L842).

## Test Principles

The file registers focused ray tracing pipeline scenarios and varies only the dimensions visible in its registration loops or child-group construction. Claims above are limited to inspected registration code and mustpass-observed path components.

## Notes
