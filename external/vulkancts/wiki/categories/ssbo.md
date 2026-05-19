# ssbo

## Overview

The [`ssbo`](../../modules/vulkan/vktTestPackage.cpp#L1357) category verifies shader storage buffer object layout, storage-buffer descriptor binding, shader reads and writes through generated compute shaders, runtime-sized array behavior, physical-storage-buffer-address access, and one buffer-reference crash regression. The category root is implemented by [`vktSSBOLayoutTests.cpp`](../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L2235-L2255), with shared layout execution in [`vktSSBOLayoutCase.cpp`](../../modules/vulkan/ssbo/vktSSBOLayoutCase.cpp#L2291-L2648), delegated corner-case registration in [`vktSSBOCornerCase.cpp`](../../modules/vulkan/ssbo/vktSSBOCornerCase.cpp#L330-L334), and delegated nested unsized-array coverage in [`vktSSBOLayoutNestedUnsizedArraysTests.cpp`](../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L1155-L1158).

## Registration Entry Point

The Vulkan package registers `ssbo` through [`TestPackage::init()`](../../modules/vulkan/vktTestPackage.cpp#L1345-L1358), and the Vulkan SC package also registers it through [`TestPackageSC::init()`](../../modules/vulkan/vktTestPackage.cpp#L1413-L1426). The category factory [`ssbo::createTests()`](../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L2235-L2255) returns a group using the package-provided name and registers the direct children below:

```text
ssbo
├── layout
├── unsized_array_length
├── readonly
├── phys
└── corner_case
```

The `layout`, `unsized_array_length`, `readonly`, and `phys` branches are registered in [`vktSSBOLayoutTests.cpp`](../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L2235-L2250), while `corner_case` is delegated to [`createSSBOCornerCaseTests()`](../../modules/vulkan/ssbo/vktSSBOCornerCase.cpp#L330-L334).

## File Inventory

| File | Role | Notes |
|---|---|---|
| [`vktSSBOLayoutTests.cpp`](../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L1) | Root registration and implementation | Registers the category root and generated layout, readonly, phys, and unsized-array-length families. |
| [`vktSSBOLayoutTests.hpp`](../../modules/vulkan/ssbo/vktSSBOLayoutTests.hpp#L29-L35) | Public factory declaration | Declares [`createTests()`](../../modules/vulkan/ssbo/vktSSBOLayoutTests.hpp#L34) for package registration. |
| [`vktSSBOLayoutCase.cpp`](../../modules/vulkan/ssbo/vktSSBOLayoutCase.cpp#L1) | Helper / execution infrastructure | Computes reference layouts, generates compute shaders, allocates storage buffers, dispatches compute work, and compares output data. |
| [`vktSSBOLayoutCase.hpp`](../../modules/vulkan/ssbo/vktSSBOLayoutCase.hpp#L38-L59) | Helper declarations | Defines layout, access, relaxed-layout, storage-size, and descriptor-indexing flags used by layout cases. |
| [`vktSSBOCornerCase.cpp`](../../modules/vulkan/ssbo/vktSSBOCornerCase.cpp#L1) | Registered implementation file | Registers `corner_case.long_shader_bitwise_and` and implements the crash-oriented buffer-reference stress case. |
| [`vktSSBOCornerCase.hpp`](../../modules/vulkan/ssbo/vktSSBOCornerCase.hpp#L29-L34) | Public subgroup factory declaration | Declares [`createSSBOCornerCaseTests()`](../../modules/vulkan/ssbo/vktSSBOCornerCase.hpp#L33). |
| [`vktSSBOLayoutNestedUnsizedArraysTests.cpp`](../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L1) | Registered leaf implementation | Appends `unsized_array_length.nested_unsized_arrays` and implements descriptor-array nested unsized-array checks. |
| [`vktSSBOLayoutNestedUnsizedArraysTests.hpp`](../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.hpp#L33-L39) | Public append declaration | Declares [`appendNestedUnsizedArraysTests()`](../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.hpp#L38). |

## Level-3 Documents

| Source file | Wiki document |
|---|---|
| [`vktSSBOLayoutTests.cpp`](../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L1) | [`vktSSBOLayoutTests.md`](../testfiles/ssbo/vktSSBOLayoutTests.md) |
| [`vktSSBOCornerCase.cpp`](../../modules/vulkan/ssbo/vktSSBOCornerCase.cpp#L1) | [`vktSSBOCornerCase.md`](../testfiles/ssbo/vktSSBOCornerCase.md) |
| [`vktSSBOLayoutNestedUnsizedArraysTests.cpp`](../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L1) | [`vktSSBOLayoutNestedUnsizedArraysTests.md`](../testfiles/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.md) |

## Subgroup Structure and Major Themes

- `layout` is the writable generated layout suite. It registers direct layout-shape families for basic members, arrays, unsized arrays, nested arrays, struct forms, multi-block forms, and random cases in [`SSBOLayoutTests::init()`](../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L1297-L2188).
- `unsized_array_length` focuses on runtime array-length computation from storage-buffer descriptor ranges. The registration table [`subcases[]`](../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L2204-L2218) covers offset and `VK_WHOLE_SIZE` cases, variable-pointer variants, and non-Vulkan SC 64-bit range variants, then appends `nested_unsized_arrays` through [`appendNestedUnsizedArraysTests()`](../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L1155-L1158).
- `readonly` reuses `SSBOLayoutTests` with `m_readonly` enabled at registration time in [`createTests()`](../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L2243-L2247), so families guarded by `if (!m_readonly)` are omitted while read-only-safe layout checks remain.
- `phys` reuses `SSBOLayoutTests` with physical-storage-buffer support enabled in [`createTests()`](../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L2248-L2250); the execution path requests shader-device-address-capable buffers and passes buffer device addresses through push constants in [`SSBOLayoutCaseInstance::iterate()`](../../modules/vulkan/ssbo/vktSSBOLayoutCase.cpp#L2352-L2359) and [`SSBOLayoutCaseInstance::iterate()`](../../modules/vulkan/ssbo/vktSSBOLayoutCase.cpp#L2463-L2486).
- `corner_case` contains `long_shader_bitwise_and`, a buffer-reference stress case whose pass condition is that dispatching the generated long comparison shader does not crash in [`SSBOCornerCaseInstance::iterate()`](../../modules/vulkan/ssbo/vktSSBOCornerCase.cpp#L300-L307).

## Recurring Parameter Dimensions

| Dimension | Observed source evidence |
|---|---|
| Data types | [`basicTypes[]`](../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L1299-L1312) includes scalar, vector, matrix, boolean, 8-bit integer, 16-bit integer, and 16-bit floating-point forms. |
| Layout modes | [`layoutFlags[]`](../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L1320-L1328) registers `std140`, `std430`, and `scalar`; relaxed layout appears in multi-basic-type and random families through [`LAYOUT_RELAXED`](../../modules/vulkan/ssbo/vktSSBOLayoutCase.hpp#L53-L59) and [`allRelaxed`](../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L2078-L2082). |
| Matrix forms | [`matrixFlags[]`](../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L1330-L1334), [`matrixLoadTypes`](../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L1346-L1349), and [`matrixStoreTypes`](../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L1351-L1354) combine row/column major layout, full versus component matrix loads, and full versus column stores. |
| Buffer placement | [`bufferModes[]`](../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L1336-L1341) registers per-block-buffer and single-buffer modes; runtime allocation follows those modes in [`SSBOLayoutCaseInstance::iterate()`](../../modules/vulkan/ssbo/vktSSBOLayoutCase.cpp#L2369-L2432). |
| Array and instance sizes | Fixed registration code uses array size `3`, unsized-array size `19`, nested dimensions such as `3`/`4`, `3`/`2`/`4`, and `2`/`4`/`3`, and instance-array count `3` in the corresponding family blocks. |
| Random coverage bits | [`FeatureBits`](../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L66-L87) controls vectors, matrices, arrays, structs, nested structs, instance arrays, unused variables/members, layouts, matrix layout, unsized arrays, arrays of arrays, relaxed/scalar layout, 16-bit/8-bit storage, descriptor indexing, and 64-bit indexing. |
| Descriptor and runtime-array dimensions | [`createUnsizedArrayTests()`](../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L2202-L2231) varies descriptor offsets/ranges and 64-bit lengths, while nested unsized arrays vary generated struct shape, descriptor-array length/stride, and guard-zone-protected root array writes in [`vktSSBOLayoutNestedUnsizedArraysTests.cpp`](../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L900-L958). |

## Recurring Support Requirements

The shared layout gate [`SSBOLayoutCase::checkSupport()`](../../modules/vulkan/ssbo/vktSSBOLayoutCase.cpp#L2718-L2754) checks relaxed block layout, 16-bit storage-buffer and uniform-and-storage-buffer access, 8-bit storage-buffer access, scalar block layout, physical storage buffer pointers, descriptor indexing over storage buffers, non-Vulkan SC 64-bit indexing, and the maximum per-stage storage-buffer descriptor count. Unsized-array-length tests add variable-pointer and 64-bit-indexing gates in [`checkSupportUnsizedArrays()`](../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L2190-L2200). Nested unsized arrays require `runtimeDescriptorArray` and `shaderStorageBufferArrayNonUniformIndexing` in [`NestedUnsizedArraysTestCase::checkSupport()`](../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L1106-L1117). The corner-case subgroup requires buffer-device-address support in [`CornerCase::createInstance()`](../../modules/vulkan/ssbo/vktSSBOCornerCase.cpp#L317-L322).

## Recurring Verification Methods

Layout cases compute expected offsets and reference data in [`SSBOLayoutCase::delayedInit()`](../../modules/vulkan/ssbo/vktSSBOLayoutCase.cpp#L2756-L2777), generate compute shaders through [`generateComputeShader()`](../../modules/vulkan/ssbo/vktSSBOLayoutCase.cpp#L1529-L1531), upload initial storage-buffer contents, dispatch compute, barrier shader writes for host reads, verify a shader-side pass counter, and compare device-written data with reference write data in [`SSBOLayoutCaseInstance::iterate()`](../../modules/vulkan/ssbo/vktSSBOLayoutCase.cpp#L2291-L2648). Runtime array-length tests compare the shader-reported length against `boundLength / elementSize` in [`ssboUnsizedArrayLengthTest()`](../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L1243-L1258). Nested unsized arrays verify generated buffer contents after dispatch in [`NestedUnsizedArraysTestInstance::iterate()`](../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L955-L958). The corner case passes when dispatch completes without a crash in [`SSBOCornerCaseInstance::iterate()`](../../modules/vulkan/ssbo/vktSSBOCornerCase.cpp#L300-L307).

## Relationship to the Test Plan

[`doc/testspecs/VK/apitests.adoc`](../../../../doc/testspecs/VK/apitests.adoc) was searched for `SSBO`, `Shader Storage`, `storage buffer`, and `Storage Buffer`; no category-specific SSBO test-plan section was found in that inspected file. The factual claims above therefore rely on source and mustpass evidence under [`external/vulkancts/`](../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L1).

## Notes / Uncertainties

- Mustpass inspection confirms the five direct `ssbo` children listed above in [`vk-default/ssbo.txt`](../../mustpass/main/vk-default/ssbo.txt#L1) and [`vksc-default/ssbo.txt`](../../mustpass/main/vksc-default/ssbo.txt#L1).
- Level-3 pages are limited to registered source files: [`vktSSBOLayoutCase.cpp`](../../modules/vulkan/ssbo/vktSSBOLayoutCase.cpp#L1) is important execution infrastructure but does not register its own tests, so it is documented through source links rather than a separate Level-3 page.
