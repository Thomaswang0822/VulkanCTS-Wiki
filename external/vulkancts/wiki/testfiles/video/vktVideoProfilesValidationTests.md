# vktVideoProfilesValidationTests

## Overview

`vktVideoProfilesValidationTests.cpp` registers the `video.profiles` group. It splits validation into `decode` and `encode` branches, then into codec groups for H.264, H.265, AV1, VP9 decode and H.264, H.265, AV1 encode ([vktVideoProfilesValidationTests.cpp](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L1096-L1324)).

## Role of File

| Aspect | Evidence-backed description |
|---|---|
| Registration role | Creates `profiles`, nested `decode`/`encode`, and codec child groups before adding generated `VideoProfilesValidationTestCase` leaves ([vktVideoProfilesValidationTests.cpp](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L1096-L1324)). |
| Implementation role | Validates codec/profile compatibility, video-format query consistency, image-format property alignment, and session creation for profiles ([vktVideoProfilesValidationTests.cpp](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L240-L392), [vktVideoProfilesValidationTests.cpp](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L394-L782)). |

## Registration Hierarchy

```text
video.profiles
├── decode
└── encode
video.profiles.decode
├── av1
├── h264
├── h265
└── vp9
video.profiles.encode
├── av1
├── h264
└── h265
```

## Test Families

- H.264 decode cases combine picture layout and H.264 profile ID with generated chroma and bit-depth combinations ([vktVideoProfilesValidationTests.cpp](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L1117-L1128), [vktVideoProfilesValidationTests.cpp](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L1176-L1196)).
- H.265, AV1, and VP9 decode cases iterate their codec profile arrays; AV1 also iterates film-grain support ([vktVideoProfilesValidationTests.cpp](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L1130-L1151), [vktVideoProfilesValidationTests.cpp](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L1198-L1252)).
- H.264, H.265, and AV1 encode cases iterate codec profile arrays with the same chroma and bit-depth dimensions ([vktVideoProfilesValidationTests.cpp](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L1254-L1306)).

## Parameter Dimensions and Observed Values

| Dimension | Observed values or source |
|---|---|
| Codec operations | Decode H.264/H.265/AV1/VP9 and encode H.264/H.265/AV1 ([vktVideoProfilesValidationTests.cpp](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L1100-L1104)). |
| Chroma/bit-depth dimensions | Monochrome/420/422/444; luma and chroma 8/10/12-bit with monochrome mismatches skipped ([vktVideoProfilesValidationTests.cpp](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L1110-L1115), [vktVideoProfilesValidationTests.cpp](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L1153-L1174)). |
| Codec profile dimensions | H.264, H.265, AV1, and VP9 profile arrays are explicit source lists ([vktVideoProfilesValidationTests.cpp](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L1123-L1149)). |
| Generated names | Names include codec profile, chroma subsampling, luma bit depth, and chroma bit depth ([vktVideoProfilesValidationTests.cpp](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L1000-L1081)). |

## Support and Feature Requirements

Each case requires `VK_KHR_video_queue`; decode cases require the decode queue and codec extension, encode cases require the encode queue and codec extension, and maintenance1 is required when exposed ([vktVideoProfilesValidationTests.cpp](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L809-L848)). Instance construction requests a device with transfer plus encode or decode queue bits and synchronization2-or-not-supported handling; VP9 adds the decode-VP9 flag ([vktVideoProfilesValidationTests.cpp](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L127-L160)).

## Verification Methods

- `validateProfileCodec()` checks whether chroma subsampling and bit-depth combinations are compatible with the selected codec profile before interpreting capability-query results ([vktVideoProfilesValidationTests.cpp](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L240-L392)).
- `validateVideoFormatsWithProfile()` queries format properties, checks nonzero results, verifies returned formats against expected sets and requested usage, then cross-checks format and image-format properties ([vktVideoProfilesValidationTests.cpp](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L582-L782)).
- `tryCreateVideoSession()` creates and destroys a video session using the selected profile and returned formats to verify that the advertised profile can be instantiated ([vktVideoProfilesValidationTests.cpp](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L166-L237)).

## Test Principles

- Invalid profile combinations are expected to produce video capability query errors rather than successful format lists ([vktVideoProfilesValidationTests.cpp](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L753-L782)).
- The tests validate profile-format consistency through several Vulkan query surfaces instead of relying on one query result alone ([vktVideoProfilesValidationTests.cpp](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L394-L782)).

## Notes / Uncertainties

- The hierarchy block lists codec groups one level below the profile decode/encode roots; generated leaf names are described by the parameter dimensions and are present in mustpass but are not all repeated here.
