# Understanding Brief: `ray_tracing_pipeline.pipeline_library`

## One-Sentence Test Purpose

This test checks whether a ray tracing pipeline built by linking several pipeline libraries together produces the same rendering output and the same shader-group handles as a pipeline with the same groups built directly, and whether capture/replay handles round-trip through a second pipeline build using saved handles.

## Background Knowledge

### `VK_KHR_pipeline_library` for ray tracing

A pipeline library is a `VkPipeline` created with `VK_PIPELINE_CREATE_LIBRARY_BIT_KHR`. It cannot be bound directly. Instead, it is referenced by another pipeline through `VkPipelineLibraryCreateInfoKHR`. For ray tracing pipelines, each library contributes some shader groups to the final pipeline. The final pipeline is the one bound to a command buffer and used to build shader binding tables.

Why it matters here:

- The test builds a tree of pipeline libraries. The root pipeline links all libraries via `RayTracingPipeline::addLibrary` and is then created with `createPipelineWithLibraries`.
- Each library carries a slice of the closest-hit shaders. The root pipeline carries the raygen and miss shaders plus its own closest-hit shaders, unless `rgenMissInLibrary` is set, in which case raygen and miss live in their own library linked first to the root.

### `VK_EXT_pipeline_library_group_handles`

The `pipelineLibraryGroupHandles` feature lets the implementation expose shader-group handles for the libraries that contribute to a linked pipeline. When the host queries group handles from the root pipeline through `vkGetRayTracingShaderGroupHandlesKHR`, the returned vector contains the handles of every group across every linked library, in the order produced by the library tree flatten.

Why it matters here:

- Non-default `TestType` values query the root pipeline's full handle vector and slice it per-library using `PipelineTree::getGroupOffsets()`, then compare each slice against the handles returned by querying that library directly.
- Capture/replay handles use a separate size and a separate query (`vkGetRayTracingShaderGroupCaptureReplayHandlesKHR`), and the host feeds them back through `setGroupCaptureReplayHandle` when rebuilding the pipeline in replay mode.

### Link-time optimization flags

`VK_EXT_graphics_pipeline_library` introduces `VK_PIPELINE_CREATE_LINK_TIME_OPTIMIZATION_BIT_EXT` and `VK_PIPELINE_CREATE_RETAIN_LINK_TIME_OPTIMIZATION_INFO_BIT_EXT`. The first requests full link-time optimization; the second retains information needed so a future link can still optimize.

Why it matters here:

- `use_link_time_optimizations` cases set the link-time optimization bit, expecting the implementation to optimize across library boundaries.
- `retain_link_time_optimizations` cases set the retain bit, expecting later links to still be able to optimize.

### `VK_KHR_maintenance5`

Maintenance5 introduces `VkPipelineCreateFlags2` and `vkCreateRayTracingPipelinesKHR` variants that take the flags through the new 64-bit flags2 field. The test sets the same create flags through `setCreateFlags2(translateCreateFlag(creationFlags))` when `useMaintenance5` is true.

### Capture/replay feature gate

`rayTracingPipelineShaderGroupHandleCaptureReplay` must be `VK_TRUE` for any case that records or replays capture/replay handles. The test throws `NotSupportedError` otherwise.

## One Concrete Example

Take `ray_tracing_pipeline.pipeline_library.configurations.singlethreaded_compilation.s3_l232`. The library configuration is `{{3, {{0, 2}, {0, 3}, {0, 2}}}, "s3_l232"}`, meaning:

- Root pipeline carries 3 closest-hit shaders plus rgen and miss.
- Three sibling libraries, each child of the root, contribute 2, 3, and 2 closest-hit shaders respectively.
- Total closest-hit groups: 3 + 2 + 3 + 2 = 10.

The host:

