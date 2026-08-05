## Overview

**Core question:** Does an implementation correctly record, suspend, resume, and execute dynamic rendering instances across primary and secondary command buffers, and does it honor partial depth/stencil attachment binding when a rendering instance names only one aspect of a packed depth/stencil image?

`DynamicRendering` is the `basic` test family under `renderpasses.dynamic_rendering.primary_cmd_buff`. It is implemented entirely by [`vktDynamicRenderingTests.cpp`](../../../modules/vulkan/renderpass/vktDynamicRenderingTests.cpp), which defines a shared `DynamicRenderingTestInstance` base class and a set of subclasses that override only the command-buffer recording step. Each test case draws two triangles into color, depth, and stencil attachments using the `VK_KHR_dynamic_rendering` begin/end rendering commands, then copies the attachments back to host-visible buffers and compares them against reference images.

The family exercises four interaction surfaces of dynamic rendering: a single self-contained rendering instance in a primary command buffer, suspending and resuming a render pass instance across one or more command buffers, executing secondary command buffers inside a rendering instance with `VK_RENDERING_CONTENTS_SECONDARY_COMMAND_BUFFERS_BIT_KHR`, and partial binding of a packed depth/stencil image. The `endRendering2` flag is folded across the whole matrix: every test case leaf is instantiated twice, once with `vkCmdEndRendering` and once with `vkCmdEndRendering2KHR`.

## Background Knowledge

- Dynamic rendering replaces render-pass objects and framebuffers with `vkCmdBeginRendering`/`vkCmdEndRendering`. The `VK_KHR_dynamic_rendering` extension (core in Vulkan 1.3) supplies these commands. A render pass instance is the unit of work between a begin and the matching end.
- A render pass instance may be **suspended** with `VK_RENDERING_SUSPENDING_BIT_KHR` and later **resumed** with `VK_RENDERING_RESUMING_BIT_KHR`. The spec requires that the contents of the `VkRenderingInfo` match between the suspended instance and the resuming one, except for the suspending, resuming, and contents flags. No action, synchronization, or other render pass instance commands are allowed between the two.
- A primary command buffer may delegate the contents of a rendering instance to secondary command buffers by passing `VK_RENDERING_CONTENTS_SECONDARY_COMMAND_BUFFERS_BIT_KHR` to `vkCmdBeginRendering` and then calling `vkCmdExecuteCommands`. The secondary command buffer must be begun with `VK_COMMAND_BUFFER_USAGE_RENDER_PASS_CONTINUE_BIT` and a `VkCommandBufferInheritanceRenderingInfoKHR` that names the attachment formats.
- `vkCmdEndRendering2KHR` (from `VK_KHR_maintenance10`) performs the same end as `vkCmdEndRendering` but takes the parameters through a `VkRenderingEndInfoKHR` struct. The `endRendering2` dimension checks that both entry points are accepted and produce identical results.
- `VK_EXT_dynamic_rendering_unused_attachments` relaxes the rule that every attachment named in `VkRenderingInfo` must be bound. Partial binding lets a rendering instance bind only the depth aspect or only the stencil aspect of a packed depth/stencil image while the unbound aspect is left untouched.

## Registration Hierarchy

```text
renderpasses.dynamic_rendering.primary_cmd_buff.basic
```

