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
└── invalid_sample_index
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

6 Amber test cases (lines 105-145):
- `sample_count_2`
- `sample_count_4`
- `sample_count_8`
- `sample_count_16`
- `sample_count_32`
- `sample_count_64`

Requires: `shaderStorageImageMultisample` feature.

Test principle: Validates that writes to out-of-range sample indices are silently discarded.

## Parameter Dimensions

None at the registration level. Each sub-group enumerates specific test cases as individual Amber tests.

## Support/Feature Requirements

- `atomic` sub-group: requires `shaderStorageImageMultisample`. R64 variants additionally require `shaderInt64`. Excluded on VulkanSC builds.
- `invalid_sample_index` sub-group: requires `shaderStorageImageMultisample`. Available on all platforms including VulkanSC.

## Verification Methods

All tests are Amber-based. No C++-side verification logic.

## Notes

- The `atomic` sub-group is excluded on VulkanSC builds.
- The `invalid_sample_index` sub-group is available on all platforms.
- The factory function creates a `TestCaseGroup(testCtx, "multisample")` at line 151.
