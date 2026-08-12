# [vktSynchronizationInternallySynchronizedObjectsTests.cpp](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L1)

## Brief

Legacy synchronization tests for concurrent use of the internally synchronized `VkPipelineCache` object. Multiple threads create pipelines from one shared cache while independently executing those pipelines on queues selected from a custom device. Worker executions write the sequence `0..15` to a host-visible storage buffer and validate the result.

The factory creates the legacy group `synchronization.internally_synchronized_objects`. This page describes the legacy group and must not be confused with the different sync2-only `internally_synchronized_queues` tests in [vktSynchronizationInternallySynchronizedTests.cpp](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedTests.cpp#L1).

## Contract

| Item | Contract |
|---|---|
| Legacy test group | `synchronization.internally_synchronized_objects` |
| Cases | `pipeline_cache_compute`, `pipeline_cache_graphics` |
| Object under test | One `VkPipelineCache` shared by all worker threads |
| Concurrency | Each worker calls pipeline creation with the shared cache without an application mutex, then executes the result |
| Queue setup | Custom device exposing every queue in every family matching the requested queue flags; queue allocation/release is protected by `MultiQueues`' mutex |
| Worker count | Non-SC: `clamp(deGetNumAvailableLogicalCores(), 4u, 32u)`; Vulkan SC: `2` |
| Executions per worker | Non-SC: `100`; Vulkan SC: `10` |
| Output | 16 `int32` values in a host-visible storage buffer; expected value at index `n` is `n` |
| Result | Any pipeline or execution error or worker exception fails the case; each worker execution also fails on a buffer mismatch. The preliminary execution's returned status is not checked |

## Registration

```text
synchronization
└── internally_synchronized_objects
    ├── pipeline_cache_compute
    └── pipeline_cache_graphics
```

[`createInternallySynchronizedObjects()`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L1351) adds exactly these two cases and has no `SynchronizationType` parameter. The group is not registered under `synchronization2`.

## Test cases

### `pipeline_cache_compute`

`PipelineCacheComputeTest::checkSupport()` requires a queue family supporting `VK_QUEUE_COMPUTE_BIT`. The instance creates three compute shader/pipeline variants, all writing `0..15` to the storage buffer:

| Shader | Dispatch | Write strategy |
|---|---:|---|
| `compute_0` | 16 workgroups, local size 1 | `gl_GlobalInvocationID.x` |
| `compute_1` | 1 workgroup, local size 1 | One invocation loops over all 16 elements |
| `compute_2` | 1 workgroup, local size 16 | `gl_LocalInvocationID.x` |

The test creates a compute pipeline layout, descriptor set layout, storage buffer, and shared pipeline cache. It creates and executes the first pipeline before starting the workers. Each worker repeats the following `EXECUTION_PER_THREAD` times, selecting `compute_(executionNdx % 3)`:

1. Create a compute pipeline using the shared `VkPipelineCache`.
2. Acquire an available compute-capable queue and command buffer.
3. Bind the pipeline and storage-buffer descriptor, dispatch the variant, and wait for completion.
4. Release the queue and compare all 16 mapped buffer elements with their indices.

### `pipeline_cache_graphics`

`PipelineCacheGraphicTest::checkSupport()` requires a graphics-capable queue family and `FEATURE_VERTEX_PIPELINE_STORES_AND_ATOMICS`. The instance creates three vertex shader/pipeline variants plus a fragment shader. Each variant writes `0..15` to the storage buffer; the fragment shader outputs white.

| Shader | Draw count | Write strategy |
|---|---:|---|
| `vert_0` | 16 points | `gl_VertexIndex` |
| `vert_1` | 1 point | One vertex invocation loops over all 16 elements |
| `vert_2` | 1 point | One vertex invocation writes the elements in reverse loop order |

The test creates a 1x1 render pass, graphics pipeline layout, descriptor set layout, and shared pipeline cache; each execution creates its own framebuffer and storage buffer. It warms the cache by creating and executing the first graphics pipeline. Each worker repeats the following `EXECUTION_PER_THREAD` times, selecting `vert_(executionNdx % 3)`:

1. Create a graphics pipeline using the shared `VkPipelineCache`.
2. Acquire an available graphics-capable queue and command buffer.
3. Render the variant's point count through the 1x1 render pass, with a barrier making storage-buffer writes visible to the host.
4. Wait for completion, release the queue, and compare all 16 mapped buffer elements with their indices.

## Execution and synchronization model

`PipelineCacheComputeTestInstance::iterate()` and `PipelineCacheGraphicTestInstance::iterate()` create a custom instance/device and collect all queues in families matching the case's queue flag. `MultiQueues` tracks queue availability and owns one resettable command pool per queue. Its mutex protects only queue bookkeeping and command-buffer ownership; it does not protect the pipeline cache.

`ThreadGroup` starts and joins all `ThreadGroupThread` workers and combines their `tcu::ResultCollector` results. Its `de::SpinBarrier` provides the per-iteration synchronization used for Vulkan SC pipeline-pool reservation; it is not an initial start barrier. Worker exceptions are converted to failures. On Vulkan SC, pipeline-cache creation uses read-only/application-storage cache data and the implementation includes the required `MultithreadedDestroyGuard`.

The test therefore stresses concurrent pipeline-cache access while retaining the synchronization needed for unrelated resources: queue allocation, command execution completion, host visibility, and SC resource accounting.

## Validation

A conforming run should satisfy all of the following:

- The requested queue family exists; otherwise `checkSupport()` reports `NotSupportedError`.
- Every worker can repeatedly create a pipeline from the same cache without a cache-access failure.
- Worker compute dispatches and graphics draws complete successfully; the preliminary warm-up execution's returned status is discarded by `iterate()`.
- After each worker execution, the mapped storage buffer contains exactly `0, 1, 2, ..., 15`. The preliminary execution performs the same comparison, but `iterate()` currently discards its returned `TestStatus`.
- `ThreadGroup::run()` returns the aggregate pass result after all workers join.

The fixed buffer constants are `BUFFER_ELEMENT_COUNT = 16` and `BUFFER_SIZE = 64` bytes. No extension is explicitly enabled by this source beyond the requirements of the basic Vulkan context; graphics additionally checks `FEATURE_VERTEX_PIPELINE_STORES_AND_ATOMICS`.

## Source map

| Symbol | Purpose |
|---|---|
| [`MultiQueues`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L98) | Collects queues and serializes queue allocation/release bookkeeping |
| [`createQueues()`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L241) | Builds the custom device and queue pools |
| [`ThreadGroup`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L636) | Starts, joins, and aggregates worker threads |
| [`CreateComputeThread`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L677) | Repeated shared-cache compute pipeline creation/execution |
| [`CreateGraphicThread`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L720) | Repeated shared-cache graphics pipeline creation/execution |
| [`PipelineCacheComputeTest`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L1182) | Support check and compute shader setup |
| [`PipelineCacheGraphicTest`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L1256) | Support check and graphics shader setup |
| [`createInternallySynchronizedObjects()`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L1351) | Registers the two legacy cases |

## Header

The public declaration is in [vktSynchronizationInternallySynchronizedObjectsTests.hpp](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.hpp#L1).
