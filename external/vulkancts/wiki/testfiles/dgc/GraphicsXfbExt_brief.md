# Understanding Brief: EXT graphics transform-feedback tests

## One-Sentence Test Purpose

This test checks whether `VK_EXT_device_generated_commands` executes graphics draws while transform feedback captures the expected pre-rasterization vertices, and whether a later indirect draw reproduces the same geometry.

## Background Knowledge

### Transform feedback capture and draw-count execution

Transform feedback writes selected outputs from the last pre-rasterization shader stage into a bound transform-feedback buffer while a graphics draw runs. The counter records how many bytes the draw produced. `vkCmdDrawIndirectByteCountEXT` then uses that counter and a vertex stride to draw the captured vertices.

Why it matters here:
- The first generated-command sequence runs while transform feedback is active.
- The second draw reads the captured `vec4` positions as a vertex buffer and uses the byte count produced by the first draw.
- The test therefore checks both DGC draw execution and the EXT transform-feedback handoff.

### Pipeline and shader-object graphics state

A graphics command can use a conventional graphics pipeline or bind `VkShaderEXT` objects with dynamic shader-object state. Both paths must expose the same shader stages and rasterization state to the draw. The shader-object variants test that the DGC sequence works with this alternate state representation.

### Tessellation and geometry stages

Without tessellation, the vertex shader receives a triangle strip and the geometry shader, when enabled, passes each triangle through. With tessellation, the input uses three-vertex patches. The tessellation control shader emits three control points and unit tessellation levels, and the tessellation evaluation shader interpolates the patch. A geometry shader may then pass the resulting triangle through. Transform feedback captures the output of the last pre-rasterization stage, so the `xfb` interface moves from the vertex shader to tessellation evaluation or geometry as stages are added.

## One Concrete Example

Consider `dEQP-VK.dgc.ext.graphics.xfb.nodiscard` using pipeline state without tessellation or geometry. The host supplies two four-vertex strips that cover the upper and lower halves of an 8 x 8 framebuffer. The vertex shader writes `gl_Position` and declares it with `layout(xfb_buffer = 0, xfb_offset = 0)`. The DGC layout contains one draw token, and the stream contains two ordinary draw records. Transform feedback captures the six vertices that form the two triangles from each strip. The second draw consumes that buffer with `vkCmdDrawIndirectByteCountEXT` and renders blue pixels.

The tessellation form uses two three-vertex patches per draw instead. Because the passthrough tessellation shaders use unit tessellation levels, each patch produces one triangle, so the expected captured vertex list is the input patch list in triangle order.

## End-to-End Test Flow

