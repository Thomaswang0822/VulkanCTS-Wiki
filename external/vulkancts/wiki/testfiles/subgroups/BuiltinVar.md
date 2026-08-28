## Overview

**Core question:** Do shader invocations report subgroup built-ins that satisfy their specified size and index relationships?

- [`vktSubgroupsBuiltinVarTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsBuiltinVarTests.cpp) implements the `subgroups.builtin_var` test family.
- Compute, mesh, and task shaders record all four built-ins. Graphics, framebuffer, and ray-tracing shaders record only `gl_SubgroupSize` and `gl_SubgroupInvocationID`; each case checks the relationship selected by its test case leaf.
- The tests exercise the same invariants through compute, graphics, framebuffer, ray-tracing, mesh, and task execution paths where those paths exist.

## Background Knowledge

For the shared concepts subgroup identity and subgroup-size control, see [Background Knowledge](../../categories/subgroups.md#background-knowledge) of the `subgroups` page.

- `NumSubgroups` is the number of subgroups in a local workgroup. `SubgroupId` is the subgroup's index in `[0, NumSubgroups - 1]`. These two built-ins apply to compute, mesh, and task execution models.

## Registration Hierarchy

```text
subgroups.builtin_var
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
| Built-in value | `subgroupsize`, `subgroupinvocationid`, `numsubgroups`, `subgroupid` | Selects the recorded component and host-side invariant. The last two values apply only to workgroup execution models: compute, mesh, and task. | [`TestType` and registration lists](../../../modules/vulkan/subgroups/vktSubgroupsBuiltinVarTests.cpp#L43-L58) |
| Execution path | `graphics`, `compute`, `framebuffer`, `ray_tracing`, `mesh` | Selects the pipeline and result transport. `mesh` contains mesh- and task-stage leaves. | [`createSubgroupsBuiltinVarTests`](../../../modules/vulkan/subgroups/vktSubgroupsBuiltinVarTests.cpp#L1946-L2106) |
| Shader stage | all graphics stages as one case; compute; vertex, tessellation control, tessellation evaluation, and geometry framebuffer leaves; ray-tracing stages; mesh or task | Expands the built-in check across stage-specific program and harness paths. | [Stage arrays and case construction](../../../modules/vulkan/subgroups/vktSubgroupsBuiltinVarTests.cpp#L1964-L2094) |
| Required subgroup size | ordinary leaf or `_requiredsubgroupsize` leaf | Required-size compute, mesh, and task cases test every supported power-of-two size. | [Required-size registration](../../../modules/vulkan/subgroups/vktSubgroupsBuiltinVarTests.cpp#L2007-L2092) and [runtime loop](../../../modules/vulkan/subgroups/vktSubgroupsBuiltinVarTests.cpp#L1742-L1901) |

## Behavior Parameters

The primary behavioral axis is the **built-in value**: each value selects a different specified relationship and host check. The execution path, stage, and required-size choice change where that relationship is exercised, not what it means.

### `subgroupsize`: subgroup invocation capacity

Each invocation records `gl_SubgroupSize`. The host requires every checked record to equal the subgroup size supplied by the harness. A `_requiredsubgroupsize` case repeats the test for each supported power-of-two size from `minSubgroupSize` through `maxSubgroupSize`.

### `subgroupinvocationid`: invocation index within the subgroup

Each invocation is expected to record `gl_SubgroupInvocationID`, and the host rejects values outside `[0, subgroupSize - 1]`. It also sums a histogram of the scanned IDs, but every in-range record contributes exactly once, so that sum does not impose a uniqueness or dense-ID requirement. Repeated IDs and missing ID values can pass.

### `numsubgroups`: subgroup count in the local workgroup

Compute, mesh, and task invocations record `gl_NumSubgroups`. The host checks the source's chosen upper bound: the value must not exceed the number of local invocations. This is not an exact partition-count check.

### `subgroupid`: subgroup index within the local workgroup

Compute, mesh, and task invocations record both `gl_SubgroupID` and `gl_NumSubgroups`. The host requires `gl_SubgroupID < gl_NumSubgroups` for every invocation.

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.subgroups.builtin_var.compute.subgroupsize_compute
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `compute` execution path | Uses the direct GLSL branch of `initPrograms`, a storage-buffer result, and specialization-controlled local sizes. |
| `subgroupsize_compute` | Selects the ordinary subgroup-size case without required subgroup-size pipeline state. |
| `initPrograms` | This exact builder emits the representative compute shader and targets SPIR-V 1.3. |

#### Purpose

The shader records the subgroup size seen by every compute invocation. The host later checks every first component against the subgroup size reported by the test harness.

#### Structural Design

| Phase | Shader action | Observable result |
|-------|---------------|-------------------|
| Addressing | Multiply workgroup count by local size and flatten `gl_GlobalInvocationID`. | One unique SSBO element per global invocation. |
| Observation | Read all four subgroup built-ins. | A single `uvec4` captures invocation- and workgroup-level subgroup facts. |
| Recording | Store the vector at the flattened offset. | The host can select component 0 for this `subgroupsize` leaf. |

#### Shader Code

```glsl
#version 450
#extension GL_KHR_shader_subgroup_basic: enable
/// Local sizes are specialization constants 0, 1, and 2; the harness chooses the dispatch shape.
layout (local_size_x_id = 0, local_size_y_id = 1, local_size_z_id = 2) in;

/// Binding 0 is a std430 storage buffer with one uvec4 record per global invocation.
layout(set = 0, binding = 0, std430) buffer Output
{
  uvec4 result[];
};

void main (void)
{
  /// Flatten the 3D dispatch coordinate to a unique output record.
  uvec3 globalSize = gl_NumWorkGroups * gl_WorkGroupSize;
  highp uint offset = globalSize.x * ((globalSize.y * gl_GlobalInvocationID.z) + gl_GlobalInvocationID.y) + gl_GlobalInvocationID.x;
  /// Store all four built-ins so the host can select the component for this test case.
  result[offset] = uvec4(gl_SubgroupSize, gl_SubgroupInvocationID, gl_NumSubgroups, gl_SubgroupID);
}
```

#### Additional Info

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Built-in value | The compute shader remains the same and records all four values; the case selects a different host callback and component relationship. | [`initPrograms` and check callbacks](../../../modules/vulkan/subgroups/vktSubgroupsBuiltinVarTests.cpp#L983-L1010) |
| Required subgroup size | Shader text is unchanged; the harness applies required subgroup-size pipeline state and reruns supported power-of-two sizes. | [`test`](../../../modules/vulkan/subgroups/vktSubgroupsBuiltinVarTests.cpp#L1727-L1901) |
| Execution path | Graphics/framebuffer use stage-specific direct SPIR-V, while mesh/task and ray tracing use shared GLSL generation with different pipeline interfaces. | [`initFrameBufferPrograms` and `initPrograms`](../../../modules/vulkan/subgroups/vktSubgroupsBuiltinVarTests.cpp#L317-L1628) |

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
; Bound: 58
; Schema: 0
               OpCapability Shader
               OpCapability GroupNonUniform
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_NumWorkGroups %gl_GlobalInvocationID %gl_SubgroupSize %gl_SubgroupInvocationID %gl_NumSubgroups %gl_SubgroupID
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpSourceExtension "GL_KHR_shader_subgroup_basic"
               OpName %main "main"
               OpName %globalSize "globalSize"
               OpName %gl_NumWorkGroups "gl_NumWorkGroups"
               OpName %offset "offset"
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
               OpName %Output "Output"
               OpMemberName %Output 0 "result"
               OpName %_ ""
               OpName %gl_SubgroupSize "gl_SubgroupSize"
               OpName %gl_SubgroupInvocationID "gl_SubgroupInvocationID"
               OpName %gl_NumSubgroups "gl_NumSubgroups"
               OpName %gl_SubgroupID "gl_SubgroupID"
               OpDecorate %gl_NumWorkGroups BuiltIn NumWorkgroups
               OpDecorate %13 SpecId 0
               OpDecorate %14 SpecId 1
               OpDecorate %15 SpecId 2
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %_runtimearr_v4uint ArrayStride 16
               OpDecorate %Output Block
               OpMemberDecorate %Output 0 Offset 0
               OpDecorate %_ Binding 0
               OpDecorate %_ DescriptorSet 0
               OpDecorate %gl_SubgroupSize RelaxedPrecision
               OpDecorate %gl_SubgroupSize BuiltIn SubgroupSize
               OpDecorate %48 RelaxedPrecision
               OpDecorate %gl_SubgroupInvocationID RelaxedPrecision
               OpDecorate %gl_SubgroupInvocationID BuiltIn SubgroupLocalInvocationId
               OpDecorate %50 RelaxedPrecision
               OpDecorate %gl_NumSubgroups BuiltIn NumSubgroups
               OpDecorate %gl_SubgroupID BuiltIn SubgroupId
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
%_runtimearr_v4uint = OpTypeRuntimeArray %v4uint
     %Output = OpTypeStruct %_runtimearr_v4uint
%_ptr_StorageBuffer_Output = OpTypePointer StorageBuffer %Output
          %_ = OpVariable %_ptr_StorageBuffer_Output StorageBuffer
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%gl_SubgroupSize = OpVariable %_ptr_Input_uint Input
%gl_SubgroupInvocationID = OpVariable %_ptr_Input_uint Input
%gl_NumSubgroups = OpVariable %_ptr_Input_uint Input
%gl_SubgroupID = OpVariable %_ptr_Input_uint Input
%_ptr_StorageBuffer_v4uint = OpTypePointer StorageBuffer %v4uint
       %main = OpFunction %void None %3
          %5 = OpLabel
 %globalSize = OpVariable %_ptr_Function_v3uint Function
     %offset = OpVariable %_ptr_Function_uint Function
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
         %46 = OpLoad %uint %offset
         %48 = OpLoad %uint %gl_SubgroupSize
         %50 = OpLoad %uint %gl_SubgroupInvocationID
         %52 = OpLoad %uint %gl_NumSubgroups
         %54 = OpLoad %uint %gl_SubgroupID
         %55 = OpCompositeConstruct %v4uint %48 %50 %52 %54
         %57 = OpAccessChain %_ptr_StorageBuffer_v4uint %_ %int_0 %46
               OpStore %57 %55
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- Compute and mesh/task helpers use four workgroups by two by two and exercise local sizes including `1×1×1`, subgroup-sized dimensions, `32×4×1`, `1×4×32`, and `3×5×7`. Specialization constants select the local size.
- Each invocation writes one `uvec4` to the output SSBO. A shader-write-to-host-read barrier, queue completion, and allocation invalidation make the records visible before the callback scans them.
- Ordinary graphics and ray-tracing paths use per-stage output buffers. Framebuffer cases write `R32G32B32A32_UINT`, copy the attachment into a host-visible buffer, and run the check across several render widths.
- Required-size compute, mesh, and task cases create or select pipeline state for each supported power-of-two size. The case fails on the first size whose callback fails.
- Final pass/fail comes from the callback for the selected built-in. The harness reports failure when any iteration or required subgroup size violates that callback.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `subgroupsize` | Incorrect subgroup-size built-in value or required-subgroup-size application. |
| `subgroupinvocationid` | Out-of-range invocation index. |
| `numsubgroups` | Invalid workgroup subgroup-count built-in value. |
| `subgroupid` | Invalid subgroup index relative to the invocation's reported subgroup count. |

All values also depend on correct shader lowering, output addressing, pipeline execution, synchronization, and readback in the selected execution path.

### Cause Analysis

#### Incorrect subgroup-size built-in value or required-subgroup-size application

**Possible failure symptoms:** one or more records contain a first component different from the harness subgroup size, or a required-size iteration fails for a particular requested size.

**Possible implementation causes:** the implementation may expose the wrong `SubgroupSize` value, fail to apply `VkPipelineShaderStageRequiredSubgroupSizeCreateInfo`, or lower the built-in incorrectly for the selected shader stage. The specification requires `SubgroupSize` to be a power of two and to match `requiredSubgroupSize` when that state is used.

#### Out-of-range invocation index

**Possible failure symptoms:** a scanned output slot contains an invocation ID at least `subgroupSize`.

**Possible implementation causes:** `SubgroupLocalInvocationId` may be generated outside its specified range. Stage execution, output addressing, or result transport can also make a scanned slot contain an out-of-range value, but repeated in-range IDs and missing ID values alone do not fail this leaf.

#### Invalid workgroup subgroup-count built-in value

**Possible failure symptoms:** an invocation reports `NumSubgroups` greater than the local workgroup's total invocation count.

**Possible implementation causes:** the workgroup-level built-in may be lowered incorrectly, or the shader may record corrupted data. The callback checks only this upper bound, so a smaller but otherwise incorrect count can remain undetected by this leaf.

#### Invalid subgroup index relative to the invocation's reported subgroup count

**Possible failure symptoms:** a record has `SubgroupId >= NumSubgroups`.

**Possible implementation causes:** either workgroup-level built-in may be lowered or populated inconsistently. The specification requires `SubgroupId` to lie in `[0, NumSubgroups - 1]`.

#### Shared execution or result-transport failure

**Possible failure symptoms:** failures cluster by execution path or stage, multiple built-in leaves read corrupted records, or framebuffer/SSBO results remain at cleared values.

**Possible implementation causes:** shader compilation, pipeline execution, output indexing, stage-specific buffer or attachment writes, synchronization, image-to-buffer copy, or host visibility may be wrong. Source-level investigation is needed to distinguish these shared paths from a built-in semantic defect.

## Case Pruning

### Requirement-based pruning

- Subgroup support is required, and the selected stage must support subgroup operations. Lack of compute subgroup support is a conformance failure because compute support is mandatory; unsupported optional stages are skipped.
- `_requiredsubgroupsize` leaves require `VK_EXT_subgroup_size_control`, `subgroupSizeControl`, `computeFullSubgroups`, and support for required subgroup sizes in the selected stage.
- Ray-tracing cases require `VK_KHR_ray_tracing_pipeline`. Mesh/task cases require `VK_EXT_mesh_shader`, vertex-pipeline stores and atomics, and `taskShader` for task cases.
- Tessellation and geometry paths adapt point-size handling to device support. Portability-subset devices without tessellation isolines skip the affected stages.

### Design-based pruning

- `numsubgroups` and `subgroupid` are not registered for ordinary graphics, framebuffer, or ray-tracing paths because the built-ins are restricted to compute, mesh, and task execution models.
- Framebuffer cases cover only `subgroupsize` and `subgroupinvocationid`, since their checks fit the attachment transport and do not need workgroup built-ins.
- Vulkan SC registration excludes `ray_tracing` and `mesh`.
- Ordinary and required-size leaves share shader text; required subgroup size is a pipeline-state variation rather than a separate shader behavior.

## Key Takeaways

- The built-in value is the primary behavioral axis: each of the four leaves checks a different size or index invariant.
- One compute shader records all four values; case selection changes the host callback rather than the shader text.
- `subgroupinvocationid` checks each scanned value's range, not uniqueness or a dense set of IDs. `numsubgroups` checks an upper bound, not the exact subgroup count.
- Required-size cases repeat the invariant across every supported power-of-two subgroup size.
- See `## Failure Meaning` to distinguish a built-in semantic failure from shared execution, output, or readback faults.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `TestType` and check callbacks | [`vktSubgroupsBuiltinVarTests.cpp#L43-L304`](../../../modules/vulkan/subgroups/vktSubgroupsBuiltinVarTests.cpp#L43-L304) | Defines the four built-ins and exact host predicates. |
| `initFrameBufferPrograms` | [`vktSubgroupsBuiltinVarTests.cpp#L317-L962`](../../../modules/vulkan/subgroups/vktSubgroupsBuiltinVarTests.cpp#L317-L962) | Builds direct-SPIR-V framebuffer programs. |
| `initPrograms` | [`vktSubgroupsBuiltinVarTests.cpp#L983-L1628`](../../../modules/vulkan/subgroups/vktSubgroupsBuiltinVarTests.cpp#L983-L1628) | Builds the representative compute GLSL and routes other execution paths. |
| Support and execution | [`vktSubgroupsBuiltinVarTests.cpp#L1630-L1944`](../../../modules/vulkan/subgroups/vktSubgroupsBuiltinVarTests.cpp#L1630-L1944) | Applies feature gates and selects runtime/check helpers. |
| Registration | [`vktSubgroupsBuiltinVarTests.cpp#L1946-L2106`](../../../modules/vulkan/subgroups/vktSubgroupsBuiltinVarTests.cpp#L1946-L2106) | Defines the hierarchy, stages, leaves, and required-size variants. |
| Shared shader generation | [`vktSubgroupsTestsUtils.cpp#L1406-L1675`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L1406-L1675) | Expands mesh/task and ray-tracing GLSL. |
| Compute/mesh dispatch and readback | [`vktSubgroupsTestsUtils.cpp#L3985-L4131`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L3985-L4131) | Shows dispatch, barrier, invalidation, callback, and tested local sizes. |
| Framebuffer copyback and verdict | [`vktSubgroupsTestsUtils.cpp#L2430-L2637`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L2430-L2637) | Shows attachment execution, image copy, callback, and final result. |
| Registered mustpass leaves | [`subgroups.txt#L18502-L18537`](../../../mustpass/main/vk-default/subgroups.txt#L18502-L18537) | Confirms all executable `builtin_var` paths, including the representative case. |
| Vulkan built-in semantics | [`interfaces.adoc#L3891-L3916`](../../../../vulkan-docs/src/chapters/interfaces.adoc#L3891-L3916) | Defines `NumSubgroups`; `SubgroupId`, `SubgroupLocalInvocationId`, and `SubgroupSize` follow at lines 4955-5246. |
| Vulkan subgroup scope | [`shaders.adoc#L3219-L3247`](../../../../vulkan-docs/src/chapters/shaders.adoc#L3219-L3247) | Defines subgroup membership and scope. |
