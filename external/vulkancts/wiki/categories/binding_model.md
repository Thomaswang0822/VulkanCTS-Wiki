# Binding Model Tests

The `binding_model` category documents Vulkan descriptor binding, descriptor updates/copies, descriptor buffers and heaps, mutable descriptors, dynamic offsets, buffer device addresses, inline uniform blocks, acceleration-structure descriptors, and related shader access behavior.

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
| [`vktBindingShaderAccessTests.cpp`](../../modules/vulkan/binding_model/vktBindingShaderAccessTests.cpp) | `shader_access` | VK + VKSC | [vktBindingShaderAccessTests.cpp.md](../testfiles/binding_model/vktBindingShaderAccessTests.cpp.md) |
| [`vktBindingDescriptorUpdateTests.cpp`](../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp) | `descriptor_update` | VK + VKSC | [vktBindingDescriptorUpdateTests.cpp.md](../testfiles/binding_model/vktBindingDescriptorUpdateTests.cpp.md) |
| [`vktBindingDescriptorUpdateASTests.cpp`](../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp) | `descriptor_update → acceleration_structure` | VK only nested | [vktBindingDescriptorUpdateASTests.cpp.md](../testfiles/binding_model/vktBindingDescriptorUpdateASTests.cpp.md) |
| [`vktBindingDescriptorSetRandomTests.cpp`](../../modules/vulkan/binding_model/vktBindingDescriptorSetRandomTests.cpp) | `descriptorset_random` | VK + VKSC | [vktBindingDescriptorSetRandomTests.cpp.md](../testfiles/binding_model/vktBindingDescriptorSetRandomTests.cpp.md) |
| [`vktBindingDescriptorCopyTests.cpp`](../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp) | `descriptor_copy` | VK + VKSC | [vktBindingDescriptorCopyTests.cpp.md](../testfiles/binding_model/vktBindingDescriptorCopyTests.cpp.md) |
| [`vktBindingBufferDeviceAddressTests.cpp`](../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp) | `buffer_device_address` | VK + VKSC | [vktBindingBufferDeviceAddressTests.cpp.md](../testfiles/binding_model/vktBindingBufferDeviceAddressTests.cpp.md) |
| [`vktBindingDynamicOffsetTests.cpp`](../../modules/vulkan/binding_model/vktBindingDynamicOffsetTests.cpp) | `dynamic_offset` | VK only | [vktBindingDynamicOffsetTests.cpp.md](../testfiles/binding_model/vktBindingDynamicOffsetTests.cpp.md) |
| [`vktBindingMutableTests.cpp`](../../modules/vulkan/binding_model/vktBindingMutableTests.cpp) | `mutable_descriptor` | VK only | [vktBindingMutableTests.cpp.md](../testfiles/binding_model/vktBindingMutableTests.cpp.md) |
| [`vktBindingDescriptorBufferTests.cpp`](../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp) | `descriptor_buffer` | VK only | [vktBindingDescriptorBufferTests.cpp.md](../testfiles/binding_model/vktBindingDescriptorBufferTests.cpp.md) |
| [`vktBindingDescriptorCombinationTests.cpp`](../../modules/vulkan/binding_model/vktBindingDescriptorCombinationTests.cpp) | `descriptor_combination` | VK only | [vktBindingDescriptorCombinationTests.cpp.md](../testfiles/binding_model/vktBindingDescriptorCombinationTests.cpp.md) |
| [`vktBindingPushConstantBankTests.cpp`](../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp) | `push_constant_bank` | VK only | [vktBindingPushConstantBankTests.cpp.md](../testfiles/binding_model/vktBindingPushConstantBankTests.cpp.md) |
| [`vktBindingDescriptorHeapTests.cpp`](../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp) | `descriptor_heap` | VK only | [vktBindingDescriptorHeapTests.cpp.md](../testfiles/binding_model/vktBindingDescriptorHeapTests.cpp.md) |
| [`vktBindingStagesTests.cpp`](../../modules/vulkan/binding_model/vktBindingStagesTests.cpp) | `stages` | VK only | [vktBindingStagesTests.cpp.md](../testfiles/binding_model/vktBindingStagesTests.cpp.md) |
| [`vktBindingDescriptorInlineUniformTests.cpp`](../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp) | `inline_uniform_blocks` | VK only | [vktBindingDescriptorInlineUniformTests.cpp.md](../testfiles/binding_model/vktBindingDescriptorInlineUniformTests.cpp.md) |
| [`vktBindingUnusedInvalidDescriptorTests.cpp`](../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp) | `unused_invalid_descriptor` | VK only | [vktBindingUnusedInvalidDescriptorTests.cpp.md](../testfiles/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp.md) |

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

- Official tracker count: 14 top-level groups discovered from root includes and cross-checked against direct child registration.
- Writing scope: 15 Level-3 pages, because [`vktBindingDescriptorUpdateASTests.cpp`](../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp) is a nested registered group under `descriptor_update`.
- Mustpass validation may be unavailable for this category if no category-specific mustpass text file exists in the expected `vk-default` location.
