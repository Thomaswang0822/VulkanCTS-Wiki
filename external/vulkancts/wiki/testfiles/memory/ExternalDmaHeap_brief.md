# Understanding Brief: External DMA Heap Memory Tests

## One-Sentence Test Purpose

This test family checks whether Vulkan can import Linux DMA heap allocations as `DMA_BUF` buffer memory, bind them, and preserve data through GPU storage-buffer access, including an allocation with a nonzero aligned bind offset.

## Background Knowledge

### DMA heap allocation and Vulkan external-memory import

A Linux DMA heap allocation is represented by a dma-buf file descriptor. Vulkan does not allocate that underlying payload in these tests. The CTS allocator obtains the file descriptor from `/dev/dma_heap/system`, queries which Vulkan memory types can import it, and passes it through `VkImportMemoryFdInfoKHR` when allocating `VkDeviceMemory`.

Why it matters here:
- `VK_EXTERNAL_MEMORY_HANDLE_TYPE_DMA_BUF_BIT_EXT` identifies the file descriptor as a Linux dma-buf.
- A successful import transfers file-descriptor ownership to the Vulkan implementation.
- Buffer creation must declare the same external handle type, and the imported memory type must satisfy both the dma-buf properties and the buffer's memory requirements.

### Binding offset and non-coherent atom alignment

A buffer may bind to an offset within a larger memory allocation. The offset must satisfy the buffer memory requirement alignment. CTS also aligns the offset to `nonCoherentAtomSize` so that a host-visible imported allocation could be mapped, flushed, or invalidated without violating non-coherent atom rules.

Why it matters here:
- The offset case supplies the unaligned requested value `20000`.
- `DmaHeapAllocator` rounds that request up to the least common multiple of the buffer alignment and `nonCoherentAtomSize`, then allocates `memoryRequirements.size + alignedOffset` bytes.

## One Concrete Example

For `dEQP-VK.memory.dma_heap_memory.shader_access_offset`, the host creates a 4 KiB host-visible storage buffer and a 4 KiB externally backed storage buffer. It initializes 1024 `uint` elements in the host-visible buffer to `42`. The allocator imports a DMA heap allocation and binds the external buffer at an aligned offset derived from `20000`.

Two compute shaders perform a round trip:

```text
host-visible buffer (42) -> write shader -> DMA heap buffer
DMA heap buffer          -> read shader  -> host-visible buffer
```

Before each shader writes its destination, the command buffer fills that destination with a different sentinel value. A final host comparison therefore detects a missing write as well as corrupted imported-memory access.

## End-to-End Test Flow

```text
[host] check DMA_BUF import support, reject dedicated-only imports, and check DMA heap availability
[host] choose allocate-only, zero-offset shader access, or nonzero-offset shader access
[host] allocate a Linux DMA heap payload and import its file descriptor into VkDeviceMemory
[host] create and bind the external buffer; shader cases also create a host-visible buffer
[host] initialize 1024 host-visible uint elements to 42 and flush the allocation
[host] fill the DMA heap buffer with 24 and issue a transfer-to-compute barrier
[device] dispatch 1024 compute workgroups to copy host-visible data into DMA heap memory
[host] fill the host-visible buffer with 12 after the required compute-to-transfer ordering
[device] dispatch 1024 compute workgroups to copy DMA heap data back into host-visible memory
[host] make shader writes available to host reads, submit, wait, and invalidate the host allocation
[host] compare every returned uint with 42 and report the first mismatch
```

The `allocate_and_bind` path stops after successful imported allocation and binding. Vulkan or CTS helper failures surface through the normal test framework; the case has no content comparison.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

`initProgramsDmaHeapMemoryShaderAccess()` adds two fixed GLSL 4.50 compute shaders. Each uses a `1 x 1 x 1` local size and indexes one `uint` with `gl_GlobalInvocationID.x`. The write shader copies binding 0 to binding 1. The read shader reverses the resource roles. No explicit `ShaderBuildOptions` are supplied, so CTS uses its baseline SPIR-V target, SPIR-V 1.0.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Host-visible buffer | yes | yes, descriptor binding 0 | read by the first shader and written by the second | yes | Holds the original pattern and the final round-trip result. |
| DMA heap buffer | yes, with external-memory buffer metadata | yes, descriptor binding 1 | written by the first shader and read by the second | no direct host read | Exercises imported dma-buf memory through Vulkan shader access. |
| DMA heap file descriptor | yes, through the Linux DMA heap ioctl | imported, not shader-visible | no | no | Carries ownership of the external payload into `VkDeviceMemory`. |
| Descriptor set | yes | yes | selects both storage buffers | no | Both pipelines use the same bindings; only shader access qualifiers and copy direction differ. |
| Two compute pipelines | yes | yes | dispatch one invocation per element | no | Provide the forward and reverse copies used by validation. |

