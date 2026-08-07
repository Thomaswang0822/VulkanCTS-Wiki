## Overview

**Core question:** Does a graphics pipeline route each primitive to the array layer selected by a vertex or tessellation-evaluation shader through `gl_Layer`?

- `ShaderLayerTests` is implemented by `vktDrawShaderLayerTests.cpp` and registered as the `shader_layer` test family.
- It provides `vertex_shader_<numLayers>` and `tessellation_shader_<numLayers>` test cases.
- Each case renders one colored rectangle per requested layer into a 2D-array color attachment, copies the layers to host memory, and compares them with generated reference images.
- The same implementation is reused under render-pass and dynamic-rendering draw paths. Secondary-command-buffer variants deliberately use a reduced layer-count set.

## Background Knowledge

- `gl_Layer` is the shader `Layer` built-in used to route a primitive to a slice of a layered framebuffer. The Vulkan specification describes `shaderOutputLayer` as the capability that permits Layer output from vertex or tessellation-evaluation shaders; this family additionally requires the `VK_EXT_shader_viewport_index_layer` device functionality in `checkRequirements`.
- A 2D-array image view exposes several same-sized color-image layers to one rendering operation. The layer selected by a primitive is independent of the fragment color written into that layer.
- The vertex and tessellation-evaluation stages see different identifiers. This test derives the layer from `gl_VertexIndex` in one family and from `gl_PrimitiveID` in the other, so the two families exercise stage-specific Layer-output paths.

## Registration Hierarchy

The dispatcher registers the family under `renderpass` and, outside Vulkan SC, under five dynamic-rendering command-buffer modes. The relevant paths are:

```text
draw.renderpass.shader_layer
├── vertex_shader_1
└── tessellation_shader_1

draw.dynamic_rendering.primary_cmd_buff.shader_layer
├── vertex_shader_1
└── tessellation_shader_1

draw.dynamic_rendering.partial_secondary_cmd_buff.shader_layer
├── vertex_shader_1
└── tessellation_shader_1

draw.dynamic_rendering.complete_secondary_cmd_buff.shader_layer
├── vertex_shader_1
└── tessellation_shader_1
```

