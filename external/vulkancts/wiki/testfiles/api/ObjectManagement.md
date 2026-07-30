## Overview

**Core question:** Can the implementation create and destroy every major Vulkan object type under plain sequential use, shared and unique resource dependencies, peak concurrency, multithreaded contention, custom allocator validation, deterministic allocation failure, and `VK_EXT_private_data` storage?

- [`vktApiObjectManagementTests.cpp`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp) is the sole implementation file for the `api.object_management` test family. It is registered into the `api` test category by [`createApiTests`](../../../modules/vulkan/api/vktApiTests.cpp#L101) through [`createObjectManagementTests`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3601-L4130).
- The family fans out into 11 intermediate nodes that each select a different create/destroy mechanism: `single`, `multiple_unique_resources`, `multiple_shared_resources`, `max_concurrent`, `multithreaded_per_thread_device`, `multithreaded_per_thread_resources`, `multithreaded_shared_resources`, `single_alloc_callbacks`, `alloc_callback_fail`, `alloc_callback_fail_multiple`, and `private_data`.
- Each intermediate node walks the same list of object types (`Instance`, `Device`, `DeviceGroup`, `DeviceMemory`, `Buffer`, `BufferView`, `Image`, `ImageView`, `Semaphore`, `Event`, `Fence`, `QueryPool`, `ShaderModule`, `PipelineCache`, `MergedPipelineCache`, `PipelineLayout`, `RenderPass`, `GraphicsPipeline`, `ComputePipeline`, `DescriptorSetLayout`, `Sampler`, `DescriptorPool`, `DescriptorSet`, `Framebuffer`, `CommandPool`, `CommandBuffer`) and emits one test case leaf per object variant.
- The core test idea is that the host drives the full `vkCreate*`/`vkDestroy*` lifecycle of one or many handles against a real dependency chain and observes whether the calls return `VK_SUCCESS`, whether allocation callbacks stay clean, and whether private data values round-trip.

## Background Knowledge

- **Vulkan object lifetime and parent-child ownership.** Vulkan objects are created by `vkCreate*` calls that return a handle and destroyed by matching `vkDestroy*` calls. The spec requires every child object to be destroyed before its parent. CTS models this with `Unique<VkType>` destructors that tear the dependency chain down in reverse order, so a failure in any leaf can point to either the object under test or one of its parents.
- **`VkAllocationCallbacks` and allocation scopes.** When `VkAllocationCallbacks` is supplied, every host-side allocation the implementation makes for a create/destroy call flows through the application's `pfnAllocation`/`pfnReallocation`/`pfnFree`. Each allocation is tagged with a `VkSystemAllocationScope` (`INSTANCE`, `DEVICE`, `CACHE`, `OBJECT`, or `COMMAND`) describing its expected lifetime. The contract verified here is that `COMMAND`-scope allocations do not outlive the constructing call, and that every allocation is freed once the owning object is destroyed.
- **Thread safety of object creation.** Vulkan commands are externally synchronized only where the spec explicitly says so; otherwise the implementation must serialize internally. For the majority of `vkCreate*`/`vkDestroy*` calls, concurrent calls from multiple threads on the same `VkDevice` are required to be safe. The multithreaded intermediate nodes exploit this by running barrier-synchronized `CreateThread<Object>` workers that repeatedly construct and destroy the same object.
- **`VK_EXT_private_data` per-object storage.** `VK_EXT_private_data` adds `VkPrivateDataSlotEXT`, `vkSetPrivateDataEXT`, and `vkGetPrivateDataEXT`. Each slot is a key, and each (object, slot) pair stores one `uint64_t`. The contract verified here is that the initial value for any (object, slot) pair is zero, that `vkSetPrivateDataEXT` overwrites the value, and that `vkGetPrivateDataEXT` reads back exactly what was last set.

## Registration Hierarchy

```text
api.object_management
├── single
├── multiple_unique_resources
├── multiple_shared_resources
├── max_concurrent (not in Vulkan SC)
├── multithreaded_per_thread_device
├── multithreaded_per_thread_resources
├── multithreaded_shared_resources
├── single_alloc_callbacks (not in Vulkan SC)
├── alloc_callback_fail (not in Vulkan SC)
├── alloc_callback_fail_multiple (not in Vulkan SC)
└── private_data (not in Vulkan SC)
```

Five intermediate nodes are excluded from Vulkan SC builds because `VkAllocationCallbacks` and `VK_EXT_private_data` are not part of Vulkan SC: `max_concurrent`, `single_alloc_callbacks`, `alloc_callback_fail`, `alloc_callback_fail_multiple`, and `private_data`.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Object type | `instance`, `device`, `device_group`, `device_memory_small`, `buffer_uniform_small`, `buffer_uniform_large`, `buffer_storage_small`, `buffer_storage_large`, `buffer_view_uniform_r8g8b8a8_unorm`, `buffer_view_storage_r8g8b8a8_unorm`, `image_1d`, `image_2d`, `image_3d`, `image_view_1d`, `image_view_1d_arr`, `image_view_2d`, `image_view_2d_arr`, `image_view_cube`, `image_view_cube_arr`, `image_view_3d`, `semaphore`, `event`, `fence`, `fence_signaled`, `query_pool`, `shader_module`, `pipeline_cache`, `merged_pipeline_cache`, `merged_pipeline_cache_src_sync`, `merged_pipeline_cache_dst_sync`, `merged_pipeline_cache_src_dst_sync`, `pipeline_layout_empty`, `pipeline_layout_single`, `render_pass`, `graphics_pipeline`, `compute_pipeline`, `descriptor_set_layout_empty`, `descriptor_set_layout_single`, `sampler`, `descriptor_pool`, `descriptor_pool_free_descriptor_set`, `descriptor_set`, `framebuffer`, `command_pool`, `command_pool_transient`, `command_buffer_primary`, `command_buffer_secondary` | Selects which Vulkan object type is constructed and destroyed. Changes the dependency chain, the create call, and which feature gates apply. | [`s_*Cases` definitions](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3640-L3738) |
| Buffer variant | `uniform_small` (1024 B), `uniform_large` (16 MiB), `storage_small` (1024 B), `storage_large` (16 MiB) | Changes buffer size and usage flag for `Buffer`, `BufferView`, and downstream leaves. | [`s_bufferCases`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3655-L3672) |
| Image variant | `1d` (256×1×1), `2d` (64×64×1), `3d` (64×64×4), cube (64×64×1, 6 layers) | Changes image type, extents, and layer count. The cube variant feeds `image_view_cube` and `image_view_cube_arr`. | [`s_imageCases`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3681-L3685), [imgCube](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3612-L3615) |
| ImageView variant | `1d`, `1d_arr`, `2d`, `2d_arr`, `cube`, `cube_arr`, `3d` | Changes `VkImageViewType` and subresource layer range. The `cube_arr` variant requires the `imageCubeArray` feature. | [`s_imageViewCases`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3686-L3691) |
| Resource sharing model | `single`, `multiple_unique_resources`, `multiple_shared_resources`, `max_concurrent` | Selects how many handles are alive simultaneously and whether resource chains are shared. `max_concurrent` walks a computed peak count. | [Sequential intermediate node registrations](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3768-L3877) |
| Threading model | `per_thread_device`, `per_thread_resources`, `shared_resources` | Selects whether each thread owns its own `VkDevice`, owns its own resource chain, or shares both device and resource chain. | [Multithreaded intermediate node registrations](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3880-L3984) |
| Allocation callback mode | `single_alloc_callbacks`, `alloc_callback_fail`, `alloc_callback_fail_multiple` | Selects whether callbacks are recorded, recorded and deterministically failed, or recorded and failed in bulk creation. | [Allocation callback intermediate node registrations](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3989-L4091) |
| Private data slot count | 100 slots per device iteration, across 5 singleton devices and 3 iterations | Stress coverage for `vkSetPrivateDataEXT`/`vkGetPrivateDataEXT` across many (object, slot) pairs. | [`createPrivateDataTest`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2742-L2869) |

## Behavior Parameters

The primary behavioral axis for this page is the **intermediate node** under `api.object_management`. The object type (the test case leaf) is a secondary axis: it changes *what* is constructed but not *how* the create/destroy path is exercised. The intermediate node selects the tested mechanism: plain lifecycle, threading, allocation callback contract, allocation failure handling, or private data semantics.

### single — single create-then-destroy

Constructs one `Object::Type` handle against a real `Object::Resources` dependency chain inside an `Environment` rooted at the context's instance and device, then lets the `Unique<VkType>` destructor destroy it. The pass condition is that `Object::create` returns a valid handle and the destructor does not throw. See [`createSingleTest`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2542-L2553).

### multiple_unique_resources — four handles, four independent chains

Constructs four `Object::Resources` chains and four `Object::Type` handles, one per chain. The pass condition is that all four create calls succeed and all four destructors run cleanly. This isolates per-object ownership: a leak or state corruption in one chain must not break the next. See [`createMultipleUniqueResourcesTest`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2555-L2572).

### multiple_shared_resources — four handles, one shared chain

Constructs one `Object::Resources` chain shared by four `Object::Type` handles. The `Environment` is configured with `maxResourceConsumers = 4` so that resource sizing accounts for four concurrent users. The pass condition is that all four handles can coexist against the shared chain. See [`createMultipleSharedResourcesTest`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2591-L2605).

### max_concurrent — peak live handle count

Computes a per-object-type safe count from the platform memory limits and a measured per-object system-memory footprint, capped by constants such as `MAX_CONCURRENT_INSTANCES = 32`, `MAX_CONCURRENT_SYNC_PRIMITIVES = 100`, `MAX_CONCURRENT_PIPELINE_CACHES = 128`, `MAX_CONCURRENT_QUERY_POOLS = 8192`, and `DEFAULT_MAX_CONCURRENT_OBJECTS = 16 * 1024`. Creates that many handles simultaneously, touches the watchdog every 1024 creations, then releases all of them. The pass condition is that every create succeeds and every destructor runs cleanly. See [`createMaxConcurrentTest`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2875-L2902) and the count helpers at [`getSafeObjectCount`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L415-L467).

### multithreaded_per_thread_device — per-thread `VkDevice`

Each thread clones its own `VkDevice` via `EnvClone`, then runs a `CreateThread<Object>` worker that performs `getCreateCount<Object>()` create/destroy iterations (100 for most types, 20 for `Instance`/`Device`/`DeviceGroup`) with a barrier sync five times per loop (every `numIters/5` iterations). The pass condition is that no thread throws. `Instance`, `Device`, and `DeviceGroup` are excluded because per-thread device creation requires a shared instance and defeats the test's purpose. See [`multithreadedCreatePerThreadDeviceTest`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3079-L3110) and [`CreateThread::runThread`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2961-L2988).

### multithreaded_per_thread_resources — shared device, per-thread chains

Threads share the context `VkDevice` but each owns its own `Object::Resources` chain. The same barrier-synced create/destroy loop runs in each thread. The pass condition is that no thread throws. Unlike the per-thread-device variant, `Instance`, `Device`, and `DeviceGroup` cases are registered because they exercise the shared device directly. See [`multithreadedCreatePerThreadResourcesTest`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3016-L3038).

### multithreaded_shared_resources — shared device and chain

Threads share both the context `VkDevice` and one `Object::Resources` chain. The `Environment` is configured with `maxResourceConsumers = numThreads` so that the shared resource chain is sized for concurrent use. The pass condition is that no thread throws. `Instance` is excluded because it has no resources to share, and `DescriptorSet` and `CommandBuffer` are excluded because their pools are externally synchronized and cannot be safely shared across threads. See [`multithreadedCreateSharedResourcesTest`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2996-L3014).

### single_alloc_callbacks — recorder-validated single object

Wraps a single create/destroy in two `AllocationCallbackRecorder` instances: one for the resource chain (chained into a cloned device), one for the object under test. After construction, calls [`validateAndLog`](../../../framework/vulkan/vkAllocationCallbackUtil.hpp#L255) with `noCmdScope`, a mask allowing `INSTANCE`, `DEVICE`, `CACHE`, and `OBJECT` scope allocations to remain live. After destruction, calls `validateAndLog` with scope `0u` to require every allocation to be freed. The pass condition is that no `AllocationCallbackViolation` is recorded and no disallowed live allocation remains. See [`createSingleAllocCallbacksTest`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3112-L3165).

### alloc_callback_fail — deterministic single-object allocation failure

Iteratively wraps `Object::create` in a `DeterministicFailAllocator` that fails after `numPassingAllocs` allocations, retrying with progressively larger `numPassingAllocs` until construction succeeds. Each failed attempt must throw `vk::OutOfMemoryError` with `VK_ERROR_OUT_OF_HOST_MEMORY`, leave the recorder clean, and not throw a different error. `maxTries` is `--deqp-test-iteration-count` if set, else 40 (or 20 for `Device`/`DeviceGroup`); `finalLimit` is `max(maxTries, 10000)`. The loop terminates when construction succeeds or when `numPassingAllocs` reaches `finalLimit`; when `numPassingAllocs` reaches `maxTries` without success, the loop makes one final attempt at `finalLimit`. The pass result is `Ok` on early success, `QualityWarning` if callbacks were never called, or `Pass` with a max-iter message if `finalLimit` is reached. See [`allocCallbackFailTest`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3189-L3290).

### alloc_callback_fail_multiple — bulk creation failure and handle zeroing

Exercises `Object::createMultiple` for `GraphicsPipeline`, `ComputePipeline`, `DescriptorSet`, and `CommandBuffer`. These are the only object types with a multi-object create path. For each `numPassingAllocs` from 0 to `numObjects = 4`, fills the output handle vector with garbage, attempts bulk creation through a `DeterministicFailAllocator`, and verifies the result. On failure, [`isNullHandleOnAllocationFailure`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3294-L3317) decides whether uncreated handles must be `VK_NULL_HANDLE`: `VkPipeline` always requires it, while `VkCommandBuffer` and `VkDescriptorSet` require it only when `VK_KHR_maintenance1` is enabled. The error code must be `VK_ERROR_OUT_OF_HOST_MEMORY`, and the recorder must be clean. [`isPooledObject`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3319-L3335) returns true for `VkCommandBuffer` and `VkDescriptorSet`, which suppresses the "Allocation callbacks not called" quality warning. See [`allocCallbackFailMultipleObjectsTest`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3337-L3416).

### private_data — `VK_EXT_private_data` set/get

Uses five singleton `VkDevice`s created with different `privateDataSlotRequestCount` values (0/0, 1/0, 1/1, 4/4, 1/100, chained through two `VkDevicePrivateDataCreateInfoEXT` structs). For each device, interleaves object creation with `VkPrivateDataSlotEXT` creation, then verifies across 100 slots, 4 objects, and 3 iterations that: the initial `vkGetPrivateDataEXT` value is zero for every (object, slot) pair; `vkSetPrivateDataEXT` succeeds; and `vkGetPrivateDataEXT` reads back exactly `i*i*i + o*o + 1` for object `o` and slot `i`. The same checks run on `VkPrivateDataSlotEXT` objects themselves and on `VkDevice`. See [`createPrivateDataTest`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2720-L2873) and [`SingletonDevice`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2609-L2707).

## Shader Analysis

No shader code participates in this test. The `ShaderModule`, `GraphicsPipeline`, `ComputePipeline`, and `MergedPipelineCache` leaves do register a minimal SPIR-V program through `Object::initPrograms`, but the shader content is not part of the tested behavior; it exists only so the pipeline and shader module creation calls have a valid `VkShaderModule` to consume.

## Runtime Execution and Result Checking

- The host builds an `Environment` rooted at the context instance and device, optionally chaining an `AllocationCallbackRecorder` through a cloned `EnvClone` device. See [`Environment`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L247-L319) and [`EnvClone`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3040-L3071).
- For `single`, `multiple_unique_resources`, `multiple_shared_resources`, and `max_concurrent`, the host creates one or more `Object::Type` handles via `Object::create`, then lets the `Unique<VkType>` destructors destroy them in reverse order. The pass condition is that no `vk::Error` is thrown.
- For the multithreaded variants, the host spawns a `ThreadGroup` of `CreateThread<Object>` workers, each running `getCreateCount<Object>()` create/destroy iterations with a barrier sync five times per loop (every `numIters/5` iterations, or every iteration on Vulkan SC). `ThreadGroup::run` collects per-thread `ResultCollector` results into a single `TestStatus`. See [`ThreadGroup`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L113-L191) and [`CreateThread`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2949-L2994).
- For `single_alloc_callbacks`, the host runs two `validateAndLog` passes after construction and after destruction, with the `noCmdScope` and `0u` scope masks respectively.
- For `alloc_callback_fail`, the host runs an iterative retry loop with a `DeterministicFailAllocator`, validating the recorder after each failed attempt and breaking on success. See [`DeterministicFailAllocator`](../../../framework/vulkan/vkAllocationCallbackUtil.hpp#L184-L207).
- For `alloc_callback_fail_multiple`, the host iterates `numPassingAllocs` from 0 to 4, validates the recorder, and (when `expectNullHandles` applies) verifies that uncreated handles are `VK_NULL_HANDLE`.
- For `private_data`, the host interleaves object and slot creation, then runs three iterations of zero-check, set, and read-back across 100 slots and 4 objects, plus the same checks on slot objects and on the device itself.
- The final pass/fail condition is `tcu::TestStatus::pass("Ok")` unless any leaf-specific check returns `fail` or `QualityWarning`. There is no device-side result buffer; all checks are host-side.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `single` | Object lifecycle failure: `vkCreate*` returned an error, `vkDestroy*` returned an error, or the destructor threw. The cause is specific to the object type that failed. |
| `multiple_unique_resources` | Object lifecycle failure on one of four independent resource chains, or cross-object interference (a resource leak in one chain breaking the next). |
| `multiple_shared_resources` | Object lifecycle failure when four handles share one resource chain, or shared-resource accounting error in the implementation. |
| `max_concurrent` | Object lifecycle failure under high handle count, or the implementation enforces a lower concurrent-object limit than the platform memory budget predicts. |
| `multithreaded_per_thread_device` | Threading failure: race condition, deadlock, or crash during concurrent `vkCreate*`/`vkDestroy*` on per-thread devices. |
| `multithreaded_per_thread_resources` | Threading failure on the shared `VkDevice` when only resources are per-thread. |
| `multithreaded_shared_resources` | Threading failure when both device and resources are shared; may also indicate the implementation did not internally serialize an externally synchronized call. |
| `single_alloc_callbacks` | Allocation callback contract violation: live `COMMAND`-scope allocation after construction, live allocation of any scope after destruction, double free, free of unallocated pointer, or realloc violation. |
| `alloc_callback_fail` | Allocation failure handling violation: invalid error code (not `VK_ERROR_OUT_OF_HOST_MEMORY`), leaked allocation after a failed attempt, or `AllocationCallbackViolation`. |
| `alloc_callback_fail_multiple` | Allocation failure handling violation for pooled/bulk creation: invalid error code, leaked allocation, or uncreated handles not set to `VK_NULL_HANDLE` when `VK_KHR_maintenance1` is enabled (or for `VkPipeline`, always). |
| `private_data` | Private data set/get violation: initial value not zero, value read back did not match the value written, or `vkSetPrivateDataEXT` returned an error. |

### Cause Analysis

#### Object lifecycle failure

**Possible failure symptoms:** A `vkCreate*` call returns a `VkResult` other than `VK_SUCCESS`, the `Unique<VkType>` destructor throws, or a `vk::Error` propagates out of the test body. The failing leaf name identifies the object type and variant.

**Possible implementation causes:** The symptom can indicate that the implementation rejected a legal `createInfo`, failed to allocate or bind a required resource, or corrupted parent state during construction or destruction. The dependency chain includes parent objects (instance, device, memory, buffers, images, command pools, descriptor pools, pipeline caches) so a failure in a leaf such as `image_view_cube_arr` may originate in the parent `VkImage` or in the view itself. Source-level investigation is needed to localize the failure to a specific create or destroy call.

#### Threading failure

**Possible failure symptoms:** A multithreaded leaf fails with an unexpected `VkResult`, an exception, a crash, or a timeout. The failure may be intermittent and may not reproduce on every run.

**Possible implementation causes:** The Vulkan spec requires `vkCreate*`/`vkDestroy*` to be safe to call concurrently from multiple threads unless a specific command is documented as externally synchronized. A failure here indicates that the implementation did not internally serialize a command that should be internally synchronized, or that it shared mutable state across threads without proper locking. The shared-resources variant additionally stresses any internal resource accounting that the implementation performs on the shared `Object::Resources` chain. Source-level investigation is needed to identify which command lost the race.

#### Allocation callback contract violation

**Possible failure symptoms:** `single_alloc_callbacks` returns `fail("Invalid allocation callback")` after construction or destruction. The `AllocationCallbackRecorder` logs at least one `AllocationCallbackViolation` (double free, free of unallocated pointer, realloc violation, invalid scope, invalid alignment, or negative internal allocation total) or reports a live allocation in a scope that should already have been cleaned up.

**Possible implementation causes:** A `COMMAND`-scope allocation still live after construction means the implementation retained command-scoped host memory beyond the create call, which the spec does not permit. A live allocation of any scope after destruction means the implementation leaked host memory when the object was destroyed. A double-free or free-of-unallocated-pointer violation means the implementation mis-tracked its own allocations. These are direct spec violations; the recorder log identifies the specific allocation that caused the failure.

#### Allocation failure handling violation

**Possible failure symptoms:** `alloc_callback_fail` or `alloc_callback_fail_multiple` returns `fail("Got invalid error code")`, `fail("Invalid allocation callback")`, or `fail("Some object handles weren't set to NULL")`. The test may also return `QualityWarning` if `numPassingAllocs == 0` (callbacks were never called) for a non-pooled object type.

**Possible implementation causes:** When `pfnAllocation` returns `NULL`, the implementing `vkCreate*` call must return `VK_ERROR_OUT_OF_HOST_MEMORY` (or, for pooled objects, the documented pooled status) and must not leak partial state. A different error code, a leaked allocation recorded by the recorder, or a non-NULL uncreated handle (for `VkPipeline` always, and for `VkCommandBuffer`/`VkDescriptorSet` under `VK_KHR_maintenance1`) is a direct spec violation. The `AllocationCallbackRecorder` log identifies which allocation was not freed; the handle vector inspection identifies which handle was not zeroed.

#### Private data set/get violation

**Possible failure symptoms:** `private_data` returns `fail("Expected initial value of zero")`, `fail("Didn't read back set value")`, or `fail("Didn't read back set value from device")`. The failure may occur on the first iteration or after several iterations of slot destruction and reallocation.

**Possible implementation causes:** `VK_EXT_private_data` requires the initial value for any (object, slot) pair to be zero, `vkSetPrivateDataEXT` to overwrite the stored value, and `vkGetPrivateDataEXT` to return exactly what was last set. A non-zero initial value means the implementation did not initialize storage for the (object, slot) pair; a mismatched read-back means the implementation mis-routed the slot, mis-sized the storage, or corrupted the value. The five singleton devices stress different `privateDataSlotRequestCount` values, so a failure on only one device points to mishandling of the slot reservation chain. Source-level investigation is needed to identify whether the failure is in slot creation, set, or get.

## Case Pruning

### Requirement-based pruning

- `max_concurrent`, `single_alloc_callbacks`, `alloc_callback_fail`, `alloc_callback_fail_multiple`, and `private_data` are excluded from Vulkan SC builds because `VkAllocationCallbacks` and `VK_EXT_private_data` are not part of Vulkan SC. The `CTS_USES_VULKANSC` preprocessor guard removes them at registration time. See [Vulkan SC exclusions](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3845-L3846).
- `Device` and `DeviceGroup` cases are excluded from `multiple_unique_resources` and `multiple_shared_resources` on Vulkan SC. See the `EMPTY_CASE_DESC(Device)` and `EMPTY_CASE_DESC(DeviceGroup)` entries gated by `CTS_USES_VULKANSC`.
- `ImageView` cube-array leaves require the `imageCubeArray` feature. See [`checkImageCubeArraySupport`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3488-L3492).
- `Event` leaves require `VK_KHR_portability_subset.events` to be true when the portability subset is enabled. See [`checkEventSupport`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3499-L3508).
- `MergedPipelineCache` leaves require `VK_EXT_pipeline_creation_cache_control` and the `pipelineCreationCacheControl` feature. They are unsupported on Vulkan SC. See [`checkPipelineCacheControlSupport`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3510-L3520).
- `Device` leaves in the `single` intermediate node require `VK_KHR_get_physical_device_properties2`. See [`checkGetPhysicalDevicePropertiesExtension`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3494-L3497).
- `private_data` leaves require `VK_EXT_private_data` and the `privateData` feature. The test throws `NotSupportedError` if the feature is absent. See [`createPrivateDataTest`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2723-L2724).
- `DescriptorSet` leaves in the multithreaded variants require `recycleDescriptorSetMemory` on Vulkan SC. See [`checkRecycleDescriptorSetMemorySupport`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3522-L3532).

### Design-based pruning

- `multithreaded_per_thread_device` excludes `Instance`, `Device`, and `DeviceGroup`. The source marks them `EMPTY_CASE_DESC` with the comment "Does not make sense" because per-thread device creation requires a shared instance. See [`s_multithreadedCreatePerThreadDeviceGroup`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3880-L3909).
- `multithreaded_shared_resources` excludes `Instance` (no resources to share), `DescriptorSet`, and `CommandBuffer`. The latter two are excluded because their pools are externally synchronized and cannot be safely shared across threads. See [`s_multithreadedCreateSharedResourcesGroup`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3948-L3981).
- `alloc_callback_fail` excludes `DescriptorSet` and `CommandBuffer` because pooled objects are tested separately in `alloc_callback_fail_multiple`. See [`s_allocCallbackFailGroup`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L4025-L4053).
- `alloc_callback_fail_multiple` only emits tests for `GraphicsPipeline`, `ComputePipeline`, `DescriptorSet`, and `CommandBuffer`, the only object types with a multi-object create path. All other object types are marked `EMPTY_CASE_DESC` with the comment "most objects can be created one at a time only". See [`s_allocCallbackFailMultipleObjectsGroup`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L4061-L4088).
- `private_data` excludes `Instance`, `Device`, and `DeviceGroup` (the device is tested directly inside each leaf rather than as a leaf object), and `MergedPipelineCache`. See [`s_privateDataResourcesGroup`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L4096-L4123).
- `multiple_shared_resources` excludes `Instance` because it has no resources to share. See [`s_createMultipleSharedResourcesGroup`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3808-L3841).

## Key Takeaways

- The 11 intermediate nodes under `api.object_management` select five distinct tested mechanisms: plain lifecycle (`single`, `multiple_unique_resources`, `multiple_shared_resources`, `max_concurrent`), threading (`multithreaded_*`), allocation callback contract (`single_alloc_callbacks`), allocation failure handling (`alloc_callback_fail`, `alloc_callback_fail_multiple`), and private data semantics (`private_data`).
- The object type is a secondary axis: it changes what is constructed but not how the create/destroy path is exercised. Per-intermediate-node exclusion rules, not per-object-type rules, control which combinations are emitted.
- The host never inspects device-written output for any non-`private_data` leaf. Pass/fail is determined by whether `vkCreate*` and `vkDestroy*` returned `VK_SUCCESS` and (for alloc callback variants) whether the recorder is clean.
- Allocation callback validation enforces the spec's scope-lifetime contract: `COMMAND`-scope allocations must not outlive the constructing call, and every allocation must be freed by the time the owning object is destroyed.
- Allocation failure handling requires `VK_ERROR_OUT_OF_HOST_MEMORY` (or the documented pooled status), a clean recorder, and zeroed uncreated handles for `VkPipeline` always and for `VkCommandBuffer`/`VkDescriptorSet` under `VK_KHR_maintenance1`.
- The `private_data` leaf is the only one that reads back device-stored values; it verifies zero-initialization, exact round-trip, and slot reuse across five devices with different slot reservation counts.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test family registration | [`createObjectManagementTests`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3601-L4130) | Adds every intermediate node and defines per-leaf `EMPTY_CASE_DESC` exclusions. |
| Parent registration | [`createApiTests`](../../../modules/vulkan/api/vktApiTests.cpp#L101) | Adds `object_management` to the `api` test category. |
| `single` test body | [`createSingleTest`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2542-L2553) | Create-then-destroy contract for one handle. |
| `multiple_unique_resources` test body | [`createMultipleUniqueResourcesTest`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2555-L2572) | Four independent resource chains. |
| `multiple_shared_resources` test body | [`createMultipleSharedResourcesTest`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2591-L2605) | One shared resource chain, four handles. |
| `max_concurrent` test body | [`createMaxConcurrentTest`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2875-L2902) | Computed object count, watchdog-touched creation loop. |
| `max_concurrent` count computation | [`getSafeObjectCount`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L415-L467) | Per-type count caps and platform-memory-limit derivation. |
| Multithreaded shared-resources body | [`multithreadedCreateSharedResourcesTest`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2996-L3014) | Shared-device, shared-resource thread group. |
| Multithreaded per-thread-resources body | [`multithreadedCreatePerThreadResourcesTest`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3016-L3038) | Shared device, per-thread resource chains. |
| Multithreaded per-thread-device body | [`multithreadedCreatePerThreadDeviceTest`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3079-L3110) | Per-thread `VkDevice` clone. |
| `CreateThread` worker | [`CreateThread::runThread`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2949-L2994) | Barrier-synced create/destroy loop used by all multithreaded variants. |
| `ThreadGroup` runner | [`ThreadGroup::run`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L174-L191) | Collects per-thread `ResultCollector` results into one test status. |
| `single_alloc_callbacks` test body | [`createSingleAllocCallbacksTest`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3112-L3165) | Two-stage recorder validation with `noCmdScope`. |
| `alloc_callback_fail` test body | [`allocCallbackFailTest`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3189-L3290) | `DeterministicFailAllocator` retry loop, `VK_ERROR_OUT_OF_HOST_MEMORY` enforcement. |
| `alloc_callback_fail_multiple` test body | [`allocCallbackFailMultipleObjectsTest`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3337-L3416) | Bulk creation, handle-zeroing and pooled-object policies. |
| Handle-zeroing policy | [`isNullHandleOnAllocationFailure`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3294-L3317) | Per-type handle-zeroing expectations. |
| Pooled-object policy | [`isPooledObject`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3319-L3335) | Suppresses the "Allocation callbacks not called" warning for pooled objects. |
| `private_data` test body | [`createPrivateDataTest`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2720-L2873) | 100-slot, 4-object, 5-device, 3-iteration private data verification. |
| Singleton device pool | [`SingletonDevice`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2609-L2707) | Five devices with different `privateDataSlotRequestCount` values. |
| Object case parameter tables | [`s_*Cases` definitions](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3640-L3738) | Per-object-type `NamedParameters` (sizes, formats, view types, fence flags). |
| Support check helpers | [`check*Support` functions](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3488-L3532) | Feature gates for `imageCubeArray`, `events`, `pipelineCreationCacheControl`, `get_physical_device_properties2`, `recycleDescriptorSetMemory`. |
| Allocation callback recorder | [`AllocationCallbackRecorder`](../../../framework/vulkan/vkAllocationCallbackUtil.hpp#L147-L181) | Logs every allocation, reallocation, free, and internal allocation. |
| Deterministic fail allocator | [`DeterministicFailAllocator`](../../../framework/vulkan/vkAllocationCallbackUtil.hpp#L184-L207) | Fails after N successful allocations; used by both `alloc_callback_fail*` variants. |
| Recorder validation | [`validateAndLog`](../../../framework/vulkan/vkAllocationCallbackUtil.hpp#L255) | Checks for violations and disallowed live allocations. |
| Mustpass coverage | [`api.txt`](../../../mustpass/main/vk-default/api.txt) | Contains every `dEQP-VK.api.object_management.*` leaf for the default mustpass. |
