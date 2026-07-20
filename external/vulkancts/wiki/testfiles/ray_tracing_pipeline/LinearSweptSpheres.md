## Overview

**Core question:** Does the implementation correctly build, traverse, and report hits for the `VK_NV_ray_tracing_linear_swept_spheres` geometry types (standalone spheres and linear swept spheres) across indexing modes, endcap configurations, BLAS copy, ray-query, hit-object, vertex-format, and radius-format choices?

This page covers one test family registered from [vktRayTracingLinearSweptSpheresTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingLinearSweptSpheresTests.cpp#L960-L1149):

- `linear_swept_spheres` registers two direct children: `spheres` and `lss`. The two children switch between the two new bottom-level acceleration structure geometry types introduced by `VK_NV_ray_tracing_linear_swept_spheres`.
- Each case builds a bottom-level acceleration structure with sphere or LSS geometry, traces rays at known vertex positions, and checks that the accumulated hit count in a result buffer matches the expected value for the geometry type, test type, and endcap configuration.
- The test matrix varies seven configuration dimensions on top of the geometry type: test type (vertices, indices, indexing mode list, indexing mode successive), BLAS copy, endcaps, ray query, hit object, vertex format, and radius format. Pruning rules remove invalid combinations.

## Background Knowledge

- `VK_NV_ray_tracing_linear_swept_spheres` adds two new bottom-level acceleration structure geometry types: `VK_GEOMETRY_TYPE_SPHERES_NV` for standalone sphere primitives and `VK_GEOMETRY_TYPE_LINEAR_SWEPT_SPHERES_NV` for capsule-like swept sphere primitives. Each vertex has a paired radius.
- The ray tracing pipeline must set `VK_PIPELINE_CREATE_2_RAY_TRACING_ALLOW_SPHERES_AND_LINEAR_SWEPT_SPHERES_BIT_NV` or the implementation will not traverse these geometry types.
- LSS indexing modes control how the index buffer defines segments: `VK_RAY_TRACING_LSS_INDEXING_MODE_LIST_NV` treats each index pair as one independent segment; `VK_RAY_TRACING_LSS_INDEXING_MODE_SUCCESSIVE_NV` treats the index list as a polyline chain.
- LSS endcaps control whether the sphere at each segment endpoint is part of the geometry. With endcaps enabled, rays that hit the endpoint sphere report a hit. With endcaps disabled, only the swept surface between endpoints is tested.
- Hit classification built-ins identify which geometry type was hit: `gl_HitIsSphereNV` and `gl_HitIsLSSNV` in closest-hit shaders, `rayQueryIsSphereHitNV` and `rayQueryIsLSSHitNV` for ray queries, and `hitObjectIsSphereHitNV` and `hitObjectIsLSSHitNV` for hit objects.
- The custom device is created without `VK_KHR_pipeline_library` to verify that the LSS extension works without it.

## Registration Hierarchy

```text
ray_tracing_pipeline.linear_swept_spheres
├── lss
└── spheres
```

Each direct child is a test group that expands through nested intermediate nodes: `<test_type>.<blas_copy>.<endcaps>.<ray_query>.<hit_object>.<vertex_format>.<radius_format>`. The test type dimension has four registered values (`vertices`, `indices`, `indexing_mode_list`, `indexing_mode_successive`), but pruning rules restrict which values are valid for each geometry type. The full leaf path for a case looks like `ray_tracing_pipeline.linear_swept_spheres.lss.indexing_mode_list.no_blascopy.endcaps.no_use_ray_query.no_use_hit_object.float3.float`.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Geometry type | `spheres`, `lss` | Selects the BLAS geometry type: standalone spheres or linear swept spheres. Changes the hit-classification built-in checked by the shader and the expected hit-count formula. | [vktRayTracingLinearSweptSpheresTests.cpp#L1030-L1033](../../../modules/vulkan/ray_tracing/vktRayTracingLinearSweptSpheresTests.cpp#L1030-L1033) |
| Test type | `vertices`, `indices`, `indexing_mode_list`, `indexing_mode_successive` | Controls how the BLAS uses vertex and index data. `vertices` uses all vertices without an index buffer. `indices` uses an index buffer with `VK_INDEX_TYPE_UINT32`. `indexing_mode_list` and `indexing_mode_successive` select the LSS indexing mode. | [vktRayTracingLinearSweptSpheresTests.cpp#L1035-L1038](../../../modules/vulkan/ray_tracing/vktRayTracingLinearSweptSpheresTests.cpp#L1035-L1038) |
| BLAS copy | `no_blascopy`, `blascopy` | When enabled, the test compact-copies the built BLAS before traversal, exercising the copy path for the new geometry types. | [vktRayTracingLinearSweptSpheresTests.cpp#L994-L998](../../../modules/vulkan/ray_tracing/vktRayTracingLinearSweptSpheresTests.cpp#L994-L998) |
| Endcaps | `no_endcaps`, `endcaps` | Controls whether LSS segment endpoint spheres are part of the geometry. Changes the expected hit count. Pruned for `spheres` because standalone spheres are always full spheres. | [vktRayTracingLinearSweptSpheresTests.cpp#L1000-L1007](../../../modules/vulkan/ray_tracing/vktRayTracingLinearSweptSpheresTests.cpp#L1000-L1007) |
| Ray query | `no_use_ray_query`, `use_ray_query` | When enabled, the raygen shader uses `rayQueryEXT` instead of `traceRayEXT`. Hit classification uses `rayQueryIsSphereHitNV` or `rayQueryIsLSSHitNV` inside the raygen shader. | [vktRayTracingLinearSweptSpheresTests.cpp#L1009-L1016](../../../modules/vulkan/ray_tracing/vktRayTracingLinearSweptSpheresTests.cpp#L1009-L1016) |
| Hit object | `no_use_hit_object`, `use_hit_object` | When enabled, the raygen shader uses `hitObjectTraceRayNV` from `GL_NV_shader_invocation_reorder`. Hit classification uses `hitObjectIsSphereHitNV` or `hitObjectIsLSSHitNV`. | [vktRayTracingLinearSweptSpheresTests.cpp#L1018-L1025](../../../modules/vulkan/ray_tracing/vktRayTracingLinearSweptSpheresTests.cpp#L1018-L1025) |
| Vertex format | `float3`, `float2`, `half3`, `half2` | Controls vertex position format: 3D or 2D (z implied zero), 32-bit or 16-bit float. Maps to `VK_FORMAT_R32G32B32_SFLOAT`, `VK_FORMAT_R32G32_SFLOAT`, `VK_FORMAT_R16G16B16_SFLOAT`, `VK_FORMAT_R16G16_SFLOAT`. | [vktRayTracingLinearSweptSpheresTests.cpp#L1040-L1045](../../../modules/vulkan/ray_tracing/vktRayTracingLinearSweptSpheresTests.cpp#L1040-L1045) |
| Radius format | `float`, `half` | Controls radius data format: `VK_FORMAT_R32_SFLOAT` or `VK_FORMAT_R16_SFLOAT`. | [vktRayTracingLinearSweptSpheresTests.cpp#L1047-L1050](../../../modules/vulkan/ray_tracing/vktRayTracingLinearSweptSpheresTests.cpp#L1047-L1050) |

## Behavior Parameters

The primary behavioral axis is the geometry type: the direct child of `linear_swept_spheres`. The two values change what is being tested. `spheres` exercises standalone sphere geometry. `lss` exercises linear swept sphere geometry with its own indexing modes, endcap configurations, and hit-classification built-ins. All other dimensions are configuration choices that modify how the geometry is built, traversed, or queried.

### spheres — Standalone sphere geometry via VK_GEOMETRY_TYPE_SPHERES_NV

The host builds a BLAS with `VK_GEOMETRY_TYPE_SPHERES_NV` containing 16 sphere vertices with per-vertex radii. The `testType` dimension has two valid values for this geometry type: `vertices` uses all 16 vertices without an index buffer, and `indices` uses an 8-element index buffer to select a subset of spheres. The expected hit count is 12 for `vertices` (the raygen shader shoots 12 rays at 12 of the 16 vertex positions) and 8 for `indices` (the raygen shader shoots 12 rays, but only 8 hit indexed spheres).

The `no_endcaps` branch is pruned because standalone spheres are always full spheres. The `indexing_mode_list` and `indexing_mode_successive` branches are pruned because those test types are LSS-specific.

### lss — Linear swept sphere geometry via VK_GEOMETRY_TYPE_LINEAR_SWEPT_SPHERES_NV

The host builds a BLAS with `VK_GEOMETRY_TYPE_LINEAR_SWEPT_SPHERES_NV`. The `testType` dimension has three valid values: `vertices`, `indexing_mode_list`, and `indexing_mode_successive`. The `indices` test type is pruned because LSS uses indexing modes rather than a plain index buffer. The expected hit count depends on the test type and endcap configuration:

- `vertices` with `endcaps`: 12 hits.
- `indexing_mode_list` with `endcaps`: 6 hits.
- `indexing_mode_successive` with `endcaps`: 10 hits.
- `indexing_mode_list` with `no_endcaps`: 1 hit.
- `indexing_mode_successive` with `no_endcaps`: 3 hits.

The `no_endcaps` branch uses 3 geometry vertices at `(2, 0, -15)`, `(6, 0, -15)`, `(10, 0, -15)` with radius 2.0 and a 5-ray shader loop. The `endcaps` branch uses 16 geometry vertices arranged in pairs across the x-axis and a 12-ray shader loop. The `float2` and `half2` vertex formats are pruned for `no_endcaps` because 2D vertex positions are not supported for that configuration.

## Shader Analysis

The page uses one representative walkthrough. The `traceRayEXT` path for LSS with endcaps and `indexing_mode_list` is the simplest case that exercises the core LSS geometry traversal through the standard pipeline path. The ray-query and hit-object paths change the ray dispatch mechanism and hit-classification logic inside the raygen shader, but the geometry building and expected hit count remain the same. The closest-hit and miss shaders are short payload-setting one-liners covered in `## Behavior Parameters`.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.ray_tracing_pipeline.linear_swept_spheres.lss.indexing_mode_list.no_blascopy.endcaps.no_use_ray_query.no_use_hit_object.float3.float
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `lss` geometry type | Exercises `VK_GEOMETRY_TYPE_LINEAR_SWEPT_SPHERES_NV`, the core new geometry type |
| `indexing_mode_list` | Uses `VK_RAY_TRACING_LSS_INDEXING_MODE_LIST_NV` with 12 indices defining 6 segments |
| `endcaps` | Endcap spheres at segment endpoints are part of the geometry; 6 of 12 rays hit endcap spheres |
| `no_use_ray_query`, `no_use_hit_object` | Uses the standard `traceRayEXT` pipeline path; closest-hit shader sets payload to 1 on hit |
| `float3` vertex format, `float` radius format | Default 32-bit formats for positions and radii |

#### Purpose

The raygen shader fires 12 rays from positions at `z = 1` in direction `(0, 0, -1)` toward LSS geometry at `z = -15`. It accumulates the hit count across all 12 rays and writes the total to a storage buffer. The host checks that the accumulated count equals 6, verifying that the implementation correctly built and traversed LSS geometry with endcaps and list indexing.

#### Structural Design

| Phase | What happens |
|-------|--------------|
| Initialize | Set `tmin = 0.001`, `tmax = 1000.0`, `hitValue = 0`, `results = 0` |
| Define vertices | 12 ray origin positions matching the first 12 LSS geometry vertices (same x, y; z = 1 instead of -15) |
| Loop 12 rays | For each vertex: call `traceRayEXT` from the vertex position in direction `(0, 0, -1)`; accumulate `results += hitValue` |
| Store result | Write `results + 0xFF000000` to `result.value[launchIndex]` |

The closest-hit shader sets `hitValue = 1` on every hit. The miss shader sets `hitValue = 0`. Six rays hit endcap spheres at segment endpoints; six rays pass through positions that do not coincide with any swept surface or endcap and miss.

#### Shader Code

```glsl
#version 460
#extension GL_EXT_ray_tracing : enable
#extension GL_EXT_ray_query : enable
#extension GL_NV_shader_invocation_reorder : enable
#extension GL_NV_linear_swept_spheres : enable
/// Top-level acceleration structure at set 0, binding 0.
/// Holds one instance referencing the LSS bottom-level acceleration structure.
layout(binding = 0, set = 0) uniform accelerationStructureEXT topLevelAS;
/// Result storage buffer at set 0, binding 1.
/// 64x64 int entries; raygen writes accumulated hit count + 0xFF000000.
layout(set = 0, binding = 1, std430) writeonly buffer Result {
    int value[];
} result;
/// Ray payload: 1 on hit (closest-hit), 0 on miss.
layout(location = 0) rayPayloadEXT int hitValue;

void main()
{
    float tmin = 0.001;
    float tmax = 1000.0;

    hitValue = 0;
    int results = 0;

    /// 12 ray origin positions at z=1, matching the first 12 LSS geometry
    /// vertices (same x,y; geometry lives at z=-15). Rays fire in -z toward
    /// the geometry. 6 of 12 positions coincide with segment endpoint
    /// endcap spheres; the other 6 miss.
    vec3 vertices[12] = vec3[12](
        vec3(-8, 7, 1),  // Vertex 1
        vec3(8, 7, 1),   // Vertex 2
        vec3(8, 5, 1),   // Vertex 3
        vec3(-8, 5, 1),  // Vertex 4
        vec3(-8, 3, 1),  // Vertex 5
        vec3(8, 3, 1),   // Vertex 6
        vec3(8, 1, 1),   // Vertex 7
        vec3(-8, 1, 1),  // Vertex 8
        vec3(-8, -1, 1), // Vertex 9
        vec3(8, -1, 1),  // Vertex 10
        vec3(8, -3, 1),  // Vertex 11
        vec3(-8, -3, 1)  // Vertex 12
    );

    // Shoot rays at the vertices
    for (int i = 0; i < 12; i++) {
        vec3 vertex = vertices[i];

        vec3 direction = vec3(0,0,-1);
        // Trace a ray from 'origin' towards the 'vertex' in the direction
        traceRayEXT(topLevelAS, 0, 0xff, 0, 1, 0, vertex, tmin, vec3(0,0,-1), tmax, 0);
        // Store the result by adding the hit value with the constant 0xFF000000
        results += hitValue;
    }
    uint  resultIndex = gl_LaunchIDEXT.x + gl_LaunchIDEXT.y * gl_LaunchSizeEXT.x;
    result.value[resultIndex] = results + 0xFF000000;
};
```

#### Additional Info

- The closest-hit shader for this case computes `cond = gl_HitIsLSSNV && !gl_HitIsSphereNV` but always sets `hitValue = 1` regardless of `cond`. The `cond` variable is dead code on the `traceRayEXT` path. The hit-classification built-ins are only load-bearing when `use_ray_query` or `use_hit_object` is active, because those paths set `hitValue = int(cond)` inside the raygen shader.
- The `0xFF000000` constant sets the alpha byte to 0xFF so the host can interpret the result buffer as `R8G8B8A8_UNORM` and read the hit count from the red channel (byte 0, the least significant byte).
- The `direction` variable in the shader is declared but unused; `traceRayEXT` receives `vec3(0,0,-1)` directly as the direction argument.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Geometry type (`spheres`) | Replaces the 12-vertex LSS array with a 12-vertex sphere array in a different order. The closest-hit shader switches to `gl_HitIsSphereNV && !gl_HitIsLSSNV`. | [vktRayTracingLinearSweptSpheresTests.cpp#L798-L815](../../../modules/vulkan/ray_tracing/vktRayTracingLinearSweptSpheresTests.cpp#L798-L815) |
| Endcaps (`no_endcaps`) | Replaces the 12-vertex array with a 5-vertex `noendCapsVertices` array and loops 5 times instead of 12. | [vktRayTracingLinearSweptSpheresTests.cpp#L834-L847](../../../modules/vulkan/ray_tracing/vktRayTracingLinearSweptSpheresTests.cpp#L834-L847) |
| Ray query (`use_ray_query`) | Replaces `traceRayEXT` with `rayQueryInitializeEXT` + `rayQueryProceedEXT` + `rayQueryGetIntersectionTypeEXT`. Sets `hitValue = int(rayQueryIsLSSHitNV(rq, true))` inside the raygen shader. Closest-hit shader is not invoked. | [vktRayTracingLinearSweptSpheresTests.cpp#L856-L883](../../../modules/vulkan/ray_tracing/vktRayTracingLinearSweptSpheresTests.cpp#L856-L883) |
| Hit object (`use_hit_object`) | Replaces `traceRayEXT` with `hitObjectTraceRayNV` + `reorderThreadNV` + `hitObjectIsHitNV`. Sets `hitValue = int(hitObjectIsLSSHitNV(hObj))` inside the raygen shader. | [vktRayTracingLinearSweptSpheresTests.cpp#L885-L908](../../../modules/vulkan/ray_tracing/vktRayTracingLinearSweptSpheresTests.cpp#L885-L908) |

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
; Bound: 104
; Schema: 0
               OpCapability RayTracingKHR
               OpExtension "SPV_KHR_ray_tracing"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint RayGenerationKHR %main "main" %hitValue %topLevelAS %gl_LaunchIDEXT %gl_LaunchSizeEXT %result
               OpSource GLSL 460
               OpSourceExtension "GL_EXT_ray_query"
               OpSourceExtension "GL_EXT_ray_tracing"
               OpSourceExtension "GL_NV_linear_swept_spheres"
               OpSourceExtension "GL_NV_shader_invocation_reorder"
               OpName %main "main"
               OpName %tmin "tmin"
               OpName %tmax "tmax"
               OpName %hitValue "hitValue"
               OpName %results "results"
               OpName %vertices "vertices"
               OpName %i "i"
               OpName %vertex "vertex"
               OpName %direction "direction"
               OpName %topLevelAS "topLevelAS"
               OpName %resultIndex "resultIndex"
               OpName %gl_LaunchIDEXT "gl_LaunchIDEXT"
               OpName %gl_LaunchSizeEXT "gl_LaunchSizeEXT"
               OpName %Result "Result"
               OpMemberName %Result 0 "value"
               OpName %result "result"
               OpDecorate %topLevelAS Binding 0
               OpDecorate %topLevelAS DescriptorSet 0
               OpDecorate %gl_LaunchIDEXT BuiltIn LaunchIdKHR
               OpDecorate %gl_LaunchSizeEXT BuiltIn LaunchSizeKHR
               OpDecorate %_runtimearr_int ArrayStride 4
               OpDecorate %Result Block
               OpMemberDecorate %Result 0 NonReadable
               OpMemberDecorate %Result 0 Offset 0
               OpDecorate %result NonReadable
               OpDecorate %result Binding 1
               OpDecorate %result DescriptorSet 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
%_ptr_Function_float = OpTypePointer Function %float
%float_0_00100000005 = OpConstant %float 0.00100000005
 %float_1000 = OpConstant %float 1000
        %int = OpTypeInt 32 1
%_ptr_RayPayloadKHR_int = OpTypePointer RayPayloadKHR %int
   %hitValue = OpVariable %_ptr_RayPayloadKHR_int RayPayloadKHR
      %int_0 = OpConstant %int 0
%_ptr_Function_int = OpTypePointer Function %int
    %v3float = OpTypeVector %float 3
       %uint = OpTypeInt 32 0
    %uint_12 = OpConstant %uint 12
%_arr_v3float_uint_12 = OpTypeArray %v3float %uint_12
%_ptr_Function__arr_v3float_uint_12 = OpTypePointer Function %_arr_v3float_uint_12
   %float_n8 = OpConstant %float -8
    %float_7 = OpConstant %float 7
    %float_1 = OpConstant %float 1
         %27 = OpConstantComposite %v3float %float_n8 %float_7 %float_1
    %float_8 = OpConstant %float 8
         %29 = OpConstantComposite %v3float %float_8 %float_7 %float_1
    %float_5 = OpConstant %float 5
         %31 = OpConstantComposite %v3float %float_8 %float_5 %float_1
         %32 = OpConstantComposite %v3float %float_n8 %float_5 %float_1
    %float_3 = OpConstant %float 3
         %34 = OpConstantComposite %v3float %float_n8 %float_3 %float_1
         %35 = OpConstantComposite %v3float %float_8 %float_3 %float_1
         %36 = OpConstantComposite %v3float %float_8 %float_1 %float_1
         %37 = OpConstantComposite %v3float %float_n8 %float_1 %float_1
   %float_n1 = OpConstant %float -1
         %39 = OpConstantComposite %v3float %float_n8 %float_n1 %float_1
         %40 = OpConstantComposite %v3float %float_8 %float_n1 %float_1
   %float_n3 = OpConstant %float -3
         %42 = OpConstantComposite %v3float %float_8 %float_n3 %float_1
         %43 = OpConstantComposite %v3float %float_n8 %float_n3 %float_1
         %44 = OpConstantComposite %_arr_v3float_uint_12 %27 %29 %31 %32 %34 %35 %36 %37 %39 %40 %42 %43
     %int_12 = OpConstant %int 12
       %bool = OpTypeBool
%_ptr_Function_v3float = OpTypePointer Function %v3float
    %float_0 = OpConstant %float 0
         %62 = OpConstantComposite %v3float %float_0 %float_0 %float_n1
         %63 = OpTypeAccelerationStructureKHR
%_ptr_UniformConstant_63 = OpTypePointer UniformConstant %63
 %topLevelAS = OpVariable %_ptr_UniformConstant_63 UniformConstant
     %uint_0 = OpConstant %uint 0
   %uint_255 = OpConstant %uint 255
     %uint_1 = OpConstant %uint 1
      %int_1 = OpConstant %int 1
%_ptr_Function_uint = OpTypePointer Function %uint
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_LaunchIDEXT = OpVariable %_ptr_Input_v3uint Input
%_ptr_Input_uint = OpTypePointer Input %uint
%gl_LaunchSizeEXT = OpVariable %_ptr_Input_v3uint Input
%_runtimearr_int = OpTypeRuntimeArray %int
     %Result = OpTypeStruct %_runtimearr_int
%_ptr_StorageBuffer_Result = OpTypePointer StorageBuffer %Result
     %result = OpVariable %_ptr_StorageBuffer_Result StorageBuffer
%int_n16777216 = OpConstant %int -16777216
%_ptr_StorageBuffer_int = OpTypePointer StorageBuffer %int
       %main = OpFunction %void None %3
          %5 = OpLabel
       %tmin = OpVariable %_ptr_Function_float Function
       %tmax = OpVariable %_ptr_Function_float Function
    %results = OpVariable %_ptr_Function_int Function
   %vertices = OpVariable %_ptr_Function__arr_v3float_uint_12 Function
          %i = OpVariable %_ptr_Function_int Function
     %vertex = OpVariable %_ptr_Function_v3float Function
  %direction = OpVariable %_ptr_Function_v3float Function
%resultIndex = OpVariable %_ptr_Function_uint Function
               OpStore %tmin %float_0_00100000005
               OpStore %tmax %float_1000
               OpStore %hitValue %int_0
               OpStore %results %int_0
               OpStore %vertices %44
               OpStore %i %int_0
               OpBranch %46
         %46 = OpLabel
               OpLoopMerge %48 %49 None
               OpBranch %50
         %50 = OpLabel
         %51 = OpLoad %int %i
         %54 = OpSLessThan %bool %51 %int_12
               OpBranchConditional %54 %47 %48
         %47 = OpLabel
         %57 = OpLoad %int %i
         %58 = OpAccessChain %_ptr_Function_v3float %vertices %57
         %59 = OpLoad %v3float %58
               OpStore %vertex %59
               OpStore %direction %62
         %66 = OpLoad %63 %topLevelAS
         %70 = OpLoad %v3float %vertex
         %71 = OpLoad %float %tmin
         %72 = OpLoad %float %tmax
               OpTraceRayKHR %66 %uint_0 %uint_255 %uint_0 %uint_1 %uint_0 %70 %71 %62 %72 %hitValue
         %73 = OpLoad %int %hitValue
         %74 = OpLoad %int %results
         %75 = OpIAdd %int %74 %73
               OpStore %results %75
               OpBranch %49
         %49 = OpLabel
         %76 = OpLoad %int %i
         %78 = OpIAdd %int %76 %int_1
               OpStore %i %78
               OpBranch %46
         %48 = OpLabel
         %85 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_0
         %86 = OpLoad %uint %85
         %87 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_1
         %88 = OpLoad %uint %87
         %90 = OpAccessChain %_ptr_Input_uint %gl_LaunchSizeEXT %uint_0
         %91 = OpLoad %uint %90
         %92 = OpIMul %uint %88 %91
         %93 = OpIAdd %uint %86 %92
               OpStore %resultIndex %93
         %98 = OpLoad %uint %resultIndex
         %99 = OpLoad %int %results
        %101 = OpIAdd %int %99 %int_n16777216
        %103 = OpAccessChain %_ptr_StorageBuffer_int %result %int_0 %98
               OpStore %103 %101
               OpReturn
               OpFunctionEnd
```

</details>## Runtime Execution and Result Checking

The test instance `LinearSweptSpheresTestInstance::iterate` builds all resources and records a single command buffer per case.

Resource setup:

- A custom device created with `VK_KHR_ray_tracing_pipeline`, `VK_KHR_acceleration_structure`, `VK_KHR_deferred_host_operations`, `VK_KHR_buffer_device_address`, `VK_EXT_descriptor_indexing`, `VK_KHR_spirv_1_4`, `VK_KHR_shader_float_controls`, and `VK_NV_ray_tracing_linear_swept_spheres` extensions. The device is created without `VK_KHR_pipeline_library`.
- A ray tracing pipeline with the `VK_PIPELINE_CREATE_2_RAY_TRACING_ALLOW_SPHERES_AND_LINEAR_SWEPT_SPHERES_BIT_NV` flag. The `SpheresTestInstance` also sets `VK_PIPELINE_CREATE_2_RAY_TRACING_SKIP_BUILT_IN_PRIMITIVES_BIT_KHR` when `skipBuiltinPrimitives` is true (not exercised in the registered matrix because `skipBuiltinPrimitives` is always false in `TestParams`).
- A bottom-level acceleration structure built with sphere or LSS geometry data. The `addSphereGeometry` framework helper selects `VK_GEOMETRY_TYPE_LINEAR_SWEPT_SPHERES_NV` or `VK_GEOMETRY_TYPE_SPHERES_NV` based on the `linear` parameter.
- A top-level acceleration structure with one instance referencing the BLAS.
- Two storage buffers (reference and result) of `64 * 64 * sizeof(int)` bytes, cleared to `0x01` before the trace.
- Shader binding table regions for raygen, closest-hit, and miss shader groups, sized from `shaderGroupHandleSize` and `shaderGroupBaseAlignment`.

Command buffer recording:

- Build the BLAS and TLAS inside the command buffer.
- Update the descriptor set with the TLAS (binding 0) and reference storage buffer (binding 1).
- Pipeline barrier from `TRANSFER_BIT` to `RAY_TRACING_SHADER_BIT_KHR` for buffer upload, and from `ACCELERATION_STRUCTURE_BUILD_BIT_KHR` to `RAY_TRACING_SHADER_BIT_KHR` for AS build.
- Bind pipeline and descriptor sets, then call `cmdTraceRays` with launch size `64 x 64 x 1`.
- Pipeline barrier from `RAY_TRACING_SHADER_BIT_KHR` to `TRANSFER_BIT`.

Result checking in `iterate`:

- Invalidate the mapped reference buffer.
- Interpret the buffer as `R8G8B8A8_UNORM` with 64x64 pixels.
- For every pixel, read the red channel and compare against the expected hit count:
  - `spheres` with `vertices`: expect 12.
  - `spheres` with `indices`: expect 8.
  - `lss` with `vertices` and `endcaps`: expect 12.
  - `lss` with `indexing_mode_list` and `endcaps`: expect 6.
  - `lss` with `indexing_mode_successive` and `endcaps`: expect 10.
  - `lss` with `indexing_mode_list` and `no_endcaps`: expect 1.
  - `lss` with `indexing_mode_successive` and `no_endcaps`: expect 3.
- Any pixel whose red channel does not match the expected count fails the test.
- Invalid combinations detected at validation time return `QP_TEST_RESULT_NOT_SUPPORTED`.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `spheres` | The implementation incorrectly built, traversed, or reported hits for standalone sphere geometry (`VK_GEOMETRY_TYPE_SPHERES_NV`). The hit count in the result buffer does not match the expected 12 (vertices) or 8 (indices). |
| `lss` | The implementation incorrectly built, traversed, or reported hits for linear swept sphere geometry (`VK_GEOMETRY_TYPE_LINEAR_SWEPT_SPHERES_NV`). The hit count does not match the expected value for the given indexing mode, endcap, and test-type combination. Includes incorrect hit classification by `gl_HitIsLSSNV`, `rayQueryIsLSSHitNV`, or `hitObjectIsLSSHitNV` when those paths are active. |

### Cause Analysis

#### Incorrect sphere geometry building or traversal

**Possible failure symptoms:** The `spheres` child fails. The red channel of one or more result buffer pixels differs from the expected 12 (vertices) or 8 (indices). The mismatch may appear as a lower count (missed hits) or a higher count (spurious hits).

**Possible implementation causes:** The acceleration structure builder did not correctly encode standalone sphere vertex and radius data for `VK_GEOMETRY_TYPE_SPHERES_NV`. The traversal engine did not test rays against the sphere surfaces correctly, producing misses at positions that should hit or hits at positions that should miss. The `VK_PIPELINE_CREATE_2_RAY_TRACING_ALLOW_SPHERES_AND_LINEAR_SWEPT_SPHERES_BIT_NV` pipeline flag was not honored, causing the pipeline to skip the new geometry types entirely. When `doBlasCopy` is true, the BLAS compact copy path dropped or corrupted sphere geometry data.

#### Incorrect LSS geometry building or traversal

**Possible failure symptoms:** The `lss` child fails. The red channel of one or more result buffer pixels differs from the expected hit count for the given indexing mode, endcap, and test-type combination. The mismatch may appear as a lower count (missed hits on endcap spheres or swept surfaces) or a higher count (spurious hits).

**Possible implementation causes:** The acceleration structure builder did not correctly encode LSS vertex, radius, and index data for `VK_GEOMETRY_TYPE_LINEAR_SWEPT_SPHERES_NV`. The indexing mode (`LIST_NV` or `SUCCESSIVE_NV`) was interpreted incorrectly, producing a different number of segments than expected. The endcap configuration was not honored: endcap spheres were not included when enabled, or were included when disabled. The traversal engine did not test rays against the swept surface or endcap spheres correctly. When `doBlasCopy` is true, the BLAS compact copy path dropped or corrupted LSS geometry data.

#### Incorrect hit classification by LSS or sphere built-ins

**Possible failure symptoms:** The `lss` or `spheres` child fails only when `use_ray_query` or `use_hit_object` is active. The hit count is lower or higher than expected because the raygen shader's `cond` check misclassified hits. For example, `rayQueryIsLSSHitNV` returned false for a hit on LSS geometry, causing the raygen to count it as a miss.

**Possible implementation causes:** The `gl_HitIsSphereNV`, `gl_HitIsLSSNV`, `rayQueryIsSphereHitNV`, `rayQueryIsLSSHitNV`, `hitObjectIsSphereHitNV`, or `hitObjectIsLSSHitNV` built-in returned a wrong value for the hit geometry type. The driver did not correctly populate the hit kind metadata during traversal. On the `traceRayEXT` path this cause is masked because the closest-hit shader always sets `hitValue = 1` regardless of the `cond` check, so a built-in bug only surfaces on the ray-query or hit-object paths.

## Case Pruning

### Requirement-based pruning

- All cases require `VK_KHR_ray_tracing_pipeline`, `VK_KHR_acceleration_structure`, and `VK_NV_ray_tracing_linear_swept_spheres` device features. The `checkSupport` method throws `NotSupportedError` if `rayTracingPipeline` is false and `TestError` if `linearSweptSpheres` is false.
- The custom device requires `VK_KHR_buffer_device_address`, `VK_EXT_descriptor_indexing`, `VK_KHR_spirv_1_4`, and `VK_KHR_shader_float_controls` extensions in addition to the ray tracing and LSS extensions.
- The `no_endcaps` branch for `spheres` is pruned at registration time because standalone sphere geometry is always full spheres; the concept of endcaps does not apply.
- The `indexing_mode_list` and `indexing_mode_successive` test types are pruned for `spheres` because those indexing modes are LSS-specific.
- The `indices` test type is pruned for `lss` because LSS uses indexing modes rather than a plain index buffer.
- The `float2` and `half2` vertex formats are pruned for `lss` with `no_endcaps` because 2D vertex positions are not supported for that configuration.

### Design-based pruning

- The `skipBuiltinPrimitives` flag in `TestParams` is always false in the registered matrix. The `SpheresTestInstance::setupRayTracingPipeline` code path that sets `VK_PIPELINE_CREATE_2_RAY_TRACING_SKIP_BUILT_IN_PRIMITIVES_BIT_KHR` is never exercised by any registered case. This flag exists in the source for potential future use but does not affect the current test matrix.
- The test matrix does not vary the pipeline skip flags independently. The `ALLOW_SPHERES_AND_LINEAR_SWEPT_SPHERES_BIT_NV` flag is always set, and `SKIP_BUILT_IN_PRIMITIVES_BIT_KHR` is never set in the registered cases.
- The `result` storage buffer is allocated and cleared but never traced against in the inspected flow. Only the `reference` buffer is bound to the descriptor set and traced. The `result` buffer appears to be a leftover from a two-pass design that was simplified to a single-pass design.

## Key Takeaways

- The `linear_swept_spheres` family verifies that `VK_NV_ray_tracing_linear_swept_spheres` correctly builds, traverses, and reports hits for two new geometry types: standalone spheres and linear swept spheres.
- The geometry type (`spheres` vs `lss`) is the primary behavioral axis. It changes the BLAS geometry type, the valid test-type subset, the hit-classification built-in, and the expected hit-count formula.
- The expected hit count is hardcoded per valid combination of geometry type, test type, and endcap configuration. The host checks the red channel of every pixel in the result buffer against this count.
- The hit-classification built-ins (`gl_HitIsSphereNV`, `gl_HitIsLSSNV`, and their ray-query and hit-object equivalents) are only load-bearing when `use_ray_query` or `use_hit_object` is active. On the default `traceRayEXT` path, the closest-hit shader always sets the payload to 1 on hit.
- The test exercises the BLAS compact copy path for the new geometry types when `doBlasCopy` is true.
- See `## Failure Meaning` for the distinction between sphere geometry building/traversal failures, LSS geometry building/traversal failures, and hit-classification built-in failures.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `TestParams` struct | [vktRayTracingLinearSweptSpheresTests.cpp#L174-L185](../../../modules/vulkan/ray_tracing/vktRayTracingLinearSweptSpheresTests.cpp#L174-L185) | Per-case parameters: geometry type, test type, BLAS copy, endcaps, ray query, hit object, vertex format, radius format. |
| `DeviceHelper` custom device creation | [vktRayTracingLinearSweptSpheresTests.cpp#L101-L172](../../../modules/vulkan/ray_tracing/vktRayTracingLinearSweptSpheresTests.cpp#L101-L172) | Creates a custom device with required extensions and features, without `VK_KHR_pipeline_library`. |
| `iterate` validation | [vktRayTracingLinearSweptSpheresTests.cpp#L249-L454](../../../modules/vulkan/ray_tracing/vktRayTracingLinearSweptSpheresTests.cpp#L249-L454) | Host-side result checking: expected hit counts for each geometry type, test type, and endcap combination. |
| `SpheresTestInstance::setupRayTracingPipeline` | [vktRayTracingLinearSweptSpheresTests.cpp#L474-L504](../../../modules/vulkan/ray_tracing/vktRayTracingLinearSweptSpheresTests.cpp#L474-L504) | Builds the ray tracing pipeline with `ALLOW_SPHERES_AND_LINEAR_SWEPT_SPHERES_BIT_NV` and optional `SKIP_BUILT_IN_PRIMITIVES_BIT_KHR`. |
| `SpheresTestInstance::setupAccelerationStructures` | [vktRayTracingLinearSweptSpheresTests.cpp#L506-L568](../../../modules/vulkan/ray_tracing/vktRayTracingLinearSweptSpheresTests.cpp#L506-L568) | Builds sphere BLAS with 16 vertices, radii, and optional index buffer. |
| `LSSpheresTestInstance::setupAccelerationStructures` | [vktRayTracingLinearSweptSpheresTests.cpp#L614-L717](../../../modules/vulkan/ray_tracing/vktRayTracingLinearSweptSpheresTests.cpp#L614-L717) | Builds LSS BLAS with vertex, radius, index data, indexing mode, and endcap configuration. |
| `checkSupport` | [vktRayTracingLinearSweptSpheresTests.cpp#L747-L768](../../../modules/vulkan/ray_tracing/vktRayTracingLinearSweptSpheresTests.cpp#L747-L768) | Feature checks for acceleration structure, ray tracing pipeline, and LSS extension. |
| `initPrograms` raygen generation | [vktRayTracingLinearSweptSpheresTests.cpp#L770-L921](../../../modules/vulkan/ray_tracing/vktRayTracingLinearSweptSpheresTests.cpp#L770-L921) | Generates the raygen shader with branches for geometry type, endcaps, ray query, and hit object. |
| `initPrograms` closest-hit and miss | [vktRayTracingLinearSweptSpheresTests.cpp#L923-L955](../../../modules/vulkan/ray_tracing/vktRayTracingLinearSweptSpheresTests.cpp#L923-L955) | Generates the closest-hit and miss shaders. |
| `createLinearSweptSpheresTests` registration | [vktRayTracingLinearSweptSpheresTests.cpp#L960-L1149](../../../modules/vulkan/ray_tracing/vktRayTracingLinearSweptSpheresTests.cpp#L960-L1149) | Registers the test hierarchy with pruning rules for invalid combinations. |
| `addSphereGeometry` helper | [vkRayTracingUtil.cpp#L905-L939](../../../framework/vulkan/vkRayTracingUtil.cpp#L905-L939) | Framework helper that creates sphere or LSS geometry with the specified parameters. |
