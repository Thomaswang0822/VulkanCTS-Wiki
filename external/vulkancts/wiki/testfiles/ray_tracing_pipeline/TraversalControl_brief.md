# Understanding Brief: ray_tracing_pipeline.traversal_control

## One-Sentence Test Purpose

This test checks whether a ray tracing pipeline honors the any-hit shader's
`ignoreIntersectionEXT`, `terminateRayEXT`, and pass-through behavior, and the intersection
shader's `reportIntersectionEXT` decision, by comparing a two-layer result image against a
reference built from the spec semantics of each operation.

## Background Knowledge

### Ray tracing pipeline hit stages and traversal

A ray tracing pipeline runs a raygen shader, which calls `traceRayEXT`. For each candidate
intersection the runtime discovers, it runs the any-hit shader; after traversal finds the closest
accepted intersection, it runs the closest-hit shader. If no intersection is accepted, it runs the
miss shader. The intersection shader only runs for procedural (AABB) geometry, where the runtime
does not compute intersections itself and the shader must call `reportIntersectionEXT` to declare a
candidate hit. For triangle geometry, fixed-function intersection runs and no intersection shader is
bound.

Why it matters here:

- The test swaps the any-hit shader body and the intersection shader body across cases, so the same
  acceleration structure and ray setup produces different accepted-or-rejected hits depending only
  on the traversal-control instruction under test.
- The two-layer result image separates the any-hit contribution (layer 0, written through
  `hitValue.x`) from the closest-hit contribution (layer 1, written through `hitValue.y`), so a
  single pixel comparison shows which stages ran.

### Traversal-control operations

- `ignoreIntersectionEXT` (`OpIgnoreIntersectionKHR`): terminates the current any-hit invocation and
  discards the candidate intersection. Traversal continues looking for other candidates. Payload
  writes the any-hit shader performed before the call remain visible to later stages.
- `terminateRayEXT` (`OpTerminateRayKHR`): terminates the current any-hit invocation and ends ray
  traversal. The candidate is accepted, so the closest-hit shader runs for it (or the miss shader
  runs if no candidate was accepted). Payload writes before the call remain visible.
- An empty any-hit shader body (pass-through): the candidate is accepted without payload
  modification, traversal continues, and the closest-hit shader runs for the closest accepted hit.
- `reportIntersectionEXT` (`OpReportIntersectionKHR`) inside an intersection shader: declares a
  candidate hit at a given `t` with a hit kind. If the function returns true, the candidate was
  accepted into traversal and the any-hit shader runs for it. An intersection shader that never
  calls `reportIntersectionEXT` produces no candidates, so the ray misses.

### Ray payload sharing

`rayPayloadEXT` in rgen and `rayPayloadInEXT` in ahit/chit/miss refer to the same storage. Writes
in one stage are visible to later stages for the same ray. The rgen initializes the payload to zero,
so any stage that does not write a component leaves it at zero, and a miss shader writing `x` will
overwrite an any-hit's earlier `x` write when the intersection is later ignored and the ray misses.

## One Concrete Example

Reconstructed rgen shader for every case (shared, from `initPrograms`):

```glsl
#version 460 core
#extension GL_EXT_ray_tracing : require
layout(location = 0) rayPayloadEXT uvec4 hitValue;
layout(r32ui, set = 0, binding = 0) uniform uimage3D result;
layout(set = 0, binding = 1) uniform accelerationStructureEXT topLevelAS;

void main()
{
  float tmin   = 0.0;
  float tmax   = 1.0;
  vec3  origin = vec3(float(gl_LaunchIDEXT.x) + 0.5f, float(gl_LaunchIDEXT.y) + 0.5f, 0.5f);
  vec3  direct = vec3(0.0, 0.0, -1.0);
  hitValue     = uvec4(0,0,0,0);
  traceRayEXT(topLevelAS, 0, 0xFF, 0, 0, 0, origin, tmin, direct, tmax, 0);
  imageStore(result, ivec3(gl_LaunchIDEXT.xy, 0), uvec4(hitValue.x, 0, 0, 0));
  imageStore(result, ivec3(gl_LaunchIDEXT.xy, 1), uvec4(hitValue.y, 0, 0, 0));
}
```

Reconstructed `ahit_terminate` any-hit shader (the case under test):

```glsl
#version 460 core
#extension GL_EXT_ray_tracing : require
layout(location = 0) rayPayloadInEXT uvec4 hitValue;
void main()
{
  hitValue.x = 1;
  terminateRayEXT;
  hitValue.x = 2;
}
```

The post-`terminateRayEXT` assignment to `hitValue.x = 2` is unreachable in a conformant
implementation. If layer 0 reads back as `2`, the implementation did not terminate the any-hit
invocation when `terminateRayEXT` executed.

