# Understanding Brief: `ray_tracing_pipeline.ser`

## One-Sentence Test Purpose

This test checks whether `VK_EXT_ray_tracing_invocation_reorder` (`GL_EXT_shader_invocation_reorder`) correctly preserves ray tracing execution invariants when threads are reordered by hint, by `hitObjectEXT`, or by a combined trace-reorder-execute call, and whether the `hitObjectEXT` API built-ins (record, query, get, execute) report spec-consistent values across built-in, motion, and large-dimension launch shapes.

## Background Knowledge

### Shader invocation reorder (SER)

`VK_EXT_ray_tracing_invocation_reorder` lets a shader invocation ask the implementation to reorder itself relative to other invocations before continuing. Three reorder entry points exist in GLSL (`GL_EXT_shader_invocation_reorder`):

- `reorderThreadEXT(uint hint, uint bits)` reorders by a caller-supplied hint value.
- `reorderThreadEXT(hitObjectEXT hObj)` reorders using the implementation-resident hit object state as the hint.
- `reorderThreadEXT(hitObjectEXT hObj, uint hint, uint bits)` combines both.

A combined form `hitObjectReorderExecuteEXT(hObj, ...)` records the hit object, reorders the thread, and executes the bound shader in one call. `hitObjectTraceReorderExecuteEXT(...)` further folds the trace itself into the same call.

Why it matters here:

- The implementation is free to ignore a hint, but it must not corrupt payload, SBT selection, hit object state, or subgroup semantics across the reorder point.
- The hint is an optimization hint, not a synchronization primitive. Tests must therefore be invariant-based: a correct implementation produces the same observable result with or without reorder.

### `hitObjectEXT` API

`GL_EXT_shader_invocation_reorder` introduces the `hitObjectEXT` opaque type. A hit object records the result of a trace, a miss, or a ray query, and can later be executed, inspected, or used as a reorder hint. Built-in operations tested here include `hitObjectRecordEmptyEXT`, `hitObjectTraceRayEXT`, `hitObjectRecordMissEXT`, `hitObjectRecordFromQueryEXT`, `hitObjectExecuteShaderEXT`, `hitObjectReorderExecuteEXT`, `hitObjectTraceReorderExecuteEXT`, the motion variants, and a large set of property getters (`hitObjectGetRayTMinEXT`, `hitObjectGetInstanceCustomIndexEXT`, `hitObjectGetObjectToWorldEXT`, `hitObjectGetCurrentTimeEXT`, `hitObjectGetShaderBindingTableRecordIndexEXT`, `hitObjectGetShaderRecordBufferHandleEXT`, `hitObjectGetIntersectionTriangleVertexPositionsEXT`, etc.).

### Motion blur and large dimensions

- `VK_NV_ray_tracing_motion_blur` extends acceleration structures with a rest-pose and a moving geometry. `hitObjectTraceRayMotionEXT` accepts a `time` parameter; `hitObjectGetCurrentTimeEXT` reads it back. Motion variants here use `time = 0.25` and shift geometry by +2 in X so that hits land on the right half of the result image.
- Large-dimension cases exercise the reorder hint path with one very large dispatch axis (X=15210, Y=15181, or Z=17233) to stress device limits (`maxImageDimension2D`, `maxRayDispatchInvocationCount`) and any internal tiling or padding in the reorder unit.

## One Concrete Example

Reconstructed raygen for `ray_tracing_pipeline.ser.reorder.reorder_hint_160x91` (per-case body inlined into the shared header emitted by `RayTracingTestCase::initPrograms`):

