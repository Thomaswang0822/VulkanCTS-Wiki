# Understanding Brief: Pipeline binaries

## One-Sentence Test Purpose

The `pipeline_binary` test category checks whether Vulkan can create, export, consume, and validate pipeline binary data while preserving the required pipeline behavior and API status results.

## Background Knowledge

A pipeline binary is opaque implementation data associated with pipeline creation. Vulkan exposes handles, keys, and serialized data for that binary, but the test must treat the contents as uninterpreted bytes. A successful binary lookup therefore matters through the pipeline that consumes it, the returned key or data size, and the Vulkan result code.

The pipeline construction type selects how CTS builds the pipeline before it obtains or consumes binary data. The same binary operation can be exercised with monolithic, fast-linked-library, and pipeline-library construction paths, while some compute and ray-tracing cases are registered only for the monolithic path.

## One Concrete Example

A representative `dedicated.graphics_pipeline_from_internal_cache` case creates a graphics pipeline with vertex and fragment shaders, obtains binaries from the implementation's internal cache, destroys the original pipeline and shader module, and creates a replacement pipeline from the retrieved binary data. It renders a small scene and compares the result with the expected output. The comparison tests whether the binary can stand in for the original pipeline state, rather than whether the test can interpret the binary bytes.

## End-to-End Test Flow

```text
[host] choose a PipelineConstructionType and a registered binary operation
[host] require VK_KHR_pipeline_binary and any ray-tracing or pipeline-library extensions
[host] create shader modules, pipeline layouts, resources, and a pipeline where the case needs one
[host] create pipeline binaries from a pipeline, retrieve keys/data, or prepare binary input
[host] create or execute a replacement graphics, compute, or ray-tracing pipeline
[device] execute the selected pipeline when the case has observable work
[host] wait for completion, compare output data, or check the required Vulkan result and size
```

The error-contract cases stop after checking `VK_INCOMPLETE`, `VK_ERROR_NOT_ENOUGH_SPACE_KHR`, or valid destruction of `VK_NULL_HANDLE`. Internal-cache cases destroy the original pipeline before using retrieved data. Ray-tracing cases may build a pipeline library and require the acceleration-structure and buffer-device-address functionality.

## Generated Test Artifacts and Bound Resources

| Resource or artifact | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|---|---:|---:|---:|---:|---|
| `VkPipelineBinaryKHR` handles | yes | consumed by pipeline creation | implementation-defined | keys/data queried | Objects under test |
| `VkPipelineBinaryKeyKHR` and serialized data | queried or supplied by host | passed to Vulkan | consumed by pipeline creation | yes | Exercise key/data contracts |
| Graphics, compute, or ray-tracing pipeline descriptions | yes | yes | used by the selected pipeline | sometimes | Establish the source or replacement pipeline |
| Shader modules and pipeline layouts | yes | yes | execute in observable cases | no | Supply valid pipeline inputs |
| Output buffers or images | yes | yes | written by graphics or compute work | yes where the case compares output | Detect a behavior change after binary reuse |

The shaders support valid pipeline creation and observable work. Binary identity, key validity, data-size handling, and pipeline reuse are the tested behavior; shader arithmetic is not an independent subject.

## What Is Checked

- Basic graphics and compute binary cases compare or validate pipeline creation after binary serialization and retrieval.
- `dedicated` checks unique key pairs, valid keys, internal-cache creation, zero-binary-count creation, incomplete creation, insufficient output space, and null-binary destruction.
- Ray-tracing dedicated cases exercise binary creation from an internal cache, another pipeline, serialized data, and pipeline-library variants.
- The implementation requires `VK_KHR_pipeline_binary`; internal-cache cases require the `pipelineBinaryInternalCache` property, and ray-tracing cases require `VK_KHR_acceleration_structure`, `VK_KHR_buffer_device_address`, and `VK_KHR_ray_tracing_pipeline`.

## Behavior Parameter Identification

> **Behavior parameter:** direct registered test family
>
> **Candidate values:** `graphics_tests`, `pipeline_from_get_data`, `compute_tests`, `creation_feedback`, `dedicated`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `graphics_tests` | Binary-backed graphics pipeline creation or output equivalence is incorrect. |
| `pipeline_from_get_data` | Serialized binary data cannot be consumed as required, or the resulting pipeline is not equivalent. |
| `compute_tests` | Binary-backed compute pipeline creation or execution is incorrect. |
| `creation_feedback` | Binary-backed pipeline creation reports or preserves creation feedback incorrectly. |
| `dedicated` | A binary key, handle, data-size, internal-cache, zero-count, error, or ray-tracing contract is incorrect. |

## Important Variations and Special Cases

- The graphics matrix uses vertex+fragment, vertex+geometry+fragment, and vertex+tessellation-control+tessellation-evaluation+fragment stage combinations.
- `compute_tests` and all monolithic-only dedicated leaves are not repeated for the other construction roots.
- The mustpass split currently contains 16 leaves under `pipeline_library`, 16 under `fast_linked_library`, and 14 under `no_queues`; the no-queues file covers binary shader-stage cases rather than the main binary-operation families.
- Geometry, tessellation, ray-tracing, acceleration-structure, buffer-device-address, and pipeline-library cases are pruned when their source requirements are unavailable.

## Source Mapping

| Topic | Source link | Why it matters |
|---|---|---|
| Category registration | [`createChildren`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L94-L158) | Creates `pipeline_binary` for non-shader-object construction paths |
| Basic binary families | [`addPipelineBinaryBasicTests`](../../../modules/vulkan/pipeline/vktPipelineCacheTests.cpp#L2461-L2466) | Reuses the binary mode graphics, data, and monolithic compute matrix |
| Creation feedback family | [`addPipelineBinaryCreationFeedbackTests`](../../../modules/vulkan/pipeline/vktPipelineCreationFeedbackTests.cpp#L1513-L1520) | Adds binary-mode creation-feedback cases |
| Dedicated registration | [`addPipelineBinaryDedicatedTests`](../../../modules/vulkan/pipeline/vktPipelineBinaryTests.cpp#L1470-L1528) | Defines the dedicated families and monolithic-only leaves |
| Support and instance selection | [`BaseTestCase::checkSupport`](../../../modules/vulkan/pipeline/vktPipelineBinaryTests.cpp#L1415-L1465) | Shows extension, property, construction, and implementation selection gates |
| Vulkan pipeline binary proposal | [VK_KHR_pipeline_binary](../../../../vulkan-docs/src/proposals/VK_KHR_pipeline_binary.adoc) | Defines the extension model and binary operations used by these tests |

## Questions / Risk Points for User Audit

- The rewritten pair preserves the legacy `vktPipelineBinaryTests.md` page and documents the existing `pipeline_binary` registration and mustpass split.
- The mustpass files available in this checkout use `fast-linked-library.txt`, `pipeline-library.txt`, and `no-queues.txt`; the source registration also describes monolithic coverage, so counts should be read as file-scoped evidence rather than a single category total.

## Conversion Notes for Final Wiki Rewrite

Use `direct registered test family` as the primary behavioral axis. Keep the parseable tree at one concrete construction root, then explain monolithic-only leaves and the three mustpass-file scopes in tables and pruning notes. Copy the failure-cause mapping table into `Binary.md` and write fresh cause analysis there.