1. Builds four `RayTracingPipeline` objects. The root is created without `VK_PIPELINE_CREATE_LIBRARY_BIT_KHR`. The other three get the library bit.
2. Adds the libraries to the root through `rtPipelines[0]->addLibrary(rtPipelines[idx])`.
3. Calls `createPipelineWithLibraries` on the root, which returns the linked `VkPipeline` handles.
4. Builds an 8x8 checkerboard TLAS where each odd `(x + y)` instance is a hit and the instance's `instanceShaderBindingTableRecordOffset` cycles through `0..numShadersUsed - 1`.
5. Traces 8x8 rays, copies the result image back, and compares each pixel against `shaderIdx % numShadersUsed` for hit pixels and `RTPL_MAX_CHIT_SHADER_COUNT = 16` for miss pixels.

Reconstructed rgen shader (from `initPrograms`):

```glsl
#version 460 core
#extension GL_EXT_ray_tracing : require
layout(location = 0) rayPayloadEXT uvec4 hitValue;
layout(r32ui, set = 0, binding = 0) uniform uimage2D result;
layout(set = 0, binding = 1) uniform accelerationStructureEXT topLevelAS;

void main()
{
  float tmin     = 0.0;
  float tmax     = 1.0;
  vec3  origin   = vec3(float(gl_LaunchIDEXT.x) + 0.5f, float(gl_LaunchIDEXT.y) + 0.5f, float(gl_LaunchIDEXT.z + 0.5f));
  vec3  direct   = vec3(0.0, 0.0, -1.0);
  hitValue       = uvec4(17,0,0,0); // RTPL_MAX_CHIT_SHADER_COUNT + 1
  traceRayEXT(topLevelAS, 0, 0xFF, 0, 0, 0, origin, tmin, direct, tmax, 0);
  imageStore(result, ivec2(gl_LaunchIDEXT.xy), hitValue);
}
```

Each `chit<i>` shader writes `uvec4(i, 0, 0, 1)`, so the result image at a hit pixel records which closest-hit group ran. The miss shader writes `uvec4(16, 0, 0, 1)`, the sentinel for "no hit".

## End-to-End Test Flow

