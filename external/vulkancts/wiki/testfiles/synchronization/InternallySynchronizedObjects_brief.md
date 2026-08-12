# Understanding Brief: `synchronization.internally_synchronized_objects`

## One-Sentence Test Purpose

This test checks whether a single `VkPipelineCache` correctly supports concurrent pipeline creation from multiple host threads while the resulting compute or graphics pipelines execute correctly.

## Background Knowledge

### Vulkan host threading and internally synchronized objects

Vulkan commands may be called concurrently from multiple host threads, but parameters marked externally synchronized require the application to serialize access. Parameters that are not externally synchronized are either not mutated by the command or are internally synchronized ([Vulkan Threading Behavior](../../../../vulkan-docs/src/chapters/fundamentals.adoc#fundamentals-threadingbehavior)). The distinction matters here: worker threads share one `VkPipelineCache` when creating pipelines, while the test separately protects queue allocation and command-buffer ownership with its own mutex.

### A pipeline cache is shared pipeline-creation state

A `VkPipelineCache` is an opaque object used by pipeline-creation commands to reuse implementation-defined data; it is not the storage buffer written by the shaders. The test deliberately shares one cache between workers, but gives each execution its own pipeline and result resources. The Vulkan specification describes the object and its creation parameters in [Pipeline Cache Objects](../../../../vulkan-docs/src/chapters/pipelines.adoc#pipelines-pipeline-cache).

## One Concrete Example

Consider one `pipeline_cache_compute` iteration. A worker selects `compute_0`, which has a local workgroup size of `1`. The host creates a compute pipeline using the shared `VkPipelineCache`, acquires an available compute queue, and dispatches `16` workgroups. Each invocation uses `gl_GlobalInvocationID.x` as an index and writes that index to the storage buffer:

```glsl
// Conceptual reconstruction of the source-generated shader.
layout(local_size_x = 1, local_size_y = 1, local_size_z = 1) in;
layout(set = 0, binding = 0, std430) buffer Output { int result[]; } sb_out;

void main() {
    uint ndx = gl_GlobalInvocationID.x;
    sb_out.result[ndx] = int(ndx);
}
```

This produces `0, 1, ..., 15`. `compute_1` produces the same sequence with one invocation looping over all elements, and `compute_2` produces it with one workgroup of `16` local invocations. The graphics family has the same three output-producing patterns in vertex shaders, with a fragment shader that only writes a white color.

## End-to-End Test Flow

1. `[host]` Create a custom instance and logical device, selecting all queue families and queues that support the requested queue flag (`VK_QUEUE_COMPUTE_BIT` or `VK_QUEUE_GRAPHICS_BIT`).
2. `[host]` Create queue-specific command pools, a descriptor-set layout for one storage-buffer binding, a pipeline layout, shader modules, and pipeline-create-info variants.
3. `[host]` Create one shared `VkPipelineCache` and create one initial pipeline from it. Execute this pipeline once as a warm-up; the returned warm-up status is not used by `iterate()`.
4. `[host]` Choose `clamp(deGetNumAvailableLogicalCores(), 4u, 32u)` worker threads for ordinary Vulkan, or `2` workers for Vulkan SC. Give every worker the same pipeline cache and pipeline descriptions.
5. `[host]` Each worker repeats `100` executions for ordinary Vulkan or `10` for Vulkan SC. On each iteration it selects a shader/pipeline variant by `executionNdx % 3`, creates the pipeline using the shared cache without an application mutex around the cache, and acquires an available queue.
6. `[device]` Execute the compute dispatch or graphics draw. The shader writes the expected sequence to a host-visible storage buffer. The graphics path also renders to a separate `1x1` color attachment; its color is not the pass/fail payload.
7. `[host]` A pipeline barrier makes storage-buffer shader writes visible to host reads, the submission is waited on, and the queue is released. The host invalidates/maps the result allocation and checks all `16` elements.
8. `[host]` Each worker records failure for pipeline/execution errors, exceptions, or any element whose value is not its index. `ThreadGroup` joins all workers and aggregates their `ResultCollector` results; the test passes only when the aggregate result passes.

The queue mutex and the command-completion wait synchronize unrelated resources. They do not serialize the shared pipeline-cache argument, which is the behavior under test.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- Three compute GLSL programs, `compute_0`, `compute_1`, and `compute_2`, differ only in how the same `0..15` result is generated; their dispatch counts are `16`, `1`, and `1` respectively.
- Three vertex GLSL programs, `vert_0`, `vert_1`, and `vert_2`, use `gl_VertexIndex`, a forward loop, and a reverse loop respectively; their draw counts are `16`, `1`, and `1`.
- The graphics family also loads `frag`, which writes `vec4(1.0)` to the color output. The fragment output is supporting render-pass behavior, not the result comparison.
- The host creates pipeline descriptions for each variant and repeatedly passes them to pipeline creation with the shared cache. In Vulkan SC, cache creation uses `VK_PIPELINE_CACHE_CREATE_READ_ONLY_BIT | VK_PIPELINE_CACHE_CREATE_USE_APPLICATION_STORAGE_BIT` with the resource-interface cache data.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Shared `VkPipelineCache` | yes | passed to pipeline creation, not shader-bound | used by implementation during pipeline creation | no | Concurrently accessed object under test |
| Host-visible storage `Buffer` | yes | descriptor binding `0` | shader writes `16` `int32` values | yes | Observable correctness payload |
| Descriptor set and pipeline layout | yes | yes | enables storage-buffer access | no | Connects each shader to the result buffer |
| Graphics `1x1` color attachment and view | yes | framebuffer attachment | fragment shader writes white | no | Completes the graphics pipeline path; not the checked sequence |
| Queue command pools and command buffers | yes | submitted to selected queues | execute dispatch/draw and barrier | no | Per-queue execution state; queue bookkeeping is mutex-protected |

The shared cache is not a GPU buffer and the storage buffer is not shared between worker executions: each `executeComputePipeline()` or `executeGraphicPipeline()` creates its own result buffer.

## What Is Checked

- Support checks require a queue family with `VK_QUEUE_COMPUTE_BIT` for `pipeline_cache_compute`, or `VK_QUEUE_GRAPHICS_BIT` for `pipeline_cache_graphics`.
- The graphics family additionally requires `FEATURE_VERTEX_PIPELINE_STORES_AND_ATOMICS`.
- After each worker execution, the host checks every result element: element `n` must contain exactly `n` for `n = 0..15`.
- A pipeline-creation error, queue/command execution error, worker exception, or result mismatch contributes a failure. The worker results are aggregated after all threads join.
- The fixed payload is `16` `int32` values (`64` bytes). The shader output is made host-visible with a storage-buffer-to-host pipeline barrier and host allocation invalidation before inspection.

## Behavior Parameter Identification

> **Behavior parameter:** test family
>
> **Candidate values:** `pipeline_cache_compute`, `pipeline_cache_graphics`

These two registered test families are the primary behavioral axis: they exercise the same shared-cache concurrency contract through different pipeline bind points, shader stages, queue requirements, and execution setup.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `pipeline_cache_compute` | Incorrect concurrent handling of the shared `VkPipelineCache` during compute-pipeline creation; compute pipeline compilation or dispatch failure; storage-buffer visibility or result-production failure; host-side result-checking or queue-management failure. |
| `pipeline_cache_graphics` | Incorrect concurrent handling of the shared `VkPipelineCache` during graphics-pipeline creation; graphics pipeline, render-pass, or vertex-pipeline execution failure; storage-buffer visibility or result-production failure; missing required vertex-pipeline stores/atomics support; host-side result-checking or queue-management failure. |

## Important Variations and Special Cases

- The two families differ by queue and pipeline type, not by the object-synchronization claim: both pass the same `VkPipelineCache` handle to all worker threads.
- Each family cycles through three equivalent result-producing shader variants. This changes invocation and loop structure while keeping the expected host-visible sequence fixed.
- Ordinary Vulkan uses a logical-core-dependent worker count clamped to `4..32` and `100` iterations per worker. Vulkan SC uses `2` workers and `10` iterations, with additional pipeline-pool reservation synchronization and multithreaded-destruction handling.
- The `de::SpinBarrier` is used for the Vulkan SC pipeline-pool reservation path; the `MultiQueues` mutex protects queue availability bookkeeping, not pipeline-cache access.
- The factory has no `SynchronizationType` parameter and is called only for the legacy `synchronization` category. It must not be conflated with sync2's separate `internally_synchronized_queues` group.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Queue collection and protected bookkeeping | [`MultiQueues`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L98-L239) | Shows how all suitable queues are made available and why the mutex is not the cache lock. |
| Custom device and queue setup | [`createQueues()`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L241-L353) | Establishes the concurrent execution resources. |
| Per-execution compute result and host check | [`executeComputePipeline()`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L371-L453) | Shows storage-buffer initialization, dispatch, barrier, wait, and `0..15` validation. |
| Per-execution graphics result and host check | [`executeGraphicPipeline()`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L455-L553) | Shows the graphics render pass, draw, barrier, wait, and validation. |
| Worker aggregation | [`ThreadGroup`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L555-L675) | Converts worker outcomes and exceptions into one case result. |
| Shared-cache worker creation | [`CreateComputeThread::runThread()`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L677-L718), [`CreateGraphicThread::runThread()`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L720-L763) | Shows repeated cache-sharing and variant selection. |
| Compute instance and worker count | [`PipelineCacheComputeTestInstance::iterate()`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L765-L838) | Creates the shared cache and launches concurrent compute workers. |
| Graphics instance and worker count | [`PipelineCacheGraphicTestInstance::iterate()`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L898-L970) | Creates the shared cache and launches concurrent graphics workers. |
| Family shader variants and support checks | [`PipelineCacheComputeTest`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L1182-L1254), [`PipelineCacheGraphicTest`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L1256-L1347) | Defines the registered variants, dispatch/draw counts, and feature requirements. |
| Legacy registration | [`createInternallySynchronizedObjects()`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L1351-L1360) | Registers exactly the two legacy test families. |
| Legacy mustpass coverage | [`synchronization.txt`](../../../../vulkancts/mustpass/main/vk-default/synchronization.txt) | Lists both legacy test case leaves. |
| Vulkan threading semantics | [Threading Behavior](../../../../vulkan-docs/src/chapters/fundamentals.adoc#fundamentals-threadingbehavior) | Defines external versus internal synchronization. |
| Pipeline-cache semantics | [Pipeline Cache Objects](../../../../vulkan-docs/src/chapters/pipelines.adoc#pipelines-pipeline-cache) | Defines `VkPipelineCache` and its use in pipeline creation. |

## Questions / Risk Points for User Audit

- Is the distinction between the shared internally synchronized cache and the separately mutex-protected queue bookkeeping clear?
- Is it clear that the storage buffer is per execution and that only its `0..15` contents are validated?
- Should the final page retain the Vulkan SC-specific barrier and reservation details, or reduce them to a concise special-case note?
- Is the legacy-only scope sufficiently explicit to prevent confusion with `internally_synchronized_queues` under `synchronization2`?
- Should the discarded warm-up `TestStatus` be called out in the final page's validation discussion?

## Conversion Notes for Final Wiki Rewrite

- Use the two test families as the primary behavior parameter and preserve the failure-cause table unchanged in the final page.
- Keep one representative concrete walkthrough, preferably `pipeline_cache_compute` with `compute_0`; summarize the equivalent loop/local-invocation variants in a parameter table.
- Distill the Background Knowledge to Vulkan host-thread synchronization and the distinction between a pipeline cache and the result buffer; do not copy the tutorial scaffolding verbatim.
- Preserve the end-to-end timeline and resource table in a more compact formal style. Explain the queue mutex, submission wait, and buffer barrier as synchronization for surrounding resources rather than as protection of `VkPipelineCache`.
- Include the exact legacy registration paths and mustpass leaves, and retain a short note that `synchronization2` uses a different internally synchronized-queues family.
- Keep source-navigation links in the final Source Reference Appendix rather than the main narrative.
- Write fresh `### Cause Analysis` during the Level-3 rewrite from the observed `0..15` validation and the Vulkan threading/pipeline-cache semantics.
