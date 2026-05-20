# vktTextureFilteringAnisotropyTests.cpp

## Overview

Registers the `filtering_anisotropy` test group under the `texture` category. This group contains tests that validate anisotropic texture filtering by comparing GPU anisotropic output against the GPU's own isotropic output, using a perspective-tilted quad to induce anisotropy.

## Role

Implementation file

## Source Code

- [vktTextureFilteringAnisotropyTests.cpp](../../../modules/vulkan/texture/vktTextureFilteringAnisotropyTests.cpp#L55) - `AnisotropyParams` struct
- [vktTextureFilteringAnisotropyTests.cpp](../../../modules/vulkan/texture/vktTextureFilteringAnisotropyTests.cpp#L91) - maxAnisotropy clamping logic
- [vktTextureFilteringAnisotropyTests.cpp](../../../modules/vulkan/texture/vktTextureFilteringAnisotropyTests.cpp#L106) - `FilteringAnisotropyInstance::iterate()`
- [vktTextureFilteringAnisotropyTests.cpp](../../../modules/vulkan/texture/vktTextureFilteringAnisotropyTests.cpp#L193) - `samplerAnisotropy` feature check
- [vktTextureFilteringAnisotropyTests.cpp](../../../modules/vulkan/texture/vktTextureFilteringAnisotropyTests.cpp#L207) - `createFilteringAnisotropyTests`

## Registration Hierarchy

```text
texture.filtering_anisotropy
├── basic
├── single_level
└── mipmap
```

## Test Families

### basic

Basic anisotropy filtering tests (added at line 252). Tests anisotropic filtering with standard min/mag filter combinations on a 128x128 `VK_FORMAT_R8G8B8A8_UNORM` texture.

### single_level

Anisotropy filtering on a single-mip-level texture (added at line 285). Tests anisotropic filtering behavior when the texture has only one mip level, using a 128x128 `VK_FORMAT_R8G8B8A8_UNORM` texture.

### mipmap

Anisotropy filtering with mipmap minification filters (added at line 319). Tests anisotropic filtering with mipmap-capable min filters on a 128x128 `VK_FORMAT_R8G8B8A8_UNORM` texture.

## Parameter Dimensions

- **maxAnisotropy**: {2.0, 4.0, 8.0, 10000.0} (test names: `anisotropy_2`, `anisotropy_4`, `anisotropy_8`, `anisotropy_max`)
- **minFilter** (basic/single_level): {NEAREST, LINEAR}
- **minFilter** (mipmap): {NEAREST_MIPMAP_NEAREST, NEAREST_MIPMAP_LINEAR, LINEAR_MIPMAP_NEAREST, LINEAR_MIPMAP_LINEAR}
- **magFilter**: {NEAREST, LINEAR}
- **useCompute**: {false, true} (graphics + compute variants)
- **Texture**: 128x128 `VK_FORMAT_R8G8B8A8_UNORM`

## Support/Feature Requirements

- Requires `samplerAnisotropy` feature (lines 193-199).
- `maxAnisotropy` is clamped to the device's `maxSamplerAnisotropy` limit (lines 91-94).

## Verification Methods

Two-phase comparison in `FilteringAnisotropyInstance::iterate()` (lines 106-166):

1. **Fuzzy similarity check**: `tcu::fuzzyCompare` with threshold 0.05, comparing anisotropic (maxAnisotropy) vs isotropic (1.0) rendering.
2. **Difference detection** (when neither minFilter nor magFilter is plain NEAREST): `tcu::floatThresholdCompare` with `Vec4(0.02f)`, expecting anisotropic output to differ from isotropic output.

## Notes

- Self-referential verification: compares GPU's anisotropic output against its own isotropic output rather than a CPU reference.
- Uses a perspective-tilted quad to induce anisotropy.
- Every test has both graphics and compute variants.
- The `AnisotropyParams` struct (lines 55-76) inherits `ReferenceParams` and adds `maxAnisotropy`, `minFilter`, `magFilter`, `singleLevelImage`, `mipMap`, and `useCompute`.
