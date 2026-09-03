# Understanding Brief: vktVideoProfilesValidationTests

## One-Sentence Test Purpose

This test checks whether a Vulkan implementation rejects invalid video profile combinations and keeps reported capabilities, image formats, image properties, and video-session creation consistent for valid profiles.

## Background Knowledge

### A video profile combines codec operation and picture format

`VkVideoProfileInfoKHR` names a decode or encode operation and carries three format dimensions: chroma subsampling, luma bit depth, and chroma bit depth. The codec-specific structure in `pNext` adds the standard profile and, for some codecs, extra choices such as H.264 picture layout or AV1 film-grain support. Vulkan uses the complete structure chain for capability, format, image, and session queries, so changing one field changes the profile being queried.

The chroma choices describe how often the two chroma components are sampled relative to luma: monochrome, 4:2:0, 4:2:2, or 4:4:4. Luma and chroma bit depth are separate fields. A non-monochrome profile can therefore name different component depths, although this test treats unequal depths as invalid for AV1 and VP9. Vulkan's valid usage rules require a single bit in luma depth and in non-monochrome chroma depth; the test's generator also supplies one value per field.

Why it matters here:
- Codec profile rules restrict which chroma and depth dimensions are legal.
- The same complete profile must produce compatible capability and image-format answers.

### A format query is a compatibility contract

`vkGetPhysicalDeviceVideoCapabilitiesKHR` answers whether a profile is supported and returns limits and capability flags. `vkGetPhysicalDeviceVideoFormatPropertiesKHR` then enumerates image formats for a requested video usage and profile list. Each returned format describes its Vulkan format, image type, tiling, supported image usages, and creation flags. Vulkan requires those entries to agree with ordinary format properties and with `vkGetPhysicalDeviceImageFormatProperties2` queried using the reported values.

Why it matters here:
- A successful profile query does not by itself prove that an image can be created for decode or encode use.
- A session is the final cross-check because it uses the profile, capability limits, picture format, DPB format, queue family, and codec standard-header version together.

## One Concrete Example

Consider the registered decode case `video.profiles.decode.av1.main_without_filmgrain_420_luma_8bit_chroma_8bit`. The generator creates an AV1 decode profile with `STD_VIDEO_AV1_PROFILE_MAIN`, film grain disabled, 4:2:0 chroma, and 8-bit luma and chroma. The test first asks for capabilities for that exact profile. If the query succeeds, it requests video formats for decode output and decode DPB usage, checks every returned format against the profile's `(8, 8)` depth pair and requested usage, cross-checks tiling features and image creation properties, and tries every unique output-format and DPB-format pair in a video session.

For contrast, `video.profiles.decode.av1.main_without_filmgrain_420_luma_8bit_chroma_10bit` keeps the codec and subsampling but changes only chroma depth. The implementation's AV1 compatibility check rejects unequal luma and chroma depth for non-monochrome profiles. A successful capability query for that case is a CTS failure because the implementation accepted a profile that the test classifies as invalid.

## End-to-End Test Flow

```text
[host] generate a codec operation, codec-specific profile, chroma mode, luma depth, and chroma depth
[host] build VkVideoProfileInfoKHR and its codec-specific pNext chain
[host] require the queue and codec extensions needed by the operation
[host] query vkGetPhysicalDeviceVideoCapabilitiesKHR for the profile
[host] compare the query result with the CTS codec-compatibility rules
[host] query video format properties for each required decode or encode image usage
[host] check returned component depths, usages, decode DPB/output capability semantics, and format features
[host] query image-format properties with the reported format, type, tiling, usages, creation flags, and profile list
[host] form unique image-format and DPB-format pairs
[host] create and destroy a video session for each pair using the returned extent, DPB, reference, and standard-header limits
[host] pass only when every required query and session creation satisfies the cross-checks
```

An implementation may return a recognized `VK_ERROR_VIDEO_PROFILE_*_NOT_SUPPORTED_KHR` result for an unsupported profile. The test treats that as a support skip. It fails when a query returns an unexpected error, when a query succeeds for a profile rejected by the test's codec rules, or when a successful result contradicts another Vulkan query.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The test generates parameter objects, not shaders. `setProfiles` fills the operation, chroma, luma depth, and chroma depth fields. Codec-specific profile structures are attached to `VkVideoProfileInfoKHR`, capability structures are attached to `VkVideoCapabilitiesKHR`, and a one-profile `VkVideoProfileListInfoKHR` is used for format and image-format queries. The test name generator serializes the codec profile, decode-only options, chroma mode, and both component depths into the registered identifier.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `VkVideoProfileInfoKHR` and codec-specific `pNext` structure | yes | no | no | no | Describes the exact profile passed to all capability and resource queries. |
| `VkVideoCapabilitiesKHR` and decode or encode capability structure | returned by query | no | no | yes | Supplies capability flags and limits used for format and session checks. |
| `VkVideoFormatPropertiesKHR` entries | returned by query | no | no | yes | Describe candidate image formats and their usage, tiling, type, and create flags. |
| `VkImageFormatProperties2` result | returned by query | no | no | yes | Confirms that the reported image parameters are supported by image creation rules. |
| `VkVideoSessionKHR` | yes, then destroyed | yes, as a video object | no video commands run | no | Confirms that the profile, formats, queue family, and returned limits form a creatable session. |

The test does not allocate picture images, bind DPB resources, submit decode or encode work, or inspect coded output. Its observable result comes from Vulkan query results and session creation.

## What Is Checked

