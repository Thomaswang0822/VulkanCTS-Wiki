# vktRayTracingShaderBindingTableTests

This registered implementation file registers `shader_binding_table` under `ray_tracing_pipeline`. The group construction is evidenced in [vktRayTracingShaderBindingTableTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L1617-L1621).

## Source Files

| Role | Link |
|------|------|
| Registration and implementation | [vktRayTracingShaderBindingTableTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L1617-L1637) |

## Registration Hierarchy

```text
ray_tracing_pipeline.shader_binding_table
├── handle_alignment
├── indexing_call
├── indexing_hit
└── indexing_miss
```

## Test Families

### shader_binding_table — Registered branch

Shader-binding-table tests cover hit/miss/callable indexing and shader-group handle alignment. The registered group name is created in [vktRayTracingShaderBindingTableTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L1620-L1623). Direct children observed in mustpass/source include `handle_alignment`, `indexing_call`, `indexing_hit`, `indexing_miss`.

## Parameter Dimensions

| Dimension | Observed values | Evidence |
|-----------|-----------------|----------|
| `shader_binding_table` direct children | `handle_alignment`, `indexing_call`, `indexing_hit`, `indexing_miss` | [vktRayTracingShaderBindingTableTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L1620-L1640) |

## Support Requirements

Support checks are implemented by the file's test cases; common ray tracing pipeline tests require `VK_KHR_ray_tracing_pipeline` and, where acceleration structures are used, `VK_KHR_acceleration_structure`, as illustrated by [vktRayTracingBuildTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L186-L205).

## Verification Methods

Verification is implemented in the generated test instances for this file; recurring methods include creating ray tracing pipelines/SBTs and comparing shader-visible outputs, with representative pipeline/SBT setup shown in [vktRayTracingBuildTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L437-L450).

## Test Principles

The file registers focused ray tracing pipeline scenarios and varies only the dimensions visible in its registration loops or child-group construction. Claims above are limited to inspected registration code and mustpass-observed path components.

## Notes

The API test plan provides general CTS framework context but no ray-tracing-pipeline-specific family breakdown in the inspected file.
