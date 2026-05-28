# vktPipelineTimestampTests.cpp

## Overview

[`vktPipelineTimestampTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineTimestampTests.cpp#L1) implements the [`timestamp`](../../../modules/vulkan/pipeline/vktPipelineTimestampTests.cpp#L4213) topic group. It verifies timestamp query behavior across pipeline stages, transfer operations, and calibrated timestamps, ensuring that `vkCmdWriteTimestamp` produces valid, monotonically non-decreasing values for graphics, compute, and transfer stages.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineTimestampTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineTimestampTests.cpp#L1)
- Header: [`vktPipelineTimestampTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineTimestampTests.hpp#L1)

## Registration Hierarchy

```text
pipeline.monolithic.timestamp
├── basic_graphics_tests
├── advanced_graphics_tests
├── basic_compute_tests (monolithic only)
├── transfer_tests (monolithic only)
├── calibrated (monolithic only)
└── misc_tests (monolithic only)
```

Source: [`createTimestampTests()`](../../../modules/vulkan/pipeline/vktPipelineTimestampTests.cpp#L4211) returns the `timestamp` group, attached under each variant root by [`createChildren()`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L146). Variant coverage: all variants.

## Test Families

### basic_graphics_tests — Basic graphics pipeline stage timestamps

Verifies timestamp queries for basic graphics pipeline stages (vertex input, vertex shader, fragment shader, early/late fragment tests, color attachment output). Contains leaf test cases named `{stage_pair}_{in/out_of_render_pass}{_host_query_reset}{_with_availability_bit}` for each combination of stage pair, render-pass context, host-query-reset mode, and availability-bit flag.

### advanced_graphics_tests — Advanced graphics pipeline stage timestamps

Verifies timestamp queries for advanced graphics pipeline stages (draw indirect, tessellation control/evaluation, geometry shader). Contains leaf test cases named `{stage_pair}_{in/out_of_render_pass}{_host_query_reset}{_with_availability_bit}`.

### basic_compute_tests — Compute pipeline stage timestamps (monolithic only)

Verifies timestamp queries for compute pipeline stages (compute shader, all commands). Contains leaf test cases named `{stage_pair}{_host_query_reset}{_with_availability_bit}`. Only registered for `PIPELINE_CONSTRUCTION_TYPE_MONOLITHIC`.

### transfer_tests — Transfer operation timestamps (monolithic only)

Verifies timestamp queries for transfer operations across all transfer methods and queue types. Contains leaf test cases named `{stage}_with_{transfer_method}{_host_query_reset}{_transfer_queue}{_with_availability_bit}`. Only registered for `PIPELINE_CONSTRUCTION_TYPE_MONOLITHIC`. Transfer tests skip methods not supported on transfer-only queues (blit, clear, resolve, copy query pool results).

### calibrated — Calibrated timestamp queries (monolithic only)

Verifies calibrated timestamp queries across device and host time domains. Contains three leaf test cases: `dev_domain_test`, `host_domain_test`, and `calibration_test`. Only registered for `PIPELINE_CONSTRUCTION_TYPE_MONOLITHIC`.

### misc_tests — Miscellaneous timestamp tests (monolithic only)

Contains standalone and edge-case timestamp tests. Leaf test cases include `timestamp_only{_with_availability_bit}`, `two_cmd_buffers_primary{_with_availability_bit}`, `two_cmd_buffers_secondary{_with_availability_bit}`, `timestamp_only_host_query_reset{_with_availability_bit}`, `two_cmd_buffers_primary_host_query_reset{_with_availability_bit}`, `two_cmd_buffers_secondary_host_query_reset{_with_availability_bit}`, `two_cmd_buffers_secondary_transfer_queue{_with_availability_bit}`, `reset_query_before_copy`, `fill_buffer_before_copy`, `consistent_results`, `check_timestamp_compute_and_graphics` (monolithic only), and `sequential_timestamps` (monolithic only). Only registered for `PIPELINE_CONSTRUCTION_TYPE_MONOLITHIC`.

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| PipelineConstructionType | Parameter | All variant types |
| Pipeline stage flags | `VkPipelineStageFlagBits` | Combinations of graphics, compute, transfer, and host stages |
| In-render-pass vs out-of-render-pass | Boolean | Whether timestamp is written inside or outside a render pass |
| Host query reset | Boolean | Whether `VK_EXT_host_query_reset` is used instead of `vkCmdResetQueryPool` |
| Query result flags | `VkQueryResultFlags` | `64_BIT \| WAIT_BIT`, with/without `WITH_AVAILABILITY_BIT` |
| Transfer method | [`TransferMethod`](../../../modules/vulkan/pipeline/vktPipelineTimestampTests.cpp#L134) enum | 12 methods: copy buffer/image, blit, buffer-to-image, image-to-buffer, update/fill buffer, clear color/depth-stencil image, resolve image, copy query pool results |
| Transfer-only queue | Boolean | Whether to use a dedicated transfer queue |
| Command buffer level | `VkCommandBufferLevel` | Primary or secondary |

## Support / Feature Requirements

| Requirement | Context |
|---|---|
| `VK_EXT_host_query_reset` | Required for host query reset test variants |
| `VK_KHR_calibrated_timestamps` / `VK_EXT_calibrated_timestamps` | Required for calibrated timestamp tests |
| `timestampComputeAndGraphics` device limit | Required for `check_timestamp_compute_and_graphics` test |
| `timestampValidBits` queue property | Checked for all timestamp tests via `checkTimestampValidBitsSupport()` |

## Verification Methods

- **Timestamp validity**: Verify that queried timestamp values are non-zero and within `timestampValidBits` mask
- **Monotonic ordering**: Verify that timestamps for later pipeline stages are >= earlier stages
- **Availability bit**: Verify that `VK_QUERY_RESULT_WITH_AVAILABILITY_BIT` reports correct availability status
- **Host query reset**: Verify that host-side query reset produces the same results as command-buffer reset
- **Calibration**: Verify that calibrated timestamps from device and host domains are consistent
- **Consistent bit width**: Verify that 32-bit and 64-bit query results agree within the valid bits range
- **Cross-queue validation**: Verify timestamp support across all graphics/compute queue families

## Notes

- The `basic_compute_tests`, `transfer_tests`, `calibrated`, and `misc_tests` subgroups are only added for `PIPELINE_CONSTRUCTION_TYPE_MONOLITHIC` (checked at [`vktPipelineTimestampTests.cpp#L4308`](../../../modules/vulkan/pipeline/vktPipelineTimestampTests.cpp#L4308), [`vktPipelineTimestampTests.cpp#L4334`](../../../modules/vulkan/pipeline/vktPipelineTimestampTests.cpp#L4334), [`vktPipelineTimestampTests.cpp#L4383`](../../../modules/vulkan/pipeline/vktPipelineTimestampTests.cpp#L4383), [`vktPipelineTimestampTests.cpp#L4399`](../../../modules/vulkan/pipeline/vktPipelineTimestampTests.cpp#L4399))
- The `check_timestamp_compute_and_graphics` and `sequential_timestamps` tests have an additional monolithic-only guard within the already-monolithic-restricted `misc_tests` block
- Transfer tests skip methods not supported on transfer-only queues (blit, clear, resolve, copy query pool results)
- The `timestamp` topic group is available for both VK and VKSC (no `CTS_USES_VULKANSC` exclusion guard at registration)
