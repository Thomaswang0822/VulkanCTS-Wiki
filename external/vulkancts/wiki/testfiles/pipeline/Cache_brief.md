# Understanding Brief: Pipeline Cache

## One-Sentence Test Purpose

The `pipeline` test category checks whether Vulkan pipeline caches can be created, reused, merged, serialized, validated, and accessed concurrently across graphics and compute pipeline construction paths.

## Background Knowledge

A `VkPipelineCache` stores implementation-defined data that can accelerate later pipeline creation. Applications can export that data with `vkGetPipelineCacheData`, use it as `pInitialData` when creating another cache, and combine source caches with `vkMergePipelineCaches`. The exported blob is opaque, so the test can validate API behavior and resulting pipeline behavior without interpreting its internal contents.

Pipeline-cache entries are useful only when the implementation can match them to the requested pipeline. The graphics tests therefore create a reference pipeline and a second pipeline using the same cache, while the miss variants alter shader arithmetic by `+ 0.1` so the test exercises a distinct pipeline key.

## One Concrete Example

A representative graphics case uses `vertex_stage_fragment_stage`:

1. The test creates an empty `VkPipelineCache` and two equivalent graphics-pipeline descriptions.
2. It creates one pipeline without cache data and one with the same cache.
3. It renders the same overlapping quads into separate 32×32 color images.
4. It copies both images to host-visible buffers and compares the results.

The stage-combination variants add a geometry stage or tessellation control/evaluation stages without changing the cache-reuse question. The `_externally_synchronized` variants set `VK_PIPELINE_CACHE_CREATE_EXTERNALLY_SYNCHRONIZED_BIT`.

## End-to-End Test Flow

```text
[host] choose TestMode::CACHE, PipelineConstructionType, shader stages, and cache flags
[host] create a pipeline cache, render targets, depth resources, vertex data, pipeline layout, and pipeline descriptions
[host] create pipelines with and without the relevant cache/blob data
[host] record render, image-transition, copy, and synchronization commands
[device] execute the graphics or compute pipeline
[host] wait for queue completion and read back cache data or rendered/output-buffer data
[host] compare outputs, check Vulkan return codes, or confirm the expected cache-data status
```

The `internally_synchronized_test` uses two threads. One repeatedly creates compute pipelines, while the other creates local caches, creates compute pipelines, and merges those caches into a global cache created with `VK_PIPELINE_CACHE_CREATE_INTERNALLY_SYNCHRONIZED_MERGE_BIT_KHR`. The test joins both threads, exports and recreates the cache, then creates more pipelines.

## Generated Test Artifacts and Bound Resources

| Resource or artifact | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|---|---:|---:|---:|---:|---|
| Pipeline-cache objects | yes | implementation-defined | used during pipeline creation | cache blob exported | Core object under test |
| Graphics pipeline descriptions | yes | yes | used for rendering | no | Compare creation with and without cache data |
| Vertex buffer | yes | yes | read by vertex stage | no | Supplies overlapping quads |
| Color images and depth image | yes | yes | written by rendering | yes | Result comparison for graphics cases |
| Storage buffers | yes | yes | compute shader reads/writes | yes, for the synchronized case's setup | Result and concurrent compute-pipeline setup |
| Opaque cache blobs | yes, from `vkGetPipelineCacheData` | passed to Vulkan | consumed during cache/pipeline creation | yes | Exercise serialization and incomplete-data handling |

The shaders are small fixtures used to construct and execute graphics or compute pipelines. Their arithmetic is not the primary subject; the cache behavior is.

## What Is Checked

- Graphics cases compare the rendered output from pipelines created without and with the tested cache data.
- `pipeline_from_get_data` creates a pipeline from a complete blob returned by `vkGetPipelineCacheData` and checks the resulting rendering.
- `pipeline_from_incomplete_get_data` truncates the exported data by one byte and requires `vkGetPipelineCacheData` to return `VK_INCOMPLETE`; it then creates a cache from that incomplete blob and compares pipeline output.
- Merge cases build empty, data-initialized, hit, miss, miss-and-hit, or already-merged caches, merge one or two source caches, and exercise the merged cache through pipeline creation.
- Miscellaneous cases check cache-header validity, invalid sizes, zero-size data, invalid blobs, and internally synchronized access.

