# Memory Binding Tests

Memory binding tests exercising `VK_KHR_bind_memory2`. Validates batch binding of buffers and images to device memory, including aliasing, dedicated allocation, overallocation, and memory priority scenarios.

## Source

- [vktMemoryBindingTests.cpp](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp)

## Registration

- **Group name:** `binding`
- **Registration function:** [`createMemoryBindingTests()`](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp:1127)
- **Parent group:** `memory`

## Test Hierarchy

```
binding
├── regular
│   ├── suballocated
│   │   ├── buffer_33
│   │   ├── buffer_257
│   │   ├── buffer_4087
│   │   ├── buffer_8095
│   │   ├── buffer_1048577
│   │   ├── image_8_8
│   │   ├── image_8_33
│   │   ├── image_8_257
│   │   ├── image_33_8
│   │   ├── image_33_33
│   │   ├── image_33_257
│   │   ├── image_257_8
│   │   ├── image_257_33
│   │   └── image_257_257
│   ├── dedicated (same sub-cases as suballocated)
│   └── overallocated (same sub-cases as suballocated)
├── aliasing
│   └── suballocated
│       ├── buffer_* (same sizes as regular)
│       └── image_* (same sizes as regular)
├── priority
│   ├── regular (same structure as top-level regular)
│   └── aliasing (same structure as top-level aliasing)
├── priority_dynamic
│   ├── regular (same structure)
│   └── aliasing (same structure)
└── maintenance6
    └── (same structure as top-level, with checkIndividualResult=true)
        ├── regular
        ├── aliasing
        ├── priority
        └── priority_dynamic
```

## Test Families

### regular

Standard memory binding tests using `vkBindBufferMemory2()` / `vkBindImageMemory2()`. Tests both suballocated (shared memory) and dedicated allocation patterns. Each test creates 10 buffers or images, allocates individual memory for each, binds them, then verifies data integrity by copying data through each resource.

### aliasing

Tests memory aliasing where two sets of resources are bound to the same underlying memory. Validates that writing to one alias and reading from another produces correct results. Images use `VK_IMAGE_CREATE_ALIAS_BIT` ([vktMemoryBindingTests.cpp:1168](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp:1168)).

### overallocated

Tests binding with intentionally oversized memory allocations (factors of 1.5x, 2.3x, 3.0x). Only applies to dedicated allocation tests for images ([vktMemoryBindingTests.cpp:697-700](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp:697)).

### priority

Tests `VK_EXT_memory_priority` with static priority values set during allocation via `VkMemoryPriorityAllocateInfoEXT` ([vktMemoryBindingTests.cpp:593-595](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp:593)).

### priority_dynamic

Tests `VK_EXT_pageable_device_local_memory` with dynamic priority changes after allocation using `vkSetDeviceMemoryPriorityEXT()` ([vktMemoryBindingTests.cpp:602-604](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp:602)).

### maintenance6

Tests `VK_KHR_maintenance6` individual bind result checking via `VkBindMemoryStatusKHR` chained to each bind info ([vktMemoryBindingTests.cpp:738-746](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp:738)).

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

## Support Requirements

| Extension/Feature | Required by |
|-------------------|-------------|
| `VK_KHR_bind_memory2` | All tests ([vktMemoryBindingTests.cpp:1108](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp:1108)) |
| `VK_EXT_memory_priority` | priority and priority_dynamic groups ([vktMemoryBindingTests.cpp:1111-1112](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp:1111)) |
| `VK_EXT_pageable_device_local_memory` | priority_dynamic group ([vktMemoryBindingTests.cpp:1113-1115](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp:1113)) |
| `VK_KHR_maintenance6` | maintenance6 group ([vktMemoryBindingTests.cpp:1116-1117](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp:1116)) |

## Verification Method

Each test follows this pattern:

1. **Create resources** — 10 buffers or images with specified parameters
2. **Allocate memory** — individual allocations per resource (or shared for suballocated)
3. **Bind** — batch bind all resources using `vkBindBufferMemory2()` / `vkBindImageMemory2()` ([vktMemoryBindingTests.cpp:760](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp:760), [vktMemoryBindingTests.cpp:805](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp:805))
4. **Write** — fill a source buffer with pseudo-random data seeded with a known value
5. **Copy through** — for each target resource, copy data from source buffer through the target to a destination buffer
6. **Verify** — read back destination buffer and compare against expected pseudo-random sequence ([vktMemoryBindingTests.cpp:973-988](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp:973))

For aliasing tests, the pattern is:
1. Create two sets of resources
2. Bind both sets to the same memory
3. Layout-transition alias 1, then write to alias 0
4. Read from alias 1 and verify data matches what was written to alias 0 ([vktMemoryBindingTests.cpp:1076-1080](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp:1076))

## Test Principles

- **Batch binding correctness:** Verifies that `vkBindBufferMemory2`/`vkBindImageMemory2` correctly binds multiple resources in a single call
- **Data integrity:** End-to-end copy-through-verify ensures bound memory is functional for transfer operations
- **Aliasing safety:** Tests that resources sharing the same memory can be independently accessed
- **Priority behavior:** Validates that memory priority can be set at allocation time (static) or changed dynamically
- **Individual results:** With maintenance6, each bind operation reports its own success/failure via `VkBindMemoryStatusKHR`

## Notes

- Image format is fixed to `VK_FORMAT_R8G8B8A8_UINT` with linear tiling ([vktMemoryBindingTests.cpp:198-215](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp:198))
- Buffer usage is `VK_BUFFER_USAGE_TRANSFER_SRC_BIT | VK_BUFFER_USAGE_TRANSFER_DST_BIT`
- The `priority_dynamic` tests create a custom device with the required extensions enabled ([vktMemoryBindingTests.cpp:458-489](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp:458))
- Vulkan SC builds only run 1 iteration (no priority/maintenance6 variants) ([vktMemoryBindingTests.cpp:1133-1137](../../../modules/vulkan/memory/vktMemoryBindingTests.cpp:1133))
