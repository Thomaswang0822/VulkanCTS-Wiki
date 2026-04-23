# vktGeometryTests.cpp

## Overview

[`vktGeometryTests.cpp`](../../modules/vulkan/geometry/vktGeometryTests.cpp#L1) is the registration file for the top-level [`geometry`](../../modules/vulkan/geometry/vktGeometryTests.cpp#L36) category. Its role is to assemble the category subtree by delegating to the implementation files for each major geometry-shader test area.

## Role

Registration / dispatcher file.

## Source Code

- Primary source: [`vktGeometryTests.cpp`](../../modules/vulkan/geometry/vktGeometryTests.cpp#L1)
- Related headers included for subgroup creation:
  - [`vktGeometryBasicGeometryShaderTests.hpp`](../../modules/vulkan/geometry/vktGeometryTests.cpp#L25)
  - [`vktGeometryInputGeometryShaderTests.hpp`](../../modules/vulkan/geometry/vktGeometryTests.cpp#L26)
  - [`vktGeometryLayeredRenderingTests.hpp`](../../modules/vulkan/geometry/vktGeometryTests.cpp#L27)
  - [`vktGeometryInstancedRenderingTests.hpp`](../../modules/vulkan/geometry/vktGeometryTests.cpp#L28)
  - [`vktGeometryVaryingGeometryShaderTests.hpp`](../../modules/vulkan/geometry/vktGeometryTests.cpp#L29)
  - [`vktGeometryEmitGeometryShaderTests.hpp`](../../modules/vulkan/geometry/vktGeometryTests.cpp#L30)
  - [`vktGeometryBuiltinVariableGeometryShaderTests.hpp`](../../modules/vulkan/geometry/vktGeometryTests.cpp#L31)

## Registration Path

The category entry point is [`createTests()`](../../modules/vulkan/geometry/vktGeometryTests.cpp#L56), which builds a test group via [`createTestGroup()`](../../modules/vulkan/geometry/vktGeometryTests.cpp#L58). The actual child registration happens in [`createChildren()`](../../modules/vulkan/geometry/vktGeometryTests.cpp#L41).

## Test Hierarchy

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

Source: [`createChildren()`](../../modules/vulkan/geometry/vktGeometryTests.cpp#L41).

## Registered Subgroups

| Subgroup | Registration call | Implementing source |
|---|---|---|
| `input` | [`createInputGeometryShaderTests()`](../../modules/vulkan/geometry/vktGeometryTests.cpp#L45) | [`vktGeometryInputGeometryShaderTests.cpp`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L260) |
| `basic` | [`createBasicGeometryShaderTests()`](../../modules/vulkan/geometry/vktGeometryTests.cpp#L46) | [`vktGeometryBasicGeometryShaderTests.cpp`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L1000) |
| `layered` | [`createLayeredRenderingTests()`](../../modules/vulkan/geometry/vktGeometryTests.cpp#L47) | Inspected through [`vktGeometryLayeredRenderingTests.cpp`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L62) |
| `instanced` | [`createInstancedRenderingTests()`](../../modules/vulkan/geometry/vktGeometryTests.cpp#L48) | [`vktGeometryInstancedRenderingTests.cpp`](../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L423) |
| `varying` | [`createVaryingGeometryShaderTests()`](../../modules/vulkan/geometry/vktGeometryTests.cpp#L49) | [`vktGeometryVaryingGeometryShaderTests.cpp`](../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L273) |
| `emit` | [`createEmitGeometryShaderTests()`](../../modules/vulkan/geometry/vktGeometryTests.cpp#L50) | [`vktGeometryEmitGeometryShaderTests.cpp`](../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L226) |
| `builtin_variable` | [`createBuiltinVariableGeometryShaderTests()`](../../modules/vulkan/geometry/vktGeometryTests.cpp#L51) | [`vktGeometryBuiltinVariableGeometryShaderTests.cpp`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp#L428) |

## Test Families

This file does not implement individual test logic itself. Instead, it defines the top-level family split of the geometry category:

1. **Input primitive handling** via [`input`](../../modules/vulkan/geometry/vktGeometryTests.cpp#L45)
2. **Basic geometry expansion and output-count behavior** via [`basic`](../../modules/vulkan/geometry/vktGeometryTests.cpp#L46)
3. **Layered rendering** via [`layered`](../../modules/vulkan/geometry/vktGeometryTests.cpp#L47)
4. **Instanced rendering with GS invocations** via [`instanced`](../../modules/vulkan/geometry/vktGeometryTests.cpp#L48)
5. **Varying propagation** via [`varying`](../../modules/vulkan/geometry/vktGeometryTests.cpp#L49)
6. **Emit/end primitive sequencing** via [`emit`](../../modules/vulkan/geometry/vktGeometryTests.cpp#L50)
7. **Built-in variable behavior** via [`builtin_variable`](../../modules/vulkan/geometry/vktGeometryTests.cpp#L51)

## Parameter Dimensions

This file is a dispatcher and does not define its own parameter structs or value ranges. Parameterization is delegated to subgroup implementation files such as:
- [`PrimitiveTestSpec`](../../modules/vulkan/geometry/vktGeometryTestsUtil.hpp#L47) for input-related tests
- [`TestParams`](../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L58) for instanced tests
- [`TestParams`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L82) for layered tests
- [`EmitTestSpec`](../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L71) for emit tests

## Support / Feature Requirements

No support checks are implemented in this file. Support gating is delegated to subgroup-specific implementations such as [`GeometryExpanderRenderTest::checkSupport()`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp#L134), [`VaryingTest::checkSupport()`](../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp#L125), and [`BuiltinVariableRenderTest::checkSupport()`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp#L194).

## Verification Methods

No verification logic is implemented in this file. Verification is delegated to subgroup files.

## Test Principles Observed

- **Explicit hierarchical registration**: the category tree is assembled by named subgroup factory calls in [`createChildren()`](../../modules/vulkan/geometry/vktGeometryTests.cpp#L41)
- **Separation of concerns**: this file registers structure, while other files implement test generation and verification
- **Category-level navigability**: the subgroup list provides the high-level organization of geometry-shader coverage

## Notes / Uncertainties

- The subgroup name is [`builtin_variable`](../../modules/vulkan/geometry/vktGeometryTests.cpp#L51), not `builtin`; any wiki summary should preserve the actual registration name.
