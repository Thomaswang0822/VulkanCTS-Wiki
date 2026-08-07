# Understanding Brief: `draw.renderpass.ahb`

## One-Sentence Test Purpose

This test checks whether Vulkan can render triangle lists into a color image backed by imported Android Hardware Buffer memory and preserve the expected pixels for each tested array layer.

## Background Knowledge

### Android Hardware Buffer memory import

An Android Hardware Buffer (AHB) is an Android-managed allocation that Vulkan can import as external device memory through `VK_ANDROID_external_memory_android_hardware_buffer`. An AHB-backed image has intrinsic dimensions, format, and usage properties. Vulkan therefore queries the allocation requirements and imports the particular AHB with a dedicated allocation.

Why it matters here:
- The rendered image uses memory allocated by the Android API, not ordinary CTS image allocation.
- The test covers image creation, import, binding, rendering, and transfer readback as one interoperable path.

### Array layers and render-pass attachments

A 2D-array image contains independently addressable array layers. A 2D image view can select one layer. A render pass can use a different attachment in each subpass, allowing this test to render to one selected layer at a time.

Why it matters here:
- Multi-layer cases create one image view and one color attachment per layer.
- Each subpass draws the nine vertices assigned to its layer, then the test copies that layer to its own host-visible result buffer.

## One Concrete Example

In `triangle_list_layers_3`, the test allocates a 256 by 256, three-layer `VK_FORMAT_R8G8B8A8_UNORM` AHB. It creates three 2D views, each selecting one array layer, and a three-subpass render pass. Subpass 0 draws vertices 0 through 8 to layer 0; subpass 1 draws vertices 9 through 17 to layer 1; subpass 2 draws vertices 18 through 26 to layer 2. The host copies each layer to a separate buffer and compares it with a software-rendered image for those same nine vertices.

## End-to-End Test Flow

