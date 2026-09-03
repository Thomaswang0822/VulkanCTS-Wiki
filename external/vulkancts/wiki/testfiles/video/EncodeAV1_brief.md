# Understanding Brief: AV1 encode tests

## One-Sentence Test Purpose

This test checks whether an AV1 video encode implementation can encode the generated YCbCr input cases across the registered picture, GOP, tiling, rate-control, filtering, DPB, ordering, and intra-refresh choices and produce decodable output with acceptable quality.

## Background Knowledge

### Video encode pictures and coded extents

Vulkan video encode operations consume video picture resources backed by `VkImage` objects. A picture resource identifies an image view, array layer, coded offset, and coded extent. Access can include padding required by picture-access granularity, so the displayed extent and the storage extent are related but are not always identical. The Vulkan video-coding chapter defines these resources and their coded extents ([video picture resources](../../../../vulkan-docs/src/chapters/videocoding.adoc#L25-L94)).

Why it matters here:
- The test creates an input YCbCr clip at the selected width, height, chroma subsampling, and bit depth.
- The output decoder compares the decoded picture against the input using the expected output extent. If the AV1 coded-picture alignment rounds the extent, validation uses that rounded extent rather than assuming the raw input dimensions always describe the decoded image.

### Reconstructed pictures, references, and the DPB

An encode operation may produce a reconstructed picture that later acts as a reference picture. The decoded picture buffer (DPB) holds indexed reference-picture slots. Vulkan separates DPB slot state in the video session from the image resources that back those slots, while the application maintains the slot-to-resource association ([DPB model](../../../../vulkan-docs/src/chapters/videocoding.adoc#L113-L188)).

Why it matters here:
- I/P/B GOPs depend on reference-picture management, and the separate and layered DPB choices exercise different resource arrangements.
- An encode result can be syntactically produced yet fail the later decode and quality check if references, picture extents, or output frames are wrong.

## One Concrete Example

A representative ordinary case is the registered path `dEQP-VK.video.encode.av1.720x480_8le_420.i_p_b3_13_15.default`.

The generator selects a 720x480, 8-bit, 4:2:0 input, an I/P/B GOP with 15 frames and three consecutive B frames, one tile, ordered recording, default quantization, 64x64 superblocks, default rate control, loop filtering and restoration disabled, CDEF disabled, and the separate DPB mode. The test creates or loads a YCbCr input clip, passes the matching AV1 encoder options to `VulkanVideoEncoder`, encodes every frame, obtains each bitstream, then decodes the IVF output and checks every displayed frame.

The output check is per frame. It first checks that the decoded display extent matches the expected extent, then computes PSNR against the corresponding source frame. A PSNR below 50.0 but above the critical 10.0 threshold produces a quality warning; a PSNR at or below 10.0 fails the case. The implementation of this check is in [`validateEncodedContent`](../../../modules/vulkan/video/vktVideoTestUtils.cpp#L339-L484), and AV1 invokes it after all frames have encoded ([`VideoTestInstance::iterate`](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L423-L471)).

## End-to-End Test Flow

```text
[host] select one value from each AV1 definition vector and reject invalid combinations
[host] build the exact registered test name and requirement set
[host] construct the input clip path from dimensions, chroma, and bit depth
[host] generate the YCbCr clip when the archived input file is absent
[host] build AV1 encoder arguments for frame count, GOP, tiling, quantization, rate control, filtering, DPB, ordering, and intra refresh
[host] query AV1 encode capabilities, video profile capabilities, supported formats, limits, and required extensions
[host] create the Vulkan video encoder and expected output extent
[host] encode each input frame and retrieve its bitstream
[host] open the encoded IVF stream with the AV1 decoder path
[device] decode each encoded frame through a decode queue and obtain the decoded picture
[host] check the decoded display extent against the expected output extent
[host] compute PSNR between each source frame and decoded frame
[host] return pass, quality warning, or failure and remove the output clip unless dump mode requests it
```

The host-side support check rejects unsupported cases before encoder creation. The encode loop stops at the first `EncodeNextFrame` or `GetBitstream` error. Validation only starts when every frame encoded and the encoder reported the expected final frame count ([AV1 test instance](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L423-L471)).

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The test does not generate a shader. Its generated artifacts are the multidimensional case definitions, a raw YCbCr input clip when needed, encoder command-line parameters, and the encoded AV1 IVF stream. The frame generator uses the maximum registered GOP frame count, which is 15, even though special intra-refresh cases use two or seven frames ([frame and GOP definitions](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L1232-L1270)). The output filename includes the GOP, frame count, and non-default behavior suffixes ([clip naming](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L368-L390)).

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|---|---|---|---|---|---|
| YCbCr input clip | yes, loaded or generated | passed to the encoder | read by the encode implementation | read again as the reference | Supplies the source frame for each PSNR comparison. |
| Video encode picture resources | configured by `VulkanVideoEncoder` | yes | read as encode input and used for reconstructed/reference pictures | decoded output is read through the validation path | Carries the Vulkan video image data and coded extents. |
| DPB backing images | configured by the encoder | yes | written as reconstructed pictures and read as references | indirectly observed through decoded output | Separate or layered DPB selection changes reference storage. |
| Encoded IVF bitstream | created as an output file | consumed by the decoder | written by encoding and read by demux/decode | yes | Connects the encode result to the independent decode and quality check. |
| Decoded output image | configured by the decoder validation path | yes | written by decode | yes, converted to I420 | Supplies the frame compared with the source. |

The AV1 page describes the encoder and decoder resources at the level exposed by the test. It does not claim that the raw clip or IVF file is itself a Vulkan resource.

## What Is Checked

- The encoder must successfully encode all frames. A failure from `EncodeNextFrame` reports the frame index; a failure from `GetBitstream` reports the frame whose bitstream could not be retrieved.
- The final encoded frame count must satisfy `frameNumEncoded + 1 == totalFrames` before content validation begins.
- The IVF stream must yield the requested number of decoded frames. Fewer frames are treated as an internal CTS error or invalid bitstream.
- Every decoded frame must have the expected display width and height. The expected extent is rounded to the AV1 coded-picture alignment when that alignment is not 8x8 ([expected extent calculation](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L542-L550)).
- The decoded frame is converted to I420 and compared with the corresponding source frame using `PSNRImplicitCrop`. The test uses a 50.0 lower quality threshold and a 10.0 critical threshold ([PSNR checking](../../../modules/vulkan/video/vktVideoTestUtils.cpp#L426-L484)).
- A result below 50.0 and above 10.0 is a quality warning. A result at or below 10.0 is a failure. If all frames pass the quality check, the test returns `Video encoding completed successfully`.

## Behavior Parameter Identification

> **Behavior parameter:** AV1 encode behavior family
>
> **Candidate values:** regular GOP and picture coding, tiling, quantization and rate control, loop restoration and filtering, DPB layout, picture ordering, intra refresh

The test generator combines many configuration dimensions, but the behavior axis is the family of AV1 coding behavior being exercised. The family boundaries correspond to the option groups that change frame dependencies, coded partitions, quantization, post-processing, reference storage, recording order, or refresh behavior.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| regular GOP and picture coding | AV1 frame-type or reference-picture handling, encoder setup, bitstream production, or decode compatibility. |
| tiling | AV1 tile configuration, tile-size limits, tile boundary coding, or encoder handling of tile parameters. |
| quantization and rate control | Unsupported or incorrectly applied Q-index or rate-control configuration, bitrate control, or resulting reconstruction quality. |
| loop restoration and filtering | AV1 loop-filter, loop-restoration, or CDEF syntax/state handling, or filtering that produces unacceptable reconstruction. |
| DPB layout | Reference-image allocation, DPB slot association, layered-array indexing, or separate-reference-image handling. |
| picture ordering | Submission or recording order handling, especially for out-of-order recording with B-frame references. |
| intra refresh | Intra-refresh capability negotiation, refresh-cycle calculation, refresh region selection, or refresh state in the encoded stream. |

## Important Variations and Special Cases

- The source definition vectors contain seven resolutions, three bit depths, four chroma subsampling modes, seven GOP definitions, two ordering values, three resolution-change values, five Q-index values, three tiling values, two superblock sizes, four rate-control modes, two loop-filter values, two loop-restoration values, two CDEF values, two DPB modes, and twelve intra-refresh definitions ([definition vectors](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L1234-L1340)).
- The registered mustpass contains 5,600 surviving AV1 encode leaves and fourteen direct picture-format roots. Those roots are the seven resolutions paired with 8-bit and 10-bit 4:2:0 input ([AV1 mustpass entries](../../../mustpass/main/vk-default/video.txt)). The source prunes all non-4:2:0 cases, 12-bit input, 128x128 superblocks, and resolution changes at generation time ([definition pruning](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L955-L1056)).
- The nested combination matrix is intentionally concentrated on 720x480. For other resolutions, the source requires the I/P/B family and default values for the other nested controls. The source condition uses `width != 720 && height != 480`, so this statement follows the implementation's exact condition rather than treating it as a general aspect-ratio rule.
- Intra-refresh cases are fixed to 352x288, ordered I/P coding, 64x64 superblocks, default rate control, no filtering or quantization override, and no resolution change. Empty-region cases use two frames and `i_p_empty_region`; midway cases use seven frames, `i_p_midway`, a four-frame refresh cycle, and restart index 2 ([intra-refresh setup](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L743-L792), [intra-refresh pruning](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L985-L1027)).
- The source excludes 1x2 tiling at 7680x4320 because the AV1 specification's maximum tile width makes that combination invalid. Runtime support checks additionally cover extensions, B-frame support, rate-control modes, superblock sizes, coded extents, DPB image mode, tile limits, picture formats, and intra-refresh capabilities ([capability checks](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L566-L733)).

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| AV1 registration and matrix construction | [`createVideoEncodeTestsAV1`](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L1342-L1399) | Builds the `av1` test category and combines the definition vectors. |
| Registered surviving leaves | [`video.txt`](../../../mustpass/main/vk-default/video.txt) | Confirms the default mustpass AV1 encode coverage. |
| Generated dimensions and values | [`frameSizeTests` through `intraRefreshTests`](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L1234-L1340) | Defines the candidate values used by the generator. |
| Design pruning | [`validateTestDefinition`](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L955-L1056) | Removes unsupported or intentionally invalid combinations before registration. |
| Support and format validation | [`validateCapabilities`](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L588-L733) | Maps a case to required Vulkan capabilities and limits. |
| Encode and validation flow | [`VideoTestInstance::iterate`](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L423-L471) | Encodes all frames, retrieves bitstreams, and starts content validation. |
| Decode and PSNR validation | [`validateEncodedContent`](../../../modules/vulkan/video/vktVideoTestUtils.cpp#L339-L484) | Decodes IVF output, checks extent, computes PSNR, and returns status. |
| Video picture and DPB semantics | [`videocoding.adoc`](../../../../vulkan-docs/src/chapters/videocoding.adoc#L25-L188) | Grounds the resource and reference-picture model. |

## Questions / Risk Points for User Audit

- Is the behavior-family axis useful for readers, or should the final page emphasize a narrower axis such as GOP structure and treat the other dimensions as configuration?
- Is the distinction between generation-time pruning and capability-based runtime skipping clear?
- Does the quality-warning boundary at PSNR 50.0 and the failure boundary at 10.0 need a small result table in the final page?
- Should the final page call out the 5,600 mustpass leaves, or is the dimension table enough for navigation?
- The source comment says that 1x2 tiling is removed at 7680x4320 because of `MAX_TILE_WIDTH` in the AV1 specification. Is the specification citation sufficiently direct for the final page, or should this remain a source-level note?

## Conversion Notes for Final Wiki Page

- Keep `## Background Knowledge` to the two concepts needed later: coded extents and DPB/reference pictures.
- Use `video.encode.av1` with the fourteen direct picture-format roots as the single registration tree. Put the large leaf matrix in the parameter table instead of expanding it in the tree.
- Retain the full generated dimension inventory, but separate registered candidates from the fourteen mustpass picture-format roots and the 5,600 surviving leaves.
- Carry the behavior-family conclusion into `## Behavior Parameters` and use one subsection per candidate value.
- Copy the `### Failure Cause Mapping` table into the final page without changing its rows. Write `### Cause Analysis` independently.
- State in `## Shader Analysis` that no shader is involved. This page needs the reviewed video no-walkthrough exception, but the assignment forbids editing the shared exception registry; report that validator blocker rather than modifying the registry.
- Preserve the host/device flow in a compact list, with the encode loop, IVF decode, extent check, PSNR thresholds, and cleanup behavior.
