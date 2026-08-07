## Overview

**Core question:** Can Vulkan render expected pixels into an image backed by imported Android Hardware Buffer memory for one or several array layers?

- [`vktDrawAhbTests.cpp`](../../../modules/vulkan/draw/vktDrawAhbTests.cpp) implements the `draw.renderpass.ahb` test family.
- Each case imports an Android Hardware Buffer (AHB) as dedicated external memory for a `VK_FORMAT_R8G8B8A8_UNORM` color image, renders triangle lists, copies the result into host-visible buffers, and compares each layer with an `rr::Renderer` reference image.
- The four registered leaves differ only in layer count: one, three, five, or eight. Multi-layer cases use one 2D view, color attachment, subpass, pipeline, draw, and readback copy per layer.
- The family runs only in the non-VulkanSC render-pass path. It is excluded from dynamic rendering because its implementation uses subpasses.

## Background Knowledge

- An Android Hardware Buffer is Android-managed memory that Vulkan can import through `VK_ANDROID_external_memory_android_hardware_buffer`. An AHB-backed image has intrinsic dimensions, format, and usage properties, so its imported memory uses a dedicated allocation.
- A 2D-array image has independently selectable layers. A 2D image view can select one layer, and a render pass can bind separate color attachments in separate subpasses.

## Registration Hierarchy

```text
draw.renderpass.ahb
├── triangle_list
├── triangle_list_layers_3
├── triangle_list_layers_5
└── triangle_list_layers_8
```

