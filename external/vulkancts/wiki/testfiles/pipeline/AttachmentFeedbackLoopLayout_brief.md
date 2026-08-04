# Understanding Brief: Attachment feedback loop layout

## One-Sentence Test Purpose

This test checks whether an implementation can render to an attachment while reading the same image through a sampler, with the layout, feedback-loop state, aspect, and access pattern required by `VK_EXT_attachment_feedback_loop_layout`.

## Background Knowledge

### Attachment feedback loops

A feedback loop uses one image subresource as a rendering attachment and as a non-attachment resource during the same render pass. The extension feature enables `VK_IMAGE_LAYOUT_ATTACHMENT_FEEDBACK_LOOP_OPTIMAL_EXT` for images created with `VK_IMAGE_USAGE_ATTACHMENT_FEEDBACK_LOOP_BIT_EXT`. A pipeline must declare the relevant color or depth/stencil feedback-loop aspect, or set that information dynamically when the dynamic-state path is selected.

The layout alone does not define a safe ordering between an arbitrary read and write. This family uses controlled patterns: a read-only sample, separate read and write regions, same-pixel output, and a component-interleaving variant. The generated reference image captures the result expected for each pattern.

### Image aspects and observed output

Color, depth, and stencil are separate image aspects for this test. CTS creates views and attachment state for the selected aspect, reads the resulting image after submission, and compares it with a host-generated reference. A pixel mismatch shows that the final observation disagrees with the selected test pattern; it does not isolate a single internal stage.

## One Concrete Example

A representative leaf is `pipeline.monolithic.attachment_feedback_loop_layout.sampler.attachment_feedback_loop_optimal.sampled_image.image_type.2d.format.r8g8b8a8_unorm_color_read_write_different_areas`. It uses a 2D `VK_FORMAT_R8G8B8A8_UNORM` color image in `VK_IMAGE_LAYOUT_ATTACHMENT_FEEDBACK_LOOP_OPTIMAL_EXT`. The draw samples one part of the image and writes the sampled values to another part, then CTS copies the image back and compares it with the reference image that performs the same region mapping.

## End-to-End Test Flow

