## Overview

**Core question:** Can Vulkan use application-allocated host memory as real resource backing without losing compatibility, rendering correctness, or host/device visibility?

- This page covers the three test families implemented and registered by `vktMemoryExternalMemoryHostTests.cpp`: `simple_allocation`, `bind_image_memory_and_render`, and `synchronization`.
- Every family imports an aligned host allocation with `VK_EXTERNAL_MEMORY_HANDLE_TYPE_HOST_ALLOCATION_BIT_EXT`. `simple_allocation` checks the import itself, `bind_image_memory_and_render` uses imported memory as image backing, and `synchronization` passes imported-buffer data between host and device.
- The render family binds imported memory at zero or at one image-alignment unit and checks four color formats. The synchronization family binds a transfer buffer, modifies its imported memory on the host, and lets a timeline semaphore release the device copy.

## Background Knowledge

For the shared concepts memory types, heaps, and resource compatibility, host-visible and non-coherent memory, and memory dependencies, see [Background Knowledge](../../categories/memory.md#background-knowledge) of the `memory` page.

- **Host-pointer import:** `VkImportMemoryHostPointerInfoEXT` attaches an application-owned host allocation to a `VkDeviceMemory` allocation. The pointer and allocation size must meet `minImportedHostPointerAlignment`. `vkGetMemoryHostPointerPropertiesEXT` supplies the memory types available for that pointer, which must also satisfy the bound resource's memory requirements.
- **Imported memory and host mapping:** imported host memory already has an original host address, but Vulkan does not consider it host-mapped device memory until `vkMapMemory` succeeds. Flush and invalidate operations apply to accesses through the mapped pointer; platform synchronization remains the application's responsibility for accesses through the original pointer.
- **Host-to-device ordering:** a host-signaled timeline semaphore can release queued device work. Memory barriers still define which host and transfer accesses participate in the dependency.

## Registration Hierarchy

```text
memory.external_memory_host
├── simple_allocation
├── bind_image_memory_and_render
└── synchronization
```

The source registers all three direct test families and implements their behavior in the same file. The main Vulkan and Vulkan SC mustpass lists contain the resulting 11 test case leaves.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test family | `simple_allocation`, `bind_image_memory_and_render`, `synchronization` | Selects allocation-only, imported-image rendering, or synchronized imported-buffer behavior. | [registration](../../../modules/vulkan/memory/vktMemoryExternalMemoryHostTests.cpp#L1123-L1179) |
| Simple-allocation leaf | `minImportedHostPointerAlignment_x1`, `minImportedHostPointerAlignment_x3` | Supplies constructor multipliers 1 and 3. The current `iterate()` path reallocates either case to one alignment unit before import. | [registration](../../../modules/vulkan/memory/vktMemoryExternalMemoryHostTests.cpp#L1133-L1140), [iteration](../../../modules/vulkan/memory/vktMemoryExternalMemoryHostTests.cpp#L306-L330) |
| Bind offset intermediate node | `with_zero_offset`, `with_non_zero_offset` | Binds the image at byte offset 0 or `imageMemoryRequirements.alignment`; the latter reserves an aligned prefix before the image. | [image allocation and bind](../../../modules/vulkan/memory/vktMemoryExternalMemoryHostTests.cpp#L348-L387) |
| Render format leaf | `r8g8b8a8_unorm`, `r16g16b16a16_unorm`, `r16g16b16a16_sfloat`, `r32g32b32a32_sfloat` | Changes the image, render target, readback interpretation, and required byte count. | [format list](../../../modules/vulkan/memory/vktMemoryExternalMemoryHostTests.cpp#L1142-L1169) |
| Synchronization leaf | `synchronization` | Uses `VK_FORMAT_R8G8B8A8_UNORM` to size and interpret a 10000-pixel transfer buffer. | [synchronization registration](../../../modules/vulkan/memory/vktMemoryExternalMemoryHostTests.cpp#L1173-L1178) |

## Behavior Parameters

The primary behavioral axis is the **test family**. Each value changes the property under test, rather than only changing the resource configuration.

### `simple_allocation`: query and import a host pointer

This family checks the minimum viable import path. It queries the external-host alignment, allocates aligned host memory, asks `vkGetMemoryHostPointerPropertiesEXT` for usable memory types, chooses one reported type, and imports the pointer through `vkAllocateMemory`.

It also checks that `minImportedHostPointerAlignment` is a power of two and no greater than 65536. The current implementation converges both registered multiplier leaves to a final allocation size of one alignment unit before import.

### `bind_image_memory_and_render`: use imported memory as image backing

This family adds resource compatibility and device use. It creates a 100x100 linear image declared for external host memory, intersects the image's `memoryTypeBits` with the host pointer's bits, imports enough host memory for the requested bind offset, and binds the image.

Device commands clear the full image blue, begin a 75-pixel-wide render area cleared red, and draw a green quad over the left 50 columns. Copyback must produce green columns `[0,50)`, red columns `[50,75)`, and blue columns `[75,100)`.

### `synchronization`: hand imported-buffer data from host to device

This family tests a host/device handoff through the same imported allocation. The device first fills an external transfer buffer. After a fence confirms completion, the host maps the imported memory, invalidates it, writes the reference pixels, flushes it, and compares the bytes visible through the mapped pointer with the bytes at the original imported pointer.

A second queue submission waits for timeline semaphore value 1 before copying the external buffer to a normal host-visible result buffer. The host signals that value only after its write and then compares the copied pixels with the reference.

## Shader Analysis

The shaders belong to the render family. They are fixed across all four formats and both bind offsets, so one walkthrough captures the shader-side behavior. The vertex shader is primary because its storage-buffer read turns four host-prepared positions into the quad that defines the green region; the fragment shader only writes a constant color.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.memory.external_memory_host.bind_image_memory_and_render.with_zero_offset.r8g8b8a8_unorm
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `bind_image_memory_and_render` | Executes the only family that uses the generated graphics shaders. |
| `with_zero_offset` | Binds the imported allocation directly at image offset 0; the shader remains identical for the nonzero-offset cases. |
| `r8g8b8a8_unorm` | Uses the smallest registered pixel format; format selection does not change shader source. |

#### Purpose

The shaders draw a constant green quad into an image backed by imported host memory. The vertex stage reads four clip-space positions from a storage buffer, while the fragment stage supplies the green value checked after image copyback.

#### Structural Design

| Stage | Input | Operation | Output |
|-------|-------|-----------|--------|
| Vertex | `pos.p[gl_VertexIndex]` from storage-buffer binding 0 | Select one of four host-prepared positions | `gl_Position` |
| Fragment | Rasterized fragments inside the quad | Emit constant `(0, 1, 0, 1)` | Color attachment location 0 |

#### Shader Code

##### Vertex Shader

```glsl
#version 430

/// Binding 0 is an ordinary storage buffer containing the four clip-space positions.
layout(std430, binding = 0) buffer BufferPos {
    vec4 p[100];
} pos;

/// The pipeline issues four vertices as a triangle fan; each index selects one position.
out gl_PerVertex {
    vec4 gl_Position;
};

void main() {
    gl_Position = pos.p[gl_VertexIndex];
}
```

##### Fragment Shader

```glsl
#version 430

/// Every covered sample receives the green value expected by the host reference image.
layout(location = 0) out vec4 my_FragColor;

void main() {
    my_FragColor = vec4(0, 1, 0, 1);
}
```

#### Additional Info

- The fragment shader stays fixed for every render case. Its constant output matters because the readback comparison distinguishes the drawn green area from the red render-area clear and blue full-image clear.
- The host binds only 16 floats from the 100-element shader array because the four selected `gl_VertexIndex` values access the first four `vec4` positions.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Bind offset | None. Offset changes memory sizing and `vkBindImageMemory`, not shader construction. | [bind logic](../../../modules/vulkan/memory/vktMemoryExternalMemoryHostTests.cpp#L364-L387) |
| Format | None. All render factories use the same `AddPrograms` builder. | [registration](../../../modules/vulkan/memory/vktMemoryExternalMemoryHostTests.cpp#L1142-L1169) |
| Test family | `simple_allocation` and `synchronization` receive programs from the factory machinery but do not create or execute the graphics pipeline. | [program builder and factories](../../../modules/vulkan/memory/vktMemoryExternalMemoryHostTests.cpp#L1004-L1037) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `vert`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 27
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %_ %gl_VertexIndex
               OpSource GLSL 430
               OpName %main "main"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpName %_ ""
               OpName %BufferPos "BufferPos"
               OpMemberName %BufferPos 0 "p"
               OpName %pos "pos"
               OpName %gl_VertexIndex "gl_VertexIndex"
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpDecorate %_arr_v4float_uint_100 ArrayStride 16
               OpDecorate %BufferPos BufferBlock
               OpMemberDecorate %BufferPos 0 Offset 0
               OpDecorate %pos Binding 0
               OpDecorate %pos DescriptorSet 0
               OpDecorate %gl_VertexIndex BuiltIn VertexIndex
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%gl_PerVertex = OpTypeStruct %v4float
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
       %uint = OpTypeInt 32 0
   %uint_100 = OpConstant %uint 100
%_arr_v4float_uint_100 = OpTypeArray %v4float %uint_100
  %BufferPos = OpTypeStruct %_arr_v4float_uint_100
%_ptr_Uniform_BufferPos = OpTypePointer Uniform %BufferPos
        %pos = OpVariable %_ptr_Uniform_BufferPos Uniform
%_ptr_Input_int = OpTypePointer Input %int
%gl_VertexIndex = OpVariable %_ptr_Input_int Input
%_ptr_Uniform_v4float = OpTypePointer Uniform %v4float
%_ptr_Output_v4float = OpTypePointer Output %v4float
       %main = OpFunction %void None %3
          %5 = OpLabel
         %21 = OpLoad %int %gl_VertexIndex
         %23 = OpAccessChain %_ptr_Uniform_v4float %pos %int_0 %21
         %24 = OpLoad %v4float %23
         %26 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %26 %24
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- All cases query `VkPhysicalDeviceExternalMemoryHostPropertiesEXT`. They fail if `minImportedHostPointerAlignment` exceeds 65536 or is not a power of two.
- The host allocates with `deAlignedMalloc` or `deAlignedRealloc`, queries pointer-specific `memoryTypeBits`, and imports through a `VkImportMemoryHostPointerInfoEXT` chained to `VkMemoryAllocateInfo`.
- Render support checks require linear-tiling color-attachment support. They query the exact external image configuration and require the returned properties to include the host-allocation handle and `IMPORTABLE`, without `DEDICATED_ONLY`.
- A render case sizes the host allocation for the image requirements plus its optional bind offset. It creates the external image, ordinary vertex and result buffers, descriptor binding 0, and a triangle-fan pipeline. One command buffer clears, draws, and copies the image. `tcu::floatThresholdCompare` checks every pixel with component threshold `0.01`.
- The synchronization support check performs the equivalent external-buffer property checks and requires `VK_KHR_timeline_semaphore`.
- The synchronization case selects a memory type that is compatible with both the buffer and pointer and also has `VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT`. A first submission fills the imported buffer and a fence closes the device-to-host phase.
- The host maps and invalidates the imported memory before writing the reference pattern, flushes afterward, and runs `deMemCmp` between the original host allocation and the mapped pointer. A host signal advances the timeline semaphore to 1. The waiting submission then applies a host-write-to-transfer-read barrier, copies into the result buffer, and applies a transfer-write-to-host-read barrier.
- A fence protects final result access. The host compares the copied synchronization result against the same three-zone reference with threshold `0.01`.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `simple_allocation` | Invalid external-host alignment reporting, unusable host-pointer memory-type reporting, or host-pointer import failure. |
| `bind_image_memory_and_render` | Incorrect external image properties, imported-memory compatibility or offset binding, or loss/corruption during clear, rendering, and image copyback. |
| `synchronization` | Incorrect host-visible imported-memory aliasing, cache management, host-to-device ordering, or transfer copyback. |

### Cause Analysis

#### Invalid alignment, memory-type reporting, or import

**Possible failure symptoms:** the test reports an alignment above 65536, a non-power-of-two alignment, no selectable bit from `VkMemoryHostPointerPropertiesEXT::memoryTypeBits`, or an error while importing the aligned pointer.

**Possible implementation causes:** the implementation may report an external-host limit inconsistent with the Vulkan limit rules, omit usable memory types for a valid aligned allocation, or reject an import whose pointer, size, handle type, and memory type meet the reported requirements. An allocation failure caused by exhausted host or device resources has the same CTS symptom but requires log and source-level investigation before assigning it to import handling.

#### External image property, binding, or device-use failure

**Possible failure symptoms:** support checking returns incompatible external-memory feature flags, no common pointer/image memory type exists, image binding fails, or copied pixels differ from the green/red/blue reference.

**Possible implementation causes:** external image capability reporting may disagree with image creation or binding behavior. For executed cases, imported allocation offset handling, color-attachment access, layout transitions, rendering, or transfer copyback may corrupt pixels. A mismatch can also come from unrelated graphics-pipeline behavior, so the image log and mismatch location are needed to separate import/binding faults from rendering or copy faults.

#### Imported-memory aliasing, cache management, or ordering failure

**Possible failure symptoms:** `deMemCmp` finds different bytes through the original and mapped pointers, the queued copy completes with stale or incorrect pixels, or final result comparison fails.

**Possible implementation causes:** the mapped range may not alias the imported payload correctly, flush/invalidate handling may fail for the selected host-visible memory type, the host signal and queue wait may not establish the expected execution dependency, or the host-write-to-transfer-read barrier may not make the updated bytes visible to the copy. Transfer or result-buffer visibility faults can produce the same final mismatch; the earlier alias comparison distinguishes some, but not all, of these paths.

## Case Pruning

### Requirement-based pruning

- Every case requires `VK_EXT_external_memory_host`.
- Render cases skip formats without `VK_FORMAT_FEATURE_COLOR_ATTACHMENT_BIT` in `linearTilingFeatures` or without external host-memory support for the exact image configuration.
- Render execution skips when no memory type satisfies both image and pointer `memoryTypeBits`.
- The synchronization family requires `VK_KHR_timeline_semaphore`, valid importable external-buffer properties, and a common memory type with `VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT`.
- On non-SC builds with `VK_KHR_portability_subset`, synchronization also requires the portability `events` feature because the current support check applies that gate.

### Design-based pruning

- The render matrix uses four representative color formats, one fixed 100x100 extent, linear tiling, one sample, one mip level, and one array layer.
- Bind offsets are limited to zero and one `imageMemoryRequirements.alignment` unit. The test does not generate arbitrary aligned offsets.
- `synchronization` fixes the format to `r8g8b8a8_unorm` and binds its buffer at offset zero. Its `TestParams` offset flag is not consumed by the buffer path.
- The two simple-allocation leaves start with different constructor multipliers, but current iteration reallocates both to one alignment unit. Readers should not treat them as distinct final imported sizes.
- In Vulkan SC parent-process reservation discovery, the compatibility helper returns memory type index 0. The subprocess performs the actual selection.

## Key Takeaways

- The three test families form a progression: import an aligned pointer, use it as image backing, then coordinate host and device access to an imported buffer.
- Image cases test both direct and aligned-offset binding across four formats, then validate the full clear/render/copy path by pixel comparison.
- The synchronization case checks two views of the imported payload before it tests the timeline-semaphore handoff and transfer result.
- The fixed shaders define only the green region. Red and blue regions come from render-area and full-image clears, so the final image distinguishes multiple stages of device use.
- See `## Failure Meaning` to separate property/import failures from binding, rendering, aliasing, cache, ordering, and copyback symptoms.

## Source Reference Appendix

| Source | Relevant area | What it establishes |
|--------|---------------|---------------------|
| [vktMemoryExternalMemoryHostTests.cpp](../../../modules/vulkan/memory/vktMemoryExternalMemoryHostTests.cpp#L71-L330) | External properties and base instance | Alignment checks, pointer property query, memory-type search, and import allocation. |
| [vktMemoryExternalMemoryHostTests.cpp](../../../modules/vulkan/memory/vktMemoryExternalMemoryHostTests.cpp#L348-L440) | Render iteration | Image sizing, offset binding, command submission, and image comparison. |
| [vktMemoryExternalMemoryHostTests.cpp](../../../modules/vulkan/memory/vktMemoryExternalMemoryHostTests.cpp#L443-L759) | Render helpers | External image creation, buffers, pipeline, clear/draw/copy commands, and reference pixels. |
| [vktMemoryExternalMemoryHostTests.cpp](../../../modules/vulkan/memory/vktMemoryExternalMemoryHostTests.cpp#L768-L1002) | Synchronization implementation | Fence phases, mapped-memory operations, host signal, barriers, copy, alias check, and result comparison. |
| [vktMemoryExternalMemoryHostTests.cpp](../../../modules/vulkan/memory/vktMemoryExternalMemoryHostTests.cpp#L1004-L1179) | Programs, support, and registration | Fixed shaders, feature gates, exact values, and registered hierarchy. |
| [vktMemoryTests.cpp](../../../modules/vulkan/memory/vktMemoryTests.cpp#L69) | Root registration | Attaches `external_memory_host` below `memory`. |
| [Vulkan mustpass: memory](../../../mustpass/main/vk-default/memory.txt#L915-L925) | Vulkan test leaves | Lists all 11 `dEQP-VK.memory.external_memory_host` cases. |
| [Vulkan SC mustpass: memory](../../../mustpass/main/vksc-default/memory.txt#L58-L68) | Vulkan SC test leaves | Lists the equivalent 11 `dEQP-VKSC` cases. |
| [Vulkan memory chapter](../../../../vulkan-docs/src/chapters/memory.adoc#L1576-L1601) | Import allocation rules | Requires a reported memory type and aligned allocation size. |
| [Vulkan memory chapter](../../../../vulkan-docs/src/chapters/memory.adoc#L2840-L2968) | Host-pointer semantics | Defines payload lifetime, alignment, query results, and non-host-visible caveats. |
| [Vulkan memory chapter](../../../../vulkan-docs/src/chapters/memory.adoc#L5137-L5171) | Mapping and cache operations | Distinguishes original-pointer access from explicit Vulkan mapping. |
| [Vulkan limits chapter](../../../../vulkan-docs/src/chapters/limits.adoc#L1227-L1248) | External-host alignment | Defines `minImportedHostPointerAlignment` as a power-of-two base-address and size alignment. |
| [Vulkan synchronization chapter](../../../../vulkan-docs/src/chapters/synchronization.adoc#L1733-L1760) | Host access | Defines flush/invalidate behavior for noncoherent mapped memory. |
| [Vulkan synchronization chapter](../../../../vulkan-docs/src/chapters/synchronization.adoc#L4760-L4788) | Host semaphore signal | Defines the synchronization scope of `vkSignalSemaphore`. |
