## Overview

**Core question:** When a compute pipeline is built under the dispatcher-selected pipeline-construction variant and dispatched across a known workgroup grid, do the per-invocation compute shader builtins (`gl_NumWorkGroups`, `gl_WorkGroupSize`, `gl_WorkGroupID`, `gl_LocalInvocationID`, `gl_GlobalInvocationID`, `gl_LocalInvocationIndex`) report the values the host expects?

- [`vktComputeShaderBuiltinVarTests.cpp`](../../../modules/vulkan/compute/vktComputeShaderBuiltinVarTests.cpp#L1) implements one test family rooted at `compute.pipeline.builtin_var`. It registers six cases plus a `_component` variant for the five vector builtins, covering vector reads and per-component reads of the same underlying value.
- The shader writes the builtin's value at an offset the host computes from `gl_GlobalInvocationID`; the host reads the result buffer back and compares every invocation's written value against an expected value derived from the dispatch parameters and the builtin's spec rule.
- The same descriptor and pipeline plumbing supports all six cases. The cases differ only in which builtin the shader stores and which formula the host uses for the per-invocation expected value.
- The page documents how each builtin is read by the shader, how the host computes the expected reference, and what a failure of each behavior parameter value would point to.

## Background Knowledge

- **The six compute-shader builtins covered here.** The five vector builtins are `gl_NumWorkGroups` (number of dispatched workgroups per axis), `gl_WorkGroupSize` (declared local size per axis), `gl_WorkGroupID` (this invocation's workgroup coordinate), `gl_LocalInvocationID` (this invocation's coordinate inside its workgroup), and `gl_GlobalInvocationID` (global coordinate). `gl_LocalInvocationIndex` is a flat scalar derived from `gl_LocalInvocationID` by the local-invocation linearization rule. Each vector builtin is a `uvec3`; `gl_LocalInvocationIndex` is a `uint`.
- **Specialization constants for `gl_WorkGroupSize`.** The generated shader declares both literal `layout(local_size_*)` values and `layout(local_size_*_id)` IDs. The IDs make the effective workgroup size specialization constants whose defaults are the literal values; the host supplies no specialization overrides. This ensures the `gl_WorkGroupSize` case exercises the specialization-constant representation of the builtin instead of reducing the local size to ordinary constants. Because the same header is emitted for every case, their SPIR-V may retain the `WorkgroupSize` specialization constants even when that builtin is not the stored result.
- **Test-side reuse of `gl_GlobalInvocationID`.** The same shader generator writes *every* builtin's value, so it must pick a storage offset independently of the builtin it is testing. Every shader uses `gl_GlobalInvocationID` to compute `offset = stride.u_stride.x * gl_GlobalInvocationID.z + stride.u_stride.y * gl_GlobalInvocationID.y + gl_GlobalInvocationID.x`, where `stride` is a uniform the host filled with `(globalSize.x * globalSize.y, globalSize.x)`. This means the storage index coincides with the linearized global invocation ID and lets the host iterate invocations independently of which builtin is being captured.
- **Vector vs per-component read paths.** Each of the five vector builtins is registered twice: once storing the whole vector (`sb_out.result[offset] = varName;`) and once storing each component individually (`sb_out.result[offset].x = varName.x;` etc.). The component path catches access-form regressions where the implementation lowers swizzles or component accesses incorrectly. The scalar `gl_LocalInvocationIndex` is registered once because it has no components to test separately.

> Limitation: this page grounds its claims in CTS source code and registration evidence only. The Vulkan specification chapter tree was not present in this environment at the time of writing, so spec citations for the exact semantics of each builtin (`BuiltIn NumWorkgroups`, `WorkgroupId`, `WorkgroupSize`, `GlobalInvocationId`, `LocalInvocationId`, `LocalInvocationIndex`) are not quoted. The shape, type, and reference formula for each builtin here is derived from the CTS source's `computeReference(...)` implementations and from the SPIR-V assembly's `OpDecorate ... BuiltIn ...` lines.

## Registration Hierarchy

```text
compute.pipeline.builtin_var
├── num_work_groups
├── num_work_groups_component
├── work_group_size
├── work_group_size_component
├── work_group_id
├── work_group_id_component
├── local_invocation_id
├── local_invocation_id_component
├── global_invocation_id
├── global_invocation_id_component
└── local_invocation_index
```

In Vulkan CTS builds, the category dispatcher replicates the same eleven children under each of its `pipeline`, `shader_object_spirv`, and `shader_object_binary` construction-mode roots. (Vulkan SC builds compile only the `pipeline` root.) The `vk-default/compute.txt` mustpass file lists the same eleven leaves under all three Vulkan roots, so the `compute.pipeline.builtin_var.*`, `compute.shader_object_spirv.builtin_var.*`, and `compute.shader_object_binary.builtin_var.*` ranges are all covered there.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Builtin under test | `num_work_groups`, `work_group_size`, `work_group_id`, `local_invocation_id`, `global_invocation_id`, `local_invocation_index` | Selects which GLSL builtin the shader writes to the storage buffer and which reference formula the host uses. | [vktComputeShaderBuiltinVarTests.cpp#L286-L449](../../../modules/vulkan/compute/vktComputeShaderBuiltinVarTests.cpp#L286-L449) |
| Vector vs per-component read | `*` (whole vector) or `*_component` | Decides whether the shader writes `sb_out.result[offset] = builtin;` or assigns each component individually. | [genBuiltinVarSource](../../../modules/vulkan/compute/vktComputeShaderBuiltinVarTests.cpp#L230-L284), [registration loop](../../../modules/vulkan/compute/vktComputeShaderBuiltinVarTests.cpp#L657-L671) |
| Local size per subcase | Inline `SubCase(localSize, numWorkGroups)` pairs (1,1,1), (2,1,1), (1,3,1), (2,3,4), (10,3,4), ... | Sets the `layout(local_size_*)` qualifiers and the dispatch grid used to derive the expected reference per builtin. | [NumWorkGroupsCase subcases](../../../modules/vulkan/compute/vktComputeShaderBuiltinVarTests.cpp#L294-L299), [WorkGroupSizeCase subcases](../../../modules/vulkan/compute/vktComputeShaderBuiltinVarTests.cpp#L321-L329), [WorkGroupIDCase subcases](../../../modules/vulkan/compute/vktComputeShaderBuiltinVarTests.cpp#L351-L356), [LocalInvocationIDCase subcases](../../../modules/vulkan/compute/vktComputeShaderBuiltinVarTests.cpp#L377-L385), [GlobalInvocationIDCase subcases](../../../modules/vulkan/compute/vktComputeShaderBuiltinVarTests.cpp#L406-L413), [LocalInvocationIndexCase subcases](../../../modules/vulkan/compute/vktComputeShaderBuiltinVarTests.cpp#L432-L437) |
| Pipeline construction type | `PIPELINE`, `SHADER_OBJECT_SPIRV`, `SHADER_OBJECT_BINARY` | Decides whether `ComputePipelineWrapper` builds a compute pipeline or a SPIR-V/binary shader object. | [dispatcher](../../../modules/vulkan/compute/vktComputeTests.cpp#L48-L85), [wrapper build](../../../framework/vulkan/vkComputePipelineConstructionUtil.cpp#L210-L289), [checkSupport](../../../modules/vulkan/compute/vktComputeShaderBuiltinVarTests.cpp#L169-L173) |

Each builtin case has its own `(localSize, numWorkGroups)` matrix; only `LocalInvocationIndexCase` omits the per-axis fan-out because the index is a scalar.

## Behavior Parameters

The primary behavioral axis for this page is the **builtin under test**. Each case class fixes one builtin, one GLSL data type (`uvec3` for the five vector builtins, `uint` for `gl_LocalInvocationIndex`), and one `computeReference(...)` formula. The host uses that formula to compute the expected value for every (workgroup, local) coordinate pair covered by the dispatch.

### `num_work_groups` — `gl_NumWorkGroups`

`NumWorkGroupsCase` declares the builtin type `uvec3`, exposes six `(localSize, numWorkGroups)` subcases, and returns `numWorkGroups` from `computeReference(...)`. The two read-mode variants are `num_work_groups` (whole-vector store) and `num_work_groups_component` (per-component store). The shader writes the count the host dispatched with; a failing case means the implementation observed a different dispatch shape than the host recorded [vktComputeShaderBuiltinVarTests.cpp#L286-L311], [vktComputeShaderBuiltinVarTests.cpp#L657-L671].

### `work_group_size` — `gl_WorkGroupSize`

`WorkGroupSizeCase` declares `uvec3` and returns `workGroupSize` (the local size declared on the case) from `computeReference(...)`. The nine subcases vary both local size and dispatch shape to cover `(1,1,1)`, `(2,1,1)`, `(1,3,1)`, `(1,1,7)`, `(10,3,4)`, and combinations thereof. The shader generator adds the `layout(local_size_*_id)` spec-constant IDs so that glslang cannot constant-fold `gl_WorkGroupSize` away. A failing case means the implementation returned a different workgroup size from the one the host declared [vktComputeShaderBuiltinVarTests.cpp#L313-L340], [vktComputeShaderBuiltinVarTests.cpp#L235-L242].

### `work_group_id` — `gl_WorkGroupID`

`WorkGroupIDCase` declares `uvec3` and returns `workGroupID` from `computeReference(...)`. The six subcases fan the dispatch across each axis individually (`(52,1,1)`, `(1,39,1)`, `(1,1,78)`, `(4,7,11)`, plus `(1,1,1)` and `(2,3,4) × (4,7,11)`). The whole-vector and `_component` variants test both store forms. A failing case means the implementation assigned an invocation to the wrong workgroup coordinate for one or more invocations [vktComputeShaderBuiltinVarTests.cpp#L342-L367].

### `local_invocation_id` — `gl_LocalInvocationID`

`LocalInvocationIDCase` declares `uvec3` and returns `localInvocationID` from `computeReference(...)`. The nine subcases exercise each local-size axis independently and stacked. Whole-vector and `_component` variants are registered. A failing case means the implementation assigned an invocation the wrong coordinate inside its workgroup [vktComputeShaderBuiltinVarTests.cpp#L369-L396].

### `global_invocation_id` — `gl_GlobalInvocationID`

`GlobalInvocationIDCase` declares `uvec3` and returns `workGroupID * workGroupSize + localInvocationID` from `computeReference(...)`. The eight subcases include single-axis dispatch stretches and the multi-axis `(4,7,11)` shape used by the `(2,3,4)` local size. The reference formula is the only one that combines workgroup and local coordinates [vktComputeShaderBuiltinVarTests.cpp#L398-L422]. Note that this case also uses `gl_GlobalInvocationID` to select the output slot. Consequently, some systematic wrong-ID permutations could be self-consistent (the value and destination move together) and escape this comparison; collisions, holes, out-of-range writes, or non-self-consistent errors should still fail. The other builtin cases use the same offset expression but store an independently derived value.

### `local_invocation_index` — `gl_LocalInvocationIndex`

`LocalInvocationIndexCase` declares `uint` (scalar) and returns `UVec3(localInvocationID.z() * workGroupSize.x() * workGroupSize.y() + localInvocationID.y() * workGroupSize.x() + localInvocationID.x(), 0, 0)`. Only the whole-vector read form is registered because the type has no per-component decomposition. A failing case means the implementation linearized the local coordinates differently than the spec's `x + y * size.x + z * size.x * size.y` rule [vktComputeShaderBuiltinVarTests.cpp#L424-L449], [vktComputeShaderBuiltinVarTests.cpp#L670-L671].

## Shader Analysis

The page's six cases share one shader-generation function (`ComputeBuiltinVarCase::genBuiltinVarSource`) parameterized by builtin name, data type, local size, and read mode. The representative walkthrough covers the `work_group_id` (vector read) case, which captures the full contract: builtin write, global-ID offset, descriptor set, dispatch barrier, and host readback.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.compute.pipeline.builtin_var.work_group_id
```

The same generated shader text backs the other four vector cases and the five `_component` variants; each case differs only in the substituted builtin identifier and whether per-component writes are emitted. The local-size `(2,3,4)` × workgroup `(4,7,11)` pairing comes from the `WorkGroupIDCase` constructor.

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `work_group_id` builtin | The `varName` substituted into both `GenBuiltinVarSource` and the `computeReference` formula. The variant set picks up the full compute coordinate contract. |
| `uvec3` result type | The shader writes a whole `uvec3` per invocation (`readByComponent = false`). The `ReadResultVec` / `compareNumComponents` helpers read the same three scalars back. |
| `localSize = (2,3,4)`, `numWorkGroups = (4,7,11)` | Picks a multi-axis shape that produces `(2*4, 3*7, 4*11) = (8, 21, 44)` global invocations per axis and confirms `gl_WorkGroupID` ranges independently across all three axes. |
| `readByComponent = false` | The vector store branch emits the single line `sb_out.result[offset] = gl_WorkGroupID;`, the whole-vector path the other nine vector leaves use, minus the `_component` siblings. |
| `pipeline` construction type | The pipeline-root run uses standard `vkCreateComputePipelines`. The mustpass coverage shows identical leaves under `shader_object_spirv` and `shader_object_binary`, which execute the same shader text against the same shader-object plumbing. |

#### Purpose

The shader writes `gl_WorkGroupID` at a per-invocation storage offset computed from `gl_GlobalInvocationID`. The host reads the buffer back, computes the expected value as `(groupX, groupY, groupZ)` for every dispatched invocation, and fails if any invocation wrote a different workgroup coordinate than the host expected.

#### Structural Design

| Phase | What the shader does | Inputs read | Outputs written |
|-------|----------------------|-------------|-----------------|
| Offset | Compute the flat storage offset from `gl_GlobalInvocationID` using the host-supplied uniform stride. | `stride.u_stride.x`, `stride.u_stride.y`, `gl_GlobalInvocationID` | `offset` (function-local `uint`) |
| Write | Store the builtin value at the offset. | `gl_WorkGroupID` (vector read mode) | `sb_out.result[offset]` |

The offset phase is shared by every case in the family. The write phase differs only in which builtin identifier the generator substitutes. The `_component` variants replace the write phase with a per-component ladder that hits all of `.x`, `.y` (and `.z` / `.w` as applicable).

#### Shader Code

```glsl
#version 310 es
// Generated by ComputeBuiltinVarCase::genBuiltinVarSource, vector read mode (readByComponent = false).
// Selected dimensions: local_size = (2,3,4), workgroups = (4,7,11).
layout (local_size_x = 2, local_size_y = 3, local_size_z = 4) in;
/// Forces glslang to surface gl_WorkGroupSize via spec constants rather than constant-folding it
/// away; the host leaves the spec constants at their defaults so the builtin read survives lowering.
layout (local_size_x_id = 0, local_size_y_id = 1, local_size_z_id = 2) in;

/// Binding 0 is the stride uniform that the host populated with
/// (globalSize.x * globalSize.y, globalSize.x) so the same offset math works for any grid shape.
layout(set = 0, binding = 0) uniform Stride
{
    uvec2 u_stride;
} stride;
/// Binding 1 is the per-invocation result buffer. Each invocation writes one uvec3 here at offset
/// (= linearized global invocation id). The host invalidates and reads it back after the barrier.
layout(set = 0, binding = 1, std430) buffer Output
{
    uvec3 result[];
} sb_out;

void main (void)
{
    highp uint offset =
        stride.u_stride.x * gl_GlobalInvocationID.z +
        stride.u_stride.y * gl_GlobalInvocationID.y +
        gl_GlobalInvocationID.x;

    sb_out.result[offset] = gl_WorkGroupID;
}
```

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Builtin under test | The generator substitutes the case's `m_varName` (`gl_NumWorkGroups`, `gl_WorkGroupSize`, `gl_WorkGroupID`, `gl_LocalInvocationID`, `gl_GlobalInvocationID`, `gl_LocalInvocationIndex`) for the GLSL identifier on the right-hand side of the store. | [case constructor `super(...)` calls](../../../modules/vulkan/compute/vktComputeShaderBuiltinVarTests.cpp#L290-L448) |
| Read mode | `readByComponent = true` flips the write to a per-component ladder that assigns `.x`, `.y`, `.z` (and `.w` for uvec4) individually. Only the uvec3/uvec4 data types take this branch; the scalar `gl_LocalInvocationIndex` stays on the vector store form. | [genBuiltinVarSource per-component branch](../../../modules/vulkan/compute/vktComputeShaderBuiltinVarTests.cpp#L258-L276) |
| Local size | The `(localSize.x, localSize.y, localSize.z)` triple is substituted into the `layout(local_size_*)` qualifiers, with the same triple feeding `OpSpecConstant` IDs 0-2. The shader text looks identical aside from those substitutions. | [genBuiltinVarSource header](../../../modules/vulkan/compute/vktComputeShaderBuiltinVarTests.cpp#L235-L242) |
| Pipeline construction type | The shader text is identical under all three dispatcher roots. `ComputePipelineWrapper` decides at build time whether to create a compute pipeline or a shader object; the binary variant first creates a SPIR-V shader object, retrieves its binary, then recreates it from that binary. | [dispatcher](../../../modules/vulkan/compute/vktComputeTests.cpp#L68-L85), [wrapper build](../../../framework/vulkan/vkComputePipelineConstructionUtil.cpp#L210-L289) |

#### Additional Info

- The five vector cases all share the same shader template; only the substituted GLSL identifier (`gl_NumWorkGroups`, `gl_WorkGroupSize`, `gl_WorkGroupID`, `gl_LocalInvocationID`, `gl_GlobalInvocationID`) changes. The differences in test behavior come from the host's `computeReference` formula and from the `(localSize, numWorkGroups)` subcase matrix chosen by each case class.
- The `work_group_size` case is the only one where the generator's `layout(local_size_*_id)` declarations are functionally relevant: they prevent GLSL frontends from constant-folding the builtin read away. For the other cases the layout spec IDs exist for symmetry but do not change the test contract.
- The `local_invocation_index` case uses `glu::TYPE_UINT` (scalar), so the shader's `buffer Output { uint result[]; }` is one element wide per invocation and the `resultBufferStride` in `iterate()` reduces to `sizeof(uint32_t)`.

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `comp`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 50
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_GlobalInvocationID %gl_WorkGroupID
               OpExecutionMode %main LocalSize 2 3 4
               OpSource ESSL 310
               OpName %main "main"
               OpName %offset "offset"
               OpName %Stride "Stride"
               OpMemberName %Stride 0 "u_stride"
               OpName %stride "stride"
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
               OpName %Output "Output"
               OpMemberName %Output 0 "result"
               OpName %sb_out "sb_out"
               OpName %gl_WorkGroupID "gl_WorkGroupID"
               OpDecorate %Stride Block
               OpMemberDecorate %Stride 0 Offset 0
               OpDecorate %stride Binding 0
               OpDecorate %stride DescriptorSet 0
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %_runtimearr_v3uint ArrayStride 16
               OpDecorate %Output BufferBlock
               OpMemberDecorate %Output 0 Offset 0
               OpDecorate %sb_out Binding 1
               OpDecorate %sb_out DescriptorSet 0
               OpDecorate %gl_WorkGroupID BuiltIn WorkgroupId
               OpDecorate %46 SpecId 0
               OpDecorate %47 SpecId 1
               OpDecorate %48 SpecId 2
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
     %v2uint = OpTypeVector %uint 2
     %Stride = OpTypeStruct %v2uint
%_ptr_Uniform_Stride = OpTypePointer Uniform %Stride
     %stride = OpVariable %_ptr_Uniform_Stride Uniform
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
     %uint_0 = OpConstant %uint 0
%_ptr_Uniform_uint = OpTypePointer Uniform %uint
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
     %uint_2 = OpConstant %uint 2
%_ptr_Input_uint = OpTypePointer Input %uint
     %uint_1 = OpConstant %uint 1
%_runtimearr_v3uint = OpTypeRuntimeArray %v3uint
     %Output = OpTypeStruct %_runtimearr_v3uint
%_ptr_Uniform_Output = OpTypePointer Uniform %Output
     %sb_out = OpVariable %_ptr_Uniform_Output Uniform
%gl_WorkGroupID = OpVariable %_ptr_Input_v3uint Input
%_ptr_Uniform_v3uint = OpTypePointer Uniform %v3uint
         %46 = OpSpecConstant %uint 2
         %47 = OpSpecConstant %uint 3
         %48 = OpSpecConstant %uint 4
%gl_WorkGroupSize = OpSpecConstantComposite %v3uint %46 %47 %48
       %main = OpFunction %void None %3
          %5 = OpLabel
     %offset = OpVariable %_ptr_Function_uint Function
         %17 = OpAccessChain %_ptr_Uniform_uint %stride %int_0 %uint_0
         %18 = OpLoad %uint %17
         %24 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_2
         %25 = OpLoad %uint %24
         %26 = OpIMul %uint %18 %25
         %28 = OpAccessChain %_ptr_Uniform_uint %stride %int_0 %uint_1
         %29 = OpLoad %uint %28
         %30 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_1
         %31 = OpLoad %uint %30
         %32 = OpIMul %uint %29 %31
         %33 = OpIAdd %uint %26 %32
         %34 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %35 = OpLoad %uint %34
         %36 = OpIAdd %uint %33 %35
               OpStore %offset %36
         %41 = OpLoad %uint %offset
         %43 = OpLoad %v3uint %gl_WorkGroupID
         %45 = OpAccessChain %_ptr_Uniform_v3uint %sb_out %int_0 %41
               OpStore %45 %43
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- **Resource setup.** The instance allocates one host-visible uniform buffer that holds `tcu::UVec2(globalSize.x * globalSize.y, globalSize.x)` and one host-visible storage buffer of `numInvocations * resultBufferStride` bytes. `resultBufferStride` is `sizeof(UVec4)` for `uvec3` cases and `sizeof(uint32_t)` for the scalar `local_invocation_index` case. The descriptor set layout has one `UNIFORM_BUFFER` binding (stride) and one `STORAGE_BUFFER` binding (result buffer) [vktComputeShaderBuiltinVarTests.cpp#L501-L531].
- **Pipeline build.** `ComputePipelineWrapper` is constructed with the `vk::ComputePipelineConstructionType` that the category dispatcher passed in. For `PIPELINE` it creates a conventional compute pipeline; for `SHADER_OBJECT_SPIRV` it creates a shader object from SPIR-V; for `SHADER_OBJECT_BINARY` it retrieves binary code from an initially created shader object and recreates the shader object from that binary. The wrapper uses the per-subcase compiled shader binary retrieved by `program_name = "compute_<i>"` [vktComputeShaderBuiltinVarTests.cpp#L522-L525], [vkComputePipelineConstructionUtil.cpp#L210-L289](../../../framework/vulkan/vkComputePipelineConstructionUtil.cpp#L210-L289).
- **Dispatch and barrier.** The command buffer binds the pipeline, binds the descriptor set, dispatches `cmdDispatch(numWorkGroups.x, numWorkGroups.y, numWorkGroups.z)`, then issues a `cmdPipelineBarrier(COMPUTE_SHADER_BIT → HOST_BIT)` over the result buffer. After `submitCommandsAndWait` the host invalidates the result allocation [vktComputeShaderBuiltinVarTests.cpp#L541-L576].
- **Host-side reference loop.** The instance iterates `groupZ × groupY × groupX × localZ × localY × localX`, derives the per-invocation `refGroupID` and `refLocalID`, computes the linearized `refOffset` against the stride uniform, asks the case class for the expected `refValue` via `computeReference(...)`, reads `numScalars` scalars from the buffer, and compares them via `compareNumComponents`. The first 10 mismatches are written to the test log as `ERROR: comparison failed at offset <n>: expected <v>, got <v>`; further mismatches are summarized as `...`. The final summary line is `<numInvocations - numFailed> / <numInvocations> values passed`. The case fails when `numFailed > 0` and returns `incomplete` until every subcase has run [vktComputeShaderBuiltinVarTests.cpp#L580-L632].
- **Reference formulas per case.** The per-invocation expected value is the case's `computeReference(numWorkGroups, workGroupSize, workGroupID, localInvocationID)` result. `NumWorkGroups` returns the unchanged `numWorkGroups` arg; `WorkGroupSize` returns `workGroupSize`; `WorkGroupID` returns `workGroupID`; `LocalInvocationID` returns `localInvocationID`; `GlobalInvocationID` returns `workGroupID * workGroupSize + localInvocationID`; `LocalInvocationIndex` returns `UVec3(localInvocationID.z() * workGroupSize.x() * workGroupSize.y() + localInvocationID.y() * workGroupSize.x() + localInvocationID.x(), 0, 0)` [vktComputeShaderBuiltinVarTests.cpp#L286-L449].
- **Pass/fail.** The test group returns `fail("Comparison failed")` if any iteration reports a mismatch. It returns `pass("Comparison succeeded")` once every `SubCase` has run with no mismatches.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `num_work_groups` | Wrong dispatch grid reaching the shader; the implementation ignoring `cmdDispatch` group counts. |
| `num_work_groups_component` | Wrong per-component access of `gl_NumWorkGroups`; swizzle or component access lowering bug. |
| `work_group_size` | Implementation returning a different workgroup size than declared; spec-constant optimization bypassing the builtin read. |
| `work_group_size_component` | Wrong per-component access of `gl_WorkGroupSize`; swizzle or component access lowering bug. |
| `work_group_id` | Wrong workgroup coordinate assigned to one or more invocations; cross-axis partitioning bug. |
| `work_group_id_component` | Wrong per-component access of `gl_WorkGroupID`; swizzle or component access lowering bug. |
| `local_invocation_id` | Wrong intra-workgroup coordinate assigned to one or more invocations. |
| `local_invocation_id_component` | Wrong per-component access of `gl_LocalInvocationID`; swizzle or component access lowering bug. |
| `global_invocation_id` | Wrong global coordinate composed from workgroup ID and local ID, except for a possible self-indexing blind spot because the tested builtin also chooses the output slot. |
| `global_invocation_id_component` | Wrong per-component access of `gl_GlobalInvocationID`; swizzle or component access lowering bug. |
| `local_invocation_index` | Wrong linearization of local coordinates relative to `x + y * size.x + z * size.x * size.y`. |

### Cause Analysis

#### `num_work_groups` failures

**Possible failure symptoms:** `ERROR: comparison failed at offset <n>: expected <(gx,gy,gz)>, got <(gx,gy,gz)>` for one or more invocations, where `expected` is the host-recorded dispatch triple and `got` differs on one or more axes.

**Possible implementation causes:** The dispatch layer did not propagate the workgroup count recorded by the host command buffer to the shader. A driver that ignores `cmdDispatch(groupCountX, ...)` arguments or one that substitutes its own dispatch shape from the pipeline layout could produce this symptom. Other failure sources (driver scheduler, descriptor binding skew) require source-level investigation.

#### `work_group_size` failures

**Possible failure symptoms:** `ERROR: comparison failed at offset <n>` for `expected` triples that match the case's local size, while `got` reflects a different shape.

**Possible implementation causes:** A shader compiler that returns the spec-constant defaults (`(2,3,4)` in this walkthrough) instead of the declared local size would surface as the full default triple being written by every invocation. A GLSL frontend that constant-folds `gl_WorkGroupSize` against the static `layout(local_size_*)` qualifiers weakens the test, which is why the generator emits the `local_size_*_id` spec-constant IDs as well. Other failure sources (driver recompile path, pipeline cache mismatch) require source-level investigation.

#### `work_group_id` failures

**Possible failure symptoms:** `ERROR: comparison failed at offset <n>: expected <(gx,gy,gz)>, got <(gx',gy',gz')>` where the two triples differ on one or more axes.

**Possible implementation causes:** A workload splitter that distributes invocations across workgroups using a different rule from the host's `cmdDispatch(groupCount)` arguments would produce this mismatch. A driver that propagates base offsets (`VK_PIPELINE_CREATE_DISPATCH_BASE`) to the workgroup ID without honoring it as an `gl_WorkGroupID`-neutral per-group offset can also produce mismatches, though this family does not exercise the dispatch-base path; that contract is covered by the `basic` and `device_group` families.

#### `local_invocation_id` failures

**Possible failure symptoms:** `ERROR: comparison failed at offset <n>: expected <(lx,ly,lz)>, got <(...)>` with `lx < localSize.x`, etc.

**Possible implementation causes:** A shader compiler or scheduler that miscounts invocations within a workgroup would swap or skip local coordinates. The descriptor set, barrier, and dispatch remain unchanged, so the failure is local to per-invocation coordinate assignment.

#### `global_invocation_id` failures

**Possible failure symptoms:** `ERROR: comparison failed at offset <n>: expected <(gx*lsx + lx, ...)>, got <(...)>`. The expected value is the per-axis sum `workGroupID * workGroupSize + localInvocationID`.

**Possible implementation causes:** A driver or compiler that supplies the wrong global coordinate, or a storage-layout/write problem, can produce a mismatch. Interpretation needs care: the shader uses `gl_GlobalInvocationID` both as the stored value and to calculate its destination. A bijective wrong-ID mapping over the expected grid can therefore write each wrong value into the correspondingly wrong slot and leave a buffer that still looks correct to the host. This case reliably exposes errors that create collisions, holes, out-of-range accesses, or disagreement between destination and value, but it does not independently prove every invocation received the correct global ID.

#### `local_invocation_index` failures

**Possible failure symptoms:** `ERROR: comparison failed at offset <n>: expected <(x + y*lsx + z*lsx*lsy, 0, 0)>, got <(...)>`.

**Possible implementation causes:** A linearization rule other than `x + y * size.x + z * size.x * size.y` would shift every index except `(0,0,0)` and produce a per-invocation mismatched scalar. This is most often a driver or shader-compiler lowering bug on `gl_LocalInvocationIndex`; other failure sources (offset-by-one in the host stride uniform) require source-level investigation.

## Case Pruning

### Requirement-based pruning

- Each case calls `checkShaderObjectRequirements(...)` for its chosen `vk::ComputePipelineConstructionType` [vktComputeShaderBuiltinVarTests.cpp#L169-L173]. The dispatcher still registers the shader-object roots in non-Vulkan-SC builds; unsupported shader-object requirements cause the affected cases to report not-supported rather than removing those roots from the hierarchy. Vulkan SC excludes both shader-object roots at compile time [vktComputeTests.cpp#L64-L82](../../../modules/vulkan/compute/vktComputeTests.cpp#L64-L82).
- The `std430` storage buffer gives a `uvec3` runtime-array element a 16-byte stride, which is why the host uses `sizeof(tcu::UVec4)` for `TYPE_UINT_VEC3` [vktComputeShaderBuiltinVarTests.cpp#L482-L499](../../../modules/vulkan/compute/vktComputeShaderBuiltinVarTests.cpp#L482-L499). This is ordinary resource setup, not a case-pruning condition.

### Design-based pruning

- The five vector builtins each get a `_component` variant to cover both whole-vector and per-component read paths; `gl_LocalInvocationIndex` is scalar, so the source notes that it is not duplicated [vktComputeShaderBuiltinVarTests.cpp#L670-L671].
- Each case class picks its own `(localSize, numWorkGroups)` matrix. `NumWorkGroupsCase` and `WorkGroupIDCase` exercise single-axis stretch and multi-axis shapes; `WorkGroupSizeCase` and `LocalInvocationIDCase` add a `(10,3,4)` shape to cover non-uniform local sizes; `GlobalInvocationIDCase` adds `(10,3,4) × (3,1,2)`; `LocalInvocationIndexCase` drops the single-axis per-coordinate stretches because the linearization is the same shape on any axis [vktComputeShaderBuiltinVarTests.cpp#L286-L449].
- The `work_group_id`, `num_work_groups`, `local_invocation_id`, and `global_invocation_id` cases overlap on the `(1,1,1) × (1,1,1)` and `(2,3,4) × (4,7,11)` shapes; the duplicated subcases confirm that all three builtins agree on the same dispatch.

## Key Takeaways

- The six cases answer one question per builtin: does the value the shader observes match the host-expected reference under the same dispatch shape and pipeline-construction variant?
- The shader template is shared across all six cases; it stores one builtin identifier at a per-invocation offset computed from `gl_GlobalInvocationID` and a host-supplied stride uniform. The test behavior differs through `computeReference(...)` formulas and through each case's `(localSize, numWorkGroups)` matrix.
- The five vector builtins each have a whole-vector and a `_component` sibling. The `_component` variant catches swizzle or per-component lowering regressions that the whole-vector variant misses.
- The `work_group_size` case adds `layout(local_size_*_id)` spec-constant IDs to prevent the GLSL frontend from constant-folding the builtin read away. The SPIR-V for every case in this family includes the spec constants because the generator emits the same header for all of them.
- The host verification is per-invocation: the result buffer is invalidated after the dispatch-to-host barrier, then iterated across `(groupZ, groupY, groupX, localZ, localY, localX)` with each invocation's expected value computed by the case's `computeReference(...)`. The first ten mismatches are logged; further mismatches are summarized as `...`. The whole case fails when any single mismatch is observed.
- See `## Failure Meaning` for per-builtin failure analysis grounded in the test's validation logic.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `ComputeBuiltinVarCase::genBuiltinVarSource` | [vktComputeShaderBuiltinVarTests.cpp#L230-L284](../../../modules/vulkan/compute/vktComputeShaderBuiltinVarTests.cpp#L230-L284) | One shader generator parameterized by builtin identifier, type, local size, and read mode. |
| `ComputeBuiltinVarCase::initPrograms` | [vktComputeShaderBuiltinVarTests.cpp#L218-L228](../../../modules/vulkan/compute/vktComputeShaderBuiltinVarTests.cpp#L218-L228) | Per-subcase shader name `compute_<i>` registration. |
| `ComputeBuiltinVarCase::checkSupport` | [vktComputeShaderBuiltinVarTests.cpp#L169-L173](../../../modules/vulkan/compute/vktComputeShaderBuiltinVarTests.cpp#L169-L173) | Shader-object requirements check from the chosen pipeline-construction type. |
| `NumWorkGroupsCase` | [vktComputeShaderBuiltinVarTests.cpp#L286-L311](../../../modules/vulkan/compute/vktComputeShaderBuiltinVarTests.cpp#L286-L311) | `gl_NumWorkGroups` subcases and `computeReference`. |
| `WorkGroupSizeCase` | [vktComputeShaderBuiltinVarTests.cpp#L313-L340](../../../modules/vulkan/compute/vktComputeShaderBuiltinVarTests.cpp#L313-L340) | `gl_WorkGroupSize` subcases and `computeReference`. |
| `WorkGroupIDCase` | [vktComputeShaderBuiltinVarTests.cpp#L342-L367](../../../modules/vulkan/compute/vktComputeShaderBuiltinVarTests.cpp#L342-L367) | `gl_WorkGroupID` subcases and `computeReference`. |
| `LocalInvocationIDCase` | [vktComputeShaderBuiltinVarTests.cpp#L369-L396](../../../modules/vulkan/compute/vktComputeShaderBuiltinVarTests.cpp#L369-L396) | `gl_LocalInvocationID` subcases and `computeReference`. |
| `GlobalInvocationIDCase` | [vktComputeShaderBuiltinVarTests.cpp#L398-L422](../../../modules/vulkan/compute/vktComputeShaderBuiltinVarTests.cpp#L398-L422) | `gl_GlobalInvocationID` subcases and `computeReference`. |
| `LocalInvocationIndexCase` | [vktComputeShaderBuiltinVarTests.cpp#L424-L449](../../../modules/vulkan/compute/vktComputeShaderBuiltinVarTests.cpp#L424-L449) | `gl_LocalInvocationIndex` scalar subcases and `computeReference`. |
| `ComputeBuiltinVarInstance::iterate` | [vktComputeShaderBuiltinVarTests.cpp#L468-L633](../../../modules/vulkan/compute/vktComputeShaderBuiltinVarTests.cpp#L468-L633) | Dispatch, barrier, and per-invocation reference loop. |
| `ComputeShaderBuiltinVarTests::init` | [vktComputeShaderBuiltinVarTests.cpp#L657-L671](../../../modules/vulkan/compute/vktComputeShaderBuiltinVarTests.cpp#L657-L671) | Vector read modes and scalar `local_invocation_index` registration. |
| `createComputeShaderBuiltinVarTests` | [vktComputeShaderBuiltinVarTests.cpp#L676-L680](../../../modules/vulkan/compute/vktComputeShaderBuiltinVarTests.cpp#L676-L680) | Factory entrypoint consumed by the category dispatcher. |
| Header | [vktComputeShaderBuiltinVarTests.hpp#L36-L37](../../../modules/vulkan/compute/vktComputeShaderBuiltinVarTests.hpp#L36-L37) | `createComputeShaderBuiltinVarTests` declaration. |
| Category dispatcher | [vktComputeTests.cpp#L48-L85](../../../modules/vulkan/compute/vktComputeTests.cpp#L48-L85) | `pipeline` / `shader_object_spirv` / `shader_object_binary` roots. |
| Mustpass coverage | [vk-default/compute.txt#L86-L96](../../../mustpass/main/vk-default/compute.txt#L86-L96) | `dEQP-VK.compute.pipeline.builtin_var.*` leaves. |
| Mustpass coverage (shader-object roots) | [vk-default/compute.txt#L20371-L20381](../../../mustpass/main/vk-default/compute.txt#L20371-L20381), [vk-default/compute.txt#L40643-L40653](../../../mustpass/main/vk-default/compute.txt#L40643-L40653) | `dEQP-VK.compute.shader_object_{binary,spirv}.builtin_var.*` leaves. |
