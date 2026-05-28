# vktDynamicRenderingMultiviewClearTests

## Source

[vktDynamicRenderingMultiviewClearTests.cpp](../../../modules/vulkan/renderpass/vktDynamicRenderingMultiviewClearTests.cpp)

## Registration Hierarchy

```text
renderpasses.dynamic_rendering.primary_cmd_buff.multiview_clear
├── d16_unorm
├── d24_unorm_s8_uint
├── d32_sfloat_s8_uint
├── r8g8b8a8_unorm
└── s8_uint
```

Registered under `primary_cmd_buff` only ([vktRenderPassTests.cpp#L8539](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8539)). The `multiview_clear` group is created at [line 456](../../../modules/vulkan/renderpass/vktDynamicRenderingMultiviewClearTests.cpp#L456).

## Test Families

### r8g8b8a8_unorm — Color format multiview clear

R8G8B8A8_UNORM format clear tests with multiview.

### d16_unorm — D16_UNORM multiview clear

D16_UNORM depth format clear tests with multiview.

### d24_unorm_s8_uint — D24_UNORM_S8_UINT multiview clear

D24_UNORM_S8_UINT combined depth/stencil format clear tests with multiview.

### d32_sfloat_s8_uint — D32_SFLOAT_S8_UINT multiview clear

D32_SFLOAT_S8_UINT combined depth/stencil format clear tests with multiview.

### s8_uint — S8_UINT multiview clear

S8_UINT stencil-only format clear tests with multiview.

Each format subgroup contains view-mask subgroups (view_mask_0x1, view_mask_0x2, view_mask_0x4, view_mask_0x8, view_mask_0xf), each with 3 test variants:
- `_render_pass` -- render pass clear
- `_clear_regions` -- `vkCmdClearAttachments` with two sub-regions
- `_clear_full` -- `vkCmdClearAttachments` with full-size clear rect

**Parameter Dimensions** ([lines 458-491](../../../modules/vulkan/renderpass/vktDynamicRenderingMultiviewClearTests.cpp#L458-L491)):

- format: {R8G8B8A8_UNORM, D16_UNORM, D24_UNORM_S8_UINT, D32_SFLOAT_S8_UINT, S8_UINT}
- viewMask: {1, 2, 4, 8, 15}

**Verification** ([lines 400](../../../modules/vulkan/renderpass/vktDynamicRenderingMultiviewClearTests.cpp#L400), [407](../../../modules/vulkan/renderpass/vktDynamicRenderingMultiviewClearTests.cpp#L407)):

- Color: `tcu::floatThresholdCompare` per layer
- Depth: `tcu::dsThresholdCompare` per layer
- Stencil: separate stencil buffer verification

## Support / Feature Requirements

| Requirement | Context |
|---|---|
| VK_KHR_dynamic_rendering | [line 102](../../../modules/vulkan/renderpass/vktDynamicRenderingMultiviewClearTests.cpp#L102) |
| VK_KHR_multiview | [line 103](../../../modules/vulkan/renderpass/vktDynamicRenderingMultiviewClearTests.cpp#L103) |
| Format support | Per-format support checks |
| maxArrayLayers | Checked against view count requirements |
