# vktRayTracingDataSpillTests

This registered implementation file registers `data_spill` under `ray_tracing_pipeline`. The group construction is evidenced in [vktRayTracingDataSpillTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L2887-L2891).

## Source Files

| Role | Link |
|------|------|
| Registration and implementation | [vktRayTracingDataSpillTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L2887-L2907) |

## Registration Hierarchy

```text
ray_tracing_pipeline.data_spill
├── execute_callable
├── pipeline_interface
├── report_intersection
└── trace_ray
```

## Test Families

### data_spill — Registered branch

Data-spill tests cover data spilling around trace-ray, report-intersection, execute-callable, and pipeline-interface paths. The registered group name is created in [vktRayTracingDataSpillTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L2890-L2893). Direct children observed in mustpass/source include `execute_callable`, `pipeline_interface`, `report_intersection`, `trace_ray`.

## Parameter Dimensions

| Dimension | Observed values | Evidence |
|-----------|-----------------|----------|
| `data_spill` direct children | `execute_callable`, `pipeline_interface`, `report_intersection`, `trace_ray` | [vktRayTracingDataSpillTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L2890-L2910) |

## Support Requirements

Support starts with common acceleration-structure/ray-tracing-pipeline checks and then adds conditional gates based on spilled data type: 64-bit integer/float features, 16-bit storage and float/int features, 8-bit storage/int features, or descriptor indexing for sampler-based data [vktRayTracingDataSpillTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L476-L533).

## Verification Methods

Verification compares generated output data against expected values assembled for each call or pipeline-interface path, for example callable-data, hit-attribute, and shader-record-buffer expectations [vktRayTracingDataSpillTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L2820-L2836).

## Test Principles

The file registers focused ray tracing pipeline scenarios and varies only the dimensions visible in its registration loops or child-group construction. Claims above are limited to inspected registration code and mustpass-observed path components.

## Notes

The API test plan provides general CTS framework context but no ray-tracing-pipeline-specific family breakdown in the inspected file.
