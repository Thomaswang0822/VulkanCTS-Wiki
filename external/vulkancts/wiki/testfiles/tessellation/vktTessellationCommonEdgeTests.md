# vktTessellationCommonEdgeTests.cpp

## Overview

[`vktTessellationCommonEdgeTests.cpp`](../../../modules/vulkan/tessellation/vktTessellationCommonEdgeTests.cpp#L1) registers [`common_edge`](../../../modules/vulkan/tessellation/vktTessellationCommonEdgeTests.cpp#L495-L514), checking adjacent tessellated shapes for cracks.

## Role

Implementation file.

## Source Code

- Primary source: [`vktTessellationCommonEdgeTests.cpp`](../../../modules/vulkan/tessellation/vktTessellationCommonEdgeTests.cpp#L1)

## Registration Hierarchy

The documented root is [`tessellation.common_edge`](../../../modules/vulkan/tessellation/vktTessellationCommonEdgeTests.cpp#L1).

```text
tessellation.common_edge
├── quads_equal_spacing
├── quads_equal_spacing_precise
├── quads_fractional_even_spacing
├── quads_fractional_even_spacing_precise
├── quads_fractional_odd_spacing
├── quads_fractional_odd_spacing_precise
├── triangles_equal_spacing
├── triangles_equal_spacing_precise
├── triangles_fractional_even_spacing
├── triangles_fractional_even_spacing_precise
├── triangles_fractional_odd_spacing
└── triangles_fractional_odd_spacing_precise
```

## Test Families

### quads_equal_spacing — Common Edge

Cases combine triangle/quad primitive types, spacing modes, and standard/precise variants from [`createCommonEdgeTests()`](../../../modules/vulkan/tessellation/vktTessellationCommonEdgeTests.cpp#L498-L514).

## Parameter Dimensions

Parameters are primitive type, spacing mode, and precision case type.

## Support / Feature Requirements

Tessellation support is required through shared program/test setup.

## Verification Methods

[`verifyResult()`](../../../modules/vulkan/tessellation/vktTessellationCommonEdgeTests.cpp#L78) validates rendered output after image readback at [`iterate()`](../../../modules/vulkan/tessellation/vktTessellationCommonEdgeTests.cpp#L479).

## Test Principles Observed
- Case generation is table- or loop-driven in the registration function.
- Verification is tied to observed rendered, queried, or buffered results.

## Notes / Uncertainties

- This page summarizes behavior observed in inspected tessellation source files; deeper generated cases are described where visible in source loops or arrays.
