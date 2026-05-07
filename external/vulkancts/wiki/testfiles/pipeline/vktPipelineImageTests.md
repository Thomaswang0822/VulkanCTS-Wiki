# vktPipelineImageTests.cpp

## Overview

[`vktPipelineImageTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineImageTests.cpp#L1) implements the [`image`](../../../modules/vulkan/pipeline/vktPipelineImageTests.cpp#L919) topic group. It verifies image sampling across all view types, formats, image counts, and sizes, using both suballocated and dedicated allocation memory.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineImageTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineImageTests.cpp#L1)
- Header: [`vktPipelineImageTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineImageTests.hpp#L1)
- Shared instance: [`vktPipelineImageSamplingInstance.cpp`](../../../modules/vulkan/pipeline/vktPipelineImageSamplingInstance.cpp#L1)

## Registration Path

[`createImageTests()`](../../../modules/vulkan/pipeline/vktPipelineImageTests.cpp#L917) returns the `image` group, attached under each variant root by `createChildren()`.

**Variant coverage**: Monolithic or base ESO only.

## Test Hierarchy

```text
image
├── suballocation
│   └── sampling_type
│       ├── combined
│       │   └── view_type
│       │       └── {1d,1d_array,2d,2d_array,3d,cube,cube_array}
│       │           └── format/<format>/count_{1,4,8}/size/<size_cases>
│       └── separate
│           └── (same structure)
└── dedicated_allocation
    └── (same structure, limited formats/counts)
```

## Test Families

### 1. suballocation

Image sampling with suballocated memory. Full format set, counts 1/4/8, all size variants.

### 2. dedicated_allocation

Image sampling with dedicated allocation memory. Only R8G8B8A8_UNORM and R16_SFLOAT formats, count=1.

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| AllocationKind | Enum | SUBALLOCATED, DEDICATED |
| VkDescriptorType | Loop | COMBINED_IMAGE_SAMPLER, SAMPLED_IMAGE |
| VkImageViewType | Loop | 7 types (1d through cube_array) |
| VkFormat | `formats::pipelineImageFormats` | ~100+ formats (suballocated); 2 formats (dedicated) |
| Image count | Array | {1, 4, 8} (suballocated); {1} (dedicated) |
| Image sizes | Per view type | POT, NPOT, rectangular sizes |
| Pipeline protected flag | bool | {false, true} (non-VulkanSC) |

## Support / Feature Requirements

| Requirement | Condition | Line |
|---|---|---|
| `DEVICE_CORE_FEATURE_SHADER_SAMPLED_IMAGE_ARRAY_DYNAMIC_INDEXING` | imageCount > 1 | [112](../../../modules/vulkan/pipeline/vktPipelineImageTests.cpp#L112) |
| `VK_KHR_maintenance5` | A8_UNORM/A1B5G5R5 formats | [119](../../../modules/vulkan/pipeline/vktPipelineImageTests.cpp#L119) |
| `VK_EXT_pipeline_protected_access` | pipelineProtectedFlag (non-VulkanSC) | [137](../../../modules/vulkan/pipeline/vktPipelineImageTests.cpp#L137) |
| Pipeline construction requirements | Always | [130](../../../modules/vulkan/pipeline/vktPipelineImageTests.cpp#L130) |

## Verification Methods

Renders a textured quad (graphics) or dispatches compute, then compares output against reference using `ImageSamplingInstance` with format-aware pixel thresholds. Each leaf test has a `_compute` variant.

## Notes / Uncertainties

- Compressed formats skipped for 1D/1D_ARRAY view types
- ASTC 3D formats only for VK_IMAGE_VIEW_TYPE_3D with suballocated memory
