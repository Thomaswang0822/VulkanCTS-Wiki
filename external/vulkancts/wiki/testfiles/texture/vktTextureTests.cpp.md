# vktTextureTests.cpp

## Overview

Root registration file for the texture category. Creates the top-level `texture` test group and dispatches to all topic-group registration functions.

## Role

Registration / dispatcher file. Does not implement any test logic directly.

## Source Code

- [vktTextureTests.cpp](../../../modules/vulkan/texture/vktTextureTests.cpp)
- Header: [vktTextureTests.hpp](../../../modules/vulkan/texture/vktTextureTests.hpp)

## Registration Hierarchy

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
├── subgroup_lod (non-VulkanSC only)
├── conversion (non-VulkanSC only)
├── texel_buffer (non-VulkanSC only)
├── multisample (non-VulkanSC only)
└── texel_offset (non-VulkanSC only)
```

Source: [createTextureTests](../../../modules/vulkan/texture/vktTextureTests.cpp#L48-L67).

## Test Families

### filtering

2D, cube, 2D array, and 3D texture filtering with various filter modes, wrap modes, and formats. Includes unnormalized coordinate tests and cubic filtering. Registered by [createTextureFilteringTests](../../../modules/vulkan/texture/vktTextureFilteringTests.cpp#L2079).

### mipmap

2D, cube, and 3D mipmap filtering with LOD controls (bias, min/max LOD, base/max level) and image view min LOD extension. Registered by [createTextureMipmappingTests](../../../modules/vulkan/texture/vktTextureMipmapTests.cpp#L4198).

### explicit_lod

2D texture filtering with explicit LOD (textureLod) and explicit gradients (textureGrad). Per-sample mathematical verification. Registered by [createExplicitLodTests](../../../modules/vulkan/texture/vktTextureFilteringExplicitLodTests.cpp#L1411).

### shadow

Depth comparison (shadow) sampling across 2D, cube, 2D array, 1D, 1D array, and cube array texture types with multiple compare operations and depth formats. Registered by [createTextureShadowTests](../../../modules/vulkan/texture/vktTextureShadowTests.cpp#L2080).

### filtering_anisotropy

Anisotropic filtering tests with basic, mipmap, and single-level variants. Self-referential verification comparing anisotropic vs isotropic output. Registered by [createFilteringAnisotropyTests](../../../modules/vulkan/texture/vktTextureFilteringAnisotropyTests.cpp#L207).

### compressed

2D compressed texture (ETC2, EAC, ASTC, BC) sampling with graphics and compute shader variants. Flat leaf test cases with naming pattern `{format}_2d_{size}{backingMode}`. Registered by [createTextureCompressedFormatTests](../../../modules/vulkan/texture/vktTextureCompressedFormatTests.cpp#L721).

### compressed_3D

3D compressed texture sampling across multiple Z-slices. Includes ASTC 3D formats (non-VulkanSC). Flat leaf test cases with naming pattern `{format}_3d_{size}{backingMode}`. Registered by [create3DTextureCompressedFormatTests](../../../modules/vulkan/texture/vktTextureCompressedFormatTests.cpp#L726).

### swizzle

VkComponentMapping (component swizzle) and texture coordinate swizzle tests across color, depth, and stencil formats. Registered by [createTextureSwizzleTests](../../../modules/vulkan/texture/vktTextureSwizzleTests.cpp#L651).

### subgroup_lod

Subgroup LOD consistency tests using textureLod, textureGrad, and texelFetch. Amber-based. Non-VulkanSC only. Registered by [createTextureSubgroupLodTests](../../../modules/vulkan/texture/vktTextureSubgroupLodTests.cpp#L59).

### conversion

Format conversion tests: UFLOAT negative values, SNORM clamping, and SNORM linear filtering clamping. Non-VulkanSC only. Registered by [createTextureConversionTests](../../../modules/vulkan/texture/vktTextureConversionTests.cpp#L438).

### texel_buffer

Uniform texel buffer tests with sRGB, packed, and SNORM formats. Non-VulkanSC only. Registered by [createTextureTexelBufferTests](../../../modules/vulkan/texture/vktTextureTexelBufferTests.cpp#L167).

### multisample

Multisample texture atomic operations and invalid sample index tests. Non-VulkanSC only. Registered by [createTextureMultisampleTests](../../../modules/vulkan/texture/vktTextureMultisampleTests.cpp#L149).

### texel_offset

Texel offset texture fetch test. Amber-based. Non-VulkanSC only. Registered by [createTextureTexelOffsetTests](../../../modules/vulkan/texture/vktTextureTexelOffsetTests.cpp#L36).

## VulkanSC Conditional Registration

Groups 9–13 (`subgroup_lod`, `conversion`, `texel_buffer`, `multisample`, `texel_offset`) are guarded by `#ifndef CTS_USES_VULKANSC` at [line 60](../../../modules/vulkan/texture/vktTextureTests.cpp#L60). On VulkanSC builds, these groups are not registered.
