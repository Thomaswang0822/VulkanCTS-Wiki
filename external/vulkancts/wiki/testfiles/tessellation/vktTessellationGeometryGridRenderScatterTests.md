# vktTessellationGeometryGridRenderScatterTests.cpp

## Overview

[`vktTessellationGeometryGridRenderTests.cpp`](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L1) also implements the [`scatter`](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L765-L782) child of [`geometry_interaction`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L52-L61).

## Role

Implementation file.

## Source Code

- Primary source: [`vktTessellationGeometryGridRenderTests.cpp`](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L1)

## Registration Hierarchy

The documented root is [`tessellation.geometry_interaction.scatter`](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L1).

```text
tessellation.geometry_interaction.scatter
├── geometry_scatter_instances
├── geometry_scatter_layers
└── geometry_scatter_primitives
```

## Test Families

### geometry_scatter_instances — Scatter cases

Cases scatter geometry output by instances, primitives, or layers from [`cases[]`](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L770-L777).

## Parameter Dimensions

Parameters are scatter flags for instances, primitives, separate primitives, and layers from [`FlagBits`](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L65-L76).

## Support / Feature Requirements

The tests require tessellation/geometry functionality through generated pipeline stages and shared feature checks.

## Verification Methods

[`verifyResultLayer()`](../../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L578-L603) validates expected layer colors.

## Test Principles Observed
- Case generation is table- or loop-driven in the registration function.
- Verification is tied to observed rendered, queried, or buffered results.

## Notes / Uncertainties

- This page summarizes behavior observed in inspected tessellation source files; deeper generated cases are described where visible in source loops or arrays.
