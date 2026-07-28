# Understanding Brief: `binding_model.descriptor_update`

## One-Sentence Test Purpose

This test checks whether descriptor-set writes handle reserved empty bindings, ignore sampler fields for samplerless image descriptor types, and expose the latest randomly selected uniform-buffer descriptor through graphics and compute execution.

## Background Knowledge

### Descriptor-set layout bindings and updates

A descriptor-set layout assigns a descriptor type and count to each binding number. A binding whose `descriptorCount` is zero is reserved, and shaders must not access a resource through it. The binding number still exists as a number in the layout, so an implementation must not shift later bindings around it. The Vulkan specification states this rule in [`VkDescriptorSetLayoutBinding`](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L435-L455).

`vkUpdateDescriptorSets` applies writes in array order before it applies copies. A `VkWriteDescriptorSet` names the destination binding, array element, descriptor count, and descriptor type. The descriptor type decides which source structure members the implementation reads ([descriptor update ordering](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L2900-L2930), [`VkWriteDescriptorSet`](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3059-L3132)).

Why it matters here:

- `empty_descriptor` places a zero-count binding between bindings 0 and 2, then writes binding 2.
- `random` can issue several writes before one draw or dispatch sequence. The final write selects the uniform buffer and byte range used by the next submission.

### Samplerless image descriptors

`VkDescriptorImageInfo` contains `sampler`, `imageView`, and `imageLayout`, but not every image descriptor type consumes every member. For `VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE`, `VK_DESCRIPTOR_TYPE_STORAGE_IMAGE`, and `VK_DESCRIPTOR_TYPE_INPUT_ATTACHMENT`, the specification says that the implementation accesses only `imageView` and `imageLayout`; it does not access `sampler` ([member-selection rules](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3129-L3143)).

Why it matters here:

- The `samplerless` cases place zero, non-object, or destroyed-object bit patterns in `sampler`.
- Correct behavior depends on descriptor-type-directed member access. The implementation must not inspect the sampler field just because it occupies the same structure.

## One Concrete Example

Consider the registered samplerless case:

```text
dEQP-VK.binding_model.descriptor_update.samplerless.storage_img_sampler_destroyed_graphics
```

The host creates an `R8G8B8A8_UNORM` storage image, clears it to green, and prepares a `VkDescriptorImageInfo`. Its `imageView` names the live image view and its `imageLayout` is `VK_IMAGE_LAYOUT_GENERAL`. Its `sampler` field holds the former handle of a sampler that has already been destroyed ([sampler-handle construction](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L339-L379), [descriptor write](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L545-L581)).

The descriptor type is `VK_DESCRIPTOR_TYPE_STORAGE_IMAGE`, so the implementation must use the view and layout without reading or validating the sampler field. The fragment shader performs `imageLoad`, writes the result to the color attachment, and the host checks that every pixel is green. A sampler dereference in this path is an implementation error even though the structure contains a sampler-shaped value.

## End-to-End Test Flow

```text
1. empty_descriptor
[host] create a descriptor-set layout with uniform-buffer bindings 0 and 2 and a zero-count binding 1
[host] allocate the descriptor set and a uniform buffer
[host] write one uniform-buffer descriptor to binding 2
[host] report Pass if the API path completes normally

2. samplerless
[host] choose descriptor type, sampler bit pattern, set index, image-layout variant, and pipeline type
[host] create and clear the source image to green
[host] create empty set layouts before the selected set when set index is 1
[host] write the sampled-image, storage-image, or input-attachment descriptor with the selected sampler bit pattern
[host] record and submit one full-screen draw or one 64 x 64 compute dispatch
[device] read the image descriptor and copy its green value to the output image
[host] copy the output image to a host-visible buffer and require every pixel to equal green

3. random
[host] initialize three uniform buffers with distinguishable data at five aligned offsets
[host] generate 1000 deterministic mutations, including optional descriptor updates, zero to nine draws or dispatches, and occasional redundant writes
[host] model the current descriptor from the last write and accumulate the expected RGB result
[host] before each submission, apply the mutation's descriptor writes, then record and submit its draw or dispatch sequence
[device] read two vec4 values through the current uniform-buffer descriptor and accumulate them in the output
[host] copy the 64 x 64 output image to a host-visible buffer
[host] require each RGB component to be within 0.5 of the modeled final color
```

