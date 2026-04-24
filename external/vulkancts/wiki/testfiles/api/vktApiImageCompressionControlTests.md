# [vktApiImageCompressionControlTests.cpp](../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L1)

## Overview

Tests the `VK_EXT_image_compression_control` and `VK_EXT_image_compression_control_swapchain` extensions. Validates that image and swapchain creation with compression control structures produces images whose queried compression properties are consistent with the requested compression flags and fixed-rate settings.

## Role of File

Implementation-heavy. Contains test logic, validation helpers, and registration in a single source file (~808 lines). The public entry point [createImageCompressionControlTests()](../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L738) assembles the full test tree.

## Source Code

- Source: [vktApiImageCompressionControlTests.cpp](../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L1)
- Header: [vktApiImageCompressionControlTests.hpp](../../modules/vulkan/api/vktApiImageCompressionControlTests.hpp#L1)
- Parent registration: `api` test group, child `image_compression_control` (non-VKSC only)

## Registration Path

```
api
 +-- image_compression_control
      +-- create_image
      +-- android_hardware_buffer
      +-- swapchain
```

## Test Hierarchy

```
image_compression_control
 +-- create_image
 |    +-- no_compression_control       -- images created without VkImageCompressionControlEXT
 |    +-- default                      -- VK_IMAGE_COMPRESSION_DEFAULT_EXT
 |    +-- fixed_rate_default           -- VK_IMAGE_COMPRESSION_FIXED_RATE_DEFAULT_EXT
 |    +-- disabled                     -- VK_IMAGE_COMPRESSION_DISABLED_EXT
 |    +-- explicit                     -- VK_IMAGE_COMPRESSION_FIXED_RATE_EXPLICIT_EXT
 |         +-- <format_name>           -- per core/YCbCr/YCbCr-ext format
 +-- android_hardware_buffer
 |    +-- default
 |    +-- fixed_rate_default
 |    +-- disabled
 |    +-- explicit
 |         +-- <format_name>           -- per AHB format
 +-- swapchain
      +-- <wsi_type>                   -- per platform (e.g. xlib, wayland, win32, etc.)
           +-- default
           +-- fixed_rate_default
           +-- disabled
           +-- explicit
```

## Test Families

### Create Image Family

Tests creating images with `VkImageCompressionControlEXT` in the pNext chain and validating compression properties via `vkGetImageSubresourceLayout2EXT`. Uses [imageCreateTest()](../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L367). Iterates over core formats, YCbCr formats, and YCbCr extended formats via [addImageCompressionControlTests()](../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L423). For `FIXED_RATE_EXPLICIT`, iterates 24 combinations of fixed-rate flags per plane.

### Android Hardware Buffer Family

Tests creating images backed by Android Hardware Buffers with compression control. Uses [ahbImageCreateTest()](../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L293) which allocates AHB memory, creates an image with external memory and compression control, binds memory, and validates. Covers a fixed set of AHB-compatible formats via [addAhbCompressionControlTests()](../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L714).

### Swapchain Family

Tests creating swapchains with `VkImageCompressionControlEXT` in the swapchain create info pNext chain. Uses [swapchainCreateTest()](../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L592). Creates a WSI surface, queries surface format compression properties, creates a swapchain with compression control, and validates the resulting swapchain images. Iterates over all WSI types and all surface formats.

## Parameter Dimensions

| Dimension | Observed Values |
|---|---|
| Compression Flag | default, fixed_rate_default, disabled, explicit |
| Use Extension | true, false (no_compression_control sub-group) |
| Image Format (create_image) | All core formats + YCbCr + YCbCr extended (compressed formats skipped) |
| Image Format (AHB) | R8G8B8A8_UNORM, R8G8B8_UNORM, R5G6B5_UNORM_PACK16, R16G16B16A16_SFLOAT, A2B10G10R10_UNORM_PACK32, D16_UNORM, X8_D24_UNORM_PACK32, D24_UNORM_S8_UINT, D32_SFLOAT, D32_SFLOAT_S8_UINT, S8_UINT |
| WSI Type | All platform WSI types (xlib, xcb, wayland, win32, android, etc.) |
| Fixed Rate Flags | 24 combinations of XOR-shifted bit patterns per plane (explicit mode only) |

## Support / Feature Requirements

- `VK_EXT_image_compression_control` required for all tests ([checkImageCompressionControlSupport()](../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L80))
- `VK_EXT_image_compression_control_swapchain` required for swapchain tests ([checkImageCompressionControlSupport()](../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L88))
- `imageCompressionControl` feature must be enabled
- `imageCompressionControlSwapchain` feature must be enabled for swapchain tests
- `VK_ANDROID_external_memory_android_hardware_buffer` required for AHB tests ([ahbImageCreateTest()](../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L297))
- WSI surface and swapchain support required for swapchain tests
- AHB format and usage must be supported ([checkAhbImageSupport()](../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L219))

## Verification Methods

- [validate()](../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L102): After image creation, queries compression properties via `vkGetImageSubresourceLayout2EXT` and `vkGetPhysicalDeviceImageFormatProperties2`, then checks:
  - Fixed-rate flags returned are a subset of supported flags
  - Compression flags returned are a subset of supported flags
  - DEFAULT compression does not produce lossy fixed-rate flags
  - DISABLED compression results in `VK_IMAGE_COMPRESSION_DISABLED_EXT` and zero fixed-rate flags
  - FIXED_RATE_DEFAULT returns explicit, disabled, or default compression flags
  - FIXED_RATE_EXPLICIT actual rate is not less than requested minimum rate
  - Without extension: fixed-rate should be NONE and compression should be default or disabled only
- Uses `tcu::ResultCollector` to accumulate multiple validation failures per test

## Test Principles Observed

- YCbCr multi-plane format support with per-plane compression control plane count ([addImageCompressionControlTests()](../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L453))
- Comprehensive fixed-rate flag iteration for explicit mode (24 XOR-shifted combinations)
- Swapchain compression validation against surface format capabilities
- AHB external memory integration with compression control

## Notes / Uncertainties

- The fixed-rate flag iteration pattern (`planeFlags[0] ^= 3 << i`) generates 24 combinations that may not cover all valid fixed-rate flag values systematically ([line 314-319](../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L314))
- The swapchain test creates a custom instance and device with WSI extensions rather than using the default context device ([DeviceHelper](../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L561))
- Compressed formats are explicitly skipped in create_image tests ([line 450](../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L450))
