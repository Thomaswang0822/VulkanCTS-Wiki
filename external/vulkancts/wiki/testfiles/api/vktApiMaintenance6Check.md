# [vktApiMaintenance6Check.cpp](../../modules/vulkan/api/vktApiMaintenance6Check.cpp#L1)

## Overview

Tests the VK_KHR_maintenance6 extension by verifying that the maxCombinedImageSamplerDescriptorCount property reported via VkPhysicalDeviceMaintenance6PropertiesKHR is an upper bound for the per-format combinedImageSamplerDescriptorCount values reported for YCbCr and related formats.

## Role of File

Implementation-heavy. Contains the single test instance, test case, and the registration entry point. The entire file is wrapped in a `#ifndef CTS_USES_VULKANSC` guard, making it non-VKSC only.

## Source Code

- Implementation: [vktApiMaintenance6Check.cpp](../../modules/vulkan/api/vktApiMaintenance6Check.cpp#L1)
- Header: [vktApiMaintenance6Check.hpp](../../modules/vulkan/api/vktApiMaintenance6Check.hpp#L1)
- Registration function: [createMaintenance6Tests()](../../modules/vulkan/api/vktApiMaintenance6Check.cpp#L142)
- Registered under: api -> maintenance6 (non-VKSC only)

## Registration Path

```
api
+-- maintenance6
    +-- maintenance6_check
```

## Test Hierarchy

```
maintenance6_check
+-- maintenance6_properties
```

## Test Families

### maintenance6_properties

Queries VkPhysicalDeviceMaintenance6PropertiesKHR to obtain maxCombinedImageSamplerDescriptorCount, then iterates over three format ranges (YCbCr formats, YCbCr extended formats, and VK_FORMAT_R16G16_S10_5_NV). For each format, it queries VkSamplerYcbcrConversionImageFormatProperties via getPhysicalDeviceImageFormatProperties2 and verifies that the per-format combinedImageSamplerDescriptorCount does not exceed the global maxCombinedImageSamplerDescriptorCount.

- Instance: [Maintenance6MaxCombinedImageSamplerDescriptorCountTestInstance](../../modules/vulkan/api/vktApiMaintenance6Check.cpp#L52)
- Case: [Maintenance6MaxCombinedImageSamplerDescriptorCountTestCase](../../modules/vulkan/api/vktApiMaintenance6Check.cpp#L117)
- Support gate: [VK_KHR_maintenance6](../../modules/vulkan/api/vktApiMaintenance6Check.cpp#L130)
- Format ranges: [L68-L81](../../modules/vulkan/api/vktApiMaintenance6Check.cpp#L68)

## Parameter Dimensions

| Dimension | Observed Values | Notes |
|---|---|---|
| formatRange | YCbCr formats (VK_FORMAT_G8B8G8R8_422_UNORM to VK_FORMAT_G16_B16_R16_3PLANE_444_UNORM), YCbCr extended formats (VK_FORMAT_G8_B8R8_2PLANE_444_UNORM to VK_FORMAT_G16_B16R16_2PLANE_444_UNORM), VK_FORMAT_R16G16_S10_5_NV | 3 ranges at [L68-L81](../../modules/vulkan/api/vktApiMaintenance6Check.cpp#L68) |

## Support / Feature Requirements

| Requirement | Where | Context |
|---|---|---|
| VK_KHR_maintenance6 | [L130](../../modules/vulkan/api/vktApiMaintenance6Check.cpp#L130) | All tests |
| Non-VKSC build | [L39](../../modules/vulkan/api/vktApiMaintenance6Check.cpp#L39) | Entire file guarded |

## Verification Methods

- **Upper bound check**: For each YCbCr-related format, verifies that combinedImageSamplerDescriptorCount (per-format) <= maxCombinedImageSamplerDescriptorCount (global) at [L100-L109](../../modules/vulkan/api/vktApiMaintenance6Check.cpp#L100)

## Test Principles Observed

- **Cross-property consistency**: Validates that a global property serves as an upper bound for per-format properties ([L100-L109](../../modules/vulkan/api/vktApiMaintenance6Check.cpp#L100))
- **Format range coverage**: Tests all formats in the YCbCr, extended YCbCr, and R16G16_S10_5_NV ranges rather than a subset ([L68-L81](../../modules/vulkan/api/vktApiMaintenance6Check.cpp#L68))

## Notes / Uncertainties

- The test only covers YCbCr and related formats. It does not test other aspects of VK_KHR_maintenance6 such as the new vkCmdBindDescriptorSets2 / vkCmdPushConstants2 / vkCmdSetViewport2 / vkCmdSetScissor2 commands or the VK_KHR_maintenance6 push descriptor set functionality.
- The file is entirely excluded from VKSC builds via the `#ifndef CTS_USES_VULKANSC` guard at [L39](../../modules/vulkan/api/vktApiMaintenance6Check.cpp#L39).
- The test does not verify that getPhysicalDeviceImageFormatProperties2 succeeds for each format; it simply queries and checks the combinedImageSamplerDescriptorCount if the call returns properties.
