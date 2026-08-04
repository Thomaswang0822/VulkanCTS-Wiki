# Understanding Brief: Framebuffer attachment behavior

## One-Sentence Test Purpose

This test checks whether graphics rendering keeps writes within the framebuffer render area and handles attachment configurations that do not follow the ordinary one-color-output path. Some leaves deliberately omit execution or comparison of an attachment, so they do not establish preservation for every unwritten target.

## Background Knowledge

### Framebuffer extent and attachment extent

A framebuffer supplies image views to a render pass and has its own width and height. The images behind those views may be larger. A render pass instance uses a render area, and the viewport and scissor bound rasterization. Pixels outside that area must retain their cleared value when the test draws a full-screen quad.

### Color, input, and resolve attachment roles

A subpass can write a multisampled color attachment, resolve it to a single-sample attachment, and read an input attachment through `subpassLoad`. An attachment reference may also be `VK_ATTACHMENT_UNUSED`. Fragment shader output locations select color attachment slots; an attachment with no matching output remains outside the shader's writes.

### Host-visible result comparison

The tests transition rendered images for transfer, copy them to host-visible buffers, and compare the copies with generated expected images. `tcu::intThresholdCompare` accepts a component difference of at most `tcu::UVec4(1)`, which accommodates format conversion while retaining an exact spatial and color expectation.

## One Concrete Example

The representative `pipeline.monolithic.framebuffer_attachment.2d_32x32_64x64` case creates a 64x64 color image but a 32x32 framebuffer, viewport, scissor, and render area. It clears the whole image to black, draws a quad whose fragment shader writes `(1.0, 0.5, 0.25, 1.0)`, copies the full image to the host, and expects the 32x32 rendered rectangle to have that color while the remaining pixels stay black.

## End-to-End Test Flow

