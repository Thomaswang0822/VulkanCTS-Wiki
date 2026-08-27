# Understanding Brief: shader_object.binding (vktShaderObjectBindingTests.cpp)

## One-Sentence Test Purpose

This test checks whether an implementation applies `vkCmdBindShadersEXT` bindings by execution time, so that swapping,
unbinding, or interleaving per-stage bindings between draws and dispatches changes exactly the stage it should and
nothing else.

## Background Knowledge

### Per-stage command buffer binding

`VK_EXT_shader_object` replaces the monolithic graphics pipeline with per-stage `VkShaderEXT` objects that are bound to
a command buffer with `vkCmdBindShadersEXT(commandBuffer, stageCount, pStages, pShaders)`. Each element of `pStages`
names one stage; the element of `pShaders` at the same index supplies the handle for that stage. Bindings accumulate
across calls: a later call for a stage replaces the earlier binding for that stage, and untouched stages keep their
bindings. Linked and unlinked shaders may be bound in any combination of one or more calls.

Why it matters here:

- Every family in this test changes the binding state between two executions (two draws, two dispatches, or a draw and
  a mesh draw) and checks that only the intended stage changed.
- The expected image is built from the coverage of both executions, so a binding applied too early, too late, or not at
  all produces a wrong region or color.

### Unbinding a stage

A bound shader may be unbound by setting its `pShaders` element to `VK_NULL_HANDLE`. If `pShaders` is `NULL`, the command
behaves as if `pShaders` were an array of `stageCount` null handles, unbinding every stage listed in `pStages`.
Unbinding a stage that is already unbound is legal.

Why it matters here:

- The classic unbind cases compare an array of null handles against a null pointer, and the final unbind cases switch
  between the vertex path and the mesh path purely by unbinding stages.

### Draw-time binding validity

When drawing with shader objects and no bound graphics pipeline, the spec constrains which stages may be bound:

- If the task or mesh shader feature is enabled, exactly one of the vertex and mesh stages must hold a valid shader and
  the other must be unbound. A valid vertex binding requires the task and mesh stages to be unbound.
- Mesh draws (`vkCmdDrawMeshTasksEXT`) require the vertex, tessellation control, tessellation evaluation, and geometry
  stages to be unbound.
- A mesh shader created without `VK_SHADER_CREATE_NO_TASK_SHADER_BIT_EXT` requires a valid task shader bound when the
  task and mesh features are enabled.
- Each stage whose feature is enabled must have been touched by at least one `vkCmdBindShadersEXT` call before drawing,
  even if the call bound `VK_NULL_HANDLE`. On a device created with `geometryShader` or `tessellationShader` disabled,
  that stage may simply stay unbound.
- Every required dynamic state must be set before the draw, but state commands may be recorded before or after the
  shader bindings.

Why it matters here:

- These rules explain why the unbind families unbind vertex/tessellation/geometry before a mesh draw, why the
  tessellation pair is unbound in one call, and why the disabled-stage families never bind the feature-disabled stage.
- The before/after timing axis exists because the spec allows both orderings.

### Graphics and compute binding independence

Graphics-stage and compute-stage bindings are separate command buffer state. Binding a compute shader does not disturb
bound graphics stages, and binding graphics shaders does not disturb the compute binding.

Why it matters here:

- `draw_dispatch_draw` binds a compute shader between two draws, and `dispatch_draw_dispatch` binds graphics shaders
  between two dispatches. Both executions must run with their own domain's bindings intact.

## One Concrete Example

`dEQP-VK.shader_object.binding.swap_frag`, reconstructed and simplified from the source:

```text
[host] create vert, tesc, tese, geom, frag ("blendFrag", outputs 0.5 gray), fragAlt (outputs red)
[host] record: bind the five classic stages; bind null task and mesh if supported;
       set dynamic states and enable blending (src ONE, dst ONE_MINUS_SRC_ALPHA)
[host] record: cmdDraw(4 vertices, triangle strip)
[device] draw 1 covers the inner 24x24 region of the 32x32 target with 0.5 gray
[host] record: cmdBindShadersEXT(stageCount=1, pStages={FRAGMENT}, pShaders={fragAlt})
[host] record: cmdDraw(4 vertices, triangle strip)
[device] draw 2 overwrites the same region with red
[host] copy image back and compare each pixel: red inside the quad, black outside
```

