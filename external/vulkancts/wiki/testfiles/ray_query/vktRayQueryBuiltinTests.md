# vktRayQueryBuiltinTests

This file registers the `builtin` and `advanced` ray-query branches and verifies many ray-query result built-ins and two advanced cases. The registered group names are constructed in [vktRayQueryBuiltinTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryBuiltinTests.cpp#L6291-L6295) and [vktRayQueryBuiltinTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryBuiltinTests.cpp#L6419-L6428).

## Source Files

| Role | Link |
|------|------|
| Implementation and registration | [vktRayQueryBuiltinTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryBuiltinTests.cpp#L6291-L6492) |

## Registration Hierarchy

```text
ray_query
├── builtin
└── advanced
```

## Test Families

### builtin — Built-in query results

The `builtin` branch creates direct child groups for `flow`, primitive and instance identifiers, ray origin/direction, object/world transforms, ray `tmin`, candidate/committed intersection state, barycentrics, SBT record offsets, `rayqueryterminate`, and intersection type [vktRayQueryBuiltinTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryBuiltinTests.cpp#L6291-L6328). Each child is crossed with graphics, compute, and ray-tracing shader stages listed through `pipelineStages`; stage-specific support is selected by `getPipelineCheckSupport()` [vktRayQueryBuiltinTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryBuiltinTests.cpp#L6359-L6413) and [vktRayQueryBuiltinTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryBuiltinTests.cpp#L6130-L6151).

### advanced — Null acceleration structure and wrapper function

The `advanced` branch registers `null_as` and `using_wrapper_function`; the wrapper-function case is explicitly limited to compute by the stage filter in [vktRayQueryBuiltinTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryBuiltinTests.cpp#L6419-L6450).

## Parameter Dimensions

| Dimension | Observed values | Evidence |
|-----------|-----------------|----------|
| Built-in test type | `flow`, IDs, transforms, world/object ray values, intersection properties, barycentrics, SBT offset, terminate, intersection type | [vktRayQueryBuiltinTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryBuiltinTests.cpp#L6296-L6328) |
| Shader stage | Graphics, compute, and ray-tracing stages selected through `pipelineStages` | [vktRayQueryBuiltinTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryBuiltinTests.cpp#L6359-L6365) |
| Geometry type | Iterates `geomTypes`; some candidate AABB and triangle-only tests are filtered by geometry | [vktRayQueryBuiltinTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryBuiltinTests.cpp#L6372-L6404) |
| Advanced test type | `null_as`, `using_wrapper_function` | [vktRayQueryBuiltinTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryBuiltinTests.cpp#L6423-L6428) |

## Support / Feature Requirements

Cases require `VK_KHR_acceleration_structure`, `VK_KHR_ray_query`, and the `rayQuery` and `accelerationStructure` feature bits [vktRayQueryBuiltinTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryBuiltinTests.cpp#L6052-L6067). Graphics-stage variants require vertex-pipeline stores and, when selected, tessellation or geometry features [vktRayQueryBuiltinTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryBuiltinTests.cpp#L381-L404). Ray-tracing shader stages require `VK_KHR_ray_tracing_pipeline` and its feature bit [vktRayQueryBuiltinTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryBuiltinTests.cpp#L1172-L1181). The `null_as` capability setup adds robustness and extension requirements in [vktRayQueryBuiltinTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryBuiltinTests.cpp#L6083-L6117).

## Verification Methods

Result buffers are compared against per-case expected integer or fixed-point values; mismatches increment failure counts in the base verifier [vktRayQueryBuiltinTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryBuiltinTests.cpp#L1591-L1608), and the test instance returns pass/fail based on that verifier [vktRayQueryBuiltinTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryBuiltinTests.cpp#L6019-L6024).

## Test Principles

The file builds compact scenes whose expected values are derived in configuration objects, then runs identical semantic checks through multiple shader pipelines and geometry modes.
