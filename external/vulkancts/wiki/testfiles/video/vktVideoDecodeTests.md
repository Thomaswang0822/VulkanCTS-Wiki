# vktVideoDecodeTests

## Overview

`vktVideoDecodeTests.cpp` registers the `video.decode` group with H.264, H.265, AV1, and VP9 child groups. It generates decode cases from clip definitions, DPB layout mode, and image layout mode, and it separately registers interleaving decode tests ([vktVideoDecodeTests.cpp](../../../modules/vulkan/video/vktVideoDecodeTests.cpp#L1976-L2033)).

## Role of File

| Aspect | Evidence-backed description |
|---|---|
| Registration role | Creates `decode` plus `h264`, `h265`, `av1`, and `vp9` groups, then adds generated test cases to the codec-specific group selected by `getTestCodec()` ([vktVideoDecodeTests.cpp](../../../modules/vulkan/video/vktVideoDecodeTests.cpp#L1976-L2033)). |
| Implementation role | Parses video streams, records decode work, downloads frames, and validates frame contents by checksum or AV1 film-grain PSNR range ([vktVideoDecodeTests.cpp](../../../modules/vulkan/video/vktVideoDecodeTests.cpp#L67-L142), [vktVideoDecodeTests.cpp](../../../modules/vulkan/video/vktVideoDecodeTests.cpp#L1483-L1557)). |

## Registration Hierarchy

```text
video.decode
├── av1
├── h264
├── h265
└── vp9
video.decode.h264
├── 420_8bit_high_176x144_30frames_layered_dpb_general_layout
├── 420_8bit_high_176x144_30frames_layered_dpb_video_layout
├── 420_8bit_high_176x144_30frames_separated_dpb_general_layout
├── 420_8bit_high_176x144_30frames_separated_dpb_video_layout
├── h265_interleaved_layered_dpb_general_layout
├── h265_interleaved_layered_dpb_video_layout
├── h265_interleaved_separated_dpb_general_layout
├── h265_interleaved_separated_dpb_video_layout
├── i_layered_dpb_general_layout
├── i_layered_dpb_video_layout
├── i_p_b_13_layered_dpb_general_layout
├── i_p_b_13_layered_dpb_video_layout
├── i_p_b_13_not_matching_order_layered_dpb_general_layout
├── i_p_b_13_not_matching_order_layered_dpb_video_layout
├── i_p_b_13_not_matching_order_separated_dpb_general_layout
├── i_p_b_13_not_matching_order_separated_dpb_video_layout
├── i_p_b_13_separated_dpb_general_layout
├── i_p_b_13_separated_dpb_video_layout
├── i_p_layered_dpb_general_layout
├── i_p_layered_dpb_video_layout
├── i_p_not_matching_order_layered_dpb_general_layout
├── i_p_not_matching_order_layered_dpb_video_layout
├── i_p_not_matching_order_separated_dpb_general_layout
├── i_p_not_matching_order_separated_dpb_video_layout
├── i_p_separated_dpb_general_layout
├── i_p_separated_dpb_video_layout
├── i_separated_dpb_general_layout
├── i_separated_dpb_video_layout
├── inline_query_with_status_layered_dpb_general_layout
├── inline_query_with_status_layered_dpb_video_layout
├── inline_query_with_status_separated_dpb_general_layout
├── inline_query_with_status_separated_dpb_video_layout
├── inline_session_params_layered_dpb_general_layout
├── inline_session_params_layered_dpb_video_layout
├── inline_session_params_separated_dpb_general_layout
├── inline_session_params_separated_dpb_video_layout
├── interleaved_layered_dpb_general_layout
├── interleaved_layered_dpb_video_layout
├── interleaved_separated_dpb_general_layout
├── interleaved_separated_dpb_video_layout
├── query_with_status_layered_dpb_general_layout
├── query_with_status_layered_dpb_video_layout
├── query_with_status_separated_dpb_general_layout
├── query_with_status_separated_dpb_video_layout
├── relaxed_session_params_layered_dpb_general_layout
├── relaxed_session_params_layered_dpb_video_layout
├── relaxed_session_params_separated_dpb_general_layout
├── relaxed_session_params_separated_dpb_video_layout
├── resolution_change_dpb_layered_dpb_general_layout
├── resolution_change_dpb_layered_dpb_video_layout
├── resolution_change_dpb_separated_dpb_general_layout
├── resolution_change_dpb_separated_dpb_video_layout
├── resolution_change_layered_dpb_general_layout
├── resolution_change_layered_dpb_video_layout
├── resolution_change_separated_dpb_general_layout
├── resolution_change_separated_dpb_video_layout
├── resources_without_profiles_layered_dpb_general_layout
├── resources_without_profiles_layered_dpb_video_layout
├── resources_without_profiles_separated_dpb_general_layout
└── resources_without_profiles_separated_dpb_video_layout
video.decode.h265
├── 420_8bit_main_176x144_30frames_layered_dpb_general_layout
├── 420_8bit_main_176x144_30frames_layered_dpb_video_layout
├── 420_8bit_main_176x144_30frames_separated_dpb_general_layout
├── 420_8bit_main_176x144_30frames_separated_dpb_video_layout
├── i_layered_dpb_general_layout
├── i_layered_dpb_video_layout
├── i_p_b_13_layered_dpb_general_layout
├── i_p_b_13_layered_dpb_video_layout
├── i_p_b_13_not_matching_order_layered_dpb_general_layout
├── i_p_b_13_not_matching_order_layered_dpb_video_layout
├── i_p_b_13_not_matching_order_separated_dpb_general_layout
├── i_p_b_13_not_matching_order_separated_dpb_video_layout
├── i_p_b_13_separated_dpb_general_layout
├── i_p_b_13_separated_dpb_video_layout
├── i_p_layered_dpb_general_layout
├── i_p_layered_dpb_video_layout
├── i_p_not_matching_order_layered_dpb_general_layout
├── i_p_not_matching_order_layered_dpb_video_layout
├── i_p_not_matching_order_separated_dpb_general_layout
├── i_p_not_matching_order_separated_dpb_video_layout
├── i_p_separated_dpb_general_layout
├── i_p_separated_dpb_video_layout
├── i_separated_dpb_general_layout
├── i_separated_dpb_video_layout
├── inline_query_with_status_layered_dpb_general_layout
├── inline_query_with_status_layered_dpb_video_layout
├── inline_query_with_status_separated_dpb_general_layout
├── inline_query_with_status_separated_dpb_video_layout
├── inline_session_params_layered_dpb_general_layout
├── inline_session_params_layered_dpb_video_layout
├── inline_session_params_separated_dpb_general_layout
├── inline_session_params_separated_dpb_video_layout
├── long_term_reference_layered_dpb_general_layout
├── long_term_reference_layered_dpb_video_layout
├── long_term_reference_separated_dpb_general_layout
├── long_term_reference_separated_dpb_video_layout
├── query_with_status_layered_dpb_general_layout
├── query_with_status_layered_dpb_video_layout
├── query_with_status_separated_dpb_general_layout
├── query_with_status_separated_dpb_video_layout
├── relaxed_session_params_layered_dpb_general_layout
├── relaxed_session_params_layered_dpb_video_layout
├── relaxed_session_params_separated_dpb_general_layout
├── relaxed_session_params_separated_dpb_video_layout
├── resources_without_profiles_layered_dpb_general_layout
├── resources_without_profiles_layered_dpb_video_layout
├── resources_without_profiles_separated_dpb_general_layout
├── resources_without_profiles_separated_dpb_video_layout
├── slist_a_layered_dpb_general_layout
├── slist_a_layered_dpb_video_layout
├── slist_a_separated_dpb_general_layout
├── slist_a_separated_dpb_video_layout
├── slist_b_layered_dpb_general_layout
├── slist_b_layered_dpb_video_layout
├── slist_b_separated_dpb_general_layout
└── slist_b_separated_dpb_video_layout
video.decode.av1
├── allintra_8_layered_dpb_general_layout
├── allintra_8_layered_dpb_video_layout
├── allintra_8_separated_dpb_general_layout
├── allintra_8_separated_dpb_video_layout
├── allintra_nosetup_8_layered_dpb_general_layout
├── allintra_nosetup_8_layered_dpb_video_layout
├── allintra_nosetup_8_separated_dpb_general_layout
├── allintra_nosetup_8_separated_dpb_video_layout
├── allintrabc_8_layered_dpb_general_layout
├── allintrabc_8_layered_dpb_video_layout
├── allintrabc_8_separated_dpb_general_layout
├── allintrabc_8_separated_dpb_video_layout
├── argon_filmgrain_10_test1019_layered_dpb_general_layout
├── argon_filmgrain_10_test1019_layered_dpb_video_layout
├── argon_filmgrain_10_test1019_separated_dpb_general_layout
├── argon_filmgrain_10_test1019_separated_dpb_video_layout
├── basic_10_layered_dpb_general_layout
├── basic_10_layered_dpb_video_layout
├── basic_10_separated_dpb_general_layout
├── basic_10_separated_dpb_video_layout
├── basic_8_layered_dpb_general_layout
├── basic_8_layered_dpb_video_layout
├── basic_8_not_matching_order_layered_dpb_general_layout
├── basic_8_not_matching_order_layered_dpb_video_layout
├── basic_8_not_matching_order_separated_dpb_general_layout
├── basic_8_not_matching_order_separated_dpb_video_layout
├── basic_8_separated_dpb_general_layout
├── basic_8_separated_dpb_video_layout
├── cdef_10_layered_dpb_general_layout
├── cdef_10_layered_dpb_video_layout
├── cdef_10_separated_dpb_general_layout
├── cdef_10_separated_dpb_video_layout
├── cdfupdate_8_layered_dpb_general_layout
├── cdfupdate_8_layered_dpb_video_layout
├── cdfupdate_8_separated_dpb_general_layout
├── cdfupdate_8_separated_dpb_video_layout
├── filmgrain_8_layered_dpb_general_layout
├── filmgrain_8_layered_dpb_video_layout
├── filmgrain_8_separated_dpb_general_layout
├── filmgrain_8_separated_dpb_video_layout
├── forwardkeyframe_10_layered_dpb_general_layout
├── forwardkeyframe_10_layered_dpb_video_layout
├── forwardkeyframe_10_separated_dpb_general_layout
├── forwardkeyframe_10_separated_dpb_video_layout
├── globalmotion_8_layered_dpb_general_layout
├── globalmotion_8_layered_dpb_video_layout
├── globalmotion_8_separated_dpb_general_layout
├── globalmotion_8_separated_dpb_video_layout
├── golden_frame_layered_dpb_general_layout
├── golden_frame_layered_dpb_video_layout
├── golden_frame_separated_dpb_general_layout
├── golden_frame_separated_dpb_video_layout
├── i_layered_dpb_general_layout
├── i_layered_dpb_video_layout
├── i_p_layered_dpb_general_layout
├── i_p_layered_dpb_video_layout
├── i_p_not_matching_order_layered_dpb_general_layout
├── i_p_not_matching_order_layered_dpb_video_layout
├── i_p_not_matching_order_separated_dpb_general_layout
├── i_p_not_matching_order_separated_dpb_video_layout
├── i_p_separated_dpb_general_layout
├── i_p_separated_dpb_video_layout
├── i_separated_dpb_general_layout
├── i_separated_dpb_video_layout
├── inline_session_params_layered_dpb_general_layout
├── inline_session_params_layered_dpb_video_layout
├── inline_session_params_separated_dpb_general_layout
├── inline_session_params_separated_dpb_video_layout
├── loopfilter_10_layered_dpb_general_layout
├── loopfilter_10_layered_dpb_video_layout
├── loopfilter_10_separated_dpb_general_layout
├── loopfilter_10_separated_dpb_video_layout
├── lossless_10_layered_dpb_general_layout
├── lossless_10_layered_dpb_video_layout
├── lossless_10_separated_dpb_general_layout
├── lossless_10_separated_dpb_video_layout
├── orderhint_10_layered_dpb_general_layout
├── orderhint_10_layered_dpb_video_layout
├── orderhint_10_separated_dpb_general_layout
├── orderhint_10_separated_dpb_video_layout
├── relaxed_session_params_layered_dpb_general_layout
├── relaxed_session_params_layered_dpb_video_layout
├── relaxed_session_params_separated_dpb_general_layout
├── relaxed_session_params_separated_dpb_video_layout
├── sizeup_8_layered_dpb_general_layout
├── sizeup_8_layered_dpb_video_layout
├── sizeup_8_separated_dpb_general_layout
├── sizeup_8_separated_dpb_video_layout
├── superres_8_layered_dpb_general_layout
├── superres_8_layered_dpb_video_layout
├── superres_8_separated_dpb_general_layout
├── superres_8_separated_dpb_video_layout
├── svcl1t2_8_layered_dpb_general_layout
├── svcl1t2_8_layered_dpb_video_layout
├── svcl1t2_8_separated_dpb_general_layout
└── svcl1t2_8_separated_dpb_video_layout
video.decode.vp9
├── 10bits_layered_dpb_general_layout
├── 10bits_layered_dpb_video_layout
├── 10bits_separated_dpb_general_layout
├── 10bits_separated_dpb_video_layout
├── 351x287_layered_dpb_general_layout
├── 351x287_layered_dpb_video_layout
├── 351x287_separated_dpb_general_layout
├── 351x287_separated_dpb_video_layout
├── basic_10_layered_dpb_general_layout
├── basic_10_layered_dpb_video_layout
├── basic_10_not_matching_order_layered_dpb_general_layout
├── basic_10_not_matching_order_layered_dpb_video_layout
├── basic_10_not_matching_order_separated_dpb_general_layout
├── basic_10_not_matching_order_separated_dpb_video_layout
├── basic_10_separated_dpb_general_layout
├── basic_10_separated_dpb_video_layout
├── inter_intra_only_layered_dpb_general_layout
├── inter_intra_only_layered_dpb_video_layout
├── inter_intra_only_separated_dpb_general_layout
├── inter_intra_only_separated_dpb_video_layout
├── intra_only_layered_dpb_general_layout
├── intra_only_layered_dpb_video_layout
├── intra_only_separated_dpb_general_layout
├── intra_only_separated_dpb_video_layout
├── keyframe_10_layered_dpb_general_layout
├── keyframe_10_layered_dpb_video_layout
├── keyframe_10_separated_dpb_general_layout
├── keyframe_10_separated_dpb_video_layout
├── lf_layered_dpb_general_layout
├── lf_layered_dpb_video_layout
├── lf_separated_dpb_general_layout
├── lf_separated_dpb_video_layout
├── quant_00_layered_dpb_general_layout
├── quant_00_layered_dpb_video_layout
├── quant_00_separated_dpb_general_layout
├── quant_00_separated_dpb_video_layout
├── quant_26_layered_dpb_general_layout
├── quant_26_layered_dpb_video_layout
├── quant_26_separated_dpb_general_layout
├── quant_26_separated_dpb_video_layout
├── quant_59_layered_dpb_general_layout
├── quant_59_layered_dpb_video_layout
├── quant_59_separated_dpb_general_layout
├── quant_59_separated_dpb_video_layout
├── resize_1_2_layered_dpb_general_layout
├── resize_1_2_layered_dpb_video_layout
├── resize_1_2_separated_dpb_general_layout
├── resize_1_2_separated_dpb_video_layout
├── resize_layered_dpb_general_layout
├── resize_layered_dpb_video_layout
├── resize_separated_dpb_general_layout
├── resize_separated_dpb_video_layout
├── seg_key_layered_dpb_general_layout
├── seg_key_layered_dpb_video_layout
├── seg_key_separated_dpb_general_layout
├── seg_key_separated_dpb_video_layout
├── show_existing_frames_10_layered_dpb_general_layout
├── show_existing_frames_10_layered_dpb_video_layout
├── show_existing_frames_10_separated_dpb_general_layout
├── show_existing_frames_10_separated_dpb_video_layout
├── svc_layered_dpb_general_layout
├── svc_layered_dpb_video_layout
├── svc_separated_dpb_general_layout
├── svc_separated_dpb_video_layout
├── tile_1x2_layered_dpb_general_layout
├── tile_1x2_layered_dpb_video_layout
├── tile_1x2_separated_dpb_general_layout
├── tile_1x2_separated_dpb_video_layout
├── tile_1x4_layered_dpb_general_layout
├── tile_1x4_layered_dpb_video_layout
├── tile_1x4_separated_dpb_general_layout
├── tile_1x4_separated_dpb_video_layout
├── tile_1x8_layered_dpb_general_layout
├── tile_1x8_layered_dpb_video_layout
├── tile_1x8_separated_dpb_general_layout
├── tile_1x8_separated_dpb_video_layout
├── tile_4x4_layered_dpb_general_layout
├── tile_4x4_layered_dpb_video_layout
├── tile_4x4_separated_dpb_general_layout
└── tile_4x4_separated_dpb_video_layout
```

## Test Families

- Base decode cases come from `g_DecodeTests`, which maps codec-specific `TestType` values to clip names, frame counts, and decoder options such as status queries, cached decoding, inline session parameters, relaxed session parameters, film-grain handling, and VP9 special streams ([vktVideoDecodeTests.cpp](../../../modules/vulkan/video/vktVideoDecodeTests.cpp#L150-L241), [vktVideoDecodeTests.cpp](../../../modules/vulkan/video/vktVideoDecodeTests.cpp#L590-L689)).
- Interleaving cases are registered from `g_InterleavingTests` and include H.264/H.264 and H.264/H.265 stream pairs ([vktVideoDecodeTests.cpp](../../../modules/vulkan/video/vktVideoDecodeTests.cpp#L691-L703), [vktVideoDecodeTests.cpp](../../../modules/vulkan/video/vktVideoDecodeTests.cpp#L2006-L2024)).
- Generated names append `_layered_dpb` or `_separated_dpb`, then `_general_layout` or `_video_layout` to the base test-type name ([vktVideoDecodeTests.cpp](../../../modules/vulkan/video/vktVideoDecodeTests.cpp#L771-L785)).

## Parameter Dimensions and Observed Values

| Dimension | Observed values or source |
|---|---|
| Codec groups | H.264, H.265, AV1, and VP9 ([vktVideoDecodeTests.cpp](../../../modules/vulkan/video/vktVideoDecodeTests.cpp#L1979-L1983)). |
| DPB image mode | `layeredDpb` true and false ([vktVideoDecodeTests.cpp](../../../modules/vulkan/video/vktVideoDecodeTests.cpp#L1985-L1986)). |
| Image layout mode | `generalLayout` true and false ([vktVideoDecodeTests.cpp](../../../modules/vulkan/video/vktVideoDecodeTests.cpp#L1987-L1988)). |
| Clip and stream options | Explicit entries in `g_DecodeTests`, including H.264/H.265/AV1/VP9 clips and decoder options ([vktVideoDecodeTests.cpp](../../../modules/vulkan/video/vktVideoDecodeTests.cpp#L590-L689)). |

## Support and Feature Requirements

Decode cases call `VideoDevice::checkSupport`, require `VK_KHR_synchronization2`, require the codec-specific decode extension, add maintenance1 or maintenance2 for tests that use those options, and require unified image layouts when generated with general layout ([vktVideoDecodeTests.cpp](../../../modules/vulkan/video/vktVideoDecodeTests.cpp#L1749-L1931)). Interleaving cases require synchronization2 and the involved codec decode extensions ([vktVideoDecodeTests.cpp](../../../modules/vulkan/video/vktVideoDecodeTests.cpp#L1935-L1970)).

## Verification Methods

- Decoded frames are downloaded from video images, including deinterleaving for two-plane formats and per-plane copies for three-plane formats ([vktVideoDecodeTests.cpp](../../../modules/vulkan/video/vktVideoDecodeTests.cpp#L1181-L1238)).
- Normal decode cases compare downloaded-frame MD5 checksums with `checksumForClipFrame()` reference data; AV1 film-grain cases compare PSNR against a bounded range when checksum comparison is not the criterion ([vktVideoDecodeTests.cpp](../../../modules/vulkan/video/vktVideoDecodeTests.cpp#L1483-L1557), [vktVideoClipInfo.cpp](../../../modules/vulkan/video/vktVideoClipInfo.cpp#L20-L28)).
- Interleaving cases validate checksums for each decoded stream and require the total checked-frame count to match expectations ([vktVideoDecodeTests.cpp](../../../modules/vulkan/video/vktVideoDecodeTests.cpp#L1658-L1701)).

## Test Principles

- The same stream definitions are run across layered/separated DPB and general/video layout dimensions to exercise resource layout variation ([vktVideoDecodeTests.cpp](../../../modules/vulkan/video/vktVideoDecodeTests.cpp#L1985-L2026)).
- Verification is content-based: successful decode is not enough unless output frame checksums or film-grain PSNR criteria match inspected references ([vktVideoDecodeTests.cpp](../../../modules/vulkan/video/vktVideoDecodeTests.cpp#L1483-L1557)).

## Notes / Uncertainties

