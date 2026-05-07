# [vktApiDescriptorPoolTests.cpp](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L1)

## Overview

Tests Vulkan descriptor pool operations: repeated reset, free-and-reset cycles, out-of-pool-memory error handling, and zero-pool-size pool creation. Verifies that descriptor pool resources are properly recycled and that allocation failures return correct error codes.

## Role of File

Implementation-heavy. Contains all test logic and the registration function [createDescriptorPoolTests()](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L509).

## Source Code

- Implementation: [vktApiDescriptorPoolTests.cpp](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L1)
- Header: [vktApiDescriptorPoolTests.hpp](../../../modules/vulkan/api/vktApiDescriptorPoolTests.hpp#L1)
- Parent registration: [vktApiTests.cpp](../../../modules/vulkan/api/vktApiTests.cpp#L112)

## Registration Path

```
api
  +-- descriptor_pool
```

## Test Hierarchy

```
descriptor_pool
  +-- repeated_reset_short
  +-- repeated_reset_long
  +-- repeated_free_reset_short
  +-- repeated_free_reset_long
  +-- out_of_pool_memory
  +-- zero_pool_size_count
  +-- repeated_free_no_reset_short     [SC only]
  +-- repeated_free_no_reset_long      [SC only]
```

## Test Families

### Repeated Reset

[resetDescriptorPoolTest()](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L84) allocates descriptor sets from a pool and resets the pool repeatedly. `repeated_reset_short` runs 2 iterations; `repeated_reset_long` runs 4096 iterations (100 on SC). This verifies that pool reset properly recycles resources without memory leaks.

### Repeated Free and Reset

The same [resetDescriptorPoolTest()](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L84) with `freeDescriptorSets=true` allocates descriptor sets, frees them with vkFreeDescriptorSets, then resets the pool. `repeated_free_reset_short` runs 2 iterations; `repeated_free_reset_long` runs 4096 iterations. This verifies that free-then-reset cycles work correctly.

### Out of Pool Memory

[outOfPoolMemoryTest()](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L174) creates descriptor pools with insufficient resources and attempts to allocate more descriptor sets than the pool can hold. Verifies that VK_ERROR_OUT_OF_POOL_MEMORY is returned when VK_KHR_maintenance1 is supported. Tests multiple failure scenarios: out of descriptor sets, out of descriptors due to binding count, and out of descriptors due to array size.

### Zero Pool Size Count

[zeroPoolSizeCount()](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L331) creates a descriptor pool with zero pool sizes (maxSets=1, poolSizeCount=0) and verifies that an empty descriptor set can be allocated and freed from it.

### Repeated Free No Reset (SC only)

[noResetDescriptorPoolTest()](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L384) is a Vulkan SC-specific test that allocates and frees descriptor sets without resetting the pool, instead destroying and recreating the device. `repeated_free_no_reset_short` runs 2 iterations; `repeated_free_no_reset_long` runs 200 iterations.

## Parameter Dimensions

| Dimension | Observed Values |
|---|---|
| Iteration count | 2 (short), 200 (SC long), 4096 (non-SC long) |
| Free before reset | true, false |
| Pool flags | 0, VK_DESCRIPTOR_POOL_CREATE_FREE_DESCRIPTOR_SET_BIT |
| Descriptor type | All VK_DESCRIPTOR_TYPE values (in out_of_pool_memory) |
| Failure case | Out of sets, out of descriptors by binding count, out of descriptors by array size |

## Support / Feature Requirements

| Feature / Extension | Used By |
|---|---|
| VK_KHR_maintenance1 | out_of_pool_memory (expected to return VK_ERROR_OUT_OF_POOL_MEMORY) |
| VulkanSC recycleDescriptorSetMemory | repeated_free_reset tests on SC |

## Verification Methods

- **Crash detection**: reset tests pass if no crash or memory leak occurs during repeated cycles
- **VK_CHECK**: API calls are verified for VK_SUCCESS
- **Error code verification**: out_of_pool_memory tests verify VK_ERROR_OUT_OF_POOL_MEMORY is returned when expected
- **Allocation success**: zero_pool_size_count verifies that allocation and free succeed

## Test Principles Observed

- Resource leak detection: repeated reset/free cycles expose memory leaks
- Error code correctness: out-of-pool conditions must return the correct Vulkan error code
- Edge case coverage: zero-size pool tests an unusual but valid configuration
- SC divergence: Vulkan SC has separate no-reset tests and reduced iteration counts

## Notes / Uncertainties

- The out_of_pool_memory test iterates over all descriptor types, making it one of the more thorough tests
- On SC, the number of descriptor sets per iteration is reduced from 2048 to 100
- The noResetDescriptorPoolTest creates a custom device for each iteration, which is expensive but necessary for SC