```text
[host] select the construction type, layout, descriptor type, view type, format, aspect, test mode, and feedback-loop state mode
[host] create images with attachment-feedback-loop usage, views, sampler or sampled-image descriptors, render pass resources, and a graphics pipeline
[host] initialize image contents and record layout transitions, feedback-loop state, rendering, and final transfer operations
[device] execute the draw while the selected image is both an attachment and a sampled resource
[host] submit and wait, read the checked image, generate the corresponding expected image, and compare the two
[host] run the monolithic-only no-color or separate-mip path when that registered leaf was selected; separate mips use ordinary shader-read-only and color-attachment layouts rather than a feedback-loop layout
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

`AttachmentFeedbackLoopLayoutSamplerTest::initPrograms` generates a pass-through vertex shader and fragment shaders matched to color, depth, or stencil sampling. The shader algorithm is deliberately small: it samples the selected image and writes the value, or writes the selected components for the interleaving mode. `noColorAttachmentPrograms` generates the storage-buffer atomic path used by `no_color_draw`. `feedbackLoopDiffMipsInitPrograms` generates the shaders for the separate-mip cases.

### Bound resources and memory objects

| Resource | Created/configured by host? | Used by device? | Read back by host? | Why it matters |
|---|---|---|---|---|
| Feedback-loop image and image view | yes | attachment and sampled image | yes for sampler leaves | The same image supplies both roles under the chosen layout. |
| Descriptor set and sampler or sampled image | yes | fragment-stage sampling | no | It gives the shader its non-attachment view of the image. |
| Graphics pipeline and dynamic feedback-loop state | yes | draw setup | no | They declare the color or depth/stencil aspect allowed for feedback access. |
| Host-generated reference texture | yes | no | yes | CTS compares it with the copied image. |
| Storage buffer | yes | atomic increment in `no_color_draw` | yes | It makes a no-color-attachment draw observable. |

## What Is Checked

Sampler leaves submit a draw, read back the image, and use threshold comparison against a host-generated expected texture. Color images use `tcu::floatThresholdCompare` or `tcu::intThresholdCompare`; depth and stencil paths use aspect-specific comparisons. `no_color_draw` checks two copied color images as well as the atomic counter. `separate_mip_levels` and `separate_mip_levels_large_fb` use distinct mip subresources with ordinary shader-read-only and color-attachment layouts, then compare the copied result with a color threshold of `0.005` and alpha threshold `0.0`.

## Behavior Parameter Identification

> **Behavior parameter:** feedback-loop access pattern
>
> **Candidate values:** sampled read-only access, same-pixel read/write, different-area read/write, same-pixel component interleaving, no-color draw, and separate mip levels.

Layout selection, descriptor type, image view type, format, aspect, and pipeline construction type expand coverage around that access pattern. They do not replace it as the behavior the test observes.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| Sampled read-only access | Attachment-feedback-loop layout, descriptor sampling, aspect selection, or image readback produces values different from the initialized image. |
| Same-pixel read/write or component interleaving | Feedback-loop enable state, same-pixel sampling, fragment output, or component preservation produces a result different from the generated reference. |
| Different-area read/write | Coordinate mapping or attachment feedback access reads from or writes to the wrong region. |
| No-color draw | The empty-framebuffer draw produces the wrong atomic count, or either surrounding color-image comparison fails. |
| Separate mip levels | Image-view subresource selection, ordinary per-mip layout handling, sampling, rasterization, or image copyback produces the wrong mip-level result. |

## Important Variations and Special Cases

The `sampler` family contains `attachment_feedback_loop_optimal` and `general` layout groups, `combined_image_sampler` and `sampled_image` descriptor groups, nine image-view types, color/depth/stencil formats, and static or dynamic feedback-loop state variants. The source registers `misc` under the family root only for monolithic construction. It also registers a maintenance5 sub-group under each sampler layout only for monolithic construction.

The current pipeline mustpass files contain 2,383 monolithic leaves, 2,376 leaves each for fast-linked-library and pipeline-library, and 1,584 leaves in each shader-object mustpass file. The counts use the literal `.attachment_feedback_loop_layout.` path segment.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Family entry point | [`createAttachmentFeedbackLoopLayoutTests`](../../../modules/vulkan/pipeline/vktPipelineAttachmentFeedbackLoopLayoutTests.cpp#L3366-L3390) | Creates the family and its sampler and monolithic-only misc children. |
| Sampler matrix registration | [`createAttachmentFeedbackLoopLayoutSamplerTests`](../../../modules/vulkan/pipeline/vktPipelineAttachmentFeedbackLoopLayoutTests.cpp#L3160-L3364) | Builds layout, descriptor, image-type, format, access-pattern, and state variants. |
| Sampler setup and comparison | [`setup`, `verifyImage`, and `iterate`](../../../modules/vulkan/pipeline/vktPipelineAttachmentFeedbackLoopLayoutTests.cpp#L422-L1859) | Sets up the sampled attachment, submits the draw, reads it back, and compares it. |
| Support and generated shaders | [`checkSupport` and `initPrograms`](../../../modules/vulkan/pipeline/vktPipelineAttachmentFeedbackLoopLayoutTests.cpp#L1984-L2548) | Requires extensions and creates the selected shader path. |
| No-color path | [`noColorAttachmentSupport`, `noColorAttachmentPrograms`, and `noColorAttachmentTest`](../../../modules/vulkan/pipeline/vktPipelineAttachmentFeedbackLoopLayoutTests.cpp#L2550-L2850) | Covers feedback-loop state with a storage-buffer observation. |
| Separate-mip path | [`feedbackLoopDiffMipsInitPrograms` and `feedbackLoopDiffMipsRun`](../../../modules/vulkan/pipeline/vktPipelineAttachmentFeedbackLoopLayoutTests.cpp#L2852-L3158) | Covers feedback loops between different mip levels. |

## Questions / Risk Points for User Audit

- Does the page keep the access pattern as the behavioral axis instead of treating each format or pipeline construction type as a separate behavior?
- Does it make clear that a final-image mismatch can involve setup, sampling, attachment writes, transitions, or copyback?
- Does it distinguish monolithic-only `misc` and maintenance5 registrations from the cross-construction sampler matrix?

## Conversion Notes for Final Wiki Rewrite

Copy the failure-cause table unchanged into the final page. Keep shader discussion limited to its role as an observable sampling/write path, explain the host reference and comparisons, and preserve the exact registration hierarchy and source links.
