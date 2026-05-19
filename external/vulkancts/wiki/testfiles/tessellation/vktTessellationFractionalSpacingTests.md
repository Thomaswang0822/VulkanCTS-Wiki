# vktTessellationFractionalSpacingTests.cpp

## Overview

[`vktTessellationFractionalSpacingTests.cpp`](../../../modules/vulkan/tessellation/vktTessellationFractionalSpacingTests.cpp#L1) registers [`fractional_spacing`](../../../modules/vulkan/tessellation/vktTessellationFractionalSpacingTests.cpp#L763-L774), validating fractional odd/even spacing.

## Role

Implementation file.

## Source Code

- Primary source: [`vktTessellationFractionalSpacingTests.cpp`](../../../modules/vulkan/tessellation/vktTessellationFractionalSpacingTests.cpp#L1)

## Registration Hierarchy

The documented root is [`tessellation.fractional_spacing`](../../../modules/vulkan/tessellation/vktTessellationFractionalSpacingTests.cpp#L1).

```text
tessellation.fractional_spacing
├── glsl_even
├── glsl_odd
├── hlsl_even
└── hlsl_odd
```

## Test Families

### glsl_even — Fractional Spacing

Four direct cases combine shader language and fractional spacing mode in [`createFractionalSpacingTests()`](../../../modules/vulkan/tessellation/vktTessellationFractionalSpacingTests.cpp#L765-L774).

## Parameter Dimensions

Parameters are GLSL/HLSL language and odd/even fractional spacing, with tessellation-level cases consumed by verification helpers.

## Support / Feature Requirements

The cases use [`checkSupportTess`](../../../modules/vulkan/tessellation/vktTessellationFractionalSpacingTests.cpp#L767-L773) as support gate.

## Verification Methods

[`verifyFractionalSpacingSingle()`](../../../modules/vulkan/tessellation/vktTessellationFractionalSpacingTests.cpp#L153) and [`verifyFractionalSpacingMultiple()`](../../../modules/vulkan/tessellation/vktTessellationFractionalSpacingTests.cpp#L303) validate the coordinate spacing properties.

## Test Principles Observed
- Case generation is table- or loop-driven in the registration function.
- Verification is tied to observed rendered, queried, or buffered results.

## Notes / Uncertainties

- This page summarizes behavior observed in inspected tessellation source files; deeper generated cases are described where visible in source loops or arrays.
