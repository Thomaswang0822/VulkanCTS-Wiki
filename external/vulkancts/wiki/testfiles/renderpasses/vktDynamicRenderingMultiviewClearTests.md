# vktDynamicRenderingMultiviewClearTests

## Source

[vktDynamicRenderingMultiviewClearTests.cpp](../../../modules/vulkan/renderpass/vktDynamicRenderingMultiviewClearTests.cpp)

## Registration

Added to dynamic_rendering root group (no secondary CB).

Registered group name: `"multiview_clear"` ([line 456](../../../modules/vulkan/renderpass/vktDynamicRenderingMultiviewClearTests.cpp#L456))

## Test Families

```
multiview_clear
|-- format
    |-- view_mask_0xH
        |-- _render_pass
        |-- _clear_regions
        |-- _clear_full
```

3 variants per view mask:
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

## Support Requirements

| Requirement | Context |
|---|---|
| VK_KHR_dynamic_rendering | [line 102](../../../modules/vulkan/renderpass/vktDynamicRenderingMultiviewClearTests.cpp#L102) |
| VK_KHR_multiview | [line 103](../../../modules/vulkan/renderpass/vktDynamicRenderingMultiviewClearTests.cpp#L103) |
| Format support | Per-format support checks |
| maxArrayLayers | Checked against view count requirements |