- `validateProfileCodec` derives the allowed chroma and component-depth sets for each codec profile. AV1 non-monochrome and all VP9 profiles also require equal luma and chroma depth.
- A successful capability query for a profile that fails those rules is an error. A recognized unsupported-profile result becomes `NotSupportedError`, while an unexpected query error fails the case.
- Each returned YCbCr format must report the same luma and chroma depth pair as the profile. Each returned entry must include the requested image usage.
- Decode format entries must agree with the capability flags that describe coincident or distinct DPB and output images.
- `vkGetPhysicalDeviceFormatProperties2` must expose the required video format feature for the entry's tiling and usage.
- `vkGetPhysicalDeviceImageFormatProperties2` must succeed with the reported format, image type, tiling, usage, create flags, profile list, and each compatible DRM modifier. A mismatch in reported usage or create flags produces a capability warning.
- The test must create a session for every unique pair of an encode source or decode output format and an encode or decode DPB format.

## Behavior Parameter Identification

> **Behavior parameter:** codec operation and codec-specific profile branch
>
> **Candidate values:** `decode.h264`, `decode.h265`, `decode.av1`, `decode.vp9`, `encode.h264`, `encode.h265`, `encode.av1`

This is the primary behavior axis because it selects the codec-specific compatibility rules, the profile `pNext` structure, the queue direction, the capability structure, and the standard-header version used for session creation. Chroma and the independent luma/chroma depth fields form a secondary format axis exercised inside every branch.

## What Failure Means

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

The secondary format axis adds the same cross-cutting causes to each operation: an unsupported chroma or depth combination may be incorrectly accepted, or a supported profile may return a format whose component depths, usages, ordinary format features, image creation properties, or session parameters do not agree.

## Important Variations and Special Cases

- H.264 decode adds `progressive`, `interlaced_interleaved_lines`, and `interlaced_separate_planes` to the codec-profile dimension. H.264 encode has no picture-layout suffix.
- AV1 decode adds `with_filmgrain` and `without_filmgrain`; AV1 encode has no film-grain dimension.
- H.264 baseline and main are restricted by the test to 8-bit 4:2:0. H.264 high is restricted to 8-bit monochrome or 4:2:0. H.264 high 4:4:4 predictive keeps the generator's broader format matrix.
- H.265 main and main still picture are restricted to 8-bit 4:2:0. H.265 main 10 permits 8-bit or 10-bit 4:2:0. The format-range and SCC extension branches keep the broader generated matrix.
- AV1 main permits 8-bit or 10-bit monochrome or 4:2:0. AV1 high permits those depths with monochrome, 4:2:0, or 4:4:4. AV1 professional keeps the broader matrix, but non-monochrome unequal depths still fail the common AV1 rule.
- VP9 profiles 0 and 2 use 4:2:0; profiles 1 and 3 use 4:2:2 or 4:4:4. Profiles 0 and 1 use 8-bit; profiles 2 and 3 use 10-bit or 12-bit. Every VP9 case requires equal luma and chroma depth.
- For monochrome generation, the test omits unequal luma/chroma pairs even though the test name still carries both fields. For non-monochrome generation, all nine 8/10/12 by 8/10/12 pairs are generated and then checked against codec rules.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Parameter generation and registration | [createVideoProfilesValidationTests](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L1086-L1324) | Builds the operation, codec profile, chroma, and two independent depth loops and registers each generated case. |
| Test naming | [getTestName](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L868-L1082) | Defines the exact profile, option, chroma, luma, and chroma-depth path tokens. |
| Codec compatibility rules | [validateProfileCodec](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L240-L392) | Determines which generated profiles should be rejected. |
| Capability and format validation | [iterate and validateVideoFormatsWithProfile](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L582-L782) | Performs capability, video-format, format-feature, image-format, and session checks. |
| Vulkan profile semantics | [Video Profiles](../../../../vulkan-docs/src/chapters/videocoding.adoc#L321-L390) | Defines profile dimensions, codec-specific chains, and profile error meanings. |
| Vulkan format and session contract | [Video Format Capabilities](../../../../vulkan-docs/src/chapters/videocoding.adoc#L939-L1120) and [Creating a Video Session](../../../../vulkan-docs/src/chapters/videocoding.adoc#L1234-L1326) | Defines returned format properties and the required image and session relationships. |
| Exact mustpass paths | [video.txt profiles entries](../../../mustpass/main/vk-default/video.txt#L7859-L9028) | Records the generated decode and encode paths consumed by the default mustpass set. |

## Questions / Risk Points for User Audit

- Is the distinction between an invalid generated profile and an unsupported device profile clear?
- Is the reason for keeping separate luma and chroma depth fields clear enough?
- Does the capability, format, image-format, and session sequence show why each query is needed?
- Should H.264 picture layout and AV1 film grain receive more or less emphasis in the final page?
- Are capability warnings distinguished from hard test failures clearly enough?

## Conversion Notes for Final Wiki Page

- Keep `VkVideoProfileInfoKHR` and the profile-to-format compatibility contract as the two Background Knowledge prerequisites.
- Use the AV1 `main_without_filmgrain_420_luma_8bit_chroma_8bit` path as the concrete registered example, with the unequal-depth AV1 path as the short contrast.
- Use one registration tree rooted at `video.profiles`, expanded to `decode` and `encode`; describe codec branches and generated leaves in the parameter sections rather than expanding the tree into thousands of leaves.
- Carry the behavior-axis conclusion into `## Behavior Parameters` and copy the `### Failure Cause Mapping` table directly into `## Failure Meaning`.
- Write `### Cause Analysis` fresh. Organize it around invalid profile acceptance, format-query contradictions, image-format or format-feature contradictions, and session-creation contradictions.
- Keep the page's shader section factual: the source generates profile and query data, not shader code, so no shader walkthrough is needed. The current structure validator requires a reviewed no-walkthrough exception for this page; the assigned-file boundary prevents changing that registry.
