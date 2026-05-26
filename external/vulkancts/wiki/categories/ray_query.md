# ray_query

The `ray_query` category documents Vulkan CTS tests for `VK_KHR_ray_query` behavior across graphics, compute, and ray-tracing shader stages. The category dispatcher creates the registered children in [vktRayQueryTests.cpp](../../modules/vulkan/ray_query/vktRayQueryTests.cpp#L49-L71), and the build file lists the implementation sources in [CMakeLists.txt](../../modules/vulkan/ray_query/CMakeLists.txt#L6-L37).

## Registration Entry Point

| Item | Evidence |
|------|----------|
| Category root | [vktRayQueryTests.cpp](../../modules/vulkan/ray_query/vktRayQueryTests.cpp#L49-L71) |
| Root header includes | [vktRayQueryTests.cpp](../../modules/vulkan/ray_query/vktRayQueryTests.cpp#L24-L38) |
| Build inventory | [CMakeLists.txt](../../modules/vulkan/ray_query/CMakeLists.txt#L6-L37) |

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

### builtin — Ray-query built-ins

The built-in branch covers flow, primitive/instance identifiers, transforms, ray origin/direction, intersection attributes, barycentrics, SBT record offsets, termination, and intersection types [vktRayQueryBuiltinTests.cpp](../../modules/vulkan/ray_query/vktRayQueryBuiltinTests.cpp#L6296-L6328). See [vktRayQueryBuiltinTests](../testfiles/ray_query/vktRayQueryBuiltinTests.md).

### traversal_control — Generated and skipped intersections

The traversal-control branch crosses shader source, `generate_intersection`/`skip_intersection`, and triangle/AABB bottom geometry [vktRayQueryTraversalControlTests.cpp](../../modules/vulkan/ray_query/vktRayQueryTraversalControlTests.cpp#L2066-L2165). See [vktRayQueryTraversalControlTests](../testfiles/ray_query/vktRayQueryTraversalControlTests.md).

### acceleration_structures — AS construction and operation variants

This branch covers build flags, formats, operations, host threading, function arguments, instance culling/update, dynamic indexing, and empty AS cases [vktRayQueryAccelerationStructuresTests.cpp](../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L4744-L4768). See [vktRayQueryAccelerationStructuresTests](../testfiles/ray_query/vktRayQueryAccelerationStructuresTests.md).

### procedural_geometry — AABB procedural geometry scenes

The branch registers two explicit procedural-geometry arrangements [vktRayQueryProceduralGeometryTests.cpp](../../modules/vulkan/ray_query/vktRayQueryProceduralGeometryTests.cpp#L495-L503). See [vktRayQueryProceduralGeometryTests](../testfiles/ray_query/vktRayQueryProceduralGeometryTests.md).

### advanced — Null AS and wrapper-function cases

The advanced branch is registered from the built-in source file and contains `null_as` and `using_wrapper_function` [vktRayQueryBuiltinTests.cpp](../../modules/vulkan/ray_query/vktRayQueryBuiltinTests.cpp#L6419-L6428). See [vktRayQueryBuiltinTests](../testfiles/ray_query/vktRayQueryBuiltinTests.md).

### watertightness — No-miss and single-hit consistency

The branch registers `nomiss` and `singlehit` across shader stages and geometry types [vktRayQueryWatertightnessTests.cpp](../../modules/vulkan/ray_query/vktRayQueryWatertightnessTests.cpp#L2251-L2344). See [vktRayQueryWatertightnessTests](../testfiles/ray_query/vktRayQueryWatertightnessTests.md).

### ray_flags — Ray flag effects

The branch covers opacity, terminate-on-first-hit, face culling, and skip-geometry flag families [vktRayQueryCullRayFlagsTests.cpp](../../modules/vulkan/ray_query/vktRayQueryCullRayFlagsTests.cpp#L2173-L2245). See [vktRayQueryCullRayFlagsTests](../testfiles/ray_query/vktRayQueryCullRayFlagsTests.md).

### misc — Miscellaneous cases

The misc branch includes ray-query dynamic indexing, scratch-buffer reuse, empty-AS update cases, and per-invocation ray counts [vktRayQueryMiscTests.cpp](../../modules/vulkan/ray_query/vktRayQueryMiscTests.cpp#L2207-L2270). See [vktRayQueryMiscTests](../testfiles/ray_query/vktRayQueryMiscTests.md).

### direction_length — Ray direction scale/rotation

The branch varies triangle/AABB geometry, generated scaling factors, and generated rotations [vktRayQueryDirectionTests.cpp](../../modules/vulkan/ray_query/vktRayQueryDirectionTests.cpp#L546-L614). See [vktRayQueryDirectionTests](../testfiles/ray_query/vktRayQueryDirectionTests.md).

### inside_aabbs — Ray origins inside AABBs

The branch varies ray end positions, scaling factors, and rotations for rays starting inside AABBs [vktRayQueryDirectionTests.cpp](../../modules/vulkan/ray_query/vktRayQueryDirectionTests.cpp#L617-L681). See [vktRayQueryDirectionTests](../testfiles/ray_query/vktRayQueryDirectionTests.md).

### barycentric_coordinates — Triangle barycentric results

This branch registers one compute case with deterministic seed [vktRayQueryBarycentricCoordinatesTests.cpp](../../modules/vulkan/ray_query/vktRayQueryBarycentricCoordinatesTests.cpp#L381-L390). See [vktRayQueryBarycentricCoordinatesTests](../testfiles/ray_query/vktRayQueryBarycentricCoordinatesTests.md).

### non_uniform_args — Non-uniform arguments

The branch iterates `MissCause` values to register `no_miss` and numbered miss causes [vktRayQueryNonUniformArgsTests.cpp](../../modules/vulkan/ray_query/vktRayQueryNonUniformArgsTests.cpp#L375-L388). See [vktRayQueryNonUniformArgsTests](../testfiles/ray_query/vktRayQueryNonUniformArgsTests.md).

### helper_invocations — Helper invocation behavior

This branch crosses CPU/GPU build, derivative style, mode, screen size, and model size [vktRayQueryMiscTests.cpp](../../modules/vulkan/ray_query/vktRayQueryMiscTests.cpp#L2142-L2203). See [vktRayQueryMiscTests](../testfiles/ray_query/vktRayQueryMiscTests.md).

### opacity_micromap — Opacity micromap integration

This branch registers render and copy families and requires `VK_EXT_opacity_micromap` support [vktRayQueryOpacityMicromapTests.cpp](../../modules/vulkan/ray_query/vktRayQueryOpacityMicromapTests.cpp#L1267-L1275). See [vktRayQueryOpacityMicromapTests](../testfiles/ray_query/vktRayQueryOpacityMicromapTests.md).

### position_fetch — Vertex position fetch

This branch crosses shader source, CPU/GPU build, vertex formats, and flag masks [vktRayQueryPositionFetchTests.cpp](../../modules/vulkan/ray_query/vktRayQueryPositionFetchTests.cpp#L732-L837). See [vktRayQueryPositionFetchTests](../testfiles/ray_query/vktRayQueryPositionFetchTests.md).

### multiple_ray_queries — Multiple query objects

This branch registers one case per shader source and traverses multiple ray-query objects in parallel [vktRayQueryMultipleRayQueries.cpp](../../modules/vulkan/ray_query/vktRayQueryMultipleRayQueries.cpp#L401-L470). See [vktRayQueryMultipleRayQueries](../testfiles/ray_query/vktRayQueryMultipleRayQueries.md).

### stress — Larger ray-query scenes

This branch registers shader-source groups with triangle/AABB leaves and a larger ray count [vktRayQueryStressTests.cpp](../../modules/vulkan/ray_query/vktRayQueryStressTests.cpp#L474-L572). See [vktRayQueryStressTests](../testfiles/ray_query/vktRayQueryStressTests.md).

## File Inventory

| Wiki page | Source role | Registered path roots |
|-----------|-------------|-----------------------|
| [vktRayQueryTests](../testfiles/ray_query/vktRayQueryTests.md) | Category dispatcher | `ray_query` |
| [vktRayQueryBuiltinTests](../testfiles/ray_query/vktRayQueryBuiltinTests.md) | Built-in and advanced implementation | `ray_query.builtin`, `ray_query.advanced` |
| [vktRayQueryTraversalControlTests](../testfiles/ray_query/vktRayQueryTraversalControlTests.md) | Traversal-control implementation | `ray_query.traversal_control` |
| [vktRayQueryAccelerationStructuresTests](../testfiles/ray_query/vktRayQueryAccelerationStructuresTests.md) | Acceleration-structure implementation | `ray_query.acceleration_structures` |
| [vktRayQueryProceduralGeometryTests](../testfiles/ray_query/vktRayQueryProceduralGeometryTests.md) | Procedural-geometry implementation | `ray_query.procedural_geometry` |
| [vktRayQueryWatertightnessTests](../testfiles/ray_query/vktRayQueryWatertightnessTests.md) | Watertightness implementation | `ray_query.watertightness` |
| [vktRayQueryCullRayFlagsTests](../testfiles/ray_query/vktRayQueryCullRayFlagsTests.md) | Ray-flags implementation | `ray_query.ray_flags` |
| [vktRayQueryMiscTests](../testfiles/ray_query/vktRayQueryMiscTests.md) | Misc and helper-invocation implementation | `ray_query.misc`, `ray_query.helper_invocations` |
| [vktRayQueryDirectionTests](../testfiles/ray_query/vktRayQueryDirectionTests.md) | Direction and inside-AABB implementation | `ray_query.direction_length`, `ray_query.inside_aabbs` |
| [vktRayQueryBarycentricCoordinatesTests](../testfiles/ray_query/vktRayQueryBarycentricCoordinatesTests.md) | Barycentric implementation | `ray_query.barycentric_coordinates` |
| [vktRayQueryNonUniformArgsTests](../testfiles/ray_query/vktRayQueryNonUniformArgsTests.md) | Non-uniform argument implementation | `ray_query.non_uniform_args` |
| [vktRayQueryOpacityMicromapTests](../testfiles/ray_query/vktRayQueryOpacityMicromapTests.md) | Opacity micromap implementation | `ray_query.opacity_micromap` |
| [vktRayQueryPositionFetchTests](../testfiles/ray_query/vktRayQueryPositionFetchTests.md) | Position-fetch implementation | `ray_query.position_fetch` |
| [vktRayQueryMultipleRayQueries](../testfiles/ray_query/vktRayQueryMultipleRayQueries.md) | Multiple ray-query implementation | `ray_query.multiple_ray_queries` |
| [vktRayQueryStressTests](../testfiles/ray_query/vktRayQueryStressTests.md) | Stress implementation | `ray_query.stress` |

## Recurring Parameter Dimensions

| Theme | Observed dimensions | Evidence |
|-------|---------------------|----------|
| Shader stages | Graphics, compute, and ray-tracing shader source groups recur in built-in, traversal, flags, multiple-query, stress, and selected extension files | [vktRayQueryBuiltinTests.cpp](../../modules/vulkan/ray_query/vktRayQueryBuiltinTests.cpp#L6359-L6413), [vktRayQueryMultipleRayQueries.cpp](../../modules/vulkan/ray_query/vktRayQueryMultipleRayQueries.cpp#L401-L470) |
| Geometry | Triangle and AABB geometry is explicit in traversal, flags, watertightness, stress, and direction tests | [vktRayQueryTraversalControlTests.cpp](../../modules/vulkan/ray_query/vktRayQueryTraversalControlTests.cpp#L2131-L2138), [vktRayQueryStressTests.cpp](../../modules/vulkan/ray_query/vktRayQueryStressTests.cpp#L538-L545) |
| AS construction | Residency, CPU/GPU build, flags, formats, operation type, and empty-structure modes | [vktRayQueryAccelerationStructuresTests.cpp](../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L3522-L3773), [vktRayQueryAccelerationStructuresTests.cpp](../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L4572-L4741) |
| Extension-specific options | Opacity micromap flags/modes/levels/copy types and position-fetch vertex formats | [vktRayQueryOpacityMicromapTests.cpp](../../modules/vulkan/ray_query/vktRayQueryOpacityMicromapTests.cpp#L1070-L1264), [vktRayQueryPositionFetchTests.cpp](../../modules/vulkan/ray_query/vktRayQueryPositionFetchTests.cpp#L764-L837) |

## Recurring Support Requirements

Most implementations require `VK_KHR_acceleration_structure`, `VK_KHR_ray_query`, and the corresponding feature bits, as shown in built-in support checks [vktRayQueryBuiltinTests.cpp](../../modules/vulkan/ray_query/vktRayQueryBuiltinTests.cpp#L6052-L6067). Stage matrices add tessellation, geometry, vertex-pipeline-store, and `VK_KHR_ray_tracing_pipeline` gates [vktRayQueryTraversalControlTests.cpp](../../modules/vulkan/ray_query/vktRayQueryTraversalControlTests.cpp#L1312-L1340). Extension branches add `VK_EXT_opacity_micromap` or `VK_KHR_ray_tracing_position_fetch` [vktRayQueryOpacityMicromapTests.cpp](../../modules/vulkan/ray_query/vktRayQueryOpacityMicromapTests.cpp#L153-L193), [vktRayQueryPositionFetchTests.cpp](../../modules/vulkan/ray_query/vktRayQueryPositionFetchTests.cpp#L132-L186).

## Recurring Verification Methods

Observed verification methods include result-buffer comparison against expected integers/fixed-point values [vktRayQueryBuiltinTests.cpp](../../modules/vulkan/ray_query/vktRayQueryBuiltinTests.cpp#L1591-L1608), image/reference comparison with `tcu::intThresholdCompare` [vktRayQueryTraversalControlTests.cpp](../../modules/vulkan/ray_query/vktRayQueryTraversalControlTests.cpp#L580-L688), scalar/vector tolerance checks [vktRayQueryDirectionTests.cpp](../../modules/vulkan/ray_query/vktRayQueryDirectionTests.cpp#L476-L503), and extension-specific output-buffer comparisons [vktRayQueryOpacityMicromapTests.cpp](../../modules/vulkan/ray_query/vktRayQueryOpacityMicromapTests.cpp#L1032-L1065).

## Scope Notes

Helper-only files were not present in this category directory; every `.cpp` file under [ray_query](../../modules/vulkan/ray_query/) that registers tests received a Level-3 page.
