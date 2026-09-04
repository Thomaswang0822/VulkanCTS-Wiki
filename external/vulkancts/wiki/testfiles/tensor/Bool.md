## Overview

**Core question:** Does shader boolean tensor access apply each registered logical operation to every `VK_FORMAT_R8_BOOL_ARM` element and preserve the result across tensor layouts?

- This page covers the `tensor.boolean` test family implemented by [vktTensorBool.cpp](../../../modules/vulkan/tensor/vktTensorBool.cpp#L370-L438).
- The family creates boolean tensors, reads one element per compute invocation, applies `AND`, `OR`, `NOT`, or `XOR`, and writes the result to a second tensor.
- The registered matrix uses four shapes, two boolean operands, four layout forms where the rank permits them, and all four operators. The default mustpass lists 112 boolean cases at [tensor.txt#L409-L520](../../../mustpass/main/vk-default/tensor.txt#L409-L520).
- The page explains the exact `tensor.boolean` registration position, generated shader coordinate mapping, tensor staging for optimal tiling, host-side comparison, support gates, pruning, and what a mismatch can and cannot identify.

## Background Knowledge

- A tensor view exposes a logical rank, shape, format, and tiling to shader tensor operations. The shader's `tensorARM<bool, rank>` declaration must agree with the tensor view's element type and rank; `tensorReadARM` and `tensorWriteARM` use an array of integer coordinates. See [Tensor Operations](../../../../vulkan-docs/src/chapters/VK_ARM_tensors/tensorops.adoc#tensors).
- Linear tensors can use explicit byte strides, while optimal tensors use implementation-defined storage. The test therefore uses a linear tensor as a staging object for optimal cases rather than making the shader depend on the optimal layout.
- A compute dispatch has one local invocation per workgroup here (`local_size_x = local_size_y = local_size_z = 1`). `gl_GlobalInvocationID.x` is consequently a flattened logical element index, which the generated shader converts back to rank-specific coordinates.

## Registration Hierarchy

```text
tensor.boolean
```

`tensor.boolean` is a direct child of the `tensor` test category, added by [createTests](../../../modules/vulkan/tensor/vktTensorTests.cpp#L37-L49). [createTensorBoolTests](../../../modules/vulkan/tensor/vktTensorBool.cpp#L432-L438) creates the `boolean` test family and [addTensorBoolTests](../../../modules/vulkan/tensor/vktTensorBool.cpp#L370-L430) adds executable cases directly; there are no registered intermediate nodes below `boolean`.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Format | `r8_bool` (`VK_FORMAT_R8_BOOL_ARM`) | Selects one-byte boolean tensor elements and the GLSL `bool` tensor type. | [format and element size](../../../modules/vulkan/tensor/vktTensorBool.cpp#L379-L380), [format name/type mapping](../../../modules/vulkan/tensor/vktTensorTestsUtil.cpp#L182-L210), [shader type mapping](../../../modules/vulkan/tensor/shaders/vktTensorShaderUtil.cpp#L39-L70) |
| Shape and rank | `shape_71693` (rank 1); `shape_263_269` (rank 2); `shape_37_43_47` (rank 3); `shape_13_17_19_23` (rank 4) | Sets the number of coordinates, tensor elements, and generated `tensorSizeARM`/coordinate statements. | [shape list and matrix loops](../../../modules/vulkan/tensor/vktTensorBool.cpp#L372-L397) |
| Layout | `linear` without strides; `linear` with packed strides; `linear` with non-packed strides; `optimal` | Selects implicit packed linear storage, explicit packed linear storage, padded linear storage, or optimal tiling with host staging. Explicit stride forms are registered only for ranks greater than 1. | [stride construction and case registration](../../../modules/vulkan/tensor/vktTensorBool.cpp#L382-L426) |
| Boolean operator | `and`, `or`, `not`, `xor` | Selects the logical operation emitted by `genShaderBooleanOp` and the matching host expectation. | [operator loop](../../../modules/vulkan/tensor/vktTensorBool.cpp#L394-L397), [shader operator selection](../../../modules/vulkan/tensor/shaders/vktTensorBooleanShader.cpp#L83-L100) |
| Applied operand | `apply_1`, `apply_0` | Supplies the constant right-hand operand for `AND`, `OR`, and `XOR`; `NOT` is still instantiated with both values even though the generated unary operation does not use it. | [test-value loop](../../../modules/vulkan/tensor/vktTensorBool.cpp#L394-L397), [case-name construction](../../../modules/vulkan/tensor/vktTensorBool.cpp#L308-L316) |

The exact registered naming pattern is `r8_bool_<tiling>_shape_<dimensions>[_strides_<strides>]_operator_<and|or|not|xor>_apply_<0|1>`. The rank-1 shape has `1 × 4 × 2 × 2 = 16` cases (one shape, four operators, two applied values, and two layouts: implicit packed linear and optimal). Each of the rank-2, rank-3, and rank-4 shapes has `1 × 4 × 2 × 4 = 32` cases because it also includes explicit packed and non-packed linear strides. Thus the matrix contains `16 + 3 × 32 = 112` cases. The default mustpass confirms the concrete expansion, including `strides_7429_437_23_1` and `strides_11862_697_36_1` for the rank-4 shape, at [tensor.txt#L409-L520](../../../mustpass/main/vk-default/tensor.txt#L409-L520).

## Behavior Parameters

The primary behavioral axis is the boolean operator. The shape and layout dimensions change coordinate and storage coverage, while the operator changes the value computed for every element.

### `and`: conjunction with the applied operand

The shader computes `tens_val && test_value`. With `apply_0`, every output must be false; with `apply_1`, the output must reproduce the input boolean. The host uses the same rule when constructing the expected result.

### `or`: disjunction with the applied operand

The shader computes `tens_val || test_value`. With `apply_1`, every output must be true; with `apply_0`, the output must reproduce the input boolean. This exercises the binary logical operation without changing the tensor coordinate path.

### `not`: unary inversion

The shader computes `!tens_val`. The case name still includes `apply_0` or `apply_1` because the registration loop instantiates both values, but `test_value` is not referenced by the generated `NOT` expression or by the host's `NOT` expectation.

### `xor`: exclusive disjunction with the applied operand

The shader computes `tens_val ^^ test_value`. `apply_0` preserves the input and `apply_1` inverts it, providing the two operand-sensitive outcomes for the XOR path.

## Shader Analysis

The shader generator emits rank-specialized GLSL for each test case. The walkthrough below uses a rank-1, implicit-packed, `AND`/`apply_1` case. It is intentionally small enough to show that the operation is a tensor read, a scalar boolean expression, and a tensor write; higher-rank cases repeat the dimension and coordinate logic for every rank dimension.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.tensor.boolean.r8_bool_linear_shape_71693_operator_and_apply_1
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `r8_bool` | The tensor format is `VK_FORMAT_R8_BOOL_ARM`; the generator maps it to GLSL `bool`. |
| `linear` with empty strides | The tensor uses the implicit packed linear form; no explicit stride suffix appears in the case name. |
| `shape_71693` | The tensor has rank 1 and 71,693 logical elements. |
| `operator_and_apply_1` | Each invocation reads one boolean and computes `tens_val && true`. |
| `local_size_x = local_size_y = local_size_z = 1` | One invocation handles one flattened element index. |

#### Purpose

This shader checks that a rank-1 boolean tensor can be read and written through the tensor shader interface while applying the generated `AND` operation. The host later compares every output element with the corresponding logical expression.

#### Structural Design

| Shader phase | Operation | Result |
|--------------|-----------|--------|
| Tensor declaration | Bind `tensorARM<bool, 1>` views at set 0, bindings 0 and 1. | Input and output have the same boolean element type and rank. |
| Dimension query | Evaluate `tensorSizeARM(tens, 0)`. | The shader uses the tensor's runtime size rather than hard-coding 71,693. |
| Coordinate construction | Divide the flattened `gl_GlobalInvocationID.x` by 1 and take modulo `size_d0`. | Each invocation obtains one valid rank-1 coordinate. |
| Tensor read | Call `tensorReadARM` with a one-element coordinate array containing `coord_0`. | One input `bool` is copied into `tens_val`. |
| Boolean operation | Evaluate `tens_val && true`. | `res` is the expected logical result for `apply_1`. |
| Tensor write | Call `tensorWriteARM` at the same coordinate. | The output tensor receives one result element. |

#### Shader Code

The following is the GLSL emitted by [genShaderBooleanOp](../../../modules/vulkan/tensor/shaders/vktTensorBooleanShader.cpp#L40-L112) for the representative path:

```glsl
#version 450
#extension GL_ARM_tensors : require
#extension GL_EXT_shader_explicit_arithmetic_types : require
layout(local_size_x = 1, local_size_y = 1, local_size_z = 1) in;
layout(set=0, binding = 0) uniform tensorARM<bool, 1> tens;
layout(set=0, binding = 1) uniform tensorARM<bool, 1> tens_out;
void main()
{
    const uint size_d0 = tensorSizeARM(tens, 0);
    const uint coord_0 = gl_GlobalInvocationID.x / (1) % size_d0;
    bool tens_val;
    tensorReadARM(tens, uint&#91;&#93;(coord_0), tens_val);
    bool res = tens_val && true;
    tensorWriteARM(tens_out, uint&#91;&#93;(coord_0), res);
}
```

#### Additional Info

- The source emits one `tensorSizeARM` query and one coordinate expression per rank dimension [vktTensorBooleanShader.cpp#L56-L70](../../../modules/vulkan/tensor/shaders/vktTensorBooleanShader.cpp#L56-L70).
- The generated shader always uses `tensorReadARM` into a scalar `bool`, applies one of the four source-selected expressions, and writes the scalar with `tensorWriteARM` [vktTensorBooleanShader.cpp#L73-L108](../../../modules/vulkan/tensor/shaders/vktTensorBooleanShader.cpp#L73-L108).
- The shader does not branch on `test_value` at runtime: the host generator inserts the literal `true` or `false` into the source [vktTensorBooleanShader.cpp#L83-L96](../../../modules/vulkan/tensor/shaders/vktTensorBooleanShader.cpp#L83-L96).
- For rank 4, the same generator emits four dimension queries and four coordinate expressions. It does not emit a separate shader algorithm for packed, non-packed, or optimal storage; those differences are in tensor creation and host transfer.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Rank/shape | Changes the second `tensorARM` type argument, the number of `tensorSizeARM` statements, and the coordinate expressions. | [rank-specialized generator](../../../modules/vulkan/tensor/shaders/vktTensorBooleanShader.cpp#L50-L70) |
| Boolean operator | Selects `!tens_val`, `tens_val && literal`, `tens_val || literal`, or `tens_val ^^ literal`. | [operator switch](../../../modules/vulkan/tensor/shaders/vktTensorBooleanShader.cpp#L83-L100) |
| Applied operand | Changes the binary-operation literal to `true` or `false`; it has no shader effect for `NOT`. | [literal emission](../../../modules/vulkan/tensor/shaders/vktTensorBooleanShader.cpp#L89-L96) |
| Format | Remains `bool` for every boolean case because registration fixes `VK_FORMAT_R8_BOOL_ARM`; the format mapping supplies that type. | [fixed format](../../../modules/vulkan/tensor/vktTensorBool.cpp#L379-L380), [format mapping](../../../modules/vulkan/tensor/shaders/vktTensorShaderUtil.cpp#L64-L70) |
| Layout and strides | Do not change the generated GLSL. They change tensor descriptions and, for optimal tiling, the host's staging copies. | [tensor description](../../../modules/vulkan/tensor/vktTensorBool.cpp#L88-L115), [optimal transfer path](../../../modules/vulkan/tensor/vktTensorBool.cpp#L181-L243) |

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
; Bound: 44
; Schema: 0
               OpCapability Shader
               OpCapability TensorsARM
               OpExtension "SPV_ARM_tensors"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_GlobalInvocationID
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpSourceExtension "GL_ARM_tensors"
               OpSourceExtension "GL_EXT_shader_explicit_arithmetic_types"
               OpName %main "main"
               OpName %size_d0 "size_d0"
               OpName %tens "tens"
               OpName %coord_0 "coord_0"
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
               OpName %tens_val "tens_val"
               OpName %res "res"
               OpName %tens_out "tens_out"
               OpDecorate %tens Binding 0
               OpDecorate %tens DescriptorSet 0
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %tens_out Binding 1
               OpDecorate %tens_out DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
       %bool = OpTypeBool
     %uint_1 = OpConstant %uint 1
         %11 = OpTypeTensorARM %bool %uint_1
%_ptr_UniformConstant_11 = OpTypePointer UniformConstant %11
       %tens = OpVariable %_ptr_UniformConstant_11 UniformConstant
     %uint_0 = OpConstant %uint 0
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
%_ptr_Input_uint = OpTypePointer Input %uint
%_arr_uint_uint_1 = OpTypeArray %uint %uint_1
%_ptr_Function_bool = OpTypePointer Function %bool
       %true = OpConstantTrue %bool
   %tens_out = OpVariable %_ptr_UniformConstant_11 UniformConstant
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
    %size_d0 = OpVariable %_ptr_Function_uint Function
    %coord_0 = OpVariable %_ptr_Function_uint Function
   %tens_val = OpVariable %_ptr_Function_bool Function
        %res = OpVariable %_ptr_Function_bool Function
         %14 = OpLoad %11 %tens
         %16 = OpTensorQuerySizeARM %uint %14 %uint_0
               OpStore %size_d0 %16
         %22 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %23 = OpLoad %uint %22
         %24 = OpUDiv %uint %23 %uint_1
         %25 = OpLoad %uint %size_d0
         %26 = OpUMod %uint %24 %25
               OpStore %coord_0 %26
         %27 = OpLoad %11 %tens
         %28 = OpLoad %uint %coord_0
         %30 = OpCompositeConstruct %_arr_uint_uint_1 %28
         %33 = OpTensorReadARM %bool %27 %30
               OpStore %tens_val %33
         %35 = OpLoad %bool %tens_val
         %37 = OpLogicalAnd %bool %35 %true
               OpStore %res %37
         %39 = OpLoad %11 %tens_out
         %40 = OpLoad %uint %coord_0
         %41 = OpCompositeConstruct %_arr_uint_uint_1 %40
         %42 = OpLoad %bool %res
               OpTensorWriteARM %39 %41 %42
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- For each case, `iterate` multiplies the shape dimensions to obtain the element count and creates input and output tensor descriptions with the selected format, tiling, strides, and `VK_TENSOR_USAGE_SHADER_BIT_ARM | VK_TENSOR_USAGE_TRANSFER_SRC_BIT_ARM | VK_TENSOR_USAGE_TRANSFER_DST_BIT_ARM` [vktTensorBool.cpp#L88-L101](../../../modules/vulkan/tensor/vktTensorBool.cpp#L88-L101).
- It fills `initialTensorData` using the selected dimensions and strides. Linear cases upload that data to the input tensor and clear the output tensor. Optimal cases instead upload to a linear staging tensor; the command buffer later copies that tensor into the optimal input tensor [vktTensorBool.cpp#L103-L131](../../../modules/vulkan/tensor/vktTensorBool.cpp#L103-L131).
- The descriptor set has two `VK_DESCRIPTOR_TYPE_TENSOR_ARM` compute bindings: binding 0 is the input view and binding 1 is the output view [vktTensorBool.cpp#L133-L162](../../../modules/vulkan/tensor/vktTensorBool.cpp#L133-L162).
- The generated `comp` source is compiled into a compute shader module and dispatched with `elements, 1, 1`, so the total number of invocations equals the product of the tensor dimensions [vktTensorBool.cpp#L164-L209](../../../modules/vulkan/tensor/vktTensorBool.cpp#L164-L209).
- Optimal cases place a transfer-to-compute tensor barrier before the dispatch, then a compute-to-transfer barrier and a tensor copy for readback. A final compute-to-host tensor barrier makes the selected result tensor visible to the host [vktTensorBool.cpp#L181-L243](../../../modules/vulkan/tensor/vktTensorBool.cpp#L181-L243).
- After submission and completion, the host downloads either `tensorOut` for linear cases or the linear staging tensor for optimal cases. It computes the expected boolean independently for each element and fails at the first mismatch with `Comparison failed at index <n>: expected = <0|1>, buffer = <value>`; a complete match returns `Tensor test succeeded` [vktTensorBool.cpp#L248-L305](../../../modules/vulkan/tensor/vktTensorBool.cpp#L248-L305).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `and` | Boolean tensor read, logical conjunction lowering, coordinate calculation, tensor write, or input/output transfer path |
| `or` | Boolean tensor read, logical disjunction lowering, coordinate calculation, tensor write, or input/output transfer path |
| `not` | Boolean tensor read, unary inversion lowering, coordinate calculation, tensor write, or input/output transfer path |
| `xor` | Boolean tensor read, exclusive-or lowering, coordinate calculation, tensor write, or input/output transfer path |

All operator values share the same format, descriptor, synchronization, and first-mismatch reporting infrastructure. A failure at a support check is `NotSupported`, not an operator-result failure.

### Cause Analysis

#### Boolean tensor access and operation lowering

**Possible failure symptoms:** An executed case reports the first index whose downloaded output does not equal the host-computed logical result. `and` and `or` failures can appear as incorrect constant propagation, while `not` and `xor` failures can appear as an inversion or exclusive-or mismatch; the index alone does not identify the implementation layer.

**Possible implementation causes:** The shader compiler or implementation may lower `OpTensorReadARM`, the boolean logical instruction, or `OpTensorWriteARM` incorrectly, or may associate the tensor view's boolean format with the wrong shader element representation. The source establishes the generated operation and comparison rule but does not establish a specific driver, hardware, or compiler defect, so that distinction requires further implementation investigation.

#### Coordinate and stride handling

**Possible failure symptoms:** The first mismatch clusters at a row, slice, or higher-dimensional boundary, or is consistently associated with explicit stride cases while implicit packed cases pass. A valid logical operation can therefore still report a wrong value if the read and write coordinates do not address the intended element.

**Possible implementation causes:** The generated coordinate reconstruction uses runtime dimension sizes and flattened invocation IDs; an implementation or compiler problem in coordinate calculation, tensor view interpretation, or explicit non-packed stride handling could select a different element. The test source does not prove which layer caused such a pattern.

#### Optimal staging and host result transport

**Possible failure symptoms:** An optimal case can fail after the shader result is written, with the host observing stale or incorrectly copied data in the downloaded linear staging tensor. The comparison reports the same first-mismatch format as a shader error.

**Possible implementation causes:** The optimal path includes a linear-to-optimal initialization copy, a transfer-to-compute tensor barrier, a compute-to-transfer barrier, an optimal-to-linear copy, and a compute-to-host barrier. A defect in tensor copy, synchronization, memory visibility, or host download can produce the observed mismatch; the page cannot assign it to a shader without isolating the path.

## Case Pruning

### Requirement-based pruning

- Every executable case requires the `VK_ARM_tensors` device functionality [checkSupport](../../../modules/vulkan/tensor/vktTensorBool.cpp#L325-L328).
- A case is reported as `NotSupported` when its rank exceeds `maxTensorDimensionCount`, shader tensor access is unavailable, compute-stage tensor access is unavailable, or the selected format/tiling lacks `VK_FORMAT_FEATURE_2_TENSOR_SHADER_BIT_ARM` support [vktTensorBool.cpp#L329-L348](../../../modules/vulkan/tensor/vktTensorBool.cpp#L329-L348).
- Explicit non-packed linear cases are also reported as `NotSupported` when the device does not support non-packed tensors [vktTensorBool.cpp#L350-L353](../../../modules/vulkan/tensor/vktTensorBool.cpp#L350-L353). This gate applies to the generated non-packed stride cases; packed and optimal parameter objects use empty strides and are considered packed by `TensorParameters::packed` [TensorParameters](../../../modules/vulkan/tensor/vktTensorTestsUtil.hpp#L68-L101).
- A support rejection happens before shader creation and dispatch. It means the selected requirement is not available on the current implementation, not that the boolean operation produced a wrong result.

### Design-based pruning

- The matrix fixes the format to `VK_FORMAT_R8_BOOL_ARM` because this page tests boolean tensor operations rather than cross-format behavior [vktTensorBool.cpp#L379-L380].
- It uses exactly four shapes: one rank-1 shape and three shapes with ranks 2 through 4. Explicit packed and non-packed stride cases are omitted for rank 1 by the `if (rank > 1)` guards [vktTensorBool.cpp#L372-L391](../../../modules/vulkan/tensor/vktTensorBool.cpp#L372-L391).
- For ranks greater than 1, the stride matrix intentionally contains the implicit packed form, explicit packed strides, explicit padded strides, and optimal tiling. The two explicit stride vectors are produced once per shape and reused for every operator/value pair [vktTensorBool.cpp#L382-L426](../../../modules/vulkan/tensor/vktTensorBool.cpp#L382-L426).
- `NOT` is registered for both `apply_0` and `apply_1` to keep the operator/value matrix uniform, although the applied value is semantically unused by the unary shader expression [vktTensorBool.cpp#L394-L397](../../../modules/vulkan/tensor/vktTensorBool.cpp#L83-L96).

## Key Takeaways

- The complete default registration is the direct `tensor.boolean` family with 112 leaves: four shapes, four logical operators, two applied values, and two or four layout forms depending on rank.
- The shader performs a scalar boolean operation between one tensor read and one tensor write; layout and explicit stride variation is exercised by host tensor setup, not by shader branches.
- `NOT` ignores the registered applied value, whereas `AND`, `OR`, and `XOR` embed it as a literal in the generated shader.
- A passing case means every logical element matched after the relevant linear or optimal readback path. A failing index identifies the first observed mismatch, not a unique fault location.
- `NotSupported` from the device-functionality, rank, shader-access, format-feature, or non-packed gates is a pruned case, not evidence of an incorrect boolean result.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Tensor category registration | [createTests](../../../modules/vulkan/tensor/vktTensorTests.cpp#L37-L49) | Adds the `boolean` test family below the `tensor` category. |
| Boolean family registration | [createTensorBoolTests](../../../modules/vulkan/tensor/vktTensorBool.cpp#L370-L438) | Creates the exact `boolean` group and its generated cases. |
| Boolean case matrix | [addTensorBoolTests](../../../modules/vulkan/tensor/vktTensorBool.cpp#L370-L430) | Defines shapes, strides, tilings, operators, applied values, and rank-based layout guards. |
| Support gates | [TensorBooleanOpTestCase::checkSupport](../../../modules/vulkan/tensor/vktTensorBool.cpp#L325-L354) | Maps extension, rank, shader-stage, format, and non-packed requirements to `NotSupported`. |
| Runtime and comparison | [TensorBooleanOpTestInstance::iterate](../../../modules/vulkan/tensor/vktTensorBool.cpp#L80-L305) | Creates tensors, dispatches the shader, performs barriers/copies, downloads results, and reports pass/fail. |
| Boolean shader generator | [genShaderBooleanOp](../../../modules/vulkan/tensor/shaders/vktTensorBooleanShader.cpp#L40-L112) | Emits rank-specific tensor declarations, coordinate mapping, logical expression, and tensor write. |
| Boolean format mapping | [getTensorFormat](../../../modules/vulkan/tensor/shaders/vktTensorShaderUtil.cpp#L39-L70) | Maps `VK_FORMAT_R8_BOOL_ARM` to GLSL `bool`. |
| Tensor parameter semantics | [TensorParameters](../../../modules/vulkan/tensor/vktTensorTestsUtil.hpp#L68-L101) | Defines rank, element count, host size, and packed detection. |
| Tensor operation rules | [Tensor Operations](../../../../vulkan-docs/src/chapters/VK_ARM_tensors/tensorops.adoc#tensors) | Defines the shader tensor coordinate, read, and write model used by the test. |
| Registered leaves | [tensor.txt#L409-L520](../../../mustpass/main/vk-default/tensor.txt#L409-L520) | Confirms the 112 concrete `tensor.boolean` cases in the default mustpass. |
