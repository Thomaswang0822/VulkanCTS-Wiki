# vktSpvAsmCrossStageInterfaceTests

## Overview

Tests cross-stage shader interface passing in SPIR-V assembly, verifying correct data transmission between vertex, tessellation, geometry, and fragment shader stages. Tests cover [`flat`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L2724-L2729), [`no_perspective`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L2731-L2733), and [`relaxedprecision`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L2737-L2740) qualifier scenarios on basic types and interface blocks.

## Role

Implementation file

## Source

- [vktSpvAsmCrossStageInterfaceTests.cpp](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L2717)

## Registration Hierarchy

```text
spirv_assembly.instruction.graphics.cross_stage
├── basic_type
└── interface_blocks
```

## Test Families

### basic_type — Basic type cross-stage interface tests

Tests cross-stage interface passing of basic types with different interpolation qualifiers. Uses [`CrossStageBasicTestsCase`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L2728) test cases. Tests three qualifiers:

- **flat**: Flat interpolation. The source creates three decoration-placement options and adds the `flat` basic-type case in [`createCrossStageInterfaceTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L2724-L2729).
- **no_perspective**: No-perspective interpolation. The source reuses the same decoration-placement options and adds the `no_perspective` basic-type case in [`createCrossStageInterfaceTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L2731-L2733).
- **relaxedprecision**: RelaxedPrecision decoration. The source creates only the `DECORATION_IN_ALL_SHADERS` option before adding the `relaxedprecision` basic-type case in [`createCrossStageInterfaceTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L2737-L2740).

Observed in [`createCrossStageInterfaceTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L2717-L2743).

### interface_blocks — Interface block cross-stage interface tests

Tests cross-stage interface passing using interface blocks instead of individual variables. Uses [`CrossStageInterfaceTestsCase`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L2729) test cases. Same three qualifier scenarios as `basic_type`:

- **flat**: Flat decoration on interface block members, added beside the basic-type `flat` case in [`createCrossStageInterfaceTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L2724-L2729).
- **no_perspective**: NoPerspective decoration on interface block members, added in [`createCrossStageInterfaceTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L2731-L2733).
- **relaxedprecision**: RelaxedPrecision decoration on interface block members, added with only `DECORATION_IN_ALL_SHADERS` in [`createCrossStageInterfaceTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L2737-L2740).

Observed in [`createCrossStageInterfaceTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L2717-L2743).

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| TestType (qualifier) | `flat`, `no_perspective`, `relaxedprecision` | Interpolation/decoration qualifier registered in [`createCrossStageInterfaceTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L2724-L2740) |
| Decoration placement | `DECORATION_IN_VERTEX` (0), `DECORATION_IN_FRAGMENT` (1), `DECORATION_IN_ALL_SHADERS` (2) | Where the decoration is applied; the first two qualifier families iterate through all decoration options in [`parm.testOptions`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L2724-L2726), while relaxed precision uses only `DECORATION_IN_ALL_SHADERS` at the first [`parm.testOptions`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L2737-L2738) slot |
| Pipeline stages | VF, VTF, VGF, VTGF | Shader stage combinations selected at runtime from device support in [`shadersStagesFlagsBits`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L262-L275) |

For `flat` and `no_perspective`, all three decoration placement options are tested. For `relaxedprecision`, only `DECORATION_IN_ALL_SHADERS` is tested, as shown in [`createCrossStageInterfaceTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L2724-L2740).

## Support / Feature Requirements

- **tessellationShader** — queried from device features in [`CrossStageTestInstance::iterate()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L186-L188) and used to add tessellation stage combinations at [`shadersStagesFlagsBits`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L264-L275).
- **geometryShader** — queried from device features in [`CrossStageTestInstance::iterate()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L186-L188) and used to add geometry stage combinations at [`shadersStagesFlagsBits`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L268-L275).
- Pipeline stages are dynamically selected based on device feature support in [`CrossStageTestInstance::iterate()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L262-L275).

## Verification Methods

- **Image comparison**: Renders to a `51x51` color attachment and compares against a reference image using [`checkImage()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L167-L168).
- Reference images are generated based on qualifier type:
  - **flat**: [`interpolationFill()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L281-L283) for `referenceImage1` and [`redFill()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L281-L283) for `referenceImage2`.
  - **no_perspective**: [`perspectiveFill()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L285-L288) for `referenceImage1` and [`interpolationFill()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L285-L288) for `referenceImage2`.
  - **relaxedprecision**: [`interpolationFill()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L289-L291) for both references.
- For `flat`/`no_perspective` with `DECORATION_IN_VERTEX`, comparison uses `referenceImage1`; for other decoration placements with the VF-only pipeline, comparison uses `referenceImage2`; for multi-stage pipelines, a negative test inverts `checkImage()` against `referenceImage1`, as shown in the comparison logic in [`CrossStageTestInstance::iterate()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L369-L378).

## Notes

- The test dynamically adapts to device capabilities by selecting pipeline stage combinations based on tessellation and geometry shader support in [`CrossStageTestInstance::iterate()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L262-L275).
- For `flat` and `no_perspective` qualifiers, tests with decoration only in the fragment shader and multi-stage pipelines are expected to fail by negating the image comparison result in [`CrossStageTestInstance::iterate()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L377-L378).
- The `relaxedprecision` qualifier tests compare as expected pass regardless of decoration placement in the source branch at [`TEST_TYPE_RELAXEDPRECISION`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L361-L366).
