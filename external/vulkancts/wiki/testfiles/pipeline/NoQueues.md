## Overview

**Core question:** Can a Vulkan implementation create pipeline state without queues, preserve it through a cache or opaque binary representation, and use the recreated state correctly on a device that has a queue?

- [`vktPipelineNoQueuesTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineNoQueuesTests.cpp#L1) implements the independent `pipeline.no_queues` test family. It is a direct child of `pipeline`, rather than a construction-type variant.
- Each test case creates a first logical device with zero queues, creates pipeline or shader state there, captures the selected reusable representation, then creates a second device with one queue to consume that representation and execute work.
- The direct intermediate nodes `pipeline_cache`, `pipeline_binary`, and `shader_binary` select the representation captured on the zero-queue device. The test case leaves select the shader stage.
- This page documents the two-device timeline, stage and feature matrix, output-buffer oracle, and what each family can localize when it fails.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- `VkDeviceCreateInfo::queueCreateInfoCount` controls the queue-create-info array supplied during logical-device creation. This test deliberately supplies zero queue create infos for its first pass. It can create pipeline-related objects on that device, but it cannot submit the work used for the final oracle.
- A `VkPipelineCache` is an optional input to pipeline creation. For compute pipelines, the [pipeline creation command](../../../../vulkan-docs/src/chapters/pipelines.adoc#pipelines-compute) accepts either `VK_NULL_HANDLE` or a valid cache handle; the test creates a cache on both passes and uses retrieved data as the second cache's initial data for `pipeline_cache`.
- `VK_KHR_pipeline_binary` and `VK_EXT_shader_object` expose opaque binary representations through different APIs. The former supplies pipeline binary keys and data to a subsequent pipeline creation path, while the latter retrieves binary data from `VkShaderEXT` objects and uses it to create later shader objects.
- Pipeline creation and pipeline execution are separate observations in this family. The zero-queue pass validates creation and data retrieval. The one-queue pass validates that the recreated pipeline or shaders can drive the selected commands to the expected output.

## Registration Hierarchy

```text
pipeline.no_queues
├── pipeline_cache
├── pipeline_binary
└── shader_binary
```

[`createNoQueuesTests()`](../../../modules/vulkan/pipeline/vktPipelineNoQueuesTests.cpp#L1723-L1785) registers all three intermediate nodes below the one independent root. The VK mustpass file has 36 executable leaves: 14 each for `pipeline_cache` and `pipeline_binary`, plus eight non-ray-tracing leaves for `shader_binary`, in [`pipeline/no-queues.txt`](../../../mustpass/main/vk-default/pipeline/no-queues.txt#L1-L36).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Intermediate node | `pipeline_cache`, `pipeline_binary`, `shader_binary` | Selects cache-data reuse, pipeline-binary reuse, or shader-object-binary reuse. | [`ttCases[]`](../../../modules/vulkan/pipeline/vktPipelineNoQueuesTests.cpp#L1741-L1745) |
| Test case leaf stage | `compute`, `raygen`, `isect`, `ahit`, `chit`, `miss`, `callable`, `vertex`, `fragment`, `geometry`, `tessctrl`, `tesseval`, `task`, `mesh` | Chooses the selected shader stage and its pipeline or command path. | [`stageCases[]`](../../../modules/vulkan/pipeline/vktPipelineNoQueuesTests.cpp#L1733-L1739) |
| Device pass | first pass with zero queues; second pass with one universal queue | Separates state capture from execution and result checking. | [two-pass device creation](../../../modules/vulkan/pipeline/vktPipelineNoQueuesTests.cpp#L648-L671) |
| Work configuration | 8 by 8 threads for ordinary stages; 32 by 1 for geometry, tessellation, task, and mesh; two workgroups in both dimensions | Determines the dispatch or render extent and the number of output elements inspected. | [case setup](../../../modules/vulkan/pipeline/vktPipelineNoQueuesTests.cpp#L1758-L1778) |
| Pipeline form | compute, graphics, ray tracing, or mesh | Selects the bind point, supporting stages, and execution command. | [pipeline selection](../../../modules/vulkan/pipeline/vktPipelineNoQueuesTests.cpp#L703-L713), [stage construction](../../../modules/vulkan/pipeline/vktPipelineNoQueuesTests.cpp#L935-L1263) |

## Behavior Parameters

The primary behavioral axis is the direct registered test family. Each family changes the state representation transferred between the zero-queue and one-queue device passes. The stage leaf is a secondary coverage dimension.

### `pipeline_cache`: recreate from pipeline-cache data

The first pass creates a `VkPipelineCache` and passes it to pipeline creation. After successful creation, it queries `vkGetPipelineCacheData`, saves nonempty cache data, and creates the second pass's cache with that data as `pInitialData`. The second pass then creates the same selected pipeline with its cache handle and executes it. The test observes both cache-compatible creation and output behavior; it does not inspect the opaque cache bytes.

### `pipeline_binary`: recreate from pipeline binary keys and data

The first pass creates the selected pipeline with `VK_PIPELINE_CREATE_2_CAPTURE_DATA_BIT_KHR` through `VkPipelineCreateFlags2CreateInfoKHR`. It obtains pipeline binary handles, then retrieves a `VkPipelineBinaryKeyKHR` and data for every binary. On the second pass, it builds `VkPipelineBinaryKeysAndDataKHR`, creates pipeline binaries from those values, attaches `VkPipelineBinaryInfoKHR` to pipeline creation, and executes the resulting pipeline.

### `shader_binary`: recreate shader objects from shader binary data

The first pass creates `VkShaderEXT` objects from the generated SPIR-V and retrieves each object's binary data through `vkGetShaderBinaryDataEXT`. The second pass creates shader objects from the saved binary data, binds the resulting shader-object state, and executes the compute or graphics command path. This family excludes KHR ray-tracing stages because the registration loop skips them for `TT_SHADER_BINARY`.

## Shader Analysis

The source generates stage-specific GLSL in [`initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineNoQueuesTests.cpp#L281-L591), including supporting graphics, mesh, and ray-tracing stages where required. Each selected shader samples a texture at an out-of-range coordinate and stores `1.0` when the opaque-white border color is returned. The program supplies a deterministic execution oracle after state reconstruction, but the test does not compare shader algorithms or SPIR-V forms. A representative shader walkthrough or embedded disassembly would therefore obscure the cache and binary-reuse property under test.

## Runtime Execution and Result Checking

1. [`checkSupport()`](../../../modules/vulkan/pipeline/vktPipelineNoQueuesTests.cpp#L220-L279) requires Vulkan 1.1 and `VK_KHR_maintenance9` for all leaves. It adds stage-specific feature and extension requirements, `VK_KHR_pipeline_binary` for `pipeline_binary`, and `VK_EXT_shader_object` for `shader_binary`.
2. The test generates the selected shader artifacts, then enters the two-iteration loop. Iteration zero creates a logical device with `queueCreateInfoCount = 0`; iteration one creates a device with one universal-queue create info. The source constructs both devices from the same physical-device features and enabled extensions.
3. Both passes create layouts, descriptors, a sampler with `VK_BORDER_COLOR_FLOAT_OPAQUE_WHITE`, a sampled image, storage buffers, and the selected compute, graphics, mesh, or ray-tracing pipeline state. The first pass either passes the pipeline-cache handle, captures pipeline binary data after pipeline creation, or creates shader objects from SPIR-V.
4. At the end of iteration zero, the selected branch retrieves cache data with `vkGetPipelineCacheData`, pipeline binary keys/data through `PipelineBinaryWrapper` and `vkGetPipelineBinaryDataKHR`, or per-shader binary data with `vkGetShaderBinaryDataEXT`. Iteration one supplies that saved representation to its corresponding creation path.
5. Only iteration one obtains the queue, records a command buffer, binds the recreated pipeline or shader objects, and dispatches, draws, draws mesh tasks, or traces rays. It submits that command buffer and waits for completion.
6. The source invalidates the output allocation and checks every selected output element. Any element other than `1.0f` marks the case as failed. The final image or buffer check confirms the reconstructed state can execute work, but it cannot distinguish a reuse defect from every pipeline-state or stage-execution defect on its own.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `pipeline_cache` | Zero-queue pipeline creation, pipeline-cache data export/import, or execution of the recreated pipeline |
| `pipeline_binary` | Pipeline-binary extraction, key/data pairing, binary-backed pipeline creation, or execution of the recreated pipeline |
| `shader_binary` | Shader-binary extraction, binary-backed shader-object creation, shader binding, or execution of the recreated shader |

### Cause Analysis

#### Zero-queue pipeline creation, pipeline-cache data export/import, or execution of the recreated pipeline

**Possible failure symptoms:** A `pipeline_cache` leaf fails while creating the pipeline or cache, retrieving cache data, creating the second-pass pipeline with the initialized cache, or while checking an output element after submission.

**Possible implementation causes:** The implementation may reject valid pipeline creation when the first `VkDeviceCreateInfo` has no queues, fail to preserve usable pipeline-cache state through the retrieval and initial-data sequence, or create executable state that behaves incorrectly on the second device. The final buffer comparison includes pipeline execution, so source-level or driver investigation is needed to separate cache reuse from stage construction, descriptor state, or execution faults.

#### Pipeline-binary extraction, key/data pairing, binary-backed pipeline creation, or execution of the recreated pipeline

**Possible failure symptoms:** A `pipeline_binary` leaf fails while extracting binaries or data, creating pipeline binaries from saved keys/data, creating the second pipeline, or validating its output.

**Possible implementation causes:** The implementation may return a binary count, key, or data blob that it cannot consume later; associate a key with incompatible data; mishandle `VkPipelineBinaryInfoKHR`; or construct an executable pipeline that differs from the source-created pipeline. The CTS cannot inspect opaque pipeline-binary contents, and its execution oracle covers both binary consumption and ordinary pipeline execution, so it cannot identify an internal serialization component without further investigation.

#### Shader-binary extraction, binary-backed shader-object creation, shader binding, or execution of the recreated shader

**Possible failure symptoms:** A `shader_binary` leaf fails when retrieving shader binary data, creating second-pass `VkShaderEXT` objects with `VK_SHADER_CODE_TYPE_BINARY_EXT`, binding shader-object state, or comparing output.

**Possible implementation causes:** The implementation may serialize shader object state incompletely, reject valid binary data that it produced, lose stage-chain or specialization state during recreation, or bind or execute reconstructed shader objects incorrectly. The source prunes ray-tracing leaves before this path, so a failure in this family localizes to the supported compute, graphics, task, or mesh shader-object path rather than KHR ray tracing.

## Case Pruning

### Requirement-based pruning

- All leaves require Vulkan 1.1 and `VK_KHR_maintenance9`.
- Ray-tracing stage leaves require `VK_KHR_acceleration_structure`, `VK_KHR_ray_tracing_pipeline`, `rayTracingPipeline`, and `accelerationStructure`; acceleration-structure-consuming ray stages additionally build the needed descriptor and structures.
- Task and mesh leaves require the relevant `VK_EXT_mesh_shader` features. Geometry and tessellation leaves require their core features, and vertex or fragment paths require storage-and-atomic support in their respective shader stage.
- `pipeline_binary` requires `VK_KHR_pipeline_binary`; `shader_binary` requires `VK_EXT_shader_object`.

### Design-based pruning

- `shader_binary` omits `raygen`, `isect`, `ahit`, `chit`, `miss`, and `callable`, leaving eight leaves instead of 14.
- Each family chooses one representative stage at a time rather than combining all legal stage combinations. Supporting stages exist only where needed to form a valid graphics, mesh, or ray-tracing pipeline.
- The zero-queue device never records or submits work. The one-queue device supplies the single execution and output-validation pass.
- The source registers this VK-only root inside `#ifndef CTS_USES_VULKANSC`; it does not create a Vulkan SC family.

## Key Takeaways

- `pipeline.no_queues` separates creation and state capture on a zero-queue device from execution and output checking on a one-queue device.
- Its three intermediate nodes test different reusable representations: pipeline cache data, pipeline binary keys/data, and shader binary data.
- The 14-stage registration matrix exercises compute, graphics, mesh, and ray-tracing construction where the selected family supports them. The shader-binary family removes the six ray-tracing stage leaves.
- An output mismatch proves that the second-pass state did not execute as expected, but the shared end-to-end oracle cannot isolate opaque-data reuse from every pipeline or shader execution cause.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Support gate | [`NoQueuesTestCase::checkSupport()`](../../../modules/vulkan/pipeline/vktPipelineNoQueuesTests.cpp#L220-L279) | Defines baseline, extension, feature, and stage prerequisites. |
| Shader generation | [`NoQueuesTestCase::initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineNoQueuesTests.cpp#L281-L591) | Generates the selected stage artifact and its deterministic output store. |
| Two-device setup | [`NoQueuesTestInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineNoQueuesTests.cpp#L614-L690) | Creates the zero-queue or one-queue device and initializes cache handling. |
| Binary consumption setup | [pipeline-binary recreation](../../../modules/vulkan/pipeline/vktPipelineNoQueuesTests.cpp#L814-L842) | Builds `VkPipelineBinaryInfoKHR` from the saved keys and data. |
| Capture branch | [cache and binary retrieval](../../../modules/vulkan/pipeline/vktPipelineNoQueuesTests.cpp#L1265-L1319) | Retrieves the selected reusable representation after the first pass. |
| Execution oracle | [submission and output comparison](../../../modules/vulkan/pipeline/vktPipelineNoQueuesTests.cpp#L1658-L1710) | Runs second-pass work and requires every output value to equal `1.0f`. |
| Family registration | [`createNoQueuesTests()`](../../../modules/vulkan/pipeline/vktPipelineNoQueuesTests.cpp#L1723-L1785) | Registers the three intermediate nodes and stage leaves. |
| Mustpass scope | [`pipeline/no-queues.txt`](../../../mustpass/main/vk-default/pipeline/no-queues.txt#L1-L37) | Lists the 37 VK executable leaves. |
| Pipeline cache contract | [Pipeline Cache](../../../../vulkan-docs/src/chapters/pipelines.adoc#pipelines-cache) | Defines the pipeline-cache concept used by the cache branch. |
| Compute pipeline cache parameter | [Compute Pipelines](../../../../vulkan-docs/src/chapters/pipelines.adoc#pipelines-compute) | Documents the valid `pipelineCache` input form used by compute leaves. |
