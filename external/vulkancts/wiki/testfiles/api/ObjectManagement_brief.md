# Understanding Brief: `api.object_management`

## One-Sentence Test Purpose

This test family checks whether the implementation can create and destroy every major Vulkan object type under plain sequential use, shared and unique resource dependencies, peak concurrency, multithreaded contention, custom allocator validation, deterministic allocation failure, and `VK_EXT_private_data` storage.

## Background Knowledge

### Vulkan object lifetime and parent-child ownership

A Vulkan object is created by a `vkCreate*` call that returns a handle, used for the lifetime of the object, and destroyed by a matching `vkDestroy*` call. The spec requires that all *child* objects (objects created with a parent handle in their `createInfo`) are destroyed before their parent. For example, a `VkBuffer` must be destroyed before its parent `VkDevice`. The implementation is expected to either reject illegal lifetime operations at create/destroy time or, where the spec allows it, defer the underlying resource release. CTS exercises this contract by constructing each object with its real dependency chain and letting `Unique<VkType>` destructors tear the chain down in reverse order.

Why it matters here:
- Each `single.<object>` leaf constructs not just the object under test but its full resource dependency chain, so a failure points to either the object itself or a dependency.
- The multiple and max_concurrent leaves rely on independent lifetimes that must not interact, which is only true if the implementation honors per-object ownership.

### `VkAllocationCallbacks` and allocation scopes

`VkAllocationCallbacks` lets the application supply its own `pfnAllocation`, `pfnReallocation`, and `pfnFree` functions. Every `vkCreate*`/`vkDestroy*` call (and many internal driver allocations) flows through these callbacks when they are provided. The spec tags each allocation with a `VkSystemAllocationScope` — `INSTANCE`, `DEVICE`, `CACHE`, `OBJECT`, or `COMMAND` — describing how long the allocation is expected to live.

The contract the spec imposes, and that this family verifies, is:

- Allocations tagged `OBJECT` or shorter-lived scopes (`COMMAND`) must be freed by the time object construction or destruction returns.
- Allocations tagged `INSTANCE` or `DEVICE` may legitimately remain live for the lifetime of the parent instance or device, so they are allowed to persist after a single object is destroyed.
- When `pfnAllocation` returns `NULL`, the implementing `vkCreate*` call must return `VK_ERROR_OUT_OF_HOST_MEMORY` (or, for pooled objects such as `VkDescriptorSet` and `VkCommandBuffer`, a different documented status) and must not leak any partial state.

CTS uses an `AllocationCallbackRecorder` to log every callback, then `validateAndLog` checks for double frees, frees of unallocated pointers, realloc violations, and leftover live allocations in scopes that should already have been cleaned up.

### Thread safety of Vulkan object creation

The Vulkan spec makes object creation and destruction externally synchronized only where it explicitly says so; otherwise the implementation must serialize internally. For the vast majority of `vkCreate*`/`vkDestroy*` calls, concurrent calls from multiple threads on the same `VkDevice` (or on different `VkDevice`s) are required to be safe. CTS exercises this by spawning a `ThreadGroup` that runs a barrier-synchronized `CreateThread<Object>` per thread, with each thread repeatedly constructing and destroying the object. The test passes only if every thread completes without exception.

### `VK_EXT_private_data` per-object storage

`VK_EXT_private_data` (promoted to core in Vulkan 1.3 as `VK_KHR_private_data`) adds `vkCreatePrivateDataSlotEXT`, `vkSetPrivateDataEXT`, and `vkGetPrivateDataEXT`. Each `VkPrivateDataSlotEXT` is a key; for each (object, slot) pair, the implementation stores a `uint64_t` value. The contract is that the initial value for any new (object, slot) pair is zero, `vkSetPrivateDataEXT` overwrites the value, and `vkGetPrivateDataEXT` reads back exactly what was last set. The slot count is bounded by `privateDataSlotRequestCount` at device creation plus any reserved by the implementation.

## One Concrete Example

Consider `dEQP-VK.api.object_management.single_alloc_callbacks.buffer_uniform_small`. The test does roughly the following, in order:

1. Build an `Environment` rooted at the context's instance and device, but with an `AllocationCallbackRecorder` chained into the device's callbacks so that every allocation made by the device and its children is recorded.
2. Inside that environment, construct the `Buffer::Resources` (a parent `VkBuffer` plus its `VkDeviceMemory` binding), then construct a separate `AllocationCallbackRecorder` for just the object under test.
3. Create a `VkBuffer` with usage `VK_BUFFER_USAGE_UNIFORM_BUFFER_BIT` and size 1024, scoped to the object recorder.
4. After construction returns, call `validateAndLog(..., noCmdScope)` to confirm that no `COMMAND`-scope allocation made during construction is still live. `INSTANCE`, `DEVICE`, `CACHE`, and `OBJECT` scope allocations are tolerated because the spec permits them to outlive the create call.
5. Destroy the buffer (the `Unique<VkBuffer>` destructor runs).
6. Call `validateAndLog(..., 0u)` to confirm every allocation made through the object recorder has been freed.
7. Tear down the resources and the resource recorder, then call `validateAndLog` on the resource recorder with scope `0u` to confirm the resource chain is also clean.

This is a conceptual reconstruction; the real control flow is in `createSingleAllocCallbacksTest<Object>`.

## End-to-End Test Flow

The flow varies by intermediate node, but the shared skeleton is:

```text
[host] build an Environment rooted at the context instance/device, optionally chaining an AllocationCallbackRecorder
[host] build the Object::Resources (parent objects, memory, descriptors, command pool, etc.) needed by the object under test
[host] (single_alloc_callbacks only) install a second recorder for the object under test
[host] create one or more Object::Type handles via Object::create (which calls the appropriate vkCreate*)
[host] (alloc_callback_fail only) wrap create in a retry loop with a DeterministicFailAllocator that fails after N allocations
[host] (private_data only) interleave object and slot creation, then set/get/verify private data across many slots and objects
[host] destroy the object handles via Unique<VkType> destructors (which call vkDestroy*)
[host] (alloc callbacks only) validate the recorder: no live allocations in scopes that should be clean, no double frees, no orphan frees
[host] destroy the resources and validate their recorder
[host] decide pass/fail: any vk::Error or recorder violation fails; specific leaf checks (e.g. private data value mismatch, null-handle expectation) also fail
```

For multithreaded variants, the inner `[host] create -> [host] destroy` block runs inside a `CreateThread<Object>` on N threads, with a barrier sync every few iterations to maximize the chance of concurrent driver entry.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- For `ShaderModule`, `GraphicsPipeline`, `ComputePipeline`, and `MergedPipelineCache` leaves, a small GLSL program is registered via `Object::initPrograms` and built into SPIR-V by the framework. The shader content is not part of the tested behavior; it exists only so the pipeline and shader module creation calls have a valid `VkShaderModule` to consume.
- No pipeline state, render pass, or descriptor set layout is varied in a behaviorally meaningful way. They use fixed, minimal configurations.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `VkInstance` and `VkDevice` (root) | yes | n/a | n/a | n/a | Parent for every other object; some leaves create their own per-thread device. |
| `VkDeviceMemory` (1 KB) | yes | yes (host-visible) | no | no | Backs the test buffers and images; used as the `DeviceMemory` leaf itself. |
| `VkBuffer` (uniform/storage, 1 KB and 16 MB) | yes | yes | no | no | Backs `BufferView` and `DescriptorSet` leaves; the `Buffer` leaf itself. |
| `VkImage` (1D/2D/3D, cube) | yes | yes | no | no | Backs `ImageView` and `Framebuffer` leaves; the `Image` leaf itself. |
| `VkCommandPool`, `VkDescriptorPool` | yes | n/a | n/a | n/a | Pool parents for `CommandBuffer` and `DescriptorSet` leaves; excluded from shared-resources multithreaded cases because pools are not thread-safe externally. |
| `VkPipelineCache` (parent + source/dst sync variants) | yes | n/a | n/a | n/a | Parent for `MergedPipelineCache` leaves; the merge variants exercise `VK_EXT_pipeline_creation_cache_control`. |
| `VkPrivateDataSlotEXT` (100 per device iteration) | yes | n/a | n/a | yes (via `vkGetPrivateDataEXT`) | Keys for the private data tests; values are written by `vkSetPrivateDataEXT` and read back by the host. |

The host never inspects device-written output for any non-`private_data` leaf. Pass/fail is determined by whether `vkCreate*` and `vkDestroy*` returned `VK_SUCCESS` and (for alloc callback variants) whether the recorder is clean.

## What Is Checked

