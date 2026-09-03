## Overview

**Core question:** Can the AV1 encoder produce decodable pictures with the requested coding controls and acceptable quality?

- This page covers the implementation in [`vktVideoEncodeTestsAV1.cpp`](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp), registered below `video.encode.av1`.
- The generator combines picture format, GOP, ordering, resolution-change, quantization, tiling, superblock, rate-control, filtering, DPB, and intra-refresh definitions, then discards combinations that the test design does not support.
- The default mustpass contains 5,600 surviving AV1 encode leaves under fourteen picture-format roots. The roots are seven resolutions paired with 8-bit or 10-bit 4:2:0 input ([`video.txt`](../../../mustpass/main/vk-default/video.txt)).
- Each case creates or loads a YCbCr input clip, configures the AV1 encoder, encodes every frame, decodes the resulting IVF stream, checks each decoded extent, and compares each frame with the source using PSNR.
- The page explains the generated matrix, the behavior families it covers, capability and design pruning, and what different validation failures can indicate.

## Background Knowledge

- A Vulkan video picture resource identifies an image subresource and a coded offset and extent. Video operations may access padding required by picture-access granularity, so a displayed extent and the image storage extent are not always identical ([video picture resources](../../../../vulkan-docs/src/chapters/videocoding.adoc#L25-L94)).
- An encoded frame can become a reconstructed picture and a later reference picture. The decoded picture buffer (DPB) associates indexed slots with picture resources, while the video session maintains slot state ([DPB state and backing store](../../../../vulkan-docs/src/chapters/videocoding.adoc#L113-L188)). This is needed to understand GOP references and the separate and layered DPB cases.

## Registration Hierarchy

```text
video.encode.av1
├── 128x128_8le_420
├── 128x128_10le_420
├── 176x144_8le_420
├── 176x144_10le_420
├── 352x288_8le_420
├── 352x288_10le_420
├── 720x480_8le_420
├── 720x480_10le_420
├── 1920x1080_8le_420
├── 1920x1080_10le_420
├── 3840x2160_8le_420
├── 3840x2160_10le_420
├── 7680x4320_8le_420
└── 7680x4320_10le_420
```

The `av1` test family is created by [`createVideoEncodeTestsAV1`](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L1342-L1399). Each direct child names a resolution, bit depth, and chroma subsampling combination that has surviving leaves in the default mustpass.

## Parameter Dimensions and Observed Values

The following are the candidate values in the source definition vectors. The generator does not register their unrestricted Cartesian product. `validateTestDefinition` removes combinations before a `TestCase` is created, and the mustpass file records the surviving leaves.

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Resolution | `128x128`, `176x144`, `352x288`, `720x480`, `1920x1080`, `3840x2160`, `7680x4320` | Selects input and expected picture dimensions and participates in special-case pruning. | [`frameSizeTests`](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L1234-L1237) |
| Bit depth | `8le`, `10le`, `12le` | Selects the YCbCr sample depth and the encode profile format check. | [`bitDepthTests`](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L1239-L1243) |
| Chroma subsampling | `400`, `420`, `422`, `444` | Selects the input chroma layout and the required supported image format. | [`subsamplingTests`](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L1245-L1250) |
| GOP | `i_15`, `i_p_15`, `i_p_open_15`, `i_p_b3_13_15`, `idr_p_b3_13_15`, `i_p_empty_region_2`, `i_p_midway_7` | Changes frame types, reference dependencies, closed or open GOP behavior, B-frame count, and frame count. | [`gopTests`](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L1252-L1260) |
| Recording order | ``, `unordered` | Selects ordered recording or out-of-order recording of the video work. | [`orderingTests`](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L1273-L1276) |
| Resolution change | ``, `res_to_larger`, `res_to_smaller` | Represents a requested change of coded resolution. The current generator keeps only no-change cases. | [`resolutionChangeTests`](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L1278-L1282), [`validateTestDefinition`](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L972-L974) |
| Q index | ``, `qindex64`, `qindex128`, `qindex192`, `qindex255` | Sets I, P, and B quantization values. Non-default Q index cases require disabled rate control. | [`quantizationTests`](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L1284-L1287), [`buildEncoderParams`](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L874-L881) |
| Tiling | ``, `tiling_1x2`, `tiling_4x4` | Selects one tile, a 1 by 2 tile arrangement, or a 4 by 4 arrangement and changes tile capability requirements. | [`tilingTests`](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L1289-L1293), [`buildEncoderParams`](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L819-L856) |
| Superblock size | ``, `superblocks_128x128` | Selects the AV1 coding block size and the required capability bit. The current generator keeps only 64x64. | [`superblockTests`](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L1295-L1298), [`validateTestDefinition`](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L968-L970) |
| Rate control | ``, `rc_disabled`, `rc_cbr`, `rc_vbr` | Selects default, disabled, constant-bitrate, or variable-bitrate encoding. | [`rateControlTests`](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L1300-L1305) |
| Loop filter | ``, `lf` | Enables or disables the AV1 loop filter. | [`lfTests`](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L1307-L1310) |
| Loop restoration | ``, `lr` | Enables or disables loop restoration. | [`lrTests`](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L1312-L1315) |
| CDEF | ``, `cdef` | Enables or disables constrained directional enhancement filtering. | [`cdefTests`](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L1317-L1320) |
| DPB mode | ``, `layered_dpb` | Selects separate reference images or a layered DPB image arrangement. | [`dpbModeTests`](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L1322-L1325), [`buildEncoderParams`](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L895-L907) |
| Intra refresh | ``, `intra_refresh_picture_partition`, `intra_refresh_row_based`, `intra_refresh_column_based`, `intra_refresh_any_block_based`, `intra_refresh_row_based_empty_region`, `intra_refresh_column_based_empty_region`, `intra_refresh_any_block_based_empty_region`, `intra_refresh_picture_partition_midway`, `intra_refresh_row_based_midway`, `intra_refresh_column_based_midway`, `intra_refresh_any_block_based_midway` | Selects the refresh granularity and the empty-region or midway special case. | [`intraRefreshTests`](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L1327-L1340) |

The output filename preserves the selected format, GOP, frame count, and non-default suffixes. The input filename contains the base clip, dimensions, subsampling, and bit depth ([`buildClipName`](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L368-L390)).

## Behavior Parameters

The primary behavior axis is the **AV1 encode behavior family**. These families group parameters by the property they change, rather than treating every encoder option as a separate correctness claim.

### Regular GOP and picture coding: frame dependencies

The `i`, `i_p`, `i_p_open`, `i_p_b3_13`, and `idr_p_b3_13` GOP definitions exercise intra pictures, predicted pictures, open or closed GOP handling, and B-frame references. The encoder receives the frame count, IDR period, GOP size, closed-GOP flag, and consecutive B-frame count ([GOP argument construction](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L795-L817), [GOP definitions](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L1252-L1260)).

### Tiling: coded picture partitions

The one-tile case leaves tile arguments out. The 1 by 2 case computes tile dimensions in superblocks and passes explicit tile parameters. The 4 by 4 case requests four columns and four rows. Capability checks compare the requested tile counts and derived tile dimensions with AV1 limits ([tiling arguments](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L819-L856), [tile checks](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L666-L689)).

### Quantization and rate control: reconstruction quality

Q index values are applied to I, P, and B pictures. The source permits non-default Q index values only when rate control is disabled. CBR and VBR cases instead require the corresponding encode capability bit ([Q index and rate-control pruning](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L980-L982), [rate-control checks](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L631-L641)). The final quality result is measured against the decoded reconstruction, not against the encoded file size.

### Loop restoration and filtering: post-processing state

The `lf`, `lr`, and `cdef` suffixes enable the corresponding AV1 encoder options. They may be combined in the surviving 720x480 matrix, subject to the other design restrictions. The options are passed as flags to the encoder ([filter arguments](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L883-L893)).

### DPB layout: reference storage

The default suffix uses separate reference images, while `layered_dpb` requests a layered DPB. The requirement builder maps the latter to an array-backed DPB requirement, and the support check rejects a separate-image case when the implementation lacks `VK_VIDEO_CAPABILITY_SEPARATE_REFERENCE_IMAGES_BIT_KHR` ([requirement mapping](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L1127-L1132), [DPB capability check](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L660-L664)).

### Picture ordering: recording order

The empty ordering suffix records work in the normal order. `unordered` adds `--testOutOfOrderRecording`. The generator permits out-of-order recording only for the B-frame shape required by its condition, so this family focuses on recording order while retaining a defined reference pattern ([ordering pruning](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L976-L978), [ordering argument](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L909-L910)).

### Intra refresh: partial picture refresh

The four ordinary refresh modes map to per-picture partition, block-row, block-column, and block-based Vulkan modes. The source also defines empty-region and midway cases. It computes a cycle duration from the supported superblock size, tile limits, picture dimensions, and `maxIntraRefreshCycleDuration`; midway cases use a four-frame cycle and restart index 2 ([cycle calculation](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L743-L792), [refresh arguments](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L912-L951)).

## Shader Analysis

No shader is used by this test. The behavior is implemented by the Vulkan video encoder and by the decode and PSNR validation path, so no shader walkthrough is applicable.

## Runtime Execution and Result Checking

- `createInstance` builds the encoder argument list and the input and output clip names. If the input YCbCr clip is absent, the test generates it with the maximum registered GOP frame count and the selected dimensions, subsampling, and bit depth ([instance setup](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L488-L559)).
- The test builds an AV1 profile using `STD_VIDEO_AV1_PROFILE_MAIN`, the selected chroma and bit-depth requirements, and the AV1 encode operation. It checks required extensions, B-frame support, rate-control support, superblock support, coded extents, tile limits, supported formats, and intra-refresh capabilities before creating the encoder ([capability validation](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L588-L733)).
- The encode loop calls `EncodeNextFrame` and then `GetBitstream` for every input frame. It stops on the first error. Content validation starts only when all frames encoded and the final encoded frame count matches the total ([encode loop](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L423-L461)).
- AV1 output uses IVF framing. The validation path creates a decoder with the selected AV1 profile, demuxes the output, and obtains one decoded frame per expected frame ([AV1 decode selection](../../../modules/vulkan/video/vktVideoTestUtils.cpp#L339-L416)).
- For each frame, validation checks the decoded display extent, converts the decoded image to I420, loads the matching source frame, and computes `PSNRImplicitCrop`. It uses the selected bit depth for the conversion ([per-frame comparison](../../../modules/vulkan/video/vktVideoTestUtils.cpp#L418-L458)).
- A PSNR below 50.0 but above 10.0 returns a quality warning. A PSNR at or below 10.0 fails. If all frames meet the quality check, the result is `Video encoding completed successfully` ([result thresholds](../../../modules/vulkan/video/vktVideoTestUtils.cpp#L460-L484)).
- Unless video dump mode requests the encoded bitstream, the test removes the output clip before returning ([output cleanup](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L468-L471)).

## Failure Meaning

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

### Cause Analysis

#### Regular GOP and picture coding failures

**Possible failure symptoms:** The encoder may fail on a particular frame, fail to provide its bitstream, produce too few decodable IVF frames, report a decoded extent mismatch, or produce a low PSNR reconstruction.

**Possible implementation causes:** The AV1 frame and reference state may not match the requested I/P/B or IDR pattern. The source confirms that B-frame cases require `maxBidirectionalCompoundReferenceCount` support, but it does not identify a more specific implementation cause. Further investigation is needed if the failure occurs after those checks pass.

#### Tiling failures

**Possible failure symptoms:** If a tiled case executes, it may fail during encoding, produce an undecodable stream, or produce a decoded frame whose PSNR falls below the threshold.

**Possible implementation causes:** The encoder may reject the requested tile count, derive tile dimensions incorrectly, or encode tile boundaries inconsistently with the AV1 syntax. The source validates minimum and maximum tile dimensions before execution, so a failure after that check needs implementation investigation rather than an assumption about a particular hardware block.

#### Quantization and rate-control failures

**Possible failure symptoms:** A Q-index or CBR/VBR case may be skipped for a missing capability, fail while encoding, or decode successfully with a quality warning or failure.

**Possible implementation causes:** The selected Q index may not reach the encoder correctly, rate-control state may not honor the requested mode, or the resulting reconstruction may differ enough from the source to cross a PSNR boundary. The source checks only the advertised CBR or VBR capability and the design rule for Q index combinations; it does not prove which internal rate-control stage caused a quality result.

#### Loop restoration and filtering failures

**Possible failure symptoms:** The stream may fail to encode or decode, or a case with `lf`, `lr`, or `cdef` may produce a warning or failure from the per-frame PSNR check.

**Possible implementation causes:** The encoder may omit, misconfigure, or incorrectly apply the selected AV1 post-processing state. The CTS check observes the decoded reconstruction, so it cannot distinguish a syntax error from a filter implementation error without additional diagnostics.

#### DPB layout failures

**Possible failure symptoms:** A DPB case may be skipped when separate reference images are unsupported, fail during encoder creation, fail on a reference-dependent frame, produce too few decoded frames, or produce low PSNR.

**Possible implementation causes:** The image arrangement, DPB slot association, layered array layer selection, or separate reference-image path may not match the requested mode. Vulkan defines DPB slot state separately from its backing picture resources, so failures can involve either the session state or the resource association. The test source does not localize the cause further.

#### Picture ordering failures

**Possible failure symptoms:** An out-of-order case may fail during encoding, fail to retrieve a bitstream for a frame, or produce a stream that decodes with an extent or PSNR failure.

**Possible implementation causes:** The recording order may not be reconciled with the frame dependency order for the B-frame GOP, or the encoder may associate a reference with the wrong picture. The source intentionally limits this case to a defined B-frame shape, but it does not identify whether a later failure belongs to command recording, queue submission, or codec state.

#### Intra-refresh failures

**Possible failure symptoms:** An intra-refresh case may be skipped for a missing extension or mode, fail during encoder creation or frame encoding, or decode with a frame count, extent, or PSNR failure.

**Possible implementation causes:** The implementation may advertise a mode but apply the refresh cycle or region differently from the requested picture-partition, row, column, block, empty-region, or midway case. The source derives cycle duration from capabilities and fixes the midway restart index, so a failure after capability validation requires investigation of refresh state and encoded syntax.

## Case Pruning

### Requirement-based pruning

- The test requires `VK_KHR_video_queue`, `VK_KHR_video_encode_queue`, and `VK_KHR_video_encode_av1`. Intra-refresh cases also require `VK_KHR_video_encode_intra_refresh` ([requirement construction](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L1108-L1115), [intra-refresh requirements](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L1182-L1205)).
- Support checks require the AV1 encode operation, the AV1 Main profile, a supported matching picture format, coded extents within `minCodedExtent` and `maxCodedExtent`, requested superblock support, and the relevant tile limits ([capability query and limits](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L588-L720)).
- B-frame cases require a nonzero `maxBidirectionalCompoundReferenceCount`. CBR and VBR cases require the corresponding rate-control capability. A separate DPB case requires separate reference-image support ([capability gates](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L625-L664)).
- Intra-refresh cases require a supported refresh mode. Midway cases require `maxIntraRefreshCycleDuration >= 4` ([intra-refresh support](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L722-L733)).

These checks mean that a case can be legal in the test definition but unsupported by the current device and therefore skipped before execution.

### Design-based pruning

- The generator keeps only 4:2:0 input and removes 12-bit input because those combinations are not supported by the current vendor coverage assumptions ([format pruning](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L960-L966)).
- It keeps only 64x64 superblocks and no resolution change. The source also uses a resolution guard that restricts the nested controls to 720x480 and requires the I/P/B family for other resolutions ([matrix pruning](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L968-L1042)).
- It removes 1 by 2 tiling at 7680x4320 because the source identifies that combination as outside the AV1 specification's tile-width limit ([large-resolution pruning](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L1044-L1047)).
- Non-intra-refresh cases cannot use the special `i_p_midway` or `i_p_empty_region` GOPs. Intra-refresh cases are fixed to 352x288, ordered I/P coding, no resolution change, default quantization and rate control, 64x64 superblocks, and disabled loop filter, loop restoration, and CDEF ([intra-refresh design rules](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L985-L1027)).
- Empty-region cases require two frames, `i_p_empty_region`, and one tile. Midway cases require seven frames and `i_p_midway` ([special GOP rules](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L1004-L1025)).

These exclusions define the intended coverage shape. They are not device capability results.

## Key Takeaways

- AV1 coverage is a generated matrix, but the default mustpass contains the 5,600 combinations that survive the source's format, resolution, GOP, special-case, and tile rules.
- The fourteen direct registration children identify the supported format roots in the default mustpass: seven resolutions at two bit depths, all using 4:2:0 input.
- The test validates more than successful encode calls. It decodes the IVF stream, checks every frame's display extent, and compares every frame with the source using PSNR.
- A quality warning and a failure are distinct results. PSNR below 50.0 is a warning unless it reaches the critical threshold of 10.0 or lower.
- The failure family matters when triaging a result. GOP, tile, rate-control, filter, DPB, ordering, and intra-refresh failures exercise different state and resource relationships.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| AV1 test registration | [`createVideoEncodeTestsAV1`](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L1342-L1399) | Creates the `video.encode.av1` test family and its fourteen format roots. |
| Definition vectors | [`frameSizeTests` through `intraRefreshTests`](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L1234-L1340) | Supplies the generated dimensions and candidate values. |
| Test-name construction | [`buildTestName`](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L1077-L1106) | Shows how non-default behavior suffixes enter the executable case name. |
| Design pruning | [`validateTestDefinition`](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L955-L1056) | Removes invalid and intentionally unsupported combinations before registration. |
| Capability pruning | [`checkSupport` and `validateCapabilities`](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L566-L733) | Checks extensions, codec capabilities, limits, formats, and intra-refresh support. |
| Encoder configuration | [`buildEncoderParams`](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L795-L951) | Maps each surviving definition to AV1 encoder arguments. |
| Encode loop | [`VideoTestInstance::iterate`](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L423-L471) | Encodes all frames and invokes content validation. |
| Encoded-content validation | [`validateEncodedContent`](../../../modules/vulkan/video/vktVideoTestUtils.cpp#L339-L484) | Demuxes and decodes IVF output, checks extents, computes PSNR, and returns status. |
| Default mustpass coverage | [`video.txt`](../../../mustpass/main/vk-default/video.txt) | Records the surviving AV1 encode leaves. |
| Video picture resources | [`videocoding.adoc`](../../../../vulkan-docs/src/chapters/videocoding.adoc#L25-L94) | Defines coded extents and picture-resource access. |
| DPB semantics | [`videocoding.adoc`](../../../../vulkan-docs/src/chapters/videocoding.adoc#L113-L188) | Defines reconstructed pictures, reference pictures, DPB slots, and backing resources. |
