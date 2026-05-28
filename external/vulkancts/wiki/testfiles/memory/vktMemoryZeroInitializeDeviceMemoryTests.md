# Zero Initialize Device Memory Tests

Tests for `VK_EXT_zero_initialize_device_memory`. Validates that device memory allocated with `VK_MEMORY_ALLOCATE_ZERO_INITIALIZE_BIT_EXT` is correctly zero-initialized across all memory types, buffer usages, and image formats.

## Source

- [vktMemoryZeroInitializeDeviceMemoryTests.cpp](../../../modules/vulkan/memory/vktMemoryZeroInitializeDeviceMemoryTests.cpp)

## Registration

- **Group name:** `zero_initialize_device_memory`
- **Registration function:** [`createClearedAllocationControlTests()`](../../../modules/vulkan/memory/vktMemoryZeroInitializeDeviceMemoryTests.cpp#L1252)
- **Parent group:** `memory`

## Registration Hierarchy

```text
memory.zero_initialize_device_memory
├── clear_buffer
└── image_transition
```

## Test Families

### clear_buffer

Tests that buffer memory allocated with the zero-initialize flag contains all zeros. Iterates over all compatible memory types (excluding protected and AMD device-coherent memory). For non-host-visible buffers, data is copied to a host-visible buffer via `vkCmdCopyBuffer` for CPU verification ([vktMemoryZeroInitializeDeviceMemoryTests.cpp:136-222](../../../modules/vulkan/memory/vktMemoryZeroInitializeDeviceMemoryTests.cpp#L136)).

| Dimension | Values |
|-----------|--------|
| Buffer usage | `transfer_dst`, `uniform_texel_buffer`, `storage_texel_buffer`, `uniform_buffer`, `storage_buffer`, `index_buffer`, `vertex_buffer`, `indirect_buffer` |
| Buffer size | 1, 4, 4096, 4194304 (4MB) bytes |
| Host visible | `true`, `false` |

### image_transition

Tests that image memory allocated with the zero-initialize flag contains all zeros after transitioning from `VK_IMAGE_LAYOUT_ZERO_INITIALIZED_EXT`. Verification is done via transfer copy, compute shader read, or fragment shader read depending on the usage ([vktMemoryZeroInitializeDeviceMemoryTests.cpp:530-884](../../../modules/vulkan/memory/vktMemoryZeroInitializeDeviceMemoryTests.cpp#L530)).

| Dimension | Values |
|-----------|--------|
| Format | `R8_UNORM`, `R8G8_UNORM`, `R16_UNORM`, `R8G8B8_UNORM`, `R8G8B8A8_UNORM`, `R32_UINT`, `R32_SINT`, `R32_SFLOAT`, `R32G32B32A32_SFLOAT`, `BC1_RGBA_UNORM_BLOCK` |
| Usage | `transfer_src`, `sampled`, `storage` |
| Read stage | `xfer` (transfer), `comp` (compute), `frag` (fragment) |
| Mip size | 1×1, 4×4, 53×92, 512×512 |
| Mip level | `first_mip` (1-level image), `second_mip` (2-level image, reads level 1) |

#### Depth/stencil formats

Separate test cases for depth/stencil formats within `image_transition`. Uses a render pass with depth/stencil attachment, clears to zero, then draws a triangle and verifies the result ([vktMemoryZeroInitializeDeviceMemoryTests.cpp:1031-1246](../../../modules/vulkan/memory/vktMemoryZeroInitializeDeviceMemoryTests.cpp#L1031)).

| Dimension | Values |
|-----------|--------|
| Format | All formats from `formats::depthAndStencilFormats` |
| Mip size | 1×1, 4×4, 53×92, 512×512 |
| Mip level | `first_mip`, `second_mip` |

## Parameter Dimensions

### Memory type selection

The test iterates over all memory types that:
- Match the `MemoryRequirement::ZeroInitialize` requirement
- Are compatible with the resource's memory type bits
- Are **not** protected memory (`VK_MEMORY_PROPERTY_PROTECTED_BIT`)
- Are **not** AMD device-coherent memory (`VK_MEMORY_PROPERTY_DEVICE_COHERENT_BIT_AMD`) — the extension is not enabled by default for these ([vktMemoryZeroInitializeDeviceMemoryTests.cpp:101-109](../../../modules/vulkan/memory/vktMemoryZeroInitializeDeviceMemoryTests.cpp#L101))

### Allocation flags

Memory is allocated with `VkMemoryAllocateFlagsInfo` containing `VK_MEMORY_ALLOCATE_ZERO_INITIALIZE_BIT_EXT` in the `pNext` chain ([vktMemoryZeroInitializeDeviceMemoryTests.cpp:120-133](../../../modules/vulkan/memory/vktMemoryZeroInitializeDeviceMemoryTests.cpp#L120)).

### Image initial layout

Images are created with `VK_IMAGE_LAYOUT_ZERO_INITIALIZED_EXT` as the initial layout, which is the layout that indicates the memory has been zero-initialized ([vktMemoryZeroInitializeDeviceMemoryTests.cpp:560](../../../modules/vulkan/memory/vktMemoryZeroInitializeDeviceMemoryTests.cpp#L560)).

## Support / Feature Requirements

| Extension/Feature | Required by |
|-------------------|-------------|
| `VK_EXT_zero_initialize_device_memory` | All tests ([vktMemoryZeroInitializeDeviceMemoryTests.cpp:61](../../../modules/vulkan/memory/vktMemoryZeroInitializeDeviceMemoryTests.cpp#L61)) |
| Format support for image usage | image_transition tests — checked via `vkGetPhysicalDeviceImageFormatProperties` ([vktMemoryZeroInitializeDeviceMemoryTests.cpp:342-352](../../../modules/vulkan/memory/vktMemoryZeroInitializeDeviceMemoryTests.cpp#L342)) |
| Image extent support | image_transition tests — max extent checked ([vktMemoryZeroInitializeDeviceMemoryTests.cpp:357-362](../../../modules/vulkan/memory/vktMemoryZeroInitializeDeviceMemoryTests.cpp#L357)) |
| Mip level support | image_transition tests — max mip levels checked ([vktMemoryZeroInitializeDeviceMemoryTests.cpp:365-366](../../../modules/vulkan/memory/vktMemoryZeroInitializeDeviceMemoryTests.cpp#L365)) |

## Verification Methods

### Buffer zero-check ([vktMemoryZeroInitializeDeviceMemoryTests.cpp:200-213](../../../modules/vulkan/memory/vktMemoryZeroInitializeDeviceMemoryTests.cpp#L200))

For each memory type, the buffer contents are compared against a reference buffer filled with zeros using `memcmp()`. If any memory type fails, the test reports failure with details in the log.

### Image zero-check (transfer) ([vktMemoryZeroInitializeDeviceMemoryTests.cpp:618-650](../../../modules/vulkan/memory/vktMemoryZeroInitializeDeviceMemoryTests.cpp#L618))

1. Image is transitioned from `VK_IMAGE_LAYOUT_ZERO_INITIALIZED_EXT` to `VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL`
2. Image is copied to a host-visible buffer via `vkCmdCopyImageToBuffer`
3. Buffer contents are compared against a reference texture filled with zeros

### Image zero-check (shader read) ([vktMemoryZeroInitializeDeviceMemoryTests.cpp:738-814](../../../modules/vulkan/memory/vktMemoryZeroInitializeDeviceMemoryTests.cpp#L738))

1. Image is transitioned from `VK_IMAGE_LAYOUT_ZERO_INITIALIZED_EXT` to the appropriate layout (`GENERAL` for storage, `SHADER_READ_ONLY_OPTIMAL` for sampled)
2. A compute or fragment shader reads each pixel and writes to an SSBO
3. SSBO contents are compared against a reference texture filled with zeros
4. Expected values: RGB = 0, A = 1 for non-compressed formats (alpha defaults to 1.0)

### Depth/stencil zero-check ([vktMemoryZeroInitializeDeviceMemoryTests.cpp:1100-1246](../../../modules/vulkan/memory/vktMemoryZeroInitializeDeviceMemoryTests.cpp#L1100))

1. Depth/stencil image is created with `VK_IMAGE_LAYOUT_ZERO_INITIALIZED_EXT`
2. Render pass begins, depth is cleared to 0.0
3. A full-screen triangle is drawn with blue color
4. Color attachment is copied to a host-visible buffer
5. Color buffer is compared against expected blue render result

## Test Principles

- **Per-memory-type iteration:** Each test iterates over all compatible memory types, ensuring the zero-initialize feature works across all memory heaps and types
- **Multiple verification paths:** Images can be verified via transfer copy, compute shader, or fragment shader read
- **Format coverage:** Tests cover uncompressed formats (8/16/32-bit, float/int/uint), BC1 compressed format, and all depth/stencil formats
- **Mip level coverage:** Tests verify both the first mip level (single-level images) and the second mip level (two-level images)

## Notes

- RGB8 format is excluded from storage image tests because storage images with 3-channel formats do not exist ([vktMemoryZeroInitializeDeviceMemoryTests.cpp:1338-1342](../../../modules/vulkan/memory/vktMemoryZeroInitializeDeviceMemoryTests.cpp#L1338))
- Transfer read mode is incompatible with compressed formats in this test because block size calculations would be needed ([vktMemoryZeroInitializeDeviceMemoryTests.cpp:582](../../../modules/vulkan/memory/vktMemoryZeroInitializeDeviceMemoryTests.cpp#L582))
- The test uses `tcu::floatThresholdCompare` and `tcu::intThresholdCompare` with zero thresholds for image comparison ([vktMemoryZeroInitializeDeviceMemoryTests.cpp:862-867](../../../modules/vulkan/memory/vktMemoryZeroInitializeDeviceMemoryTests.cpp#L862))
