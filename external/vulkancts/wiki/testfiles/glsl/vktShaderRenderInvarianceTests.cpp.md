# Shader Invariance and Precise Decoration Tests

## Overview

Tests for the GLSL `invariant` and `precise` decorations, verifying that values marked with these decorations produce identical results across shader invocations even when the compiler might otherwise reorder or optimize expressions differently. Uses a dual-shader rendering comparison approach where two vertex shaders (one with unrelated computation that could affect optimization, one without) must produce pixel-identical output.

## Role

Both registration and implementation. Two separate test group creation functions (`createShaderInvarianceTests` and `createShaderPreciseTests`) each produce a `tcu::TestCaseGroup`. Both use the `InvarianceTest` class for test case implementation. The `addBasicTests` function populates both groups with common test cases, while `addExtendedInstructionsTests` adds additional cases only to the `precise` group.

## Source Code

[../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L1-L1143)

## Registration Hierarchy

### glsl.invariance

```text
glsl.invariance
├── mediump
└── highp
```

### glsl.precise

```text
glsl.precise
├── mediump
├── highp
└── extended_instructions
```

## Test Families

- **InvarianceTest** - Dual-shader rendering comparison test. Renders the same geometry twice with different vertex shaders: one that shares a subexpression with an unrelated output variable (which could cause the compiler to reorder or optimize differently), and one that zeroes out the unrelated variable. Both shaders use the same fragment shader. If the decoration (`invariant` or `precise`) is correctly implemented, the outputs must be pixel-identical.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Decoration | invariant, precise | The GLSL decoration under test |
| Precision | mediump, highp | Precision qualifier for the tested variable |
| Variable type | gl_position, user_defined | Whether the decorated variable is `gl_Position` or a user-defined varying |
| Extended instruction type | smoothstep, normalize, reflect, exp, etc. | Built-in function used in the precise extended instruction tests |

### Extended Instruction Types (precise group only)

The `extended_instructions` subgroup tests precise behavior with specific GLSL built-in functions:
- `smoothstep` - With cross-precision combinations for the unrelated variable
- `normalize` - Vector normalization with precise decoration
- `reflect` - Vector reflection with precise decoration
- `exp` - Exponential function with precise decoration
- Additional built-in operations

## Support/Feature Requirements

No additional requirements beyond core Vulkan.

## Verification Methods

- **Dual-shader rendering comparison**: The test renders the same scene twice using two different vertex shaders:
  1. **Shader 1**: Contains an unrelated computation that shares a subexpression with the decorated variable. The shared subexpression uses high-magnitude values that could cause precision loss if the compiler reorders operations.
  2. **Shader 2**: The unrelated computation is replaced with a zero assignment, eliminating any potential for shared subexpression optimization interference.
- Both renders use the same fragment shader that combines the unrelated variable with a uniform color.
- The two rendered images are compared using `tcu::pixelThresholdCompare` to verify pixel-identical output. If the `invariant` or `precise` decoration is correctly respected by the compiler, the results must match exactly regardless of the presence of unrelated computations.

## Notes

- The `lowp` precision is defined in the precisions array but is not used as a direct child group in the registration hierarchy. The basic tests iterate over `mediump` and `highp` precision groups.
- The `invariance` group only calls `addBasicTests` with the `"invariant"` decoration, while the `precise` group calls both `addBasicTests` with `"precise"` and `addExtendedInstructionsTests` with `"precise"`.
- Each precision group contains `gl_position` and `user_defined` subgroups, which in turn contain multiple test cases with different subexpression sharing patterns (common_subexpression_0 through common_subexpression_3, and loop-based variants).
- The test uses high-magnitude literal values (e.g., 1.0e20 for highp, 1.0e4 for mediump) to create conditions where compiler expression reordering could produce different results if the decoration is not properly enforced.
