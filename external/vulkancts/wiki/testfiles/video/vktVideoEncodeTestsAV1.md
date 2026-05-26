# vktVideoEncodeTestsAV1

## Overview

`vktVideoEncodeTestsAV1.cpp` registers the AV1 branch under `video.encode.av1`. It generates resolution/bit-depth/subsampling groups from static source dimensions, creates nested GOP groups, and adds AV1 encode test cases only when the remaining parameter combination passes `validateTestDefinition()`; the default mustpass-covered direct AV1 encode paths are the 8-bit and 10-bit 4:2:0 groups listed below ([vktVideoEncodeTestsAV1.cpp](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L1342-L1398), [vktVideoEncodeTestsAV1.cpp](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L1215-L1228)).

## Role of File

| Aspect | Evidence-backed description |
|---|---|
| Registration role | Creates `av1`, frame-size/bit-depth/subsampling groups, one nested group per GOP descriptor under each, and leaf test cases only for validated remaining AV1 dimensions; the canonical hierarchy block is limited to default mustpass-covered AV1 encode group paths ([vktVideoEncodeTestsAV1.cpp](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L1342-L1398), [vktVideoEncodeTestsAV1.cpp](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L1215-L1228), [video.txt](../../../mustpass/main/vk-default/video.txt#L1-L25)). |
| Implementation role | Builds AV1 encoder parameters, runs encode, validates encoded output by decoding and PSNR comparison, and applies AV1 capability gates ([vktVideoEncodeTestsAV1.cpp](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L424-L459), [vktVideoEncodeTestsAV1.cpp](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L566-L733)). |

## Registration Hierarchy

```text
video.encode.av1
├── 128x128_10le_420
├── 128x128_8le_420
├── 176x144_10le_420
├── 176x144_8le_420
├── 1920x1080_10le_420
├── 1920x1080_8le_420
├── 352x288_10le_420
├── 352x288_8le_420
├── 3840x2160_10le_420
├── 3840x2160_8le_420
├── 720x480_10le_420
├── 720x480_8le_420
├── 7680x4320_10le_420
└── 7680x4320_8le_420
```

## Test Families

- Top-level AV1 child names combine frame size, bit depth, and chroma subsampling in names such as `128x128_8le_420`; source dimensions include additional bit-depth/subsampling inputs, while the listed canonical paths are the default mustpass-covered groups that survived into the default path set ([vktVideoEncodeTestsAV1.cpp](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L1348-L1359), [vktVideoEncodeTestsAV1.cpp](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L1234-L1250), [video.txt](../../../mustpass/main/vk-default/video.txt#L1-L25)).
- Each top-level child contains GOP groups named from GOP sub-name and frame count, and leaves combine tiling, ordering, resolution change, quantization, superblock, rate control, loop filter/restoration, CDEF, DPB mode, and intra-refresh dimensions after validation ([vktVideoEncodeTestsAV1.cpp](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L1360-L1395)).
- Invalid or unsupported static combinations are discarded by `validateTestDefinition()` before a `VideoTestCase` is returned ([vktVideoEncodeTestsAV1.cpp](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L955-L958), [vktVideoEncodeTestsAV1.cpp](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L1217-L1228)).

## Parameter Dimensions and Observed Values

| Dimension | Observed values or source |
|---|---|
| Frame sizes | 128x128, 176x144, 352x288, 720x480, 1920x1080, 3840x2160, and 7680x4320 from `frameSizeTests` ([vktVideoEncodeTestsAV1.cpp](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L1233-L1237)). |
| Source bit-depth inputs | `8le`, `10le`, and `12le` from `bitDepthTests`; the canonical default path list contains 8-bit and 10-bit 4:2:0 groups ([vktVideoEncodeTestsAV1.cpp](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L1239-L1243), [video.txt](../../../mustpass/main/vk-default/video.txt#L1-L25)). |
| Source chroma subsampling inputs | `400`, `420`, `422`, and `444` from `subsamplingTests`; the canonical default path list contains 4:2:0 groups ([vktVideoEncodeTestsAV1.cpp](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L1245-L1250), [vktVideoEncodeTestsAV1.cpp](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L1348-L1397), [video.txt](../../../mustpass/main/vk-default/video.txt#L1-L25)). |
| Source chroma subsampling inputs | `400`, `420`, `422`, and `444` from `subsamplingTests`; the canonical default path list contains 4:2:0 groups ([vktVideoEncodeTestsAV1.cpp](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L1245-L1250), [vktVideoEncodeTestsAV1.cpp](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L1348-L1397), [video.txt](../../../mustpass/main/vk-default/video.txt#L1-L25)). |
| Core AV1 dimensions | Chroma subsampling, GOP, ordering, resolution change, quantization, tiling, superblock, rate-control, loop filter/restoration, CDEF, DPB mode, and intra-refresh structs are part of `TestDefinition` ([vktVideoEncodeTestsAV1.cpp](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L267-L284)). |

## Support and Feature Requirements

AV1 cases call `VideoDevice::checkSupport`, require all extensions collected in `TestRequirements`, validate AV1 encode capabilities, reject unsupported B frames, bitrate modes, superblock sizes, dimensions, separate DPB images, tile geometry, missing formats, and unsupported intra-refresh modes or midway cycle duration ([vktVideoEncodeTestsAV1.cpp](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L566-L733)).

## Verification Methods

`iterate()` encodes every expected frame, fetches the bitstream for each frame, and validates the encoded content with `validateEncodedContent()` using AV1 profile, source clip, expected extent, chroma subsampling, bit depth, and a PSNR lower limit of 50.0 ([vktVideoEncodeTestsAV1.cpp](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L424-L459), [vktVideoEncodeTestsAV1.cpp](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L63-L65)).

## Test Principles

- AV1 generation uses broader source dimensions than the default mustpass path set, and filters impossible combinations before creating leaf test cases, so not every source Cartesian-product point becomes a default listed path ([vktVideoEncodeTestsAV1.cpp](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L1348-L1397), [vktVideoEncodeTestsAV1.cpp](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L955-L958), [vktVideoEncodeTestsAV1.cpp](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L1217-L1228), [video.txt](../../../mustpass/main/vk-default/video.txt#L1-L25)).
- Capability checks are tied to each generated `TestRequirements` instance rather than only to global AV1 encode support ([vktVideoEncodeTestsAV1.cpp](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L286-L306), [vktVideoEncodeTestsAV1.cpp](../../../modules/vulkan/video/vktVideoEncodeTestsAV1.cpp#L566-L733)).

## Notes / Uncertainties

