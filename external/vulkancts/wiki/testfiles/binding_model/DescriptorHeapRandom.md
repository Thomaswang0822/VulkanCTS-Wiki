## Overview

**Core question:** Can `VK_EXT_descriptor_heap` correctly map randomly generated descriptor layouts to the resources read and written by shaders?

- This page covers `vktBindingDescriptorHeapRandomTests.cpp`, which generates descriptor-set layouts, maps their bindings into descriptor-heap offsets, and executes compute, vertex, or fragment shader cases.
- Each backing descriptor contains its global linear index; the shader reads descriptors and accumulates mismatches, while selected storage descriptors are written and checked by the host.
- The registered matrix varies descriptor-set count, indexing mode, descriptor budgets, storage-image/texel-buffer shape, shader stage, input attachments, and random seed.

## Background Knowledge

- A descriptor heap stores resource or sampler descriptors in host-visible heap memory. `VK_EXT_descriptor_heap` separates the shader's ordinary set/binding declarations from the heap locations supplied through `VkDescriptorSetAndBindingMappingEXT`.
- A descriptor array may be indexed by a constant, push-constant-derived value, dynamically computed value, or runtime-sized array. Dynamic indexing therefore exercises both shader indexing and the mapping of each array element to a heap range.
- Input attachments are fragment-stage resources, while storage images, storage buffers, and storage texel buffers can be written as well as read. The test uses these distinctions when generating legal layouts and when selecting synchronization and result-copy operations.

## Registration Hierarchy

```text
binding_model.descriptor_heap_random
├── sets4
├── sets8
```

