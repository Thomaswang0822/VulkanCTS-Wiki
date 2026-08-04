## Overview

**Core question:** Can a graphics pipeline render every required color, depth, and stencil sample when its attachments use different sample counts, and can shader sample built-ins observe that configuration correctly?

`MultisampleMixedAttachmentSamples` is the `mixed_attachment_samples` test family implemented by [`vktPipelineMultisampleMixedAttachmentSamplesTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleMixedAttachmentSamplesTests.cpp#L1931-L2165). It covers two per-sample attachment-validation nodes and one shader-built-in node. The first two draw subpixel triangles, run a compute checker over the attachment samples, and compare host-visible checksum bits. The built-in node renders and resolves a color image, then checks the copied image.

The default `vk-default/pipeline` mustpass contains 218 leaves under each of seven construction roots: monolithic, fast-linked-library, pipeline-library, shader-object-linked-binary, shader-object-linked-spirv, shader-object-unlinked-binary, and shader-object-unlinked-spirv. The `shader_builtins` intermediate node is omitted when the parent enables fragment shading rate.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- `VkPipelineMultisampleStateCreateInfo::rasterizationSamples` controls the pipeline coverage sample count. With [`VK_AMD_mixed_attachment_samples`](../../../../vulkan-docs/src/chapters/fragops.adoc#fragops-multisampling), the pipeline count equals the maximum sample count of the color and depth/stencil attachments. The NV path uses `VK_NV_framebuffer_mixed_samples` with `VK_NV_coverage_reduction_mode` and a supported coverage-reduction combination.
- The implementation calls the maximum count `numCoverageSamples`, while `numColorSamples` and `numDepthStencilSamples` describe the two attachment image counts. The color attachment therefore can have fewer samples than the rasterization count.
- Programmable sample locations come from `VK_EXT_sample_locations`. The test supplies a generated location grid to the pipeline and to the expected-coverage geometry. Standard-location cases use the Vulkan standard locations instead.
- A depth/stencil format can expose depth, stencil, or both aspects. The checksum checker records separate bits, so a failure must match the aspects present in the selected format.

## Registration Hierarchy

```text
pipeline.monolithic.multisample.mixed_attachment_samples
├── verify_standard_locations
├── verify_programmable_locations
└── shader_builtins
```

The source creates the `mixed_attachment_samples` family under the parent multisample group. Its direct children are intermediate nodes, not separate test families. Equivalent roots use the same three direct children when the selected construction type supports them. The `shader_builtins` child is conditional on `useFragmentShadingRate == false`.

## Parameter Dimensions and Observed Values

| Parameter | Source | Values and observed role |
|---|---|---|
| Direct intermediate node | [`createMixedAttachmentSamplesTestsInGroup`](../../../modules/vulkan/pipeline/vktPipelineMultisampleMixedAttachmentSamplesTests.cpp#L2027-L2153) | `verify_standard_locations`, `verify_programmable_locations`, `shader_builtins`; selects the validation path |
| Single-subpass color/depth sample pair | [`singlePassCases`](../../../modules/vulkan/pipeline/vktPipelineMultisampleMixedAttachmentSamplesTests.cpp#L1952-L1966) | 10 pairs: color 1, 2, or 4 with larger depth/stencil counts through 16, plus color 8 with depth/stencil 16 |
| Multi-subpass sequence | [`subpassCases`](../../../modules/vulkan/pipeline/vktPipelineMultisampleMixedAttachmentSamplesTests.cpp#L1968-L2025) | Eight increase/decrease color or coverage sequences using counts 1, 2, 4, and 8 |
| Color format | Format arrays | `VK_FORMAT_R8G8B8A8_UNORM` |
| Depth/stencil format, full set | `depthStencilFormatRange` | `VK_FORMAT_D16_UNORM`, `VK_FORMAT_X8_D24_UNORM_PACK32`, `VK_FORMAT_D32_SFLOAT`, `VK_FORMAT_S8_UINT`, `VK_FORMAT_D16_UNORM_S8_UINT`, `VK_FORMAT_D24_UNORM_S8_UINT`, `VK_FORMAT_D32_SFLOAT_S8_UINT` |
| Depth/stencil format, reduced set | `depthStencilReducedFormatRange` | `VK_FORMAT_D16_UNORM`, `VK_FORMAT_D24_UNORM_S8_UINT`, `VK_FORMAT_D32_SFLOAT_S8_UINT` |
| Sample-location mode | Group selection | Standard locations or programmable locations from `VK_EXT_sample_locations` |
| Pipeline construction type | Factory parameter | The construction root supplied by the pipeline category; all supported variants are exercised |
| Fragment shading rate | Factory parameter | `false` or `true`; `shader_builtins` is registered only for `false` |

The generated leaf names encode coverage, color, and depth/stencil counts as `coverage_<coverage>_color_<color>_depth_stencil_<depth>`, followed by format names. Multi-subpass leaves encode their sequence name instead.

## Behavior Parameters

The primary behavioral axis is the direct intermediate node. It selects whether the test uses standard locations, programmable locations, or shader built-ins.

### verify_standard_locations: per-sample validation with standard locations

The test creates mixed-count attachments, generates subpixel triangles from standard framebuffer sample locations, and validates all requested attachment aspects through the compute checker. It covers both single-subpass pairs and multi-subpass changes in color or coverage counts.

### verify_programmable_locations: per-sample validation with programmable locations

This node follows the same draw and checksum path, but obtains the device sample-location grid properties, fills a deterministic `MultisamplePixelGrid` with seed values based on the subpass index, and uses those locations when generating triangles and pipeline state. It checks that programmable locations do not break mixed-count attachment coverage.

### shader_builtins: `gl_SampleMaskIn` and `gl_SampleID`

This node uses the single-subpass sample-count pairs. With one color sample, its fragment program requires `gl_SampleMaskIn[0]` to contain every coverage-sample bit. With multiple color samples, it requires `gl_SampleMaskIn[0]` to contain only the bit selected by `gl_SampleID` and also checks that `gl_SampleID` is less than the color sample count. A satisfied predicate produces green; a bad mask produces red, and an out-of-range sample ID also adds blue. The test resolves the color attachment when it has more than one sample, copies the result to a host-visible buffer, and passes only when `compareGreenImage` accepts it.

## Shader Analysis

The implementation generates GLSL in C++ for both paths. The per-sample verifier's fragment program writes sample-dependent values and the compute checker reads color and depth/stencil images through descriptors; the host does not compare the rendered image directly. The built-in path generates a vertex/fragment pair that checks `gl_SampleMaskIn` and, for multisampled color attachments, `gl_SampleID`; its output is observed after rendering and resolve. It does not read `gl_SamplePosition`. These shaders establish the observation mechanism, while the tested behavior is mixed attachment sample coverage and the sample-count-dependent built-in result.

The source does not load a fixed shader artifact or embed a stable SPIR-V listing. Each leaf changes sample counts, formats, location mode, and sometimes the subpass sequence, so a single disassembly would not represent the generated matrix.

## Runtime Execution and Result Checking

1. The case checks for `VK_AMD_mixed_attachment_samples`, or the NV extension pair. Programmable cases additionally require `VK_EXT_sample_locations`. The NV path queries `vkGetPhysicalDeviceSupportedFramebufferMixedSamplesCombinationsNV` and requires a matching `VK_COVERAGE_REDUCTION_MODE_TRUNCATE_NV` combination. Fragment-shading-rate cases check `VK_KHR_fragment_shading_rate` and a suitable `2x2` rate.
2. For each subpass, the verifier creates color and depth/stencil images using their selected counts, image views, comparison data, a host-visible result buffer, and vertices covering the small `2x2` render area. Programmable cases create their seeded sample-location grid.
3. It builds the render pass and graphics pipeline. `rasterizationSamples` receives the maximum coverage count; optional `VkPipelineSampleLocationsStateCreateInfoEXT` and `VkPipelineCoverageReductionStateCreateInfoNV` structures extend the multisample state.
4. The test records and submits the draw. It then dispatches a compute shader that reads the attachment samples and writes one checksum per expected sample to the result buffer. A buffer barrier makes those writes visible to the host, and the allocation is invalidated before inspection.
5. For each result element, host code requires the color bit and, when present, the depth and stencil bits. Any missing bit returns `Multisampled image has incorrect samples`; otherwise the verifier returns `Pass`.
6. The `shader_builtins` path creates a color image and depth/stencil image, creates a single-sample resolve image when needed, records a draw and resolve, copies the color result to a host-visible buffer, and returns pass only when `compareGreenImage` succeeds.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `verify_standard_locations` | Incorrect mixed-count attachment coverage, standard sample-location handling, per-sample attachment access, or compute-checker readback. |
| `verify_programmable_locations` | Incorrect programmable sample-location state or mixed-count attachment coverage and per-sample validation. |
| `shader_builtins` | Incorrect `gl_SampleMaskIn` or `gl_SampleID` behavior for the mixed-count pipeline, resolve behavior, or image copyback. |

### Cause Analysis

#### Standard-location per-sample validation

**Possible failure symptoms:** The checksum lacks a required color, depth, or stencil bit, and the test reports `Multisampled image has incorrect samples`.

**Possible implementation causes:** The implementation may apply mixed-count coverage incorrectly, use the wrong standard sample locations, mishandle depth or stencil sample access, or fail to make compute-checker writes visible to the host. The final checksum spans rasterization, attachment access, compute validation, synchronization, and readback, so source-level investigation is needed to isolate the failing operation.

#### Programmable-location per-sample validation

**Possible failure symptoms:** The programmable-location node reports a missing attachment-aspect bit for one or more sample positions, or fails during sample-location setup.

**Possible implementation causes:** The implementation may reject or misapply `VkPipelineSampleLocationsStateCreateInfoEXT`, use a different location grid for rasterization and expected geometry, or combine programmable locations with mixed attachment coverage incorrectly. A host-visible checksum failure cannot by itself distinguish location interpolation from attachment or copyback behavior.

#### Shader-built-in result

**Possible failure symptoms:** `shader_builtins` fails its resolved-image comparison or reports `Some samples were incorrect`.

**Possible implementation causes:** The implementation may expose a wrong `gl_SampleMaskIn` value or an out-of-range or mismatched `gl_SampleID`, apply the mixed-count rasterization rules incorrectly, resolve the color attachment incorrectly, or copy the result back incorrectly. The final green-image observation crosses shader execution, rasterization, resolve, transfer, and host comparison, so it does not prove one exclusive Vulkan stage caused the failure.

## Case Pruning

- The source skips the complete family when neither extension path is supported. It also skips individual sample pairs that fail image, sample-count, programmable-location, NV-combination, fragment-shading-rate, or pipeline-construction requirements.
- `shader_builtins` is design-pruned for `useFragmentShadingRate == true`; the factory adds it only when that flag is false.
- Multi-subpass cases use the reduced depth/stencil format set to cover depth-only and combined depth/stencil behavior without repeating the full format matrix.
- The default mustpass represents the construction-root expansion. The source's conditional node registration and support checks determine which leaves are executable on a particular device.

## Key Takeaways

- The family tests mixed color and depth/stencil sample counts, not a generic multisample image matrix.
- `verify_standard_locations` and `verify_programmable_locations` validate every relevant attachment sample through a compute checksum path.
- `shader_builtins` checks `gl_SampleMaskIn` and `gl_SampleID` through a separate render, resolve, and host-image comparison path and is absent under fragment shading rate.
- A failing checksum or image comparison identifies a complete tested operation chain. Further source-level investigation is required to isolate a driver stage.

## Source Reference Appendix

| Topic | Source reference | Evidence |
|---|---|---|
| Family registration | [`createMultisampleMixedAttachmentSamplesTests`](../../../modules/vulkan/pipeline/vktPipelineMultisampleMixedAttachmentSamplesTests.cpp#L2158-L2165) | Creates the `mixed_attachment_samples` family. |
| Pipeline multisample state | [`preparePipelineWrapper`](../../../modules/vulkan/pipeline/vktPipelineMultisampleMixedAttachmentSamplesTests.cpp#L176-L252) | Sets `rasterizationSamples` and optional sample-location and coverage-reduction state. |
| Per-sample setup and draw | [`createPerSubpassData` and `draw`](../../../modules/vulkan/pipeline/vktPipelineMultisampleMixedAttachmentSamplesTests.cpp#L1200-L1317) | Creates resources, expected data, vertices, and draw inputs. |
| Compute checker and synchronization | [`dispatchImageCheck`](../../../modules/vulkan/pipeline/vktPipelineMultisampleMixedAttachmentSamplesTests.cpp#L1094-L1198) | Dispatches image checking and makes results host-visible. |
| Per-sample result check | [`VerifySamples::test`](../../../modules/vulkan/pipeline/vktPipelineMultisampleMixedAttachmentSamplesTests.cpp#L1418-L1508) | Checks color, depth, and stencil checksum bits. |
| Built-in result check | [`ShaderBuiltins::test`](../../../modules/vulkan/pipeline/vktPipelineMultisampleMixedAttachmentSamplesTests.cpp#L1824-L1905) | Resolves/copies and compares the green image. |
| Test matrix | [`createMixedAttachmentSamplesTestsInGroup`](../../../modules/vulkan/pipeline/vktPipelineMultisampleMixedAttachmentSamplesTests.cpp#L1931-L2153) | Defines counts, formats, direct nodes, and conditional registration. |
| Mixed-sample coverage rules | [Fragment operations](../../../../vulkan-docs/src/chapters/fragops.adoc#fragops-multisampling) | Describes coverage when rasterization and attachment counts differ. |
| Pipeline validity rules | [Graphics pipeline creation](../../../../vulkan-docs/src/chapters/pipelines.adoc#pipelines-graphics-pipeline-creation) | Describes mixed-sample pipeline constraints. |
| Default mustpass scope | [`pipeline` mustpass files](../../../mustpass/main/vk-default/pipeline) | Records the construction-root leaf lists. |
