# [vktImageTranscodingSupportTests.cpp](../../../../modules/vulkan/image/vktImageTranscodingSupportTests.cpp#L1)

## Overview

[`vktImageTranscodingSupportTests.cpp`](../../../../modules/vulkan/image/vktImageTranscodingSupportTests.cpp#L1) is an implementation-heavy Level-3 file for the `image.extended_usage_bit` subtree. It tests the `VK_IMAGE_CREATE_EXTENDED_USAGE_BIT` feature, which allows creating image views with usage flags that differ from the parent image's original usage flags. The tests verify transcoding between formats with different image usage capabilities through graphics pipeline operations.

## Role of File

- **Role:** implementation-heavy test file
- **Primary source:** [`vktImageTranscodingSupportTests.cpp`](../../../../modules/vulkan/image/vktImageTranscodingSupportTests.cpp#L1)
- **Header:** [`vktImageTranscodingSupportTests.hpp`](../../../../modules/vulkan/image/vktImageTranscodingSupportTests.hpp#L1)
- **Registration context:** registered under `image` in [`vktImageTests.cpp`](../../../../modules/vulkan/image/vktImageTests.cpp) as `extended_usage_bit` group via [`createImageTranscodingSupportTests()`](../../../../modules/vulkan/image/vktImageTranscodingSupportTests.cpp#L1180-L1261)

## Source Code

- Implementation: [vktImageTranscodingSupportTests.cpp](../../../../modules/vulkan/image/vktImageTranscodingSupportTests.cpp#L1)
- Header: [vktImageTranscodingSupportTests.hpp](../../../../modules/vulkan/image/vktImageTranscodingSupportTests.hpp#L1)

## Registration Hierarchy

```text
image.extended_usage_bit
├── attachment_read
├── attachment_write
├── texture_read
└── texture_write
```

## Test Families

### attachment_read �?Attachment read with extended usage

Covers the `attachment_read` direct child registered by [`createImageTranscodingSupportTests()`](../../../../modules/vulkan/image/vktImageTranscodingSupportTests.cpp#L1205-L1257). Tests reading from input attachments where the view usage differs from the original image. Uses `VK_IMAGE_USAGE_INPUT_ATTACHMENT_BIT` as the tested feature with `VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT` as the paired usage.

### attachment_write �?Attachment write with extended usage

Covers the `attachment_write` direct child registered by [`createImageTranscodingSupportTests()`](../../../../modules/vulkan/image/vktImageTranscodingSupportTests.cpp#L1205-L1257). Tests writing to color attachments where the view usage differs from the original image. Uses `VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT` as the tested feature with `VK_IMAGE_USAGE_INPUT_ATTACHMENT_BIT` as the paired usage.

### texture_read �?Texture read with extended usage

Covers the `texture_read` direct child registered by [`createImageTranscodingSupportTests()`](../../../../modules/vulkan/image/vktImageTranscodingSupportTests.cpp#L1205-L1257). Tests reading from sampled images where the view usage differs from the original image. Uses `VK_IMAGE_USAGE_SAMPLED_BIT` as the tested feature with `VK_IMAGE_USAGE_STORAGE_BIT` as the paired usage. Requires `fragmentStoresAndAtomics`.

### texture_write �?Texture write with extended usage

Covers the `texture_write` direct child registered by [`createImageTranscodingSupportTests()`](../../../../modules/vulkan/image/vktImageTranscodingSupportTests.cpp#L1205-L1257). Tests writing to storage images where the view usage differs from the original image. Uses `VK_IMAGE_USAGE_STORAGE_BIT` as the tested feature with `VK_IMAGE_USAGE_SAMPLED_BIT` as the paired usage. Requires `fragmentStoresAndAtomics`.

## Parameter Dimensions

| Dimension | Observed values / construction | Evidence |
|---|---|---|
| Image type | `IMAGE_TYPE_2D` (fixed) | [Line 1244](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageTranscodingSupportTests.cpp#L1244) |
| Image size | `UVec3(16u, 16u, 1u)` (fixed) | [Line 1243](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageTranscodingSupportTests.cpp#L1243) |
| Format families | 8-bit, 16-bit, 24-bit, 32-bit, 48-bit, 64-bit, 96-bit, 128-bit, 192-bit, 256-bit | [Lines 1173-1178](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageTranscodingSupportTests.cpp#L1173-L1178) |
| Tested image usage | Input attachment, color attachment, sampled, storage (per operation) | [Lines 1188-1193](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageTranscodingSupportTests.cpp#L1188-L1193) |
| Base flags | `VK_IMAGE_USAGE_TRANSFER_SRC_BIT \| VK_IMAGE_USAGE_TRANSFER_DST_BIT` | [Line 1201](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageTranscodingSupportTests.cpp#L1201) |

## Support / Feature Requirements

| Feature / Extension | When it applies | Evidence |
|---|---|---|
| `VK_KHR_maintenance2` | All extended usage bit tests | [Line 1089](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageTranscodingSupportTests.cpp#L1089) |
| `fragmentStoresAndAtomics` | `texture_read` and `texture_write` operations | [Lines 1091-1093](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageTranscodingSupportTests.cpp#L1091-L1093) |
| Format support check | All tests verify format supports required usage flags | [Lines 1095-1100](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageTranscodingSupportTests.cpp#L1095-L1100) |

## Verification Methods

- **Data comparison:** Test generates source data, transcodes through shader operation, and verifies output matches input
- **Format compatibility detection:** Tests dynamically find compatible formats that have the required usage feature in [`createInstance()`](../../../../modules/vulkan/image/vktImageTranscodingSupportTests.cpp#L1103-L1168)
- **Memory comparison:** Uses 64-bit word comparison to detect any data corruption during transcoding ([Lines 717-748](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageTranscodingSupportTests.cpp#L717-L748))

## Test Principles Observed

- **Feature format detection:** Tests search for a "featureless" format that does not support the tested usage flag but is compatible with the featured format
- **Usage flag pairing:** Each operation uses a tested flag paired with a compatible alternate flag to verify transcoding
- **Graphics pipeline:** Uses full graphics pipeline with render passes for attachment operations and texture operations
- **Data generation:** Generates test data with special values including infinities, NaNs, and denormalized numbers to stress the transcoding path

## Notes / Uncertainties

- SRGB formats are skipped due to shader layout classifier limitations ([Line 1225-1226](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageTranscodingSupportTests.cpp#L1225-L1226))
- Packed formats are skipped due to shader layout classifier limitations ([Lines 1229-1230](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageTranscodingSupportTests.cpp#L1229-L1230))
- Swizzled component formats (e.g., bgr) are skipped ([Lines 1233-1234](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageTranscodingSupportTests.cpp#L1233-L1234))
- Three-component formats are skipped ([Lines 1237-1238](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageTranscodingSupportTests.cpp#L1237-L1238))
- Compressed formats are skipped ([Lines 1212-1219](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageTranscodingSupportTests.cpp#L1212-L1219))
- Tests only run when a featureless format exists in the compatible format group
