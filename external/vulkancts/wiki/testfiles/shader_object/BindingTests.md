## Overview

**Core question:** When `vkCmdBindShadersEXT` swaps, unbinds, or interleaves per-stage shader bindings between two recorded executions, does each execution run with exactly the stages that were bound when it was recorded?

- [vktShaderObjectBindingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp) implements the `shader_object.binding` test family: 273 registered cases covering single-stage swaps, stage unbinding in both legal forms, drawing with feature-disabled stages, graphics/compute binding interleaving, mesh-stage swaps, a full eight-stage bind combination matrix, and vertex/mesh path switching through unbinding.
- Image-checked draw-family cases use a 32x32 target; the two-draw cases use blending and a host-side pixel model combining both draws. Single-execution cases and mesh/path-switch cases use their own expected-image checks, with some also checking storage-buffer side effects. A binding applied too early, too late, or not at all changes an execution's contribution and fails the relevant check.
- Buffer-checked cases read back storage-buffer side effects written by compute, task, or mesh shaders, and the binding-list cases submit eight-stage bind calls without drawing at all.

## Background Knowledge

For the shared concepts shader objects and per-stage binding, see [Background Knowledge](../../categories/shader_object.md#background-knowledge) of the `shader_object` page.

- **Per-stage binding.** `VK_EXT_shader_object` binds one `VkShaderEXT` per stage to a command buffer with `vkCmdBindShadersEXT(commandBuffer, stageCount, pStages, pShaders)`. Each `pStages` element names one stage and the `pShaders` element at the same index supplies its handle. Bindings accumulate across calls: a later call for a stage replaces that stage's binding, and untouched stages keep theirs. Linked and unlinked shaders may be bound in any combination of one or more calls.
- **Unbinding forms.** A bound shader is unbound by setting its `pShaders` element to `VK_NULL_HANDLE`. If `pShaders` is `NULL`, the command behaves as if it were an array of `stageCount` null handles and unbinds every stage listed in `pStages`. Unbinding an already-unbound stage is legal.
- **Draw-time stage validity.** When drawing with shader objects and no bound graphics pipeline: if the task or mesh shader feature is enabled, exactly one of the vertex and mesh stages must hold a valid shader and the other must be unbound; a valid vertex binding requires the task and mesh stages to be unbound; mesh draws require the vertex, tessellation control, tessellation evaluation, and geometry stages to be unbound; and a mesh shader created without `VK_SHADER_CREATE_NO_TASK_SHADER_BIT_EXT` requires a bound task shader.
- **Feature-gated binding requirement.** Each stage whose feature is enabled at device creation must have been touched by at least one `vkCmdBindShadersEXT` call before drawing, even a call that bound `VK_NULL_HANDLE` for it. On a device created with a stage feature disabled, that stage may stay unbound.
- **Graphics/compute independence.** Graphics-stage and compute-stage bindings are separate command buffer state. Binding a compute shader does not disturb bound graphics stages, and binding graphics shaders does not disturb the compute binding.
- **Dynamic state timing.** Every dynamic state a draw needs must be set before the draw, but the state commands may be recorded before or after the shader bindings. Both orderings must produce the same result.

## Registration Hierarchy

```text
shader_object
└── binding
```

All 273 registered cases are direct test case leaves of `shader_object.binding`; the family has no intermediate nodes. The leaves form seven behavioral groups: 5 simple stage swaps plus the 250-case swap cross product, 5 classic unbind cases, 4 disabled-stage cases, 2 draw/dispatch interleaving cases, 2 mesh swaps, 2 binding-list cases, and 3 final unbind cases
([registration](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L2073-L2200)). The root file adds this branch unconditionally
([vktShaderObjectTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L57)), and no `binding` case appears in `excluded-tests.txt`.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Swapped stage | `vert`, `tesc`, `tese`, `geom`, `frag` | The stage whose alt shader is rebound between the two draws of a swap case; each alt shader changes the covered region in a way only that stage can. | [stageTest table](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L2088-L2098) |
| Unused-output stage | `vert`, `tesc`, `tese`, `geom`, `frag` | Names the stage whose alt shader declares an extra output no following stage consumes; it takes effect only when it matches the swapped stage. | [alt shader generation](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L747-L859) |
| Binary stage | `vert`, `tesc`, `tese`, `geom`, `frag` | The named stage's shader is created from its own `vkGetShaderBinaryDataEXT` binary instead of SPIR-V. | [createShader round-trip](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L152-L180) |
| State timing | `before`, `after` | Whether the dynamic state block is recorded before or after the initial shader binding. | [timing branch](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L362-L363) |
| Unbind style | `null_handle`, `null_pshaders` | Compares an array of `VK_NULL_HANDLE` entries against a null `pShaders` pointer for the same unbind. | [unbind branch](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L456-L480) |
| Disabled feature | `geom`, `tess`, each with and without explicit bind | Runs on a custom device with the feature off; the `_bind` variants also null-bind the disabled stage. | [custom device](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L112-L150) |
| Mesh swap stage | `task`, `mesh` | Which mesh-pipeline stage is swapped between two mesh draws. | [meshStageTest](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L2153-L2168) |
| Mesh binding toggle | off, on | `bindings_mesh_shaders` adds real task and mesh shaders to the eight-stage bind matrix. | [bindings registration](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L2185-L2189) |
| Final unbind mode | `vtg`, `task_mesh`, `mesh_draw_vertex` | Chooses which vertex/mesh path-switching sequence runs. | [final unbind registration](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L2191-L2197) |

## Behavior Parameters

The primary behavioral axis is the **behavioral group**: the registered case families, since all 273 leaves sit directly under the test family. Each group stresses a different part of the binding rules. Two secondary axes apply as well: the swap cross product varies the unused-output stage, the binary stage, and the state timing, and the classic unbind group varies the unbind style.

### Swap families: one stage rebound between two draws

The 255 swap cases bind the full classic chain, draw, rebind one stage's alt shader with a single-stage `cmdBindShadersEXT` call, and draw again
([SWAP branch](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L394-L414)). The first draw covers a 24x24 rectangle inset 4 pixels, because the base vertex shader emits a half-size quad that the evaluation shader scales in x and the geometry shader scales in y. Each alt shader then produces a stage-characteristic second region: the vertex alt scales positions to cover the whole target, the control and evaluation alts halve positions on one or both axes, the geometry alt halves only y, and the fragment alt keeps the region but outputs red. The expected image is the combination: 0.75 gray where both draws land, 0.5 gray where exactly one lands, black elsewhere, and red instead of 0.75 gray for the fragment swap. The 250 cross-product cases add the unused-output, binary, and timing dimensions to the same two-draw sequence.

### Classic unbind: stages unbound between draws

Five cases unbind stages between two draws and check that the second draw runs as if the stage never existed
([UNBIND branch](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L456-L480)). `unbind_passthrough_geom` draws once with a pass-through geometry shader, unbinds the geometry stage, and draws again; both draws must cover the same rectangle, because a pass-through geometry shader reproduces the same primitives as no geometry stage. `unbind_geom_null_handle` and `unbind_geom_null_pshaders` unbind geometry after a scaling geometry shader ran, so the second quad must lose its y scaling and come out shorter. `unbind_tesc_null_handle` and `unbind_tesc_null_pshaders` unbind the tessellation pair in one two-stage call, so the second quad must lose its x scaling and come out narrower. The two styles must be equivalent: a null handle per stage versus a null `pShaders` pointer.

### Disabled-stage families: drawing with feature-disabled stages

The four `disabled_*` cases create a custom device with `geometryShader` or `tessellationShader` turned off, never create the disabled stage's shader, and draw once with the remaining stages
([DISABLED branch](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L415-L455),
[custom device](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L112-L150)). Because the feature is off at device creation, the spec does not require the stage to be bound at all. `disabled_geom_bind` and `disabled_tess_bind` also record a `VK_NULL_HANDLE` bind for the disabled stage, which must be accepted and change nothing.

### Draw and dispatch interleaving: cross-domain binding between executions

`draw_dispatch_draw` draws, binds the compute shader, and draws again
([DRAW_DISPATCH_DRAW branch](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L481-L491)); the second draw must cover the same rectangle as the first, producing one uniform 0.75 gray region. `dispatch_draw_dispatch` dispatches with one descriptor set and buffer, binds all graphics shaders, binds a second descriptor set, and dispatches again
([DISPATCH_DRAW_DISPATCH branch](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L492-L504)); both buffers must hold `0..15`, proving each dispatch ran the compute shader with its own descriptor set. Together the two cases check that neither binding domain disturbs the other.

### Mesh swap: task or mesh rebound between mesh draws

`mesh_swap_task` and `mesh_swap_mesh` first null-bind the classic rasterization stages, then draw once with task and mesh shaders that write `0,1` and `2,3` into a storage buffer, then rebind the task or mesh alt shader and draw again
([mesh swap instance](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L1179-L1224)). The task alt writes `4,5` and the mesh alt writes `6,7`, so the final buffer is `[4, 5, 2, 3]` for a task swap and `[0, 1, 6, 7]` for a mesh swap. The case never reads the image back; only the buffer distinguishes which binding each draw used.

### Binding lists: full-stage bind combination matrix

`bindings` and `bindings_mesh_shaders` iterate every bind/don't-bind combination of the eight stages (vertex, tessellation control, tessellation evaluation, geometry, fragment, compute, mesh, task) and submit one eight-stage `cmdBindShadersEXT` call per combination, with `VK_NULL_HANDLE` for unbound or unsupported stages
([combination loop](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L971-L1026)). Combinations that bind vertex together with task or mesh are skipped, because a single call may not carry valid handles for both vertex and task, or for both vertex and mesh. When the device reports all four optional stage features (tessellation, geometry, task, mesh), one extra call passes `pShaders = NULL` for all eight stages, unbinding everything in one command
([null-pointer call](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L1028-L1045)). In `bindings_mesh_shaders`, real task and mesh shaders replace the null entries. No draw or dispatch is recorded; the case passes when every call records and the submission completes.

### Final unbind: vertex and mesh path switching

Three cases cross from one pre-rasterization path to the other by unbinding the stages of the path they leave before drawing with the other:
[VTG unbind](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L1648-L1699),
[task/mesh unbind](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L1700-L1749),
[mesh-draw-then-vertex-draw](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L1750-L1773)). `unbind_vtg` unbinds vertex, tessellation control, tessellation evaluation, and geometry in one four-stage call, binds task and mesh, repeats the VTG unbind, and issues a mesh draw; the image must be white everywhere and the mesh shader's buffer must hold `[0, 1, 2, 3]`. `unbind_task_mesh` binds task, mesh, and fragment, unbinds task and mesh, binds a vertex shader, and draws; the expected image is a white center quad on black. `unbind_mesh_draw_vertex` draws with mesh shaders first, then unbinds task and mesh, binds a vertex shader with a red fragment shader, and issues an indexed draw whose primitive-restart entry splits the strip; the mesh background stays white, the red quad lands in the center, and the mesh shader's buffer still reads `[0, 1, 2, 3]`.

