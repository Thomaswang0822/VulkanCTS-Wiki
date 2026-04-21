# vktGeometryBuiltinVariableGeometryShaderTests.cpp

## Overview

[`vktGeometryBuiltinVariableGeometryShaderTests.cpp`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:1) implements the [`builtin_variable`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:430) subgroup. It covers selected built-in variables used with geometry shaders: point size, [`gl_PrimitiveIDIn`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:311), [`gl_PrimitiveID`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:338), and a position-focused case implemented through an HLSL geometry shader path.

## Role

Implementation file.

## Source Code

- Primary source: [`vktGeometryBuiltinVariableGeometryShaderTests.cpp`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:1)
- Shared base instance: [`GeometryExpanderRenderTestInstance`](../../modules/vulkan/geometry/vktGeometryBasicClass.hpp:37)
- Related helper declaration: [`checkPointSize()`](../../modules/vulkan/geometry/vktGeometryTestsUtil.hpp:166)

## Registration Path

This file contributes the subgroup returned by [`createBuiltinVariableGeometryShaderTests()`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:428), which is attached under geometry by [`createChildren()`](../../modules/vulkan/geometry/vktGeometryTests.cpp:51).

## Test Hierarchy

```text
builtin_variable
├── in_block
│   ├── point_size
│   ├── primitive_id_in
│   ├── primitive_id_in_restarted
│   └── primitive_id
└── outside_block
    └── position
```

Source: [`createBuiltinVariableGeometryShaderTests()`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:428).

## Test Families

### 1. Point-size handling

The [`point_size`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:435) case uses [`TEST_POINT_SIZE`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:66). The vertex shader passes a per-vertex value via [`v_geom_pointSize`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:217), and the geometry shader writes [`gl_PointSize = v_geom_pointSize[0].x + 1.0`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:279).

### 2. Primitive ID input

The [`primitive_id_in`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:437) case uses [`TEST_PRIMITIVE_ID_IN`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:67). The geometry shader colors output from a small color table indexed by [`gl_PrimitiveIDIn % 4`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:311).

The [`primitive_id_in_restarted`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:439) case reuses the same test type with [`indicesTest = true`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:439), which enables indexed drawing with a primitive-restart marker [`0xFFFF`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:127).

### 3. Primitive ID output

The [`primitive_id`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:441) case uses [`TEST_PRIMITIVE_ID`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:68). The geometry shader derives [`gl_PrimitiveID`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:338) from the input varying, and the fragment shader maps [`gl_PrimitiveID % 4`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:403) to one of four colors.

### 4. Position case

The [`position`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:443) case uses [`TEST_POSITION`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:69). Unlike the GLSL-based cases above, the geometry stage here is emitted as HLSL source beginning at [`struct VSOut`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:350) and appends the three triangle input positions to the output stream.

## Parameter Dimensions

| Parameter | Observed values / source |
|---|---|
| Built-in under test | [`TEST_POINT_SIZE`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:66), [`TEST_PRIMITIVE_ID_IN`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:67), [`TEST_PRIMITIVE_ID`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:68), [`TEST_POSITION`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:69) |
| Indexed/restart mode | Controlled by [`indicesTest`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:77) / [`m_indicesTest`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:85) |
| Primitive topology chosen by test kind | point list / line strip / triangle strip in [`BuiltinVariableRenderTestInstance`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:93) |
| Vertex count | Fixed to [`5`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:105) in [`genVertexAttribData()`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:103) |

## Support / Feature Requirements

Support checking is explicit in [`BuiltinVariableRenderTest::checkSupport()`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:194):
- requires [`DEVICE_CORE_FEATURE_GEOMETRY_SHADER`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:196)
- additionally requires [`DEVICE_CORE_FEATURE_SHADER_TESSELLATION_AND_GEOMETRY_POINT_SIZE`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:199) for the point-size case

## Verification Methods

This file does not define a file-local CPU-side image checker in the inspected range. Instead, it encodes expectations through shader-visible colors and relies on the common geometry render path via [`BuiltinVariableRenderTestInstance`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:73), which derives from [`GeometryExpanderRenderTestInstance`](../../modules/vulkan/geometry/vktGeometryBasicClass.hpp:37).

Observable expectations visible in this file include:
- point-size case outputs constant white through [`v_frag_FragColor = vec4(1.0, 1.0, 1.0, 1.0)`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:280)
- primitive-id-in case colors geometry from the [`colors[4]`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:306) lookup keyed by [`gl_PrimitiveIDIn`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:311)
- primitive-id case colors fragments from [`colors[gl_PrimitiveID % 4]`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:403)
- position case fragment output is fixed yellow at [`fragColor = vec4(1.0, 1.0, 0.0, 1.0)`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:410)

## Test Principles Observed

- **Built-in-specific specialization**: one file-local enum controls which built-in variable behavior the generated shaders exercise
- **Input and output primitive-ID coverage**: the file tests both [`gl_PrimitiveIDIn`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:311) and [`gl_PrimitiveID`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:338)
- **Restart-sensitive coverage**: the primitive-ID-in path is reused with indexed primitive restart enabled through the explicit restart index buffer setup at [`0xFFFF`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:127)
- **Mixed shader-language coverage**: the position case is notable for using an HLSL geometry shader source path at [`sourceCollections.hlslSources.add("geometry")`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:365)

## Notes / Uncertainties

- The exact shared render-path image comparison helper was not part of the inspected snippet set, so this document avoids naming a more specific runtime comparator than the common geometry render path.
