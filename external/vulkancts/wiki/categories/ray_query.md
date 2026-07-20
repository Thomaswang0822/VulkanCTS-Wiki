## Overview

The `ray_query` test category collects tests that check device-side ray traversal through `VK_KHR_ray_query` across graphics, compute, and ray-tracing shader stages.

## Background Knowledge

These concepts form the shared model used throughout the `ray_query` test category. Level-3 pages briefly restate the
part they need, then add family-specific prerequisites.

- **Acceleration-structure hierarchy and spaces.** A bottom-level acceleration structure (BLAS) stores triangle or
  AABB geometry in object space. A top-level acceleration structure (TLAS) stores transformed instances that reference
  BLASes and supply metadata. For example, one bunny BLAS can be reused by several differently transformed bunny
  instances inside a Cornell Box scene. Traversal selects a TLAS instance, transforms the ray into the instance's
  object space, and traverses the referenced BLAS. See [Acceleration
  Structures](../../../vulkan-docs/src/chapters/accelstructures.adoc) for more details.

- **Parametric rays and intervals.** A ray is evaluated as `origin + t * direction`. `Tmin` and `Tmax` bound the
  accepted interval of `t`; because `direction` need not be normalized, `t` is not necessarily world-space distance.

- **Inline traversal versus pipeline tracing.** A `rayQueryEXT` object keeps traversal state inside the shader
  invocation that calls `rayQueryInitializeEXT`. The shader advances that state explicitly with `rayQueryProceedEXT`.
  By contrast, `traceRayEXT` launches traversal through a ray tracing pipeline and transfers control through
  shader-binding-table stages. A ray-tracing shader can host an inline query, but the pipeline trace and the query
  remain separate traversals.

- **Candidate and committed state.** `rayQueryProceedEXT` can expose a provisional candidate while the query
  separately retains the closest accepted, or committed, intersection. Candidate selectors read the currently exposed
  intersection; committed selectors read the retained result. If traversal finishes without an accepted hit, the
  committed type remains none.

- **Triangle and AABB acceptance.** An opaque triangle can commit without being exposed for shader confirmation, while
  a non-opaque triangle candidate can be accepted with `rayQueryConfirmIntersectionEXT`. An AABB represents a
  procedural opportunity rather than a built-in surface hit, so it is exposed as a candidate and requires
  `rayQueryGenerateIntersectionEXT` with an application-supplied `t` to create an intersection. Calling neither
  acceptance operation discards an exposed candidate and lets traversal continue. See the [ray traversal
  chapter](../../../vulkan-docs/src/chapters/raytraversal.adoc).

## Category Structure

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

