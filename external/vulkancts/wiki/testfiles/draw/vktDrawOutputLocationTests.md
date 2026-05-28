# output_location

## Overview

Fragment output location tests that verify correct behavior when writing to fragment output attachments with various formats and location configurations. The tests exercise two scenarios: array-style output across multiple formats with different precision and component counts, and shuffle-style output where input/output locations are remapped.

## Role

Validates that fragment shader output locations are correctly mapped to color attachments. Covers format-specific output writing (packed formats, multi-component formats) and location shuffling where the output location assignment differs from the input layout. Ensures implementations handle `layout(location = N)` correctly across diverse format and precision combinations.

## Source Code

- [vktDrawOutputLocationTests.cpp](../../../modules/vulkan/draw/vktDrawOutputLocationTests.cpp)

## Registration Hierarchy

```text
draw.renderpass.output_location
├── array
└── shuffle
```

## Test Families

### array — Fragment output location array tests

Tests fragment output writing to array-style attachments across a variety of formats and precision levels. Each test case renders using an amber shader pipeline and validates the output image.

Amber test cases (data directory: `draw/output_location/array`):

| Test Case | Format | Precision | Output Type |
|-----------|--------|-----------|-------------|
| b10g11r11-ufloat-pack32-highp | B10G11R11_UFLOAT_PACK32 | highp | vec3 (3-component) |
| b10g11r11-ufloat-pack32-highp-output-float | B10G11R11_UFLOAT_PACK32 | highp | float |
| b10g11r11-ufloat-pack32-highp-output-vec2 | B10G11R11_UFLOAT_PACK32 | highp | vec2 |
| b10g11r11-ufloat-pack32-mediump | B10G11R11_UFLOAT_PACK32 | mediump | vec3 (3-component) |
| b10g11r11-ufloat-pack32-mediump-output-float | B10G11R11_UFLOAT_PACK32 | mediump | float |
| b10g11r11-ufloat-pack32-mediump-output-vec2 | B10G11R11_UFLOAT_PACK32 | mediump | vec2 |
| b8g8r8a8-unorm-highp | B8G8R8A8_UNORM | highp | vec4 |
| b8g8r8a8-unorm-highp-output-vec2 | B8G8R8A8_UNORM | highp | vec2 |
| b8g8r8a8-unorm-highp-output-vec3 | B8G8R8A8_UNORM | highp | vec3 |
| b8g8r8a8-unorm-mediump | B8G8R8A8_UNORM | mediump | vec4 |
| b8g8r8a8-unorm-mediump-output-vec2 | B8G8R8A8_UNORM | mediump | vec2 |
| b8g8r8a8-unorm-mediump-output-vec3 | B8G8R8A8_UNORM | mediump | vec3 |
| r16g16-sfloat-highp | R16G16_SFLOAT | highp | vec2 |
| r16g16-sfloat-highp-output-float | R16G16_SFLOAT | highp | float |
| r16g16-sfloat-mediump | R16G16_SFLOAT | mediump | vec2 |
| r16g16-sfloat-mediump-output-float | R16G16_SFLOAT | mediump | float |
| r32g32b32a32-sfloat-highp | R32G32B32A32_SFLOAT | highp | vec4 |
| r32g32b32a32-sfloat-highp-output-vec2 | R32G32B32A32_SFLOAT | highp | vec2 |
| r32g32b32a32-sfloat-highp-output-vec3 | R32G32B32A32_SFLOAT | highp | vec3 |
| r32g32b32a32-sfloat-mediump | R32G32B32A32_SFLOAT | mediump | vec4 |
| r32g32b32a32-sfloat-mediump-output-vec2 | R32G32B32A32_SFLOAT | mediump | vec2 |
| r32g32b32a32-sfloat-mediump-output-vec3 | R32G32B32A32_SFLOAT | mediump | vec3 |
| r32-sfloat-highp | R32_SFLOAT | highp | float |
| r32-sfloat-mediump | R32_SFLOAT | mediump | float |
| r8g8-uint-highp | R8G8_UINT | highp | uvec2 |
| r8g8-uint-highp-output-uint | R8G8_UINT | highp | uint |
| r8g8-uint-mediump | R8G8_UINT | mediump | uvec2 |
| r8g8-uint-mediump-output-uint | R8G8_UINT | mediump | uint |

Source: [vktDrawOutputLocationTests.cpp#L57-L101](../../../modules/vulkan/draw/vktDrawOutputLocationTests.cpp#L57-L101)

### shuffle — Fragment output location shuffle tests

Tests fragment output where the output location assignment is shuffled relative to the input layout, verifying that implementations correctly handle non-trivial location mappings.

Amber test cases (data directory: `draw/output_location/shuffle`):

| Test Case | Description |
|-----------|-------------|
| inputs-outputs | Basic input-to-output location shuffle |
| inputs-outputs-mod | Modified input-to-output location shuffle with stride constraints |

Source: [vktDrawOutputLocationTests.cpp#L103-L119](../../../modules/vulkan/draw/vktDrawOutputLocationTests.cpp#L103-L119)

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Format | B10G11R11_UFLOAT_PACK32, B8G8R8A8_UNORM, R16G16_SFLOAT, R32G32B32A32_SFLOAT, R32_SFLOAT, R8G8_UINT | Color attachment format |
| Precision | highp, mediump | Shader precision qualifier |
| Output component count | float, vec2, vec3, vec4 | Number of components written to output location |
| Location mapping | identity (array), shuffled (shuffle) | How output locations map to attachments |

## Support / Feature Requirements

| Requirement | Condition | Details |
|-------------|-----------|---------|
| Vulkan only | `!CTS_USES_VULKANSC` | Entire test group guarded by Vulkan SC exclusion macro ([vktDrawOutputLocationTests.cpp#L53](../../../modules/vulkan/draw/vktDrawOutputLocationTests.cpp#L53)) |
| Renderpass only | `!useDynamicRendering` | Not added to dynamic rendering variants ([vktDrawTests.cpp#L106-L110](../../../modules/vulkan/draw/vktDrawTests.cpp#L106-L110)) |
| Portability subset | `VK_KHR_portability_subset` | Tests with `r8g8` names in the `array` group are skipped if `minVertexInputBindingStrideAlignment == 4` ([vktDrawOutputLocationTests.cpp#L42-L48](../../../modules/vulkan/draw/vktDrawOutputLocationTests.cpp#L42-L48)) |

## Verification Methods

| Method | Description |
|--------|-------------|
| Amber comparison | All test cases are amber-based; the amber framework performs rendering and image comparison internally against expected results defined in the amber scripts |

## Notes

- All test cases are amber-based and rely on external `.amber` script files located in the `draw/output_location/array` and `draw/output_location/shuffle` data directories.
- The portability subset check is applied as a `checkSupport` callback on each amber test case in the `array` group, but not on the `shuffle` group (the shuffle group does not set a check support callback).
- The `r8g8-uint` format tests are the only unsigned integer format tests in this group; all other formats are floating-point.
