## Overview

**Core question:** When a ray tracing pipeline is built by linking several pipeline libraries together, does the implementation produce the same rendering output and the same per-library shader-group handles as a directly built pipeline with the same groups, and do capture/replay handles round-trip through a second pipeline build that feeds the saved handles back?

- [vktRayTracingPipelineLibraryTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp) implements the `pipeline_library` test family under the `ray_tracing_pipeline` test category.
- The family has one intermediate node, `configurations`, which holds five subgroups: `singlethreaded_compilation`, `multithreaded_compilation`, `multithreaded_compilation_dho`, `misc`, and `rgen_miss_in_library`.
- The core idea is to build a tree of pipeline libraries, link them into a root pipeline, trace rays through the resulting pipeline, and verify both rendering output and (optionally) shader-group handle consistency between the linked pipeline and the libraries that contributed to it.
- The test type axis controls what is verified: rendering only, rendering plus normal handle slice consistency, rendering plus capture/replay round-trip, or all of the above.
- The page explains the library tree shapes, the handle-slicing mechanism, the capture/replay flow, the feature gates, and the failure meaning for each test type.

## Background Knowledge

- **Pipeline libraries for ray tracing.** `VK_KHR_pipeline_library` lets a `VkPipeline` created with `VK_PIPELINE_CREATE_LIBRARY_BIT_KHR` be referenced by another pipeline through `VkPipelineLibraryCreateInfoKHR`. A library cannot be bound directly. For ray tracing pipelines, each library contributes shader groups to the linked pipeline. The linked root pipeline is what gets bound and used to build shader binding tables.
- **`VK_EXT_pipeline_library_group_handles`.** When `pipelineLibraryGroupHandles` is enabled, querying shader-group handles from the linked root pipeline returns the handles of every group across every linked library, in the order produced by the library tree flatten. The test slices that vector per library and compares each slice against handles queried from that library alone.
- **Capture/replay handles.** `rayTracingPipelineShaderGroupHandleCaptureReplay` lets the host save capture/replay handles from a first pipeline build and feed them back through `vkSetRayTracingShaderGroupHandlesKHR` (wrapped here as `setGroupCaptureReplayHandle`) when rebuilding the pipeline. The replayed pipeline must produce the same handles and the same rendering output.
- **Link-time optimization flags.** `VK_EXT_graphics_pipeline_library` adds `VK_PIPELINE_CREATE_LINK_TIME_OPTIMIZATION_BIT_EXT` (request cross-library optimization at link time) and `VK_PIPELINE_CREATE_RETAIN_LINK_TIME_OPTIMIZATION_INFO_BIT_EXT` (retain information so a later link can still optimize).
- **Maintenance5 path.** `VK_KHR_maintenance5` introduces `VkPipelineCreateFlags2`. The test routes the same creation flags through `setCreateFlags2` when `useMaintenance5` is true.
- **Shader binding table layout.** `cmdTraceRaysKHR` reads raygen, miss, hit, and callable regions described by `VkStridedDeviceAddressRegionKHR`. The host builds these regions from the linked root pipeline. Each hit record carries one shader-group handle; the per-instance `instanceShaderBindingTableRecordOffset` selects which record a hit resolves to.

## Registration Hierarchy

```text
ray_tracing_pipeline.pipeline_library
└── configurations
```

The `configurations` intermediate node holds five subgroups observed in mustpass: `singlethreaded_compilation`, `multithreaded_compilation`, `multithreaded_compilation_dho`, `misc`, and `rgen_miss_in_library`. The first three iterate the same library configuration, geometry, and test-type matrix under different compilation modes. `misc` adds `maintenance5`, `use_link_time_optimizations`, and `retain_link_time_optimizations` leaves with a fixed library configuration. `rgen_miss_in_library` iterates a smaller library configuration and geometry matrix with rgen and miss placed in a separate library.

## Parameter Dimensions and Observed Values

