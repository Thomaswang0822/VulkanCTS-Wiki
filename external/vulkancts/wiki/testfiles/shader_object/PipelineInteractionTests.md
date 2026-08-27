## Overview

**Core question:** When one command buffer draws and dispatches through bound pipelines and bound shader objects in
alternation, does the implementation unbind the previous object type at each switch and still produce the exact
expected output from every draw and dispatch?

- [vktShaderObjectPipelineInteractionTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp) implements the whole `shader_object.pipeline_interaction` test family: ten sequencing test case leaves that interleave graphics pipelines, graphics shader objects, render-pass pipelines, and compute work, plus eight stage-binding test case leaves that draw with partial graphics stage sets, 18 registered cases in total.
- The sequencing leaves cover both switch directions: pipeline draws followed by shader-object draws and back again. The pipelines involved carry either a maximal dynamic state list or fully static state. Two more leaves bind graphics pipelines created against a legacy `VkRenderPass` around a dynamic-rendering shader-object draw, and two leaves alternate a compute shader object with a compute pipeline.
- The stage-binding leaves bind every subset of tessellation, geometry, and fragment over an always-bound vertex stage after a pipeline draw, with `VK_NULL_HANDLE` for the stages that must not run.
- Verification is host-side and exact: each draw must fill one image quadrant with a specific color, compute dispatches must fill a storage buffer with per-invocation index values, and the stage-binding cases check per-stage buffer writes of `1`, `2`, and `3` from the selected stages.

## Background Knowledge

