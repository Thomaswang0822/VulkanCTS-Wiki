# vktPipelineMultisampleMixedAttachmentSamplesTests.cpp

## Overview

[`vktPipelineMultisampleMixedAttachmentSamplesTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleMixedAttachmentSamplesTests.cpp#L1) implements the [`mixed_attachment_samples`](../../../modules/vulkan/pipeline/vktPipelineMultisampleMixedAttachmentSamplesTests.cpp#L2163) topic group. It verifies VK_AMD_mixed_attachment_samples and VK_NV_framebuffer_mixed_samples with VK_NV_coverage_reduction_mode, testing graphics pipelines with varying sample counts per color and depth/stencil attachment.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineMultisampleMixedAttachmentSamplesTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleMixedAttachmentSamplesTests.cpp#L1)
- Header: [`vktPipelineMultisampleMixedAttachmentSamplesTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleMixedAttachmentSamplesTests.hpp#L1)

## Registration Path

[`createMultisampleMixedAttachmentSamplesTests()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleMixedAttachmentSamplesTests.cpp#L2162) returns the `mixed_attachment_samples` group, added to the `multisample` group by `createMultisampleTests()`.

**Variant coverage**: All variants.

## Test Hierarchy

```text
mixed_attachment_samples
├── verify_standard_locations
│   └── {sample_case}
│       └── {subpass_case}
├── verify_programmable_locations
│   └── {sample_case}
│       └── {subpass_case}
└── shader_builtins
    └── {sample_count}
```

## Test Families

| Family | Description |
|---|---|
| Standard locations test | Verifies mixed attachment samples with standard sample locations |
| Programmable locations test | Verifies mixed attachment samples with programmable sample locations |
| Shader builtins test | Verifies shader built-in variables work correctly with mixed sample counts |

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
