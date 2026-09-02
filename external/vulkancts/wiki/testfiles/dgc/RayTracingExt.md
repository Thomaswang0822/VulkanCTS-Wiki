## Overview

**Core question:** Does EXT device-generated command execution preserve ray-tracing shader selection, launch coordinates, and shader-visible results?

- This page covers `dgc.ext.ray_tracing`, implemented by [RayTracingCase::initPrograms](../../../modules/vulkan/device_generated_commands/vktDGCRayTracingTestsExt.cpp#L419-L845) and [RayTracingInstance::iterate](../../../modules/vulkan/device_generated_commands/vktDGCRayTracingTestsExt.cpp#L852-L1988).
- The sixteen registered leaves combine execution-set use, explicit preprocessing, unordered sequences, and compute-queue submission.
- Each case emits two `16 x 8 x 1` trace-ray commands and checks a `16 x 16` result grid. The shaders record payloads, ray built-ins, hit attributes, transforms, launch values, and shader-record-buffer data.

## Background Knowledge

- A device-generated command layout describes tokens that the implementation reads from a generated stream. This test uses an optional execution-set token, a push-constant token, and a trace-rays token. Explicit preprocessing separates command generation from execution; unordered sequences remove stream order as a source of meaning.
- A ray-tracing pipeline connects ray generation with miss, intersection, closest-hit, and callable stages. A ray payload carries data across those calls, while a shader binding table selects records and can provide `shaderRecordEXT` data.
- A bottom-level acceleration structure stores geometry. A top-level acceleration structure stores transformed instances of those bottom-level structures, so the traversal built-ins can expose both instance and object-space information.

## Registration Hierarchy

```text
dgc.ext.ray_tracing
├── no_execution_set
├── no_execution_set_cq
├── no_execution_set_preprocess
├── no_execution_set_preprocess_cq
├── no_execution_set_preprocess_unordered
├── no_execution_set_preprocess_unordered_cq
├── no_execution_set_unordered
├── no_execution_set_unordered_cq
├── with_execution_set
├── with_execution_set_cq
├── with_execution_set_preprocess
├── with_execution_set_preprocess_cq
├── with_execution_set_preprocess_unordered
├── with_execution_set_preprocess_unordered_cq
├── with_execution_set_unordered
└── with_execution_set_unordered_cq
```

The leaves come from the nested Boolean loops in [createDGCRayTracingTestsExt](../../../modules/vulkan/device_generated_commands/vktDGCRayTracingTestsExt.cpp#L1993-L2010) and appear in [dgc.txt](../../../mustpass/main/vk-default/dgc.txt#L4334-L4349).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Execution set | `no_execution_set`, `with_execution_set` | Uses one fixed pipeline, or selects two compatible ray-tracing pipelines from an indirect execution set. | [pipeline and execution-set setup](../../../modules/vulkan/device_generated_commands/vktDGCRayTracingTestsExt.cpp#L1136-L1242) |
| Preprocessing | absent, `preprocess` | Executes the generated stream directly, or preprocesses it before execution. | [preprocess and execution](../../../modules/vulkan/device_generated_commands/vktDGCRayTracingTestsExt.cpp#L1373-L1393) |
| Sequence order | absent, `unordered` | Uses ordinary sequence order, or allows unordered sequence execution while carrying each sequence's own data. | [layout flags](../../../modules/vulkan/device_generated_commands/vktDGCRayTracingTestsExt.cpp#L1092-L1104) |
| Queue | graphics-capable context queue, `cq` | Submits on the context queue, or selects a compute queue. | [queue selection and support](../../../modules/vulkan/device_generated_commands/vktDGCRayTracingTestsExt.cpp#L990-L997), [checkSupport](../../../modules/vulkan/device_generated_commands/vktDGCRayTracingTestsExt.cpp#L382-L393) |
| Geometry | triangles, AABBs | Exercises triangle culling and custom intersection traversal. | [BLAS construction](../../../modules/vulkan/device_generated_commands/vktDGCRayTracingTestsExt.cpp#L256-L316) |
| Shader-record form | first eight rows without SRB, second eight rows with SRB | Selects SBT records without or with `layout(shaderRecordEXT, std430)` data. | [SBT and shader sets](../../../modules/vulkan/device_generated_commands/vktDGCRayTracingTestsExt.cpp#L1136-L1226) |

## Behavior Parameters

The primary behavioral axis is the registered leaf. Its four Boolean dimensions change how the same two trace-ray sequences are generated and executed.

### `no_execution_set` and suffixes: fixed pipeline

The command stream contains push constants and trace-ray data, and the initially bound pipeline performs the work. Suffixes add preprocessing, unordered sequences, compute-queue submission, or both.

### `with_execution_set` and suffixes: indirect pipeline selection

The stream starts each sequence with a pipeline index. The first sequence selects pipeline 0 and the second selects pipeline 1; each pipeline receives the shader set associated with its sequence. The suffixes combine that selection with the other execution modes.

### `_preprocess`: separate preparation

The host records `vkCmdPreprocessGeneratedCommandsEXT`, inserts `preprocessToExecuteBarrierExt`, and executes with `isPreprocessed = VK_TRUE`. Without the suffix, execution consumes the stream without that preceding preprocess command.

### `_unordered`: per-sequence coordinates

The layout sets `VK_INDIRECT_COMMANDS_LAYOUT_USAGE_UNORDERED_SEQUENCES_BIT_EXT`. Each sequence carries `offsetY`, SBT addresses, and trace dimensions. The shader computes its result index from `gl_LaunchIDEXT` and `offsetY`, so sequence order does not define the destination cell.

### `_cq`: compute-queue submission

The case requests a compute queue before command-pool creation. The queue must exist; an unavailable queue is handled by support checking rather than by the result comparison.

## Shader Analysis

The generator emits raygen, miss, closest-hit, intersection, and two callable stages. Each stage has a pair of SBT variants: one without SRB data and one with `layout(shaderRecordEXT, std430)`. The following walkthrough uses the first registered leaf and the raygen stage because it connects the generated command parameters to every later shader stage.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.dgc.ext.ray_tracing.no_execution_set
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `no_execution_set` | The stream does not carry an execution-set token; the initially bound ray-tracing pipeline executes both sequences. |
| First sequence, `offsetY = 0`, `16 x 8 x 1` | The raygen invocation covers rows 0 through 7 and maps its local launch ID into the full output grid. |
| `rgen` SBT variant | The selected raygen record has no shader-record-buffer declaration, while the second sequence uses the SRB-enabled set. |

#### Purpose

Raygen converts one generated trace-ray record into a ray launch and initializes the payload. It writes launch metadata before traversal and writes the payload again after miss or hit processing returns.

#### Structural Design

| Phase | Shader operation | Observable result |
|-------|------------------|-------------------|
| Index | Add `pc.offsetY` to `gl_LaunchIDEXT.y`; flatten with `gl_LaunchSizeEXT.x`. | Selects one of 256 output cells. |
| Inputs | Read ray flags, origin, direction, limits, and miss index from `ib.params[cellIdx]`. | Replays host-generated per-cell traversal parameters. |
| Payload | Set `payload` to `vec4(gl_LaunchIDEXT.xyz, 0.0)`, trace the ray, then store it again. | Exposes propagation through miss, closest-hit, and callable stages. |

#### Shader Code

```glsl
#version 460 core
#extension GL_EXT_debug_printf : enable
#extension GL_EXT_ray_tracing : require
layout (location=0) rayPayloadEXT vec4 payload;

/// Binding 0 holds the TLAS. Bindings 1 and 2 hold the host-filled cell inputs and shader outputs.
layout (set=0, binding=0) uniform accelerationStructureEXT topLevelAS;
layout (set=0, binding=1, std430) readonly buffer InputBlock { CellParams params[256]; } ib;
layout (set=0, binding=2, std430) buffer OutputBlock { CellOutput values[256]; } ob;
/// The DGC push-constant token supplies the row offset for this 16 x 8 sequence.
layout (push_constant, std430) uniform PCBlock { uint offsetY; } pc;

uint getCellIndex(bool print) {
    const uint row = gl_LaunchIDEXT.y + pc.offsetY;
    const uint cellIndex = row * gl_LaunchSizeEXT.x + gl_LaunchIDEXT.x;
    return cellIndex;
}

void main()
{
    const uint cellIdx = getCellIndex(false);
    ob.values[cellIdx].rgenLaunchIDEXT = uvec4(gl_LaunchIDEXT.xyz, 0u);
    ob.values[cellIdx].rgenLaunchSizeEXT = uvec4(gl_LaunchSizeEXT.xyz, 0u);

    const uint  rayFlags  = ib.params[cellIdx].rayFlags;
    const vec3  origin    = ib.params[cellIdx].origin.xyz;
    const vec3  direction = vec3(0, 0, ib.params[cellIdx].zDirection);
    const float tMin      = ib.params[cellIdx].minT;
    const float tMax      = ib.params[cellIdx].maxT;
    const uint  missIndex = ib.params[cellIdx].missIndex;
    const uint  cullMask  = 0xFF;
    const uint  sbtOffset = 0u;
    const uint  sbtStride = 1u;

    const vec4 payloadValue = vec4(gl_LaunchIDEXT.xyz, 0.0);
    payload = payloadValue;
    ob.values[cellIdx].rgenInitialPayload = payload;
    traceRayEXT(topLevelAS, rayFlags, cullMask, sbtOffset, sbtStride, missIndex,
                origin, tMin, direction, tMax, 0);
    ob.values[cellIdx].rgenFinalPayload = payload;
}
```

#### Additional Info

- The source generator emits `CellParams`, `CellOutput`, descriptor declarations, and `getCellIndex` before the stage-specific body; the walkthrough abbreviates those generated struct declarations to keep the control flow readable. See [shared declarations](../../../modules/vulkan/device_generated_commands/vktDGCRayTracingTestsExt.cpp#L423-L569).
- The explicit build options request SPIR-V 1.4 for every generated shader. The source uses GLSL 4.60 and `GL_EXT_ray_tracing`. See [build options and raygen generation](../../../modules/vulkan/device_generated_commands/vktDGCRayTracingTestsExt.cpp#L419-L608).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Execution set | Changes the DGC stream by adding an execution-set token; raygen source remains the same. | [layout token](../../../modules/vulkan/device_generated_commands/vktDGCRayTracingTestsExt.cpp#L1098-L1103) |
| Preprocessing | Does not change raygen source; it changes whether generated state is prepared before execution. | [preprocess branch](../../../modules/vulkan/device_generated_commands/vktDGCRayTracingTestsExt.cpp#L1384-L1392) |
| Sequence order | Does not change raygen source; `offsetY` keeps the cell mapping independent of processing order. | [cell-index generator](../../../modules/vulkan/device_generated_commands/vktDGCRayTracingTestsExt.cpp#L547-L560) |
| SRB selection | Adds `shaderRecordEXT` and records `srb.data` in the SRB-enabled raygen variant. | [raygen SRB branch](../../../modules/vulkan/device_generated_commands/vktDGCRayTracingTestsExt.cpp#L572-L608) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed GLSL from this walkthrough
- Stage: rgen
- Target SPIRV version: spirv1.4

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.4
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 172
; Schema: 0
               OpCapability RayTracingKHR
               OpExtension "SPV_KHR_non_semantic_info"
               OpExtension "SPV_KHR_ray_tracing"
          %1 = OpExtInstImport "GLSL.std.450"
         %57 = OpExtInstImport "NonSemantic.DebugPrintf"
               OpMemoryModel Logical GLSL450
               OpEntryPoint RayGenerationKHR %main "main" %gl_LaunchIDEXT %pc %gl_LaunchSizeEXT %ob %ib %payload %topLevelAS
         %44 = OpString "pc.offsetY=%u gl_LaunchIDEXT.x=%u gl_LaunchIDEXT.y=%u gl_LaunchSizeEXT.x=%u gl_LaunchSizeEXT.y=%u row=%u cellIndex=%u
"
               OpSource GLSL 460
               OpSourceExtension "GL_EXT_debug_printf"
               OpSourceExtension "GL_EXT_ray_tracing"
               OpName %main "main"
               OpName %getCellIndex_b1_ "getCellIndex(b1;"
               OpName %print "print"
               OpName %row "row"
               OpName %gl_LaunchIDEXT "gl_LaunchIDEXT"
               OpName %PCBlock "PCBlock"
               OpMemberName %PCBlock 0 "offsetY"
               OpName %pc "pc"
               OpName %cellIndex "cellIndex"
               OpName %gl_LaunchSizeEXT "gl_LaunchSizeEXT"
               OpName %cellIdx "cellIdx"
               OpName %param "param"
               OpName %CellOutput "CellOutput"
               OpMemberName %CellOutput 0 "rgenInitialPayload"
               OpMemberName %CellOutput 1 "rgenFinalPayload"
               OpMemberName %CellOutput 2 "chitPayload"
               OpMemberName %CellOutput 3 "missPayload"
               OpMemberName %CellOutput 4 "chitIncomingPayload"
               OpMemberName %CellOutput 5 "missIncomingPayload"
               OpMemberName %CellOutput 6 "isecAttribute"
               OpMemberName %CellOutput 7 "chitAttribute"
               OpMemberName %CellOutput 8 "rgenSRB"
               OpMemberName %CellOutput 9 "isecSRB"
               OpMemberName %CellOutput 10 "chitSRB"
               OpMemberName %CellOutput 11 "missSRB"
               OpMemberName %CellOutput 12 "call0SRB"
               OpMemberName %CellOutput 13 "call1SRB"
               OpMemberName %CellOutput 14 "rgenLaunchIDEXT"
               OpMemberName %CellOutput 15 "rgenLaunchSizeEXT"
               OpMemberName %CellOutput 16 "chitLaunchIDEXT"
               OpMemberName %CellOutput 17 "chitLaunchSizeEXT"
               OpMemberName %CellOutput 18 "chitPrimitiveID"
               OpMemberName %CellOutput 19 "chitInstanceID"
               OpMemberName %CellOutput 20 "chitInstanceCustomIndexEXT"
               OpMemberName %CellOutput 21 "chitGeometryIndexEXT"
               OpMemberName %CellOutput 22 "chitWorldRayOriginEXT"
               OpMemberName %CellOutput 23 "chitWorldRayDirectionEXT"
               OpMemberName %CellOutput 24 "chitObjectRayOriginEXT"
               OpMemberName %CellOutput 25 "chitObjectRayDirectionEXT"
               OpMemberName %CellOutput 26 "chitRayTminEXT"
               OpMemberName %CellOutput 27 "chitRayTmaxEXT"
               OpMemberName %CellOutput 28 "chitIncomingRayFlagsEXT"
               OpMemberName %CellOutput 29 "chitHitTEXT"
               OpMemberName %CellOutput 30 "chitHitKindEXT"
               OpMemberName %CellOutput 31 "chitObjectToWorldEXT"
               OpMemberName %CellOutput 32 "chitObjectToWorld3x4EXT"
               OpMemberName %CellOutput 33 "chitWorldToObjectEXT"
               OpMemberName %CellOutput 34 "chitWorldToObject3x4EXT"
               OpMemberName %CellOutput 35 "isecLaunchIDEXT"
               OpMemberName %CellOutput 36 "isecLaunchSizeEXT"
               OpMemberName %CellOutput 37 "isecPrimitiveID"
               OpMemberName %CellOutput 38 "isecInstanceID"
               OpMemberName %CellOutput 39 "isecInstanceCustomIndexEXT"
               OpMemberName %CellOutput 40 "isecGeometryIndexEXT"
               OpMemberName %CellOutput 41 "isecWorldRayOriginEXT"
               OpMemberName %CellOutput 42 "isecWorldRayDirectionEXT"
               OpMemberName %CellOutput 43 "isecObjectRayOriginEXT"
               OpMemberName %CellOutput 44 "isecObjectRayDirectionEXT"
               OpMemberName %CellOutput 45 "isecRayTminEXT"
               OpMemberName %CellOutput 46 "isecRayTmaxEXT"
               OpMemberName %CellOutput 47 "isecIncomingRayFlagsEXT"
               OpMemberName %CellOutput 48 "missLaunchIDEXT"
               OpMemberName %CellOutput 49 "missLaunchSizeEXT"
               OpMemberName %CellOutput 50 "missWorldRayOriginEXT"
               OpMemberName %CellOutput 51 "missWorldRayDirectionEXT"
               OpMemberName %CellOutput 52 "missRayTminEXT"
               OpMemberName %CellOutput 53 "missRayTmaxEXT"
               OpMemberName %CellOutput 54 "missIncomingRayFlagsEXT"
               OpMemberName %CellOutput 55 "callLaunchIDEXT"
               OpMemberName %CellOutput 56 "callLaunchSizeEXT"
               OpName %OutputBlock "OutputBlock"
               OpMemberName %OutputBlock 0 "values"
               OpName %ob "ob"
               OpName %rayFlags "rayFlags"
               OpName %CellParams "CellParams"
               OpMemberName %CellParams 0 "origin"
               OpMemberName %CellParams 1 "transformMatrix"
               OpMemberName %CellParams 2 "closestPrimitive"
               OpMemberName %CellParams 3 "zDirection"
               OpMemberName %CellParams 4 "minT"
               OpMemberName %CellParams 5 "maxT"
               OpMemberName %CellParams 6 "blasIndex"
               OpMemberName %CellParams 7 "instanceCustomIndex"
               OpMemberName %CellParams 8 "opaque"
               OpMemberName %CellParams 9 "rayFlags"
               OpMemberName %CellParams 10 "missIndex"
               OpName %InputBlock "InputBlock"
               OpMemberName %InputBlock 0 "params"
               OpName %ib "ib"
               OpName %origin "origin"
               OpName %direction "direction"
               OpName %tMin "tMin"
               OpName %tMax "tMax"
               OpName %missIndex "missIndex"
               OpName %payloadValue "payloadValue"
               OpName %payload "payload"
               OpName %topLevelAS "topLevelAS"
               OpDecorate %gl_LaunchIDEXT BuiltIn LaunchIdKHR
               OpDecorate %PCBlock Block
               OpMemberDecorate %PCBlock 0 Offset 0
               OpDecorate %gl_LaunchSizeEXT BuiltIn LaunchSizeKHR
               OpDecorate %_arr_v4float_uint_3 ArrayStride 16
               OpDecorate %_arr_v4float_uint_4 ArrayStride 16
               OpDecorate %_arr_v4float_uint_3_0 ArrayStride 16
               OpDecorate %_arr_v4float_uint_4_0 ArrayStride 16
               OpMemberDecorate %CellOutput 0 Offset 0
               OpMemberDecorate %CellOutput 1 Offset 16
               OpMemberDecorate %CellOutput 2 Offset 32
               OpMemberDecorate %CellOutput 3 Offset 48
               OpMemberDecorate %CellOutput 4 Offset 64
               OpMemberDecorate %CellOutput 5 Offset 80
               OpMemberDecorate %CellOutput 6 Offset 96
               OpMemberDecorate %CellOutput 7 Offset 112
               OpMemberDecorate %CellOutput 8 Offset 128
               OpMemberDecorate %CellOutput 9 Offset 144
               OpMemberDecorate %CellOutput 10 Offset 160
               OpMemberDecorate %CellOutput 11 Offset 176
               OpMemberDecorate %CellOutput 12 Offset 192
               OpMemberDecorate %CellOutput 13 Offset 208
               OpMemberDecorate %CellOutput 14 Offset 224
               OpMemberDecorate %CellOutput 15 Offset 240
               OpMemberDecorate %CellOutput 16 Offset 256
               OpMemberDecorate %CellOutput 17 Offset 272
               OpMemberDecorate %CellOutput 18 Offset 288
               OpMemberDecorate %CellOutput 19 Offset 292
               OpMemberDecorate %CellOutput 20 Offset 296
               OpMemberDecorate %CellOutput 21 Offset 300
               OpMemberDecorate %CellOutput 22 Offset 304
               OpMemberDecorate %CellOutput 23 Offset 320
               OpMemberDecorate %CellOutput 24 Offset 336
               OpMemberDecorate %CellOutput 25 Offset 352
               OpMemberDecorate %CellOutput 26 Offset 368
               OpMemberDecorate %CellOutput 27 Offset 372
               OpMemberDecorate %CellOutput 28 Offset 376
               OpMemberDecorate %CellOutput 29 Offset 380
               OpMemberDecorate %CellOutput 30 Offset 384
               OpMemberDecorate %CellOutput 31 Offset 400
               OpMemberDecorate %CellOutput 32 Offset 448
               OpMemberDecorate %CellOutput 33 Offset 512
               OpMemberDecorate %CellOutput 34 Offset 560
               OpMemberDecorate %CellOutput 35 Offset 624
               OpMemberDecorate %CellOutput 36 Offset 640
               OpMemberDecorate %CellOutput 37 Offset 656
               OpMemberDecorate %CellOutput 38 Offset 660
               OpMemberDecorate %CellOutput 39 Offset 664
               OpMemberDecorate %CellOutput 40 Offset 668
               OpMemberDecorate %CellOutput 41 Offset 672
               OpMemberDecorate %CellOutput 42 Offset 688
               OpMemberDecorate %CellOutput 43 Offset 704
               OpMemberDecorate %CellOutput 44 Offset 720
               OpMemberDecorate %CellOutput 45 Offset 736
               OpMemberDecorate %CellOutput 46 Offset 740
               OpMemberDecorate %CellOutput 47 Offset 744
               OpMemberDecorate %CellOutput 48 Offset 752
               OpMemberDecorate %CellOutput 49 Offset 768
               OpMemberDecorate %CellOutput 50 Offset 784
               OpMemberDecorate %CellOutput 51 Offset 800
               OpMemberDecorate %CellOutput 52 Offset 816
               OpMemberDecorate %CellOutput 53 Offset 820
               OpMemberDecorate %CellOutput 54 Offset 824
               OpMemberDecorate %CellOutput 55 Offset 832
               OpMemberDecorate %CellOutput 56 Offset 848
               OpDecorate %_arr_CellOutput_uint_256 ArrayStride 864
               OpDecorate %OutputBlock Block
               OpMemberDecorate %OutputBlock 0 Offset 0
               OpDecorate %ob Binding 2
               OpDecorate %ob DescriptorSet 0
               OpDecorate %_arr_float_uint_12 ArrayStride 4
               OpMemberDecorate %CellParams 0 Offset 0
               OpMemberDecorate %CellParams 1 Offset 16
               OpMemberDecorate %CellParams 2 Offset 64
               OpMemberDecorate %CellParams 3 Offset 68
               OpMemberDecorate %CellParams 4 Offset 72
               OpMemberDecorate %CellParams 5 Offset 76
               OpMemberDecorate %CellParams 6 Offset 80
               OpMemberDecorate %CellParams 7 Offset 84
               OpMemberDecorate %CellParams 8 Offset 88
               OpMemberDecorate %CellParams 9 Offset 92
               OpMemberDecorate %CellParams 10 Offset 96
               OpDecorate %_arr_CellParams_uint_256 ArrayStride 112
               OpDecorate %InputBlock Block
               OpMemberDecorate %InputBlock 0 NonWritable
               OpMemberDecorate %InputBlock 0 Offset 0
               OpDecorate %ib NonWritable
               OpDecorate %ib Binding 1
               OpDecorate %ib DescriptorSet 0
               OpDecorate %topLevelAS Binding 0
               OpDecorate %topLevelAS DescriptorSet 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %bool = OpTypeBool
%_ptr_Function_bool = OpTypePointer Function %bool
       %uint = OpTypeInt 32 0
          %9 = OpTypeFunction %uint %_ptr_Function_bool
%_ptr_Function_uint = OpTypePointer Function %uint
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_LaunchIDEXT = OpVariable %_ptr_Input_v3uint Input
     %uint_1 = OpConstant %uint 1
%_ptr_Input_uint = OpTypePointer Input %uint
    %PCBlock = OpTypeStruct %uint
%_ptr_PushConstant_PCBlock = OpTypePointer PushConstant %PCBlock
         %pc = OpVariable %_ptr_PushConstant_PCBlock PushConstant
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_PushConstant_uint = OpTypePointer PushConstant %uint
%gl_LaunchSizeEXT = OpVariable %_ptr_Input_v3uint Input
     %uint_0 = OpConstant %uint 0
      %false = OpConstantFalse %bool
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
     %v4uint = OpTypeVector %uint 4
     %uint_3 = OpConstant %uint 3
%_arr_v4float_uint_3 = OpTypeArray %v4float %uint_3
     %uint_4 = OpConstant %uint 4
%_arr_v4float_uint_4 = OpTypeArray %v4float %uint_4
%_arr_v4float_uint_3_0 = OpTypeArray %v4float %uint_3
%_arr_v4float_uint_4_0 = OpTypeArray %v4float %uint_4
 %CellOutput = OpTypeStruct %v4float %v4float %v4float %v4float %v4float %v4float %v4float %v4float %v4float %v4float %v4float %v4float %v4float %v4float %v4uint %v4uint %v4uint %v4uint %int %int %int %int %v4float %v4float %v4float %v4float %float %float %uint %float %uint %_arr_v4float_uint_3 %_arr_v4float_uint_4 %_arr_v4float_uint_3_0 %_arr_v4float_uint_4_0 %v4uint %v4uint %int %int %int %int %v4float %v4float %v4float %v4float %float %float %uint %v4uint %v4uint %v4float %v4float %float %float %uint %v4uint %v4uint
   %uint_256 = OpConstant %uint 256
%_arr_CellOutput_uint_256 = OpTypeArray %CellOutput %uint_256
%OutputBlock = OpTypeStruct %_arr_CellOutput_uint_256
%_ptr_StorageBuffer_OutputBlock = OpTypePointer StorageBuffer %OutputBlock
         %ob = OpVariable %_ptr_StorageBuffer_OutputBlock StorageBuffer
     %int_14 = OpConstant %int 14
%_ptr_StorageBuffer_v4uint = OpTypePointer StorageBuffer %v4uint
     %int_15 = OpConstant %int 15
    %uint_12 = OpConstant %uint 12
%_arr_float_uint_12 = OpTypeArray %float %uint_12
 %CellParams = OpTypeStruct %v4float %_arr_float_uint_12 %uint %float %float %float %uint %uint %uint %uint %uint
%_arr_CellParams_uint_256 = OpTypeArray %CellParams %uint_256
 %InputBlock = OpTypeStruct %_arr_CellParams_uint_256
%_ptr_StorageBuffer_InputBlock = OpTypePointer StorageBuffer %InputBlock
         %ib = OpVariable %_ptr_StorageBuffer_InputBlock StorageBuffer
      %int_9 = OpConstant %int 9
%_ptr_StorageBuffer_uint = OpTypePointer StorageBuffer %uint
    %v3float = OpTypeVector %float 3
%_ptr_Function_v3float = OpTypePointer Function %v3float
%_ptr_StorageBuffer_v4float = OpTypePointer StorageBuffer %v4float
    %float_0 = OpConstant %float 0
      %int_3 = OpConstant %int 3
%_ptr_StorageBuffer_float = OpTypePointer StorageBuffer %float
%_ptr_Function_float = OpTypePointer Function %float
      %int_4 = OpConstant %int 4
      %int_5 = OpConstant %int 5
     %int_10 = OpConstant %int 10
%_ptr_Function_v4float = OpTypePointer Function %v4float
%_ptr_RayPayloadKHR_v4float = OpTypePointer RayPayloadKHR %v4float
    %payload = OpVariable %_ptr_RayPayloadKHR_v4float RayPayloadKHR
        %157 = OpTypeAccelerationStructureKHR
%_ptr_UniformConstant_157 = OpTypePointer UniformConstant %157
 %topLevelAS = OpVariable %_ptr_UniformConstant_157 UniformConstant
   %uint_255 = OpConstant %uint 255
      %int_1 = OpConstant %int 1
       %main = OpFunction %void None %3
          %5 = OpLabel
    %cellIdx = OpVariable %_ptr_Function_uint Function
      %param = OpVariable %_ptr_Function_bool Function
   %rayFlags = OpVariable %_ptr_Function_uint Function
     %origin = OpVariable %_ptr_Function_v3float Function
  %direction = OpVariable %_ptr_Function_v3float Function
       %tMin = OpVariable %_ptr_Function_float Function
       %tMax = OpVariable %_ptr_Function_float Function
  %missIndex = OpVariable %_ptr_Function_uint Function
%payloadValue = OpVariable %_ptr_Function_v4float Function
               OpStore %param %false
         %65 = OpFunctionCall %uint %getCellIndex_b1_ %param
               OpStore %cellIdx %65
         %81 = OpLoad %uint %cellIdx
         %83 = OpLoad %v3uint %gl_LaunchIDEXT
         %84 = OpCompositeExtract %uint %83 0
         %85 = OpCompositeExtract %uint %83 1
         %86 = OpCompositeExtract %uint %83 2
         %87 = OpCompositeConstruct %v4uint %84 %85 %86 %uint_0
         %89 = OpAccessChain %_ptr_StorageBuffer_v4uint %ob %int_0 %81 %int_14
               OpStore %89 %87
         %90 = OpLoad %uint %cellIdx
         %92 = OpLoad %v3uint %gl_LaunchSizeEXT
         %93 = OpCompositeExtract %uint %92 0
         %94 = OpCompositeExtract %uint %92 1
         %95 = OpCompositeExtract %uint %92 2
         %96 = OpCompositeConstruct %v4uint %93 %94 %95 %uint_0
         %97 = OpAccessChain %_ptr_StorageBuffer_v4uint %ob %int_0 %90 %int_15
               OpStore %97 %96
        %106 = OpLoad %uint %cellIdx
        %109 = OpAccessChain %_ptr_StorageBuffer_uint %ib %int_0 %106 %int_9
        %110 = OpLoad %uint %109
               OpStore %rayFlags %110
        %114 = OpLoad %uint %cellIdx
        %116 = OpAccessChain %_ptr_StorageBuffer_v4float %ib %int_0 %114 %int_0
        %117 = OpLoad %v4float %116
        %118 = OpVectorShuffle %v3float %117 %117 0 1 2
               OpStore %origin %118
        %121 = OpLoad %uint %cellIdx
        %124 = OpAccessChain %_ptr_StorageBuffer_float %ib %int_0 %121 %int_3
        %125 = OpLoad %float %124
        %126 = OpCompositeConstruct %v3float %float_0 %float_0 %125
               OpStore %direction %126
        %129 = OpLoad %uint %cellIdx
        %131 = OpAccessChain %_ptr_StorageBuffer_float %ib %int_0 %129 %int_4
        %132 = OpLoad %float %131
               OpStore %tMin %132
        %134 = OpLoad %uint %cellIdx
        %136 = OpAccessChain %_ptr_StorageBuffer_float %ib %int_0 %134 %int_5
        %137 = OpLoad %float %136
               OpStore %tMax %137
        %139 = OpLoad %uint %cellIdx
        %141 = OpAccessChain %_ptr_StorageBuffer_uint %ib %int_0 %139 %int_10
        %142 = OpLoad %uint %141
               OpStore %missIndex %142
        %145 = OpLoad %v3uint %gl_LaunchIDEXT
        %146 = OpConvertUToF %v3float %145
        %147 = OpCompositeExtract %float %146 0
        %148 = OpCompositeExtract %float %146 1
        %149 = OpCompositeExtract %float %146 2
        %150 = OpCompositeConstruct %v4float %147 %148 %149 %float_0
               OpStore %payloadValue %150
        %153 = OpLoad %v4float %payloadValue
               OpStore %payload %153
        %154 = OpLoad %uint %cellIdx
        %155 = OpLoad %v4float %payload
        %156 = OpAccessChain %_ptr_StorageBuffer_v4float %ob %int_0 %154 %int_0
               OpStore %156 %155
        %160 = OpLoad %157 %topLevelAS
        %161 = OpLoad %uint %rayFlags
        %163 = OpLoad %uint %missIndex
        %164 = OpLoad %v3float %origin
        %165 = OpLoad %float %tMin
        %166 = OpLoad %v3float %direction
        %167 = OpLoad %float %tMax
               OpTraceRayKHR %160 %161 %uint_255 %uint_0 %uint_1 %163 %164 %165 %166 %167 %payload
        %168 = OpLoad %uint %cellIdx
        %170 = OpLoad %v4float %payload
        %171 = OpAccessChain %_ptr_StorageBuffer_v4float %ob %int_0 %168 %int_1
               OpStore %171 %170
               OpReturn
               OpFunctionEnd
%getCellIndex_b1_ = OpFunction %uint None %9
      %print = OpFunctionParameter %_ptr_Function_bool
         %12 = OpLabel
        %row = OpVariable %_ptr_Function_uint Function
  %cellIndex = OpVariable %_ptr_Function_uint Function
         %20 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_1
         %21 = OpLoad %uint %20
         %28 = OpAccessChain %_ptr_PushConstant_uint %pc %int_0
         %29 = OpLoad %uint %28
         %30 = OpIAdd %uint %21 %29
               OpStore %row %30
         %32 = OpLoad %uint %row
         %35 = OpAccessChain %_ptr_Input_uint %gl_LaunchSizeEXT %uint_0
         %36 = OpLoad %uint %35
         %37 = OpIMul %uint %32 %36
         %38 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_0
         %39 = OpLoad %uint %38
         %40 = OpIAdd %uint %37 %39
               OpStore %cellIndex %40
         %41 = OpLoad %bool %print
               OpSelectionMerge %43 None
               OpBranchConditional %41 %42 %43
         %42 = OpLabel
         %45 = OpAccessChain %_ptr_PushConstant_uint %pc %int_0
         %46 = OpLoad %uint %45
         %47 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_0
         %48 = OpLoad %uint %47
         %49 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_1
         %50 = OpLoad %uint %49
         %51 = OpAccessChain %_ptr_Input_uint %gl_LaunchSizeEXT %uint_0
         %52 = OpLoad %uint %51
         %53 = OpAccessChain %_ptr_Input_uint %gl_LaunchSizeEXT %uint_1
         %54 = OpLoad %uint %53
         %55 = OpLoad %uint %row
         %56 = OpLoad %uint %cellIndex
         %58 = OpExtInst %void %57 1 %44 %46 %48 %50 %52 %54 %55 %56
               OpBranch %43
         %43 = OpLabel
         %59 = OpLoad %uint %cellIndex
               OpReturnValue %59
               OpFunctionEnd

```

</details>

## Runtime Execution and Result Checking

- The host creates 16 BLAS objects, each with four triangles or four AABBs. It places the selected geometry near `+10` in Z and the other geometry behind the ray origin, then creates 256 translated TLAS instances.
- It fills host-visible input and output buffers. Descriptor bindings 0, 1, and 2 hold the TLAS, `CellParams[256]`, and `CellOutput[256]`.
- It builds two SBT sets. The first dispatch uses `offsetY = 0`; the second uses `offsetY = 8`. Both use width 16, height 8, and depth 1.
- For execution-set cases, the DGC stream starts each record with index 0 or 1. Every record then contains the push constant and a `VkTraceRaysIndirectCommand2KHR` structure with four SBT regions and the dispatch dimensions.
- After execution, the host invalidates the output allocation and compares all 256 cells. It predicts culling, miss or hit traversal, payload offsets, hit attributes, built-ins, transforms, and SRB values. Integer and vector fields use exact comparisons; floating-point fields use a `1.0f / 256.0f` threshold.
- A mismatch logs the field and cell coordinate and returns `tcu::TestStatus::fail("Fail; check log for details")`. A complete match returns `tcu::TestStatus::pass("Pass")`. See [verification loop](../../../modules/vulkan/device_generated_commands/vktDGCRayTracingTestsExt.cpp#L1410-L1988).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `no_execution_set` and suffixes | Fixed-pipeline DGC binding, trace-ray decoding, SBT selection, synchronization, queue execution, or ray-tracing result mismatch. |
| `with_execution_set` and suffixes | Execution-set pipeline selection or compatibility, plus the same DGC and ray-tracing result mechanisms. |
| `_preprocess` combinations | Preprocessed generated state or the preprocess-to-execute dependency differs from direct execution. |
| `_unordered` combinations | Per-sequence data, launch-coordinate mapping, or unordered execution handling changes the destination or shader inputs. |
| `_cq` combinations | The generated work or its synchronization produces a different result on the selected compute queue. |

### Cause Analysis

#### DGC token decoding and pipeline binding

**Possible failure symptoms:** The host sees wrong launch dimensions, SBT observations, payloads, or ray built-ins in one or more cells.

**Possible implementation causes:** The implementation may decode the execution-set, push-constant, or trace-ray tokens incorrectly, or associate the generated command with the wrong initially bound or execution-set pipeline. The source provides the expected token order and fields in [DGC setup](../../../modules/vulkan/device_generated_commands/vktDGCRayTracingTestsExt.cpp#L1092-L1104).

#### Preprocessing and synchronization

**Possible failure symptoms:** A `_preprocess` result differs from the equivalent direct-execution result, or output readback contains stale fields.

**Possible implementation causes:** The generated state may not survive `vkCmdPreprocessGeneratedCommandsEXT` and the following `preprocessToExecuteBarrierExt`, or the final shader-write-to-host-read barrier may not make the output visible. The ordering and access masks are in [preprocess and readback synchronization](../../../modules/vulkan/device_generated_commands/vktDGCRayTracingTestsExt.cpp#L1384-L1408).

#### Unordered sequence mapping

**Possible failure symptoms:** Results land in the wrong eight-row half, or `offsetY`, launch IDs, launch sizes, and payload records disagree with the host model.

**Possible implementation causes:** The implementation may treat stream order as the source of row identity instead of using each sequence's push constant and launch coordinates. The shader's flattening rule and the two generated records are in [cell index calculation](../../../modules/vulkan/device_generated_commands/vktDGCRayTracingTestsExt.cpp#L547-L560) and [DGC records](../../../modules/vulkan/device_generated_commands/vktDGCRayTracingTestsExt.cpp#L1301-L1360).

#### Ray traversal and shader-stage data flow

**Possible failure symptoms:** Miss or closest-hit payloads, callable offsets, intersection attributes, hit built-ins, transforms, or SRB fields differ from expected values.

**Possible implementation causes:** Traversal may select the wrong geometry or shader record, or stage-to-stage payload, callable data, built-in, transform, or shader-record accesses may not follow the ray-tracing pipeline semantics. The generated stage bodies and host predictions are linked in [shader generation](../../../modules/vulkan/device_generated_commands/vktDGCRayTracingTestsExt.cpp#L611-L845) and [expected-value checks](../../../modules/vulkan/device_generated_commands/vktDGCRayTracingTestsExt.cpp#L1487-L1983).

#### Compute-queue execution

**Possible failure symptoms:** A `_cq` case fails while its non-`_cq` counterpart passes, or support checking rejects the case because no compute queue exists.

**Possible implementation causes:** Queue-family command execution or synchronization may differ for the selected queue. When no compute queue exists, [checkSupport](../../../modules/vulkan/device_generated_commands/vktDGCRayTracingTestsExt.cpp#L382-L393) rejects the case before functional validation, so that outcome does not identify a ray-tracing result error.

## Case Pruning

### Requirement-based pruning

- The case requires `VK_KHR_acceleration_structure`, `VK_KHR_ray_tracing_pipeline`, and `VK_KHR_ray_tracing_maintenance1`. DGC support must cover the ray-tracing stages used by the generated pipeline.
- Cases ending in `_cq` require a compute queue. `checkSupport` calls `context.getComputeQueue()` and rejects the case when the queue is unavailable.

These checks remove cases that cannot legally use the requested Vulkan functionality or queue.

### Design-based pruning

- The implementation registers four Boolean dimensions, not separate leaves for every geometry, flag, or SBT combination. A fixed seed of `1720182500u` fills the 256 cell parameters.
- Two `16 x 8` records cover the 16-row result without losing the distinction between the two SBT sets. The inactive BLAS geometry sits behind the ray origin so one BLAS can carry both geometry options.
- The generated shader set uses two values for each miss, closest-hit, intersection, and callable index and two SRB forms. These choices expose selection and data flow without turning each cell combination into a separate registered leaf.

These exclusions are part of the test design rather than support failures.

## Key Takeaways

- The sixteen leaves test the same shader-visible contract across fixed-pipeline and execution-set binding, direct and preprocessed execution, ordered and unordered sequences, and two queue choices.
- `offsetY` is part of the sequence data. The output cell must follow the sequence's own push constant and launch ID even when unordered execution changes processing order.
- Payload offsets make miss, closest-hit, and callable selection observable. The output buffer also checks traversal built-ins, transforms, hit attributes, launch values, and SRB data.
- Support failures remove unavailable features before execution. A functional failure means the selected path produced a cell output that differs from the host model.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Parameters and support checks | [RayTracingInstance::Params and RayTracingCase::checkSupport](../../../modules/vulkan/device_generated_commands/vktDGCRayTracingTestsExt.cpp#L333-L393) | Defines the four registration dimensions and required device functionality. |
| Generated shader programs | [RayTracingCase::initPrograms](../../../modules/vulkan/device_generated_commands/vktDGCRayTracingTestsExt.cpp#L419-L845) | Defines declarations, raygen, miss, hit, intersection, callable, and SRB variants. |
| Acceleration structures | [makeBottomLevelASWithParams and makeTopLevelASWithParams](../../../modules/vulkan/device_generated_commands/vktDGCRayTracingTestsExt.cpp#L256-L330) | Creates the geometry, inactive geometry, and translated instances. |
| DGC layout and records | [layout](../../../modules/vulkan/device_generated_commands/vktDGCRayTracingTestsExt.cpp#L1092-L1104), [records and execution](../../../modules/vulkan/device_generated_commands/vktDGCRayTracingTestsExt.cpp#L1289-L1408) | Defines tokens, SBT regions, dimensions, preprocessing, execution, and barriers. |
| Result model | [cell output verification](../../../modules/vulkan/device_generated_commands/vktDGCRayTracingTestsExt.cpp#L1410-L1988) | Computes expected traversal and shader results and returns CTS status. |
| Registration and mustpass | [createDGCRayTracingTestsExt](../../../modules/vulkan/device_generated_commands/vktDGCRayTracingTestsExt.cpp#L1993-L2010), [dgc.txt](../../../mustpass/main/vk-default/dgc.txt#L4334-L4349) | Confirms all sixteen registered identifiers. |
