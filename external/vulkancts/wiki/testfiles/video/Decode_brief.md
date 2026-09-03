# Understanding Brief: `vktVideoDecodeTests.cpp`

## One-Sentence Test Purpose

This test checks whether Vulkan video decode sessions for H.264, H.265, AV1, and VP9 reconstruct the registered bitstreams correctly while the implementation handles DPB ownership, output layouts, ordering, session options, and decode status reporting.

## Background Knowledge

### Decode output, reconstructed pictures, and the DPB

A Vulkan decode operation consumes compressed bitstream data and reference pictures, then writes a decode output picture. It may also write a reconstructed picture that becomes a reference. The decoded picture buffer (DPB) keeps indexed references available to later operations; the video session owns DPB slot state, while images provide the backing storage. Vulkan defines separate layouts for output-only images (`VK_IMAGE_LAYOUT_VIDEO_DECODE_DST_KHR`) and images used as reconstructed or reference pictures (`VK_IMAGE_LAYOUT_VIDEO_DECODE_DPB_KHR`). With `unifiedImageLayoutsVideo`, `VK_IMAGE_LAYOUT_GENERAL` can serve these video accesses.

Why it matters here:
- The test deliberately runs each case with a layered or separated DPB arrangement.
- It also runs each arrangement with the codec-specific video layouts and with `VK_IMAGE_LAYOUT_GENERAL`.
- The Vulkan decode specification allows DPB and output resources to coincide or remain distinct, so the test must preserve the correct resource role while copying decoded samples back.

### Decode order and display order

A compressed stream can require frames to decode in coding order while the application displays them in display order. Inter-frame dependencies make this distinction visible in `i_p`, B-frame, and cached out-of-order cases. The test records decoded frames with the parser's picture information, submits them in coding order, and dequeues displayed frames for comparison.

Why it matters here:
- `CachedDecoding` changes command-buffer recording order but keeps queue submissions in coding order.
- The expected checksum index follows the displayed frame sequence consumed by the test.
- Interleaving tests repeat the same recording and submission pattern across two decode sessions on one decode queue.

## One Concrete Example

Consider `h264.i_p_b_13_layered_dpb_video_layout`. The source selects the 26-frame, 3840x2160 H.264 stream `avc/4k_26_ibp_main.h264`, asks the parser and decoder to process all 26 frames, uses one layered image array for DPB storage, and uses `VK_IMAGE_LAYOUT_VIDEO_DECODE_DPB_KHR` for DPB references. The parser supplies each picture's bitstream range, current picture, codec-specific reference slots, and setup slot. The decoder records `vkCmdBeginVideoCodingKHR`, a pipeline barrier for the bitstream and image resources, `vkCmdDecodeVideoKHR`, and `vkCmdEndVideoCodingKHR`. The queue submits in coding order. The test dequeues each displayed picture, copies its Y, Cb, and Cr samples to host-visible plane buffers, computes an MD5 digest, and compares it with the checksum for the same display-frame index.

`h264.i_p_b_13_not_matching_order` uses the same clip but enables `CachedDecoding`: it gathers enough parser output first, records command buffers in a deterministic shuffled order, then submits the cached commands in their original order. A correct implementation therefore must tolerate command-buffer recording order that differs from coding order without changing the decoded pictures.

## End-to-End Test Flow

```text
[host] select a registered codec case, clip, frame count, decoder options, DPB mode, and image layout
[host] load the clip through the matching demuxer framing: H.26X byte stream, IVF, or AV1 Annex B
[host] query the selected profile's decode capabilities and supported output and DPB formats
[host] create a video session and a pool of decode images, using array layers for layered DPB or separate images for separated DPB
[host] parse sequence and picture data, cache codec parameters and bitstream ranges, and allocate DPB slots
[host] record one decode command per picture, optionally with status queries or inline session parameters
[host] submit commands in coding order, waiting on frame fences and status queries when the selected option requires it
[device] read the compressed range and active reference pictures in the video decode stage
[device] reconstruct the picture and write the decode output and, when requested, the reconstructed DPB picture
[host] dequeue displayed frames, wait for completion, and release each frame after copying its planes
[host] copy every plane through decode and transfer queues, deinterleave two-plane chroma when needed, normalize 10/12-bit samples, and calculate MD5
[host] compare each actual digest with the clip's reference digest, applying the AV1 film-grain PSNR rule when that option is enabled
[host] pass only when every requested frame matches, or return a failure with the incorrect frame indices
```

