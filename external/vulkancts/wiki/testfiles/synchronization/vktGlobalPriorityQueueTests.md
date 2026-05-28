# vktGlobalPriorityQueueTests

## Overview

Tests for global priority queues using the `VK_EXT_global_priority` and `VK_EXT_global_priority_query` extensions. These tests verify that queue family ownership transitions work correctly between queues with different global priority levels, and that task preemption behaves as expected when higher-priority work is submitted alongside lower-priority work.

This is a **LEGACY-only** test file (non-SC). It is registered under the `synchronization` (LEGACY) category only.

## Role of File

Provides the `global_priority_transition` test group, which contains two major test categories:
1. **Queue transition tests**: Verify data integrity when transitioning resources between queues with global priorities, using graphics, compute, and transfer queue types with semaphore or no-sync synchronization.
2. **Preemption tests**: Attempt to trigger task preemption by submitting a large workload to a lower-priority queue and a small workload to a higher-priority queue, verifying both complete successfully.

## Source Code

- [vktGlobalPriorityQueueTests.cpp](../../../modules/vulkan/synchronization/vktGlobalPriorityQueueTests.cpp)
- Utility code: [vktGlobalPriorityQueueUtils.cpp](../../../modules/vulkan/synchronization/vktGlobalPriorityQueueUtils.cpp) / [vktGlobalPriorityQueueUtils.hpp](../../../modules/vulkan/synchronization/vktGlobalPriorityQueueUtils.hpp) (no Level-3 doc for utils)

## Registration Hierarchy

```text
synchronization.global_priority_transition
├── low
├── medium
├── high
├── realtime
└── preemption
```

