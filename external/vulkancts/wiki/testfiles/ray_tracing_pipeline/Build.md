## Overview

**Core question:** Do acceleration structures built on the GPU, on the CPU single-threaded, or on the CPU through `VK_KHR_deferred_host_operations` with a varying number of host worker threads all produce the same correct ray tracing hit/miss pattern?

- [vktRayTracingBuildTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp) implements the single test family `build` under the `ray_tracing_pipeline` test category.
- All leaves share one scene, one ray tracing pipeline, and one rgen/any-hit/miss/intersection shader set. What varies is the acceleration structure build path: device-side build (`gpu`), host-side single-threaded build (`cpu`), or host-side build deferred across N host worker threads (`cpuht_1` through `cpuht_max`).
- Each leaf builds a bottom-level/top-level acceleration structure pair on the selected path, traces one ray per pixel straight down the -z axis, and compares the resulting per-pixel hit/miss values against an expected pattern derived from geometry placement.
- The page explains the build-path axis, the AS-level scaling matrix, the AABB expansion tolerance in the result check, and what a failure of each build path points to.

## Background Knowledge

- **Acceleration structure build types.** `VK_KHR_acceleration_structure` defines `VK_ACCELERATION_STRUCTURE_BUILD_TYPE_DEVICE_KHR` (build recorded and executed on the device via command buffer) and `VK_ACCELERATION_STRUCTURE_BUILD_TYPE_HOST_KHR` (build performed by the host). The build type selects where the build work runs, not the resulting traversal semantics.
- **Deferred host operations.** `VK_KHR_deferred_host_operations` lets a host-side AS build be split across multiple host threads. The implementation partitions the build work and joins the worker threads. The `cpuht_N` leaves request N worker threads; `cpuht_max` requests `UINT32_MAX`, which the implementation maps to its own preferred thread count. A non-zero thread count is what turns a plain host build into a deferred host build.
- **Acceleration structure levels.** A bottom-level acceleration structure (BLAS) holds geometry (triangles or AABBs). A top-level acceleration structure (TLAS) holds instances that reference BLAS. The `level_*` intermediate nodes scale the count at exactly one of those three levels while holding the others small.
- **AABB expansion.** The Vulkan spec permits implementations to expand AABB geometries in an acceleration structure to mitigate precision issues, which can produce false-positive intersection reports. The test's result check tolerates this for AABB and mixed geometry types.

## Registration Hierarchy

```text
ray_tracing_pipeline.build
├── cpu
├── cpuht_1
├── cpuht_2
├── cpuht_3
├── cpuht_4
├── cpuht_8
├── cpuht_max
└── gpu
```

The eight direct children are registered by [createBuildTests](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L753-L798). Each child corresponds to one `(threadCount, deviceBuild)` pair: `gpu` is the only device-build child (`threadCount == 0, deviceBuild == true`); `cpu` is the host single-threaded child (`threadCount == 0, deviceBuild == false`); the `cpuht_*` children are host deferred-operation children with the named worker-thread count.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| AS build path | `gpu`, `cpu`, `cpuht_1`, `cpuht_2`, `cpuht_3`, `cpuht_4`, `cpuht_8`, `cpuht_max` | Selects the acceleration structure build type and, for host builds, the deferred-host worker-thread count. This is the primary behavioral axis. | [createBuildTests](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L753-L798) |
| AS scaling level | `level_primitives`, `level_geometries`, `level_instances` | Selects which AS level receives the large count: primitives per geometry, geometries per BLAS, or instances per TLAS. The other two levels stay at the small factor. | [buildTest tests array](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L643-L644) |
| Geometry type | `triangles`, `aabbs`, `mixed` | Selects BLAS geometry: triangle geometry only, AABB geometry only, or alternating triangle/AABB per instance. Mixed requires at least two instances so both types appear. | [TestType enum](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L61-L66) |
| Size | `4`, `16`, `64`, `256`, `1024` | Base image and grid dimension squared. Drives the largest-group count as `size*size/factor/factor`. Device builds skip sizes above 256. | [buildTest sizes array](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L644) |
| Factor | `1`, `4` | Inverse scaling: the large level gets `size*size/factor/factor`, the other two levels get `factor`. | [buildTest factors array](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L645) |
| SPIR-V target | `spirv1.4` | All generated shaders use `vk::SPIRV_VERSION_1_4`. | [ShaderBuildOptions](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L213) |

