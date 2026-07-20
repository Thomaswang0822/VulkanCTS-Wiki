## Overview

**Core question:** When an implementation declares `VK_EXT_ray_tracing_invocation_reorder` support and reports a non-`NONE` reorder hint, does `reorderThreadEXT` actually perturb shader invocation grouping, or is it a silent no-op?

- [vktRayTracingInvocationReorderActivityTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingInvocationReorderActivityTests.cpp) implements the single test family `rtir_activity` under the `ray_tracing_pipeline` test category.
- The family has one test case leaf, `activity`, registered with `use_shader_invocation_reorder = true` and a fixed 512x512 dispatch.
- The rgen shader traces rays through `hitObjectTraceRayEXT` into a 16-instance scene. The left half of the image skips `reorderThreadEXT`; the right half calls it. Both halves then execute the hit shader and write a per-pixel color derived from `gl_SubgroupInvocationID`.
- Reordering changes which subgroup invocations process which pixels, so the subgroup-derived color pattern differs between halves. The host compares the two halves: a mismatch proves reordering occurred.
- The page explains the reorder detection mechanism, the representative rgen shader, and what a failure means.

## Background Knowledge

- **`VK_EXT_ray_tracing_invocation_reorder`.** This extension lets a ray generation shader request that the implementation reorder shader invocations so that rays hitting similar geometry execute together, improving locality. The GLSL extension is `GL_EXT_shader_invocation_reorder`; the SPIR-V capability is `ShaderInvocationReorderEXT`.
- **Hit objects.** `GL_EXT_hit_object` (folded into the same SPIR-V capability) introduces the `hitObjectEXT` type and functions `hitObjectRecordEmptyEXT`, `hitObjectTraceRayEXT`, `hitObjectExecuteShaderEXT`. A hit object records the result of a ray trace and defers shader execution until `hitObjectExecuteShaderEXT` is called.
- **`reorderThreadEXT`.** Takes a hit object as a hint and asks the implementation to reorder the calling thread relative to other threads that recorded similar hits. The reorder is optional; the implementation may ignore it.
- **`gl_SubgroupInvocationID`.** The index of the current invocation within its subgroup. The test uses this to derive a per-pixel color. Without reordering, subgroup assignment follows a regular pattern tied to launch IDs. With reordering, the pattern changes, producing a different color distribution.
- **Reorder hint.** `VkPhysicalDeviceRayTracingInvocationReorderPropertiesEXT::rayTracingInvocationReorderReorderingHint` reports whether the implementation actually performs reordering. `VK_RAY_TRACING_INVOCATION_REORDER_MODE_NONE_EXT` means it does not.

## Registration Hierarchy

```text
ray_tracing_pipeline.rtir_activity
└── activity
```

