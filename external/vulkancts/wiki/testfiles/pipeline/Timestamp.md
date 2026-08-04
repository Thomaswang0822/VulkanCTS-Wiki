## Overview

**Core question:** Do Vulkan timestamp queries return available, valid-bit-safe, and correctly ordered values for the pipeline, transfer, calibrated-time, and query-lifecycle paths exercised by the CTS?

- [`vktPipelineTimestampTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineTimestampTests.cpp#L1) implements the `timestamp` test family in the `pipeline` test category.
- The family writes timestamp queries at selected stages, submits work, retrieves query-pool results, and checks masked values plus limited ordering relations. It also exercises availability-result layouts, host reset, transfer-only queues, calibrated timestamps, copied results, and queue-family coverage. The common availability check has a source-level indexing limitation described below.
- The graphics stage groups run for each supported pipeline construction type. The source registers compute, transfer, calibrated, and miscellaneous groups only for `PIPELINE_CONSTRUCTION_TYPE_MONOLITHIC`.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

A `VK_QUERY_TYPE_TIMESTAMP` query pool receives a device timestamp when `vkCmdWriteTimestamp` executes at its requested pipeline stage. The queue-family `timestampValidBits` value determines which low-order timestamp bits are meaningful, so the CTS masks higher bits before comparing retrieved values. It separately rejects an out-of-range nonzero `timestampValidBits` value and, in calibrated tests, checks that invalid device-timestamp bits are zero.

`vkGetQueryPoolResults` can append an availability value for each query through `VK_QUERY_RESULT_WITH_AVAILABILITY_BIT`. A zero availability value means the result was unavailable when Vulkan wrote the result data. Ordinary command-buffer reset uses `vkCmdResetQueryPool`; `VK_EXT_host_query_reset` adds `vkResetQueryPool` for host-side reset.

A timestamp does not define a total order for arbitrary stage flags. The source compares pairs only when the later stage is `VK_PIPELINE_STAGE_TOP_OF_PIPE_BIT`, the earlier stage is `VK_PIPELINE_STAGE_BOTTOM_OF_PIPE_BIT`, or both stages are the same. Calibrated timestamp cases query device and host time domains supported by `VK_KHR_calibrated_timestamps` or `VK_EXT_calibrated_timestamps` and use the returned deviation to bound their comparison.

## Registration Hierarchy

```text
pipeline.monolithic.timestamp
├── basic_graphics_tests
├── advanced_graphics_tests
├── basic_compute_tests
├── transfer_tests
├── calibrated
└── misc_tests
```

The concrete monolithic root shows every direct intermediate node. The source registers `basic_graphics_tests` and `advanced_graphics_tests` under each supported construction-type root, while it adds the other four groups only in the monolithic branch. The default mustpass split contains 262 `pipeline.monolithic.timestamp` leaves. Each of `fast-linked-library.txt`, `pipeline-library.txt`, `shader-object-linked-binary.txt`, `shader-object-linked-spirv.txt`, `shader-object-unlinked-binary.txt`, and `shader-object-unlinked-spirv/shader-object-unlinked-spirv.txt` contains 112 timestamp leaves, all in the graphics groups.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Direct intermediate node | `basic_graphics_tests`, `advanced_graphics_tests`, `basic_compute_tests`, `transfer_tests`, `calibrated`, `misc_tests` | Selects the workload and result checker. | [registration](../../../modules/vulkan/pipeline/vktPipelineTimestampTests.cpp#L4210-L4480) |
| Pipeline construction type | monolithic and supported non-monolithic types | Changes the registered root. Only graphics groups repeat outside monolithic construction. | [registration guards](../../../modules/vulkan/pipeline/vktPipelineTimestampTests.cpp#L4306-L4399) |
| Timestamp stages | basic graphics, advanced graphics, compute, transfer, host, `ALL_GRAPHICS`, `ALL_COMMANDS` | Determines where the command buffer writes one or more timestamp queries. | [stage matrices](../../../modules/vulkan/pipeline/vktPipelineTimestampTests.cpp#L4222-L4231) and [monolithic matrices](../../../modules/vulkan/pipeline/vktPipelineTimestampTests.cpp#L4312-L4340) |
| Render-pass placement | `in_render_pass`, `out_of_render_pass` | Places graphics timestamp writes inside or outside the render pass. | [graphics registration](../../../modules/vulkan/pipeline/vktPipelineTimestampTests.cpp#L4232-L4269) |
| Reset method | command-buffer reset, `_host_query_reset` | Chooses `vkCmdResetQueryPool` or a host-side reset followed by unavailable-result checks. | [iteration path](../../../modules/vulkan/pipeline/vktPipelineTimestampTests.cpp#L635-L712) |
| Result layout | 64-bit result, `_with_availability_bit` | Requests `WAIT_BIT` and optionally appends availability values. | [result flags](../../../modules/vulkan/pipeline/vktPipelineTimestampTests.cpp#L4213-L4216) |
| Transfer method and queue | 12 `TransferMethod` values; default or `_transfer_queue` | Exercises transfer and host stages around copy, blit, clear, fill, resolve, and query-result-copy operations. | [`TransferMethod`](../../../modules/vulkan/pipeline/vktPipelineTimestampTests.cpp#L134-L149) and [transfer registration](../../../modules/vulkan/pipeline/vktPipelineTimestampTests.cpp#L4332-L4379) |
| Command-buffer level | primary, secondary | Exercises timestamp/query-result work split across command buffers. | [misc registration](../../../modules/vulkan/pipeline/vktPipelineTimestampTests.cpp#L4418-L4459) |

## Behavior Parameters

The primary behavioral axis is the direct intermediate node. Each value changes the submitted workload or the host-side query contract under test.

### `basic_graphics_tests`: common graphics-stage timestamps

These cases write timestamps from `TOP_OF_PIPE` to vertex input, vertex shader, fragment shader, early or late fragment tests, color attachment output, `ALL_GRAPHICS`, or `ALL_COMMANDS`. They also include two three-stage sequences. Each stage matrix runs inside and outside a render pass, with command-buffer reset and with host reset, and with or without availability data.

### `advanced_graphics_tests`: draw-indirect and optional graphics-stage timestamps

These cases cover draw indirect, tessellation control, tessellation evaluation, and geometry shader timestamps. They use the same placement, reset, and availability combinations as the basic graphics group. Feature support determines whether the relevant pipeline stages can run.

### `basic_compute_tests`: monolithic compute timestamps

The monolithic path writes timestamps from `TOP_OF_PIPE` to `COMPUTE_SHADER` or `ALL_COMMANDS`. Each stage pair runs with command-buffer reset and host query reset. The source does not duplicate compute coverage for graphics pipeline library construction.

### `transfer_tests`: transfer and host operation timestamps

These cases select `TRANSFER` or `HOST` as the target stage, then pair it with each `TransferMethod`. The source runs default-queue variants and host-reset variants; transfer-only queue variants omit blit, clear, resolve, and query-result-copy methods that such a queue cannot execute.

### `calibrated`: device and host time-domain checks

The three leaves are `dev_domain_test`, `host_domain_test`, and `calibration_test`. They validate device-domain values, supported host-domain values, and a device-host calibration sample.

### `misc_tests`: query lifecycle and consistency checks

This group covers timestamp-only command buffers, primary and secondary command-buffer paths, query reset before copy, fill before query-result copy, 32-bit versus 64-bit consistency, graphics/compute queue-family support, and sequential writes.

## Shader Analysis

The shaders only create graphics, compute, and transfer workloads at the requested stage. The host validates query results rather than shader output, so this family has no shader-specific result path or SPIR-V artifact to document.

## Runtime Execution and Result Checking

1. The test selects a queue family. Timestamp cases skip a family with `timestampValidBits == 0` and fail an invalid nonzero value outside the 36-to-64-bit range; transfer-only cases create a device for a queue with transfer capability and without graphics or compute capability. Host-reset cases require `VK_EXT_host_query_reset` and its feature.
2. The common timestamp instance creates a `VK_QUERY_TYPE_TIMESTAMP` query pool with eight entries, a transient command pool, and a primary command buffer. It derives a mask from the selected queue family's `timestampValidBits`.
3. The instance records `vkCmdResetQueryPool` unless the case requests host reset. It writes one timestamp per selected stage with `vkCmdWriteTimestamp`, builds the family-specific graphics, compute, or transfer work where needed, submits the command buffer, and waits for completion.
4. The host calls `vkGetQueryPoolResults` with `VK_QUERY_RESULT_64_BIT | VK_QUERY_RESULT_WAIT_BIT`, optionally adding `VK_QUERY_RESULT_WITH_AVAILABILITY_BIT`. It masks each returned timestamp before checking it.
5. Host-reset cases save the completed values, call `vkResetQueryPool`, then retrieve results with availability data. The source expects `VK_NOT_READY`, unchanged result slots, and availability values of zero after the reset.
6. For comparable pairs, `verifyTimestamp` fails if the later timestamp is lower than the earlier timestamp. Availability-enabled common cases intend to reject zero availability values, but the function advances its loop indices by the interleaved result stride while also indexing the stage vector with those indices. With the registered two- and three-stage vectors, this leaves some availability values and pairs unchecked and can associate a result value with the wrong stage when deciding whether to compare it. Specialized classes add independent checks for calibration, copied results, bit-width consistency, queue-family coverage, and sequential writes.

## Failure Meaning

### Failure Cause Mapping

| Behavior group | What a failure means |
|---|---|
| `basic_graphics_tests` | A graphics timestamp path violates a check that the common validator actually reaches. Availability-enabled leaves currently have incomplete availability and pairwise-order coverage because of the validator's indexing limitation. |
| `advanced_graphics_tests` | A draw-indirect, tessellation, or geometry timestamp path violates a check that the common validator actually reaches; the same availability-indexing limitation applies. |
| `basic_compute_tests` | A monolithic compute timestamp path violates a reached host-reset or common-validator check; the same availability-indexing limitation applies. |
| `transfer_tests` | A transfer or host-operation timestamp path violates a reached query-result, host-reset, ordering, or transfer-queue check; the same availability-indexing limitation applies. |
| `calibrated` | A supported device or host time-domain query is invalid, or calibration falls outside the source tolerance. |
| `misc_tests` | Query reset, command-buffer nesting, result copy, 32-bit versus 64-bit consistency, queue-family support, or sequential timestamp behavior fails. |

### Cause Analysis

#### A completed query remains unavailable or returns unusable bits

**Possible failure symptoms:** A common timestamp case reports "Timestamp query not available", or a calibrated checker rejects a value whose invalid bits are nonzero. Because `verifyTimestamp` advances stage-vector indices using the interleaved result stride, the registered availability-enabled common cases do not check every returned availability slot.

**Possible implementation causes:** For a reached availability failure, the driver may publish query availability incorrectly or write result data with the wrong layout. A calibrated invalid-bit failure can indicate inconsistent timestamp capability or timestamp encoding. A pass does not establish full common-case availability coverage until the CTS indexing limitation is fixed.

#### Comparable timestamps run backward

**Possible failure symptoms:** The test reports "Latter stage timestamp is smaller than the former stage timestamp." This applies only to pairs that the source classifies as comparable.

**Possible implementation causes:** The implementation may associate a timestamp write with the wrong command or stage boundary, order query writes incorrectly, or serialize result data incorrectly. The source deliberately avoids treating every stage pair as a total order, so a failure identifies an ordering error only for its limited comparison rule.

The same source-level indexing limitation means availability-enabled common leaves may skip otherwise comparable pairs. A pass in those leaves is therefore weaker than the corresponding intended ordering coverage.

#### Host reset does not restore the unavailable state

**Possible failure symptoms:** A host-reset variant reports incorrect reset results, changed stored values, or a nonzero availability status after reset.

**Possible implementation causes:** The host-reset implementation may leave stale availability data, modify data slots that Vulkan leaves untouched for unavailable queries, or return a completion result instead of `VK_NOT_READY`. The CTS saves its first result, resets the pool with `vkResetQueryPool`, and reads the availability layout again.

#### Calibrated time domains fail their bounded comparison

**Possible failure symptoms:** `dev_domain_test`, `host_domain_test`, or `calibration_test` rejects a timestamp mask, deviation, or interval relationship.

**Possible implementation causes:** The implementation may report unsupported time domains, convert device ticks with the wrong timestamp period, calculate maximum deviation incorrectly, or sample the host and device clocks outside the promised tolerance. Source-level driver investigation is needed to isolate the platform clock conversion.

#### Transfer or miscellaneous query lifecycle checks fail

**Possible failure symptoms:** A transfer-queue path, copied query result, 32-bit versus 64-bit result comparison, secondary command-buffer path, queue-family coverage check, or sequential timestamp case fails.

**Possible implementation causes:** The implementation may mishandle query state across command buffers, apply a transfer-only queue capability incorrectly, copy a result with an incorrect stride or width, or expose different timestamp behavior across eligible graphics and compute queue families. These cases combine several operations, so the final result may not isolate one internal driver path without logs or source-level tracing.

## Case Pruning

### Requirement-based pruning

- Timestamp cases skip a queue family whose `timestampValidBits` is zero. A nonzero value below 36 or above 64 is reported as invalid by the CTS instead of being treated as an unsupported queue.
- `_host_query_reset` variants require `VK_EXT_host_query_reset` and `hostQueryReset`.
- Calibrated tests require `VK_KHR_calibrated_timestamps` or `VK_EXT_calibrated_timestamps`. The device-domain case needs a suitable device domain, the host-domain case needs a suitable host domain, and the calibration case needs both.
- Optional graphics-stage variants require the relevant graphics pipeline features; all cases check their pipeline construction requirements.
- `check_timestamp_compute_and_graphics` requires the `timestampComputeAndGraphics` device limit.

### Design-based pruning

- The source registers only the graphics groups for non-monolithic construction types. Compute, transfer, calibrated, and miscellaneous tests do not vary with graphics pipeline construction.
- Transfer-only queue cases omit blit, clear color, clear depth-stencil, resolve, and query-result-copy methods because the selected queue cannot support those commands.
- The comparison loop checks only explicitly comparable stage pairs rather than asserting a global order across all pipeline stages.
- The calibrated group has three focused leaves instead of multiplying every timestamp stage by every host domain.

## Key Takeaways

- The CTS checks query-pool semantics and constrained timestamp ordering, not performance or shader output.
- `timestampValidBits` controls the mask applied before host validation.
- Availability, reset behavior, result-copy layout, and queue-family support matter alongside the timestamp value itself, but the common availability-enabled validator currently has incomplete coverage because it mixes stage indices with interleaved result indices.
- Graphics coverage repeats across construction types; the non-graphics groups remain monolithic-only by design.
- A backward comparable pair or an unavailable completed query is a hard result error. Calibration failures need implementation-specific clock-path investigation.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Names and dimensions | [`TimestampTestParam::generateTestName`](../../../modules/vulkan/pipeline/vktPipelineTimestampTests.cpp#L300-L343) | Defines stage, render-pass, host-reset, transfer-queue, and availability suffixes |
| Capability checks | [`TimestampTest::checkSupport`](../../../modules/vulkan/pipeline/vktPipelineTimestampTests.cpp#L530-L551) | Checks timestamp support, host query reset, and construction requirements |
| Common command and result flow | [`TimestampTestInstance::configCommandBuffer` and `iterate`](../../../modules/vulkan/pipeline/vktPipelineTimestampTests.cpp#L631-L715) | Resets, writes, submits, retrieves, masks, and host-resets timestamp queries |
| Common ordering check | [`TimestampTestInstance::verifyTimestamp`](../../../modules/vulkan/pipeline/vktPipelineTimestampTests.cpp#L717-L741) | Defines availability and comparable-pair ordering failures |
| Transfer inventory | [`TransferMethod`](../../../modules/vulkan/pipeline/vktPipelineTimestampTests.cpp#L134-L183) | Defines the transfer operations used by the transfer group |
| Calibrated timestamp framework | [`CalibratedTimestampTestInstance`](../../../modules/vulkan/pipeline/vktPipelineTimestampTests.cpp#L948-L1008) | Holds calibrated values, deviation limits, time domains, and timestamp period |
| Registration | [`createTimestampTests`](../../../modules/vulkan/pipeline/vktPipelineTimestampTests.cpp#L4210-L4480) | Defines the direct groups, stage matrices, and monolithic-only branches |
| Timestamp command | [`vkCmdWriteTimestamp`](../../../../vulkan-docs/src/chapters/queries.adoc#L2247-L2355) | Defines legacy timestamp writes and their valid use |
| Queue valid-bit property | [`timestampValidBits`](../../../../vulkan-docs/src/chapters/queries.adoc#L2105-L2110) | Defines the valid timestamp bits used to mask CTS results |
| Query results and availability | [`vkGetQueryPoolResults`](../../../../vulkan-docs/src/chapters/queries.adoc#L1160-L1265) | Defines result layout, availability, and unavailable-query behavior |
| Command and host resets | [`vkCmdResetQueryPool` and `vkResetQueryPool`](../../../../vulkan-docs/src/chapters/queries.adoc#L1280-L1348) | Defines query-pool reset behavior used by normal and host-reset variants |
