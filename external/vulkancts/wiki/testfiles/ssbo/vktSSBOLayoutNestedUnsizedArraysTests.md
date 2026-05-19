# vktSSBOLayoutNestedUnsizedArraysTests.cpp

## Overview

[`vktSSBOLayoutNestedUnsizedArraysTests.cpp`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L1) appends the `nested_unsized_arrays` leaf under `ssbo.unsized_array_length`. The test builds generated nested struct shapes with an unsized array in the generated root structure, uses descriptor arrays of storage-buffer ranges, writes through non-uniformly indexed root array elements, and verifies guard zones and expected writes after compute execution.

## Role

Implementation-heavy registered leaf file. The parent group `unsized_array_length` is created by [`createUnsizedArrayTests()`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L2202-L2231), and this file contributes the nested unsized-array child through [`appendNestedUnsizedArraysTests()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L1155-L1158).

## Source Code

- Primary source: [`vktSSBOLayoutNestedUnsizedArraysTests.cpp`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L1)
- Public append declaration: [`vktSSBOLayoutNestedUnsizedArraysTests.hpp`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.hpp#L33-L39)
- Parent unsized-array-length registration: [`createUnsizedArrayTests()`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L2202-L2231)

## Registration Hierarchy

```text
ssbo.unsized_array_length.nested_unsized_arrays
```

## Test Families

### nested_unsized_arrays — Nested generated structs with runtime-sized arrays

[`appendNestedUnsizedArraysTests()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L1155-L1158) adds one [`NestedUnsizedArraysTestCase`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L1155-L1158) named `nested_unsized_arrays`. During shader generation, the test emits `#version 450 core`, requires `GL_EXT_nonuniform_qualifier`, declares push constants, prints generated struct declarations, and declares a `std430` storage buffer whose root array is indexed with `nonuniformEXT(gl_LocalInvocationID.x + guardZoneCount)` in [`NestedUnsizedArraysTestCase::initPrograms()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L1119-L1150).

## Parameter Dimensions

| Dimension | Evidence-backed values |
|---|---|
| Generated structure shape | The generator chooses `outerArrayLen` as `((rand % typesSize) + 1) * 4`, `nestedArrayLen` as `((rand % typesSize) + 1) * 3`, builds a generated `Root` struct, and appends an unsized array field from the largest generated struct in [`generateStructure()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L1085-L1103). |
| Descriptor array layout | Runtime setup computes `descriptorArrayStride * descriptorArrayLen`, allocates one storage buffer, creates a descriptor-set layout with one storage-buffer array binding, and writes one descriptor per range in [`NestedUnsizedArraysTestInstance::iterate()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L900-L925). |
| Guard zones | The shader comments and indexes the root array as `guardZoneCount + outerArrayLen + guardZoneCount`, then writes starting at `gl_LocalInvocationID.x + guardZoneCount` in [`NestedUnsizedArraysTestCase::initPrograms()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L1137-L1147). |
| Push constants | The runtime push constant contains `seed` and `visits`, populated from `m_seed` and the generated structure visit count in [`NestedUnsizedArraysTestInstance::iterate()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L927-L933). |

## Support / Feature Requirements

[`NestedUnsizedArraysTestCase::checkSupport()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L1106-L1117) requires Vulkan 1.2 `runtimeDescriptorArray` and `shaderStorageBufferArrayNonUniformIndexing` features; it throws `NotSupportedError` if either feature is unavailable.

## Verification Methods

Runtime execution initializes the whole storage buffer to `1`, dispatches the generated compute shader once, and calls [`verify()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L955-L958). The verification entry point [`NestedUnsizedArraysTestInstance::verify()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L961-L965) checks the generated buffer contents using the same descriptor-array stride and guard-zone layout used during execution. The pass/fail status is returned directly from that verdict in [`NestedUnsizedArraysTestInstance::iterate()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L955-L958).

## Test Principles Observed

- The test targets runtime-sized arrays nested in generated aggregate layouts while using descriptor arrays and non-uniform indexing, as shown by the generated shader declarations in [`NestedUnsizedArraysTestCase::initPrograms()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L1123-L1150).
- Guard zones are part of the generated buffer model, helping detect writes outside the intended active root elements through the verification path in [`NestedUnsizedArraysTestInstance::verify()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L961-L965).

## Notes / Uncertainties

- Mustpass inspection confirms the leaf under `unsized_array_length` in `vk-default/ssbo.txt`; the line was not in the small excerpt read directly, but it is validated by the mandatory registration verifier after this page is generated.
- [`doc/testspecs/VK/apitests.adoc`](../../../../../doc/testspecs/VK/apitests.adoc) was searched for `SSBO`, `Shader Storage`, `storage buffer`, and `Storage Buffer`; no category-specific SSBO test-plan section was found.
