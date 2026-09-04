## Overview

**Core question:** Do compute shaders preserve tensor values when they access `VK_ARM_tensors` through the registered formats, ranks, layouts, strides, and memory paths?

- This page covers the `tensor.basic_access` test family, created by [`createBasicAccessTests`](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L1025-L1036) and attached below the `tensor` test category by [`createTests`](../../../modules/vulkan/tensor/vktTensorTests.cpp#L37-L49).
- The family checks shader access to 8-, 16-, 32-, and 64-bit signed and unsigned integer tensors. Linear cases register both shader directions; optimal cases run a buffer-to-tensor-to-buffer round trip.
- The matrix covers ranks one through four, implicit and explicit packed linear storage, explicit non-packed byte strides, implementation-defined optimal tiling, max-rank shapes, forced staging, allocation offsets, and registered DMA-BUF paths.
- The page explains how `genShaderTensorAccess` maps a flattened invocation index to tensor coordinates, how the host transfers data and synchronizes, and how failures map to access direction and layout path.

## Background Knowledge

- **Tensor coordinates.** A rank-`N` tensor needs `N` integer coordinates. `tensorSizeARM` reports a dimension size, while `tensorReadARM` and `tensorWriteARM` operate on a coordinate vector. The shader must keep the coordinate count and bounds consistent with the created tensor view.
- **Linear strides and optimal tiling.** Linear tensors use byte strides. Empty strides request packed addressing; explicit strides can insert padding between outer dimensions. Optimal tensors use an implementation-defined arrangement, so callers describe them with empty strides and use tensor operations rather than host pointer arithmetic.
- **Tensor operation compatibility.** The tensor view and SPIR-V tensor type must agree on element type and rank, and a coordinate must lie within every dimension. These rules explain why this test varies the shader type and rank together and why its coordinate calculation matters. See [Tensor Operations](../../../../vulkan-docs/src/chapters/VK_ARM_tensors/tensorops.adoc#tensors).

## Registration Hierarchy

```text
tensor.basic_access
```

The family generates leaves from format, tiling, shape, stride, access, allocator, staging, and offset choices. The generated names are listed in the parameter sections and in `tensor.txt`.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Host element type and tensor format | `r8_uint`, `r8_sint`, `r16_uint`, `r16_sint`, `r32_uint`, `r32_sint`, `r64_uint`, `r64_sint` | Each host type instantiation supplies the matching signed and unsigned format at one element width. | [`getTestFormats<T>`](../../../modules/vulkan/tensor/vktTensorTestsUtil.cpp#L115-L156) |
| Shape and rank | `71693` (rank 1), `263_269` (rank 2), `37_43_47` (rank 3), `13_17_19_23` (rank 4) | Tests flattened indexing across ranks one through four. | [`shapes`](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L853-L861) |
| Linear packing | implicit packed, explicit packed strides, explicit non-packed strides | Distinguishes implementation-supplied packed strides from explicit byte-stride descriptions. | [`addShaderAccessTests`](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L872-L906) |
| Tiling | `linear`, `optimal` | Linear cases expose address calculation and strides; optimal cases expose shader access without assuming a host layout. | [`addShaderAccessTests`](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L908-L912) |
| Linear access direction | `shader_read`, `shader_write` | The registered name identifies whether the shader reads the tensor or writes it; the opposite endpoint is a storage buffer. | [`AccessVariant` name mapping](../../../modules/vulkan/tensor/vktTensorTestsUtil.cpp#L272-L294) |
| Max-rank coverage | `*_linear_max_rank_shader_read`, `*_linear_max_rank_shader_write`, `*_optimal_max_rank` | An empty source dimension vector is replaced with the device's `maxTensorDimensionCount`. | [`calculateMaxDimensionCountParameters`](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L70-L84) |
| Memory path | ordinary allocation, `forced_staging`, `_offset_2000`, `_dma_heap_buffer`, combined DMA offset | Exercises direct or helper-mediated transfers, binding at a nonzero allocation offset, and importable DMA-BUF tensor memory. | [`addShaderAccessTests`](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L916-L934), [`addDmaHeapBufferAccessTestInternal`](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L956-L1013) |

For explicit non-packed linear cases, the innermost stride is `elementSize`; each preceding stride is the next stride multiplied by the next dimension plus `13 * elementSize`. The resulting byte values appear in registered names such as `strides_1128_4`. Rank-one cases omit this dimension because there is no outer dimension in which to add padding.

## Behavior Parameters

The primary behavioral axis is the access path. Format, rank, shape, stride, and memory-path values change the instance within that path.

### `shader_read`: tensor input, buffer output

The shader calls `tensorReadARM` and stores the returned value in the runtime storage buffer. The host fills the tensor reference data, uploads it, clears the buffer, dispatches one invocation per element, then compares the buffer with the tensor reference. The registered spelling is counterintuitive if read as a host operation: it names the shader's tensor read, not a host readback.

### `shader_write`: buffer input, tensor output

The shader loads `data[index]` from the storage buffer and calls `tensorWriteARM` with the computed tensor coordinate. The host fills the buffer, clears the tensor, dispatches, downloads the tensor when needed, and compares tensor data with the original buffer.

### Optimal buffer-to-tensor-to-buffer round trip: opaque tensor layout

An optimal case compiles both access directions. The first dispatch reads the source buffer and writes the tensor; a tensor memory barrier orders the second dispatch, which reads the tensor and writes the destination buffer. The host compares the two linear buffers, so it checks the opaque layout through the shader operations without interpreting optimal tensor memory on the host.

## Shader Analysis

The following walkthrough uses the exact rank-2 `r32_sint` `shader_write` case. The generator emits the same structure for other ranks and formats, changing only the explicit type, rank, and number of coordinate calculations.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.tensor.basic_access.r32_sint_linear_shape_263_269_shader_write
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `r32_sint` | Selects `VK_FORMAT_R32_SINT`, the `uint32_t` host instantiation, and GLSL type `int32_t`. |
| `linear_shape_263_269` | Creates a rank-2 linear tensor with dimensions 263 and 269 and implicit packed strides. |
| `shader_write` | Generates `tensorWriteARM`; the shader reads the storage buffer and writes the tensor. |

#### Purpose

This shader tests whether a compute invocation can translate its flattened element index into a valid rank-2 tensor coordinate and write the matching 32-bit signed value there.

#### Structural Design

| Phase | Shader operation | Result |
|-------|------------------|--------|
| Query | `tensorSizeARM(tens, 0/1)` | Load the runtime dimension sizes. |
| Address | Divide and modulo `gl_GlobalInvocationID.x` | Produce row coordinate `coord_0` and column coordinate `coord_1`. |
| Transfer | Load `data[index]` and call `tensorWriteARM` | Write one logical element to the tensor. |

#### Shader Code

```glsl
#version 450
#extension GL_ARM_tensors : require
#extension GL_EXT_shader_explicit_arithmetic_types : require
layout(local_size_x = 1, local_size_y = 1, local_size_z = 1) in;
/// Binding 0 is the rank-2 tensor view; binding 1 is the linear reference buffer.
layout(set=0, binding = 0) uniform tensorARM<int32_t, 2> tens;
layout(set=0, binding = 1, std430) buffer _buff { int32_t data[]; };

void main()
{
    /// Query both tensor dimensions so the same shader shape works for runtime-created tensors.
    const uint size_d0 = tensorSizeARM(tens, 0);
    const uint size_d1 = tensorSizeARM(tens, 1);
    /// Flattened invocation i maps to (i / size_d1) % size_d0, i % size_d1.
    const uint coord_0 = gl_GlobalInvocationID.x / (1 * size_d1) % size_d0;
    const uint coord_1 = gl_GlobalInvocationID.x / (1) % size_d1;
    const uint index = gl_GlobalInvocationID.x;
    /// This direction reads the buffer and writes the tensor.
    tensorWriteARM(tens, uint[]
                   (coord_0, coord_1), data[index]);
}
```

#### Additional Info

- The source generator uses `tensorReadARM` for `WRITE_TO_BUFFER` and `tensorWriteARM` for `READ_FROM_BUFFER`; `AccessVariant` maps those enum values to the registered suffixes `shader_read` and `shader_write`, respectively. [`genShaderTensorAccess`](../../../modules/vulkan/tensor/shaders/vktTensorAccessShaders.cpp#L40-L94)
- For a max-rank leaf, the host resolves the empty dimension vector from `maxTensorDimensionCount` before creating the instance and shader. [`LinearTensorAccessTestCase::createInstance`](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L174-L190)

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Format | Changes the GLSL explicit arithmetic type in both the tensor declaration and storage buffer. | [`getTensorFormat`](../../../modules/vulkan/tensor/shaders/vktTensorShaderUtil.cpp#L39-L71) |
| Rank | Changes `tensorARM<type, rank>`, the number of `tensorSizeARM` queries, and the coordinate vector length. | [`genShaderTensorAccess`](../../../modules/vulkan/tensor/shaders/vktTensorAccessShaders.cpp#L52-L89) |
| Access direction | Selects `tensorReadARM` for `shader_read` or `tensorWriteARM` for `shader_write`. | [`genShaderTensorAccess`](../../../modules/vulkan/tensor/shaders/vktTensorAccessShaders.cpp#L75-L89) |
| Shape and strides | Do not change emitted shader text; the queried sizes and tensor descriptor change the address target, while host `StridedMemoryUtils` models explicit strides. | [`TensorParameters::packed`](../../../modules/vulkan/tensor/vktTensorTestsUtil.hpp#L68-L101) |

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
; Bound: 57
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
               OpName %coord_0 "coord_0"
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
               OpName %coord_1 "coord_1"
               OpName %index "index"
               OpName %_buff "_buff"
               OpMemberName %_buff 0 "data"
               OpName %_ ""
               OpDecorate %tens Binding 0
               OpDecorate %tens DescriptorSet 0
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %_runtimearr_int ArrayStride 4
               OpDecorate %_buff Block
               OpMemberDecorate %_buff 0 Offset 0
               OpDecorate %_ Binding 1
               OpDecorate %_ DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
        %int = OpTypeInt 32 1
     %uint_2 = OpConstant %uint 2
         %11 = OpTypeTensorARM %int %uint_2
%_ptr_UniformConstant_11 = OpTypePointer UniformConstant %11
       %tens = OpVariable %_ptr_UniformConstant_11 UniformConstant
     %uint_0 = OpConstant %uint 0
     %uint_1 = OpConstant %uint 1
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
%_ptr_Input_uint = OpTypePointer Input %uint
%_arr_uint_uint_2 = OpTypeArray %uint %uint_2
%_runtimearr_int = OpTypeRuntimeArray %int
      %_buff = OpTypeStruct %_runtimearr_int
%_ptr_StorageBuffer__buff = OpTypePointer StorageBuffer %_buff
          %_ = OpVariable %_ptr_StorageBuffer__buff StorageBuffer
      %int_0 = OpConstant %int 0
%_ptr_StorageBuffer_int = OpTypePointer StorageBuffer %int
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
    %size_d0 = OpVariable %_ptr_Function_uint Function
    %size_d1 = OpVariable %_ptr_Function_uint Function
    %coord_0 = OpVariable %_ptr_Function_uint Function
    %coord_1 = OpVariable %_ptr_Function_uint Function
      %index = OpVariable %_ptr_Function_uint Function
         %14 = OpLoad %11 %tens
         %16 = OpTensorQuerySizeARM %uint %14 %uint_0
               OpStore %size_d0 %16
         %18 = OpLoad %11 %tens
         %20 = OpTensorQuerySizeARM %uint %18 %uint_1
               OpStore %size_d1 %20
         %26 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %27 = OpLoad %uint %26
         %28 = OpLoad %uint %size_d1
         %29 = OpIMul %uint %uint_1 %28
         %30 = OpUDiv %uint %27 %29
         %31 = OpLoad %uint %size_d0
         %32 = OpUMod %uint %30 %31
               OpStore %coord_0 %32
         %34 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %35 = OpLoad %uint %34
         %36 = OpUDiv %uint %35 %uint_1
         %37 = OpLoad %uint %size_d1
         %38 = OpUMod %uint %36 %37
               OpStore %coord_1 %38
         %40 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %41 = OpLoad %uint %40
               OpStore %index %41
         %42 = OpLoad %11 %tens
         %43 = OpLoad %uint %coord_0
         %44 = OpLoad %uint %coord_1
         %46 = OpCompositeConstruct %_arr_uint_uint_2 %43 %44
         %52 = OpLoad %uint %index
         %54 = OpAccessChain %_ptr_StorageBuffer_int %_ %int_0 %52
         %55 = OpLoad %int %54
               OpTensorWriteARM %42 %46 %55
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- **Support and instance setup.** Each case requires `VK_ARM_tensors`, checks the registered rank against `maxTensorDimensionCount`, requires `VK_FORMAT_FEATURE_2_TENSOR_SHADER_BIT_ARM` for the selected tiling, and checks `shaderTensorAccess` plus compute-stage support. Non-packed cases also require `tensorNonPacked`. DMA cases additionally require `VK_EXT_external_memory_dma_buf`, a supported DMA heap allocator, and an importable, non-dedicated DMA-BUF description. [`LinearTensorAccessTestCase::checkSupport`](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L193-L240), [`OptimalTensorAccessTestCase::checkSupport`](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L324-L366)
- **Tensor and buffer creation.** The host constructs `VkTensorDescriptionARM` from tiling, format, dimensions, and strides with `VK_TENSOR_USAGE_SHADER_BIT_ARM`, binds a `VkTensorViewARM` at descriptor binding 0, and creates a host-visible `VK_BUFFER_USAGE_STORAGE_BUFFER_BIT` buffer at binding 1. The optimal path creates separate source and destination host-visible buffers. [`LinearTensorAccessTestInstance::iterate`](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L449-L474), [`OptimalTensorAccessTestInstance::iterate`](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L665-L694)
- **Reference preparation.** `StridedMemoryUtils<T>` represents tensor bytes with the selected dimensions and strides. For `shader_read`, it fills tensor data, uploads it, and clears the buffer. For `shader_write`, it clears the tensor and fills the buffer. The host flushes buffer allocations before dispatch. [`LinearTensorAccessTestInstance::iterate`](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L476-L500)
- **Memory paths.** Ordinary cases use the default allocator. `_offset_2000` and DMA cases create a `SimpleAllocator` or `DmaHeapAllocator` with optional offset parameters based on `nonCoherentAtomSize`; DMA tensor creation adds `VK_EXTERNAL_MEMORY_HANDLE_TYPE_DMA_BUF_BIT_EXT`. `forced_staging` passes `true` to tensor upload/download helpers even when the tensor allocation is host visible. [`LinearTensorAccessTestInstance::iterate`](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L413-L447), [`LinearTensorAccessTestInstance::iterate`](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L459-L466)
- **Dispatch and synchronization.** The host builds a compute pipeline, binds the descriptor set, and dispatches `elements` workgroups. A `shader_write` case uses a tensor barrier for the subsequent tensor download; a `shader_read` case uses a buffer barrier from compute shader writes to host reads. The queue submission is waited on before host validation. [`LinearTensorAccessTestInstance::iterate`](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L532-L585)
- **Optimal sequence.** The first compute pipeline reads the source buffer and writes the tensor. `vkCmdPipelineBarrier2` carries the tensor write to the second compute shader's tensor read. The second pipeline writes the destination buffer, followed by a compute-to-host buffer barrier and queue wait. [`OptimalTensorAccessTestInstance::iterate`](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L761-L823)
- **Host check.** The host invalidates buffer allocations, downloads the tensor for `shader_write` cases when needed, and compares all logical elements. A mismatch returns the index and values; success returns `Tensor test succeeded`. Optimal cases compare source and destination buffers after invalidation. [`LinearTensorAccessTestInstance::iterate`](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L587-L616), [`OptimalTensorAccessTestInstance::iterate`](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L825-L850)

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `shader_read` | Incorrect tensor read, coordinate calculation, format or stride handling, storage-buffer write, or tensor-to-host synchronization. |
| `shader_write` | Incorrect tensor write, coordinate calculation, format or stride handling, storage-buffer read, or host-to-tensor preparation. |
| optimal buffer-to-tensor-to-buffer round trip | Incorrect buffer-to-tensor or tensor-to-buffer shader access, optimal tensor layout handling, inter-dispatch ordering, or final readback. |

### Cause Analysis

#### Tensor read and buffer write path

**Possible failure symptoms:** A `shader_read` case reports `Comparison failed at index <n>`, with the buffer value different from the tensor reference at that flattened index.

**Possible implementation causes:** The compute shader may lower `tensorReadARM` incorrectly, use a wrong coordinate for a rank or stride combination, or store the wrong value in the storage buffer. If tensor values are correct before dispatch but the host sees stale buffer data, inspect the compute-to-host barrier, allocation invalidation, and queue wait. The source does not identify a more specific implementation cause.

#### Buffer read and tensor write path

**Possible failure symptoms:** A `shader_write` case reports a mismatch after the host downloads the tensor. Failures that begin at a row or higher-dimensional slice boundary are consistent with a stride or coordinate-addressing error.

**Possible implementation causes:** The implementation may mishandle `tensorWriteARM`, the tensor view's format or rank, or explicit non-packed byte strides. A mismatch across all elements can also indicate incorrect buffer preparation or tensor download; the test flushes the buffer, orders shader writes to the tensor, waits for completion, and invalidates host allocations before comparison.

#### Optimal round-trip path

**Possible failure symptoms:** An optimal case fails when linear cases pass, or the destination buffer diverges from the source after the two dispatches. The first mismatch can expose a problem in either tensor access direction or in the opaque layout transition.

**Possible implementation causes:** The implementation may mishandle optimal tensor storage or one direction of the two tensor operations. The test inserts a tensor write-to-read barrier between dispatches and a final shader-write-to-host-read barrier, so a remaining mismatch needs implementation-level investigation rather than an assumed host-ordering fault.

#### Shared format, rank, and host-transfer conditions

**Possible failure symptoms:** A format-specific, max-rank, non-packed, offset, forced-staging, or DMA leaf fails while a nearby ordinary case passes. The reported symptom remains a value mismatch, but its parameter suffix identifies the condition that changed.

**Possible implementation causes:** The tensor view and shader declaration may disagree on the selected element type or rank, or the implementation may address explicit strides, allocation offsets, staging transfers, or imported DMA memory incorrectly. The Vulkan tensor operation rules make type/rank compatibility and in-bounds coordinates requirements; the source does not justify narrowing a failure to hardware, driver, compiler, or host without further investigation.

## Case Pruning

### Requirement-based pruning

- `VK_ARM_tensors` is required for every case.
- A rank above `maxTensorDimensionCount` is rejected. Rank-0 registration is resolved to that device property before execution.
- The selected format and tiling must expose `VK_FORMAT_FEATURE_2_TENSOR_SHADER_BIT_ARM`.
- `shaderTensorAccess` and compute-stage membership in `shaderTensorSupportedStages` are required.
- Explicit non-packed linear cases require the `tensorNonPacked` feature.
- DMA cases require `VK_EXT_external_memory_dma_buf`, a supported `DmaHeapAllocator`, and an external tensor query that reports importable DMA-BUF support, does not require dedicated-only allocation, and accepts the DMA-BUF handle type. [`formatSupportTensorFlags`, feature helpers, and `tensorSupportsDmaBufImport`](../../../modules/vulkan/tensor/vktTensorTestsUtil.cpp#L341-L432)

These checks report unsupported cases rather than failed tensor results.

### Design-based pruning

- The matrix uses one signed and one unsigned format at each width, from 8 through 64 bits. It does not register floating-point or boolean formats for this family, although shared utilities support other tensor pages.
- Non-packed strides are generated only for ranks greater than one because rank one has no outer stride to pad.
- Optimal tensors use empty strides and are tested through linear host buffers. The test does not assume that optimal tensor memory can be directly interpreted by the host.
- The max-rank shape uses sizes `151`, `3`, and `157` at selected positions and `1` elsewhere, rather than enumerating a separate fixed shape for every possible device rank.
- DMA special cases use the first format for each host type and the rank-4 shape. The registration includes linear read/write paths, forced staging, offset `2000`, and optimal offset cases; these are targeted memory-path checks, not a second full format and shape matrix.

## Key Takeaways

- `shader_read` and `shader_write` name the shader's tensor direction, so the suffix should be read together with the generator's `AccessVariant` mapping.
- The shader uses runtime dimension queries and a flattened invocation index. The host varies rank and strides while keeping the generated coordinate algorithm generic.
- Explicit non-packed cases make byte-stride mistakes visible at row and slice boundaries; optimal cases test opaque storage through a two-dispatch round trip.
- Offsets, forced staging, and DMA-BUF allocations alter the memory path without changing the shader's tensor interface. Failures on those leaves need the allocation and transfer path checked alongside shader access.
- The host declares success only after synchronization, cache invalidation or tensor download, and an element-by-element comparison.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Tensor category registration | [`createTests`](../../../modules/vulkan/tensor/vktTensorTests.cpp#L37-L49) | Adds the `basic_access` test family below `tensor`. |
| Basic-access registration | [`createBasicAccessTests`](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L1025-L1036) | Defines the page boundary and format-type instantiations. |
| Linear and special-case matrix | [`addShaderAccessTests`](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L853-L953) | Registers shapes, strides, directions, staging, offsets, optimal leaves, and max-rank leaves. |
| DMA matrix | [`addDmaHeapBufferAccessTestInternal`](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L956-L1013) | Registers DMA-BUF, staging, and DMA-offset leaves. |
| Linear runtime | [`LinearTensorAccessTestInstance::iterate`](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L401-L616) | Creates resources, dispatches, synchronizes, transfers, and compares. |
| Optimal runtime | [`OptimalTensorAccessTestInstance::iterate`](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L618-L850) | Runs buffer-to-tensor-to-buffer and compares the two host buffers. |
| Shader generator | [`genShaderTensorAccess`](../../../modules/vulkan/tensor/shaders/vktTensorAccessShaders.cpp#L40-L94) | Emits the rank-specific compute shader and chooses tensor read/write. |
| Shader type mapping | [`getTensorFormat`](../../../modules/vulkan/tensor/shaders/vktTensorShaderUtil.cpp#L39-L71) | Maps `VkFormat` to GLSL explicit arithmetic types. |
| Tensor parameters | [`TensorParameters`](../../../modules/vulkan/tensor/vktTensorTestsUtil.hpp#L68-L101) | Defines dimensions, strides, rank, element count, and packed detection. |
| Feature and DMA checks | [`formatSupportTensorFlags` and helpers](../../../modules/vulkan/tensor/vktTensorTestsUtil.cpp#L341-L432) | Implements format, feature, stage, non-packed, and DMA support queries. |
| Tensor operation semantics | [Tensor Operations](../../../../vulkan-docs/src/chapters/VK_ARM_tensors/tensorops.adoc#tensors) | Defines coordinate, type/rank compatibility, read, write, and format-conversion rules. |
| Registered cases | [`tensor.txt`](../../../mustpass/main/vk-default/tensor.txt#L129-L408) | Lists the 280 `tensor.basic_access` mustpass leaves, including special suffixes. |
