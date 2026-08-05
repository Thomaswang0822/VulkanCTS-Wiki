## Overview

**Core question:** When a dynamic render pass instance and the pipeline bound inside it disagree about which color, depth, and stencil attachments are used, does the implementation still write exactly the pixels the active path should write and leave every other attachment at its clear value?

- This page covers the `unused_attachments` test family implemented in
  [vktDynamicRenderingUnusedAttachmentsTests.cpp](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp).
- The family is registered under the `renderpasses` test category, attached to two
  dynamic-rendering intermediate nodes: `primary_cmd_buff`
  ([vktRenderPassTests.cpp#L8534](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8534)) and
  `partial_secondary_cmd_buff`
  ([vktRenderPassTests.cpp#L8543](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8543)). It is
  excluded from Vulkan SC builds.
- The family exercises `VK_EXT_dynamic_rendering_unused_attachments`, which lifts the
  `VK_KHR_dynamic_rendering` requirement that the render pass instance and every bound pipeline agree on
  attachment count, attachment presence, and attachment formats.
- Each case renders a single fullscreen triangle into one or more 1x1 attachment images, then compares
  every attachment against a host-precomputed expected value. The expected value is the fragment color
  when the attachment was written, and the pre-render clear value otherwise.
- The family is generated from a small number of parameter masks (attachment count, format mask, handle
  mask, layer mask, depth/stencil booleans), so one case can be understood by reading how each mask bit
  controls whether an attachment is "used" on the pipeline side, the framebuffer side, or both.

## Background Knowledge

- **Dynamic rendering attachment state.** Under `VK_KHR_dynamic_rendering`, a render pass instance is described by a
  `VkRenderingInfo` that lists color attachments through an array of `VkRenderingAttachmentInfo`, plus optional depth and
  stencil attachments. Each `VkRenderingAttachmentInfo` carries an `imageView`; passing `VK_NULL_HANDLE` marks that attachment
  slot as unused for the render pass instance. A pipeline that will draw inside the instance is created with a
  `VkPipelineRenderingCreateInfo` whose `colorAttachmentCount`, `pColorAttachmentFormats`,
  `depthAttachmentFormat`, and `stencilAttachmentFormat` describe the attachment layout the pipeline was compiled against.
- **The unused-attachments restriction this extension lifts.** Without `VK_EXT_dynamic_rendering_unused_attachments`, the spec
  requires the render pass instance and every bound pipeline to agree on `colorAttachmentCount`
  (VUID-`{refpage}`-colorAttachmentCount-06179) and requires a non-`NULL` framebuffer attachment view to match a defined
  pipeline format while a `VK_NULL_HANDLE` view requires `VK_FORMAT_UNDEFINED`
  (VUID-`{refpage}`-dynamicRenderingUnusedAttachments-08910 through 08918). When the
  `dynamicRenderingUnusedAttachments` feature is enabled, those VUIDs relax: the pipeline format may stay defined when the
  framebuffer view is `VK_NULL_HANDLE` (as long as the attachment is unused), the render and pipeline attachment counts may
  differ, and the view-format-versus-pipeline-format link is loosened for unused slots.
- **Pipeline-side versus framebuffer-side unused.** An attachment can be unused on the pipeline side (its entry in
  `pColorAttachmentFormats` is `VK_FORMAT_UNDEFINED`, or it is beyond the pipeline's `colorAttachmentCount`) or on the
  framebuffer side (its `VkRenderingAttachmentInfo::imageView` is `VK_NULL_HANDLE`). A slot can be unused on one side and used
  on the other; the test enumerates exactly those combinations and verifies the active side still works.

## Registration Hierarchy

```text
renderpasses.dynamic_rendering.primary_cmd_buff.unused_attachments
├── comb
├── bad_formats
├── extra_att
├── extra_pipe_att
├── extra_render_att
└── misc
```

The `unused_attachments` test family is created by
[createDynamicRenderingUnusedAttachmentsTests](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L1593-L1807),
which is called once with `useSecondaries = false` for the `primary_cmd_buff` intermediate node
([vktRenderPassTests.cpp#L8534](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8534)) and once with
`useSecondaries = true` for the `partial_secondary_cmd_buff` intermediate node
([vktRenderPassTests.cpp#L8543](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8543)). The same six intermediate
nodes appear identically under both parents; the only difference is that the `partial_secondary_cmd_buff` variants record
draw commands inside a secondary command buffer using
`VK_RENDERING_CONTENTS_SECONDARY_COMMAND_BUFFERS_BIT`. The family is not registered under
`complete_secondary_cmd_buff` or `graphics_pipeline_library`.

The tree above uses `primary_cmd_buff` as the representative path. Below each intermediate node, every test case leaf is a
long synthesized name produced by [TestParams::getTestName](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L188-L204)
from the parameter masks; the full leaf matrix is described in [Parameter Dimensions and Observed Values](#parameter-dimensions-and-observed-values).

## Parameter Dimensions and Observed Values

The family is generated by nested loops over a fixed set of masks. Each leaf name encodes the parameter combination, for
example `pipe_4_frag_4_layers_1_mask_0x01_formats_0xffffffff_handles_0xaaaaaaaa_depth_no_undef_null_stencil_no_undef_null`.

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Pipe/framebuffer attachment count | `1`, `4`, `8` | Number of color attachments declared in both `VkPipelineRenderingCreateInfo::colorAttachmentCount` and `VkRenderingInfo::colorAttachmentCount` for the base cases. Counts beyond `maxColorAttachments` are pruned. | [attachmentCounts](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L1608-L1612) |
| Fragment attachment count | `1`, `4`, `8` | Number of fragment shader output declarations. Must be at least the pipe count so every pipeline slot has a matching fragment output. | [fragAtt loop](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L1626-L1657) |
| Layer count | `1`, `4` | Number of image array layers. Drives image creation extent and the per-layer verification loop. | [layerCounts](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L1613-L1616) |
| Layer mask | `0xFFFFFFFF`, `0x00000000`, `0x55555555`, `0xAAAAAAAA` | Selects which layers are written. In multiview mode this becomes the `viewMask`; in manual mode the host skips layers whose bit is clear. | [masksToTest](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L1617-L1622) |
| Format mask | `0xFFFFFFFF`, `0x00000000`, `0x55555555`, `0xAAAAAAAA` | Per color attachment bit. A set bit means `VK_FORMAT_R8G8B8A8_UINT` in `pColorAttachmentFormats`; a clear bit means `VK_FORMAT_UNDEFINED`, marking the slot unused on the pipeline side. | [getPipelineFormatVector](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L232-L235) |
| Handle mask | `0xFFFFFFFF`, `0x00000000`, `0x55555555`, `0xAAAAAAAA` | Per color attachment bit. A set bit means a valid `VkImageView` in `VkRenderingAttachmentInfo::imageView`; a clear bit means `VK_NULL_HANDLE`, marking the slot unused on the framebuffer side. | [getRenderingAttachmentInfos](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L269-L297) |
| Depth present / defined / valid handle | `false`, `true` each | Whether the pipeline carries a depth attachment, whether its pipeline format is defined, and whether its framebuffer view is a valid handle. | [depth booleans](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L1660-L1712) |
| Stencil present / defined / valid handle | `false`, `true` each | Same three-state shape for the stencil attachment. | [stencil booleans](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L1667-L1712) |
| Multiview | `false`, `true` | When true, the layer mask is passed as `VkRenderingInfo::viewMask` and requires `VK_KHR_multiview`. When false, the host iterates layers manually with a push constant. | [multiview loop](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L1642-L1654) |

### Intermediate-node-specific dimensions

The six registered intermediate nodes each exercise a different slice of the unused-attachment space.

| Intermediate node | Extra dimensions | Registered leaves under `primary_cmd_buff` |
|----------|------------------|--------------------------------------------|
| `comb` (color) | `pipeAtt` x `fragAtt` x `layerCount` x `layerMask` x `formatMask` x `handleMask` x `multiview` | large matrix, see [color loop](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L1624-L1657) |
| `comb` (depth_stencil) | `depthPresent/Defined/ValidHandle` x `stencilPresent/Defined/ValidHandle` x `layerCount` x `layerMask` x `multiview` | see [depth/stencil loop](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L1659-L1712) |
| `bad_formats` | `formatMask` x `handleMask`, with `wrongFormatWithNullViews = true` | [bad format loop](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L1719-L1731) |
| `extra_att` | `attCount` x `formatMask` x `handleMask`, with `largePipeAttCount = true` and `extraAttIsUnused = false` | [extra_att loop](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L1736-L1748) |
| `extra_pipe_att` | `attCount` x `formatMask` x `handleMask`, with `largePipeAttCount = true` and `extraAttIsUnused = true` | [extra_pipe_att loop](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L1752-L1767) |
| `extra_render_att` | `attCount` x `formatMask` x `handleMask` x `extraAttIsUnused`, with `largeRenderAttCount = true` | [extra_render_att loop](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L1771-L1785) |
| `misc` | `dynamicDepthEnable` x `useSecondaries` | exactly two leaves: `color_used_then_unused` and `color_used_then_unused_dynamic_depth_enable` |

## Behavior Parameters

The primary behavioral axis is the **per-attachment used/unused pairing** between the pipeline side and the framebuffer side.
Each leaf fixes, for every color slot, whether `pColorAttachmentFormats[i]` is defined (pipeline-used) and whether
`pColorAttachments[i].imageView` is a valid handle (framebuffer-used); depth and stencil get the same three-state treatment.
The expected value for an attachment is determined entirely by whether that attachment is written, which requires it to be
used on both sides and to land in a written layer:

- a color attachment `i` in layer `L` is written when the pipeline format is defined, the framebuffer view is non-null, and
  bit `L` of the layer mask is set; its expected value is `uvec4(L, 255, i, 255)`;
- the depth attachment is written when `depthPresent && depthDefined && depthValidHandle` and the layer bit is set; its
  expected depth is `1.0`;
- the stencil attachment is written when `stencilPresent && stencilDefined && stencilValidHandle` and the layer bit is set;
  its expected stencil is `0xFF`.

Every other attachment keeps the pre-render clear value `{0, 0, 0, 0}`. The exact decision logic lives in the verification
loop ([imgWritten / depthWritten / stencilWritten](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L1028-L1081)).

### `comb`: count, layer, format, and handle combinations

The `comb` intermediate node enumerates the base matrix. Its `color` child node sweeps pipeline and fragment attachment counts, layer
counts, layer masks, format masks, handle masks, and multiview on/off; its `depth_stencil` child node fixes a single color
attachment and sweeps the three-state depth and stencil booleans. Together these leaves cover the relaxed VUID-06179 and
VUID-08910 through 08918 behavior: a slot can be pipeline-used but framebuffer-unused, framebuffer-used but
pipeline-unused, used on both, or unused on both.

### `bad_formats`: wrong format paired with a null view

The `bad_formats` intermediate node sets `wrongFormatWithNullViews = true`. When the framebuffer view is `VK_NULL_HANDLE`, the test
deliberately fills the corresponding pipeline format slot with a different format
([kBadColorFormat](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L59),
[alt depth/stencil format](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L723-L741)).
Without the extension this would be illegal; with the extension the unused slot's format is ignored, so the draw must still
succeed and the unused attachment must stay cleared.

### `extra_att`, `extra_pipe_att`, and `extra_render_att`: mismatched counts

These three intermediate nodes exercise the relaxed VUID-`{refpage}`-colorAttachmentCount-06179 rule, which under the extension no
longer requires the pipeline and render pass instance to report the same `colorAttachmentCount`.

- `extra_att` uses `largePipeAttCount = true` with `extraAttIsUnused = false`: the pipeline declares four extra color
  attachments beyond the framebuffer count, and those extras carry a real (wrong) format `kBadColorFormat`
  ([extra pipeline formats](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L743-L749)).
- `extra_pipe_att` uses `largePipeAttCount = true` with `extraAttIsUnused = true`: the pipeline again declares four extra
  attachments, but those extras are `VK_FORMAT_UNDEFINED`, so they are explicitly unused on the pipeline side.
- `extra_render_att` uses `largeRenderAttCount = true`: the render pass instance declares four extra attachments beyond the
  pipeline count. The `extraAttIsUnused` flag toggles whether those extra render attachments carry a real view
  (`VK_FORMAT_R8G8B8A8_UNORM`) or are `VK_NULL_HANDLE`.

### `misc`: an attachment used then unused across two render passes

The `misc` intermediate node has two leaves, `color_used_then_unused` and `color_used_then_unused_dynamic_depth_enable`
([usedThenUnusedRun](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L1176-L1587)). It is
the only intermediate node that records more than one render pass instance in the same command buffer. The first pass renders blue
into a color attachment with the depth attachment unused; the second pass drops the color attachment
(`colorAttachmentCount = 0` in `depthOnlyRenderInfo`) and binds a depth-enabled pipeline (or flips
`VK_DYNAMIC_STATE_DEPTH_TEST_ENABLE` on when `dynamicDepthEnable` is true). The color attachment must stay blue because the
second pass does not touch it, and the depth attachment must end at the vertex-written depth, proving an attachment can
transition from used to unused (color) and from unused to used (depth) across render pass boundaries under the extension.

## Shader Analysis

The shaders are simple and not the tested behavior; they exist only to write a deterministic value into every active
attachment so the host can distinguish written from cleared pixels. The tested behavior is whether the implementation honors
the used/unused pairing, so this page does not include a representative SPIR-V walkthrough.

The vertex shader
([vert](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L380-L391)) emits a fullscreen
triangle from `gl_VertexIndex` with no vertex inputs. When the case is not multiview but has more than one layer, it also
writes `gl_Layer` from a push constant so the host can target a specific layer
([vertExportsLayer](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L212-L215)). The shader
is built twice, once targeting SPIR-V 1.0 with the `ShaderViewportIndexLayerEXT` capability and once targeting SPIR-V 1.5
with the `ShaderLayer` capability, and the runtime picks the right module based on whether the context is Vulkan 1.2 or
later ([vert-spv10 / vert-spv15](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L417-L422)).

The fragment shader
([frag](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L434-L486)) is generated per case.
It declares `fragAttachmentCount` color outputs, skipping any output whose corresponding pipeline format is
`VK_FORMAT_UNDEFINED`, and writes `colorN = uvec4(layerIndex, 255, N, 255)` into each active output. The
`layerIndex` expression is `gl_ViewIndex` in multiview mode, `gl_Layer` when the vertex shader exports the layer, and `0u` otherwise. The
`largeRenderAttCount` variants also declare `kExtraRenderAttCount` float outputs so the fragment shader covers the
extra render attachments. The `misc` intermediate node uses a separate, simpler vertex/fragment pair
([usedThenUnusedPrograms](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L1154-L1174)) that
outputs a push-constant `vec4` color to location 0.

## Runtime Execution and Result Checking

- **Images.** Each case creates `pipeFBAttachmentCount` color images of format `VK_FORMAT_R8G8B8A8_UINT`, extent 1x1, and
  `layerCount` array layers, each backed by a host-visible verification buffer
  ([colorImages allocation](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L556-L560)). The
  `largeRenderAttCount` variants add `kExtraRenderAttCount` images of format `VK_FORMAT_R8G8B8A8_UNORM`
  ([extra render images](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L562-L571)). When
  depth or stencil is present, a single depth/stencil image is created and copied into two host-visible buffers, one for each
  aspect ([dsImage](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L581-L625)).
- **Pre-render clear.** Every image transitions `UNDEFINED -> TRANSFER_DST_OPTIMAL` and is cleared to
  `{0, 0, 0, 0}` (color) or `{depth: 0.0, stencil: 0}` (depth/stencil)
  ([clear loop](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L816-L849)). The clear value
  is the expected value for any attachment that is not written, so a written-but-uncleared attachment and an
  unused-but-overwritten attachment are both detectable.
- **Layout transition into rendering.** All images move to their attachment-optimal layout before
  `vkCmdBeginRendering` ([rendering barriers](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L851-L879)).
- **Pipeline construction.** The graphics pipeline is built from the case's `VkPipelineRenderingCreateInfo`, whose
  `colorAttachmentCount`, color format vector, depth format, and stencil format are assembled from the parameter masks and
  intermediate-node flags
  ([pipeline format assembly](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L662-L759)).
  The depth and stencil tests are enabled only when the corresponding attachment is present, defined, and has a valid handle
  ([depthEnabled / stencilEnabled](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L644-L646)).
- **Render pass instance.** `vkCmdBeginRendering` is called with a `VkRenderingInfo` whose
  `pColorAttachments` array carries a valid view or `VK_NULL_HANDLE` per the handle mask, and whose depth and stencil
  attachments are non-null only when the corresponding booleans say so
  ([renderingInfo](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L801-L812)). The
  `partial_secondary_cmd_buff` parent records the draw inside a secondary command buffer bracketed by the primary's
  `cmdBeginRendering`/`cmdEndRendering` using `VK_RENDERING_CONTENTS_SECONDARY_COMMAND_BUFFERS_BIT`
  ([secondary path](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L791-L799)).
- **Draws.** The host pushes the current layer index as a push constant and draws the fullscreen triangle once per written
  layer ([draw loop](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L926-L937)). In
  multiview mode a single draw covers every layer selected by the `viewMask`.
- **Copyback.** After rendering, every image transitions to `TRANSFER_SRC_OPTIMAL` and is copied into its verification
  buffer. Depth and stencil are copied into separate buffers through aspect-scoped copy regions
  ([copy loop](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L947-L992)). A global memory
  barrier makes the copies visible to the host.
- **Color verification.** For every color image and every layer, the host builds a reference level cleared to the expected
  color, then compares with a zero threshold. Integer attachments use `tcu::intThresholdCompare`; float attachments (the
  extra render attachments) use `tcu::floatThresholdCompare`
  ([color verification](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L1024-L1076)).
- **Depth and stencil verification.** Each aspect is compared against its expected value with `tcu::dsThresholdCompare` at
  threshold `0.0f`, expecting exact results
  ([depth verify](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L1083-L1106),
  [stencil verify](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L1108-L1131)).
- **Pass condition.** A case passes only when every checked attachment, in every layer, matches its expected value. Any
  mismatch returns `tcu::TestStatus::fail`
  ([final status](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L1134-L1137)).

| Resource | Created/configured by host? | Bound to GPU? | Device access | Host readback | Role |
|---------|-----------------------------|---------------|---------------|---------------|------|
| Color attachment images | Yes | Color attachment views in `VkRenderingAttachmentInfo` | Written by draw, read by copy | Yes, via per-image verification buffer | Carry the per-attachment color encoding; expected value distinguishes written from cleared. |
| Extra render attachment images (`largeRenderAttCount`) | Yes | Extra color attachment views beyond the pipeline count | Written by draw when the view is non-null | Yes | Exercise the relaxed attachment-count rule on the render side. |
| Depth/stencil image | Yes, when depth or stencil is present | Depth and/or stencil attachment view | Written by draw when used on both sides | Yes, via two aspect-scoped verification buffers | Carries the depth and stencil values checked by `tcu::dsThresholdCompare`. |
| Push constant range | Yes | `cmdPushConstants` | Read by vertex shader (layer index) and, in `misc`, by fragment shader (color) | No | Selects the target layer for non-multiview multi-layer cases; carries the color in the `misc` intermediate node. |
| Secondary command buffer | Yes, for the `partial_secondary_cmd_buff` parent | `cmdExecuteCommands` | Records the draw inside the render pass instance | No | Records draws with `VK_COMMAND_BUFFER_USAGE_RENDER_PASS_CONTINUE_BIT` and a matching `VkCommandBufferInheritanceRenderingInfo`. |

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `comb` color attachment that is used on both sides | Implementation writing the wrong color into an active attachment, or fragment output routing mismatched to the attachment index. |
| `comb` color attachment that is unused on one side | Unused attachment overwritten when it should stay cleared; the implementation treated a `VK_NULL_HANDLE` view or a `VK_FORMAT_UNDEFINED` slot as active. |
| `comb` depth or stencil attachment | Depth or stencil test mis-enabled or mis-disabled when the attachment's present/defined/valid-handle booleans disagree; the written value is wrong or the clear value is overwritten. |
| `bad_formats` | Implementation rejecting or mishandling a wrong pipeline format paired with a `VK_NULL_HANDLE` view, instead of ignoring the unused slot's format as the extension allows. |
| `extra_att` / `extra_pipe_att` | Implementation enforcing the pre-extension VUID-`{refpage}`-colorAttachmentCount-06179 rule, or writing into the extra pipeline attachments when `extraAttIsUnused` is false. |
| `extra_render_att` | Implementation rejecting the larger render-side `colorAttachmentCount`, or writing into the extra render attachments when `extraAttIsUnused` is true. |
| `misc` (color part) | Color attachment not preserved across the two render pass instances; the second pass overwrote or corrupted the color written by the first. |
| `misc` (depth part) | Depth test state not switched correctly between the two passes (static pipeline swap or dynamic `VK_DYNAMIC_STATE_DEPTH_TEST_ENABLE`), so the depth attachment holds the wrong value. |
| Any case | Shared infrastructure: layout transition, copyback, layer routing, or secondary-command-buffer inheritance defect. |

### Cause Analysis

#### Unused attachment written when it should stay cleared

**Possible failure symptoms:** A color, depth, or stencil attachment whose pipeline format is `VK_FORMAT_UNDEFINED`, whose
framebuffer view is `VK_NULL_HANDLE`, or whose layer bit is clear fails because it no longer holds the pre-render clear
value, even though no draw should have written to it.

**Possible implementation causes:** The extension's contract is that an unused attachment is ignored. A defect that treats a
`VK_NULL_HANDLE` view as if it were a real target, or that honors a `VK_FORMAT_UNDEFINED` pipeline slot as if it were a
defined format, would route fragment output into the unused attachment. A layer-routing defect in non-multiview multi-layer
cases could also write into a layer whose mask bit is clear. Source-level investigation of the driver's dynamic rendering
attachment setup for the specific used/unused combination would be needed to confirm the mechanism.

#### Active attachment receives the wrong value

**Possible failure symptoms:** An attachment that is used on both sides and whose layer bit is set fails because its value is
not the expected `uvec4(L, 255, i, 255)` (color), `1.0` (depth), or `0xFF` (stencil).

**Possible implementation causes:** The fragment shader writes a deterministic value into each active output, so a wrong
value points at fragment-output-to-attachment routing, depth/stencil test state, or stencil reference handling rather than
shader arithmetic. Under the extension the attachment index mapping can shift when counts differ, so a defect that maps
fragment output `i` to the wrong framebuffer slot would produce a swapped or stale value. Source-level investigation of the
driver's color attachment remapping for mismatched counts would be needed to confirm.

#### Depth or stencil test state disagrees with the present/defined/valid-handle booleans

**Possible failure symptoms:** A `comb` depth/stencil case fails because the depth or stencil attachment holds the clear
value when it should have been written, or holds a written value when it should have stayed cleared.

**Possible implementation causes:** The test enables the depth or stencil test only when the attachment is present, defined,
and has a valid handle
([depthEnabled / stencilEnabled](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L644-L646)).
A defect that enables the test when the pipeline format is `VK_FORMAT_UNDEFINED` but the view is valid (or vice versa) would
write into an attachment the spec says is unused, or skip writing into one the spec says is active. This is a
dynamic-rendering depth/stencil state handling defect.

#### Mismatched attachment counts rejected or mishandled

**Possible failure symptoms:** An `extra_att`, `extra_pipe_att`, or `extra_render_att` case fails at draw time or produces
wrong attachment values, even though the extension allows the pipeline and render pass instance to report different
`colorAttachmentCount` values.

**Possible implementation causes:** Under the extension the pre-extension VUID-`{refpage}`-colorAttachmentCount-06179 rule
no longer applies. A defect that still enforces equal counts would reject the draw or corrupt the extra slots. For
`extra_att` with `extraAttIsUnused = false`, the extra pipeline attachments carry a deliberately wrong format
(`kBadColorFormat`); the implementation must ignore those formats because the slots are beyond the render-side count. For
`extra_render_att`, the implementation must honor the extra render-side attachments only when their views are non-null.

#### Color attachment not preserved across the two `misc` render passes

**Possible failure symptoms:** The `misc` color comparison fails because the color attachment no longer matches the blue
written by the first pass, even though the second pass should not have overwritten it.

**Possible implementation causes:** The `misc` intermediate node drops the color attachment in the second render pass instance
(`colorAttachmentCount = 0`). The first pass writes blue with depth unused; the second pass binds a depth-enabled pipeline
(or flips the dynamic depth state) and draws red, but the color attachment is not present in the second pass's
`VkRenderingInfo`. A defect that does not isolate attachment state across dynamic render pass instances, or that carries
color attachment state from the first pass into the second, would corrupt the blue result. Depth handling is not implicated
when the depth check already passed.

#### Depth state not switched between the two `misc` render passes

**Possible failure symptoms:** The `misc` depth comparison fails because the depth attachment holds the clear value when it
should hold the vertex-written depth, or vice versa.

**Possible implementation causes:** The first pass must leave depth untouched; the second pass must write depth. The
`color_used_then_unused_dynamic_depth_enable` leaf toggles depth on between passes with
`VK_DYNAMIC_STATE_DEPTH_TEST_ENABLE`
([depth enable flip](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L1350-L1364)). A
defect that does not honor the dynamic state change, or that carries pipeline depth state across render pass instances,
would produce the wrong depth value. This is a dynamic depth-test-enable handling defect.

## Case Pruning

### Requirement-based pruning

- Every case requires `VK_KHR_dynamic_rendering` and `VK_EXT_dynamic_rendering_unused_attachments`
  ([checkBasicExtSupport](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L489-L493)).
- The fragment attachment count must not exceed `limits.maxFragmentOutputAttachments`, and the pipe/framebuffer count must
  not exceed `limits.maxColorAttachments`
  ([limit checks](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L501-L505)).
- The `largePipeAttCount` and `largeRenderAttCount` variants add `kExtraPipelineAttCount` or `kExtraRenderAttCount`
  attachments and prune when the total exceeds `limits.maxFragmentOutputAttachments`
  ([extra count checks](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L507-L521)).
- Cases whose vertex shader exports `gl_Layer` require `VK_EXT_shader_viewport_index_layer` (or the Vulkan 1.2 features) and
  `DEVICE_CORE_FEATURE_GEOMETRY_SHADER`
  ([vert layer support](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L523-L530)).
- Multiview cases require `VK_KHR_multiview`
  ([multiview support](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L532-L533)).
- The `misc` intermediate node with `dynamicDepthEnable = true` requires `VK_EXT_extended_dynamic_state`
  ([usedThenUnusedCheckSupport](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L1146-L1152)).
- The whole family is excluded from Vulkan SC builds (`#ifndef CTS_USES_VULKANSC` around the dynamic-rendering registration
  block in [vktRenderPassTests.cpp#L8521-L8548](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8521-L8548)).

### Design-based pruning

- In the `comb` color intermediate node, `fragAttachmentCount` must be at least `pipeFBAttachmentCount`; smaller combinations are
  skipped ([fragAtt < pipeAtt skip](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L1629-L1630)).
- When `layerCount == 1`, only the all-on and all-off layer masks are emitted to avoid duplicate cases
  ([duplicate mask skip](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L1636-L1637)).
- Multiview cases with an empty `viewMask` are skipped
  ([empty viewMask skip](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L1646-L1647)).
- In the `comb` depth/stencil intermediate node, if depth or stencil is not present then its defined/valid-handle booleans must also
  be false, the depth and stencil valid-handle booleans must match, and the depth and stencil defined booleans must match;
  see the inline comments about the lack of a VU for splitting the two formats
  ([depth/stencil pruning](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L1664-L1686)).
- The `bad_formats` intermediate node requires the format mask and handle mask to differ, and requires at least one null handle, so
  every case exercises the wrong-format-with-null-view path
  ([bad_formats skip](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L1724-L1725)).
- The `extra_att` intermediate node requires the format mask and handle mask to differ and requires at least one null handle
  (`handleMask != 0xFFFFFFFFu`), so every case exercises both the count mismatch and at least one used/unused split
  ([extra_att skip](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L1741-L1742)).
- The `extra_pipe_att` intermediate node requires the format mask and handle mask to differ so every case exercises at least
  one used/unused split
  ([extra_pipe_att skip](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L1759)).
- The `extra_render_att` intermediate node applies no format/handle mask pruning; all mask combinations are emitted
  ([extra_render_att loop](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L1771-L1785)).
- The `largeRenderAttCount` constructor asserts `layerCount == 1`
  ([layer count assertion](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L363)), so those
  variants do not combine with multi-layer cases.
- The family is registered under `primary_cmd_buff` and `partial_secondary_cmd_buff` but not under
  `complete_secondary_cmd_buff` or `graphics_pipeline_library`, because the registration is gated on monolithic pipeline
  construction and the partial-secondary path
  ([vktRenderPassTests.cpp#L8530-L8546](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8530-L8546)).

## Key Takeaways

- The tested property is the used/unused pairing between the pipeline side (`VkPipelineRenderingCreateInfo` formats and
  count) and the framebuffer side (`VkRenderingAttachmentInfo` views). Every leaf fixes that pairing through masks, and the
  expected value for each attachment follows directly from whether both sides agree it is used.
- The test distinguishes written from cleared attachments by pre-clearing every attachment to `{0, 0, 0, 0}` and checking
  against a zero threshold. A written-but-uncleared attachment and an unused-but-overwritten attachment are both caught.
- `bad_formats` proves the extension ignores the pipeline format of a framebuffer-unused slot: a deliberately wrong format
  paired with a `VK_NULL_HANDLE` view must still draw successfully.
- `extra_att`, `extra_pipe_att`, and `extra_render_att` prove the extension lifts the equal-count rule: the pipeline and
  render pass instance may report different `colorAttachmentCount` values, and the extra slots are honored or ignored based
  on whether they are marked unused.
- `misc` is the only multi-pass intermediate node: it writes a color attachment in the first pass and drops it (color becomes
  unused) in the second, while flipping depth from unused to used, which catches defects in attachment state isolation and
  dynamic depth-test-enable handling.
- The family is registered under `primary_cmd_buff` and `partial_secondary_cmd_buff` only, so the same parameter matrix is
  exercised once with direct primary recording and once with secondary command buffer recording.
- See [Failure Meaning](#failure-meaning) for how each failure mode maps to specific implementation defect categories.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test family factory | [vktDynamicRenderingUnusedAttachmentsTests.cpp#L1593-L1807](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L1593-L1807) | Creates the `unused_attachments` group and its six intermediate nodes; enumerates the parameter matrices. |
| Test parameters and name synthesis | [vktDynamicRenderingUnusedAttachmentsTests.cpp#L101-L336](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L101-L336) | Owns the `TestParams` struct, mask-to-format and mask-to-view helpers, and the leaf name string. |
| Shader generation | [vktDynamicRenderingUnusedAttachmentsTests.cpp#L376-L487](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L376-L487) | Emits the vertex and fragment shaders, including the dual SPIR-V 1.0 / 1.5 vertex modules and the per-case fragment output declarations. |
| Support checks | [vktDynamicRenderingUnusedAttachmentsTests.cpp#L489-L534](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L489-L534) | Extension, feature, and limit gates; multiview and vertex-layer support. |
| Instance iterate and verification | [vktDynamicRenderingUnusedAttachmentsTests.cpp#L536-L1138](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L536-L1138) | Image creation, layout transitions, render pass recording, copyback, and the color/depth/stencil comparisons. |
| `misc` intermediate node | [vktDynamicRenderingUnusedAttachmentsTests.cpp#L1140-L1587](../../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp#L1140-L1587) | The two-pass used-then-unused case, including the dynamic depth-enable path. |
| Group attachment | [vktRenderPassTests.cpp#L8534](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8534), [vktRenderPassTests.cpp#L8543](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8543) | Adds the family under the `primary_cmd_buff` and `partial_secondary_cmd_buff` dynamic-rendering intermediate nodes. |
| Mustpass entries | [renderpasses.txt](../../../mustpass/main/vk-default/renderpasses.txt) | Lists all `dEQP-VK.renderpasses.dynamic_rendering.{primary_cmd_buff,partial_secondary_cmd_buff}.unused_attachments.*` leaves. |
