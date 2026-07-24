## Overview

**Core question:** Do eligible Vulkan memory types support the required allocation and free sequences in ordinary, device-group, and pageable device-local-memory modes?

- This page covers [`vktMemoryAllocationTests.cpp`](../../../modules/vulkan/memory/vktMemoryAllocationTests.cpp), which implements the `memory.allocation`, `memory.device_group_allocation`, and `memory.pageable_allocation` test families.
- All three families use the same generated `basic` and `random` areas. The allocation mode changes device creation and allocation metadata.
- The tests allocate `VkDeviceMemory` objects without binding them to resources. A temporary buffer supplies memory requirements in the deterministic path.

## Background Knowledge

For the shared concept memory types, heaps, and resource compatibility, see [Background Knowledge](../../categories/memory.md#background-knowledge) of the `memory` page.

- `VkMemoryAllocateFlagsInfo` supplies a device mask for device-group allocations. Pageable device-local allocations require the corresponding feature and extension setup.
- The `forward` and `reverse` registered identifiers must not be read as an English description of the free loop. In this implementation, `forward` allocates all objects then frees them in reverse index order; `reverse` frees them in allocation index order.

## Registration Hierarchy

```text
memory
├── allocation
├── device_group_allocation
└── pageable_allocation
```

All three direct test families are rooted in the same implementation file and share its generated child areas.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test family | `allocation`, `device_group_allocation`, `pageable_allocation` | Selects the ordinary, device-group, or pageable device-local allocation mode. | [`createAllocationTestsCommon`](../../../modules/vulkan/memory/vktMemoryAllocationTests.cpp#L1027-L1043) |
| Behavior area | `basic`, `random` | Selects a deterministic count/order matrix or bounded seeded allocation/free stress. | [`createAllocationTestsCommon`](../../../modules/vulkan/memory/vktMemoryAllocationTests.cpp#L1067-L1197) |
| Nominal allocation size | `64`, `128`, `256`, `512`, `1KiB`, `4KiB`, `8KiB`, `1MiB`; `percent_1` | Changes the allocation size or selects one percent of the current heap. | [`createAllocationTestsCommon`](../../../modules/vulkan/memory/vktMemoryAllocationTests.cpp#L1045-L1057) |
| Allocation count | `1`, `10`, `100`, `1000`, computed count | Changes the number of concurrently live memory objects. | [`createAllocationTestsCommon`](../../../modules/vulkan/memory/vktMemoryAllocationTests.cpp#L1083-L1115) |
| Free order | `forward`, `reverse`, `mixed` | Changes when objects are freed: reverse index, allocation index, or immediately after each allocation. | [`AllocateFreeTestInstance::iterate`](../../../modules/vulkan/memory/vktMemoryAllocationTests.cpp#L514-L596) |
| Device mask | nonzero subset masks or all devices | Device-group mode repeats work for the masks allowed by the selected physical-device group. | [`AllocateFreeTestInstance::iterate`](../../../modules/vulkan/memory/vktMemoryAllocationTests.cpp#L503-L513) |

## Behavior Parameters

The test family is the primary behavioral axis. Each family uses the same generated hierarchy but configures a different allocation mode.

### allocation: ordinary device-memory allocation

This family uses the ordinary custom-device path and checks allocation/free behavior for each eligible memory type. It has no device-group allocation flags or pageable-memory feature chain.

### device_group_allocation: allocation with a device mask

This family creates a device-group device and passes `VkMemoryAllocateFlagsInfo` with `VK_MEMORY_ALLOCATE_DEVICE_MASK_BIT`. When subset allocation is available, each nonzero mask is exercised; otherwise, the all-devices mask is used.

### pageable_allocation: pageable device-local allocation

This family enables `VK_EXT_pageable_device_local_memory` and `VK_EXT_memory_priority` during custom-device creation. It then runs the same deterministic and randomized allocation patterns under the pageable allocation mode.

The secondary behavioral axis is `basic` versus `random`.

### basic: deterministic count and free-order matrix

The deterministic path selects an eligible memory type, creates a transfer buffer to obtain requirements, then allocates the requested number of memory objects. It checks every allocation result and frees handles according to the selected order.

### random: bounded seeded allocation/free stress

The random path makes 128 seeded choices between allocation and free where permitted, limits each heap to one eighth of its size, then frees all remaining objects. It exercises lifetime transitions rather than one fixed order.

## Shader Analysis

No shader code participates in this test. The test observes allocation API results and memory-object lifetimes on the host.

## Runtime Execution and Result Checking

- `basic` iterates each reported memory type. It creates a transfer source/destination buffer, retrieves its requirements, chooses the requested allocation size, and calls `vkAllocateMemory` for each object. [`AllocateFreeTestInstance::iterate`](../../../modules/vulkan/memory/vktMemoryAllocationTests.cpp#L392-L631)
- The test fails on an allocation error or null result handle that is not covered by its explicit capacity and protected-memory exceptions. It also records an invalid memory-type heap index.
- The source skips a case when the rounded allocation total exceeds the heap. On 32-bit builds it avoids runs that would exceed its host virtual-address threshold for host-visible allocations. [`AllocateFreeTestInstance::iterate`](../../../modules/vulkan/memory/vktMemoryAllocationTests.cpp#L475-L500)
- `random` tracks heap usage and system/device-memory limits, performs 128 operations per seeded case, then releases remaining objects. [`RandomAllocFreeTestInstance::iterate`](../../../modules/vulkan/memory/vktMemoryAllocationTests.cpp#L839-L1024)

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `allocation` | Incorrect ordinary allocation/free behavior for an eligible memory type, size, count, or order. |
| `device_group_allocation` | Incorrect device-group allocation or device-mask handling, or ordinary allocation/free behavior under that mode. |
| `pageable_allocation` | Incorrect pageable device-local-memory feature setup or allocation/free behavior under that mode. |
| `basic` | Incorrect allocation result, handle creation, or selected free-order handling. |
| `random` | Incorrect allocation/free lifetime management under the bounded seeded stress sequence. |

### Cause Analysis

#### Ordinary allocation or free failure

**Possible failure symptoms:** A supported `vkAllocateMemory` call returns an unexpected error, returns a null handle, or the case records an invalid heap index.

**Possible implementation causes:** The symptom can indicate incorrect device-memory allocation accounting, memory-type handling, or release behavior. The CTS source excludes insufficient-capacity cases before treating an outcome as a failure; source-level investigation is needed to identify the implementation layer responsible for an unexpected result.

#### Device-group allocation or mask failure

**Possible failure symptoms:** A `device_group_allocation` case fails for a valid tested device mask while the same allocation configuration is otherwise eligible.

**Possible implementation causes:** The allocation's `VkMemoryAllocateFlagsInfo` device mask or device-group memory handling may be incorrect. The source checks group size and applies either every nonzero subset mask or the all-devices mask, so investigation should compare the failing mask with the selected group properties.

#### Pageable allocation setup or behavior failure

**Possible failure symptoms:** A `pageable_allocation` case fails after the extension and feature setup succeeded.

**Possible implementation causes:** The custom device enables the pageable-device-local-memory feature and memory-priority extension before the allocation loop. An unexpected allocation result may involve that feature chain or allocation behavior under pageable mode; source-level investigation is needed to localize it.

#### Random lifetime-management failure

**Possible failure symptoms:** A seeded random case fails while allocating or freeing its bounded set of objects.

**Possible implementation causes:** The result can arise from incorrect allocation accounting, lifetime tracking, or memory-limit behavior during interleaved operations. The fixed seed makes the sequence reproducible for a source-level investigation.

## Case Pruning

### Requirement-based pruning

- All three families are registered only outside Vulkan SC because they require freeing allocations; the random path also uses non-null allocation callbacks.
- `device_group_allocation` requires at least two physical devices in the selected group. [`commonCheckSupport`](../../../modules/vulkan/memory/vktMemoryAllocationTests.cpp#L1013-L1023)
- `pageable_allocation` requires `VK_EXT_pageable_device_local_memory`.
- Unsupported AMD device-coherent memory types, insufficient heap capacity, and incompatible memory-type cases are skipped by the source checks.

### Design-based pruning

- Fixed size/count combinations whose total exceeds 50 MiB are omitted.
- Computed-count variants are omitted when they duplicate `1`, `10`, `100`, or `1000`; small sizes do not receive computed-count cases.
- Percent cases stay below one eighth of a heap, and random cases limit each heap to one eighth of its size.

## Key Takeaways

- One implementation file drives three registered allocation modes; the allocation mode, rather than a different algorithm, defines their primary distinction.
- The `basic` matrix checks allocation count and lifetime order across eligible memory types.
- The `random` cases use fixed seeds and bounded heap usage to make allocation/free stress reproducible.
- The source-defined free loops, not the `forward` and `reverse` labels alone, determine the observed order.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Custom-device setup | [`BaseAllocateTestInstance`](../../../modules/vulkan/memory/vktMemoryAllocationTests.cpp#L124-L368) | Selects ordinary, device-group, or pageable feature configuration. |
| Deterministic allocation/free | [`AllocateFreeTestInstance::iterate`](../../../modules/vulkan/memory/vktMemoryAllocationTests.cpp#L392-L631) | Implements memory-type iteration, allocations, free order, and result collection. |
| Random stress sequence | [`RandomAllocFreeTestInstance::iterate`](../../../modules/vulkan/memory/vktMemoryAllocationTests.cpp#L839-L1024) | Implements bounded seeded allocation/free stress. |
| Registered matrices | [`createAllocationTestsCommon`](../../../modules/vulkan/memory/vktMemoryAllocationTests.cpp#L1027-L1216) | Defines family names, matrix values, and random case registration. |
| Mustpass coverage | [`memory.txt`](../../../mustpass/main/vk-default/memory.txt) | Contains 202 selected cases for each of the three allocation families. |
