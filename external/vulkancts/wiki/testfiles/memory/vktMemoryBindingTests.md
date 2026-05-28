# Memory Binding Tests

Memory binding tests exercising `VK_KHR_bind_memory2`. Validates batch binding of buffers and images to device memory, including aliasing, dedicated allocation, overallocation, and memory priority scenarios.

The historical Vulkan API test plan calls out binding buffers/images, sub-allocation, rebinding, aliasing, and supported allocation types as binding-memory objectives ([`apitests.adoc`](../../../../../doc/testspecs/VK/apitests.adoc#L257-L266)); current source and mustpass remain authoritative for exact behavior.

## Source

- [vktMemoryBindingTests.cpp](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp)

## Registration

- **Group name:** `binding`
- **Registration function:** [`createMemoryBindingTests()`](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp#L1127)
- **Parent group:** `memory`

## Registration Hierarchy

```text
memory.binding
├── regular
├── aliasing
├── priority
├── priority_dynamic
└── maintenance6
```

## Test Families

### regular — Standard memory binding

Standard memory binding tests using `vkBindBufferMemory2()` / `vkBindImageMemory2()`. Tests both suballocated (shared memory) and dedicated allocation patterns. Each test creates 10 buffers or images, allocates individual memory for each, binds them, then verifies data integrity by copying data through each resource.

The `regular` group contains three subgroups:

- **suballocated** — Resources share a single memory allocation. Individual buffer and image tests are generated for each size variant: `buffer_33`, `buffer_257`, `buffer_4087`, `buffer_8095`, `buffer_1048577`, and images `image_8_8` through `image_257_257` (all 3x3 combinations of widths and heights from {8, 33, 257}).
- **dedicated** — Each resource gets its own dedicated memory allocation. Same size variants as suballocated.
- **overallocated** — Tests binding with intentionally oversized dedicated memory allocations (factors of 1.5x, 2.3x, 3.0x) for both buffer and image size variants; the source adds overallocated buffer cases and image cases separately ([vktMemoryBindingTests.cpp:1157](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp#L1157), [vktMemoryBindingTests.cpp:1181-L1182](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp#L1181-L1182), [vktMemoryBindingTests.cpp:1207-L1210](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp#L1207-L1210)).

### aliasing — Memory aliasing

Tests memory aliasing where two sets of resources are bound to the same underlying memory. Validates that writing to one alias and reading from another produces correct results. Images use `VK_IMAGE_CREATE_ALIAS_BIT` ([vktMemoryBindingTests.cpp:1168](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp#L1168)).

The `aliasing` group contains a **suballocated** subgroup with the same buffer and image size variants as `regular`.

### priority — Static memory priority

Tests `VK_EXT_memory_priority` with static priority values set during allocation via `VkMemoryPriorityAllocateInfoEXT` ([vktMemoryBindingTests.cpp:593-595](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp#L593)). Contains the same `regular` and `aliasing` subgroup structure as the top-level binding tests, but with priority values ranging from 0.0 to 0.9.

### priority_dynamic — Dynamic memory priority

Tests `VK_EXT_pageable_device_local_memory` with dynamic priority changes after allocation using `vkSetDeviceMemoryPriorityEXT()` ([vktMemoryBindingTests.cpp:602-604](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp#L602)). Contains the same `regular` and `aliasing` subgroup structure as the top-level binding tests, but with dynamically changing priority values.

### maintenance6 — Individual bind result checking

Tests `VK_KHR_maintenance6` individual bind result checking via `VkBindMemoryStatusKHR` chained to each bind info ([vktMemoryBindingTests.cpp:738-746](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp#L738)). Contains the same `regular`, `aliasing`, `priority`, and `priority_dynamic` subgroup structure as the top-level binding tests, but with `checkIndividualResult=true` so each bind operation reports its own success/failure.

## Parameter Dimensions

| Dimension | Values |
|-----------|--------|
| Resource type | Buffer, Image |
| Allocation mode | Suballocated, Dedicated, Overallocated |
| Buffer sizes | 33, 257, 4087, 8095, 1MB+1 bytes |
| Image sizes | 8x8, 8x33, 8x257, 33x8, 33x33, 33x257, 257x8, 257x33, 257x257 |
| Target count | 10 per test |
| Priority mode | Default, Static (0.0 to 0.9), Dynamic |
| Individual result check | Off (default), On (maintenance6) |
| Overallocation factors | 1.5, 2.3, 3.0 |

## Support / Feature Requirements

| Extension/Feature | Required by |
|-------------------|-------------|
| `VK_KHR_bind_memory2` | All tests ([vktMemoryBindingTests.cpp:1108](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp#L1108)) |
| `VK_EXT_memory_priority` | priority and priority_dynamic groups ([vktMemoryBindingTests.cpp:1111-1112](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp#L1111)) |
| `VK_EXT_pageable_device_local_memory` | priority_dynamic group ([vktMemoryBindingTests.cpp:1113-1115](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp#L1113)) |
| `VK_KHR_maintenance6` | maintenance6 group ([vktMemoryBindingTests.cpp:1116-1117](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp#L1116)) |

## Verification Method

Each test follows this pattern:

1. **Create resources** — 10 buffers or images with specified parameters
2. **Allocate memory** — individual allocations per resource (or shared for suballocated)
3. **Bind** — batch bind all resources using `vkBindBufferMemory2()` / `vkBindImageMemory2()` ([vktMemoryBindingTests.cpp:760](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp#L760), [vktMemoryBindingTests.cpp:805](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp#L805))
4. **Write** — fill a source buffer with pseudo-random data seeded with a known value
5. **Copy through** — for each target resource, copy data from source buffer through the target to a destination buffer
6. **Verify** — read back destination buffer and compare against expected pseudo-random sequence ([vktMemoryBindingTests.cpp:973-988](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp#L973))

For aliasing tests, the pattern is:
1. Create two sets of resources
2. Bind both sets to the same memory
3. Layout-transition alias 1, then write to alias 0
4. Read from alias 1 and verify data matches what was written to alias 0 ([vktMemoryBindingTests.cpp:1076-1080](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp#L1076))

## Test Principles

- **Batch binding correctness:** Verifies that `vkBindBufferMemory2`/`vkBindImageMemory2` correctly binds multiple resources in a single call
- **Data integrity:** End-to-end copy-through-verify ensures bound memory is functional for transfer operations
- **Aliasing safety:** Tests that resources sharing the same memory can be independently accessed
- **Priority behavior:** Validates that memory priority can be set at allocation time (static) or changed dynamically
- **Individual results:** With maintenance6, each bind operation reports its own success/failure via `VkBindMemoryStatusKHR`

## Notes

- Image format is fixed to `VK_FORMAT_R8G8B8A8_UINT` with linear tiling ([vktMemoryBindingTests.cpp:198-215](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp#L198))
- Buffer usage is `VK_BUFFER_USAGE_TRANSFER_SRC_BIT | VK_BUFFER_USAGE_TRANSFER_DST_BIT`
- The `priority_dynamic` tests create a custom device with the required extensions enabled ([vktMemoryBindingTests.cpp:458-489](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp#L458))
- Vulkan SC builds only run 1 iteration (no priority/maintenance6 variants) ([vktMemoryBindingTests.cpp:1133-1137](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp#L1133))
