# Understanding Brief: binding_model.shader_access / vktBindingShaderAccessTests.cpp

## One-Sentence Test Purpose

This test checks whether Vulkan descriptor bindings reach the shader correctly when the same resource-access cases use primary or secondary command buffers, the legacy or maintenance6 bind command, several descriptor update methods, descriptor types, shader stages, and descriptor-set layouts.

## Background Knowledge

### Descriptor set bindings and shader interfaces

A Vulkan descriptor is opaque data that gives a shader access to a buffer, image, sampler, or texel buffer. A shader resource declaration carries `DescriptorSet` and `Binding` decorations, and the pipeline layout connects those decorations to descriptor-set layouts. At draw or dispatch recording time, every descriptor set number used by a pipeline must have a compatible bound set. The specification describes these rules in [Resource Descriptors](../../../../vulkan-docs/src/chapters/descriptors.adoc#descriptors) and [Descriptor Set Binding](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#descriptor-set-binding).

Why it matters here:

- The generated shader changes its descriptor declarations between one descriptor, multiple bindings, large binding gaps, arrays, and multiple set numbers.
- The host must create compatible layouts, update the descriptors, bind the sets at the right set numbers, and then execute a pipeline that consumes them.
- A descriptor that is never bound, has the wrong type, or is disturbed by incompatible pipeline layout state is not a valid source for the shader access under test.

### Primary and secondary command buffers

A primary command buffer can record the render pass and draw directly. A secondary command buffer cannot be submitted by itself; a primary command buffer executes it with `vkCmdExecuteCommands`. In this test, the secondary path records pipeline binding, descriptor binding, and draw commands in the secondary buffer, then executes that buffer inside a render pass with matching inheritance information. The Vulkan execution rules are described in [Secondary Command Buffer Execution](../../../../vulkan-docs/src/chapters/cmdbuffers.adoc#commandbuffers-secondary).

Why it matters here:

- `primary_cmd_buf` tests descriptor binding in the command buffer that records the render pass and draw.
- `secondary_cmd_buf` tests descriptor binding in the executed secondary command buffer while the primary command buffer supplies the render-pass context.
- The registration excludes `compute` from `secondary_cmd_buf` because the source marks compute as unsupported for secondary command buffers.

### Dynamic buffer offsets

For dynamic uniform or storage-buffer descriptors, the effective offset combines the descriptor's base buffer offset and the dynamic offset supplied by the bind command. Vulkan orders dynamic offsets by set, binding, and array element, as described in [Descriptor Set Binding](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#descriptors-binding-dynamicoffsets). This test also has a static view-offset dimension. The generated buffer data is placed so that selecting the intended effective range changes which color values the shader reads.

Why it matters here:

- `offset_view_*` cases change the descriptor range offset.
- `*_dynamic_zero` and `*_dynamic_nonzero` cases add dynamic descriptors and bind-time offsets.
- The source intentionally treats the dynamic offset as replacing the view offset for dynamic descriptor cases, rather than adding it to the view offset a second time.

## One Concrete Example

Representative mustpass case:

```text
dEQP-VK.binding_model.shader_access.primary_cmd_buf.bind.storage_buffer.vertex.single_descriptor.offset_view_zero
```

For this case:

1. `primary_cmd_buf` records the graphics commands in the primary command buffer.
2. `bind` selects `vkCmdBindDescriptorSets`, rather than `vkCmdBindDescriptorSets2`.
3. `storage_buffer` creates one mutable storage-buffer descriptor.
4. `vertex` makes the vertex shader the active resource-access stage while the fragment shader passes the color through.
5. `single_descriptor` emits one descriptor at set `0`, binding `0`.
6. `offset_view_zero` leaves the descriptor view offset at zero.

The generated vertex shader divides six vertices into four quadrants. It selects `colorA` for quadrants 1 and 2 and `colorB` for quadrants 0 and 3. The host initializes the selected buffer range with the matching color pair. The shader writes the selected color to `frag_color`, and the fragment stage forwards it to the color attachment.

The exact generated shader and compiler-produced SPIR-V for this representative case appear in the final page's `Representative Shader Walkthrough 1`.

## End-to-End Test Flow

```text
[host] register the `shader_access` hierarchy and select one combination of binding path, bind command, update method, descriptor type, shader stage, descriptor-set layout, interface shape, and resource variant
[host] check required Vulkan extensions, features, shader-stage support, and image-view support
[host] generate GLSL for the active stage and the passthrough or helper stages needed by the selected pipeline
[host] create source buffers, images, image views, samplers, texel-buffer views, descriptor pools, descriptor-set layouts, descriptor sets, and the pipeline layout
[host] update descriptors with `vkUpdateDescriptorSets`, a descriptor update template, push descriptors, or a push descriptor template
[host] record the selected descriptor binding operation and the draw or dispatch
[host] for the secondary path, record the pipeline, descriptor binding, and draw in a secondary command buffer and execute it from a primary render-pass command buffer
[device] run the generated shader; access the selected descriptors and produce quadrant colors or four compute result values
[host] submit the command buffer and wait for completion
[host] read the color attachment or compute result buffer and compare it with the expected descriptor-derived values
[host] pass the test when all checked pixels or all four compute result values match; otherwise report a failed image comparison or invalid result values
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- GLSL stages come from `QuadrantRendederCase::initPrograms()` and the stage-specific generators. The active stage calls the descriptor access generator; other graphics stages either transport the color or pass it through. Compute cases generate one `local_size_x = 1` shader with a result storage buffer.
- Pipeline state uses a triangle list when no tessellation stage is present and a patch list when tessellation stages exist. The graphics path draws four quadrants. The compute path dispatches four workgroups and stores one `vec4` per workgroup.
- The representative page walkthrough uses the exact `#version 310 es` vertex shader shape selected by `BufferDescriptorCase`, with SPIR-V generated from that reconstructed GLSL using the baseline `spirv1.0` target.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Source buffer or image | Yes | Yes through descriptor sets or push descriptors | Read by the active shader stage | No | Carries the color values that identify the descriptor selected by the shader. |
| Sampler and image view | Yes for sampler and image cases | Yes through the selected descriptor type | Sampled or fetched by the active shader stage | No | Exercises sampler mutability, immutable samplers, image view shape, mip, and array-slice handling. |
| Texel buffer view | Yes | Yes through a uniform or storage texel-buffer descriptor | Fetched by the active shader stage | No | Exercises texel-buffer descriptors and zero or nonzero view offsets. |
| Descriptor set layouts and sets | Yes | Yes, or represented by push descriptors | Provide the shader-visible bindings | No | Connects the registered layout shape to the generated `set` and `binding` declarations. |
| Graphics color attachment | Yes | Yes as a framebuffer attachment | Written by fragment output | Yes | Carries the four quadrant results to the host comparison. |
| Compute result buffer | Yes | Yes at set `0`, binding `0` in the generated compute shader | Written by the compute shader | Yes | Receives four `vec4` values that the host compares to references. |
| Secondary command buffer | Yes | Executed from a primary command buffer | Records pipeline, binding, and draw commands | No | Separates the `secondary_cmd_buf` binding path from the primary path. |

The shader-local `quadrant_id`, `result_color`, and generated stage variables are not host-created Vulkan resources.

## What Is Checked

- Graphics cases build a reference image with the expected quadrant colors. The host compares the rendered image with `bilinearCompare`; any mismatch returns `Image verification failed`.
- Compute buffer cases initialize the result buffer to `-1`, dispatch four workgroups, invalidate the host-visible allocation, and compare all four `vec4` results with the calculated references. An untouched buffer reports `Result buffer was not written to`; any other mismatch reports `Invalid result values`.
- The expected result depends on the active shader stages, descriptor-set count, interface shape, descriptor type, and resource-specific variant. In active-stage cases, the shader must consume the intended descriptor data. In `no_access`, the shader produces the fixed green/yellow reference without consuming the tested descriptor.

## Behavior Parameter Identification

> **Behavior parameter:** command-buffer binding path
>
> **Candidate values:** `primary_cmd_buf`, `secondary_cmd_buf`

The source registers these as the two direct intermediate nodes under the `shader_access` test family. They change where the descriptor binding and consuming draw are recorded. Other registered dimensions vary the resource or API details inside each path and are documented as parameter dimensions and variations.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `primary_cmd_buf` | Descriptor delivery through the selected layout, update, bind, shader interface, or primary execution path. |
| `secondary_cmd_buf` | Descriptor and pipeline state recorded in the secondary command buffer, or its render-pass inheritance and execution from the primary command buffer. |

## Important Variations and Special Cases

- `bind` calls `vkCmdBindDescriptorSets`. `bind2` calls `vkCmdBindDescriptorSets2` or its KHR form through `VkBindDescriptorSetsInfoKHR` and requires `VK_KHR_maintenance6` in the buffer cases.
- Normal updates use `vkUpdateDescriptorSets`. Non-VulkanSC builds also register `with_template`, `with_push`, and `with_push_template`. Push descriptor methods create only one descriptor-set layout, so the multiple-set branches are omitted for those update methods.
- The descriptor matrix covers mutable and immutable samplers, combined image samplers, storage images, uniform and storage texel buffers, uniform and storage buffers, and dynamic uniform and storage buffers. `VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE` is intentionally omitted because the source notes that this test has no way to access it without a sampler.
- The active-stage matrix includes `no_access`, `vertex`, `tess_ctrl`, `tess_eval`, `geometry`, `fragment`, `compute`, and `vertex_fragment`. `compute` is excluded from `secondary_cmd_buf` by `supportsSecondaryCmdBufs = false`.
- Interface shapes select one descriptor, two contiguous bindings, two discontiguous bindings, two high-valued arbitrary bindings, or a two-element descriptor array. Multiple descriptor-set variants use set numbers `0` and `1`, or `0` and `2` with an empty set layout between them.
- Image generation prunes view shapes for discontiguous and arbitrary interfaces and for discontiguous descriptor-set cases. Dynamic buffer cases omit push descriptor update methods because the source does not support dynamic buffers with push descriptor sets.
- Feature and extension checks skip unsupported cases. The source checks descriptor update extensions, storage access features for active graphics stages, `imageCubeArray`, shader-stage support, and `VK_KHR_maintenance6` for `bind2`.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Test-family registration and matrix | [createShaderAccessTests()](../../../modules/vulkan/binding_model/vktBindingShaderAccessTests.cpp#L9724-L10011) | Defines `primary_cmd_buf`, `secondary_cmd_buf`, bind commands, update methods, descriptor types, stages, interface shapes, and set-count branches. |
| Buffer shader generation | [QuadrantRendederCase::genVertexSource()](../../../modules/vulkan/binding_model/vktBindingShaderAccessTests.cpp#L3052-L3100), [BufferDescriptorCase::genResourceDeclarations()](../../../modules/vulkan/binding_model/vktBindingShaderAccessTests.cpp#L3466-L3553), [BufferDescriptorCase::genResourceAccessSource()](../../../modules/vulkan/binding_model/vktBindingShaderAccessTests.cpp#L3556-L3602) | Shows the representative vertex shader declarations, quadrant mapping, descriptor-member selection, and interface variants. |
| All generated stages | [QuadrantRendederCase::genTessCtrlSource()](../../../modules/vulkan/binding_model/vktBindingShaderAccessTests.cpp#L3103-L3180), [QuadrantRendederCase::genTessEvalSource()](../../../modules/vulkan/binding_model/vktBindingShaderAccessTests.cpp#L3183-L3235), [QuadrantRendederCase::genGeometrySource()](../../../modules/vulkan/binding_model/vktBindingShaderAccessTests.cpp#L3238-L3290), [QuadrantRendederCase::genFragmentSource()](../../../modules/vulkan/binding_model/vktBindingShaderAccessTests.cpp#L3292-L3355), [QuadrantRendederCase::genComputeSource()](../../../modules/vulkan/binding_model/vktBindingShaderAccessTests.cpp#L3358-L3400) | Shows how active and passthrough stages carry the descriptor-derived color. |
| Descriptor binding helper | [bindDescriptorSets()](../../../modules/vulkan/binding_model/vktBindingShaderAccessTests.cpp#L478-L508) | Selects `vkCmdBindDescriptorSets` or `vkCmdBindDescriptorSets2`. |
| Primary and secondary graphics execution | [SingleCmdRenderInstance::renderToTarget()](../../../modules/vulkan/binding_model/vktBindingShaderAccessTests.cpp#L1001-L1062), [BufferRenderInstance::writeDrawCmdBuffer()](../../../modules/vulkan/binding_model/vktBindingShaderAccessTests.cpp#L1868-L1937) | Places pipeline, descriptor binding, and draw commands in the selected command buffer. |
| Compute execution and barriers | [ComputeCommand::submitAndWait()](../../../modules/vulkan/binding_model/vktBindingShaderAccessTests.cpp#L2226-L2317) | Binds descriptors, applies host-to-shader and shader-to-host barriers, dispatches four workgroups, and waits. |
| Graphics result checking | [BufferRenderInstance::verifyResultImage()](../../../modules/vulkan/binding_model/vktBindingShaderAccessTests.cpp#L1939-L1983) | Builds the expected quadrant colors and compares the rendered image. |
| Compute result checking | [BufferComputeInstance::testResourceAccess()](../../../modules/vulkan/binding_model/vktBindingShaderAccessTests.cpp#L2804-L3008) | Computes references, reads the result buffer, and distinguishes untouched from incorrect results. |
| Support checks | [verifyDriverSupport()](../../../modules/vulkan/binding_model/vktBindingShaderAccessTests.cpp#L164-L259), [BufferDescriptorCase::checkSupport()](../../../modules/vulkan/binding_model/vktBindingShaderAccessTests.cpp#L3631-L3635) | Defines extension, feature, image, shader-stage, and `bind2` requirements. |
| Mustpass representative | [binding-model.txt](../../../mustpass/main/vk-default/binding-model.txt#L65729) | Confirms the exact representative path used in the brief and final walkthrough. |
| Descriptor semantics | [descriptors.adoc](../../../../vulkan-docs/src/chapters/descriptors.adoc#descriptors), [descriptorsets.adoc](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#descriptor-set-binding) | Grounds descriptor access, set binding, validity, and dynamic-offset explanations. |
| Secondary execution semantics | [cmdbuffers.adoc](../../../../vulkan-docs/src/chapters/cmdbuffers.adoc#commandbuffers-secondary) | Grounds the primary execution of the secondary command buffer and render-pass inheritance. |
| Shader access synchronization | [synchronization.adoc](../../../../vulkan-docs/src/chapters/synchronization.adoc#synchronization-access-types) | Grounds shader uniform, sampled, storage, host, and transfer access masks used by the host barriers. |

## Questions / Risk Points for User Audit

- Is `primary_cmd_buf` versus `secondary_cmd_buf` the useful primary behavioral axis for this page, given that all other dimensions vary the resource-access mechanism inside each family?
- Does the representative storage-buffer vertex case make the descriptor declaration, quadrant selection, and host-side image check clear enough?
- Should a future revision add a separate image or descriptor-array walkthrough, or is the parameter variation summary sufficient for those cases?
- Are the source-level explanations of `bind2`, push descriptors, and dynamic-offset pruning sufficiently bounded by the inspected implementation and specification text?
- The mustpass list is generated and large. The representative line anchor was checked in the current checkout and may move if the generated list changes.

## Conversion Notes for Final Wiki Rewrite

- Distill descriptor/set compatibility, primary versus secondary execution, and dynamic effective offsets into the final page's `Background Knowledge` section.
- Use the exact representative path above for one generated vertex walkthrough. Keep image, texel-buffer, compute, stage, interface, and set-count changes in `Parameter Variation Summary` and `Important variations` rather than adding more walkthroughs.
- Copy the `### Failure Cause Mapping` table into `ShaderAccess.md` unchanged. Write `### Cause Analysis` fresh in the final page.
- Keep the distinction between shader-generated artifacts and host-created resources visible in the final page.
- Keep generated code details in the shader section and source appendix; keep the runtime section focused on binding, execution, copyback, and result checking.