Each random mutation completes before the next descriptor update because the source uses `submitCommandsAndWait`. This isolates descriptor-state selection from update-while-pending behavior ([graphics mutation loop](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L1458-L1519), [compute mutation loop](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L1684-L1848)).

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The file builds small inline GLSL programs:

- `samplerless` generates a fragment shader and, where legal, a compute shader that reads one sampled image, storage image, or input attachment and writes the value to the output ([program generation](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L222-L286)).
- `random` generates graphics and compute programs that read two `vec4` members from one uniform-buffer descriptor. Graphics uses fixed-function additive blending; compute reads a temporary image and performs the same addition in shader code ([program generation](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L984-L1031)).
- `empty_descriptor` has no shader, pipeline, command buffer, or device-side result artifact.

The shaders are observation tools. They do not implement descriptor updates and their control flow is not a behavior parameter.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `empty_descriptor` uniform buffer | yes | written into binding 2, but no command uses it | no | no | Makes the destination write concrete while leaving binding 1 reserved. |
| `samplerless` main image and view | yes | yes, as binding 0 in set 0 or 1 | read by fragment or compute shader | indirectly through output | Supplies the known green descriptor value while the sampler field is unusable. |
| `samplerless` output image | yes | color attachment or storage image | written by graphics or compute | yes, through a transfer buffer | Carries the shader-observed descriptor value to host validation. |
| `random` uniform buffers | yes, three buffers with five populated offsets each | one selected buffer/range at binding 0 | read by fragment or compute shader | no | Makes buffer and offset changes visible as different accumulated colors. |
| `random` framebuffer image | yes | color attachment or storage image | accumulates output | yes, through a transfer buffer | Holds the result compared with the host model. |
| `random` temporary image | yes, compute path only | storage image binding 2 | read and refreshed between dispatches | no | Emulates graphics additive blending in the compute path. |
| Host-visible result buffers | yes | transfer destination | written by image-to-buffer copy | yes | Provide the final pixel data for CTS pass/fail checks. |

## What Is Checked

| Implemented intermediate node | Check | Pass condition |
|-------------------------------|-------|----------------|
| `empty_descriptor` | API execution only | Layout creation, allocation, buffer setup, and the write to binding 2 complete; the case returns `Pass`. |
| `samplerless` | Host pixel scan after shader access | Every output pixel equals `(0, 1, 0, 1)` exactly ([result scan](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L854-L880)). |
| `random` | Host pixel scan after 1000 modeled mutations | Every output pixel's RGB components differ from the modeled final color by at most `0.5` ([result scan](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L1851-L1881)). |

