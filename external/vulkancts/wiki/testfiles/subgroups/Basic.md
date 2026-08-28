## Overview

**Core question:** Do subgroup election and barrier operations produce the expected result for every supported execution path and subgroup size?

- This page covers the `subgroups.basic` test family implemented by [`vktSubgroupsBasicTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L1).
- The family exercises election, control barriers, and memory barriers across compute, graphics, framebuffer, ray-tracing, mesh, and task shaders.
- The shaders record either the elected invocation or a value that should be visible after the selected barrier. Host callbacks then check every output element or rendered value.
- Compute and mesh cases also have `_requiredsubgroupsize` variants that repeat the same correctness check at each supported power-of-two subgroup size.

## Background Knowledge

For the shared concepts subgroup identity, active invocations, collective result shapes, and subgroup-size control, see [Background Knowledge](../../categories/subgroups.md#background-knowledge) of the `subgroups` page.

- A control barrier synchronizes subgroup execution and carries memory semantics. A memory barrier establishes the selected memory dependency; the GLSL variants in this family cover general memory, buffer memory, workgroup `shared` memory, and image memory.

## Registration Hierarchy

```text
subgroups.basic
├── graphics
├── compute
├── framebuffer
├── ray_tracing
└── mesh
```

`ray_tracing` and `mesh` are present only in non-VulkanSC builds. The deeper executable leaves combine operation, stage where applicable, and optional required-subgroup-size suffixes.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Execution path | `graphics`, `compute`, `framebuffer`, `ray_tracing`, `mesh` | Selects pipeline type, shader-stage coverage, result transport, and runtime helper. | [`createSubgroupsBasicTests`](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L2196-L2314) |
| Operation test case leaf stem | `subgroupelect`, `subgroupbarrier`, `subgroupmemorybarrier`, `subgroupmemorybarrierbuffer`, `subgroupmemorybarriershared`, `subgroupmemorybarrierimage` | Selects the election rule or the memory/resource class whose subgroup barrier behavior is checked. | [`OpType` and `getOpTypeName`](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L43-L52) |
| Framebuffer stage suffix | `fragment`, `vertex`, `tess_eval`, `tess_control`, `geometry` | Runs the tested operation in one graphics stage and returns values through an attachment rather than an SSBO. | [`fbStages`](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L2204-L2210) |
| Mesh stage suffix | `mesh`, `task` | Runs the same generated logic in a mesh or task shader. | [`meshStages`](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L2211-L2216) |
| Required subgroup size | no suffix, `_requiredsubgroupsize` | Uses the implementation-selected subgroup size or sweeps every supported required size. | [compute registration](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L2219-L2237) and [mesh registration](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L2239-L2257) |
| Runtime required size | powers of two from `minSubgroupSize` through `maxSubgroupSize` | Repeats one registered required-size case with each legal advertised size. | [`test`](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L1949-L1973) |

The operation set is not uniform across all paths. `subgroupmemorybarriershared` is limited to compute and mesh. Framebuffer election omits the fragment-stage leaf.

## Behavior Parameters

The primary behavioral axis is the **operation test case leaf stem**. It changes the subgroup property or memory class under test; execution path, shader stage, and required size change where and under what configuration that property is exercised.

### `subgroupelect`: one elected invocation

Each subgroup must select exactly one active invocation. Compute and mesh shaders count elected invocations with a shared-memory ballot and write `1` for every invocation. Other paths write `42` for elected invocations and `13` for the rest, with an atomic counter recording how many subgroups executed.

### `subgroupbarrier`: execution and memory synchronization

The elected invocation writes a reference value to a subgroup-specific slot, then all active invocations execute `subgroupBarrier()` before reading it. Every checked invocation must observe the reference value.

### `subgroupmemorybarrier`: general memory dependency

This case keeps the elected-write/peer-read pattern but uses `subgroupMemoryBarrier()`. It checks the general subgroup-scoped memory dependency through the resource path selected by the execution helper.

### `subgroupmemorybarrierbuffer`: buffer memory dependency

This case uses `subgroupMemoryBarrierBuffer()` between a storage-buffer write by the elected invocation and storage-buffer reads by its peers. The output must still equal the host-provided reference.

### `subgroupmemorybarriershared`: workgroup shared-memory dependency

The elected invocation writes the reference into shader-local `shared` storage indexed by subgroup. After `subgroupMemoryBarrierShared()`, each active invocation reads that entry. This leaf is registered only for compute, mesh, and task paths.

### `subgroupmemorybarrierimage`: image memory dependency

The elected invocation writes the reference value to an `r32ui` storage image. After `subgroupMemoryBarrierImage()`, subgroup peers load the same texel and report it for host checking.

## Shader Analysis

The compute control-barrier case is representative because it exposes the family's common elected-write, barrier, peer-read, and host-scan pattern. Nearby operation leaves replace the barrier or resource access while retaining that structure.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.subgroups.basic.compute.subgroupbarrier_requiredsubgroupsize
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `compute` | Uses the compute template, SSBO result path, and compute dispatch helper. |
| `subgroupbarrier` | Places `subgroupBarrier()` between the elected write and all subgroup reads. |
| `_requiredsubgroupsize` | Runs the shader at every supported power-of-two required subgroup size. |

#### Purpose

This shader checks that one elected invocation can write a subgroup-specific buffer slot and that every active invocation observes the value after a subgroup control barrier.

#### Structural Design

| Phase | Per-subgroup behavior | Observable result |
|-------|-----------------------|-------------------|
| Address | Derive one slot from workgroup coordinates and `gl_SubgroupID`. | Peers in the same subgroup use the same `tempBuffer` element. |
| Produce | The elected invocation stores the host-provided `value`. | Exactly one invocation performs the write. |
| Synchronize | Every active invocation executes `subgroupBarrier()`. | Execution reaches the read after the barrier. |
| Observe | Every invocation loads the common slot. | `result[offset]` should equal `value`. |

#### Shader Code

```glsl
#version 450
#extension GL_KHR_shader_subgroup_basic: enable
layout (local_size_x_id = 0, local_size_y_id = 1, local_size_z_id = 2) in;
/// Binding 0 stores one checked uint for each global invocation.
layout (set = 0, binding = 0, std430) buffer Buffer1
{
  uint result[];
};
/// Binding 1 provides one uint slot per workgroup/subgroup pair; the elected invocation writes it.
layout (set = 0, binding = 1, std430) buffer Buffer2
{
  uint tempBuffer[];
};
/// Binding 2 contains the nonzero reference value selected by the host.
layout (set = 0, binding = 2, std430) buffer Buffer3
{
  uint value;
};
/// Binding 3 and tempShared are declared by the common non-election template but are unused by subgroupBarrier.
layout (set = 0, binding = 3, r32ui) uniform uimage2D tempImage;
shared uint tempShared[gl_WorkGroupSize.x * gl_WorkGroupSize.y * gl_WorkGroupSize.z];

void main (void)
{
  /// Flatten the global invocation coordinate so every invocation has one result element.
  uvec3 globalSize = gl_NumWorkGroups * gl_WorkGroupSize;
  highp uint offset = globalSize.x * ((globalSize.y * gl_GlobalInvocationID.z) + gl_GlobalInvocationID.y) + gl_GlobalInvocationID.x;
  uint localId = gl_SubgroupID;
  uint id = globalSize.x * ((globalSize.y * gl_WorkGroupID.z) + gl_WorkGroupID.y) + gl_WorkGroupID.x + localId;
  uint tempResult = 0;
  /// Exactly one active invocation writes this subgroup's reference slot.
  if (subgroupElect())
  {
    tempBuffer[id] = value;
  }
  /// All active subgroup invocations synchronize before reading that slot.
  subgroupBarrier();
  tempResult = tempBuffer[id];
  result[offset] = tempResult;
}
```

#### Additional Info

- Specialization IDs 0, 1, and 2 set the local workgroup dimensions; the required subgroup size is pipeline state rather than a shader constant.
- `tempImage` and `tempShared` remain declared because this source comes from the common non-election compute template, but this operation does not access them.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Operation test case leaf stem | Replaces `subgroupBarrier()` with another barrier and, for shared/image variants, changes the elected write and peer read to `tempShared` or `tempImage`; election uses a separate template. | [`getTestString`](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L1498-L1600) |
| Execution path | Compute uses this template; mesh/task specialize it with mesh layouts and terminal calls, while graphics and ray-tracing use per-stage declarations and shared standard builders. | [`initComputeOrMeshPrograms`](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L1611-L1758) |
| Required subgroup size | Does not alter GLSL text; runtime pipeline creation supplies each supported size. | [`test`](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L2010-L2034) |

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
; Bound: 102
; Schema: 0
               OpCapability Shader
               OpCapability GroupNonUniform
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_NumWorkGroups %gl_GlobalInvocationID %gl_SubgroupID %gl_WorkGroupID
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpSourceExtension "GL_KHR_shader_subgroup_basic"
               OpName %main "main"
               OpName %globalSize "globalSize"
               OpName %gl_NumWorkGroups "gl_NumWorkGroups"
               OpName %offset "offset"
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
               OpName %localId "localId"
               OpName %gl_SubgroupID "gl_SubgroupID"
               OpName %id "id"
               OpName %gl_WorkGroupID "gl_WorkGroupID"
               OpName %tempResult "tempResult"
               OpName %Buffer2 "Buffer2"
               OpMemberName %Buffer2 0 "tempBuffer"
               OpName %_ ""
               OpName %Buffer3 "Buffer3"
               OpMemberName %Buffer3 0 "value"
               OpName %__0 ""
               OpName %Buffer1 "Buffer1"
               OpMemberName %Buffer1 0 "result"
               OpName %__1 ""
               OpName %tempImage "tempImage"
               OpName %tempShared "tempShared"
               OpDecorate %gl_NumWorkGroups BuiltIn NumWorkgroups
               OpDecorate %13 SpecId 0
               OpDecorate %14 SpecId 1
               OpDecorate %15 SpecId 2
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %gl_SubgroupID BuiltIn SubgroupId
               OpDecorate %gl_WorkGroupID BuiltIn WorkgroupId
               OpDecorate %_runtimearr_uint ArrayStride 4
               OpDecorate %Buffer2 Block
               OpMemberDecorate %Buffer2 0 Offset 0
               OpDecorate %_ Binding 1
               OpDecorate %_ DescriptorSet 0
               OpDecorate %Buffer3 Block
               OpMemberDecorate %Buffer3 0 Offset 0
               OpDecorate %__0 Binding 2
               OpDecorate %__0 DescriptorSet 0
               OpDecorate %_runtimearr_uint_0 ArrayStride 4
               OpDecorate %Buffer1 Block
               OpMemberDecorate %Buffer1 0 Offset 0
               OpDecorate %__1 Binding 0
               OpDecorate %__1 DescriptorSet 0
               OpDecorate %tempImage Binding 3
               OpDecorate %tempImage DescriptorSet 0
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
%gl_SubgroupID = OpVariable %_ptr_Input_uint Input
%gl_WorkGroupID = OpVariable %_ptr_Input_v3uint Input
       %bool = OpTypeBool
     %uint_3 = OpConstant %uint 3
%_runtimearr_uint = OpTypeRuntimeArray %uint
    %Buffer2 = OpTypeStruct %_runtimearr_uint
%_ptr_StorageBuffer_Buffer2 = OpTypePointer StorageBuffer %Buffer2
          %_ = OpVariable %_ptr_StorageBuffer_Buffer2 StorageBuffer
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
    %Buffer3 = OpTypeStruct %uint
%_ptr_StorageBuffer_Buffer3 = OpTypePointer StorageBuffer %Buffer3
        %__0 = OpVariable %_ptr_StorageBuffer_Buffer3 StorageBuffer
%_ptr_StorageBuffer_uint = OpTypePointer StorageBuffer %uint
  %uint_3400 = OpConstant %uint 3400
%_runtimearr_uint_0 = OpTypeRuntimeArray %uint
    %Buffer1 = OpTypeStruct %_runtimearr_uint_0
%_ptr_StorageBuffer_Buffer1 = OpTypePointer StorageBuffer %Buffer1
        %__1 = OpVariable %_ptr_StorageBuffer_Buffer1 StorageBuffer
         %91 = OpTypeImage %uint 2D 0 0 0 2 R32ui
%_ptr_UniformConstant_91 = OpTypePointer UniformConstant %91
  %tempImage = OpVariable %_ptr_UniformConstant_91 UniformConstant
         %94 = OpSpecConstantOp %uint CompositeExtract %gl_WorkGroupSize 0
         %95 = OpSpecConstantOp %uint CompositeExtract %gl_WorkGroupSize 1
         %96 = OpSpecConstantOp %uint IMul %94 %95
         %97 = OpSpecConstantOp %uint CompositeExtract %gl_WorkGroupSize 2
         %98 = OpSpecConstantOp %uint IMul %96 %97
%_arr_uint_98 = OpTypeArray %uint %98
%_ptr_Workgroup__arr_uint_98 = OpTypePointer Workgroup %_arr_uint_98
 %tempShared = OpVariable %_ptr_Workgroup__arr_uint_98 Workgroup
       %main = OpFunction %void None %3
          %5 = OpLabel
 %globalSize = OpVariable %_ptr_Function_v3uint Function
     %offset = OpVariable %_ptr_Function_uint Function
    %localId = OpVariable %_ptr_Function_uint Function
         %id = OpVariable %_ptr_Function_uint Function
 %tempResult = OpVariable %_ptr_Function_uint Function
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
         %41 = OpLoad %uint %gl_SubgroupID
               OpStore %localId %41
         %43 = OpAccessChain %_ptr_Function_uint %globalSize %uint_0
         %44 = OpLoad %uint %43
         %45 = OpAccessChain %_ptr_Function_uint %globalSize %uint_1
         %46 = OpLoad %uint %45
         %48 = OpAccessChain %_ptr_Input_uint %gl_WorkGroupID %uint_2
         %49 = OpLoad %uint %48
         %50 = OpIMul %uint %46 %49
         %51 = OpAccessChain %_ptr_Input_uint %gl_WorkGroupID %uint_1
         %52 = OpLoad %uint %51
         %53 = OpIAdd %uint %50 %52
         %54 = OpIMul %uint %44 %53
         %55 = OpAccessChain %_ptr_Input_uint %gl_WorkGroupID %uint_0
         %56 = OpLoad %uint %55
         %57 = OpIAdd %uint %54 %56
         %58 = OpLoad %uint %localId
         %59 = OpIAdd %uint %57 %58
               OpStore %id %59
               OpStore %tempResult %uint_0
         %63 = OpGroupNonUniformElect %bool %uint_3
               OpSelectionMerge %65 None
               OpBranchConditional %63 %64 %65
         %64 = OpLabel
         %72 = OpLoad %uint %id
         %77 = OpAccessChain %_ptr_StorageBuffer_uint %__0 %int_0
         %78 = OpLoad %uint %77
         %79 = OpAccessChain %_ptr_StorageBuffer_uint %_ %int_0 %72
               OpStore %79 %78
               OpBranch %65
         %65 = OpLabel
               OpControlBarrier %uint_3 %uint_3 %uint_3400
         %81 = OpLoad %uint %id
         %82 = OpAccessChain %_ptr_StorageBuffer_uint %_ %int_0 %81
         %83 = OpLoad %uint %82
               OpStore %tempResult %83
         %88 = OpLoad %uint %offset
         %89 = OpLoad %uint %tempResult
         %90 = OpAccessChain %_ptr_StorageBuffer_uint %__1 %int_0 %88
               OpStore %90 %89
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- `supportedCheck` first requires subgroup support, `VK_SUBGROUP_FEATURE_BASIC_BIT`, and support for the selected shader stages. Non-election cases whose shader-stage set is not compute also require ballot support; the graphics and ray-tracing generated code uses election and broadcast to assign subgroup slots, while mesh/task code uses its subgroup ID directly.
- Compute and mesh barrier cases bind a result buffer, temporary buffer, one reference-value buffer, and an image. The shared variant uses shader-local `tempShared`; unused common-template resources remain bound or declared.
- The compute/mesh helper dispatches several workgroup and local-size shapes, waits for completion, invalidates result allocations, and invokes the selected callback. `checkComputeOrMeshSubgroupBarriers` obtains the reference from callback data and requires every result element to match it.
- Required-size compute and mesh cases loop from `minSubgroupSize` to `maxSubgroupSize`, doubling on each run. The first failing size is logged and returned; the registered case passes only when the entire range passes.
- All-stage graphics and ray-tracing paths allocate per-stage result and support data, run the applicable stages, and use callbacks that either compare election markers and counters or require every barrier result to equal the reference.
- Framebuffer cases render through one selected graphics stage. Their callbacks decode attachment components carrying the observed value, reference, elected marker, and pre-barrier value.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `subgroupelect` | Election or active-invocation handling does not produce exactly one elected invocation per subgroup, or the result/count transport is wrong. |
| `subgroupbarrier` | Subgroup execution synchronization or the associated memory dependency does not make the elected write visible before peer reads. |
| `subgroupmemorybarrier` | The general subgroup-scoped memory dependency does not make the elected write visible through the exercised resource path. |
| `subgroupmemorybarrierbuffer` | The buffer-memory subgroup dependency or buffer access path does not preserve the elected write for peer reads. |
| `subgroupmemorybarriershared` | The workgroup `shared`-memory subgroup dependency or shared-memory access path does not preserve the elected write for peer reads. |
| `subgroupmemorybarrierimage` | The image-memory subgroup dependency, storage-image access, or image result path does not preserve the elected write for peer reads. |

### Cause Analysis

#### Election or result/count transport failure

**Possible failure symptoms:** compute or mesh output contains a value other than `1`; an all-stage output contains neither `42` nor `13`; or the number of `42` markers disagrees with the atomic subgroup count.

**Possible implementation causes:** the subgroup election instruction may select zero or multiple active invocations, active-invocation handling may be wrong, or the shader/pipeline result transport may lose an elected marker or counter update. The Vulkan shader chapter requires `OpGroupNonUniformElect` to return true only for the lowest-id invocation in the group.

#### Subgroup control synchronization failure

**Possible failure symptoms:** at least one result element differs from the reference value after `subgroupBarrier()`, or a framebuffer result reports a pre-barrier value instead of the elected write.

**Possible implementation causes:** lowering or execution of the subgroup control barrier may fail to synchronize active subgroup invocations or apply its memory semantics before the following buffer read.

#### General subgroup memory dependency failure

**Possible failure symptoms:** a `subgroupmemorybarrier` result differs from the host reference even though the elected invocation wrote the subgroup slot.

**Possible implementation causes:** the general subgroup-scoped memory barrier may be lowered with incomplete scope or memory semantics, or the exercised resource access may not participate in the intended dependency. Source-level investigation is needed to distinguish those paths after a failure.

#### Buffer-memory dependency or access failure

**Possible failure symptoms:** only or primarily `subgroupmemorybarrierbuffer` cases return stale or unexpected SSBO values.

**Possible implementation causes:** subgroup buffer-memory semantics may be lowered incorrectly, or storage-buffer access/coherency handling may not preserve the elected write across the barrier.

#### Shared-memory dependency or access failure

**Possible failure symptoms:** compute, mesh, or task `subgroupmemorybarriershared` output differs from the reference while buffer-backed variants pass.

**Possible implementation causes:** workgroup `shared` storage addressing may alias subgroup slots incorrectly, or subgroup shared-memory barrier semantics may not make the elected store visible to peers. The affected invocations are in one workgroup because compute-like subgroups are contained within a local workgroup.

#### Image-memory dependency or access failure

**Possible failure symptoms:** `subgroupmemorybarrierimage` reports a stale texel or an unexpected value while corresponding buffer cases pass.

**Possible implementation causes:** the image-memory barrier may be lowered with incorrect scope/semantics, or storage-image format, addressing, write, or read handling may break the `r32ui` round trip.

## Case Pruning

### Requirement-based pruning

- All cases require subgroup support, `VK_SUBGROUP_FEATURE_BASIC_BIT`, and subgroup support in the selected shader stage.
- Required-size cases require `VK_EXT_subgroup_size_control`, `subgroupSizeControl`, `computeFullSubgroups`, and the selected stage in `requiredSubgroupSizeStages`.
- Non-election operations outside compute require `VK_SUBGROUP_FEATURE_BALLOT_BIT` because their helper code uses subgroup election and broadcast.
- Ray-tracing cases require `VK_KHR_ray_tracing_pipeline`. Mesh/task cases require `VK_EXT_mesh_shader` and `vertexPipelineStoresAndAtomics`; task cases also require `taskShader`.
- The graphics all-stage path requires fragment-stage SSBO writes. Shared-memory leaves are unavailable outside compute-like stages.

### Design-based pruning

- `subgroupmemorybarriershared` is not registered for `graphics`, `framebuffer`, or `ray_tracing` because shader `shared` storage is unavailable there.
- Framebuffer `subgroupelect_fragment` is deliberately omitted. The source comment says it is not tested but does not establish why, so no stronger rationale is inferred.
- Required-subgroup-size variants are generated only for compute, mesh, and task paths.
- Vulkan SC builds omit the ray-tracing and mesh branches.
- The main `test-issues.txt` contains no exclusion for `subgroups.basic`.

## Key Takeaways

- The operation test case leaf stem is the main behavioral axis: it selects election or a specific synchronization/resource dependency.
- Most barrier cases reduce to one pattern: elect a writer, write a reference, execute the selected subgroup barrier, then require every peer result to match.
- Compute and mesh required-size leaves apply the same rule at every advertised power-of-two subgroup size, not just one selected size.
- Different execution paths change resource transport and validation callbacks without changing the central election/barrier question.
- See `## Failure Meaning` to distinguish election, control synchronization, buffer, shared-memory, and image-memory failure signals.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Operation model | [`OpType`, `CaseDefinition`, and callbacks](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L43-L294) | Defines operations and path-specific result rules. |
| Framebuffer builder | [`initFrameBufferPrograms`](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L317-L1410) | Generates no-SSBO single-stage artifacts and fixed passthrough stages. |
| Shader behavior assembly | [`getTestString`](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L1498-L1600) | Emits the elected-write, barrier, and peer-read bodies. |
| Compute/mesh template | [`initComputeOrMeshPrograms`](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L1611-L1758) | Owns the representative compute shader and mesh/task specializations. |
| Exact builder | [`initPrograms`](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L1760-L1786) | Selects SPIR-V 1.3 or 1.4 and routes the stage set. |
| Support and runtime | [`supportedCheck` and `test`](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L1788-L2188) | Applies feature gates, resources, helpers, callbacks, and required-size sweeps. |
| Registration | [`createSubgroupsBasicTests`](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L2196-L2314) | Constructs exact hierarchy and executable leaf names. |
| Shared compute ballot | [`getSharedMemoryBallotHelper`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L867-L895) | Counts elected invocations for compute and mesh election. |
| Result scan | [`checkComputeOrMesh`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L2655-L2663) | Checks every compute-like result against one reference value. |
| Compute/mesh execution | [`makeComputeOrMeshTestRequiredSubgroupSize`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L3762-L4064) | Builds, submits, reads back, and validates compute-like runs. |
| Mustpass paths | [`subgroups.txt`](../../../mustpass/main/vk-default/subgroups.txt#L18372-L18441) | Confirms the registered compute, framebuffer, graphics, mesh, and ray-tracing leaves. |
| Subgroup semantics | [`shaders.adoc`](../../../../vulkan-docs/src/chapters/shaders.adoc#L3220-L3247) and [`shaders.adoc`](../../../../vulkan-docs/src/chapters/shaders.adoc#L3447-L3474) | Defines subgroup scope, basic operations, election, and barriers. |
| Required size rules | [`pipelines.adoc`](../../../../vulkan-docs/src/chapters/pipelines.adoc#L1503-L1549) | Defines required subgroup size and its legal range. |
| Advertised support | [`limits.adoc`](../../../../vulkan-docs/src/chapters/limits.adoc#L1305-L1353) | Defines supported subgroup stages and operation feature bits. |
