# vktImageDepthStencilSeparateTests ([source](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp))

## Overview

Tests for `VK_FORMAT_FEATURE_2_DEPTH_STENCIL_SEPARATE_FRAMEBUFFER_ACCESS_BIT_KHR` (VK_KHR_maintenance7). The file verifies that depth and stencil aspects of a combined depth/stencil image can be accessed separately during rendering - one aspect sampled in the shader while the other is written through the framebuffer attachment mechanism. Tests cover multiple write mechanisms (clear, don't care, test+store, test+resolve), both general and separate image layouts, and dynamic stencil reference values.

## Role of File

Implementation file that registers the `depth_stencil_separate_access` test group and provides complete test implementations. Contains test case class, test instance class, and the factory function that populates the test hierarchy.

## Source Code

- Implementation: [vktImageDepthStencilSeparateTests.cpp](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp)
- Header: [vktImageDepthStencilSeparateTests.hpp](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.hpp)

## Registration Hierarchy

```text
image.depth_stencil_separate_access
├── d16_unorm_s8_uint
├── d24_unorm_s8_uint
└── d32_sfloat_s8_uint
```

Evidence:
- `depth_stencil_separate_access` group created by [`createImageDepthStencilSeparateTests()`](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L1409-L1479)
- Format subgroups added at lines 1441-1444 with names from `getFormatShortString(format)`
- Write mechanism, layout, and stencil reference variants generated at lines 1446-1473

## Test Families

### Per-format format groups

Each format subgroup generates a comprehensive matrix of test variants:

| Parameter | Values | Description |
|-----------|--------|-------------|
| Write aspect | write_depth, write_stencil | Which aspect is written through framebuffer |
| Write mechanism | render_pass_clears, render_pass_dont_care, test_and_store, test_and_resolve | How the aspect is written |
| Layout | general_layout, separate_layouts | Image layout strategy |
| Stencil ref | _dynamic_stencil_ref | Dynamic stencil reference (stencil write + test only) |

### Write mechanism families

- **render_pass_clears**: Aspect written during render pass via VK_ATTACHMENT_LOAD_OP_CLEAR
- **render_pass_dont_care**: Aspect written via VK_ATTACHMENT_LOAD_OP_DONT_CARE (may produce undefined values)
- **test_and_store**: Aspect written by passing depth/stencil test, store operation preserves result
- **test_and_resolve**: Aspect written by passing test and then resolved to single-sample target

### Layout families

- **general_layout**: Uses combined depth/stencil layouts (DEPTH_READ_ONLY_STENCIL_ATTACHMENT_OPTIMAL or DEPTH_ATTACHMENT_STENCIL_READ_ONLY_OPTIMAL)
- **separate_layouts**: Uses separate per-aspect layouts (DEPTH_READ_ONLY_OPTIMAL, DEPTH_ATTACHMENT_OPTIMAL, STENCIL_READ_ONLY_OPTIMAL, STENCIL_ATTACHMENT_OPTIMAL)

## Parameter Dimensions

| Dimension | Values | Source |
|-----------|--------|--------|
| Image Format | D16_UNORM_S8_UINT, D24_UNORM_S8_UINT, D32_SFLOAT_S8_UINT | [line 1415-1419](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L1415-L1419) |
| Framebuffer Size | 16x16 | [line 60](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L60) |
| Sample Count | 1-bit (single sample) or 4-bit (multisample for resolve tests) | [lines 63-64, 174-176](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L63-L64) |
| Color Format | VK_FORMAT_R8G8B8A8_UNORM | [line 58](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L58) |
| Storage Image Format | R32_SFLOAT (for depth read) or R32_UINT (for stencil read) | [line 181-183](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L181-183) |
| Vertex Count | 1 point per pixel (256 points) | [line 844](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L844) |
| Stencil Reference Values | 1-255 (pseudorandom per vertex) | [line 860](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L860) |
| Depth Values | [0.5, 1.0) pseudorandom range | [line 859](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L859) |

## Support / Feature Requirements

| Requirement | Condition | Source |
|-------------|-----------|--------|
| VK_KHR_get_physical_device_properties2 | Instance functionality required | [line 318](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L318) |
| VK_KHR_maintenance7 | Device functionality required | [line 319](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L319) |
| VK_KHR_format_feature_flags2 | Device functionality required | [line 320](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L320) |
| separateDepthStencilAttachmentAccess | Physical device property must be true on non-VulkanSC builds | [lines 322-326](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L322-L326) |
| VK_EXT_shader_stencil_export | When dynamicStencilRef is true | [line 391-392](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L391-L392) |
| VK_KHR_depth_stencil_resolve | When write mechanism is TEST_RESOLVE | [line 394-395](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L394-L395) |
| VK_KHR_separate_depth_stencil_layouts | When separateLayouts is true | [line 397-398](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L397-L398) |
| Format features | On non-VulkanSC builds, optimal tiling must expose depth/stencil attachment, sampled image, transfer source, and transfer destination feature bits | [lines 382-389](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L382-L389) |
| Sample count support | Must support requested sample count for format | [line 375-377](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L375-L377) |

## Verification Methods

### Buffer comparison

Tests verify results by copying buffers to host-visible memory and comparing against reference:

- **Color buffer**: Compared using `tcu::floatThresholdCompare` with threshold 0.005 at [line 1379-1381](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L1379-1381)
- **Storage buffer (sampled read)**: Depth values compared with `tcu::floatThresholdCompare` using format-specific threshold at [line 1383-1386](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L1383-1386); stencil values compared with `tcu::intThresholdCompare` at [line 1387-1388](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L1387-1388)
- **Depth buffer**: Compared using `tcu::dsThresholdCompare` when not sampled via storage at [line 1390-1394](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L1390-1394)
- **Stencil buffer**: Compared using `tcu::dsThresholdCompare` when not sampled via storage at [line 1396-1400](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L1396-1400)

### Depth threshold by format

| Format | Threshold | Source |
|--------|-----------|--------|
| D16_UNORM | 1.5/65535.0 (~0.000023) | [line 797-798](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L797-798) |
| D24_UNORM_S8_UINT | 1.5/16777215.0 (~0.000000089) | [line 799-800](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L799-800) |
| D32_SFLOAT | 1.0/33554431.0 (~0.000000030) | [line 802-803](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L802-803) |

## Test Principles Observed

- **Separate aspect access**: One aspect is sampled in the shader while the other is accessed through the framebuffer attachment mechanism
- **Pseudorandom test data**: Each pixel gets unique pseudorandom depth and stencil values to detect any data mixing between aspects
- **Dynamic stencil reference**: When testing stencil writes with dynamic reference, each draw call uses a different stencil reference value (single-point draws)
- **Load/store operations**: Tests verify all combinations of load and store operations for each aspect
- **Multisample resolve**: Test resolution verifies that MSAA resolves correctly when using separate framebuffer access
- **Pre-fill validation**: Read-only aspects are pre-filled and must be preserved (with load_op=LOAD and store_op=STORE) when the other aspect is written

## Notes / Uncertainties

- The file requires `separateDepthStencilAttachmentAccess` to be true, which is verified in `checkSupport` at [lines 323-325](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L323-325)
- When `generalLayout` and `separateLayouts` are both true, the combination is skipped (not meaningful)
- When `writeMechanism` is TEST_RESOLVE and `separateLayouts` is true, the combination is skipped to avoid combinatorial explosion
- Stencil reference is only dynamic when writing stencil with a test mechanism and not using shader-based stencil export
- The vertex shader passes pseudorandom depth/stencil values as per-vertex attributes; the fragment shader samples the depth/stencil image and stores to a storage image for verification
