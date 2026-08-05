## Overview

**Core question:** when a render pass writes a distinct value into each sample of a multisample attachment, can a later subpass read each individual sample back through a multisample input attachment and resolve it correctly?

- This page covers the `renderpasses.<rendering>.suballocation.multisample` test family implemented entirely in
  [vktRenderPassMultisampleTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp).
- The test family registers 57 format-named intermediate nodes plus one `separate_stencil_usage` intermediate node under
  `multisample`, attached to the `suballocation` group at
  [vktRenderPassTests.cpp#L8560](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8560).
- For every supported color, depth-only, stencil-only, and depth-stencil format, the test renders a per-sample-distinct
  pattern into a multisample attachment, then reads each sample back with a multisample input attachment in a follow-up
  subpass, resolves it to a single-sample image, and compares it against an XOR-based reference computed on the host.
- The same logic runs under legacy render pass (`renderpass1`), render pass 2 (`renderpass2`), and dynamic rendering
  (`dynamic_rendering`). The representative root shown below is `renderpass1`; the registered name differs only in the
  rendering-type root.

## Background Knowledge

- **Multisample attachment samples are independent.** A multisample color or depth/stencil attachment stores one value
  per sample location per pixel. Per-sample writes controlled by `gl_SampleMask` therefore land in distinct sample
  slots, and a correct implementation must keep those slots separate until resolve.
- **Multisample input attachment reads.** A multisample input attachment (`subpassInputMS` in GLSL) is read with
  `subpassLoad(i_attach, sampleIndex)`, which returns the value stored in one specific sample. The Vulkan spec restricts
  a fragment to the samples covered by its input `SampleMask`, so the test renders a single fully-covered triangle to
  guarantee every sample is readable in every fragment.
- **Resolve.** Resolving combines the per-sample values of a multisample image into one single-sample pixel. For color
  the default is averaging; for integer formats the test forces sample-zero resolve. The test resolves each sample
  independently into its own single-sample image, so the host can inspect every sample separately.
- **`MAX_COLOR_ATTACHMENT_COUNT` split.** Vulkan limits a subpass to four color attachments. To copy all samples of a
  high-sample-count attachment out through color attachments, the test splits the copies across multiple follow-up
  subpasses, each handling up to four samples.

## Registration Hierarchy

```text
renderpasses.renderpass1.suballocation.multisample
├── a2b10g10r10_uint_pack32
├── a2b10g10r10_unorm_pack32
├── a2r10g10b10_unorm_pack32
├── a8_unorm
├── a8b8g8r8_sint_pack32
├── a8b8g8r8_snorm_pack32
├── a8b8g8r8_srgb_pack32
├── a8b8g8r8_uint_pack32
├── a8b8g8r8_unorm_pack32
├── b8g8r8a8_srgb
├── b8g8r8a8_unorm
├── d16_unorm
├── d16_unorm_s8_uint
├── d24_unorm_s8_uint
├── d32_sfloat
├── d32_sfloat_s8_uint
├── r10x6g10x6b10x6a10x6_unorm_4pack16
├── r16_sfloat
├── r16_sint
├── r16_snorm
├── r16_uint
├── r16_unorm
├── r16g16_sfloat
├── r16g16_sint
├── r16g16_snorm
├── r16g16_uint
├── r16g16_unorm
├── r16g16b16a16_sfloat
├── r16g16b16a16_sint
├── r16g16b16a16_snorm
├── r16g16b16a16_uint
├── r16g16b16a16_unorm
├── r32_sfloat
├── r32_sint
├── r32_uint
├── r32g32_sfloat
├── r32g32_sint
├── r32g32_uint
├── r32g32b32a32_sfloat
├── r32g32b32a32_sint
├── r32g32b32a32_uint
├── r5g6b5_unorm_pack16
├── r8_sint
├── r8_snorm
├── r8_uint
├── r8_unorm
├── r8g8_sint
├── r8g8_snorm
├── r8g8_uint
├── r8g8_unorm
├── r8g8b8a8_sint
├── r8g8b8a8_snorm
├── r8g8b8a8_srgb
├── r8g8b8a8_uint
├── r8g8b8a8_unorm
├── s8_uint
├── separate_stencil_usage
└── x8_d24_unorm_pack32
```

The `multisample` test family is created by
[`createRenderPassMultisampleTests()`](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L2513-L2516).
Its format-named intermediate nodes are added in
[`initTests()`](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L2392-L2509), and the
`separate_stencil_usage` node is attached at the end of that same function
([vktRenderPassMultisampleTests.cpp#L2456-L2508](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L2456-L2508)).
Each format-named node expands to `samples_<N>` test case leaves for N in {2, 4, 8, 16, 32}; the
`separate_stencil_usage` node expands to `<format>/samples_<N>/test_depth` and `test_stencil` leaves.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Format | 57 `VkFormat` values spanning color, depth-only, stencil-only, and depth-stencil classes | Selects the multisample attachment format. The format drives the generated fragment shader type (`vec4`/`ivec4`/`uvec4`), the input-attachment GLSL type, the destination resolve format, and the host comparison routine. | [formats array](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L2394-L2453) |
| Sample count | `2`, `4`, `8`, `16`, `32` | The multisample attachment sample count. Each sample receives a distinct XOR-pattern value; higher counts exercise more split subpasses and more per-sample reads. | [sampleCounts](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L2454) |
| Separate stencil usage | `TEST_DEPTH`, `TEST_STENCIL` | Only used inside `separate_stencil_usage`. Selects whether the depth aspect or the stencil aspect of a combined depth/stencil format is exercised with `VK_EXT_separate_stencil_usage`. | [TestSeparateUsage enum](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L97-L101) |

The 57 entries in the formats array map one-to-one to the 57 registered format-named nodes; each node expands to
`samples_<N>` test case leaves for N in {2, 4, 8, 16, 32}. The `separate_stencil_usage` node is a separate registration
that reuses three of the depth/stencil formats with an extra `VkImageStencilUsageCreateInfo`.

## Behavior Parameters

The primary behavioral axis is the format class of the multisample attachment, because it changes which aspect is
written, how the per-sample value is generated, and how the host validates the result. The `separate_stencil_usage`
node is a second, smaller axis that reuses the depth/stencil path with a separate-usage image.

### Color formats: per-sample XOR color written through `gl_SampleMask`

For each color format the first subpass draws one fully-covered triangle `sampleCount` times. Each draw writes exactly
one sample (`gl_SampleMask[0] = int(0x1u << sampleIndex)` for unsigned/signed/floating paths) and computes a per-pixel
color from an XOR of the fragment coordinate bits with the sample index
([Programs::init color path](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L2014-L2199)). The
generated color type matches the format's channel class: `uvec4` for unsigned integer, `ivec4` for signed integer, and
`vec4` for unsigned/signed fixed-point and floating-point. Each follow-up subpass then reads the multisample input
attachment one sample at a time with `subpassLoad(i_color, sampleIndex)` and writes it to one of up to four color
attachments, which the render pass resolves to single-sample images.

### Depth-only and stencil-only formats: depth value or stencil counter per sample

Depth-only formats (`d16_unorm`, `x8_d24_unorm_pack32`, `d32_sfloat`) write a per-sample depth computed from the same
XOR bit pattern, and the stencil-only format `s8_uint` writes a per-sample stencil counter through
`VK_STENCIL_OP_INCREMENT_AND_WRAP`. The first-subpass shader for depth sets
`gl_SampleMask[0] = int((~0x0u) << sampleIndex)` and writes `gl_FragDepth`
([depth shader](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L1963-L2000)); the stencil path
sets the same mask and lets the fixed-function stencil stage increment the value
([stencil shader](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L2001-L2013)). Follow-up subpasses
read each sample back through a depth or stencil multisample input attachment and copy it to a color attachment.

### Depth-stencil formats: both aspects read in one pass

Combined depth/stencil formats (`d16_unorm_s8_uint`, `d24_unorm_s8_uint`, `d32_sfloat_s8_uint`) write both aspects in
the first subpass and read both back through two input attachments (`i_depth` and `i_stencil`) in the split subpasses
([split shader](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L2206-L2269)). The destination
format for these cases is `VK_FORMAT_R32G32_SFLOAT`, packing depth and stencil into one resolve target.

### `separate_stencil_usage`: `VK_EXT_separate_stencil_usage` aspect isolation

The `separate_stencil_usage` node applies only to the three combined depth/stencil formats. For each, it registers two
leaves per sample count: `test_depth` and `test_stencil`
([registration](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L2481-L2501)). The test creates
the source image with a `VkImageStencilUsageCreateInfo` that assigns a different usage to the stencil aspect than to
the depth aspect ([createImage](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L162-L202)), then
exercises only the selected aspect through the matching input attachment view
([createSrcPrimaryInputImageView](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L315-L327)).

## Shader Analysis

The shaders are generated per format class and are not the focus of the tested behavior; the per-sample isolation is
enforced by `gl_SampleMask` and the multisample input-attachment read, both of which are fixed-function or
straightforward GLSL constructs. A representative walkthrough would add no insight beyond the behavior already
described, so no `### Representative Shader Walkthrough` subsection is included. The generated fragment shaders live
in [`Programs::init()`](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L1938-L2326).

## Runtime Execution and Result Checking

The host builds one multisample source image, `sampleCount` multisample destination color images, `sampleCount`
single-sample resolve images, and `sampleCount` host-visible readback buffers
([constructor](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L1056-L1130)).

A single command buffer records the render pass
([iterateInternal](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L1368-L1427) for legacy and
render pass 2, [iterateInternalDynamicRendering](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L1429-L1587)
for dynamic rendering):

- The first subpass draws the quad `sampleCount` times, each time pushing a different `sampleIndex` and letting the
  fragment shader mask coverage to one sample
  ([drawFirstSubpass](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L1646-L1655)).
- For stencil-bearing formats the stencil aspect is cleared to zero before the first draw so the increment produces a
  known per-sample value ([iterateInternal](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L1392-L1408)).
- Each follow-up subpass binds one split pipeline, pushes its `splitSubpassIndex`, and copies up to four samples out of
  the input attachment into color attachments that the render pass resolves
  ([drawNextSubpass](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L1657-L1666)). The number of
  split subpasses is `ceil(sampleCount / 4)`.
- After the render pass, each single-sample resolve image is copied to its host-visible buffer
  ([postRenderCommands](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L1668-L1677)).

Result checking happens per sample in
[`verifyResult()`](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L1679-L1934). For each sample
the host recomputes the same XOR-based reference the shader used, then compares the readback buffer against it:

- **Depth** uses `tcu::floatThresholdCompare` with a threshold of `1.0f / 1024.0f`
  ([vktRenderPassMultisampleTests.cpp#L1702-L1747](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L1702-L1747)).
- **Stencil** uses an exact integer comparison
  ([vktRenderPassMultisampleTests.cpp#L1724-L1747](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L1724-L1747)).
- **Color** dispatches on `tcu::TextureChannelClass`: unsigned and signed integer formats use exact
  `tcu::intThresholdCompare` with a zero threshold; floating-point formats use `tcu::floatUlpThresholdCompare` allowing
  64 ULP; fixed-point formats use `tcu::floatThresholdCompare` allowing four times the minimum presentable difference
  ([vktRenderPassMultisampleTests.cpp#L1749-L1930](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L1749-L1930)).
  sRGB formats are compared in sRGB space.
- Any per-sample mismatch is recorded through `m_resultCollector.fail("Compare failed for sample " + ...)`, and the
  case returns the aggregated status.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| Color format | Per-sample color value wrong, input-attachment per-sample read returns the wrong sample, or resolve picked the wrong sample / averaged when it should not. |
| Depth-only format | Per-sample depth value wrong, depth input-attachment read returns the wrong sample, or depth resolve mode incorrect. |
| Stencil-only format (`s8_uint`) | Stencil clear or increment wrong, stencil input-attachment read returns the wrong sample, or stencil resolve incorrect. |
| Depth-stencil format | Depth or stencil aspect wrong (same causes as the single-aspect cases), or the two aspects interfered when packed into the `R32G32_SFLOAT` resolve target. |
| `separate_stencil_usage` `test_depth` | Depth aspect value wrong when the stencil aspect has a separate usage, or the separate-usage image view exposed the wrong aspect. |
| `separate_stencil_usage` `test_stencil` | Stencil aspect value wrong when it has a separate usage, or the stencil aspect was not actually isolated from the depth aspect. |

A failure shared across all values, for example a wrong sample count, a wrong resolve target, or a host reference bug , 
would point at the shared render-pass / resolve infrastructure rather than a format-specific path.

### Cause Analysis

#### Per-sample value or coverage wrong

**Possible failure symptoms:** the compared image for one or more samples differs from the XOR reference; the mismatch
follows a sample-index pattern (for example only odd samples, or only the first subpass's four samples).

**Possible implementation causes:** the fragment shader computed the wrong per-sample value, `gl_SampleMask` did not
isolate the intended sample, or the depth/stencil state wrote depth or stencil to a sample other than the masked one.
The host recomputes the same XOR pattern, so a shader-compiler lowering of `bitfieldExtract` or `gl_SampleMask` that
changed coverage would surface here.

#### Multisample input-attachment read returns the wrong sample

**Possible failure symptoms:** the resolve image for sample *i* contains the value that should have landed in sample
*j*, or a swapped/mirrored sample ordering across the split subpasses.

**Possible implementation causes:** the implementation's `subpassLoad` on a multisample input attachment returned the
wrong sample index, the split-pipeline `splitSubpassIndex` push constant was misrouted, or the
`VK_KHR_dynamic_rendering_local_read` attachment-location / input-attachment-index remapping pointed at the wrong
sample for the dynamic-rendering path.

#### Resolve picked the wrong sample or mode

**Possible failure symptoms:** the single-sample resolve image holds an averaged value instead of one specific sample
(for integer formats), or holds sample zero instead of the requested sample.

**Possible implementation causes:** the resolve mode was not set to `VK_RESOLVE_MODE_SAMPLE_ZERO_BIT` for integer color
formats, the resolve attachment was bound to the wrong source sample, or the per-sample single-sample resolve target
received a resolve from the wrong multisample image. The test deliberately uses one resolve target per sample to expose
exactly this kind of mismatch.

#### Depth/stencil aspect isolation or packing wrong

**Possible failure symptoms:** for combined depth/stencil formats, only one of the two channels of the `R32G32_SFLOAT`
resolve matches; for `separate_stencil_usage`, the aspect that was supposed to be untested still appears in the result.

**Possible implementation causes:** the depth and stencil input-attachment views exposed the wrong aspects, the
separate-usage create-info did not actually separate the aspects, or the packed `vec2(depth, stencil)` write was
reordered. Source-level investigation is needed before attributing these to driver or hardware.

## Case Pruning

### Requirement-based pruning

- `VK_KHR_create_renderpass2` is required for the `renderpass2` root
  ([checkSupport](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L2328-L2380)).
- `VK_KHR_dynamic_rendering_local_read` is required for the `dynamic_rendering` root; on Vulkan 1.4 and above the test
  also requires `dynamicRenderingLocalReadMultisampledAttachments`, and for depth/stencil formats
  `dynamicRenderingLocalReadDepthStencilAttachments`.
- `VK_EXT_separate_stencil_usage` plus `VK_KHR_get_physical_device_properties2` are required for any case under
  `separate_stencil_usage`.
- `VK_KHR_maintenance5` is required for `VK_FORMAT_A8_UNORM_KHR` (`a8_unorm`).
- A case is skipped with `NotSupportedError` when the physical device does not support the format as a color or
  depth/stencil attachment at the requested sample count
  ([createImage](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L235-L292)).

### Design-based pruning

- Non-monolithic pipelines (pipeline libraries and fast-linked libraries) skip `samples_16` and `samples_32`, so only
  `samples_2`, `samples_4`, and `samples_8` are registered for those pipeline construction types
  ([initTests](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L2467-L2470)). This trims
  redundant repetition of the same per-sample behavior at high sample counts.
- The `separate_stencil_usage` node is populated only for the three combined depth/stencil formats, because the
  extension only applies where depth and stencil coexist in one image
  ([initTests](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L2482-L2484)).

## Key Takeaways

- The test isolates each sample of a multisample attachment by masking coverage to one sample per draw, then reads that
  sample back through a multisample input attachment. A failure almost always means a sample was not kept separate.
- The four-color-attachment limit forces the readback into `ceil(sampleCount / 4)` split subpasses; a mismatch that
  clusters by groups of four samples points at split-subpass routing, not at the format itself.
- Resolve is intentionally per-sample: one single-sample image per sample. Integer formats use sample-zero resolve;
  other color formats average; depth/stencil is copied through a packed `R32G32_SFLOAT` target.
- `separate_stencil_usage` reuses the depth/stencil path with a `VkImageStencilUsageCreateInfo`, so a failure there
  isolates whether separate stencil usage correctly decoupled the two aspects.
- See `## Failure Meaning` for how each symptom maps to a cause.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test family creation | [createRenderPassMultisampleTests](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L2513-L2516) | Top-level group named `multisample`. |
| Registration / matrix | [initTests](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L2392-L2509) | Builds the 57 format nodes, the sample-count leaves, and the `separate_stencil_usage` node. |
| Format and sample-count tables | [formats / sampleCounts](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L2394-L2454) | The generated matrix dimensions. |
| Test instance | [MultisampleRenderPassTestInstance](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L984-L1054) | Resource setup, pipelines, and iterate entry points. |
| Render pass construction | [createRenderPass (template)](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L470-L717), [createRenderPass (dispatch)](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L719-L738) | Builds the multi-subpass render pass with input and resolve attachments. |
| Separate-usage image creation | [createImage](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L162-L202) | Wires `VkImageStencilUsageCreateInfo` for `separate_stencil_usage`. |
| Shader generation | [Programs::init](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L1938-L2326) | Generates `quad-vert`, `quad-frag`, and `quad-split-frag` per format class. |
| Feature / support checks | [checkSupport](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L2328-L2380) | Extension and limit gating per rendering type. |
| Result verification | [verifyResult](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L1679-L1934) | Per-sample host comparison and tolerance selection. |
| Attachment to category | [vktRenderPassTests.cpp#L8560](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8560) | Where `multisample` is attached under `suballocation`. |
