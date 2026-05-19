# [vktImageSampleCompressedTextureTests.cpp](../../../modules/vulkan/image/vktImageSampleCompressedTextureTests.cpp#L1)

## Overview

[`vktImageSampleCompressedTextureTests.cpp`](../../../modules/vulkan/image/vktImageSampleCompressedTextureTests.cpp#L1) implements the `image.sample_texture` subgroup registered by the image module. The file tests sampling from images with block-compressed formats (BC1/BC3) through image views with compatible uncompressed formats, verifying that the extended usage and mutable format features work correctly.

## Role of File

Implementation-heavy test file for the `image.sample_texture` subgroup.

## Source Code

- Primary source: [vktImageSampleCompressedTextureTests.cpp](../../../modules/vulkan/image/vktImageSampleCompressedTextureTests.cpp#L1)
- Parent-category registration: `createImageSampleDrawnTextureTests()` called from image module

## Registration Hierarchy

```text
image.sample_texture
├── 128_bit_compressed_format
├── 128_bit_compressed_format_cubemap
├── 128_bit_compressed_format_two_samplers
├── 128_bit_compressed_format_two_samplers_cubemap
├── 64_bit_compressed_format
├── 64_bit_compressed_format_cubemap
├── 64_bit_compressed_format_two_samplers
└── 64_bit_compressed_format_two_samplers_cubemap
```

Evidence:
- `sample_texture` group created at [`createImageSampleDrawnTextureTests()`](../../../modules/vulkan/image/vktImageSampleCompressedTextureTests.cpp#L888)
- Eight test cases added at lines 890-912

## Test Families

### 64_bit_compressed_format �?BC1 compressed texture sampling

Tests sampling a BC1_RGB_UNORM_BLOCK compressed image through a VK_FORMAT_R32G32_UINT image view. The test:
1. Compute shader fills storage image with compressed pure blue values
2. Fragment shader samples via uncompressed image view and renders to target
3. Verifies rendered image is pure blue

Validation: Compare result against pure blue reference image at [`vktImageSampleCompressedTextureTests.cpp#L680-682`](../../../modules/vulkan/image/vktImageSampleCompressedTextureTests.cpp#L680).

### 64_bit_compressed_format_two_samplers �?BC1 with dual samplers

Same as above but uses two samplers:
1. First pass: compute writes compressed blue, fragment samples with sampler2 (compressed format) - draws garbage
2. Second pass: fragment samples with sampler (uncompressed format) - draws correct blue

Verifies both sampler paths work correctly.

### 128_bit_compressed_format �?BC3 compressed texture sampling

Same pattern as 64-bit tests but uses BC3_UNORM_BLOCK with VK_FORMAT_R32G32B32A32_UINT view.

### {format}_cubemap variants �?Cubemap compressed texture sampling

Same as above but creates a cubemap image (6 layers) and tests sampling each face:
1. Renders to each cubemap face separately
2. Samples the rendered faces
3. Verifies all faces contain pure blue (R=0, B>0, A>0) at [`vktImageSampleCompressedTextureTests.cpp#L660-669`](../../../modules/vulkan/image/vktImageSampleCompressedTextureTests.cpp#L660)

## Test Parameters

| Test | Image Format | View Format | Two Samplers | Cubemap |
|------|-------------|-------------|--------------|---------|
| 64_bit_compressed_format | VK_FORMAT_BC1_RGB_UNORM_BLOCK | VK_FORMAT_R32G32_UINT | No | No |
| 64_bit_compressed_format_two_samplers | VK_FORMAT_BC1_RGB_UNORM_BLOCK | VK_FORMAT_R32G32_UINT | Yes | No |
| 128_bit_compressed_format | VK_FORMAT_BC3_UNORM_BLOCK | VK_FORMAT_R32G32B32A32_UINT | No | No |
| 128_bit_compressed_format_two_samplers | VK_FORMAT_BC3_UNORM_BLOCK | VK_FORMAT_R32G32B32A32_UINT | Yes | No |
| 64_bit_compressed_format_cubemap | VK_FORMAT_BC1_RGB_UNORM_BLOCK | VK_FORMAT_R32G32_UINT | No | Yes |
| 64_bit_compressed_format_two_samplers_cubemap | VK_FORMAT_BC1_RGB_UNORM_BLOCK | VK_FORMAT_R32G32_UINT | Yes | Yes |
| 128_bit_compressed_format_cubemap | VK_FORMAT_BC3_UNORM_BLOCK | VK_FORMAT_R32G32B32A32_UINT | No | Yes |
| 128_bit_compressed_format_two_samplers_cubemap | VK_FORMAT_BC3_UNORM_BLOCK | VK_FORMAT_R32G32B32A32_UINT | Yes | Yes |

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Image dimensions | 80x80 pixels at [`vktImageSampleCompressedTextureTests.cpp#L77-78`](../../../modules/vulkan/image/vktImageSampleCompressedTextureTests.cpp#L77) |
| Compressed block sizes | BC1: 8x8, BC3: 8x8 at [`vktImageSampleCompressedTextureTests.cpp#L288`](../../../modules/vulkan/image/vktImageSampleCompressedTextureTests.cpp#L288) |
| Cubemap faces | 6 faces |
| Test colors | Pure red (BC1/BC3 compressed), Pure blue (BC1/BC3 compressed) |
| Vertex buffer size | 100KB at [`vktImageSampleCompressedTextureTests.cpp#L76`](../../../modules/vulkan/image/vktImageSampleCompressedTextureTests.cpp#L76) |

## Support / Feature Requirements

- `VK_KHR_maintenance2` required for `VK_IMAGE_CREATE_MUTABLE_FORMAT_BIT`, `VK_IMAGE_CREATE_EXTENDED_USAGE_BIT`, and `VK_IMAGE_CREATE_BLOCK_TEXEL_VIEW_COMPATIBLE_BIT` via [`SampleDrawnTextureTest::checkSupport()`](../../../modules/vulkan/image/vktImageSampleCompressedTextureTests.cpp#L735-737)
- Format must support the combined usage flags (STORAGE, SAMPLED, TRANSFER) with the creation flags at [`vktImageSampleCompressedTextureTests.cpp#L739-752`](../../../modules/vulkan/image/vktImageSampleCompressedTextureTests.cpp#L739)

## Verification Methods

- Graphics rendering with compute pre-pass for 2D tests
- Reference image comparison with 0.01 float threshold at [`vktImageSampleCompressedTextureTests.cpp#L680-682`](../../../modules/vulkan/image/vktImageSampleCompressedTextureTests.cpp#L680)
- Cubemap face validation: R=0, B>0, A>0 for all pixels at [`vktImageSampleCompressedTextureTests.cpp#L660-669`](../../../modules/vulkan/image/vktImageSampleCompressedTextureTests.cpp#L660)
- Image logged to test output for visual verification

## Test Principles Observed

- Test both 64-bit (BC1) and 128-bit (BC3) compressed formats
- Verify image view format override works via `VkImageViewUsageCreateInfo`
- Test cubemap variants covering all 6 faces
- Two-sampler tests verify both compressed and uncompressed sampling paths
- Graphics pipeline is used for actual sampling validation

## Notes / Uncertainties

- Only BC1 and BC3 formats are tested; other compressed formats (BC2, BC4-BC7, ASTC, ETC) are not covered
- Fixed image size of 80x80 may not test boundary conditions for compressed blocks
- The test requires the compressed format to support STORAGE usage, which may limit device compatibility
- Cubemap tests create separate image views for each face rather than using a single cube view
- Result logging for cubemaps shows a single 2D image rather than all 6 faces clearly