The test case leaf name encodes the geometry type and the three group counts as `triangles_<instances>_<geometries>_<squares>` (and likewise for `aabbs_`, `mixed_`), so the leaf name directly records the scaling configuration.

## Behavior Parameters

The primary behavioral axis is the acceleration structure build path. Each value is a direct child of `ray_tracing_pipeline.build` and selects a different `VK_ACCELERATION_STRUCTURE_BUILD_TYPE_KHR` and worker-thread configuration. The scene, shaders, and result check are identical across all values.

### gpu - device-side acceleration structure build

Builds both BLAS and TLAS with `VK_ACCELERATION_STRUCTURE_BUILD_TYPE_DEVICE_KHR`. The build is recorded into the command buffer via `cmdBuildAccelerationStructuresKHR` and executed on the device before the trace. This path never uses deferred host operations and requires no `VK_KHR_deferred_host_operations`. It is the baseline device path: if it fails, the device-side AS build or the shared trace pipeline is suspect. Device builds skip sizes above 256, so the `gpu` matrix is smaller than the `cpu`/`cpuht_*` matrices.

### cpu - host single-threaded acceleration structure build

Builds both BLAS and TLAS with `VK_ACCELERATION_STRUCTURE_BUILD_TYPE_HOST_KHR` and `workerThreadsCount == 0`, so deferred operation is disabled. The build runs entirely on the calling host thread. This path requires `accelerationStructureHostCommands` support. It is the baseline host path against which the deferred-threaded paths are compared.

### cpuht_1 through cpuht_max - host deferred-operation builds with N worker threads

Builds both BLAS and TLAS with `VK_ACCELERATION_STRUCTURE_BUILD_TYPE_HOST_KHR` and `deferredOperation == true`, requesting the named worker-thread count. `cpuht_1` through `cpuht_8` request 1, 2, 3, 4, and 8 threads respectively; `cpuht_max` requests `UINT32_MAX`, which the implementation resolves to its preferred thread count. This path requires both `VK_KHR_deferred_host_operations` and `accelerationStructureHostCommands`. It exercises whether the implementation correctly partitions the host build across worker threads and joins them before the trace. The AS data and expected results are identical to `cpu`; only the threading of the build differs.

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.ray_tracing_pipeline.build.gpu.level_geometries.triangles_1_16_1
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `gpu` | Builds the BLAS and TLAS on the device before the shared ray tracing shader probe runs. |
| `level_geometries` | Places the large count at the geometries-per-BLAS level. |
| `triangles_1_16_1` | Uses a `4 x 4` launch, one triangle BLAS instance, 16 geometries, and one primitive per geometry. |

#### Purpose

The shaders turn traversal of the newly built acceleration structures into a 16-pixel hit/miss image. This makes the device-built structure observable: the any-hit stage writes `1` for a hit, while the miss stage writes `2`.

#### Structural Design

| Stage | Role in the probe | Observable effect |
|-------|-------------------|-------------------|
| Ray generation (`rgen`) | Launches one downward ray from the center of each image cell into the TLAS. | Selects either the hit or miss path for every output pixel. |
| Any-hit (`ahit`) | Runs for an accepted triangle or procedural hit. | Stores `1` in the `r32ui` result image. |
| Intersection (`sect`) | Supplies an intersection at `t = 1.0` for procedural AABB geometry. | Makes AABB variants reach the same any-hit result path; it is generated but not invoked by this triangle case. |
| Miss (`miss`) | Runs when traversal finds no accepted intersection. | Stores `2` in the result image. |

#### Shader Code

##### Ray Generation Shader

```glsl
#version 460 core
#extension GL_EXT_ray_tracing : require
/// Carries traversal payload state at location 0; the hit/miss shaders do not consume its value.
layout(location = 0) rayPayloadEXT vec3 hitValue;
/// Descriptor set 0, binding 1 is the TLAS traversed by every launch.
layout(set = 0, binding = 1) uniform accelerationStructureEXT topLevelAS;

void main()
{
  uint  rayFlags = 0;
  uint  cullMask = 0xFF;
  float tmin     = 0.0;
  float tmax     = 9.0;
  /// Map this launch to the center of its normalized image cell on z = 0.
  vec3  origin   = vec3((float(gl_LaunchIDEXT.x) + 0.5f) / float(gl_LaunchSizeEXT.x), (float(gl_LaunchIDEXT.y) + 0.5f) / float(gl_LaunchSizeEXT.y), 0.0);
  vec3  direct   = vec3(0.0, 0.0, -1.0);
  /// SBT offsets select hit-group 0 for triangles; TLAS instance offsets add 1 for AABBs.
  traceRayEXT(topLevelAS, rayFlags, cullMask, 0, 0, 0, origin, tmin, direct, tmax, 0);
}
```

