# Understanding Brief: `api.descriptor_set`

## One-Sentence Test Purpose

This test family checks whether the implementation correctly handles three distinct `VkDescriptorSetLayout` lifecycle and update behaviors: deferred layout lifetime after pipeline-layout creation, creation of legally empty layouts (including the push-descriptor variant), and writes to `vkUpdateDescriptorSets` that span multiple bindings when the destination binding runs out of array elements.

## Background Knowledge

### Descriptor set layout is captured at pipeline-layout creation time

The Vulkan spec lets `vkCreatePipelineLayout` consume one or more `VkDescriptorSetLayout` handles and bake their content into the resulting `VkPipelineLayout`. After `vkCreatePipelineLayout` returns, the descriptor set layout objects are no longer referenced by the pipeline layout and may be destroyed. Drivers must not hold onto the descriptor set layout handle or require it to remain alive when a pipeline is later created against that pipeline layout. This is the property exercised by the `descriptor_set_layout_lifetime` intermediate node.

Why it matters here:
- The test deliberately destroys the descriptor set layout after creating the pipeline layout and then creates and executes a pipeline, so a driver that secretly retained the layout would still pass, while a driver that re-reads the layout during pipeline creation would fail.
- Because the test uses a no-op vertex or compute shader and checks only that the pipeline-creation and submit calls succeed without returning an error, the failure mode is a validation or runtime error, not a wrong-pixel result.

### Empty descriptor set layouts are a legal edge case

`VkDescriptorSetLayoutCreateInfo` allows `bindingCount = 0` and `pBindings = nullptr`. Such a layout has no bindings but is still a valid object that can be used to allocate descriptor sets, create pipeline layouts, or — when the `VK_DESCRIPTOR_SET_LAYOUT_CREATE_PUSH_DESCRIPTOR_BIT_KHR` flag from `VK_KHR_push_descriptor` is set — be the target of push-descriptor updates. Why it matters here:
- The `descriptor_set_layout.empty_set` cases verify that the implementation accepts this edge-case `VkDescriptorSetLayoutCreateInfo` both with flags=0 and with the push-descriptor flag.
- The push-descriptor variant additionally requires the device to support `VK_KHR_push_descriptor`, which the test gates through `context.requireDeviceFunctionality`.

### `vkUpdateDescriptorSets` writes can spill into subsequent bindings

When a `VkWriteDescriptorSet` targets `dstBinding` with `dstArrayElement` and `descriptorCount`, the spec allows the write to span more than one binding if the destination binding's array runs out of elements. Concretely: if `dstBinding` has fewer than `descriptorCount` array elements remaining starting from `dstArrayElement`, the surplus writes continue into the next binding (and beyond) as long as each subsequent binding has the same `descriptorType` and the descriptor type is compatible. Why it matters here:
- The `update_subsequent_binding` test case writes 3 `VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER` descriptors into a layout where binding 0 has 2 array elements and binding 1 has 1 array element of the same type, so 2 writes fill binding 0 and the 3rd write fills the single element of binding 1.
- A separate write then puts one `VK_DESCRIPTOR_TYPE_STORAGE_BUFFER` descriptor into binding 2. A compute shader reads all three uniform buffer elements and copies the source value (5) into a storage buffer; pass requires all three result slots to equal 5.

## One Concrete Example

The `update_subsequent_binding` case is the clearest example. Reconstructed from the CTS setup:

