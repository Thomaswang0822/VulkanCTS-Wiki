# vktRayTracingLinearSweptSpheresTests

This registered implementation file registers `linear_swept_spheres` under `ray_tracing_pipeline`. The group construction is evidenced in [vktRayTracingLinearSweptSpheresTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingLinearSweptSpheresTests.cpp#L960-L964).

## Source Files

| Role | Link |
|------|------|
| Registration and implementation | [vktRayTracingLinearSweptSpheresTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingLinearSweptSpheresTests.cpp#L960-L980) |

## Registration Hierarchy

```text
ray_tracing_pipeline.linear_swept_spheres
├── lss
└── spheres
```

## Test Families

### linear_swept_spheres — Registered branch

Linear swept spheres tests compare sphere and linear-swept-sphere geometry modes across copy, endcap, ray-query, hit-object, vertex-format, and radius-format choices. The registered group name is created in [vktRayTracingLinearSweptSpheresTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingLinearSweptSpheresTests.cpp#L1029-L1032). Direct children observed in mustpass/source include `lss`, `spheres`.

## Parameter Dimensions

| Dimension | Observed values | Evidence |
|-----------|-----------------|----------|
| `linear_swept_spheres` direct children | `lss`, `spheres` | [vktRayTracingLinearSweptSpheresTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingLinearSweptSpheresTests.cpp#L1029-L1049) |

## Support Requirements

Support requires acceleration structure, ray tracing pipeline, and `VK_NV_ray_tracing_linear_swept_spheres`, with an explicit ray-tracing-pipeline feature check [vktRayTracingLinearSweptSpheresTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingLinearSweptSpheresTests.cpp#L747-L757).

## Verification Methods

Verification reads a reference/result image and checks expected hit counts for spheres and linear-swept-sphere cases, including endcap-dependent expectations [vktRayTracingLinearSweptSpheresTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingLinearSweptSpheresTests.cpp#L351-L446).

## Test Principles

The file registers focused ray tracing pipeline scenarios and varies only the dimensions visible in its registration loops or child-group construction. Claims above are limited to inspected registration code and mustpass-observed path components.

## Notes

The API test plan provides general CTS framework context but no ray-tracing-pipeline-specific family breakdown in the inspected file.
