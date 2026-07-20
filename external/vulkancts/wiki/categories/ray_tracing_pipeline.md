## Overview

The `ray_tracing_pipeline` test category collects tests that check device-side ray traversal through `VK_KHR_ray_tracing_pipeline` across raygen, closest-hit, any-hit, miss, callable, and intersection shader stages.

## Background Knowledge

- **TLAS and BLAS.** A ray tracing pipeline traverses a top-level acceleration structure (TLAS) that references one or more bottom-level acceleration structures (BLAS). Each BLAS holds geometry (triangles or AABBs). Each TLAS instance references a BLAS, applies a 3x4 transform, and carries an `instanceCustomIndex`, a `mask`, an `instanceShaderBindingTableRecordOffset`, and `VkGeometryInstanceFlagsKHR`. Multiple Level-3 pages in this category (e.g., [Build](../testfiles/ray_tracing_pipeline/Build.md), [AccelerationStructures](../testfiles/ray_tracing_pipeline/AccelerationStructures.md), [ProceduralGeometry](../testfiles/ray_tracing_pipeline/ProceduralGeometry.md)) assume this two-level structure when describing their geometry setup.
- **Acceleration structure build types.** `VK_KHR_acceleration_structure` defines `VK_ACCELERATION_STRUCTURE_BUILD_TYPE_DEVICE_KHR` (build recorded and executed on the device via command buffer) and `VK_ACCELERATION_STRUCTURE_BUILD_TYPE_HOST_KHR` (build performed by the host). The build type selects where the build work runs, not the resulting traversal semantics. Pages exercising build-type variation include [Build](../testfiles/ray_tracing_pipeline/Build.md), [BuildLarge](../testfiles/ray_tracing_pipeline/BuildLarge.md), [BuildIndirect](../testfiles/ray_tracing_pipeline/BuildIndirect.md), [AccelerationStructures](../testfiles/ray_tracing_pipeline/AccelerationStructures.md), and [PipelineFlags](../testfiles/ray_tracing_pipeline/PipelineFlags.md).
- **Deferred host operations.** `VK_KHR_deferred_host_operations` lets a host-side AS build be split across multiple host threads. The application partitions the build work by calling `vkDeferredOperationJoinKHR` from each worker thread; the implementation joins them. A non-zero worker-thread count is what turns a plain host build into a deferred host build. This mechanism underlies the `cpuht_*` / `cpu_ht_*` leaves in [Build](../testfiles/ray_tracing_pipeline/Build.md), [BuildLarge](../testfiles/ray_tracing_pipeline/BuildLarge.md), and [BuildIndirect](../testfiles/ray_tracing_pipeline/BuildIndirect.md), and the `host_threading` dimension in [AccelerationStructures](../testfiles/ray_tracing_pipeline/AccelerationStructures.md).
- **Shader Binding Table regions.** `cmdTraceRaysKHR` consumes four `VkStridedDeviceAddressRegionKHR` regions: raygen, miss, hit, and callable. Each region is an array of records; a record begins with a shader-group handle and may carry a shader-record data block after it. Hit-group indexing resolves `instanceContributionToHitGroupIndex + sbtRecordOffset + geometryIndex * sbtRecordStride`; miss indexing uses `missIndex` strides. Pages that depend on SBT layout include [ShaderBindingTable](../testfiles/ray_tracing_pipeline/ShaderBindingTable.md), [NullAS](../testfiles/ray_tracing_pipeline/NullAS.md), [CallableShaders](../testfiles/ray_tracing_pipeline/CallableShaders.md), and [TraceRays](../testfiles/ray_tracing_pipeline/TraceRays.md).

## Category Structure

```text
ray_tracing_pipeline
├── amber
├── builtin
├── spec_constants
├── large_shader_set
├── build
├── callable_shader
├── trace_rays_cmds
├── trace_rays_cmds_maintenance_1
├── shader_binding_table
├── traversal_control
├── acceleration_structures
├── procedural_geometry
├── indirect_acceleration_structure
├── watertightness
├── pipeline_library
├── memguarantee
├── null_as
├── capture_replay
├── misc
├── complexcontrolflow
├── barrier
├── data_spill
├── direction_length
├── inside_aabbs
├── barycentric_coordinates
├── non_uniform_args
├── pipeline_no_null_shaders_flag
├── trace_rays_indirect2
├── opacity_micromap
├── position_fetch
├── ser
├── linear_swept_spheres
├── limits
└── rtir_activity
```

The dispatcher [vktRayTracingTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L65-L104) is registration-only: it adds 34 child groups and delegates each to a separate `create*Tests` function. The 34 registered families map to 30 Level-3 pages because four pages each cover multiple families rooted in the same implementation file:

