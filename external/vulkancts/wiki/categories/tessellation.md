# tessellation

## Overview

The [`tessellation`](../../modules/vulkan/tessellation/vktTessellationTests.cpp#L47) category documents Vulkan tessellation shader coverage registered by [`createChildren()`](../../modules/vulkan/tessellation/vktTessellationTests.cpp#L64-L81). Inspected files cover required tessellation limits, generated coordinates, winding/domain-origin behavior, shader input/output built-ins, miscellaneous draw paths, common-edge continuity, fractional spacing, primitive discard, invariance, user-defined IO, geometry-stage interaction, maximum IO usage, and a matrix multiplication regression.

## Registration Entry Point

The category is rooted in [`createTests()`](../../modules/vulkan/tessellation/vktTessellationTests.cpp#L85-L88), with child registration performed in [`createChildren()`](../../modules/vulkan/tessellation/vktTessellationTests.cpp#L64-L81):

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

## File Inventory

| File | Role | Notes |
|---|---|---|
| [`vktTessellationTests.cpp`](../../modules/vulkan/tessellation/vktTessellationTests.cpp#L1) | Registration | Top-level category dispatcher and local `geometry_interaction` group |
| [`vktTessellationLimitsTests.cpp`](../../modules/vulkan/tessellation/vktTessellationLimitsTests.cpp#L1) | Implementation | Required tessellation device limits |
| [`vktTessellationCoordinatesTests.cpp`](../../modules/vulkan/tessellation/vktTessellationCoordinatesTests.cpp#L1) | Implementation | Tessellation coordinate reference matching |
| [`vktTessellationWindingTests.cpp`](../../modules/vulkan/tessellation/vktTessellationWindingTests.cpp#L1) | Implementation | Winding and tessellation domain origin |
| [`vktTessellationShaderInputOutputTests.cpp`](../../modules/vulkan/tessellation/vktTessellationShaderInputOutputTests.cpp#L1) | Implementation | Built-in and cross-invocation shader IO |
| [`vktTessellationMiscDrawTests.cpp`](../../modules/vulkan/tessellation/vktTessellationMiscDrawTests.cpp#L1) | Implementation | Draw modes, instancing, and state switching |
| [`vktTessellationCommonEdgeTests.cpp`](../../modules/vulkan/tessellation/vktTessellationCommonEdgeTests.cpp#L1) | Implementation | Adjacent primitive continuity |
| [`vktTessellationFractionalSpacingTests.cpp`](../../modules/vulkan/tessellation/vktTessellationFractionalSpacingTests.cpp#L1) | Implementation | Fractional odd/even spacing validity |
| [`vktTessellationPrimitiveDiscardTests.cpp`](../../modules/vulkan/tessellation/vktTessellationPrimitiveDiscardTests.cpp#L1) | Implementation | Primitive discard from non-positive levels |
| [`vktTessellationInvarianceTests.cpp`](../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L1) | Implementation | Primitive and coordinate invariance properties |
| [`vktTessellationUserDefinedIO.cpp`](../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L1) | Implementation | User-defined per-patch/per-vertex IO |
| [`vktTessellationGeometryPassthroughTests.cpp`](../../modules/vulkan/tessellation/vktTessellationGeometryPassthroughTests.cpp#L1) | Implementation | Passthrough geometry/tessellation interaction |
| [`vktTessellationGeometryGridRenderTests.cpp`](../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L1) | Implementation | Geometry interaction limits and scatter |
| [`vktTessellationGeometryPointSizeTests.cpp`](../../modules/vulkan/tessellation/vktTessellationGeometryPointSizeTests.cpp#L1) | Implementation | Point-size propagation through tessellation/geometry stages |
| [`vktTessellationMaxIOTests.cpp`](../../modules/vulkan/tessellation/vktTessellationMaxIOTests.cpp#L1) | Implementation | Maximum tessellation IO and tessellation-level IO |
| [`vktTessellationMatrixMultiplicationTests.cpp`](../../modules/vulkan/tessellation/vktTessellationMatrixMultiplicationTests.cpp#L1) | Implementation | TCS matrix multiplication cases |
| [`vktTessellationUtil.cpp`](../../modules/vulkan/tessellation/vktTessellationUtil.cpp#L802-L824) | Helper | Shared feature gates and tessellation utility logic |

## Level-3 Documents

| Source file | Wiki document |
|---|---|
| [`vktTessellationCommonEdgeTests.cpp`](../../modules/vulkan/tessellation/vktTessellationCommonEdgeTests.cpp#L1) | [`vktTessellationCommonEdgeTests.md`](../testfiles/tessellation/vktTessellationCommonEdgeTests.md) |
| [`vktTessellationCoordinatesTests.cpp`](../../modules/vulkan/tessellation/vktTessellationCoordinatesTests.cpp#L1) | [`vktTessellationCoordinatesTests.md`](../testfiles/tessellation/vktTessellationCoordinatesTests.md) |
| [`vktTessellationFractionalSpacingTests.cpp`](../../modules/vulkan/tessellation/vktTessellationFractionalSpacingTests.cpp#L1) | [`vktTessellationFractionalSpacingTests.md`](../testfiles/tessellation/vktTessellationFractionalSpacingTests.md) |
| [`vktTessellationGeometryGridRenderTests.cpp` (`scatter` subgroup)](../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L765-L782) | [`vktTessellationGeometryGridRenderScatterTests.md`](../testfiles/tessellation/vktTessellationGeometryGridRenderScatterTests.md) |
| [`vktTessellationGeometryGridRenderTests.cpp`](../../modules/vulkan/tessellation/vktTessellationGeometryGridRenderTests.cpp#L1) | [`vktTessellationGeometryGridRenderTests.md`](../testfiles/tessellation/vktTessellationGeometryGridRenderTests.md) |
| [`vktTessellationGeometryPassthroughTests.cpp`](../../modules/vulkan/tessellation/vktTessellationGeometryPassthroughTests.cpp#L1) | [`vktTessellationGeometryPassthroughTests.md`](../testfiles/tessellation/vktTessellationGeometryPassthroughTests.md) |
| [`vktTessellationGeometryPointSizeTests.cpp`](../../modules/vulkan/tessellation/vktTessellationGeometryPointSizeTests.cpp#L1) | [`vktTessellationGeometryPointSizeTests.md`](../testfiles/tessellation/vktTessellationGeometryPointSizeTests.md) |
| [`vktTessellationInvarianceTests.cpp`](../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L1) | [`vktTessellationInvarianceTests.md`](../testfiles/tessellation/vktTessellationInvarianceTests.md) |
| [`vktTessellationLimitsTests.cpp`](../../modules/vulkan/tessellation/vktTessellationLimitsTests.cpp#L1) | [`vktTessellationLimitsTests.md`](../testfiles/tessellation/vktTessellationLimitsTests.md) |
| [`vktTessellationMatrixMultiplicationTests.cpp`](../../modules/vulkan/tessellation/vktTessellationMatrixMultiplicationTests.cpp#L1) | [`vktTessellationMatrixMultiplicationTests.md`](../testfiles/tessellation/vktTessellationMatrixMultiplicationTests.md) |
| [`vktTessellationMaxIOTests.cpp`](../../modules/vulkan/tessellation/vktTessellationMaxIOTests.cpp#L1) | [`vktTessellationMaxIOTests.md`](../testfiles/tessellation/vktTessellationMaxIOTests.md) |
| [`vktTessellationMiscDrawTests.cpp`](../../modules/vulkan/tessellation/vktTessellationMiscDrawTests.cpp#L1) | [`vktTessellationMiscDrawTests.md`](../testfiles/tessellation/vktTessellationMiscDrawTests.md) |
| [`vktTessellationPrimitiveDiscardTests.cpp`](../../modules/vulkan/tessellation/vktTessellationPrimitiveDiscardTests.cpp#L1) | [`vktTessellationPrimitiveDiscardTests.md`](../testfiles/tessellation/vktTessellationPrimitiveDiscardTests.md) |
| [`vktTessellationShaderInputOutputTests.cpp`](../../modules/vulkan/tessellation/vktTessellationShaderInputOutputTests.cpp#L1) | [`vktTessellationShaderInputOutputTests.md`](../testfiles/tessellation/vktTessellationShaderInputOutputTests.md) |
| [`vktTessellationTests.cpp`](../../modules/vulkan/tessellation/vktTessellationTests.cpp#L1) | [`vktTessellationTests.md`](../testfiles/tessellation/vktTessellationTests.md) |
| [`vktTessellationUserDefinedIO.cpp`](../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L1) | [`vktTessellationUserDefinedIO.md`](../testfiles/tessellation/vktTessellationUserDefinedIO.md) |
| [`vktTessellationWindingTests.cpp`](../../modules/vulkan/tessellation/vktTessellationWindingTests.cpp#L1) | [`vktTessellationWindingTests.md`](../testfiles/tessellation/vktTessellationWindingTests.md) |

## Subgroup Structure and Major Themes

- [`limits`](../../modules/vulkan/tessellation/vktTessellationLimitsTests.cpp#L117-L141): required minimum tessellation limits.
- [`tesscoord`](../../modules/vulkan/tessellation/vktTessellationCoordinatesTests.cpp#L871-L886): generated coordinate sets across primitive and spacing modes.
- [`winding`](../../modules/vulkan/tessellation/vktTessellationWindingTests.cpp#L610-L624): clockwise/counter-clockwise layout and domain-origin behavior.
- [`shader_input_output`](../../modules/vulkan/tessellation/vktTessellationShaderInputOutputTests.cpp#L974-L1080): built-in variables, patch data, barriers, and cross-invocation values.
- [`misc_draw`](../../modules/vulkan/tessellation/vktTessellationMiscDrawTests.cpp#L1859-L2080): draw variants, indirect draw, instancing, and state switching.
- [`geometry_interaction`](../../modules/vulkan/tessellation/vktTessellationTests.cpp#L52-L61): interaction with geometry shaders through passthrough, grid, scatter, and point-size cases.
- [`tess_io`](../../modules/vulkan/tessellation/vktTessellationMaxIOTests.cpp#L1800-L1988): maximum IO permutations and tessellation-level reads/writes.

## Recurring Parameter Dimensions

| Dimension | Observed examples |
|---|---|
| Primitive type | Triangles, quads, and isolines from loops such as [`createCoordinatesTests()`](../../modules/vulkan/tessellation/vktTessellationCoordinatesTests.cpp#L875-L883) |
| Spacing mode | Equal, fractional-even, and fractional-odd modes in coordinate and invariance loops |
| Winding and point mode | Winding/point-mode nested loops in [`createInvarianceTests()`](../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L2479-L2500) |
| Domain origin | Default/lower-left/upper-left groups in [`createWindingTests()`](../../modules/vulkan/tessellation/vktTessellationWindingTests.cpp#L615-L622) |
| Shader language | GLSL/HLSL variants in winding and fractional-spacing registrations |
| IO type and width | Owner, data type, bit width, vector dimension, interpolation, and feature groups in [`createTessIOTests()`](../../modules/vulkan/tessellation/vktTessellationMaxIOTests.cpp#L1807-L1935) |

## Recurring Support Requirements

The central support gate is tessellation-shader support, checked directly in files such as [`vktTessellationLimitsTests.cpp`](../../modules/vulkan/tessellation/vktTessellationLimitsTests.cpp#L79-L80) and through [`requireFeatures()`](../../modules/vulkan/tessellation/vktTessellationUtil.cpp#L802-L824). Other observed gates include geometry-shader support, shader float/int width features, vertex/fragment stores and atomics, `shaderTessellationAndGeometryPointSize`, portability-subset primitive/point-mode checks, and [`VK_KHR_maintenance2`](../../modules/vulkan/tessellation/vktTessellationMiscDrawTests.cpp#L667-L668) for non-default domain origin.

## Recurring Verification Methods

Observed verification methods include device-limit comparisons, generated coordinate set comparison in [`compareTessCoords()`](../../modules/vulkan/tessellation/vktTessellationCoordinatesTests.cpp#L330-L347), image fuzzy/threshold comparison in draw tests, pixel/color counting for winding and common-edge behavior, exact primitive/triangle-set comparisons in invariance tests, and shader-side comparison status using SSBO or color output in user-defined IO.


## Notes / Uncertainties

- The summary is based on inspected source and mustpass-observed registration paths. Some implementation files generate many deeper cases; Level-3 hierarchy trees intentionally list only one level below each documented root.
