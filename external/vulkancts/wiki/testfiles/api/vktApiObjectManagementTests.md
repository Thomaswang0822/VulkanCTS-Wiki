# [vktApiObjectManagementTests.cpp](../../../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L1)

## Overview

[`vktApiObjectManagementTests.cpp`](../../../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L1) implements the `api/object_management` subgroup registered by [`createApiTests()`](../../../../../modules/vulkan/api/vktApiTests.cpp#L101). The file is very large and systematically tests creation and destruction of every major Vulkan object type under various resource-sharing and threading models: single creation, multiple creation with unique resources, multiple creation with shared resources, maximum concurrent objects, multithreaded creation with per-thread device/resources/shared resources, allocation callback tests, and private data tests.

## Role of File

Implementation-heavy test file for the `api/object_management` subgroup.

## Source Code

- Primary source: [vktApiObjectManagementTests.cpp](../../../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L1)
- Header: [vktApiObjectManagementTests.hpp](../../../../../modules/vulkan/api/vktApiObjectManagementTests.hpp#L1)
- Parent-category registration: [`createApiTests()`](../../../../../modules/vulkan/api/vktApiTests.cpp#L101)

## Registration Path

```text
TestPackage::init / TestPackageSC::init
  api
  +-- createApiTests(apiTests)
      +-- createObjectManagementTests(testCtx)
          +-- object_management
              +-- single/
              +-- multiple_unique_resources/
              +-- multiple_shared_resources/
              +-- max_concurrent/  (not in Vulkan SC)
              +-- multithreaded_per_thread_device/
              +-- multithreaded_per_thread_resources/
              +-- multithreaded_shared_resources/
              +-- single_alloc_callbacks/  (not in Vulkan SC)
              +-- alloc_callback_fail/  (not in Vulkan SC)
              +-- alloc_callback_fail_multiple/  (not in Vulkan SC)
              +-- private_data/  (not in Vulkan SC)
```

Evidence:
- `object_management` group created at [`createObjectManagementTests()`](../../../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3597)
- subgroups added from [`vktApiObjectManagementTests.cpp`](../../../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3763) through [`vktApiObjectManagementTests.cpp`](../../../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L4120)

## Test Hierarchy

```text
api
+-- object_management
    +-- single/
        +-- instance
        +-- device
        +-- device_group
        +-- device_memory_small
        +-- buffer_uniform_small
        +-- buffer_uniform_large
        +-- buffer_storage_small
        +-- buffer_storage_large
        +-- buffer_view_uniform_r8g8b8a8_unorm
        +-- buffer_view_storage_r8g8b8a8_unorm
        +-- image_1d, image_2d, image_3d
        +-- image_view_1d, image_view_1d_arr, image_view_2d, ...
        +-- semaphore
        +-- event
        +-- fence, fence_signaled
        +-- query_pool
        +-- shader_module
        +-- pipeline_cache
        +-- merged_pipeline_cache, merged_pipeline_cache_src_sync, ...
        +-- pipeline_layout_empty, pipeline_layout_single
        +-- render_pass
        +-- graphics_pipeline
        +-- compute_pipeline
        +-- descriptor_set_layout_empty, descriptor_set_layout_single
        +-- sampler
        +-- descriptor_pool, descriptor_pool_free_descriptor_set
        +-- descriptor_set
        +-- framebuffer
        +-- command_pool, command_pool_transient
        +-- command_buffer_primary, command_buffer_secondary
    +-- multiple_unique_resources/
        +-- (same object types as single/)
    +-- multiple_shared_resources/
        +-- (same object types as single/)
    +-- max_concurrent/  (excluded for Vulkan SC)
        +-- (same object types as single/)
    +-- multithreaded_per_thread_device/
        +-- (same object types, minus Instance/Device/DeviceGroup)
    +-- multithreaded_per_thread_resources/
        +-- (same object types)
    +-- multithreaded_shared_resources/
        +-- (same object types, some EMPTY_CASE_DESC)
    +-- single_alloc_callbacks/  (excluded for Vulkan SC)
        +-- (same object types as single/)
    +-- alloc_callback_fail/  (excluded for Vulkan SC)
        +-- (same object types, some EMPTY_CASE_DESC)
    +-- alloc_callback_fail_multiple/  (excluded for Vulkan SC)
        +-- (only GraphicsPipeline, ComputePipeline, DescriptorSet, CommandBuffer)
    +-- private_data/  (excluded for Vulkan SC)
        +-- (same object types minus Instance/Device/DeviceGroup/MergedPipelineCache)
```

Source: [`createObjectManagementTests()`](../../../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3595).

## Test Families

### 1. Single object creation

The `single` subgroup at [`vktApiObjectManagementTests.cpp`](../../../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3763) tests creating one instance of each Vulkan object type. Object types include Instance, Device, DeviceGroup, DeviceMemory, Buffer (4 variants), BufferView (2 variants), Image (1D/2D/3D), ImageView (7 variants), Semaphore, Event, Fence (2 variants), QueryPool, ShaderModule, PipelineCache, MergedPipelineCache (4 variants), PipelineLayout, RenderPass, GraphicsPipeline, ComputePipeline, DescriptorSetLayout, Sampler, DescriptorPool, DescriptorSet, Framebuffer, CommandPool, and CommandBuffer. Case definitions at [`vktApiObjectManagementTests.cpp`](../../../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3634).

### 2. Multiple objects with unique resources

The `multiple_unique_resources` subgroup at [`vktApiObjectManagementTests.cpp`](../../../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3800) creates multiple instances of each object type where each instance has its own independent resources. Device and DeviceGroup cases are excluded for Vulkan SC.

### 3. Multiple objects with shared resources

The `multiple_shared_resources` subgroup at [`vktApiObjectManagementTests.cpp`](../../../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3837) creates multiple instances sharing common resources. Device and DeviceGroup cases are excluded for Vulkan SC.

### 4. Maximum concurrent live objects

The `max_concurrent` subgroup at [`vktApiObjectManagementTests.cpp`](../../../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3871) tests creating the maximum number of concurrently live objects. Entirely excluded for Vulkan SC because `VkAllocationCallbacks` is not supported.

### 5. Multithreaded object construction

Three multithreaded subgroups exercise concurrent object creation:
- `multithreaded_per_thread_device` at [`vktApiObjectManagementTests.cpp`](../../../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3906): each thread uses its own device
- `multithreaded_per_thread_resources` at [`vktApiObjectManagementTests.cpp`](../../../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3940): each thread uses its own resources
- `multithreaded_shared_resources` at [`vktApiObjectManagementTests.cpp`](../../../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3978): threads share resources

### 6. Allocation callback tests

Three allocation-callback subgroups (all excluded for Vulkan SC):
- `single_alloc_callbacks` at [`vktApiObjectManagementTests.cpp`](../../../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L4013): single object creation with custom allocation callbacks
- `alloc_callback_fail` at [`vktApiObjectManagementTests.cpp`](../../../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L4049): tests behavior when allocation callbacks fail
- `alloc_callback_fail_multiple` at [`vktApiObjectManagementTests.cpp`](../../../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L4085): allocation callback failure for bulk object creation

### 7. Private data tests

The `private_data` subgroup at [`vktApiObjectManagementTests.cpp`](../../../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L4120) tests `VK_EXT_private_data` functionality for each object type. Excluded for Vulkan SC.

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Object types | Instance, Device, DeviceGroup, DeviceMemory, Buffer, BufferView, Image, ImageView, Semaphore, Event, Fence, QueryPool, ShaderModule, PipelineCache, MergedPipelineCache, PipelineLayout, RenderPass, GraphicsPipeline, ComputePipeline, DescriptorSetLayout, Sampler, DescriptorPool, DescriptorSet, Framebuffer, CommandPool, CommandBuffer at [`vktApiObjectManagementTests.cpp`](../../../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3634) |
| Buffer variants | uniform_small, uniform_large, storage_small, storage_large at [`vktApiObjectManagementTests.cpp`](../../../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3649) |
| Image variants | 1D, 2D, 3D at [`vktApiObjectManagementTests.cpp`](../../../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3675) |
| ImageView variants | 1D, 1D_array, 2D, 2D_array, Cube, Cube_array, 3D at [`vktApiObjectManagementTests.cpp`](../../../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3680) |
| Resource sharing model | single, multiple_unique_resources, multiple_shared_resources, max_concurrent at [`vktApiObjectManagementTests.cpp`](../../../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3763) |
| Threading model | per_thread_device, per_thread_resources, shared_resources at [`vktApiObjectManagementTests.cpp`](../../../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3906) |
| Allocation callback mode | single_alloc_callbacks, alloc_callback_fail, alloc_callback_fail_multiple at [`vktApiObjectManagementTests.cpp`](../../../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L4013) |

## Support / Feature Requirements

- ImageView cases require image cube array support via `checkImageCubeArraySupport` at [`vktApiObjectManagementTests.cpp`](../../../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3742)
- Event cases require event support via `checkEventSupport` at [`vktApiObjectManagementTests.cpp`](../../../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3744)
- MergedPipelineCache cases require pipeline cache control support via `checkPipelineCacheControlSupport` at [`vktApiObjectManagementTests.cpp`](../../../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3749)
- Device cases require `VK_EXT_vertex_attribute_divisor` or similar via `checkGetPhysicalDevicePropertiesExtension` at [`vktApiObjectManagementTests.cpp`](../../../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3736)
- Private data tests require `VK_EXT_private_data` (excluded for Vulkan SC)
- Allocation callback tests excluded for Vulkan SC because `VkAllocationCallbacks` is not supported

## Verification Methods

- single/multiple creation tests verify that objects are created and destroyed successfully
- multithreaded tests verify that concurrent creation does not cause crashes or data races
- allocation callback failure tests verify that the implementation handles allocation failures gracefully
- private data tests verify that private data can be associated with and retrieved from objects

## Test Principles Observed

- Systematic coverage of every major Vulkan object type
- Multiple resource-sharing and threading models exercise different usage patterns
- Allocation callback failure tests probe robustness under memory pressure
- Vulkan SC exclusions are clearly documented in comments

## Notes / Uncertainties

- The file is very large (over 4100 lines); only the registration function and parameter definitions were fully inspected. The individual test class implementations were not read in detail.
- Some object types are marked `EMPTY_CASE_DESC` in certain subgroups (e.g., Instance in shared-resources groups), meaning no test is generated for that combination.
- The exact support check implementations for `checkEventSupport`, `checkImageCubeArraySupport`, `checkPipelineCacheControlSupport`, and `checkGetPhysicalDevicePropertiesExtension` were not inspected.
