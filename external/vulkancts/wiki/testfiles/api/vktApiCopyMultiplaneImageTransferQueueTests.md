# vktApiCopyMultiplaneImageTransferQueueTests ([source](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp))

## Overview

Tests that verify the correctness of multiplane (YCbCr) image copy operations executed on dedicated transfer queues. The file covers copies between multiplane images of various formats and chroma subsampling ratios, testing both direct image-to-image copies via `vkCmdCopyImage` and indirect copies through an intermediate buffer via `vkCmdCopyImageToBuffer` followed by `vkCmdCopyBufferToImage`. Disjoint and non-disjoint image allocations are tested, and random copy regions are generated respecting transfer queue granularity constraints.

## Role of File

This file provides the test implementation and registration for all multiplane image transfer queue copy tests in the Vulkan CTS `api` test group. It uses a function-based test approach (`addFunctionCase`) rather than the class-based approach used in other copy test files. The file contains helper functions for format compatibility checking, random copy region generation, and byte-level verification.

## Source Code

- Implementation: [vktApiCopyMultiplaneImageTransferQueueTests.cpp](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp)
- Header: [vktApiCopyMultiplaneImageTransferQueueTests.hpp](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.hpp)

## Registration Path

```
api > copy_and_blit > multiplanar_xfer
```

The top-level registration function `createCopyMultiplaneImageTransferQueueTests` at [line 769](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L769) creates the `multiplanar_xfer` group. This is registered directly under `copy_and_blit` in [vktApiCopiesAndBlittingTests.cpp](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp) at [line 283](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L283).

## Test Hierarchy

```
multiplanar_xfer
|-- <src_format_name>
|   |-- <dst_format_name>
|   |   |-- optimal_disjoint_buffer_optimal
|   |   |-- optimal_disjoint_buffer_optimal_disjoint
|   |   |-- optimal_disjoint_optimal
|   |   |-- optimal_disjoint_optimal_disjoint
|   |   |-- optimal_buffer_optimal
|   |   |-- optimal_buffer_optimal_disjoint
|   |   |-- optimal_optimal
|   |   |-- optimal_optimal_disjoint
```

Each test name encodes the source tiling, source disjoint flag, optional buffer indicator, destination tiling, and destination disjoint flag. Only optimal tiling combinations are generated (linear tiling is skipped at [line 838](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L838)).

## Test Families

### Multiplane Image Copy on Transfer Queue

Registered in `createCopyMultiplaneImageTransferQueueTests` at [line 769](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L769). Uses `addFunctionCase` with `testCopies` at [line 485](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L485) as the test function and `checkSupport` at [line 142](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L142) for support checking.

| Family | Description |
|--------|-------------|
| optimal_optimal | Direct image-to-image copy, both non-disjoint |
| optimal_optimal_disjoint | Direct image-to-image copy, dst disjoint |
| optimal_disjoint_optimal | Direct image-to-image copy, src disjoint |
| optimal_disjoint_optimal_disjoint | Direct image-to-image copy, both disjoint |
| optimal_buffer_optimal | Indirect copy through intermediate buffer, both non-disjoint |
| optimal_buffer_optimal_disjoint | Indirect copy through buffer, dst disjoint |
| optimal_disjoint_buffer_optimal | Indirect copy through buffer, src disjoint |
| optimal_disjoint_buffer_optimal_disjoint | Indirect copy through buffer, both disjoint |

## Parameter Dimensions

| Dimension | Values | Source |
|-----------|--------|--------|
| Source Format | 19 multiplane YCbCr formats (8-bit, 10-bit, 12-bit, 16-bit; 420/422/444 subsampling; 2-plane and 3-plane) | [line 777](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L777) |
| Destination Format | Same 19 multiplane formats (only copy-compatible pairs are generated) | [line 817](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L817) |
| Source Tiling | VK_IMAGE_TILING_OPTIMAL only (linear skipped) | [line 838](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L838) |
| Destination Tiling | VK_IMAGE_TILING_OPTIMAL only (linear skipped) | [line 838](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L838) |
| Source Disjoint | true, false | [line 841](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L841) |
| Destination Disjoint | true, false | [line 842](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L842) |
| Intermediate Buffer | true, false | [line 843](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L843) |
| Copy Count | 10 random copies per test | [line 496](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L496) |
| Image Size | 64x64 for YCbCr formats | [line 814](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L814) |