[`vktDrawTests.cpp`](../../../modules/vulkan/draw/vktDrawTests.cpp#L103-L116) registers `ahb` in the render-pass tree. [`draw.txt`](../../../mustpass/main/vk-default/draw.txt#L16956-L16959) contains all four leaves.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test case leaf / AHB layer count | `triangle_list` (1), `triangle_list_layers_3` (3), `triangle_list_layers_5` (5), `triangle_list_layers_8` (8) | Controls how many AHB image layers, views, attachments, subpasses, draws, copies, and reference comparisons the case uses. | [`createAhbDrawTests`](../../../modules/vulkan/draw/vktDrawAhbTests.cpp#L628-L643) |
| Vertices | 9 per layer | Each layer receives three triangle-list primitives from a distinct nine-vertex slice of the shared vertex buffer. | [`cmdDraw`](../../../modules/vulkan/draw/vktDrawAhbTests.cpp#L524-L532) |
| Target | 256 by 256, `VK_FORMAT_R8G8B8A8_UNORM` | Fixed single-sample color target used for Vulkan output and software reference images. | [`iterate`](../../../modules/vulkan/draw/vktDrawAhbTests.cpp#L277-L316) |
| Comparison threshold | `0.053f` | Bounds acceptable pixel differences in the per-layer fuzzy comparison. | [`fuzzyCompare`](../../../modules/vulkan/draw/vktDrawAhbTests.cpp#L596-L625) |

## Behavior Parameters

The primary behavioral axis is the test case leaf, which selects the AHB image's layer count.

### triangle_list: one-layer AHB image

This case tests a single imported AHB-backed color attachment. It draws nine vertices as three triangles, copies layer 0 to a result buffer, and compares that image with the software reference.

### triangle_list_layers_3: three-layer AHB image

This case tests three independently selected array layers in one imported AHB. The render pass uses three subpasses; subpass `i` draws vertex slice `i * 9` through `i * 9 + 8` into layer `i`.

### triangle_list_layers_5: five-layer AHB image

This case uses the same per-layer mechanism with five attachments and five subpasses. It increases the attachment, view, subpass, draw, copy, and comparison count without changing shader or rasterization behavior.

### triangle_list_layers_8: eight-layer AHB image

This case uses eight layers and therefore exercises the largest attachment count in this family. `checkSupport` rejects it if `maxColorAttachments` is below eight or the platform cannot allocate the AHB.

## Shader Analysis

The shaders do not introduce a separate behavior axis. [`initShaderSources`](../../../modules/vulkan/draw/vktDrawAhbTests.cpp#L230-L256) generates a GLSL 430 vertex shader that assigns `in_position` to `gl_Position` and forwards `in_color`, plus a fragment shader that writes that color. The reference renderer uses equivalent pass-through vertex and fragment shaders. The test therefore focuses on AHB-backed image setup, layered render-pass routing, transfer readback, and final pixels rather than shader computation.

## Runtime Execution and Result Checking

- The case requires `VK_ANDROID_external_memory_android_hardware_buffer`; it also rejects layer counts above `maxColorAttachments`. [`checkSupport`](../../../modules/vulkan/draw/vktDrawAhbTests.cpp#L217-L228)
- A deterministic random generator creates positions and colors using `SEED ^ m_numLayers ^ m_numVertices`. The implementation allocates one host-visible result buffer for each layer. [`generateDrawData`](../../../modules/vulkan/draw/vktDrawAhbTests.cpp#L263-L275) and [`iterate`](../../../modules/vulkan/draw/vktDrawAhbTests.cpp#L277-L310)
- The host allocates an AHB for color-attachment use, creates an image declaring `VK_EXTERNAL_MEMORY_HANDLE_TYPE_ANDROID_HARDWARE_BUFFER_BIT_ANDROID`, queries AHB properties, imports the AHB with `VkImportAndroidHardwareBufferInfoANDROID`, and binds the image through `VkMemoryDedicatedAllocateInfo`. [`AHB allocation and import`](../../../modules/vulkan/draw/vktDrawAhbTests.cpp#L324-L378)
- For every layer, the case creates a 2D image view selecting that layer, adds a color attachment and a subpass, and creates a pipeline for that subpass. The command buffer transitions all layers to `VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL`, begins the render pass, and issues one nine-vertex draw per subpass. [`per-layer render pass`](../../../modules/vulkan/draw/vktDrawAhbTests.cpp#L380-L534)
- After the render pass, the image transitions to `VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL`. The command buffer copies each layer into its matching result buffer and makes transfer writes visible to host reads. [`readback barriers and copies`](../../../modules/vulkan/draw/vktDrawAhbTests.cpp#L536-L588)
- After submission completes, the test rasterizes the same nine vertices for each layer with `rr::Renderer`, then calls `tcu::fuzzyCompare` with threshold `0.053f`. Any failed layer changes the final result to `QP_TEST_RESULT_FAIL`. [`result check`](../../../modules/vulkan/draw/vktDrawAhbTests.cpp#L592-L625)

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `triangle_list` | AHB import or binding, single-layer attachment rendering, image transfer, or image comparison mismatch. |
| `triangle_list_layers_3` | Multi-layer AHB allocation, per-layer view or attachment selection, subpass-to-layer rendering, transfer selection, or image comparison mismatch. |
| `triangle_list_layers_5` | Multi-layer AHB allocation, per-layer view or attachment selection, subpass-to-layer rendering, transfer selection, or image comparison mismatch. |
| `triangle_list_layers_8` | Multi-layer AHB allocation, per-layer view or attachment selection, subpass-to-layer rendering, transfer selection, or image comparison mismatch. |

### Cause Analysis

#### AHB import or binding

**Possible failure symptoms:** The rendered pixels for the affected case differ from the reference image, or the case cannot run because AHB allocation or required support is unavailable.

**Possible implementation causes:** The test imports the exact AHB allocated for the target image and binds it through a dedicated allocation. The Vulkan specification requires dedicated allocations for images bound to memory imported from an AHB. A failure after the support checks can indicate incorrect handling of that imported AHB memory, its required allocation properties, or its binding to the image. [`AHB image resources`](../../../../vulkan-docs/src/chapters/memory.adoc#L5792-L5808)

#### Per-layer attachment, subpass, or draw routing

**Possible failure symptoms:** One layer differs while another layer passes, or multiple layers show pixels from the wrong nine-vertex slice.

**Possible implementation causes:** The implementation builds one view and attachment for each array layer, selects subpass `i`, and draws with `firstVertex = i * 9`. A mismatch can result from an incorrect array-layer view selection, attachment/subpass association, graphics-pipeline subpass selection, or draw offset. Source-level investigation is needed to separate those mechanisms from the image symptom.

#### Image transfer and host readback

**Possible failure symptoms:** Rendering may be correct internally, but the copied result buffer differs from the reference for one or more layers.

**Possible implementation causes:** The test transitions the image from color-attachment output to transfer source, copies each selected layer, barriers the buffer for host reads, waits for submission, and invalidates mapped memory. Incorrect layout transition, layer selection in `VkBufferImageCopy`, visibility, or host-cache handling can corrupt the observed pixels. [`readback barriers and copies`](../../../modules/vulkan/draw/vktDrawAhbTests.cpp#L536-L599)

#### Image comparison mismatch

**Possible failure symptoms:** `tcu::fuzzyCompare` reports a difference larger than `0.053f` for at least one layer and the CTS case returns `QP_TEST_RESULT_FAIL`.

**Possible implementation causes:** The reference and Vulkan paths receive the same per-layer positions and colors but use separate rasterizers. A discrepancy can arise from earlier import, attachment routing, rendering, or readback behavior. The comparison alone does not identify which stage produced the mismatch.

## Case Pruning

### Requirement-based pruning

- Each case requires the Android external-memory extension, an available AHB API, successful allocation of the requested layer count, and enough `maxColorAttachments` for that count. [`support and allocation checks`](../../../modules/vulkan/draw/vktDrawAhbTests.cpp#L217-L228) and [`AHB allocation`](../../../modules/vulkan/draw/vktDrawAhbTests.cpp#L324-L336)

### Design-based pruning

The parent draw dispatcher registers this family only when the build does not use Vulkan SC and only on the render-pass path, because its per-layer subpass design cannot be translated to dynamic rendering. [`vktDrawTests.cpp`](../../../modules/vulkan/draw/vktDrawTests.cpp#L103-L116)

## Key Takeaways

- The family verifies a complete Android external-memory render path, from AHB allocation and dedicated import to Vulkan rendering, transfer readback, and pixel comparison.
- Layer count is the behavioral variation. Each additional layer receives its own view, attachment, subpass, pipeline selection, nine-vertex draw, copy, and reference comparison.
- A failing comparison proves only that the final pixels differ. The failure mapping separates likely import, layered routing, transfer/readback, and comparison-stage causes for further investigation.

## Source Reference Appendix

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Test registration | [`vktDrawAhbTests.cpp`](../../../modules/vulkan/draw/vktDrawAhbTests.cpp#L628-L652) | Defines `ahb` and the four exact test case leaves. |
| Support and shaders | [`vktDrawAhbTests.cpp`](../../../modules/vulkan/draw/vktDrawAhbTests.cpp#L211-L256) | Defines extension and attachment-limit gates and the pass-through shaders. |
| AHB-backed image creation | [`vktDrawAhbTests.cpp`](../../../modules/vulkan/draw/vktDrawAhbTests.cpp#L312-L378) | Allocates, imports, dedicates, and binds the AHB memory. |
| Layered render pass and draws | [`vktDrawAhbTests.cpp`](../../../modules/vulkan/draw/vktDrawAhbTests.cpp#L380-L534) | Defines per-layer views, attachments, subpasses, pipelines, and draw offsets. |
| Readback and validation | [`vktDrawAhbTests.cpp`](../../../modules/vulkan/draw/vktDrawAhbTests.cpp#L536-L625) | Defines layout transitions, copies, host visibility, reference rendering, and fuzzy comparison. |
| Draw dispatcher | [`vktDrawTests.cpp`](../../../modules/vulkan/draw/vktDrawTests.cpp#L103-L116) | Establishes render-pass-only registration scope. |
| Mustpass evidence | [`draw.txt`](../../../mustpass/main/vk-default/draw.txt#L16956-L16959) | Confirms all four category-qualified paths. |
| Vulkan AHB semantics | [`memory.adoc`](../../../../vulkan-docs/src/chapters/memory.adoc#L5792-L5808) | Documents intrinsic AHB image properties and the dedicated-allocation requirement. |
