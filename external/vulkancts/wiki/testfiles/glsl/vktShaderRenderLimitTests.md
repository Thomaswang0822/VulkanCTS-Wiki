# vktShaderRenderLimitTests.cpp

## Overview

[`vktShaderRenderLimitTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLimitTests.cpp#L1) registers the `glsl.limits` subtree for ShaderRenderCase-based GLSL tests. The implemented family targets near-threshold vertex-output and fragment-input interface budgets by generating vertex outputs and matching fragment inputs from a requested component-count value, then rendering a green-or-red result image according to whether the fragment shader observed the expected values.

## Role

Registration and implementation-heavy test file. The GLSL package registers this file's group through [`createGlslTests()`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1263), and `createLimitTests()` constructs the `limits`, `near_max`, and `fragment_input` groups in [`vktShaderRenderLimitTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLimitTests.cpp#L241-L260). `FragmentInputComponentCase` generates the shaders and performs per-case limit checks, while `FragmentInputComponentCaseInstance` supplies the quad input, renders, and compares the result image.

## Source Code

- Primary source: [`vktShaderRenderLimitTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLimitTests.cpp#L1)
- Header: [`vktShaderRenderLimitTests.hpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLimitTests.hpp#L29-L35)
- GLSL package registration: [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1215-L1263)
- Root package attachment for Vulkan and Vulkan SC: [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1345-L1354) and [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1416-L1422)
- Shared render harness: [`vktShaderRender.cpp`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L637-L808) and [`vktShaderRender.cpp`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L1899-L1907)

## Registration Hierarchy

```text
glsl.limits
└── near_max
```

## Test Families

### near_max — Fragment input interface budget near fixed thresholds

The `near_max` child is created under the `limits` group in [`createLimitTests()`](../../../modules/vulkan/shaderrender/vktShaderRenderLimitTests.cpp#L241-L260). Its direct implementation subgroup is `fragment_input`, and that subgroup receives one `FragmentInputComponentCase` per generated `components_N` name at [`vktShaderRenderLimitTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLimitTests.cpp#L246-L257).

For each case, the vertex shader assigns `gl_Position = a_position`, declares user output variables named `o_colorN`, and assigns each variable a constructor filled with its zero-based location index at [`FragmentInputComponentCase::initPrograms()`](../../../modules/vulkan/shaderrender/vktShaderRenderLimitTests.cpp#L131-L140) and [`vktShaderRenderLimitTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLimitTests.cpp#L198-L201). The fragment shader declares matching `i_colorN` inputs, increments `errorCount` for values that do not exactly equal the same constructor value, and outputs green when no mismatches are found or red otherwise at [`vktShaderRenderLimitTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLimitTests.cpp#L142-L154) and [`vktShaderRenderLimitTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLimitTests.cpp#L202-L205).

The source comment states that the requested component budget is treated as inclusive of built-ins, so `gl_Position` leaves `m_inputComponents - 4` user-specified output components for the generated interface at [`vktShaderRenderLimitTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLimitTests.cpp#L156-L170). The implementation then derives a number of user locations with `ceil((m_inputComponents - 4) / 4)` and emits one varying declaration per location at [`vktShaderRenderLimitTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLimitTests.cpp#L171-L206).

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Registered root and subgroup names | `limits`, `near_max`, and `fragment_input` are constructed as `TestCaseGroup` names at [`createLimitTests()`](../../../modules/vulkan/shaderrender/vktShaderRenderLimitTests.cpp#L241-L247). |
| Threshold seeds | `fragmentComponentMaxLimits[] = {64u, 128u, 256u}` at [`vktShaderRenderLimitTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLimitTests.cpp#L248-L250). |
| Generated case names and requested values | The nested loops subtract `5`, `4`, `3`, `2`, and `1` from each threshold, producing `components_59` through `components_63`, `components_123` through `components_127`, and `components_251` through `components_255` at [`vktShaderRenderLimitTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLimitTests.cpp#L251-L257). |
| Shader interface locations | `maxLocations` is computed from `(m_inputComponents - 4) / 4`, rounded up, before declarations are emitted for locations `0 .. maxLocations - 1` at [`vktShaderRenderLimitTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLimitTests.cpp#L171-L206). |
| Varying type selection | Non-final locations use `vec4`; the final location can be `float`, `vec2`, `vec3`, or `vec4` depending on the switch expression in [`vktShaderRenderLimitTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLimitTests.cpp#L176-L196). |
| Draw geometry | Six vertex positions are uploaded as a location-0 `VK_FORMAT_R32G32B32A32_SFLOAT` attribute at [`setupDefaultInputs()`](../../../modules/vulkan/shaderrender/vktShaderRenderLimitTests.cpp#L98-L104), and rendering uses 12 indices for four triangles at [`iterate()`](../../../modules/vulkan/shaderrender/vktShaderRenderLimitTests.cpp#L76-L80). |

## Support / Feature Requirements

| Requirement | Evidence |
|---|---|
| Fragment input component limit | `createInstance()` reads `maxFragmentInputComponents` and throws `NotSupportedError` when `m_inputComponents` is greater than the reported limit at [`vktShaderRenderLimitTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLimitTests.cpp#L212-L226). |
| Vertex output component limit | The same method reads `maxVertexOutputComponents`; because the source treats `gl_Position` as an output component, it rejects cases where `m_inputComponents + 4` exceeds the reported vertex-output limit at [`vktShaderRenderLimitTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLimitTests.cpp#L227-L235). |
| No additional feature gate in this file | The inspected implementation does not define a separate `checkSupport()` method or extension/feature checks beyond the two physical-device limit comparisons in [`createInstance()`](../../../modules/vulkan/shaderrender/vktShaderRenderLimitTests.cpp#L212-L237). |

## Verification Methods

- `iterate()` calls `setup()`, renders the indexed quad, copies the render target into a result surface, and builds a solid green reference image at [`vktShaderRenderLimitTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLimitTests.cpp#L66-L87).
- The fragment shader is the first-stage oracle for varying correctness: it compares every generated input variable with its expected constructor value, accumulates `errorCount`, and writes green for zero errors or red otherwise at [`vktShaderRenderLimitTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLimitTests.cpp#L142-L154) and [`vktShaderRenderLimitTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLimitTests.cpp#L202-L205).
- Host-side pass/fail is a rendered-image comparison against the solid green reference using `tcu::pixelThresholdCompare()` with `tcu::RGBA(2, 2, 2, 2)`; a matching image returns pass and a mismatch returns fail at [`vktShaderRenderLimitTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLimitTests.cpp#L71-L95).

## Test Principles

- The file uses generated shader source, not hand-written per-case shader files, so the case name and requested component budget drive both limit checks and shader interface declaration count at [`vktShaderRenderLimitTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLimitTests.cpp#L109-L118) and [`vktShaderRenderLimitTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLimitTests.cpp#L171-L206).
- The tested budgets intentionally sit just below the fixed threshold seeds from the source array, with five generated values per threshold at [`vktShaderRenderLimitTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLimitTests.cpp#L248-L257).
- Correctness is reduced to a visible green/red render result: shader-side equality checks decide the output color, and the harness only accepts an image matching the green reference within a small per-channel threshold at [`vktShaderRenderLimitTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLimitTests.cpp#L89-L95) and [`vktShaderRenderLimitTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLimitTests.cpp#L147-L153).

## Notes / Uncertainties

- The source comment describes the component budget as inclusive of `gl_Position`, and the implementation generates user-defined varying locations from `m_inputComponents - 4`; therefore this page avoids claiming that each `components_N` case declares exactly `N` fragment input components in shader source.
- No separate helper file registers additional `limits` subgroups in the inspected source; the group returned by `createLimitTests()` contains only `near_max` as its direct child at [`vktShaderRenderLimitTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLimitTests.cpp#L241-L261).