For interleaving, the flow has two streams. The host buffers each stream first, records one command for each stream at each cached index, submits the streams in alternating order, then checks each stream's displayed frames against its own checksum array.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- The registered case produces a `TestDefinition` from a `BaseDecodeParam`, then appends `_layered_dpb` or `_separated_dpb` and `_general_layout` or `_video_layout` to the case name.
- The demuxer reads the clip file and passes codec operation and framing to the parser. H.264 and H.265 use byte-stream framing, AV1 cases use IVF except the two OBU cases, and the Argon film-grain case uses AV1 Annex B.
- The decoder caches per-picture bitstream offsets, slice information, codec-specific picture structures, session parameter objects, reference slots, and synchronization objects. The cached set holds at most 32 frames for out-of-order recording.
- Clip metadata supplies codec profile, chroma and bit depth, coded dimensions, total frame count, DPB/GOP information, framing, and a pointer to per-frame MD5 strings.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Bitstream buffer | yes | yes | decode reads | no | Carries the aligned compressed range for each picture. |
| DPB images | yes | yes | decode reads references and writes reconstructed pictures | sometimes, when DPB and output coincide | Back the session's DPB slots. A layered DPB uses array layers; a separated DPB uses separate image resources. |
| Decode output image | yes | yes | decode writes output | yes | Holds the displayed decoded picture, either distinct from or coincident with the DPB resource. |
| Video session | yes | yes, as the coding scope state | maintains decode and DPB slot state | no | Couples the profile, session dimensions, DPB capacity, and session options. |
| Video session parameters | yes or inline | yes, unless the relaxed option intentionally omits them for a reset | decode reads codec parameter sets | no | Supplies H.264/H.265 SPS/PPS, AV1 sequence headers, or the valid session-parameter path after a reset. VP9 does not bind a session parameter object here. |
| Query pool | yes when status is selected | yes | decode writes status | yes | Provides `VkQueryResultStatusKHR` after a fence wait, or receives inline status queries. |
| Host-visible plane buffers | yes | transfer destination | transfer writes | yes | Receive each image plane before MD5 computation. |
| Semaphores and fences | yes | queue synchronization | device signals and waits | host waits on fences | Order decode-to-transfer ownership changes and frame completion. |

## What Is Checked

- `DownloadedFrame::checksum()` feeds the downloaded luma, Cb, and Cr byte arrays to MD5 in that order. The expected string comes from `checksumForClipFrame(clipInfo, frameNumber)`.
- For two-plane formats, the host deinterleaves chroma words into Cb and Cr arrays. For 10-bit and 12-bit samples, it rotates the stored words so the checksum representation matches the reference data. The implementation rejects untested 16-bit samples.
- The ordinary decode path records a frame as correct only when its actual checksum equals the expected checksum. A case passes when the number of correct frames equals `framesToCheck`; otherwise it fails and reports either correct or incorrect indices.
- The AV1 film-grain case decodes a second copy with film grain disabled. A checksum mismatch can still count as correct when the three-plane average PSNR stays within 28.0 to 34.0 dB. A mismatch outside that interval raises a quality warning with the frame summary.
- The interleaving path checks every stream independently, requires the total checked-frame count to equal the sum of its per-stream results, and reports incorrect frame indices by stream.
- Status-query cases wait for the frame fence, read one `VkQueryResultStatusKHR` with `VK_QUERY_RESULT_WITH_STATUS_BIT_KHR | VK_QUERY_RESULT_WAIT_BIT`, and reject an error status. Inline queries attach `VkVideoInlineQueryInfoKHR` to the decode command instead of using `vkCmdBeginQuery` and `vkCmdEndQuery`.

## Behavior Parameter Identification

> **Behavior parameter:** decode test family, expressed by the registered test case leaf
>
> **Candidate values:** codec-and-stream correctness (`i`, `i_p`, clip playback, and codec-specific feature clips), ordering and interleaving (`*_not_matching_order`, `interleaved`, `h265_interleaved`), resource/session behavior (`resolution_change`, `resolution_change_dpb`, `resources_without_profiles`, `inline_session_params`, `relaxed_session_params`), status reporting (`query_with_status`, `inline_query_with_status`), and codec-specific bitstream features such as AV1 film grain, AV1 super-resolution, AV1 CDF updates, H.265 scaling lists and long-term references, and VP9 tiles, resize, segmentation, quantizer, SVC, and show-existing-frames.

