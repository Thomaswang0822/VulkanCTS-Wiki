# Understanding Brief: External Memory Host Tests

## One-Sentence Test Purpose

This test checks whether a Vulkan implementation can import an aligned host allocation, bind it to buffers or images, use it in device work, and preserve data through the required host/device synchronization.

## Background Knowledge

### Importing a host allocation as Vulkan device memory

`VK_EXT_external_memory_host` lets an application pass an existing host pointer through `VkImportMemoryHostPointerInfoEXT` while allocating a `VkDeviceMemory` object. The pointer and allocation size must satisfy `minImportedHostPointerAlignment`, and `vkGetMemoryHostPointerPropertiesEXT` reports the memory types under which that pointer may be imported. A resource can use the imported memory only when its own `memoryTypeBits` intersect that reported set.

Why it matters here:
- The imported host allocation remains application-owned and must stay valid for the lifetime of the Vulkan memory object.
- Binding an image or buffer adds the resource's memory requirements to the pointer-import requirements.

### Host access, cache management, and timeline semaphore ordering

Imported host memory is inherently present in host address space, but Vulkan treats accesses through the original pointer differently from accesses through a pointer returned by `vkMapMemory`. The synchronization test maps the imported `VkDeviceMemory`, invalidates before host reading or writing, flushes after writing, and uses a host-signaled timeline semaphore to release a queued device copy. The semaphore wait orders the copy after the host signal; the recorded buffer barrier changes the relevant access scope from host writes to transfer reads.

## One Concrete Example

The `dEQP-VK.memory.external_memory_host.synchronization.synchronization` test case uses one imported allocation as the backing memory for a 10000-pixel transfer buffer:

1. The device fills the buffer with `0xFFFFFFFF`, and a fence lets the host wait for that work.
2. The host maps the imported `VkDeviceMemory`, invalidates the range, writes the same three-zone pixel pattern used by the render tests, flushes the range, and confirms that the original imported pointer and mapped pointer expose identical bytes.
3. A second queue submission waits for timeline value 1 before copying the buffer into a normal host-visible result buffer.
4. The host signals value 1, waits for the copy fence, and compares the copied pixels with the expected pattern at a per-component threshold of `0.01`.

## End-to-End Test Flow

