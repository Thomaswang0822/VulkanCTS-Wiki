# Understanding Brief: `synchronization.global_priority_transition`

## One-sentence purpose

This LEGACY-only family checks that work submitted through queues configured with Vulkan global priorities can transfer ownership correctly between queue families, and that a higher-priority submission completes correctly alongside a lower-priority workload.

## Concrete mental model

Think of two queues as two workers sharing Vulkan resources:

- A **queue-transition** case has a producer worker write an image, release ownership with a pipeline barrier, and a consumer worker acquire and read it. The queues have the same requested global priority; the test varies synchronization and queue modifiers.
- A **preemption** case starts a large workload on queue A, then submits a small workload on the higher-priority queue B. It verifies the outputs from both queues, but deliberately does not claim that hardware preemption itself can be observed or guaranteed.

The representative transition path is:

```text
dEQP-VK.synchronization.global_priority_transition.high.semaphore.protected.from_graphics_to_compute
```

The representative preemption path is:

```text
dEQP-VK.synchronization.global_priority_transition.compute_low_to_graphics_high_double_preemption
```

## End-to-end flow

```text
[registration] create global_priority_transition under LEGACY synchronization
[transition] choose priority, sync type, modifier, and one supported queue direction
[host] create a SpecialDevice with the requested queue priorities and separate families
[producer] write the test value (113) to an image
[ownership] release the image on queue A; acquire it on queue B
[consumer] read the image and write pass/fail data
[host] wait on fences and validate the result

[preemption] create devices/queues for a lower-priority large workload and a higher-priority small workload
[GPU] submit the large workload first, then the small workload (optionally twice)
[host] validate gradients or increasing buffer values for both workloads
```

## What the source registers

The factory is [`createGlobalPriorityQueueTests()`](../../../modules/vulkan/synchronization/vktGlobalPriorityQueueTests.cpp#L2281). It creates this hierarchy:

```text
synchronization.global_priority_transition
├── low
├── medium
├── high
├── realtime
└── preemption
```

Each of the four priority groups expands to:

```text
<priority> / <no_sync|semaphore> / <no_modifiers|sparse|protected>
    / <from_graphics_to_compute|from_compute_to_graphics|
       from_compute_to_transfer|from_transfer_to_compute>
```

The factory skips identical queue types and explicitly skips graphics↔transfer. Queue-transition cases use the same priority for source and destination queues. The `preemption` leaves use the form `<queueA>_<priorityA>_to_<queueB>_<priorityB>[_double_preemption]`; only strictly increasing priority pairs are registered.

The parent registration is visible in [`vktSynchronizationTests.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L134-L143): the family is added only to the LEGACY branch and is excluded from Vulkan SC builds.

## What is checked

### Queue transition

The producer writes the value `113`. In non-protected cases, a consumer compute shader writes `1` to the result buffer when pixel (0, 0) has the expected value; the host checks that result. In protected cases, a mismatch enters a deliberate loop and the host uses a ten-second fence timeout to detect it. The submission path uses either no semaphore or an explicit semaphore, depending on the leaf.

### Preemption

- Graphics workloads render a gradient and are checked with `tcu::floatThresholdCompare`.
- Compute workloads write increasing values beginning at zero.
- Transfer workloads are checked for increasing values with the transfer offset (1000).
- The large and small extents are 512×512 and 8×8 respectively.
- `_double_preemption` submits the small workload a second time.

A successful result proves completion and output correctness under the requested priorities; it is not proof that the scheduler physically preempted queue A.

## Support and skip conditions

The transition cases require `VK_KHR_get_physical_device_properties2`, `VK_EXT_global_priority`, and `VK_EXT_global_priority_query`, suitable R-channel format support, separate queue families with the requested priority, and any requested sparse/protected features. Sparse cases require sparse binding, sparse buffer residency, and sparse image-2D residency; protected cases require `protectedMemory`.

Preemption performs its own support checks, including `VK_KHR_global_priority` and the queue/device capabilities needed by the selected workload. A requested priority may produce `VK_ERROR_NOT_PERMITTED_KHR`; the implementation treats that as a quality warning rather than a conformance failure because denying the request is permitted.

## Audit conclusions

- Registration is LEGACY-only: no `synchronization2` or Vulkan SC path is created.
- The default mustpass list contains 396 leaves: 24 each under `low`, `medium`, `high`, and `realtime`, plus 300 under `preemption`.
- The transition matrix is 4 priorities × 2 sync modes × 3 modifiers × 4 directions = 96 registered leaves in total; the default mustpass selection contains 24 per priority.
- No graphics↔transfer transition leaves are generated.
- The old page remains intentionally preserved as the obsolete/source-era page; this brief is the audit companion for the rewritten page.

## Source map

| Topic | Source |
|---|---|
| Test factory and complete registration loops | [`vktGlobalPriorityQueueTests.cpp`](../../../modules/vulkan/synchronization/vktGlobalPriorityQueueTests.cpp#L2281-L2420) |
| LEGACY-only parent registration | [`vktSynchronizationTests.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L114-L159) |
| Default mustpass selection | [`synchronization.txt`](../../../mustpass/main/vk-default/synchronization.txt#L31336) |
| Transition support and queue-family checks | [`vktGlobalPriorityQueueTests.cpp`](../../../modules/vulkan/synchronization/vktGlobalPriorityQueueTests.cpp#L484-L555) |
| Transition submission and validation | [`vktGlobalPriorityQueueTests.cpp`](../../../modules/vulkan/synchronization/vktGlobalPriorityQueueTests.cpp#L321-L373) |
| Preemption support and execution | [`vktGlobalPriorityQueueTests.cpp`](../../../modules/vulkan/synchronization/vktGlobalPriorityQueueTests.cpp#L1430-L2277) |
