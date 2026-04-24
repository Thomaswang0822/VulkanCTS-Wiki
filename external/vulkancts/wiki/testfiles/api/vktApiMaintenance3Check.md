# [vktApiMaintenance3Check.cpp](../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L1)

## Overview

Tests conformance of the VK_KHR_maintenance3 extension by validating the VkPhysicalDeviceMaintenance3Properties structure against minimum required values, exercising vkGetDescriptorSetLayoutSupport across all descriptor type combinations at maximum counts, and verifying VkDescriptorSetVariableDescriptorCountLayoutSupport behavior for variable-size descriptor bindings.

## Role of File

Implementation-heavy. Contains all test logic, instance classes, helper functions for descriptor count distribution, and the registration entry point.

## Source Code

- Implementation: [vktApiMaintenance3Check.cpp](../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L1)
- Header: [vktApiMaintenance3Check.hpp](../../modules/vulkan/api/vktApiMaintenance3Check.hpp#L1)
- Registration function: [createMaintenance3Tests()](../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L862)
- Registered under: api -> maintenance3

## Registration Path

```
api
+-- maintenance3
    +-- maintenance3_check
```

## Test Hierarchy

```
maintenance3_check
+-- maintenance3_properties
+-- descriptor_set
+-- support_count_sampler_no_variable_size
+-- support_count_sampler_no_variable_size_nonzero_binding_offset
+-- support_count_sampler_no_variable_size_create_layout
+-- support_count_sampler_no_variable_size_nonzero_binding_offset_create_layout
+-- support_count_sampler_no_variable_size_extra_bindings
+-- ... (many more support_count_* variants)
```

## Test Families

### maintenance3_properties

Verifies that VkPhysicalDeviceMaintenance3Properties returned by the implementation meets the minimum required values: maxMemoryAllocationSize >= 1073741824 (1 GiB) and maxPerSetDescriptors >= 1024. The test pre-fills the struct with values one below the minimums, queries the device, and checks the returned values.

- Instance: [Maintenance3StructTestInstance](../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L408)
- Case: [Maintenance3StructTestCase](../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L447)
- Support gate: [VK_KHR_maintenance3](../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L459)

### descriptor_set

Enumerates every combination of descriptor types (1 through all types), calculates the maximum descriptor counts per type that respect all device limits using an even distribution algorithm, then calls vkGetDescriptorSetLayoutSupport and verifies it returns supported=VK_TRUE. On non-VKSC builds, inline uniform block types are conditionally included and limited when counts exceed 64.

- Instance: [Maintenance3DescriptorTestInstance](../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L469)
- Case: [Maintenance3DescriptorTestCase](../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L615)
- Support gate: [VK_KHR_maintenance3](../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L627)
- Key helper: [distributeCounts()](../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L139) - distributes descriptor counts evenly across types respecting limits
- Key helper: [buildLimitsVector()](../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L230) - builds the limits vector from device properties

### support_count_* (generated)

Tests VkDescriptorSetVariableDescriptorCountLayoutSupport returned by vkGetDescriptorSetLayoutSupport. Each test is parameterized by descriptor type, extra bindings, variable-size usage, binding offset, and whether to actually create the layout. Verifies: maxVariableDescriptorCount is 0 when no variable counts are used; consistency between zero-descriptor and one-descriptor queries; that the reported max count is actually usable; and for inline uniform blocks, that the count is a multiple of 4 and does not exceed maxInlineUniformBlockSize.

- Function: [testCountLayoutSupport()](../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L680)
- Params struct: [CountLayoutSupportParams](../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L635)
- Support gate: [VK_KHR_maintenance3 + VK_EXT_descriptor_indexing](../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L644-L647)
- Additional gate for variable size: [descriptorBindingVariableDescriptorCount](../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L649-L654)
- Additional gate for inline uniform block: [VK_EXT_inline_uniform_block](../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L656-L658)

## Parameter Dimensions

| Dimension | Observed Values | Notes |
|---|---|---|
| descriptorType | SAMPLER, COMBINED_IMAGE_SAMPLER, SAMPLED_IMAGE, STORAGE_IMAGE, UNIFORM_TEXEL_BUFFER, STORAGE_TEXEL_BUFFER, UNIFORM_BUFFER, STORAGE_BUFFER, UNIFORM_BUFFER_DYNAMIC, STORAGE_BUFFER_DYNAMIC, INPUT_ATTACHMENT, INLINE_UNIFORM_BLOCK | 12 types at [L869-L882](../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L869) |
| extraBindings | false, true | Adds 3 uniform buffer bindings; [L885](../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L885) |
| useVariableSize | false, true | Skipped for DYNAMIC types; [L886](../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L886), skip at [L890-L892](../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L890) |
| bindingOffset | 0u, 1u | [L887](../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L887) |
| createLayout | false, true | Actually creates the descriptor set layout; [L888](../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L888) |

## Support / Feature Requirements

| Requirement | Where | Context |
|---|---|---|
| VK_KHR_maintenance3 | [L459](../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L459), [L627](../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L627), [L646](../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L646) | All tests |
| VK_EXT_descriptor_indexing | [L647](../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L647) | support_count_* tests |
| descriptorBindingVariableDescriptorCount | [L651-L653](../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L651) | support_count_* with useVariableSize=true |
| VK_EXT_inline_uniform_block | [L656-L657](../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L656) | support_count_* with INLINE_UNIFORM_BLOCK type |
| VK_EXT_inline_uniform_block (feature: inlineUniformBlock) | [L486-L496](../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L486) | descriptor_set test on non-VKSC |

## Verification Methods

- **Minimum value check**: Compares returned property values against spec-mandated minimums ([L433-L437](../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L433))
- **Layout support query**: Calls vkGetDescriptorSetLayoutSupport and asserts supported=VK_TRUE for maximally-filled layouts ([L601-L607](../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L601))
- **maxVariableDescriptorCount consistency**: Verifies zero-descriptor and one-descriptor queries return the same maxVariableDescriptorCount ([L818-L824](../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L818))
- **Max count usability**: Creates a layout with the reported max count and verifies it is supported ([L827-L834](../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L827))
- **Inline uniform block alignment**: Verifies maxVariableDescriptorCount is a multiple of 4 and <= maxInlineUniformBlockSize ([L806-L813](../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L806))
- **Layout creation**: Optionally creates the descriptor set layout to confirm it succeeds ([L837-L846](../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L837))

## Test Principles Observed

- **Limit coverage**: Exercises all per-stage and per-set descriptor limits from VkPhysicalDeviceProperties and VkPhysicalDeviceMaintenance3Properties ([L276-L302](../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L276))
- **Combinatorial exhaustiveness**: Tests every subset of descriptor type combinations from size 1 through all types ([L563-L608](../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L563))
- **Sentinel pre-fill**: Pre-fills maintenance3 properties with below-minimum values to detect if the implementation actually writes them ([L419-L424](../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L419))
- **Garbage value probe**: Sets maxVariableDescriptorCount to UINT32_MAX before querying to detect if the implementation actually writes the output ([L673](../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L673))

## Notes / Uncertainties

- The descriptor_set test uses a custom even-distribution algorithm ([distributeCounts()](../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L139)) to assign descriptor counts across types. This is an approximation and may not exercise the absolute maximum for every individual type.
- On VKSC builds, inline uniform block types are excluded entirely, and binding counts are capped at 1024 ([L328-L332](../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L328)).
- The support_count tests for sparse image format with invalid flags always pass because some implementations ignore wrong flags ([L306-L308](../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L306), [L316-L318](../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L316)).
- The entire file is compiled for both VKSC and non-VKSC, with conditional compilation guards for inline uniform block functionality.
