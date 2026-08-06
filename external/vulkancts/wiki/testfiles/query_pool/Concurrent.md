## Overview

**Core question:** Can one workload use multiple query types and keep each query's result scoped to the commands it measures?

- This page covers the `query_pool.concurrent_queries` test family registered by [`vktQueryPoolTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L42-L54) and implemented in [`vktQueryPoolConcurrentTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L55-L61).
- The test has two test case leaves: `primary_command_buffer` and `secondary_command_buffer`.
- Each case creates up to three query pools, one each for occlusion, pipeline statistics, and timestamp queries. The device must support at least two of these query types.
- Each pool has two query slots. Slot `0` measures an empty interval and must be zero; occlusion and pipeline-statistics slot `0` results are available after their begin/end commands, while the unwritten timestamp slot remains unavailable. Slot `1` measures the triangle draw and must become non-zero and available.

## Background Knowledge

- A Vulkan query has both a numerical result and an availability state. [`vkCmdResetQueryPool`](../../../../vulkan-docs/src/chapters/queries.adoc#L478-L505) makes the selected queries unavailable; ending an occlusion or pipeline statistics query, or writing a timestamp, makes its result available.
- Occlusion and pipeline statistics queries measure commands between `vkCmdBeginQuery` and `vkCmdEndQuery`. Timestamp queries write a timestamp at a selected pipeline stage. Vulkan permits active queries of different types to overlap in one command buffer, which is the behavior this test exercises.
- A secondary command buffer can execute while an occlusion query is active in its primary command buffer when `inheritedQueries` is enabled. The secondary buffer must provide conservative query inheritance settings, as described by the Vulkan query-operation rules ([`queries.adoc`](../../../../vulkan-docs/src/chapters/queries.adoc#L648-L672)).

## Registration Hierarchy

```text
query_pool.concurrent_queries
├── primary_command_buffer
└── secondary_command_buffer
```

`QueryPoolConcurrentTests::init()` adds both test case leaves ([`vktQueryPoolConcurrentTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L906-L918)). The same two paths appear in the Vulkan and Vulkan SC mustpass files: [`vk-default/query-pool.txt`](../../../mustpass/main/vk-default/query-pool.txt#L1-L2) and [`vksc-default/query-pool.txt`](../../../mustpass/main/vksc-default/query-pool.txt#L1-L2).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Command-buffer mode | `primary_command_buffer`, `secondary_command_buffer` | Selects whether the draw and query commands are recorded in one primary buffer or split between a primary and a secondary buffer. | [`QueryPoolConcurrentTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L912-L918) |
| Query type | `VK_QUERY_TYPE_OCCLUSION`, `VK_QUERY_TYPE_PIPELINE_STATISTICS`, `VK_QUERY_TYPE_TIMESTAMP` | Selects which query pools participate. Occlusion is counted as supported; pipeline statistics requires `pipelineStatisticsQuery`; timestamps require non-zero `timestampValidBits` on the universal queue family. | [`QueryType`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L55-L61), [`checkSupport()`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L858-L873) |
| Query slot | `0`, `1` | Pairs an empty capture with the draw capture in every supported pool. | [`PrimaryCommandBufferConcurrentTestInstance`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L261-L281) |
| Pipeline statistic | `VK_QUERY_PIPELINE_STATISTIC_FRAGMENT_SHADER_INVOCATIONS_BIT` | Limits pipeline statistics to fragment shader invocations. | [`PrimaryCommandBufferConcurrentTestInstance` constructor](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L310-L326) |
| Secondary occlusion inheritance | enabled or disabled by `inheritedQueries` | Chooses whether slot `1` occlusion begins in the primary around `vkCmdExecuteCommands`, or begins and ends inside the secondary buffer. | [`SecondaryCommandBufferConcurrentTestInstance::iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L614-L674) |

The test prunes unsupported query types at construction. It skips the case only when the support check finds fewer than two supported types and raises `NotSupportedError` with `Device does not support multiple query types` ([`checkSupport()`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L858-L873)).

## Behavior Parameters

The primary behavioral axis is command-buffer mode. Query types are a capability-dependent set inside each mode, while the two slots define the common validation contract.

### `primary_command_buffer` - all query activity in one primary buffer

The test allocates one primary command buffer and records the supported query types around a render pass. It begins occlusion and pipeline statistics queries for slot `0`, ends them without a draw, then starts slot `1`, draws one triangle, writes the slot `1` timestamp when supported, and ends the slot `1` occlusion and pipeline statistics queries ([`iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L333-L413)).

### `secondary_command_buffer` - query activity split across primary and secondary buffers

The secondary buffer binds the pipeline and vertex buffer, records the draw, records slot `1` pipeline statistics and timestamp commands, and handles slot `1` occlusion locally when inherited queries are disabled. The primary buffer resets the pools, captures the empty slot, begins inherited slot `1` occlusion when `inheritedQueries` is enabled, begins a render pass with `VK_SUBPASS_CONTENTS_SECONDARY_COMMAND_BUFFERS`, executes the secondary buffer, and ends the inherited query ([`iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L614-L735)).

### Query-type variations

- Occlusion is always included in the support count used by this test.
- Pipeline statistics is included only when `pipelineStatisticsQuery` is enabled, and the pool requests fragment shader invocation statistics.
- Timestamp is included only when the universal queue family reports `timestampValidBits > 0`.

The shared render setup creates 128 by 128 color and depth attachments, a graphics pipeline, and a vertex buffer containing one triangle ([`StateObjects::StateObjects()`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L63-L90)). The fragment shader writes a color and discards fragments whose integer `gl_FragCoord` coordinates have matching parity ([`initPrograms()`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L880-L900)). That gives the occlusion and fragment-invocation queries work to count.

## Shader Analysis

The shaders only provide the fixed draw workload. The test does not compare rendered pixels. The vertex shader passes through the input position, and the fragment shader writes its output while discarding alternating fragments. No shader walkthrough is needed to understand the query validation.

## Runtime Execution and Result Checking

### Primary mode

1. The test creates a primary command buffer and transitions the color and depth images for the render pass.
2. It records `vkCmdResetQueryPool` for every supported pool, resetting both slots. Vulkan defines reset queries as unavailable with undefined numerical results until the test records new query operations ([`queries.adoc`](../../../../vulkan-docs/src/chapters/queries.adoc#L478-L505)).
3. It begins slot `0` occlusion and pipeline statistics queries, ends them before any draw, then begins slot `1` for those same types.
4. It draws the triangle. If timestamps are supported, it writes slot `1` at `VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT`, then ends slot `1` occlusion and pipeline statistics queries.
5. It ends the render pass and submits the primary command buffer to the universal queue with `submitCommandsAndWait` ([`iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L404-L413)).
6. After the wait, it reads occlusion and pipeline statistics results with `VK_QUERY_RESULT_64_BIT`. It reads timestamps with `VK_QUERY_RESULT_64_BIT | VK_QUERY_RESULT_WITH_AVAILABILITY_BIT` ([`iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L419-L478)).

### Secondary mode

1. The test records the secondary command buffer with render-pass inheritance. Its `occlusionQueryEnable` field follows `inheritedQueries`; the query flags and pipeline-statistics inheritance mask are zero ([`iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L630-L643)).
2. The secondary buffer records the draw workload. It records slot `1` pipeline statistics and timestamp operations. It records slot `1` occlusion locally when the device does not support inherited queries.
3. The primary buffer resets all supported pools and records slot `0` occlusion and pipeline statistics begin/end before the render pass.
4. When inherited queries are supported, the primary begins slot `1` occlusion around `vkCmdExecuteCommands`; otherwise the secondary owns that slot. The primary executes the secondary buffer inside the render pass, ends the inherited query when needed, and submits the primary buffer ([`iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L676-L735)).
5. The host waits for submission completion, then applies the same result and availability checks as primary mode ([`iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L741-L846)).

### Slot pairing rule

The two slots are deliberately asymmetric:

| Slot | Recorded work | Occlusion / pipeline statistics | Timestamp result | Timestamp availability |
|------|---------------|----------------------------------|------------------|------------------------|
| `0` (`QUERY_INDEX_CAPTURE_EMPTY`) | Begin and end before the triangle draw, or reset without a timestamp write | `0` | `0` | `0` |
| `1` (`QUERY_INDEX_CAPTURE_DRAWCALL`) | Covers the triangle draw; timestamp is written at the color-output stage | non-zero | non-zero | non-zero |

The test uses exactly two slots in every supported pool ([`PrimaryCommandBufferConcurrentTestInstance`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L270-L280)). The slot pairing checks that one query type does not overwrite or leak into another capture interval.

For timestamps, the test asks `vkGetQueryPoolResults` for availability and expects `VK_NOT_READY` because slot `0` was reset but never written. Vulkan permits `vkGetQueryPoolResults` without `VK_QUERY_RESULT_WAIT_BIT` to return `VK_NOT_READY` when any requested query remains unavailable ([`queries.adoc`](../../../../vulkan-docs/src/chapters/queries.adoc#L1222-L1229), [`vktQueryPoolConcurrentTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L470-L515)). This is intentional and distinct from the occlusion and pipeline-statistics reads, which must return success after the queue wait.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `primary_command_buffer` | Incorrect query scoping or result handling when different query types overlap in one primary command buffer; a non-zero draw result or an unexpected empty-slot result indicates the capture boundaries or query state are wrong. |
| `secondary_command_buffer` | Incorrect query scoping across primary and secondary command buffers, including inherited occlusion-query handling, secondary inheritance state, or execution of the secondary draw. |

Both rows share the query-type and result-availability causes: a supported occlusion, pipeline statistics, or timestamp query may report the wrong slot value, availability, or return status.

### Cause Analysis

#### Query capture boundaries or cross-type interference

**Possible failure symptoms:** Slot `0` reports a non-zero occlusion or fragment-invocation count, slot `1` reports zero, or the completed occlusion/statistics read returns `VK_NOT_READY` after the submission wait. A timestamp may also have a non-zero or available slot `0`, or a zero or unavailable slot `1`.

**Possible implementation causes:** The driver or hardware may mishandle query state when different query types are active in the same command buffer, fail to scope begin/end operations to the selected query index, or fail to make a completed query result available. The source proves the observed checks; the exact implementation fault needs investigation if a failure occurs.

#### Primary and secondary command-buffer interaction

**Possible failure symptoms:** The primary and secondary cases disagree, or `secondary_command_buffer` produces an incorrect slot `1` occlusion result while pipeline statistics and timestamps pass. The symptom can occur with either inherited occlusion enabled or the local secondary-query path.

**Possible implementation causes:** A driver may mishandle query inheritance, the `occlusionQueryEnable` inheritance value, or the active-query interval spanning `vkCmdExecuteCommands`. Vulkan requires the secondary inheritance settings to describe conservative query behavior and requires a query to begin and end in the same command buffer, with the inherited-query exception for a primary executing secondary work ([`queries.adoc`](../../../../vulkan-docs/src/chapters/queries.adoc#L648-L672)). The precise faulty stage needs investigation from the failing log and implementation.

#### Timestamp availability and status

**Possible failure symptoms:** The timestamp result call returns success instead of `VK_NOT_READY`, slot `0` has a non-zero result or availability, or slot `1` has zero result or zero availability.

**Possible implementation causes:** The query may be incorrectly treated as available after reset, timestamp writes may fail to reach the requested pool slot, or result retrieval may mishandle the `(result, availability)` layout. Vulkan defines zero availability as not ready and non-zero availability as complete ([`queries.adoc`](../../../../vulkan-docs/src/chapters/queries.adoc#L1167-L1169), [`queries.adoc`](../../../../vulkan-docs/src/chapters/queries.adoc#L1222-L1229)). The test's expected `VK_NOT_READY` therefore checks the deliberately unwritten slot, not a failed submission.

## Case Pruning

- The support check counts occlusion, `pipelineStatisticsQuery`, and queue-family `timestampValidBits > 0`. It skips the test case with `NotSupportedError` when fewer than two query types are available.
- Unsupported query pools are not created, reset, or read. The remaining supported query types still run together.
- `inheritedQueries` changes only the ownership of the slot `1` occlusion query in the secondary case. It does not remove the secondary test case.

## Key Takeaways

- The test covers two command-buffer modes under the same `concurrent_queries` test family.
- It pairs an empty slot (`0`) with a draw slot (`1`) in each supported query pool. Zero and unavailable are the expected state for the empty pair; non-zero and available are expected for the draw pair.
- A queue wait must make the occlusion and pipeline-statistics results readable. The timestamp read intentionally returns `VK_NOT_READY` because one requested timestamp was never written.
- A failure means that at least one query type, slot boundary, availability state, or primary/secondary interaction did not follow the test's contract. It does not by itself identify whether the fault lies in the host, driver, compiler, or hardware.

## Source Reference Appendix

| Topic | Evidence |
|-------|----------|
| Query types and two-slot constants | [`vktQueryPoolConcurrentTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L55-L61), [`vktQueryPoolConcurrentTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L270-L281) |
| Primary query-pool creation and command flow | [`vktQueryPoolConcurrentTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L283-L331), [`vktQueryPoolConcurrentTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L333-L413) |
| Primary result checks | [`vktQueryPoolConcurrentTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L419-L524) |
| Secondary inheritance and split recording | [`vktQueryPoolConcurrentTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L614-L735) |
| Secondary result checks | [`vktQueryPoolConcurrentTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L741-L846) |
| Support filtering and registration | [`vktQueryPoolConcurrentTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L849-L918) |
| Vulkan mustpass coverage | [`vk-default/query-pool.txt`](../../../mustpass/main/vk-default/query-pool.txt#L1-L2), [`vksc-default/query-pool.txt`](../../../mustpass/main/vksc-default/query-pool.txt#L1-L2) |
| Query state, reset, active queries, and result availability | [`queries.adoc`](../../../../vulkan-docs/src/chapters/queries.adoc#L478-L505), [`queries.adoc`](../../../../vulkan-docs/src/chapters/queries.adoc#L648-L672), [`queries.adoc`](../../../../vulkan-docs/src/chapters/queries.adoc#L1222-L1229) |
