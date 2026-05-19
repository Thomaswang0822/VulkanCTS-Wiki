# [vktImageCompressionTranscodingSupport.cpp](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L1)

## Overview

[`vktImageCompressionTranscodingSupport.cpp`](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L1) is an implementation-heavy Level-3 file for the `image.texel_view_compatible` subtree. It tests the ability to create texel views of compressed images using `VK_IMAGE_CREATE_BLOCK_TEXEL_VIEW_COMPATIBLE_BIT` and `VK_IMAGE_CREATE_MUTABLE_FORMAT_BIT`. The tests verify that compressed formats (ASTC, BC, ETC2) can be viewed as compatible uncompressed formats and that data can be transcoded between compressed and uncompressed representations through shader operations.

## Role of File

- **Role:** implementation-heavy test file
- **Primary source:** [`vktImageCompressionTranscodingSupport.cpp`](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L1)
- **Header:** [`vktImageCompressionTranscodingSupport.hpp`](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.hpp#L1)
- **Registration context:** registered under `image` in [`vktImageTests.cpp`](../../../modules/vulkan/image/vktImageTests.cpp) as `texel_view_compatible` group via [`createImageCompressionTranscodingTests()`](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L3651-L3975)

## Source Code

- Implementation: [vktImageCompressionTranscodingSupport.cpp](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L1)
- Header: [vktImageCompressionTranscodingSupport.hpp](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.hpp#L1)

## Registration Hierarchy

```text
image.texel_view_compatible
├── compute
�?  ├── basic
�?  �?  ├── 1d_image
�?  �?  ├── 2d_image
�?  �?  └── 3d_image
�?  └── extended
�?      ├── 1d_image
�?      ├── 2d_image
�?      └── 3d_image
├── graphic
�?  ├── basic
�?  �?  ├── 1d_image
�?  �?  ├── 2d_image
�?  �?  └── 3d_image
�?  └── extended
�?      ├── 1d_image
�?      ├── 2d_image
�?      └── 3d_image
└── multi_layer_views (non-VulkanSC only)
```

## Test Families

### compute �?Compute shader texel view compatibility tests

Covers the `compute` direct child registered by [`createImageCompressionTranscodingTests()`](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L3805-L3902). These tests use compute shaders to verify that compressed images can be viewed as texel-compatible uncompressed formats.

### graphic �?Graphics shader texel view compatibility tests

Covers the `graphic` direct child registered by [`createImageCompressionTranscodingTests()`](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L3805-L3902). These tests use fragment shaders to verify texel view compatibility through attachment operations and texture sampling.

### multi_layer_views �?Multi-layer view compatibility tests (non-VulkanSC only)

Covers the `multi_layer_views` direct child registered at lines [3907-3971](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L3907-L3971). Requires `VK_KHR_maintenance6` `blockTexelViewCompatibleMultipleLayers` feature. Tests texel view compatibility when using multi-layer image views.

### Operation variants across all shader types

Within each shader type, tests are organized by operation type:
- `image_load` - Load from compressed image view
- `texel_fetch` - Texel fetch operations
- `texture` - Texture sampling
- `image_store` - Store to compressed image view
- `attachment_read` - Fragment shader input attachment read (graphics only)
- `attachment_write` - Fragment shader color attachment write (graphics only)
- `texture_read` - Fragment shader texture read (graphics only)
- `texture_write` - Fragment shader storage image write (graphics only)

## Parameter Dimensions

| Dimension | Observed values / construction | Evidence |
|---|---|---|
| Image type | `IMAGE_TYPE_1D`, `IMAGE_TYPE_2D`, `IMAGE_TYPE_3D` | [Lines 3684-3688](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L3684-L3688) |
| Mipmap mode | `basic` (false), `extended` (true) | [Lines 3659-3672](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L3659-L3672) |
| Image layers | 1 layer for basic; 3 layers for extended with non-3D images | [Lines 3869-3872](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L3869-L3872) |
| Compressed formats (64-bit) | BC1, BC4, ETC2 8-bit formats | [Lines 3737-3742](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L3737-L3742) |
| Compressed formats (128-bit) | BC2/BC3/BC5/BC6/BC7, ETC2 EAC, ASTC formats | [Lines 3744-3766](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L3744-L3766) |
| Uncompressed formats (64-bit) | R16G16B16A16 formats, R32G32 integer | [Lines 3768-3777](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L3768-L3777) |
| Uncompressed formats (128-bit) | R32G32B32A32 formats | [Lines 3779-3785](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L3779-L3785) |
| Image sizes | 64x64 for basic; "unnice" mipmap sizes for extended | [Lines 3869](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L3869), [Lines 3629-3649](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L3629-L3649) |
| Verification format | `VK_FORMAT_R8G8B8A8_UNORM` | [Line 3881](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L3881) |

## Support / Feature Requirements

| Feature / Extension | When it applies | Evidence |
|---|---|---|
| `VK_KHR_maintenance2` | All texel view compatible tests | [Line 3525](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L3525) |
| `textureCompressionBC` | BC1-BC7 compressed formats | [Lines 3549-3551](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L3549-L3551) |
| `textureCompressionETC2` | ETC2 compressed formats | [Lines 3553-3556](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L3553-L3556) |
| `textureCompressionASTC_LDR` | ASTC compressed formats | [Lines 3558-3559](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L3558-L3559) |
| `fragmentStoresAndAtomics` | Storage image operations | Checked in test instance creation |
| `blockTexelViewCompatibleMultipleLayers` (maintenance6) | Multi-layer view tests only | [Lines 3571-3576](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L3571-L3576) |

## Verification Methods

- **Data comparison:** Generated test data is written to uncompressed source images, transcoded through shader operations, and compared with the original data to verify bit-exact preservation
- **ASTC error color tolerance:** Special comparison mode allows for ASTC LDR/HDR error color mismatches with quality warning instead of failure ([Lines 148-218](../../../modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp#L148-L218))
- **Compressed format validation:** Verifies that formats match expected bit depths between view and image formats

## Test Principles Observed

- **Format matching by bitness:** Tests match compressed and uncompressed formats by total bits (64-bit or 128-bit groups) to ensure compatible texel sizes
- **Shader compatibility:** Compute shader tests cover image_load, texel_fetch, texture, and image_store operations; graphics tests cover attachment and texture operations
- **Mipmap handling:** Extended mipmap tests verify behavior with multiple mip levels while respecting block size boundaries
- **Multi-layer views:** Special tests verify block texel view compatibility with multiple array layers (requires maintenance6 extension)

## Notes / Uncertainties

- Float formats are excluded from uncompressed format lists because they cannot preserve all possible values (NaN, INF, denorm) when transcoding
- Some formats are commented out due to tcu::TextureFormat limitations
- Multi-layer view tests are only available on non-VulkanSC builds
- The verification uses R8G8B8A8_UNORM as the reference format for comparing transcoded results
