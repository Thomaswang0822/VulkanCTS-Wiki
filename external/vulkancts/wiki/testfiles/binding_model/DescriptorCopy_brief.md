# Understanding Brief: `binding_model.descriptor_copy`

## One-Sentence Test Purpose

This test checks whether Vulkan descriptor-set copy operations preserve descriptor contents and array ranges across compute, graphics, update-after-bind graphics, descriptor types, and immutable-sampler layouts.

## Background Knowledge

### Descriptor copies are reference copies

A descriptor contains the resource reference and the metadata needed to interpret it. `vkUpdateDescriptorSets` applies all `VkWriteDescriptorSet` operations before the `VkCopyDescriptorSet` operations, and each copy transfers descriptors from a source binding and array range to a destination binding and array range. The specification describes the copy as copying the reference itself, not using the referenced resource ([descriptor set updates](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L2900-L2951), [`VkCopyDescriptorSet`](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3888-L3971)).

Why it matters here:

- The source writes selected descriptor elements, then the copy makes those elements observable through a different binding or set.
- The generated host model marks copied destination elements and derives the value that the shader must observe.
- Array copies can start at nonzero source and destination elements, cross descriptor sets, or fill only part of a destination array.

### Descriptor types and immutable samplers

The descriptor type determines which resource representation a shader uses. Buffer descriptors expose buffer data, texel-buffer descriptors expose buffer views, image descriptors expose image views and layouts, and inline uniform blocks expose bytes in a block. Inline uniform block copy offsets and counts are byte quantities, while ordinary descriptor arrays use descriptor elements ([descriptor binding counts](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L435-L455), [`VkCopyDescriptorSet` inline-uniform rules](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3897-L3925)).

An immutable sampler belongs to the descriptor-set layout and cannot be changed by a descriptor update. For a combined image sampler, a write can still replace the image view while the immutable sampler remains layout state ([immutable samplers](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L470-L480)). The miscellaneous cases therefore copy combined-image-sampler descriptors while placing a storage-buffer binding before or after them. This makes an implementation's descriptor-size and binding-offset calculations observable.

### Update-after-bind layouts

