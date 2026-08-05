## Overview

**Core question:** When dynamic rendering resolves a multisampled depth/stencil attachment to a single-sample resolve image, does the implementation produce the depth and stencil value that the chosen resolve mode requires, for every supported combination of sample count, format, and depth/stencil resolve mode?

- This page covers the `depth_stencil_resolve` test family implemented in
  [vktDynamicRenderingDepthStencilResolveTests.cpp](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp).
- The family is registered under the `dynamic_rendering` test category, attached to each of the three
  dynamic-rendering intermediate nodes (`primary_cmd_buff`, `partial_secondary_cmd_buff`, and
  `complete_secondary_cmd_buff`) by [vktRenderPassTests.cpp#L8527](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8527).
  It is not registered under `graphics_pipeline_library`, and it is excluded from Vulkan SC builds.
- Each case renders a fullscreen quad into a multisampled depth/stencil image, lets the dynamic rendering
  `VkRenderingAttachmentInfo` resolve step reduce it to a single-sample image using a chosen depth and stencil
  resolve mode, copies the resolved image back, and compares every pixel against a host-precomputed expected value.
- The core design separates the *tested aspect* (depth or stencil) from the *untested aspect*. Because stencil
  testing requires discarding fragments per sample, depth and stencil are exercised in separate test case leaves
  even when the attachment format carries both aspects.

## Background Knowledge

- **Multisample resolve for depth/stencil.** A multisampled color attachment is conventionally resolved by averaging
  per-sample color. Depth and stencil have no single canonical reduction, so `VK_KHR_depth_stencil_resolve` (promoted
  into Vulkan 1.2 and exposed identically through dynamic rendering) lets the application choose how the per-sample
  depth or stencil values are combined into the single-sample resolve image. The available modes are
  `VK_RESOLVE_MODE_SAMPLE_ZERO_BIT` (take sample 0), `VK_RESOLVE_MODE_AVERAGE_BIT` (average, depth only),
  `VK_RESOLVE_MODE_MIN_BIT` / `VK_RESOLVE_MODE_MAX_BIT` (extreme value), and `VK_RESOLVE_MODE_NONE` (do not resolve
  that aspect). An implementation advertises which modes it supports through
  `VkPhysicalDeviceDepthStencilResolveProperties`.
- **Depth/stencil resolve under dynamic rendering.** Instead of a render-pass resolve attachment, dynamic rendering
  puts the resolve configuration on each attachment's `VkRenderingAttachmentInfo`: `resolveMode`,
  `resolveImageView`, and `resolveImageLayout`. Depth and stencil are configured independently through the
  `pDepthAttachment` and `pStencilAttachment` pointers of `VkRenderingInfo`. The spec synchronizes the resolve
  write using the color-attachment-write access mask rather than a depth/stencil attachment mask.
- **Independent depth and stencil resolve modes.** An implementation may require depth and stencil resolve modes to
  match, allow them to differ only when one is `NONE`, or fully allow them to differ. The
  `independentResolve` and `independentResolveNone` properties report which combinations are legal on this device.
- **Separate depth/stencil image layouts.** `VK_KHR_separate_depth_stencil_layouts` lets the depth and stencil
  aspects of a combined-format image transition independently. The test exercises this path on combined formats by
  transitioning only the tested aspect before copyback.

## Registration Hierarchy

```text
renderpasses.dynamic_rendering.primary_cmd_buff.depth_stencil_resolve
├── samples_2
├── samples_4
├── samples_8
├── samples_16
├── samples_32
└── samples_64
```

The `depth_stencil_resolve` test family is created by
[createDynamicRenderingDepthStencilResolveTests](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L1926-L1931)
and attached under each of the three dynamic-rendering intermediate nodes at
[vktRenderPassTests.cpp#L8527](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8527). The tree above uses
`primary_cmd_buff` as the representative path; the same `depth_stencil_resolve` subtree appears identically under
`partial_secondary_cmd_buff` and `complete_secondary_cmd_buff`. The family is not registered under
`graphics_pipeline_library`, and it is excluded from Vulkan SC builds. The three intermediate nodes share the same
set of test case leaves; the per-case `SharedGroupParams` select primary, partial-secondary, or complete-secondary
command-buffer recording.

Each intermediate node expands identically to the six sample-count groups shown above. Below each sample-count
group, a format group is created per supported depth/stencil format, with a second `_separate_layouts` format group
added for combined depth/stencil formats. Each format group contains `depth_<mode>_stencil_<mode>_testing_depth`,
`..._testing_stencil`, and (depth-only formats only) `..._testing_pushconsts` test case leaves. The full leaf
matrix is enumerated in [Parameter Dimensions and Observed Values](#parameter-dimensions-and-observed-values).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Sample count | `samples_2`, `samples_4`, `samples_8`, `samples_16`, `samples_32`, `samples_64` | Number of MSAA samples written per pixel before resolve. The fragment shader cycles per-sample depth over a fixed 4-value set, so sample counts above 4 do not introduce new depth values; they only thicken the distribution. | [sample-count loop](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L1743), [sample group creation](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L1766-L1772) |
| Depth/stencil format | `d16_unorm`, `x8_d24_unorm_pack32`, `d32_sfloat`, `s8_uint`, `d16_unorm_s8_uint`, `d24_unorm_s8_uint`, `d32_sfloat_s8_uint` | Selects the attachment format and which aspect(s) exist. Depth-only formats produce depth leaves; stencil-only produces stencil leaves; combined formats produce both plus a `_separate_layouts` variant. | [format table](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L1706-L1714) |
| Separate depth/stencil layouts | absent, or `_separate_layouts` | When present, transitions only the tested aspect before copyback and requires `VK_KHR_separate_depth_stencil_layouts`. Registered only for combined depth/stencil formats. | [separate-layouts loop](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L1784-L1791) |
| Depth resolve mode | `none`, `zero`, `average`, `min`, `max` | Controls how per-sample depth values are reduced to the resolve image. The fragment shader produces a fixed per-sample depth set, so each mode maps to a precomputed expected value. | [resolve-mode table](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L1721-L1725) |
| Stencil resolve mode | `none`, `zero`, `min`, `max` (no `average`) | Controls how per-sample stencil references are reduced. `average` is skipped because the spec does not define a stencil average mode. | [stencil average skip](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L1804-L1807) |
| Tested aspect | `testing_depth`, `testing_stencil`, `testing_pushconsts` | Selects which aspect the case verifies and which verification function runs. The push-constants variant is registered only for depth-only formats with `depth_average_stencil_none`. | [test case creation](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L1825-L1914) |

### Depth expected-value table

The depth-testing fragment shader assigns each sample a depth from the set `{0.04, 0.02, 0.16, 0.32}` by indexing
`gl_SampleID % 4` ([fragment source](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L1129-L1142)).
The expected resolved value is precomputed per resolve mode and sample count
([table](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L1744-L1751)):

| Depth resolve mode | 2 samples | 4 / 8 / 16 / 32 / 64 samples |
|--------------------|-----------|------------------------------|
| `none` | clear value (0.0) | clear value (0.0) |
| `zero` (sample 0) | 0.04 | 0.04 |
| `average` | 0.03 (mean of 0.04, 0.02) | 0.135 (mean of the four unique values) |
| `min` | 0.02 | 0.02 |
| `max` | 0.04 (max of the two 2-sample values) | 0.32 (max of the four unique values) |

For `none`, no resolve runs, so the resolve image keeps its pre-render clear value of `0.0` everywhere.

### Stencil expected-value table

The host draws once per sample, setting the stencil reference to `1` for the first half of samples and `255` for the
second half ([per-sample reference logic](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L761-L772)).
The expected resolved value is precomputed per resolve mode
([table](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L1752-L1759)):

| Stencil resolve mode | All sample counts |
|----------------------|-------------------|
| `none` | clear value (0) |
| `zero` (sample 0) | 1 |
| `min` | 1 |
| `max` | 255 |

## Behavior Parameters

The primary behavioral axis is the **resolve-mode pair** `(depthResolveMode, stencilResolveMode)` combined with the
**tested aspect** (`testing_depth`, `testing_stencil`, or `testing_pushconsts`). Each registered leaf fixes one legal
resolve-mode pair and verifies one aspect. The case-creation loop prunes illegal pairs (both modes `none`, stencil
`average`, or a non-`none` mode on an absent aspect) before emitting leaves
([pruning logic](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L1804-L1823)).

### `testing_depth`: depth resolve against a precomputed value

The case binds the multisampled image as the depth attachment and the single-sample image as its resolve target with
the chosen `depthResolveMode`. The fullscreen quad writes the per-sample depth set described above; the resolve step
reduces it to one value per pixel. The test passes when every pixel inside the render area matches the precomputed
expected depth within epsilon `0.002f`, and every pixel outside the render area still holds the clear value
([verifyDepth](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L913-L995)). A single
rendering pass is enough because every sample is written in one draw.

### `testing_stencil`: stencil resolve against a precomputed value

The case binds the same images but as the stencil attachment with the chosen `stencilResolveMode`. Because
`vkCmdSetStencilReference` sets a single reference for all samples, the host issues one rendering pass per sample,
discarding every fragment whose `gl_SampleID` does not match the current pass and writing the per-sample reference
into the surviving sample ([stencil pass loop](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L761-L772)).
The resolve step then reduces the per-sample stencil references, and `verifyStencil` byte-compares every pixel
against the precomputed expected value
([verifyStencil](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L997-L1056)).

### `testing_pushconsts`: layered resolve followed by a push-constant color draw

This variant is registered only for depth-only formats with `depth_average_stencil_none` and only when secondary
command buffers are not in use
([guard](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L1885-L1886)). It uses a
two-layer multisampled depth image (resolved via a geometry shader that broadcasts the quad to both layers), then
records a second dynamic rendering pass that draws a fullscreen quad into a separate single-sample color attachment
using a push-constant color. The depth resolve is verified as in `testing_depth`, and the color attachment is
compared against a solid green reference image. The case exercises the corner where depth/stencil resolve and a
subsequent push-constant-driven color render share the same command buffer
([DepthStencilPushConstResolveTest::iterate](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L1660-L1690)).

## Shader Analysis

Shader code is part of the tested behavior only insofar as it produces the per-sample depth and stencil inputs that
the resolve step reduces. The shaders themselves are simple and do not require a representative walkthrough.

The vertex shader ([`quad-vert`](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L1116-L1125))
generates a fullscreen triangle-list quad from `gl_VertexIndex` with no vertex inputs. When `imageLayers > 1`, a
geometry shader ([`quad-geom`](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L1087-L1113))
broadcasts the quad to each layer using `gl_Layer`.

The depth-testing fragment shader ([`quad-frag` depth variant](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L1129-L1142))
maps `gl_SampleID` to one of four depth values through integer arithmetic:

```glsl
float sampleIndex = float(gl_SampleID);
float valueIndex  = round(mod(sampleIndex, 4.0));   // 0,1,2,3
float value       = valueIndex + 2.0;                // 2,3,4,5
value             = round(exp2(value));              // 4,8,16,32
bool condition    = (int(value) == 8);
value             = round(value - float(condition) * 6.0); // 4,2,16,32
gl_FragDepth      = value / 100.0;                   // 0.04, 0.02, 0.16, 0.32
```

This deterministic per-sample mapping is what makes the expected-value tables exact: every sample with the same
`gl_SampleID % 4` writes the same depth, so the resolved value depends only on the resolve mode and (for `average`)
the sample count.

The stencil-testing fragment shader ([`quad-frag` stencil variant](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L1146-L1157))
discards every fragment whose `gl_SampleID` does not equal the push-constant `sampleID` for the current pass, then
writes `gl_FragDepth = 0.5`. Depth is irrelevant here; the discard plus per-pass `vkCmdSetStencilReference` is what
places a known stencil reference into exactly one sample per pass.

The push-constants variant adds a second vertex/fragment pair
([`vert-pc`](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L1162-L1178),
[`frag-pc`](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L1180-L1192)) that
outputs a push-constant `vec4` color to a color attachment, used only for the post-resolve color render.

## Runtime Execution and Result Checking

- **Images.** Each case creates a multisampled depth/stencil image (`sampleCount` samples) and a single-sample
  resolve image of the same format and extent (32×32). Both have `TRANSFER_SRC_BIT`; the resolve image also has
  `TRANSFER_DST_BIT` so it can be pre-cleared ([createImage](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L259-L286)).
- **Resolve-image pre-clear.** Before rendering, the resolve image is cleared to `{depth: 0.0, stencil: 0}` so that
  any pixel the resolve step does not touch retains a known value
  ([clear loop](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L585-L599)).
- **Layout transitions.** The resolve image moves `TRANSFER_DST_OPTIMAL → DEPTH_STENCIL_ATTACHMENT_OPTIMAL`, and the
  multisampled image moves `UNDEFINED → DEPTH_STENCIL_ATTACHMENT_OPTIMAL` before rendering
  ([barriers](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L557-L583)). When
  `separateDepthStencilLayouts` is set, the post-render barrier transitions only the tested aspect
  ([aspect-scoped barrier](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L863-L866)).
- **Dynamic rendering instance.** The case calls `vkCmdBeginRendering` with a `VkRenderingAttachmentInfo` whose
  `resolveMode`, `resolveImageView`, and `resolveImageLayout` configure the resolve. Depth cases attach the image as
  `pDepthAttachment`; stencil cases attach it as `pStencilAttachment`. `loadOp` is `CLEAR` and `storeOp` is `STORE`
  on the multisampled image ([depth attachment](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L608-L619),
  [stencil attachment](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L710-L721)).
- **Draws.** Depth cases draw the fullscreen quad once. Stencil cases draw once per sample, pushing the current
  sample index as a push constant and setting the per-sample stencil reference
  ([stencil draw loop](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L761-L772)).
- **Command-buffer variants.** The `SharedGroupParams` select primary, partial-secondary, or complete-secondary
  recording. Partial-secondary records draw commands in a secondary buffer bracketed by the primary's
  `cmdBeginRendering`/`cmdEndRendering`; complete-secondary records the entire rendering instance inside the
  secondary buffer with `VK_RENDERING_CONTENTS_SECONDARY_COMMAND_BUFFERS_BIT`
  ([secondary path](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L638-L689)).
- **Copyback.** After rendering, the resolve image transitions to `TRANSFER_SRC_OPTIMAL` (synchronized with
  `COLOR_ATTACHMENT_WRITE_BIT` per the spec note on resolve synchronization) and is copied to a host-visible buffer
  ([copy](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L872-L887)).
- **Depth verification.** `verifyDepth` decodes each pixel with a format-specific getter (16-bit, 24-bit packed, or
  32-bit float), classifies it as inside or outside the render area, and compares against the expected value with
  epsilon `0.002f`. Outside pixels must match the clear value; inside pixels must match the precomputed resolve
  result ([verifyDepth](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L913-L995)).
- **Stencil verification.** `verifyStencil` reads each byte and applies the same inside/outside classification with
  an exact byte comparison ([verifyStencil](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L997-L1056)).
- **Pass condition.** A case passes only if every checked pixel matches. The push-constants variant also
  requires the post-resolve color attachment to match a solid green reference image
  ([iterate](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L1660-L1690)).

| Resource | Created/configured by host? | Bound to GPU? | Device access | Host readback | Role |
|---------|-----------------------------|---------------|---------------|---------------|------|
| Multisampled depth/stencil image | Yes | Rendering depth/stencil attachment | Written by draw, read by resolve | No | Carries the per-sample depth/stencil inputs to be resolved. |
| Single-sample resolve image | Yes | Rendering resolve attachment | Written by resolve and pre-clear, read by copy | Yes, via transfer copy | Holds the resolved result under test. |
| Push-constant buffer (stencil, pushconsts variants) | Yes | `cmdPushConstants` | Read by fragment shader | No | Selects which sample the current draw writes (stencil) or the output color (pushconsts). |
| Readback buffer | Yes | Transfer destination | Written by copy command | Yes | Host-visible copy of the resolved aspect for pixel comparison. |
| Color image and buffer (pushconsts variant only) | Yes | Color attachment / transfer destination | Written by the post-resolve draw | Yes | Verifies a push-constant color render after depth resolve. |

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `testing_depth` with `zero`, `average`, `min`, or `max` | Resolve producing the wrong reduced depth for the mode; per-sample depth inputs not matching the shader's deterministic mapping. |
| `testing_depth` with `none` | Resolve running when it should not, overwriting the pre-clear value inside the render area. |
| `testing_stencil` with `zero`, `min`, or `max` | Resolve producing the wrong reduced stencil; per-sample stencil reference not landing in the intended sample due to discard or reference-setting defects. |
| `testing_stencil` with `none` | Resolve running when it should not, overwriting the pre-clear stencil value. |
| `testing_pushconsts` (depth part) | Same as the corresponding `testing_depth` `average` failure, plus layered resolve geometry routing. |
| `testing_pushconsts` (color part) | Push-constant update not visible to the post-resolve color draw; color attachment layout or copy defect. |
| Outside-render-area pixels on any case | Resolve, clear, or layout transition writing outside the render area. |
| Any case | Shared infrastructure: layout transition, copyback, or pixel-decode defect (for example, wrong depth-component getter for the format). |

### Cause Analysis

#### Wrong reduced value for a resolve mode

**Possible failure symptoms:** A depth or stencil `testing_*` case fails because pixels inside the render area do
not match the precomputed expected value for the chosen resolve mode, while pixels outside the render area still
hold the clear value.

**Possible implementation causes:** The resolve step must combine per-sample values according to the exact mode
selected in `VkRenderingAttachmentInfo::resolveMode`. A defect here would produce a value that corresponds to a
different mode (for example, `average` collapsing to `sample_zero` on implementations that lack real averaging, or
`min`/`max` swapped). The per-sample inputs are deterministic in this test, so a consistent wrong value across all
pixels points at the resolve computation rather than the inputs. Source-level investigation of the driver's resolve
path for the specific format and mode would be needed to confirm the mechanism.

#### Resolve running when `resolveMode` is `NONE`

**Possible failure symptoms:** A `testing_depth` or `testing_stencil` case whose resolve mode is `none` fails
because pixels inside the render area no longer hold the pre-clear value `{0.0, 0}`, even though no resolve should
have written them.

**Possible implementation causes:** `VK_RESOLVE_MODE_NONE` means the aspect is not resolved. If the implementation
still performs a resolve write for that aspect (for example, by treating `NONE` as `SAMPLE_ZERO` or by always
resolving when a resolve image is present), the pre-clear value is overwritten. This is a resolve-mode handling
defect in the dynamic rendering resolve path.

#### Per-sample stencil reference not landing in the intended sample

**Possible failure symptoms:** A `testing_stencil` case fails because the resolved stencil value is neither the
expected `1` (for `zero`/`min`) nor `255` (for `max`), suggesting the per-sample references were placed into the
wrong samples.

**Possible implementation causes:** The stencil path relies on per-pass `vkCmdSetStencilReference` plus a fragment
shader that discards every sample except the current pass. If sample-rate shading is not honoring
`gl_SampleID`, or if the dynamic stencil reference is applied to the wrong samples, the per-sample stencil
distribution fed into the resolve is wrong. The failure would then be in sample-rate fragment dispatch or dynamic
stencil reference handling rather than in the resolve itself.

#### Push-constant color render defect

**Possible failure symptoms:** The `testing_pushconsts` variant passes its depth verification but fails the
post-resolve color comparison against the solid green reference.

**Possible implementation causes:** The variant's second render pass draws a fullscreen quad whose fragment color
comes from a push constant. A mismatch points at push-constant update visibility across the two rendering instances
in the same command buffer, or at the color attachment layout transition and copyback used for that pass. Depth
resolve itself is not implicated when the depth check already passed.

#### Outside-render-area corruption

**Possible failure symptoms:** Any case fails because pixels outside the 32×32 render area (the whole image here,
but the check still classifies against `renderArea`) do not hold the pre-clear value.

**Possible implementation causes:** Resolve, clear, or layout-transition operations are scoped to the attachment
subresource, not to the render area, so they should not disturb pre-cleared pixels. A defect that bleeds writes
outside the intended region (for example, a resolve that writes the full image regardless of the render area, or a
layout transition that triggers an implicit clear) would produce this symptom.

## Case Pruning

### Requirement-based pruning

- Every case requires `VK_KHR_dynamic_rendering` and `VK_KHR_depth_stencil_resolve`
  ([checkSupport](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L1199-L1200)).
- Every case requires the `DEVICE_CORE_FEATURE_SAMPLE_RATE_SHADING` feature because the fragment shader depends on
  per-sample dispatch ([L1202](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L1202)).
- The `_separate_layouts` variants require `VK_KHR_separate_depth_stencil_layouts`
  ([L1207-L1208](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L1207-L1208)).
- The `testing_pushconsts` layered variants require `DEVICE_CORE_FEATURE_GEOMETRY_SHADER` because the geometry
  shader broadcasts the quad across layers ([L1204-L1205](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L1204-L1205)).
- Each requested depth or stencil resolve mode must be present in the device's
  `supportedDepthResolveModes` / `supportedStencilResolveModes`, and the depth/stencil mode combination must satisfy
  `independentResolve` / `independentResolveNone`; otherwise the case throws `NotSupportedError`
  ([mode checks](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L1224-L1248)).
- The chosen format, sample count, and layer count must be reported as supported by
  `getPhysicalDeviceImageFormatProperties`; otherwise the case throws `NotSupportedError`
  ([format/sample/layer checks](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L1256-L1283)).
- The whole family is excluded from Vulkan SC builds (`#ifndef CTS_USES_VULKANSC` around the dynamic-rendering
  registration block in [vktRenderPassTests.cpp#L8521-L8548](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8521-L8548)).

### Design-based pruning

- Stencil `average` is skipped because the spec defines no average stencil resolve mode
  ([L1804-L1807](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L1804-L1807)).
- The combination where both depth and stencil resolve modes are `none` is skipped because the spec forbids it when
  a resolve attachment is present ([L1811-L1813](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L1811-L1813)).
- A non-`none` resolve mode on an absent aspect is skipped: depth-only formats force stencil mode to `none` or to
  match the depth mode, and vice versa for stencil-only formats
  ([L1815-L1823](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L1815-L1823)).
- The `testing_pushconsts` variant is emitted only for depth-only formats with `depth_average_stencil_none` and only
  when secondary command buffers are not in use
  ([L1885-L1886](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L1885-L1886)).
- The family is registered under `primary_cmd_buff`, `partial_secondary_cmd_buff`, and
  `complete_secondary_cmd_buff` but not under `graphics_pipeline_library`, because the registration is gated on
  monolithic pipeline construction
  ([vktRenderPassTests.cpp#L8524-L8525](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8524-L8525)).

## Key Takeaways

- The test reduces correctness to a table lookup: a deterministic per-sample fragment shader feeds known depth and
  stencil inputs into the resolve, so each resolve mode has exactly one correct resolved value, precomputed in the
  source.
- Depth and stencil are verified in separate test case leaves because stencil testing needs per-sample discard,
  which would perturb the depth inputs. Combined formats still exercise both aspects, but not in the same case.
- `RESOLVE_MODE_NONE` is verified negatively: the resolve image is pre-cleared and must stay cleared inside the
  render area, proving the implementation did not resolve an aspect it was told to leave alone.
- The `_separate_layouts` variants exercise `VK_KHR_separate_depth_stencil_layouts` by transitioning only the tested
  aspect before copyback, catching defects where a combined-format layout transition disturbs the other aspect.
- The `testing_pushconsts` variant covers the corner where a layered depth resolve and a subsequent push-constant
  color render share one command buffer, a real-world sequence that simpler single-pass cases do not exercise.
- See [Failure Meaning](#failure-meaning) for how each failure mode maps to specific implementation defect
  categories.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test family factory | [vktDynamicRenderingDepthStencilResolveTests.cpp#L1926-L1931](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L1926-L1931) | Creates the `depth_stencil_resolve` group and calls `initTests` to populate it. |
| Case creation loop | [vktDynamicRenderingDepthStencilResolveTests.cpp#L1692-L1922](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L1692-L1922) | Enumerates sample counts, formats, resolve modes, and tested aspects; applies design-based pruning. |
| Expected-value tables | [vktDynamicRenderingDepthStencilResolveTests.cpp#L1744-L1759](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L1744-L1759) | Precomputed depth and stencil resolved values per resolve mode and sample count. |
| Support checks | [vktDynamicRenderingDepthStencilResolveTests.cpp#L1197-L1284](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L1197-L1284) | Extension, feature, resolve-mode, and image-format requirement checks. |
| Render pipeline and shaders | [vktDynamicRenderingDepthStencilResolveTests.cpp#L351-L462](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L351-L462) | Builds the graphics pipeline with dynamic rendering `VkPipelineRenderingCreateInfo`. |
| Shader sources | [vktDynamicRenderingDepthStencilResolveTests.cpp#L1078-L1195](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L1078-L1195) | Vertex, geometry, and both fragment shaders, plus the push-constants variant pair. |
| Submit and resolve | [vktDynamicRenderingDepthStencilResolveTests.cpp#L527-L911](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L527-L911) | Records the dynamic rendering instance with resolve, draw loops, barriers, and copyback. |
| Push-constants submit | [vktDynamicRenderingDepthStencilResolveTests.cpp#L1417-L1658](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L1417-L1658) | Layered resolve plus a second push-constant color render in one command buffer. |
| Depth verification | [vktDynamicRenderingDepthStencilResolveTests.cpp#L913-L995](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L913-L995) | Format-specific depth decode and inside/outside comparison against the expected value. |
| Stencil verification | [vktDynamicRenderingDepthStencilResolveTests.cpp#L997-L1056](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L997-L1056) | Byte-wise stencil comparison against the expected value. |
| Group attachment | [vktRenderPassTests.cpp#L8527](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8527) | Adds the family under each dynamic-rendering intermediate node. |
| Mustpass entries | [renderpasses.txt](../../../mustpass/main/vk-default/renderpasses.txt) | Lists all `dEQP-VK.renderpasses.dynamic_rendering.{primary_cmd_buff,partial_secondary_cmd_buff,complete_secondary_cmd_buff}.depth_stencil_resolve.*` leaves. |
