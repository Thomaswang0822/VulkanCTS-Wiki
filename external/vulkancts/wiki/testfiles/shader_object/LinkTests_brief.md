# Understanding Brief: shader_object.link / vktShaderObjectLinkTests.cpp

This brief prepares the Level-3 rewrite of the shader object link test family. It is explanation-first and treats the CTS
source, the mustpass registration, and the Vulkan spec (VK_EXT_shader_object) as the authorities. The local checkout does not
vendor `external/vulkan-docs`, so spec semantics below were checked against the current Vulkan specification pages for
`VkShaderCreateInfoEXT`, `vkCreateShadersEXT`, `vkCmdBindShadersEXT`, and `VkShaderCreateFlagBitsEXT`.

## One-Sentence Test Purpose

This test checks whether an implementation accepts every legal combination of linked and unlinked shader stages, next-stage
declarations, creation orders, and bind modes, and still renders or writes the expected output.

Core question: **when a graphics or mesh shader chain mixes shaders created linked with shaders created unlinked, does the
implementation honor exactly the spec rules for which stages may share a `vkCreateShadersEXT` call, what `nextStage` may
declare, and how the resulting shaders may be bound and drawn?**

## Background Knowledge

### Linked and unlinked shader objects

`VK_SHADER_CREATE_LINK_STAGE_BIT_EXT` marks a shader as linked to every other shader created in the same
`vkCreateShadersEXT` call whose create info also carries the flag. The flag is the shader-object replacement for pipeline
link-time compilation: it lets implementations compile a whole graphics or mesh chain together, but only when the application
explicitly groups the shaders into one call.

Why it matters here:

- Within one call, if any element carries the link flag, all other elements whose stage is a graphics stage
  (vertex, tessellation control, tessellation evaluation, geometry, fragment) must also carry it, and the same rule covers
  task and mesh stages (VUID-vkCreateShadersEXT-pCreateInfos-08402 and -08403). An unlinked graphics shader therefore
  **must** be created in its own call, separate from linked shaders.
- Compute shaders are exempt from those rules, so an unlinked compute shader may legally ride along in the same call as a
  linked graphics chain. The test appends an empty `comp2` compute shader to every linked batch to cover this.
- Linked task or mesh stages must not share a call with linked vertex/tessellation/geometry stages (VUID -08404), and a mesh
  shader created with both the link flag and `VK_SHADER_CREATE_NO_TASK_SHADER_BIT_EXT` must not share a call with a linked
  task shader (VUID -08405). The mesh cases honor this by never creating classic graphics stages.

### nextStage declaration

`nextStage` in `VkShaderCreateInfoEXT` declares which stages can be used as the logically next bound stage when drawing with
the shader bound; zero means the stage must be the last one. The spec restricts the mask per stage: vertex may declare
tessellation control, geometry, or fragment; tessellation control only tessellation evaluation; tessellation evaluation only
geometry or fragment; geometry only fragment; task only mesh; mesh only fragment; fragment and compute must be zero
(VUID-VkShaderCreateInfoEXT-nextStage-08427 through -08436). Declaring a tessellation or geometry bit additionally requires
the corresponding device feature (VUID -08428 and -08429).

Why it matters here:

- For a linked shader followed by another linked shader in the same call, `nextStage` must equal **exactly** the stage of the
  next linked shader (VUID-vkCreateShadersEXT-pCreateInfos-08409). The test computes this exact value per linked stage in
  [`getNextStage()`](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L130-L191).
- For an unlinked shader, or a linked shader with no later linked stage in its call, `nextStage` may be any legal subset. The
  `next_stage` group varies these masks independently of which shaders actually exist, including multi-option masks such as
  vertex declaring tessellation control, geometry, and fragment at once.

### Binding linked shaders

`vkCmdBindShadersEXT` binds one or more stages; a `VK_NULL_HANDLE` entry unbinds that stage. The spec states that linked
shaders may be bound in any combination of one or more calls, so shaders created linked together do not need to be bound in
the same call. At draw time, if any bound shader was created with the link flag, all shaders linked to it must also be bound;
this is the application's responsibility.

