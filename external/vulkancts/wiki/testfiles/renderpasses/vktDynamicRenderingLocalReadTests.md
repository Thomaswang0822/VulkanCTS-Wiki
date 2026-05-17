# vktDynamicRenderingLocalReadTests

## Source

[vktDynamicRenderingLocalReadTests.cpp](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp)

## Registration Hierarchy

```text
renderpasses.dynamic_rendering.primary_cmd_buff.local_read
├── depth_mapping_stencil_not
├── depth_stencil_mapping_to_large_index
├── depth_stencil_mapping_to_no_index
├── depth_stencil_mapping_to_no_index_depth_clear
├── depth_stencil_mapping_to_no_index_stencil_clear
├── depth_stencil_mapping_to_same_index
├── feedback_loop
├── feedback_loop_msaa
├── feedback_loop_with_shader_object
├── input_attachments_without_mapping
├── interaction_with_color_write_enable
├── interaction_with_extended_dynamic_state3
├── interaction_with_graphics_pipeline_library
├── interaction_with_shader_object
├── mapping_1_attachments_to_locs_from_1
├── mapping_1_attachments_to_locs_from_2
├── mapping_1_attachments_to_locs_from_3
├── mapping_2_attachments_to_locs_from_2
├── mapping_not_affecting_blend_state
├── max_attachments_remapped_repeatedly
├── max_input_attachments
├── null_color_attachment_location_with_command
├── null_color_attachment_location_with_command_after_remap
├── null_color_attachment_location_with_locationinfo
├── null_color_attachment_location_with_locationinfo_before_identity
├── remap_single_attachment_fast_lib
├── remap_single_attachment_monolithic
├── remap_single_attachment_shader_object
└── unused_writen_discarded
```

Registered under `primary_cmd_buff` ([vktRenderPassTests.cpp#L8535](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8535)) and also under `partial_secondary_cmd_buff` ([vktRenderPassTests.cpp#L8544](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8544)). The `local_read` group is created at [line 3776](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L3776). The `null_color_attachment_location_*` and `mapping_*` tests are only added when `useSecondaryCmdBuffer` is false (i.e., under `primary_cmd_buff` only).

## Test Families

21 TestType configs defined at [lines 3751-3773](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L3751-L3773), plus null-attachment-location tests ([lines 3782-3798](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L3782-L3798)) and high-location-remapping tests ([lines 3802-3818](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L3802-L3818)).

### max_input_attachments — Max input attachments

Tests with the maximum number of input attachments.

### max_attachments_remapped_repeatedly — Max attachments remapped repeatedly

Tests where attachments are remapped repeatedly.

### input_attachments_without_mapping — Input attachments without mapping

Tests input attachments that are not mapped.

### unused_writen_discarded — Unused written discarded

Tests where unused attachments are written and then discarded.

### depth_stencil_mapping_to_no_index / depth_stencil_mapping_to_no_index_depth_clear / depth_stencil_mapping_to_no_index_stencil_clear — Depth/stencil mapping to no index

Tests depth/stencil attachment mapping to no index, with depth-clear and stencil-clear variants.

### depth_stencil_mapping_to_same_index — Depth/stencil mapping to same index

Tests depth and stencil mapped to the same index.

### depth_stencil_mapping_to_large_index — Depth/stencil mapping to large index

Tests depth/stencil mapped to a large attachment index.

### depth_mapping_stencil_not — Depth mapping, stencil not

Tests depth mapping while stencil is not mapped.

### mapping_not_affecting_blend_state — Mapping not affecting blend state

Verifies that attachment remapping does not affect blend state.

### interaction_with_color_write_enable — Interaction with color write enable

Tests interaction between local read and VK_EXT_color_write_enable.

### interaction_with_graphics_pipeline_library — Interaction with graphics pipeline library

Tests interaction between local read and graphics pipeline library.

### interaction_with_extended_dynamic_state3 — Interaction with extended dynamic state 3

Tests interaction between local read and VK_EXT_extended_dynamic_state3.

### interaction_with_shader_object — Interaction with shader object

Tests interaction between local read and VK_EXT_shader_object.

### remap_single_attachment_monolithic / remap_single_attachment_fast_lib / remap_single_attachment_shader_object — Remap single attachment

Tests remapping a single attachment with monolithic pipeline, fast-linked library, and shader object variants.

### feedback_loop / feedback_loop_with_shader_object / feedback_loop_msaa — Feedback loop

Tests feedback loop patterns, including shader object and MSAA variants.

### null_color_attachment_location_with_locationinfo / null_color_attachment_location_with_locationinfo_before_identity — Null attachment location with location info

Tests pColorAttachmentLocations set to NULL with location info. Parameter dimensions: nullBeforeIdentity {false, true}.

### null_color_attachment_location_with_command / null_color_attachment_location_with_command_after_remap — Null attachment location with command

Tests pColorAttachmentLocations set to NULL with command mode. Parameter dimensions: nullAfterRemap {false, true}.

### mapping_1_attachments_to_locs_from_1 / mapping_1_attachments_to_locs_from_2 / mapping_1_attachments_to_locs_from_3 / mapping_2_attachments_to_locs_from_2 — High location remapping

Tests mapping to (unused) locations higher than default locations. Parameter dimensions: numAttachments {1, 2}, firstRemapLocation from numAttachments to kMaxLocation (3).

**Verification:**

- `tcu::floatThresholdCompare` for color/depth/stencil against expected values

## Support Requirements

| Requirement | Context |
|---|---|
| VK_KHR_dynamic_rendering_local_read | [line 2455](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L2455) |
| maxPerStageDescriptorInputAttachments >= 21 | Required for `DEPTH_STENCIL_MAPPING_TO_LARGE_INDEX` |
| Format support checks | Per-attachment format requirements |
