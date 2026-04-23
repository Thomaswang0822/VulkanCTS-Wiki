# vktGeometryBasicGeometryShaderTests.cpp

## Overview

[`vktGeometryBasicGeometryShaderTests.cpp`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L1) implements the [`basic`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L1002) subgroup of the geometry category. In the inspected code, it covers fixed output-vertex-count patterns, runtime-varying output counts sourced from attributes/uniforms/textures, and side-effect cases that verify geometry-shader writes even when no color output should be produced.

## Role

Implementation file.

## Source Code

- Primary source: [`vktGeometryBasicGeometryShaderTests.cpp`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L1)
- Shared base: [`GeometryExpanderRenderTestInstance`](../../modules/vulkan/geometry/vktGeometryBasicClass.hpp#L37)
- Shared helpers: [`compareWithFileImage()`](../../modules/vulkan/geometry/vktGeometryTestsUtil.cpp#L412), [`makeImageCreateInfo()`](../../modules/vulkan/geometry/vktGeometryTestsUtil.cpp#L374)

## Registration Path

This file contributes the subgroup returned by [`createBasicGeometryShaderTests()`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L1000), which is attached under geometry by [`createChildren()`](../../modules/vulkan/geometry/vktGeometryTests.cpp#L46).

## Test Hierarchy

```text
basic
├── output_10
├── output_128
├── output_10_and_100
├── output_100_and_10
├── output_0_and_128
├── output_128_and_0
├── output_vary_by_attribute
├── output_vary_by_uniform
├── output_vary_by_texture
├── output_vary_by_attribute_instancing
├── output_vary_by_uniform_instancing
├── output_vary_by_texture_instancing
├── side_effect_with_condition
└── side_effect_with_degenerate
```

Source: [`createBasicGeometryShaderTests()`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L1000).

## Test Families

### 1. Fixed output-count patterns

[`GeometryOutputCountTest`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L451) registers single-pattern and two-pattern cases:
- [`output_10`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L1005)
- [`output_128`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L1006)
- [`output_10_and_100`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L1008)
- [`output_100_and_10`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L1009)
- [`output_0_and_128`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L1010)
- [`output_128_and_0`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L1011)

The geometry program computes the emitted vertex count from [`m_pattern`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L461) and emits a row/column arrangement of primitives in [`GeometryOutputCountTest::initPrograms()`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L475).

### 2. Varying output count from runtime sources

[`VaryingOutputCountCase`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L550) creates six cases, combining three count sources with two instancing modes:
- source kinds: [`READ_ATTRIBUTE`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L64), [`READ_UNIFORM`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L67), [`READ_TEXTURE`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L68)
- instancing modes: [`MODE_WITHOUT_INSTANCING`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L74), [`MODE_WITH_INSTANCING`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L75)

The corresponding registrations are at [`createBasicGeometryShaderTests()`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L1014).

Data sources are realized as:
- per-vertex/per-instance attribute values in [`genVertexDataWithoutInstancing()`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L393) and [`genVertexDataWithInstancing()`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L424)
- uniform buffer upload in [`bindDescriptorSets()`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L315)
- sampled texture lookup in [`bindDescriptorSets()`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L340)

### 3. Side-effect cases

Two function-style cases are added through [`addFunctionCaseWithPrograms()`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L1041):
- [`side_effect_with_condition`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L1039)
- [`side_effect_with_degenerate`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L1039)

The geometry shader for these cases writes [`ssbo.value = 777u`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L843) or [`ssbo.value = 777u`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L854), and the test later checks both SSBO content and an unchanged color buffer in [`sideEffectTest()`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L868).

## Parameter Dimensions

| Parameter | Observed values / source |
|---|---|
| Fixed output-count pattern | Single-count and two-count patterns created by [`createPattern()`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L771) and [`createPattern()`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L778) |
| Canonical emit-count constants | [`EMIT_COUNT_VERTEX_0 = 6`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L81), [`EMIT_COUNT_VERTEX_1 = 0`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L82), [`EMIT_COUNT_VERTEX_2 = -1`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L83), [`EMIT_COUNT_VERTEX_3 = 10`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L84) where `-1` maps to the max emit count |
| Varying-output source | [`READ_ATTRIBUTE`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L64), [`READ_UNIFORM`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L67), [`READ_TEXTURE`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L68) |
| Instancing mode | [`MODE_WITHOUT_INSTANCING`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L74), [`MODE_WITH_INSTANCING`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L75) |
| Maximum varying emit count | [`m_maxEmitCount(128)`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L220) |
| Side-effect scenario | [`SideEffectCase::CONDITION`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L788), [`SideEffectCase::DEGENERATE`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L789) |

## Support / Feature Requirements

Observed support checks include:
- geometry shader core feature in [`GeometryOutputCountTest::checkSupport()`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L470)
- geometry shader core feature in [`VaryingOutputCountCase::checkSupport()`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L572)
- geometry shader plus vertex-pipeline stores-and-atomics in [`sideEffectSupportCheck()`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L797)

## Verification Methods

Observed verification paths differ by family:

### Fixed output-count and varying-output-count families

These tests are built on [`GeometryExpanderRenderTestInstance`](../../modules/vulkan/geometry/vktGeometryBasicClass.hpp#L37) and shared geometry utilities. The inspected helpers show a file-image comparison path in [`compareWithFileImage()`](../../modules/vulkan/geometry/vktGeometryTestsUtil.cpp#L412), which first uses [`tcu::fuzzyCompare()`](../../modules/vulkan/geometry/vktGeometryTestsUtil.cpp#L418) and then [`tcu::intThresholdPositionDeviationCompare()`](../../modules/vulkan/geometry/vktGeometryTestsUtil.cpp#L420).

### Side-effect family

[`sideEffectTest()`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L868) performs two explicit validations:
- SSBO content check against the expected sentinel value [`777u`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L970)
- exact color-buffer comparison against a cleared reference image using [`tcu::floatThresholdCompare()`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L991)

## Test Principles Observed

- **Pattern-driven output validation**: output-count tests encode expected emitted geometry through integer patterns rather than separate bespoke shaders
- **Multiple runtime count sources**: the same conceptual test is applied to attributes, uniform buffers, and textures
- **Instanced and non-instanced variants**: varying-output tests reuse the same logic with and without geometry-shader invocations-based instancing in [`initPrograms()`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L614)
- **Side effects are checked separately from raster output**: the side-effect tests explicitly verify both storage-buffer writes and absence of framebuffer changes

## Notes / Uncertainties

- The file strongly suggests that the non-side-effect families compare rendered results against known reference images through the shared geometry base/helpers, but the exact shared iterate path is outside the inspected snippet set.
- The documentation therefore describes the observed helper-based verification path without claiming every call site in this file directly invokes it.
