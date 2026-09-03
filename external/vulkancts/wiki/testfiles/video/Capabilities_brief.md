# Understanding Brief: vktVideoCapabilitiesTests

## One-Sentence Test Purpose

This test checks whether a Vulkan implementation reports internally consistent video queue, profile capability, and image-format support for the codecs and usages registered in the `video` test category.

## Background Knowledge

### Video profiles describe one codec operation and format shape

A `VkVideoProfileInfoKHR` combines a codec operation with chroma subsampling, luma bit depth, and chroma bit depth. Its `pNext` chain carries codec-specific profile data, such as `VkVideoDecodeH264ProfileInfoKHR` or `VkVideoEncodeAV1ProfileInfoKHR`. The Vulkan specification uses the same profile description for capability queries, video-format queries, and later image creation, so a format result only has meaning for the exact profile and image usage used to obtain it. See [`VkVideoProfileInfoKHR`](../../../../vulkan-docs/src/chapters/videocoding.adoc#L323-L352).

A video profile uses one subsampling bit and one luma bit-depth bit. For non-monochrome profiles, the chroma bit depth also has one bit. The four subsampling choices in this test mean monochrome, 4:2:0, 4:2:2, and 4:4:4; the bit-depth choices are 8, 10, and 12 bits. See [`VkVideoChromaSubsamplingFlagBitsKHR` and `VkVideoComponentBitDepthFlagBitsKHR`](../../../../vulkan-docs/src/chapters/videocoding.adoc#L486-L537).

Why it matters here:
- The format matrix pairs the requested `VkFormat` with the profile's subsampling and bit depth before asking Vulkan whether that combination is supported.
- A returned format is useful only if its usage flags, tiling, and image-creation parameters also work with the same profile list.

### Capability structures extend one another through `pNext`

Capability queries return a general `VkVideoCapabilitiesKHR` structure plus a decode or encode structure and a codec-specific structure. For example, an H.264 encode query uses `VkVideoCapabilitiesKHR` → `VkVideoEncodeCapabilitiesKHR` → `VkVideoEncodeH264CapabilitiesKHR`, with an optional `VkVideoEncodeIntraRefreshCapabilitiesKHR` at the end. The query fills every structure in the chain. Vulkan requires the chain to match the operation: decode profiles need the generic decode structure and the matching codec structure; encode profiles need the corresponding encode structures. See [`vkGetPhysicalDeviceVideoCapabilitiesKHR`](../../../../vulkan-docs/src/chapters/videocoding.adoc#L766-L859).

This test queries twice after filling one result chain with zero bytes and the other with `0xFF`. It then compares returned fields. The two-call comparison checks that the implementation writes the advertised result fields rather than leaving caller initialization visible.

## One Concrete Example

Consider the generated case represented by the registered name `decode_av1_g10x6_b10x6_r10x6_3plane_420_unorm_3pack16_decode_dst_420_10bit`. The case supplies an AV1 decode profile, `VK_VIDEO_CHROMA_SUBSAMPLING_420_BIT_KHR`, equal 10-bit luma and chroma depths, the listed three-plane 4:2:0 format, and `VK_IMAGE_USAGE_VIDEO_DECODE_DST_BIT_KHR`.

The format test first asks `vkGetPhysicalDeviceVideoFormatPropertiesKHR` for formats supporting the profile and usage. It looks for the requested `VkFormat` and requires the returned `imageUsageFlags` to contain the requested usage. It then derives `VkPhysicalDeviceImageFormatInfo2` from the returned format properties, keeps the same profile list in `pNext`, and calls `vkGetPhysicalDeviceImageFormatProperties2`. Finally, it checks the matching linear or optimal format feature bit. This is a conceptual case description based on the generator and the query sequence, not an additional registered leaf.

## End-to-End Test Flow

1. `[host]` The CTS creates the `video` test category's `capabilities` and `formats` test families. The capability family registers 25 leaves. The formats family generates cases from seven codec operations, four image usages, the source format vector, four subsampling values, and three component bit depths.
2. `[host]` For `queue_support_query`, the test queries the queue-family count, attaches one `VkQueueFamilyVideoPropertiesKHR` to each `VkQueueFamilyProperties2`, and queries the properties again.
3. `[host]` For codec capability leaves, the test builds a `VkVideoProfileInfoKHR` and the matching codec-specific profile structure. It builds the required general, decode or encode, codec-specific, and, for encode cases, intra-refresh capability chain.
4. `[host]` The test calls `vkGetPhysicalDeviceVideoCapabilitiesKHR` twice. It initializes one chain to zero and one to `0xFF`, then compares selected returned fields, extension metadata, allowed flags, required nonzero values, and codec-specific relationships.
5. `[host]` For intra-refresh leaves, the test calls the same capability query once and checks reference-picture support and the intra-refresh mode rules against the codec's maximum slice count, slice-segment count, or tile count.
6. `[host]` For each surviving format case, the test requires the base video queue extension and the codec extension, queries the count and then the entries from `vkGetPhysicalDeviceVideoFormatPropertiesKHR`, and handles the specification's profile and usage error codes.
7. `[host]` The format test finds the requested format and usage in the returned entries. For DRM modifier tiling it enumerates modifiers and tests each one with `vkGetPhysicalDeviceImageFormatProperties2`; for linear and optimal tiling it checks the corresponding format feature bit from `vkGetPhysicalDeviceFormatProperties2`.
8. `[host]` The test returns pass when the relevant consistency checks succeed. Unsupported requirements are reported through CTS support handling or `NotSupportedError`; malformed successful query results and inconsistent cross-query results return a failure.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The generator creates no shader, SPIR-V, draw, dispatch, or video bitstream artifact. It creates `formats::TestParams` values and uses them to build a `VkVideoCoreProfile`, a `VkVideoProfileListInfoKHR`, and the query structures passed to Vulkan.

The capability family creates arrays of two result chains for the repeatability check. The format family creates a single query-result vector after its count query, then derives image-format query structures from each returned `VkVideoFormatPropertiesKHR` entry.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `VkQueueFamilyProperties2` plus `VkQueueFamilyVideoPropertiesKHR` | yes | no | no | yes, as query output | Reports queue count, queue flags, and codec operations for each queue family. |
| `VkVideoProfileInfoKHR` and codec-specific profile structures | yes | no | no | no | Defines the codec, profile, subsampling, and component depths used by the queries. |
| `VkVideoCapabilitiesKHR` and chained capability structures | yes | no | no | yes, as query output | Carries general, decode or encode, codec-specific, and intra-refresh capabilities. |
| `VkVideoFormatPropertiesKHR` vector | yes | no | no | yes, as query output | Lists format, component mapping, image type, tiling, creation flags, and supported usages. |
| `VkPhysicalDeviceFormatProperties2` and `VkImageFormatProperties2` | yes | no | no | yes, as query output | Cross-checks format feature bits and image creation support for each returned video format. |

## What Is Checked

- Queue-family enumeration reports a nonempty set and returns the same count on the data query. A queue with `VK_QUEUE_VIDEO_ENCODE_BIT_KHR` or `VK_QUEUE_VIDEO_DECODE_BIT_KHR` must expose compatible codec-operation bits and a nonzero queue count. At least one encode or decode path must remain available after extension support gates.
- General capability results match across the two initialized result chains. The test checks the structure type, flags, buffer alignment values, picture access granularity, coded extents, DPB limits, active reference-picture limit, and `stdHeaderVersion`.
- General and codec-specific flag masks contain only currently recognized bits. Required alignment, granularity, extent, DPB, reference, rate-control, quality-level, block-size, and superblock values meet the source checks.
- Decode capability flags are limited to the DPB/output coincidence choices. Encode capability results include the checked rate-control fields, layer and quality counts, and, when `VK_KHR_video_maintenance2` is available, the disabled rate-control mode.
- Codec-specific results match across the repeated query. H.264 and H.265 require a supported reference-frame path for their intra-refresh leaves; AV1 requires a supported non-intra prediction reference path. Codec-specific intra-refresh relationships and limits must hold.
- A format query succeeds with at least one result. The returned count is nonzero and agrees with the allocated result vector. Every returned format writes a value other than `VK_FORMAT_MAX_ENUM`; opaque DPB results may use `VK_FORMAT_UNDEFINED` only as the sole result.
- The generated format test finds the requested format with the requested video usage. Image-format properties succeed with the returned parameters and the same profile list, except that an individual DRM modifier may be rejected with `VK_ERROR_FORMAT_NOT_SUPPORTED`. The matching linear or optimal video format feature bit must be present.

## Behavior Parameter Identification

> **Behavior parameter:** test family
>
> **Candidate values:** `capabilities`, `formats`

The test family is the primary axis because it selects two different Vulkan contracts. `capabilities` validates queue and profile capability reports. `formats` validates the relationship between profile/usage format enumeration and ordinary image-format and format-feature queries. Codec, usage, format, subsampling, and bit depth vary cases inside those families but do not change the family-level mechanism.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `capabilities` | Queue-family video properties, profile capability `pNext` chain population, capability field or flag reporting, extension metadata, codec-specific limits, or intra-refresh capability relationships are inconsistent with Vulkan requirements. |
| `formats` | The implementation reports a video format that does not support the requested usage, profile, image creation parameters, DRM modifier, or corresponding video format feature bit; or it returns an invalid query result or error code. |

## Important Variations and Special Cases

- The queue leaf is separate from profile capability leaves. It checks the relationship between `VkQueueFlags` and `VkQueueFamilyVideoPropertiesKHR::videoCodecOperations`, then masks the result with support for `VK_KHR_video_encode_queue` and `VK_KHR_video_decode_queue`.
- Decode capability cases use H.264, H.265, AV1, or VP9 profile structures and compare the generic decode capability flags. Encode capability cases use H.264, H.265, or AV1 structures and also validate generic encode fields. Intra-refresh cases add `VkVideoEncodeIntraRefreshCapabilitiesKHR` and apply codec-specific reference and partition limits.
- The format generator includes four usages: `VK_IMAGE_USAGE_VIDEO_DECODE_DST_BIT_KHR`, `VK_IMAGE_USAGE_VIDEO_DECODE_DPB_BIT_KHR`, `VK_IMAGE_USAGE_VIDEO_ENCODE_SRC_BIT_KHR`, and `VK_IMAGE_USAGE_VIDEO_ENCODE_DPB_BIT_KHR`. It includes monochrome, 4:2:0, 4:2:2, and 4:4:4 profiles with equal 8, 10, or 12-bit component depths.
- Non-YCbCr formats are retained only for encode-source cases with monochrome subsampling. YCbCr formats must have a component bit depth equal to the selected profile depth and a subsampling layout compatible with the selected 4:2:0, 4:2:2, or 4:4:4 profile. These are design reductions in the generated matrix.
- The format helper maps each video image usage to its required format feature: decode output, decode DPB, encode input, or encode DPB. DRM modifier entries require at least one compatible modifier; an unsupported individual modifier is skipped, while a returned entry with no compatible modifier fails.
- `VK_ERROR_VIDEO_PROFILE_OPERATION_NOT_SUPPORTED_KHR`, `VK_ERROR_VIDEO_PROFILE_FORMAT_NOT_SUPPORTED_KHR`, `VK_ERROR_VIDEO_PROFILE_CODEC_NOT_SUPPORTED_KHR`, `VK_ERROR_VIDEO_PICTURE_LAYOUT_NOT_SUPPORTED_KHR`, and `VK_ERROR_IMAGE_USAGE_NOT_SUPPORTED_KHR` identify unsupported profile or usage combinations in the format helper and become `NotSupportedError`. Out-of-memory errors fail the case. `VK_INCOMPLETE` and other unexpected results fail as invalid query behavior.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Queue-family query | [`VideoQueueQueryTestInstance::iterate`](../../../modules/vulkan/video/vktVideoCapabilitiesTests.cpp#L108-L180) | Attaches `VkQueueFamilyVideoPropertiesKHR`, checks queue flags and codec operations, and applies encode/decode support gates. |
| Profile format query | [`VideoFormatPropertiesQueryTestInstance::iterate`](../../../modules/vulkan/video/vktVideoCapabilitiesTests.cpp#L340-L456) | Builds the profile and usage query, checks returned formats, and handles opaque DPB results. |
| Capability chain and repeated queries | [`VideoCapabilitiesQueryH264DecodeTestInstance::iterate`](../../../modules/vulkan/video/vktVideoCapabilitiesTests.cpp#L652-L713) | Shows the two initialized result chains and generic/decode/codec validation sequence. |
| Generic capability validation | [`validateVideoCapabilities`](../../../modules/vulkan/video/vktVideoCapabilitiesTests.cpp#L508-L560) | Defines field equality, allowed flags, nonzero values, extent, DPB, and reference checks. |
| Encode and intra-refresh validation | [`validateVideoEncodeCapabilities`](../../../modules/vulkan/video/vktVideoCapabilitiesTests.cpp#L577-L611) and [`validateIntraRefreshCapabilities`](../../../modules/vulkan/video/vktVideoCapabilitiesTests.cpp#L1434-L1483) | Defines encode field checks, maintenance2 behavior, and intra-refresh constraints. |
| Capability support gates | [`VideoCapabilitiesQueryTestCase::checkSupport`](../../../modules/vulkan/video/vktVideoCapabilitiesTests.cpp#L1750-L1829) | Maps each leaf to `VK_KHR_video_queue`, codec, maintenance2, and intra-refresh requirements. |
| Format matrix and pruning | [`createVideoFormatsTests`](../../../modules/vulkan/video/vktVideoCapabilitiesTests.cpp#L2315-L2486) | Registers codec, format, usage, subsampling, and bit-depth combinations and prunes incompatible cases. |
| Format cross-query validation | [`formats::test`](../../../modules/vulkan/video/vktVideoCapabilitiesTests.cpp#L2200-L2291) | Compares video-format properties with DRM, image-format, and format-feature queries. |
| Queue-family semantics | [`VkQueueFamilyVideoPropertiesKHR`](../../../../vulkan-docs/src/chapters/devsandqueues.adoc#L1649-L1668) | Defines what `videoCodecOperations` reports for a queue family. |
| Video profile and result errors | [`VkVideoProfileInfoKHR`](../../../../vulkan-docs/src/chapters/videocoding.adoc#L344-L379) | Defines profile dimensions and the specific unsupported-profile error meanings. |
| Capability query contract | [`Video Coding Capabilities`](../../../../vulkan-docs/src/chapters/videocoding.adoc#L766-L908) | Defines the capability query and required decode/encode `pNext` structures. |
| Format query contract | [`Video Format Capabilities`](../../../../vulkan-docs/src/chapters/videocoding.adoc#L939-L1117) | Defines count/data queries, usage inclusion, profile lists, and cross-query requirements. |
| Video format feature mapping | [`Format Feature Dependent Usage Flags`](../../../../vulkan-docs/src/chapters/formats.adoc#L4117-L4165) | Defines the format feature bit required for each video image usage. |

## Questions / Risk Points for User Audit

- Does the page make the `capabilities` versus `formats` family split clear enough for a generated source file that also contains the matrix generator?
- Is the two-call zero-versus-`0xFF` capability check explained as a result-population and repeatability check rather than as a device execution test?
- Are unsupported profile and usage results clearly separated from malformed successful results and from out-of-memory failures?
- Should the final page name more codec-specific capability fields, or is the shared validation pattern enough for this page's scope?
- Is the distinction between design pruning and device support pruning clear in the format matrix discussion?

## Conversion Notes for Final Wiki Page

- Use `video.capabilities` with its 25 exact children and `video.formats` as a bare root in the registration tree. Keep the 1701 format leaves as compact count and dimension statements rather than expanding them into the hierarchy.
- Distill the profile and `pNext` explanations into short prerequisite bullets. Keep the conceptual AV1 format case only as a concise example of the generated name and query sequence.
- Use `test family` as the primary behavior axis with `capabilities` and `formats` values. Copy the `### Failure Cause Mapping` table above directly into the final page.
- Write `### Cause Analysis` fresh. Explain capability-query failures through returned fields, masks, chains, and relationships; explain format failures through usage inclusion, image-format properties, modifiers, and feature mapping.
- The source contains no shader or shader code. State that under `## Shader Analysis` and do not invent a walkthrough or SPIR-V artifact.
- Preserve exact source and mustpass identifiers, including `dEQP-VK.video.capabilities.*`, `dEQP-VK.video.formats.*`, and the Vulkan structure and enum names.
