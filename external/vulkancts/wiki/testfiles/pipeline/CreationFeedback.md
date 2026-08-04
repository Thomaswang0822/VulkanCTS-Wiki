## Overview

**Core question:** Does Vulkan return internally consistent pipeline and stage creation feedback when the CTS creates graphics and compute pipelines through cache, derivative, and pipeline-binary paths?

- [`vktPipelineCreationFeedbackTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineCreationFeedbackTests.cpp#L1) implements the `creation_feedback` test family in the `pipeline` test category.
- The family requests `VK_EXT_pipeline_creation_feedback` records while it creates graphics and, for the monolithic construction type, compute pipelines.
- The tests validate feedback-record consistency rather than rendered pixels or compute results. They distinguish hard API-contract failures from quality warnings about a cache hit or a zero duration.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- [`VkPipelineCreationFeedbackCreateInfoEXT`](../../../../vulkan-docs/src/chapters/pipelines.adoc#pipelines-creation-feedback) extends graphics or compute pipeline creation with one pipeline feedback record and an optional ordered stage-feedback array. The record's `duration` is measured in nanoseconds.
- `VK_PIPELINE_CREATION_FEEDBACK_VALID_BIT_EXT` controls whether a record is meaningful. Without it, no other flag may be set and all other record fields are undefined.
- `VK_PIPELINE_CREATION_FEEDBACK_APPLICATION_PIPELINE_CACHE_HIT_BIT_EXT` identifies use of a readily usable entry from the application-provided pipeline cache. `VK_PIPELINE_CREATION_FEEDBACK_BASE_PIPELINE_ACCELERATION_BIT_EXT` identifies use of the declared base pipeline to accelerate a derivative's creation.
- Per-stage feedback is optional. A whole-pipeline cache hit is one documented reason an implementation can omit it.

## Registration Hierarchy

```text
pipeline.monolithic.creation_feedback
├── graphics_tests
└── compute_tests
```

The source registers `graphics_tests` for each supported pipeline construction type. It registers `compute_tests` only for `pipeline.monolithic.creation_feedback`. The parseable root above uses the monolithic form because it is the only construction path with both direct intermediate nodes.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test mode | `TestMode::CACHE`, `TestMode::BINARY` | Chooses application-cache reuse or `VK_KHR_pipeline_binary` inputs. | [`TestParam`](../../../modules/vulkan/pipeline/vktPipelineCreationFeedbackTests.cpp#L118-L180), [registration](../../../modules/vulkan/pipeline/vktPipelineCreationFeedbackTests.cpp#L1444-L1504) |
| Pipeline construction type | monolithic and supported non-monolithic types | Changes the pipeline wrapper and registered root. Compute coverage is monolithic-only. | [graphics and compute registration](../../../modules/vulkan/pipeline/vktPipelineCreationFeedbackTests.cpp#L1444-L1504) |
| Direct intermediate node | `graphics_tests`, `compute_tests` | Selects graphics multi-stage or compute single-stage creation and validation. | [registration](../../../modules/vulkan/pipeline/vktPipelineCreationFeedbackTests.cpp#L1444-L1504) |
| Shader-stage chain | `vertex_stage_fragment_stage`, `vertex_stage_geometry_stage_fragment_stage`, `vertex_stage_tessellation_control_stage_tessellation_evaluation_stage_fragment_stage`, `compute_stage` | Changes the requested graphics stage-feedback count or chooses the compute path. | [stage matrix](../../../modules/vulkan/pipeline/vktPipelineCreationFeedbackTests.cpp#L1450-L1498) |
| Creation sequence | no cached pipeline, derivative, cached or binary-backed pipeline | Supplies the expected context for cache-hit and base-pipeline-acceleration flags. | [graphics lifecycle](../../../modules/vulkan/pipeline/vktPipelineCreationFeedbackTests.cpp#L496-L668), [compute creation](../../../modules/vulkan/pipeline/vktPipelineCreationFeedbackTests.cpp#L1158-L1265) |
| Cache and lifetime variation | normal cache, `_no_cache`, `_delayed_destroy` | Controls whether an application cache is present and when the first pipeline is destroyed. | [`TestParam::generateTestName`](../../../modules/vulkan/pipeline/vktPipelineCreationFeedbackTests.cpp#L172-L180), [case matrix](../../../modules/vulkan/pipeline/vktPipelineCreationFeedbackTests.cpp#L1458-L1469) |
| Stage-feedback request | normal count, `_zero_out_feedback_cout` | Graphics cases request feedback for all active stages or, in the vertex-plus-fragment zero-count case, set `pipelineStageCreationFeedbackCount` to zero. Compute cases always request their single stage record. The registered suffix preserves the source spelling. | [feedback-chain setup](../../../modules/vulkan/pipeline/vktPipelineCreationFeedbackTests.cpp#L769-L835), [case matrix](../../../modules/vulkan/pipeline/vktPipelineCreationFeedbackTests.cpp#L1458-L1491) |

The default mustpass suite contains 13 cache-mode leaves for `pipeline.monolithic.creation_feedback`: ten graphics and three compute. Each of the six non-monolithic construction roots contains the ten graphics leaves. Pipeline-binary creation feedback is registered below separate `pipeline_binary.creation_feedback` roots and is not part of this page's canonical `creation_feedback` hierarchy.

## Behavior Parameters

The primary behavioral axis is the direct intermediate node. It selects the pipeline kind and feedback-array shape that the CTS validates.

### `graphics_tests`: graphics pipeline and active-stage feedback

Graphics cases create three pipeline forms: a no-cache pipeline, a derivative that uses that pipeline as its base, and a cached or binary-backed pipeline. The stage chain can contain vertex and fragment stages only, add geometry, or add tessellation control and evaluation stages. The feedback chain targets the final monolithic pipeline or relevant graphics-pipeline-library parts, and it requests one stage record per active shader stage unless the zero-count variation suppresses the request.

### `compute_tests`: monolithic compute pipeline and compute-stage feedback

The monolithic path creates no-cache, derivative, and cached or binary-backed compute pipelines. The feedback chain contains one pipeline record and one record for `VkComputePipelineCreateInfo::stage`; the zero-count variation is not registered for compute. The source does not repeat compute tests for non-monolithic construction types.

## Shader Analysis

The shaders are fixtures for pipeline creation, not the tested computation. Graphics cases compile vertex and fragment shaders plus optional geometry or tessellation shaders. Compute cases build a minimal compute shader and descriptor configuration. The test does not submit graphics commands or dispatch compute work, and it does not inspect shader output. Its observations come from host-visible feedback structures populated during pipeline creation.

## Runtime Execution and Result Checking

1. The test checks for `VK_EXT_pipeline_creation_feedback`; binary mode also requires `VK_KHR_pipeline_binary`. Graphics stage variants require geometry or tessellation support where applicable.
2. In cache mode, the base instance creates an empty `VkPipelineCache` unless `_no_cache` is selected. The graphics and compute instances create their shaders and pipeline creation state.
3. The graphics path allocates feedback storage for up to five pipeline parts and six shader stages. It chains `VkPipelineCreationFeedbackCreateInfoEXT` through the wrapper's pipeline-create information. For monolithic creation it supplies the final part's record; for non-monolithic construction it associates records with the relevant parts. The compute path chains one pipeline record and one requested stage record to `VkComputePipelineCreateInfo`.
4. The source creates a no-cache pipeline first. It creates a derivative with that pipeline as its base, then creates a cached or binary-backed pipeline. The delayed-destroy variation controls whether the source destroys the initial pipeline before the final creation.
5. The validator examines each pipeline feedback record. If `VALID` is absent, it fails only when another flag is present. If `VALID` is set, it rejects a cache-hit bit for a cache-disabled or no-cache creation and rejects a base-pipeline-acceleration bit outside the eligible derivative case.
6. For the final graphics pipeline, it examines each requested stage record. In the zero-count graphics case, it instead verifies that the pre-cleared stage records contain no returned flag bits. The compute validator always examines its one requested stage record. Cache-hit absence in a cached case and zero duration produce `QP_TEST_RESULT_QUALITY_WARNING` under the source's stated conditions; they do not turn an otherwise valid record into a hard test failure.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `graphics_tests` | Graphics pipeline or per-stage feedback violates the validity, cache-hit, base-pipeline, or zero-count no-write contract. |
| `compute_tests` | Compute pipeline or compute-stage feedback violates the same contract for a single-stage pipeline. |

### Cause Analysis

#### Feedback validity state is internally inconsistent

**Possible failure symptoms:** A pipeline or stage record lacks `VK_PIPELINE_CREATION_FEEDBACK_VALID_BIT_EXT` but contains another feedback flag, causing a hard CTS failure.

**Possible implementation causes:** The implementation may leave stale flag bits in a record it marks invalid or fail to initialize the pipeline and stage feedback outputs consistently. The Vulkan contract requires every supplied record to have `VALID` set or clear and forbids other flags when `VALID` is clear. Source-level driver investigation is needed to locate the write path.

#### Cache-hit feedback appears for a creation that cannot use the application cache

**Possible failure symptoms:** A `_no_cache` or no-cache pipeline reports `VK_PIPELINE_CREATION_FEEDBACK_APPLICATION_PIPELINE_CACHE_HIT_BIT_EXT`; the test reports a hard failure.

**Possible implementation causes:** The driver may conflate an internal cache with the application-supplied `VkPipelineCache`, retain state across the CTS creation sequence, or report the cache-hit bit without an eligible application cache. The bit specifically describes a readily usable entry in the pipeline cache supplied to the creation command.

#### Base-pipeline acceleration is reported outside the derivative path

**Possible failure symptoms:** The no-cache or cached/binary-backed creation reports `VK_PIPELINE_CREATION_FEEDBACK_BASE_PIPELINE_ACCELERATION_BIT_EXT`, although it did not use the required base-pipeline relationship.

**Possible implementation causes:** The driver may incorrectly retain derivative metadata, associate the feedback record with a neighboring pipeline creation, or set the acceleration bit without using `basePipelineHandle` or `basePipelineIndex`. The test isolates the expected derivative sequence, but implementation investigation is required to identify the internal association error.

#### Stage feedback flags do not match the requested graphics or compute shape

**Possible failure symptoms:** A requested graphics stage record or the compute stage record has an invalid flag combination, or a pre-cleared graphics stage record contains flag bits after the CTS requested zero stage records.

**Possible implementation causes:** The implementation may index stage feedback incorrectly, mishandle optional geometry or tessellation stages, or write records after a count-zero request. The graphics and compute creation rules constrain the count supplied by the CTS when it is nonzero; the observable CTS failures concern returned record flags, not a returned feedback count.

#### Cache-hit or duration diagnostics produce a quality warning

**Possible failure symptoms:** A cached or binary-backed case reports no cache hit for the pipeline and relevant stage records, or a valid heavy graphics record or compute record reports zero duration. The CTS returns a quality warning rather than failure.

**Possible implementation causes:** The implementation may legitimately miss an application-cache reuse opportunity, have timing precision below the observed creation work, or report feedback conservatively. These outcomes do not alone show a Vulkan contract violation. The source records them to flag feedback usefulness; diagnosing performance or timestamp behavior requires implementation-specific evidence.

## Case Pruning

### Requirement-based pruning

- Every case requires `VK_EXT_pipeline_creation_feedback`.
- `TestMode::BINARY` requires `VK_KHR_pipeline_binary`.
- Geometry cases require `geometryShader`; tessellation cases require `tessellationShader`.
- The selected `PipelineConstructionType` must meet the construction wrapper's requirements.
- The existing source excludes the test family under its `CTS_USES_VULKANSC` guard.

### Design-based pruning

- `compute_tests` appears only for `PIPELINE_CONSTRUCTION_TYPE_MONOLITHIC`, as the source intentionally avoids repeating compute feedback through graphics pipeline library construction.
- Binary mode filters cache-enabled and cache-disabled variants differently because it uses pipeline-binary data rather than the ordinary application cache sequence.
- The three graphics stage chains cover a minimal, geometry, and tessellation-inclusive layout instead of every graphics-stage combination.
- `_zero_out_feedback_cout` is registered only for the vertex-plus-fragment graphics case. It isolates a zero requested stage-feedback count without multiplying every stage chain.
- The source limits its creation sequences to no-cache, derivative, and cached or binary-backed forms, which directly exercise the feedback flags under discussion.

## Key Takeaways

- The page tests creation-time feedback records, not shader execution or rendered output.
- `VALID` determines whether the other fields may be interpreted; invalid feedback must not carry other flags.
- The CTS derives its hard cache-hit and base-pipeline checks from the exact creation sequence it builds.
- A missing expected cache hit or zero duration is logged as a quality signal, while an impossible flag combination fails the case.
- Graphics coverage varies the requested stage array; compute coverage tests the monolithic single-stage case.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Parameters and naming | [`TestParam`](../../../modules/vulkan/pipeline/vktPipelineCreationFeedbackTests.cpp#L118-L180) | Defines all registered mode, stage, cache, lifetime, and count variations |
| Capability checks | [`BaseTestCase::checkSupport`](../../../modules/vulkan/pipeline/vktPipelineCreationFeedbackTests.cpp#L190-L210) | Requires the feedback extension and pipeline-binary extension when needed |
| Graphics pipeline lifecycle | [`GraphicsTestInstance::GraphicsTestInstance`](../../../modules/vulkan/pipeline/vktPipelineCreationFeedbackTests.cpp#L450-L669) | Creates the three pipeline forms and applies destruction timing |
| Graphics feedback setup | [`GraphicsTestInstance::preparePipelineWrapper`](../../../modules/vulkan/pipeline/vktPipelineCreationFeedbackTests.cpp#L671-L835) | Chains the feedback create info and sizes stage-feedback arrays |
| Graphics result checking | [`GraphicsTestInstance::verifyTestResult`](../../../modules/vulkan/pipeline/vktPipelineCreationFeedbackTests.cpp#L836-L1030) | Implements pipeline-part and per-stage flag, warning, and duration checks |
| Compute creation and checking | [`ComputeTestInstance`](../../../modules/vulkan/pipeline/vktPipelineCreationFeedbackTests.cpp#L1070-L1440) | Creates compute pipelines and checks their pipeline and stage feedback |
| Registration | [`createTestsInternal`](../../../modules/vulkan/pipeline/vktPipelineCreationFeedbackTests.cpp#L1444-L1504) | Registers graphics cases for all construction types and compute cases for monolithic only |
| Public entry points | [`createCreationFeedbackTests` and `addPipelineBinaryCreationFeedbackTests`](../../../modules/vulkan/pipeline/vktPipelineCreationFeedbackTests.cpp#L1506-L1520) | Places cache and binary variants below their respective roots |
| Vulkan feedback specification | [Pipeline Creation Feedback](../../../../vulkan-docs/src/chapters/pipelines.adoc#pipelines-creation-feedback) | Defines feedback structure, validity, optional stage reporting, flags, and duration |
| Pipeline creation validity | [Graphics pipeline feedback count](../../../../vulkan-docs/src/chapters/pipelines.adoc#L4161-L4166) and [compute pipeline feedback count](../../../../vulkan-docs/src/chapters/pipelines.adoc#L1004-L1009) | Constrains nonzero stage-feedback counts |
