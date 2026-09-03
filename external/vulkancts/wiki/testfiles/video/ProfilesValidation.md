## Overview

**Core question:** Does one video profile produce consistent answers across profile, capability, format, image, and session APIs?

- This page covers the `profiles` test family implemented in [`vktVideoProfilesValidationTests.cpp`](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L38-L1324).
- The generator registers decode branches for H.264, H.265, AV1, and VP9, plus encode branches for H.264, H.265, and AV1.
- Each case describes one codec profile, chroma-subsampling mode, luma bit depth, and chroma bit depth. H.264 decode adds a picture layout; AV1 decode adds a film-grain choice.
- The test checks two outcomes. Invalid codec and picture-format combinations must not be reported as supported. Supported profiles must give mutually consistent capability, video-format, ordinary format, image-format, and video-session results.
- The default mustpass file lists 1,170 generated paths under `video.profiles`: 810 decode cases and 360 encode cases ([mustpass entries](../../../mustpass/main/vk-default/video.txt#L7859-L9028)).

## Background Knowledge

- A `VkVideoProfileInfoKHR` identifies a codec operation and its chroma subsampling, luma bit depth, and chroma bit depth. Its `pNext` chain supplies the codec-specific profile. Vulkan uses this complete description for capability and format queries and for resource creation ([video profile definition](../../../../vulkan-docs/src/chapters/videocoding.adoc#L321-L352)).
- Chroma subsampling describes the spatial rate of chroma samples relative to luma. 4:2:0 halves chroma sampling horizontally and vertically, 4:2:2 halves it horizontally, and 4:4:4 preserves the luma sampling rate for all three components. Monochrome has no chroma samples ([chroma definitions](../../../../vulkan-docs/src/chapters/videocoding.adoc#L486-L507)).
- Vulkan stores luma and chroma bit depth in separate fields. The test generates them independently for non-monochrome profiles, so it can check mixed pairs such as 8-bit luma with 10-bit chroma. Codec rules may still make such a pair invalid.
- A returned `VkVideoFormatPropertiesKHR` entry is more than a format name. It reports image type, tiling, usage flags, creation flags, and component mapping for a profile and requested usage. Vulkan requires those properties to agree with ordinary format and image-format queries ([video format contract](../../../../vulkan-docs/src/chapters/videocoding.adoc#L1023-L1120)).

## Registration Hierarchy

```text
video.profiles
├── decode
└── encode
```

Each direct child contains codec intermediate nodes. `decode` contains `h264`, `h265`, `av1`, and `vp9`; `encode` contains `h264`, `h265`, and `av1`. The registration function builds those branches and attaches all generated leaves ([registration](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L1096-L1324)).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Operation and codec | decode H.264, H.265, AV1, VP9; encode H.264, H.265, AV1 | Selects the codec-specific profile and capability structures, queue direction, required extensions, image usages, and standard header used for session creation. | [codec loop and branches](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L1100-L1104), [support checks](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L809-L848) |
| H.264 profile | `baseline`, `main`, `high`, `high_444_predictive` | Changes the allowed chroma and depth combinations. | [H.264 profiles and names](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L868-L910) |
| H.264 decode picture layout | `progressive`, `interlaced_interleaved_lines`, `interlaced_separate_planes` | Extends the H.264 decode profile and can cause `VK_ERROR_VIDEO_PICTURE_LAYOUT_NOT_SUPPORTED_KHR`. | [layout generation](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L1117-L1128), [profile errors](../../../../vulkan-docs/src/chapters/videocoding.adoc#L354-L379) |
| H.265 profile | `main`, `main_10`, `main_still_pic`, `format_range_ext`, `scc_ext` | Changes the codec-level picture-format compatibility rules. | [H.265 profiles and names](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L913-L941) |
| AV1 profile | `main`, `high`, `professional` | Selects AV1 profile restrictions on chroma and bit depth. | [AV1 profiles and names](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L943-L972) |
| AV1 decode film grain | `with_filmgrain`, `without_filmgrain` | States whether sessions for the profile can decode pictures with AV1 film grain enabled. | [AV1 naming](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L963-L969), [AV1 decode profile semantics](../../../../vulkan-docs/src/chapters/video/av1_decode.adoc#L164-L198) |
| VP9 profile | `profile0`, `profile1`, `profile2`, `profile3` | Selects VP9 chroma and component-depth restrictions. | [VP9 names](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L974-L998) |
| Chroma subsampling | `monochrome`, `420`, `422`, `444` | Describes the profile's component sampling and must agree with the codec profile and returned image format. | [chroma loop](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L1110-L1115) |
| Luma bit depth | `luma_8bit`, `luma_10bit`, `luma_12bit` | Describes the luma component and is checked against the returned YCbCr format. | [depth values and naming](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L1051-L1064) |
| Chroma bit depth | `chroma_8bit`, `chroma_10bit`, `chroma_12bit` | Describes the chroma components independently from luma for non-monochrome cases. | [depth values and naming](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L1066-L1079) |

For non-monochrome cases, registration forms the full 3 by 3 luma/chroma depth product. This includes mixed-depth cases that some codec profiles must reject. For monochrome, the generator keeps only equal field values because it ignores chroma depth as a behavioral distinction ([generation loops and omission](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L1167-L1174)).

The test name records each active profile choice. For example, `video.profiles.decode.av1.main_without_filmgrain_420_luma_8bit_chroma_8bit` names the operation, codec, standard profile, film-grain choice, chroma mode, and both depths. A nearby mixed case, `video.profiles.decode.av1.main_without_filmgrain_420_luma_8bit_chroma_10bit`, should not produce a successful capability result because the test requires equal component depths for non-monochrome AV1 profiles.

## Behavior Parameters

The primary behavioral axis is the operation and codec-specific profile branch. It selects the profile structure, compatibility rules, query chain, queue direction, and video-session header. Chroma and independent luma/chroma depths supply a secondary picture-format axis within every branch.

### `decode.h264`: H.264 decoding

This branch tests four H.264 standard profiles across three picture layouts. Baseline and main accept only 8-bit 4:2:0 in the CTS compatibility model. High accepts 8-bit monochrome or 4:2:0, while high 4:4:4 predictive retains the wider generated matrix. Successful profiles continue through decode DPB and output checks.

### `decode.h265`: H.265 decoding

This branch tests five H.265 profiles. Main and main still picture accept 8-bit 4:2:0. Main 10 accepts 8-bit or 10-bit 4:2:0. The format-range and SCC extension profiles retain the wider generated matrix because `validateProfileCodec` does not narrow their default chroma and depth masks.

### `decode.av1`: AV1 decoding

This branch combines main, high, or professional profile with film grain enabled or disabled. Main accepts 8-bit or 10-bit monochrome or 4:2:0. High also accepts 4:4:4. Professional retains the broad generated set. Every non-monochrome AV1 case must use equal luma and chroma depth.

### `decode.vp9`: VP9 decoding

VP9 profile 0 and profile 2 require 4:2:0; profile 1 and profile 3 require 4:2:2 or 4:4:4. Profiles 0 and 1 require 8-bit components. Profiles 2 and 3 require 10-bit or 12-bit components. All VP9 profiles require equal luma and chroma depth.

### `encode.h264`: H.264 encoding

The encode branch uses the same H.264 standard-profile compatibility masks without the decode picture-layout dimension. Supported profiles proceed through encode source, encode DPB, format, image-format, and session checks.

### `encode.h265`: H.265 encoding

The encode branch uses the same five H.265 profiles and the same CTS compatibility masks as decode. The host requests encode source and DPB usages and creates an encode session with the corresponding standard-header version.

### `encode.av1`: AV1 encoding

The encode branch tests main, high, and professional profiles without a film-grain parameter. It applies the same AV1 chroma and depth rules as decode, including equal depths for non-monochrome profiles.

The source implements these codec rules in one compatibility function ([`validateProfileCodec`](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L240-L392)).

## Shader Analysis

This test contains no shader source and submits no video coding commands. It validates host API query relationships and video-session creation; no representative shader walkthrough applies.

## Runtime Execution and Result Checking

- `checkSupport` requires `VK_KHR_video_queue`, the decode or encode queue extension, and the selected codec extension. VP9 device creation also requests VP9 decode support. The video device must provide synchronization2 support through the shared video-device helper ([support setup](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L127-L159), [extension checks](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L809-L848)).
- `iterate` calls `vkGetPhysicalDeviceVideoCapabilitiesKHR` with the generated profile and a correctly chained generic, operation-specific, and codec-specific capability structure. If the query succeeds for a profile that `validateProfileCodec` rejects, the case fails. A recognized profile-specific error marks the case unsupported; another error fails the query ([capability decision](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L746-L782)).
- For a supported profile, the test queries formats separately for decode DPB and output, or encode DPB and source. Decode also requests combined DPB and output usage when the capability allows coincident images ([usage selection](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L582-L609)).
- A zero format count fails. For every returned YCbCr format, the luma and chroma component depths must match the profile fields. The entry must include the requested usage. Decode entries must also agree with the capability flags for coincident and distinct DPB/output resources ([format checks](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L622-L701)).
- The test maps each requested video usage to its required `VkFormatFeatureFlagBits` and checks the feature in the reported tiling class with `vkGetPhysicalDeviceFormatProperties2` ([format-feature check](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L394-L434)).
- It derives image usage and creation flags for `vkGetPhysicalDeviceImageFormatProperties2`. Decode outputs add transfer-source and sampled usage; encode sources add transfer-destination usage. YCbCr source and output images also request mutable format and extended usage. A successful image-format query paired with missing flags in the video-format entry produces a capability warning ([image-format check](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L459-L580)).
- DRM modifier tiling is tested once per reported modifier. Unsupported modifiers are skipped individually, but at least one modifier must work when the video format advertises DRM modifier tiling.
- The test collects unique picture/source and DPB format pairs. For each pair, it creates and destroys a video session using the queried profile, queue family, maximum coded extent, DPB limits, active-reference limit, and codec standard-header version. Any creation error fails the case ([session check](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L166-L238), [format pairing](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L727-L743)).

Vulkan defines the same chain of obligations: supported profiles return capabilities, returned video formats include the requested usages, ordinary format features cover those usages, image-format queries accept matching parameters, and sessions use profile-compatible formats and limits ([capabilities and formats](../../../../vulkan-docs/src/chapters/videocoding.adoc#L766-L785), [cross-query requirements](../../../../vulkan-docs/src/chapters/videocoding.adoc#L1083-L1117), [session creation](../../../../vulkan-docs/src/chapters/videocoding.adoc#L1234-L1305)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `decode.h264` | H.264 profile or picture-layout compatibility handling; decode capability or DPB/output usage reporting; format, image-format, or decode-session inconsistency. |
| `decode.h265` | H.265 profile compatibility handling; decode capability or DPB/output usage reporting; format, image-format, or decode-session inconsistency. |
| `decode.av1` | AV1 profile or film-grain compatibility handling; decode capability or DPB/output usage reporting; format, image-format, or decode-session inconsistency. |
| `decode.vp9` | VP9 profile, chroma, or equal-depth compatibility handling; decode capability or DPB/output usage reporting; format, image-format, or decode-session inconsistency. |
| `encode.h264` | H.264 profile compatibility handling; encode capability or source/DPB usage reporting; format, image-format, or encode-session inconsistency. |
| `encode.h265` | H.265 profile compatibility handling; encode capability or source/DPB usage reporting; format, image-format, or encode-session inconsistency. |
| `encode.av1` | AV1 profile or equal-depth compatibility handling; encode capability or source/DPB usage reporting; format, image-format, or encode-session inconsistency. |

### Cause Analysis

#### H.264 profile or picture-layout compatibility handling; decode capability or DPB/output usage reporting; format, image-format, or decode-session inconsistency

**Possible failure symptoms:** An invalid H.264 profile succeeds, a supported layout has no formats, a returned format contradicts its depth or decode usage, the DPB/output flags conflict with decode capabilities, a related format or image-format query disagrees, or video-session creation fails.

**Possible implementation causes:** The implementation may map an H.264 standard profile or picture layout to the wrong supported set. It may also expose capability flags, format records, or session validation from different internal tables. The failing CTS message identifies which API relationship broke; a profile-specific unsupported error is a skip rather than this failure.

#### H.265 profile compatibility handling; decode capability or DPB/output usage reporting; format, image-format, or decode-session inconsistency

**Possible failure symptoms:** A disallowed H.265 chroma or depth combination succeeds, or a supported H.265 profile fails one of the decode capability, returned-format, image-format, or session checks.

**Possible implementation causes:** The codec-profile lookup may apply the wrong Main, Main 10, Main Still Picture, format-range, or SCC rule. If capability discovery succeeds first, inconsistent decode format metadata or session validation can produce the later symptom.

#### AV1 profile or film-grain compatibility handling; decode capability or DPB/output usage reporting; format, image-format, or decode-session inconsistency

**Possible failure symptoms:** The implementation accepts an invalid AV1 chroma or mixed-depth profile, mishandles a film-grain profile, or reports a supported profile whose decode format and session results do not agree.

**Possible implementation causes:** The AV1 profile key may omit the film-grain field, apply Main or High restrictions to the wrong standard profile, or accept unequal component depths for a non-monochrome profile. A failure after capability success can instead come from stale or inconsistent decode image capabilities.

#### VP9 profile, chroma, or equal-depth compatibility handling; decode capability or DPB/output usage reporting; format, image-format, or decode-session inconsistency

**Possible failure symptoms:** A VP9 profile accepts the wrong subsampling, depth range, or unequal component depths. Supported-profile failures can also report no formats, incompatible usages or bit depths, or a session-creation error.

**Possible implementation causes:** The implementation may confuse VP9 profiles 0 and 2 with profiles 1 and 3, or omit the 8-bit versus 10/12-bit split. Later failures point to disagreement between VP9 capability discovery and shared video image or session handling.

#### H.264 profile compatibility handling; encode capability or source/DPB usage reporting; format, image-format, or encode-session inconsistency

**Possible failure symptoms:** An invalid H.264 encode profile succeeds, or a supported profile returns inconsistent encode source, DPB, format-feature, image-format, or session results.

**Possible implementation causes:** The encode profile table may apply the wrong H.264 chroma and depth restrictions. The implementation may also advertise encode image usage that its ordinary image queries or video-session validation cannot support.

#### H.265 profile compatibility handling; encode capability or source/DPB usage reporting; format, image-format, or encode-session inconsistency

**Possible failure symptoms:** A disallowed H.265 encode combination succeeds, a supported profile yields no source or DPB format, returned metadata conflicts with another format query, or encode-session creation fails.

**Possible implementation causes:** The H.265 encode profile lookup may select the wrong format restrictions. Another possibility is that encode capability, image-format, and session code paths use inconsistent format or limit data.

#### AV1 profile or equal-depth compatibility handling; encode capability or source/DPB usage reporting; format, image-format, or encode-session inconsistency

**Possible failure symptoms:** The implementation accepts an invalid AV1 encode profile, especially a non-monochrome mixed-depth pair, or later contradicts its successful capability result through format or session behavior.

**Possible implementation causes:** The AV1 encode profile key may not enforce the selected standard profile's chroma and depth rules. If profile validation is correct, the failure instead points to inconsistent encode source/DPB reporting, image support, or session creation.

## Case Pruning

### Requirement-based pruning

- A case requires `VK_KHR_video_queue`, the operation's decode or encode queue extension, and its codec extension. Missing functionality makes the case unsupported before execution.
- `VK_KHR_video_maintenance1` is required when the physical device exposes it, and the shared video-device setup requires synchronization2 support.
- The capability query can return `VK_ERROR_VIDEO_PICTURE_LAYOUT_NOT_SUPPORTED_KHR`, `VK_ERROR_VIDEO_PROFILE_FORMAT_NOT_SUPPORTED_KHR`, `VK_ERROR_VIDEO_PROFILE_OPERATION_NOT_SUPPORTED_KHR`, or `VK_ERROR_VIDEO_PROFILE_CODEC_NOT_SUPPORTED_KHR`. The test treats these defined outcomes as unsupported profiles, not conformance failures.
- DRM modifier validation ignores individual modifiers that return `VK_ERROR_FORMAT_NOT_SUPPORTED`, but fails if none of the advertised modifiers works.

### Design-based pruning

- The generator removes monochrome cases whose luma and chroma fields differ. Chroma depth carries no separate picture-content meaning for monochrome, so those pairs would duplicate the luma-depth cases.
- Non-monochrome mixed-depth cases stay in the matrix. They are deliberate negative cases for codec rules that require equal depths.
- VP9 has no encode branch in this source, H.264 picture layout appears only under decode, and film grain appears only under AV1 decode. These are boundaries of the generated test design.

## Key Takeaways

- The generated leaves test complete profile descriptions, not codec names alone. Chroma and the two component depths remain independent path dimensions.
- Invalid generated combinations are useful negative cases. The capability query must reject them through a profile-specific error rather than report support.
- Capability success starts a chain of cross-checks through video formats, ordinary format features, image-format properties, and video-session creation.
- The test creates no images and submits no coding work. It tests whether the implementation's discovery and creation interfaces describe one coherent set of video capabilities.
- Failure details depend on the operation and codec branch; see `## Failure Meaning` for the mapped causes.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Parameter storage and test instance | [test structures and instance declaration](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L38-L125) | Shows the profile, capability chains, and validation stages held by each case. |
| Codec compatibility rules | [`validateProfileCodec`](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L240-L392) | Defines which codec, chroma, and depth combinations the test accepts. |
| Format and image-format checks | [`validateVideoFormatsWithProfile`](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L582-L744) | Cross-validates usages, component depths, decode capability flags, format features, image-format support, and format pairs. |
| Capability decision | [`iterate`](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L746-L783) | Distinguishes invalid-profile acceptance, supported execution, unsupported profiles, and unexpected query errors. |
| Generated names and registration | [`getTestName` and `createVideoProfilesValidationTests`](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L1000-L1324) | Defines exact path tokens, dimensions, omission rules, and hierarchy. |
| Vulkan video profiles | [Video Profiles](../../../../vulkan-docs/src/chapters/videocoding.adoc#L321-L390) | Defines profile fields, complete profile chains, and profile-specific error meanings. |
| Vulkan video formats | [Video Format Capabilities](../../../../vulkan-docs/src/chapters/videocoding.adoc#L939-L1211) | Defines requested usages, returned properties, and cross-query requirements. |
| Vulkan video sessions | [Creating a Video Session](../../../../vulkan-docs/src/chapters/videocoding.adoc#L1234-L1326) | Defines profile-bound session creation and capability-derived limits. |
| Default mustpass range | [`video.profiles` paths](../../../mustpass/main/vk-default/video.txt#L7859-L9028) | Confirms the exact generated profile paths included in the default run. |
