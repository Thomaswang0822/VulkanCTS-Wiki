## Overview

**Core question:** Do sparse `VkBuffer` mappings produce the expected data when the buffer is transferred, bound to a pipeline, used for indirect work, partially resident, aliased, rebound, or accessed by address?

- This page covers the implementation and registrations rooted at `sparse_resources.buffer` in [`vktSparseResourcesBufferTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L24-L32).
- The test category contains direct buffer-use families plus delegated transfer, residency, aliasing, and rebind implementations.
- Cases validate results in host-visible memory, shader output, or both. Passing `vkQueueBindSparse` alone is not sufficient.
- The page explains the registration tree, the behavior variants, the host/device timeline, and what each failure can indicate.

## Background Knowledge

- Sparse binding lets a `VkBuffer` map non-contiguous ranges of one or more `VkDeviceMemory` allocations. A sparse buffer has a defined buffer-range to memory-range mapping for each contiguous bound range. See [`sparsemem.adoc`](../../../../vulkan-docs/src/chapters/sparsemem.adoc#L7-L20).
- Sparse residency builds on sparse binding and permits unbound ranges. With `residencyNonResidentStrict`, reads from an unbound range behave as zero and writes are discarded. Without that property, reads from such a range are undefined, so the test skips those reads rather than comparing them with a fixed value. See [`sparsemem.adoc`](../../../../vulkan-docs/src/chapters/sparsemem.adoc#L101-L119).
- Sparse aliasing lets multiple bindings observe the same physical memory. Rebinding changes the memory mapped to a range while the resource remains alive. These tests therefore inspect data after the bind operation, not only the API return value.

## Registration Hierarchy

```text
sparse_resources.buffer
├── transfer
├── ssbo
├── ubo
├── texel_buffers
├── vertex_buffer
├── index_buffer
├── indirect_buffer
├── transform_feedback
├── indirect_dispatch
├── misc (non-VulkanSC only)
└── memory_copy_indirect
```

The direct children are registered by [`populateTestGroup()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L2598-L2808). The `transfer` family delegates `sparse_binding`, `device_group_sparse_binding`, and `rebind` cases to helper files. `ssbo` delegates memory-aliasing and residency cases, while the other direct families use the common buffer-object implementation or their local implementation in the same source file.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Direct test family | `transfer`, `ssbo`, `ubo`, `texel_buffers`, `vertex_buffer`, `index_buffer`, `indirect_buffer`, `transform_feedback`, `indirect_dispatch`, optional `misc`, `memory_copy_indirect` | Selects the buffer operation and its validation path | [`populateTestGroup()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L2598-L2808) |
| Common sparse flags | `sparse_binding`, `sparse_binding_aliased`, `sparse_residency`, `sparse_residency_aliased`, `sparse_residency_non_resident_strict` | Selects full binding, aliasing, holes, or strict treatment of holes | [`groups[]`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L2565-L2597) |
| Device-group mode | `device_group_` variants where registered | Separates resource-device and memory-device indices during sparse binding | [`populateTestGroup()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L2607-L2610) |
| Helper buffer size | `2^10`, `2^12`, `2^16`, `2^17`, `2^20`, `2^24` in the binding, aliasing, and residency helpers; `2^16`, `2^18`, `2^20`, `2^24` for rebind | Changes the number and layout of sparse blocks exercised | [`vktSparseResourcesBufferSparseBinding.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferSparseBinding.cpp#L348-L356), [`vktSparseResourcesBufferRebind.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferRebind.cpp#L412-L418) |
| Nonresident operation | copy, fill, update | Checks how commands interact with holes | [`BufferInitCommand`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferSparseResidency.cpp#L65-L83) |
| Texel-buffer matrix | uniform or storage; sparse fetch, sparse read, or ordinary read; `2^10`, `2^16`, `2^24`; `VK_FORMAT_R32_UINT` or `VK_FORMAT_R64_UINT`; strict or non-strict | Varies the resource type, operation, format, and residency rule | [`addTexelBufferSparseResidencyTests()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferSparseResidency.cpp#L1838-L1884) |

## Behavior Parameters

The primary behavioral axis is the direct test family. Each family changes the operation performed on sparse memory rather than merely changing setup.

### `transfer` | bind, copy, and rebind

The sparse-binding cases register six sizes from `buffer_size_2_10` through `buffer_size_2_24`. They bind the sparse ranges, copy reference bytes into the buffer, copy them back, and compare the result. Rebind cases perform full binds, fills, a partial rebind, and a final copy-out. Device-group cases also select resource and memory devices.

### `ssbo` | storage-buffer reads and writes

The family covers sparse memory aliasing, sparse residency, nonresident copy/fill/update commands, and `read_write`. Aliasing binds two buffers to shared memory and verifies that a compute write through one is visible through the other. The direct `read_write` path enables residency and strict nonresident flags for a storage buffer.

### `ubo` | uniform-buffer descriptor access

The common buffer-object path creates a sparse UBO with the selected flags, initializes its data, and has a fragment shader check the values through a descriptor. Aliased and residency variants alter the sparse allocation layout; device-group variants repeat the supported flag set with device-group binding.

### `texel_buffers` | sparse texel operations

The helper varies uniform and storage texel buffers, sparse fetch and sparse read operations, ordinary reads, two unsigned formats, buffer sizes, and strict residency. Invalid combinations, such as uniform sparse read or storage sparse fetch, are skipped by the generator.

### `vertex_buffer` | vertex input

The test fills sparse ranges with grid vertices, binds the sparse buffer as a vertex buffer twice, and draws two half-view grids. The four default flag variants are repeated for device groups; the strict-only entry is excluded from this family.

### `index_buffer` | indexed input

A regular vertex buffer supplies positions while sparse index ranges supply indexed primitives from two offsets. The result uses the same image check as the other graphics paths.

### `indirect_buffer` | indirect draw commands

The test writes `VkDrawIndirectCommand` records into sparse ranges and executes two `cmdDrawIndirect` calls from different offsets. A rendered-image mismatch identifies an incorrect command fetch or subsequent draw result.

### `transform_feedback` | sparse transform-feedback output

One residency case binds a sparse transform-feedback buffer, emits vertex indices, copies the buffer back, and compares selected entries with their indices. The family requires `VK_EXT_transform_feedback`.

### `indirect_dispatch` | indirect compute dispatch

The test leaves a hole at the start of a sparse indirect buffer, places a `VkDispatchIndirectCommand` at `sparseChunkSize + 4`, and calls `cmdDispatchIndirect`. It checks that the output buffer contains `135 + i` for each expected index.

### `misc` | null-address behavior

On non-VulkanSC builds, generated cases vary local-invocation-index use, descriptor versus buffer-device-address access, map-first behavior, and read versus write mode. The test compares mapped and unmapped behavior with the expected zero or nonzero vectors.

### `memory_copy_indirect` | indirect copy to sparse memory

The four non-strict variants use `VK_KHR_copy_memory_indirect` and `VK_KHR_buffer_device_address`. The test builds copy commands containing source and sparse-destination addresses, calls `cmdCopyMemoryIndirectKHR`, then draws from the sparse vertex buffer and checks the image.

## Shader Analysis

The buffer page has two materially different shader-backed validation paths, so this section uses two representative walkthroughs: the graphics fragment shader for the strict sparse SSBO read/write case, and the compute shader for the indirect-dispatch case. The first validates sparse buffer values and discarded writes through a descriptor; the second does not inspect sparse data in shader code, but its dispatch dimensions come from a sparse indirect buffer and its storage writes provide the final compute oracle.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.sparse_resources.buffer.ssbo.read_write.sparse_residency_non_resident_strict
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `ssbo.read_write` | Selects the common graphics buffer-object path with a storage-buffer descriptor; the fragment shader both reads and writes `buff.data`. |
| `sparse_residency_non_resident_strict` | Leaves a resource chunk unbound and requires strict nonresident semantics: reads from the hole and writes to it must both behave as zero/discarded. |
| `layout(constant_id = 1/2)` | `dataSize` and `chunkSize` are specialization constants filled from the sparse allocation at draw time; the source-level defaults are used when compiling the reconstructed shader. |

#### Purpose

Each fragment checks the `ivec4` value initialized in the sparse SSBO, writes an index-derived value, and reads it back. Bound ranges must preserve the initialization and the write/read result, while the strict nonresident range must read as zero and discard the write.

#### Structural Design

| Phase | Shader action | Validation contribution |
|-------|---------------|-------------------------|
| Indexing | Convert `gl_FragCoord` to a linear index and advance by one framebuffer page | The 128×128 fragment grid covers the buffer in strided passes. |
| Access | Load `buff.data[ndx]`, write `newData`, then load it again | Tests both sparse storage-buffer reads and writes. |
| Residency branch | Treat `[chunkSize, 2*chunkSize)` as the nonresident chunk | Strict residency expects zero before and after the write; other entries use the initialized pattern. |
| Oracle | Emit green when `ok` remains true, red otherwise | `imageHasErrorPixels()` turns a red/blank rendered result into failure. |

#### Shader Code

```glsl
#version 450

layout(location = 0) out vec4 o_color;

layout(constant_id = 1) const int dataSize  = 1;
layout(constant_id = 2) const int chunkSize = 1;

/// Binding 0 is the host-created sparse storage buffer. Its std430 ivec4 array is sized by the
/// dataSize specialization constant; volatile access is emitted for the storage-buffer read/write case.
layout(set = 0, binding = 0, std430) buffer SparseBuffer {
    volatile ivec4 data[dataSize];
} buff;

void main(void)
{
    /// The 128x128 render target assigns each fragment a linear starting element. The loop stride
    /// is one complete framebuffer page so every invocation can cover later buffer pages too.
    const int fragNdx        = int(gl_FragCoord.x) + 128 * int(gl_FragCoord.y);
    const int pageSize       = 128 * 128;
    const int numChunks      = dataSize / chunkSize;
    bool      ok             = true;

    for (int ndx = fragNdx; ndx < dataSize; ndx += pageSize)
    {
        ivec4 readData = buff.data[ndx];

        // Write a new value based on index
        ivec4 newData = ivec4(ndx * 2 + 1, ndx ^ 0x55, ndx, 1);
        buff.data[ndx] = newData;
        ivec4 verifyData = buff.data[ndx];

        /// The strict nonresident interval is the resource hole. A compliant implementation
        /// returns zero there and discards the write; all other entries must retain the initialized pattern.
        if (ndx >= chunkSize && ndx < 2 * chunkSize)
            ok = ok && (readData == ivec4(0)) && (verifyData == ivec4(0));
        else
            ok = ok && (readData == ivec4(3*ndx ^ 127, 0, 0, 0)) && (verifyData == newData);
    }

    /// Green is the success token consumed by the host image check; any mismatch makes the pixel red.
    if (ok)
        o_color = vec4(0.0, 1.0, 0.0, 1.0);
    else
        o_color = vec4(1.0, 0.0, 0.0, 1.0);
}
```

#### Additional Info

- The host initializes each `ivec4` entry as `ivec4(3 * i ^ 127, 0, 0, 0)` before drawing, and binds the descriptor with the allowed range capped by the uniform/storage-buffer limit ([`BufferObjectTestInstance::iterate()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L951-L1021)).
- This representative path has no alias flag, so the generator checks the initialized value directly as `ivec4(3*ndx ^ 127, 0, 0, 0)`; aliased variants add a modulo by the non-aliased range ([`initProgramsDrawWithBufferObject()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L754-L834)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|----------------------------------------|----------|
| UBO versus SSBO | Changes the block to `uniform`/`std140` or `buffer`/`std430`; the SSBO path also emits `volatile` and performs the write/read-back sequence. | [`initProgramsDrawWithBufferObject()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L756-L803) |
| Aliasing | Adds `nonAliasedSize` to the expected-value expression so the aliased final chunk is checked against the shared physical data. | [`initProgramsDrawWithBufferObject()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L756-L786) |
| Residency and strictness | Non-strict residency skips the hole; strict residency checks zero before and after the write. Fully bound cases check the initialized pattern everywhere. | [`initProgramsDrawWithBufferObject()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L805-L824) |
| `dataSize`/`chunkSize` | Specialization constants control array length, chunk count, hole interval, and loop bounds. | [`BufferObjectTestInstance::iterate()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L1043-L1078) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `frag`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 124
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %gl_FragCoord %o_color
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 450
               OpName %main "main"
               OpName %fragNdx "fragNdx"
               OpName %gl_FragCoord "gl_FragCoord"
               OpName %ok "ok"
               OpName %ndx "ndx"
               OpName %dataSize "dataSize"
               OpName %readData "readData"
               OpName %SparseBuffer "SparseBuffer"
               OpMemberName %SparseBuffer 0 "data"
               OpName %buff "buff"
               OpName %newData "newData"
               OpName %verifyData "verifyData"
               OpName %chunkSize "chunkSize"
               OpName %o_color "o_color"
               OpDecorate %gl_FragCoord BuiltIn FragCoord
               OpDecorate %dataSize SpecId 1
               OpDecorate %_arr_v4int_dataSize ArrayStride 16
               OpDecorate %SparseBuffer BufferBlock
               OpMemberDecorate %SparseBuffer 0 Volatile
               OpMemberDecorate %SparseBuffer 0 Coherent
               OpMemberDecorate %SparseBuffer 0 Offset 0
               OpDecorate %buff Binding 0
               OpDecorate %buff DescriptorSet 0
               OpDecorate %chunkSize SpecId 2
               OpDecorate %o_color Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
%_ptr_Function_int = OpTypePointer Function %int
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Input_v4float = OpTypePointer Input %v4float
%gl_FragCoord = OpVariable %_ptr_Input_v4float Input
       %uint = OpTypeInt 32 0
     %uint_0 = OpConstant %uint 0
%_ptr_Input_float = OpTypePointer Input %float
    %int_128 = OpConstant %int 128
     %uint_1 = OpConstant %uint 1
       %bool = OpTypeBool
%_ptr_Function_bool = OpTypePointer Function %bool
       %true = OpConstantTrue %bool
   %dataSize = OpSpecConstant %int 1
      %v4int = OpTypeVector %int 4
%_ptr_Function_v4int = OpTypePointer Function %v4int
%_arr_v4int_dataSize = OpTypeArray %v4int %dataSize
%SparseBuffer = OpTypeStruct %_arr_v4int_dataSize
%_ptr_Uniform_SparseBuffer = OpTypePointer Uniform %SparseBuffer
       %buff = OpVariable %_ptr_Uniform_SparseBuffer Uniform
      %int_0 = OpConstant %int 0
%_ptr_Uniform_v4int = OpTypePointer Uniform %v4int
      %int_2 = OpConstant %int 2
      %int_1 = OpConstant %int 1
     %int_85 = OpConstant %int 85
  %chunkSize = OpSpecConstant %int 1
         %76 = OpSpecConstantOp %int IMul %int_2 %chunkSize
         %83 = OpConstantComposite %v4int %int_0 %int_0 %int_0 %int_0
     %v4bool = OpTypeVector %bool 4
      %int_3 = OpConstant %int 3
    %int_127 = OpConstant %int 127
  %int_16384 = OpConstant %int 16384
%_ptr_Output_v4float = OpTypePointer Output %v4float
    %o_color = OpVariable %_ptr_Output_v4float Output
    %float_0 = OpConstant %float 0
    %float_1 = OpConstant %float 1
        %121 = OpConstantComposite %v4float %float_0 %float_1 %float_0 %float_1
        %123 = OpConstantComposite %v4float %float_1 %float_0 %float_0 %float_1
       %main = OpFunction %void None %3
          %5 = OpLabel
    %fragNdx = OpVariable %_ptr_Function_int Function
         %ok = OpVariable %_ptr_Function_bool Function
        %ndx = OpVariable %_ptr_Function_int Function
   %readData = OpVariable %_ptr_Function_v4int Function
    %newData = OpVariable %_ptr_Function_v4int Function
 %verifyData = OpVariable %_ptr_Function_v4int Function
         %16 = OpAccessChain %_ptr_Input_float %gl_FragCoord %uint_0
         %17 = OpLoad %float %16
         %18 = OpConvertFToS %int %17
         %21 = OpAccessChain %_ptr_Input_float %gl_FragCoord %uint_1
         %22 = OpLoad %float %21
         %23 = OpConvertFToS %int %22
         %24 = OpIMul %int %int_128 %23
         %25 = OpIAdd %int %18 %24
               OpStore %fragNdx %25
               OpStore %ok %true
         %31 = OpLoad %int %fragNdx
               OpStore %ndx %31
               OpBranch %32
         %32 = OpLabel
               OpLoopMerge %34 %35 None
               OpBranch %36
         %36 = OpLabel
         %37 = OpLoad %int %ndx
         %39 = OpSLessThan %bool %37 %dataSize
               OpBranchConditional %39 %33 %34
         %33 = OpLabel
         %48 = OpLoad %int %ndx
         %50 = OpAccessChain %_ptr_Uniform_v4int %buff %int_0 %48
         %51 = OpLoad %v4int %50
               OpStore %readData %51
         %53 = OpLoad %int %ndx
         %55 = OpIMul %int %53 %int_2
         %57 = OpIAdd %int %55 %int_1
         %58 = OpLoad %int %ndx
         %60 = OpBitwiseXor %int %58 %int_85
         %61 = OpLoad %int %ndx
         %62 = OpCompositeConstruct %v4int %57 %60 %61 %int_1
               OpStore %newData %62
         %63 = OpLoad %int %ndx
         %64 = OpLoad %v4int %newData
         %65 = OpAccessChain %_ptr_Uniform_v4int %buff %int_0 %63
               OpStore %65 %64
         %67 = OpLoad %int %ndx
         %68 = OpAccessChain %_ptr_Uniform_v4int %buff %int_0 %67
         %69 = OpLoad %v4int %68
               OpStore %verifyData %69
         %70 = OpLoad %int %ndx
         %72 = OpSGreaterThanEqual %bool %70 %chunkSize
               OpSelectionMerge %74 None
               OpBranchConditional %72 %73 %74
         %73 = OpLabel
         %75 = OpLoad %int %ndx
         %77 = OpSLessThan %bool %75 %76
               OpBranch %74
         %74 = OpLabel
         %78 = OpPhi %bool %72 %33 %77 %73
               OpSelectionMerge %80 None
               OpBranchConditional %78 %79 %92
         %79 = OpLabel
         %81 = OpLoad %bool %ok
         %82 = OpLoad %v4int %readData
         %85 = OpIEqual %v4bool %82 %83
         %86 = OpAll %bool %85
         %87 = OpLogicalAnd %bool %81 %86
         %88 = OpLoad %v4int %verifyData
         %89 = OpIEqual %v4bool %88 %83
         %90 = OpAll %bool %89
         %91 = OpLogicalAnd %bool %87 %90
               OpStore %ok %91
               OpBranch %80
         %92 = OpLabel
         %93 = OpLoad %bool %ok
               OpSelectionMerge %95 None
               OpBranchConditional %93 %94 %95
         %94 = OpLabel
         %96 = OpLoad %v4int %readData
         %98 = OpLoad %int %ndx
         %99 = OpIMul %int %int_3 %98
        %101 = OpBitwiseXor %int %99 %int_127
        %102 = OpCompositeConstruct %v4int %101 %int_0 %int_0 %int_0
        %103 = OpIEqual %v4bool %96 %102
        %104 = OpAll %bool %103
               OpBranch %95
         %95 = OpLabel
        %105 = OpPhi %bool %93 %92 %104 %94
        %106 = OpLoad %v4int %verifyData
        %107 = OpLoad %v4int %newData
        %108 = OpIEqual %v4bool %106 %107
        %109 = OpAll %bool %108
        %110 = OpLogicalAnd %bool %105 %109
               OpStore %ok %110
               OpBranch %80
         %80 = OpLabel
               OpBranch %35
         %35 = OpLabel
        %112 = OpLoad %int %ndx
        %113 = OpIAdd %int %112 %int_16384
               OpStore %ndx %113
               OpBranch %32
         %34 = OpLabel
        %114 = OpLoad %bool %ok
               OpSelectionMerge %116 None
               OpBranchConditional %114 %115 %122
        %115 = OpLabel
               OpStore %o_color %121
               OpBranch %116
        %122 = OpLabel
               OpStore %o_color %123
               OpBranch %116
        %116 = OpLabel
               OpReturn
               OpFunctionEnd

```

</details>

## Runtime Execution and Result Checking

- The common instance requests a sparse-binding queue and a graphics/compute queue. If the families need separate queue families, it creates the buffer with concurrent sharing for those families. The base device setup reports `NotSupportedError` when the requested queues or features are unavailable ([`SparseResourcesBaseInstance`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBase.cpp#L88-L194)).
- The host queries sparse requirements, constructs memory binds, resource holes, memory holes, or aliased binds, creates the buffer, and submits `vkQueueBindSparse`. The bind helper waits on a fence before later work uses the resource ([`bindSparseBuffer`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L788-L837)).
- Staging data initializes bound ranges. Families then submit transfer, draw, compute, transform-feedback, indirect draw, indirect dispatch, or indirect-copy work.
- Graphics paths copy the color image to a host-visible buffer. `imageHasErrorPixels()` treats red or blank pixels as failure ([`imageHasErrorPixels()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L447-L462)).
- Transfer and residency helpers compare host-visible bytes. Compute and indirect-dispatch paths compare result vectors. The test case fails when the relevant comparison finds a mismatch.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `transfer` | Incorrect sparse block binding, device-group bind indices, or rebind result |
| `ssbo` | Incorrect aliasing, residency semantics, sparse read/write behavior, or copy/fill/update handling |
| `ubo` | Incorrect descriptor access to sparse uniform-buffer data or flag handling |
| `texel_buffers` | Incorrect sparse texel fetch/read, format handling, or residency-status result |
| `vertex_buffer` | Incorrect vertex-input access to sparse ranges |
| `index_buffer` | Incorrect indexed draw access to sparse ranges |
| `indirect_buffer` | Incorrect indirect command fetch from sparse memory |
| `transform_feedback` | Incorrect sparse transform-feedback writes or copyback |
| `indirect_dispatch` | Incorrect indirect dispatch command fetch or output writes |
| `misc` | Incorrect null-address, mapping, descriptor, or buffer-device-address behavior |
| `memory_copy_indirect` | Incorrect indirect copy to a sparse destination or subsequent vertex access |

### Cause Analysis

#### Sparse mapping, holes, aliases, or rebinding

**Possible failure symptoms:** Copyback differs from the reference bytes, an alias does not observe the other buffer's write, or a partially rebound range contains the wrong pattern.

**Possible implementation causes:** The implementation may apply a `VkSparseMemoryBind` at the wrong buffer offset, use the wrong memory range, mishandle a resource or memory hole, or fail to make a shared or rebound mapping visible as required. The source and the sparse-resource specification support these interpretations; a more specific driver or hardware cause needs investigation.

#### Sparse access through a buffer operation

**Possible failure symptoms:** The rendered image contains red or blank pixels, an indirect command produces the wrong draw or dispatch, transform feedback contains an unexpected index, or a compute result differs from its expected vector.

**Possible implementation causes:** The operation may fetch from the wrong sparse range, or the implementation may mishandle sparse residency while reading or writing through the selected pipeline or transfer operation. The exact cause requires investigation of the failing family and parameter values.

#### Nonresident or feature-gated behavior

**Possible failure symptoms:** A strict-residency case observes a nonzero value in an unbound range, fails to discard a write, or a supported texel, transform-feedback, device-group, or indirect-copy case cannot produce the checked result.

**Possible implementation causes:** The implementation may apply the wrong `residencyNonResidentStrict` semantics or may not correctly enable or use the feature path required by that case. An unsupported device should be rejected during capability checks rather than fail the data comparison.

## Case Pruning

### Requirement-based pruning

- Sparse binding is required for all sparse-buffer cases. Residency cases require `sparseResidencyBuffer`; aliased cases require `sparseResidencyAliased`; strict cases require `sparseProperties.residencyNonResidentStrict` ([`checkSupport()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L2016-L2032)).
- Device-group cases require at least two physical devices and suitable peer-memory features ([`SparseResourcesBaseInstance`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBase.cpp#L109-L131)).
- Transform feedback, indirect memory copy, buffer device address, and 64-bit texel cases require their corresponding extensions and features.
- `misc` is omitted under `CTS_USES_VULKANSC`. Vulkan SC does not support sparse resources ([`sparsemem.adoc`](../../../../vulkan-docs/src/chapters/sparsemem.adoc#L23-L32)).

### Design-based pruning

- The generators omit invalid texel-buffer operation and type combinations.
- The `vertex_buffer`, `index_buffer`, and `indirect_buffer` families use the four default flag variants and omit the strict-only variant because that behavior is not part of those test shapes.
- Helper files register their cases under the `buffer` root only when `populateTestGroup()` calls them; they do not create separate top-level test categories.

## Key Takeaways

- `sparse_resources.buffer` tests observable buffer behavior across transfer, descriptors, fixed-function input, indirect commands, transform feedback, and address-based access.
- Holes, aliases, rebinds, and device-group indices are tested through data comparisons or rendered output, not just successful bind calls.
- Strict residency changes the expected value for an unbound range. Non-strict cases avoid asserting a value for that range.
- A failure identifies the tested operation and mapping combination. The exact implementation cause still depends on the failing family and its parameters.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Registration and direct families | [`populateTestGroup()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L2565-L2808) | Defines the complete `sparse_resources.buffer` tree |
| Common buffer-object setup and shader | [`BufferObjectTestInstance`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L838-L1085) | Covers UBO and SSBO descriptor paths |
| Graphics result handling | [`Renderer::draw()` and `imageHasErrorPixels()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L447-L462) | Copies and checks rendered output |
| Sparse binding helper | [`vktSparseResourcesBufferSparseBinding.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferSparseBinding.cpp#L149-L356) | Tests copy-in/copy-out binding cases |
| Sparse residency and texel cases | [`vktSparseResourcesBufferSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferSparseResidency.cpp#L1120-L1884) | Tests holes, commands, and sparse texel operations |
| Sparse memory aliasing | [`vktSparseResourcesBufferMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferMemoryAliasing.cpp#L246-L439) | Tests shared memory through two sparse buffers |
| Sparse rebind | [`vktSparseResourcesBufferRebind.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferRebind.cpp#L23-L418) | Tests partial rebinding and final contents |
| Queue and device setup | [`vktSparseResourcesBase.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBase.cpp#L88-L194) | Selects sparse, graphics, compute, and device-group support |
| Mustpass evidence | [`sparse-resources.txt`](../../../mustpass/main/vk-default/sparse-resources.txt) | Records executable `dEQP-VK.sparse_resources.*` paths |
| API test plan | [`apitests.adoc`](../../../../../doc/testspecs/VK/apitests.adoc#L273-L276) | Places sparse buffers in the Vulkan test plan |
