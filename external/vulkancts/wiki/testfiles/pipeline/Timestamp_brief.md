# Understanding Brief: pipeline timestamp tests

## Purpose

The `timestamp` test family checks whether Vulkan timestamp queries report usable device timestamps for selected pipeline stages and transfer commands. The family also covers query availability, host-side query reset, calibrated host and device time domains, query-result copies, and queue-family support.

The test records timestamps with `vkCmdWriteTimestamp`, submits the command buffer, reads the query pool with `vkGetQueryPoolResults`, masks values to the queue's `timestampValidBits`, and compares only stage pairs for which the Vulkan ordering rules make comparison meaningful. It does not compare rendered pixels or shader results.

## Background Knowledge

A timestamp query pool stores timestamp values written by device commands. `timestampValidBits` describes the valid low-order bits for a queue family, so the CTS masks values before comparison. `VK_QUERY_RESULT_WITH_AVAILABILITY_BIT` adds an availability value for each result. `VK_EXT_host_query_reset` lets the host reset queries with `vkResetQueryPool`.

Vulkan defines stage ordering for timestamp writes, but not every pair of stage flags is directly comparable. The CTS therefore compares a pair when one stage is `TOP_OF_PIPE`, one is `BOTTOM_OF_PIPE`, or both flags are equal. The calibrated cases use `VK_KHR_calibrated_timestamps` or `VK_EXT_calibrated_timestamps` to compare device and host time domains within a measured deviation and tolerance.

## Test Shape

The source registers six direct groups below `pipeline.timestamp`. The graphics groups are present for every supported pipeline construction type. Compute, transfer, calibrated, and miscellaneous coverage is monolithic-only because the source avoids repeating work that does not depend on pipeline construction.

## Main Questions

- Does each requested timestamp become available and stay within the queue's valid-bit mask?
- Do comparable stage timestamps obey non-decreasing order?
- Do host reset, secondary command buffers, transfer queues, and copied query results preserve the query contract?
- Can calibrated device and host timestamps be related within the implementation's reported deviation?

## What Failure Means

### Failure Cause Mapping

| Behavior group | What a failure means |
|---|---|
| `basic_graphics_tests` | A graphics stage timestamp is unavailable, has an invalid value after masking, or violates the applicable ordering check. |
| `advanced_graphics_tests` | A timestamp for draw-indirect, tessellation, or geometry related stages violates the same query or ordering checks. |
| `basic_compute_tests` | A monolithic compute stage timestamp fails availability, valid-bit, or comparable-order checks. |
| `transfer_tests` | A timestamp around a transfer or host operation fails the query result, ordering, or transfer-queue path check. |
| `calibrated` | A supported device or host time-domain query is invalid, or calibration falls outside the source tolerance. |
| `misc_tests` | Query reset, command-buffer nesting, result copy, 32-bit versus 64-bit consistency, queue-family support, or sequential timestamp behavior fails. |

## Source Anchors

- [`TimestampTestParam::generateTestName`](../../../modules/vulkan/pipeline/vktPipelineTimestampTests.cpp#L300-L343) defines stage, render-pass, host-reset, transfer-queue, and availability suffixes.
- [`TimestampTest::checkSupport`](../../../modules/vulkan/pipeline/vktPipelineTimestampTests.cpp#L530-L551) checks queue timestamp support, host reset, and pipeline construction requirements.
- [`TimestampTestInstance::iterate`](../../../modules/vulkan/pipeline/vktPipelineTimestampTests.cpp#L649-L715) records, reads, masks, and rechecks query values.
- [`TimestampTestInstance::verifyTimestamp`](../../../modules/vulkan/pipeline/vktPipelineTimestampTests.cpp#L717-L741) implements availability and comparable-pair ordering checks.
- [`createTimestampTests`](../../../modules/vulkan/pipeline/vktPipelineTimestampTests.cpp#L4210-L4480) defines the registration matrix and monolithic-only boundaries.

## Vulkan Specification Anchors

- [`vkCmdWriteTimestamp`](../../../../vulkan-docs/src/chapters/queries.adoc#L2247-L2355) defines timestamp writes and their valid stage and query-pool usage.
- [`vkCmdWriteTimestamp2`](../../../../vulkan-docs/src/chapters/queries.adoc#L2120-L2243) gives the synchronization2 form of the timestamp command.
- [`timestampValidBits`](../../../../vulkan-docs/src/chapters/queries.adoc#L2105-L2110) defines the queue property used by the CTS mask.
- [`vkGetQueryPoolResults` availability rules](../../../../vulkan-docs/src/chapters/queries.adoc#L1160-L1265) defines result layout, availability, and unavailable-query behavior.
- [`vkResetQueryPool`](../../../../vulkan-docs/src/chapters/queries.adoc#L1280-L1348) defines command-side reset behavior.
