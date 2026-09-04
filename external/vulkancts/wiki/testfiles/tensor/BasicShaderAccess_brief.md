# Understanding Brief: tensor.basic_access

## One-Sentence Test Purpose

This test checks whether compute shaders can read from and write to `VK_ARM_tensors` tensors correctly across supported integer formats, ranks, layouts, strides, and tensor-memory paths.

## Background Knowledge

### Tensor coordinates and linear storage

A tensor has a rank and one size per dimension. A shader supplies one coordinate for each dimension to `tensorReadARM` or `tensorWriteARM`; the coordinate count must match the tensor rank. Linear tensor storage uses byte strides. Packed strides place elements consecutively, while non-packed strides add padding between outer dimensions. Optimal tiling leaves the physical arrangement to the implementation.

Why it matters here:
- The shader derives coordinates from one flattened invocation index, so every logical element can be checked without embedding a shape in the shader.
- The host's `StridedMemoryUtils` uses the same dimensions and strides to construct the expected tensor contents.

### Tensor operations and compute execution

`tensorReadARM` reads a tensor element into the shader, and `tensorWriteARM` writes a shader value to a tensor element. `tensorSizeARM` queries a dimension size from the bound tensor. Each compute invocation has a one-dimensional global index because the generated workgroup size is `1,1,1`.

Why it matters here:
- The `shader_read` name means the shader reads the tensor and writes the storage buffer; `shader_write` means the shader reads the storage buffer and writes the tensor.
- The Vulkan tensor operation rules require compatible element type, rank, shape, and coordinates. A mismatch can produce an invalid result or an ineffective write.

## One Concrete Example

Consider `dEQP-VK.tensor.basic_access.r32_sint_linear_shape_263_269_shader_write`. The host creates a rank-2 `VK_FORMAT_R32_SINT` linear tensor with dimensions `263,269`, fills a storage buffer with one value per logical element, and clears the tensor. The generated compute shader queries the two sizes, maps invocation `i` to `(i / 269) % 263, i % 269`, and writes `data[i]` to that tensor coordinate. After dispatch, the host downloads the tensor and compares all `263 * 269` values with the original buffer.

The example is faithful to the generator, except that the explanatory comments are added for this brief.

## End-to-End Test Flow