Why it matters here:

- The three registered bind modes exist to cover the legal binding spectrum: one call for all stages, one call per stage, and
  a two-call split that mixes linked and unlinked shaders in the first call.
- Unused stages are explicitly unbound with `VK_NULL_HANDLE` entries, and task/mesh (or classic rasterization) stages are
  nulled when the other pipeline type draws.

## One Concrete Example

Conceptual walk-through of `dEQP-VK.shader_object.link.linked_linked_unlinked_unused_unlinked.all.default`
(shaders: vertex `LINKED`, tessellation control `LINKED`, tessellation evaluation `UNLINKED`, geometry `UNUSED`, fragment
`UNLINKED`):

1. Tessellation evaluation and fragment shaders are unlinked, so each is created in its own single-shader
   `vkCreateShadersEXT` call; they must not share a call with the linked pair.
2. Vertex and tessellation control shaders carry `VK_SHADER_CREATE_LINK_STAGE_BIT_EXT` and are created together in one call,
   with the empty `comp2` compute shader appended. Vertex `nextStage` is exactly
   `VK_SHADER_STAGE_TESSELLATION_CONTROL_BIT` (the next linked stage); tessellation control `nextStage` is
   `VK_SHADER_STAGE_TESSELLATION_EVALUATION_BIT` (its only legal option anyway).
3. All five graphics stages are bound in a single `cmdBindShadersEXT` call, geometry receiving `VK_NULL_HANDLE`; task and
   mesh stages are bound null when supported.
4. The draw is a 4-vertex triangle strip (or patch list when tessellation control is active); the fragment shader writes
   white where the geometry covers the 32x32 attachment.

This is reconstructed from
[`ShaderObjectLinkInstance::iterate()`](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L193-L464); the
`all` bind path is [vktShaderObjectLinkTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L585-L593).

## End-to-End Test Flow

