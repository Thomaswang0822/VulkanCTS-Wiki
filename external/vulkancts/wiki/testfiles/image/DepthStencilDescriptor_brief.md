# Understanding Brief: `image.depth_stencil_descriptor`

## One-Sentence Test Purpose

This test checks whether a depth or stencil aspect in a selected depth/stencil image layout can remain usable through its legal attachment access while shaders read that same aspect through sampled-image or input-attachment descriptors.

## Background Knowledge

### Aspect-only views and descriptor layouts

A depth/stencil format can contain a depth aspect, a stencil aspect, or both. A descriptor view of such an image selects exactly one of those aspects; Vulkan requires a descriptor image view of a depth/stencil image to include depth or stencil, but not both ([descriptor validity](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3667-L3671)). `VkDescriptorImageInfo::imageLayout` describes the layout in which the view's subresources will be when the descriptor is accessed ([descriptor image information](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3618-L3629)).

Why it matters here:

- The tested layouts grant different access to depth and stencil. For example, `DEPTH_READ_ONLY_STENCIL_ATTACHMENT_OPTIMAL` makes depth read-only while stencil remains an attachment aspect.
- The test creates depth-only and stencil-only views, then reads only the aspect whose selected access permits a descriptor.

### Three read-only uses

A graphics path can use a read-only aspect as a depth/stencil attachment, an input attachment, a sampled image, or a permitted combination of those uses. An input attachment is a fragment-shader descriptor tied to the fragment's framebuffer location; its view and layout are supplied by `VkDescriptorImageInfo`, while the render pass identifies the accessible aspect.

Why it matters here:

- The test distinguishes the attachment role, which can affect depth/stencil testing, from descriptor reads, which copy a value to a storage image.
- A compute pipeline has no render pass or depth/stencil test, so it covers only sampled-image cases.

## One Concrete Example

Consider the registered path:

```text
dEQP-VK.image.depth_stencil_descriptor.depth_read_only_optimal.d32_sfloat.depth_sampled_stencil_none_compute
```

The depth-only `D32_SFLOAT` image is cleared to `0.5`, transitioned to `VK_IMAGE_LAYOUT_DEPTH_READ_ONLY_OPTIMAL`, and exposed through a depth-only sampled-image view. A compute shader samples each texel with an unnormalized-coordinate sampler and writes the result into an `R32_SFLOAT` storage image. The host reads that storage image back and accepts each value within `0.1` of `0.5`.

## End-to-End Test Flow