```glsl
#version 460 core
#extension GL_EXT_ray_tracing : require
#extension GL_EXT_shader_invocation_reorder : require
layout(r32f, set = 0, binding = 0) uniform image2D result;
layout(set = 0, binding = 1) uniform accelerationStructureEXT topLevelAS;
layout(set = 0, binding = 2) buffer StorageBuffer { uint data[]; } storageBuffer;
layout(location = 0) rayPayloadEXT vec4 payload;

void main()
{
  uint  rayFlags         = gl_RayFlagsOpaqueEXT;
  uint  sbtRecordOffset1 = 1;
  uint  sbtRecordStride  = 1;
  uint  missIndex1       = 1;
  uint  cullMask         = 0xFF;
  float tmin             = 0.5f;
  float tmax             = 9.0f;
  vec3  origin           = vec3((float(gl_LaunchIDEXT.x) + 0.5f) / float(gl_LaunchSizeEXT.x),
                                (float(gl_LaunchIDEXT.y) + 0.5f) / float(gl_LaunchSizeEXT.y), 0.0);
  vec3  direct           = vec3(0.0, 0.0, -1.0);

  hitObjectEXT hObj;
  payload = vec4(1,0,0,1);
  hitObjectTraceRayEXT(hObj, topLevelAS, rayFlags, cullMask, sbtRecordOffset1, sbtRecordStride,
                       missIndex1, origin, tmin, direct, tmax, 0);
  // SER hint: reorder by odd/even subgroup invocation; implementation may honor or ignore.
  reorderThreadEXT(gl_SubgroupInvocationID % 2, 1);
  hitObjectExecuteShaderEXT(hObj, 0);
  imageStore(result, ivec2(gl_LaunchIDEXT.xy), payload);
}
```

The matching closest-hit shader (`chit2`, SBT offset 1) writes `payload = vec4(7,0,0,1)`; the matching miss shader (`miss2`, index 1) writes `payload = vec4(11,0,0,1)`. Geometry spans the left half of the launch grid, so left-half rays must observe `7.0f` (hit) and right-half rays must observe `11.0f` (miss) regardless of how the implementation reordered the threads.

## End-to-End Test Flow

