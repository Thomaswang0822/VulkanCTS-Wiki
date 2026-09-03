# Understanding Brief: H.264 and H.265 encode tests

## One-Sentence Test Purpose

This test checks whether Vulkan H.264 and H.265 video encode sessions can consume the selected YUV 4:2:0 pictures, construct valid codec state and reference relationships, write an elementary bitstream, and produce decoded pictures with acceptable quality under the selected encode option.

## Background Knowledge

### Encode input pictures, reference pictures, and the DPB

A video encode operation reads an encode input picture and optional active reference pictures, then writes compressed data to a bitstream buffer. When reference picture setup is requested, the encoder also associates a reconstructed picture with a DPB slot for later use. The Vulkan encode operation model and the required image access stage are described in the [video encode operation steps](../../../../vulkan-docs/src/chapters/video/encode.adoc#L199-L235).

Why it matters here:
- The CTS creates YUV images for input pictures and DPB images for reconstructed/reference pictures.
- P and B cases depend on the reference lists and slot state, while I and IDR cases begin without active references.

### Codec picture types and coding blocks

H.264 uses macroblocks, with a 16 by 16 minimum coding block for the intra-refresh calculations in this test. H.265 uses coding tree units and coding units; the test chooses a minimum block size from the supported CTB sizes. The codec-specific picture and slice types are defined for [H.264](../../../../vulkan-docs/src/chapters/video/h264_encode.adoc#L207-L265) and [H.265](../../../../vulkan-docs/src/chapters/video/h265_encode.adoc#L240-L301).

Why it matters here:
- Coded extents must be within the profile's queried `minCodedExtent` and `maxCodedExtent`.
- Intra-refresh region counts depend on coding-block rows or columns and on the codec's slice or slice-segment limits.

## One Concrete Example

Consider `video.encode.h264.i_p_b_13_layered_src_video_layout`. The test uses two GOPs of a 14-picture pattern. The pattern contains an IDR picture, a P picture, and B pictures, with the encode order `{0, 3, 1, 2, 6, 4, 5, 9, 7, 8, 12, 10, 11, 13}`. It stores source pictures in one array image and refers to each array layer through a separate `VkVideoPictureResourceInfoKHR`. The first picture has no active reference; later P and B pictures use the DPB slots listed by the test definition. The `video` layout variant uses `VK_IMAGE_LAYOUT_VIDEO_ENCODE_SRC_KHR` for input pictures and the video DPB layout for reference images. The implementation records one `vkCmdEncodeVideoKHR` operation per picture, waits for its submission, advances the bitstream offset from encode feedback, and later decodes the accumulated H.264 byte stream for PSNR checking. The registration and test-name construction are in [`createVideoEncodeTests`](../../../modules/vulkan/video/vktVideoEncodeTests.cpp#L3979-L4015), while the 13-picture definitions are in [`g_EncodeTests`](../../../modules/vulkan/video/vktVideoEncodeTests.cpp#L667-L703).

## End-to-End Test Flow

```text
[host] select the H.264 or H.265 test definition, source-image mode, and image-layout mode
[host] initialize the codec operation, GOP pattern, DPB slot count, option flags, QP values, and encode/decode profiles
[host] query source and DPB formats, obtain encode/decode/transfer queues, and check required device functionality
[host] query codec, rate-control, quantization-map, intra-refresh, extent, DPB, and query-status capabilities
[host] create and bind the video encode session
[host] create quantization-map images when requested and copy their generated values from host-visible buffers
[host] create one or two codec session-parameter objects and retrieve encoded VPS/SPS/PPS headers
[host] create DPB images, picture resources, reference-slot structures, source images, the host-visible bitstream buffer, and encode queries
[host] load YUV frames from the selected clip, convert NV12 data to I420, and upload it to source images
[host] configure rate control, quality level, command buffers, and per-frame codec picture/reference information
[host] record and submit one encode operation per frame, using ordinary or swapped submission order
[device] read the input and active reference pictures and write encoded bytes and optional reconstructed/reference data
[host] wait for submissions, consume bitstream offset and bytes-written query feedback, and submit swapped command buffers when requested
[host] parse and decode the encoded H.264 or H.265 byte stream
[host] convert decoded NV12 output to I420, compare it with the input, apply quantization-map checks, and decide pass, warning, or fail
```

The ordered implementation call chain is [`iterate`](../../../modules/vulkan/video/vktVideoEncodeTests.cpp#L3819-L3842). Per-frame command recording, including reference lists, session state, optional inline queries, quantization maps, intra refresh, and `vkCmdEncodeVideoKHR`, is in [`encodeFrame`](../../../modules/vulkan/video/vktVideoEncodeTests.cpp#L2981-L3332).

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- The test does not generate a shader or other programmable GPU program. Encoding uses Vulkan video commands and codec-specific Video Std structures.
- H.264 session parameters contain one SPS and one PPS. H.265 session parameters contain one VPS, one SPS, and one PPS. The test retrieves encoded parameter bytes before encoding and prefixes them to the bitstream; a second set is created for the half-resolution session in `resolution_change_dpb` ([`setupSessionParameters`](../../../modules/vulkan/video/vktVideoEncodeTests.cpp#L2484-L2569), [`getSessionParametersHeaders`](../../../modules/vulkan/video/vktVideoEncodeTests.cpp#L2799-L2860)).
- The bitstream buffer is sized from the image format and coded extent, with each frame region aligned to `minBitstreamBufferSizeAlignment` ([`prepareEncodeBuffer`](../../../modules/vulkan/video/vktVideoEncodeTests.cpp#L3507-L3533)).
- Quantization-map tests generate two or three constant-sided map images. Delta-map tests use a third map with different left and right values; emphasis-map tests use a second map with different sides ([`setupQuantizationMapResources`](../../../modules/vulkan/video/vktVideoEncodeTests.cpp#L2278-L2482)).

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Source picture image or layered source image | yes | yes | read by video encode | no | Holds uploaded YUV input pictures. |
| DPB image or separate DPB images | yes | yes | read as references and written as reconstructed pictures | no | Carries reference pictures and slot state for P/B and multi-frame cases. |
| Quantization-map images | yes, only for map cases | yes | read by video encode | no | Supplies delta or emphasis values for the coded extent. |
| Host-visible encode bitstream buffer | yes | yes | written by video encode | yes | Receives session headers and encoded bytes; the host passes it to the decoder. |
| Encode query pool | yes | yes | written by encode feedback | yes | Supplies bitstream offset and bytes-written feedback, and optionally completion status. |
| Video session and session parameters | yes | yes | used by video coding | indirectly | Holds codec profile state and H.264/H.265 parameter sets. |
| Host-side input/output vectors | yes | no | no | yes | Provide I420 input data and receive converted decoded output for comparison. |

For the `layered_src` variant, one source image has one array layer per processed frame. For `separated_src`, the test creates one image per frame. The image creation and picture-resource mapping are in [`prepareInputImages`](../../../modules/vulkan/video/vktVideoEncodeTests.cpp#L2691-L2728). The input image is normally transitioned to `VK_IMAGE_LAYOUT_VIDEO_ENCODE_SRC_KHR`; the `general_layout` variant uses `VK_IMAGE_LAYOUT_GENERAL` and requires unified video image layouts ([`checkSupport`](../../../modules/vulkan/video/vktVideoEncodeTests.cpp#L3868-L3970), [specification layout rules](../../../../vulkan-docs/src/chapters/video/encode.adoc#L42-L77)).

## What Is Checked

- The test requires the queried encode capability to support `VK_VIDEO_ENCODE_FEEDBACK_BITSTREAM_BYTES_WRITTEN_BIT_KHR`. It uses query feedback to advance and align the bitstream offset. If status queries are selected, it also requires `VK_QUERY_RESULT_STATUS_COMPLETE_KHR` for each checked encode operation ([`processQueryPoolResults`](../../../modules/vulkan/video/vktVideoEncodeTests.cpp#L1412-L1433)).
- The host constructs a byte-stream demuxer and a basic decoder for the same codec, decodes the expected number of processed frames, converts each result to I420, and compares it to the corresponding uploaded frame ([`verifyEncodedBitstream`](../../../modules/vulkan/video/vktVideoEncodeTests.cpp#L3358-L3505)).
- Ordinary cases use a PSNR threshold of 30.0. Rate-control-disabled cases use 20.0. A result above 10.0 but below its applicable lower threshold returns a quality warning; a result at or below 10.0 fails.
- Emphasis-map case `NALIdx == 1` must have a larger PSNR difference than the first frame. Delta-map case `NALIdx == 2` must not report a positive PSNR difference for the left half relative to the right half. The expected lower quality of the mapped second frame is exempted from the ordinary threshold failure path.
- A successful result reports the number of correctly encoded frames. A parser that returns fewer frames is treated as an internal error, because the produced bitstream did not contain the expected output sequence.

## Behavior Parameter Identification

> **Behavior parameter:** registered test case leaf returned by `getTestName`, with codec (`h264` or `h265`) as a parallel syntax axis.
>
> **Candidate values:** `i`, `rc_vbr`, `rc_cbr`, `rc_disable`, `quality_level`, `quantization_map_delta_rc_vbr`, `quantization_map_delta_rc_cbr`, `quantization_map_delta_rc_disable`, `quantization_map_delta`, `quantization_map_emphasis_cbr`, `quantization_map_emphasis_vbr`, `usage`, `i_p`, `i_p_not_matching_order`, `i_p_b_13`, `resolution_change_dpb`, `query_with_status`, `inline_query`, `resources_without_profiles`, `intra_refresh_picture_partition`, `intra_refresh_any_block_based`, `intra_refresh_row_based`, `intra_refresh_column_based`, `intra_refresh_any_block_based_empty_region`, `intra_refresh_row_based_empty_region`, `intra_refresh_column_based_empty_region`, `intra_refresh_picture_partition_midway`, `intra_refresh_any_block_based_midway`, `intra_refresh_row_based_midway`, `intra_refresh_column_based_midway`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `i` | Basic codec profile, session, I-picture setup, source-image access, or bitstream production. |
| `rc_vbr` | VBR capability, rate-control state, or encoded quality. |
| `rc_cbr` | CBR capability, rate-control state, or encoded quality. |
| `rc_disable` | Disabled-rate-control constant-QP path or encoded quality. |
| `quality_level` | Quality-level state or its effect on encoded quality. |
| `quantization_map_delta_rc_vbr` | Delta-map resource/session setup combined with VBR encoding. |
| `quantization_map_delta_rc_cbr` | Delta-map resource/session setup combined with CBR encoding. |
| `quantization_map_delta_rc_disable` | Delta-map resource/session setup combined with constant-QP encoding. |
| `quantization_map_delta` | Delta-map resource/session setup or delta-map effect on PSNR distribution. |
| `quantization_map_emphasis_cbr` | Emphasis-map resource/session setup combined with CBR encoding. |
| `quantization_map_emphasis_vbr` | Emphasis-map resource/session setup combined with VBR encoding. |
| `usage` | Non-default encode usage state or its effect on encoded quality. |
| `i_p` | P-picture reference-slot setup, forward prediction, or frame ordering. |
| `i_p_not_matching_order` | Command submission order, synchronization, or deferred bitstream-offset handling. |
| `i_p_b_13` | H.264/H.265 P/B reference lists, DPB slot lifetime, frame numbering, or reordered pictures. |
| `resolution_change_dpb` | Second session-parameter set, half-resolution picture resources, or resolution transition handling. |
| `query_with_status` | Encode feedback query status, query-result support, or completion handling. |
| `inline_query` | Inline-query session creation, query association, or inline feedback handling. |
| `resources_without_profiles` | Video-profile-independent source/DPB resource compatibility. |
| `intra_refresh_picture_partition` | Per-picture-partition intra-refresh indices, slice count, or DPB updates. |
| `intra_refresh_any_block_based` | Block-based intra-refresh mode or refreshed-region handling. |
| `intra_refresh_row_based` | Block-row intra-refresh mode or row-region handling. |
| `intra_refresh_column_based` | Block-column intra-refresh mode or column-region handling. |
| `intra_refresh_any_block_based_empty_region` | Empty-region block-based intra-refresh control or cycle-duration handling. |
| `intra_refresh_row_based_empty_region` | Empty-region row-based intra-refresh control or cycle-duration handling. |
| `intra_refresh_column_based_empty_region` | Empty-region column-based intra-refresh control or cycle-duration handling. |
| `intra_refresh_picture_partition_midway` | Starting a new per-picture-partition refresh cycle mid-way through the sequence. |
| `intra_refresh_any_block_based_midway` | Starting a new block-based refresh cycle mid-way through the sequence. |
| `intra_refresh_row_based_midway` | Starting a new row-based refresh cycle mid-way through the sequence. |
| `intra_refresh_column_based_midway` | Starting a new column-based refresh cycle mid-way through the sequence. |

The same leaf names are registered under both codecs. The codec selects the H.264 or H.265 profile-specific parameter structures, picture syntax, and capability fields; it does not change the host-side PSNR contract.

## Important Variations and Special Cases

- Each registered leaf is instantiated for four layout/resource combinations: `_layered_src_general_layout`, `_layered_src_video_layout`, `_separated_src_general_layout`, and `_separated_src_video_layout` ([`createVideoEncodeTests`](../../../modules/vulkan/video/vktVideoEncodeTests.cpp#L3986-L4007)).
- The standard H.264 clip is `yuv/176x144_30_i420.yuv` at 176 by 144 and 24 frames per second. The standard H.265 clip is `yuv/720x480_420_8le.yuv` at 720 by 480 and 24 frames per second. Resolution-change leaves use H.264 clip `yuv/352x288_15_i420.yuv` at 352 by 288 and H.265 clip `yuv/1920x1080_420_8le.yuv` at 1920 by 1080, both at 15 frames per second ([`Clips`](../../../modules/vulkan/video/vktVideoClipInfo.cpp#L508-L587)).
- The basic I case encodes one IDR frame. `rc_disable` and I/P cases encode an IDR followed by a P frame. `i_p_b_13` uses two GOPs of the 14-picture IDR/P/B pattern. Quantization-map cases use two or three one-frame GOP iterations as specified by the test definition. The intra-refresh macros define a 16-frame pattern for ordinary, empty-region cases and a seven-frame pattern for midway cases ([`g_EncodeTests`](../../../modules/vulkan/video/vktVideoEncodeTests.cpp#L432-L1088)).
- For `resolution_change_dpb`, the second GOP uses half the original coded width and height, and the test creates a second session-parameter object with the same half-size dimensions ([`currentCodedExtent`](../../../modules/vulkan/video/vktVideoEncodeTests.cpp#L2665-L2688), [`setupSessionParameters`](../../../modules/vulkan/video/vktVideoEncodeTests.cpp#L2506-L2518)).
- Intra-refresh cases clamp the cycle and frame count to queried capabilities. Per-picture partition mode is limited by codec slice or slice-segment capacity and coding-block geometry; row, column, and block modes use their corresponding block dimensions. Empty-region cases use the maximum cycle duration, while midway cases use cycle duration 4 over frames 1 through 6 ([`queryIntraRefreshCapabilities`](../../../modules/vulkan/video/vktVideoEncodeTests.cpp#L3535-L3708)).
- If a clip contains fewer frames than the requested matrix, `loadVideoFrames` limits processing to the available complete frames. For intra refresh it also clamps `m_gopFrameCount` before loading and encoding ([`loadVideoFrames`](../../../modules/vulkan/video/vktVideoEncodeTests.cpp#L2730-L2797)).

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Registration and four layout variants | [`createVideoEncodeTests`](../../../modules/vulkan/video/vktVideoEncodeTests.cpp#L3979-L4015) | Creates `video.encode.h264` and `video.encode.h265` and appends layout suffixes. |
| Registered leaf names and definitions | [`getTestName` and `g_EncodeTests`](../../../modules/vulkan/video/vktVideoEncodeTests.cpp#L172-L265) ([`g_EncodeTests`](../../../modules/vulkan/video/vktVideoEncodeTests.cpp#L432-L1088)) | Defines exact leaf identifiers, clips, patterns, GOP counts, references, and options. |
| Clip dimensions and profiles | [`Clips`](../../../modules/vulkan/video/vktVideoClipInfo.cpp#L508-L587) | Supplies filenames, H.264/H.265 encode profiles, dimensions, frame rates, and optional frame counts. |
| Setup and capability pruning | [`initializeTestParameters`](../../../modules/vulkan/video/vktVideoEncodeTests.cpp#L1997-L2080) and [`queryAndValidateCapabilities`](../../../modules/vulkan/video/vktVideoEncodeTests.cpp#L2114-L2238) | Selects options and rejects unsupported features, formats, references, rates, DPB sizes, and quality levels. |
| Resource and extent setup | [`prepareDPBResources`](../../../modules/vulkan/video/vktVideoEncodeTests.cpp#L2572-L2663), [`prepareInputImages`](../../../modules/vulkan/video/vktVideoEncodeTests.cpp#L2691-L2728) | Creates DPB/source images and maps picture resources to slots and layers. |
| Host/device encode flow | [`iterate`](../../../modules/vulkan/video/vktVideoEncodeTests.cpp#L3819-L3838) and [`encodeFrame`](../../../modules/vulkan/video/vktVideoEncodeTests.cpp#L2981-L3332) | Shows ordered setup, command recording, submission, feedback, and encode operation construction. |
| Output verification | [`verifyEncodedBitstream`](../../../modules/vulkan/video/vktVideoEncodeTests.cpp#L3358-L3505) | Decodes the bitstream and applies frame-count, PSNR, and quantization-map checks. |
| Codec-independent encode semantics | [Video Encode Operations](../../../../vulkan-docs/src/chapters/video/encode.adoc#L8-L93) | Defines input/reference reads, bitstream writes, layouts, and unsuccessful-encode consequences. |
| H.264 codec semantics and limits | [H.264 Encode Operations](../../../../vulkan-docs/src/chapters/video/h264_encode.adoc#L4-L60) and [H.264 capabilities](../../../../vulkan-docs/src/chapters/video/h264_encode.adoc#L296-L375) | Grounds H.264 picture types, macroblocks, syntax, and capability checks. |
| H.265 codec semantics and limits | [H.265 Encode Operations](../../../../vulkan-docs/src/chapters/video/h265_encode.adoc#L4-L63) and [H.265 capabilities](../../../../vulkan-docs/src/chapters/video/h265_encode.adoc#L330-L425) | Grounds H.265 picture types, coding blocks, syntax, and capability checks. |

## Questions / Risk Points for User Audit

- Is the registered test case leaf, with codec as a parallel axis, the right primary behavior parameter for this combined page?
- Is the distinction between layered versus separated source images and general versus video image layouts clear?
- Does the explanation distinguish the host-visible encoded bitstream buffer from DPB and source images?
- Are PSNR warnings, hard failures, and quantization-map exceptions described without implying bitstream byte equality?
- Should the page call out the source comment that Android excludes the external decode validation path, or is the generic source-backed description enough?
- The source has a FIXME that intra-refresh GOP size is limited because of current DPB slot management. Should this implementation limitation be emphasized in the final page?

## Conversion Notes for Final Wiki Page

- Keep the combined registration tree at `video.encode` with direct children `h264` and `h265`; put the 31 shared leaf names and four suffix combinations in parameter tables and prose rather than expanding the hierarchy tree.
- Distill Background Knowledge to the encode input/reference/DPB model and the codec coding-block distinction. Keep setup and validation out of that section.
- Preserve the four source/resource layout variants, four clip dimension cases, GOP patterns, capability gates, and intra-refresh clamping in the body sections.
- Carry the behavior-axis conclusion into `## Behavior Parameters`. Copy the `### Failure Cause Mapping` table above directly into the final page. Write `### Cause Analysis` fresh.
- The page has no shader. `vktVideoEncodeTests.cpp` uses Vulkan video commands and Video Std structures rather than shader code. The required `video` exception entry is not in the allowed write set for this assignment; report it if the structure validator requires the exact filename to be added.
