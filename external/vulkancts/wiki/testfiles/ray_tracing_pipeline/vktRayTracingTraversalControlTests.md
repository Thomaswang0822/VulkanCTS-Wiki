# vktRayTracingTraversalControlTests

This registered implementation file registers `traversal_control` under `ray_tracing_pipeline`. The group construction is evidenced in [vktRayTracingTraversalControlTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L766-L770).

## Source Files

| Role | Link |
|------|------|
| Registration and implementation | [vktRayTracingTraversalControlTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L766-L786) |

## Registration Hierarchy

```text
ray_tracing_pipeline.traversal_control
├── ahit_ignore_intersection
├── ahit_pass_through
├── ahit_terminate_ray
├── isect_dont_report_intersection
└── isect_report_intersection
```

## Test Families

### traversal_control — Registered branch

Traversal-control tests verify any-hit ignore/pass-through/terminate behavior and intersection shader report/donot-report behavior. The registered group name is created in [vktRayTracingTraversalControlTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L769-L772). Direct children observed in mustpass/source include `ahit_ignore_intersection`, `ahit_pass_through`, `ahit_terminate_ray`, `isect_dont_report_intersection`, `isect_report_intersection`.

## Parameter Dimensions

| Dimension | Observed values | Evidence |
|-----------|-----------------|----------|
| `traversal_control` direct children | `ahit_ignore_intersection`, `ahit_pass_through`, `ahit_terminate_ray`, `isect_dont_report_intersection`, `isect_report_intersection` | [vktRayTracingTraversalControlTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L769-L789) |

## Support / Feature Requirements

Support checks are implemented by the file's test cases; common ray tracing pipeline tests require `VK_KHR_ray_tracing_pipeline` and, where acceleration structures are used, `VK_KHR_acceleration_structure`, as illustrated by [vktRayTracingBuildTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L186-L205).

## Verification Methods

Verification is implemented in the generated test instances for this file; recurring methods include creating ray tracing pipelines/SBTs and comparing shader-visible outputs, with representative pipeline/SBT setup shown in [vktRayTracingBuildTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L437-L450).

## Test Principles

The file registers focused ray tracing pipeline scenarios and varies only the dimensions visible in its registration loops or child-group construction. Claims above are limited to inspected registration code and mustpass-observed path components.

## Notes
