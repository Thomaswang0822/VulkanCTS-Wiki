# Binding Model Tests

The `binding_model` category documents Vulkan descriptor binding, descriptor updates/copies, descriptor buffers and heaps, mutable descriptors, dynamic offsets, buffer device addresses, inline uniform blocks, acceleration-structure descriptors, and related shader access behavior. The historical Vulkan API test plan gives useful high-level background for this category by identifying descriptor-set creation, shader resource access through varied layouts, descriptor updates, descriptor-set chaining, descriptor limits, and pipeline-layout corner cases as binding-model objectives ([`apitests.adoc`](../../../../doc/testspecs/VK/apitests.adoc#L278-L297)).

## Source

- **Root registration:** [`vktBindingModelTests.cpp`](../../modules/vulkan/binding_model/vktBindingModelTests.cpp)

## Registration Entry Point

The category factory is [`createTests()`](../../modules/vulkan/binding_model/vktBindingModelTests.cpp#L80), which delegates root children to [`createChildren()`](../../modules/vulkan/binding_model/vktBindingModelTests.cpp#L52). Top-level discovery was performed from the root include section: the root header and [`vktTestGroupUtil.hpp`](../../modules/vulkan/binding_model/vktBindingModelTests.cpp#L31) are excluded, and the remaining included headers map to registered source files. The direct child additions in [`createChildren()`](../../modules/vulkan/binding_model/vktBindingModelTests.cpp#L56) through [`vktBindingModelTests.cpp:70`](../../modules/vulkan/binding_model/vktBindingModelTests.cpp#L70) cross-check registration and `CTS_USES_VULKANSC` guards.

## Subgroup Structure

```
binding_model
├── shader_access                         (VK + VKSC)
├── descriptor_update                     (VK + VKSC)
│   └── acceleration_structure            (VK only, nested)
├── descriptorset_random                  (VK + VKSC, reduced VKSC stage set)
├── descriptor_copy                       (VK + VKSC)
├── buffer_device_address                 (VK + VKSC)
├── dynamic_offset                        (VK only)
├── mutable_descriptor                    (VK only)
├── descriptor_buffer                     (VK only)
├── descriptor_combination                (VK only)
├── push_constant_bank                    (VK only)
├── descriptor_heap                       (VK only)
├── stages                                (VK only)
├── inline_uniform_blocks                 (VK only)
└── unused_invalid_descriptor             (VK only)
```

## File Inventory

| Source file | Verified group | Availability | Level-3 doc |
|-------------|----------------|--------------|-------------|
| [`vktBindingShaderAccessTests.cpp`](../../modules/vulkan/binding_model/vktBindingShaderAccessTests.cpp) | `shader_access` | VK + VKSC | [vktBindingShaderAccessTests.md](../testfiles/binding_model/vktBindingShaderAccessTests.md) |
| [`vktBindingDescriptorUpdateTests.cpp`](../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp) | `descriptor_update` | VK + VKSC | [vktBindingDescriptorUpdateTests.md](../testfiles/binding_model/vktBindingDescriptorUpdateTests.md) |
| [`vktBindingDescriptorUpdateASTests.cpp`](../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp) | `descriptor_update → acceleration_structure` | VK only nested | [vktBindingDescriptorUpdateASTests.md](../testfiles/binding_model/vktBindingDescriptorUpdateASTests.md) |
| [`vktBindingDescriptorSetRandomTests.cpp`](../../modules/vulkan/binding_model/vktBindingDescriptorSetRandomTests.cpp) | `descriptorset_random` | VK + VKSC | [vktBindingDescriptorSetRandomTests.md](../testfiles/binding_model/vktBindingDescriptorSetRandomTests.md) |
| [`vktBindingDescriptorCopyTests.cpp`](../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp) | `descriptor_copy` | VK + VKSC | [vktBindingDescriptorCopyTests.md](../testfiles/binding_model/vktBindingDescriptorCopyTests.md) |
| [`vktBindingBufferDeviceAddressTests.cpp`](../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp) | `buffer_device_address` | VK + VKSC | [vktBindingBufferDeviceAddressTests.md](../testfiles/binding_model/vktBindingBufferDeviceAddressTests.md) |
| [`vktBindingDynamicOffsetTests.cpp`](../../modules/vulkan/binding_model/vktBindingDynamicOffsetTests.cpp) | `dynamic_offset` | VK only | [vktBindingDynamicOffsetTests.md](../testfiles/binding_model/vktBindingDynamicOffsetTests.md) |
| [`vktBindingMutableTests.cpp`](../../modules/vulkan/binding_model/vktBindingMutableTests.cpp) | `mutable_descriptor` | VK only | [vktBindingMutableTests.md](../testfiles/binding_model/vktBindingMutableTests.md) |
| [`vktBindingDescriptorBufferTests.cpp`](../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp) | `descriptor_buffer` | VK only | [vktBindingDescriptorBufferTests.md](../testfiles/binding_model/vktBindingDescriptorBufferTests.md) |
| [`vktBindingDescriptorCombinationTests.cpp`](../../modules/vulkan/binding_model/vktBindingDescriptorCombinationTests.cpp) | `descriptor_combination` | VK only | [vktBindingDescriptorCombinationTests.md](../testfiles/binding_model/vktBindingDescriptorCombinationTests.md) |
| [`vktBindingPushConstantBankTests.cpp`](../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp) | `push_constant_bank` | VK only | [vktBindingPushConstantBankTests.md](../testfiles/binding_model/vktBindingPushConstantBankTests.md) |
| [`vktBindingDescriptorHeapTests.cpp`](../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp) | `descriptor_heap` | VK only | [vktBindingDescriptorHeapTests.md](../testfiles/binding_model/vktBindingDescriptorHeapTests.md) |
| [`vktBindingStagesTests.cpp`](../../modules/vulkan/binding_model/vktBindingStagesTests.cpp) | `stages` | VK only | [vktBindingStagesTests.md](../testfiles/binding_model/vktBindingStagesTests.md) |
| [`vktBindingDescriptorInlineUniformTests.cpp`](../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp) | `inline_uniform_blocks` | VK only | [vktBindingDescriptorInlineUniformTests.md](../testfiles/binding_model/vktBindingDescriptorInlineUniformTests.md) |
| [`vktBindingUnusedInvalidDescriptorTests.cpp`](../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp) | `unused_invalid_descriptor` | VK only | [vktBindingUnusedInvalidDescriptorTests.md](../testfiles/binding_model/vktBindingUnusedInvalidDescriptorTests.md) |

## VK / VKSC Split

The root include section includes five groups outside the `CTS_USES_VULKANSC` guard: `shader_access`, `descriptor_update`, `descriptorset_random`, `descriptor_copy`, and `buffer_device_address` ([`vktBindingModelTests.cpp:26`](../../modules/vulkan/binding_model/vktBindingModelTests.cpp#L26)). Nine additional top-level groups are included and registered only when `CTS_USES_VULKANSC` is not defined ([`vktBindingModelTests.cpp:32`](../../modules/vulkan/binding_model/vktBindingModelTests.cpp#L32), [`vktBindingModelTests.cpp:61`](../../modules/vulkan/binding_model/vktBindingModelTests.cpp#L61)). The acceleration-structure descriptor-update file is also Vulkan-only, but it is nested under `descriptor_update` rather than registered by the category root ([`vktBindingDescriptorUpdateTests.cpp:1914`](../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L1914)).

## Cross-File Themes

| Theme | Representative files |
|-------|----------------------|
| Descriptor update and copy mechanics | [`vktBindingDescriptorUpdateTests.cpp`](../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp), [`vktBindingDescriptorCopyTests.cpp`](../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp) |
| Shader-visible descriptor access | [`vktBindingShaderAccessTests.cpp`](../../modules/vulkan/binding_model/vktBindingShaderAccessTests.cpp), [`vktBindingDescriptorSetRandomTests.cpp`](../../modules/vulkan/binding_model/vktBindingDescriptorSetRandomTests.cpp) |
| Newer descriptor storage models | [`vktBindingDescriptorBufferTests.cpp`](../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp), [`vktBindingDescriptorHeapTests.cpp`](../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp) |
| Extension interactions | [`vktBindingMutableTests.cpp`](../../modules/vulkan/binding_model/vktBindingMutableTests.cpp), [`vktBindingDescriptorCombinationTests.cpp`](../../modules/vulkan/binding_model/vktBindingDescriptorCombinationTests.cpp), [`vktBindingPushConstantBankTests.cpp`](../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp) |
| Address and acceleration-structure descriptors | [`vktBindingBufferDeviceAddressTests.cpp`](../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp), [`vktBindingDescriptorUpdateASTests.cpp`](../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp) |

## Notes

- Top-level group count: 14 direct root children discovered from root includes and cross-checked against direct child registration.
- Writing scope: 15 Level-3 pages, because [`vktBindingDescriptorUpdateASTests.cpp`](../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp) is a nested registered group under `descriptor_update`.
- Mustpass coverage is available in [`binding-model.txt`](../../mustpass/main/vk-default/binding-model.txt).
