# Device Memory Report Tests

Tests for `VK_EXT_device_memory_report`. Validates that the device memory report callback mechanism correctly reports allocation, free, import, and unimport events for all Vulkan object types that consume device memory.

## Source

- [vktMemoryDeviceMemoryReportTests.cpp](../../../modules/vulkan/memory/vktMemoryDeviceMemoryReportTests.cpp)

## Registration

- **Group name:** `device_memory_report`
- **Registration function:** [`createDeviceMemoryReportTests()`](../../../modules/vulkan/memory/vktMemoryDeviceMemoryReportTests.cpp#L2202)
- **Parent group:** `memory`

## Registration Hierarchy

```text
memory.device_memory_report
├── create_and_destroy_object
├── vk_device_memory
└── external_memory
```

## Test Families

### create_and_destroy_object

Tests that creating and destroying each Vulkan object type produces properly paired `ALLOCATE`/`FREE` (or `IMPORT`/`UNIMPORT`) callback events. Covers 23 object types:

| Object Type | Parameters |
|-------------|-----------|
| `Device` | Default device with memory report enabled |
| `DeviceMemory` | 1024 bytes, type index 0 |
| `Buffer` | Uniform buffer (1KB, 16MB), storage buffer (1KB, 16MB) |
| `BufferView` | Uniform texel buffer view, storage texel buffer view (R8G8B8A8_UNORM) |
| `Image` | 1D (256×1, 4 layers), 2D (64×64, 12 layers), 3D (64×64×4) |
| `ImageView` | 1D, 1D array, 2D, 2D array, cube, cube array, 3D views |
| `Semaphore` | Default |
| `Event` | Default |
| `Fence` | Unsignaled, signaled (`VK_FENCE_CREATE_SIGNALED_BIT`) |
| `QueryPool` | Occlusion query, 1 entry |
| `ShaderModule` | Compute shader |
| `PipelineCache` | Default |
| `Sampler` | Default (nearest, clamp-to-edge, no anisotropy) |
| `DescriptorSetLayout` | Empty, single UBO binding |
| `PipelineLayout` | Empty, single descriptor set layout |
| `RenderPass` | Default (R8G8B8A8_UNORM color + D16_UNORM depth) |
| `GraphicsPipeline` | Default (vertex + fragment, triangle list) |
| `ComputePipeline` | Default (compute shader with 2 storage buffers) |
| `DescriptorPool` | Default, with `FREE_DESCRIPTOR_SET` flag |
| `DescriptorSet` | Single UBO layout |
| `Framebuffer` | Default (256×256, color + depth attachments) |
| `CommandPool` | Default, transient |
| `CommandBuffer` | Primary, secondary |

Each test creates the object within a scoped block, then validates that all callback records are properly paired ([vktMemoryDeviceMemoryReportTests.cpp:1739-1765](../../../modules/vulkan/memory/vktMemoryDeviceMemoryReportTests.cpp#L1739)).

### vk_device_memory

Direct test of `vkAllocateMemory()` / `vkFreeMemory()` using the raw device interface (not through the object template system). Verifies specific callback fields:
- `objectType` must be `VK_OBJECT_TYPE_DEVICE_MEMORY`
- `memoryObjectId` must be non-zero and consistent across allocate/free
- `size` must be at least the requested allocation size
- `heapIndex` must match the physical device memory properties ([vktMemoryDeviceMemoryReportTests.cpp:1767-1849](../../../modules/vulkan/memory/vktMemoryDeviceMemoryReportTests.cpp#L1767))

### external_memory

Tests import and unimport callbacks for various external memory handle types. The test:
1. Creates an exportable buffer and allocates exportable memory
2. Exports the memory to a native handle
3. Creates two more buffers and imports the same memory into each (dedicated import)
4. Destroys the imported memory objects (triggering `UNIMPORT`)
5. Destroys the original memory (triggering `FREE`)

Validates that `ALLOCATE`, `IMPORT` (×2), `UNIMPORT` (×2), and `FREE` events are all received with correct `memoryObjectId` consistency ([vktMemoryDeviceMemoryReportTests.cpp:2020-2176](../../../modules/vulkan/memory/vktMemoryDeviceMemoryReportTests.cpp#L2020)).

## Parameter Dimensions

### External memory handle types

| Handle Type | Required Extensions |
|-------------|-------------------|
| `VK_EXTERNAL_MEMORY_HANDLE_TYPE_OPAQUE_FD_BIT` | `VK_KHR_external_memory_fd` |
| `VK_EXTERNAL_MEMORY_HANDLE_TYPE_OPAQUE_WIN32_BIT` | `VK_KHR_external_memory_win32` |
| `VK_EXTERNAL_MEMORY_HANDLE_TYPE_OPAQUE_WIN32_KMT_BIT` | `VK_KHR_external_memory_win32` |
| `VK_EXTERNAL_MEMORY_HANDLE_TYPE_ANDROID_HARDWARE_BUFFER_BIT_ANDROID` | `VK_ANDROID_external_memory_android_hardware_buffer`, `VK_EXT_queue_family_foreign`, `VK_KHR_sampler_ycbcr_conversion` |
| `VK_EXTERNAL_MEMORY_HANDLE_TYPE_DMA_BUF_BIT_EXT` | `VK_KHR_external_memory_fd`, `VK_EXT_external_memory_dma_buf` |

## Support / Feature Requirements

| Extension/Feature | Required by |
|-------------------|-------------|
| `VK_EXT_device_memory_report` | All tests ([vktMemoryDeviceMemoryReportTests.cpp:1569-1596](../../../modules/vulkan/memory/vktMemoryDeviceMemoryReportTests.cpp#L1569)) |
| `VK_KHR_external_memory_capabilities` | external_memory tests ([vktMemoryDeviceMemoryReportTests.cpp:1865](../../../modules/vulkan/memory/vktMemoryDeviceMemoryReportTests.cpp#L1865)) |
| `VK_KHR_dedicated_allocation` | external_memory tests ([vktMemoryDeviceMemoryReportTests.cpp:1866](../../../modules/vulkan/memory/vktMemoryDeviceMemoryReportTests.cpp#L1866)) |
| `VK_KHR_get_memory_requirements2` | external_memory tests ([vktMemoryDeviceMemoryReportTests.cpp:1867](../../../modules/vulkan/memory/vktMemoryDeviceMemoryReportTests.cpp#L1867)) |
| `VK_IMAGE_VIEW_TYPE_CUBE_ARRAY` support | cube array image view test ([vktMemoryDeviceMemoryReportTests.cpp:1607-1608](../../../modules/vulkan/memory/vktMemoryDeviceMemoryReportTests.cpp#L1607)) |

## Verification Methods

### Callback pairing validation ([vktMemoryDeviceMemoryReportTests.cpp:1663-1721](../../../modules/vulkan/memory/vktMemoryDeviceMemoryReportTests.cpp#L1663))

The `validateCallbackRecords()` function checks:
1. `heapIndex` must be within valid range for `ALLOCATE` and `ALLOCATION_FAILED` events
2. `ALLOCATE`/`IMPORT` events are tracked by `(memoryObjectId, objectHandle)` pairs
3. `FREE`/`UNIMPORT` events must have matching prior `ALLOCATE`/`IMPORT` events
4. All tracked pairs must be consumed by the end (no leaked allocations)

### Per-record field validation

For `vk_device_memory` and `external_memory` tests, individual record fields are validated:
- `objectType` must be `VK_OBJECT_TYPE_DEVICE_MEMORY`
- `memoryObjectId` must be non-zero and consistent across the lifecycle of a single memory object
- `size` must be ≥ the requested allocation size
- `heapIndex` must match the expected heap from `VkPhysicalDeviceMemoryProperties`
- Callback marker ordering: the test sets markers before each API call and verifies the marker matches the record ([vktMemoryDeviceMemoryReportTests.cpp:1822](../../../modules/vulkan/memory/vktMemoryDeviceMemoryReportTests.cpp#L1822))

### External memory identity validation

For imported memory, the test verifies that `memoryObjectId` is the **same** across the original allocation and all imports, confirming that the implementation correctly identifies them as the same underlying memory object ([vktMemoryDeviceMemoryReportTests.cpp:2113-2116](../../../modules/vulkan/memory/vktMemoryDeviceMemoryReportTests.cpp#L2113)).

## Test Principles

- **Callback completeness:** Every allocation/import must have a corresponding free/unimport
- **Identity tracking:** The same underlying memory object should have the same `memoryObjectId` regardless of how many times it is imported
- **Field accuracy:** Reported size, heap index, and object type must match expected values
- **Ordering:** Callbacks must occur in the correct temporal order relative to API calls
- **Custom device isolation:** Most object tests create a custom device with memory report enabled to avoid interference from the test framework's own allocations ([vktMemoryDeviceMemoryReportTests.cpp:1754](../../../modules/vulkan/memory/vktMemoryDeviceMemoryReportTests.cpp#L1754))

## Notes

- The `Device` test case is the only one that uses the parent environment directly; all other objects create a cloned environment with a custom device ([vktMemoryDeviceMemoryReportTests.cpp:1747-1757](../../../modules/vulkan/memory/vktMemoryDeviceMemoryReportTests.cpp#L1747))
- Shader module tests require program compilation — they use `addFunctionCaseWithPrograms` ([vktMemoryDeviceMemoryReportTests.cpp:1623-1629](../../../modules/vulkan/memory/vktMemoryDeviceMemoryReportTests.cpp#L1623))
- The test framework uses a template-based object creation system (`Dependency<Object>`, `CaseDescription<Object>`) to generically test all object types with the same validation logic ([vktMemoryDeviceMemoryReportTests.cpp:152-163](../../../modules/vulkan/memory/vktMemoryDeviceMemoryReportTests.cpp#L152))
- `ALLOCATION_FAILED` events are logged but do not cause test failure — they are expected when memory is exhausted ([vktMemoryDeviceMemoryReportTests.cpp:1685-1689](../../../modules/vulkan/memory/vktMemoryDeviceMemoryReportTests.cpp#L1685))
