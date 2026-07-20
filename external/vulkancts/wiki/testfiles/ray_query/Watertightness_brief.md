# Understanding Brief: ray_query.watertightness

## One-Sentence Test Purpose

This test checks whether `VK_KHR_ray_query` traversal of a heavily subdivided 2D mesh reports at least one hit per pixel ray (`nomiss`) and exactly one hit per pixel ray (`singlehit`), which exposes cracks from missed primitives and duplicate hits from edge-shared geometry.

## Background Knowledge

### Watertightness in ray traversal

A ray tracer is watertight when a ray that should hit a connected mesh never falls through a crack between adjacent primitives, and never double-hits a shared edge. Cracks happen when floating-point triangle intersection rejects a ray that grazes a shared edge or vertex. Duplicate hits happen when both triangles sharing an edge accept the same ray.

Why it matters here:

- The host generates a 2D mesh of triangles or AABBs that fully tiles the unit square, then subdivides it until there are `256 * 256 = 65536` primitives. Every pixel ray (origin at pixel center, direction `(0, 0, -1)`) must hit at least one primitive.
- A driver that drops a candidate at a shared edge produces a `0` in that pixel's count. A driver that accepts both sides of an edge produces a count greater than 1. The `nomiss` and `singlehit` test types separate these two failure modes.

### Ray query candidate and confirmation

For triangle geometry the shader uses `gl_RayFlagsNoOpaqueEXT`, so triangle candidates are not committed automatically. The shader calls `rayQueryConfirmIntersectionEXT` to commit each candidate and increments `count`. For AABB geometry the shader uses `rayFlags = 0` and calls `rayQueryGenerateIntersectionEXT(rayQuery, 0.5f)` to commit a procedural hit at the middle of the candidate interval. Both paths count every candidate that the implementation reports during `rayQueryProceedEXT`.

### Per-pixel result image

The shader writes `count` as `ivec4(count, 0, 0, 0)` into a 3D `r32i` storage image of size `256 x 256 x 1`. The host copies this image back and scans every pixel. `nomiss` requires `count > 0`; `singlehit` requires `count == 1`. The image is `VK_FORMAT_R32_SINT`, so each pixel is one signed `int32`.

## One Concrete Example

