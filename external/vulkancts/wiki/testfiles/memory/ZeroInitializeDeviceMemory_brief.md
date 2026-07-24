# Understanding Brief: `memory.zero_initialize_device_memory`

## One-Sentence Test Purpose

This test checks whether allocations made with `VK_MEMORY_ALLOCATE_ZERO_INITIALIZE_BIT_EXT` expose zero-initialized contents through buffer, transfer, compute, fragment, and depth/stencil read paths.

## Background Knowledge

### Zero-initialized device memory

`VK_EXT_zero_initialize_device_memory` adds a memory-allocation flag that requests zeroed contents for the allocation. The test still has to bind the allocation to a buffer or image and observe the contents through a legal access path.

Why it matters here:

- The allocation flag is attached through `VkMemoryAllocateFlagsInfo`.
- The test checks each compatible memory type that advertises the required zero-initialization capability, excluding protected and unsupported AMD device-coherent types.

### `VK_IMAGE_LAYOUT_ZERO_INITIALIZED_EXT`

An image created with `VK_IMAGE_LAYOUT_ZERO_INITIALIZED_EXT` starts in the extension-defined zero-initialized layout. The test transitions the complete image subresource range to a transfer or shader-readable layout before reading it. The Vulkan synchronization rules require the old layout to be included in the barrier and require all image subresources to be covered for this transition. [Image layout transition validity](../../../../vulkan-docs/src/chapters/commonvalidity/image_layout_transition_common.adoc#L170-L180)

## One Concrete Example

The representative case `dEQP-VK.memory.zero_initialize_device_memory.image_transition.r8_unorm_sampled_shader_comp_4x4_first_mip` creates a 4x4 `R8_UNORM` image with one mip level and sampled usage. The test allocates zero-initialized memory, binds it, reads the image in a compute shader, writes the sampled values to a host-visible storage buffer, and compares the result with the expected zero texture.

## End-to-End Test Flow

```text
[host] choose the registered buffer or image parameters
[host] check VK_EXT_zero_initialize_device_memory and resource support
[host] create the resource and query compatible memory types
[host] allocate with VK_MEMORY_ALLOCATE_ZERO_INITIALIZE_BIT_EXT and bind the allocation
[host] transition an image from VK_IMAGE_LAYOUT_ZERO_INITIALIZED_EXT when the case reads an image
[device] copy the buffer/image data or read image texels through compute/fragment work
[host] wait for completion, invalidate the host-visible readback allocation, and compare against zero data
[host] report pass or identify the memory type whose observation failed
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

`image_transition` generates a compute shader for `comp` cases, and a vertex/fragment pair for `frag` cases. Transfer cases do not generate shaders. The representative compute shader reads the image at each pixel coordinate and writes the result to a storage-buffer array.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Tested `VkBuffer` or `VkImage` | yes | yes | read by the selected path | indirectly | Carries the allocation whose initial contents are tested. |
| Zero-initialized `VkDeviceMemory` | yes | bound to tested resource | supplies tested contents | no | Receives the allocation flag under test. |
| Host-visible readback buffer | yes | yes | written by transfer or shader output | yes | Gives the host a stable comparison target. |
| Image descriptor and storage buffer descriptor | yes, shader paths | yes | shader reads image and writes output | no | Connects the sampled/storage image to the validation buffer. |

## What Is Checked

- `clear_buffer` compares every byte in the host-visible tested allocation or copied readback buffer with zero.
- Transfer image cases copy the selected mip level to a host-visible buffer and compare it with a zero reference.
- Compute and fragment image cases compare shader output with zero-valued color components. Missing channels use the source reference rule, including an alpha value of one when the format has no alpha channel.
- Depth/stencil cases render after the zero-initialized transition and compare the resulting color attachment with the expected blue triangle image.
- A failure in any tested memory type marks the case as failed; unsupported resource or memory combinations are reported as not supported.

## Behavior Parameter Identification

> **Behavior parameter:** test family
>
> **Candidate values:** `clear_buffer`, `image_transition`

Within `image_transition`, the read path (`xfer`, `comp`, `frag`, or depth/stencil rendering) is the secondary behavioral axis.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `clear_buffer` | The zero-initialize allocation flag, buffer binding, memory-type selection, copy path, or host readback exposes nonzero contents. |
| `image_transition` | The zero-initialized image contents, initial-layout transition, image read path, descriptor/resource access, or readback comparison is incorrect. |
| `image_transition.comp` | Compute image access or storage-buffer result production does not preserve the expected zero values. |
| `image_transition.frag` | Fragment image access or rasterization/readback result production does not preserve the expected zero values. |
| `image_transition.xfer` | The image-to-buffer transfer path or its layout transition exposes unexpected contents. |
| `image_transition.depth_stencil` | The depth/stencil transition or render-pass path produces an unexpected validation image. |

## Important Variations and Special Cases

- Buffer cases use four sizes, eight buffer usages, and both host-visible and non-host-visible allocation paths.
- Color image cases vary format, usage, read stage, extent, and first versus second mip level. Transfer cases exclude compressed formats because the source would need block-size handling.
- RGB formats are excluded from storage-image cases because three-channel storage images are not available in the tested interface.
- Depth/stencil cases use the separate render-pass path and the formats listed by `formats::depthAndStencilFormats`.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Zero-initialize allocation | [`allocateZeroInitMemory`](../../../modules/vulkan/memory/vktMemoryZeroInitializeDeviceMemoryTests.cpp#L113-L133) | Adds `VK_MEMORY_ALLOCATE_ZERO_INITIALIZE_BIT_EXT` to the allocation chain. |
| Buffer validation | [`clearBufferAllocation`](../../../modules/vulkan/memory/vktMemoryZeroInitializeDeviceMemoryTests.cpp#L136-L221) | Iterates memory types, copies non-host-visible data, and compares bytes. |
| Image shader generation | [`ImageTransitionCase::initPrograms`](../../../modules/vulkan/memory/vktMemoryZeroInitializeDeviceMemoryTests.cpp#L445-L528) | Generates compute, vertex, and fragment programs for image reads. |
| Image execution and comparison | [`ImageTransitionTest::iterate`](../../../modules/vulkan/memory/vktMemoryZeroInitializeDeviceMemoryTests.cpp#L530-L884) | Performs the layout transition, access path, readback, and comparison. |
| Registration | [`createClearedAllocationControlTests`](../../../modules/vulkan/memory/vktMemoryZeroInitializeDeviceMemoryTests.cpp#L1252-L1395) | Defines both families and their registered dimensions. |
| Vulkan feature semantics | [`features.adoc`](../../../../vulkan-docs/src/chapters/features.adoc#L6380-L6386) | Defines support for user-requested zero-initialized allocations. |
| Vulkan allocation flag validity | [`memory.adoc`](../../../../vulkan-docs/src/chapters/memory.adoc#L4659-L4664) | Defines a restriction on the zero-initialize flag for imported memory. |

## Questions / Risk Points for User Audit

- Is the distinction between zero initialization and the later image layout transition clear?
- Does the page separate resource support skips from failures after a supported memory type runs?
- Is the compute walkthrough sufficient without duplicating the fragment and transfer variants?

## Conversion Notes for Final Wiki Rewrite

- Use `clear_buffer` and `image_transition` as the primary behavior values.
- Preserve the Failure Cause Mapping table unchanged.
- Use the compute `R8_UNORM`, sampled, 4x4, first-mip case as the representative shader walkthrough.
- Keep depth/stencil rendering as a separate behavior explanation, not a second shader walkthrough unless later evidence requires it.
