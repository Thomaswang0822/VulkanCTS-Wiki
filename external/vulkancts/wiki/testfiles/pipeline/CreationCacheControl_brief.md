# Understanding Brief: Pipeline creation cache control

## One-Sentence Test Purpose

This test checks whether an implementation handles the pipeline-creation cache-control flags correctly when pipeline creation would require compilation.

## Background Knowledge

### Compile-required creation

`VK_PIPELINE_CREATE_FAIL_ON_PIPELINE_COMPILE_REQUIRED_BIT_EXT` asks pipeline creation to fail instead of compiling a valid pipeline when compilation is required. The result may be `VK_ERROR_PIPELINE_COMPILE_REQUIRED_EXT`, and the corresponding pipeline handle is null. The [`pipelineCreationCacheControl` feature](../../../../vulkan-docs/src/chapters/features.adoc#features-pipelineCreationCacheControl) enables use of this behavior.

Why it matters here:
- The test first creates a pipeline where compilation is allowed, then repeats related creation requests with compilation prohibited.
- A null handle can be the expected result for a compile-required request; it is not automatically a CTS failure.

### Early return in a batch

`VK_PIPELINE_CREATE_EARLY_RETURN_ON_FAILURE_BIT_EXT` applies to a multi-pipeline creation call. If one element fails, the API returns control rather than continuing creation of later elements. The [pipeline creation rules](../../../../vulkan-docs/src/chapters/pipelines.adoc#pipelines) specify that pipeline array entries at or after the failing index are null.

Why it matters here:
- The early-return cases check both the API result and the state of later output handles.
- The test treats the specified result and timing as compatibility or quality expectations in several cases, but requires the handle ordering rule when the leading request fails.

## One Concrete Example

Consider `dEQP-VK.pipeline.monolithic.creation_cache_control.compute_pipelines.duplicate_batch_pipelines_explicit_cache`.

The host creates an explicit empty `VkPipelineCache`, then calls `vkCreateComputePipelines` for three otherwise matching compute create infos: no-compile, normal, no-compile. The normal middle entry can compile and must yield a valid pipeline. The first and third entries request no compilation. The test accepts `VK_SUCCESS` or `VK_ERROR_PIPELINE_COMPILE_REQUIRED_EXT`, then classifies the documented cache-dependent results as warnings where implementation caching choices allow either outcome.

## End-to-End Test Flow

```text
[host] require VK_EXT_pipeline_creation_cache_control and pipelineCreationCacheControl
[host] require VK_KHR_maintenance5 for the maintenance5 leaf
[host] choose a graphics or compute test case leaf and its cache mode
[host] create an explicit pipeline cache only for EXPLICIT_CACHE
[host] create pipeline layout, shader modules, and graphics or compute create-info templates
[host] build one or more create infos with normal, no-compile, or early-return flags
[host] call vkCreateGraphicsPipelines or vkCreateComputePipelines and measure elapsed host time
[host] wrap non-null pipeline handles for lifetime management
[host] validate result code, required null or valid handles, early-return ordering, and selected timing bounds
[host] retain the first valid pipeline as a derivative base when the case uses DERIVATIVE_HANDLE
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The source generates simple vertex, fragment, geometry, tessellation, and compute GLSL programs so Vulkan can create representative pipelines. Their rendered or dispatched results are not read. The test observes pipeline-creation results, output handles, and elapsed time.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `VkPipelineCache` | for `EXPLICIT_CACHE` only | passed to pipeline creation | implementation-defined cache use | no | separates explicit-cache behavior from null-cache and derivative cases |
| `VkPipeline` output array | yes | returned by creation call | no rendering or dispatch required | yes | validators check which entries are valid or null |
| shader modules and pipeline layouts | yes | referenced by create infos | compilation inputs | no | make the requested pipeline creation valid apart from the cache-control condition |

## What Is Checked

- `validateResults()` rejects results other than `VK_SUCCESS` and `VK_ERROR_PIPELINE_COMPILE_REQUIRED_EXT` before case-specific validators run.
- Initial compilation steps require `VK_SUCCESS` and a valid pipeline where the case needs a populated cache or a derivative base.
- No-compile, duplicate-batch, and early-return steps inspect the result, selected output handles, and in some cases elapsed creation time.
- Timing overruns and some cache-dependent outcomes are recorded as compatibility or quality warnings. Required handle invariants, such as a valid middle pipeline in a mixed batch or null pipelines after a real early-return failure, remain failures.

## Behavior Parameter Identification

> **Behavior parameter:** behavioral group of test case leaves
>
> **Candidate values:** `single_pipeline_no_compile`, `duplicate_single_recreate_*`, `duplicate_batch_pipelines_*`, `batch_pipelines_early_return`, `batch_pipelines_early_return_maintenance5`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `single_pipeline_no_compile` | Compile-required flag handling or immediate-return behavior |
| `duplicate_single_recreate_*` | Reuse handling with an explicit cache, no cache, or derivative base |
| `duplicate_batch_pipelines_*` | Per-element handling of mixed compile-required batch creation |
| `batch_pipelines_early_return` | Early-return result, output-handle ordering, or immediate-return behavior |
| `batch_pipelines_early_return_maintenance5` | `VkPipelineCreateFlags2CreateInfoKHR` translation or the same early-return behavior |

## Important Variations and Special Cases

- The source registers the same nine test case leaves for `graphics_pipelines` and `compute_pipelines`, yielding 18 monolithic mustpass leaves.
- `duplicate_single_recreate_explicit_caching` passes an explicit `VkPipelineCache`; `duplicate_single_recreate_no_caching` passes a null cache; `duplicate_single_recreate_derivative` retains a successful pipeline as `basePipelineHandle` for the later request.
- `duplicate_batch_pipelines_derivative_index` supplies the base relationship through `basePipelineIndex` inside a single call.
- The maintenance5 leaf moves nonzero legacy creation flags into `VkPipelineCreateFlags2CreateInfoKHR` and requires `VK_KHR_maintenance5`. It is excluded from Vulkan SC by source conditional compilation.
- Registration is monolithic only. The test measures creation-time behavior and does not register split pipeline construction variants.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Support checks | [`checkSupport()`](../../../modules/vulkan/pipeline/vktPipelineCreationCacheControlTests.cpp#L312-L328) | Requires the extension, feature, and maintenance5 when needed. |
| Result and handle validators | [`validateResults()` and helpers](../../../modules/vulkan/pipeline/vktPipelineCreationCacheControlTests.cpp#L99-L257) | Defines allowed results, handle checks, early-return ordering, and timing thresholds. |
| Pipeline-cache selection | [`createPipelineCache()`](../../../modules/vulkan/pipeline/vktPipelineCreationCacheControlTests.cpp#L413-L429) | Creates a cache only for explicit-cache cases. |
| Compute execution path | [`compute_tests::testInstance()`](../../../modules/vulkan/pipeline/vktPipelineCreationCacheControlTests.cpp#L1064-L1122) | Builds create infos, calls Vulkan, and applies validators. |
| Registered case definitions | [`TEST_CASES`](../../../modules/vulkan/pipeline/vktPipelineCreationCacheControlTests.cpp#L1128-L1297) | Gives the behavioral groups and per-iteration expectations. |
| Test-family registration | [`createCacheControlTests()`](../../../modules/vulkan/pipeline/vktPipelineCreationCacheControlTests.cpp#L1308-L1357) | Registers graphics and compute intermediate nodes. |

## Questions / Risk Points for User Audit

- Does the distinction between mandatory handle invariants and warning-level timing or cache outcomes remain clear?
- Does the behavioral grouping explain the test leaves without implying that a particular cache implementation strategy is required?
- Does the maintenance5 variant clearly remain a flag-transport variant of the early-return test?

## Conversion Notes for Final Wiki Rewrite

- Preserve the failure-mapping table verbatim in the final page.
- Keep the final page focused on creation calls and validators; mention shader generation only to establish that the test does not inspect shader execution.
- Use the test case behavioral groups as the final page's primary behavioral axis.
