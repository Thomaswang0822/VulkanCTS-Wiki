## Overview

**Core question:** Can Vulkan create, retrieve, and reuse pipeline binaries while preserving required pipeline behavior and binary-operation results?

- `vktPipelineBinaryTests.cpp` implements the `dedicated` test family under the `pipeline_binary` test category. `vktPipelineTests.cpp` also registers binary-mode families from the cache and creation-feedback implementations in the same category.
- The construction-specific `pipeline_binary` category covers graphics and compute pipeline binary round trips, pipeline creation from retrieved data, binary-mode creation feedback, and dedicated key, data-size, internal-cache, zero-count, null-handle, and ray-tracing cases. A separate `pipeline.no_queues.pipeline_binary` family exercises pipeline-binary recreation for each shader stage without queue submission.
- The test treats binary contents as opaque. It observes API return codes, queried keys and sizes, successful replacement-pipeline creation, and graphics or compute output where an executable pipeline can provide an observable result.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- `VK_KHR_pipeline_binary` exposes opaque pipeline-binary handles, keys, and data. Applications can create binary handles from pipeline state or supplied data, retrieve a key and data from a handle, and use binary information when creating a pipeline. The extension does not make binary bytes portable pipeline source.
- A pipeline construction type selects the CTS wrapper used to create the source pipeline. The binary category is registered only when the construction type is not a shader-object variant. Some cases are further limited to `PIPELINE_CONSTRUCTION_TYPE_MONOLITHIC`.
- A pipeline's executable behavior remains the observable contract. When a case creates a replacement pipeline from binary data, the test checks output or successful required operations rather than the implementation-defined binary representation.

## Registration Hierarchy

```text
pipeline.monolithic.pipeline_binary
├── graphics_tests
├── pipeline_from_get_data
├── compute_tests
├── creation_feedback
└── dedicated

pipeline.no_queues.pipeline_binary
```

