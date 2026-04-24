# [vktApiDescriptorPoolTests.cpp](../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L1)

## Overview

Tests Vulkan descriptor pool operations: repeated reset and free-then-reset cycles, out-of-pool-memory error reporting, and zero pool size count edge cases. On Vulkan SC, also tests repeated free-without-reset cycles across device recreation.

## Role of File

Implementation-heavy. Contains all test logic, support checks, and the registration function [createDescriptorPoolTests()](../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L509).

## Source Code

- Implementation: [vktApiDescriptorPoolTests.cpp](../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L1)
- Header: [vktApiDescriptorPoolTests.hpp](../../modules/vulkan/api/vktApiDescriptorPoolTests.hpp#L1)
- Parent registration: [vktApiTests.cpp](../../modules/vulkan/api/vktApiTests.cpp#L112)

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
  +-- repeated_free_no_reset_short       [SC only]
  +-- repeated_free_no_reset_long        [SC only]
```

## Test Families

### Repeated Reset

[resetDescriptorPoolTest()](../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L84) allocates 2048 descriptor sets (100 on SC) per iteration, then calls vkResetDescriptorPool. The short variant runs 2 iterations; the long variant runs 4096 iterations. The test passes if no crash or memory leak occurs. Uses VK_DESCRIPTOR_TYPE_SAMPLER with a single binding per layout. Registered at [line 516](../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L516) and [line 519](../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L519).

### Repeated Free and Reset

Same [resetDescriptorPoolTest()](../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L84) function but with `freeDescriptorSets=true`, meaning vkFreeDescriptorSets is called on the first descriptor set before vkResetDescriptorPool. The pool is created with VK_DESCRIPTOR_POOL_CREATE_FREE_DESCRIPTOR_SET_BIT. Short (2 iterations) and long (4096 iterations) variants. Registered at [line 522](../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L522) and [line 525](../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L525).

### Out of Pool Memory

[outOfPoolMemoryTest()](../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L174) creates descriptor pools with deliberately insufficient resources and attempts to allocate descriptor sets beyond pool capacity. Tests five failure scenarios: out of descriptor sets, out of descriptors due to number of sets, due to number of bindings, due to descriptor array size, and due to descriptor array size across all bindings. Each scenario is tested across all VkDescriptorType values. When VK_KHR_maintenance1 is supported, expects VK_ERROR_OUT_OF_POOL_MEMORY; otherwise any error is accepted. Registered at [line 528](../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L528).

### Zero Pool Size Count

[zeroPoolSizeCount()](../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L331) creates a descriptor pool with poolSizeCount=0 and maxSets=1, then allocates an empty descriptor set (no bindings). Verifies that vkAllocateDescriptorSets returns VK_SUCCESS and that vkFreeDescriptorSets also succeeds. Registered at [line 530](../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L530).

### Repeated Free No Reset (SC only)

[noResetDescriptorPoolTest()](../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L384) is a Vulkan SC-specific test that creates a custom device per iteration, allocates and frees descriptor sets without calling vkResetDescriptorPool, then destroys the device. Tests 2 iterations (short) and 200 iterations (long). Registered at [line 533](../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L533) and [line 537](../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L537).

## Parameter Dimensions

| Dimension | Observed Values |
|---|---|
| Iteration count | 2, 4096 (200 for SC no-reset long) |
| Descriptor sets per iteration | 2048 (100 on SC) |
| freeDescriptorSets flag | true, false |
| Pool create flags | 0, VK_DESCRIPTOR_POOL_CREATE_FREE_DESCRIPTOR_SET_BIT |
| Descriptor type | All VK_DESCRIPTOR_TYPE values (SAMPLER through INPUT_ATTACHMENT) |
| Pool size count | 0, 1 |
| Failure scenario | Out of sets, out of descriptors (3 sub-cases) |

## Support / Feature Requirements

| Feature / Extension | Used By |
|---|---|
| VK_KHR_maintenance1 | out_of_pool_memory (expects VK_ERROR_OUT_OF_POOL_MEMORY when supported) |
| VulkanSC recycleDescriptorSetMemory | checkSupportFreeDescriptorSets gates free-and-reset tests on SC |

## Verification Methods

- **Crash detection**: repeated_reset and repeated_free_reset tests pass if no crash occurs during many allocate/reset cycles ([line 170](../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L170))
- **VK_RESULT checking**: out_of_pool_memory checks that vkAllocateDescriptorSets returns an error when pool resources are exceeded; validates VK_ERROR_OUT_OF_POOL_MEMORY when VK_KHR_maintenance1 is present ([line 316](../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L316))
- **API success validation**: zero_pool_size_count verifies VK_SUCCESS from both vkAllocateDescriptorSets and vkFreeDescriptorSets ([line 370](../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L370), [line 376](../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L376))

## Test Principles Observed

- Resource leak detection: long-iteration tests are designed to surface memory leaks that would eventually crash
- Edge case coverage: zero pool size count tests a corner case of the spec
- Error code validation: out_of_pool_memory verifies correct error codes per the maintenance1 extension
- SC-specific behavior: separate test path for SC where vkResetDescriptorPool may not be used

## Notes / Uncertainties

- The VK_DESCRIPTOR_TYPE_LAST macro at [line 48](../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L48) is defined as VK_DESCRIPTOR_TYPE_INPUT_ATTACHMENT + 1, which may need updating if new descriptor types are added to the spec
- The out_of_pool_memory test logs "Not validated" if no errors are returned at all ([line 326](../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L326)), treating this as a pass since the implementation may have more resources than the test expects
