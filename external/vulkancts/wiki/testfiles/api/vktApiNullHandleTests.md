# [vktApiNullHandleTests.cpp](../../../../../modules/vulkan/api/vktApiNullHandleTests.cpp#L1)

## Overview

Tests that destroying or freeing a VK_NULL_HANDLE is silently ignored by the implementation, as required by the Vulkan specification. Covers all Vulkan object types that have destroy/free functions.

## Role of File

Implementation-heavy. Contains all test logic and the registration function [createNullHandleTests()](../../../../../modules/vulkan/api/vktApiNullHandleTests.cpp#L373).

## Source Code

- Implementation: [vktApiNullHandleTests.cpp](../../../../../modules/vulkan/api/vktApiNullHandleTests.cpp#L1)
- Header: [vktApiNullHandleTests.hpp](../../../../../modules/vulkan/api/vktApiNullHandleTests.hpp#L1)
- Parent registration: [vktApiTests.cpp](../../../../../modules/vulkan/api/vktApiTests.cpp#L113)

## Registration Path

```
api
  +-- null_handle
```

## Test Hierarchy

```
null_handle
  +-- destroy_buffer
  +-- destroy_buffer_view
  +-- destroy_command_pool              [non-SC]
  +-- destroy_descriptor_pool           [non-SC]
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
  +-- destroy_query_pool               [non-SC]
  +-- destroy_render_pass
  +-- destroy_sampler
  +-- destroy_semaphore
  +-- destroy_shader_module
  +-- destroy_shader_object             [non-SC]
  +-- free_command_buffers
  +-- free_descriptor_sets
  +-- free_memory                       [non-SC]
```

## Test Families

### Destroy Object with Null Handle

The template function [test<Object>()](../../../../../modules/vulkan/api/vktApiNullHandleTests.cpp#L194) calls the appropriate destroy function with VK_NULL_HANDLE and a null allocator. On non-SC, it also tests with a recording allocator to verify that no memory allocation or deallocation occurs.

### Free Command Buffers with Null Handle

[test<VkCommandBuffer>()](../../../../../modules/vulkan/api/vktApiNullHandleTests.cpp#L216) creates a command pool and calls vkFreeCommandBuffers with an array of VK_NULL_HANDLE values. Verifies that the call is silently ignored.

### Free Descriptor Sets with Null Handle

[test<VkDescriptorSet>()](../../../../../modules/vulkan/api/vktApiNullHandleTests.cpp#L274) creates a descriptor pool and calls vkFreeDescriptorSets with an array of VK_NULL_HANDLE values. Verifies that the call is silently ignored.

### Allocation Callback Verification

On non-SC builds, tests use [AllocationCallbackRecorder](../../../../../modules/vulkan/api/vktApiNullHandleTests.cpp#L200) to verify that destroying a null handle does not trigger any allocation or deallocation callbacks. The test passes only if the number of recorded callbacks remains at zero.

## Parameter Dimensions

| Dimension | Observed Values |
|---|---|
| Object type | VkBuffer, VkBufferView, VkCommandPool, VkDescriptorPool, VkDescriptorSetLayout, VkDevice, VkEvent, VkFence, VkFramebuffer, VkImage, VkImageView, VkInstance, VkPipeline, VkPipelineCache, VkPipelineLayout, VkQueryPool, VkRenderPass, VkSampler, VkSemaphore, VkShaderModule, VkShaderEXT, VkCommandBuffer, VkDescriptorSet, VkDeviceMemory |
| Allocator | nullptr, recording allocator (non-SC) |

## Support / Feature Requirements

| Feature / Extension | Used By |
|---|---|
| VK_EXT_shader_object | destroy_shader_object |
| VK_KHR_portability_subset | destroy_event (events may not be supported) |
| VulkanSC recycleDescriptorSetMemory | free_descriptor_sets on SC |

## Verification Methods

- **No observable side effects**: On non-SC, [AllocationCallbackRecorder](../../../../../modules/vulkan/api/vktApiNullHandleTests.cpp#L200) verifies that no allocation callbacks are triggered
- **Silent success**: On SC, the test simply verifies that the destroy/free call does not crash
- **reportStatus()**: [reportStatus()](../../../../../modules/vulkan/api/vktApiNullHandleTests.cpp#L186) returns pass if no allocation occurred, fail otherwise

## Test Principles Observed

- Spec compliance: the Vulkan spec requires that destroying VK_NULL_HANDLE is silently ignored
- No allocation verification: destroying a null handle must not allocate or free memory
- Object type coverage: all destroyable/freeable Vulkan object types are tested
- SC divergence: some object types (VkCommandPool, VkDescriptorPool, VkQueryPool, VkDeviceMemory) are not tested on SC because their destroy/free functions do not exist in Vulkan SC

## Notes / Uncertainties

- The test for VkDevice destroys VK_NULL_HANDLE via vkDestroyDevice, which is a special case since the device is the object being used to make the call
- The test for VkInstance destroys VK_NULL_HANDLE via the instance interface, not the device interface
- VkCommandBuffer and VkDescriptorSet use vkFreeCommandBuffers and vkFreeDescriptorSets respectively, which take arrays of handles