##### Any-Hit Shader

```glsl
#version 460 core
#extension GL_EXT_ray_tracing : require
/// Incoming payload and hit attributes are declared for the ray-tracing interface but are not read.
layout(location = 0) rayPayloadInEXT vec3 hitValue;
hitAttributeEXT vec3 attribs;
/// Descriptor set 0, binding 0 is the single-component unsigned result image.
layout(r32ui, set = 0, binding = 0) uniform uimage2D result;
void main()
{
  /// Mark the launch pixel as a hit; only the x component is stored by the r32ui image.
  uvec4 color = uvec4(1,0,0,1);
  imageStore(result, ivec2(gl_LaunchIDEXT.xy), color);
}
```

##### Intersection Shader

```glsl
#version 460 core
#extension GL_EXT_ray_tracing : require
/// Procedural AABB hits expose this attribute to the following hit stage; its value is unused here.
hitAttributeEXT vec3 hitAttribute;
void main()
{
  /// Report a candidate procedural intersection one unit along the ray.
  reportIntersectionEXT(1.0f, 0);
}
```

##### Miss Shader

```glsl
#version 460 core
#extension GL_EXT_ray_tracing : require
/// The payload declaration matches location 0 used by the ray-generation stage but is not read.
layout(location = 0) rayPayloadInEXT vec3 unusedPayload;
/// Descriptor set 0, binding 0 is shared with the any-hit stage.
layout(r32ui, set = 0, binding = 0) uniform uimage2D result;
void main()
{
  /// Mark the launch pixel as a miss.
  uvec4 color = uvec4(2,0,0,1);
  imageStore(result, ivec2(gl_LaunchIDEXT.xy), color);
}
```

#### Additional Info

- The any-hit and miss shaders stay fixed across every leaf. Together they encode traversal as the exact values consumed by `validateBuffer`: `1` for hit and `2` for miss.
- The intersection shader also stays fixed. It matters to the page's `aabbs` and `mixed` leaves, whose second hit-group record combines this stage with the same any-hit shader; the selected triangle leaf uses the first hit-group record and does not invoke it.
- `updateRayTracingGLSL` is an identity wrapper, so the displayed stage sources preserve the strings assembled by `RayTracingTestCase::initPrograms`. All four are compiled with the explicit SPIR-V 1.4 target.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|-----------------------------------------|----------|
| Build path (`gpu`, `cpu`, `cpuht_*`) | None. It changes where and how the acceleration structures are built, not the generated shader source. | [build-path registration and `CaseDef`](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L753-L798) |
| Scaling level, size, and factor | None. These dimensions change launch dimensions and BLAS/TLAS contents; all leaves call the same shader builder. | [`buildTest`](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L641-L751) |
| Geometry type (`triangles`, `aabbs`, `mixed`) | None in generated source. Runtime TLAS SBT record offsets select the triangle hit group or the AABB hit group that adds the intersection stage. | [TLAS instance setup](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L268-L290) and [pipeline/SBT setup](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L437-L464) |

#### SPIR-V

##### Ray Generation Shader

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
; Bound: 62
; Schema: 0
               OpCapability RayTracingKHR
               OpExtension "SPV_KHR_ray_tracing"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint RayGenerationKHR %main "main" %gl_LaunchIDEXT %gl_LaunchSizeEXT %topLevelAS %hitValue
               OpSource GLSL 460
               OpSourceExtension "GL_EXT_ray_tracing"
               OpName %main "main"
               OpName %rayFlags "rayFlags"
               OpName %cullMask "cullMask"
               OpName %tmin "tmin"
               OpName %tmax "tmax"
               OpName %origin "origin"
               OpName %gl_LaunchIDEXT "gl_LaunchIDEXT"
               OpName %gl_LaunchSizeEXT "gl_LaunchSizeEXT"
               OpName %direct "direct"
               OpName %topLevelAS "topLevelAS"
               OpName %hitValue "hitValue"
               OpDecorate %gl_LaunchIDEXT BuiltIn LaunchIdKHR
               OpDecorate %gl_LaunchSizeEXT BuiltIn LaunchSizeKHR
               OpDecorate %topLevelAS Binding 1
               OpDecorate %topLevelAS DescriptorSet 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
     %uint_0 = OpConstant %uint 0
   %uint_255 = OpConstant %uint 255
      %float = OpTypeFloat 32