For the shared concepts shader objects, per-stage binding, dynamic state, and dynamic rendering, see [Background Knowledge](../../categories/shader_object.md#background-knowledge) of the `shader_object` page.

- **Binding disturbance between pipelines and shader objects.** The spec makes the two object types disturb each other's binding state on a command buffer. `vkCmdBindShadersEXT` disturbs the pipeline bind points for the stages in `pStages`, so a previously bound pipeline is no longer bound; when the graphics bind point is disturbed, every graphics pipeline state the previous pipeline did not specify as dynamic becomes undefined and must be set in the command buffer before drawing with shader objects. `vkCmdBindPipeline` disturbs the corresponding shader stages, so previously bound shader objects are no longer bound, even if the pipeline was created without shaders for some of those stages. Every case in this family is a chain of these two commands separated by draws.
- **Shader-object draws require dynamic rendering and set dynamic state.** If a shader object is bound to any graphics stage, the current render pass instance must have been begun with `vkCmdBeginRendering` (VUID-vkCmdDraw-None-08876), and the common drawing validity rules demand their `vkCmdSet*` calls as if every one of those dynamic states were enabled. With the `geometryStreams` feature and a bound geometry shader object, `vkCmdSetRasterizationStreamEXT` must also have been called and not subsequently invalidated (VUID-vkCmdDraw-None-07630). Separately, a draw inside a dynamic render pass instance requires its bound pipeline to have been created with `renderPass = VK_NULL_HANDLE` (VUID-vkCmdDraw-renderPass-06198); the render-pass cases in this family stay legal because binding shader objects to all graphics stages disturbs the legacy pipeline binding before the draw.
- **Stage coverage and null unbinding.** When no graphics pipeline is bound, `vkCmdBindShadersEXT` must have been called at least once with every feature-enabled graphics stage in `pStages` (VUID-vkCmdDraw-None-08684 through -08690), and a `VK_NULL_HANDLE` entry unbinds a stage. Vertex and mesh stages are mutually exclusive at draw time. The helper `bindGraphicsShaders` always covers all five classic graphics stages in one call, passing null handles for stages that should not run.

## Registration Hierarchy

```text
shader_object.pipeline_interaction
├── shader_object
├── max_pipeline
├── max_pipeline_shader_object_max_pipeline
├── shader_object_max_pipeline_shader_object
├── min_pipeline_shader_object
├── shader_object_min_pipeline
├── render_pass_pipeline_shader_object
├── render_pass_pipeline_shader_object_after_begin
├── compute_shader_object_min_pipeline
├── shader_object_compute_pipeline
├── vert
├── vert_tess
├── vert_geom
├── vert_frag
├── vert_tess_geom
├── vert_tess_frag
├── vert_geom_frag
└── vert_tess_geom_frag
```

The ten sequencing leaves come from the `tests[]` table and the eight stage-binding leaves from the `shaderBindTests[]`
table in [createShaderObjectPipelineInteractionTests()](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L1506-L1553);
the family has no intermediate nodes. All 18 leaves appear in the mustpass set
[pipeline-interaction.txt](../../../mustpass/main/vk-default/shader-object/pipeline-interaction.txt), which
[vk-default.txt](../../../mustpass/main/vk-default.txt) includes as a fragment. The source mustpass entry is the
wildcard `dEQP-VK.*` [main.txt](../../../mustpass/main/src/main.txt), and the only `shader_object` exclusion covers
`performance`, not `pipeline_interaction` [excluded-tests.txt](../../../mustpass/main/src/excluded-tests.txt).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Interaction type | `shader_object`, `max_pipeline`, `max_pipeline_shader_object_max_pipeline`, `shader_object_max_pipeline_shader_object`, `min_pipeline_shader_object`, `shader_object_min_pipeline`, `render_pass_pipeline_shader_object`, `render_pass_pipeline_shader_object_after_begin`, `compute_shader_object_min_pipeline`, `shader_object_compute_pipeline` | Selects the exact order of `cmdBindPipeline`, `cmdBindShadersEXT`, draw, and dispatch calls recorded into one command buffer. | [tests table](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L1510-L1533) |
| Pipeline dynamic-state flavor | max, min (source constant) | A max pipeline is created with the largest dynamic state list the device supports and viewport and scissor counts of zero; a min pipeline is fully static, including one viewport covering the render area. The flavor decides how much state survives or must be re-supplied across a switch. | [flavor selection](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L307-L321) |
| Expected draw count | 1, 2, or 3 per test type | Gates the quadrant check: red upper-left for the first draw, green upper-right for the second, blue lower-left for the third. | [getDrawCount()](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L102-L128) |
| Stage-binding booleans | `vertShader`, `tessShader`, `geomShader`, `fragShader` in `StageTestParams` | Choose which graphics stages receive a valid shader object; the rest are bound as `VK_NULL_HANDLE`. Vertex is always true. | [StageTestParams](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L64-L70) |
| Stage-binding names | `vert`, `vert_tess`, `vert_geom`, `vert_frag`, `vert_tess_geom`, `vert_tess_frag`, `vert_geom_frag`, `vert_tess_geom_frag` | The full 2x2x2 cross product of tessellation, geometry, and fragment presence over the always-bound vertex stage. | [shaderBindTests table](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L1535-L1550) |
| Compute dispatch shape | 4x1x1 workgroups of 16 invocations (source constant) | One dispatch of four 16-invocation workgroups fills storage buffer entries 0 through 15 with the compute shader object or the compute pipeline; the host checks entries 0 through 3. | [dispatch constants](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L529-L531) |

## Behavior Parameters

The primary behavioral axis is the **behavioral group** formed by the 18 test case leaves: five groups exercise
different parts of the pipeline and shader-object switching rules. A secondary axis, the presence of tessellation,
geometry, and fragment stages, applies inside the stage-binding group.

### Single-binding baselines: one object type only

`shader_object` binds the five graphics shader objects and draws once; `max_pipeline` binds one max-dynamic pipeline
and draws once ([SHADER_OBJECT and MAX_PIPELINE paths](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L610-L620)).
These leaves isolate each programming model on its own, so a failure here means basic shader-object drawing or basic
pipeline drawing is broken, with no switching involved. Both draws render the red upper-left quadrant, and their
expected draw count is 1.

### Pipeline and shader-object interleaving: switches in both directions

Four leaves chain draws through alternating binding states. `max_pipeline_shader_object_max_pipeline` draws with a max
pipeline, then with the vert2/frag2 shader objects, then with another max pipeline; `shader_object_max_pipeline_shader_object`
starts with shader objects, switches to a max pipeline, and switches back
([triple sequences](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L621-L665)).
`min_pipeline_shader_object` and `shader_object_min_pipeline` perform one switch each, in opposite directions, with a
fully static min pipeline ([switch sequences](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L666-L702)).
Each draw fills a different quadrant (red, green, then blue for the triples), so the image check attributes one
quadrant to each binding event; a switch that loses state or keeps the previous object's shaders produces a wrong or
missing quadrant. The interleaving group also varies the pipeline flavor, because a min pipeline invalidates all of
its state when disturbed while a max pipeline keeps its dynamic values alive.

### Render-pass pipeline mixes: legacy render pass pipelines around dynamic rendering

Both leaves create their graphics pipelines against a real `VkRenderPass` instead of a
`VkPipelineRenderingCreateInfo` ([render pass selection](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L546-L553)),
then bind one of those pipelines either before `vkCmdBeginRendering` or inside the dynamic render pass instance, bind
the graphics shader objects, and draw
([pipeline bound before begin](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L592-L595),
[draw sequences](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L678-L693)).
The shader-object binding disturbs the pipeline binding, so the draw runs with shader objects only and no bound
pipeline remains to violate the dynamic-rendering render pass rule. The two leaves differ only in where the
`cmdBindPipeline` call is recorded; both must render the red upper-left quadrant with draw count 1.

### Compute interactions: compute shader objects and compute pipelines

`compute_shader_object_min_pipeline` binds the compute descriptor set and the compute shader object, dispatches
outside the render pass, then begins rendering, draws with a min pipeline, and ends rendering; `shader_object_compute_pipeline`
reverses the order: it draws with the graphics shader objects inside the render pass, then binds the compute pipeline
and dispatches after rendering ends
([compute sequences](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L703-L732)).
The graphics draw renders the red upper-left quadrant, and the dispatch must fill storage buffer entries 0 through 3
with their own index values, so each leaf verifies that using one object type on a bind point does not break the
subsequent use of the other.

### Stage-binding subsets: partial graphics stage sets

The eight `vert*` leaves draw once with a graphics pipeline built from the matching shader modules (vertex and
fragment stages, plus tessellation and geometry when selected), then bind the
selected subset of shader objects, with null handles for tessellation control, tessellation evaluation, geometry, or
fragment as appropriate, and draw again
([subset binding](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L1211-L1217)).
The pipeline draw uses a static viewport at (32, 0) that lies entirely outside the 32x32 image, so it covers no
pixels; its role is to put a real pipeline draw before the switch. Each selected stage leaves a trace: the vertex,
tessellation control, and geometry shader objects write 1, 2, and 3 into a storage buffer, and the fragment shader
paints a white rectangle whose size reflects the tessellation and geometry scaling, as detailed in the secondary axis
below.

The secondary axis inside this group is the **stage presence**: tessellation, geometry, and fragment each on or off.

### Tessellation active: `vert_tess`, `vert_tess_geom`, `vert_tess_frag`, `vert_tess_geom_frag`

The draw uses a patch list with four control points, the tessellation control shader sets all inner and outer levels
to 1.0 so the quad tessellates once, and the tessellation evaluation shader scales x by 1.5. The expected white
rectangle therefore widens to an x border of 4 pixels instead of 8, and the storage buffer must contain 2 from the
tessellation control invocation.

### Geometry active: `vert_geom`, `vert_tess_geom`, `vert_geom_frag`, `vert_tess_geom_frag`

The geometry shader processes each incoming triangle, scales y by 1.5, and emits a triangle strip, so the white
rectangle deepens to a y border of 4 pixels instead of 8, and the storage buffer must contain 3 from geometry
invocation 0.

### Fragment active: `vert_frag`, `vert_tess_frag`, `vert_geom_frag`, `vert_tess_geom_frag`

The fragment shader outputs white, so the image check runs: white inside the centered rectangle computed from the
tessellation and geometry borders, black outside it. The draw must fill exactly that rectangle; a missing or
mis-scaled stage shows up as the wrong region or no white at all.

### Fragment inactive: `vert`, `vert_tess`, `vert_geom`, `vert_tess_geom`

The fragment stage is bound as `VK_NULL_HANDLE`, so the draw performs no fragment shading and the image is not
checked. Only the storage buffer writes prove that the selected pre-fragment stages executed after the switch.

## Shader Analysis

This page has no representative shader walkthrough. The tested behavior is binding-mode switching, and the shader code
is incidental to it: the sequencing programs are fixed quadrant painters (three vertex shaders that place a
quarter-size quad in one quadrant, a shared tessellation pair and geometry shader that expand it to the full quadrant,
and three solid-color fragment shaders) plus a compute shader that writes its local invocation index
([sequencing programs](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L842-L952)).
The stage-binding programs add storage-buffer writes of 1, 2, and 3 to the vertex, tessellation control, and geometry
shaders, plus a second program set with different position scaling for the pipeline draw
([stage-binding programs](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L1335-L1502)).
No shader contains logic that depends on the interaction type or on which stages are bound, so a walkthrough would not
clarify the tested property. One source quirk is worth noting: the compute shader declares
`layout(local_size_x=16, local_size_x=1, local_size_x=1)`, repeating `local_size_x` where `local_size_y` and
`local_size_z` were intended
([comp program](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L933-L940)). The CTS
shader compiler accepts it and emits a workgroup size of 16x1x1, so the dispatched invocations fill entries 0 through
15 and the check of entries 0 through 3 succeeds; the same pattern exists in the shared basic shader set. Because
shader code is incidental here, this page is recorded as a no-walkthrough exception for the `shader_object` category.

## Runtime Execution and Result Checking

- **Resource setup.** Both instances create a 32x32 `R8G8B8A8_UNORM` color attachment with a view, a host-visible
  color output buffer as transfer destination, a descriptor pool and set with one storage buffer binding, and a
  command pool with a main and a copy command buffer. The sequencing instance adds a 64-byte vertex buffer that is
  bound but never read, because no vertex input state exists and the shaders use `gl_VertexIndex`
  ([setup](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L151-L208)).
- **Object creation.** The sequencing instance creates ten unlinked shader objects and matching shader modules for
  vert1..3, tesc, tese, geom, frag1..3, and comp, three graphics pipelines from the modules, and one compute pipeline.
  A `VkRenderPass` and `VkFramebuffer` exist only so the two render-pass cases can create their pipelines against a
  legacy render pass; the framebuffer is never used for rendering. The stage-binding instance creates the selected
  shader objects, the matching pipeline shader modules, and one dynamic-rendering graphics pipeline
  ([sequencing creation](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L221-L274),
  [stage-binding creation](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L1072-L1172)).
- **Dynamic state assembly.** For max pipelines the instance collects every dynamic state the device supports,
  feature-gated and extension-gated one by one, and creates the pipelines with zero viewport and scissor counts;
  min pipelines get no dynamic state list and one static viewport ([state
  list](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L328-L527)).
- **Command buffer recording.** After an image barrier, the `render_pass_pipeline_shader_object` case binds its pipeline before
  `vkCmdBeginRendering`, while `render_pass_pipeline_shader_object_after_begin` binds it after rendering begins; every
  non-compute case begins its dynamic rendering instance. The command buffer then records the full default dynamic state set through
  [setDefaultShaderObjectDynamicStates](../../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.cpp#L244-L418),
  binds null task and mesh shaders when supported, and binds the vertex buffer. After pipeline-to-shader-object switches the
  instance normally re-issues the default dynamic state set, because the disturbed pipeline's non-dynamic state is undefined;
  the `render_pass_pipeline_shader_object` case is the exception because it records that state after the early pipeline bind and
  before binding shader objects. After shader-object-to-pipeline switches no re-issue happens. The two triple sequences also record
  `cmdSetRasterizationStreamEXT(0)` between draws, guarded on conservative rasterization support and annotated VUID-vkCmdDraw-None-07630
  ([recording](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L586-L737)).
- **Draws.** Every sequencing graphics draw submits four vertices as a patch list with four control points, so the
  full vert-tesc-tese-geom-frag chain runs and fills one quadrant. The stage-binding draws use a patch list when
  tessellation is selected and a triangle strip otherwise. Compute dispatches happen outside the render pass
  instance, before it begins or after it ends.
- **Copyback and image check.** A second command buffer copies the image into the host-visible buffer, and
  `verifyImage` compares exact colors: red upper-left when the draw count exceeds 0, green upper-right when it exceeds
  1, blue lower-left when it exceeds 2; the lower-right quadrant keeps the clear color and is not checked
  ([copy and check](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L740-L761),
  [verifyImage](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L780-L817)).
- **Compute check.** The two compute leaves invalidate the storage buffer allocation and require entries 0 through 3
  to equal their own index ([compute check](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L763-L775)).
- **Stage-binding checks.** When fragment is bound, the copied image must be white inside the centered rectangle and
  black outside it, with the 4-or-8 pixel borders derived from tessellation and geometry presence; the storage buffer
  must hold 1, 2, and 3 for the vertex, tessellation control, and geometry stages whenever those stages are selected
  ([stage-binding checks](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L1225-L1263),
  [stage-binding verifyImage](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L1266-L1299)).
- **Pass/fail.** A case passes only when every recorded draw and dispatch succeeds without validation errors and all
  exact comparisons hold; any mismatch returns `TestStatus::fail`.

## Failure Meaning

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

### Cause Analysis

#### Baseline shader-object or pipeline drawing broken

**Possible failure symptoms:** `shader_object` or `max_pipeline` fails with a wrong or missing red upper-left quadrant,
or the case fails during recording or submission with a validation error before any image exists.

**Possible implementation causes:** When a shader object is bound to any graphics stage, the drawing validity rules
require the applicable dynamic states to have been set, the same as if a pipeline had enabled them all, and the draw
must happen inside dynamic rendering. An implementation that ignores the dynamically set viewport and scissor counts,
that applies undefined state because it treats the shader-object draw as if a pipeline were still bound, or that
rejects the five-stage single-call binding would fail `shader_object`. For `max_pipeline`, the pipeline carries zero
viewport and scissor counts and the largest supported dynamic state list, so the same quadrant defect points at
dynamic state values not reaching the draw.

#### Binding disturbance mishandled

**Possible failure symptoms:** One of the four interleaving leaves fails while the baselines pass. The failing quadrant
identifies the draw: a wrong or missing second-quadrant green after a pipeline-to-shader-object switch, or a wrong or
missing quadrant after the reverse switch. A validation error at draw time is the other possible symptom.

**Possible implementation causes:** The spec requires `cmdBindShadersEXT` to disturb the graphics pipeline bind point
and makes the disturbed pipeline's non-dynamic state undefined, and `cmdBindPipeline` to disturb the bound shader
stages. An implementation that keeps the disturbed pipeline's shaders or static state in effect, that does not reset
state the spec declares undefined, or that fails to track the dynamic values recorded before the switch would produce
exactly one wrong quadrant. The min-pipeline leaves are the harder variant: a fully static pipeline invalidates every
piece of state at the disturbance point, so the re-issued default dynamic state set is the only state source for the
following draw. The `cmdSetRasterizationStreamEXT` call annotated VUID-vkCmdDraw-None-07630 requires the
rasterization stream value to stay defined across the transition when a geometry shader object is bound.

#### Render-pass pipeline binding mishandled around dynamic rendering

**Possible failure symptoms:** One or both `render_pass_pipeline_shader_object*` leaves fail with a validation error,
a device loss, or a wrong red upper-left quadrant, while pure shader-object and pure pipeline cases pass.

**Possible implementation causes:** Pipeline binding has no render pass scope, and the render pass compatibility rules
are draw-time rules, so binding a pipeline created against a legacy `VkRenderPass` either before or inside a dynamic
render pass instance is legal as long as no draw uses it. An implementation that enforces render pass compatibility
at bind time, that still considers the pipeline bound after the shader-object binding disturbed it, or that attempts
the draw with the legacy pipeline and hits the `renderPass = VK_NULL_HANDLE` requirement would fail these two leaves.
The two leaves together cover both bind positions, so a failure in only one narrows the cause to bind-position
handling.

#### Compute object-type boundary mishandled

**Possible failure symptoms:** A compute leaf fails the storage buffer check (entries 0 through 3 not equal to their
index), or fails during recording or dispatch, while its graphics draw renders the correct quadrant.

**Possible implementation causes:** The compute shader object and the compute pipeline occupy the same compute bind
point under the same disturbance rules as the graphics side. An implementation that requires a compute pipeline to be
bound for dispatch, that leaves the compute bind point in a broken state after the other object type was used, or that
dispatches with wrong workgroup dimensions writes wrong or missing buffer entries. Because the compute shader
writes `gl_LocalInvocationID.x` per invocation, wrong dispatch geometry also produces a wrong pattern in the entries
that are checked.

#### Partial stage binding mishandled

**Possible failure symptoms:** A stage-binding leaf fails with a missing storage buffer value (1, 2, or 3), a wrong
white rectangle, or a validation error, while the full five-stage bindings in the sequencing group pass.

**Possible implementation causes:** The draw with no bound graphics pipeline requires `cmdBindShadersEXT` to have been
called with every feature-enabled graphics stage in `pStages`, and a null handle must leave that stage absent. An
implementation that rejects the partial binding, that runs a stage bound as null, or that fails to execute a selected
stage after the pipeline-to-shader-object switch produces the observed symptom. A wrong rectangle size rather than a
missing rectangle points at stage execution with wrong geometry: the tessellation evaluation x scaling or the geometry
y scaling not applied. In the fragment-inactive leaves only the buffer writes can fail, which separates stage
execution defects from fragment output defects.

#### Output verification mismatch

**Possible failure symptoms:** The host reports a pixel that is not the expected red, green, blue, white, or black
value, or a storage buffer entry with the wrong index value, at a logged coordinate or position.

**Possible implementation causes:** When the binding sequences are not the explanation, the mismatch points at the
rendering or copyback path itself: the image-to-buffer copy, the barriers, or the host comparison. The test performs
its own barrier, copy, and exact comparison steps, so distinguishing a device rendering defect from a copyback or
synchronization defect would need source-level investigation of the specific log.

## Case Pruning

### Requirement-based pruning

- Every case requires `VK_EXT_shader_object`
  ([sequencing support check](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L954-L960),
  [stage-binding support check](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L1324-L1333)).
- Every sequencing case requires both the `tessellationShader` and `geometryShader` core features, which matches its
  usage: every sequencing draw runs the full five-stage chain through the tessellation and geometry stages.
- Stage-binding cases require the `tessellationShader` feature only when tessellation is selected and the
  `geometryShader` feature only when geometry is selected, so devices without those features still run the remaining
  subsets ([per-stage gates](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L1328-L1332)).
- The max pipeline's dynamic state list is assembled from the features and extensions the device reports, so the
  pipeline adapts its state list to the device rather than pruning cases.

### Design-based pruning

- The ten sequencing leaves are hand-picked sequences, not the full space of orderings: each switch direction, each
  pipeline flavor, each render-pass bind position, and each compute order is covered at least once, but combinations
  such as a min-pipeline triple sequence or a render-pass pipeline followed by another render-pass pipeline are not
  registered.
- The stage-binding matrix is the complete 2x2x2 cross product of tessellation, geometry, and fragment presence, with
  vertex always present because a draw needs a vertex or mesh stage; no subset is excluded.
- The lower-right image quadrant is never compared and keeps the clear color, because no draw targets it; the
  draw-count gating compares only the quadrants that the recorded draws fill.
- The stage-binding pipeline draw is intentionally invisible (its static viewport lies entirely outside the image), so
  the image check observes only the shader-object draw; the sequencing cases instead let every draw contribute its own
  quadrant.

## Key Takeaways

- The disturbance rule is the contract under test: binding shader objects unbinds pipelines and makes their
  non-dynamic state undefined, and binding a pipeline unbinds shader objects. The quadrant-per-draw design turns each
  binding event into one independently checked output region.
- Switching from a pipeline to shader objects requires re-issuing dynamic state, which the test does after every such
  switch; switching back needs no re-issue because the newly bound pipeline supplies its own state, and a max pipeline
  even keeps previously recorded dynamic values alive.
- The render-pass leaves show the boundary from both sides: a pipeline created against a legacy `VkRenderPass` may be
  bound anywhere, but drawing with it in dynamic rendering is illegal, so the shader-object binding must disturb it
  before the draw. Both bind positions are covered.
- The compute leaves extend the same rule to the compute bind point in both orders, with the storage buffer
  readback catching dispatches that ran with the wrong object or the wrong geometry.
- Failures surface as exact quadrant, rectangle, or buffer-entry mismatches, or as validation errors before output
  exists; which behavioral group fails narrows the cause, as detailed in `## Failure Meaning`.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test type enum and draw counts | [vktShaderObjectPipelineInteractionTests.cpp#L45-L57](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L45-L57), [getDrawCount()](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L102-L128) | The ten sequencing test types and their expected draw counts. |
| Sequencing instance | [iterate()](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L135-L778) | Resource setup, per-type bind and draw sequences, dynamic state re-issue, copyback, and checks. |
| Pipeline flavor and dynamic state assembly | [vktShaderObjectPipelineInteractionTests.cpp#L307-L527](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L307-L527) | Max versus min pipeline construction and the feature-gated dynamic state list. |
| Sequencing shader programs | [initPrograms()](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L842-L952) | Quadrant vertex shaders, tessellation, geometry, color fragment shaders, and the compute shader. |
| Sequencing support check | [checkSupport()](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L954-L960) | Extension and feature gates for the sequencing cases. |
| Stage-binding instance | [iterate()](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L991-L1264) | Invisible pipeline draw, subset binding, draw, and both verification paths. |
| Stage-binding shader programs | [initPrograms()](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L1335-L1502) | Shader-object variants with storage writes and the pipeline variants. |
| Stage-binding support check | [checkSupport()](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L1324-L1333) | Extension gate plus per-stage feature gates. |
| Registration | [createShaderObjectPipelineInteractionTests()](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L1506-L1553) | The ten sequencing and eight stage-binding leaves under `pipeline_interaction`. |
| Shared helpers | [vktShaderObjectCreateUtil.cpp#L244-L489](../../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.cpp#L244-L489) | `setDefaultShaderObjectDynamicStates`, `bindGraphicsShaders`, and null task/mesh binding. |
| Mustpass evidence | [pipeline-interaction.txt](../../../mustpass/main/vk-default/shader-object/pipeline-interaction.txt) | All 18 registered `dEQP-VK.shader_object.pipeline_interaction.*` case paths. |