```text
[host] select format, tiling, dimensions, optional strides, access direction, offset, and allocator path
[host] query support for VK_ARM_tensors, shader tensor access, the compute stage, format features, and any non-packed or DMA requirements
[host] create and bind a tensor and a host-visible storage buffer
[host] fill the tensor and clear the buffer for shader_read, or clear the tensor and fill the buffer for shader_write
[host] generate and compile the rank/format-specific compute shader
[host] bind the tensor view at descriptor binding 0 and the storage buffer at binding 1
[host] submit a dispatch with one invocation per logical element
[device] query tensor dimensions and calculate one valid tensor coordinate from gl_GlobalInvocationID.x
[device] read one resource and write the other with tensorReadARM or tensorWriteARM
[host] apply the tensor or buffer memory barrier, wait for queue completion, and download or invalidate data as needed
[host] compare every logical element and return pass or the first mismatch
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `genShaderTensorAccess` emits one GLSL compute shader for each linear case. It selects the explicit arithmetic type from the tensor format and the tensor rank from the dimensions. Optimal cases compile two shaders, one for each direction of a buffer-to-tensor round trip.
- The shader declares `layout(local_size_x = 1, local_size_y = 1, local_size_z = 1) in`, a `tensorARM<type, rank>` at set 0 binding 0, and a `std430` runtime storage buffer at set 0 binding 1.
- For a rank-0 registration used for max-rank coverage, the test queries `maxTensorDimensionCount` during instance creation and uses dimensions with leading size `151`, trailing sizes `3` and `157`, and `1` elsewhere.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `VkTensorARM` plus `VkTensorViewARM` | yes | yes, binding 0 | read or written by the selected shader | indirectly, through tensor upload/download helpers | Carries the format, tiling, dimensions, and optional byte strides under test. |
| Storage buffer | yes, host-visible | yes, binding 1 | written for `shader_read`, read for `shader_write` | yes | Supplies or receives the reference sequence. |
| Optimal-path source buffer | yes, host-visible | yes, binding 1 in the first compute pipeline | read | yes | Supplies values to the first buffer-to-tensor shader. |
| Optimal-path destination buffer | yes, host-visible | yes, binding 1 in the second compute pipeline | written | yes | Receives values from the tensor-to-buffer shader. |
| Staging buffer, when selected by the helper | yes | temporarily, through a tensor-memory alias | transfers tensor data | copied by the host helper | Exercises a non-host-visible or forced-staging transfer route; it is not the shader's tensor descriptor. |
| DMA-BUF-backed tensor allocation, where registered | yes | through the tensor binding | read or written by the shader | through the helper | Exercises importable external tensor memory. |

The tensor itself is not a host array. `StridedMemoryUtils<T>` is host-side reference storage that knows the tensor dimensions and byte strides.

## What Is Checked

- The shader runs once per logical element with `vk.cmdDispatch(..., elements, 1, 1)`.
- In a linear single-direction case, the host compares the tensor reference data and storage-buffer data at every flattened element index. For `shader_write`, the reference is the buffer that the shader read and the downloaded tensor data is compared with it. For `shader_read`, the tensor reference is compared with the buffer written by the shader.
- In an optimal case, the host compares the initialized source buffer with the final destination buffer after buffer-to-tensor and tensor-to-buffer dispatches.
- The first mismatch returns `Comparison failed at index <n>` with the two values. A complete comparison returns `Tensor test succeeded`.

## Behavior Parameter Identification

> **Behavior parameter:** access path
>
> **Candidate values:** `shader_read`, `shader_write`, optimal buffer-to-tensor-to-buffer round trip

The first two values are the registered linear shader direction. Optimal leaves use the fixed two-dispatch round trip generated by `OptimalTensorAccessTestCase`.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `shader_read` | Incorrect tensor read, coordinate calculation, format or stride handling, storage-buffer write, or tensor-to-host synchronization. |
| `shader_write` | Incorrect tensor write, coordinate calculation, format or stride handling, storage-buffer read, or host-to-tensor preparation. |
| optimal buffer-to-tensor-to-buffer round trip | Incorrect buffer-to-tensor or tensor-to-buffer shader access, optimal tensor layout handling, inter-dispatch ordering, or final readback. |

## Important Variations and Special Cases

- Formats are `VK_FORMAT_R8_UINT`, `VK_FORMAT_R8_SINT`, `VK_FORMAT_R16_UINT`, `VK_FORMAT_R16_SINT`, `VK_FORMAT_R32_UINT`, `VK_FORMAT_R32_SINT`, `VK_FORMAT_R64_UINT`, and `VK_FORMAT_R64_SINT`. The host type and GLSL explicit arithmetic type match the format width and signedness.
- The ordinary linear matrix uses shapes `71693`, `263_269`, `37_43_47`, and `13_17_19_23`, covering ranks one through four. Rank-one cases have no non-packed-stride variant.
- Empty linear strides request implicit packed layout. Explicit packed strides are also registered. Explicit non-packed strides retain an innermost stride equal to the element size and add `13 * elementSize` to each outer stride.
- Optimal cases use empty strides because optimal tensor storage is implementation-dependent. The registered DMA cases use the rank-4 shape `13,17,19,23` and the first format for each host type, with linear read/write cases plus optimal cases at offset `0` and `2000`.
- `forced_staging` asks upload/download helpers to use staging even when tensor memory is host visible. `_offset_2000` binds the tensor at byte offset `2000`; DMA variants use `VK_EXTERNAL_MEMORY_HANDLE_TYPE_DMA_BUF_BIT_EXT`, and the combined offset case uses the same offset inside the DMA-heap allocation.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Test-category registration | [`createTests`](../../../modules/vulkan/tensor/vktTensorTests.cpp#L37-L49) | Adds `basic_access` below `tensor`. |
| Basic-access registration | [`createBasicAccessTests`](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L1025-L1036) | Creates the test family and adds format, layout, staging, offset, max-rank, and DMA cases. |
| Linear and optimal matrix | [`addShaderAccessTests`](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L853-L953) | Defines shapes, packed/non-packed strides, directions, optimal cases, forced staging, offset, and max-rank leaves. |
| DMA matrix | [`addDmaHeapBufferAccessTestInternal`](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L956-L1013) | Registers DMA-heap, staging, and offset variants. |
| Shader generation | [`genShaderTensorAccess`](../../../modules/vulkan/tensor/shaders/vktTensorAccessShaders.cpp#L40-L94) | Emits tensor declarations, dimension queries, coordinate mapping, and read/write operation. |
| Format mapping | [`getTensorFormat`](../../../modules/vulkan/tensor/shaders/vktTensorShaderUtil.cpp#L39-L71) | Maps Vulkan formats to GLSL types. |
| Linear execution and check | [`LinearTensorAccessTestInstance::iterate`](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L401-L616) | Creates resources, dispatches, synchronizes, downloads, and compares. |
| Optimal execution and check | [`OptimalTensorAccessTestInstance::iterate`](../../../modules/vulkan/tensor/vktTensorBasicShaderAccess.cpp#L618-L850) | Runs the two-direction round trip and compares source and destination buffers. |
| Support helpers | [`formatSupportTensorFlags` and feature helpers](../../../modules/vulkan/tensor/vktTensorTestsUtil.cpp#L341-L432) | Checks format features, shader tensor features, stages, non-packed tensors, and DMA import. |
| Tensor operation rules | [Tensor Operations](../../../../vulkan-docs/src/chapters/VK_ARM_tensors/tensorops.adoc#tensors) | Defines tensor coordinates, compatibility validation, format conversion, and read/write behavior. |

## Questions / Risk Points for User Audit

- Does the distinction between the registered `shader_read`/`shader_write` names and the resource direction remain clear?
- Is the difference between host reference storage and the actual `VkTensorARM` clear?
- Does the rank-0 max-rank explanation avoid implying a fixed rank when the device property supplies it?
- Are the DMA and forced-staging paths described as registered special cases rather than universal behavior?
- Does the representative rank-2 shader make the flattened-index-to-coordinate mapping easy to verify?

## Conversion Notes for Final Wiki Page

- Keep the final page's Background Knowledge to the tensor coordinate and layout concepts needed by the later sections.
- Use the rank-2 `r32_sint` `shader_write` case as the one representative shader walkthrough.
- Preserve the parameter and resource tables, but move setup details into Runtime Execution and Result Checking.
- Copy the `### Failure Cause Mapping` table directly into the final page. Write `### Cause Analysis` separately so it is not inherited from this brief.
- Keep Vulkan tensor-operation semantics in the page's background and source appendix rather than turning the page into a general Vulkan tutorial.
