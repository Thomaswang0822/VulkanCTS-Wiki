## Overview

**Core question:** Do the video capability and format queries report support that is internally consistent with queue properties, video profiles, image usage, and ordinary Vulkan image queries?

- This page covers `vktVideoCapabilitiesTests.cpp`, which registers the `video.capabilities` and `video.formats` test families under the `video` test category.
- `video.capabilities` contains 25 mustpass leaves for queue support, codec capability queries, video-format support queries, and encode intra-refresh capability queries.
- `video.formats` contains 1701 generated mustpass leaves. Each leaf combines a codec operation, `VkFormat`, video image usage, chroma subsampling, and component bit depth.
- The tests query physical-device properties. They do not create a video session, submit video commands, run a shader, or compare decoded or encoded pictures.
- The page explains the query structures, generated dimensions, support gates, pruning rules, cross-query checks, and what each failure indicates.

## Background Knowledge

- A `VkVideoProfileInfoKHR` identifies one codec operation together with its chroma subsampling and luma and chroma component bit depths. Codec-specific profile structures hang from its `pNext` chain. Vulkan uses this profile description for capability and format queries, so a result applies to the exact profile and usage used by the query. See [`VkVideoProfileInfoKHR`](../../../../vulkan-docs/src/chapters/videocoding.adoc#L323-L352).
- A capability result is also a `pNext` chain. `VkVideoCapabilitiesKHR` carries general limits, a decode or encode structure carries operation-level fields, and a codec-specific structure carries codec fields. The returned chain must match the operation named by the profile. See [`vkGetPhysicalDeviceVideoCapabilitiesKHR`](../../../../vulkan-docs/src/chapters/videocoding.adoc#L766-L859).
- `VkQueueFamilyVideoPropertiesKHR::videoCodecOperations` reports the codec operations supported by a queue family. The structure is returned by chaining it to `VkQueueFamilyProperties2` in `vkGetPhysicalDeviceQueueFamilyProperties2`. See [`VkQueueFamilyVideoPropertiesKHR`](../../../../vulkan-docs/src/chapters/devsandqueues.adoc#L1649-L1668).

## Registration Hierarchy

```text
video.capabilities
├── av1_decode_capabilities_query
├── av1_decode_dpb_video_format_support_query
├── av1_decode_dst_video_format_support_query
├── av1_encode_capabilities_query
├── av1_encode_dpb_video_format_support_query
├── av1_encode_intra_refresh_capabilities_query
├── av1_encode_src_video_format_support_query
├── h264_decode_capabilities_query
├── h264_decode_dpb_video_format_support_query
├── h264_decode_dst_video_format_support_query
├── h264_encode_capabilities_query
├── h264_encode_dpb_video_format_support_query
├── h264_encode_intra_refresh_capabilities_query
├── h264_encode_src_video_format_support_query
├── h265_decode_capabilities_query
├── h265_decode_dpb_video_format_support_query
├── h265_decode_dst_video_format_support_query
├── h265_encode_capabilities_query
├── h265_encode_dpb_video_format_support_query
├── h265_encode_intra_refresh_capabilities_query
├── h265_encode_src_video_format_support_query
├── queue_support_query
├── vp9_decode_capabilities_query
├── vp9_decode_dpb_video_format_support_query
└── vp9_decode_dst_video_format_support_query

video.formats
```

The `capabilities` and `formats` families are both implemented by this source file and owned by this page. The `capabilities` tree lists its 25 exact registered leaves. The `formats` tree is a bare root because its 1701 generated leaves are flat single components that each combine a codec operation, format, usage, subsampling, and bit depth; the matrix is described in the parameter sections rather than expanded in the tree.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test family | `capabilities`, `formats` | Selects the queue/profile capability checks or the profile-to-image-format consistency checks. | [`createVideoCapabilitiesTests` and `createVideoFormatsTests`](../../../modules/vulkan/video/vktVideoCapabilitiesTests.cpp#L2297-L2486) |
| Capability leaf | 25 exact names, including `queue_support_query`, codec capability leaves, codec video-format support leaves, and encode intra-refresh leaves | Selects the query structure chain and validation routine. | [`getTestName`](../../../modules/vulkan/video/vktVideoCapabilitiesTests.cpp#L1891-L1948) |
| Codec operation | `DECODE_H264`, `DECODE_H265`, `DECODE_AV1`, `DECODE_VP9`, `ENCODE_H264`, `ENCODE_H265`, `ENCODE_AV1` | Selects the codec profile structure and the required codec extension. | [`codecs` vector and profile selection](../../../modules/vulkan/video/vktVideoCapabilitiesTests.cpp#L2319-L2323), [`checkSupport`](../../../modules/vulkan/video/vktVideoCapabilitiesTests.cpp#L2132-L2168) |
| Image usage | `VIDEO_DECODE_DST`, `VIDEO_DECODE_DPB`, `VIDEO_ENCODE_SRC`, `VIDEO_ENCODE_DPB` | Selects the image role requested from `vkGetPhysicalDeviceVideoFormatPropertiesKHR`. | [`usageFlags` vector and usage naming](../../../modules/vulkan/video/vktVideoCapabilitiesTests.cpp#L2017-L2036) and [`createVideoFormatsTests`](../../../modules/vulkan/video/vktVideoCapabilitiesTests.cpp#L2390-L2392) |
| Format | 62 formats in the source vector, with surviving leaves determined by pruning | Selects the format to find in the returned video format properties. | [`formats` vector](../../../modules/vulkan/video/vktVideoCapabilitiesTests.cpp#L2325-L2388) |
| Chroma subsampling | `MONOCHROME`, `420`, `422`, `444` | Selects the profile's chroma sampling relationship and must match the YCbCr format layout when applicable. | [`subsamplingFlags`](../../../modules/vulkan/video/vktVideoCapabilitiesTests.cpp#L2394-L2399), [`VkVideoChromaSubsamplingFlagBitsKHR`](../../../../vulkan-docs/src/chapters/videocoding.adoc#L486-L507) |
| Component bit depth | `8_BIT`, `10_BIT`, `12_BIT` | Selects equal luma and chroma profile depths and must match the YCbCr format's component depth. | [`bitdepthFlags` and depth pruning](../../../modules/vulkan/video/vktVideoCapabilitiesTests.cpp#L2401-L2403), [`VkVideoComponentBitDepthFlagBitsKHR`](../../../../vulkan-docs/src/chapters/videocoding.adoc#L517-L529) |
| Image tiling | Returned `LINEAR`, `OPTIMAL`, or `DRM_FORMAT_MODIFIER_EXT` | Selects the format-feature field or DRM modifier compatibility path used for the cross-query check. | [`formats::test`](../../../modules/vulkan/video/vktVideoCapabilitiesTests.cpp#L2218-L2283) |

The source vector contains 62 formats. The generator does not register the full Cartesian product. It emits 1701 format leaves after its format-class, depth, and subsampling pruning rules, as confirmed by the exact `video.txt` mustpass entries.

## Behavior Parameters

The primary behavioral axis is the test family. `capabilities` and `formats` use different query contracts, so a failure in one family narrows the likely fault differently from a failure in the other.

### capabilities: queue and profile capability reporting

The family queries queue-family video properties and `vkGetPhysicalDeviceVideoCapabilitiesKHR`. It validates the generic capability structure, the decode or encode structure, the codec-specific extension, and the optional intra-refresh structure. Repeating the capability query with result storage initialized to `0x00` and `0xFF` checks both repeatability and that the implementation writes the fields the test reads.

The 25 leaves cover queue support; H.264, H.265, AV1, and VP9 decode capability queries; H.264, H.265, and AV1 encode capability queries; decode and encode video-format support queries that use the simpler query instance; and H.264, H.265, and AV1 encode intra-refresh capability queries. The exact leaf names appear in [`getTestName`](../../../modules/vulkan/video/vktVideoCapabilitiesTests.cpp#L1891-L1948) and the mustpass file [`video.txt`](../../../mustpass/main/vk-default/video.txt#L1-L25).

For generic capabilities, the test compares flags, bitstream-buffer alignments, picture access granularity, coded extents, DPB slots, active reference pictures, and the Video Std header version. It rejects unknown flags, zero alignments or dimensions, invalid extents, and zero DPB or active-reference limits. Decode flags are restricted to DPB/output coincidence flags. Encode results also require nonzero rate-control layer and quality-level counts; when `VK_KHR_video_maintenance2` is supported, the disabled rate-control mode must be reported. See [`validateVideoCapabilities`](../../../modules/vulkan/video/vktVideoCapabilitiesTests.cpp#L508-L560), [`validateVideoDecodeCapabilities`](../../../modules/vulkan/video/vktVideoCapabilitiesTests.cpp#L562-L575), and [`validateVideoEncodeCapabilities`](../../../modules/vulkan/video/vktVideoCapabilitiesTests.cpp#L577-L611).

Codec-specific checks compare the fields that belong to the selected codec. H.264 checks its maximum level and field granularity. H.265 checks its maximum level. AV1 and VP9 check their maximum levels. Encode H.264 and H.265 check reference counts, slice limits, temporal behavior, quantizer ranges, and allowed codec flags. AV1 encode checks reference counts, operating-point and layer limits, quantizer indices, superblock sizes, and allowed flags. The source performs these checks in the codec-specific validation methods linked from the appendix.

The intra-refresh leaves add a chained `VkVideoEncodeIntraRefreshCapabilitiesKHR`. They require at least one reference path, at least one valid intra-refresh mode, the required dependency between row or column block modes and the general block mode, a valid cycle duration, and at least one active reference picture. If per-picture-partition mode is the only mode, its cycle duration cannot exceed the codec's maximum picture partitions. See [`validateIntraRefreshCapabilities`](../../../modules/vulkan/video/vktVideoCapabilitiesTests.cpp#L1434-L1483).

### formats: profile, usage, and image-format consistency

The family enumerates formats for a single `VkVideoProfileListInfoKHR` and one image usage. It must find the requested `VkFormat` in the returned `VkVideoFormatPropertiesKHR` entries, with the requested usage bit present. It then derives `VkPhysicalDeviceImageFormatInfo2` from the returned entry and calls `vkGetPhysicalDeviceImageFormatProperties2` with the same profile list, format, image type, tiling, usage, and creation flags.

The helper maps each requested video usage to the corresponding ordinary format feature: decode destination to `VK_FORMAT_FEATURE_VIDEO_DECODE_OUTPUT_BIT_KHR`, decode DPB to `VK_FORMAT_FEATURE_VIDEO_DECODE_DPB_BIT_KHR`, encode source to `VK_FORMAT_FEATURE_VIDEO_ENCODE_INPUT_BIT_KHR`, and encode DPB to `VK_FORMAT_FEATURE_VIDEO_ENCODE_DPB_BIT_KHR`. The test checks the linear or optimal feature field returned by `vkGetPhysicalDeviceFormatProperties2`. For DRM modifier tiling, it queries the modifiers and requires one compatible modifier; an individual modifier that returns `VK_ERROR_FORMAT_NOT_SUPPORTED` is skipped. See [`kUsageToFeatureMap`](../../../modules/vulkan/video/vktVideoCapabilitiesTests.cpp#L2170-L2175) and [`formats::test`](../../../modules/vulkan/video/vktVideoCapabilitiesTests.cpp#L2200-L2291).

A successful video-format query must return at least one entry and the data query must write the reported number of entries. The test rejects unwritten `VK_FORMAT_MAX_ENUM`. `VK_FORMAT_UNDEFINED` is accepted only for an opaque DPB result and only when it is the sole returned entry. For the simpler capability-family format-support leaves, a non-opaque result passes only when it includes `VK_FORMAT_G8_B8_R8_3PLANE_420_UNORM` or `VK_FORMAT_G8_B8R8_2PLANE_420_UNORM`. These checks distinguish an unsupported combination from a successful query that returned invalid data.

## Shader Analysis

This source contains no shader or shader-generated artifact. The capability and format families only query physical-device properties and inspect the returned structures, so no representative shader walkthrough or SPIR-V artifact applies.

## Runtime Execution and Result Checking

- `[host]` The CTS checks the build-time video switch and requires `VK_KHR_video_queue`. Each capability leaf then requires its codec extension; intra-refresh leaves also require `VK_KHR_video_encode_intra_refresh`. The capability test requires `VK_KHR_video_maintenance2` when the device reports it. The format test requires the extension matching its codec operation. See [`VideoCapabilitiesQueryTestCase::checkSupport`](../../../modules/vulkan/video/vktVideoCapabilitiesTests.cpp#L1750-L1829) and [`formats::checkSupport`](../../../modules/vulkan/video/vktVideoCapabilitiesTests.cpp#L2132-L2168).
- `[host]` For `queue_support_query`, the test obtains the queue-family count, allocates one `VkQueueFamilyProperties2` and one chained `VkQueueFamilyVideoPropertiesKHR` per family, initializes the chain, and makes the data query.
- `[host]` For a capability leaf, the test constructs a profile and the matching output chain. It performs two capability queries using result arrays initialized to different byte patterns, then compares fields and checks Vulkan constraints.
- `[host]` For an intra-refresh leaf, the test makes one capability query and checks codec reference support and the intra-refresh constraints against the returned codec limit.
- `[host]` For a format leaf, the test performs the count query, allocates and initializes the `VkVideoFormatPropertiesKHR` array, and performs the data query. It searches the returned entries for the requested format and usage.
- `[host]` For each matching entry, the test queries DRM modifiers when needed, calls `vkGetPhysicalDeviceImageFormatProperties2` with parameters copied from the video-format result, and checks the matching linear or optimal format feature bit.
- `[host]` The test returns pass after all relevant checks succeed. Support pruning becomes `NotSupportedError`; invalid return codes, malformed successful results, failed cross-query checks, and violated capability relationships become test failures.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `capabilities` | Queue-family video properties, profile capability `pNext` chain population, capability field or flag reporting, extension metadata, codec-specific limits, or intra-refresh capability relationships are inconsistent with Vulkan requirements. |
| `formats` | The implementation reports a video format that does not support the requested usage, profile, image creation parameters, DRM modifier, or corresponding video format feature bit; or it returns an invalid query result or error code. |

### Cause Analysis

#### Queue and profile capability reporting

**Possible failure symptoms:** The queue query reports no usable encode or decode path, a video queue has zero queues, or its `videoCodecOperations` bits do not match its `VK_QUEUE_VIDEO_ENCODE_BIT_KHR` or `VK_QUEUE_VIDEO_DECODE_BIT_KHR` flag. A capability query can also fail, leave fields at their initialization pattern, return an unknown flag, return zero or contradictory limits, mismatch its second query, or violate a codec-specific relationship.

**Possible implementation causes:** The queue-family property path may expose queue flags without the matching codec-operation mask, or the device may report a queue family that has no usable queue. A profile-to-capability dispatch path may select the wrong codec structure or fail to populate a chained result structure. A driver may report unsupported capability bits, invalid alignments or extents, inconsistent Video Std header metadata, or codec limits that conflict with the generic or intra-refresh structures. The source and specification identify these checks, but they do not identify the hardware or driver component responsible for a particular failure. Further implementation investigation is needed.

#### Profile and usage format enumeration

**Possible failure symptoms:** `vkGetPhysicalDeviceVideoFormatPropertiesKHR` returns an error for a supported test case, returns zero entries, reports fewer entries than the data query contract allows, leaves a format at `VK_FORMAT_MAX_ENUM`, returns an invalid opaque-DPB result, or omits the requested format or usage bit. The query can also return a video-format entry whose derived image-format query fails for reasons other than an individually unsupported DRM modifier.

**Possible implementation causes:** The implementation may reject a codec-specific profile, a picture layout, a chroma or bit-depth combination, or an image usage that its advertised extension path should support. It may enumerate a format without preserving the required usage relationship, or it may fail to honor the count/data-query contract. A mismatch in the profile list, image type, tiling, usage, or creation flags passed to `vkGetPhysicalDeviceImageFormatProperties2` can expose inconsistent format-query handling. The specification assigns specific Vulkan error codes to unsupported profile operation, format parameters, codec parameters, picture layout, and image usage; the test treats those as support outcomes where the helper handles them, not as proof of an implementation defect.

#### Cross-query format and modifier consistency

**Possible failure symptoms:** An enumerated linear or optimal format lacks the required video format feature bit, `vkGetPhysicalDeviceImageFormatProperties2` rejects the returned parameters, a DRM entry has no compatible modifier, or the image-format query and video-format query return inconsistent results.

**Possible implementation causes:** The implementation may advertise a video usage without exposing the corresponding format feature in the selected tiling, or may disagree between video-format enumeration and ordinary image-format validation. A DRM modifier list can lack a modifier compatible with the returned video entry. The test allows `VK_ERROR_FORMAT_NOT_SUPPORTED` for an individual DRM modifier and continues to the next modifier; it fails when no modifier works or when a non-DRM query returns another error. The source does not identify whether such a mismatch originates in format tables, modifier handling, or image-creation validation.

## Case Pruning

### Requirement-based pruning

- The build must include video tests. Otherwise `DE_BUILD_VIDEO` disables the cases through `NotSupportedError`.
- Every capability and format case requires `VK_KHR_video_queue`; codec cases require the matching decode or encode extension. Intra-refresh cases require both the codec extension and `VK_KHR_video_encode_intra_refresh`.
- The profile must use one chroma subsampling value and one luma bit depth. Non-monochrome profiles use the selected component depth for chroma as well. The codec-specific profile structure must match the selected codec operation.
- The format query can report unsupported operation, format parameters, codec parameters, picture layout, or image usage through the Vulkan video-profile error codes. The format helper converts those outcomes to `NotSupportedError`. Out-of-memory results fail the case; `VK_INCOMPLETE` and other unexpected results fail as invalid query behavior.
- The returned image format must support the requested video usage. The corresponding linear or optimal feature bit must be present, and the returned image parameters must succeed in `vkGetPhysicalDeviceImageFormatProperties2`. These are checks on a surviving case, not generator pruning.

### Design-based pruning

- The generator starts with seven codec operations, four usages, 65 source formats, four subsampling values, and three bit depths, then removes combinations that do not describe the intended format/profile relationship.
- Non-YCbCr formats survive only for `VK_IMAGE_USAGE_VIDEO_ENCODE_SRC_BIT_KHR` with monochrome subsampling. The source comments identify this as a reduction because other uses are unlikely to support such formats.
- For YCbCr formats, the selected profile depth must equal `ycbcr::getYCbCrBitDepth(format)`. The generator also removes subsampling values that disagree with the format's horizontal and vertical chroma subsampling flags.
- The generator sets luma and chroma profile depth to the same value. This reduces duplicate combinations; it does not test unequal component depths.
- The source emits 1701 format leaves after these rules. A skipped combination is outside the generated test design. It does not establish that the implementation would reject that combination.

## Key Takeaways

- `capabilities` checks the population, repeatability, allowed values, and relationships of queue and video-profile capability structures. It does not exercise video coding commands.
- `formats` checks a complete chain of claims: the requested profile and usage must produce a matching video format, that format must survive ordinary image-format validation, and the selected tiling must expose the corresponding video format feature.
- The two initialized capability result chains make an unwritten or partially written field visible by comparing the `0x00` and `0xFF` query results.
- The format matrix is broad but intentionally pruned. Its 1701 mustpass leaves cover supported shape combinations selected by the generator, not every theoretical codec, format, usage, subsampling, and bit-depth product.
- Unsupported profile and usage errors describe a skipped support combination. A malformed successful result or a disagreement between related Vulkan queries is a test failure. See [`Failure Meaning`](#failure-meaning).

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Queue-family query | [`VideoQueueQueryTestInstance::iterate`](../../../modules/vulkan/video/vktVideoCapabilitiesTests.cpp#L108-L180) | Queries queue-family video properties and checks queue flags, codec operations, queue counts, and support gates. |
| Capability leaf registration | [`createVideoCapabilitiesTests`](../../../modules/vulkan/video/vktVideoCapabilitiesTests.cpp#L2297-L2313) | Registers the `video.capabilities` family and its 25 exact leaves. |
| Capability support and dispatch | [`checkSupport` and `createInstance`](../../../modules/vulkan/video/vktVideoCapabilitiesTests.cpp#L1750-L1889) | Shows build, extension, maintenance2, and intra-refresh gates and maps leaves to implementations. |
| Generic capability validation | [`validateVideoCapabilities`](../../../modules/vulkan/video/vktVideoCapabilitiesTests.cpp#L508-L560) | Checks repeated generic fields, flags, alignments, extents, DPB limits, and reference limits. |
| Encode and intra-refresh validation | [`validateVideoEncodeCapabilities`](../../../modules/vulkan/video/vktVideoCapabilitiesTests.cpp#L577-L611) and [`validateIntraRefreshCapabilities`](../../../modules/vulkan/video/vktVideoCapabilitiesTests.cpp#L1434-L1483) | Checks encode fields, maintenance2 behavior, codec reference requirements, modes, and limits. |
| Format matrix registration | [`createVideoFormatsTests`](../../../modules/vulkan/video/vktVideoCapabilitiesTests.cpp#L2315-L2486) | Defines codecs, formats, usages, subsampling, bit depths, names, and design pruning. |
| Format query helper | [`getVideoFormatProperties`](../../../modules/vulkan/video/vktVideoCapabilitiesTests.cpp#L2077-L2129) | Performs count and data queries and classifies Vulkan return codes. |
| Format cross-query test | [`formats::test`](../../../modules/vulkan/video/vktVideoCapabilitiesTests.cpp#L2200-L2291) | Matches the requested format and usage, checks image-format properties, DRM modifiers, and format features. |
| Capability query specification | [`Video Coding Capabilities`](../../../../vulkan-docs/src/chapters/videocoding.adoc#L759-L908) | Defines the profile-specific capability query and required output chain. |
| Format query specification | [`Video Format Capabilities`](../../../../vulkan-docs/src/chapters/videocoding.adoc#L939-L1117) | Defines count/data enumeration, profile lists, usage inclusion, and image-format cross-checks. |
| Queue-family specification | [`VkQueueFamilyVideoPropertiesKHR`](../../../../vulkan-docs/src/chapters/devsandqueues.adoc#L1649-L1668) | Defines the queue-family codec-operation report. |
| Format feature specification | [`Format Feature Dependent Usage Flags`](../../../../vulkan-docs/src/chapters/formats.adoc#L4117-L4165) | Maps each video image usage to its required format feature bit. |
| Exact mustpass registration | [`video.txt`](../../../mustpass/main/vk-default/video.txt#L1-L25) and [`format leaves`](../../../mustpass/main/vk-default/video.txt#L6158-L7858) | Confirms 25 capability leaves and 1701 `video.formats` leaves in the default mustpass. |
