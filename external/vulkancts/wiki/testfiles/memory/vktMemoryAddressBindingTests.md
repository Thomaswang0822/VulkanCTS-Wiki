# Address Binding Report Tests

Tests for `VK_EXT_device_address_binding_report`. Validates that the debug utils callback mechanism correctly reports device address binding and unbinding events for all Vulkan object types that consume device address space.

## Source

- [vktMemoryAddressBindingTests.cpp](../../../modules/vulkan/memory/vktMemoryAddressBindingTests.cpp)

## Registration

- **Group name:** `address_binding_report`
- **Registration function:** [`createAddressBindingReportTests()`](../../../modules/vulkan/memory/vktMemoryAddressBindingTests.cpp#L1831)
- **Parent group:** `memory`

## Registration Hierarchy

```text
memory.address_binding_report
└── create_and_destroy_object
```

The `create_and_destroy_object` subgroup contains 37 leaf test cases covering 23 Vulkan object types. Each leaf test is named after the object type and its configuration variant (e.g., `device`, `buffer_uniform_small`, `image_view_cube_arr`). The full list is detailed in [Test Families](#test-families).

Evidence:
- `address_binding_report` group created at [`createAddressBindingReportTests()`](../../../modules/vulkan/memory/vktMemoryAddressBindingTests.cpp#L1831)
- `create_and_destroy_object` subgroup added at [line 1982](../../../modules/vulkan/memory/vktMemoryAddressBindingTests.cpp#L1982)

## Test Families

### create_and_destroy_object — Create/destroy callback pairing per object type

Tests that creating and destroying each Vulkan object type produces properly paired `BIND`/`UNBIND` callback events. Covers 23 object types:

| Object Type | Parameters |
|-------------|-----------|
| `Device` | Default device with address binding report enabled |
| `DeviceMemory` | 1024 bytes, type index 0 |
| `Buffer` | Uniform buffer (1KB, 16MB), storage buffer (1KB, 16MB) |
| `BufferView` | Uniform texel buffer view, storage texel buffer view (R8G8B8A8_UNORM, 4KB range) |
| `Image` | 1D (256×1, 4 layers), 2D (64×64, 12 layers), 3D (64×64×4) |
| `ImageView` | 1D, 1D array, 2D, 2D array, cube, cube array, 3D views |
| `Semaphore` | Default |
| `Event` | Default |
| `Fence` | Unsignaled, signaled (`VK_FENCE_CREATE_SIGNALED_BIT`) |
| `QueryPool` | Occlusion query, 1 entry |
| `ShaderModule` | Compute shader |
| `PipelineCache` | Default |
| `Sampler` | Default |
| `DescriptorSetLayout` | Empty, single UBO binding |
| `PipelineLayout` | Empty, single descriptor set layout |
| `RenderPass` | Default |
| `GraphicsPipeline` | Default |
| `ComputePipeline` | Default |
| `DescriptorPool` | Default, with `FREE_DESCRIPTOR_SET` flag |
| `DescriptorSet` | Single UBO layout |
| `Framebuffer` | Default |
| `CommandPool` | Default, transient |
| `CommandBuffer` | Primary, secondary |

Each test creates the object within a scoped block, then validates that all callback records are properly paired ([vktMemoryAddressBindingTests.cpp:1956-1983](../../../modules/vulkan/memory/vktMemoryAddressBindingTests.cpp#L1956)).

## Parameter Dimensions

### Object-specific parameters

| Object | Size/Config | Usage/Flags |
|--------|------------|-------------|
| Buffer (small) | 1024 bytes | `VK_BUFFER_USAGE_UNIFORM_BUFFER_BIT` |
| Buffer (large) | 16 MB | `VK_BUFFER_USAGE_UNIFORM_BUFFER_BIT` |
| Buffer (storage small) | 1024 bytes | `VK_BUFFER_USAGE_STORAGE_BUFFER_BIT` |
| Buffer (storage large) | 16 MB | `VK_BUFFER_USAGE_STORAGE_BUFFER_BIT` |
| BufferView (uniform) | 8192 bytes buffer, offset 0, range 4096 | `VK_BUFFER_USAGE_UNIFORM_TEXEL_BUFFER_BIT`, R8G8B8A8_UNORM |
| BufferView (storage) | 8192 bytes buffer, offset 0, range 4096 | `VK_BUFFER_USAGE_STORAGE_TEXEL_BUFFER_BIT`, R8G8B8A8_UNORM |
| Image 1D | 256×1×1, 1 mip, 4 layers | `VK_IMAGE_USAGE_SAMPLED_BIT` |
| Image 2D | 64×64×1, 1 mip, 12 layers | `VK_IMAGE_USAGE_SAMPLED_BIT \| VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT` |
| Image 3D | 64×64×4, 1 mip, 1 layer | `VK_IMAGE_USAGE_SAMPLED_BIT` |
| ImageView cube | 64×64, cube compatible, 6 faces | `VK_IMAGE_USAGE_SAMPLED_BIT \| VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT` |
| ImageView cube array | 64×64, cube compatible, 12 faces (2 cubes) | `VK_IMAGE_USAGE_SAMPLED_BIT \| VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT` |

## Support Requirements

| Extension/Feature | Required by |
|-------------------|-------------|
| `VK_EXT_device_address_binding_report` | All tests ([vktMemoryAddressBindingTests.cpp:200](../../../modules/vulkan/memory/vktMemoryAddressBindingTests.cpp#L200)) |
| `VK_EXT_device_address_binding_report` feature | Device created with `VkPhysicalDeviceAddressBindingReportFeaturesEXT::deviceAddressBindingReport = VK_TRUE` ([vktMemoryAddressBindingTests.cpp:203-204](../../../modules/vulkan/memory/vktMemoryAddressBindingTests.cpp#L203)) |
| `VK_IMAGE_VIEW_TYPE_CUBE_ARRAY` support | cube array image view test |

## Verification Methods

### Callback recorder ([vktMemoryAddressBindingTests.cpp:92-146](../../../modules/vulkan/memory/vktMemoryAddressBindingTests.cpp#L92))

The `BindingCallbackRecorder` class:
1. Registers as a `VK_DEBUG_UTILS_MESSAGE_TYPE_DEVICE_ADDRESS_BINDING_BIT_EXT` callback via `vkCreateDebugUtilsMessengerEXT`
2. Captures `VkDeviceAddressBindingCallbackDataEXT` records containing:
   - `baseAddress` — the base device address of the binding
   - `size` — the size of the address range
   - `bindingType` — `VK_DEVICE_ADDRESS_BINDING_TYPE_BIND_EXT` or `VK_DEVICE_ADDRESS_BINDING_TYPE_UNBIND_EXT`
   - `objectHandle` — the Vulkan object handle

### Callback pairing validation ([vktMemoryAddressBindingTests.cpp:1650-1730](../../../modules/vulkan/memory/vktMemoryAddressBindingTests.cpp#L1650))

The `validateCallbackRecords()` function checks:
1. Each `BIND` event is tracked by `(objectHandle, bindingAddress)` pairs
2. `UNBIND` events must have matching prior `BIND` events for the same object and address
3. All tracked pairs must be consumed by the end (no leaked bindings)
4. The total number of BIND events must equal the total number of UNBIND events

## Test Principles

- **Callback completeness:** Every address binding must have a corresponding unbinding
- **Object lifecycle:** Bindings occur when objects are created; unbindings occur when objects are destroyed
- **Custom device isolation:** All object tests create a custom device with address binding report enabled to avoid interference from the test framework's own allocations ([vktMemoryAddressBindingTests.cpp:1800-1811](../../../modules/vulkan/memory/vktMemoryAddressBindingTests.cpp#L1800))
- **Scoped lifetime:** Objects are created within a scoped block `{ ... }` to ensure deterministic destruction before validation ([vktMemoryAddressBindingTests.cpp:1813-1816](../../../modules/vulkan/memory/vktMemoryAddressBindingTests.cpp#L1813))

## Notes

- The test uses a template-based object creation system (`Dependency<Object>`, `NamedParameters<Object>`) to generically test all object types with the same validation logic ([vktMemoryAddressBindingTests.cpp:181-192](../../../modules/vulkan/memory/vktMemoryAddressBindingTests.cpp#L181))
- The `Device` test case creates a custom device with the extension enabled; all other objects clone the environment and create their own custom device ([vktMemoryAddressBindingTests.cpp:1793-1811](../../../modules/vulkan/memory/vktMemoryAddressBindingTests.cpp#L1793))
- The debug messenger is destroyed after all object tests complete ([vktMemoryAddressBindingTests.cpp:1819](../../../modules/vulkan/memory/vktMemoryAddressBindingTests.cpp#L1819))
- Only one test group exists (`create_and_destroy_object`); there are no direct address manipulation tests or external address tests
