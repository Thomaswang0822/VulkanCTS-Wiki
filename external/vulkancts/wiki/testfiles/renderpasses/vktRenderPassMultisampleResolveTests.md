# vktRenderPassMultisampleResolveTests

## Source

- [vktRenderPassMultisampleResolveTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassMultisampleResolveTests.cpp)

## Registration Hierarchy

```text
renderpasses.renderpass1.suballocation.multisample_resolve
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
├── layers_3
├── layers_6
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
└── r8g8b8a8_unorm
```

Evidence:
- `multisample_resolve` group created at [`createRenderPassMultisampleResolveTests()`](../../../modules/vulkan/renderpass/vktRenderPassMultisampleResolveTests.cpp#L3263)
- Format-named subgroups (layerCount=1) added at [vktRenderPassMultisampleResolveTests.cpp#L3248](../../../modules/vulkan/renderpass/vktRenderPassMultisampleResolveTests.cpp#L3248)
- `layers_<N>` subgroups (layerCount>1) added at [vktRenderPassMultisampleResolveTests.cpp#L3254](../../../modules/vulkan/renderpass/vktRenderPassMultisampleResolveTests.cpp#L3254)

Note: The representative root uses `renderpass1`; the same topic group also appears under `renderpass2` and `dynamic_rendering`. Non-monolithic pipelines limit sample counts and layer counts.

## Role

Implementation file

The historical Vulkan API test plan includes resolve behavior among multipass data-flow dimensions ([`apitests.adoc`](../../../../../doc/testspecs/VK/apitests.adoc#L302-L308)); current source and mustpass remain authoritative for exact behavior.

## Test Families

### a2b10g10r10_uint_pack32 through b8g8r8a8_unorm — Per-format basic resolve tests (single layer)

Each format-named subgroup (layerCount=1) contains test cases for basic multisample resolve, plus monolithic-only variants for base layer offset, resolve level, max attachments, and compatibility.

- **Basic resolve**: `<formatName>/samples_<N>` for N in {2, 4, 8}
- **Base layer offset**: `<formatName>/samples_<N>_baseLayer1` (monolithic pipeline only)
- **Resolve level**: `<formatName>/samples_<N>_resolve_level_<L>` for L in {2, 3, 4} (monolithic pipeline only)
- **Max attachments**: `<formatName>/max_attachments_<P>_samples_<N>` for P in {4, 8, 16} (power of 2)
- **Compatibility**: `<formatName>/compatibility_samples_<N>` (non-dynamic rendering only)
- **Definition**: [vktRenderPassMultisampleResolveTests.cpp#L3149-L3248](../../../modules/vulkan/renderpass/vktRenderPassMultisampleResolveTests.cpp#L3149-L3248)
- 50 color-only format subgroups

### layers_3 — Multi-layer resolve tests with 3 layers

Tests multisample resolve with 3 array layers. Requires `DEVICE_CORE_FEATURE_GEOMETRY_SHADER`.

- **Pattern**: `layers_3/<formatName>/samples_<N>`
- **Definition**: [vktRenderPassMultisampleResolveTests.cpp#L3143-L3254](../../../modules/vulkan/renderpass/vktRenderPassMultisampleResolveTests.cpp#L3143-L3254)
- Skips layerCount=6 with sampleCount=8 (slow test)
- Secondary command buffer variants limit sample counts > 2 and layer counts > 3

### layers_6 — Multi-layer resolve tests with 6 layers

Tests multisample resolve with 6 array layers. Requires `DEVICE_CORE_FEATURE_GEOMETRY_SHADER`.

- **Pattern**: `layers_6/<formatName>/samples_<N>`
- **Definition**: [vktRenderPassMultisampleResolveTests.cpp#L3143-L3254](../../../modules/vulkan/renderpass/vktRenderPassMultisampleResolveTests.cpp#L3143-L3254)
- Skips layerCount=6 with sampleCount=8 (slow test)
- Secondary command buffer variants limit sample counts > 2 and layer counts > 3

## Parameter Dimensions

| Parameter | Values | Source |
|-----------|--------|--------|
| Formats | 48 color-only VkFormat values | [vktRenderPassMultisampleResolveTests.cpp#L3084-L3137](../../../modules/vulkan/renderpass/vktRenderPassMultisampleResolveTests.cpp#L3084-L3137) |
| Sample counts | {2, 4, 8} | [vktRenderPassMultisampleResolveTests.cpp#L3138](../../../modules/vulkan/renderpass/vktRenderPassMultisampleResolveTests.cpp#L3138) |
| Layer counts | {1, 3, 6} | [vktRenderPassMultisampleResolveTests.cpp#L3139](../../../modules/vulkan/renderpass/vktRenderPassMultisampleResolveTests.cpp#L3139) |
| Resolve levels | {2, 3, 4} | [vktRenderPassMultisampleResolveTests.cpp#L3140](../../../modules/vulkan/renderpass/vktRenderPassMultisampleResolveTests.cpp#L3140) |
| Max attachment counts | Powers of 2 from 4 to 16 | - |

## Support Requirements

Defined at [vktRenderPassMultisampleResolveTests.cpp#L2995-L3070](../../../modules/vulkan/renderpass/vktRenderPassMultisampleResolveTests.cpp#L2995-L3070):

- VK_KHR_maintenance5 for VK_FORMAT_A8_UNORM_KHR
- DEVICE_CORE_FEATURE_GEOMETRY_SHADER when layerCount > 1
- VK_KHR_create_renderpass2 for RENDERPASS2
- VK_KHR_dynamic_rendering + VK_KHR_dynamic_rendering_local_read for DYNAMIC_RENDERING
- VK_KHR_portability_subset: multisampleArrayImage check
- maxColorAttachments and maxPerStageDescriptorInputAttachments limits

## Verification Methods

- **Resolve** (line 1008): per-pixel comparison against expected resolve result; float/fixed-point uses tcu::floatThresholdCompare; integer uses tcu::intThresholdCompare
- **Max attachments** (line 2263): compares against reference color (0.0, 0.3, 0.6, 0.75) with format-dependent threshold
