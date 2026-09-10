## Overview

**Core question:** How does the Vulkan SC command-pool memory-consumption query account for reservation, recorded command buffers, and reset?

`sc.command_pool_memory_reservation` checks the accounting exposed by Vulkan SC for a command pool. It asks two concrete questions:

1. Does `vkGetCommandPoolMemoryConsumption` return the reservation supplied through `VkCommandPoolMemoryReservationCreateInfo`?
2. After recording and resetting primary command buffers, does the pool allocation equal the sum of the allocations attributed to those buffers?

The implementation lives in [`vktCommandPoolMemoryReservationTests.cpp`](../../../modules/vulkan/sc/vktCommandPoolMemoryReservationTests.cpp#L24-L372). The SC root registers it from [`vktSafetyCriticalTests.cpp`](../../../modules/vulkan/sc/vktSafetyCriticalTests.cpp#L45-L64). The checked-in default mustpass contains the generated leaves under [`sc.txt`](../../../mustpass/main/vksc-default/sc.txt#L17-L106).

The test measures in the CTS child process. The parent process performs mock recording, so the source deliberately avoids treating parent-side memory-consumption queries as evidence ([`vktCommandPoolMemoryReservationTests.cpp#L123-L143`](../../../modules/vulkan/sc/vktCommandPoolMemoryReservationTests.cpp#L123-L143)).

## Background Knowledge

Each case creates a command pool with a `VkCommandPoolMemoryReservationCreateInfo` chained to `VkCommandPoolCreateInfo`. The reservation structure supplies:

- `commandPoolReservedSize`, the byte-sized reservation requested by the case;
- `commandPoolMaxCommandBuffers`, the count selected by the `cb_*` group.

The test allocates primary command buffers from that pool for the allocation cases. It creates one `VkEvent` for `size_small` or 32 events for `size_big`, then records `vkCmdSetEvent` into every command buffer. That command is workload for command-buffer accounting; it is not a shader dispatch ([`vktCommandPoolMemoryReservationTests.cpp#L146-L203`](../../../modules/vulkan/sc/vktCommandPoolMemoryReservationTests.cpp#L146-L203)).

`VkCommandPoolMemoryConsumption` carries three values used here:

- `commandPoolAllocated`: the pool-level allocation reported by the query;
- `commandPoolReservedSize`: the pool reservation reported by the query;
- `commandBufferAllocated`: the allocation attributed to the command buffer passed to the query.

The test queries once with a null command-buffer handle for the reservation case. For allocation cases it queries each allocated command buffer and sums the returned `commandBufferAllocated` fields. It takes `commandPoolAllocated` from the query results and compares the two quantities ([`vktCommandPoolMemoryReservationTests.cpp#L236-L270`](../../../modules/vulkan/sc/vktCommandPoolMemoryReservationTests.cpp#L236-L270)).

## Registration Hierarchy

```text
sc.command_pool_memory_reservation
└── memory_consumption
```

The `memory_consumption` test family expands into five command-buffer-count groups, two reserved-size groups, and two recording-order groups. The exact executable leaves appear in `## Parameter Dimensions and Observed Values`; the factory creates this hierarchy in [`vktCommandPoolMemoryReservationTests.cpp#L286-L372`](../../../modules/vulkan/sc/vktCommandPoolMemoryReservationTests.cpp#L286-L372).

The default list has 90 leaves: each of the five counts has two sizes, with nine leaves for single recording and eight for multiple recording. The names and paths in the list are the externally registered names; support checks can still prune a leaf at runtime.

## Parameter Dimensions and Observed Values

The registered dimensions are `cb_single`, `cb_few`, `cb_many`, `cb_min_limit`, and `cb_above_min_limit`; `size_small` and `size_big`; `single_recording` and `multiple_recording`; and allocation leaves `allocated_size_1`, `_2`, `_8`, and `_16`. The factory and their exact source effects are documented in the matrix below ([`vktCommandPoolMemoryReservationTests.cpp#L286-L372`](../../../modules/vulkan/sc/vktCommandPoolMemoryReservationTests.cpp#L286-L372)).

| Dimension | Values | Effect |
|---|---|---|
| Command-buffer count | `1`, `4`, `21`, `256`, `1024` | Requested maximum and allocation count. |
| Size class | `size_small`, `size_big` | 64/8192 default-size units for reservation; 1/32 event commands for allocation. |
| Recording order | `single_recording`, `multiple_recording` | Per-buffer sequence versus all-buffers begin/fill/end order. |
| Repetition | `1`, `2`, `8`, `16` | Registered leaf names backed by internal values 1, 2, 4, and 8. |

## Behavior Parameters

| Group | Registered values | Source effect |
|---|---|---|
| `cb_*` | `cb_single`, `cb_few`, `cb_many`, `cb_min_limit`, `cb_above_min_limit` | Requests 1, 4, 21, 256, or 1024 primary command buffers. The count is also passed as `commandPoolMaxCommandBuffers`. |
| `size_*` | `size_small`, `size_big` | In `reserved_size`, starts from 64 or 8192 command-default-size units. In allocation cases, records one or 32 event commands. |
| recording mode | `single_recording`, `multiple_recording` | Records each buffer completely before moving to the next, or begins all buffers, fills all buffers, and ends all buffers. |
| allocation leaf | `allocated_size_1`, `_2`, `_8`, `_16` | Passes internal iteration values 1, 2, 4, and 8. The loop performs twice that many passes because recording and reset alternate. |

The reservation calculation applies minimums. For `reserved_size`, the source takes the maximum of the size-class workload and `commandPoolMinSize`, then the maximum of that result and `commandBufferCount * commandBufferMinSize` ([`vktCommandPoolMemoryReservationTests.cpp#L76-L106`](../../../modules/vulkan/sc/vktCommandPoolMemoryReservationTests.cpp#L76-L106)). Allocation cases use the event count in the same pattern ([`vktCommandPoolMemoryReservationTests.cpp#L146-L173`](../../../modules/vulkan/sc/vktCommandPoolMemoryReservationTests.cpp#L146-L173)). Therefore `size_small` and `size_big` describe inputs to a calculation, not guaranteed final byte values.

The names `_1`, `_2`, `_8`, and `_16` are registered leaf names. Their internal values are 1, 2, 4, and 8. On each even pass the test records. On each odd pass it resets. Thus `allocated_size_8`, for example, performs four record/reset pairs, while the loop counter runs through eight passes ([`vktCommandPoolMemoryReservationTests.cpp#L205-L242`](../../../modules/vulkan/sc/vktCommandPoolMemoryReservationTests.cpp#L205-L242)).

### `reserved_size`

This leaf exercises the reservation report without allocating command buffers.

1. The case checks the requested count against `maxCommandPoolCommandBuffers`.
2. It computes the reservation from the selected size class, `commandPoolMinSize`, and `commandBufferMinSize`.
3. It fills `VkCommandPoolMemoryReservationCreateInfo` with the computed size and requested maximum count.
4. It chains that structure into `VkCommandPoolCreateInfo` and creates the pool for the universal queue family.
5. In the CTS subprocess, it calls `vkGetCommandPoolMemoryConsumption(device, pool, nullptr, &consumption)`.
6. It compares `consumption.commandPoolReservedSize` with the exact value supplied at pool creation.
7. A mismatch returns `tcu::TestStatus::fail("Failed")`; otherwise the function returns `pass("Pass")` ([`vktCommandPoolMemoryReservationTests.cpp#L76-L143`](../../../modules/vulkan/sc/vktCommandPoolMemoryReservationTests.cpp#L76-L143)).

This leaf does not assert `commandPoolAllocated` or `commandBufferAllocated`. A pass establishes a reservation-report round trip for this pool configuration. It does not establish an allocator layout or the allocation identity exercised by the other leaves.

### `allocated_size_*`

The allocation function follows the same setup for every count, size, recording mode, and iteration leaf.

### Setup

The function maps `size_small` to one event and `size_big` to 32 events. It computes the reservation using the event count, `commandPoolMinSize`, and the command-buffer minimum. It creates the pool with that reservation and maximum command-buffer count, then allocates the selected number of primary command buffers ([`vktCommandPoolMemoryReservationTests.cpp#L146-L190`](../../../modules/vulkan/sc/vktCommandPoolMemoryReservationTests.cpp#L146-L190)).

It creates the event objects before entering the iteration loop. The event handles remain available for every record pass. The test does not submit the buffers to a queue; the accounting observation concerns command-pool recording state.

### Record pass

On an even loop iteration, the case records event commands.

- `single_recording` begins one command buffer, records one or 32 `vkCmdSetEvent` commands into it, ends it, and repeats for the remaining buffers.
- `multiple_recording` begins every command buffer first, records all event commands into every buffer, and ends every buffer last.

Both modes create the same number of command buffers and event commands. They differ only in host call order, allowing the implementation's multiple-buffer recording path to receive separate coverage ([`vktCommandPoolMemoryReservationTests.cpp#L205-L235`](../../../modules/vulkan/sc/vktCommandPoolMemoryReservationTests.cpp#L205-L235)).

### Measurement after recording

In the subprocess, the case queries each command buffer. For each result it adds `commandBufferAllocated` to `cbAllocSum` and records `commandPoolAllocated` as `commandPoolAlloc`. It then requires:

```text
sum(commandBufferAllocated for every buffer) == commandPoolAllocated
```

A mismatch sets `isOK` to false. The test does not identify which command buffer or allocation category caused the difference; it reports the failed accounting relation.

### Reset pass

On the following odd iteration, the case calls `vkResetCommandPool` unless the device lacks `commandPoolResetCommandBuffer`. It then performs the same per-buffer query and equality check. Because this measurement follows a reset, it also requires `commandPoolAllocated == 0` ([`vktCommandPoolMemoryReservationTests.cpp#L236-L270`](../../../modules/vulkan/sc/vktCommandPoolMemoryReservationTests.cpp#L236-L270)).

The function returns `Pass` only if every performed measurement satisfies both applicable conditions. A reset leaf can therefore fail either because the pool total disagrees with the per-buffer sum or because the reported pool allocation remains nonzero after reset.

## Shader Analysis

No shader participates. The test records command-pool operations and checks reservation accounting; it creates no shader module, pipeline, draw, or dispatch.

## Runtime Execution and Result Checking

The child process creates the pool, allocates primary command buffers for allocation leaves, records event commands, queries memory consumption after recording, resets when supported, and queries again. The reservation leaf queries with a null command-buffer handle. The result checks and source locations are described above and are implemented in [`vktCommandPoolMemoryReservationTests.cpp`](../../../modules/vulkan/sc/vktCommandPoolMemoryReservationTests.cpp#L76-L270).

## Failure Meaning

### Failure Cause Mapping

The table below maps each failed observation to the checked API relation.

### Cause Analysis

#### Accounting mismatch

**Possible failure symptoms:** The pool total differs from the sum of per-buffer values, or the post-reset pool total is nonzero.

**Possible implementation causes:** Pool-level accounting, command-buffer attribution, or reset bookkeeping may disagree. The source does not isolate the implementation subsystem that produced the mismatch.


| Observation | What the source establishes | What it does not establish |
|---|---|---|
| `reserved_size` returns `Failed` | The queried `commandPoolReservedSize` differs from the computed value supplied at pool creation. | Which internal allocation or reporting stage produced the difference. |
| Allocation leaf fails after recording | Pool allocation differs from the sum of per-buffer allocations at a recorded state. | That one named command buffer or a particular allocator subsystem is responsible. |
| Allocation leaf fails after reset | The post-reset pool total is nonzero, or the pool total still differs from the per-buffer sum. | That physical memory remains allocated; the test observes the API's accounting value. |
| `NotSupportedError` | A required SC property or command-buffer limit rejected the case before its assertion. | An implementation failure in the accounting contract. |

The parent/subprocess split also bounds the result. The source comment says the parent performs mock recording and that the query belongs in the child. A pass therefore describes the child-side observations at the tested points; it does not validate command contents outside this setup.

## Case Pruning

### Requirement-based pruning

The device-property and command-buffer-count gates described in this section prune unsupported leaves before the accounting assertion.

### Design-based pruning

The factory omits unsupported enum values and keeps the reservation-only leaf under single recording because recording order is irrelevant to that assertion.


`checkSupport` runs before each allocation function:

- A leaf with internal `iterations > 1` requires `commandPoolResetCommandBuffer`.
- `multiple_recording` requires `commandPoolMultipleCommandBuffersRecording`.
- Every requested count must not exceed `maxCommandPoolCommandBuffers` ([`vktCommandPoolMemoryReservationTests.cpp#L273-L281`](../../../modules/vulkan/sc/vktCommandPoolMemoryReservationTests.cpp#L273-L281)).

The reservation function repeats the maximum-count check because it has no `checkSupport` callback. A rejected condition raises `NotSupportedError`. That outcome means the implementation did not advertise the operation needed by the case; it is not the same result as an accounting assertion returning `Failed`.

The factory does not register other reserved-size enum values. `CPS_UNUSED` is a sentinel, and passing it to the test functions raises `InternalError` rather than creating a case ([`vktCommandPoolMemoryReservationTests.cpp#L39-L60`](../../../modules/vulkan/sc/vktCommandPoolMemoryReservationTests.cpp#L39-L60)). The factory also keeps `reserved_size` under single recording because recording order has no role in that reservation-only assertion.

## Key Takeaways

The matrix varies four independent inputs: requested command-buffer count, reservation/workload size, recording order, and repetition of recording followed by reset. The reservation-only leaf checks the declared reservation. The allocation leaves check attribution and reset accounting. Together they cover the registered paths in `sc.txt`, while support properties determine which paths are runnable on a particular device.

The test does not submit command buffers, wait for event state, inspect event payloads, or compare rendered or computed data. Those omissions follow from the purpose of this family: it measures command-pool memory reporting, not execution semantics.

## Source Reference Appendix

| Source | Lines | Use |
|---|---:|---|
| [`vktSafetyCriticalTests.cpp`](../../../modules/vulkan/sc/vktSafetyCriticalTests.cpp#L45-L64) | 45-64 | Registers the command-pool reservation group below the SC root. |
| [`vktCommandPoolMemoryReservationTests.cpp`](../../../modules/vulkan/sc/vktCommandPoolMemoryReservationTests.cpp#L76-L143) | 76-143 | Computes and verifies the declared reservation. |
| [`vktCommandPoolMemoryReservationTests.cpp`](../../../modules/vulkan/sc/vktCommandPoolMemoryReservationTests.cpp#L146-L203) | 146-203 | Creates allocation workloads and records event commands. |
| [`vktCommandPoolMemoryReservationTests.cpp`](../../../modules/vulkan/sc/vktCommandPoolMemoryReservationTests.cpp#L205-L270) | 205-270 | Alternates recording/reset and checks memory-consumption fields. |
| [`vktCommandPoolMemoryReservationTests.cpp`](../../../modules/vulkan/sc/vktCommandPoolMemoryReservationTests.cpp#L273-L281) | 273-281 | Applies support and device-limit gates. |
| [`vktCommandPoolMemoryReservationTests.cpp`](../../../modules/vulkan/sc/vktCommandPoolMemoryReservationTests.cpp#L286-L372) | 286-372 | Defines the registered hierarchy and parameter names. |
| [`sc.txt`](../../../mustpass/main/vksc-default/sc.txt#L17-L106) | 17-106 | Lists the default generated test paths. |
