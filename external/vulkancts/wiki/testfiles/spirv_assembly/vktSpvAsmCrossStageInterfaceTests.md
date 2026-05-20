# vktSpvAsmCrossStageInterfaceTests

## Overview

Tests for cross-stage shader interface passing in SPIR-V Assembly, verifying correct data transmission between vertex, tessellation, geometry, and fragment shader stages. Tests cover flat, no_perspective, and relaxedprecision interpolation qualifiers on basic types and interface blocks.

## Role

Implementation file

## Source

- [vktSpvAsmCrossStageInterfaceTests.cpp](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp)

## Registration Hierarchy

```text
spirv_assembly.instruction.graphics.cross_stage
├── basic_type
└── interface_blocks
```

## Test Families

### basic_type — Basic type cross-stage interface tests

Tests cross-stage interface passing of basic types (scalar float, vec2, vec3, vec4) with different interpolation qualifiers. Uses `CrossStageBasicTestsCase` test class. Tests three qualifiers:

- **flat**: Flat interpolation (no interpolation, takes provoking vertex value). Tests decoration placement in vertex only, fragment only, and all shaders — vktSpvAsmCrossStageInterfaceTests.cpp#L2724-L2729
- **no_perspective**: No perspective interpolation. Same decoration placement variations as flat — vktSpvAsmCrossStageInterfaceTests.cpp#L2731-L2733
- **relaxedprecision**: RelaxedPrecision decoration. Only tests `DECORATION_IN_ALL_SHADERS` option — vktSpvAsmCrossStageInterfaceTests.cpp#L2737-L2740

Observed in `createCrossStageInterfaceTests()` at vktSpvAsmCrossStageInterfaceTests.cpp#L2721-L2742.

### interface_blocks — Interface block cross-stage interface tests

Tests cross-stage interface passing using interface blocks (structs with OpMemberDecorate) instead of individual variables. Uses `CrossStageInterfaceTestsCase` test class. Same three qualifiers as basic_type:

- **flat**: Flat decoration on interface block members — vktSpvAsmCrossStageInterfaceTests.cpp#L2729
- **no_perspective**: NoPerspective decoration on interface block members — vktSpvAsmCrossStageInterfaceTests.cpp#L2733
- **relaxedprecision**: RelaxedPrecision decoration on interface block members — vktSpvAsmCrossStageInterfaceTests.cpp#L2740

Observed in `createCrossStageInterfaceTests()` at vktSpvAsmCrossStageInterfaceTests.cpp#L2722-L2743.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| TestType (qualifier) | `flat`, `no_perspective`, `relaxedprecision` | Interpolation/decoration qualifier |
| Decoration placement | `DECORATION_IN_VERTEX` (0), `DECORATION_IN_FRAGMENT` (1), `DECORATION_IN_ALL_SHADERS` (2) | Where the decoration is applied |
| Pipeline stages | VF, VTF, VGF, VTGF | Shader stage combinations (V=vertex, T=tessellation, G=geometry, F=fragment) |

For `flat` and `no_perspective`, all 3 decoration placement options are tested (3 testOptions). For `relaxedprecision`, only `DECORATION_IN_ALL_SHADERS` is tested (1 testOption) — vktSpvAsmCrossStageInterfaceTests.cpp#L2724-L2740.

## Support Requirements

- **tessellationShader** — required for tessellation control/evaluation stages — checked at runtime at vktSpvAsmCrossStageInterfaceTests.cpp#L187
- **geometryShader** — required for geometry stage — checked at runtime at vktSpvAsmCrossStageInterfaceTests.cpp#L188
- Pipeline stages are dynamically selected based on device feature support — vktSpvAsmCrossStageInterfaceTests.cpp#L262-L275

## Verification Methods

- **Image comparison**: Renders to a 51x51 color attachment and compares against a reference image using `checkImage()` — vktSpvAsmCrossStageInterfaceTests.cpp#L167
- Reference images are generated based on qualifier type:
  - **flat**: `interpolationFill` (reference1) and `redFill` (reference2) — vktSpvAsmCrossStageInterfaceTests.cpp#L281-L284
  - **no_perspective**: `perspectiveFill` (reference1) and `interpolationFill` (reference2) — vktSpvAsmCrossStageInterfaceTests.cpp#L286-L289
  - **relaxedprecision**: `interpolationFill` for both references — vktSpvAsmCrossStageInterfaceTests.cpp#L291-L294
- For `flat`/`no_perspective` with `DECORATION_IN_VERTEX`, comparison uses reference1; for other decoration placements with VF-only pipeline, comparison uses reference2; for multi-stage pipelines, a negative test (expected fail) is used — vktSpvAsmCrossStageInterfaceTests.cpp#L369-L379

## Notes

- The test dynamically adapts to device capabilities by selecting pipeline stage combinations based on tessellation and geometry shader support
- For `flat` and `no_perspective` qualifiers, tests with decoration only in the fragment shader and multi-stage pipelines are expected to fail (negative tests) — vktSpvAsmCrossStageInterfaceTests.cpp#L377-L378
- The `relaxedprecision` qualifier tests always expect pass regardless of decoration placement — vktSpvAsmCrossStageInterfaceTests.cpp#L362-L366
