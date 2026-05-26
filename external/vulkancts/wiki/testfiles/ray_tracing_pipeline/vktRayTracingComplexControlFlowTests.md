# vktRayTracingComplexControlFlowTests

This registered implementation file registers `complexcontrolflow` under `ray_tracing_pipeline`. The group construction is evidenced in [vktRayTracingComplexControlFlowTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L1797-L1801).

## Source Files

| Role | Link |
|------|------|
| Registration and implementation | [vktRayTracingComplexControlFlowTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L1797-L1817) |

## Registration Hierarchy

```text
ray_tracing_pipeline.complexcontrolflow
├── function_call
├── if
├── loop
├── loop_double_call
├── loop_double_call_sparse
├── nested_function_call
├── nested_loop
├── nested_loop_loop_after
├── nested_loop_loop_before
└── switch
```

## Test Families

### complexcontrolflow — Registered branch

Complex-control-flow tests cover conditionals, switches, loops, nested loops, and function-call patterns around ray tracing shader calls. The registered group name is created in [vktRayTracingComplexControlFlowTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L1845-L1848). Direct children observed in mustpass/source include `function_call`, `if`, `loop`, `loop_double_call`, `loop_double_call_sparse`, `nested_function_call`, `nested_loop`, `nested_loop_loop_after` and additional direct children.

## Parameter Dimensions

| Dimension | Observed values | Evidence |
|-----------|-----------------|----------|
| `complexcontrolflow` direct children | `function_call`, `if`, `loop`, `loop_double_call`, `loop_double_call_sparse`, `nested_function_call`, `nested_loop`, `nested_loop_loop_after`, `nested_loop_loop_before`, `switch` | [vktRayTracingComplexControlFlowTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L1845-L1865) |

## Support Requirements

Support checks are implemented by the file's test cases; common ray tracing pipeline tests require `VK_KHR_ray_tracing_pipeline` and, where acceleration structures are used, `VK_KHR_acceleration_structure`, as illustrated by [vktRayTracingBuildTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L186-L205).

## Verification Methods

Verification is implemented in the generated test instances for this file; recurring methods include creating ray tracing pipelines/SBTs and comparing shader-visible outputs, with representative pipeline/SBT setup shown in [vktRayTracingBuildTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L437-L450).

## Test Principles

The file registers focused ray tracing pipeline scenarios and varies only the dimensions visible in its registration loops or child-group construction. Claims above are limited to inspected registration code and mustpass-observed path components.

## Notes