Only the fragment slot is rebound between the draws, so only the fragment behavior may change. A stale fragment binding
leaves the overlap at 0.75 gray (two 0.5 blend passes) instead of red, and the pixel comparison fails. The other swap
cases rebind vertex, tessellation control, tessellation evaluation, or geometry instead, and each alt shader moves or
recolors the covered region in a way that only that stage can.

## End-to-End Test Flow

```text
[host] pick the registered case parameters (test type, stage, unused-output stage, binary stage, timing, unbind style)
[host] create the color image, copyback buffer, and any storage buffers and descriptor sets the case needs
[host] create shader objects per stage; for the binary-stage dimension, create that stage's shader from
       getShaderBinaryDataEXT binary data instead of SPIR-V
[host] for the disabled-stage families only: create a custom device with geometryShader or tessellationShader off
[host] begin the command buffer; barrier the image; set dynamic states (before or after binding, per the timing axis)
[host] record execution 1 (draw, dispatch, or mesh draw) with the initial bindings
[host] record the binding change under test (stage swap, null-handle unbind, null-pointer unbind, disabled-stage null
       bind, or cross-domain bind)
[host] record execution 2 (draw, dispatch, or mesh draw); some families use only one execution
[host] end rendering, barrier the image to transfer, copy it to the host-visible buffer
[host] submit and wait
[host] scan every pixel against the expected region model, or read the storage buffers, and decide pass/fail
```

