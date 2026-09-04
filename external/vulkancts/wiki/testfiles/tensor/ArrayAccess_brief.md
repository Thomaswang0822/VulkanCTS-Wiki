# Understanding Brief: tensor.array_access

## One-Sentence Test Purpose

This test checks whether compute-shader `tensorReadARM` and `tensorWriteARM` correctly transfer a bounded array of adjacent tensor elements for supported integer formats, ranks, tilings, and array lengths.

## Background Knowledge

### Tensor coordinates and array operations

A tensor has one coordinate per dimension. `OpTensorReadARM` reads one or more consecutive elements from a coordinate, while `OpTensorWriteARM` writes one or more elements. Vulkan validates every coordinate against the tensor dimensions. An invalid read produces a replacement value, while an invalid write has no effect; this test avoids invalid starting coordinates and clips the final run instead. See [Tensor Operations](../../../../vulkan-docs/src/chapters/VK_ARM_tensors/tensorops.adoc#tensors).

Why it matters here:
- The innermost dimension is divided into runs of 2, 3, or 4 elements, so a dispatch invocation can cover a partial run at the boundary.
- The other dimensions are reconstructed from the second global invocation coordinate, which tests indexing through a rank-4 tensor rather than only a flat tensor.

### Packed and optimal tensor storage

Linear tensors may have packed host data, while optimal tensors use implementation-defined storage. Tensor views and tensor copy operations keep the shader from depending on physical offsets. The host therefore uses tensor copies for optimal tensors and compares logical element values after transfer.

## One Concrete Example

For `dEQP-VK.tensor.array_access.r32_uint_optimal_shape_13_17_19_23_array_read_array_size_2`, the tensor has 96,577 `uint` elements in shape `{13, 17, 19, 23}`. The generator declares `tensorARM<uint, 4>`, queries all four sizes, and assigns two consecutive innermost elements to each invocation. An invocation with `gl_GlobalInvocationID = (0, 0, 0)` reads coordinates `(0, 0, 0, 0)` and stores the returned pair at `data[0]` and `data[1]`. The final invocation in a run may store only one element when the coordinate plus the loop index reaches 23.

The example uses a conceptual excerpt of the generated shader; the final page carries the full generated GLSL and a compiler-produced SPIR-V artifact.

```glsl
layout(set=0, binding = 0) uniform tensorARM<uint, 4> tens;
layout(set=0, binding = 1, std430) buffer _buff { uint data[]; };
const uint offset_x = 2 * gl_GlobalInvocationID.x;
const uint offset_y = gl_GlobalInvocationID.y;
const uint coord_0 = offset_y / (1 * size_d1 * size_d2) % size_d0;
const uint coord_1 = offset_y / (1 * size_d2) % size_d1;
const uint coord_2 = offset_y / 1 % size_d2;
const uint coord_3 = offset_x;
tensorReadARM(tens, uint[](coord_0, coord_1, coord_2, coord_3), tmp);
```

## End-to-End Test Flow

```text
[host] choose an integer format, fixed rank-4 shape {13, 17, 19, 23}, linear or optimal tiling, array length 2/3/4, and array_read or array_write
[host] resolve array size 0 as the device-supported maximum
[host] create the tensor view and a host-visible storage buffer
[host] initialize the tensor and buffer for the selected direction
[host] generate and compile the compute shader
[host] bind the tensor view at binding 0 and the storage buffer at binding 1
[host] dispatch ceil(23 / array length) by (13*17*19) workgroups
[device] query tensor dimensions and compute the rank-4 coordinate
[device] read an array from the tensor, or read an array from the buffer and write it to the tensor
[device] write/read the participating storage object
[host] apply the direction-specific barrier, wait, and invalidate host memory
[host] download the tensor when the shader wrote it, then compare every logical element with the buffer
[host] pass only when all 96,577 element comparisons match
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `genShaderArrayAccess(rank, variant, format, arraySize)` emits GLSL with the tensor and explicit arithmetic-type extensions, a one-by-one compute local size, tensor rank/type declarations, dimension queries, coordinate arithmetic, and the selected read/write branch.
- `arraySize == 0` is a runtime maximum case. The test obtains the smaller of `maxTensorShaderAccessSize / elementSize` and `maxTensorShaderAccessArrayLength` before generating the shader.
- The representative page walkthrough uses the default source-collection target, SPIR-V 1.0, and a validated disassembly.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Tensor view of the test tensor | yes | binding 0 as `VK_DESCRIPTOR_TYPE_TENSOR_ARM` | read or written by shader | yes, directly for linear or through a linear staging tensor for optimal | Carries format, rank, shape, and tiling semantics. |
| Storage buffer | yes, host-visible | binding 1 as `VK_DESCRIPTOR_TYPE_STORAGE_BUFFER` | written by `array_read` or read by `array_write` | yes | Supplies the comparison side and the shader's linear array. |
| Local shader array `tmp[arraySize]` | no, shader-local | no | temporary read/write values | no | Holds one tensor-operation array result or input. |
| Linear staging tensor (optimal only) | yes | used by tensor copy commands | transfer source/destination | yes through download | Converts optimal storage to a host-readable logical layout. |

## What Is Checked

- `array_read` fills the tensor and clears the buffer, reads arrays from the tensor, and writes them to the buffer.
- `array_write` clears the tensor and fills the buffer, reads arrays from the buffer, and writes them to the tensor.
- The host compares each logical element with `tensorData[element_idx] != bufferMemory[element_idx]`. A mismatch reports the index and both values; only an entirely matching comparison returns `Tensor test succeeded`.
- Linear cases use the tensor directly. Optimal cases copy a linear tensor into the optimal tensor before dispatch and copy it back after a tensor memory barrier.

## Behavior Parameter Identification

> **Behavior parameter:** access variant
>
> **Candidate values:** `array_read`, `array_write`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `array_read` | Tensor read-array lowering, coordinate calculation, local-array handling, storage-buffer writes, or tensor-to-host initialization/copy path |
| `array_write` | Tensor write-array lowering, storage-buffer reads, local-array handling, coordinate calculation, or tensor readback/copy path |

## Important Variations and Special Cases

- The registered scalar formats are `VK_FORMAT_R8_UINT`, `VK_FORMAT_R8_SINT`, `VK_FORMAT_R16_UINT`, `VK_FORMAT_R16_SINT`, `VK_FORMAT_R32_UINT`, `VK_FORMAT_R32_SINT`, `VK_FORMAT_R64_UINT`, and `VK_FORMAT_R64_SINT`. The C++ template selects the matching host type.
- Every format uses the same rank-4 shape `{13, 17, 19, 23}` and both `VK_TENSOR_TILING_LINEAR_ARM` and `VK_TENSOR_TILING_OPTIMAL_ARM`.
- Array lengths 2, 3, and 4 expose different run alignment. The generator clips the final run with `coord_3 + i < size_d3`.
- The `max` leaf uses implementation limits: the minimum of `maxTensorShaderAccessArrayLength` and `maxTensorShaderAccessSize` divided by element size.
- Optimal tensors add a linear tensor and tensor-copy barriers. This changes resource movement, not shader array semantics.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Registration root and direct child | [vktTensorTests.cpp#L37-L47](../../modules/vulkan/tensor/vktTensorTests.cpp#L37-L47) | Places `array_access` under `tensor`. |
| Test construction and matrix | [vktTensorArrayAccess.cpp#L712-L777](../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L712-L777) | Defines formats, tilings, shape, array lengths, variants, and max cases. |
| Shader generator | [vktTensorArrayAccessShaders.cpp#L40-L116](../../modules/vulkan/tensor/shaders/vktTensorArrayAccessShaders.cpp#L40-L116) | Emits declarations, coordinate indexing, and read/write branches. |
| Support gates | [vktTensorArrayAccess.cpp#L134-L168](../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L134-L168) | Checks extension, rank, shader access, format/tiling, array length, and byte-size limits. |
| Runtime and linear verification | [vktTensorArrayAccess.cpp#L330-L495](../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L330-L495) | Shows setup, dispatch, barriers, readback, and comparison. |
| Runtime and optimal verification | [vktTensorArrayAccess.cpp#L498-L709](../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L498-L709) | Shows staging tensor copies and synchronization. |
| Registered cases | [tensor.txt#L1-L128](../../mustpass/main/vk-default/tensor.txt#L1-L128) | Confirms the 128 `array_access` leaves. |
| Tensor read/write semantics | [tensorops.adoc#L8-L24](../../../../vulkan-docs/src/chapters/VK_ARM_tensors/tensorops.adoc#L8-L24) | Defines tensor operations. |

## Questions / Risk Points for User Audit

- Does the distinction between an array returned or consumed by a tensor operation and a descriptor array read clearly?
- Is the rank-4 coordinate reconstruction understandable without treating `gl_GlobalInvocationID.y` as a tensor coordinate by itself?
- Is the optimal-tensor staging path detailed enough to explain why the shader remains unchanged?
- Are the two failure rows specific enough to separate shader behavior from host readback failures?

## Conversion Notes for Final Wiki Page

- Keep the concise coordinate explanation in `Background Knowledge` and move the concrete shape example to the behavior or shader section.
- Preserve the exact `Failure Cause Mapping` table unchanged in the final page.
- Write `Cause Analysis` separately, using the comparison message and direction-specific barriers.
- Use the representative `r32_uint` optimal `array_read` case and the generated compute shader as the single walkthrough; cover other formats, array lengths, and `array_write` in the variation summary.
