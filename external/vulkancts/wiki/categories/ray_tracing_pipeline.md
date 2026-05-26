# ray_tracing_pipeline

The `ray_tracing_pipeline` category documents Vulkan CTS tests registered from the `ray_tracing` source directory for `VK_KHR_ray_tracing_pipeline` behavior, including ray tracing shader built-ins, pipeline/SBT construction, trace commands, acceleration-structure interaction, pipeline libraries, shader execution reorder, opacity micromap, position fetch, and related edge cases. The root is registered as `ray_tracing_pipeline` in [vktTestPackage.cpp](../../modules/vulkan/vktTestPackage.cpp#L1387), and dispatches through [vktRayTracingTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L65-L104).

## Registration Entry Point

| Item | Evidence |
|------|----------|
| Category root registration | [vktTestPackage.cpp](../../modules/vulkan/vktTestPackage.cpp#L1387) |
| Category dispatcher | [vktRayTracingTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L65-L104) |
| Dispatcher includes | [vktRayTracingTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L24-L54) |
| Build inventory | [CMakeLists.txt](../../modules/vulkan/ray_tracing/CMakeLists.txt#L6-L70) |

## Registration Hierarchy

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

## Test Families

### amber — Registered branch

Amber-scripted ray tracing cases require ray tracing pipeline, acceleration structure, buffer device address, and selected pipeline-library/deferred-host-operation features declared in the Amber requirement arrays. Registered by the dispatcher in [vktRayTracingTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L69-L102) and constructed in [vktRayTracingAmberTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingAmberTests.cpp#L35). See [vktRayTracingAmberTests](../testfiles/ray_tracing_pipeline/vktRayTracingAmberTests.md).

### builtin — Registered branch

Shader built-in result checks cover launch IDs/sizes, primitive and instance identifiers, ray parameters, transforms, incoming flags, hit attributes, and indirect variants. Registered by the dispatcher in [vktRayTracingTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L69-L102) and constructed in [vktRayTracingBuiltinTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L4794). See [vktRayTracingBuiltinTests](../testfiles/ray_tracing_pipeline/vktRayTracingBuiltinTests.md).

### spec_constants — Registered branch

Specialization-constant cases register shader-stage leaves for raygen, hit, miss, callable, and intersection stage coverage. Registered by the dispatcher in [vktRayTracingTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L69-L102) and constructed in [vktRayTracingBuiltinTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L4811). See [vktRayTracingBuiltinTests](../testfiles/ray_tracing_pipeline/vktRayTracingBuiltinTests.md).

### large_shader_set — Registered branch

Large shader-set tests vary GPU and host-threaded CPU build modes and square sizes to exercise many callable groups. Registered by the dispatcher in [vktRayTracingTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L69-L102) and constructed in [vktRayTracingBuildLargeTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L574). See [vktRayTracingBuildLargeTests](../testfiles/ray_tracing_pipeline/vktRayTracingBuildLargeTests.md).

### build — Registered branch

Build tests compare ray tracing results when acceleration structures are built on GPU, CPU, and CPU host-threaded paths. Registered by the dispatcher in [vktRayTracingTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L69-L102) and constructed in [vktRayTracingBuildTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L756). See [vktRayTracingBuildTests](../testfiles/ray_tracing_pipeline/vktRayTracingBuildTests.md).

### callable_shader — Registered branch

Callable-shader tests cover callable invocation through raygen, miss, closest-hit, and callable stages, including single and multiple invocations. Registered by the dispatcher in [vktRayTracingTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L69-L102) and constructed in [vktRayTracingCallableShadersTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L1978). See [vktRayTracingCallableShadersTests](../testfiles/ray_tracing_pipeline/vktRayTracingCallableShadersTests.md).

### trace_rays_cmds — Registered branch

Trace-rays command tests cover direct and indirect CPU/GPU buffer-source paths for `vkCmdTraceRays*` style dispatch. Registered by the dispatcher in [vktRayTracingTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L69-L102) and constructed in [vktRayTracingTraceRaysTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L1462). See [vktRayTracingTraceRaysTests](../testfiles/ray_tracing_pipeline/vktRayTracingTraceRaysTests.md).

### trace_rays_cmds_maintenance_1 — Registered branch

Maintenance1 trace-rays command tests cover indirect2 CPU and GPU buffer-source paths. Registered by the dispatcher in [vktRayTracingTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L69-L102) and constructed in [vktRayTracingTraceRaysTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L1507). See [vktRayTracingTraceRaysTests](../testfiles/ray_tracing_pipeline/vktRayTracingTraceRaysTests.md).

### shader_binding_table — Registered branch

Shader-binding-table tests cover hit/miss/callable indexing and shader-group handle alignment. Registered by the dispatcher in [vktRayTracingTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L69-L102) and constructed in [vktRayTracingShaderBindingTableTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L1620). See [vktRayTracingShaderBindingTableTests](../testfiles/ray_tracing_pipeline/vktRayTracingShaderBindingTableTests.md).

### traversal_control — Registered branch

Traversal-control tests verify any-hit ignore/pass-through/terminate behavior and intersection shader report/donot-report behavior. Registered by the dispatcher in [vktRayTracingTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L69-L102) and constructed in [vktRayTracingTraversalControlTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L769). See [vktRayTracingTraversalControlTests](../testfiles/ray_tracing_pipeline/vktRayTracingTraversalControlTests.md).

### acceleration_structures — Registered branch

Acceleration-structure tests cover flags, formats, operations, host threading, function arguments, instance indexing/culling/update, dynamic indexing, empty structures, query results, and pipeline-stage use. Registered by the dispatcher in [vktRayTracingTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L69-L102) and constructed in [vktRayTracingAccelerationStructuresTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L7740). See [vktRayTracingAccelerationStructuresTests](../testfiles/ray_tracing_pipeline/vktRayTracingAccelerationStructuresTests.md).

### procedural_geometry — Registered branch

Procedural-geometry tests register explicit AABB arrangements for objects behind bounding boxes and triangles between boxes. Registered by the dispatcher in [vktRayTracingTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L69-L102) and constructed in [vktRayTracingProceduralGeometryTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingProceduralGeometryTests.cpp#L614). See [vktRayTracingProceduralGeometryTests](../testfiles/ray_tracing_pipeline/vktRayTracingProceduralGeometryTests.md).

### indirect_acceleration_structure — Registered branch

Indirect acceleration-structure tests vary build/update mode and indirect count/offset fields for triangles, AABBs, and instances. Registered by the dispatcher in [vktRayTracingTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L69-L102) and constructed in [vktRayTracingBuildIndirectTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1390). See [vktRayTracingBuildIndirectTests](../testfiles/ray_tracing_pipeline/vktRayTracingBuildIndirectTests.md).

### watertightness — Registered branch

Watertightness tests generate fan and closed-fan triangle arrangements and check no-miss/single-hit consistency. Registered by the dispatcher in [vktRayTracingTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L69-L102) and constructed in [vktRayTracingWatertightnessTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingWatertightnessTests.cpp#L875). See [vktRayTracingWatertightnessTests](../testfiles/ray_tracing_pipeline/vktRayTracingWatertightnessTests.md).

### pipeline_library — Registered branch

Pipeline-library tests create linked ray tracing pipeline-library configurations and check shader group handles, capture-replay, and optimization variants. Registered by the dispatcher in [vktRayTracingTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L69-L102) and constructed in [vktRayTracingPipelineLibraryTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L1227). See [vktRayTracingPipelineLibraryTests](../testfiles/ray_tracing_pipeline/vktRayTracingPipelineLibraryTests.md).

### memguarantee — Registered branch

Memory-guarantee tests register inside and between cases around shader-call memory behavior. Registered by the dispatcher in [vktRayTracingTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L69-L102) and constructed in [vktRayTracingMemGuaranteeTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingMemGuaranteeTests.cpp#L877). See [vktRayTracingMemGuaranteeTests](../testfiles/ray_tracing_pipeline/vktRayTracingMemGuaranteeTests.md).

### null_as — Registered branch

Null acceleration-structure tests check always-miss behavior and mixed dispatches using null descriptors. Registered by the dispatcher in [vktRayTracingTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L69-L102) and constructed in [vktRayTracingNullASTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingNullASTests.cpp#L759). See [vktRayTracingNullASTests](../testfiles/ray_tracing_pipeline/vktRayTracingNullASTests.md).

### capture_replay — Registered branch

Capture-replay tests cover shader-binding-table and acceleration-structure capture/replay configurations. Registered by the dispatcher in [vktRayTracingTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L69-L102) and constructed in [vktRayTracingCaptureReplayTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L1731). See [vktRayTracingCaptureReplayTests](../testfiles/ray_tracing_pipeline/vktRayTracingCaptureReplayTests.md).

### misc — Registered branch

Miscellaneous tests cover callable stress, cull masks, recursion, shader-record layouts, empty pipeline layouts, null miss, memory access, and related edge cases. Registered by the dispatcher in [vktRayTracingTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L69-L102) and constructed in [vktRayTracingMiscTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingMiscTests.cpp#L10908). See [vktRayTracingMiscTests](../testfiles/ray_tracing_pipeline/vktRayTracingMiscTests.md).

### complexcontrolflow — Registered branch

Complex-control-flow tests cover conditionals, switches, loops, nested loops, and function-call patterns around ray tracing shader calls. Registered by the dispatcher in [vktRayTracingTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L69-L102) and constructed in [vktRayTracingComplexControlFlowTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L1845). See [vktRayTracingComplexControlFlowTests](../testfiles/ray_tracing_pipeline/vktRayTracingComplexControlFlowTests.md).

### barrier — Registered branch

Barrier tests cross resource types, barrier types, and writer/reader stages involving ray tracing stages. Registered by the dispatcher in [vktRayTracingTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L69-L102) and constructed in [vktRayTracingBarrierTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingBarrierTests.cpp#L1753). See [vktRayTracingBarrierTests](../testfiles/ray_tracing_pipeline/vktRayTracingBarrierTests.md).

### data_spill — Registered branch

Data-spill tests cover data spilling around trace-ray, report-intersection, execute-callable, and pipeline-interface paths. Registered by the dispatcher in [vktRayTracingTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L69-L102) and constructed in [vktRayTracingDataSpillTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L2890). See [vktRayTracingDataSpillTests](../testfiles/ray_tracing_pipeline/vktRayTracingDataSpillTests.md).

### direction_length — Registered branch

Direction-length tests vary hit/intersection stages, geometry, scaling factors, and rotation angles. Registered by the dispatcher in [vktRayTracingTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L69-L102) and constructed in [vktRayTracingDirectionTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingDirectionTests.cpp#L684). See [vktRayTracingDirectionTests](../testfiles/ray_tracing_pipeline/vktRayTracingDirectionTests.md).

### inside_aabbs — Registered branch

Inside-AABB tests vary stages, ray-end choices, scaling factors, and rotation angles for rays starting inside AABBs. Registered by the dispatcher in [vktRayTracingTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L69-L102) and constructed in [vktRayTracingDirectionTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingDirectionTests.cpp#L778). See [vktRayTracingDirectionTests](../testfiles/ray_tracing_pipeline/vktRayTracingDirectionTests.md).

### barycentric_coordinates — Registered branch

Barycentric-coordinate tests register closest-hit, any-hit, and terminating any-hit cases with deterministic seeds. Registered by the dispatcher in [vktRayTracingTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L69-L102) and constructed in [vktRayTracingBarycentricCoordinatesTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingBarycentricCoordinatesTests.cpp#L503). See [vktRayTracingBarycentricCoordinatesTests](../testfiles/ray_tracing_pipeline/vktRayTracingBarycentricCoordinatesTests.md).

### non_uniform_args — Registered branch

Non-uniform argument tests generate closest-hit ray-type combinations and miss-cause cases. Registered by the dispatcher in [vktRayTracingTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L69-L102) and constructed in [vktRayTracingNonUniformArgsTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingNonUniformArgsTests.cpp#L520). See [vktRayTracingNonUniformArgsTests](../testfiles/ray_tracing_pipeline/vktRayTracingNonUniformArgsTests.md).

### pipeline_no_null_shaders_flag — Registered branch

Pipeline flag tests exercise `VK_PIPELINE_CREATE_RAY_TRACING_NO_NULL_*_SHADERS_BIT_KHR` combinations over CPU/GPU processors, geometry, stride, offset, and library mode. Registered by the dispatcher in [vktRayTracingTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L69-L102) and constructed in [vktRayTracingPipelineFlagsTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L1573). See [vktRayTracingPipelineFlagsTests](../testfiles/ray_tracing_pipeline/vktRayTracingPipelineFlagsTests.md).

### trace_rays_indirect2 — Registered branch

Indirect2 trace-rays tests vary indirect CPU/GPU buffer source, copy style, queue submission path, and dimensions. Registered by the dispatcher in [vktRayTracingTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L69-L102) and constructed in [vktRayTracingTraceRaysTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L1553). See [vktRayTracingTraceRaysTests](../testfiles/ray_tracing_pipeline/vktRayTracingTraceRaysTests.md).

### opacity_micromap — Registered branch

Opacity-micromap tests combine opacity flags, special-index use, modes, levels, copy behavior, and non-zero base variants. Registered by the dispatcher in [vktRayTracingTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L69-L102) and constructed in [vktRayTracingOpacityMicromapTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingOpacityMicromapTests.cpp#L821). See [vktRayTracingOpacityMicromapTests](../testfiles/ray_tracing_pipeline/vktRayTracingOpacityMicromapTests.md).

### position_fetch — Registered branch

Position-fetch tests vary CPU/GPU build modes, vertex formats, and flag masks for ray pipeline shaders using vertex position fetch. Registered by the dispatcher in [vktRayTracingTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L69-L102) and constructed in [vktRayTracingPositionFetchTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingPositionFetchTests.cpp#L532). See [vktRayTracingPositionFetchTests](../testfiles/ray_tracing_pipeline/vktRayTracingPositionFetchTests.md).

### ser — Registered branch

Shader execution reorder tests register built-in, large-dimension, motion, and reorder cases for invocation reorder behavior. Registered by the dispatcher in [vktRayTracingTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L69-L102) and constructed in [vktRayTracingShaderExecutionReorderTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingShaderExecutionReorderTests.cpp#L2256). See [vktRayTracingShaderExecutionReorderTests](../testfiles/ray_tracing_pipeline/vktRayTracingShaderExecutionReorderTests.md).

### linear_swept_spheres — Registered branch

Linear swept spheres tests compare sphere and linear-swept-sphere geometry modes across copy, endcap, ray-query, hit-object, vertex-format, and radius-format choices. Registered by the dispatcher in [vktRayTracingTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L69-L102) and constructed in [vktRayTracingLinearSweptSpheresTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingLinearSweptSpheresTests.cpp#L1029). See [vktRayTracingLinearSweptSpheresTests](../testfiles/ray_tracing_pipeline/vktRayTracingLinearSweptSpheresTests.md).

### limits — Registered branch

Limits tests query acceleration-structure and ray-tracing pipeline property groups. Registered by the dispatcher in [vktRayTracingTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L69-L102) and constructed in [vktRayTracingLimitsTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingLimitsTests.cpp#L279). See [vktRayTracingLimitsTests](../testfiles/ray_tracing_pipeline/vktRayTracingLimitsTests.md).

### rtir_activity — Registered branch

RTIR activity tests register a single activity case for invocation reorder activity with ray pipelines. Registered by the dispatcher in [vktRayTracingTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L69-L102) and constructed in [vktRayTracingInvocationReorderActivityTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingInvocationReorderActivityTests.cpp#L637). See [vktRayTracingInvocationReorderActivityTests](../testfiles/ray_tracing_pipeline/vktRayTracingInvocationReorderActivityTests.md).

## File Inventory

| Wiki page | Source role | Registered path roots |
|-----------|-------------|-----------------------|
| [vktRayTracingAccelerationStructuresTests](../testfiles/ray_tracing_pipeline/vktRayTracingAccelerationStructuresTests.md) | Registered implementation | `ray_tracing_pipeline.acceleration_structures` |
| [vktRayTracingAmberTests](../testfiles/ray_tracing_pipeline/vktRayTracingAmberTests.md) | Registered implementation | `ray_tracing_pipeline.amber` |
| [vktRayTracingBarrierTests](../testfiles/ray_tracing_pipeline/vktRayTracingBarrierTests.md) | Registered implementation | `ray_tracing_pipeline.barrier` |
| [vktRayTracingBarycentricCoordinatesTests](../testfiles/ray_tracing_pipeline/vktRayTracingBarycentricCoordinatesTests.md) | Registered implementation | `ray_tracing_pipeline.barycentric_coordinates` |
| [vktRayTracingBuildIndirectTests](../testfiles/ray_tracing_pipeline/vktRayTracingBuildIndirectTests.md) | Registered implementation | `ray_tracing_pipeline.indirect_acceleration_structure` |
| [vktRayTracingBuildLargeTests](../testfiles/ray_tracing_pipeline/vktRayTracingBuildLargeTests.md) | Registered implementation | `ray_tracing_pipeline.large_shader_set` |
| [vktRayTracingBuildTests](../testfiles/ray_tracing_pipeline/vktRayTracingBuildTests.md) | Registered implementation | `ray_tracing_pipeline.build` |
| [vktRayTracingBuiltinTests](../testfiles/ray_tracing_pipeline/vktRayTracingBuiltinTests.md) | Registered implementation | `ray_tracing_pipeline.builtin`, `ray_tracing_pipeline.spec_constants` |
| [vktRayTracingCallableShadersTests](../testfiles/ray_tracing_pipeline/vktRayTracingCallableShadersTests.md) | Registered implementation | `ray_tracing_pipeline.callable_shader` |
| [vktRayTracingCaptureReplayTests](../testfiles/ray_tracing_pipeline/vktRayTracingCaptureReplayTests.md) | Registered implementation | `ray_tracing_pipeline.capture_replay` |
| [vktRayTracingComplexControlFlowTests](../testfiles/ray_tracing_pipeline/vktRayTracingComplexControlFlowTests.md) | Registered implementation | `ray_tracing_pipeline.complexcontrolflow` |
| [vktRayTracingDataSpillTests](../testfiles/ray_tracing_pipeline/vktRayTracingDataSpillTests.md) | Registered implementation | `ray_tracing_pipeline.data_spill` |
| [vktRayTracingDirectionTests](../testfiles/ray_tracing_pipeline/vktRayTracingDirectionTests.md) | Registered implementation | `ray_tracing_pipeline.direction_length`, `ray_tracing_pipeline.inside_aabbs` |
| [vktRayTracingInvocationReorderActivityTests](../testfiles/ray_tracing_pipeline/vktRayTracingInvocationReorderActivityTests.md) | Registered implementation | `ray_tracing_pipeline.rtir_activity` |
| [vktRayTracingLimitsTests](../testfiles/ray_tracing_pipeline/vktRayTracingLimitsTests.md) | Registered implementation | `ray_tracing_pipeline.limits` |
| [vktRayTracingLinearSweptSpheresTests](../testfiles/ray_tracing_pipeline/vktRayTracingLinearSweptSpheresTests.md) | Registered implementation | `ray_tracing_pipeline.linear_swept_spheres` |
| [vktRayTracingMemGuaranteeTests](../testfiles/ray_tracing_pipeline/vktRayTracingMemGuaranteeTests.md) | Registered implementation | `ray_tracing_pipeline.memguarantee` |
| [vktRayTracingMiscTests](../testfiles/ray_tracing_pipeline/vktRayTracingMiscTests.md) | Registered implementation | `ray_tracing_pipeline.misc` |
| [vktRayTracingNonUniformArgsTests](../testfiles/ray_tracing_pipeline/vktRayTracingNonUniformArgsTests.md) | Registered implementation | `ray_tracing_pipeline.non_uniform_args` |
| [vktRayTracingNullASTests](../testfiles/ray_tracing_pipeline/vktRayTracingNullASTests.md) | Registered implementation | `ray_tracing_pipeline.null_as` |
| [vktRayTracingOpacityMicromapTests](../testfiles/ray_tracing_pipeline/vktRayTracingOpacityMicromapTests.md) | Registered implementation | `ray_tracing_pipeline.opacity_micromap` |
| [vktRayTracingPipelineFlagsTests](../testfiles/ray_tracing_pipeline/vktRayTracingPipelineFlagsTests.md) | Registered implementation | `ray_tracing_pipeline.pipeline_no_null_shaders_flag` |
| [vktRayTracingPipelineLibraryTests](../testfiles/ray_tracing_pipeline/vktRayTracingPipelineLibraryTests.md) | Registered implementation | `ray_tracing_pipeline.pipeline_library` |
| [vktRayTracingPositionFetchTests](../testfiles/ray_tracing_pipeline/vktRayTracingPositionFetchTests.md) | Registered implementation | `ray_tracing_pipeline.position_fetch` |
| [vktRayTracingProceduralGeometryTests](../testfiles/ray_tracing_pipeline/vktRayTracingProceduralGeometryTests.md) | Registered implementation | `ray_tracing_pipeline.procedural_geometry` |
| [vktRayTracingShaderBindingTableTests](../testfiles/ray_tracing_pipeline/vktRayTracingShaderBindingTableTests.md) | Registered implementation | `ray_tracing_pipeline.shader_binding_table` |
| [vktRayTracingShaderExecutionReorderTests](../testfiles/ray_tracing_pipeline/vktRayTracingShaderExecutionReorderTests.md) | Registered implementation | `ray_tracing_pipeline.ser` |
| [vktRayTracingTests](../testfiles/ray_tracing_pipeline/vktRayTracingTests.md) | Category dispatcher | `ray_tracing_pipeline` |
| [vktRayTracingTraceRaysTests](../testfiles/ray_tracing_pipeline/vktRayTracingTraceRaysTests.md) | Registered implementation | `ray_tracing_pipeline.trace_rays_cmds`, `ray_tracing_pipeline.trace_rays_cmds_maintenance_1`, `ray_tracing_pipeline.trace_rays_indirect2` |
| [vktRayTracingTraversalControlTests](../testfiles/ray_tracing_pipeline/vktRayTracingTraversalControlTests.md) | Registered implementation | `ray_tracing_pipeline.traversal_control` |
| [vktRayTracingWatertightnessTests](../testfiles/ray_tracing_pipeline/vktRayTracingWatertightnessTests.md) | Registered implementation | `ray_tracing_pipeline.watertightness` |

## Recurring Parameter Dimensions

| Theme | Observed dimensions | Evidence |
|-------|---------------------|----------|
| Build and execution modes | CPU/GPU AS build, host-thread counts, direct/indirect trace commands, indirect2 queue/copy choices | [vktRayTracingBuildTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L758-L787), [vktRayTracingTraceRaysTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L1459-L1590) |
| Shader stages and shader roles | Raygen, closest-hit, any-hit, miss, callable, and intersection roles recur in built-in, callable, SBT, data-spill, and direction tests | [vktRayTracingBuiltinTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L4772-L4803), [vktRayTracingDataSpillTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L2887-L3003) |
| Geometry and acceleration structures | Triangle, AABB, instance, top/bottom AS layouts, flags, formats, operations, and update/copy/query variants | [vktRayTracingAccelerationStructuresTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L7738-L7741), [vktRayTracingBuildIndirectTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1258-L1399) |
| Extension-specific branches | Pipeline libraries, opacity micromap, position fetch, shader execution reorder, linear swept spheres, and invocation reorder activity | [vktRayTracingPipelineLibraryTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L298-L318), [vktRayTracingOpacityMicromapTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingOpacityMicromapTests.cpp#L818-L932) |

## Recurring Support Requirements

Most implementation files require `VK_KHR_ray_tracing_pipeline`; acceleration-structure scenarios also require `VK_KHR_acceleration_structure` and feature bits, as shown by build-test support checks [vktRayTracingBuildTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L186-L205). Some branches add specific extension gates such as `VK_KHR_pipeline_library`, `VK_EXT_pipeline_library_group_handles`, `VK_EXT_graphics_pipeline_library`, and `VK_KHR_maintenance5` in pipeline-library tests [vktRayTracingPipelineLibraryTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L298-L318).

## Recurring Verification Methods

Observed verification patterns include ray tracing pipeline and SBT creation followed by shader-output checking [vktRayTracingBuildTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L437-L450), large pipeline creation with watchdog management [vktRayTracingBuildLargeTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L385-L395), pipeline-library run collection [vktRayTracingPipelineLibraryTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L615-L625), and explicit edge-case pass conditions such as empty-layout pipeline creation without crash [vktRayTracingMiscTests.cpp](../../modules/vulkan/ray_tracing/vktRayTracingMiscTests.cpp#L8753-L8765).

## Scope Notes

The actual registered source location is [external/vulkancts/modules/vulkan/ray_tracing](../../modules/vulkan/ray_tracing/) even though the category is named `ray_tracing_pipeline`. Helper/model headers without direct registration were not given separate Level-3 pages.
