## Overview

**Core question:** Does a data graph pipeline cache produce the expected hit or compile-required result, and does a cache miss affect later pipelines as specified?

- This page covers the implementation and registration in [`vktDataGraphPipelineCacheTests.cpp`](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L66-L146).
- The `data_graph.cache` test category contains pipeline creation tests in `create_pipeline` and cache-backed execution tests in `submit_pipeline` [registration](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L834-L855).
- Creation tests arrange pipelines in fill, hit, and miss sequences. Single-pipeline calls use pipeline-creation feedback, while the single-call batched path checks `VK_PIPELINE_COMPILE_REQUIRED` and returned handles [single-pipeline checks](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L283-L344) [batched checks](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L521-L577).
- The `submit_pipeline` family creates several pipelines with one cache, dispatches each through a data graph session, waits for the queue, and verifies tensor outputs [execution and checking](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L658-L792).
- The generated test names expose the cache sequence and the TOSA graph/resource dimensions. The large generated matrix is described below rather than expanded into the registration tree.

## Background Knowledge

- A `VkPipelineCache` is an opaque cache object passed to pipeline creation. Reusing the same object lets later compatible pipeline creations consult entries produced by earlier creations; the Vulkan pipeline-cache description covers this reuse model in [`pipelines.adoc`](../../../../vulkan-docs/src/chapters/pipelines.adoc#L7978-L8067).
- `VK_PIPELINE_CREATE_FAIL_ON_PIPELINE_COMPILE_REQUIRED_BIT_EXT` changes a creation request into a check for whether compilation is already available. A cache miss is reported as `VK_PIPELINE_COMPILE_REQUIRED`, rather than producing a usable pipeline; the flag is described in [`pipelines.adoc`](../../../../vulkan-docs/src/chapters/pipelines.adoc#L684-L695).
- Pipeline creation feedback is an optional result structure. Its `VK_PIPELINE_CREATION_FEEDBACK_VALID_BIT` says that the feedback is valid, while `VK_PIPELINE_CREATION_FEEDBACK_APPLICATION_PIPELINE_CACHE_HIT_BIT` reports an application pipeline-cache hit [spec description](../../../../vulkan-docs/src/chapters/pipelines.adoc#L10752-L10840).

## Registration Hierarchy

The page covers both direct families registered below `data_graph.cache`:

```text
data_graph.cache
├── create_pipeline
└── submit_pipeline
```

`create_pipeline` then registers the two implementation paths `single_call` and `multi_calls`; their generated leaves are the cache-sequence names described in the parameter sections. The exact registrations are in [`createPipelineTests`](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L834-L838) and [`createPipelineSingleCallTests` / `createPipelineMultiCallsTests`](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L796-L832). The mustpass file contains the corresponding `data_graph.cache.create_pipeline.single_call`, `data_graph.cache.create_pipeline.multi_calls`, and `data_graph.cache.submit_pipeline` prefixes [mustpass examples](../../../mustpass/main/vk-default/data-graph.txt#L3181-L3184) [submit prefix](../../../mustpass/main/vk-default/data-graph.txt#L5981-L5984).

## Parameter Dimensions and Observed Values

The test generator forms a Cartesian product, then keeps only valid `TestParams` and provider-supported format strings [generation](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.cpp#L175-L215). The cache family adds its own sequence and failure-mode dimensions.

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Pipeline family | `create_pipeline.single_call`, `create_pipeline.multi_calls`, `submit_pipeline` | Selects one-at-a-time creation, one batched creation call, or cache-aware creation followed by dispatch. | [registration](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L796-L855) |
| Failure mode | `failOnMissNoEarlyReturn`, `failOnMissEarlyReturn` | Selects whether expected compile-required behavior is checked without or with early return in the single-call creation sequence. The generated cache tests do not register `ignoreMiss`; that enum value exists only as an implementation branch. | [modes and names](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L73-L126) [registrations](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L802-L830) |
| Cache sequence | `FillHitHitHit`, `FillHitMissHit` | Controls which pipeline creation is expected to populate the cache, reuse it, or miss it. `single_call` registers both sequences; `multi_calls` registers `FillHitMissHit`. | [single-call sequences](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L802-L817) [multi-call sequence](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L822-L831) |
| Submit sequence | `FillHitHit` | Builds the first pipeline with an empty cache and creates the following pipelines with that same cache before dispatching all successful sessions. | [submit registration](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L840-L848) |
| Instruction set | `tosa` | Selects the provider used by these tests. The source passes `"TOSA"` to `DataGraphTestProvider`. | [provider calls](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L163-L167) [provider selection](../../../modules/vulkan/data_graph/vktDataGraphTestProvider.hpp#L44-L62) |
| Session memory | `noSession`, `session` | Selects whether the data graph session uses session memory in the submit path. | [default dimensions](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.hpp#L434-L440) [session creation](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L710-L716) |
| Resource cardinality | `noIn`, `oneIn`, `manyIn`; `oneOut`, `manyOut`; `noConst`, `oneConst`, `manyConst` | Changes the number of input, output, and constant resources in the provider-selected graph. The generator deliberately excludes `noOut`; every graph has an output. | [cardinality list](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.hpp#L127-L132) [validity rule](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.cpp#L161-L170) |
| Format string | Observed values include `fp16`, `fp32`, `i8`, `i32`, `fp16fp16fp16`, and `i8i8i32` | Selects the data types for the provider's resource layout. The exact set depends on the selected cardinalities. | [format generation](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.cpp#L199-L209) [TOSA formats](../../../modules/vulkan/data_graph/tosa/vktDataGraphTosaUtil.hpp#L235-L253) |
| Input/output/constant strides | `implicit`, `packed`, `notPacked` | Changes the tensor descriptions used in pipeline keys and resource creation. Constants are packed by the validity rules; a resource type that is absent must use implicit strides. | [name encoding](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.cpp#L84-L96) [validity rules](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.cpp#L139-L160) |
| Binding order | `orderedBindings`, `unorderedBindings` | Selects the normal or shuffled resource-binding order used to build the descriptor layout and graph resource list. | [name encoding and generation](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.cpp#L92-L97) [dimensions](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.hpp#L434-L440) |
| Tensor tiling | `linearTiling`, `optimalTiling` | Selects the tensor tiling in the generated resource descriptions. Optimal tiling is retained only with implicit strides. | [tiling names and validity](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.cpp#L98-L107) [validity rule](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.cpp#L139-L145) |
| Sparse constants | absent or `sparseConstants` | Adds constant sparsity metadata when the graph has constants. Provider validation rejects a requested sparse case without matching sparsity information. | [name encoding](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.cpp#L108-L116) [provider validation](../../../modules/vulkan/data_graph/vktDataGraphTestProvider.cpp#L108-L138) |

## Behavior Parameters

The primary behavioral axis is the cache sequence combined with the requested failure mode. The cache mode values are internal enum values `FILL_CACHE`, `HIT_CACHE`, and `MISS_CACHE`; the generated names concatenate them as `Fill`, `Hit`, and `Miss` [name conversion](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L87-L126).

### `Fill`: create the cache entry

The test creates a pipeline with an empty `VkPipelineCache` and expects a valid feedback structure whose application-cache-hit bit is clear. This is the reference creation used by later `Hit` cases. The single-call path performs this check directly after creation [fill check](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L289-L302).

### `Hit`: reuse the cache entry

The test creates the same logical TOSA data graph with the cache containing the reference entry and expects a valid pipeline-creation feedback structure with `VK_PIPELINE_CREATION_FEEDBACK_APPLICATION_PIPELINE_CACHE_HIT_BIT` set [hit check](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L303-L316). When the failure mode is not `IGNORE_CACHE_MISS`, the test also sets `VK_PIPELINE_CREATE_FAIL_ON_PIPELINE_COMPILE_REQUIRED_BIT_EXT`, so an unexpected compile requirement fails the API check instead of silently compiling [flag setup](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L283-L287).

### `Miss`: require compilation to be reported

For the single-call path, the miss entry uses the same cache as the other entries but changes the pipeline parameters as described below. The registered cases use a fail-on-miss mode, so the miss request carries `VK_PIPELINE_CREATE_FAIL_ON_PIPELINE_COMPILE_REQUIRED_BIT_EXT`; the batched call must return `VK_PIPELINE_COMPILE_REQUIRED`, and the miss handle must be null [single-call miss check](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L521-L577). In the multi-call implementation, `IGNORE_CACHE_MISS` instead permits creation and checks that the feedback hit bit remains clear, but that mode is not registered; its registered miss also expects `VK_PIPELINE_COMPILE_REQUIRED` and a null handle [multi-call miss checks](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L317-L340).

### `FillHitHitHit`: repeated hits after fill

This sequence is registered for `single_call` creation. The first pipeline fills the cache, and the three later creations must hit it. No pipeline is expected to fail in this sequence [registration](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L801-L805).

### `FillHitMissHit`: a miss between cache hits

This sequence is registered for both creation paths. The first pipeline fills the cache, the second must hit, the third must miss, and the fourth uses the reference parameters again. In `single_call`, the final `Hit` remains valid under both early-return settings. In `multi_calls`, the four requests are passed to one `vkCreateDataGraphPipelinesARM` call [registered sequences](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L807-L830).

### `FillHitHit`: cache-aware dispatch

This is the `submit_pipeline` behavior. The test creates three successful pipelines against one cache, creates a session for each, binds each pipeline and its tensor descriptor set, dispatches each session, waits for completion, and checks the output tensor resources [submit path](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L658-L716) [dispatch and checking](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L747-L792).

## Shader Analysis

This page has no representative shader walkthrough. The cache implementation obtains a provider-owned TOSA shader module and passes it to `VkDataGraphPipelineShaderModuleCreateInfoARM`, but this page does not define or inspect that shader's code or semantics. Its assertions are about pipeline-cache creation feedback, `VK_PIPELINE_COMPILE_REQUIRED`, returned handles, early-return propagation, and (for `submit_pipeline`) successful cache-backed dispatch and provider-owned tensor verification [provider boundary](../../../modules/vulkan/data_graph/vktDataGraphTestProvider.hpp#L44-L62) [shader-module handoff](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L253-L275) [cache assertions](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L289-L340) [dispatch and verification](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L658-L792). Shader generation and shader semantics therefore belong to the TOSA provider, not to the cache behavior documented here; this page is listed in the source-reviewed no-walkthrough exception registry.

## Runtime Execution and Result Checking

- Each creation case obtains a TOSA `DataGraphTest`, creates tensor resources and views for tensor resources, and initializes host or tensor data before assembling graph resource and constant descriptions [resource setup](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L163-L251).
- The single-call path builds one pipeline-create-info per sequence entry, chains the data graph shader-module information and pipeline-creation feedback structure, then submits all entries in one call. It checks each returned handle against the expected miss position [batched creation](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L407-L551) [handle checks](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L553-L577).
- The multi-call path creates a separate cache object for each requested pipeline. A `FILL_CACHE` entry records the reference cache index; `HIT_CACHE` entries use that cache, while `MISS_CACHE` entries use a newly created empty cache [cache selection](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L153-L225). It checks feedback on fill and hit and checks `VK_PIPELINE_COMPILE_REQUIRED` and a null handle for a required miss [multi-call creation](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L289-L344).
- In the batched single-call path, a miss is represented by a null pipeline handle. Without early return, the expected successful entries before and after the miss remain valid. With `VK_PIPELINE_CREATE_EARLY_RETURN_ON_FAILURE_BIT_EXT` on the miss entry, the test expects the miss and all later entries to be null [early-return flags and checks](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L521-L575).
- The submit path creates sessions only for successful pipelines. It records binding and `cmdDispatchDataGraphARM` commands for each session in one command buffer, submits and waits on the universal queue, then calls the provider test's `verifyData` for every tensor output [dispatch](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L710-L767) [verification](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L769-L792).
- A successful creation case returns a passing `tcu::TestStatus`; an unexpected feedback bit, unexpected successful miss, unexpected compile result, invalid handle, or tensor verification failure returns a failing status or propagates the failed verification result [status checks](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L294-L344) [submit verification](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L781-L792).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `Fill` | The initial pipeline creation did not produce the expected cache state or reported an application-cache hit. |
| `Hit` | The later creation did not find the compatible cache entry, did not report the hit feedback bit, or unexpectedly required compilation. |
| `Miss` | The deliberately changed pipeline did not produce the expected compile-required result, or the returned handle did not remain null. |
| `FillHitHitHit` | Cache reuse failed for one of the repeated creations, or the batched handle validation disagreed with the all-success expectation. |
| `FillHitMissHit` | The cache sequence, miss differentiation, compile-required result, or post-miss handle behavior did not match the selected early-return mode. |
| `FillHitHit` | Pipeline creation succeeded but cache-aware session setup, dispatch, queue completion, or output verification failed. |

A failure can also indicate that the required support gate was not met; such a case should be reported as unsupported rather than interpreted as a cache mismatch.

### Cause Analysis

#### Pipeline-cache lookup or feedback mismatch

**Possible failure symptoms:** A `Fill` creation reports `VK_PIPELINE_CREATION_FEEDBACK_APPLICATION_PIPELINE_CACHE_HIT_BIT`, a `Hit` creation lacks that bit, or the feedback-valid bit is absent where the test asserts it.

**Possible implementation causes:** The implementation may not identify compatible data graph pipeline state consistently across the cache sequence, or it may report pipeline-creation feedback that does not describe the creation result. The source establishes the expected bits but does not identify a narrower implementation defect [feedback assertions](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L289-L315).

#### Compile-required and returned-handle mismatch

**Possible failure symptoms:** A miss succeeds when the test expects `VK_PIPELINE_COMPILE_REQUIRED`, returns a non-null pipeline for the expected failure, or returns a different result from the batched creation call.

**Possible implementation causes:** The `VK_PIPELINE_CREATE_FAIL_ON_PIPELINE_COMPILE_REQUIRED_BIT_EXT` contract may not be honored for the data graph pipeline, or the implementation may not preserve the required output-handle state on a compile-required return. The source checks the Vulkan result and handle directly [single miss](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L333-L340) [batched result](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L540-L575).

#### Batched early-return propagation

**Possible failure symptoms:** In the early-return sequence, a pipeline after the expected miss is non-null; in the non-early-return sequence, an otherwise cacheable pipeline is null.

**Possible implementation causes:** The implementation may stop or continue processing batched pipeline entries contrary to `VK_PIPELINE_CREATE_EARLY_RETURN_ON_FAILURE_BIT_EXT`, or may apply the failure state to the wrong entry. The test deliberately sets the flag only on the miss entry and then checks later handles [flag and propagation check](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L527-L575).

#### Cache-aware dispatch or tensor result mismatch

**Possible failure symptoms:** A successful submit case fails while creating a session, recording or submitting dispatches, waiting for completion, or verifying an output tensor.

**Possible implementation causes:** The failure may involve data graph pipeline/session integration, descriptor binding, command execution, or provider-defined tensor results. This page does not attribute such a failure to the cache alone; the submit path verifies the complete successful pipeline-to-dispatch path [submit flow](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L710-L792).

#### Missing required support

**Possible failure symptoms:** The test is skipped with a not-supported result before pipeline creation because `pipelineCreationCacheControl`, a data graph feature, a tensor feature, or the required non-packed-resource support is absent.

**Possible implementation causes:** The device does not expose the feature set required by this category. Cache tests first require `pipelineCreationCacheControl`; the shared check then requires `VK_ARM_data_graph`, `VK_ARM_tensors`, `dataGraph`, `dataGraphShaderModule`, `tensors`, `shaderTensorAccess`, and, for non-packed resources, `tensorNonPacked` [cache gate](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L129-L146) [shared gate](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.hpp#L219-L257).

## Case Pruning

### Requirement-based pruning

- The cache-specific support check requires `pipelineCreationCacheControl`. The common data graph check requires `VK_ARM_data_graph`, `VK_ARM_tensors`, `dataGraph`, `dataGraphShaderModule`, `tensors`, and `shaderTensorAccess` [support checks](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L129-L146) [common features](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.hpp#L219-L251).
- Cases with non-packed input or output resources additionally require `tensorNonPacked` [feature gate](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.hpp#L253-L256).
- The generator rejects optimal tiling with explicit strides, non-packed constants, non-implicit strides for absent resources, sparse constants without constants, and graphs with no output [validity rules](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.cpp#L139-L170).
- Provider validation rejects combinations whose requested resource cardinality, tiling, stride packing, or sparse-constant metadata does not match the selected TOSA graph [validation](../../../modules/vulkan/data_graph/vktDataGraphTestProvider.cpp#L37-L138).

This pruning means that the removed case is unsupported or invalid for the selected device or graph contract, not a cache failure.

### Design-based pruning

- `allResourceCardinalityCombinations` intentionally omits `noOut`; the generator documents that every graph must have at least one output [cardinalities](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.hpp#L127-L132).
- A miss case changes only the selected pipeline's effective resource description by forcing linear tiling and toggling input packing. This supplies a controlled cache-key difference while retaining the same surrounding sequence [miss construction](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L390-L412).
- `multi_calls` uses one pipeline-cache object per pipeline creation path so a miss can be isolated on a fresh empty cache, while the single-call path uses one cache and distinguishes the miss through pipeline parameters [multi-call cache selection](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L153-L225) [single-call cache setup](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L533-L551).
- The registered sequences do not include every permutation of `Fill`, `Hit`, and `Miss`. They select the shortest sequences that exercise initial fill, repeated reuse, an intervening miss, and the early-return distinction [registrations](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L796-L848).

## Key Takeaways

- `Fill`, `Hit`, and `Miss` are checked through different observables: feedback bits for regular creation and compile-required plus null handles for expected failures.
- The registered single-call cases distinguish a batch that continues after a compile-required entry from a batch that returns early and invalidates later output handles.
- `multi_calls` and `single_call` use different cache arrangements, so their miss mechanics should not be read as identical API call shapes.
- `submit_pipeline` treats cache reuse as part of a complete data graph execution path: it creates sessions, dispatches them, waits, and verifies tensor outputs.
- A failure does not by itself identify a cache bug. The observed failing check determines whether the issue is feedback, compile-required handling, batch propagation, dispatch, tensor verification, or support gating.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Cache support gate | [`checkSupport`](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L129-L146) | Requires `pipelineCreationCacheControl` and delegates shared data graph/tensor feature checks. |
| Single-call registration | [`createPipelineSingleCallTests`](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L796-L820) | Defines the exact `FillHitHitHit`, `FillHitMissHit`, and early-return registrations. |
| Multi-call registration | [`createPipelineMultiCallsTests`](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L822-L831) | Defines the exact batched `FillHitMissHit` registration. |
| Submit registration | [`submitPipelineTests`](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L840-L848) | Defines the exact `FillHitHit` cache-aware dispatch registration. |
| Single-call creation checks | [`createPipelineSingleCallTest`](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L347-L577) | Builds the batch and validates compile-required, null-handle, and early-return behavior. |
| Multi-call creation checks | [`createPipelineMultiCallsTest`](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L148-L345) | Isolates fresh-cache misses and checks pipeline creation feedback. |
| Cache-aware dispatch checks | [`submitPipelineTest`](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L580-L792) | Creates sessions, dispatches all successful pipelines, and verifies tensor outputs. |
| Generated dimensions | [`getTestParamsVariations`](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.cpp#L175-L215) | Produces valid TOSA/resource/stride/binding/tiling/sparsity combinations and provider formats. |
| Mustpass evidence | [`data-graph.txt`](../../../mustpass/main/vk-default/data-graph.txt#L3181-L3184) | Shows the registered `multi_calls` prefix and generated cache leaves. |
| Vulkan pipeline-cache semantics | [`pipelines.adoc`](../../../../vulkan-docs/src/chapters/pipelines.adoc#L7978-L8067) | Defines cache reuse and cache consultation during pipeline creation. |
