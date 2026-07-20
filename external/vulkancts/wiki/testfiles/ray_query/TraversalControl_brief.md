# Understanding Brief: ray_query traversal_control

## One-Sentence Test Purpose

This test checks whether a ray query's traversal-control operations (`rayQueryConfirmIntersectionEXT` for triangles, `rayQueryGenerateIntersectionEXT` for AABBs, and the omission of both for "skip") report the correct committed intersection type and the correct hit/miss status for a single ray traced from each cell of an 8x8 grid, across every shader stage that can host an inline ray query.

## Background Knowledge

### Candidate and committed intersection states

Traversing a ray query produces two kinds of intersections. A *candidate* is an intersection traversal found but the shader has not yet acted on. A *committed* intersection is the one the shader accepted. A candidate is classified as `gl_RayQueryCandidateIntersectionTriangleEXT` or `gl_RayQueryCandidateIntersectionAABBEXT`; the committed intersection is `gl_RayQueryCommittedIntersectionNoneEXT`, `gl_RayQueryCommittedIntersectionTriangleEXT`, or `gl_RayQueryCommittedIntersectionGeneratedEXT`. The shader inspects these with `rayQueryGetIntersectionTypeEXT(rayQuery, committed)`. These definitions are in the [ray traversal chapter](../../../../vulkan-docs/src/chapters/raytraversal.adoc).

### Confirm/generate/skip controls

For triangles the *only* way to commit a non-opaque candidate is `rayQueryConfirmIntersectionEXT`. For AABBs, where there is no implicit hit point, the shader supplies one with `rayQueryGenerateIntersectionEXT(rq, t)`. If neither is called, the candidate is dropped and the next `proceed` continues. The Vulkan spec calls this "skipping" the intersection. Traversal control tests isolate each behavior:

- `generate_intersection` (triangles): call `rayQueryConfirmIntersectionEXT` after confirming a triangle candidate.
- `generate_intersection` (AABBs): call `rayQueryGenerateIntersectionEXT(rq, 0.5)`.
- `skip_intersection` (triangles): observe a triangle candidate but do not call `confirm`.
- `skip_intersection` (AABBs): observe an AABB candidate but do not call `generate`.

The committed intersection enum value the device reports is the test target for `hitValue.x`; the candidate-found flag is the test target for `hitValue.y`.

### Shader-stage hosting matters

An inline ray query may run in the vertex, tessellation-control, tessellation-evaluation, geometry, fragment, or compute stage, or in any of the ray-tracing pipeline stages (raygen, intersection, any-hit, closest-hit, miss, callable). Each of these stages reaches the commit step differently, so verifying traversal control across all of them catches stage-specific bugs: a driver might correctly commit in rgen but skip the confirm call when the same logic is spliced into an any-hit shader.

### Two result layers: geometry hit/miss and pipeline hit/miss

For graphics and compute stages the shader stores `hitValue.x` (committed type) and `hitValue.y` (candidate-present flag) per result-image cell, where each cell corresponds to one ray origin in the 8x8 grid. For ray-tracing pipeline stages the test passes through `traceRayEXT` first, so `hitValue` is written inside an ahit/closest-hit/miss/intersection/callable shader. The reference image has two layers per cell: `hitValue.x` and `hitValue.y`. Both layers are checked.

