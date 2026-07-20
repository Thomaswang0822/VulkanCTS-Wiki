# Understanding Brief: ray_tracing_pipeline.watertightness

## One-Sentence Test Purpose

This test checks whether ray tracing acceleration structure traversal is watertight across shared triangle edges and vertices, catching both cracks (rays that miss when they should hit) and duplicate any-hit invocations (rays that hit the same shared edge from two adjacent triangles) in fan and closed-fan triangle arrangements.

## Background Knowledge

### Watertightness in ray traversal

A triangle acceleration structure is watertight when a ray that passes through a point on a shared edge or shared vertex between two adjacent triangles is reported as a hit by exactly one of those triangles. Watertightness failures produce two classes of bug:

- **Cracks**: the ray slips through the shared edge/vertex and reports a miss. This happens when both adjacent triangles' edge intersection tests reject the ray due to floating-point roundoff or inconsistent edge orientation.
- **Duplicate hits**: both adjacent triangles report a hit for the same ray at the shared edge/vertex. This happens when the traversal engine invokes the any-hit shader more than once for geometry that shares an edge.

Why it matters here:
- The `0` through `9` legacy fan cases generate random recursive fan triangulations and fire one ray per pixel downward through the fan. The host treats any miss as a failure, directly catching crack bugs.
- The `closedFan` and `closedFan2` cases build a closed fan of triangles sharing a center vertex and test rays that aim at the center vertex and at the midpoint of each shared edge. They use `imageAtomicAdd` per any-hit invocation so duplicate hits accumulate, and they set `VK_GEOMETRY_NO_DUPLICATE_ANY_HIT_INVOCATION_BIT_KHR` on each geometry so the implementation must not invoke the any-hit shader twice for the same ray/geometry pair.

### VK_GEOMETRY_NO_DUPLICATE_ANY_HIT_INVOCATION_BIT_KHR

This geometry flag requests that the implementation avoid invoking the any-hit shader more than once per primitive per ray. The Vulkan spec allows implementations to invoke the any-hit shader multiple times for a primitive when a ray hits the same primitive in multiple internal nodes, but this flag asks them not to. The closedFan variants rely on this flag so a duplicate hit at a shared edge can only come from two different triangles (a true watertightness failure), not from a single triangle being visited twice.

### gl_PrimitiveID vs gl_GeometryIndexEXT

- `gl_PrimitiveID` is the index of the triangle within the current geometry in the bottom-level acceleration structure.
- `gl_GeometryIndexEXT` is the index of the geometry within the bottom-level acceleration structure that was hit.

The closedFan variant (single BLAS, N geometries, one triangle per geometry) uses `gl_PrimitiveID` for the result image z coordinate. The closedFan2 variant (N BLASes, one geometry per BLAS) uses `gl_GeometryIndexEXT` for the z coordinate. Both built-ins are 0 in their respective topologies because each geometry has exactly one primitive and each BLAS has exactly one geometry. The z coordinate therefore ends up identifying the per-ray hit slot, and the host check uses the full `(x, y, z)` cell to detect duplicate hits.

## One Concrete Example

Take `dEQP-VK.ray_tracing_pipeline.watertightness.closedFan.4`:

- The host builds a closed fan of 4 triangles arranged around the origin in the XY plane, all sharing the center vertex `(0, 0, 0)`. Each triangle also shares an edge with its neighbor.
- The fan lives in a single bottom-level acceleration structure as 4 separate geometries (one triangle each), all created with `VK_GEOMETRY_NO_DUPLICATE_ANY_HIT_INVOCATION_BIT_KHR`.
- The raygen shader fires 5 rays: ray 0 aims at the shared center vertex, rays 1 through 4 aim at the midpoint of each shared edge.
- Each ray's any-hit invocation does `imageAtomicAdd(result, ivec3(gl_LaunchIDEXT.xy, gl_PrimitiveID), 1)`. The miss shader does `imageAtomicAdd(result, ivec3(gl_LaunchIDEXT.xy, 0), 10000)`.
- The host scans every cell of the 3D result image. Any cell with value greater than 1 (excluding the magic 10000) is a duplicate-hit failure. Any cell with value 10000 is a miss and produces a quality warning.

