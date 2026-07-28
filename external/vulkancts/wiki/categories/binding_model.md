## Overview

The `binding_model` test category collects tests that check how Vulkan applications describe, update, bind, and access shader resources through descriptor sets, descriptor buffers, descriptor heaps, physical addresses, and pipeline state.

## Background Knowledge

- **Descriptor interfaces and pipeline layouts.** A shader resource declaration identifies a descriptor set and binding, while the descriptor-set layout supplies its type, count, and stage visibility. A pipeline layout combines the set layouts and connects that interface to a pipeline. Descriptor buffers and descriptor heaps use different storage and mapping mechanisms, but their test pages still explain how shader declarations reach the selected resource ([descriptor-set layouts](../../../vulkan-docs/src/chapters/descriptorsets.adoc#L435-L469), [pipeline layouts](../../../vulkan-docs/src/chapters/descriptorsets.adoc#L1168-L1182)).
- **Descriptor writes, copies, and active state.** Descriptor writes populate a destination binding, while descriptor copies transfer descriptor state from a source range without copying the referenced resource. Update-after-bind, inline uniform blocks, acceleration-structure writes, and mutable descriptors add rules for when a binding may change and which source members or active types define its contents ([descriptor set updates](../../../vulkan-docs/src/chapters/descriptorsets.adoc#L2900-L2951)).
- **Descriptor validity and dynamic use.** A descriptor that a shader dynamically accesses must contain a defined, type-compatible resource. Partially bound bindings relax that requirement only for elements that no invocation dynamically uses. Static shader use, dynamic execution, binding compatibility, and descriptor contents therefore describe different parts of the validity contract ([descriptor validity](../../../vulkan-docs/src/chapters/descriptorsets.adoc#L4583-L4619), [static use](../../../vulkan-docs/src/chapters/shaders.adoc#shaders-staticuse)).
- **Availability, visibility, and observation.** Queue execution order does not by itself make a write visible to a later access. Memory dependencies establish availability and visibility for descriptor data, referenced resources, shader results, and host readback. The Level-3 pages apply this shared model to their own command paths and result checks ([memory dependencies](../../../vulkan-docs/src/chapters/synchronization.adoc#L110-L182)).

## Category Structure

```text
binding_model
├── shader_access
├── descriptor_update
├── descriptorset_random
├── descriptor_copy
├── buffer_device_address
├── dynamic_offset
├── mutable_descriptor
├── descriptor_buffer
├── descriptor_combination
├── push_constant_bank
├── descriptor_heap
├── stages
├── inline_uniform_blocks
└── unused_invalid_descriptor
```

The `acceleration_structure` intermediate node belongs to `descriptor_update`; it is not a direct child of the category. The other entries are direct test families registered by the category dispatcher.

## How the Families Fit Together

The families share a shader-visible resource-binding problem but vary the storage model, update operation, address calculation, or pipeline state that selects the resource.

- **When** the question concerns descriptor-set layout and command-buffer binding, use `ShaderAccess`, `DescriptorSetRandom`, `DescriptorUpdate`, `DescriptorCopy`, `DynamicOffset`, or `Stages`.
- **Which bytes** the shader receives changes in `DescriptorInlineUniform`, `DescriptorBuffer`, `Mutable`, and `DescriptorHeap`, where byte-addressed data, encoded descriptors, active types, or heap mappings add another layer.
- **Which fields** the shader or host uses changes in `DescriptorUpdateAS`, `BufferDeviceAddress`, `PushConstantBank`, and `DescriptorCombination`, which combine resource binding with traversal, pointer arithmetic, decorated push storage, or multiple descriptor state mechanisms.
- `UnusedInvalidDescriptor` isolates validity rules for descriptors that are unused, copied, partially bound, destroyed, or dynamically accessed.

## Level-3 Pages Navigation

| Registered test family or area | Level-3 page | What to read there |
|--------------------------------|--------------|--------------------|
| `shader_access` | [ShaderAccess.md](../testfiles/binding_model/ShaderAccess.md) | Descriptor declarations, update methods, command-buffer paths, and shader-visible results. |
| `descriptor_update` | [DescriptorUpdate.md](../testfiles/binding_model/DescriptorUpdate.md) | Empty bindings, samplerless image updates, and randomized descriptor writes. |
| `descriptor_update.acceleration_structure` | [DescriptorUpdateAS.md](../testfiles/binding_model/DescriptorUpdateAS.md) | Acceleration-structure writes through ray queries and ray-tracing pipelines. |
| `descriptorset_random` | [DescriptorSetRandom.md](../testfiles/binding_model/DescriptorSetRandom.md) | Generated layouts, descriptor indexing, update-after-bind, and deterministic shader checks. |
| `descriptor_copy` | [DescriptorCopy.md](../testfiles/binding_model/DescriptorCopy.md) | Host-side descriptor copies across compute, graphics, update-after-bind, and immutable-sampler cases. |
| `buffer_device_address` | [BufferDeviceAddress.md](../testfiles/binding_model/BufferDeviceAddress.md) | Physical storage buffer pointers, address capture replay, layouts, and access chains. |
| `dynamic_offset` | [DynamicOffset.md](../testfiles/binding_model/DynamicOffset.md) | Dynamic buffer offsets, compatible pipeline layouts, push-constant ordering, and result buffers. |
| `mutable_descriptor` | [Mutable.md](../testfiles/binding_model/Mutable.md) | Active descriptor types, mutable arrays, aliasing, indexing, and feature-based pruning. |
| `descriptor_buffer` | [DescriptorBuffer.md](../testfiles/binding_model/DescriptorBuffer.md) | Encoded descriptor bytes, address and offset calculation, sparse modes, and visibility. |
| `descriptor_combination` | [DescriptorCombination.md](../testfiles/binding_model/DescriptorCombination.md) | Legacy and descriptor-buffer state interaction plus sampler capture replay. |
| `push_constant_bank` | [PushConstantBank.md](../testfiles/binding_model/PushConstantBank.md) | Bank and member placement for ordinary push constants and descriptor-heap push data. |
| `descriptor_heap` | [DescriptorHeap.md](../testfiles/binding_model/DescriptorHeap.md) | Heap mappings, direct heap access, state lifetime, queue use, and graphics or compute integration. |
| `stages` | [Stages.md](../testfiles/binding_model/Stages.md) | Descriptor binding from multiple pipeline bind points and stage-specific observations. |
| `inline_uniform_blocks` | [DescriptorInlineUniform.md](../testfiles/binding_model/DescriptorInlineUniform.md) | Byte-addressed inline uniform writes, copies, shader representation, and readback. |
| `unused_invalid_descriptor` | [UnusedInvalidDescriptor.md](../testfiles/binding_model/UnusedInvalidDescriptor.md) | Static use, dynamic use, partial binding, undefined descriptors, and actual access. |

## Category Notes

The category dispatcher, [`vktBindingModelTests.cpp`](../../modules/vulkan/binding_model/vktBindingModelTests.cpp), registers five direct families outside the `CTS_USES_VULKANSC` guard and the remaining nine only for Vulkan ([`createChildren()`](../../modules/vulkan/binding_model/vktBindingModelTests.cpp#L52-L71)). The nested `descriptor_update.acceleration_structure` branch is also Vulkan-only ([nested registration](../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L1909-L1917)). The dispatcher has no separate technical page, so this page records its root routing and availability. [`binding-model.txt`](../../mustpass/main/vk-default/binding-model.txt) lists the default Vulkan leaves.
