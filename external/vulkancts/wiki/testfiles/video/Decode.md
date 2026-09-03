## Overview

**Core question:** Does each Vulkan video decode case produce the expected pictures while exercising the requested codec, DPB arrangement, layout, ordering, and session behavior?

- This page covers `external/vulkancts/modules/vulkan/video/vktVideoDecodeTests.cpp`, which registers decode cases under the `video.decode` test family for H.264, H.265, AV1, and VP9.
- Each ordinary definition expands to four registered cases: `_layered_dpb` or `_separated_dpb`, crossed with `_general_layout` or `_video_layout`.
- Cases load a compressed clip, decode a selected number of displayed frames, copy the YCbCr planes to host-visible buffers, and compare an MD5 digest with the clip's stored frame checksum.
- The page explains the codec and clip matrix, status and session options, cached ordering, interleaving, DPB resource choices, layout requirements, support gates, frame checking, pruning, and failure interpretation.

## Background Knowledge

- Vulkan separates DPB slot state, which belongs to a video session, from the image subregions that back those slots. A decode operation can write a decode output picture and an optional reconstructed picture used as a future reference. See [DPB state and backing store](../../../../vulkan-docs/src/chapters/videocoding.adoc#dpb-state-and-backing-store).
- Decode output-only resources use `VK_IMAGE_LAYOUT_VIDEO_DECODE_DST_KHR`; reconstructed and reference resources use `VK_IMAGE_LAYOUT_VIDEO_DECODE_DPB_KHR`. `VK_IMAGE_LAYOUT_GENERAL` is also valid when `unifiedImageLayoutsVideo` is enabled. See [decode image layouts](../../../../vulkan-docs/src/chapters/video/decode.adoc#video-decode-operations).
- Coding order and display order can differ when inter-frame references are involved. The Vulkan operation consumes the active reference list and writes the output according to codec-specific semantics, while this CTS dequeues pictures in display order for checking. See [decode operation steps](../../../../vulkan-docs/src/chapters/video/decode.adoc#decode-operation-steps).

## Registration Hierarchy

```text
video.decode
├── h264
├── h265
├── av1
└── vp9
```

The four codec groups share the same DPB and layout suffixes. Their leaves differ in bitstream syntax, reference rules, and feature-focused clips.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Codec group | `h264`, `h265`, `av1`, `vp9` | Selects the codec-specific Vulkan decode operation and profile. | [`createVideoDecodeTests`](../../../modules/vulkan/video/vktVideoDecodeTests.cpp#L1976-L2031) |
| Test case leaf | `i`, `i_p`, `i_p_b_13`, `basic_8`, `tile_1x4`, and other exact leaves used by the matrix | Selects the stream or API behavior under test. | [`testTypeToStr`](../../../modules/vulkan/video/vktVideoDecodeTests.cpp#L253-L456) |
| DPB organization | `layered_dpb`, `separated_dpb` | Uses an image array with a layer per decode surface, or separate reference images. | [`TestDefinition::getTestName`](../../../modules/vulkan/video/vktVideoDecodeTests.cpp#L771-L785), [`StartVideoSequence`](../../../modules/vulkan/video/vktVideoBaseDecodeUtils.cpp#L591-L624) |
| Image layout | `general_layout`, `video_layout` | Uses `VK_IMAGE_LAYOUT_GENERAL`, or the dedicated decode destination and DPB layouts. | [`TestDefinition::getTestName`](../../../modules/vulkan/video/vktVideoDecodeTests.cpp#L771-L785), [`DecodePictureWithParameters`](../../../modules/vulkan/video/vktVideoBaseDecodeUtils.cpp#L1801-L1804) |
| Frame selection | `ALL_FRAMES` or an explicit count | `ALL_FRAMES` becomes the clip's `totalFrames`; explicit counts test a prefix. | [`g_DecodeTests`](../../../modules/vulkan/video/vktVideoDecodeTests.cpp#L591-L688), [`TestDefinition` constructor](../../../modules/vulkan/video/vktVideoDecodeTests.cpp#L714-L736) |
| Decoder option | `Default`, status, cached, profile-less resources, film grain, intra-only, Annex B, and maintenance2 options | Changes query, ordering, resource, framing, or session-parameter behavior. | [`DecoderOption`](../../../modules/vulkan/video/vktVideoDecodeTests.cpp#L550-L575) |

The default mustpass contains 292 decode paths: 60 H.264 paths, 56 H.265 paths, 96 AV1 paths, and 80 VP9 paths. Each path has the `dEQP-VK.video.decode.<codec>.<leaf>_<dpb>_<layout>` form. See [the decode entries](../../../mustpass/main/vk-default/video.txt#L26-L317).

## Behavior Parameters

The primary behavioral axis is the registered test case leaf. It selects the codec syntax or API behavior being exercised. The DPB and layout suffixes are orthogonal resource realizations applied by the factory to the same leaf.

### H.264 test case leaves: H.264 decode behavior

H.264 cases cover I and I/P prefixes, the 30-frame `clip-a` playback case, a 26-frame 4K I/P/B stream, matching-order and cached recording order, status queries, resolution changes, profile-less resources, and maintenance2 session-parameter behavior. The `i_p_b_13` cases use `avc/4k_26_ibp_main.h264`; the `resolution_change` cases use `avc/clip-c.h264`. H.264 uses High profile for `clip-a` and Main profile for the 4K clip. See [`g_DecodeTests`](../../../modules/vulkan/video/vktVideoDecodeTests.cpp#L592-L608).

### H.265 test case leaves: H.265 decode behavior

H.265 cases cover I, I/P, I/P/B, the 30-frame `clip-d` playback case, two 65-frame ITU scaling-list streams, a long-term-reference stream, cached recording order, status queries, profile-less resources, and maintenance2 session-parameter behavior. H.265 uses the Main profile. See [`g_DecodeTests`](../../../modules/vulkan/video/vktVideoDecodeTests.cpp#L610-L627).

### AV1 test case leaves: AV1 decode behavior

AV1 cases cover I and I/P prefixes, basic 8-bit and 10-bit streams, cached order, all-intra and intra-block-copy streams, CDF updates, global motion, film grain, SVC, super-resolution, size changes, order hints, forward key frames, lossless mode, loop filtering, CDEF, golden-frame references, and maintenance2 session-parameter behavior. The active Argon film-grain case checks one frame with film grain disabled because later parser assertions remain unresolved. See [`g_DecodeTests`](../../../modules/vulkan/video/vktVideoDecodeTests.cpp#L629-L665).

### VP9 test case leaves: VP9 decode behavior

VP9 cases cover keyframe and basic streams, cached order, show-existing-frames, a 351x287 frame size, tile layouts, resize, loop filtering, 10-bit content, intra-only content, segmentation, three quantizer values, resize by 1/2, and SVC. VP9 cases use profile 0 for every case except `10bits_10`, which uses profile 2 for 10-bit content. See [`ClipInfo` entries](../../../modules/vulkan/video/vktVideoClipInfo.cpp#L867-L997).

### `interleaved` and `h265_interleaved`: alternating decode sessions

The interleaving leaves exercise two cached streams on the same decode queue. `interleaved` uses two H.264 `clip-a` streams. `h265_interleaved` pairs an H.264 `clip-a` stream with an H.265 `clip-d` stream. The host records one command from each stream at each cached index, submits the two streams alternately, then checks each stream separately. See [`g_InterleavingTests`](../../../modules/vulkan/video/vktVideoDecodeTests.cpp#L691-L703) and [`InterleavingDecodeTestInstance::iterate`](../../../modules/vulkan/video/vktVideoDecodeTests.cpp#L1563-L1705).

## Shader Analysis

This page has no shader walkthrough. Video decode runs in the fixed-function `VK_PIPELINE_STAGE_2_VIDEO_DECODE_BIT_KHR` stage through `vkCmdDecodeVideoKHR`; the page's observable output comes from decoded image planes copied and checked on the host. The Vulkan operation reads the source bitstream and active reference pictures, then writes the decode output and optional reconstructed picture. See [video decode operations](../../../../vulkan-docs/src/chapters/video/decode.adoc#video-decode-operations).

## Runtime Execution and Result Checking

- `TestDefinition` obtains `ClipInfo`, constructs a `VkVideoCoreProfile` for each session profile, and replaces `ALL_FRAMES` with `ClipInfo::totalFrames`. The demuxer reads the clip using H.26X byte-stream, IVF, or AV1 Annex B framing.
- The decoder queries decode capabilities and supported formats, validates coded and image extents against implementation limits, creates a video session, and initializes `MAX_NUM_DECODE_SURFACES` decode surfaces. Layered DPB cases use an image array and image-view array. Separated cases require `VK_VIDEO_CAPABILITY_SEPARATE_REFERENCE_IMAGES_BIT_KHR`.
- The parser supplies sequence and picture information. The decoder caches the aligned bitstream range, codec-specific picture data, session parameter object, active reference slots, setup slot, image barriers, and frame synchronization objects. A sequence change can reuse a compatible session; `RecreateDPBImages` forces session and DPB recreation.
- For normal playback, the decoder waits for a reusable frame fence, applies picture parameters, records `vkCmdBeginVideoCodingKHR`, reset and pipeline-barrier commands as needed, `vkCmdDecodeVideoKHR`, and `vkCmdEndVideoCodingKHR`, then submits one command buffer to the decode queue.
- `CachedDecoding` gathers the requested frames first, records command buffers in a deterministic swapped or shuffled order, and submits them in the original order. The cache supports at most 32 frames, and inter-frame dependencies can cause more decoded frames to be buffered than the requested count.
- Status cases read `VkQueryResultStatusKHR` after frame completion. Inline status cases attach `VkVideoInlineQueryInfoKHR` to the decode command. Maintenance2 inline-session cases attach codec session parameters to the decode operation; relaxed-session cases issue a reset with no session parameters, end coding, and restart with valid parameters.
- The host waits for frame completion, copies each plane from the decode queue to host-visible buffers through the transfer queue, and returns the image to its decode queue and original layout. Two-plane chroma is deinterleaved. 10-bit and 12-bit words are normalized before hashing.
- The host compares `DownloadedFrame::checksum()` with `checksumForClipFrame()` for each requested displayed frame. A normal case passes only when every requested frame matches. Interleaving requires all streams to pass and checks that the number of classified frames equals the number buffered.
- AV1 film grain gets a second decode with film grain disabled. A checksum mismatch remains acceptable when the computed `psnr` value is between 28.0 and 34.0 dB; in the current source, the accumulator adds only the Cb and Cr PSNR values and divides their sum by three because the luma PSNR return value is discarded.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| Basic I/P or full-clip decode leaves | Codec parser or codec-specific decode state, reference-slot mapping, session profile, or decoded-image resource handling produced samples whose MD5 differs from the clip reference. |
| `*_not_matching_order` | The decoder or frame-buffer bookkeeping depends incorrectly on command-buffer recording order, or cached bitstream and reference data do not survive until in-order submission. |
| `interleaved` or `h265_interleaved` | One of the sessions mishandles alternating command recording/submission, shared queue synchronization, or per-session DPB and parameter state. |
| `query_with_status` or `inline_query_with_status` | The implementation reports an error status, or the CTS uses the query pool, availability, query count, or inline-query path incorrectly for the supported feature. |
| `resolution_change` or `resolution_change_dpb` | Sequence reconfiguration, session compatibility, DPB image recreation, or coded/display extent handling is wrong. |
| `resources_without_profiles` | Profile-less resource creation or the maintenance1 resource path is unsupported or incorrectly associated with the active video profile. |
| `inline_session_params` or `relaxed_session_params` | The maintenance2 inline parameter path or reset-without-session-parameters behavior is not accepted, or codec parameter data is not restored for subsequent decoding. |
| Codec-specific feature leaves | The named codec syntax or semantic feature, its reference picture list, or the associated profile-specific decode structures produced the wrong picture. |
| Any leaf with `_layered_dpb` | Array-layer selection, DPB slot to layer mapping, or image-view-array use is wrong. |
| Any leaf with `_separated_dpb` | Separate reference-image support, per-image ownership, or DPB reference-resource binding is wrong. |
| Any leaf with `_general_layout` | `unifiedImageLayoutsVideo`, `VK_IMAGE_LAYOUT_GENERAL` transitions, or access synchronization for video images is wrong. |
| Any leaf with `_video_layout` | The resource transitions or access scopes for `VK_IMAGE_LAYOUT_VIDEO_DECODE_DST_KHR` and `VK_IMAGE_LAYOUT_VIDEO_DECODE_DPB_KHR` are wrong. |

A checksum mismatch means that the displayed decoded samples differ from the stored reference representation. It does not identify the failing layer by itself. The first failing leaf, suffix, and frame index narrow the investigation.

### Cause Analysis

#### Codec reconstruction, reference state, or host comparison

**Possible failure symptoms:** A requested frame reaches the display queue, but its MD5 digest differs from the checksum stored for that clip frame. The case reports the count and indices of incorrect frames.

**Possible implementation causes:** The codec-specific parser data, active reference list, DPB slot mapping, profile parameters, decode output resource, or image-to-buffer conversion can change the samples that the host hashes. The Vulkan specification defines the bitstream interpretation, reference-picture list, output generation, and optional reconstructed picture as codec-specific decode behavior, so source-level comparison against the relevant H.264, H.265, AV1, or VP9 path is needed to isolate the defect. See [codec-specific semantics](../../../../vulkan-docs/src/chapters/video/decode.adoc#decode-codec-specific-semantics).

#### Cached ordering and interleaving

**Possible failure symptoms:** A cached or interleaved case reports specific incorrect frame indices, while ordinary in-order playback may pass. An internal error can also occur if a requested decoded frame never reaches the display queue.

**Possible implementation causes:** Cached cases record command buffers in a swapped or shuffled order and submit them in coding order. Interleaved cases do this for two streams on one decode queue. A mismatch can therefore come from lifetime handling of cached bitstream or parameter data, frame-buffer bookkeeping, DPB state, or queue synchronization. The source intentionally checks the total interleaved result count and reports the failing stream, but it cannot identify which internal mechanism failed.

#### DPB organization and image layouts

**Possible failure symptoms:** The same leaf fails only with `_layered_dpb`, `_separated_dpb`, `_general_layout`, or `_video_layout`. The failure may appear as a checksum mismatch or as a resource or synchronization error during decode or copyback.

**Possible implementation causes:** Layered cases select a DPB image-array layer from the picture index; separated cases bind each DPB slot to a separate reference image. The decode specification requires DPB and output resources to use roles and layouts compatible with how each resource participates in the operation. A failure points to the image-array or separate-image binding, subresource range, layout transition, queue-family ownership transfer, or `unifiedImageLayoutsVideo` support for the selected suffix. See [decode picture resource rules](../../../../vulkan-docs/src/chapters/video/decode.adoc#decode-output-picture-info).

#### Status and session-parameter controls

**Possible failure symptoms:** A status case rejects `VK_QUERY_RESULT_STATUS_ERROR_KHR`, reports an invalid query result, or fails while using inline queries. A maintenance2 case fails during a reset or when decoding resumes after a reset.

**Possible implementation causes:** The implementation may not support the requested query or maintenance extension, may expose a queue or query configuration that does not match the session, or may mishandle status production and session-parameter sourcing. The CTS support gate is supposed to remove unsupported cases before execution; an executed case that fails still needs source and validation-layer investigation.

#### Sequence changes and film grain

**Possible failure symptoms:** A resolution-change case fails when coded or display dimensions change, or an AV1 film-grain case raises a quality warning after the exact checksum differs and the average PSNR falls outside 28.0 to 34.0 dB.

**Possible implementation causes:** Resolution changes exercise sequence detection, extent validation, session compatibility, DPB image recreation, and codec reset state. Film grain requires a distinct displayed output when the reconstructed reference is kept without post-processing. A failure can arise in those resource or reset transitions, in codec film-grain processing, or in host-side plane comparison. The source comments leave two other Argon cases out of the active matrix because available implementations did not explain their failures; those cases do not establish a general cause for this active test.

## Case Pruning

### Requirement-based pruning

- `VideoDecodeTestCase::checkSupport` requires `VK_KHR_synchronization2`, the codec's decode extension, the matching standard codec extension and version, and the maintenance extension for maintenance1 or maintenance2 cases.
- VP9 cases require `VK_KHR_video_decode_vp9`. Inline status and profile-less resource cases require `VK_KHR_video_maintenance1`. Inline and relaxed session-parameter cases require `VK_KHR_video_maintenance2`.
- General-layout cases require `VK_KHR_unified_image_layouts` and the `unifiedImageLayoutsVideo` feature. The decoder also rejects profiles without supported decode formats, extents outside reported limits, and separated-DPB cases when `VK_VIDEO_CAPABILITY_SEPARATE_REFERENCE_IMAGES_BIT_KHR` is absent.
- The source supports only 8-, 10-, 12-, and 16-bit decoded component descriptions in its conversion assertions, then explicitly rejects untested 16-bit samples. Unsupported profiles or format queries produce `NotSupportedError`, while a disabled video build returns `NotSupportedError` before decode.

These checks remove cases that the current device or build cannot legally exercise. They do not count as decoded-frame failures.

### Design-based pruning

- The factory applies exactly two DPB arrangements and two layout choices to every active definition instead of adding separate test leaves for each cross-product value.
- `ALL_FRAMES` uses the clip metadata's total frame count. Explicit prefixes keep short I/P and feature cases focused, while long clips retain enough frames to exercise their reference behavior.
- `CachedDecoding` is limited to 32 cached frames, which the source considers sufficient for out-of-order command recording. The interleaving cases use two streams and equal cached counts so their command buffers can be interleaved by index.
- `argon_seqchange_affine_8` and `argon_test787` remain commented out because the source lacks enough implementations to explain their failures. The active Argon film-grain case checks one frame because later frames assert in the parser.

These exclusions define the intended matrix and unresolved coverage boundary. They do not indicate unsupported Vulkan capabilities.

## Key Takeaways

- The registered leaf carries the primary behavior choice. DPB organization and image layout change how the same behavior reaches Vulkan, not which codec feature the leaf names.
- The test compares displayed YCbCr samples, not compressed bytes or an implementation-specific internal surface. Host-side deinterleaving and bit-depth normalization are part of the comparison contract.
- Cached cases prove that command-buffer recording order can differ from submission order. Interleaved cases extend that check to two decode streams sharing a queue.
- Layered and separated DPB cases exercise two valid ways to bind reference resources. General-layout cases additionally test the `unifiedImageLayoutsVideo` feature and its synchronization requirements.
- A skipped case means a support or build gate removed it. A failed case means an executed frame, query, resource transition, or internal invariant did not meet the CTS contract. See [Failure Meaning](#failure-meaning).

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Decode registration and matrix | [`createVideoDecodeTests`](../../../modules/vulkan/video/vktVideoDecodeTests.cpp#L1976-L2033) | Creates codec groups, four DPB/layout variants, ordinary cases, and interleaving cases. |
| Case parameter table | [`g_DecodeTests`](../../../modules/vulkan/video/vktVideoDecodeTests.cpp#L591-L688) | Defines exact leaves, clips, frame counts, and decoder options. |
| Interleaving parameter table | [`g_InterleavingTests`](../../../modules/vulkan/video/vktVideoDecodeTests.cpp#L691-L703) | Defines the two two-stream cases. |
| Test naming and support flags | [`TestDefinition::getTestName`](../../../modules/vulkan/video/vktVideoDecodeTests.cpp#L771-L833) | Defines suffixes and device feature flags. |
| Support checks | [`VideoDecodeTestCase::checkSupport`](../../../modules/vulkan/video/vktVideoDecodeTests.cpp#L1749-L1933) | Enforces codec, synchronization, maintenance, standard-version, and general-layout gates. |
| Clip metadata | [`ClipInfo`](../../../modules/vulkan/video/vktVideoClipInfo.hpp#L121-L136) and [`Clips`](../../../modules/vulkan/video/vktVideoClipInfo.cpp#L515-L1082) | Maps clips to filenames, profiles, framing, dimensions, frame totals, and checksums. |
| Session and image setup | [`StartVideoSequence`](../../../modules/vulkan/video/vktVideoBaseDecodeUtils.cpp#L493-L633) | Queries capabilities, validates extents, creates sessions, and selects layered or separated resources. |
| Decode resource binding | [`DecodePictureWithParameters`](../../../modules/vulkan/video/vktVideoBaseDecodeUtils.cpp#L1714-L1985) | Assigns layouts, array layers, reference slots, output resources, and barriers. |
| Command recording and status | [`RecordCommandBuffer`](../../../modules/vulkan/video/vktVideoBaseDecodeUtils.cpp#L2085-L2192) and [`QueryDecodeResults`](../../../modules/vulkan/video/vktVideoBaseDecodeUtils.cpp#L2229-L2252) | Records reset, query, inline-parameter, decode, and status operations. |
| Cached command order | [`decodeFramesOutOfOrder`](../../../modules/vulkan/video/vktVideoBaseDecodeUtils.cpp#L2254-L2300) | Records shuffled commands and submits them in original order. |
| Host copy and hash | [`getDecodedImage`](../../../modules/vulkan/video/vktVideoDecodeTests.cpp#L919-L1298) | Transfers planes, normalizes samples, and returns downloaded data for MD5. |
| Ordinary result checking | [`VideoDecodeTestInstance::iterate`](../../../modules/vulkan/video/vktVideoDecodeTests.cpp#L1381-L1557) | Applies checksums, film-grain PSNR, and pass/fail messages. |
| Interleaved result checking | [`InterleavingDecodeTestInstance::iterate`](../../../modules/vulkan/video/vktVideoDecodeTests.cpp#L1563-L1705) | Records, submits, and checks two streams. |
| Vulkan decode operation rules | [`Video Decode Operations`](../../../../vulkan-docs/src/chapters/video/decode.adoc#video-decode-operations) | Defines resource roles, layouts, decode steps, and unsuccessful output contents. |
| Codec decode chapters | [`H.264`](../../../../vulkan-docs/src/chapters/video/h264_decode.adoc#decode-h264), [`H.265`](../../../../vulkan-docs/src/chapters/video/h265_decode.adoc#decode-h265), [`AV1`](../../../../vulkan-docs/src/chapters/video/av1_decode.adoc#decode-av1), and [`VP9`](../../../../vulkan-docs/src/chapters/video/vp9_decode.adoc#decode-vp9) | Defines codec-specific bitstream and reference semantics. |
| DPB and sessions | [`DPB state`](../../../../vulkan-docs/src/chapters/videocoding.adoc#dpb-state-and-backing-store) and [`Video Sessions`](../../../../vulkan-docs/src/chapters/videocoding.adoc#video-session) | Explains session-owned DPB state and image-backed slots. |
| Mustpass decode paths | [`video.txt`](../../../mustpass/main/vk-default/video.txt#L26-L317) | Confirms exact active decode registrations and suffixes. |