```text
[host] choose a layout, compatible depth/stencil format, legal per-aspect access, and graphics or compute mode
[host] create one 8×8 depth/stencil image, aspect-only descriptor views, output storage images, descriptor sets, and a pipeline
[host] clear the depth aspect to 0.5 and the stencil aspect to 100
[host] transition the depth/stencil image from transfer destination to the selected descriptor/attachment layout
[device] run a compute dispatch, or run one or two fullscreen graphics draws with the selected attachment state
[device] copy every descriptor read into a float depth or uint stencil storage image
[host] copy attachment aspects and storage images to host-visible buffers after barriers and queue completion
[host] check graphics color, expected attachment values, and each descriptor-read value
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

`DepthStencilDescriptorCase::initPrograms()` builds GLSL source from the requested descriptors ([generator](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L522-L647)). For every input descriptor, it generates either `subpassLoad()` for an input attachment or `texture()` for a sampled image, then writes that value with `imageStore()` to an aspect-matched storage image. Graphics cases also generate a fullscreen vertex shader and a fragment shader that writes a pass/fail color.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Depth/stencil image | Yes | Yes | Cleared, used as an attachment and/or read by descriptors | Yes | Contains the aspect values and layout/access combination under test. |
| Depth-only or stencil-only image view | Yes | Yes, in input descriptors | Read by fragment or compute shader | Indirectly | Restricts each descriptor to exactly one depth/stencil aspect. |
| Descriptor-read output image | Yes | Yes, as an `R32_SFLOAT` or `R32_UINT` storage image | Written by shader | Yes | Makes each descriptor load observable to the host. |
| Color attachment, graphics only | Yes | Yes | Written by fullscreen draw | Yes | Shows whether the required depth/stencil attachment tests passed. |
| Aspect and output verification buffers | Yes | Transfer destinations | Written by image-to-buffer copies | Yes | Provide the final host comparisons. |

## What Is Checked

- Graphics cases require the color image to be green. When a depth or stencil attachment test is active, the first draw deliberately fails it and produces red; the final draw must pass and overwrite the color result with green.
- The read-back depth aspect must equal `0.5` when it remains read-only, or `0.0` when the selected graphics depth write occurs. The test uses a `0.1` depth tolerance.
- The read-back stencil aspect must equal `100` when it remains read-only, or `10` when the selected graphics stencil write occurs.
- Each storage image must contain the original clear value for its descriptor-selected aspect: `0.5` for depth or `100` for stencil.

## Behavior Parameter Identification

> **Behavior parameter:** `layout`
>
> **Candidate values:** `depth_read_only_stencil_attachment_optimal`, `depth_attachment_stencil_read_only_optimal`, `depth_read_only_optimal`, `stencil_read_only_optimal`

The selected layout is the primary behavioral axis because it decides which aspect is read-only and descriptor-readable, which aspect may be an attachment with read/write behavior, and which formats can contribute cases.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `depth_read_only_stencil_attachment_optimal` | Incorrect depth descriptor access while stencil acts as an attachment, aspect-view selection, layout transition, or descriptor/attachment coexistence. |
| `depth_attachment_stencil_read_only_optimal` | Incorrect stencil descriptor access while depth acts as an attachment, aspect-view selection, layout transition, or descriptor/attachment coexistence. |
| `depth_read_only_optimal` | Incorrect descriptor access to a depth-only format/aspect in the depth-read-only layout, sampled/input descriptor setup, or compute sampled path. |
| `stencil_read_only_optimal` | Incorrect descriptor access to a stencil-only format/aspect in the stencil-read-only layout, sampled/input descriptor setup, or compute sampled path. |

## Important Variations and Special Cases

- The factory covers `D16_UNORM`, `X8_D24_UNORM_PACK32`, `D32_SFLOAT`, `S8_UINT`, `D16_UNORM_S8_UINT`, `D24_UNORM_S8_UINT`, and `D32_SFLOAT_S8_UINT`, but retains only format/layout pairs whose actual aspects match the layout's legal aspect accesses.
- Read-only accesses are registered as `att`, `ia`, `sampled`, `att_sampled`, and `ia_sampled`. Input attachment and depth/stencil attachment use cannot be mixed across different aspects of a two-aspect image, because the source intentionally excludes that incompatible shape.
- A `_compute` leaf is added only when the case uses sampled descriptors alone. These leaves clear depth/stencil through aspect-specific buffer-to-image copies on the compute queue and require the maintenance10 copy-on-compute format features.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Layout-to-aspect access model | [`layoutExtension()` and `getLegalAccess()`](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L79-L164) | Defines the extension gates and legal read-only/read-write access for each tested layout. |
| Descriptor selection and compute eligibility | [`TestParams` helpers](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L270-L395) | Derives image usage, descriptors, attachment needs, and compute-only eligibility. |
| Support checks and GLSL generator | [`checkSupport()` and `initPrograms()`](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L457-L647) | Defines prerequisites and generated descriptor-read shaders. |
| Runtime and result comparisons | [`DepthStencilDescriptorInstance::iterate()`](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L667-L1585) | Creates resources, executes the selected path, and checks all read-back values. |
| Registration matrix | [`createImageDepthStencilDescriptorTests()`](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L1589-L1759) | Defines layouts, formats, access combinations, exclusions, and `_compute` leaves. |
| Default Vulkan mustpass coverage | [`depth-stencil-descriptor.txt`](../../../mustpass/main/vk-default/image/depth-stencil-descriptor.txt#L1-L42) | Provides executable default-Vulkan path examples. |

## Questions / Risk Points for User Audit

- Is the distinction between an aspect's attachment role and its descriptor-read role clear?
- Does the representative compute example make clear why `_compute` appears only for sampled-image cases?
- Does the failure mapping use the layout as the right primary behavioral axis?
- Should a final reader-facing page retain the generated compute walkthrough, the graphics observer path, or both?

## Conversion Notes for Final Wiki Rewrite

- Retain a short explanation of aspect-only descriptor views and `VkDescriptorImageInfo::imageLayout` in the final Background Knowledge section.
- Use the compute sampled-depth case as the representative shader walkthrough because one generated shader exposes the descriptor, sampler, coordinate, and output-storage relationship without graphics attachment boilerplate.
- Distill the graphics path into runtime prose. Its two-draw color oracle and attachment-aspect read-back are more useful there than as a second walkthrough.
- Copy the `### Failure Cause Mapping` table above unchanged into the final Level-3 page, then write fresh cause analysis from the actual comparisons.
