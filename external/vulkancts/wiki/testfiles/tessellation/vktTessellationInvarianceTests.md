# vktTessellationInvarianceTests.cpp

## Overview

[`vktTessellationInvarianceTests.cpp`](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L1) registers [`invariance`](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L2438-L2512), covering primitive-set, edge, triangle-set, and coordinate-component invariants.

## Role

Implementation file.

## Source Code

- Primary source: [`vktTessellationInvarianceTests.cpp`](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L1)

## Registration Hierarchy

The documented root is [`tessellation.invariance`](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L1).

```text
tessellation.invariance
├── inner_triangle_set
├── one_minus_tess_coord_component
├── outer_edge_division
├── outer_edge_index_independence
├── outer_edge_symmetry
├── outer_triangle_set
├── primitive_set
├── tess_coord_component_range
└── triangle_set
```

## Test Families

### inner_triangle_set — Invariance

Direct child groups are created in [`createInvarianceTests()`](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L2440-L2511), and generated cases combine primitive type, spacing mode, winding, and point mode.

## Parameter Dimensions

Parameters are primitive type, spacing mode, winding, point mode, and invariant case type.

## Support / Feature Requirements

Support checks call subgroup-specific [`checkSupport()`](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L1137-L1205) paths and shared case support.

## Verification Methods

[`comparePrimitivesExact()`](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L1360), [`compareTriangleSets()`](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L1280-L1355), and [`compareTessCoordRange()`](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L2124) perform observed validation.

## Test Principles Observed
- Case generation is table- or loop-driven in the registration function.
- Verification is tied to observed rendered, queried, or buffered results.

## Notes / Uncertainties

- This page summarizes behavior observed in inspected tessellation source files; deeper generated cases are described where visible in source loops or arrays.
