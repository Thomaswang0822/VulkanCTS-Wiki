## Overview

**Core question:** Does a ray tracing pipeline created with combinations of `VK_PIPELINE_CREATE_RAY_TRACING_NO_NULL_*_SHADERS_BIT_KHR` flags trace rays correctly when the shader binding table uses nonzero stride and offset, across device and host AS builds, geometry types, and pipeline library modes?

- [vktRayTracingPipelineFlagsTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp) implements the `pipeline_no_null_shaders_flag` test family under the `ray_tracing_pipeline` test category.
- The test generates all non-empty subsets of four NO_NULL pipeline creation flags (any-hit, closest-hit, intersection, miss) and registers a case for each subset, crossed with processor (gpu or cpu), geometry type (triangles, boxes, tri_and_box), SBT stride (3 or 5), SBT offset (7), and library mode (use_libs or no_libs). 300 cases are registered in mustpass.
- Each case builds a ray tracing pipeline with the selected flags, constructs a scene with 3 instances and 2 geometries per instance, traces one ray per pixel down the -z axis, and compares the result image against a host-side offline ray trace using a flood-fill similarity check with a 0.95 accuracy threshold.
- The `misc` subgroup adds four standalone cases that exercise each flag individually with `VK_KHR_maintenance5` enabled, using the `setCreateFlags2` creation path instead of the legacy `setCreateFlags` path.
- The page explains the flag combination matrix, the SBT layout with nonzero stride and offset, the shader set, the flood-fill validation, and what a failure of each processor path points to.

## Background Knowledge

- **NO_NULL pipeline creation flags.** `VK_PIPELINE_CREATE_RAY_TRACING_NO_NULL_*_SHADERS_BIT_KHR` flags declare that the pipeline will never encounter a null shader of the corresponding type during traversal. The implementation may use this as an optimization hint to skip null-shader checks. The four flags cover any-hit, closest-hit, intersection, and miss shaders.
- **Shader binding table stride and offset.** `traceRayEXT` takes `sbtRecordOffset` and `sbtRecordStride` parameters that select which hit group in the SBT to use for a given geometry. The effective hit group index combines the instance's SBT record offset (set in the TLAS instance), the ray's `sbtRecordOffset`, and `geometryIndex * sbtRecordStride`. Nonzero stride and offset exercise SBT indexing beyond the trivial sequential layout.
- **Pipeline libraries.** `VK_KHR_pipeline_library` allows splitting a pipeline into libraries that are linked at creation time. The `use_libs` cases put miss and hit-group shaders into separate library pipelines with `VK_PIPELINE_CREATE_LIBRARY_BIT_KHR`, while `no_libs` builds everything in one pipeline. The rgen shader always stays in the main pipeline.
- **Maintenance5 flag2 creation path.** `VK_KHR_maintenance5` introduces `VkPipelineCreateFlags2CreateInfo`, allowing flags to be set via the extended 2-creation-flags path. The `misc` cases use `setCreateFlags2` to exercise this path with individual NO_NULL flags.
- **Host vs device AS build.** `VK_ACCELERATION_STRUCTURE_BUILD_TYPE_DEVICE_KHR` builds the AS on the GPU via command buffer. `VK_ACCELERATION_STRUCTURE_BUILD_TYPE_HOST_KHR` builds it on the CPU, requiring the `accelerationStructureHostCommands` feature.

## Registration Hierarchy

```text
ray_tracing_pipeline.pipeline_no_null_shaders_flag
├── cpu
├── gpu
└── misc
```