| Intermediate node | Pass condition |
|-------------------|----------------|
| `single` | `Object::create` returns a valid handle; the implicit destructor returns without throwing. |
| `multiple_unique_resources` | Four handles created against four independent resource chains; all destructors return without throwing. |
| `multiple_shared_resources` | Four handles created against one shared resource chain; all destructors return without throwing. |
| `max_concurrent` | A computed `numObjects` (capped by `MAX_CONCURRENT_*` constants and host/device memory limits) handles are alive simultaneously; all destructors return without throwing. |
| `multithreaded_per_thread_device` | Each thread creates its own `VkDevice` and then loops create/destroy; no thread throws. |
| `multithreaded_per_thread_resources` | Threads share the device but each owns its resource chain; no thread throws. |
| `multithreaded_shared_resources` | Threads share device and resource chain; no thread throws. Excludes `DescriptorSet` and `CommandBuffer` because their pools are externally synchronized. |
| `single_alloc_callbacks` | After construction, no `COMMAND`-scope allocation is live. After destruction, no allocation of any scope is live. No `AllocationCallbackViolation` recorded. |
| `alloc_callback_fail` | Iteratively inject an allocation failure after `numPassingAllocs` successful allocations. Each failed attempt must return `VK_ERROR_OUT_OF_HOST_MEMORY`, leave the recorder clean, and not throw a different error. Eventually the object must construct successfully. |
| `alloc_callback_fail_multiple` | Same as `alloc_callback_fail` but for `Object::createMultiple` (graphics/compute pipeline, descriptor set, command buffer). On failure, the implementation must zero the uncreated handles when `VK_KHR_maintenance1` is enabled (or always, for `VkPipeline`). |
| `private_data` | Initial `vkGetPrivateDataEXT` value is zero for every (object, slot) pair. After `vkSetPrivateDataEXT`, `vkGetPrivateDataEXT` reads back exactly the value written. Verified across 100 slots, 4 objects, 5 singleton devices, and 3 iterations. Also exercised on `VkPrivateDataSlotEXT` itself and on `VkDevice`. |

## Behavior Parameter Identification

> **Behavior parameter:** intermediate node (the subgroup below `object_management`)
>
> **Candidate values:** `single`, `multiple_unique_resources`, `multiple_shared_resources`, `max_concurrent`, `multithreaded_per_thread_device`, `multithreaded_per_thread_resources`, `multithreaded_shared_resources`, `single_alloc_callbacks`, `alloc_callback_fail`, `alloc_callback_fail_multiple`, `private_data`

The object type (the test case leaf, e.g. `instance`, `buffer_uniform_small`, `image_view_cube_arr`) is a secondary axis. It changes *what* is constructed but not *how* the create/destroy path is exercised. The intermediate node is the axis that selects the tested behavior: lifecycle, threading, allocation callback contract, allocation failure handling, or private data semantics.

## What Failure Means

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
| `alloc_callback_fail_multiple` | Allocation failure handling violation for pooled/bulk creation: invalid error code, leaked allocation, or — when `VK_KHR_maintenance1` is enabled (or for `VkPipeline`, always) — uncreated handles not set to `VK_NULL_HANDLE`. |
| `private_data` | Private data set/get violation: initial value not zero, value read back did not match the value written, or `vkSetPrivateDataEXT` returned an error. |

## Important Variations and Special Cases

