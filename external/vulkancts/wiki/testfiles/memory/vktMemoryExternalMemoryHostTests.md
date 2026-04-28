# External Memory Host Tests

Tests for `VK_EXT_external_memory_host`. Validates importing host-allocated memory into Vulkan for use with buffers and images, including rendering and host-device synchronization scenarios.

## Source

- [vktMemoryExternalMemoryHostTests.cpp](../../../modules/vulkan/memory/vktMemoryExternalMemoryHostTests.cpp)

## Registration

- **Group name:** `external_memory_host`
- **Registration function:** [`createMemoryExternalMemoryHostTests()`](../../../modules/vulkan/memory/vktMemoryExternalMemoryHostTests.cpp#L1113)
- **Parent group:** `memory`

## Test Hierarchy

```
external_memory_host
├── simple_allocation
│   ├── minImportedHostPointerAlignment_x1
│   └── minImportedHostPointerAlignment_x3
├── bind_image_memory_and_render
│   ├── with_zero_offset
│   │   ├── r8g8b8a8_unorm
│   │   ├── r16g16b16a16_unorm
│   │   ├── r16g16b16a16_sfloat
│   │   └── r32g32b32a32_sfloat
│   └── with_non_zero_offset
│       ├── r8g8b8a8_unorm
│       ├── r16g16b16a16_unorm
│       ├── r16g16b16a16_sfloat
│       └── r32g32b32a32_sfloat
└── synchronization
    └── synchronization
```

## Test Families

### simple_allocation

Basic tests that verify host pointer memory import works. Allocates host memory aligned to `minImportedHostPointerAlignment` (×1 and ×3), queries memory type bits via `vkGetMemoryHostPointerPropertiesEXT()`, and allocates device memory from the host pointer ([vktMemoryExternalMemoryHostTests.cpp:296-319](../../../modules/vulkan/memory/vktMemoryExternalMemoryHostTests.cpp#L296)).

### bind_image_memory_and_render

Tests importing host memory and binding it to an image, then performing a render pass. Creates a 100x100 2D image with linear tiling, binds imported host memory, clears the image, renders a green triangle over a blue background, copies the result to a buffer, and compares against a reference image ([vktMemoryExternalMemoryHostTests.cpp:338-431](../../../modules/vulkan/memory/vktMemoryExternalMemoryHostTests.cpp#L338)).

- **with_zero_offset:** Binds image memory at offset 0
- **with_non_zero_offset:** Binds image memory at offset equal to `imageMemoryRequirements.alignment` ([vktMemoryExternalMemoryHostTests.cpp:376-377](../../../modules/vulkan/memory/vktMemoryExternalMemoryHostTests.cpp#L376))

### synchronization

Tests host-device synchronization using imported host memory. The test:
1. Creates a buffer with external host memory handle type
2. Fills the buffer with data via GPU (`vkCmdFillBuffer`)
3. Waits for GPU completion via fence
4. Host maps the imported memory, invalidates cache, and modifies the data
5. Host signals a timeline semaphore
6. GPU reads the modified data via a second command buffer waiting on the timeline semaphore
7. Verifies the result matches the host-modified data ([vktMemoryExternalMemoryHostTests.cpp:758-895](../../../modules/vulkan/memory/vktMemoryExternalMemoryHostTests.cpp#L758))

## Parameter Dimensions

| Parameter | Values |
|-----------|--------|
| Format (render tests) | `VK_FORMAT_R8G8B8A8_UNORM`, `VK_FORMAT_R16G16B16A16_UNORM`, `VK_FORMAT_R16G16B16A16_SFLOAT`, `VK_FORMAT_R32G32B32A32_SFLOAT` |
| Bind offset | 0, `imageMemoryRequirements.alignment` |
| Allocation size multiplier | 1×, 3× `minImportedHostPointerAlignment` |

## Support Requirements

| Extension/Feature | Required by |
|-------------------|-------------|
| `VK_EXT_external_memory_host` | All tests ([vktMemoryExternalMemoryHostTests.cpp:1037](../../../modules/vulkan/memory/vktMemoryExternalMemoryHostTests.cpp#L1037)) |
| `VK_KHR_timeline_semaphore` | synchronization test ([vktMemoryExternalMemoryHostTests.cpp:1085](../../../modules/vulkan/memory/vktMemoryExternalMemoryHostTests.cpp#L1085)) |
| Color attachment with linear tiling | bind_image_memory_and_render tests ([vktMemoryExternalMemoryHostTests.cpp:1050-1051](../../../modules/vulkan/memory/vktMemoryExternalMemoryHostTests.cpp#L1050)) |

## Verification Methods

### simple_allocation

- Verifies `vkGetMemoryHostPointerPropertiesEXT()` returns valid `memoryTypeBits`
- Finds a compatible memory type index
- Successfully allocates device memory from host pointer via `VkImportMemoryHostPointerInfoEXT` ([vktMemoryExternalMemoryHostTests.cpp:247-261](../../../modules/vulkan/memory/vktMemoryExternalMemoryHostTests.cpp#L247))

### bind_image_memory_and_render

- Renders a triangle to the imported-host-memory-backed image
- Copies result to a host-visible buffer
- Compares rendered output against reference image using `tcu::floatThresholdCompare` with 0.01 tolerance ([vktMemoryExternalMemoryHostTests.cpp:426-428](../../../modules/vulkan/memory/vktMemoryExternalMemoryHostTests.cpp#L426))
- Reference image has three zones: green (x<50), red (50≤x<75), blue (x≥75) ([vktMemoryExternalMemoryHostTests.cpp:688-699](../../../modules/vulkan/memory/vktMemoryExternalMemoryHostTests.cpp#L688))

### synchronization

- After GPU fill + host modify + GPU read cycle, compares result buffer against reference
- Also verifies that host-mapped pointer and device-mapped pointer point to the same memory via `deMemCmp` ([vktMemoryExternalMemoryHostTests.cpp:865-866](../../../modules/vulkan/memory/vktMemoryExternalMemoryHostTests.cpp#L865))

## External Memory Property Validation

The test validates that external memory properties for `VK_EXTERNAL_MEMORY_HANDLE_TYPE_HOST_ALLOCATION_BIT_EXT` are correct ([vktMemoryExternalMemoryHostTests.cpp:71-83](../../../modules/vulkan/memory/vktMemoryExternalMemoryHostTests.cpp#L71)):
- `compatibleHandleTypes` must include the host allocation bit
- `externalMemoryFeatures` must **not** include `VK_EXTERNAL_MEMORY_FEATURE_DEDICATED_ONLY_BIT`
- `externalMemoryFeatures` must include `VK_EXTERNAL_MEMORY_FEATURE_IMPORTABLE_BIT`

## Test Principles

- **Host pointer alignment:** Tests verify that `minImportedHostPointerAlignment` is a power of two and within the 64KB limit ([vktMemoryExternalMemoryHostTests.cpp:220-224](../../../modules/vulkan/memory/vktMemoryExternalMemoryHostTests.cpp#L220))
- **Memory type compatibility:** Tests find memory types that satisfy both the resource requirements and the host pointer properties
- **Render correctness:** End-to-end render test validates that imported host memory works correctly as a color attachment
- **Synchronization:** The synchronization test validates proper cache invalidation/flush when host and device share the same memory, using timeline semaphores for host-to-device signaling

## Notes

- All images use `VK_IMAGE_TILING_LINEAR` ([vktMemoryExternalMemoryHostTests.cpp:344](../../../modules/vulkan/memory/vktMemoryExternalMemoryHostTests.cpp#L344))
- Image dimensions are fixed at 100x100 ([vktMemoryExternalMemoryHostTests.cpp:446](../../../modules/vulkan/memory/vktMemoryExternalMemoryHostTests.cpp#L446))
- The synchronization test format is fixed to `VK_FORMAT_R8G8B8A8_UNORM` ([vktMemoryExternalMemoryHostTests.cpp:760](../../../modules/vulkan/memory/vktMemoryExternalMemoryHostTests.cpp#L760))
- Host memory is allocated via `deAlignedMalloc` and reallocated via `deAlignedRealloc` as needed to meet size requirements