- [Builtin.md](../testfiles/ray_tracing_pipeline/Builtin.md) covers `builtin` and `spec_constants` (both in `vktRayTracingBuiltinTests.cpp`).
- [TraceRays.md](../testfiles/ray_tracing_pipeline/TraceRays.md) covers `trace_rays_cmds`, `trace_rays_cmds_maintenance_1`, and `trace_rays_indirect2` (all in `vktRayTracingTraceRaysTests.cpp`).
- [DirectionLength.md](../testfiles/ray_tracing_pipeline/DirectionLength.md) covers `direction_length` and `inside_aabbs` (both in `vktRayTracingDirectionTests.cpp`).

The source directory is `ray_tracing/` even though the category is `ray_tracing_pipeline`.

## How the Families Fit Together

All families exercise `vkCmdTraceRays*` dispatch through a ray tracing pipeline, but they target different aspects of the pipeline contract:

- `builtin`, `spec_constants`, `callable_shader`, and `shader_binding_table` test **what values** the pipeline produces: shader built-in results, specialization-constant substitution, callable invocation, and SBT record indexing.
- `traversal_control`, `watertightness`, `barycentric_coordinates`, `non_uniform_args`, and `direction_length` test **which candidates survive traversal** under control-flow, edge, and argument conditions.
- `build`, `large_shader_set`, `acceleration_structures`, `indirect_acceleration_structure`, `procedural_geometry`, `null_as`, `capture_replay`, and `pipeline_no_null_shaders_flag` test **how the pipeline and acceleration structure behave** when build mode, geometry, flags, or descriptors vary.
- `barrier`, `memguarantee`, `complexcontrolflow`, and `data_spill` test **synchronization and shader-call mechanics** around `traceRayEXT`, `executeCallableEXT`, and `reportIntersectionEXT`.
- `opacity_micromap`, `position_fetch`, `ser`, `linear_swept_spheres`, and `rtir_activity` test **extension-specific features** integrated into the pipeline.
- `amber` and `limits` test **Amber-scripted scenarios and property queries** that do not fit the C++-shader pattern.

## Level-3 Pages Navigation