```c
// Layout: binding 0 = UNIFORM_BUFFER x2, binding 1 = UNIFORM_BUFFER x1, binding 2 = STORAGE_BUFFER x1
const VkDescriptorSetLayoutBinding layoutBindings[] = {
    {0, VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER, 2u, VK_SHADER_STAGE_ALL, nullptr},
    {1, VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER, 1u, VK_SHADER_STAGE_ALL, nullptr},
    {2, VK_DESCRIPTOR_TYPE_STORAGE_BUFFER, 1u, VK_SHADER_STAGE_ALL, nullptr},
};

// One write that fills binding 0 (2 elements) and spills into binding 1 (1 element).
const VkWriteDescriptorSet descriptorWrite = {
    VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET, nullptr,
    descriptorSet,
    0u,                           // dstBinding
    0u,                           // dstArrayElement
    3u,                           // descriptorCount  -> exceeds 2 elements in binding 0
    VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER,
    nullptr, descriptorBufferInfos, nullptr,
};

// Separate write for the storage buffer in binding 2.
const VkWriteDescriptorSet descriptorWriteResult = {
    VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET, nullptr,
    descriptorSet,
    2u,                           // dstBinding
    0u,                           // dstArrayElement
    1u,                           // descriptorCount
    VK_DESCRIPTOR_TYPE_STORAGE_BUFFER,
    nullptr, &descriptorBufferInfoResult, nullptr,
};
```

The bound uniform buffer contains `5`. The compute shader copies each of the three uniform buffer slots into a separate slot of a storage buffer. If the implementation routes the writes the way the spec requires, all three storage buffer slots read back as `5`.

## End-to-End Test Flow

```text
[host] choose the intermediate node (lifetime, empty_set, or binding order)
[host] create VkDescriptorSetLayout with the chosen flags and bindings
[host] for lifetime cases: create VkPipelineLayout from the layout, then destroy the layout
[host] for binding-order cases: allocate a descriptor set and issue VkWriteDescriptorSet calls
[host] for graphics/compute lifetime and binding-order cases: build shader modules and a pipeline
[host] submit a command buffer that begins a render pass and draws (graphics) or dispatches (compute)
[device] execute the no-op or copy shader
[host] wait for the queue, optionally invalidate and read back the result buffer
[host] pass if creation/submit succeeded and, for binding-order, all three result slots equal 5
```

The empty-set cases stop after `vkCreateDescriptorSetLayout` succeeds; there is no draw, dispatch, or readback.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- Inline GLSL vertex shader for `descriptor_set_layout_lifetime.graphics` ([source](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L559-L566)) — sets `gl_Position` to a constant and does nothing else.
- Inline GLSL compute shader for `descriptor_set_layout_lifetime.compute` ([source](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L568-L576)) — empty `main`, used only so a compute pipeline can be created and dispatched.
- Inline GLSL compute shader for `descriptor_set_layout_binding.update_subsequent_binding` ([source](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L578-L601)) — declares `uniformbufferarray[2]` at binding 0, `uniformbuffer2` at binding 1, and a `StorageBuffer` at binding 2; copies each uniform buffer element into a separate storage buffer slot.
- Amber script for `descriptor_set_layout_binding.layout_binding_order`, loaded from the data directory `api/descriptor_set/descriptor_set_layout_binding/layout_binding_order.amber` ([source](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L645-L650)). The Amber file itself is fetched by the CTS source-fetch step and is not present in this repository's working tree.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `VkDescriptorSetLayout` for the lifetime case | yes | no (consumed at pipeline-layout creation) | no | no | Destroyed before pipeline creation; its survival is what the test verifies. |
| `VkPipelineLayout` for the lifetime case | yes | yes (used by the pipeline) | no | no | Holds the baked-in descriptor set layout state after the source layout is destroyed. |
| `VkPipeline` (graphics or compute) | yes | yes | no (no-op shader) | no | Its successful creation after layout destruction is the lifetime check. |
| `VkDescriptorSetLayout` for the empty-set cases | yes | no | no | no | Object whose creation is the test; never used for binding. |
| Uniform buffer for `update_subsequent_binding` | yes (host writes `5`) | yes | read by compute shader | no | Source value copied into each result slot. |
| Storage buffer for `update_subsequent_binding` | yes | yes | written by compute shader | yes | Holds the three result values that the host compares. |

## What Is Checked

