# Understanding Brief: shader_object.pipeline_interaction / vktShaderObjectPipelineInteractionTests.cpp

This brief prepares the Level-3 rewrite of the shader object pipeline interaction test family. It treats the CTS source,
the mustpass registration, and the Vulkan spec as the authorities. The local checkout does not vendor
`external/vulkan-docs`, so spec semantics below were checked against the current Vulkan specification sources for
`vkCmdBindShadersEXT`, `vkCmdBindPipeline`, the shader objects chapter, and the common drawing-command validity rules
(VUID-vkCmdDraw-None-08876, VUID-vkCmdDraw-renderPass-06198, VUID-vkCmdDraw-None-08684 through -08696,
VUID-vkCmdDraw-None-07630).

## One-Sentence Test Purpose

This test checks whether a command buffer can legally switch between bound graphics or compute pipelines and bound
shader objects, in both directions and in mixed sequences, while every draw and dispatch still produces the correct
output.

Core question: **when a command buffer draws or dispatches through pipelines and shader objects in alternation, does
the implementation honor the spec rules that disturb the previous binding when the other object type is bound, and does
each draw still render or write the exact expected result?**

## Background Knowledge

### Binding disturbance between pipelines and shader objects

The spec gives pipelines and shader objects mutually disturbing binding state on a command buffer. Calling
`vkCmdBindShadersEXT` disturbs the pipeline bind points for the stages in `pStages`, so any pipeline previously bound to
those bind points is no longer bound. If the graphics bind point is disturbed, every graphics pipeline state the
previously bound pipeline did not specify as dynamic becomes undefined and must be set in the command buffer before the
next draw that uses shader objects. The rule is symmetric: calling `vkCmdBindPipeline` disturbs the shader stages of
that bind point, so previously bound shader objects are no longer bound, even when the pipeline was created without
shaders for some of those stages.

Why it matters here:

- Every sequencing case in this test is a chain of `cmdBindPipeline` and `cmdBindShadersEXT` calls separated by draws.
  The test's pass condition is exactly the spec's disturbance rule: the draw after each switch must use the most
  recently bound object, with its state correctly assembled.