| Registered test family or area | Level-3 page | What to read there |
|--------------------------------|--------------|--------------------|
| `builtin`, `spec_constants` | [Builtin.md](../testfiles/ray_tracing_pipeline/Builtin.md) | Shader built-in result checks and specialization-constant substitution across raygen, hit, miss, callable, and intersection stages. |
| `traversal_control` | [TraversalControl.md](../testfiles/ray_tracing_pipeline/TraversalControl.md) | Any-hit ignore, pass-through, and terminate behavior plus intersection report and do-not-report cases. |
| `shader_binding_table` | [ShaderBindingTable.md](../testfiles/ray_tracing_pipeline/ShaderBindingTable.md) | SBT hit, miss, and callable indexing plus shader-group handle alignment. |
| `callable_shader` | [CallableShaders.md](../testfiles/ray_tracing_pipeline/CallableShaders.md) | Callable invocation through raygen, miss, closest-hit, and callable stages, including single and multiple invocations. |
| `trace_rays_cmds`, `trace_rays_cmds_maintenance_1`, `trace_rays_indirect2` | [TraceRays.md](../testfiles/ray_tracing_pipeline/TraceRays.md) | Direct, indirect, and indirect2 CPU and GPU dispatch paths, copy styles, and queue submission variants. |
| `build` | [Build.md](../testfiles/ray_tracing_pipeline/Build.md) | CPU, GPU, and host-threaded acceleration-structure build comparison via result-buffer checking. |
| `large_shader_set` | [BuildLarge.md](../testfiles/ray_tracing_pipeline/BuildLarge.md) | Large pipeline with many callable groups, watchdog-managed creation, and CPU and GPU build modes. |
| `indirect_acceleration_structure` | [BuildIndirect.md](../testfiles/ray_tracing_pipeline/BuildIndirect.md) | Indirect build and update with count and offset fields for triangles, AABBs, and instances. |
| `procedural_geometry` | [ProceduralGeometry.md](../testfiles/ray_tracing_pipeline/ProceduralGeometry.md) | Two explicit AABB arrangements and result-buffer comparison. |
| `amber` | [Amber.md](../testfiles/ray_tracing_pipeline/Amber.md) | Amber-scripted ray tracing cases with pipeline, AS, and buffer-device-address requirements. |
| `barycentric_coordinates` | [BarycentricCoordinates.md](../testfiles/ray_tracing_pipeline/BarycentricCoordinates.md) | Closest-hit, any-hit, and terminating any-hit barycentric result verification with deterministic seeds. |
| `acceleration_structures` | [AccelerationStructures.md](../testfiles/ray_tracing_pipeline/AccelerationStructures.md) | Build flags, formats, operations, host threading, instance culling and update, dynamic indexing, empty structures, and query results. |
| `pipeline_library` | [PipelineLibrary.md](../testfiles/ray_tracing_pipeline/PipelineLibrary.md) | Linked pipeline-library configurations, shader group handles, capture-replay, and optimization variants. |
| `capture_replay` | [CaptureReplay.md](../testfiles/ray_tracing_pipeline/CaptureReplay.md) | SBT and acceleration-structure capture and replay configurations. |
| `pipeline_no_null_shaders_flag` | [PipelineFlags.md](../testfiles/ray_tracing_pipeline/PipelineFlags.md) | `VK_PIPELINE_CREATE_RAY_TRACING_NO_NULL_*_SHADERS_BIT_KHR` flag combinations over CPU and GPU build, geometry, stride, offset, and library mode. |
| `null_as` | [NullAS.md](../testfiles/ray_tracing_pipeline/NullAS.md) | Null descriptor always-miss behavior and mixed dispatches between ray tracing and compute. |
| `watertightness` | [Watertightness.md](../testfiles/ray_tracing_pipeline/Watertightness.md) | Fan and closed-fan triangle arrangements with no-miss and single-hit consistency. |
| `direction_length`, `inside_aabbs` | [DirectionLength.md](../testfiles/ray_tracing_pipeline/DirectionLength.md) | Direction scaling and rotation, plus rays starting inside AABBs. |
| `non_uniform_args` | [NonUniformArgs.md](../testfiles/ray_tracing_pipeline/NonUniformArgs.md) | Closest-hit ray-type combinations and miss-cause cases via non-uniform SBT offsets. |
| `misc` | [Misc.md](../testfiles/ray_tracing_pipeline/Misc.md) | Callable stress, cull masks, recursion, shader-record layouts, empty pipeline layouts, null miss, memory access, and related edge cases. |
| `limits` | [Limits.md](../testfiles/ray_tracing_pipeline/Limits.md) | Acceleration-structure and ray-tracing pipeline property queries against spec-required bounds. |
| `barrier` | [Barrier.md](../testfiles/ray_tracing_pipeline/Barrier.md) | Barrier synchronization crossing resource types, barrier types, and writer and reader stages involving ray tracing stages. |
| `memguarantee` | [MemGuarantee.md](../testfiles/ray_tracing_pipeline/MemGuarantee.md) | Shader-call memory behavior: inside and between cases with `shadercallcoherent` qualifiers. |
| `complexcontrolflow` | [ComplexControlFlow.md](../testfiles/ray_tracing_pipeline/ComplexControlFlow.md) | Conditionals, switches, loops, nested loops, and function-call patterns around trace-ray calls. |
| `data_spill` | [DataSpill.md](../testfiles/ray_tracing_pipeline/DataSpill.md) | Data spilling around trace-ray, report-intersection, execute-callable, and pipeline-interface paths. |
| `opacity_micromap` | [OpacityMicromap.md](../testfiles/ray_tracing_pipeline/OpacityMicromap.md) | `VK_EXT_opacity_micromap` integration: opacity flags, special-index use, modes, levels, copy behavior, and non-zero base variants. |
| `position_fetch` | [PositionFetch.md](../testfiles/ray_tracing_pipeline/PositionFetch.md) | `VK_KHR_ray_tracing_position_fetch`: vertex formats, CPU and GPU build, flag masks, and fetched-position tolerance. |
| `ser` | [ShaderExecutionReorder.md](../testfiles/ray_tracing_pipeline/ShaderExecutionReorder.md) | `VK_NV_shader_invocation_reorder`: built-in, large-dimension, motion, and reorder cases. |
| `linear_swept_spheres` | [LinearSweptSpheres.md](../testfiles/ray_tracing_pipeline/LinearSweptSpheres.md) | `VK_NV_ray_tracing_linear_swept_spheres`: sphere and LSS geometry modes, copy, endcap, ray-query, hit-object, vertex-format, and radius-format choices. |
| `rtir_activity` | [InvocationReorderActivity.md](../testfiles/ray_tracing_pipeline/InvocationReorderActivity.md) | Single activity case for invocation reorder with `hitObjectTraceRayEXT` and conditional `reorderThreadEXT`. |

## Category Notes

- The dispatcher [vktRayTracingTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L65-L104) contains no test implementation. It adds 34 child groups, each delegated to a separate `create*Tests` function.
- Most families require `VK_KHR_ray_tracing_pipeline` and `VK_KHR_acceleration_structure`. Extension families add `VK_EXT_opacity_micromap`, `VK_KHR_ray_tracing_position_fetch`, `VK_NV_shader_invocation_reorder`, or `VK_NV_ray_tracing_linear_swept_spheres`. Pipeline-library tests add `VK_KHR_pipeline_library` and related extension gates.
- The build file [CMakeLists.txt](../../modules/vulkan/ray_tracing/CMakeLists.txt#L6-L70) lists all implementation sources.