The dispatcher [vktRayQueryTests.cpp](../../modules/vulkan/ray_query/vktRayQueryTests.cpp#L49-L71) is registration-only: it adds 17 child groups and delegates each to a separate `create*Tests` function. The 17 registered families map to 14 Level-3 pages because three pages each cover two families rooted in the same implementation file:

- [Builtin.md](../testfiles/ray_query/Builtin.md) covers `builtin` and `advanced` (both in `vktRayQueryBuiltinTests.cpp`).
- [Misc.md](../testfiles/ray_query/Misc.md) covers `misc` and `helper_invocations` (both in `vktRayQueryMiscTests.cpp`).
- [DirectionLength.md](../testfiles/ray_query/DirectionLength.md) covers `direction_length` and `inside_aabbs` (both in `vktRayQueryDirectionTests.cpp`).

## How the Families Fit Together

All families exercise inline ray-query operations in shader code. Several run those operations from ray-tracing shader stages, but the query maintains its own traversal state rather than launching a separate `traceRayEXT` traversal; the `stress` family also includes one `traceRayEXT` control path for comparison.

- `builtin`, `traversal_control`, and `barycentric_coordinates` test **what values** the query built-ins return for hit candidates, generated/skipped intersections, and triangle barycentric coordinates.
- `watertightness`, `ray_flags`, `non_uniform_args`, and `direction_length` test **which candidates** survive traversal under edge conditions: watertightness cracks, cull and flag masks, miss-causing arguments, and non-unit direction scaling.
- `acceleration_structures`, `procedural_geometry`, and `misc` test **how the query behaves** when the acceleration structure or query infrastructure varies: build flags, AABB scenes, dynamic indexing, empty-AS updates, and helper-invocation contexts.
- `opacity_micromap`, `position_fetch`, `multiple_ray_queries`, and `stress` test **extension-specific features and scale**: opacity micromap, position fetch, concurrent query objects, and large ray counts across all shader stages.

## Level-3 Pages Navigation

| Registered test family or area | Level-3 page | What to read there |
|--------------------------------|--------------|--------------------|
| `builtin`, `advanced` | [Builtin.md](../testfiles/ray_query/Builtin.md) | Ray-query result built-ins across shader stages, plus null-AS and wrapper-function cases. |
| `traversal_control` | [TraversalControl.md](../testfiles/ray_query/TraversalControl.md) | `generate_intersection` and `skip_intersection` behavior across shader stages and triangle/AABB geometry. |
| `acceleration_structures` | [AccelerationStructures.md](../testfiles/ray_query/AccelerationStructures.md) | Build flags, formats, operations, host threading, instance culling/update, dynamic indexing, and empty AS cases. |
| `procedural_geometry` | [ProceduralGeometry.md](../testfiles/ray_query/ProceduralGeometry.md) | Two procedural AABB arrangements and result-buffer comparison. |
| `watertightness` | [Watertightness.md](../testfiles/ray_query/Watertightness.md) | `nomiss` and `singlehit` consistency across shader stages and geometry types. |
| `ray_flags` | [CullRayFlags.md](../testfiles/ray_query/CullRayFlags.md) | Opacity, terminate-on-first-hit, face culling, and skip-geometry flag families. |
| `misc`, `helper_invocations` | [Misc.md](../testfiles/ray_query/Misc.md) | Dynamic indexing, scratch-buffer reuse, empty-AS updates, per-invocation ray counts, and helper-invocation ray queries. |
| `direction_length`, `inside_aabbs` | [DirectionLength.md](../testfiles/ray_query/DirectionLength.md) | Direction scaling and rotation, plus rays starting inside AABBs. |
| `barycentric_coordinates` | [BarycentricCoordinates.md](../testfiles/ray_query/BarycentricCoordinates.md) | Triangle barycentric result verification with a deterministic seed. |
| `non_uniform_args` | [NonUniformArgs.md](../testfiles/ray_query/NonUniformArgs.md) | `MissCause` iteration: `no_miss` and `miss_cause_1` through `miss_cause_6`. |
| `opacity_micromap` | [OpacityMicromap.md](../testfiles/ray_query/OpacityMicromap.md) | `VK_EXT_opacity_micromap` render and copy families: formats, modes, levels, copy types. |
| `position_fetch` | [PositionFetch.md](../testfiles/ray_query/PositionFetch.md) | `VK_KHR_ray_tracing_position_fetch`: 15 vertex formats, CPU/GPU build, flag masks, fetched-position tolerance. |
| `multiple_ray_queries` | [MultipleRayQueries.md](../testfiles/ray_query/MultipleRayQueries.md) | One case per shader source traversing multiple query objects in parallel. |
| `stress` | [Stress.md](../testfiles/ray_query/Stress.md) | Larger ray-count scenes across shader sources and triangle/AABB leaves. |

## Category Notes

- The dispatcher [vktRayQueryTests.cpp](../../modules/vulkan/ray_query/vktRayQueryTests.cpp#L49-L71) contains no test implementation. It adds 17 child groups, each delegated to a separate `create*Tests` function.
- Most families require `VK_KHR_acceleration_structure` and `VK_KHR_ray_query`. Extension families add `VK_EXT_opacity_micromap` or `VK_KHR_ray_tracing_position_fetch`. Stage-sweep families add `VK_KHR_ray_tracing_pipeline` and tessellation or geometry feature gates as needed.
- The build file [CMakeLists.txt](../../modules/vulkan/ray_query/CMakeLists.txt#L6-L37) lists all implementation sources.