The three direct children are registered by [createPipelineFlagsTests](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L1528-L1643). `gpu` and `cpu` share the same nested matrix (geometry, stride, offset, lib, flags) and differ only in AS build type. `misc` holds four standalone cases that each set one NO_NULL flag with `useMaintenance5 = true`. Below each processor child, the hierarchy continues as `<geometry>.stride_<N>.offset_<N>.<lib>.<flag_combination>` down to the test case leaf.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Processor | `gpu`, `cpu`, `misc` | Selects AS build type (device vs host) and, for `misc`, the maintenance5 flag2 creation path. | [processors and misc arrays](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L1533-L1637) |
| Geometry type | `triangles`, `boxes`, `tri_and_box` | Selects BLAS geometry. Triangles use only chit; boxes require isect; tri_and_box uses both chit and isect. | [geometries array](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L1547-L1549) |
| SBT stride | `3`, `5` | `stbRecStride` passed to `traceRayEXT`. Controls hit-group indexing stride per geometry within an instance. | [strides array](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L1530) |
| SBT offset | `7` | `stbRecOffset` passed to `traceRayEXT`. Fixed offset into the hit-group region of the SBT. | [offsets array](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L1531) |
| Library mode | `use_libs`, `no_libs` | Whether miss and hit-group shaders go into pipeline libraries or the main pipeline. | [libs array](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L1542) |
| NO_NULL flag combination | 15 non-empty subsets of {any, chit, isect, miss} | The tested property. Each subset is OR'd into `VkPipelineCreateFlags`. Triangles prune any combination containing isect, leaving 7. | [NoNullShadersFlagGenerator](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L1450-L1524) |
| misc flag | `any_maintenance5`, `chit_maintenance5`, `isect_maintenance5`, `miss_maintenance5` | Individual flags with `setCreateFlags2`. Fixed: Box geometry, stride 3, offset 7, use_libs. | [misc group](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L1625-L1638) |
| Image size | 256x256 (release), 30x8 (debug) | Result image dimensions. | [width/height](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L1554-L1562) |
| Instance count | 3 | `instCount` in TestParams. Number of TLAS instances. | [TestParams default](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L1568) |
| Geometry count | 2 | `geomCount` in TestParams. Number of geometries per BLAS. | [TestParams default](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L1569) |
| Accuracy | 0.95 (release), 0.80 (debug) | Flood-fill similarity threshold. The ratio of result to reference pixel count must meet or exceed this. | [accuracy](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L1557-L1561) |

The leaf name encodes the flag combination as bit names joined by `_or_`, for example `any_or_chit_or_isect_or_miss` for all four flags. The generator excludes the empty set, so no `none` leaf is registered. The full leaf path is `<processor>.<geometry>.stride_<N>.offset_<N>.<lib>.<flag_combination>`.

## Behavior Parameters

The primary behavioral axis is the processor: the direct child of `pipeline_no_null_shaders_flag` that selects the AS build type and, for `misc`, the flag2 creation path. The flag combination matrix is identical across `gpu` and `cpu`; `misc` narrows it to individual flags with maintenance5.

### gpu — device-side AS build with the full flag matrix

Builds both BLAS and TLAS with `VK_ACCELERATION_STRUCTURE_BUILD_TYPE_DEVICE_KHR` via command buffer. Exercises the full flag combination matrix (15 or 7 subsets depending on geometry) crossed with both stride values, both library modes, and all three geometry types. Pipeline creation uses `setCreateFlags` with the OR'd flag bits. This is the baseline device path. A failure here, when `cpu` passes, points at device-build-specific AS correctness or device-side pipeline creation with the NO_NULL flags.

### cpu — host-side AS build with the full flag matrix

Builds both BLAS and TLAS with `VK_ACCELERATION_STRUCTURE_BUILD_TYPE_HOST_KHR` on the calling host thread. Requires the `accelerationStructureHostCommands` feature. The flag matrix, shader set, SBT layout, and validation are identical to `gpu`; only the AS build type differs. A failure here, when `gpu` passes, points at host-build-specific AS correctness. A failure common to both `gpu` and `cpu` points at shared pipeline or SBT infrastructure.

### misc — individual flags with maintenance5 and the flag2 creation path

Registers four standalone cases, one per NO_NULL flag bit, all with Box geometry, stride 3, offset 7, `use_libs = true`, and `useMaintenance5 = true`. Pipeline creation calls `setCreateFlags2(translateCreateFlag(m_params.flags))` in addition to `setCreateFlags`, exercising the `VkPipelineCreateFlags2CreateInfo` extended path introduced by `VK_KHR_maintenance5`. This subgroup isolates the flag2 creation path from the full combination matrix. A failure here points at the maintenance5 flag2 translation or creation path for the specific flag bit.

## Shader Analysis

The test uses five ray tracing shaders, conditionally built based on the flag combination and geometry type:

- **rgen** (always): traces one ray per pixel down the -z axis into the TLAS, passing `stbRecOffset` and `stbRecStride` from `TestParams` to `traceRayEXT`. Stores the returned payload into a `rgba32i` storage image.
- **miss** (always): returns `record.retValue` from the shader record. The miss shader record stores `(0, '-', 0, 0)` where `'-'` is ASCII 45.
- **chit** (always): if `record.geomType == Triangle`, returns `record.retValue`; otherwise returns `hitAttribute`. Triangle hit records store incrementing green-component values starting at `'A'` (ASCII 65).
- **ahit** (only when `NO_NULL_ANY_HIT` flag is set): calls `ignoreIntersectionEXT` when `record.geomIndex % 2 == 1`. This makes odd-indexed geometries transparent, so rays pass through them to the next geometry or miss.
- **isect** (when `NO_NULL_INTERSECTION` flag is set, or geometry is Box or tri_and_box): sets `hitAttribute = record.retValue + (0, 2, 3, 4)` and calls `reportIntersectionEXT(0.0, 0)`. Box hit records store incrementing green-component values starting at `defBoxRetGreenComp`.

The shader record (`ShaderRecordEXT`) is a std430 struct with `geomType` (uint), `geomIndex` (uint), and `retValue` (ivec4), stored in the SBT after the shader group handle. The `retValue` green component is the distinguishing color for each geometry in the flood-fill check.

The rgen shader is the entry point that exercises the SBT stride and offset mechanism, which is the core of what the NO_NULL flags interact with. The other shaders are identical across all cases; only their presence in the pipeline varies with the flags.

### Representative Shader Walkthrough 1

**CTS case:** `dEQP-VK.ray_tracing_pipeline.pipeline_no_null_shaders_flag.gpu.tri_and_box.stride_3.offset_7.use_libs.any_or_chit_or_isect_or_miss`

This case exercises all five shaders (rgen, miss, chit, ahit, isect) with all four NO_NULL flags set. It uses tri_and_box geometry, requiring both triangle and intersection hit groups. The SBT uses stride 3 and offset 7, and the pipeline is built with pipeline libraries. This case covers the widest parameter combination in the matrix.

**Reconstructed GLSL (rgen):**

```glsl
#version 460 core
#extension GL_EXT_ray_tracing : require
layout(location = 0) rayPayloadEXT ivec4 payload;
layout(rgba32i, set = 0, binding = 0) uniform iimage2D result;
layout(set = 0, binding = 1) uniform accelerationStructureEXT topLevelAS;
void main()
{
  float rx           = (float(gl_LaunchIDEXT.x * 2) / float(gl_LaunchSizeEXT.x)) - 1.0;
  float ry           = (float(gl_LaunchIDEXT.y) + 0.5) / float(gl_LaunchSizeEXT.y);
  /// rgenPayload is tcu::IVec4(0, ':', 0, 0); ':' has ASCII value 58
  payload            = ivec4(0, 58, 0, 0);
  uint  rayFlags     = gl_RayFlagsNoneEXT;
  uint  cullMask     = 0xFFu;
  /// SBT record offset and stride from TestParams (stbRecOffset=7, stbRecStride=3)
  uint  stbRecOffset = 7u;
  uint  stbRecStride = 3u;
  uint  missIdx      = 0u;
  vec3  orig         = vec3(rx, ry, 1.0);
  float tmin         = 0.0;
  vec3  dir          = vec3(0.0, 0.0, -1.0);
  float tmax         = 1000.0;
  traceRayEXT(topLevelAS, rayFlags, cullMask, stbRecOffset, stbRecStride, missIdx, orig, tmin, dir, tmax, 0);
  imageStore(result, ivec2(gl_LaunchIDEXT.xy), payload);
}
```

**Shader resources:**

| Resource | Binding | Type | Role |
|----------|---------|------|------|
| `payload` | location 0 | `rayPayloadEXT ivec4` | Ray payload, written by miss/chit/isect, read back by rgen |
| `result` | set 0, binding 0 | `rgba32i uniform iimage2D` | Storage image storing per-pixel result |
| `topLevelAS` | set 0, binding 1 | `accelerationStructureEXT` | TLAS to trace against |

**Walkthrough:**

