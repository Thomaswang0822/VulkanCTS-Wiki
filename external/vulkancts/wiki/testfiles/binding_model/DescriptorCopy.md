## Overview

**Core question:** Do descriptor copies make the source descriptor state visible through the destination binding in every registered pipeline and layout variant?

- [`vktBindingDescriptorCopyTests.cpp`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp) implements `binding_model.descriptor_copy` and creates the `compute`, `graphics`, `graphics_uab`, and `misc` test families.
- `compute`, `graphics`, and `graphics_uab` generate descriptor-copy cases for multiple descriptor types, array ranges, descriptor-set placements, and copy histories. `graphics_uab` repeats the eligible graphics cases with update-after-bind layouts and post-bind updates.
- `misc` contains four graphics cases that copy combined-image-sampler descriptors with immutable samplers while a storage-buffer binding appears before or after the sampler bindings.
- The page explains how the host reference model tracks copied descriptors, how generated shaders check shader-visible values, how compute and graphics results are validated, and why unsupported or intentionally omitted cases are pruned.

## Background Knowledge

For the shared concepts of descriptor writes, copies, and active state, see [Background Knowledge](../../categories/binding_model.md#background-knowledge) of the `binding_model` page.

- **Descriptor-copy semantics.** `vkUpdateDescriptorSets` applies descriptor writes before descriptor copies. A `VkCopyDescriptorSet` copies the descriptor reference from a source set, binding, and array range to a destination range. It does not use the referenced resource. The source and destination binding types must match, and an in-place copy must not overlap ([descriptor set updates](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L2900-L2951), [`VkCopyDescriptorSet`](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3888-L3971)).
- **Descriptor representations.** Buffer descriptors expose `VkDescriptorBufferInfo`, texel-buffer descriptors expose `VkBufferView` handles, image descriptors expose image views and layouts, and inline uniform blocks expose byte data. For inline uniform blocks, copy offsets and counts are bytes rather than descriptor elements ([descriptor binding counts](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L435-L455), [descriptor-type source members](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3129-L3160)).
- **Immutable samplers.** An immutable sampler is part of the descriptor-set layout and cannot be replaced by a descriptor update. A combined-image-sampler update can still change its image view while the layout-provided sampler remains fixed ([immutable samplers](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L470-L480)).
- **Update-after-bind.** `VK_DESCRIPTOR_BINDING_UPDATE_AFTER_BIND_BIT` permits supported descriptor bindings to be updated after the set is bound. The layout and pool need the corresponding update-after-bind flags, and the device needs a feature matching the descriptor type ([layout flag](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L363-L376), [update-after-bind features](../../../../vulkan-docs/src/chapters/features.adoc#L2078-L2121)).

## Registration Hierarchy

```text
binding_model.descriptor_copy
├── compute
├── graphics
├── graphics_uab
└── misc
```

The parent binding-model factory attaches `descriptor_copy` under `binding_model` ([`createChildren()`](../../../modules/vulkan/binding_model/vktBindingModelTests.cpp#L52-L60)). The descriptor-copy factory creates all four children in [`createDescriptorCopyTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L3754-L3786). These children are implemented in the same source file, so none is registration only.

## Parameter Dimensions and Observed Values

The default Vulkan mustpass file contains 289 descriptor-copy leaves: 99 under `compute`, 111 under `graphics`, 75 under `graphics_uab`, and 4 under `misc` ([mustpass range](../../../mustpass/main/vk-default/binding-model.txt#L10152-L10440)).

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test family | `compute`, `graphics`, `graphics_uab`, `misc` | Selects the execution path and descriptor-layout contract. | [`createDescriptorCopyTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L3754-L3786) |
| Standard descriptor type | `uniform_buffer`, `storage_buffer`, `combined_image_sampler`, `storage_image`, `uniform_texel_buffer`, `storage_texel_buffer` | Selects the resource representation and shader verification operation. | [`createTestsForAllDescriptorTypes()`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L3713-L3728) |
| Inline uniform descriptor type | `inline_uniform_block` | Tests byte-addressed inline uniform data. This value is excluded from Vulkan SC builds. | [`createTestsForAllDescriptorTypes()`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L3729-L3732), [`InlineUniformBlockDescriptor`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L831-L915) |
| Dynamic descriptor type | `uniform_buffer_dynamic`, `storage_buffer_dynamic` | Selects descriptors whose shader read uses a runtime dynamic offset. These values are ordinary compute and graphics cases only. | [`createTestsForAllDescriptorTypes()`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L3734-L3741), [`setDynamicAreas()`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L1666-L1683) |
| Graphics-only descriptor type | `input_attachment` | Tests copied input-attachment views and subpass attachment indices in a fragment shader. | [`createTestsForAllDescriptorTypes()`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L3742-L3747), [`InputAttachmentDescriptor`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L1289-L1351) |
| Descriptor-copy case suffix | `_0` through `_6`, `array0`, `array1`, `array2` | Selects same-set, cross-set, partial, repeated, reverse, non-consecutive-set, and array-range copy shapes. | [`addDescriptorCopyTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L2605-L2865) |
| Descriptor-specific cases | `sampler_0`, `sampler_array0`, `sampler_array1`, `sampled_image_0`, `sampled_image_array0` | Separates standalone sampler and sampled-image copies from combined-image-sampler copies. | [`addSamplerCopyTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L2867-L2939), [`addSampledImageCopyTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L2941-L2986) |
| Mixed descriptor cases | `mix_0`, `mix_1`, `mix_2`, `mix_3`, `mix_array0`, `mix_array1` | Combines descriptor classes and copy ranges in one test. `mix_2` and `mix_3` are graphics-only. | [`addMixedDescriptorCopyTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L2988-L3244) |
| Immutable-sampler count | `1`, `4` | Selects one sampled image or four quadrant-selected sampled images in the `misc` family. | [`createDescriptorCopyTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L3770-L3778) |
| Immutable-sampler binding order | `buffer_first`, no suffix | Places the storage-buffer binding before or after the immutable combined-image-sampler bindings. | [`CopyImmutableSamplerParams`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L3246-L3270), [`CopyImmutableSamplerTest::iterate()`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L3490-L3569) |
| Update-after-bind mode | disabled for `compute` and `graphics`; enabled for `graphics_uab` | Chooses whether descriptor writes and copies occur before binding or after the set is bound. | [`DescriptorCommands::run()`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L1978-L1988), [`DescriptorCommands::run()`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L2122-L2124) |

## Behavior Parameters

The primary behavioral axis is the top-level test family. Each value selects a distinct execution or descriptor-layout contract; the descriptor type and copy-shape dimensions configure the behavior within that family.

### `compute` - Compute verification of copied descriptors

The test builds a compute pipeline and a generated shader that checks each written or copied descriptor. The shader stores `1` in the result storage buffer only when all checks succeed. The family includes dynamic buffers and mixed descriptor cases when update-after-bind is disabled.

### `graphics` - Graphics verification of copied descriptors

The test builds a graphics pipeline with a fixed vertex shader and a generated fragment shader. The fragment shader checks copied descriptors and writes green for success or magenta for failure into a `64 x 64` color attachment. The host copies that image to a buffer and checks every pixel.

### `graphics_uab` - Post-bind graphics descriptor updates

The test uses the graphics verification path with update-after-bind pool, layout, and binding flags. It binds the pipeline and descriptor sets before `updateDescriptorSets` applies the writes and copies. The fragment shader then observes the post-bind state. Dynamic buffers, input attachments, and mixed descriptor cases are not registered in this family.

### `misc` - Immutable-sampler copy layout stress

The test creates two descriptor sets with combined-image-sampler bindings that use one immutable sampler object. It writes image views and separate storage-buffer ranges, copies all sampler descriptors from the first set to the second, and renders with both sets. The `1`-image cases split the framebuffer into two halves; the `4`-image cases select one sampler per quadrant. The storage-buffer position changes the binding offsets that the implementation must preserve.

## Shader Analysis

One representative walkthrough is enough. `compute.uniform_buffer_0` is the smallest case that exposes the generated verification contract: the shader reads a directly written descriptor, reads its copied destination, and returns one combined result to the host. Graphics uses the same generated comparison pattern but converts the result to green or magenta, while `graphics_uab` changes when the host updates descriptors rather than changing the shader logic. The reconstructed shader was compiled for the CTS baseline SPIR-V 1.0 target.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.binding_model.descriptor_copy.compute.uniform_buffer_0
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `compute` | Uses the compute verification path and returns the combined check through a storage buffer. |
| `uniform_buffer` | Generates two uniform blocks whose `data` members make the descriptor copy visible. |
| `_0` | Writes both bindings in set 0, then copies binding 0 over binding 1. |
| `0xabc` source identifier | The first descriptor receives ID `0xabc`, or `2748`; the copied destination must expose that value. |

#### Purpose

The shader checks one directly written uniform-buffer descriptor and the binding overwritten by its copy. It stores `1` only if both bindings expose the source value `2748`.

#### Structural Design

| Phase | Shader operation | Observable meaning |
|-------|------------------|--------------------|
| Declare inputs | Bind `uniformBuffer2748` and `uniformBuffer2749` at set 0 bindings 0 and 1. | Binding 0 is the copy source; binding 1 is the destination. |
| Check source | Compare `uniformBuffer2748.data` with `2748`. | Confirms the source descriptor exposes its initialized buffer. |
| Check destination | Compare `uniformBuffer2749.data` with `2748`. | Confirms the copied destination exposes the same buffer value. |
| Return result | Store `result` through `storageBuffer2750` at binding 2. | Gives the host one integer for the combined shader-visible check. |

#### Shader Code

```glsl
#version 430

/// Binding 0 is the directly written uniform-buffer descriptor. Its buffer starts with the reference value 2748.
layout (set=0, binding=0) uniform UniformBuffer2748
{
    int data;
} uniformBuffer2748;
/// Binding 1 is overwritten by the copy from binding 0 and must expose the same buffer value.
layout (set=0, binding=1) uniform UniformBuffer2749
{
    int data;
} uniformBuffer2749;
/// Binding 2 carries the combined shader check back to the host.
layout (set=0, binding=2) buffer StorageBuffer2750
{
    int data;
} storageBuffer2750;

void main()
{
int result = 1;
/// Check the written source and copied destination against the host reference model.
if (uniformBuffer2748.data != 2748) result = 0;
if (uniformBuffer2749.data != 2748) result = 0;
storageBuffer2750.data = result;
}
```

#### Additional Info

- The source creates this case before the other descriptor-copy leaves. Its descriptors therefore receive IDs `2748`, `2749`, and `2750` from the counter initialized to `0xabc` ([ID initialization](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L615-L623), [case construction](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L2609-L2625)).
- `addResultBuffer()` appends the result storage buffer as the last binding in set 0. The generator skips that binding when it emits descriptor checks, then writes the final `result` into it ([result-buffer setup](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L1645-L1663), [compute generator](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L2537-L2553)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|-----------------------------------------|----------|
| Descriptor type | Buffer descriptors use `.data`; image, texel-buffer, sampler, input-attachment, and inline-uniform descriptors emit their type-specific declarations and reads. | [`getShaderVerifyCode()` implementations](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L886-L1533) |
| Compute versus graphics | Compute writes an integer result buffer. Graphics uses a fixed vertex shader and writes green or magenta from the same sequence of generated checks. | [`DescriptorCopyTestCase::initPrograms()`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L2537-L2585) |
| Update-after-bind | The graphics shader is unchanged. `graphics_uab` moves `updateDescriptorSets` after descriptor-set binding. | [`DescriptorCommands::run()`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L2396-L2427) |
| Copy shape | Array and multi-copy cases add declarations and checks for each written or copied element. | [`DescriptorCommands::getDescriptorVerifications()`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L1636-L1654) |

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
; Bound: 35
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main"
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 430
               OpName %main "main"
               OpName %result "result"
               OpName %UniformBuffer2748 "UniformBuffer2748"
               OpMemberName %UniformBuffer2748 0 "data"
               OpName %uniformBuffer2748 "uniformBuffer2748"
               OpName %UniformBuffer2749 "UniformBuffer2749"
               OpMemberName %UniformBuffer2749 0 "data"
               OpName %uniformBuffer2749 "uniformBuffer2749"
               OpName %StorageBuffer2750 "StorageBuffer2750"
               OpMemberName %StorageBuffer2750 0 "data"
               OpName %storageBuffer2750 "storageBuffer2750"
               OpDecorate %UniformBuffer2748 Block
               OpMemberDecorate %UniformBuffer2748 0 Offset 0
               OpDecorate %uniformBuffer2748 Binding 0
               OpDecorate %uniformBuffer2748 DescriptorSet 0
               OpDecorate %UniformBuffer2749 Block
               OpMemberDecorate %UniformBuffer2749 0 Offset 0
               OpDecorate %uniformBuffer2749 Binding 1
               OpDecorate %uniformBuffer2749 DescriptorSet 0
               OpDecorate %StorageBuffer2750 BufferBlock
               OpMemberDecorate %StorageBuffer2750 0 Offset 0
               OpDecorate %storageBuffer2750 Binding 2
               OpDecorate %storageBuffer2750 DescriptorSet 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
%_ptr_Function_int = OpTypePointer Function %int
      %int_1 = OpConstant %int 1
%UniformBuffer2748 = OpTypeStruct %int
%_ptr_Uniform_UniformBuffer2748 = OpTypePointer Uniform %UniformBuffer2748
%uniformBuffer2748 = OpVariable %_ptr_Uniform_UniformBuffer2748 Uniform
      %int_0 = OpConstant %int 0
%_ptr_Uniform_int = OpTypePointer Uniform %int
   %int_2748 = OpConstant %int 2748
       %bool = OpTypeBool
%UniformBuffer2749 = OpTypeStruct %int
%_ptr_Uniform_UniformBuffer2749 = OpTypePointer Uniform %UniformBuffer2749
%uniformBuffer2749 = OpVariable %_ptr_Uniform_UniformBuffer2749 Uniform
%StorageBuffer2750 = OpTypeStruct %int
%_ptr_Uniform_StorageBuffer2750 = OpTypePointer Uniform %StorageBuffer2750
%storageBuffer2750 = OpVariable %_ptr_Uniform_StorageBuffer2750 Uniform
       %main = OpFunction %void None %3
          %5 = OpLabel
     %result = OpVariable %_ptr_Function_int Function
               OpStore %result %int_1
         %15 = OpAccessChain %_ptr_Uniform_int %uniformBuffer2748 %int_0
         %16 = OpLoad %int %15
         %19 = OpINotEqual %bool %16 %int_2748
               OpSelectionMerge %21 None
               OpBranchConditional %19 %20 %21
         %20 = OpLabel
               OpStore %result %int_0
               OpBranch %21
         %21 = OpLabel
         %25 = OpAccessChain %_ptr_Uniform_int %uniformBuffer2749 %int_0
         %26 = OpLoad %int %25
         %27 = OpINotEqual %bool %26 %int_2748
               OpSelectionMerge %29 None
               OpBranchConditional %27 %28 %29
         %28 = OpLabel
               OpStore %result %int_0
               OpBranch %29
         %29 = OpLabel
         %33 = OpLoad %int %result
         %34 = OpAccessChain %_ptr_Uniform_int %storageBuffer2750 %int_0
               OpStore %34 %33
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

### Common descriptor setup

- Each descriptor object receives a deterministic ID starting at `0xabc`. Its backing buffer or image is initialized with a value derived from that ID and array element. The host stores whether each element was written directly and whether a copy overwrote it ([descriptor initialization](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L618-L641)).
- `DescriptorCommands::copyDescriptor()` records source and destination set, binding, array element, and count for the Vulkan update. It also updates the reference model by copying the source data into the destination model. For inline uniform blocks it converts integer element indices to byte offsets and counts before creating `VkCopyDescriptorSet` ([copy recording](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L1590-L1615)).
- Support checks reject too many descriptor sets or descriptors for device limits. `graphics_uab` requires `VK_EXT_descriptor_indexing`; the source checks the matching update-after-bind feature for the standard buffer, image, sampler, and texel-buffer types. Inline uniform block cases also query inline-uniform support and properties ([support checks](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L1695-L1943)).
- The descriptor pool counts each descriptor type. The descriptor-set layouts use one binding per descriptor object and the selected shader stage. Update-after-bind cases add the pool, layout, and binding flags before allocating their sets ([pool and layout creation](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L1978-L2124)).

### Compute path

- The host initializes all descriptor resources, allocates the descriptor sets, writes directly initialized elements, and records the descriptor copies.
- The host creates a compute pipeline from the generated `compute` shader and binds all descriptor sets. Dynamic cases pass the selected dynamic offsets in 256-byte units.
- The host dispatches one workgroup. The compute shader checks every element marked written or copied and writes the final `result` to the storage-buffer descriptor added as the last binding in set 0.
- The host invalidates that allocation and reads the first integer. `1` returns `Pass`; any other value returns `Data validation failed` ([compute setup and check](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L2146-L2173), [dispatch and result](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L2384-L2441)).

### Graphics path

- The host initializes descriptor resources and images. Image descriptors are cleared to their reference value and transitioned from transfer-destination layout to the descriptor class's shader-readable layout.
- The host creates a `64 x 64` color attachment, a render pass, a framebuffer, and a graphics pipeline with the generated vertex and fragment shaders. Input-attachment descriptors contribute framebuffer attachments and subpass references.
- The host binds the pipeline and descriptor sets, draws six vertices for a full-screen quad, ends the render pass, and copies the result image to a host-visible buffer.
- Every pixel must equal `(0, 1, 0, 1)`. A different pixel is logged and returns `Result image validation failed` ([graphics resources](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L2175-L2381), [draw and result scan](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L2396-L2465)).

### Graphics update-after-bind path

- The host creates the same graphics resources, but uses `VK_DESCRIPTOR_POOL_CREATE_UPDATE_AFTER_BIND_BIT`, `VK_DESCRIPTOR_SET_LAYOUT_CREATE_UPDATE_AFTER_BIND_POOL_BIT`, and `VK_DESCRIPTOR_BINDING_UPDATE_AFTER_BIND_BIT`.
- The host binds the graphics pipeline and descriptor sets before calling `updateDescriptorSets`. That call performs the direct writes first and the recorded copies second, matching the specification's operation order.
- The host draws the full-screen quad after the post-bind update. The fragment shader checks the copied descriptor state, and the host applies the same all-green image check as the ordinary graphics path ([post-bind update](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L2384-L2427), [operation order](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L2917-L2934)).

### Immutable-sampler path

- The host creates one or four `1 x 1` sampled images, one immutable sampler, two descriptor sets, and a storage buffer whose first half contains red values of `0.5` and whose aligned second half contains red values of `1.0`.
- The first descriptor set receives all image views and the first storage-buffer range. The second receives the second storage-buffer range, then receives one copy operation covering all immutable combined-image-sampler descriptors.
- The vertex shader passes a quadrant value. The fragment shader selects one sampler for each quadrant when four images are present, samples at `(0, 0)`, and replaces the sampled red channel with `inBuffer.red`.
- The host draws half the vertices with each descriptor set, copies the `2 x 2` framebuffer to host memory, and compares it with a reference image using a `0.005` threshold ([immutable-sampler setup and copy](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L3380-L3569), [draw and comparison](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L3634-L3708)).

## Failure Meaning

A failure means that the case's descriptor-copy contract did not produce the expected shader-visible value or framebuffer. The result does not identify a driver, hardware, compiler, or host location by itself. The failing family and exact suffix narrow the contract that needs investigation.

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `compute` | Descriptor copy or descriptor-type handling failure visible through the verification compute shader, dynamic-offset or inline-uniform byte-range handling failure, or compute result-buffer failure. |
| `graphics` | Descriptor copy or descriptor-type handling failure visible through the verification fragment shader, graphics resource or input-attachment setup failure, or result-image failure. |
| `graphics_uab` | Incorrect update-after-bind layout, feature, post-bind update, or descriptor-copy behavior, or graphics result-image failure. |
| `misc` | Immutable-sampler copy sizing or binding-order failure, incorrect sampled image or storage-buffer descriptor state, or framebuffer/reference construction failure. |

### Cause Analysis

#### Descriptor copy or descriptor-type handling failure visible through the verification compute shader, dynamic-offset or inline-uniform byte-range handling failure, or compute result-buffer failure

**Possible failure symptoms:** The compute result buffer contains `0` and the case reports `Data validation failed`. The failed case may be a scalar descriptor, an array-range copy, a dynamic-buffer case, a mixed descriptor case, or an inline-uniform block case.

**Possible implementation causes:** The implementation may copy the wrong descriptor reference, use the wrong descriptor type representation, apply a dynamic offset to the wrong buffer range, or interpret inline-uniform copy indices as elements instead of bytes. The host model and the Vulkan rules establish the expected source and destination ranges, but a zero result cannot isolate descriptor lookup, shader resource access, dynamic-offset application, or result-buffer handling. The exact failing case needs source-level investigation.

#### Descriptor copy or descriptor-type handling failure visible through the verification fragment shader, graphics resource or input-attachment setup failure, or result-image failure

**Possible failure symptoms:** One or more pixels are not `(0, 1, 0, 1)`, and the test reports `Result image validation failed`. Input-attachment cases can also fail if a copied attachment index or framebuffer attachment does not match the descriptor visible to the fragment shader.

**Possible implementation causes:** The implementation may expose the wrong copied image view, buffer view, sampler, buffer range, or inline-uniform data to the shader. It may also create an incorrect input-attachment mapping, image layout transition, render-pass attachment, draw result, or image-to-buffer copy. The source and descriptor specification define the intended descriptor type and resource members, but the uniform green or magenta result cannot distinguish descriptor state from graphics setup or readback behavior. The exact failing case needs source-level investigation.

#### Incorrect update-after-bind layout, feature, post-bind update, or descriptor-copy behavior, or graphics result-image failure

**Possible failure symptoms:** A `graphics_uab` case fails support checks, fails during descriptor update, or produces a non-green result image after the descriptor set was bound. A successful API call followed by a wrong pixel means the fragment shader did not observe the expected post-bind descriptor state or the graphics result path failed.

**Possible implementation causes:** The implementation may mishandle the required update-after-bind pool and layout flags, apply the wrong per-type update-after-bind feature rule, fail to make a post-bind write or copy visible, or process the copy before the write despite the required order. The Vulkan specification requires update-after-bind layout compatibility for copies and defines the per-type feature requirements ([copy compatibility](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3987-L4020), [feature requirements](../../../../vulkan-docs/src/chapters/features.adoc#L2078-L2121)). A framebuffer mismatch can still come from graphics setup or readback, so the exact failing case needs source-level investigation.

#### Immutable-sampler copy sizing or binding-order failure, incorrect sampled image or storage-buffer descriptor state, or framebuffer/reference construction failure

**Possible failure symptoms:** One or more quadrants in the `2 x 2` framebuffer differs from the reference image, and the case reports `Unexpected result in color buffer`. The mismatch can affect the sampled image color, the red value supplied by the storage-buffer range, or both.

**Possible implementation causes:** The implementation may calculate the combined-image-sampler copy span incorrectly when immutable sampler metadata occupies descriptor storage, or may use the wrong binding offset when the storage buffer comes first. It may expose the wrong image view, storage-buffer range, or immutable sampler to the fragment shader. The host's separate buffer ranges, layout binding order, copy count, and reference image make each of those values observable, but the final image comparison does not isolate descriptor storage from framebuffer or copyback behavior. The exact failing case needs source-level investigation.

## Case Pruning

### Requirement-based pruning

- `graphics_uab` requires `VK_EXT_descriptor_indexing`. The implementation checks the matching update-after-bind feature for the standard buffer, image, sampler, and texel-buffer types. If one of those features is absent, the case is `NotSupported`, not a descriptor-copy failure ([support gate](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L1704-L1705), [per-type gates](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L1916-L1941)).
- Inline uniform block cases query `VK_EXT_inline_uniform_block` features and properties when the extension is available. The implementation rejects a block larger than `maxInlineUniformBlockSize` and rejects descriptor counts above the inline-uniform limits ([inline-uniform checks](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L1707-L1723), [size and count checks](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L1762-L1779)).
- The support path checks maximum bound descriptor sets, per-set descriptor counts, per-stage counts, dynamic-buffer counts, inline-uniform block sizes, and inline-uniform block counts. Cases exceeding those device limits are skipped as unsupported ([limit checks](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L1695-L1779), [descriptor counts](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L1855-L1915)).
- Inline uniform block cases are excluded under `CTS_USES_VULKANSC` because the implementation compiles their descriptor class only outside that build mode ([conditional registration](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L3729-L3732)).
- `graphics_uab` excludes dynamic buffer descriptors because update-after-bind layouts cannot contain `VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER_DYNAMIC` or `VK_DESCRIPTOR_TYPE_STORAGE_BUFFER_DYNAMIC` bindings ([layout restriction](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L161-L170), [registration](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L3734-L3748)).

This requirement-based pruning means the selected case is unavailable or illegal for the current device or build. It does not mean the implementation failed the descriptor-copy contract.

### Design-based pruning

- Mixed descriptor cases are registered only for ordinary compute and graphics paths. `mix_2` and `mix_3` require graphics behavior because they use input attachments; `mix_3` also includes inline uniform blocks.
- The ordinary `_0` through `_6` cases deliberately cover distinct set layouts and copy histories without generating every possible permutation of the same operations. The array cases cover representative full, cross-set, and partial array ranges.
- The immutable-sampler loop fixes the sampler object and varies only sampler count and storage-buffer binding order. Those four cases isolate descriptor-copy sizing and binding offsets without adding unrelated sampler-state combinations.
- `graphics_uab` reuses the eligible descriptor-type copy cases instead of repeating dynamic, input-attachment, and mixed cases whose layout or feature requirements would change the update-after-bind contract.

Design-based pruning reduces redundant combinations. An omitted combination is not an unsupported-device result and is not itself a failure.

## Key Takeaways

- The test copies descriptor references, then checks the copied state through the descriptor type's real shader access operation.
- The host model distinguishes directly written elements from destination elements overwritten by a copy. Generated checks cover both categories and ignore unwritten elements that the case does not intend to access.
- Compute reports a scalar result-buffer value. Ordinary graphics and `graphics_uab` report an all-green framebuffer. The immutable-sampler family compares a small reference image with separate sampled-image and storage-buffer contributions.
- `graphics_uab` changes update timing, not shader logic. The descriptor set is bound before writes and copies, so the case exercises the update-after-bind contract and its per-type feature gates.
- Inline uniform block copies use byte offsets and byte counts. Immutable-sampler cases vary descriptor storage layout by moving the storage-buffer binding across the sampler bindings.
- A failure identifies a mismatch in the selected descriptor-copy observation path. The exact suffix and result log are needed before assigning the cause to descriptor state, shader access, pipeline setup, or readback.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Binding-model category attachment | [`createChildren()`](../../../modules/vulkan/binding_model/vktBindingModelTests.cpp#L52-L60) | Attaches `descriptor_copy` under `binding_model`. |
| Descriptor-copy factory | [`createDescriptorCopyTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L3754-L3786) | Creates the four test families and the immutable-sampler leaves. |
| Descriptor-type family registration | [`createTestsForAllDescriptorTypes()`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L3713-L3751) | Applies ordinary, graphics-only, update-after-bind, and Vulkan SC registration gates. |
| Ordinary copy scenarios | [`addDescriptorCopyTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L2605-L2865) | Defines set placement, copy histories, array ranges, and dynamic-offset scenarios. |
| Sampler and sampled-image scenarios | [`addSamplerCopyTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L2867-L2939), [`addSampledImageCopyTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L2941-L2986) | Defines standalone sampler, sampled-image, and combined-image-sampler cases. |
| Mixed descriptor scenarios | [`addMixedDescriptorCopyTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L2988-L3244) | Defines mixed descriptor and inline-uniform cases. |
| Descriptor reference model | [`Descriptor::copyValue()`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L647-L661) | Tracks values copied into destination elements. |
| Vulkan copy construction | [`DescriptorCommands::copyDescriptor()`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L1590-L1615) | Records `VkCopyDescriptorSet` values and handles inline-uniform byte conversion. |
| Generated declarations and checks | [`getShaderDeclarations()` and `getDescriptorVerifications()`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L1617-L1654) | Builds the shader-visible validation program. |
| Support and layout setup | [`DescriptorCommands::checkSupport()`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L1695-L1943), [`DescriptorCommands::run()`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L1974-L2124) | Applies device limits, feature requirements, pool flags, layout flags, and binding flags. |
| Compute and graphics execution | [`DescriptorCommands::run()`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L2146-L2465) | Creates pipelines, binds descriptors, applies updates, submits work, and checks results. |
| Standard shader generation | [`DescriptorCopyTestCase::initPrograms()`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L2537-L2585) | Generates compute, vertex, and fragment GLSL. |
| Immutable-sampler shader generation | [`CopyImmutableSamplerCase::initPrograms()`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L3309-L3377) | Generates the sampler-count-dependent vertex and fragment shaders. |
| Immutable-sampler runtime | [`CopyImmutableSamplerTest::iterate()`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L3379-L3709) | Creates immutable layouts, copies descriptors, renders, and compares the reference image. |
| Mustpass evidence | [`binding-model.txt`](../../../mustpass/main/vk-default/binding-model.txt#L10152-L10440) | Confirms the exact 289-leaf descriptor-copy inventory. |
| Descriptor-copy specification | [Descriptor Set Updates](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L2900-L2951), [`VkCopyDescriptorSet`](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3888-L4047) | Defines operation order, reference-copy behavior, range rules, type matching, immutable-sampler restrictions, and update-after-bind compatibility. |
| Update-after-bind specification | [Descriptor indexing features](../../../../vulkan-docs/src/chapters/features.adoc#L2078-L2121) | Defines the per-type features required by `graphics_uab`. |
| Shader target selection | [`getBaselineSpirvVersion()`](../../../framework/vulkan/vkPrograms.cpp#L1048-L1052) | Shows why the representative shader targets SPIR-V 1.0. |
