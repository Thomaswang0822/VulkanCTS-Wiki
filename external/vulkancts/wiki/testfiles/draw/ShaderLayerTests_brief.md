# Understanding Brief: ShaderLayerTests

## One-Sentence Test Purpose

This test checks whether vertex and tessellation-evaluation shader writes to `gl_Layer` select the intended framebuffer-array layer for rendered primitives, including render-pass, dynamic-rendering, and secondary-command-buffer paths.

## Background Knowledge

### `gl_Layer` selects an array layer

A layered framebuffer has several 2D slices addressed by one array image view. The `Layer` shader built-in supplies the slice used by rasterization for a primitive. This is distinct from a fragment shader choosing a color: the layer selection happens while the primitive is routed to the layered color attachment. The Vulkan feature `shaderOutputLayer` governs whether the relevant shader stages may export the `Layer` built-in; this CTS family also requires `VK_EXT_shader_viewport_index_layer` and multi-viewport support.

### The shader stage changes how layer selection is derived

The vertex path assigns a layer from `gl_VertexIndex`, so each six-vertex rectangle is routed to one layer. The tessellation path assigns a layer from `gl_PrimitiveID` in the tessellation-evaluation shader after a three-vertex patch is processed. Both paths preserve a color per rectangle, allowing the host to compare each layer independently.

## One Concrete Example

For `vertex_shader_3`, the host creates three rectangles and emits six vertices per rectangle. The conceptual vertex-shader portion is:

```glsl
// Conceptual excerpt reconstructed from initVertexTestPrograms.
gl_Layer = gl_VertexIndex / 6;
gl_Position = in_position;
out_color = in_color;
```

The first six vertices therefore target layer 0, the next six layer 1, and the final six layer 2. The fragment shader only forwards the interpolated color. A faithful result has each rectangle in its assigned layer and the untouched pixels in the clear color.

## End-to-End Test Flow