The reference image is built by [`GraphicsConfiguration::verifyImage`](../../../modules/vulkan/ray_query/vktRayQueryTraversalControlTests.cpp#L580-L690), [`ComputeConfiguration::verifyImage`](../../../modules/vulkan/ray_query/vktRayQueryTraversalControlTests.cpp#L805-L874), and [`RayTracingConfiguration::verifyImage`](../../../modules/vulkan/ray_query/vktRayQueryTraversalControlTests.cpp#L1123-L1244). Each variant knows where it expects hits/misses depending on the shader under test.

## One Concrete Example

Representative case: `dEQP-VK.ray_query.traversal_control.compute_shader.generate_intersection.triangles`. The compute shader body, reconstructed from [`initPrograms`](../../../modules/vulkan/ray_query/vktRayQueryTraversalControlTests.cpp#L1624-L1646) and the [`STT_GENERATE_INTERSECTION` triangle fragment](../../../modules/vulkan/ray_query/vktRayQueryTraversalControlTests.cpp#L1356-L1375):

```glsl
layout(r32ui, set = 0, binding = 0) uniform uimage3D result;
layout(set = 0, binding = 1) uniform accelerationStructureEXT rqTopLevelAS;

void main()
{
    vec3  origin   = vec3(float(gl_GlobalInvocationID.x) + 0.5,
                          float(gl_GlobalInvocationID.y) + 0.5, 0.5);
    uvec4 hitValue = uvec4(0, 0, 0, 0);

    rayQueryEXT rq;
    rayQueryInitializeEXT(rq, rqTopLevelAS, 0, 0xFF, origin, 0.0, vec3(0.0, 0.0, -1.0), 1.0);

    if (rayQueryProceedEXT(rq))
    {
        if (rayQueryGetIntersectionTypeEXT(rq, false) == gl_RayQueryCandidateIntersectionTriangleEXT)
        {
            hitValue.y = 1;                                  // candidate was a triangle
            rayQueryConfirmIntersectionEXT(rq);              // commit
            rayQueryProceedEXT(rq);
            hitValue.x = rayQueryGetIntersectionTypeEXT(rq, true);  // committed type
        }
    }

    imageStore(result, ivec3(gl_GlobalInvocationID.xy, 0), uvec4(hitValue.x, 0, 0, 0));
    imageStore(result, ivec3(gl_GlobalInvocationID.xy, 1), uvec4(hitValue.y, 0, 0, 0));
}
```

The BLAS holds two triangles covering (1,1)-(width-1, height-1) on a quad, so cells inside `(1..width-2, 1..height-2)` hit and cells on the borders miss. Expected output: for each cell, `result[x,y,0] = 1` (committed type = `gl_RayQueryCommittedIntersectionTriangleEXT`) and `result[x,y,1] = 1` (a candidate was found), or `0,0` on the border cells where traversal finishes without finding a candidate.

For AABBs the BLAS instead holds a single AABB covering the same interior range. With `generate_intersection` the body calls `rayQueryGenerateIntersectionEXT(rq, 0.5)` instead of `rayQueryConfirmIntersectionEXT`, so `hitValue.x` is reported as `gl_RayQueryCommittedIntersectionGeneratedEXT` (2). With `skip_intersection` the body never commits; `hitValue.x` stays at `0` (`CommittedIntersectionNoneEXT`).

## End-to-End Test Flow

```text
[host] choose ShaderSourcePipeline (graphics / compute / ray-tracing), ShaderSourceType (vertex..callable), ShaderTestType (generate/skip), BottomTestType (triangles/aabbs)
[host] require VK_KHR_acceleration_structure + VK_KHR_ray_query feature bits; stage-specific gates (tessellation, geometry, vertex-pipeline-store, ray-tracing-pipeline)
[host] allocate a 3D R32_UINT result image (width=8, height=8, depth=2) and a host-visible readback buffer; clear to 0xFF
[host] build a TLAS over a single BLAS (triangles: two-triangle quad (1..width-1, 1..height-1); AABBs: a single box (1..width-1, 1..height-1))
[host] generate per-stage shader source(s); for the stage under test, splice the per-(bottom,test) ray-query body into the stage wrapper
[host] build the matching pipeline and ShaderBindingTable (ray-tracing case)
[host] record compute commands: 8x8 dispatch (compute), one draw with 4 vertices (graphics), or 8x8 traceRays (ray tracing); bind result image (b0) and TLAS (b1, or b1 + b2 for ray-tracing)
[device] shader runs: rayQueryInitializeEXT + rayQueryProceedEXT + (confirm or generate or skip)
[device] imageStore writes per-cell hitValue.x into layer 0 and hitValue.y into layer 1
[host] vkCmdCopyImageToBuffer into the readback buffer; pipeline barrier into HOST stage; invalidate mapped range
[host] build a per-pipeline reference image (8x8x2) using the per-stage miss/hit pattern
[host] tcu::intThresholdCompare with threshold UVec4(0); pass only when comparison reports no failure
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- Inline GLSL shader source strings, one per stage (vert/tesc/tese/geom/frag/comp/rgen/isect/ahit/chit/miss/call). The stage wrapper is generated by [`initPrograms`](../../../modules/vulkan/ray_query/vktRayQueryTraversalControlTests.cpp#L1348-L1874) and splices a per-(bottomType, shaderTestType) ray-query body assembled at [vktRayQueryTraversalControlTests.cpp:1353](../../../modules/vulkan/ray_query/vktRayQueryTraversalControlTests.cpp#L1353-L1436).
- Pipeline objects (`GraphicsConfiguration::pipeline`, `ComputeConfiguration::pipeline`, `RayTracingConfiguration::rtPipeline`) and shader binding tables for ray-tracing stages.
- A 3D image (`VK_FORMAT_R32_UINT`, 8x8x2) and a host-visible readback buffer.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| result image (`uimage3D`, `r32ui`, set 0 binding 0) | yes | yes | written by `imageStore` | copied to buffer | layer 0 stores committed type, layer 1 stores candidate-found flag |
| TLAS the ray query traces against | yes | yes (b1 in compute/graphics; b2 in ray tracing) | traversed | no | geometry the ray query runs against |
| regular TLAS (ray-tracing case only) | yes | yes (b1) | traversed by `traceRayEXT` | no | drives landing in a hit shader, which then issues an inline ray-query |
| BLAS (triangles or AABBs) | yes | folded into the TLAS | traversed indirectly | no | source of the candidate intersection under test |
| result readback buffer (`TRANSFER_DST`) | yes | yes | `vkCmdCopyImageToBuffer` writes it | yes | host maps it for `tcu::intThresholdCompare` |

## What Is Checked

- The verified outputs are two layers of an 8x8 R32_UINT 3D image.
- The host computes a per-stage reference image of the same shape. For each cell it sets a `missValue` (typically `0,0,0,0`) or a stage-specific `hitValue` such as `(1,0,0,0)` for triangle confirm, `(2,0,0,0)` for AABB generate, `(3,0,0,0)` for a closest-hit payload, `(4,0,0,0)` for miss/ahit-paths without ray-query commit.
- Result is compared with `tcu::intThresholdCompare` using threshold `UVec4(0)` (exact equality on each layer), and the instance passes only when the comparison reports no failure ([vktRayQueryTraversalControlTests.cpp:688](../../../modules/vulkan/ray_query/vktRayQueryTraversalControlTests.cpp#L688-L689), [vktRayQueryTraversalControlTests.cpp:872](../../../modules/vulkan/ray_query/vktRayQueryTraversalControlTests.cpp#L872-L873), [vktRayQueryTraversalControlTests.cpp:1242](../../../modules/vulkan/ray_query/vktRayQueryTraversalControlTests.cpp#L1242-L1243)).

## Behavior Parameter Identification

> **Behavior parameter:** `ShaderTestType` (the traversal-control operation under test: `generate_intersection` vs `skip_intersection`), crossed with `BottomTestType` (triangles vs AABBs) and `ShaderSourcePipeline` + `ShaderSourceType` (graphics / compute / ray-tracing × 12 stages).
>
> **Candidate values:** `generate_intersection.triangles`, `generate_intersection.aabbs`, `skip_intersection.triangles`, `skip_intersection.aabbs`, each iterated across the 12 stages.

The reason `ShaderTestType` is the primary behavioral axis: each value changes which commit call the shader issues (or omits) and which committed type the host expects. The geometry type modifies which commit call is legal (confirm for triangles, generate for AABBs) and the expected committed enum. The shader-source pipeline modifies the verification matrix but does not change the commit semantics.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `generate_intersection.triangles` | `rayQueryConfirmIntersectionEXT` does not commit a triangle candidate as `CommittedIntersectionTriangleEXT`, or the shader-level path that produces a triangle candidate did not run as expected. |
| `generate_intersection.aabbs` | `rayQueryGenerateIntersectionEXT(rq, t)` does not commit an AABB candidate as `CommittedIntersectionGeneratedEXT`, or `t` is not applied. |
| `skip_intersection.triangles` | The driver still commits a triangle intersection after the shader only proceeds, or the committed type is reported as `Triangle` instead of `None`. |
| `skip_intersection.aabbs` | The driver still commits a generated AABB intersection after the shader only proceeds, or `hitValue.x` is non-zero. |

When the failure is specific to a shader stage (graphics vertex vs raytracing miss vs callable, etc.), the same row above applies, with the additional possible cause that the stage-local plumbing (pipeline barriers, SBT entries, descriptor binding for the ray-query TLAS, or callable payload round-trip) does not deliver the ray query's outcome to the result image correctly.

## Important Variations and Special Cases

- **Hit/miss split per stage.** Ray-tracing stages split the 8x8 grid into two halves: top half tests the hit path, bottom half tests the miss path. The reference pattern alternates `hitHit`, `missHit`, `hitMiss`, and `missMiss` over the four quadrants of the image ([vktRayQueryTraversalControlTests.cpp:1214-L1239](../../../modules/vulkan/ray_query/vktRayQueryTraversalControlTests.cpp#L1214-L1239)). Stage-specific routings:

  - `rgen_shader`: `traceRayEXT` itself is the only ray invocation; `hitValue` is set by the hit shaders downstream.
  - `isect_shader`: an inline `isect_*` intersects one AABB geometry (`reportIntersectionEXT`), then runs the inline ray query.
  - `chit_shader`: a fixed `chit` sets `hitValue.y = 3`; the inline ray-query variant must match it.
  - `miss_shader`: a fixed `miss` sets `hitValue.x = 4`; the inline ray-query variant must match it.
  - `ahit_shader`: ahit shader reports the candidates but does not commit; the fixed path leaves `hitValue.x = 4` (`CommittedIntersectionNoneEXT`).
  - `call_shader`: rgen uses `executeCallableEXT(0,0)`; the callable body stores its own `result.hitValue` into `CallValue`; back in rgen, `param.hitValue.x` is written.

- **Two TLAS bindings in ray-tracing stages.** Like [`Builtin.md`](Builtin.md), the ray-tracing variant binds two AS descriptors: b1 for the regular TLAS used by `traceRayEXT`, b2 for the ray-query TLAS the inline query traces against. The hit/miss/closest-hit path takes a different code path than the inline path; a stage-specific failure mode is failing to bind the correct b2.

- **Triangles versus AABBs commit call.** Only `confirm` legal for triangles; only `generate` legal for AABBs. The shader body chooses the right call from the same enum; if the shader and host diverge on `bottomType`, the test still verifies, but the result image values change.

- **Hit-area for graphics stages.** Vertex stores one sample per `gl_VertexIndex`; tesc/tese/geom iterate over the primitive's vertices; frag uses a clipped interior region.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| `TestParams`, enums, constants | [vktRayQueryTraversalControlTests.cpp:61-L98](../../../modules/vulkan/ray_query/vktRayQueryTraversalControlTests.cpp#L61-L98) | Defines per-case parameters, shader-source-pipeline, shader-source-type, shader-test-type, bottom-type. |
| `GraphicsConfiguration::initConfiguration` | [vktRayQueryTraversalControlTests.cpp:244-L543](../../../modules/vulkan/ray_query/vktRayQueryTraversalControlTests.cpp#L244-L543) | Graphics pipeline creation, vertex buffer, framebuffer, the per-stage wrapper selection. |
| `GraphicsConfiguration::verifyImage` | [vktRayQueryTraversalControlTests.cpp:580-L690](../../../modules/vulkan/ray_query/vktRayQueryTraversalControlTests.cpp#L580-L690) | Reference image generator and `tcu::intThresholdCompare` for graphics. |
| `ComputeConfiguration::initConfiguration` / `verifyImage` | [vktRayQueryTraversalControlTests.cpp:734-L803](../../../modules/vulkan/ray_query/vktRayQueryTraversalControlTests.cpp#L734-L803), [L805-L874](../../../modules/vulkan/ray_query/vktRayQueryTraversalControlTests.cpp#L805-L874) | Compute pipeline and reference image generator for compute. |
| `RayTracingConfiguration::initConfiguration` / `verifyImage` | [vktRayQueryTraversalControlTests.cpp:927-L1013](../../../modules/vulkan/ray_query/vktRayQueryTraversalControlTests.cpp#L927-L1013), [L1123-L1244](../../../modules/vulkan/ray_query/vktRayQueryTraversalControlTests.cpp#L1123-L1244) | Ray-tracing pipeline creation and reference image generator for all ray-tracing stages. |
| `initPrograms` (GLSL assembly) | [vktRayQueryTraversalControlTests.cpp:1348-L1874](../../../modules/vulkan/ray_query/vktRayQueryTraversalControlTests.cpp#L1348-L1874) | Per-stage shader wrappers; the four per-(bottom,test) ray-query bodies are spliced into each. |
| Per-(bottom,test) ray-query bodies | [vktRayQueryTraversalControlTests.cpp:1353-L1436](../../../modules/vulkan/ray_query/vktRayQueryTraversalControlTests.cpp#L1353-L1436) | The actual traversal-control bodies; `generate` calls confirm/generate, `skip` calls neither. |
| `RayQueryTraversalControlTestCase::checkSupport` | [vktRayQueryTraversalControlTests.cpp:1297-L1346](../../../modules/vulkan/ray_query/vktRayQueryTraversalControlTests.cpp#L1297-L1346) | Acceleration-structure / ray-query feature gates and stage-specific support gating. |
| `iterate` | [vktRayQueryTraversalControlTests.cpp:1891-L2057](../../../modules/vulkan/ray_query/vktRayQueryTraversalControlTests.cpp#L1891-L2057) | Image + buffer creation, acceleration-structure build, dispatch/draw/trace, copy-back, verification. |
| `createTraversalControlTests` | [vktRayQueryTraversalControlTests.cpp:2061-L2167](../../../modules/vulkan/ray_query/vktRayQueryTraversalControlTests.cpp#L2061-L2167) | Top-level registration; `traversal_control.<shader_source>.<test_type>.<bottom_type>`. |
| Vulkan spec: ray query traversal | [raytraversal.adoc:623](../../../../vulkan-docs/src/chapters/raytraversal.adoc) | Confirm / generate / skip semantics. |

## Questions / Risk Points for User Audit

- Is `compute_shader.generate_intersection.triangles` the right default walkthrough? Compute is the simplest stage wrapper (one invocation per cell, one TLAS binding), but it does not exercise the stage-splicing machinery used by the ray-tracing stages. A user may prefer `rgen_shader.skip_intersection.triangles` to also cover the two-TLAS path.
- Are the four hit-value constants (`0,1,2,3,4`) carrying semantic load beyond the bare `hitValue.x` numeric? Some are committed-intersection enum values; some are arbitrary values written by fixed chit/miss shaders (3,4) to make stage plumbing distinguishable. The brief treats them as numeric tokens, not enum values, because that is how the source distinguishes them.
- Should the page emphasize the stage-splicing arrangements more than the commit-call semantics? The current outline brief emphasizes commit semantics, since that is the spec-defined behavior under test. If auditing suggests otherwise, the page should be reorganized around the 12 stages.

## Conversion Notes for Final Wiki Rewrite

- Use `compute_shader.generate_intersection.triangles` as the default `## Shader Analysis` walkthrough; it is the smallest case that still shows `confirm` and a committed type.
- Brief's `## Background Knowledge` should be condensed into an unordered prerequisite list in the final page (Candidate / committed; confirm / generate / skip; the 12-stage hosting model; the two layers of the result image).
- `### Failure Cause Mapping` table copies verbatim. `### Cause Analysis` is written fresh during the rewrite, grounded only in what the comparison result actually checks (committed type value, candidate-found flag).
- Move per-stage reference-image detail into `## Runtime Execution and Result Checking` as a compact 12-row summary; this keeps the failure analysis focused.
