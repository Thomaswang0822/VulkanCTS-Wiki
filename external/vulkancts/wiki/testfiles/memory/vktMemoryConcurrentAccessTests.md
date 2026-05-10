# Memory Concurrent Access Tests

Tests for concurrent access to device memory from both the host (CPU) and device (compute shader). Verifies that while a compute shader writes to specific elements of a storage buffer, the host can simultaneously read unwritten elements without observing torn or corrupted values, and that after shader completion with an appropriate pipeline barrier, all written values are correctly visible to the host.

## Source

[`vktMemoryConcurrentAccessTests.cpp`](../../../modules/vulkan/memory/vktMemoryConcurrentAccessTests.cpp)

## Verified Group Name

`concurrent_access` ([line 291](../../../modules/vulkan/memory/vktMemoryConcurrentAccessTests.cpp#L291))

## Registration Hierarchy

```text
memory.concurrent_access
└── shader_and_host
```

## Test Families

### shader_and_host

A single test case that exercises concurrent host+device access to a storage buffer. The test:

1. Allocates a 501-byte buffer with `HOST_VISIBLE | COHERENT` memory ([line 118](../../../modules/vulkan/memory/vktMemoryConcurrentAccessTests.cpp#L118)).
2. Fills the buffer with a known byte pattern (`0b01011011`) via host pointer ([line 135](../../../modules/vulkan/memory/vktMemoryConcurrentAccessTests.cpp#L135)).
3. Dispatches a compute shader that reads every other element (even indices) and replaces it with a different pattern (`0b11001010`) if the original value matches ([line 260](../../../modules/vulkan/memory/vktMemoryConcurrentAccessTests.cpp#L260)).
4. A **second thread** concurrently reads the odd-indexed elements (not being written by the shader) and verifies they still match the initial pattern ([line 77](../../../modules/vulkan/memory/vktMemoryConcurrentAccessTests.cpp#L77)).
5. After the shader completes (with a `vkCmdPipelineBarrier` from `COMPUTE_SHADER` to `HOST`), the second thread validates the entire buffer: even indices should have the shader-written value, odd indices should retain the initial value ([line 91](../../../modules/vulkan/memory/vktMemoryConcurrentAccessTests.cpp#L91)).

## Parameter Dimensions

| Dimension | Values | Source |
|-----------|--------|--------|
| Buffer size | 501 bytes (odd, to stress alignment) | [line 118](../../../modules/vulkan/memory/vktMemoryConcurrentAccessTests.cpp#L118) |
| Smallest integer type | uint8, uint16, or uint32 (depends on 8-bit/16-bit storage support) | [line 128](../../../modules/vulkan/memory/vktMemoryConcurrentAccessTests.cpp#L128) |
| Initial byte pattern | `0b01011011` | [line 113](../../../modules/vulkan/memory/vktMemoryConcurrentAccessTests.cpp#L113) |
| Shader byte pattern | `0b11001010` | [line 114](../../../modules/vulkan/memory/vktMemoryConcurrentAccessTests.cpp#L114) |

## Support / Feature Requirements

| Requirement | Condition | Source |
|-------------|-----------|--------|
| Host-visible + coherent memory | `MemoryRequirement::HostVisible | MemoryRequirement::Coherent` | [line 122](../../../modules/vulkan/memory/vktMemoryConcurrentAccessTests.cpp#L122) |
| Storage buffer | `VK_BUFFER_USAGE_STORAGE_BUFFER_BIT` | [line 119](../../../modules/vulkan/memory/vktMemoryConcurrentAccessTests.cpp#L119) |
| 8-bit storage (optional) | `VK_EXT_shader_8bit_storage` / `uniformAndStorageBuffer8BitAccess` | [line 131](../../../modules/vulkan/memory/vktMemoryConcurrentAccessTests.cpp#L131) |
| 16-bit storage (optional) | `VK_EXT_shader_16bit_storage` / `uniformAndStorageBuffer16BitAccess` | [line 129](../../../modules/vulkan/memory/vktMemoryConcurrentAccessTests.cpp#L129) |

## Verification Methods

1. **Concurrent read validation**: The second thread reads odd-indexed elements during shader execution and verifies they match the initial pattern ([`secondThreadFunction()`](../../../modules/vulkan/memory/vktMemoryConcurrentAccessTests.cpp#L64)). A `WRONG_INITIAL_VALUE_DURING_COMPUTE_SHADER` result indicates a data race.
2. **Post-barrier full validation**: After the pipeline barrier signals completion, the second thread validates the entire buffer. Even indices should contain the shader-written value; odd indices should contain the initial value ([line 91](../../../modules/vulkan/memory/vktMemoryConcurrentAccessTests.cpp#L91)). Errors are classified as `WRONG_SHADER_VALUE_AFTER_COMPUTE_SHADER` or `WRONG_INITIAL_VALUE_AFTER_COMPUTE_SHADER`.
3. **Thread synchronization**: A `std::mutex` ensures the second thread does not begin post-barrier validation until the main thread signals after `submitCommandsAndWait()` ([line 199](../../../modules/vulkan/memory/vktMemoryConcurrentAccessTests.cpp#L199)).

## Test Principles

- **Concurrent access safety**: The shader writes to even indices while the host reads odd indices simultaneously. This tests that the implementation does not corrupt adjacent memory locations during concurrent access.
- **Pipeline barrier effectiveness**: The `vkCmdPipelineBarrier` from `COMPUTE_SHADER` to `HOST` must ensure that shader writes are visible to the host after the barrier completes.
- **Smallest integer granularity**: The test picks the smallest supported integer type (8-bit, 16-bit, or 32-bit) to stress finer granularity of concurrent access.

## Notes

- This is a VK+VKSC test (not excluded from Vulkan SC) because it does not depend on `VkAllocationCallbacks` or `vkFreeMemory`.
- The test uses C++ `std::thread` for concurrent host access, with a `std::mutex` for synchronization ([line 46](../../../modules/vulkan/memory/vktMemoryConcurrentAccessTests.cpp#L46)).
- The buffer size (501) is deliberately odd to create misalignment with typical integer boundaries, increasing the chance of catching implementation bugs.
- Copyright date is 2024, making this one of the newer tests in the memory category.
