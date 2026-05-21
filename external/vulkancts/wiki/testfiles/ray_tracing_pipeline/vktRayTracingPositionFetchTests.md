# vktRayTracingPositionFetchTests

This registered implementation file registers `position_fetch` under `ray_tracing_pipeline`. The group construction is evidenced in [vktRayTracingPositionFetchTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingPositionFetchTests.cpp#L529-L533).

## Source Files

| Role | Link |
|------|------|
| Registration and implementation | [vktRayTracingPositionFetchTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingPositionFetchTests.cpp#L529-L549) |

## Registration Hierarchy

```text
ray_tracing_pipeline.position_fetch
├── cpu_built
└── gpu_built
```

## Test Families

### position_fetch — Registered branch

Position-fetch tests vary CPU/GPU build modes, vertex formats, and flag masks for ray pipeline shaders using vertex position fetch. The registered group name is created in [vktRayTracingPositionFetchTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingPositionFetchTests.cpp#L532-L535). Direct children observed in mustpass/source include `cpu_built`, `gpu_built`.

## Parameter Dimensions

| Dimension | Observed values | Evidence |
|-----------|-----------------|----------|
| `position_fetch` direct children | `cpu_built`, `gpu_built` | [vktRayTracingPositionFetchTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingPositionFetchTests.cpp#L532-L552) |

## Support Requirements

Support requires acceleration structure, ray tracing pipeline, and `VK_KHR_ray_tracing_position_fetch`; host-build cases additionally require acceleration-structure host commands, and all cases check the `rayTracingPositionFetch` feature [vktRayTracingPositionFetchTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingPositionFetchTests.cpp#L113-L134).

## Verification Methods

Verification reads the output positions buffer after invalidating host memory and compares it with expected output positions [vktRayTracingPositionFetchTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingPositionFetchTests.cpp#L490-L498).

## Test Principles

The file registers focused ray tracing pipeline scenarios and varies only the dimensions visible in its registration loops or child-group construction. Claims above are limited to inspected registration code and mustpass-observed path components.

## Notes

The API test plan provides general CTS framework context but no ray-tracing-pipeline-specific family breakdown in the inspected file.