[`createChildren`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L94-L158) creates the construction-specific `pipeline_binary` category only for non-shader-object construction paths, then adds the basic, creation-feedback, and dedicated registrations in that order. The first fenced root uses the concrete monolithic path so the registration validator can resolve it. `compute_tests` and the extra dedicated leaves are monolithic-only; the other construction roots retain the compatible graphics and dedicated coverage. Independently, [`createNoQueuesTests`](../../../modules/vulkan/pipeline/vktPipelineNoQueuesTests.cpp#L1723-L1750) registers `pipeline_binary` under `pipeline.no_queues`; its direct test case leaves are the 14 shader stages listed below.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Pipeline construction type | `PIPELINE_CONSTRUCTION_TYPE_MONOLITHIC`, fast-linked-library, pipeline-library | Selects the pipeline-construction wrapper. The source does not register this category for shader-object variants; compute and several dedicated cases are monolithic-only. | [`createChildren`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L94-L158), [`addPipelineBinaryDedicatedTests`](../../../modules/vulkan/pipeline/vktPipelineBinaryTests.cpp#L1470-L1528) |
| Binary test family | `graphics_tests`, `pipeline_from_get_data`, `compute_tests`, `creation_feedback`, `dedicated` | Selects the binary operation or binary-mode validation contract. | [category registration](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L151-L157) |
| Graphics stage combination | `vertex_stage_fragment_stage`, `vertex_stage_geometry_stage_fragment_stage`, `vertex_stage_tessellation_control_stage_tessellation_evaluation_stage_fragment_stage` | Changes the source graphics pipeline whose binary data is created or consumed. | [`createPipelineBlobTestsInternal`](../../../modules/vulkan/pipeline/vktPipelineCacheTests.cpp#L2297-L2339) |
| Dedicated operation | `unique_key_pairs`, `graphics_pipeline_from_internal_cache`, `valid_key`, monolithic-only error, zero-count, compute, graphics, and ray-tracing leaves | Selects a direct pipeline-binary contract such as key identity, data retrieval, error status, or replacement-pipeline construction. | [dedicated registration](../../../modules/vulkan/pipeline/vktPipelineBinaryTests.cpp#L1474-L1525) |
| Pipeline source | pipeline, internal cache, binary data, or pipeline library | Changes the source used to create a binary or the input used to construct a replacement pipeline. | [`TestType`](../../../modules/vulkan/pipeline/vktPipelineBinaryTests.cpp#L56-L71), [support checks](../../../modules/vulkan/pipeline/vktPipelineBinaryTests.cpp#L1415-L1444) |
| No-queue shader stage | `compute`, `raygen`, `isect`, `ahit`, `chit`, `miss`, `callable`, `vertex`, `fragment`, `geometry`, `tessctrl`, `tesseval`, `task`, `mesh` | Selects the stage used to create a pipeline twice: first with SPIR-V and capture enabled, then from the retrieved pipeline binary. | [`stageCases`](../../../modules/vulkan/pipeline/vktPipelineNoQueuesTests.cpp#L1733-L1749), [binary recreation](../../../modules/vulkan/pipeline/vktPipelineNoQueuesTests.cpp#L814-L842) |

The primary behavioral axis is the direct registered test family. Each family changes the pipeline-binary operation or the result contract being checked.

## Behavior Parameters

### `graphics_tests`: graphics binary round trips

The cache implementation runs its graphics matrix in `TestMode::BINARY`. It creates graphics pipelines for the three registered stage combinations, obtains binary-backed pipeline state, and checks that the binary path can produce the required graphics result. Geometry and tessellation variants add their supported stages without changing the binary-reuse question.

### `pipeline_from_get_data`: construction from retrieved binary data

This family uses `PipelineFromBlobsTest` with the same three graphics stage combinations. It retrieves binary data from an earlier pipeline path, supplies that data to a later creation path, and checks that the resulting graphics pipeline can be created and used as required.

### `compute_tests`: monolithic compute binary cases

The shared helper adds this family only for `PIPELINE_CONSTRUCTION_TYPE_MONOLITHIC`. It exercises normal compute binary use and a zero-binary-count variation. The restriction prevents repeating compute coverage across graphics pipeline library construction types.

### `creation_feedback`: binary-mode creation feedback

[`addPipelineBinaryCreationFeedbackTests`](../../../modules/vulkan/pipeline/vktPipelineCreationFeedbackTests.cpp#L1513-L1520) delegates this test family to the creation-feedback implementation with `TestMode::BINARY`. Its graphics subfamily is present across supported construction paths, while its compute subfamily follows the monolithic restriction.

### `dedicated`: direct binary API contracts

The dedicated family contains three leaves for every registered construction path: `unique_key_pairs`, `graphics_pipeline_from_internal_cache`, and `valid_key`. The monolithic path adds:

| Dedicated test case leaf group | Leaves | Property checked |
|---|---|---|
| API result and lifetime | `create_incomplete`, `not_enough_space`, `destroy_null_binary` | Required incomplete, insufficient-space, and null-handle behavior |
| Zero-count creation | `compute_pipeline_with_zero_binary_count`, `graphics_pipeline_with_zero_binary_count` | Pipeline creation with zero supplied binary handles |
| Internal cache | `compute_pipeline_from_internal_cache`, `graphics_pipeline_from_internal_cache`, `ray_tracing_pipeline_from_internal_cache` | Retrieval and later use of data held by the implementation's internal cache |
| Ray tracing | `ray_tracing_pipeline_from_pipeline`, `ray_tracing_pipeline_from_binary_data`, `ray_tracing_pipeline_with_zero_binary_count` | Binary creation or consumption for a ray-tracing pipeline |
| Ray-tracing pipeline library | `ray_tracing_pipeline_library_from_internal_cache`, `ray_tracing_pipeline_library_from_pipeline`, `ray_tracing_pipeline_library_from_binary_data` | The same source choices with `usePipelineLibrary` enabled |

### `pipeline.no_queues.pipeline_binary`: stage-specific creation without submission

This separately registered family creates each supported stage pipeline in two iterations. The first iteration creates a pipeline from SPIR-V with `VK_PIPELINE_CREATE_2_CAPTURE_DATA_BIT_KHR`, retrieves every binary key and data blob, and destroys the pipeline. The second recreates binary handles from those key/data pairs and creates the equivalent pipeline with shader modules omitted. The family does not submit commands or compare shader output, so success proves pipeline creation and binary consumption for the selected stage, not executable equivalence.

## Shader Analysis

The shaders provide valid graphics, compute, and ray-tracing pipelines so binary operations can be observed through pipeline creation or execution. The test does not isolate shader behavior as a subject. It does not need a representative shader walkthrough or generated SPIR-V listing: binary keys, binary data, and replacement-pipeline behavior are the relevant artifacts.

## Runtime Execution and Result Checking

- The construction-specific registration creates `pipeline_binary` after confirming that the selected construction type is not a shader-object variant. The three registration helpers then add basic, creation-feedback, and dedicated families. The separate no-queue registration adds its own `pipeline_binary` family under `pipeline.no_queues` without a pipeline-construction-type wrapper.
- Dedicated instances require `VK_KHR_pipeline_binary` and call `checkPipelineConstructionRequirements`. Ray-tracing leaves additionally require `VK_KHR_acceleration_structure`, `VK_KHR_buffer_device_address`, and `VK_KHR_ray_tracing_pipeline`; pipeline-library variants require `VK_KHR_pipeline_library`. Internal-cache leaves skip if `pipelineBinaryInternalCache` is false.
- A simple error-contract instance creates a compute pipeline with `VK_PIPELINE_CREATE_2_CAPTURE_DATA_BIT_KHR`. `create_incomplete` first asks Vulkan for the binary count, supplies capacity for one binary when multiple binaries are available, and passes only on `VK_INCOMPLETE`. `not_enough_space` queries binary data size, provides one byte less, and requires `VK_ERROR_NOT_ENOUGH_SPACE_KHR` plus the corrected size. `destroy_null_binary` calls `vkDestroyPipelineBinaryKHR` with `VK_NULL_HANDLE`.
- Internal-cache and binary-data cases create a source pipeline, obtain binary handles, keys, or data through `PipelineBinaryWrapper`, and build a replacement pipeline. Where the implementation executes work, the test submits the relevant graphics, compute, or ray-tracing commands and compares the output or checks successful required use. The no-queue family stops after the second pipeline creation and therefore has no execution oracle.
- `BaseTestCase::createInstance` selects the instance implementation for each `TestType`, so each registered dedicated leaf reaches the matching API or executable-work path.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `graphics_tests` | Binary-backed graphics pipeline creation or output equivalence is incorrect. |
| `pipeline_from_get_data` | Serialized binary data cannot be consumed as required, or the resulting pipeline is not equivalent. |
| `compute_tests` | Binary-backed compute pipeline creation or execution is incorrect. |
| `creation_feedback` | Binary-backed pipeline creation reports or preserves creation feedback incorrectly. |
| `dedicated` | A binary key, handle, data-size, internal-cache, zero-count, error, or ray-tracing contract is incorrect. |
| `pipeline.no_queues.pipeline_binary` | Pipeline binary retrieval, binary-handle reconstruction, or pipeline recreation fails for the selected shader stage; no execution result is checked. |

### Cause Analysis

#### Binary creation or reuse changes executable behavior

**Possible failure symptoms:** A graphics image or compute-buffer comparison differs after a binary-backed replacement pipeline is used, or the required replacement pipeline cannot be created.

**Possible implementation causes:** The implementation may associate binary data with incompatible pipeline state, fail to preserve executable state while serializing or consuming binary data, or select the wrong internal-cache entry. CTS observes API behavior and output, so driver or compiler investigation is needed to locate the internal mismatch.

#### Binary key or serialized-data handling is inconsistent

**Possible failure symptoms:** `unique_key_pairs` reports a quality warning because byte-identical binary blobs have different same-sized keys, `valid_key` finds a zero-length or over-limit key, retrieved data cannot create the expected pipeline, or the queried size changes unexpectedly.

**Possible implementation causes:** The implementation may assign inconsistent keys to identical serialized data, return a key outside the required size range, return data that it cannot consume, pair a key with the wrong binary, or mishandle the two-call size/data retrieval sequence. `unique_key_pairs` does not require different pipelines to produce different binary bytes or keys, and reports inconsistent keys for identical data as a quality warning rather than a hard failure. The test cannot inspect opaque binary bytes, so it cannot identify the serialization component that caused the failure.

#### Required error or zero-count behavior is wrong

**Possible failure symptoms:** `create_incomplete` does not return `VK_INCOMPLETE` in its tested condition, `not_enough_space` does not return `VK_ERROR_NOT_ENOUGH_SPACE_KHR` with the corrected size, a zero-count pipeline path fails unexpectedly, or null-binary destruction does not complete.

**Possible implementation causes:** The implementation may report binary counts incorrectly, fail to update output-size data, reject a valid zero-count setup, or mishandle the null-handle destruction contract. The direct API checks localize the failure to the tested operation but source-level investigation is needed to identify the implementation path.

#### Internal-cache, ray-tracing, or pipeline-library binary paths are unavailable or incorrect

**Possible failure symptoms:** An internal-cache leaf runs despite unsupported `pipelineBinaryInternalCache`, a supported internal-cache operation cannot produce usable data, or a ray-tracing or pipeline-library replacement pipeline cannot be used as required.

**Possible implementation causes:** The implementation may expose an inconsistent property, fail to preserve state required by the selected ray-tracing or library configuration, or mishandle binary data after the source pipeline is destroyed. The source's support gates distinguish unavailable features from a failure in a supported execution path; they do not reveal the internal binary representation.

## Case Pruning

### Requirement-based pruning

- All documented paths require `VK_KHR_pipeline_binary`. Construction-specific paths also require a construction type accepted by `checkPipelineConstructionRequirements`; no-queue paths instead require `VK_KHR_maintenance9` and stage-specific features.
- `pipeline_binary` is absent for shader-object construction paths because [`createChildren`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L149-L158) guards its registration with `isNotShaderObjectVariant`.
- Geometry and tessellation graphics leaves require the corresponding device features in the reused cache implementation.
- Ray-tracing leaves require `VK_KHR_acceleration_structure`, `VK_KHR_buffer_device_address`, and `VK_KHR_ray_tracing_pipeline`. Pipeline-library leaves also require `VK_KHR_pipeline_library`.
- Internal-cache leaves require `pipelineBinaryInternalCache`.
- No-queue leaves require the selected shader stage and its supporting features. Ray-tracing stages require the ray-tracing and acceleration-structure extensions; task and mesh require `VK_EXT_mesh_shader`; geometry and tessellation require their corresponding core features. Storage-buffer writes from vertex, geometry, tessellation, or fragment stages require the matching pipeline-store feature.

### Design-based pruning

- `compute_tests` and the extra dedicated error, zero-count, compute, and ray-tracing leaves are registered only for `PIPELINE_CONSTRUCTION_TYPE_MONOLITHIC`.
- The graphics stage matrix uses three stage chains instead of every legal graphics-pipeline combination.
- The `pipeline_binary` category deliberately reuses cache and creation-feedback implementations under one root. Cache-only families such as incomplete cache data and cache merging do not become binary families.
- The mustpass split under `external/vulkancts/mustpass/main/vk-default/pipeline/` contains 33 construction-specific leaves in `monolithic/monolithic.txt`, 16 in `fast-linked-library.txt`, 16 in `pipeline-library.txt`, and 14 separate shader-stage leaves in `no-queues.txt`. These file-scoped counts do not replace the source registration matrix.

## Key Takeaways

- Pipeline binary tests validate opaque binary operations through API results and the behavior of resulting pipelines.
- `pipeline_binary` gathers reused binary-mode cache and creation-feedback coverage with dedicated binary API cases under one test category.
- The monolithic construction path carries the broader compute, error, zero-count, and ray-tracing dedicated set.
- The separate no-queue family validates stage-specific binary capture and pipeline recreation but does not submit the recreated pipeline.
- Source support checks separate missing extension, feature, property, and construction-type prerequisites from failures in supported binary operations.
- A failed output comparison points to an incompatible binary-backed pipeline path, but opaque binary data prevents CTS from identifying the implementation component that produced it.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Category registration | [`createChildren`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L94-L158) | Creates and populates the `pipeline_binary` category for eligible construction types |
| Basic binary registration | [`addPipelineBinaryBasicTests`](../../../modules/vulkan/pipeline/vktPipelineCacheTests.cpp#L2461-L2466) | Reuses the graphics, retrieved-data, and monolithic compute binary matrix |
| Basic graphics/data matrix | [`createPipelineBlobTestsInternal`](../../../modules/vulkan/pipeline/vktPipelineCacheTests.cpp#L2297-L2374) | Defines the graphics stage chains, retrieved-data family, and monolithic compute gating |
| Binary creation feedback | [`addPipelineBinaryCreationFeedbackTests`](../../../modules/vulkan/pipeline/vktPipelineCreationFeedbackTests.cpp#L1513-L1520) | Adds creation-feedback coverage in `TestMode::BINARY` |
| Dedicated test types and basic error paths | [`TestType` and `BasicComputePipelineTestInstance::iterate`](../../../modules/vulkan/pipeline/vktPipelineBinaryTests.cpp#L56-L201) | Defines direct error and zero-count operations |
| Support and instance selection | [`BaseTestCase::checkSupport` and `createInstance`](../../../modules/vulkan/pipeline/vktPipelineBinaryTests.cpp#L1415-L1465) | Defines extension/property gates and maps each `TestType` to an instance |
| Dedicated registration | [`addPipelineBinaryDedicatedTests`](../../../modules/vulkan/pipeline/vktPipelineBinaryTests.cpp#L1470-L1528) | Defines always-present and monolithic-only dedicated leaves |
| No-queue binary implementation | [`NoQueuesTestCase` binary path](../../../modules/vulkan/pipeline/vktPipelineNoQueuesTests.cpp#L270-L278) | Requires pipeline-binary and maintenance9 support before the two-iteration creation path |
| No-queue binary recreation | [binary key/data consumption](../../../modules/vulkan/pipeline/vktPipelineNoQueuesTests.cpp#L814-L842) | Reconstructs binary handles and supplies them to the second pipeline creation |
| No-queue registration | [`createNoQueuesTests`](../../../modules/vulkan/pipeline/vktPipelineNoQueuesTests.cpp#L1723-L1750) | Registers the 14 stage leaves under the separate `pipeline.no_queues.pipeline_binary` family |
| Vulkan pipeline binary proposal | [VK_KHR_pipeline_binary](../../../../vulkan-docs/src/proposals/VK_KHR_pipeline_binary.adoc) | Provides the extension model for opaque pipeline binary operations |
