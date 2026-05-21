# vktRayTracingNullASTests

This registered implementation file registers `null_as` under `ray_tracing_pipeline`. The group construction is evidenced in [vktRayTracingNullASTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingNullASTests.cpp#L756-L760).

## Source Files

| Role | Link |
|------|------|
| Registration and implementation | [vktRayTracingNullASTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingNullASTests.cpp#L756-L776) |

## Registration Hierarchy

```text
ray_tracing_pipeline.null_as
├── mixed_dispatches
└── test
```

## Test Families

### null_as — Registered branch

Null acceleration-structure tests check always-miss behavior and mixed dispatches using null descriptors. The registered group name is created in [vktRayTracingNullASTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingNullASTests.cpp#L759-L762). Direct children observed in mustpass/source include `mixed_dispatches`, `test`.

## Parameter Dimensions

| Dimension | Observed values | Evidence |
|-----------|-----------------|----------|
| `null_as` direct children | `mixed_dispatches`, `test` | [vktRayTracingNullASTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingNullASTests.cpp#L759-L779) |

## Support Requirements

Support is checked in this file: the `test` case requires ray tracing pipeline support plus acceleration-structure, deferred-host-operation, buffer-device-address consistency and robustness2/nullDescriptor support [vktRayTracingNullASTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingNullASTests.cpp#L278-L310); the `mixed_dispatches` descriptor case requires acceleration structure and ray tracing pipeline support [vktRayTracingNullASTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingNullASTests.cpp#L707-L711).

## Verification Methods

The `test` case validates every output element against expected value `4` [vktRayTracingNullASTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingNullASTests.cpp#L528-L556); `mixed_dispatches` verifies four buffer sections written by alternating trace-rays and compute dispatches [vktRayTracingNullASTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingNullASTests.cpp#L674-L685).

## Test Principles

The file registers focused ray tracing pipeline scenarios and varies only the dimensions visible in its registration loops or child-group construction. Claims above are limited to inspected registration code and mustpass-observed path components.

## Notes

The API test plan provides general CTS framework context but no ray-tracing-pipeline-specific family breakdown in the inspected file.
