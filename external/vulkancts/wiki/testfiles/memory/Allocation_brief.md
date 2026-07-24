# Understanding Brief: `memory.allocation`, `memory.device_group_allocation`, and `memory.pageable_allocation`

## One-Sentence Test Purpose

These tests check whether Vulkan allocates and frees device memory correctly across memory types, allocation sizes, free orders, randomized lifetimes, device-group masks, and pageable device-local memory mode.

## Background Knowledge

### Device memory types and heaps

A memory type selects a heap and property flags. A resource's memory requirements constrain which types can back it. The basic cases create a buffer before allocating so they can identify resource-compatible types. [Device memory properties](../../../../vulkan-docs/src/chapters/memory.adoc#L494-L553)

Why it matters here:

- Each case iterates reported memory types.
- The test skips a type or size when the heap cannot support the requested allocation safely.

### Allocation order and device masks

The ordinary test allocates a sequence of `VkDeviceMemory` objects, then frees them in a selected order. Device-group allocations include `VkMemoryAllocateFlagsInfo` and a device mask. [Device memory allocation](../../../../vulkan-docs/src/chapters/memory.adoc#L1052-L1077)

Why it matters here:

- The order dimension changes allocation lifetime behavior.
- The device-group family checks available device masks when subset allocation is supported.

## One Concrete Example

A `memory.allocation.basic.size_4KiB.forward.count_100` case chooses each memory type in turn, creates a 4 KiB transfer buffer to obtain memory requirements, allocates 100 matching memory objects, then frees the objects in reverse index order. The `forward` identifier refers to `ALLOC_FREE`; source, rather than the name alone, determines the actual free loop.

## End-to-End Test Flow

```text
[host] select an allocation mode and create the required logical device
[host] choose a memory type and derive a compatible allocation size
[host] allocate memory objects using the selected count and order
[host] for device-group mode, repeat for each required device mask
[host] free remaining objects and continue to the next memory type
[host] collect allocation errors and report the case result
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The page has no shader programs or pipelines.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Probe buffer | yes | no | no | no | Supplies requirements and compatible memory-type bits for the deterministic path. |
| `VkDeviceMemory` objects | yes | no | no | no | They are the allocated and freed objects under test. |
| `VkMemoryAllocateFlagsInfo` | yes, device-group mode | no | no | no | Supplies the device mask for a device-group allocation. |

## What Is Checked

- Each successful `allocateMemory` call must return `VK_SUCCESS` and a non-null handle.
- The deterministic path checks every reported memory type, subject to source-defined support and resource-capacity skips.
- The randomized path performs 128 seeded allocation/free operations, then frees remaining allocations.
- A case fails when the source records an allocation or memory-configuration error that is not an allowed skip or tolerated protected-memory limitation.

## Behavior Parameter Identification

> **Behavior parameter:** test family
>
> **Candidate values:** `allocation`, `device_group_allocation`, `pageable_allocation`

A second behavioral axis under each family is `basic` versus `random`: deterministic allocation/free ordering versus randomized allocation lifetime stress.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `allocation` | Incorrect ordinary allocation/free behavior for an eligible memory type, size, count, or order. |
| `device_group_allocation` | Incorrect device-group allocation or device-mask handling, or ordinary allocation/free behavior under that mode. |
| `pageable_allocation` | Incorrect pageable device-local-memory feature setup or allocation/free behavior under that mode. |
| `basic` | Incorrect allocation result, handle creation, or selected free-order handling. |
| `random` | Incorrect allocation/free lifetime management under the bounded seeded stress sequence. |

## Important Variations and Special Cases

- The three families share one generator and each has 102 `basic` plus 100 `random` mustpass cases.
- `device_group_allocation` requires at least two physical devices.
- `pageable_allocation` requires `VK_EXT_pageable_device_local_memory` and enables `VK_EXT_memory_priority` for its custom device. [Pageable device-local memory](../../../../vulkan-docs/src/chapters/memory.adoc#L1205-L1227)
- The random path is omitted in Vulkan SC because it uses non-null allocation callbacks.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Custom-device setup | [`BaseAllocateTestInstance`](../../../modules/vulkan/memory/vktMemoryAllocationTests.cpp#L124-L368) | Selects standard, device-group, or pageable setup. |
| Deterministic allocation/free | [`AllocateFreeTestInstance::iterate`](../../../modules/vulkan/memory/vktMemoryAllocationTests.cpp#L392-L631) | Implements type iteration, allocation, order behavior, and result collection. |
| Random stress | [`RandomAllocFreeTestInstance`](../../../modules/vulkan/memory/vktMemoryAllocationTests.cpp#L681-L1024) | Implements bounded seeded allocation/free stress. |
| Registration | [`createAllocationTestsCommon`](../../../modules/vulkan/memory/vktMemoryAllocationTests.cpp#L1027-L1216) | Defines all names and parameter values. |

## Questions / Risk Points for User Audit

- Is the source-defined distinction between `forward` and `reverse` free loops explicit enough?
- Does the family axis make the standard, device-group, and pageable modes clearer than their common implementation file alone?

## Conversion Notes for Final Wiki Rewrite

- Use test family as the primary page-level behavior axis and `basic`/`random` as the secondary axis.
- Copy the Failure Cause Mapping table unchanged into the final page.
- State that no shader participates in the test.
