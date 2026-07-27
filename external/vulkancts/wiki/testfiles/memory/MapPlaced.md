## Overview

**Core question:** Does `VK_EXT_map_memory_placed` place a host-visible memory map at the requested address and preserve the requested address range when `VK_MEMORY_UNMAP_RESERVE_BIT_EXT` is used?

- This page covers [`vktMemoryMapPlacedTests.cpp`](../../../modules/vulkan/memory/vktMemoryMapPlacedTests.cpp), which implements the `memory.map_placed` test family.
- The test checks exact placed-map extent, CPU/GPU access through a placed map, and address reservation after unmapping.
- The placement and reservation paths use POSIX virtual-memory facilities to inspect the process address space. The GPU path binds the mapped memory to a storage buffer and dispatches a compute shader.

## Background Knowledge

For the shared concepts host-visible and non-coherent memory, and flush and invalidate direction, see [Background Knowledge](../../categories/memory.md#background-knowledge) of the `memory` page.

- `vkMapMemory2` accepts a `VkMemoryMapInfoKHR` chain; `VK_MEMORY_MAP_PLACED_BIT_EXT` and `VkMemoryMapPlacedInfoEXT` request a specific virtual address. A successful call returns that address. [Vulkan memory mapping rules](../../../../vulkan-docs/src/chapters/memory.adoc#L4971-L5108)
- `VK_MEMORY_UNMAP_RESERVE_BIT_EXT` separates unmapping from releasing the process address range. The reservation cases use OS-visible mapping checks to observe that distinction.

## Registration Hierarchy

```text
memory.map_placed
├── exact_size
├── gpu_access
├── unmap_reserve
└── normal_unmap_reserve
```

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test family | `exact_size`, `gpu_access`, `unmap_reserve`, `normal_unmap_reserve` | Selects the primary placed-mapping or reservation property under test. | [`createMapPlacedTests`](../../../modules/vulkan/memory/vktMemoryMapPlacedTests.cpp#L926-L997) |
| Memory size | `4096`, `8192`, `65536`, `1048576` bytes for all families except `gpu_access`; `65536` bytes for `gpu_access` | Exercises one page through 1 MiB of placed or reserved address space. | [`createMapPlacedTests`](../../../modules/vulkan/memory/vktMemoryMapPlacedTests.cpp#L930-L990) |
| Alignment | `max(system page size, minPlacedMemoryMapAlignment)` | The placed address and allocation size are rounded so the map meets extension and OS page constraints. | [`MapPlacedExactSizeTestInstance::iterate`](../../../modules/vulkan/memory/vktMemoryMapPlacedTests.cpp#L147-L236) |

## Behavior Parameters

The test family is the primary behavioral axis. Each value changes the observable contract rather than only changing a size or feature setting.

### exact_size: exact placed-map range

This family checks that a placed `VkDeviceMemory` map begins exactly at `pPlacedAddress` and does not replace adjacent pages. The test creates two mappings of one memfd-backed range, fills them with `0xAB`, then uses the second mapping to verify that only the Vulkan map's requested range differs after unmapping.

### gpu_access: CPU-to-GPU-to-CPU data path

This family checks that memory mapped at a caller-selected address remains usable after it is bound to a storage buffer. The host writes increasing integers, the compute shader increments them, and the host requires every result to equal `i + 1`.

### unmap_reserve: reservation after a placed map

This family unmaps a placed mapping with `VK_MEMORY_UNMAP_RESERVE_BIT_EXT`. It verifies that the surrounding guard pages remain intact and that the placed range remains covered in `/proc/self/maps` where that inspection is available.

### normal_unmap_reserve: reservation after a normal map

This family first maps the allocation with legacy `vkMapMemory`, then uses `vkUnmapMemory2` with `VK_MEMORY_UNMAP_RESERVE_BIT_EXT`. A fresh anonymous `mmap` must not overlap the retained range, and the Linux process-map check confirms coverage.

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.memory.map_placed.gpu_access.read_write
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `gpu_access` | Selects the only family that binds placed-mapped memory to a GPU-visible resource. |
| `read_write` | Uses a 65536-byte storage buffer; the CPU initializes each `uint` and the shader increments it. |

#### Purpose

The shader provides the device-side half of the placed-map round trip. Each invocation increments one buffer element so the host can detect an incorrect mapping, visibility transition, descriptor binding, or compute result.

#### Structural Design

| Phase | Shader action |
|-------|---------------|
| Invocation selection | Read `gl_GlobalInvocationID.x` as the array index. |
| Bounds check | Compare the index with the runtime storage-buffer array length. |
| Update | Increment the selected `values[idx]` element. |

#### Shader Code

```glsl
#version 450
/// One invocation handles one 32-bit storage-buffer element.
layout(local_size_x = 64) in;

/// Set 0, binding 0 is the VkBuffer bound by the host as a storage buffer.
layout(set = 0, binding = 0) buffer Data {
    uint values[];
};

void main() {
    uint idx = gl_GlobalInvocationID.x;
    /// The final workgroup can contain invocations beyond the buffer length.
    if (idx < values.length()) {
        values[idx] = values[idx] + 1;
    }
}
```

#### Additional Info

- [`MapPlacedGpuAccessTestInstance::iterate`](../../../modules/vulkan/memory/vktMemoryMapPlacedTests.cpp#L536-L549) flushes the host write for non-coherent memory before the dispatch and invalidates the mapped range after queue completion.
- The host dispatches `(numElements + 63) / 64` workgroups, matching the shader's `local_size_x = 64`. [`MapPlacedGpuAccessTestInstance::iterate`](../../../modules/vulkan/memory/vktMemoryMapPlacedTests.cpp#L648-L675)

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Test family | Only `gpu_access` creates a shader; the exact-size and reservation families are host-side virtual-memory checks. | [`MapPlacedTestCase::initPrograms`](../../../modules/vulkan/memory/vktMemoryMapPlacedTests.cpp#L860-L877) |
| Buffer size | The shader uses `values.length()`, so the bounds check adapts to the host-selected buffer extent. | [`MapPlacedGpuAccessTestInstance::iterate`](../../../modules/vulkan/memory/vktMemoryMapPlacedTests.cpp#L471-L483) |

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
               OpEntryPoint GLCompute %main "main" %gl_GlobalInvocationID
               OpExecutionMode %main LocalSize 64 1 1
               OpSource GLSL 450
               OpName %main "main"
               OpName %idx "idx"
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
               OpName %Data "Data"
               OpMemberName %Data 0 "values"
               OpName %_ ""
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %_runtimearr_uint ArrayStride 4
               OpDecorate %Data BufferBlock
               OpMemberDecorate %Data 0 Offset 0
               OpDecorate %_ Binding 0
               OpDecorate %_ DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
     %uint_0 = OpConstant %uint 0
%_ptr_Input_uint = OpTypePointer Input %uint
%_runtimearr_uint = OpTypeRuntimeArray %uint
       %Data = OpTypeStruct %_runtimearr_uint
%_ptr_Uniform_Data = OpTypePointer Uniform %Data
          %_ = OpVariable %_ptr_Uniform_Data Uniform
        %int = OpTypeInt 32 1
       %bool = OpTypeBool
      %int_0 = OpConstant %int 0
%_ptr_Uniform_uint = OpTypePointer Uniform %uint
     %uint_1 = OpConstant %uint 1
    %uint_64 = OpConstant %uint 64
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_64 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
        %idx = OpVariable %_ptr_Function_uint Function
         %14 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %15 = OpLoad %uint %14
               OpStore %idx %15
         %16 = OpLoad %uint %idx
         %21 = OpArrayLength %uint %_ 0
         %23 = OpBitcast %int %21
         %24 = OpBitcast %uint %23
         %26 = OpULessThan %bool %16 %24
               OpSelectionMerge %28 None
               OpBranchConditional %26 %27 %28
         %27 = OpLabel
         %30 = OpLoad %uint %idx
         %31 = OpLoad %uint %idx
         %33 = OpAccessChain %_ptr_Uniform_uint %_ %int_0 %31
         %34 = OpLoad %uint %33
         %36 = OpIAdd %uint %34 %uint_1
         %37 = OpAccessChain %_ptr_Uniform_uint %_ %int_0 %30
               OpStore %37 %36
               OpBranch %28
         %28 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- All cases require `VK_EXT_map_memory_placed`, `VK_KHR_map_memory2`, `memoryMapPlaced`, and Linux or Android POSIX mapping support. The two reservation families also require `memoryUnmapReserve`. [`MapPlacedTestCase::checkSupport`](../../../modules/vulkan/memory/vktMemoryMapPlacedTests.cpp#L827-L850) and [`MapNormalUnmapReserveTestCase::checkSupport`](../../../modules/vulkan/memory/vktMemoryMapPlacedTests.cpp#L893-L913)
- `exact_size` maps a host-visible allocation into a guarded memfd-backed region. After ordinary unmap, the inspector mapping must retain `0xAB` before and after the range, while the placed region must not expose the memfd fill pattern. The test also attempts a same-address remap and CPU read/write check. [`MapPlacedExactSizeTestInstance::iterate`](../../../modules/vulkan/memory/vktMemoryMapPlacedTests.cpp#L160-L424)
- `gpu_access` allocates host-visible memory, binds it to a storage buffer, reserves an aligned address range, and maps the allocation there. It records host-to-compute and compute-to-host buffer barriers around the dispatch, waits for the queue, then verifies every incremented value. [`MapPlacedGpuAccessTestInstance::iterate`](../../../modules/vulkan/memory/vktMemoryMapPlacedTests.cpp#L465-L715)
- `unmap_reserve` retains the placed range through `vkUnmapMemory2`; `normal_unmap_reserve` retains a legacy map's range. Both use OS-level observations as their result checks. [`MapPlacedExactSizeTestInstance::iterate`](../../../modules/vulkan/memory/vktMemoryMapPlacedTests.cpp#L266-L320) and [`MapNormalUnmapReserveTestInstance::iterate`](../../../modules/vulkan/memory/vktMemoryMapPlacedTests.cpp#L735-L806)

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `exact_size` | Incorrect requested-address placement, replacement of pages outside the placed range, or inaccessible/corrupted guard ranges. |
| `gpu_access` | Incorrect placed mapping access, host/device visibility handling, buffer binding, compute execution, or readback. |
| `unmap_reserve` | Incorrect reservation semantics after unmapping a placed mapping. |
| `normal_unmap_reserve` | Incorrect reservation semantics after `VK_MEMORY_UNMAP_RESERVE_BIT_EXT` is applied to a normal mapping. |

### Cause Analysis

#### Incorrect placed-map extent or address

**Possible failure symptoms:** `vkMapMemory2` returns a pointer different from `pPlacedAddress`, a guard byte differs from `0xAB`, or the inspector mapping still sees `0xAB` inside the Vulkan range.

**Possible implementation causes:** The extension requires the implementation to place the map at the supplied address on success. The symptoms point to an incorrect placed-map range or unintended replacement of pages outside it; source-level investigation is needed to localize an implementation fault.

#### CPU/GPU access or visibility failure

**Possible failure symptoms:** One or more readback elements differ from `i + 1` after the submitted compute work completes.

**Possible implementation causes:** The observed result can arise from an invalid buffer-memory binding, incorrect compute execution, or missing availability/visibility across the host and compute accesses. The test flushes and invalidates non-coherent memory and records matching buffer barriers, so an implementation investigation should begin with those contracts and the storage-buffer access path.

#### Reservation retained incorrectly

**Possible failure symptoms:** Guard pages are inaccessible or corrupted, `/proc/self/maps` does not cover the retained range, or a probe mapping overlaps the range after `VK_MEMORY_UNMAP_RESERVE_BIT_EXT`.

**Possible implementation causes:** The unmap-with-reservation path may have released or altered the virtual address reservation incorrectly. The CTS source provides the observable OS-level checks; source-level investigation is needed to distinguish Vulkan implementation behavior from platform mapping integration.

## Case Pruning

### Requirement-based pruning

- The entire test family skips when `VK_EXT_map_memory_placed`, `VK_KHR_map_memory2`, or `memoryMapPlaced` is unavailable.
- `unmap_reserve` and `normal_unmap_reserve` also skip when `memoryUnmapReserve` is unavailable.
- All cases require POSIX mapping facilities on Linux or Android. The source rejects other platforms.
- `gpu_access` skips if no chosen host-visible memory type is compatible with the storage buffer. [`MapPlacedGpuAccessTestInstance::iterate`](../../../modules/vulkan/memory/vktMemoryMapPlacedTests.cpp#L465-L493)

### Design-based pruning

- `gpu_access` uses only a 65536-byte buffer because its purpose is the CPU/GPU round trip, not a size matrix.
- The other families use the four page-scale sizes so they can expose placement and reservation errors at different ranges without duplicating shader work.

## Key Takeaways

- `exact_size` checks both the returned virtual address and the boundaries of the replaced mapping.
- `gpu_access` proves that the placed mapping remains the same usable memory after buffer binding and compute access.
- The two `UNMAP_RESERVE` families distinguish reserved-address behavior after placed and legacy mapping APIs.
- The non-coherent path needs cache operations in addition to the host/compute buffer barriers.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Exact-size and placed-reservation implementation | [`MapPlacedExactSizeTestInstance::iterate`](../../../modules/vulkan/memory/vktMemoryMapPlacedTests.cpp#L130-L433) | Creates the guard layout and checks exact placement, remapping, and placed-map reservation. |
| GPU access implementation | [`MapPlacedGpuAccessTestInstance::iterate`](../../../modules/vulkan/memory/vktMemoryMapPlacedTests.cpp#L435-L724) | Defines the storage buffer, compute submission, visibility operations, and readback rule. |
| Normal-map reservation implementation | [`MapNormalUnmapReserveTestInstance::iterate`](../../../modules/vulkan/memory/vktMemoryMapPlacedTests.cpp#L726-L815) | Checks retained reservation after legacy `vkMapMemory`. |
| Registration and shader generation | [`MapPlacedTestCase` and `createMapPlacedTests`](../../../modules/vulkan/memory/vktMemoryMapPlacedTests.cpp#L817-L997) | Defines feature gates, the compute shader, registered families, and size choices. |
| Mustpass coverage | [`memory.txt`](../../../mustpass/main/vk-default/memory.txt) | Contains the registered `dEQP-VK.memory.map_placed.*` paths. |
| Vulkan mapping semantics | [`memory.adoc`](../../../../vulkan-docs/src/chapters/memory.adoc#L4820-L5316) | Defines host mapping, placed map placement, and cache-management rules. |
