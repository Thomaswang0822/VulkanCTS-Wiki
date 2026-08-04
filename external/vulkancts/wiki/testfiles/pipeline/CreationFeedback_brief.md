# Understanding Brief: Pipeline Creation Feedback

## One-Sentence Test Purpose

This test checks whether Vulkan reports creation feedback for graphics and compute pipelines consistently with cache use, derivative creation, pipeline binaries, and the requested pipeline-stage feedback array.

## Background Knowledge

`VkPipelineCreationFeedbackCreateInfoEXT` requests two related observations: one `VkPipelineCreationFeedbackEXT` for the pipeline and an optional array for its stages. The `VALID` bit determines whether the remaining fields are meaningful. A valid report may identify a pipeline-cache hit or use of a base pipeline, and it reports a creation duration in nanoseconds.

The feedback is advisory. An implementation may omit per-stage feedback, including when the whole pipeline came from an application pipeline cache. The CTS therefore checks the contracts that are observable from the returned flags and values rather than requiring a particular duration or a per-stage report in every case.

## One Concrete Example

A representative monolithic graphics case uses `vertex_stage_fragment_stage`:

1. The test chains feedback structures to the graphics pipeline create information and allocates storage for the pipeline and stage reports.
2. It creates a pipeline with no cache hit, then creates a derivative and a cached pipeline using the same cache.
3. It destroys selected pipelines between creations so a later creation can test reuse without relying on a still-live pipeline object.
4. It checks `VALID`, cache-hit, base-pipeline-acceleration, and duration fields for the final pipeline and its vertex and fragment stages.

The geometry and tessellation variants use the same feedback flow with additional stage reports.

## End-to-End Test Flow

```text
[host] choose cache or binary mode, pipeline construction type, shader stages, cache setting, and lifetime setting
[host] create shader modules, pipeline layout, render pass, feedback storage, and the cache or pipeline-binary inputs
[host] create a no-cache/reference pipeline, a derivative pipeline, and a cached or binary-backed pipeline
[host] destroy pipelines according to the delayed-destroy variant
[host] inspect pipeline and stage feedback records
[host] compare each record with the Vulkan feedback contracts and return pass, quality warning, or failure
```

Compute cases create descriptor-backed storage-buffer resources and three compute pipelines. They record feedback for the compute pipeline and its single compute stage, then apply the same checks.

## Generated Test Artifacts and Bound Resources

| Resource or artifact | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|---|---:|---:|---:|---:|---|
| `VkPipelineCreationFeedbackCreateInfoEXT` and feedback arrays | yes | passed through pipeline create info | written by implementation during creation | yes | Observations under test |
| Graphics shader modules | yes | yes | executed by graphics pipeline | no | Provide vertex, fragment, geometry, or tessellation stages |
| Graphics render targets and vertex buffer | yes | yes | rendered | feedback test does not compare image output | Minimal pipeline construction workload |
| Compute descriptor set and storage buffers | yes | yes | compute stage accesses buffers | no | Minimal compute pipeline construction workload |
| `VkPipelineCache` | yes in `TestMode::CACHE` | passed to creation | consulted during creation | no | Exercises cache-hit feedback |
| `VkPipelineBinaryInfoKHR` | yes in `TestMode::BINARY` | passed to creation | consumed during creation | no | Exercises binary-backed creation feedback |

## What Is Checked

- A record without `VK_PIPELINE_CREATION_FEEDBACK_VALID_BIT_EXT` must not carry other flags.
- A cache-disabled or no-cache pipeline must not report `VK_PIPELINE_CREATION_FEEDBACK_APPLICATION_PIPELINE_CACHE_HIT_BIT_EXT`.
- `VK_PIPELINE_CREATION_FEEDBACK_BASE_PIPELINE_ACCELERATION_BIT_EXT` is accepted only for the derivative case that supplies a base pipeline.
- Cached or binary-backed cases warn when no pipeline or relevant stage reports a cache hit; this is a quality warning, not a hard failure.
- A zero duration produces a quality warning. The graphics test gives this warning only for pipeline parts marked heavy, while the compute test reports it for valid compute feedback.
- The test logs pipeline and stage flags and durations. It does not require a fixed duration value.

