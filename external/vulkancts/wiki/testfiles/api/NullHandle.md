## Overview

**Core question:** does the implementation silently ignore a destroy or free call made with `VK_NULL_HANDLE`, without performing any host-side allocation or deallocation?

The `null_handle` test family is implemented in [vktApiNullHandleTests.cpp](../../../modules/vulkan/api/vktApiNullHandleTests.cpp#L1) and registered as the `api.null_handle` test family inside the `api` test category.

- The family registers 24 direct test case leaves, one per Vulkan object type that exposes a destroy or free entry point.
- Each test case calls the object's destroy or free function with `VK_NULL_HANDLE` and verifies the implementation silently ignores the call.
- On non-VulkanSC builds, the test records allocator callbacks to confirm the call performs no allocation or deallocation.
- On VulkanSC builds, the test verifies only that the call does not crash.

## Background Knowledge

No additional prerequisite concepts are needed for this page.

## Registration Hierarchy

```text
api.null_handle
├── destroy_buffer
├── destroy_buffer_view
├── destroy_command_pool (non-VulkanSC only)
├── destroy_descriptor_pool (non-VulkanSC only)
├── destroy_descriptor_set_layout
├── destroy_device
├── destroy_event
├── destroy_fence
├── destroy_framebuffer
├── destroy_image
├── destroy_image_view
├── destroy_instance
├── destroy_pipeline
├── destroy_pipeline_cache
├── destroy_pipeline_layout
├── destroy_query_pool (non-VulkanSC only)
├── destroy_render_pass
├── destroy_sampler
├── destroy_semaphore
├── destroy_shader_module
├── destroy_shader_object (non-VulkanSC only)
├── free_command_buffers
├── free_descriptor_sets
└── free_memory (non-VulkanSC only)
```

The `null_handle` test family is created by [createNullHandleTests()](../../../modules/vulkan/api/vktApiNullHandleTests.cpp#L373) and attached to the `api` test category in [vktApiTests.cpp](../../../modules/vulkan/api/vktApiTests.cpp#L113). All 24 direct children are added by [addTestsToGroup()](../../../modules/vulkan/api/vktApiNullHandleTests.cpp#L332). The five children marked `non-VulkanSC only` correspond to entry points that Vulkan SC removes, so their registration is guarded by `#ifndef CTS_USES_VULKANSC`.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Object type | `VkBuffer`, `VkBufferView`, `VkCommandPool`, `VkDescriptorPool`, `VkDescriptorSetLayout`, `VkDevice`, `VkEvent`, `VkFence`, `VkFramebuffer`, `VkImage`, `VkImageView`, `VkInstance`, `VkPipeline`, `VkPipelineCache`, `VkPipelineLayout`, `VkQueryPool`, `VkRenderPass`, `VkSampler`, `VkSemaphore`, `VkShaderModule`, `VkShaderEXT`, `VkCommandBuffer`, `VkDescriptorSet`, `VkDeviceMemory` | Each value selects a different Vulkan destroy or free entry point and exercises its null-handle behavior independently. | [release() overloads](../../../modules/vulkan/api/vktApiNullHandleTests.cpp#L42-L183) |
| Allocator | `nullptr`, recording allocator (non-VulkanSC only) | The first call uses a null allocator to exercise the spec-required silent-ignore path. On non-VulkanSC builds, the second call passes a recording allocator so the test can detect any host allocation or deallocation triggered by the destroy/free of `VK_NULL_HANDLE`. | [test<Object>()](../../../modules/vulkan/api/vktApiNullHandleTests.cpp#L194-L213) |
| Handle multiplicity | single handle, array of three handles | Single-handle destroy/free cases pass `VK_NULL_HANDLE` directly. `free_command_buffers` and `free_descriptor_sets` pass an array of three `VK_NULL_HANDLE` values, matching the array form of `vkFreeCommandBuffers` and `vkFreeDescriptorSets`. | [test<VkCommandBuffer>()](../../../modules/vulkan/api/vktApiNullHandleTests.cpp#L216), [test<VkDescriptorSet>()](../../../modules/vulkan/api/vktApiNullHandleTests.cpp#L274) |

## Behavior Parameters

The primary behavioral axis is the test case leaf. The 24 leaves cluster into three behavioral groups based on how the destroy/free call is constructed.

### Single-object destroy or free — `destroy_*` and `free_memory`

Each leaf in this group instantiates the generic [test<Object>()](../../../modules/vulkan/api/vktApiNullHandleTests.cpp#L194) template. The template resolves the matching [release()](../../../modules/vulkan/api/vktApiNullHandleTests.cpp#L42) overload for the object type and calls it twice on non-VulkanSC builds: once with a null allocator and once with a recording allocator. On VulkanSC, only the null-allocator call is made because Vulkan SC requires `VkAllocationCallbacks` to be `NULL`.

This group contains 22 leaves:

- `destroy_buffer`, `destroy_buffer_view`, `destroy_descriptor_set_layout`, `destroy_fence`, `destroy_framebuffer`, `destroy_image`, `destroy_image_view`, `destroy_pipeline`, `destroy_pipeline_cache`, `destroy_pipeline_layout`, `destroy_render_pass`, `destroy_sampler`, `destroy_semaphore`, and `destroy_shader_module` exercise the straightforward device-interface destroy entry point.
- `destroy_command_pool`, `destroy_descriptor_pool`, `destroy_query_pool`, and `free_memory` are non-VulkanSC only because their corresponding Vulkan SC entry points do not exist.
- `destroy_event` adds the [checkEventSupport()](../../../modules/vulkan/api/vktApiNullHandleTests.cpp#L321) gate so the case is skipped on `VK_KHR_portability_subset` implementations that report `events == VK_FALSE`.
- `destroy_shader_object` adds the [checkSupportShaderObject()](../../../modules/vulkan/api/vktApiNullHandleTests.cpp#L257) gate and is non-VulkanSC only; it requires `VK_EXT_shader_object` and destroys a `VkShaderEXT` via `vkDestroyShaderEXT`.
- `destroy_device` calls `vkDestroyDevice(VK_NULL_HANDLE, pAllocator)` through the device interface obtained from the real device. The null handle is the object being destroyed, not the device used to load the entry point.
- `destroy_instance` calls `vkDestroyInstance(VK_NULL_HANDLE, pAllocator)` through the instance interface rather than the device interface.
- `destroy_shader_module` on VulkanSC is a no-op `release()` overload that drops its arguments, because Vulkan SC has no `vkDestroyShaderModule` entry point. The case still runs but performs no destroy call on SC builds.

### Multi-handle array free — `free_command_buffers` and `free_descriptor_sets`

These two leaves use dedicated specializations of the test template because their entry points take an array of handles rather than a single handle.

- `free_command_buffers` is implemented by [test<VkCommandBuffer>()](../../../modules/vulkan/api/vktApiNullHandleTests.cpp#L216). The case creates a real `VkCommandPool` and then calls `vkFreeCommandBuffers` with an array of three `VK_NULL_HANDLE` values. On non-VulkanSC builds it also uses a recording allocator for the pool creation and confirms the free call adds no new allocator records.
- `free_descriptor_sets` is implemented by [test<VkDescriptorSet>()](../../../modules/vulkan/api/vktApiNullHandleTests.cpp#L274). The case creates a real `VkDescriptorPool` with `VK_DESCRIPTOR_POOL_CREATE_FREE_DESCRIPTOR_SET_BIT` and then calls `vkFreeDescriptorSets` with an array of three `VK_NULL_HANDLE` values. The [checkSupportFreeDescriptorSets()](../../../modules/vulkan/api/vktApiNullHandleTests.cpp#L263) gate skips the case on VulkanSC implementations whose `recycleDescriptorSetMemory` property is `VK_FALSE`.

The real pool objects exist only so the array free entry point has a valid owning pool to pass alongside the null handle array. They are not the subject of the test.

## Shader Analysis

No shader is involved in this test family. Every test case is host-side API behavior, so no `### Representative Shader Walkthrough` subsection is created.

## Runtime Execution and Result Checking

Each test case runs entirely on the host.

- The case obtains the device or instance interface and, for the array-free cases, creates a real owning pool with `createCommandPool` or `createDescriptorPool`.
- It calls the destroy or free entry point with `VK_NULL_HANDLE` and a null allocator. The Vulkan contract requires the implementation to silently ignore this call.
- On non-VulkanSC builds, the case calls the same entry point a second time using an `AllocationCallbackRecorder` provided by [AllocationCallbackRecorder](../../../modules/vulkan/api/vktApiNullHandleTests.cpp#L200). For the array-free cases, the recorder wraps pool creation, and the case records the allocator count after pool creation but before the free call.
- The pass condition is computed by [reportStatus()](../../../modules/vulkan/api/vktApiNullHandleTests.cpp#L185-L191):
  - on non-VulkanSC, the case returns pass when `recordingAllocator.getNumRecords()` is unchanged by the destroy/free call, and fail with `"Implementation allocated/freed the memory"` otherwise;
  - on VulkanSC, the case returns pass unconditionally as long as the call did not crash.

The check is per-case. Results are not aggregated across object types; each leaf reports its own pass or fail status.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| Any single-object `destroy_*` leaf or `free_memory` | Crash, validation error, or visible allocator activity when destroying or freeing `VK_NULL_HANDLE`. |
| `destroy_event` | Same as above, plus portability-subset implementations that fail to gate event support correctly. |
| `destroy_shader_object` | Same as the single-object case, but only on implementations advertising `VK_EXT_shader_object`. |
| `destroy_device` or `destroy_instance` | Crash or error caused by mishandling a null handle as the destroyed object rather than as the device or instance used to load the entry point. |
| `free_command_buffers` or `free_descriptor_sets` | Crash, validation error, or visible allocator activity when freeing an array that contains only `VK_NULL_HANDLE` values. |
| Any VulkanSC-only skipped leaf (`destroy_command_pool`, `destroy_descriptor_pool`, `destroy_query_pool`, `destroy_shader_object`, `free_memory`) | Not applicable on VulkanSC; these leaves are pruned at registration time. |

### Cause Analysis

#### Null-handle destroy or free is not silently ignored

**Possible failure symptoms:** the implementation crashes, returns a `VkResult` error, triggers the validation layer, or (on non-VulkanSC builds) causes `AllocationCallbackRecorder` to record one or more allocator callbacks during the destroy or free call. The CTS case then returns `fail` with the message `"Implementation allocated/freed the memory"` for the recorder path, or the test process crashes before reaching `reportStatus()`.

**Possible implementation causes:** the driver's destroy or free entry point fails to test the incoming handle against `VK_NULL_HANDLE` before dereferencing internal state, or it routes null handles through an allocation path that allocates and immediately frees a small bookkeeping object. Both behaviors violate the Vulkan contract that destroying or freeing `VK_NULL_HANDLE` is silently ignored.

#### Special-interface null-handle destroy (`destroy_device`, `destroy_instance`)

**Possible failure symptoms:** the case crashes or returns an error specifically on `destroy_device` or `destroy_instance` while the other single-object leaves pass.

**Possible implementation causes:** the implementation conflates the device or instance used to load the entry point with the device or instance being destroyed. The CTS case passes `VK_NULL_HANDLE` as the destroyed object and a real handle as the dispatching object, so a driver that reads the wrong argument and tries to dereference it as a valid object will fail. Distinguishing this cause requires source-level investigation of the implementation's destroy-device and destroy-instance entry points.

#### Array free with null handles (`free_command_buffers`, `free_descriptor_sets`)

**Possible failure symptoms:** the case crashes, returns a `VkResult` error from `vkFreeCommandBuffers` or `vkFreeDescriptorSets`, or (on non-VulkanSC builds) records allocator callbacks during the free call.

**Possible implementation causes:** the free entry point iterates the handle array and dereferences each entry without checking for `VK_NULL_HANDLE`, or it allocates temporary tracking state per array element. Both violate the Vulkan contract that null handles in the array are silently ignored.

#### SC-specific feature gates (`destroy_event`, `free_descriptor_sets`)

**Possible failure symptoms:** the case throws `NotSupportedError` instead of returning a pass or fail status. This is not a test failure; it is the support gate skipping the case.

**Possible implementation causes:** the implementation advertises `VK_KHR_portability_subset` with `events == VK_FALSE`, or (on VulkanSC) reports `recycleDescriptorSetMemory == VK_FALSE`. These are correct skip outcomes, not failures. If an implementation reports support but cannot actually destroy or free a null handle, the failure surfaces under one of the causes above rather than here.

## Case Pruning

### Requirement-based pruning

- Five leaves (`destroy_command_pool`, `destroy_descriptor_pool`, `destroy_query_pool`, `destroy_shader_object`, and `free_memory`) are registered only on non-VulkanSC builds because the corresponding Vulkan SC entry points do not exist. The pruning happens at registration time via `#ifndef CTS_USES_VULKANSC` guards in [addTestsToGroup()](../../../modules/vulkan/api/vktApiNullHandleTests.cpp#L332-L369).
- `destroy_event` is skipped at runtime on `VK_KHR_portability_subset` implementations that report `events == VK_FALSE`.
- `destroy_shader_object` is skipped at runtime when `VK_EXT_shader_object` is not supported.
- `free_descriptor_sets` is skipped at runtime on VulkanSC implementations whose `recycleDescriptorSetMemory` property is `VK_FALSE`.

### Design-based pruning

- The family does not generate combinations of object type and allocator. Each leaf exercises exactly two allocator configurations on non-VulkanSC builds (null allocator and recording allocator) and a single null-allocator call on VulkanSC. This fixed shape matches the spec contract being tested and avoids generating redundant cases.
- The family does not vary the array length for `free_command_buffers` or `free_descriptor_sets`. A single array of three `VK_NULL_HANDLE` values is enough to exercise the array path; expanding the dimension would not change what the test proves.

## Key Takeaways

- Every leaf in the family verifies the same Vulkan contract: destroying or freeing `VK_NULL_HANDLE` must be silently ignored.
- On non-VulkanSC builds, the silent-ignore contract is reinforced by an allocator-recording check that fails if the implementation allocates or frees any memory during the call. See `## Failure Meaning` for the failure analysis behind this.
- The 24 leaves exist to cover every Vulkan destroy or free entry point individually, so a regression in one entry point's null-handle path is reported by name rather than masked by an aggregate result.
- Five leaves are pruned on VulkanSC because Vulkan SC removes the corresponding entry points; the remaining leaves run on VulkanSC but use the simpler crash-only verification path.
- A separate cause analysis covers `destroy_device` and `destroy_instance` because they are the only leaves where the dispatching interface and the destroyed object are different handles.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `createNullHandleTests()` | [vktApiNullHandleTests.cpp#L373](../../../modules/vulkan/api/vktApiNullHandleTests.cpp#L373) | Creates the `null_handle` test family and wires it into the `api` test category. |
| `addTestsToGroup()` | [vktApiNullHandleTests.cpp#L332-L369](../../../modules/vulkan/api/vktApiNullHandleTests.cpp#L332-L369) | Registers all 24 test case leaves, including the VulkanSC guards and feature gates. |
| `test<Object>()` template | [vktApiNullHandleTests.cpp#L194-L213](../../../modules/vulkan/api/vktApiNullHandleTests.cpp#L194-L213) | Generic single-object destroy/free test logic, used by 22 leaves. |
| `test<VkCommandBuffer>()` specialization | [vktApiNullHandleTests.cpp#L216-L254](../../../modules/vulkan/api/vktApiNullHandleTests.cpp#L216-L254) | Array-free path for `free_command_buffers`. |
| `test<VkDescriptorSet>()` specialization | [vktApiNullHandleTests.cpp#L274-L319](../../../modules/vulkan/api/vktApiNullHandleTests.cpp#L274-L319) | Array-free path for `free_descriptor_sets`. |
| `release()` overloads | [vktApiNullHandleTests.cpp#L42-L183](../../../modules/vulkan/api/vktApiNullHandleTests.cpp#L42-L183) | Per-object-type destroy or free entry point dispatch, including the VulkanSC no-op overload for `VkShaderModule`. |
| `reportStatus()` | [vktApiNullHandleTests.cpp#L185-L191](../../../modules/vulkan/api/vktApiNullHandleTests.cpp#L185-L191) | Final pass or fail decision based on allocator-record count. |
| `checkEventSupport()` | [vktApiNullHandleTests.cpp#L321-L330](../../../modules/vulkan/api/vktApiNullHandleTests.cpp#L321-L330) | Portability-subset event support gate for `destroy_event`. |
| `checkSupportShaderObject()` | [vktApiNullHandleTests.cpp#L257-L261](../../../modules/vulkan/api/vktApiNullHandleTests.cpp#L257-L261) | `VK_EXT_shader_object` gate for `destroy_shader_object`. |
| `checkSupportFreeDescriptorSets()` | [vktApiNullHandleTests.cpp#L263-L271](../../../modules/vulkan/api/vktApiNullHandleTests.cpp#L263-L271) | VulkanSC `recycleDescriptorSetMemory` gate for `free_descriptor_sets`. |
| Parent registration | [vktApiTests.cpp#L113](../../../modules/vulkan/api/vktApiTests.cpp#L113) | Attaches `createNullHandleTests()` to the `api` test category. |
| Header | [vktApiNullHandleTests.hpp](../../../modules/vulkan/api/vktApiNullHandleTests.hpp#L1) | Declares `createNullHandleTests()`. |
