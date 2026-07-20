# Understanding Brief: ray_tracing_pipeline.linear_swept_spheres

## One-Sentence Test Purpose

This test checks whether a Vulkan implementation that advertises `VK_NV_ray_tracing_linear_swept_spheres` correctly builds, traverses, and reports hits for the two new bottom-level acceleration structure geometry types (standalone spheres and linear swept spheres), across indexing modes, endcap configurations, BLAS copy, ray-query, hit-object, vertex-format, and radius-format choices.

## Background Knowledge

### VK_NV_ray_tracing_linear_swept_spheres geometry types

The extension introduces two new bottom-level acceleration structure geometry types that sit alongside triangles and AABBs:

- `VK_GEOMETRY_TYPE_SPHERES_NV` places standalone sphere primitives. Each vertex defines one sphere center, paired with a per-vertex radius. A ray hits the sphere surface directly.
- `VK_GEOMETRY_TYPE_LINEAR_SWEPT_SPHERES_NV` places capsule-like swept sphere primitives. Each primitive is a segment defined by two endpoint vertices and their radii. The swept surface is the union of all spheres of varying radius whose centers slide along the segment.

Why it matters here:

- The test family registers two direct children (`spheres`, `lss`) that switch between these two geometry types. The shader-side hit classification built-ins (`gl_HitIsSphereNV`, `gl_HitIsLSSNV`) and ray-query equivalents (`rayQueryIsSphereHitNV`, `rayQueryIsLSSHitNV`) change with this choice.
- The pipeline flag `VK_PIPELINE_CREATE_2_RAY_TRACING_ALLOW_SPHERES_AND_LINEAR_SWEPT_SPHERES_BIT_NV` must be set on the ray tracing pipeline or the implementation will not traverse these geometry types.

### LSS indexing modes

The extension defines two indexing modes for linear swept spheres:

- `VK_RAY_TRACING_LSS_INDEXING_MODE_LIST_NV` treats each pair of indices as one independent segment. The index list `{0, 2, 2, 4}` defines two segments: `(0, 2)` and `(2, 4)`.
- `VK_RAY_TRACING_LSS_INDEXING_MODE_SUCCESSIVE_NV` treats the index list as a polyline. The index list `{0, 1, 2, 3}` defines three segments: `(0, 1)`, `(1, 2)`, `(2, 3)`.

Why it matters here:

- The test exercises both modes through the `indexing_mode_list` and `indexing_mode_successive` test type children. The expected hit count changes with the indexing mode because the number of segments produced from the same vertex and index data differs.

### LSS endcaps

An LSS primitive can include or exclude endcap spheres at each segment endpoint:

- With endcaps enabled, the sphere at each endpoint is part of the geometry. A ray that hits the endpoint sphere reports a hit.
- With endcaps disabled, only the swept surface between the endpoints is tested. Rays that would only hit the endpoint sphere miss.

Why it matters here:

- The test registers `endcaps` and `no_endcaps` children. The expected hit count changes because endcaps add hit surfaces at segment endpoints.
- Standalone sphere geometry (`spheres`) always has endcaps effectively enabled (each sphere is a full sphere), so the `no_endcaps` branch is pruned for `spheres`.

### Hit classification built-ins

The extension adds shader built-ins that identify which geometry type was hit:

- `gl_HitIsSphereNV` is true when the hit was on standalone sphere geometry.
- `gl_HitIsLSSNV` is true when the hit was on linear swept sphere geometry.
- `rayQueryIsSphereHitNV` and `rayQueryIsLSSHitNV` are the ray-query equivalents.
- `hitObjectIsSphereHitNV` and `hitObjectIsLSSHitNV` are the hit-object equivalents.

Why it matters here:

- The raygen shader uses these built-ins differently depending on the `useRayQuery` and `useHitObject` flags. When neither is set, the closest-hit shader runs and always sets the payload to 1 on hit. When ray query or hit object is used, the raygen shader itself checks the built-in to decide whether to count the hit.

## One Concrete Example

Take `dEQP-VK.ray_tracing_pipeline.linear_swept_spheres.lss.indexing_mode_list.no_blascopy.endcaps.no_use_ray_query.no_use_hit_object.float3.float`:

