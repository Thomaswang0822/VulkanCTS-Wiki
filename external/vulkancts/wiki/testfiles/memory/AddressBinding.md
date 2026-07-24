## Overview

**Core question:** Does `VK_EXT_device_address_binding_report` report a matching bind and unbind for each tested Vulkan object?

- This page covers the implementation in [`vktMemoryAddressBindingTests.cpp`](../../../modules/vulkan/memory/vktMemoryAddressBindingTests.cpp), registered under the `memory` test category as `address_binding_report`.
- The `create_and_destroy_object` test family creates one object at a time, records device-address binding callback data, destroys the object and its dependencies, then checks the records.
- The matrix covers 41 test case leaves for 23 Vulkan object types. The test compares the reported base address, size, and object handle; it does not test shader output or GPU work.
- A failure means that the callback stream did not preserve the expected bind/unbind pairing for the selected object construction path, or that the test setup could not complete.

## Background Knowledge

- `VK_EXT_device_address_binding_report` exposes implementation changes to GPU-accessible virtual address ranges through the debug utils callback mechanism. A callback carries the address range, its size, the binding event type, and the associated Vulkan object.
- A `BIND` event reports a newly bound range and an `UNBIND` event reports a range being released. Vulkan requires these messages when the enabled reporting feature covers address-space changes, including both explicit memory binding and bindings created as part of allocation or object creation. See [`VkDeviceAddressBindingCallbackDataEXT`](../../../../vulkan-docs/src/chapters/debugging.adoc#VkDeviceAddressBindingCallbackDataEXT).
- Callback object handles can describe internal objects before an application receives a valid handle. The test records the handle supplied in the callback and uses it only as an identifier for pairing, not as an input to another Vulkan command.

## Registration Hierarchy

```text
memory.address_binding_report
└── create_and_destroy_object
```

[`createObjectTestsGroup()`](../../../modules/vulkan/memory/vktMemoryAddressBindingTests.cpp#L1632-L1660) builds `create_and_destroy_object`. [`createAddressBindingReportTests()`](../../../modules/vulkan/memory/vktMemoryAddressBindingTests.cpp#L1831-L1985) assembles its 23 object-specific case arrays.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Object type | `device`, `device_memory_small`, `buffer_*`, `buffer_view_*`, `image_*`, `image_view_*`, `semaphore`, `event`, `fence_*`, `query_pool`, `shader_module`, `pipeline_cache`, `sampler`, `descriptor_set_layout_*`, `pipeline_layout_*`, `render_pass`, `graphics_pipeline`, `compute_pipeline`, `descriptor_pool_*`, `descriptor_set`, `framebuffer`, `command_pool_*`, `command_buffer_*` | Selects which Vulkan object construction and destruction path emits the callback records. | [`CaseDescriptions`](../../../modules/vulkan/memory/vktMemoryAddressBindingTests.cpp#L1558-L1583), [`addCases()`](../../../modules/vulkan/memory/vktMemoryAddressBindingTests.cpp#L1610-L1658) |
| Buffer size and usage | `1024`, `16 MB`; uniform or storage usage | Exercises small and large buffer address ranges and two buffer usage classes. | [`s_bufferCases`](../../../modules/vulkan/memory/vktMemoryAddressBindingTests.cpp#L1876-L1893) |
| Buffer-view backing range | 8192-byte buffer, `offset = 0`, `range = 4096`; uniform or storage texel usage; `VK_FORMAT_R8G8B8A8_UNORM` | Tests a view whose address-bearing dependency is a bound buffer. | [`s_bufferViewCases`](../../../modules/vulkan/memory/vktMemoryAddressBindingTests.cpp#L1894-L1900) |
| Image shape | 1D `256x1x1` with 4 layers; 2D `64x64x1` with 12 layers; 3D `64x64x4` with 1 layer | Varies image dimensionality and array extent before binding image memory. | [`img1D`, `img2D`, `img3D`](../../../modules/vulkan/memory/vktMemoryAddressBindingTests.cpp#L1835-L1848) |
| Image-view shape | 1D, 1D array, 2D, 2D array, cube, cube array, 3D | Covers view subresource ranges, including six-face and two-cube ranges. | [`s_imageViewCases`](../../../modules/vulkan/memory/vktMemoryAddressBindingTests.cpp#L1907-L1911) |
| Object flags and layout | Signaled or unsignaled fence; empty or single-binding descriptor/pipeline layout; free-descriptor-set pool; transient command pool; primary or secondary command buffer | Checks whether common creation flags and dependency choices change callback pairing. | [`s_fenceCases`](../../../modules/vulkan/memory/vktMemoryAddressBindingTests.cpp#L1918-L1919), [`s_descriptorSetLayoutCases`](../../../modules/vulkan/memory/vktMemoryAddressBindingTests.cpp#L1927-L1932), [`s_descriptorPoolCases`](../../../modules/vulkan/memory/vktMemoryAddressBindingTests.cpp#L1938-L1949), [`s_commandBufferCases`](../../../modules/vulkan/memory/vktMemoryAddressBindingTests.cpp#L1950-L1954) |

## Behavior Parameters

The primary behavioral axis is the **object type**. Each value selects a different Vulkan object creation path. Size, usage, view shape, and flags are secondary variations within that path.

### `Device`, `DeviceMemory`, `Buffer`, and `BufferView`

`Device` checks the custom device creation path with the extension and feature enabled. `DeviceMemory` checks allocation of a 1024-byte block from memory type index 0. `Buffer` checks uniform and storage buffers at 1024 bytes and 16 MB. `BufferView` creates an 8192-byte bound buffer and a 4096-byte `VK_FORMAT_R8G8B8A8_UNORM` view. The buffer-view case therefore checks both the view object and its memory-backed buffer dependencies.

### `Image` and `ImageView`

`Image` covers 1D, 2D, and 3D images with the registered extents and sampled or color-attachment usage. `ImageView` covers ordinary, array, cube, cube-array, and 3D views. Image-view cases first create and bind their backing image and memory, then create the view, so the recorder sees a dependency chain rather than only the final view object.

### `Semaphore`, `Event`, `Fence`, and `QueryPool`

These cases cover synchronization objects and an occlusion query pool with one entry. The fence has both default and `VK_FENCE_CREATE_SIGNALED_BIT` variants. The query pool uses `VK_QUERY_TYPE_OCCLUSION` with no pipeline statistics.

### `ShaderModule`, `PipelineCache`, and `Sampler`

`ShaderModule` creates one compute shader module from the generated `comp` program. `PipelineCache` uses an empty initial cache. `Sampler` uses the default nearest-filter, clamp-to-edge configuration. The shader module is created for object-lifetime reporting; the test does not dispatch it.

### `DescriptorSetLayout`, `PipelineLayout`, and `DescriptorSet`

Descriptor-set layouts are either empty or contain one uniform-buffer binding at set binding 0 for the vertex stage. Pipeline layouts are empty or contain one descriptor-set layout. The descriptor-set case allocates one set from a freeable descriptor pool using the single-UBO layout.

### `RenderPass`, `GraphicsPipeline`, and `ComputePipeline`

The render pass uses an `R8G8B8A8_UNORM` color attachment and a `D16_UNORM` depth attachment. The graphics pipeline depends on vertex and fragment shader modules, a pipeline layout, render pass, and empty pipeline cache. The compute pipeline depends on a compute shader module, a layout with two storage-buffer bindings, and an empty pipeline cache. Neither pipeline is submitted for execution.

### `DescriptorPool`, `Framebuffer`, `CommandPool`, and `CommandBuffer`

Descriptor pools have a default and `VK_DESCRIPTOR_POOL_CREATE_FREE_DESCRIPTOR_SET_BIT` variant, each allowing four sets and three uniform-buffer descriptors. The framebuffer creates color and depth image-view dependencies plus a render pass. Command pools use default or `VK_COMMAND_POOL_CREATE_TRANSIENT_BIT` flags. Command buffers allocate one primary or secondary buffer from a default command pool.

## Shader Analysis

Shader code participates only as an object-construction dependency for `shader_module`, `graphics_pipeline`, and `compute_pipeline`. No shader executes, produces a result, or controls the callback validation. The test therefore has no representative shader walkthrough and no SPIR-V analysis.

## Runtime Execution and Result Checking

- Each test first calls [`checkSupport()`](../../../modules/vulkan/memory/vktMemoryAddressBindingTests.cpp#L1585-L1608) to confirm that the implementation advertises `VK_EXT_device_address_binding_report` and supports the `reportAddressBinding` feature. The function skips unsupported implementations.
- `createDestroyObjectTest()` creates a custom instance with the required debug-utils instance extensions, selects a graphics-capable queue family, and installs a debug messenger listening for `VK_DEBUG_UTILS_MESSAGE_TYPE_DEVICE_ADDRESS_BINDING_BIT_EXT` at info severity ([`createDestroyObjectTest()`](../../../modules/vulkan/memory/vktMemoryAddressBindingTests.cpp#L1763-L1797)).
- The test creates a new device with `VK_EXT_device_address_binding_report` and `reportAddressBinding = VK_TRUE`. The selected object and its dependencies are created inside a scope. Their RAII wrappers destroy them before the device leaves its scope ([`createDeviceWithAdressBindingReport()`](../../../modules/vulkan/memory/vktMemoryAddressBindingTests.cpp#L194-L232), [`createDestroyObjectTest()`](../../../modules/vulkan/memory/vktMemoryAddressBindingTests.cpp#L1799-L1817)).
- The callback recorder accepts only the device-address-binding message type. It stores `baseAddress`, `size`, `bindingType`, and `pObjects[0].objectHandle` from each callback ([`BindingCallbackRecorder`](../../../modules/vulkan/memory/vktMemoryAddressBindingTests.cpp#L92-L145)).
- After destroying the debug messenger, `validateCallbackRecords()` scans the recorded sequence. Every `BIND` must have a later equal `UNBIND`; every `UNBIND` must have an earlier equal `BIND`. Equality uses the base address, size, and object handle. A missing pair returns failure with `Invalid address binding report callback`; otherwise the test returns `Ok` ([`validateCallbackRecords()`](../../../modules/vulkan/memory/vktMemoryAddressBindingTests.cpp#L1663-L1733)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `Device`, `DeviceMemory` | Device or allocation address-space reporting did not produce a matching pair. |
| `Buffer`, `BufferView` | Buffer memory binding, view dependency creation, or object destruction produced a missing or mismatched pair. |
| `Image`, `ImageView` | Image memory binding, view dependency creation, or destruction produced a missing or mismatched pair. |
| `Semaphore`, `Event`, `Fence`, `QueryPool` | The selected synchronization or query object path produced a missing or mismatched pair. |
| `ShaderModule`, `PipelineCache`, `Sampler` | The selected module, cache, or sampler path produced a missing or mismatched pair. |
| `DescriptorSetLayout`, `PipelineLayout`, `DescriptorSet` | Descriptor object creation, allocation, dependency destruction, or reported address identity did not pair correctly. |
| `RenderPass`, `GraphicsPipeline`, `ComputePipeline` | Render-pass or pipeline dependency construction/destruction produced a missing or mismatched pair. |
| `DescriptorPool`, `Framebuffer`, `CommandPool`, `CommandBuffer` | Pool, framebuffer, or command-resource construction/destruction produced a missing or mismatched pair. |

All rows share the same recorder and validator. A failure in any row can also indicate that the implementation did not emit the required debug message, attached `VkDeviceAddressBindingCallbackDataEXT` incorrectly, associated the wrong object identity, or reported a different address range on unbind.

### Cause Analysis

#### Missing or unmatched address-binding callback

**Possible failure symptoms:** The validator reports a lonely `BIND` or `UNBIND` record, or it cannot find an equal record with the same base address, size, and object handle. The case returns `Invalid address binding report callback`.

**Possible implementation causes:** The specification requires an info-severity device-address-binding debug message with the associated object in `pObjects` and `VkDeviceAddressBindingCallbackDataEXT` in the callback data chain when the enabled feature observes a binding change ([`debugging.adoc`](../../../../vulkan-docs/src/chapters/debugging.adoc#VkDeviceAddressBindingCallbackDataEXT)). A missing message, an incorrect binding type, or a changed address range would produce the observed symptom. The exact implementation cause requires investigation in the failing object path.

#### Wrong object identity or address-range fields

**Possible failure symptoms:** Both event types appear, but the pair does not compare equal because the callback supplies a different object handle, base address, or size for the unbind record. The validator logs the fields for a matching pair, but returns failure for a mismatch.

**Possible implementation causes:** The callback data defines `baseAddress` as the start of the GPU-accessible virtual range, `size` as its byte size, and `pObjects` as the associated Vulkan object. The implementation may have associated a dependency rather than the selected object, or may have reported inconsistent range metadata. Source-level investigation is needed to distinguish those cases.

#### Lifetime or dependency destruction ordering

**Possible failure symptoms:** Object cases with dependencies, such as `BufferView`, `ImageView`, pipelines, descriptor sets, framebuffers, and command buffers, leave a bind without a later matching unbind or emit an unbind before the recorded bind.

**Possible implementation causes:** The test creates dependencies before the selected object and destroys the scoped RAII objects before destroying the device. Vulkan object lifetime rules require dependent objects to be destroyed before the objects they reference. The source establishes that order; a failure points to reporting behavior during one of those creation or destruction paths, but the failing implementation location needs investigation.

#### Unsupported prerequisite or setup failure

**Possible failure symptoms:** The case is reported as not supported because the extension or `reportAddressBinding` feature is absent, or object creation fails before callback validation runs.

**Possible implementation causes:** The test intentionally skips implementations that do not expose `VK_EXT_device_address_binding_report` or its feature. A setup error can instead reflect an invalid combination of object parameters, an unavailable memory type, a missing shader program binary, or an unrelated device-creation failure. The source does not classify those failures as callback-pairing failures, so they require separate investigation.

## Case Pruning

### Requirement-based pruning

- `checkSupport()` skips the test when `VK_EXT_device_address_binding_report` is not available or `reportAddressBinding` is false ([`checkSupport()`](../../../modules/vulkan/memory/vktMemoryAddressBindingTests.cpp#L1585-L1608)).
- The image-view cube-array case requires `VK_IMAGE_VIEW_TYPE_CUBE_ARRAY` support and valid cube-compatible image parameters. Standard Vulkan object validity rules also constrain formats, usage flags, memory requirements, and descriptor dependencies.
- The source selects a graphics-capable queue family for the custom device. The test does not create a test case for every queue family.

### Design-based pruning

- The matrix uses one representative configuration for most object types. It varies a parameter only when the variation exercises a distinct creation flag, resource shape, usage class, or dependency path.
- Shader source exists for shader-module and pipeline construction, but the test does not submit graphics or compute work. There are no execution-result cases.
- The test uses one scoped object lifetime per leaf so the callback stream can be checked without interleaving unrelated test objects.

## Key Takeaways

- The primary behavior choice is the Vulkan object construction path, not shader execution.
- The validator checks callback identity: `BIND` and `UNBIND` must agree on object handle, base address, and size.
- Memory-backed objects and dependent objects exercise callback reporting across both explicit memory binding and nested resource lifetimes.
- The page covers 41 mustpass leaves under `memory.address_binding_report.create_and_destroy_object`. The support check skips unsupported devices before object creation.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Feature and extension support check | [`checkSupport()`](../../../modules/vulkan/memory/vktMemoryAddressBindingTests.cpp#L1585-L1608) | Establishes the required extension and `reportAddressBinding` feature. |
| Callback recorder | [`BindingCallbackRecorder`](../../../modules/vulkan/memory/vktMemoryAddressBindingTests.cpp#L92-L145) | Extracts callback message type, address, size, binding type, and object handle. |
| Custom device setup | [`createDeviceWithAdressBindingReport()`](../../../modules/vulkan/memory/vktMemoryAddressBindingTests.cpp#L194-L232) | Enables the extension and feature for each isolated test device. |
| Object creation and lifetime | [`createDestroyObjectTest()`](../../../modules/vulkan/memory/vktMemoryAddressBindingTests.cpp#L1763-L1827) | Installs the messenger, creates the object in a scope, destroys dependencies, and invokes validation. |
| Pairing validator | [`validateCallbackRecords()`](../../../modules/vulkan/memory/vktMemoryAddressBindingTests.cpp#L1663-L1733) | Defines the pass/fail contract for BIND and UNBIND records. |
| Test registration and matrix | [`createAddressBindingReportTests()`](../../../modules/vulkan/memory/vktMemoryAddressBindingTests.cpp#L1831-L1985) | Defines the hierarchy, object case names, parameter values, and 23 object types. |
| Root memory registration | [`createChildren()`](../../../modules/vulkan/memory/vktMemoryTests.cpp#L52-L77) | Adds `address_binding_report` below the `memory` test category. |
| Vulkan callback semantics | [`VkDeviceAddressBindingCallbackDataEXT`](../../../../vulkan-docs/src/chapters/debugging.adoc#VkDeviceAddressBindingCallbackDataEXT) | Defines required callback fields, event types, object association, and reporting conditions. |
| Feature semantics | [`reportAddressBinding`](../../../../vulkan-docs/src/chapters/features.adoc#features-reportAddressBinding) | Defines the feature that controls address-binding reporting support. |
