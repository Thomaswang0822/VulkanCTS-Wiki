# vktUniformBlockTests.cpp

## Overview

[`vktUniformBlockTests.cpp`](../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L1) is the registration and case-definition file for the Vulkan CTS [`ubo`](../../../modules/vulkan/vktTestPackage.cpp#L1353-L1356) category. It builds the top-level uniform-block groups in [`UniformBlockTests::init()`](../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L446-L1256), while shared execution, layout calculation, shader generation, support checks, and result validation are implemented in [`vktUniformBlockCase.cpp`](../../../modules/vulkan/ubo/vktUniformBlockCase.cpp#L2572-L2691) and randomized case construction is implemented in [`vktRandomUniformBlockCase.cpp`](../../../modules/vulkan/ubo/vktRandomUniformBlockCase.cpp#L55-L319).

## Role

Registration / implementation file. This is the only inspected source file under [`modules/vulkan/ubo/`](../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L26-L29) that registers tests into the `ubo` category; [`vktUniformBlockCase.cpp`](../../../modules/vulkan/ubo/vktUniformBlockCase.cpp#L26) and [`vktRandomUniformBlockCase.cpp`](../../../modules/vulkan/ubo/vktRandomUniformBlockCase.cpp#L26) provide reusable case infrastructure.

## Source Code

- Primary source: [`vktUniformBlockTests.cpp`](../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L1)
- Root package registration: [`TestPackage::init()`](../../../modules/vulkan/vktTestPackage.cpp#L1345-L1356) and [`TestPackageSC::init()`](../../../modules/vulkan/vktTestPackage.cpp#L1413-L1424)
- Shared execution support: [`vktUniformBlockCase.cpp`](../../../modules/vulkan/ubo/vktUniformBlockCase.cpp#L2572-L2691)
- Random case generator: [`vktRandomUniformBlockCase.cpp`](../../../modules/vulkan/ubo/vktRandomUniformBlockCase.cpp#L55-L319)

## Registration Hierarchy

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

## Test Families

### 2_level_array — Two-dimensional arrays of basic uniform types

The `2_level_array` group is registered in [`UniformBlockTests::init()`](../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L492-L525). It iterates `std140`, `std430`, and `scalar` layout groups from [`layoutFlags[]`](../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L473-L477), then creates nested arrays with child size `4` and parent size `3` for every entry in [`basicTypes[]`](../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L448-L461). Matrix types also receive `row_major` and `column_major` variants through [`matrixFlags[]`](../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L479-L483).

### 2_level_struct_array — Arrays of structs with nested array members

The `2_level_struct_array` group is registered in [`UniformBlockTests::init()`](../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L564-L608). It creates `per_block_buffer` and `single_buffer` mode groups from [`bufferModes[]`](../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L485-L490), applies each layout in [`layoutFlags[]`](../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L473-L477), and uses [`Block2LevelStructArrayCase`](../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L348-L378) to test a struct array nested inside a block member.

### 3_level_array — Three-dimensional arrays of basic uniform types

The `3_level_array` group is registered in [`UniformBlockTests::init()`](../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L527-L562). It creates arrays with sizes `2`, `4`, and `3` across three levels before passing the resulting `VarType` to [`createBlockBasicTypeCases()`](../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L85-L109); matrix types add row-major and column-major cases at the same registration site.

### instance_array_basic_type — Uniform-block instance arrays for basic types

The `instance_array_basic_type` group is registered in [`UniformBlockTests::init()`](../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L946-L978). It uses `numInstances = 3` for each basic type and layout, with matrix row/column variants when [`glu::isDataTypeMatrix()`](../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L967-L974) is true.

### link_by_binding — Same block name linked by descriptor binding

The `link_by_binding` group is registered in [`UniformBlockTests::init()`](../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L1102-L1115). [`LinkByBindingCase`](../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L380-L407) creates two `TestBlock` declarations with different members and stage flags, then registers single-buffer and per-block-buffer variants with and without instance arrays.

### multi_basic_types — Multiple blocks with basic members

The `multi_basic_types` group is registered in [`UniformBlockTests::init()`](../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L980-L1039). [`BlockMultiBasicTypesCase`](../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L278-L306) defines `BlockA` and `BlockB` with different scalar, vector, matrix, and boolean members, and the registration loops combine buffer mode, layout, instance-array option, shader-stage usage, mixed vertex/fragment usage, and matrix component access.

### multi_nested_struct — Multiple blocks with nested struct members

The `multi_nested_struct` group is registered in [`UniformBlockTests::init()`](../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L1041-L1100). [`BlockMultiNestedStructCase`](../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L308-L346) defines structs `S` and `T` and places them in `BlockA` and `BlockB`; the registration dimensions mirror `multi_basic_types` with per-block versus single-buffer modes and stage/matrix-access variants.

### random — Deterministic random uniform-block layouts

The `random` group is registered in [`UniformBlockTests::init()`](../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L1117-L1255). [`createRandomCaseGroup()`](../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L409-L420) creates numbered [`RandomUniformBlockCase`](../../../modules/vulkan/ubo/vktRandomUniformBlockCase.cpp#L55-L99) children from fixed base seeds plus the command-line base seed. The group includes normal, `16bit`, and `8bit` subgroups, and each subgroup contains families such as `scalar_types`, `vector_types`, `basic_types`, arrays, nested structs, `all_per_block_buffers`, `all_shared_buffer`, `all_out_of_order_offsets`, `scalar`, and `descriptor_indexing` as registered in [`UniformBlockTests::init()`](../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L1137-L1253).

### single_basic_array — One uniform array member

The `single_basic_array` group is registered in [`UniformBlockTests::init()`](../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L662-L694). It creates arrays of size `3` for each basic type and layout, with matrix row/column variants registered through [`matrixFlags[]`](../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L683-L690).

### single_basic_type — One basic uniform member

The `single_basic_type` group is registered in [`UniformBlockTests::init()`](../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L610-L660). It covers non-precision-qualified types directly and precision-qualified types under `lowp`, `mediump`, and `highp` groups from [`precisionFlags[]`](../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L463-L471); [`createBlockBasicTypeCases()`](../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L85-L109) then registers `vertex`, `fragment`, `compute`, `both`, and component-access variants.

### single_nested_struct — One nested struct member

The `single_nested_struct` group is registered in [`UniformBlockTests::init()`](../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L841-L891). [`BlockSingleNestedStructCase`](../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L216-L245) creates structs `S` and `T` and a block containing `s`, `v`, `t`, and `u` members, with buffer mode, layout, optional instance-array, shader-stage, and component-access variants supplied by the registration loop.

### single_nested_struct_array — Nested struct arrays

The `single_nested_struct_array` group is registered in [`UniformBlockTests::init()`](../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L893-L944). [`BlockSingleNestedStructArrayCase`](../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L247-L276) uses struct arrays inside nested structs and is registered with the same buffer-mode, layout, instance-array, stage, and component-access dimensions as the other struct groups.

### single_struct — One struct member

The `single_struct` group is registered in [`UniformBlockTests::init()`](../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L737-L787). [`BlockSingleStructCase`](../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L166-L188) creates a struct `S` with integer-vector, matrix-array, and vector members, then places it as uniform `s` in `Block`.

### single_struct_array — Array of structs plus surrounding members

The `single_struct_array` group is registered in [`UniformBlockTests::init()`](../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L789-L839). [`BlockSingleStructArrayCase`](../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L190-L214) adds `u`, an array of three `S` structs, and `v` to a single block, then the registration loop applies the common buffer/layout/stage/component-access dimensions.

### unsized_array — Runtime-sized last member in a uniform block

The `unsized_array` group is registered in [`UniformBlockTests::init()`](../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L696-L735). [`BlockBasicUnsizedArrayCase`](../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L111-L145) places an unsized array as the last block member and sets a test size of `19`; [`createUnsizedArrayTestCases()`](../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L147-L164) registers vertex, fragment, compute, and both-stage variants, plus matrix component-access variants when applicable.

## Parameter Dimensions

| Dimension | Evidence-backed values |
|---|---|
| Basic data types | Floating, integer, unsigned integer, boolean, matrix, 8-bit, 16-bit, and vector variants enumerated in [`basicTypes[]`](../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L448-L461). |
| Layout qualifiers | `std140`, `std430`, and `scalar` are registered by [`layoutFlags[]`](../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L473-L477); generated GLSL emits these qualifiers through [`LayoutFlagsFmt`](../../../modules/vulkan/ubo/vktUniformBlockCase.cpp#L272-L311). |
| Precision qualifiers | `lowp`, `mediump`, and `highp` are registered in [`precisionFlags[]`](../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L463-L471) and emitted by [`PrecisionFlagsFmt`](../../../modules/vulkan/ubo/vktUniformBlockCase.cpp#L253-L270). |
| Matrix layout and access | `row_major` and `column_major` are registered in [`matrixFlags[]`](../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L479-L483); component-access variants use `LOAD_MATRIX_COMPONENTS` in [`createBlockBasicTypeCases()`](../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L98-L106). |
| Shader stages | Fixed groups register `vertex`, `fragment`, `compute`, and `both` stage variants in [`createBlockBasicTypeCases()`](../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L90-L106), and generated shaders declare blocks only for matching stage flags in [`generateVertexShader()`](../../../modules/vulkan/ubo/vktUniformBlockCase.cpp#L1779-L1784), [`generateFragmentShader()`](../../../modules/vulkan/ubo/vktUniformBlockCase.cpp#L1829-L1834), and [`generateComputeShader()`](../../../modules/vulkan/ubo/vktUniformBlockCase.cpp#L1888-L1893). |
| Buffer placement | `per_block_buffer` and `single_buffer` come from [`bufferModes[]`](../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L485-L490); [`UniformBlockCase::BufferMode`](../../../modules/vulkan/ubo/vktUniformBlockCase.hpp#L438-L444) defines single shared-buffer and per-block-buffer modes. |
| Arrays and instance arrays | Fixed cases include array sizes `3`, nested sizes `4`/`3` and `2`/`4`/`3`, instance-array count `3`, and unsized-array size `19` in the corresponding registration blocks. |
| Random features | Random generation is controlled by feature bits such as vectors, matrices, arrays, structs, instance arrays, 8-bit/16-bit storage, `std430`, scalar layout, descriptor indexing, and out-of-order offsets in [`FeatureBits`](../../../modules/vulkan/ubo/vktRandomUniformBlockCase.hpp#L39-L64). |

## Support / Feature Requirements

[`UniformBlockCase::checkSupport()`](../../../modules/vulkan/ubo/vktUniformBlockCase.cpp#L2671-L2691) gates 16-bit storage on `uniformAndStorageBuffer16BitAccess`, 8-bit storage on `uniformAndStorageBuffer8BitAccess`, `std430` layouts on scalar-block-layout or uniform-buffer-standard-layout support, scalar layouts on `scalarBlockLayout`, descriptor-indexing cases on uniform-buffer non-uniform indexing plus runtime descriptor arrays, and unsized arrays on `shaderUniformBufferUnsizedArray` when Vulkan SC is not in use.

## Verification Methods

[`UniformBlockCase::delayedInit()`](../../../modules/vulkan/ubo/vktUniformBlockCase.cpp#L2623-L2669) computes a reference layout, allocates host reference storage, fills values, and generates shaders. Reference layout rules for `std140`, `std430`, relaxed, and scalar alignment are implemented in [`computeStd140BaseAlignment()`](../../../modules/vulkan/ubo/vktUniformBlockCase.cpp#L410-L450), [`computeStd430BaseAlignment()`](../../../modules/vulkan/ubo/vktUniformBlockCase.cpp#L452-L489), [`computeRelaxedBlockBaseAlignment()`](../../../modules/vulkan/ubo/vktUniformBlockCase.cpp#L491-L525), and [`computeScalarBlockAlignment()`](../../../modules/vulkan/ubo/vktUniformBlockCase.cpp#L527-L547). Generated shaders compare UBO reads against embedded reference values in [`generateCompareSrc()`](../../../modules/vulkan/ubo/vktUniformBlockCase.cpp#L1612-L1733). Runtime execution renders or dispatches to an image and passes only when the readback image is entirely white in [`UniformBlockCaseInstance::iterate()`](../../../modules/vulkan/ubo/vktUniformBlockCase.cpp#L2356-L2403).

## Test Principles Observed

- The category compares device UBO loads against a source-computed reference layout and generated reference values instead of relying on fixed golden images, as shown by [`computeReferenceLayout()`](../../../modules/vulkan/ubo/vktUniformBlockCase.cpp#L719-L767), [`generateValues()`](../../../modules/vulkan/ubo/vktUniformBlockCase.cpp#L838-L854), and shader comparison generation in [`generateCompareSrc()`](../../../modules/vulkan/ubo/vktUniformBlockCase.cpp#L1612-L1733).
- Fixed families isolate specific layout shapes, while the `random` family combines feature bits and deterministic seeds via [`createRandomCaseGroup()`](../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L409-L420) and [`RandomUniformBlockCase`](../../../modules/vulkan/ubo/vktRandomUniformBlockCase.cpp#L55-L99).
- Graphics cases propagate vertex and fragment comparison results into color, while compute cases write comparison results to a storage image; both paths use the same final all-white image criterion in [`UniformBlockCaseInstance::iterate()`](../../../modules/vulkan/ubo/vktUniformBlockCase.cpp#L2222-L2354) and [`UniformBlockCaseInstance::iterate()`](../../../modules/vulkan/ubo/vktUniformBlockCase.cpp#L2356-L2403).

## Notes / Uncertainties

- Mustpass inspection confirmed the direct `ubo` children listed in the hierarchy tree. The generated leaf set is large, so this page documents direct groups and source-observed parameter generators rather than enumerating every leaf case.
- [`doc/testspecs/VK/apitests.adoc`](../../../../../doc/testspecs/VK/apitests.adoc) was searched for `ubo`, `uniform buffer`, and `uniform block`; no category-specific UBO test-plan section was found in that inspected file, so this page relies on source and mustpass evidence.