- **Per-intermediate-node object exclusions.** Each intermediate node marks certain object types as `EMPTY_CASE_DESC`, meaning no test is generated for that combination. The exclusions are intentional, not bugs:
  - `multithreaded_per_thread_device` excludes `Instance`, `Device`, and `DeviceGroup` (a per-thread device cannot be created without a shared instance, and a per-thread instance defeats the test's purpose).
  - `multithreaded_shared_resources` excludes `Instance`, `DescriptorSet`, and `CommandBuffer` (the latter two need per-thread pools, which are externally synchronized).
  - `alloc_callback_fail` excludes `DescriptorSet` and `CommandBuffer` (pooled objects are tested in `alloc_callback_fail_multiple` instead).
  - `alloc_callback_fail_multiple` only emits tests for `GraphicsPipeline`, `ComputePipeline`, `DescriptorSet`, and `CommandBuffer` (the only object types with a multi-object create path).
  - `private_data` excludes `Instance`, `Device`, `DeviceGroup`, and `MergedPipelineCache`.
- **Vulkan SC exclusions.** `max_concurrent`, `single_alloc_callbacks`, `alloc_callback_fail`, `alloc_callback_fail_multiple`, and `private_data` are entirely excluded from Vulkan SC builds because `VkAllocationCallbacks` and `VK_EXT_private_data` are not part of Vulkan SC. `Device` and `DeviceGroup` are also excluded from the multiple and shared-resources variants in SC builds.
- **Feature gates.** `ImageView` cube-array leaves require `imageCubeArray`. `Event` leaves require `VK_KHR_portability_subset.events` to be true (or the absence of the portability subset). `MergedPipelineCache` leaves require `VK_EXT_pipeline_creation_cache_control`. `Device` leaves require `VK_KHR_get_physical_device_properties2`. `private_data` leaves require `VK_EXT_private_data`.
- **`isNullHandleOnAllocationFailure` policy.** For `alloc_callback_fail_multiple`, the test expects uncreated handles to be set to `VK_NULL_HANDLE` when `VK_KHR_maintenance1` is enabled for `VkCommandBuffer` and `VkDescriptorSet`, and always for `VkPipeline`. Without `VK_KHR_maintenance1`, the handles are not checked.
- **`isPooledObject` policy.** `VkCommandBuffer` and `VkDescriptorSet` are pooled; their `alloc_callback_fail_multiple` pass result is `Not validated: pooled objects didn't seem to use host memory` when `numPassingAllocs == 0`, instead of a quality warning.
- **`max_concurrent` count computation.** The number of objects created is computed from the platform memory limits and a measured per-object system-memory footprint, capped by per-type constants such as `MAX_CONCURRENT_INSTANCES = 32`, `MAX_CONCURRENT_SYNC_PRIMITIVES = 100`, `MAX_CONCURRENT_PIPELINE_CACHES = 128`, `MAX_CONCURRENT_QUERY_POOLS = 8192`, and `DEFAULT_MAX_CONCURRENT_OBJECTS = 16 * 1024`.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Test family registration | [vktApiObjectManagementTests.cpp#L3601-L4130](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3601-L4130) | `createObjectManagementTests` adds every intermediate node and defines per-leaf `EMPTY_CASE_DESC` exclusions. |
| Parent registration | [vktApiTests.cpp#L101](../../../modules/vulkan/api/vktApiTests.cpp#L101) | `createObjectManagementTests` is added to the `api` test category. |
| `single` test body | [vktApiObjectManagementTests.cpp#L2542-L2553](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2542-L2553) | `createSingleTest` shows the create-then-destroy contract. |
| `multiple_unique_resources` test body | [vktApiObjectManagementTests.cpp#L2555-L2572](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2555-L2572) | Four independent resource chains. |
| `multiple_shared_resources` test body | [vktApiObjectManagementTests.cpp#L2591-L2605](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2591-L2605) | One shared resource chain, four handles. |
| `max_concurrent` test body | [vktApiObjectManagementTests.cpp#L2875-L2902](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2875-L2902) | Computed object count, watchdog-touched creation loop. |
| `multithreadedCreateSharedResourcesTest` | [vktApiObjectManagementTests.cpp#L2996-L3014](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2996-L3014) | Shared-device, shared-resource thread group. |
| `multithreadedCreatePerThreadResourcesTest` | [vktApiObjectManagementTests.cpp#L3016-L3038](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3016-L3038) | Shared device, per-thread resource chains. |
| `multithreadedCreatePerThreadDeviceTest` | [vktApiObjectManagementTests.cpp#L3079-L3110](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3079-L3110) | Per-thread `VkDevice` clone. |
| `createSingleAllocCallbacksTest` | [vktApiObjectManagementTests.cpp#L3112-L3165](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3112-L3165) | Two-stage recorder validation with `noCmdScope`. |
| `allocCallbackFailTest` | [vktApiObjectManagementTests.cpp#L3189-L3290](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3189-L3290) | DeterministicFailAllocator retry loop, `VK_ERROR_OUT_OF_HOST_MEMORY` enforcement. |
| `allocCallbackFailMultipleObjectsTest` | [vktApiObjectManagementTests.cpp#L3337-L3416](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3337-L3416) | Bulk creation, `isNullHandleOnAllocationFailure` and `isPooledObject` policies. |
| `isNullHandleOnAllocationFailure` policy | [vktApiObjectManagementTests.cpp#L3294-L3317](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3294-L3317) | Per-type handle-zeroing expectations. |
| `createPrivateDataTest` | [vktApiObjectManagementTests.cpp#L2720-L2873](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2720-L2873) | 100-slot, 4-object, 5-device, 3-iteration private data verification. |
| `CreateThread<Object>` worker | [vktApiObjectManagementTests.cpp#L2949-L2994](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2949-L2994) | Barrier-synced create/destroy loop used by all multithreaded variants. |
| `ThreadGroup` runner | [vktApiObjectManagementTests.cpp#L113-L191](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L113-L191) | Collects per-thread `ResultCollector` results into one test status. |
| Object case parameter tables | [vktApiObjectManagementTests.cpp#L3640-L3738](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3640-L3738) | Per-object-type `NamedParameters` (sizes, formats, view types, fence flags). |
| Support check helpers | [vktApiObjectManagementTests.cpp#L3488-L3532](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3488-L3532) | `checkImageCubeArraySupport`, `checkEventSupport`, `checkPipelineCacheControlSupport`, `checkGetPhysicalDevicePropertiesExtension`, `checkRecycleDescriptorSetMemorySupport`. |

## Questions / Risk Points for User Audit

- Is the choice of intermediate node as the primary behavioral axis correct, given that the object type is also a strong axis? The object type changes *what* is created but the intermediate node changes the *mechanism* being verified, so the brief treats the intermediate node as primary.
- Is the Vulkan SC exclusion wording precise enough? The source comments are the authority; the brief paraphrases them as "VkAllocationCallbacks is not supported and pointers to this type must be NULL".
- Should the `private_data` description of the `SingletonDevice` (5 devices with varying `privateDataSlotRequestCount`) be summarized as "5 singleton devices" or described in full? The brief summarizes; the final page can keep the summary.
- Is the `alloc_callback_fail` `maxTries`/`finalLimit` retry policy (40 iterations default, expandable to 10000 via `--deqp-test-iteration-count`) worth documenting in the final page? The brief mentions it lightly; the final page should keep the light treatment unless the user wants more detail.
- The Vulkan spec chapters at `external/vulkan-docs/src/chapters/` were not present in this checkout. The brief's `Background Knowledge` is grounded in the Vulkan 1.3 spec text for object lifetime, allocation callbacks, threading, and `VK_EXT_private_data` from assistant knowledge, not from a local spec read. If the user has a local spec checkout elsewhere, the final page should re-verify the wording against it.

## Conversion Notes for Final Wiki Rewrite

- Distill `Background Knowledge` into four brief prerequisites: object lifetime/parent-child ownership, `VkAllocationCallbacks` and allocation scopes, Vulkan thread-safety default, and `VK_EXT_private_data` per-object storage semantics. Drop the long teaching prose.
- Keep the `One Concrete Example` as a short narrative inside `## Runtime Execution and Result Checking` for `single_alloc_callbacks`, because it is the most representative alloc-callback flow.
- Carry `## Behavior Parameter Identification` directly into `## Behavior Parameters`, with one `###` subsection per intermediate node value.
- Copy `### Failure Cause Mapping` verbatim into the final page's `### Failure Cause Mapping`.
- Write `### Cause Analysis` fresh, with one `####` subsection per distinct cause: object lifecycle failure, threading failure, allocation callback contract violation, allocation failure handling violation, private data set/get violation. Some causes apply to multiple intermediate nodes; group them rather than repeating per value.
- Move the source-mapping table to `## Source Reference Appendix` and trim entries that the page does not actually reference.
- Preserve the per-intermediate-node exclusion list as a `## Case Pruning` `### Design-based pruning` subsection, because the exclusions are intentional design choices, not requirement gates.
- Put feature gates (`imageCubeArray`, `VK_EXT_pipeline_creation_cache_control`, `VK_KHR_get_physical_device_properties2`, `VK_KHR_portability_subset.events`, `VK_EXT_private_data`, Vulkan SC `recycleDescriptorSetMemory`) under `### Requirement-based pruning`.
- Drop the `Bound resources` table from the final page; object management does not bind GPU resources in any behaviorally meaningful way, and the table is learning scaffolding.
- Risk points are resolved by the inspected source. The only unresolved item is the absence of a local Vulkan spec checkout, which does not affect final page semantics.