- After a pipeline-to-shader-object switch, the test re-issues the full default dynamic state set
  ([setDefaultShaderObjectDynamicStates](../../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.cpp#L244-L418))
  because the previous pipeline's static state is now undefined. After a shader-object-to-pipeline switch, no re-issue
  happens, because the newly bound pipeline supplies its own state.

### Drawing with shader objects requires dynamic rendering and set dynamic state

Two draw-time rules shape every graphics path in this test. First, if a shader object is bound to any graphics stage,
the current render pass instance must have been begun with `vkCmdBeginRendering` (VUID-vkCmdDraw-None-08876). Second,
the common drawing validity rules apply their dynamic-state requirements whenever "a shader object is bound to any
graphics stage", the same as if every one of those dynamic states were enabled in a bound pipeline, so the applicable
`vkCmdSet*` calls must have been recorded before the draw. When the device supports the `geometryStreams` feature and a
geometry shader object is bound, `vkCmdSetRasterizationStreamEXT` must also have been called and not subsequently
invalidated (VUID-vkCmdDraw-None-07630); the test source annotates its rasterization stream call with exactly this
VUID ([call site](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L621-L642)).

Why it matters here:

- All graphics draws happen inside one dynamic rendering instance over a 32x32 attachment; no legacy render pass
  instance is ever begun.
- A separate rule (VUID-vkCmdDraw-renderPass-06198) says that when the current render pass instance was begun with
  `vkCmdBeginRendering`, the bound graphics pipeline must have been created with `renderPass = VK_NULL_HANDLE`. The
  two `render_pass_pipeline_shader_object*` cases exploit the disturbance rule to stay on the legal side of this
  boundary: they bind a pipeline created against a legacy `VkRenderPass`, then bind graphics shader objects, which
  disturbs the pipeline binding so the draw proceeds with shader objects only and no bound pipeline remains to violate
  the rule.

### Stage coverage and unbinding

When no graphics pipeline is bound, `vkCmdBindShadersEXT` must have been called at least once with every
feature-enabled graphics stage in `pStages` (VUID-vkCmdDraw-None-08684 through -08690): vertex and fragment always,
both tessellation stages when the `tessellationShader` feature is enabled, geometry when `geometryShader` is enabled,
task and mesh when their features are enabled. A `VK_NULL_HANDLE` entry unbinds a stage, so a draw can run with a
subset of stages by binding the missing stages as null handles. Vertex and mesh are mutually exclusive
(VUID-vkCmdDraw-None-08693, -08696).

Why it matters here:

- The helper `bindGraphicsShaders` always issues one `cmdBindShadersEXT` call covering all five classic graphics
  stages, passing `VK_NULL_HANDLE` for stages that should not run
  ([helper](../../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.cpp#L420-L447)).
- The eight stage-binding cases are exactly the subsets of {tessellation, geometry, fragment} over an always-bound
  vertex stage, drawn after a pipeline draw, so they test partial stage sets across a pipeline-to-shader-object
  switch.

## One Concrete Example

Conceptual walk-through of `dEQP-VK.shader_object.pipeline_interaction.max_pipeline_shader_object_max_pipeline`
(reconstructed from
[ShaderObjectPipelineInteractionInstance::iterate()](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L621-L642)):

1. The instance creates three max-dynamic graphics pipelines from shader modules (vert1/frag1, vert2/frag2,
   vert3/frag3 plus shared tesc/tese/geom), ten unlinked shader objects covering the same stages, and a compute
   pipeline. "Max" here means the pipeline is created with the largest set of dynamic states the device supports and
   with viewport and scissor counts of zero, so those values come from `cmdSetViewportWithCount` and
   `cmdSetScissorWithCount` at draw time.
2. The command buffer transitions the color image, begins a dynamic rendering instance, records the default dynamic
   state set, binds null task and mesh shaders when supported, and binds a 64-byte vertex buffer even though no vertex
   input state exists (the shaders read `gl_VertexIndex` only).
3. It binds pipeline1 and draws 4 vertices. The draw renders the red upper-left quadrant: vert1 places a quarter-size
   quad there, tessellation evaluation doubles its x extent, and the geometry shader doubles its y extent.
4. It records `cmdSetRasterizationStreamEXT(0)` (guarded on conservative rasterization support, annotated
   VUID-vkCmdDraw-None-07630), then binds the vert2/frag2 shader objects with tesc/tese/geom. This binding disturbs
   the graphics pipeline bind point, so pipeline1 is no longer bound and its static state is undefined.
5. It re-issues the full default dynamic state set and draws 4 vertices again. This draw renders the green upper-right
   quadrant using only shader objects.
6. It binds pipeline3 and draws 4 vertices a third time, rendering the blue lower-left quadrant. No dynamic state
   re-issue is needed because pipeline3 is a max-dynamic pipeline whose dynamic values were set in step 5, and its
   static values (topology, patch control points, vertex input) overwrite the command buffer state at bind time.
7. After submission, the image is copied to a host-visible buffer and the host requires red in the upper-left
   quadrant, green in the upper-right, and blue in the lower-left, one quadrant per draw.

## End-to-End Test Flow

```text
[host] create image (32x32 R8G8B8A8_UNORM), color readback buffer, descriptor set with
       storage buffer (compute / per-stage writes), command buffers
[host] create 10 unlinked shader objects (vert1..3, tesc, tese, geom, frag1..3, comp) and
       matching shader modules; build 3 graphics pipelines plus 1 compute pipeline
[host] record the main command buffer:
       image barrier, optional early pipeline bind (render_pass_pipeline_shader_object),
       beginRendering, default dynamic states, null task/mesh binds, vertex buffer bind,
       then the per-type sequence of cmdBindPipeline / bindGraphicsShaders / draw calls,
       re-issuing default dynamic states after each pipeline-to-shader-object switch,
       endRendering; compute cases dispatch outside the rendering instance
[device] each draw runs vert -> tess -> geom -> frag and fills one image quadrant
       (draw 1 red upper-left, draw 2 green upper-right, draw 3 blue lower-left);
       compute cases write gl_LocalInvocationID.x into a storage buffer
[host] submit, then copy the image to the readback buffer in a second command buffer
[host] verifyImage against the draw count; compute cases also invalidate and scan the
       storage buffer and require entries 0..3 to equal their own index
```

The stage-binding instance follows a shorter flow: beginRendering, one pipeline draw whose static viewport
(32, 0, 32, 32) lies entirely outside the 32x32 image so it writes nothing, bind descriptor set and default dynamic
states, bind the selected stage subset with null handles for the rest, draw, endRendering; then copyback plus image
and buffer checks
([stage-binding iterate()](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L991-L1264)).

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- Inline GLSL, compiled to SPIR-V by the CTS program build: `vert1`, `vert2`, `vert3` (place the quarter quad in the
  upper-left, upper-right, lower-left quadrant), shared `tesc` (all tessellation levels 1.0), `tese` (quad
  interpolation, x scaled by 2), `geom` (y scaled by 2), `frag1`/`frag2`/`frag3` (red, green, blue), and `comp`
  (writes `gl_LocalInvocationID.x` into a 16-entry storage buffer)
  ([sequencing programs](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L842-L952)).
- The stage-binding cases generate two parallel program sets: shader-object variants `vert`, `tesc`, `tese`, `geom`,
  `frag` that also write `1`, `2`, `3` into a storage buffer from vertex, tessellation control, and geometry,
  and pipeline variants `pipeline_vert`, `pipeline_tesc`, `pipeline_tese` (x and y scaled by 0.5), `pipeline_geom`
  (shifted by 0.25), `pipeline_frag` (red)
  ([stage-binding programs](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L1335-L1502)).
- Pipelines: three graphics pipelines plus one compute pipeline for the sequencing instance; one graphics pipeline for
  the stage-binding instance. Graphics pipelines are created either against dynamic rendering
  (`VkPipelineRenderingCreateInfo`) or against a legacy `VkRenderPass` for the two `render_pass_pipeline_shader_object*`
  cases, and with a maximal dynamic state list or with fully static state ("max" vs "min" pipelines)
  ([pipeline selection](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L307-L321),
  [creation](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L555-L574)).
- A `VkRenderPass` and `VkFramebuffer` are created solely so the two render-pass cases can create pipelines against
  the legacy render pass; the framebuffer is never used for rendering.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| 32x32 `R8G8B8A8_UNORM` color attachment + view | yes | yes (rendering attachment) | written by fragment shaders, cleared to black | yes, via copy to buffer | Carries the per-draw quadrant colors that the image check verifies |
| Host-visible color output buffer | yes | yes (transfer dst) | written by `cmdCopyImageToBuffer` | yes | Copyback target for the quadrant check |
| Storage buffer (16 uints, sequencing) + descriptor set | yes | yes (compute descriptor binding) | written by the compute shader object or compute pipeline | yes, host-visible | Verification channel for the two compute interaction cases |
| Storage buffer (4 uints, stage-binding) + descriptor set | yes | yes (graphics descriptor binding) | written by vertex, tessellation control, and geometry shader objects | yes, host-visible | Verification channel for per-stage execution in the stage-binding cases |
| 64-byte vertex buffer | yes | yes (`cmdBindVertexBuffers2`) | no (no vertex input state; shaders use `gl_VertexIndex`) | no | Exercises vertex buffer binding alongside shader objects without supplying attributes |

## What Is Checked

- Sequencing cases: after submission, the image must hold red in the upper-left quadrant when the draw count exceeds
  zero, green in the upper-right when it exceeds one, and blue in the lower-left when it exceeds two, with exact color
  comparison ([verifyImage](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L780-L817)).
  The draw count comes from the test type
  ([getDrawCount](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L102-L128)): 1 for
  the single-draw and compute cases, 2 for the two-draw switches, 3 for the two triple sequences. The lower-right
  quadrant stays at the clear color and is not checked.
- Compute interaction cases also invalidate the storage buffer and require entries 0 through 3 to equal their
  own index ([compute check](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L763-L775)).
- Stage-binding cases: when the fragment shader object is bound, the image must be white inside a centered rectangle
  and black outside it, where the x border is 4 pixels when tessellation is bound and 8 otherwise, and the y border is
  4 pixels when geometry is bound and 8 otherwise, matching the x1.5 / y1.5 scaling those stages apply; when fragment
  is not bound, the image is not checked. The storage buffer must hold 1 when the vertex stage is bound, 2 when
  tessellation control is bound, and 3 when geometry is bound
  ([stage-binding checks](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L1225-L1263)).
- Binding and dispatch sequences are implicit checks: an implementation that rejects a legal switch, unbinds the wrong
  object, or enforces render pass compatibility at bind time fails the case through validation layers or a returned
  error before any output exists.
- All comparisons are exact host-side checks after copyback; there is no tolerance.

## Behavior Parameter Identification

> **Behavior parameter:** behavioral group over the 18 registered test case leaves (the family has no intermediate
> nodes; all 18 leaves are direct children of `shader_object.pipeline_interaction`).
>
> **Primary axis candidate values:** single-binding baselines (`shader_object`, `max_pipeline`), pipeline and
> shader-object interleaving (`max_pipeline_shader_object_max_pipeline`, `shader_object_max_pipeline_shader_object`,
> `min_pipeline_shader_object`, `shader_object_min_pipeline`), render-pass pipeline mixes
> (`render_pass_pipeline_shader_object`, `render_pass_pipeline_shader_object_after_begin`), compute interactions
> (`compute_shader_object_min_pipeline`, `shader_object_compute_pipeline`), stage-binding subsets (`vert`, `vert_tess`,
> `vert_geom`, `vert_frag`, `vert_tess_geom`, `vert_tess_frag`, `vert_geom_frag`, `vert_tess_geom_frag`).
>
> **Secondary axis (inside the stage-binding group):** the on/off presence of tessellation, geometry, and fragment
> stages over an always-bound vertex stage, a full 2x2x2 cross product.

## What Failure Means

### Failure Cause Mapping

Primary axis (behavioral group):

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| Single-binding baselines (`shader_object`, `max_pipeline`) | Shader-object drawing or max-dynamic pipeline drawing fails on its own: required dynamic states missing, or basic pipeline draw broken. |
| Pipeline and shader-object interleaving (4 leaves) | Binding disturbance mishandled: the implementation keeps using the previous object after a switch, or loses non-dynamic state that must be re-supplied dynamically. |
| Render-pass pipeline mixes (2 leaves) | Legacy-render-pass pipeline binding mishandled around a dynamic rendering instance, or the pipeline binding not properly disturbed by the subsequent shader-object binding. |
| Compute interactions (2 leaves) | Compute shader object dispatch or compute pipeline dispatch mishandled after the other object type was used, producing wrong storage buffer contents. |
| Stage-binding subsets (8 leaves) | Partial stage binding mishandled: null-unbound stages still run, feature-gated stages not bound as required, or a selected stage fails to execute. |

Secondary axis (stage presence inside the stage-binding group):

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| tessellation present (`vert_tess*`) | Tessellation stage pair not executed or misconfigured after the switch (patch topology, control points, or domain scaling wrong). |
| geometry present (`vert_geom*`) | Geometry stage not executed or its y scaling wrong after the switch. |
| fragment present (`vert_frag*`, and the `*_frag` mixtures) | Fragment stage not executed, so the image stays at the clear color instead of the white rectangle. |
| fragment absent (`vert`, `vert_tess`, `vert_geom`, `vert_tess_geom`) | Pre-fragment stages or the no-fragment draw path mishandled; only the storage buffer side effects can fail. |

All cases share the same verification mechanisms (exact image region compare and exact storage buffer compare), so a
failure in any case is observed as a pixel or buffer mismatch, or as a validation error before any output exists.

## Important Variations and Special Cases

- **Max versus min pipelines.** The interleaving cases pair shader objects with two pipeline flavors. A max pipeline
  carries the largest supported dynamic state list and zero viewport/scissor counts; a min pipeline carries no dynamic
  states at all, so switching from it to shader objects invalidates every piece of pipeline state. The four interleaved
  leaves cover both directions with both flavors: max-pipeline-to-shader-to-max-pipeline,
  shader-to-max-pipeline-to-shader, min-pipeline-to-shader, and shader-to-min-pipeline.
- **Render-pass pipeline placement.** The two render-pass cases bind the legacy-render-pass pipeline in two positions:
  before `vkCmdBeginRendering` and after it, inside the dynamic render pass instance. Both must remain legal because
  pipeline binding itself has no render pass scope, and the subsequent shader-object binding disturbs the pipeline
  before any draw.
- **Compute order.** `compute_shader_object_min_pipeline` dispatches with a compute shader object first and then draws
  with a min pipeline; `shader_object_compute_pipeline` draws with graphics shader objects first and then dispatches
  with a compute pipeline. Both dispatches happen outside the render pass instance.
- **Invisible pipeline draw in the stage-binding cases.** The stage-binding pipeline is created with a static viewport
  at (32, 0), entirely outside the 32x32 image, so its draw covers no pixels and writes no buffer entries. The draw
  exists so a real pipeline draw precedes the shader-object binding, and the image check then sees only the
  shader-object draw.
- **Rasterization stream re-issue.** Inside the two triple sequences, the test records an extra
  `cmdSetRasterizationStreamEXT(0)` between draws, guarded on conservative rasterization support and annotated
  VUID-vkCmdDraw-None-07630, to keep the rasterization stream state defined across the pipeline-to-shader-object
  transition.
- **Source quirk: repeated `local_size_x`.** The compute shader declares
  `layout(local_size_x=16, local_size_x=1, local_size_x=1)`, repeating `local_size_x` where `local_size_y` and
  `local_size_z` were intended ([comp program](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L933-L940)).
  The CTS shader compiler accepts it and emits `LocalSize 16 1 1` (first value wins), so the four dispatched workgroups
  of 16 invocations write entries 0 through 15 and the check of entries 0 through 3 succeeds. The same pattern exists
  in the shared `addBasicShaderObjectShaders` set. This is an unresolved source-level concern; per audit rules the
  source is not modified and this page only states the observed behavior.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Test type enum and draw counts | [vktShaderObjectPipelineInteractionTests.cpp#L45-L57](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L45-L57), [getDrawCount](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L102-L128) | The ten sequencing leaves and their expected draw counts. |
| Sequencing instance | [iterate()](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L135-L778) | Resource setup, per-type bind/draw sequences, copyback, and checks. |
| Sequencing programs | [initPrograms](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L842-L952) | The ten GLSL programs including the quadrant vertex shaders and the storage-buffer compute shader. |
| Sequencing support check | [checkSupport](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L954-L960) | Extension plus tessellation and geometry feature gates. |
| Stage-binding instance | [iterate()](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L991-L1264) | Pipeline draw, subset binding, draw, and both checks. |
| Stage-binding programs | [initPrograms](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L1335-L1502) | The shader-object variants with storage writes and the shifted pipeline variants. |
| Stage-binding support check | [checkSupport](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L1324-L1333) | Extension gate plus per-stage feature gates. |
| Registration | [createShaderObjectPipelineInteractionTests](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L1506-L1553) | The ten sequencing and eight stage-binding leaves under `pipeline_interaction`. |
| Shared helpers | [vktShaderObjectCreateUtil.cpp#L244-L489](../../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.cpp#L244-L489) | `setDefaultShaderObjectDynamicStates`, `bindGraphicsShaders`, null task/mesh binding. |
| Mustpass evidence | [pipeline-interaction.txt](../../../mustpass/main/vk-default/shader-object/pipeline-interaction.txt) | All 18 registered `dEQP-VK.shader_object.pipeline_interaction.*` case paths. |

## Questions / Risk Points for User Audit

- Is the five-group behavioral cluster the right primary axis (baselines, interleaving, render-pass mixes, compute
  interactions, stage-binding subsets), with stage presence as the secondary axis inside the last group, rather than
  treating all 18 leaves individually?
- Spec grounding came from the current official Vulkan specification sources (the `external/vulkan-docs` tree is not
  vendored in this checkout). The load-bearing rules are the pipeline/shader-object disturbance rules, the
  dynamic-rendering requirement for shader-object draws (VUID-vkCmdDraw-None-08876), the renderPass-null requirement
  in dynamic rendering (VUID-vkCmdDraw-renderPass-06198), and the stage coverage rules (VUID-vkCmdDraw-None-08684
  through -08696). Are these consistent with the intended pinned spec revision?
- The compute shader's repeated `local_size_x` layout qualifier is reported above as an unresolved source-level
  concern (the shader runs in this family, unlike in `create` where it never executes). Confirm the wiki should state
  the observed first-wins behavior rather than flag it as a defect in the page body.
- The shaders are trivial quadrant painters and index writers, and the tested behavior is binding-mode switching, so
  the plan is a no-walkthrough `## Shader Analysis` with a `walkthrough_exceptions.py` entry. Confirm this matches the
  lead's pre-approval.
- The extra `cmdSetRasterizationStreamEXT(0)` call is guarded on conservative rasterization support while the cited
  VUID-vkCmdDraw-None-07630 condition tracks the `geometryStreams` feature and a bound geometry shader object. The
  page states the call and its VUID annotation factually without explaining the guard; is that depth sufficient?

## Conversion Notes for Final Wiki Rewrite

- Distill the three Background Knowledge topics (binding disturbance, dynamic rendering and dynamic state
  requirements, stage coverage and unbinding) into a short prerequisite bullet list; keep the VUID-grounded statements
  and drop tutorial padding.
- The concrete example becomes prose support inside `## Behavior Parameters` and
  `## Runtime Execution and Result Checking`; no shader walkthrough is planned.
- Copy the two failure-cause tables directly into `## Failure Meaning` -> `### Failure Cause Mapping`; write
  `### Cause Analysis` fresh during the rewrite.
- Feature requirements go to `### Requirement-based pruning`; the max/min pipeline distinction, the invisible pipeline
  draw, and the compute ordering go into the page body and `### Design-based pruning` where they fit.
- Keep the mustpass-backed tree (18 direct children under `shader_object.pipeline_interaction`) as the
  `## Registration Hierarchy` fence, and cite `pipeline-interaction.txt` plus the wildcard `main.txt` and
  `excluded-tests.txt` for coverage.
