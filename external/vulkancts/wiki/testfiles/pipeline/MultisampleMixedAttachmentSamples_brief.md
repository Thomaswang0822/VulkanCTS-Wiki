# Understanding Brief: MultisampleMixedAttachmentSamples

## One-Sentence Test Purpose

This test checks whether a graphics pipeline can render and validate mixed color and depth/stencil attachment sample counts, with standard or programmable sample locations, and whether the shader built-ins remain correct for those mixed counts.

## Background Knowledge

### Mixed attachment samples

A graphics pipeline normally uses `VkPipelineMultisampleStateCreateInfo::rasterizationSamples` with attachment sample counts. The `VK_AMD_mixed_attachment_samples` and `VK_NV_framebuffer_mixed_samples` paths allow the color and depth/stencil attachments to use different counts. With AMD mixed attachment samples, `rasterizationSamples` must equal the maximum sample count of the subpass color and depth/stencil attachments. The related coverage rules define which color samples retain coverage when the counts differ. See [graphics-pipeline validation](../../../../vulkan-docs/src/chapters/pipelines.adoc#pipelines-graphics-pipeline-creation) and [fragment operations](../../../../vulkan-docs/src/chapters/fragops.adoc#fragops-multisampling).

### Coverage, attachments, and sample locations

The test names the larger count `numCoverageSamples`. It creates a color image with `numColorSamples` and a depth/stencil image with `numDepthStencilSamples`, then uses the maximum as the pipeline rasterization count. Standard-location cases use Vulkan's standard sample locations. Programmable-location cases use `VK_EXT_sample_locations` and generate a seeded location grid for that coverage count.

## One Concrete Example

A representative single-subpass case uses one color sample and four depth/stencil samples. The pipeline uses four rasterization samples, creates a `VK_FORMAT_R8G8B8A8_UNORM` color attachment with one sample and a depth/stencil attachment with four samples, draws subpixel triangles, and dispatches a compute validator. The validator produces a checksum for every pixel and coverage-sample position; host code requires the color, depth, and stencil bits appropriate to the selected format.

## End-to-End Test Flow

```text
[host] select a construction type, sample-count arrangement, format, and location mode
[host] require AMD mixed samples or NV mixed samples plus coverage reduction mode
[host] create mixed-count color and depth/stencil images, render pass, and graphics pipeline
[device] draw generated subpixel triangles for each subpass
[device] dispatch a compute checker over every attachment sample
[host] inspect checker checksums and fail on a missing required color, depth, or stencil bit
```

The `shader_builtins` path instead renders, resolves the color image when needed, copies it to host-visible memory, and requires a green resolved image. It uses `gl_SampleID` and `gl_SamplePosition` to expose the pipeline rasterization sample count.

## Generated Test Artifacts and Bound Resources

| Resource | Created/configured by host? | Used by device? | Read by host? | Why it matters |
|---|---|---|---|---|
| Color and depth/stencil images | yes | attachments and compute-validator inputs | checker results indirectly | Their distinct sample counts are the tested state. |
| Render pass and graphics pipeline | yes | used for the draw | no | They carry `rasterizationSamples`, optional sample locations, and coverage-reduction state. |
| Generated vertices | yes | vertex input | no | Subpixel triangles create expected per-sample coverage. |
| Compute result buffer | yes | written by validator | yes | It records the color/depth/stencil checksum bits per checked sample. |
| Resolve image and color buffer | yes, built-ins path | resolve/copy destination | yes | They expose the built-in result to `compareGreenImage`. |

## What Is Checked

- `verify_standard_locations` checks every sample in each selected color, depth, and stencil attachment using standard sample locations.
- `verify_programmable_locations` performs the same sample check after enabling `VK_EXT_sample_locations` and supplying generated locations.
- `shader_builtins` checks a resolved green image after shaders use `gl_SampleID` and `gl_SamplePosition` for the mixed-count configuration.

## Behavior Parameter Identification

> **Behavior parameter:** direct intermediate node
>
> **Candidate values:** `verify_standard_locations`, `verify_programmable_locations`, `shader_builtins`

The first two nodes share the attachment-sample validator but differ in the source of sample locations. `shader_builtins` uses a separate render, resolve, and image comparison path. Sample counts, depth/stencil format, construction type, and fragment-shading-rate mode build the matrix around these behaviors.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `verify_standard_locations` | Incorrect mixed-count attachment coverage, standard sample-location handling, per-sample attachment access, or compute-checker readback. |
| `verify_programmable_locations` | Incorrect programmable sample-location state or mixed-count attachment coverage and per-sample validation. |
| `shader_builtins` | Incorrect `gl_SampleID` or `gl_SamplePosition` behavior for the mixed-count pipeline, resolve behavior, or image copyback. |

## Important Variations and Special Cases

- The source registers ten single-subpass color/depth-stencil sample-count pairs, from `1/2` through `8/16`, plus eight multi-subpass sequences that increase or decrease color or coverage counts.
- Standard and programmable location nodes use seven depth/stencil formats for single-subpass cases and a reduced three-format set for multi-subpass cases. `shader_builtins` uses the reduced set.
- `shader_builtins` is omitted when `useFragmentShadingRate` is true. The other two nodes remain registered.
- The source skips unsupported devices: it requires `VK_AMD_mixed_attachment_samples`, or both `VK_NV_framebuffer_mixed_samples` and `VK_NV_coverage_reduction_mode`; programmable cases also require `VK_EXT_sample_locations`. The NV path queries supported combinations and requires `VK_COVERAGE_REDUCTION_MODE_TRUNCATE_NV` for the selected counts.

## Source Mapping

| Topic | Source link | Why it matters |
|---|---|---|
| Factory and root registration | [`createMultisampleMixedAttachmentSamplesTests`](../../../modules/vulkan/pipeline/vktPipelineMultisampleMixedAttachmentSamplesTests.cpp#L2158-L2165) | Creates `mixed_attachment_samples`. |
| Pipeline multisample state | [`preparePipelineWrapper`](../../../modules/vulkan/pipeline/vktPipelineMultisampleMixedAttachmentSamplesTests.cpp#L176-L252) | Sets rasterization samples and attaches location or coverage-reduction state. |
| Requirements | [`VerifySamples::checkRequirements`](../../../modules/vulkan/pipeline/vktPipelineMultisampleMixedAttachmentSamplesTests.cpp#L1319-L1416) | Checks extensions, NV combinations, programmable locations, shading rate, and construction support. |
| Per-sample validation | [`VerifySamples::test`](../../../modules/vulkan/pipeline/vktPipelineMultisampleMixedAttachmentSamplesTests.cpp#L1418-L1508) | Dispatches the compute checker and consumes its checksum bits. |
| Built-in validation | [`ShaderBuiltins::test`](../../../modules/vulkan/pipeline/vktPipelineMultisampleMixedAttachmentSamplesTests.cpp#L1824-L1905) | Renders, resolves/copies, and requires a green image. |
| Matrix registration | [`createMixedAttachmentSamplesTestsInGroup`](../../../modules/vulkan/pipeline/vktPipelineMultisampleMixedAttachmentSamplesTests.cpp#L1931-L2153) | Defines the direct nodes, count matrices, formats, and conditional built-ins node. |
| Mixed-sample pipeline rules | [Graphics pipeline creation](../../../../vulkan-docs/src/chapters/pipelines.adoc#pipelines-graphics-pipeline-creation) | Defines mixed-sample validation conditions. |
| Mixed-sample coverage | [Fragment operations](../../../../vulkan-docs/src/chapters/fragops.adoc#fragops-multisampling) | Defines coverage behavior when counts differ. |

## Questions / Risk Points for User Audit

- Is the separation between per-sample checksum validation and resolved-image built-in validation clear?
- Is the conditional absence of `shader_builtins` under fragment shading rate clear?

## Conversion Notes for Final Wiki Rewrite

Preserve the `### Failure Cause Mapping` table byte-for-byte in the final page. Use the three direct intermediate nodes as the behavioral axis, distinguish the two validation paths, and state that a final failure classifies an operation chain rather than proving one Vulkan stage caused it.
