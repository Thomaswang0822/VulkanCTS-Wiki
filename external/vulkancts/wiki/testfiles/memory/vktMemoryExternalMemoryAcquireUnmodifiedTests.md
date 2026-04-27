# External Memory Acquire Unmodified Tests

Tests for `VK_EXT_external_memory_acquire_unmodified`. Verifies that when acquiring ownership of an image from a foreign queue with `acquireUnmodifiedMemory = VK_TRUE`, the driver correctly preserves unmodified regions of the image during partial updates.

## Source

- [vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp](../../../modules/vulkan/memory/vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp)

## Registration

- **Group name:** `external_memory_acquire_unmodified`
- **Registration function:** [`createExternalMemoryAcquireUnmodifiedTests()`](../../../modules/vulkan/memory/vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp:872)
- **Parent group:** `memory`

## Test Hierarchy

```
external_memory_acquire_unmodified
├── dma_buf
│   ├── r8g8b8a8_unorm
│   ├── b8g8r8a8_unorm
│   ├── r16g16b16a16_unorm
│   ├── r16g16b16a16_sfloat
│   └── r32g32b32a32_sfloat
└── android_hardware_buffer
    ├── r8g8b8a8_unorm
    ├── b8g8r8a8_unorm
    ├── r16g16b16a16_unorm
    ├── r16g16b16a16_sfloat
    └── r32g32b32a32_sfloat
```

## Test Families

### dma_buf

Tests `VK_EXTERNAL_MEMORY_HANDLE_TYPE_DMA_BUF_BIT_EXT` external memory with DRM format modifiers. For each format, the test queries all compatible DRM format modifiers and tests each one individually ([vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp:352-369](../../../modules/vulkan/memory/vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp:352)).

### android_hardware_buffer

Tests `VK_EXTERNAL_MEMORY_HANDLE_TYPE_ANDROID_HARDWARE_BUFFER_BIT_ANDROID` external memory using Android Hardware Buffer allocation ([vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp:347-350](../../../modules/vulkan/memory/vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp:347)).

## Parameter Dimensions

| Parameter | Values |
|-----------|--------|
| `externalMemoryType` | `VK_EXTERNAL_MEMORY_HANDLE_TYPE_DMA_BUF_BIT_EXT`, `VK_EXTERNAL_MEMORY_HANDLE_TYPE_ANDROID_HARDWARE_BUFFER_BIT_ANDROID` |
| `format` | `VK_FORMAT_R8G8B8A8_UNORM`, `VK_FORMAT_B8G8R8A8_UNORM`, `VK_FORMAT_R16G16B16A16_UNORM`, `VK_FORMAT_R16G16B16A16_SFLOAT`, `VK_FORMAT_R32G32B32A32_SFLOAT` |
| DRM format modifier | All compatible modifiers per format (dma_buf only) |

## Support Requirements

| Extension | Required for |
|-----------|-------------|
| `VK_EXT_external_memory_acquire_unmodified` | All tests ([vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp:200](../../../modules/vulkan/memory/vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp:200)) |
| `VK_EXT_external_memory_dma_buf` | dma_buf tests ([vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp:205](../../../modules/vulkan/memory/vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp:205)) |
| `VK_EXT_image_drm_format_modifier` | dma_buf tests ([vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp:206](../../../modules/vulkan/memory/vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp:206)) |
| `VK_ANDROID_external_memory_android_hardware_buffer` | android_hardware_buffer tests ([vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp:209](../../../modules/vulkan/memory/vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp:209)) |

## Verification Method

Each test performs the following sequence:

1. **Fill src1 buffer** with a color gradient
2. **Copy to image** — copies the gradient from src1 buffer to the entire external image
3. **Release ownership** — releases the image to `VK_QUEUE_FAMILY_FOREIGN_EXT` ([vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp:452-465](../../../modules/vulkan/memory/vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp:452))
4. **Fill src2 buffer** — copies src1 content, then overwrites a central subregion (1/4 to 3/4 of width/height) with a different gradient
5. **Acquire ownership** — acquires from foreign queue with `VkExternalMemoryAcquireUnmodifiedEXT::acquireUnmodifiedMemory = VK_TRUE` ([vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp:496-512](../../../modules/vulkan/memory/vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp:496))
6. **Partial copy** — copies only the updated subregion from src2 to the image
7. **Read back** — copies the full image to a result buffer
8. **Compare** — verifies the result buffer matches the full src2 buffer content (both the original gradient in the outer region and the new gradient in the inner region)

Comparison uses `tcu::floatThresholdCompare` for float formats and `tcu::intThresholdCompare` for UNORM formats, with zero tolerance ([vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp:591-617](../../../modules/vulkan/memory/vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp:591)).

## Test Principles

The test validates that `acquireUnmodifiedMemory = VK_TRUE` correctly signals to the driver that the image content has not been modified by external consumers since the last release. This allows the driver to skip re-reading unmodified memory regions. The partial update pattern (copying only a subregion) specifically exercises this behavior — if the driver incorrectly assumes the entire image needs to be re-read, the test would still pass; if the driver incorrectly assumes unmodified regions are invalid, the outer gradient region would contain garbage and the comparison would fail.

## Notes

- The test creates images with `VK_EXTERNAL_MEMORY_IMAGE_CREATE_INFO::handleTypes` set to the external memory type, but does **not** actually import/export external memory. For dma_buf, the image is created with Vulkan as the memory allocator ([vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp:759-767](../../../modules/vulkan/memory/vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp:759)).
- A TODO in the source notes that testing with GBM as the actual dma_buf allocator would better test the full graphics stack ([vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp:767](../../../modules/vulkan/memory/vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp:767)).
- Image dimensions are fixed at 512x512 ([vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp:69](../../../modules/vulkan/memory/vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp:69)).
- Only handle types supporting `VK_QUEUE_FAMILY_FOREIGN_EXT` are tested; `VK_QUEUE_FAMILY_EXTERNAL` is excluded due to spec restrictions ([vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp:21-29](../../../modules/vulkan/memory/vktMemoryExternalMemoryAcquireUnmodifiedTests.cpp:21)).
