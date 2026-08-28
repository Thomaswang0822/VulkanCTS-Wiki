## Overview

**Core question:** Does every subgroup in one compute dispatch report the same subgroup size when the pipeline allows the implementation to vary that size?

- The `subgroups.multiple_dispatches` test family contains one test case, `uniform_subgroup_size`. [vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp](../../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp) implements both the family and case.
- The host creates compute pipelines for power-of-two local sizes and sets `VK_PIPELINE_SHADER_STAGE_CREATE_ALLOW_VARYING_SUBGROUP_SIZE_BIT_EXT` on every pipeline.
- One elected invocation per subgroup writes `gl_SubgroupSize` to a host-readable storage buffer.
- For each dispatch, the host requires every nonzero report to match and requires the report count to equal the number of subgroups implied by the local size and reported subgroup size.
- Separate dispatches may select different subgroup sizes. The tested Vulkan rule requires uniformity within each compute command scope.

## Background Knowledge

For the shared concepts subgroup identity, collective result shapes, and subgroup-size control, see [Background Knowledge](../../categories/subgroups.md#background-knowledge) of the `subgroups` page.

- **Command scope.** The invocations produced by one `vkCmdDispatch` form one command scope instance. A later dispatch forms a different command scope, even if it uses the same shader and descriptor set [shaders.adoc](../../../../vulkan-docs/src/chapters/shaders.adoc#L3104-L3127).

## Registration Hierarchy

```text
subgroups.multiple_dispatches
└── uniform_subgroup_size
```

The default mustpass list contains the exact executable path `dEQP-VK.subgroups.multiple_dispatches.uniform_subgroup_size` [subgroups.txt](../../../mustpass/main/vk-default/subgroups.txt#L22567).

## Parameter Dimensions and Observed Values

| Dimension | Registered or observed values | Meaning in this test | Evidence |
|-----------|-------------------------------|----------------------|----------|
| Test case leaf | `uniform_subgroup_size` | Selects the only executable case in the `multiple_dispatches` test family. | [registration](../../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L301-L307), [mustpass](../../../mustpass/main/vk-default/subgroups.txt#L22567) |
| Local X size | `1, 2, 4, ...` through `maxComputeWorkGroupSize[0]` | Creates one pipeline and one dispatch for each power-of-two workgroup size. | [pipeline and dispatch loops](../../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L118-L160) |
| Pipeline stage flag | `VK_PIPELINE_SHADER_STAGE_CREATE_ALLOW_VARYING_SUBGROUP_SIZE_BIT_EXT` | Lets the implementation select a legal subgroup size while retaining command-scope uniformity requirements. | [pipeline stage creation](../../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L135-L155) |
| Dispatch dimensions | `1, 1, 1` workgroups | Keeps the shader's report array focused on the subgroups of one workgroup for each command scope. | [dispatch](../../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L172-L185) |
| Result capacity | `(maxLocalSize / minSubgroupSize + 1)` 32-bit entries | Covers the maximum subgroup-report count implied by the tested local-size range and minimum supported subgroup size, with one extra entry. | [buffer allocation](../../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L77-L87) |
| Shader build target | SPIR-V 1.3 | Fixes the target used to compile the generated GLSL. | [shader build options](../../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L289-L291) |

## Behavior Parameters

The primary behavioral axis is the fixed test case leaf `uniform_subgroup_size`. This test family has no registered multi-value behavioral axis. The power-of-two local sizes are internal pipeline and dispatch variants within that one case, not separate registered behavior values.

The fixed behavior asks the implementation to choose subgroup sizes under `VK_PIPELINE_SHADER_STAGE_CREATE_ALLOW_VARYING_SUBGROUP_SIZE_BIT_EXT`, then checks two linked properties for every local-size variant:

- all subgroup-size reports from one dispatch are equal;
- the number of reports is `ceil(localSize / reportedSubgroupSize)`.

The host repeats these checks independently for each dispatch. It does not require separate command scopes to choose the same subgroup size [validation loop](../../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L196-L240).

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.subgroups.multiple_dispatches.uniform_subgroup_size
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `uniform_subgroup_size` | Selects the only executable test case in the `multiple_dispatches` test family. |
| Compute stage | Runs one workgroup and exposes compute-specific `gl_NumSubgroups` and `gl_SubgroupID` values. |
| `local_size_x_id = 0` | Lets specialization constant ID `0` select each power-of-two X local size without changing the shader module. |
| Allow varying subgroup size | Permits an implementation-selected subgroup size while the test checks command-scope uniformity. |

#### Purpose

The compute shader records one subgroup-size value for every subgroup in the dispatched workgroup. The host uses those records to check command-scope uniformity and subgroup count.

#### Structural Design

| Shader step | Result used by the host |
|-------------|-------------------------|
| `subgroupElect()` selects one invocation per subgroup. | Exactly one invocation should report for each subgroup. |
| The elected invocation indexes `sizes` by workgroup and subgroup ID. | Each subgroup has a distinct result slot. |
| The elected invocation stores `gl_SubgroupSize`. | Nonzero entries expose the size reported by each subgroup. |

#### Shader Code

```glsl
#version 450
#extension GL_KHR_shader_subgroup_basic : enable
#extension GL_KHR_shader_subgroup_vote : enable
#extension GL_KHR_shader_subgroup_ballot : enable

/// Binding 0 is a host-visible storage buffer cleared before each dispatch.
/// One elected invocation per subgroup writes one subgroup-size report.
layout(std430, binding = 0) buffer Outputs { uint sizes[]; };

/// Specialization constant ID 0 supplies the X local size for each pipeline variant.
layout(local_size_x_id = 0) in;

void main()
{
    /// Elect one writer in each subgroup so the result count matches the subgroup count.
    if (subgroupElect())
    {
        /// The test dispatches one workgroup. gl_SubgroupID selects that subgroup's unique slot.
        sizes[gl_WorkGroupID.x * gl_NumSubgroups + gl_SubgroupID] = gl_SubgroupSize;
    }
}
```

#### Additional Info

- `MultipleDispatchesUniformSubgroupSize::initPrograms` emits this shader and supplies explicit `ShaderBuildOptions` for SPIR-V 1.3 [shader builder](../../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L270-L291).
- The host specializes constant ID `0` when it creates each compute pipeline [specialization setup](../../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L118-L155).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Local X size | The GLSL stays fixed; specialization constant ID `0` changes the `LocalSizeId` X value for each pipeline. | [local-size pipeline variants](../../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L118-L158) |
| Selected subgroup size | The GLSL does not request a specific size. The varying-size pipeline flag lets the implementation choose a legal value for each command scope. | [pipeline stage flag](../../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L135-L143) |
| Registered case | No other shader variants exist under this test family; registration adds only `uniform_subgroup_size`. | [case registration](../../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L301-L307) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed GLSL from this walkthrough
- Stage: `comp`
- Target SPIRV version: `spirv1.3`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.3
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 38
; Schema: 0
               OpCapability Shader
               OpCapability GroupNonUniform
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_WorkGroupID %gl_NumSubgroups %gl_SubgroupID %gl_SubgroupSize
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpSourceExtension "GL_KHR_shader_subgroup_ballot"
               OpSourceExtension "GL_KHR_shader_subgroup_basic"
               OpSourceExtension "GL_KHR_shader_subgroup_vote"
               OpName %main "main"
               OpName %Outputs "Outputs"
               OpMemberName %Outputs 0 "sizes"
               OpName %_ ""
               OpName %gl_WorkGroupID "gl_WorkGroupID"
               OpName %gl_NumSubgroups "gl_NumSubgroups"
               OpName %gl_SubgroupID "gl_SubgroupID"
               OpName %gl_SubgroupSize "gl_SubgroupSize"
               OpDecorate %_runtimearr_uint ArrayStride 4
               OpDecorate %Outputs Block
               OpMemberDecorate %Outputs 0 Offset 0
               OpDecorate %_ Binding 0
               OpDecorate %_ DescriptorSet 0
               OpDecorate %gl_WorkGroupID BuiltIn WorkgroupId
               OpDecorate %gl_NumSubgroups BuiltIn NumSubgroups
               OpDecorate %gl_SubgroupID BuiltIn SubgroupId
               OpDecorate %gl_SubgroupSize RelaxedPrecision
               OpDecorate %gl_SubgroupSize BuiltIn SubgroupSize
               OpDecorate %32 RelaxedPrecision
               OpDecorate %35 SpecId 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %bool = OpTypeBool
       %uint = OpTypeInt 32 0
     %uint_3 = OpConstant %uint 3
%_runtimearr_uint = OpTypeRuntimeArray %uint
    %Outputs = OpTypeStruct %_runtimearr_uint
%_ptr_StorageBuffer_Outputs = OpTypePointer StorageBuffer %Outputs
          %_ = OpVariable %_ptr_StorageBuffer_Outputs StorageBuffer
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_WorkGroupID = OpVariable %_ptr_Input_v3uint Input
     %uint_0 = OpConstant %uint 0
%_ptr_Input_uint = OpTypePointer Input %uint
%gl_NumSubgroups = OpVariable %_ptr_Input_uint Input
%gl_SubgroupID = OpVariable %_ptr_Input_uint Input
%gl_SubgroupSize = OpVariable %_ptr_Input_uint Input
%_ptr_StorageBuffer_uint = OpTypePointer StorageBuffer %uint
         %35 = OpSpecConstant %uint 1
     %uint_1 = OpConstant %uint 1
%gl_WorkGroupSize = OpSpecConstantComposite %v3uint %35 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
          %9 = OpGroupNonUniformElect %bool %uint_3
               OpSelectionMerge %11 None
               OpBranchConditional %9 %10 %11
         %10 = OpLabel
         %23 = OpAccessChain %_ptr_Input_uint %gl_WorkGroupID %uint_0
         %24 = OpLoad %uint %23
         %26 = OpLoad %uint %gl_NumSubgroups
         %27 = OpIMul %uint %24 %26
         %29 = OpLoad %uint %gl_SubgroupID
         %30 = OpIAdd %uint %27 %29
         %32 = OpLoad %uint %gl_SubgroupSize
         %34 = OpAccessChain %_ptr_StorageBuffer_uint %_ %int_0 %30
               OpStore %34 %32
               OpBranch %11
         %11 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The host checks `subgroupSizeControl`. It reports the case as unsupported if the feature is false [checkSupport](../../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L262-L268).
- It allocates one host-visible storage buffer and binds the full range at descriptor binding `0` [buffer and descriptor setup](../../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L77-L113).
- It creates one compute pipeline per power-of-two X local size. Each pipeline uses the same shader module, specialization constant ID `0`, and the varying-subgroup-size stage flag [pipeline setup](../../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L115-L158).
- Before each dispatch, `vkCmdFillBuffer` clears the report buffer. A transfer-to-compute buffer barrier makes the clear visible before shader writes [clear and fill barrier](../../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L160-L170).
- The host binds the matching pipeline and records `vkCmdDispatch(1, 1, 1)`. A compute-to-host memory barrier follows the dispatch, then the host submits, waits, and invalidates the host-visible allocation [dispatch and readback](../../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L172-L195).
- The host scans all entries. The first nonzero value becomes the expected subgroup size for that dispatch. Any different nonzero value fails the command-scope uniformity check [uniformity check](../../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L196-L220).
- A zero-only result fails. Otherwise, the host counts nonzero entries and compares the count with `ceil(localSize / size)` [count check](../../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L222-L234).

| Resource | Host setup | Device access | Host observation | Test role |
|----------|------------|---------------|------------------|-----------|
| Result storage buffer | Host-visible allocation, descriptor binding `0`, cleared before each dispatch | One elected invocation per subgroup writes one 32-bit size | Host invalidates and scans all entries | Carries subgroup-size and subgroup-count evidence. |
| Compute pipeline variants | One variant per power-of-two local X size | Execute the same specialized compute shader | No direct readback | Exercise the command-scope rule across workgroup sizes. |
| Primary command buffer | Reset-capable pool, recorded once per local-size iteration | Orders fill, barrier, dispatch, and visibility barrier | Submission completes before scanning | Separates each local-size run into its own dispatch command scope. |

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `uniform_subgroup_size` | Non-uniform `SubgroupSize` within one compute command scope, incorrect subgroup formation or built-in reporting, missing subgroup reports, or a broken clear/synchronization/readback path. |

### Cause Analysis

#### Command-scope subgroup reporting or result visibility failure

**Possible failure symptoms:** The host reports two different nonzero subgroup sizes in one dispatch, finds no nonzero report, or counts a number of nonzero entries different from `ceil(localSize / reportedSubgroupSize)` [validation](../../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L196-L234).

**Possible implementation causes:** A mismatched pair of nonzero values violates the compute `SubgroupSize` command-scope uniformity rule [interfaces.adoc](../../../../vulkan-docs/src/chapters/interfaces.adoc#L5222-L5231). A bad count can result from incorrect subgroup partitioning, incorrect `NumSubgroups`, `SubgroupId`, or `SubgroupSize` values, or shader compilation that fails to preserve the elected-writer and indexing logic. A zero-only or stale result can also come from a failure in the buffer clear, transfer-to-compute dependency, shader storage write, compute-to-host dependency, or host invalidation path exercised by the test source [execution path](../../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L160-L234).

## Case Pruning

### Requirement-based pruning

- The case runs only when `subgroupSizeControl` is supported. Otherwise `checkSupport` raises `NotSupportedError` [support check](../../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L262-L268).
- The source derives the local-size upper bound from `maxComputeWorkGroupSize[0]` and the result capacity from `minSubgroupSize` [device properties](../../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L77-L87).

### Design-based pruning

- Registration provides one fixed test case leaf. Local sizes are pipeline variants within the case rather than separate registered leaves [registration](../../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L301-L307).
- The local-size loop keeps powers of two from `1` through the device limit. Non-power-of-two local sizes are outside this test's design [variant loop](../../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L118-L158).
- Each variant dispatches one workgroup. Multi-workgroup dispatches are not generated by this test [dispatch](../../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L185).
- The pipeline does not request a particular subgroup size or set `VK_PIPELINE_SHADER_STAGE_CREATE_REQUIRE_FULL_SUBGROUPS_BIT_EXT`. Those behaviors belong outside this fixed uniformity check.

## Key Takeaways

- `uniform_subgroup_size` is the only registered test case leaf; its local-size sequence is an internal runtime matrix.
- The varying-size pipeline flag permits different subgroup-size choices, but compute `SubgroupSize` must stay uniform within each dispatch command scope.
- One elected invocation per subgroup turns subgroup formation into a countable result-buffer record.
- Clearing before every dispatch and waiting before host inspection isolate each command scope's reports.
- See `## Failure Meaning` for how size mismatches, report-count errors, and missing records map to implementation or visibility failures.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Category attachment | [vktSubgroupsTests.cpp#L70-L80](../../../modules/vulkan/subgroups/vktSubgroupsTests.cpp#L70-L80) | Adds the `multiple_dispatches` test family under the `subgroups` test category. |
| Test family and leaf registration | [createMultipleDispatchesUniformSubgroupSizeTests](../../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L301-L307) | Registers the exact hierarchy documented on this page. |
| Support gate | [MultipleDispatchesUniformSubgroupSize::checkSupport](../../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L262-L268) | Requires subgroup-size-control support. |
| Shader builder | [MultipleDispatchesUniformSubgroupSize::initPrograms](../../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L270-L291) | Emits the compute GLSL and selects SPIR-V 1.3. |
| Runtime setup | [MultipleDispatchesUniformSubgroupSizeInstance::iterate](../../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L61-L158) | Creates resources, descriptors, specialization data, and pipeline variants. |
| Dispatch and validation | [MultipleDispatchesUniformSubgroupSizeInstance::iterate](../../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L160-L243) | Clears, dispatches, synchronizes, reads back, and checks results. |
| Command scope specification | [shaders.adoc#L3104-L3127](../../../../vulkan-docs/src/chapters/shaders.adoc#L3104-L3127) | Defines the command scope created by one dispatch. |
| `SubgroupSize` specification | [interfaces.adoc#L5199-L5231](../../../../vulkan-docs/src/chapters/interfaces.adoc#L5199-L5231) | States the varying-size range and compute command-scope uniformity rule. |
| Varying-size stage flag | [pipelines.adoc#L1419-L1441](../../../../vulkan-docs/src/chapters/pipelines.adoc#L1419-L1441) | Defines the pipeline flag used by all variants. |
| Default mustpass entry | [subgroups.txt#L22567](../../../mustpass/main/vk-default/subgroups.txt#L22567) | Confirms the exact executable path. |
