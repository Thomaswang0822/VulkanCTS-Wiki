## Overview

**Core question:** Can Vulkan reuse, export, merge, validate, and concurrently update pipeline-cache data without changing the behavior of the resulting graphics or compute pipelines?

- `vktPipelineCacheTests.cpp` implements the `cache` test family in the `pipeline` test category.
- The page covers graphics pipeline reuse, pipeline creation from complete and incomplete `vkGetPipelineCacheData` blobs, compute pipeline cache use, cache merging, cache validation errors, and internally synchronized merge access.
- The graphics and compute cases compare two pipelines created through the cache path. The remaining cases check Vulkan return codes, exported header fields, and successful object use for opaque cache-data operations.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- A `VkPipelineCache` stores implementation-defined pipeline data. Applications may export that data with `vkGetPipelineCacheData`, pass it back through `VkPipelineCacheCreateInfo::pInitialData`, and combine caches with `vkMergePipelineCaches`.
- Cache contents are opaque. A valid cache hit does not change the required pipeline result, while invalid or incomplete input must follow the API's defined status and error behavior.
- `VK_PIPELINE_CACHE_CREATE_INTERNALLY_SYNCHRONIZED_MERGE_BIT_KHR` changes the concurrency contract for merge operations. This page's concurrent case creates pipelines and merges another cache into one shared cache from separate threads.

## Registration Hierarchy

```text
pipeline.monolithic.cache
├── graphics_tests
├── pipeline_from_get_data
├── pipeline_from_incomplete_get_data
├── compute_tests
├── merge
└── misc_tests
```

