# vktTessellationPrimitiveDiscardTests.cpp

## Overview

[`vktTessellationPrimitiveDiscardTests.cpp`](../../../modules/vulkan/tessellation/vktTessellationPrimitiveDiscardTests.cpp#L1) registers [`primitive_discard`](../../../modules/vulkan/tessellation/vktTessellationPrimitiveDiscardTests.cpp#L626-L650), checking discard behavior when relevant outer levels are non-positive.

## Role

Implementation file.

## Source Code

- Primary source: [`vktTessellationPrimitiveDiscardTests.cpp`](../../../modules/vulkan/tessellation/vktTessellationPrimitiveDiscardTests.cpp#L1)

## Registration Hierarchy

The documented root is [`tessellation.primitive_discard`](../../../modules/vulkan/tessellation/vktTessellationPrimitiveDiscardTests.cpp#L1).

```text
tessellation.primitive_discard
├── isolines_equal_spacing_ccw
├── isolines_equal_spacing_ccw_point_mode
├── isolines_equal_spacing_cw
├── isolines_equal_spacing_cw_point_mode
├── isolines_fractional_even_spacing_ccw
├── isolines_fractional_even_spacing_ccw_point_mode
├── isolines_fractional_even_spacing_cw
├── isolines_fractional_even_spacing_cw_point_mode
├── isolines_fractional_odd_spacing_ccw
├── isolines_fractional_odd_spacing_ccw_point_mode
├── isolines_fractional_odd_spacing_cw
├── isolines_fractional_odd_spacing_cw_point_mode
├── quads_equal_spacing_ccw
├── quads_equal_spacing_ccw_point_mode
├── quads_equal_spacing_cw
├── quads_equal_spacing_cw_point_mode
├── quads_fractional_even_spacing_ccw
├── quads_fractional_even_spacing_ccw_point_mode
├── quads_fractional_even_spacing_cw
├── quads_fractional_even_spacing_cw_point_mode
├── quads_fractional_odd_spacing_ccw
├── quads_fractional_odd_spacing_ccw_point_mode
├── quads_fractional_odd_spacing_ccw_point_mode_valid_levels
├── quads_fractional_odd_spacing_ccw_valid_levels
├── quads_fractional_odd_spacing_cw
├── quads_fractional_odd_spacing_cw_point_mode
├── quads_fractional_odd_spacing_cw_point_mode_valid_levels
├── quads_fractional_odd_spacing_cw_valid_levels
├── triangles_equal_spacing_ccw
├── triangles_equal_spacing_ccw_point_mode
├── triangles_equal_spacing_cw
├── triangles_equal_spacing_cw_point_mode
├── triangles_fractional_even_spacing_ccw
├── triangles_fractional_even_spacing_ccw_point_mode
├── triangles_fractional_even_spacing_cw
├── triangles_fractional_even_spacing_cw_point_mode
├── triangles_fractional_odd_spacing_ccw
├── triangles_fractional_odd_spacing_ccw_point_mode
├── triangles_fractional_odd_spacing_ccw_point_mode_valid_levels
├── triangles_fractional_odd_spacing_ccw_valid_levels
├── triangles_fractional_odd_spacing_cw
├── triangles_fractional_odd_spacing_cw_point_mode
├── triangles_fractional_odd_spacing_cw_point_mode_valid_levels
└── triangles_fractional_odd_spacing_cw_valid_levels
```

## Test Families

### isolines_equal_spacing_ccw — Primitive Discard

Generated names combine primitive type, spacing mode, winding, point mode, and valid-level variants in the registration loops near [`createPrimitiveDiscardTests()`](../../../modules/vulkan/tessellation/vktTessellationPrimitiveDiscardTests.cpp#L629-L650).

## Parameter Dimensions

Parameters are primitive type, spacing mode, winding, point mode, and valid-level variant.

## Support / Feature Requirements

Tessellation support is required by the generated draw programs.

## Verification Methods

[`verifyResultImage()`](../../../modules/vulkan/tessellation/vktTessellationPrimitiveDiscardTests.cpp#L156) checks rendered attributes and primitive counts; fractional-odd count exceptions are explicitly noted in [`iterate()`](../../../modules/vulkan/tessellation/vktTessellationPrimitiveDiscardTests.cpp#L586).

## Test Principles Observed
- Case generation is table- or loop-driven in the registration function.
- Verification is tied to observed rendered, queried, or buffered results.

## Notes / Uncertainties

- This page summarizes behavior observed in inspected tessellation source files; deeper generated cases are described where visible in source loops or arrays.