## Shader Analysis

This page has no representative shader walkthrough. The tested behavior is command-buffer binding semantics, and the shader code is incidental: the graphics cases use the shared basic shader object set plus alt variants that only shift vertex positions or output a constant color, the compute shader writes its local invocation index into a buffer, and the task and mesh shaders emit one workgroup and a viewport-covering triangle while writing constant buffer values
([alt and variant programs](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L690-L875),
[mesh programs](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L1303-L1394),
[unbind programs](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L2000-L2069),
[basic shader set](../../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.cpp#L122-L211)). No shader contains logic that depends on the binding sequence under test, so a walkthrough would not clarify the tested property. The page is listed under `shader_object` in the walkthrough exception registry for this reason.

## Runtime Execution and Result Checking

- **Common graphics setup.** Every image-checked case creates a 32x32 `R8G8B8A8_UNORM` target, a host-visible copyback buffer, and, for compute cases, two 16-entry storage buffers with their own descriptor sets. Dynamic states come from `setDefaultShaderObjectDynamicStates`, and blending is enabled with src `ONE` and dst `ONE_MINUS_SRC_ALPHA`, so the shared fragment shader's 0.5 gray leaves 0.5 over black and 0.75 over a previous 0.5
  ([setup](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L206-L352)).
- **Shader variant selection.** The vertex shader binary is chosen from the device's tessellation and geometry support (`vert`, `vertNoTess`, `vertNoGeom`, `vertNoTessGeom`, each with an alt counterpart), and the tessellation and geometry shaders are skipped when the matching feature is absent
  ([variant selection](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L314-L350)).
- **Binary round-trip.** When the binary-stage dimension names a stage, that stage's shader is created from SPIR-V, read back with `vkGetShaderBinaryDataEXT`, and recreated from the retrieved data with `VK_SHADER_CODE_TYPE_BINARY_EXT`
  ([createShader](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L152-L180)).
- **Recording.** Each family records its own binding and execution sequence in one command buffer, as described under `## Behavior Parameters`; the disabled-stage families draw once, and the binding-list family records no execution at all. The timing axis controls whether the dynamic state block is recorded before the initial binding or between the binding and the first draw
  ([timing branch](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L362-L363)).
- **Copyback.** After the last execution, the image is barriered to transfer and copied into the host-visible buffer, and the submit waits for completion
  ([copyback](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L509-L525)).
- **Image check.** The host walks every pixel and compares it against the two-rectangle model, with a tolerance of 1/256 per channel; the first mismatching pixel is logged with its expected and actual color
  ([pixel check](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L624-L650)).
- **Buffer checks.** `dispatch_draw_dispatch` scans both storage buffers for `0..15`; mesh swap expects `[4, 5, 2, 3]` or `[0, 1, 6, 7]`; the final unbind cases expect `[0, 1, 2, 3]` from the mesh shader
  ([dispatch check](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L605-L622),
  [mesh check](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L1245-L1263),
  [unbind check](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L1857-L1960)).
- **Binding-list pass condition.** The `bindings` family has no output comparison; it passes when all bind calls record and the command buffer submits and waits without error
  ([bindings iterate](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L895-L1048)).

## Failure Meaning

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

### Cause Analysis

#### Stage rebind timing or persistence failure

**Possible failure symptoms:** An image-checked swap or mesh-swap case fails with one wrong region or one wrong color band, or a mesh-swap buffer holds `[0, 1, 2, 3]`, the first draw's values, instead of the swapped-in stage's values. The log names the first mismatching pixel or the four buffer entries.

**Possible implementation causes:** The spec makes the last recorded binding for a stage the one that executes. An implementation that snapshots bindings at the first draw, that applies a later bind call retroactively to already recorded draws, or that caches a compiled stage combination and misses the single-stage replacement would produce exactly this split between the two draws' contributions.

#### Unbind not honored or over-applied

**Possible failure symptoms:** A classic unbind case fails because the second draw keeps the unbound stage's scaling, so the second rectangle has the wrong size, or because the unbind disturbed other stages and the first rectangle is also wrong. A `null_pshaders` case fails while its `null_handle` twin passes, or both fail together. A final unbind case fails with a validation error or a wrong path output, for example a mesh draw after the vertex stages were unbound.

**Possible implementation causes:** `VK_NULL_HANDLE` entries and a `NULL` `pShaders` pointer must both clear the listed stages and touch nothing else. An implementation that ignores null entries, that treats the null pointer form differently from the array form, or that clears an entire graphics binding set when one stage is unbound would fail these cases. The requirement that the classic pre-rasterization stages be unbound for a mesh draw, and the reverse requirement when a vertex draw follows a mesh draw, are exercised by the final unbind cases.

#### Feature-disabled stage handling failure

**Possible failure symptoms:** A `disabled_*` case fails at draw time or produces a wrong single-draw rectangle. The `_bind` variants fail specifically when the explicit null bind of the disabled stage is rejected, while the plain variants fail when the implementation wrongly demands a binding for the disabled stage.

**Possible implementation causes:** The spec requires a stage to be bound or explicitly unbound only when the stage's feature is enabled at device creation. An implementation that validates the full five-stage set regardless of the device's enabled features, or that rejects `VK_NULL_HANDLE` for a feature-disabled stage, fails these cases. The draw also compiles a shorter chain, so a driver that cannot link vertex to fragment across a missing tessellation or geometry stage would fail the rectangle comparison.

#### Cross-domain binding interference

**Possible failure symptoms:** `draw_dispatch_draw` renders a wrong second rectangle or a validation error occurs when the compute shader is bound between the draws. `dispatch_draw_dispatch` leaves one buffer untouched or partially written, or the second dispatch runs against the first descriptor set and both buffers hold the same values.

**Possible implementation causes:** Graphics and compute bindings are independent command buffer state. An implementation that rebuilds or clears graphics bindings when a compute handle is bound, or that invalidates the compute binding when the five graphics stages are bound, produces these symptoms. The second buffer also depends on a fresh descriptor set bind between the dispatches, so a descriptor-tracking defect can produce the same signature.

#### Bind combination rejection

**Possible failure symptoms:** A `bindings` case fails or crashes during recording or submission, with no pixel or buffer evidence because nothing was executed.

**Possible implementation causes:** The spec allows any subset of stages to be bound in one call, including subsets that would be invalid at draw time, such as tessellation control without evaluation or mesh without task, because no draw follows. An implementation that validates draw-time stage combinations inside `vkCmdBindShadersEXT` itself, rather than at draw time, would reject legal calls here. This pass condition is weaker than an output check: without validation layers, an implementation that accepts the calls but tracks them incorrectly would still pass this case.

#### Binary-recreated or unused-output stage linkage failure

**Possible failure symptoms:** A cross-product swap case fails only when its `binary_*` stage equals the swapped stage, or only when its `unused_output_*` stage equals the swapped stage, while the same swap passes in the plain five-case form.

**Possible implementation causes:** The binary dimension replaces one stage's shader with a recreation from its own opaque binary data, and the unused-output dimension adds an output that no following stage consumes. An implementation whose binary path produces a shader with a different stage interface, or whose linker rejects outputs without consumers, fails exactly these cases.

#### Output verification mismatch

**Possible failure symptoms:** The host logs a pixel outside the 1/256 tolerance or a buffer entry with the wrong value, and the failing coordinate or index identifies which draw's rectangle or write is wrong.

**Possible implementation causes:** When the binding paths above are not the explanation, the mismatch points to the draw itself: a stage that scales positions inconsistently with its expected rectangle, a mesh shader writing the wrong buffer values, or a copyback or barrier defect. Distinguishing a rendering defect from a copyback defect would need source-level investigation of the specific log, since the test performs its own barrier, copy, and host comparison steps.

## Case Pruning

### Requirement-based pruning

- Every case requires `VK_EXT_shader_object`
  ([draw-family support check](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L676-L688)).
- The draw family requires the `tessellationShader` feature when the swapped or binary stage is a tessellation stage, and the `geometryShader` feature when it is the geometry stage. This also applies to the `disabled_*` cases: the physical device must support the feature so the custom device can turn it off. The two interleaving cases inherit a leftover tessellation stage parameter from the registration loop, so they require the tessellation feature as well.
- The mesh swap cases and all final unbind cases require `VK_EXT_mesh_shader` with both the `taskShader` and `meshShader` features
  ([mesh support check](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L1292-L1301),
  [unbind support check](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L1989-L1998)).
- `bindings_mesh_shaders` requires `VK_EXT_mesh_shader`; plain `bindings` does not, and its task and mesh entries are always null handles
  ([bindings support check](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L1419-L1424)).
- Registration itself is unconditional once the root adds the branch, and `excluded-tests.txt` removes only `shader_object.performance.*`, so no `binding` case is excluded from the default mustpass.

### Design-based pruning

- The binding-list matrix skips every combination that binds vertex together with task or mesh, mirroring the single-call validity rule; those pairings are never submitted in one call
  ([skip conditions](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L986-L991)).
- The tessellation pair is unbound in a single two-stage call, because leaving one half bound would leave a dangling tessellation stage at draw time
  ([pair unbind](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L469-L478)).
- The unused-output declaration becomes active only when it names the same stage as the swapped stage, since only that stage's alt shader is bound. Four of the five unused-output values per (stage, binary, timing) combination therefore re-run the same swap without the extra output, keeping the registered matrix complete at little cost
  ([alt shader generation](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L747-L859)).
- `draw_dispatch_draw` records no actual dispatch between its two draws; the compute binding alone is the interference under test, and both draws must render identically
  ([DRAW_DISPATCH_DRAW branch](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L481-L491)).
- In `unbind_mesh_draw_vertex`, the indexed strip after the restart entry contains only two vertices and renders nothing, so only the first strip's red quad is observable; the mesh-draw background and buffer side effects carry the rest of the check
  ([indexed draw](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L1816-L1819)).

## Key Takeaways

- The binding in force at each execution is the last one recorded before it, so a two-draw expected image built from per-draw coverage is enough to detect a binding applied too early, too late, or not at all.
- `VK_NULL_HANDLE` per stage and `pShaders = NULL` are equivalent unbind forms, and both are held to the same result by paired cases.
- Graphics and compute bindings are independent state, which is why binding a compute shader between two draws and binding graphics shaders between two dispatches changes nothing in either domain's output.
- Vertex and mesh paths exclude each other at execution time, and the test switches between them by unbinding the path it leaves before binding the target path; four-stage and two-stage unbind calls ensure the excluded stages are not left bound.
- Stage requirements follow enabled features, not stage existence: on a device created without geometry or tessellation, the stage may stay unbound, and explicitly null-binding it must also succeed.
- Failures surface as exact pixel or buffer mismatches, except in the binding-list family, whose pass condition is successful submission; that family cannot detect silent tracking errors without validation layers.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Parameter structs and test types | [vktShaderObjectBindingTests.cpp#L52-L81](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L52-L81) | Defines `BindingDrawParams`, `MeshBindingDrawParams`, `BindingParams`, and the six draw test types. |
| Custom device for disabled stages | [vktShaderObjectBindingTests.cpp#L112-L150](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L112-L150) | Creates the device with `geometryShader` or `tessellationShader` off. |
| Binary round-trip creation | [vktShaderObjectBindingTests.cpp#L152-L180](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L152-L180) | Creates one stage's shader from its own binary data. |
| Draw-family command recording | [vktShaderObjectBindingTests.cpp#L353-L519](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L353-L519) | Implements the passthrough, swap, disabled, unbind, and interleaving sequences. |
| Expected region model and checks | [vktShaderObjectBindingTests.cpp#L527-L650](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L527-L650) | The two-rectangle pixel model, the dispatch buffer check, and the pixel scan. |
| Draw-family shader variants | [vktShaderObjectBindingTests.cpp#L690-L875](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L690-L875) | Alt shaders with optional unused outputs and feature-dependent vertex variants. |
| Bindings matrix instance | [vktShaderObjectBindingTests.cpp#L895-L1048](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L895-L1048) | The eight-stage combination loop and the null-pointer unbind call. |
| Mesh swap instance | [vktShaderObjectBindingTests.cpp#L1068-L1267](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L1068-L1267) | Two mesh draws with a task or mesh swap between them, checked through the storage buffer. |
| Final unbind instance | [vktShaderObjectBindingTests.cpp#L1503-L1964](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L1503-L1964) | VTG unbind, task/mesh unbind, and mesh-draw-then-indexed-vertex-draw sequences with image and buffer checks. |
| Registration | [vktShaderObjectBindingTests.cpp#L2073-L2200](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L2073-L2200) | Builds all 273 leaves of the `binding` group. |
| Shared shader set and bind helpers | [vktShaderObjectCreateUtil.cpp#L122-L211](../../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.cpp#L122-L211), [vktShaderObjectCreateUtil.cpp#L420-L489](../../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.cpp#L420-L489) | Basic GLSL set, `bindGraphicsShaders`, and null-stage bind helpers. |
| Parent registration | [vktShaderObjectTests.cpp#L47-L63](../../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L47-L63) | Adds the `binding` branch to the `shader_object` tree. |
| Mustpass evidence | [binding.txt](../../../mustpass/main/vk-default/shader-object/binding.txt) | All 273 registered `dEQP-VK.shader_object.binding.*` case paths. |
