# vktDataGraphPipelineCacheTests

This page documents the implementation file for the `dEQP-VK.data_graph.cache` tests.

## Overview

`vktDataGraphPipelineCacheTests.cpp` verifies data graph pipeline cache behavior. The tests create one or more data graph pipelines with a `VkPipelineCache`, inspect pipeline-creation feedback, exercise cache hits and misses, and cover `VK_PIPELINE_CREATE_FAIL_ON_PIPELINE_COMPILE_REQUIRED_BIT_EXT` plus early-return behavior for batched creation.

## Role of File

- **Registration file:** yes. It registers the direct children under `data_graph.cache`.
- **Implementation file:** yes. It implements cache-aware pipeline creation and dispatch tests.

## Source Code Links

| Item | Evidence |
|------|----------|
| `cache` root child registration | [vktDataGraphTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphTests.cpp#L43-L45) |
| Cache subgroup registration | [vktDataGraphPipelineCacheTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L851-L855) |
| Nested create-pipeline registration | [vktDataGraphPipelineCacheTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L834-L838) |
| Cache support check | [vktDataGraphPipelineCacheTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L129-L146) |

## Registration Hierarchy

```text
data_graph.cache
├── create_pipeline
└── submit_pipeline
```

## Test Families

### create_pipeline — Cache hit, miss, and failure behavior

The `create_pipeline` branch contains two nested groups, `single_call` and `multi_calls`, registered by `createPipelineTests()` [vktDataGraphPipelineCacheTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L834-L838). `single_call` registers three cache-mode sequences for each shared `TestParams` value: all hit after fill, miss without early return, and miss with early return [vktDataGraphPipelineCacheTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L796-L820). `multi_calls` registers a fill-hit-miss-hit sequence for each shared `TestParams` value [vktDataGraphPipelineCacheTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L822-L832).

The multi-call implementation creates a separate pipeline cache for each pipeline, uses the fill cache as a reference for hit cases, switches to an empty cache for miss cases, and checks the `VK_PIPELINE_CREATION_FEEDBACK_APPLICATION_PIPELINE_CACHE_HIT_BIT` against expected hit or miss behavior [vktDataGraphPipelineCacheTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L148-L344). For miss cases where failure is expected, it uses `VK_PIPELINE_CREATE_FAIL_ON_PIPELINE_COMPILE_REQUIRED_BIT_EXT`, expects `VK_PIPELINE_COMPILE_REQUIRED_EXT`, and checks that the returned pipeline handle is null [vktDataGraphPipelineCacheTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L283-L340).

The single-call implementation prepares multiple `VkDataGraphPipelineCreateInfoARM` entries, changes the input stride mode in the miss-specific parameter set to force a cache miss, optionally adds early-return-on-failure, creates the batch with `createDataGraphPipelinesARM`, and checks which pipeline handles are valid or null [vktDataGraphPipelineCacheTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L347-L577).

### submit_pipeline — Cache-backed dispatch

`submit_pipeline` registers a fill-hit-hit sequence for each shared `TestParams` value [vktDataGraphPipelineCacheTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L840-L848). The implementation creates provider-backed data graph tests, tensors, descriptor sets, cache-backed pipelines, and sessions [vktDataGraphPipelineCacheTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L580-L716). It records binds and `cmdDispatchDataGraphARM` calls for each pipeline, submits once, waits, and verifies output tensor data [vktDataGraphPipelineCacheTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L747-L792).

## Parameter Dimensions

| Dimension | Observed values / source |
|-----------|--------------------------|
| Pipeline mode | `FILL_CACHE`, `HIT_CACHE`, and `MISS_CACHE` [vktDataGraphPipelineCacheTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L66-L71) |
| Failure mode | `IGNORE_CACHE_MISS`, `FAIL_ON_CACHE_MISS_NO_EARLY_RETURN`, and `FAIL_ON_CACHE_MISS_EARLY_RETURN` [vktDataGraphPipelineCacheTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L73-L78) |
| Single-call sequences | fill-hit-hit-hit, fill-hit-miss-hit without early return, and fill-hit-miss-hit with early return [vktDataGraphPipelineCacheTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L796-L820) |
| Multi-call sequence | fill-hit-miss-hit without early return [vktDataGraphPipelineCacheTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L822-L832) |
| Submit sequence | fill-hit-hit [vktDataGraphPipelineCacheTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L840-L848) |
| Shared graph parameters | All cache families iterate over `getTestParamsVariations()` [vktDataGraphPipelineCacheTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L798-L819), [vktDataGraphPipelineCacheTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L824-L831), [vktDataGraphPipelineCacheTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L842-L848) |

## Support and Feature Requirements

Cache tests first query `VkPhysicalDevicePipelineCreationCacheControlFeatures` and require `pipelineCreationCacheControl` [vktDataGraphPipelineCacheTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L129-L143). They then delegate to `TestParams::checkSupport()` for `VK_ARM_data_graph`, `VK_ARM_tensors`, required data graph and tensor features, and conditional `tensorNonPacked` support [vktDataGraphPipelineCacheTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L145-L146), [vktDataGraphTestUtil.hpp](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.hpp#L220-L256).

## Verification Methods

- Cache-hit expectations are checked with `VK_PIPELINE_CREATION_FEEDBACK_APPLICATION_PIPELINE_CACHE_HIT_BIT` after ensuring feedback is valid [vktDataGraphPipelineCacheTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L289-L315).
- Expected cache misses with compile-required behavior use `VK_CHECK_COMPILE_REQUIRED` and then verify the pipeline handle is `VK_NULL_HANDLE` [vktDataGraphPipelineCacheTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L333-L340).
- Batched pipeline creation checks for `VK_PIPELINE_COMPILE_REQUIRED_EXT` when the batch contains a miss and failure-on-miss is enabled [vktDataGraphPipelineCacheTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L540-L551).
- Batched early-return behavior is verified by expecting null handles from the first early-return miss onward [vktDataGraphPipelineCacheTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L553-L575).
- Submit tests validate output tensors after dispatch by calling each provider test's `verifyData()` method [vktDataGraphPipelineCacheTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L769-L790).

## Test Principles

- Use a filled cache as the reference for intended hit cases and an empty or changed-parameter pipeline as the miss source [vktDataGraphPipelineCacheTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L218-L226), [vktDataGraphPipelineCacheTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L390-L413).
- Check both creation-only cache semantics and execution of cache-backed pipelines.
- Cover both one-at-a-time creation and batch creation paths for data graph pipelines.

## Notes and Uncertainties

The file defines `IGNORE_CACHE_MISS`, but the registered sequences observed in this source use the failure-on-miss modes for create tests and submit tests [vktDataGraphPipelineCacheTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L796-L848). This page describes the registered cases rather than unregistered enum possibilities.