The source file implements all six direct intermediate nodes. The monolithic construction path adds `compute_tests` and `internally_synchronized_test`; the incomplete-data, merge, and miscellaneous intermediate nodes are cache-mode-specific. Equivalent cache roots under the other pipeline construction types register the graphics, complete-data, incomplete-data, merge, and miscellaneous coverage documented below.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Pipeline construction type | `PIPELINE_CONSTRUCTION_TYPE_MONOLITHIC`, other supported construction types | Selects the pipeline-construction wrapper used by the cache-backed pipeline. Compute cache tests and `internally_synchronized_test` are limited to the monolithic path. | [`createPipelineBlobTestsInternal`](../../../modules/vulkan/pipeline/vktPipelineCacheTests.cpp#L2288-L2458) |
| Shader-stage combination | `vertex_stage_fragment_stage`, `vertex_stage_geometry_stage_fragment_stage`, `vertex_stage_tessellation_control_stage_tessellation_evaluation_stage_fragment_stage`, `compute_stage` | Changes the graphics pipeline stage chain or selects compute pipeline creation. | [`getShaderFlagStr`](../../../modules/vulkan/pipeline/vktPipelineCacheTests.cpp#L66-L85), [registration matrix](../../../modules/vulkan/pipeline/vktPipelineCacheTests.cpp#L2292-L2373) |
| Cache operation family | `graphics_tests`, `pipeline_from_get_data`, `pipeline_from_incomplete_get_data`, `compute_tests`, `merge`, `misc_tests` | Selects the cache contract under test. | [cache registration](../../../modules/vulkan/pipeline/vktPipelineCacheTests.cpp#L2297-L2450) |
| Cache creation flags | `0`, `VK_PIPELINE_CACHE_CREATE_EXTERNALLY_SYNCHRONIZED_BIT`, `VK_PIPELINE_CACHE_CREATE_INTERNALLY_SYNCHRONIZED_MERGE_BIT_KHR` | Exercises ordinary cache access, externally synchronized graphics cases, and the concurrent merge case. | [`TestParam`](../../../modules/vulkan/pipeline/vktPipelineCacheTests.cpp#L88-L156), [`InternallySynchronizedInstance::iterate`](../../../modules/vulkan/pipeline/vktPipelineCacheTests.cpp#L2143-L2240) |
| Cache blob state | `empty`, `from_data`, `hit`, `miss`, `misshit`, `merged`, incomplete, invalid, zero-size | Selects the initial contents and expected cache-data behavior for merge and validation cases. | [`MergeBlobsType`](../../../modules/vulkan/pipeline/vktPipelineCacheTests.cpp#L1441-L1483), [`MergeBlobsTestInstance::createPipelineCache`](../../../modules/vulkan/pipeline/vktPipelineCacheTests.cpp#L1571-L1710) |

## Behavior Parameters

The primary behavioral axis is the direct registered test family. Each family tests a different cache operation or contract.

### `graphics_tests`: cache-backed graphics pipeline reuse

The test creates both graphics pipelines sequentially with the same initially empty cache. The first creation can populate the cache and the second can reuse it. It renders overlapping quads through the resulting pipelines and compares the output images. The `_externally_synchronized` variants set `VK_PIPELINE_CACHE_CREATE_EXTERNALLY_SYNCHRONIZED_BIT`; the test itself performs these cache accesses serially, so application-provided external synchronization is not stressed by concurrent calls.

### `pipeline_from_get_data`: pipeline creation from a complete exported blob

Before building either graphics pipeline, the test exports the initially empty cache with `vkGetPipelineCacheData` and creates another cache from the complete returned blob. It then creates one pipeline with the original cache and the comparison pipeline with the imported cache. The three graphics stage combinations check that a complete exported blob can initialize a usable cache and that both pipelines render equivalently; they do not prove that a populated pipeline entry was serialized or reused.

### `pipeline_from_incomplete_get_data`: pipeline creation from truncated cache data

The test requests the cache-data size, subtracts one byte, and requires the data query to return `VK_INCOMPLETE`. It creates a second cache from the truncated bytes and compares pipelines built with the original and incomplete-data caches. This family is registered only for `TestMode::CACHE`.

### `compute_tests`: cache-backed compute pipeline creation

The monolithic path registers `compute_stage`. The compute implementation creates a compute shader, layouts, storage-buffer resources, and two pipelines sequentially with the same cache. It dispatches both pipelines and compares their output buffers byte for byte. This proves equivalence between the two cache-path creations, not correctness against a separately calculated reference. The family is not repeated for non-monolithic construction types.

### `merge`: merging cache contents from one or two source caches

For each graphics stage combination, the source creates a destination cache and one- or two-cache source combinations. Each cache can be empty, initialized from exported data, populated by a pipeline hit, populated by a miss, populated by both, or already merged. It calls `vkMergePipelineCaches` and then uses the resulting destination cache to create pipelines.

### `misc_tests`: cache headers, sizes, invalid blobs, and internal synchronization

The family contains `cache_header_test`, `invalid_size_test`, `zero_size_test`, and `invalid_blob_test`. The invalid-blob case changes individual cache-header fields and verifies that cache creation still succeeds, as invalid initial data is ignored rather than reported as an API error. The monolithic path also registers `internally_synchronized_test`, which runs concurrent pipeline creation and cache merging under `VK_PIPELINE_CACHE_CREATE_INTERNALLY_SYNCHRONIZED_MERGE_BIT_KHR`, exports and recreates the merged cache, and creates more compute pipelines from it.

## Shader Analysis

The shaders provide small graphics and compute workloads so most cases can observe pipelines created through a cache. Shader execution itself is not the primary behavior under test. The graphics variants use vertex, fragment, optional geometry, and optional tessellation shaders; miss variants alter the generated shader expression by `+ 0.1` to select a distinct pipeline description. The `compute_tests` shader squares each input `vec4` into an output storage buffer. The internally synchronized case compiles the same arithmetic shader but only creates pipelines from it; it allocates no storage buffers and records no dispatch.

## Runtime Execution and Result Checking

- Common cache-mode instances create a transient command pool and primary command buffer, then create a `VkPipelineCache` with the selected flags.
- Graphics instances create a 32×32 `VK_FORMAT_R8G8B8A8_UNORM` color target, a `VK_FORMAT_D16_UNORM` depth target, image views, framebuffers, a pipeline layout, and a vertex buffer containing overlapping quads.
- The command buffer transitions the images, begins the render pass, binds each pipeline and its vertex data, draws, and copies the color result into host-visible buffers. After queue completion, the test compares the reference and cache-backed results.
- Complete-blob cases export an initially empty cache, create a new cache with those bytes as initial data, and create one pipeline against each cache. Incomplete-blob cases likewise export the initially empty cache, check the required `VK_INCOMPLETE` status for a buffer one byte too small, and use the returned truncated bytes as initial data.
- Merge cases prepare source caches according to their `MergeBlobsType`, merge them into a destination cache, and exercise the destination through pipeline creation. The source creation path can populate a cache with a hit, a miss, or both before export or merge.
- The internally synchronized case starts `CreatePipelineThread` and `MergePipelineCacheThread`, waits for both, exports the global cache, destroys and recreates it from the blob, then creates two more compute pipelines. It returns pass after these operations complete without an error.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `graphics_tests` | Two sequential graphics-pipeline creations against the same cache produce different rendering, or cache flags affect valid serial use incorrectly. |
| `pipeline_from_get_data` | Exporting an initially empty cache, importing its complete blob, or creating a pipeline against either cache is mishandled. |
| `pipeline_from_incomplete_get_data` | The implementation mishandles truncated cache data or returns the wrong `vkGetPipelineCacheData` status. |
| `compute_tests` | Two sequential compute-pipeline creations against the same cache produce different buffer results. |
| `merge` | Cache initialization, cache-entry merging, or merged-cache pipeline lookup is mishandled. |
| `misc_tests` | Exported cache-header fields, size/status handling, required acceptance of zero-size or invalid initial data, or the internally synchronized merge contract is mishandled. |

### Cause Analysis

#### Cache lookup or reuse does not preserve pipeline behavior

**Possible failure symptoms:** A graphics image comparison differs between the reference pipeline and the cache-backed pipeline, or a compute result does not match the expected output.

**Possible implementation causes:** The implementation may associate cache data with the wrong pipeline state or shader-stage combination, fail to reuse compatible entries correctly, or produce different executable behavior when it uses a cache entry. The exact cause requires driver/compiler investigation beyond the CTS result comparison.

#### Cache data export, import, or incomplete-data handling fails

**Possible failure symptoms:** `vkGetPipelineCacheData` returns an unexpected status, a cache created from complete or truncated bytes cannot be used as required, or a complete-blob pipeline result differs from the reference.

**Possible implementation causes:** The implementation may mishandle the size/data-query sequence, serialize data that it cannot consume, reject a permitted incomplete blob incorrectly, or parse the blob with an incorrect boundary. The opaque blob format prevents the CTS from localizing the internal parsing defect.

#### Cache merge loses or corrupts entries

**Possible failure symptoms:** A merge operation returns an error, a merged cache cannot create the expected pipeline, or a pipeline created from the merged destination produces a different result.

**Possible implementation causes:** The implementation may mishandle source-cache state, fail to combine compatible entries, or use stale or incompatible metadata after `vkMergePipelineCaches`. The test does not inspect cache internals, so source-level and implementation-level investigation is needed to distinguish these cases.

#### Cache validation and error handling are incorrect

**Possible failure symptoms:** `cache_header_test` observes incorrect exported header fields; `invalid_size_test` gets the wrong `VK_INCOMPLETE`, byte-count, or write behavior; or cache creation fails for the zero-size and deliberately invalid initial-data cases.

**Possible implementation causes:** The implementation may emit incorrect header metadata, mishandle a too-small destination buffer, read initial data when `initialDataSize` is zero, or fail to ignore initial data whose header version, vendor ID, device ID, or UUID is incompatible. These cases do not require `vkCreatePipelineCache` to report a validation error for incompatible initial data; successful creation is the tested behavior.

#### Internally synchronized merge access is unsafe

**Possible failure symptoms:** The two-thread test reports a Vulkan error, fails to complete, cannot export or recreate the shared cache, or cannot create a pipeline from the recreated cache.

**Possible implementation causes:** The implementation may fail to synchronize concurrent pipeline creation and merge operations under `VK_PIPELINE_CACHE_CREATE_INTERNALLY_SYNCHRONIZED_MERGE_BIT_KHR`, corrupt shared cache state, or mishandle cache data after concurrent updates. The CTS joins both threads and checks later cache use, but it cannot identify which internal operation caused corruption.

## Case Pruning

### Requirement-based pruning

- Geometry-stage cases require `DEVICE_CORE_FEATURE_GEOMETRY_SHADER`.
- Tessellation-stage cases require `DEVICE_CORE_FEATURE_TESSELLATION_SHADER`.
- The construction wrapper must satisfy `checkPipelineConstructionRequirements` for the selected `PipelineConstructionType`.
- `internally_synchronized_test` requires `VK_KHR_maintenance8`.
- Pipeline-cache tests are excluded for Vulkan SC by the source's `CTS_USES_VULKANSC` guard.

### Design-based pruning

- The cache-specific families `pipeline_from_incomplete_get_data`, `merge`, and `misc_tests` are omitted when the shared helper is building pipeline-binary tests.
- `compute_tests` is not repeated for graphics pipeline library construction types because the source explicitly restricts it to `PIPELINE_CONSTRUCTION_TYPE_MONOLITHIC`.
- The graphics stage matrix uses three representative stage chains rather than every possible shader-stage combination. The externally synchronized flag is paired with the same graphics cases instead of creating a separate family.
- Merge cases cover one and two source caches over the six cache-state values, which exercises source-count behavior without an unbounded number of cache combinations.

## Key Takeaways

- The page tests the pipeline-cache API around pipeline creation, not a particular cache-file format or shader algorithm.
- Graphics results provide an observable equivalence check between two cache-path pipeline creations; the ordinary graphics case passes the same cache to both.
- Export/import and merge cases treat cache bytes as opaque and validate behavior through API status and subsequent pipeline use. The complete and incomplete export cases obtain their bytes before populating the source cache with a graphics pipeline.
- The incomplete-data case checks the size/data-query contract before attempting to consume the truncated blob.
- The internal-synchronization case combines concurrent pipeline creation and cache merging with later cache export, recreation, and use.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `TestParam` and generated test names | [`TestParam`](../../../modules/vulkan/pipeline/vktPipelineCacheTests.cpp#L88-L156) | Defines mode, construction type, shader-stage flags, cache flags, and case-name suffixes |
| Common cache creation and execution | [`BaseTestInstance`](../../../modules/vulkan/pipeline/vktPipelineCacheTests.cpp#L243-L323) | Creates the cache and submits the command buffer |
| Graphics setup and result comparison | [`GraphicsTestInstance`](../../../modules/vulkan/pipeline/vktPipelineCacheTests.cpp#L340-L1100) | Shows resources, pipeline construction, rendering, copyback, and comparison |
| Complete cache data | [`PipelineFromBlobsTestInstance`](../../../modules/vulkan/pipeline/vktPipelineCacheTests.cpp#L1170-L1370) | Exports a complete cache blob and builds a pipeline from it |
| Incomplete cache data | [`PipelineFromIncompleteBlobsTestInstance`](../../../modules/vulkan/pipeline/vktPipelineCacheTests.cpp#L1373-L1439) | Checks `VK_INCOMPLETE` and creates a cache from truncated data |
| Cache-state construction and merge | [`MergeBlobsTestInstance`](../../../modules/vulkan/pipeline/vktPipelineCacheTests.cpp#L1492-L1710) | Covers cache source states and `vkMergePipelineCaches` |
| Cache validation tests | [`CacheHeaderTest`, `InvalidSizeTest`, `ZeroSizeTest`, and `InvalidBlobTest`](../../../modules/vulkan/pipeline/vktPipelineCacheTests.cpp#L1710-L2040) | Exercises malformed headers, sizes, zero-size data, and invalid blobs |
| Concurrent cache access | [`InternallySynchronizedInstance::iterate`](../../../modules/vulkan/pipeline/vktPipelineCacheTests.cpp#L2143-L2240) | Runs concurrent creation and merge, then recreates and uses the cache |
| Registration | [`createCacheTests`](../../../modules/vulkan/pipeline/vktPipelineCacheTests.cpp#L2288-L2458) | Defines the direct `pipeline.cache` test-family tree and gating |
| Vulkan cache specification | [Pipeline Cache](../../../../vulkan-docs/src/chapters/pipelines.adoc#pipelines-cache) | Provides the normative cache creation, data, and merge contract |