The `nomiss.comp.triangles` case reconstructs as the following compute shader (host-generated, source literal at [vktRayQueryWatertightnessTests.cpp:1520-L1584](../../../modules/vulkan/ray_query/vktRayQueryWatertightnessTests.cpp#L1520-L1584) and the compute wrapper at [vktRayQueryWatertightnessTests.cpp:947-L978](../../../modules/vulkan/ray_query/vktRayQueryWatertightnessTests.cpp#L947-L978)):

```glsl
#version 460 core
#extension GL_EXT_ray_query : require
layout(set = 0, binding = 0, r32i) uniform iimage3D result;
layout(set = 0, binding = 1) uniform accelerationStructureEXT rayQueryTopLevelAccelerationStructure;

void main()
{
  ivec3       pos      = ivec3(gl_WorkGroupID);
  ivec3       size     = ivec3(gl_NumWorkGroups);
  uint        rayFlags = gl_RayFlagsNoOpaqueEXT;
  uint        cullMask = 0xFF;
  float       tmin     = 0.0;
  float       tmax     = 9.0;
  vec3        origin   = vec3((float(pos.x) + 0.5f) / float(size.x), (float(pos.y) + 0.5f) / float(size.y), 0.0);
  vec3        direct   = vec3(0.0, 0.0, -1.0);
  uint        count    = 0;
  rayQueryEXT rayQuery;

  rayQueryInitializeEXT(rayQuery, rayQueryTopLevelAccelerationStructure, rayFlags, cullMask, origin, tmin, direct, tmax);

  while(rayQueryProceedEXT(rayQuery))
  {
    if (rayQueryGetIntersectionTypeEXT(rayQuery, false) == gl_RayQueryCandidateIntersectionTriangleEXT)
    {
      rayQueryConfirmIntersectionEXT(rayQuery);
      count++;
    }
  }
  imageStore(result, pos, ivec4(count, 0, 0, 0));
}
```

The host dispatches `256 x 256 x 1` workgroups (one per pixel) and verifies every pixel holds a positive count.

## End-to-End Test Flow

```text
[host] choose TestType (NO_MISS or SINGLE_HIT), GeomType (TRIANGLES or AABBS), shader stage
[host] build a subdivided BLAS of 65536 triangles or AABBs that tile the unit square
[host] wrap BLAS in a single-instance TLAS
[host] create R32_SINT 3D image sized 256x256x1 and a host-visible readback buffer
[host] clear image to zero, transition to GENERAL layout
[host] build descriptor set: b0 = result image (storage), b1 = ray query TLAS
[host] dispatch (compute), draw (graphics), or traceRays (ray tracing) with stage-specific wrapper
[device] per pixel: initialize rayQuery at pixel center, dir = (0,0,-1), tmin=0, tmax=9
[device] proceed loop: for each triangle candidate call rayQueryConfirmIntersectionEXT and count++
                  (or AABB candidate call rayQueryGenerateIntersectionEXT(0.5) and count++)
[device] imageStore result(pos, ivec4(count, 0, 0, 0))
[host] vkCmdCopyImageToBuffer, barrier, invalidateMappedMemoryRange
[host] scan 65536 ints:
         NO_MISS:    failure if any value <= 0
         SINGLE_HIT: failure if any value != 1
[host] return pass/fail
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- Inline GLSL stage wrapper per pipeline family:
  - Graphics (`GraphicsConfiguration::initPrograms`): vert/tesc/tese/geom/frag wrappers that derive `pos` from `gl_VertexIndex`, `gl_InvocationID`, `gl_PrimitiveIDIn`, or `gl_FragCoord`, then call the shared `testFunc(pos, size)` body ([vktRayQueryWatertightnessTests.cpp:393-L672](../../../modules/vulkan/ray_query/vktRayQueryWatertightnessTests.cpp#L393-L672)).
  - Compute (`ComputeConfiguration::initPrograms`): the body above with `pos = gl_WorkGroupID`, `size = gl_NumWorkGroups` ([vktRayQueryWatertightnessTests.cpp:947-L978](../../../modules/vulkan/ray_query/vktRayQueryWatertightnessTests.cpp#L947-L978)).
  - Ray tracing (`RayTracingConfiguration::initPrograms`): rgen wrapper that calls `executeCallableEXT` for `call`, plus the tested stage's body using `gl_LaunchIDEXT`/`gl_LaunchSizeEXT` ([vktRayQueryWatertightnessTests.cpp:1126-L1336](../../../modules/vulkan/ray_query/vktRayQueryWatertightnessTests.cpp#L1126-L1336)).
- Per-`GeomType` shared `testFunc` body emitted by `getShaderBodyText` ([vktRayQueryWatertightnessTests.cpp:1520-L1584](../../../modules/vulkan/ray_query/vktRayQueryWatertightnessTests.cpp#L1520-L1584)). Triangle body uses `gl_RayFlagsNoOpaqueEXT` and `rayQueryConfirmIntersectionEXT`. AABB body uses `rayFlags = 0` and `rayQueryGenerateIntersectionEXT(rq, 0.5f)`.
- Build options: `vk::ShaderBuildOptions(usedVulkanVersion, SPIRV_VERSION_1_4, 0u, true)` ([vktRayQueryWatertightnessTests.cpp:395](../../../modules/vulkan/ray_query/vktRayQueryWatertightnessTests.cpp#L395)).

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `result` 3D image (`VK_FORMAT_R32_SINT`, 256x256x1, usage STORAGE / TRANSFER_SRC / TRANSFER_DST) | yes | yes (descriptor b0) | written by `imageStore` per pixel | yes, via `vkCmdCopyImageToBuffer` | Per-pixel hit count; sole shader-visible output |
| `rayQueryTopLevelAccelerationStructure` (TLAS wrapping the subdivided BLAS) | yes | yes (descriptor b1 for graphics/compute; b2 for ray tracing) | read by `rayQueryInitializeEXT` | no | The traversed scene |
| Subdivided BLAS (65536 triangles or AABBs in a single geometry) | yes, built in `initAccelerationStructures` | yes (referenced by the TLAS instance) | traversed by the ray query | no | The geometry under test |
| Readback buffer (`256*256*4` bytes, host-visible) | yes | yes (TRANSFER_DST) | written by `vkCmdCopyImageToBuffer` | yes | Passes pixel data to the host scan |
| Vertex buffer (graphics and ray tracing paths only) | yes | yes (VERTEX_BUFFER) | read by vertex shader | no | Drives the per-pixel `pos` derivation in graphics/tess/geometry paths |

## What Is Checked

- The device writes one `int32` per pixel into the result image.
- The host scans all 65536 ints.
- `nomiss` fails when any pixel has `count <= 0`. The host counts `failures` and logs a grid of failing cells ([vktRayQueryWatertightnessTests.cpp:1876-L1920](../../../modules/vulkan/ray_query/vktRayQueryWatertightnessTests.cpp#L1876-L1920)).
- `singlehit` fails when any pixel has `count != 1` (where `expectedValue = 1`). The host counts `failures` and logs a grid of failing cells ([vktRayQueryWatertightnessTests.cpp:1928-L1973](../../../modules/vulkan/ray_query/vktRayQueryWatertightnessTests.cpp#L1928-L1973)).
- Pass condition: `failures == 0`.

## Behavior Parameter Identification

> **Behavior parameter:** `TestType` (`nomiss` vs `singlehit`)
>
> **Candidate values:** `nomiss`, `singlehit`

Both values share one shader body (`getShaderBodyText`) and one geometry generator (`TestConfigurationNoMiss::initAccelerationStructures`). The only difference is the host verification rule. `singlehit` inherits the same acceleration-structure setup as `nomiss` ([vktRayQueryWatertightnessTests.cpp:1922-L1926](../../../modules/vulkan/ray_query/vktRayQueryWatertightnessTests.cpp#L1922-L1926)) and overrides only `verify`.

The secondary axes (shader stage and geometry type) are configuration dimensions, not behavior parameters. They change which pipeline runs the same body and which `rayQuery*` calls commit hits, but the watertightness property under test is the same.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `nomiss` | A pixel ray that should hit the subdivided mesh reported zero candidates. Indicates a traversal crack at a shared edge or vertex, a BVH node that drops a primitive, or a confirm step that the driver skipped. |
| `singlehit` | A pixel ray reported more than one confirmed hit. Indicates duplicate-hit at a shared edge, or an over-broad AABB candidate that fires multiple intersections. AABB geometry is pruned from this value because `rayQueryGenerateIntersectionEXT` could legitimately fire more than once across overlapping AABBs. |
| (both values, same pixel pattern) | Stage-specific wrapper or descriptor binding fails to dispatch the body for every pixel, leaving the cleared `0` in place. Affects both `nomiss` and `singlehit` the same way. |

## Important Variations and Special Cases

- **`singlehit` skips AABB geometry.** `rayQueryGenerateIntersectionEXT(rq, 0.5f)` commits a hit at the middle of the AABB candidate. Overlapping AABBs in the subdivided mesh could legitimately produce multiple generated intersections per ray, which is allowed by the spec. Restricting `singlehit` to triangles keeps the test well defined ([vktRayQueryWatertightnessTests.cpp:2333-L2334](../../../modules/vulkan/ray_query/vktRayQueryWatertightnessTests.cpp#L2333-L2334)).
- **Triangle subdivision rule.** `chooseTriangle` rejects candidate triangles whose edge length falls below `MIN_TRIANGLE_EDGE_LENGTH = 1.0f / float(10 * 256 * 256)` or whose area falls below `MIN_TRIANGLE_AREA_SIZE` ([vktRayQueryWatertightnessTests.cpp:1631-L1633](../../../modules/vulkan/ray_query/vktRayQueryWatertightnessTests.cpp#L1631-L1633)). This keeps the generator from emitting sliver triangles that no intersection algorithm could resolve.
- **AABB subdivision rule.** `chooseAABB` rejects AABBs whose X or Y side length is below `MIN_AABB_SIDE_LENGTH = 1e-6f` ([vktRayQueryWatertightnessTests.cpp:1610-L1611](../../../modules/vulkan/ray_query/vktRayQueryWatertightnessTests.cpp#L1610-L1611)).
- **Shared shader body.** Both `nomiss` and `singlehit` use the same `getShaderBodyText` return value. The test type changes only the host scan rule.
- **Random seed.** `randomSeed = baseSeed` from the test context ([vktRayQueryWatertightnessTests.cpp:2253](../../../modules/vulkan/ray_query/vktRayQueryWatertightnessTests.cpp#L2253)). The same seed drives both triangle and AABB subdivision so failures reproduce.
- **`sect` (intersection) stage.** The intersection shader body always calls `reportIntersectionEXT(1.0f, 0)` after the ray query loop, marking the candidate as a hit for the parent traceRays call. The ray-query count is still written to the result image before that.
- **`call` (callable) stage.** The rgen shader calls `executeCallableEXT(0, 0)` and the callable shader runs the ray-query body. The descriptor b1 in this stage is the traceRays TLAS (default geometry), and b2 is the ray-query TLAS.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| `TestType` enum | [vktRayQueryWatertightnessTests.cpp:60-L64](../../../modules/vulkan/ray_query/vktRayQueryWatertightnessTests.cpp#L60-L64) | Defines the behavior parameter values. |
| `GeomType` enum | [vktRayQueryWatertightnessTests.cpp:66-L71](../../../modules/vulkan/ray_query/vktRayQueryWatertightnessTests.cpp#L66-L71) | Defines the geometry-type configuration dimension. |
| `TestConfigurationNoMiss::initAccelerationStructures` | [vktRayQueryWatertightnessTests.cpp:1639-L1874](../../../modules/vulkan/ray_query/vktRayQueryWatertightnessTests.cpp#L1639-L1874) | Builds the subdivided BLAS for both `nomiss` and `singlehit`. |
| `TestConfigurationNoMiss::verify` | [vktRayQueryWatertightnessTests.cpp:1876-L1920](../../../modules/vulkan/ray_query/vktRayQueryWatertightnessTests.cpp#L1876-L1920) | The `nomiss` scan rule. |
| `TestConfigurationSingleHit::verify` | [vktRayQueryWatertightnessTests.cpp:1928-L1973](../../../modules/vulkan/ray_query/vktRayQueryWatertightnessTests.cpp#L1928-L1973) | The `singlehit` scan rule. |
| `getShaderBodyText` | [vktRayQueryWatertightnessTests.cpp:1520-L1584](../../../modules/vulkan/ray_query/vktRayQueryWatertightnessTests.cpp#L1520-L1584) | The shared shader body for triangles and AABBs. |
| `RayQueryBuiltinTestInstance::iterate` | [vktRayQueryWatertightnessTests.cpp:2042-L2128](../../../modules/vulkan/ray_query/vktRayQueryWatertightnessTests.cpp#L2042-L2128) | End-to-end host flow including barriers, copyback, and pass/fail. |
| `createWatertightnessTests` | [vktRayQueryWatertightnessTests.cpp:2251-L2347](../../../modules/vulkan/ray_query/vktRayQueryWatertightnessTests.cpp#L2251-L2347) | Registration: 2 test types x 12 stages x 2 geom types, minus `singlehit x aabbs`. |

## Questions / Risk Points for User Audit

- Is the watertightness framing (cracks versus duplicate hits) the right mental model for the two test types, given that they share one shader body and one geometry generator?
- Is it clear that the behavior parameter is `TestType` even though the test type only changes the host scan rule?
- The `sect` stage injects a `reportIntersectionEXT(1.0f, 0)` after the ray-query body. Is this side effect worth mentioning in the final page, or does it confuse the watertightness story?
- The AABB subdivision produces overlapping AABBs by design (the four children of a split AABB share the central vertex). Does the page need to call this out, or is it enough to mention it under `singlehit x aabbs` pruning?
- The ray tracing pipeline builds a second, default-geometry BLAS/TLAS for the `traceRays` call (used only to drive `rgen` execution). Is this worth mentioning in the runtime section, or does it distract from the ray-query TLAS that the body actually queries?

## Conversion Notes for Final Wiki Rewrite

- The brief's Background Knowledge is too tutorial-heavy for the final page. Distill to a short bullet list: watertightness concept, candidate vs committed intersection, R32_SINT result image.
- Use the `nomiss.comp.triangles` case as the single representative shader walkthrough. Compute is the simplest pipeline, triangles exercise the most common `rayQueryConfirmIntersectionEXT` path, and the shader body is shared with every other stage and geometry combination.
- Carry the `### Failure Cause Mapping` table verbatim into `## Failure Meaning`.
- The brief's "Important Variations and Special Cases" should feed the `## Behavior Parameters` subsections and `## Case Pruning` rather than be copied wholesale.
- Source-mapping table becomes the basis of `## Source Reference Appendix` with the same entries.
