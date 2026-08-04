# Understanding Brief: Pipeline Derivatives

## One-Sentence Test Purpose

This test checks whether Vulkan can create compute pipeline derivatives through a previously created parent handle and an earlier entry in the same `vkCreateComputePipelines` call.

## Background Knowledge

A pipeline derivative is a child pipeline created from a parent pipeline that is expected to share substantial pipeline state. Vulkan creates a derivative with `VK_PIPELINE_CREATE_DERIVATIVE_BIT`; exactly one of `basePipelineHandle` and `basePipelineIndex` identifies its parent. A handle names a pipeline created earlier, while an index names an earlier element in the current creation array.

The parent must have `VK_PIPELINE_CREATE_ALLOW_DERIVATIVES_BIT`. The `VK_KHR_maintenance5` variant supplies the equivalent flags through `VkPipelineCreateFlags2CreateInfoKHR`. Vulkan SC does not support pipeline derivatives.

## One Concrete Example

`derivative_by_handle` compiles a trivial `comp` shader and creates a compute pipeline with `VK_PIPELINE_CREATE_ALLOW_DERIVATIVES_BIT`. It then reuses the same create information with `VK_PIPELINE_CREATE_DERIVATIVE_BIT` and sets `basePipelineHandle` to the first pipeline. The test passes after both creation calls return and the RAII wrappers destroy the pipelines.

## End-to-End Test Flow

```text
[host] compile the minimal `comp` shader and create a shader module and pipeline layout
[host] create a base compute pipeline marked `VK_PIPELINE_CREATE_ALLOW_DERIVATIVES_BIT`
[host] create a derivative by parent handle, or create a base-and-derivative pair with base index 0
[host] destroy raw index-path pipelines, or let RAII wrappers release handle-path pipelines
[host] pass if the required creation calls complete without an error or crash
```

The test never dispatches the compute shader. Pipeline creation is the observable operation.

## Generated Test Artifacts and Bound Resources

| Resource or artifact | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|---|---:|---:|---:|---:|---|
| `comp` shader module | yes | pipeline creation input | no dispatch | no | Supplies the required compute stage with no workload-dependent behavior |
| `VkPipelineLayout` | yes | pipeline creation input | no dispatch | no | Provides the empty layout required by each compute pipeline create info |
| Base `VkPipeline` | yes | referenced by derivative create info in handle path | no dispatch | no | Supplies `basePipelineHandle` and carries `ALLOW_DERIVATIVES` |
| `VkComputePipelineCreateInfo[2]` | yes for index path | passed to one creation call | no dispatch | no | Places the base at index 0 and the derivative at index 1 |

## What Is Checked

- `derivative_by_handle` creates a parent pipeline, then creates a child with `basePipelineHandle`.
- `derivative_by_handle_maintenance5` uses the same handle relationship with `VK_KHR_maintenance5` flags2 values.
- `derivative_by_index` creates two pipelines in one call and sets the child `basePipelineIndex` to `0`.
- The functions return pass only after the CTS pipeline-creation wrappers have completed; they do not inspect shader output.

## Behavior Parameter Identification

> **Behavior parameter:** test case leaf
>
> **Candidate values:** `derivative_by_handle`, `derivative_by_handle_maintenance5`, `derivative_by_index`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `derivative_by_handle` | Compute pipeline creation rejects or mishandles a derivative whose parent is supplied through `basePipelineHandle`. |
| `derivative_by_handle_maintenance5` | The `VK_KHR_maintenance5` flags2 path rejects or mishandles the same parent-handle derivative relationship. |
| `derivative_by_index` | Batched compute pipeline creation rejects or mishandles an earlier parent selected through `basePipelineIndex`. |

## Important Variations and Special Cases

- The default Vulkan mustpass file has three leaves below `pipeline.monolithic.derivative.compute`, one per test case leaf.
- `derivative_by_handle_maintenance5` is omitted under `CTS_USES_VULKANSC` and requires `VK_KHR_maintenance5` through `checkSupport`.
- `createPipelineTests` registers this test family only for `PIPELINE_CONSTRUCTION_TYPE_MONOLITHIC`; the source avoids repeating compute pipeline tests for other construction types.
- The source uses one do-nothing compute shader for all leaves, so shader execution and result readback do not distinguish the cases.

## Source Mapping

| Topic | Source link | Why it matters |
|---|---|---|
| Maintenance5 capability gate | [`checkSupport`](../../../modules/vulkan/pipeline/vktPipelineDerivativeTests.cpp#L60-L64) | Requires `VK_KHR_maintenance5` for its dedicated leaf |
| Minimal compute program | [`initComputeDerivativePrograms`](../../../modules/vulkan/pipeline/vktPipelineDerivativeTests.cpp#L66-L78) | Defines the shared no-op `comp` shader |
| Parent-handle creation | [`testComputeDerivativeByHandle`](../../../modules/vulkan/pipeline/vktPipelineDerivativeTests.cpp#L80-L127) | Creates the parent and child in separate calls and selects flags2 when requested |
| Parent-index creation | [`testComputeDerivativeByIndex`](../../../modules/vulkan/pipeline/vktPipelineDerivativeTests.cpp#L129-L166) | Creates both entries in one call with base index `0` |
| Leaf registration | [`createDerivativeTests`](../../../modules/vulkan/pipeline/vktPipelineDerivativeTests.cpp#L170-L186) | Registers the exact `compute` leaves |
| Monolithic-only registration | [`createPipelineTests`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L198-L205) | Places the family under the monolithic construction path |
| Derivative contract | [Pipeline Derivatives](../../../../vulkan-docs/src/chapters/pipelines.adoc#L7940-L7967) | Defines parent selection, ordering, and `ALLOW_DERIVATIVES` requirements |

## Questions / Risk Points for User Audit

- Is it clear that successful pipeline creation, rather than compute execution, is the pass condition?
- Is the distinction between the handle and index parent-selection paths clear?
- Is the Vulkan SC exclusion clear enough for readers comparing CTS variants?

## Conversion Notes for Final Wiki Rewrite

Use the test case leaf as the behavioral axis. Preserve the failure table verbatim under `## Failure Meaning`, explain the two creation timelines in the runtime section, and state in `## Shader Analysis` that the no-op shader is only a creation fixture.
