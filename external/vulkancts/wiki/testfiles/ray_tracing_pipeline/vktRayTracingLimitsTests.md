# vktRayTracingLimitsTests

This registered implementation file registers `limits` under `ray_tracing_pipeline`. The group construction is evidenced in [vktRayTracingLimitsTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingLimitsTests.cpp#L277-L281).

## Source Files

| Role | Link |
|------|------|
| Registration and implementation | [vktRayTracingLimitsTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingLimitsTests.cpp#L277-L297) |

## Registration Hierarchy

```text
ray_tracing_pipeline.limits
├── accel_struct_props
└── ray_tracing_props
```

## Test Families

### limits — Registered branch

Limits tests query acceleration-structure and ray-tracing pipeline property groups. The registered group name is created in [vktRayTracingLimitsTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingLimitsTests.cpp#L279-L282). Direct children observed in mustpass/source include `accel_struct_props`, `ray_tracing_props`.

## Parameter Dimensions

| Dimension | Observed values | Evidence |
|-----------|-----------------|----------|
| `limits` direct children | `accel_struct_props`, `ray_tracing_props` | [vktRayTracingLimitsTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingLimitsTests.cpp#L279-L299) |

## Support / Feature Requirements

Support is property-family-specific: acceleration-structure property checks require `VK_KHR_acceleration_structure`, and ray-tracing-pipeline property checks require `VK_KHR_ray_tracing_pipeline` [vktRayTracingLimitsTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingLimitsTests.cpp#L71-L77).

## Verification Methods

Verification checks reported acceleration-structure and ray-tracing-pipeline properties against required minimum ranges and alignment relationships, failing on individual property violations [vktRayTracingLimitsTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingLimitsTests.cpp#L123-L262).

## Test Principles

The file registers focused ray tracing pipeline scenarios and varies only the dimensions visible in its registration loops or child-group construction. Claims above are limited to inspected registration code and mustpass-observed path components.

## Notes
