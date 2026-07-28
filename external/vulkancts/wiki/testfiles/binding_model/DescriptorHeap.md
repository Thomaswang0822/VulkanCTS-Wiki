## Overview

**Core question:** Does `VK_EXT_descriptor_heap` preserve descriptor representation, mapping arithmetic, heap state, and shader-visible results across every registered behavior group?

- [`vktBindingDescriptorHeapTests.cpp`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp) implements the `binding_model.descriptor_heap` test family and registers 36 first-level behavior groups.
- The common path writes opaque sampler and resource descriptors, binds heap address ranges, maps ordinary `DescriptorSet` and `Binding` resources or uses heap built-ins, executes shaders, and compares device output with a deterministic oracle.
- Focused paths cover property limits, capture replay, reserved ranges, push data, state transitions, queue concurrency, graphics pipeline forms, SPIR-V operations, direct heap access, and unusual mapping layouts.
- The default Vulkan mustpass has 457 leaves for this family. This page explains the first-level behaviors and their shared mechanisms instead of reproducing that leaf inventory.

## Background Knowledge

For the shared concepts of descriptor interfaces and availability and visibility, see [Background Knowledge](../../categories/binding_model.md#background-knowledge) of the `binding_model` page.

- **Bound heap state.** A descriptor heap is a device-address range recorded as command-buffer state. The resource heap stores image, buffer, texel-buffer, and acceleration-structure descriptors. The sampler heap stores sampler descriptors. Each bound range may also contain an implementation-reserved portion that the application allocates but must not access while the binding remains live ([heap model](../../../../vulkan-docs/src/chapters/descriptorheaps.adoc#L5-L32), [reservation](../../../../vulkan-docs/src/chapters/descriptorheaps.adoc#L712-L731)).
- **Two shader interfaces.** A shader can index `ResourceHeapEXT` or `SamplerHeapEXT` directly. It can instead keep ordinary SPIR-V `DescriptorSet` and `Binding` decorations while pipeline or shader-object creation supplies `VkDescriptorSetAndBindingMappingEXT` records. A mapping derives the final heap byte offset from constants, push data, indirect memory, heap data, or shader-record data ([shader bindings](../../../../vulkan-docs/src/chapters/descriptorheaps.adoc#L1113-L1200), [mapping-source selection](../../../../vulkan-docs/src/chapters/descriptorheaps.adoc#L1213-L1318)).
- **Mapping arithmetic.** Constant mappings use `heapOffset + shaderIndex * heapArrayStride`. Push-index and indirect-index mappings add an index read from push data or an address. Combined image samplers may use separate resource and sampler offsets. The strides are byte counts, which matters for the non-packed and unaligned groups ([constant mapping](../../../../vulkan-docs/src/chapters/descriptorheaps.adoc#L1603-L1642), [push mapping](../../../../vulkan-docs/src/chapters/descriptorheaps.adoc#L1663-L1726), [indirect mapping](../../../../vulkan-docs/src/chapters/descriptorheaps.adoc#L1753-L1830)).
- **Push data and visibility.** `vkCmdPushDataEXT` exposes bytes through the SPIR-V `PushConstant` storage class. Mappings can interpret those bytes as payload, indices, or device addresses. Descriptor memory, referenced resources, indirect data, and host readback still need the applicable synchronization and lifetime rules ([push data](../../../../vulkan-docs/src/chapters/descriptorheaps.adoc#L965-L1032), [indirect-index lifetime](../../../../vulkan-docs/src/chapters/descriptorheaps.adoc#L1788-L1807)).

## Registration Hierarchy

```text
binding_model.descriptor_heap
├── limit
├── basic
├── invariance
├── capture_replay
├── dynamic_indexing
├── binding_mapping
├── high_binding
├── combined_image_samplers
├── reserved_heap
├── push_data
├── null_descriptor
├── ycbcr
├── different_mappings_per_shader
├── graphics_pipeline_library
├── switch_heaps
├── concurrent_queues
├── concurrent_heap_set
├── state_invalidation
├── write_after_record
├── spirv
├── resource_masking
├── null_image_queries
├── graphics
├── graphics_and_compute
├── different_mappings_same_shader
├── non_uniform_mappings
├── msaa_image_read
├── resource_heap_access
├── sampler_heap_access
├── shader_object_invariance
├── push_data_access
├── non_uniform_access
├── special_heap
├── non_packed
├── unaligned
└── secondary
```

The factory registers these children in one implementation file ([factory](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L15415-L15461)). The default mustpass lists their 457 executable leaves at [`binding-model.txt#L10441-L10897`](../../../mustpass/main/vk-default/binding-model.txt#L10441-L10897). The hierarchy stays one level deep here; generated stage, descriptor-type, mapping, and stride descendants appear in the next sections.

The mustpass provides exact leaf anchors for each behavior cluster without requiring a 457-leaf inventory:

| Behavior cluster | Exact mustpass path |
|------------------|---------------------|
| Limits and representation | `dEQP-VK.binding_model.descriptor_heap.capture_replay.acceleration_structure` |
| Typed access and descriptor semantics | `dEQP-VK.binding_model.descriptor_heap.basic.compute.acceleration_structure` |
| Binding mappings and resource selection | `dEQP-VK.binding_model.descriptor_heap.binding_mapping.heap_with_constant_offset.acceleration_structure` |
| Heap state lifetime | `dEQP-VK.binding_model.descriptor_heap.write_after_record.write_after_record` |
| Reservation, concurrency, and memory modes | `dEQP-VK.binding_model.descriptor_heap.reserved_heap.both_heaps.blit_image` |
| Push data and mapped addresses | `dEQP-VK.binding_model.descriptor_heap.push_data_access.push_data_access` |
| Pipeline and stage integration | `dEQP-VK.binding_model.descriptor_heap.graphics_and_compute.graphics_and_compute` |
| Direct heap built-ins | `dEQP-VK.binding_model.descriptor_heap.resource_heap_access.compute` |
| Irregular mapping layouts | `dEQP-VK.binding_model.descriptor_heap.non_packed.heap_with_constant_offset.acceleration_structure_stride_128` |
| SPIR-V operations | `dEQP-VK.binding_model.descriptor_heap.spirv.array_variable_pointers` |

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Behavior group | the 36 exact children in `## Registration Hierarchy` | Selects the contract under test. The primary axis below clusters these children by mechanism. | [registration functions](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L13331-L15461) |
| Shader stage | `fragment`, `compute`, `raygen`; graphics variants also use vertex, tessellation control/evaluation, geometry, mesh, task, and fragment stages | Moves heap access through graphics, compute, and ray-tracing execution models. | [`populateBasicTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L13339-L13476), [`populateGraphicsTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14712-L14796) |
| Descriptor type | sampler, sampled/storage image, uniform/storage texel buffer, uniform/storage buffer, input attachment, acceleration structure; combined image sampler in its dedicated group | Changes descriptor size, heap kind, shader declaration, access operation, support gates, and expected value. | [basic descriptor types](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L13345-L13361) |
| Mapping source | `heap_with_constant_offset`, `heap_with_push_index`, `heap_with_indirect_index`, `resource_heap_data`, `push_data`, `push_address`, `indirect_address`, `heap_with_shader_record_index`, `shader_record_data`, `shader_record_address`, `heap_with_indirect_index_array` | Selects where the shader-visible resource's heap offset or address comes from. | [`populateBindingMappingTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L13637-L13863) |
| Heap memory mode | ordinary, `sparse`, `protected`, `sparse_and_protected`; sampler heap, resource heap, both, or neither in reserved-range cases | Changes allocation, queue, protection, and reserved-range behavior without changing the payload oracle. | [`populateReservedHeapTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14150-L14204), [`populateSpecialHeapTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14963-L15089) |
| Mapping layout | default aligned stride, non-packed stride factors `1`, `3`, and `4`, and unaligned source variants | Separates explicit byte arithmetic from an implementation's preferred descriptor stride. | [`populateNonPackedTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L15091-L15259), [`populateUnalignedTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L15261-L15413) |
| Direct heap access | resource or sampler heap; compute or graphics; six non-uniform resource descriptor types | Uses `ResourceHeapEXT` and `SamplerHeapEXT` without a decorated-binding mapping. | [`populateResourceHeapAccessTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14847-L14863), [`populateNonUniformAccessTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14922-L14961) |
| SPIR-V operation | 13 leaves for size, untyped pointers, array length, heap built-ins, function calls, variable pointers, image atomics, and 64-bit operations | Isolates extension instructions and resource classification in source-authored SPIR-V assembly. | [`populateSpirvTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14650-L14685) |
| Mustpass population | 457 Vulkan leaves | Confirms the current default executable population. `non_packed` accounts for 120 leaves but remains one layout behavior. | [`binding-model.txt`](../../../mustpass/main/vk-default/binding-model.txt#L10441-L10897) |

## Behavior Parameters

The primary behavioral axis is the first-level behavior cluster. Each value below groups exact registered children that expose the same implementation contract.

### `limits and representation`: Descriptor bits and reproducibility

`limit` checks reported descriptor-heap properties. `invariance` checks deterministic opaque descriptor bytes and write bounds. `capture_replay` recreates capture-compatible resources and checks replayed bytes. `high_binding` exercises large set and binding numbers, while `shader_object_invariance` checks the corresponding shader-object binary and access contract ([limit oracle](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L801-L927), [invariance execution](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L6052-L6120)).

### `typed access and descriptor semantics`: Descriptor types, nulls, and conversion

`basic` covers ordinary descriptor types across fragment, compute, and ray-generation stages. `dynamic_indexing` selects decorated array elements at runtime. `combined_image_samplers` varies separate or embedded sampler selection. `null_descriptor` and `null_image_queries` check null reads and zero image-query results. `ycbcr` checks multiplanar conversion and the implementation-reported combined descriptor count ([basic registration](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L13339-L13476), [null and YCbCr registration](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14271-L14397)).

### `binding mappings and resource selection`: Mapping sources and masks

`binding_mapping` spans all 11 mapping sources. `different_mappings_per_shader` supplies different records to graphics stages. `different_mappings_same_shader` combines mapping sources in one shader. `resource_masking` verifies that a mapping applies only to the selected SPIR-V resource classes. `high_binding` also tests the set and binding match predicate ([mapping registration](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L13637-L13863), [resource masking](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L8743-L9048)).

### `heap state lifetime`: Switching, invalidation, and recording

`switch_heaps` changes bound ranges, with push-descriptor and command-buffer-inheritance variants. `state_invalidation` transitions between heap state and legacy descriptor state. `write_after_record` fills descriptor memory only after command recording. `secondary` verifies heap binding inheritance and use in secondary command buffers ([state paths](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L2127-L2195), [write after record](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L3446-L3569), [state invalidation rule](../../../../vulkan-docs/src/chapters/descriptorheaps.adoc#L675-L710)).

### `reservation, concurrency, and memory modes`: Reserved ranges and queue use

`reserved_heap` binds no heap, either heap, or both heaps while transfer and clear operations run across queues. `concurrent_queues` runs the typed-access path on several queues. `concurrent_heap_set` compares heap-backed and ordinary descriptor-set work in concurrent submissions. `special_heap` selects sparse, protected, or combined sparse/protected storage ([reserved execution](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L6585-L7050), [concurrent heap and set](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L2870-L3130)).

### `push data and mapped addresses`: Payload, indices, and addresses

`push_data` checks fragment, compute, and ray-generation use. `push_data_access` copies the complete `maxPushDataSize` range through a direct resource-heap descriptor. Mapping descendants named `push_data`, `push_address`, `indirect_address`, `resource_heap_data`, and shader-record forms interpret data as values, indices, or addresses ([push-data registration](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14206-L14270), [full-range access](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L12713-L12858)).

### `pipeline and stage integration`: Graphics, compute, libraries, and MSAA

`graphics` covers classic and mesh graphics stages, primary and secondary recording, and vector transport. `graphics_and_compute` uses both bind points in one command buffer. `graphics_pipeline_library` covers library-linked pipelines and shader objects. `msaa_image_read` writes and reads four samples through a heap image descriptor ([graphics registration](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14712-L14807), [MSAA registration](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14833-L14845)).

### `direct heap built-ins`: Resource and sampler heap arrays

`resource_heap_access` and `sampler_heap_access` index the corresponding built-in heap in compute and graphics. `non_uniform_access` gives 64 invocations distinct sampled-image, storage-image, texel-buffer, uniform-buffer, or storage-buffer descriptors. These paths do not depend on a `DescriptorSet` and `Binding` mapping for the resource under test ([direct access shaders](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L11172-L11758), [non-uniform generator](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L12897-L12959)).

### `irregular mapping layouts`: Non-uniform, non-packed, and unaligned selection

`non_uniform_mappings` uses a non-uniform invocation index with mapped bindings. `non_packed` varies explicit resource and sampler strides across constant, push-index, indirect-index, shader-record-index, and indirect-index-array sources. `unaligned` applies descriptor-sized strides and offsets to push, indirect, and shader-record mappings. Each group catches implementations that substitute preferred packing for the supplied byte formula ([non-uniform mappings](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L10541-L10687), [packing registration](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L15091-L15413)).

### `SPIR-V operations`: Extension instruction coverage

`spirv` uses source-authored SPIR-V assembly for `OpConstantSizeOfEXT`, `OpUntypedAccessChainKHR`, `OpBufferPointerEXT`, `OpUntypedArrayLengthKHR`, `OpUntypedImageTexelPointerEXT`, heap built-ins, function calls, variable pointers, image atomics, and 64-bit operations. `resource_masking` complements these operation probes by checking how declared resources are classified ([SPIR-V programs and oracle](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L7408-L8681)).

## Shader Analysis

Three shaders are needed because the central mechanisms are different. The first keeps ordinary set and binding decorations and tests descriptor-memory timing. The second reads push data while writing through `ResourceHeapEXT`. The third selects a direct heap descriptor separately for each invocation.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.binding_model.descriptor_heap.write_after_record.write_after_record
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `write_after_record` | The host records the dispatch before it writes the descriptor bytes. |
| storage texel buffer | Set 0, binding 0 is an `r32ui` `uimageBuffer`. |
| constant-offset mapping | The pipeline maps the binding to resource heap offset zero. |
| default build target | No explicit build options are supplied, so CTS uses baseline `spirv1.0`. |

#### Purpose

The shader stores pushed data through an ordinary decorated resource mapped into the heap. The test detects an implementation that snapshots empty descriptor bytes during command recording.

#### Structural Design

| Step | Shader operation | Observable result |
|------|------------------|-------------------|
| Resolve | Load set 0, binding 0 through the pipeline's constant-offset mapping. | The resource must come from heap byte offset zero. |
| Write | Store `uvec4(value, 0, 0, 0)` at texel zero. | The output word becomes the pushed random value. |
| Check | The host reads one `uint32_t` after completion. | Any stale or wrong descriptor produces a mismatch. |

#### Shader Code

```glsl
#version 450
/// One compute invocation writes the pushed value through set 0, binding 0. Pipeline creation maps this
/// ordinary storage-texel-buffer declaration to byte offset 0 in the bound resource heap.
layout(local_size_x = 1) in;
layout(binding = 0, r32ui) uniform uimageBuffer outputBuffer;
/// Descriptor-heap push data is exposed through the existing PushConstant storage class.
layout(push_constant) uniform PushConstant {
  uint value;
};

void main()
{
    imageStore(outputBuffer, 0, uvec4(value, 0, 0, 0));
}
```

#### Additional Info

- [`DescriptorHeapTestCaseWriteAfterRecord::initPrograms()`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L3446-L3462) supplies this GLSL without explicit build options.
- The host records heap binding, push data, pipeline binding, and dispatch before calling `vkWriteResourceDescriptorsEXT` ([late write](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L3511-L3559)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|------------------------------------------|----------|
| Descriptor type | The common generator changes declarations and operations for samplers, images, texel buffers, buffers, input attachments, and acceleration structures. | [generated declarations](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L3901-L4217) |
| Mapping source | Other groups replace the constant offset with push, indirect, heap-data, or shader-record sources. | [mapping registration](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L13637-L13863) |
| Host ordering | Only this group writes the descriptor after recording the command buffer. | [iterate path](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L3464-L3569) |

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
; Bound: 25
; Schema: 0
               OpCapability Shader
               OpCapability ImageBuffer
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main"
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpName %main "main"
               OpName %outputBuffer "outputBuffer"
               OpName %PushConstant "PushConstant"
               OpMemberName %PushConstant 0 "value"
               OpName %_ ""
               OpDecorate %outputBuffer Binding 0
               OpDecorate %outputBuffer DescriptorSet 0
               OpDecorate %PushConstant Block
               OpMemberDecorate %PushConstant 0 Offset 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
          %7 = OpTypeImage %uint Buffer 0 0 0 2 R32ui
%_ptr_UniformConstant_7 = OpTypePointer UniformConstant %7
%outputBuffer = OpVariable %_ptr_UniformConstant_7 UniformConstant
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%PushConstant = OpTypeStruct %uint
%_ptr_PushConstant_PushConstant = OpTypePointer PushConstant %PushConstant
          %_ = OpVariable %_ptr_PushConstant_PushConstant PushConstant
%_ptr_PushConstant_uint = OpTypePointer PushConstant %uint
     %uint_0 = OpConstant %uint 0
     %v4uint = OpTypeVector %uint 4
     %v3uint = OpTypeVector %uint 3
     %uint_1 = OpConstant %uint 1
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
         %10 = OpLoad %7 %outputBuffer
         %17 = OpAccessChain %_ptr_PushConstant_uint %_ %int_0
         %18 = OpLoad %uint %17
         %21 = OpCompositeConstruct %v4uint %18 %uint_0 %uint_0 %uint_0
               OpImageWrite %10 %int_0 %21
               OpReturn
               OpFunctionEnd
```

</details>

### Representative Shader Walkthrough 2

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.binding_model.descriptor_heap.push_data_access.push_data_access
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `push_data_access` | One specialization constant expands the loop to `maxPushDataSize / 4` words. |
| `ResourceHeapEXT` | `buffers[0]` directly resolves the output storage-buffer descriptor. |
| `PushConstant` | `vkCmdPushDataEXT` supplies the source array. |
| explicit build target | CTS requests `SPIRV_VERSION_1_4` with relaxed GLSL enabled. |

#### Purpose

The shader copies every supported push-data word through a direct resource-heap storage buffer. The host checks the complete copied sequence.

#### Structural Design

| Step | Shader operation | Observable result |
|------|------------------|-------------------|
| Specialize | Set `PUSH_LENGTH` from `maxPushDataSize / 4`. | The loop covers the advertised range. |
| Read | Load `pushData[i]` from `PushConstant`. | Each four-byte position contributes one value. |
| Write | Store into `buffers[0].outputBuffer[i]`. | Host-visible output must equal every pushed word. |

#### Shader Code

```glsl
#version 450
#extension GL_EXT_descriptor_heap: require
layout(local_size_x = 1) in;

/// The ResourceHeapEXT-backed runtime array resolves element 0 to the output storage-buffer descriptor
/// written at the start of the bound resource heap.
layout(descriptor_heap) buffer O { uint outputBuffer[]; } buffers[];

/// Pipeline specialization expands this loop to maxPushDataSize / 4 elements.
layout(constant_id = 0) const int PUSH_LENGTH = 1;

/// vkCmdPushDataEXT supplies this array through the PushConstant storage class.
layout(push_constant, std430) uniform P {
    int pushData[PUSH_LENGTH];
};

void main() {
    for (int i = 0; i < PUSH_LENGTH; ++i) {
        buffers[0].outputBuffer[i] = pushData[i];
    }
}
```

#### Additional Info

- The reconstructed source follows [`DescriptorHeapTestCasePushDataAccess::initPrograms()`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L12713-L12735). Only `///` documentation comments were added.
- The host specializes the loop, pushes random words, dispatches once, records a compute-to-host dependency, and compares every element ([runtime path](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L12738-L12858)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|------------------------------------------|----------|
| Push-data role | Mapping groups can consume the bytes as heap indices or addresses instead of copying them as payload. | [mapping-source rules](../../../../vulkan-docs/src/chapters/descriptorheaps.adoc#L1511-L1553) |
| Push-data size | The specialization value changes with `maxPushDataSize`; the shader structure remains fixed. | [specialization setup](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L12742-L12783) |
| Heap interface | This shader uses `ResourceHeapEXT`; ordinary mapping cases retain `DescriptorSet` and `Binding`. | [built-in semantics](../../../../vulkan-docs/src/chapters/descriptorheaps.adoc#L926-L960) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `comp`
- Target SPIRV version: `spirv1.4`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.4
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 47
; Schema: 0
               OpCapability Shader
               OpCapability UntypedPointersKHR
               OpCapability DescriptorHeapEXT
               OpExtension "SPV_EXT_descriptor_heap"
               OpExtension "SPV_KHR_untyped_pointers"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %resource_heap %_
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpSourceExtension "GL_EXT_descriptor_heap"
               OpName %main "main"
               OpName %i "i"
               OpName %PUSH_LENGTH "PUSH_LENGTH"
               OpName %resource_heap "resource_heap"
               OpName %O "O"
               OpMemberName %O 0 "outputBuffer"
               OpName %P "P"
               OpMemberName %P 0 "pushData"
               OpName %_ ""
               OpDecorate %PUSH_LENGTH SpecId 0
               OpDecorate %resource_heap BuiltIn ResourceHeapEXT
               OpDecorate %_runtimearr_uint ArrayStride 4
               OpDecorate %O Block
               OpMemberDecorate %O 0 Offset 0
               OpDecorate %_arr_int_PUSH_LENGTH ArrayStride 4
               OpDecorate %P Block
               OpMemberDecorate %P 0 Offset 0
               OpDecorateId %_runtimearr_36 ArrayStrideIdEXT %37
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
%_ptr_Function_int = OpTypePointer Function %int
      %int_0 = OpConstant %int 0
%PUSH_LENGTH = OpSpecConstant %int 1
       %bool = OpTypeBool
%_ptr_UniformConstant = OpTypeUntypedPointerKHR UniformConstant
%resource_heap = OpUntypedVariableKHR %_ptr_UniformConstant UniformConstant
       %uint = OpTypeInt 32 0
%_runtimearr_uint = OpTypeRuntimeArray %uint
          %O = OpTypeStruct %_runtimearr_uint
%_arr_int_PUSH_LENGTH = OpTypeArray %int %PUSH_LENGTH
          %P = OpTypeStruct %_arr_int_PUSH_LENGTH
%_ptr_PushConstant_P = OpTypePointer PushConstant %P
          %_ = OpVariable %_ptr_PushConstant_P PushConstant
%_ptr_PushConstant_int = OpTypePointer PushConstant %int
%_ptr_StorageBuffer = OpTypeUntypedPointerKHR StorageBuffer
         %36 = OpTypeBufferEXT StorageBuffer
         %37 = OpConstantSizeOfEXT %int %36
%_runtimearr_36 = OpTypeRuntimeArray %36
      %int_1 = OpConstant %int 1
     %v3uint = OpTypeVector %uint 3
     %uint_1 = OpConstant %uint 1
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
          %i = OpVariable %_ptr_Function_int Function
               OpStore %i %int_0
               OpBranch %10
         %10 = OpLabel
               OpLoopMerge %12 %13 None
               OpBranch %14
         %14 = OpLabel
         %15 = OpLoad %int %i
         %18 = OpSLessThan %bool %15 %PUSH_LENGTH
               OpBranchConditional %18 %11 %12
         %11 = OpLabel
         %24 = OpLoad %int %i
         %29 = OpLoad %int %i
         %31 = OpAccessChain %_ptr_PushConstant_int %_ %int_0 %29
         %32 = OpLoad %int %31
         %33 = OpBitcast %uint %32
         %35 = OpUntypedAccessChainKHR %_ptr_UniformConstant %_runtimearr_36 %resource_heap %int_0
         %39 = OpBufferPointerEXT %_ptr_StorageBuffer %35
         %40 = OpUntypedAccessChainKHR %_ptr_StorageBuffer %O %39 %int_0 %24
               OpStore %40 %33
               OpBranch %13
         %13 = OpLabel
         %41 = OpLoad %int %i
         %43 = OpIAdd %int %41 %int_1
               OpStore %i %43
               OpBranch %10
         %12 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

### Representative Shader Walkthrough 3

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.binding_model.descriptor_heap.non_uniform_access.storage_buffer
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `storage_buffer` | The resource heap contains 64 one-word storage-buffer descriptors. |
| `non_uniform_access` | `gl_GlobalInvocationID.x` selects a different descriptor per invocation. |
| local size 64 | One workgroup covers all descriptor indices. |
| explicit build target | CTS requests `SPIRV_VERSION_1_4` with relaxed GLSL enabled. |

#### Purpose

Each invocation reads one direct resource-heap descriptor and writes its value into a shared result buffer. The output identifies incorrect runtime selection or descriptor stride.

#### Structural Design

| Step | Shader operation | Observable result |
|------|------------------|-------------------|
| Index | Read `gl_GlobalInvocationID.x`. | Each invocation selects index 0 through 63. |
| Resolve | Load `descs[idx].data` through `ResourceHeapEXT`. | The selected descriptor supplies one initialized word. |
| Return | Store the word to `result[idx]`. | The host compares all 64 values independently. |

#### Shader Code

```glsl
#version 450
#extension GL_EXT_nonuniform_qualifier: require
#extension GL_EXT_samplerless_texture_functions: require
#extension GL_EXT_descriptor_heap: require
/// Sixty-four invocations each select a different descriptor from ResourceHeapEXT.
layout(local_size_x = 64) in;
/// Set 0, binding 0 is mapped separately to one output buffer holding all observed values.
layout(binding = 0, std430) buffer OutputBuffer {
    uint result[];
};
/// This ResourceHeapEXT-backed runtime array contains 64 storage-buffer descriptors.
layout(descriptor_heap) buffer SSBO { uint data; } descs[];

void main()
{
    uint idx = gl_GlobalInvocationID.x;
    uint value = descs[idx].data;
    result[idx] = value;
}
```

#### Additional Info

- The storage-buffer branch comes from [`DescriptorHeapTestCaseNonUniformAccess::initPrograms()`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L12897-L12959). Only `///` documentation comments were added.
- Runtime code aligns each descriptor stride, creates 64 resources, writes one descriptor per index, and builds 64 expected values ([setup](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L12961-L13030)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|------------------------------------------|----------|
| Descriptor type | Other leaves use `texelFetch`, `imageLoad`, texel-buffer operations, or a uniform-buffer member. | [type branches](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L12909-L12955) |
| Mapping interface | `non_uniform_mappings` uses mapped decorated bindings, while this case directly indexes `ResourceHeapEXT`. | [mapped variant](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L10541-L10687) |
| Invocation count | The runtime fixes the descriptor count at 64 so one dispatch checks the whole heap slice. | [descriptor count](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L12961-L12986) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `comp`
- Target SPIRV version: `spirv1.4`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.4
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 42
; Schema: 0
               OpCapability Shader
               OpCapability UntypedPointersKHR
               OpCapability DescriptorHeapEXT
               OpExtension "SPV_EXT_descriptor_heap"
               OpExtension "SPV_KHR_untyped_pointers"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %resource_heap %gl_GlobalInvocationID %_
               OpExecutionMode %main LocalSize 64 1 1
               OpSource GLSL 450
               OpSourceExtension "GL_EXT_descriptor_heap"
               OpSourceExtension "GL_EXT_nonuniform_qualifier"
               OpSourceExtension "GL_EXT_samplerless_texture_functions"
               OpName %main "main"
               OpName %idx "idx"
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
               OpName %value "value"
               OpName %resource_heap "resource_heap"
               OpName %SSBO "SSBO"
               OpMemberName %SSBO 0 "data"
               OpName %OutputBuffer "OutputBuffer"
               OpMemberName %OutputBuffer 0 "result"
               OpName %_ ""
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %resource_heap BuiltIn ResourceHeapEXT
               OpDecorate %SSBO Block
               OpMemberDecorate %SSBO 0 Offset 0
               OpDecorateId %_runtimearr_25 ArrayStrideIdEXT %26
               OpDecorate %_runtimearr_uint ArrayStride 4
               OpDecorate %OutputBuffer Block
               OpMemberDecorate %OutputBuffer 0 Offset 0
               OpDecorate %_ Binding 0
               OpDecorate %_ DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
     %uint_0 = OpConstant %uint 0
%_ptr_Input_uint = OpTypePointer Input %uint
%_ptr_UniformConstant = OpTypeUntypedPointerKHR UniformConstant
%resource_heap = OpUntypedVariableKHR %_ptr_UniformConstant UniformConstant
       %SSBO = OpTypeStruct %uint
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_StorageBuffer = OpTypeUntypedPointerKHR StorageBuffer
         %25 = OpTypeBufferEXT StorageBuffer
         %26 = OpConstantSizeOfEXT %int %25
%_runtimearr_25 = OpTypeRuntimeArray %25
%_runtimearr_uint = OpTypeRuntimeArray %uint
%OutputBuffer = OpTypeStruct %_runtimearr_uint
%_ptr_StorageBuffer_OutputBuffer = OpTypePointer StorageBuffer %OutputBuffer
          %_ = OpVariable %_ptr_StorageBuffer_OutputBuffer StorageBuffer
%_ptr_StorageBuffer_uint = OpTypePointer StorageBuffer %uint
    %uint_64 = OpConstant %uint 64
     %uint_1 = OpConstant %uint 1
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_64 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
        %idx = OpVariable %_ptr_Function_uint Function
      %value = OpVariable %_ptr_Function_uint Function
         %14 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %15 = OpLoad %uint %14
               OpStore %idx %15
         %19 = OpLoad %uint %idx
         %24 = OpUntypedAccessChainKHR %_ptr_UniformConstant %_runtimearr_25 %resource_heap %19
         %28 = OpBufferPointerEXT %_ptr_StorageBuffer %24
         %29 = OpUntypedAccessChainKHR %_ptr_StorageBuffer %SSBO %28 %int_0
         %30 = OpLoad %uint %29
               OpStore %value %30
         %35 = OpLoad %uint %idx
         %36 = OpLoad %uint %value
         %38 = OpAccessChain %_ptr_StorageBuffer_uint %_ %int_0 %35
               OpStore %38 %36
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- Common cases query `VkPhysicalDeviceDescriptorHeapPropertiesEXT`, align image, buffer, and sampler descriptor strides, allocate host-visible device-address buffers, and reserve the advertised implementation range ([stride helpers](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L204-L273), [common instance state](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L307-L422)).
- The host initializes images, buffers, samplers, texel views, or acceleration structures, then calls `vkWriteResourceDescriptorsEXT` or `vkWriteSamplerDescriptorsEXT`. Direct heap-data cases write their payload or indirect table at the mapped address.
- Pipelines use `VK_PIPELINE_CREATE_2_DESCRIPTOR_HEAP_BIT_EXT`. Decorated shader resources receive stage-specific `VkShaderDescriptorSetAndBindingMappingInfoEXT` records. Direct built-in shaders need no mapping for the heap array itself.
- Command buffers bind sampler and resource ranges, push required bytes, bind a graphics, compute, ray-tracing, or shader-object pipeline, and issue draws, dispatches, or traces. Reserved-heap cases coordinate several queues with timeline semaphores before final copyback ([reserved execution](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L6585-L7050)).
- The common typed path compares every generated scalar or vector with values derived from deterministic resource initialization. Focused paths compare descriptor bytes, query results, YCbCr channels, graphics pixels, graphics and compute sentinels, four MSAA samples, direct heap values, SPIR-V operation results, or shader-object binaries.
- Before host reads, cases wait for the device or queue and, when needed, record shader-to-host or transfer-to-host dependencies. A mismatch reports the relevant element, value, pixel, sample, descriptor bytes, or operation result.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `limits and representation` | Descriptor-heap property reporting, descriptor-size reporting, deterministic descriptor encoding, capture/replay reconstruction, or shader-object binary invariance failure. |
| `typed access and descriptor semantics` | Type-specific descriptor writing, heap placement, shader decoding, array indexing, null behavior, combined image sampler handling, or YCbCr conversion failure. |
| `binding mappings and resource selection` | Descriptor set and binding matching, mapping-source address calculation, per-stage mapping selection, or SPIR-V resource-mask classification failure. |
| `heap state lifetime` | Heap rebinding, legacy-state invalidation, secondary-command-buffer inheritance, or descriptor visibility after command recording failure. |
| `reservation, concurrency, and memory modes` | Reserved-range lifetime or isolation failure, cross-queue heap use failure, or sparse/protected descriptor-heap allocation and access failure. |
| `push data and mapped addresses` | `vkCmdPushDataEXT` range handling, PushConstant exposure, push-index/address mapping, or maximum push-data transfer failure. |
| `pipeline and stage integration` | Graphics-stage, compute-stage, graphics pipeline library, shader-object, or multisample image integration failure. |
| `direct heap built-ins` | `ResourceHeapEXT` or `SamplerHeapEXT` lowering, direct descriptor selection, or non-uniform direct heap access failure. |
| `irregular mapping layouts` | Non-uniform mapped-array selection, non-packed descriptor size/stride handling, or unaligned base/index arithmetic failure. |
| `SPIR-V operations` | `SPV_EXT_descriptor_heap`, untyped pointer, size, array-length, image atomic, function-call, variable-pointer, or 64-bit operation lowering failure. |

### Cause Analysis

#### Descriptor property or representation failure

**Possible failure symptoms:** `limit`, `invariance`, `capture_replay`, `high_binding`, or `shader_object_invariance` reports an invalid property, overwritten guard bytes, unequal descriptor encodings, replay mismatch, wrong high binding result, or unequal shader-object data.

**Possible implementation causes:** Property reporting may violate the extension's limits, descriptor writers may emit the wrong number of bytes, equal create information may produce non-invariant encodings, or capture-replay and shader-object creation may fail to preserve the required representation ([descriptor invariance](../../../../vulkan-docs/src/chapters/descriptorheaps.adoc#L53-L60), [heap limits](../../../../vulkan-docs/src/chapters/limits.adoc#L5854-L5870)).

#### Typed descriptor semantic failure

**Possible failure symptoms:** A typed access, combined image sampler, null descriptor, null image query, dynamic-indexing, or YCbCr case returns the wrong value, image dimensions, mip count, or converted color.

**Possible implementation causes:** Type-specific descriptor writing or decoding may use the wrong size, resource address, image metadata, sampler state, null behavior, or YCbCr conversion data. The source chooses a separate declaration, resource setup, and oracle for each descriptor class.

#### Mapping and resource-selection failure

**Possible failure symptoms:** One mapping source, stage-specific mapping, same-shader mapping, resource-mask class, or high set/binding value selects the wrong initialized resource.

**Possible implementation causes:** The implementation may match the wrong `DescriptorSet`, `Binding`, or `resourceMask`, or evaluate constant, push, indirect, heap-data, shader-record, image, or sampler byte formulas incorrectly ([mapping match](../../../../vulkan-docs/src/chapters/descriptorheaps.adoc#L1195-L1231), [resource masks](../../../../vulkan-docs/src/chapters/descriptorheaps.adoc#L1461-L1500)).

#### Heap state lifetime failure

**Possible failure symptoms:** A switched heap reads an earlier range, descriptor-set and heap state remain valid when they should invalidate each other, late-written bytes are ignored, or a secondary command buffer loses inherited heap state.

**Possible implementation causes:** Command recording may snapshot descriptor contents instead of heap address state, invalidate the wrong binding model, apply the wrong pipeline bind-point state, or fail to retain heap references until command buffers reset or free them ([binding lifetime and invalidation](../../../../vulkan-docs/src/chapters/descriptorheaps.adoc#L675-L731)).

#### Reservation, concurrency, or memory-mode failure

**Possible failure symptoms:** A reserved-range transfer or clear returns wrong data, concurrent queue results diverge from their expected values, or sparse/protected cases fail when ordinary heaps pass.

**Possible implementation causes:** Reserved offsets or sizes may be handled incorrectly, heap state may leak between queues or submissions, or descriptor-heap buffers may not follow sparse and protected memory requirements. The test isolates setup, concurrent submissions, and final readback before reporting a mismatch.

#### Push-data or mapped-address failure

**Possible failure symptoms:** A push-data word differs, a maximum-range copy stops early, or a push, indirect, heap-data, or shader-record mapping resolves the wrong location.

**Possible implementation causes:** `vkCmdPushDataEXT` may expose the wrong byte range through `PushConstant`, or a mapping may apply the wrong 4-byte or 8-byte offset, index stride, address offset, or indirect memory read ([push-index formula](../../../../vulkan-docs/src/chapters/descriptorheaps.adoc#L1694-L1722), [indirect-address formula](../../../../vulkan-docs/src/chapters/descriptorheaps.adoc#L2005-L2047)).

#### Pipeline or stage integration failure

**Possible failure symptoms:** Graphics, graphics-plus-compute, graphics pipeline library, shader-object, MSAA, or secondary graphics output differs from the expected pixel, vector, sentinel, or sample while a compute case passes.

**Possible implementation causes:** Descriptor-heap pipeline flags, per-stage mapping records, library linking, shader-object state, stage interfaces, bind-point separation, or sample-rate access may not preserve the same heap semantics used by compute pipelines.

#### Direct heap built-in failure

**Possible failure symptoms:** Resource, sampler, or non-uniform direct access reports a wrong word, texel, image value, sampled border color, or per-invocation result.

**Possible implementation causes:** `ResourceHeapEXT` or `SamplerHeapEXT` may lower to the wrong bound range, apply the wrong descriptor size, or lose a runtime heap-array index ([heap built-ins](../../../../vulkan-docs/src/chapters/descriptorheaps.adoc#L926-L960)).

#### Irregular layout failure

**Possible failure symptoms:** Only one non-uniform invocation, non-packed stride, unaligned offset, descriptor type, or index source fails while its default-layout counterpart passes.

**Possible implementation causes:** Explicit byte strides may be replaced with preferred packing, interpreted in descriptor units, or combined with the wrong base offset. A non-uniform selector may also be treated as a uniform value. The descriptor-size query permits tighter non-power-of-two encodings, so implementations must honor the reported and supplied byte layout ([exact descriptor sizes](../../../../vulkan-docs/src/chapters/descriptorheaps.adoc#L2153-L2200)).

#### SPIR-V operation failure

**Possible failure symptoms:** A `spirv` leaf writes the wrong size, array length, atomic value, function result, variable-pointer result, or heap-built-in value.

**Possible implementation causes:** The SPIR-V consumer may reject or lower `SPV_EXT_descriptor_heap`, untyped-pointer, 64-bit-indexing, image atomic, function-call, or variable-pointer operations incorrectly. The source-authored modules isolate each operation and compare an operation-specific result.

## Case Pruning

### Requirement-based pruning

- Common cases require `VK_EXT_descriptor_heap`, `VK_KHR_shader_untyped_pointers`, `VK_KHR_maintenance5`, `VK_KHR_buffer_device_address`, and `VK_KHR_synchronization2`. Optional paths require their exact ray-query, acceleration-structure, ray-tracing, YCbCr, graphics-pipeline-library, shader-object, dynamic-rendering, robustness, custom-border-color, mesh, variable-pointer, push-descriptor, sample-rate, image-atomic, sparse, protected, or non-uniform indexing feature ([support checks](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L509-L722)).
- Reserved-heap cases also require timeline semaphores. If all advertised minimum reservation sizes are zero, the case passes without exercising nonzero reserved storage ([reserved support](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L780-L799), [zero-reservation branch](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L6585-L6593)).
- Input attachments run only in fragment shaders. Shader-record mappings require a ray-tracing stage. Non-uniform descriptor-array cases require the descriptor-type-specific indexing feature.

### Design-based pruning

- The generator excludes custom border color from non-sampler descriptors and excludes input attachments from compute and ray-generation stages ([basic filtering](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L13392-L13403)).
- Mapping, non-packed, and unaligned groups retain only source and descriptor-type combinations that have defined data, address, sampler, or shader-record semantics.
- This page treats the 120 `non_packed` leaves and other generated dimensions as mechanism variations. The exact first-level tree and mustpass span preserve coverage without a leaf-by-leaf listing.

## Key Takeaways

- The family checks opaque descriptor bytes, heap address state, mapping formulas, direct heap built-ins, shader stages, and result visibility as separate contracts.
- `ResourceHeapEXT` and `SamplerHeapEXT` exercise a different compiler interface from mapped `DescriptorSet` and `Binding` resources.
- Reserved ranges, heap switching, invalidation, concurrency, secondary recording, and write-after-record expose state-lifetime defects that ordinary descriptor reads cannot detect.
- Non-uniform, non-packed, unaligned, push, indirect, shader-record, graphics, MSAA, and SPIR-V cases turn byte-level mistakes into exact host-visible mismatches.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Core parameters and helpers | [`TestParams`, `ShaderBinding`, and stride helpers](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L61-L228) | Defines case switches, mapping records, and default descriptor strides. |
| Common support | [`DescriptorHeapTestCaseBase::checkSupport()`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L500-L722) | Applies common and optional feature gates. |
| Shared generated path | [`DescriptorHeapTestCaseBasic::initQueuePrograms()`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L3901-L4217), [`DescriptorHeapTestInstanceBasic::iterate()`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L4219-L4847) | Implements broad typed descriptor and mapping access. |
| Representation path | [`DescriptorHeapTestInstanceInvariance::iterate()`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L6052-L6120) | Checks descriptor bytes, bounds, and capture replay. |
| Reserved heap path | [`DescriptorHeapTestInstanceReservedHeap::iterate()`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L6585-L7050) | Implements queue, timeline, reservation, transfer, and readback behavior. |
| Source-authored SPIR-V | [`DescriptorHeapTestCaseSpirv::initPrograms()`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L7408-L8083) | Builds the isolated extension-operation modules. |
| Graphics and direct heap paths | [graphics through direct sampler access](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L9634-L11758) | Covers stage integration, MSAA, and built-in heaps. |
| Push and non-uniform artifacts | [push-data and non-uniform builders](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L12713-L13030) | Owns two reconstructed shaders and their runtime setup. |
| Complete registration | [`populateDescriptorHeapTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L13331-L15461) | Registers all first-level behavior groups. |
| Local specification | [`descriptorheaps.adoc`](../../../../vulkan-docs/src/chapters/descriptorheaps.adoc#L5-L32), [`limits.adoc`](../../../../vulkan-docs/src/chapters/limits.adoc#L5854-L5870), [`features.adoc`](../../../../vulkan-docs/src/chapters/features.adoc#L9551-L9557) | Defines extension semantics, limits, and feature reporting. |
