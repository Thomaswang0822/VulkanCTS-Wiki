# [vktApiMaintenance3Check.cpp](../../../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L1)

## Overview

Tests VK_KHR_maintenance3 functionality, verifying that the `VkPhysicalDeviceMaintenance3Properties` struct reports correct minimum values and that `vkGetDescriptorSetLayoutSupport` correctly reports support for maximal descriptor set layouts. Also tests `VkDescriptorSetVariableDescriptorCountLayoutSupport` via the `VK_EXT_descriptor_indexing` extension.

## Role of File

Implementation-heavy. Contains test logic for struct validation, descriptor set layout support queries, and variable descriptor count support checks. The public entry point [createMaintenance3Tests()](../../../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L862) assembles the test tree.

## Source Code

- Source: [vktApiMaintenance3Check.cpp](../../../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L1)
- Header: [vktApiMaintenance3Check.hpp](../../../../../modules/vulkan/api/vktApiMaintenance3Check.hpp#L1)
- Parent registration: [vktApiTests.cpp](../../../../../modules/vulkan/api/vktApiTests.cpp#L119) adds `maintenance3_check` group to `api`

## Registration Path

```
api
 +-- maintenance3_check
      +-- maintenance3_properties
      +-- descriptor_set
      +-- support_count_<type>[_extra_bindings][_no_variable_size][_nonzero_binding_offset][_create_layout]
```

## Test Hierarchy

```
maintenance3_check
 +-- maintenance3_properties     -- verifies VkPhysicalDeviceMaintenance3Properties minimum values
 +-- descriptor_set              -- tests maximal descriptor set layout support
 +-- support_count_*             -- tests VkDescriptorSetVariableDescriptorCountLayoutSupport
      (parameterized by descriptor type, extra bindings, variable size, binding offset, create layout)
```

## Test Families

### maintenance3_properties

Verifies that `VkPhysicalDeviceMaintenance3Properties` reports `maxMemoryAllocationSize` >= 1073741824 and `maxPerSetDescriptors` >= 1024, as required by the Vulkan specification minimums. Implemented by [Maintenance3StructTestInstance](../../../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L408).

### descriptor_set

Tests that `vkGetDescriptorSetLayoutSupport` returns `supported=VK_TRUE` for descriptor set layouts that maximize descriptor counts within reported device limits. Uses a limit-distribution algorithm ([distributeCounts()](../../../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L139)) to evenly distribute descriptor counts across all descriptor type combinations. Implemented by [Maintenance3DescriptorTestInstance](../../../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L469).

### support_count_* (Count Layout Support)

Tests `VkDescriptorSetVariableDescriptorCountLayoutSupport` reporting. Each test creates a descriptor set layout with one binding of a specific descriptor type and queries support. Verifies that `maxVariableDescriptorCount` is reported correctly, that switching from one to zero descriptors returns the same count, and that the maximum promised count is actually usable. Optionally creates the layout to confirm it succeeds. Implemented by [testCountLayoutSupport()](../../../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L680).

## Parameter Dimensions

| Dimension | Observed Values |
|---|---|
| Descriptor Type | sampler, combined_image_sampler, sampled_image, storage_image, uniform_texel_buffer, storage_texel_buffer, uniform_buffer, storage_buffer, uniform_buffer_dynamic, storage_buffer_dynamic, input_attachment, inline_uniform_block |
| Extra Bindings | true, false |
| Variable Size | true, false |
| Binding Offset | 0, 1 |
| Create Layout | true, false |

## Support / Feature Requirements

- `VK_KHR_maintenance3` required by all tests ([Maintenance3StructTestCase::checkSupport()](../../../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L457), [Maintenance3DescriptorTestCase::checkSupport()](../../../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L625))
- `VK_EXT_descriptor_indexing` required by support_count_* tests ([checkSupportCountLayoutSupport()](../../../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L644))
- `descriptorBindingVariableDescriptorCount` feature required when `useVariableSize=true` ([checkSupportCountLayoutSupport()](../../../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L649))
- `VK_EXT_inline_uniform_block` required when descriptor type is `VK_DESCRIPTOR_TYPE_INLINE_UNIFORM_BLOCK` ([checkSupportCountLayoutSupport()](../../../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L656))

## Verification Methods

- Struct validation: Compares reported property values against spec minimums ([Maintenance3StructTestInstance::iterate()](../../../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L414))
- Descriptor set support: Calls `vkGetDescriptorSetLayoutSupport` and verifies `supported == VK_TRUE` for maximally-sized layouts ([Maintenance3DescriptorTestInstance::iterate()](../../../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L475))
- Count layout support: Verifies `maxVariableDescriptorCount` consistency across zero/one/max descriptor counts; verifies inline uniform block size is a multiple of 4 and within limits; optionally confirms layout creation succeeds ([testCountLayoutSupport()](../../../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L680))

## Test Principles Observed

- Descriptor count distribution algorithm ensures even coverage of all device limits
- Variable descriptor count tests verify both query and creation paths
- Inline uniform block special handling (descriptorCount must be multiple of 4 per VUID 02209)
- VK_SC conditional compilation removes inline uniform block tests

## Notes / Uncertainties

- The group name is `maintenance3_check` as confirmed in [createMaintenance3Tests()](../../../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L864), not `maintenance3`
- The support_count_* tests skip `UNIFORM_BUFFER_DYNAMIC` and `STORAGE_BUFFER_DYNAMIC` when `useVariableSize=true` since variable-size descriptors are not valid for dynamic buffer types ([L890-L892](../../../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L890))
- The descriptor_set test iterates over all combinations of descriptor types from size 1 to full set, which can be a large number of combinations
