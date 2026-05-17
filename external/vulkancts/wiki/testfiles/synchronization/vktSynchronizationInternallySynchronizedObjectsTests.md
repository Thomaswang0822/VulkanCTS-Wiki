# [vktSynchronizationInternallySynchronizedObjectsTests.cpp](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L1)

## Overview

This file implements tests that verify the internally synchronized behavior of Vulkan objects -- specifically `VkPipelineCache`. The Vulkan specification states that certain objects are internally synchronized, meaning concurrent access from multiple threads does not require explicit synchronization by the application. These tests exercise `VkPipelineCache` from multiple threads simultaneously to confirm that implementations correctly handle concurrent pipeline creation and execution.

## Role of File

This file contributes the `internally_synchronized_objects` group to the **LEGACY-only** `synchronization` category. It is **NOT** registered under `synchronization2`. The factory function [`createInternallySynchronizedObjects()`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L1352) does not take a `SynchronizationType` parameter.

## Source Code

| File | Description |
|------|-------------|
| [`vktSynchronizationInternallySynchronizedObjectsTests.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L1) | Implementation |
| [`vktSynchronizationInternallySynchronizedObjectsTests.hpp`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.hpp#L1) | Public header |

## Registration Hierarchy

```text
synchronization.internally_synchronized_objects
├── pipeline_cache_compute
└── pipeline_cache_graphics
```

Source: [`createInternallySynchronizedObjects()`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L1352).

**NOT registered under `synchronization2`**. The synchronization2 category has a separate `internally_synchronized_queues` group from a different source file.

## Test Families

### pipeline_cache_compute — PipelineCacheComputeTest

Tests concurrent access to `VkPipelineCache` from multiple threads creating and executing compute pipelines.

**Algorithm**:
1. Create a custom device with all available compute-capable queues
2. Create 3 compute shaders with different dispatch configurations:
   - `compute_0`: dispatch 16 workgroups of size 1 (linear index)
   - `compute_1`: dispatch 1 workgroup of size 1 (loop over all elements)
   - `compute_2`: dispatch 1 workgroup of size 16 (local invocation index)
3. Create a pipeline cache and an initial compute pipeline
4. Execute the initial pipeline once to warm the cache
5. Spawn N threads (clamped to 4-32 based on available logical cores, or 2 for Vulkan SC)
6. Each thread iterates `EXECUTION_PER_THREAD` times (100 for non-SC, 10 for SC):
   - Creates a compute pipeline from the shared pipeline cache
   - Executes the pipeline, writing expected values to a storage buffer
   - Verifies the output buffer contents
7. All threads run concurrently using a [`de::SpinBarrier`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L637) for synchronization

**Verification**: Each thread checks that the output buffer contains the expected values (0, 1, 2, ..., 15) after pipeline execution.

### pipeline_cache_graphics — PipelineCacheGraphicTest

Tests concurrent access to `VkPipelineCache` from multiple threads creating and executing graphics pipelines.

**Algorithm**:
1. Create a custom device with all available graphics-capable queues
2. Create 3 vertex shaders + 1 fragment shader:
   - `vert_0`: write vertex index to SSBO (dispatch 16 vertices)
   - `vert_1`: loop over all elements and write index (dispatch 1 vertex)
   - `vert_2`: reverse loop over elements (dispatch 1 vertex)
   - `frag`: output white color
3. Create a pipeline cache and an initial graphics pipeline
4. Execute the initial pipeline once to warm the cache
5. Spawn N threads (same count logic as compute variant)
6. Each thread iterates `EXECUTION_PER_THREAD` times:
   - Creates a graphics pipeline from the shared pipeline cache
   - Executes the pipeline via a render pass with a 1x1 color attachment
   - Verifies the output buffer contents
7. All threads run concurrently using a [`de::SpinBarrier`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L637)

**Verification**: Each thread checks that the output buffer contains the expected values (0, 1, 2, ..., 15) after pipeline execution.

**Additional requirement**: `FEATURE_VERTEX_PIPELINE_STORES_AND_ATOMICS` must be supported.

## Parameter Dimensions

This file has minimal parameterization compared to other synchronization test files. The main dimensions are:

### Pipeline Type

| Test | Pipeline Bind Point | Queue Flag |
|------|---------------------|------------|
| `pipeline_cache_compute` | `VK_PIPELINE_BIND_POINT_COMPUTE` | `VK_QUEUE_COMPUTE_BIT` |
| `pipeline_cache_graphics` | `VK_PIPELINE_BIND_POINT_GRAPHICS` | `VK_QUEUE_GRAPHICS_BIT` |

### Thread Count

| Platform | Thread Count |
|----------|-------------|
| Non-VulkanSC | `clamp(deGetNumAvailableLogicalCores(), 4, 32)` |
| VulkanSC | 2 |

### Executions Per Thread

| Platform | Count |
|----------|-------|
| Non-VulkanSC | 100 |
| VulkanSC | 10 |

### Shader Variants

Each test uses 3 shader variants that produce the same output through different dispatch patterns. The shader index is selected via `executionNdx % shaderCount`.

## Support / Feature Requirements

| Requirement | Applicable Tests |
|-------------|-----------------|
| `VK_QUEUE_COMPUTE_BIT` queue family | `pipeline_cache_compute` |
| `VK_QUEUE_GRAPHICS_BIT` queue family | `pipeline_cache_graphics` |
| `FEATURE_VERTEX_PIPELINE_STORES_AND_ATOMICS` | `pipeline_cache_graphics` |

No extensions are required beyond what is needed for basic Vulkan operation.

## Verification Methods

- **Buffer content comparison**: After each pipeline execution, the output storage buffer is mapped and each element is compared against its expected value (element at index N should equal N).
- **Result collection**: Each thread collects results in a [`ResultCollector`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L576). The [`ThreadGroup`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L637) aggregates results from all threads and returns a combined pass/fail status.

## Test Principles

- **Internal synchronization**: The Vulkan specification states that `VkPipelineCache` is internally synchronized. These tests verify that concurrent `vkCreateComputePipelines` / `vkCreateGraphicsPipelines` calls using the same pipeline cache from different threads produce correct results without explicit application-level synchronization on the cache object.
- **Thread group pattern**: The [`ThreadGroup`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L637) class manages a collection of [`ThreadGroupThread`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L556) instances, using a [`de::SpinBarrier`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L637) to synchronize thread startup.
- **Multi-queue device**: A custom device is created with all queue families and all available queues per family, enabling true concurrent execution across multiple queues. The [`MultiQueues`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L98) class manages queue allocation and release with mutex protection.
- **Pipeline cache sharing**: All threads share the same `VkPipelineCache` object, exercising the internally synchronized path. The cache is pre-warmed with an initial pipeline creation to ensure cache hits occur during concurrent access.
- **Vulkan SC considerations**: Thread count and execution count are reduced for Vulkan SC. Pipeline cache creation uses read-only flags with application storage. A [`MultithreadedDestroyGuard`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L781) is used for SC device destruction.

## Notes / Uncertainties

- This test group is LEGACY-only and does not appear in the `synchronization2` category. The synchronization2 category has a separate `internally_synchronized_queues` group from [`vktSynchronizationInternallySynchronizedTests.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedTests.cpp#L1) which tests a different aspect of internal synchronization.
- The test creates a custom device rather than using the context device, because it needs access to all available queues across all queue families. This custom device is created via [`createCustomDevice()`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L344).
- The [`MultiQueues`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L98) class uses a mutex to protect queue availability tracking, but the pipeline cache itself is accessed without any application-level synchronization -- this is the behavior being tested.
- The `checkQueueFlags()` helper considers `VK_QUEUE_GRAPHICS_BIT` and `VK_QUEUE_COMPUTE_BIT` queues as implicitly supporting `VK_QUEUE_TRANSFER_BIT`, following the Vulkan specification.
- The buffer element count (16) and buffer size (64 bytes) are fixed constants defined at the top of the anonymous namespace.
