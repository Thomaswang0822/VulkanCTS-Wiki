## Overview

**Core question:** Do partitioned subgroup reductions and scans match ordinary subgroup arithmetic over the same active invocations?

- This page covers the `subgroups.partitioned` test family implemented by [`vktSubgroupsPartitionedTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsPartitionedTests.cpp#L1).
- The family checks seven arithmetic and bitwise operators in reduce, inclusive scan, and exclusive scan forms across compute, graphics, framebuffer, ray tracing, mesh, and task execution paths.
- Each shader forms full, singleton, hash-derived, and control-flow-dependent partitions. It compares the partitioned result with an ordinary subgroup operation executed by the same active subset.
- The entire family is excluded from Vulkan SC builds by the dispatcher guard in [`vktSubgroupsTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsTests.cpp#L40-L45) and [`vktSubgroupsTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsTests.cpp#L68-L70).

## Background Knowledge

For the shared concepts subgroup identity, active invocations, ballots, masks, and collective result shapes, see [Background Knowledge](../../categories/subgroups.md#background-knowledge) of the `subgroups` page.

- A **partition** is a ballot mask selecting invocations within the subgroup. `subgroupPartitionNV` gives invocations with equal keys the same partition mask. Partitioning changes which invocations contribute to an operation; it does not create a new Vulkan execution scope.
- An ordinary subgroup operation inside divergent control flow uses the invocations active at that call. The test uses this property to produce an independent reference for each hash-selected partition.

## Registration Hierarchy

```text
subgroups.partitioned
├── graphics
├── compute
├── framebuffer
├── ray_tracing
└── mesh
```

These five direct children share the same generated semantic checks. Their pipeline construction, shader-stage coverage, result transport, and required-subgroup-size handling differ.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test family | `graphics`, `compute`, `framebuffer`, `ray_tracing`, `mesh` | Selects the execution harness, stage coverage, result transport, and whether stage or subgroup-size suffixes are generated. | [`createSubgroupsPartitionedTests`](../../../modules/vulkan/subgroups/vktSubgroupsPartitionedTests.cpp#L526-L704) |
| Scan form and operator | reduce, inclusive, or exclusive forms of add, mul, min, max, and, or, and xor | Chooses the `subgroupPartitioned*NV` instruction under test and the corresponding ordinary subgroup reference. Registered names use the ordinary `subgroup*` base, such as `subgroupadd`. | [`getOperator`, `getScanType`, and name builders`](../../../modules/vulkan/subgroups/vktSubgroupsPartitionedTests.cpp#L81-L176) |
| Data format | Scalar and vector 8-bit, 16-bit, 32-bit, and 64-bit integers; 16-bit, 32-bit, and 64-bit floats; Boolean formats; long-vector forms where available | Changes operand type, required GLSL type extension, exact versus tolerance comparison, and format support requirements. Ray tracing uses a smaller format set. | [`getAllFormats`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L1878-L1912), [`getAllRayTracingFormats`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L4190-L4221) |
| Required subgroup size | absent or `_requiredsubgroupsize` for compute, mesh, and task leaves | The required variant repeats the case for each supported power-of-two subgroup size from the device minimum through maximum. | [`test`](../../../modules/vulkan/subgroups/vktSubgroupsPartitionedTests.cpp#L432-L483) |
| Stage suffix | framebuffer: `_vertex`, `_tess_control`, `_tess_eval`, `_geometry`; mesh family: `_mesh`, `_task` | Chooses a specific framebuffer, mesh, or task stage. The `graphics` and `ray_tracing` families exercise all supported stages through shared harnesses. | [`createSubgroupsPartitionedTests`](../../../modules/vulkan/subgroups/vktSubgroupsPartitionedTests.cpp#L534-L647) |

The source applies two design filters before registration: floating-point formats omit bitwise operations, and Boolean formats omit non-bitwise operations. The default mustpass contains 12,087 executable leaves under `dEQP-VK.subgroups.partitioned`: 1,065 graphics, 2,130 compute, 4,260 framebuffer, 372 ray tracing, and 4,260 mesh leaves.

A leaf name records the ordinary operation name even though the subject is partitioned. For example, the registered leaf [`subgroupadd_float`](../../../mustpass/main/vk-default/subgroups.txt#L22582) maps as follows:

| Registered leaf component | Source selection | Invoked operation under test | Reference operation |
|---------------------------|------------------|------------------------------|---------------------|
| `subgroupadd_float` | `OPERATOR_ADD`, `SCAN_REDUCE`, scalar `float` | `subgroupPartitionedAddNV` | `subgroupAdd` |

## Behavior Parameters

The primary behavioral axis is the **test family**. Each value keeps the partition semantics but changes where the shader runs and how its 24-bit result reaches the host.

### `graphics`: all supported graphics pipeline stages

The graphics family asks whether the same partitioned operation works in every graphics stage that advertises subgroup support. A shared harness creates the pipeline, provides an SSBO input, writes per-stage results, and scans them for the full pass mask.

### `compute`: compute dispatch and subgroup-size sweeps

The compute family runs the generated body in a compute shader with harness-selected workgroup and local sizes. Its required-size leaves repeat the test for every supported power-of-two required subgroup size, so a failure can be tied to a particular subgroup width.

### `framebuffer`: stage result through an attachment

The framebuffer family targets vertex, tessellation control, tessellation evaluation, or geometry execution without relying on SSBO writes from the tested stage. The tested stage converts its 24-bit pass mask to a floating-point varying; a fixed fragment shader converts that value back to `uint` for the `R32_UINT` attachment, which the host copies to a buffer before checking it.

### `ray_tracing`: supported programmable ray tracing stages

The ray tracing family inserts the same body into the supported ray generation, any-hit, closest-hit, miss, intersection, and callable stages. A shared ray tracing harness returns each stage result for the same `0xFFFFFF` host predicate.

### `mesh`: mesh or task execution and subgroup-size sweeps

The mesh family places the body in either a mesh or task shader. Like compute, it has ordinary and required-subgroup-size leaves, but it also requires the mesh shader extension and the selected mesh or task feature.

## Shader Analysis

The compute reduction leaf below is representative because it shows the complete partition logic without extra pipeline stages. It also makes the registered-to-invoked mapping explicit: `subgroupadd_float` selects `subgroupPartitionedAddNV` as the operation under test and `subgroupAdd` as the reference.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.subgroups.partitioned.compute.subgroupadd_float
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `compute` | Uses the common compute shader shell and compute dispatch/readback harness. |
| Registered `subgroupadd` plus scalar `float` | Selects `OPERATOR_ADD`, `SCAN_REDUCE`, and scalar `float`; the generated subject call is `subgroupPartitionedAddNV`. |
| No `_requiredsubgroupsize` suffix | Uses harness-selected local sizes without setting a pipeline required subgroup size. |

#### Purpose

This shader checks that partitioned floating-point additions agree with ordinary subgroup additions executed over the same active subsets. It covers full, singleton, hash-derived, and divergent partitions and records each successful comparison in a 24-bit result mask.

#### Structural Design

| Phase | Partition or active set | Partitioned result | Independent reference | Success bits |
|-------|-------------------------|--------------------|-----------------------|--------------|
| Full subgroup | `subgroupBallot(true)` | `subgroupPartitionedAddNV` | `subgroupAdd` | `0x1` |
| Full ballot in divergence | Full ballot, but only even invocations execute the calls | `subgroupPartitionedAddNV` | `subgroupAdd` in the same branch | `0x2` |
| Singleton | Equal-key partition from unique invocation IDs | `subgroupPartitionedAddNV` | The current input value | `0x4` |
| Hash partitions | Equal-key partition for each generated hash | `subgroupPartitionedAddNV` | `subgroupAdd` inside the matching-key branch | `0x4 << N` |
| Hash partitions in outer divergence | Equal-key partition for odd invocations | `subgroupPartitionedAddNV` | `subgroupAdd` inside both outer and key branches | `0x20000 << N` |

#### Shader Code

```glsl
#version 450
#extension GL_NV_shader_subgroup_partitioned: enable
#extension GL_KHR_shader_subgroup_arithmetic: enable
#extension GL_KHR_shader_subgroup_ballot: enable

/// The local size is supplied through specialization constants 0, 1, and 2 by the common compute harness.
layout (local_size_x_id = 0, local_size_y_id = 1, local_size_z_id = 2) in;

/// Binding 0 stores one 24-bit pass mask per global invocation. The host requires every stored value to be 0xFFFFFF.
layout(set = 0, binding = 0, std430) buffer Buffer1
{
  uint result[];
};

/// Binding 1 contains nonzero float input values. It has at least the maximum supported subgroup size in elements.
layout(set = 0, binding = 1, std430) buffer Buffer2
{
  float data[];
};

void main (void)
{
  uvec3 globalSize = gl_NumWorkGroups * gl_WorkGroupSize;
  highp uint offset = globalSize.x * ((globalSize.y * gl_GlobalInvocationID.z) + gl_GlobalInvocationID.y) + gl_GlobalInvocationID.x;
  uint tempRes;

  /// Build the active mask and accumulate one success bit for each partition scenario.
  uvec4 mask = subgroupBallot(true);
  uint tempResult = 0;
  uint id = gl_SubgroupInvocationID;

  /// One partition containing every active invocation must match ordinary subgroupAdd.
  uvec4 allBallot = mask;
  float allResult = subgroupPartitionedAddNV(data[gl_SubgroupInvocationID], allBallot);
  float refResult = subgroupAdd(data[gl_SubgroupInvocationID]);
  if ((abs(allResult - refResult) < (gl_SubgroupSize==128 ? 0.000025:0.00001))) {
      tempResult |= 0x1;
  }

  /// Repeat the full partition comparison in divergent control flow. Inactive ballot bits must not contribute.
  if (0 == (gl_SubgroupInvocationID % 2)) {
    float allResult = subgroupPartitionedAddNV(data[gl_SubgroupInvocationID], allBallot);
    float refResult = subgroupAdd(data[gl_SubgroupInvocationID]);
    if ((abs(allResult - refResult) < (gl_SubgroupSize==128 ? 0.000025:0.00001))) {
        tempResult |= 0x2;
    }
  } else {
    tempResult |= 0x2;
  }

  /// A unique key per invocation creates singleton partitions, whose reduction result must equal that invocation's input.
  uvec4 selfBallot = subgroupPartitionNV(gl_SubgroupInvocationID);
  float selfResult = subgroupPartitionedAddNV(data[gl_SubgroupInvocationID], selfBallot);
  if ((abs(selfResult - data[gl_SubgroupInvocationID]) < (gl_SubgroupSize==128 ? 0.000025:0.00001))) {
      tempResult |= 0x4;
  }

  /// Hash-derived keys create many partitions. Divergent subgroupAdd calls provide the reference for each matching key.
  for (uint N = 1; N < 16; ++N) {
    float idhashFmt = float(((id%N)+(id%(N+1))-(id%2)+(id/2))%((N+1)/2));
    uvec4 partitionBallot = subgroupPartitionNV(idhashFmt) & mask;
    float partitionedResult = subgroupPartitionedAddNV(data[gl_SubgroupInvocationID], partitionBallot);
      for (uint i = 0; i < N; ++i) {
        float iFmt = float(i);
        if ((idhashFmt == iFmt)) {
          float subsetResult = subgroupAdd(data[gl_SubgroupInvocationID]);
          tempResult |= (abs(partitionedResult - subsetResult) < (gl_SubgroupSize==128 ? 0.000025:0.00001)) ? (0x4 << N) : 0;
        }
      }
  }

  /// Odd invocations repeat six hash partitions inside outer divergent control flow; even invocations pre-fill those bits.
  if (1 == (gl_SubgroupInvocationID % 2)) {
    for (uint N = 1; N < 7; ++N) {
      float idhashFmt = float(((id%N)+(id%(N+1))-(id%2)+(id/2))%((N+1)/2));
      uvec4 partitionBallot = subgroupPartitionNV(idhashFmt) & mask;
      float partitionedResult = subgroupPartitionedAddNV(data[gl_SubgroupInvocationID], partitionBallot);
        for (uint i = 0; i < N; ++i) {
          float iFmt = float(i);
          if ((idhashFmt == iFmt)) {
            float subsetResult = subgroupAdd(data[gl_SubgroupInvocationID]);
            tempResult |= (abs(partitionedResult - subsetResult) < (gl_SubgroupSize==128 ? 0.000025:0.00001)) ? (0x20000 << N) : 0;
          }
        }
    }
  } else {
    tempResult |= 0xFC0000;
  }
  tempRes = tempResult;
  result[offset] = tempRes;
}
```

#### Additional Info

- [`initPrograms`](../../../modules/vulkan/subgroups/vktSubgroupsPartitionedTests.cpp#L321-L333) selects SPIR-V 1.3 for this compute case and calls the common [`initStdPrograms`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L1406-L1434) builder.
- The generated float comparator uses a tolerance of `0.00001`, increased to `0.000025` when `gl_SubgroupSize` is 128, as defined by [`getCompare`](../../../modules/vulkan/subgroups/vktSubgroupsScanHelpers.cpp#L304-L349).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Scan form | Inclusive and exclusive leaves change both partitioned and reference operation names. Singleton exclusive scans compare with the operator identity rather than the input. | [`getScanType` and `getTestString`](../../../modules/vulkan/subgroups/vktSubgroupsPartitionedTests.cpp#L119-L151) |
| Operator | Replaces add with multiply, minimum, maximum, and, or, or xor; comparison and identity expressions follow the operator and type. | [`getOperator`](../../../modules/vulkan/subgroups/vktSubgroupsPartitionedTests.cpp#L81-L117), [`getIdentity`](../../../modules/vulkan/subgroups/vktSubgroupsScanHelpers.cpp#L218-L302) |
| Data format | Changes `data[]` and temporary types, adds extended-type GLSL extensions when needed, and selects exact or tolerance comparison code. | [`getExtHeader`](../../../modules/vulkan/subgroups/vktSubgroupsPartitionedTests.cpp#L178-L184), [`getCompare`](../../../modules/vulkan/subgroups/vktSubgroupsScanHelpers.cpp#L304-L349) |
| Execution family or stage | Wraps the same generated test body in graphics, framebuffer, ray tracing, mesh, or task stage shells and changes declarations and output transport. | [`initStdPrograms`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L1406-L1675) |
| Required subgroup size | Shader source retains specialization-controlled local size, while the pipeline requests each supported subgroup size. | [`test`](../../../modules/vulkan/subgroups/vktSubgroupsPartitionedTests.cpp#L432-L483) |

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
; Bound: 334
; Schema: 0
               OpCapability Shader
               OpCapability GroupNonUniform
               OpCapability GroupNonUniformArithmetic
               OpCapability GroupNonUniformBallot
               OpCapability GroupNonUniformPartitionedEXT
               OpExtension "SPV_NV_shader_subgroup_partitioned"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_NumWorkGroups %gl_GlobalInvocationID %gl_SubgroupInvocationID %gl_SubgroupSize
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpSourceExtension "GL_KHR_shader_subgroup_arithmetic"
               OpSourceExtension "GL_KHR_shader_subgroup_ballot"
               OpSourceExtension "GL_KHR_shader_subgroup_basic"
               OpSourceExtension "GL_NV_shader_subgroup_partitioned"
               OpName %main "main"
               OpName %globalSize "globalSize"
               OpName %gl_NumWorkGroups "gl_NumWorkGroups"
               OpName %offset "offset"
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
               OpName %mask "mask"
               OpName %tempResult "tempResult"
               OpName %id "id"
               OpName %gl_SubgroupInvocationID "gl_SubgroupInvocationID"
               OpName %allBallot "allBallot"
               OpName %allResult "allResult"
               OpName %Buffer2 "Buffer2"
               OpMemberName %Buffer2 0 "data"
               OpName %_ ""
               OpName %refResult "refResult"
               OpName %gl_SubgroupSize "gl_SubgroupSize"
               OpName %allResult_0 "allResult"
               OpName %refResult_0 "refResult"
               OpName %selfBallot "selfBallot"
               OpName %selfResult "selfResult"
               OpName %N "N"
               OpName %idhashFmt "idhashFmt"
               OpName %partitionBallot "partitionBallot"
               OpName %partitionedResult "partitionedResult"
               OpName %i "i"
               OpName %iFmt "iFmt"
               OpName %subsetResult "subsetResult"
               OpName %N_0 "N"
               OpName %idhashFmt_0 "idhashFmt"
               OpName %partitionBallot_0 "partitionBallot"
               OpName %partitionedResult_0 "partitionedResult"
               OpName %i_0 "i"
               OpName %iFmt_0 "iFmt"
               OpName %subsetResult_0 "subsetResult"
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
               OpDecorate %gl_SubgroupInvocationID RelaxedPrecision
               OpDecorate %gl_SubgroupInvocationID BuiltIn SubgroupLocalInvocationId
               OpDecorate %49 RelaxedPrecision
               OpDecorate %_runtimearr_float ArrayStride 4
               OpDecorate %Buffer2 Block
               OpMemberDecorate %Buffer2 0 Offset 0
               OpDecorate %_ Binding 1
               OpDecorate %_ DescriptorSet 0
               OpDecorate %61 RelaxedPrecision
               OpDecorate %68 RelaxedPrecision
               OpDecorate %gl_SubgroupSize RelaxedPrecision
               OpDecorate %gl_SubgroupSize BuiltIn SubgroupSize
               OpDecorate %77 RelaxedPrecision
               OpDecorate %88 RelaxedPrecision
               OpDecorate %89 RelaxedPrecision
               OpDecorate %94 RelaxedPrecision
               OpDecorate %100 RelaxedPrecision
               OpDecorate %108 RelaxedPrecision
               OpDecorate %120 RelaxedPrecision
               OpDecorate %121 RelaxedPrecision
               OpDecorate %123 RelaxedPrecision
               OpDecorate %129 RelaxedPrecision
               OpDecorate %134 RelaxedPrecision
               OpDecorate %178 RelaxedPrecision
               OpDecorate %201 RelaxedPrecision
               OpDecorate %209 RelaxedPrecision
               OpDecorate %230 RelaxedPrecision
               OpDecorate %231 RelaxedPrecision
               OpDecorate %270 RelaxedPrecision
               OpDecorate %293 RelaxedPrecision
               OpDecorate %301 RelaxedPrecision
               OpDecorate %_runtimearr_uint ArrayStride 4
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
%gl_SubgroupInvocationID = OpVariable %_ptr_Input_uint Input
      %float = OpTypeFloat 32
%_ptr_Function_float = OpTypePointer Function %float
%_runtimearr_float = OpTypeRuntimeArray %float
    %Buffer2 = OpTypeStruct %_runtimearr_float
%_ptr_StorageBuffer_Buffer2 = OpTypePointer StorageBuffer %Buffer2
          %_ = OpVariable %_ptr_StorageBuffer_Buffer2 StorageBuffer
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_StorageBuffer_float = OpTypePointer StorageBuffer %float
%gl_SubgroupSize = OpVariable %_ptr_Input_uint Input
   %uint_128 = OpConstant %uint 128
%float_2_49999994en05 = OpConstant %float 2.49999994e-05
%float_9_99999975en06 = OpConstant %float 9.99999975e-06
     %uint_4 = OpConstant %uint 4
    %uint_16 = OpConstant %uint 16
%_ptr_Function_int = OpTypePointer Function %int
      %int_4 = OpConstant %int 4
      %int_1 = OpConstant %int 1
     %uint_7 = OpConstant %uint 7
 %int_131072 = OpConstant %int 131072
%uint_16515072 = OpConstant %uint 16515072
%_runtimearr_uint = OpTypeRuntimeArray %uint
    %Buffer1 = OpTypeStruct %_runtimearr_uint
%_ptr_StorageBuffer_Buffer1 = OpTypePointer StorageBuffer %Buffer1
        %__0 = OpVariable %_ptr_StorageBuffer_Buffer1 StorageBuffer
%_ptr_StorageBuffer_uint = OpTypePointer StorageBuffer %uint
       %main = OpFunction %void None %3
          %5 = OpLabel
 %globalSize = OpVariable %_ptr_Function_v3uint Function
     %offset = OpVariable %_ptr_Function_uint Function
       %mask = OpVariable %_ptr_Function_v4uint Function
 %tempResult = OpVariable %_ptr_Function_uint Function
         %id = OpVariable %_ptr_Function_uint Function
  %allBallot = OpVariable %_ptr_Function_v4uint Function
  %allResult = OpVariable %_ptr_Function_float Function
  %refResult = OpVariable %_ptr_Function_float Function
%allResult_0 = OpVariable %_ptr_Function_float Function
%refResult_0 = OpVariable %_ptr_Function_float Function
 %selfBallot = OpVariable %_ptr_Function_v4uint Function
 %selfResult = OpVariable %_ptr_Function_float Function
          %N = OpVariable %_ptr_Function_uint Function
  %idhashFmt = OpVariable %_ptr_Function_float Function
%partitionBallot = OpVariable %_ptr_Function_v4uint Function
%partitionedResult = OpVariable %_ptr_Function_float Function
          %i = OpVariable %_ptr_Function_uint Function
       %iFmt = OpVariable %_ptr_Function_float Function
%subsetResult = OpVariable %_ptr_Function_float Function
        %214 = OpVariable %_ptr_Function_int Function
        %N_0 = OpVariable %_ptr_Function_uint Function
%idhashFmt_0 = OpVariable %_ptr_Function_float Function
%partitionBallot_0 = OpVariable %_ptr_Function_v4uint Function
%partitionedResult_0 = OpVariable %_ptr_Function_float Function
        %i_0 = OpVariable %_ptr_Function_uint Function
     %iFmt_0 = OpVariable %_ptr_Function_float Function
%subsetResult_0 = OpVariable %_ptr_Function_float Function
        %305 = OpVariable %_ptr_Function_int Function
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
         %45 = OpGroupNonUniformBallot %v4uint %uint_3 %true
               OpStore %mask %45
               OpStore %tempResult %uint_0
         %49 = OpLoad %uint %gl_SubgroupInvocationID
               OpStore %id %49
         %51 = OpLoad %v4uint %mask
               OpStore %allBallot %51
         %61 = OpLoad %uint %gl_SubgroupInvocationID
         %63 = OpAccessChain %_ptr_StorageBuffer_float %_ %int_0 %61
         %64 = OpLoad %float %63
         %65 = OpLoad %v4uint %allBallot
         %66 = OpGroupNonUniformFAdd %float %uint_3 PartitionedReduceEXT %64 %65
               OpStore %allResult %66
         %68 = OpLoad %uint %gl_SubgroupInvocationID
         %69 = OpAccessChain %_ptr_StorageBuffer_float %_ %int_0 %68
         %70 = OpLoad %float %69
         %71 = OpGroupNonUniformFAdd %float %uint_3 Reduce %70
               OpStore %refResult %71
         %72 = OpLoad %float %allResult
         %73 = OpLoad %float %refResult
         %74 = OpFSub %float %72 %73
         %75 = OpExtInst %float %1 FAbs %74
         %77 = OpLoad %uint %gl_SubgroupSize
         %79 = OpIEqual %bool %77 %uint_128
         %82 = OpSelect %float %79 %float_2_49999994en05 %float_9_99999975en06
         %83 = OpFOrdLessThan %bool %75 %82
               OpSelectionMerge %85 None
               OpBranchConditional %83 %84 %85
         %84 = OpLabel
         %86 = OpLoad %uint %tempResult
         %87 = OpBitwiseOr %uint %86 %uint_1
               OpStore %tempResult %87
               OpBranch %85
         %85 = OpLabel
         %88 = OpLoad %uint %gl_SubgroupInvocationID
         %89 = OpUMod %uint %88 %uint_2
         %90 = OpIEqual %bool %uint_0 %89
               OpSelectionMerge %92 None
               OpBranchConditional %90 %91 %116
         %91 = OpLabel
         %94 = OpLoad %uint %gl_SubgroupInvocationID
         %95 = OpAccessChain %_ptr_StorageBuffer_float %_ %int_0 %94
         %96 = OpLoad %float %95
         %97 = OpLoad %v4uint %allBallot
         %98 = OpGroupNonUniformFAdd %float %uint_3 PartitionedReduceEXT %96 %97
               OpStore %allResult_0 %98
        %100 = OpLoad %uint %gl_SubgroupInvocationID
        %101 = OpAccessChain %_ptr_StorageBuffer_float %_ %int_0 %100
        %102 = OpLoad %float %101
        %103 = OpGroupNonUniformFAdd %float %uint_3 Reduce %102
               OpStore %refResult_0 %103
        %104 = OpLoad %float %allResult_0
        %105 = OpLoad %float %refResult_0
        %106 = OpFSub %float %104 %105
        %107 = OpExtInst %float %1 FAbs %106
        %108 = OpLoad %uint %gl_SubgroupSize
        %109 = OpIEqual %bool %108 %uint_128
        %110 = OpSelect %float %109 %float_2_49999994en05 %float_9_99999975en06
        %111 = OpFOrdLessThan %bool %107 %110
               OpSelectionMerge %113 None
               OpBranchConditional %111 %112 %113
        %112 = OpLabel
        %114 = OpLoad %uint %tempResult
        %115 = OpBitwiseOr %uint %114 %uint_2
               OpStore %tempResult %115
               OpBranch %113
        %113 = OpLabel
               OpBranch %92
        %116 = OpLabel
        %117 = OpLoad %uint %tempResult
        %118 = OpBitwiseOr %uint %117 %uint_2
               OpStore %tempResult %118
               OpBranch %92
         %92 = OpLabel
        %120 = OpLoad %uint %gl_SubgroupInvocationID
        %121 = OpGroupNonUniformPartitionEXT %v4uint %120
               OpStore %selfBallot %121
        %123 = OpLoad %uint %gl_SubgroupInvocationID
        %124 = OpAccessChain %_ptr_StorageBuffer_float %_ %int_0 %123
        %125 = OpLoad %float %124
        %126 = OpLoad %v4uint %selfBallot
        %127 = OpGroupNonUniformFAdd %float %uint_3 PartitionedReduceEXT %125 %126
               OpStore %selfResult %127
        %128 = OpLoad %float %selfResult
        %129 = OpLoad %uint %gl_SubgroupInvocationID
        %130 = OpAccessChain %_ptr_StorageBuffer_float %_ %int_0 %129
        %131 = OpLoad %float %130
        %132 = OpFSub %float %128 %131
        %133 = OpExtInst %float %1 FAbs %132
        %134 = OpLoad %uint %gl_SubgroupSize
        %135 = OpIEqual %bool %134 %uint_128
        %136 = OpSelect %float %135 %float_2_49999994en05 %float_9_99999975en06
        %137 = OpFOrdLessThan %bool %133 %136
               OpSelectionMerge %139 None
               OpBranchConditional %137 %138 %139
        %138 = OpLabel
        %141 = OpLoad %uint %tempResult
        %142 = OpBitwiseOr %uint %141 %uint_4
               OpStore %tempResult %142
               OpBranch %139
        %139 = OpLabel
               OpStore %N %uint_1
               OpBranch %144
        %144 = OpLabel
               OpLoopMerge %146 %147 None
               OpBranch %148
        %148 = OpLabel
        %149 = OpLoad %uint %N
        %151 = OpULessThan %bool %149 %uint_16
               OpBranchConditional %151 %145 %146
        %145 = OpLabel
        %153 = OpLoad %uint %id
        %154 = OpLoad %uint %N
        %155 = OpUMod %uint %153 %154
        %156 = OpLoad %uint %id
        %157 = OpLoad %uint %N
        %158 = OpIAdd %uint %157 %uint_1
        %159 = OpUMod %uint %156 %158
        %160 = OpIAdd %uint %155 %159
        %161 = OpLoad %uint %id
        %162 = OpUMod %uint %161 %uint_2
        %163 = OpISub %uint %160 %162
        %164 = OpLoad %uint %id
        %165 = OpUDiv %uint %164 %uint_2
        %166 = OpIAdd %uint %163 %165
        %167 = OpLoad %uint %N
        %168 = OpIAdd %uint %167 %uint_1
        %169 = OpUDiv %uint %168 %uint_2
        %170 = OpUMod %uint %166 %169
        %171 = OpConvertUToF %float %170
               OpStore %idhashFmt %171
        %173 = OpLoad %float %idhashFmt
        %174 = OpGroupNonUniformPartitionEXT %v4uint %173
        %175 = OpLoad %v4uint %mask
        %176 = OpBitwiseAnd %v4uint %174 %175
               OpStore %partitionBallot %176
        %178 = OpLoad %uint %gl_SubgroupInvocationID
        %179 = OpAccessChain %_ptr_StorageBuffer_float %_ %int_0 %178
        %180 = OpLoad %float %179
        %181 = OpLoad %v4uint %partitionBallot
        %182 = OpGroupNonUniformFAdd %float %uint_3 PartitionedReduceEXT %180 %181
               OpStore %partitionedResult %182
               OpStore %i %uint_0
               OpBranch %184
        %184 = OpLabel
               OpLoopMerge %186 %187 None
               OpBranch %188
        %188 = OpLabel
        %189 = OpLoad %uint %i
        %190 = OpLoad %uint %N
        %191 = OpULessThan %bool %189 %190
               OpBranchConditional %191 %185 %186
        %185 = OpLabel
        %193 = OpLoad %uint %i
        %194 = OpConvertUToF %float %193
               OpStore %iFmt %194
        %195 = OpLoad %float %idhashFmt
        %196 = OpLoad %float %iFmt
        %197 = OpFOrdEqual %bool %195 %196
               OpSelectionMerge %199 None
               OpBranchConditional %197 %198 %199
        %198 = OpLabel
        %201 = OpLoad %uint %gl_SubgroupInvocationID
        %202 = OpAccessChain %_ptr_StorageBuffer_float %_ %int_0 %201
        %203 = OpLoad %float %202
        %204 = OpGroupNonUniformFAdd %float %uint_3 Reduce %203
               OpStore %subsetResult %204
        %205 = OpLoad %float %partitionedResult
        %206 = OpLoad %float %subsetResult
        %207 = OpFSub %float %205 %206
        %208 = OpExtInst %float %1 FAbs %207
        %209 = OpLoad %uint %gl_SubgroupSize
        %210 = OpIEqual %bool %209 %uint_128
        %211 = OpSelect %float %210 %float_2_49999994en05 %float_9_99999975en06
        %212 = OpFOrdLessThan %bool %208 %211
               OpSelectionMerge %216 None
               OpBranchConditional %212 %215 %220
        %215 = OpLabel
        %218 = OpLoad %uint %N
        %219 = OpShiftLeftLogical %int %int_4 %218
               OpStore %214 %219
               OpBranch %216
        %220 = OpLabel
               OpStore %214 %int_0
               OpBranch %216
        %216 = OpLabel
        %221 = OpLoad %int %214
        %222 = OpBitcast %uint %221
        %223 = OpLoad %uint %tempResult
        %224 = OpBitwiseOr %uint %223 %222
               OpStore %tempResult %224
               OpBranch %199
        %199 = OpLabel
               OpBranch %187
        %187 = OpLabel
        %225 = OpLoad %uint %i
        %227 = OpIAdd %uint %225 %int_1
               OpStore %i %227
               OpBranch %184
        %186 = OpLabel
               OpBranch %147
        %147 = OpLabel
        %228 = OpLoad %uint %N
        %229 = OpIAdd %uint %228 %int_1
               OpStore %N %229
               OpBranch %144
        %146 = OpLabel
        %230 = OpLoad %uint %gl_SubgroupInvocationID
        %231 = OpUMod %uint %230 %uint_2
        %232 = OpIEqual %bool %uint_1 %231
               OpSelectionMerge %234 None
               OpBranchConditional %232 %233 %320
        %233 = OpLabel
               OpStore %N_0 %uint_1
               OpBranch %236
        %236 = OpLabel
               OpLoopMerge %238 %239 None
               OpBranch %240
        %240 = OpLabel
        %241 = OpLoad %uint %N_0
        %243 = OpULessThan %bool %241 %uint_7
               OpBranchConditional %243 %237 %238
        %237 = OpLabel
        %245 = OpLoad %uint %id
        %246 = OpLoad %uint %N_0
        %247 = OpUMod %uint %245 %246
        %248 = OpLoad %uint %id
        %249 = OpLoad %uint %N_0
        %250 = OpIAdd %uint %249 %uint_1
        %251 = OpUMod %uint %248 %250
        %252 = OpIAdd %uint %247 %251
        %253 = OpLoad %uint %id
        %254 = OpUMod %uint %253 %uint_2
        %255 = OpISub %uint %252 %254
        %256 = OpLoad %uint %id
        %257 = OpUDiv %uint %256 %uint_2
        %258 = OpIAdd %uint %255 %257
        %259 = OpLoad %uint %N_0
        %260 = OpIAdd %uint %259 %uint_1
        %261 = OpUDiv %uint %260 %uint_2
        %262 = OpUMod %uint %258 %261
        %263 = OpConvertUToF %float %262
               OpStore %idhashFmt_0 %263
        %265 = OpLoad %float %idhashFmt_0
        %266 = OpGroupNonUniformPartitionEXT %v4uint %265
        %267 = OpLoad %v4uint %mask
        %268 = OpBitwiseAnd %v4uint %266 %267
               OpStore %partitionBallot_0 %268
        %270 = OpLoad %uint %gl_SubgroupInvocationID
        %271 = OpAccessChain %_ptr_StorageBuffer_float %_ %int_0 %270
        %272 = OpLoad %float %271
        %273 = OpLoad %v4uint %partitionBallot_0
        %274 = OpGroupNonUniformFAdd %float %uint_3 PartitionedReduceEXT %272 %273
               OpStore %partitionedResult_0 %274
               OpStore %i_0 %uint_0
               OpBranch %276
        %276 = OpLabel
               OpLoopMerge %278 %279 None
               OpBranch %280
        %280 = OpLabel
        %281 = OpLoad %uint %i_0
        %282 = OpLoad %uint %N_0
        %283 = OpULessThan %bool %281 %282
               OpBranchConditional %283 %277 %278
        %277 = OpLabel
        %285 = OpLoad %uint %i_0
        %286 = OpConvertUToF %float %285
               OpStore %iFmt_0 %286
        %287 = OpLoad %float %idhashFmt_0
        %288 = OpLoad %float %iFmt_0
        %289 = OpFOrdEqual %bool %287 %288
               OpSelectionMerge %291 None
               OpBranchConditional %289 %290 %291
        %290 = OpLabel
        %293 = OpLoad %uint %gl_SubgroupInvocationID
        %294 = OpAccessChain %_ptr_StorageBuffer_float %_ %int_0 %293
        %295 = OpLoad %float %294
        %296 = OpGroupNonUniformFAdd %float %uint_3 Reduce %295
               OpStore %subsetResult_0 %296
        %297 = OpLoad %float %partitionedResult_0
        %298 = OpLoad %float %subsetResult_0
        %299 = OpFSub %float %297 %298
        %300 = OpExtInst %float %1 FAbs %299
        %301 = OpLoad %uint %gl_SubgroupSize
        %302 = OpIEqual %bool %301 %uint_128
        %303 = OpSelect %float %302 %float_2_49999994en05 %float_9_99999975en06
        %304 = OpFOrdLessThan %bool %300 %303
               OpSelectionMerge %307 None
               OpBranchConditional %304 %306 %311
        %306 = OpLabel
        %309 = OpLoad %uint %N_0
        %310 = OpShiftLeftLogical %int %int_131072 %309
               OpStore %305 %310
               OpBranch %307
        %311 = OpLabel
               OpStore %305 %int_0
               OpBranch %307
        %307 = OpLabel
        %312 = OpLoad %int %305
        %313 = OpBitcast %uint %312
        %314 = OpLoad %uint %tempResult
        %315 = OpBitwiseOr %uint %314 %313
               OpStore %tempResult %315
               OpBranch %291
        %291 = OpLabel
               OpBranch %279
        %279 = OpLabel
        %316 = OpLoad %uint %i_0
        %317 = OpIAdd %uint %316 %int_1
               OpStore %i_0 %317
               OpBranch %276
        %278 = OpLabel
               OpBranch %239
        %239 = OpLabel
        %318 = OpLoad %uint %N_0
        %319 = OpIAdd %uint %318 %int_1
               OpStore %N_0 %319
               OpBranch %236
        %238 = OpLabel
               OpBranch %234
        %320 = OpLabel
        %322 = OpLoad %uint %tempResult
        %323 = OpBitwiseOr %uint %322 %uint_16515072
               OpStore %tempResult %323
               OpBranch %234
        %234 = OpLabel
        %325 = OpLoad %uint %tempResult
               OpStore %tempRes %325
        %330 = OpLoad %uint %offset
        %331 = OpLoad %uint %tempRes
        %333 = OpAccessChain %_ptr_StorageBuffer_uint %__0 %int_0 %330
               OpStore %333 %331
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The support check requires Vulkan subgroup support, `VK_SUBGROUP_FEATURE_PARTITIONED_BIT_NV`, the selected subgroup data format, and subgroup support in the selected shader stage. It also checks 8-bit or 16-bit uniform-buffer storage when a framebuffer format needs it.
- Compute-like and ordinary pipeline paths initialize `data[]` with nonzero values and allocate at least the maximum supported subgroup size in elements. The generated shader indexes this input by `gl_SubgroupInvocationID`.
- The shader assigns one bit to each semantic check. Full-subgroup, divergent full-subgroup, singleton, 15 hash-partition, and 6 divergent hash-partition checks cover bits 0 through 23. An invocation that passes all checks writes `0xFFFFFF`.
- Compute and mesh shaders flatten `gl_GlobalInvocationID` into `result[]`. Graphics and ray tracing harnesses collect equivalent per-stage output. In framebuffer cases, the tested stage converts the mask to a floating-point varying, a fixed fragment shader converts it back to `uint` for the `R32_UINT` attachment, and the host copies that image into a host-readable buffer.
- The shared callbacks scan every produced `uint` and require exact equality with `0xFFFFFF`. They do not decode a missing bit, so diagnosis requires the observed value or a shader-level rerun.
- Required-subgroup-size cases execute once for every supported power-of-two size from `minSubgroupSize` to `maxSubgroupSize`. The test logs the first failed size and returns.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `graphics` | Partitioned subgroup arithmetic or result storage is incorrect in one or more enabled graphics pipeline stages. |
| `compute` | Partitioned subgroup arithmetic is incorrect in compute execution, potentially only for a required subgroup size or harness-selected local size. |
| `framebuffer` | Partitioned subgroup arithmetic or stage-to-framebuffer result transport is incorrect in a vertex, tessellation, or geometry framebuffer path. |
| `ray_tracing` | Partitioned subgroup arithmetic is incorrect in one or more supported programmable ray tracing stages, or the stage result is not returned correctly. |
| `mesh` | Partitioned subgroup arithmetic is incorrect in mesh or task execution, potentially only for a required subgroup size. |

### Cause Analysis

#### Partition construction or partitioned arithmetic mismatch

**Possible failure symptoms:** one or more shader result words differ from `0xFFFFFF`. The missing bit can correspond to the full subgroup, inactive-bit handling, a singleton partition, a hash-derived partition, or the outer divergent path. Operation and format variants can narrow the mismatch to a reduction or scan form and data type.

**Possible implementation causes:** lowering of `subgroupPartitionNV` may produce an incorrect equal-key mask, inactive ballot bits may contribute when they must not, or `subgroupPartitioned*NV` may apply the operation to the wrong invocations or use incorrect inclusive, exclusive, or identity behavior. The Vulkan extension advertises these operations through the partitioned feature bit, while the GLSL and SPIR-V extensions define their shader representation.

#### Stage execution or result transport mismatch

**Possible failure symptoms:** only `graphics`, `framebuffer`, `ray_tracing`, or `mesh` leaves fail while the same operation and format pass in compute. A framebuffer failure can appear as an incorrect copied `R32_UINT` value even when no SSBO is written by the tested stage.

**Possible implementation causes:** stage-specific compilation or execution may mishandle subgroup partitioned instructions, or the tested stage's result may not reach the harness output correctly. For framebuffer cases, conversion of the 24-bit integer mask to a floating-point varying and back, attachment output, synchronization, image copy, or readback can corrupt the pass mask. For other families, stage-specific SSBO writes or harness collection can expose the same symptom.

#### Required subgroup size dependence

**Possible failure symptoms:** an ordinary compute, mesh, or task leaf passes, but its `_requiredsubgroupsize` counterpart fails and logs one requested size.

**Possible implementation causes:** pipeline required-subgroup-size control may not produce the requested subgroup width, or partition masks and scans may be incorrect only at a particular supported width. A float mismatch can also indicate that the operation result falls outside the source-defined tolerance for that width.

## Case Pruning

### Requirement-based pruning

- Vulkan subgroup support and `VK_SUBGROUP_FEATURE_PARTITIONED_BIT_NV` are mandatory.
- The selected format must be supported for subgroup operations. Extended types require the corresponding Vulkan data type and storage features.
- The selected shader stage must advertise subgroup support. Compute subgroup support is required; unsupported optional graphics or ray tracing stages are not exercised by their shared harnesses.
- Required-subgroup-size leaves require `VK_EXT_subgroup_size_control`, `subgroupSizeControl`, `computeFullSubgroups`, and support for required subgroup size in the selected stage.
- Ray tracing leaves require `VK_KHR_ray_tracing_pipeline`. Mesh and task leaves require `VK_EXT_mesh_shader`; task leaves also require the task shader feature.
- Framebuffer 8-bit and 16-bit input formats require the corresponding uniform-buffer storage support.

### Design-based pruning

- Floating-point formats are not registered for bitwise and, or, or xor operations.
- Boolean formats are registered only for bitwise operations.
- Ray tracing uses a smaller representative format list than the other families.
- Required subgroup size variants are generated for compute, mesh, and task paths, not for graphics, framebuffer, or ray tracing paths.
- Vulkan SC omits the entire `partitioned` test family at compile-time registration.
- The current [`test-issues.txt`](../../../mustpass/main/src/test-issues.txt#L1) has no partitioned-specific exclusion.

## Key Takeaways

- Registered leaf names such as `subgroupadd_float` identify the operator and data format but omit `PartitionedNV`. The source maps that leaf to `subgroupPartitionedAddNV`; ordinary `subgroupAdd` is the reference.
- One generated shader body checks full, singleton, hash-derived, and divergent partitions. The final `0xFFFFFF` mask means all 24 checks passed for one invocation.
- The five direct test families vary execution and result transport, not the underlying partition algorithm.
- Compute and mesh required-size leaves can isolate width-dependent behavior across every supported power-of-two subgroup size.
- See `## Failure Meaning` for how a failing family and leaf suffix narrow the failure mechanism.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Dispatcher registration guard | [`vktSubgroupsTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsTests.cpp#L40-L45), [`vktSubgroupsTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsTests.cpp#L68-L70) | Registers the family only outside Vulkan SC. |
| Operation and scan mapping | [`getOperator`, `getScanType`, and name builders`](../../../modules/vulkan/subgroups/vktSubgroupsPartitionedTests.cpp#L81-L176) | Maps each registered leaf prefix to the ordinary reference and partitioned GLSL function names. |
| Extension header and generated checks | [`getExtHeader` and `getTestString`](../../../modules/vulkan/subgroups/vktSubgroupsPartitionedTests.cpp#L178-L308) | Emits extensions, partition scenarios, comparisons, and pass-mask bits. |
| Shader program builders | [`initFrameBufferPrograms` and `initPrograms`](../../../modules/vulkan/subgroups/vktSubgroupsPartitionedTests.cpp#L310-L333) | Selects the common stage shell and SPIR-V target. |
| Feature and stage requirements | [`supportedCheck`](../../../modules/vulkan/subgroups/vktSubgroupsPartitionedTests.cpp#L335-L401) | Enforces all runtime capabilities before execution. |
| Family-specific runtime routing | [`noSSBOtest` and `test`](../../../modules/vulkan/subgroups/vktSubgroupsPartitionedTests.cpp#L403-L519) | Routes cases to framebuffer, compute, graphics, ray tracing, mesh, or task harnesses and subgroup-size sweeps. |
| Registration matrix | [`createSubgroupsPartitionedTests`](../../../modules/vulkan/subgroups/vktSubgroupsPartitionedTests.cpp#L526-L704) | Creates the direct children and executable leaves. |
| Common shader shells | [`initStdFrameBufferPrograms`, `getBufferDeclarations`, and `initStdPrograms`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L1275-L1675) | Builds framebuffer conversion/varying paths plus stage declarations, resources, offsets, and result writes around the generated body. |
| Host result checks | [`check` and `checkComputeOrMesh`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L2640-L2663) | Requires every result word to equal `0xFFFFFF`. |
| Scan operation helpers | [`vktSubgroupsScanHelpers.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsScanHelpers.cpp#L39-L349) | Generates operation names, identities, operation expressions, and comparisons. |
| Vulkan subgroup semantics | [`shaders.adoc`](../../../../vulkan-docs/src/chapters/shaders.adoc#L3220-L3247), [`shaders.adoc`](../../../../vulkan-docs/src/chapters/shaders.adoc#L3447-L3511) | Defines subgroups, group operations, reductions, and scan forms. |
| NV partitioned extension | [`VK_NV_shader_subgroup_partitioned.adoc`](../../../../vulkan-docs/src/appendices/VK_NV_shader_subgroup_partitioned.adoc#L17-L36) | Connects the Vulkan feature bit with the GLSL and SPIR-V partitioned extensions. |
| Default mustpass evidence | [`subgroups.txt`](../../../mustpass/main/vk-default/subgroups.txt#L22568-L22624) | Confirms representative compute leaf names, including `subgroupadd_float`. |