```text
[host] select a pipeline construction type and registered case definition
[host] create attachment images, views, render pass, framebuffer, buffers, and graphics pipeline
[host] clear the relevant images and transition them to their attachment layouts
[device] begin the render pass, draw a quad, and end the render pass
[host] transition the checked images for transfer and copy them to host-visible buffers
[host] generate expected pixels and compare them, or pass after the unused-attachment path completes
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

Most rendering cases generate a vertex shader that passes through quad positions and a fragment shader with location 0 output. The multiple-attachment case generates outputs at locations 0, 1, and 2. The not-exported variant declares locations 0, 1, and 2 but writes only locations 0 and 2. The `resolve_input_same_attachment` fragment shader reads `subpassInput` at set 0, binding 0 and writes a color derived from `subpassLoad`.

The no-attachment case uses a fragment shader that writes a storage image with `imageStore`; its support check requires fragment stores and atomics, `geometryShader` or `tessellationShader` for `gl_PrimitiveID`, and sample-rate shading for its multisample form.

### Bound resources and memory objects

| Resource | Created/configured by host? | Used by device? | Read back by host? | Why it matters |
|---|---|---|---|---|
| Color attachments and multisample attachments | yes | cleared, rendered, and sometimes resolved | yes | They expose writes within and outside the render area. |
| Framebuffer and render pass | yes | define attachment roles and render extent | no | They express the attachment configuration under test. |
| Input-attachment descriptor set | yes | read by the resolve/input case | no | It binds the resolve target as `VK_DESCRIPTOR_TYPE_INPUT_ATTACHMENT`. |
| Host-visible copy buffers | yes | transfer destination | yes | CTS compares their contents with generated expected images. |
| Storage image | yes | written by the no-attachment fragment shader | yes | It supplies observable output without a color attachment. |

## What Is Checked

The size-mismatch, no-attachment, different-size, not-exported, and resolve/input paths copy results to the host and use `tcu::intThresholdCompare` with `tcu::UVec4(1)`. In the not-exported path all three targets are copied, but location 1 is deliberately skipped during comparison; only exported locations 0 and 2 are validated. The unused-attachment leaf records render-pass commands but never submits its command buffer, so it covers render-pass/framebuffer creation and command recording only, with no draw, readback, or device-execution oracle.

## Behavior Parameter Identification

> **Behavior parameter:** attachment behavior family
>
> **Candidate values:** larger-than-framebuffer attachments, no attachments, unused attachment, different attachment sizes, resolve/input same attachment, and attachments not exported by the fragment shader

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| Larger-than-framebuffer attachments | Rasterization, framebuffer extent, viewport/scissor, layer, resolve, or transfer-copy handling writes or reports pixels outside the expected render area. |
| No attachments | The implementation does not execute fragment storage-image writes correctly when the render pass has no color attachment. |
| Unused attachment | Render-pass/framebuffer creation or command recording rejects or mishandles `VK_ATTACHMENT_UNUSED`; this leaf does not submit the recorded commands. |
| Different attachment sizes | Per-attachment clears, output routing, or image copies leak values between color attachments with different extents. |
| Resolve/input same attachment | Input-attachment reads, multisample resolve, or their attachment-role pairing produces the wrong resolved image. |
| Attachments not exported by the fragment shader | One of the two exported outputs produces the wrong copied image. The test does not compare the unexported location-1 attachment, so this result cannot show whether that attachment was modified. |

## Important Variations and Special Cases

The source registers the same family under several pipeline-construction roots. Current split mustpass files contain 50 monolithic leaves, 49 leaves each for fast-linked-library and pipeline-library, 48 leaves for each linked or unlinked binary and linked SPIR-V shader-object root, and 49 leaves for unlinked-SPIR-V shader objects. `unused_attachment` is registered only for monolithic and shader-object-unlinked-SPIR-V. `resolve_input_same_attachment` is omitted for shader objects because this test path requires input attachments rather than dynamic rendering.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Test registration | [`addAttachmentTestCasesWithFunctions`](../../../modules/vulkan/pipeline/vktPipelineFramebufferAttachmentTests.cpp#L1938-L2096) | Builds every test case leaf and applies construction-type exclusions. |
| Family entry point | [`createFramebufferAttachmentTests`](../../../modules/vulkan/pipeline/vktPipelineFramebufferAttachmentTests.cpp#L2101-L2105) | Registers `framebuffer_attachment`. |
| Larger-attachment path | [`test`](../../../modules/vulkan/pipeline/vktPipelineFramebufferAttachmentTests.cpp#L359-L655) | Clears, renders, copies, and compares a larger attachment. |
| No-attachment path | [`testNoAtt`](../../../modules/vulkan/pipeline/vktPipelineFramebufferAttachmentTests.cpp#L768-L954) | Uses storage-image output without color attachments. |
| Multiple-attachment path | [`testMultiAttachments`](../../../modules/vulkan/pipeline/vktPipelineFramebufferAttachmentTests.cpp#L1017-L1364) | Checks different-size and not-exported attachment behavior. |
| Resolve/input path | [`testInputResolveSameAttachment`](../../../modules/vulkan/pipeline/vktPipelineFramebufferAttachmentTests.cpp#L1478-L1752) | Exercises input attachment and resolve target pairing. |
| Unused-attachment path | [`testUnusedAtt`](../../../modules/vulkan/pipeline/vktPipelineFramebufferAttachmentTests.cpp#L1754-L1783) | Completes a render pass with `VK_ATTACHMENT_UNUSED`. |

## Questions / Risk Points for User Audit

- Does the page make clear that the behavioral axis is the attachment behavior family rather than the pipeline-construction root?
- Does the distinction between host pixel comparison and the pass-by-completion unused-attachment path remain clear?
- Are the shader-object exclusions and split mustpass counts stated without treating all construction roots as equivalent?

## Conversion Notes for Final Wiki Rewrite

Turn this brief into an explanation-first Level-3 page. Preserve the exact failure-cause table, explain each attachment behavior family in `## Behavior Parameters`, retain the no-attachment feature checks and construction-type pruning, and separate shader output structure from host-side image validation.