The mustpass list contains 63 leaves implemented by this page: one `empty_descriptor` leaf, 60 `samplerless` leaves, and two `random` leaves. It also contains 60 `acceleration_structure` leaves delegated to `vktBindingDescriptorUpdateASTests.cpp` ([mustpass range](../../../mustpass/main/vk-default/binding-model.txt#L10898-L11020)).

## Behavior Parameter Identification

> **Behavior parameter:** implemented intermediate node under `binding_model.descriptor_update`
>
> **Candidate values:** `empty_descriptor`, `samplerless`, `random`

`acceleration_structure` is a fourth registered intermediate node, but this file only attaches it. Its implementation and behavior analysis belong to the separate `DescriptorUpdateAS` assignment.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `empty_descriptor` | Reserved zero-count binding handling or destination-binding lookup failure. |
| `samplerless` | Incorrect samplerless `VkDescriptorImageInfo` member selection, or an image access/output observation failure. |
| `random` | Incorrect descriptor-write ordering or current descriptor state, incorrect uniform-buffer address/range selection, or an accumulation/readback failure. |

## Important Variations and Special Cases

- `samplerless` crosses three descriptor types (`sampled_img`, `storage_img`, `input_attachment`), three sampler bit patterns (`sampler_zero`, `sampler_one`, `sampler_destroyed`), descriptor sets 0 and 1, base and `general_layout` forms, and graphics or compute pipelines. Input attachments omit compute because Vulkan input attachments are fragment-shader resources ([registration loops](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L883-L929), [stage restriction](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L463-L469)).
- `samplerless` requires the chosen `R8G8B8A8_UNORM` format to support transfer destination, color attachment, and the descriptor-type-specific image feature. Unsupported format combinations produce `NotSupported` rather than a failure ([support check](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L288-L325)).
- `random` uses a fixed random seed, three buffers, five 256-byte-spaced offsets, and 1000 mutations. A mutation may retain the previous descriptor and may issue several redundant writes; source-side expected-value calculation uses the final write ([constants and seed](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L971-L975), [mutation generation](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L1371-L1458)).
- `acceleration_structure` is registered only outside `CTS_USES_VULKANSC`. It expands into ray-query and ray-tracing behavior implemented in another source file, so this brief records only its registration boundary ([parent registration](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L1907-L1918), [delegated registration](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L2566-L2662)).

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| `binding_model` attachment | [`createChildren()`](../../../modules/vulkan/binding_model/vktBindingModelTests.cpp#L52-L59) | Registers `descriptor_update` under the test category. |
| Reserved-binding case | [`EmptyDescriptorUpdateCase()`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L62-L145) | Builds bindings 0, 1, and 2 and writes only binding 2. |
| Samplerless programs and support | [`SamplerlessDescriptorWriteTestCase`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L148-L330) | Defines parameters, generated observer shaders, and format gates. |
| Samplerless runtime and validation | [`queuePass()`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L460-L881) | Creates images and descriptor sets, submits work, and checks green pixels. |
| Samplerless matrix | [`createSamplerlessWriteTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L883-L930) | Generates the 60 registered leaves. |
| Random programs and constants | [`RandomDescriptorUpdateTestCase`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L932-L1043) | Defines graphics/compute probes, fixed dimensions, and deterministic seed. |
| Random runtime | [`RandomDescriptorUpdateTestInstance::queuePass()`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L1045-L1882) | Generates mutations, updates descriptors between submissions, and validates pixels. |
| Parent hierarchy | [`createDescriptorUpdateTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L1907-L1918) | Registers the three implemented intermediate nodes and the delegated Vulkan-only child. |
| Delegated acceleration-structure hierarchy | [`createDescriptorUpdateASTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L2566-L2662) | Confirms the separate implementation boundary and its child matrix. |
| Registered leaves | [`binding-model.txt`](../../../mustpass/main/vk-default/binding-model.txt#L10898-L11020) | Confirms exact names and coverage. |
| Vulkan descriptor-update contract | [Descriptor Set Updates](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L2900-L3143) | Defines write ordering and descriptor-type-directed source-member access. |

## Questions / Risk Points for User Audit

- The primary behavioral axis is resolved as the three intermediate nodes implemented in `vktBindingDescriptorUpdateTests.cpp`, not the finer `samplerless` matrix.
- The `acceleration_structure` child remains registration-only on this page. No behavior, shader, or failure claims from `DescriptorUpdateAS` are pulled across the assignment boundary.
- The random path's expected result follows the final descriptor write before each completed submission. Both source and specification ordering support this interpretation.
- Shader walkthroughs are unnecessary for this page because the shaders only expose host-selected descriptor state. Their short read-and-copy or read-and-add logic does not control the tested update behavior.
- No unresolved semantic risk remains after checking source, mustpass registration, and the descriptor-set specification chapter.

## Conversion Notes for Final Wiki Rewrite

- Carry `empty_descriptor`, `samplerless`, and `random` into `## Behavior Parameters` as the implemented-intermediate-node axis.
- Copy the `### Failure Cause Mapping` table unchanged.
- Keep the descriptor type/member-access rule and zero-count binding rule as compact prerequisites.
- Preserve the host execution detail, especially samplerless exact-pixel checking and random mutation modeling.
- Keep `## Shader Analysis`, but use an evidence-based no-walkthrough statement. Do not invoke shader analysis or disassembly.
- Mark `acceleration_structure` as `(registration only)` in the hierarchy and direct readers to the separate `DescriptorUpdateAS.md` page.
