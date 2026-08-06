## Overview

**Core question:** Does a compute shader access every intended element of a generated nested, runtime-sized SSBO layout through a non-uniformly indexed storage-buffer descriptor array, while preserving the checked leading guard ranges?

- This page documents the `nested_unsized_arrays` test case leaf under the `ssbo.unsized_array_length` test family. The parent creates the family, while [`vktSSBOLayoutNestedUnsizedArraysTests.cpp`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L829-L1158) implements this leaf.
- The test generates nested structures containing scalars, vectors, matrices, fixed arrays, arrays of structures, and a final runtime-sized array. It creates a ranged storage-buffer descriptor for each outer element.
- One compute workgroup selects descriptor ranges with `nonuniformEXT`, writes the generated structure contents, and leaves two descriptor ranges at each end untouched.
- The host reconstructs the expected data and compares every dword in the two leading ranges and the active ranges; the two trailing ranges are allocated but not compared.

## Background Knowledge

- A runtime-sized array is the final member of a storage-buffer block. Its available element count comes from the buffer range, but its elements still follow the block layout's alignment and stride rules.
- A descriptor array provides multiple storage-buffer descriptors at one binding. If invocations use different descriptor indices, the shader marks the index non-uniform so descriptor selection is valid for that access pattern.
- `std430` controls the placement and stride of structure members and arrays in this storage buffer. The test depends on those rules matching the host's generated structure model.

## Registration Hierarchy

```text
ssbo.unsized_array_length
└── nested_unsized_arrays
```

[`createUnsizedArrayTests()`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L2202-L2231) creates the parent test family, and [`appendNestedUnsizedArraysTests()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L1155-L1158) adds this test case leaf. Mustpass includes `dEQP-VK.ssbo.unsized_array_length.nested_unsized_arrays` and `dEQP-VKSC.ssbo.unsized_array_length.nested_unsized_arrays`.

## Parameter Dimensions and Observed Values

| Dimension | Registered or generated values | Meaning in this test | Evidence |
|---|---|---|---|
| Test case leaf | `nested_unsized_arrays` | Selects the generated nested-layout and descriptor-array test. | [`appendNestedUnsizedArraysTests()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L1155-L1158) |
| Outer descriptor-array length | `4`, `8`, `12` | Sets the local X size, active `Root` elements, and descriptor-array length after guard ranges are added. | [`generateStructure()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L1097-L1103) |
| Nested final-array length | `3`, `6`, `9` | Sets the generated final unsized-array member's element count for the generated test structure. | [`generateStructure()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L1097-L1103) |
| Structure contents | Seed-derived arrangement of `float`, `vec3`, `mat2x3`, fixed arrays, structures, and arrays of structures | Varies the layout paths that the generated shader walks before reaching the final unsized array. | [`generateStructure()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L1030-L1103) |
| Guard ranges | Two leading and two trailing descriptor ranges | The two leading ranges detect writes before the active outer-array elements. Two trailing ranges are allocated but `verify()` does not compare them. | [`NestedUnsizedArraysTestCase`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L849-L867), [`verify()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L961-L1011) |

The descriptor range stride is the generated structure's logical size aligned to `minStorageBufferOffsetAlignment`. The full buffer contains `guardZoneCount + outerArrayLen + guardZoneCount` such ranges.

## Behavior Parameters

The primary behavioral axis is the generated outer descriptor-array length. It changes how many compute invocations select descriptors and how many active `Root` elements the verifier expects.

### `4` - four active descriptor ranges

The workgroup has four local invocations. Each invocation selects one of four active ranges after the two leading guard ranges and writes one generated `Root` element.

### `8` - eight active descriptor ranges

The same generated access pattern covers eight active descriptor ranges. This expands the set of invocation-derived non-uniform descriptor indices and expected structures.

### `12` - twelve active descriptor ranges

The workgroup covers twelve active descriptor ranges. The host checks the same two leading ranges before the active data; the two trailing ranges remain allocated but are not part of the comparison.

The nested final-array length and generated field ordering vary the data layout within each selected range. They are generated structure variations rather than separate registered behavior values.

## Shader Analysis

