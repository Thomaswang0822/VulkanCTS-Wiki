# vktTessellationMaxIOTests.cpp

## Overview

[`vktTessellationMaxIOTests.cpp`](../../../modules/vulkan/tessellation/vktTessellationMaxIOTests.cpp#L1) registers [`tess_io`](../../../modules/vulkan/tessellation/vktTessellationMaxIOTests.cpp#L1800-L1988), containing maximum IO and tessellation-level IO tests.

## Role

Implementation file.

## Source Code

- Primary source: [`vktTessellationMaxIOTests.cpp`](../../../modules/vulkan/tessellation/vktTessellationMaxIOTests.cpp#L1)

## Registration Hierarchy

The documented root is [`tessellation.tess_io`](../../../modules/vulkan/tessellation/vktTessellationMaxIOTests.cpp#L1).

```text
tessellation.tess_io
├── level_io
└── max_in_out
```

## Test Families

### level_io — Tess Io

[`max_in_out`](../../../modules/vulkan/tessellation/vktTessellationMaxIOTests.cpp#L1805-L1943) uses required-feature groups, random permutations, and TCS/TES read/write modes; [`level_io`](../../../modules/vulkan/tessellation/vktTessellationMaxIOTests.cpp#L1947-L1985) reads and writes inner/outer tessellation levels.

## Parameter Dimensions

Parameters include owner, data type, bit width, dimension, interpolation, required feature group, permutation index, TCS/TES read mode, and tessellation level operation.

## Support / Feature Requirements

[`MaxIOTest::checkSupport()`](../../../modules/vulkan/tessellation/vktTessellationMaxIOTests.cpp#L851-L987) requires tessellation, multi-viewport, optional float/int width features, float16/storage16 support, and SPIR-V version suitability; [`LevelIOTest::checkSupport()`](../../../modules/vulkan/tessellation/vktTessellationMaxIOTests.cpp#L1621-L1625) requires tessellation and multi-viewport.

## Verification Methods

[`tcu::floatThresholdCompare()`](../../../modules/vulkan/tessellation/vktTessellationMaxIOTests.cpp#L1152-L1153) compares rendered images; level IO uses reference and verification buffers around [`LevelIOTestInstance`](../../../modules/vulkan/tessellation/vktTessellationMaxIOTests.cpp#L1769-L1786).

## Test Principles Observed
- Case generation is table- or loop-driven in the registration function.
- Verification is tied to observed rendered, queried, or buffered results.

## Notes / Uncertainties

- This page summarizes behavior observed in inspected tessellation source files; deeper generated cases are described where visible in source loops or arrays.
