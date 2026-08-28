## Overview

**Core question:** Do subgroup broadcast operations return the value from the correct active invocation?

- This page covers the `subgroups.ballot_broadcast` test family implemented by `vktSubgroupsBallotBroadcastTests.cpp`.
- The tests compare constant-ID, dynamic-ID, and first-active broadcasts across core and legacy extension forms.
- Generated cases cover compute, graphics, framebuffer, ray tracing, mesh, data-type, and required subgroup-size variants.

## Background Knowledge

For the shared concepts subgroup identity, active invocations, ballots, masks, and collective result shapes, see [Background Knowledge](../../categories/subgroups.md#background-knowledge) of the `subgroups` page.

- `subgroupBroadcast` takes an invocation ID. Its dynamic-ID form requires `subgroupBroadcastDynamicId` and a dynamically uniform ID. `subgroupBroadcastFirst` instead selects the active invocation with the lowest subgroup-local ID.
- The legacy `VK_EXT_shader_subgroup_ballot` path exposes related behavior through `readInvocationARB` and `readFirstInvocationARB` with a 64-bit ballot mask.

## Registration Hierarchy

```text
subgroups.ballot_broadcast
├── graphics
├── compute
├── framebuffer
├── ray_tracing
├── mesh
└── ext_shader_subgroup_ballot
```

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Broadcast operation | `subgroupbroadcast`, `subgroupbroadcast_nonconst`, `subgroupbroadcastfirst` | Selects constant-ID, dynamic-ID, or first-active behavior. | [`getOpTypeCaseName`](../../../modules/vulkan/subgroups/vktSubgroupsBallotBroadcastTests.cpp#L77-L90) |
| Execution path | `graphics`, `compute`, `framebuffer`, `ray_tracing`, `mesh`, `ext_shader_subgroup_ballot` | Changes the shader-stage harness or selects the legacy extension branch. | [`createSubgroupsBallotBroadcastTests`](../../../modules/vulkan/subgroups/vktSubgroupsBallotBroadcastTests.cpp#L461-L693) |
| Data type | scalar, vector, and long-vector Boolean, signed integer, unsigned integer, and floating-point types | Checks broadcast lowering and comparison for each registered GLSL type. The extension path keeps only scalar `int`, `uint`, and `float`. | [`getAllFormats`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L1878-L1912) |
| Required subgroup size | default, or powers of two from 1 through 128 for compute and mesh | Repeats the same operation under a requested subgroup size when supported. | [Registration loop](../../../modules/vulkan/subgroups/vktSubgroupsBallotBroadcastTests.cpp#L536-L554) |
| Framebuffer stage | vertex, tessellation control, tessellation evaluation, geometry | Runs the operation without an SSBO result write in the tested shader stage. | [`fbStages`](../../../modules/vulkan/subgroups/vktSubgroupsBallotBroadcastTests.cpp#L478-L483) |

The default mustpass list contains 6,117 executable paths below `subgroups.ballot_broadcast`: 1,620 compute, 180 graphics, 720 framebuffer, 69 ray-tracing, 3,240 mesh, and 288 legacy extension paths.

## Behavior Parameters

The primary behavioral axis is the `broadcast operation` prefix in each test case leaf.

### `subgroupbroadcast` - constant source invocation

Each invocation reads its own input value. The generated shader issues a separate broadcast for every constant source ID up to the CTS maximum subgroup size, then compares each active source's result with `data[id]`.

### `subgroupbroadcast_nonconst` - dynamic source invocation

The shader loops over runtime source IDs and performs `subgroupBroadcast` with a dynamically uniform ID. A second branch checks an ID that is uniform only among the active invocations in that control-flow region. These cases require `subgroupBroadcastDynamicId` and SPIR-V 1.5.

### `subgroupbroadcastfirst` - first active invocation

The shader locates the first active invocation from a ballot and checks `subgroupBroadcastFirst` against that invocation's input. Invocations other than that first invocation then enter a branch that excludes it, take another ballot, and check the new first active invocation. The original first invocation skips this second broadcast and sets result bit 1 directly; the other invocations set it only when their second comparison succeeds. Together with the initial comparison in bit 0, this produces `3` for every invocation when all applicable checks pass.

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.subgroups.ballot_broadcast.compute.subgroupbroadcast_bool
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `compute` | Uses the compute wrapper, storage buffers, specialization-controlled local sizes, and dispatch/readback harness. |
| `subgroupbroadcast_bool` | Tests the core constant-ID broadcast operation with scalar Boolean data and the default subgroup size. |

#### Purpose

This shader checks that every active constant source ID broadcasts the Boolean value originally stored for that invocation. Each invocation writes `3` only when all applicable comparisons succeed.

#### Structural Design

| Phase | Shader action | Observable result |
|-------|---------------|-------------------|
| Addressing | Flatten `gl_GlobalInvocationID` into a result-buffer offset. | Each invocation owns one result element. |
| Source capture | Read `data[gl_SubgroupInvocationID]`. | Every invocation contributes its own Boolean value. |
| Broadcast generation | Execute 128 constant-ID `subgroupBroadcast` calls. | `ops[id]` records the value obtained from source ID `id`. |
| Active-source validation | Use the ballot mask and runtime subgroup size to compare valid entries. | Any mismatch clears `tempRes` from `3` to `0`. |
| Result write | Store `tempRes` at the flattened offset. | The host later requires every element to equal `3`. |

#### Shader Code

```glsl
#version 450
#extension GL_KHR_shader_subgroup_ballot: enable
/// Specialization constants 0, 1, and 2 select local workgroup dimensions for each harness iteration.
layout (local_size_x_id = 0, local_size_y_id = 1, local_size_z_id = 2) in;
/// Binding 0 is the host-visible uint result buffer. Each invocation writes 3 only if every check passes.
layout(set = 0, binding = 0, std430) buffer Buffer1
{
  uint result[];
};
/// Binding 1 contains 128 seeded Boolean values, one possible value per subgroup invocation ID.
layout(set = 0, binding = 1, std430) buffer Buffer2
{
  bool data[];
};
void main (void)
{
  uvec3 globalSize = gl_NumWorkGroups * gl_WorkGroupSize;
  highp uint offset = globalSize.x * ((globalSize.y * gl_GlobalInvocationID.z) + gl_GlobalInvocationID.y) + gl_GlobalInvocationID.x;
  uint tempRes;
  /// Record active invocations so comparisons only use source IDs with defined broadcast results.
  uvec4 mask = subgroupBallot(true);
  uint sgSize = gl_SubgroupSize;
  uint sgInvocation = gl_SubgroupInvocationID;
  tempRes = 0x3;
  bool ops[128];
  bool d = data[sgInvocation];
  /// The generator emits one constant-ID broadcast for every ID from 0 through 127.
  ops[0] = subgroupBroadcast(d, 0u);
  ops[1] = subgroupBroadcast(d, 1u);
  ops[2] = subgroupBroadcast(d, 2u);
  ops[3] = subgroupBroadcast(d, 3u);
  ops[4] = subgroupBroadcast(d, 4u);
  ops[5] = subgroupBroadcast(d, 5u);
  ops[6] = subgroupBroadcast(d, 6u);
  ops[7] = subgroupBroadcast(d, 7u);
  ops[8] = subgroupBroadcast(d, 8u);
  ops[9] = subgroupBroadcast(d, 9u);
  ops[10] = subgroupBroadcast(d, 10u);
  ops[11] = subgroupBroadcast(d, 11u);
  ops[12] = subgroupBroadcast(d, 12u);
  ops[13] = subgroupBroadcast(d, 13u);
  ops[14] = subgroupBroadcast(d, 14u);
  ops[15] = subgroupBroadcast(d, 15u);
  ops[16] = subgroupBroadcast(d, 16u);
  ops[17] = subgroupBroadcast(d, 17u);
  ops[18] = subgroupBroadcast(d, 18u);
  ops[19] = subgroupBroadcast(d, 19u);
  ops[20] = subgroupBroadcast(d, 20u);
  ops[21] = subgroupBroadcast(d, 21u);
  ops[22] = subgroupBroadcast(d, 22u);
  ops[23] = subgroupBroadcast(d, 23u);
  ops[24] = subgroupBroadcast(d, 24u);
  ops[25] = subgroupBroadcast(d, 25u);
  ops[26] = subgroupBroadcast(d, 26u);
  ops[27] = subgroupBroadcast(d, 27u);
  ops[28] = subgroupBroadcast(d, 28u);
  ops[29] = subgroupBroadcast(d, 29u);
  ops[30] = subgroupBroadcast(d, 30u);
  ops[31] = subgroupBroadcast(d, 31u);
  ops[32] = subgroupBroadcast(d, 32u);
  ops[33] = subgroupBroadcast(d, 33u);
  ops[34] = subgroupBroadcast(d, 34u);
  ops[35] = subgroupBroadcast(d, 35u);
  ops[36] = subgroupBroadcast(d, 36u);
  ops[37] = subgroupBroadcast(d, 37u);
  ops[38] = subgroupBroadcast(d, 38u);
  ops[39] = subgroupBroadcast(d, 39u);
  ops[40] = subgroupBroadcast(d, 40u);
  ops[41] = subgroupBroadcast(d, 41u);
  ops[42] = subgroupBroadcast(d, 42u);
  ops[43] = subgroupBroadcast(d, 43u);
  ops[44] = subgroupBroadcast(d, 44u);
  ops[45] = subgroupBroadcast(d, 45u);
  ops[46] = subgroupBroadcast(d, 46u);
  ops[47] = subgroupBroadcast(d, 47u);
  ops[48] = subgroupBroadcast(d, 48u);
  ops[49] = subgroupBroadcast(d, 49u);
  ops[50] = subgroupBroadcast(d, 50u);
  ops[51] = subgroupBroadcast(d, 51u);
  ops[52] = subgroupBroadcast(d, 52u);
  ops[53] = subgroupBroadcast(d, 53u);
  ops[54] = subgroupBroadcast(d, 54u);
  ops[55] = subgroupBroadcast(d, 55u);
  ops[56] = subgroupBroadcast(d, 56u);
  ops[57] = subgroupBroadcast(d, 57u);
  ops[58] = subgroupBroadcast(d, 58u);
  ops[59] = subgroupBroadcast(d, 59u);
  ops[60] = subgroupBroadcast(d, 60u);
  ops[61] = subgroupBroadcast(d, 61u);
  ops[62] = subgroupBroadcast(d, 62u);
  ops[63] = subgroupBroadcast(d, 63u);
  ops[64] = subgroupBroadcast(d, 64u);
  ops[65] = subgroupBroadcast(d, 65u);
  ops[66] = subgroupBroadcast(d, 66u);
  ops[67] = subgroupBroadcast(d, 67u);
  ops[68] = subgroupBroadcast(d, 68u);
  ops[69] = subgroupBroadcast(d, 69u);
  ops[70] = subgroupBroadcast(d, 70u);
  ops[71] = subgroupBroadcast(d, 71u);
  ops[72] = subgroupBroadcast(d, 72u);
  ops[73] = subgroupBroadcast(d, 73u);
  ops[74] = subgroupBroadcast(d, 74u);
  ops[75] = subgroupBroadcast(d, 75u);
  ops[76] = subgroupBroadcast(d, 76u);
  ops[77] = subgroupBroadcast(d, 77u);
  ops[78] = subgroupBroadcast(d, 78u);
  ops[79] = subgroupBroadcast(d, 79u);
  ops[80] = subgroupBroadcast(d, 80u);
  ops[81] = subgroupBroadcast(d, 81u);
  ops[82] = subgroupBroadcast(d, 82u);
  ops[83] = subgroupBroadcast(d, 83u);
  ops[84] = subgroupBroadcast(d, 84u);
  ops[85] = subgroupBroadcast(d, 85u);
  ops[86] = subgroupBroadcast(d, 86u);
  ops[87] = subgroupBroadcast(d, 87u);
  ops[88] = subgroupBroadcast(d, 88u);
  ops[89] = subgroupBroadcast(d, 89u);
  ops[90] = subgroupBroadcast(d, 90u);
  ops[91] = subgroupBroadcast(d, 91u);
  ops[92] = subgroupBroadcast(d, 92u);
  ops[93] = subgroupBroadcast(d, 93u);
  ops[94] = subgroupBroadcast(d, 94u);
  ops[95] = subgroupBroadcast(d, 95u);
  ops[96] = subgroupBroadcast(d, 96u);
  ops[97] = subgroupBroadcast(d, 97u);
  ops[98] = subgroupBroadcast(d, 98u);
  ops[99] = subgroupBroadcast(d, 99u);
  ops[100] = subgroupBroadcast(d, 100u);
  ops[101] = subgroupBroadcast(d, 101u);
  ops[102] = subgroupBroadcast(d, 102u);
  ops[103] = subgroupBroadcast(d, 103u);
  ops[104] = subgroupBroadcast(d, 104u);
  ops[105] = subgroupBroadcast(d, 105u);
  ops[106] = subgroupBroadcast(d, 106u);
  ops[107] = subgroupBroadcast(d, 107u);
  ops[108] = subgroupBroadcast(d, 108u);
  ops[109] = subgroupBroadcast(d, 109u);
  ops[110] = subgroupBroadcast(d, 110u);
  ops[111] = subgroupBroadcast(d, 111u);
  ops[112] = subgroupBroadcast(d, 112u);
  ops[113] = subgroupBroadcast(d, 113u);
  ops[114] = subgroupBroadcast(d, 114u);
  ops[115] = subgroupBroadcast(d, 115u);
  ops[116] = subgroupBroadcast(d, 116u);
  ops[117] = subgroupBroadcast(d, 117u);
  ops[118] = subgroupBroadcast(d, 118u);
  ops[119] = subgroupBroadcast(d, 119u);
  ops[120] = subgroupBroadcast(d, 120u);
  ops[121] = subgroupBroadcast(d, 121u);
  ops[122] = subgroupBroadcast(d, 122u);
  ops[123] = subgroupBroadcast(d, 123u);
  ops[124] = subgroupBroadcast(d, 124u);
  ops[125] = subgroupBroadcast(d, 125u);
  ops[126] = subgroupBroadcast(d, 126u);
  ops[127] = subgroupBroadcast(d, 127u);
  /// Compare every active source below the runtime subgroup size with its original input.
  for(int id = 0; id < sgSize; id++)
  {
    if (subgroupBallotBitExtract(mask, id) && ops[id] != data[id])
    {
      tempRes = 0;
    }
  };
  result[offset] = tempRes;
}
```

#### Additional Info

- The Boolean storage buffer is represented as 32-bit values in SPIR-V, while GLSL loads convert each element to `bool` for broadcast and comparison.
- `initPrograms` selects SPIR-V 1.3 for this constant-ID compute case.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Broadcast operation | `subgroupbroadcast_nonconst` uses runtime IDs and a dynamically uniform control-flow case; `subgroupbroadcastfirst` performs two first-active checks. | [`getTestSrc`](../../../modules/vulkan/subgroups/vktSubgroupsBallotBroadcastTests.cpp#L137-L202) |
| Data type | Changes `bool` to the selected scalar, vector, or long-vector type and may add an extended-type GLSL extension. | [`getAdditionalExtensionForFormat`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L1848-L1875) |
| Stage path | Places the same test body in compute, graphics, ray-tracing, mesh, or task wrappers; framebuffer cases use a separate wrapper. | [`initStdPrograms`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L1406-L1675) |
| Extension mode | Replaces core functions and built-ins with ARB forms and a 64-bit ballot mask. | [`getExtHeader` and `getTestSrc`](../../../modules/vulkan/subgroups/vktSubgroupsBallotBroadcastTests.cpp#L92-L135) |
| Required subgroup size | Keeps the behavior but requests a pipeline subgroup size and fixes the unrolled broadcast bound to that size. | [`getTestSrc`](../../../modules/vulkan/subgroups/vktSubgroupsBallotBroadcastTests.cpp#L127-L130) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `comp`
- Target SPIRV version: `spirv1.3`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.3
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 742
; Schema: 0
               OpCapability Shader
               OpCapability GroupNonUniform
               OpCapability GroupNonUniformBallot
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_NumWorkGroups %gl_GlobalInvocationID %gl_SubgroupSize %gl_SubgroupInvocationID
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpSourceExtension "GL_KHR_shader_subgroup_ballot"
               OpSourceExtension "GL_KHR_shader_subgroup_basic"
               OpName %main "main"
               OpName %globalSize "globalSize"
               OpName %gl_NumWorkGroups "gl_NumWorkGroups"
               OpName %offset "offset"
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
               OpName %mask "mask"
               OpName %sgSize "sgSize"
               OpName %gl_SubgroupSize "gl_SubgroupSize"
               OpName %sgInvocation "sgInvocation"
               OpName %gl_SubgroupInvocationID "gl_SubgroupInvocationID"
               OpName %tempRes "tempRes"
               OpName %d "d"
               OpName %Buffer2 "Buffer2"
               OpMemberName %Buffer2 0 "data"
               OpName %_ ""
               OpName %ops "ops"
               OpName %id "id"
               OpName %Buffer1 "Buffer1"
               OpMemberName %Buffer1 0 "result"
               OpName %__0 ""
               OpDecorate %gl_NumWorkGroups BuiltIn NumWorkgroups
               OpDecorate %13 SpecId 0
               OpDecorate %14 SpecId 1
               OpDecorate %15 SpecId 2
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %gl_SubgroupSize RelaxedPrecision
               OpDecorate %gl_SubgroupSize BuiltIn SubgroupSize
               OpDecorate %48 RelaxedPrecision
               OpDecorate %gl_SubgroupInvocationID RelaxedPrecision
               OpDecorate %gl_SubgroupInvocationID BuiltIn SubgroupLocalInvocationId
               OpDecorate %51 RelaxedPrecision
               OpDecorate %_runtimearr_uint ArrayStride 4
               OpDecorate %Buffer2 Block
               OpMemberDecorate %Buffer2 0 Offset 0
               OpDecorate %_ Binding 1
               OpDecorate %_ DescriptorSet 0
               OpDecorate %_runtimearr_uint_0 ArrayStride 4
               OpDecorate %Buffer1 Block
               OpMemberDecorate %Buffer1 0 Offset 0
               OpDecorate %__0 Binding 0
               OpDecorate %__0 DescriptorSet 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
     %v3uint = OpTypeVector %uint 3
%_ptr_Function_v3uint = OpTypePointer Function %v3uint
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_NumWorkGroups = OpVariable %_ptr_Input_v3uint Input
         %13 = OpSpecConstant %uint 1
         %14 = OpSpecConstant %uint 1
         %15 = OpSpecConstant %uint 1
%gl_WorkGroupSize = OpSpecConstantComposite %v3uint %13 %14 %15
%_ptr_Function_uint = OpTypePointer Function %uint
     %uint_0 = OpConstant %uint 0
     %uint_1 = OpConstant %uint 1
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
     %uint_2 = OpConstant %uint 2
%_ptr_Input_uint = OpTypePointer Input %uint
     %v4uint = OpTypeVector %uint 4
%_ptr_Function_v4uint = OpTypePointer Function %v4uint
       %bool = OpTypeBool
       %true = OpConstantTrue %bool
     %uint_3 = OpConstant %uint 3
%gl_SubgroupSize = OpVariable %_ptr_Input_uint Input
%gl_SubgroupInvocationID = OpVariable %_ptr_Input_uint Input
%_ptr_Function_bool = OpTypePointer Function %bool
%_runtimearr_uint = OpTypeRuntimeArray %uint
    %Buffer2 = OpTypeStruct %_runtimearr_uint
%_ptr_StorageBuffer_Buffer2 = OpTypePointer StorageBuffer %Buffer2
          %_ = OpVariable %_ptr_StorageBuffer_Buffer2 StorageBuffer
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_StorageBuffer_uint = OpTypePointer StorageBuffer %uint
   %uint_128 = OpConstant %uint 128
%_arr_bool_uint_128 = OpTypeArray %bool %uint_128
%_ptr_Function__arr_bool_uint_128 = OpTypePointer Function %_arr_bool_uint_128
      %int_1 = OpConstant %int 1
      %int_2 = OpConstant %int 2
      %int_3 = OpConstant %int 3
      %int_4 = OpConstant %int 4
     %uint_4 = OpConstant %uint 4
      %int_5 = OpConstant %int 5
     %uint_5 = OpConstant %uint 5
      %int_6 = OpConstant %int 6
     %uint_6 = OpConstant %uint 6
      %int_7 = OpConstant %int 7
     %uint_7 = OpConstant %uint 7
      %int_8 = OpConstant %int 8
     %uint_8 = OpConstant %uint 8
      %int_9 = OpConstant %int 9
     %uint_9 = OpConstant %uint 9
     %int_10 = OpConstant %int 10
    %uint_10 = OpConstant %uint 10
     %int_11 = OpConstant %int 11
    %uint_11 = OpConstant %uint 11
     %int_12 = OpConstant %int 12
    %uint_12 = OpConstant %uint 12
     %int_13 = OpConstant %int 13
    %uint_13 = OpConstant %uint 13
     %int_14 = OpConstant %int 14
    %uint_14 = OpConstant %uint 14
     %int_15 = OpConstant %int 15
    %uint_15 = OpConstant %uint 15
     %int_16 = OpConstant %int 16
    %uint_16 = OpConstant %uint 16
     %int_17 = OpConstant %int 17
    %uint_17 = OpConstant %uint 17
     %int_18 = OpConstant %int 18
    %uint_18 = OpConstant %uint 18
     %int_19 = OpConstant %int 19
    %uint_19 = OpConstant %uint 19
     %int_20 = OpConstant %int 20
    %uint_20 = OpConstant %uint 20
     %int_21 = OpConstant %int 21
    %uint_21 = OpConstant %uint 21
     %int_22 = OpConstant %int 22
    %uint_22 = OpConstant %uint 22
     %int_23 = OpConstant %int 23
    %uint_23 = OpConstant %uint 23
     %int_24 = OpConstant %int 24
    %uint_24 = OpConstant %uint 24
     %int_25 = OpConstant %int 25
    %uint_25 = OpConstant %uint 25
     %int_26 = OpConstant %int 26
    %uint_26 = OpConstant %uint 26
     %int_27 = OpConstant %int 27
    %uint_27 = OpConstant %uint 27
     %int_28 = OpConstant %int 28
    %uint_28 = OpConstant %uint 28
     %int_29 = OpConstant %int 29
    %uint_29 = OpConstant %uint 29
     %int_30 = OpConstant %int 30
    %uint_30 = OpConstant %uint 30
     %int_31 = OpConstant %int 31
    %uint_31 = OpConstant %uint 31
     %int_32 = OpConstant %int 32
    %uint_32 = OpConstant %uint 32
     %int_33 = OpConstant %int 33
    %uint_33 = OpConstant %uint 33
     %int_34 = OpConstant %int 34
    %uint_34 = OpConstant %uint 34
     %int_35 = OpConstant %int 35
    %uint_35 = OpConstant %uint 35
     %int_36 = OpConstant %int 36
    %uint_36 = OpConstant %uint 36
     %int_37 = OpConstant %int 37
    %uint_37 = OpConstant %uint 37
     %int_38 = OpConstant %int 38
    %uint_38 = OpConstant %uint 38
     %int_39 = OpConstant %int 39
    %uint_39 = OpConstant %uint 39
     %int_40 = OpConstant %int 40
    %uint_40 = OpConstant %uint 40
     %int_41 = OpConstant %int 41
    %uint_41 = OpConstant %uint 41
     %int_42 = OpConstant %int 42
    %uint_42 = OpConstant %uint 42
     %int_43 = OpConstant %int 43
    %uint_43 = OpConstant %uint 43
     %int_44 = OpConstant %int 44
    %uint_44 = OpConstant %uint 44
     %int_45 = OpConstant %int 45
    %uint_45 = OpConstant %uint 45
     %int_46 = OpConstant %int 46
    %uint_46 = OpConstant %uint 46
     %int_47 = OpConstant %int 47
    %uint_47 = OpConstant %uint 47
     %int_48 = OpConstant %int 48
    %uint_48 = OpConstant %uint 48
     %int_49 = OpConstant %int 49
    %uint_49 = OpConstant %uint 49
     %int_50 = OpConstant %int 50
    %uint_50 = OpConstant %uint 50
     %int_51 = OpConstant %int 51
    %uint_51 = OpConstant %uint 51
     %int_52 = OpConstant %int 52
    %uint_52 = OpConstant %uint 52
     %int_53 = OpConstant %int 53
    %uint_53 = OpConstant %uint 53
     %int_54 = OpConstant %int 54
    %uint_54 = OpConstant %uint 54
     %int_55 = OpConstant %int 55
    %uint_55 = OpConstant %uint 55
     %int_56 = OpConstant %int 56
    %uint_56 = OpConstant %uint 56
     %int_57 = OpConstant %int 57
    %uint_57 = OpConstant %uint 57
     %int_58 = OpConstant %int 58
    %uint_58 = OpConstant %uint 58
     %int_59 = OpConstant %int 59
    %uint_59 = OpConstant %uint 59
     %int_60 = OpConstant %int 60
    %uint_60 = OpConstant %uint 60
     %int_61 = OpConstant %int 61
    %uint_61 = OpConstant %uint 61
     %int_62 = OpConstant %int 62
    %uint_62 = OpConstant %uint 62
     %int_63 = OpConstant %int 63
    %uint_63 = OpConstant %uint 63
     %int_64 = OpConstant %int 64
    %uint_64 = OpConstant %uint 64
     %int_65 = OpConstant %int 65
    %uint_65 = OpConstant %uint 65
     %int_66 = OpConstant %int 66
    %uint_66 = OpConstant %uint 66
     %int_67 = OpConstant %int 67
    %uint_67 = OpConstant %uint 67
     %int_68 = OpConstant %int 68
    %uint_68 = OpConstant %uint 68
     %int_69 = OpConstant %int 69
    %uint_69 = OpConstant %uint 69
     %int_70 = OpConstant %int 70
    %uint_70 = OpConstant %uint 70
     %int_71 = OpConstant %int 71
    %uint_71 = OpConstant %uint 71
     %int_72 = OpConstant %int 72
    %uint_72 = OpConstant %uint 72
     %int_73 = OpConstant %int 73
    %uint_73 = OpConstant %uint 73
     %int_74 = OpConstant %int 74
    %uint_74 = OpConstant %uint 74
     %int_75 = OpConstant %int 75
    %uint_75 = OpConstant %uint 75
     %int_76 = OpConstant %int 76
    %uint_76 = OpConstant %uint 76
     %int_77 = OpConstant %int 77
    %uint_77 = OpConstant %uint 77
     %int_78 = OpConstant %int 78
    %uint_78 = OpConstant %uint 78
     %int_79 = OpConstant %int 79
    %uint_79 = OpConstant %uint 79
     %int_80 = OpConstant %int 80
    %uint_80 = OpConstant %uint 80
     %int_81 = OpConstant %int 81
    %uint_81 = OpConstant %uint 81
     %int_82 = OpConstant %int 82
    %uint_82 = OpConstant %uint 82
     %int_83 = OpConstant %int 83
    %uint_83 = OpConstant %uint 83
     %int_84 = OpConstant %int 84
    %uint_84 = OpConstant %uint 84
     %int_85 = OpConstant %int 85
    %uint_85 = OpConstant %uint 85
     %int_86 = OpConstant %int 86
    %uint_86 = OpConstant %uint 86
     %int_87 = OpConstant %int 87
    %uint_87 = OpConstant %uint 87
     %int_88 = OpConstant %int 88
    %uint_88 = OpConstant %uint 88
     %int_89 = OpConstant %int 89
    %uint_89 = OpConstant %uint 89
     %int_90 = OpConstant %int 90
    %uint_90 = OpConstant %uint 90
     %int_91 = OpConstant %int 91
    %uint_91 = OpConstant %uint 91
     %int_92 = OpConstant %int 92
    %uint_92 = OpConstant %uint 92
     %int_93 = OpConstant %int 93
    %uint_93 = OpConstant %uint 93
     %int_94 = OpConstant %int 94
    %uint_94 = OpConstant %uint 94
     %int_95 = OpConstant %int 95
    %uint_95 = OpConstant %uint 95
     %int_96 = OpConstant %int 96
    %uint_96 = OpConstant %uint 96
     %int_97 = OpConstant %int 97
    %uint_97 = OpConstant %uint 97
     %int_98 = OpConstant %int 98
    %uint_98 = OpConstant %uint 98
     %int_99 = OpConstant %int 99
    %uint_99 = OpConstant %uint 99
    %int_100 = OpConstant %int 100
   %uint_100 = OpConstant %uint 100
    %int_101 = OpConstant %int 101
   %uint_101 = OpConstant %uint 101
    %int_102 = OpConstant %int 102
   %uint_102 = OpConstant %uint 102
    %int_103 = OpConstant %int 103
   %uint_103 = OpConstant %uint 103
    %int_104 = OpConstant %int 104
   %uint_104 = OpConstant %uint 104
    %int_105 = OpConstant %int 105
   %uint_105 = OpConstant %uint 105
    %int_106 = OpConstant %int 106
   %uint_106 = OpConstant %uint 106
    %int_107 = OpConstant %int 107
   %uint_107 = OpConstant %uint 107
    %int_108 = OpConstant %int 108
   %uint_108 = OpConstant %uint 108
    %int_109 = OpConstant %int 109
   %uint_109 = OpConstant %uint 109
    %int_110 = OpConstant %int 110
   %uint_110 = OpConstant %uint 110
    %int_111 = OpConstant %int 111
   %uint_111 = OpConstant %uint 111
    %int_112 = OpConstant %int 112
   %uint_112 = OpConstant %uint 112
    %int_113 = OpConstant %int 113
   %uint_113 = OpConstant %uint 113
    %int_114 = OpConstant %int 114
   %uint_114 = OpConstant %uint 114
    %int_115 = OpConstant %int 115
   %uint_115 = OpConstant %uint 115
    %int_116 = OpConstant %int 116
   %uint_116 = OpConstant %uint 116
    %int_117 = OpConstant %int 117
   %uint_117 = OpConstant %uint 117
    %int_118 = OpConstant %int 118
   %uint_118 = OpConstant %uint 118
    %int_119 = OpConstant %int 119
   %uint_119 = OpConstant %uint 119
    %int_120 = OpConstant %int 120
   %uint_120 = OpConstant %uint 120
    %int_121 = OpConstant %int 121
   %uint_121 = OpConstant %uint 121
    %int_122 = OpConstant %int 122
   %uint_122 = OpConstant %uint 122
    %int_123 = OpConstant %int 123
   %uint_123 = OpConstant %uint 123
    %int_124 = OpConstant %int 124
   %uint_124 = OpConstant %uint 124
    %int_125 = OpConstant %int 125
   %uint_125 = OpConstant %uint 125
    %int_126 = OpConstant %int 126
   %uint_126 = OpConstant %uint 126
    %int_127 = OpConstant %int 127
   %uint_127 = OpConstant %uint 127
%_ptr_Function_int = OpTypePointer Function %int
%_runtimearr_uint_0 = OpTypeRuntimeArray %uint
    %Buffer1 = OpTypeStruct %_runtimearr_uint_0
%_ptr_StorageBuffer_Buffer1 = OpTypePointer StorageBuffer %Buffer1
        %__0 = OpVariable %_ptr_StorageBuffer_Buffer1 StorageBuffer
       %main = OpFunction %void None %3
          %5 = OpLabel
 %globalSize = OpVariable %_ptr_Function_v3uint Function
     %offset = OpVariable %_ptr_Function_uint Function
       %mask = OpVariable %_ptr_Function_v4uint Function
     %sgSize = OpVariable %_ptr_Function_uint Function
%sgInvocation = OpVariable %_ptr_Function_uint Function
    %tempRes = OpVariable %_ptr_Function_uint Function
          %d = OpVariable %_ptr_Function_bool Function
        %ops = OpVariable %_ptr_Function__arr_bool_uint_128 Function
         %id = OpVariable %_ptr_Function_int Function
         %12 = OpLoad %v3uint %gl_NumWorkGroups
         %17 = OpIMul %v3uint %12 %gl_WorkGroupSize
               OpStore %globalSize %17
         %21 = OpAccessChain %_ptr_Function_uint %globalSize %uint_0
         %22 = OpLoad %uint %21
         %24 = OpAccessChain %_ptr_Function_uint %globalSize %uint_1
         %25 = OpLoad %uint %24
         %29 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_2
         %30 = OpLoad %uint %29
         %31 = OpIMul %uint %25 %30
         %32 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_1
         %33 = OpLoad %uint %32
         %34 = OpIAdd %uint %31 %33
         %35 = OpIMul %uint %22 %34
         %36 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %37 = OpLoad %uint %36
         %38 = OpIAdd %uint %35 %37
               OpStore %offset %38
         %45 = OpGroupNonUniformBallot %v4uint %uint_3 %true
               OpStore %mask %45
         %48 = OpLoad %uint %gl_SubgroupSize
               OpStore %sgSize %48
         %51 = OpLoad %uint %gl_SubgroupInvocationID
               OpStore %sgInvocation %51
               OpStore %tempRes %uint_3
         %61 = OpLoad %uint %sgInvocation
         %63 = OpAccessChain %_ptr_StorageBuffer_uint %_ %int_0 %61
         %64 = OpLoad %uint %63
         %65 = OpINotEqual %bool %64 %uint_0
               OpStore %d %65
         %70 = OpLoad %bool %d
         %71 = OpGroupNonUniformBroadcast %bool %uint_3 %70 %uint_0
         %72 = OpAccessChain %_ptr_Function_bool %ops %int_0
               OpStore %72 %71
         %74 = OpLoad %bool %d
         %75 = OpGroupNonUniformBroadcast %bool %uint_3 %74 %uint_1
         %76 = OpAccessChain %_ptr_Function_bool %ops %int_1
               OpStore %76 %75
         %78 = OpLoad %bool %d
         %79 = OpGroupNonUniformBroadcast %bool %uint_3 %78 %uint_2
         %80 = OpAccessChain %_ptr_Function_bool %ops %int_2
               OpStore %80 %79
         %82 = OpLoad %bool %d
         %83 = OpGroupNonUniformBroadcast %bool %uint_3 %82 %uint_3
         %84 = OpAccessChain %_ptr_Function_bool %ops %int_3
               OpStore %84 %83
         %86 = OpLoad %bool %d
         %88 = OpGroupNonUniformBroadcast %bool %uint_3 %86 %uint_4
         %89 = OpAccessChain %_ptr_Function_bool %ops %int_4
               OpStore %89 %88
         %91 = OpLoad %bool %d
         %93 = OpGroupNonUniformBroadcast %bool %uint_3 %91 %uint_5
         %94 = OpAccessChain %_ptr_Function_bool %ops %int_5
               OpStore %94 %93
         %96 = OpLoad %bool %d
         %98 = OpGroupNonUniformBroadcast %bool %uint_3 %96 %uint_6
         %99 = OpAccessChain %_ptr_Function_bool %ops %int_6
               OpStore %99 %98
        %101 = OpLoad %bool %d
        %103 = OpGroupNonUniformBroadcast %bool %uint_3 %101 %uint_7
        %104 = OpAccessChain %_ptr_Function_bool %ops %int_7
               OpStore %104 %103
        %106 = OpLoad %bool %d
        %108 = OpGroupNonUniformBroadcast %bool %uint_3 %106 %uint_8
        %109 = OpAccessChain %_ptr_Function_bool %ops %int_8
               OpStore %109 %108
        %111 = OpLoad %bool %d
        %113 = OpGroupNonUniformBroadcast %bool %uint_3 %111 %uint_9
        %114 = OpAccessChain %_ptr_Function_bool %ops %int_9
               OpStore %114 %113
        %116 = OpLoad %bool %d
        %118 = OpGroupNonUniformBroadcast %bool %uint_3 %116 %uint_10
        %119 = OpAccessChain %_ptr_Function_bool %ops %int_10
               OpStore %119 %118
        %121 = OpLoad %bool %d
        %123 = OpGroupNonUniformBroadcast %bool %uint_3 %121 %uint_11
        %124 = OpAccessChain %_ptr_Function_bool %ops %int_11
               OpStore %124 %123
        %126 = OpLoad %bool %d
        %128 = OpGroupNonUniformBroadcast %bool %uint_3 %126 %uint_12
        %129 = OpAccessChain %_ptr_Function_bool %ops %int_12
               OpStore %129 %128
        %131 = OpLoad %bool %d
        %133 = OpGroupNonUniformBroadcast %bool %uint_3 %131 %uint_13
        %134 = OpAccessChain %_ptr_Function_bool %ops %int_13
               OpStore %134 %133
        %136 = OpLoad %bool %d
        %138 = OpGroupNonUniformBroadcast %bool %uint_3 %136 %uint_14
        %139 = OpAccessChain %_ptr_Function_bool %ops %int_14
               OpStore %139 %138
        %141 = OpLoad %bool %d
        %143 = OpGroupNonUniformBroadcast %bool %uint_3 %141 %uint_15
        %144 = OpAccessChain %_ptr_Function_bool %ops %int_15
               OpStore %144 %143
        %146 = OpLoad %bool %d
        %148 = OpGroupNonUniformBroadcast %bool %uint_3 %146 %uint_16
        %149 = OpAccessChain %_ptr_Function_bool %ops %int_16
               OpStore %149 %148
        %151 = OpLoad %bool %d
        %153 = OpGroupNonUniformBroadcast %bool %uint_3 %151 %uint_17
        %154 = OpAccessChain %_ptr_Function_bool %ops %int_17
               OpStore %154 %153
        %156 = OpLoad %bool %d
        %158 = OpGroupNonUniformBroadcast %bool %uint_3 %156 %uint_18
        %159 = OpAccessChain %_ptr_Function_bool %ops %int_18
               OpStore %159 %158
        %161 = OpLoad %bool %d
        %163 = OpGroupNonUniformBroadcast %bool %uint_3 %161 %uint_19
        %164 = OpAccessChain %_ptr_Function_bool %ops %int_19
               OpStore %164 %163
        %166 = OpLoad %bool %d
        %168 = OpGroupNonUniformBroadcast %bool %uint_3 %166 %uint_20
        %169 = OpAccessChain %_ptr_Function_bool %ops %int_20
               OpStore %169 %168
        %171 = OpLoad %bool %d
        %173 = OpGroupNonUniformBroadcast %bool %uint_3 %171 %uint_21
        %174 = OpAccessChain %_ptr_Function_bool %ops %int_21
               OpStore %174 %173
        %176 = OpLoad %bool %d
        %178 = OpGroupNonUniformBroadcast %bool %uint_3 %176 %uint_22
        %179 = OpAccessChain %_ptr_Function_bool %ops %int_22
               OpStore %179 %178
        %181 = OpLoad %bool %d
        %183 = OpGroupNonUniformBroadcast %bool %uint_3 %181 %uint_23
        %184 = OpAccessChain %_ptr_Function_bool %ops %int_23
               OpStore %184 %183
        %186 = OpLoad %bool %d
        %188 = OpGroupNonUniformBroadcast %bool %uint_3 %186 %uint_24
        %189 = OpAccessChain %_ptr_Function_bool %ops %int_24
               OpStore %189 %188
        %191 = OpLoad %bool %d
        %193 = OpGroupNonUniformBroadcast %bool %uint_3 %191 %uint_25
        %194 = OpAccessChain %_ptr_Function_bool %ops %int_25
               OpStore %194 %193
        %196 = OpLoad %bool %d
        %198 = OpGroupNonUniformBroadcast %bool %uint_3 %196 %uint_26
        %199 = OpAccessChain %_ptr_Function_bool %ops %int_26
               OpStore %199 %198
        %201 = OpLoad %bool %d
        %203 = OpGroupNonUniformBroadcast %bool %uint_3 %201 %uint_27
        %204 = OpAccessChain %_ptr_Function_bool %ops %int_27
               OpStore %204 %203
        %206 = OpLoad %bool %d
        %208 = OpGroupNonUniformBroadcast %bool %uint_3 %206 %uint_28
        %209 = OpAccessChain %_ptr_Function_bool %ops %int_28
               OpStore %209 %208
        %211 = OpLoad %bool %d
        %213 = OpGroupNonUniformBroadcast %bool %uint_3 %211 %uint_29
        %214 = OpAccessChain %_ptr_Function_bool %ops %int_29
               OpStore %214 %213
        %216 = OpLoad %bool %d
        %218 = OpGroupNonUniformBroadcast %bool %uint_3 %216 %uint_30
        %219 = OpAccessChain %_ptr_Function_bool %ops %int_30
               OpStore %219 %218
        %221 = OpLoad %bool %d
        %223 = OpGroupNonUniformBroadcast %bool %uint_3 %221 %uint_31
        %224 = OpAccessChain %_ptr_Function_bool %ops %int_31
               OpStore %224 %223
        %226 = OpLoad %bool %d
        %228 = OpGroupNonUniformBroadcast %bool %uint_3 %226 %uint_32
        %229 = OpAccessChain %_ptr_Function_bool %ops %int_32
               OpStore %229 %228
        %231 = OpLoad %bool %d
        %233 = OpGroupNonUniformBroadcast %bool %uint_3 %231 %uint_33
        %234 = OpAccessChain %_ptr_Function_bool %ops %int_33
               OpStore %234 %233
        %236 = OpLoad %bool %d
        %238 = OpGroupNonUniformBroadcast %bool %uint_3 %236 %uint_34
        %239 = OpAccessChain %_ptr_Function_bool %ops %int_34
               OpStore %239 %238
        %241 = OpLoad %bool %d
        %243 = OpGroupNonUniformBroadcast %bool %uint_3 %241 %uint_35
        %244 = OpAccessChain %_ptr_Function_bool %ops %int_35
               OpStore %244 %243
        %246 = OpLoad %bool %d
        %248 = OpGroupNonUniformBroadcast %bool %uint_3 %246 %uint_36
        %249 = OpAccessChain %_ptr_Function_bool %ops %int_36
               OpStore %249 %248
        %251 = OpLoad %bool %d
        %253 = OpGroupNonUniformBroadcast %bool %uint_3 %251 %uint_37
        %254 = OpAccessChain %_ptr_Function_bool %ops %int_37
               OpStore %254 %253
        %256 = OpLoad %bool %d
        %258 = OpGroupNonUniformBroadcast %bool %uint_3 %256 %uint_38
        %259 = OpAccessChain %_ptr_Function_bool %ops %int_38
               OpStore %259 %258
        %261 = OpLoad %bool %d
        %263 = OpGroupNonUniformBroadcast %bool %uint_3 %261 %uint_39
        %264 = OpAccessChain %_ptr_Function_bool %ops %int_39
               OpStore %264 %263
        %266 = OpLoad %bool %d
        %268 = OpGroupNonUniformBroadcast %bool %uint_3 %266 %uint_40
        %269 = OpAccessChain %_ptr_Function_bool %ops %int_40
               OpStore %269 %268
        %271 = OpLoad %bool %d
        %273 = OpGroupNonUniformBroadcast %bool %uint_3 %271 %uint_41
        %274 = OpAccessChain %_ptr_Function_bool %ops %int_41
               OpStore %274 %273
        %276 = OpLoad %bool %d
        %278 = OpGroupNonUniformBroadcast %bool %uint_3 %276 %uint_42
        %279 = OpAccessChain %_ptr_Function_bool %ops %int_42
               OpStore %279 %278
        %281 = OpLoad %bool %d
        %283 = OpGroupNonUniformBroadcast %bool %uint_3 %281 %uint_43
        %284 = OpAccessChain %_ptr_Function_bool %ops %int_43
               OpStore %284 %283
        %286 = OpLoad %bool %d
        %288 = OpGroupNonUniformBroadcast %bool %uint_3 %286 %uint_44
        %289 = OpAccessChain %_ptr_Function_bool %ops %int_44
               OpStore %289 %288
        %291 = OpLoad %bool %d
        %293 = OpGroupNonUniformBroadcast %bool %uint_3 %291 %uint_45
        %294 = OpAccessChain %_ptr_Function_bool %ops %int_45
               OpStore %294 %293
        %296 = OpLoad %bool %d
        %298 = OpGroupNonUniformBroadcast %bool %uint_3 %296 %uint_46
        %299 = OpAccessChain %_ptr_Function_bool %ops %int_46
               OpStore %299 %298
        %301 = OpLoad %bool %d
        %303 = OpGroupNonUniformBroadcast %bool %uint_3 %301 %uint_47
        %304 = OpAccessChain %_ptr_Function_bool %ops %int_47
               OpStore %304 %303
        %306 = OpLoad %bool %d
        %308 = OpGroupNonUniformBroadcast %bool %uint_3 %306 %uint_48
        %309 = OpAccessChain %_ptr_Function_bool %ops %int_48
               OpStore %309 %308
        %311 = OpLoad %bool %d
        %313 = OpGroupNonUniformBroadcast %bool %uint_3 %311 %uint_49
        %314 = OpAccessChain %_ptr_Function_bool %ops %int_49
               OpStore %314 %313
        %316 = OpLoad %bool %d
        %318 = OpGroupNonUniformBroadcast %bool %uint_3 %316 %uint_50
        %319 = OpAccessChain %_ptr_Function_bool %ops %int_50
               OpStore %319 %318
        %321 = OpLoad %bool %d
        %323 = OpGroupNonUniformBroadcast %bool %uint_3 %321 %uint_51
        %324 = OpAccessChain %_ptr_Function_bool %ops %int_51
               OpStore %324 %323
        %326 = OpLoad %bool %d
        %328 = OpGroupNonUniformBroadcast %bool %uint_3 %326 %uint_52
        %329 = OpAccessChain %_ptr_Function_bool %ops %int_52
               OpStore %329 %328
        %331 = OpLoad %bool %d
        %333 = OpGroupNonUniformBroadcast %bool %uint_3 %331 %uint_53
        %334 = OpAccessChain %_ptr_Function_bool %ops %int_53
               OpStore %334 %333
        %336 = OpLoad %bool %d
        %338 = OpGroupNonUniformBroadcast %bool %uint_3 %336 %uint_54
        %339 = OpAccessChain %_ptr_Function_bool %ops %int_54
               OpStore %339 %338
        %341 = OpLoad %bool %d
        %343 = OpGroupNonUniformBroadcast %bool %uint_3 %341 %uint_55
        %344 = OpAccessChain %_ptr_Function_bool %ops %int_55
               OpStore %344 %343
        %346 = OpLoad %bool %d
        %348 = OpGroupNonUniformBroadcast %bool %uint_3 %346 %uint_56
        %349 = OpAccessChain %_ptr_Function_bool %ops %int_56
               OpStore %349 %348
        %351 = OpLoad %bool %d
        %353 = OpGroupNonUniformBroadcast %bool %uint_3 %351 %uint_57
        %354 = OpAccessChain %_ptr_Function_bool %ops %int_57
               OpStore %354 %353
        %356 = OpLoad %bool %d
        %358 = OpGroupNonUniformBroadcast %bool %uint_3 %356 %uint_58
        %359 = OpAccessChain %_ptr_Function_bool %ops %int_58
               OpStore %359 %358
        %361 = OpLoad %bool %d
        %363 = OpGroupNonUniformBroadcast %bool %uint_3 %361 %uint_59
        %364 = OpAccessChain %_ptr_Function_bool %ops %int_59
               OpStore %364 %363
        %366 = OpLoad %bool %d
        %368 = OpGroupNonUniformBroadcast %bool %uint_3 %366 %uint_60
        %369 = OpAccessChain %_ptr_Function_bool %ops %int_60
               OpStore %369 %368
        %371 = OpLoad %bool %d
        %373 = OpGroupNonUniformBroadcast %bool %uint_3 %371 %uint_61
        %374 = OpAccessChain %_ptr_Function_bool %ops %int_61
               OpStore %374 %373
        %376 = OpLoad %bool %d
        %378 = OpGroupNonUniformBroadcast %bool %uint_3 %376 %uint_62
        %379 = OpAccessChain %_ptr_Function_bool %ops %int_62
               OpStore %379 %378
        %381 = OpLoad %bool %d
        %383 = OpGroupNonUniformBroadcast %bool %uint_3 %381 %uint_63
        %384 = OpAccessChain %_ptr_Function_bool %ops %int_63
               OpStore %384 %383
        %386 = OpLoad %bool %d
        %388 = OpGroupNonUniformBroadcast %bool %uint_3 %386 %uint_64
        %389 = OpAccessChain %_ptr_Function_bool %ops %int_64
               OpStore %389 %388
        %391 = OpLoad %bool %d
        %393 = OpGroupNonUniformBroadcast %bool %uint_3 %391 %uint_65
        %394 = OpAccessChain %_ptr_Function_bool %ops %int_65
               OpStore %394 %393
        %396 = OpLoad %bool %d
        %398 = OpGroupNonUniformBroadcast %bool %uint_3 %396 %uint_66
        %399 = OpAccessChain %_ptr_Function_bool %ops %int_66
               OpStore %399 %398
        %401 = OpLoad %bool %d
        %403 = OpGroupNonUniformBroadcast %bool %uint_3 %401 %uint_67
        %404 = OpAccessChain %_ptr_Function_bool %ops %int_67
               OpStore %404 %403
        %406 = OpLoad %bool %d
        %408 = OpGroupNonUniformBroadcast %bool %uint_3 %406 %uint_68
        %409 = OpAccessChain %_ptr_Function_bool %ops %int_68
               OpStore %409 %408
        %411 = OpLoad %bool %d
        %413 = OpGroupNonUniformBroadcast %bool %uint_3 %411 %uint_69
        %414 = OpAccessChain %_ptr_Function_bool %ops %int_69
               OpStore %414 %413
        %416 = OpLoad %bool %d
        %418 = OpGroupNonUniformBroadcast %bool %uint_3 %416 %uint_70
        %419 = OpAccessChain %_ptr_Function_bool %ops %int_70
               OpStore %419 %418
        %421 = OpLoad %bool %d
        %423 = OpGroupNonUniformBroadcast %bool %uint_3 %421 %uint_71
        %424 = OpAccessChain %_ptr_Function_bool %ops %int_71
               OpStore %424 %423
        %426 = OpLoad %bool %d
        %428 = OpGroupNonUniformBroadcast %bool %uint_3 %426 %uint_72
        %429 = OpAccessChain %_ptr_Function_bool %ops %int_72
               OpStore %429 %428
        %431 = OpLoad %bool %d
        %433 = OpGroupNonUniformBroadcast %bool %uint_3 %431 %uint_73
        %434 = OpAccessChain %_ptr_Function_bool %ops %int_73
               OpStore %434 %433
        %436 = OpLoad %bool %d
        %438 = OpGroupNonUniformBroadcast %bool %uint_3 %436 %uint_74
        %439 = OpAccessChain %_ptr_Function_bool %ops %int_74
               OpStore %439 %438
        %441 = OpLoad %bool %d
        %443 = OpGroupNonUniformBroadcast %bool %uint_3 %441 %uint_75
        %444 = OpAccessChain %_ptr_Function_bool %ops %int_75
               OpStore %444 %443
        %446 = OpLoad %bool %d
        %448 = OpGroupNonUniformBroadcast %bool %uint_3 %446 %uint_76
        %449 = OpAccessChain %_ptr_Function_bool %ops %int_76
               OpStore %449 %448
        %451 = OpLoad %bool %d
        %453 = OpGroupNonUniformBroadcast %bool %uint_3 %451 %uint_77
        %454 = OpAccessChain %_ptr_Function_bool %ops %int_77
               OpStore %454 %453
        %456 = OpLoad %bool %d
        %458 = OpGroupNonUniformBroadcast %bool %uint_3 %456 %uint_78
        %459 = OpAccessChain %_ptr_Function_bool %ops %int_78
               OpStore %459 %458
        %461 = OpLoad %bool %d
        %463 = OpGroupNonUniformBroadcast %bool %uint_3 %461 %uint_79
        %464 = OpAccessChain %_ptr_Function_bool %ops %int_79
               OpStore %464 %463
        %466 = OpLoad %bool %d
        %468 = OpGroupNonUniformBroadcast %bool %uint_3 %466 %uint_80
        %469 = OpAccessChain %_ptr_Function_bool %ops %int_80
               OpStore %469 %468
        %471 = OpLoad %bool %d
        %473 = OpGroupNonUniformBroadcast %bool %uint_3 %471 %uint_81
        %474 = OpAccessChain %_ptr_Function_bool %ops %int_81
               OpStore %474 %473
        %476 = OpLoad %bool %d
        %478 = OpGroupNonUniformBroadcast %bool %uint_3 %476 %uint_82
        %479 = OpAccessChain %_ptr_Function_bool %ops %int_82
               OpStore %479 %478
        %481 = OpLoad %bool %d
        %483 = OpGroupNonUniformBroadcast %bool %uint_3 %481 %uint_83
        %484 = OpAccessChain %_ptr_Function_bool %ops %int_83
               OpStore %484 %483
        %486 = OpLoad %bool %d
        %488 = OpGroupNonUniformBroadcast %bool %uint_3 %486 %uint_84
        %489 = OpAccessChain %_ptr_Function_bool %ops %int_84
               OpStore %489 %488
        %491 = OpLoad %bool %d
        %493 = OpGroupNonUniformBroadcast %bool %uint_3 %491 %uint_85
        %494 = OpAccessChain %_ptr_Function_bool %ops %int_85
               OpStore %494 %493
        %496 = OpLoad %bool %d
        %498 = OpGroupNonUniformBroadcast %bool %uint_3 %496 %uint_86
        %499 = OpAccessChain %_ptr_Function_bool %ops %int_86
               OpStore %499 %498
        %501 = OpLoad %bool %d
        %503 = OpGroupNonUniformBroadcast %bool %uint_3 %501 %uint_87
        %504 = OpAccessChain %_ptr_Function_bool %ops %int_87
               OpStore %504 %503
        %506 = OpLoad %bool %d
        %508 = OpGroupNonUniformBroadcast %bool %uint_3 %506 %uint_88
        %509 = OpAccessChain %_ptr_Function_bool %ops %int_88
               OpStore %509 %508
        %511 = OpLoad %bool %d
        %513 = OpGroupNonUniformBroadcast %bool %uint_3 %511 %uint_89
        %514 = OpAccessChain %_ptr_Function_bool %ops %int_89
               OpStore %514 %513
        %516 = OpLoad %bool %d
        %518 = OpGroupNonUniformBroadcast %bool %uint_3 %516 %uint_90
        %519 = OpAccessChain %_ptr_Function_bool %ops %int_90
               OpStore %519 %518
        %521 = OpLoad %bool %d
        %523 = OpGroupNonUniformBroadcast %bool %uint_3 %521 %uint_91
        %524 = OpAccessChain %_ptr_Function_bool %ops %int_91
               OpStore %524 %523
        %526 = OpLoad %bool %d
        %528 = OpGroupNonUniformBroadcast %bool %uint_3 %526 %uint_92
        %529 = OpAccessChain %_ptr_Function_bool %ops %int_92
               OpStore %529 %528
        %531 = OpLoad %bool %d
        %533 = OpGroupNonUniformBroadcast %bool %uint_3 %531 %uint_93
        %534 = OpAccessChain %_ptr_Function_bool %ops %int_93
               OpStore %534 %533
        %536 = OpLoad %bool %d
        %538 = OpGroupNonUniformBroadcast %bool %uint_3 %536 %uint_94
        %539 = OpAccessChain %_ptr_Function_bool %ops %int_94
               OpStore %539 %538
        %541 = OpLoad %bool %d
        %543 = OpGroupNonUniformBroadcast %bool %uint_3 %541 %uint_95
        %544 = OpAccessChain %_ptr_Function_bool %ops %int_95
               OpStore %544 %543
        %546 = OpLoad %bool %d
        %548 = OpGroupNonUniformBroadcast %bool %uint_3 %546 %uint_96
        %549 = OpAccessChain %_ptr_Function_bool %ops %int_96
               OpStore %549 %548
        %551 = OpLoad %bool %d
        %553 = OpGroupNonUniformBroadcast %bool %uint_3 %551 %uint_97
        %554 = OpAccessChain %_ptr_Function_bool %ops %int_97
               OpStore %554 %553
        %556 = OpLoad %bool %d
        %558 = OpGroupNonUniformBroadcast %bool %uint_3 %556 %uint_98
        %559 = OpAccessChain %_ptr_Function_bool %ops %int_98
               OpStore %559 %558
        %561 = OpLoad %bool %d
        %563 = OpGroupNonUniformBroadcast %bool %uint_3 %561 %uint_99
        %564 = OpAccessChain %_ptr_Function_bool %ops %int_99
               OpStore %564 %563
        %566 = OpLoad %bool %d
        %568 = OpGroupNonUniformBroadcast %bool %uint_3 %566 %uint_100
        %569 = OpAccessChain %_ptr_Function_bool %ops %int_100
               OpStore %569 %568
        %571 = OpLoad %bool %d
        %573 = OpGroupNonUniformBroadcast %bool %uint_3 %571 %uint_101
        %574 = OpAccessChain %_ptr_Function_bool %ops %int_101
               OpStore %574 %573
        %576 = OpLoad %bool %d
        %578 = OpGroupNonUniformBroadcast %bool %uint_3 %576 %uint_102
        %579 = OpAccessChain %_ptr_Function_bool %ops %int_102
               OpStore %579 %578
        %581 = OpLoad %bool %d
        %583 = OpGroupNonUniformBroadcast %bool %uint_3 %581 %uint_103
        %584 = OpAccessChain %_ptr_Function_bool %ops %int_103
               OpStore %584 %583
        %586 = OpLoad %bool %d
        %588 = OpGroupNonUniformBroadcast %bool %uint_3 %586 %uint_104
        %589 = OpAccessChain %_ptr_Function_bool %ops %int_104
               OpStore %589 %588
        %591 = OpLoad %bool %d
        %593 = OpGroupNonUniformBroadcast %bool %uint_3 %591 %uint_105
        %594 = OpAccessChain %_ptr_Function_bool %ops %int_105
               OpStore %594 %593
        %596 = OpLoad %bool %d
        %598 = OpGroupNonUniformBroadcast %bool %uint_3 %596 %uint_106
        %599 = OpAccessChain %_ptr_Function_bool %ops %int_106
               OpStore %599 %598
        %601 = OpLoad %bool %d
        %603 = OpGroupNonUniformBroadcast %bool %uint_3 %601 %uint_107
        %604 = OpAccessChain %_ptr_Function_bool %ops %int_107
               OpStore %604 %603
        %606 = OpLoad %bool %d
        %608 = OpGroupNonUniformBroadcast %bool %uint_3 %606 %uint_108
        %609 = OpAccessChain %_ptr_Function_bool %ops %int_108
               OpStore %609 %608
        %611 = OpLoad %bool %d
        %613 = OpGroupNonUniformBroadcast %bool %uint_3 %611 %uint_109
        %614 = OpAccessChain %_ptr_Function_bool %ops %int_109
               OpStore %614 %613
        %616 = OpLoad %bool %d
        %618 = OpGroupNonUniformBroadcast %bool %uint_3 %616 %uint_110
        %619 = OpAccessChain %_ptr_Function_bool %ops %int_110
               OpStore %619 %618
        %621 = OpLoad %bool %d
        %623 = OpGroupNonUniformBroadcast %bool %uint_3 %621 %uint_111
        %624 = OpAccessChain %_ptr_Function_bool %ops %int_111
               OpStore %624 %623
        %626 = OpLoad %bool %d
        %628 = OpGroupNonUniformBroadcast %bool %uint_3 %626 %uint_112
        %629 = OpAccessChain %_ptr_Function_bool %ops %int_112
               OpStore %629 %628
        %631 = OpLoad %bool %d
        %633 = OpGroupNonUniformBroadcast %bool %uint_3 %631 %uint_113
        %634 = OpAccessChain %_ptr_Function_bool %ops %int_113
               OpStore %634 %633
        %636 = OpLoad %bool %d
        %638 = OpGroupNonUniformBroadcast %bool %uint_3 %636 %uint_114
        %639 = OpAccessChain %_ptr_Function_bool %ops %int_114
               OpStore %639 %638
        %641 = OpLoad %bool %d
        %643 = OpGroupNonUniformBroadcast %bool %uint_3 %641 %uint_115
        %644 = OpAccessChain %_ptr_Function_bool %ops %int_115
               OpStore %644 %643
        %646 = OpLoad %bool %d
        %648 = OpGroupNonUniformBroadcast %bool %uint_3 %646 %uint_116
        %649 = OpAccessChain %_ptr_Function_bool %ops %int_116
               OpStore %649 %648
        %651 = OpLoad %bool %d
        %653 = OpGroupNonUniformBroadcast %bool %uint_3 %651 %uint_117
        %654 = OpAccessChain %_ptr_Function_bool %ops %int_117
               OpStore %654 %653
        %656 = OpLoad %bool %d
        %658 = OpGroupNonUniformBroadcast %bool %uint_3 %656 %uint_118
        %659 = OpAccessChain %_ptr_Function_bool %ops %int_118
               OpStore %659 %658
        %661 = OpLoad %bool %d
        %663 = OpGroupNonUniformBroadcast %bool %uint_3 %661 %uint_119
        %664 = OpAccessChain %_ptr_Function_bool %ops %int_119
               OpStore %664 %663
        %666 = OpLoad %bool %d
        %668 = OpGroupNonUniformBroadcast %bool %uint_3 %666 %uint_120
        %669 = OpAccessChain %_ptr_Function_bool %ops %int_120
               OpStore %669 %668
        %671 = OpLoad %bool %d
        %673 = OpGroupNonUniformBroadcast %bool %uint_3 %671 %uint_121
        %674 = OpAccessChain %_ptr_Function_bool %ops %int_121
               OpStore %674 %673
        %676 = OpLoad %bool %d
        %678 = OpGroupNonUniformBroadcast %bool %uint_3 %676 %uint_122
        %679 = OpAccessChain %_ptr_Function_bool %ops %int_122
               OpStore %679 %678
        %681 = OpLoad %bool %d
        %683 = OpGroupNonUniformBroadcast %bool %uint_3 %681 %uint_123
        %684 = OpAccessChain %_ptr_Function_bool %ops %int_123
               OpStore %684 %683
        %686 = OpLoad %bool %d
        %688 = OpGroupNonUniformBroadcast %bool %uint_3 %686 %uint_124
        %689 = OpAccessChain %_ptr_Function_bool %ops %int_124
               OpStore %689 %688
        %691 = OpLoad %bool %d
        %693 = OpGroupNonUniformBroadcast %bool %uint_3 %691 %uint_125
        %694 = OpAccessChain %_ptr_Function_bool %ops %int_125
               OpStore %694 %693
        %696 = OpLoad %bool %d
        %698 = OpGroupNonUniformBroadcast %bool %uint_3 %696 %uint_126
        %699 = OpAccessChain %_ptr_Function_bool %ops %int_126
               OpStore %699 %698
        %701 = OpLoad %bool %d
        %703 = OpGroupNonUniformBroadcast %bool %uint_3 %701 %uint_127
        %704 = OpAccessChain %_ptr_Function_bool %ops %int_127
               OpStore %704 %703
               OpStore %id %int_0
               OpBranch %707
        %707 = OpLabel
               OpLoopMerge %709 %710 None
               OpBranch %711
        %711 = OpLabel
        %712 = OpLoad %int %id
        %713 = OpBitcast %uint %712
        %714 = OpLoad %uint %sgSize
        %715 = OpULessThan %bool %713 %714
               OpBranchConditional %715 %708 %709
        %708 = OpLabel
        %716 = OpLoad %v4uint %mask
        %717 = OpLoad %int %id
        %718 = OpBitcast %uint %717
        %719 = OpGroupNonUniformBallotBitExtract %bool %uint_3 %716 %718
               OpSelectionMerge %721 None
               OpBranchConditional %719 %720 %721
        %720 = OpLabel
        %722 = OpLoad %int %id
        %723 = OpAccessChain %_ptr_Function_bool %ops %722
        %724 = OpLoad %bool %723
        %725 = OpLoad %int %id
        %726 = OpAccessChain %_ptr_StorageBuffer_uint %_ %int_0 %725
        %727 = OpLoad %uint %726
        %728 = OpINotEqual %bool %727 %uint_0
        %729 = OpLogicalNotEqual %bool %724 %728
               OpBranch %721
        %721 = OpLabel
        %730 = OpPhi %bool %719 %708 %729 %720
               OpSelectionMerge %732 None
               OpBranchConditional %730 %731 %732
        %731 = OpLabel
               OpStore %tempRes %uint_0
               OpBranch %732
        %732 = OpLabel
               OpBranch %710
        %710 = OpLabel
        %733 = OpLoad %int %id
        %734 = OpIAdd %int %733 %int_1
               OpStore %id %734
               OpBranch %707
        %709 = OpLabel
        %739 = OpLoad %uint %offset
        %740 = OpLoad %uint %tempRes
        %741 = OpAccessChain %_ptr_StorageBuffer_uint %__0 %int_0 %739
               OpStore %741 %740
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The host creates a `uint` result storage buffer and one initialized input resource. Compute and mesh use `std430`; framebuffer variants use a `std140` uniform buffer because the tested stage does not write an SSBO.
- Compute and mesh helpers run seven local-size shapes, including one invocation, dimensions equal to the subgroup size, common rectangular shapes, and `3 x 5 x 7`. Each dispatch uses `4 x 2 x 2` workgroups.
- Required-size cases attach the requested subgroup size to pipeline creation after support checks confirm the feature, range, and stage.
- After execution, a shader-write to host-read barrier is recorded, the queue is submitted and waited, and mapped result memory is invalidated.
- `checkComputeOrMesh` scans the product of workgroup and local dimensions. Graphics and framebuffer callbacks scan their produced width. Every checked value must equal `3`.
- Any failed local-size or stage iteration increments the failure count, and any nonzero failure count returns `Failed!`.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `subgroupbroadcast` | Constant source invocation selection or broadcast value propagation is incorrect for an active source lane. |
| `subgroupbroadcast_nonconst` | Dynamic source ID handling, dynamically uniform ID recognition, or broadcast value propagation is incorrect. |
| `subgroupbroadcastfirst` | First-active invocation selection or active-set tracking in divergent control flow is incorrect. |

All values can also expose incorrect data-type lowering, stage-specific subgroup support, required subgroup-size handling, or result transport and readback.

### Cause Analysis

#### Constant source invocation selection or propagation

**Possible failure symptoms:** one or more result elements are `0` because a broadcast from an active constant source ID differs from `data[id]`.

**Possible implementation causes:** `OpGroupNonUniformBroadcast` may select the wrong invocation, propagate the wrong scalar or composite value, or be lowered incorrectly for a tested data type or shader stage.

#### Dynamic source ID handling

**Possible failure symptoms:** constant-ID cases pass, but `subgroupbroadcast_nonconst` produces `0` for ordinary loop IDs or for the ID that is uniform only among active invocations in the branch.

**Possible implementation causes:** SPIR-V 1.5 dynamic `Id` handling may be compiled or executed as if the operand had to be a compile-time constant, or dynamically uniform analysis may not respect the active invocation set. Vulkan permits a dynamically uniform `Id` only when `subgroupBroadcastDynamicId` is enabled.

#### First-active invocation selection

**Possible failure symptoms:** result bit 0 remains clear after the initial first-active check, or bit 1 remains clear for a non-first invocation after the control-flow-modified check, so the host observes a value other than `3`. The original first invocation sets bit 1 directly because it does not execute the second broadcast.

**Possible implementation causes:** first-active selection may use the wrong active invocation, or active-mask tracking in divergent control flow may not reflect that the original first invocation is excluded from the second ballot and broadcast.

#### Shared type, stage, size, or transport failure

**Possible failure symptoms:** all operations fail only for one data type, stage path, local-size shape, required subgroup size, or output mechanism.

**Possible implementation causes:** subgroup operation lowering may mishandle that type or stage, pipeline subgroup-size control may not produce the requested execution shape, or shader result writes and framebuffer copyback may not reach the host-visible data scanned by the common checker. Source-level investigation is needed to distinguish these mechanisms from the failing case pattern.

## Case Pruning

### Requirement-based pruning

- The device must support Vulkan subgroup operations, the ballot feature bit, the selected shader stage, and the selected data type.
- The extension branch requires `VK_EXT_shader_subgroup_ballot` and 64-bit integers.
- Dynamic-ID cases require `subgroupBroadcastDynamicId`.
- Required subgroup-size cases require `VK_EXT_subgroup_size_control`, `subgroupSizeControl`, `computeFullSubgroups`, an in-range size, and stage membership in `requiredSubgroupSizeStages`.
- Ray-tracing and mesh paths require their respective extensions and stage features. Unsupported optional stages are skipped, while compute subgroup support is required.
- Framebuffer tests using 8-bit or 16-bit input types require the matching uniform-buffer storage support.

### Design-based pruning

- Legacy extension cases omit vectors, Boolean values, doubles, and non-32-bit scalar formats because the tested extension functions are registered only for scalar `int`, `uint`, and `float`.
- Ray-tracing registration uses a smaller explicit format inventory than the general stage paths.
- Required subgroup-size leaves are generated only for compute and mesh paths and only for power-of-two values from 1 through 128.
- The family does not register a fragment-only framebuffer case; framebuffer coverage uses vertex, tessellation control, tessellation evaluation, and geometry stages.

## Key Takeaways

- The operation prefix is the main behavior axis: constant source ID, dynamic source ID, or first active invocation.
- A result of `3` means every operation-specific check succeeded for that shader invocation; the host requires `3` in every produced element and every harness iteration.
- The constant-ID representative emits all source IDs explicitly, then uses the ballot mask and runtime subgroup size to avoid checking undefined inactive sources.
- The dynamic case specifically tests the Vulkan 1.2 `subgroupBroadcastDynamicId` contract with SPIR-V 1.5.
- The first-active case checks active-mask changes: every invocation checks the initial first active value, while the non-first invocations repeat the operation in a branch that excludes the original first invocation.
- See `## Failure Meaning` for how a failing operation, type, stage, or subgroup-size pattern narrows the likely cause.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Operation and extension selection | [`getOpTypeCaseName`, `getExtHeader`](../../../modules/vulkan/subgroups/vktSubgroupsBallotBroadcastTests.cpp#L77-L99) | Defines registered prefixes and core versus ARB shader headers. |
| Generated test body | [`getTestSrc`](../../../modules/vulkan/subgroups/vktSubgroupsBallotBroadcastTests.cpp#L101-L207) | Emits constant-ID, dynamic-ID, and first-active validation logic. |
| Program builder | [`initPrograms`](../../../modules/vulkan/subgroups/vktSubgroupsBallotBroadcastTests.cpp#L242-L262) | Selects SPIR-V 1.3, 1.4, or 1.5 and invokes the shared generator. |
| Support checks | [`supportedCheck`](../../../modules/vulkan/subgroups/vktSubgroupsBallotBroadcastTests.cpp#L264-L347) | Applies subgroup, format, extension, stage, and subgroup-size requirements. |
| Runtime routing | [`test`](../../../modules/vulkan/subgroups/vktSubgroupsBallotBroadcastTests.cpp#L379-L454) | Defines input resources and selects each execution helper. |
| Registration | [`createSubgroupsBallotBroadcastTests`](../../../modules/vulkan/subgroups/vktSubgroupsBallotBroadcastTests.cpp#L461-L693) | Generates the operation, type, stage, extension, and size matrix. |
| Shared shader wrappers | [`initStdPrograms`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L1406-L1675) | Builds compute, graphics, mesh, task, and ray-tracing GLSL. |
| Compute and mesh execution | [`makeComputeOrMeshTestRequiredSubgroupSize`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L3762-L4063) | Creates resources and pipelines, executes local-size variants, synchronizes, and reads results. |
| Common result checks | [`check`, `checkComputeOrMesh`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L2640-L2663) | Requires every result element to equal the reference value. |
| Mustpass hierarchy | [`subgroups.txt`](../../../mustpass/main/vk-default/subgroups.txt#L12111) | Confirms the representative executable and registered family prefix. |
| Subgroup and ballot semantics | [`shaders.adoc`](../../../../vulkan-docs/src/chapters/shaders.adoc#L3447-L3523) | Defines subgroup group operations and ballot broadcast behavior. |
| Dynamic broadcast IDs | [`features.adoc`](../../../../vulkan-docs/src/chapters/features.adoc#L951-L957) | Defines constant and dynamically uniform source-ID support. |
| SPIR-V runtime rule | [`spirvenv.adoc`](../../../../vulkan-docs/src/appendices/spirvenv.adoc#L1244-L1250) | Connects dynamic broadcast IDs to the feature and SPIR-V 1.5. |
| Legacy extension | [`VK_EXT_shader_subgroup_ballot.adoc`](../../../../vulkan-docs/src/appendices/VK_EXT_shader_subgroup_ballot.adoc#L21-L79) | Defines ARB mappings and their relationship to core subgroup operations. |