- The host builds one bottom-level acceleration structure with `VK_GEOMETRY_TYPE_LINEAR_SWEPT_SPHERES_NV`, 16 vertices, 12 indices in list mode, endcaps enabled, `float3` vertex format (`VK_FORMAT_R32G32B32_SFLOAT`), and `float` radius format (`VK_FORMAT_R32_SFLOAT`).
- The raygen shader defines 12 ray origin positions at `z = 1` that correspond to the first 12 geometry vertices (same `x, y`, different `z`). It loops over those positions and calls `traceRayEXT` in direction `(0, 0, -1)` toward the geometry at `z = -15`.
- The closest-hit shader sets the payload `hitValue = 1`. The miss shader sets `hitValue = 0`. The raygen accumulates `results += hitValue` across the 12 rays.
- The host reads the result buffer, interprets it as `R8G8B8A8_UNORM`, and checks that the red channel equals 6. Six of the twelve rays hit endcap spheres at segment endpoints; the other six rays pass through positions that do not coincide with any swept surface or endcap and miss.

This case is the simplest LSS path: no ray query, no hit object, no BLAS copy, default formats. It exercises the core extension mechanism: building and traversing LSS geometry through the standard `traceRayEXT` pipeline path.

## End-to-End Test Flow

```text
[host] check VK_NV_ray_tracing_linear_swept_spheres and dependent feature support
[host] create custom device with required extensions and features enabled
[host] build ray tracing pipeline with ALLOW_SPHERES_AND_LINEAR_SWEPT_SPHERES flag
[host] build bottom-level acceleration structure:
       - spheres: standalone sphere vertices + radii, optional index buffer
       - lss: LSS vertices + radii + indices (list or successive), optional endcaps
[host] optionally compact-copy the BLAS when doBlasCopy is true
[host] build top-level acceleration structure with one instance referencing the BLAS
[host] allocate result/reference storage buffers (64x64 int entries), clear to 0x01
[host] record command buffer: AS build, descriptor update, bind pipeline, traceRays 64x64x1
[device] raygen loops over 12 (or 5 for no-endcaps) vertex positions, fires rays in -z
[device] closest-hit sets payload 1, miss sets payload 0 (traceRayEXT path)
[device] raygen accumulates hit count, writes results + 0xFF000000 to result buffer
[host] invalidate and read back reference buffer
[host] interpret buffer as R8G8B8A8_UNORM, check red channel against expected hit count
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `rgen` raygen shader. Generated inline by `LinearSweptSpheresTestCase::initPrograms`. The vertex array content, loop count (12 for endcaps, 5 for no-endcaps), and ray dispatch mechanism (`traceRayEXT`, `rayQueryInitializeEXT`, or `hitObjectTraceRayNV`) vary with test parameters. All variants use GLSL 460 with `GL_EXT_ray_tracing`, `GL_EXT_ray_query`, `GL_NV_shader_invocation_reorder`, and `GL_NV_linear_swept_spheres`, compiled with SPIR-V 1.4 build options.
- `chit` closest-hit shader. Sets `hitValue = 1` on every hit. Computes a `cond` boolean from `gl_HitIsSphereNV`/`gl_HitIsLSSNV` but does not use it to gate the write. Only invoked on the `traceRayEXT` path.
- `miss` miss shader. Sets `hitValue = 0`.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Top-level acceleration structure | yes | yes (binding 0) | yes (traversal reads) | no | Holds one instance referencing the BLAS; raygen traces against it |
| Bottom-level acceleration structure | yes | yes (referenced by TLAS) | yes (traversal reads) | no | Holds sphere or LSS geometry; optionally compact-copied when `doBlasCopy` is true |
| Result/reference storage buffer | yes | yes (binding 1, `std430`) | yes (shader writes) | yes (host invalidate + read) | 64x64 int entries; raygen writes accumulated hit count plus `0xFF000000` |
| Shader binding table regions | yes | yes (traceRays argument) | yes (traversal reads) | no | Selects raygen, closest-hit, and miss shader groups |

## What Is Checked

- The host reads the reference buffer (the only buffer traced against in this test; the result buffer is allocated but not traced in the inspected flow).
- The buffer is interpreted as `R8G8B8A8_UNORM` with 64x64 pixels. The red channel of every pixel must equal the expected hit count.
- Expected hit counts depend on geometry type, test type, and endcap configuration:
  - `spheres` with `vertices`: 12 hits.
  - `spheres` with `indices`: 8 hits.
  - `lss` with `indexing_mode_list` and `endcaps`: 6 hits.
  - `lss` with `indexing_mode_successive` and `endcaps`: 10 hits.
  - `lss` with `vertices` and `endcaps`: 12 hits.
  - `lss` with `indexing_mode_list` and `no_endcaps`: 1 hit.
  - `lss` with `indexing_mode_successive` and `no_endcaps`: 3 hits.
- Every pixel is checked independently. Any pixel whose red channel does not match the expected count fails the test.
- Invalid parameter combinations (for example `spheres` with `no_endcaps`) return `QP_TEST_RESULT_NOT_SUPPORTED` at validation time.

## Behavior Parameter Identification

> **Behavior parameter:** `geometry type` (the direct child of `linear_swept_spheres`)
>
> **Candidate values:** `spheres`, `lss`

The geometry type is the primary behavioral axis because it changes what is being tested: standalone sphere geometry versus linear swept sphere geometry. The two values exercise different acceleration structure geometry types, different shader hit-classification built-ins, different valid test-type subsets, and different expected hit-count formulas. All other dimensions (BLAS copy, endcaps, ray query, hit object, vertex format, radius format) are configuration choices that modify how the geometry is built, traversed, or queried, but they do not change the fundamental property being tested.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `spheres` | The implementation incorrectly built, traversed, or reported hits for standalone sphere geometry (`VK_GEOMETRY_TYPE_SPHERES_NV`). The hit count in the result buffer does not match the expected 12 (vertices) or 8 (indices). |
| `lss` | The implementation incorrectly built, traversed, or reported hits for linear swept sphere geometry (`VK_GEOMETRY_TYPE_LINEAR_SWEPT_SPHERES_NV`). The hit count does not match the expected value for the given indexing mode, endcap, and test-type combination. Includes incorrect hit classification by `gl_HitIsLSSNV`, `rayQueryIsLSSHitNV`, or `hitObjectIsLSSHitNV` when those paths are active. |

## Important Variations and Special Cases

- BLAS copy (`blascopy` vs `no_blascopy`): when enabled, the test compact-copies the built BLAS before traversal. This exercises the copy path for the new geometry types.
- Ray query (`use_ray_query` vs `no_use_ray_query`): when enabled, the raygen shader uses `rayQueryEXT` instead of `traceRayEXT`. The hit classification uses `rayQueryIsSphereHitNV` or `rayQueryIsLSSHitNV` instead of the closest-hit shader.
- Hit object (`use_hit_object` vs `no_use_hit_object`): when enabled, the raygen shader uses `hitObjectTraceRayNV` from `GL_NV_shader_invocation_reorder`. The hit classification uses `hitObjectIsSphereHitNV` or `hitObjectIsLSSHitNV`.
- Vertex format (`float3`, `float2`, `half3`, `half2`): controls whether vertex positions are 3D or 2D (with z implied zero) and whether they use 32-bit or 16-bit float. The `float2` and `half2` formats are pruned for LSS without endcaps.
- Radius format (`float`, `half`): controls whether radii use `VK_FORMAT_R32_SFLOAT` or `VK_FORMAT_R16_SFLOAT`.
- The closest-hit shader computes `cond` from `gl_HitIsSphereNV`/`gl_HitIsLSSNV` but always sets `hitValue = 1` regardless. The `cond` variable is effectively dead code on the `traceRayEXT` path. The hit-classification built-ins are only load-bearing on the ray-query and hit-object paths.
- The custom device is created without `VK_KHR_pipeline_library` to verify that the LSS extension works without it.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| `TestParams` struct | [vktRayTracingLinearSweptSpheresTests.cpp#L174-L185](../../../modules/vulkan/ray_tracing/vktRayTracingLinearSweptSpheresTests.cpp#L174-L185) | Per-case parameters: geometry type, test type, BLAS copy, endcaps, ray query, hit object, vertex format, radius format. |
| `checkSupport` | [vktRayTracingLinearSweptSpheresTests.cpp#L747-L768](../../../modules/vulkan/ray_tracing/vktRayTracingLinearSweptSpheresTests.cpp#L747-L768) | Feature checks for acceleration structure, ray tracing pipeline, and LSS extension. |
| `initPrograms` raygen generation | [vktRayTracingLinearSweptSpheresTests.cpp#L770-L921](../../../modules/vulkan/ray_tracing/vktRayTracingLinearSweptSpheresTests.cpp#L770-L921) | Generates the raygen shader with branches for geometry type, endcaps, ray query, and hit object. |
| `initPrograms` closest-hit and miss | [vktRayTracingLinearSweptSpheresTests.cpp#L923-L955](../../../modules/vulkan/ray_tracing/vktRayTracingLinearSweptSpheresTests.cpp#L923-L955) | Generates the closest-hit and miss shaders. |
| `iterate` validation | [vktRayTracingLinearSweptSpheresTests.cpp#L249-L454](../../../modules/vulkan/ray_tracing/vktRayTracingLinearSweptSpheresTests.cpp#L249-L454) | Host-side result checking: expected hit counts for each geometry type, test type, and endcap combination. |
| `SpheresTestInstance::setupAccelerationStructures` | [vktRayTracingLinearSweptSpheresTests.cpp#L506-L568](../../../modules/vulkan/ray_tracing/vktRayTracingLinearSweptSpheresTests.cpp#L506-L568) | Builds sphere BLAS with vertex, radius, and index data. |
| `LSSpheresTestInstance::setupAccelerationStructures` | [vktRayTracingLinearSweptSpheresTests.cpp#L614-L717](../../../modules/vulkan/ray_tracing/vktRayTracingLinearSweptSpheresTests.cpp#L614-L717) | Builds LSS BLAS with vertex, radius, index data, indexing mode, and endcap configuration. |
| `createLinearSweptSpheresTests` registration | [vktRayTracingLinearSweptSpheresTests.cpp#L960-L1149](../../../modules/vulkan/ray_tracing/vktRayTracingLinearSweptSpheresTests.cpp#L960-L1149) | Registers the test hierarchy with pruning rules for invalid combinations. |
| `addSphereGeometry` helper | [vkRayTracingUtil.cpp#L905-L939](../../../framework/vulkan/vkRayTracingUtil.cpp#L905-L939) | Framework helper that creates sphere or LSS geometry with the specified parameters. |

## Questions / Risk Points for User Audit

- Is the distinction between `spheres` (standalone sphere geometry) and `lss` (linear swept sphere geometry) as the primary behavioral axis clear?
- Is the role of the hit-classification built-ins (`gl_HitIsSphereNV`, `gl_HitIsLSSNV`, ray-query and hit-object equivalents) correctly described, including the fact that they are only load-bearing on the ray-query and hit-object paths?
- Are the expected hit counts for all valid combinations of geometry type, test type, and endcaps correctly captured from the source?
- Is the pruning logic (spheres always has endcaps, spheres only supports vertices/indices, lss does not support indices, lss without endcaps does not support float2/half2) accurately described?
- Should the representative walkthrough use the `traceRayEXT` path (simplest, default) or the `use_ray_query` path (exercises `rayQueryIsLSSHitNV`)?

## Conversion Notes for Final Wiki Rewrite

- The `Background Knowledge` list should distill the LSS geometry types, indexing modes, endcaps, and hit-classification built-ins into a brief unordered list.
- The representative walkthrough should use the `traceRayEXT` path for LSS with endcaps and `indexing_mode_list` because it is the simplest path that exercises the core LSS geometry traversal. The ray-query and hit-object variations can be covered in the parameter variation summary.
- The `### Failure Cause Mapping` table above should be copied directly into the final page's `### Failure Cause Mapping`.
- The `### Cause Analysis` should be written fresh, deriving each cause from the test's validation logic: the host checks the red channel of the result buffer against an expected hit count, so a mismatch points to either incorrect geometry building, incorrect traversal, incorrect hit classification, or incorrect BLAS copy.
- Source-navigation details (line ranges, function names) should move to the Source Reference Appendix.
- The `spheres` and `lss` children should each get a `### <value> — <description>` subsection in `## Behavior Parameters`.
