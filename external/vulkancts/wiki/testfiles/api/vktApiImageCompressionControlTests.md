# [vktApiImageCompressionControlTests.cpp](../../../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L1)

## Overview

Tests the VK_EXT_image_compression_control extension, verifying that images created with compression control structures report correct compression properties. Covers image creation with various compression flags, Android Hardware Buffer compression control, and swapchain image compression control.

## Role of File

Implementation-heavy. Contains all test logic, support checking, and registration. The public entry point [createImageCompressionControlTests()](../../../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L738) assembles the test tree.

## Source Code

- Source: [vktApiImageCompressionControlTests.cpp](../../../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L1)
- Header: [vktApiImageCompressionControlTests.hpp](../../../../../modules/vulkan/api/vktApiImageCompressionControlTests.hpp#L1)
- Parent registration: [vktApiTests.cpp](../../../../../modules/vulkan/api/vktApiTests.cpp#L129) adds `image_compression_control` group to `api`

## Registration Path

```
api
 +-- image_compression_control
      +-- create_image
      |    +-- no_compression_control
      |    +-- default
      |    +-- fixed_rate_default
      |    +-- disabled
      |    +-- explicit
      +-- android_hardware_buffer
      |    +-- default
      |    +-- fixed_rate_default
      |    +-- disabled
      |    +-- explicit
      +-- swapchain
           +-- <wsi_type>
                +-- default
                +-- fixed_rate_default
                +-- disabled
                +-- explicit
```

## Test Hierarchy

```
image_compression_control
 +-- create_image
 |    +-- no_compression_control  -- images created without compression control struct
 |    +-- default                 -- VK_IMAGE_COMPRESSION_DEFAULT_EXT
 |    +-- fixed_rate_default      -- VK_IMAGE_COMPRESSION_FIXED_RATE_DEFAULT_EXT
 |    +-- disabled                -- VK_IMAGE_COMPRESSION_DISABLED_EXT
 |    +-- explicit                -- VK_IMAGE_COMPRESSION_FIXED_RATE_EXPLICIT_EXT
 |         (each contains per-format subtests for core, YCbCr, and YCbCr extended formats)
 +-- android_hardware_buffer
 |    +-- default
 |    +-- fixed_rate_default
 |    +-- disabled
 |    +-- explicit
 |         (each contains per-AHB-format subtests)
 +-- swapchain
      +-- <wsi_type>              (one subgroup per WSI platform)
           +-- default
           +-- fixed_rate_default
           +-- disabled
           +-- explicit
```

## Test Families

### create_image

Tests image creation with `VkImageCompressionControlEXT` in the pNext chain. For each compression flag, iterates over core formats, YCbCr formats, and YCbCr extended formats (skipping compressed formats). Creates an image, then queries `VkImageCompressionPropertiesEXT` via `vkGetImageSubresourceLayout2` and `vkGetPhysicalDeviceImageFormatProperties2`. Validates that reported compression properties are consistent with the requested control flags. Implemented by [imageCreateTest()](../../../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L367) and [validate()](../../../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L102).

### android_hardware_buffer

Tests image creation with compression control for Android Hardware Buffer external memory. Iterates over AHB-compatible formats. Creates an AHB, imports it as a Vulkan image with compression control, and validates compression properties. Implemented by [ahbImageCreateTest()](../../../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L293).

### swapchain

Tests swapchain image compression control. Creates a swapchain with `VkImageCompressionControlEXT` in the pNext chain, retrieves swapchain images, and validates their compression properties. Requires `VK_EXT_image_compression_control_swapchain`. Implemented by [swapchainCreateTest()](../../../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L592).

## Parameter Dimensions

| Dimension | Observed Values |
|---|---|
| Compression Flag | DEFAULT, FIXED_RATE_DEFAULT, DISABLED, FIXED_RATE_EXPLICIT |
| Image Source | create_image, android_hardware_buffer, swapchain |
| Format | Core formats, YCbCr formats, YCbCr extended formats, AHB formats |
| WSI Type | All vk::wsi::Type values (for swapchain) |

## Support / Feature Requirements

- `VK_EXT_image_compression_control` required by all tests ([checkImageCompressionControlSupport()](../../../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L80))
- `imageCompressionControl` feature must be enabled ([L94-L96](../../../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L94))
- `VK_EXT_image_compression_control_swapchain` required for swapchain tests ([L88](../../../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L88))
- `imageCompressionControlSwapchain` feature must be enabled for swapchain tests ([L97-L99](../../../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L97))
- `VK_ANDROID_external_memory_android_hardware_buffer` required for AHB tests ([L297](../../../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L297))
- WSI platform extensions required for swapchain tests

## Verification Methods

- Compression flag validation: When `useExtension=true`, verifies that reported compression flags are consistent with requested flags (e.g., `DISABLED` must report `VK_IMAGE_COMPRESSION_DISABLED_EXT`, `DEFAULT` must not report fixed-rate flags) ([validate()](../../../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L102))
- Fixed rate validation: For `FIXED_RATE_EXPLICIT_EXT`, verifies the actual rate is >= the minimum requested rate ([L190-L199](../../../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L190))
- Format property consistency: Verifies that compression properties from `vkGetImageSubresourceLayout2` are consistent with those from `vkGetPhysicalDeviceImageFormatProperties2`
- When `useExtension=false` (no compression control), verifies no fixed-rate compression is reported

## Test Principles Observed

- Compression control is an optional feature with separate enable flags for images and swapchains
- YCbCr multi-plane images are tested per-plane
- AHB tests require both external memory and compression control support
- WSI tests create custom instances and devices with required extensions

## Notes / Uncertainties

- The group name is `image_compression_control` as confirmed in [createImageCompressionControlTests()](../../../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L741)
- Compressed formats (e.g., BC, ETC, ASTC) are explicitly skipped in the create_image tests ([L450-L451](../../../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L450))
- The `FIXED_RATE_EXPLICIT_EXT` tests set `compressionControlPlaneCount` to the number of YCbCr planes for multi-planar formats ([L454](../../../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L454))
- Swapchain tests iterate over all WSI types, but most will be skipped on platforms that do not support them
