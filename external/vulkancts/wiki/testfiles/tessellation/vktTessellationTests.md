# vktTessellationTests.cpp

## Overview

[`vktTessellationTests.cpp`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L25) is the top-level dispatcher for the [`tessellation`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L47) category. It includes subgroup headers and registers the category children in [`createChildren()`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L64-L81).

## Role

Registration / dispatcher file.

## Source Code

- Primary source: [`vktTessellationTests.cpp`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L1)

## Registration Hierarchy

This file contributes the [`tessellation`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L1) registration path.

```text
tessellation
├── common_edge
├── fractional_spacing
├── geometry_interaction
├── invariance
├── limits
├── matrix_multiplication
├── misc_draw
├── primitive_discard
├── shader_input_output
├── tess_io
├── tesscoord
├── user_defined_io
└── winding
```

## Test Families

### common_edge — Common Edge

[`common_edge`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L73) is registered directly by the dispatcher and is implemented by [`createCommonEdgeTests()`](../../../modules/vulkan/tessellation/vktTessellationCommonEdgeTests.cpp#L495-L514).

### fractional_spacing — Fractional Spacing

[`fractional_spacing`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L74) is registered directly by the dispatcher and is implemented by [`createFractionalSpacingTests()`](../../../modules/vulkan/tessellation/vktTessellationFractionalSpacingTests.cpp#L763-L774).

### geometry_interaction — Geometry Interaction

[`geometry_interaction`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L78) is assembled locally from passthrough, grid-render limit, scatter, and point-size implementation factories in [`createGeometryInteractionTests()`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L52-L61).

### invariance — Invariance

[`invariance`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L76) is registered directly by the dispatcher and is implemented by [`createInvarianceTests()`](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L2438-L2512).

### limits — Limits

[`limits`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L68) is registered directly by the dispatcher and is implemented by [`createLimitsTests()`](../../../modules/vulkan/tessellation/vktTessellationLimitsTests.cpp#L117-L141).

### matrix_multiplication — Matrix Multiplication

[`matrix_multiplication`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L80) is registered directly by the dispatcher and is implemented by [`createTessellationMatrixMultiplicationTests()`](../../../modules/vulkan/tessellation/vktTessellationMatrixMultiplicationTests.cpp#L368-L375).

### misc_draw — Misc Draw

[`misc_draw`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L72) is registered directly by the dispatcher and is implemented by [`createMiscDrawTests()`](../../../modules/vulkan/tessellation/vktTessellationMiscDrawTests.cpp#L1859-L2084).

### primitive_discard — Primitive Discard

[`primitive_discard`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L75) is registered directly by the dispatcher and is implemented by [`createPrimitiveDiscardTests()`](../../../modules/vulkan/tessellation/vktTessellationPrimitiveDiscardTests.cpp#L626-L650).

### shader_input_output — Shader Input Output

[`shader_input_output`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L71) is registered directly by the dispatcher and is implemented by [`createShaderInputOutputTests()`](../../../modules/vulkan/tessellation/vktTessellationShaderInputOutputTests.cpp#L974-L1085).

### tess_io — Tess Io

[`tess_io`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L79) is registered directly by the dispatcher and is implemented by [`createTessIOTests()`](../../../modules/vulkan/tessellation/vktTessellationMaxIOTests.cpp#L1800-L1988).

### tesscoord — Tesscoord

[`tesscoord`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L69) is registered directly by the dispatcher and is implemented by [`createCoordinatesTests()`](../../../modules/vulkan/tessellation/vktTessellationCoordinatesTests.cpp#L871-L886).

### user_defined_io — User Defined Io

[`user_defined_io`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L77) is registered directly by the dispatcher and is implemented by [`createUserDefinedIOTests()`](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L1031-L1087).

### winding — Winding

[`winding`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L70) is registered directly by the dispatcher and is implemented by [`createWindingTests()`](../../../modules/vulkan/tessellation/vktTessellationWindingTests.cpp#L610-L624).

## Parameter Dimensions

This dispatcher does not define parameter matrices; it delegates to implementation files registered from [`createChildren()`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L64-L81).

## Support / Feature Requirements

No support checks are implemented here; subgroup implementations and [`requireFeatures()`](../../../modules/vulkan/tessellation/vktTessellationUtil.cpp#L802-L824) perform feature gating.

## Verification Methods

No verification logic is implemented here; subgroup files perform image, SSBO, limit, or shader-result validation.

## Test Principles Observed
- The file separates category structure from implementation logic through factory functions in [`createChildren()`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L64-L81).
- The [`geometry_interaction`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L52-L61) subgroup is assembled locally from multiple implementation files.

## Notes / Uncertainties

- The page summarizes behavior observed in the inspected tessellation source files and does not infer additional generated cases beyond visible loops, arrays, or mustpass-confirmed paths.
