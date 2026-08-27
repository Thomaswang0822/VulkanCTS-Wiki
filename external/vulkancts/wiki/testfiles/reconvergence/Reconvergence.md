## Overview

**Core question:** Does maximal reconvergence keep the terminated invocation out of the later subgroup ballot while preserving the expected ballot for the remaining invocations?

- [vktReconvergenceTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp) owns the `reconvergence` root, five generated families, the delegated `terminate_invocation` child, and the fixed maximal-fragment Amber cases.
- This page covers the whole implementation file because it registers the five direct generated families and delegates `terminate_invocation` to [vktReconvergenceTerminateInvocationTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTerminateInvocationTests.cpp#L653-L675).
- The generated families create random control-flow shaders and compare device observations with a CPU simulation. The fixed Amber cases exercise maximal reconvergence with termination and demotion in fragment shaders.
- The main package calls `Reconvergence::createTests`; the experimental package calls `Reconvergence::createTestsExperimental`. Both register the exact root name `reconvergence`.

## Background Knowledge

- **Subgroup ballots.** `subgroupBallot(condition)` returns a bit mask for the active subgroup invocations for which `condition` is true. `subgroupBallotFindLSB` selects the lowest set lane, and `subgroupBallotBitCount` counts set lanes.
- **Maximal reconvergence.** The `shaderMaximalReconvergence` feature enables the `MaximallyReconvergesKHR` execution mode. In the representative fragment shader, `[[maximally_reconverges]]` makes the post-termination ballot the value under test. The Vulkan shader specification states that helper invocations remain active for the lifetime of their quad scope instance when this mode applies.
- **Helper invocations.** Fragment helper invocations participate in some shader operations but must not be treated as ordinary rendered fragments. The case chooses the first non-helper invocation to write the result buffer.

## Registration Hierarchy

```text
reconvergence
├── subgroup_uniform_control_flow_elect
├── subgroup_uniform_control_flow_ballot
├── workgroup_uniform_control_flow_elect
├── workgroup_uniform_control_flow_ballot
├── maximal
└── terminate_invocation (registration only)
```

The five generated families are registered by `createTests`; `terminate_invocation` is appended at the end of that builder and implemented in the separate delegated source file. `maximal.fragment` also receives the fixed Amber leaves registered by `createAmberFragmentTestCases`. The same direct hierarchy is produced for main and experimental roots, while generated leaves are split by index.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test family | `subgroup_uniform_control_flow_elect`, `subgroup_uniform_control_flow_ballot`, `workgroup_uniform_control_flow_elect`, `workgroup_uniform_control_flow_ballot`, `maximal` | Selects the execution-mode contract and observation rule for generated cases. | [test-family table](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7797-L7803) |
| Shader stage | `compute` for all five families; `fragment` for `maximal` in the current configuration | Selects the generated shader stage. Other graphics stages are behind `INCLUDE_GRAPHICS_TESTS`. | [stage filter](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7805-L7825) |
| Nesting | `nesting2` to `nesting4` for non-maximal families; `nesting2` to `nesting6` for maximal compute | Controls generated control-flow depth. | [nesting construction](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7827-L7872) |
| Seed | `0` through `7` | Initializes the random masks and operation generator. | [seed groups](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7842-L7848) |
| Generated index | `0` through `249` for nesting 2 to 4, `0` through `99` for nesting 5, `0` through `49` for nesting 6 | Selects a generated case within a seed and nesting group. | [case counts](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7849-L7866) |
| Compute dimensions | `sizeX = 7`, `sizeY = 13` | Initial compute dimensions before full-subgroup adjustment. | [compute dimensions](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7874-L7887) |
| Maximal fragment Amber leaves | `terminate_invocation`, `demote_invocation`, `demote_entire_quad`, `demote_half_quad_top`, `demote_half_quad_right`, `demote_half_quad_bottom`, `demote_half_quad_left`, `demote_half_quad_slash`, `demote_half_quad_backslash` | Fixed fragment checks below `maximal.fragment`. | [Amber case table](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7951-L8016) |
| Main/experimental split | main for `ndx < numTests / 5`; experimental for the remaining indices | Keeps the root and family names unchanged while partitioning generated leaves. | [split predicate](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7929-L7933), [package registration](../../../modules/vulkan/vktTestPackage.cpp#L1387-L1407) |

## Behavior Parameters

The primary behavioral axis is the **test family**. The family changes the reconvergence or uniform-control-flow contract. Stage, nesting, seed, and generated index select the workload.

### `subgroup_uniform_control_flow_elect` | subgroup-uniform election

Generated control flow uses `[[subgroup_uniform_control_flow]]` and elect observations. The checker expects the elected lane to produce the source-defined elect value at fully converged reference locations.

### `subgroup_uniform_control_flow_ballot` | subgroup-uniform ballot

Generated control flow uses the same execution-mode attribute but records `subgroupBallot(true)` masks. The checker expects a full subgroup mask where the CPU reference identifies a fully converged observation.

### `workgroup_uniform_control_flow_elect` | workgroup-uniform election

This family selects workgroup-uniform control-flow behavior and records elect observations. It uses the same random operation generator with the workgroup-uniform classification.

### `workgroup_uniform_control_flow_ballot` | workgroup-uniform ballot

This family selects workgroup-uniform control-flow behavior and records ballot masks. It requires both ballot support and the uniform-control-flow feature.

### `maximal` | maximal reconvergence

Generated maximal cases emit `[[maximally_reconverges]]` and compare every recorded compute value with the CPU reference. Maximal fragment cases also contain fixed Amber tests whose ballots encode termination and demotion behavior.

### `terminate_invocation` | delegated termination family

The root registers this family, but its four direct leaves, `bit_count`, `terminate_helpers`, `oob_read`, and `quad_any`, are implemented by `createTerminateInvocationTests`. See [TerminateInvocation.md](TerminateInvocation.md).

## Shader Analysis

The representative walkthrough uses the exact fixed Amber case `dEQP-VK.reconvergence.maximal.fragment.terminate_invocation`. Unlike the generated random cases, its GLSL is stored verbatim in the repository and its Amber registration supplies the framebuffer, buffers, and expected result.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.reconvergence.maximal.fragment.terminate_invocation
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `maximal.fragment` | Selects the fixed Amber fragment cases registered by `createAmberFragmentTestCases`. |
| `terminate_invocation` | Terminates the lane selected by the input fragment ID and checks the later ballot. |
| `FRAMEBUFFER_SIZE 16 16` | Makes `fragmentID = uint(gl_FragCoord.y) * 16 + uint(gl_FragCoord.x)`. |
| `fragments[0] = 136` | Selects the fragment whose first matching subgroup invocation is terminated when that fragment is covered. |
| `TARGET_ENV spv1.6` | Selects the Amber shader compilation target, reflected by the generated SPIR-V version. |

#### Purpose

The fragment shader finds the first invocation whose `fragmentID` equals the input `fragment`, removes that lane with `terminateInvocation`, and checks that the later ballot equals the original subgroup ballot with that lane cleared. A non-helper invocation writes `1` to `Y.result` only when the comparison succeeds.

#### Structural Design

| Phase | Shader operation | Expected relation |
|-------|------------------|-------------------|
| Select lane | `subgroupBallot(fragmentID == fragment)` then `findBallotLSB` | Finds the lane to terminate, or `UINT_MAX` if no lane matches. |
| Build reference | `ballotResetBit(subgroupBallot(true), terminateInvocationID)` | Removes the selected lane from a full ballot. |
| Terminate | The selected lane executes `terminateInvocation`. | That invocation stops executing the remainder of the entry point. |
| Check result | The surviving subgroup computes `resultBallot`; the first non-helper invocation compares it with `referenceBallot`. | `Y.result` becomes `1` only for equality. |

#### Shader Code

```glsl
#version 450

#extension GL_EXT_maximal_reconvergence : require
#extension GL_KHR_shader_subgroup_ballot : require
#extension GL_EXT_terminate_invocation : require

#define UINT_MAX 0xFFFFFFFF

layout(binding = 0) readonly buffer X { uint fragment; };
layout(binding = 1)          buffer Y { uint result; };
layout(location = 0) out vec4 dEQP_FragColor;

void resetBit(in out uvec4 ballot, uint bit) { if (bit < gl_SubgroupSize) ballot[bit/32] &= (UINT_MAX ^ (1u << (bit % 32))); }
uvec4 ballotResetBit(uvec4 ballot, uint bit) { resetBit(ballot, bit); return ballot; }
uint findBallotLSB(uvec4 ballot) { return subgroupBallotBitCount(ballot) > 0 ? subgroupBallotFindLSB(ballot) : UINT_MAX; }

void main()
[[maximally_reconverges]]
{
    /// The Amber pipeline uses a 16 by 16 framebuffer, so this maps each fragment to 0 through 255.
    const uint fragmentID = uint(gl_FragCoord.y) * 16 + uint(gl_FragCoord.x);
    /// Binding 0 supplies the target fragment ID. The ballot identifies the lane that will terminate.
    const uvec4 terminateSubgroupBallot = subgroupBallot(fragmentID == fragment);
    const uint terminateInvocationID = findBallotLSB(terminateSubgroupBallot);
    const bool terminateSubgroup = terminateInvocationID < gl_SubgroupSize;
    /// The reference ballot is the full active ballot with the selected lane cleared.
    const uvec4 referenceBallot = ballotResetBit(subgroupBallot(true), terminateInvocationID);

    if (terminateSubgroup && (gl_SubgroupInvocationID == terminateInvocationID))
    {
        terminateInvocation;
    }

    const uvec4 resultBallot = subgroupBallot(true);
    /// Helper invocations do not write the result buffer. The first non-helper lane records the comparison.
    const uvec4 nonHelperBallot = subgroupBallot(!gl_HelperInvocation);
    const uint writeInvocation = subgroupBallotFindLSB(nonHelperBallot);

    if (terminateSubgroup && (gl_SubgroupInvocationID == writeInvocation))
    {
        result = (resultBallot == referenceBallot) ? 1 : 0;
    }

    dEQP_FragColor = vec4(1.0);
}
```

#### Additional Info

- The exact source is [terminate_invocation.amber](../../../data/vulkan/amber/reconvergence/maximal/fragment/terminate_invocation.amber#L5-L48). The `///` lines above are documentation annotations; the GLSL statements and source `//` comments are unchanged.
- The Amber pipeline binds `fragments` at descriptor set 0 binding 0, `result` at binding 1, uses a 16 by 16 framebuffer, and expects `result[0] == 1` [Amber pipeline](../../../data/vulkan/amber/reconvergence/maximal/fragment/terminate_invocation.amber#L51-L80).
- `createAmberFragmentTestCases` constructs the path under `reconvergence/maximal/<group name>` and applies the maximal-reconvergence, subgroup-ballot, and stage support checks [Amber registration](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7951-L8069).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| `fragment` input | Changes which `fragmentID` sets `terminateSubgroupBallot` and therefore which lane is removed from `referenceBallot`. | [Amber input buffer](../../../data/vulkan/amber/reconvergence/maximal/fragment/terminate_invocation.amber#L55-L57), [shader selection](../../../data/vulkan/amber/reconvergence/maximal/fragment/terminate_invocation.amber#L25-L35) |
| Maximal reconvergence | Applies `[[maximally_reconverges]]` and requires the matching extension. | [Amber execution mode](../../../data/vulkan/amber/reconvergence/maximal/fragment/terminate_invocation.amber#L5-L10), [feature support](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L8020-L8027) |
| Helper invocation status | Selects the lane allowed to write `Y.result`, without changing the target ballot. | [non-helper selection](../../../data/vulkan/amber/reconvergence/maximal/fragment/terminate_invocation.amber#L37-L45) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed GLSL from this walkthrough
- Stage: `frag`
- Target SPIRV version: `spirv1.6`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.6
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 158
; Schema: 0
               OpCapability Shader
               OpCapability GroupNonUniform
               OpCapability GroupNonUniformBallot
               OpExtension "SPV_KHR_maximal_reconvergence"
               OpExtension "SPV_KHR_terminate_invocation"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %gl_SubgroupSize %gl_FragCoord %_ %gl_SubgroupInvocationID %gl_HelperInvocation %__0 %dEQP_FragColor
               OpExecutionMode %main MaximallyReconvergesKHR
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 450
               OpSourceExtension "GL_EXT_maximal_reconvergence"
               OpSourceExtension "GL_EXT_terminate_invocation"
               OpSourceExtension "GL_KHR_shader_subgroup_ballot"
               OpName %main "main"
               OpName %resetBit_vu4_u1_ "resetBit(vu4;u1;"
               OpName %ballot "ballot"
               OpName %bit "bit"
               OpName %ballotResetBit_vu4_u1_ "ballotResetBit(vu4;u1;"
               OpName %ballot_0 "ballot"
               OpName %bit_0 "bit"
               OpName %findBallotLSB_vu4_ "findBallotLSB(vu4;"
               OpName %ballot_1 "ballot"
               OpName %gl_SubgroupSize "gl_SubgroupSize"
               OpName %param "param"
               OpName %param_0 "param"
               OpName %fragmentID "fragmentID"
               OpName %gl_FragCoord "gl_FragCoord"
               OpName %terminateSubgroupBallot "terminateSubgroupBallot"
               OpName %X "X"
               OpMemberName %X 0 "fragment"
               OpName %_ ""
               OpName %terminateInvocationID "terminateInvocationID"
               OpName %param_1 "param"
               OpName %terminateSubgroup "terminateSubgroup"
               OpName %referenceBallot "referenceBallot"
               OpName %param_2 "param"
               OpName %param_3 "param"
               OpName %gl_SubgroupInvocationID "gl_SubgroupInvocationID"
               OpName %resultBallot "resultBallot"
               OpName %nonHelperBallot "nonHelperBallot"
               OpName %gl_HelperInvocation "gl_HelperInvocation"
               OpName %writeInvocation "writeInvocation"
               OpName %Y "Y"
               OpMemberName %Y 0 "result"
               OpName %__0 ""
               OpName %dEQP_FragColor "dEQP_FragColor"
               OpDecorate %gl_SubgroupSize RelaxedPrecision
               OpDecorate %gl_SubgroupSize BuiltIn SubgroupSize
               OpDecorate %gl_SubgroupSize Flat
               OpDecorate %27 RelaxedPrecision
               OpDecorate %gl_FragCoord BuiltIn FragCoord
               OpDecorate %X Block
               OpMemberDecorate %X 0 NonWritable
               OpMemberDecorate %X 0 Offset 0
               OpDecorate %_ NonWritable
               OpDecorate %_ Binding 0
               OpDecorate %_ DescriptorSet 0
               OpDecorate %102 RelaxedPrecision
               OpDecorate %gl_SubgroupInvocationID RelaxedPrecision
               OpDecorate %gl_SubgroupInvocationID BuiltIn SubgroupLocalInvocationId
               OpDecorate %gl_SubgroupInvocationID Flat
               OpDecorate %115 RelaxedPrecision
               OpDecorate %gl_HelperInvocation BuiltIn HelperInvocation
               OpDecorate %gl_HelperInvocation Volatile
               OpDecorate %136 RelaxedPrecision
               OpDecorate %Y Block
               OpMemberDecorate %Y 0 Offset 0
               OpDecorate %__0 Binding 1
               OpDecorate %__0 DescriptorSet 0
               OpDecorate %dEQP_FragColor Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
     %v4uint = OpTypeVector %uint 4
%_ptr_Function_v4uint = OpTypePointer Function %v4uint
%_ptr_Function_uint = OpTypePointer Function %uint
         %10 = OpTypeFunction %void %_ptr_Function_v4uint %_ptr_Function_uint
         %15 = OpTypeFunction %v4uint %_ptr_Function_v4uint %_ptr_Function_uint
         %20 = OpTypeFunction %uint %_ptr_Function_v4uint
%_ptr_Input_uint = OpTypePointer Input %uint
%gl_SubgroupSize = OpVariable %_ptr_Input_uint Input
       %bool = OpTypeBool
    %uint_32 = OpConstant %uint 32
%uint_4294967295 = OpConstant %uint 4294967295
     %uint_1 = OpConstant %uint 1
     %uint_3 = OpConstant %uint 3
     %uint_0 = OpConstant %uint 0
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Input_v4float = OpTypePointer Input %v4float
%gl_FragCoord = OpVariable %_ptr_Input_v4float Input
%_ptr_Input_float = OpTypePointer Input %float
    %uint_16 = OpConstant %uint 16
          %X = OpTypeStruct %uint
%_ptr_StorageBuffer_X = OpTypePointer StorageBuffer %X
          %_ = OpVariable %_ptr_StorageBuffer_X StorageBuffer
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_StorageBuffer_uint = OpTypePointer StorageBuffer %uint
%_ptr_Function_bool = OpTypePointer Function %bool
       %true = OpConstantTrue %bool
%gl_SubgroupInvocationID = OpVariable %_ptr_Input_uint Input
%_ptr_Input_bool = OpTypePointer Input %bool
%gl_HelperInvocation = OpVariable %_ptr_Input_bool Input
          %Y = OpTypeStruct %uint
%_ptr_StorageBuffer_Y = OpTypePointer StorageBuffer %Y
        %__0 = OpVariable %_ptr_StorageBuffer_Y StorageBuffer
     %v4bool = OpTypeVector %bool 4
      %int_1 = OpConstant %int 1
%_ptr_Output_v4float = OpTypePointer Output %v4float
%dEQP_FragColor = OpVariable %_ptr_Output_v4float Output
    %float_1 = OpConstant %float 1
        %157 = OpConstantComposite %v4float %float_1 %float_1 %float_1 %float_1
       %main = OpFunction %void None %3
          %5 = OpLabel
 %fragmentID = OpVariable %_ptr_Function_uint Function
%terminateSubgroupBallot = OpVariable %_ptr_Function_v4uint Function
%terminateInvocationID = OpVariable %_ptr_Function_uint Function
    %param_1 = OpVariable %_ptr_Function_v4uint Function
%terminateSubgroup = OpVariable %_ptr_Function_bool Function
%referenceBallot = OpVariable %_ptr_Function_v4uint Function
    %param_2 = OpVariable %_ptr_Function_v4uint Function
    %param_3 = OpVariable %_ptr_Function_uint Function
%resultBallot = OpVariable %_ptr_Function_v4uint Function
%nonHelperBallot = OpVariable %_ptr_Function_v4uint Function
%writeInvocation = OpVariable %_ptr_Function_uint Function
         %74 = OpAccessChain %_ptr_Input_float %gl_FragCoord %uint_1
         %75 = OpLoad %float %74
         %76 = OpConvertFToU %uint %75
         %78 = OpIMul %uint %76 %uint_16
         %79 = OpAccessChain %_ptr_Input_float %gl_FragCoord %uint_0
         %80 = OpLoad %float %79
         %81 = OpConvertFToU %uint %80
         %82 = OpIAdd %uint %78 %81
               OpStore %fragmentID %82
         %84 = OpLoad %uint %fragmentID
         %91 = OpAccessChain %_ptr_StorageBuffer_uint %_ %int_0
         %92 = OpLoad %uint %91
         %93 = OpIEqual %bool %84 %92
         %94 = OpGroupNonUniformBallot %v4uint %uint_3 %93
               OpStore %terminateSubgroupBallot %94
         %97 = OpLoad %v4uint %terminateSubgroupBallot
               OpStore %param_1 %97
         %98 = OpFunctionCall %uint %findBallotLSB_vu4_ %param_1
               OpStore %terminateInvocationID %98
        %101 = OpLoad %uint %terminateInvocationID
        %102 = OpLoad %uint %gl_SubgroupSize
        %103 = OpULessThan %bool %101 %102
               OpStore %terminateSubgroup %103
        %106 = OpGroupNonUniformBallot %v4uint %uint_3 %true
               OpStore %param_2 %106
        %109 = OpLoad %uint %terminateInvocationID
               OpStore %param_3 %109
        %110 = OpFunctionCall %v4uint %ballotResetBit_vu4_u1_ %param_2 %param_3
               OpStore %referenceBallot %110
        %111 = OpLoad %bool %terminateSubgroup
               OpSelectionMerge %113 None
               OpBranchConditional %111 %112 %113
        %112 = OpLabel
        %115 = OpLoad %uint %gl_SubgroupInvocationID
        %116 = OpLoad %uint %terminateInvocationID
        %117 = OpIEqual %bool %115 %116
               OpBranch %113
        %113 = OpLabel
        %118 = OpPhi %bool %111 %5 %117 %112
               OpSelectionMerge %120 None
               OpBranchConditional %118 %119 %120
        %119 = OpLabel
               OpTerminateInvocation
        %120 = OpLabel
        %123 = OpGroupNonUniformBallot %v4uint %uint_3 %true
               OpStore %resultBallot %123
        %127 = OpLoad %bool %gl_HelperInvocation
        %128 = OpLogicalNot %bool %127
        %129 = OpGroupNonUniformBallot %v4uint %uint_3 %128
               OpStore %nonHelperBallot %129
        %131 = OpLoad %v4uint %nonHelperBallot
        %132 = OpGroupNonUniformBallotFindLSB %uint %uint_3 %131
               OpStore %writeInvocation %132
        %133 = OpLoad %bool %terminateSubgroup
               OpSelectionMerge %135 None
               OpBranchConditional %133 %134 %135
        %134 = OpLabel
        %136 = OpLoad %uint %gl_SubgroupInvocationID
        %137 = OpLoad %uint %writeInvocation
        %138 = OpIEqual %bool %136 %137
               OpBranch %135
        %135 = OpLabel
        %139 = OpPhi %bool %133 %120 %138 %134
               OpSelectionMerge %141 None
               OpBranchConditional %139 %140 %141
        %140 = OpLabel
        %145 = OpLoad %v4uint %resultBallot
        %146 = OpLoad %v4uint %referenceBallot
        %148 = OpIEqual %v4bool %145 %146
        %149 = OpAll %bool %148
        %151 = OpSelect %int %149 %int_1 %int_0
        %152 = OpBitcast %uint %151
        %153 = OpAccessChain %_ptr_StorageBuffer_uint %__0 %int_0
               OpStore %153 %152
               OpBranch %141
        %141 = OpLabel
               OpStore %dEQP_FragColor %157
               OpReturn
               OpFunctionEnd
%resetBit_vu4_u1_ = OpFunction %void None %10
     %ballot = OpFunctionParameter %_ptr_Function_v4uint
        %bit = OpFunctionParameter %_ptr_Function_uint
         %14 = OpLabel
         %24 = OpLoad %uint %bit
         %27 = OpLoad %uint %gl_SubgroupSize
         %29 = OpULessThan %bool %24 %27
               OpSelectionMerge %31 None
               OpBranchConditional %29 %30 %31
         %30 = OpLabel
         %32 = OpLoad %uint %bit
         %34 = OpUDiv %uint %32 %uint_32
         %37 = OpLoad %uint %bit
         %38 = OpUMod %uint %37 %uint_32
         %39 = OpShiftLeftLogical %uint %uint_1 %38
         %40 = OpBitwiseXor %uint %uint_4294967295 %39
         %41 = OpAccessChain %_ptr_Function_uint %ballot %34
         %42 = OpLoad %uint %41
         %43 = OpBitwiseAnd %uint %42 %40
         %44 = OpAccessChain %_ptr_Function_uint %ballot %34
               OpStore %44 %43
               OpBranch %31
         %31 = OpLabel
               OpReturn
               OpFunctionEnd
%ballotResetBit_vu4_u1_ = OpFunction %v4uint None %15
   %ballot_0 = OpFunctionParameter %_ptr_Function_v4uint
      %bit_0 = OpFunctionParameter %_ptr_Function_uint
         %19 = OpLabel
      %param = OpVariable %_ptr_Function_v4uint Function
    %param_0 = OpVariable %_ptr_Function_uint Function
         %46 = OpLoad %v4uint %ballot_0
               OpStore %param %46
         %48 = OpLoad %uint %bit_0
               OpStore %param_0 %48
         %49 = OpFunctionCall %void %resetBit_vu4_u1_ %param %param_0
         %50 = OpLoad %v4uint %param
               OpStore %ballot_0 %50
         %51 = OpLoad %v4uint %ballot_0
               OpReturnValue %51
               OpFunctionEnd
%findBallotLSB_vu4_ = OpFunction %uint None %20
   %ballot_1 = OpFunctionParameter %_ptr_Function_v4uint
         %23 = OpLabel
         %59 = OpVariable %_ptr_Function_uint Function
         %54 = OpLoad %v4uint %ballot_1
         %56 = OpGroupNonUniformBallotBitCount %uint %uint_3 Reduce %54
         %58 = OpUGreaterThan %bool %56 %uint_0
               OpSelectionMerge %61 None
               OpBranchConditional %58 %60 %64
         %60 = OpLabel
         %62 = OpLoad %v4uint %ballot_1
         %63 = OpGroupNonUniformBallotFindLSB %uint %uint_3 %62
               OpStore %59 %63
               OpBranch %61
         %64 = OpLabel
               OpStore %59 %uint_4294967295
               OpBranch %61
         %61 = OpLabel
         %65 = OpLoad %uint %59
               OpReturnValue %65
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- `createAmberFragmentTestCases` creates an Amber test with the `terminate_invocation.amber` file under `reconvergence/maximal/fragment`, attaches the maximal-reconvergence support callback, and registers the case as `maximal.fragment.terminate_invocation` [Amber registration](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7951-L8069).
- The Amber script renders a triangle into a 16 by 16 framebuffer. It binds `fragments` as a read-only storage buffer at binding 0 and `result` as a storage buffer at binding 1, initializes `fragments[0]` to `136`, and expects `result[0] == 1` [Amber setup](../../../data/vulkan/amber/reconvergence/maximal/fragment/terminate_invocation.amber#L51-L80).
- For each fragment, the shader computes `fragmentID`. If the ID matches `fragment`, it finds the first matching lane, clears that lane from the reference ballot, terminates that lane, and computes `resultBallot` after termination.
- The first non-helper invocation writes `1` only if `resultBallot == referenceBallot`; it writes `0` for a mismatch. If no invocation in the subgroup matches `fragment`, the conditional result write is skipped, so the test's fixed input and rasterization must produce a matching subgroup.
- The fragment output is `vec4(1.0)` so the framebuffer itself supplies a stable render target while `Y.result` carries the tested value.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `subgroup_uniform_control_flow_elect` | Incorrect subgroup-uniform reconvergence or `subgroupElect()` result in generated divergent control flow. |
| `subgroup_uniform_control_flow_ballot` | Incorrect subgroup-uniform reconvergence or subgroup ballot mask in generated divergent control flow. |
| `workgroup_uniform_control_flow_elect` | Incorrect workgroup-uniform control-flow behavior or `subgroupElect()` result. |
| `workgroup_uniform_control_flow_ballot` | Incorrect workgroup-uniform control-flow behavior or subgroup ballot mask. |
| `maximal` | Incorrect maximal-reconvergence execution, including failure to remove the terminated invocation from the later ballot. |

### Cause Analysis

#### Termination or maximal-reconvergence ballot mismatch

**Possible failure symptoms:** The Amber check reads `Y.result == 0` instead of `1`, which means the post-termination `resultBallot` differs from the reference ballot with the selected lane cleared.

**Possible implementation causes:** The implementation may keep the terminated invocation active for the later ballot, reconverge the subgroup incorrectly, or lower `terminateInvocation` or subgroup ballot operations incorrectly. The Vulkan feature and shader evidence establish the required execution mode and the source comparison; the exact implementation cause requires investigation of the failing device and shader.

#### Helper-invocation result-write mismatch

**Possible failure symptoms:** The ballot comparison is correct in shader logic but `Y.result` remains unchanged or contains an unexpected value because the designated non-helper writer did not perform the store.

**Possible implementation causes:** A fragment helper-invocation or subgroup-ballot result may be handled incorrectly, or the host-side Amber resource binding may be wrong. The source does not justify assigning this symptom to a particular driver, hardware, or host component without examining the failure.

#### Generated-family mismatch

**Possible failure symptoms:** A generated compute case logs a missing expected full-mask/election observation or an element mismatch against its CPU reference.

**Possible implementation causes:** The implementation may apply the selected uniform-control-flow or maximal-reconvergence mode incorrectly across generated branches, loops, switches, calls, or returns. The source defines the reference and comparison rules; a specific implementation cause requires investigation of that generated case.

## Case Pruning

### Requirement-based pruning

- Generated cases require Vulkan 1.1, subgroup support for the selected stage, and compute dimensions within device limits.
- Elect cases require `VK_SUBGROUP_FEATURE_BASIC_BIT`; ballot cases require `VK_SUBGROUP_FEATURE_BALLOT_BIT`.
- Uniform-control-flow cases require `shaderSubgroupUniformControlFlow`; maximal cases require `shaderMaximalReconvergence` [support checks](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L4395-L4433).
- The Amber `terminate_invocation` case requires fragment subgroup support, maximal reconvergence, subgroup ballot support, subgroup size at least 4, and `shaderTerminateInvocation` [Amber support callback](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L8018-L8043).
- Non-compute generated stages are skipped unless the family is `TT_MAXIMAL`. Vertex, tessellation, and geometry paths remain behind the disabled `INCLUDE_GRAPHICS_TESTS` block [stage list](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L69-L69), [stage filter](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7805-L7814).

### Design-based pruning

- Non-maximal families skip nesting levels 5 and 6. Maximal compute keeps them [nesting filter](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7868-L7872).
- Maximal fragment cases set `nNdx = 7`, register the fixed Amber cases, and skip generated nesting groups [fragment branch](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7827-L7837).
- Generated indices are divided by `numTests / 5` between the main and experimental packages. This changes coverage placement, not the generated family semantics [experimental split](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7929-L7933).
- SUCF generation retries until the CPU simulation observes a nonuniform ballot result, so the selected UCF behavior has an observable case [random program generation](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L1612-L1633).

## Key Takeaways

- The five generated families share a random control-flow generator but test different uniform-control-flow or maximal-reconvergence contracts.
- The fixed Amber path `maximal.fragment.terminate_invocation` is an exact fragment-shader case: it removes one selected lane from a reference ballot, terminates that lane, and compares the later ballot.
- The test writes its pass signal to a storage buffer, not to the color attachment. The color output only keeps the graphics pipeline valid.
- The main and experimental packages preserve the same root and family identifiers while partitioning generated leaves.
- `terminate_invocation` is a direct root child with delegated implementation. The maximal fragment Amber cases are registered by the main implementation file.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Root declarations | [vktReconvergenceTests.hpp](../../../modules/vulkan/reconvergence/vktReconvergenceTests.hpp#L30-L36) | Declares main and experimental root constructors. |
| Package registration | [vktTestPackage.cpp](../../../modules/vulkan/vktTestPackage.cpp#L1387-L1407) | Registers both `reconvergence` roots. |
| Generated root builder | [createTests](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7786-L7948) | Registers five generated families and appends delegated `terminate_invocation`. |
| Amber fragment registration | [createAmberFragmentTestCases](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7951-L8069) | Registers fixed maximal fragment leaves and support checks. |
| Amber source | [terminate_invocation.amber](../../../data/vulkan/amber/reconvergence/maximal/fragment/terminate_invocation.amber#L5-L80) | Provides the exact representative GLSL, pipeline, buffers, and expected result. |
| Delegated registration | [createTerminateInvocationTests](../../../modules/vulkan/reconvergence/vktReconvergenceTerminateInvocationTests.cpp#L653-L675) | Registers the four delegated leaves. |
| Generated support checks | [checkSupport](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L4395-L4433) | Defines API, subgroup operation, stage, UCF, maximal, and compute-limit gates. |
| Generated shader setup | [initPrograms](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L4547-L5037) | Emits random GLSL, resource layouts, execution attributes, and SPIR-V target 1.3. |
| Generated comparison | [compute result checking](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L5278-L5420) | Runs the CPU reference and applies maximal/SUCF comparison rules. |
|| Vulkan feature evidence | [uniform-control-flow feature](../../../../vulkan-docs/src/chapters/features.adoc#L5147-L5170), [maximal-reconvergence feature](../../../../vulkan-docs/src/chapters/features.adoc#L8602-L8624) | Connects CTS support checks to the Vulkan feature fields and SPIR-V execution modes. |
|| Vulkan maximal execution rule | [shader execution](../../../../vulkan-docs/src/chapters/shaders.adoc#L3755-L3767) | Grounds the helper-invocation behavior for maximal reconvergence. |
| Build inventory | [CMakeLists.txt](../../../modules/vulkan/reconvergence/CMakeLists.txt#L7-L12) | Shows the reconvergence sources included in the build. |