## Support / Feature Requirements

| Requirement | Condition | Source |
|-------------|-----------|--------|
| Dedicated transfer queue | Device must have a transfer queue family | [line 146](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L146) |
| maxImageDimension2D | Image dimensions must not exceed limits | [line 149](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L149) |
| VK_FORMAT_FEATURE_TRANSFER_SRC_BIT / DST_BIT | Format must support transfer operations | [line 131](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L131) |
| VK_FORMAT_FEATURE_DISJOINT_BIT | Required when disjoint flag is used | [line 137](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L137) |
| Image format properties | vkGetPhysicalDeviceImageFormatProperties2 must succeed for the format | [line 87](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L87) |
| Plane compatible format support | When disjoint, each plane's compatible format must also be supported | [line 94](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L94) |
| Copy compatibility | Source and destination formats must be copy-compatible per `isCopyCompatible` | [line 824](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L824) |

## Verification Methods

### testCopies (multiplane image copy)

Uses CPU-side reference comparison with byte-level masking. The `testCopies` function at [line 485](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L485) performs the following:

1. Generates 10 random copy regions respecting transfer queue granularity via `genCopies` at [line 221](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L221)
2. Fills source and destination images with random data (avoiding NaNs) at [line 515](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L515)
3. Executes the copies on the transfer queue
4. Downloads the destination image and computes a reference by manually applying each copy region at [line 673](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L673)
5. Compares result against reference byte-by-byte with optional LSB masking:
   - 6-bit don't-care mask (0xC0) for certain format combinations via `areLsb6BitsDontCare` at [line 724](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L724)
   - 4-bit don't-care mask (0xF0) for certain format combinations via `areLsb4BitsDontCare` at [line 725](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L725)
6. Reports up to 30 errors before stopping at [line 674](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L674)

## Test Principles Observed

- **Transfer queue execution**: All copy operations are submitted to the dedicated transfer queue at [line 559](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L559), verifying that multiplane image copies work correctly on non-universal queue families.
- **Transfer queue granularity**: Random copy regions are aligned to the transfer queue's `minImageTransferGranularity` at [line 262](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L262).
- **Disjoint image support**: Tests both disjoint (separate memory per plane) and non-disjoint allocations at [line 841](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L841), with plane-compatible format support checks at [line 94](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L94).
- **Intermediate buffer path**: The `intermediateBuffer` flag at [line 595](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L595) tests the image-to-buffer-to-image copy path, which is needed when direct image-to-image copies are not possible (e.g., cross-plane format incompatibility).
- **Copy compatibility filtering**: Only format pairs that are copy-compatible per `isCopyCompatible` at [line 436](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L436) are tested, avoiding invalid test configurations.
- **Randomized copy regions**: Copy regions are randomly generated from a deterministic seed at [line 506](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L506), providing coverage of various offset/extent combinations while remaining reproducible.
- **LSB tolerance**: The verification accounts for implementation-defined LSB differences in certain YCbCr format conversions at [line 724](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L724).

## Notes / Uncertainties

- Linear tiling combinations are explicitly skipped at [line 838](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L838) with the comment that linear tiling is not tested for multiplane images on transfer queues. This may be because multiplane linear images are rarely supported.
- The `createFlags` vector at [line 797](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L797) defines various image create flags (MUTABLE_FORMAT, CUBE_COMPATIBLE, etc.) but these flags are not used in the test registration loop. They appear to be defined for reference but not exercised.
- The `getBlockByteSize` function at [line 375](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L375) returns `DE_FATAL` for several multiplane formats, indicating those formats are not supported in the intermediate buffer path.
- Source and destination images are uploaded using the universal queue at [line 545](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L545) but the actual copy operations are performed on the transfer queue at [line 559](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L559). This means the test verifies queue ownership transfer is handled correctly.
