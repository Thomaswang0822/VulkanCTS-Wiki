# vktShaderRenderBuiltinVarTests.cpp

## Overview

[`vktShaderRenderBuiltinVarTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L1) implements the `glsl.builtin_var` group registered from the GLSL root in [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1272). The file covers rendered checks for `gl_FragCoord.xyz`, `gl_FragCoord.w`, `gl_PointCoord`, `gl_FrontFacing`, `gl_FragDepth`, multisample `gl_FragCoord`, and generated shader-input combinations built from builtin, varying, and push-constant inputs.

## Role

Registration / dispatcher file and implementation-heavy test file. The group factory creates `builtin_var`, constructs six direct child groups, fills them with concrete cases, and returns the group at [`createBuiltinVarTests()`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2499-L2690).

## Source Code

- Primary source: [`vktShaderRenderBuiltinVarTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L1)
- Header: [`vktShaderRenderBuiltinVarTests.hpp`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.hpp#L30-L35)
- GLSL root registration: [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1272)

## Registration Hierarchy

```text
glsl.builtin_var
├── frontfacing
├── fragdepth
├── fragcoord_msaa
├── fragcoord_msaa_input
├── simple
└── input_variations
```

## Test Families

### frontfacing — `gl_FrontFacing` by topology, culling, and optional UBO load

The `frontfacing` group is constructed as a direct child of `builtin_var` at [`createBuiltinVarTests()`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2504-L2505) and attached at [`vktShaderRenderBuiltinVarTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2676-L2677). It has two generated subgroups, `none` and `add_ubo_load`, selected by the `addUboLoad` loop at [`vktShaderRenderBuiltinVarTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2598-L2622).

Each subgroup iterates point, line, triangle-list, triangle-strip, and triangle-fan registered names from `frontfacingCases[]` at [`vktShaderRenderBuiltinVarTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2570-L2585). The `none` branch adds a single `simple` case under each topology, while `add_ubo_load` adds the cull-mode cases `none`, `front`, `back`, and `front_and_back` at [`vktShaderRenderBuiltinVarTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2587-L2621).

The fragment shader reads `gl_FrontFacing` directly. The non-UBO variant writes red for front-facing fragments and green for back-facing fragments, while the UBO variant adds the uniform value to `1.0` or `-1.0` and writes the scalar to all color channels at [`BuiltinGlFrontFacingCase::initPrograms()`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L318-L364). Reference rendering uses `FrontFacingVertexShader` and `FrontFacingFragmentShader`, whose expected colors follow the same non-UBO and UBO encodings at [`vktShaderRenderBuiltinVarTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L69-L130).

### fragdepth — `gl_FragDepth` across topologies, depth formats, depth clamp, large depth, and samples

The `fragdepth` group is constructed as a direct child at [`createBuiltinVarTests()`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2504-L2506) and attached at [`vktShaderRenderBuiltinVarTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2676-L2678). It is generated from three registered topology names, `point_list`, `line_list`, and `triangle_list`, and fifteen depth-case rows at [`vktShaderRenderBuiltinVarTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2625-L2673). The source maps the registered `triangle_list` name to `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP` in the table at [`vktShaderRenderBuiltinVarTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2631-L2638).

The depth-case rows include no-depth-clamp variants for `VK_FORMAT_D16_UNORM`, `VK_FORMAT_X8_D24_UNORM_PACK32`, `VK_FORMAT_D32_SFLOAT`, `VK_FORMAT_D16_UNORM_S8_UINT`, `VK_FORMAT_D24_UNORM_S8_UINT`, and `VK_FORMAT_D32_SFLOAT_S8_UINT`; a large-depth `VK_FORMAT_D32_SFLOAT` row; depth-clamp rows for `VK_FORMAT_D32_SFLOAT` and `VK_FORMAT_D32_SFLOAT_S8_UINT`; and multisample `VK_FORMAT_D32_SFLOAT` rows for 2, 4, 8, 16, 32, and 64 samples at [`vktShaderRenderBuiltinVarTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2640-L2663).

The first pass writes `gl_FragDepth` from a control buffer, marks covered sample locations in a storage image, and rechecks that `gl_FragDepth` retains the written value at [`BuiltinFragDepthCase::initPrograms()`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L1765-L1800). A second pass samples the depth attachment and writes resolved per-sample depth values to an `r32f` storage image for host readback at [`vktShaderRenderBuiltinVarTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L1803-L1827).

### fragcoord_msaa — sample-shading `gl_FragCoord` sample locations

The `fragcoord_msaa` group is constructed as a direct child at [`createBuiltinVarTests()`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2504-L2507) and attached at [`vktShaderRenderBuiltinVarTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2676-L2679). It registers one sample-shading case for each sample-count row named `1_bit`, `2_bit`, `4_bit`, `8_bit`, `16_bit`, `32_bit`, and `64_bit` at [`vktShaderRenderBuiltinVarTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2522-L2545).

For sample-shading cases, the fragment shader uses `gl_SampleID` to write each invocation's `gl_FragCoord` to a per-sample storage-image slot at [`BuiltinFragCoordMsaaTestCase::initPrograms()`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L1582-L1597). The instance copies that storage image to a host-visible buffer and validates the recorded coordinates at [`BuiltinFragCoordMsaaCaseInstance::iterate()`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L1359-L1385).

### fragcoord_msaa_input — sample-shading, no-sample-shading, and centroid input variants

The `fragcoord_msaa_input` group shares the same sample-count table as `fragcoord_msaa`, but registers three variants per sample count: the base sample-shading case, `_no_sample_shading`, and `_no_sample_shading_centroid_interpolation` at [`vktShaderRenderBuiltinVarTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2537-L2566).

When sample shading is disabled and centroid interpolation is not requested, the GLSL fragment shader writes one `gl_FragCoord` value per pixel to the storage image at [`vktShaderRenderBuiltinVarTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L1601-L1617). The centroid variant uses SPIR-V assembly with `OpDecorate %gl_FragCoord Centroid` at [`vktShaderRenderBuiltinVarTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L1618-L1685).

### simple — direct `gl_FragCoord` and `gl_PointCoord` cases

The `simple` group is constructed at [`createBuiltinVarTests()`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2501-L2503), populated with five direct cases at [`vktShaderRenderBuiltinVarTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2509-L2520), and attached at [`vktShaderRenderBuiltinVarTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2676-L2681). The registered cases are `fragcoord_xyz`, `fragcoord_w`, `pointcoord`, `pointcoord_uniform_frag`, and `pointcoord_uniform_vert`.

`fragcoord_xyz` writes `gl_FragCoord.xyz * u_scale` and compares every rendered pixel against an analytical window-coordinate reference at [`BuiltinGlFragCoordXYZCase::initPrograms()`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L1921-L1938) and [`BuiltinGlFragCoordXYZCaseInstance::iterate()`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L1852-L1887). `fragcoord_w` writes `1.0 / gl_FragCoord.w - 1.0` and validates the result with the same `0.00001` component tolerance using projected interpolation math at [`BuiltinGlFragCoordWCase::initPrograms()`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2037-L2053) and [`BuiltinGlFragCoordWCaseInstance::iterate()`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L1970-L2005).

The three `pointcoord` variants differ by whether the scale uniform is unused, applied in the fragment shader, or applied in the vertex shader at [`BuiltinGlPointCoordCase::initPrograms()`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2212-L2268). The instance generates 16 random point positions and sizes from the device point-size range, draws point-list primitives, builds a CPU reference for `gl_PointCoord`, and compares with `fuzzyCompare()` at a `0.02` threshold at [`BuiltinGlPointCoordCaseInstance::iterate()`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2085-L2180).

### input_variations — generated builtin, varying, and constant input combinations

The `input_variations` group is constructed at [`createBuiltinVarTests()`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2501-L2504), filled after the other direct children, and attached at [`vktShaderRenderBuiltinVarTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2682-L2689). The loop iterates all bit patterns from zero through `SHADER_INPUT_BUILTIN_BIT | SHADER_INPUT_VARYING_BIT | SHADER_INPUT_CONSTANT_BIT`, producing `input_none`, `input_builtin`, `input_varying`, `input_builtin_varying`, `input_constant`, `input_builtin_constant`, `input_varying_constant`, and `input_builtin_varying_constant` via `shaderInputTypeToString()` at [`vktShaderRenderBuiltinVarTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2275-L2301) and [`vktShaderRenderBuiltinVarTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2682-L2687).

The generated shaders conditionally include `gl_FrontFacing`, vertex-to-fragment varying color, and a push-constant color according to the selected bits at [`BuiltinInputVariationsCase::initPrograms()`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2436-L2490). The instance enables a push-constant range only when the constant bit is set, renders indexed triangles, computes a CPU reference from the same enabled inputs, and validates with `pixelThresholdCompare()` at [`BuiltinInputVariationsCaseInstance::iterate()`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2325-L2381).

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Direct child groups | `frontfacing`, `fragdepth`, `fragcoord_msaa`, `fragcoord_msaa_input`, `simple`, and `input_variations` are constructed and attached in [`createBuiltinVarTests()`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2499-L2690) |
| Front-facing topology names | `point_list`, `line_list`, `triangle_list`, `triangle_strip`, and `triangle_fan` from `frontfacingCases[]` at [`vktShaderRenderBuiltinVarTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2570-L2585) |
| Front-facing UBO/cull variants | `none` creates `simple`; `add_ubo_load` creates `none`, `front`, `back`, and `front_and_back` cull-mode cases at [`vktShaderRenderBuiltinVarTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2587-L2622) |
| FragDepth topology names | `point_list`, `line_list`, and registered `triangle_list` from [`primitiveTopologyTable[]`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2627-L2638); the `triangle_list` row uses `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP` in source |
| FragDepth formats and modes | Depth/stencil format rows, large-depth row, depth-clamp rows, and 2/4/8/16/32/64 sample rows from [`testCaseTable[]`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2640-L2663) |
| FragCoord MSAA sample counts | `1_bit`, `2_bit`, `4_bit`, `8_bit`, `16_bit`, `32_bit`, and `64_bit` from [`fragCoordMsaaCaseList[]`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2524-L2532) |
| FragCoord MSAA input variants | Base sample-shading, `_no_sample_shading`, and `_no_sample_shading_centroid_interpolation` forms registered at [`vktShaderRenderBuiltinVarTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2537-L2566) |
| Simple cases | `fragcoord_xyz`, `fragcoord_w`, `pointcoord`, `pointcoord_uniform_frag`, and `pointcoord_uniform_vert` at [`vktShaderRenderBuiltinVarTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2509-L2520) |
| PointCoord random points | 16 points with positions from `[-0.9, 0.9]` and sizes derived from `pointSizeRange` and `pointSizeGranularity` at [`vktShaderRenderBuiltinVarTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2085-L2116) |
| Input variation bits | `SHADER_INPUT_BUILTIN_BIT`, `SHADER_INPUT_VARYING_BIT`, and `SHADER_INPUT_CONSTANT_BIT` at [`vktShaderRenderBuiltinVarTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2275-L2280), iterated as all values 0 through 7 at [`vktShaderRenderBuiltinVarTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2682-L2687) |

## Support / Feature Requirements

| Requirement | Evidence |
|---|---|
| Triangle fan portability-subset gate | `BuiltinGlFrontFacingCase::checkSupport()` rejects triangle-fan cases when `VK_KHR_portability_subset` is present and `triangleFans` is false at [`vktShaderRenderBuiltinVarTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L366-L379) |
| FragDepth storage, sample shading, format, and sample-count gates | The FragDepth instance requires `fragmentStoresAndAtomics`, `sampleRateShading`, depth-image format/sample-count support, and `VK_FORMAT_R8G8B8A8_UINT` storage-image support at [`BuiltinFragDepthCaseInstance::BuiltinFragDepthCaseInstance()`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L425-L449) |
| Large depth extension | FragDepth large-depth variants require `VK_EXT_depth_range_unrestricted` when `m_largeDepthEnable` is true at [`vktShaderRenderBuiltinVarTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L451-L454) |
| Depth clamp feature | FragDepth depth-clamp variants require `depthClamp` when `m_depthClampEnable` is true at [`vktShaderRenderBuiltinVarTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L456-L457), and the pipeline state uses the same parameter at [`vktShaderRenderBuiltinVarTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L860-L864) |
| FragCoord MSAA sample-shading and storage gates | The MSAA instance requires `sampleRateShading`, `fragmentStoresAndAtomics`, `VK_FORMAT_R32G32B32A32_SFLOAT` color-image sample-count support, and storage-image support at [`BuiltinFragCoordMsaaCaseInstance::BuiltinFragCoordMsaaCaseInstance()`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L1111-L1158). This constructor runs even for `_no_sample_shading` input variants, so `sampleRateShading` is an instance-level gate in the inspected source. |

## Verification Methods

- `frontfacing` compares the rendered image against a reference draw using `tcu::intThresholdPositionDeviationCompare()` at [`vktShaderRenderBuiltinVarTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L260-L282), with reference shader color encodings defined in [`FrontFacingFragmentShader`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L91-L130).
- `fragdepth` copies the marker image and resolved depth image to host-visible buffers, then checks every pixel/sample against the expected depth or default depth with `0.001` tolerance in [`validateDepthBuffer()`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L1004-L1087).
- `fragcoord_msaa` and `fragcoord_msaa_input` copy the storage image of recorded `gl_FragCoord` values to a host-visible buffer, then validate z/w components, in-pixel coordinate bounds, uniqueness, standard sample locations when reported by device limits, and pixel-center behavior when sample shading is disabled at [`validateSampleLocations()`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L1394-L1530).
- `fragcoord_xyz` and `fragcoord_w` build analytical references from window coordinates and projected interpolation and fail when component differences exceed `0.00001` at [`BuiltinGlFragCoordXYZCaseInstance::iterate()`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L1852-L1887) and [`BuiltinGlFragCoordWCaseInstance::iterate()`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L1970-L2005).
- `pointcoord` constructs a CPU reference image for expected `gl_PointCoord` values and compares with `fuzzyCompare()` at threshold `0.02` at [`BuiltinGlPointCoordCaseInstance::iterate()`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2085-L2180).
- `input_variations` constructs a CPU reference image from the selected builtin/varying/constant bits and validates the rendered image with `pixelThresholdCompare()` and threshold `(2, 2, 2, 2)` at [`BuiltinInputVariationsCaseInstance::iterate()`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2325-L2381).

## Test Principles

- The file groups builtin-variable behavior by direct registered family instead of by shader class alone: `frontfacing`, `fragdepth`, `fragcoord_msaa`, `fragcoord_msaa_input`, `simple`, and `input_variations` are the top-level branches below `glsl.builtin_var` at [`createBuiltinVarTests()`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2499-L2690).
- Rendered-image comparison is the dominant pass/fail mechanism: the tests either compare against analytical images, reference rasterization, sampled depth readback, or storage-image records of shader builtin values.
- Generated tables and loops define the documented parameter space; the page does not infer additional topologies, formats, sample counts, or shader-input combinations beyond the arrays and loops in [`createBuiltinVarTests()`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2499-L2690).

## Notes / Uncertainties

- The inspected file is both the registration source and implementation source for `glsl.builtin_var`; no separate helper source file was needed to verify the documented direct children.
- The registered FragDepth case name `triangle_list` is preserved because it is the registered source name, even though the table's `prim` value is `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP` in the inspected source at [`vktShaderRenderBuiltinVarTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2631-L2638).
