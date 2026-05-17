# [vktApiDSColorBitCopyTests.cpp](../../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L1)

## Overview

Tests copying between depth/stencil images and color images using vkCmdCopyImage. Verifies that depth or stencil aspect data is preserved bit-for-bit when copied to a same-size color format and back, as enabled by VK_KHR_maintenance8.

## Role of File

Implementation-heavy. Contains all test logic, helper types, and the registration function [createDSColorBitCopyTests()](../../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L875).

## Source Code

- Implementation: [vktApiDSColorBitCopyTests.cpp](../../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L1)
- Header: [vktApiDSColorBitCopyTests.hpp](../../../modules/vulkan/api/vktApiDSColorBitCopyTests.hpp#L1)
- Parent registration: [vktApiTests.cpp](../../../modules/vulkan/api/vktApiTests.cpp#L109)

## Registration Hierarchy

```text
api.ds_color_copy
```

This file registers the top-level `ds_color_copy` subgroup directly under `api` via [createDSColorBitCopyTests()](../../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L875-L877). The remaining test names are generated leaf cases within that subgroup rather than separately registered child groups.

## Test Families

The file does not register any direct child subgroups under `ds_color_copy`; instead, [createDSColorBitCopyTests()](../../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L875-L910) generates leaf tests directly in the `ds_color_copy` group by iterating format pairs, copy direction, mip levels, attachment usage, unrestricted-depth mode, and queue type.

### generated_leaf_cases — Generated depth/stencil-color copy permutations

[DSColorCopyInstance::iterate()](../../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L604) performs a round-trip copy: source buffer to source image, source image to destination image via vkCmdCopyImage, then destination image to destination buffer. The test compares source and destination pixel values bit-for-bit.

[DSColorCopyCase::checkSupport()](../../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L362) verifies that both source and destination formats support the required image usage and mip levels, and checks queue-specific format feature flags for compute-only and transfer-only queues.

### format_groups — Depth/stencil-color format pairing sets

[getFormatGroups()](../../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L67) defines four format groups that pair depth/stencil formats with compatible color formats:

- 32-bit depth: D32_SFLOAT, D32_SFLOAT_S8_UINT paired with R32_SFLOAT, R32_SINT, R32_UINT
- 24-bit depth: X8_D24_UNORM_PACK32, D24_UNORM_S8_UINT paired with R32_SFLOAT, R32_SINT, R32_UINT
- 16-bit depth: D16_UNORM, D16_UNORM_S8_UINT paired with R16_SFLOAT, R16_UNORM, R16_SNORM, R16_UINT, R16_SINT
- 8-bit stencil: S8_UINT, D32_SFLOAT_S8_UINT, D24_UNORM_S8_UINT, D16_UNORM_S8_UINT paired with R8_UINT, R8_SINT, R8_UNORM, R8_SNORM

## Parameter Dimensions

| Dimension | Observed Values |
|---|---|
| Direction | ds-to-color, color-to-ds |
| Aspect | VK_IMAGE_ASPECT_DEPTH_BIT, VK_IMAGE_ASPECT_STENCIL_BIT |
| Source mip level | 0, 3 |
| Destination mip level | 0, 3 |
| Attachment usage | false, true (skipped when mip levels are non-zero) |
| Queue type | UNIVERSAL, COMPUTE_ONLY, TRANSFER_ONLY |
| Unrestricted depth | false (all bit counts), true (32-bit only) |
| DS formats | D32_SFLOAT, D32_SFLOAT_S8_UINT, X8_D24_UNORM_PACK32, D24_UNORM_S8_UINT, D16_UNORM, D16_UNORM_S8_UINT, S8_UINT |
| Color formats | R32_SFLOAT, R32_SINT, R32_UINT, R16_SFLOAT, R16_UNORM, R16_SNORM, R16_UINT, R16_SINT, R8_UINT, R8_SINT, R8_UNORM, R8_SNORM |

## Support / Feature Requirements

| Feature / Extension | Used By |
|---|---|
| VK_KHR_maintenance8 | All tests (required at [line 501](../../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L501)) |
| VK_EXT_depth_range_unrestricted | Tests with unrestricted=true |
| VK_KHR_maintenance10 | Compute-only and transfer-only queue tests (non-SC) |
| VK_KHR_format_feature_flags2 | Compute-only and transfer-only queue tests (non-SC) |
| VK_FORMAT_FEATURE_2_DEPTH_COPY_ON_COMPUTE_QUEUE_BIT_KHR | Compute-only queue tests for depth aspect |
| VK_FORMAT_FEATURE_2_STENCIL_COPY_ON_COMPUTE_QUEUE_BIT_KHR | Compute-only queue tests for stencil aspect |
| VK_FORMAT_FEATURE_2_DEPTH_COPY_ON_TRANSFER_QUEUE_BIT_KHR | Transfer-only queue tests for depth aspect |
| VK_FORMAT_FEATURE_2_STENCIL_COPY_ON_TRANSFER_QUEUE_BIT_KHR | Transfer-only queue tests for stencil aspect |

## Verification Methods

- **Bit-exact pixel comparison**: [PixelValue](../../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L507) compares source and destination pixels at each coordinate. For 8/16/32-bit values, exact integer comparison is used. For 24-bit depth, the lower 24 bits are masked and compared.
- **VK_CHECK**: API calls are verified for success
- **NotSupportedError**: Tests skip if the format does not support the required features or mip levels

## Test Principles Observed

- Bit-exact verification: no tolerance is used; values must match exactly
- Comprehensive format coverage: all valid DS-to-color format pairs are tested in both directions
- Queue coverage: universal, compute-only, and transfer-only queues are tested
- Mip level coverage: both base level and level 3 are tested
- SC divergence: compute-only and transfer-only queue types are skipped for Vulkan SC

## Notes / Uncertainties

- The group name in the source code is `ds_color_copy` at [line 877](../../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L877), not `ds_color_bit_copy` as the filename might suggest
- The factory function is named `createDSColorBitCopyTests` but the group name is `ds_color_copy`
- This Level-3 page documents the registered subgroup `api.ds_color_copy`, which has no separately registered direct child groups in the inspected file; generated test names are leaf cases only
- When using a transfer queue with a depth/stencil source image, a staging image workaround is used because vkCmdCopyBufferToImage cannot be called on a transfer queue with DS images (VUID-vkCmdCopyBufferToImage-commandBuffer-07739)
- The base image extent is 16x16; mip levels scale the source and destination image sizes accordingly
