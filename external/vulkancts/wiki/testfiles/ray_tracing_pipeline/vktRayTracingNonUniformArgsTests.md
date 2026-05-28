# vktRayTracingNonUniformArgsTests

This registered implementation file registers `non_uniform_args` under `ray_tracing_pipeline`. The group construction is evidenced in [vktRayTracingNonUniformArgsTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingNonUniformArgsTests.cpp#L517-L521).

## Source Files

| Role | Link |
|------|------|
| Registration and implementation | [vktRayTracingNonUniformArgsTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingNonUniformArgsTests.cpp#L517-L537) |

## Registration Hierarchy

```text
ray_tracing_pipeline.non_uniform_args
├── chit_1_types_0
├── chit_2_types_0
├── chit_2_types_1
├── chit_3_types_0
├── chit_3_types_1
├── chit_3_types_2
├── chit_4_types_0
├── chit_4_types_1
├── chit_4_types_2
├── chit_4_types_3
├── miss_cause_1
├── miss_cause_2
├── miss_cause_3
├── miss_cause_4
├── miss_cause_5
└── miss_cause_6
```

## Test Families

### non_uniform_args — Registered branch

Non-uniform argument tests generate closest-hit ray-type combinations and miss-cause cases. The registered group name is created in [vktRayTracingNonUniformArgsTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingNonUniformArgsTests.cpp#L520-L523). Direct children observed in mustpass/source include `chit_1_types_0`, `chit_2_types_0`, `chit_2_types_1`, `chit_3_types_0`, `chit_3_types_1`, `chit_3_types_2`, `chit_4_types_0`, `chit_4_types_1` and additional direct children.

## Parameter Dimensions

| Dimension | Observed values | Evidence |
|-----------|-----------------|----------|
| `non_uniform_args` direct children | `chit_1_types_0`, `chit_2_types_0`, `chit_2_types_1`, `chit_3_types_0`, `chit_3_types_1`, `chit_3_types_2`, `chit_4_types_0`, `chit_4_types_1`, `chit_4_types_2`, `chit_4_types_3`, `miss_cause_1`, `miss_cause_2` ... | [vktRayTracingNonUniformArgsTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingNonUniformArgsTests.cpp#L520-L540) |

## Support / Feature Requirements

Support checks are implemented by the file's test cases; common ray tracing pipeline tests require `VK_KHR_ray_tracing_pipeline` and, where acceleration structures are used, `VK_KHR_acceleration_structure`, as illustrated by [vktRayTracingBuildTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L186-L205).

## Verification Methods

Verification is implemented in the generated test instances for this file; recurring methods include creating ray tracing pipelines/SBTs and comparing shader-visible outputs, with representative pipeline/SBT setup shown in [vktRayTracingBuildTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L437-L450).

## Test Principles

The file registers focused ray tracing pipeline scenarios and varies only the dimensions visible in its registration loops or child-group construction. Claims above are limited to inspected registration code and mustpass-observed path components.

## Notes
