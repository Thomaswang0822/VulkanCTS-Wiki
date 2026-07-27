## Overview

**Core question:** Do batched buffer and image bindings preserve data across the binding modes and extension paths registered by this test family?

- [`vktMemoryBindingTests.cpp`](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp) implements `memory.binding` for buffers and linear `VK_FORMAT_R8G8B8A8_UINT` images.
- Each test case creates ten targets, binds them with `vkBindBufferMemory2` or `vkBindImageMemory2`, transfers deterministic bytes through them, and compares the readback on the host.
- The five top-level behaviors cover ordinary binding, aliases, allocation-time priority, dynamic priority updates, and maintenance6 individual bind results.

## Background Knowledge

For the shared concepts memory types, heaps, and resource compatibility, host-visible and non-coherent memory, flush and invalidate direction, and memory dependencies, see [Background Knowledge](../../categories/memory.md#background-knowledge) of the `memory` page.

- **Resource-memory binding:** The `*Memory2` commands accept an array of bind descriptions and bind several resources in one call.
- **Dedicated and non-dedicated allocations:** A dedicated allocation names its buffer or image in a `VkMemoryDedicatedAllocateInfo` chain. A non-dedicated allocation omits that identity. The registered name `suballocated` denotes the latter path here, although this implementation still creates one allocation for each target.
- **Aliasing:** Two resources bound to the same memory range access the same backing bytes. The aliasing cases write through one resource and read through its partner.
- **Memory priority and bind status:** `VkMemoryPriorityAllocateInfoEXT` sets allocation-time priority, `vkSetDeviceMemoryPriorityEXT` updates an allocation, and `VkBindMemoryStatusKHR` reports the result of one element in a batched bind.

## Registration Hierarchy

```text
memory.binding
├── regular
├── aliasing
├── priority
├── priority_dynamic
└── maintenance6
```

The root dispatcher adds this test family to `memory` in [`createChildren`](../../../modules/vulkan/memory/vktMemoryTests.cpp#L52-L78). The default mustpass list contains 336 `dEQP-VK.memory.binding.*` test cases.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test-family behavior | `regular`, `aliasing`, `priority`, `priority_dynamic`, `maintenance6` | Selects the binding relationship and extension behavior. | [registration loop](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp#L1126-L1237) |
| Allocation path | `suballocated`, `dedicated`, `overallocated` | Chooses a non-dedicated allocation, a dedicated allocation, or the dedicated overallocation variant. Aliasing only uses `suballocated`. | [intermediate-node construction](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp#L1143-L1153) |
| Resource and size | `buffer_33`, `buffer_257`, `buffer_4087`, `buffer_8095`, `buffer_1048577`; `image_8_8` through `image_257_257` for each width/height in `{8, 33, 257}` | Changes transfer byte count and memory requirements. | [test-case generation](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp#L1155-L1210) |
| Target count | `10` | Exercises a ten-element bind array and ten independent round trips per test case. | [parameter creation](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp#L1159-L1199) |
| Priority values | `0.0` through `0.9` | Assigns allocation index `i` the value `i / 10`, at allocation time or through a later update. | [allocation paths](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp#L575-L724) |
| Individual bind result | disabled, enabled under `maintenance6` | Adds one `VkBindMemoryStatusKHR` to each bind info and checks each result. | [binding functions](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp#L726-L815) |
| Overallocation factor | `1.5`, `2.3`, `3.0` | Enlarges dedicated image allocation requirements according to the generated case index. | [factor selection and image allocation](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp#L684-L719) |

## Behavior Parameters

The primary behavioral axis is the top-level behavior below `memory.binding`.

### `regular` - round trip through each bound resource

This behavior checks ordinary batched binding. The host copies deterministic data into each target and back from the same target. Its intermediate nodes cover non-dedicated, dedicated, and overallocated configurations.

### `aliasing` - write through one resource and read through its alias

This behavior creates two target sets and binds both sets to the same memory objects. For each index, the host writes the first resource and reads the second. Images set `VK_IMAGE_CREATE_ALIAS_BIT`, and the second image receives its layout transition before the first alias is written.

### `priority` - allocation-time priority

This behavior repeats regular and aliasing tests while chaining `VkMemoryPriorityAllocateInfoEXT` into allocation. Allocation index `i` receives priority `i / 10`, so the ten targets span 0.0 through 0.9. The payload check stays unchanged.

### `priority_dynamic` - priority update after allocation

This behavior creates a logical device with `VK_EXT_memory_priority` and `VK_EXT_pageable_device_local_memory`, then calls `vkSetDeviceMemoryPriorityEXT` for each allocation. Most allocation paths omit the allocation-time priority chain in this mode. The dedicated-image specialization includes the priority structure for every non-default mode and also performs the dynamic update. The behavior repeats regular and aliasing paths.

### `maintenance6` - individual status for each bind

This behavior repeats default, static-priority, and dynamic-priority regular and aliasing paths. Each bind description chains a separate `VkBindMemoryStatusKHR`; the test checks the command result and then every individual result before running transfers.

## Shader Analysis

No shader participates in this test family. The device work consists of transfer commands and pipeline barriers, and the host performs the final byte comparison. No shader source, shader module, SPIR-V, descriptor set, or graphics/compute pipeline is generated.

## Runtime Execution and Result Checking

- The host creates ten buffers or images. Aliasing cases create two sets of ten.
- It queries each target's memory requirements and allocates one `VkDeviceMemory` object per target index. Dedicated paths chain the target identity. Static-priority paths chain the priority value, and dynamic paths call `vkSetDeviceMemoryPriorityEXT` after allocation. The dedicated-image dynamic path does both.
- It builds a ten-element bind array and calls `vkBindBufferMemory2` or `vkBindImageMemory2`. Maintenance6 cases initialize each individual result to `VK_ERROR_UNKNOWN`, attach its status structure, and require every returned result to be successful.
- A host-visible source buffer receives a deterministic byte sequence. The host flushes mapped memory before submitting transfer work.
- Regular cases copy source to target and target to destination. Aliasing cases copy source to alias set 0 and alias set 1 to destination. Buffer and image barriers provide the host/transfer and transfer/transfer dependencies needed by these copies.
- After each round trip, the host invalidates destination memory and compares the first `bufferSize` bytes. Regular cases regenerate seed 1; aliasing cases regenerate seed 2.
- The test passes only when every target's bytes match. A failed Vulkan call is reported through `VK_CHECK`; a byte mismatch returns `Failed`.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `regular` | Batched binding, non-dedicated or dedicated allocation binding, oversized image allocation binding, or transfer data-integrity failure. |
| `aliasing` | Aliased resource binding or cross-alias transfer visibility failure. |
| `priority` | Allocation-time memory-priority handling, or the underlying regular/aliasing binding and transfer path, failed. |
| `priority_dynamic` | Dynamic memory-priority update handling, custom-device setup, or the underlying regular/aliasing binding and transfer path, failed. |
| `maintenance6` | Individual bind-status reporting, or the enclosed default/static/dynamic regular/aliasing path, failed. |

### Cause Analysis

#### Batched binding or allocation binding failure

**Possible failure symptoms:** `vkBindBufferMemory2` or `vkBindImageMemory2` returns an error, or readback differs for one or more regular targets.

**Possible implementation causes:** The implementation may mishandle an element of the bind-info array, the selected compatible memory type, a dedicated-allocation chain, or an allocation larger than the image requirement. A byte mismatch can also come from the transfer or synchronization path used to make the binding observable.

#### Aliased resource binding or cross-alias visibility failure

**Possible failure symptoms:** A write through alias set 0 does not produce the expected bytes when copied from alias set 1.

**Possible implementation causes:** The implementation may associate the aliases with different backing storage, mishandle image alias creation or layout state, or fail to preserve the transfer dependency between the write and read operations.

#### Allocation-time memory-priority handling failure

**Possible failure symptoms:** Allocation or binding fails only when `VkMemoryPriorityAllocateInfoEXT` is present, or a priority case returns corrupted readback while the matching default case succeeds.

**Possible implementation causes:** The allocation path may reject or misread a valid priority in the inclusive 0-to-1 range, or may mishandle the priority structure when it precedes a dedicated-allocation structure in the `pNext` chain. The payload does not test eviction policy or performance.

#### Dynamic memory-priority or custom-device failure

**Possible failure symptoms:** Feature/device setup fails, `vkSetDeviceMemoryPriorityEXT` causes a failure, or later binding and transfer checks fail only in `priority_dynamic` cases.

**Possible implementation causes:** The implementation may expose inconsistent feature support, mishandle the valid priority update, or corrupt allocation state after the update. The custom device path can also expose device or queue setup defects before binding begins.

#### Individual bind-status reporting failure

**Possible failure symptoms:** The batch command succeeds but one status remains `VK_ERROR_UNKNOWN` or contains another error; later payload comparison can also fail in the enclosed path.

**Possible implementation causes:** The maintenance6 path may fail to write one `VkBindMemoryStatusKHR::pResult`, report a result inconsistent with the corresponding bind, or mishandle the status structure in a bind-info `pNext` chain.

## Case Pruning

### Requirement-based pruning

- Every test case requires `VK_KHR_bind_memory2`.
- `priority` and `priority_dynamic` require the `memoryPriority` feature from `VK_EXT_memory_priority`.
- `priority_dynamic` also requires `VK_EXT_pageable_device_local_memory`; its custom device enables `pageableDeviceLocalMemory`.
- `maintenance6` requires `VK_KHR_maintenance6`. Dynamic-priority maintenance6 cases also enable its feature on the custom device.
- Allocation uses a memory type allowed by the resource memory requirements. Source and destination buffers select a host-visible compatible type.

### Design-based pruning

- Aliasing has only the `suballocated` intermediate node; there are no dedicated or overallocated aliasing leaves.
- Vulkan SC registers one default iteration, omitting priority and maintenance6 variants.
- The registered `suballocated` path does not pack targets into a shared allocation. It gives each resource index a separate non-dedicated allocation.
- `regular.overallocated.buffer_*` leaves are registered, but the dedicated-buffer allocator uses the unmodified memory requirement. Only the dedicated-image allocator applies `overallocationFactor`; the buffer leaves therefore exercise the ordinary dedicated-buffer path under those registered names.

## Key Takeaways

- The test makes binding observable with deterministic transfer round trips rather than shaders.
- Aliasing changes the read resource, not the expected bytes: set 0 receives the write and set 1 supplies the readback.
- Priority variants verify that valid priority metadata and updates do not break allocation, binding, or data integrity; they do not measure residency policy or speed.
- Maintenance6 adds per-element result checking to the same binding behaviors. See `Failure Meaning` for diagnosis by behavior.

## Source Reference Appendix

| Source area | Purpose |
|-------------|---------|
| [`BindingCaseParameters` and resource creation](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp#L143-L230) | Defines target count, dimensions, transfer usage, image format, and creation flags. |
| [Memory allocation helpers and specializations](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp#L234-L350) | Builds allocation, dedicated, priority, bind-info, and status structures. |
| [Target allocation paths](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp#L545-L724) | Allocates non-dedicated/dedicated memory, applies priority, and implements image overallocation. |
| [Batched binding](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp#L726-L815) | Calls the buffer/image `*Memory2` commands and checks individual maintenance6 results. |
| [Transfer, synchronization, and comparison](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp#L817-L988) | Copies through resources, handles image layouts, and compares host readback. |
| [Regular and aliasing instances](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp#L990-L1084) | Implements the two data-flow shapes. |
| [Support checks and registration](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp#L1086-L1237) | Gates extensions/features and creates the complete test matrix. |
| [`memory` root registration](../../../modules/vulkan/memory/vktMemoryTests.cpp#L52-L76) | Attaches `binding` to the parent test category. |
| [Default mustpass list](../../../mustpass/main/vk-default/memory.txt) | Provides the shipped `dEQP-VK.memory.binding.*` case inventory. |
| [Vulkan resource binding rules](../../../../vulkan-docs/src/chapters/resources.adoc#L10511-L10677) | Defines batched binding and individual bind-status semantics. |
| [Vulkan memory priority rules](../../../../vulkan-docs/src/chapters/memory.adoc#L2108-L2170) | Defines static and dynamic memory priority operations and valid ranges. |
