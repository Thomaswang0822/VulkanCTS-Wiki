# Understanding Brief: nested unsized arrays

## One-Sentence Test Purpose

This test checks whether storage-buffer layout, descriptor-array indexing, and nested runtime-sized array access agree when a compute shader writes generated structures through non-uniform descriptor indices.

## Background Knowledge

### Runtime-sized arrays and `std430` storage buffers

A runtime-sized array is the final member of a storage-buffer block. Its element count is determined by the buffer range available at runtime, while its element stride still follows the declared buffer layout rules. `std430` lays out the structure and its nested arrays using explicit alignment and stride rules. Here, the runtime-sized member is nested in a generated `Root` structure, so a wrong stride can shift every later element.

### Descriptor arrays and non-uniform indexing

A descriptor array contains multiple storage-buffer descriptors. A shader index derived from a local invocation may differ between invocations, so the index must be marked non-uniform when the implementation cannot assume a single descriptor is selected for the whole execution group. This test uses one physical buffer with separate ranged descriptors. Each descriptor range represents one `Root` element.

## One Concrete Example

Conceptually, for an outer array length of four and two guard descriptors on each side, the descriptor array has eight entries:

```text
descriptor index:  0   1   2   3   4   5   6   7
active element:   pad pad  R0  R1  R2  R3 pad pad
```

The compute shader uses `root[nonuniformEXT(gl_LocalInvocationID.x + guardZoneCount)]`. Invocation `0` writes `R0`, and invocation `3` writes `R3`. The generated `Root` type contains fixed arrays, structures, arrays of structures, and a final unsized array field. The snippet above is a conceptual simplification, not the exact generated declaration.

## End-to-End Test Flow