```text
[host] choose discard, geometry, tessellation, and shader-object parameters
[host] create two half-screen quads as either triangle strips or three-vertex patch lists
[host] create the vertex buffer, transform-feedback buffer, counter buffer, and color images
[host] build vertex and fragment GLSL, plus passthrough tessellation and geometry GLSL when selected
[host] create conventional pipelines or VkShaderEXT objects and shader-object state
[host] create one DGC draw token layout and two stream records, one per quad
[host] clear the output images and begin the first render pass or dynamic-rendering instance
[host] bind the transform-feedback buffer and begin transform feedback
[device] execute the two generated draws and write captured vertices and the byte counter
[host] end transform feedback and insert barriers from transform-feedback writes to vertex input and indirect reads
[host] begin the second render pass or dynamic-rendering instance
[device] draw the captured vertices with vkCmdDrawIndirectByteCountEXT
[host] copy color images and the transform-feedback buffer to host-visible memory
[host] compare color images and captured triangles with the expected results
[host] decide pass/fail
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `initPrograms` creates a vertex shader and a fragment shader for every case. It adds `tesc` and `tese` for tessellation cases and `geom` for geometry cases.
- The vertex shader places the `xfb` qualifier on `gl_Position` in the last pre-rasterization stage: the vertex shader without tessellation or geometry, the tessellation evaluation shader with tessellation only, or the geometry shader when geometry is enabled.
- Conventional cases create two graphics pipelines. The first uses rasterizer discard for the capture draw and the second enables rasterization for the indirect draw. Shader-object cases bind the same stage objects twice with the corresponding topology and rasterization state.
- The DGC stream has two `VkDrawIndirectCommand` records. Each record supplies the selected vertex count, one instance, and the first vertex for one quad.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Input vertex buffer | yes | yes, as vertex input | read by the first generated draw | no | Holds two quads as strips or patches. |
| Transform-feedback buffer | yes | yes, with `cmdBindTransformFeedbackBuffersEXT` and later as a vertex buffer | written during capture, read by the second draw | yes | Carries the captured `gl_Position` values between draws. |
| Transform-feedback counter buffer | yes | yes, for begin/end and byte-count drawing | written by transform feedback and read by `vkCmdDrawIndirectByteCountEXT` | no | Supplies the captured byte count to the second draw. |
| Capture color image | yes for `nodiscard` cases | yes when rasterization is enabled for the first draw | written by the capture draw when discard is disabled | yes | Confirms that the capture draw itself renders the expected blue image when it is not discarded. |
| Indirect-draw color image | yes | yes as the second color attachment | written by the second draw | yes | Confirms that captured vertices reproduce the expected geometry. |
| DGC stream buffer | yes | yes through its device address | read by DGC execution | no | Holds the two `VkDrawIndirectCommand` records. |

## What Is Checked

- Each color image is compared with an 8 x 8 reference image cleared to black and filled with `vec4(0.0, 0.0, 1.0, 1.0)` where the geometry covers the framebuffer. The threshold is zero for all channels.
- `nodiscard` cases compare both the first capture-draw image and the second indirect-draw image. `discard` cases omit the first image because rasterizer discard removes its color output, then compare the indirect-draw image.
- The host copies the transform-feedback buffer after queue completion and divides it into four triangles. The expected non-tessellation output expands each four-vertex strip into two triangles per quad. The expected tessellation output copies the two three-vertex patches directly.
- `verifyTriangle` compares each expected and captured triangle as sets of three `tcu::Vec4` values, so vertex order within a triangle does not affect the result.
- Any color comparison or triangle mismatch makes the case fail with `Unexpected result in color buffers or vertex buffers; check log for details`. A fully matching case returns `Pass`.

## Behavior Parameter Identification

> **Behavior parameter:** registered variant family formed by the four boolean parameters
>
> **Candidate values:** `discard`, `discard_geom`, `discard_geom_shader_objects`, `discard_shader_objects`, `discard_tess`, `discard_tess_geom`, `discard_tess_geom_shader_objects`, `discard_tess_shader_objects`, `nodiscard`, `nodiscard_geom`, `nodiscard_geom_shader_objects`, `nodiscard_shader_objects`, `nodiscard_tess`, `nodiscard_tess_geom`, `nodiscard_tess_geom_shader_objects`, `nodiscard_tess_shader_objects`

The primary behavioral axis is the registered variant family. `discardXFB` changes whether the first draw's rasterization is discarded, `useGeom` and `useTess` change the last pre-rasterization capture stage and primitive topology, and `useShaderObjects` changes the graphics state representation.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| Any `discard` variant | Transform-feedback capture, counter handling, DGC draw execution, selected pre-rasterization stage, or the shader-object path. The first color image is intentionally absent. |
| Any `nodiscard` variant | The same capture and execution causes, plus rasterizer discard state or the first color attachment and copyback path. |
| Any `_geom` variant | Geometry-stage passthrough, geometry-stage `xfb` declaration, triangle-strip output, or the shared capture and indirect-draw path. |
| Any `_tess` variant | Tessellation patch input, passthrough tessellation stages, tessellation-evaluation `xfb` declaration, or the shared capture and indirect-draw path. |
| Any `_tess_geom` variant | The tessellation-to-geometry stage chain, geometry-stage capture, or the shared capture and indirect-draw path. |
| Any `_shader_objects` variant | `VkShaderEXT` creation or binding, `nextStage` declarations, shader-object graphics state, or the shared capture and indirect-draw path. |

### Cause Analysis

#### Transform-feedback capture and counter handoff

**Possible failure symptoms:** The captured buffer contains an incorrect position, an incomplete triangle, extra vertices, or a counter value that makes the indirect draw render the wrong amount of geometry. The color comparison can fail in the second image even when the first image passes.

**Possible implementation causes:** The implementation may mishandle `cmdBindTransformFeedbackBuffersEXT`, `cmdBeginTransformFeedbackEXT`, `cmdEndTransformFeedbackEXT`, the selected `xfb` output, or the counter consumed by `cmdDrawIndirectByteCountEXT`. The source and transform-feedback valid-usage chapters establish these operations and their ordering. The failing buffer and image entries are needed to separate them.

#### DGC draw stream and indirect execution

**Possible failure symptoms:** One quad is missing, both quads are shifted, or the capture and indirect images disagree even though the shader-stage configuration is otherwise valid.

**Possible implementation causes:** The implementation may read the DGC device address, vertex count, or first-vertex fields incorrectly, or may execute the two generated draw sequences with incorrect state. The test source identifies the stream contents and the `VK_INDIRECT_COMMANDS_TOKEN_TYPE_DRAW_EXT` layout; a precise implementation-layer cause needs further investigation.

#### Tessellation and geometry stage chain

**Possible failure symptoms:** Tessellation variants produce triangles with wrong positions or counts. Geometry variants can show missing output or incorrect triangle boundaries. The host triangle comparison reports the affected output triangle.

**Possible implementation causes:** The implementation may connect `nextStage` incorrectly for shader objects, select the wrong last pre-rasterization stage for transform feedback, mishandle patch-list input, or lower the passthrough tessellation or geometry shader incorrectly. The source does not assign a failure to a specific driver, compiler, or hardware layer.

#### Rasterizer discard and color results

**Possible failure symptoms:** A `discard` case reports an unexpected first color result only if the source or result handling incorrectly treats that image as present. A `nodiscard` case can fail in the first image while the captured vertex comparison passes, or in the second image after capture.

**Possible implementation causes:** The selected pipeline or shader-object rasterization state may not apply `rasterizerDiscardEnable` consistently. A failure limited to the first color image can also involve the capture attachment setup or copyback. Source inspection is needed to distinguish state application from image handling.

#### Shader-object graphics state

**Possible failure symptoms:** Only `_shader_objects` variants fail, with color or captured-position differences while the corresponding pipeline variant passes.

**Possible implementation causes:** The implementation may create or bind a shader object with an incorrect stage chain, fail to bind a null handle for unused optional stages, or apply the wrong topology or rasterization state between the capture and indirect draws. The source establishes the differing state path; it does not identify the faulty implementation layer.

## Important Variations and Special Cases

- The source constructs all 16 combinations of `discardXFB`, `useGeom`, `useTess`, and `useShaderObjects`. The registered name order is `discard` or `nodiscard`, then `_tess`, then `_geom`, then `_shader_objects`.
- `discard` sets `rasterizerDiscardEnable` for the capture pipeline or shader-object state. It also removes the capture color image and uses no fragment module in the conventional capture pipeline. Transform feedback still captures vertices.
- `nodiscard` keeps the capture color attachment and fragment shader, so the first image is checked as well as the second image.
- `useTess` changes the input to two three-vertex patch-list draws. Without tessellation, the input uses two four-vertex triangle-strip draws. The indirect draw uses triangle-list topology without tessellation and patch-list topology with tessellation.
- `useGeom` adds a passthrough geometry shader that emits three vertices for each input triangle. When geometry is present, the geometry shader owns the `xfb` output declaration.
- `_shader_objects` cases require `VK_EXT_shader_object`; geometry and tessellation cases require their corresponding core features. All cases require transform feedback, transform-feedback drawing, and the DGC support checked by `checkDGCExtSupport`.
- The source always uses two generated draws, two triangles per draw, three captured vertices per triangle, and an 8 x 8 `VK_FORMAT_R8G8B8A8_UNORM` color target.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Parameters and support | [Params, `checkSupport`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsXfbTestsExt.cpp#L54-L127) | Defines the four switches and feature gates. |
| Generated shaders | [XFB shader construction](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsXfbTestsExt.cpp#L134-L234) | Shows stage-specific `xfb` placement and passthrough stages. |
| Capture and indirect pipelines | [pipeline and shader-object setup](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsXfbTestsExt.cpp#L474-L586) | Distinguishes capture state from indirect-draw state. |
| DGC stream and execution | [layout and generated draws](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsXfbTestsExt.cpp#L589-L619) | Defines the draw token and two stream records. |
| Transform-feedback commands | [capture sequence](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsXfbTestsExt.cpp#L673-L743) | Shows buffer binding, begin/end, generated execution, and barriers. |
| Indirect draw and copies | [second draw and copyback](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsXfbTestsExt.cpp#L745-L781) | Shows counter-based drawing and host readback. |
| Result checking | [color and vertex validation](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsXfbTestsExt.cpp#L783-L878) | Defines reference images, triangle comparison, and pass/fail. |
| Registered names | [registration loop](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsXfbTestsExt.cpp#L883-L907) | Defines all 16 exact direct-child names. |
| Transform-feedback validity | [bind, begin, draw, and end common valid usage](../../../../vulkan-docs/src/chapters/commonvalidity/xform_feedback_bind_common.adoc), [begin](../../../../vulkan-docs/src/chapters/commonvalidity/xform_feedback_begin_common.adoc), [draw](../../../../vulkan-docs/src/chapters/commonvalidity/xform_feedback_draw_common.adoc), [end](../../../../vulkan-docs/src/chapters/commonvalidity/xform_feedback_end_common.adoc) | Grounds the feature and command-order requirements. |

## Questions / Risk Points for User Audit

- Does the distinction between captured vertices and the two color-image checks match the intended reading of the test?
- Is the stage-specific placement of the `xfb` qualifier clear for tessellation and geometry variants?
- Does the explanation distinguish the pipeline path from the shader-object path without treating shader objects as a different rendering result?
- Are the exact registered names and their suffix order preserved?

## Conversion Notes for Final Wiki Rewrite

- Use the registered variant family as the primary behavior axis and retain the exact 16 names in the observed-values table.
- Keep one representative shader walkthrough for the non-tessellation capture path. Summarize the tessellation, geometry, and shader-object changes in the parameter variation table.
- Distill the transform-feedback counter, barrier, indirect draw, and triangle-set checking into the final runtime section.
- Copy the failure mapping table into the final page and write cause analysis from the actual validation logic.
