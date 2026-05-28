# vktRayTracingMemGuaranteeTests

This registered implementation file registers `memguarantee` under `ray_tracing_pipeline`. The group construction is evidenced in [vktRayTracingMemGuaranteeTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingMemGuaranteeTests.cpp#L855-L859).

## Source Files

| Role | Link |
|------|------|
| Registration and implementation | [vktRayTracingMemGuaranteeTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingMemGuaranteeTests.cpp#L855-L875) |

## Registration Hierarchy

```text
ray_tracing_pipeline.memguarantee
├── between
└── inside
```

## Test Families

### memguarantee — Registered branch

Memory-guarantee tests register inside and between cases around shader-call memory behavior. The registered group name is created in [vktRayTracingMemGuaranteeTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingMemGuaranteeTests.cpp#L877-L880). Direct children observed in mustpass/source include `between`, `inside`.

## Parameter Dimensions

| Dimension | Observed values | Evidence |
|-----------|-----------------|----------|
| `memguarantee` direct children | `between`, `inside` | [vktRayTracingMemGuaranteeTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingMemGuaranteeTests.cpp#L877-L897) |

## Support / Feature Requirements

Support checks are implemented by the file's test cases; common ray tracing pipeline tests require `VK_KHR_ray_tracing_pipeline` and, where acceleration structures are used, `VK_KHR_acceleration_structure`, as illustrated by [vktRayTracingBuildTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L186-L205).

## Verification Methods

Verification is implemented in the generated test instances for this file; recurring methods include creating ray tracing pipelines/SBTs and comparing shader-visible outputs, with representative pipeline/SBT setup shown in [vktRayTracingBuildTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L437-L450).

## Test Principles

The file registers focused ray tracing pipeline scenarios and varies only the dimensions visible in its registration loops or child-group construction. Claims above are limited to inspected registration code and mustpass-observed path components.

## Notes
