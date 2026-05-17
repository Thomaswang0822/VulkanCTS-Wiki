# vktDrawDifferingInterpolationTests.cpp

## Overview

Tests for mismatching interpolation decorations between vertex and fragment shader stages. When the interpolation qualifier (e.g., `flat`, `noperspective`) differs between the vertex output and the fragment input, the Vulkan specification defines specific behavior. These tests verify that rendering results are consistent regardless of which stage carries the qualifier, by comparing images produced with different qualifier placements.

## Role

Validates that implementations correctly handle differing interpolation decorations on vertex-fragment interface variables. The tests render the same geometry twice: once with the qualifier on one stage and once on the other stage (or with no qualifier on one side). The resulting images must match, confirming that the implementation treats the interpolation consistently regardless of which shader stage declares the qualifier.

## Source Code

- [vktDrawDifferingInterpolationTests.cpp](../../../modules/vulkan/draw/vktDrawDifferingInterpolationTests.cpp)

## Registration Hierarchy

```text
draw.renderpass.differing_interpolation
├── flat_0
├── flat_1
├── noperspective_0
└── noperspective_1
```

## Test Families

### flat_0 — No qualifier on vertex, flat on fragment

Renders a triangle twice and compares the results. The first pass uses a vertex shader with no interpolation qualifier and a fragment shader with the `flat` qualifier. The reference pass uses both vertex and fragment shaders with the `flat` qualifier. The images should match because `flat` interpolation on the fragment side dominates the behavior.

**Shader configuration**: vert=`vert`, frag=`fragFlatColor`; ref vert=`vertFlatColor`, ref frag=`fragFlatColor`

**Test class**: [DrawTestCase](../../../modules/vulkan/draw/vktDrawDifferingInterpolationTests.cpp#L101) / [DrawTestInstance](../../../modules/vulkan/draw/vktDrawDifferingInterpolationTests.cpp#L67)

### flat_1 — Flat on vertex, no qualifier on fragment

Renders a triangle twice and compares the results. The first pass uses a vertex shader with the `flat` qualifier and a fragment shader with no qualifier. The reference pass uses both vertex and fragment shaders with no qualifier. The images should match because the fragment input's lack of qualifier (smooth) takes precedence over the vertex output's `flat`, and the reference also uses smooth interpolation.

**Shader configuration**: vert=`vertFlatColor`, frag=`frag`; ref vert=`vert`, ref frag=`frag`

**Test class**: [DrawTestCase](../../../modules/vulkan/draw/vktDrawDifferingInterpolationTests.cpp#L101) / [DrawTestInstance](../../../modules/vulkan/draw/vktDrawDifferingInterpolationTests.cpp#L67)

### noperspective_0 — No qualifier on vertex, noperspective on fragment

Renders a triangle twice and compares the results. The first pass uses a vertex shader with no interpolation qualifier and a fragment shader with the `noperspective` qualifier. The reference pass uses both vertex and fragment shaders with the `noperspective` qualifier. The images should match.

**Shader configuration**: vert=`vert`, frag=`fragNoPerspective`; ref vert=`vertNoPerspective`, ref frag=`fragNoPerspective`

**Test class**: [DrawTestCase](../../../modules/vulkan/draw/vktDrawDifferingInterpolationTests.cpp#L101) / [DrawTestInstance](../../../modules/vulkan/draw/vktDrawDifferingInterpolationTests.cpp#L67)

### noperspective_1 — Noperspective on vertex, no qualifier on fragment

Renders a triangle twice and compares the results. The first pass uses a vertex shader with the `noperspective` qualifier and a fragment shader with no qualifier. The reference pass uses both vertex and fragment shaders with no qualifier. The images should match.

**Shader configuration**: vert=`vertNoPerspective`, frag=`frag`; ref vert=`vert`, ref frag=`frag`

**Test class**: [DrawTestCase](../../../modules/vulkan/draw/vktDrawDifferingInterpolationTests.cpp#L101) / [DrawTestInstance](../../../modules/vulkan/draw/vktDrawDifferingInterpolationTests.cpp#L67)

**Registration**: [createTests](../../../modules/vulkan/draw/vktDrawDifferingInterpolationTests.cpp#L461)

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| interpolation | `flat`, `noperspective` | The interpolation qualifier being tested |
| mismatchSide | 0, 1 | Which stage has the mismatching qualifier (0=vertex missing, 1=fragment missing) |

## Support Requirements

| Requirement | Condition | Source |
|-------------|-----------|--------|
| `VK_KHR_dynamic_rendering` | When using dynamic rendering variant | [checkSupport](../../../modules/vulkan/draw/vktDrawDifferingInterpolationTests.cpp#L163-L165) |

## Verification Methods

| Method | Description | Source |
|--------|-------------|--------|
| Integer threshold comparison | `tcu::intThresholdCompare` with `UVec4(0)` threshold between the two rendered images (test and reference). A zero-threshold integer comparison ensures exact pixel match between the two passes. | [iterate](../../../modules/vulkan/draw/vktDrawDifferingInterpolationTests.cpp#L394-L396) |

## Notes

- The test renders a single triangle with position and color attributes. The color is passed through the vertex-fragment interface with varying interpolation qualifiers.
- The vertex shader template uses `tcu::StringTemplate` with a `${qualifier:opt}` placeholder that is specialized to empty, `flat`, or `noperspective`.
- The comparison is between two rendered frames (not against a software reference), so the test validates consistency rather than absolute correctness.
- The render target is 256x256 with `VK_FORMAT_R8G8B8A8_UNORM`.