1. The rgen shader maps `gl_LaunchIDEXT.xy` to ray origin coordinates. The x coordinate maps to `[-1, 1)` and the y coordinate maps to `[0, 1)`, covering the 2D extent of the geometry.
2. The payload is initialized to `ivec4(0, 58, 0, 0)`. The value 58 is the ASCII code for `':'`, used as the default rgen payload green component. If no shader modifies the payload, this value is stored.
3. The ray is traced with `sbtRecOffset = 7` and `sbtRecStride = 3`. These select which hit group in the SBT processes the ray for a given geometry. The effective hit group index for geometry `g` of instance `i` is `i * groupsAndGapsPerInstance + 7 + g * 3`, where `groupsAndGapsPerInstance = geomCount * stbRecStride + stbRecOffset + 1 = 2 * 3 + 7 + 1 = 14`.
4. The ray origin is at `(rx, ry, 1.0)` and direction is `(0, 0, -1)`, traveling straight down the -z axis with `tmin = 0.0` and `tmax = 1000.0`. All geometry is placed at `z = 0.0`.
5. After `traceRayEXT` returns, the payload holds the result from whichever shader last wrote it (miss, chit, or the rgen default if no shader ran). The result is stored to the image at `gl_LaunchIDEXT.xy`.

The key SPIR-V operations are the `OpTraceRayKHR` instruction (line 131 in the disassembly) which encodes all SBT parameters, and the `OpImageWrite` with `SignExtend` (line 137) which stores the signed integer payload.

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
; Bound: 90
; Schema: 0
               OpCapability RayTracingKHR
               OpExtension "SPV_KHR_ray_tracing"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint RayGenerationKHR %main "main" %gl_LaunchIDEXT %gl_LaunchSizeEXT %payload %topLevelAS %result
               OpSource GLSL 460
               OpSourceExtension "GL_EXT_ray_tracing"
               OpName %main "main"
               OpName %rx "rx"
               OpName %gl_LaunchIDEXT "gl_LaunchIDEXT"
               OpName %gl_LaunchSizeEXT "gl_LaunchSizeEXT"
               OpName %ry "ry"
               OpName %payload "payload"
               OpName %rayFlags "rayFlags"
               OpName %cullMask "cullMask"
               OpName %stbRecOffset "stbRecOffset"
               OpName %stbRecStride "stbRecStride"
               OpName %missIdx "missIdx"
               OpName %orig "orig"
               OpName %tmin "tmin"
               OpName %dir "dir"
               OpName %tmax "tmax"
               OpName %topLevelAS "topLevelAS"
               OpName %result "result"
               OpDecorate %gl_LaunchIDEXT BuiltIn LaunchIdKHR
               OpDecorate %gl_LaunchSizeEXT BuiltIn LaunchSizeKHR
               OpDecorate %topLevelAS Binding 1
               OpDecorate %topLevelAS DescriptorSet 0
               OpDecorate %result Binding 0
               OpDecorate %result DescriptorSet 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
%_ptr_Function_float = OpTypePointer Function %float
       %uint = OpTypeInt 32 0
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_LaunchIDEXT = OpVariable %_ptr_Input_v3uint Input
     %uint_0 = OpConstant %uint 0
%_ptr_Input_uint = OpTypePointer Input %uint
     %uint_2 = OpConstant %uint 2
%gl_LaunchSizeEXT = OpVariable %_ptr_Input_v3uint Input
    %float_1 = OpConstant %float 1
     %uint_1 = OpConstant %uint 1
  %float_0_5 = OpConstant %float 0.5
        %int = OpTypeInt 32 1
      %v4int = OpTypeVector %int 4
%_ptr_RayPayloadKHR_v4int = OpTypePointer RayPayloadKHR %v4int
    %payload = OpVariable %_ptr_RayPayloadKHR_v4int RayPayloadKHR
      %int_0 = OpConstant %int 0
     %int_58 = OpConstant %int 58
         %44 = OpConstantComposite %v4int %int_0 %int_58 %int_0 %int_0
%_ptr_Function_uint = OpTypePointer Function %uint
   %uint_255 = OpConstant %uint 255
     %uint_7 = OpConstant %uint 7
     %uint_3 = OpConstant %uint 3
    %v3float = OpTypeVector %float 3
