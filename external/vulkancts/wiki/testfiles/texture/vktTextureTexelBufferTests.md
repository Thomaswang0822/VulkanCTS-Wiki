# vktTextureTexelBufferTests.cpp

## Overview

Registers the `texel_buffer` test group under the `texture` category. This group contains Amber-based tests that validate texel buffer operations including sRGB-to-linear conversion, packed format unpacking, and SNORM conversion including clamping of the most negative value.

## Role

Registration file

## Source Code

- [vktTextureTexelBufferTests.cpp](../../../modules/vulkan/texture/vktTextureTexelBufferTests.cpp#L43) - sRGB sub-group creation
- [vktTextureTexelBufferTests.cpp](../../../modules/vulkan/texture/vktTextureTexelBufferTests.cpp#L97) - packed sub-group creation
- [vktTextureTexelBufferTests.cpp](../../../modules/vulkan/texture/vktTextureTexelBufferTests.cpp#L121) - snorm sub-group creation
- [vktTextureTexelBufferTests.cpp](../../../modules/vulkan/texture/vktTextureTexelBufferTests.cpp#L167) - `createTextureTexelBufferTests`

## Registration Hierarchy

```text
texture.texel_buffer
└── uniform
```

The `uniform` group contains 3 sub-groups (srgb, packed, snorm) which are one level below the root expansion.

## Test Families

### uniform

TestCaseGroup created by `createUniformTexelBufferTests` at line 171. Contains three sub-groups of Amber test cases for uniform texel buffer formats:

#### srgb

6 Amber test cases for sRGB formats (lines 43-94):
- `r8g8b8a8_srgb`
- `b8g8r8a8_srgb`
- `b8g8r8_srgb`
- `r8g8b8_srgb`
- `r8g8_srgb`
- `r8_srgb`

Buffer requirement: `VK_FORMAT_FEATURE_UNIFORM_TEXEL_BUFFER_BIT` per format.

Test principle: Validates sRGB-to-linear conversion in texel buffers.

#### packed

7 Amber test cases for packed formats (lines 97-118, non-VulkanSC only):
- `a2b10g10r10-uint-pack32`
- `a2b10g10r10-unorm-pack32`
- `a8b8g8r8-sint-pack32`
- `a8b8g8r8-snorm-pack32`
- `a8b8g8r8-uint-pack32`
- `a8b8g8r8-unorm-pack32`
- `b10g11r11-ufloat-pack32`

Test principle: Validates unpacking of packed formats in texel buffers.

#### snorm

10 Amber test cases for SNORM formats (lines 121-160, non-VulkanSC only). Non-mandatory formats require `VK_FORMAT_FEATURE_UNIFORM_TEXEL_BUFFER_BIT`.

Test principle: Validates SNORM conversion including clamping of the most negative value.

## Parameter Dimensions

None at the registration level. Each sub-group enumerates specific format test cases as individual Amber tests.

## Support/Feature Requirements

- sRGB tests: require `VK_FORMAT_FEATURE_UNIFORM_TEXEL_BUFFER_BIT` for each format.
- packed tests: excluded on VulkanSC builds.
- snorm tests: excluded on VulkanSC builds. Non-mandatory formats require `VK_FORMAT_FEATURE_UNIFORM_TEXEL_BUFFER_BIT`.

## Verification Methods

All tests are Amber-based. No C++-side verification logic.

## Notes

- The `packed` and `snorm` sub-groups are excluded on VulkanSC builds.
- The factory function creates a `TestCaseGroup(testCtx, "texel_buffer")` at line 169.
