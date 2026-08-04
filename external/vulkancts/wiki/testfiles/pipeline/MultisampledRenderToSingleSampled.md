## Overview

**Core question:** Does `VK_EXT_multisampled_render_to_single_sampled` produce the expected single-sampled color, depth, and stencil results when the implementation renders with multiple samples?

This test family documents `pipeline.monolithic.multisample.multisampled_render_to_single_sampled`. Its direct children are intermediate nodes that select a rendering scenario: basic rendering, clears, pass sequencing, input attachments, a query, or dynamic rendering. The same source also registers the parallel `pipeline.monolithic.multisample.misc` test family, which uses the shared machinery without enabling the extension path.

For rendering cases, the implementation creates single-sampled images with `VK_IMAGE_CREATE_MULTISAMPLED_RENDER_TO_SINGLE_SAMPLED_BIT_EXT` when `isMultisampledRenderToSingleSampled` is enabled. It renders sample-distinct values, exposes the single-sampled result through image views, and uses compute shaders plus host readback to determine pass or fail. The query subgroup is an exception: it only validates the value returned through a chained format-properties query.

The default mustpass scope contains 4,288 leaves under the monolithic root, 4,288 under `pipeline.fast_linked_library`, and 1,520 under `pipeline.shader_object_unlinked_spirv`. Each count uses the literal `multisampled_render_to_single_sampled` path component in the corresponding file.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- Multisampled render to single-sampled rendering changes attachment rendering behavior while the application owns a single-sampled image. The image requires `VK_IMAGE_CREATE_MULTISAMPLED_RENDER_TO_SINGLE_SAMPLED_BIT_EXT`; the render pass or dynamic-rendering state supplies the multisample information. See [the Vulkan pipeline requirements](../../../../vulkan-docs/src/chapters/pipelines.adoc#L3036-L3048).
- A resolve mode selects one single-sampled value from multiple samples. The generated shaders make sample values differ, so `VK_RESOLVE_MODE_SAMPLE_ZERO_BIT` and modes such as `VK_RESOLVE_MODE_MAX_BIT` can be observed through the resulting attachment. See [multisample and resolve operations](../../../../vulkan-docs/src/chapters/fragops.adoc#L2530-L2545).
- Color, depth, and stencil results use different representations. The checker therefore uses floating-point tolerances where required and exact comparisons for integer and stencil values.

## Registration Hierarchy

```text
pipeline.monolithic.multisample.multisampled_render_to_single_sampled
├── basic
├── clear_attachments
├── multi_subpass
├── multi_renderpass
├── input_attachments
├── subpass_resolve_efficiency_query
└── dynamic_rendering
```

[`createMultisampledRenderToSingleSampledTests`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L6099-L6105) supplies this test family. [`createMultisampledRenderToSingleSampledTestsInGroup`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L6067-L6080) omits the non-dynamic path for shader-object construction types, because shader objects require dynamic rendering. The separate [`createMultisampledMiscTests`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L6107-L6111) registers `pipeline.monolithic.multisample.misc`; it is a separate test family and does not appear in this canonical tree.

## Parameter Dimensions and Observed Values

| Dimension | Representative values | Observed effect |
|---|---|---|
| Color and depth/stencil formats | floating-point color, signed or unsigned integer color, depth-only, stencil-only, combined depth/stencil | Selects attachment views and the appropriate verification comparison |
| Sample count | 2, 4, 8, 16 | Selects the number of sample-distinct fragment outputs |
| Resolve mode | `VK_RESOLVE_MODE_SAMPLE_ZERO_BIT`, `VK_RESOLVE_MODE_MAX_BIT` | Selects the expected depth/stencil resolve value; color resolve behavior is fixed by the attachment setup |
| Render area | whole framebuffer or partial area | Partial cases also verify pixels outside the rendered area |
| Attachment memory | default, Android Hardware Buffer color, Android Hardware Buffer depth/stencil | Exercises allocation and image binding variants |
| Pipeline construction type | monolithic, fast linked library, shader-object variants | Changes registered paths and restricts shader-object cases to dynamic rendering |
| Rendering form | render pass or dynamic rendering | Changes attachment setup while retaining the target behavior |
| Input attachment form | color, depth, or stencil input types | Selects the later attachment access scenario |

The generator initializes `TestParams` with attachment formats, sample counts, clear values, per-pass configuration, render-area state, memory type, and the construction type. [`makeImage`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L440-L466) applies the MSRTSS image-create flag only when the image is single-sampled and the extension path is enabled. AHB memory variants are generated by `basic`; the other generated scenarios use the default image-memory path.

## Behavior Parameters

The primary behavioral axis is the direct intermediate node under `pipeline.monolithic.multisample.multisampled_render_to_single_sampled`.

### basic: Sample-distinct rendering and resolve

The generator draws a fullscreen triangle and uses sample-dependent floating-point and integer color outputs plus sample-dependent depth. Stencil is checked when present, but this basic fragment shader does not write a per-sample stencil output; the expected stencil value comes from the test's stencil setup. It verifies that the resulting attachments match the selected sample count and depth/stencil resolve mode.

### clear_attachments: Clears in an MSRTSS attachment setup

The test calls `vkCmdClearAttachments` in the configured rendering path, then verifies the affected attachment values.

### multi_subpass: MSRTSS across subpasses

The test uses one render pass with multiple subpasses. It checks attachment state and results across subpass boundaries. This intermediate node requires render-pass rendering.

### multi_renderpass: MSRTSS across rendering sequences

The test distributes work over multiple rendering sequences, checking that attachment contents and transitions remain valid between passes. The non-dynamic form uses multiple render-pass instances; the dynamic form uses multiple dynamic-rendering instances.

### input_attachments: Read rendered values as input attachments

The test renders multisampled data, then accesses it through input attachments. Dynamic rendering and shader objects do not cover this intermediate node.

### subpass_resolve_efficiency_query: Resolve query reporting

This path runs only for the extension path, monolithic construction, and non-dynamic render-pass construction. For each format in the generated attachment-format ranges, it chains `VkSubpassResolvePerformanceQueryEXT` to `vkGetPhysicalDeviceFormatProperties2` and checks that `optimal` is populated with a valid Vulkan boolean.

### dynamic_rendering: MSRTSS without a render-pass object

This path repeats supported scenarios with dynamic-rendering attachment state. Non-monolithic construction types add `garbage_color_attachment`, which probes dynamic attachment handling when a color attachment contains deliberately unusable data.

## Shader Analysis

The shaders are generated by [`initBasicPrograms`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L3007-L3250), so this page does not preserve a static GLSL or SPIR-V artifact. The relevant behavior is in the generated source:

1. The vertex shader passes fullscreen-triangle positions through unchanged.
2. The fragment shader branches on `gl_SampleID`. For each sample it writes a different floating-point gradient, integer vector, and depth value. The source chooses values so sample zero and maximum resolve modes produce different results.
3. A compute verification shader samples the resolved color, depth, and stencil views. It increments `VerificationResults` counters for matching pixels and writes a red or green diagnostic value to the `verify` image.

The shader code does not itself create the MSRTSS mode. Pipeline and attachment state establish that mode; the shaders make incorrect sample count or resolve behavior visible.

## Runtime Execution and Result Checking

1. The host selects a format matrix, sample count, resolve mode, rendering form, memory type, and pipeline construction type. It skips unsupported feature combinations through the test requirements.
2. The host creates color and depth/stencil images, optional resolve images, views, a vertex buffer, verification buffer, diagnostic image, graphics pipeline, and compute pipeline. For the extension path, the relevant single-sampled image receives `VK_IMAGE_CREATE_MULTISAMPLED_RENDER_TO_SINGLE_SAMPLED_BIT_EXT`.
3. The host records attachment clears or initialization, graphics rendering, and any required subpass, render-pass, input-attachment, or dynamic-rendering sequence.
4. For rendering cases, the device runs the fragment shader at the configured sample count and produces the attachment result according to the configured state. In the MSRTSS path the target image itself is single-sampled and carries the extension image-create flag; ordinary `misc` cases use the normal multisample/resolve control path.
5. The host binds the result views to the compute checker through [`setupVerifyDescriptorSetAndPipeline`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L2354-L2427). The compute dispatch compares attachment values over the target area. Partial-area helpers separately check that untouched pixels retain their expected values.
6. [`postVerifyBarrier`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L2429-L2447) makes compute writes available for host reads. The host submits, waits, reads `verificationBuffer`, and logs the diagnostic `verify` image on failure.

## Failure Meaning

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

### Cause Analysis

#### `basic`

**Possible failure symptoms:** The computed counters show mismatching color, depth, stencil, or integer pixels. The diagnostic image marks those pixels red.

**Possible implementation causes:** Investigate creation of the single-sampled MSRTSS image, attachment sample state, fragment sample evaluation, resolve-mode selection, format conversion, and the transition to shader-readable layouts. The final resolved image localizes the failure to this rendering-and-observation path, but cannot isolate one pipeline stage without a smaller reproducer.

#### `clear_attachments`

**Possible failure symptoms:** A cleared attachment differs from the configured clear value while adjacent rendering scenarios pass.

**Possible implementation causes:** Investigate `vkCmdClearAttachments` execution, attachment layout and load/clear state, aspect selection, and interaction between the clear and MSRTSS attachment setup. Source-level tracing is needed to distinguish command processing from later verification.

#### `multi_subpass`

**Possible failure symptoms:** Results diverge only when the sequence crosses subpass boundaries.

**Possible implementation causes:** Investigate subpass dependencies, attachment references, layout transitions, visibility to subsequent subpasses, and preservation of the MSRTSS state. This intermediate node combines several attachment operations, so its image result does not identify an exclusive cause.

#### `multi_renderpass`

**Possible failure symptoms:** An earlier rendering sequence appears correct but a later sequence mismatches.

**Possible implementation causes:** Investigate image layout transitions, synchronization and visibility between rendering sequences, attachment lifetime, and restoration of the required multisample state for the next sequence. The relevant sequence is a render-pass instance in the non-dynamic form and a dynamic-rendering instance in the dynamic form.

#### `input_attachments`

**Possible failure symptoms:** Rendering succeeds, but values read through input attachments fail the later comparison.

**Possible implementation causes:** Investigate input-attachment descriptors and references, subpass ordering, depth/stencil aspect selection, shader-readable layout state, and resolve behavior before the input read.

#### `subpass_resolve_efficiency_query`

**Possible failure symptoms:** The query is unavailable despite the case's feature conditions, or its `optimal` field is not populated with a valid boolean value.

**Possible implementation causes:** Investigate the `VkSubpassResolvePerformanceQueryEXT` format-property query and the extension-specific capability path. This intermediate node does not render or compare attachment pixels: it only checks that the queried `optimal` field is populated as `VK_TRUE` or `VK_FALSE`.

#### `dynamic_rendering`

**Possible failure symptoms:** Render-pass cases pass while equivalent dynamic-rendering cases fail, including garbage-color-attachment cases for non-monolithic construction.

**Possible implementation causes:** Investigate dynamic-rendering attachment descriptors, sample-count state, resolve configuration, image layouts, and garbage-attachment validation. Compare the recorded dynamic-rendering state with the corresponding render-pass path before attributing the failure to resolve hardware.

## Case Pruning

- The family requires `VK_EXT_multisampled_render_to_single_sampled` for the extension path.
- Shader-object construction types register only dynamic-rendering cases.
- `multi_subpass` requires render-pass rendering; `subpass_resolve_efficiency_query` is also restricted to the non-dynamic render-pass construction path.
- `input_attachments` excludes dynamic rendering and shader objects.
- `subpass_resolve_efficiency_query` further requires the extension path and monolithic pipeline construction.
- `garbage_color_attachment` is registered only inside `dynamic_rendering` for non-monolithic construction types.
- Format, resolve-mode, sample-count, and Android Hardware Buffer cases are pruned by support checks and test requirements.

## Key Takeaways

- This test family checks MSRTSS rendering through observable single-sampled attachment data, not merely successful pipeline creation.
- `basic` provides the central signal: sample-distinct shader values make sample count and resolve choice externally visible.
- The remaining intermediate nodes extend the same core behavior across clears, pass boundaries, input attachment reads, query reporting, and dynamic rendering.
- The `misc` family shares implementation code but remains a separate test family because it exercises the ordinary multisample control configuration.

## Source Reference Appendix

| Topic | Source |
|---|---|
| Main implementation | [`vktPipelineMultisampledRenderToSingleSampledTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L1) |
| Test parameter model | [`TestParams`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L174-L300) |
| MSRTSS image creation | [`makeImage`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L440-L466) |
| Generated basic shaders | [`initBasicPrograms`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L3007-L3250) |
| Group generation | [`createMultisampledTestsInGroup`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L5641-L6065) |
| Extension-family registration | [`createMultisampledRenderToSingleSampledTests`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L6099-L6105) |
| Control-family registration | [`createMultisampledMiscTests`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L6107-L6111) |
| Vulkan MSRTSS requirements | [`pipelines.adoc`](../../../../vulkan-docs/src/chapters/pipelines.adoc#L3036-L3048) |
| Vulkan multisample and resolve rules | [`fragops.adoc`](../../../../vulkan-docs/src/chapters/fragops.adoc#L2530-L2545) |
| Monolithic mustpass coverage | [`monolithic.txt`](../../../../vulkancts/mustpass/main/vk-default/pipeline/monolithic/monolithic.txt) |
| Fast-linked-library mustpass coverage | [`fast-linked-library.txt`](../../../../vulkancts/mustpass/main/vk-default/pipeline/fast-linked-library.txt) |
| Unlinked shader-object mustpass coverage | [`shader-object-unlinked-spirv.txt`](../../../../vulkancts/mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/shader-object-unlinked-spirv.txt) |
