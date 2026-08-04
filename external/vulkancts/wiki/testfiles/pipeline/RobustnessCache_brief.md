# Understanding Brief: Pipeline Robustness Cache

## One-Sentence Test Purpose

This test checks whether pipeline-level robustness settings remain effective when a graphics or compute pipeline is created through a `VkPipelineCache`, including out-of-bounds buffer and image accesses.

## Background Knowledge

A pipeline cache is an opaque Vulkan object used while creating pipelines. The implementation may reuse compatible pipeline data from the cache, but cache reuse must not change the behavior required by the pipeline create information. This test therefore creates a reference pipeline and a second pipeline with a `VkPipelineRobustnessCreateInfoEXT` chained into creation, while using the same cache.

Pipeline robustness selects the out-of-bounds behavior for storage buffers, uniform buffers, vertex inputs, and images. The pipeline robustness feature enables per-pipeline selection; the `robustBufferAccess2` and `robustImageAccess2` features provide the stronger robustness2 behaviors used by the `robustness2` family.

## One Concrete Example

A representative monolithic graphics case is `pipeline.monolithic.pipeline_cache.robustness2.storage`:

1. The host creates a storage buffer containing four `0.5` values and an index buffer.
2. It creates a normal graphics pipeline and a second pipeline with `storageBuffers` set to `VK_PIPELINE_ROBUSTNESS_BUFFER_BEHAVIOR_ROBUST_BUFFER_ACCESS_2_EXT`, both using the same empty `VkPipelineCache`.
3. The first draw reads index zero and establishes the expected `0.5` output.
4. The host changes the index to an out-of-bounds value, draws with the robustness2 pipeline, copies the 32×32 render target to a host-visible buffer, and checks the result.

The same pattern is used for uniform buffers and images. Monolithic storage, uniform, and image cases also have `_compute` leaves; vertex-input cases are graphics-only.

## End-to-End Test Flow