%_ptr_Function_v3float = OpTypePointer Function %v3float
    %float_0 = OpConstant %float 0
   %float_n1 = OpConstant %float -1
         %64 = OpConstantComposite %v3float %float_0 %float_0 %float_n1
 %float_1000 = OpConstant %float 1000
         %67 = OpTypeAccelerationStructureKHR
%_ptr_UniformConstant_67 = OpTypePointer UniformConstant %67
 %topLevelAS = OpVariable %_ptr_UniformConstant_67 UniformConstant
         %80 = OpTypeImage %int 2D 0 0 0 2 Rgba32i
%_ptr_UniformConstant_80 = OpTypePointer UniformConstant %80
     %result = OpVariable %_ptr_UniformConstant_80 UniformConstant
     %v2uint = OpTypeVector %uint 2
      %v2int = OpTypeVector %int 2
       %main = OpFunction %void None %3
          %5 = OpLabel
         %rx = OpVariable %_ptr_Function_float Function
         %ry = OpVariable %_ptr_Function_float Function
   %rayFlags = OpVariable %_ptr_Function_uint Function
   %cullMask = OpVariable %_ptr_Function_uint Function
%stbRecOffset = OpVariable %_ptr_Function_uint Function
%stbRecStride = OpVariable %_ptr_Function_uint Function
    %missIdx = OpVariable %_ptr_Function_uint Function
       %orig = OpVariable %_ptr_Function_v3float Function
       %tmin = OpVariable %_ptr_Function_float Function
        %dir = OpVariable %_ptr_Function_v3float Function
       %tmax = OpVariable %_ptr_Function_float Function
         %15 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_0
         %16 = OpLoad %uint %15
         %18 = OpIMul %uint %16 %uint_2
         %19 = OpConvertUToF %float %18
         %21 = OpAccessChain %_ptr_Input_uint %gl_LaunchSizeEXT %uint_0
         %22 = OpLoad %uint %21
         %23 = OpConvertUToF %float %22
         %24 = OpFDiv %float %19 %23
         %26 = OpFSub %float %24 %float_1
               OpStore %rx %26
         %29 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_1
         %30 = OpLoad %uint %29
         %31 = OpConvertUToF %float %30
         %33 = OpFAdd %float %31 %float_0_5
         %34 = OpAccessChain %_ptr_Input_uint %gl_LaunchSizeEXT %uint_1
         %35 = OpLoad %uint %34
         %36 = OpConvertUToF %float %35
         %37 = OpFDiv %float %33 %36
               OpStore %ry %37
               OpStore %payload %44
               OpStore %rayFlags %uint_0
               OpStore %cullMask %uint_255
               OpStore %stbRecOffset %uint_7
               OpStore %stbRecStride %uint_3
               OpStore %missIdx %uint_0
         %57 = OpLoad %float %rx
         %58 = OpLoad %float %ry
         %59 = OpCompositeConstruct %v3float %57 %58 %float_1
               OpStore %orig %59
               OpStore %tmin %float_0
               OpStore %dir %64
               OpStore %tmax %float_1000
         %70 = OpLoad %67 %topLevelAS
         %71 = OpLoad %uint %rayFlags
         %72 = OpLoad %uint %cullMask
         %73 = OpLoad %uint %stbRecOffset
         %74 = OpLoad %uint %stbRecStride
         %75 = OpLoad %uint %missIdx
         %76 = OpLoad %v3float %orig
         %77 = OpLoad %float %tmin
         %78 = OpLoad %v3float %dir
         %79 = OpLoad %float %tmax
               OpTraceRayKHR %70 %71 %72 %73 %74 %75 %76 %77 %78 %79 %payload
         %83 = OpLoad %80 %result
         %85 = OpLoad %v3uint %gl_LaunchIDEXT
         %86 = OpVectorShuffle %v2uint %85 %85 0 1
         %88 = OpBitcast %v2int %86
         %89 = OpLoad %v4int %payload
               OpImageWrite %83 %88 %89 SignExtend
               OpReturn
               OpFunctionEnd
