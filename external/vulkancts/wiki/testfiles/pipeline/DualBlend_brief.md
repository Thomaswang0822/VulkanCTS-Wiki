# Understanding Brief: dual-source blend multi-attachment tests

## One-Sentence Test Purpose

This test checks whether Vulkan dual-source blending produces the same color result as an equivalent ordinary blend across four color attachments for each supported blend format.

## Background Knowledge

### Dual-source blending

A fragment shader can write two outputs for one color attachment: index 0 supplies the ordinary source color and index 1 supplies the second source used by `VK_BLEND_FACTOR_SRC1_COLOR`, `VK_BLEND_FACTOR_SRC1_ALPHA`, and their complements. The `dualSrcBlend` feature permits those factors, while `maxFragmentDualSrcAttachments` limits how many attachments can use the dual-source form at once. This test uses the second output only for attachment 0 and compares the result with a pipeline that writes four ordinary outputs.

Why it matters here:
- The two outputs share location 0 but use output indices 0 and 1.
- The generic reference replaces `SRC1` factors with ordinary `SRC` factors and writes all four attachments.
- A match on the selected attachment tests the arithmetic path without treating the two shader programs as identical implementations.

### Blend format and attachment state

Vulkan applies color blending per color attachment. The format controls component count, numeric representation, channel write mask, and comparison threshold. Formats without an alpha component still run the color part of the matrix, while alpha blend factors and operations are disabled for those formats by the generator.

## One Concrete Example

For `r8g8b8a8_unorm`, the host supplies four push-constant colors to the generic fragment shader. It supplies the color at `reusedColor = 2` to every field of the dual-source shader. The generic draw writes four attachments. The dual-source draw writes only attachment 0, using two fragment outputs at location 0. The test then compares the dual-source image for attachment 0 with the generic image for attachment 2, and checks that the other dual-source attachments retain the expected cleared contents.

