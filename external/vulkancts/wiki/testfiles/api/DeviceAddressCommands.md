## Overview

**Core question:** Do the `VK_KHR_device_address_commands` entry points correctly handle buffer-device-address-based copy, vertex/index binding, and memory-range barrier operations when ranges are partially bound or when stride state crosses multiple command variants?

[`vktApiDeviceAddressCommandsTests.cpp`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L1) is the implementation source for the `api.device_address` test family. The family is registered only when `CTS_USES_VULKANSC` is not defined ([vktApiTests.cpp#L128-L137](../../../modules/vulkan/api/vktApiTests.cpp#L128-L137)).

- Test category: `api`.
- Test family: `device_address`, created by [`createDeviceAddressCommandsTests()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L926-L949).
- Intermediate node: `misc`, the only direct child of `device_address`.
- Test case leaves (six), all under `misc`: `copy_to_memory_with_unbound_ranges`, `copy_from_memory_with_unbound_ranges`, `use_all_vertex_index_binds`, `basic_set_stride`, `complex_set_stride`, `memory_range_barrier`.

The family splits into three behavioral clusters. Two leaves exercise `vkCmdCopyMemoryKHR` against sparse buffers with one bound chunk. Three leaves exercise the address-form vertex/index binding commands (`vkCmdBindVertexBuffers3KHR` and `vkCmdBindIndexBuffer3KHR`) and the `setStride` toggle. One leaf exercises `VkMemoryRangeBarrierKHR` between two compute dispatches.

## Background Knowledge

- `VK_KHR_device_address_commands` provides address-form variants of buffer copy, vertex/index binding, and pipeline barrier commands. These variants take `VkDeviceAddress` ranges directly instead of `VkBuffer` plus offset, allowing partially bound sparse memory regions, dynamic stride state, and address-scoped barriers.
- Sparse buffer binding binds memory to a buffer in chunks; some address ranges of the buffer may have no memory backing. The bound chunks are addressed by their offset within the buffer's device address range.
- `VkMemoryRangeBarrierKHR` is a synchronization2 structure that scopes a `vkCmdPipelineBarrier2` dependency to a specific `{deviceAddress, size}` range instead of a `VkBuffer` range, with a `VkAddressCommandFlagsKHR` flag for the intended usage.

## Registration Hierarchy

```text
api.device_address
└── misc
```

The `device_address` test family is registered under the `api` test category in [`createApiTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L86-L142), inside `#ifndef CTS_USES_VULKANSC`. The only intermediate node is `misc`, created by [`new tcu::TestCaseGroup(testCtx, "misc")`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L929-L929). The six test case leaves are added through the [`caseVect`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L931-L938) loop and appear in the mustpass file at [`api.txt#L269223-L269228`](../../../mustpass/main/vk-default/api.txt#L269223-L269228).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test case leaf | `copy_to_memory_with_unbound_ranges`, `copy_from_memory_with_unbound_ranges`, `use_all_vertex_index_binds`, `basic_set_stride`, `complex_set_stride`, `memory_range_barrier` | selects which device-address command path is exercised | [`caseVect`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L931-L938) |
| Test mode enum | `COPY_TO_MEMORY_WITH_UNBOUND_RANGES`, `COPY_FROM_MEMORY_WITH_UNBOUND_RANGES`, `USE_ALL_VERTEX_INDEX_BINDS`, `BASIC_SET_STRIDE`, `COMPLEX_SET_STRIDE`, `MEMORY_RANGE_BARRIER` | selects which `TestInstance` subclass is constructed for each leaf | [`enum class CommandFlagTestMode`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L41-L52) |
| Sparse copy region size | `512u` bytes via `m_copyRegion{0u, 0u, 512u}` | bytes copied by `vkCmdCopyMemoryKHR`; the dense side is 512 bytes, the sparse side is `1<<18` bytes | [`BufferAddressCommandFlagsTestInstance` constructor](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L93-L131) |
| Sparse single-chunk binding | `m_useSingleChunk = true`; only the second chunk is bound | leaves the first chunk's address range unbacked; the copy targets the bound chunk at offset = `m_chunkSize` | [`bindBufferMemory()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L269-L324) |
| Copy fill value | `253` (`uint8_t`) | sentinel byte written to the source and expected at every byte of the destination after copy | [`iterate()` fill and clear](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L166-L172) |
| Vertex/index buffer count | 3 for `use_all_vertex_index_binds`, 2 for `basic_set_stride`, 6 for `complex_set_stride` | number of vertex buffers exercised; size of `m_unusedVertexFloats` | [`VertexIndexBindingTestInstance` constructor](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L363-L383) |
| Memory-range barrier dispatch geometry | `groupCount = 16`, `outputOffset = 16` bytes, `outputSize = 64` bytes | first dispatch writes `v[i] = i` for `i` in `[0, 16)` at non-zero offset; second dispatch adds 3 | [`MemoryRangeBarrierBetweenOperationsTestInstance::iterate()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L713-L826) |

## Behavior Parameters

The primary behavioral axis is the test case leaf. The six leaves cluster into three behavioral groups based on the device-address command mechanism they exercise.

### Address-based sparse copy cluster

These two leaves exercise `vkCmdCopyMemoryKHR` against a sparse buffer with one bound chunk. The other side of the copy is a dense buffer with the same 512-byte size.

#### `copy_to_memory_with_unbound_ranges` — copy into a sparse destination with one bound chunk

A dense 512-byte source is filled with `253`. A sparse `1<<18`-byte destination is created with `VK_BUFFER_CREATE_SPARSE_BINDING_BIT | VK_BUFFER_CREATE_SPARSE_RESIDENCY_BIT`; only its second chunk (offset = `m_chunkSize`) is bound. The destination address range covers the bound chunk, and `m_dstCommandFlag = VK_ADDRESS_COMMAND_UNKNOWN_STORAGE_BUFFER_USAGE_BIT_KHR` is set on the destination side. After `vkCmdCopyMemoryKHR`, every byte of the destination's bound chunk must equal `253`.

Paired with `copy_from_memory_with_unbound_ranges`; the sparse-buffer role moves to the source side and the address-flag side flips.

#### `copy_from_memory_with_unbound_ranges` — copy from a sparse source with one bound chunk

A sparse `1<<18`-byte source has only its second chunk bound; that chunk is populated from a staging buffer with `253`. The destination is a dense 512-byte buffer. After `vkCmdCopyMemoryKHR`, every byte of the destination must equal `253`.

Paired with `copy_to_memory_with_unbound_ranges`; the sparse-buffer role moves to the destination side.

### Vertex/index buffer address binding cluster

These three leaves exercise address-form vertex/index binding commands and the `setStride` toggle in `VkBindVertexBuffer3InfoKHR`. All three render quads and verify the red-channel occupancy pattern.

#### `use_all_vertex_index_binds` — exercise all three generations of vertex/index binding commands

Three vertex buffers and three index buffers are allocated with `VK_BUFFER_USAGE_SHADER_DEVICE_ADDRESS_BIT`. Three quads are drawn, each using a different command generation:
- `vkCmdBindVertexBuffers` + `vkCmdBindIndexBuffer`
- `vkCmdBindVertexBuffers2` + `vkCmdBindIndexBuffer2`
- `vkCmdBindVertexBuffers3KHR` + `vkCmdBindIndexBuffer3KHR`

Index buffers use distinct offsets (zero for the first draw, non-zero for the others) so the wrong buffer would produce visibly wrong geometry. The rendered image's red channel must show the expected red/black interleaved pattern across all three quads.

Establishes the baseline that the three command generations are behaviorally equivalent; `basic_set_stride` and `complex_set_stride` then test stride-state interactions.

#### `basic_set_stride` — toggle `setStride` between two `vkCmdBindVertexBuffers3KHR` calls

Two vertex buffers with the same stride (24 bytes per vertex) are bound in sequence. The first call sets `setStride = true` with `addressRange.stride = 24`. The second call sets `setStride = false` with `addressRange.stride = 0`. The test verifies that the previous stride is preserved when `setStride = false`, so both draws render the quad correctly.

Validates the `setStride` boolean semantics in isolation; `complex_set_stride` then exercises the same semantics across mixed command variants.

#### `complex_set_stride` — interleave `vkCmdSetVertexInputEXT`, `vkCmdBindVertexBuffers2`, and `vkCmdBindVertexBuffers3KHR`

Six vertex buffers with three distinct strides (`strideA`, `strideB`, `strideC`) are bound in sequence across six draws:
1. `vkCmdSetVertexInputEXT` sets stride to `strideA`.
2. `vkCmdBindVertexBuffers2` sets stride to `strideB`.
3. `vkCmdBindVertexBuffers3KHR` with `setStride = true` sets stride to `strideC`.
4. `vkCmdBindVertexBuffers2` sets stride back to `strideB`.
5. `vkCmdSetVertexInputEXT` sets stride back to `strideA`.
6. `vkCmdBindVertexBuffers3KHR` with `setStride = false` and `addressRange.stride = 0`; the previously set `strideA` must be preserved.

The final draw validates that `setStride = false` preserves the most recent stride, regardless of which command family set it.

### Memory-range barrier cluster

#### `memory_range_barrier` — `VkMemoryRangeBarrierKHR` between two compute dispatches

A storage buffer with `VK_BUFFER_USAGE_SHADER_DEVICE_ADDRESS_BIT` is created with a non-zero `outputOffset = 16` bytes and `outputSize = 64` bytes (16 `uint32_t` elements). The first compute dispatch writes `v[i] = i` for `i` in `[0, 16)`. A `VkMemoryRangeBarrierKHR` covering `{outputBufferAddress + outputOffset, outputSize}` is inserted via `vkCmdPipelineBarrier2`. The barrier transitions `VK_ACCESS_2_SHADER_STORAGE_WRITE_BIT` → `VK_ACCESS_2_SHADER_STORAGE_READ_BIT` and carries `VK_ADDRESS_COMMAND_STORAGE_BUFFER_USAGE_BIT_KHR`. The second dispatch reads and adds 3 to each element. A second barrier transitions to `VK_ACCESS_2_HOST_READ_BIT`. The host verifies `bufferPtr[i] == i + 3` for all `i` in `[0, 16)`.

The non-zero `outputOffset` deliberately exercises offset-aware barrier scoping.

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.api.device_address.misc.memory_range_barrier
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `MEMORY_RANGE_BARRIER` | Selects the address-scoped synchronization leaf and its two compute stages, `comp0` and `comp1`. |
| `groupCount = 16`, `outputOffset = 16`, `outputSize = 64` | The producer and consumer each cover 16 `uint` elements, while the barrier begins at a deliberately non-zero buffer offset. |
| First dispatch `(16, 1, 1)`; second dispatch `(1, 16, 1)` | `comp0` indexes `gl_WorkGroupID.x`, while `comp1` indexes `gl_WorkGroupID.y`, so both stages visit the same 16-element range. |

#### Purpose

This representative tests whether an address-scoped `VkMemoryRangeBarrierKHR` makes the first compute dispatch's storage writes visible to the second dispatch's storage reads over the exact `{outputBufferAddress + outputOffset, outputSize}` range. The host expects the producer's `v[i] = i` values to become `i + 3` after the consumer dispatch.

#### Structural Design

| Phase | Dispatch geometry | Shader access | Synchronization or observation |
|-------|-------------------|---------------|--------------------------------|
| Produce | `vkCmdDispatch(16, 1, 1)` | `comp0`: write `v[gl_WorkGroupID.x] = gl_WorkGroupID.x` | `VK_ACCESS_2_SHADER_STORAGE_WRITE_BIT` is the source access of the address-range barrier. |
| Consume | `vkCmdDispatch(1, 16, 1)` | `comp1`: read, add 3, and write `v[gl_WorkGroupID.y]` | The barrier makes the producer writes visible as shader-storage reads. |
| Host check | CPU reads the 16 `uint` values at offset 16 | Requires `bufferPtr[i] == i + 3` | A second barrier changes the destination access to `VK_ACCESS_2_HOST_READ_BIT_KHR`. |

#### Shader Code

##### Producer (`comp0`) Shader

```glsl
#version 450
/// One invocation per x workgroup writes its index into the address-ranged buffer.
layout (local_size_x = 1) in;
/// The host descriptor binds the 64-byte output range at binding 0 with a 16-byte buffer offset.
layout(binding = 0) writeonly buffer Output {
    uint v[];
};
void main (void) {
    v[gl_WorkGroupID.x] = gl_WorkGroupID.x;
}
```

##### Consumer (`comp1`) Shader

```glsl
#version 450
/// One invocation per y workgroup reads the producer result and adds the expected increment.
layout (local_size_x = 1) in;
/// This read/write declaration consumes the same binding-0 range after the memory-range barrier.
layout(binding = 0) buffer Output {
    uint v[];
};
void main (void) {
    v[gl_WorkGroupID.y] += 3;
}
```

#### Additional Info

- `BufferAddressCommandTestCase::initPrograms()` emits `comp0` and `comp1` only for `MEMORY_RANGE_BARRIER`; the host creates both compute pipelines from those named modules ([`initPrograms()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L865-L910), [`iterate()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L750-L756)).
- The descriptor is binding 0 and covers `outputOffset = 16` through `outputSize = 64`; the shaders therefore use a runtime array whose index 0 corresponds to the offset range, not the beginning of the allocation ([`iterate()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L720-L743)).
- The producer uses `gl_WorkGroupID.x` because its dispatch varies x, whereas the consumer uses `gl_WorkGroupID.y` because its dispatch varies y; this is a deliberate host/shader geometry pairing ([`iterate()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L780-L794)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Test leaf / mode | Only `MEMORY_RANGE_BARRIER` emits `comp0` and `comp1`; the vertex/index leaves emit `vert` and `frag`, while the copy leaves emit no shader source in this builder. | [`initPrograms()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L865-L910) |
| Dispatch geometry | The two fixed dispatch shapes select the work-group coordinate used by each stage: x for `comp0`, y for `comp1`; changing the geometry without changing the shader index would alter coverage. | [`iterate()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L718-L723), [`iterate()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L782-L789) |
| Output range | The shader declarations stay fixed, while host-side `outputOffset` and `outputSize` determine which descriptor/barrier range the runtime array addresses. | [`iterate()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L720-L743), [`iterate()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L758-L767) |

#### SPIR-V

##### Producer (`comp0`) Shader

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
; Bound: 26
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_WorkGroupID
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpName %main "main"
               OpName %Output "Output"
               OpMemberName %Output 0 "v"
               OpName %_ ""
               OpName %gl_WorkGroupID "gl_WorkGroupID"
               OpDecorate %_runtimearr_uint ArrayStride 4
               OpDecorate %Output BufferBlock
               OpMemberDecorate %Output 0 NonReadable
               OpMemberDecorate %Output 0 Offset 0
               OpDecorate %_ NonReadable
               OpDecorate %_ Binding 0
               OpDecorate %_ DescriptorSet 0
               OpDecorate %gl_WorkGroupID BuiltIn WorkgroupId
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_runtimearr_uint = OpTypeRuntimeArray %uint
     %Output = OpTypeStruct %_runtimearr_uint
%_ptr_Uniform_Output = OpTypePointer Uniform %Output
          %_ = OpVariable %_ptr_Uniform_Output Uniform
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_WorkGroupID = OpVariable %_ptr_Input_v3uint Input
     %uint_0 = OpConstant %uint 0
%_ptr_Input_uint = OpTypePointer Input %uint
%_ptr_Uniform_uint = OpTypePointer Uniform %uint
     %uint_1 = OpConstant %uint 1
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
         %18 = OpAccessChain %_ptr_Input_uint %gl_WorkGroupID %uint_0
         %19 = OpLoad %uint %18
         %20 = OpAccessChain %_ptr_Input_uint %gl_WorkGroupID %uint_0
         %21 = OpLoad %uint %20
         %23 = OpAccessChain %_ptr_Uniform_uint %_ %int_0 %19
               OpStore %23 %21
               OpReturn
               OpFunctionEnd
```

</details>

##### Consumer (`comp1`) Shader

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
; Bound: 27
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_WorkGroupID
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpName %main "main"
               OpName %Output "Output"
               OpMemberName %Output 0 "v"
               OpName %_ ""
               OpName %gl_WorkGroupID "gl_WorkGroupID"
               OpDecorate %_runtimearr_uint ArrayStride 4
               OpDecorate %Output BufferBlock
               OpMemberDecorate %Output 0 Offset 0
               OpDecorate %_ Binding 0
               OpDecorate %_ DescriptorSet 0
               OpDecorate %gl_WorkGroupID BuiltIn WorkgroupId
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_runtimearr_uint = OpTypeRuntimeArray %uint
     %Output = OpTypeStruct %_runtimearr_uint
%_ptr_Uniform_Output = OpTypePointer Uniform %Output
          %_ = OpVariable %_ptr_Uniform_Output Uniform
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_WorkGroupID = OpVariable %_ptr_Input_v3uint Input
     %uint_1 = OpConstant %uint 1
%_ptr_Input_uint = OpTypePointer Input %uint
     %uint_3 = OpConstant %uint 3
%_ptr_Uniform_uint = OpTypePointer Uniform %uint
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
         %18 = OpAccessChain %_ptr_Input_uint %gl_WorkGroupID %uint_1
         %19 = OpLoad %uint %18
         %22 = OpAccessChain %_ptr_Uniform_uint %_ %int_0 %19
         %23 = OpLoad %uint %22
         %24 = OpIAdd %uint %23 %uint_3
         %25 = OpAccessChain %_ptr_Uniform_uint %_ %int_0 %19
               OpStore %25 %24
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

### Sparse-buffer copy leaves

- The host creates a dense source or destination buffer (512 bytes) and a sparse buffer (`1<<18` bytes) with `VK_BUFFER_CREATE_SPARSE_BINDING_BIT | VK_BUFFER_CREATE_SPARSE_RESIDENCY_BIT`.
- `bindBufferMemory()` binds only one chunk of the sparse buffer at offset = `m_chunkSize` (the second chunk). The first chunk's address range is left unbacked.
- The source side is filled with `253` and the destination side is initialized to `0`. For `copy_from_memory_with_unbound_ranges`, the staging buffer (filled with `253`) is uploaded to the sparse source's bound chunk via `vkCmdCopyBuffer` before `vkCmdCopyMemoryKHR`; for `copy_to_memory_with_unbound_ranges`, `vkCmdCopyMemoryKHR` populates the sparse destination's bound chunk directly from the dense source.
- `vkCmdCopyMemoryKHR` copies 512 bytes between the dense buffer and the sparse buffer's bound chunk, addressed by `VkDeviceAddressRangeKHR`.
- For sparse destinations, the result is copied back to the staging buffer; for sparse sources, the dense destination is read directly.
- The host scans every byte of the result and requires all 512 bytes to equal `253` ([`iterate()` byte scan](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L239-L246)).

### Vertex/index binding leaves

- The host creates a `64×8` `R8G8B8A8_UNORM` color attachment backed by a host-visible buffer.
- Vertex buffers (and index buffers when `m_useIndexBuffers`) are allocated with `VK_BUFFER_USAGE_SHADER_DEVICE_ADDRESS_BIT` and filled with quad positions, offset horizontally per buffer.
- Two graphics pipelines are created: a regular pipeline with static stride 8 and a dynamic-state pipeline with `VK_DYNAMIC_STATE_VERTEX_INPUT_BINDING_STRIDE` (and conditionally `VK_DYNAMIC_STATE_VERTEX_INPUT_EXT`).
- The render pass records the appropriate draw sequence per leaf and copies the color image to the host-visible buffer.
- The host verifies the red-channel occupancy pattern at `imageExtent.height / 2`: every even-indexed fragment pair should be 255 (red quad), every odd-indexed pair should be 0 (gap between quads) ([`iterate()` verification loop](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L537-L555)).

### Memory-range barrier leaf

- The host creates a storage buffer with `outputOffset = 16` and `outputSize = 64`, and a descriptor set that binds the storage buffer at that offset.
- Two compute pipelines are created from `comp0` (writes `v[i] = i`) and `comp1` (adds 3 per element).
- The command buffer records: `vkCmdBindDescriptorSets`, `vkCmdBindPipeline` + `vkCmdDispatch` (16 work groups), `vkCmdPipelineBarrier2` with `VkMemoryRangeBarrierKHR`, `vkCmdBindPipeline` + `vkCmdDispatch` (16 work groups), second `vkCmdPipelineBarrier2` to host.
- Submission uses `vkQueueSubmit2` and `vkQueueWaitIdle`.
- The host invalidates the allocation and verifies `bufferPtr[i] == i + 3` for all `i` in `[0, 16)` ([`iterate()` verification loop](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L811-L823)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `copy_to_memory_with_unbound_ranges` | Sparse-buffer chunk address handling in `vkCmdCopyMemoryKHR`; address-range offset handling when only the second chunk is bound; `VK_ADDRESS_COMMAND_UNKNOWN_STORAGE_BUFFER_USAGE_BIT_KHR` flag handling. |
| `copy_from_memory_with_unbound_ranges` | Sparse-buffer chunk address handling in `vkCmdCopyMemoryKHR`; address-range offset handling when reading from a sparse source with one bound chunk. |
| `use_all_vertex_index_binds` | Address-form binding-command equivalence across `vkCmdBindVertexBuffers`/`2`/`3KHR` and `vkCmdBindIndexBuffer`/`2`/`3KHR`; index buffer offset handling. |
| `basic_set_stride` | `setStride` boolean handling in `VkBindVertexBuffer3InfoKHR`; stride preservation when `setStride = false`. |
| `complex_set_stride` | Stride precedence across `vkCmdSetVertexInputEXT`, `vkCmdBindVertexBuffers2`, and `vkCmdBindVertexBuffers3KHR`; stride preservation across mixed command variants when `setStride = false`. |
| `memory_range_barrier` | `VkMemoryRangeBarrierKHR` synchronization scope; address-range barrier not waiting for prior writes or not releasing to subsequent reads at non-zero offset. |

All leaves share a common dependency on `vkGetBufferDeviceAddress` returning correct buffer device addresses. A failure in address query would propagate to all leaves.

### Cause Analysis

#### Sparse-buffer chunk address handling

**Possible failure symptoms:** After `vkCmdCopyMemoryKHR` against a sparse buffer with one bound chunk, the destination bytes do not all equal `253`. Either zero bytes are written (the bound chunk was not the actual copy target), the wrong region is written (the unbound first chunk was targeted instead), or only a partial sub-range is filled (the address range extends past the bound chunk).

**Possible implementation causes:** The driver translates the destination address range to the wrong memory offset (e.g., ignores `m_copyRegion.dstOffset = m_chunkSize` and writes to the unbound first chunk); sparse binding state is not correctly consulted by the address-form copy path; the `VK_ADDRESS_COMMAND_UNKNOWN_STORAGE_BUFFER_USAGE_BIT_KHR` flag is misinterpreted and changes the write target or mask. Source-level investigation into the driver's `vkCmdCopyMemoryKHR` sparse-buffer address translation is needed to confirm a specific cause; this analysis is grounded in what the test verifies, not in a specific driver bug.

#### Address-based vertex/index binding equivalence

**Possible failure symptoms:** The rendered image's red-channel occupancy pattern is wrong. Some quads do not appear (the clear color survives where a quad was expected), appear in the wrong horizontal position (overlapping or shifted), or are stretched or compressed horizontally.

**Possible implementation causes:** One of the address-form binding-command variants records a wrong vertex or index buffer device address; applies an incorrect offset (the test deliberately uses non-zero index buffer offsets in `use_all_vertex_index_binds` to distinguish buffers); or does not honor `addressRange.size`. Source-level investigation is needed to identify which specific variant diverges; the test isolates each variant to a separate draw, so the failing draw narrows the suspect command.

#### Stride state precedence and preservation

**Possible failure symptoms:** One or more draws in `basic_set_stride` or `complex_set_stride` produce wrong geometry, typically stretched, compressed, or missing quads, because the implementation applied a stride other than the one specified by the most recent state-setting command.

**Possible implementation causes:** The `setStride` boolean in `VkBindVertexBuffer3InfoKHR` is mishandled (e.g., the address-range stride is applied when `setStride = false`, or ignored when `setStride = true`); `vkCmdBindVertexBuffers2`'s `pStrides` argument does not override the previously set dynamic stride; `vkCmdSetVertexInputEXT`'s stride does not establish the baseline that `setStride = false` should preserve; the dynamic-state pipeline's `VK_DYNAMIC_STATE_VERTEX_INPUT_BINDING_STRIDE` or `VK_DYNAMIC_STATE_VERTEX_INPUT_EXT` flag is mishandled. Source-level investigation is needed to identify which command's stride state is mis-persisted; the failing draw indicates which transition is broken.

#### Memory-range barrier synchronization

**Possible failure symptoms:** After both dispatches complete, `bufferPtr[i] != i + 3`. Common patterns: all-zero (the first dispatch did not write, or the barrier flushed writes too early); `v[i] == i` (the second dispatch did not run, or read stale data); partial corruption (the barrier does not cover the full `{outputBufferAddress + outputOffset, outputSize}` range).

**Possible implementation causes:** `VkMemoryRangeBarrierKHR` does not correctly wait for `VK_ACCESS_2_SHADER_STORAGE_WRITE_BIT` from the first dispatch before `VK_ACCESS_2_SHADER_STORAGE_READ_BIT` in the second; the barrier's address range is incorrectly scoped (e.g., starts at the buffer base rather than `outputBufferAddress + outputOffset`); the `VK_ADDRESS_COMMAND_STORAGE_BUFFER_USAGE_BIT_KHR` flag is misinterpreted and the barrier is dropped. The non-zero `outputOffset = 16` deliberately exercises offset-aware barrier scoping. Source-level investigation into the driver's barrier submission is needed to confirm the specific cause.

## Case Pruning

### Requirement-based pruning

- All leaves require `VK_KHR_device_address_commands` ([`checkSupport()` at L851](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L851)).
- `copy_to_memory_with_unbound_ranges` and `complex_set_stride` additionally require `VK_EXT_vertex_input_dynamic_state` ([`checkSupport()` at L852-L853](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L852-L853)).
- `memory_range_barrier` additionally requires `VK_KHR_synchronization2` ([`checkSupport()` at L854-L855](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L854-L855)).
- The two copy leaves additionally require `DEVICE_CORE_FEATURE_SPARSE_BINDING` and `DEVICE_CORE_FEATURE_SPARSE_RESIDENCY_BUFFER` ([`checkSupport()` at L857-L862](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L857-L862)).
- The whole `device_address` family is registered only when `CTS_USES_VULKANSC` is not defined, so Vulkan SC builds skip the family entirely ([vktApiTests.cpp#L128-L137](../../../modules/vulkan/api/vktApiTests.cpp#L128-L137)).

### Design-based pruning

- The two copy leaves exercise only one chunk of the sparse buffer (`m_useSingleChunk = true`). Multi-chunk configurations and partially bound multi-region scenarios are out of scope; the test focuses on the single-bound-chunk edge case.
- `basic_set_stride` exercises exactly two `setStride` transitions. Deeper stride-state transition sequences are deferred to `complex_set_stride`.
- The `memory_range_barrier` leaf uses a single barrier between two dispatches. Multi-barrier chaining and queue-family ownership transfer scenarios are out of scope.

## Key Takeaways

- The `device_address` family is the CTS coverage for `VK_KHR_device_address_commands`: address-form copy, address-form vertex/index binding, and address-scoped memory-range barriers.
- The two copy leaves validate that `vkCmdCopyMemoryKHR` correctly addresses the bound chunk of a sparse buffer when the source or destination has an unbound first chunk.
- The three binding leaves validate behavioral equivalence across `vkCmdBindVertexBuffers`/`2`/`3KHR` and `vkCmdBindIndexBuffer`/`2`/`3KHR`, plus stride precedence when `vkCmdSetVertexInputEXT`, `vkCmdBindVertexBuffers2`, and `vkCmdBindVertexBuffers3KHR` interleave.
- The `setStride` boolean in `VkBindVertexBuffer3InfoKHR` controls whether the `addressRange` stride is applied; `false` preserves the previously set stride, regardless of which command family set it.
- The `memory_range_barrier` leaf validates that `VkMemoryRangeBarrierKHR` provides correct `VK_ACCESS_2_SHADER_STORAGE_WRITE_BIT` → `VK_ACCESS_2_SHADER_STORAGE_READ_BIT` synchronization for a non-zero-offset, address-scoped storage buffer region.
- The family is non-VulkanSC only; sparse-binding/residency features gate the copy leaves, and `VK_EXT_vertex_input_dynamic_state` plus `VK_KHR_synchronization2` gate specific leaves.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `createDeviceAddressCommandsTests()` | [vktApiDeviceAddressCommandsTests.cpp#L926-L949](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L926-L949) | Public entry point; creates `device_address` group and `misc` child; populates the six leaves from `caseVect`. |
| `enum class CommandFlagTestMode` | [vktApiDeviceAddressCommandsTests.cpp#L41-L52](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L41-L52) | The six test-mode values that select the `TestInstance` subclass for each leaf. |
| `BufferAddressCommandFlagsTestInstance::iterate()` | [vktApiDeviceAddressCommandsTests.cpp#L134-L247](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L134-L247) | Implementation of the two copy leaves; sparse-buffer setup, single-chunk binding, and byte-exact destination validation. |
| `BufferAddressCommandFlagsTestInstance::bindBufferMemory()` | [vktApiDeviceAddressCommandsTests.cpp#L269-L324](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L269-L324) | Sparse-memory binding implementation including `m_useSingleChunk` and the second-chunk offset behavior. |
| `VertexIndexBindingTestInstance::iterate()` | [vktApiDeviceAddressCommandsTests.cpp#L385-L562](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L385-L562) | Implementation of the three binding-command leaves; vertex/index buffer setup and image verification. |
| `VertexIndexBindingTestInstance::drawUsingAllVertexIndexBinds()` | [vktApiDeviceAddressCommandsTests.cpp#L657-L697](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L657-L697) | `use_all_vertex_index_binds` draw sequence across three command generations. |
| `VertexIndexBindingTestInstance::drawUsingBasicSetStride()` | [vktApiDeviceAddressCommandsTests.cpp#L579-L603](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L579-L603) | `basic_set_stride` draw sequence with the `setStride` toggle. |
| `VertexIndexBindingTestInstance::drawUsingComplexSetStride()` | [vktApiDeviceAddressCommandsTests.cpp#L605-L655](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L605-L655) | `complex_set_stride` interleaved stride-state sequence across three command families. |
| `MemoryRangeBarrierBetweenOperationsTestInstance::iterate()` | [vktApiDeviceAddressCommandsTests.cpp#L713-L826](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L713-L826) | Implementation of the memory-range-barrier leaf; two-dispatch compute flow with `VkMemoryRangeBarrierKHR`. |
| `BufferAddressCommandTestCase::checkSupport()` | [vktApiDeviceAddressCommandsTests.cpp#L847-L863](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L847-L863) | Per-leaf feature requirements: `VK_KHR_device_address_commands`, `VK_EXT_vertex_input_dynamic_state`, `VK_KHR_synchronization2`, sparse core features. |
| `BufferAddressCommandTestCase::initPrograms()` | [vktApiDeviceAddressCommandsTests.cpp#L865-L910](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L865-L910) | GLSL sources for the trivial vertex/fragment and compute shaders. |
| `createApiTests()` registration | [vktApiTests.cpp#L136-L136](../../../modules/vulkan/api/vktApiTests.cpp#L136-L136) | Parent registration: `apiTests->addChild(createDeviceAddressCommandsTests(testCtx))`, inside `#ifndef CTS_USES_VULKANSC`. |
| Mustpass entries | [api.txt#L269223-L269228](../../../mustpass/main/vk-default/api.txt#L269223-L269228) | The six `dEQP-VK.api.device_address.misc.*` leaves. |