%_ptr_Function_float = OpTypePointer Function %float
    %float_0 = OpConstant %float 0
    %float_9 = OpConstant %float 9
    %v3float = OpTypeVector %float 3
%_ptr_Function_v3float = OpTypePointer Function %v3float
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_LaunchIDEXT = OpVariable %_ptr_Input_v3uint Input
%_ptr_Input_uint = OpTypePointer Input %uint
  %float_0_5 = OpConstant %float 0.5
%gl_LaunchSizeEXT = OpVariable %_ptr_Input_v3uint Input
     %uint_1 = OpConstant %uint 1
   %float_n1 = OpConstant %float -1
         %47 = OpConstantComposite %v3float %float_0 %float_0 %float_n1
         %48 = OpTypeAccelerationStructureKHR
%_ptr_UniformConstant_48 = OpTypePointer UniformConstant %48
 %topLevelAS = OpVariable %_ptr_UniformConstant_48 UniformConstant
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_RayPayloadKHR_v3float = OpTypePointer RayPayloadKHR %v3float
   %hitValue = OpVariable %_ptr_RayPayloadKHR_v3float RayPayloadKHR
       %main = OpFunction %void None %3
          %5 = OpLabel
   %rayFlags = OpVariable %_ptr_Function_uint Function
   %cullMask = OpVariable %_ptr_Function_uint Function
       %tmin = OpVariable %_ptr_Function_float Function
       %tmax = OpVariable %_ptr_Function_float Function
     %origin = OpVariable %_ptr_Function_v3float Function
     %direct = OpVariable %_ptr_Function_v3float Function
               OpStore %rayFlags %uint_0
               OpStore %cullMask %uint_255
               OpStore %tmin %float_0
               OpStore %tmax %float_9
         %25 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_0
         %26 = OpLoad %uint %25
         %27 = OpConvertUToF %float %26
         %29 = OpFAdd %float %27 %float_0_5
         %31 = OpAccessChain %_ptr_Input_uint %gl_LaunchSizeEXT %uint_0
         %32 = OpLoad %uint %31
         %33 = OpConvertUToF %float %32
         %34 = OpFDiv %float %29 %33
         %36 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_1
         %37 = OpLoad %uint %36
         %38 = OpConvertUToF %float %37
         %39 = OpFAdd %float %38 %float_0_5
         %40 = OpAccessChain %_ptr_Input_uint %gl_LaunchSizeEXT %uint_1
         %41 = OpLoad %uint %40
         %42 = OpConvertUToF %float %41
         %43 = OpFDiv %float %39 %42
         %44 = OpCompositeConstruct %v3float %34 %43 %float_0
               OpStore %origin %44
               OpStore %direct %47
         %51 = OpLoad %48 %topLevelAS
         %52 = OpLoad %uint %rayFlags
         %53 = OpLoad %uint %cullMask
         %54 = OpLoad %v3float %origin
         %55 = OpLoad %float %tmin
         %56 = OpLoad %v3float %direct
         %57 = OpLoad %float %tmax
               OpTraceRayKHR %51 %52 %53 %uint_0 %uint_0 %uint_0 %54 %55 %56 %57 %hitValue
               OpReturn
               OpFunctionEnd