The DPB mode and image layout are important cross-cutting dimensions, but they do not define the primary behavioral axis: the factory applies both values to the same registered decode case. The leaf selects the stream semantics or API behavior being exercised; `_layered_dpb`/`_separated_dpb` and `_general_layout`/`_video_layout` select the resource realization of that behavior.

## What Failure Means

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

A checksum mismatch means that the displayed decoded samples do not match the stored reference representation. It does not by itself identify whether the source was parsing, codec semantics, DPB state, image layout, synchronization, or host-side conversion; the first failing test option and the reported frame index narrow that investigation.

## Important Variations and Special Cases

- The factory creates four variants for every ordinary definition: layered versus separated DPB, crossed with general versus video layouts. The default mustpass contains those four suffix forms for each registered case.
- H.264 uses High profile for the small clip and Main profile for the 4K IBP clip. H.265 uses Main profile. AV1 uses Main profile with 8-bit or 10-bit 4:2:0 profiles; VP9 uses profile 0 for 8-bit and profile 2 for 10-bit.
- The source uses `ALL_FRAMES` as zero. `TestDefinition` replaces it with `ClipInfo::totalFrames`. Explicit checks cover short prefixes or selected frames: H.264/H.265/AV1 I cases check one frame, I/P cases check two, H.265 scaling-list cases check 28 frames, VP9 feature cases check 2, 5, 7, 10, or 30 frames as registered, and the 4K H.264/H.265 B-frame cases check their full 26-frame clips.
- AV1 film grain forces a separate output when the output and DPB would otherwise coincide, because the displayed post-processing result differs from the reconstructed reference. The test compares the film-grain result with a second no-film-grain decode using PSNR when the exact checksum is not expected to match.
- `IntraOnlyDecodingNoSetupRef` creates a zero-slot session configuration for intra-only streams. The decoder then uses destination layout barriers without a setup reference slot. The VP9 `inter_intra_only` name is a source-specific exception: its clip begins with two inter non-showable frames, so it is not an all-intra stream.
- The source comments out `argon_seqchange_affine_8` and `argon_test787` because available implementations did not explain their failures. The Argon film-grain case checks only its first frame because later parser assertions remain unresolved.
- `RecreateDPBImages` forces a new session and DPB image pool on compatible resolution changes. The H.264 `resolution_change_dpb` case also enables a picture-parameter update trigger used by the NVIDIA decode-client API.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Decode case definitions and variant factory | [`createVideoDecodeTests`](../../../modules/vulkan/video/vktVideoDecodeTests.cpp#L591-L703) | Defines registered leaves, clips, frame counts, options, interleaving streams, and the four DPB/layout variants. |
| Test naming and support flags | [`TestDefinition::getTestName` and `requiredDeviceFlags`](../../../modules/vulkan/video/vktVideoDecodeTests.cpp#L771-L833) | Shows suffix construction and feature gates for status queries, maintenance extensions, VP9, and general layouts. |
| Device and session setup | [`StartVideoSequence`](../../../modules/vulkan/video/vktVideoBaseDecodeUtils.cpp#L493-L633) | Queries capabilities and formats, validates extents, chooses session compatibility, and allocates layered or separated resources. |
| Decode resource roles and layouts | [`DecodePictureWithParameters`](../../../modules/vulkan/video/vktVideoBaseDecodeUtils.cpp#L1714-L1985) | Maps DPB slots and output resources to layouts, barriers, array layers, references, and setup slots. |
| Recording, submission, and status | [`RecordCommandBuffer`, `SubmitQueue`, and `QueryDecodeResults`](../../../modules/vulkan/video/vktVideoBaseDecodeUtils.cpp#L2085-L2252) | Shows reset, query, inline parameter, decode, fence, and status behavior. |
| Cached ordering | [`decodeFramesOutOfOrder`](../../../modules/vulkan/video/vktVideoBaseDecodeUtils.cpp#L2254-L2300) | Records in shuffled order and submits in original order. |
| Host copy and checksum | [`DownloadedFrame::checksum` and `getDecodedImage`](../../../modules/vulkan/video/vktVideoDecodeTests.cpp#L919-L1298) | Defines plane extraction, normalization, queue ownership transfers, and MD5 input. |
| Ordinary and interleaved result checks | [`VideoDecodeTestInstance::iterate`](../../../modules/vulkan/video/vktVideoDecodeTests.cpp#L1381-L1557) and [`InterleavingDecodeTestInstance::iterate`](../../../modules/vulkan/video/vktVideoDecodeTests.cpp#L1563-L1705) | Defines frame comparison, film-grain PSNR, pass/fail messages, and interleaving accounting. |
| Clip metadata and references | [`ClipInfo` and clip table](../../../modules/vulkan/video/vktVideoClipInfo.hpp#L121-L136) and [`Clips`](../../../modules/vulkan/video/vktVideoClipInfo.cpp#L515-L1082) | Maps names to files, profiles, framing, dimensions, total frames, and checksum arrays. |
| Support gates | [`VideoDecodeTestCase::checkSupport`](../../../modules/vulkan/video/vktVideoDecodeTests.cpp#L1749-L1933) | Selects codec extensions, maintenance extensions, synchronization2, standard codec versions, and unified image layouts. |
| Mustpass paths | [`video.txt` decode entries](../../../mustpass/main/vk-default/video.txt#L26-L317) | Confirms exact registered decode paths and their four suffix variants. |
| Vulkan decode semantics | [`Video Decode Operations`](../../../../vulkan-docs/src/chapters/video/decode.adoc#L5-L162) | Defines output/reconstructed pictures, layouts, operation steps, and unsuccessful decode contents. |
| Vulkan DPB and session semantics | [`Video Coding`](../../../../vulkan-docs/src/chapters/videocoding.adoc#L122-L188) and [`Video Sessions`](../../../../vulkan-docs/src/chapters/videocoding.adoc#L1214-L1264) | Defines DPB slot state, backing resources, session state, and session creation. |
| Inline query and session parameter semantics | [`Inline Queries`](../../../../vulkan-docs/src/chapters/videocoding.adoc#L3910-L3955) and [`Video session creation flags`](../../../../vulkan-docs/src/chapters/videocoding.adoc#L1637-L1655) | Grounds maintenance1 inline queries and maintenance2 inline session parameters. |
| Codec-specific operations | [`H.264`](../../../../vulkan-docs/src/chapters/video/h264_decode.adoc#L4-L52), [`H.265`](../../../../vulkan-docs/src/chapters/video/h265_decode.adoc#L4-L52), [`AV1`](../../../../vulkan-docs/src/chapters/video/av1_decode.adoc#L4-L54), and [`VP9`](../../../../vulkan-docs/src/chapters/video/vp9_decode.adoc#L4-L54) | Grounds the codec-family split and codec-specific bitstream/reference semantics. |

## Questions / Risk Points for User Audit

- Does the page distinguish display order from coding order clearly enough for cached and interleaved cases?
- Are the four resource variants presented as cross-cutting dimensions rather than separate codec behaviors?
- Is the checksum path clear about host-side plane conversion and the film-grain PSNR exception?
- Does the support section separate a skipped unsupported case from a decoded frame that fails its checksum?
- Should the two commented-out Argon cases remain documented as source-pruned coverage rather than presented as active mustpass paths?
- Is the distinction between a Vulkan decode operation completing unsuccessfully with undefined output and a CTS internal error clear?

## Conversion Notes for Final Wiki Page

- Carry the behavior-axis conclusion into `## Behavior Parameters`: the test case leaf selects the codec syntax or API behavior, while DPB mode and image layout are orthogonal realization dimensions.
- Copy the `### Failure Cause Mapping` table above directly into `## Failure Meaning` in the final page. Write `### Cause Analysis` from the source and spec rather than copying it from this brief.
- Distill the DPB, output/reconstructed picture, and coding/display-order material into short prerequisite bullets. Keep the concrete H.264 I/P/B example as a concise parameter and execution explanation.
- Use a no-walkthrough shader section because this implementation performs fixed-function video decode and host-side image checking; no shader source participates in the tested behavior.
- Keep clip metadata in a compact table grouped by codec and frame count. Put full source entry points in the appendix.
- Preserve exact registered names, option names, extension names, layouts, frame counts, and mustpass suffixes.