## Behavior Parameter Identification

> **Behavior parameter:** direct test family
>
> **Candidate values:** `graphics_tests`, `compute_tests`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `graphics_tests` | Graphics pipeline or per-stage feedback violates the validity, cache-hit, base-pipeline, or feedback-count contract. |
| `compute_tests` | Compute pipeline or compute-stage feedback violates the same contract for a single-stage pipeline. |

## Important Variations and Special Cases

- Graphics cases use `vertex_stage_fragment_stage`, `vertex_stage_geometry_stage_fragment_stage`, and `vertex_stage_tessellation_control_stage_tessellation_evaluation_stage_fragment_stage`.
- Cache-mode graphics cases vary no-cache, delayed destruction, and `zero_out_feedback_cout`. Binary-mode cases use `VK_KHR_pipeline_binary`; cache-only variants are filtered from that mode.
- `compute_tests` is registered only below `pipeline.monolithic.creation_feedback`. The source skips repeated compute coverage for non-monolithic construction types.
- Geometry and tessellation cases require their corresponding device features. The source requires `VK_EXT_pipeline_creation_feedback` for every case and `VK_KHR_pipeline_binary` for binary mode.
- The source excludes this functionality from Vulkan SC through the existing `CTS_USES_VULKANSC` guard in the registration path.

## Source Mapping

| Topic | Source link | Why it matters |
|---|---|---|
| Parameters and generated names | [`TestParam`](../../../modules/vulkan/pipeline/vktPipelineCreationFeedbackTests.cpp#L118-L180) | Defines mode, stages, cache, lifetime, and feedback-count dimensions |
| Feature requirements | [`BaseTestCase::checkSupport`](../../../modules/vulkan/pipeline/vktPipelineCreationFeedbackTests.cpp#L190-L210) | Shows extension and binary requirements |
| Graphics creation lifecycle | [`GraphicsTestInstance::GraphicsTestInstance`](../../../modules/vulkan/pipeline/vktPipelineCreationFeedbackTests.cpp#L450-L669) | Creates reference, derivative, and cached or binary-backed pipelines |
| Feedback-chain setup | [`preparePipelineWrapper`](../../../modules/vulkan/pipeline/vktPipelineCreationFeedbackTests.cpp#L671-L835) | Sets pipeline-part and stage feedback counts and pointers |
| Graphics validation | [`GraphicsTestInstance::verifyTestResult`](../../../modules/vulkan/pipeline/vktPipelineCreationFeedbackTests.cpp#L836-L1030) | Checks flags, cache hits, base acceleration, and durations |
| Compute validation | [`ComputeTestInstance::verifyTestResult`](../../../modules/vulkan/pipeline/vktPipelineCreationFeedbackTests.cpp#L1278-L1440) | Applies the feedback contract to pipeline and compute-stage records |
| Registration | [`createTestsInternal`](../../../modules/vulkan/pipeline/vktPipelineCreationFeedbackTests.cpp#L1444-L1504) | Defines the two direct families and their construction-type gating |
| Vulkan feedback contract | [Pipeline Creation Feedback](../../../../vulkan-docs/src/chapters/pipelines.adoc#pipelines-creation-feedback) | Defines structure fields, validity, cache-hit, base-pipeline, and duration semantics |

## Questions / Risk Points for User Audit

- Is the distinction between a hard feedback-contract failure and a quality warning clear?
- Should the final page show the complete ten-case graphics matrix, or is the parameter table sufficient?
- Is the monolithic-only `compute_tests` boundary clear for readers comparing construction types?

## Conversion Notes for Final Wiki Rewrite

Keep `direct test family` as the primary behavioral axis. Use one graphics lifecycle as the concrete runtime example, then distinguish compute validation and binary mode where their control flow differs. Preserve the failure table verbatim in the final page under `## Failure Meaning` and add source-grounded cause analysis there.
