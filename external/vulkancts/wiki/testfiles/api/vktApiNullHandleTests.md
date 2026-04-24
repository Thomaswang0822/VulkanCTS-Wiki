# [vktApiNullHandleTests.cpp](../../modules/vulkan/api/vktApiNullHandleTests.cpp#L1)

## Overview

Tests that destroying or freeing a `VK_NULL_HANDLE` is silently ignored by the implementation, as required by the Vulkan specification. Covers all Vulkan object types that have destroy/free functions, verifying that no host memory allocations or deallocations occur through the allocation callbacks when a null handle is passed.

## Role of File

Implementation-heavy. Uses a template-based approach with overloaded `release()` functions for each Vulkan object type, and an `AllocationCallbackRecorder` to detect any unintended memory operations.

## Source Code

- Implementation: [vktApiNullHandleTests.cpp](../../modules/vulkan/api/vktApiNullHandleTests.cpp#L1)
- Header: [vktApiNullHandleTests.hpp](../../modules/vulkan/api/vktApiNullHandleTests.hpp#L1)
- Parent registration: `createNullHandleTests()` declared at [L34](../../modules/vulkan/api/vktApiNullHandleTests.hpp#L34)

## Registration Path

```
api
  +-- null_handle
        +-- destroy_buffer
        +-- destroy_buffer_view
        +-- destroy_command_pool         (non-VKSC only)
        +-- destroy_descriptor_pool      (non-VKSC only)
        +-- destroy_descriptor_set_layout
        +-- destroy_device
        +-- destroy_event
        +-- destroy_fence
        +-- destroy_framebuffer
        +-- destroy_image
        +-- destroy_image_view
        +-- destroy_instance
        +-- destroy_pipeline
        +-- destroy_pipeline_cache
        +-- destroy_pipeline_layout
        +-- destroy_query_pool           (non-VKSC only)
        +-- destroy_render_pass
        +-- destroy_sampler
        +-- destroy_semaphore
        +-- destroy_shader_module
        +-- destroy_shader_object        (non-VKSC only)
        +-- free_command_buffers
        +-- free_descriptor_sets
        +-- free_memory                  (non-VKSC only)
```

## Test Hierarchy

```
null_handle
  +-- destroy_*           (one test per destroyable Vulkan object type)
  +-- free_*              (one test per freeable Vulkan object type)
```

## Test Families

### destroy_* (template-based)

Each test instantiates the template function `test<Object>()` which calls the corresponding `destroy*` API with `VK_NULL_HANDLE` and a null allocator. On non-VKSC builds, it also tests with a recording allocator to verify no host memory operations occur. The following object types are tested:

- `VkBuffer` at [L334](../../modules/vulkan/api/vktApiNullHandleTests.cpp#L334)
- `VkBufferView` at [L335](../../modules/vulkan/api/vktApiNullHandleTests.cpp#L335)
- `VkCommandPool` at [L338](../../modules/vulkan/api/vktApiNullHandleTests.cpp#L338) (non-VKSC)
- `VkDescriptorPool` at [L339](../../modules/vulkan/api/vktApiNullHandleTests.cpp#L339) (non-VKSC)
- `VkDescriptorSetLayout` at [L341](../../modules/vulkan/api/vktApiNullHandleTests.cpp#L341)
- `VkDevice` at [L342](../../modules/vulkan/api/vktApiNullHandleTests.cpp#L342)
- `VkEvent` at [L343](../../modules/vulkan/api/vktApiNullHandleTests.cpp#L343)
- `VkFence` at [L344](../../modules/vulkan/api/vktApiNullHandleTests.cpp#L344)
- `VkFramebuffer` at [L345](../../modules/vulkan/api/vktApiNullHandleTests.cpp#L345)
- `VkImage` at [L346](../../modules/vulkan/api/vktApiNullHandleTests.cpp#L346)
- `VkImageView` at [L347](../../modules/vulkan/api/vktApiNullHandleTests.cpp#L347)
- `VkInstance` at [L348](../../modules/vulkan/api/vktApiNullHandleTests.cpp#L348)
- `VkPipeline` at [L349](../../modules/vulkan/api/vktApiNullHandleTests.cpp#L349)
- `VkPipelineCache` at [L350](../../modules/vulkan/api/vktApiNullHandleTests.cpp#L350)
- `VkPipelineLayout` at [L351](../../modules/vulkan/api/vktApiNullHandleTests.cpp#L351)
- `VkQueryPool` at [L354](../../modules/vulkan/api/vktApiNullHandleTests.cpp#L354) (non-VKSC)
- `VkRenderPass` at [L356](../../modules/vulkan/api/vktApiNullHandleTests.cpp#L356)
- `VkSampler` at [L357](../../modules/vulkan/api/vktApiNullHandleTests.cpp#L357)
- `VkSemaphore` at [L358](../../modules/vulkan/api/vktApiNullHandleTests.cpp#L358)
- `VkShaderModule` at [L359](../../modules/vulkan/api/vktApiNullHandleTests.cpp#L359)
- `VkShaderEXT` at [L361](../../modules/vulkan/api/vktApiNullHandleTests.cpp#L361) (non-VKSC)

### free_command_buffers (VkCommandBuffer specialization)

Creates a command pool, then calls `vkFreeCommandBuffers` with an array of 3 `VK_NULL_HANDLE` entries. Verifies no allocation callback activity occurs.

- Template specialization at [L216](../../modules/vulkan/api/vktApiNullHandleTests.cpp#L216)

### free_descriptor_sets (VkDescriptorSet specialization)

Creates a descriptor pool with `VK_DESCRIPTOR_POOL_CREATE_FREE_DESCRIPTOR_SET_BIT`, then calls `vkFreeDescriptorSets` with an array of 3 `VK_NULL_HANDLE` entries. Verifies no allocation callback activity occurs.

- Template specialization at [L274](../../modules/vulkan/api/vktApiNullHandleTests.cpp#L274)

### free_memory (non-VKSC only)

Calls `vkFreeMemory` with `VK_NULL_HANDLE`. Verifies no allocation callback activity occurs.

- At [L367](../../modules/vulkan/api/vktApiNullHandleTests.cpp#L367)

## Parameter Dimensions

| Dimension | Observed Values | Notes |
|-----------|----------------|-------|
| Null handle count | 3 | For free_command_buffers and free_descriptor_sets at [L229](../../modules/vulkan/api/vktApiNullHandleTests.cpp#L229) and [L294](../../modules/vulkan/api/vktApiNullHandleTests.cpp#L294) |
| Allocator variants | nullptr, recordingAllocator | Tests both default and custom allocators at [L205](../../modules/vulkan/api/vktApiNullHandleTests.cpp#L205) |

## Support / Feature Requirements

| Requirement | Gate | Location |
|-------------|------|----------|
| VK_EXT_shader_object | Required for `destroy_shader_object` test | [L258](../../modules/vulkan/api/vktApiNullHandleTests.cpp#L258) |
| VK_KHR_portability_subset (events feature) | Checked for `destroy_event`; throws NotSupportedError if events not supported | [L324](../../modules/vulkan/api/vktApiNullHandleTests.cpp#L324) |
| recycleDescriptorSetMemory (VKSC) | Checked for `free_descriptor_sets` on VKSC | [L266](../../modules/vulkan/api/vktApiNullHandleTests.cpp#L266) |

## Verification Methods

- **No allocation activity**: `recordingAllocator.getNumRecords() == 0` after destroying/freeing null handle at [L209](../../modules/vulkan/api/vktApiNullHandleTests.cpp#L209)
- **No allocation delta**: `numInitialRecords == recordingAllocator.getNumRecords()` for free_command_buffers and free_descriptor_sets at [L249](../../modules/vulkan/api/vktApiNullHandleTests.cpp#L249) and [L314](../../modules/vulkan/api/vktApiNullHandleTests.cpp#L314)
- **Silent success**: On VKSC, the test simply returns pass since allocation callbacks must be NULL at [L211](../../modules/vulkan/api/vktApiNullHandleTests.cpp#L211)

## Test Principles Observed

- **Spec compliance**: Vulkan spec requires that destroying a null handle must be silently ignored
- **No side effects**: Allocation callback recording ensures no host memory operations occur
- **Complete coverage**: All destroyable/freeable object types are tested

## Notes / Uncertainties

- On VKSC builds, several tests are omitted because the corresponding destroy/free functions do not exist in the Vulkan SC spec: `destroy_command_pool`, `destroy_descriptor_pool`, `destroy_query_pool`, `destroy_shader_object`, and `free_memory`.
- The `destroy_device` test at [L342](../../modules/vulkan/api/vktApiNullHandleTests.cpp#L342) calls `vkDestroyDevice` with a null handle, which could be dangerous if the implementation does not properly handle it, but the spec guarantees it must be silently ignored.
- The `destroy_instance` test at [L348](../../modules/vulkan/api/vktApiNullHandleTests.cpp#L348) uses the instance interface (not device interface) for the destroy call.
