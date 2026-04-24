# [vktApiComputeInstanceResultBuffer.cpp](../../modules/vulkan/api/vktApiComputeInstanceResultBuffer.cpp#L1)

## Overview

Provides the `ComputeInstanceResultBuffer` class, a self-contained utility that creates a host-visible storage buffer for compute shader output, initializes it with a sentinel value, and provides methods to read back results and create memory barriers for synchronization.

## Role of File

Utility/helper. Provides a reusable result buffer abstraction consumed by compute-based API tests.

## Source Code

- Implementation: [vktApiComputeInstanceResultBuffer.cpp](../../modules/vulkan/api/vktApiComputeInstanceResultBuffer.cpp#L1)
- Header: [vktApiComputeInstanceResultBuffer.hpp](../../modules/vulkan/api/vktApiComputeInstanceResultBuffer.hpp#L1)

## Registration Path

Utility file. Not directly registered in the test hierarchy. Used by other test files that need a compute result buffer.

## Test Hierarchy

Not applicable (utility file).

## Classes and Utilities

### ComputeInstanceResultBuffer ([L38](../../modules/vulkan/api/vktApiComputeInstanceResultBuffer.hpp#L38))

A class that encapsulates a storage buffer for compute shader output. Key characteristics:

- **DATA_SIZE**: `sizeof(tcu::Vec4[4])` = 64 bytes ([L43](../../modules/vulkan/api/vktApiComputeInstanceResultBuffer.hpp#L43)). The buffer holds 4 Vec4 values.
- **Constructor** ([L34](../../modules/vulkan/api/vktApiComputeInstanceResultBuffer.cpp#L34)): Takes `DeviceInterface`, `VkDevice`, `Allocator`, and optional `initValue` (default -1.0f). Creates the buffer, allocates host-visible memory, binds it, fills with `initValue`, and flushes.
- **readResultContentsTo(tcu::Vec4 (*results)[4])** ([L44](../../modules/vulkan/api/vktApiComputeInstanceResultBuffer.cpp#L44)): Invalidates the allocation and copies 64 bytes (4 Vec4s) to the output array.
- **readResultContentsTo(uint32_t *result)** ([L50](../../modules/vulkan/api/vktApiComputeInstanceResultBuffer.cpp#L50)): Invalidates the allocation and copies a single uint32_t to the output.
- **getBuffer()** ([L53](../../modules/vulkan/api/vktApiComputeInstanceResultBuffer.hpp#L53)): Returns the underlying `VkBuffer` handle.
- **getResultReadBarrier()** ([L58](../../modules/vulkan/api/vktApiComputeInstanceResultBuffer.hpp#L58)): Returns a `VkBufferMemoryBarrier` with `srcAccessMask=VK_ACCESS_SHADER_WRITE_BIT` and `dstAccessMask=VK_ACCESS_HOST_READ_BIT`, suitable for inserting after compute dispatch to ensure host visibility.

### createResultBuffer (private static) ([L56](../../modules/vulkan/api/vktApiComputeInstanceResultBuffer.cpp#L56))

Creates a `VK_BUFFER_USAGE_STORAGE_BUFFER_BIT` buffer of `DATA_SIZE` bytes, allocates host-visible memory, binds it, fills with the `initValue` repeated across the entire buffer, and flushes.

### createResultBufferBarrier (private static) ([L90](../../modules/vulkan/api/vktApiComputeInstanceResultBuffer.cpp#L90))

Creates a `VkBufferMemoryBarrier` for the result buffer covering the full `DATA_SIZE`, transitioning from shader write to host read access.

## Parameter Dimensions

Not applicable (utility file). The buffer size is fixed at `sizeof(tcu::Vec4[4])` = 64 bytes.

## Support / Feature Requirements

No extension requirements. Uses core Vulkan functionality only.

## Verification Methods

Not applicable (utility file). This class provides infrastructure for reading compute shader results; verification is performed by the consuming test instances. The sentinel initialization value (-1.0f) allows consuming tests to detect whether the compute shader has written to the buffer.

## Test Principles Observed

- **Self-contained resource management**: The class owns the buffer, allocation, and barrier, ensuring proper RAII cleanup.
- **Sentinel initialization**: The buffer is pre-filled with a known value (-1.0f), enabling detection of unwritten results.
- **Synchronization support**: The built-in `getResultReadBarrier()` provides a correctly configured memory barrier for the common compute-to-host-read pattern.

## Notes / Uncertainties

- The `DATA_SIZE` is fixed at 64 bytes (4 Vec4s), which limits the utility to tests that need at most 4 Vec4 output values. Tests requiring larger result buffers would need a different approach.
- The `readResultContentsTo(uint32_t *result)` overload ([L50](../../modules/vulkan/api/vktApiComputeInstanceResultBuffer.cpp#L50)) only reads a single uint32_t but invalidates the entire allocation, which is correct but may be slightly inefficient for very small reads.
- The `createResultBufferBarrier` creates a barrier with `VK_QUEUE_FAMILY_IGNORED` for both source and destination queue family indices, which means it does not support queue-family ownership transfers.
- The class stores `const` references to `DeviceInterface` and `VkDevice`, meaning the caller must ensure these remain valid for the lifetime of the `ComputeInstanceResultBuffer` instance.
