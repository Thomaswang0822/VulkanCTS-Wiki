# vktTessellationGeometryPassthroughTests.cpp

## Overview

[`vktTessellationGeometryPassthroughTests.cpp`](../../../modules/vulkan/tessellation/vktTessellationGeometryPassthroughTests.cpp#L1) implements the [`passthrough`](../../../modules/vulkan/tessellation/vktTessellationGeometryPassthroughTests.cpp#L767-L781) child of [`geometry_interaction`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L52-L61).

## Role

Implementation file.

## Source Code

- Primary source: [`vktTessellationGeometryPassthroughTests.cpp`](../../../modules/vulkan/tessellation/vktTessellationGeometryPassthroughTests.cpp#L1)

## Registration Hierarchy

The documented root is [`tessellation.geometry_interaction.passthrough`](../../../modules/vulkan/tessellation/vktTessellationGeometryPassthroughTests.cpp#L1).

```text
tessellation.geometry_interaction.passthrough
├── passthrough_tessellation_geometry_shade_isolines_no_change
├── passthrough_tessellation_geometry_shade_triangles_no_change
├── tessellate_isolines_passthrough_geometry_no_change
├── tessellate_quads_passthrough_geometry_no_change
└── tessellate_triangles_passthrough_geometry_no_change
```

## Test Families

### passthrough_tessellation_geometry_shade_isolines_no_change — Passthrough comparisons

Cases compare pipelines with passthrough geometry or passthrough tessellation shaders for triangles, quads, and isolines in [`createGeometryPassthroughTests()`](../../../modules/vulkan/tessellation/vktTessellationGeometryPassthroughTests.cpp#L772-L779).

## Parameter Dimensions

Parameters include primitive type and whether the passthrough stage is geometry or tessellation evaluation/control.

## Support / Feature Requirements

Support requires tessellation and geometry shader features through [`requireFeatures()`](../../../modules/vulkan/tessellation/vktTessellationGeometryPassthroughTests.cpp#L160-L163).

## Verification Methods

Rendered pipeline results are compared with [`tcu::floatThresholdCompare()`](../../../modules/vulkan/tessellation/vktTessellationGeometryPassthroughTests.cpp#L665).

## Test Principles Observed
- Case generation is table- or loop-driven in the registration function.
- Verification is tied to observed rendered, queried, or buffered results.

## Notes / Uncertainties

- This page summarizes behavior observed in inspected tessellation source files; deeper generated cases are described where visible in source loops or arrays.
