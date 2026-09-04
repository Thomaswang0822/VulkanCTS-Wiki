## Overview

**Core question:** Does shader array access move the right consecutive tensor elements for every registered integer format, tiling, rank, and array length?

- This page covers the `tensor.array_access` test family implemented by `vktTensorArrayAccess.cpp` and `genShaderArrayAccess`.
- Each case binds one tensor view and one storage buffer, then tests either `array_read` (tensor to buffer) or `array_write` (buffer to tensor).
- The registered matrix uses eight integer formats, the fixed rank-4 shape `{13, 17, 19, 23}`, linear and optimal tiling, array lengths 2, 3, 4, and an implementation maximum. The 128 leaves are listed in [tensor.txt#L1-L128](../../../mustpass/main/vk-default/tensor.txt#L1-L128).
- The page explains coordinate mapping, optimal-tensor staging, and the host comparison that turns a mismatch into a CTS failure.

## Background Knowledge

- A rank-`N` tensor uses `N` integer coordinates. `tensorReadARM` and `tensorWriteARM` operate on a starting coordinate and an array of elements; coordinates must stay within the tensor dimensions. See [Tensor Operations](../../../../vulkan-docs/src/chapters/VK_ARM_tensors/tensorops.adoc#tensors).
- Linear tensor storage can expose packed host data, while optimal tiling uses implementation-defined storage. Tensor views and tensor copy operations keep the shader from depending on physical offsets.

## Registration Hierarchy

```text
tensor.array_access
```

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Format | `r8_uint`, `r8_sint`, `r16_uint`, `r16_sint`, `r32_uint`, `r32_sint`, `r64_uint`, `r64_sint` | Selects the tensor element type and matching host comparison type. | [vktTensorTestsUtil.cpp#L115-L156](../../../modules/vulkan/tensor/vktTensorTestsUtil.cpp#L115-L156) |
| Tiling | `linear`, `optimal` | Chooses direct tensor transfer or a linear staging tensor used to initialize the optimal tensor and, for `array_write`, receive its result. | [vktTensorArrayAccess.cpp#L721-L759](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L721-L759) |
| Shape and rank | `shape_13_17_19_23` | Fixes rank to 4 and gives the coordinate calculation three outer dimensions plus an innermost dimension of 23. | [vktTensorArrayAccess.cpp#L715-L716](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L715-L716) |
| Array size | `2`, `3`, `4`, `max` | Sets the number of consecutive values handled by one tensor operation. `max` is resolved from device limits. | [vktTensorArrayAccess.cpp#L68-L76](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L68-L76) |
| Access variant | `array_read`, `array_write` | Selects the tensor-operation direction and initialized side. | [vktTensorArrayAccess.cpp#L365-L378](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L365-L378), [vktTensorArrayAccessShaders.cpp#L83-L109](../../../modules/vulkan/tensor/shaders/vktTensorArrayAccessShaders.cpp#L83-L109) |

## Behavior Parameters

The primary behavioral axis is the access variant. Both values use the same coordinate mapping and differ in which resource supplies the input and which resource receives the tensor-operation result.

### `array_read`: tensor array to buffer

The shader calls `tensorReadARM` at a computed rank-4 coordinate, stores the returned array in `tmp`, and copies valid entries from `tmp` into the storage buffer. The host initializes the tensor and clears the buffer, so a match means the tensor read and buffer writes preserved every logical element.

### `array_write`: buffer array to tensor

The shader loads valid entries from the storage buffer into `tmp` and calls `tensorWriteARM` at the same coordinate. The host clears the tensor and fills the buffer, then downloads the tensor and compares it with the unchanged buffer.

## Shader Analysis

The generator emits one compute shader for each exact parameter combination. The walkthrough below uses a mustpass case with `arraySize` 2, so the final innermost run demonstrates the boundary guard.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.tensor.array_access.r32_uint_optimal_shape_13_17_19_23_array_read_array_size_2
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `r32_uint` | The tensor and shader use 32-bit unsigned integer elements, and the host uses `uint32_t`. |
| `optimal` | The host initializes the optimal tensor from a linear staging tensor before dispatch; an `array_write` case would also copy the result back afterward. The descriptor remains the optimal tensor view. |
| `shape_13_17_19_23` | The shader declares rank 4 and reconstructs coordinates across 13 × 17 × 19 outer positions and 23 innermost elements. |
| `array_read_array_size_2` | Each invocation requests two consecutive values; the loop writes only values inside the innermost dimension. |

#### Purpose

This shader checks that an array-valued tensor read returns the consecutive values beginning at the computed rank-4 coordinate. It then writes those values to a linearly indexed storage buffer for host comparison.

#### Structural Design

| Shader phase | Operation | Result |
|--------------|-----------|--------|
| Dimension query | Call `tensorSizeARM` for dimensions 0 through 3. | The shader uses the bound tensor's actual sizes. |
| Work mapping | Use `gl_GlobalInvocationID.x` for the innermost run and `.y` for the flattened outer position. | Each invocation owns at most two values. |
| Coordinate construction | Divide and take modulo by later dimension sizes. | `coord_0` through `coord_3` identify the run start. |
| Tensor access | Read `tmp[2]` with `tensorReadARM`. | The tensor supplies the run values. |
| Boundary-safe store | Check `coord_3 + i < size_d3` before writing `data`. | The final run does not write past element 22. |

#### Shader Code

```glsl
#version 450
#extension GL_ARM_tensors : require
#extension GL_EXT_shader_explicit_arithmetic_types : require
layout(local_size_x = 1, local_size_y = 1, local_size_z = 1) in;
layout(set=0, binding = 0) uniform tensorARM<uint, 4> tens;
layout(set=0, binding = 1, std430) buffer _buff { uint data[]; };
void main()
{
\tconst uint size_d0 = tensorSizeARM(tens, 0);
\tconst uint size_d1 = tensorSizeARM(tens, 1);
\tconst uint size_d2 = tensorSizeARM(tens, 2);
\tconst uint size_d3 = tensorSizeARM(tens, 3);
\tconst uint offset_x = 2 * gl_GlobalInvocationID.x;
\tconst uint offset_y = gl_GlobalInvocationID.y;
\tconst uint coord_0 = offset_y / (1 * size_d1 * size_d2) % size_d0;
\tconst uint coord_1 = offset_y / (1 * size_d2) % size_d1;
\tconst uint coord_2 = offset_y / (1) % size_d2;
\tconst uint coord_3 = offset_x;
\tconst uint buffer_index = size_d3 * gl_GlobalInvocationID.y + 2 * gl_GlobalInvocationID.x;
\tuint tmp[2];
\ttensorReadARM(tens, uint&#91;&#93;(coord_0, coord_1, coord_2, coord_3), tmp);
\tfor (int i = 0; (i < 2) && (coord_3 + i < size_d3); ++i)
\t{
\t\tdata[buffer_index + i] = tmp[i];
\t}
}
```

#### Additional Info

- The generator uses `rank` to emit one `tensorSizeARM` query and one coordinate term per dimension; this case emits four of each.
- The dispatch dimensions are `ceil(23 / 2)` by `13*17*19`, or 12 by 4199 workgroups. Each local size is 1 × 1 × 1.
- `array_write` uses the same declarations and coordinate calculations but reverses the local-array transfer and calls `tensorWriteARM`.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Format | Changes `glslType`, the tensor and buffer element types, and the host template type. | [vktTensorArrayAccessShaders.cpp#L40-L54](../../../modules/vulkan/tensor/shaders/vktTensorArrayAccessShaders.cpp#L40-L54) |
| Array size | Changes `offset_x`, buffer indexing, the local array declaration, and the bounded loop. | [vktTensorArrayAccessShaders.cpp#L64-L103](../../../modules/vulkan/tensor/shaders/vktTensorArrayAccessShaders.cpp#L64-L103) |
| Access variant | Selects `tensorReadARM` plus buffer stores or buffer loads plus `tensorWriteARM`. | [vktTensorArrayAccessShaders.cpp#L83-L109](../../../modules/vulkan/tensor/shaders/vktTensorArrayAccessShaders.cpp#L83-L109) |
| Tiling | Does not change generated GLSL; optimal tiling changes host-side staging and copy commands. | [vktTensorArrayAccess.cpp#L512-L525](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L512-L525) |

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
; Bound: 121
; Schema: 0
               OpCapability Shader
               OpCapability TensorsARM
               OpExtension "SPV_ARM_tensors"
               OpExtension "SPV_KHR_storage_buffer_storage_class"
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
               OpName %size_d1 "size_d1"
               OpName %size_d2 "size_d2"
               OpName %size_d3 "size_d3"
               OpName %offset_x "offset_x"
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
               OpName %offset_y "offset_y"
               OpName %coord_0 "coord_0"
               OpName %coord_1 "coord_1"
               OpName %coord_2 "coord_2"
               OpName %coord_3 "coord_3"
               OpName %buffer_index "buffer_index"
               OpName %tmp "tmp"
               OpName %i "i"
               OpName %_buff "_buff"
               OpMemberName %_buff 0 "data"
               OpName %_ ""
               OpDecorate %tens Binding 0
               OpDecorate %tens DescriptorSet 0
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %_runtimearr_uint ArrayStride 4
               OpDecorate %_buff Block
               OpMemberDecorate %_buff 0 Offset 0
               OpDecorate %_ Binding 1
               OpDecorate %_ DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
     %uint_4 = OpConstant %uint 4
         %10 = OpTypeTensorARM %uint %uint_4
%_ptr_UniformConstant_10 = OpTypePointer UniformConstant %10
       %tens = OpVariable %_ptr_UniformConstant_10 UniformConstant
     %uint_0 = OpConstant %uint 0
     %uint_1 = OpConstant %uint 1
     %uint_2 = OpConstant %uint 2
     %uint_3 = OpConstant %uint 3
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
%_ptr_Input_uint = OpTypePointer Input %uint
%_arr_uint_uint_4 = OpTypeArray %uint %uint_4
%_arr_uint_uint_2 = OpTypeArray %uint %uint_2
%_ptr_Function__arr_uint_uint_2 = OpTypePointer Function %_arr_uint_uint_2
        %int = OpTypeInt 32 1
%_ptr_Function_int = OpTypePointer Function %int
      %int_0 = OpConstant %int 0
       %bool = OpTypeBool
      %int_2 = OpConstant %int 2
%_runtimearr_uint = OpTypeRuntimeArray %uint
      %_buff = OpTypeStruct %_runtimearr_uint
%_ptr_StorageBuffer__buff = OpTypePointer StorageBuffer %_buff
          %_ = OpVariable %_ptr_StorageBuffer__buff StorageBuffer
%_ptr_StorageBuffer_uint = OpTypePointer StorageBuffer %uint
      %int_1 = OpConstant %int 1
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
    %size_d0 = OpVariable %_ptr_Function_uint Function
    %size_d1 = OpVariable %_ptr_Function_uint Function
    %size_d2 = OpVariable %_ptr_Function_uint Function
    %size_d3 = OpVariable %_ptr_Function_uint Function
   %offset_x = OpVariable %_ptr_Function_uint Function
   %offset_y = OpVariable %_ptr_Function_uint Function
    %coord_0 = OpVariable %_ptr_Function_uint Function
    %coord_1 = OpVariable %_ptr_Function_uint Function
    %coord_2 = OpVariable %_ptr_Function_uint Function
    %coord_3 = OpVariable %_ptr_Function_uint Function
%buffer_index = OpVariable %_ptr_Function_uint Function
        %tmp = OpVariable %_ptr_Function__arr_uint_uint_2 Function
          %i = OpVariable %_ptr_Function_int Function
         %13 = OpLoad %10 %tens
         %15 = OpTensorQuerySizeARM %uint %13 %uint_0
               OpStore %size_d0 %15
         %17 = OpLoad %10 %tens
         %19 = OpTensorQuerySizeARM %uint %17 %uint_1
               OpStore %size_d1 %19
         %21 = OpLoad %10 %tens
         %23 = OpTensorQuerySizeARM %uint %21 %uint_2
               OpStore %size_d2 %23
         %25 = OpLoad %10 %tens
         %27 = OpTensorQuerySizeARM %uint %25 %uint_3
               OpStore %size_d3 %27
         %33 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %34 = OpLoad %uint %33
         %35 = OpIMul %uint %uint_2 %34
               OpStore %offset_x %35
         %37 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_1
         %38 = OpLoad %uint %37
               OpStore %offset_y %38
         %40 = OpLoad %uint %offset_y
         %41 = OpLoad %uint %size_d1
         %42 = OpIMul %uint %uint_1 %41
         %43 = OpLoad %uint %size_d2
         %44 = OpIMul %uint %42 %43
         %45 = OpUDiv %uint %40 %44
         %46 = OpLoad %uint %size_d0
         %47 = OpUMod %uint %45 %46
               OpStore %coord_0 %47
         %49 = OpLoad %uint %offset_y
         %50 = OpLoad %uint %size_d2
         %51 = OpIMul %uint %uint_1 %50
         %52 = OpUDiv %uint %49 %51
         %53 = OpLoad %uint %size_d1
         %54 = OpUMod %uint %52 %53
               OpStore %coord_1 %54
         %56 = OpLoad %uint %offset_y
         %57 = OpUDiv %uint %56 %uint_1
         %58 = OpLoad %uint %size_d2
         %59 = OpUMod %uint %57 %58
               OpStore %coord_2 %59
         %61 = OpLoad %uint %offset_x
               OpStore %coord_3 %61
         %63 = OpLoad %uint %size_d3
         %64 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_1
         %65 = OpLoad %uint %64
         %66 = OpIMul %uint %63 %65
         %67 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %68 = OpLoad %uint %67
         %69 = OpIMul %uint %uint_2 %68
         %70 = OpIAdd %uint %66 %69
               OpStore %buffer_index %70
         %71 = OpLoad %10 %tens
         %72 = OpLoad %uint %coord_0
         %73 = OpLoad %uint %coord_1
         %74 = OpLoad %uint %coord_2
         %75 = OpLoad %uint %coord_3
         %77 = OpCompositeConstruct %_arr_uint_uint_4 %72 %73 %74 %75
         %81 = OpTensorReadARM %_arr_uint_uint_2 %71 %77
               OpStore %tmp %81
               OpStore %i %int_0
               OpBranch %86
         %86 = OpLabel
               OpLoopMerge %88 %89 None
               OpBranch %90
         %90 = OpLabel
         %92 = OpLoad %int %i
         %94 = OpSLessThan %bool %92 %int_2
               OpSelectionMerge %96 None
               OpBranchConditional %94 %95 %96
         %95 = OpLabel
         %97 = OpLoad %uint %coord_3
         %98 = OpLoad %int %i
         %99 = OpBitcast %uint %98
        %100 = OpIAdd %uint %97 %99
        %101 = OpLoad %uint %size_d3
        %102 = OpULessThan %bool %100 %101
               OpBranch %96
         %96 = OpLabel
        %103 = OpPhi %bool %94 %90 %102 %95
               OpBranchConditional %103 %87 %88
         %87 = OpLabel
        %108 = OpLoad %uint %buffer_index
        %109 = OpLoad %int %i
        %110 = OpBitcast %uint %109
        %111 = OpIAdd %uint %108 %110
        %112 = OpLoad %int %i
        %113 = OpAccessChain %_ptr_Function_uint %tmp %112
        %114 = OpLoad %uint %113
        %116 = OpAccessChain %_ptr_StorageBuffer_uint %_ %int_0 %111
               OpStore %116 %114
               OpBranch %89
         %89 = OpLabel
        %117 = OpLoad %int %i
        %119 = OpIAdd %int %117 %int_1
               OpStore %i %119
               OpBranch %86
         %88 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The test creates a tensor with `VK_TENSOR_USAGE_SHADER_BIT_ARM`, a tensor view, and a host-visible storage buffer. The buffer contains one scalar for each tensor element.
- `array_read` fills the tensor and clears the buffer. `array_write` clears the tensor and fills the buffer.
- Both descriptor layouts have a tensor binding at 0 and a storage-buffer binding at 1, visible to the compute stage.
- The shader dispatch uses `inner_count = ceil(innermost_elements / arraySize)` and `outer_count = elements / innermost_elements`, then submits and waits on the universal queue.
- For `array_read`, a compute-to-host buffer barrier makes shader-written buffer contents visible before host inspection. For linear `array_write`, a compute-to-host tensor barrier makes the tensor readable before download.
- Optimal cases first copy a linear staging tensor into the optimal tensor. Only `array_write` copies the optimal tensor back after a compute-to-transfer barrier and downloads the linear tensor; `array_read` validates the shader-written buffer directly.
- The host compares all logical elements. The first mismatch returns `Comparison failed at index ...`; a complete match returns `Tensor test succeeded`.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `array_read` | Tensor read-array lowering, coordinate calculation, local-array handling, storage-buffer writes, or the host-to-optimal initialization path |
| `array_write` | Tensor write-array lowering, storage-buffer reads, local-array handling, coordinate calculation, or tensor readback/copy path |

### Cause Analysis

#### Tensor read-array path

**Possible failure symptoms:** An `array_read` case reports a mismatching element index, with the tensor-side value differing from the buffer value. A mismatch at a run boundary points to the array length or final-run guard; a mismatch repeated across outer positions points to coordinate reconstruction or the buffer index.

**Possible implementation causes:** The shader compiler or implementation may lower `OpTensorReadARM` with the wrong element count, starting coordinate, or result-array handling. A tensor view whose rank, format, or dimensions do not match the SPIR-V tensor type can also invalidate the operation under the tensor rules. For optimal cases, the linear-to-optimal initialization copy or its transfer-to-compute barrier can produce the same comparison symptom; buffer host visibility is shared with the linear path.

#### Tensor write-array path

**Possible failure symptoms:** An `array_write` case reports a mismatch after tensor download. The buffer contains the initialized source value, while the downloaded tensor differs at a particular run, outer position, or element index.

**Possible implementation causes:** The shader compiler or implementation may load the wrong buffer elements, lower `OpTensorWriteARM` with the wrong coordinate or array length, or mishandle the last partial run. A write that fails coordinate or view validation has no effect according to the tensor specification. In optimal cases, a missing or ineffective compute-to-transfer barrier, tensor copy, or linear-tensor download can leave stale data for the host; investigation must compare the shader path with the recorded copy and readback sequence.

#### Shared format, limit, and comparison infrastructure

**Possible failure symptoms:** The test may stop as `NotSupported` before dispatch when a required gate fails. If it reaches comparison, every access variant uses the same first-mismatch format, so a wrong scalar interpretation can appear as mismatches across the buffer.

**Possible implementation causes:** The test requires `VK_ARM_tensors`, shader tensor access in the compute stage, format support with `VK_FORMAT_FEATURE_2_TENSOR_SHADER_BIT_ARM`, a supported rank, and array length and byte size within device limits. A failure after those gates can require checking format conversion, host typed storage, tensor memory transfer helpers, and the element-by-element comparison path rather than assuming a shader defect.

## Case Pruning

### Requirement-based pruning

- `checkSupport` requires `VK_ARM_tensors`, a rank no larger than `maxTensorDimensionCount`, shader tensor access, compute-stage tensor access, and tensor shader format support for the selected format and tiling. Unsupported cases are reported as `NotSupported`.
- The selected array length must not exceed `maxTensorShaderAccessArrayLength`, and its byte count must not exceed `maxTensorShaderAccessSize`. The `max` case is calculated as the minimum of those two limits after division by the format element size.
- Optimal cases additionally require `deviceSupportsNonPackedTensors` when the tensor parameters are non-packed. The array-access matrix uses empty strides, so its tensors are packed.

### Design-based pruning

- The matrix fixes the shape to `{13, 17, 19, 23}` and the rank to 4. It varies the innermost run length instead of generating the broader shape and stride matrix used by other tensor test families.
- The test registers only array lengths 2, 3, 4, and the implementation maximum. The generator covers the partial final run through its bounds check, so additional lengths are not needed for this behavior axis.
- Each format is instantiated for both access variants and both tilings. Descriptor-array indexing and non-packed stride behavior are outside this test family.

## Key Takeaways

- `array_read` and `array_write` test opposite directions around the same rank-4 coordinate mapping, which makes their differences useful when a failure is direction-specific.
- The innermost dimension of 23 does not divide evenly by array sizes 2, 3, or 4. The shader must clip the last run rather than write beyond the tensor or buffer.
- Optimal tiling changes host staging and synchronization, not the generated coordinate or tensor-array operation.
- A passing case means every logical element matched after the direction-specific readback path; a failing index identifies the first observed mismatch, not a unique fault location.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Root registration | [vktTensorTests.cpp#L37-L47](../../../modules/vulkan/tensor/vktTensorTests.cpp#L37-L47) | Adds the `array_access` test family under `tensor`. |
| Array matrix and factory | [createArrayAccessTests#L712-L777](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L712-L777) | Defines every registered format, tiling, variant, and array length. |
| Support and max-size calculation | [calculateMaxArraySizeSupported#L68-L76](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L68-L76), [checkSupport#L134-L168](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L134-L168) | Maps device capabilities to skip decisions. |
| GLSL generator | [genShaderArrayAccess#L40-L116](../../../modules/vulkan/tensor/shaders/vktTensorArrayAccessShaders.cpp#L40-L116) | Emits tensor declarations, indexing, and array read/write code. |
| Linear execution | [TensorArrayReadWriteTestInstance::iterate#L330-L495](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L330-L495) | Creates resources, dispatches, synchronizes, and compares. |
| Optimal execution | [OptimalTensorArrayReadWriteTestInstance::iterate#L498-L709](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L498-L709) | Adds linear staging tensor copies around the same shader test. |
| Tensor operation rules | [tensorops.adoc#L8-L24](../../../../vulkan-docs/src/chapters/VK_ARM_tensors/tensorops.adoc#L8-L24), [tensorops.adoc#L82-L109](../../../../vulkan-docs/src/chapters/VK_ARM_tensors/tensorops.adoc#L82-L109) | Defines coordinate validation and tensor read semantics. |
| Device limits | [limits.adoc#L5704-L5728](../../../../vulkan-docs/src/chapters/limits.adoc#L5704-L5728) | Defines rank, array-length, and byte-size limits. |
| Tensor shader feature | [features.adoc#L8042-L8055](../../../../vulkan-docs/src/chapters/features.adoc#L8042-L8055) | Defines `shaderTensorAccess` and related shader features. |
| Mustpass cases | [tensor.txt#L1-L128](../../../mustpass/main/vk-default/tensor.txt#L1-L128) | Confirms the exact 128 registered array-access leaves. |