The deeper matrix is generated beneath each set-count group by `populateDescriptorHeapRandomTests`; the direct-child tree above is the useful registration boundary for this page.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Descriptor-set count | `sets4`, `sets8` | Exercises mappings across four or eight descriptor sets. | [`populateDescriptorHeapRandomTests`](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/binding_model/vktBindingDescriptorHeapRandomTests.cpp#L1510-L1517) |
| Indexing mode | `noarray`, `constant`, `unifindexed`, `dynindexed`, `runtimesize` | Selects non-arrayed, constant-indexed, push-constant-indexed, dependent-indexed, or runtime-sized descriptor accesses. | [`indexCases`](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/binding_model/vktBindingDescriptorHeapRandomTests.cpp#L1519-L1525) |
| Uniform-buffer budget | `noubo`, `ubolimitlow`, `ubolimithigh` | Requests zero, 12, or 4096 per-stage uniform buffers during random layout generation. | [`uboCases`](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/binding_model/vktBindingDescriptorHeapRandomTests.cpp#L1527-L1531) |
| Storage-buffer budget | `nosbo`, `sbolimitlow`, `sbolimithigh` | Requests zero, 4, or 4096 storage buffers. | [`sboCases`](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/binding_model/vktBindingDescriptorHeapRandomTests.cpp#L1533-L1537) |
| Sampled-image budget | `nosampledimg`, `sampledimglow`, `sampledimghigh` | Controls the shared budget used by uniform texel buffers and combined image samplers. | [`sampledImgCases`](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/binding_model/vktBindingDescriptorHeapRandomTests.cpp#L1539-L1543) |
| Storage-image/texel shape | `outimgonly`, `outimgtexlow`, `lowimgnotex`, `lowimgsingletex` | Varies output-only storage image, storage texel buffers, and additional storage images. | [`sImgTexCases`](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/binding_model/vktBindingDescriptorHeapRandomTests.cpp#L1545-L1551) |
| Shader stage | `comp`, `vert`, `frag` | Runs the generated checking shader as compute, vertex, or fragment work. | [`stageCases`](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/binding_model/vktBindingDescriptorHeapRandomTests.cpp#L1553-L1558) |
| Input attachments | `noia`, `ialimitlow` | Omits input attachments or allows four in fragment cases. | [`iaCases`](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/binding_model/vktBindingDescriptorHeapRandomTests.cpp#L1561-L1565) |
| Seed | `0`, `1`, `2` where selected | Selects independent random layouts for a subset of low-limit `sets4` combinations; other combinations use seed `0`. | [`numSeeds`](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/binding_model/vktBindingDescriptorHeapRandomTests.cpp#L1609-L1615) |

## Behavior Parameters

### Random descriptor layout — generated resource topology

`generateRandomLayout` chooses zero or more bindings per set, with at most `128 / numDescriptorSets` bindings per set. Set zero binding zero is reserved for the output storage image. Other bindings are randomly selected from uniform/storage buffers, storage texel buffers, storage images, uniform texel buffers, combined image samplers, and—only for fragment cases—input attachments. Array sizes are zero for `noarray`; indexed modes can generate arrays up to 32 elements. [`generateRandomLayout`](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/binding_model/vktBindingDescriptorHeapRandomTests.cpp#L181-L249)

### Indexing mode — descriptor access

The generated GLSL keeps ordinary `layout(set, binding)` declarations, but the host supplies per-stage mapping ranges that point those declarations at heap offsets. Indexed cases use the generated array size and emit access expressions appropriate to the selected mode. The test consequently checks that heap mapping remains correct when indexing is constant, push-constant-derived, dependent, or runtime-sized, rather than only when every access is statically scalar.

### Shader stage — execution context

Compute cases dispatch the checking shader directly. Vertex and fragment cases build a graphics pipeline; fragment cases may additionally consume input attachments. Stage-specific feature checks protect shader writes and fragment input-attachment limits. [`DescriptorHeapRandomCase::checkSupport`](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/binding_model/vktBindingDescriptorHeapRandomTests.cpp#L450-L497)

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.binding_model.descriptor_heap_random.sets4.unifindexed.noubo.nosbo.nosampledimg.outimgonly.comp.noia.0
```

| Parameter choice | Meaning in this representative case |
|---|---|
| Sets / indexing | `sets4` / `unifindexed` |
| Budgets / stage | `noubo`, `nosbo`, `nosampledimg`, `outimgonly`, `comp` |

#### Purpose

Show the generated descriptor declarations, heap mapping, and mismatch accumulator for the simplest compute case. The exact declaration list is generated from the seeded layout; the invariant is that each descriptor value equals its global index.

#### Structural Design

The output storage image is reserved at set 0/binding 0. Other descriptors are assigned aligned heap slots and mapped through `VkDescriptorSetAndBindingMappingEXT`.

- output image: set 0, binding 0;
- backing values: one aligned slot per descriptor;
- mapping: each ordinary set/binding declaration maps to a heap range.

#### Shader Code

For this output-only case, every non-output descriptor budget is zero. The layout therefore emits only `simage0_0`; no descriptor-value checks are generated. `unifindexed` still emits the push-constant declaration, and the compute wrapper retains its invocation index and accumulator variables ([generator](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapRandomTests.cpp#L499-L703)).

```glsl
#version 450 core
#extension GL_EXT_nonuniform_qualifier : enable
layout(push_constant, std430) uniform PushBlock { int identity[32]; } pc;
layout(r32i, set = 0, binding = 0) uniform iimage2D simage0_0;
layout(local_size_x = 1, local_size_y = 1) in;
void main()
{
  const int invocationID = int(gl_GlobalInvocationID.y) * 8 + int(gl_GlobalInvocationID.x);
  int accum = 0, temp;
  ivec4 color = (accum != 0) ? ivec4(0,0,0,0) : ivec4(1,0,0,1);
  imageStore(simage0_0, ivec2(gl_GlobalInvocationID.xy), color);
}
```

#### Additional Info

- The source generator is authoritative for the layout-specific module.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---|---|---|
| Indexing | `noarray`, `constant`, `unifindexed`, `dynindexed`, `runtimesize` | [`indexCases`](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/binding_model/vktBindingDescriptorHeapRandomTests.cpp#L1519-L1525) |
| Stage | `comp`, `vert`, `frag` | [`stageCases`](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/binding_model/vktBindingDescriptorHeapRandomTests.cpp#L1553-L1558) |

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
; Bound: 53
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_GlobalInvocationID %simage0_0 %pc
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpSourceExtension "GL_EXT_nonuniform_qualifier"
               OpName %main "main"
               OpName %invocationID "invocationID"
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
               OpName %accum "accum"
               OpName %color "color"
               OpName %simage0_0 "simage0_0"
               OpName %PushBlock "PushBlock"
               OpMemberName %PushBlock 0 "identity"
               OpName %pc "pc"
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %simage0_0 Binding 0
               OpDecorate %simage0_0 DescriptorSet 0
               OpDecorate %_arr_int_uint_32 ArrayStride 4
               OpDecorate %PushBlock Block
               OpMemberDecorate %PushBlock 0 Offset 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
%_ptr_Function_int = OpTypePointer Function %int
       %uint = OpTypeInt 32 0
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
     %uint_1 = OpConstant %uint 1
%_ptr_Input_uint = OpTypePointer Input %uint
      %int_8 = OpConstant %int 8
     %uint_0 = OpConstant %uint 0
      %int_0 = OpConstant %int 0
      %v4int = OpTypeVector %int 4
%_ptr_Function_v4int = OpTypePointer Function %v4int
       %bool = OpTypeBool
         %33 = OpConstantComposite %v4int %int_0 %int_0 %int_0 %int_0
      %int_1 = OpConstant %int 1
         %35 = OpConstantComposite %v4int %int_1 %int_0 %int_0 %int_1
         %37 = OpTypeImage %int 2D 0 0 0 2 R32i
%_ptr_UniformConstant_37 = OpTypePointer UniformConstant %37
  %simage0_0 = OpVariable %_ptr_UniformConstant_37 UniformConstant
     %v2uint = OpTypeVector %uint 2
      %v2int = OpTypeVector %int 2
    %uint_32 = OpConstant %uint 32
%_arr_int_uint_32 = OpTypeArray %int %uint_32
  %PushBlock = OpTypeStruct %_arr_int_uint_32
%_ptr_PushConstant_PushBlock = OpTypePointer PushConstant %PushBlock
         %pc = OpVariable %_ptr_PushConstant_PushBlock PushConstant
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
%invocationID = OpVariable %_ptr_Function_int Function
      %accum = OpVariable %_ptr_Function_int Function
      %color = OpVariable %_ptr_Function_v4int Function
         %15 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_1
         %16 = OpLoad %uint %15
         %17 = OpBitcast %int %16
         %19 = OpIMul %int %17 %int_8
         %21 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %22 = OpLoad %uint %21
         %23 = OpBitcast %int %22
         %24 = OpIAdd %int %19 %23
               OpStore %invocationID %24
               OpStore %accum %int_0
         %30 = OpLoad %int %accum
         %32 = OpINotEqual %bool %30 %int_0
         %36 = OpSelect %v4int %32 %33 %35
               OpStore %color %36
         %40 = OpLoad %37 %simage0_0
         %42 = OpLoad %v3uint %gl_GlobalInvocationID
         %43 = OpVectorShuffle %v2uint %42 %42 0 1
         %45 = OpBitcast %v2int %43
         %46 = OpLoad %v4int %color
               OpImageWrite %40 %45 %46 SignExtend
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The instance first assigns every descriptor element a global index and allocates an aligned backing buffer with one value slot per descriptor. It creates a resource heap sized from descriptor stride and heap alignment, including the reserved range required by the extension. [`DescriptorHeapRandomInstance::iterate`](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/binding_model/vktBindingDescriptorHeapRandomTests.cpp#L844-L917)
- It creates image resources, writes resource descriptors into the heap, and builds the per-stage binding mappings. Combined image samplers share one nearest sampler descriptor in the sampler heap. [`iterate`](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/binding_model/vktBindingDescriptorHeapRandomTests.cpp#L932-L1058)
- Before execution, the command buffer clears participating images and inserts image barriers to transition them to the layouts required by storage, sampled, or input-attachment access. It binds the resource heap and, when needed, the sampler heap, then dispatches or draws the selected stage.
- The output image is copied to a transfer buffer. Shader-written storage images are also copied to a readback buffer. The host checks the output accumulator and written values; a nonzero mismatch accumulator or an unexpected written value fails the case. [`iterate`](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/binding_model/vktBindingDescriptorHeapRandomTests.cpp#L1260-L1355)

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `noarray` | Incorrect scalar descriptor mapping, descriptor encoding, or resource-address calculation. |
| `constant`, `unifindexed` | Incorrect mapping of array elements or lowering of constant/push-constant indexing. |
| `dynindexed` | Incorrect dynamic descriptor-array indexing, mapping range, or descriptor address calculation. |
| `runtimesize` | Incorrect runtime descriptor-array length or heap mapping for a runtime-sized declaration. |
| `sets4`, `sets8` | Incorrect set-to-mapping translation, especially for higher-numbered sets. |
| `comp`, `vert`, `frag` | Stage-specific pipeline, descriptor, image-layout, or heap-binding error. |

### Cause Analysis

#### Heap mapping or descriptor encoding

**Possible failure symptoms:** The output mismatch accumulator is nonzero, or a storage descriptor written by the shader does not contain its expected global index.

**Possible implementation causes:** The implementation may translate a set/binding/array-element mapping to the wrong heap offset, encode a resource descriptor incorrectly, or apply the wrong descriptor stride or alignment.

#### Shader indexing and generated declarations

**Possible failure symptoms:** Scalar and constant cases pass while dependent or runtime-sized indexed cases fail, or only some array elements report mismatches.

**Possible implementation causes:** Source-level investigation is needed to distinguish shader compiler lowering from descriptor-heap indexing semantics; the failure is localized by the registered indexing mode and the generated layout.

#### Stage or image-access handling

**Possible failure symptoms:** Compute cases pass but vertex/fragment cases fail, or output/readback images contain unexpected values.

**Possible implementation causes:** The issue may be in stage-specific descriptor mapping, graphics pipeline setup, image layout transitions, input-attachment access, or synchronization between shader writes and transfer reads.

## Case Pruning

### Requirement-based pruning

- Every case requires `VK_EXT_descriptor_heap`, `VK_KHR_shader_untyped_pointers`, `VK_KHR_maintenance5`, and `VK_KHR_buffer_device_address`.
- The device must expose `descriptorHeap`, shader untyped pointers, maintenance5, buffer device address, and the indexing features required by the selected case.
- Runtime-sized cases require `runtimeDescriptorArray`; vertex and fragment cases require their corresponding pipeline-store feature. Input-attachment counts are checked against `maxPerStageDescriptorInputAttachments`. [`initDeviceCapabilities` and `checkSupport`](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/binding_model/vktBindingDescriptorHeapRandomTests.cpp#L422-L497)

### Design-based pruning

- Partial combinations of multiple high limits are removed: only none, one, or all three of the high uniform-buffer, storage-buffer, and sampled-image budgets are retained.
- Partial combinations of zero uniform-buffer, storage-buffer, and sampled-image budgets are removed for the same reason.
- Multiple storage-image shapes require an indexed mode; non-indexed cases cannot meaningfully exercise those arrays.
- Input attachments are registered only for fragment cases, and the output image is always retained so every generated layout has a pass/fail destination. [`populateDescriptorHeapRandomTests`](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/binding_model/vktBindingDescriptorHeapRandomTests.cpp#L1580-L1607)

## Key Takeaways

- The test validates descriptor-heap translation against ordinary set/binding shader declarations rather than replacing those declarations with heap-specific source syntax.
- Global descriptor indices make every generated resource independently checkable, including descriptor-array elements and multiple descriptor types.
- Random layout generation is constrained by the selected descriptor budgets and stage legality, while the registration matrix deliberately removes redundant partial limit combinations.
- A passing case demonstrates that the selected generated layout, mapping, shader indexing mode, stage, and resource-access path agree; it does not establish support for unregistered combinations.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| `createDescriptorHeapRandomTests` | [`vktBindingDescriptorHeapRandomTests.cpp#L1679-L1683`](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/binding_model/vktBindingDescriptorHeapRandomTests.cpp#L1679-L1683) | Registers `descriptor_heap_random`. |
| `populateDescriptorHeapRandomTests` | [`#L1501-L1674`](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/binding_model/vktBindingDescriptorHeapRandomTests.cpp#L1501-L1674) | Builds the complete parameter matrix and pruning rules. |
| `generateRandomLayout` | [`#L181-L337`](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/binding_model/vktBindingDescriptorHeapRandomTests.cpp#L181-L337) | Generates bindings, arrays, and write selections. |
| `DescriptorHeapRandomCase::initPrograms` | [`#L499-L748`](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/binding_model/vktBindingDescriptorHeapRandomTests.cpp#L499-L748) | Generates the checking shaders. |
| `DescriptorHeapRandomInstance::iterate` | [`#L844-L1498`](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/binding_model/vktBindingDescriptorHeapRandomTests.cpp#L844-L1498) | Creates heaps/resources, executes cases, and checks results. |
| `binding-model.txt` | [`descriptor_heap_random`](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/mustpass/main/vk-default/binding-model.txt#L11062-L11140) | Confirms registered mustpass paths. |
