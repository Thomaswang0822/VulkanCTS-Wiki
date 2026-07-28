# Understanding Brief: `binding_model.descriptor_combination`

## One-Sentence Test Purpose

This test checks whether Vulkan keeps descriptor-buffer, push-descriptor, and traditional descriptor-set state correct across one command buffer, and whether opaque sampler capture data preserves custom border-color sampling after sampler recreation.

## Background Knowledge

### Descriptor sets and descriptor buffers use different command-buffer state

A descriptor set is an object updated through descriptor-set APIs and bound with `vkCmdBindDescriptorSets`; a descriptor buffer stores implementation-produced descriptor data in application-visible memory and is selected with `vkCmdBindDescriptorBuffersEXT` plus `vkCmdSetDescriptorBufferOffsetsEXT`. A descriptor-buffer layout is created with `VK_DESCRIPTOR_SET_LAYOUT_CREATE_DESCRIPTOR_BUFFER_BIT_EXT`, and its binding offsets come from the implementation. The shader still names resources with the same descriptor-set and binding interface, but the command buffer obtains the descriptor data through a different state path ([resource descriptors](../../../../vulkan-docs/src/chapters/descriptors.adoc#L7-L27), [descriptor-buffer layout and offsets](../../../../vulkan-docs/src/chapters/descriptorbuffers.adoc#L19-L36), [descriptor-buffer binding](../../../../vulkan-docs/src/chapters/descriptorbuffers.adoc#L661-L677)).

At one pipeline bind point, these state paths replace one another for the affected set. A `vkCmdSetDescriptorBufferOffsetsEXT` call invalidates a previous `vkCmdBindDescriptorSets` binding, and `vkCmdBindDescriptorSets` invalidates a descriptor-buffer binding. Push descriptors are recorded into the command buffer through a push-descriptor layout and command. The first registered case therefore tests ordered state changes, not simultaneous use of two descriptors for one dispatch.

Why it matters here:

- The first case binds push descriptors, a traditional descriptor set, and a descriptor buffer in sequence, with a different pipeline layout for each path.
- The descriptor-buffer binding uses the layout offset and a zero set offset, so the shader must read the storage-buffer descriptor from the intended memory location.
- A compute memory barrier connects shader writes from earlier dispatches to later shader reads. The descriptor-state transition and the memory dependency are separate parts of the test.

### Opaque sampler capture data and custom border colors

`VK_EXT_descriptor_buffer` can expose opaque capture data for a sampler. The application obtains that data with `vkGetSamplerOpaqueCaptureDescriptorDataEXT`, then supplies it through `VkOpaqueCaptureDescriptorDataCreateInfoEXT` when recreating the sampler. The `descriptorBufferCaptureReplay` feature enables this path, and `samplerCaptureReplayDescriptorDataSize` gives the required data size ([capture and replay](../../../../vulkan-docs/src/chapters/descriptorbuffers.adoc#L1196-L1208), [sampler capture data](../../../../vulkan-docs/src/chapters/descriptorbuffers.adoc#L1374-L1402), [replay structure](../../../../vulkan-docs/src/chapters/descriptorbuffers.adoc#L1502-L1548)).

A custom border sampler uses `VK_BORDER_COLOR_FLOAT_CUSTOM_EXT` with `VkSamplerCustomBorderColorCreateInfoEXT`. For a sampler with `CLAMP_TO_BORDER`, an out-of-range texture coordinate produces the sampler's border color. The test uses an explicit `VK_FORMAT_R8G8B8A8_UNORM` format and three colors, so the sampler's custom color remains observable in fragment output ([custom border-color creation](../../../../vulkan-docs/src/chapters/samplers.adoc#L1203-L1268), [border replacement](../../../../vulkan-docs/src/chapters/textures.adoc#L582-L615)).

Why it matters here:

- The descriptor buffer stores the sampled-image descriptor followed by sampler descriptors A, B, and C before the samplers are destroyed.
- The host recreates samplers in order C, B, A while pairing each one with the matching opaque capture bytes and custom color.
- The fragment shader samples the same image with all three sampler descriptors at `(2, 2)`, outside the 8 by 8 image, then combines the three returned border colors.

## One Concrete Example

The first registered case is:

```text
dEQP-VK.binding_model.descriptor_combination.basic.descriptor_buffer_and_legacy_descriptor_in_command_buffer
```

The host creates three 16-element storage buffers. One receives data through a push descriptor, one through a traditional descriptor set, and one through a descriptor buffer. The `comp_init` shader writes `gl_LocalInvocationIndex * mulVal` to binding 0. The command buffer dispatches that shader with values 3, 5, and 6 through the three descriptor paths. It then runs `comp_add` with values 2, 1, 3, and 2 on the selected buffers. The expected arrays distinguish each path and the order of all updates.

The second registered case is:

```text
dEQP-VK.binding_model.descriptor_combination.basic.descriptor_buffer_capture_replay_with_custom_border_color
```

The host creates custom-border samplers A, B, and C with red, green, and magenta colors. It writes descriptors for those sampler objects into a descriptor buffer, captures each sampler's opaque descriptor data, destroys the samplers, and recreates them in reverse order with the matching capture bytes. The fragment shader samples all three descriptors at `(2, 2)`. Since that coordinate is outside the image and all samplers clamp to border, the output must reflect red, green, and magenta in the weighted mix.

## End-to-End Test Flow

```text
1. legacy and descriptor-buffer state interaction
[host] require VK_EXT_descriptor_buffer and VK_KHR_push_descriptor
[host] create three host-visible 16-element storage buffers
[host] create push-descriptor, traditional descriptor-set, and descriptor-buffer layouts
[host] update the traditional descriptor set and encode the descriptor-buffer storage-buffer descriptor
[host] create compute pipelines for comp_init and comp_add for each layout
[host] record push-descriptor initialization, traditional-set initialization, and descriptor-buffer initialization dispatches
[host] record shader-write to shader-read barriers and the ordered add dispatches
[device] execute 4 by 4 compute workgroups through the three descriptor mechanisms
[host] wait for completion, invalidate the mapped allocations, and compare all 16 integers in each buffer
[host] return Pass only when all three expected arrays match

2. capture replay with custom border color
[host] require VK_EXT_descriptor_buffer, VK_EXT_custom_border_color, and descriptorBufferCaptureReplay
[host] create an 8 by 8 R8G8B8A8_UNORM texture image and a color-attachment readback target
[host] create custom-border samplers A, B, and C and encode the image plus sampler descriptors in a host-visible descriptor buffer
[host] capture opaque sampler data, destroy the samplers, and recreate them in order C, B, A with matching colors and capture data
[host] create the full-screen vertex and descriptor-buffer graphics pipeline
[host] transition the texture for fragment-shader reads, bind the descriptor buffer, and draw three vertices
[device] sample the texture three times at the out-of-range coordinate (2, 2), then mix the returned border colors
[host] copy the color attachment to a host-visible buffer and compare four sampled fragments with the weighted expected color
[host] return Pass only when each checked fragment is within 0.05 per component
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- The first case generates `comp_init` and `comp_add` as inline GLSL compute shaders. Both use a 4 by 4 local size, a push-constant integer, and one storage-buffer binding ([program generation](../../../modules/vulkan/binding_model/vktBindingDescriptorCombinationTests.cpp#L605-L630)).
- The second case generates `vert` and `frag` as inline GLSL graphics shaders. The vertex shader emits a full-screen triangle from `gl_VertexIndex`; the fragment shader combines three sampled-image and sampler bindings ([program generation](../../../modules/vulkan/binding_model/vktBindingDescriptorCombinationTests.cpp#L631-L656)).
- The final page should show a representative `comp_add` shader and a representative `frag` shader. Their descriptor reads and output operations materially determine the observed results, so each walkthrough needs a fresh compiler-produced SPIR-V block.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Three storage buffers in the first case | yes | one through each descriptor mechanism | read and written by compute shaders | yes | Separates the three descriptor paths and records the arithmetic sequence. |
| Descriptor buffer for the first case | yes, host-visible and device-addressable | yes | read for its storage-buffer descriptor | no | Holds the encoded descriptor selected by `vkCmdSetDescriptorBufferOffsetsEXT`. |
| Texture image and image view | yes | yes, as sampled-image binding 0 | read by the fragment shader | indirectly | Supplies the image resource paired with each sampler descriptor. |
| Three custom-border samplers | yes, then destroyed and recreated | yes through sampler bindings 1, 2, and 3 | read by fragment sampling | indirectly | Their capture data and colors must survive recreation and remain distinct. |
| Descriptor buffer for the second case | yes, host-visible and device-addressable | yes | read for one sampled-image and three sampler descriptors | no | Keeps the pre-destruction descriptor bytes available for replay verification. |
| Color attachment and transfer buffer | yes | color attachment, then transfer destination | written by rasterization and copy | yes | Carries the mixed border-color result to host validation. |

## What Is Checked

| Registered test case | Device operation | Host-side pass condition |
|----------------------|------------------|---------------------------|
| `descriptor_buffer_and_legacy_descriptor_in_command_buffer` | Sixteen-invocation `comp_init` and `comp_add` dispatches use push descriptors, a traditional descriptor set, and a descriptor buffer in one command buffer. | The three buffers equal the [source-defined arrays](../../../modules/vulkan/binding_model/vktBindingDescriptorCombinationTests.cpp#L295-L309). |
| `descriptor_buffer_capture_replay_with_custom_border_color` | A fragment shader samples the descriptor-buffer image with three recreated custom-border samplers. | Four selected fragments are within 0.05 of `mix(mix(red, green, 0.25), magenta, 0.7)` ([result scan](../../../modules/vulkan/binding_model/vktBindingDescriptorCombinationTests.cpp#L551-L567)). |

The first case uses exact integer comparison for all 48 output integers. The second case converts each checked four-byte pixel to normalized floats and permits a per-component absolute difference of 0.05. A failed case returns `Fail`; a supported case that satisfies its check returns `Pass` ([first result scan](../../../modules/vulkan/binding_model/vktBindingDescriptorCombinationTests.cpp#L295-L312), [second result scan](../../../modules/vulkan/binding_model/vktBindingDescriptorCombinationTests.cpp#L551-L569)).

## Behavior Parameter Identification

> **Behavior parameter:** registered test case leaf under `binding_model.descriptor_combination.basic`
>
> **Candidate values:** `descriptor_buffer_and_legacy_descriptor_in_command_buffer`, `descriptor_buffer_capture_replay_with_custom_border_color`

The two leaves are the primary behavioral axis. They select different test instances, resource models, command sequences, shaders, support gates, observables, and failure causes.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `descriptor_buffer_and_legacy_descriptor_in_command_buffer` | Descriptor-buffer, push-descriptor, or traditional descriptor-set state selection failure; missing shader-write to shader-read ordering; or storage-buffer result/readback failure. |
| `descriptor_buffer_capture_replay_with_custom_border_color` | Sampler opaque capture-data replay failure; custom border-color or sampler descriptor encoding failure; sampled-image layout or graphics synchronization failure; or color result/readback failure. |

## Important Variations and Special Cases

- The source registers exactly two test case leaves below `basic`; it has no generated parameter matrix beyond the fixed resource and command sequences ([registration](../../../modules/vulkan/binding_model/vktBindingDescriptorCombinationTests.cpp#L668-L684)).
- In the first case, the three descriptor paths use separate layouts and pipelines. The descriptor-buffer pipelines carry `VK_PIPELINE_CREATE_DESCRIPTOR_BUFFER_BIT_EXT`; the push and traditional pipelines do not ([pipeline creation](../../../modules/vulkan/binding_model/vktBindingDescriptorCombinationTests.cpp#L189-L204)).
- The first case's `VkMemoryBarrier` covers shader writes to shader reads at the compute stage. It does not substitute for descriptor binding; it orders buffer data accesses after earlier dispatches ([barrier recording](../../../modules/vulkan/binding_model/vktBindingDescriptorCombinationTests.cpp#L237-L281), [memory dependency](../../../../vulkan-docs/src/chapters/synchronization.adoc#L137-L147)).
- The second case uses `VK_SAMPLER_CREATE_DESCRIPTOR_BUFFER_CAPTURE_REPLAY_BIT_EXT` on each sampler and `samplerCaptureReplayDescriptorDataSize` bytes per captured sampler. The source reverses both sampler recreation order and color selection while pairing each sampler with its matching opaque data ([sampler setup](../../../modules/vulkan/binding_model/vktBindingDescriptorCombinationTests.cpp#L397-L419), [capture and recreation](../../../modules/vulkan/binding_model/vktBindingDescriptorCombinationTests.cpp#L476-L503)).
- The second case stores `VK_IMAGE_LAYOUT_ATTACHMENT_OPTIMAL` in its sampled-image descriptor and records a barrier to `VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL` before the draw ([descriptor encoding](../../../modules/vulkan/binding_model/vktBindingDescriptorCombinationTests.cpp#L454-L474), [image transition](../../../modules/vulkan/binding_model/vktBindingDescriptorCombinationTests.cpp#L524-L529)). The source does not gate the leaf on `descriptorBufferImageLayoutIgnored`. When that feature is false, Vulkan uses the supplied descriptor layout and requires it to match the accessed subresource. The two layouts in this source do not match, so the leaf's legal execution depends on `descriptorBufferImageLayoutIgnored` even though `checkSupport()` does not enforce it ([feature definition](../../../../vulkan-docs/src/chapters/features.adoc#L6156-L6159), [layout matching](../../../../vulkan-docs/src/chapters/resources.adoc#L5603-L5631), [support check](../../../modules/vulkan/binding_model/vktBindingDescriptorCombinationTests.cpp#L592-L603)).

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Binding-model attachment | [`createChildren()`](../../../modules/vulkan/binding_model/vktBindingModelTests.cpp#L52-L70) | Shows that this test family is omitted from Vulkan SC builds and attached under `binding_model` in other builds. |
| Case registration | [`populateDescriptorCombinationTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorCombinationTests.cpp#L668-L684) | Defines `basic` and the two exact test case leaves. |
| Legacy and descriptor-buffer runtime | [`DescriptorCombinationTestInstance::iterate()`](../../../modules/vulkan/binding_model/vktBindingDescriptorCombinationTests.cpp#L81-L313) | Creates resources, records the ordered compute operations, and checks the three arrays. |
| Capture-replay runtime | [`DescriptorCustomBorderColorTestInstance::iterate()`](../../../modules/vulkan/binding_model/vktBindingDescriptorCombinationTests.cpp#L362-L569) | Creates, captures, recreates, binds, samples, and checks custom-border samplers. |
| Support and program selection | [`DescriptorCombinationTestCase`](../../../modules/vulkan/binding_model/vktBindingDescriptorCombinationTests.cpp#L572-L666) | Defines support pruning, shader sources, and the split between the two test instances. |
| Mustpass coverage | [`binding-model.txt`](../../../mustpass/main/vk-default/binding-model.txt#L10150-L10151) | Confirms both executable leaves in the default Vulkan mustpass list. |
| Descriptor-buffer state interaction | [Binding descriptor buffers](../../../../vulkan-docs/src/chapters/descriptorbuffers.adoc#L661-L677) | Defines the separate binding point and invalidation relationship with traditional descriptor sets. |
| Descriptor-buffer capture replay | [Capture and replay](../../../../vulkan-docs/src/chapters/descriptorbuffers.adoc#L1196-L1208) | Defines opaque descriptor data and the capture/replay feature. |
| Sampler opaque data | [`vkGetSamplerOpaqueCaptureDescriptorDataEXT`](../../../../vulkan-docs/src/chapters/descriptorbuffers.adoc#L1374-L1402) | Defines the sampler data query and required property size. |
| Replay data structure | [`VkOpaqueCaptureDescriptorDataCreateInfoEXT`](../../../../vulkan-docs/src/chapters/descriptorbuffers.adoc#L1502-L1548) | Defines how opaque data enters sampler recreation. |
| Custom border colors | [`VkSamplerCustomBorderColorCreateInfoEXT`](../../../../vulkan-docs/src/chapters/samplers.adoc#L1203-L1268) | Defines the custom color and format relationship. |
| Border replacement | [Border replacement](../../../../vulkan-docs/src/chapters/textures.adoc#L582-L615) | Defines the out-of-range sample result used by the fragment shader. |
| Feature and property definitions | [`VkPhysicalDeviceDescriptorBufferFeaturesEXT`](../../../../vulkan-docs/src/chapters/features.adoc#L6134-L6162), [`samplerCaptureReplayDescriptorDataSize`](../../../../vulkan-docs/src/chapters/limits.adoc#L4431-L4450) | Defines support and buffer-size inputs used by the source. |
| Synchronization semantics | [Memory dependencies](../../../../vulkan-docs/src/chapters/synchronization.adoc#L137-L147) | Defines availability and visibility between shader writes and reads. |

## Questions / Risk Points for User Audit

- Does the first flow make clear that descriptor-buffer and traditional descriptor bindings replace one another at the same set state rather than serving one dispatch simultaneously?
- Does the first expected-array table remain tied to the push, traditional, and descriptor-buffer buffers?
- Does the second flow distinguish opaque descriptor data from the sampler's custom border-color value?
- Does the out-of-range coordinate explain why the texture's stored texels do not determine the checked color?
- Are `descriptorBufferCaptureReplay`, `samplerCaptureReplayDescriptorDataSize`, and the custom-border feature rules separated from the local source's explicit support checks?
- Are shader walkthroughs limited to the two shader stages whose descriptor reads determine the observables?

## Conversion Notes for Final Wiki Rewrite

- Use the two registered test case leaves as the primary behavior axis and keep their runtime mechanisms separate.
- Copy the `### Failure Cause Mapping` table unchanged into the final page.
- Distill the two descriptor-state and capture-replay background topics into short page-local prerequisite bullets.
- Include one representative `comp_add` walkthrough and one representative `frag` walkthrough, each with full compiler-produced SPIR-V generated from the exact target `spirv1.0`.
- Keep the vertex shader as a runtime detail because it only generates the full-screen triangle and does not determine descriptor values.
- Preserve the exact support checks, mustpass lines, result tolerances, and source/spec links. Do not infer a particular driver or hardware fault from a failed observable.
