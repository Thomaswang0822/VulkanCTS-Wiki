# Understanding Brief: ShaderViewportIndexTests

## One-Sentence Test Purpose

This test checks whether graphics shaders route primitives to the intended viewport with `gl_ViewportIndex`, and whether a fragment shader receives that viewport index when it selects its output color.

## Background Knowledge

### Viewport selection by a pre-rasterization shader

A graphics pipeline can define several viewports. A vertex or tessellation evaluation shader that writes `gl_ViewportIndex` selects one viewport for the primitive it produces. The value must be the same for all vertices of that primitive. The final active pre-rasterization stage that writes the built-in controls the selection.

Why it matters here:
- The vertex cases derive an index from each six-vertex quad.
- The tessellation cases derive an index from each pair of input triangles after tessellation evaluation.

### `gl_ViewportIndex` in a fragment shader

A fragment shader reads the viewport index of the primitive that produced each fragment. It does not select the viewport at that stage. The fragment cases use the value as an index into a uniform-buffer color array.

Why it matters here:
- A primitive can reach the correct viewport but still produce the wrong color if fragment-stage input is wrong.
- `fragment_shader_implicit` uses one viewport without an earlier shader writing the built-in, so it checks the default first viewport path.

## One Concrete Example

Consider `dEQP-VK.draw.renderpass.shader_viewport_index.vertex_shader_4`. The host creates four grid cells and four colors, then issues one draw with 24 vertices. Each six consecutive vertices form a full-viewport quad. The vertex shader computes `gl_VertexIndex / 6`, so the two triangles for a quad share viewport indices 0 through 3. The pipeline applies the matching viewport and the reference image expects one colored rectangle in each cell.

## End-to-End Test Flow

```text
[host] choose a shader-stage variant and numViewports from 1 through 16
[host] generate grid rectangles, colors, and six vertices per rectangle
[host] create a 128 by 128 color image, vertex buffer, graphics pipeline, and readback buffer
[host] for fragment cases, upload the colors into a uniform buffer and bind it at set 0, binding 0
[host] record a render pass or dynamic-rendering sequence and draw numViewports * 6 vertices
[device] the selected stage writes or the fragment stage reads gl_ViewportIndex
[device] rasterization places each quad in its selected viewport and writes its color
[host] copy the color image to the host-visible buffer after rendering
[host] compare the image with the generated grid using a 0.02 per-component float threshold
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The source builds three program sets: a vertex-index writer, a fragment-index reader, and a tessellation-evaluation writer. Vertex and tessellation evaluation shaders have SPIR-V 1.0 programs plus SPIR-V 1.5 variants selected for a Vulkan 1.2 context. The fragment shader has no explicit build option and uses the default target.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Color attachment image | yes | yes | written by rasterization | yes, through a copy buffer | Holds the rendered viewport grid. |
| Vertex buffer | yes | yes | read by the vertex stage | no | Contains two triangles and one color per viewport. |
| `Colors` uniform buffer | yes, fragment cases only | yes, set 0 binding 0 | read by the fragment stage | no | Lets the fragment shader select `color[gl_ViewportIndex]`. |
| Readback buffer | yes | yes, transfer destination | written by image-to-buffer copy | yes | Supplies pixels for the comparison. |

## What Is Checked

The host constructs a reference image with the same grid geometry, gray clear color, and per-cell colors as the draw. `tcu::floatThresholdCompare` compares all rendered pixels against that reference with `Vec4(0.02f)`. Any mismatch fails the test with "Rendered image is not correct".

## Behavior Parameter Identification

> **Behavior parameter:** behavioral group
>
> **Candidate values:** `vertex_shader_N`, `fragment_shader_implicit`, `fragment_shader_N`, `tessellation_shader_N`

`N` ranges from 1 through 16 for the three numbered groups. It changes grid size and pipeline viewport count, but the behavioral group determines which stage produces or consumes `gl_ViewportIndex`.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `vertex_shader_N` | Vertex-stage `ViewportIndex` export, primitive viewport selection, or multi-viewport rasterization is incorrect. |
| `fragment_shader_implicit` | The default viewport index supplied to fragment invocations is incorrect. |
| `fragment_shader_N` | Vertex-stage viewport selection or fragment-stage `ViewportIndex` input and uniform-array indexing is incorrect. |
| `tessellation_shader_N` | Tessellation-evaluation `ViewportIndex` export, primitive indexing, or multi-viewport rasterization is incorrect. |

## Important Variations and Special Cases

- `fragment_shader_implicit` has `numViewports = 1` and leaves `writeFromVertex` false. It isolates fragment-stage reading of the first viewport index.
- The numbered fragment cases set `writeFromVertex` true. They test the producer-consumer path from vertex output to fragment input.
- The tessellation cases require `tessellationShader`; the tessellation control shader sets every tessellation level to 1.0, so the evaluation shader routes the original triangle pairs.
- All variants require `multiViewport`, `VK_EXT_shader_viewport_index_layer`, and at least 16 supported viewports. Dynamic-rendering variants also require `VK_KHR_dynamic_rendering`.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Vertex and fragment program generation | [initVertexTestPrograms and initFragmentTestPrograms](../../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp#L418-L504) | Shows the vertex export and fragment uniform-array read. |
| Tessellation program generation | [initTessellationTestPrograms](../../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp#L506-L600) | Shows the evaluation-stage export and fixed control stage. |
| Grid, colors, and reference image | [generateGrid through generateReferenceImage](../../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp#L353-L416) | Defines the expected image. |
| Renderer setup and draw | [Renderer](../../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp#L646-L943) | Builds resources, binds the fragment uniform buffer, and records the draw. |
| Image validation | [testVertexFragmentShader and testTessellationShader](../../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp#L945-L1068) | Defines readback and pass/fail behavior. |
| Support and registration | [checkSupport and createShaderViewportIndexTests](../../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp#L1070-L1117) | Defines requirements and all registered cases. |
| Vulkan `ViewportIndex` semantics | [interfaces.adoc](../../../../vulkan-docs/src/chapters/interfaces.adoc#L5662-L5748) | Defines stage use, selection, and per-primitive consistency. |

## Questions / Risk Points for User Audit

- Does the behavioral grouping make the distinction between writing and reading `gl_ViewportIndex` clear?
- Is the special role of `fragment_shader_implicit` clear?
- Does the grid-based image comparison make the observable failure signal clear?
- Does the resource table distinguish the fragment-only uniform buffer from vertex attributes?

## Conversion Notes for Final Wiki Rewrite

- Keep only the two viewport-index concepts in the final Background Knowledge section.
- Use the four behavioral groups in final `## Behavior Parameters` and copy the failure mapping table unchanged.
- Use `vertex_shader_4` as the representative shader walkthrough because it exposes the direct index calculation with a small grid.
- Keep pipeline setup, readback, and feature gates in the final runtime and pruning sections.
