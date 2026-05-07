# vktDynamicRenderingLocalReadTests

## Source

[vktDynamicRenderingLocalReadTests.cpp](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp)

## Registration

Added to dynamic_rendering root group (no secondary CB or partial secondary CB).

Registered group name: `"local_read"` ([line 3776](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L3776))

## Test Families

```
local_read
|-- max_input_attachments
|-- max_attachments_remapped_repeatedly
|-- input_attachments_without_mapping
|-- unused_writen_discarded
|-- depth_stencil_mapping_to_no_index (3 variants)
|-- depth_stencil_mapping_to_same_index
|-- depth_stencil_mapping_to_large_index
|-- depth_mapping_stencil_not
|-- mapping_not_affecting_blend_state
|-- interaction_with_color_write_enable
|-- interaction_with_graphics_pipeline_library
|-- interaction_with_extended_dynamic_state3
|-- interaction_with_shader_object
|-- remap_single_attachment (monolithic / fast_lib / shader_object)
|-- feedback_loop
|-- feedback_loop_with_shader_object
|-- feedback_loop_msaa
|-- null_attachment_location (sub-family)
|-- high_location_remapping (sub-family)
```

21 TestType configs defined at [lines 3751-3773](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L3751-L3773).

### Null Attachment Location Tests

[lines 3782-3798](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L3782-L3798)

**Parameter Dimensions:**

- nullBeforeIdentity: {false, true}
- nullAfterRemap: {false, true}

### High Location Remapping Tests

[lines 3802-3818](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L3802-L3818)

**Parameter Dimensions:**

- numAttachments: {1, 2}
- firstRemapLocation: from numAttachments to kMaxLocation (3)

**Verification:**

- `tcu::floatThresholdCompare` for color/depth/stencil against expected values

## Support Requirements

| Requirement | Context |
|---|---|
| VK_KHR_dynamic_rendering_local_read | [line 2455](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L2455) |
| maxPerStageDescriptorInputAttachments >= 21 | Required for `DEPTH_STENCIL_MAPPING_TO_LARGE_INDEX` |
| Format support checks | Per-attachment format requirements |
