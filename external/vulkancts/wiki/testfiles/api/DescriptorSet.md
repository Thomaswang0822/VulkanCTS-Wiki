## Overview

**Core question:** does the implementation correctly handle `VkDescriptorSetLayout` lifetime, legally empty layouts, and `vkUpdateDescriptorSets` writes that span multiple bindings?

The `api.descriptor_set` test family is implemented in [vktApiDescriptorSetTests.cpp](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L1) and registered under the `api` test category by [`createApiTests`](../../../modules/vulkan/api/vktApiTests.cpp#L120-L120). It exercises three descriptor-set behaviors through three intermediate nodes:

- deferred `VkDescriptorSetLayout` lifetime after `VkPipelineLayout` creation;
- creation of legally empty descriptor set layouts, including the push-descriptor variant;
- `vkUpdateDescriptorSets` writes that spill into the next binding when the destination binding runs out of array elements.

The page covers what each intermediate node verifies, how the host-side setup and result checking work, what failure of each node means, and which cases are pruned for Vulkan SC.

## Background Knowledge

- **Pipeline layouts bake descriptor set layout state at creation time.** `vkCreatePipelineLayout` consumes one or more `VkDescriptorSetLayout` handles and copies their content into the resulting `VkPipelineLayout`. After that call returns, the descriptor set layout objects are no longer referenced by the pipeline layout and may be destroyed. A driver must not require the layout to remain alive when a pipeline is later created against the same pipeline layout.
- **Empty descriptor set layouts are a legal edge case.** `VkDescriptorSetLayoutCreateInfo` allows `bindingCount = 0` and `pBindings = nullptr`. The resulting layout is a valid object that can be used to allocate descriptor sets, create pipeline layouts, or be the target of push-descriptor updates when `VK_DESCRIPTOR_SET_LAYOUT_CREATE_PUSH_DESCRIPTOR_BIT_KHR` is set. The push-descriptor flag requires the `VK_KHR_push_descriptor` extension.
- **`vkUpdateDescriptorSets` writes can span multiple bindings.** When a `VkWriteDescriptorSet` targets `dstBinding` with `dstArrayElement` and `descriptorCount`, and the destination binding has fewer than `descriptorCount` array elements remaining starting from `dstArrayElement`, the surplus writes continue into the next binding as long as each subsequent binding has the same `descriptorType` and the descriptor type is compatible.

## Registration Hierarchy

```text
api.descriptor_set
├── descriptor_set_layout_lifetime
├── descriptor_set_layout
└── descriptor_set_layout_binding
```

The `descriptor_set` test family is built by [`createDescriptorSetTests`](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L664-L672). The three direct intermediate nodes are registered by `createDescriptorSetLayoutLifetimeTests`, `createDescriptorSetLayoutTests`, and `createDescriptorSetLayoutBindingOrderingTests`. The six executable test case leaves under this family are listed in [`api.txt`](../../../mustpass/main/vk-default/api.txt).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Intermediate node | `descriptor_set_layout_lifetime`, `descriptor_set_layout`, `descriptor_set_layout_binding` | Selects the descriptor-set property under test: deferred lifetime, empty-layout creation, or binding-order spill. | [vktApiDescriptorSetTests.cpp#L666-L670](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L666-L670) |
| Lifetime pipeline type | `graphics`, `compute` | Selects which pipeline-creation entry point exercises the lifetime property. The two leaves share the same lifetime mechanism. | [vktApiDescriptorSetTests.cpp#L610-L615](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L610-L615) |
| Empty-layout flags | `0`, `VK_DESCRIPTOR_SET_LAYOUT_CREATE_PUSH_DESCRIPTOR_BIT_KHR` | Selects whether the empty layout is a normal layout or a push-descriptor layout. | [vktApiDescriptorSetTests.cpp#L626-L632](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L626-L632) |
| Binding-order case | `update_subsequent_binding`, `layout_binding_order` | Splits the binding-order concept into a host-side functional check and a declarative Amber check. | [vktApiDescriptorSetTests.cpp#L642-L649](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L642-L649) |

## Behavior Parameters

The primary behavioral axis is the intermediate node directly below `descriptor_set`. Each value tests a different descriptor-set property.

### `descriptor_set_layout_lifetime` — deferred layout lifetime after pipeline-layout creation

Both test case leaves in this node share the helper [`createPipelineLayoutDestroyDescriptorSetLayout`](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L50-L67). That helper creates a `VkDescriptorSetLayout`, uses it to build a `VkPipelineLayout`, and then releases the source layout through a `Unique<VkDescriptorSetLayout>` when the helper returns. The test then creates a pipeline against the surviving pipeline layout and submits a no-op draw or dispatch.

The `graphics` leaf creates a graphics pipeline with `rasterizerDiscardEnable = VK_TRUE` and a render pass with no attachments, then issues a 3-vertex draw. The `compute` leaf creates a compute pipeline, binds a descriptor set, and dispatches a 1×1×1 workgroup. Both shaders are no-ops; the tested property is that pipeline creation and submit succeed after the source descriptor set layout has been destroyed.

### `descriptor_set_layout` — legally empty descriptor set layout creation

This node has a single registered child, `empty_set`, which contains two test case leaves. Both call [`emptyDescriptorSetLayoutTest`](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L308-L332) with a `VkDescriptorSetLayoutCreateInfo` whose `bindingCount = 0` and `pBindings = nullptr`.

The `normal` leaf passes flags = 0. The `push_descriptor` leaf passes `VK_DESCRIPTOR_SET_LAYOUT_CREATE_PUSH_DESCRIPTOR_BIT_KHR` and first gates on `VK_KHR_push_descriptor` device support through `context.requireDeviceFunctionality`. The tested property is that `vkCreateDescriptorSetLayout` accepts both create-info variants on hardware that advertises the relevant extension.

### `descriptor_set_layout_binding` — binding-order spill in `vkUpdateDescriptorSets`

This node contains two test case leaves. The `update_subsequent_binding` leaf is the functional check. It builds a layout with three bindings: binding 0 holds two `VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER` descriptors, binding 1 holds one `VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER` descriptor, and binding 2 holds one `VK_DESCRIPTOR_TYPE_STORAGE_BUFFER` descriptor. It then issues a single `VkWriteDescriptorSet` with `dstBinding = 0`, `dstArrayElement = 0`, `descriptorCount = 3`. The first two writes fill binding 0; the third spills into binding 1 because the bindings have the same descriptor type. A second write puts one storage buffer descriptor into binding 2. A compute shader copies the source value of `5` from each of the three uniform buffer slots into a storage buffer; the test passes only when all three result slots equal `5`.

The `layout_binding_order` leaf is an Amber-driven case loaded from the data directory `api/descriptor_set/descriptor_set_layout_binding`. The C++ source registers it with the description string `"Test descriptor set layout binding order"`. The Amber script itself is not present in this repository's working tree; it is fetched by the CTS source-fetch step. The functional `update_subsequent_binding` leaf is the source-grounded description of the binding-order behavior tested by this node.

## Shader Analysis

No `shader-analyzer` walkthrough is produced for this page. The shaders used by the lifetime cases are no-op vertex and compute shaders whose only role is to make `vkCreateGraphicsPipelines` / `vkCreateComputePipelines` and a subsequent submit legal. The shader used by `update_subsequent_binding` is a trivial copy shader that reads three uniform buffer elements and writes them into a storage buffer; its behavior is fully described by the test logic in [`descriptorSetLayoutBindingOrderingTest`](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L334-L556) and by the inline GLSL in [`createDescriptorSetLayoutBindingOrderingSource`](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L578-L601). The test core is host-side descriptor set behavior, not shader behavior.

## Runtime Execution and Result Checking

- In the lifetime cases, the host builds a descriptor set layout, uses it to create a pipeline layout, releases the layout, then creates a graphics or compute pipeline and submits a command buffer that draws or dispatches. Pass is returned unconditionally after `submitCommandsAndWait` returns; Vulkan errors from `vkCreate*Pipelines` or `vkQueueSubmit` are converted into test failures by the CTS `VK_CHECK` helpers used by the create and submit wrappers, so a returned error surfaces as a test failure rather than as a silent pass.
- In the empty-layout cases, the host calls `vkCreateDescriptorSetLayout` with `bindingCount = 0` and the chosen flags. Pass is returned unconditionally after `createDescriptorSetLayout` returns; `VK_CHECK` inside the wrapper converts a non-`VK_SUCCESS` return into a test failure.
- For `update_subsequent_binding`, the host creates the descriptor set layout and pool, allocates a descriptor set, issues the two `vkUpdateDescriptorSets` calls, builds and dispatches a compute pipeline, then invalidates the result allocation and reads three `uint32_t` slots. Pass requires `resultPtr[0] == 5 && resultPtr[1] == 5 && resultPtr[2] == 5`; any other value produces `tcu::TestStatus::fail("Fail")`.
- For `layout_binding_order`, the host loads and runs the Amber script. Pass and fail are decided by the Amber harness based on the assertions in `layout_binding_order.amber`.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `descriptor_set_layout_lifetime` | Driver or validation layers incorrectly require the `VkDescriptorSetLayout` to remain alive after `VkPipelineLayout` creation, or pipeline creation/execution fails because the layout was destroyed. |
| `descriptor_set_layout` | `vkCreateDescriptorSetLayout` rejects a legally empty `VkDescriptorSetLayoutCreateInfo`, or rejects the `VK_DESCRIPTOR_SET_LAYOUT_CREATE_PUSH_DESCRIPTOR_BIT_KHR` flag on a device that advertises `VK_KHR_push_descriptor`. |
| `descriptor_set_layout_binding` | `vkUpdateDescriptorSets` does not spill writes into the next binding when the destination binding runs out of array elements, or the Amber-declared equivalent fails for the same reason. |

### Cause Analysis

#### `descriptor_set_layout_lifetime` failures

**Possible failure symptoms:** `vkCreateGraphicsPipelines` or `vkCreateComputePipelines` returns a non-`VK_SUCCESS` result, or `vkQueueSubmit` fails, or the validation layers report an error referencing the destroyed descriptor set layout. The test reports fail through the `VK_CHECK` path inside the CTS create and submit wrappers.

**Possible implementation causes:** the driver captures the `VkDescriptorSetLayout` handle rather than copying its content at `vkCreatePipelineLayout` time and then dereferences the destroyed handle during pipeline creation; the validation layers incorrectly flag the destroyed layout as a use-after-free; or the driver depends on a host-side mirror of the layout that was de-allocated when the layout was destroyed. Per Vulkan spec, the descriptor set layout state is baked into the pipeline layout at creation time and the source handle may be destroyed afterward, so any of these would be a conformance bug.

#### `descriptor_set_layout` failures

**Possible failure symptoms:** `vkCreateDescriptorSetLayout` returns a non-`VK_SUCCESS` result for a `VkDescriptorSetLayoutCreateInfo` with `bindingCount = 0`, or returns an error specifically for the `VK_DESCRIPTOR_SET_LAYOUT_CREATE_PUSH_DESCRIPTOR_BIT_KHR` flag on a device that advertises `VK_KHR_push_descriptor`. The `VK_CHECK` inside `createDescriptorSetLayout` surfaces this as a test failure.

**Possible implementation causes:** the driver rejects the empty-binding edge case in its create-info validation, or the push-descriptor flag path is gated on the wrong extension query. For the `push_descriptor` case the test first calls `context.requireDeviceFunctionality("VK_KHR_push_descriptor")`, so a failure on a device that does not advertise the extension is a test skip rather than a test failure; an actual fail means the extension is advertised but the flag is rejected.

#### `descriptor_set_layout_binding` failures

**Possible failure symptoms:** for `update_subsequent_binding`, the host reads back result slots that do not all equal `5`. At least one of the three uniform buffer reads observed a value other than `5`, which means at least one of the three descriptors was not bound to the source buffer as expected. The test reports `tcu::TestStatus::fail("Fail")` after the comparison.

**Possible implementation causes:** `vkUpdateDescriptorSets` did not spill the third `VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER` write into binding 1 when binding 0 ran out of array elements, so binding 1's descriptor was left unbound or pointed at a stale resource; the binding-order spill rule was applied across incompatible descriptor types when it should not have been; or the descriptor write was silently truncated to the first binding. Source-level investigation of the driver's update-descriptor path is needed to confirm which of these applies. For the Amber-driven `layout_binding_order` case, the symptom and cause depend on the assertions in `layout_binding_order.amber`, which is not present in this repository's working tree; the C++ source's description string `"Test descriptor set layout binding order"` is the only on-tree documentation of its intent.

## Case Pruning

### Requirement-based pruning

- `descriptor_set_layout.empty_set.push_descriptor` is excluded from the Vulkan SC test set by [`#ifndef CTS_USES_VULKANSC`](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L628-L633) because `VK_KHR_push_descriptor` is not part of Vulkan SC.
- `descriptor_set_layout_binding.layout_binding_order` is excluded from the Vulkan SC test set by [`#ifndef CTS_USES_VULKANSC`](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L645-L650) for the same reason: the Amber case targets a behavior that depends on extension support that is not in Vulkan SC.
- The `push_descriptor` leaf additionally self-skips at runtime through `context.requireDeviceFunctionality("VK_KHR_push_descriptor")` if the device does not advertise the extension.

### Design-based pruning

- The lifetime node does not generate a separate leaf for each pipeline bind point; only `graphics` and `compute` are registered because they cover the two pipeline-creation entry points that the lifetime property exercises. Other bind points (ray tracing, mesh) are out of scope for this test family.
- The empty-set node does not generate leaves that allocate descriptor sets or create pipeline layouts from the empty layout. The node's scope is `vkCreateDescriptorSetLayout` acceptance only.
- The binding-order node exercises one specific spill pattern (a single write that spans two `VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER` bindings) and one storage-buffer write into a separate binding. Other spill patterns, such as writes that span three or more bindings or that mix descriptor types, are out of scope.

## Key Takeaways

- The `descriptor_set` test family covers three distinct descriptor-set properties, one per intermediate node: deferred layout lifetime after pipeline-layout creation, legally empty layout creation, and binding-order spill in `vkUpdateDescriptorSets`.
- The lifetime cases rely on `VK_CHECK` inside the CTS create and submit wrappers to convert Vulkan errors into test failures; they do not inspect a shader-observed value.
- The `update_subsequent_binding` case is the only leaf in this family that reads back a shader-written result. Its pass condition `resultPtr[0] == 5 && resultPtr[1] == 5 && resultPtr[2] == 5` directly verifies that the spill write reached binding 1 after filling binding 0.
- Two test case leaves (`push_descriptor` and `layout_binding_order`) are pruned for Vulkan SC because they depend on `VK_KHR_push_descriptor` or behavior that Vulkan SC does not include.
- See `## Failure Meaning` for the cause analysis behind each behavior parameter value's failure.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `createDescriptorSetTests` registration | [vktApiDescriptorSetTests.cpp#L664-L672](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L664-L672) | Builds the `descriptor_set` test family and adds the three intermediate nodes. |
| Parent registration in `createApiTests` | [vktApiTests.cpp#L120-L120](../../../modules/vulkan/api/vktApiTests.cpp#L120-L120) | Adds `createDescriptorSetTests` under the `api` test category. |
| `createPipelineLayoutDestroyDescriptorSetLayout` | [vktApiDescriptorSetTests.cpp#L50-L67](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L50-L67) | Shared lifetime helper: creates the pipeline layout, then releases the descriptor set layout. |
| `descriptorSetLayoutLifetimeGraphicsTest` | [vktApiDescriptorSetTests.cpp#L69-L226](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L69-L226) | Graphics lifetime path: creates a render pass, graphics pipeline, framebuffer, and submits a draw. |
| `descriptorSetLayoutLifetimeComputeTest` | [vktApiDescriptorSetTests.cpp#L228-L306](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L228-L306) | Compute lifetime path: builds a compute pipeline and dispatches a no-op shader. |
| `emptyDescriptorSetLayoutTest` | [vktApiDescriptorSetTests.cpp#L308-L332](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L308-L332) | Empty-layout creation entry; takes the create flags as a parameter. |
| `descriptorSetLayoutBindingOrderingTest` | [vktApiDescriptorSetTests.cpp#L334-L556](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L334-L556) | Functional binding-order test: issues the spill write and compares three result slots. |
| Inline GLSL shader sources | [vktApiDescriptorSetTests.cpp#L559-L601](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L559-L601) | Vertex, compute, and binding-order shaders used by the three shader-bearing leaves. |
| Empty-set registration | [vktApiDescriptorSetTests.cpp#L620-L635](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L620-L635) | Registers `normal` and `push_descriptor` under `empty_set`; gates `push_descriptor` on Vulkan SC. |
| Binding-order registration | [vktApiDescriptorSetTests.cpp#L637-L653](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L637-L653) | Registers `update_subsequent_binding` and the Amber `layout_binding_order` case. |
| Mustpass entries | [api.txt](../../../mustpass/main/vk-default/api.txt) | Lists the six registered test case leaves under `dEQP-VK.api.descriptor_set.*`. |
