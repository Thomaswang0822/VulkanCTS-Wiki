# vktRayTracingInvocationReorderActivityTests

This registered implementation file registers `rtir_activity` under `ray_tracing_pipeline`. The group construction is evidenced in [vktRayTracingInvocationReorderActivityTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingInvocationReorderActivityTests.cpp#L634-L638).

## Source Files

| Role | Link |
|------|------|
| Registration and implementation | [vktRayTracingInvocationReorderActivityTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingInvocationReorderActivityTests.cpp#L634-L654) |

## Registration Hierarchy

```text
ray_tracing_pipeline.rtir_activity
└── activity
```

## Test Families

### rtir_activity — Registered branch

RTIR activity tests register a single activity case for invocation reorder activity with ray pipelines. The registered group name is created in [vktRayTracingInvocationReorderActivityTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingInvocationReorderActivityTests.cpp#L637-L640). Direct children observed in mustpass/source include `activity`.

## Parameter Dimensions

| Dimension | Observed values | Evidence |
|-----------|-----------------|----------|
| `rtir_activity` direct children | `activity` | [vktRayTracingInvocationReorderActivityTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingInvocationReorderActivityTests.cpp#L637-L657) |

## Support Requirements

Support requires deferred host operations, acceleration structure, ray tracing pipeline, buffer device address, and `VK_EXT_ray_tracing_invocation_reorder`, then checks the buffer-device-address, ray-tracing-pipeline, acceleration-structure, and invocation-reorder feature bits [vktRayTracingInvocationReorderActivityTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingInvocationReorderActivityTests.cpp#L96-L126).

## Verification Methods

Verification reads the output modes buffer after invalidating host memory and checks per-pixel activity output values [vktRayTracingInvocationReorderActivityTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingInvocationReorderActivityTests.cpp#L591-L600).

## Test Principles

The file registers focused ray tracing pipeline scenarios and varies only the dimensions visible in its registration loops or child-group construction. Claims above are limited to inspected registration code and mustpass-observed path components.

## Notes
