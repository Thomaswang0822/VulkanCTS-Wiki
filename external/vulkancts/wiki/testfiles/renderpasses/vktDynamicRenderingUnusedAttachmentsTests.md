# vktDynamicRenderingUnusedAttachmentsTests

## Source

[vktDynamicRenderingUnusedAttachmentsTests.cpp](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp)

## Registration Hierarchy

```text
renderpasses.dynamic_rendering.primary_cmd_buff.unused_attachments
├── bad_formats
├── comb
├── extra_att
├── extra_pipe_att
├── extra_render_att
└── misc
```

Registered under `primary_cmd_buff` ([vktRenderPassTests.cpp#L8534](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8534)) and also under `partial_secondary_cmd_buff` ([vktRenderPassTests.cpp#L8543](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8543)). The `unused_attachments` group is created at [line 1596](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L1596).

## Test Families

6 sub-groups defined at [lines 1600-1606](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L1600-L1606).

### comb — Combination tests

VK_EXT_dynamic_rendering_unused_attachments with different combinations. Contains `color` and `depth_stencil` subgroups.

- **color**: Pipeline/fragment attachment count, layer, mask, and multiview combinations. Parameters: pipeAtt {1,4,8} x fragAtt {1,4,8} x layerCount {1,4} x layerMask (4) x formatMask (4) x handleMask (4) x multiview {false,true}
- **depth_stencil**: Depth/stencil present/defined/validHandle boolean combinations

### bad_formats — Bad format tests

VK_FORMAT_UNDEFINED with valid handles. Parameters: formatMask x handleMask combinations.

### extra_att — Extra attachment tests

Extra render pass attachments. Parameters: attCount {1,4,8} x formatMask x handleMask.

### extra_pipe_att — Extra pipeline attachment tests

Extra pipeline attachments. Parameters: attCount {1,4,8} x formatMask x handleMask.

### extra_render_att — Extra render attachment tests

Extra render attachments. Parameters: attCount {1,4,8} x formatMask x handleMask.

### misc — Miscellaneous tests

- `color_used_then_unused`: Used-then-unused color attachment tests
- `color_used_then_unused_dynamic_depth_enable`: Same with dynamic depth enable

Parameters: dynamicDepthEnable {false, true}. Requires VK_EXT_extended_dynamic_state for `dynamicDepthEnable`.

**Verification:**

- Color: `tcu::floatThresholdCompare` or pixel-by-pixel comparison
- Depth/stencil: `tcu::dsThresholdCompare` with threshold `0.0f`

## Support / Feature Requirements

| Requirement | Context |
|---|---|
| VK_KHR_dynamic_rendering | [line 491](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L491) |
| VK_EXT_dynamic_rendering_unused_attachments | [line 492](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L492) |
| maxFragmentOutputAttachments, maxColorAttachments | Device limit checks |
| VK_EXT_extended_dynamic_state | Required for misc with `dynamicDepthEnable` |
