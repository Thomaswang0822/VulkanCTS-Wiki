# [vktApiMaintenance6Check.cpp](../../../modules/vulkan/api/vktApiMaintenance6Check.cpp#L1)

## Overview

Tests VK_KHR_maintenance6 properties by verifying that `maxCombinedImageSamplerDescriptorCount` reported via `VkPhysicalDeviceMaintenance6PropertiesKHR` is at least as large as the `combinedImageSamplerDescriptorCount` reported for any YCbCr format via `VkSamplerYcbcrConversionImageFormatProperties`.

## Role of File

Implementation-heavy. Contains both the test case registration and the full test instance logic in a single file.

## Source Code

| File | Description |
|------|-------------|
| [vktApiMaintenance6Check.cpp](../../../modules/vulkan/api/vktApiMaintenance6Check.cpp#L1) | Test implementation and registration |
| [vktApiMaintenance6Check.hpp](../../../modules/vulkan/api/vktApiMaintenance6Check.hpp#L1) | Declares `createMaintenance6Tests` |
| [vktApiTests.cpp](../../../modules/vulkan/api/vktApiTests.cpp#L131) | Parent registration: `apiTests->addChild(createMaintenance6Tests(testCtx))` |

## Registration Hierarchy

```text
api.maintenance6_check
└── maintenance6_properties (non-VulkanSC only)
```

## Test Families

Group `maintenance6_check` registered at [vktApiMaintenance6Check.cpp#L145](../../../modules/vulkan/api/vktApiMaintenance6Check.cpp#L145): `new tcu::TestCaseGroup(testCtx, "maintenance6_check", "Maintenance6 Tests")`.

### maintenance6_properties — Maintenance6 property validation

Registered at [vktApiMaintenance6Check.cpp#L146](../../../modules/vulkan/api/vktApiMaintenance6Check.cpp#L146).

The test instance `Maintenance6MaxCombinedImageSamplerDescriptorCountTestInstance` at [vktApiMaintenance6Check.cpp#L52](../../../modules/vulkan/api/vktApiMaintenance6Check.cpp#L52):
1. Queries `VkPhysicalDeviceMaintenance6PropertiesKHR` via `getPhysicalDeviceProperties2` ([line 66](../../../modules/vulkan/api/vktApiMaintenance6Check.cpp#L66))
2. Iterates over three YCbCr format ranges defined at [lines 68-81](../../../modules/vulkan/api/vktApiMaintenance6Check.cpp#L68):
   - YCbCr formats: `VK_FORMAT_G8B8G8R8_422_UNORM` through `VK_FORMAT_G16_B16_R16_3PLANE_444_UNORM`
   - YCbCr extended formats: `VK_FORMAT_G8_B8R8_2PLANE_444_UNORM` through `VK_FORMAT_G16_B16R16_2PLANE_444_UNORM`
   - `VK_FORMAT_R16G16_S10_5_NV`
3. For each format, queries `VkSamplerYcbcrConversionImageFormatProperties::combinedImageSamplerDescriptorCount` via `getPhysicalDeviceImageFormatProperties2` ([line 99](../../../modules/vulkan/api/vktApiMaintenance6Check.cpp#L99))
4. Fails if any format's `combinedImageSamplerDescriptorCount` exceeds `maxCombinedImageSamplerDescriptorCount` ([line 100](../../../modules/vulkan/api/vktApiMaintenance6Check.cpp#L100))

## Parameter Dimensions

| Dimension | Observed Values | Notes |
|-----------|----------------|-------|
| Format ranges | 3 ranges | YCbCr, YCbCr extended, and R16G16_S10_5_NV |
| Image type | VK_IMAGE_TYPE_2D | Hard-coded at [line 96](../../../modules/vulkan/api/vktApiMaintenance6Check.cpp#L96) |
| Tiling | VK_IMAGE_TILING_OPTIMAL | Hard-coded at [line 97](../../../modules/vulkan/api/vktApiMaintenance6Check.cpp#L97) |
| Usage | VK_IMAGE_USAGE_TRANSFER_DST_BIT | Hard-coded at [line 98](../../../modules/vulkan/api/vktApiMaintenance6Check.cpp#L98) |

## Support / Feature Requirements

- `VK_KHR_maintenance6` required via `checkSupport` at [line 130](../../../modules/vulkan/api/vktApiMaintenance6Check.cpp#L130)
- Entire file is guarded by `#ifndef CTS_USES_VULKANSC` at [line 39](../../../modules/vulkan/api/vktApiMaintenance6Check.cpp#L39)

## Verification Methods

- **Property comparison**: For each YCbCr format, `combinedImageSamplerDescriptorCount` must not exceed `maxCombinedImageSamplerDescriptorCount`. A violation produces a descriptive failure message including the format name and both values ([lines 103-108](../../../modules/vulkan/api/vktApiMaintenance6Check.cpp#L103)).

## Test Principles Observed

- Conformance property validation: checks that a reported limit is consistent with per-format properties
- Exhaustive format iteration: covers all YCbCr and related formats

## Notes / Uncertainties

- The test does not verify the `VkSamplerYcbcrConversionImageFormatProperties` pNext chain is actually supported; it relies on `getPhysicalDeviceImageFormatProperties2` silently ignoring unsupported pNext chains
- The group name is `maintenance6_check` (not `maintenance6`), which differs from the factory function name `createMaintenance6Tests`
