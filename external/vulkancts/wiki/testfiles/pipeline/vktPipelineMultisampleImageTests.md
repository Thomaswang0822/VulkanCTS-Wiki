# vktPipelineMultisampleImageTests.cpp

## Overview

[`vktPipelineMultisampleImageTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleImageTests.cpp#L1) implements the [`sampled_image`](../../../modules/vulkan/pipeline/vktPipelineMultisampleImageTests.cpp#L2955) subgroup under `multisample`. It verifies multisample image sampling produces correct resolved colors. The same source file also implements sibling subgroups `storage_image`, `standardsampleposition`, `samples_mapping_order`, and `3d` which are registered separately under `multisample`.

## Role

Implementation file. The [`createMultisampleSampledImageTests()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleImageTests.cpp#L2952) factory function creates the `sampled_image` subgroup registered under `multisample` by the parent dispatcher [`createMultisampleTests()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleTests.cpp#L7247).

## Source Code

- Primary source: [`vktPipelineMultisampleImageTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleImageTests.cpp#L1)
- Header: [`vktPipelineMultisampleImageTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleImageTests.hpp#L1)
- Base classes: [`vktPipelineMultisampleBase.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleBase.cpp#L1)

## Registration Hierarchy

```text
pipeline.monolithic.multisample.sampled_image
├── 64x64_1
├── 64x64_4
├── 79x31_1
└── 79x31_4
```

**Variant coverage**: All variants. The sibling subgroups `storage_image`, `standardsampleposition`, and `samples_mapping_order` (conditional on `VK_EXT_sample_locations`) are also registered under `multisample` from this same source file.

## Test Families

### 64x64_1 — 64x64 image with 1 layer

Tests multisample sampled image with a 64x64 image and a single layer. Each child is a format group (R8G8B8A8_UNORM, R32_UINT, R16G16_SINT, R32G32B32A32_SFLOAT), which in turn contains sample count cases (2, 4, 8, 16, 32, 64).

### 64x64_4 — 64x64 image with 4 layers

Tests multisample sampled image with a 64x64 image and 4 layers. Same format and sample count structure as `64x64_1`.

### 79x31_1 — 79x31 image with 1 layer

Tests multisample sampled image with a non-power-of-two 79x31 image and a single layer. Same format and sample count structure.

### 79x31_4 — 79x31 image with 4 layers

Tests multisample sampled image with a non-power-of-two 79x31 image and 4 layers. Same format and sample count structure.

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| VkFormat | Loop | R8G8B8A8_UNORM, R32_UINT, R16G16_SINT, R32G32B32A32_SFLOAT |
| Sample count | Array | 2, 4, 8, 16, 32, 64 |
| Image size | Array | (64,64), (79,31) |
| Num layers | Array | 1, 4 |
| PipelineConstructionType | Parameter | All variant types |

## Support/Feature Requirements

| Requirement | Context |
|---|---|
| `shaderStorageImageMultisample` | Required for storage_image sibling subgroup |
| `standardSampleLocations` | Required for standardsampleposition sibling subgroup |
| `VK_EXT_sample_locations` | Required for samples_mapping_order sibling subgroup |

## Verification Methods

- **Pixel comparison**: Render using multisample image, resolve, compare against expected color

## Notes

- The sibling subgroups `storage_image`, `standardsampleposition`, `samples_mapping_order`, and `3d` are also implemented in this source file but registered as separate children of `multisample`
- The `samples_mapping_order` subgroup is only registered when `VK_EXT_sample_locations` is supported
- The `3d` subgroup tests 3D multisample images which require `shaderStorageImageMultisample` feature
