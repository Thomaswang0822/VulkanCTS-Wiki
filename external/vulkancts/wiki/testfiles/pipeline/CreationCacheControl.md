## Overview

**Core question:** Does pipeline creation honor compile-required and early-return controls without violating required output-handle behavior?

- [`vktPipelineCreationCacheControlTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineCreationCacheControlTests.cpp#L1) implements the `pipeline.creation_cache_control` test family for `VK_EXT_pipeline_creation_cache_control`.
- The family is registered only under monolithic construction and divides execution into `graphics_pipelines` and `compute_pipelines` intermediate nodes.
- Each path exercises equivalent creation-control case leaves with a graphics or compute create-info template, then checks the Vulkan result, produced pipeline handles, and selected host-side timing bounds.
- This page explains the behavioral groups, cache and derivative variants, validation rules, and the limited role of the generated shaders.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- `VK_PIPELINE_CREATE_FAIL_ON_PIPELINE_COMPILE_REQUIRED_BIT_EXT` requests failure rather than compilation when creation of a valid pipeline would require compilation. The enabled [`pipelineCreationCacheControl` feature](../../../../vulkan-docs/src/chapters/features.adoc#features-pipelineCreationCacheControl) permits this use.
- `VK_PIPELINE_CREATE_EARLY_RETURN_ON_FAILURE_BIT_EXT` affects a multi-pipeline creation call. The [pipeline creation rules](../../../../vulkan-docs/src/chapters/pipelines.adoc#pipelines) require output entries at and after a failing element to be null when this flag applies.
- A `VkPipelineCache` is an optional creation input. Passing a cache, passing `VK_NULL_HANDLE`, and using a derivative relationship create different reuse contexts; they do not require the implementation to make the same cache hit decision.

## Registration Hierarchy

```text
pipeline.monolithic.creation_cache_control
├── graphics_pipelines
└── compute_pipelines
```

The source registers the same case array below each intermediate node. The split monolithic mustpass scope contains 18 leaves: nine for `graphics_pipelines` and nine for `compute_pipelines` in [`pipeline/monolithic/monolithic.txt`](../../../mustpass/main/vk-default/pipeline/monolithic/monolithic.txt#L22009-L22026).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Intermediate node | `graphics_pipelines`, `compute_pipelines` | Chooses the graphics or compute creation entry point while retaining the same cache-control case array. | [`addGraphicsPipelineTests()` and `addComputePipelineTests()`](../../../modules/vulkan/pipeline/vktPipelineCreationCacheControlTests.cpp#L1308-L1342) |
| Creation flags per iteration | normal, `VK_PIPELINE_CREATE_FAIL_ON_PIPELINE_COMPILE_REQUIRED_BIT_EXT`, and that flag with `VK_PIPELINE_CREATE_EARLY_RETURN_ON_FAILURE_BIT_EXT` | Selects ordinary compilation, prohibited compilation, or early exit after a batch failure. | [`TestParams::Iteration`](../../../modules/vulkan/pipeline/vktPipelineCreationCacheControlTests.cpp#L274-L307) |
| Cache/reuse context | `EXPLICIT_CACHE`, `NO_CACHE`, `DERIVATIVE_HANDLE`, `DERIVATIVE_INDEX` | Changes whether equivalent pipeline creation can use an explicit cache, an implicit cache, a prior derivative handle, or a batch base index. | [case definitions](../../../modules/vulkan/pipeline/vktPipelineCreationCacheControlTests.cpp#L1128-L1242) |
| Flag representation | legacy `VkPipelineCreateFlags`; `VkPipelineCreateFlags2CreateInfoKHR` for `batch_pipelines_early_return_maintenance5` | Tests the same early-return pattern through the maintenance5 flags2 transport. | [maintenance5 handling](../../../modules/vulkan/pipeline/vktPipelineCreationCacheControlTests.cpp#L897-L914) |

## Behavior Parameters

The primary behavioral axis is the behavioral group of test case leaves. Both intermediate nodes use the same groups.

### `single_pipeline_no_compile`: unseen pipeline without compilation

This leaf creates one pipeline with the compile-required flag and no explicit cache. The source records a quality warning if creation takes longer than the immediate threshold. It probes the no-compile request without assuming that a particular cache lookup must succeed.

### `duplicate_single_recreate_*`: recreate one equivalent pipeline

These leaves first allow compilation and require a valid pipeline. They then recreate the equivalent pipeline with compilation prohibited. The suffix selects an explicit `VkPipelineCache`, no passed cache, or a prior pipeline as the derivative base. The source marks selected result, validity, and timing outcomes as warnings because reuse can depend on implementation caching, while the initial successful creation remains required.

### `duplicate_batch_pipelines_*`: mix prohibited and allowed entries in one call

These leaves submit a no-compile, normal, no-compile sequence. The normal middle entry must create a valid pipeline. The suffix changes the reuse context: explicit cache, no passed cache, or a derivative base selected by `basePipelineIndex`. This isolates per-element behavior in a batch whose members have related creation inputs.

### `batch_pipelines_early_return`: stop after a compile-required failure

This leaf submits early-return/no-compile, normal, no-compile entries. The hard validator checks later handles only when the leading output handle is null; in that situation, every later handle must also be null. A non-null leading handle, a result other than the expected compile-required result, and slow return are warning-level outcomes, provided the result is one of the two globally accepted values.

### `batch_pipelines_early_return_maintenance5`: early return through flags2

This Vulkan-only leaf uses the same batch sequence and validators, but moves nonzero creation flags from the legacy field into `VkPipelineCreateFlags2CreateInfoKHR`. It requires `VK_KHR_maintenance5` and checks that this representation preserves the early-return behavior.

## Shader Analysis

The test builds minimal GLSL programs and shader modules solely to make graphics and compute pipeline creation valid. It does not submit rendering or dispatch work, read shader output, or compare shader behavior. Pipeline-creation results and output handles are the observed behavior, so a representative shader walkthrough would not explain the property under test.

## Runtime Execution and Result Checking

- [`checkSupport()`](../../../modules/vulkan/pipeline/vktPipelineCreationCacheControlTests.cpp#L312-L328) requires `VK_EXT_pipeline_creation_cache_control`, an enabled `pipelineCreationCacheControl` feature, and `VK_KHR_maintenance5` for the flags2 leaf.
- The test creates an explicit `VkPipelineCache` only for `EXPLICIT_CACHE`; all other cache modes pass a null cache to the Vulkan call. It creates the layouts, shader modules, and base graphics or compute create info needed for pipeline creation.
- For each iteration, the path builds one or more create infos with the selected flags. The graphics and compute paths call their respective Vulkan pipeline-creation functions and measure elapsed host time around that call.
- [`validateResults()`](../../../modules/vulkan/pipeline/vktPipelineCreationCacheControlTests.cpp#L99-L124) first accepts only `VK_SUCCESS` or `VK_ERROR_PIPELINE_COMPILE_REQUIRED_EXT`. Case validators then inspect required output handles, result codes, early-return handle ordering, and timing.
- A derivative-handle case retains the first valid pipeline from the initial iteration as the base for the later iteration. Pipeline wrappers destroy returned non-null handles after validation.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `single_pipeline_no_compile` | Compile-required flag handling or immediate-return behavior |
| `duplicate_single_recreate_*` | Reuse handling with an explicit cache, no cache, or derivative base |
| `duplicate_batch_pipelines_*` | Per-element handling of mixed compile-required batch creation |
| `batch_pipelines_early_return` | Early-return result, output-handle ordering, or immediate-return behavior |
| `batch_pipelines_early_return_maintenance5` | `VkPipelineCreateFlags2CreateInfoKHR` translation or the same early-return behavior |

### Cause Analysis

#### Compile-required flag handling or immediate-return behavior

**Possible failure symptoms:** `single_pipeline_no_compile` reports an unexpected API result or crosses its immediate-time quality threshold.

**Possible implementation causes:** The implementation may compile despite the compile-required request, report a result other than the allowed values, or take longer than the source's 500 microsecond quality threshold. Source-level investigation is needed to distinguish cache lookup, driver synchronization, and compilation-path causes from timing noise.

#### Reuse handling with an explicit cache, no cache, or derivative base

**Possible failure symptoms:** The required initial creation fails or returns a null pipeline; later recreation can produce warning-level result, handle, or timing diagnostics.

**Possible implementation causes:** The explicit cache input, implicit cache state, derivative handle, or derivative index may not be consumed consistently during pipeline creation. The test does not make a later cache hit mandatory, so warning-level outcomes alone do not identify a specification violation.

#### Per-element handling of mixed compile-required batch creation

**Possible failure symptoms:** In a no-compile, normal, no-compile batch, the required middle pipeline is null or the call reports an unaccepted result.

**Possible implementation causes:** The implementation may apply the compile-required condition to the wrong batch element, mishandle its interaction with the normal element, or fail to establish the requested derivative-by-index relationship. Source-level investigation is needed to localize the internal pipeline-cache or compiler path.

#### Early-return result, output-handle ordering, or immediate-return behavior

**Possible failure symptoms:** When the leading output handle is null, a later pipeline handle is non-null. The case can also report warning-level deviations in result code, first-handle state, or elapsed time.

**Possible implementation causes:** The batch implementation may continue processing elements after the null leading output or leave a later output handle populated. The [pipeline creation rules](../../../../vulkan-docs/src/chapters/pipelines.adoc#pipelines) define the null-handle ordering contract. Because the hard CTS validator is conditional on the leading handle being null, while the expected result and leading-handle state are warning checks, this leaf does not hard-fail every independently malformed combination of result and output handles.

#### `VkPipelineCreateFlags2CreateInfoKHR` translation or the same early-return behavior

**Possible failure symptoms:** The maintenance5 leaf differs from the legacy early-return leaf in required handle ordering or accepted creation result.

**Possible implementation causes:** The test moves nonzero legacy flags into a flags2 `pNext` structure before creation. A defect can arise while translating or consuming that structure, or in the common early-return implementation. The source-level comparison between the flags2 path and the legacy path is needed to localize it.

## Case Pruning

### Requirement-based pruning

The family skips when the device lacks `VK_EXT_pipeline_creation_cache_control` or its `pipelineCreationCacheControl` feature. The maintenance5 leaf additionally requires `VK_KHR_maintenance5`. Source conditional compilation excludes that leaf for Vulkan SC.

### Design-based pruning

The source registers this family only for `pipeline.monolithic`. The property depends on the timing and output behavior of whole-pipeline creation calls, so it does not construct equivalent split-pipeline variants. The shared nine-leaf case array deliberately covers graphics and compute creation without multiplying the matrix by shader behavior, because shaders are not executed.

## Key Takeaways

- These tests observe pipeline-creation control behavior rather than rendering or compute results.
- Cache mode and derivative setup provide distinct reuse contexts, but the source deliberately treats several later reuse outcomes as warnings instead of requiring a particular cache-hit result.
- The hard early-return check is conditional: once the leading output handle is null, every later entry must also be null. The expected result and leading-handle state are checked as warnings.
- `batch_pipelines_early_return_maintenance5` verifies the flags2 representation of the same creation-control contract.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Support checks | [`checkSupport()`](../../../modules/vulkan/pipeline/vktPipelineCreationCacheControlTests.cpp#L312-L328) | Requires the extension, feature, and maintenance5 when applicable. |
| Result, handle, and timing validators | [`validateResults()` and helpers](../../../modules/vulkan/pipeline/vktPipelineCreationCacheControlTests.cpp#L99-L257) | Defines accepted results and the observable pass, warning, and fail conditions. |
| Explicit cache creation | [`createPipelineCache()`](../../../modules/vulkan/pipeline/vktPipelineCreationCacheControlTests.cpp#L413-L429) | Creates an empty `VkPipelineCache` only for explicit-cache cases. |
| Graphics execution path | [`graphics_tests::testInstance()`](../../../modules/vulkan/pipeline/vktPipelineCreationCacheControlTests.cpp#L853-L942) | Builds graphics create infos, calls Vulkan, and validates each iteration. |
| Compute execution path | [`compute_tests::testInstance()`](../../../modules/vulkan/pipeline/vktPipelineCreationCacheControlTests.cpp#L1064-L1122) | Builds compute create infos, calls Vulkan, and validates each iteration. |
| Case definitions | [`TEST_CASES`](../../../modules/vulkan/pipeline/vktPipelineCreationCacheControlTests.cpp#L1128-L1297) | Defines the behavioral groups, flag sequences, cache modes, and validators. |
| Registration | [`createCacheControlTests()`](../../../modules/vulkan/pipeline/vktPipelineCreationCacheControlTests.cpp#L1308-L1357) | Registers the graphics and compute intermediate nodes. |
