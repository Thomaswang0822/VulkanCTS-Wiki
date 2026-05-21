# vktVideoEncodeTests

## Overview

`vktVideoEncodeTests.cpp` registers the `video.encode` group for H.264 and H.265 encode-session tests, then attaches the AV1 encode group provided by `vktVideoEncodeTestsAV1.cpp` ([vktVideoEncodeTests.cpp](../../../modules/vulkan/video/vktVideoEncodeTests.cpp#L3979-L4015)).

## Role of File

| Aspect | Evidence-backed description |
|---|---|
| Registration role | Creates `encode`, `h264`, and `h265`, generates H.264/H.265 leaves, and delegates `av1` registration to `createVideoEncodeTestsAV1()` ([vktVideoEncodeTests.cpp](../../../modules/vulkan/video/vktVideoEncodeTests.cpp#L3979-L4015)). |
| Implementation role | Encodes configured frame patterns, validates query status when requested, and verifies encoded bitstreams by decoding/comparing output quality ([vktVideoEncodeTests.cpp](../../../modules/vulkan/video/vktVideoEncodeTests.cpp#L3329-L3356), [vktVideoEncodeTests.cpp](../../../modules/vulkan/video/vktVideoEncodeTests.cpp#L3358-L3838)). |

## Registration Hierarchy

```text
video.encode
├── av1
├── h264
└── h265
video.encode.h264
├── i_layered_src_general_layout
├── i_layered_src_video_layout
├── i_p_b_13_layered_src_general_layout
├── i_p_b_13_layered_src_video_layout
├── i_p_b_13_separated_src_general_layout
├── i_p_b_13_separated_src_video_layout
├── i_p_layered_src_general_layout
├── i_p_layered_src_video_layout
├── i_p_not_matching_order_layered_src_general_layout
├── i_p_not_matching_order_layered_src_video_layout
├── i_p_not_matching_order_separated_src_general_layout
├── i_p_not_matching_order_separated_src_video_layout
├── i_p_separated_src_general_layout
├── i_p_separated_src_video_layout
├── i_separated_src_general_layout
├── i_separated_src_video_layout
├── inline_query_layered_src_general_layout
├── inline_query_layered_src_video_layout
├── inline_query_separated_src_general_layout
├── inline_query_separated_src_video_layout
├── intra_refresh_any_block_based_empty_region_layered_src_general_layout
├── intra_refresh_any_block_based_empty_region_layered_src_video_layout
├── intra_refresh_any_block_based_empty_region_separated_src_general_layout
├── intra_refresh_any_block_based_empty_region_separated_src_video_layout
├── intra_refresh_any_block_based_layered_src_general_layout
├── intra_refresh_any_block_based_layered_src_video_layout
├── intra_refresh_any_block_based_midway_layered_src_general_layout
├── intra_refresh_any_block_based_midway_layered_src_video_layout
├── intra_refresh_any_block_based_midway_separated_src_general_layout
├── intra_refresh_any_block_based_midway_separated_src_video_layout
├── intra_refresh_any_block_based_separated_src_general_layout
├── intra_refresh_any_block_based_separated_src_video_layout
├── intra_refresh_column_based_empty_region_layered_src_general_layout
├── intra_refresh_column_based_empty_region_layered_src_video_layout
├── intra_refresh_column_based_empty_region_separated_src_general_layout
├── intra_refresh_column_based_empty_region_separated_src_video_layout
├── intra_refresh_column_based_layered_src_general_layout
├── intra_refresh_column_based_layered_src_video_layout
├── intra_refresh_column_based_midway_layered_src_general_layout
├── intra_refresh_column_based_midway_layered_src_video_layout
├── intra_refresh_column_based_midway_separated_src_general_layout
├── intra_refresh_column_based_midway_separated_src_video_layout
├── intra_refresh_column_based_separated_src_general_layout
├── intra_refresh_column_based_separated_src_video_layout
├── intra_refresh_picture_partition_layered_src_general_layout
├── intra_refresh_picture_partition_layered_src_video_layout
├── intra_refresh_picture_partition_midway_layered_src_general_layout
├── intra_refresh_picture_partition_midway_layered_src_video_layout
├── intra_refresh_picture_partition_midway_separated_src_general_layout
├── intra_refresh_picture_partition_midway_separated_src_video_layout
├── intra_refresh_picture_partition_separated_src_general_layout
├── intra_refresh_picture_partition_separated_src_video_layout
├── intra_refresh_row_based_empty_region_layered_src_general_layout
├── intra_refresh_row_based_empty_region_layered_src_video_layout
├── intra_refresh_row_based_empty_region_separated_src_general_layout
├── intra_refresh_row_based_empty_region_separated_src_video_layout
├── intra_refresh_row_based_layered_src_general_layout
├── intra_refresh_row_based_layered_src_video_layout
├── intra_refresh_row_based_midway_layered_src_general_layout
├── intra_refresh_row_based_midway_layered_src_video_layout
├── intra_refresh_row_based_midway_separated_src_general_layout
├── intra_refresh_row_based_midway_separated_src_video_layout
├── intra_refresh_row_based_separated_src_general_layout
├── intra_refresh_row_based_separated_src_video_layout
├── quality_level_layered_src_general_layout
├── quality_level_layered_src_video_layout
├── quality_level_separated_src_general_layout
├── quality_level_separated_src_video_layout
├── quantization_map_delta_layered_src_general_layout
├── quantization_map_delta_layered_src_video_layout
├── quantization_map_delta_rc_cbr_layered_src_general_layout
├── quantization_map_delta_rc_cbr_layered_src_video_layout
├── quantization_map_delta_rc_cbr_separated_src_general_layout
├── quantization_map_delta_rc_cbr_separated_src_video_layout
├── quantization_map_delta_rc_disable_layered_src_general_layout
├── quantization_map_delta_rc_disable_layered_src_video_layout
├── quantization_map_delta_rc_disable_separated_src_general_layout
├── quantization_map_delta_rc_disable_separated_src_video_layout
├── quantization_map_delta_rc_vbr_layered_src_general_layout
├── quantization_map_delta_rc_vbr_layered_src_video_layout
├── quantization_map_delta_rc_vbr_separated_src_general_layout
├── quantization_map_delta_rc_vbr_separated_src_video_layout
├── quantization_map_delta_separated_src_general_layout
├── quantization_map_delta_separated_src_video_layout
├── quantization_map_emphasis_cbr_layered_src_general_layout
├── quantization_map_emphasis_cbr_layered_src_video_layout
├── quantization_map_emphasis_cbr_separated_src_general_layout
├── quantization_map_emphasis_cbr_separated_src_video_layout
├── quantization_map_emphasis_vbr_layered_src_general_layout
├── quantization_map_emphasis_vbr_layered_src_video_layout
├── quantization_map_emphasis_vbr_separated_src_general_layout
├── quantization_map_emphasis_vbr_separated_src_video_layout
├── query_with_status_layered_src_general_layout
├── query_with_status_layered_src_video_layout
├── query_with_status_separated_src_general_layout
├── query_with_status_separated_src_video_layout
├── rc_cbr_layered_src_general_layout
├── rc_cbr_layered_src_video_layout
├── rc_cbr_separated_src_general_layout
├── rc_cbr_separated_src_video_layout
├── rc_disable_layered_src_general_layout
├── rc_disable_layered_src_video_layout
├── rc_disable_separated_src_general_layout
├── rc_disable_separated_src_video_layout
├── rc_vbr_layered_src_general_layout
├── rc_vbr_layered_src_video_layout
├── rc_vbr_separated_src_general_layout
├── rc_vbr_separated_src_video_layout
├── resolution_change_dpb_layered_src_general_layout
├── resolution_change_dpb_layered_src_video_layout
├── resolution_change_dpb_separated_src_general_layout
├── resolution_change_dpb_separated_src_video_layout
├── resources_without_profiles_layered_src_general_layout
├── resources_without_profiles_layered_src_video_layout
├── resources_without_profiles_separated_src_general_layout
├── resources_without_profiles_separated_src_video_layout
├── usage_layered_src_general_layout
├── usage_layered_src_video_layout
├── usage_separated_src_general_layout
└── usage_separated_src_video_layout
video.encode.h265
├── i_layered_src_general_layout
├── i_layered_src_video_layout
├── i_p_b_13_layered_src_general_layout
├── i_p_b_13_layered_src_video_layout
├── i_p_b_13_separated_src_general_layout
├── i_p_b_13_separated_src_video_layout
├── i_p_layered_src_general_layout
├── i_p_layered_src_video_layout
├── i_p_not_matching_order_layered_src_general_layout
├── i_p_not_matching_order_layered_src_video_layout
├── i_p_not_matching_order_separated_src_general_layout
├── i_p_not_matching_order_separated_src_video_layout
├── i_p_separated_src_general_layout
├── i_p_separated_src_video_layout
├── i_separated_src_general_layout
├── i_separated_src_video_layout
├── inline_query_layered_src_general_layout
├── inline_query_layered_src_video_layout
├── inline_query_separated_src_general_layout
├── inline_query_separated_src_video_layout
├── intra_refresh_any_block_based_empty_region_layered_src_general_layout
├── intra_refresh_any_block_based_empty_region_layered_src_video_layout
├── intra_refresh_any_block_based_empty_region_separated_src_general_layout
├── intra_refresh_any_block_based_empty_region_separated_src_video_layout
├── intra_refresh_any_block_based_layered_src_general_layout
├── intra_refresh_any_block_based_layered_src_video_layout
├── intra_refresh_any_block_based_midway_layered_src_general_layout
├── intra_refresh_any_block_based_midway_layered_src_video_layout
├── intra_refresh_any_block_based_midway_separated_src_general_layout
├── intra_refresh_any_block_based_midway_separated_src_video_layout
├── intra_refresh_any_block_based_separated_src_general_layout
├── intra_refresh_any_block_based_separated_src_video_layout
├── intra_refresh_column_based_empty_region_layered_src_general_layout
├── intra_refresh_column_based_empty_region_layered_src_video_layout
├── intra_refresh_column_based_empty_region_separated_src_general_layout
├── intra_refresh_column_based_empty_region_separated_src_video_layout
├── intra_refresh_column_based_layered_src_general_layout
├── intra_refresh_column_based_layered_src_video_layout
├── intra_refresh_column_based_midway_layered_src_general_layout
├── intra_refresh_column_based_midway_layered_src_video_layout
├── intra_refresh_column_based_midway_separated_src_general_layout
├── intra_refresh_column_based_midway_separated_src_video_layout
├── intra_refresh_column_based_separated_src_general_layout
├── intra_refresh_column_based_separated_src_video_layout
├── intra_refresh_picture_partition_layered_src_general_layout
├── intra_refresh_picture_partition_layered_src_video_layout
├── intra_refresh_picture_partition_midway_layered_src_general_layout
├── intra_refresh_picture_partition_midway_layered_src_video_layout
├── intra_refresh_picture_partition_midway_separated_src_general_layout
├── intra_refresh_picture_partition_midway_separated_src_video_layout
├── intra_refresh_picture_partition_separated_src_general_layout
├── intra_refresh_picture_partition_separated_src_video_layout
├── intra_refresh_row_based_empty_region_layered_src_general_layout
├── intra_refresh_row_based_empty_region_layered_src_video_layout
├── intra_refresh_row_based_empty_region_separated_src_general_layout
├── intra_refresh_row_based_empty_region_separated_src_video_layout
├── intra_refresh_row_based_layered_src_general_layout
├── intra_refresh_row_based_layered_src_video_layout
├── intra_refresh_row_based_midway_layered_src_general_layout
├── intra_refresh_row_based_midway_layered_src_video_layout
├── intra_refresh_row_based_midway_separated_src_general_layout
├── intra_refresh_row_based_midway_separated_src_video_layout
├── intra_refresh_row_based_separated_src_general_layout
├── intra_refresh_row_based_separated_src_video_layout
├── quality_level_layered_src_general_layout
├── quality_level_layered_src_video_layout
├── quality_level_separated_src_general_layout
├── quality_level_separated_src_video_layout
├── quantization_map_delta_layered_src_general_layout
├── quantization_map_delta_layered_src_video_layout
├── quantization_map_delta_rc_cbr_layered_src_general_layout
├── quantization_map_delta_rc_cbr_layered_src_video_layout
├── quantization_map_delta_rc_cbr_separated_src_general_layout
├── quantization_map_delta_rc_cbr_separated_src_video_layout
├── quantization_map_delta_rc_disable_layered_src_general_layout
├── quantization_map_delta_rc_disable_layered_src_video_layout
├── quantization_map_delta_rc_disable_separated_src_general_layout
├── quantization_map_delta_rc_disable_separated_src_video_layout
├── quantization_map_delta_rc_vbr_layered_src_general_layout
├── quantization_map_delta_rc_vbr_layered_src_video_layout
├── quantization_map_delta_rc_vbr_separated_src_general_layout
├── quantization_map_delta_rc_vbr_separated_src_video_layout
├── quantization_map_delta_separated_src_general_layout
├── quantization_map_delta_separated_src_video_layout
├── quantization_map_emphasis_cbr_layered_src_general_layout
├── quantization_map_emphasis_cbr_layered_src_video_layout
├── quantization_map_emphasis_cbr_separated_src_general_layout
├── quantization_map_emphasis_cbr_separated_src_video_layout
├── quantization_map_emphasis_vbr_layered_src_general_layout
├── quantization_map_emphasis_vbr_layered_src_video_layout
├── quantization_map_emphasis_vbr_separated_src_general_layout
├── quantization_map_emphasis_vbr_separated_src_video_layout
├── query_with_status_layered_src_general_layout
├── query_with_status_layered_src_video_layout
├── query_with_status_separated_src_general_layout
├── query_with_status_separated_src_video_layout
├── rc_cbr_layered_src_general_layout
├── rc_cbr_layered_src_video_layout
├── rc_cbr_separated_src_general_layout
├── rc_cbr_separated_src_video_layout
├── rc_disable_layered_src_general_layout
├── rc_disable_layered_src_video_layout
├── rc_disable_separated_src_general_layout
├── rc_disable_separated_src_video_layout
├── rc_vbr_layered_src_general_layout
├── rc_vbr_layered_src_video_layout
├── rc_vbr_separated_src_general_layout
├── rc_vbr_separated_src_video_layout
├── resolution_change_dpb_layered_src_general_layout
├── resolution_change_dpb_layered_src_video_layout
├── resolution_change_dpb_separated_src_general_layout
├── resolution_change_dpb_separated_src_video_layout
├── resources_without_profiles_layered_src_general_layout
├── resources_without_profiles_layered_src_video_layout
├── resources_without_profiles_separated_src_general_layout
├── resources_without_profiles_separated_src_video_layout
├── usage_layered_src_general_layout
├── usage_layered_src_video_layout
├── usage_separated_src_general_layout
└── usage_separated_src_video_layout
```

## Test Families

- H.264/H.265 cases come from `g_EncodeTests`, whose entries specify codec clip, GOP count, frame pattern, frame indices, reference slots, active references, and encoder options ([vktVideoEncodeTests.cpp](../../../modules/vulkan/video/vktVideoEncodeTests.cpp#L416-L432), [vktVideoEncodeTests.cpp](../../../modules/vulkan/video/vktVideoEncodeTests.cpp#L432-L1088)).
- Test names combine the base encode test name with `_layered_src` or `_separated_src`, and `_general_layout` or `_video_layout` ([vktVideoEncodeTests.cpp](../../../modules/vulkan/video/vktVideoEncodeTests.cpp#L172-L269), [vktVideoEncodeTests.cpp](../../../modules/vulkan/video/vktVideoEncodeTests.cpp#L3991-L3997)).
- Encode options cover status queries, variable/constant/disabled rate control, swapped order, quality level, maintenance1 resource behavior, quantization maps, and intra-refresh modes ([vktVideoEncodeTests.cpp](../../../modules/vulkan/video/vktVideoEncodeTests.cpp#L356-L380)).

## Parameter Dimensions and Observed Values

| Dimension | Observed values or source |
|---|---|
| Codec groups in this file | H.264 and H.265 leaves are generated here; AV1 is delegated to `vktVideoEncodeTestsAV1.cpp` ([vktVideoEncodeTests.cpp](../../../modules/vulkan/video/vktVideoEncodeTests.cpp#L3983-L4013)). |
| Source image mode | `layeredSrc` true and false ([vktVideoEncodeTests.cpp](../../../modules/vulkan/video/vktVideoEncodeTests.cpp#L3986-L3987)). |
| Image layout mode | `generalLayout` true and false ([vktVideoEncodeTests.cpp](../../../modules/vulkan/video/vktVideoEncodeTests.cpp#L3988-L3989)). |
| Frame/reference patterns | Explicit `EncodeTestParam` fields encode GOP count, frame type sequence, frame indices, reference slots, and encoder options ([vktVideoEncodeTests.cpp](../../../modules/vulkan/video/vktVideoEncodeTests.cpp#L416-L432)). |

## Support and Feature Requirements

Encode cases call `VideoDevice::checkSupport`, require `VK_KHR_synchronization2`, require H.264 or H.265 encode extensions by test type, require `VK_KHR_video_maintenance1` for inline-query/resources-without-profiles tests, require `VK_KHR_video_encode_quantization_map` for quantization-map tests, require `VK_KHR_video_encode_intra_refresh` for intra-refresh tests, and require unified image layouts plus `unifiedImageLayoutsVideo` for general-layout cases ([vktVideoEncodeTests.cpp](../../../modules/vulkan/video/vktVideoEncodeTests.cpp#L3868-L3968)). Runtime capability gates also reject unsupported query status, quantization map flags, P/B reference support, rate-control modes, and dimensions outside supported extents ([vktVideoEncodeTests.cpp](../../../modules/vulkan/video/vktVideoEncodeTests.cpp#L2053-L2226), [vktVideoEncodeTests.cpp](../../../modules/vulkan/video/vktVideoEncodeTests.cpp#L2678-L2686)).

## Verification Methods

- Query-status tests check encode query results after command submission and fail on unexpected query result status ([vktVideoEncodeTests.cpp](../../../modules/vulkan/video/vktVideoEncodeTests.cpp#L3329-L3356)).
- `verifyEncodedBitstream()` decodes the output bitstream and compares PSNR against thresholds, including special PSNR-difference checks for quantization-map tests ([vktVideoEncodeTests.cpp](../../../modules/vulkan/video/vktVideoEncodeTests.cpp#L3358-L3499)).
- Intra-refresh paths compute and validate refresh cycle behavior before final bitstream verification ([vktVideoEncodeTests.cpp](../../../modules/vulkan/video/vktVideoEncodeTests.cpp#L3714-L3838)).

## Test Principles

- H.264/H.265 tests validate encoded content after round-tripping through decode/quality checks instead of only checking encode command success ([vktVideoEncodeTests.cpp](../../../modules/vulkan/video/vktVideoEncodeTests.cpp#L3358-L3838)).
- Registration separates codec group names from test names so H.264 and H.265 can share many base test-name strings under different codec groups ([vktVideoEncodeTests.cpp](../../../modules/vulkan/video/vktVideoEncodeTests.cpp#L3997-L4003)).

## Notes / Uncertainties

- `doc/testspecs/VK/apitests.adoc` was inspected as required; text search found no video-specific section, so category-specific claims in this page are based on inspected `external/vulkancts/` source and `mustpass/main/vk-default/video.txt` evidence.
- `video.encode.av1` is registered through this file but documented in [vktVideoEncodeTestsAV1](vktVideoEncodeTestsAV1.md) because its source file contains the AV1-specific registration and parameter loops.
