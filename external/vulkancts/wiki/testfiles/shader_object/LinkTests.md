## Overview

**Core question:** When a graphics or mesh shader chain mixes stages created linked with stages created unlinked, does the
implementation accept exactly the legal creation calls, `nextStage` declarations, and bind layouts, and still render or
write correct output?

- [vktShaderObjectLinkTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp) implements the
  `shader_object.link` test family: 16 graphics linked/unlinked combination groups, the `next_stage` group with 16
  next-stage chain cases, and 5 mesh/task combination groups, 161 registered cases in total.
- Each graphics case puts the five classic stages into one of three states: `UNUSED` (never created), `LINKED` (created in
  one batched `vkCreateShadersEXT` call with `VK_SHADER_CREATE_LINK_STAGE_BIT_EXT`), or `UNLINKED` (created in its own
  call). Cases then vary the bind mode, the creation order, and the `nextStage` masks.
- The family checks the `VK_EXT_shader_object` rules that decide which shaders may share a creation call, what `nextStage`
  may declare, and how linked shaders may be bound, using a fixed 32x32 render target and a fixed expected output.

## Background Knowledge

For the shared concepts shader objects, linked creation, stage chains, and per-stage binding, see [Background Knowledge](../../categories/shader_object.md#background-knowledge) of the `shader_object` page.

- **Linked shader objects.** `VK_SHADER_CREATE_LINK_STAGE_BIT_EXT` links a shader to the other flag-carrying shaders created
  in the same `vkCreateShadersEXT` call. Within one call, if any element carries the flag, every other graphics-stage
  element (vertex, tessellation control, tessellation evaluation, geometry, fragment) must carry it too, and the same rule
  applies to task and mesh elements. Compute shaders are exempt, so an unlinked compute shader may share the call. The
  direct consequence for this test: an unlinked graphics stage must be created in its own call, separate from the linked
  batch.
- **`nextStage` declaration.** `nextStage` in `VkShaderCreateInfoEXT` declares which stages can be used as the logically
  next bound stage when drawing; zero means the stage must be the last one. Each stage has a legal subset: vertex may
  declare tessellation control, geometry, or fragment; tessellation control only tessellation evaluation; tessellation
  evaluation only geometry or fragment; geometry only fragment; task only mesh; mesh only fragment. For a linked shader
  followed by another linked shader in the same call, `nextStage` must equal exactly that next linked stage. An unlinked
  shader, or a linked shader with no later linked stage in its call, may declare any legal subset, including several options
  at once. Declaring a tessellation or geometry bit also requires the corresponding device feature.
- **Binding linked shaders.** `vkCmdBindShadersEXT` binds one or more stages per call, and linked shaders may be bound in
  any combination of one or more calls; shaders created linked together do not need to be bound in the same call. A
  `VK_NULL_HANDLE` entry unbinds a stage. At draw time, if any bound shader was created with the link flag, every shader
  linked to it must also be bound; the application is responsible for this.
- **Task-less mesh shaders.** `VK_SHADER_CREATE_NO_TASK_SHADER_BIT_EXT` is valid only on a mesh shader and marks it as used
  without a task shader. A mesh shader created with both this flag and the link flag must not share a creation call with a
  linked task shader.

## Registration Hierarchy

```text
shader_object.link
├── linked_linked_linked_linked_linked
├── linked_linked_linked_linked_unlinked
├── linked_linked_linked_unlinked_unlinked
├── linked_linked_linked_unused_unlinked
├── linked_linked_unlinked_unused_unlinked
├── linked_unused_unused_linked_linked
├── linked_unused_unused_linked_unlinked
├── linked_unused_unused_unused_linked
├── unlinked_linked_linked_linked_linked
├── unlinked_linked_linked_linked_unlinked
├── unlinked_linked_linked_unused_linked
├── unlinked_linked_linked_unused_unlinked
├── unlinked_unlinked_unlinked_unused_unlinked
├── unlinked_unused_unused_linked_linked
├── unlinked_unused_unused_unlinked_unlinked
├── unlinked_unused_unused_unused_unlinked
├── next_stage
├── mesh_linked_linked_linked
├── mesh_linked_linked_unlinked
├── mesh_unlinked_linked_linked
├── mesh_unlinked_unlinked_unlinked
└── mesh_unlinked_unlinked_unused
```

Each graphics group name lists the states of vertex, tessellation control, tessellation evaluation, geometry, and fragment
in that order. Every graphics group contains three bind-mode groups (`separate`, `one_linked_unlinked`, `all`); each bind
group holds the `default` and `random_order` cases, plus `separate_link` when at least one stage is `LINKED`. `next_stage`
holds its 16 cases directly, and each mesh group holds `default` and `random_order`
([createShaderObjectLinkTests()](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L1351-L1650)).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Stage link state | `unused`, `linked`, `unlinked` per stage | Chooses whether a stage is absent, created in the linked batch, or created alone; the 16 graphics groups sample the meaningful mixtures. | [shaderTests table](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L1355-L1364) |
| Graphics bind mode | `separate`, `one_linked_unlinked`, `all` | Changes how the created shaders reach the command buffer: one call per stage, a two-call linked/unlinked split, or one call for all five stages. | [bindTypeTests](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L1371-L1379) |
| Creation ordering | `default`, `random_order`, `separate_link` | Varies whether the linked batch keeps stage order, has two entries swapped, or is replaced by one call per linked shader. | [ordering loop](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L1391-L1447) |
| nextStage masks | per-stage flags such as `vert_t`, `vert_tgf`, `tese_gf`, `geom_f` | Declares legal next stages independently of which shaders exist, including multi-option masks and no-fragment chains. | [nextStageTests](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L1453-L1615) |
| Mesh link state | `unused`, `linked`, `unlinked` for task, mesh, fragment | Repeats the link-state idea for the mesh pipeline, where task and mesh link through to fragment. | [meshShaderTests](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L1617-L1620) |
| Descriptor layout identity | shared layout object vs. four identically defined objects | Checks that linking accepts distinct `VkDescriptorSetLayout` objects with identical definitions. | [layout selection](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L257-L293), [identically_defined_layouts](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L1596-L1604) |

## Behavior Parameters

The primary behavioral axis is the **behavioral group** formed by the registered intermediate nodes: the graphics
linked/unlinked combinations, the `next_stage` chain cases, and the mesh/task combinations. Each group stresses a different
part of the linkage rules. Two secondary registered axes also apply: the bind mode, registered for the graphics groups, and
the creation ordering, registered for the graphics and mesh groups with `separate_link` limited to graphics.

### Graphics linked/unlinked combinations: mixed link-state chains

The 16 `linked_*` and `unlinked_*` groups draw one fixed quad through chains that mix linked and unlinked stages, such as
linked vertex and tessellation control with an unlinked tessellation evaluation, or an unlinked vertex feeding four linked
stages. The property under test is that the creation split itself is legal and that the implementation compiles the chain
correctly no matter where the linked segment sits
([shaderTests table](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L1355-L1364)). When fragment is
`UNUSED`, the last active pre-fragment stage writes the verification values into a storage buffer instead of the image.

### next_stage: next-stage chain declarations

The 16 leaves under `next_stage` hold `nextStage` masks that vary independently of shader presence: a vertex declaring only
tessellation control (`vert_t`), one declaring tessellation control, geometry, and fragment at once (`vert_tgf`), chains
that end before the fragment stage (`vert_no_frag`, `tess_no_frag`, `geom_no_frag`), and per-stage single-successor cases
such as `tesc_t` and `geom_f`
([nextStageTests](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L1453-L1615)). No stage in this
group is created linked, so the cases isolate the declaration rules from linkage. `identically_defined_layouts` repeats the
`geom_no_frag` chain with a distinct but identically defined descriptor set layout per stage.

### mesh_*: task/mesh/fragment link combinations

The five mesh groups apply the same three-state idea to task, mesh, and fragment shaders, with
`cmdDrawMeshTasksEXT` replacing the vertex-based draw. The mesh shader is created with
`VK_SHADER_CREATE_NO_TASK_SHADER_BIT_EXT` whenever the task shader is `UNUSED`
([mesh creation](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L985-L1012)), and linked task, mesh,
and fragment shaders are batched together in one call, as in the graphics case.

The first secondary axis is the **bind mode**, which decides how the created shaders are bound before the draw.

### separate: one bind call per stage

Each of the five graphics stages is bound with its own `cmdBindShadersEXT` call, unused stages receiving `VK_NULL_HANDLE`
([separate path](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L487-L505)). This exercises the spec
rule that linked shaders do not need to be bound in the same call.

### one_linked_unlinked: linked and unlinked shaders bound in two calls

The first non-unused stage in stage order joins every unlinked stage in one binding call; each remaining linked stage is
bound in a second call. Before both calls, all five graphics stages are unbound with null handles
([one_linked_unlinked path](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L506-L584)). The mode mixes
linked and unlinked shader handles inside a single call.

### all: every stage bound in one call

All five graphics stages, including `VK_NULL_HANDLE` entries for unused ones, are bound in one `cmdBindShadersEXT` call,
followed by null task and mesh bindings when supported
([all path](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L585-L593)).

The second secondary axis is the **creation ordering** of the linked batch.

### default: stage-ordered creation

The linked batch lists the create infos in stage order, and shaders are bound in the selected bind mode. This is the
baseline against which the other two orderings differ.

### random_order: permuted creation array

Two entries of the linked batch are swapped before the `vkCreateShadersEXT` call, and the returned handles are swapped back
afterwards, so the call receives create infos out of stage order while the test still maps handles to stages correctly
([random order swap](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L419-L441)). The case checks that
creation does not depend on array order.

### separate_link: linked shaders created one call at a time

Every linked shader is submitted in its own single-create-info `vkCreateShadersEXT` call instead of one batch
([separateLinked path](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L429-L437)). Each shader still
carries the link flag, so this case checks that a link-flagged shader created alone is accepted and renders correctly when
bound together with the rest of the chain.

## Shader Analysis

This page has no representative shader walkthrough. The tested behavior is linkage legality and binding behavior, and the
shader code is incidental to it: the graphics cases use the trivial quad, passthrough, and white-output shaders from the
shared basic shader object set, plus storage-buffer variants that write `1..4`; the mesh cases use a task shader that
emits one workgroup, a mesh shader that emits a viewport-covering triangle and writes `0..3`, and a white fragment shader
([graphics programs](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L756-L832),
[mesh programs](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L1266-L1321),
[basic shader set](../../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.cpp#L122-L211)). No shader contains
logic that depends on the link state, bind mode, or ordering, so a walkthrough would not clarify the tested property. The
page is listed under `shader_object` in the walkthrough exception registry for this reason.

## Runtime Execution and Result Checking

- **Creation split.** The instance builds one `VkShaderCreateInfoEXT` per non-unused stage. Each `LINKED` stage gets the
  link flag and goes into a batch vector; each `UNLINKED` stage is created in its own single-shader call
  ([creation](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L304-L401)). Whenever the batch is
  non-empty, an empty `comp2` compute shader without the link flag is appended to it, so that one call contains a linked
  graphics chain together with an unlinked compute shader
  ([comp2 append](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L403-L408)).
- **`nextStage` computation.** For each linked stage, `getNextStage()` returns the exact next linked stage when one exists
  in the batch, and otherwise falls back to the registered per-stage mask; unlinked stages always use the registered mask
  ([getNextStage](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L130-L191)). The graphics
  registration derives those masks from which stages are non-unused
  ([mask derivation](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L1396-L1412)).
- **Ordering variants.** `random_order` swaps two batch entries before creation and swaps the returned handles back;
  `separate_link` submits each linked shader in its own call
  ([batch creation](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L414-L464)).
- **Binding and state.** The command buffer binds shaders in the selected bind mode, unbinds task and mesh stages for
  graphics draws (or the classic rasterization stages for mesh draws), and sets the full set of dynamic states that shader
  object drawing requires through `setDefaultShaderObjectDynamicStates`
  ([binding](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L487-L596),
  [dynamic states](../../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.cpp#L244-L418)).
- **Draw.** Graphics cases draw four vertices as a triangle strip, or as a patch list with four control points when
  tessellation control is active ([draw](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L598-L607)).
  When fragment is `UNUSED`, the storage descriptor set is bound so the writing stage can fill the result buffer. Mesh
  cases issue one `cmdDrawMeshTasksEXT` call
  ([mesh draw](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L1128-L1141)).
- **Copyback and verification.** The image is barriered and copied to a host-visible buffer. Fragment-active graphics cases
  require white inside the covered rectangle and black outside it; the x border is 4 pixels when tessellation control is
  active and 8 otherwise, and the y border is 4 pixels when geometry is active and 8 otherwise, matching the position
  scaling those stages apply. Fragment-unused graphics cases require the storage buffer to hold `1, 2, 3, 4`. Mesh cases
  require an all-white image when fragment is active and a `0, 1, 2, 3` storage buffer whenever the mesh shader runs
  ([graphics checks](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L661-L717),
  [mesh checks](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L1199-L1238)). All comparisons are exact.
- **Cleanup.** Every created shader, including `comp2`, is destroyed before the case returns
  ([cleanup](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L642-L659)).

## Failure Meaning

### Failure Cause Mapping

Primary axis (behavioral group):

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| Graphics linked/unlinked combinations | Linked batch creation or link-chain compilation failure, or unlinked-stage creation split mishandled, producing wrong or missing render output. |
| `next_stage` cases | Illegal rejection or wrong enforcement of `nextStage` masks (per-stage subsets, exact-next-linked-stage rule, or feature-gated bits). |
| `mesh_*` combinations | Task/mesh link-chain creation failure, `VK_SHADER_CREATE_NO_TASK_SHADER_BIT_EXT` handling error, or wrong mesh draw output. |

Secondary axis 1 (bind mode):

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `separate` | Multi-call binding of linked shaders mishandled (spec allows linked shaders to be bound across separate calls). |
| `one_linked_unlinked` | A single call that binds a mix of linked and unlinked shaders mishandled, or the two-call split mis-tracked. |
| `all` | Single-call full-stage binding mishandled, including null-binding of unused stages. |

Secondary axis 2 (ordering):

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `default` | Order-independent defect in creation, binding, or rendering (baseline). |
| `random_order` | Implementation wrongly assumes create infos arrive in stage order within one `vkCreateShadersEXT` call. |
| `separate_link` | Implementation wrongly assumes linked shaders always arrive in one call and mishandles one-call-per-linked-shader creation. |

All cases share the same verification mechanisms (image region compare and/or storage buffer compare), so a failure in any
case is observed as a pixel or buffer mismatch in the log.

### Cause Analysis

#### Linked chain creation or compilation failure

**Possible failure symptoms:** A case with at least one linked stage fails during `vkCreateShadersEXT` or produces a wrong
image or storage buffer afterwards. Depending on the failure, the log shows a returned error or validation message before
the draw, or a pixel or buffer mismatch after it.

**Possible implementation causes:** The spec scopes linkage to the flag-carrying shaders of one creation call and requires
every graphics or task/mesh element of that call to be either all linked or all unlinked. An implementation that rejects
the appended unlinked compute shader, that tries to link a chain across the individually created unlinked stages, or that
compiles a linked segment without resolving its interface to the unlinked neighbors would show this symptom. The appended
`comp2` shader and the unlinked creation split exist to expose such assumptions.

#### nextStage rejection or wrong chain enforcement

**Possible failure symptoms:** A `next_stage` case fails at creation with a validation error, or a combination case fails
because a legal declaration was refused. In both situations the case never reaches a correct output comparison, or the
output comparison fails because the implementation bound the wrong successor stage.

**Possible implementation causes:** The declaration rules allow any legal per-stage subset for unlinked shaders and for the
last linked stage of a call, while requiring an exact single-stage value for a linked stage followed by another linked
stage. An implementation that rejects multi-option masks such as vertex declaring tessellation control, geometry, and
fragment together, that demands exact masks where subsets are legal, or that treats `nextStage` as a binding constraint
rather than a declaration would fail these cases. Rejecting a declared tessellation or geometry bit on hardware without
the matching feature would instead be correct behavior.

#### Task/mesh link or no-task flag handling failure

**Possible failure symptoms:** A `mesh_*` case fails at creation, or the mesh draw produces a wrong image or a storage
buffer other than `0, 1, 2, 3`.

**Possible implementation causes:** The mesh cases batch linked task, mesh, and fragment shaders together, set
`VK_SHADER_CREATE_NO_TASK_SHADER_BIT_EXT` on a mesh shader whose task stage is unused, and never mix linked mesh stages
with linked classic graphics stages, mirroring the spec restrictions. An implementation that mishandles the no-task flag,
that rejects the linked task-to-mesh or mesh-to-fragment chain, or that fails the registered mixtures where only the
fragment or only the task is unlinked would fail here.

#### Multi-call or mixed binding of linked shaders mishandled

**Possible failure symptoms:** A case fails only in one bind mode while the same chain passes in another mode. The output
mismatch is identical in form to a rendering defect, but it tracks the binding layout rather than the chain itself.

**Possible implementation causes:** The spec allows linked shaders to be bound in any combination of one or more
`cmdBindShadersEXT` calls and requires only that the whole link chain be bound at draw time. An implementation that tracks
link groups per binding call instead of per draw, that ignores the null-handle unbinding of unused stages, or that
mishandles a single call containing both linked and unlinked handles would fail the `separate`, `all`, or
`one_linked_unlinked` mode specifically.

#### Creation-order or per-call linked creation mishandled

**Possible failure symptoms:** A `random_order` or `separate_link` case fails while the corresponding `default` case of
the same chain and bind mode passes.

**Possible implementation causes:** `vkCreateShadersEXT` fills `pShaders` in array order regardless of stage order, and a
link-flagged shader created alone forms a valid single-shader link set. An implementation that assumes create infos arrive
in stage order within one call, or that only accepts the link flag when the whole chain arrives in that one call, would
fail exactly these two orderings. The `separate_link` case also widens the registered `nextStage` masks to full per-stage
subsets, since the exact-next-linked-stage rule does not apply across separate calls.

#### Output verification mismatch

**Possible failure symptoms:** The host reports a pixel that is not the expected white or black value, or a storage buffer
entry that is not the expected index value, with the failing coordinate or index logged.

**Possible implementation causes:** When the creation and binding paths are not the explanation, the mismatch points to the
rendering itself: a linked segment compiled with a wrong stage interface, tessellation evaluation or geometry scaling
applied inconsistently with the expected covered rectangle, or a mesh shader writing the wrong buffer values. Distinguishing
a shader-execution defect from a copyback or barrier problem would need source-level investigation of the specific log,
since the test performs its own barrier, copy, and host comparison steps.

## Case Pruning

### Requirement-based pruning

- Every case requires `VK_EXT_shader_object`
  ([graphics support check](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L742-L745),
  [mesh support check](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L1323-L1328)).
- Every graphics link case requires both the `tessellationShader` and `geometryShader` core features, including
  combinations that use neither stage. The support check ORs the tessellation-control and geometry bits into its
  `nextStage` bit tests, and a bitwise OR with those bits is always nonzero, so both feature requirements always trigger
  ([support check](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L746-L753)).
- Mesh cases always require `VK_EXT_mesh_shader` with both the `taskShader` and `meshShader` features, even when the task
  shader is `UNUSED`
  ([mesh support check](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L1328-L1333)).
- The `nextStage` declaration rules themselves require the tessellation and geometry features whenever their bits are
  declared, but the graphics-wide requirement above already subsumes this for this family.

### Design-based pruning

- The 16 graphics combinations are hand-picked samples of the three-state space, not the full cross product. They cover
  fully linked chains, fully unlinked chains, linked segments in every position, gaps left by unused stages, and
  combinations that skip tessellation or geometry entirely
  ([shaderTests table](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L1355-L1364)).
- `separate_link` is registered only for the 13 combinations with at least one `LINKED` stage; the three fully unlinked
  groups have no linked shader to create separately
  ([separate_link condition](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L1428-L1447)).
- The `comp2` compute shader is appended only when a linked batch exists, so fully unlinked cases never create it
  ([comp2 append](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L403-L408)).
- All `next_stage` cases use `UNLINKED` stages and the `all` bind mode, isolating the declaration rules from linkage and
  binding variation. `identically_defined_layouts` is the single case that distributes distinct but identically defined
  descriptor set layouts across stages
  ([nextStageTests](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L1453-L1605)).
- The mesh groups contain only task, mesh, and fragment shaders, because a mesh draw does not use the classic graphics
  stages; the spec also forbids creating linked task or mesh stages together with linked vertex, tessellation, or
  geometry stages in one call, so such mixtures stay out of the family by design.

## Key Takeaways

- The core constraint is per creation call, not per chain: within one `vkCreateShadersEXT` call, graphics stages must be
  all linked or all unlinked, which is why the test creates unlinked stages in separate calls and why the unlinked
  `comp2` compute shader may legally ride along in the linked batch.
- `nextStage` has two regimes: a linked stage followed by another linked stage must declare exactly that stage, while
  unlinked stages and the last linked stage of a call may declare any legal per-stage subset, including several options.
- Linked shaders may be bound across any number of `cmdBindShadersEXT` calls; the three bind modes exist to hold the
  implementation to that rule, and the ordering variants hold it to array-order independence and per-call linked creation.
- Failures surface as creation or validation errors before any draw, or as an exact pixel or storage-buffer mismatch
  afterwards; which axis failed narrows the cause, as detailed in `## Failure Meaning`.
- Graphics cases need tessellation and geometry feature support regardless of the stages they use, because of how the
  current support check tests the `nextStage` bits, so absence of those features prunes the whole graphics part of this
  family.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Link state, bind type, and parameter structs | [vktShaderObjectLinkTests.cpp#L45-L104](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L45-L104) | Defines `ShaderType`, `BindType`, `NextStages`, and the parameter payloads. |
| Graphics `getNextStage()` | [vktShaderObjectLinkTests.cpp#L130-L191](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L130-L191) | Computes the exact next linked stage or the fallback mask per stage. |
| Graphics creation and batching | [vktShaderObjectLinkTests.cpp#L304-L464](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L304-L464) | Implements the linked/unlinked creation split, `comp2` append, random order, and separate link. |
| Graphics bind modes | [vktShaderObjectLinkTests.cpp#L487-L596](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L487-L596) | Implements `separate`, `one_linked_unlinked`, `all`, null unbinds, and dynamic state setup. |
| Graphics verification | [vktShaderObjectLinkTests.cpp#L661-L717](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L661-L717) | Image region check and storage buffer check with the 4/8 pixel border rule. |
| Graphics support check | [vktShaderObjectLinkTests.cpp#L742-L754](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L742-L754) | Extension and feature gates, including the tessellation and geometry requirement. |
| Graphics shader programs | [vktShaderObjectLinkTests.cpp#L756-L832](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L756-L832) | Storage-buffer shader variants and the empty compute shader. |
| Mesh instance | [vktShaderObjectLinkTests.cpp#L834-L1241](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L834-L1241) | Mesh/task/fragment creation, no-task flag handling, binding, draw, and checks. |
| Registration | [vktShaderObjectLinkTests.cpp#L1351-L1650](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L1351-L1650) | Builds the 16 graphics groups, the `next_stage` group, and the 5 mesh groups. |
| Shared shader set and helpers | [vktShaderObjectCreateUtil.cpp#L58-L211](../../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.cpp#L58-L211) | Basic GLSL set, default `nextStage` derivation, and `makeShaderCreateInfo`. |
| Dynamic state and bind helpers | [vktShaderObjectCreateUtil.cpp#L244-L489](../../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.cpp#L244-L489) | `setDefaultShaderObjectDynamicStates`, `bindGraphicsShaders`, and null-stage bind helpers. |
| Mustpass evidence | [link.txt](../../../mustpass/main/vk-default/shader-object/link.txt) | All 161 registered `dEQP-VK.shader_object.link.*` case paths. |