The full matrix is built by nested loops in [addPipelineLibraryConfigurationsTests](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L1029-L1168) and the `rgen_miss_in_library` loop in [vktRayTracingPipelineLibraryTests.cpp#L1174-L1222](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L1174-L1222).

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Compilation mode | `singlethreaded_compilation`, `multithreaded_compilation`, `multithreaded_compilation_dho` | Selects how shader modules are added to each pipeline node. `multithreaded_compilation` compiles shaders for each node on separate host threads. `multithreaded_compilation_dho` also sets `setDeferredOperation(true)` to defer pipeline compilation. | [threadData](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L1031-L1040) |
| Library configuration | `s0_l1`, `s1_l1`, `s0_l11`, `s3_l11`, `s0_l23`, `s2_l23`, `s0_l1_l1`, `s1_l1_l1`, `s0_l2_l3`, `s3_l2_l3`, `s3_l232`, `s3_l22_l22` | Encodes the root pipeline's chit shader count and the library tree. Each `s<N>_l<M>` token means N chit shaders in the root and a library subtree described by the `l` suffix. Nested suffixes like `l_l` mean a library is a child of another library. | [libraryConfigurationData](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L1042-L1067) |
| Test type | (no suffix), `_check_group_handles`, `_check_capture_replay_handles`, `_check_all_handles` | The primary behavioral axis. Controls what is verified: rendering only, rendering plus normal handle slice consistency, rendering plus capture/replay round-trip, or all of the above. | [testTypeCases](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L1069-L1078) |
| Geometry type | (no suffix), `_aabbs` | Selects triangle BLAS geometries or AABB BLAS geometries. AABB cases add an intersection shader to every closest-hit group. | [geometryTypeCases](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L1080-L1087) |
| `misc` variant | `maintenance5`, `use_link_time_optimizations`, `retain_link_time_optimizations` | Three single leaves that exercise alternative pipeline-creation paths with a fixed library configuration. `maintenance5` uses `VkPipelineCreateFlags2`. The two link-time leaves set the corresponding `VK_EXT_graphics_pipeline_library` flags. | [misc group](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L1122-L1168) |
| `rgen_miss_in_library` variant | `s0_l1`, `s0_l11`, `s0_l23`, `s0_l1_l1`, `s0_l2_l3`, each with `_aabbs` | Places rgen and miss in a separate library linked to the root before any hit-group library. Targets a driver bug where intersection shaders were not invoked when rgen/miss lived in a library. Always uses the `DEFAULT` test type. | [rgen_miss group](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L1174-L1222) |
| Image dimensions | 8x8 (`RTPL_DEFAULT_SIZE`) | Fixed launch size. Half the pixels hit geometry (odd `x + y`); the other half miss. | [RTPL_DEFAULT_SIZE](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L59) |

## Behavior Parameters

The primary behavioral axis is the test type. The other dimensions change how the pipeline is built or which geometry it traces against, but they do not change what is being verified. The test type is the only axis that changes the verification scope.

### DEFAULT — Rendering correctness only

The `DEFAULT` test type verifies that the linked pipeline produces the correct per-pixel closest-hit index. The host traces 8x8 rays through the linked root pipeline, copies the result image back, and compares each pixel against `shaderIdx % numShadersUsed` for hit pixels and `RTPL_MAX_CHIT_SHADER_COUNT = 16` for miss pixels. No shader-group handle queries are performed. This is the only test type used by the `rgen_miss_in_library` subfamily because that subfamily targets a rendering bug, not a handle bug.

### CHECK_GROUP_HANDLES — Rendering plus normal handle slice consistency

The `CHECK_GROUP_HANDLES` test type adds a normal shader-group handle consistency check on top of the rendering check. The host queries the full handle vector from the linked root pipeline using `vkGetRayTracingShaderGroupHandlesKHR`, slices it per library according to `PipelineTree::getGroupOffsets()`, and compares each slice against the handles queried from that library alone. The check requires `VK_EXT_pipeline_library_group_handles`. A mismatch fails with `"Shader Group Handle verification failed for pipeline <idx>"`.

### CHECK_CAPTURE_REPLAY_HANDLES — Rendering plus capture/replay round-trip

The `CHECK_CAPTURE_REPLAY_HANDLES` test type runs the test twice. The first run queries and saves the full capture/replay handle vector. The second run rebuilds every pipeline with `VK_PIPELINE_CREATE_RAY_TRACING_SHADER_GROUP_HANDLE_CAPTURE_REPLAY_BIT_KHR` set and feeds the saved handles back through `setGroupCaptureReplayHandle`. The host then queries the new full capture/replay handle vector and compares it against the saved one. The second run also produces a second result image, which must equal the first. Requires `rayTracingPipelineShaderGroupHandleCaptureReplay == VK_TRUE`. The check also requires `VK_EXT_pipeline_library_group_handles` because the test type is not `DEFAULT`.

### CHECK_ALL_HANDLES — All checks combined

The `CHECK_ALL_HANDLES` test type runs the handle verification loop twice. The first iteration checks normal handles (the `CHECK_GROUP_HANDLES` path). The second iteration checks capture/replay handles (the `CHECK_CAPTURE_REPLAY_HANDLES` path), including the replayed rebuild and the result-vector equality check. Requires both `VK_EXT_pipeline_library_group_handles` and `rayTracingPipelineShaderGroupHandleCaptureReplay == VK_TRUE`.

## Shader Analysis

This page uses one representative walkthrough. The rgen shader is identical across all cases; library configuration, geometry, and test-type differences are host-side and covered by the runtime section. The closest-hit, miss, and intersection shaders write a single constant each, so they do not need separate walkthroughs.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
ray_tracing_pipeline.pipeline_library.configurations.singlethreaded_compilation.s0_l1
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `singlethreaded_compilation` | Shaders are added to each pipeline node sequentially on the host thread. No deferred operations. |
| `s0_l1` | Root pipeline carries 0 closest-hit shaders plus rgen and miss. One library, child of the root, carries 1 closest-hit shader. Total hit groups: 1. |
| No test-type suffix | `DEFAULT` test type. Only rendering correctness is verified. |
| No `_aabbs` suffix | Triangle BLAS geometries. No intersection shader. |

#### Purpose

The rgen shader drives one ray per pixel of the 8x8 result image. Each ray either hits geometry and routes to the closest-hit group selected by the instance's `instanceShaderBindingTableRecordOffset`, or misses and routes to the miss shader. The result image stores which group ran, and the host compares it against the expected pattern.

#### Structural Design

| Step | rgen behavior | Meaning |
|------|---------------|---------|
| 1 | Read `gl_LaunchIDEXT.xy` and convert to a pixel-center origin `(x + 0.5, y + 0.5, z + 0.5)`. | Each of the 8x8 launch invocations traces one ray into the checkerboard. |
| 2 | Initialize `hitValue` to `uvec4(17, 0, 0, 0)`. | The sentinel 17 (`RTPL_MAX_CHIT_SHADER_COUNT + 1`) is never written by any chit or miss shader, so a leftover 17 in the result image would mean no shader ran. |
| 3 | Call `traceRayEXT(topLevelAS, 0, 0xFF, 0, 0, 0, origin, tmin, direct, tmax, 0)`. | `sbtRecordOffset = 0`, `sbtRecordStride = 0`, `missIndex = 0`. The hit group is selected purely by `instanceContributionToHitGroupIndex`. |
| 4 | `imageStore(result, ivec2(gl_LaunchIDEXT.xy), hitValue)`. | Writes the chit-or-miss index back to the result image for host comparison. |

The `chit<i>` shaders write `uvec4(i, 0, 0, 1)` into the ray payload, so the result image at a hit pixel records which closest-hit group ran. The miss shader writes `uvec4(16, 0, 0, 1)`, the sentinel for "no hit".

#### Shader Code

Reconstructed GLSL from the `initPrograms` literal in [vktRayTracingPipelineLibraryTests.cpp#L324-L346](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L324-L346):

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

#### Additional Info

- The `rgen` shader is generated once and reused across all cases. The `updateRayTracingGLSL` post-processing hook rewrites the source for the active Vulkan version.
- The `miss` shader writes `uvec4(16, 0, 0, 1)`, where 16 is `RTPL_MAX_CHIT_SHADER_COUNT`. The host treats 16 as the expected miss value.
- The `chit<i>` shaders for `i` in `[0..15]` write `uvec4(i, 0, 0, 1)`. The test always generates 16 chit modules, but only `getHitGroupCount()` are added to any given pipeline. The `shaderOffset + i` indexing in [pipelineShaders fill](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L717-L722) assigns each library its own slot range.
- The `isec` shader, used only when `useAABBs` is true, calls `reportIntersectionEXT(gl_RayTminEXT, 0)` so any ray whose AABB overlaps the cell reports a hit at `t = gl_RayTminEXT`.

#### Parameter Variation Summary

| Parameter dimension | GLSL-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Library configuration | No GLSL change. The host changes how many chit modules are added to each pipeline node and how the libraries are linked. | [pipelineShaders fill](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L711-L723) |
| Geometry type (`_aabbs`) | No rgen change. The host adds an `isec` shader module alongside each chit module and swaps triangle BLAS geometries for AABB geometries. | [isec generation](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L363-L374) |
| Test type | No GLSL change. The host changes what is verified after the trace: rendering only, normal handles, capture/replay handles, or all. | [handle verification](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L804-L866) |
| Compilation mode | No GLSL change. The host chooses between single-threaded and multi-threaded shader compilation, with or without deferred pipeline creation. | [compileShadersThread](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L729-L750) |
| `misc` link-time variants | No GLSL change. The host sets `VK_PIPELINE_CREATE_LINK_TIME_OPTIMIZATION_BIT_EXT` or `VK_PIPELINE_CREATE_RETAIN_LINK_TIME_OPTIMIZATION_INFO_BIT_EXT` on every pipeline node. | [creation flags](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L695-L701) |
| `misc.maintenance5` | No GLSL change. The host routes the same creation flags through `setCreateFlags2(translateCreateFlag(creationFlags))`. | [maintenance5 flag routing](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L704-L705) |
| `rgen_miss_in_library` | No rgen change. The host moves rgen and miss into a separate library linked to the root before any hit-group library, so their group indices (0 and 1) appear before the hit groups in the flattened pipeline. | [basePipelineLibrary](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L755-L771) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `rgen`
- Target SPIRV version: `spirv1.4`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.4
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 66
; Schema: 0
               OpCapability RayTracingKHR
               OpExtension "SPV_KHR_ray_tracing"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint RayGenerationKHR %main "main" %gl_LaunchIDEXT %hitValue %topLevelAS %result
               OpSource GLSL 460
               OpSourceExtension "GL_EXT_ray_tracing"
               OpName %main "main"
               OpName %tmin "tmin"
               OpName %tmax "tmax"
               OpName %origin "origin"
               OpName %gl_LaunchIDEXT "gl_LaunchIDEXT"
               OpName %direct "direct"
               OpName %hitValue "hitValue"
               OpName %topLevelAS "topLevelAS"
               OpName %result "result"
               OpDecorate %gl_LaunchIDEXT BuiltIn LaunchIdKHR
               OpDecorate %topLevelAS Binding 1
               OpDecorate %topLevelAS DescriptorSet 0
               OpDecorate %result Binding 0
               OpDecorate %result DescriptorSet 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
%_ptr_Function_float = OpTypePointer Function %float
    %float_0 = OpConstant %float 0
    %float_1 = OpConstant %float 1
    %v3float = OpTypeVector %float 3
%_ptr_Function_v3float = OpTypePointer Function %v3float
       %uint = OpTypeInt 32 0
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_LaunchIDEXT = OpVariable %_ptr_Input_v3uint Input
     %uint_0 = OpConstant %uint 0
%_ptr_Input_uint = OpTypePointer Input %uint
  %float_0_5 = OpConstant %float 0.5
     %uint_1 = OpConstant %uint 1
     %uint_2 = OpConstant %uint 2
   %float_n1 = OpConstant %float -1
         %39 = OpConstantComposite %v3float %float_0 %float_0 %float_n1
     %v4uint = OpTypeVector %uint 4
%_ptr_RayPayloadKHR_v4uint = OpTypePointer RayPayloadKHR %v4uint
   %hitValue = OpVariable %_ptr_RayPayloadKHR_v4uint RayPayloadKHR
    %uint_17 = OpConstant %uint 17
         %44 = OpConstantComposite %v4uint %uint_17 %uint_0 %uint_0 %uint_0
         %45 = OpTypeAccelerationStructureKHR
%_ptr_UniformConstant_45 = OpTypePointer UniformConstant %45
 %topLevelAS = OpVariable %_ptr_UniformConstant_45 UniformConstant
   %uint_255 = OpConstant %uint 255
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
         %56 = OpTypeImage %uint 2D 0 0 0 2 R32ui
%_ptr_UniformConstant_56 = OpTypePointer UniformConstant %56
     %result = OpVariable %_ptr_UniformConstant_56 UniformConstant
     %v2uint = OpTypeVector %uint 2
      %v2int = OpTypeVector %int 2
       %main = OpFunction %void None %3
          %5 = OpLabel
       %tmin = OpVariable %_ptr_Function_float Function
       %tmax = OpVariable %_ptr_Function_float Function
     %origin = OpVariable %_ptr_Function_v3float Function
     %direct = OpVariable %_ptr_Function_v3float Function
               OpStore %tmin %float_0
               OpStore %tmax %float_1
         %21 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_0
         %22 = OpLoad %uint %21
         %23 = OpConvertUToF %float %22
         %25 = OpFAdd %float %23 %float_0_5
         %27 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_1
         %28 = OpLoad %uint %27
         %29 = OpConvertUToF %float %28
         %30 = OpFAdd %float %29 %float_0_5
         %32 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_2
         %33 = OpLoad %uint %32
         %34 = OpConvertUToF %float %33
         %35 = OpFAdd %float %34 %float_0_5
         %36 = OpCompositeConstruct %v3float %25 %30 %35
               OpStore %origin %36
               OpStore %direct %39
               OpStore %hitValue %44
         %48 = OpLoad %45 %topLevelAS
         %50 = OpLoad %v3float %origin
         %51 = OpLoad %float %tmin
         %52 = OpLoad %v3float %direct
         %53 = OpLoad %float %tmax
               OpTraceRayKHR %48 %uint_0 %uint_255 %uint_0 %uint_0 %uint_0 %50 %51 %52 %53 %hitValue
         %59 = OpLoad %56 %result
         %61 = OpLoad %v3uint %gl_LaunchIDEXT
         %62 = OpVectorShuffle %v2uint %61 %61 0 1
         %64 = OpBitcast %v2int %62
         %65 = OpLoad %v4uint %hitValue
               OpImageWrite %59 %64 %65 ZeroExtend
               OpReturn
               OpFunctionEnd
```

</details>## Runtime Execution and Result Checking

- **Library tree construction.** The host builds one `RayTracingPipeline` per node. The root carries rgen, miss, and its own chit shaders. Every other node carries only chit shaders and gets `VK_PIPELINE_CREATE_LIBRARY_BIT_KHR`. Each library is linked to its parent through `addLibrary` in [vktRayTracingPipelineLibraryTests.cpp#L773-L781](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L773-L781). The root is then created through `createPipelineWithLibraries`.
- **Creation flag routing.** Capture/replay cases set `VK_PIPELINE_CREATE_RAY_TRACING_SHADER_GROUP_HANDLE_CAPTURE_REPLAY_BIT_KHR` on every node. Link-time cases set `VK_PIPELINE_CREATE_LINK_TIME_OPTIMIZATION_BIT_EXT` or `VK_PIPELINE_CREATE_RETAIN_LINK_TIME_OPTIMIZATION_INFO_BIT_EXT`. Maintenance5 cases also call `setCreateFlags2(translateCreateFlag(creationFlags))` so the same flags go through `VkPipelineCreateFlags2`.
- **`rgen_miss_in_library` layout.** When this flag is set, the host creates a separate `basePipelineLibrary` containing rgen and miss, links it to the root first, and only then links the hit-group libraries. This forces rgen=group 0 and miss=group 1 to appear before the hit groups in the flattened pipeline, which is the configuration that exposed the original driver bug.
- **Compilation modes.** `singlethreaded_compilation` calls `compileShaders` sequentially on each node. `multithreaded_compilation` spawns one host thread per node and joins them all. `multithreaded_compilation_dho` also sets `setDeferredOperation(true)` on every node.
- **Handle verification.** For non-default test types, the host queries the full handle vector from the linked root pipeline using `getShaderGroupHandlesVector` (or `getShaderGroupReplayHandlesVector` for capture/replay). It also queries each library's own handles. The `PipelineTree::getGroupOffsets` helper computed the per-library offsets at instance construction. The host slices the full vector by those offsets and compares each slice against the per-library query. A mismatch fails with `"Shader Group Handle verification failed for pipeline <idx>"` (prefixed by `"Capture Replay "` for replay handles).
- **Capture/replay flow.** When the test type includes capture replay, `iterate` calls `runTest()` once to save the full capture/replay handle vector, then calls `runTest(true /*replay*/)` to rebuild every pipeline with the saved handles fed back through `setGroupCaptureReplayHandle`. The second run queries the new full vector and compares it against the saved one. A mismatch fails with `"Capture Replay Shader Group Handles do not match creation handles for top-level pipeline"`. The second run also produces a second result vector; `iterate` compares it against the first and fails with `"Replay results differ from original results"` if they differ.
- **Acceleration structure setup.** The host builds one BLAS per odd `(x + y)` cell of the 8x8 grid. Triangle BLAS cells hold two triangles forming a quad. AABB BLAS cells hold one AABB. The TLAS adds one instance per BLAS, with `instanceShaderBindingTableRecordOffset = currentInstanceIndex % numShadersUsed` so the instances cycle through the available hit groups.
- **SBT construction.** The host builds raygen, miss, and hit SBT regions from the linked root pipeline. Raygen and miss each have one record. Hit has `hitGroupCount` records, one per closest-hit group across the root and all libraries.
- **Dispatch and copyback.** The host clears the result image to `0xFF000000`, inserts the image layout barriers, builds the acceleration structures, binds descriptor sets and pipeline, and calls `cmdTraceRays` over `8x8x1`. A `RAY_TRACING_SHADER` to `TRANSFER` memory barrier precedes `cmdCopyImageToBuffer`, then a `TRANSFER` to `HOST` barrier precedes `invalidateMappedMemoryRange`.
- **Pass/fail scan.** `iterate` walks the result vector and counts failures. Hit pixels must equal `shaderIdx % numShadersUsed` (with `shaderIdx` incrementing per hit pixel). Miss pixels must equal `RTPL_MAX_CHIT_SHADER_COUNT = 16`. A non-zero failure count produces `tcu::TestStatus::fail("failures=" + N)`; otherwise the test passes.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `DEFAULT` (no suffix) | The implementation linked the pipeline libraries into a working ray tracing pipeline that produced a wrong closest-hit index for at least one pixel, or dispatched the wrong SBT slot. Likely causes are incorrect library group ordering when flattening the linked pipeline, intersection shaders not firing when rgen/miss live in a library, or pipeline-creation flag handling that drops shader groups. |
| `CHECK_GROUP_HANDLES` (`_check_group_handles`) | The implementation returned a per-library handle slice from the root pipeline's full handle vector that does not equal the handles queried from that library alone. Likely causes are incorrect group-offset accounting when libraries are linked, handle reordering across library boundaries, or `pipelineLibraryGroupHandles` returning stale or remapped handles. |
| `CHECK_CAPTURE_REPLAY_HANDLES` (`_check_capture_replay_handles`) | The capture/replay handles saved from the first pipeline build did not match the handles returned by the replayed pipeline, or the replayed pipeline produced a different rendering result. Likely causes are non-deterministic capture/replay handle generation, the implementation ignoring `setGroupCaptureReplayHandle` data during replay, or replay-pipeline shader groups being laid out differently from the original. |
| `CHECK_ALL_HANDLES` (`_check_all_handles`) | Either the normal handle slice check failed, the capture/replay handle round-trip failed, or the replayed rendering differs from the original. Causes are the union of the `CHECK_GROUP_HANDLES` and `CHECK_CAPTURE_REPLAY_HANDLES` causes. |

All four values also share the rendering correctness check, so a `DEFAULT`-style rendering failure can surface under any of them.

### Cause Analysis

#### Linked pipeline renders the wrong closest-hit index

**Possible failure symptoms:** A `DEFAULT` (or any) case fails with `"failures=N"`. Hit pixels in the result image contain values that do not match `shaderIdx % numShadersUsed`, or miss pixels contain values other than 16. Some pixels may still be 17, the rgen sentinel, meaning no chit or miss shader ran at all.

**Possible implementation causes:** The implementation flattens linked libraries into a single pipeline and assigns shader-group indices in some order. A grounded investigation should check whether the implementation honors the `addLibrary` order when computing group offsets, whether `createPipelineWithLibraries` produces the same group layout that the host assumed in `PipelineTree::getGroupOffsets`, and whether the SBT built from the root pipeline resolves the per-instance `instanceShaderBindingTableRecordOffset` to the correct group. For `rgen_miss_in_library` cases specifically, the test exists because some implementations did not invoke intersection shaders when rgen and miss lived in a library and the hit groups (with intersection) lived in other libraries; a failure limited to `_aabbs` leaves under that subfamily points to that same path.

#### Per-library normal handle slice mismatch

**Possible failure symptoms:** A `CHECK_GROUP_HANDLES` (or `CHECK_ALL_HANDLES`) case fails with `"Shader Group Handle verification failed for pipeline <idx>"`. The handle bytes the host read from the linked root pipeline's full vector at the slice `[curGroupOffset * handleSize, (curGroupOffset + curGroupCount) * handleSize)` do not equal the bytes returned by querying pipeline `<idx>` alone.

**Possible implementation causes:** The `pipelineLibraryGroupHandles` feature requires the implementation to expose, through the root pipeline, the same handle bytes that each library would produce on its own. A grounded investigation should check whether the implementation computes per-library offsets in the full handle vector the same way the host does in `PipelineTree::calcOffsetRecursively`, whether it reorders groups when linking (for example, placing library groups before root groups), and whether handle bytes for a given group are stable across the linked-pipeline and per-library queries. If the rendering passes but the handle slice fails, the issue is in the handle-exposure path rather than in the rendering path.

#### Capture/replay handle round-trip mismatch

**Possible failure symptoms:** A `CHECK_CAPTURE_REPLAY_HANDLES` (or `CHECK_ALL_HANDLES`) case fails with `"Capture Replay Shader Group Handles do not match creation handles for top-level pipeline"`. The handle bytes the host saved from the first build do not equal the bytes returned by the replayed pipeline.

**Possible implementation causes:** The capture/replay contract requires the implementation to produce, on the replayed build, the same handle bytes it returned from the original build when the host feeds those bytes back through `setGroupCaptureReplayHandle`. A grounded investigation should check whether the implementation reads the saved bytes at pipeline-creation time, whether it re-derives handles deterministically from the saved bytes or generates fresh ones, and whether the per-group byte layout matches between the original query and the replay query. If the rendering also fails on the replay run, the replay pipeline may have a different group layout than the original.

#### Replay rendering differs from original rendering

**Possible failure symptoms:** A `CHECK_CAPTURE_REPLAY_HANDLES` (or `CHECK_ALL_HANDLES`) case fails with `"Replay results differ from original results"`. The second-run result vector differs from the first-run result vector at one or more pixels.

**Possible implementation causes:** The replayed pipeline should produce the same per-pixel closest-hit index as the original. A grounded investigation should check whether the replay pipeline's group layout matches the original (otherwise the SBT resolves to different groups), whether the implementation honors the saved capture/replay handles when building the SBT, and whether any deferred compilation path produces a different compiled shader for the same module. If the handle round-trip check also fails, this symptom is a downstream consequence of the same root cause.

#### Host-side reference or copyback error

**Possible failure symptoms:** The host reports failure but shader-side and handle-side reasoning do not explain the mismatch. The result image contains values that look reasonable but do not match the host-recomputed reference, or the handle slice comparison fails by a small offset that lines up with an off-by-one in `PipelineTree::getGroupOffsets`.

**Possible implementation causes:** The host recreates the expected per-pixel value in `iterate` using the same `shaderIdx % numShadersUsed` formula that the device follows. Source-level investigation is needed to distinguish an actual device-side bug from a host-side reference computation bug, an image-clear or barrier issue, or a `PipelineTree` offset-accounting bug. The `PipelineTree` flattening is deterministic given the library configuration, so an offset-accounting bug would likely affect many cases consistently.

## Case Pruning

### Requirement-based pruning

- All cases require `VK_KHR_ray_tracing_pipeline` and `VK_KHR_pipeline_library` [vktRayTracingPipelineLibraryTests.cpp#L300-L301](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L300-L301).
- Any case whose test type is not `DEFAULT` requires `VK_EXT_pipeline_library_group_handles` [vktRayTracingPipelineLibraryTests.cpp#L303-L304](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L303-L304).
- `use_link_time_optimizations` and `retain_link_time_optimizations` require `VK_EXT_graphics_pipeline_library` [vktRayTracingPipelineLibraryTests.cpp#L306-L307](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L306-L307).
- `maintenance5` requires `VK_KHR_maintenance5` [vktRayTracingPipelineLibraryTests.cpp#L309-L310](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L309-L310).
- Any case whose test type includes capture replay requires `rayTracingPipelineShaderGroupHandleCaptureReplay == VK_TRUE`, otherwise the test throws `NotSupportedError` [vktRayTracingPipelineLibraryTests.cpp#L312-L317](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L312-L317).

### Design-based pruning

- The `misc` subfamily uses a single library configuration (`s1_l1` for `maintenance5`, `s2_l23` for the link-time leaves) instead of the full matrix, because the focus is on the pipeline-creation path, not on exercising every library tree shape.
- The `rgen_miss_in_library` subfamily uses a smaller set of library configurations (`s0_l1`, `s0_l11`, `s0_l23`, `s0_l1_l1`, `s0_l2_l3`) and always uses the `DEFAULT` test type, because the focus is on the rendering bug, not on handle verification.
- The `rgen_miss_in_library` subfamily does not set the capture/replay or link-time flags, because those flags would obscure whether the rendering bug is reproduced.
- The library configuration table does not include configurations with more than 4 libraries or more than 3 chit shaders in the root, because the point is to exercise the tree-flattening logic, not to stress the maximum pipeline size.
- The 16 chit shader modules are generated once and reused across all cases. Only the first `getHitGroupCount()` are added to any given pipeline. This avoids generating shaders that the test never uses.

## Key Takeaways

- The test type axis controls the verification scope. `DEFAULT` checks rendering only. `CHECK_GROUP_HANDLES` adds normal handle slice consistency. `CHECK_CAPTURE_REPLAY_HANDLES` adds a full replay round-trip. `CHECK_ALL_HANDLES` does both handle checks.
- The other registered dimensions (library configuration, geometry, compilation mode, `misc` variants, `rgen_miss_in_library`) change how the pipeline is built, but they do not change what is verified. They exist to exercise different library tree shapes, geometry paths, and pipeline-creation paths under the same verification scope.
- The rgen shader is identical across all cases. The `chit<i>` and `miss` shaders each write a single constant. The interesting behavior is on the host side: how the library tree is built, how the SBT is constructed, and how the handle vectors are sliced.
- `rgen_miss_in_library` exists to reproduce a specific driver bug where intersection shaders were not invoked when rgen and miss lived in a library and hit groups (with intersection) lived in other libraries. The subfamily is the most likely place to see a `DEFAULT` rendering failure.
- Capture/replay is the only path that runs the test twice. The first run saves handles; the second run feeds them back. Both rendering and handles must match across the two runs.
- Failure analysis is per test type: rendering correctness, normal handle slice consistency, capture/replay handle round-trip, and replay rendering consistency each have their own cause analysis in `## Failure Meaning`.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Category root registration | [vktRayTracingPipelineLibraryTests.cpp#L1225-L1232](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L1225-L1232) | Builds the `pipeline_library` group and attaches the `configurations` child. |
| `TestParams` struct | [vktRayTracingPipelineLibraryTests.cpp#L76-L107](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L76-L107) | Captures library configuration, compilation flags, test type, geometry, maintenance5, link-time optimization, rgen-miss-in-library, and image dimensions. |
| `PipelineTree` helper | [vktRayTracingPipelineLibraryTests.cpp#L111-L226](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L111-L226) | Flattens the library tree into per-pipeline group offsets used for handle slicing. |
| `checkSupport` gates | [vktRayTracingPipelineLibraryTests.cpp#L298-L318](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L298-L318) | Feature gates for `VK_EXT_pipeline_library_group_handles`, `VK_EXT_graphics_pipeline_library`, `VK_KHR_maintenance5`, and the capture/replay feature. |
| `initPrograms` shader generation | [vktRayTracingPipelineLibraryTests.cpp#L320-L393](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L320-L393) | Generates the rgen, miss, chit, and isec shaders. |
| `runTest` pipeline construction | [vktRayTracingPipelineLibraryTests.cpp#L615-L866](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L615-L866) | Builds the library tree, sets creation flags, links libraries, creates the root pipeline, and runs the handle verification. |
| Handle verification loop | [vktRayTracingPipelineLibraryTests.cpp#L804-L866](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L804-L866) | Queries the full handle vector from the root pipeline, slices it per library, and compares against per-library queries. Saves or checks capture/replay handles. |
| Rendering dispatch and copyback | [vktRayTracingPipelineLibraryTests.cpp#L868-L983](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L868-L983) | Builds SBT, traces rays, copies result image back. |
| `iterate` pass/fail decision | [vktRayTracingPipelineLibraryTests.cpp#L985-L1025](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L985-L1025) | Runs the test, runs replay when applicable, scans the result image against the expected pattern. |
| Library configuration table | [vktRayTracingPipelineLibraryTests.cpp#L1042-L1067](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L1042-L1067) | Defines the 12 library configurations used by the matrix. |
| Test-type and geometry suffix table | [vktRayTracingPipelineLibraryTests.cpp#L1069-L1087](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L1069-L1087) | Maps `TestType` and `useAABBs` to leaf-name suffixes. |
| `misc` subfamily construction | [vktRayTracingPipelineLibraryTests.cpp#L1122-L1168](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L1122-L1168) | Defines the maintenance5, use_link_time_optimizations, and retain_link_time_optimizations leaves. |
| `rgen_miss_in_library` subfamily construction | [vktRayTracingPipelineLibraryTests.cpp#L1174-L1222](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L1174-L1222) | Defines the rgen/miss-in-library leaves and the smaller library configuration matrix. |