Registered in the LEGACY path via [`createGlobalPriorityQueueTests()`](../../../modules/vulkan/synchronization/vktGlobalPriorityQueueTests.cpp#L2281), added to the `synchronization` group in [`vktSynchronizationTests.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L142).

## Test Families

### low — Queue transition at LOW priority

Queue transition tests where both source and destination queues use `VK_QUEUE_GLOBAL_PRIORITY_LOW_KHR`. Each priority group expands into sync-type subgroups (`no_sync`, `semaphore`), then modifier subgroups (`no_modifiers`, `sparse`, `protected`), then leaf transition tests (e.g., `from_graphics_to_compute`).

Implemented by `GPQCase`.

### medium — Queue transition at MEDIUM priority

Queue transition tests where both source and destination queues use `VK_QUEUE_GLOBAL_PRIORITY_MEDIUM_KHR`. Internal structure is identical to `low`.

Implemented by `GPQCase`.

### high — Queue transition at HIGH priority

Queue transition tests where both source and destination queues use `VK_QUEUE_GLOBAL_PRIORITY_HIGH_KHR`. Internal structure is identical to `low`.

Implemented by `GPQCase`.

### realtime — Queue transition at REALTIME priority

Queue transition tests where both source and destination queues use `VK_QUEUE_GLOBAL_PRIORITY_REALTIME_KHR`. Internal structure is identical to `low`.

Implemented by `GPQCase`.

#### Shared queue-transition hierarchy

All four priority groups (`low`, `medium`, `high`, `realtime`) share the same internal expansion:

```
<priority>
├── no_sync
│   ├── no_modifiers
│   ├── sparse
│   └── protected
└── semaphore
    ├── no_modifiers
    ├── sparse
    └── protected
```

Each modifier subgroup contains leaf tests named `from_<srcQueue>_to_<dstQueue>`:

| Transition name | Source queue | Destination queue |
|---|---|---|
| `from_graphics_to_compute` | GRAPHICS | COMPUTE |
| `from_compute_to_graphics` | COMPUTE | GRAPHICS |
| `from_compute_to_transfer` | COMPUTE | TRANSFER |
| `from_transfer_to_compute` | TRANSFER | COMPUTE |

Only graphics<->compute and compute<->transfer transitions are generated; graphics<->transfer is explicitly skipped.

Modifier details:
- **no_modifiers**: No additional queue flags.
- **sparse**: Adds `VK_QUEUE_SPARSE_BINDING_BIT` (requires `sparseBinding` + `sparseResidencyImage2D` features).
- **protected**: Adds `VK_QUEUE_PROTECTED_BIT` (requires `protectedMemory` feature).

### preemption — Preemption tests

Preemption tests that submit a large workload to a lower-priority queue and a small workload to a higher-priority queue, verifying both produce correct results. Implemented by `PreemptionCase`.

Leaf test names follow the pattern `<queueTypeA>_<priorityA>_to_<queueTypeB>_<priorityB>[_double_preemption]`.

Queue type names: `graphics`, `compute`, `exclusive-compute`, `transfer`, `exclusive-transfer`.

Priority names: `low`, `medium`, `high`, `realtime`.

Only combinations where `priorityA < priorityB` are generated. The optional `_double_preemption` suffix indicates the small workload is submitted twice.

## Parameter Dimensions

### Queue Transition Tests

| Dimension | Values | Notes |
|-----------|--------|-------|
| Priority | LOW, MEDIUM, HIGH, REALTIME | Same priority used for both from and to queues |
| Sync Type | None, Semaphore | Controls whether a semaphore synchronizes producer and consumer |
| Modifier | no_modifiers, sparse, protected | Adds queue flags for sparse binding or protected memory |
| Transition From | GRAPHICS, COMPUTE, TRANSFER | Source queue type |
| Transition To | COMPUTE, GRAPHICS, TRANSFER | Destination queue type (only 4 combinations tested) |
| Image dimensions | 34x25 or 25x34 (alternating) | Swapped per test case |

### Preemption Tests

| Dimension | Values | Notes |
|-----------|--------|-------|
| Queue A type | GRAPHICS, COMPUTE, COMPUTE_EXCLUSIVE, TRANSFER, TRANSFER_EXCLUSIVE | Lower-priority queue |
| Queue B type | GRAPHICS, COMPUTE, COMPUTE_EXCLUSIVE, TRANSFER, TRANSFER_EXCLUSIVE | Higher-priority queue |
| Priority A | LOW, MEDIUM, HIGH, REALTIME | Must be strictly less than Priority B |
| Priority B | LOW, MEDIUM, HIGH, REALTIME | Must be strictly greater than Priority A |
| Double preemption | false, true | Whether to submit the small workload twice |

## Support / Feature Requirements

| Requirement | Type | Notes |
|-------------|------|-------|
| VK_EXT_global_priority | Device Extension | Required for all tests |
| VK_EXT_global_priority_query | Device Extension | Required for queue transition tests |
| VK_KHR_get_physical_device_properties2 | Instance Extension | Required for all tests |
| VK_KHR_global_priority | Device Extension | Required for preemption tests |
| Queue family with required priority | Queue Property | Must find queue family supporting the specified global priority |
| Separate queue families | Queue Property | Queue transition tests require two different queue family indices |
| sparseBinding + sparseResidencyImage2D | Device Features | Required when modifier is `sparse` |
| protectedMemory | Device Feature | Required when modifier is `protected` |
| Format support | Format Properties | Must find a suitable R-channel format (R32_SINT, R32_UINT, R8_SINT, or R8_UINT) |

## Verification Methods

1. **Queue transition (non-protected)**: The consumer compute shader reads a pixel from the image produced by the graphics/compute/transfer pipeline and writes 1 to an output buffer if the value matches the expected test value (113), or 0 otherwise. The test checks `resultBufferAccess.getPixelUint(0, 0).x() == 1`.

2. **Queue transition (protected)**: For protected memory, the consumer shader checks the value and enters an infinite loop if it does not match. The test uses a 10-second fence timeout to detect failure. If the shader completes, the test passes.

3. **Preemption - graphics workload**: Verifies a gradient image using `tcu::floatThresholdCompare` with threshold `Vec4(0.0f, 0.005f, 0.005f, 0.0f)`.

4. **Preemption - compute workload**: Verifies an output buffer contains sequential increasing values starting from 0 (or 1000 for transfer) using `verifyIncreasingValues()`.

5. **Preemption - transfer workload**: Verifies output buffer contains sequential values starting from offset 1000 using `verifyIncreasingValues()`.

## Test Principles

1. **Global priority queue creation**: Tests create custom devices with `VkDeviceQueueGlobalPriorityCreateInfoKHR` to request specific global priorities for queue families.

2. **Queue ownership transfer**: Queue transition tests exercise the full ownership transfer pattern: producer writes on one queue, ownership is released via pipeline barrier, consumer acquires on another queue and reads.

3. **Semaphore vs no-sync**: The sync type dimension tests whether explicit semaphore synchronization is needed or if the global priority mechanism alone provides sufficient ordering.

4. **Preemption validation**: Preemption tests submit a large (512x512) workload to a lower-priority queue and a small (8x8) workload to a higher-priority queue, verifying that the higher-priority work can preempt the lower-priority work and complete correctly.

5. **VK_ERROR_NOT_PERMITTED_KHR handling**: If device creation with the requested priority returns `VK_ERROR_NOT_PERMITTED_KHR`, the test reports a quality warning rather than failing, as this is a valid implementation behavior.

## Notes/Uncertainties

- **LEGACY-only**: The `global_priority_transition` group is only added to the LEGACY `synchronization` tree, not to `synchronization2`.
- **Non-SC only**: The test is excluded from Vulkan SC builds (`#ifndef CTS_USES_VULKANSC`).
- **Utility code dependency**: Uses `SpecialDevice`, `findQueueFamilyIndex()`, and other utilities from `vktGlobalPriorityQueueUtils.cpp/.hpp`. No Level-3 documentation is created for the utils file.
- **Limited transition combinations**: Only graphics<->compute and compute<->transfer transitions are tested; graphics<->transfer is explicitly skipped.
- **Same priority for both queues**: In the queue transition tests, both the source and destination queues use the same global priority level. Different priorities between queues are only tested in the preemption sub-group.
- **Preemption is best-effort**: The preemption tests cannot guarantee that preemption actually occurs; they only verify that both workloads complete correctly when submitted with different priorities.