```text
[host] derive a deterministic generated structure from the test seed
[host] choose the outer array length and obtain the generated structure size
[host] allocate one host-visible, coherent storage buffer for descriptor-sized ranges
[host] create a storage-buffer descriptor array with leading and trailing guard ranges
[host] generate a compute shader with the generated structures and `std430` root array
[host] create the compute pipeline, bind the descriptor array, and push `seed` and `visits`
[host] initialize every buffer dword to 1
[host] dispatch one workgroup with `m_outerArrayLen` local invocations
[device] each invocation selects one active descriptor range non-uniformly and walks the nested structure
[device] the generated walk writes successive values into the selected structure
[host] reconstruct the expected structures, compare active ranges and guard ranges, and decide pass/fail
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

`generateStructure()` seeds `std::rand()` from the test seed. It builds scalar, `vec3`, and `mat2x3` fields, fixed arrays, two generated structures, arrays of structures, a shuffled aggregate, and a final unsized array of the largest generated structure. The outer array length is 4, 8, or 12, and the nested fixed-array length is 3, 6, or 9. `initPrograms()` prints these types into compute GLSL and emits a `comp_<outerArrayLen>` program.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|---|---:|---:|---:|---:|---|
| One storage buffer | yes | yes, through every descriptor | yes | yes | Holds guard ranges and active `Root` elements. |
| Storage-buffer descriptor array | yes | yes, binding 0 | selected descriptors are accessed | no | Maps local invocation indices to ranged views of the buffer. |
| Push constants | yes | yes | read | no | Supplies `seed` and the generated structure visit count. |
| Compute pipeline and command buffer | yes | yes | executes shader | no | Performs the single dispatch. |

Each descriptor range starts at the next `descriptorArrayStride`, where the stride is the generated structure's logical size aligned to `minStorageBufferOffsetAlignment`.

## What Is Checked

- The buffer starts entirely filled with `1`, including both guard regions.
- For each active outer element, the host clones the generated structure, runs its `loop(seed)`, and serializes that expected value at the corresponding aligned offset.
- The host deserializes the device result using the same generated structure model.
- The comparison covers all dwords in the two guard ranges and the active ranges. Any mismatch reports its dword index and expected and observed hexadecimal values.
- The test passes only when every compared dword matches. The test does not use a tolerance in this verification path.

## Behavior Parameter Identification

> **Behavior parameter:** generated outer descriptor-array length
>
> **Candidate values:** 4, 8, 12

The registered test has one test case leaf. The generated outer length is the primary behavioral axis because it changes the number of local invocations, descriptor ranges, active structure instances, and non-uniform index values. The nested array length and generated structure contents are seed-derived variations within that behavior.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `4` | Layout or stride handling for a four-element descriptor-indexed active range; descriptor-array indexing or guard-zone corruption. |
| `8` | Layout or stride handling for an eight-element descriptor-indexed active range; descriptor-array indexing or guard-zone corruption. |
| `12` | Layout or stride handling for a twelve-element descriptor-indexed active range; descriptor-array indexing or guard-zone corruption. |

## Important Variations and Special Cases

- The test requires Vulkan 1.2 `runtimeDescriptorArray` and `shaderStorageBufferArrayNonUniformIndexing`. Unsupported devices are skipped before execution.
- The generated nested array is runtime-sized only at the final `Root` member. Other generated arrays have fixed lengths selected during generation.
- Two guard ranges precede and follow the active ranges. Because the shader writes only the active indices, changed guard dwords indicate an out-of-range write or an incorrect descriptor/range calculation.
- The descriptor range stride is aligned to the device's `minStorageBufferOffsetAlignment`, so the test exercises both generated structure size and descriptor offset alignment.

## Source Mapping

| Topic | Source link | Why it matters |
|---|---|---|
| Test registration | [`appendNestedUnsizedArraysTests()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L1155-L1158) | Adds the exact `nested_unsized_arrays` test case leaf. |
| Parent registration | [`createUnsizedArrayTests()`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L2202-L2231) | Places the leaf under `ssbo.unsized_array_length`. |
| Structure generation | [`generateStructure()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L1027-L1104) | Defines generated types, fixed arrays, and the final unsized array. |
| Feature gate | [`NestedUnsizedArraysTestCase::checkSupport()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L1106-L1117) | Requires both descriptor-array features. |
| Shader generation | [`NestedUnsizedArraysTestCase::initPrograms()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L1119-L1151) | Emits the compute shader, `std430` block, and non-uniform root access. |
| Runtime and verification | [`NestedUnsizedArraysTestInstance::iterate()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L887-L959), [`verify()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L961-L1011) | Defines allocation, descriptor updates, dispatch, expected data, and comparison. |
| Shared layout support | [`SSBOLayoutCase`](../../../modules/vulkan/ssbo/vktSSBOLayoutCase.hpp#L293-L330) and [`generateComputeShader()`](../../../modules/vulkan/ssbo/vktSSBOLayoutCase.cpp#L1529-L1644) | Provides the shared SSBO layout model and generated compute-test conventions used by the family. |
| Mustpass | [`vk-default/ssbo.txt`](../../../mustpass/main/vk-default/ssbo.txt#L12225), [`vksc-default/ssbo.txt`](../../../mustpass/main/vksc-default/ssbo.txt#L12162) | Confirms Vulkan and Vulkan SC registration. |
| Vulkan specification | [`descriptorsets.adoc`](../../../vulkan-docs/src/chapters/descriptorsets.adoc), [`features.adoc`](../../../vulkan-docs/src/chapters/features.adoc), [`resources.adoc`](../../../vulkan-docs/src/chapters/resources.adoc), [`shaders.adoc`](../../../vulkan-docs/src/chapters/shaders.adoc) | Spec chapters consulted for descriptor arrays, feature requirements, buffer resources, and shader execution. |

## Questions / Risk Points for User Audit

- The exact generated GLSL varies with the seed. Is the conceptual descriptor map sufficient, or should a fixed seed be selected for a full shader walkthrough?
- The repository's local spec sources describe the relevant descriptor and buffer rules across shared chapters rather than exposing a single SSBO-specific chapter. Claims here stay at the feature, descriptor, alignment, and runtime-sized-array level.
- The mustpass entries confirm both API and Vulkan SC paths, but this inspection did not execute the test binary.

## Conversion Notes for Final Wiki Rewrite

- Keep the final `Background Knowledge` to concise bullets about runtime-sized storage-buffer arrays, descriptor arrays, and non-uniform indexing.
- Use the descriptor-map example only if it remains useful after the formal parameter table is added.
- Make generated outer array length the primary behavior parameter and retain `4`, `8`, and `12` as the values.
- Copy the `### Failure Cause Mapping` table directly into the final page. Write `### Cause Analysis` separately from the test's dword comparison and guard-zone semantics.
- Explain the generated shader in `## Shader Analysis`; a fixed seed is needed for a fully reconstructed representative walkthrough.
- Keep source links in a focused appendix rather than repeating them in every paragraph.
