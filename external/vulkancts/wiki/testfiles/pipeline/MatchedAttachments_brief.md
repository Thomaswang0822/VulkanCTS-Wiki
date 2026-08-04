# Understanding Brief: Matched attachments pipeline construction

## One-Sentence Test Purpose

This test checks whether graphics pipeline creation correctly handles a render pass whose input and color attachments refer to different attachments with matching format and sample count but different layouts.

## Background Knowledge

### Input and color attachments

A subpass can read an input attachment through a fragment shader while writing a color attachment. Each use is described by a `VkAttachmentReference`, which identifies an attachment and the layout used for that subpass use. The references may select different attachments even when those attachments otherwise have matching descriptions.

Why it matters here:
- The fragment shader uses an input attachment at set 0, binding 0 and reads it with `subpassLoad`.
- The render pass binds attachment 1 as the input attachment and attachment 0 as the color attachment, with `VK_IMAGE_LAYOUT_GENERAL` and `VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL`, respectively.
- The test targets pipeline construction and does not render or compare pixels.

### Pipeline cache selection

A pipeline cache is an optional input to graphics pipeline creation. Both leaves create a `VkPipelineCache`; they keep the render-pass and shader setup constant while selecting whether `buildPipeline` receives that valid handle or `VK_NULL_HANDLE`.

## One Concrete Example

The representative setup creates two `VK_FORMAT_R8G8B8A8_UNORM` single-sample attachments. The color reference selects attachment 0 in `VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL`; the input reference selects attachment 1 in `VK_IMAGE_LAYOUT_GENERAL`. The fragment shader declares `layout(input_attachment_index=0, set=0, binding=0) uniform subpassInput x;` and assigns `subpassLoad(x)` to the color output.

The `cache` test passes the created pipeline cache to `buildPipeline`; `no_cache` passes `VK_NULL_HANDLE`.

## End-to-End Test Flow

```text
[host] select a supported pipeline construction type and the cache variant
[host] create the input-attachment descriptor set layout and pipeline layout
[host] compile the minimal vertex and fragment GLSL programs
[host] create a render pass with two matching-format attachments and one subpass
[host] configure graphics pipeline state and call buildPipeline
[host] return pass if pipeline creation completes without throwing or crashing
```

The source excludes shader-object construction types because input attachments are not supported with dynamic rendering in this test path.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The test generates two inline GLSL programs: `color_vert` writes `gl_Position = vec4(1)`, and `color_frag` reads the input attachment with `subpassLoad` and writes location 0. No generated SPIR-V is documented separately; the CTS program collection compiles these sources for pipeline creation.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|---|---|---|---|---|---|
| Two render-pass attachment descriptions | yes | through render pass | would define input/color uses | no | They provide the matched attachment pair and distinct layouts |
| Input-attachment descriptor set layout | yes | pipeline layout | referenced by fragment shader interface | no | It declares set 0, binding 0 as `VK_DESCRIPTOR_TYPE_INPUT_ATTACHMENT` |
| Render pass and subpass | yes | graphics pipeline | describes one input and one color attachment reference | no | It is the behavior under pipeline construction |
| Pipeline cache | yes for both leaves | passed to pipeline creation only for `cache` | no shader access | no | The handle supplied to `buildPipeline`, not cache-object creation, distinguishes the leaves. |

## What Is Checked

The callback returns `tcu::TestStatus::pass("Pass")` after `buildPipeline` returns. There is no draw, submission, synchronization, image readback, or pixel comparison. A failure therefore indicates an exception, validation failure, device error, or implementation crash during setup or graphics pipeline creation rather than a wrong rendered value.

## Behavior Parameter Identification

> **Behavior parameter:** pipeline-cache selection
>
> **Candidate values:** `cache`, `no_cache`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `cache` | Setup fails while creating the pipeline cache, or graphics pipeline creation does not correctly handle the matched input/color attachment descriptions when the cache handle is supplied. |
| `no_cache` | Setup fails while creating the unused pipeline cache, or graphics pipeline creation does not correctly handle the matched input/color attachment descriptions when `VK_NULL_HANDLE` is supplied. |

## Important Variations and Special Cases

The same two leaves are registered under the supported pipeline construction roots used by the mustpass files, including `pipeline.monolithic`, `pipeline.fast_linked_library`, and `pipeline.pipeline_library`. The source-level helper accepts a construction type, but all leaves retain the same attachment and shader arrangement. Shader-object variants are pruned because the input-attachment path depends on a render pass and is not supported with dynamic rendering here.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Test registration | [`createMatchedAttachmentsTests`](../../../modules/vulkan/pipeline/vktPipelineMatchedAttachmentsTests.cpp#L254-L258) | Registers the `matched_attachments` test family |
| Attachment and subpass setup | [`testMatchedAttachments`](../../../modules/vulkan/pipeline/vktPipelineMatchedAttachmentsTests.cpp#L121-L180) | Defines the two matching attachments and their different layouts |
| Shader programs | [`initPrograms`](../../../modules/vulkan/pipeline/vktPipelineMatchedAttachmentsTests.cpp#L58-L76) | Defines the input-attachment fragment shader |
| Cache split and pruning | [`addMatchedAttachmentsTestCasesWithFunctions`](../../../modules/vulkan/pipeline/vktPipelineMatchedAttachmentsTests.cpp#L238-L249) | Registers `cache` and `no_cache` and excludes shader objects |
| Vulkan input attachments | [Render Pass - Depth/Stencil and Input Attachments](../../../../vulkan-docs/src/chapters/renderpass.adoc#depth-stencil-and-input-attachments) | Describes the input-attachment render-pass model |

## Questions / Risk Points for User Audit

- Is the distinction between matching attachment descriptions and different attachment-reference layouts clear?
- Is the absence of execution and pixel validation explicit enough?
- Should the page enumerate additional construction roots beyond those present in the current mustpass files?

## Conversion Notes for Final Wiki Rewrite

Distill the brief into an explanation-first Level-3 page. Keep the attachment pair and two cache leaves as the representative example, preserve the exact `### Failure Cause Mapping` table, and explain that the observable result is successful pipeline creation rather than rendered output. Keep the source links and the shader-object pruning rule.