```

</details>

##### Any-Hit Shader

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `rahit`
- Target SPIRV version: `spirv1.4`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.4
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 33
; Schema: 0
               OpCapability RayTracingKHR
               OpExtension "SPV_KHR_ray_tracing"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint AnyHitKHR %main "main" %result %gl_LaunchIDEXT %hitValue %attribs
               OpSource GLSL 460
               OpSourceExtension "GL_EXT_ray_tracing"
               OpName %main "main"
               OpName %color "color"
               OpName %result "result"
               OpName %gl_LaunchIDEXT "gl_LaunchIDEXT"
               OpName %hitValue "hitValue"
               OpName %attribs "attribs"
               OpDecorate %result Binding 0
               OpDecorate %result DescriptorSet 0
               OpDecorate %gl_LaunchIDEXT BuiltIn LaunchIdKHR
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
     %v4uint = OpTypeVector %uint 4
%_ptr_Function_v4uint = OpTypePointer Function %v4uint
     %uint_1 = OpConstant %uint 1
     %uint_0 = OpConstant %uint 0
         %12 = OpConstantComposite %v4uint %uint_1 %uint_0 %uint_0 %uint_1
         %13 = OpTypeImage %uint 2D 0 0 0 2 R32ui
%_ptr_UniformConstant_13 = OpTypePointer UniformConstant %13
     %result = OpVariable %_ptr_UniformConstant_13 UniformConstant
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_LaunchIDEXT = OpVariable %_ptr_Input_v3uint Input
     %v2uint = OpTypeVector %uint 2
        %int = OpTypeInt 32 1
      %v2int = OpTypeVector %int 2
      %float = OpTypeFloat 32
    %v3float = OpTypeVector %float 3
%_ptr_IncomingRayPayloadKHR_v3float = OpTypePointer IncomingRayPayloadKHR %v3float
   %hitValue = OpVariable %_ptr_IncomingRayPayloadKHR_v3float IncomingRayPayloadKHR
%_ptr_HitAttributeKHR_v3float = OpTypePointer HitAttributeKHR %v3float
    %attribs = OpVariable %_ptr_HitAttributeKHR_v3float HitAttributeKHR
       %main = OpFunction %void None %3
          %5 = OpLabel
      %color = OpVariable %_ptr_Function_v4uint Function
               OpStore %color %12
         %16 = OpLoad %13 %result
         %21 = OpLoad %v3uint %gl_LaunchIDEXT
         %22 = OpVectorShuffle %v2uint %21 %21 0 1
         %25 = OpBitcast %v2int %22
         %26 = OpLoad %v4uint %color
               OpImageWrite %16 %25 %26 ZeroExtend
               OpReturn
               OpFunctionEnd
```

</details>

##### Intersection Shader

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `rint`
- Target SPIRV version: `spirv1.4`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.4
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 15
; Schema: 0
               OpCapability RayTracingKHR
               OpExtension "SPV_KHR_ray_tracing"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint IntersectionKHR %main "main" %hitAttribute
               OpSource GLSL 460
               OpSourceExtension "GL_EXT_ray_tracing"
               OpName %main "main"
               OpName %hitAttribute "hitAttribute"
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %float_1 = OpConstant %float 1
       %uint = OpTypeInt 32 0
     %uint_0 = OpConstant %uint 0
       %bool = OpTypeBool
    %v3float = OpTypeVector %float 3
%_ptr_HitAttributeKHR_v3float = OpTypePointer HitAttributeKHR %v3float
%hitAttribute = OpVariable %_ptr_HitAttributeKHR_v3float HitAttributeKHR
       %main = OpFunction %void None %3
          %5 = OpLabel
         %11 = OpReportIntersectionKHR %bool %float_1 %uint_0
               OpReturn
               OpFunctionEnd
