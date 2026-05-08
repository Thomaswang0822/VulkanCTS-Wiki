# vktGeometryTests.cpp

## Overview

[`vktGeometryTests.cpp`](../../../modules/vulkan/geometry/vktGeometryTests.cpp#L1) is the registration file for the top-level [`geometry`](../../../modules/vulkan/geometry/vktGeometryTests.cpp#L36) category. Its role is to assemble the category subtree by delegating to the implementation files for each major geometry-shader test area.

## Role

Registration / dispatcher file.

## Source Code

- Primary source: [`vktGeometryTests.cpp`](../../../modules/vulkan/geometry/vktGeometryTests.cpp#L1)
- Related headers included for subgroup creation:
  - [`vktGeometryBasicGeometryShaderTests.hpp`](../../../modules/vulkan/geometry/vktGeometryTests.cpp#L25)
  - [`vktGeometryInputGeometryShaderTests.hpp`](../../../modules/vulkan/geometry/vktGeometryTests.cpp#L26)
  - [`vktGeometryLayeredRenderingTests.hpp`](../../../modules/vulkan/geometry/vktGeometryTests.cpp#L27)
  - [`vktGeometryInstancedRenderingTests.hpp`](../../../modules/vulkan/geometry/vktGeometryTests.cpp#L28)
  - [`vktGeometryVaryingGeometryShaderTests.hpp`](../../../modules/vulkan/geometry/vktGeometryTests.cpp#L29)
  - [`vktGeometryEmitGeometryShaderTests.hpp`](../../../modules/vulkan/geometry/vktGeometryTests.cpp#L30)
  - [`vktGeometryBuiltinVariableGeometryShaderTests.hpp`](../../../modules/vulkan/geometry/vktGeometryTests.cpp#L31)

## Registration Hierarchy

The category entry point is [`createTests()`](../../../modules/vulkan/geometry/vktGeometryTests.cpp#L56), which builds a test group via [`createTestGroup()`](../../../modules/vulkan/geometry/vktGeometryTests.cpp#L58). The actual child registration happens in [`createChildren()`](../../../modules/vulkan/geometry/vktGeometryTests.cpp#L41).

```text
geometry
├── input
├── basic
├── layered
├── instanced
├── varying
├── emit
└── builtin_variable
```

Source: [`createChildren()`](../../../modules/vulkan/geometry/vktGeometryTests.cpp#L41).

## Registered Subgroups

| Group Name | Source |
|---|---|
| `input` | [`vktGeometryInputGeometryShaderTests.cpp`](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L1) |
| `basic` | [`vktGeometryBasicGeometryShaderTests.cpp`](../../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L1) |
| `layered` | [`vktGeometryLayeredRenderingTests.cpp`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L1) |
| `instanced` | [`vktGeometryInstancedRenderingTests.cpp`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L1) |
| `varying` | [`vktGeometryVaryingGeometryShaderTests.cpp`](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L1) |
| `emit` | [`vktGeometryEmitGeometryShaderTests.cpp`](../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L1) |
| `builtin_variable` | [`vktGeometryBuiltinVariableGeometryShaderTests.cpp`](../../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp#L1) |

## Test Families

### input — Input primitive handling

[`input`](../../../modules/vulkan/geometry/vktGeometryTests.cpp#L45) delegates to [`vktGeometryInputGeometryShaderTests.cpp`](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L1), which covers primitive topology handling, adjacency variants, and primitive-type conversion.

### basic — Basic geometry expansion and output-count behavior

[`basic`](../../../modules/vulkan/geometry/vktGeometryTests.cpp#L46) delegates to [`vktGeometryBasicGeometryShaderTests.cpp`](../../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L1), which covers fixed output counts, runtime-varying output counts, and side-effect-focused geometry shader cases.

### layered — Layered rendering

[`layered`](../../../modules/vulkan/geometry/vktGeometryTests.cpp#L47) delegates to [`vktGeometryLayeredRenderingTests.cpp`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L1), which covers geometry-shader-controlled layered rendering, per-layer content variation, readback, and secondary-command-buffer behavior.

### instanced — Instanced rendering with GS invocations

[`instanced`](../../../modules/vulkan/geometry/vktGeometryTests.cpp#L48) delegates to [`vktGeometryInstancedRenderingTests.cpp`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L1), which combines draw instancing with geometry-shader invocation counts.

### varying — Varying propagation

[`varying`](../../../modules/vulkan/geometry/vktGeometryTests.cpp#L49) delegates to [`vktGeometryVaryingGeometryShaderTests.cpp`](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L1), which focuses on cross-stage varying production and forwarding behavior.

### emit — Emit/end primitive sequencing

[`emit`](../../../modules/vulkan/geometry/vktGeometryTests.cpp#L50) delegates to [`vktGeometryEmitGeometryShaderTests.cpp`](../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L1), which varies [`EmitVertex()`](../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L199) and [`EndPrimitive()`](../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L204) sequencing.

### builtin_variable — Built-in variable behavior

[`builtin_variable`](../../../modules/vulkan/geometry/vktGeometryTests.cpp#L51) delegates to [`vktGeometryBuiltinVariableGeometryShaderTests.cpp`](../../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp#L1), which covers point size, primitive ID, and position-oriented built-in behavior.

## Parameter Dimensions

This file is a dispatcher and does not define its own parameter structs or value ranges. Parameterization is delegated to subgroup implementation files such as:
- [`PrimitiveTestSpec`](../../../modules/vulkan/geometry/vktGeometryTestsUtil.hpp#L47) for input-related tests
- [`TestParams`](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L58) for instanced tests
- [`TestParams`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L82) for layered tests
- [`EmitTestSpec`](../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L71) for emit tests

## Support / Feature Requirements

No support checks are implemented in this file. Support gating is delegated to subgroup-specific implementations such as [`GeometryExpanderRenderTest::checkSupport()`](../../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L134), [`VaryingTest::checkSupport()`](../../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L125), and [`BuiltinVariableRenderTest::checkSupport()`](../../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp#L194).

## Verification Methods

No verification logic is implemented in this file. Verification is delegated to subgroup files.

## Test Principles Observed

- **Explicit hierarchical registration**: the category tree is assembled by named subgroup factory calls in [`createChildren()`](../../../modules/vulkan/geometry/vktGeometryTests.cpp#L41)
- **Separation of concerns**: this file registers structure, while other files implement test generation and verification
- **Category-level navigability**: the subgroup list provides the high-level organization of geometry-shader coverage

## Notes / Uncertainties

- The subgroup name is [`builtin_variable`](../../../modules/vulkan/geometry/vktGeometryTests.cpp#L51), not `builtin`; any wiki summary should preserve the actual registration name.
