# Understanding Brief: Multisampled Render to Single Sampled

## One-Sentence Test Purpose

This test checks whether a Vulkan implementation can render multisample data into single-sampled attachments created with `VK_IMAGE_CREATE_MULTISAMPLED_RENDER_TO_SINGLE_SAMPLED_BIT_EXT` and resolve color, depth, and stencil results correctly.

## Background Knowledge

### Multisampled render to single-sampled attachments

`VK_EXT_multisampled_render_to_single_sampled` lets a render pass use a single-sampled framebuffer attachment while the implementation evaluates fragments at multiple sample locations. The image remains single-sampled from the application's resource perspective, so the feature changes the render target's internal rendering behavior rather than requiring a separate multisampled image and explicit resolve image.

Why it matters here:
- The test compares the extension path with the expected multisample and resolve semantics.
- The render-pass and dynamic-rendering paths must carry the same sample-count and resolve-mode contract.

### Resolve behavior

A resolve mode selects how multiple sample values become one stored value. `VK_RESOLVE_MODE_SAMPLE_ZERO_BIT` selects sample zero, while modes such as `VK_RESOLVE_MODE_MAX_BIT` select a value according to the attachment's resolve rules. Color, depth, and stencil have different value types and comparison rules.

Why it matters here:
- The generated fragment shader gives samples distinct values, making the selected resolve behavior observable.
- The verification path must distinguish floating-point tolerance from exact integer and stencil comparisons.

## One Concrete Example

A representative `basic` case uses a 2D color or depth/stencil attachment with 2, 4, 8, or 16 samples, a selected resolve mode, and either a whole-framebuffer or partial render area. The fragment shader branches on `gl_SampleID` and writes a distinct gradient to floating-point color attachments, distinct integer vectors to an integer attachment, and a sample-dependent depth value. A compute shader reads the resulting single-sampled views and checks the expected resolved values.

## End-to-End Test Flow

