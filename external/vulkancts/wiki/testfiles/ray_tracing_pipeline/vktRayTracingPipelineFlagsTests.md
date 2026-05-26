# vktRayTracingPipelineFlagsTests

This registered implementation file registers `pipeline_no_null_shaders_flag` under `ray_tracing_pipeline`. The group construction is evidenced in [vktRayTracingPipelineFlagsTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L1528-L1532).

## Source Files

| Role | Link |
|------|------|
| Registration and implementation | [vktRayTracingPipelineFlagsTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L1528-L1548) |

## Registration Hierarchy

```text
ray_tracing_pipeline.pipeline_no_null_shaders_flag
├── cpu
├── gpu
└── misc
```

## Test Families

### pipeline_no_null_shaders_flag — Registered branch

Pipeline flag tests exercise `VK_PIPELINE_CREATE_RAY_TRACING_NO_NULL_*_SHADERS_BIT_KHR` combinations over CPU/GPU processors, geometry, stride, offset, and library mode. The registered group name is created in [vktRayTracingPipelineFlagsTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L1573-L1576). Direct children observed in mustpass/source include `cpu`, `gpu`, `misc`.

## Parameter Dimensions

| Dimension | Observed values | Evidence |
|-----------|-----------------|----------|
| `pipeline_no_null_shaders_flag` direct children | `cpu`, `gpu`, `misc` | [vktRayTracingPipelineFlagsTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L1573-L1593) |

## Support Requirements

Support checks reject illegal triangle/intersection-flag combinations, require ray tracing pipeline with acceleration structure and buffer device address consistency, conditionally require maintenance5, and require acceleration-structure host commands for host-build cases [vktRayTracingPipelineFlagsTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L578-L616).

## Verification Methods

Verification builds expected geometry-dependent output and compares the result image in `verifyResult()` [vktRayTracingPipelineFlagsTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L1203-L1215).

## Test Principles

The file registers focused ray tracing pipeline scenarios and varies only the dimensions visible in its registration loops or child-group construction. Claims above are limited to inspected registration code and mustpass-observed path components.

## Notes