The shader sources are generated inline in [`DualSourceBlendMACase::initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineDualBlendTests.cpp#L903-L945). The fragment shader is deliberately simple: the blend state, rather than shader control flow, carries the behavior under test.

## End-to-End Test Flow

```text
[host] select one registered format and initialize the blend-state generator
[host] create four same-format color images, views, render targets, and host-visible readback buffers
[host] generate the common vertex shader and the generic and dual-source fragment shaders
[host] clear source and destination image/buffer state
[host] submit a generic draw with four outputs and genericized blend factors
[device] blend the four outputs into four attachments and write the generic readback buffers
[host] clear the images and submit a dual-source draw to attachment 0
[device] blend output indices 0 and 1 with the selected dual-source factors
[host] copy all attachments to the dual readback buffers and wait for host visibility
[host] compare the required buffers with format-aware thresholds and report pass, fail, or quality warning
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `common_vert` is a GLSL 4.50 vertex shader that maps one `vec4` position input to `gl_Position`.
- `generic_frag` declares four push-constant `vec4` values and four fragment outputs at locations 0 through 3.
- `dual_frag` declares the same push-constant block and two outputs at location 0 with indices 0 and 1.
- The host generates a `VkPipelineColorBlendAttachmentState` combination from source and destination color and alpha factors plus color and alpha blend operations. Each vector is capped at five entries for the iteration matrix.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Four same-format color images and views | yes | yes | written by fragment blending | copied indirectly | Hold generic and dual-source render results. |
| Generic and dual-source render passes/framebuffers or dynamic-rendering attachments | yes | yes | used as color targets | no | The generic path exposes four outputs; the dual-source path enables only attachment 0 for the relevant draw. |
| Push-constant `PC` block | yes | yes | read by fragment shaders | no | Supplies the four source colors to the two fragment programs. |
| Vertex buffer | yes | yes | read by the vertex stage | no | Provides the triangle geometry. |
| Source, destination, generic, and dual readback buffers | yes | transfer destination | written by image-to-buffer copies | yes | Preserve cleared and rendered pixels for the host comparisons. |

## What Is Checked

- The generic draw first establishes four reference images using genericized blend factors.
- Before the dual-source draw, the test skips an iteration with `QUALITY_WARNING` if the selected destination buffer is all zero bytes. This avoids treating a blend state that produces no useful destination result as a meaningful pass.
- For attachment 0, the generic result must differ from the destination and source reference buffers, and the dual-source result must match the generic result for `reusedColor`, which is attachment 2.
- For attachments 1 through 3, the dual-source result must match the corresponding generic result after the dual-source draw leaves those attachments untouched.
- `compareBuffers()` reads every pixel and channel and accepts only differences below `getFormatThreshold(format, 1)`.

## Behavior Parameter Identification

> **Behavior parameter:** blend-state combination within one format
>
> **Candidate values:** the generated combinations of source color factor, destination color factor, source alpha factor, destination alpha factor, color blend operation, and alpha blend operation, with `SRC1` factors selected by the fixed dual-source mask `dstColorFactor | dstAlphaFactor`.

The format is the page's registration dimension; the blend-state combination is the primary behavioral axis because it changes the equation being checked. Pipeline construction type changes how the same behavior is constructed and is a coverage dimension.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| A generated blend-state combination for a format with an alpha component | Incorrect dual-source blend-factor or blend-operation behavior, format conversion, attachment routing, or reference setup for that combination. |
| A generated blend-state combination for a format without an alpha component | Incorrect color blending, channel-mask handling, format conversion, attachment routing, or reference setup for that combination. |

## Important Variations and Special Cases

- The registration loop creates one test case per format returned by `getBlendFormats()`, covering non-integer, uncompressed blend formats from `R4G4_UNORM_PACK8` through `R10X6G10X6B10X6A10X6_UNORM_4PACK16`.
- The blend-state generator uses the format's channel count to exclude alpha factors for formats without an alpha component.
- The same test family runs through the construction variants represented by the mustpass files, including monolithic, fast-linked library, pipeline library, and shader-object paths. Shader-object cases require `VK_EXT_shader_object`, `VK_EXT_color_write_enable`, dynamic rendering, and the corresponding dynamic state commands.
- The source guards registration with `#ifndef CTS_USES_VULKANSC`.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Format registration | [`addDualBlendMultiAttachmentTests()`](../../../modules/vulkan/pipeline/vktPipelineDualBlendTests.cpp#L1758-L1774) and [`getBlendFormats()`](../../../modules/vulkan/pipeline/vktPipelineBlendTestsCommon.cpp#L41-L89) | Defines the test case leaves and format set. |
| Shader generation | [`DualSourceBlendMACase::initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineDualBlendTests.cpp#L903-L945) | Defines all three generated shader artifacts. |
| Feature checks | [`DualSourceBlendMACase::checkSupport()`](../../../modules/vulkan/pipeline/vktPipelineDualBlendTests.cpp#L871-L901) | Defines feature, limit, construction, and format pruning. |
| Blend-state matrix | [`BlendAttachmentStateGenerator`](../../../modules/vulkan/pipeline/vktPipelineDualBlendTests.cpp#L952-L1155) and [`getBlendOps()`](../../../modules/vulkan/pipeline/vktPipelineBlendTestsCommon.cpp#L150-L155) | Defines the generated behavior combinations. |
| Per-case setup and draws | [`iteratePerArgs()`](../../../modules/vulkan/pipeline/vktPipelineDualBlendTests.cpp#L1249-L1609) | Defines colors, clears, barriers, generic and dual-source draws, and comparisons. |
| Pixel comparison | [`compareBuffers()`](../../../modules/vulkan/pipeline/vktPipelineDualBlendTests.cpp#L1619-L1677) | Defines the host-side tolerance check. |
| Dual-source feature semantics | [`dualSrcBlend`](../../../../vulkan-docs/src/chapters/features.adoc#L266-L271) and [dual-source framebuffer blending](../../../../vulkan-docs/src/chapters/framebuffer.adoc#L178-L227) | Grounds the feature and blend-factor requirements. |

## Questions / Risk Points for User Audit

- Is the distinction between the format registration dimension and the generated blend-state behavioral axis clear?
- Should the final page list the complete format set, or is the source-linked range plus representative values sufficient?
- Is the attachment-0 comparison with `reusedColor = 2` clear enough to explain why the two draws use different push-constant arrangements?
- Does the page need a second shader walkthrough for the generic fragment shader, or is the dual-source fragment shader plus the variation table sufficient?

## Conversion Notes for Final Wiki Rewrite

- Keep the final page centered on the per-format test family and the generated blend-state axis, not on the source class layout.
- Use the registration tree at the `multi_attachments` test family and list the format leaves in the parameter section rather than expanding every leaf in the tree.
- Distill the dual-source explanation into a short Background Knowledge section.
- Use the dual-source fragment shader as the representative walkthrough. Mention the fixed common vertex shader and generic fragment shader in `Additional Info` and the variation summary.
- Copy the failure mapping table above into `## Failure Meaning` and write cause analysis fresh.
- Preserve the distinction between a quality warning for an all-zero destination and an actual comparison failure.