```text
[host] choose 1, 3, 5, or 8 layers and generate deterministic positions and colors
[host] allocate an AHB suitable for color-attachment use and create an external-memory Vulkan image
[host] query AHB memory properties, import the AHB through a dedicated allocation, and bind it to the image
[host] create one 2D view, color attachment, subpass, and graphics pipeline for each layer
[host] upload the vertex data and record layout transitions, the render pass, and one draw per subpass
[device] rasterize nine triangle-list vertices into the selected layer for each subpass
[host] transition the image for transfer, copy every layer into a host-visible buffer, and wait for completion
[host] generate a software reference image for each layer and fuzzy-compare it with the copied pixels
[host] fail the CTS case if any layer comparison fails
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

| Artifact | How it is produced | Role |
|----------|--------------------|------|
| Vertex GLSL | `AhbTestCase::initShaderSources` emits a GLSL 430 pass-through vertex shader. | Copies position to `gl_Position` and color to the varying. |
| Fragment GLSL | `AhbTestCase::initShaderSources` emits a GLSL 430 pass-through fragment shader. | Writes the interpolated color to the color attachment. |
| Per-layer graphics pipeline | The instance builds one pipeline for each render-pass subpass. | Selects the matching subpass while keeping triangle-list and vertex-input state fixed. |
| Software reference program | `PassthruVertShader` and `PassthruFragShader` form an `rr::Program`. | Rasterizes each layer's nine generated vertices independently of Vulkan. |

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| AHB allocation | yes, through `AndroidHardwareBufferExternalApi` | imported as image memory | backs the color image | indirectly | Exercises Android-owned external memory. |
| External color image | yes | yes, with imported dedicated memory | written as color attachment and read for copy | indirectly | Holds one to eight array layers of results. |
| Per-layer image views and attachments | yes | used by render pass | select the layer written in each subpass | indirectly | Connect each subpass to exactly one layer. |
| Vertex buffer | yes | yes | read by vertex input | no | Stores deterministic positions and colors for all layers. |
| Result buffers | yes | yes | written by image-to-buffer copies | yes | Supply pixels for host comparison. |

## What Is Checked

For every layer, the test clears a 256 by 256 reference image, rasterizes that layer's nine generated vertices with `rr::Renderer`, and compares the reference with the copied Vulkan result through `tcu::fuzzyCompare`. The threshold is `0.053f`. The case passes only when every layer matches. A comparison failure reports `QP_TEST_RESULT_FAIL`.

## Behavior Parameter Identification

> **Behavior parameter:** test case leaf, representing AHB image layer count.
>
> **Candidate values:** `triangle_list`, `triangle_list_layers_3`, `triangle_list_layers_5`, `triangle_list_layers_8`.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `triangle_list` | AHB import or binding, single-layer attachment rendering, image transfer, or image comparison mismatch. |
| `triangle_list_layers_3` | Multi-layer AHB allocation, per-layer view or attachment selection, subpass-to-layer rendering, transfer selection, or image comparison mismatch. |
| `triangle_list_layers_5` | Multi-layer AHB allocation, per-layer view or attachment selection, subpass-to-layer rendering, transfer selection, or image comparison mismatch. |
| `triangle_list_layers_8` | Multi-layer AHB allocation, per-layer view or attachment selection, subpass-to-layer rendering, transfer selection, or image comparison mismatch. |

## Important Variations and Special Cases

- `checkSupport` requires `VK_ANDROID_external_memory_android_hardware_buffer` and rejects a case whose layer count exceeds `maxColorAttachments`.
- The implementation rejects platforms that cannot expose the AHB API or allocate the requested number of layers.
- The test appears only in the non-VulkanSC render-pass tree. The draw dispatcher excludes it from dynamic rendering because it relies on subpasses.
- The color format, extent, topology, vertex count per layer, and comparison threshold stay fixed. Layer count is the behavioral variation.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Registration and case dimensions | [`vktDrawAhbTests.cpp`](../../../modules/vulkan/draw/vktDrawAhbTests.cpp#L628-L652) | Defines the `ahb` family and its four leaves. |
| Support checks and generated shaders | [`vktDrawAhbTests.cpp`](../../../modules/vulkan/draw/vktDrawAhbTests.cpp#L211-L256) | Shows extension, attachment-limit checks, and the two pass-through stages. |
| AHB allocation and imported binding | [`vktDrawAhbTests.cpp`](../../../modules/vulkan/draw/vktDrawAhbTests.cpp#L312-L378) | Creates the AHB, imports it, and binds dedicated memory to the image. |
| Per-layer render-pass setup and draw calls | [`vktDrawAhbTests.cpp`](../../../modules/vulkan/draw/vktDrawAhbTests.cpp#L380-L534) | Builds views, attachments, subpasses, and one draw for every layer. |
| Readback and comparison | [`vktDrawAhbTests.cpp`](../../../modules/vulkan/draw/vktDrawAhbTests.cpp#L536-L625) | Copies layers and defines the pass condition. |
| Dispatcher scope | [`vktDrawTests.cpp`](../../../modules/vulkan/draw/vktDrawTests.cpp#L103-L116) | Places the family in the render-pass registration path. |
| Mustpass evidence | [`draw.txt`](../../../mustpass/main/vk-default/draw.txt#L16956-L16959) | Confirms all four registered leaves. |
| Vulkan AHB image rules | [`memory.adoc`](../../../../vulkan-docs/src/chapters/memory.adoc#L5792-L5808) | Describes intrinsic AHB image properties and dedicated allocation requirements. |

## Questions / Risk Points for User Audit

- Does the explanation distinguish an AHB-backed image from an image using ordinary CTS allocation?
- Is the per-layer relationship among image views, attachments, subpasses, draws, copies, and reference images clear?
- Is it clear that the test checks pixels after Vulkan rendering and transfer, rather than directly mapping the AHB?
- The test validates the four render-pass leaves in `vk-default/draw.txt`; it does not claim dynamic-rendering coverage.

## Conversion Notes for Final Wiki Rewrite

- Distill the AHB import and per-layer attachment concepts into short prerequisite bullets.
- Preserve the behavior parameter conclusion and copy the failure-cause table unchanged.
- Keep shader discussion short because the pass-through stages support the external-memory path rather than test shader logic.
- Use the resource table, ordered runtime flow, exact registration hierarchy, and focused source appendix in the final page.