## What Is Checked

- `allocate_and_bind` passes if CTS can allocate DMA heap memory, import it, choose a compatible memory type, and bind an 8192-byte external buffer.
- `shader_access` and `shader_access_offset` compare all 1024 returned `uint` elements against the original value `42`.
- The DMA heap destination starts with `24`, and the host-visible return destination starts with `12`. These sentinels distinguish an untouched destination from the expected copy result.
- The first mismatch fails the case and reports its index plus the input and output values.

## Behavior Parameter Identification

> **Behavior parameter:** test case leaf
>
> **Candidate values:** `allocate_and_bind`, `shader_access`, `shader_access_offset`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `allocate_and_bind` | DMA heap allocation, dma-buf import, compatible memory-type selection, external buffer binding, or external-memory lifetime failure. |
| `shader_access` | Zero-offset imported-memory shader access, descriptor/pipeline setup, command synchronization, or host cache-management failure. |
| `shader_access_offset` | Any `shader_access` cause, plus incorrect offset alignment, allocation sizing, or binding at the nonzero imported-memory offset. |

## Important Variations and Special Cases

- All three leaves require `VK_EXT_external_memory_dma_buf`, importable external storage-buffer memory, and an environment where `DmaHeapAllocator` is supported.
- The test rejects a `DEDICATED_ONLY` capability because `DmaHeapAllocator` imports a suballocated-style memory object and does not use a dedicated-allocation chain.
- `shader_access` requests offset `0`. `shader_access_offset` requests `20000`; the allocator computes the actual aligned offset.
- The two shader leaves use identical shader source, dispatch shape, buffer size, patterns, and validation. Only allocator offset configuration changes.
- The source compiles DMA heap support only on Linux or Android. Other platforms report the allocator as unsupported.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Capability checks | [`checkDmaHeapMemory()`](../../../modules/vulkan/memory/vktMemoryExternalDmaHeapTests.cpp#L54-L85) | Requires the extension, import support, non-dedicated import, and platform allocator support. |
| Shader generation | [`initProgramsDmaHeapMemoryShaderAccess()`](../../../modules/vulkan/memory/vktMemoryExternalDmaHeapTests.cpp#L97-L130) | Defines both fixed compute copy shaders. |
| Allocation-only behavior | [`testDmaHeapMemoryAllocateAndBind()`](../../../modules/vulkan/memory/vktMemoryExternalDmaHeapTests.cpp#L132-L157) | Creates and binds the 8192-byte external buffer. |
| Shader-access setup | [`testDmaHeapMemoryShaderAccess()` resource setup](../../../modules/vulkan/memory/vktMemoryExternalDmaHeapTests.cpp#L159-L259) | Configures offset handling, buffers, descriptors, and pipelines. |
| Dispatch and validation | [`testDmaHeapMemoryShaderAccess()` execution](../../../modules/vulkan/memory/vktMemoryExternalDmaHeapTests.cpp#L261-L349) | Records fills, barriers, two dispatches, readback, and comparison. |
| Registered leaves | [`createDmaHeapTests()`](../../../modules/vulkan/memory/vktMemoryExternalDmaHeapTests.cpp#L354-L367) | Registers the three exact cases and their offset values. |
| DMA heap import implementation | [`DmaHeapAllocator::allocate()`](../../../framework/vulkan/vkMemUtil.cpp#L491-L548) | Aligns offsets, allocates a dma-buf, selects a memory type, imports it, and records the bind offset. |
| External handle semantics | [Vulkan external-memory handle types](../../../../vulkan-docs/src/chapters/capabilities.adoc#L612-L617) | Defines the DMA_BUF handle as a Linux dma-buf file descriptor that owns a payload reference. |
| File-descriptor import semantics | [`VkImportMemoryFdInfoKHR`](../../../../vulkan-docs/src/chapters/memory.adoc#L2619-L2678) | Defines import support and ownership-transfer requirements. |

## Questions / Risk Points for User Audit

- Does the test-case-leaf axis match the three distinct behaviors exposed by registration?
- Is it clear that the nonzero requested offset is rounded up rather than used literally as the bind offset?
- Is the distinction between the Linux dma-buf payload, imported `VkDeviceMemory`, and bound Vulkan buffer clear?
- The inspected source, mustpass lists, allocator implementation, and Vulkan specification resolve the behavior and validation questions; no semantic risk point remains open.

## Conversion Notes for Final Wiki Rewrite

- Keep the external-memory import and aligned-offset concepts as short prerequisites.
- Use `shader_access_offset` as the representative walkthrough because it includes the ordinary round trip and the additional offset condition.
- Carry the test-case-leaf behavior axis into `## Behavior Parameters`.
- Copy the `### Failure Cause Mapping` table unchanged into the final page.
- Move allocator, registration, mustpass, and specification links into a focused source appendix.