```text
[host] choose shader family and numLayers
[host] generate a grid of per-layer rectangles, colors, and matching vertices
[host] generate GLSL programs and select the Vulkan 1.2/SPIR-V 1.5 variants when supported
[host] create a 256x256 R8G8B8A8_UNORM array image, 2D-array view, vertex buffer, and graphics pipeline
[host] record either a render pass or dynamic-rendering commands; secondary modes record draw commands in a secondary command buffer
[device] execute the vertex or tessellation pipeline and route primitives using the shader Layer output
[device] render the color attachment and copy every array layer into a host-visible buffer
[host] compare each layer with a generated reference image using a per-channel threshold of 0.02
[host] pass only when every layer comparison succeeds
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- Vertex-family programs contain a vertex shader that computes `gl_Layer = gl_VertexIndex / 6`, plus a pass-through fragment shader.
- Tessellation-family programs contain a pass-through vertex shader, a three-vertex tessellation-control shader with all tessellation levels set to `1.0`, a tessellation-evaluation shader that computes `gl_Layer = gl_PrimitiveID / 2`, and the same pass-through fragment shader.
- For Vulkan 1.2-capable contexts, the source is also compiled with the `vert_1_2` and `tese_1_2` program names and SPIR-V 1.5 build options; older contexts use `vert` and `tese`.
- The generated vertex data contains six vertices per layer for the vertex path and the corresponding patch data for the tessellation path.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|---|---|---|---|---|---|
| 256x256 layered color image | yes | color attachment | written by fragment output | copied indirectly | One array layer is the independent validation unit. |
| 2D-array image view | yes | framebuffer/rendering attachment | used for layered rendering | no | Exposes `numLayers` slices to the rendering operation. |
| Host-visible vertex buffer | yes | vertex input | read by vertex processing | no | Supplies per-layer rectangle geometry and colors. |
| Host-visible color readback buffer | yes | transfer destination | written by image-to-buffer copy | yes | Holds one 2D result image per layer for comparisons. |

## What Is Checked

- The clear color is gray (`0.5, 0.5, 0.5, 1.0`), and each generated rectangle has a deterministic position and color.
- The host partitions the readback buffer into `numLayers` 256x256 images.
- Each result image is compared with `generateReferenceImage` using `tcu::floatThresholdCompare` and `Vec4(0.02f)`.
- Any incorrect layer routing, missing/extra primitive coverage, wrong color, or other image mismatch fails the test with `Rendered image is not correct`.

## Behavior Parameter Identification

> **Behavior parameter:** shader family
>
> **Candidate values:** `vertex_shader`, `tessellation_shader`

The `numLayers` dimension changes the size of the layered rendering problem and is covered as a matrix dimension; the shader family changes where and how the Layer built-in is produced and is therefore the primary behavioral axis.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `vertex_shader` | Incorrect Layer output handling in the vertex path; incorrect per-vertex routing or associated vertex/color processing; layered attachment or image-copy behavior. |
| `tessellation_shader` | Incorrect Layer output handling in the tessellation-evaluation path; patch/primitive processing or tessellation pipeline behavior; layered attachment or image-copy behavior. |

## Important Variations and Special Cases

- `numLayers` is registered as `1, 2, 3, 4, 5, 6, 7, 8, 256`. The last value exercises the required minimum `maxFramebufferLayers` limit.
- Render-pass execution and dynamic rendering share the same image/reference model. Dynamic-rendering cases additionally require `VK_KHR_dynamic_rendering`.
- Dynamic-rendering secondary-command-buffer modes skip every odd index in the layer-count array, leaving `1, 3, 5, 7, 256` registered values for those modes. Nested secondary modes are not reached for this family because the draw dispatcher excludes all non-basic families when `nestedSecondaryCmdBuffer` is set.
- The tessellation family requires the core `tessellationShader` feature. Both families require `multiViewport`, `VK_EXT_shader_viewport_index_layer`, at least 256 framebuffer layers, and at least 16 viewports.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Shader-layer test factory and exact leaves | [createShaderLayerTests](../../../modules/vulkan/draw/vktDrawShaderLayerTests.cpp#L1015-L1049) | Registers the `shader_layer` family, both shader-family prefixes, and layer-count values. |
| Vertex shader generation | [initVertexTestPrograms](../../../modules/vulkan/draw/vktDrawShaderLayerTests.cpp#L349-L391) | Defines the `gl_VertexIndex`-based Layer assignment and pass-through fragment shader. |
| Tessellation shader generation | [initTessellationTestPrograms](../../../modules/vulkan/draw/vktDrawShaderLayerTests.cpp#L393-L479) | Defines patch processing and the `gl_PrimitiveID`-based Layer assignment. |
| Requirements | [checkRequirements](../../../modules/vulkan/draw/vktDrawShaderLayerTests.cpp#L863-L881) | Shows required feature, extension, and device-limit checks. |
| Rendering and copyback | [Renderer::draw](../../../modules/vulkan/draw/vktDrawShaderLayerTests.cpp#L674-L752) | Covers render-pass, dynamic-rendering, secondary recording, submission, and copyback. |
| Host image validation | [testVertexShader](../../../modules/vulkan/draw/vktDrawShaderLayerTests.cpp#L883-L946), [testTessellationShader](../../../modules/vulkan/draw/vktDrawShaderLayerTests.cpp#L948-L1012) | Shows reference generation, per-layer partitioning, threshold comparison, and failure condition. |
| Draw-suite registration | [createChildren](../../../modules/vulkan/draw/vktDrawTests.cpp#L70-L120) | Places `shader_layer` beneath the supported draw roots and excludes nested-secondary registration. |
| Layer-output feature semantics | [shader output layer feature](../../../../vulkan-docs/src/chapters/features.adoc#L941-L948) | Grounds the requirement for exporting the `Layer` built-in. |

## Questions / Risk Points for User Audit

- Is `shader family` the intended primary behavioral axis, with `numLayers` treated as the matrix dimension?
- Should the final page include a full generated shader walkthrough and SPIR-V subsection, or is this source-grounded summary sufficient for the batch's current artifact contract?
- Should the distinction between the `vert`/`tese` and `_1_2` program variants be expanded in the final page?

## Conversion Notes for Final Wiki Rewrite

- Keep `gl_Layer` and the two stage-specific formulas as the central explanation; move the conceptual excerpt into a concise shader walkthrough if shader-analyzer output is available.
- Preserve the exact registration names and layer-count matrix, but explain the secondary-command-buffer skip rather than presenting it as an unexplained omission.
- Distill Background Knowledge to the Layer built-in, layered image view, and stage-specific output semantics.
- Copy the Failure Cause Mapping table directly into the final page; write Cause Analysis fresh.
- Keep implementation helpers in the source appendix, not in the main narrative.