- `descriptor_set_layout_lifetime.graphics` and `descriptor_set_layout_lifetime.compute`: the test passes if `vkCreateGraphicsPipelines` / `vkCreateComputePipelines` and the subsequent `vkQueueSubmit` succeed without returning an error or surfacing a validation error. There is no shader-observed value to check; the shader is a no-op. The lifetime property is verified implicitly by successful pipeline creation and execution after the descriptor set layout has been destroyed.
- `descriptor_set_layout.empty_set.normal`: passes if `vkCreateDescriptorSetLayout` succeeds with `bindingCount = 0`, `pBindings = nullptr`, and flags = 0.
- `descriptor_set_layout.empty_set.push_descriptor`: passes if `vkCreateDescriptorSetLayout` succeeds with the same parameters plus `VK_DESCRIPTOR_SET_LAYOUT_CREATE_PUSH_DESCRIPTOR_BIT_KHR`. The test gates on `VK_KHR_push_descriptor` support first.
- `descriptor_set_layout_binding.update_subsequent_binding`: passes if, after the two `vkUpdateDescriptorSets` calls and a compute dispatch, `resultPtr[0] == 5 && resultPtr[1] == 5 && resultPtr[2] == 5`. All three uniform buffer reads must observe the source value of `5`.
- `descriptor_set_layout_binding.layout_binding_order`: passes whatever the Amber script asserts. The Amber file is not in the working tree; the C++ source's only documentation of intent is the test name and the registered description string `"Test descriptor set layout binding order"`.

## Behavior Parameter Identification

> **Behavior parameter:** intermediate node directly below `descriptor_set` (the registered dimension that controls what is being tested)
>
> **Candidate values:** `descriptor_set_layout_lifetime`, `descriptor_set_layout`, `descriptor_set_layout_binding`

Each value of this axis exercises a different descriptor-set property: lifetime after pipeline-layout creation, legal empty-layout creation, and binding-order semantics in `vkUpdateDescriptorSets`. Within `descriptor_set_layout_binding`, the two test case leaves split the same concept into a host-side functional check (`update_subsequent_binding`) and a declarative Amber check (`layout_binding_order`).

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `descriptor_set_layout_lifetime` | Driver or validation layers incorrectly require the `VkDescriptorSetLayout` to remain alive after `VkPipelineLayout` creation, or pipeline creation/execution fails because the layout was destroyed. |
| `descriptor_set_layout` | `vkCreateDescriptorSetLayout` rejects a legally empty `VkDescriptorSetLayoutCreateInfo`, or rejects the `VK_DESCRIPTOR_SET_LAYOUT_CREATE_PUSH_DESCRIPTOR_BIT_KHR` flag on a device that advertises `VK_KHR_push_descriptor`. |
| `descriptor_set_layout_binding` | `vkUpdateDescriptorSets` does not spill writes into the next binding when the destination binding runs out of array elements, or the Amber-declared equivalent fails for the same reason. |

## Important Variations and Special Cases

