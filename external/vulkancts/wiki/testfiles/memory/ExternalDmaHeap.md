## Overview

**Core question:** Can Vulkan import a Linux DMA heap allocation, bind it to a buffer, and access the payload correctly at zero and nonzero binding offsets?

- This page covers the `memory.dma_heap_memory` test family implemented by [`vktMemoryExternalDmaHeapTests.cpp`](../../../modules/vulkan/memory/vktMemoryExternalDmaHeapTests.cpp).
- The three test case leaves separate basic imported-memory allocation and binding from a compute-shader data round trip.
- The offset variant repeats the round trip with an aligned nonzero bind offset inside the imported allocation.
- Host comparison of 1024 `uint` values checks that data survives both shader copies.

## Background Knowledge

For the shared concepts host-visible and non-coherent memory, and flush and invalidate direction, see [Background Knowledge](../../categories/memory.md#background-knowledge) of the `memory` page.

- A Linux dma-buf file descriptor can identify memory allocated outside Vulkan. `VkImportMemoryFdInfoKHR` imports that payload into `VkDeviceMemory`, and a successful import transfers file-descriptor ownership to Vulkan.
- A buffer binding offset must satisfy the buffer memory alignment. The CTS allocator also aligns a requested offset to `nonCoherentAtomSize`, which keeps mapped non-coherent ranges suitable for flush or invalidation operations.

## Registration Hierarchy

```text
memory.dma_heap_memory
├── allocate_and_bind
├── shader_access
└── shader_access_offset
```

The default Vulkan mustpass list contains all three executable paths at [`dEQP-VK.memory.dma_heap_memory.*`](../../../mustpass/main/vk-default/memory.txt#L902-L904).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test case leaf | `allocate_and_bind`, `shader_access`, `shader_access_offset` | Selects basic import-and-bind behavior or one of two shader-access paths. | [`createDmaHeapTests()`](../../../modules/vulkan/memory/vktMemoryExternalDmaHeapTests.cpp#L354-L367) |
| Requested allocator offset | no offset, `0`, `20000` | The shader leaves choose zero or nonzero offset handling. The allocator rounds a nonzero request up to its required alignment. | [Offset setup](../../../modules/vulkan/memory/vktMemoryExternalDmaHeapTests.cpp#L173-L183), [alignment calculation](../../../framework/vulkan/vkMemUtil.cpp#L491-L503) |
| Buffer size | 8192 bytes; 4096 bytes | The allocation-only case binds an 8192-byte buffer. Shader cases use 1024 32-bit elements. | [Buffer setup](../../../modules/vulkan/memory/vktMemoryExternalDmaHeapTests.cpp#L145-L205) |
| Values | input `42`; DMA heap fill `24`; host fill `12` | Distinct fills make an omitted shader write visible during comparison. | [Initialization and commands](../../../modules/vulkan/memory/vktMemoryExternalDmaHeapTests.cpp#L207-L313) |
| Dispatch shape | 1024 workgroups of `1 x 1 x 1` invocations | One global invocation copies one `uint` in each direction. | [Shaders](../../../modules/vulkan/memory/vktMemoryExternalDmaHeapTests.cpp#L97-L130) |

## Behavior Parameters

The primary behavioral axis is the test case leaf. Each leaf changes the property checked by the family.

### `allocate_and_bind` - imported allocation and binding

This leaf checks the minimum DMA heap path. CTS allocates an 8192-byte Linux DMA heap payload, imports its file descriptor, chooses a compatible Vulkan memory type, and binds the memory to an external buffer. The case passes after construction succeeds; it does not inspect buffer contents.

### `shader_access` - zero-offset GPU round trip

This leaf checks shader access to imported DMA heap memory bound at offset zero. One compute shader copies 1024 values from a host-visible buffer into the external buffer. A second shader copies them back, and the host requires every result to equal `42`.

### `shader_access_offset` - aligned nonzero-offset GPU round trip

This leaf performs the same round trip after requesting offset `20000`. The allocator rounds the request up to the least common multiple of the buffer alignment and `nonCoherentAtomSize`, allocates space for the aligned prefix plus the buffer, and records that value as the binding offset.

## Shader Analysis

The `shader_access_offset` leaf is representative because it includes the same two fixed shaders and result check as `shader_access`, plus the nonzero allocator-offset path. The write shader is primary below. The read shader reverses the bindings to complete the round trip.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.memory.dma_heap_memory.shader_access_offset
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `shader_access_offset` | Selects the two-dispatch round trip with requested offset `20000`. |
| 1024 elements, local size `1 x 1 x 1` | Dispatch produces one invocation per `uint`. |
| write shader as primary | Shows the first GPU access that writes the imported payload. |

#### Purpose

The shader copies each host-initialized `uint` into the DMA heap buffer. The reverse shader later reads the payload back for host validation.

#### Structural Design

| Step | Shader action | Resource effect |
|------|---------------|-----------------|
| Index | Read `gl_GlobalInvocationID.x` | Select one of 1024 elements. |
| Load | Read binding 0 | Obtain input value `42`. |
| Store | Write binding 1 | Replace the DMA heap sentinel. |

#### Shader Code

##### Write Compute Shader

```glsl
#version 450

/// One invocation handles one uint. The host dispatches 1024 workgroups.
layout(local_size_x = 1, local_size_y = 1, local_size_z = 1) in;
/// Binding 0 is the 4096-byte host-visible storage buffer initialized to 42.
layout(set=0, binding = 0, std430) readonly buffer _input { uint hostVisibleData[]; };
/// Binding 1 is the 4096-byte buffer backed by imported DMA heap memory.
layout(set=0, binding = 1, std430) writeonly buffer _output { uint dmaHeapMemoryData[]; };

void main()
{
    /// Copy the element selected by this invocation into the imported payload.
    uint index = gl_GlobalInvocationID.x;
    dmaHeapMemoryData[index] = hostVisibleData[index];
}
```

##### Read Compute Shader

```glsl
#version 450

/// The second dispatch uses the same one-invocation-per-element shape.
layout(local_size_x = 1, local_size_y = 1, local_size_z = 1) in;
/// Binding 0 becomes the destination host-visible storage buffer.
layout(set=0, binding = 0, std430) writeonly buffer _output { uint hostVisibleData[]; };
/// Binding 1 remains the imported DMA heap buffer and becomes the source.
layout(set=0, binding = 1, std430) readonly buffer _input { uint dmaHeapMemoryData[]; };

void main()
{
    /// Return the imported payload to memory that the host can inspect.
    uint index = gl_GlobalInvocationID.x;
    hostVisibleData[index] = dmaHeapMemoryData[index];
}
```

#### Additional Info

- The read shader stays fixed across both shader-access leaves. It returns imported memory contents through the host-visible buffer because the test does not map the DMA heap allocation directly.
- Both pipelines use one descriptor set. API binding roles stay fixed, while shader access qualifiers and copy direction change.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Test case leaf | Both shader leaves use identical programs; `allocate_and_bind` has no shader. | [Registration](../../../modules/vulkan/memory/vktMemoryExternalDmaHeapTests.cpp#L357-L364) |
| Requested offset | No GLSL changes. The host binds at the allocator's aligned offset. | [Offset setup](../../../modules/vulkan/memory/vktMemoryExternalDmaHeapTests.cpp#L173-L183) |

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
; Bound: 34
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_GlobalInvocationID
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpName %main "main"
               OpName %index "index"
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
               OpName %_output "_output"
               OpMemberName %_output 0 "dmaHeapMemoryData"
               OpName %_ ""
               OpName %_input "_input"
               OpMemberName %_input 0 "hostVisibleData"
               OpName %__0 ""
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %_runtimearr_uint ArrayStride 4
               OpDecorate %_output BufferBlock
               OpMemberDecorate %_output 0 NonReadable
               OpMemberDecorate %_output 0 Offset 0
               OpDecorate %_ NonReadable
               OpDecorate %_ Binding 1
               OpDecorate %_ DescriptorSet 0
               OpDecorate %_runtimearr_uint_0 ArrayStride 4
               OpDecorate %_input BufferBlock
               OpMemberDecorate %_input 0 NonWritable
               OpMemberDecorate %_input 0 Offset 0
               OpDecorate %__0 NonWritable
               OpDecorate %__0 Binding 0
               OpDecorate %__0 DescriptorSet 0
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
    %_output = OpTypeStruct %_runtimearr_uint
%_ptr_Uniform__output = OpTypePointer Uniform %_output
          %_ = OpVariable %_ptr_Uniform__output Uniform
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_runtimearr_uint_0 = OpTypeRuntimeArray %uint
     %_input = OpTypeStruct %_runtimearr_uint_0
%_ptr_Uniform__input = OpTypePointer Uniform %_input
        %__0 = OpVariable %_ptr_Uniform__input Uniform
%_ptr_Uniform_uint = OpTypePointer Uniform %uint
     %uint_1 = OpConstant %uint 1
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
      %index = OpVariable %_ptr_Function_uint Function
         %14 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %15 = OpLoad %uint %14
               OpStore %index %15
         %22 = OpLoad %uint %index
         %27 = OpLoad %uint %index
         %29 = OpAccessChain %_ptr_Uniform_uint %__0 %int_0 %27
         %30 = OpLoad %uint %29
         %31 = OpAccessChain %_ptr_Uniform_uint %_ %int_0 %22
               OpStore %31 %30
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- CTS requires `VK_EXT_external_memory_dma_buf`, queries external storage-buffer properties, and requires `IMPORTABLE`. It skips `DEDICATED_ONLY` implementations because this allocator path has no dedicated-allocation chain.
- `DmaHeapAllocator` opens `/dev/dma_heap/system`, allocates a dma-buf with `DMA_HEAP_IOCTL_ALLOC`, obtains compatible memory types with `vkGetMemoryFdPropertiesKHR`, and intersects them with buffer constraints.
- The allocator imports the descriptor through `VkImportMemoryFdInfoKHR`. Successful Vulkan allocation takes ownership of it.
- Shader cases create a host-visible storage buffer and an external DMA heap buffer. The host writes `42` into all 1024 input elements and flushes the host allocation.
- The command buffer fills the external buffer with `24`, makes that transfer available to compute, and dispatches the write shader. It fills the host buffer with `12` after ordering the earlier shader read before the transfer write.
- A transfer-to-compute barrier precedes the read shader. A compute-to-host barrier makes its writes available to the final host read.
- After queue completion, CTS invalidates the host allocation and compares every output with the original input. It reports the first mismatching index and values.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `allocate_and_bind` | DMA heap allocation, dma-buf import, compatible memory-type selection, external buffer binding, or external-memory lifetime failure. |
| `shader_access` | Zero-offset imported-memory shader access, descriptor/pipeline setup, command synchronization, or host cache-management failure. |
| `shader_access_offset` | Any `shader_access` cause, plus incorrect offset alignment, allocation sizing, or binding at the nonzero imported-memory offset. |

### Cause Analysis

#### DMA heap allocation, import, memory-type selection, binding, or lifetime failure

**Possible failure symptoms:** `allocate_and_bind` cannot construct its external buffer and allocation. A shader leaf can also stop during setup before dispatch.

**Possible implementation causes:** The DMA heap may fail to produce a usable dma-buf, `vkGetMemoryFdPropertiesKHR` may expose no compatible memory type, or import and binding may mishandle the descriptor or payload lifetime. Vulkan transfers descriptor ownership after a successful import.

#### Shader access, descriptor/pipeline, synchronization, or host cache-management failure

**Possible failure symptoms:** One or more returned elements differ from `42`. An untouched destination may retain a sentinel derived from `24` or `12`; other values indicate corruption or incorrect access.

**Possible implementation causes:** Descriptor access may target the wrong buffer or element, compute execution may fail to preserve writes for the second shader, or final writes may not become visible to the host. Incorrect host flush or invalidation can produce the same result. The logged index and value guide source-level investigation.

#### Nonzero offset alignment, allocation sizing, or binding failure

**Possible failure symptoms:** `shader_access_offset` fails during allocation or binding, or its data differs from `42` while the zero-offset leaf passes.

**Possible implementation causes:** The requested offset may be rounded incorrectly, the dma-buf allocation may omit the aligned prefix, or Vulkan may bind at a different offset. The allocator must satisfy both `VkMemoryRequirements::alignment` and its non-coherent atom rule.

## Case Pruning

### Requirement-based pruning

- All leaves require `VK_EXT_external_memory_dma_buf` and `VK_EXTERNAL_MEMORY_FEATURE_IMPORTABLE_BIT` for the tested storage-buffer usage.
- CTS reports `NotSupported` for dedicated-only memory, absent DMA heap support, failed system-heap allocation, or no compatible Vulkan memory type.
- The allocator works on Linux and Android builds. Other platforms report it as unsupported.

### Design-based pruning

- The family uses one allocation-only size and one fixed shader workload instead of a broad size, pattern, or workgroup matrix.
- Two shader leaves separate zero-offset access from a nonzero request that forces alignment. Their shader logic remains identical so behavioral differences come from offset handling.
- Dedicated-only memory is outside this allocator design because the import omits `VkMemoryDedicatedAllocateInfo`.

## Key Takeaways

- `allocate_and_bind` isolates allocation, import, compatible memory-type selection, and binding from shader execution.
- The shader leaves send 1024 values through imported memory and back, with sentinel fills that expose missing writes.
- `shader_access_offset` checks the round trip after the allocator aligns a nonzero request and enlarges the allocation.
- See `## Failure Meaning` to distinguish setup failures, data mismatches, and offset-specific failures.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Capability checks | [`checkDmaHeapMemory()`](../../../modules/vulkan/memory/vktMemoryExternalDmaHeapTests.cpp#L54-L85) | Defines extension, importability, dedicated-only, and allocator gates. |
| Compute programs | [`initProgramsDmaHeapMemoryShaderAccess()`](../../../modules/vulkan/memory/vktMemoryExternalDmaHeapTests.cpp#L97-L130) | Supplies both reconstructed shaders. |
| Allocation-only case | [`testDmaHeapMemoryAllocateAndBind()`](../../../modules/vulkan/memory/vktMemoryExternalDmaHeapTests.cpp#L132-L157) | Implements basic allocation and binding. |
| Shader setup | [`testDmaHeapMemoryShaderAccess()` setup](../../../modules/vulkan/memory/vktMemoryExternalDmaHeapTests.cpp#L159-L259) | Creates offset configuration, resources, and pipelines. |
| Commands and comparison | [`testDmaHeapMemoryShaderAccess()` execution](../../../modules/vulkan/memory/vktMemoryExternalDmaHeapTests.cpp#L261-L349) | Records fills, barriers, dispatches, visibility, and comparison. |
| Registration | [`createDmaHeapTests()`](../../../modules/vulkan/memory/vktMemoryExternalDmaHeapTests.cpp#L354-L367) | Registers all leaves and offsets. |
| DMA heap allocator | [`DmaHeapAllocator::allocate()`](../../../framework/vulkan/vkMemUtil.cpp#L491-L548) | Implements alignment, dma-buf allocation, memory-type selection, and import. |
| dma-buf semantics | [External memory handle types](../../../../vulkan-docs/src/chapters/capabilities.adoc#L612-L617) | Defines `DMA_BUF` as a Linux dma-buf descriptor. |
| Import semantics | [`VkImportMemoryFdInfoKHR`](../../../../vulkan-docs/src/chapters/memory.adoc#L2619-L2678) | Defines file-descriptor import and ownership transfer. |
