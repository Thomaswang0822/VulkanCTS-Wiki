## Overview

**Core question:** Does DGC execute the capture draw and does transform feedback preserve the vertices used by the later indirect draw?

- This page covers the implementation and registration in `vktDGCGraphicsXfbTestsExt.cpp` for `dgc.ext.graphics.xfb`.
- The test registers 16 direct test families. Four boolean parameters select transform-feedback rasterizer discard, geometry, tessellation, and shader-object state.
- Each case executes two generated draws. The first draw captures pre-rasterization `gl_Position` values and a byte counter. The second draw consumes that buffer with `vkCmdDrawIndirectByteCountEXT`.
- The page explains the exact variants, stage-specific capture behavior, host synchronization, and color and vertex result checks.

## Background Knowledge

- Transform feedback writes selected outputs from the last pre-rasterization shader stage into a bound buffer. Its counter records the amount of data produced, and `vkCmdDrawIndirectByteCountEXT` can use that count for a later draw.
- A graphics pipeline and shader objects provide two ways to bind the same graphics stages and state. The shader-object path still needs a valid stage chain, topology, viewport, vertex input, and rasterization state.
- Tessellation consumes patch-list input. Geometry shaders consume assembled primitives and can emit a replacement primitive stream. When either stage is enabled here, the test places the transform-feedback declaration on the last pre-rasterization stage that produces the captured position.

## Registration Hierarchy

```text
dgc.ext.graphics.xfb
├── discard
├── discard_geom
├── discard_geom_shader_objects
├── discard_shader_objects
├── discard_tess
├── discard_tess_geom
├── discard_tess_geom_shader_objects
├── discard_tess_shader_objects
├── nodiscard
├── nodiscard_geom
├── nodiscard_geom_shader_objects
├── nodiscard_shader_objects
├── nodiscard_tess
├── nodiscard_tess_geom
├── nodiscard_tess_geom_shader_objects
└── nodiscard_tess_shader_objects
```

