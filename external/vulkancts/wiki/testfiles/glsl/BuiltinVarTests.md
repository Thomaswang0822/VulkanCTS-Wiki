## Overview

[`vktShaderRenderBuiltinVarTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L1) implements the rendered GLSL test group `glsl.builtin_var`. The GLSL package attaches it through [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1272). The group checks fragment-stage built-ins and the input paths used to feed generated shaders: `gl_FrontFacing`, `gl_FragDepth`, `gl_FragCoord`, `gl_PointCoord`, and combinations of a builtin, an interpolated varying, and a push constant.

This is a registration-and-implementation page. The factory creates six direct children and expands their leaves from source tables and loops. The observed Vulkan and Vulkan SC mustpass files each contain 111 normalized `glsl.builtin_var` leaves; the profile prefixes differ (`dEQP-VK` versus `dEQP-VKSC`).

## Role

The source file is both the dispatcher and the implementation for this group. It builds ordinary GLSL vertex/fragment programs for most cases and uses an inline SPIR-V assembly fragment for the centroid-interpolation variant. The tests render images or record builtin values into storage images, copy the results back, and compare them with reference values.

## Source Code

- Primary source and factory: [`vktShaderRenderBuiltinVarTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2499-L2690)
- Public declarations: [`vktShaderRenderBuiltinVarTests.hpp`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.hpp#L30-L35)
- GLSL root registration: [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1272)
- Front-facing case and shader construction: [`BuiltinGlFrontFacingCase`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L305-L383)
- FragDepth support and execution: [`BuiltinFragDepthCaseInstance`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L386-L466)
- Sample-location validation: [`validateSampleLocations()`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L1394-L1530)
- Generated input-variation shaders and instance: [`BuiltinInputVariationsCase`](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2275-L2495)

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

The tree shows the canonical direct-child hierarchy. Nested topology, mode, format, sample-count, and input-bit leaves are described below and in the mustpass evidence.

## Test Families

### `frontfacing`

`frontfacing` has two subgroups, `none` and `add_ubo_load`, and five topology groups: `point_list`, `line_list`, `triangle_list`, `triangle_strip`, and `triangle_fan` ([factory](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2568-L2622)). The `none` subgroup adds one `simple` case per topology, giving 5 leaves. The `add_ubo_load` subgroup adds four cull-mode cases (`none`, `front`, `back`, and `front_and_back`) per topology, giving 20 leaves and 25 total.

The fragment shader reads `gl_FrontFacing`. Without the UBO load it writes red for a front-facing fragment and green for a back-facing fragment. With the UBO load it adds the uniform value to `1.0` or `-1.0` and writes that scalar to all color channels ([shader generation](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L318-L364)). The rendered image is compared with a reference draw using `tcu::intThresholdPositionDeviationCompare()` ([comparison](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L260-L282)).

Triangle-fan cases are rejected on implementations advertising `VK_KHR_portability_subset` without the `triangleFans` feature. The source contains a Vulkan SC branch that does not perform that runtime query ([support check](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L366-L379)).

### `fragdepth`

The factory combines three registered topology names—`point_list`, `line_list`, and `triangle_list`—with 15 depth configurations ([factory](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2625-L2673)). This is 3 × 15 = 45 leaves. The registered `triangle_list` name deliberately maps to `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP` in the source table ([topology table](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2627-L2638)).

The 15 rows cover six single-sample no-depth-clamp formats (`D16_UNORM`, `X8_D24_UNORM_PACK32`, `D32_SFLOAT`, `D16_UNORM_S8_UINT`, `D24_UNORM_S8_UINT`, and `D32_SFLOAT_S8_UINT`), one unrestricted-large-depth `D32_SFLOAT` row, two depth-clamp rows, and six `D32_SFLOAT` multisample rows for 2, 4, 8, 16, 32, and 64 samples ([case table](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2640-L2663)).

The first pass writes `gl_FragDepth` from a control buffer and records covered sample locations in an `R8G8B8A8_UINT` storage image. A second pass samples the depth attachment and writes resolved per-sample depth values to an `R32_SFLOAT` storage image. Host validation checks every relevant pixel/sample against the expected depth or default depth with a 0.001 tolerance ([validation](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L1004-L1087)).

### `fragcoord_msaa`

Seven cases are generated for `1_bit`, `2_bit`, `4_bit`, `8_bit`, `16_bit`, `32_bit`, and `64_bit` sample counts ([factory](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2522-L2545)). Sample-shaded fragment invocations use `gl_SampleID` to store their `gl_FragCoord` values in per-sample storage-image slots ([shader generation](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L1582-L1597)). The instance copies the records to a host-visible buffer and validates them with the shared sample-location checks ([instance](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L1359-L1385)).

### `fragcoord_msaa_input`

The same seven sample counts are expanded into three variants: the sample-shaded base case, `_no_sample_shading`, and `_no_sample_shading_centroid_interpolation`, for 21 leaves ([factory](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2537-L2566)). Without sample shading, the shader records one `gl_FragCoord` value per pixel. The centroid form uses inline SPIR-V assembly with `OpDecorate %gl_FragCoord Centroid` ([shader sources](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L1601-L1685)). Validation checks z/w, in-pixel bounds, uniqueness, standard sample locations when device limits report them, and pixel-center behavior for non-sample-shaded cases ([validator](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L1394-L1530)).

The instance-level constructor requires `sampleRateShading` and `fragmentStoresAndAtomics`, plus supported `R32G32B32A32_SFLOAT` color-image sample counts and storage-image usage ([support check](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L1111-L1158)). Consequently, the sample-rate feature gate is applied even to the no-sample-shading input variants in this inspected implementation.

### `simple`

Five direct cases are registered: `fragcoord_xyz`, `fragcoord_w`, `pointcoord`, `pointcoord_uniform_frag`, and `pointcoord_uniform_vert` ([factory](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2509-L2520)).

- `fragcoord_xyz` writes `gl_FragCoord.xyz * u_scale` and compares all rendered pixels with an analytical window-coordinate reference ([shader and instance](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L1852-L1938)).
- `fragcoord_w` writes `1.0 / gl_FragCoord.w - 1.0` and uses projected-interpolation math with a 0.00001 component tolerance ([shader and instance](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L1970-L2053)).
- The three `pointcoord` cases differ in whether the scale uniform is unused, consumed in the fragment shader, or consumed in the vertex shader ([shader generation](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2212-L2268)). The instance renders 16 random point positions and sizes derived from the device point-size range and compares a CPU `gl_PointCoord` reference with a 0.02 fuzzy threshold ([instance](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2085-L2180)).

### `input_variations`

The factory iterates every value from zero through the OR of `SHADER_INPUT_BUILTIN_BIT`, `SHADER_INPUT_VARYING_BIT`, and `SHADER_INPUT_CONSTANT_BIT` ([loop](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2682-L2687)). The eight leaves are `input_none`, `input_builtin`, `input_varying`, `input_builtin_varying`, `input_constant`, `input_builtin_constant`, `input_varying_constant`, and `input_builtin_varying_constant` ([name conversion](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2275-L2301)).

The generated programs conditionally include `gl_FrontFacing`, a vertex-to-fragment varying color, and a push-constant color ([program generation](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2436-L2490)). The instance enables a push-constant range only when the constant bit is selected, renders indexed triangles, builds the matching CPU reference from the enabled inputs, and uses `pixelThresholdCompare()` with threshold `(2, 2, 2, 2)` ([instance](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2325-L2381)).

## Coverage Reconciliation

| Family | Source expansion | Leaves |
|---|---:|---:|
| `frontfacing` | 5 topologies × (1 simple + 4 UBO/cull cases) | 25 |
| `fragdepth` | 3 topology names × 15 depth rows | 45 |
| `fragcoord_msaa` | 7 sample counts | 7 |
| `fragcoord_msaa_input` | 7 sample counts × 3 input/interpolation modes | 21 |
| `simple` | 5 direct cases | 5 |
| `input_variations` | 2³ combinations of three input bits | 8 |
| **Total** |  | **111** |

The exact normalized leaf set in [`vk-default/glsl.txt`](../../../mustpass/main/vk-default/glsl.txt#L3913-L4023) contains 111 entries rooted at `dEQP-VK.glsl.builtin_var`. The Vulkan SC set in [`vksc-default/glsl.txt`](../../../mustpass/main/vksc-default/glsl.txt#L3050-L3160) also contains 111 entries rooted at `dEQP-VKSC.glsl.builtin_var`. The different line order is not treated as a coverage difference.

## Support / Feature Requirements

| Requirement | Scope and evidence |
|---|---|
| Portability-subset triangle-fan support | `frontfacing` triangle-fan cases skip when `VK_KHR_portability_subset` is supported but `triangleFans` is false ([check](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L366-L379)). |
| Fragment storage and sample-rate features | FragDepth requires `fragmentStoresAndAtomics` and `sampleRateShading` ([constructor](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L433-L437)); MSAA cases use corresponding storage/sample feature checks ([constructor](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L1111-L1158)). |
| Image format and sample-count support | FragDepth checks the selected depth format's attachment sample counts and `VK_FORMAT_R8G8B8A8_UINT` storage-image support ([check](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L439-L449)). MSAA checks the selected color format and sample count. |
| `VK_EXT_depth_range_unrestricted` | Required only for the `large_depth` FragDepth rows ([check](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L451-L454)). |
| `depthClamp` | Required only when the FragDepth row enables depth clamping ([check](../../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L456-L457)). |

The factory call itself is not guarded out of the GLSL package for Vulkan SC. A support-query branch is nevertheless compile-partitioned with `#ifndef CTS_USES_VULKANSC`; this is a runtime-support behavior difference, not evidence that the source file or group is absent from the Vulkan SC mustpass list.

## Verification Methods

- `frontfacing` compares the rendered image with reference rasterization using an integer-threshold position-deviation comparison.
- `fragdepth` reads marker and resolved-depth images back to host memory and checks the expected depth values per pixel and sample with a 0.001 tolerance.
- `fragcoord_msaa` and `fragcoord_msaa_input` read recorded builtin values and check coordinate bounds, z/w, uniqueness, reported standard sample locations, and the no-sample-shading center rule.
- `fragcoord_xyz` and `fragcoord_w` compare analytical references, with the latter using projected interpolation and a 0.00001 component tolerance.
- `pointcoord` compares a CPU-generated point-rasterization reference using a 0.02 fuzzy threshold.
- `input_variations` compares the rendered image with a reference assembled from the selected shader-input bits using `(2, 2, 2, 2)` pixel thresholds.

A mismatch establishes that the selected shader, rasterization path, image/buffer setup, synchronization/readback, and host comparison did not agree. It does not by itself isolate GLSL builtin lowering from rasterization, format handling, pipeline setup, or framework code. Unsupported feature or format predicates yield `NotSupportedError` rather than an executed-case output failure.

## Test Principles

- Registration names and generated loops define the coverage; no additional topology, format, sample count, cull mode, or input combination is implied beyond the inspected tables.
- The family uses both image-oracle tests and storage-image readback. A rendered-image mismatch and a recorded-builtin mismatch have different immediate observability, even when they share the same graphics runner.
- The source keeps the registered `triangle_list` FragDepth name even though its implementation table selects triangle-strip topology; this is a source-level naming/parameter distinction, not an inferred correction.
- The Vulkan and Vulkan SC mustpass inventories match after removing their profile-specific prefixes; support filtering must not be confused with registration absence.

## Notes / Uncertainties
- The documented counts are mechanically derived from the factory: 25 + 45 + 7 + 21 + 5 + 8 = 111.
- The page describes source-backed behavior and coverage; it does not claim that the device tests were executed in this environment.
- The source's Vulkan SC conditional changes the portability-subset support-query branch. The factory remains registered and the Vulkan SC mustpass inventory is present, so no broader Vulkan SC exclusion is asserted.
