## Overview

**Core question:** Do generated compute shaders and the CTS reference model agree on where SSBO values live, which values they may access, and what they must write?

- This page covers the implementation-bearing `vktSSBOLayoutTests.cpp` source for the `ssbo` test category. Its `SSBOLayoutTests` class implements the generated `layout` suite and its `readonly` and `phys` wrappers; the same file implements `unsized_array_length`.
- The suite builds storage-buffer block shapes from scalars, vectors, matrices, arrays, structs, and seeded random combinations. It computes a reference byte layout and expected data before it generates and dispatches a compute shader.
- `layout` checks writable storage-buffer access, `readonly` retains read-safe layouts, and `phys` uses buffer device addresses for the same generated layout shapes. `unsized_array_length` checks the length exposed by a runtime array for a descriptor's offset and range.
- `corner_case` is registered here but implemented by [`vktSSBOCornerCase.cpp`](../../../modules/vulkan/ssbo/vktSSBOCornerCase.cpp#L330-L334). The delegated `nested_unsized_arrays` leaf is appended under `unsized_array_length` by [`vktSSBOLayoutNestedUnsizedArraysTests.cpp`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L1155-L1158).

## Background Knowledge

- A storage buffer gives a shader a structured view of bytes in a `VkBuffer`. Layout rules determine member offsets and array or matrix strides. SPIR-V records the storage-buffer interface with decorations such as `Block`, `Offset`, `ArrayStride`, and `MatrixStride` ([Shader Interfaces](../../../../vulkan-docs/src/chapters/interfaces.adoc#interfaces-resources)).
- A descriptor set layout defines the type, count, and shader-stage access of each binding, and associates descriptor bindings with resources ([Descriptor Set Layout](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#descriptors-setlayout)). The generated-layout harness binds a pass counter plus one or more storage buffers; the separate `unsized_array_length` tests use two storage-buffer bindings instead.
- A GLSL runtime array has no declared final count. `length()` reflects the descriptor-visible range, so a descriptor offset and `VK_WHOLE_SIZE` alter the value that the shader observes.

## Registration Hierarchy

```text
ssbo
├── layout
├── unsized_array_length
├── readonly
├── phys
└── corner_case
```

[`createTests()`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L2235-L2255) builds this hierarchy. The direct paths are present in [`vk-default/ssbo.txt`](../../../mustpass/main/vk-default/ssbo.txt#L1), including representative `layout`, `unsized_array_length`, `readonly`, `phys`, and `corner_case` leaves. `vksc-default/ssbo.txt` also contains `layout`, `readonly`, `phys`, and `corner_case` leaves; the source excludes its 64-bit unsized-array subcases under `CTS_USES_VULKANSC`.

## Parameter Dimensions and Observed Values

| Dimension | Values and effect on the test |
|-----------|-------------------------------|
| Test mode | `layout` is writable, `readonly` suppresses families that need writes, and `phys` enables physical storage-buffer references. `unsized_array_length` uses a separate small runtime-array shader. |
| Block layout | `std140`, `std430`, and `scalar` select different member, array, and matrix packing rules. Random cases can also request relaxed layout. |
| Types and shapes | Fixed cases and random cases use scalar, vector, matrix, fixed-array, runtime-array, struct, nested-struct, and block-instance-array forms. The type list includes 8-bit and 16-bit forms when support permits. |
| Matrix access | Row-major and column-major variants combine with full-matrix or component loads and full-matrix or column stores. |
| Buffer placement | `per_block_buffer` allocates a buffer for each block. `single_buffer` packs blocks into one buffer with `minStorageBufferOffsetAlignment` alignment. |
| Random generation | Seeded cases select feature bits for vectors, matrices, arrays, structs, unused fields, layout qualifiers, descriptor indexing, and 64-bit indexing. The seed makes each generated case reproducible. |
| Runtime-array descriptor range | `unsized_array_length` varies element size, buffer size, descriptor offset, explicit range or `VK_WHOLE_SIZE`, variable pointers, and, outside Vulkan SC, 64-bit indexing and `length64()`. |

## Behavior Parameters

The primary behavioral axis is the registered layout test mode. Each value changes the access mechanism or the rule that supplies the expected result.

### `layout`

`layout` creates writable storage-buffer cases. The generated shader first compares fields that the case marks readable, increments a pass counter if those comparisons succeed, then writes deterministic expected values to fields that the case marks writable. The host compares the final buffer bytes with the reference write data.

### `readonly`

`readonly` constructs the same `SSBOLayoutTests` class with `m_readonly=true`. Registration blocks guarded by `if (!m_readonly)` disappear, leaving cases that can establish the layout and read values without requiring shader writes. The shared harness still checks the shader counter and reference data for the registered cases.

### `phys`

`phys` constructs the generated suite with `m_usePhysStorageBuffer=true`. The harness creates storage buffers with shader-device-address usage, obtains each bound buffer address, and supplies the addresses through push constants. Generated declarations then use physical storage-buffer references where an instance name is present.

### `unsized_array_length`

`unsized_array_length` dispatches a dedicated shader that writes `xs.length()` or `xs.length64()` to an output buffer. The expected count is the descriptor-visible byte length divided by the element size. Its `nested_unsized_arrays` test case leaf comes from a separate implementation file.

## Shader Analysis

The generated layout shader varies with the complete interface and its access flags, so this page uses the smaller runtime-array shader as the representative walkthrough. It exposes the rule that `unsized_array_length` checks without replacing the generated-layout matrix with a hand-written approximation.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.ssbo.unsized_array_length.float_offset_whole_size
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `float_offset_whole_size` | The input storage buffer has a descriptor offset and uses `VK_WHOLE_SIZE`; the shader must derive the array length from the remaining descriptor-visible range. |
| `int xs[]` | The source generator uses a four-byte element and calls `length()` rather than `length64()`. |
| SPIR-V 1.0 | This case does not request variable pointers, so [`createUnsizedArrayLengthProgs()`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L1014-L1042) selects SPIR-V 1.0. |

#### Purpose

This compute shader reports the runtime length of a readonly `std430` storage-buffer array. The host checks that the result reflects the binding offset and `VK_WHOLE_SIZE` range.

#### Structural Design

| Phase | Shader action | Observable result |
|-------|---------------|-------------------|
| Input | Reads the runtime-array metadata for binding 0 | `xs.length()` yields the descriptor-visible element count |
| Output | Writes that count through binding 1 | The host reads `observed_size` after the dispatch |

#### Shader Code

```glsl
#version 450 core
#extension GL_EXT_shader_explicit_arithmetic_types_int64 : enable
#extension GL_EXT_shader_64bit_indexing : enable

/// Binding 0 is the readonly std430 input storage buffer. Its runtime-array
/// length reflects the descriptor range visible to this binding.
layout(set=0, binding=0, std430) readonly buffer x {
    int xs[];
};

/// Binding 1 holds the observed runtime-array length for host readback.
layout(set=0, binding=1, std430) writeonly buffer y {
    int observed_size;
};

layout(local_size_x=1) in;

void main (void) {
    observed_size = xs.length();
}
```

#### Additional Info

- The source emits the two extension directives for this generated shader even when this representative path uses `length()`.
- The host initializes the output buffer to a sentinel before dispatch, so a missing or failed shader write cannot accidentally match a normal expected count.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| 64-bit length | `length64` cases change the output type to `int64_t` and call `xs.length64()`. | [`createUnsizedArrayLengthProgs()`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L1014-L1042) |
| Variable pointers | Variable-pointer cases emit `#pragma use_variable_pointers` and select SPIR-V 1.3. | [`createUnsizedArrayLengthProgs()`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L1014-L1042) |
| Generated layout suite | Other modes generate block declarations, comparison helpers, pass-counter increment, and writes from the interface tree rather than using this fixed shader. | [`generateComputeShader()`](../../../modules/vulkan/ssbo/vktSSBOLayoutCase.cpp#L1529-L1645) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `comp`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 23
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main"
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpSourceExtension "GL_EXT_shader_64bit_indexing"
               OpSourceExtension "GL_EXT_shader_explicit_arithmetic_types_int64"
               OpName %main "main"
               OpName %y "y"
               OpMemberName %y 0 "observed_size"
               OpName %_ ""
               OpName %x "x"
               OpMemberName %x 0 "xs"
               OpName %__0 ""
               OpDecorate %y BufferBlock
               OpMemberDecorate %y 0 NonReadable
               OpMemberDecorate %y 0 Offset 0
               OpDecorate %_ NonReadable
               OpDecorate %_ Binding 1
               OpDecorate %_ DescriptorSet 0
               OpDecorate %_runtimearr_int ArrayStride 4
               OpDecorate %x BufferBlock
               OpMemberDecorate %x 0 NonWritable
               OpMemberDecorate %x 0 Offset 0
               OpDecorate %__0 NonWritable
               OpDecorate %__0 Binding 0
               OpDecorate %__0 DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
          %y = OpTypeStruct %int
%_ptr_Uniform_y = OpTypePointer Uniform %y
          %_ = OpVariable %_ptr_Uniform_y Uniform
      %int_0 = OpConstant %int 0
%_runtimearr_int = OpTypeRuntimeArray %int
          %x = OpTypeStruct %_runtimearr_int
%_ptr_Uniform_x = OpTypePointer Uniform %x
        %__0 = OpVariable %_ptr_Uniform_x Uniform
       %uint = OpTypeInt 32 0
%_ptr_Uniform_int = OpTypePointer Uniform %int
     %v3uint = OpTypeVector %uint 3
     %uint_1 = OpConstant %uint 1
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
         %16 = OpArrayLength %uint %__0 0
         %17 = OpBitcast %int %16
         %19 = OpAccessChain %_ptr_Uniform_int %_ %int_0
               OpStore %19 %17
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- [`SSBOLayoutCase::delayedInit()`](../../../modules/vulkan/ssbo/vktSSBOLayoutCase.cpp#L2756-L2777) computes the reference layout, allocates initial and expected-write reference storage, fills deterministic values, preserves fields the shader will not write, and generates the compute shader.
- The layout harness creates a host-visible pass-counter buffer at binding 0. It adds a storage-buffer descriptor for every generated block; block arrays become descriptor-array bindings.
- In `per_block_buffer` mode, each block gets its own storage buffer. In `single_buffer` mode, the harness packs blocks into one buffer and rounds each binding offset to `minStorageBufferOffsetAlignment` ([`iterate()`](../../../modules/vulkan/ssbo/vktSSBOLayoutCase.cpp#L2291-L2460)).
- The `phys` path adds `VK_BUFFER_USAGE_SHADER_DEVICE_ADDRESS_BIT`, queries `VkDeviceAddress` values for the descriptors, and pushes those addresses before the dispatch ([`iterate()`](../../../modules/vulkan/ssbo/vktSSBOLayoutCase.cpp#L2463-L2508)).
- The harness dispatches one compute workgroup, records shader-write to host-read buffer barriers, waits for the universal queue, invalidates mapped allocations, and checks the pass counter and byte-for-byte data comparison ([`iterate()`](../../../modules/vulkan/ssbo/vktSSBOLayoutCase.cpp#L2552-L2648)).
- `unsized_array_length` builds its own two-binding descriptor set, dispatches once, and compares the output against `(boundLength / elementSize)` after accounting for the descriptor offset ([`ssboUnsizedArrayLengthTest()`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L1044-L1258)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `layout` | Incorrect block offsets, array or matrix strides, access lowering, shader-generated comparison/write logic, descriptor binding, synchronization, or host reference-data handling |
| `readonly` | Incorrect read-only declaration or access handling, layout computation, descriptor setup, shader comparison, or result checking |
| `phys` | Incorrect buffer-device-address support, address transport through push constants, physical storage-buffer reference lowering, or the shared layout/readback path |
| `unsized_array_length` | Incorrect descriptor offset/range interpretation, `VK_WHOLE_SIZE` handling, runtime-array length calculation, 32-bit or 64-bit indexing, or host expected-value computation |

### Cause Analysis

#### Layout, access, descriptor, or readback mismatch

**Possible failure symptoms:** The generated shader pass counter is not one, the device-written storage-buffer data differs from the reference write data, or both checks fail. The CTS reports which check failed.

**Possible implementation causes:** A wrong member offset, array stride, matrix stride, descriptor offset, generated access, or shader store can make the shader read a value that differs from the reference model or write to the wrong bytes. A missing shader-write to host-read dependency or stale mapped-memory view can also make correct device writes appear incorrect to the host. The test's barrier and invalidation steps isolate that host observation path.

#### Read-only access handling

**Possible failure symptoms:** A registered `readonly` case reports a counter or data mismatch even though it does not require one of the write-dependent layout families.

**Possible implementation causes:** The implementation may mishandle the generated readonly declaration or its loads, calculate the same layout differently for a readonly block, or bind or expose the buffer range incorrectly. The source does not attribute this failure to a particular compiler or driver component; source-level investigation is needed to distinguish those paths.

#### Physical storage-buffer address transport

**Possible failure symptoms:** `phys` cases fail their counter or data comparison while comparable ordinary `layout` cases pass.

**Possible implementation causes:** The physical path changes buffer usage, memory allocation requirements, buffer-address query, push-constant contents, and generated declaration form. A mismatch in any of those address-handling steps can make the shader dereference the wrong storage location. `checkSupport()` excludes devices without buffer-device-address support, so a normal executed failure points to the enabled path rather than absence of the feature.

#### Runtime-array descriptor-range calculation

**Possible failure symptoms:** The readback value differs from the host's computed element count. The log records buffer size, descriptor offset, descriptor range, element size, expected count, and actual count.

**Possible implementation causes:** The shader or implementation may calculate `OpArrayLength` from the wrong effective range, mishandle a nonzero descriptor offset or `VK_WHOLE_SIZE`, or use the wrong width for a 64-bit length case. The host formula follows the descriptor setup in the same test, so a mismatch also warrants checking the CTS expected-range calculation before assigning a cause to the implementation.

## Case Pruning

### Requirement-based pruning

- [`SSBOLayoutCase::checkSupport()`](../../../modules/vulkan/ssbo/vktSSBOLayoutCase.cpp#L2718-L2754) skips generated cases that require unsupported relaxed block layout, 16-bit or 8-bit storage, scalar block layout, buffer device address, descriptor indexing, runtime descriptor arrays, 64-bit indexing, or more storage-buffer descriptors than the device limit permits.
- `unsized_array_length` checks `variablePointersStorageBuffer` for variable-pointer cases and, outside Vulkan SC, `shader64BitIndexing` for 64-bit cases ([`checkSupportUnsizedArrays()`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L2190-L2200)). Deliberate allocations at least 4 GiB may report unsupported on out-of-memory.

### Design-based pruning

- `readonly` omits the `if (!m_readonly)` families because those layouts need shader writes and would not test read-only access.
- Random cases bound array depth, struct depth, block count, instance count, and member count to create reproducible coverage without an unbounded matrix.
- `nested_unsized_arrays` and `corner_case` remain separate delegated implementations because their behavior is more specific than the common generated layout suite.

## Key Takeaways

- The suite checks a generated shader against a separately computed reference layout and expected data, so it can expose both incorrect byte placement and incorrect shader access behavior.
- The pass counter checks shader-side reads before writes, while the host comparison checks the final layout-sensitive writes. Both conditions must pass.
- `readonly` and `phys` reuse the generated layout matrix but change access semantics and resource transport. `unsized_array_length` isolates the descriptor-range rule behind GLSL runtime-array length.
- The direct `ssbo` registration tree includes delegated `corner_case`; this page documents the file's hybrid dispatcher and common layout implementation without absorbing the delegated test family's details.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Category dispatcher | [`createTests()`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L2235-L2255) | Registers the five direct `ssbo` children and mode wrappers |
| Generated family registration | [`SSBOLayoutTests::init()`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L1297-L2188) | Defines fixed and seeded layout case dimensions |
| Runtime-array program and support | [`createUnsizedArrayLengthProgs()` and `checkSupportUnsizedArrays()`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L1014-L1042) | Generates the dedicated shader and selects its SPIR-V target |
| Runtime-array execution | [`ssboUnsizedArrayLengthTest()`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L1044-L1258) | Defines descriptor setup, expected length, and pass condition |
| Reference layout and generated shader | [`SSBOLayoutCase::delayedInit()`](../../../modules/vulkan/ssbo/vktSSBOLayoutCase.cpp#L2756-L2777) | Builds reference data and compute source |
| Layout shader generator | [`generateComputeShader()`](../../../modules/vulkan/ssbo/vktSSBOLayoutCase.cpp#L1529-L1645) | Emits declarations, comparison, counter increment, and writes |
| Layout execution and result checks | [`SSBOLayoutCaseInstance::iterate()`](../../../modules/vulkan/ssbo/vktSSBOLayoutCase.cpp#L2291-L2648) | Binds resources, dispatches, synchronizes, and compares results |
| Feature and limit gates | [`SSBOLayoutCase::checkSupport()`](../../../modules/vulkan/ssbo/vktSSBOLayoutCase.cpp#L2718-L2754) | Defines requirement-based pruning |
| Default Vulkan mustpass evidence | [`vk-default/ssbo.txt`](../../../mustpass/main/vk-default/ssbo.txt#L1) | Confirms registered `dEQP-VK.ssbo` prefixes |
| Vulkan SC mustpass evidence | [`vksc-default/ssbo.txt`](../../../mustpass/main/vksc-default/ssbo.txt#L1) | Confirms the Vulkan SC `ssbo` leaf set where present |