```text
[host] choose robustness family, resource type, graphics or compute path, and pipeline construction type
[host] require the pipeline robustness extension/features needed by the selected family
[host] create buffers, an input image and sampler when needed, a 32x32 render target, descriptors, and synchronization objects
[host] create a pipeline cache and a normal pipeline, then create a second pipeline with VkPipelineRobustnessCreateInfoEXT chained into creation
[host] execute the normal pipeline once with an in-bounds index and verify the 0.5 result
[host] replace the index with an out-of-bounds value and execute the robustness pipeline
[device] perform the graphics draw or compute dispatch and write the output image
[host] wait for completion, copy the output image to a host-visible buffer, invalidate the allocation, and inspect every pixel
[host] require the expected robust result and return pass or fail
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The source generates minimal GLSL for compute cases and vertex/fragment GLSL for graphics cases. The shaders read one of the selected resource types and write a value to an output image. Their purpose is to make the robustness access observable; the test does not compare shader binaries or test a particular shader algorithm.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|---|---:|---:|---:|---:|---|
| Input storage or uniform buffer | yes | yes | read | no | Tests buffer robustness for `STORAGE` and `UNIFORM`. |
| Vertex buffer | yes, for `VERTEX_INPUT` | yes | read by vertex input | no | Tests an out-of-bounds vertex attribute index. |
| Input storage image and sampler | yes, for `IMAGE` | yes | read | no | Tests robust image access. |
| Index buffer | yes | yes | read | yes, through the resulting image | Selects an in-bounds or out-of-bounds element. |
| 32×32 render target or storage image | yes | yes | written by graphics or compute | yes | Carries the accessed value to host validation. |
| `VkPipelineCache` | yes | passed to pipeline creation | implementation-defined cache use | no | Exercises robustness settings together with cache-backed creation. |

## What Is Checked

- The normal pipeline must produce the initialized `0.5` value for every output pixel.
- The robustness pipeline is executed after the index is changed to `15` for vertex input or `999` for the other resource types.
- `robustness2` cases require zero for out-of-bounds buffer/image results, except that out-of-bounds image components may be any value of `0.0` or `1.0`, matching the source predicate.
- `robustness` cases execute the robust pipeline after the index update, but the source has no second image comparison for that family. A failure therefore detects an execution or API error, while the final-pixel predicate belongs to `robustness2`.

## Behavior Parameter Identification

> **Behavior parameter:** robustness resource family
>
> **Candidate values:** `robustness.storage`, `robustness.uniform`, `robustness.vertex_input`, `robustness.image`, `robustness2.storage`, `robustness2.uniform`, `robustness2.vertex_input`, `robustness2.image`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `robustness.storage` | Pipeline-cache creation or `storageBuffers` robustness does not preserve the required out-of-bounds behavior. |
| `robustness.uniform` | Pipeline-cache creation or `uniformBuffers` robustness does not preserve the required out-of-bounds behavior. |
| `robustness.vertex_input` | Pipeline-cache creation or `vertexInputs` robustness mishandles an out-of-bounds vertex attribute access. |
| `robustness.image` | Pipeline-cache creation or `images` robustness mishandles an out-of-bounds image access. |
| `robustness2.storage` | Robustness2 storage-buffer behavior or its feature/extension integration is mishandled when using a pipeline cache. |
| `robustness2.uniform` | Robustness2 uniform-buffer behavior or its feature/extension integration is mishandled when using a pipeline cache. |
| `robustness2.vertex_input` | Robustness2 vertex-input behavior or its feature/extension integration is mishandled when using a pipeline cache. |
| `robustness2.image` | Robustness2 image behavior or its feature/extension integration is mishandled when using a pipeline cache. |

## Important Variations and Special Cases

- `robustness` uses `VK_EXT_pipeline_robustness` and the `ROBUST_BUFFER_ACCESS_EXT` or `ROBUST_IMAGE_ACCESS_EXT` behavior values.
- `robustness2` additionally requires `VK_KHR_robustness2` or `VK_EXT_robustness2`; it checks `robustBufferAccess2` for buffers and `robustImageAccess2` for images.
- The source registers monolithic, pipeline-library, and fast-linked-library construction roots, but excludes shader-object variants and Vulkan SC through the surrounding registration guards.
- Compute variants are registered only for `PIPELINE_CONSTRUCTION_TYPE_MONOLITHIC` and only for `STORAGE`, `UNIFORM`, and `IMAGE`.

## Source Mapping

| Topic | Source link | Why it matters |
|---|---|---|
| Test registration | [`createPipelineRobustnessCacheTests()`](../../../modules/vulkan/pipeline/vktPipelineRobustnessCacheTests.cpp#L813-L860) | Defines `pipeline_cache`, the two robustness families, four resource types, and monolithic compute leaves. |
| Support checks | [`PipelineCacheTestCase::checkSupport()`](../../../modules/vulkan/pipeline/vktPipelineRobustnessCacheTests.cpp#L628-L708) | Requires the extensions and feature bits for each selected behavior. |
| Resource and pipeline setup | [`PipelineCacheTestInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineRobustnessCacheTests.cpp#L279-L625) | Creates descriptors, cache, normal/robust pipelines, executes them, and validates output. |
| Shader generation | [`PipelineCacheTestCase::initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineRobustnessCacheTests.cpp#L710-L809) | Shows how each resource type is read by graphics or compute shaders. |
| Pipeline robustness contract | [Pipeline robustness](../../../../vulkan-docs/src/chapters/pipelines.adoc#VkPipelineRobustnessCreateInfo) | Defines the scope of `VkPipelineRobustnessCreateInfo` and its per-resource behavior members. |
| Feature contract | [Pipeline robustness feature](../../../../vulkan-docs/src/chapters/features.adoc#features-pipelineRobustness) and [robustness2 features](../../../../vulkan-docs/src/chapters/features.adoc#features-robustBufferAccess2) | Grounds feature enablement and robustness2 guarantees. |
| Pipeline cache contract | [Pipeline Cache](../../../../vulkan-docs/src/chapters/pipelines.adoc#pipelines-cache) | Grounds opaque cache reuse during pipeline creation. |

## Questions / Risk Points for User Audit

- Is the distinction between the `robustness` and `robustness2` behavior values clear enough?
- Does the example make clear that the cache is not interpreted by the test and that output behavior is the observable result?
- Should the final page include separate mustpass counts for the three construction roots?

## Conversion Notes for Final Wiki Rewrite

Use resource type plus robustness family as the primary behavioral axis. Preserve the resource table and the failure-cause mapping in the final page, then add fresh cause analysis. Keep the shader section concise because the generated shaders only expose the selected out-of-bounds access; do not add a shader or SPIR-V walkthrough.
