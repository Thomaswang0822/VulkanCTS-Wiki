# ubo

## Overview

The [`ubo`](../../modules/vulkan/vktTestPackage.cpp#L1353-L1356) category verifies uniform-buffer-object block declarations, layout rules, descriptor binding, shader-stage visibility, and generated shader reads. The category root is implemented by [`vktUniformBlockTests.cpp`](../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L1), which registers fixed layout-shape families and deterministic random-layout families; execution and validation are shared through [`vktUniformBlockCase.cpp`](../../modules/vulkan/ubo/vktUniformBlockCase.cpp#L2572-L2691).

## Registration Entry Point

The Vulkan package registers `ubo` through [`TestPackage::init()`](../../modules/vulkan/vktTestPackage.cpp#L1345-L1356), and the Vulkan SC package also registers it through [`TestPackageSC::init()`](../../modules/vulkan/vktTestPackage.cpp#L1413-L1424). The category factory [`ubo::createTests()`](../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L1260-L1263) returns [`UniformBlockTests`](../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L424-L439), whose [`init()`](../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L446-L1256) registers the direct children below:

```text
ubo
├── 2_level_array
├── 2_level_struct_array
├── 3_level_array
├── instance_array_basic_type
├── link_by_binding
├── multi_basic_types
├── multi_nested_struct
├── random
├── single_basic_array
├── single_basic_type
├── single_nested_struct
├── single_nested_struct_array
├── single_struct
├── single_struct_array
└── unsized_array
```

## File Inventory

| File | Role | Notes |
|---|---|---|
| [`vktUniformBlockTests.cpp`](../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L1) | Registration and implementation | Registers all direct `ubo` groups and fixed/random case families. |
| [`vktUniformBlockTests.hpp`](../../modules/vulkan/ubo/vktUniformBlockTests.hpp#L35) | Public factory declaration | Declares [`createTests()`](../../modules/vulkan/ubo/vktUniformBlockTests.hpp#L35) for package registration. |
| [`vktUniformBlockCase.cpp`](../../modules/vulkan/ubo/vktUniformBlockCase.cpp#L1) | Helper / execution infrastructure | Computes reference layouts, generates shaders, creates descriptors/pipelines, and validates rendered/compute output. |
| [`vktUniformBlockCase.hpp`](../../modules/vulkan/ubo/vktUniformBlockCase.hpp#L40-L73) | Helper declarations | Defines uniform/layout flags and the base [`UniformBlockCase`](../../modules/vulkan/ubo/vktUniformBlockCase.hpp#L435-L464). |
| [`vktRandomUniformBlockCase.cpp`](../../modules/vulkan/ubo/vktRandomUniformBlockCase.cpp#L1) | Helper / random case construction | Builds deterministic random block layouts and type trees. |
| [`vktRandomUniformBlockCase.hpp`](../../modules/vulkan/ubo/vktRandomUniformBlockCase.hpp#L39-L64) | Helper declarations | Defines random feature bits used by the `random` group. |

## Level-3 Documents

| Source file | Wiki document |
|---|---|
| [`vktUniformBlockTests.cpp`](../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L1) | [`vktUniformBlockTests.md`](../testfiles/ubo/vktUniformBlockTests.md) |

## Subgroup Structure and Major Themes

- Array-layout coverage is split into [`single_basic_array`](../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L662-L694), [`2_level_array`](../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L492-L525), [`3_level_array`](../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L527-L562), and [`unsized_array`](../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L696-L735).
- Struct-layout coverage is split into [`single_struct`](../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L737-L787), [`single_struct_array`](../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L789-L839), [`single_nested_struct`](../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L841-L891), [`single_nested_struct_array`](../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L893-L944), [`2_level_struct_array`](../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L564-L608), and [`multi_nested_struct`](../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L1041-L1100).
- Basic and multi-block coverage includes [`single_basic_type`](../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L610-L660), [`instance_array_basic_type`](../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L946-L978), [`multi_basic_types`](../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L980-L1039), and [`link_by_binding`](../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L1102-L1115).
- Deterministic random coverage is grouped under [`random`](../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L1117-L1255) and implemented by [`RandomUniformBlockCase`](../../modules/vulkan/ubo/vktRandomUniformBlockCase.cpp#L55-L99).

## Recurring Parameter Dimensions

| Dimension | Observed source evidence |
|---|---|
| Data types | [`basicTypes[]`](../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L448-L461) includes scalar, vector, matrix, boolean, 8-bit, and 16-bit types. |
| Layout qualifiers | [`layoutFlags[]`](../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L473-L477) registers `std140`, `std430`, and `scalar`; [`LayoutFlagsFmt`](../../modules/vulkan/ubo/vktUniformBlockCase.cpp#L272-L311) emits those qualifiers into GLSL. |
| Precision qualifiers | [`precisionFlags[]`](../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L463-L471) registers `lowp`, `mediump`, and `highp` for types that support precision modifiers. |
| Matrix variants | [`matrixFlags[]`](../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L479-L483) registers row-major and column-major variants, and [`LOAD_MATRIX_COMPONENTS`](../../modules/vulkan/ubo/vktUniformBlockCase.hpp#L75-L79) enables component-access checks. |
| Shader stages | [`createBlockBasicTypeCases()`](../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L85-L109) creates vertex, fragment, compute, both-stage, and component-access variants for basic block cases. |
| Buffer mode | [`bufferModes[]`](../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L485-L490) registers per-block-buffer and single-shared-buffer modes; [`UniformBlockCase::BufferMode`](../../modules/vulkan/ubo/vktUniformBlockCase.hpp#L438-L444) defines those two modes. |
| Instance arrays and nesting | Fixed registration code uses explicit sizes such as array size `3`, nested sizes `4`/`3` and `2`/`4`/`3`, instance-array count `3`, and unsized-array test size `19` in the corresponding family registration blocks. |
| Random feature bits | [`FeatureBits`](../../modules/vulkan/ubo/vktRandomUniformBlockCase.hpp#L39-L64) controls random use of vectors, matrices, arrays, structs, instance arrays, unused members/uniforms, matrix layout, arrays of arrays, out-of-order offsets, 8-bit/16-bit storage, `std430`, scalar layout, and descriptor indexing. |

## Recurring Support Requirements

The shared support gate is [`UniformBlockCase::checkSupport()`](../../modules/vulkan/ubo/vktUniformBlockCase.cpp#L2671-L2691). It checks 16-bit storage, 8-bit storage, `std430` support through scalar-block-layout or uniform-buffer-standard-layout features, scalar block layout, descriptor-indexing support for uniform buffers, runtime descriptor arrays, and the uniform-buffer unsized-array feature when relevant.

## Recurring Verification Methods

The category computes expected layout entries in [`computeReferenceLayout()`](../../modules/vulkan/ubo/vktUniformBlockCase.cpp#L719-L767), writes deterministic reference values in [`generateValues()`](../../modules/vulkan/ubo/vktUniformBlockCase.cpp#L838-L854), emits GLSL declarations in [`generateDeclaration()`](../../modules/vulkan/ubo/vktUniformBlockCase.cpp#L1313-L1350), and emits read/compare code in [`generateCompareSrc()`](../../modules/vulkan/ubo/vktUniformBlockCase.cpp#L1612-L1733). Runtime validation uploads the reference UBO data, runs either the graphics or compute path, reads back an image, and requires every pixel to be white in [`UniformBlockCaseInstance::iterate()`](../../modules/vulkan/ubo/vktUniformBlockCase.cpp#L2089-L2404).

## Relationship to the Test Plan

[`doc/testspecs/VK/apitests.adoc`](../../../../doc/testspecs/VK/apitests.adoc) was searched for `ubo`, `uniform buffer`, and `uniform block`; no category-specific UBO test-plan section was found in that inspected file. The factual claims above therefore rely on source and mustpass evidence under [`external/vulkancts/`](../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L1).

## Notes / Uncertainties

- The inspected registration source and mustpass paths agree on the 15 direct `ubo` children listed above.
- Only [`vktUniformBlockTests.cpp`](../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L1) receives a Level-3 page because it is the only inspected `ubo` source file that registers tests; helper files are documented through source links in that page.