The `basic` group is created by [`createDynamicRenderingBasicTests`](../../../modules/vulkan/renderpass/vktDynamicRenderingTests.cpp#L3728-L3750). It contains 30 direct test case leaves: 15 `TestType` values, each instantiated once with `endRendering2=false` and once with `endRendering2=true` (which appends `_end_rendering_2` to the leaf name).

The `basic` group is one of several groups registered under `primary_cmd_buff` by the shared function [`createRenderPassTestsInternal`](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8486-L8612). That function builds the `suballocation`, `dedicated_allocation`, and `no_draws` subtrees as siblings of `basic`, and then dispatches into many other render-pass source files whose behavior is outside this page. The `dynamic_rendering` families are registered through four sibling roots (`primary_cmd_buff`, `partial_secondary_cmd_buff`, `complete_secondary_cmd_buff`, `graphics_pipeline_library`) via [`createDynamicRenderingTests`](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8638-L8679). The `basic` group itself appears only under `primary_cmd_buff`, because the dispatcher guards it on `useSecondaryCmdBuffer == false`.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| `TestType` | 15 values | The behavioral axis: which command-buffer topology and which dynamic-rendering feature is exercised | [enum definition](../../../modules/vulkan/renderpass/vktDynamicRenderingTests.cpp#L72-L123), [name table](../../../modules/vulkan/renderpass/vktDynamicRenderingTests.cpp#L3703-L3719) |
| `endRendering2` | `false`, `true` | Selects `vkCmdEndRendering` versus `vkCmdEndRendering2KHR`; `true` appends `_end_rendering_2` to the leaf name | [registration loop](../../../modules/vulkan/renderpass/vktDynamicRenderingTests.cpp#L3733-L3747) |
| Color format | `VK_FORMAT_R8G8B8A8_UNORM` | Fixed across the family; up to four color attachments | [parameters](../../../modules/vulkan/renderpass/vktDynamicRenderingTests.cpp#L3741) |
| Render size | 32x32 | Fixed | [parameters](../../../modules/vulkan/renderpass/vktDynamicRenderingTests.cpp#L3742) |
| Attachment load op | `LOAD`, `CLEAR`, `DONT_CARE` | Iterated inside each leaf; verification runs only on the `CLEAR`/`STORE` combination | [rendering loop](../../../modules/vulkan/renderpass/vktDynamicRenderingTests.cpp#L912-L913) |
| Attachment store op | `STORE`, `DONT_CARE` | Iterated inside each leaf | [rendering loop](../../../modules/vulkan/renderpass/vktDynamicRenderingTests.cpp#L913) |

The load-op and store-op iteration is internal: it does not expand the registered leaf count. Each leaf re-runs its recording and verification across the full load/store matrix, but only validates results for the `CLEAR`/`STORE` pair. The reference image is the same for every leaf, so the comparison confirms that the topology change did not alter the rendered output.

## Behavior Parameters

The primary behavioral axis is `TestType`. It groups into four mechanisms. The `endRendering2` doubling is orthogonal and is covered separately at the end of this section.

### single_cmdbuffer: one self-contained rendering instance

The base case. One primary command buffer begins rendering, binds the pipeline and vertex buffer, draws the triangles, and ends rendering. No suspending, resuming, or secondary command buffers are involved. This is the reference topology against which every other leaf varies.

### *_resuming: suspending and resuming across command buffers

These leaves split the rendering work across two render pass instances that are logically one. The first instance is begun with `VK_RENDERING_SUSPENDING_BIT_KHR`; the second is begun with `VK_RENDERING_RESUMING_BIT_KHR`. The spec forbids any intervening action or synchronization commands between them.

The `_resuming` suffix covers several command-buffer topologies:

- `single_cmdbuffer_resuming`: both instances are recorded into the same primary command buffer.
- `2_cmdbuffers_resuming`: the suspending instance is in one primary command buffer and the resuming instance is in a second primary command buffer, submitted together.
- `2_secondary_cmdbuffers_resuming`: the two instances are recorded into two secondary command buffers, both executed by a single primary command buffer.
- `2_secondary_2_primary_cmdbuffers_resuming`: the two secondary command buffers are executed by two separate primary command buffers.

In all resuming leaves the two halves draw complementary triangle sets, so the final image must match the single-instance reference exactly. Splitting the work must not lose or duplicate any attachment state.

### contents_*: secondary command buffers inside a rendering instance

These leaves begin rendering in the primary command buffer with `VK_RENDERING_CONTENTS_SECONDARY_COMMAND_BUFFERS_BIT_KHR` and then call `vkCmdExecuteCommands`. The draw commands are recorded into one or more secondary command buffers begun with `VK_COMMAND_BUFFER_USAGE_RENDER_PASS_CONTINUE_BIT` and a `VkCommandBufferInheritanceRenderingInfoKHR` that names the attachment formats.

The `contents_*` prefix covers how many secondary command buffers are used and whether they themselves suspend and resume:

- `contents_secondary_cmdbuffers`: one secondary command buffer inside one render pass instance.
- `contents_2_secondary_cmdbuffers`: two secondary command buffers inside one render pass instance.
- `contents_2_secondary_cmdbuffers_resuming`: two secondary command buffers, the first suspending and the second resuming, both executed by one primary command buffer.
- `contents_2_secondary_2_primary_cmdbuffers_resuming`: two secondary command buffers across two primary command buffers.

A further four leaves mix a draw recorded directly in the primary command buffer with a draw recorded in a secondary command buffer, across one or two primary command buffers. These are `contents_primary_secondary_cmdbuffers_resuming`, `contents_secondary_primary_cmdbuffers_resuming`, `contents_2_primary_secondary_cmdbuffers_resuming`, and `contents_secondary_2_primary_cmdbuffers_resuming`. The name encodes the order: the primary-buffer draw comes first or second, and the primary command buffer count is one or two.

### secondary_cmdbuffer_out_of_rendering_commands: mixing inside and outside rendering in a secondary

This leaf records the entire begin/draw/end rendering sequence inside a single secondary command buffer, followed by a copy-image-to-buffer command. The secondary is then executed by a primary command buffer. It checks that a secondary command buffer can both contain a dynamic rendering instance and perform post-rendering transfer work, mixing render-pass-continue semantics with out-of-rendering commands.

### partial_binding_depth_stencil: binding one aspect of a packed depth/stencil image

This leaf exercises `VK_EXT_dynamic_rendering_unused_attachments`. It begins a rendering instance whose depth/stencil attachment image view names a packed format, but the `VkRenderingAttachmentInfo` binds only one aspect (depth or stencil). The unbound aspect must be left at its pre-rendering contents.

The leaf runs several sub-cases internally. When exactly one of depth or stencil is enabled, it runs four combinations of `clearOnly` (clear versus clear-plus-draw) and `useSecondary` (primary command buffer versus secondary command buffer), each under both `VK_ATTACHMENT_LOAD_OP_LOAD` and `VK_ATTACHMENT_LOAD_OP_CLEAR`. When both depth and stencil are present, it runs `secondaryUndefinedFormatTest`, which records a secondary command buffer whose `VkCommandBufferInheritanceRenderingInfoKHR` reports `VK_FORMAT_UNDEFINED` for one aspect while the primary rendering instance also unbinds that same aspect; the test verifies that the secondary is accepted with an undefined inheritance format and that the unbound aspect is preserved. In every sub-case the unbound aspect is pre-cleared to a sentinel value and the test confirms that value survives unchanged.

### endRendering2: the orthogonal doubling

Every `TestType` value above is also instantiated with `endRendering2=true`, producing a leaf with `_end_rendering_2` appended. That leaf calls `vkCmdEndRendering2KHR` with a `VkRenderingEndInfoKHR` instead of `vkCmdEndRendering`. The expected output is identical, so the doubling checks that the maintenance10 struct-based end command is accepted by the same recording paths and produces the same attachment contents.

## Shader Analysis

The shader pair is trivial and is not the observed behavior. The vertex shader ([source](../../../modules/vulkan/renderpass/vktDynamicRenderingTests.cpp#L3588-L3604)) passes through `position` and derives a color from `gl_Position.z`. The fragment shader ([source](../../../modules/vulkan/renderpass/vktDynamicRenderingTests.cpp#L3608-L3627)) writes a per-attachment color to up to four color outputs. The depth and stencil values exercised by the test come from fixed-function rasterization and stencil state set in [`makeGraphicsPipeline`](../../../modules/vulkan/renderpass/vktDynamicRenderingTests.cpp#L267-L460), not from shader logic. A representative walkthrough would not add information beyond the source listing, because the correctness question is command-buffer recording and attachment binding, not shader execution.

## Runtime Execution and Result Checking

Each leaf overrides `DynamicRenderingTestInstance::rendering` and shares a common host-side harness:

- Resource setup ([constructor](../../../modules/vulkan/renderpass/vktDynamicRenderingTests.cpp#L780-L891)): creates four color attachment images, one packed depth/stencil image, host-visible readback buffers, a vertex buffer with three triangle vertices, the graphics pipeline, and reference images for color, depth, and stencil.
- Recording loop ([example](../../../modules/vulkan/renderpass/vktDynamicRenderingTests.cpp#L903-L984)): for each combination of attachment load op and store op, the leaf records `preBarier` to transition images to attachment-optimal, begins rendering, draws the triangles, ends rendering, and copies the attachments to readback buffers.
- Verification gate ([example](../../../modules/vulkan/renderpass/vktDynamicRenderingTests.cpp#L942-L983)): results are checked only for the `VK_ATTACHMENT_LOAD_OP_CLEAR` and `VK_ATTACHMENT_STORE_OP_STORE` combination. When that combination runs, the test records a second pass that uses `vkCmdClearAttachments` to clear sub-regions of the attachments, then verifies again against the reference.
- Color comparison: `tcu::floatThresholdCompare` against the reference image with a per-component threshold of `Vec4(0.02f)` ([verifyResults](../../../modules/vulkan/renderpass/vktDynamicRenderingTests.cpp#L1185-L1215)).
- Depth comparison: `verifyDepth` compares the copied depth buffer against the depth reference, handling the `VK_FORMAT_D24_UNORM_S8_UINT` packed-layout special case ([verifyDepth](../../../modules/vulkan/renderpass/vktDynamicRenderingTests.cpp#L1217-L1255)).
- Stencil comparison: `verifyStencil` compares the copied stencil buffer against the stencil reference with a zero threshold ([verifyStencil](../../../modules/vulkan/renderpass/vktDynamicRenderingTests.cpp#L1256-L1272)).

The resuming leaves submit the suspending and resuming command buffers together with a single `submitCommandsAndWait` call so that no other work intervenes, matching the spec constraint.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `single_cmdbuffer` | Basic dynamic rendering begin/draw/end path is broken for this attachment and format combination |
| `*_resuming` (all) | Attachment state is not correctly preserved across a suspend/resume boundary, or the implementation rejects the suspending or resuming flag |
| `contents_*` (all) | Secondary command buffer inheritance info or `CONTENTS_SECONDARY_COMMAND_BUFFERS_BIT` execution is mishandled, so draws recorded in secondaries do not reach the attachments |
| `secondary_cmdbuffer_out_of_rendering_commands` | A secondary command buffer cannot mix a dynamic rendering instance with post-rendering transfer commands |
| `partial_binding_depth_stencil` | The implementation writes to, clears, or reinitializes the unbound aspect of a packed depth/stencil image, or rejects a valid partial binding |
| `*_end_rendering_2` (all) | The maintenance10 `vkCmdEndRendering2KHR` path diverges from the `vkCmdEndRendering` path |
| Shared infrastructure | Reference image generation, copy-image-to-buffer layout transitions, or the color/depth/stencil compare helpers are wrong |

### Cause Analysis

#### Suspend/resume state preservation

**Possible failure symptoms:** A resuming leaf produces an attachment that is missing the triangles drawn in the suspending half, shows the clear color instead of the drawn geometry, or differs from the `single_cmdbuffer` reference.

**Possible implementation causes:** The implementation may flush attachment contents at `vkCmdEndRendering` when `VK_RENDERING_SUSPENDING_BIT_KHR` is set instead of retaining them for the resuming instance, or it may treat the resuming instance as a fresh clear. Per the spec, the `VkRenderingInfo` contents must match between the suspended and resuming instances except for the flag bits, and no intervening work is allowed; a driver that injects an implicit barrier or clear between the two halves would produce this symptom.

#### Secondary command buffer execution

**Possible failure symptoms:** A `contents_*` leaf produces a blank or partially drawn attachment, indicating that draws recorded into a secondary command buffer were not executed against the rendering instance.

**Possible implementation causes:** The `VkCommandBufferInheritanceRenderingInfoKHR` format list may not be propagated correctly to pipeline compatibility checks for the secondary, or `VK_RENDERING_CONTENTS_SECONDARY_COMMAND_BUFFERS_BIT_KHR` may not route `vkCmdExecuteCommands` into the active rendering instance. The inheritance info also carries the rendering flags; a mismatch in the suspending or resuming bit between the secondary and the primary begin could cause the secondary to be rejected or mis-executed.

#### Partial depth/stencil binding

**Possible failure symptoms:** The unbound aspect (depth or stencil) of the packed image does not match the sentinel value written before rendering, or the bound aspect is cleared or drawn to the wrong region.

**Possible implementation causes:** When `VK_EXT_dynamic_rendering_unused_attachments` allows partial binding, the implementation may still initialize the whole packed image on `VK_ATTACHMENT_LOAD_OP_CLEAR`, or may write both aspects during the draw. The `secondaryUndefinedFormatTest` sub-case adds inheritance-info variation: the secondary command buffer's `VkCommandBufferInheritanceRenderingInfoKHR` reports `VK_FORMAT_UNDEFINED` for one aspect while the primary rendering instance also unbinds that same aspect; the draw clears both aspects inside the secondary and the test verifies the unbound aspect retains its sentinel value. A driver that rejects an undefined inheritance format for an aspect, or that writes the unbound aspect despite it being unbound by both the secondary and the primary, would fail this sub-case.

#### endRendering2 divergence

**Possible failure symptoms:** An `_end_rendering_2` leaf fails where the corresponding non-`2` leaf passes, with identical attachment contents otherwise expected.

**Possible implementation causes:** The two commands must produce identical recording. A divergence points to the maintenance10 struct-based path taking a different code path than the direct command, for example skipping a state update that `vkCmdEndRendering` performs.

#### Shared infrastructure

**Possible failure symptoms:** Every leaf in the family fails identically, including `single_cmdbuffer`.

**Possible implementation causes:** A defect in the copy-image-to-buffer layout transitions in `copyImgToBuff` or in the reference image generation would surface across the whole family rather than on a single topology. This is also the expected failure mode if `VK_KHR_dynamic_rendering` itself is not supported and the case is not skipped.

## Case Pruning

### Requirement-based pruning

- `VK_KHR_dynamic_rendering` is required for every leaf ([checkSupport](../../../modules/vulkan/renderpass/vktDynamicRenderingTests.cpp#L3571-L3572)).
- `VK_KHR_maintenance10` is required when `endRendering2` is true ([checkSupport](../../../modules/vulkan/renderpass/vktDynamicRenderingTests.cpp#L3574-L3575)).
- `VK_EXT_dynamic_rendering_unused_attachments` is required only for `partial_binding_depth_stencil` ([checkSupport](../../../modules/vulkan/renderpass/vktDynamicRenderingTests.cpp#L3578-L3582)).
- The whole `basic` group is registered only under `primary_cmd_buff`. The dispatcher in `createRenderPassTestsInternal` guards `createDynamicRenderingBasicTests` on `useSecondaryCmdBuffer == false`, so the group does not appear under `partial_secondary_cmd_buff`, `complete_secondary_cmd_buff`, or `graphics_pipeline_library` ([registration](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8530-L8540)).

### Design-based pruning

- Verification runs only for the `VK_ATTACHMENT_LOAD_OP_CLEAR` and `VK_ATTACHMENT_STORE_OP_STORE` combination. The other load/store combinations are recorded and submitted to exercise the recording path, but their results are not compared, because the reference image assumes a clear-and-store sequence ([gate](../../../modules/vulkan/renderpass/vktDynamicRenderingTests.cpp#L942-L943)).
- The depth/stencil format is selected at runtime by `getSupportedStencilFormat` rather than enumerated as a parameter, so there is no per-format leaf expansion ([setup](../../../modules/vulkan/renderpass/vktDynamicRenderingTests.cpp#L838)).

## Key Takeaways

- The family is a topology matrix, not a shader or format matrix. The shader and attachment configuration are fixed; what changes between leaves is how the rendering instance is recorded and executed.
- Suspend/resume and secondary-command-buffer execution are the two interactions that can silently lose or duplicate work. A resuming leaf failing where `single_cmdbuffer` passes isolates the problem to the suspend/resume boundary; a `contents_*` leaf failing under the same condition isolates it to secondary execution.
- `partial_binding_depth_stencil` is the only leaf that depends on `VK_EXT_dynamic_rendering_unused_attachments` and the only one that checks aspect-level binding semantics for packed depth/stencil images.
- The `endRendering2` doubling is a pure command-entry-point regression check; a divergence between a leaf and its `_end_rendering_2` twin localizes the defect to the maintenance10 end path.
- The `basic` group shares its registration path with the `suballocation`, `dedicated_allocation`, and `no_draws` subtrees through `createRenderPassTestsInternal`, but those subtrees belong to other source files and other Level-3 pages.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `TestType` enum and per-value comments | [vktDynamicRenderingTests.cpp#L72-L123](../../../modules/vulkan/renderpass/vktDynamicRenderingTests.cpp#L72-L123) | Authoritative description of each behavioral axis value |
| `TestParameters` struct | [vktDynamicRenderingTests.cpp#L143-L152](../../../modules/vulkan/renderpass/vktDynamicRenderingTests.cpp#L143-L152) | Fields that parameterize every leaf |
| `beginRendering` helper | [vktDynamicRenderingTests.cpp#L1044-L1137](../../../modules/vulkan/renderpass/vktDynamicRenderingTests.cpp#L1044-L1137) | Builds `VkRenderingInfo` and the attachment info list |
| `endRendering` helper | [vktDynamicRenderingTests.cpp#L1139-L1149](../../../modules/vulkan/renderpass/vktDynamicRenderingTests.cpp#L1139-L1149) | Selects `vkCmdEndRendering` or `vkCmdEndRendering2KHR` |
| `beginSecondaryCmdBuffer` helper | [vktDynamicRenderingTests.cpp#L565-L599](../../../modules/vulkan/renderpass/vktDynamicRenderingTests.cpp#L565-L599) | Builds the `VkCommandBufferInheritanceRenderingInfoKHR` |
| `DynamicRenderingTestInstance::rendering` (base) | [vktDynamicRenderingTests.cpp#L903-L984](../../../modules/vulkan/renderpass/vktDynamicRenderingTests.cpp#L903-L984) | The `single_cmdbuffer` recording loop |
| `SingleCmdBufferResuming::rendering` | [vktDynamicRenderingTests.cpp#L1290-L1381](../../../modules/vulkan/renderpass/vktDynamicRenderingTests.cpp#L1290-L1381) | Representative suspend/resume recording |
| `ContentsSecondaryCmdBuffer::rendering` | [vktDynamicRenderingTests.cpp#L1845-L1940](../../../modules/vulkan/renderpass/vktDynamicRenderingTests.cpp#L1845-L1940) | Representative `CONTENTS_SECONDARY` recording |
| `SecondaryCmdBufferOutOfRenderingCommands::rendering` | [vktDynamicRenderingTests.cpp#L3018-L3116](../../../modules/vulkan/renderpass/vktDynamicRenderingTests.cpp#L3018-L3116) | Mixed in-rendering and out-of-rendering secondary |
| `PartialBindingDepthStencil::rendering` | [vktDynamicRenderingTests.cpp#L3497-L3543](../../../modules/vulkan/renderpass/vktDynamicRenderingTests.cpp#L3497-L3543) | Dispatch over partial-binding sub-cases |
| `PartialBindingDepthStencil::baseTest` | [vktDynamicRenderingTests.cpp#L3178-L3321](../../../modules/vulkan/renderpass/vktDynamicRenderingTests.cpp#L3178-L3321) | Partial-binding clear and draw verification |
| `verifyResults`, `verifyDepth`, `verifyStencil` | [vktDynamicRenderingTests.cpp#L1185-L1272](../../../modules/vulkan/renderpass/vktDynamicRenderingTests.cpp#L1185-L1272) | Color, depth, and stencil comparison helpers |
| `createInstance` dispatch | [vktDynamicRenderingTests.cpp#L3631-L3699](../../../modules/vulkan/renderpass/vktDynamicRenderingTests.cpp#L3631-L3699) | Maps `TestType` to the subclass |
| `createDynamicRenderingBasicTests` | [vktDynamicRenderingTests.cpp#L3728-L3750](../../../modules/vulkan/renderpass/vktDynamicRenderingTests.cpp#L3728-L3750) | Registers the `basic` group and the `endRendering2` doubling |
| `createRenderPassTestsInternal` | [vktRenderPassTests.cpp#L8486-L8612](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8486-L8612) | Shared dispatcher that places `basic` beside `suballocation`, `dedicated_allocation`, and `no_draws` |
| `createDynamicRenderingTests` | [vktRenderPassTests.cpp#L8638-L8679](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8638-L8679) | Registers the four `dynamic_rendering` roots |
| Spec: render pass suspension | [renderpass.adoc#L995-L1002](../../../../vulkan-docs/src/chapters/renderpass.adoc#L995-L1002) | Suspending and resuming constraints |