The single direct child is registered by [createRTIRActivityTests](../../../modules/vulkan/ray_tracing/vktRayTracingInvocationReorderActivityTests.cpp#L634-L649). The leaf is created with `TestParams{use_shader_invocation_reorder = true, resX = 512, resY = 512}`.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test case leaf | `activity` | Single fixed case that exercises reorder activity. This is the only registered leaf. | [createRTIRActivityTests](../../../modules/vulkan/ray_tracing/vktRayTracingInvocationReorderActivityTests.cpp#L646) |
| Reorder mode | `use_shader_invocation_reorder = true` | The rgen shader uses the hit-object path with conditional `reorderThreadEXT`. The `false` path exists in shader generation code but is never registered. | [TestParams](../../../modules/vulkan/ray_tracing/vktRayTracingInvocationReorderActivityTests.cpp#L639-L644) |
| Resolution | `resX = 512`, `resY = 512` | Fixed 512x512 dispatch. Must be a multiple of 2, and each half must be a multiple of the subgroup size. | [TestParams](../../../modules/vulkan/ray_tracing/vktRayTracingInvocationReorderActivityTests.cpp#L643-L644) |
| SPIR-V target | `spirv1.4` | Generated shaders use `vk::SPIRV_VERSION_1_4`. | [ShaderBuildOptions](../../../modules/vulkan/ray_tracing/vktRayTracingInvocationReorderActivityTests.cpp#L145) |

## Behavior Parameters

The primary behavioral axis is the test case leaf. The family has one leaf, so the axis is trivial.

### activity — single reorder activity case

The test verifies that `reorderThreadEXT` produces observable reordering when the implementation claims to support it. The rgen shader traces primary rays through a 16-instance scene where consecutive pixels hit different instances and thus different closest-hit shaders. The left half of the image skips `reorderThreadEXT` and serves as the reference pattern. The right half calls `reorderThreadEXT` before `hitObjectExecuteShaderEXT`. Both halves write a color derived from `gl_SubgroupInvocationID` into the output buffer. If reordering occurred, the subgroup composition on the right half differs from the left, and the color patterns mismatch. The test passes when the halves differ. If the implementation reports `NONE` reorder hint or does not expose the feature, the test passes early without running the trace.

## Shader Analysis

The rgen shader is the tested behavior. The miss shader writes `vec3(0.0)` to the payload and is never reached because all geometry is opaque. The eight closest-hit shaders (`ch0` through `ch7`) each run a heavy floating-point loop with a distinct `uScale` constant to simulate different materials and create incoherent workload across pixels. Their shader text is identical except for the `uScale` value. No closest-hit walkthrough is needed because the rgen shader is where the reorder logic lives.

### Representative Shader Walkthrough 1: `rtir_activity.activity` rgen

**CTS case:** `dEQP-VK.ray_tracing_pipeline.rtir_activity.activity`

**Source:** reconstructed from [RTIRActivityCase::initPrograms](../../../modules/vulkan/ray_tracing/vktRayTracingInvocationReorderActivityTests.cpp#L129-L339), which assembles the rgen string from three fragments. The `use_shader_invocation_reorder = true` path concatenates `rgen_begin` + `rgen_TraceRTIR` + `rgen_end`. The `updateRayTracingGLSL` wrapper is an identity function, so the emitted source matches the string exactly.

**Stage:** Ray generation (`VK_SHADER_STAGE_RAYGEN_BIT_KHR`).

**Resources:**

- `topLevelAS` (binding 0, set 0): `accelerationStructureEXT`. Bound at runtime to a 16-instance TLAS. Each instance references the same BLAS (one opaque triangle quad) with a different transform and SBT record offset `2*j + i`, selecting one of eight closest-hit shaders.
- `outBuf` (binding 1, set 0): `std430` storage buffer of `uint values[1048576]`. The array length is `sizeof(uint32_t) * resX * resY = 1048576`, which is four times the pixel count. Only the first `512*512 = 262144` entries are written. Each entry packs an RGB color as `R << 16 | G << 8 | B`.
- `hitValue` (location 0): `rayPayloadEXT vec3`. Written by the closest-hit or miss shader, then ignored by rgen after `hitObjectExecuteShaderEXT` returns.
- `hObj`: `hitObjectEXT` variable in `Private` storage. Records the ray trace result and drives the reorder decision.

**Shader logic:**

The rgen shader computes a defocused primary ray per launch ID. It maps `gl_LaunchIDEXT.xy` to a normalized `[-1, 1]` coordinate, perturbs the ray origin using a disk-sampled lens offset (`apertureSize = 1.0`, `focusDistance = 1.15`), and normalizes the direction toward the focus point. The defocus makes consecutive pixels trace incoherent rays that hit different TLAS instances and thus different closest-hit shaders.

The reorder path is the core of the test:

1. `hitObjectRecordEmptyEXT(hObj)` initializes the hit object.
2. `hitObjectTraceRayEXT(hObj, ...)` traces the ray into the TLAS with `gl_RayFlagsOpaqueEXT`, `cullMask = 0xFF`, `sbtRecordOffset = 0`, and records the result in `hObj` without immediately invoking a hit or miss shader.
3. If `gl_LaunchIDEXT.x > gl_LaunchSizeEXT.x / 2` (right half of the image), `reorderThreadEXT(hObj)` asks the implementation to reorder the thread based on the recorded hit.
4. `hitObjectExecuteShaderEXT(hObj, 0)` invokes the shader (closest-hit or miss) associated with the recorded hit object, using payload location 0.

After the hit shader returns, the rgen shader writes a color to the output buffer. The color comes from a 192-element lookup table `col[192]` that holds 64 RGB triples with component values from `{0, 85, 170, 255}`. The index is `gl_SubgroupInvocationID * 3`, so each subgroup invocation maps to a fixed color. Without reordering, the subgroup assignment follows the implementation's default launch-ID-to-subgroup mapping, producing a regular color pattern. With reordering on the right half, threads with similar hits cluster together, changing the subgroup composition and the resulting color pattern.

The output write packs the color as `R << 16 | G << 8 | B` into `outBuf.values[gl_LaunchIDEXT.y * 512 + gl_LaunchIDEXT.x]`.

#### Reconstructed GLSL

```glsl
#version 460
#extension GL_EXT_ray_tracing : require
#extension GL_KHR_shader_subgroup_basic : require
#extension GL_EXT_shader_invocation_reorder : require

layout(binding = 0, set = 0) uniform accelerationStructureEXT topLevelAS;
layout(binding = 1, set = 0, std430) buffer OutputBuffer {
    uint values[1048576];
} outBuf;

layout(location = 0) rayPayloadEXT vec3 hitValue;

float rand(float seed) {
    uint n = floatBitsToUint(seed);
    n = (n ^ 61u) ^ (n >> 16);
    n *= 9u;
    n = n ^ (n >> 4);
    n *= 0x27d4eb2du;
    n = n ^ (n >> 15);
    return float(n) / float(0xFFFFFFFFu);
}

vec2 sampleDisk(float seed) {
    float theta = 2.0 * 3.141592653589793 * rand(seed);
    float r = sqrt(rand(seed + 1.0));
    return vec2(r * cos(theta), r * sin(theta));
}

void main()
{
    const vec2 pixelCenter = vec2(gl_LaunchIDEXT.xy) + vec2(0.5);
    const vec2 inUV = pixelCenter/vec2(gl_LaunchSizeEXT.xy);
    vec2 d = inUV * 2.0 - 1.0;

    vec3 origin = vec3(d, -1.0);
    vec3 direction = vec3(0.0, 0.0, 1.0);

    float apertureSize = 1.0;
    float focusDistance = 1.15;

    vec2 lensSample = sampleDisk(float(pixelCenter.x + pixelCenter.y * gl_LaunchSizeEXT.x)) * apertureSize;
    vec3 defocusedRayOrigin = origin + vec3(lensSample, 0.0);
    vec3 focusPoint = origin + focusDistance * direction;
    vec3 finalRayDirection = normalize(focusPoint - defocusedRayOrigin);

    float tmin = 0.001;
    float tmax = 10000.0;

    hitValue = vec3(0.0);
    uvec3 invocationRes = uvec3(0);

    hitObjectEXT hObj;
    hitObjectRecordEmptyEXT(hObj);

    hitObjectTraceRayEXT(hObj, topLevelAS, gl_RayFlagsOpaqueEXT, 0xFF, 0, 0, 0, defocusedRayOrigin, tmin, finalRayDirection, tmax, 0);

    if (gl_LaunchIDEXT.x > (gl_LaunchSizeEXT.x/2))
        reorderThreadEXT(hObj);

    hitObjectExecuteShaderEXT(hObj,0);

    uint col[192] = {0, 0, 0, 0, 0, 85,0, 0, 170,0, 0, 255,0, 85, 0,0, 85, 85,0, 85, 170,
0, 85, 255, 0, 170, 0,0, 170, 85,0, 170, 170,0, 170, 255,0, 255, 0,0, 255, 85,0, 255, 170,
0, 255, 255, 85, 0, 0,85, 0, 85,85, 0, 170,85, 0, 255,85, 85, 0,85, 85, 85,85, 85, 170,85,
85, 255,85, 170, 0,85, 170, 85, 85, 170, 170,85, 170, 255,85, 255, 0,85, 255, 85,85, 255,
170,85, 255, 255,170, 0, 0,170, 0, 85,170, 0, 170,170, 0, 255,170, 85, 0,170, 85, 85,170,
85, 170,170, 85, 255,170, 170, 0,170, 170, 85,170, 170, 170,170, 170, 255,170, 255, 0,170,
255, 85,170, 255, 170,170, 255, 255,255, 0, 0,255, 0, 85,255, 0, 170,255, 0, 255,255, 85,
0,255, 85, 85,255, 85, 170,255, 85, 255,255, 170, 0,255, 170, 85,255, 170, 170,255, 170,
255,255, 255, 0,255, 255, 85,255, 255, 170,255, 255, 255};
    uint subInvID = gl_SubgroupInvocationID*3;
    invocationRes = uvec3(col[subInvID], col[subInvID+1], col[subInvID+2]);

    uint index = gl_LaunchIDEXT.y * 512 + gl_LaunchIDEXT.x;
    outBuf.values[index] = uint(invocationRes.x) << 16 | uint(invocationRes.y) << 8 | uint(invocationRes.z);
}
```

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `rgen`
- Target SPIRV version: `spirv1.5`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.5
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 234
; Schema: 0
               OpCapability GroupNonUniform
               OpCapability RayTracingKHR
               OpCapability ShaderInvocationReorderEXT
               OpExtension "SPV_EXT_shader_invocation_reorder"
               OpExtension "SPV_KHR_ray_tracing"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint RayGenerationKHR %main "main" %gl_LaunchIDEXT %gl_LaunchSizeEXT %hitValue %hObj %topLevelAS %gl_SubgroupInvocationID %outBuf
               OpSource GLSL 460
               OpSourceExtension "GL_EXT_ray_tracing"
               OpSourceExtension "GL_EXT_shader_invocation_reorder"
               OpSourceExtension "GL_KHR_shader_subgroup_basic"
               OpName %main "main"
               OpName %rand_f1_ "rand(f1;"
               OpName %seed "seed"
               OpName %sampleDisk_f1_ "sampleDisk(f1;"
               OpName %seed_0 "seed"
               OpName %n "n"
               OpName %theta "theta"
               OpName %param "param"
               OpName %r "r"
               OpName %param_0 "param"
               OpName %pixelCenter "pixelCenter"
               OpName %gl_LaunchIDEXT "gl_LaunchIDEXT"
               OpName %inUV "inUV"
               OpName %gl_LaunchSizeEXT "gl_LaunchSizeEXT"
               OpName %d "d"
               OpName %origin "origin"
               OpName %direction "direction"
               OpName %apertureSize "apertureSize"
               OpName %focusDistance "focusDistance"
               OpName %lensSample "lensSample"
               OpName %param_1 "param"
               OpName %defocusedRayOrigin "defocusedRayOrigin"
               OpName %focusPoint "focusPoint"
               OpName %finalRayDirection "finalRayDirection"
               OpName %tmin "tmin"
               OpName %tmax "tmax"
               OpName %hitValue "hitValue"
               OpName %invocationRes "invocationRes"
               OpName %hObj "hObj"
               OpName %topLevelAS "topLevelAS"
               OpName %col "col"
               OpName %subInvID "subInvID"
               OpName %gl_SubgroupInvocationID "gl_SubgroupInvocationID"
               OpName %index "index"
               OpName %OutputBuffer "OutputBuffer"
               OpMemberName %OutputBuffer 0 "values"
               OpName %outBuf "outBuf"
               OpDecorate %gl_LaunchIDEXT BuiltIn LaunchIdKHR
               OpDecorate %gl_LaunchSizeEXT BuiltIn LaunchSizeKHR
               OpDecorate %topLevelAS Binding 0
               OpDecorate %topLevelAS DescriptorSet 0
               OpDecorate %gl_SubgroupInvocationID RelaxedPrecision
               OpDecorate %gl_SubgroupInvocationID BuiltIn SubgroupLocalInvocationId
               OpDecorate %gl_SubgroupInvocationID Volatile
               OpDecorate %gl_SubgroupInvocationID Coherent
               OpDecorate %192 RelaxedPrecision
               OpDecorate %194 RelaxedPrecision
               OpDecorate %_arr_uint_uint_1048576 ArrayStride 4
               OpDecorate %OutputBuffer Block
               OpMemberDecorate %OutputBuffer 0 Offset 0
               OpDecorate %outBuf Binding 1
               OpDecorate %outBuf DescriptorSet 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
%_ptr_Function_float = OpTypePointer Function %float
          %8 = OpTypeFunction %float %_ptr_Function_float
    %v2float = OpTypeVector %float 2
         %13 = OpTypeFunction %v2float %_ptr_Function_float
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
    %uint_61 = OpConstant %uint 61
        %int = OpTypeInt 32 1
     %int_16 = OpConstant %int 16
     %uint_9 = OpConstant %uint 9
      %int_4 = OpConstant %int 4
%uint_668265261 = OpConstant %uint 668265261
     %int_15 = OpConstant %int 15
%float_4_2949673e_09 = OpConstant %float 4.2949673e+09
%float_6_28318548 = OpConstant %float 6.28318548
    %float_1 = OpConstant %float 1
%_ptr_Function_v2float = OpTypePointer Function %v2float
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_LaunchIDEXT = OpVariable %_ptr_Input_v3uint Input
     %v2uint = OpTypeVector %uint 2
  %float_0_5 = OpConstant %float 0.5
         %86 = OpConstantComposite %v2float %float_0_5 %float_0_5
%gl_LaunchSizeEXT = OpVariable %_ptr_Input_v3uint Input
    %float_2 = OpConstant %float 2
    %v3float = OpTypeVector %float 3
%_ptr_Function_v3float = OpTypePointer Function %v3float
   %float_n1 = OpConstant %float -1
    %float_0 = OpConstant %float 0
        %111 = OpConstantComposite %v3float %float_0 %float_0 %float_1
%float_1_14999998 = OpConstant %float 1.14999998
     %uint_0 = OpConstant %uint 0
     %uint_1 = OpConstant %uint 1
%_ptr_Input_uint = OpTypePointer Input %uint
%float_0_00100000005 = OpConstant %float 0.00100000005
%float_10000 = OpConstant %float 10000
%_ptr_RayPayloadKHR_v3float = OpTypePointer RayPayloadKHR %v3float
   %hitValue = OpVariable %_ptr_RayPayloadKHR_v3float RayPayloadKHR
        %156 = OpConstantComposite %v3float %float_0 %float_0 %float_0
%_ptr_Function_v3uint = OpTypePointer Function %v3uint
        %159 = OpConstantComposite %v3uint %uint_0 %uint_0 %uint_0
        %160 = OpTypeHitObjectEXT
%_ptr_Private_160 = OpTypePointer Private %160
       %hObj = OpVariable %_ptr_Private_160 Private
        %163 = OpTypeAccelerationStructureKHR
%_ptr_UniformConstant_163 = OpTypePointer UniformConstant %163
 %topLevelAS = OpVariable %_ptr_UniformConstant_163 UniformConstant
   %uint_255 = OpConstant %uint 255
      %int_0 = OpConstant %int 0
     %uint_2 = OpConstant %uint 2
       %bool = OpTypeBool
   %uint_192 = OpConstant %uint 192
%_arr_uint_uint_192 = OpTypeArray %uint %uint_192
%_ptr_Function__arr_uint_uint_192 = OpTypePointer Function %_arr_uint_uint_192
    %uint_85 = OpConstant %uint 85
   %uint_170 = OpConstant %uint 170
        %189 = OpConstantComposite %_arr_uint_uint_192 %uint_0 %uint_0 %uint_0 %uint_0 %uint_0 %uint_85 %uint_0 %uint_0 %uint_170 %uint_0 %uint_0 %uint_255 %uint_0 %uint_85 %uint_0 %uint_0 %uint_85 %uint_85 %uint_0 %uint_85 %uint_170 %uint_0 %uint_85 %uint_255 %uint_0 %uint_170 %uint_0 %uint_0 %uint_170 %uint_85 %uint_0 %uint_170 %uint_170 %uint_0 %uint_170 %uint_255 %uint_0 %uint_255 %uint_0 %uint_0 %uint_255 %uint_85 %uint_0 %uint_255 %uint_170 %uint_0 %uint_255 %uint_255 %uint_85 %uint_0 %uint_0 %uint_85 %uint_0 %uint_85 %uint_85 %uint_0 %uint_170 %uint_85 %uint_0 %uint_255 %uint_85 %uint_85 %uint_0 %uint_85 %uint_85 %uint_85 %uint_85 %uint_85 %uint_170 %uint_85 %uint_85 %uint_255 %uint_85 %uint_170 %uint_0 %uint_85 %uint_170 %uint_85 %uint_85 %uint_170 %uint_170 %uint_85 %uint_170 %uint_255 %uint_85 %uint_255 %uint_0 %uint_85 %uint_255 %uint_85 %uint_85 %uint_255 %uint_170 %uint_85 %uint_255 %uint_255 %uint_170 %uint_0 %uint_0 %uint_170 %uint_0 %uint_85 %uint_170 %uint_0 %uint_170 %uint_170 %uint_0 %uint_255 %uint_170 %uint_85 %uint_0 %uint_170 %uint_85 %uint_85 %uint_170 %uint_85 %uint_170 %uint_170 %uint_85 %uint_255 %uint_170 %uint_170 %uint_0 %uint_170 %uint_170 %uint_85 %uint_170 %uint_170 %uint_170 %uint_170 %uint_170 %uint_255 %uint_170 %uint_255 %uint_0 %uint_170 %uint_255 %uint_85 %uint_170 %uint_255 %uint_170 %uint_170 %uint_255 %uint_255 %uint_255 %uint_0 %uint_0 %uint_255 %uint_0 %uint_85 %uint_255 %uint_0 %uint_170 %uint_255 %uint_0 %uint_255 %uint_255 %uint_85 %uint_0 %uint_255 %uint_85 %uint_85 %uint_255 %uint_85 %uint_170 %uint_255 %uint_85 %uint_255 %uint_255 %uint_170 %uint_0 %uint_255 %uint_170 %uint_85 %uint_255 %uint_170 %uint_170 %uint_255 %uint_170 %uint_255 %uint_255 %uint_255 %uint_0 %uint_255 %uint_255 %uint_85 %uint_255 %uint_255 %uint_170 %uint_255 %uint_255 %uint_255
%gl_SubgroupInvocationID = OpVariable %_ptr_Input_uint Input
     %uint_3 = OpConstant %uint 3
   %uint_512 = OpConstant %uint 512
%uint_1048576 = OpConstant %uint 1048576
%_arr_uint_uint_1048576 = OpTypeArray %uint %uint_1048576
%OutputBuffer = OpTypeStruct %_arr_uint_uint_1048576
%_ptr_StorageBuffer_OutputBuffer = OpTypePointer StorageBuffer %OutputBuffer
     %outBuf = OpVariable %_ptr_StorageBuffer_OutputBuffer StorageBuffer
      %int_8 = OpConstant %int 8
%_ptr_StorageBuffer_uint = OpTypePointer StorageBuffer %uint
       %main = OpFunction %void None %3
          %5 = OpLabel
%pixelCenter = OpVariable %_ptr_Function_v2float Function
       %inUV = OpVariable %_ptr_Function_v2float Function
          %d = OpVariable %_ptr_Function_v2float Function
     %origin = OpVariable %_ptr_Function_v3float Function
  %direction = OpVariable %_ptr_Function_v3float Function
%apertureSize = OpVariable %_ptr_Function_float Function
%focusDistance = OpVariable %_ptr_Function_float Function
 %lensSample = OpVariable %_ptr_Function_v2float Function
    %param_1 = OpVariable %_ptr_Function_float Function
%defocusedRayOrigin = OpVariable %_ptr_Function_v3float Function
 %focusPoint = OpVariable %_ptr_Function_v3float Function
%finalRayDirection = OpVariable %_ptr_Function_v3float Function
       %tmin = OpVariable %_ptr_Function_float Function
       %tmax = OpVariable %_ptr_Function_float Function
%invocationRes = OpVariable %_ptr_Function_v3uint Function
        %col = OpVariable %_ptr_Function__arr_uint_uint_192 Function
   %subInvID = OpVariable %_ptr_Function_uint Function
      %index = OpVariable %_ptr_Function_uint Function
         %82 = OpLoad %v3uint %gl_LaunchIDEXT
         %83 = OpVectorShuffle %v2uint %82 %82 0 1
         %84 = OpConvertUToF %v2float %83
         %87 = OpFAdd %v2float %84 %86
               OpStore %pixelCenter %87
         %89 = OpLoad %v2float %pixelCenter
         %91 = OpLoad %v3uint %gl_LaunchSizeEXT
         %92 = OpVectorShuffle %v2uint %91 %91 0 1
         %93 = OpConvertUToF %v2float %92
         %94 = OpFDiv %v2float %89 %93
               OpStore %inUV %94
         %96 = OpLoad %v2float %inUV
         %98 = OpVectorTimesScalar %v2float %96 %float_2
         %99 = OpCompositeConstruct %v2float %float_1 %float_1
        %100 = OpFSub %v2float %98 %99
               OpStore %d %100
        %104 = OpLoad %v2float %d
        %106 = OpCompositeExtract %float %104 0
        %107 = OpCompositeExtract %float %104 1
        %108 = OpCompositeConstruct %v3float %106 %107 %float_n1
               OpStore %origin %108
               OpStore %direction %111
               OpStore %apertureSize %float_1
               OpStore %focusDistance %float_1_14999998
        %117 = OpAccessChain %_ptr_Function_float %pixelCenter %uint_0
        %118 = OpLoad %float %117
        %120 = OpAccessChain %_ptr_Function_float %pixelCenter %uint_1
        %121 = OpLoad %float %120
        %123 = OpAccessChain %_ptr_Input_uint %gl_LaunchSizeEXT %uint_0
        %124 = OpLoad %uint %123
        %125 = OpConvertUToF %float %124
        %126 = OpFMul %float %121 %125
        %127 = OpFAdd %float %118 %126
               OpStore %param_1 %127
        %129 = OpFunctionCall %v2float %sampleDisk_f1_ %param_1
        %130 = OpLoad %float %apertureSize
        %131 = OpVectorTimesScalar %v2float %129 %130
               OpStore %lensSample %131
        %133 = OpLoad %v3float %origin
        %134 = OpLoad %v2float %lensSample
        %135 = OpCompositeExtract %float %134 0
        %136 = OpCompositeExtract %float %134 1
        %137 = OpCompositeConstruct %v3float %135 %136 %float_0
        %138 = OpFAdd %v3float %133 %137
               OpStore %defocusedRayOrigin %138
        %140 = OpLoad %v3float %origin
        %141 = OpLoad %float %focusDistance
        %142 = OpLoad %v3float %direction
        %143 = OpVectorTimesScalar %v3float %142 %141
        %144 = OpFAdd %v3float %140 %143
               OpStore %focusPoint %144
        %146 = OpLoad %v3float %focusPoint
        %147 = OpLoad %v3float %defocusedRayOrigin
        %148 = OpFSub %v3float %146 %147
        %149 = OpExtInst %v3float %1 Normalize %148
               OpStore %finalRayDirection %149
               OpStore %tmin %float_0_00100000005
               OpStore %tmax %float_10000
               OpStore %hitValue %156
               OpStore %invocationRes %159
               OpHitObjectRecordEmptyEXT %hObj
        %166 = OpLoad %163 %topLevelAS
        %168 = OpLoad %v3float %defocusedRayOrigin
        %169 = OpLoad %float %tmin
        %170 = OpLoad %v3float %finalRayDirection
        %171 = OpLoad %float %tmax
               OpHitObjectTraceRayEXT %hObj %166 %uint_1 %uint_255 %uint_0 %uint_0 %uint_0 %168 %169 %170 %171 %hitValue
        %173 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_0
        %174 = OpLoad %uint %173
        %175 = OpAccessChain %_ptr_Input_uint %gl_LaunchSizeEXT %uint_0
        %176 = OpLoad %uint %175
        %178 = OpUDiv %uint %176 %uint_2
        %180 = OpUGreaterThan %bool %174 %178
               OpSelectionMerge %182 None
               OpBranchConditional %180 %181 %182
        %181 = OpLabel
               OpReorderThreadWithHitObjectEXT %hObj
               OpBranch %182
        %182 = OpLabel
               OpHitObjectExecuteShaderEXT %hObj %hitValue
               OpStore %col %189
        %192 = OpLoad %uint %gl_SubgroupInvocationID
        %194 = OpIMul %uint %192 %uint_3
               OpStore %subInvID %194
        %195 = OpLoad %uint %subInvID
        %196 = OpAccessChain %_ptr_Function_uint %col %195
        %197 = OpLoad %uint %196
        %198 = OpLoad %uint %subInvID
        %199 = OpIAdd %uint %198 %uint_1
        %200 = OpAccessChain %_ptr_Function_uint %col %199
        %201 = OpLoad %uint %200
        %202 = OpLoad %uint %subInvID
        %203 = OpIAdd %uint %202 %uint_2
        %204 = OpAccessChain %_ptr_Function_uint %col %203
        %205 = OpLoad %uint %204
        %206 = OpCompositeConstruct %v3uint %197 %201 %205
               OpStore %invocationRes %206
        %208 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_1
        %209 = OpLoad %uint %208
        %211 = OpIMul %uint %209 %uint_512
        %212 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_0
        %213 = OpLoad %uint %212
        %214 = OpIAdd %uint %211 %213
               OpStore %index %214
        %220 = OpLoad %uint %index
        %221 = OpAccessChain %_ptr_Function_uint %invocationRes %uint_0
        %222 = OpLoad %uint %221
        %223 = OpShiftLeftLogical %uint %222 %int_16
        %224 = OpAccessChain %_ptr_Function_uint %invocationRes %uint_1
        %225 = OpLoad %uint %224
        %227 = OpShiftLeftLogical %uint %225 %int_8
        %228 = OpBitwiseOr %uint %223 %227
        %229 = OpAccessChain %_ptr_Function_uint %invocationRes %uint_2
        %230 = OpLoad %uint %229
        %231 = OpBitwiseOr %uint %228 %230
        %233 = OpAccessChain %_ptr_StorageBuffer_uint %outBuf %int_0 %220
               OpStore %233 %231
               OpReturn
               OpFunctionEnd
   %rand_f1_ = OpFunction %float None %8
       %seed = OpFunctionParameter %_ptr_Function_float
         %11 = OpLabel
          %n = OpVariable %_ptr_Function_uint Function
         %20 = OpLoad %float %seed
         %21 = OpBitcast %uint %20
               OpStore %n %21
         %22 = OpLoad %uint %n
         %24 = OpBitwiseXor %uint %22 %uint_61
         %25 = OpLoad %uint %n
         %28 = OpShiftRightLogical %uint %25 %int_16
         %29 = OpBitwiseXor %uint %24 %28
               OpStore %n %29
         %31 = OpLoad %uint %n
         %32 = OpIMul %uint %31 %uint_9
               OpStore %n %32
         %33 = OpLoad %uint %n
         %34 = OpLoad %uint %n
         %36 = OpShiftRightLogical %uint %34 %int_4
         %37 = OpBitwiseXor %uint %33 %36
               OpStore %n %37
         %39 = OpLoad %uint %n
         %40 = OpIMul %uint %39 %uint_668265261
               OpStore %n %40
         %41 = OpLoad %uint %n
         %42 = OpLoad %uint %n
         %44 = OpShiftRightLogical %uint %42 %int_15
         %45 = OpBitwiseXor %uint %41 %44
               OpStore %n %45
         %46 = OpLoad %uint %n
         %47 = OpConvertUToF %float %46
         %49 = OpFDiv %float %47 %float_4_2949673e_09
               OpReturnValue %49
               OpFunctionEnd
%sampleDisk_f1_ = OpFunction %v2float None %13
     %seed_0 = OpFunctionParameter %_ptr_Function_float
         %16 = OpLabel
      %theta = OpVariable %_ptr_Function_float Function
      %param = OpVariable %_ptr_Function_float Function
          %r = OpVariable %_ptr_Function_float Function
    %param_0 = OpVariable %_ptr_Function_float Function
         %55 = OpLoad %float %seed_0
               OpStore %param %55
         %56 = OpFunctionCall %float %rand_f1_ %param
         %57 = OpFMul %float %float_6_28318548 %56
               OpStore %theta %57
         %59 = OpLoad %float %seed_0
         %61 = OpFAdd %float %59 %float_1
               OpStore %param_0 %61
         %63 = OpFunctionCall %float %rand_f1_ %param_0
         %64 = OpExtInst %float %1 Sqrt %63
               OpStore %r %64
         %65 = OpLoad %float %r
         %66 = OpLoad %float %theta
         %67 = OpExtInst %float %1 Cos %66
         %68 = OpFMul %float %65 %67
         %69 = OpLoad %float %r
         %70 = OpLoad %float %theta
         %71 = OpExtInst %float %1 Sin %70
         %72 = OpFMul %float %69 %71
         %73 = OpCompositeConstruct %v2float %68 %72
               OpReturnValue %73
               OpFunctionEnd
```

</details>## Runtime Execution and Result Checking

### Feature and hint gating

- Before running the trace, the instance queries `VkPhysicalDeviceRayTracingInvocationReorderPropertiesEXT::rayTracingInvocationReorderReorderingHint`. If the hint is `VK_RAY_TRACING_INVOCATION_REORDER_MODE_NONE_EXT`, the test passes immediately: the implementation declares it does not reorder, so there is nothing to verify [hint gate](../../../modules/vulkan/ray_tracing/vktRayTracingInvocationReorderActivityTests.cpp#L382-L384).
- The instance also queries `VkPhysicalDeviceRayTracingInvocationReorderFeaturesEXT::rayTracingInvocationReorder`. If the feature bit is `0`, the test passes immediately [feature gate](../../../modules/vulkan/ray_tracing/vktRayTracingInvocationReorderActivityTests.cpp#L390-L401).
- The instance queries the subgroup size and asserts that `resX` and `resY` are multiples of 2, and that `resX/2` and `resY/2` are multiples of the subgroup size. This ensures each half of the image contains whole subgroups [resolution assertion](../../../modules/vulkan/ray_tracing/vktRayTracingInvocationReorderActivityTests.cpp#L403-L419).

### Scene construction

- One BLAS holds a single opaque triangle quad (two triangles covering a 0.48 x 0.48 region) [BLAS build](../../../modules/vulkan/ray_tracing/vktRayTracingInvocationReorderActivityTests.cpp#L432-L449).
- The TLAS has 16 instances, each referencing the same BLAS with a different transform. The instance SBT record offset is `2*j + i` for `n` in {0,1}, `j` in {0..3}, `i` in {0,1}, so the 16 instances map to 8 distinct hit groups. Consecutive pixels trace defocused rays that hit different instances, creating the incoherent workload that reordering targets [TLAS build](../../../modules/vulkan/ray_tracing/vktRayTracingInvocationReorderActivityTests.cpp#L458-L467).

### Pipeline and dispatch

- The ray tracing pipeline has 10 shader groups: one rgen, one miss, and eight closest-hit shaders (`ch0` through `ch7`) with `uScale` constants from 10.0 to 80.0. Each closest-hit shader runs a nested loop (100 outer, 100 inner) of `sin`/`cos`/`fract` operations to simulate a heavy material workload [pipeline creation](../../../modules/vulkan/ray_tracing/vktRayTracingInvocationReorderActivityTests.cpp#L545-L574).
- `cmdTraceRaysKHR` dispatches `512 x 512 x 1` rays. A `SHADER_WRITE` to `HOST_READ` memory barrier separates the trace from the host read [trace and barrier](../../../modules/vulkan/ray_tracing/vktRayTracingInvocationReorderActivityTests.cpp#L577-L589).

### Result check

- The host invalidates the output buffer allocation, copies the data into a `std::vector<uint32_t>`, and compares the left and right halves column by column. For each `(i, j)` with `i` in `[0, resX/2)`, it compares `outputData[j * resX + i]` (left half) against `outputData[j * resX + (i + resX/2)]` (right half) [result check](../../../modules/vulkan/ray_tracing/vktRayTracingInvocationReorderActivityTests.cpp#L600-L610).
- Since `use_shader_invocation_reorder = true`, the test expects a mismatch. If `matchFlag == true` (all pixels match), the test calls `TCU_FAIL("Comparison should not match")`. If `matchFlag == false` (at least one pixel differs), the test passes [pass/fail](../../../modules/vulkan/ray_tracing/vktRayTracingInvocationReorderActivityTests.cpp#L612-L618).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `activity` | The implementation declares `rayTracingInvocationReorder` feature support and a non-`NONE` reorder hint, but `reorderThreadEXT` is a no-op and does not actually perturb subgroup invocation grouping. |

### Cause Analysis

#### Reorder is a declared but inert no-op

**Possible failure symptoms:** The test reaches the trace and comparison stage (feature bit is set, hint is not `NONE`), and `matchFlag == true`: every pixel in the left half equals the corresponding pixel in the right half. The test calls `TCU_FAIL("Comparison should not match")`. The packed RGB values derived from `gl_SubgroupInvocationID` are identical across both halves, meaning the subgroup composition was not perturbed by `reorderThreadEXT`.

**Possible implementation causes:** The implementation advertises the `rayTracingInvocationReorder` feature and reports a non-`NONE` reorder hint, which tells the test that reordering is expected to occur. The rgen shader calls `reorderThreadEXT(hObj)` only on the right half. If the implementation treats this call as a hint it chooses to ignore, the subgroup assignment on the right half matches the left half, and the `gl_SubgroupInvocationID`-derived colors match. Source-level investigation should confirm that the right-half condition `gl_LaunchIDEXT.x > gl_LaunchSizeEXT.x / 2` was reached (it is, per the SPIR-V conditional branch at `OpBranchConditional %180`), that the hit object was populated by `OpHitObjectTraceRayEXT` before the reorder call, and that the defocus parameters actually produce incoherent hits across the 16 instances. If the defocus were too weak to spread rays across instances, both halves would hit the same materials in the same subgroup pattern regardless of reordering, but the defocus (`apertureSize = 1.0`, `focusDistance = 1.15`) and the 16-instance layout with 0.5-unit spacing are designed to prevent this.

## Case Pruning

### Requirement-based pruning

- The test requires `VK_KHR_deferred_host_operations`, `VK_KHR_acceleration_structure`, `VK_KHR_ray_tracing_pipeline`, `VK_KHR_buffer_device_address`, and `VK_EXT_ray_tracing_invocation_reorder` [checkSupport](../../../modules/vulkan/ray_tracing/vktRayTracingInvocationReorderActivityTests.cpp#L96-L103).
- The `bufferDeviceAddress`, `rayTracingPipeline`, and `accelerationStructure` feature bits must be set, otherwise the test throws `TestError` [feature checks](../../../modules/vulkan/ray_tracing/vktRayTracingInvocationReorderActivityTests.cpp#L105-L119).
- The `rayTracingInvocationReorder` feature bit must be set, otherwise the test throws `NotSupportedError` [reorder feature check](../../../modules/vulkan/ray_tracing/vktRayTracingInvocationReorderActivityTests.cpp#L122-L126).

### Design-based pruning

- The family has no generated matrix. Only one `TestParams` combination is registered: `use_shader_invocation_reorder = true`, `resX = 512`, `resY = 512`. The `use_shader_invocation_reorder = false` shader path exists in `initPrograms` but is never registered as a test case.
- The resolution comment notes "Test may not work at lower resolutions" [registration comment](../../../modules/vulkan/ray_tracing/vktRayTracingInvocationReorderActivityTests.cpp#L641). The 512x512 size ensures enough subgroups for the reorder signal to be distinguishable from noise.

## Key Takeaways

- The `rtir_activity` family has one leaf, `activity`, that verifies `reorderThreadEXT` produces observable reordering when the implementation claims to support it.
- The detection mechanism is indirect: the rgen shader derives each pixel's color from `gl_SubgroupInvocationID`, so a change in subgroup composition (caused by reordering) changes the color pattern. The left half skips `reorderThreadEXT` as the reference; the right half calls it. A mismatch between halves proves reordering occurred.
- The test passes early if the implementation reports `NONE` reorder hint or does not expose the feature, because there is nothing to verify in those cases.
- The only failure mode is the implementation declaring reordering support and a non-`NONE` hint but treating `reorderThreadEXT` as a silent no-op. See `## Failure Meaning` for the cause analysis.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `TestParams` struct | [vktRayTracingInvocationReorderActivityTests.cpp#L53-L57](../../../modules/vulkan/ray_tracing/vktRayTracingInvocationReorderActivityTests.cpp#L53-L57) | Per-case parameters: reorder flag and resolution |
| `checkSupport` | [vktRayTracingInvocationReorderActivityTests.cpp#L96-L127](../../../modules/vulkan/ray_tracing/vktRayTracingInvocationReorderActivityTests.cpp#L96-L127) | Feature gates for ray tracing, acceleration structure, buffer device address, and invocation reorder |
| `initPrograms` | [vktRayTracingInvocationReorderActivityTests.cpp#L129-L339](../../../modules/vulkan/ray_tracing/vktRayTracingInvocationReorderActivityTests.cpp#L129-L339) | rgen (with and without reorder paths), miss, and eight closest-hit shaders |
| `iterate` | [vktRayTracingInvocationReorderActivityTests.cpp#L352-L630](../../../modules/vulkan/ray_tracing/vktRayTracingInvocationReorderActivityTests.cpp#L352-L630) | Hint/feature gating, scene build, trace dispatch, and left/right comparison |
| `createRTIRActivityTests` | [vktRayTracingInvocationReorderActivityTests.cpp#L634-L649](../../../modules/vulkan/ray_tracing/vktRayTracingInvocationReorderActivityTests.cpp#L634-L649) | Registration of the `rtir_activity` group and its single `activity` child |
