# vktRayTracingCaptureReplayTests

This registered implementation file registers `capture_replay` under `ray_tracing_pipeline`. The group construction is evidenced in [vktRayTracingCaptureReplayTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L1729-L1733).

## Source Files

| Role | Link |
|------|------|
| Registration and implementation | [vktRayTracingCaptureReplayTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L1729-L1749) |

## Registration Hierarchy

```text
ray_tracing_pipeline.capture_replay
├── acceleration_structures
└── shader_binding_tables
```

## Test Families

### capture_replay — Registered branch

Capture-replay tests cover shader-binding-table and acceleration-structure capture/replay configurations. The registered group name is created in [vktRayTracingCaptureReplayTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L1731-L1734). Direct children observed in mustpass/source include `acceleration_structures`, `shader_binding_tables`.

## Parameter Dimensions

| Dimension | Observed values | Evidence |
|-----------|-----------------|----------|
| `capture_replay` direct children | `acceleration_structures`, `shader_binding_tables` | [vktRayTracingCaptureReplayTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L1731-L1751) |

## Support Requirements

Support checks are implemented by the file's test cases; common ray tracing pipeline tests require `VK_KHR_ray_tracing_pipeline` and, where acceleration structures are used, `VK_KHR_acceleration_structure`, as illustrated by [vktRayTracingBuildTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L186-L205).

## Verification Methods

Verification is implemented in the generated test instances for this file; recurring methods include creating ray tracing pipelines/SBTs and comparing shader-visible outputs, with representative pipeline/SBT setup shown in [vktRayTracingBuildTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L437-L450).

## Test Principles

The file registers focused ray tracing pipeline scenarios and varies only the dimensions visible in its registration loops or child-group construction. Claims above are limited to inspected registration code and mustpass-observed path components.

## Notes
