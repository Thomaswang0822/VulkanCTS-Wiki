# [vktApiObjectManagementTests.cpp](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3595)

## Overview

[`vktApiObjectManagementTests.cpp`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3595) implements the early foundational `api/object_management` subtree registered immediately after [`createDeviceInitializationTests()`](../../modules/vulkan/api/vktApiTests.cpp#L100) and before [`createBufferTests()`](../../modules/vulkan/api/vktApiTests.cpp#L102). Its role matches the Vulkan API test plan's object-management intent: create and destroy many Vulkan object types, vary whether resources are unique or shared, exercise concurrent construction, and probe allocation-callback and private-data behavior where supported by the build and runtime ([`apitests.adoc`](../../../../doc/testspecs/VK/apitests.adoc#L134)).

This file is implementation-heavy and highly generic. Rather than one object type, it builds repeated test families over arrays of per-object parameter sets and shared template helpers. The inspected slice was limited to the registration block, the generic creation helpers, support gates, and the explicitly visible negative/private-data helpers needed to justify the documented families.

## Role of File

Implementation-heavy test file for the `api/object_management` subgroup.

## Source Code

- Primary source: [`vktApiObjectManagementTests.cpp`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L1)
- Declaration: [`vktApiObjectManagementTests.hpp`](../../modules/vulkan/api/vktApiObjectManagementTests.hpp)
- Parent-category registration: [`createApiTests()`](../../modules/vulkan/api/vktApiTests.cpp#L101)
- Related plan context: [`apitests.adoc`](../../../../doc/testspecs/VK/apitests.adoc#L134)

## Registration Path

```text
TestPackage::init / TestPackageSC::init
└── api
    └── createTests(testCtx, "api")
        └── createApiTests(apiTests)
            └── createObjectManagementTests(testCtx)
                └── object_management
                    ├── single
                    ├── multiple_unique_resources
                    ├── multiple_shared_resources
                    ├── max_concurrent                         (not in Vulkan SC)
                    ├── multithreaded_per_thread_device
                    ├── multithreaded_per_thread_resources
                    ├── multithreaded_shared_resources
                    ├── single_alloc_callbacks                (not in Vulkan SC)
                    ├── alloc_callback_fail                   (not in Vulkan SC)
                    ├── alloc_callback_fail_multiple          (not in Vulkan SC)
                    └── private_data                          (not in Vulkan SC)
```

Evidence:

- package-level `api` attachment in [`TestPackage::init()`](../../modules/vulkan/vktTestPackage.cpp#L1349) and [`TestPackageSC::init()`](../../modules/vulkan/vktTestPackage.cpp#L1417)
- parent attachment in [`createApiTests()`](../../modules/vulkan/api/vktApiTests.cpp#L101)
- subgroup registration in [`createObjectManagementTests()`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3595)

## Test Hierarchy

The visible top-level hierarchy is assembled by repeated `createGroup(...)` calls inside [`createObjectManagementTests()`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3595). Each family expands into many object-specific leaf cases through the generic [`addCases()`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3473) helper.

```text
api
└── object_management
    ├── single
    │   ├── instance
    │   ├── device
    │   ├── device_group
    │   ├── device_memory_small
    │   ├── buffer_uniform_small / large
    │   ├── buffer_storage_small / large
    │   ├── buffer_view_uniform_r8g8b8a8_unorm
    │   ├── buffer_view_storage_r8g8b8a8_unorm
    │   ├── image_* / image_view_*
    │   ├── semaphore / event / fence / query_pool
    │   ├── shader_module / pipeline_cache / merged_pipeline_cache*
    │   ├── pipeline_layout* / render_pass / graphics_pipeline / compute_pipeline
    │   ├── descriptor_set_layout* / sampler / descriptor_pool* / descriptor_set
    │   └── framebuffer / command_pool* / command_buffer*
    ├── multiple_unique_resources
    ├── multiple_shared_resources
    ├── max_concurrent                         (not in Vulkan SC)
    ├── multithreaded_per_thread_device
    ├── multithreaded_per_thread_resources
    ├── multithreaded_shared_resources
    ├── single_alloc_callbacks                (not in Vulkan SC)
    ├── alloc_callback_fail                   (not in Vulkan SC)
    ├── alloc_callback_fail_multiple          (not in Vulkan SC)
    └── private_data                          (not in Vulkan SC)
```

Observed leaf construction details:

- every family reuses the same object-parameter tables such as [`s_bufferCases`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3649), [`s_bufferViewCases`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3667), [`s_imageCases`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3675), and others through `CASE_DESC(...)` entries in the family-specific `CaseDescriptions` arrays beginning at [`s_createSingleGroup`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3734)
- object families are omitted selectively with `EMPTY_CASE_DESC(...)` when the pattern is not meaningful or needs per-thread/per-pool dependencies, for example `DescriptorSet` and `CommandBuffer` under [`s_multithreadedCreateSharedResourcesGroup`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3942)
- some leaves use support functions rather than unconditional registration, via [`addCases()`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3473), such as [`checkImageCubeArraySupport()`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3484), [`checkEventSupport()`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3495), and [`checkPipelineCacheControlSupport()`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3506)

## Test Families

### 1. Single-object construction and destruction

The `single` branch registers one create/destroy smoke test per object/parameter tuple via [`createSingleTest()`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2539) and [`s_createSingleGroup`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3734).

Observed behavior:

- [`createSingleTest()`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2539) creates one [`Environment`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L247) with `maxResourceConsumers = 1`, constructs the object's `Resources`, creates exactly one Vulkan object, then relies on RAII destruction when the local `Unique<...>` goes out of scope at [`vktApiObjectManagementTests.cpp#L2546`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2546)
- the object/parameter span is broad and includes instances, devices, memory, buffers, buffer views, images, pipelines, descriptor objects, framebuffers, and command infrastructure through the case arrays at [`vktApiObjectManagementTests.cpp#L3646`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3646)
- the inspected plan text says object-management tests should focus on creation/destruction rather than functional use, which matches the simple pass condition in [`createSingleTest()`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2549) and the plan note in [`apitests.adoc`](../../../../doc/testspecs/VK/apitests.adoc#L137)

### 2. Multiple objects with unique vs shared resources

Two adjacent branches compare repeated creation with independent versus shared dependencies:

- `multiple_unique_resources` uses [`createMultipleUniqueResourcesTest()`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2552) and registration array [`s_createMultipleUniqueResourcesGroup`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3765)
- `multiple_shared_resources` uses [`createMultipleSharedResourcesTest()`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2588) and registration array [`s_createMultipleSharedResourcesGroup`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3802)

Observed behavior:

- the unique-resources variant allocates four distinct `Resources` objects (`res0`..`res3`) before constructing four objects of the same type ([`vktApiObjectManagementTests.cpp#L2555`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2555))
- the shared-resources variant builds one `Resources` object with `maxResourceConsumers = 4` and reuses it for all four constructions ([`vktApiObjectManagementTests.cpp#L2591`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2591))
- Vulkan SC trims some device/device-group unique/shared branches with `EMPTY_CASE_DESC(...)` in the registration arrays ([`vktApiObjectManagementTests.cpp#L3767`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3767), [`vktApiObjectManagementTests.cpp#L3804`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3804))

### 3. Maximum concurrently live objects

The non-Vulkan-SC `max_concurrent` branch uses [`createMaxConcurrentTest()`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2871) and registration array [`s_createMaxConcurrentGroup`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3841).

Observed behavior:

- the per-object concurrency target comes from `Object::getMaxConcurrent(context, params)` at [`vktApiObjectManagementTests.cpp#L2877`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2877)
- the test keeps all created handles alive in a vector of shared pointers until the full target count is reached, then clears the vector to trigger destruction ([`vktApiObjectManagementTests.cpp#L2880`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2880))
- watchdog touches every `1024` creations and once at the end prevent very large object-count loops from looking hung ([`vktApiObjectManagementTests.cpp#L2881`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2881))
- the plan's "allocating multiple objects of same type" objective is consistent with this branch, but the exact per-type limits are not documented here because `getMaxConcurrent()` implementations were not inspected in this run

### 4. Multithreaded construction patterns

Three sibling branches cover concurrent creation using different sharing models:

- `multithreaded_per_thread_device` via registration array [`s_multithreadedCreatePerThreadDeviceGroup`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3874)
- `multithreaded_per_thread_resources` via registration array [`s_multithreadedCreatePerThreadResourcesGroup`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3908)
- `multithreaded_shared_resources` via registration array [`s_multithreadedCreateSharedResourcesGroup`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3942)

Evidence for the concurrency framework:

- the file defines a dedicated [`ThreadGroup`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L113) and [`ThreadGroupThread`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L129) abstraction with a shared [`de::SpinBarrier`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L126) so worker threads can start in lockstep and still report independent failures through [`tcu::ResultCollector`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L155)
- the default thread count is clamped to `2..8` logical cores outside Vulkan SC and fixed at `2` in Vulkan SC by [`getDefaultTestThreadCount()`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L236)

Observed registration distinctions:

- `Instance`, `Device`, and `DeviceGroup` are intentionally omitted from `multithreaded_per_thread_device` because that pattern "does not make sense" for those object categories ([`vktApiObjectManagementTests.cpp#L3875`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3875))
- `DescriptorSet` in per-thread-device and per-thread-resources branches uses `checkRecycleDescriptorSetMemorySupport` at [`vktApiObjectManagementTests.cpp#L3898`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3898), indicating a support condition specific to descriptor-set recycling; that helper's implementation was not inspected in this run, so the exact gate should be treated as observed registration fact rather than fully explained semantics
- `DescriptorSet` and `CommandBuffer` are omitted from the shared-resources branch because they need per-thread pools ([`vktApiObjectManagementTests.cpp#L3971`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3971))

### 5. Allocation-callback correctness and failure behavior

Four non-Vulkan-SC branches focus on host-allocation callback behavior:

- `single_alloc_callbacks` uses the helper that validates zero outstanding callback allocations before returning pass at [`vktApiObjectManagementTests.cpp#L3144`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3144) through [`vktApiObjectManagementTests.cpp#L3160`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3160), and is registered through [`s_createSingleAllocCallbacksGroup`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3983)
- `alloc_callback_fail` uses [`allocCallbackFailTest()`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3186) and registration array [`s_allocCallbackFailGroup`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L4019)
- `alloc_callback_fail_multiple` uses [`allocCallbackFailMultipleObjectsTest()`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3333) and registration array [`s_allocCallbackFailMultipleObjectsGroup`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L4055)

Observed behavior:

- the single-allocation-callback family validates that object-scoped and resource-scoped callback recorders return to zero outstanding allocations after construction and destruction, using [`validateAndLog()`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3148) and [`validateAndLog()`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3157)
- [`allocCallbackFailTest()`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3186) uses `DeterministicFailAllocator` at [`vktApiObjectManagementTests.cpp#L3210`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3210) to fail host allocations after `N` successful ones, repeatedly retries creation, and requires any thrown OOM to be specifically [`VK_ERROR_OUT_OF_HOST_MEMORY`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3234)
- if the search space is too large, [`allocCallbackFailTest()`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3267) degrades to an incomplete-but-pass result with an explicit message rather than overclaiming total coverage
- [`allocCallbackFailMultipleObjectsTest()`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3333) exercises APIs that create multiple handles in one call, checks whether post-failure handles are required to be null based on [`isNullHandleOnAllocationFailure()`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3291), and again requires [`VK_ERROR_OUT_OF_HOST_MEMORY`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3394) on failure
- pooled objects are treated specially by [`isPooledObject()`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3315); if they appear not to use host memory, the multiple-object failure test returns a pass with a "Not validated" note instead of a hard failure ([`vktApiObjectManagementTests.cpp#L3405`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3405))

### 6. Private-data attachment and persistence checks

The non-Vulkan-SC `private_data` branch is registered through [`createTestGroup()`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L4120) and uses [`createPrivateDataTest()`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2717) for many object types.

Observed behavior:

- the branch first requires `privateData == VK_TRUE` through [`context.getPrivateDataFeatures().privateData`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2720)
- [`SingletonDevice`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2607) creates five cached logical devices with different requested private-data-slot counts, using chained [`VkDevicePrivateDataCreateInfoEXT`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2623) structures and enabling `VK_EXT_private_data` in [`VkDeviceCreateInfo`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2658)
- for each tested object type, the helper allocates `100` private-data slots, interleaves slot allocation with four object constructions, verifies all initial values read back as zero, writes deterministic values, and verifies the written values for both the tested objects and the private-data-slot objects themselves ([`vktApiObjectManagementTests.cpp#L2739`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2739), [`vktApiObjectManagementTests.cpp#L2770`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2770), [`vktApiObjectManagementTests.cpp#L2803`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2803))
- it also checks device-scoped private data on each logical device ([`vktApiObjectManagementTests.cpp#L2837`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2837)) and recreates all slots across three outer iterations ([`vktApiObjectManagementTests.cpp#L2766`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2766), [`vktApiObjectManagementTests.cpp#L2858`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2858))

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Top-level subgroup names | Registered in [`createObjectManagementTests()`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3763) through [`createObjectManagementTests()`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L4120) |
| Buffer parameter set | `buffer_uniform_small`, `buffer_uniform_large`, `buffer_storage_small`, `buffer_storage_large` in [`s_bufferCases`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3649) |
| Buffer sizes in object-management coverage | `1024` and `16 * 1024 * 1024` bytes in [`s_bufferCases`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3652) |
| Buffer-view parameter set | uniform/storage texel buffer cases using `VK_FORMAT_R8G8B8A8_UNORM`, buffer size `8192`, range `4096` in [`s_bufferViewCases`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3667) |
| Image parameter set | 1D, 2D, cube-compatible 2D, and 3D image shapes in [`img1D`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3599) through [`img3D`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3610) |
| Image-view parameter set | `1D`, `1D_ARRAY`, `2D`, `2D_ARRAY`, `CUBE`, `CUBE_ARRAY`, `3D` in [`imgView1D`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3613) through [`imgView3D`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3628) |
| Fence cases | unsignaled and `VK_FENCE_CREATE_SIGNALED_BIT` in [`s_fenceCases`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3691) |
| Descriptor-pool cases | default and `VK_DESCRIPTOR_POOL_CREATE_FREE_DESCRIPTOR_SET_BIT` in [`s_descriptorPoolCases`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3716) |
| Command-buffer levels | primary and secondary in [`s_commandBufferCases`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3728) |
| Objects per repeated-creation helpers | `4` objects in [`createMultipleUniqueResourcesTest()`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2562), [`createMultipleSharedResourcesTest()`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2595), and private-data object arrays at [`objs[4]`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2764) |
| Private-data slot count | `100` in [`createPrivateDataTest()`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2739) |
| Private-data logical-device variants | five requested-slot patterns `{0,0}`, `{1,0}`, `{1,1}`, `{4,4}`, `{1,100}` in [`SingletonDevice::createPrivateDataDevice()`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2611) |
| Default multithread count | logical-core clamp `2..8` or fixed `2` in [`getDefaultTestThreadCount()`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L236) |

## Support / Feature Requirements

Observed explicit support gates:

- cube-array image-view cases require `imageCubeArray` through [`checkImageCubeArraySupport()`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3484)
- `Device` object cases require instance functionality `VK_KHR_get_physical_device_properties2` through [`checkGetPhysicalDevicePropertiesExtension()`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3490)
- `Event` cases may be rejected on portability-subset implementations when `events == VK_FALSE` through [`checkEventSupport()`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3495)
- merged-pipeline-cache cases require `VK_EXT_pipeline_creation_cache_control` and the corresponding feature via [`checkPipelineCacheControlSupport()`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3506)
- private-data cases require `privateData` support via [`createPrivateDataTest()`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2720)
- all allocation-callback-centered groups are excluded from Vulkan SC by preprocessor guards around their registration blocks ([`vktApiObjectManagementTests.cpp#L3980`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3980), [`vktApiObjectManagementTests.cpp#L4016`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L4016), [`vktApiObjectManagementTests.cpp#L4052`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L4052), [`vktApiObjectManagementTests.cpp#L4088`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L4088))

## Verification Methods

Observed pass/fail logic in the inspected helpers is primarily structural rather than feature-functional:

- success-path helpers pass when object creation and implicit destruction complete without exception, for example [`createSingleTest()`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2549), [`createMultipleUniqueResourcesTest()`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2568), and [`createMultipleSharedResourcesTest()`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2601)
- maximum-concurrency helpers pass after constructing the requested number of live objects and then releasing them without error ([`vktApiObjectManagementTests.cpp#L2886`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2886))
- allocation-callback families verify balanced callback state using [`validateAndLog()`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3148) and [`validateAndLog()`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3261)
- OOM negative tests explicitly validate returned error codes and, where applicable, that failed output handles are zeroed ([`vktApiObjectManagementTests.cpp#L3234`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3234), [`vktApiObjectManagementTests.cpp#L3389`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3389))
- private-data tests validate exact readback values before and after writes across objects, slots, and devices ([`vktApiObjectManagementTests.cpp#L2777`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2777), [`vktApiObjectManagementTests.cpp#L2796`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2796), [`vktApiObjectManagementTests.cpp#L2841`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2841))

## Test Principles Observed

- broad object coverage is generated from common templates rather than duplicated per-object code, making the file a matrix of object categories × stress patterns rather than many unrelated hand-written tests
- resource-sharing mode is a first-class variable: several families differ only by whether dependencies are unique per object, shared within one thread, or shared across threads
- negative allocation tests are designed to assert API-contract details, not just crash resistance: expected error code, callback cleanup, and null-handle behavior are all checked when visible in the API under test
- private-data tests treat object-management as more than raw handle lifetime by verifying that object identity can carry per-object metadata consistently across creation patterns

## Notes / Uncertainties

- This document intentionally centers on the registration-visible object-management matrix and the generic helper logic that defines each family. It does not expand every object-specific `Object::Resources`, `Object::create`, or `Object::getMaxConcurrent()` specialization, because those implementations were outside the chosen slice.
- `checkRecycleDescriptorSetMemorySupport` is referenced in registration at [`vktApiObjectManagementTests.cpp#L3898`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3898), but its implementation was not inspected in this run; only its existence as a support gate is claimed here.
- The multithreaded test executors themselves were not traced line-by-line in this pass. The concurrency model is evidenced by [`ThreadGroup`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L113), the family names, and the registered helper names, but exact per-thread object counts beyond the visible defaults are not claimed.
