# vktRenderPassMultisampleTests

## Source

- [vktRenderPassMultisampleTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp)

## Registration Hierarchy

```text
renderpasses.renderpass1.suballocation.multisample
├── a2b10g10r10_uint_pack32
├── a2b10g10r10_unorm_pack32
├── a2r10g10b10_unorm_pack32
├── a8_unorm
├── a8b8g8r8_sint_pack32
├── a8b8g8r8_snorm_pack32
├── a8b8g8r8_srgb_pack32
├── a8b8g8r8_uint_pack32
├── a8b8g8r8_unorm_pack32
├── b8g8r8a8_srgb
├── b8g8r8a8_unorm
├── d16_unorm
├── d16_unorm_s8_uint
├── d24_unorm_s8_uint
├── d32_sfloat
├── d32_sfloat_s8_uint
├── r10x6g10x6b10x6a10x6_unorm_4pack16
├── r16_sfloat
├── r16_sint
├── r16_snorm
├── r16_uint
├── r16_unorm
├── r16g16_sfloat
├── r16g16_sint
├── r16g16_snorm
├── r16g16_uint
├── r16g16_unorm
├── r16g16b16a16_sfloat
├── r16g16b16a16_sint
├── r16g16b16a16_snorm
├── r16g16b16a16_uint
├── r16g16b16a16_unorm
├── r32_sfloat
├── r32_sint
├── r32_uint
├── r32g32_sfloat
├── r32g32_sint
├── r32g32_uint
├── r32g32b32a32_sfloat
├── r32g32b32a32_sint
├── r32g32b32a32_uint
├── r5g6b5_unorm_pack16
├── r8_sint
├── r8_snorm
├── r8_uint
├── r8_unorm
├── r8g8_sint
├── r8g8_snorm
├── r8g8_uint
├── r8g8_unorm
├── r8g8b8a8_sint
├── r8g8b8a8_snorm
├── r8g8b8a8_srgb
├── r8g8b8a8_uint
├── r8g8b8a8_unorm
├── s8_uint
├── separate_stencil_usage
└── x8_d24_unorm_pack32
```

Evidence:
- `multisample` group created at [`createRenderPassMultisampleTests()`](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L2515)
- Format-named subgroups added at [vktRenderPassMultisampleTests.cpp#L2504](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L2504)
- `separate_stencil_usage` subgroup added at [vktRenderPassMultisampleTests.cpp#L2508](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L2508)

Note: The representative root uses `renderpass1`; the same topic group also appears under `renderpass2` and `dynamic_rendering`. Non-monolithic pipelines skip sample counts > 4.

## Role

Implementation file

## Test Families

### a2b10g10r10_uint_pack32 through x8_d24_unorm_pack32 — Per-format per-sample-count tests

Each format-named subgroup contains test cases for every supported sample count. The test renders to a multisample attachment and verifies per-sample pixel values against an XOR-based reference.

- **Pattern**: `<formatName>/samples_<N>` for N in {2, 4, 8, 16, 32}
- **Definition**: [vktRenderPassMultisampleTests.cpp#L2458-L2504](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L2458-L2504)
- 57 format subgroups covering color, depth-only, stencil-only, and depth-stencil formats
- Non-monolithic pipelines skip sample counts > 4

### separate_stencil_usage — Separate stencil usage tests

Tests `VK_EXT_separate_stencil_usage` with combined depth/stencil formats. For each depth+stencil format, creates tests that separately exercise depth and stencil aspects.

- **Pattern**: `separate_stencil_usage/<formatName>/samples_<N>/test_depth` and `test_stencil`
- **Definition**: [vktRenderPassMultisampleTests.cpp#L2456-L2508](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L2456-L2508)
- Requires `VK_EXT_separate_stencil_usage` + `VK_KHR_get_physical_device_properties2`
- Only applies to combined depth/stencil formats: d16_unorm_s8_uint, d24_unorm_s8_uint, d32_sfloat_s8_uint

## Parameter Dimensions

| Parameter | Values | Source |
|-----------|--------|--------|
| Formats | 50 VkFormat values | [vktRenderPassMultisampleTests.cpp#L2394-L2453](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L2394-L2453) |
| Sample counts | {2, 4, 8, 16, 32} | [vktRenderPassMultisampleTests.cpp#L2454](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L2454) |
| Separate stencil usage | TEST_DEPTH, TEST_STENCIL | [vktRenderPassMultisampleTests.cpp#L99-L100](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L99-L100) |

Note: Non-monolithic pipelines skip sample counts > 4.

## Support Requirements

Defined at [vktRenderPassMultisampleTests.cpp#L2328-L2380](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L2328-L2380):

- VK_KHR_create_renderpass2 for RENDERPASS2
- VK_KHR_dynamic_rendering_local_read for DYNAMIC_RENDERING
- VK_EXT_separate_stencil_usage + VK_KHR_get_physical_device_properties2 when separateStencilUsage
- VK_KHR_maintenance5 for VK_FORMAT_A8_UNORM_KHR
- Vulkan 1.4 dynamicRenderingLocalReadMultisampledAttachments / dynamicRenderingLocalReadDepthStencilAttachments

## Verification Methods

Defined at [vktRenderPassMultisampleTests.cpp#L1679-L1778](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L1679-L1778):

- Per-sample pixel comparison with XOR-based reference
- Depth: tcu::floatThresholdCompare with threshold 1.0/1024.0
- Stencil: exact comparison
- Color: dispatches by TextureChannelClass with format-appropriate comparison