```text
[host] pick the registered combination: per-stage link state (UNUSED / LINKED / UNLINKED),
       bind mode, ordering, nextStage masks
[host] build one VkShaderCreateInfoEXT per non-unused stage; linked stages (plus an
       unlinked compute shader) go into one batch call, unlinked stages go into
       individual calls; batch order optionally swapped (random_order) or split into
       one call per linked shader (separate_link)
[host] record a command buffer: image barrier, bind shaders in the selected mode,
       set all shader-object dynamic states, unbind the unused pipeline type's stages,
       bind the storage descriptor set when fragment is unused
[device] graphics cases: draw 4 vertices (triangle strip or patch list); mesh cases:
       cmdDrawMeshTasksEXT(1,1,1)
[device] fragment-present cases write white into the color attachment; fragment-unused
       cases write 1..4 into a storage buffer from the last active stage (graphics) or
       0..3 from the mesh shader
[host] barrier, copy the image to a host-visible buffer, submit and wait
[host] verify pixel region / storage buffer contents; destroy all created shaders
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- Inline GLSL, compiled to SPIR-V by the CTS program build: the shared basic set `vert`, `tesc`, `tese`, `geom`, `frag`,
  `comp` from [addBasicShaderObjectShaders()](../../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.cpp#L122-L211),
  plus link-file variants `vert2`, `tese2`, `geom2` (same geometry, but each writes `result[0..3] = 1..4` into a storage
  buffer), `comp2` (empty compute shader), and mesh `task`, `mesh`, `frag`
  ([vktShaderObjectLinkTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L756-L832) and
  [vktShaderObjectLinkTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L1266-L1321)).
- No pipelines, no specialization constants, no render pass objects (dynamic rendering is used).
- The `identically_defined_layouts` case builds four descriptor set layout objects with identical definitions so each stage
  gets a distinct-but-equal layout.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| 32x32 `R8G8B8A8_UNORM` color attachment + view | yes | yes (rendering attachment) | written by fragment or cleared | yes, via copy to buffer | Carries the white/black pattern checked when fragment is active |
| Host-visible color output buffer | yes | yes (transfer dst) | written by `cmdCopyImageToBuffer` | yes | Copyback target for the pixel check |
| Storage buffer `Result { uint result[4]; }` + descriptor set + layout + pipeline layout | yes (only when fragment is `UNUSED`) | yes (graphics or mesh descriptor binding) | written by `vert2`/`tese2`/`geom2` or mesh shader | yes, host-visible | The verification channel for no-fragment cases |

## What Is Checked

- Fragment-active graphics cases: after the draw, every pixel inside the expected interior rectangle must be white
  `(1,1,1,1)` and every border pixel black `(0,0,0,1)`. The interior offset is 4 pixels when tessellation control is active
  (tessellation evaluation scales x by 1.5) or geometry is active (geometry scales y by 1.5), otherwise 8 pixels
  ([image check](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L661-L701)).
- Fragment-unused graphics cases: the storage buffer must contain `1, 2, 3, 4`
  ([buffer check](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L702-L714)).
- Mesh cases: with fragment active, all 1024 pixels must be white; with mesh active, the storage buffer must contain
  `0, 1, 2, 3` ([mesh checks](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L1199-L1238)).
- Creation and binding themselves are implicit checks: an implementation that rejects a legal linked/unlinked split or bind
  layout fails the case through validation layers or a returned error before any output exists.
- All checks are exact host-side comparisons after copyback; there is no tolerance.

## Behavior Parameter Identification

> **Behavior parameter:** behavioral group over the registered intermediate nodes, with two secondary registered axes.
>
> **Primary axis candidate values:** graphics linked/unlinked combinations (the 16 `linked_*` / `unlinked_*` groups),
> next-stage chain cases (`next_stage` leaves), mesh/task combinations (the 5 `mesh_*` groups).
>
> **Secondary axis 1 (bind mode):** `separate`, `one_linked_unlinked`, `all`.
>
> **Secondary axis 2 (creation/binding ordering):** `default`, `random_order`, `separate_link`.

## What Failure Means

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

## Important Variations and Special Cases

- **Compute shader in the linked batch.** The `comp2` compute shader is appended to every linked batch without the link
  flag. This is legal because the all-linked-or-none rule covers only graphics stages (and separately task/mesh); compute is
  exempt. It also means cases with no linked stage never create `comp2` at all.
- **`one_linked_unlinked` split rule.** The first non-unused stage in stage order joins all unlinked stages in the first
  binding call; every remaining linked stage is bound in a second call. Before both, all five graphics stages are unbound.
- **`separate_link` nextStage widening.** Because each linked shader is created alone, VUID -08409 does not constrain its
  `nextStage`; the case uses the full per-stage masks (for example vertex declaring tessellation control, geometry, and
  fragment together).
- **No-fragment verification path.** When fragment is `UNUSED`, the last active pre-fragment stage (geometry, else
  tessellation evaluation, else vertex) writes `1..4` into the storage buffer, and the image is cleared but not checked.
- **`identically_defined_layouts`.** Four descriptor set layout objects with identical definitions are distributed across
  stages to confirm that layout compatibility is by value, not by object identity.
- **Graphics support check is broader than the per-combination need.** `ShaderObjectLinkCase::checkSupport` ORs the
  tessellation-control and geometry bits into the `vertNextStage`/`teseNextStage` tests
  ([vktShaderObjectLinkTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L742-L754)). Because a
  bitwise OR with a nonzero bit is always nonzero, every graphics link case (including vertex+fragment-only combinations)
  requires both `tessellationShader` and `geometryShader` features. A bitwise AND was probably intended. This is an
  unresolved source-level concern; per audit rules the source is not modified and the wiki only states the observed
  requirement.
- **Mesh support check.** Mesh cases always require `VK_EXT_mesh_shader` with both `taskShader` and `meshShader` features,
  even for combinations whose task shader is `UNUSED`
  ([vktShaderObjectLinkTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L1323-L1333)).

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Per-stage link state, bind type, nextStage parameter structs | [vktShaderObjectLinkTests.cpp#L45-L104](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L45-L104) | Defines the three link states, bind types, and parameter payloads. |
| Graphics `getNextStage()` | [vktShaderObjectLinkTests.cpp#L130-L191](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L130-L191) | Computes exact next linked stage or the fallback mask per stage. |
| Graphics shader creation and batching | [vktShaderObjectLinkTests.cpp#L304-L464](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L304-L464) | Splits linked batch vs individual unlinked creation, random order swap, separate-link creation. |
| Graphics bind modes | [vktShaderObjectLinkTests.cpp#L487-L593](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L487-L593) | Implements `separate`, `one_linked_unlinked`, and `all` binding. |
| Graphics verification | [vktShaderObjectLinkTests.cpp#L661-L717](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L661-L717) | Image region check and storage buffer check. |
| Graphics support check | [vktShaderObjectLinkTests.cpp#L742-L754](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L742-L754) | Extension and feature gates, including the broad tessellation/geometry requirement. |
| Mesh instance | [vktShaderObjectLinkTests.cpp#L834-L1241](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L834-L1241) | Mesh/task/fragment creation (including `NO_TASK_SHADER` flag), binding, draw, and checks. |
| Registration | [vktShaderObjectLinkTests.cpp#L1351-L1650](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L1351-L1650) | Builds the 16 combination groups, `next_stage` group, and 5 mesh groups. |
| Shared shader sources and helpers | [vktShaderObjectCreateUtil.cpp#L58-L211](../../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.cpp#L58-L211), [vktShaderObjectCreateUtil.cpp#L244-L489](../../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.cpp#L244-L489) | Basic GLSL set, `makeShaderCreateInfo`, dynamic-state setup, bind helpers. |
| Mustpass evidence | [link.txt](../../../mustpass/main/vk-default/shader-object/link.txt) | All 161 registered link case paths. |

## Questions / Risk Points for User Audit

- Is the three-cluster behavioral group the right primary axis, with bind mode and ordering as secondary axes, rather than
  treating the 16 combination groups individually?
- The `checkSupport` OR-expression makes tessellation and geometry support mandatory for all graphics link cases. The wiki
  will state this factually; the suspected `|`-vs-`&` defect is reported here and left unfixed per audit rules. Should the
  final page flag it explicitly as a likely test defect, or only describe the requirement?
- Spec grounding came from the official Vulkan specification (the `external/vulkan-docs` tree is not vendored in this
  checkout). Are the cited rules (link-flag scope, per-stage `nextStage` masks, multi-call binding of linked shaders)
  consistent with the intended pinned spec revision?
- The shaders are trivial (white output, index writes) and incidental to the tested property; the plan is a no-walkthrough
  `## Shader Analysis` with a `walkthrough_exceptions.py` entry. Confirm this matches the lead's pre-approval.

## Conversion Notes for Final Wiki Rewrite

- Distill the three Background Knowledge topics (linked vs unlinked creation, `nextStage` rules, linked binding) into a
  short prerequisite bullet list; keep the VUID-grounded statements but drop tutorial padding.
- The concrete example becomes prose support inside `## Behavior Parameters` and `## Runtime Execution and Result Checking`;
  no shader walkthrough is planned.
- Copy the three failure-cause tables directly into `## Failure Meaning` → `### Failure Cause Mapping`; write
  `### Cause Analysis` fresh during the rewrite.
- Feature requirements, including the broader-than-needed tessellation/geometry gate and the mesh feature gate, go to
  `### Requirement-based pruning`. The `comp2`-in-batch and layout-identity variations go to
  `### Design-based pruning` or `## Important Variations` content folded into the page body.
- Keep the mustpass-backed tree (22 direct children under `shader_object.link`) as the `## Registration Hierarchy` fence.
