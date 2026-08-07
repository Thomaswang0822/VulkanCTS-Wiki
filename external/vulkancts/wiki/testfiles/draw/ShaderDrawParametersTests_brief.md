# Understanding Brief: ShaderDrawParametersTests

## One-Sentence Test Purpose

This test checks whether Vulkan exposes the correct base vertex, base instance, and draw index to vertex shaders across direct, indexed, indirect, instanced, and multi-draw command forms.

## Background Knowledge

### Shader-visible draw parameters

`gl_BaseVertexARB` describes the vertex offset of an indexed draw, `gl_BaseInstanceARB` describes the draw's first instance, and `gl_DrawIDARB` identifies a draw within a multi-draw indirect call. They are related to command parameters, but they are not interchangeable: vertex indexing, instance indexing, and indirect-record selection are separate parts of execution.

### Why the image can validate a built-in

The test's vertex shader turns these values into visible rectangle positions and colors. The host also constructs the expected rectangles from the same intended offsets. Junk records around the valid vertex data make accidental zero-based fetches visibly different from the expected result.

## One Concrete Example

In `draw_index.draw_indexed_instanced`, one indexed indirect call consumes three `VkDrawIndexedIndirectCommand` records and draws three instances per record. The shader uses `gl_DrawIDARB` to select one of three per-draw offsets and colors, and subtracts `gl_BaseInstanceARB` from `gl_InstanceIndex` to select the instance offset. A wrong draw ID changes the rectangle's position or color even if index and instance fetch are otherwise correct.

## End-to-End Test Flow

```text
[host] register a test family and select command flags
[host] create vertex data with valid and junk records
[host] create an index buffer for indexed cases or an indirect buffer for indirect cases
[host] build the graphics pipeline with the selected vertex shader and pass-through fragment shader
[host] record a direct draw or an indirect draw with the selected indexed, instanced, first-instance, and multi-draw parameters
[device] execute the vertex shader and rasterize the triangle strip into the color target
[host] submit and wait, then read back the color image
[host] build the reference rectangles and fuzzy-compare the rendered image with threshold 0.05
[host] return `OK` or `Rendered image is incorrect`
```

The shared draw infrastructure may record the work through a legacy render pass, dynamic rendering, or a secondary command buffer. Those modes change recording and attachment scope, not the built-in values being checked.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

| Artifact | How it is produced | Role |
|---|---|---|
| Vertex GLSL | The four `VertexFetchShaderDrawParameters*.vert` files are loaded according to the test family. | Reads shader draw-parameter built-ins and encodes them into position/color. |
| Fragment GLSL | `vulkan/draw/VertexFetch.frag` is used by every family. | Writes the vertex-stage color to the color attachment. |
| Graphics pipeline | Shared draw setup creates the pipeline with `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP`. | Executes the shader and rasterization path under test. |
| Reference image | `DrawTest::drawReferenceImage` constructs rectangles from expected instance and draw offsets. | Supplies the independent expected result. |

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|---|---|---|---|---|---|
| Vertex buffer | yes | yes | read by vertex input | no | Contains valid rectangle vertices separated by junk data. |
| Index buffer | yes, indexed cases | yes | read by indexed commands | no | Exercises `firstIndex` and `vertexOffset`. |
| Indirect buffer | yes, indirect cases | yes | read by indirect commands | no | Contains one or three draw command records. |
| Color target image | yes | yes | written by rasterization | yes | Carries the shader-visible parameter result. |

## What Is Checked

- The shader output is checked indirectly through the final color attachment image, not through a storage buffer or a scalar built-in readback.
- The reference image draws the expected rectangle for each instance and indirect draw. Its instance offsets are `(0,0)`, `(-0.3,0)`, and `(0,0.3)`; its draw offsets are `(0,0)`, `(-0.3,-0.3)`, and `(0.3,0.3)`.
- `tcu::fuzzyCompare` uses a threshold of `0.05`. Any mismatch returns `Rendered image is incorrect`; a successful comparison returns `OK`.

## Behavior Parameter Identification

> **Behavior parameter:** registered test family
>
> **Candidate values:** `base_vertex`, `base_vertex_only`, `base_instance`, `base_instance_only`, `draw_index`