```text
[host] choose formats, sample count, resolve mode, render area, attachment type, and pipeline construction type
[host] create single-sampled images with the MSRTSS image-create flag when the extension path is enabled
[host] create views, render-pass or dynamic-rendering state, graphics pipelines, descriptors, and verification buffers
[host] compile generated vertex, fragment, and compute GLSL programs
[host] clear or initialize attachments, then submit fullscreen-triangle rendering and any subpass or render-pass sequence
[device] execute the fragment shader at the configured sample count and store the implementation's resolved attachment values
[device] run compute verification over the rendered area and, for partial renders, over pixels outside that area
[host] wait for completion, apply the shader-write-to-host-read barrier, read verification counters, and inspect the verification image
[host] pass when the expected color, depth, stencil, clear, input-attachment, query, or garbage-attachment condition holds
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `initBasicPrograms` generates a vertex shader, a `gl_SampleID`-based fragment shader, and compute verification shaders. The fragment shader encodes different expected values per sample; the compute programs compare the resolved images.
- Pipeline state is generated for both traditional render passes and `VK_KHR_dynamic_rendering`. The same test generator can configure multiple subpasses, multiple render passes, input-attachment use, clear behavior, and garbage color attachments.
- The test registers the `multisampled_render_to_single_sampled` family for the extension path and a parallel `misc` family for the ordinary multisample control path. Both families contain a `dynamic_rendering` intermediate node.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|---|---|---|---|---|---|
| Color and depth/stencil images | yes | yes | rendered and sampled | indirectly | Carry the MSRTSS result and resolve inputs |
| Resolve images/views | yes when the relevant attachment is multisampled | yes | sampled by verification | indirectly | Expose the resolved value to the compute checker |
| Vertex buffer | yes | yes | read by graphics | no | Supplies the fullscreen triangle |
| `verificationBuffer` | yes | yes | written by compute | yes | Stores per-attachment match counters |
| `verify` image | yes | yes | written by compute | inspected as diagnostics | Marks matching pixels green and mismatches red |
| Descriptor set and pipeline layouts | yes | yes | consumed by compute | no | Bind result buffers and attachment views for verification |

## What Is Checked

- Basic rendering checks expected floating-point gradients with a tolerance, integer colors with exact or bounded comparisons, depth within `0.01`, and stencil with exact comparison.
- The sample-dependent data makes `SAMPLE_ZERO` and `MAX` resolve modes distinguishable.
- Partial render cases verify that pixels outside the render area keep their initialized values.
- `clear_attachments` checks `vkCmdClearAttachments` behavior. `multi_subpass` and `multi_renderpass` check state across pass boundaries. `input_attachments` checks later access to rendered data as input attachments.
- `subpass_resolve_efficiency_query` checks the query result when the extension, monolithic construction, and render-pass requirements permit it.
- Dynamic-rendering cases exercise the same behaviors with dynamic state. Non-monolithic dynamic-rendering cases also test garbage color attachments.

## Behavior Parameter Identification

> **Behavior parameter:** intermediate node under `pipeline.monolithic.multisample.multisampled_render_to_single_sampled`
>
> **Candidate values:** `basic`, `clear_attachments`, `multi_subpass`, `multi_renderpass`, `input_attachments`, `subpass_resolve_efficiency_query`, `dynamic_rendering`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `basic` | MSRTSS image creation, multisample evaluation, resolve selection, attachment setup, or result verification |
| `clear_attachments` | Clear command handling, clear/load interaction, attachment state, or result verification |
| `multi_subpass` | Subpass dependency, attachment transition, input/resolve state, or multisample handling across subpasses |
| `multi_renderpass` | Resource lifetime, layout transition, synchronization, or MSRTSS state across render passes |
| `input_attachments` | Input-attachment visibility, subpass ordering, resolve state, or attachment format handling |
| `subpass_resolve_efficiency_query` | Resolve-efficiency query support or reported query value |
| `dynamic_rendering` | Dynamic-rendering attachment state, MSRTSS state, resolve behavior, or garbage-attachment handling |

## Important Variations and Special Cases

- The extension family is conditional on `VK_EXT_multisampled_render_to_single_sampled`; the `misc` family uses the same implementation machinery with `isMultisampledRenderToSingleSampled` set to false.
- Shader objects can only use the dynamic-rendering path, so non-dynamic groups are omitted for shader-object construction types.
- `multi_subpass` requires a render pass. Input-attachment cases do not use dynamic rendering or shader objects.
- Formats cover floating-point color, integer color, depth-only, stencil-only, and combined depth/stencil cases. The source also includes Android Hardware Buffer color and depth/stencil memory variants.
- The source permits sample counts up to 16. The registered mustpass files cover 4,288 leaves each for monolithic and fast-linked-library construction, and 1,520 leaves for unlinked shader-object SPIR-V construction.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Registration entry points | [`createMultisampledRenderToSingleSampledTests`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L6099-L6105), [`createMultisampledMiscTests`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L6107-L6111) | Defines the two root families |
| Intermediate groups | [`createMultisampledRenderToSingleSampledTestsInGroup`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L6067-L6080) | Defines `dynamic_rendering` and construction-type gating |
| Test group generation | [`createMultisampledTestsInGroup`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L5641-L6065) | Defines the seven behavior intermediates and their matrices |
| MSRTSS image creation | [`makeImage`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L440-L466) | Sets the extension image-create flag |
| Generated programs and expected values | [`initBasicPrograms`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L3007-L3250) | Makes per-sample rendering observable |
| Compute verification setup | [`setupVerifyDescriptorSetAndPipeline`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L2354-L2427) | Binds result storage and resolved views |
| Vulkan render-pass contract | [`pipelines.adoc`](../../../../vulkan-docs/src/chapters/pipelines.adoc#L3036-L3048) | Defines MSRTSS image and rendering requirements |
| Vulkan resolve operations | [`fragops.adoc`](../../../../vulkan-docs/src/chapters/fragops.adoc#L2530-L2545) | Defines multisample and resolve behavior |
| Mustpass coverage | [`monolithic.txt`](../../../../vulkancts/mustpass/main/vk-default/pipeline/monolithic/monolithic.txt), [`fast-linked-library.txt`](../../../../vulkancts/mustpass/main/vk-default/pipeline/fast-linked-library.txt), [`shader-object-unlinked-spirv.txt`](../../../../vulkancts/mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/shader-object-unlinked-spirv.txt) | Records registered executable leaves |

## Questions / Risk Points for User Audit

- Is the distinction between the extension family and the `misc` control family clear?
- Does the sample-dependent example explain why resolve modes produce different observable values?
- Is the compute verification path described at the right level without implying that it validates only color?
- Should the Android Hardware Buffer variation receive more detail in the final page?

## Conversion Notes for Final Wiki Rewrite

Use the seven direct registered children as the Level-3 page's behavior axis and keep the fenced hierarchy to one concrete monolithic path. Distill the brief's two background topics into concise prerequisites. Use the `basic` case for the representative runtime walkthrough, retain the resource table in formal form, and copy the `### Failure Cause Mapping` table byte-for-byte into the final page. Keep `misc` as a separate registered family described outside the canonical tree.