- Vulkan SC pruning: the `push_descriptor` case and the Amber `layout_binding_order` case are both excluded from the Vulkan SC test set through `#ifndef CTS_USES_VULKANSC`, because `VK_KHR_push_descriptor` is not part of Vulkan SC. This is a requirement-based pruning rule, not a behavioral difference.
- Two pipeline types in the lifetime node: the `graphics` case uses a graphics pipeline with `rasterizerDiscardEnable = VK_TRUE` so that the vertex shader runs but no attachments are touched, while the `compute` case uses a compute pipeline that dispatches a no-op shader. The two cases share the same lifetime mechanism; they only differ in which pipeline-creation entry point they exercise.
- Single-write vs. two-write updates in the binding-order node: `update_subsequent_binding` issues one write that spans bindings 0 and 1, and a second write that targets binding 2 alone. The first write is the one that exercises the spill rule; the second write confirms that writes to a later binding still work after the spill.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| `createDescriptorSetTests` registration entry point | [vktApiDescriptorSetTests.cpp#L664-L672](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L664-L672) | Builds the `descriptor_set` group and adds the three intermediate nodes. |
| `createPipelineLayoutDestroyDescriptorSetLayout` | [vktApiDescriptorSetTests.cpp#L50-L67](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L50-L67) | The shared lifetime mechanism: creates the pipeline layout, then releases the descriptor set layout. |
| `descriptorSetLayoutLifetimeGraphicsTest` | [vktApiDescriptorSetTests.cpp#L69-L226](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L69-L226) | Graphics lifetime path; creates a render pass, pipeline, framebuffer, and submits a draw. |
| `descriptorSetLayoutLifetimeComputeTest` | [vktApiDescriptorSetTests.cpp#L228-L306](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L228-L306) | Compute lifetime path; dispatches a no-op shader. |
| `emptyDescriptorSetLayoutTest` | [vktApiDescriptorSetTests.cpp#L308-L332](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L308-L332) | Empty-layout creation entry; takes the create flags as a parameter. |
| `descriptorSetLayoutBindingOrderingTest` | [vktApiDescriptorSetTests.cpp#L334-L556](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L334-L556) | The functional binding-order test; issues the spill write and reads back three result slots. |
| Shader sources | [vktApiDescriptorSetTests.cpp#L559-L601](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L559-L601) | Inline GLSL for the three shader-bearing cases. |
| Amber case registration | [vktApiDescriptorSetTests.cpp#L645-L650](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L645-L650) | Registers `layout_binding_order` from the `api/descriptor_set/descriptor_set_layout_binding` data directory. |
| Parent registration in `createApiTests` | [vktApiTests.cpp#L120-L120](../../../modules/vulkan/api/vktApiTests.cpp#L120-L120) | Adds `createDescriptorSetTests` under the `api` test category. |
| Mustpass entries | [api.txt](../../../mustpass/main/vk-default/api.txt) | Lists the six registered test case leaves under `dEQP-VK.api.descriptor_set.*`. |

## Questions / Risk Points for User Audit

- Is the behavior parameter axis correct? The three direct intermediate nodes (`descriptor_set_layout_lifetime`, `descriptor_set_layout`, `descriptor_set_layout_binding`) read as the natural primary axis because each tests a different descriptor-set property. If you prefer a different axis (for example, treating test case leaves as the axis), the failure cause mapping will need to be re-shaped.
- The Amber file `layout_binding_order.amber` is not present in the repository working tree. The C++ source registers it but does not document its exact assertions. The brief assumes it tests the same binding-order spill rule as `update_subsequent_binding`; this should be confirmed against the Amber file when it is available. If the Amber script asserts something different, the `descriptor_set_layout_binding` row of the failure cause mapping should be adjusted.
- The lifetime cases return `tcu::TestStatus::pass("Pass")` unconditionally after `submitCommandsAndWait`. They rely on `VK_CHECK`-style helpers inside the create/submit wrappers to convert Vulkan errors into test failures. Is this the expected pass/fail behavior, or should the test also catch validation-layer messages?
- The graphics lifetime case uses `rasterizerDiscardEnable = VK_TRUE` and a framebuffer with no attachments; is the framebuffer/renderpass setup worth calling out in the final page, or is it incidental to the lifetime property being tested?

## Conversion Notes for Final Wiki Rewrite

- Distill `Descriptor set layout is captured at pipeline-layout creation time` into one Background Knowledge bullet about pipeline-layout baking plus the consequence that the source layout may be destroyed afterward.
- Distill `Empty descriptor set layouts are a legal edge case` into one Background Knowledge bullet; do not duplicate the empty-set test setup.
- Distill `vkUpdateDescriptorSets writes can spill into subsequent bindings` into one Background Knowledge bullet covering the spill rule.
- Keep the concrete code example for `update_subsequent_binding` as the most efficient way to show the spill rule, but shorten it to the layout bindings plus the first spill write.
- The `### Failure Cause Mapping` table above will be copied directly into the final page's `### Failure Cause Mapping`.
- The behavior parameter axis (intermediate node directly below `descriptor_set`) will be carried into the final page's `## Behavior Parameters` with one `###` subsection per value.
- `### Cause Analysis` will be written fresh during the rewrite; do not copy the brief's per-cause prose verbatim.
- Move the source-link table to the Source Reference Appendix with the same row labels.
