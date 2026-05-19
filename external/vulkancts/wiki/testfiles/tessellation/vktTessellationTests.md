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

[`common_edge`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L68-L80) is registered directly or via the synthetic [`geometry_interaction`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L52-L61) subgroup.

### fractional_spacing — Fractional Spacing

[`fractional_spacing`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L68-L80) is registered directly or via the synthetic [`geometry_interaction`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L52-L61) subgroup.

### geometry_interaction — Geometry Interaction

[`geometry_interaction`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L68-L80) is registered directly or via the synthetic [`geometry_interaction`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L52-L61) subgroup.

### invariance — Invariance

[`invariance`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L68-L80) is registered directly or via the synthetic [`geometry_interaction`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L52-L61) subgroup.

### limits — Limits

[`limits`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L68-L80) is registered directly or via the synthetic [`geometry_interaction`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L52-L61) subgroup.

### matrix_multiplication — Matrix Multiplication

[`matrix_multiplication`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L68-L80) is registered directly or via the synthetic [`geometry_interaction`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L52-L61) subgroup.

### misc_draw — Misc Draw

[`misc_draw`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L68-L80) is registered directly or via the synthetic [`geometry_interaction`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L52-L61) subgroup.

### primitive_discard — Primitive Discard

[`primitive_discard`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L68-L80) is registered directly or via the synthetic [`geometry_interaction`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L52-L61) subgroup.

### shader_input_output — Shader Input Output

[`shader_input_output`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L68-L80) is registered directly or via the synthetic [`geometry_interaction`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L52-L61) subgroup.

### tess_io — Tess Io

[`tess_io`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L68-L80) is registered directly or via the synthetic [`geometry_interaction`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L52-L61) subgroup.

### tesscoord — Tesscoord

[`tesscoord`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L68-L80) is registered directly or via the synthetic [`geometry_interaction`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L52-L61) subgroup.

### user_defined_io — User Defined Io

[`user_defined_io`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L68-L80) is registered directly or via the synthetic [`geometry_interaction`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L52-L61) subgroup.

### winding — Winding

[`winding`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L68-L80) is registered directly or via the synthetic [`geometry_interaction`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L52-L61) subgroup.

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
