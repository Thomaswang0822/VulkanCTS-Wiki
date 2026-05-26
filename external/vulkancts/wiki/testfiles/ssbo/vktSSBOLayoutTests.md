# vktSSBOLayoutTests.cpp

## Overview

[`vktSSBOLayoutTests.cpp`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L1) is the root registration and major case-definition file for the Vulkan CTS [`ssbo`](../../../modules/vulkan/vktTestPackage.cpp#L1357) category. The category factory [`createTests()`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L2235-L2255) constructs the top-level `ssbo` group, registers the main writable layout suite, appends unsized-array-length tests, registers a read-only variant of the layout suite, registers a physical-storage-buffer variant, and delegates the `corner_case` group to [`vktSSBOCornerCase.cpp`](../../../modules/vulkan/ssbo/vktSSBOCornerCase.cpp#L330-L334).

## Role

Registration / implementation file. It owns the category root and the generated layout families through [`SSBOLayoutTests::init()`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L1297-L2188). Shared execution, reference layout calculation, compute-shader generation, support checks, and result comparison are implemented in [`vktSSBOLayoutCase.cpp`](../../../modules/vulkan/ssbo/vktSSBOLayoutCase.cpp#L2653-L2777). The nested unsized-array leaf under `unsized_array_length` is appended from [`vktSSBOLayoutNestedUnsizedArraysTests.cpp`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L1155-L1158).

## Source Code

- Primary source: [`vktSSBOLayoutTests.cpp`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L1)
- Public factory declaration: [`vktSSBOLayoutTests.hpp`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.hpp#L29-L35)
- Root package registration: [`TestPackage::init()`](../../../modules/vulkan/vktTestPackage.cpp#L1345-L1358) and [`TestPackageSC::init()`](../../../modules/vulkan/vktTestPackage.cpp#L1413-L1426)
- Shared execution support: [`vktSSBOLayoutCase.cpp`](../../../modules/vulkan/ssbo/vktSSBOLayoutCase.cpp#L2291-L2648)
- Delegated corner-case registration: [`createSSBOCornerCaseTests()`](../../../modules/vulkan/ssbo/vktSSBOCornerCase.cpp#L330-L334)
- Delegated nested-unsized-array registration: [`appendNestedUnsizedArraysTests()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L1155-L1158)

## Registration Hierarchy

```text
ssbo
├── layout
├── unsized_array_length
├── readonly
├── phys
└── corner_case
```

## Test Families

### layout — Writable shader-storage-buffer layout tests

The `layout` group is registered directly by [`createTests()`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L2235-L2241) through an [`SSBOLayoutTests`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L1269-L1292) instance whose displayed group name is `layout`. Its [`init()`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L1297-L2188) builds direct layout-shape families including scalar/vector/matrix basic members, fixed arrays, unsized arrays, nested arrays, structs, struct arrays, unsized struct arrays, multiple blocks, and deterministic random layouts. Writable-only families are guarded by `if (!m_readonly)` blocks, for example [`2_level_array`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L1554-L1598), [`single_struct_array`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L1731-L1764), and [`multi_basic_types`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L1988-L2034).

### unsized_array_length — Runtime array length and descriptor range tests

The `unsized_array_length` group is registered by [`addTestGroup()`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L2239-L2242). [`createUnsizedArrayTests()`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L2202-L2231) adds explicit cases for no-offset and offset descriptor ranges, `VK_WHOLE_SIZE`, variable pointers, and non-Vulkan SC 64-bit-size variants, then appends `nested_unsized_arrays` from [`appendNestedUnsizedArraysTests()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L1155-L1158). The runtime check computes the expected unsized-array length from the bound descriptor range and compares it with shader output in [`ssboUnsizedArrayLengthTest()`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L1243-L1258).

### readonly — Read-only variant of layout tests

The `readonly` group is registered by [`createTests()`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L2243-L2247). It contains an [`SSBOLayoutTests`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L1269-L1292) child named `layout`, but with the `readonly` constructor argument set to `true` at registration time. In the generated `SSBOLayoutTests::init()` tree, families protected by `if (!m_readonly)` are omitted from this variant, while read-only-safe families such as [`single_basic_type`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L1356-L1410), [`single_basic_array`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L1412-L1454), [`basic_unsized_array`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L1456-L1496), and [`single_struct`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L1697-L1729) remain registered.

### phys — Physical-storage-buffer-address variant of layout tests

The `phys` group is registered by [`createTests()`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L2248-L2250). It contains a `layout` child with `usePhysStorageBuffer` set to `true`, causing the execution path to request shader-device-address buffer usage, query GPU buffer addresses, and push those addresses to the compute shader in [`SSBOLayoutCaseInstance::iterate()`](../../../modules/vulkan/ssbo/vktSSBOLayoutCase.cpp#L2352-L2359) and [`SSBOLayoutCaseInstance::iterate()`](../../../modules/vulkan/ssbo/vktSSBOLayoutCase.cpp#L2463-L2486). Support is gated on buffer-device-address availability in [`SSBOLayoutCase::checkSupport()`](../../../modules/vulkan/ssbo/vktSSBOLayoutCase.cpp#L2731-L2732).

### corner_case — Delegated long-shader buffer-reference crash regression

The `corner_case` group is registered through [`createSSBOCornerCaseTests()`](../../../modules/vulkan/ssbo/vktSSBOCornerCase.cpp#L330-L334), which returns a group named `corner_case` and adds the `long_shader_bitwise_and` case. This file is documented separately in [`vktSSBOCornerCase.md`](vktSSBOCornerCase.md).

## Parameter Dimensions

| Dimension | Evidence-backed values |
|---|---|
| Basic data types | [`basicTypes[]`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L1299-L1312) includes float, int, uint, bool, matrices, 8-bit integer, 16-bit integer, and 16-bit float scalar/vector forms. |
| Layout qualifiers | [`layoutFlags[]`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L1320-L1328) registers `std140`, `std430`, and `scalar`; layout flag definitions live in [`BufferVarFlags`](../../../modules/vulkan/ssbo/vktSSBOLayoutCase.hpp#L38-L59). |
| Matrix layout and access | [`matrixFlags[]`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L1330-L1334) registers row-major and column-major variants, while [`matrixLoadTypes`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L1346-L1349) and [`matrixStoreTypes`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L1351-L1354) add component-load and column-store variants. |
| Buffer placement | [`bufferModes[]`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L1336-L1341) registers `per_block_buffer` and `single_buffer`; the execution code either allocates one buffer per block or packs blocks into one buffer aligned to `minStorageBufferOffsetAlignment` in [`SSBOLayoutCaseInstance::iterate()`](../../../modules/vulkan/ssbo/vktSSBOLayoutCase.cpp#L2369-L2432). |
| Fixed array sizes | Fixed families use array size `3`, nested array sizes `3`/`4` and `3`/`2`/`4`, unsized-array test size `19`, 64-bit unsized-array sizes derived to exceed 4 GiB, and instance-array count `3` in the corresponding registration blocks. |
| Random feature bits | [`FeatureBits`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L66-L87) controls random inclusion of vectors, matrices, arrays, structs, nested structs, instance arrays, unused members/variables, `std140`, `std430`, matrix layout, unsized arrays, arrays of arrays, relaxed layout, 16-bit/8-bit storage, scalar layout, descriptor indexing, and 64-bit indexing. |
| Random case families | [`createRandomCaseGroup()`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L604-L620) creates numbered seeded cases; [`SSBOLayoutTests::init()`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L2084-L2185) registers scalar, vector, basic, array, unsized-array, arrays-of-arrays, instance-array, nested-struct, all-feature, relaxed, scalar, and descriptor-indexing random groups, with `16bit` and `8bit` subgroups. |
| Unsized-array-length subcases | [`subcases[]`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L2204-L2218) enumerates element size, buffer size, descriptor offset usage, descriptor range, variable-pointer usage, 64-bit length handling, and case names. |

## Support / Feature Requirements

[`SSBOLayoutCase::checkSupport()`](../../../modules/vulkan/ssbo/vktSSBOLayoutCase.cpp#L2718-L2754) gates relaxed layouts on `VK_KHR_relaxed_block_layout`, 16-bit layouts on both `storageBuffer16BitAccess` and `uniformAndStorageBuffer16BitAccess`, 8-bit layouts on `storageBuffer8BitAccess`, scalar layouts on `scalarBlockLayout`, physical-storage-buffer variants on buffer-device-address support, descriptor-indexing cases on storage-buffer non-uniform indexing plus runtime descriptor arrays, non-Vulkan SC 64-bit indexing cases on `shader64BitIndexing`, and generated block counts on `maxPerStageDescriptorStorageBuffers`. The unsized-array-length helper [`checkSupportUnsizedArrays()`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L2190-L2200) additionally gates variable-pointer and 64-bit-indexing subcases.

## Verification Methods

For layout cases, [`SSBOLayoutCase::delayedInit()`](../../../modules/vulkan/ssbo/vktSSBOLayoutCase.cpp#L2756-L2777) computes a reference layout, initializes reference storage, generates deterministic initial and write values, preserves non-written data, and generates the compute shader. Runtime execution uploads storage buffers, dispatches a compute shader, barriers shader writes for host reads, checks the shader-side pass counter, invalidates mapped storage, and compares device-written data with reference write data in [`SSBOLayoutCaseInstance::iterate()`](../../../modules/vulkan/ssbo/vktSSBOLayoutCase.cpp#L2291-L2648). Unsized-array-length tests compare the shader-written runtime length against the descriptor-bound length divided by element size in [`ssboUnsizedArrayLengthTest()`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L1243-L1258).

## Test Principles Observed

- The layout suite computes expected memory layout and data values from source-side type trees rather than relying on static golden buffers, as shown by [`computeReferenceLayout()`](../../../modules/vulkan/ssbo/vktSSBOLayoutCase.cpp#L741-L767), [`generateValues()`](../../../modules/vulkan/ssbo/vktSSBOLayoutCase.cpp#L867-L870), and [`generateComputeShader()`](../../../modules/vulkan/ssbo/vktSSBOLayoutCase.cpp#L1529-L1531).
- Writable and read-only variants share one generator, with `m_readonly` controlling which families are registered and how basic cases are constructed in [`SSBOLayoutTests::init()`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L1356-L2188).
- Physical-storage-buffer coverage is implemented as a top-level wrapper variant over the same generated layout suite, using buffer-device-address support in execution rather than a separate registration file.

## Notes / Uncertainties

- Mustpass inspection confirms the direct `ssbo` children listed in the hierarchy tree in [`vk-default/ssbo.txt`](../../../mustpass/main/vk-default/ssbo.txt#L1) and [`vksc-default/ssbo.txt`](../../../mustpass/main/vksc-default/ssbo.txt#L1). The generated leaf set is large, so this page documents direct groups and source-observed generators rather than enumerating every leaf case.