```text
1. simple_allocation
[host] query minImportedHostPointerAlignment and allocate aligned host memory
[host] query memoryTypeBits for the pointer
[host] import the pointer with a compatible memory type
[host] pass if import succeeds; fail if alignment/property checks or type selection fail

2. bind_image_memory_and_render
[host] query external-image support for one format and linear tiling
[host] create an external 100x100 image and choose offset zero or one image-alignment unit
[host] resize the aligned allocation, intersect image and pointer memoryTypeBits, import, and bind
[host] create a render pass, fixed shaders, vertex storage buffer, and readback buffer
[device] clear the whole image blue, clear a 75-pixel-wide render area red, then draw green over its left 50 pixels
[device] copy the image into the readback buffer
[host] compare all pixels with the green/red/blue reference image

3. synchronization
[host] create an external transfer buffer and import host-visible memory for it
[device] fill the buffer, then signal completion through a fence
[host] map and invalidate the memory, write the reference pattern, flush, and compare both host aliases
[host] signal timeline semaphore value 1
[device] after waiting for value 1, copy the imported buffer into the readback buffer
[host] wait for completion and compare the copied pixels with the reference
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

`AddPrograms::init()` supplies fixed GLSL 4.30 vertex and fragment shaders to every case factory, although only the render family executes them. The vertex shader reads four positions from a storage buffer through `gl_VertexIndex`; the fragment shader emits green. The host configures a triangle-fan pipeline and draws four vertices so the green area covers the left half of the 75-pixel render area.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Aligned host allocation | yes | through imported `VkDeviceMemory` | yes, after resource binding | yes | This is the external payload under test. |
| Imported `VkDeviceMemory` | yes | yes | yes | mapped only in `synchronization` | It gives Vulkan access to the host allocation. |
| Linear color image | yes | yes, to imported memory at zero or nonzero offset | clear, render, and copy source | through result buffer | It tests image binding and rendering on imported memory. |
| Vertex storage buffer | yes | yes, ordinary host-visible allocation | read by vertex shader | no | It supplies the four draw positions. |
| External transfer data buffer | yes | yes, to imported host-visible memory | filled and copied | through result buffer | It carries the synchronization test's host/device data handoff. |
| Result buffer | yes | yes, ordinary host-visible allocation | copy destination | yes | It exposes image or buffer contents to the host comparison. |
| Timeline semaphore and fences | yes | synchronization objects, not memory resources | gate queue work and report completion | host waits/signals | They establish the synchronization test's execution order. |

## What Is Checked

- Every case checks that `minImportedHostPointerAlignment` is a power of two and no greater than 65536 bytes.
- Support checks require host-allocation external properties to include the handle type and `IMPORTABLE`, and to exclude `DEDICATED_ONLY`.
- `simple_allocation` passes when the pointer property query supplies a usable memory type and `vkAllocateMemory` successfully imports the pointer.
- Each render case compares a 100x100 readback image against green columns `[0,50)`, red columns `[50,75)`, and blue columns `[75,100)`, with `0.01` component tolerance.
- `synchronization` first requires byte-for-byte equality between the original host pointer and the `vkMapMemory` pointer after the host update. It then applies the same `0.01` image comparison to the copied data.

## Behavior Parameter Identification

> **Behavior parameter:** test family
>
> **Candidate values:** `simple_allocation`, `bind_image_memory_and_render`, `synchronization`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `simple_allocation` | Invalid external-host alignment reporting, unusable host-pointer memory-type reporting, or host-pointer import failure. |
| `bind_image_memory_and_render` | Incorrect external image properties, imported-memory compatibility or offset binding, or loss/corruption during clear, rendering, and image copyback. |
| `synchronization` | Incorrect host-visible imported-memory aliasing, cache management, host-to-device ordering, or transfer copyback. |

## Important Variations and Special Cases

- `simple_allocation` registers allocation multipliers 1 and 3. Its `iterate()` path reallocates to exactly one alignment unit before import, so the two leaves exercise the same final import size in the current source.
- Render cases cross four exact formats with `with_zero_offset` and `with_non_zero_offset`. A nonzero case binds at `imageMemoryRequirements.alignment` and allocates enough room for that prefix plus the image requirements.
- All render images use linear tiling. Support checking rejects formats without linear-tiling color-attachment support or external host-memory image support.
- `synchronization` fixes the format to `VK_FORMAT_R8G8B8A8_UNORM`, uses a nonzero `TestParams` offset value that does not affect its buffer binding, and requires `VK_KHR_timeline_semaphore`.
- The Vulkan SC parent process returns memory type index 0 during reservation discovery; the subprocess performs the real compatibility search.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| External property rules | [checkExternalMemoryProperties](../../../modules/vulkan/memory/vktMemoryExternalMemoryHostTests.cpp#L71-L84) | Defines the compatibility, dedicated-only, and importable checks. |
| Pointer alignment, properties, and import | [base instance](../../../modules/vulkan/memory/vktMemoryExternalMemoryHostTests.cpp#L176-L330) | Implements aligned allocation, memory-type selection, and `VkImportMemoryHostPointerInfoEXT`. |
| Image bind and comparison | [render iterate](../../../modules/vulkan/memory/vktMemoryExternalMemoryHostTests.cpp#L348-L440) | Shows offset sizing, compatible memory selection, device work, and final comparison. |
| Render resources and commands | [render helpers](../../../modules/vulkan/memory/vktMemoryExternalMemoryHostTests.cpp#L443-L759) | Defines the image, buffers, pipeline, clear/draw sequence, and reference image. |
| Host/device handoff | [synchronization iterate](../../../modules/vulkan/memory/vktMemoryExternalMemoryHostTests.cpp#L768-L905) | Defines fence waits, mapped-memory operations, host signal, copy, and checks. |
| Buffer barriers and copy | [synchronization helpers](../../../modules/vulkan/memory/vktMemoryExternalMemoryHostTests.cpp#L908-L1002) | Defines host-write-to-transfer-read and transfer-write-to-host-read barriers. |
| Fixed shaders | [AddPrograms](../../../modules/vulkan/memory/vktMemoryExternalMemoryHostTests.cpp#L1004-L1037) | Supplies the render shaders. |
| Support and registration | [support and registration](../../../modules/vulkan/memory/vktMemoryExternalMemoryHostTests.cpp#L1045-L1179) | Defines feature gates, formats, hierarchy, and leaves. |
| Host pointer import semantics | [Vulkan memory chapter](../../../../vulkan-docs/src/chapters/memory.adoc#L2840-L2968) | Grounds lifetime, alignment, import, and memory-type claims. |
| Imported-memory mapping caveat | [Vulkan memory chapter](../../../../vulkan-docs/src/chapters/memory.adoc#L5137-L5171) | Distinguishes original-pointer accesses from mapped-pointer accesses. |
| Host access and semaphore ordering | [Vulkan synchronization chapter](../../../../vulkan-docs/src/chapters/synchronization.adoc#L1733-L1760) and [host signal semantics](../../../../vulkan-docs/src/chapters/synchronization.adoc#L4760-L4788) | Grounds flush/invalidate and host-signaled timeline behavior. |

## Questions / Risk Points for User Audit

- The behavior axis is the test family because each family tests a different stage of using host-imported memory; no unresolved evidence contradicts this choice.
- The render shader walkthrough should use `dEQP-VK.memory.external_memory_host.bind_image_memory_and_render.with_zero_offset.r8g8b8a8_unorm`; shader code is fixed across formats and offsets.
- The `simple_allocation` multiplier distinction is retained as an observed current-source behavior rather than overstated as distinct final allocation coverage.
- No unresolved source, registration, mustpass, shader-selection, or validation risk remains before the final rewrite.

## Conversion Notes for Final Wiki Rewrite

- Distill the two background topics into short prerequisite bullets.
- Carry the test-family behavior axis into `## Behavior Parameters`.
- Copy the `### Failure Cause Mapping` table unchanged.
- Put the fixed render shaders in one representative walkthrough and generate the primary vertex shader's SPIR-V at baseline `spirv1.0`.
- Keep detailed source navigation in the final appendix and preserve the current-source caveat about the allocation multipliers in the parameter or pruning discussion.
