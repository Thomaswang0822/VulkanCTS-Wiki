# vktFragmentShadingRatePixelConsistency.cpp

This page documents the `pixel_consistency` branch contributed by [`vktFragmentShadingRatePixelConsistency.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRatePixelConsistency.cpp#L1).

## Overview

The branch verifies consistency of values inside fragment-sized pixel regions for multiple fragment shading rates, sample counts, framebuffer extents, and selected `FragCoord.zw` cases. It is registered only for the renderpass2, monolithic, non-secondary-command-buffer permutation by the parent dispatcher at [`vktFragmentShadingRateTests.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateTests.cpp#L550-L556).

## Role of File

- Implementation-heavy registered subgroup file.
- It creates `TestCaseGroup(testCtx, "pixel_consistency")` at [`vktFragmentShadingRatePixelConsistency.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRatePixelConsistency.cpp#L1285-L1285).

## Registration Hierarchy

```text
fragment_shading_rate.renderpass2.monolithic.pixel_consistency
├── rate_1x1
├── rate_1x2
├── rate_1x4
├── rate_2x1
├── rate_2x2
├── rate_2x4
├── rate_4x1
├── rate_4x2
└── rate_4x4
```

## Test Families

### rate_1x1 — 1 by 1 fragment size

Registered from `shadingRateCases[]` at [`vktFragmentShadingRatePixelConsistency.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRatePixelConsistency.cpp#L1250-L1252).

### rate_1x2 — 1 by 2 fragment size

Registered at [`vktFragmentShadingRatePixelConsistency.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRatePixelConsistency.cpp#L1251-L1253).

### rate_1x4 — 1 by 4 fragment size

Registered at [`vktFragmentShadingRatePixelConsistency.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRatePixelConsistency.cpp#L1252-L1254).

### rate_2x1 — 2 by 1 fragment size

Registered at [`vktFragmentShadingRatePixelConsistency.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRatePixelConsistency.cpp#L1253-L1255).

### rate_2x2 — 2 by 2 fragment size

Registered at [`vktFragmentShadingRatePixelConsistency.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRatePixelConsistency.cpp#L1254-L1256).

### rate_2x4 — 2 by 4 fragment size

Registered at [`vktFragmentShadingRatePixelConsistency.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRatePixelConsistency.cpp#L1256-L1259).

### rate_4x1 — 4 by 1 fragment size

Registered at [`vktFragmentShadingRatePixelConsistency.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRatePixelConsistency.cpp#L1260-L1263).

### rate_4x2 — 4 by 2 fragment size

Registered at [`vktFragmentShadingRatePixelConsistency.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRatePixelConsistency.cpp#L1264-L1267).

### rate_4x4 — 4 by 4 fragment size

Registered at [`vktFragmentShadingRatePixelConsistency.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRatePixelConsistency.cpp#L1268-L1271).

## Parameter Dimensions

Each rate group contains sample-count groups `samples_1`, `samples_2`, `samples_4`, `samples_8`, and `samples_16` at [`vktFragmentShadingRatePixelConsistency.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRatePixelConsistency.cpp#L1274-L1278). Each sample group contains framebuffer extents `extent_1x1`, `extent_4x4`, `extent_33x35`, `extent_151x431`, and `extent_256x256` at [`vktFragmentShadingRatePixelConsistency.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRatePixelConsistency.cpp#L1280-L1283). Extra `_zw_coord` cases are generated only for extents wider than 150 and sample counts 1 or 4 at [`vktFragmentShadingRatePixelConsistency.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRatePixelConsistency.cpp#L1302-L1308).

## Support / Feature Requirements

Per-case support requires `VK_KHR_fragment_shading_rate`, `pipelineFragmentShadingRate`, support for `VK_FORMAT_R32G32_UINT` with the tested usage, the selected sample count, and framebuffer extents no larger than the reported image maximum at [`FSRPixelConsistencyTestCase::checkSupport()`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRatePixelConsistency.cpp#L160-L184).

## Verification Methods

`verifyResult()` scans the copied result image for each component index. It skips uncovered pixels, handles partially outside fragment regions specially when image robustness is present, requires consistent values within interior fragment areas, and fails on mismatches at [`vktFragmentShadingRatePixelConsistency.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRatePixelConsistency.cpp#L359-L425).

## Test Principles

The branch focuses on whether pixels that belong to the same coarse fragment report consistent values across rate, sample-count, and extent combinations, including odd framebuffer extents that create boundary fragments.

## Notes / Uncertainties

This branch is intentionally not registered for dynamic rendering because the parent code notes that subpasses cannot be translated to dynamic rendering.
