## Overview

**Core question:** Does `tensorSizeARM` return each dimension recorded in the bound tensor descriptor?

- This page covers the `tensor.dimension_query` test family created by [createDimensionQueryTests](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp#L293-L300).
- The family creates rank-1 through rank-5 tensors, queries every dimension in a one-invocation compute shader, and compares the returned `uint` values with the tensor dimensions supplied at creation.
- The registered matrix crosses five shapes, eight integer formats, and both `VK_TENSOR_TILING_LINEAR_ARM` and `VK_TENSOR_TILING_OPTIMAL_ARM`. The default mustpass contains the resulting 80 cases at [tensor.txt#L761-L840](../../../mustpass/main/vk-default/tensor.txt#L761-L840).
- The page explains the generated `tensorSizeARM` shader, compute-stage support gates, descriptor and output-buffer setup, host readback, result checking, and the cases that the test prunes before execution.

## Background Knowledge

- **Tensor rank and shape.** Rank is the number of tensor dimensions. The shape stores the size of each dimension in index order, so shape `{2, 1}` has dimension 0 of size 2 and dimension 1 of size 1. The shader's tensor type rank and the created tensor's dimension count must agree.
- **Tensor query semantics.** `tensorSizeARM` maps to the SPIR-V `OpTensorQuerySizeARM` operation. The operation queries the size of the tensor descriptor that a shader tensor operation would access; it does not read tensor element contents. The specification describes this operation in [tensorops.adoc#L231-L239](../../../../vulkan-docs/src/chapters/VK_ARM_tensors/tensorops.adoc#L231-L239).

## Registration Hierarchy

```text
tensor.dimension_query
```

The `dimension_query` test family has no registered intermediate nodes. Its executable cases are generated directly from format, shape, and tiling values by [addDimensionQueriesTestCases](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp#L275-L289).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Format | `VK_FORMAT_R8_UINT`, `VK_FORMAT_R8_SINT`, `VK_FORMAT_R16_UINT`, `VK_FORMAT_R16_SINT`, `VK_FORMAT_R32_UINT`, `VK_FORMAT_R32_SINT`, `VK_FORMAT_R64_UINT`, `VK_FORMAT_R64_SINT` | Selects the tensor element type in the generated `tensorARM<...>` declaration and the tensor description. | [getAllTestFormats](../../../modules/vulkan/tensor/vktTensorTestsUtil.cpp#L48-L56), [shader declaration](../../../modules/vulkan/tensor/shaders/vktTensorQueryDimensionsShaders.cpp#L49-L51) |
| Tiling | `VK_TENSOR_TILING_LINEAR_ARM`, `VK_TENSOR_TILING_OPTIMAL_ARM` | Selects the tensor layout passed to `makeTensorDescription`; linear cases also compute strides before creation. | [constructor and tensor description](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp#L67-L81), [tensor creation](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp#L100-L106) |
| Shape and rank | `{1}`; `{2, 1}`; `{4, 2, 1}`; `{8, 4, 2, 1}`; `{4, 8, 16, 2, 1}` | Sets `dimensionCount`, supplies the expected dimension sequence, and controls how many `tensorSizeARM` statements the generator emits. | [test dimensions](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp#L275-L287), [generator loop](../../../modules/vulkan/tensor/shaders/vktTensorQueryDimensionsShaders.cpp#L57-L60) |
| Output-buffer length | `rank` `uint32_t` elements | Gives the shader one result slot for each queried dimension. | [buffer sizing](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp#L108-L123) |

The five shape values produce ranks 1, 2, 3, 4, and 5. Each shape is paired with each format and each tiling, yielding `5 × 8 × 2 = 80` generated cases in the default mustpass.

## Behavior Parameters

The primary behavioral axis is the tensor shape and rank. It determines how many descriptor dimensions the shader queries and how many host results must match.

### `shape_1`: rank 1

The tensor has one dimension of size 1. The shader emits `data[0] = tensorSizeARM(tens, 0)`, and the host checks one result.

### `shape_2_1`: rank 2

The tensor has dimensions 2 and 1. The shader queries indices 0 and 1, preserving the order supplied to `VkTensorDescriptionARM::pDimensions`.

### `shape_4_2_1`: rank 3

The tensor has dimensions 4, 2, and 1. Three query results test indexing across a rank-3 descriptor.

### `shape_8_4_2_1`: rank 4

The tensor has dimensions 8, 4, 2, and 1. Four query results exercise the rank-4 form of the tensor shader type.

### `shape_4_8_16_2_1`: rank 5

The tensor has dimensions 4, 8, 16, 2, and 1. Five query results exercise the highest rank used by this family and the final dimension index 4.

## Shader Analysis

The representative case below uses rank 2 so both a non-final dimension and the final dimension appear in the generated code. The format and tiling variants change the tensor declaration or tensor creation, but the query loop and result transport remain the same.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.tensor.dimension_query.r32_uint_linear_shape_2_1
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `VK_FORMAT_R32_UINT` | Makes the shader tensor element type `uint`, matching the 32-bit unsigned tensor format. |
| `VK_TENSOR_TILING_LINEAR_ARM` | Selects linear tensor creation; the host computes linear strides before building the tensor description. |
| `{2, 1}` | Selects rank 2 and makes the expected query result sequence `[2, 1]`. |
| `local_size_x = local_size_y = local_size_z = 1` | Runs one compute invocation, which writes both dimension results. |

#### Purpose

This shader queries the two sizes stored in the bound rank-2 tensor descriptor and writes them to a storage buffer. The host later requires the buffer to contain `2, 1` in that order.

#### Structural Design

| Phase | Shader operation | Observable result |
|-------|------------------|-------------------|
| Declaration | Bind `tensorARM<uint, 2>` at set 0, binding 0 and a `uint` runtime array at binding 1. | The shader type rank matches the created tensor rank. |
| Query 0 | Evaluate `tensorSizeARM(tens, 0)`. | Dimension 0 is written to `data[0]`. |
| Query 1 | Evaluate `tensorSizeARM(tens, 1)`. | Dimension 1 is written to `data[1]`. |
| Host check | Read the two `uint32_t` slots after the compute submission completes. | Expected values are 2 and 1. |

#### Shader Code

The following is the GLSL emitted by `genShaderQueryDimensions(2, VK_FORMAT_R32_UINT)` for this representative path:

```glsl
#version 450
#extension GL_ARM_tensors : require
#extension GL_EXT_shader_explicit_arithmetic_types : require

layout(local_size_x = 1, local_size_y = 1, local_size_z = 1) in;
/// Binding 0 carries the rank-2 tensor view whose descriptor dimensions are queried.
layout(set=0, binding=0) uniform tensorARM<uint, 2> tens;
/// Binding 1 receives one uint result for each tensor dimension.
layout(set=0, binding=1, std430) buffer _buff { uint data[]; };

void main()
{
    /// Query dimension 0 and store the descriptor-reported size in the first result slot.
    data[0] = tensorSizeARM(tens, 0);
    /// Query dimension 1 and store the descriptor-reported size in the second result slot.
    data[1] = tensorSizeARM(tens, 1);
}
```

#### Additional Info

- The generator uses `getTensorFormat(tensorFormat)` for the tensor element type and uses the input rank as the second `tensorARM` type argument [vktTensorQueryDimensionsShaders.cpp#L40-L51](../../../modules/vulkan/tensor/shaders/vktTensorQueryDimensionsShaders.cpp#L40-L51).
- The loop emits exactly one statement for each index in `[0, rank)`, so this case has no tensor element-coordinate calculation [vktTensorQueryDimensionsShaders.cpp#L57-L60](../../../modules/vulkan/tensor/shaders/vktTensorQueryDimensionsShaders.cpp#L57-L60).
- The source collection adds the generated text as the `comp` program, which the test turns into a compute shader module [vktTensorDimensionQuery.cpp#L263-L267](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp#L263-L267).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Format | The tensor element type in `tensorARM<...>` changes with the selected integer format; the query statements still write `uint` sizes to the output buffer. | [format mapping and declaration](../../../modules/vulkan/tensor/shaders/vktTensorQueryDimensionsShaders.cpp#L40-L51) |
| Rank/shape | The tensor type rank and the number of `tensorSizeARM` statements change with `m_dimension.size()`. | [generator rank and loop](../../../modules/vulkan/tensor/shaders/vktTensorQueryDimensionsShaders.cpp#L49-L60) |
| Tiling | Tiling changes host tensor creation and, for linear tiling, stride setup; it does not add a shader branch. | [tensor setup](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp#L67-L106) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed GLSL from this walkthrough
- Stage: `comp`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 29
; Schema: 0
               OpCapability Shader
               OpCapability TensorsARM
               OpExtension "SPV_ARM_tensors"
               OpExtension "SPV_KHR_storage_buffer_storage_class"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main"
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpSourceExtension "GL_ARM_tensors"
               OpSourceExtension "GL_EXT_shader_explicit_arithmetic_types"
               OpName %main "main"
               OpName %_buff "_buff"
               OpMemberName %_buff 0 "data"
               OpName %_ ""
               OpName %tens "tens"
               OpDecorate %_runtimearr_uint ArrayStride 4
               OpDecorate %_buff Block
               OpMemberDecorate %_buff 0 Offset 0
               OpDecorate %_ Binding 1
               OpDecorate %_ DescriptorSet 0
               OpDecorate %tens Binding 0
               OpDecorate %tens DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_runtimearr_uint = OpTypeRuntimeArray %uint
      %_buff = OpTypeStruct %_runtimearr_uint
%_ptr_StorageBuffer__buff = OpTypePointer StorageBuffer %_buff
          %_ = OpVariable %_ptr_StorageBuffer__buff StorageBuffer
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
     %uint_2 = OpConstant %uint 2
         %14 = OpTypeTensorARM %uint %uint_2
%_ptr_UniformConstant_14 = OpTypePointer UniformConstant %14
       %tens = OpVariable %_ptr_UniformConstant_14 UniformConstant
     %uint_0 = OpConstant %uint 0
%_ptr_StorageBuffer_uint = OpTypePointer StorageBuffer %uint
      %int_1 = OpConstant %int 1
     %uint_1 = OpConstant %uint 1
     %v3uint = OpTypeVector %uint 3
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
         %17 = OpLoad %14 %tens
         %19 = OpTensorQuerySizeARM %uint %17 %uint_0
         %21 = OpAccessChain %_ptr_StorageBuffer_uint %_ %int_0 %int_0
               OpStore %21 %19
         %23 = OpLoad %14 %tens
         %25 = OpTensorQuerySizeARM %uint %23 %uint_1
         %26 = OpAccessChain %_ptr_StorageBuffer_uint %_ %int_0 %int_1
               OpStore %26 %25
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The test builds a `VkTensorDescriptionARM` with the selected tiling, format, dimensions, computed linear strides when applicable, and `VK_TENSOR_USAGE_SHADER_BIT_ARM`; it then creates a `TensorWithMemory` and a tensor view [vktTensorDimensionQuery.cpp#L100-L106](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp#L100-L106).
- It allocates a host-visible storage buffer sized as `rank * sizeof(uint32_t)`, clears its slots, and flushes the allocation before device use [vktTensorDimensionQuery.cpp#L108-L123](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp#L108-L123).
- Descriptor binding 0 contains the `VK_DESCRIPTOR_TYPE_TENSOR_ARM` tensor view. Binding 1 contains the `VK_DESCRIPTOR_TYPE_STORAGE_BUFFER` result buffer. Both bindings are visible to the compute stage [vktTensorDimensionQuery.cpp#L125-L153](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp#L125-L153).
- The test creates a compute pipeline from the generated `comp` module, binds the descriptor set, and dispatches exactly `1, 1, 1`. The single invocation executes every generated query statement [vktTensorDimensionQuery.cpp#L155-L184](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp#L155-L184).
- A buffer barrier changes visibility from `VK_ACCESS_SHADER_WRITE_BIT` at `VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT` to `VK_ACCESS_HOST_READ_BIT` at `VK_PIPELINE_STAGE_HOST_BIT`. The test submits the command buffer and waits before reading [vktTensorDimensionQuery.cpp#L178-L193](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp#L178-L193).
- The host invalidates the allocation, scans every result slot, and compares it with the corresponding `m_dimensions` entry. The first mismatch returns failure with its index, expected value, and actual buffer value; a complete match returns `pass("Tensor test succeeded")` [vktTensorDimensionQuery.cpp#L196-L218](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp#L196-L218).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `shape_1` | Rank-1 tensor query or dimension-0 descriptor metadata handling. |
| `shape_2_1` | Rank-2 query indexing or shape propagation for dimensions 0 and 1. |
| `shape_4_2_1` | Rank-3 query indexing or shape propagation for dimensions 0 through 2. |
| `shape_8_4_2_1` | Rank-4 query indexing or shape propagation for dimensions 0 through 3. |
| `shape_4_8_16_2_1` | Rank-5 support, query indexing, or propagation of the final dimension. |

### Cause Analysis

#### Rank-1 tensor query or dimension-0 descriptor metadata handling

**Possible failure symptoms:** The one output slot differs from the expected value 1, and the failure reports index 0.

**Possible implementation causes:** The failure can arise from incorrect handling of the rank-1 tensor descriptor or from lowering `OpTensorQuerySizeARM` for dimension index 0. The source confirms the test's rank and expected value, but it does not identify a particular driver or hardware cause; that requires implementation-level investigation.

#### Rank-2 query indexing or shape propagation for dimensions 0 and 1

**Possible failure symptoms:** One of the two output slots differs from 2 or 1. The reported index distinguishes the first dimension from the final dimension.

**Possible implementation causes:** The result points to query-index handling or propagation of the two `pDimensions` values into the tensor descriptor and shader-visible tensor type. A mismatch may also expose incorrect handling of the rank-2 tensor type. The CTS source does not establish which implementation layer is responsible.

#### Rank-3 query indexing or shape propagation for dimensions 0 through 2

**Possible failure symptoms:** The host reports a mismatch at index 0, 1, or 2 against the expected sequence 4, 2, 1.

**Possible implementation causes:** The failure is consistent with an error in rank-3 metadata propagation or in one of the three query indices. The source provides no evidence to separate descriptor creation, shader compilation, and execution, so further implementation investigation is needed.

#### Rank-4 query indexing or shape propagation for dimensions 0 through 3

**Possible failure symptoms:** At least one of the four slots fails against 8, 4, 2, or 1, and the failure identifies the first bad index encountered by the host loop.

**Possible implementation causes:** The implementation may mishandle the rank-4 tensor type, a dimension index, or the corresponding descriptor metadata. This page does not assign the cause to hardware, driver, compiler, or host code without evidence.

#### Rank-5 support, query indexing, or propagation of the final dimension

**Possible failure symptoms:** One of five slots fails against 4, 8, 16, 2, or 1. A failure at index 4 isolates the final dimension query; an earlier index indicates a broader rank-5 result problem.

**Possible implementation causes:** The failure can indicate incorrect rank-5 support, query indexing, or descriptor shape propagation. The test's support gate removes devices whose reported maximum rank is below 5, so an executed failure concerns behavior after that gate rather than an unsupported rank being treated as a normal result.

Format and tiling are crossed with every shape. A failure restricted to one format or tiling can point to format/tiling tensor support or tensor-view creation behavior, while a failure across all combinations points more broadly to query or metadata handling. The available source does not prove a more specific implementation cause.

## Case Pruning

### Requirement-based pruning

- The test requires the `VK_ARM_tensors` device functionality [vktTensorDimensionQuery.cpp#L238-L241](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp#L238-L241).
- It skips a case when the selected rank exceeds `maxTensorDimensionCount` [vktTensorDimensionQuery.cpp#L242-L245](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp#L242-L245).
- It requires the `shaderTensorAccess` feature and compute-stage support in `shaderTensorSupportedStages` [vktTensorDimensionQuery.cpp#L247-L255](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp#L247-L255).
- It requires the selected format and tiling to advertise `VK_FORMAT_FEATURE_2_TENSOR_SHADER_BIT_ARM` [vktTensorDimensionQuery.cpp#L257-L260](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp#L257-L260). The helper checks the corresponding optimal- or linear-tiling tensor feature flags [vktTensorTestsUtil.cpp#L341-L363](../../../modules/vulkan/tensor/vktTensorTestsUtil.cpp#L341-L363).

These checks remove cases that the current implementation cannot legally or meaningfully execute. They are support skips, not passing results.

### Design-based pruning

- The family uses the fixed shapes `{1}`, `{2, 1}`, `{4, 2, 1}`, `{8, 4, 2, 1}`, and `{4, 8, 16, 2, 1}` rather than generating arbitrary dimension values [vktTensorDimensionQuery.cpp#L275-L278](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp#L275-L278).
- It tests both supported tensor tilings and all eight integer formats returned by `getAllTestFormats`, but it does not add non-packed stride variants, tensor element initialization, or non-compute shader stages. Those omissions follow the query test's purpose: the generated shader reads descriptor sizes and writes them to a buffer.
- The dispatch is fixed at one workgroup of one invocation because the shader has no per-element workload. The invocation writes all rank results sequentially, so additional invocations would duplicate the same query work rather than test another behavior [vktTensorQueryDimensionsShaders.cpp#L49-L60](../../../modules/vulkan/tensor/shaders/vktTensorQueryDimensionsShaders.cpp#L49-L60).

## Key Takeaways

- `tensorSizeARM(tens, i)` is checked against the same dimension sequence used to create the tensor, in the same index order.
- Rank controls both the tensor type's dimension count and the number of output-buffer values; the selected cases cover ranks 1 through 5.
- The query shader does not need tensor element data. It needs a compatible tensor view, a compute-stage tensor-access feature, and a storage buffer for the returned sizes.
- The host makes shader writes visible before invalidating and checking the buffer, and it reports the first mismatching dimension with expected and observed values.
- Format and tiling surround the rank/shape behavior in the matrix. The test skips a case when the extension, rank limit, compute-stage support, or selected format/tiling tensor-shader feature is unavailable.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `createTests` | [vktTensorTests.cpp#L37-L49](../../../modules/vulkan/tensor/vktTensorTests.cpp#L37-L49) | Adds `dimension_query` as a direct child of the `tensor` test category. |
| `createDimensionQueryTests` | [vktTensorDimensionQuery.cpp#L293-L300](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp#L293-L300) | Registers the `dimension_query` test family. |
| `addDimensionQueriesTestCases` | [vktTensorDimensionQuery.cpp#L275-L289](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp#L275-L289) | Defines the complete shape, format, and tiling matrix. |
| `genShaderQueryDimensions` | [vktTensorQueryDimensionsShaders.cpp#L40-L65](../../../modules/vulkan/tensor/shaders/vktTensorQueryDimensionsShaders.cpp#L40-L65) | Generates the rank-specific compute GLSL. |
| `TensorDimensionQueriesTestCase::checkSupport` | [vktTensorDimensionQuery.cpp#L238-L261](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp#L238-L261) | Implements extension, rank, feature, stage, and format/tiling gates. |
| `TensorDimensionsQueriesTestInstance::iterate` | [vktTensorDimensionQuery.cpp#L92-L218](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp#L92-L218) | Creates resources, dispatches the shader, synchronizes, reads back, and checks results. |
| `getAllTestFormats` | [vktTensorTestsUtil.cpp#L48-L56](../../../modules/vulkan/tensor/vktTensorTestsUtil.cpp#L48-L56) | Supplies the eight formats crossed with each shape and tiling. |
| Tensor query specification | [tensorops.adoc#L231-L239](../../../../vulkan-docs/src/chapters/VK_ARM_tensors/tensorops.adoc#L231-L239) | Defines the semantics of `OpTensorQuerySizeARM`. |
| Default mustpass | [tensor.txt#L761-L840](../../../mustpass/main/vk-default/tensor.txt#L761-L840) | Lists the 80 dimension-query cases. |
