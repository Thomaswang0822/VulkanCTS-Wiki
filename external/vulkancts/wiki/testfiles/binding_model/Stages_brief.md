# Understanding Brief: `binding_model.stages`

## One-Sentence Test Purpose

This test checks whether one `vkCmdBindDescriptorSets2` call binds the same valid descriptor sets for later graphics and compute work when its stage mask selects both pipeline bind points.

## Background Knowledge

### Stage masks can select more than one pipeline bind point

`VkBindDescriptorSetsInfo::stageFlags` specifies the shader stages affected by `vkCmdBindDescriptorSets2`. If any listed stage belongs to a pipeline bind point, the operation affects all stages for that bind point. A mask containing fragment and compute bits is equivalent to one traditional descriptor-set bind for graphics and another for compute ([`VkBindDescriptorSetsInfo`](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L4720-L4764)). Graphics and compute pipeline bindings remain independent, so binding one pipeline does not disturb the other ([pipeline bind points](../../../../vulkan-docs/src/chapters/pipelines.adoc#L9794-L9819)).

Why it matters here:

- The test records one descriptor-set binding call before binding either pipeline.
- `VK_SHADER_STAGE_FRAGMENT_BIT | VK_SHADER_STAGE_COMPUTE_BIT` selects both graphics and compute descriptor-set state.
- The later draw and dispatch use the same pipeline layout and the same two descriptor sets.

### Descriptor layouts control access and compatibility

A descriptor-set layout binding declares its descriptor type and stage visibility. A shader stage omitted from `stageFlags` must not access the binding, while one binding may be visible to both graphics and compute stages ([layout binding stage visibility](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L435-L469)). A descriptor set remains usable after a pipeline change when its pipeline layout is compatible and the binding has not been disturbed ([pipeline layout compatibility](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L2021-L2055)). A consumed descriptor also needs defined contents, a matching descriptor type, and a valid binding ([descriptor validity](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L4583-L4618)).

Why it matters here:

- Set 0 contains the selected read descriptor. Set 1 contains a storage buffer for compute output.
- Both set layouts expose binding 0 to fragment and compute stages.
- The host writes every consumed descriptor with `vkUpdateDescriptorSets` before command recording. Buffer writes use `VkDescriptorBufferInfo`; the image case uses `VkDescriptorImageInfo` with a sampler, image view, and shader-read layout ([descriptor set updates](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L2900-L2934), [resource validity for descriptor writes](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L2955-L2992)).

### Synchronization applies to resource use, not descriptor-state selection

Execution order alone does not make memory writes visible to later accesses. A memory dependency combines execution order with availability and visibility for the selected access scopes ([execution and memory dependencies](../../../../vulkan-docs/src/chapters/synchronization.adoc#L71-L182)). This test's graphics and compute shaders both read the input and write separate outputs, so they do not have a read/write hazard with each other. The image case does need transfer-to-shader synchronization before sampling, and the color attachment needs a color-write-to-transfer-read barrier before readback.

## One Concrete Example

Consider `dEQP-VK.binding_model.stages.storage_buffer`. The host fills a 16-byte storage buffer with `1.0`, `2.0`, `3.0`, and `4.0`. Set 0 binding 0 points to that buffer. Set 1 binding 0 points to a second storage buffer used for compute output ([buffer descriptor setup](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L143-L187), [output descriptor setup](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L303-L335)).

One `vkCmdBindDescriptorSets2` call names both sets, the shared pipeline layout, and fragment-plus-compute stage flags. The host then draws a 32 by 32 image before dispatching four compute invocations. The fragment shader divides the four input values by four and emits `(0.25, 0.5, 0.75, 1.0)`; the compute shader copies the four original values to the output buffer. Both observations must pass ([mixed command sequence](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L372-L434), [result comparison](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L436-L468)).

## End-to-End Test Flow

```text
[host] select storage_buffer, uniform_buffer, or combined_image_sampler
[host] create set 0 for the selected read descriptor and set 1 for compute output
[host] create one pipeline layout used by both graphics and compute pipelines
[host] initialize 1, 2, 3, 4 as buffer values or an equivalent repeating image color
[host] update both descriptor sets before recording the main command buffer
[host] for the image case, copy texels and transition the image to SHADER_READ_ONLY_OPTIMAL
[host] call vkCmdBindDescriptorSets2 once with fragment and compute stage bits
[host] bind the graphics pipeline, draw four vertices, and end the render pass
[device] the fragment shader reads set 0 and writes the expected normalized color
[host] bind the compute pipeline and dispatch four invocations
[device] the compute shader reads set 0 and writes four values through set 1
[host] transition the color image for transfer and copy it to a host-visible buffer
[host] submit once and wait for completion
[host] compare compute output with 1, 2, 3, 4 and every pixel with 0.25, 0.5, 0.75, 1.0
```

The draw comes before the dispatch, but neither operation produces data consumed by the other. Their shared dependency is descriptor state established by the earlier binding command. The explicit barrier after dispatch covers color-attachment writes before the image-to-buffer copy; the dispatch does not touch the color image ([main command buffer](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L404-L434)).

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

`StagesTestCase::initPrograms()` emits three GLSL 4.50 shaders for each descriptor-type leaf ([shader generation](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L493-L576)):

- The fixed vertex shader derives four clip-space corners from `gl_VertexIndex`.
- The fragment and compute shaders declare set 0 as a storage buffer, uniform buffer, or combined image sampler according to the leaf.
- The compute shader always declares set 1 as a storage buffer. Buffer leaves copy one selected scalar per invocation. The image leaf samples one texel and multiplies each component by four.
- The fragment shader emits the four buffer values divided by four or samples the image center.
- No explicit `ShaderBuildOptions` are supplied, so the source collection uses the CTS baseline SPIR-V 1.0 target ([baseline target](../../../framework/vulkan/vkPrograms.cpp#L1048-L1052)).

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Read buffer | yes | set 0 for buffer leaves; transfer source for image initialization | read by fragment and compute shaders for buffer leaves | no | Holds `1.0`, `2.0`, `3.0`, `4.0`, or the bytes copied into the sampled image. |
| Sampled image, view, and sampler | image leaf only | set 0 as a combined image sampler | transfer-written, then sampled by fragment and compute shaders | indirectly through both outputs | Changes the read path from buffer loads to texture sampling. |
| Write buffer | yes | set 1 as a storage buffer | written by four compute invocations | yes | Carries the compute observation to the host. |
| Color image | yes | color attachment, then transfer source | written by the fragment shader and copied | through the color output buffer | Carries the graphics observation to the host. |
| Color output buffer | yes | transfer destination | receives the image copy | yes | Lets the host inspect every rendered pixel. |
| Shared pipeline layout | yes | used for descriptor binding and both pipelines | defines set compatibility | no | Makes one descriptor-set bind applicable to both graphics and compute pipelines. |

## What Is Checked

| Observation | Expected values | Host check |
|-------------|-----------------|------------|
| Compute output buffer | `1.0`, `2.0`, `3.0`, `4.0` | Each float must differ from its reference by less than `0.02`. |
| Graphics color image | every pixel is `(0.25, 0.5, 0.75, 1.0)` | Every component of every `32 x 32` pixel must differ from its reference by less than `0.02`. |

The image bytes are `63`, `127`, `191`, and `255` in every texel. Their UNORM values are close to the quarter-step references. The compute shader multiplies them by four, while the fragment shader uses them as the rendered color. The tolerance covers the expected UNORM quantization ([image initialization](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L191-L300), [host checks](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L436-L468)).

Both checks must pass. A correct framebuffer with a wrong compute buffer, or the reverse, proves that one bind point did not produce the expected observation even though the other did.

## Behavior Parameter Identification

> **Behavior parameter:** descriptor-type test case leaf under `binding_model.stages`
>
> **Candidate values:** `storage_buffer`, `uniform_buffer`, `combined_image_sampler`

The leaf is the primary behavioral axis because it changes the set 0 descriptor type, backing resource, shader declaration, shader read operation, image synchronization needs, and initialization path. The shared stage mask, one-call binding mechanism, command order, output resources, and comparisons stay fixed.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `storage_buffer` | Storage-buffer descriptor binding or stage visibility failure, storage-buffer load failure, or shared graphics/compute execution and readback failure. |
| `uniform_buffer` | Uniform-buffer descriptor binding or stage visibility failure, uniform-block load failure, or shared graphics/compute execution and readback failure. |
| `combined_image_sampler` | Combined-image-sampler binding or stage visibility failure, image layout or sampling failure, or shared graphics/compute execution and readback failure. |

## Important Variations and Special Cases

- `storage_buffer` and `uniform_buffer` use the same 16-byte initialized buffer and the same arithmetic. They differ in descriptor type and GLSL interface: a runtime float array in a storage block versus one `vec4` in a uniform block.
- `combined_image_sampler` creates a `4 x 4` `VK_FORMAT_R8G8B8A8_UNORM` image, copies repeating RGBA bytes into it, and transitions it to `VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL` before the main submission. This adds image-view, sampler, layout, filtering, and transfer synchronization behavior.
- The graphics pipeline uses only set 0, while the compute pipeline uses sets 0 and 1. The call still binds both sets at both selected bind points. A shader need not access every layout set, but every statically accessed set needs a compatible bound descriptor set ([bound descriptor requirements](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L4583-L4594)).
- The source requires `VK_KHR_maintenance6` for all three leaves. The parent registration excludes the entire `stages` family from `CTS_USES_VULKANSC` builds ([support check](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L579-L582), [category registration](../../../modules/vulkan/binding_model/vktBindingModelTests.cpp#L61-L71)).
- The default Vulkan mustpass list contains exactly the three leaves, in lexical order: `combined_image_sampler`, `storage_buffer`, and `uniform_buffer` ([mustpass evidence](../../../mustpass/main/vk-default/binding-model.txt#L146932-L146934)).

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Binding-model attachment | [`createChildren()`](../../../modules/vulkan/binding_model/vktBindingModelTests.cpp#L52-L71) | Attaches `stages` under `binding_model` outside Vulkan SC builds. |
| Test-family factory | [`createStagesTests()`](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L586-L613) | Registers the exact three descriptor-type leaves. |
| Layouts and descriptor sets | [`StagesTestInstance::iterate()`](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L90-L113) | Creates two set layouts visible to fragment and compute stages and one shared pipeline layout. |
| Buffer input setup | [`StagesTestInstance::iterate()`](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L143-L187) | Creates, updates, and initializes storage or uniform input. |
| Image input setup | [`StagesTestInstance::iterate()`](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L189-L300) | Creates the sampled image and performs transfer-to-shader synchronization. |
| Compute output setup | [`StagesTestInstance::iterate()`](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L303-L335) | Creates and updates the set 1 storage-buffer descriptor. |
| Pipelines and one-call bind | [`StagesTestInstance::iterate()`](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L337-L405) | Builds both pipelines and records `vkCmdBindDescriptorSets2` with both stage bits. |
| Mixed draw/dispatch and copyback | [`StagesTestInstance::iterate()`](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L407-L434) | Records graphics work, compute work, the color-image barrier, and copyback in order. |
| Result comparison | [`StagesTestInstance::iterate()`](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L436-L468) | Checks all four compute floats and every framebuffer component. |
| Shader generation | [`StagesTestCase::initPrograms()`](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L493-L576) | Emits exact descriptor-type-dependent compute and fragment shaders. |
| Mustpass inventory | [`binding-model.txt`](../../../mustpass/main/vk-default/binding-model.txt#L146932-L146934) | Confirms the three executable registered paths. |
| Multi-bind-point stage semantics | [`vkCmdBindDescriptorSets2` and `VkBindDescriptorSetsInfo`](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L4688-L4774) | Defines how fragment and compute stage bits select graphics and compute bind points in one call. |
| Layout visibility, compatibility, and validity | [layout bindings](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L435-L469), [layout compatibility](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L2021-L2055), [descriptor validity](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L4583-L4618) | Defines the conditions under which both pipelines can consume the bound sets. |
| Synchronization | [execution and memory dependencies](../../../../vulkan-docs/src/chapters/synchronization.adoc#L71-L182) | Explains the image upload and color readback barriers. |

## Questions / Risk Points for User Audit

- Does the explanation distinguish descriptor-set binding from descriptor-set updating? Yes. `vkUpdateDescriptorSets` initializes the sets; `vkCmdBindDescriptorSets2` applies them to both selected bind points.
- Is the fragment-plus-compute stage mask interpreted as selecting graphics and compute pipeline bind points? Yes, directly from `VkBindDescriptorSetsInfo` semantics.
- Is the draw-before-dispatch order clear without implying a data dependency? Yes. Both operations read set 0 and write separate outputs.
- Are both independent host comparisons included? Yes. The brief covers four compute floats and every framebuffer component.
- Is the descriptor-type leaf the behavior axis? Yes. Source registration and shader/resource branches use that exact dimension.
- No unresolved semantic risk remains after checking source, parent registration, mustpass paths, local specification chapters, and all generated shader variants.

## Conversion Notes for Final Wiki Rewrite

- Use `storage_buffer`, `uniform_buffer`, and `combined_image_sampler` as the `## Behavior Parameters` values.
- Copy the `### Failure Cause Mapping` table unchanged into the final page.
- Keep the stage-mask-to-bind-point rule, compatible shared pipeline layout, descriptor validity, and relevant synchronization as compact prerequisites.
- Use two walkthroughs because buffer loads and image sampling have different shader interfaces and resource paths. Show the storage-buffer compute shader and combined-image-sampler fragment shader. Explain the uniform-block difference and the complementary stages in the variation summaries.
- Preserve the draw-then-dispatch order, separate outputs, post-render barrier, submission wait, and both host comparisons in `## Runtime Execution and Result Checking`.
- Write fresh cause analysis with separate symptoms and grounded possible causes for all three mapped leaf values.
