# vktTessellationGeometryPointSizeTests.cpp

## Overview

[`vktTessellationGeometryPointSizeTests.cpp`](../../../modules/vulkan/tessellation/vktTessellationGeometryPointSizeTests.cpp#L1) implements the [`point_size`](../../../modules/vulkan/tessellation/vktTessellationGeometryPointSizeTests.cpp#L468-L489) child of [`geometry_interaction`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L52-L61).

## Role

Implementation file.

## Source Code

- Primary source: [`vktTessellationGeometryPointSizeTests.cpp`](../../../modules/vulkan/tessellation/vktTessellationGeometryPointSizeTests.cpp#L1)

## Registration Hierarchy

The documented root is [`tessellation.geometry_interaction.point_size`](../../../modules/vulkan/tessellation/vktTessellationGeometryPointSizeTests.cpp#L1).

```text
tessellation.geometry_interaction.point_size
├── evaluation_set
├── geometry_set
├── vertex_set
├── vertex_set_control_pass_eval_add_geometry_add
├── vertex_set_evaluation_set
├── vertex_set_evaluation_set_geometry_set
└── vertex_set_geometry_set
```

## Test Families

### vertex_set — Point-size propagation

Cases vary whether vertex, tessellation evaluation, and geometry stages set or add point size using [`caseFlags[]`](../../../modules/vulkan/tessellation/vktTessellationGeometryPointSizeTests.cpp#L472-L480).

## Parameter Dimensions

Parameters are stage flags from [`FlagBits`](../../../modules/vulkan/tessellation/vktTessellationGeometryPointSizeTests.cpp#L62-L69).

## Support / Feature Requirements

[`checkPointSizeRequirements()`](../../../modules/vulkan/tessellation/vktTessellationGeometryPointSizeTests.cpp#L72-L77) checks physical point-size limits; portability point-mode support is checked in [`checkSupportTess()`](../../../modules/vulkan/tessellation/vktTessellationGeometryPointSizeTests.cpp#L452-L462).

## Verification Methods

[`verifyImage()`](../../../modules/vulkan/tessellation/vktTessellationGeometryPointSizeTests.cpp#L115-L140) measures the non-black rasterized area against expected point size.

## Test Principles Observed
- Case generation is table- or loop-driven in the registration function.
- Verification is tied to observed rendered, queried, or buffered results.

## Notes / Uncertainties

- This page summarizes behavior observed in inspected tessellation source files; deeper generated cases are described where visible in source loops or arrays.
