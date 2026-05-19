# vktTessellationWindingTests.cpp

## Overview

[`vktTessellationWindingTests.cpp`](../../../modules/vulkan/tessellation/vktTessellationWindingTests.cpp#L1) registers [`winding`](../../../modules/vulkan/tessellation/vktTessellationWindingTests.cpp#L610-L624), testing clockwise/counter-clockwise layout qualifiers and domain origin.

## Role

Implementation file.

## Source Code

- Primary source: [`vktTessellationWindingTests.cpp`](../../../modules/vulkan/tessellation/vktTessellationWindingTests.cpp#L1)

## Registration Hierarchy

The documented root is [`tessellation.winding`](../../../modules/vulkan/tessellation/vktTessellationWindingTests.cpp#L1).

```text
tessellation.winding
├── default_domain
├── lower_left_domain
└── upper_left_domain
```

## Test Families

### default_domain — Winding

[`populateWindingGroup()`](../../../modules/vulkan/tessellation/vktTessellationWindingTests.cpp#L582-L604) combines triangle/quad primitives, GLSL/HLSL, winding modes, and Y-flip variants.

## Parameter Dimensions

Parameters are domain origin, primitive type, shader language, winding, and Y-flip.

## Support / Feature Requirements

Domain origin use may require portability or functionality support checks; unsupported functionality throws [`NotSupportedError`](../../../modules/vulkan/tessellation/vktTessellationWindingTests.cpp#L402-L403).

## Verification Methods

[`verifyResultImage()`](../../../modules/vulkan/tessellation/vktTessellationWindingTests.cpp#L84-L109) counts red/white pixels to confirm whether the expected primitive is visible.

## Test Principles Observed
- Case generation is table- or loop-driven in the registration function.
- Verification is tied to observed rendered, queried, or buffered results.

## Notes / Uncertainties

- This page summarizes behavior observed in inspected tessellation source files; deeper generated cases are described where visible in source loops or arrays.