## End-to-End Test Flow

```text
[host] build a single-square bottom-level AS (triangles or AABB) covering the central 6x6 area
[host] build a one-instance top-level AS over that BLAS
[host] build a ray tracing pipeline with rgen + (rint for AABB) + ahit + chit + rmiss, choosing the ahit/rint variant from the test case
[host] build raygen/hit/miss shader binding tables (one entry each)
[host] clear a 2-layer r32ui storage image to 0xFF.. and barrier it to GENERAL
[host] cmdTraceRays over an 8x8 launch
[device] rgen traces one ray per launch invocation straight down -Z through the square
[device] for central pixels: candidate hit -> ahit runs (sets x=1, then ignore/terminate/pass-through) -> chit runs (sets y=3) for accepted hits
[device] for border pixels or ignored-intersection rays: miss runs (sets x=4)
[device] rgen stores hitValue.x to layer 0 and hitValue.y to layer 1
[host] copyImageToBuffer the 2-layer result to a host-visible buffer
[host] build a 2-layer reference image from the per-case expected hit/miss values
[host] intThresholdCompare result against reference; pass iff exact match (zero threshold)
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- Five inline GLSL shader sets, one per `HitShaderTestType`, selected by indexing a name table. Each
  set shares the same rgen, chit, and miss shaders; the ahit and (for AABB cases) rint shader
  differ per case. Built with `SPIRV_VERSION_1_4`.
- A ray tracing pipeline with three shader groups: group 0 = raygen, group 1 = hit (rint + ahit +
  chit for AABB, or ahit + chit for triangles), group 2 = miss.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `result` storage image (r32ui, 8x8x2 3D) | yes | yes (binding 0) | written by rgen via `imageStore` | yes, via `copyImageToBuffer` | Carries the two-layer pass/fail signal: layer 0 = ahit/miss x, layer 1 = chit y |
| `topLevelAS` acceleration structure | yes, built on device | yes (binding 1) | read by `traceRayEXT` | no | Single instance over a single-square BLAS; geometry type varies per case |
| Result buffer (host-visible) | yes | yes | written by copy | yes, invalidated then read | Host reads it for the reference comparison |
| Shader binding tables (raygen, hit, miss) | yes | yes | read by `cmdTraceRays` | no | One entry each, sized to `shaderGroupHandleSize` |

## What Is Checked

- The host builds a 2-layer reference image of size `width x height x 2` (8x8x2).
- Layer 0 holds the expected `hitValue.x` (any-hit or miss contribution). Layer 1 holds the expected
  `hitValue.y` (closest-hit contribution, or 0 when no closest-hit ran).
- Central pixels (x in 1..width-2, y in 1..height-2) are inside the square and expected to hit;
  border pixels are expected to miss.
- The expected per-case values are:

| Case | Layer 0 (x) inside | Layer 1 (y) inside | Border pixels |
|------|--------------------|--------------------|---------------|
| `isect_report_intersection` | 1 (ahit) | 3 (chit) | miss x=4, y=0 |
| `isect_dont_report_intersection` | 4 (miss) | 0 | miss x=4, y=0 |
| `ahit_pass_through` | 0 (initial) | 3 (chit) | miss x=4, y=0 |
| `ahit_ignore_intersection` | 4 (miss overwrites ahit's 1) | 0 | miss x=4, y=0 |
| `ahit_terminate_ray` | 1 (ahit, traversal ends, chit still runs) | 3 (chit) | miss x=4, y=0 |

- Comparison uses `tcu::intThresholdCompare` with a zero UVec4 threshold, so any single-pixel
  mismatch fails the case.

## Behavior Parameter Identification

> **Behavior parameter:** `HitShaderTestType` (the test case leaf under
> `ray_tracing_pipeline.traversal_control`)
>
> **Candidate values:** `isect_report_intersection`, `isect_dont_report_intersection`,
> `ahit_pass_through`, `ahit_ignore_intersection`, `ahit_terminate_ray`

A secondary configuration axis is `BottomTestType` (`triangles` vs `aabbs`), but it changes which
stages are bound, not the traversal-control rule being tested. The intersection-shader cases are
restricted to AABBs because intersection shaders only run for procedural geometry.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `isect_report_intersection` | Intersection shader's `reportIntersectionEXT` call did not produce an accepted candidate, so ahit/chit did not run and the pixel reported miss instead of hit. |
| `isect_dont_report_intersection` | Intersection shader that never calls `reportIntersectionEXT` still produced a candidate hit, so ahit/chit ran instead of miss. |
| `ahit_pass_through` | Empty any-hit shader was treated as ignore, or the closest-hit shader did not run for an accepted candidate. |
| `ahit_ignore_intersection` | `ignoreIntersectionEXT` did not discard the candidate, so closest-hit ran (layer 1 = 3) instead of miss (layer 1 = 0); or the candidate was discarded but the miss shader did not run. |
| `ahit_terminate_ray` | `terminateRayEXT` did not end the any-hit invocation (post-terminate `hitValue.x = 2` executed, layer 0 = 2), or it did not accept the candidate (closest-hit did not run, layer 1 != 3). |

## Important Variations and Special Cases

- The intersection-shader cases (`isect_report_intersection`,
  `isect_dont_report_intersection`) are registered with `onlyAabbTest = true`, so they only generate
  the `aabbs` leaf. The any-hit cases generate both `triangles` and `aabbs` leaves. This is enforced
  in the registration loop and reflected in mustpass.
- For the AABB cases, the intersection shader is bound as part of hit group 1; for triangle cases,
  only ahit and chit are bound to group 1 and no rint shader exists.
- `ahit_terminate_ray` is the only case where the post-control-instruction code is a deliberate
  canary: if it runs, layer 0 reads back `2` instead of `1`. The other cases do not place code after
  the control instruction.
- The rgen initializes the payload to zero, which is why `ahit_pass_through` expects layer 0 = 0:
  the empty any-hit shader does not modify the payload, and there is no other stage that writes `x`
  on a hit path.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| `HitShaderTestType` enum and shader-name table | [vktRayTracingTraversalControlTests.cpp#L59-L67](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L59-L67) | Defines the five behavior parameter values and the per-case shader name selection. |
| Shader-name table per case | [vktRayTracingTraversalControlTests.cpp#L251-L257](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L251-L257) | Maps each `HitShaderTestType` to its rgen/rint/ahit/chit/miss shader names. |
| `initPrograms` GLSL literals | [vktRayTracingTraversalControlTests.cpp#L456-L591](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L456-L591) | Source of the reconstructed walkthrough shaders. |
| `verifyImage` expected-value switch | [vktRayTracingTraversalControlTests.cpp#L322-L384](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L322-L384) | Encodes the per-case reference image semantics. |
| BLAS geometry construction | [vktRayTracingTraversalControlTests.cpp#L187-L229](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L187-L229) | Triangle square vs single AABB. |
| Pipeline and SBT setup | [vktRayTracingTraversalControlTests.cpp#L245-L320](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L245-L320) | Three shader groups, one SBT entry each. |
| `runTest` host flow | [vktRayTracingTraversalControlTests.cpp#L608-L752](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L608-L752) | Resource creation, clear, trace, copyback. |
| Registration loop and `onlyAabbTest` | [vktRayTracingTraversalControlTests.cpp#L766-L813](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L766-L813) | Builds the five test case groups and their triangle/AABB leaves. |
| Support checks | [vktRayTracingTraversalControlTests.cpp#L439-L454](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L439-L454) | `VK_KHR_acceleration_structure` and `VK_KHR_ray_tracing_pipeline` feature gates. |

## Questions / Risk Points for User Audit

- Is the distinction between `terminateRayEXT` (accept candidate, end traversal, chit runs) and
  `ignoreIntersectionEXT` (discard candidate, traversal continues) correctly reflected in the
  expected-value table? The `ahit_terminate_ray` expected values (layer 0 = 1, layer 1 = 3) depend
  on this distinction.
- Is the claim that an intersection shader which never calls `reportIntersectionEXT` produces a miss
  (not a default accepted candidate) grounded in the spec? The `isect_dont_report_intersection`
  expected values depend on it.
- Is the payload-overwrite reasoning for `ahit_ignore_intersection` (miss sets x=4, overwriting
  ahit's x=1) the intended spec behavior? Payload writes from a terminated any-hit invocation remain
  visible to subsequent stages for the same ray.
- Is one representative walkthrough (rgen + `ahit_terminate` any-hit shader) sufficient, or should a
  second walkthrough cover the intersection-shader path for the AABB-only cases?

## Conversion Notes for Final Wiki Rewrite

- Distill the background knowledge into a brief bullet list for the final `## Background Knowledge`
  section; keep the per-operation semantics compact.
- Use the rgen + `ahit_terminate` shaders as the single representative walkthrough, because
  `terminateRayEXT` is the most distinctive traversal-control operation and the post-terminate
  canary makes the pass/fail signal directly observable.
- Move the shader-name table, geometry construction, and SBT setup details to the source appendix.
- Copy the `### Failure Cause Mapping` table directly into the final page's `### Failure Cause
  Mapping`.
- Write `### Cause Analysis` fresh during the rewrite, grounded in the spec semantics above.
- The `isect_dont_report_intersection` and `isect_report_intersection` AABB-only restriction goes in
  `## Case Pruning` as design-based pruning (intersection shaders require procedural geometry).
