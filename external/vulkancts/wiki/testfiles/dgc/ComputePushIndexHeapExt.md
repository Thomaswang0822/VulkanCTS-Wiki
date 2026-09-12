## Overview

**Core question:** Does the push index that each DGC sequence supplies select exactly the descriptor-heap slot, and therefore exactly the storage buffer, that the compute write is expected to hit?

This page covers `dgc.ext.compute.push_index_heap`, implemented by [vktDGCComputePushIndexHeapTestsExt.cpp](../../../modules/vulkan/device_generated_commands/vktDGCComputePushIndexHeapTestsExt.cpp#L112-L323). The family registers one test case leaf, `stage_compute`, that combines three EXT mechanisms on a single compute pipeline:

- a resource descriptor heap that holds one storage-buffer descriptor per slot, written from the host with `writeResourceDescriptorsEXT`;
- a descriptor-heap compute pipeline (no pipeline layout) whose set `0` / binding `0` is mapped to the heap through `VK_DESCRIPTOR_MAPPING_SOURCE_HEAP_WITH_PUSH_INDEX_EXT`, so the slot it resolves to comes from a pushed 32-bit index;
- a DGC command stream in which each sequence pushes its own index through a `PUSH_DATA_EXT` token and then dispatches one work group.

Sixteen sequences push indices `0..15` and dispatch. Each compute invocation adds a fixed marker to whichever buffer its binding resolves to. The family passes only when every one of the sixteen host-visible buffers received exactly one marker on top of its slot index, which proves each pushed index routed its sequence's write to the intended heap slot.

## Background Knowledge

- **Resource descriptor heap.** A descriptor heap is a device buffer, flagged `VK_BUFFER_USAGE_DESCRIPTOR_HEAP_BIT_EXT`, that stores resource descriptors as opaque bytes at fixed strides. The host writes descriptors into it with `writeResourceDescriptorsEXT` at host-side addresses it computes from the device-reported `bufferDescriptorSize` and `bufferDescriptorAlignment`, then binds a range of it into a command buffer with `cmdBindResourceHeapEXT`. A heap range can carry a trailing reserved region sized from `minResourceHeapReservedRange`.
- **Descriptor-heap pipeline and set-binding mapping.** A compute pipeline can be created for descriptor-heap use instead of a pipeline layout: the pipeline is created with `VK_PIPELINE_CREATE_2_DESCRIPTOR_HEAP_BIT_EXT` and no layout, and a `VkShaderDescriptorSetAndBindingMappingInfoEXT` chained to the shader stage maps each set/binding to a descriptor source rather than to a bound descriptor set.
- **Push-index mapping source.** One such mapping source is `VK_DESCRIPTOR_MAPPING_SOURCE_HEAP_WITH_PUSH_INDEX_EXT`: instead of a fixed heap offset, the selected slot is supplied at draw/dispatch time by a 32-bit push value, and the mapping's `heapIndexStride`/`heapArrayStride` fields translate that value into a byte offset into the bound heap. This is the mechanism that lets a pushed number choose a resource.
- **DGC push-data token.** An indirect-commands layout maps fixed byte ranges of each sequence record to command tokens. A `PUSH_DATA_EXT` token copies bytes from the record into a push range, and a `DISPATCH_EXT` token supplies work-group counts; the pushed bytes are how the per-sequence index reaches the push-index mapping.

## Registration Hierarchy

```text
dgc.ext.compute.push_index_heap
└── stage_compute
```

The `push_index_heap` group is attached to the EXT compute branch by [vktDGCTests.cpp](../../../modules/vulkan/device_generated_commands/vktDGCTests.cpp#L97-L104). Its single leaf comes from the factory in [vktDGCComputePushIndexHeapTestsExt.cpp](../../../modules/vulkan/device_generated_commands/vktDGCComputePushIndexHeapTestsExt.cpp#L314-L323) and appears in [dgc.txt](../../../mustpass/main/vk-default/dgc.txt#L382-L382).

## Parameter Dimensions and Observed Values

The family has no generated cross-product. Its registered leaf is fixed, and a small set of compile-time constants shapes the single recorded scenario.

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Test case leaf | `stage_compute` | The only leaf; runs the compute-stage push-index routing. | [registration](../../../modules/vulkan/device_generated_commands/vktDGCComputePushIndexHeapTestsExt.cpp#L318-L320) |
| Push stage (`pushStage`) | `VK_SHADER_STAGE_COMPUTE_BIT` | Stage that owns the push range carrying the index; matches the mapping's push offset `0`. | [TestParams and token](../../../modules/vulkan/device_generated_commands/vktDGCComputePushIndexHeapTestsExt.cpp#L245-L247) |
| Slot count (`kNumSlots`) | `16` | Number of heap slots, output buffers, and generated sequences. | [constant](../../../modules/vulkan/device_generated_commands/vktDGCComputePushIndexHeapTestsExt.cpp#L55-L56) |
| Marker (`kMarker`) | `1048576` (`1 << 20`) | Value the shader adds; large enough that `slot + marker` never aliases a pre-filled slot value. | [constant](../../../modules/vulkan/device_generated_commands/vktDGCComputePushIndexHeapTestsExt.cpp#L58-L60) |
| Pushed index | `0` … `15` (one per sequence) | Per-sequence value the `PUSH_DATA_EXT` token supplies; selects the heap slot the write targets. | [command stream](../../../modules/vulkan/device_generated_commands/vktDGCComputePushIndexHeapTestsExt.cpp#L253-L262) |
| Dispatch dimensions | `1 x 1 x 1` | Every sequence dispatches a single work group with a single invocation. | [dispatch record](../../../modules/vulkan/device_generated_commands/vktDGCComputePushIndexHeapTestsExt.cpp#L259-L261) |

## Behavior Parameters

This family has no behavioral axis in the sense of a registered dimension that changes which property is exercised. It registers exactly one leaf, `stage_compute`, and the shader, dispatch shape, and heap layout are fixed for that leaf. The only per-sequence variation, the pushed index `0..15`, is the internal data that exercises one mechanism (push-index heap selection) rather than a set of alternative behaviors. A failure of `stage_compute` therefore reports a defect in that single mechanism, localized further only by which slot's buffer held the wrong value.

## Shader Analysis

The family compiles one small compute shader from a GLSL template. Its single operation (add `kMarker` to the one `uint` in a set `0` / binding `0` storage buffer) is the observable that makes heap-slot selection visible: the shader itself computes nothing meaningful, and which buffer it touches is decided entirely by the pushed index, not by any shader input. The walkthrough records the shader as the write side of the push-index experiment.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.dgc.ext.compute.push_index_heap.stage_compute
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `stage_compute` | The compute pipeline resolves set `0` / binding `0` through a descriptor heap chosen by a pushed index, so the shader's single write lands in one of sixteen candidate buffers. |
| `local_size = 1 x 1 x 1` | One invocation per work group, and every sequence dispatches `(1, 1, 1)`, so a selected buffer receives the marker exactly once. |
| `MARKER = 1048576` | The fixed addend baked into the shader; a buffer that was hit ends at `slotIndex + 1048576`. |

#### Purpose

The shader adds a fixed marker to the single word of whichever storage buffer its set `0` / binding `0` descriptor resolves to. It provides the observable write that confirms the pushed index selected the intended descriptor-heap slot.

#### Structural Design

| Phase | Source-generated operation | Result checked by the host |
|-------|----------------------------|-----------------------------|
| Slot selection (host/DGC) | `PUSH_DATA_EXT` supplies the sequence index; the push-index heap mapping routes set `0` / binding `0` to that slot's buffer. | Determines which of the sixteen buffers this dispatch touches. |
| Marker write | The single invocation executes `outBuffer.value += 1048576u`. | Adds `1048576` to the selected buffer's current value. |
| Host verification | Sequences push indices `0..15`; the host reads back all sixteen buffers. | Buffer `i` must equal `i + 1048576`. |

#### Shader Code

```glsl
#version 460
/// One invocation per workgroup, and the host dispatches (1, 1, 1) per sequence.
layout (local_size_x = 1, local_size_y = 1, local_size_z = 1) in;
/// The only interface: set 0, binding 0, resolved through the resource heap slot the pushed index selects.
layout (set = 0, binding = 0) buffer OutputBlock { uint value; } outBuffer;
/// Add the fixed marker to whichever buffer the heap index selected for this sequence.
void main (void)
{
    outBuffer.value += 1048576u;
}
```

#### Additional Info

- The source emits this shader from a `tcu::StringTemplate` and substitutes `${MARKER}` with `std::to_string(kMarker)` (`1048576`) before adding it as a compute source [initPrograms](../../../modules/vulkan/device_generated_commands/vktDGCComputePushIndexHeapTestsExt.cpp#L118-L134).
- The shader declares no push-constant block; the pushed 32-bit index is consumed by the descriptor mapping, not read as data by the shader.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Pushed index | Shader text is fixed; per sequence the host writes index `0..15` into the push-data field, and the mapping resolves binding `0` to that slot's buffer. | [command stream](../../../modules/vulkan/device_generated_commands/vktDGCComputePushIndexHeapTestsExt.cpp#L253-L262) |
| Marker value | Shader text is fixed after `${MARKER}` substitution; only the constant changes if `kMarker` changes. | [initPrograms](../../../modules/vulkan/device_generated_commands/vktDGCComputePushIndexHeapTestsExt.cpp#L126-L133) |

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
; Bound: 21
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main"
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 460
               OpName %main "main"
               OpName %OutputBlock "OutputBlock"
               OpMemberName %OutputBlock 0 "value"
               OpName %outBuffer "outBuffer"
               OpDecorate %OutputBlock BufferBlock
               OpMemberDecorate %OutputBlock 0 Offset 0
               OpDecorate %outBuffer Binding 0
               OpDecorate %outBuffer DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%OutputBlock = OpTypeStruct %uint
%_ptr_Uniform_OutputBlock = OpTypePointer Uniform %OutputBlock
  %outBuffer = OpVariable %_ptr_Uniform_OutputBlock Uniform
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%uint_1048576 = OpConstant %uint 1048576
%_ptr_Uniform_uint = OpTypePointer Uniform %uint
     %v3uint = OpTypeVector %uint 3
     %uint_1 = OpConstant %uint 1
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
         %14 = OpAccessChain %_ptr_Uniform_uint %outBuffer %int_0
         %15 = OpLoad %uint %14
         %16 = OpIAdd %uint %15 %uint_1048576
         %17 = OpAccessChain %_ptr_Uniform_uint %outBuffer %int_0
               OpStore %17 %16
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- Support is checked first through [checkSupport](../../../modules/vulkan/device_generated_commands/vktDGCComputePushIndexHeapTestsExt.cpp#L112-L116): `checkDGCExtComputeSupport(context, DGCComputeSupportType::BASIC)` requires `VK_EXT_device_generated_commands` and compute-stage DGC support, then `requireDeviceFunctionality` requires `VK_EXT_descriptor_heap`.
- The host creates sixteen host-visible, device-addressed storage buffers, each one `uint`, and pre-fills buffer `i` with `i` before flushing [buffer setup](../../../modules/vulkan/device_generated_commands/vktDGCComputePushIndexHeapTestsExt.cpp#L143-L158).
- It reads `VkPhysicalDeviceDescriptorHeapPropertiesEXT`, aligns a per-slot stride from `bufferDescriptorSize`/`bufferDescriptorAlignment`, and rounds the heap size up to `resourceHeapAlignment`, adding `minResourceHeapReservedRange` as a trailing reserved region [heap sizing](../../../modules/vulkan/device_generated_commands/vktDGCComputePushIndexHeapTestsExt.cpp#L160-L168).
- It creates a heap buffer with `VK_BUFFER_USAGE_DESCRIPTOR_HEAP_BIT_EXT`, then writes one storage-buffer descriptor per slot with `writeResourceDescriptorsEXT`, slot `i` addressing output buffer `i` [descriptor writes](../../../modules/vulkan/device_generated_commands/vktDGCComputePushIndexHeapTestsExt.cpp#L188-L208).
- It maps set `0` / binding `0` to `VK_DESCRIPTOR_MAPPING_SOURCE_HEAP_WITH_PUSH_INDEX_EXT` with `heapIndexStride` and `heapArrayStride` set to the slot stride, and builds a layout-only compute pipeline with `VK_PIPELINE_CREATE_2_DESCRIPTOR_HEAP_BIT_EXT` and `VK_NULL_HANDLE` layout [mapping and pipeline](../../../modules/vulkan/device_generated_commands/vktDGCComputePushIndexHeapTestsExt.cpp#L210-L241).
- The `IndirectCommandsLayoutBuilderExt` adds a `PUSH_DATA_EXT` token (one `uint` on the compute stage) at stream offset `0`, records the dispatch token offset, then appends a `DISPATCH_EXT` token; the command stream stores, per sequence, the pushed index at offset `0` and a `{1,1,1}` dispatch at the recorded offset [layout and stream](../../../modules/vulkan/device_generated_commands/vktDGCComputePushIndexHeapTestsExt.cpp#L243-L262).
- Recording binds the heap with `cmdBindResourceHeapEXT` (a `VkBindHeapInfoEXT` covering the heap range plus reserved region), binds the pipeline, and calls `cmdExecuteGeneratedCommandsEXT` with `isPreprocessed = VK_FALSE` for `kNumSlots` sequences, followed by a compute-shape shader-write to host-read barrier; the batch is submitted and waited on [record and submit](../../../modules/vulkan/device_generated_commands/vktDGCComputePushIndexHeapTestsExt.cpp#L277-L290).
- The host invalidates each buffer and compares its value against `i + kMarker`; the first mismatch reports the slot, expected, and actual value and returns `fail`, otherwise the case returns `pass("Pass")` [verification](../../../modules/vulkan/device_generated_commands/vktDGCComputePushIndexHeapTestsExt.cpp#L292-L307).

## Failure Meaning

### Failure Cause Mapping

This family has a single registered leaf and no behavioral axis, so the table form is replaced with a direct statement. A failure of `stage_compute` means at least one of the sixteen host-visible buffers did not equal `slotIndex + kMarker`: either some buffer kept its pre-filled value (its sequence's write never reached it), a buffer held a value that does not correspond to its own index (a write was routed to the wrong slot), or a buffer holds a marker count inconsistent with exactly one hit. Each symptom points to a defect in the push-index descriptor-heap routing path exercised by this test.

### Cause Analysis

#### Heap descriptor write and bind

**Possible failure symptoms:** One or more buffers remain at their pre-filled slot value, so the host reports `expected <slot+marker> but got <slot>` for the affected slot.

**Possible implementation causes:** Slot `i` only resolves to buffer `i` if `writeResourceDescriptorsEXT` wrote a valid descriptor at the host address `heapHostPtr + i*descriptorStride` and `cmdBindResourceHeapEXT` bound a range covering that slot with the reserved region placed after the user range. A mismatch here can indicate incorrect descriptor-stride handling, a heap-size/alignment error derived from the descriptor-heap properties, or a bound range that does not cover the selected slot. The source sets these values but does not isolate the failing layer, so source-level investigation is needed.

#### Push-index mapping and slot selection

**Possible failure symptoms:** A buffer holds a value equal to a different slot's index plus the marker, or the marker lands in a slot the corresponding sequence did not target; multiple slots can look swapped or shifted.

**Possible implementation causes:** Correct selection requires the `VK_DESCRIPTOR_MAPPING_SOURCE_HEAP_WITH_PUSH_INDEX_EXT` source to add `pushedIndex * heapIndexStride` to the mapping's heap offset when resolving set `0` / binding `0`, and the pipeline's `VK_PIPELINE_CREATE_2_DESCRIPTOR_HEAP_BIT_EXT` / mapping-in-`pNext` form to take effect with no pipeline layout. A wrong result can indicate the pushed index is scaled by the wrong stride, ignored, or applied to the wrong binding. The test exposes the routing outcome but not the internal selection step.

#### Generated command execution and push-data decode

**Possible failure symptoms:** No buffer changes, only some sequences take effect, or the write pattern does not track the pushed index at all.

**Possible implementation causes:** The `PUSH_DATA_EXT` token must copy the four index bytes from each sequence record into the mapping's push offset `0`, and the `DISPATCH_EXT` token must run one `(1,1,1)` work group per sequence under `maxSequenceCount = 16` with implicit preprocessing. A mismatch can indicate incorrect token/stride decoding, sequence-count handling, or generated dispatch execution. The evidence narrows the fault to the generated-command path but not to a single component.

## Case Pruning

### Requirement-based pruning

- `checkDGCExtComputeSupport(context, DGCComputeSupportType::BASIC)` requires `VK_EXT_device_generated_commands`, the compute stage in `supportedIndirectCommandsShaderStages`, and (for `BASIC`) no pipeline-binding or shader-binding stage requirement [support helper](../../../modules/vulkan/device_generated_commands/vktDGCUtilExt.cpp#L68-L75).
- `requireDeviceFunctionality(VK_EXT_DESCRIPTOR_HEAP_EXTENSION_NAME)` requires `VK_EXT_descriptor_heap`; without it the case is skipped rather than failed [checkSupport](../../../modules/vulkan/device_generated_commands/vktDGCComputePushIndexHeapTestsExt.cpp#L112-L116).

These mean the implementation cannot run the selected descriptor-heap-with-DGC path; they are support rejections, not result mismatches.

### Design-based pruning

- The family registers one leaf and no parameter matrix; there is no push-stage, slot-count, marker, or dispatch cross-product. The push-index heap routing is the only property under test.
- Every output buffer is a single `uint` and every dispatch is `(1, 1, 1)`, which removes shader arithmetic and dispatch-shape as confounds so the host result reflects only which slot the pushed index selected.
- `kNumSlots` is fixed at `16` and `kMarker` at `1 << 20`, keeping the marker unambiguous against every pre-filled slot value without widening the buffers.

## Key Takeaways

- The page tests one integrated mechanism: a DGC-pushed index selecting a descriptor-heap slot that redirects a layout-less compute pipeline's only binding.
- Correctness is proven through a side effect: buffer `i` ends at `i + kMarker` only if sequence `i`'s pushed index routed its single write to slot `i`.
- The pipeline is created for descriptor-heap use with `VK_PIPELINE_CREATE_2_DESCRIPTOR_HEAP_BIT_EXT` and no pipeline layout; the set/binding mapping carries the heap-with-push-index source, not a bound descriptor set.
- A pushed index is not shader data: the compute shader has no push-constant block and reads only the storage buffer its binding resolves to.
- A failure localizes to descriptor-heap routing (descriptor write/bind, push-index selection, or push-data decode), and the reported slot plus value narrows which slot was missed or misdirected.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test case registration | [createDGCComputePushIndexHeapTestsExt](../../../modules/vulkan/device_generated_commands/vktDGCComputePushIndexHeapTestsExt.cpp#L314-L323) | Creates the `push_index_heap` group and the `stage_compute` leaf. |
| Support gate | [checkSupport](../../../modules/vulkan/device_generated_commands/vktDGCComputePushIndexHeapTestsExt.cpp#L112-L116) | Requires DGC EXT compute support and `VK_EXT_descriptor_heap`. |
| Generated compute source | [initPrograms](../../../modules/vulkan/device_generated_commands/vktDGCComputePushIndexHeapTestsExt.cpp#L118-L134) | Emits the marker-write shader via `${MARKER}` substitution. |
| Heap property read and sizing | [getDescriptorHeapProperties and heap sizing](../../../modules/vulkan/device_generated_commands/vktDGCComputePushIndexHeapTestsExt.cpp#L67-L75) | Reads descriptor-heap properties used for stride and size. |
| Output buffer setup and prefill | [buffer setup](../../../modules/vulkan/device_generated_commands/vktDGCComputePushIndexHeapTestsExt.cpp#L143-L158) | Creates the sixteen slot buffers and pre-fills slot `i` with `i`. |
| Heap descriptor writes | [writeResourceDescriptorsEXT loop](../../../modules/vulkan/device_generated_commands/vktDGCComputePushIndexHeapTestsExt.cpp#L188-L208) | Writes one storage-buffer descriptor per slot into the heap. |
| Push-index mapping and pipeline | [mapping and pipeline](../../../modules/vulkan/device_generated_commands/vktDGCComputePushIndexHeapTestsExt.cpp#L210-L241) | Sets the heap-with-push-index source and the layout-less descriptor-heap pipeline. |
| Command layout and stream | [layout and stream](../../../modules/vulkan/device_generated_commands/vktDGCComputePushIndexHeapTestsExt.cpp#L243-L262) | Adds the push-data and dispatch tokens and writes per-sequence records. |
| Execution and verification | [iterate body](../../../modules/vulkan/device_generated_commands/vktDGCComputePushIndexHeapTestsExt.cpp#L277-L307) | Binds heap, executes generated commands, and checks each buffer. |
| EXT compute support helper | [checkDGCExtComputeSupport](../../../modules/vulkan/device_generated_commands/vktDGCUtilExt.cpp#L68-L75) | Applies the DGC EXT compute support checks. |
| Category registration | [vktDGCTests.cpp](../../../modules/vulkan/device_generated_commands/vktDGCTests.cpp#L97-L104) | Places `push_index_heap` under `dgc.ext.compute`. |
| vk-default mustpass path | [dgc.txt](../../../mustpass/main/vk-default/dgc.txt#L382-L382) | Lists the registered `push_index_heap.stage_compute` path. |