[`NestedUnsizedArraysTestCase::initPrograms()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L1119-L1151) emits one compute GLSL source per generated outer length. It enables `GL_EXT_nonuniform_qualifier`, sets `local_size_x` to that length, prints the generated structure declarations, and declares a `std430` storage-buffer array at binding 0.

The shader receives `seed` and `visits` through push constants. Invocation `x` starts its generated walk with `seed + x * visits` and accesses `root[nonuniformEXT(x + 2)]`. The `+ 2` skips the leading guard ranges. `SG::generateLoops()` then emits the nested member traversal and writes successive values.

The structure and GLSL text are seed-derived. This page therefore explains the stable generator path rather than presenting a reconstructed fixed-seed shader walkthrough. The source's shader build path uses the source collection default SPIR-V target; no standalone SPIR-V reconstruction is included here.

## Runtime Execution and Result Checking

- [`NestedUnsizedArraysTestInstance::iterate()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L887-L959) computes an aligned descriptor stride, allocates one host-visible coherent storage buffer, and makes one storage-buffer descriptor range for each guard or active element.
- The descriptor set layout has one storage-buffer array binding. The test writes every array element at binding 0, with each descriptor pointing at the next aligned range of the same buffer.
- The host fills the entire buffer with `1`, creates a compute pipeline from the generated shader, binds the descriptor set, pushes `seed` and `visits`, and dispatches `1 x 1 x 1` workgroups. The shader's local X size supplies the active invocation count.
- After `submitCommandsAndWait()`, [`verify()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L961-L1011) starts with an all-`1` expected buffer. It clones the generated structure for each active outer element, runs its host-side loop, serializes the expected result at the aligned offset, then compares the two leading ranges and all active ranges. Although the expected buffer also contains two trailing ranges, the comparison count excludes them.
- A mismatch logs its dword index and expected and observed hexadecimal values. The case passes only when all compared dwords match.

The test first requires Vulkan 1.2 `runtimeDescriptorArray` and `shaderStorageBufferArrayNonUniformIndexing`; devices without either feature skip the case before pipeline creation.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `4` | Layout or stride handling for a four-element descriptor-indexed active range; descriptor-array indexing or guard-zone corruption. |
| `8` | Layout or stride handling for an eight-element descriptor-indexed active range; descriptor-array indexing or guard-zone corruption. |
| `12` | Layout or stride handling for a twelve-element descriptor-indexed active range; descriptor-array indexing or guard-zone corruption. |

### Cause Analysis

#### Generated layout or stride handling

**Possible failure symptoms:** The dword comparison reports a mismatch in an active range. The reported offset may point to a member after a nested array or to data in a later descriptor range.

**Possible implementation causes:** A driver compiler, descriptor-range calculation, or storage-buffer access path may disagree with the generated `std430` member offsets or array strides. The host comparison derives expected bytes from the same generated structure model, so a mismatch identifies disagreement between that model and device-visible access rather than a tolerance issue.

#### Non-uniform descriptor-array indexing

**Possible failure symptoms:** One or more active ranges retain `1` values or contain data expected for another invocation, while other ranges match.

**Possible implementation causes:** The compute shader marks the invocation-derived descriptor index with `nonuniformEXT`, and the support gate requires `shaderStorageBufferArrayNonUniformIndexing`. A failure can indicate incorrect descriptor selection or access through that non-uniform index. Source-level investigation is needed to attribute a particular mismatch to compiler lowering, descriptor management, or another implementation layer.

#### Guard-zone corruption

**Possible failure symptoms:** The comparison reports a mismatch in a leading guard range, where the expected value remains `1`. Writes confined to the two trailing allocated ranges are not observed by this verifier.

**Possible implementation causes:** An out-of-range generated access, a wrong descriptor offset or range, or an incorrect active-index calculation can write a leading guard range. The test does not isolate which layer produced the write, so source-level investigation is needed after the logged dword offset identifies the affected range; corruption confined to trailing allocated ranges cannot cause this test to fail.

## Case Pruning

The test exposes one registered test case leaf, not a cross-product of user-selectable leaves. Its internally generated layouts use a deterministic seed, which can be overridden through the CTS base-seed command-line setting during `delayedInit()`. Devices that lack either required Vulkan 1.2 descriptor-indexing feature skip the case.

## Key Takeaways

- The test checks generated nested SSBO layouts through a storage-buffer descriptor array, not a single contiguous shader declaration.
- Every local invocation selects an active descriptor range with a non-uniform index, then walks and writes its own generated `Root` element.
- Alignment affects descriptor range boundaries, while `std430` affects contents inside each range. Both must agree with the host model.
- The two leading guard ranges turn writes before the active outer array into observable dword mismatches; the two trailing allocated ranges are not validated.

## Source Reference Appendix

| Evidence | Source |
|---|---|
| Registration under the parent test family | [`createUnsizedArrayTests()`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L2202-L2231), [`appendNestedUnsizedArraysTests()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L1155-L1158) |
| Generated structure shapes and size choices | [`NestedUnsizedArraysTestCase::generateStructure()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L1027-L1104) |
| Required descriptor-indexing features | [`NestedUnsizedArraysTestCase::checkSupport()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L1106-L1117) |
| Generated compute shader | [`NestedUnsizedArraysTestCase::initPrograms()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L1119-L1151) |
| Buffer, descriptors, dispatch, and result status | [`NestedUnsizedArraysTestInstance::iterate()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L887-L959) |
| Expected-data construction and dword comparison | [`NestedUnsizedArraysTestInstance::verify()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L961-L1011) |
| Shared SSBO layout support | [`vktSSBOLayoutCase.hpp`](../../../modules/vulkan/ssbo/vktSSBOLayoutCase.hpp#L38-L330), [`generateComputeShader()`](../../../modules/vulkan/ssbo/vktSSBOLayoutCase.cpp#L1529-L1644) |
| Vulkan and Vulkan SC mustpass entries | [`vk-default/ssbo.txt`](../../../mustpass/main/vk-default/ssbo.txt#L12225), [`vksc-default/ssbo.txt`](../../../mustpass/main/vksc-default/ssbo.txt#L12162) |
