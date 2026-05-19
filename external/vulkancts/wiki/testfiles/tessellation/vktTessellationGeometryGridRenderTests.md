# vktTessellationGeometryGridRenderTests.cpp

## Overview

[`vktTessellationGeometryGridRenderTests.cpp`](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L1) implements the [`limits`](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L744-L761) child of [`geometry_interaction`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L52-L61).

## Role

Implementation file.

## Source Code

- Primary source: [`vktTessellationGeometryGridRenderTests.cpp`](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L1)

## Registration Hierarchy

The documented root is [`tessellation.geometry_interaction.limits`](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L1).

```text
tessellation.geometry_interaction.limits
├── output_required_max_geometry
├── output_required_max_invocations
└── output_required_max_tessellation
```

## Test Families

### output_required_max_geometry — Required grid-render limits

Cases render near required tessellation/geometry limits from [`cases[]`](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L749-L756).

## Parameter Dimensions

Parameters are `FLAG_TESSELLATION_MAX_SPEC`, `FLAG_GEOMETRY_MAX_SPEC`, and `FLAG_GEOMETRY_INVOCATIONS_MAX_SPEC` from [`FlagBits`](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L65-L76).

## Support / Feature Requirements

The tests require tessellation/geometry functionality through generated pipeline stages and shared feature checks.

## Verification Methods

[`verifyResultLayer()`](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L578-L603) validates expected layer colors.

## Test Principles Observed
- Case generation is table- or loop-driven in the registration function.
- Verification is tied to observed rendered, queried, or buffered results.

## Notes / Uncertainties

- This page summarizes behavior observed in inspected tessellation source files; deeper generated cases are described where visible in source loops or arrays.
