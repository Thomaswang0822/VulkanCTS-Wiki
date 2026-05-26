# vktRayTracingBuiltinTests

This registered implementation file with multiple root groups registers `builtin`, `spec_constants` under `ray_tracing_pipeline`. The group construction is evidenced in [vktRayTracingBuiltinTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L4753-L4757).

## Source Files

| Role | Link |
|------|------|
| Registration and implementation | [vktRayTracingBuiltinTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L4753-L4773) |

## Registration Hierarchy

```text
ray_tracing_pipeline
├── builtin
└── spec_constants
```

## Test Families

### builtin — Registered branch

Shader built-in result checks cover launch IDs/sizes, primitive and instance identifiers, ray parameters, transforms, incoming flags, hit attributes, and indirect variants. The registered group name is created in [vktRayTracingBuiltinTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L4794-L4797). Direct children observed in mustpass/source include `geometryindexext`, `hitkindext`, `hittext`, `incomingrayflagsext`, `indirect`, `instancecustomindexext`, `instanceid`, `launchidext` and additional direct children.

### spec_constants — Registered branch

Specialization-constant cases register shader-stage leaves for raygen, hit, miss, callable, and intersection stage coverage. The registered group name is created in [vktRayTracingBuiltinTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L4811-L4814). Direct children observed in mustpass/source include `ahit`, `call`, `chit`, `miss`, `rgen`, `sect`.

## Parameter Dimensions

| Dimension | Observed values | Evidence |
|-----------|-----------------|----------|
| `builtin` direct children | `geometryindexext`, `hitkindext`, `hittext`, `incomingrayflagsext`, `indirect`, `instancecustomindexext`, `instanceid`, `launchidext`, `launchsizeext`, `objectraydirectionext`, `objectrayoriginext`, `objecttoworld3x4ext` ... | [vktRayTracingBuiltinTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L4794-L4814) |
| `spec_constants` direct children | `ahit`, `call`, `chit`, `miss`, `rgen`, `sect` | [vktRayTracingBuiltinTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L4811-L4831) |

## Support Requirements

Support checks are implemented by the file's test cases; common ray tracing pipeline tests require `VK_KHR_ray_tracing_pipeline` and, where acceleration structures are used, `VK_KHR_acceleration_structure`, as illustrated by [vktRayTracingBuildTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L186-L205).

## Verification Methods

Verification is implemented in the generated test instances for this file; recurring methods include creating ray tracing pipelines/SBTs and comparing shader-visible outputs, with representative pipeline/SBT setup shown in [vktRayTracingBuildTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L437-L450).

## Test Principles

The file registers focused ray tracing pipeline scenarios and varies only the dimensions visible in its registration loops or child-group construction. Claims above are limited to inspected registration code and mustpass-observed path components.

## Notes
