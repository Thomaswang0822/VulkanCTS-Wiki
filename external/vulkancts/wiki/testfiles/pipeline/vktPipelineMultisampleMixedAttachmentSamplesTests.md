# vktPipelineMultisampleMixedAttachmentSamplesTests.cpp

## Overview

[`vktPipelineMultisampleMixedAttachmentSamplesTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleMixedAttachmentSamplesTests.cpp#L1) implements the [`mixed_attachment_samples`](../../../modules/vulkan/pipeline/vktPipelineMultisampleMixedAttachmentSamplesTests.cpp#L2163) topic group. It verifies VK_AMD_mixed_attachment_samples and VK_NV_framebuffer_mixed_samples with VK_NV_coverage_reduction_mode, testing graphics pipelines with varying sample counts per color and depth/stencil attachment.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineMultisampleMixedAttachmentSamplesTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleMixedAttachmentSamplesTests.cpp#L1)
- Header: [`vktPipelineMultisampleMixedAttachmentSamplesTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleMixedAttachmentSamplesTests.hpp#L1)

## Registration Hierarchy

```text
pipeline.monolithic.multisample.mixed_attachment_samples
├── verify_standard_locations
├── verify_programmable_locations
└── shader_builtins
```

Source: [`createMultisampleMixedAttachmentSamplesTests()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleMixedAttachmentSamplesTests.cpp#L2162) returns the `mixed_attachment_samples` group, added to the `multisample` group by `createMultisampleTests()`. Variant coverage: all variants. The `shader_builtins` subgroup is only added when `useFragmentShadingRate` is false.

## Test Families

### verify_standard_locations — Standard sample locations with mixed attachment samples

Verifies mixed attachment samples with standard sample locations. Contains leaf test cases organized by `{sample_case}` (single-pass and multi-subpass configurations) and `{subpass_case}` (format combinations). Single-pass cases cover 10 color/depth-stencil sample-count combinations. Multi-subpass cases cover increase/decrease color and coverage patterns.

### verify_programmable_locations — Programmable sample locations with mixed attachment samples

Verifies mixed attachment samples with programmable sample locations. Contains the same `{sample_case}` and `{subpass_case}` structure as `verify_standard_locations`, but with programmable sample locations enabled.

### shader_builtins — Shader built-in variables with mixed sample counts

Verifies shader built-in variables (`gl_SampleID`, `gl_SamplePosition`) work correctly with mixed sample counts. Contains leaf test cases parameterized by `{sample_count}`. Only registered when `useFragmentShadingRate` is false.

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| Color sample count | Array | 1, 2, 4, 8 (less than depth/stencil) |
| Depth/stencil sample count | Array | 2, 4, 8, 16 (greater than color) |
| Subpass configuration | Enum | Single subpass, multi-subpass |
| PipelineConstructionType | Parameter | All variant types |
| useFragmentShadingRate | Bool | false / true |

## Support/Feature Requirements

| Requirement | Context |
|---|---|
| `VK_AMD_mixed_attachment_samples` | Primary extension, or |
| `VK_NV_framebuffer_mixed_samples` + `VK_NV_coverage_reduction_mode` | Alternative extension pair |

## Verification Methods

- **Pixel comparison**: Render with mixed sample counts, resolve, compare against expected color values
- **Sample location verification**: Verify that sample locations are correctly applied for each attachment's sample count
- **Shader built-in check**: Verify `gl_SampleID` and `gl_SamplePosition` return correct values for the pipeline's rasterization sample count

## Notes

- Requires either VK_AMD_mixed_attachment_samples or the combination of VK_NV_framebuffer_mixed_samples and VK_NV_coverage_reduction_mode
- The test skips if neither extension combination is supported
