# vktRayTracingCallableShadersTests

This registered implementation file registers `callable_shader` under `ray_tracing_pipeline`. The group construction is evidenced in [vktRayTracingCallableShadersTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L1975-L1979).

## Source Files

| Role | Link |
|------|------|
| Registration and implementation | [vktRayTracingCallableShadersTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L1975-L1995) |

## Registration Hierarchy

```text
ray_tracing_pipeline.callable_shader
├── callable_shader_invoked_via_callable_multiple_invocations
├── callable_shader_invoked_via_callable_single_invocation
├── callable_shader_invoked_via_closest_hit_multiple_invocations
├── callable_shader_invoked_via_closest_hit_single_invocation
├── callable_shader_invoked_via_miss_multiple_invocations
├── callable_shader_invoked_via_miss_single_invocation
├── callable_shader_invoked_via_raygen_multiple_invocations
├── callable_shader_invoked_via_raygen_single_invocation
├── hit_call
├── rgen_call
├── rgen_call_call
└── rgen_multicall
```

## Test Families

### callable_shader — Registered branch

Callable-shader tests cover callable invocation through raygen, miss, closest-hit, and callable stages, including single and multiple invocations. The registered group name is created in [vktRayTracingCallableShadersTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L1978-L1981). Direct children observed in mustpass/source include `callable_shader_invoked_via_callable_multiple_invocations`, `callable_shader_invoked_via_callable_single_invocation`, `callable_shader_invoked_via_closest_hit_multiple_invocations`, `callable_shader_invoked_via_closest_hit_single_invocation`, `callable_shader_invoked_via_miss_multiple_invocations`, `callable_shader_invoked_via_miss_single_invocation`, `callable_shader_invoked_via_raygen_multiple_invocations`, `callable_shader_invoked_via_raygen_single_invocation` and additional direct children.

## Parameter Dimensions

| Dimension | Observed values | Evidence |
|-----------|-----------------|----------|
| `callable_shader` direct children | `callable_shader_invoked_via_callable_multiple_invocations`, `callable_shader_invoked_via_callable_single_invocation`, `callable_shader_invoked_via_closest_hit_multiple_invocations`, `callable_shader_invoked_via_closest_hit_single_invocation`, `callable_shader_invoked_via_miss_multiple_invocations`, `callable_shader_invoked_via_miss_single_invocation`, `callable_shader_invoked_via_raygen_multiple_invocations`, `callable_shader_invoked_via_raygen_single_invocation`, `hit_call`, `rgen_call`, `rgen_call_call`, `rgen_multicall` | [vktRayTracingCallableShadersTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L1978-L1998) |

## Support / Feature Requirements

Support checks are implemented by the file's test cases; common ray tracing pipeline tests require `VK_KHR_ray_tracing_pipeline` and, where acceleration structures are used, `VK_KHR_acceleration_structure`, as illustrated by [vktRayTracingBuildTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L186-L205).

## Verification Methods

Verification is implemented in the generated test instances for this file; recurring methods include creating ray tracing pipelines/SBTs and comparing shader-visible outputs, with representative pipeline/SBT setup shown in [vktRayTracingBuildTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L437-L450).

## Test Principles

The file registers focused ray tracing pipeline scenarios and varies only the dimensions visible in its registration loops or child-group construction. Claims above are limited to inspected registration code and mustpass-observed path components.

## Notes