The family is the primary behavioral axis because it selects which shader-visible built-in is being validated and which command combinations are generated. Command form, instancing, first instance, and multi-draw are secondary dimensions within those families.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `base_vertex` | Incorrect base-vertex exposure or indexed vertex-offset handling, vertex fetch, command recording, or image comparison path. |
| `base_vertex_only` | Incorrect isolated base-vertex exposure, indexed/non-indexed command handling, or shader/pipeline setup. |
| `base_instance` | Incorrect base-instance exposure, instance-index calculation, `firstInstance` handling, or command execution. |
| `base_instance_only` | Incorrect isolated base-instance exposure or instanced command handling. |
| `draw_index` | Incorrect draw-ID exposure or multi-draw indirect record selection, including indexed or instanced interaction. |

The image comparison localizes the symptom to the rendered result. Further investigation is required to distinguish built-in exposure from command interpretation, rasterization, attachment, or readback problems.

## Important Variations and Special Cases

- `base_vertex` and `base_vertex_only` contain `draw`, `draw_indexed`, `draw_indirect`, and `draw_indexed_indirect`.
- `base_instance` and `base_instance_only` additionally contain `draw_indirect_first_instance` and `draw_indexed_indirect_first_instance`. These require `drawIndirectFirstInstance`.
- `draw_index` always uses indirect multi-draw with three records and covers `draw`, `draw_instanced`, `draw_indexed`, and `draw_indexed_instanced`. These cases require multi-draw indirect support.
- Dynamic rendering requires `VK_KHR_dynamic_rendering`; all cases require `VK_KHR_shader_draw_parameters` and the optional `shaderDrawParameters` feature when applicable.
- The isolated families are omitted for secondary command-buffer variants to limit repeated coverage. The topology remains `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP`.

## Source Mapping

| Topic | Source link | Why it matters |
|---|---|---|
| Registration and exact leaves | [`ShaderDrawParametersTests::init`](../../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp#L467-L538) | Defines the five test families, shaders, flags, and command forms. |
| Command construction | [`DrawTest::draw`](../../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp#L281-L355) | Shows direct and indirect command fields and draw counts. |
| Reference and validation | [`drawReferenceImage`](../../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp#L225-L255), [`DrawTest::iterate`](../../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp#L257-L279) | Defines expected rectangles and the pass/fail comparison. |
| Combined shader | [`VertexFetchShaderDrawParameters.vert`](../../../data/vulkan/draw/VertexFetchShaderDrawParameters.vert) | Uses base vertex, base instance, and draw ID together. |
| Draw-index shader | [`VertexFetchShaderDrawParametersDrawIndex.vert`](../../../data/vulkan/draw/VertexFetchShaderDrawParametersDrawIndex.vert) | Shows per-draw offset and color selection. |
| Mustpass evidence | [`draw.txt`](../../../mustpass/main/vk-default/draw.txt#L28999-L29022) | Confirms the exact `draw.renderpass.shader_draw_parameters` registration paths. |
| Vulkan feature semantics | [`features.adoc`](../../../../vulkan-docs/src/chapters/features.adoc#L1795-L1805) | Grounds the support requirements. |

## Questions / Risk Points for User Audit

- The mustpass excerpt confirms the render-pass hierarchy and leaves. Dynamic-rendering and secondary-command-buffer coverage is selected by shared dispatcher parameters and should not be inferred as additional registration identifiers in this page.
- The shader files use the `ARB` spelling (`gl_BaseVertexARB`, `gl_BaseInstanceARB`, and `gl_DrawIDARB`) because they enable `GL_ARB_shader_draw_parameters`; the page preserves those exact shader identifiers.
- The exact valid vertex locations and indirect offsets are source constants, not random per-case values: `NDX_FIRST_VERTEX = 2`, `NDX_SECOND_VERTEX = 9`, `NDX_FIRST_INDEX = 11`, and `NDX_SECOND_INDEX = 17`.

## Conversion Notes for Final Wiki Rewrite

- Preserve the exact hierarchy `draw.renderpass.shader_draw_parameters` and all five family identifiers.
- Keep the five behavior-family values and the copied Failure Cause Mapping table aligned between this brief and the final page.
- Distill the built-in definitions into the final `Background Knowledge`; keep command construction, shader walkthroughs, image comparison, and feature gates in their respective final sections.
- Preserve the exact shader filenames, `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP`, `draw_indirect_first_instance`, and `draw_indexed_indirect_first_instance` identifiers.
