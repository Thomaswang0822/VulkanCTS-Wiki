# vktImageExtendedUsageBitTests ([source](../../../../modules/vulkan/image/vktImageExtendedUsageBitTests.cpp))

## Overview

Tests that verify the VK_IMAGE_CREATE_EXTENDED_USAGE_BIT functionality with vkGetPhysicalDeviceImageFormatProperties. The file validates that images created with the extended usage and mutable format bits can use image usage flags that would not normally be supported for the image's native format, provided at least one compatible view format supports those usage flags.

## Role of File

Implementation file that registers the `extended_usage_bit_compatibility` test group and provides complete test implementations. Contains helper classes, test functions, and the factory function that populates the test hierarchy.

## Source Code

- Implementation: [vktImageExtendedUsageBitTests.cpp](../../../../modules/vulkan/image/vktImageExtendedUsageBitTests.cpp)
- Header: [vktImageExtendedUsageBitTests.hpp](../../../../modules/vulkan/image/vktImageExtendedUsageBitTests.hpp)

## Registration Hierarchy

```text
image.extended_usage_bit_compatibility
├── image_format_properties
├── image_format_properties2
└── image_format_list
```

Evidence:
- `extended_usage_bit_compatibility` group created by [`createImageExtendedUsageBitTests()`](../../../../modules/vulkan/image/vktImageExtendedUsageBitTests.cpp#L282-L356)
- Three subgroups created at lines 286-291
- Tests added to each subgroup at lines 343-348

## Test Families

### image_format_properties �?vkGetPhysicalDeviceImageFormatProperties tests

Tests using the original `vkGetPhysicalDeviceImageFormatProperties` API (VK_KHR_get_physical_device_properties2 not required). Validates that format compatibility works with the legacy API.

### image_format_properties2 �?vkGetPhysicalDeviceImageFormatProperties2 tests

Tests using `vkGetPhysicalDeviceImageFormatProperties2`. Validates that format compatibility works with the extended API structure.

### image_format_list �?vkGetPhysicalDeviceImageFormatProperties2 with ImageFormatList tests

Tests using `VkImageFormatListCreateInfo` to specify view formats. Validates that explicit format lists work correctly with extended usage bit.

### Per-combination tests

Each subgroup iterates over:
- All Vulkan core formats (VK_FORMAT_UNDEFINED+1 through VK_CORE_FORMAT_LAST-1)
- Both tiling modes (VK_IMAGE_TILING_LINEAR, VK_IMAGE_TILING_OPTIMAL)
- All image usage flags

## Parameter Dimensions

| Dimension | Values | Source |
|-----------|--------|--------|
| Image Format | All core formats (VK_FORMAT_UNDEFINED+1 to VK_CORE_FORMAT_LAST-1) | [line 330-331](../../../../modules/vulkan/image/vktImageExtendedUsageBitTests.cpp#L330-331) |
| Tiling | VK_IMAGE_TILING_LINEAR, VK_IMAGE_TILING_OPTIMAL | [line 328](../../../../modules/vulkan/image/vktImageExtendedUsageBitTests.cpp#L328) |
| Image Type | VK_IMAGE_TYPE_2D (fixed) | [line 147, 164, 192](../../../../modules/vulkan/image/vktImageExtendedUsageBitTests.cpp#L147) |

### Tested image usage flags

| Usage Flag | Name | Notes |
|------------|------|-------|
| VK_IMAGE_USAGE_TRANSFER_SRC_BIT | transfer_src | Standard transfer source |
| VK_IMAGE_USAGE_TRANSFER_DST_BIT | transfer_dst | Standard transfer destination |
| VK_IMAGE_USAGE_SAMPLED_BIT | sampled | Sampled image usage |
| VK_IMAGE_USAGE_STORAGE_BIT | storage | Storage image usage |
| VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT | color_attachment | Color attachment usage |
| VK_IMAGE_USAGE_DEPTH_STENCIL_ATTACHMENT_BIT | depth_stencil_attachment | Depth/stencil attachment |
| VK_IMAGE_USAGE_TRANSIENT_ATTACHMENT_BIT | transient_attachment | Transient attachment |
| VK_IMAGE_USAGE_INPUT_ATTACHMENT_BIT | input_attachment | Input attachment usage |
| VK_IMAGE_USAGE_VIDEO_DECODE_DST_BIT_KHR | video_decode_dst | Video decode destination (non-VulkanSC) |
| VK_IMAGE_USAGE_VIDEO_DECODE_SRC_BIT_KHR | video_decode_src | Video decode source (non-VulkanSC) |
| VK_IMAGE_USAGE_VIDEO_DECODE_DPB_BIT_KHR | video_decode_dpb | Video decode DPB (non-VulkanSC) |
| VK_IMAGE_USAGE_FRAGMENT_DENSITY_MAP_BIT_EXT | fragment_density_map | Fragment density map (non-VulkanSC) |
| VK_IMAGE_USAGE_FRAGMENT_SHADING_RATE_ATTACHMENT_BIT_KHR | fragment_shading_rate_attachment | FSR attachment (non-VulkanSC) |
| VK_IMAGE_USAGE_VIDEO_ENCODE_DST_BIT_KHR | video_encode_dst | Video encode destination (non-VulkanSC) |
| VK_IMAGE_USAGE_VIDEO_ENCODE_SRC_BIT_KHR | video_encode_src | Video encode source (non-VulkanSC) |
| VK_IMAGE_USAGE_VIDEO_ENCODE_DPB_BIT_KHR | video_encode_dpb | Video encode DPB (non-VulkanSC) |
| VK_IMAGE_USAGE_INVOCATION_MASK_BIT_HUAWEI | invocation_mask | Invocation mask (non-VulkanSC) |
| VK_IMAGE_USAGE_SHADING_RATE_IMAGE_BIT_NV | shading_rate_image | Shading rate image (non-VulkanSC) |

## Support / Feature Requirements

| Requirement | Condition | Source |
|-------------|-----------|--------|
| VK_KHR_maintenance2 | All tests | [line 246](../../../../modules/vulkan/image/vktImageExtendedUsageBitTests.cpp#L246) |
| VK_KHR_video_decode_queue | Video decode usage flags | [line 259-262](../../../../modules/vulkan/image/vktImageExtendedUsageBitTests.cpp#L259-262) |
| VK_KHR_video_encode_queue | Video encode usage flags | [line 264-267](../../../../modules/vulkan/image/vktImageExtendedUsageBitTests.cpp#L264-267) |
| VK_EXT_fragment_density_map | Fragment density map usage | [line 269-270](../../../../modules/vulkan/image/vktImageExtendedUsageBitTests.cpp#L269-270) |
| VK_KHR_fragment_shading_rate | Fragment shading rate usage | [line 272-273](../../../../modules/vulkan/image/vktImageExtendedUsageBitTests.cpp#L272-273) |
| VK_HUAWEI_invocation_mask | Invocation mask usage | [line 275-276](../../../../modules/vulkan/image/vktImageExtendedUsageBitTests.cpp#L275-276) |

## Verification Methods

### Format compatibility check

Tests verify extended usage bit compatibility by:

1. **Find compatible view format**: Iterate through all formats to find one compatible with the image format that supports the requested usage [lines 208-220](../../../../modules/vulkan/image/vktImageExtendedUsageBitTests.cpp#L208-220)
2. **Compatibility criteria** (from `isCompatibleFormat` at [lines 112-126](../../../../modules/vulkan/image/vktImageExtendedUsageBitTests.cpp#L112-126)):
   - Same format (exact match)
   - Uncompressed color formats with same bits-per-pixel
   - Compressed formats that are SRGB/non-SRGB pairs
3. **Expected result**: If any compatible format supports the usage, the query should succeed; otherwise it should fail
4. **Query with extended usage**: Call `getPhysicalDeviceImageFormatProperties` with `VK_IMAGE_CREATE_EXTENDED_USAGE_BIT | VK_IMAGE_CREATE_MUTABLE_FORMAT_BIT` [lines 230-232](../../../../modules/vulkan/image/vktImageExtendedUsageBitTests.cpp#L230-232)
5. **Compare result**: If query result differs from expected, test fails

## Test Principles Observed

- **Extended usage bit purpose**: Allows images to use usage flags not natively supported by their format, provided a compatible view format supports those flags
- **Mutable format bit combination**: Tests always use both EXTENDED_USAGE_BIT and MUTABLE_FORMAT_BIT together
- **Format compatibility matrix**: Tests validate that the compatibility rules are correctly implemented:
  - Same format always compatible
  - Uncompressed color formats with equal texel block sizes compatible
  - Specific SRGB/non-SRGB pairs in BC, ETC2, EAC, ASTC families compatible
- **Per-tiling validation**: Both linear and optimal tiling tested separately
- **Comprehensive format coverage**: All Vulkan core formats tested (185 formats)
- **API variant coverage**: Three API entry points tested: legacy, v2, and with ImageFormatList

## Notes / Uncertainties

- The test uses `VK_CORE_FORMAT_LAST` constant to determine format range, which is asserted to be 185 at [line 47](../../../../modules/vulkan/image/vktImageExtendedUsageBitTests.cpp#L47)
- Video and extension-specific usage flags are guarded by `#ifndef CTS_USES_VULKANSC`
- The test does not create actual images; it only queries format properties
- Format support is verified before adding tests to avoid throwing NotSupportedError during iteration
- If no compatible view format supports the tested usage, the test throws NotSupportedError rather than failing
- The `isCompatibleCompressedFormat` function only handles SRGB/non-SRGB pairs within the same compression family (BC1-7, ETC2, EAC, ASTC)
