# Understanding Brief: MultisampleResolveRenderArea

## One-Sentence Test Purpose

This test checks whether a render-pass multisample resolve preserves the first full-frame result outside a later, smaller render area while resolving the later clear and draw inside that area.

## Background Knowledge

### Render areas and resolve attachments

A render pass affects its `renderArea`, subject to the render-pass rules in [the Vulkan render-pass chapter](../../../../vulkan-docs/src/chapters/renderpass.adoc#renderpass). A color resolve attachment receives the single-sample result of a multisample color attachment. In this test the multisample color attachment is attachment 0 and the distinct single-sample resolve attachment is attachment 1 in [`makeRenderPass`](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveRenderAreaTests.cpp#L104-L177).

The first render pass clears both attachments across the 32 by 32 framebuffer. The second pass uses a centered 16 by 16 render area. Its clear and yellow shape should affect only that smaller area. Pixels outside it should retain the first pass's red result after resolve.

### Multisampling at a boundary

Multisampling stores several coverage samples for a pixel. A primitive whose edge is close to the render-area boundary can expose errors where an implementation applies coverage or resolve writes beyond the legal area. The rectangle, diamond, and parallelogram give the test different edge shapes while the resolve attachment supplies the host-visible result.

## One Concrete Example

The leaf `pipeline.monolithic.multisample.resolve.renderpass_renderarea.diamond_samples_4` creates a 32 by 32 four-sample color attachment and a separate one-sample resolve attachment. CTS first clears the full framebuffer red. It then begins a second render pass with the centered 16 by 16 render area, clears that area green, and draws a yellow diamond. The host reads the resolve attachment: the center must be yellow, an uncovered point inside the smaller area must be green, and every pixel outside the smaller area must remain red.

## End-to-End Test Flow

```text
[host] select a shape and sample count, then check image-format and pipeline-construction support
[host] create multisample and single-sample color images, render passes, framebuffers, shaders, a pipeline, and a readback buffer
[device] clear both attachments red through a full-frame render pass
[device] begin a second render pass with the centered 16 by 16 render area, clear it green, and draw the yellow shape
[device] resolve the multisample attachment to the single-sample attachment and copy that image to the readback buffer
[host] wait, invalidate the host allocation, inspect the center, an interior uncovered pixel where applicable, and all pixels outside the smaller area
[host] report pass only when each checked color matches its expected value
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

[`initPrograms`](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveRenderAreaTests.cpp#L477-L517) generates a pass-through vertex shader and a fragment shader that writes constant yellow `vec4(1.0, 1.0, 0.0, 1.0)`. The shader does not calculate resolve values. Fixed-function rasterization, render-pass clears, and the resolve attachment create the observation.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Multisample color image and view | yes | yes | written as color attachment | no | Holds the source samples. |
| Single-sample resolve image and view | yes | yes | written as resolve attachment and copied | yes, through the buffer | Holds the resolved result. |
| Vertex buffer | yes | yes | read by the draw | no | Defines the chosen shape. |
| Readback buffer | yes | yes | written by image-to-buffer copy | yes | Supplies resolved pixels for validation. |
| Render passes and framebuffer | yes | yes | configure attachment roles and render areas | no | Keep the two attachments distinct and route the resolve. |

## What Is Checked

The host checks three observations in [`iterate`](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveRenderAreaTests.cpp#L440-L473):

- The framebuffer center must be yellow, proving that the draw and resolve reached the expected covered point.
- For `diamond` and `parallelogram`, a selected uncovered point inside the second render area must be green. `rectangle` covers that point, so the source deliberately skips this check for that shape.
- Every pixel outside the centered 16 by 16 render area must remain red. This scan detects clear, rasterization, multisample, or resolve writes that escape the second pass's render area.

## Behavior Parameter Identification

> **Behavior parameter:** shape test case group
>
> **Candidate values:** `rectangle`, `diamond`, `parallelogram`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `rectangle` | Restricted render-area clear, rasterization, resolve, or outside-area preservation is incorrect for the fully covered shape. |
| `diamond` | Edge coverage or preservation outside the render area is incorrect; the interior uncovered-point check can also fail. |
| `parallelogram` | Slanted-edge coverage, render-area clipping, resolve, or outside-area preservation is incorrect. |

## Important Variations and Special Cases

- Sample-count leaves are `samples_2`, `samples_4`, `samples_8`, and `samples_16`; each shape has all four leaves.
- The fixed framebuffer is 32 by 32 and the second pass uses a centered 16 by 16 render area.
- The literal `.multisample.resolve.renderpass_renderarea.` segment has 12 leaves in each of seven pipeline mustpass files: `monolithic`, `fast-linked-library`, `pipeline-library`, four shader-object files. That is 84 registered mustpass leaves.
- This family is independent of `m10_resolve`; its source registers `resolve.renderpass_renderarea` directly.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Attachment and resolve setup | [`makeRenderPass`](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveRenderAreaTests.cpp#L104-L177) | Creates separate multisample color and resolve attachments. |
| Pipeline setup | [`preparePipelineWrapper`](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveRenderAreaTests.cpp#L179-L210) | Selects the requested multisample count. |
| Two-pass execution and checks | [`MultisampleRenderAreaTestInstance::iterate`](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveRenderAreaTests.cpp#L212-L473) | Records passes, copies the result, and validates colors. |
| Shader generation | [`MultisampleRenderAreaTest::initPrograms`](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveRenderAreaTests.cpp#L477-L517) | Generates pass-through and constant-yellow shaders. |
| Registration | [`createMultisampleResolveRenderpassRenderAreaTests`](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveRenderAreaTests.cpp#L519-L570) | Registers shapes and sample counts. |
| Render-pass rules | [Render-pass render area and resolves](../../../../vulkan-docs/src/chapters/renderpass.adoc#renderpass) | Defines the render-area scope and resolve-attachment model. |

## Questions / Risk Points for User Audit

- Does the two-pass red, then green-and-yellow sequence make the preservation requirement clear?
- Is it clear that the multisample source and resolve destination are different attachments?
- Does the shape-based failure table distinguish edge coverage from the sample-count configuration axis?

## Conversion Notes for Final Wiki Rewrite

Keep the final page focused on the one `renderpass_renderarea` intermediate node, then use the three shape groups as the behavioral axis. Copy the failure table into `## Failure Meaning` unchanged. Retain the explicit distinction between attachment 0 and attachment 1, because the legacy page did not establish it.
