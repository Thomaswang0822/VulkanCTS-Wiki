# vktTessellationCoordinatesTests.cpp

## Overview

[`vktTessellationCoordinatesTests.cpp`](../../../modules/vulkan/tessellation/vktTessellationCoordinatesTests.cpp#L1) registers [`tesscoord`](../../../modules/vulkan/tessellation/vktTessellationCoordinatesTests.cpp#L871-L886), comparing generated tessellation coordinates against reference coordinates.

## Role

Implementation file.

## Source Code

- Primary source: [`vktTessellationCoordinatesTests.cpp`](../../../modules/vulkan/tessellation/vktTessellationCoordinatesTests.cpp#L1)

## Registration Hierarchy

The documented root is [`tessellation.tesscoord`](../../../modules/vulkan/tessellation/vktTessellationCoordinatesTests.cpp#L1).

```text
tessellation.tesscoord
├── isolines_equal_spacing
├── isolines_equal_spacing_execution_mode_in_tesc
├── isolines_fractional_even_spacing
├── isolines_fractional_even_spacing_execution_mode_in_tesc
├── isolines_fractional_odd_spacing
├── isolines_fractional_odd_spacing_execution_mode_in_tesc
├── quads_equal_spacing
├── quads_equal_spacing_execution_mode_in_tesc
├── quads_fractional_even_spacing
├── quads_fractional_even_spacing_execution_mode_in_tesc
├── quads_fractional_odd_spacing
├── quads_fractional_odd_spacing_execution_mode_in_tesc
├── triangles_equal_spacing
├── triangles_equal_spacing_execution_mode_in_tesc
├── triangles_fractional_even_spacing
├── triangles_fractional_even_spacing_execution_mode_in_tesc
├── triangles_fractional_odd_spacing
└── triangles_fractional_odd_spacing_execution_mode_in_tesc
```

## Test Families

### isolines_* — Isoline coordinate cases

Isoline cases are created by the primitive loop in [`createCoordinatesTests()`](../../../modules/vulkan/tessellation/vktTessellationCoordinatesTests.cpp#L875-L884).

### quads_* — Quad coordinate cases

Quad cases combine spacing modes with the execution-mode-in-TCS toggle from [`TessCoordTest`](../../../modules/vulkan/tessellation/vktTessellationCoordinatesTests.cpp#L390-L395).

### triangles_* — Triangle coordinate cases

Triangle cases use reference coordinates generated from explicit levels in [`rawTessLevelCases[]`](../../../modules/vulkan/tessellation/vktTessellationCoordinatesTests.cpp#L82-L87).

## Parameter Dimensions

Parameters include primitive type, spacing mode, raw tessellation levels, and whether execution mode is declared in the evaluation shader or only in the control shader.

## Support / Feature Requirements

Portability-subset point-mode and primitive support checks are performed in [`TessCoordTest::checkSupport()`](../../../modules/vulkan/tessellation/vktTessellationCoordinatesTests.cpp#L399-L406). Tessellation feature support is handled by shared tessellation setup.

## Verification Methods

[`compareTessCoords()`](../../../modules/vulkan/tessellation/vktTessellationCoordinatesTests.cpp#L330-L347) performs bidirectional point-set comparison and logs coordinate visualizations on failure.

## Test Principles Observed
- Case generation is table- or loop-driven in the registration function.
- Verification is tied to observed rendered, queried, or buffered results.

## Notes / Uncertainties

- This page summarizes behavior observed in inspected tessellation source files; deeper generated cases are described where visible in source loops or arrays.