These direct test families are created by the four nested loops in [the registration function](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsXfbTestsExt.cpp#L883-L907) and appear as exact mustpass paths under `dEQP-VK.dgc.ext.graphics.xfb`.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Transform-feedback rasterization | `discard`, `nodiscard` | Controls whether the first draw rasterizes and whether its color image is checked. | [rasterization state and capture image](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsXfbTestsExt.cpp#L441-L449) [L491-L508](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsXfbTestsExt.cpp#L491-L508) |
| Tessellation | absent, `_tess` | Selects triangle-strip input or three-vertex patch-list input and changes the capture stage and topology. | [input vertices and topology](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsXfbTestsExt.cpp#L379-L429) [L522-L523](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsXfbTestsExt.cpp#L522-L523) |
| Geometry | absent, `_geom` | Adds a passthrough geometry shader and makes geometry the last pre-rasterization capture stage. | [geometry shader generation](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsXfbTestsExt.cpp#L213-L233) |
| Graphics state representation | absent, `_shader_objects` | Selects conventional pipelines or `VkShaderEXT` objects for both rendering instances. | [pipeline and shader-object creation](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsXfbTestsExt.cpp#L531-L586) |
| Exact registered variant | `discard`, `discard_geom`, `discard_geom_shader_objects`, `discard_shader_objects`, `discard_tess`, `discard_tess_geom`, `discard_tess_geom_shader_objects`, `discard_tess_shader_objects`, `nodiscard`, `nodiscard_geom`, `nodiscard_geom_shader_objects`, `nodiscard_shader_objects`, `nodiscard_tess`, `nodiscard_tess_geom`, `nodiscard_tess_geom_shader_objects`, `nodiscard_tess_shader_objects` | The registration name is formed in the order discard mode, `_tess`, `_geom`, `_shader_objects`. | [registration loop](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsXfbTestsExt.cpp#L889-L905) |

Every variant uses two generated draws, two triangles per draw, three output vertices per triangle, an 8 x 8 `VK_FORMAT_R8G8B8A8_UNORM` target, and a single draw token in the DGC layout.

## Behavior Parameters

The primary behavioral axis is the registered variant family. The following groups describe how the exact names change the tested mechanism.

### Any `discard` variant: capture without first-draw rasterization

The first draw uses `rasterizerDiscardEnable`. It still runs the pre-rasterization stages and writes transform-feedback output, but it has no capture color image and the conventional capture pipeline omits the fragment shader. The later indirect draw remains rasterized and supplies the checked color result.

### Any `nodiscard` variant: capture with first-draw rasterization

The first draw uses the capture color attachment and fragment shader as well as transform feedback. The test compares that image and the later indirect-draw image with the same blue reference. This makes rasterization during the capture draw observable in addition to the captured vertex data.

### Any `_tess` or `_tess_geom` variant: patch-list capture

The host supplies two three-vertex patches. The tessellation control shader emits three control points and unit tessellation levels, and the tessellation evaluation shader interpolates the patch. The indirect draw uses patch-list topology. With `_geom`, the geometry shader then emits the three vertices of each triangle, and geometry owns the `xfb` declaration.

### Any `_geom` variant without `_tess`: triangle-strip capture through geometry

The host supplies two four-vertex triangle strips. The geometry shader passes each assembled triangle through as a three-vertex triangle strip and owns the `xfb` declaration. The expected capture data expands each strip into two triangles.

### Any `_shader_objects` variant: shader-object state path

The test creates `VkShaderEXT` objects for the selected stages, declares their `nextStage` relationships, and binds them before each draw. `bindShaderObjectState` supplies the selected topology and rasterization state. The pipeline and shader-object paths must produce the same captured vertices and color images.

## Shader Analysis

The shader source is generated by `initPrograms`. One representative walkthrough covers the basic `nodiscard` path. Tessellation, geometry, and shader-object changes are summarized in the parameter variation table rather than repeated as separate shader listings.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.dgc.ext.graphics.xfb.nodiscard
```

| Parameter choice | Meaning in this representative case |
|------------------|--------------------------------------|
| `discardXFB = false` | The first draw rasterizes, so the capture color image is checked. |
| `useGeom = false`, `useTess = false` | The vertex shader is the last pre-rasterization stage and the input uses two triangle strips. |
| `useShaderObjects = false` | The case uses the two conventional graphics pipelines. |

#### Purpose

The vertex shader forwards the input position to `gl_Position` and marks that output for transform feedback. The fragment shader writes the constant blue color used by both reference images.

#### Structural Design

| Stage | Input or output role | Transform-feedback role |
|-------|----------------------|--------------------------|
| Vertex | Reads `inPos` and writes `gl_Position`. | Declares `gl_Position` with `xfb_buffer = 0` and `xfb_offset = 0`. |
| Fragment | Writes `outColor`. | Does not contribute to captured vertex data. |

#### Shader Code

##### Vertex shader

```glsl
#version 460
layout(xfb_buffer = 0, xfb_offset = 0) out gl_PerVertex {
    vec4 gl_Position;
};
layout (location=0) in vec4 inPos;
void main(void) {
    gl_Position = inPos;
}
```

##### Fragment shader

```glsl
#version 460
layout (location=0) out vec4 outColor;
void main(void) {
    outColor = vec4(0.0, 0.0, 1.0, 1.0);
}
```

#### Additional Info

- `initPrograms` emits the same shader text for the corresponding stage in every variant; optional stages add the stage-specific passthrough code.
- The `xfb` qualifier moves to tessellation evaluation or geometry when that stage becomes the last pre-rasterization stage.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|------------------------------------------|----------|
| `_tess` | Adds passthrough tessellation control and evaluation shaders; the evaluation shader owns the `xfb` declaration unless geometry is also enabled. | [tessellation shader generation](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsXfbTestsExt.cpp#L169-L210) |
| `_geom` | Adds a passthrough geometry shader that owns the `xfb` declaration and emits each input triangle. | [geometry shader generation](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsXfbTestsExt.cpp#L213-L233) |
| `_shader_objects` | Uses the same compiled stages as `VkShaderEXT` objects and binds them with explicit `nextStage` relationships. | [shader-object creation and binding](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsXfbTestsExt.cpp#L305-L366) |
| `discard` | The capture pipeline omits the fragment module and enables rasterizer discard. | [capture pipeline selection](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsXfbTestsExt.cpp#L572-L578) |

#### SPIR-V

##### Vertex shader

- Status: reconstructed from the representative GLSL source
- Source: `vktDGCGraphicsXfbTestsExt.cpp`, `initPrograms`
- Stage: Vertex shader
- Target SPIRV version: spirv1.0

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos; 0
; Bound: 1
; Schema: 0
```

</details>

## Runtime Execution and Result Checking

- The host creates an 8 x 8 framebuffer, an input vertex buffer, a transform-feedback buffer large enough for 12 `vec4` values, a 32-bit counter buffer, and the color targets. It writes two half-screen quads to the input buffer. Non-tessellation cases use four vertices per draw as triangle strips; tessellation cases use six vertices per draw as two three-vertex patches.
- The DGC layout contains one `VK_INDIRECT_COMMANDS_TOKEN_TYPE_DRAW_EXT` token. The generated stream contains two `VkDrawIndirectCommand` records. Each record has the selected per-draw vertex count, `instanceCount = 1`, the first vertex for its quad, and `firstInstance = 0`.
- The host clears the color images, begins the first render pass or dynamic-rendering instance, binds the selected pipeline or shader objects, binds the transform-feedback buffer, and calls `cmdBeginTransformFeedbackEXT`.
- DGC executes the two generated draws. Transform feedback captures `gl_Position` and updates the counter. The test ends transform feedback before leaving the first render pass or rendering instance.
- A memory barrier makes transform-feedback counter writes visible to indirect reads and transform-feedback vertex writes visible to vertex input. The second rendering instance binds the captured buffer as its vertex buffer and calls `cmdDrawIndirectByteCountEXT` with a `vec4` stride.
- The host copies each color image and waits for completion. For `nodiscard`, it compares both the capture-draw and indirect-draw images. For `discard`, it compares only the indirect-draw image because the capture image does not exist.
- The reference image is blue `(0.0, 0.0, 1.0, 1.0)` across the 8 x 8 target because the two half-screen quads cover the full framebuffer. `tcu::floatThresholdCompare` uses a zero threshold for every channel.
- The host copies the transform-feedback buffer and compares four output triangles. For strips it builds the expected triangle list as `(0,1,2)`, `(2,1,3)` for each quad. For patches it copies the six input vertices directly. `verifyTriangle` compares each triangle as a set, so captured vertex order within a triangle may differ.
- Any color or vertex mismatch sets `fail` and returns `Unexpected result in color buffers or vertex buffers; check log for details`. A matching case returns `Pass`.

## Failure Meaning

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

**Possible failure symptoms:** The captured buffer contains an incorrect position, an incomplete triangle, extra vertices, or a counter value that makes the indirect draw render the wrong amount of geometry. The second color comparison can fail even when the first image passes.

**Possible implementation causes:** The implementation may mishandle `cmdBindTransformFeedbackBuffersEXT`, `cmdBeginTransformFeedbackEXT`, `cmdEndTransformFeedbackEXT`, the selected `xfb` output, or the counter consumed by `cmdDrawIndirectByteCountEXT`. The source and transform-feedback valid-usage chapters establish these operations and their ordering. The failing buffer and image entries are needed to separate them.

#### DGC draw stream and indirect execution

**Possible failure symptoms:** One quad is missing, both quads are shifted, or the capture and indirect images disagree while the stage configuration remains valid.

**Possible implementation causes:** The implementation may read the DGC device address, vertex count, or first-vertex fields incorrectly, or execute one of the two generated draws with incorrect state. The source identifies the stream contents and draw token; a precise implementation-layer cause needs further investigation.

#### Tessellation and geometry stage chain

**Possible failure symptoms:** Tessellation cases produce wrong positions or triangle counts. Geometry cases can omit output or change triangle boundaries. The host triangle comparison reports the affected output triangle.

**Possible implementation causes:** The implementation may connect stages incorrectly, select the wrong last pre-rasterization stage for transform feedback, mishandle patch-list input, or lower a passthrough tessellation or geometry shader incorrectly. The source does not identify a specific driver, compiler, or hardware layer.

#### Rasterizer discard and color results

**Possible failure symptoms:** A `nodiscard` case can fail in the first image while captured vertices pass, or the second image can fail after capture. A discard case can fail in its indirect-draw image.

**Possible implementation causes:** The selected pipeline or shader-object rasterization state may not apply `rasterizerDiscardEnable` consistently. A failure limited to the first color image can also involve the capture attachment setup or copyback. Source inspection is needed to distinguish state application from image handling.

#### Shader-object graphics state

**Possible failure symptoms:** Only `_shader_objects` variants fail, with color or captured-position differences while the corresponding pipeline variant passes.

**Possible implementation causes:** The implementation may create or bind a shader object with an incorrect stage chain, fail to bind null handles for unused optional stages, or apply the wrong topology or rasterization state between the two draws. The source establishes the differing state path but not the faulty implementation layer.

## Case Pruning

### Requirement-based pruning

- `checkDGCExtSupport` requires the EXT device-generated-command support for the selected graphics stages and transform feedback. `transformFeedback` and `transformFeedbackDraw` must be supported.
- `_shader_objects` variants require `VK_EXT_shader_object`.
- `_geom` variants require `DEVICE_CORE_FEATURE_GEOMETRY_SHADER`.
- `_tess` variants require `DEVICE_CORE_FEATURE_TESSELLATION_SHADER`.
- Unsupported feature or property requirements raise `NotSupportedError`, so the case is skipped rather than reported as a rendering failure.

### Design-based pruning

- The registration matrix contains all 16 combinations of the four booleans. No combination is removed by the registration loop.
- The source uses two draws and two triangles per draw for every variant. It does not add a separate zero-count or alternate capture-size family.
- The capture color image is intentionally absent for `discard` variants. This is a design choice, not a missing result check.

## Key Takeaways

- DGC supplies the two capture draws, while transform feedback carries their pre-rasterization positions into a later byte-count indirect draw.
- `discard` changes only rasterization visibility for the first draw. It does not disable transform-feedback capture.
- Tessellation changes the input topology and capture stage. Geometry changes the final pre-rasterization stage. Both paths must preserve the same four output triangles.
- Pipeline and shader-object variants exercise different graphics-state binding paths but share the same captured vertices and color references.
- The test checks both rendered pixels and captured triangle data. A failure identifies a mismatch in one of the exercised command, stage, state, synchronization, resource, or result-checking paths.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `Params` and `checkSupport` | [parameters and requirements](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsXfbTestsExt.cpp#L54-L127) | Defines the four switches and support gates. |
| `initPrograms` | [generated shaders](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsXfbTestsExt.cpp#L134-L234) | Defines stage-specific `xfb` placement and passthrough shader behavior. |
| `bindShaders` and `makeShader` | [shader-object binding](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsXfbTestsExt.cpp#L236-L366) | Defines selected stage handles and `nextStage` relationships. |
| Pipeline and framebuffer setup | [capture and indirect graphics state](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsXfbTestsExt.cpp#L441-L586) | Separates capture rasterization state from the later draw state. |
| DGC layout and stream | [generated draw records](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsXfbTestsExt.cpp#L589-L619) | Defines the draw token and two `VkDrawIndirectCommand` records. |
| Transform-feedback capture | [capture commands and barrier](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsXfbTestsExt.cpp#L673-L743) | Defines buffer binding, begin/end, DGC execution, and visibility dependencies. |
| Indirect draw and copyback | [second draw](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsXfbTestsExt.cpp#L745-L781) | Defines byte-count drawing and color readback. |
| Result checking | [color and vertex validation](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsXfbTestsExt.cpp#L783-L878) | Defines reference images, triangle comparison, and pass/fail. |
| Registration | [exact direct-child names](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsXfbTestsExt.cpp#L883-L907) | Defines all 16 registered variants. |
| Transform-feedback valid usage | [bind](../../../../vulkan-docs/src/chapters/commonvalidity/xform_feedback_bind_common.adoc), [begin](../../../../vulkan-docs/src/chapters/commonvalidity/xform_feedback_begin_common.adoc), [draw](../../../../vulkan-docs/src/chapters/commonvalidity/xform_feedback_draw_common.adoc), [end](../../../../vulkan-docs/src/chapters/commonvalidity/xform_feedback_end_common.adoc) | Grounds feature, command-order, counter, and stride requirements. |