`nested_partial_secondary_cmd_buff` and `nested_complete_secondary_cmd_buff` do not contain this family: `vktDrawTests.cpp` omits all non-basic families when nested secondary command buffers are selected. The `<numLayers>` placeholder expands to the exact leaves documented below.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Shader family | `vertex_shader`, `tessellation_shader` | Selects the stage that writes `gl_Layer` and the corresponding graphics pipeline. | [`createShaderLayerTests`](../../../modules/vulkan/draw/vktDrawShaderLayerTests.cpp#L1015-L1049) |
| Number of layers, render-pass and primary dynamic-rendering paths | `1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`, `256` | Sets the array-image layer count, rectangle count, draw vertex count, and number of host-side image comparisons. | [`numLayersToTest`](../../../modules/vulkan/draw/vktDrawShaderLayerTests.cpp#L1019-L1021) |
| Number of layers, dynamic-rendering secondary paths | `1`, `3`, `5`, `7`, `256` | The implementation skips odd indices of the source array when `useSecondaryCmdBuffer` is true, reducing the matrix for secondary recording. | [secondary reduction](../../../modules/vulkan/draw/vktDrawShaderLayerTests.cpp#L1025-L1029) |
| Rendering mode | `renderpass`; `dynamic_rendering.primary_cmd_buff`; `dynamic_rendering.partial_secondary_cmd_buff`; `dynamic_rendering.complete_secondary_cmd_buff` | Selects render-pass objects or dynamic rendering, and whether draw commands are recorded directly or in a secondary command buffer. | [draw dispatcher](../../../modules/vulkan/draw/vktDrawTests.cpp#L126-L198) |

## Behavior Parameters

The primary behavioral axis is the shader family. Layer count and command-recording mode vary the same layered-rendering contract; the shader family changes which shader stage produces the Layer output.

### `vertex_shader`: vertex-stage Layer output

The generated vertex shader assigns `gl_Layer = gl_VertexIndex / 6`. Since each rectangle consists of two triangles and six vertices, all vertices of one rectangle select the same layer. It forwards position and color to the fragment shader.

### `tessellation_shader`: tessellation-evaluation-stage Layer output

The generated tessellation-control shader passes a three-vertex patch through and sets all tessellation levels to `1.0`. The tessellation-evaluation shader assigns `gl_Layer = gl_PrimitiveID / 2`, interpolates position and color, and emits the resulting primitive. This validates Layer output after tessellation rather than at the vertex stage.

## Shader Analysis

The source-generated programs contain two representative mechanisms:

- The vertex path requires `GL_ARB_shader_viewport_layer_array`, computes the layer from the vertex index, and uses a simple pass-through fragment shader.
- The tessellation path uses three-vertex patches with unit tessellation levels. Its tessellation-evaluation shader requires the same Layer-array extension and computes the layer from the primitive ID before interpolating the patch outputs.

The `_1_2` program variants use the same generated GLSL sources as `vert` and `tese`, but are built with the Vulkan 1.2/SPIR-V 1.5 options selected by the test. The test chooses those binaries only when the context supports Vulkan 1.2.

## Runtime Execution and Result Checking

- Each case uses a 256x256 `VK_FORMAT_R8G8B8A8_UNORM` color image with `numLayers` array layers and a `VK_IMAGE_VIEW_TYPE_2D_ARRAY` view.
- The host generates a grid of rectangles and one deterministic color per layer, clears the target to `(0.5, 0.5, 0.5, 1.0)`, and uploads the vertex data through a host-visible vertex buffer.
- The graphics pipeline uses triangle-list topology for the vertex family and patch-list topology for the tessellation family. It binds the array view as the color attachment.
- Render-pass cases use a framebuffer whose layer count is `numLayers`. Dynamic-rendering cases transition the image, begin rendering with that layer count, draw, and end rendering.
- In secondary modes, the secondary command buffer records the draw; depending on the mode, it either contains only the draw commands or the complete dynamic-rendering instance. The primary command buffer executes it.
- After submission and completion, `copyImageToBuffer` copies the layered image to a host-visible buffer. The host partitions the buffer into one 256x256 image per layer.
- `generateReferenceImage` builds the expected clear-color background plus that layer's rectangle. Every layer is compared with `tcu::floatThresholdCompare` using `Vec4(0.02f)`; any mismatch fails the case.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `vertex_shader` | Incorrect Layer output handling in the vertex path; incorrect per-vertex routing or associated vertex/color processing; layered attachment or image-copy behavior. |
| `tessellation_shader` | Incorrect Layer output handling in the tessellation-evaluation path; patch/primitive processing or tessellation pipeline behavior; layered attachment or image-copy behavior. |

### Cause Analysis

#### Vertex-stage Layer routing

**Possible failure symptoms:** One or more per-layer image comparisons differ from the reference. A rectangle can appear in the wrong layer, be absent, or have incorrect coverage or color.

**Possible implementation causes:** The failure is consistent with incorrect handling of a vertex-stage `Layer` output, incorrect indexing of vertex input, or a problem in the layered attachment path. The CTS check alone does not localize the cause to shader compilation, rasterization, image operations, or host copyback; source-level and implementation-level investigation is needed to distinguish them.

#### Tessellation-evaluation-stage Layer routing

**Possible failure symptoms:** A layer image differs after the tessellation path executes, including missing or misplaced patch-derived rectangles or incorrect interpolated colors.

**Possible implementation causes:** The failure is consistent with incorrect Layer handling after tessellation, primitive-ID interpretation, patch processing, or the shared layered-rendering and readback path. The test does not by itself identify which implementation component is responsible, so source-level investigation is needed before assigning a narrower cause.

## Case Pruning

### Requirement-based pruning

- Every case requires multi-viewport support, `VK_EXT_shader_viewport_index_layer`, at least 256 `maxFramebufferLayers`, and at least 16 `maxViewports`.
- Dynamic-rendering cases require `VK_KHR_dynamic_rendering`.
- `tessellation_shader_*` cases require the core `tessellationShader` feature.
- On a Vulkan 1.2-capable context, the test uses the `_1_2` binaries; otherwise it uses the base binaries. Unsupported requirements prevent execution rather than turning into an image-comparison failure.

### Design-based pruning

- Secondary-command-buffer paths skip every odd index in the layer-count array, producing `1`, `3`, `5`, `7`, and `256` instead of all nine values. This is an intentional reduction in the dynamic secondary matrix.
- Nested secondary-command-buffer roots do not register this family because the draw dispatcher retains only `basic` for nested modes.

## Key Takeaways

- The two test-family leaves differ by the stage that writes `gl_Layer`: vertex processing versus tessellation evaluation.
- The expected result is layer-specific, not just one aggregate image: every array layer is copied back and compared independently.
- The `256` case exercises the minimum framebuffer-layer limit, while secondary dynamic-rendering paths intentionally use a smaller layer-count matrix.
- A failure proves that the observed layered image does not match the stage-specific Layer-routing contract; it does not, without further investigation, identify the failing implementation component.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test registration | [`createShaderLayerTests`](../../../modules/vulkan/draw/vktDrawShaderLayerTests.cpp#L1015-L1049) | Creates `shader_layer`, exact family prefixes, and layer-count leaves. |
| Vertex program generation | [`initVertexTestPrograms`](../../../modules/vulkan/draw/vktDrawShaderLayerTests.cpp#L349-L391) | Generates the vertex and fragment shader sources. |
| Tessellation program generation | [`initTessellationTestPrograms`](../../../modules/vulkan/draw/vktDrawShaderLayerTests.cpp#L393-L479) | Generates vertex, tessellation-control, tessellation-evaluation, and fragment sources. |
| Renderer setup | [`Renderer::Renderer`](../../../modules/vulkan/draw/vktDrawShaderLayerTests.cpp#L596-L672) | Creates the layered image/view, buffers, shader modules, render-pass objects, and pipeline. |
| Command recording | [`Renderer::draw`](../../../modules/vulkan/draw/vktDrawShaderLayerTests.cpp#L674-L752) | Implements render-pass, dynamic-rendering, and secondary-command-buffer flows. |
| Requirements | [`checkRequirements`](../../../modules/vulkan/draw/vktDrawShaderLayerTests.cpp#L863-L881) | Enforces extension, feature, and limit prerequisites. |
| Vertex validation | [`testVertexShader`](../../../modules/vulkan/draw/vktDrawShaderLayerTests.cpp#L883-L946) | Generates references and compares each vertex-path layer. |
| Tessellation validation | [`testTessellationShader`](../../../modules/vulkan/draw/vktDrawShaderLayerTests.cpp#L948-L1012) | Generates references and compares each tessellation-path layer. |
| Draw-suite routing | [`createChildren`](../../../modules/vulkan/draw/vktDrawTests.cpp#L70-L120) | Shows which roots receive this family and the nested-secondary exclusion. |
| Rendering-mode roots | [`createTests`](../../../modules/vulkan/draw/vktDrawTests.cpp#L126-L201) | Defines the exact render-pass and dynamic-rendering hierarchy. |
| Vulkan feature semantics | [`shaderOutputLayer`](../../../../vulkan-docs/src/chapters/features.adoc#L941-L948) | Documents the Layer capability required by the shader output. |