```text
[host] choose testType, width, height, depth from the registration loop
[host] checkSupport: require VK_KHR_acceleration_structure, VK_KHR_ray_tracing_pipeline,
       VK_EXT_ray_tracing_invocation_reorder; motion cases additionally require
       VK_NV_ray_tracing_motion_blur; get_tri_vertices requires
       VK_KHR_ray_tracing_position_fetch; query_hitkind_* require SER specVersion >= 2;
       large_dim cases validate against maxImageDimension2D and maxRayDispatchInvocationCount
[host] build BLAS (triangles, or AABB for the procedural cases; motion BLAS adds a second
       vertex set at t=1.0); build TLAS (single instance, custom index 49; +0.5 X shift for
       object_ray_origin / object_to_world / world_to_object cases)
[host] allocate r32f storage image, host-visible readback buffer, 1024-byte storage buffer
[host] compile rgen + chit1 + chit2 + miss1 + miss2 + intersection shaders; build
       RayTracingPipeline with VK_PIPELINE_CREATE_RAY_TRACING_ALLOW_MOTION_BIT_NV when motion
[host] build raygen / hit / miss SBT regions (raygen SBT carries shader-record data
       {10,20,30,40} for the get_sbt_record_handle case)
[host] clear image to (5,5,5,255); transition to GENERAL; bind descriptor set and pipeline
[host] cmdTraceRaysKHR with (width, height, depth)
[device] rgen builds origin from gl_LaunchIDEXT, traces/reorders/executes per testType, writes
         payload-derived or color-derived float into result image at gl_LaunchIDEXT.xy
         (for LARGE_DIM_Z, writes at (x, z))
[host] memory barrier; cmdCopyImageToBuffer into host-visible buffer; invalidate mapped memory
[host] validateBuffer scans every (x,y): left half must equal anyHitValue, right half must
       equal missValue (motion and transform-shifted cases swap the two halves)
[host] for REORDER_WITH_SUBGROUP, validate against the 1024-byte storage buffer instead:
       before/after subgroup reductions must both equal the no-reorder reference
[host] pass if and only if every scanned entry matches within 1e-6 epsilon
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- Inline GLSL raygen shader, per-`testType` body inlined into a shared header (origin/direct/tmin/tmax/flags shared by all cases). Built with `SPIRV_VERSION_1_4` and `failOnUnknownEntryPoint = true`.
- Two closest-hit shaders (`chit1` writes `3.0`, `chit2` writes `7.0`). `chit1` is replaced by a custom hit-object-from-chit shader for `hit_object_from_chit` and `query_from_chit`.
- Two miss shaders (`miss1` writes `4.0`, `miss2` writes `11.0`). `miss1` is replaced by a custom hit-object-from-miss shader for `hit_object_from_miss` and `query_from_miss`.
- One intersection shader for the AABB cases (computes a slab-based ray-AABB test against hard-coded `aabbMin=(0,0,-2)`, `aabbMax=(0.5,1,-1)` and reports intersection with `hitAttr = vec2(111.0, 222.0)`).
- Per-case `GL_EXT_*` extension enables: `GL_EXT_ray_query` (record_from_query and query_hitkind cases), `GL_EXT_ray_tracing_position_fetch` (get_tri_vertices), `GL_NV_ray_tracing_motion_blur` (motion group), `GL_EXT_buffer_reference_uvec2` (get_sbt_record_handle), `GL_EXT_nonuniform_qualifier` (array_nonuniform), `GL_KHR_shader_subgroup_*` (reorder_hint, hobj_hint, execute_hint, large_dim, trace_with_and_without_*).

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `result` (r32f storage image, set 0 binding 0) | yes | yes | written by rgen via `imageStore` | yes, via `cmdCopyImageToBuffer` | Primary observable: one float per launch invocation encodes the test verdict |
| `topLevelAS` (accelerationStructureEXT, set 0 binding 1) | yes | yes | traversed by `hitObjectTraceRayEXT` etc. | no | Drives hit/miss split at the launch grid midpoint |
| `storageBuffer` (uint storage buffer, set 0 binding 2, 1024 bytes) | yes (zeroed) | yes | atomically updated by `REORDER_WITH_SUBGROUP` rgen | yes, via `invalidateMappedMemoryRange` | Holds before/after subgroup reductions for the only non-image validation path |
| Raygen SBT shader-record data `{10,20,30,40}` | yes | yes | read by `hitObjectGetShaderRecordBufferHandleEXT` | indirectly | Lets `get_sbt_record_handle` validate the SBT handle→data path |
| Host-visible readback buffer | yes | yes | destination of `cmdCopyImageToBuffer` | yes | Bridges device image to host validation |
| Motion vertex buffer (6 vec3, device-addressable) | yes (only for motion cases) | yes | read by motion BLAS build | no | Provides the t=1.0 shifted geometry that drives motion hit/miss split |

## What Is Checked

- For all non-subgroup cases: every texel of the r32f result image must equal a host-known expected float within `epsilon = 1e-6f`. Left half of the launch grid corresponds to rays that hit the geometry; right half corresponds to rays that miss. Per-test `anyHitValue` and `missValue` are listed in `validateBuffer`.
- For `REORDER_WITH_SUBGROUP`: the storage buffer must contain matching before-reorder and after-reorder subgroup reductions (`sum`, `min`, `max`, `all`, `shuffleSum`, `ballot`) at offsets `[0..5]` and `[10..15]`. The reference `sum`, `shuffleSum`, and `ballot` are `n*(n-1)/2`, `n*(n-1)/2`, and `n` where `n = width*height`.
- For `LARGE_DIM_Z_HOBJ_HINT`: validation uses `depth` as the image height because the rgen writes at `(x, z)`.
- For motion and transform-shifted cases (`HIT_OBJECT_OBJECT_RAY_ORIGIN`, `HIT_OBJECT_OBJECT_TO_WORLD`, `HIT_OBJECT_WORLD_TO_OBJECT`, `MOTION_TRACERAY`, `MOTION_REORDER_EXECUTE`, `MOTION_REORDER_EXECUTE_HINT`): `anyHitValue` and `missValue` are swapped because the +X shift or the +2 motion shift moves hits to the right half.

## Behavior Parameter Identification

> **Behavior parameter:** intermediate node under `ray_tracing_pipeline.ser` (`builtin_var`, `reorder`, `motion`, `large_dim`)
>
> **Candidate values:** `builtin_var`, `reorder`, `motion`, `large_dim`

Each intermediate node changes *what is being tested* about the SER / hit-object API surface: `builtin_var` exercises the hit-object built-in API surface, `reorder` exercises the reorder entry points and their combined forms, `motion` exercises the motion-blur variants of trace/record/get/trace-reorder-execute, and `large_dim` exercises the reorder-hint path under dispatch dimensions that stress device limits.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `builtin_var` | A `hitObjectEXT` built-in operation (record, trace, miss, query-record, execute, get-property, set-sbt-index, get-attributes, get-tri-vertices, get-sbt-handle) returned a value or invoked a shader that does not match the spec-required hit/miss/geometry state for the current ray. |
| `reorder` | A reorder entry point (`reorderThreadEXT`, `hitObjectReorderExecuteEXT`, `hitObjectTraceReorderExecuteEXT`) corrupted payload, SBT selection, hit object state, or subgroup semantics across the reorder point, or the trace-with-and-without-reorder invariants diverged. |
| `motion` | A motion-blur hit object variant (`hitObjectTraceRayMotionEXT`, `hitObjectRecordMissMotionEXT`, `hitObjectGetCurrentTimeEXT`, `hitObjectTraceMotionReorderExecuteEXT`) reported wrong hit/miss, wrong time, or invoked the wrong SBT entry for the requested `time`. |
| `large_dim` | The reorder-hint path at a large dispatch dimension exceeded or miscomputed against device limits, or hit a tiling/padding/coordinate bug in the reorder or image-write path at extreme launch extents. |

## Important Variations and Special Cases

- `REORDER_WITH_SUBGROUP` is the only case that validates through a storage buffer (not the result image). It performs subgroup reductions before and after `reorderThreadEXT(sid % 2, 1)` and requires both reductions to match the no-reorder reference, isolating reorder-vs-subgroup interaction from image-write correctness.
- `LARGE_DIM_Z_HOBJ_HINT` writes the result image at `(x, z)` rather than `(x, y)`, so the host validation uses `depth` as the image height.
- `HIT_OBJECT_QUERY_HITKIND_AABB` and `HIT_OBJECT_QUERY_HITKIND_TRI` use the 5-argument `hitObjectRecordFromQueryEXT(hObj, rq, sbtIndex, attribLoc, hitKind)` overload and require `VK_EXT_ray_tracing_invocation_reorder` specVersion >= 2. Older implementations skip these cases.
- `HIT_OBJECT_GET_TRI_VERTICES` requires `VK_KHR_ray_tracing_position_fetch` and validates exact triangle vertex positions for two triangle primitives.
- `HIT_OBJECT_GET_SBT_RECORD_HANDLE` uses `GL_EXT_buffer_reference_uvec2` to dereference the SBT handle and read back the `{10,20,30,40}` shader-record data.
- `HIT_OBJECT_FROM_CHIT` / `HIT_OBJECT_FROM_MISS` / `HIT_OBJECT_QUERY_FROM_CHIT` / `HIT_OBJECT_QUERY_FROM_MISS` create hit objects from inside a closest-hit or miss shader rather than from the raygen shader, exercising the SER API from non-raygen stages.
- Motion cases set `VK_ACCELERATION_STRUCTURE_CREATE_MOTION_BIT_NV` on the TLAS, `VK_BUILD_ACCELERATION_STRUCTURE_MOTION_BIT_NV` on the BLAS, and `VK_PIPELINE_CREATE_RAY_TRACING_ALLOW_MOTION_BIT_NV` on the pipeline.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| `HitObjectTestType` enum and name table | [vktRayTracingShaderExecutionReorderTests.cpp#L61-L207](../../../modules/vulkan/ray_tracing/vktRayTracingShaderExecutionReorderTests.cpp#L61-L207) | Defines the 63 test cases and their string names. |
| `TestParams` and `RayTracingSERTestInstance` constructor | [vktRayTracingShaderExecutionReorderTests.cpp#L209-L312](../../../modules/vulkan/ray_tracing/vktRayTracingShaderExecutionReorderTests.cpp#L209-L312) | Sets `m_isMotion` and `m_isAABB` per testType. |
| `RayTracingTestCase::checkSupport` | [vktRayTracingShaderExecutionReorderTests.cpp#L342-L438](../../../modules/vulkan/ray_tracing/vktRayTracingShaderExecutionReorderTests.cpp#L342-L438) | Extension, feature, specVersion, and device-limit gates. |
| `RayTracingTestCase::initPrograms` (rgen bodies) | [vktRayTracingShaderExecutionReorderTests.cpp#L440-L1416](../../../modules/vulkan/ray_tracing/vktRayTracingShaderExecutionReorderTests.cpp#L440-L1416) | Per-testType raygen shader generation; chit/miss/intersection shaders. |
| `RayTracingSERTestInstance::runTest` | [vktRayTracingShaderExecutionReorderTests.cpp#L1794-L2015](../../../modules/vulkan/ray_tracing/vktRayTracingShaderExecutionReorderTests.cpp#L1794-L2015) | Pipeline, SBT, descriptor, image, and dispatch setup. |
| `RayTracingSERTestInstance::validateBuffer` | [vktRayTracingShaderExecutionReorderTests.cpp#L2024-L2242](../../../modules/vulkan/ray_tracing/vktRayTracingShaderExecutionReorderTests.cpp#L2024-L2242) | Per-testType expected values and left/right-half validation. |
| `createShaderExecutionReorderTests` registration | [vktRayTracingShaderExecutionReorderTests.cpp#L2253-L2364](../../../modules/vulkan/ray_tracing/vktRayTracingShaderExecutionReorderTests.cpp#L2253-L2364) | Builds `ser.{builtin_var,reorder,motion,large_dim}` and the per-leaf names. |

## Questions / Risk Points for User Audit

- Is the core test purpose (SER + hitObjectEXT API surface across four intermediate nodes) clear?
- Is the host/device timeline understandable, especially the dual validation path (image vs storage buffer for `REORDER_WITH_SUBGROUP`)?
- Are the bound resources (image, AS, storage buffer, SBT shader-record data, motion vertex buffer) correctly distinguished from generated GLSL artifacts?
- Is the per-testType `anyHitValue`/`missValue` mapping explained at the right depth, without duplicating the full case-by-case table from the source?
- Is the representative walkthrough (`reorder_hint_160x91`) the right default, or should `reorder_subgroup_256x64` or `reorder_hit_object_hint_160x91` be the primary walkthrough?
- Are the motion and large-dimension variations explained only as much as needed?

## Conversion Notes for Final Wiki Rewrite

- Use `reorder.reorder_hint_160x91` as the single representative shader walkthrough; it exercises `reorderThreadEXT(hint, bits)` (the simplest reorder form) over a standard 160x91 launch.
- Distill Background Knowledge into a brief bullet list: SER hint semantics, hitObjectEXT API surface, motion blur, large-dimension limit checking.
- Move the per-testType rgen-body source ranges and `validateBuffer` expected-value mapping into the Source Reference Appendix.
- Carry the `### Failure Cause Mapping` table directly into the final page; write `### Cause Analysis` fresh.
- Keep `Parameter Dimensions and Observed Values` focused on the four intermediate nodes, the launch dimensions, the geometry kind, and the per-test SBT/miss index selection.
- Treat `VK_EXT_ray_tracing_invocation_reorder` as the authoritative extension name (the task header mentioned `VK_EXT_shader_object` / `VK_NV_shader_invocation_reorder`, but the source requires `VK_EXT_ray_tracing_invocation_reorder`; source wins).
- The Vulkan spec chapter files at `external/vulkan-docs/src/chapters/` are not present in this checkout; Background Knowledge and Failure Cause Mapping are grounded in the source-inspected extension semantics instead. Flag this if the user wants spec-page citations added.