This case is the smallest closed-fan case and exercises the exact mechanism the test relies on.

## End-to-End Test Flow

Two distinct flows share the same `RayTracingWatertightnessTestInstance`:

```text
[host] choose test variant (0-9, closedFan, closedFan2) and triangle count
[host] check ray tracing pipeline + acceleration structure feature support
[host] allocate result image (2D for 0-9, 3D for closedFan variants) and host-visible readback buffer
[host] build bottom-level acceleration structure(s):
       - 0-9: recursive random fan triangulation, single BLAS, single geometry with N triangles
       - closedFan: closed fan, single BLAS, N geometries (one triangle each), NO_DUPLICATE_ANY_HIT flag
       - closedFan2: closed fan, N BLASes (one triangle each), NO_DUPLICATE_ANY_HIT flag
[host] build top-level acceleration structure with one or more instances
[host] build ray tracing pipeline (raygen, miss, one or more any-hit hit groups)
[host] build shader binding table regions for raygen, miss, and hit groups
[host] clear result image (5,5,5,255 for 0-9; 0,0,0,0 for closedFan variants)
[host] record cmdBuffer: image layout transition, clear, AS build, descriptor update, bind, traceRays, copyback
[device] raygen fires one ray per launch invocation (256x256 for 0-9; (1+sqrt(N)) x sqrt(N) for closedFan)
[device] any-hit writes 1 (0-9) or atomicAdd 1 (closedFan) to result; miss writes 2 (0-9) or atomicAdd 10000 (closedFan)
[host] after submit+wait, invalidate readback buffer and scan result
[host] 0-9: first N pixels must all equal 1 (no misses)
[host] closedFan: any cell > 1 (excluding 10000) is a failure; any cell == 10000 is a quality warning
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `rgen` raygen shader. For `0-9` it is the common `getCommonRayGenerationShader` helper that fires one ray per pixel downward. For `closedFan`/`closedFan2` it is generated inline with `nSharedEdges + 1` active rays targeting the center vertex and each shared edge midpoint.
- `ahit` any-hit shader. For `0-9` it does `imageStore(result, ivec2(gl_LaunchIDEXT.xy), uvec4(1,0,0,1))`. For `closedFan`/`closedFan2` it does `imageAtomicAdd(result, ivec3(gl_LaunchIDEXT.xy, <zCoord>), 1)` where `<zCoord>` is `gl_PrimitiveID` for `closedFan` and `gl_GeometryIndexEXT` for `closedFan2`.
- `miss` miss shader. For `0-9` it does `imageStore(..., uvec4(2,0,0,1))`. For `closedFan`/`closedFan2` it does `imageAtomicAdd(result, ivec3(gl_LaunchIDEXT.xy, 0), 10000)`.

All shaders are GLSL 460 with `GL_EXT_ray_tracing`, compiled with SPIR-V 1.4 build options.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Result storage image (`VK_FORMAT_R32_UINT`) | yes | yes (binding 0) | yes (shader writes) | yes (via copyback buffer) | Stores hit/miss markers per ray; this is the only shader-visible test output |
| Top-level acceleration structure | yes | yes (binding 1) | yes (traversal reads) | no | Holds instances of the bottom-level AS; raygen traces against it |
| Bottom-level acceleration structure(s) | yes | yes (referenced by TLAS) | yes (traversal reads) | no | Holds triangle geometry with `VK_GEOMETRY_NO_DUPLICATE_ANY_HIT_INVOCATION_BIT_KHR` for closedFan variants |
| Host-visible readback buffer | yes | yes (transfer dst) | no (transfer writes) | yes | Receives image copyback for host validation |
| Shader binding table regions | yes | yes (traceRays argument) | yes (traversal reads) | no | Selects raygen, miss, and hit group shaders per ray |

## What Is Checked

For `0` through `9` (legacy random fan, `useClosedFan = false`):

- The result image is 2D, `256 x 256`, cleared to `5,5,5,255`.
- The host scans the first `squaresGroupCount` pixels. Each must equal `1` (hit). Any other value (typically `2` from the miss shader) is a failure.
- The check catches cracks only. Duplicate hits are invisible because `imageStore` overwrites with the same value `1`.

For `closedFan` and `closedFan2` (`useClosedFan = true`):

- The result image is 3D, `(1 + sqrt(N)) x sqrt(N) x N`, cleared to `0,0,0,0`.
- The host scans every cell of the 3D image.
- A cell value greater than `1`, excluding the magic `10000`, is a failure (duplicate any-hit invocation).
- A cell value equal to `10000` is a miss and produces a quality warning (not a failure), because the Vulkan spec discourages but does not forbid misses at shared edges/vertices.
- No failures and at least one quality warning yields `QP_TEST_RESULT_QUALITY_WARNING`. No failures and no warnings yields `pass`.

## Behavior Parameter Identification

> **Behavior parameter:** `test variant` (the direct child of `watertightness`)
>
> **Candidate values:** `0-9` (legacy random fan), `closedFan` (closed fan, single BLAS), `closedFan2` (closed fan, multiple BLASes)

The ten numbered children `0` through `9` share the same mechanism and differ only in the random seed fed to the recursive fan triangulator. They are treated as one behavioral value. `closedFan` and `closedFan2` are distinct because they change the BLAS topology, the result image dimensionality, the any-hit write mechanism, and the validation logic.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `0-9` (legacy random fan) | Crack in the acceleration structure traversal: a ray that should hit a triangle in the fan misses it, typically at a shared edge or vertex. The any-hit writes `1` on hit and the miss shader writes `2` on miss, so any non-`1` pixel is a miss. |
| `closedFan` | Either a crack (ray misses the shared center vertex or shared edge, producing a `10000` quality warning) or a duplicate any-hit invocation (ray hits two adjacent triangles at the shared edge, producing a cell value greater than `1`). The `VK_GEOMETRY_NO_DUPLICATE_ANY_HIT_INVOCATION_BIT_KHR` flag is set, so a duplicate invocation indicates the implementation did not honor the flag or has a watertightness bug. |
| `closedFan2` | Same crack/duplicate mechanisms as `closedFan`, but exercised across multiple bottom-level acceleration structures (one triangle per BLAS, one BLAS per instance). A failure here points to watertightness bugs that appear when shared edges cross instance boundaries, or to `gl_GeometryIndexEXT` reporting a wrong value. |

## Important Variations and Special Cases

- The ten numbered groups `0` through `9` differ only in the random seed `5 * testNdx + 11 * size + baseSeed`. Each group gives a different recursive fan triangulation for the same triangle count, increasing coverage of edge/vertex configurations.
- The triangle count dimension differs between variants: `0-9` use `4, 16, 64, 256, 1024, 4096, 16384, 65536`; `closedFan`/`closedFan2` use `4, 16, 64, 256, 1024`. The closed fan variants stop at `1024` because the closed fan geometry is more regular and the larger counts would not add coverage.
- The `closedFan2` variant creates `squaresGroupCount` hit groups in the pipeline and SBT (one per triangle), even though `traceRayEXT` is called with `sbtRecordOffset = 0` and `sbtRecordStride = 0`. The multiple hit groups exist to exercise SBT sizing with many groups; the same `ahit` shader module is bound to every hit group.
- The `closedFan`/`closedFan2` miss is a quality warning, not a failure. The Vulkan spec discourages misses at shared edges/vertices but does not forbid them, so the test reports `QP_TEST_RESULT_QUALITY_WARNING` instead of failing.
- The legacy fan uses `imageStore` (non-atomic) and therefore cannot detect duplicate hits; it only detects misses. The closed fan variants use `imageAtomicAdd` to detect duplicates.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| `CaseDef` struct | [vktRayTracingWatertightnessTests.cpp#L56-L66](../../../modules/vulkan/ray_tracing/vktRayTracingWatertightnessTests.cpp#L56-L66) | Per-case parameters: width, height, squares/instances/geometry counts, seed, depth, useManyGeometries. |
| `pointInTriangle2D` and `pointFits` | [vktRayTracingWatertightnessTests.cpp#L109-L160](../../../modules/vulkan/ray_tracing/vktRayTracingWatertightnessTests.cpp#L109-L160) | Host-side geometry validation used during recursive fan triangulation to avoid degenerate splits. |
| `RayTracingTestCase::initPrograms` | [vktRayTracingWatertightnessTests.cpp#L316-L443](../../../modules/vulkan/ray_tracing/vktRayTracingWatertightnessTests.cpp#L316-L443) | Generates `ahit`, `miss`, and `rgen` shaders for both `useClosedFan = false` and `useClosedFan = true`. |
| `initBottomAccelerationStructure` (legacy fan) | [vktRayTracingWatertightnessTests.cpp#L472-L550](../../../modules/vulkan/ray_tracing/vktRayTracingWatertightnessTests.cpp#L472-L550) | Recursive random fan triangulation: start from a unit square split into two triangles, then repeatedly pick a random triangle, add a vertex inside it, and split it into three. |
| `initBottomAccelerationStructures` (closed fan) | [vktRayTracingWatertightnessTests.cpp#L552-L644](../../../modules/vulkan/ray_tracing/vktRayTracingWatertightnessTests.cpp#L552-L644) | Closed fan construction: one center vertex plus `squaresGroupCount` perimeter vertices, with `squaresGroupCount` triangles. `useManyGeometries` switches between one BLAS with N geometries and N BLASes with one geometry each. |
| `runTest` | [vktRayTracingWatertightnessTests.cpp#L646-L795](../../../modules/vulkan/ray_tracing/vktRayTracingWatertightnessTests.cpp#L646-L795) | Pipeline/AS/image setup, descriptor update, `cmdTraceRays`, image-to-buffer copyback. |
| `iterate` validation | [vktRayTracingWatertightnessTests.cpp#L820-L868](../../../modules/vulkan/ray_tracing/vktRayTracingWatertightnessTests.cpp#L820-L868) | Host-side pass/fail/quality-warning decision for both variants. |
| `createWatertightnessTests` registration | [vktRayTracingWatertightnessTests.cpp#L872-L938](../../../modules/vulkan/ray_tracing/vktRayTracingWatertightnessTests.cpp#L872-L938) | Registers the 10 numbered groups plus `closedFan` and `closedFan2` with their size sweeps. |
| Common raygen shader helper | [vkRayTracingUtil.cpp#L118-L138](../../../framework/vulkan/vkRayTracingUtil.cpp#L118-L138) | Returns the standard downward-firing raygen shader used by the `0-9` legacy fan cases. |

## Questions / Risk Points for User Audit

- Is the distinction between crack detection (legacy fan, `imageStore`, no-miss only) and duplicate detection (closed fan, `imageAtomicAdd`, no-miss + no-duplicate) clear?
- Is the role of `VK_GEOMETRY_NO_DUPLICATE_ANY_HIT_INVOCATION_BIT_KHR` in the closed fan variants correctly described?
- Is the `closedFan` vs `closedFan2` BLAS topology difference (single BLAS with N geometries vs N BLASes with one geometry each) and the `gl_PrimitiveID` vs `gl_GeometryIndexEXT` switch accurately captured?
- Is the quality-warning semantics for misses in the closed fan variants correct per the Vulkan spec?
- Should the representative walkthrough use the closedFan raygen shader (which targets shared edges/vertices directly) or the legacy fan raygen shader (which is the common helper)?

## Conversion Notes for Final Wiki Rewrite

- The `Background Knowledge` list should distill the watertightness concept, the `VK_GEOMETRY_NO_DUPLICATE_ANY_HIT_INVOCATION_BIT_KHR` flag, and the `gl_PrimitiveID` vs `gl_GeometryIndexEXT` distinction into a brief unordered list.
- The representative walkthrough should use the `closedFan` raygen shader because it is the only shader that directly targets shared edges and vertices. The legacy fan raygen shader is the common helper used by many other tests and adds no watertightness-specific insight.
- The `### Failure Cause Mapping` table above should be copied directly into the final page's `### Failure Cause Mapping`.
- The `### Cause Analysis` should be written fresh, deriving each cause from the test's validation logic: the legacy fan detects misses via `imageStore` color mismatch, and the closed fan variants detect duplicates via `imageAtomicAdd` cell value greater than `1`.
- Source-navigation details (line ranges, function names) should move to the Source Reference Appendix.
- The numbered groups `0-9` should be grouped as one behavioral value in `## Behavior Parameters` because they differ only in random seed.
