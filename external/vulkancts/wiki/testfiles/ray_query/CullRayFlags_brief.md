# Understanding Brief: ray_query ray_flags (CullRayFlags)

## One-Sentence Test Purpose

This test checks whether `VK_KHR_ray_query` ray flags (`opacity`, `terminate_on_first_hit`, `face_culling`, `skip_geometry`) produce the spec-required hit/miss pattern when an inline ray query traces a four-square triangle scene or a two-rectangle AABB scene from any of the twelve shader stages that can host a ray query.

## Background Knowledge

### Ray flags and traversal filtering

`rayQueryInitializeEXT` accepts a `rayFlags` argument drawn from the `gl_RayFlags*EXT` set. These flags change what traversal does: some flags force geometry to be treated as opaque or non-opaque regardless of the instance opaque bit; some cull opaque or non-opaque geometry; some cull front- or back-facing triangles; some skip whole geometry types; some terminate traversal after the first committed hit. The implementation must apply every flag exactly as specified. The semantics are defined in the ray traversal chapter (`external/vulkan-docs/src/chapters/raytraversal.adoc`, not vendored in this checkout; the same definitions appear in the `GL_EXT_ray_query` specification).

Why it matters here:
- The test feeds one ray flag at a time into `rayQueryInitializeEXT` and observes whether the implementation's committed-vs-candidate behavior matches the spec-derived expected pattern.
- The expected pattern is computed by `getHitResult` ([vktRayQueryCullRayFlagsTests.cpp:262-L307](../../../modules/vulkan/ray_query/vktRayQueryCullRayFlagsTests.cpp#L262-L307)) from the flag value, the test type, and the bottom geometry type.

### Opaque vs. non-opaque and the candidate/committed distinction

For triangle geometry, traversal reports a candidate intersection that the shader may confirm or skip. The instance `VK_GEOMETRY_INSTANCE_FORCE_OPAQUE_BIT_KHR` or `VK_GEOMETRY_INSTANCE_FORCE_NO_OPAQUE_BIT_KHR` flag overrides the geometry opaque bit. The ray flags `gl_RayFlagsOpaqueEXT` and `gl_RayFlagsNoOpaqueEXT` override both. `gl_RayFlagsCullOpaqueEXT` and `gl_RayFlagsCullNoOpaqueEXT` cull candidates by opacity.

The shader in this test never calls `rayQueryConfirmIntersectionEXT` or `rayQueryGenerateIntersectionEXT`. Instead it exploits the proceed-return contract:
- For opaque geometry the implementation auto-commits a triangle hit during `rayQueryProceedEXT`, so the first `proceed` returns `false` and `rayQueryGetIntersectionTypeEXT(rq, true)` reports `gl_RayQueryCommittedIntersectionTriangleEXT`. The shader writes `hitValue = (2, 2)`.
- For non-opaque geometry the implementation reports a candidate, so the first `proceed` returns `true` and the candidate type is `gl_RayQueryCandidateIntersectionTriangleEXT`. The shader writes `hitValue = (1, 1)`. No commit is issued, so the candidate is dropped.

For AABB geometry the shader uses `rayQueryGetIntersectionCandidateAABBOpaqueEXT` to read the candidate opacity directly and writes `(2, 2)` for opaque or `(1, 1)` for non-opaque.

### Face culling and winding

`gl_RayFlagsCullBackFacingTrianglesEXT` and `gl_RayFlagsCullFrontFacingTrianglesEXT` cull triangles by facing. The test builds four triangle squares whose winding encodes front- or back-facing, so culling one facing removes exactly two of the four squares. AABB geometry has no facing, so the `face_culling` family only registers triangle leaves.

### Skip-geometry flags

`gl_RayFlagsSkipTrianglesEXT` and `gl_RayFlagsSkipAABBEXT` tell traversal to skip an entire geometry type. The `skip_geometry` family registers both flags against both bottom types; when the skip flag matches the bottom geometry, every cell is expected to miss (`hitResult = {0, 0, 0, 0}`).

### Terminate-on-first-hit

`gl_RayFlagsTerminateOnFirstHitEXT` causes traversal to stop after the first committed hit. The test verifies that this flag does not change the candidate-vs-committed pattern from the no-flag baseline; for the four-square scene the expected `hitResult` stays `{2, 1, 2, 1}` because the test's proceed-once shader logic already captures only the first reported candidate or the first auto-commit.

## One Concrete Example

Representative case: `dEQP-VK.ray_query.ray_flags.compute_shader.opacity.triangles.none` (compute stage, triangle geometry, `RF_None` ray flag, `STT_OPACITY` test type).

The four triangle squares are arranged as:

```text
(front, opaque)     (front, non-opaque)
(back,  opaque)     (back,  non-opaque)
```

With `RF_None`, the expected per-square `hitValue.x` is `{2, 1, 2, 1}` ([vktRayQueryCullRayFlagsTests.cpp:265](../../../modules/vulkan/ray_query/vktRayQueryCullRayFlagsTests.cpp#L265)). Opaque squares auto-commit during `proceed` and report `2`; non-opaque squares report a candidate and report `1`. The shader body is the triangle fragment emitted by `initPrograms` ([vktRayQueryCullRayFlagsTests.cpp:1308-L1336](../../../modules/vulkan/ray_query/vktRayQueryCullRayFlagsTests.cpp#L1308-L1336)) spliced into the compute wrapper ([vktRayQueryCullRayFlagsTests.cpp:1602-L1622](../../../modules/vulkan/ray_query/vktRayQueryCullRayFlagsTests.cpp#L1602-L1622)).

## End-to-End Test Flow

```text
[host] choose (shaderSourceType, shaderTestType, bottomType, flag0) from the registration matrix
[host] build the four-square triangle TLAS or the two-rectangle AABB TLAS with per-instance opaque / facing flags
[host] allocate R32_UINT 3D result image (8x8x2) and host-visible readback buffer
[host] write paramBuffer with uvec4(flag0 | flag1, 0, 0, 0)
[host] clear result image to 0xFF, transition to GENERAL
[host] generate per-stage GLSL with the triangle or AABB ray-query body fragment spliced in
[host] build pipeline (graphics / compute / ray-tracing) and dispatch / draw / trace
[device] shader reads rqFlags from paramBuffer, calls rayQueryInitializeEXT with that flag
[device] one proceed call: candidate triangle -> (1,1); no candidate but committed triangle -> (2,2); neither -> (0,0)
[device] imageStore hitValue.x to layer 0 and hitValue.y to layer 1
[host] copyImageToBuffer, invalidate, build reference image from getHitResult
[host] tcu::intThresholdCompare with threshold UVec4(0); pass only if every cell matches
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- Inline GLSL shader source strings, one per `(shaderSourcePipeline, bottomType)` pair. The triangle body fragment and the AABB body fragment are emitted by `initPrograms` ([vktRayQueryCullRayFlagsTests.cpp:1306-L1367](../../../modules/vulkan/ray_query/vktRayQueryCullRayFlagsTests.cpp#L1306-L1367)) and spliced into per-stage wrappers for graphics ([vktRayQueryCullRayFlagsTests.cpp:1370-L1598](../../../modules/vulkan/ray_query/vktRayQueryCullRayFlagsTests.cpp#L1370-L1598)), compute ([vktRayQueryCullRayFlagsTests.cpp:1599-L1623](../../../modules/vulkan/ray_query/vktRayQueryCullRayFlagsTests.cpp#L1599-L1623)), and ray-tracing ([vktRayQueryCullRayFlagsTests.cpp:1624-L1867](../../../modules/vulkan/ray_query/vktRayQueryCullRayFlagsTests.cpp#L1624-L1867)).
- Per-stage pipelines (graphics / compute / ray-tracing) and, for ray-tracing, a shader binding table with up to four groups (rgen, hit, miss, callable).
- The shader build options target `SPIRV_VERSION_1_4` ([vktRayQueryCullRayFlagsTests.cpp:1298](../../../modules/vulkan/ray_query/vktRayQueryCullRayFlagsTests.cpp#L1298)).

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| result storage image (`VK_FORMAT_R32_UINT`, 8x8x2) | yes | yes (descriptor b0) | written by `imageStore` | yes (copy to buffer) | layer 0 = `hitValue.x`, layer 1 = `hitValue.y` |
| ray-query TLAS | yes | yes (descriptor b1 graphics/compute, b2 ray-tracing) | traversed by `rayQueryInitializeEXT` | no | four-square triangle or two-rectangle AABB scene with per-instance opaque / facing flags |
| paramBuffer (`uvec4`) | yes | yes (descriptor b2 graphics/compute, b3 ray-tracing) | read by shader | no | carries `flag0 | flag1` as `rayFlags` |
| regular TLAS (ray-tracing only) | yes | yes (descriptor b1) | traversed by `traceRayEXT` | no | lands the inline query in the chosen ray-tracing stage |
| result readback buffer | yes | yes | copied into by `vkCmdCopyImageToBuffer` | yes | host maps it for `verifyImage` |

## What Is Checked

- For each cell of the 8x8 grid, the shader stores `hitValue.x` to layer 0 and `hitValue.y` to layer 1 of the result image.
- The host `verifyImage` overload builds a reference image from `getHitResult(testParams)` and the per-stage layout (per-vertex for vert, per-primitive-vertex for tesc/tese/geom, per-cell for frag/comp/ray-tracing).
- Comparison uses `tcu::intThresholdCompare` with threshold `UVec4(0)` (exact equality on each layer).
- A case passes only when the comparison reports no failure ([vktRayQueryCullRayFlagsTests.cpp:2102-L2108](../../../modules/vulkan/ray_query/vktRayQueryCullRayFlagsTests.cpp#L2102-L2108)).

## Behavior Parameter Identification

> **Behavior parameter:** `ShaderTestType` (the ray-flag family under test)
>
> **Candidate values:** `opacity`, `terminate_on_first_hit`, `face_culling`, `skip_geometry`

Each value selects a different category of ray flags. The `flag0` dimension enumerates the concrete flag values tested inside each family; it is a configuration axis, not the behavioral axis.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `opacity` | The implementation does not apply `gl_RayFlagsOpaqueEXT`, `gl_RayFlagsNoOpaqueEXT`, `gl_RayFlagsCullOpaqueEXT`, or `gl_RayFlagsCullNoOpaqueEXT` correctly, so the auto-commit vs. candidate-report pattern or the culling pattern deviates from `getHitResult`. |
| `terminate_on_first_hit` | The implementation does not preserve the candidate-vs-committed pattern when `gl_RayFlagsTerminateOnFirstHitEXT` is set, or it terminates before reporting a candidate that should have been reported. |
| `face_culling` | The implementation culls the wrong facing under `gl_RayFlagsCullBackFacingTrianglesEXT` or `gl_RayFlagsCullFrontFacingTrianglesEXT`, or it applies face culling to AABB geometry. |
| `skip_geometry` | The implementation does not skip the entire geometry type when `gl_RayFlagsSkipTrianglesEXT` or `gl_RayFlagsSkipAABBEXT` is set, so cells that should miss report a hit. |

## Important Variations and Special Cases

- **AABB face-culling pruning.** The `face_culling` family registers only triangle leaves. AABBs have no facing, so the AABB `flag` vector is empty ([vktRayQueryCullRayFlagsTests.cpp:2193-L2196](../../../modules/vulkan/ray_query/vktRayQueryCullRayFlagsTests.cpp#L2193-L2196)).
- **Skip-geometry cross-geometry cases.** `skip_geometry` registers `RF_SkipTriangles` and `RF_SkipAABB` against both bottom types. When the skip flag does not match the bottom geometry (for example `RF_SkipTriangles` with AABB geometry), the expected `hitResult` stays at the default `{2, 1, 2, 1}`; only the matching combination produces all-zero ([vktRayQueryCullRayFlagsTests.cpp:295-L302](../../../modules/vulkan/ray_query/vktRayQueryCullRayFlagsTests.cpp#L295-L302)).
- **Per-stage reference image layout.** Vertex, tessellation-control, tessellation-evaluation, and geometry stages write per-vertex or per-primitive-vertex entries; fragment, compute, and ray-tracing stages write per-cell entries. The `verifyImage` overload for each stage builds the matching reference layout ([vktRayQueryCullRayFlagsTests.cpp:679-L749](../../../modules/vulkan/ray_query/vktRayQueryCullRayFlagsTests.cpp#L679-L749)).
- **Ray-tracing two-TLAS binding.** Ray-tracing stages bind the regular TLAS at b1 (for `traceRayEXT`) and the ray-query TLAS at b2 (for `rayQueryInitializeEXT`). They are separate descriptor slots because pipeline tracing and inline ray queries are distinct traversal mechanisms.
- **`RF_SkipClosestHitShader` registered but not exercised.** The `RayFlags` enum defines `RF_SkipClosestHitShader`, but no `ShaderTestType` registers it. It is unused by this test.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| `ShaderTestType` and `RayFlags` enums | [vktRayQueryCullRayFlagsTests.cpp:84-L105](../../../modules/vulkan/ray_query/vktRayQueryCullRayFlagsTests.cpp#L84-L105) | Defines the four flag families and the concrete ray flag values. |
| `getHitResult` | [vktRayQueryCullRayFlagsTests.cpp:262-L307](../../../modules/vulkan/ray_query/vktRayQueryCullRayFlagsTests.cpp#L262-L307) | Computes the expected per-square hit pattern for each `(testType, flag, bottomType)`. |
| Triangle ray-query body fragment | [vktRayQueryCullRayFlagsTests.cpp:1308-L1336](../../../modules/vulkan/ray_query/vktRayQueryCullRayFlagsTests.cpp#L1308-L1336) | The proceed-once candidate-vs-committed logic shared by all stages. |
| AABB ray-query body fragment | [vktRayQueryCullRayFlagsTests.cpp:1339-L1366](../../../modules/vulkan/ray_query/vktRayQueryCullRayFlagsTests.cpp#L1339-L1366) | The candidate-opacity read for AABB geometry. |
| Compute shader wrapper | [vktRayQueryCullRayFlagsTests.cpp:1599-L1623](../../../modules/vulkan/ray_query/vktRayQueryCullRayFlagsTests.cpp#L1599-L1623) | The simplest stage wrapper; one invocation per cell. |
| `checkSupport` | [vktRayQueryCullRayFlagsTests.cpp:1245-L1294](../../../modules/vulkan/ray_query/vktRayQueryCullRayFlagsTests.cpp#L1245-L1294) | Feature gates and per-stage support checks. |
| `iterate` | [vktRayQueryCullRayFlagsTests.cpp:1884-L2108](../../../modules/vulkan/ray_query/vktRayQueryCullRayFlagsTests.cpp#L1884-L2108) | Image / buffer allocation, AS build, dispatch / draw / trace, copy-back, verification. |
| `createCullRayFlagsTests` | [vktRayQueryCullRayFlagsTests.cpp:2112-L2259](../../../modules/vulkan/ray_query/vktRayQueryCullRayFlagsTests.cpp#L2112-L2259) | Top-level registration: `ray_flags.<shader_source>.<test_type>.<bottom_type>.<flag>`. |
| Vulkan spec: ray traversal | [raytraversal.adoc](../../../../vulkan-docs/src/chapters/raytraversal.adoc) | Ray flag semantics and candidate/committed contract. |

## Questions / Risk Points for User Audit

- Is the proceed-once candidate-vs-committed interpretation correct? The shader calls `rayQueryProceedEXT` exactly once and branches on its return value. For opaque geometry the implementation auto-commits during proceed, so the first call returns `false` and the committed-type check fires. For non-opaque geometry the first call returns `true` with a candidate. This matches the expected `hitResult` defaults but should be confirmed against the spec's proceed contract.
- Is `terminate_on_first_hit` correctly described as "no change from baseline"? The expected `hitResult` is identical to the `RF_None` baseline, and the source comment says "all triangles should be hit". The test appears to verify that the flag does not break the normal candidate-vs-committed pattern.
- Should the page document the `RF_SkipClosestHitShader` enum value even though no family registers it? The brief mentions it as an unused special case; the final page can omit it unless the user wants it noted.

## Conversion Notes for Final Wiki Rewrite

- Use `compute_shader.opacity.triangles.none` as the default representative shader walkthrough. It exercises the proceed-once candidate-vs-committed logic with the natural opaque/non-opaque split and uses the simplest stage wrapper.
- Carry the `ShaderTestType` behavior parameter and the Failure Cause Mapping table directly into the final page's `## Behavior Parameters` and `### Failure Cause Mapping` sections.
- Distill the Background Knowledge into a brief unordered list; omit the tutorial-style opacity explanation.
- Keep the four-square scene description in `## Behavior Parameters` as the per-family context.
- Move source-navigation detail to the Source Reference Appendix.
