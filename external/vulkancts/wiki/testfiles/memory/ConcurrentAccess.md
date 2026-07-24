## Overview

**Core question:** Can a host thread read untouched storage-buffer elements while a compute shader accesses neighboring elements, then observe all completed shader writes correctly?

- This page covers the `memory.concurrent_access` test family implemented in `vktMemoryConcurrentAccessTests.cpp`.
- Its single test case, `shader_and_host`, divides one host-visible coherent buffer by element parity: the shader accesses even elements while a second host thread reads odd elements.
- Final validation checks both the shader-written even elements and the untouched odd elements after a compute-to-host memory barrier and queue completion.

## Background Knowledge

For the shared concept memory dependencies and host-visible memory, see [Background Knowledge](../../categories/memory.md#background-knowledge) of the `memory` page.

- **Disjoint concurrent access:** Concurrent accesses do not conflict when they target different memory locations. Here, element parity separates device-accessed locations from host-read locations; neighboring elements must remain independent.

## Registration Hierarchy

```text
memory.concurrent_access
└── shader_and_host
```

The source registers the test family under `memory`, and the default mustpass list contains the exact leaf `dEQP-VK.memory.concurrent_access.shader_and_host`.

## Parameter Dimensions and Observed Values

| Dimension | Registered or observed values | Meaning in this test | Evidence |
|-----------|-------------------------------|----------------------|----------|
| Test case leaf | `shader_and_host` | Selects the concurrent host/device mechanism. | [`createConcurrentAccessTests()`](../../../modules/vulkan/memory/vktMemoryConcurrentAccessTests.cpp#L289-L295) |
| Storage element width | 8, 16, or 32 bits | Runtime chooses the smallest supported storage-buffer integer type, setting the access granularity. | [width selection](../../../modules/vulkan/memory/vktMemoryConcurrentAccessTests.cpp#L126-L132) |
| Buffer size | 501 bytes | Produces 501, 250, or 125 complete typed elements; trailing bytes outside a complete element are not checked. | [buffer and item counts](../../../modules/vulkan/memory/vktMemoryConcurrentAccessTests.cpp#L116-L123) |
| Initial byte pattern | `0x5b` | Repeats across the selected integer width and marks untouched data. | [initialization](../../../modules/vulkan/memory/vktMemoryConcurrentAccessTests.cpp#L112-L136) |
| Shader byte pattern | `0xca` | Repeats across the selected width and marks successful shader replacement. | [shader variants](../../../modules/vulkan/memory/vktMemoryConcurrentAccessTests.cpp#L250-L284) |
| Element parity | even, odd | Even elements belong to the shader path; odd elements belong to the concurrent host-read path. | [host checks](../../../modules/vulkan/memory/vktMemoryConcurrentAccessTests.cpp#L75-L101) |

## Behavior Parameters

The primary behavioral axis is the test case leaf. Integer width changes capability coverage and granularity, but it does not select a separate registered behavior.

### `shader_and_host`: disjoint concurrent access and final visibility

The compute shader reads and conditionally writes every even typed element. During that work, a second host thread checks every odd typed element through the coherent mapping. Once queue execution completes, the thread scans the full typed range: even indices must contain the shader pattern, and odd indices must retain the initial pattern.

## Shader Analysis

The 32-bit variant gives the clearest representative path because it exercises the same parity and replacement logic without an optional 8-bit or 16-bit storage extension.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.memory.concurrent_access.shader_and_host
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `smallestIntBytes = 4` | Represents a device where neither optional narrower storage-buffer access feature is selected. |
| `comp_4` | Uses 32-bit `uint` elements and the repeated `0x5b5b5b5b` / `0xcacacaca` constants. |
| set 0, binding 0 | Exposes the full host-visible coherent buffer as one `std430` storage buffer. |

#### Purpose

The shader accesses only even elements, leaving odd elements available for concurrent host reads. It replaces an even element only when the initial value matches, so final host validation can distinguish successful shader access from unchanged or corrupted data.

#### Structural Design

| Phase | Shader action | Host-visible consequence |
|-------|---------------|--------------------------|
| Address | Compute `2 * gl_WorkGroupID.x` | Select one even typed element. |
| Check | Compare the element with `1532713819u` | Avoid replacing data that no longer has the initial pattern. |
| Replace | Store `3402287818u` on a match | Mark successful shader processing with the repeated `0xca` pattern. |
| Preserve | Never address odd elements | Let the host check neighboring elements during execution. |

#### Shader Code

```glsl
#version 460
layout(local_size_x = 1) in;
/// Binding 0 is the host-visible coherent storage buffer. Each workgroup touches one even uint index.
layout(binding = 0, std430) buffer InOutBuf { uint v[]; } inOutBuf;
void main()
{
  /// Leave every odd index for concurrent host reads; replace a matching initial pattern at each even index.
  uint index = gl_WorkGroupID.x * 2;
  if (int(inOutBuf.v[index]) == 1532713819u)
    inOutBuf.v[index] = 3402287818u;
}
```

#### Additional Info

- `initPrograms()` adds plain `glu::ComputeSource` objects without explicit `vk::ShaderBuildOptions`, so this walkthrough uses the baseline SPIR-V 1.0 target.
- The dispatch count reaches every valid even index for the 125-element 32-bit view; no invocation addresses the incomplete trailing byte.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| 8-bit width | Adds `GL_EXT_shader_8bit_storage`, declares `uint8_t v[]`, and uses `91` / `202`. | [`comp_1`](../../../modules/vulkan/memory/vktMemoryConcurrentAccessTests.cpp#L253-L263) |
| 16-bit width | Adds `GL_EXT_shader_16bit_storage`, declares `uint16_t v[]`, and uses `23387` / `51914`. | [`comp_2`](../../../modules/vulkan/memory/vktMemoryConcurrentAccessTests.cpp#L264-L274) |
| 32-bit width | Requires no storage-width extension and uses `uint v[]` with `1532713819u` / `3402287818u`. | [`comp_4`](../../../modules/vulkan/memory/vktMemoryConcurrentAccessTests.cpp#L275-L284) |

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
; Bound: 40
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_WorkGroupID
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 460
               OpName %main "main"
               OpName %index "index"
               OpName %gl_WorkGroupID "gl_WorkGroupID"
               OpName %InOutBuf "InOutBuf"
               OpMemberName %InOutBuf 0 "v"
               OpName %inOutBuf "inOutBuf"
               OpDecorate %gl_WorkGroupID BuiltIn WorkgroupId
               OpDecorate %_runtimearr_uint ArrayStride 4
               OpDecorate %InOutBuf BufferBlock
               OpMemberDecorate %InOutBuf 0 Offset 0
               OpDecorate %inOutBuf Binding 0
               OpDecorate %inOutBuf DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_WorkGroupID = OpVariable %_ptr_Input_v3uint Input
     %uint_0 = OpConstant %uint 0
%_ptr_Input_uint = OpTypePointer Input %uint
     %uint_2 = OpConstant %uint 2
%_runtimearr_uint = OpTypeRuntimeArray %uint
   %InOutBuf = OpTypeStruct %_runtimearr_uint
%_ptr_Uniform_InOutBuf = OpTypePointer Uniform %InOutBuf
   %inOutBuf = OpVariable %_ptr_Uniform_InOutBuf Uniform
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_Uniform_uint = OpTypePointer Uniform %uint
%uint_1532713819 = OpConstant %uint 1532713819
       %bool = OpTypeBool
%uint_3402287818 = OpConstant %uint 3402287818
     %uint_1 = OpConstant %uint 1
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
      %index = OpVariable %_ptr_Function_uint Function
         %14 = OpAccessChain %_ptr_Input_uint %gl_WorkGroupID %uint_0
         %15 = OpLoad %uint %14
         %17 = OpIMul %uint %15 %uint_2
               OpStore %index %17
         %24 = OpLoad %uint %index
         %26 = OpAccessChain %_ptr_Uniform_uint %inOutBuf %int_0 %24
         %27 = OpLoad %uint %26
         %28 = OpBitcast %int %27
         %29 = OpBitcast %uint %28
         %32 = OpIEqual %bool %29 %uint_1532713819
               OpSelectionMerge %34 None
               OpBranchConditional %32 %33 %34
         %33 = OpLabel
         %35 = OpLoad %uint %index
         %37 = OpAccessChain %_ptr_Uniform_uint %inOutBuf %int_0 %35
               OpStore %37 %uint_3402287818
               OpBranch %34
         %34 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The host allocates a 501-byte storage buffer from host-visible coherent memory, maps it through the allocation, and fills every byte with `0x5b`.
- Feature queries select 8-bit storage when available, then 16-bit storage, otherwise 32-bit storage. The host creates the matching shader module and views only complete typed elements.
- One descriptor exposes the full buffer at binding 0. The command buffer dispatches one workgroup per even typed element, then records a memory barrier from compute-shader read/write access to host read access.
- The main thread locks a mutex before starting the checking thread. The checker first reads odd elements without taking that mutex, so those reads can overlap queue execution.
- `submitCommandsAndWait()` waits for the dispatch and barrier. The main thread then unlocks the mutex, allowing the checker to begin its full-buffer scan.
- Concurrent odd-element mismatches produce `WRONG_INITIAL_VALUE_DURING_COMPUTE_SHADER`. The final scan classifies an even-element mismatch as `WRONG_SHADER_VALUE_AFTER_COMPUTE_SHADER` and an odd-element mismatch as `WRONG_INITIAL_VALUE_AFTER_COMPUTE_SHADER`.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `shader_and_host` | Disjoint-access corruption during the dispatch, incorrect compute storage-buffer access, or failed device-to-host visibility after the barrier. |

### Cause Analysis

#### Disjoint-access corruption during the dispatch

**Possible failure symptoms:** An odd element differs from the repeated initial pattern while the compute submission may still be executing, producing `WRONG_INITIAL_VALUE_DURING_COMPUTE_SHADER`.

**Possible implementation causes:** The device access or its storage-buffer implementation affected bytes outside the addressed even element. The test does not identify whether that fault came from compiler lowering, generated memory transactions, or another implementation layer; source-level investigation is needed to localize it.

#### Incorrect compute storage-buffer access

**Possible failure symptoms:** After completion, an even element does not contain the repeated shader pattern and produces `WRONG_SHADER_VALUE_AFTER_COMPUTE_SHADER`.

**Possible implementation causes:** The compute shader may have failed to read, compare, or store the selected 8-, 16-, or 32-bit element correctly. For narrower variants, this includes incorrect support for the enabled storage-buffer width. The same symptom can result from later visibility failure, so the CTS result alone does not isolate the stage.

#### Failed device-to-host visibility after the barrier

**Possible failure symptoms:** Final validation sees a stale or otherwise incorrect value after queue completion. Even elements may retain the initial pattern, or final odd-element validation may observe a value inconsistent with the concurrent check.

**Possible implementation causes:** The compute-to-host memory dependency may have failed to make shader writes available to the host domain, or coherent-memory handling may have failed to make available writes visible to host reads. The Vulkan synchronization specification defines a memory dependency as enforcing availability and visibility and defines coherent host visibility without explicit invalidation.

## Case Pruning

### Requirement-based pruning

No registered test case is skipped. Runtime chooses 8-bit elements only when `uniformAndStorageBuffer8BitAccess` is supported, 16-bit elements only when `uniformAndStorageBuffer16BitAccess` is supported, and otherwise uses the core 32-bit path.

The allocator must find memory satisfying `HostVisible | Coherent`; allocation failure follows ordinary CTS resource/setup handling rather than pruning a separate leaf.

### Design-based pruning

- The source registers one test case rather than separate leaves for integer width because width is selected from device capabilities.
- Integer division excludes incomplete trailing bytes from typed access. The 501-byte allocation therefore contributes 501, 250, or 125 complete elements.
- The shader and host use opposite parity, so the concurrent phase excludes conflicting accesses to the same element by design.

## Key Takeaways

- `shader_and_host` checks two contracts: neighboring disjoint elements remain intact during concurrent host/device access, and completed shader writes become host-visible.
- The smallest supported storage width increases granularity coverage without changing the registered test path or parity-based mechanism.
- Three result classes distinguish a concurrent odd-element mismatch from final even- and odd-element mismatches, while `Failure Meaning` explains why one symptom may still have more than one implementation cause.

## Source Reference Appendix

- [`vktMemoryConcurrentAccessTests.cpp`](../../../modules/vulkan/memory/vktMemoryConcurrentAccessTests.cpp)
  - [`secondThreadFunction()`](../../../modules/vulkan/memory/vktMemoryConcurrentAccessTests.cpp#L63-L104): concurrent odd-element checks and final parity-based scan.
  - [`testShaderAndHostAccess()`](../../../modules/vulkan/memory/vktMemoryConcurrentAccessTests.cpp#L106-L247): resource setup, submission, synchronization, and result reporting.
  - [`initPrograms()`](../../../modules/vulkan/memory/vktMemoryConcurrentAccessTests.cpp#L250-L285): 8-, 16-, and 32-bit compute shaders.
  - [`createConcurrentAccessTests()`](../../../modules/vulkan/memory/vktMemoryConcurrentAccessTests.cpp#L289-L295): test family and leaf registration.
- [`vktMemoryTests.cpp`](../../../modules/vulkan/memory/vktMemoryTests.cpp#L44-L74): registration under the `memory` test category, including Vulkan SC.
- [`memory.txt`](../../../mustpass/main/vk-default/memory.txt#L580): default mustpass evidence for the exact test case.
- Vulkan specification:
  - [memory dependency availability and visibility](../../../../vulkan-docs/src/chapters/synchronization.adoc#L159-L160)
  - [host read access](../../../../vulkan-docs/src/chapters/synchronization.adoc#L1593-L1597)
  - [host-coherent memory behavior](../../../../vulkan-docs/src/chapters/synchronization.adoc#L1733-L1749)
