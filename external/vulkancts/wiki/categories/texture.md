# Texture Tests

## Overview

The [`texture`](../../modules/vulkan/texture/vktTextureTests.cpp#L48) category tests Vulkan texture sampling operations across all texture types (1D, 2D, 3D, cube, and their array variants), covering filtering, mipmapping, shadow comparison, anisotropic filtering, compressed format decoding, swizzle, format conversion, texel buffers, multisample textures, and subgroup LOD consistency. The category verifies that GPU texture sampling matches CPU-computed reference results using a variety of verification strategies.

## Registration Entry Point

The category is rooted in [`createTextureTests()`](../../modules/vulkan/texture/vktTextureTests.cpp#L48), which creates 13 direct children under `texture`:

```text
texture
├── filtering
├── mipmap
├── explicit_lod
├── shadow
├── filtering_anisotropy
├── compressed
├── compressed_3D
├── swizzle
├── subgroup_lod                  (VK only)
├── conversion                    (VK only)
├── texel_buffer                  (VK only)
├── multisample                   (VK only)
└── texel_offset                  (VK only)
```

Source: [`createTextureTests()`](../../modules/vulkan/texture/vktTextureTests.cpp#L48-L67).

## Subgroup Structure

| Group | Factory Function | Source File | VKSC | Level-3 doc |
|---|---|---|---|---|
| `filtering` | `createTextureFilteringTests` | [`vktTextureFilteringTests.cpp`](../../modules/vulkan/texture/vktTextureFilteringTests.cpp#L2079) | Available | [vktTextureFilteringTests.cpp](../testfiles/texture/vktTextureFilteringTests.cpp.md) |
| `mipmap` | `createTextureMipmappingTests` | [`vktTextureMipmapTests.cpp`](../../modules/vulkan/texture/vktTextureMipmapTests.cpp#L4198) | Available | [vktTextureMipmapTests.cpp](../testfiles/texture/vktTextureMipmapTests.cpp.md) |
| `explicit_lod` | `createExplicitLodTests` | [`vktTextureFilteringExplicitLodTests.cpp`](../../modules/vulkan/texture/vktTextureFilteringExplicitLodTests.cpp#L1411) | Available | [vktTextureFilteringExplicitLodTests.cpp](../testfiles/texture/vktTextureFilteringExplicitLodTests.cpp.md) |
| `shadow` | `createTextureShadowTests` | [`vktTextureShadowTests.cpp`](../../modules/vulkan/texture/vktTextureShadowTests.cpp#L2080) | Available | [vktTextureShadowTests.cpp](../testfiles/texture/vktTextureShadowTests.cpp.md) |
| `filtering_anisotropy` | `createFilteringAnisotropyTests` | [`vktTextureFilteringAnisotropyTests.cpp`](../../modules/vulkan/texture/vktTextureFilteringAnisotropyTests.cpp#L207) | Available | [vktTextureFilteringAnisotropyTests.cpp](../testfiles/texture/vktTextureFilteringAnisotropyTests.cpp.md) |
| `compressed` | `createTextureCompressedFormatTests` | [`vktTextureCompressedFormatTests.cpp`](../../modules/vulkan/texture/vktTextureCompressedFormatTests.cpp#L721) | Available | [vktTextureCompressedFormatTests.cpp](../testfiles/texture/vktTextureCompressedFormatTests.cpp.md) |
| `compressed_3D` | `create3DTextureCompressedFormatTests` | [`vktTextureCompressedFormatTests.cpp`](../../modules/vulkan/texture/vktTextureCompressedFormatTests.cpp#L726) | Available | [vktTextureCompressedFormatTests.cpp](../testfiles/texture/vktTextureCompressedFormatTests.cpp.md) |
| `swizzle` | `createTextureSwizzleTests` | [`vktTextureSwizzleTests.cpp`](../../modules/vulkan/texture/vktTextureSwizzleTests.cpp#L651) | Available | [vktTextureSwizzleTests.cpp](../testfiles/texture/vktTextureSwizzleTests.cpp.md) |
| `subgroup_lod` | `createTextureSubgroupLodTests` | [`vktTextureSubgroupLodTests.cpp`](../../modules/vulkan/texture/vktTextureSubgroupLodTests.cpp#L59) | Excluded | [vktTextureSubgroupLodTests.cpp](../testfiles/texture/vktTextureSubgroupLodTests.cpp.md) |
| `conversion` | `createTextureConversionTests` | [`vktTextureConversionTests.cpp`](../../modules/vulkan/texture/vktTextureConversionTests.cpp#L438) | Excluded | [vktTextureConversionTests.cpp](../testfiles/texture/vktTextureConversionTests.cpp.md) |
| `texel_buffer` | `createTextureTexelBufferTests` | [`vktTextureTexelBufferTests.cpp`](../../modules/vulkan/texture/vktTextureTexelBufferTests.cpp#L167) | Excluded | [vktTextureTexelBufferTests.cpp](../testfiles/texture/vktTextureTexelBufferTests.cpp.md) |
| `multisample` | `createTextureMultisampleTests` | [`vktTextureMultisampleTests.cpp`](../../modules/vulkan/texture/vktTextureMultisampleTests.cpp#L149) | Excluded | [vktTextureMultisampleTests.cpp](../testfiles/texture/vktTextureMultisampleTests.cpp.md) |
| `texel_offset` | `createTextureTexelOffsetTests` | [`vktTextureTexelOffsetTests.cpp`](../../modules/vulkan/texture/vktTextureTexelOffsetTests.cpp#L36) | Excluded | [vktTextureTexelOffsetTests.cpp](../testfiles/texture/vktTextureTexelOffsetTests.cpp.md) |

## File Inventory

### Registration Files

| File | Role |
|---|---|
| [`vktTextureTests.cpp`](../../modules/vulkan/texture/vktTextureTests.cpp#L1) | Root dispatcher; creates 13 direct children |

### Implementation Files

| File | Group(s) |
|---|---|
| [`vktTextureFilteringTests.cpp`](../../modules/vulkan/texture/vktTextureFilteringTests.cpp#L1) | `filtering` |
| [`vktTextureMipmapTests.cpp`](../../modules/vulkan/texture/vktTextureMipmapTests.cpp#L1) | `mipmap` |
| [`vktTextureFilteringExplicitLodTests.cpp`](../../modules/vulkan/texture/vktTextureFilteringExplicitLodTests.cpp#L1) | `explicit_lod` |
| [`vktTextureShadowTests.cpp`](../../modules/vulkan/texture/vktTextureShadowTests.cpp#L1) | `shadow` |
| [`vktTextureFilteringAnisotropyTests.cpp`](../../modules/vulkan/texture/vktTextureFilteringAnisotropyTests.cpp#L1) | `filtering_anisotropy` |
| [`vktTextureCompressedFormatTests.cpp`](../../modules/vulkan/texture/vktTextureCompressedFormatTests.cpp#L1) | `compressed`, `compressed_3D` |
| [`vktTextureSwizzleTests.cpp`](../../modules/vulkan/texture/vktTextureSwizzleTests.cpp#L1) | `swizzle` |
| [`vktTextureSubgroupLodTests.cpp`](../../modules/vulkan/texture/vktTextureSubgroupLodTests.cpp#L1) | `subgroup_lod` |
| [`vktTextureConversionTests.cpp`](../../modules/vulkan/texture/vktTextureConversionTests.cpp#L1) | `conversion` |
| [`vktTextureTexelBufferTests.cpp`](../../modules/vulkan/texture/vktTextureTexelBufferTests.cpp#L1) | `texel_buffer` |
| [`vktTextureMultisampleTests.cpp`](../../modules/vulkan/texture/vktTextureMultisampleTests.cpp#L1) | `multisample` |
| [`vktTextureTexelOffsetTests.cpp`](../../modules/vulkan/texture/vktTextureTexelOffsetTests.cpp#L1) | `texel_offset` |

### Utility Files (no Level-3 docs)

| File | Purpose |
|---|---|
| [`vktTextureTestUtil.cpp`](../../modules/vulkan/texture/vktTextureTestUtil.cpp#L1) | Shared texture test infrastructure (TextureRenderer, test case classes, program definitions) |
| [`vktSampleVerifier.cpp`](../../modules/vulkan/texture/vktSampleVerifier.cpp#L1) | Per-sample mathematical verification for explicit LOD tests |
| [`vktSampleVerifierUtil.cpp`](../../modules/vulkan/texture/vktSampleVerifierUtil.cpp#L1) | Utility functions for sample verification |

## Cross-File Recurring Themes

### Texture Type Coverage

Most test groups cover multiple texture types with a consistent structure:

| Texture Type | filtering | mipmap | shadow | swizzle | compressed |
|---|---|---|---|---|---|
| 1D | — | — | ✓ | — | — |
| 2D | ✓ | ✓ | ✓ | ✓ | ✓ |
| 3D | ✓ | ✓ | — | — | ✓ |
| Cube | ✓ | ✓ | ✓ | — | — |
| 2D Array | ✓ | — | ✓ | — | — |
| 1D Array | — | — | ✓ | — | — |
| Cube Array | — | — | ✓ | — | — |

### Graphics + Compute Dual Pipeline

Nearly every test group generates both graphics pipeline and compute pipeline variants. Compute variants are typically named with a `_compute` suffix. This pattern appears in filtering, mipmap, explicit_lod, filtering_anisotropy, compressed, compressed_3D, swizzle, and conversion tests.

### Sparse Backing Mode

Many test groups offer both regular and sparse backing modes for texture memory. Sparse variants are excluded on VulkanSC. This pattern appears in filtering, shadow, compressed, compressed_3D, and swizzle tests.

## Cross-File Recurring Parameter Dimensions

| Dimension | Typical Values | Used In |
|---|---|---|
| Filter modes | nearest, linear, mipmap variants, cubic | filtering, mipmap, shadow, explicit_lod, filtering_anisotropy |
| Wrap modes | repeat, mirrored_repeat, clamp_to_edge, clamp_to_border, mirror_clamp_to_edge | filtering, mipmap |
| Texture sizes | POT, NPOT, various dimensions | filtering, mipmap, explicit_lod, compressed, swizzle |
| Formats | UNORM, SNORM, SFLOAT, SRGB, depth, compressed | filtering, shadow, compressed, swizzle, conversion, texel_buffer |
| Compare ops | less_or_equal, greater_or_equal, less, greater, equal, not_equal, always, never | shadow |
| Component mappings | IDENTITY, ZERO, ONE, R, G, B, A | swizzle |

## Cross-File Recurring Support Requirements

| Requirement | Extension/Feature | Used In |
|---|---|---|
| Anisotropic filtering | `samplerAnisotropy` | filtering_anisotropy |
| Cubic filtering | `VK_EXT_filter_cubic` | filtering |
| Mirror clamp to edge | `VK_KHR_sampler_mirror_clamp_to_edge` | filtering |
| Non-seamless cube map | `VK_EXT_non_seamless_cube_map` | filtering, shadow |
| Image view min LOD | `VK_EXT_image_view_min_lod` | mipmap |
| Robustness2 | `VK_EXT_robustness2` | mipmap (gather minLod) |
| Depth comparison | `VK_FORMAT_FEATURE_2_SAMPLED_IMAGE_DEPTH_COMPARISON_BIT_KHR` | shadow |
| Compressed formats | `textureCompressionETC2`, `textureCompressionASTC_LDR`, `textureCompressionBC` | compressed, compressed_3D |
| ASTC 3D | `VK_EXT_texture_compression_astc_3d` | compressed_3D |
| Depth/stencil swizzle | `VK_KHR_maintenance5` + `depthStencilSwizzleOneSupport` | swizzle |
| RGBA10x6 without YCbCr | `VK_EXT_rgba10x6_formats` | filtering |
| Storage image multisample | `shaderStorageImageMultisample` | multisample |
| Sparse binding | `sparseBinding` + `sparseResidencyImage2D` | filtering, shadow, compressed, swizzle |

## Cross-File Recurring Verification Methods

| Method | Description | Used In |
|---|---|---|
| Image comparison (two-tier) | High-precision `verifyTextureResult()` with low-precision fallback | filtering |
| Image comparison (lookup diff) | `computeTextureLookupDiff()` with grid-based verification | mipmap |
| Per-sample mathematical | `SampleVerifier` with device-aware precision | explicit_lod |
| PCF comparison (two-tier) | `computeTextureCompareDiff()` with high/low precision tiers | shadow |
| Self-referential comparison | Anisotropic vs isotropic output comparison | filtering_anisotropy |
| Neighborhood search | `validateTexture()` with coordinate tolerance | compressed |
| Direct pixel comparison | `compareImages()` after software swizzle application | swizzle |
| Pixel + out-of-range | Lookup diff plus [-1,+1] range check | conversion (snorm_clamp_linear) |
| Amber delegation | All verification in Amber scripts | subgroup_lod, texel_buffer, multisample, texel_offset, conversion (partial) |

## Notes

- The `compressed` and `compressed_3D` groups both originate from [`vktTextureCompressedFormatTests.cpp`](../../modules/vulkan/texture/vktTextureCompressedFormatTests.cpp#L1) and have flat leaf test cases (no sub-groups). Test names encode all parameter dimensions.
- The `explicit_lod` group uses a fundamentally different verification approach (per-sample mathematical verification via `SampleVerifier`) compared to the image-level comparison used by filtering and mipmap tests.
- Five groups (`subgroup_lod`, `conversion`, `texel_buffer`, `multisample`, `texel_offset`) are excluded on VulkanSC builds via `#ifndef CTS_USES_VULKANSC` guards.
- The `vktTextureTestUtil.cpp` utility file provides shared infrastructure (`TextureRenderer`, `TextureTestCase`, program definitions) used across multiple implementation files.
