## Overview

**Core question:** Do descriptor updates select and expose the intended descriptor state when the layout contains a reserved binding, image writes carry unusable sampler fields, or updates change repeatedly between submissions?

- [`vktBindingDescriptorUpdateTests.cpp`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp) implements the `binding_model.descriptor_update` test family and registers the `empty_descriptor`, `samplerless`, and `random` intermediate nodes.
- The same factory attaches the Vulkan-only `acceleration_structure` intermediate node. This page documents that child as registration only. Its implementation belongs to the separate `DescriptorUpdateAS` assignment.
- `empty_descriptor` checks that a zero-count binding does not displace a later binding. `samplerless` checks descriptor-type-directed use of `VkDescriptorImageInfo`. `random` checks repeated uniform-buffer descriptor changes through graphics and compute submissions.

## Background Knowledge

For the shared concepts of descriptor interfaces, writes, and active state, see [Background Knowledge](../../categories/binding_model.md#background-knowledge) of the `binding_model` page.

- **Descriptor-set binding numbers.** A descriptor-set layout maps each binding number to a descriptor type and count. A binding with `descriptorCount` equal to zero is reserved, and a shader must not access a resource through it. The binding number remains part of the layout, so later binding numbers keep their declared values ([`VkDescriptorSetLayoutBinding`](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L435-L455)).
- **Descriptor write source members.** `vkUpdateDescriptorSets` applies descriptor writes in array order. `VkWriteDescriptorSet` names the destination binding, descriptor count, descriptor type, and source array. The descriptor type determines which members of `pImageInfo`, `pBufferInfo`, or `pTexelBufferView` the implementation accesses ([descriptor set updates](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L2900-L2936), [`VkWriteDescriptorSet`](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3059-L3132)).
- **Samplerless image descriptors.** For `VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE`, `VK_DESCRIPTOR_TYPE_STORAGE_IMAGE`, and `VK_DESCRIPTOR_TYPE_INPUT_ATTACHMENT`, Vulkan uses only the `imageView` and `imageLayout` members of each `VkDescriptorImageInfo`. The `sampler` member is not part of the descriptor data used for those types ([image descriptor member selection](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3129-L3143)).

## Registration Hierarchy

```text
binding_model.descriptor_update
├── empty_descriptor
├── samplerless
├── random
└── acceleration_structure (registration only)
```

`empty_descriptor`, `samplerless`, and `random` are implemented in [`vktBindingDescriptorUpdateTests.cpp`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp). The parent factory attaches `acceleration_structure` only when `CTS_USES_VULKANSC` is not defined. The nested group is implemented and expanded by `vktBindingDescriptorUpdateASTests.cpp`, which remains outside this page's behavior scope ([parent factory](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L1907-L1918), [delegated factory](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L2566-L2662)).

## Parameter Dimensions and Observed Values

The registered leaves contain 63 cases implemented by this page and 60 delegated acceleration-structure leaves in the same test family. The source and mustpass list provide the exact values.

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Implemented intermediate node | `empty_descriptor`, `samplerless`, `random` | Selects the descriptor-update behavior under test. | [`createDescriptorUpdateTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L1907-L1918) |
| Delegated intermediate node | `acceleration_structure` | Adds the Vulkan-only acceleration-structure branch without making this page its implementation page. | [`createDescriptorUpdateASTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L2566-L2662) |
| `samplerless` descriptor type | `sampled_img`, `storage_img`, `input_attachment` | Selects which image descriptor member access and shader read operation the case exercises. | [`descriptorTypes`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L883-L891), [shader generation](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L230-L285) |
| `samplerless` sampler field | `sampler_zero`, `sampler_one`, `sampler_destroyed` | Supplies a null-like, non-object, or destroyed sampler handle while keeping the image view and layout valid. | [`pointerCases`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L893-L897), [`getSamplerHandle()`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L339-L379) |
| `samplerless` descriptor-set index | `0`, `1` | Tests the selected binding at set 0 and after one empty descriptor set. | [`descriptorSet` loop](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L904-L923) |
| `samplerless` image layout form | default, `general_layout` | Selects the normal type-specific shader layout or `VK_IMAGE_LAYOUT_GENERAL`. | [`useGeneralLayout`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L906-L918) |
| `samplerless` pipeline | `graphics`, `compute` | Runs the image read through a fragment shader or compute shader. Input attachments are graphics-only. | [`pipelineCases`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L899-L911) |
| `random` pipeline | `uniform_buffer_graphics`, `uniform_buffer_compute` | Selects additive graphics rendering or compute-image accumulation while keeping the descriptor mutation model the same. | [`createRandomDescriptorUpdateTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L1895-L1902) |
| `random` mutation dimensions | 3 buffers, 5 aligned offsets, 1000 iterations, 0 to 9 draws or dispatches, optional redundant writes | Changes the selected uniform-buffer descriptor and the number of executions used to accumulate the expected result. | [`RandomDescriptorUpdateTestInstance` constants](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L947-L975), [mutation generation](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L1371-L1458) |
| Build availability | `acceleration_structure` absent under `CTS_USES_VULKANSC` | Keeps the nested acceleration-structure registration out of Vulkan SC builds. | [`#ifndef CTS_USES_VULKANSC`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L1911-L1916) |

The `samplerless` loops produce 60 leaves: three descriptor types, three sampler fields, two descriptor-set indices, two layout forms, and two pipeline choices, minus the 12 invalid input-attachment compute combinations. The `random` and `empty_descriptor` factories add two and one leaves respectively. The default mustpass file contains these 63 leaves plus the 60 delegated `acceleration_structure` leaves ([mustpass coverage](../../../mustpass/main/vk-default/binding-model.txt#L10898-L11020)).

## Behavior Parameters

The primary behavioral axis is the implemented intermediate node directly below `binding_model.descriptor_update`. Each value changes the correctness property being checked. The `samplerless` and `random` dimensions configure variants within their intermediate node. `acceleration_structure` is registered here but remains a registration-only child for this page.

### `empty_descriptor`: Reserved binding does not shift later bindings

The case builds uniform-buffer bindings 0 and 2 with a zero-count binding 1 between them. It allocates a descriptor set, creates a uniform buffer, and writes only binding 2. The case returns `Pass` after the update call completes, so it checks API-side layout and destination-binding handling rather than shader output ([`EmptyDescriptorUpdateCase()`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L62-L145)).

### `samplerless`: Image access ignores the sampler field

Each leaf writes one `VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE`, `VK_DESCRIPTOR_TYPE_STORAGE_IMAGE`, or `VK_DESCRIPTOR_TYPE_INPUT_ATTACHMENT` descriptor. The selected sampler field contains `sampler_zero`, `sampler_one`, or `sampler_destroyed`, while the image view and layout identify a cleared green image. A generated fragment or compute shader reads the image and writes its value to an output image. The host requires every output pixel to equal the green descriptor color ([descriptor matrix](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L883-L930), [descriptor write and execution](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L573-L581), [pixel check](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L854-L880)).

### `random`: Repeated writes select the current uniform-buffer state

The graphics and compute leaves initialize three uniform buffers with distinct values at five 256-byte-spaced offsets. A deterministic generator creates 1000 mutations. A mutation may skip the descriptor update, issue redundant writes, choose a new buffer or offset, and execute zero to nine draws or dispatches. The host models the expected color from the last descriptor write, applies the writes before the submission, waits for completion, and compares the copied image with that model ([mutation model](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L1353-L1458), [graphics updates](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L1461-L1519), [compute updates](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L1687-L1848)).

## Shader Analysis

The generated shaders are small observation programs. `samplerless` reads one descriptor and copies its image value to an output. `random` reads two uniform-buffer values and accumulates them through a graphics blend or a compute image path. Neither shader contains the descriptor-update decision logic. The host-side descriptor writes, descriptor contents, resource layout, and result model control the tested behavior. A walkthrough would repeat fixed read-and-output expressions without clarifying those host-side decisions, so this page does not use `shader-analyzer` or `shader-disassembler`.

## Runtime Execution and Result Checking

### `empty_descriptor`

- The host creates a descriptor-set layout with binding 0, a zero-count binding 1, and binding 2.
- The host allocates one descriptor set, creates a uniform buffer, and calls `updateDescriptorSets` with `dstBinding = 2`.
- The case returns `Pass`. It does not submit a command buffer or read a device result.

### `samplerless`

- The host creates the source image and output framebuffer with `VK_FORMAT_R8G8B8A8_UNORM`. The source image is cleared to `kDescriptorColor`, `(0, 1, 0, 1)`.
- The host creates empty descriptor-set layouts before the selected set when `descriptorSet` is 1, then adds binding 0 with the selected image descriptor type. The compute path also adds a storage-image output binding.
- The host writes the selected `VkDescriptorImageInfo`, using the selected sampler field, image view, and image layout. The graphics path records a full-screen draw. The compute path dispatches `64 x 64 x 1` invocations.
- The host copies the output image to a host-visible buffer. It scans the result and fails with `Pixel mismatch` if any pixel differs from the green descriptor color.
- The support check requires the selected format to support transfer-destination, color-attachment, and descriptor-type-specific features. Unsupported formats are reported as not supported before execution ([format support](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L288-L325)).

### `random`

- The host creates a uniform-buffer descriptor binding and, for compute, two storage-image bindings. It fills three host-visible uniform buffers with distinguishable signed and unsigned values at five aligned offsets.
- The host creates a `64 x 64` `VK_FORMAT_R16G16B16A16_SFLOAT` output image and a host-visible result buffer. Graphics uses a full-screen quad and additive color blending. Compute uses `color_out` and `color_temp` storage images.
- For each generated mutation, the host applies every descriptor write when `update` is true, binds the descriptor set, and records the selected number of draws or dispatches. Each sequence ends with `submitCommandsAndWait`, so the next mutation starts after the previous sequence completes.
- The host copies the final output image to the result buffer and invalidates the allocation. It compares every RGB component with `expColor` using a tolerance of `0.5`; alpha is not part of the comparison ([final scan](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L1851-L1881)).

## Failure Meaning

A failure identifies a mismatch between the selected descriptor-update contract and the result observed by the case. It does not, by itself, identify a driver, hardware, compiler, or host bug location.

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `empty_descriptor` | Reserved zero-count binding handling or destination-binding lookup failure. |
| `samplerless` | Incorrect samplerless `VkDescriptorImageInfo` member selection, or an image access/output observation failure. |
| `random` | Incorrect descriptor-write ordering or current descriptor state, incorrect uniform-buffer address/range selection, or an accumulation/readback failure. |

### Cause Analysis

#### Reserved zero-count binding handling or destination-binding lookup failure

**Possible failure symptoms:** `empty_descriptor.uniform_buffer` does not complete successfully, or the update to binding 2 triggers an error instead of returning `Pass`. The test has no shader result that could distinguish one internal failure from another.

**Possible implementation causes:** The layout or update path may treat the zero-count binding as absent and renumber binding 2, or it may mishandle a valid write to a later binding. Vulkan preserves the declared binding number and reserves a zero-count entry, so the implementation must keep binding 2 as the write destination ([binding rules](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L441-L455)). The source-level result cannot determine whether a failure occurred during layout creation, descriptor allocation, or update processing, so that distinction needs source-level investigation.

#### Incorrect samplerless `VkDescriptorImageInfo` member selection, or image access/output observation failure

**Possible failure symptoms:** One or more `samplerless` output pixels differ from `(0, 1, 0, 1)`, and the test logs the rendered image with `Pixel mismatch`. The symptom can arise for any descriptor type, sampler field, set index, layout form, or pipeline variant.

**Possible implementation causes:** For the three descriptor types under test, the implementation may incorrectly inspect the `sampler` member even though Vulkan specifies that only `imageView` and `imageLayout` are accessed. It may instead select the wrong image view or layout, expose the descriptor at the wrong set, or fail to make the image read visible to the output attachment or storage image. The source confirms the image is cleared and the descriptor is written before execution, while the specification defines the member-selection rule ([descriptor write](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L573-L581), [member selection](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3129-L3143)). A pixel mismatch alone cannot separate descriptor lookup from image-layout, shader, synchronization, or copyback behavior, so the failing variant needs source-level investigation.

#### Incorrect descriptor-write ordering or current descriptor state, incorrect uniform-buffer address/range selection, or an accumulation/readback failure

**Possible failure symptoms:** One or more RGB components in either `uniform_buffer_graphics` or `uniform_buffer_compute` differ from the host-model `expColor` by more than `0.5`, and the test reports `Pixel mismatch`. The failure may appear after a skipped update, a redundant write sequence, a buffer change, an offset change, or a different draw or dispatch count.

**Possible implementation causes:** `vkUpdateDescriptorSets` may fail to apply writes in the order supplied, retain the wrong descriptor after a completed update, or use the wrong buffer and range for the current binding. Vulkan defines the write order and the buffer members used for uniform-buffer descriptors ([update order](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L2905-L2930), [buffer descriptor members](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3120-L3148)). The observed mismatch can also come from the graphics blend path, compute image accumulation, transfer synchronization, image-to-buffer copy, or host result interpretation. The case's source-level checks establish the expected mutation model and final comparison, but they do not isolate those mechanisms, so the failing case requires source-level investigation.

## Case Pruning

### Requirement-based pruning

- `samplerless` checks the optimal-tiling features for `VK_FORMAT_R8G8B8A8_UNORM`. A device that lacks transfer-destination, color-attachment, sampled-image, storage-image, or input-attachment support for the selected case receives `NotSupported` ([support check](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L311-L325)).
- The input-attachment form is fragment-shader-only. The registration loop removes its compute variant, matching the descriptor-set stage restriction for input attachments ([matrix pruning](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L904-L911), [stage rule](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L463-L469)).
- The acceleration-structure child is compiled and registered only outside `CTS_USES_VULKANSC`. Its feature and extension checks belong to the separate `DescriptorUpdateAS` page.

### Design-based pruning

- `samplerless` does not create input-attachment compute cases because that combination is outside the intended legal pipeline shape.
- `random` retries generated mutations when the modeled RGB value would leave `[-2048, 2048]`. The output format is `R16G16B16A16_SFLOAT`, and the source keeps the accumulated integer values in the exact range needed for the test's expected-color model ([range constraint](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L1435-L1453)).
- The `samplerless` case matrix varies descriptor type, sampler field, descriptor set, layout, and pipeline because each dimension changes descriptor interpretation or observation. It does not expand unrelated descriptor types or sampler-bearing descriptor cases.

## Key Takeaways

- A zero-count binding reserves its binding number. `empty_descriptor` writes binding 2 after the reserved binding 1 to check that the layout keeps that numbering intact.
- The `samplerless` matrix makes the sampler field unusable on purpose. The expected green result depends on the implementation using the image view and layout only for the selected descriptor types.
- `random` uses completed submissions and a host-side mutation model. Each result checks the descriptor state that the last applied write should expose to the following graphics or compute work.
- `acceleration_structure` is visible in this registration tree, but its ray-query and ray-tracing behavior belongs to the separate `DescriptorUpdateAS` assignment.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Binding-model category attachment | [`createChildren()`](../../../modules/vulkan/binding_model/vktBindingModelTests.cpp#L52-L59) | Attaches `descriptor_update` under `binding_model`. |
| Empty-binding implementation | [`EmptyDescriptorUpdateCase()`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L62-L145) | Creates the zero-count binding and writes binding 2. |
| Samplerless parameter and shader setup | [`SamplerlessDescriptorWriteTestCase`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L148-L330) | Defines descriptor types, sampler fields, generated shaders, and format support. |
| Samplerless case registration | [`createSamplerlessWriteTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L883-L930) | Generates the exact 60-leaf matrix and removes input-attachment compute cases. |
| Samplerless execution | [`SamplerlessDescriptorWriteTestInstance::queuePass()`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L460-L881) | Creates resources, applies the descriptor write, submits work, and checks green pixels. |
| Random program setup | [`RandomDescriptorUpdateTestCase`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L932-L1043) | Defines graphics and compute descriptor observers. |
| Random mutation and expected-color generation | [`RandomDescriptorUpdateTestInstance::queuePass()`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L1045-L1458) | Creates buffers and models 1000 descriptor mutations. |
| Random graphics and compute execution | [`queuePass()` branches](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L1461-L1848) | Applies writes between submissions and accumulates output. |
| Random result validation | [`resultPixels` scan](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L1851-L1881) | Compares copied pixels with the host-model color. |
| Page-scope registration | [`createDescriptorUpdateTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L1907-L1918) | Registers the three implemented intermediate nodes and attaches the delegated child. |
| Delegated acceleration-structure registration | [`createDescriptorUpdateASTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L2566-L2662) | Shows the separate child implementation and its `ray_query` / `ray_tracing` matrix. |
| Mustpass evidence | [`binding-model.txt`](../../../mustpass/main/vk-default/binding-model.txt#L10898-L11020) | Confirms exact registered leaves for this page and the delegated child. |
| Normative descriptor-update behavior | [Descriptor Set Updates](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L2900-L3148) | Defines write order, destination binding meaning, and descriptor-type-directed source access. |