## Behavior Parameter Identification

> **Behavior parameter:** cache operation family
>
> **Candidate values:** `graphics_tests`, `pipeline_from_get_data`, `pipeline_from_incomplete_get_data`, `compute_tests`, `merge`, `misc_tests`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `graphics_tests` | Cache-backed graphics pipeline creation does not preserve the required rendering result, or cache flags affect valid use incorrectly. |
| `pipeline_from_get_data` | Complete cache serialization or reuse is mishandled. |
| `pipeline_from_incomplete_get_data` | The implementation mishandles truncated cache data or returns the wrong `vkGetPipelineCacheData` status. |
| `compute_tests` | Cache-backed compute pipeline creation or repeated compute-pipeline use is mishandled. |
| `merge` | Cache initialization, cache-entry merging, or merged-cache pipeline lookup is mishandled. |
| `misc_tests` | Cache-header parsing, size/error handling, or the internally synchronized merge contract is mishandled. |

## Important Variations and Special Cases

- `graphics_tests`, `pipeline_from_get_data`, and `pipeline_from_incomplete_get_data` cover vertex+fragment, vertex+geometry+fragment, and vertex+tessellation+fragment stages.
- `compute_tests` is registered only for `PIPELINE_CONSTRUCTION_TYPE_MONOLITHIC`; its cache variant registers `compute_stage`.
- `pipeline_from_incomplete_get_data`, `merge`, and `misc_tests` are cache-mode tests and do not repeat in pipeline-binary mode.
- Geometry and tessellation cases are skipped when the required core features are unavailable. `internally_synchronized_test` requires `VK_KHR_maintenance8`.
- The original source comment excludes the cache tests from Vulkan SC through the `CTS_USES_VULKANSC` guard.

## Source Mapping

| Topic | Source link | Why it matters |
|---|---|---|
| Cache registration and family matrix | [createCacheTests and `createPipelineBlobTestsInternal`](../../../modules/vulkan/pipeline/vktPipelineCacheTests.cpp#L2288-L2458) | Defines the cache root, direct test families, construction-type gating, and stage combinations |
| Base cache setup and submit/check flow | [`BaseTestInstance`](../../../modules/vulkan/pipeline/vktPipelineCacheTests.cpp#L243-L323) | Creates the cache and establishes the common execution sequence |
| Graphics cache comparison | [`GraphicsTestInstance`](../../../modules/vulkan/pipeline/vktPipelineCacheTests.cpp#L340-L1100) | Builds the two graphics pipelines and compares their results |
| Incomplete cache blob | [`PipelineFromIncompleteBlobsTestInstance`](../../../modules/vulkan/pipeline/vktPipelineCacheTests.cpp#L1373-L1439) | Produces and consumes truncated cache data |
| Cache merging | [`MergeBlobsTestInstance`](../../../modules/vulkan/pipeline/vktPipelineCacheTests.cpp#L1492-L1710) | Builds source/destination cache states and calls `vkMergePipelineCaches` |
| Concurrent internal synchronization | [`InternallySynchronizedInstance::iterate`](../../../modules/vulkan/pipeline/vktPipelineCacheTests.cpp#L2075-L2240) | Exercises concurrent creation and merge, then recreates the exported cache |
| Vulkan cache contract | [Pipeline Cache](../../../../vulkan-docs/src/chapters/pipelines.adoc#pipelines-cache) | Defines cache creation, data export, and merge semantics |

## Questions / Risk Points for User Audit

- Does the distinction between a cache-backed pipeline result check and an opaque cache-blob API check remain clear?
- Should the final page include exact per-family mustpass counts for each pipeline construction type?
- Is the role of the `VK_PIPELINE_CACHE_CREATE_INTERNALLY_SYNCHRONIZED_MERGE_BIT_KHR` concurrency case sufficiently explicit?

## Conversion Notes for Final Wiki Rewrite

Distill the concrete example into the final page's runtime and behavior sections. Keep the six direct registered test families in the hierarchy, use cache operation family as the primary behavioral axis, and explain stage combinations and construction-type gating in parameter and pruning sections. Copy the failure-cause table into `Cache.md`; write fresh cause analysis there.