The `bindings` family is the exception: it records one 8-stage bind call per stage combination, submits, and passes
when submission succeeds. It never draws or dispatches.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- The shared basic shader object set (`vert`, `tesc`, `tese`, `geom`, `frag`, `comp`) from
  [vktShaderObjectCreateUtil.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.cpp#L122-L211): a
  quad vertex shader, quad tessellation pair, geometry shader scaling y by 1.5, white fragment shader, and a compute
  shader writing its local invocation index.
- Family-specific variants generated in
  [initPrograms](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L690-L875): `vertAlt`,
  `tescAlt`, `teseAlt`, `geomAlt`, `fragAlt` (each changes geometry or color so the swap is visible, and each may
  declare an extra unconsumed output), `passThroughGeom`, `blendFrag`, and feature-dependent vertex variants
  (`vertNoTess`, `vertNoGeom`, `vertNoTessGeom`, plus Alt counterparts).
- Mesh variants for the mesh families (`task1`, `task2`, `mesh1`, `mesh2`, `mesh`, `frag_white`, `frag_red`,
  `vert_offset`), built as SPIR-V 1.4
  ([mesh programs](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L1303-L1394),
  [unbind programs](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L2000-L2069)).
- Binary artifacts: for the `binary_*` dimension, the shader of the named stage is created once from SPIR-V, its data
  is read back with `vkGetShaderBinaryDataEXT`, and a second shader is created from that data with
  `VK_SHADER_CODE_TYPE_BINARY_EXT`
  ([createShader](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L152-L180)).

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| 32x32 `R8G8B8A8_UNORM` color image | yes | yes, as color attachment | written by fragment shaders | yes, copied to buffer | Carries the two-draw coverage evidence for all image-checked families. |
| Host-visible copyback buffer | yes | yes, transfer destination | written by copy | yes | Holds the image pixels for the host scan. |
| Two 16-entry storage buffers (`draw` cases) | yes | yes, descriptor sets 1 and 2 | written by the compute shader | yes | `dispatch_draw_dispatch` checks both hold `0..15`, proving each dispatch ran with its own descriptor set. |
| One 4-entry storage buffer (mesh families) | yes | yes, descriptor set | written by task and mesh shaders | yes | `mesh_swap_*` and the final unbind cases check which draw's values survived. |
| Index buffer with a restart entry (`unbind_mesh_draw_vertex`) | yes | yes, via `cmdBindIndexBuffer` | read by the draw | no | Splits the indexed strip so the red quad lands in the center region only. |

GLSL `shared` variables, samplers, textures, and push constants are not used by this family.

## What Is Checked

- Image-checked families: every pixel of the 32x32 target must match a two-rectangle model. Pixels inside both
  rectangles expect 0.75 gray (or red for the fragment swap), pixels inside exactly one expect 0.5 gray, and pixels
  outside both expect black, with a tolerance of 1/256 per channel. Each draw contributes one rectangle, so the model
  encodes which binding was active at each draw
  ([pixel check](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L624-L650)).
- `dispatch_draw_dispatch`: both storage buffers must hold `0, 1, ..., 15`
  ([buffer check](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L605-L622)).
- `mesh_swap_task` expects `[4, 5, 2, 3]` and `mesh_swap_mesh` expects `[0, 1, 6, 7]` in the storage buffer
  ([mesh checks](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L1245-L1263)).
- Final unbind cases expect white, black-bordered white, or red/white regions plus buffer `[0, 1, 2, 3]`
  ([unbind checks](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L1857-L1960)).
- `bindings` and `bindings_mesh_shaders`: no output check; the case passes when every bind call records and the command
  buffer submits and waits without error
  ([bindings iterate](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L895-L1048)).

## Behavior Parameter Identification

> **Behavior parameter:** behavioral group (the case families under the `binding` test family, since all 273 registered
> cases are direct leaves with no intermediate nodes)
>
> **Candidate values:** `swap` (5 simple swaps plus the 250-case cross product), classic `unbind` (passthrough geometry,
> tessellation pair, geometry, in two unbind styles), `disabled` stage, draw/dispatch `interleaving`, `mesh_swap`,
> `bindings` list matrix, and final `unbind` (vertex/mesh path switching)
>
> Secondary axes inside the swap cross product: unused-output stage, binary stage, and dynamic-state timing
> (`_before`/`_after`); inside classic unbind: unbind style (`_null_handle`/`_null_pshaders`).

## What Failure Means

### Failure Cause Mapping

Primary axis (behavioral group):

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| Swap families (`swap_*`, 255 cases) | Stage rebind between draws applied too early, too late, or not at all; binary-recreated shader mishandled; extra unconsumed output breaking stage linkage; dynamic-state/binding order dependence. |
| Classic unbind (`unbind_passthrough_geom`, `unbind_tesc_*`, `unbind_geom_*`, 5 cases) | Null-handle or null-pointer unbinding not honored, so the second draw still runs the unbound stage, or the unbind disturbs stages it should not. |
| Disabled-stage families (`disabled_*`, 4 cases) | Drawing without ever binding the feature-disabled stage fails, or explicitly null-binding the disabled stage is rejected or disturbs the draw. |
| Draw/dispatch interleaving (`draw_dispatch_draw`, `dispatch_draw_dispatch`) | A compute binding disturbs graphics bindings between draws, or a graphics binding disturbs compute bindings between dispatches. |
| Mesh swap (`mesh_swap_*`, 2 cases) | Task or mesh rebind between mesh draws not applied, so the buffer keeps the first draw's side-effect values. |
| Binding lists (`bindings`, `bindings_mesh_shaders`) | Some stage bind/unbind combination is rejected or crashes at submission although no draw was issued. |
| Final unbind (`unbind_vtg`, `unbind_task_mesh`, `unbind_mesh_draw_vertex`) | Vertex/mesh path switching through unbinding is rejected or runs with the wrong active stages, producing wrong image or buffer output. |

Secondary axes (swap cross product and unbind style):

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| Binary stage (`binary_vert` .. `binary_frag` in the case name) | A shader created from `getShaderBinaryDataEXT` data misbehaves when bound and swapped in. |
| Unused-output stage (`unused_output_*` in the case name) | An extra unconsumed output declared by the swapped shader breaks stage linkage or pipeline compilation. |
| State timing (`_before` / `_after`) | The implementation depends on dynamic state being set before rather than after shader binding. |
| Unbind style (`_null_handle` / `_null_pshaders`) | The `pShaders == NULL` form is mishandled relative to an array of null handles. |

## Important Variations and Special Cases

- The 250-case swap cross product iterates swapped stage x unused-output stage x binary stage x timing. The
  unused-output declaration only becomes active when it names the same stage as the swapped stage, because only the
  swapped stage's alt shader is bound. The other four unused-output values re-run the swap without the extra output,
  keeping the registered matrix complete at little cost.
- `unbind_passthrough_geom` expects the second (geometry-unbound) draw to match the first draw exactly, because a
  pass-through geometry shader reproduces the same primitives as no geometry shader.
- The tessellation pair is unbound in a single two-stage call: leaving one of the two stages bound would leave a
  dangling tessellation half at draw time.
- The `bindings` matrix skips combinations that bind vertex together with task or mesh, since one bind call may not
  carry valid handles for both sides of that pair. It ends with one call that passes `pShaders = NULL` for all eight
  stages when the device reports all four optional features.
- `draw_dispatch_draw` records no actual dispatch: it binds the compute shader between two draws. The name describes
  the interleaving pattern, and the check is that both draws render identically.
- `disabled_*` cases run on a custom device created with the stage feature turned off; `disabled_geom_bind` and
  `disabled_tess_bind` additionally call `vkCmdBindShadersEXT` with `VK_NULL_HANDLE` for the disabled stage.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Parameter structs and test types | [vktShaderObjectBindingTests.cpp#L52-L81](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L52-L81) | Defines `BindingDrawParams`, `MeshBindingDrawParams`, and `BindingParams`. |
| Custom device for disabled stages | [vktShaderObjectBindingTests.cpp#L112-L150](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L112-L150) | Creates the device with `geometryShader` or `tessellationShader` off. |
| Binary round-trip creation | [vktShaderObjectBindingTests.cpp#L152-L180](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L152-L180) | Creates one stage's shader from its own binary data. |
| Draw-family command recording | [vktShaderObjectBindingTests.cpp#L353-L519](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L353-L519) | Implements the swap, unbind, disabled, and interleaving sequences. |
| Expected region model and checks | [vktShaderObjectBindingTests.cpp#L527-L650](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L527-L650) | The two-rectangle pixel model and the buffer check. |
| Draw-family shader variants | [vktShaderObjectBindingTests.cpp#L690-L875](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L690-L875) | Alt shaders with optional unused outputs and feature-dependent vertex variants. |
| Bindings matrix instance | [vktShaderObjectBindingTests.cpp#L895-L1048](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L895-L1048) | The 8-stage combination loop and the null-pointer unbind call. |
| Mesh swap instance | [vktShaderObjectBindingTests.cpp#L1068-L1267](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L1068-L1267) | Two mesh draws with a task or mesh swap between them. |
| Final unbind instance | [vktShaderObjectBindingTests.cpp#L1503-L1964](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L1503-L1964) | VTG unbind, task/mesh unbind, and mesh-draw-then-vertex-draw sequences. |
| Registration | [vktShaderObjectBindingTests.cpp#L2073-L2200](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L2073-L2200) | Builds all 273 leaves of the `binding` group. |
| Shared shader set and bind helpers | [vktShaderObjectCreateUtil.cpp#L122-L211](../../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.cpp#L122-L211), [vktShaderObjectCreateUtil.cpp#L420-L489](../../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.cpp#L420-L489) | Basic GLSL set, `bindGraphicsShaders`, and null-stage bind helpers. |
| Mustpass evidence | [binding.txt](../../../mustpass/main/vk-default/shader-object/binding.txt) | All 273 registered `dEQP-VK.shader_object.binding.*` case paths. |

## Questions / Risk Points for User Audit

- Is the two-rectangle coverage model the clearest way to explain why a stale binding shows up as a wrong gray level?
- Is it acceptable that `bindings` passes on successful submission alone, with no output comparison? The same is true
  of the old page's description, and validation layers would catch illegal combinations, but a silent implementation
  defect in bind handling could pass.
- Should the page state that 200 of the 250 cross-product cases exercise no unused output because the declaration only
  activates when the unused-output stage equals the swapped stage? The page currently plans to record it under
  design-based pruning.
- The `draw_dispatch_draw` name promises a dispatch that the code never records. The page will describe the actual
  sequence (bind compute between two draws). Is that the right depth, or does this deserve reporting as a naming
  defect in the source?
- The `vert_offset` shader offsets x for vertex indices above 4, but the second indexed strip only contains two
  vertices (indices 4 and 5) and renders nothing. The offset is unreachable in practice. Not a correctness defect, but
  worth noting in the risk report.

## Conversion Notes for Final Wiki Rewrite

- Distill the four Background Knowledge topics into page-local prerequisite bullets; the Level-2 consolidation pass may
  later move the shared ones into the category page.
- Promote the `swap_frag` example into the Behavior Parameters explanation for the swap group, not into a walkthrough;
  the page will be a no-walkthrough page with an exception registry entry, since the shader code is incidental.
- Keep the two Failure Cause Mapping tables verbatim in the final page's `### Failure Cause Mapping`; write
  `### Cause Analysis` fresh.
- Move the source mapping into the Source Reference Appendix, keep the resource table condensed inside Runtime
  Execution and Result Checking, and keep the spec rules inline where each family uses them.
