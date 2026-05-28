# vktRayQueryTests

This file is the `ray_query` category dispatcher. It includes the per-family headers and registers the direct children under the category root in [vktRayQueryTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryTests.cpp#L24-L38) and [vktRayQueryTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryTests.cpp#L49-L71).

## Source Files

| Role | Link |
|------|------|
| Category dispatcher | [vktRayQueryTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryTests.cpp#L49-L71) |
| Dispatcher declaration | [vktRayQueryTests.hpp](../../../modules/vulkan/ray_query/vktRayQueryTests.hpp#L29-L35) |

## Registration Hierarchy

```text
ray_query
├── builtin
├── traversal_control
├── acceleration_structures
├── procedural_geometry
├── advanced
├── watertightness
├── ray_flags
├── misc
├── direction_length
├── inside_aabbs
├── barycentric_coordinates
├── non_uniform_args
├── helper_invocations
├── opacity_micromap
├── position_fetch
├── multiple_ray_queries
└── stress
```

## Test Families

### builtin — Ray-query built-in result values

Registered by `createBuiltinTests()` in [vktRayQueryTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryTests.cpp#L53), with its group name created in [vktRayQueryBuiltinTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryBuiltinTests.cpp#L6291-L6295).

### traversal_control — Generated and skipped intersections

Registered by [vktRayQueryTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryTests.cpp#L54) and built as `traversal_control` in [vktRayQueryTraversalControlTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryTraversalControlTests.cpp#L2061-L2065).

### acceleration_structures — Ray-query acceleration-structure construction and operations

Registered by [vktRayQueryTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryTests.cpp#L55) and built as `acceleration_structures` in [vktRayQueryAccelerationStructuresTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L4744-L4748).

### procedural_geometry — Complex AABB procedural geometry scenes

Registered by [vktRayQueryTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryTests.cpp#L56) and built as `procedural_geometry` in [vktRayQueryProceduralGeometryTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryProceduralGeometryTests.cpp#L495-L503).

### advanced — Null acceleration-structure and wrapper-function cases

Registered from the built-in source file by [vktRayQueryTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryTests.cpp#L57) and built as `advanced` in [vktRayQueryBuiltinTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryBuiltinTests.cpp#L6419-L6428).

### watertightness — No-miss and single-hit consistency

Registered by [vktRayQueryTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryTests.cpp#L58) and built as `watertightness` in [vktRayQueryWatertightnessTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryWatertightnessTests.cpp#L2251-L2256).

### ray_flags — Ray flag behavior

Registered by [vktRayQueryTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryTests.cpp#L59) and built as `ray_flags` in [vktRayQueryCullRayFlagsTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryCullRayFlagsTests.cpp#L2112-L2116).

### misc — Miscellaneous ray-query behavior

Registered by [vktRayQueryTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryTests.cpp#L60) and built as `misc` in [vktRayQueryMiscTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryMiscTests.cpp#L2207-L2211).

### direction_length — Direction-vector scale and rotation

Registered by [vktRayQueryTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryTests.cpp#L61) and built as `direction_length` in [vktRayQueryDirectionTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryDirectionTests.cpp#L546-L550).

### inside_aabbs — Rays starting inside AABBs

Registered by [vktRayQueryTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryTests.cpp#L62) and built as `inside_aabbs` in [vktRayQueryDirectionTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryDirectionTests.cpp#L617-L621).

### barycentric_coordinates — Reported triangle barycentrics

Registered by [vktRayQueryTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryTests.cpp#L63) and built as `barycentric_coordinates` in [vktRayQueryBarycentricCoordinatesTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryBarycentricCoordinatesTests.cpp#L381-L390).

### non_uniform_args — Non-uniform ray-query arguments

Registered by [vktRayQueryTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryTests.cpp#L64) and built as `non_uniform_args` in [vktRayQueryNonUniformArgsTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryNonUniformArgsTests.cpp#L375-L388).

### helper_invocations — Helper-invocation behavior

Registered by [vktRayQueryTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryTests.cpp#L65) and built as `helper_invocations` in [vktRayQueryMiscTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryMiscTests.cpp#L2142-L2173).

### opacity_micromap — Opacity micromap integration

Registered by [vktRayQueryTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryTests.cpp#L66) and built as `opacity_micromap` in [vktRayQueryOpacityMicromapTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryOpacityMicromapTests.cpp#L1267-L1275).

### position_fetch — Fetched triangle vertex positions

Registered by [vktRayQueryTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryTests.cpp#L67) and built as `position_fetch` in [vktRayQueryPositionFetchTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryPositionFetchTests.cpp#L732-L737).

### multiple_ray_queries — Multiple simultaneous query objects

Registered by [vktRayQueryTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryTests.cpp#L68) and built as `multiple_ray_queries` in [vktRayQueryMultipleRayQueries.cpp](../../../modules/vulkan/ray_query/vktRayQueryMultipleRayQueries.cpp#L401-L470).

### stress — Large ray-query scenes

Registered by [vktRayQueryTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryTests.cpp#L69) and built as `stress` in [vktRayQueryStressTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryStressTests.cpp#L474-L572).

## Parameter Dimensions

The dispatcher itself has no generated parameters; it delegates to implementation files through `addChild()` calls [vktRayQueryTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryTests.cpp#L53-L69).

## Support / Feature Requirements

The dispatcher does not perform feature checks. Support is checked inside implementation test cases, for example the built-in tests require ray-query and acceleration-structure functionality in [vktRayQueryBuiltinTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryBuiltinTests.cpp#L6052-L6067).

## Verification Methods

The dispatcher does not verify results. Verification is implemented by child test instances, such as built-in result-buffer comparison in [vktRayQueryBuiltinTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryBuiltinTests.cpp#L1591-L1608).

## Notes
