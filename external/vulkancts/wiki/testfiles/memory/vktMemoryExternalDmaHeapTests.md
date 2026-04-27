# External DMA Heap Memory Tests

Tests for `VK_EXT_external_memory_dma_buf` with DMA heap allocator integration. Validates that buffers backed by DMA heap memory can be allocated, bound, and accessed correctly by both the CPU (via import) and GPU (via compute shaders).

## Source

- [vktMemoryExternalDmaHeapTests.cpp](../../../modules/vulkan/memory/vktMemoryExternalDmaHeapTests.cpp)

## Registration

- **Group name:** `dma_heap_memory`
- **Registration function:** [`createDmaHeapTests()`](../../../modules/vulkan/memory/vktMemoryExternalDmaHeapTests.cpp:354)
- **Parent group:** `memory`

## Test Hierarchy

```
dma_heap_memory
├── allocate_and_bind
├── shader_access
└── shader_access_offset
```

## Test Families

### allocate_and_bind

Basic test that verifies DMA heap memory allocation and buffer binding succeeds. Creates a buffer with `VK_EXTERNAL_MEMORY_HANDLE_TYPE_DMA_BUF_BIT_EXT` and allocates memory from a `DmaHeapAllocator` ([vktMemoryExternalDmaHeapTests.cpp:132-157](../../../modules/vulkan/memory/vktMemoryExternalDmaHeapTests.cpp:132)).

### shader_access

End-to-end test verifying that DMA heap memory is accessible from both CPU and GPU:
1. A host-visible buffer is filled with a known pattern (value 42)
2. A compute shader copies data from the host-visible buffer to the DMA heap buffer
3. A second compute shader copies data back from the DMA heap buffer to the host-visible buffer
4. CPU reads back and verifies the pattern matches ([vktMemoryExternalDmaHeapTests.cpp:159-350](../../../modules/vulkan/memory/vktMemoryExternalDmaHeapTests.cpp:159))

### shader_access_offset

Same as `shader_access` but with a non-zero offset parameter (`offset = 20000`) passed to the DMA heap allocator. This tests that the allocator correctly handles offset alignment requirements using `nonCoherentAtomSize` ([vktMemoryExternalDmaHeapTests.cpp:173-183](../../../modules/vulkan/memory/vktMemoryExternalDmaHeapTests.cpp:173)).

## Parameter Dimensions

### Shader access test parameters

| Parameter | `shader_access` | `shader_access_offset` |
|-----------|-----------------|------------------------|
| `offset` | 0 | 20000 |
| Buffer size | 1024 × 4 bytes (4KB) | 1024 × 4 bytes (4KB) |
| Element count | 1024 | 1024 |
| Fill pattern | 42 | 42 |

### Buffer configuration

| Buffer | Usage | Memory Requirement |
|--------|-------|--------------------|
| Host-visible buffer | `STORAGE_BUFFER \| TRANSFER_DST` | `HostVisible` |
| DMA heap buffer | `STORAGE_BUFFER \| TRANSFER_DST` (with external memory) | `Any` (via DmaHeapAllocator) |

## Support Requirements

| Extension/Feature | Required by |
|-------------------|-------------|
| `VK_EXT_external_memory_dma_buf` | All tests ([vktMemoryExternalDmaHeapTests.cpp:59](../../../modules/vulkan/memory/vktMemoryExternalDmaHeapTests.cpp:59)) |
| `VK_EXTERNAL_MEMORY_FEATURE_IMPORTABLE_BIT` for DMA_BUF | All tests ([vktMemoryExternalDmaHeapTests.cpp:69-73](../../../modules/vulkan/memory/vktMemoryExternalDmaHeapTests.cpp:69)) |
| NOT `VK_EXTERNAL_MEMORY_FEATURE_DEDICATED_ONLY_BIT` | All tests ([vktMemoryExternalDmaHeapTests.cpp:75-79](../../../modules/vulkan/memory/vktMemoryExternalDmaHeapTests.cpp:75)) |
| `vk::DmaHeapAllocator::isSupported()` | All tests ([vktMemoryExternalDmaHeapTests.cpp:81-84](../../../modules/vulkan/memory/vktMemoryExternalDmaHeapTests.cpp:81)) |

## Verification Methods

### Shader access validation ([vktMemoryExternalDmaHeapTests.cpp:331-347](../../../modules/vulkan/memory/vktMemoryExternalDmaHeapTests.cpp:331))

After the compute shader round-trip (host → DMA heap → host), each element is compared:
```
inputPattern[i] == outputPattern[i]  // expected: all equal (value 42)
```
If any element differs, the test fails with the index and values logged.

### Synchronization

The command buffer includes explicit barriers between each stage:
1. `TRANSFER` → `COMPUTE_SHADER` barrier after `vkCmdFillBuffer` (clear DMA heap buffer to 24)
2. `COMPUTE_SHADER` → `TRANSFER` barrier after write dispatch (clear host buffer to 12)
3. `COMPUTE_SHADER` → `HOST` barrier after read dispatch (make result available to CPU)

## Test Principles

- **Round-trip verification:** Data flows host → DMA heap → host, ensuring bidirectional accessibility
- **Pre-fill verification:** Both buffers are pre-filled with known values (24 for DMA heap, 12 for host) before shader operations, ensuring the shader actually overwrites them
- **Offset alignment:** The `shader_access_offset` test verifies that the DMA heap allocator correctly handles non-zero offsets with proper alignment to `nonCoherentAtomSize`

## Notes

- The `DmaHeapAllocator` is a platform-specific allocator that allocates from Linux DMA heap interfaces
- The test uses `VK_BUFFER_USAGE_STORAGE_BUFFER_BIT` for both buffers, enabling compute shader access via storage buffer descriptors
- The DMA heap buffer is created with `VkExternalMemoryBufferCreateInfo` in the `pNext` chain of `VkBufferCreateInfo` ([vktMemoryExternalDmaHeapTests.cpp:197-205](../../../modules/vulkan/memory/vktMemoryExternalDmaHeapTests.cpp:197))
- Only Linux/Android platforms are supported — the test checks `vk::DmaHeapAllocator::isSupported()` and throws `NotSupportedError` otherwise