```text
[host] choose library configuration (root shader count, library tree) and test type
[host] build the helper PipelineTree that flattens library group offsets in the final pipeline
[host] create one RayTracingPipeline per node; non-root nodes get VK_PIPELINE_CREATE_LIBRARY_BIT_KHR
[host] set capture/replay bit on every pipeline when test type includes capture replay
[host] set link-time optimization or retain bit when useLinkTimeOptimizations is on
[host] set CreateFlags2 instead of CreateFlags when useMaintenance5 is on
[host] add rgen and miss shaders to the root pipeline (unless rgenMissInLibrary, then to a separate
       library linked to the root first)
[host] add the configured closest-hit shaders to each pipeline node
[host] single-threaded or multi-threaded compile of all shaders; DHO may be set for deferred
       pipeline compilation
[host] link libraries into a tree through addLibrary; create the root pipeline through
       createPipelineWithLibraries
[host] if test type != DEFAULT, query the full shader-group handle vector from the root pipeline,
       then for each library compare its slice of that vector against the handles queried from
       that library alone
[host] if test type includes capture replay: save the capture/replay handle vector; rebuild all
       pipelines with the saved handles fed back through setGroupCaptureReplayHandle; query the
       new full vector and compare against the saved one
[host] build the 8x8 checkerboard BLAS/TLAS, with each odd (x+y) cell holding one instance whose
       instanceShaderBindingTableRecordOffset cycles through 0..numShadersUsed-1
[host] build the SBT from the root pipeline (raygen, miss, hit groups)
[host] cmdTraceRays over 8x8x1, copy result image to host-visible buffer
[host] for each pixel, compare against (shaderIdx % numShadersUsed) for hits and 16 for misses;
       also verify the replay result vector equals the original result vector when replay ran
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- Inline GLSL `rgen` shader. One per test case. Bound at group 0 of the root pipeline.
- Inline GLSL `miss` shader writing `uvec4(16,0,0,1)`. Bound at group 1 of the root pipeline (or group 1 of the rgen/miss library when `rgenMissInLibrary` is set).
- Inline GLSL `chit<i>` shader for `i` in `[0..15]`. Each writes `uvec4(i,0,0,1)`. The shaders used by a given case are selected based on `shaderOffset + i` so each library gets its own slot indices. There are always 16 chit modules generated, but only `getHitGroupCount()` are actually added to the pipeline.
- Inline GLSL `isec` shader used only when `useAABBs` is set. It calls `reportIntersectionEXT(gl_RayTminEXT, 0)`. Added alongside each chit group as the intersection stage.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Result storage image (`r32ui`, 8x8) | yes | yes (binding 0) | written by rgen via `imageStore` | copied to host-visible buffer | Carries per-pixel closest-hit index back to the host for comparison. |
| Top-level acceleration structure | yes | yes (binding 1) | read by rgen via `traceRayEXT` | no | Provides the checkerboard of instances whose `instanceShaderBindingTableRecordOffset` cycles through the available hit groups. |
| Bottom-level acceleration structures | yes (one per odd `(x+y)` cell) | yes (referenced by TLAS) | read by `traceRayEXT` traversal | no | Provide the geometry that the rays hit. AABB geometries are used when `useAABBs` is set; otherwise two triangles per cell. |
| Raygen SBT buffer | yes | yes (raygen region) | read by `traceRayEXT` fixed function | no | Single record holding the rgen group handle. |
| Miss SBT buffer | yes | yes (miss region) | read by `traceRayEXT` fixed function | no | Single record holding the miss group handle. |
| Hit SBT buffer | yes | yes (hit region) | read by `traceRayEXT` fixed function | no | One record per closest-hit group; stride is `shaderGroupHandleSize`. |
| Capture/replay handle vector (in-memory on host) | yes when test type includes capture replay | no (host-side only) | no | used to feed replay pipeline creation and to compare against the replayed query | Saves the handles from the first run; the second run rebuilds pipelines with these handles and verifies they round-trip exactly. |

## What Is Checked

- **Rendering correctness.** For each pixel of the 8x8 result image, the stored `uvec4.x` value must equal `shaderIdx % numShadersUsed` for hit pixels (where `shaderIdx` increments per hit pixel) and `RTPL_MAX_CHIT_SHADER_COUNT = 16` for miss pixels. The host counts failures and reports `failures=N` if any pixel mismatches.
- **Normal shader-group handle slice consistency.** For non-default test types, the full handle vector queried from the root pipeline is sliced per-library according to `PipelineTree::getGroupOffsets()`. Each slice must equal the handle vector queried from that library alone. A mismatch fails with `"Shader Group Handle verification failed for pipeline <idx>"`.
- **Capture/replay handle round-trip.** When the test type includes capture replay, the saved capture/replay handle vector must equal the vector queried from the rebuilt pipeline. A mismatch fails with `"Capture Replay Shader Group Handles do not match creation handles for top-level pipeline"`.
- **Replay rendering consistency.** When the test type includes capture replay, the second-run result vector must equal the first-run result vector. A mismatch fails with `"Replay results differ from original results"`.

## Behavior Parameter Identification

> **Behavior parameter:** `TestType` (the registered test-type axis encoded in the leaf name suffix)
>
> **Candidate values:** `DEFAULT` (no suffix), `CHECK_GROUP_HANDLES` (`_check_group_handles`), `CHECK_CAPTURE_REPLAY_HANDLES` (`_check_capture_replay_handles`), `CHECK_ALL_HANDLES` (`_check_all_handles`)

The other registered dimensions (library configuration, geometry type, compilation mode, `misc` flag variants, `rgen_miss_in_library`) change how the pipeline is built or which geometry it traces against, but they do not change what is being verified. `TestType` is the only axis that changes the verification scope: rendering only, rendering plus normal handle slice consistency, rendering plus capture/replay round-trip, or all of the above.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `DEFAULT` (no suffix) | The implementation linked the pipeline libraries into a working ray tracing pipeline that produced a wrong closest-hit index for at least one pixel, or dispatched the wrong SBT slot. Likely causes are incorrect library group ordering when flattening the linked pipeline, intersection shaders not firing when rgen/miss live in a library, or pipeline-creation flag handling that drops shader groups. |
| `CHECK_GROUP_HANDLES` (`_check_group_handles`) | The implementation returned a per-library handle slice from the root pipeline's full handle vector that does not equal the handles queried from that library alone. Likely causes are incorrect group-offset accounting when libraries are linked, handle reordering across library boundaries, or `pipelineLibraryGroupHandles` returning stale or remapped handles. |
| `CHECK_CAPTURE_REPLAY_HANDLES` (`_check_capture_replay_handles`) | The capture/replay handles saved from the first pipeline build did not match the handles returned by the replayed pipeline, or the replayed pipeline produced a different rendering result. Likely causes are non-deterministic capture/replay handle generation, the implementation ignoring `setGroupCaptureReplayHandle` data during replay, or replay-pipeline shader groups being laid out differently from the original. |
| `CHECK_ALL_HANDLES` (`_check_all_handles`) | Either the normal handle slice check failed, the capture/replay handle round-trip failed, or the replayed rendering differs from the original. Causes are the union of the `CHECK_GROUP_HANDLES` and `CHECK_CAPTURE_REPLAY_HANDLES` causes. |

All four values also share the rendering correctness check, so a `DEFAULT`-style rendering failure can surface under any of them.

## Important Variations and Special Cases

- **Library tree shapes.** Twelve `LibraryConfiguration` entries vary the root shader count and the library tree: flat libraries (`s0_l1`, `s3_l11`), nested libraries where a library is the child of another library (`s0_l1_l1`, `s3_l2_l3`), and wider trees (`s3_l22_l22`, `s3_l232`). The point is to exercise different `PipelineTree` flattenings.
- **`rgen_miss_in_library`.** A separate subfamily places rgen and miss in their own library linked to the root before any hit-group library. This targets a driver bug where intersection shaders were never invoked when rgen/miss lived in a library and hit groups (with intersection) lived in other libraries. The subfamily uses only AABB geometries or triangle geometries and the `DEFAULT` test type.
- **Multi-threaded compilation and DHO.** `multithreaded_compilation` compiles shaders for each pipeline node on separate host threads. `multithreaded_compilation_dho` additionally sets `setDeferredOperation(true)`, asking the implementation to defer pipeline compilation.
- **`misc` subfamily.** Three leaves: `maintenance5` (use `VkPipelineCreateFlags2` via `VK_KHR_maintenance5`), `use_link_time_optimizations` (set `VK_PIPELINE_CREATE_LINK_TIME_OPTIMIZATION_BIT_EXT`), `retain_link_time_optimizations` (set `VK_PIPELINE_CREATE_RETAIN_LINK_TIME_OPTIMIZATION_INFO_BIT_EXT`). These exercise alternative pipeline-creation paths with a fixed library configuration.
- **AABB geometry.** The `_aabbs` suffix swaps triangle BLAS geometries for AABB geometries and adds an intersection shader to every closest-hit group. The intersection shader calls `reportIntersectionEXT(gl_RayTminEXT, 0)` so any ray whose AABB overlaps the cell reports a hit at `t = gl_RayTminEXT`.
- **Capture/replay feature gate.** Any case whose `TestType` includes capture replay requires `rayTracingPipelineShaderGroupHandleCaptureReplay == VK_TRUE`. The test throws `NotSupportedError` if the feature is missing.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Category root registration | [vktRayTracingPipelineLibraryTests.cpp#L1225-L1232](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L1225-L1232) | Builds the `pipeline_library` group and attaches the `configurations` child. |
| `TestParams` struct | [vktRayTracingPipelineLibraryTests.cpp#L76-L107](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L76-L107) | Captures library configuration, compilation flags, test type, geometry, maintenance5, link-time optimization, rgen-miss-in-library, and image dimensions. |
| `PipelineTree` helper | [vktRayTracingPipelineLibraryTests.cpp#L111-L226](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L111-L226) | Flattens the library tree into per-pipeline group offsets used for handle slicing. |
| `checkSupport` gates | [vktRayTracingPipelineLibraryTests.cpp#L298-L318](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L298-L318) | Feature gates for `VK_EXT_pipeline_library_group_handles`, `VK_EXT_graphics_pipeline_library`, `VK_KHR_maintenance5`, and the capture/replay feature. |
| `initPrograms` shader generation | [vktRayTracingPipelineLibraryTests.cpp#L320-L393](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L320-L393) | Generates the rgen, miss, chit, and isec shaders. |
| `runTest` pipeline construction | [vktRayTracingPipelineLibraryTests.cpp#L615-L866](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L615-L866) | Builds the library tree, sets creation flags, links libraries, creates the root pipeline, and runs the handle verification. |
| Rendering dispatch and copyback | [vktRayTracingPipelineLibraryTests.cpp#L868-L983](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L868-L983) | Builds SBT, traces rays, copies result image back. |
| `iterate` pass/fail decision | [vktRayTracingPipelineLibraryTests.cpp#L985-L1025](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L985-L1025) | Runs the test, runs replay when applicable, scans the result image against the expected pattern. |
| Library configuration table | [vktRayTracingPipelineLibraryTests.cpp#L1042-L1067](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L1042-L1067) | Defines the 12 library configurations used by the matrix. |
| Test-type and geometry suffix table | [vktRayTracingPipelineLibraryTests.cpp#L1069-L1087](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L1069-L1087) | Maps `TestType` and `useAABBs` to leaf-name suffixes. |
| `misc` and `rgen_miss_in_library` subfamilies | [vktRayTracingPipelineLibraryTests.cpp#L1122-L1222](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L1122-L1222) | Defines the maintenance5, link-time-optimization, retain-link-time-optimization, and rgen/miss-in-library leaves. |

## Questions / Risk Points for User Audit

- Is the `TestType` axis the right primary behavioral axis? The other registered dimensions (library configuration, geometry, compilation mode, misc, rgen_miss_in_library) change how the pipeline is built but not what is verified. `TestType` is the only axis that changes the verification scope. Confirm this matches the reader's mental model.
- Is the capture/replay flow description accurate? The test saves the full capture/replay handle vector from the first run, rebuilds every pipeline with `setGroupCaptureReplayHandle` feeding the saved bytes back, then queries the new full vector and compares. Confirm this matches the spec's intended capture/replay usage.
- Is the `rgen_miss_in_library` description accurate? The test places rgen and miss in a separate library linked to the root before any hit-group library, so their group indices (0 and 1) appear before the hit groups in the flattened pipeline. Confirm this matches the source intent and the driver bug it targets.
- Are the library tree shapes correctly described? `LibraryConfiguration::pipelineLibraries` is a vector of `(parentID, shaderCount)` pairs. `parentID = 0` means the library is a child of the root; `parentID = 1` means it is a child of the first library. Confirm this matches the reader's reading of `addNode`.

## Conversion Notes for Final Wiki Rewrite

- The brief's `Background Knowledge` distills into a short list of page-specific prerequisites: `VK_KHR_pipeline_library` for ray tracing, `VK_EXT_pipeline_library_group_handles` for handle slicing, capture/replay feature gate, link-time optimization flags, and maintenance5 flags2.
- The representative walkthrough uses the `rgen` shader for the simplest case `ray_tracing_pipeline.pipeline_library.configurations.singlethreaded_compilation.s0_l1` (root with 0 chit shaders, one library with 1 chit shader, no handle checks). The rgen shader is shared across all cases; library configuration differences are host-side and covered by the runtime section.
- The brief's source-mapping table compresses into the Source Reference Appendix; line ranges are kept for traceability.
- The `### Failure Cause Mapping` table is copied directly into the final page's `## Failure Meaning` section.
- The library-configuration, geometry, compilation-mode, misc, and rgen-miss-in-library variations belong in `## Parameter Dimensions and Observed Values`, `## Behavior Parameters` (under the `TestType` axis only), and `## Case Pruning` rather than repeated in failure analysis.
- Beginner scaffolding in `One Concrete Example` and `End-to-End Test Flow` is shortened; the final page uses prose and the runtime section instead of `[host]`/`[device]` markers.
