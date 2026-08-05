## Overview

**Core question:** When an attachment is read back as an input attachment in the same dynamic render pass instance that writes it, does the implementation honor the explicit feedback-loop declaration from `VK_KHR_maintenance10` and return the locally written value?

- This page covers the `m10_feedback_loop` test family implemented in
  [vktDynamicRenderingLocalReadMaint10Tests.cpp](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp) and attached under
  `renderpasses.dynamic_rendering.primary_cmd_buff`
  [vktRenderPassTests.cpp#L8522-L8536](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8522-L8536).
- The test family exercises the `VK_KHR_maintenance10` explicit feedback-loop declaration
  (`VK_RENDERING_ATTACHMENT_INPUT_ATTACHMENT_FEEDBACK_BIT_KHR` together with
  `VK_RENDERING_LOCAL_READ_CONCURRENT_ACCESS_CONTROL_BIT_KHR`) on top of
  `VK_KHR_dynamic_rendering_local_read`. The attachment is read back as an input attachment in the
  same render pass instance that wrote it.
- Attachment formats span color (`R8G8B8A8_UNORM`) and depth/stencil (`D16_UNORM`, `S8_UINT`,
  `D24_UNORM_S8_UINT`, `D32_SFLOAT_S8_UINT`); sample counts are 1x and 4x; and each run can be
  performed with either the `RENDERING_LOCAL_READ` layout or the `GENERAL` layout.
- 120 test case leaves are registered as direct children of the family
  [renderpasses.txt#L19675-L19794](../../../mustpass/main/vk-default/renderpasses.txt#L19675-L19794),
  and also appear in the `vk-main-2026-03-01` Android CTS mustpass subset.

## Background Knowledge

- **Dynamic rendering local read.** `VK_KHR_dynamic_rendering_local_read` (core in Vulkan 1.4) lets a
  fragment shader read an attachment written earlier in the same dynamic render pass instance by
  binding that attachment as an input attachment. The read uses the `VK_IMAGE_LAYOUT_RENDERING_LOCAL_READ`
  layout, and the mapping from attachment to input attachment index is set with
  `VkRenderingInputAttachmentIndexInfo`
  ([renderpass.adoc](../../../../vulkan-docs/src/chapters/renderpass.adoc),
  [interfaces.adoc](../../../../vulkan-docs/src/chapters/interfaces.adoc)).
- **Attachment feedback loop.** Reading an attachment as an input attachment in the same pass that
  writes it is an attachment feedback loop. In render-pass objects this is expressed with subpass
  self-dependencies; in dynamic rendering the feedback relationship is declared per attachment with
  the `VK_RENDERING_ATTACHMENT_INPUT_ATTACHMENT_FEEDBACK_BIT_KHR` flag, which gives implementations
  the same hint a subpass dependency would
  ([renderpass.adoc, rendering-attachment-input-attachment-feedback](../../../../vulkan-docs/src/chapters/renderpass.adoc)).
- **`VK_KHR_maintenance10` concurrent access control.** When the render pass instance sets
  `VK_RENDERING_LOCAL_READ_CONCURRENT_ACCESS_CONTROL_BIT_KHR`, the feedback flag is no longer implied
  by layout and usage; the application must set
  `VK_RENDERING_ATTACHMENT_INPUT_ATTACHMENT_FEEDBACK_BIT_KHR` explicitly on every attachment it wants
  to read concurrently. This explicit declaration is the maintenance10 behavior this page tests
  ([renderpass.adoc](../../../../vulkan-docs/src/chapters/renderpass.adoc)).
- **Input attachment modifiers trick.** The fragment shader multiplies each loaded texel by a buffer
  of ones and adds a buffer of zeros. This is a no-op on correct hardware but prevents the compiler
  from folding the input attachment read out of the shader, so a driver that skips the local read
  produces visibly wrong output
  ([vktDynamicRenderingLocalReadMaint10Tests.cpp#L297-L306](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L297-L306)).

## Registration Hierarchy

```text
renderpasses.dynamic_rendering.primary_cmd_buff.m10_feedback_loop
├── r8g8b8a8_unorm_samples_1_loop_N
├── r8g8b8a8_unorm_samples_1_loop_Y
├── r8g8b8a8_unorm_samples_1_loop_NN
├── r8g8b8a8_unorm_samples_1_loop_NY
├── r8g8b8a8_unorm_samples_1_loop_YN
├── r8g8b8a8_unorm_samples_1_loop_YY
├── d16_unorm_samples_1_loop_Y
├── s8_uint_samples_1_loop_Y
├── d24_unorm_s8_uint_samples_1_loop_Y
└── d32_sfloat_s8_uint_samples_1_loop_Y
```

The tree shows the family root and a representative selection of its 120 direct test case leaves. The
full leaf set is enumerated in `## Parameter Dimensions and Observed Values` and
`## Behavior Parameters`. The naming pattern is
`{format}_samples_{count}_loop_{case}{_sample_{id}}{_general_layout}`
([vktDynamicRenderingLocalReadMaint10Tests.cpp#L1744-L1748](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L1744-L1748)).

The `m10_feedback_loop` family is attached only under `primary_cmd_buff`, and only when the pipeline
construction type is monolithic. The attachment site gates both conditions: dynamic rendering with a
non-monolithic pipeline construction type breaks early before reaching this factory, and the
secondary-command-buffer path that would re-add some local read families does not re-add this one
([vktRenderPassTests.cpp#L8522-L8546](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8522-L8546)).
The family does not register under `renderpass1` or `renderpass2` at all.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| `attFormat` | `R8G8B8A8_UNORM`, `D16_UNORM`, `S8_UINT`, `D24_UNORM_S8_UINT`, `D32_SFLOAT_S8_UINT` | Selects whether the attachment is color, depth-only, stencil-only, or packed/combined depth-stencil. Determines which aspects are read back and which comparison path the host uses. | [format loop](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L1726-L1727) |
| `samples` | `1`, `4` | Single-sample attachments use a straightforward input attachment read; 4x attachments exercise `subpassInputMS` plus per-sample selection, and the result is expanded to single-sample for verification. | [sampleCount loop](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L1728) |
| `feedback` (per attachment) | boolean vector, length 1 or 2 | Each entry says whether that attachment participates in a feedback loop (`Y`) or not (`N`). Length 2 is color-only and creates two attachments, each with its own loop flag. | [feedbackLoops table](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L1715-L1724) |
| `sampleId` | `-1`, `0`, `1`, `2`, `3` | Present only for 4x samples. `-1` means the shader uses `gl_SampleID`; otherwise the shader reads one fixed sample index. `-1` is the only value used at 1x. | [sampleId loop](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L1730) |
| `generalLayout` | `false`, `true` | `false` uses `VK_IMAGE_LAYOUT_RENDERING_LOCAL_READ` for attachments and `VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL` for the copy sampler; `true` uses `VK_IMAGE_LAYOUT_GENERAL` for both. | [layout selection](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L631-L633) |

Per-format and per-sample-count registered case counts, confirmed against the mustpass file:

| Format | 1x cases | 4x cases | Total |
|--------|----------|----------|-------|
| `R8G8B8A8_UNORM` | 12 | 60 | 72 |
| `D16_UNORM` | 2 | 10 | 12 |
| `S8_UINT` | 2 | 10 | 12 |
| `D24_UNORM_S8_UINT` | 2 | 10 | 12 |
| `D32_SFLOAT_S8_UINT` | 2 | 10 | 12 |
| **Total** | **20** | **100** | **120** |

Color format arithmetic: 6 feedback vectors x 1 sampleId (-1) x 2 layouts = 12 at 1x; 6 feedback
vectors x 5 sampleIds (-1, 0, 1, 2, 3) x 2 layouts = 60 at 4x. Depth/stencil formats admit only the
single-attachment feedback vector `{true}` (registered as `loop_Y`), giving 1 x 1 x 2 = 2 cases at 1x
and 1 x 5 x 2 = 10 cases at 4x per format
([vktDynamicRenderingLocalReadMaint10Tests.cpp#L1733-L1738](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L1733-L1738)).

## Behavior Parameters

The primary behavioral axis is the feedback vector, encoded in the `loop_{case}` token of each test
name. Its values change how many attachments exist, which ones are declared as feedback attachments,
and therefore what correctness property the run checks.

### `loop_N`: single color attachment, no feedback loop

One color attachment is created and used purely as an output. The input attachment read still runs,
but against a separate non-looped attachment image, so this case confirms the infrastructure works
when no attachment carries the feedback flag
([getTotalAttCount](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L162-L176),
[getOutputAttForAtt](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L199-L206)).

### `loop_Y`: single attachment, feedback loop on

One attachment is declared with
`VK_RENDERING_ATTACHMENT_INPUT_ATTACHMENT_FEEDBACK_BIT_KHR` and is both written and read back as an
input attachment in the same render pass instance. This is the core maintenance10 feedback-loop case.
For depth/stencil formats this is the only registered feedback value, because a second depth/stencil
attachment cannot be added to carry the non-looped output
([shader comment](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L460-L462)).

### `loop_NN`, `loop_NY`, `loop_YN`, `loop_YY`: two color attachments, mixed loop flags

Two color attachments are created. Each flag position says whether that attachment is in a feedback
loop. `loop_YY` is the all-concurrent case where a single set of images serves both input and output;
the others allocate a second set of images so non-looped attachments write to distinct outputs while
looped attachments write and read the same image
([getTotalAttCount](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L162-L176)).
These four values are color-only; depth/stencil formats skip them.

### Secondary axes

Two further dimensions vary behavior without changing the feedback declaration itself:

- **`sampleId`** controls whether the input attachment read uses `gl_SampleID` (value `-1`) or a fixed
  sample index (0 through 3). The fixed-index path checks that the implementation returns the correct
  per-sample value rather than an averaged or default-sample value
  ([frag-modify sampleIndex](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L439-L441)).
- **`generalLayout`** swaps the `RENDERING_LOCAL_READ` attachment layout and the
  `SHADER_READ_ONLY_OPTIMAL` copy-sampler layout for `GENERAL`. This checks that the feedback-loop
  declaration and local read also work when the implementation cannot infer the feedback relationship
  from the layout alone
  ([layout selection](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L631-L633)).

## Shader Analysis

The test builds four fragment shaders plus a shared vertex shader. The shaders themselves are not the
behavior under test; they exist to load, read back, transform, and verify attachment data. The
interesting behavior is the host-side feedback-loop declaration and the input attachment read it
enables. The shaders are summarized here so the runtime section can focus on the feedback-loop
mechanics.

- **`vert`** draws a full-screen triangle from three hardcoded positions, so every fragment is covered
  ([vert shader](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L317-L327)).
- **`frag-load`** fills each output attachment with pseudo-random data read from storage buffers. For
  depth/stencil it writes `gl_FragDepth` and `gl_FragStencilRefARB` from the same buffer data. This
  establishes the values that the next pass must read back
  ([frag-load](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L337-L377)).
- **`frag-modify`** is the feedback-loop shader. It loads each attachment through `subpassLoad`
  (multiplied by the ones-and-zeros modifiers to defeat optimization), then writes a transformed
  value back: color components are swizzled (`.gbra`), depth is complemented (`1.0 - d`), and stencil
  is complemented (`255 - s`). The transform makes a skipped or stale read immediately visible,
  because the output would then match the loaded value instead of the transformed one
  ([frag-modify](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L438-L517)).
- **`frag-grad`** overwrites the right half of the framebuffer with a position-based gradient. Its
  output is independent of the feedback loop and lets the test distinguish the looped region from the
  overwritten region on readback
  ([frag-grad](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L519-L563)).
- **`frag-copy`** exists only for the 4x case. It expands each multisample pixel into a horizontal
  block of single-sample pixels using `texelFetch` on `sampler2DMS`, so the host can compare each
  sample individually
  ([frag-copy](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L379-L436)).

No separate `### Representative Shader Walkthrough` subsection is provided because shader correctness
is not the property under test. The shaders are deterministic data movers; the pass/fail signal comes
from whether the feedback-loop read returned the locally written value.

## Runtime Execution and Result Checking

Each case runs a single command buffer with one render pass instance containing three pipeline
draws, plus an optional second render pass instance for multisample expansion, all under dynamic
rendering.

- **Resource setup.** The host allocates the attachment images plus, for the non-all-concurrent
  feedback vectors, a second set of color images used as the non-looped outputs. Storage buffers hold
  pseudo-random load data seeded from the format and sample count
  ([image creation](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L656-L725),
  [load buffers](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L727-L761)).
  A small modifiers buffer holds the ones-and-zeros pair used by `frag-modify`
  ([modifiers buffer](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L763-L776)).
- **Feedback-loop declaration.** When any attachment is looped, the host chains a
  `VkRenderingAttachmentFlagsInfoKHR` carrying
  `VK_RENDERING_ATTACHMENT_INPUT_ATTACHMENT_FEEDBACK_BIT_KHR` onto each looped attachment's
  `VkRenderingAttachmentInfo`, and sets `VK_RENDERING_LOCAL_READ_CONCURRENT_ACCESS_CONTROL_BIT_KHR` on
  the `VkRenderingInfo`. This is the maintenance10 explicit declaration under test
  ([flags setup](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L1209-L1265)).
- **Input attachment index mapping.** For depth/stencil cases, the host sets
  `VkRenderingInputAttachmentIndexInfo` to give depth and stencil their own input attachment indices
  ([index info](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L915-L937)).
- **Three-pass sequence.** (1) `frag-load` clears and fills the attachments with load data; (2)
  `frag-modify` reads each attachment back as an input attachment, transforms it, and writes it back
  to the looped attachment or to the paired non-looped output; (3) `frag-grad` overwrites the right
  half of the result with a gradient. A `VK_DEPENDENCY_BY_REGION_BIT` memory barrier separates the
  load write from the feedback read and the feedback write from the gradient write
  ([pass sequence](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L1223-L1318),
  [fbWritesBarrier](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L589-L603)).
- **Multisample expansion.** For 4x cases a second render pass instance runs `frag-copy` to expand
  each multisample image into a single-sample image laid out as horizontal sample blocks
  ([copy pass](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L1320-L1427)).
- **Readback.** The host transitions the result images to a transfer source layout and copies them
  into verification buffers, with a final transfer-to-host barrier
  ([copy to buffer](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L1429-L1499)).
- **Reference and comparison.** The host builds reference levels per attachment: the left half holds
  the transformed load data (swizzled color, complemented depth/stencil), and the right half holds
  the gradient. Color uses `tcu::floatThresholdCompare` with a threshold of `2/255` per channel;
  depth uses `tcu::dsThresholdCompare` with a format-dependent threshold (`2/0xffff` for D16,
  `2/0xffffff` for D24/D32); stencil uses `tcu::dsThresholdCompare` with a zero threshold, which
  amounts to an exact byte comparison
  ([reference build](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L1505-L1630),
  [comparison](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L1632-L1697)).
- **Pass condition.** The case passes only if every comparison returns success; any mismatch triggers
  `TCU_FAIL`
  ([final check](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L1694-L1697)).

| Resource | Created by host | Bound to GPU | Device access | Host readback | Role |
|----------|-----------------|--------------|---------------|---------------|------|
| Attachment images (looped and non-looped) | Yes | Color or depth/stencil views, plus input attachment descriptors | Written by `frag-load` and `frag-modify`; read by `frag-modify` as input attachments | Copied to verification buffers | Carry the values the feedback loop must return. |
| Load storage buffers | Yes | Descriptor set bindings | Read by `frag-load` | No | Source of the pseudo-random attachment data. |
| Modifiers buffer | Yes | Descriptor binding 0 of `frag-modify` | Read by `frag-modify` | No | Ones and zeros that make the input attachment read non-foldable. |
| Expanded single-sample images (4x only) | Yes | Color or depth/stencil views | Written by `frag-copy` | Copied to verification buffers | Let the host compare each sample individually. |
| Verification buffers | Yes | Transfer destination | Written by copy commands | Invalidated and read by host | Hold the actual attachment contents for comparison. |

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| Any `loop_Y*` value (single or double attachment with at least one loop) | Feedback-loop input attachment read did not return the locally written value. |
| `loop_N`, `loop_NN` (no looped attachments) | Input attachment read against the non-looped output attachment returned the wrong value, or the two-attachment routing picked the wrong image. |
| 4x cases with `sampleId` set | Per-sample input attachment read returned the wrong sample, an averaged value, or a default-sample value. |
| `_general_layout` cases | Feedback-loop declaration or local read was not honored when the layout was `GENERAL` instead of `RENDERING_LOCAL_READ`. |

All cases share the comparison infrastructure: if the host-side reference build, copy, or comparison
path is wrong, every case for a format would fail together.

### Cause Analysis

#### Feedback-loop input attachment read did not return the locally written value

**Possible failure symptoms:** The left half of a looped attachment's verification buffer does not
match the reference. Because `frag-modify` transforms the loaded value (swizzle for color, complement
for depth/stencil), a mismatch means the read returned either the clear value, the pre-transform
loaded value, or stale data, rather than the value written by `frag-load` in the same render pass
instance
([frag-modify](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L438-L517),
[comparison](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L1632-L1697)).

**Possible implementation causes:** The render pass instance declared the feedback loop with
`VK_RENDERING_ATTACHMENT_INPUT_ATTACHMENT_FEEDBACK_BIT_KHR` and
`VK_RENDERING_LOCAL_READ_CONCURRENT_ACCESS_CONTROL_BIT_KHR`
([flags setup](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L1209-L1265)).
A driver that ignores the explicit flag, that fails to route the input attachment read to the in-flight
attachment write, or that inserts an unintended flush between the write and the read could produce this
symptom. The spec notes that some implementations need extra work beyond layout to make this scenario
work and may treat the flag as a no-op only when no such work is required
([renderpass.adoc, rendering-attachment-input-attachment-feedback](../../../../vulkan-docs/src/chapters/renderpass.adoc)).
Whether the root cause is driver flag handling, tile-based attachment routing, or compiler folding of
the input attachment read requires source-level investigation against the specific failing case.

#### Input attachment read against the non-looped output returned the wrong value, or two-attachment routing picked the wrong image

**Possible failure symptoms:** For feedback vectors that are not all-concurrent (`loop_N`, `loop_NN`,
`loop_NY`, `loop_YN`), a non-looped attachment's verification buffer does not match the reference.
This points at the routing that sends looped attachments to themselves and non-looped attachments to
the second set of images
([getOutputAttForAtt](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L199-L206)).

**Possible implementation causes:** The test creates a second set of color images and writes non-looped
outputs to them so the looped attachments can be read without contention
([getTotalAttCount](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L162-L176)).
The output location and the input attachment binding are computed from the feedback vector, so a
mismatch would surface as the wrong image being read or written. Within CTS this routing is fixed by
the parameter struct, so a failure here more likely reflects a driver issue with multiple color
attachments and mixed input attachment usage than a CTS routing bug; confirming either requires
source-level investigation.

#### Per-sample input attachment read returned the wrong sample

**Possible failure symptoms:** For 4x cases with a fixed `sampleId`, the expanded single-sample image
does not match the reference for the targeted sample. The reference selects exactly one sample per
pixel block, so reading the wrong sample, an averaged value, or a default sample produces a visible
mismatch
([reference sample selection](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L1528-L1533)).

**Possible implementation causes:** The shader uses `subpassInputMS` with an explicit sample index
([frag-modify](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L467-L471)),
and the case requires the `sampleRateShading` core feature and the
`dynamicRenderingLocalReadMultisampledAttachments` Vulkan 1.4 property
([checkSupport](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L273-L280)).
A driver that does not honor the explicit sample index on a multisampled input attachment under
dynamic rendering, or that returns resolved rather than per-sample data, would produce this symptom.
Whether the cause is multisample input attachment handling, sample-rate shading setup, or the local
read path requires source-level investigation.

#### Feedback-loop declaration or local read was not honored with the GENERAL layout

**Possible failure symptoms:** A `_general_layout` case fails while its `RENDERING_LOCAL_READ`
counterpart passes. Both cases use the same feedback declaration; only the image layout differs
([layout selection](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L631-L633)).

**Possible implementation causes:** With `VK_RENDERING_LOCAL_READ_CONCURRENT_ACCESS_CONTROL_BIT_KHR`
set, the application declares feedback explicitly regardless of layout, so the implementation must
honor the flag under `VK_IMAGE_LAYOUT_GENERAL` as well as under
`VK_IMAGE_LAYOUT_RENDERING_LOCAL_READ`
([renderpass.adoc](../../../../vulkan-docs/src/chapters/renderpass.adoc)). A driver that only enables
its feedback-loop path for the `RENDERING_LOCAL_READ` layout would fail the `_general_layout` variant
while passing the default one. Confirming this requires source-level investigation of the failing
implementation's layout handling.

## Case Pruning

### Requirement-based pruning

- `VK_KHR_dynamic_rendering_local_read` and `VK_KHR_maintenance10` are required
  ([checkSupport](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L254-L259)).
- Stencil cases require `VK_EXT_shader_stencil_export` because `frag-load`, `frag-modify`, and
  `frag-grad` write stencil from the fragment shader
  ([stencil export](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L264-L265)).
- Depth/stencil input attachment reads under dynamic rendering require the
  `dynamicRenderingLocalReadDepthStencilAttachments` Vulkan 1.4 property (or a pre-1.4 device)
  ([depth/stencil support](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L267-L271)).
- 4x cases require the `sampleRateShading` core feature and the
  `dynamicRenderingLocalReadMultisampledAttachments` Vulkan 1.4 property
  ([multisample support](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L273-L280)).
- Every case queries `vkGetPhysicalDeviceImageFormatProperties` for the format, usage, and sample
  count, and skips with `NotSupportedError` if the combination is unsupported
  ([format properties check](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L282-L294)).

### Design-based pruning

- Depth/stencil formats register only the single-attachment feedback vector `{true}` (`loop_Y`).
  Multi-attachment vectors are skipped because a second depth/stencil attachment cannot be added to
  carry the non-looped output
  ([skip condition](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L1736-L1738)).
- `sampleId` values that do not apply to the sample count are skipped: at 1x only `sampleId = -1` is
  used, and at 4x values greater than or equal to the sample count are dropped
  ([sampleId skip](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L1733-L1734)).
- The family attaches only under `primary_cmd_buff` with a monolithic pipeline. The
  secondary-command-buffer and graphics-pipeline-library dynamic rendering paths do not re-add it
  ([attachment site](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8522-L8546)).
- The `CLASSIC_DRLR_WITHOUT_MAINT10` compile-time switch can disable the maintenance10 requirement
  and the explicit feedback flag, but it is `#undef`-ed in the shipped source, so the maintenance10
  path is always taken
  ([switch](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L47-L48),
  [use sites](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L1209-L1265)).

## Key Takeaways

- The `m10_feedback_loop` family tests the explicit feedback-loop declaration added by
  `VK_KHR_maintenance10`: an attachment flagged with
  `VK_RENDERING_ATTACHMENT_INPUT_ATTACHMENT_FEEDBACK_BIT_KHR` must be readable as an input attachment
  in the same dynamic render pass instance that writes it.
- The `frag-modify` shader transforms the read-back value (swizzle for color, complement for
  depth/stencil), so a feedback read that returns the clear value, the pre-transform value, or stale
  data shows up as a verification mismatch on the left half of the result.
- Color formats cover six feedback vectors (one and two attachments, all loop-flag combinations);
  depth/stencil formats cover only the single-attachment looped case, giving 120 cases total.
- The `_general_layout` variants check that the explicit flag is honored under
  `VK_IMAGE_LAYOUT_GENERAL` as well as under `VK_IMAGE_LAYOUT_RENDERING_LOCAL_READ`.
- See `## Failure Meaning` for the failure interpretation: a failing result means the feedback-loop
  read, the per-sample read, the non-looped routing, or the layout handling did not satisfy the test's
  comparison.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Family attachment site | [vktRenderPassTests.cpp#L8522-L8536](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8522-L8536) | Attaches `m10_feedback_loop` under `dynamic_rendering.primary_cmd_buff`, monolithic only. |
| Test case factory | [vktDynamicRenderingLocalReadMaint10Tests.cpp#L1710-L1753](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L1710-L1753) | Builds the 120-case matrix from format, sample count, feedback vector, sample id, and layout. |
| Parameter struct | [vktDynamicRenderingLocalReadMaint10Tests.cpp#L59-L217](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L59-L217) | Holds the per-case parameters and the attachment routing helpers. |
| Support checks | [vktDynamicRenderingLocalReadMaint10Tests.cpp#L254-L295](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L254-L295) | Requires the extensions, features, and format properties used for pruning. |
| Shader generation | [vktDynamicRenderingLocalReadMaint10Tests.cpp#L308-L564](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L308-L564) | Emits the vertex, load, modify, gradient, and copy fragment shaders. |
| Feedback-loop declaration | [vktDynamicRenderingLocalReadMaint10Tests.cpp#L1209-L1265](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L1209-L1265) | Chains the maintenance10 flags onto the rendering attachment and rendering info. |
| Runtime execution | [vktDynamicRenderingLocalReadMaint10Tests.cpp#L610-L1698](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L610-L1698) | Creates resources, runs the pass sequence, expands multisample images, and compares results. |
| Mustpass entry | [renderpasses.txt#L19675-L19794](../../../mustpass/main/vk-default/renderpasses.txt#L19675-L19794) | Lists all 120 registered cases for the family. |
| Spec: feedback flag | [renderpass.adoc, rendering-attachment-input-attachment-feedback](../../../../vulkan-docs/src/chapters/renderpass.adoc) | Defines `VK_RENDERING_ATTACHMENT_INPUT_ATTACHMENT_FEEDBACK_BIT_KHR` and the concurrent access control bit. |
| Spec: local read layout | [resources.adoc](../../../../vulkan-docs/src/chapters/resources.adoc) | Restricts `VK_IMAGE_LAYOUT_RENDERING_LOCAL_READ` to input attachment plus color or depth/stencil usage. |