A binding created with `VK_DESCRIPTOR_BINDING_UPDATE_AFTER_BIND_BIT` permits the supported descriptor types to be updated after the descriptor set is bound. The layout must use `VK_DESCRIPTOR_SET_LAYOUT_CREATE_UPDATE_AFTER_BIND_POOL_BIT`, and the descriptor pool must use `VK_DESCRIPTOR_POOL_CREATE_UPDATE_AFTER_BIND_BIT`. The feature is type-specific, such as `descriptorBindingStorageBufferUpdateAfterBind` for storage buffers and `descriptorBindingSampledImageUpdateAfterBind` for sampled-image descriptors ([layout flag](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L363-L376), [update-after-bind features](../../../../vulkan-docs/src/chapters/features.adoc#L2078-L2121)).

Why it matters here:

- `graphics_uab` uses the same copy scenarios as the ordinary graphics path for the eligible descriptor types.
- The test binds the pipeline and descriptor sets before calling `updateDescriptorSets`, so the copied and written descriptors are observed after binding.
- Dynamic buffer descriptors, input attachments, and mixed descriptor scenarios are intentionally omitted from this path by the registration code.

## One Concrete Example

Consider the first registered case, `dEQP-VK.binding_model.descriptor_copy.compute.uniform_buffer_0`.

The host creates two `VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER` bindings in set 0. It writes both bindings, then records a copy from binding 0 to binding 1. The host reference model replaces the destination value with the source value ([case construction](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L2609-L2625), [copy model](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L647-L661)).

The generated compute shader reads both uniform-buffer bindings. It keeps `result` equal to 1 only when both reads equal the source reference value, then stores that result in a third storage-buffer binding. The shader observes the copied state; the host performs the copy through `vkUpdateDescriptorSets`, dispatches one workgroup, and reads the result buffer ([shader generation](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L2537-L2553), [compute execution and result](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L2384-L2441)).

## End-to-End Test Flow

```text
1. regular compute and graphics paths
[host] choose a registered descriptor type and copy scenario
[host] create descriptor resources, descriptor-set layouts, descriptor pools, and descriptor sets
[host] write the source elements that are marked as initialized
[host] record VkCopyDescriptorSet entries for the selected source and destination ranges
[host] generate the declarations and verification expressions for the selected descriptors
[host] submit a compute dispatch or graphics draw
[device] read each written or copied descriptor through the generated verification shader
[device] write a compute result value or a graphics result color
[host] read the compute result buffer or copied graphics image
[host] decide pass or fail from the observed result

2. graphics update-after-bind path
[host] choose an eligible graphics descriptor type and copy scenario
[host] create update-after-bind pool and layout flags and binding flags
[host] bind the graphics pipeline and descriptor sets
[host] apply writes and copies after the descriptor sets are bound
[device] execute the fragment verification shader using the post-bind descriptor state
[host] require a green result image

3. immutable-sampler path
[host] choose one or four immutable combined-image-sampler bindings and buffer-first or sampler-first ordering
[host] create two descriptor sets with the same layout and write all image views and the first storage-buffer range into set 0
[host] write the second storage-buffer range into set 1
[host] copy all immutable-sampler descriptors from set 0 to set 1
[host] draw the first half of the vertices with set 0 and the second half with set 1
[device] sample the selected image and replace the red channel with the bound storage-buffer value
[host] compare each framebuffer quadrant with its expected image color and red value
```

The ordinary descriptor-copy path submits one verification operation. Dynamic descriptors use the selected dynamic offsets, and image initialization includes the transfer-to-shader-read barrier required by the descriptor class. The update-after-bind path changes only the point at which descriptor writes and copies are applied relative to binding. The immutable-sampler path has its own graphics setup and reference image.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The primary descriptor-copy implementation builds inline GLSL programs in `DescriptorCopyTestCase::initPrograms()`:

- The compute program declares every descriptor and writes `1` to the result storage buffer unless a generated descriptor check changes `result` to `0`.
- The ordinary graphics and `graphics_uab` programs use a fixed vertex shader to make a full-screen quad and a fragment shader that writes green when all descriptor checks pass and magenta otherwise.
- Each descriptor class contributes its shader declaration and its verification expression. For example, storage buffers use `.data`, texel buffers use `texelFetch` or `imageLoad`, sampled images use `texture`, storage images use `imageLoad`, input attachments use `subpassLoad`, samplers sample through an associated sampled image, and inline uniform blocks compare their generated integer fields ([shader declarations and checks](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L1617-L1654), [descriptor shader methods](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L886-L1533)).
- The compiler default is the CTS baseline SPIR-V 1.0 because the source collection does not supply explicit shader build options ([baseline version](../../../framework/vulkan/vkPrograms.cpp#L1048-L1052)).

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Buffer descriptor backing buffers | yes | yes | read by the verification shader | no | Stores the per-descriptor reference values. |
| Texel-buffer views | yes | yes | read by the verification shader | no | Tests descriptor copies whose payload is a `VkBufferView`. |
| Descriptor images and views | yes | yes | cleared, then read by the shader | indirectly through the result | Give image descriptor copies a known value. |
| Samplers and sampled-image associations | yes | yes | used for sampling | indirectly through the result | Distinguish sampler, sampled-image, and combined-image-sampler copies. |
| Input-attachment images | yes | yes through a graphics framebuffer | loaded by the fragment shader | indirectly through the result | Exercises copied input-attachment references and attachment indices. |
| Inline uniform block data | yes | yes | read by the fragment or compute shader | no | Tests byte-offset and byte-count copy semantics. |
| Compute result storage buffer | yes | yes | written by the compute shader | yes | Stores `1` for success or `0` for a failed descriptor check. |
| Graphics result image and readback buffer | yes | color attachment, then transfer source and destination | written by the fragment shader and copied | yes | Carries the green or magenta verification result to host validation. |
| Immutable-sampler test images and storage buffer | yes | yes | sampled and read by the fragment shader | framebuffer copied to host | Makes sampler layout position and descriptor-buffer layout effects visible. |

## What Is Checked

| Path | Device-side observation | Host-side pass condition |
|------|-------------------------|--------------------------|
| `compute` | The verification compute shader checks every written or copied descriptor and stores the result in the last set 0 storage buffer. | The first result-buffer value is `1`; otherwise the case fails with `Data validation failed`. |
| `graphics` | The verification fragment shader checks every written or copied descriptor and writes green for success or magenta for failure. | Every pixel in the `64 x 64` result image is `(0, 1, 0, 1)`; otherwise the case fails with `Result image validation failed`. |
| `graphics_uab` | The same graphics shader observes descriptors after the descriptor set was bound and after update-after-bind writes and copies. | Every pixel in the result image is green. |
| `misc` | The fragment shader samples the immutable-sampler images, replaces the red channel with the selected storage-buffer value, and the host builds a quadrant reference. | The `2 x 2` framebuffer matches the reference within `0.005` per component. |

The generated shader checks descriptors whose host model marks them as initially written or copied into. An unwritten destination with no copy is not read by the generated check. A copied destination is checked against the copied source reference, so the test validates shader-visible state rather than just successful API return values ([reference tracking](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L618-L687), [result checking](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L2430-L2465)).

## Behavior Parameter Identification

> **Behavior parameter:** top-level test family under `binding_model.descriptor_copy`
>
> **Candidate values:** `compute`, `graphics`, `graphics_uab`, `misc`

The four values are the primary behavioral axis because each selects a distinct execution or descriptor-layout contract. Descriptor type, copy-shape suffix, array range, and immutable-sampler dimensions configure behavior inside the first three families; `misc` uses a separate immutable-sampler implementation.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `compute` | Descriptor copy or descriptor-type handling failure visible through the verification compute shader, dynamic-offset or inline-uniform byte-range handling failure, or compute result-buffer failure. |
| `graphics` | Descriptor copy or descriptor-type handling failure visible through the verification fragment shader, graphics resource or input-attachment setup failure, or result-image failure. |
| `graphics_uab` | Incorrect update-after-bind layout, feature, post-bind update, or descriptor-copy behavior, or graphics result-image failure. |
| `misc` | Immutable-sampler copy sizing or binding-order failure, incorrect sampled image or storage-buffer descriptor state, or framebuffer/reference construction failure. |

## Important Variations and Special Cases

- The standard descriptor-type matrix covers `uniform_buffer`, `storage_buffer`, `combined_image_sampler`, `storage_image`, `uniform_texel_buffer`, `storage_texel_buffer`, and, outside `CTS_USES_VULKANSC`, `inline_uniform_block`. The ordinary compute and graphics families add `uniform_buffer_dynamic` and `storage_buffer_dynamic`; graphics also adds `input_attachment` and graphics-only mixed descriptor cases ([family registration](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L3713-L3751)).
- The `_0` through `_6` cases vary set placement and copy history: same-set copy, cross-set copy, an unwritten destination, multiple sets and copies, repeated copies, copies back and forth, and non-consecutive sets. `array0` copies a three-element array, `array1` copies two elements from a two-element source into a three-element destination, and `array2` fills part of an eight-element destination after a partial write ([copy-case generation](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L2605-L2865)).
- `sampler_0`, `sampler_array0`, and `sampler_array1` exercise standalone sampler descriptors associated with sampled images. `sampled_image_0` and `sampled_image_array0` exercise sampled-image descriptors with a separate sampler. The combined-image-sampler cases exercise image and sampler state in one descriptor.
- `mix_0` and `mix_1` are registered for compute and graphics. `mix_2` and `mix_3` are graphics-only, with input attachments in `mix_2` and inline uniform blocks in `mix_3`. `mix_array0` and `mix_array1` exercise mixed descriptor arrays. These cases are excluded from `graphics_uab` because the source calls mixed registration only when `useUpdateAfterBind` is false.
- Inline uniform block copies convert the source and destination array indices and descriptor count from integer elements in the host reference model to byte offsets and byte counts in `VkCopyDescriptorSet`. The specification requires the relevant values to be multiples of four ([inline copy conversion](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L1590-L1615), [inline copy validity](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3972-L3986)).
- Dynamic uniform and storage buffer cases are not generated for `graphics_uab`. The specification disallows dynamic buffer descriptor types in an update-after-bind layout, and the source keeps those cases on the ordinary compute and graphics paths ([layout restriction](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L161-L170), [registration gate](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L3734-L3748)).
- The immutable-sampler loop produces exactly `copy_immutable_sampler_1_images`, `copy_immutable_sampler_1_images_buffer_first`, `copy_immutable_sampler_4_images`, and `copy_immutable_sampler_4_images_buffer_first`. It copies all sampler descriptors in one operation and varies whether the storage-buffer binding precedes or follows them ([registration](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L3246-L3270), [case construction](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L3380-L3569)).

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Binding-model attachment | [`createChildren()`](../../../modules/vulkan/binding_model/vktBindingModelTests.cpp#L52-L60) | Attaches `descriptor_copy` under `binding_model`. |
| Descriptor-copy factory | [`createDescriptorCopyTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L3754-L3786) | Creates the four top-level test families and the immutable-sampler leaves. |
| Descriptor-type family registration | [`createTestsForAllDescriptorTypes()`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L3713-L3751) | Selects descriptor classes and gates update-after-bind, dynamic, graphics-only, and mixed cases. |
| Copy-case construction | [`addDescriptorCopyTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L2605-L2865) | Defines the ordinary copy and array-range scenarios. |
| Descriptor-type-specific registration | [`addSamplerCopyTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L2867-L2939), [`addSampledImageCopyTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L2941-L2986), [`addMixedDescriptorCopyTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L2988-L3244) | Defines sampler, sampled-image, mixed, and inline-uniform special cases. |
| Host copy model | [`Descriptor::copyValue()`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L647-L661) and [`DescriptorCommands::copyDescriptor()`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L1590-L1615) | Tracks copied reference values and converts inline-uniform indices to bytes. |
| Generated shader declarations and checks | [`getShaderDeclarations()`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L1617-L1654) and descriptor `getShaderVerifyCode()` methods | Builds the shader-visible validation logic. |
| Support and descriptor-set setup | [`DescriptorCommands::checkSupport()`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L1695-L1943) and [`DescriptorCommands::run()`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L1974-L2124) | Applies limits, feature gates, pool flags, layout flags, and descriptor binding flags. |
| Compute and graphics execution | [`DescriptorCommands::run()`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L2146-L2465) | Creates pipelines, applies post-bind updates where requested, submits work, and checks results. |
| Immutable-sampler shader generation | [`CopyImmutableSamplerCase::initPrograms()`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L3309-L3377) | Generates the quadrant selector and sampler/storage-buffer observer shaders. |
| Immutable-sampler runtime | [`CopyImmutableSamplerTest::iterate()`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L3379-L3709) | Creates immutable layouts, copies sampler descriptors, renders both sets, and compares the reference image. |
| Mustpass evidence | [`binding-model.txt`](../../../mustpass/main/vk-default/binding-model.txt#L10152-L10440) | Confirms 289 registered descriptor-copy leaves: 99 compute, 111 graphics, 75 graphics_uab, and 4 misc. |
| Descriptor-copy semantics | [Descriptor Set Updates](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L2900-L2951) and [`VkCopyDescriptorSet`](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3888-L4047) | Defines operation order, reference-copy behavior, ranges, type matching, overlap rules, and update-after-bind compatibility. |
| Update-after-bind features | [Descriptor indexing features](../../../../vulkan-docs/src/chapters/features.adoc#L2078-L2121) | Defines the per-descriptor-type feature gates used by `graphics_uab`. |

## Questions / Risk Points for User Audit

- Is the distinction between descriptor contents, descriptor references, and the resources eventually read by the shader clear? Resolved by the descriptor-copy specification text and the host reference model.
- Does the page identify the top-level family as the behavior axis while retaining descriptor type and copy-shape dimensions as matrix dimensions? Yes, because the four factories select different execution and layout contracts.
- Does the `graphics_uab` explanation distinguish post-bind descriptor updates from ordinary graphics updates? Yes, the runtime sequence and feature requirements are called out separately.
- Does the immutable-sampler explanation cover both sampler count and buffer-first ordering? Yes, all four mustpass leaves and the buffer-binding calculation are identified.
- Are generated shader checks described without treating the shader as the component that performs the copy? Yes, the shader is explicitly described as an observation program.
- No unresolved semantic risk remains after checking implementation, registration, mustpass, shader generation, compiler output, and the descriptor-set and feature chapters.

## Conversion Notes for Final Wiki Rewrite

- Use `compute`, `graphics`, `graphics_uab`, and `misc` as the primary behavior parameter values.
- Copy the `### Failure Cause Mapping` table unchanged into the final page.
- Distill the descriptor-copy, descriptor-type, immutable-sampler, and update-after-bind explanations into compact Background Knowledge bullets.
- Include one `### Representative Shader Walkthrough 1` for `dEQP-VK.binding_model.descriptor_copy.compute.uniform_buffer_0`. It is the smallest case that shows the directly written source, copied destination, and generated host-readable result. Explain `graphics_uab` timing in the behavior and runtime sections because update timing does not change the generated shader.
- Keep the full compute, graphics, graphics_uab, and misc execution differences in Runtime Execution and Result Checking.
- Preserve exact matrix suffixes and mustpass counts while moving source-navigation details into the appendix.
- Write fresh Cause Analysis subsections for each mapped family cause and retain the exact bold lead-in labels required by the Level-3 template.
