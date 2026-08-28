## Overview

**Core question:** Do subgroup vote operations return the required collective result for every active invocation across the supported shader and execution variants?

- This page covers the implementation-bearing `subgroups.vote` test family in [`vktSubgroupsVoteTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsVoteTests.cpp#L1).
- The tests exercise all, any, and all-equal votes through compute, graphics, framebuffer, fragment-helper, mesh, and ray-tracing paths, plus legacy `VK_EXT_shader_subgroup_vote` operations.
- Shaders encode several expected vote outcomes in a bit mask. Shared harnesses return those masks to host callbacks that check every result element.

## Background Knowledge

For the shared concepts subgroup identity, active invocations, and collective result shapes, see [Background Knowledge](../../categories/subgroups.md#background-knowledge) of the `subgroups` page.

- **Active invocations.** A vote covers active invocations in the subgroup. Fragment helper invocations need special handling because they may execute the shader without representing ordinary rasterized samples.
- **Vote capability.** `VK_SUBGROUP_FEATURE_VOTE_BIT` indicates that the implementation accepts SPIR-V with `GroupNonUniformVote`; support for a given shader stage is checked separately.

## Registration Hierarchy

```text
subgroups.vote
├── graphics
├── compute
├── framebuffer
├── frag_helper
├── ray_tracing
├── mesh
└── ext_shader_subgroup_vote
```

`ray_tracing` and `mesh` are not registered in Vulkan SC builds. The legacy extension branch contains its own `graphics`, `compute`, `framebuffer`, `frag_helper`, and `mesh` intermediate nodes.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Execution path | `graphics`, `compute`, `framebuffer`, `frag_helper`, `ray_tracing`, `mesh` | Selects the shader stages, result transport, and shared harness used to run the same vote checks. | [`createSubgroupsVoteTests`](../../../modules/vulkan/subgroups/vktSubgroupsVoteTests.cpp#L545-L765) |
| Vote API | Core subgroup operations; `ext_shader_subgroup_vote` | Chooses `subgroupAll`, `subgroupAny`, and `subgroupAllEqual`, or the legacy ARB-named forms enabled by `VK_EXT_shader_subgroup_vote`. | [`getOpTypeName` and `getExtensions`](../../../modules/vulkan/subgroups/vktSubgroupsVoteTests.cpp#L109-L140) |
| Value type | `uint` for all/any; supported scalar and vector types for all-equal | All/any consume boolean predicates. All-equal also checks typed equality across subgroup invocations. | [format pruning loops](../../../modules/vulkan/subgroups/vktSubgroupsVoteTests.cpp#L578-L610) |
| Required subgroup size | absent, `_requiredsubgroupsize` | Repeats compute and mesh execution for each supported power-of-two subgroup size. | [required-size registration and execution](../../../modules/vulkan/subgroups/vktSubgroupsVoteTests.cpp#L623-L659) |
| Framebuffer stage | `vertex`, `tess_control`, `tess_eval`, `geometry`; fragment through `frag_helper` | Runs vote logic where SSBO output may not be the selected result path and isolates helper-fragment behavior. | [framebuffer registration](../../../modules/vulkan/subgroups/vktSubgroupsVoteTests.cpp#L664-L709) |

The default mustpass list contains 805 executable leaves below `dEQP-VK.subgroups.vote`: 124 compute, 62 graphics, 248 framebuffer, 62 fragment-helper, 25 ray-tracing, 248 mesh, and 36 legacy-extension leaves.

## Behavior Parameters

The primary behavioral axis is the **vote operation**. Core and legacy spellings are paired because they ask the same collective question, while registration and extension requirements remain separate.

### `subgroupAll` / `allInvocationsARB`: all predicates are true

The shader checks a predicate that is true for all invocations, one that is false for all invocations, and an invocation-indexed input predicate on the compute path. The encoded bits distinguish the required true and false outcomes.

### `subgroupAny` / `anyInvocationARB`: at least one predicate is true

This operation uses the same controlled predicate pattern but asks whether any active invocation supplies true. Uniform true and false expressions give deterministic positive and negative checks.

### `subgroupAllEqual` / `allInvocationsEqualARB`: all values compare equal

The shader supplies constant, uniform-buffer-derived, and invocation-varying expressions. It expects uniform expressions to compare equal and invocation-varying expressions not to compare equal when more than one invocation is present. The elected invocation always fills the two negative-test bits. This makes a one-active-invocation subgroup pass, while the other active invocations still exercise those negative checks in a larger subgroup.

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.subgroups.vote.compute.subgroupallequal_uint
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `compute` | Uses the SSBO-backed compute path generated by `initPrograms`. |
| `subgroupallequal_uint` | Selects core `subgroupAllEqual` with 32-bit unsigned scalar values and no required subgroup size. |
| Default subgroup size | Lets the implementation choose subgroup size; the shader still handles a one-invocation subgroup. |

#### Purpose

This shader checks that `subgroupAllEqual` accepts uniform values and rejects invocation-varying values. Non-elected invocations write `0x1F` only when all five expected outcomes are represented; the elected invocation always supplies the two negative-test bits so a one-active-invocation subgroup can pass.

#### Structural Design

| Phase | Shader action | Expected bits |
|-------|---------------|---------------|
| Address | Flatten `gl_GlobalInvocationID` to one output index. | none |
| Prepare | Build constant, buffer-derived, and invocation-varying `uint` values. | none |
| Vote | Run five `subgroupAllEqual` expressions. | `0x01`, `0x02`, `0x04`, `0x08`, `0x10` |
| Elected-invocation safeguard | Let the elected invocation always supply the unequal-case bits; other active invocations test those outcomes when an unequal pair can exist. | `0x02 | 0x10` |
| Report | Store `tempRes` in the per-invocation result slot. | `0x1F` means success |

#### Shader Code

```glsl
#version 450
#extension GL_KHR_shader_subgroup_vote: enable
layout (local_size_x_id = 0, local_size_y_id = 1, local_size_z_id = 2) in;
/// Binding 0 is an std430 result buffer with one uint mask per global invocation.
layout(set = 0, binding = 0, std430) buffer Buffer1
{
  uint result[];
};
/// Binding 1 is an std430 input buffer initialized to zero for this all-equal case.
layout(set = 0, binding = 1, std430) buffer Buffer2
{
  uint data[];
};
void main (void)
{
  /// Flatten the global invocation coordinates to select this invocation's result element.
  uvec3 globalSize = gl_NumWorkGroups * gl_WorkGroupSize;
  highp uint offset = globalSize.x * ((globalSize.y * gl_GlobalInvocationID.z) + gl_GlobalInvocationID.y) + gl_GlobalInvocationID.x;
  uint tempRes;
  /// Build values that are uniform and nonuniform across the subgroup.
  uint valueEqual = uint(1.25 * float(data[gl_SubgroupInvocationID]) + 5.0);
  uint valueNoEqual = uint(gl_SubgroupInvocationID);
  /// Set one bit for each expected all-equal outcome.
  tempRes = subgroupAllEqual(uint(1)) ? 0x1 : 0;
  tempRes |= subgroupAllEqual(uint(gl_SubgroupInvocationID)) ? 0 : 0x2;
  tempRes |= subgroupAllEqual(data[0]) ? 0x4 : 0;
  tempRes |= subgroupAllEqual(valueEqual) ? 0x8 : 0x0;
  tempRes |= subgroupAllEqual(valueNoEqual) ? 0x0 : 0x10;
  /// Always supply the two negative-test bits for the elected invocation; other active invocations test them in larger subgroups.
  if (subgroupElect()) tempRes |= 0x2 | 0x10;
  result[offset] = tempRes;
}
```

#### Additional Info

- `initPrograms` explicitly selects SPIR-V 1.3 for this compute case; mesh and ray-tracing selections can raise the target to SPIR-V 1.4.
- The input buffer uses zero initialization for all-equal operations, making `data[0]` and the invocation-indexed `data[...]` expression uniform in this representative case.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Vote operation | `subgroupAll` and `subgroupAny` replace the five typed equality checks with controlled true, false, and compute-input predicates. | [`getStageTestSource`](../../../modules/vulkan/subgroups/vktSubgroupsVoteTests.cpp#L142-L186) |
| Value type | All-equal cases change the type of `data`, `valueEqual`, and `valueNoEqual`; boolean values use `subgroupElect()` for the nonuniform expression. | [`getStageTestSource`](../../../modules/vulkan/subgroups/vktSubgroupsVoteTests.cpp#L166-L184) |
| Shader stage | The shared builder changes stage declarations, addressing, and result transport while inserting the same generated vote body. | [`initStdPrograms`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L1406-L1504) |
| Legacy extension | The extension path enables `GL_ARB_shader_group_vote` and substitutes ARB-named operations. | [`getOpTypeName` and `getExtensions`](../../../modules/vulkan/subgroups/vktSubgroupsVoteTests.cpp#L109-L140) |

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
; Bound: 109
; Schema: 0
               OpCapability Shader
               OpCapability GroupNonUniform
               OpCapability GroupNonUniformVote
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_NumWorkGroups %gl_GlobalInvocationID %gl_SubgroupInvocationID
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpSourceExtension "GL_KHR_shader_subgroup_basic"
               OpSourceExtension "GL_KHR_shader_subgroup_vote"
               OpName %main "main"
               OpName %globalSize "globalSize"
               OpName %gl_NumWorkGroups "gl_NumWorkGroups"
               OpName %offset "offset"
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
               OpName %valueEqual "valueEqual"
               OpName %Buffer2 "Buffer2"
               OpMemberName %Buffer2 0 "data"
               OpName %_ ""
               OpName %gl_SubgroupInvocationID "gl_SubgroupInvocationID"
               OpName %valueNoEqual "valueNoEqual"
               OpName %tempRes "tempRes"
               OpName %Buffer1 "Buffer1"
               OpMemberName %Buffer1 0 "result"
               OpName %__0 ""
               OpDecorate %gl_NumWorkGroups BuiltIn NumWorkgroups
               OpDecorate %13 SpecId 0
               OpDecorate %14 SpecId 1
               OpDecorate %15 SpecId 2
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %_runtimearr_uint ArrayStride 4
               OpDecorate %Buffer2 Block
               OpMemberDecorate %Buffer2 0 Offset 0
               OpDecorate %_ Binding 1
               OpDecorate %_ DescriptorSet 0
               OpDecorate %gl_SubgroupInvocationID RelaxedPrecision
               OpDecorate %gl_SubgroupInvocationID BuiltIn SubgroupLocalInvocationId
               OpDecorate %49 RelaxedPrecision
               OpDecorate %59 RelaxedPrecision
               OpDecorate %67 RelaxedPrecision
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
      %float = OpTypeFloat 32
 %float_1_25 = OpConstant %float 1.25
%_runtimearr_uint = OpTypeRuntimeArray %uint
    %Buffer2 = OpTypeStruct %_runtimearr_uint
%_ptr_StorageBuffer_Buffer2 = OpTypePointer StorageBuffer %Buffer2
          %_ = OpVariable %_ptr_StorageBuffer_Buffer2 StorageBuffer
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%gl_SubgroupInvocationID = OpVariable %_ptr_Input_uint Input
%_ptr_StorageBuffer_uint = OpTypePointer StorageBuffer %uint
    %float_5 = OpConstant %float 5
       %bool = OpTypeBool
     %uint_3 = OpConstant %uint 3
      %int_1 = OpConstant %int 1
      %int_2 = OpConstant %int 2
      %int_4 = OpConstant %int 4
      %int_8 = OpConstant %int 8
     %int_16 = OpConstant %int 16
    %uint_18 = OpConstant %uint 18
%_runtimearr_uint_0 = OpTypeRuntimeArray %uint
    %Buffer1 = OpTypeStruct %_runtimearr_uint_0
%_ptr_StorageBuffer_Buffer1 = OpTypePointer StorageBuffer %Buffer1
        %__0 = OpVariable %_ptr_StorageBuffer_Buffer1 StorageBuffer
       %main = OpFunction %void None %3
          %5 = OpLabel
 %globalSize = OpVariable %_ptr_Function_v3uint Function
     %offset = OpVariable %_ptr_Function_uint Function
 %valueEqual = OpVariable %_ptr_Function_uint Function
%valueNoEqual = OpVariable %_ptr_Function_uint Function
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
         %49 = OpLoad %uint %gl_SubgroupInvocationID
         %51 = OpAccessChain %_ptr_StorageBuffer_uint %_ %int_0 %49
         %52 = OpLoad %uint %51
         %53 = OpConvertUToF %float %52
         %54 = OpFMul %float %float_1_25 %53
         %56 = OpFAdd %float %54 %float_5
         %57 = OpConvertFToU %uint %56
               OpStore %valueEqual %57
         %59 = OpLoad %uint %gl_SubgroupInvocationID
               OpStore %valueNoEqual %59
         %63 = OpGroupNonUniformAllEqual %bool %uint_3 %uint_1
         %65 = OpSelect %int %63 %int_1 %int_0
         %66 = OpBitcast %uint %65
               OpStore %tempRes %66
         %67 = OpLoad %uint %gl_SubgroupInvocationID
         %68 = OpGroupNonUniformAllEqual %bool %uint_3 %67
         %70 = OpSelect %int %68 %int_0 %int_2
         %71 = OpBitcast %uint %70
         %72 = OpLoad %uint %tempRes
         %73 = OpBitwiseOr %uint %72 %71
               OpStore %tempRes %73
         %74 = OpAccessChain %_ptr_StorageBuffer_uint %_ %int_0 %int_0
         %75 = OpLoad %uint %74
         %76 = OpGroupNonUniformAllEqual %bool %uint_3 %75
         %78 = OpSelect %int %76 %int_4 %int_0
         %79 = OpBitcast %uint %78
         %80 = OpLoad %uint %tempRes
         %81 = OpBitwiseOr %uint %80 %79
               OpStore %tempRes %81
         %82 = OpLoad %uint %valueEqual
         %83 = OpGroupNonUniformAllEqual %bool %uint_3 %82
         %85 = OpSelect %int %83 %int_8 %int_0
         %86 = OpBitcast %uint %85
         %87 = OpLoad %uint %tempRes
         %88 = OpBitwiseOr %uint %87 %86
               OpStore %tempRes %88
         %89 = OpLoad %uint %valueNoEqual
         %90 = OpGroupNonUniformAllEqual %bool %uint_3 %89
         %92 = OpSelect %int %90 %int_0 %int_16
         %93 = OpBitcast %uint %92
         %94 = OpLoad %uint %tempRes
         %95 = OpBitwiseOr %uint %94 %93
               OpStore %tempRes %95
         %96 = OpGroupNonUniformElect %bool %uint_3
               OpSelectionMerge %98 None
               OpBranchConditional %96 %97 %98
         %97 = OpLabel
        %100 = OpLoad %uint %tempRes
        %101 = OpBitwiseOr %uint %100 %uint_18
               OpStore %tempRes %101
               OpBranch %98
         %98 = OpLabel
        %106 = OpLoad %uint %offset
        %107 = OpLoad %uint %tempRes
        %108 = OpAccessChain %_ptr_StorageBuffer_uint %__0 %int_0 %106
               OpStore %108 %107
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The support check requires subgroup support, `VK_SUBGROUP_FEATURE_VOTE_BIT`, the selected value format, and the selected shader stage. Legacy cases also require `VK_EXT_shader_subgroup_vote`.
- All-equal cases initialize their input data to zero; all and any cases use nonzero data. Compute, graphics, mesh, and ray-tracing paths use `std430` storage buffers. Framebuffer paths use a `std140` uniform buffer and return masks through framebuffer output.
- `initPrograms` delegates shader generation to `initStdPrograms`. `initFrameBufferPrograms` and `initFrameBufferProgramsFrag` use separate framebuffer builders because their stage interfaces and fragment-helper observations differ.
- Compute and mesh cases with `_requiredsubgroupsize` run once for every power-of-two size from `minSubgroupSize` through `maxSubgroupSize`. A failure at any size ends the test.
- The ordinary callbacks require `0x1F` for every result. Fragment-helper checking uses the low five bits and expects `0x1F` if helper execution was recorded, otherwise `0x1E`.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `subgroupAll` / `allInvocationsARB` | Incorrect all-active-invocations reduction, active-invocation handling, or legacy operation lowering. |
| `subgroupAny` / `anyInvocationARB` | Incorrect any-active-invocation reduction, active-invocation handling, or legacy operation lowering. |
| `subgroupAllEqual` / `allInvocationsEqualARB` | Incorrect equality comparison or collective reduction for uniform and nonuniform typed values, including legacy operation lowering. |

Failures shared across operation values can also come from stage-specific result transport, descriptor/input setup, output writes, or host readback rather than the vote operation itself.

### Cause Analysis

#### All-vote reduction or active-invocation handling

**Possible failure symptoms:** at least one checked output lacks an expected bit, so its result differs from `0x1F`; fragment-helper output may differ from its expected `0x1F` or `0x1E` low-bit mask.

**Possible implementation causes:** lowering of `OpGroupNonUniformAll` or the legacy all-invocations operation may combine the wrong active invocations or invert a predicate result. Stage-specific active-invocation handling can also produce the wrong collective value.

#### Any-vote reduction or active-invocation handling

**Possible failure symptoms:** a predicate controlled to be true for all invocations or false for all invocations produces the wrong bit, or a fragment-helper mask does not match whether helper execution was observed.

**Possible implementation causes:** lowering of `OpGroupNonUniformAny` or the legacy any-invocation operation may combine the active predicates incorrectly. Fragment execution can expose a separate error in the active set used by the vote.

#### Typed all-equal comparison and reduction

**Possible failure symptoms:** constant and uniform values do not set their positive bits, invocation-varying values do not set their negative bits, or the result changes incorrectly for a supported scalar/vector format.

**Possible implementation causes:** `OpGroupNonUniformAllEqual` lowering may compare typed values incorrectly, use the wrong active set, or mishandle the single-invocation case. A compiler error in generating the selected 8-, 16-, 32-, or 64-bit comparison can affect only part of the format matrix.

#### Shared execution or result-transport path

**Possible failure symptoms:** several operations fail in one stage family, outputs contain missing or unrelated bits, or readback reports mismatches despite otherwise consistent operation behavior.

**Possible implementation causes:** descriptor binding, stage interface transport, shader output writes, framebuffer conversion/readback, or shared harness synchronization may corrupt the mask independently of vote semantics. Source-level investigation is needed to distinguish these paths from a collective-operation defect.

## Case Pruning

### Requirement-based pruning

- Cases require subgroup support, `VK_SUBGROUP_FEATURE_VOTE_BIT`, support for the selected stage and format, and 8- or 16-bit uniform-buffer storage when a framebuffer input type needs it.
- Legacy ARB-named cases require `VK_EXT_shader_subgroup_vote`.
- Required-size cases require `VK_EXT_subgroup_size_control`, `subgroupSizeControl`, `computeFullSubgroups`, and required-size support for the selected stage.
- Mesh cases require `VK_EXT_mesh_shader` and the corresponding mesh/task feature. Ray-tracing cases require `VK_KHR_ray_tracing_pipeline`. These branches are absent in Vulkan SC.

### Design-based pruning

- Core `subgroupAll` and `subgroupAny` are generated only for scalar `uint`; their predicates are boolean, so additional typed cases would not add typed equality coverage.
- Core `subgroupAllEqual` spans the format list because value equality is the behavior under test.
- Legacy all/any functions accept scalar boolean arguments, so vector formats are excluded. `allInvocationsEqualARB` is restricted to scalar `bool` by this registration design.
- Required-subgroup-size variants are generated only for compute and mesh paths. Ray-tracing has no legacy-extension or required-size branch here.

## Key Takeaways

- The three operation values test distinct collective questions: all true, any true, and all values equal.
- Each shader encodes several positive and negative expectations in a five-bit mask; a pass requires the expected mask at every checked output.
- All-equal coverage carries the broad type matrix, while all and any focus on predicate behavior.
- The shared vote body is exercised through several stage and resource paths, with fragment helpers and required subgroup sizes receiving dedicated handling.
- See `## Failure Meaning` to separate likely vote-operation failures from shared execution and result-transport failures.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Operation and shader-body generation | [`getOpTypeName`, `getExtensions`, and `getStageTestSource`](../../../modules/vulkan/subgroups/vktSubgroupsVoteTests.cpp#L109-L186) | Maps operation values to GLSL calls and expected result bits. |
| Framebuffer shader generation | [`initFrameBufferPrograms` and `initFrameBufferProgramsFrag`](../../../modules/vulkan/subgroups/vktSubgroupsVoteTests.cpp#L188-L303) | Builds framebuffer and helper-fragment variants with explicit SPIR-V targets. |
| Primary shader builder | [`initPrograms`](../../../modules/vulkan/subgroups/vktSubgroupsVoteTests.cpp#L305-L321) | Configures `initStdPrograms` for compute, graphics, mesh, and ray tracing. |
| Support checks | [`supportedCheck` and `ssboTestSupportCheck`](../../../modules/vulkan/subgroups/vktSubgroupsVoteTests.cpp#L323-L405) | Defines feature, extension, stage, format, and required-size gates. |
| Runtime selection | [`noSSBOtest` and `test`](../../../modules/vulkan/subgroups/vktSubgroupsVoteTests.cpp#L407-L540) | Selects framebuffer, compute, graphics, mesh, and ray-tracing harnesses. |
| Registration matrix | [`createSubgroupsVoteTests`](../../../modules/vulkan/subgroups/vktSubgroupsVoteTests.cpp#L545-L767) | Generates the exact hierarchy, leaves, and design-based exclusions. |
| Shared shader wrappers | [`initStdFrameBufferPrograms` and `initStdPrograms`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L1275-L1434) | Supplies stage declarations, resources, addressing, and result writes. |
| Shared mask checks | [`check` and `checkComputeOrMesh`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L2640-L2663) | Requires the expected value for every output element. |
| Vulkan vote semantics | [Vote Group Operations](../../../../vulkan-docs/src/chapters/shaders.adoc#L3477-L3492) | Defines the collective all, any, and all-equal questions. |
| Vulkan vote feature | [`VK_SUBGROUP_FEATURE_VOTE_BIT`](../../../../vulkan-docs/src/chapters/limits.adoc#L1428-L1446) | Defines support for `GroupNonUniformVote`. |
