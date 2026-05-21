# Video Tests

## Overview

The Vulkan CTS `video` category covers video queue/capability queries, video format and profile validation, decode sessions, encode sessions, and video-specific synchronization coverage. The public category root is registered by `TestPackage::init()` as `video`, which delegates to `video::createTests` ([vktTestPackage.cpp](../../modules/vulkan/vktTestPackage.cpp#L1394-L1396)). The root dispatcher then adds seven direct child groups: `capabilities`, `formats`, `profiles`, `decode`, `encode`, `synchronization`, and `synchronization2` ([vktVideoTests.cpp](../../modules/vulkan/video/vktVideoTests.cpp#L40-L93)).

`doc/testspecs/VK/apitests.adoc` was inspected as required; text search found no video-specific section, so category-specific statements below are derived from inspected `external/vulkancts/` source and `mustpass/main/vk-default/video.txt`.

## Registration Entry Point

| Level | Evidence |
|---|---|
| Package root | `TestPackage::init()` registers `video` with `video::createTests` ([vktTestPackage.cpp](../../modules/vulkan/vktTestPackage.cpp#L1394-L1396)). |
| Category builder | `vktVideoTests.cpp` creates the supplied root group and attaches the seven observed child groups ([vktVideoTests.cpp](../../modules/vulkan/video/vktVideoTests.cpp#L40-L93)). |
| Mustpass coverage | The default mustpass branch includes `vk-default/video.txt` ([vk-default.txt](../../mustpass/main/vk-default.txt#L95-L97)), and that file contains `dEQP-VK.video.*` paths ([video.txt](../../mustpass/main/vk-default/video.txt#L1-L25)). |

## Subgroup Structure

```text
video
├── capabilities
├── decode
├── encode
├── formats
├── profiles
├── synchronization
└── synchronization2
```

## File Inventory

| Source file | Wiki page | Role |
|---|---|---|
| [vktVideoTests.cpp](../../modules/vulkan/video/vktVideoTests.cpp) | [vktVideoTests](../testfiles/video/vktVideoTests.md) | Category dispatcher and synchronization/synchronization2 video child registration. |
| [vktVideoCapabilitiesTests.cpp](../../modules/vulkan/video/vktVideoCapabilitiesTests.cpp) | [vktVideoCapabilitiesTests](../testfiles/video/vktVideoCapabilitiesTests.md) | Registers and implements `capabilities` and `formats`. |
| [vktVideoProfilesValidationTests.cpp](../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp) | [vktVideoProfilesValidationTests](../testfiles/video/vktVideoProfilesValidationTests.md) | Registers and implements `profiles`. |
| [vktVideoDecodeTests.cpp](../../modules/vulkan/video/vktVideoDecodeTests.cpp) | [vktVideoDecodeTests](../testfiles/video/vktVideoDecodeTests.md) | Registers and implements `decode`. |
| [vktVideoEncodeTests.cpp](../../modules/vulkan/video/vktVideoEncodeTests.cpp) | [vktVideoEncodeTests](../testfiles/video/vktVideoEncodeTests.md) | Registers and implements H.264/H.265 `encode`, and attaches AV1 encode. |
| [vktVideoEncodeTestsAV1.cpp](../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp) | [vktVideoEncodeTestsAV1](../testfiles/video/vktVideoEncodeTestsAV1.md) | Registers and implements the AV1 encode branch. |
| [vktVideoTestUtils.cpp](../../modules/vulkan/video/vktVideoTestUtils.cpp) | Covered by implementation pages | Shared video support, format, decode/encode validation utilities; no inspected top-level test registration. |
| [vktVideoClipInfo.cpp](../../modules/vulkan/video/vktVideoClipInfo.cpp) | Covered by decode/encode pages | Clip metadata and decode reference checksums used by content validation. |

Only source files observed registering tests receive Level-3 pages.

## Level-3 Documentation

- [vktVideoTests](../testfiles/video/vktVideoTests.md) — category dispatcher and synchronization child registration.
- [vktVideoCapabilitiesTests](../testfiles/video/vktVideoCapabilitiesTests.md) — capability query and video format query cases.
- [vktVideoProfilesValidationTests](../testfiles/video/vktVideoProfilesValidationTests.md) — profile compatibility and format/session validation.
- [vktVideoDecodeTests](../testfiles/video/vktVideoDecodeTests.md) — H.264/H.265/AV1/VP9 decode session tests.
- [vktVideoEncodeTests](../testfiles/video/vktVideoEncodeTests.md) — H.264/H.265 encode session tests.
- [vktVideoEncodeTestsAV1](../testfiles/video/vktVideoEncodeTestsAV1.md) — AV1 encode session tests.

## Recurring Test Families and Themes

| Theme | Evidence-backed summary |
|---|---|
| Capability and format introspection | `capabilities` validates queue-family video operations, video capabilities, and codec-specific capability fields; `formats` cross-checks video format properties against format and image-format properties ([vktVideoCapabilitiesTests.cpp](../../modules/vulkan/video/vktVideoCapabilitiesTests.cpp#L108-L181), [vktVideoCapabilitiesTests.cpp](../../modules/vulkan/video/vktVideoCapabilitiesTests.cpp#L2269-L2288)). |
| Profile compatibility | `profiles` combines codec profiles, chroma subsampling, and bit-depth dimensions, then validates capability-query behavior, format properties, and session creation ([vktVideoProfilesValidationTests.cpp](../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L1096-L1324), [vktVideoProfilesValidationTests.cpp](../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L240-L782)). |
| Decode output validation | Decode cases execute video decode and compare downloaded frames against clip reference checksums, with PSNR handling for film-grain cases ([vktVideoDecodeTests.cpp](../../modules/vulkan/video/vktVideoDecodeTests.cpp#L1483-L1557), [vktVideoClipInfo.cpp](../../modules/vulkan/video/vktVideoClipInfo.cpp#L20-L28)). |
| Encode output validation | H.264/H.265 and AV1 encode paths verify encoded content by decoding and PSNR-based quality checks ([vktVideoEncodeTests.cpp](../../modules/vulkan/video/vktVideoEncodeTests.cpp#L3358-L3499), [vktVideoEncodeTestsAV1.cpp](../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L424-L459)). |
| Synchronization reuse | The category registers synchronization and synchronization2 video branches by passing codec operations to shared synchronization builders ([vktVideoTests.cpp](../../modules/vulkan/video/vktVideoTests.cpp#L51-L90)). |

## Recurring Parameter Dimensions

| Dimension | Category-level evidence |
|---|---|
| Codec operations | Decode H.264/H.265/AV1/VP9 and encode H.264/H.265/AV1 recur across capabilities, formats, profiles, and root synchronization branches ([vktVideoCapabilitiesTests.cpp](../../modules/vulkan/video/vktVideoCapabilitiesTests.cpp#L2319-L2323), [vktVideoProfilesValidationTests.cpp](../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L1100-L1104), [vktVideoTests.cpp](../../modules/vulkan/video/vktVideoTests.cpp#L54-L88)). |
| Chroma and bit depth | Video format/profile generators use monochrome/420/422/444 and 8/10/12-bit combinations with source-level pruning ([vktVideoCapabilitiesTests.cpp](../../modules/vulkan/video/vktVideoCapabilitiesTests.cpp#L2394-L2441), [vktVideoProfilesValidationTests.cpp](../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L1110-L1174)). |
| Resource layout variants | Decode uses layered/separated DPB and general/video layouts; H.264/H.265 encode uses layered/separated source and general/video layouts ([vktVideoDecodeTests.cpp](../../modules/vulkan/video/vktVideoDecodeTests.cpp#L1985-L2026), [vktVideoEncodeTests.cpp](../../modules/vulkan/video/vktVideoEncodeTests.cpp#L3986-L4007)). |
| Codec-specific stream patterns | Decode and H.264/H.265 encode are driven by explicit clip/pattern arrays; AV1 encode uses explicit multidimensional definition structs ([vktVideoDecodeTests.cpp](../../modules/vulkan/video/vktVideoDecodeTests.cpp#L590-L703), [vktVideoEncodeTests.cpp](../../modules/vulkan/video/vktVideoEncodeTests.cpp#L416-L1088), [vktVideoEncodeTestsAV1.cpp](../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L267-L284)). |

## Recurring Support Requirements

| Requirement area | Evidence |
|---|---|
| Base video support | Capability and profile tests require `VK_KHR_video_queue`; decode and encode tests call `VideoDevice::checkSupport` for the selected operation ([vktVideoCapabilitiesTests.cpp](../../modules/vulkan/video/vktVideoCapabilitiesTests.cpp#L1757-L1760), [vktVideoProfilesValidationTests.cpp](../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L809-L848), [vktVideoDecodeTests.cpp](../../modules/vulkan/video/vktVideoDecodeTests.cpp#L1749-L1753), [vktVideoEncodeTests.cpp](../../modules/vulkan/video/vktVideoEncodeTests.cpp#L3868-L3873)). |
| Codec extensions | Source check paths require the selected codec extension, such as `VK_KHR_video_decode_h264`, `VK_KHR_video_encode_h265`, or `VK_KHR_video_encode_av1` ([vktVideoCapabilitiesTests.cpp](../../modules/vulkan/video/vktVideoCapabilitiesTests.cpp#L1767-L1826), [vktVideoProfilesValidationTests.cpp](../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L818-L845)). |
| Maintenance and layout gates | Decode/encode maintenance tests require maintenance1 or maintenance2; general-layout variants require unified image layout support with `unifiedImageLayoutsVideo` ([vktVideoDecodeTests.cpp](../../modules/vulkan/video/vktVideoDecodeTests.cpp#L1772-L1811), [vktVideoDecodeTests.cpp](../../modules/vulkan/video/vktVideoDecodeTests.cpp#L1926-L1931), [vktVideoEncodeTests.cpp](../../modules/vulkan/video/vktVideoEncodeTests.cpp#L3890-L3968)). |
| Encode feature gates | H.264/H.265 encode checks query-status, quantization-map, rate-control, P/B reference, intra-refresh, and extent support; AV1 encode checks B frames, rate control, superblock/tile/dimension/DPB/intra-refresh support ([vktVideoEncodeTests.cpp](../../modules/vulkan/video/vktVideoEncodeTests.cpp#L2053-L2226), [vktVideoEncodeTestsAV1.cpp](../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L566-L733)). |

## Recurring Verification Methods

- **API result and field validation:** capability and format tests reject bad query counts, missing formats, invalid flags, invalid alignments, and inconsistent properties ([vktVideoCapabilitiesTests.cpp](../../modules/vulkan/video/vktVideoCapabilitiesTests.cpp#L118-L180), [vktVideoCapabilitiesTests.cpp](../../modules/vulkan/video/vktVideoCapabilitiesTests.cpp#L508-L612), [vktVideoCapabilitiesTests.cpp](../../modules/vulkan/video/vktVideoCapabilitiesTests.cpp#L2269-L2288)).
- **Cross-query profile validation:** profile tests compare capability-query behavior, video format properties, format features, image-format properties, and session creation ([vktVideoProfilesValidationTests.cpp](../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L394-L782)).
- **Decoded-frame checksums:** decode tests compare output frame checksums against clip reference data ([vktVideoDecodeTests.cpp](../../modules/vulkan/video/vktVideoDecodeTests.cpp#L1483-L1557), [vktVideoClipInfo.cpp](../../modules/vulkan/video/vktVideoClipInfo.cpp#L1089-L1091)).
- **PSNR-based encode validation:** encode tests decode generated bitstreams and apply PSNR threshold or PSNR-difference checks ([vktVideoEncodeTests.cpp](../../modules/vulkan/video/vktVideoEncodeTests.cpp#L3358-L3499), [vktVideoEncodeTestsAV1.cpp](../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L424-L459)).

## Notes and Uncertainties

- No video-specific prose was found in the inspected `apitests.adoc`; this page intentionally relies on source and mustpass evidence.
- The `synchronization` and `synchronization2` children are registered by the video dispatcher but implemented by shared synchronization code outside `modules/vulkan/video/` ([vktVideoTests.cpp](../../modules/vulkan/video/vktVideoTests.cpp#L51-L90)).
- `external/vulkancts/wiki/README.md` was not updated to mark `video` done; the requested semantic audit is still a separate follow-up step.