```

</details>## Runtime Execution and Result Checking

### Pipeline construction

- The `RayTracingTestPipeline` constructor always creates rgen, miss, and chit modules. It creates the ahit module only when the `NO_NULL_ANY_HIT` flag is set, and the isect module when the `NO_NULL_INTERSECTION` flag is set or the geometry type includes boxes [module creation](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L316-L337).
- Pipeline flags are set via `setCreateFlags(m_params.flags)`. For `misc` cases, `setCreateFlags2(translateCreateFlag(m_params.flags))` is also called to exercise the maintenance5 path [flag setup](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L331-L333).
- When `useLibs` is true, miss and hit-group shaders are placed in separate pipeline libraries with `VK_PIPELINE_CREATE_LIBRARY_BIT_KHR`. The rgen shader stays in the main pipeline. The final pipeline is created by linking the libraries [createPipeline](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L434-L472).
- Max payload and attribute sizes are both set to `sizeof(ivec4)` (16 bytes) to match the `ShaderRecordEXT::retValue` field [payload setup](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L335-L336).

### Scene and SBT construction

- BLAS are created per instance. Triangle BLAS hold 2 triangle geometries each; box BLAS hold 2 AABB geometries each. For `tri_and_box`, both triangle and box BLAS are created. Geometry flags use `VK_GEOMETRY_NO_DUPLICATE_ANY_HIT_INVOCATION_BIT_KHR` when ahit is enabled, or `VK_GEOMETRY_OPAQUE_BIT_KHR` otherwise [BLAS creation](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L842-L902).
- The TLAS instances all BLAS with identity transforms. Each instance's SBT record offset is `i * groupsAndGapsPerInstance` where `groupsAndGapsPerInstance = geomCount * stbRecStride + stbRecOffset + 1` [TLAS creation](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L904-L929).
- The SBT is built by `prepareShaderBindingTable`, which lays out groups as: index 0 for rgen, index 1 for miss, and indices 2+ for hit groups. Each hit group record stores `geomType`, `geomIndex`, and `retValue` (a distinct green-component value per geometry) [SBT preparation](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L931-L1026).

### Trace and result copyback

- The result image is a 256x256 `R32G32B32A32_SINT` storage image, transitioned to `GENERAL` layout before the trace [image setup](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L1330-L1336).
- `cmdTraceRays` dispatches `width x height x 1` rays. Each rgen invocation traces one ray down -z into the TLAS [trace dispatch](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L1420-L1425).
- After the trace, a `SHADER_WRITE` to `TRANSFER_READ` barrier, `cmdCopyImageToBuffer`, and a `TRANSFER_WRITE` to `HOST_READ` barrier move the image into a host-visible buffer [copyback](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L1427-L1438).

### Flood-fill similarity check

- The host builds a reference image by offline ray tracing (`travelRay` for each pixel), using the same geometry, SBT, and shader logic as the GPU trace [verifyResult](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L1203-L1228).
- For each geometry (excluding those where ahit would ignore the intersection, i.e., `geomIndex % 2 == 1`), the host finds the geometry's center, gets the required color from the reference image, and flood-fills from the center in both result and reference images within the geometry's projected area [flood-fill](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L1041-L1095).
- The similarity ratio is `min(resultPixelCount, referencePixelCount) / max(resultPixelCount, referencePixelCount)`. The case passes when similarity meets or exceeds the accuracy threshold (0.95 in release) for all checked geometries [similarity check](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L1269-L1276).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `gpu` | Device-side AS build did not produce a structure that traverses to the expected hit/miss pattern, or device-side pipeline creation with NO_NULL flags is broken. |
| `cpu` | Host-side AS build did not produce a correct structure, or `accelerationStructureHostCommands` host build path has a correctness bug. |
| `misc` | The maintenance5 `setCreateFlags2` translation or flag2 creation path is broken for the specific NO_NULL flag bit. |

All `gpu` and `cpu` cases share the same shader set, SBT layout, pipeline construction logic, and flood-fill validation. A failure common to both `gpu` and `cpu` for the same flag combination, geometry, stride, and lib points at shared pipeline or SBT infrastructure rather than an AS-build-specific issue.

### Cause Analysis

#### Device-side build and pipeline creation failure

**Possible failure symptoms:** A `gpu` case fails where the corresponding `cpu` case with the same flag combination, geometry, stride, offset, and lib passes. The flood-fill similarity ratio for one or more geometries falls below 0.95.

**Possible implementation causes:** The `gpu` path builds BLAS and TLAS on the device via command buffer. The traversal result depends on the device-built structure matching the host-built reference. A grounded investigation should check whether the device build completed and was made visible to the trace (both are in the same command buffer), whether the BLAS geometry data uploaded to device buffers matches the host-side geometry used by the offline reference trace, and whether the TLAS instance SBT record offsets were set correctly. If only specific flag combinations fail, the cause may be in how the implementation handles the NO_NULL flag declarations during device-side pipeline creation. Source-level investigation is needed if the pattern is flag-specific.

#### Host-side build correctness failure

**Possible failure symptoms:** A `cpu` case fails where the corresponding `gpu` case passes, or `cpu` and `gpu` both fail for the same flag combination. The flood-fill similarity ratio falls below 0.95.

**Possible implementation causes:** The `cpu` path builds BLAS and TLAS on the host with `VK_ACCELERATION_STRUCTURE_BUILD_TYPE_HOST_KHR`. It requires the `accelerationStructureHostCommands` feature. A grounded investigation should check whether the host build respected the same geometry data and instance configuration as the device path, and whether the host-built structure was made available to the device trace (the host-built TLAS handle is bound via the descriptor set before the trace). If `gpu` passes but `cpu` fails, the cause is in the host build implementation. If both fail, the cause is shared infrastructure.

#### Maintenance5 flag2 creation path failure

**Possible failure symptoms:** A `misc` case fails where the corresponding `gpu` or `cpu` case with the same individual flag (without maintenance5) passes. The flood-fill similarity ratio falls below 0.95.

**Possible implementation causes:** The `misc` cases call `setCreateFlags2(translateCreateFlag(m_params.flags))` in addition to `setCreateFlags`. The `translateCreateFlag` function maps the legacy `VK_PIPELINE_CREATE_RAY_TRACING_NO_NULL_*_SHADERS_BIT_KHR` bits to the `VK_PIPELINE_CREATE_2_RAY_TRACING_NO_NULL_*_SHADERS_BIT_KHR` equivalents. A grounded investigation should check whether the flag translation is correct for the failing bit, whether the `VkPipelineCreateFlags2CreateInfo` extended struct is properly chained into the pipeline creation, and whether the implementation honors the flag2 path equivalently to the legacy path. Source-level inspection of `translateCreateFlag` is needed if only one flag bit fails.

#### Shared SBT and pipeline infrastructure failure

**Possible failure symptoms:** Both `gpu` and `cpu` fail for the same flag combination, geometry, stride, and lib, with the same flood-fill pattern.

**Possible implementation causes:** The shader set, SBT layout, pipeline construction, and flood-fill validation are identical across `gpu` and `cpu`. A failure common to both points at this shared setup. A grounded investigation should check whether the SBT hit-group indices computed from `stbRecOffset` and `stbRecStride` actually match the SBT records prepared by `prepareShaderBindingTable`, whether the shader record `retValue` fields are distinct per geometry, whether the pipeline library linking correctly assembles miss and hit-group libraries with the main rgen pipeline, and whether the ahit shader's `ignoreIntersectionEXT` on odd-indexed geometries produces the expected transparency behavior. For cases with `use_libs`, check that the library pipeline flags include `VK_PIPELINE_CREATE_LIBRARY_BIT_KHR` and that the main pipeline links them correctly.

## Case Pruning

### Requirement-based pruning

- All cases require `VK_KHR_ray_tracing_pipeline`, `VK_KHR_acceleration_structure`, and `VK_KHR_buffer_device_address`. If `rayTracingPipeline` or `accelerationStructure` feature bits are not set, the test throws `NotSupportedError` or `TestError` [checkSupport](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L578-L613).
- `cpu` cases also require `accelerationStructureHostCommands`; otherwise the test throws `NotSupportedError` [host build gate](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L615-L617).
- `use_libs` cases require `VK_KHR_pipeline_library` [pipeline library gate](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L598-L599).
- `misc` cases require `VK_KHR_maintenance5` [maintenance5 gate](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L601-L602).
- The vertex buffer format `VK_FORMAT_R32G32B32_SFLOAT` must be supported for acceleration structure vertex buffers [format check](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L619-L620).

### Design-based pruning

- The `NO_NULL_INTERSECTION` flag combined with `triangles` geometry is pruned at registration time, because intersection shaders are not used with triangle geometry. This removes 8 flag combinations (all subsets containing isect) from the triangles matrix, leaving 7 [isect-triangle skip](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L1601-L1603).
- The empty flag set (no NO_NULL flags) is not generated. The `NoNullShadersFlagGenerator::combine` function returns early when the input set is empty, so only non-empty subsets are registered. This is by design: the test exercises NO_NULL flag declarations, and a case with no flags would not test any declaration [combine function](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L1502-L1513).
- The `misc` group tests only individual flag bits, not combinations. This isolates the maintenance5 flag2 path from combination effects [misc loop](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L1634-L1638).

## Key Takeaways

- The `pipeline_no_null_shaders_flag` family tests ray tracing pipeline creation with all non-empty subsets of four `VK_PIPELINE_CREATE_RAY_TRACING_NO_NULL_*_SHADERS_BIT_KHR` flags, crossed with processor, geometry, SBT stride, SBT offset, and library mode. 300 cases are registered in mustpass.
- The flag combination controls which shaders are loaded into the pipeline: ahit is loaded only when `NO_NULL_ANY_HIT` is set; isect is loaded when `NO_NULL_INTERSECTION` is set or geometry includes boxes. Miss and chit are always loaded.
- The SBT uses nonzero stride (3 or 5) and offset (7) to exercise non-trivial hit-group indexing. The effective groups-per-instance count is `geomCount * stbRecStride + stbRecOffset + 1 = 14` for stride 3.
- The `misc` subgroup isolates the maintenance5 `setCreateFlags2` creation path with individual flag bits, testing the flag2 translation independently of the full combination matrix.
- The flood-fill similarity check tolerates implementation-specific rasterization differences while verifying that the overall hit/miss pattern matches the offline reference. A similarity ratio below 0.95 is a failure.
- See `## Failure Meaning` for the per-processor cause analysis. A failure isolated to one processor points at that path's AS build or pipeline creation; a failure common to `gpu` and `cpu` points at shared SBT or pipeline infrastructure.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `TestParams` struct | [vktRayTracingPipelineFlagsTests.cpp#L80-L111](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L80-L111) | Per-case parameters including flags, geometry, stride, offset, lib mode |
| `PipelineFlagsCase::checkSupport` | [vktRayTracingPipelineFlagsTests.cpp#L578-L625](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L578-L625) | Feature gates for ray tracing, acceleration structure, pipeline library, maintenance5, host commands |
| `PipelineFlagsCase::initPrograms` | [vktRayTracingPipelineFlagsTests.cpp#L627-L733](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L627-L733) | Shader generation for rgen, miss, chit, ahit, isect |
| `RayTracingTestPipeline::createPipeline` | [vktRayTracingPipelineFlagsTests.cpp#L434-L472](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L434-L472) | Pipeline construction with library mode and flag setup |
| `createBottomLevelAccelerationStructs` | [vktRayTracingPipelineFlagsTests.cpp#L842-L902](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L842-L902) | BLAS creation for triangle and box geometry |
| `createTopLevelAccelerationStruct` | [vktRayTracingPipelineFlagsTests.cpp#L904-L929](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L904-L929) | TLAS instance setup with SBT record offsets |
| `prepareShaderBindingTable` | [vktRayTracingPipelineFlagsTests.cpp#L931-L1026](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L931-L1026) | SBT record layout with geomType, geomIndex, retValue per hit group |
| `travelRay` | [vktRayTracingPipelineFlagsTests.cpp#L1097-L1189](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L1097-L1189) | Offline ray trace for reference image |
| `verifyResult` | [vktRayTracingPipelineFlagsTests.cpp#L1203-L1320](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L1203-L1320) | Flood-fill similarity check and pass/fail condition |
| `PipelineFlagsInstance::iterate` | [vktRayTracingPipelineFlagsTests.cpp#L1322-L1448](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L1322-L1448) | Runtime execution: trace, copyback, validation |
| `NoNullShadersFlagGenerator` | [vktRayTracingPipelineFlagsTests.cpp#L1450-L1524](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L1450-L1524) | Generates all non-empty subsets of the four NO_NULL flag bits |
| `createPipelineFlagsTests` | [vktRayTracingPipelineFlagsTests.cpp#L1528-L1643](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineFlagsTests.cpp#L1528-L1643) | Registration of gpu, cpu, and misc children with the full matrix |
