# vktImage2dArrayCompatibleTests ([source](../../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp))

## Overview

Tests for VK_IMAGE_CREATE_2D_ARRAY_COMPATIBLE_BIT (VK_KHR_maintenance9). The file verifies that 3D images created with the 2D array compatible flag can be viewed as 2D array images, allowing individual depth slices to be accessed as array layers. Tests cover both 2D view and 3D view types, different layer configurations, and both linear and optimal tiling modes.

## Role of File

Implementation file that registers the `2d_array_compatible` test group and provides complete test implementations. Contains test case class, test instance class, and the factory function that populates the test hierarchy.

## Source Code

- Implementation: [vktImage2dArrayCompatibleTests.cpp](../../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp)
- Header: (header file not shown in provided source)

## Registration Hierarchy

```text
image.2d_array_compatible
├── 0_1_8
�?  ├── linear
�?  �?  ├── 2d
�?  �?  └── 3d
�?  └── optimal
�?      ├── 2d
�?      └── 3d
├── 3_7_16
�?  ├── linear
�?  �?  ├── 2d
�?  �?  └── 3d
�?  └── optimal
�?      ├── 2d
�?      └── 3d
└── 3_4_5
    ├── linear
    �?  ├── 2d
    �?  └── 3d
    └── optimal
        ├── 2d
        └── 3d
```

Evidence:
- `2d_array_compatible` group created by [`createImage2dArrayCompatibleTests()`](../../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L464-L523)
- Layer configuration groups at lines 500-502 with names like `0_1_8`, `3_7_16`, `3_4_5`
- Tiling groups at lines 503-505 with names `linear` and `optimal`
- Image view type groups at lines 506-515 with names `2d` and `3d`

## Test Families

### Layer configuration variants

| Configuration | firstLayer | secondLayer | totalLayers | Description |
|---------------|------------|-------------|-------------|-------------|
| 0_1_8 | 0 | 1 | 8 | First two of eight layers |
| 3_7_16 | 3 | 7 | 16 | Middle layers of sixteen |
| 3_4_5 | 3 | 4 | 5 | Two adjacent layers of five |

### Tiling variants

- **linear**: VK_IMAGE_TILING_LINEAR - Linear tiling for host-accessible images
- **optimal**: VK_IMAGE_TILING_OPTIMAL - Device-optimal tiling

### Image view type variants

- **2d**: VK_IMAGE_VIEW_TYPE_2D - 2D array view with VK_IMAGE_CREATE_2D_VIEW_COMPATIBLE_BIT_EXT (non-VulkanSC only)
- **3d**: VK_IMAGE_VIEW_TYPE_3D - Standard 3D view access

## Parameter Dimensions

| Dimension | Values | Source |
|-----------|--------|--------|
| Image Format | VK_FORMAT_R8G8B8A8_UNORM | [line 121](../../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L121) |
| Image Type | VK_IMAGE_TYPE_3D | [line 136](../../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L136) |
| Image Extent | 32x32x{depthLayers} | [line 122](../../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L122) |
| Copy Extent | 32x32x1 | [line 123](../../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L123) |
| Mip Levels | 1 | [line 139](../../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L139) |
| Sample Count | VK_SAMPLE_COUNT_1_BIT | [line 141](../../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L141) |
| Image Usage | TRANSFER_SRC_BIT, TRANSFER_DST_BIT, SAMPLED_BIT | [line 143-144](../../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L143-144) |

## Support / Feature Requirements

| Requirement | Condition | Source |
|-------------|-----------|--------|
| VK_KHR_maintenance9 | All tests | [line 409](../../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L409) |
| VK_IMAGE_CREATE_2D_ARRAY_COMPATIBLE_BIT | Image format must support with 3D type | [line 415-419](../../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L415-419) |
| VK_EXT_image_2d_view_of_3d | 2D view type tests (non-VulkanSC only) | [line 424](../../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L424) |
| sampler2DViewOf3D feature | 2D view type tests (non-VulkanSC only) | [line 425-426](../../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L425-426) |

## Verification Methods

### Data comparison

Tests verify correct layer access by copying data between layers and comparing:

1. **Source data generation**: Random data filled into source buffer at [lines 188-190](../../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L188-190)
2. **Copy to first layer**: Buffer copied to firstLayer depth slice via `vkCmdCopyBufferToImage` at [lines 273-280](../../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L273-280)
3. **Copy between layers**: Image copy from firstLayer to secondLayer via `vkCmdCopyImage` at [lines 293-300](../../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L293-300)
4. **Shader sampling**: Compute shader samples from secondLayer view, writes to SSBO at [lines 455-456](../../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L455-456)
5. **Copy from second layer**: Result copied to destination buffer via `vkCmdCopyImageToBuffer` at [lines 331-338](../../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L331-338)

**Verification checks**:
- Byte-by-byte comparison of source and destination buffers at [line 355-372](../../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L355-372)
- SSBO verification against scaled source values with epsilon of 1.0 at [lines 373-381](../../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L373-381)

## Test Principles Observed

- **Layer isolation**: Unused layers are transitioned to transfer dst and written with don't-care to ensure isolation
- **Cross-layer copy**: Validates that 3D images with 2D array compatible bit support copy operations between depth slices
- **View type flexibility**: Tests that 3D images can be viewed as both 2D array and 3D views
- **Sampling verification**: Compute shader samples the second layer and writes to both storage buffer and SSBO for dual verification
- **Tiling coverage**: Both linear and optimal tiling tested for format compatibility
- **Layer configuration coverage**: Various first/second/total layer configurations test different slice access patterns

## Notes / Uncertainties

- 2D view type tests are skipped for VulkanSC builds (guarded by `#ifndef CTS_USES_VULKANSC` at line 494)
- The test uses a fixed extent of 32x32 pixels per layer, with depth varying by totalLayers parameter
- SSBO values are verified with epsilon=1.0 against source values scaled by 256 (likely for float precision testing in sampling)
- Random data uses `ycbcr::fillRandomNoNaN` to ensure valid RGBA values
- Transitioning unused layers to transfer dst ensures the implementation doesn't incorrectly access them during tests
