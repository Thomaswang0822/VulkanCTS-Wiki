## Overview

**Core question:** Do ballot-derived subgroup operations return the right Boolean, count, prefix count, or set-bit index for controlled ballot masks?

- This page covers the `subgroups.ballot_other` test family implemented by `vktSubgroupsBallotOtherTests.cpp`.
- Seven test case leaves exercise inverse ballot, bit extraction, reduction count, inclusive and exclusive prefix counts, and least-significant and most-significant set-bit searches.
- The same operation checks run through compute, graphics, framebuffer, ray-tracing, mesh, and task shader paths where supported.
- Every tested invocation builds a four-bit verdict. The host requires every returned scalar to equal `0xf`.

## Background Knowledge

For the shared concepts ballots, masks, and collective result shapes, see [Background Knowledge](../../categories/subgroups.md#background-knowledge) of the `subgroups` page.

- **Valid invocation range.** `gl_SubgroupSize` gives the subgroup width. A mask can physically contain bits beyond that width, but they do not identify invocations in the subgroup. Several checks target this boundary directly.

## Registration Hierarchy

```text
subgroups.ballot_other
├── graphics
├── compute
├── framebuffer
├── ray_tracing
└── mesh
```

`ray_tracing` and `mesh` are not registered in Vulkan SC builds.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Operation test case leaf | `subgroupinverseballot`, `subgroupballotbitextract`, `subgroupballotbitcount`, `subgroupballotinclusivebitcount`, `subgroupballotexclusivebitcount`, `subgroupballotfindlsb`, `subgroupballotfindmsb` | Selects the ballot-derived operation, references, and boundary checks that produce the four-bit verdict. | [operation generation](../../../modules/vulkan/subgroups/vktSubgroupsBallotOtherTests.cpp#L41-L276) |
| Execution family | `graphics`, `compute`, `framebuffer`, `ray_tracing`, `mesh` | Selects the pipeline and result transport while keeping the same operation-specific check body. | [family registration](../../../modules/vulkan/subgroups/vktSubgroupsBallotOtherTests.cpp#L458-L569) |
| Required subgroup size | absent or `_requiredsubgroupsize` for compute, mesh, and task cases | The suffixed form repeats the operation for each supported power-of-two subgroup size in the advertised range. | [variant registration and runtime loop](../../../modules/vulkan/subgroups/vktSubgroupsBallotOtherTests.cpp#L487-L519) |
| Concrete shader stage | framebuffer: `_vertex`, `_tess_eval`, `_tess_control`, `_geometry`; mesh: `_mesh`, `_task` | Selects one framebuffer, mesh, or task stage. Graphics and ray-tracing cases exercise supported stages through shared all-stage helpers. | [stage arrays and test names](../../../modules/vulkan/subgroups/vktSubgroupsBallotOtherTests.cpp#L468-L479) |
| Shader build target | SPIR-V 1.3 for compute, graphics, and framebuffer; SPIR-V 1.4 for ray tracing, mesh, and task | Matches the stage requirements while preserving the same source-level operation checks. | [build options](../../../modules/vulkan/subgroups/vktSubgroupsBallotOtherTests.cpp#L278-L307) |

The default mustpass list contains 84 executable leaves: 14 compute, 28 framebuffer, 7 graphics, 28 mesh or task, and 7 ray-tracing cases.

## Behavior Parameters

The primary behavioral axis is the `operation test case leaf`. Each value changes the subgroup operation and its expected relationship to the controlled ballot masks.

### `subgroupinverseballot` - read the current invocation's bit

The operation converts one ballot mask into a Boolean for the current invocation. The shader checks all-ones, all-zeros, and `subgroupBallot(true)` masks, then sets the fourth verdict bit unconditionally because the first three checks cover the intended behavior.

### `subgroupballotbitextract` - read one indexed bit

The operation extracts the bit at `gl_SubgroupInvocationID`. The shader checks all-ones, all-zeros, and the ballot of `true`, then repeats the all-ones extraction in a loop to retain the fourth verdict bit only when every iteration returns true.

### `subgroupballotbitcount` - count all in-range set bits

The reduction must return `gl_SubgroupSize` for an all-ones mask and zero for an all-zeros mask. A ballot of `true` must have a positive count, while a mask whose first set bit is at `gl_SubgroupSize` must count as zero.

### `subgroupballotinclusivebitcount` - count through the current invocation

For an all-ones mask, the count must be `gl_SubgroupInvocationID + 1`. The shader also checks zero and live ballots, then tries every cutoff from 0 through 127 to verify the inclusive prefix against an arithmetic reference.

### `subgroupballotexclusivebitcount` - count before the current invocation

For an all-ones mask, the count must be `gl_SubgroupInvocationID`. The exhaustive cutoff loop uses the exclusive prefix reference, so the current invocation's bit is not included.

### `subgroupballotfindlsb` - find the lowest set invocation index

An all-ones mask must return index zero. The shader avoids an undefined empty-mask result, range-checks the result of `subgroupBallot(true)`, and verifies every possible leading-zero cutoff with a mask whose lowest set bit is at the requested index.

### `subgroupballotfindmsb` - find the highest set invocation index

An all-ones mask must return `gl_SubgroupSize - 1`. The shader range-checks a live ballot and verifies each invocation index with a single-bit mask, making the expected most-significant set bit unambiguous.

## Shader Analysis

The compute `subgroupballotbitcount` leaf is representative because it exposes the common shader wrapper and the four-part verdict without unrelated pipeline stages. The other operation leaves replace the central check body; the execution families wrap that body for their selected stages.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.subgroups.ballot_other.compute.subgroupballotbitcount
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `compute` | Uses the shared compute wrapper, specialization-controlled local sizes, and one storage-buffer verdict per global invocation. |
| `subgroupballotbitcount` | Selects reduction bit count and four masks that cover all ones, all zeros, a live ballot, and the first bit outside the subgroup. |
| no `_requiredsubgroupsize` suffix | Uses the ordinary compute path rather than the host loop that requests each advertised subgroup size. |

#### Purpose

This shader verifies that ballot bit count treats the actual subgroup width as the valid range of a 128-bit ballot. It writes `0xf` only when all four reduction checks pass.

#### Structural Design

| Verdict bit | Input mask | Required count |
|-------------|------------|----------------|
| `0x1` | `uvec4(0xFFFFFFFF)` | `gl_SubgroupSize` |
| `0x2` | `uvec4(0)` | zero |
| `0x4` | `subgroupBallot(true)` | greater than zero |
| `0x8` | bits beginning at `gl_SubgroupSize` | zero |

#### Shader Code

```glsl
#version 450
#extension GL_KHR_shader_subgroup_ballot: enable
layout (local_size_x_id = 0, local_size_y_id = 1, local_size_z_id = 2) in;
/// Binding 0 is a std430 storage buffer with one uint verdict per global invocation.
layout(set = 0, binding = 0, std430) buffer Buffer1
{
  uint result[];
};
void main (void)
{
  /// Flatten the dispatched three-dimensional invocation grid into the result buffer.
  uvec3 globalSize = gl_NumWorkGroups * gl_WorkGroupSize;
  highp uint offset = globalSize.x * ((globalSize.y * gl_GlobalInvocationID.z) + gl_GlobalInvocationID.y) + gl_GlobalInvocationID.x;
  uint tempRes;
  /// Each low bit records one independent ballot bit-count check; 0xf means all checks passed.
  uvec4 allOnes = uvec4(0xFFFFFFFF);
  uvec4 allZeros = uvec4(0);
  uint tempResult = 0;
#define MAKE_HIGH_BALLOT_RESULT(i) uvec4(i >= 32 ? 0 : (0xFFFFFFFF << i), i >= 64 ? 0 : (0xFFFFFFFF << ((i < 32) ? 0 : (i - 32))), i >= 96 ? 0 : (0xFFFFFFFF << ((i < 64) ? 0 : (i - 64))), i >= 128 ? 0 : (0xFFFFFFFF << ((i < 96) ? 0 : (i - 96))))
  /* To ensure a 32-bit computation, use a variable with default highp precision. */
  uint SubgroupSize = gl_SubgroupSize;
  tempResult |= SubgroupSize == subgroupBallotBitCount(allOnes) ? 0x1 : 0;
  tempResult |= 0 == subgroupBallotBitCount(allZeros) ? 0x2 : 0;
  tempResult |= 0 < subgroupBallotBitCount(subgroupBallot(true)) ? 0x4 : 0;
  tempResult |= 0 == subgroupBallotBitCount(MAKE_HIGH_BALLOT_RESULT(SubgroupSize)) ? 0x8 : 0;
  tempRes = tempResult;
  result[offset] = tempRes;
}
```

#### Additional Info

- `initPrograms` passes explicit SPIR-V 1.3 build options for this compute case. The shared builder supplies specialization IDs 0, 1, and 2 for the local workgroup dimensions.
- `MAKE_HIGH_BALLOT_RESULT` spans four 32-bit words. For any supported subgroup size up to 128, it leaves only bits at or above `gl_SubgroupSize` set.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Operation test case leaf | Replaces the four bit-count checks with inverse, extraction, prefix-count, or set-bit-search checks and their operation-specific loops. | [operation switch](../../../modules/vulkan/subgroups/vktSubgroupsBallotOtherTests.cpp#L165-L271) |
| Execution family and shader stage | Keeps the generated test body but changes the stage wrapper, output declaration, indexing, and SPIR-V target where required. | [program builders](../../../modules/vulkan/subgroups/vktSubgroupsBallotOtherTests.cpp#L278-L307) |
| Required subgroup size | Keeps the GLSL source but creates pipelines for each supported required size and local workgroup configuration. | [required-size execution](../../../modules/vulkan/subgroups/vktSubgroupsBallotOtherTests.cpp#L391-L429) |

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
; Bound: 168
; Schema: 0
               OpCapability Shader
               OpCapability GroupNonUniform
               OpCapability GroupNonUniformBallot
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_NumWorkGroups %gl_GlobalInvocationID %gl_SubgroupSize
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpSourceExtension "GL_KHR_shader_subgroup_ballot"
               OpSourceExtension "GL_KHR_shader_subgroup_basic"
               OpName %main "main"
               OpName %globalSize "globalSize"
               OpName %gl_NumWorkGroups "gl_NumWorkGroups"
               OpName %offset "offset"
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
               OpName %allOnes "allOnes"
               OpName %allZeros "allZeros"
               OpName %tempResult "tempResult"
               OpName %SubgroupSize "SubgroupSize"
               OpName %gl_SubgroupSize "gl_SubgroupSize"
               OpName %tempRes "tempRes"
               OpName %Buffer1 "Buffer1"
               OpMemberName %Buffer1 0 "result"
               OpName %_ ""
               OpDecorate %gl_NumWorkGroups BuiltIn NumWorkgroups
               OpDecorate %13 SpecId 0
               OpDecorate %14 SpecId 1
               OpDecorate %15 SpecId 2
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %gl_SubgroupSize RelaxedPrecision
               OpDecorate %gl_SubgroupSize BuiltIn SubgroupSize
               OpDecorate %49 RelaxedPrecision
               OpDecorate %_runtimearr_uint ArrayStride 4
               OpDecorate %Buffer1 Block
               OpMemberDecorate %Buffer1 0 Offset 0
               OpDecorate %_ Binding 0
               OpDecorate %_ DescriptorSet 0
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
%uint_4294967295 = OpConstant %uint 4294967295
         %43 = OpConstantComposite %v4uint %uint_4294967295 %uint_4294967295 %uint_4294967295 %uint_4294967295
         %45 = OpConstantComposite %v4uint %uint_0 %uint_0 %uint_0 %uint_0
%gl_SubgroupSize = OpVariable %_ptr_Input_uint Input
     %uint_3 = OpConstant %uint 3
       %bool = OpTypeBool
        %int = OpTypeInt 32 1
      %int_1 = OpConstant %int 1
      %int_0 = OpConstant %int 0
      %int_2 = OpConstant %int 2
       %true = OpConstantTrue %bool
      %int_4 = OpConstant %int 4
    %uint_32 = OpConstant %uint 32
%_ptr_Function_int = OpTypePointer Function %int
     %int_n1 = OpConstant %int -1
    %uint_64 = OpConstant %uint 64
    %uint_96 = OpConstant %uint 96
   %uint_128 = OpConstant %uint 128
      %int_8 = OpConstant %int 8
%_runtimearr_uint = OpTypeRuntimeArray %uint
    %Buffer1 = OpTypeStruct %_runtimearr_uint
%_ptr_StorageBuffer_Buffer1 = OpTypePointer StorageBuffer %Buffer1
          %_ = OpVariable %_ptr_StorageBuffer_Buffer1 StorageBuffer
%_ptr_StorageBuffer_uint = OpTypePointer StorageBuffer %uint
       %main = OpFunction %void None %3
          %5 = OpLabel
 %globalSize = OpVariable %_ptr_Function_v3uint Function
     %offset = OpVariable %_ptr_Function_uint Function
    %allOnes = OpVariable %_ptr_Function_v4uint Function
   %allZeros = OpVariable %_ptr_Function_v4uint Function
 %tempResult = OpVariable %_ptr_Function_uint Function
%SubgroupSize = OpVariable %_ptr_Function_uint Function
         %84 = OpVariable %_ptr_Function_int Function
         %96 = OpVariable %_ptr_Function_int Function
        %102 = OpVariable %_ptr_Function_uint Function
        %115 = OpVariable %_ptr_Function_int Function
        %121 = OpVariable %_ptr_Function_uint Function
        %134 = OpVariable %_ptr_Function_int Function
        %140 = OpVariable %_ptr_Function_uint Function
    %tempRes = OpVariable %_ptr_Function_uint Function
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
               OpStore %allOnes %43
               OpStore %allZeros %45
               OpStore %tempResult %uint_0
         %49 = OpLoad %uint %gl_SubgroupSize
               OpStore %SubgroupSize %49
         %50 = OpLoad %uint %SubgroupSize
         %51 = OpLoad %v4uint %allOnes
         %53 = OpGroupNonUniformBallotBitCount %uint %uint_3 Reduce %51
         %55 = OpIEqual %bool %50 %53
         %59 = OpSelect %int %55 %int_1 %int_0
         %60 = OpBitcast %uint %59
         %61 = OpLoad %uint %tempResult
         %62 = OpBitwiseOr %uint %61 %60
               OpStore %tempResult %62
         %63 = OpLoad %v4uint %allZeros
         %64 = OpGroupNonUniformBallotBitCount %uint %uint_3 Reduce %63
         %65 = OpIEqual %bool %uint_0 %64
         %67 = OpSelect %int %65 %int_2 %int_0
         %68 = OpBitcast %uint %67
         %69 = OpLoad %uint %tempResult
         %70 = OpBitwiseOr %uint %69 %68
               OpStore %tempResult %70
         %72 = OpGroupNonUniformBallot %v4uint %uint_3 %true
         %73 = OpGroupNonUniformBallotBitCount %uint %uint_3 Reduce %72
         %74 = OpULessThan %bool %uint_0 %73
         %76 = OpSelect %int %74 %int_4 %int_0
         %77 = OpBitcast %uint %76
         %78 = OpLoad %uint %tempResult
         %79 = OpBitwiseOr %uint %78 %77
               OpStore %tempResult %79
         %80 = OpLoad %uint %SubgroupSize
         %82 = OpUGreaterThanEqual %bool %80 %uint_32
               OpSelectionMerge %86 None
               OpBranchConditional %82 %85 %87
         %85 = OpLabel
               OpStore %84 %int_0
               OpBranch %86
         %87 = OpLabel
         %89 = OpLoad %uint %SubgroupSize
         %90 = OpShiftLeftLogical %int %int_n1 %89
               OpStore %84 %90
               OpBranch %86
         %86 = OpLabel
         %91 = OpLoad %int %84
         %92 = OpBitcast %uint %91
         %93 = OpLoad %uint %SubgroupSize
         %95 = OpUGreaterThanEqual %bool %93 %uint_64
               OpSelectionMerge %98 None
               OpBranchConditional %95 %97 %99
         %97 = OpLabel
               OpStore %96 %int_0
               OpBranch %98
         %99 = OpLabel
        %100 = OpLoad %uint %SubgroupSize
        %101 = OpULessThan %bool %100 %uint_32
               OpSelectionMerge %104 None
               OpBranchConditional %101 %103 %105
        %103 = OpLabel
               OpStore %102 %uint_0
               OpBranch %104
        %105 = OpLabel
        %106 = OpLoad %uint %SubgroupSize
        %107 = OpISub %uint %106 %uint_32
               OpStore %102 %107
               OpBranch %104
        %104 = OpLabel
        %108 = OpLoad %uint %102
        %109 = OpShiftLeftLogical %int %int_n1 %108
               OpStore %96 %109
               OpBranch %98
         %98 = OpLabel
        %110 = OpLoad %int %96
        %111 = OpBitcast %uint %110
        %112 = OpLoad %uint %SubgroupSize
        %114 = OpUGreaterThanEqual %bool %112 %uint_96
               OpSelectionMerge %117 None
               OpBranchConditional %114 %116 %118
        %116 = OpLabel
               OpStore %115 %int_0
               OpBranch %117
        %118 = OpLabel
        %119 = OpLoad %uint %SubgroupSize
        %120 = OpULessThan %bool %119 %uint_64
               OpSelectionMerge %123 None
               OpBranchConditional %120 %122 %124
        %122 = OpLabel
               OpStore %121 %uint_0
               OpBranch %123
        %124 = OpLabel
        %125 = OpLoad %uint %SubgroupSize
        %126 = OpISub %uint %125 %uint_64
               OpStore %121 %126
               OpBranch %123
        %123 = OpLabel
        %127 = OpLoad %uint %121
        %128 = OpShiftLeftLogical %int %int_n1 %127
               OpStore %115 %128
               OpBranch %117
        %117 = OpLabel
        %129 = OpLoad %int %115
        %130 = OpBitcast %uint %129
        %131 = OpLoad %uint %SubgroupSize
        %133 = OpUGreaterThanEqual %bool %131 %uint_128
               OpSelectionMerge %136 None
               OpBranchConditional %133 %135 %137
        %135 = OpLabel
               OpStore %134 %int_0
               OpBranch %136
        %137 = OpLabel
        %138 = OpLoad %uint %SubgroupSize
        %139 = OpULessThan %bool %138 %uint_96
               OpSelectionMerge %142 None
               OpBranchConditional %139 %141 %143
        %141 = OpLabel
               OpStore %140 %uint_0
               OpBranch %142
        %143 = OpLabel
        %144 = OpLoad %uint %SubgroupSize
        %145 = OpISub %uint %144 %uint_96
               OpStore %140 %145
               OpBranch %142
        %142 = OpLabel
        %146 = OpLoad %uint %140
        %147 = OpShiftLeftLogical %int %int_n1 %146
               OpStore %134 %147
               OpBranch %136
        %136 = OpLabel
        %148 = OpLoad %int %134
        %149 = OpBitcast %uint %148
        %150 = OpCompositeConstruct %v4uint %92 %111 %130 %149
        %151 = OpGroupNonUniformBallotBitCount %uint %uint_3 Reduce %150
        %152 = OpIEqual %bool %uint_0 %151
        %154 = OpSelect %int %152 %int_8 %int_0
        %155 = OpBitcast %uint %154
        %156 = OpLoad %uint %tempResult
        %157 = OpBitwiseOr %uint %156 %155
               OpStore %tempResult %157
        %159 = OpLoad %uint %tempResult
               OpStore %tempRes %159
        %164 = OpLoad %uint %offset
        %165 = OpLoad %uint %tempRes
        %167 = OpAccessChain %_ptr_StorageBuffer_uint %_ %int_0 %164
               OpStore %167 %165
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The shared compute and mesh harness allocates a host-visible storage buffer large enough for all tested invocations and binds it at set 0, binding 0.
- Local workgroup dimensions are provided through specialization constants. The harness creates pipelines for several local sizes, dispatches the configured workgroups, and repeats this process for every requested subgroup size when the suffix is present.
- Graphics, framebuffer, ray-tracing, mesh, and task paths use equivalent stage-specific wrappers and shared execution helpers. The operation body always produces the same four-bit verdict.
- After execution, a shader-write to host-read memory barrier makes output writes available. The host waits, invalidates the mapped allocation, and passes the result data to the appropriate callback.
- `check` requires every scalar in the relevant output range to equal `0xf`. `checkComputeOrMesh` derives that range from the workgroup count and local size. Any mismatching invocation makes that iteration fail.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `subgroupinverseballot` | Incorrect mapping from the current invocation's index to its Boolean bit in a ballot mask. |
| `subgroupballotbitextract` | Incorrect extraction or indexing of one bit from the four-word ballot representation. |
| `subgroupballotbitcount` | Incorrect reduction count, especially at the actual subgroup-size boundary or for bits outside the subgroup. |
| `subgroupballotinclusivebitcount` | Incorrect inclusive prefix boundary or incorrect counting across `uvec4` word boundaries. |
| `subgroupballotexclusivebitcount` | Incorrect exclusive prefix boundary or incorrect counting across `uvec4` word boundaries. |
| `subgroupballotfindlsb` | Incorrect least-significant set-bit search or returned invocation index. |
| `subgroupballotfindmsb` | Incorrect most-significant set-bit search or returned invocation index. |

A failure in any value can also come from shader compilation or stage lowering, result-buffer addressing, synchronization and host visibility, or the shared stage harness. The failing path and result pattern are needed to separate operation semantics from shared infrastructure.

### Cause Analysis

#### Current-invocation ballot mapping failure

**Possible failure symptoms:** `subgroupinverseballot` writes a value below `0xf` for one or more invocations when an all-ones, all-zeros, or live ballot is converted to a Boolean.

**Possible implementation causes:** the subgroup operation may use the wrong local invocation index, select the wrong word or bit within the four-word mask, or lower the inverse ballot with incorrect active-invocation semantics.

#### Indexed ballot extraction failure

**Possible failure symptoms:** `subgroupballotbitextract` clears one of the first three verdict bits or loses `0x8` during its repeated all-ones extraction check.

**Possible implementation causes:** extraction may calculate the wrong 32-bit word or bit offset for `gl_SubgroupInvocationID`, especially when the invocation index crosses a word boundary. Incorrect lowering of the indexed extraction operation can produce the same symptom.

#### Ballot reduction count failure

**Possible failure symptoms:** `subgroupballotbitcount` does not return the subgroup width for all ones, zero for all zeros and out-of-range high bits, or a positive count for the ballot of `true`.

**Possible implementation causes:** the reduction may count physical mask bits that are outside `gl_SubgroupSize`, omit participating invocations, or lower `OpGroupNonUniformBallotBitCount` with a group operation other than the required `Reduce` semantics.

#### Inclusive prefix count failure

**Possible failure symptoms:** `subgroupballotinclusivebitcount` disagrees with `gl_SubgroupInvocationID + 1` for all ones or with the exhaustive cutoff reference for at least one invocation or mask word.

**Possible implementation causes:** an off-by-one prefix endpoint can exclude the current invocation. Word-to-word carry or prefix accumulation may also fail when the cutoff crosses bit 32, 64, or 96.

#### Exclusive prefix count failure

**Possible failure symptoms:** `subgroupballotexclusivebitcount` disagrees with `gl_SubgroupInvocationID` for all ones or with its exhaustive cutoff reference.

**Possible implementation causes:** an off-by-one endpoint can include the current invocation when exclusive semantics require only lower invocation indices. The same cross-word prefix defects as the inclusive case can appear at ballot word boundaries.

#### Least-significant set-bit search failure

**Possible failure symptoms:** `subgroupballotfindlsb` does not return zero for all ones, returns an index outside the subgroup for a live ballot, or disagrees with a generated leading-zero cutoff.

**Possible implementation causes:** the search may inspect mask words in the wrong order, translate a word-local bit position to the wrong invocation index, or mishandle the transition between adjacent 32-bit words.

#### Most-significant set-bit search failure

**Possible failure symptoms:** `subgroupballotfindmsb` does not return `gl_SubgroupSize - 1` for all ones, returns an out-of-range live-ballot index, or fails a single-bit mask check.

**Possible implementation causes:** the search may scan words or bits in the wrong direction, fail to constrain the all-ones result to the actual subgroup width, or return an incorrect global index for a set bit in a higher mask word.

#### Shared execution or result-transport failure

**Possible failure symptoms:** several operation leaves or stage families fail with similar output patterns, or values remain stale or are written at unexpected offsets rather than showing an operation-specific missing verdict bit.

**Possible implementation causes:** shader compilation or stage-specific lowering may alter the generated body, result indexing or descriptor binding may target the wrong storage, or shader writes may not become visible to the host before mapped memory is inspected. The shared harness and failing stage must be investigated before assigning such a failure to a ballot operation.

## Case Pruning

### Requirement-based pruning

- Subgroup operations and `VK_SUBGROUP_FEATURE_BALLOT_BIT` are required. The selected shader stages must also support subgroup operations.
- Required-subgroup-size variants require `VK_EXT_subgroup_size_control`, `subgroupSizeControl`, `computeFullSubgroups`, and support for the selected stage in `requiredSubgroupSizeStages`.
- Required sizes are the powers of two from `minSubgroupSize` through `maxSubgroupSize`, matching the Vulkan subgroup-size-control limits.
- Ray-tracing paths require `VK_KHR_ray_tracing_pipeline`. Mesh and task paths require `VK_EXT_mesh_shader`, vertex-pipeline stores and atomics, and the task shader feature when a task case is selected.
- Unsupported graphics or ray-tracing stages are removed by the shared stage-support helpers. Geometry and tessellation point-size behavior is generated only when the implementation supports it.

### Design-based pruning

- Required-subgroup-size variants are generated only for compute, mesh, and task stages, where the shared compute-like harness can sweep required sizes.
- Framebuffer coverage is limited to vertex, tessellation control, tessellation evaluation, and geometry stages because these cases use the no-SSBO framebuffer path.
- Find-LSB and find-MSB avoid checking an all-zero mask because the search result for an empty set is not used as a defined reference.
- Vulkan SC omits ray-tracing, mesh, and task registrations by construction.
- The applicable `test-issues.txt` has no exclusion for `ballot_other`.

## Key Takeaways

- The seven operation leaves are the behavioral core: they distinguish Boolean bit lookup, full reduction, two prefix boundaries, and two search directions.
- Each invocation performs four checks and writes a compact `0xf` verdict, including explicit coverage of the actual subgroup-size boundary.
- Inclusive and exclusive counts differ only at the current invocation, so their exhaustive cutoff loops are important off-by-one checks.
- The same operation body is reused across stage families, while required-size variants repeat it over the advertised power-of-two range.
- See `Failure Meaning` to interpret a missing verdict bit or a stage-wide result-transport failure.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Operation names and generated checks | [`OpType`, `getOpTypeName`, and `getTestString`](../../../modules/vulkan/subgroups/vktSubgroupsBallotOtherTests.cpp#L41-L276) | Defines all seven behavior leaves and every shader-side verdict bit. |
| Framebuffer and general program builders | [`initFrameBufferPrograms` and `initPrograms`](../../../modules/vulkan/subgroups/vktSubgroupsBallotOtherTests.cpp#L278-L307) | Selects the SPIR-V target and delegates stage wrapper generation. |
| Feature and stage support | [`supportedCheck`](../../../modules/vulkan/subgroups/vktSubgroupsBallotOtherTests.cpp#L309-L358) | Applies ballot, subgroup-size-control, ray-tracing, mesh, task, and stage requirements. |
| Runtime routing and size sweep | [`test`](../../../modules/vulkan/subgroups/vktSubgroupsBallotOtherTests.cpp#L381-L450) | Selects the shared execution helper and iterates required subgroup sizes. |
| Test matrix registration | [`createSubgroupsBallotOtherTests`](../../../modules/vulkan/subgroups/vktSubgroupsBallotOtherTests.cpp#L458-L569) | Builds the execution-family, operation, stage, and required-size paths. |
| Compute shader wrapper | [`initStdPrograms`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L1406-L1434) | Adds local-size specialization, result indexing, and the final SSBO write. |
| Scalar result callbacks | [`check` and `checkComputeOrMesh`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L2640-L2663) | Requires every observed value to equal `0xf`. |
| Compute and mesh host flow | [`makeComputeOrMeshTestRequiredSubgroupSize`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L3762-L4063) | Creates storage, pipelines, dispatches, synchronization, readback, and pass or fail results. |
| Executable path inventory | [`subgroups.txt`](../../../mustpass/main/vk-default/subgroups.txt#L18288-L18371) | Confirms all 84 default mustpass leaves and the representative path. |
| Vulkan subgroup and ballot semantics | [`shaders.adoc`](../../../../vulkan-docs/src/chapters/shaders.adoc#L3447-L3523) | Defines subgroup-scoped group operations and ballot functionality. |
| Ballot feature support | [`limits.adoc`](../../../../vulkan-docs/src/chapters/limits.adoc#L1428-L1453) | Connects `VK_SUBGROUP_FEATURE_BALLOT_BIT` to `GroupNonUniformBallot`. |
| Ballot bit-count validity | [`spirvenv.adoc`](../../../../vulkan-docs/src/appendices/spirvenv.adoc#L608-L611) | Restricts bit count to reduction, inclusive scan, and exclusive scan. |
| Subgroup-size control model | [`VK_EXT_subgroup_size_control.adoc`](../../../../vulkan-docs/src/appendices/VK_EXT_subgroup_size_control.adoc#L24-L69) | Defines variable and required subgroup sizes and full-subgroup constraints. |
