## Overview

**Core question:** Can graphics pipeline creation safely accept a render pass that contains a color attachment and an input attachment with matching format and sample count but distinct attachment-reference layouts, both when a pipeline cache handle is supplied and when `VK_NULL_HANDLE` is supplied?

`MatchedAttachments` is a `pipeline` test family implemented by [`vktPipelineMatchedAttachmentsTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMatchedAttachmentsTests.cpp#L1). It constructs the render pass, descriptor interface, shaders, and graphics pipeline, then passes solely when pipeline creation returns. It does not issue a draw or inspect image contents.

The family has two executable test case leaves, `cache` and `no_cache`. Each is represented under three construction-root registrations in the default mustpass: `pipeline.monolithic`, `pipeline.fast_linked_library`, and `pipeline.pipeline_library`, for six leaves total.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- A render-pass subpass can consume an input attachment in a fragment shader and produce a color attachment. A [`VkAttachmentReference`](../../../../vulkan-docs/src/chapters/renderpass.adoc#render-pass-creation) identifies both the attachment index and the layout used for that subpass role.
- A graphics pipeline is compatible with the supplied render pass only when its render-pass-dependent state is accepted during creation. This test checks construction, not the results of fragment execution.
- A pipeline cache is an optional graphics-pipeline-creation input. Both leaves create a pipeline cache object, but only `cache` supplies its handle to graphics pipeline creation; `no_cache` supplies `VK_NULL_HANDLE`.

## Registration Hierarchy

```text
pipeline.monolithic.matched_attachments
├── cache
└── no_cache
```

The source receives a `PipelineConstructionType`, so equivalent `cache` and `no_cache` leaves also occur under `pipeline.fast_linked_library.matched_attachments` and `pipeline.pipeline_library.matched_attachments`. Default-mustpass coverage is two leaves in each of the three roots.

## Parameter Dimensions and Observed Values

| Parameter | Source | Values and observed role |
|---|---|---|
| `usePipelineCache` | [`MatchedAttachmentsTestParams`](../../../modules/vulkan/pipeline/vktPipelineMatchedAttachmentsTests.cpp#L46-L50) | `true` for `cache`, `false` for `no_cache`; selects a created cache or `VK_NULL_HANDLE` for `buildPipeline` |
| `pipelineConstructionType` | [`createMatchedAttachmentsTests`](../../../modules/vulkan/pipeline/vktPipelineMatchedAttachmentsTests.cpp#L254-L258) | Supplied by the parent construction-root registration; checked for support before setup |
| Color attachment | [`descs` and `color`](../../../modules/vulkan/pipeline/vktPipelineMatchedAttachmentsTests.cpp#L121-L148) | Attachment 0; `VK_FORMAT_R8G8B8A8_UNORM`, one sample, `VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL` |
| Input attachment | [`descs` and `input`](../../../modules/vulkan/pipeline/vktPipelineMatchedAttachmentsTests.cpp#L134-L153) | Attachment 1; the same format and sample count, but `VK_IMAGE_LAYOUT_GENERAL` |
| Subpass interface | [`subpassDescription`](../../../modules/vulkan/pipeline/vktPipelineMatchedAttachmentsTests.cpp#L155-L166) | One input and one color attachment at the graphics bind point |

The phrase “matched attachments” describes the matching attachment properties used in this regression setup. The two references do not alias the same attachment index: the color use is attachment 0 and the input use is attachment 1.

## Behavior Parameters

The primary behavioral axis is pipeline-cache selection. The attachment, shader, and render-pass configuration remain fixed.

### cache - pipeline creation with a cache

`cache` creates a `VkPipelineCache` and passes that handle to [`buildPipeline`](../../../modules/vulkan/pipeline/vktPipelineMatchedAttachmentsTests.cpp#L221-L232). It checks that cache-enabled creation accepts the matched input/color attachment setup.

### no_cache - pipeline creation without supplying a cache

`no_cache` uses the same setup and still creates a `VkPipelineCache`, but passes `VK_NULL_HANDLE` to `buildPipeline`. It checks the same render-pass-dependent graphics pipeline creation path without supplying the created cache.

## Shader Analysis

The shaders establish a valid interface for pipeline construction but shader execution is not the observed behavior.

[`color_vert`](../../../modules/vulkan/pipeline/vktPipelineMatchedAttachmentsTests.cpp#L62-L66) writes a constant `gl_Position`. [`color_frag`](../../../modules/vulkan/pipeline/vktPipelineMatchedAttachmentsTests.cpp#L68-L75) declares an input attachment at set 0, binding 0, reads it with `subpassLoad(x)`, and writes the value to color location 0. The test never records or submits a draw, so it neither evaluates this load on the device nor validates a color result. The relevant contract is that pipeline creation accepts the shader interface together with the render pass.

## Runtime Execution and Result Checking

1. `checkSupport` verifies requirements for the selected [`PipelineConstructionType`](../../../modules/vulkan/pipeline/vktPipelineMatchedAttachmentsTests.cpp#L52-L56).
2. `initPrograms` adds the minimal vertex and fragment GLSL programs. The fragment program requires an input-attachment descriptor at set 0, binding 0.
3. The test creates an input-attachment descriptor set layout and uses it to make the pipeline layout.
4. It defines two `VK_FORMAT_R8G8B8A8_UNORM`, single-sample attachment descriptions. Attachment 0 uses `VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL`; attachment 1 uses `VK_IMAGE_LAYOUT_GENERAL`.
5. One graphics subpass references attachment 1 as its input and attachment 0 as its color output, then a `RenderPassWrapper` is created from that description.
6. The test creates a pipeline cache, configures a `GraphicsPipelineWrapper` with the render pass and shader modules, and calls `buildPipeline` with the cache handle for `cache` or `VK_NULL_HANDLE` for `no_cache`.
7. [`testMatchedAttachments`](../../../modules/vulkan/pipeline/vktPipelineMatchedAttachmentsTests.cpp#L232-L235) immediately returns pass after that call. There is no command buffer, draw, queue submission, synchronization, or host readback.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `cache` | Setup fails while creating the pipeline cache, or graphics pipeline creation does not correctly handle the matched input/color attachment descriptions when the cache handle is supplied. |
| `no_cache` | Setup fails while creating the unused pipeline cache, or graphics pipeline creation does not correctly handle the matched input/color attachment descriptions when `VK_NULL_HANDLE` is supplied. |

### Cause Analysis

#### `cache`

**Possible failure symptoms:** Pipeline creation reports an error, throws through the CTS wrapper, hangs, or crashes only when the valid `VkPipelineCache` is passed.

**Possible implementation causes:** The implementation may mishandle the interaction between cache lookup or insertion and render-pass-dependent pipeline state, including the pair of input/color attachment references and their layouts. Because the test has no execution phase, it cannot localize the defect to fragment input-attachment reads or color writes. Source-level driver investigation is needed to distinguish cache handling from general pipeline compatibility processing.

#### `no_cache`

**Possible failure symptoms:** The leaf reports an error, throws through a CTS wrapper, hangs, or crashes before returning pass. This can happen while creating the pipeline cache object or while building the graphics pipeline with `VK_NULL_HANDLE`.

**Possible implementation causes:** The implementation may fail the unconditional pipeline-cache creation that precedes `buildPipeline`, or it may incorrectly validate or compile pipeline state derived from the render pass, the input-attachment descriptor interface, or the distinct layouts of the two attachments. A failure in both leaves can arise from shared setup, including cache-object creation, or from shared graphics-pipeline construction; it does not by itself rule out cache handling. The test does not execute the shaders, so logs or source-level driver investigation are needed to identify the failing API call and the precise validation or compilation path.

## Case Pruning

### Requirement-based pruning

The source states that input attachments are not supported with dynamic rendering, and the test requires a render pass to express its input-attachment subpass.

### Design-based pruning

[`addMatchedAttachmentsTestCasesWithFunctions`](../../../modules/vulkan/pipeline/vktPipelineMatchedAttachmentsTests.cpp#L238-L249) does not register these leaves for shader-object construction types. This is an applicability boundary, not an additional behavior variant.

## Key Takeaways

- The family tests successful graphics pipeline creation for a fixed two-attachment render-pass arrangement, not rendering correctness.
- Both leaves create a pipeline cache object; they differ only in whether its handle or `VK_NULL_HANDLE` is supplied to `buildPipeline`.
- The input and color references select different attachments with matching format and sample count but different layouts.
- A failure identifies a construction-path problem; the absence of a draw prevents attributing it to runtime input-attachment sampling or color output.

## Source Reference Appendix

| Topic | Source reference | Evidence |
|---|---|---|
| Test family registration | [`createMatchedAttachmentsTests`](../../../modules/vulkan/pipeline/vktPipelineMatchedAttachmentsTests.cpp#L254-L258) | Creates `matched_attachments` for the selected construction type |
| Parameter and support check | [`MatchedAttachmentsTestParams` and `checkSupport`](../../../modules/vulkan/pipeline/vktPipelineMatchedAttachmentsTests.cpp#L46-L56) | Defines the construction type and cache boolean, then checks construction support |
| Shader programs | [`initPrograms`](../../../modules/vulkan/pipeline/vktPipelineMatchedAttachmentsTests.cpp#L58-L76) | Defines the vertex program and input-attachment fragment program |
| Attachment and subpass setup | [`testMatchedAttachments`](../../../modules/vulkan/pipeline/vktPipelineMatchedAttachmentsTests.cpp#L121-L180) | Defines attachment descriptions, references, subpass, and render pass |
| Pipeline construction and pass condition | [`testMatchedAttachments`](../../../modules/vulkan/pipeline/vktPipelineMatchedAttachmentsTests.cpp#L197-L235) | Builds the pipeline with cache or null handle and passes on return |
| Leaf registration and pruning | [`addMatchedAttachmentsTestCasesWithFunctions`](../../../modules/vulkan/pipeline/vktPipelineMatchedAttachmentsTests.cpp#L238-L249) | Registers the two leaves and excludes shader-object construction |
| Vulkan input attachment model | [Render Pass chapter](../../../../vulkan-docs/src/chapters/renderpass.adoc#depth-stencil-and-input-attachments) | Specification discussion of depth/stencil and input attachments |
| Default mustpass roots | [`monolithic`](../../../mustpass/main/vk-default/pipeline/monolithic/monolithic.txt#L190987-L190988), [`fast-linked library`](../../../mustpass/main/vk-default/pipeline/fast-linked-library.txt#L39444-L39445), [`pipeline library`](../../../mustpass/main/vk-default/pipeline/pipeline-library.txt#L39544-L39545) | Records the six default-mustpass leaves |
