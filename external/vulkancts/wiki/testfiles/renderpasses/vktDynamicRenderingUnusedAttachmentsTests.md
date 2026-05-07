# vktDynamicRenderingUnusedAttachmentsTests

## Source

[vktDynamicRenderingUnusedAttachmentsTests.cpp](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp)

## Registration

Added to dynamic_rendering root group (both no-secondary and partial-secondary CB variants).

Registered group name: `"unused_attachments"` ([line 1596](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L1596))

## Test Families

```
unused_attachments
|-- comb
|   |-- color
|   |-- depth_stencil
|-- color
|   |-- pipeline/fragment attachment count
|   |-- layer
|   |-- mask
|   |-- multiview
|-- depth_stencil
|   |-- present/defined/validHandle boolean combinations
|-- bad_formats
|   |-- VK_FORMAT_UNDEFINED with valid handles
|-- extra_att
|-- extra_pipe_att
|-- extra_render_att
|-- misc
    |-- used-then-unused
    |-- dynamicDepthEnable
```

7 sub-groups defined at [lines 1600-1606](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L1600-L1606).

**Parameter Dimensions:**

- Color: pipeAtt {1,4,8} x fragAtt {1,4,8} x layerCount {1,4} x layerMask (4) x formatMask (4) x handleMask (4) x multiview {false,true}
- Depth/stencil: depth/stencil present/defined/validHandle booleans
- Extra: attCount {1,4,8} x formatMask x handleMask
- Misc: dynamicDepthEnable {false, true}

**Verification:**

- Color: `tcu::floatThresholdCompare` or pixel-by-pixel comparison
- Depth/stencil: `tcu::dsThresholdCompare` with threshold `0.0f`

## Support Requirements

| Requirement | Context |
|---|---|
| VK_KHR_dynamic_rendering | [line 491](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L491) |
| VK_EXT_dynamic_rendering_unused_attachments | [line 492](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L492) |
| maxFragmentOutputAttachments, maxColorAttachments | Device limit checks |
| VK_EXT_extended_dynamic_state | Required for misc with `dynamicDepthEnable` |