```

</details>

##### Miss Shader

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `rmiss`
- Target SPIRV version: `spirv1.4`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.4
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 32
; Schema: 0
               OpCapability RayTracingKHR
               OpExtension "SPV_KHR_ray_tracing"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint MissKHR %main "main" %result %gl_LaunchIDEXT %unusedPayload
               OpSource GLSL 460
               OpSourceExtension "GL_EXT_ray_tracing"
               OpName %main "main"
               OpName %color "color"
               OpName %result "result"
               OpName %gl_LaunchIDEXT "gl_LaunchIDEXT"
               OpName %unusedPayload "unusedPayload"
               OpDecorate %result Binding 0
               OpDecorate %result DescriptorSet 0
               OpDecorate %gl_LaunchIDEXT BuiltIn LaunchIdKHR
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
     %v4uint = OpTypeVector %uint 4
%_ptr_Function_v4uint = OpTypePointer Function %v4uint
     %uint_2 = OpConstant %uint 2
     %uint_0 = OpConstant %uint 0
     %uint_1 = OpConstant %uint 1
         %13 = OpConstantComposite %v4uint %uint_2 %uint_0 %uint_0 %uint_1
         %14 = OpTypeImage %uint 2D 0 0 0 2 R32ui
%_ptr_UniformConstant_14 = OpTypePointer UniformConstant %14
     %result = OpVariable %_ptr_UniformConstant_14 UniformConstant
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_LaunchIDEXT = OpVariable %_ptr_Input_v3uint Input
     %v2uint = OpTypeVector %uint 2
        %int = OpTypeInt 32 1
      %v2int = OpTypeVector %int 2
      %float = OpTypeFloat 32
    %v3float = OpTypeVector %float 3
%_ptr_IncomingRayPayloadKHR_v3float = OpTypePointer IncomingRayPayloadKHR %v3float
%unusedPayload = OpVariable %_ptr_IncomingRayPayloadKHR_v3float IncomingRayPayloadKHR
       %main = OpFunction %void None %3
          %5 = OpLabel
      %color = OpVariable %_ptr_Function_v4uint Function
               OpStore %color %13
         %17 = OpLoad %14 %result
         %22 = OpLoad %v3uint %gl_LaunchIDEXT
         %23 = OpVectorShuffle %v2uint %22 %22 0 1
         %26 = OpBitcast %v2int %23
         %27 = OpLoad %v4uint %color
               OpImageWrite %17 %26 %27 ZeroExtend
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

### Scene construction

- The host builds a set of BLAS, one per instance. Each BLAS holds `geometriesGroupCount` geometries, and each geometry holds `squaresGroupCount` primitives. Each primitive covers one pixel cell of the `width x height` image. A deterministic walk (`startPos` advanced by `(n+13) % (width*height)`) places each primitive at a cell whose linear index `n` determines its z-face sign [initBottomAccelerationStructure](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L305-L351).
- Triangle primitives use three vertices per cell; AABB primitives use two opposite corners [geometryData fill](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L316-L343). The `mixed` type alternates triangle and AABB per instance [triangles flag](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L281-L282).
- A TLAS instances all BLAS with identity transforms. The instance SBT record offset is 0 for triangle instances and 1 for AABB instances, selecting the hit group with the intersection shader for AABBs [initTopAccelerationStructure](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L268-L290).

### Build path execution

- The `buildTest` registration passes the case's `deviceBuild` and `workerThreadsCount` into the `CaseDef`, and the instance's `runTest` uses those to set the build type and deferred-operation mode on every BLAS and the TLAS [runTest build setup](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L408-L528).
- BLAS are built through a `BottomLevelAccelerationStructurePool` that batches creation and build to stay under the device's `maxMemoryAllocationCount`. For host builds, the watchdog interval time limit is disabled around the BLAS batch build to avoid timeouts on low-clocked CPUs, then re-enabled [watchdog disable/enable](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L504-L516).
- The TLAS is created and built inside the command buffer for device builds, or on the host for host builds [createTopAccelerationStructure](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L292-L303).

### Trace and result copyback

- The result image is a 2D `r32ui` storage image sized to `width x height`. It is cleared to `(5,5,5,255)` and transitioned to `GENERAL` before the trace [image setup](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L466-L496).
- `cmdTraceRays` launches `width x height x 1` rays. Each raygen invocation traces one ray down -z into the TLAS; the any-hit or miss shader writes the per-pixel result into the image [trace dispatch](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L549-L550).
- After the trace, a `SHADER_WRITE` -> `TRANSFER_READ` barrier, `cmdCopyImageToBuffer`, and a `TRANSFER_WRITE` -> `HOST_READ` barrier move the image into a host-visible buffer [copyback](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L552-L565).

### Per-pixel result check

- The host scans every pixel. The expected value is `1` (any-hit) for cells whose linear index `n` is not divisible by 7, and `2` (miss) for cells where `n % 7 == 0` [validateBuffer](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L589-L627). The `n % 7 == 0` cells have z-face sign `+1`; the deterministic placement arranges them to miss the downward ray, while all other cells present a z `-1` face that the ray hits.
- For `triangles` geometry, a mismatched pixel always counts as a failure. For `aabbs` and `mixed` geometry, a mismatched pixel is only a failure if the observed value is not the any-hit value `1`; this tolerates implementation AABB expansion that reports a hit where the test expected a miss [AABB tolerance](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L606-L616).
- Pass condition: `failures == 0` [iterate](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L629-L637).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `gpu` | Device-side AS build (BLAS/TLAS) did not produce a structure that traverses to the expected hit/miss pattern, or the device build path's shared trace pipeline or SBT is broken. |
| `cpu` | Host single-threaded AS build did not produce a correct structure, or `accelerationStructureHostCommands` host build path has a correctness bug independent of threading. |
| `cpuht_1` through `cpuht_8` | Host deferred-operation build with the named worker-thread count did not produce a correct structure, pointing at deferred-operation work partitioning or thread-join synchronization for that thread count. |
| `cpuht_max` | Host deferred-operation build with the implementation's preferred (max) thread count did not produce a correct structure, pointing at deferred-operation scaling to many threads. |

All leaves share the scene construction, the trace pipeline, and the per-pixel result check, so a failure common to all build-path values points at shared infrastructure (geometry data, TLAS instance setup, SBT, image copyback, expected-value rule) rather than a build-path-specific issue.

### Cause Analysis

#### Device-side build correctness failure

**Possible failure symptoms:** A `gpu` leaf failure where the corresponding `cpu` leaf with the same scaling and geometry type passes. The result image has mismatched pixels: cells that should be `1` (hit) are `2` (miss) or the clear value, or vice versa, and the failure count is nonzero.

**Possible implementation causes:** The `gpu` path records the BLAS and TLAS builds into the command buffer and the device executes them. The traversal result depends on the device-built structure matching the host-built one. A grounded investigation should check whether the device build completed and was made visible to the trace (the build and trace are in the same command buffer), whether the BLAS geometry data uploaded to device buffers matches the host-side geometry used to compute expected values, and whether the TLAS instance SBT record offsets were set correctly for the device build. If `gpu` and `cpu` both fail at the same scaling, the cause is shared infrastructure, not the device build path. If only `gpu` fails and the host path passes, source-level investigation is needed.

#### Host single-threaded build correctness failure

**Possible failure symptoms:** A `cpu` leaf failure where the corresponding `gpu` leaf passes, or where `cpu` and all `cpuht_*` leaves fail together. Mismatched pixels in the result image with a nonzero failure count.

**Possible implementation causes:** The `cpu` path builds BLAS and TLAS on the host with `VK_ACCELERATION_STRUCTURE_BUILD_TYPE_HOST_KHR` and deferred operation disabled. It requires the `accelerationStructureHostCommands` feature. A grounded investigation should check whether the host build respected the same geometry data and instance configuration as the device path, and whether the host-built structure was made available to the device trace (the host-built TLAS handle is bound via the descriptor set before the trace). The spec ties host builds to `accelerationStructureHostCommands`; if that feature is reported but the host build is broken, the cause is in the host build implementation. If `cpu` passes but a `cpuht_*` leaf fails, the cause is deferred-operation-specific.

#### Deferred-host-operation threading failure

**Possible failure symptoms:** A `cpuht_N` or `cpuht_max` leaf failure where the `cpu` leaf with the same scaling and geometry type passes. Mismatched pixels with a nonzero failure count. The failure may appear only for specific thread counts.

**Possible implementation causes:** The `cpuht_*` paths enable deferred operation and request N worker threads. The implementation must partition the host build across the worker threads and join them so the completed structure is visible before the trace. A grounded investigation should check whether the deferred-operation join completed for the failing thread count, whether the partitioning produced a structure equivalent to the single-threaded build, and whether any per-thread scratch or allocation state leaked between threads. The spec states deferred host operations may be concurrent and the implementation must complete them before returning. If only some thread counts fail, the cause is thread-count-specific partitioning or join logic, and source-level investigation of the deferred-operation join path is needed.

#### Shared infrastructure failure

**Possible failure symptoms:** All build-path values for a given scaling and geometry type fail with the same pixel pattern, regardless of whether the build ran on the device, the host, or the host with threads.

**Possible implementation causes:** The scene construction, trace pipeline, SBT, result image clear and copyback, and the expected-value rule are identical across all build paths. A failure common to all paths points at this shared setup. A grounded investigation should check whether the deterministic primitive placement walk produced the expected z-face signs (the `n % 7 == 0` miss cells), whether the TLAS instance SBT record offsets match the hit-group layout, whether the rgen ray direction and tmax actually reach the geometry, and whether the per-pixel expected-value rule in `validateBuffer` matches the geometry placement. For `mixed` geometry, check that the AABB-expansion tolerance is applied correctly. Source-level inspection of `initBottomAccelerationStructure` and `validateBuffer` is needed to confirm the placement and expected-value correspondence.

## Case Pruning

### Requirement-based pruning

- All leaves require `VK_KHR_acceleration_structure` and `VK_KHR_ray_tracing_pipeline`, with the `rayTracingPipeline` and `accelerationStructure` feature bits set. If `accelerationStructure` is not set, the test throws `TestError` [checkSupport](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L186-L205).
- Host builds (`cpu` and all `cpuht_*`) additionally require `VK_KHR_deferred_host_operations` and `accelerationStructureHostCommands`; otherwise the test throws `NotSupportedError` [host build feature gate](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L202-L208). The `gpu` path does not require these.
- At instance time, the test checks ray tracing property limits: `maxPrimitiveCount`, `maxGeometryCount`, and `maxInstanceCount` must each cover the case's group counts, and the estimated memory allocation count (plus a 120-allocation margin) must stay under `maxMemoryAllocationCount`. Any shortfall throws `NotSupportedError` [checkSupportInInstance](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L570-L587).

### Design-based pruning

- Device builds skip sizes above 256 (`if (deviceBuild && sizes[sizesNdx] > 256) continue`), so the `gpu` matrix omits the 1024 size. This keeps device build time and scratch within practical limits [device size skip](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L656-L657).
- Cases where any group count would be zero are skipped (`squaresGroupCount == 0 || geometriesGroupCount == 0 || instancesGroupCount == 0`) [zero-count skip](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L679-L680).
- `mixed` geometry requires at least two instances, two geometries, and two squares per geometry, so that both triangle and AABB types actually appear. This is enforced by a stricter skip condition for the mixed loop [mixed minimum skip](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L743-L744).
- `workerThreadsCount` and `deviceBuild` are mutually exclusive: the registration asserts `!(threadCount != 0 && deviceBuild)`, so only the `gpu` child uses the device build and only the `cpu`/`cpuht_*` children use host builds [mutual exclusion assert](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L764).

## Key Takeaways

- The `build` family isolates the acceleration structure build path as the behavioral axis: device build (`gpu`), host single-threaded build (`cpu`), and host deferred-operation build with 1, 2, 3, 4, 8, or max worker threads (`cpuht_*`). The scene, shaders, and result check are identical across all paths.
- The `level_*` intermediate nodes and the size/factor matrix scale the AS at one level at a time, exercising large primitive counts, large geometry counts, and large instance counts against the implementation's property limits.
- The result check compares a deterministic hit/miss pattern derived from geometry placement; for AABB and mixed geometry it tolerates implementation AABB expansion that produces an extra hit, but not a miss where a hit was expected.
- A failure isolated to one build path points at that path's build or synchronization correctness; a failure common to all paths points at shared scene, pipeline, or check infrastructure. See `## Failure Meaning` for the per-path cause analysis.
- The host deferred-operation paths specifically test work partitioning and thread join correctness across the supported worker-thread counts, including the implementation-chosen max count.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `TestType` enum | [vktRayTracingBuildTests.cpp#L61-L66](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L61-L66) | Defines triangles, aabbs, mixed geometry types |
| `CaseDef` struct | [vktRayTracingBuildTests.cpp#L68-L79](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L68-L79) | Per-case parameters including build path and worker-thread count |
| `checkSupport` | [vktRayTracingBuildTests.cpp#L186-L205](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L186-L205) | Feature gates for acceleration structure, ray tracing pipeline, deferred host operations |
| `initPrograms` (ahit/miss/sect/rgen) | [vktRayTracingBuildTests.cpp#L211-L261](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L211-L261) | The fixed probe shaders, including the shared rgen helper |
| `initBottomAccelerationStructure` | [vktRayTracingBuildTests.cpp#L305-L351](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L305-L351) | Deterministic primitive placement and z-face sign rule |
| `initTopAccelerationStructure` | [vktRayTracingBuildTests.cpp#L268-L290](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L268-L290) | TLAS instance setup and SBT record offset selection |
| `runTest` | [vktRayTracingBuildTests.cpp#L408-L568](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L408-L568) | Build path execution, trace dispatch, and result copyback |
| `checkSupportInInstance` | [vktRayTracingBuildTests.cpp#L570-L587](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L570-L587) | Runtime property-limit and allocation-count pruning |
| `validateBuffer` | [vktRayTracingBuildTests.cpp#L589-L627](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L589-L627) | Per-pixel expected-value rule and AABB-expansion tolerance |
| `iterate` | [vktRayTracingBuildTests.cpp#L629-L637](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L629-L637) | Pass/fail condition |
| `buildTest` | [vktRayTracingBuildTests.cpp#L641-L751](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L641-L751) | Scaling-level, geometry-type, size, and factor matrix generation |
| `createBuildTests` | [vktRayTracingBuildTests.cpp#L753-L798](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L753-L798) | Registration of the eight build-path direct children |
| shared rgen shader helper | [vkRayTracingUtil.cpp#L118-L138](../../../framework/vulkan/vkRayTracingUtil.cpp#L118-L138) | Common ray generation shader tracing one ray per launch ID down -z |
