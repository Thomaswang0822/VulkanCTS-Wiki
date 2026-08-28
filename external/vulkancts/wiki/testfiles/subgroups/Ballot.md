## Overview

**Core question:** Do core and legacy ballot operations produce the required true-predicate and false-predicate results in every tested shader execution path?

- This page covers the `subgroups.ballot` test family implemented by [`vktSubgroupsBallotTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsBallotTests.cpp#L1).
- The tests run ballot checks in compute, graphics, framebuffer, ray tracing, task, and mesh shader paths supported by the device.
- Core cases use `subgroupBallot` or direct `OpGroupNonUniformBallot`. Generated legacy cases use `ballotARB`, while legacy framebuffer cases use direct `OpSubgroupBallotKHR`; all legacy cases require the `VK_EXT_shader_subgroup_ballot` path.
- Every shader records three check bits. The host accepts only `0x7`, which means all three checks passed.

## Background Knowledge

For the shared concepts subgroup identity, active invocations, ballots, and masks, see [Background Knowledge](../../categories/subgroups.md#background-knowledge) of the `subgroups` page.

- `VK_SUBGROUP_FEATURE_BALLOT_BIT` means the device accepts SPIR-V with the `GroupNonUniformBallot` capability. The older `VK_EXT_shader_subgroup_ballot` interface maps `ballotARB` to `OpSubgroupBallotKHR` and uses a 64-bit mask.

## Registration Hierarchy

```text
subgroups.ballot
├── graphics
├── compute
├── framebuffer
├── ray_tracing
├── mesh
└── ext_shader_subgroup_ballot
```

`ray_tracing` and `mesh` are not registered in Vulkan SC. The `ext_shader_subgroup_ballot` test family contains its own `graphics`, `compute`, `framebuffer`, and `mesh` intermediate nodes.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Execution path | `compute`, `graphics`, `framebuffer`, `ray_tracing`, `mesh` | Selects the shader stages, pipeline helper, result transport, and whether the shader compares against a shared-memory reference mask. | [`createSubgroupsBallotTests`](../../../modules/vulkan/subgroups/vktSubgroupsBallotTests.cpp#L1019-L1157) |
| Ballot interface | `core`, `ext_shader_subgroup_ballot` | Selects core `subgroupBallot` / `OpGroupNonUniformBallot` or the legacy interface. Generated legacy shaders use `ballotARB` with a `uint64_t` result; legacy framebuffer shaders use direct `OpSubgroupBallotKHR` with a four-component 32-bit result. | [`getExtHeader` and `getBodySource`](../../../modules/vulkan/subgroups/vktSubgroupsBallotTests.cpp#L762-L807) and [`initFrameBufferPrograms`](../../../modules/vulkan/subgroups/vktSubgroupsBallotTests.cpp#L64-L760) |
| Required subgroup size | ordinary case, `_requiredsubgroupsize` | Ordinary cases use the default subgroup behavior. Required-size compute and mesh cases iterate over every supported power-of-two size. | [`test`](../../../modules/vulkan/subgroups/vktSubgroupsBallotTests.cpp#L920-L975) |
| Shader stage | all supported graphics stages, framebuffer vertex-pipeline stages, ray tracing stages, `task`, `mesh`, `compute` | Extends the same ballot contract across the execution models supported by the implementation. | [`createSubgroupsBallotTests`](../../../modules/vulkan/subgroups/vktSubgroupsBallotTests.cpp#L1021-L1142) |
| Predicate | literal `true`, nonzero input, literal `false` | Produces result bits `0x1`, `0x2`, and `0x4`. | [`getBodySource`](../../../modules/vulkan/subgroups/vktSubgroupsBallotTests.cpp#L770-L807) |

The default mustpass list contains 23 executable ballot cases, from [`dEQP-VK.subgroups.ballot.compute.compute`](../../../mustpass/main/vk-default/subgroups.txt#L12088) through [`dEQP-VK.subgroups.ballot.ray_tracing.test`](../../../mustpass/main/vk-default/subgroups.txt#L12110).

## Behavior Parameters

The primary behavior parameter is **execution path**. It changes how ballot behavior is exercised and how results reach the host.

### `compute`: independent mask comparison

The compute shader constructs a reference ballot in workgroup shared memory. One elected invocation clears the subgroup's `uvec4`, voting invocations set their own bits with `atomicOr`, and subgroup-scoped memory barriers for shared-memory accesses surround the atomic phase. The shader compares this mask with `subgroupBallot` or `ballotARB` for the all-true and input-derived predicates.

### `graphics`: supported graphics stages

The test generates vertex, tessellation control, tessellation evaluation, geometry, and fragment shaders, then runs the ballot body in every graphics stage where subgroup operations are supported. Each tested stage writes a result that the shared graphics harness scans for `0x7`.

### `framebuffer`: direct SPIR-V vertex-pipeline stages

The framebuffer cases use CTS-authored SPIR-V 1.3 for vertex, tessellation control, tessellation evaluation, or geometry execution. They check that true predicates produce nonzero masks and that the false predicate produces zero, then pass the three-bit result through framebuffer output for host validation.

### `ray_tracing`: supported ray tracing stages

The ray tracing case generates programs for the supported ray generation, any-hit, closest-hit, miss, intersection, and callable stages. Each tested stage applies the same nonzero/zero ballot checks and writes to the common result buffer. This path is not present in Vulkan SC and has no legacy extension counterpart.

### `mesh`: task or mesh execution

Task and mesh shaders use output-buffer validation, checking that both true predicates produce nonzero ballot masks and that the false predicate produces zero. Both ordinary and required-subgroup-size leaves are registered for core and legacy interfaces when mesh shading is available.

The second behavior parameter is **ballot interface**. It changes the source extension, mask type, and SPIR-V operation while retaining the same predicate checks.

### `core`: `subgroupBallot`

Core cases enable `GL_KHR_shader_subgroup_ballot`, use a four-component 32-bit mask, and compile to `OpGroupNonUniformBallot`. Support requires `VK_SUBGROUP_FEATURE_BALLOT_BIT`.

### `ext_shader_subgroup_ballot`: `ballotARB`

Generated legacy cases enable `GL_ARB_shader_ballot`, `GL_ARB_gpu_shader_int64`, and `GL_KHR_shader_subgroup_basic`. They test 64-bit `ballotARB` results, which map to `OpSubgroupBallotKHR`. Legacy framebuffer cases instead execute CTS-authored `OpSubgroupBallotKHR` directly with a four-component 32-bit result. All legacy cases additionally require `VK_EXT_shader_subgroup_ballot` and `shaderInt64`.

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.subgroups.ballot.compute.compute
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `compute` execution path | Uses the compute wrapper, shared-memory reference ballot, storage buffers, and host scan over every global invocation. |
| Core ballot interface | Uses `GL_KHR_shader_subgroup_ballot`, `uvec4`, and `subgroupBallot`. |
| Ordinary subgroup size | Uses the default `compute` leaf rather than `compute_requiredsubgroupsize`; local size still varies across the harness matrix. |
| Nonzero `uint` input | Makes `data[gl_SubgroupInvocationID] != 0` true for every active invocation. |

#### Purpose

This shader compares core `subgroupBallot` results with an independently assembled shared-memory mask for two true predicates, then verifies that an all-false ballot is zero.

#### Structural Design

| Phase | Device-side action | Success bit |
|-------|--------------------|-------------|
| Reference initialization | One elected invocation clears the subgroup's shared `uvec4`, followed by a subgroup-scoped memory barrier for shared-memory accesses. | none |
| Reference voting | Each true-voting invocation atomically sets its `gl_SubgroupInvocationID` bit, followed by another such memory barrier. | none |
| All-true comparison | Compare the shared reference with `subgroupBallot(true)`. | `0x1` |
| Input-derived comparison | Compare the shared reference with `subgroupBallot(data[gl_SubgroupInvocationID] != 0)`. | `0x2` |
| All-false check | Require `subgroupBallot(false)` to equal `uvec4(0)`. | `0x4` |
| Result write | Store the OR of all success bits at the linearized global invocation offset. | expected `0x7` |

#### Shader Code

```glsl
#version 450
#extension GL_KHR_shader_subgroup_ballot: enable
layout (local_size_x_id = 0, local_size_y_id = 1, local_size_z_id = 2) in;
/// Binding 0 is a std430 result buffer with one uint per global invocation. Each invocation writes 0x7 only when all three ballot checks pass.
layout(set = 0, binding = 0, std430) buffer Buffer1
{
  uint result[];
};
/// Binding 1 is a std430 input buffer initialized by the host with 128 nonzero uint values, one for every possible subgroup-local index used by the test.
layout(set = 0, binding = 1, std430) buffer Buffer2
{
  uint data[];
};
/// This workgroup-shared array stores an independently assembled ballot mask for each subgroup in the workgroup.
shared uvec4 superSecretComputeShaderHelper[gl_WorkGroupSize.x * gl_WorkGroupSize.y * gl_WorkGroupSize.z];
uvec4 sharedMemoryBallot(bool vote)
{
  uint groupOffset = gl_SubgroupID;
  // One invocation in the group 0's the whole group's data
  if (subgroupElect())
  {
    superSecretComputeShaderHelper[groupOffset] = uvec4(0);
  }
  subgroupMemoryBarrierShared();
  if (vote)
  {
    const highp uint invocationId = gl_SubgroupInvocationID % 32;
    const highp uint bitToSet = 1u << invocationId;
    switch (gl_SubgroupInvocationID / 32)
    {
    case 0: atomicOr(superSecretComputeShaderHelper[groupOffset].x, bitToSet); break;
    case 1: atomicOr(superSecretComputeShaderHelper[groupOffset].y, bitToSet); break;
    case 2: atomicOr(superSecretComputeShaderHelper[groupOffset].z, bitToSet); break;
    case 3: atomicOr(superSecretComputeShaderHelper[groupOffset].w, bitToSet); break;
    }
  }
  subgroupMemoryBarrierShared();
  return superSecretComputeShaderHelper[groupOffset];
}
void main (void)
{
  uvec3 globalSize = gl_NumWorkGroups * gl_WorkGroupSize;
  highp uint offset = globalSize.x * ((globalSize.y * gl_GlobalInvocationID.z) + gl_GlobalInvocationID.y) + gl_GlobalInvocationID.x;
  uint tempRes;
  /// Bits 0 and 1 require the built-in ballot mask to match the shared-memory reference for all-true and input-derived predicates.
  uint tempResult = 0;
  tempResult |= sharedMemoryBallot(true) == subgroupBallot(true) ? 0x1 : 0;
  bool bData = data[gl_SubgroupInvocationID] != 0;
  tempResult |= sharedMemoryBallot(bData) == subgroupBallot(bData) ? 0x2 : 0;
  /// Bit 2 requires the all-false ballot to be exactly zero.
  tempResult |= uvec4(0) == subgroupBallot(false) ? 0x4 : 0;
  tempRes = tempResult;
  result[offset] = tempRes;
}

```

#### Additional Info

- `initPrograms` explicitly requests SPIR-V 1.3 for this compute case. Ray tracing and mesh cases instead request SPIR-V 1.4.
- The helper array length is the specialized workgroup volume. It is intentionally larger than the number of subgroups, so indexing by `gl_SubgroupID` stays within the allocation.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Ballot interface | Generated legacy wrappers replace the core extension and `subgroupBallot` with `GL_ARB_shader_ballot`, `uint64_t`, and `ballotARB`; the shared helper returns a packed 64-bit mask. Legacy framebuffer variants instead use CTS-authored direct `OpSubgroupBallotKHR` with a four-component 32-bit result. | [`getExtHeader`, `getBodySource`, and helper selection`](../../../modules/vulkan/subgroups/vktSubgroupsBallotTests.cpp#L762-L827) and [`initFrameBufferPrograms`](../../../modules/vulkan/subgroups/vktSubgroupsBallotTests.cpp#L64-L760) |
| Execution path | Graphics, ray tracing, and mesh/task wrappers omit the shared reference helper and test nonzero true-predicate masks; only the compute wrapper uses the shared reference helper. | [`getBodySource` and helper selection](../../../modules/vulkan/subgroups/vktSubgroupsBallotTests.cpp#L770-L827) and [`initStdPrograms`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L1406-L1671) |
| Required subgroup size | The shader text is unchanged, but pipeline creation supplies each supported required subgroup size and the harness reruns its local-size matrix. | [`test`](../../../modules/vulkan/subgroups/vktSubgroupsBallotTests.cpp#L941-L974) and [`makeComputeOrMeshTest`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L4090-L4109) |
| Local workgroup size | Specialization constants 0, 1, and 2 set `gl_WorkGroupSize`; this changes shared-array size, invocation layout, and result count without changing ballot logic. | [`initStdPrograms`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L1415-L1434) and [`makeComputeOrMeshTest`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L4090-L4104) |

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
; Bound: 166
; Schema: 0
               OpCapability Shader
               OpCapability GroupNonUniform
               OpCapability GroupNonUniformBallot
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_SubgroupID %gl_SubgroupInvocationID %gl_NumWorkGroups %gl_GlobalInvocationID
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpSourceExtension "GL_KHR_shader_subgroup_ballot"
               OpSourceExtension "GL_KHR_shader_subgroup_basic"
               OpName %main "main"
               OpName %sharedMemoryBallot_b1_ "sharedMemoryBallot(b1;"
               OpName %vote "vote"
               OpName %groupOffset "groupOffset"
               OpName %gl_SubgroupID "gl_SubgroupID"
               OpName %superSecretComputeShaderHelper "superSecretComputeShaderHelper"
               OpName %invocationId "invocationId"
               OpName %gl_SubgroupInvocationID "gl_SubgroupInvocationID"
               OpName %bitToSet "bitToSet"
               OpName %globalSize "globalSize"
               OpName %gl_NumWorkGroups "gl_NumWorkGroups"
               OpName %offset "offset"
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
               OpName %tempResult "tempResult"
               OpName %param "param"
               OpName %bData "bData"
               OpName %Buffer2 "Buffer2"
               OpMemberName %Buffer2 0 "data"
               OpName %_ ""
               OpName %param_0 "param"
               OpName %tempRes "tempRes"
               OpName %Buffer1 "Buffer1"
               OpMemberName %Buffer1 0 "result"
               OpName %__0 ""
               OpDecorate %gl_SubgroupID BuiltIn SubgroupId
               OpDecorate %23 SpecId 0
               OpDecorate %24 SpecId 1
               OpDecorate %25 SpecId 2
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
               OpDecorate %gl_SubgroupInvocationID RelaxedPrecision
               OpDecorate %gl_SubgroupInvocationID BuiltIn SubgroupLocalInvocationId
               OpDecorate %49 RelaxedPrecision
               OpDecorate %51 RelaxedPrecision
               OpDecorate %55 RelaxedPrecision
               OpDecorate %56 RelaxedPrecision
               OpDecorate %gl_NumWorkGroups BuiltIn NumWorkgroups
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %_runtimearr_uint ArrayStride 4
               OpDecorate %Buffer2 Block
               OpMemberDecorate %Buffer2 0 Offset 0
               OpDecorate %_ Binding 1
               OpDecorate %_ DescriptorSet 0
               OpDecorate %131 RelaxedPrecision
               OpDecorate %_runtimearr_uint_0 ArrayStride 4
               OpDecorate %Buffer1 Block
               OpMemberDecorate %Buffer1 0 Offset 0
               OpDecorate %__0 Binding 0
               OpDecorate %__0 DescriptorSet 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %bool = OpTypeBool
%_ptr_Function_bool = OpTypePointer Function %bool
       %uint = OpTypeInt 32 0
     %v4uint = OpTypeVector %uint 4
         %10 = OpTypeFunction %v4uint %_ptr_Function_bool
%_ptr_Function_uint = OpTypePointer Function %uint
%_ptr_Input_uint = OpTypePointer Input %uint
%gl_SubgroupID = OpVariable %_ptr_Input_uint Input
     %uint_3 = OpConstant %uint 3
         %23 = OpSpecConstant %uint 1
         %24 = OpSpecConstant %uint 1
         %25 = OpSpecConstant %uint 1
     %v3uint = OpTypeVector %uint 3
%gl_WorkGroupSize = OpSpecConstantComposite %v3uint %23 %24 %25
     %uint_0 = OpConstant %uint 0
         %29 = OpSpecConstantOp %uint CompositeExtract %gl_WorkGroupSize 0
     %uint_1 = OpConstant %uint 1
         %31 = OpSpecConstantOp %uint CompositeExtract %gl_WorkGroupSize 1
         %32 = OpSpecConstantOp %uint IMul %29 %31
     %uint_2 = OpConstant %uint 2
         %34 = OpSpecConstantOp %uint CompositeExtract %gl_WorkGroupSize 2
         %35 = OpSpecConstantOp %uint IMul %32 %34
%_arr_v4uint_35 = OpTypeArray %v4uint %35
%_ptr_Workgroup__arr_v4uint_35 = OpTypePointer Workgroup %_arr_v4uint_35
%superSecretComputeShaderHelper = OpVariable %_ptr_Workgroup__arr_v4uint_35 Workgroup
         %40 = OpConstantComposite %v4uint %uint_0 %uint_0 %uint_0 %uint_0
%_ptr_Workgroup_v4uint = OpTypePointer Workgroup %v4uint
   %uint_264 = OpConstant %uint 264
%gl_SubgroupInvocationID = OpVariable %_ptr_Input_uint Input
    %uint_32 = OpConstant %uint 32
%_ptr_Workgroup_uint = OpTypePointer Workgroup %uint
%_ptr_Function_v3uint = OpTypePointer Function %v3uint
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_NumWorkGroups = OpVariable %_ptr_Input_v3uint Input
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
       %true = OpConstantTrue %bool
     %v4bool = OpTypeVector %bool 4
        %int = OpTypeInt 32 1
      %int_1 = OpConstant %int 1
      %int_0 = OpConstant %int 0
%_runtimearr_uint = OpTypeRuntimeArray %uint
    %Buffer2 = OpTypeStruct %_runtimearr_uint
%_ptr_StorageBuffer_Buffer2 = OpTypePointer StorageBuffer %Buffer2
          %_ = OpVariable %_ptr_StorageBuffer_Buffer2 StorageBuffer
%_ptr_StorageBuffer_uint = OpTypePointer StorageBuffer %uint
      %int_2 = OpConstant %int 2
      %false = OpConstantFalse %bool
      %int_4 = OpConstant %int 4
%_runtimearr_uint_0 = OpTypeRuntimeArray %uint
    %Buffer1 = OpTypeStruct %_runtimearr_uint_0
%_ptr_StorageBuffer_Buffer1 = OpTypePointer StorageBuffer %Buffer1
        %__0 = OpVariable %_ptr_StorageBuffer_Buffer1 StorageBuffer
       %main = OpFunction %void None %3
          %5 = OpLabel
 %globalSize = OpVariable %_ptr_Function_v3uint Function
     %offset = OpVariable %_ptr_Function_uint Function
 %tempResult = OpVariable %_ptr_Function_uint Function
      %param = OpVariable %_ptr_Function_bool Function
      %bData = OpVariable %_ptr_Function_bool Function
    %param_0 = OpVariable %_ptr_Function_bool Function
    %tempRes = OpVariable %_ptr_Function_uint Function
         %93 = OpLoad %v3uint %gl_NumWorkGroups
         %94 = OpIMul %v3uint %93 %gl_WorkGroupSize
               OpStore %globalSize %94
         %96 = OpAccessChain %_ptr_Function_uint %globalSize %uint_0
         %97 = OpLoad %uint %96
         %98 = OpAccessChain %_ptr_Function_uint %globalSize %uint_1
         %99 = OpLoad %uint %98
        %101 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_2
        %102 = OpLoad %uint %101
        %103 = OpIMul %uint %99 %102
        %104 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_1
        %105 = OpLoad %uint %104
        %106 = OpIAdd %uint %103 %105
        %107 = OpIMul %uint %97 %106
        %108 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
        %109 = OpLoad %uint %108
        %110 = OpIAdd %uint %107 %109
               OpStore %offset %110
               OpStore %tempResult %uint_0
               OpStore %param %true
        %114 = OpFunctionCall %v4uint %sharedMemoryBallot_b1_ %param
        %115 = OpGroupNonUniformBallot %v4uint %uint_3 %true
        %117 = OpIEqual %v4bool %114 %115
        %118 = OpAll %bool %117
        %122 = OpSelect %int %118 %int_1 %int_0
        %123 = OpBitcast %uint %122
        %124 = OpLoad %uint %tempResult
        %125 = OpBitwiseOr %uint %124 %123
               OpStore %tempResult %125
        %131 = OpLoad %uint %gl_SubgroupInvocationID
        %133 = OpAccessChain %_ptr_StorageBuffer_uint %_ %int_0 %131
        %134 = OpLoad %uint %133
        %135 = OpINotEqual %bool %134 %uint_0
               OpStore %bData %135
        %137 = OpLoad %bool %bData
               OpStore %param_0 %137
        %138 = OpFunctionCall %v4uint %sharedMemoryBallot_b1_ %param_0
        %139 = OpLoad %bool %bData
        %140 = OpGroupNonUniformBallot %v4uint %uint_3 %139
        %141 = OpIEqual %v4bool %138 %140
        %142 = OpAll %bool %141
        %144 = OpSelect %int %142 %int_2 %int_0
        %145 = OpBitcast %uint %144
        %146 = OpLoad %uint %tempResult
        %147 = OpBitwiseOr %uint %146 %145
               OpStore %tempResult %147
        %149 = OpGroupNonUniformBallot %v4uint %uint_3 %false
        %150 = OpIEqual %v4bool %40 %149
        %151 = OpAll %bool %150
        %153 = OpSelect %int %151 %int_4 %int_0
        %154 = OpBitcast %uint %153
        %155 = OpLoad %uint %tempResult
        %156 = OpBitwiseOr %uint %155 %154
               OpStore %tempResult %156
        %158 = OpLoad %uint %tempResult
               OpStore %tempRes %158
        %163 = OpLoad %uint %offset
        %164 = OpLoad %uint %tempRes
        %165 = OpAccessChain %_ptr_StorageBuffer_uint %__0 %int_0 %163
               OpStore %165 %164
               OpReturn
               OpFunctionEnd
%sharedMemoryBallot_b1_ = OpFunction %v4uint None %10
       %vote = OpFunctionParameter %_ptr_Function_bool
         %13 = OpLabel
%groupOffset = OpVariable %_ptr_Function_uint Function
%invocationId = OpVariable %_ptr_Function_uint Function
   %bitToSet = OpVariable %_ptr_Function_uint Function
         %18 = OpLoad %uint %gl_SubgroupID
               OpStore %groupOffset %18
         %20 = OpGroupNonUniformElect %bool %uint_3
               OpSelectionMerge %22 None
               OpBranchConditional %20 %21 %22
         %21 = OpLabel
         %39 = OpLoad %uint %groupOffset
         %42 = OpAccessChain %_ptr_Workgroup_v4uint %superSecretComputeShaderHelper %39
               OpStore %42 %40
               OpBranch %22
         %22 = OpLabel
               OpMemoryBarrier %uint_3 %uint_264
         %44 = OpLoad %bool %vote
               OpSelectionMerge %46 None
               OpBranchConditional %44 %45 %46
         %45 = OpLabel
         %49 = OpLoad %uint %gl_SubgroupInvocationID
         %51 = OpUMod %uint %49 %uint_32
               OpStore %invocationId %51
         %53 = OpLoad %uint %invocationId
         %54 = OpShiftLeftLogical %uint %uint_1 %53
               OpStore %bitToSet %54
         %55 = OpLoad %uint %gl_SubgroupInvocationID
         %56 = OpUDiv %uint %55 %uint_32
               OpSelectionMerge %61 None
               OpSwitch %56 %61 0 %57 1 %58 2 %59 3 %60
         %57 = OpLabel
         %62 = OpLoad %uint %groupOffset
         %64 = OpAccessChain %_ptr_Workgroup_uint %superSecretComputeShaderHelper %62 %uint_0
         %65 = OpLoad %uint %bitToSet
         %66 = OpAtomicOr %uint %64 %uint_1 %uint_0 %65
               OpBranch %61
         %58 = OpLabel
         %68 = OpLoad %uint %groupOffset
         %69 = OpAccessChain %_ptr_Workgroup_uint %superSecretComputeShaderHelper %68 %uint_1
         %70 = OpLoad %uint %bitToSet
         %71 = OpAtomicOr %uint %69 %uint_1 %uint_0 %70
               OpBranch %61
         %59 = OpLabel
         %73 = OpLoad %uint %groupOffset
         %74 = OpAccessChain %_ptr_Workgroup_uint %superSecretComputeShaderHelper %73 %uint_2
         %75 = OpLoad %uint %bitToSet
         %76 = OpAtomicOr %uint %74 %uint_1 %uint_0 %75
               OpBranch %61
         %60 = OpLabel
         %78 = OpLoad %uint %groupOffset
         %79 = OpAccessChain %_ptr_Workgroup_uint %superSecretComputeShaderHelper %78 %uint_3
         %80 = OpLoad %uint %bitToSet
         %81 = OpAtomicOr %uint %79 %uint_1 %uint_0 %80
               OpBranch %61
         %61 = OpLabel
               OpBranch %46
         %46 = OpLabel
               OpMemoryBarrier %uint_3 %uint_264
         %84 = OpLoad %uint %groupOffset
         %85 = OpAccessChain %_ptr_Workgroup_v4uint %superSecretComputeShaderHelper %84
         %86 = OpLoad %v4uint %85
               OpReturnValue %86
               OpFunctionEnd

```

</details>

## Runtime Execution and Result Checking

- [`supportedCheck`](../../../modules/vulkan/subgroups/vktSubgroupsBallotTests.cpp#L830-L889) requires subgroup support, `VK_SUBGROUP_FEATURE_BALLOT_BIT`, and support for the selected shader stage. Legacy, required-size, ray tracing, and mesh cases add their own feature gates.
- The host creates a `uint` input containing 128 nonzero elements. Standard compute, graphics, ray tracing, and mesh paths bind it as a `std430` storage buffer. Framebuffer paths use a `std140` uniform buffer.
- Compute and mesh cases allocate a `VK_FORMAT_R32_UINT` result buffer and run seven local-size shapes. The dispatch grid is 4 by 2 by 2 workgroups. Required-size cases repeat this for each power-of-two size from `minSubgroupSize` through `maxSubgroupSize`.
- Graphics and ray tracing helpers run the generated ballot body in every applicable supported stage. Framebuffer helpers render the direct SPIR-V result through the selected vertex-pipeline stage.
- After execution, the harness makes shader writes visible to the host, invalidates mapped allocations, and calls the appropriate result callback.
- [`check`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L2640-L2653) rejects the case when any scanned value differs from `0x7`. [`checkComputeOrMesh`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L2655-L2663) derives the value count from workgroup and local sizes before applying the same rule.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `compute` | Incorrect subgroup ballot mask, shared-memory reference construction, compute specialization/local-size handling, or compute result write/readback. |
| `graphics` | Incorrect ballot behavior in one or more supported graphics stages, stage-specific result indexing, or graphics SSBO result handling. |
| `framebuffer` | Incorrect ballot instruction behavior in the selected vertex-pipeline stage, direct SPIR-V handling, or framebuffer output/readback. |
| `ray_tracing` | Incorrect ballot behavior in one or more supported ray tracing stages, stage-specific result writes, or ray tracing pipeline execution. |
| `mesh` | Incorrect ballot behavior in task/mesh execution, local-size or required-subgroup-size handling, or mesh result write/readback. |

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `core` | Incorrect lowering or execution of `subgroupBallot` / `OpGroupNonUniformBallot`, or incorrect reporting of core ballot support. |
| `ext_shader_subgroup_ballot` | Incorrect lowering or execution of `ballotARB` / `OpSubgroupBallotKHR`, generated-shader 64-bit mask handling, direct framebuffer SPIR-V handling, or incorrect extension and `shaderInt64` support behavior. |

### Cause Analysis

#### Core ballot mask failures

**Possible failure symptoms:** one or more result words lack `0x1` or `0x2`, or lack `0x4` because the all-false mask was nonzero. Compute and mesh failures can show a mismatch between `subgroupBallot` and the shared-memory reference.

**Possible implementation causes:** possible causes include incorrect lowering or execution of `OpGroupNonUniformBallot`, wrong active-invocation bit placement, or support properties that admit an unsupported ballot operation or stage.

#### Legacy ballot mask or 64-bit handling failures

**Possible failure symptoms:** only `ext_shader_subgroup_ballot` cases fail, with true-predicate comparisons or the zero-mask check producing values other than `0x7`.

**Possible implementation causes:** for generated legacy shaders, possible causes include incorrect `ballotARB` to `OpSubgroupBallotKHR` lowering or incorrect 64-bit ballot mask handling. Legacy framebuffer cases instead exercise CTS-authored `OpSubgroupBallotKHR` directly with a four-component 32-bit result. Inconsistent reporting and execution of `VK_EXT_shader_subgroup_ballot` or `shaderInt64` support can affect either path.

#### Shared-memory reference construction failures

**Possible failure symptoms:** compute cases fail the exact-mask `0x1` or `0x2` comparison while graphics, framebuffer, ray tracing, task, and mesh cases pass their nonzero/zero checks.

**Possible implementation causes:** possible causes include incorrect subgroup election, subgroup shared-memory barrier behavior, workgroup-shared atomic OR behavior, or handling of `gl_SubgroupID` and `gl_SubgroupInvocationID`. These mechanisms build the independent reference mask, so a failure does not by itself prove that the ballot instruction is wrong.

#### Execution-path result handling failures

**Possible failure symptoms:** failures are isolated to one path or stage even though the same ballot interface succeeds elsewhere. The host observes a missing or incorrect `0x7` result at one or more output positions.

**Possible implementation causes:** possible causes include incorrect stage-specific shader execution, result indexing, descriptor access, framebuffer transport, ray tracing stage routing, mesh/task dispatch, synchronization before host reads, or pipeline creation for the selected local and subgroup sizes. Source-level investigation is needed when the recorded result alone cannot distinguish these from a ballot failure.

## Case Pruning

### Requirement-based pruning

- Subgroup operations and `VK_SUBGROUP_FEATURE_BALLOT_BIT` are mandatory. Compute subgroup support is required by Vulkan; unsupported optional stages are skipped.
- Legacy cases require `VK_EXT_shader_subgroup_ballot` and 64-bit integer shader support.
- Required-size cases require subgroup size control, `computeFullSubgroups`, and inclusion of the selected stage in `requiredSubgroupSizeStages`.
- Ray tracing requires `VK_KHR_ray_tracing_pipeline`. Mesh and task cases require `VK_EXT_mesh_shader`; task cases also require the `taskShader` feature. These paths are omitted from Vulkan SC.
- Graphics, ray tracing, and mesh helpers limit execution to stages the device reports as supporting subgroup operations.

### Design-based pruning

- Required subgroup sizes are tested only for compute and mesh/task execution, where the harness supports full-subgroup and local-size coverage; compute uses exact shared-reference comparisons, while mesh/task uses nonzero/zero checks.
- The legacy branch has no ray tracing case. Registration creates only the core `ray_tracing.test` leaf.
- Framebuffer testing is limited to vertex, geometry, tessellation control, and tessellation evaluation stages. The common framebuffer harness supplies the fragment stage needed to capture output rather than treating it as another ballot leaf.
- The generated input has 128 elements because the subgroup utility defines 128 as its maximum supported subgroup size for these tests.
- `test-issues.txt` excludes no ballot case. Its subgroup-related entry applies only to partial `subgroup_uniform_control_flow` cases.

## Key Takeaways

- Every ballot case encodes three successful predicate checks as `0x7`; any other scanned value fails the case.
- Compute shaders compare ballot output with a mask assembled independently through subgroup-scoped shared memory and atomics.
- Graphics, framebuffer, ray tracing, task, and mesh paths check for a nonzero result from true predicates and a zero result from `false` across supported stages.
- Core and legacy paths exercise the same predicate-to-mask contract through different source types, extensions, and SPIR-V operations.
- Required-size leaves repeat compute-like testing across the device's advertised power-of-two subgroup-size range.
- See `Failure Meaning` to distinguish ballot-operation failures from reference-mask, stage execution, and result-transport failures.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Registration and test matrix | [`createSubgroupsBallotTests`](../../../modules/vulkan/subgroups/vktSubgroupsBallotTests.cpp#L1019-L1160) | Registers the direct hierarchy, executable leaves, interfaces, stages, and required-size variants. |
| Generated shader builder | [`initPrograms`](../../../modules/vulkan/subgroups/vktSubgroupsBallotTests.cpp#L809-L828) | Selects the exact extensions, test body, shared helper, shader stages, and SPIR-V target for the representative path. |
| Ballot source fragments | [`getExtHeader` and `getBodySource`](../../../modules/vulkan/subgroups/vktSubgroupsBallotTests.cpp#L762-L807) | Defines core versus legacy source and the three result bits. |
| Direct framebuffer programs | [`initFrameBufferPrograms`](../../../modules/vulkan/subgroups/vktSubgroupsBallotTests.cpp#L64-L760) | Provides SPIR-V 1.3 ballot shaders for vertex-pipeline framebuffer cases. |
| Feature checks | [`supportedCheck`](../../../modules/vulkan/subgroups/vktSubgroupsBallotTests.cpp#L830-L889) | Enforces operation, stage, extension, integer, size-control, ray tracing, and mesh requirements. |
| Runtime routing | [`test` and `noSSBOtest`](../../../modules/vulkan/subgroups/vktSubgroupsBallotTests.cpp#L891-L1012) | Selects resources and execution helpers for every path. |
| Shared ballot helpers | [`getSharedMemoryBallotHelper` and `getSharedMemoryBallotHelperARB`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L867-L925) | Build independent core and legacy reference masks. |
| Standard shader wrappers | [`initStdPrograms`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L1406-L1675) | Supplies stage-specific declarations, indexing, and result writes. |
| Compute and mesh runtime | [`makeComputeOrMeshTest`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L3830-L4113) | Binds resources, varies local sizes, dispatches work, synchronizes host reads, and invokes result checking. |
| Result comparison | [`check` and `checkComputeOrMesh`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L2640-L2663) | Requires every output value to equal `0x7`. |
| Default mustpass registration | [`subgroups.txt`](../../../mustpass/main/vk-default/subgroups.txt#L12088-L12110) | Confirms all 23 executable ballot paths documented here. |
| Ballot operation semantics | [`shaders.adoc`](../../../../vulkan-docs/src/chapters/shaders.adoc#L3447-L3523) | Defines subgroup group operations and ballot predicate-mask behavior. |
| Subgroup properties | [`limits.adoc`](../../../../vulkan-docs/src/chapters/limits.adoc#L1326-L1353) and [`limits.adoc`](../../../../vulkan-docs/src/chapters/limits.adoc#L1428-L1453) | Defines supported stages, supported operations, and the ballot feature bit. |
| Subgroup invocation built-ins | [`interfaces.adoc`](../../../../vulkan-docs/src/chapters/interfaces.adoc#L5123-L5237) | Defines subgroup-local invocation IDs, subgroup size, and full-subgroup behavior. |
| Legacy ballot extension | [`VK_EXT_shader_subgroup_ballot.adoc`](../../../../vulkan-docs/src/appendices/VK_EXT_shader_subgroup_ballot.adoc#L21-L79) | Defines the legacy extension, mask communication, and GLSL mapping. |
| Subgroup size control | [`VK_EXT_subgroup_size_control.adoc`](../../../../vulkan-docs/src/appendices/VK_EXT_subgroup_size_control.adoc#L24-L69) | Grounds the required-size range and full-subgroup variation. |
