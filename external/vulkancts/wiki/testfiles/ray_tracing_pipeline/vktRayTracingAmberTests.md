# vktRayTracingAmberTests

This registered implementation file registers `amber` under `ray_tracing_pipeline`. The group construction is evidenced in [vktRayTracingAmberTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingAmberTests.cpp#L33-L37).

## Source Files

| Role | Link |
|------|------|
| Registration and implementation | [vktRayTracingAmberTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingAmberTests.cpp#L33-L53) |

## Registration Hierarchy

```text
ray_tracing_pipeline.amber
├── barycentrics
├── basic
├── basic2
├── basic_lib
├── different-payload-sizes
├── divergent-as
├── flags-accept-first
├── flags-culling
├── flags-force-non-opaque
├── flags-force-opaque
├── flags-skip-chit
└── rt-sample
```

## Test Families

### amber — Registered branch

Amber-scripted ray tracing cases require ray tracing pipeline, acceleration structure, buffer device address, and selected pipeline-library/deferred-host-operation features declared in the Amber requirement arrays. The registered group name is created in [vktRayTracingAmberTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingAmberTests.cpp#L35-L38). Direct children observed in mustpass/source include `barycentrics`, `basic`, `basic2`, `basic_lib`, `different-payload-sizes`, `divergent-as`, `flags-accept-first`, `flags-culling` and additional direct children.

## Parameter Dimensions

| Dimension | Observed values | Evidence |
|-----------|-----------------|----------|
| `amber` direct children | `barycentrics`, `basic`, `basic2`, `basic_lib`, `different-payload-sizes`, `divergent-as`, `flags-accept-first`, `flags-culling`, `flags-force-non-opaque`, `flags-force-opaque`, `flags-skip-chit`, `rt-sample` | [vktRayTracingAmberTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingAmberTests.cpp#L35-L55) |

## Support Requirements

Amber cases are registered only outside Vulkan SC builds and attach per-script requirement arrays for acceleration structure, buffer device address, ray tracing pipeline, and, for selected scripts, pipeline library or deferred host operations in [vktRayTracingAmberTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingAmberTests.cpp#L37-L60) and [vktRayTracingAmberTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingAmberTests.cpp#L86-L92).

## Verification Methods

The C++ file registers Amber scripts from the `ray_tracing` data directory and attaches requirements; shader execution and result checking are defined by the referenced `.amber` scripts rather than by C++ verification logic in this file [vktRayTracingAmberTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingAmberTests.cpp#L80-L94).

## Test Principles

The file registers focused ray tracing pipeline scenarios and varies only the dimensions visible in its registration loops or child-group construction. Claims above are limited to inspected registration code and mustpass-observed path components.

## Notes
