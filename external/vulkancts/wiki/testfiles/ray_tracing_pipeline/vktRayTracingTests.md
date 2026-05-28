# vktRayTracingTests

This category dispatcher registers the direct children under `ray_tracing_pipeline`. The category root group is constructed from the dispatcher name in [vktRayTracingTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L65-L67), and each child is added in [vktRayTracingTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L69-L102).

## Source Files

| Role | Link |
|------|------|
| Category dispatcher | [vktRayTracingTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L65-L104) |
| Dispatcher header | [vktRayTracingTests.hpp](../../../modules/vulkan/ray_tracing/vktRayTracingTests.hpp#L29-L35) |

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

### amber — Amber-scripted cases

Registered by [vktRayTracingTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L69) and constructed as `amber` in [vktRayTracingAmberTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingAmberTests.cpp#L33-L35).

### builtin — Ray tracing shader built-ins

Registered by [vktRayTracingTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L70) and constructed as `builtin` in [vktRayTracingBuiltinTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L4753-L4795).

### spec_constants — Specialization constants

Registered by [vktRayTracingTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L71) and constructed as `spec_constants` in [vktRayTracingBuiltinTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L4809-L4812).

### large_shader_set — Large shader sets

Registered by [vktRayTracingTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L72) and constructed as `large_shader_set` in [vktRayTracingBuildLargeTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L571-L574).

### build — Acceleration-structure build modes

Registered by [vktRayTracingTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L73) and constructed as `build` in [vktRayTracingBuildTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L753-L756).

### callable_shader — Callable shader invocation

Registered by [vktRayTracingTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L74) and constructed as `callable_shader` in [vktRayTracingCallableShadersTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L1975-L1978).

### trace_rays_cmds — Trace rays commands

Registered by [vktRayTracingTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L75) and constructed as `trace_rays_cmds` in [vktRayTracingTraceRaysTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L1459-L1462).

### trace_rays_cmds_maintenance_1 — Maintenance1 trace rays commands

Registered by [vktRayTracingTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L76) and constructed as `trace_rays_cmds_maintenance_1` in [vktRayTracingTraceRaysTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L1504-L1507).

### shader_binding_table — Shader binding table behavior

Registered by [vktRayTracingTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L77) and constructed as `shader_binding_table` in [vktRayTracingShaderBindingTableTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L1617-L1620).

### traversal_control — Hit/intersection traversal control

Registered by [vktRayTracingTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L78) and constructed as `traversal_control` in [vktRayTracingTraversalControlTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L766-L769).

### acceleration_structures — AS construction and operations

Registered by [vktRayTracingTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L79) and constructed as `acceleration_structures` in [vktRayTracingAccelerationStructuresTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L7738-L7740).

### procedural_geometry — Procedural AABB geometry

Registered by [vktRayTracingTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L80) and constructed as `procedural_geometry` in [vktRayTracingProceduralGeometryTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingProceduralGeometryTests.cpp#L611-L614).

### indirect_acceleration_structure — Indirect AS build/update

Registered by [vktRayTracingTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L81) and constructed as `indirect_acceleration_structure` in [vktRayTracingBuildIndirectTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1254-L1390).

### watertightness — Watertight intersection consistency

Registered by [vktRayTracingTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L82) and constructed as `watertightness` in [vktRayTracingWatertightnessTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingWatertightnessTests.cpp#L872-L875).

### pipeline_library — Ray tracing pipeline libraries

Registered by [vktRayTracingTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L83) and constructed as `pipeline_library` in [vktRayTracingPipelineLibraryTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L1225-L1227).

### memguarantee — Memory guarantee cases

Registered by [vktRayTracingTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L84) and constructed as `memguarantee` in [vktRayTracingMemGuaranteeTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingMemGuaranteeTests.cpp#L855-L877).

### null_as — Null acceleration structure

Registered by [vktRayTracingTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L85) and constructed as `null_as` in [vktRayTracingNullASTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingNullASTests.cpp#L756-L759).

### capture_replay — Capture/replay configurations

Registered by [vktRayTracingTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L86) and constructed as `capture_replay` in [vktRayTracingCaptureReplayTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L1729-L1731).

### misc — Miscellaneous edge cases

Registered by [vktRayTracingTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L87) and constructed as `misc` in [vktRayTracingMiscTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingMiscTests.cpp#L10904-L10908).

### complexcontrolflow — Complex shader control flow

Registered by [vktRayTracingTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L88) and constructed as `complexcontrolflow` in [vktRayTracingComplexControlFlowTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L1797-L1845).

### barrier — Barriers involving ray tracing stages

Registered by [vktRayTracingTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L89) and constructed as `barrier` in [vktRayTracingBarrierTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBarrierTests.cpp#L1750-L1753).

### data_spill — Data spilling around calls

Registered by [vktRayTracingTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L90) and constructed as `data_spill` in [vktRayTracingDataSpillTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L2887-L2890).

### direction_length — Direction-vector length

Registered by [vktRayTracingTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L91) and constructed as `direction_length` in [vktRayTracingDirectionTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingDirectionTests.cpp#L681-L684).

### inside_aabbs — Rays starting inside AABBs

Registered by [vktRayTracingTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L92) and constructed as `inside_aabbs` in [vktRayTracingDirectionTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingDirectionTests.cpp#L775-L778).

### barycentric_coordinates — Hit barycentrics

Registered by [vktRayTracingTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L93) and constructed as `barycentric_coordinates` in [vktRayTracingBarycentricCoordinatesTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBarycentricCoordinatesTests.cpp#L498-L503).

### non_uniform_args — Non-uniform trace arguments

Registered by [vktRayTracingTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L94) and constructed as `non_uniform_args` in [vktRayTracingNonUniformArgsTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingNonUniformArgsTests.cpp#L517-L520).

### pipeline_no_null_shaders_flag — No-null-shader pipeline flags

Registered by [vktRayTracingTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L95) and constructed as `pipeline_no_null_shaders_flag` in [vktRayTracingPipelineFlagsTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L1528-L1573).

### trace_rays_indirect2 — Indirect2 trace rays

Registered by [vktRayTracingTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L96) and constructed as `trace_rays_indirect2` in [vktRayTracingTraceRaysTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L1551-L1553).

### opacity_micromap — Opacity micromap

Registered by [vktRayTracingTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L97) and constructed as `opacity_micromap` in [vktRayTracingOpacityMicromapTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingOpacityMicromapTests.cpp#L818-L821).

### position_fetch — Ray tracing position fetch

Registered by [vktRayTracingTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L98) and constructed as `position_fetch` in [vktRayTracingPositionFetchTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingPositionFetchTests.cpp#L529-L532).

### ser — Shader execution reorder

Registered by [vktRayTracingTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L99) and constructed as `ser` in [vktRayTracingShaderExecutionReorderTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingShaderExecutionReorderTests.cpp#L2253-L2256).

### linear_swept_spheres — Linear swept spheres

Registered by [vktRayTracingTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L100) and constructed as `linear_swept_spheres` in [vktRayTracingLinearSweptSpheresTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingLinearSweptSpheresTests.cpp#L960-L1029).

### limits — Reported properties

Registered by [vktRayTracingTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L101) and constructed as `limits` in [vktRayTracingLimitsTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingLimitsTests.cpp#L277-L282).

### rtir_activity — Invocation reorder activity

Registered by [vktRayTracingTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L102) and constructed as `rtir_activity` in [vktRayTracingInvocationReorderActivityTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingInvocationReorderActivityTests.cpp#L634-L637).

## Parameter Dimensions

The dispatcher itself has no generated parameters; it delegates to implementation files through `addChild()` calls [vktRayTracingTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L69-L102).

## Support / Feature Requirements

The dispatcher does not perform feature checks; implementation files check support before execution, for example [vktRayTracingBuildTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L186-L205).

## Verification Methods

The dispatcher does not verify results; child files implement pipeline creation, dispatch, and comparisons, such as [vktRayTracingBuildTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L437-L450).

## Test Principles

The file is a dispatcher: it fixes the top-level order and delegates all parameters, support gates, and verification to child source files through direct `addChild()` registrations [vktRayTracingTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L69-L102).

## Notes
