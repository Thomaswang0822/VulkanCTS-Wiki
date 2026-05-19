# [vktImageSampleDrawnCubeFaceTests.cpp](../../../modules/vulkan/image/vktImageSampleDrawnCubeFaceTests.cpp#L1)

## Overview

[`vktImageSampleDrawnCubeFaceTests.cpp`](../../../modules/vulkan/image/vktImageSampleDrawnCubeFaceTests.cpp#L1) implements the `image.sample_cubemap` subgroup registered by the image module. The file tests sampling from rendered cubemap faces, verifying that the sampler correctly reads from cube faces that have been written to via render passes.

## Role of File

Implementation-heavy test file for the `image.sample_cubemap` subgroup.

## Source Code

- Primary source: [vktImageSampleDrawnCubeFaceTests.cpp](../../../modules/vulkan/image/vktImageSampleDrawnCubeFaceTests.cpp#L1)
- Parent-category registration: `createImageSampleDrawnCubeFaceTests()` called from image module

## Registration Hierarchy

```text
image.sample_cubemap
└── write_face_0
```

Evidence:
- `sample_cubemap` group created at [`createImageSampleDrawnCubeFaceTests()`](../../../modules/vulkan/image/vktImageSampleDrawnCubeFaceTests.cpp#L583)
- Single test case `write_face_0` added at [`vktImageSampleDrawnCubeFaceTests.cpp#L585`](../../../modules/vulkan/image/vktImageSampleDrawnCubeFaceTests.cpp#L585)

## Test Families

### write_face_0 �?Sample from cubemap face 0 with surrounding face sampling

The `write_face_0` test renders to cubemap face 0 and samples the surrounding 4 faces (+Y, -Y, +Z, -Z) to verify cubemap sampling works correctly.

Test sequence:
1. First pass: Render pure magenta (R=1, G=0, B=1) to face 0
2. Sample the 4 faces around face 0 using texture coordinates (x, 1, y), (x, -1, y), (x, y, 1), (x, y, -1)
3. Average the 4 samples and add to face 0
4. Second pass: Render pure cyan (R=0, G=1, B=1) to face 0
5. Sample again and verify: R should be 0 (from averaged samples), G should be > 0 (from second pass)

Verification logic at [`vktImageSampleDrawnCubeFaceTests.cpp#L476-483`](../../../modules/vulkan/image/vktImageSampleDrawnCubeFaceTests.cpp#L476):
- Red component must equal 0
- Green component must be > 0

## Test Architecture

The test uses two graphics pipelines:
- Pipeline 1 (write): Renders solid colors to cubemap face
- Pipeline 2 (sample): Samples cubemap and writes to target image

Shader details from [`SampleDrawnCubeFaceTest::initPrograms()`](../../../modules/vulkan/image/vktImageSampleDrawnCubeFaceTests.cpp#L519-568):

**Pipeline 1 Fragment Shader:**
- Push constant `pass` toggles between magenta (pass 0) and cyan (pass 1)

**Pipeline 2 Fragment Shader:**
- Samples cubemap 4 times using directions derived from UV coordinates
- Averages samples and outputs to framebuffer

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Cubemap face size | 8x8 pixels at [`vktImageSampleDrawnCubeFaceTests.cpp#L581`](../../../modules/vulkan/image/vktImageSampleDrawnCubeFaceTests.cpp#L581) |
| Format | VK_FORMAT_R8G8B8A8_UNORM at [`vktImageSampleDrawnCubeFaceTests.cpp#L580`](../../../modules/vulkan/image/vktImageSampleDrawnCubeFaceTests.cpp#L580) |
| Layer count | 6 (full cubemap) at [`vktImageSampleDrawnCubeFaceTests.cpp#L249`](../../../modules/vulkan/image/vktImageSampleDrawnCubeFaceTests.cpp#L249) |
| Buffer size | 1024 bytes at [`vktImageSampleDrawnCubeFaceTests.cpp#L246`](../../../modules/vulkan/image/vktImageSampleDrawnCubeFaceTests.cpp#L246) |

## Support / Feature Requirements

- No explicit feature requirements documented
- Standard cubemap support implied by VK_IMAGE_VIEW_TYPE_CUBE usage
- All image usage flags (TRANSFER_SRC, TRANSFER_DST, COLOR_ATTACHMENT, INPUT_ATTACHMENT, SAMPLED) at [`vktImageSampleDrawnCubeFaceTests.cpp#L73-75`](../../../modules/vulkan/image/vktImageSampleDrawnCubeFaceTests.cpp#L73)

## Verification Methods

- Two-pass rendering with color validation
- Per-pixel check: R must be 0, G must be > 0 at [`vktImageSampleDrawnCubeFaceTests.cpp#L476-483`](../../../modules/vulkan/image/vktImageSampleDrawnCubeFaceTests.cpp#L476)
- Result image logged to test output for visual verification at [`vktImageSampleDrawnCubeFaceTests.cpp#L486-489`](../../../modules/vulkan/image/vktImageSampleDrawnCubeFaceTests.cpp#L486)
- Sample averaging: 4 cubemap samples averaged and divided by 4 at [`vktImageSampleDrawnCubeFaceTests.cpp#L558-562`](../../../modules/vulkan/image/vktImageSampleDrawnCubeFaceTests.cpp#L558)

## Test Principles Observed

- Tests the complete rendering and sampling pipeline for cubemaps
- Verifies that rendered content is correctly readable via sampler
- Uses simple color validation rather than complex texture comparison
- Tests multi-pass to verify accumulated sampling works correctly

## Notes / Uncertainties

- Only tests face 0 with sampling directions limited to ±Y and ±Z; other combinations are not tested
- Fixed small size (8x8) may miss edge cases
- Single format (R8G8B8A8_UNORM) limits coverage
- Only one test case exists in the subgroup, providing limited coverage
- The test does not verify blue channel, only R and G
- No validation that face layout is correct (assumes standard cubemap face ordering)
