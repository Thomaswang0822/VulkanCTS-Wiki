# vktTextureMultisampleTests.cpp

## Overview

Registers the `multisample` test group under the `texture` category. This group contains Amber-based tests that validate atomic operations on multisample storage images and behavior when writing to out-of-range sample indices.

## Role

Registration file

## Source Code

- [vktTextureMultisampleTests.cpp](../../../modules/vulkan/texture/vktTextureMultisampleTests.cpp#L38) - atomic sub-group creation
- [vktTextureMultisampleTests.cpp](../../../modules/vulkan/texture/vktTextureMultisampleTests.cpp#L105) - invalid_sample_index sub-group creation
- [vktTextureMultisampleTests.cpp](../../../modules/vulkan/texture/vktTextureMultisampleTests.cpp#L149) - `createTextureMultisampleTests`

## Registration Hierarchy

```text
texture.multisample
├── atomic (non-VulkanSC only)
└── invalid_sample_index (non-VulkanSC only)
```

## Test Families

### atomic

4 Amber test cases (lines 38-103, non-VulkanSC only):
- `storage_image_r32i` (VK_FORMAT_R32_SINT)
- `storage_image_r32ui` (VK_FORMAT_R32_UINT)
- `storage_image_r64i` (VK_FORMAT_R64_SINT, requires `shaderInt64`)
- `storage_image_r64ui` (VK_FORMAT_R64_UINT, requires `shaderInt64`)

Requires: `shaderStorageImageMultisample` feature. R64 variants additionally require `shaderInt64`.

Test principle: Validates atomic operations on multisample storage images.

### invalid_sample_index

6 Amber test cases (lines 105-145, non-VulkanSC only):
- `sample_count_2`
- `sample_count_4`
- `sample_count_8`
- `sample_count_16`
- `sample_count_32`
- `sample_count_64`

Requires: `shaderStorageImageMultisample` feature.

Test principle: Validates that writes to out-of-range sample indices are discarded.

## Parameter Dimensions

None at the registration level. Each sub-group enumerates specific test cases as individual Amber tests.

## Support/Feature Requirements

- `atomic` sub-group: requires `shaderStorageImageMultisample`. R64 variants additionally require `shaderInt64`. Excluded on VulkanSC by both the parent group registration guard and an internal `#ifndef CTS_USES_VULKANSC` guard (lines 42-100).
- `invalid_sample_index` sub-group: requires `shaderStorageImageMultisample`. Excluded on VulkanSC because the parent `multisample` group is not registered on VulkanSC (see [vktTextureTests.cpp](../../../modules/vulkan/texture/vktTextureTests.cpp#L60-L66)). No internal VulkanSC guard.

## Verification Methods

All tests are Amber-based. No C++-side verification logic.

## Notes

- Both sub-groups are excluded on VulkanSC because the parent `multisample` group is not registered on VulkanSC ([vktTextureTests.cpp](../../../modules/vulkan/texture/vktTextureTests.cpp#L60-L66)). The `atomic` sub-group has an additional internal `#ifndef CTS_USES_VULKANSC` guard, while `invalid_sample_index` relies solely on the parent exclusion.
- The factory function creates a `TestCaseGroup(testCtx, "multisample")` at line 151.
