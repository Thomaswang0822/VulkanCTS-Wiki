## Overview

**Core question:** Do inline uniform block writes and descriptor copies put each four-byte-aligned range at the requested byte offsets before shader access?

- [`vktBindingDescriptorInlineUniformTests.cpp`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp) implements `binding_model.inline_uniform_blocks`.
- The family contains four write cases and five copy cases. They vary complete and partial byte counts, a nonzero write destination, a nonzero copy destination, and a nonzero copy source.
- The host creates descriptor-set-backed inline uniform blocks, applies writes and copies, then renders a fragment shader that compares the updated members with host-side expected values.
- The host copies the `1 x 16` color image back and requires every pixel to match the exact green reference. A non-green pixel means that the tested descriptor operation or a later observation step did not produce the expected data.

## Background Knowledge

For the shared concepts of descriptor interfaces, writes, and copies, see [Background Knowledge](../../categories/binding_model.md#background-knowledge) of the `binding_model` page.

- **Inline uniform block storage.** `VK_DESCRIPTOR_TYPE_INLINE_UNIFORM_BLOCK` stores uniform-like data in the descriptor set instead of in a separate buffer object. In a descriptor-set layout, `descriptorCount` is the binding capacity in bytes. The capacity must be a multiple of four ([inline uniform block](../../../../vulkan-docs/src/chapters/descriptors.adoc#L430-L458), [`VkDescriptorSetLayoutBinding`](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L435-L452)).
- **Byte offsets and counts.** For an inline uniform block write, `dstArrayElement` is the destination byte offset and `descriptorCount` is the number of bytes updated. The data comes from `VkWriteDescriptorSetInlineUniformBlock` in `pNext`, whose `dataSize` equals `descriptorCount` and is also four-byte aligned ([`VkWriteDescriptorSet`](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3059-L3093), [`VkWriteDescriptorSetInlineUniformBlock`](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3714-L3743)). For a copy, `srcArrayElement` and `dstArrayElement` are the source and destination byte offsets, and `descriptorCount` is the number of bytes copied ([`VkCopyDescriptorSet`](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3888-L3925)).
- **Shader representation.** The shader accesses an inline uniform block as a `Uniform` block with an `OpTypeStruct`; the generated GLSL names one `int` member for each four-byte slot. The set and binding numbers must agree with the descriptor-set layout ([inline uniform block interface](../../../../vulkan-docs/src/chapters/interfaces.adoc#L1316-L1326)).

## Registration Hierarchy

```text
binding_model.inline_uniform_blocks
├── write_size_4
├── write_size_8
├── write_size_16
├── write_offset_nonzero
├── copy_size_4
├── copy_size_8
├── copy_size_16
├── copy_at_offset_nonzero
└── copy_from_offset_nonzero
```

The parent binding-model factory attaches this family under `binding_model` ([`createChildren()`](../../../modules/vulkan/binding_model/vktBindingModelTests.cpp#L52-L72)). The family factory creates the `inline_uniform_blocks` test family and adds the write and copy leaves ([`createDescriptorInlineUniformTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L846-L853)). The nine exact leaves appear in the default mustpass list ([`binding-model.txt`](../../../mustpass/main/vk-default/binding-model.txt#L46183-L46191)).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Operation kind | `write`, `copy` | Selects whether the tested range is sourced from host memory through `VkWriteDescriptorSetInlineUniformBlockEXT` or from another descriptor binding through `VkCopyDescriptorSet`. | [`DescriptorOps`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L280-L385) |
| Write case | `write_size_4`, `write_size_8`, `write_size_16`, `write_offset_nonzero` | Selects a 4, 8, or 16 byte write, or an 8 byte write at destination offset 4 in a 16 byte binding. | [`createInlineUniformWriteTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L766-L798) |
| Copy case | `copy_size_4`, `copy_size_8`, `copy_size_16`, `copy_at_offset_nonzero`, `copy_from_offset_nonzero` | Selects a 4, 8, or 16 byte copy, a copy to destination offset 4, or a copy from source offset 4. | [`createInlineUniformCopyTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L800-L843) |
| Binding capacity | `4`, `8`, `16` bytes | Determines the number of generated four-byte `int` members in each descriptor block. | [`InlineUniformBlockDescriptor`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L78-L147) |
| Byte ranges | offsets `0`, `4`; sizes `4`, `8`, `16` | Selects the source and destination slots. All registered offsets and sizes are multiples of four. | [`InlineUniformBlockWrite`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L160-L211), [`InlineUniformBlockCopy`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L215-L272) |
| Descriptor locations | set `0`; write binding `0`; copy source binding `0`, destination binding `1` | Keeps the descriptor layout fixed while changing the operation range. | [`createInlineUniformWriteTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L766-L798), [`createInlineUniformCopyTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L800-L843) |
| Build and support availability | source excluded by `CTS_USES_VULKANSC`; runtime requires `VK_EXT_inline_uniform_block` | Removes the family from Vulkan SC builds and skips devices without inline uniform block functionality. | [`#ifndef CTS_USES_VULKANSC`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L65-L80), [`checkSupport()`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L669-L702) |

The cases use 4, 8, and 16 bytes because the source models one unique `uint32_t` value per four-byte slot. They are not a matrix of invalid alignments. Vulkan requires inline uniform binding capacities, write offsets, write sizes, copy offsets, and copy sizes to satisfy the relevant four-byte rules ([layout validity](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L533-L549), [write validity](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3280-L3293), [copy validity](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3972-L3986)).

## Behavior Parameters

The primary behavioral axis is the operation shape. The five values below group the exact leaves by the range behavior that changes what the test exercises.

### `complete_write_sizes`: Write an entire binding

`write_size_4`, `write_size_8`, and `write_size_16` create one descriptor at set 0, binding 0, then write the complete 4, 8, or 16 byte binding from offset 0. Each operation checks that the requested number of four-byte words reaches the inline uniform block and remains readable in the fragment shader.

### `nonzero_write_destination`: Write a partial range at a destination offset

`write_offset_nonzero` creates a 16 byte binding and writes 8 bytes at destination byte offset 4. The test therefore exercises a range that begins at the second four-byte slot rather than at the start of the block. The source marks the updated range in its host-side status model and emits shader comparisons for the slots that its model marks as updated.

### `complete_copy_sizes`: Copy an entire binding

`copy_size_4`, `copy_size_8`, and `copy_size_16` create source binding 0 and destination binding 1 with matching capacities, then copy the complete 4, 8, or 16 byte range from offset 0 to offset 0. The source writes both descriptors before issuing the copy so that the source range contains initialized values.

### `nonzero_copy_destination`: Copy into a nonzero destination offset

`copy_at_offset_nonzero` creates two 16 byte bindings and copies 8 bytes from source offset 0 to destination offset 4. A correct copy changes the destination range beginning at its second four-byte slot while leaving the rest of the destination binding outside the requested range untouched by that copy.

### `nonzero_copy_source`: Copy from a nonzero source offset

`copy_from_offset_nonzero` creates two 16 byte bindings and copies 8 bytes from source offset 4 to destination offset 0. This distinguishes source range selection from destination range selection. The destination must receive the source's second and third four-byte words.

`DescriptorOps::updateVerificationData` records the source data expected in the destination for each copy. `writeDescriptor` and `copyDescriptor` then record the Vulkan update operations and their host-side update status ([operation bookkeeping](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L336-L385)).

## Shader Analysis

The family uses one generated fragment-shader pattern for all nine leaves. The descriptor declarations change with the operation model's capacities, but the comparison and color-selection logic stays the same. The walkthrough below uses the smallest registered case, `write_size_4`, because it exposes one complete write without adding a second shader stage or a redundant offset variant. The full SPIR-V was generated from the reconstructed GLSL with the [default CTS source-collection target](../../../framework/vulkan/vkPrograms.cpp#L1048-L1052), `spirv1.0`, validated with `spirv-val`, and disassembled with `spirv-dis`.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.binding_model.inline_uniform_blocks.write_size_4
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `write_size_4` | The descriptor binding has 4 bytes, the host writes 4 bytes, and the shader declares one `int data1` member. |
| set `0`, binding `0` | The shader resource and the host-created descriptor-set layout use the same descriptor location. |
| destination offset `0` | The write begins at the first byte of the binding. |

#### Purpose

The fragment shader reads the one four-byte member written by the host. It selects green when the value is `1`, which is the first value assigned by the operation model, and selects a diagnostic magenta color otherwise.

#### Structural Design

| Phase | Shader operation | Observable result |
|-------|------------------|--------------------|
| Initialize | Set local `result` to `1`. | Assume the descriptor value is correct. |
| Read and compare | Load `iub0.data1` and compare it with `1`. | A mismatch changes `result` to `0`. |
| Emit | Choose the output color from `result`. | Green means the comparison passed; magenta means it failed. |

#### Shader Code

```glsl
#version 450
#extension GL_EXT_debug_printf : enable

/// Set 0, binding 0 is a four-byte inline uniform block. Its only member must contain the host-written value 1.
layout(set=0, binding=0) uniform Iub0
{
    int data1;
} iub0;

/// Green means the inline uniform value matched. Any failed comparison selects the non-green diagnostic color.
layout (location = 0) out vec4 outColor;
void main()
{
    int result = 1;
    if(iub0.data1 != 1) result = 0;
    if (result == 1)
        outColor = vec4(0, 1, 0, 1);
    else
        outColor = vec4(1, 0, 1, 0);
}
```

#### Additional Info

- The source generator creates the block declaration from the modeled descriptor size, then emits one comparison for each member whose update status is not `UPD_STATUS_NONE` ([fragment generation](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L721-L763)).
- The extension line is present in the generated source even though this fragment does not call `debugPrintfEXT`; the source inserts it unconditionally before generating descriptor declarations.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Binding capacity | A 4, 8, or 16 byte descriptor produces 1, 2, or 4 `int` members. | [`initPrograms()`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L721-L735) |
| Operation range | The GLSL block shape follows descriptor capacity, while the host-side update structures select write or copy offsets and byte counts. | [`DescriptorInlineUniformTestInstance::iterate()`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L512-L573), [`createInlineUniformCopyTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L800-L843) |
| Expected values and status | The generated comparisons use host-side verification data only for slots marked as written or copied. | [`initPrograms()`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L743-L755) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `frag`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 34
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %outColor
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 450
               OpSourceExtension "GL_EXT_debug_printf"
               OpName %main "main"
               OpName %result "result"
               OpName %Iub0 "Iub0"
               OpMemberName %Iub0 0 "data1"
               OpName %iub0 "iub0"
               OpName %outColor "outColor"
               OpDecorate %Iub0 Block
               OpMemberDecorate %Iub0 0 Offset 0
               OpDecorate %iub0 Binding 0
               OpDecorate %iub0 DescriptorSet 0
               OpDecorate %outColor Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
%_ptr_Function_int = OpTypePointer Function %int
      %int_1 = OpConstant %int 1
       %Iub0 = OpTypeStruct %int
%_ptr_Uniform_Iub0 = OpTypePointer Uniform %Iub0
       %iub0 = OpVariable %_ptr_Uniform_Iub0 Uniform
      %int_0 = OpConstant %int 0
%_ptr_Uniform_int = OpTypePointer Uniform %int
       %bool = OpTypeBool
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Output_v4float = OpTypePointer Output %v4float
   %outColor = OpVariable %_ptr_Output_v4float Output
    %float_0 = OpConstant %float 0
    %float_1 = OpConstant %float 1
         %31 = OpConstantComposite %v4float %float_0 %float_1 %float_0 %float_1
         %33 = OpConstantComposite %v4float %float_1 %float_0 %float_1 %float_0
       %main = OpFunction %void None %3
          %5 = OpLabel
     %result = OpVariable %_ptr_Function_int Function
               OpStore %result %int_1
         %15 = OpAccessChain %_ptr_Uniform_int %iub0 %int_0
         %16 = OpLoad %int %15
         %18 = OpINotEqual %bool %16 %int_1
               OpSelectionMerge %20 None
               OpBranchConditional %18 %19 %20
         %19 = OpLabel
               OpStore %result %int_0
               OpBranch %20
         %20 = OpLabel
         %21 = OpLoad %int %result
         %22 = OpIEqual %bool %21 %int_1
               OpSelectionMerge %24 None
               OpBranchConditional %22 %23 %32
         %23 = OpLabel
               OpStore %outColor %31
               OpBranch %24
         %32 = OpLabel
               OpStore %outColor %33
               OpBranch %24
         %24 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- `DescriptorInlineUniformTestInstance::iterate` first totals the modeled descriptor sizes and creates a descriptor pool with `VK_DESCRIPTOR_TYPE_INLINE_UNIFORM_BLOCK_EXT`. The pool's inline-uniform-block create structure supplies the number of inline uniform block descriptors required by the case ([descriptor pool](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L486-L510)).
- For each set, the host creates one descriptor-set layout binding per modeled descriptor. The binding type is `VK_DESCRIPTOR_TYPE_INLINE_UNIFORM_BLOCK_EXT`, its count is the descriptor's byte size, and its stage flag is `VK_SHADER_STAGE_FRAGMENT_BIT`. The host allocates one descriptor set for each set map entry ([layout creation](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L512-L543)).
- For every write operation, the host builds `VkWriteDescriptorSetInlineUniformBlockEXT` with `dataSize` equal to the requested write size and `pData` pointing at the descriptor model's source words. It passes the operation's destination binding, byte offset, and byte count to the descriptor update builder ([write construction](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L160-L211), [write submission](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L545-L560)).
- For every copy operation, the host passes the source set, binding, and byte offset together with the destination set, binding, and byte offset to the descriptor update builder. The update call submits all writes and copies together ([copy construction](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L215-L272), [copy submission](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L562-L573)).
- The host creates a `VK_FORMAT_R8G8B8A8_UNORM` color image with extent `1 x 16`, a view, a render pass, and a framebuffer. It creates a host-visible transfer-destination buffer for the image result ([image and result setup](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L583-L603)).
- The fixed vertex shader and generated fragment shader are compiled into the graphics pipeline. The command buffer clears the framebuffer red, binds the pipeline and all descriptor sets, draws six vertices, ends the render pass, and copies the image to the output buffer ([pipeline and draw](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L604-L656)).
- After waiting for the submission, the host invalidates the output allocation and calls `verifyResultImage`. The function compares all `1 x 16` pixels against exact green with a zero threshold. The test returns `Pass` only if every pixel matches; otherwise it returns `Fail("Rendered image(s) are incorrect")` ([verification](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L464-L483), [final status](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L659-L666)).

The shader checks only slots whose `m_updateStatus` is not `UPD_STATUS_NONE`. The source computes `updIdx = offset / 4` and `updSize = size / 4`, then loops while `i < updSize`. For offset zero, this covers the requested slot count. For a nonzero offset, the loop does not use `updIdx + updSize` as its upper bound. For example, offset 4 and size 8 mark only index 1. This is source-side coverage behavior, not a Vulkan definition of the byte range ([`changeStatus`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L109-L155)).

## Failure Meaning

A failure means that the final color did not match the source-generated expected values for the members that the operation model marked as updated. The result alone cannot locate the fault in descriptor update handling, shader access, rendering, image copyback, or host comparison.

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `complete_write_sizes` | Complete inline uniform write handling. |
| `nonzero_write_destination` | Nonzero write destination handling. |
| `complete_copy_sizes` | Complete inline uniform copy handling. |
| `nonzero_copy_destination` | Nonzero copy destination handling. |
| `nonzero_copy_source` | Nonzero copy source handling. |

### Cause Analysis

#### Complete inline uniform write handling

**Possible failure symptoms:** Any of `write_size_4`, `write_size_8`, or `write_size_16` produces a non-green pixel, so one or more generated members does not equal its host-side expected value.

**Possible implementation causes:** The implementation may use the wrong inline uniform binding capacity, copy the wrong `dataSize` bytes from `pData`, apply the wrong destination range, or expose the descriptor block incorrectly to the fragment shader. The layout, write, and shader interface rules independently constrain these operations ([layout binding](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L435-L452), [inline write data](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3714-L3743), [shader interface](../../../../vulkan-docs/src/chapters/interfaces.adoc#L1316-L1326)). The image and host comparison can also report a failure if rendering, transfer, or result interpretation changes the observed color. The pixel symptom does not isolate those paths.

#### Nonzero write destination handling

**Possible failure symptoms:** `write_offset_nonzero` produces a non-green pixel for a member that the source status model marks as written.

**Possible implementation causes:** The update path may interpret `dstArrayElement` as an array element rather than a byte offset, or may copy the requested bytes to the wrong position. The host-side status loop also has a source-specific nonzero-offset behavior, so a mismatch may reflect a comparison range that differs from the intended operation range. The source-level evidence cannot distinguish descriptor offset handling from that bookkeeping or from later shader and readback behavior; the failing case needs source-level investigation.

#### Complete inline uniform copy handling

**Possible failure symptoms:** Any of `copy_size_4`, `copy_size_8`, or `copy_size_16` produces a non-green pixel after both source and destination descriptors have been written.

**Possible implementation causes:** `vkUpdateDescriptorSets` may copy the wrong number of bytes, fail to use the source descriptor's inline-uniform data, or expose stale destination data to the shader. The specification defines `descriptorCount` as the number of bytes for inline uniform copies and requires the source and destination binding types to match ([copy semantics](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3888-L3925), [copy validity](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3964-L3986)). A non-green result may also come from fragment execution, image transfer, or host comparison, which the test's final pixel check does not separate.

#### Nonzero copy destination handling

**Possible failure symptoms:** `copy_at_offset_nonzero` produces a non-green pixel for the destination member that the source model marks as copied.

**Possible implementation causes:** The copy path may treat `dstArrayElement = 4` as a descriptor index instead of the destination byte offset, or may shift the copied bytes to a different slot. The source's `changeStatus` behavior for a nonzero destination offset also limits which members receive generated comparisons. The observed pixel does not identify whether the issue is in the API operation, host bookkeeping, shader access, or result path.

#### Nonzero copy source handling

**Possible failure symptoms:** `copy_from_offset_nonzero` produces a non-green pixel after copying from source byte offset 4 to destination byte offset 0.

**Possible implementation causes:** The copy path may start reading at source slot zero, use the wrong source byte count, or place the selected source range incorrectly in the destination. Vulkan defines `srcArrayElement` as the starting byte offset for an inline uniform source binding and requires four-byte alignment ([copy offsets](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3897-L3904), [copy validity](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3972-L3986)). The source model and final image check cannot separate those possibilities from shader, render, transfer, or host-side causes.

## Case Pruning

### Requirement-based pruning

- The whole implementation is inside `#ifndef CTS_USES_VULKANSC`, so Vulkan SC builds do not register these cases ([build guard](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L65-L80)).
- Each test case calls `context.requireDeviceFunctionality("VK_EXT_inline_uniform_block")`. A device without the required inline uniform block functionality does not execute the case ([support check](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L669-L702)).
- The source uses the extension descriptor type and extension structures, so the required feature and extension path must be available before layout or update creation. The specification says that `VK_DESCRIPTOR_TYPE_INLINE_UNIFORM_BLOCK` cannot be used unless `inlineUniformBlock` is enabled ([inline uniform block feature](../../../../vulkan-docs/src/chapters/features.adoc#L2339-L2377)).
- All registered capacities, offsets, and operation sizes are four-byte aligned. Invalid alignment combinations are not registered because Vulkan's layout, write, and copy validity rules require multiples of four ([layout validity](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L533-L549), [write validity](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3280-L3293), [copy validity](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3972-L3986)).

### Design-based pruning

- The write family uses one descriptor at set 0, binding 0. The copy family uses two descriptors at set 0, bindings 0 and 1. The source does not add unrelated set or binding arrangements because the cases focus on byte counts and source or destination offsets ([case registration](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L766-L843)).
- The family uses complete sizes of 4, 8, and 16 bytes, then adds one nonzero write destination, one nonzero copy destination, and one nonzero copy source. This covers the intended range-selection distinctions without duplicating the same shader pattern for every possible aligned size or offset.
- The source creates the copy source and destination writes before the copy. That ordering is part of the operation model and avoids testing an uninitialized source range ([`copyDescriptor`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L374-L385)).

## Key Takeaways

- Inline uniform block layout counts and update counts are byte counts, while the test's generated shader exposes those bytes as four-byte `int` members.
- A write selects a destination byte range from host data. A copy selects both source and destination byte ranges from descriptor bindings.
- `write_offset_nonzero`, `copy_at_offset_nonzero`, and `copy_from_offset_nonzero` distinguish destination offset handling from source offset handling.
- The fragment shader is an observation mechanism. The host chooses the descriptor operation, expected values, and pass/fail result.
- A green `1 x 16` image means that the source-marked comparisons passed. A failure requires further isolation because the final image check combines descriptor, shader, rendering, transfer, and host-side behavior.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Binding-model category attachment | [`createChildren()`](../../../modules/vulkan/binding_model/vktBindingModelTests.cpp#L52-L72) | Attaches the `inline_uniform_blocks` family under `binding_model`. |
| Descriptor data and slot model | [`InlineUniformBlockDescriptor`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L78-L155) | Defines byte capacity, four-byte slot storage, initial values, verification data, and update status. |
| Write operation | [`InlineUniformBlockWrite`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L160-L211) | Builds `VkWriteDescriptorSetInlineUniformBlockEXT` data and records destination ranges. |
| Copy operation | [`InlineUniformBlockCopy`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L215-L272) | Records source and destination bindings, offsets, and copy size. |
| Operation bookkeeping | [`DescriptorOps`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L280-L385) | Computes expected copy data and orders writes before copies. |
| Descriptor pool, layouts, and updates | [`DescriptorInlineUniformTestInstance::iterate()`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L486-L573) | Creates descriptor resources and submits the tested writes and copies. |
| Generated vertex and fragment programs | [`DescriptorInlineUniformTestCase::initPrograms()`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L699-L763) | Defines the shader-visible blocks, comparisons, and diagnostic colors. |
| Host result check | [`verifyResultImage()`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L464-L483) | Compares the rendered image with exact green. |
| Write case registration | [`createInlineUniformWriteTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L766-L798) | Defines the four exact write leaves. |
| Copy case registration | [`createInlineUniformCopyTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L800-L843) | Defines the five exact copy leaves. |
| Family registration | [`createDescriptorInlineUniformTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L846-L853) | Creates the test family and attaches both operation groups. |
| Default mustpass coverage | [`binding-model.txt`](../../../mustpass/main/vk-default/binding-model.txt#L46183-L46191) | Confirms the nine exact default leaves. |
| Inline uniform block semantics | [Inline Uniform Block](../../../../vulkan-docs/src/chapters/descriptors.adoc#L430-L458) | Defines descriptor-set-backed storage and byte-capacity semantics. |
| Descriptor layout validity | [`VkDescriptorSetLayoutBinding`](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L435-L452) | Defines byte capacity and four-byte alignment. |
| Descriptor write semantics | [`VkWriteDescriptorSet`](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3059-L3159) | Defines destination byte offsets, byte counts, and the `pNext` data source. |
| Inline write structure | [`VkWriteDescriptorSetInlineUniformBlock`](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3714-L3743) | Defines `dataSize`, `pData`, and four-byte data alignment. |
| Descriptor copy semantics | [`VkCopyDescriptorSet`](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3888-L3986) | Defines source and destination byte offsets and copy alignment. |
| Shader interface | [Inline uniform block interface](../../../../vulkan-docs/src/chapters/interfaces.adoc#L1316-L1326) | Defines the `Uniform` and `OpTypeStruct` shader representation. |
| Feature gate | [Inline uniform block features](../../../../vulkan-docs/src/chapters/features.adoc#L2339-L2377) | Defines the required inline uniform block feature. |
