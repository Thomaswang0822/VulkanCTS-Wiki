# vktPipelineMultisampleImageTests.cpp

## Overview

[`vktPipelineMultisampleImageTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleImageTests.cpp#L1) implements multiple multisample image subgroups: [`sampled_image`](../../../modules/vulkan/pipeline/vktPipelineMultisampleImageTests.cpp#L2955), [`storage_image`](../../../modules/vulkan/pipeline/vktPipelineMultisampleImageTests.cpp#L2962), [`standardsampleposition`](../../../modules/vulkan/pipeline/vktPipelineMultisampleImageTests.cpp#L2969), [`samples_mapping_order`](../../../modules/vulkan/pipeline/vktPipelineMultisampleImageTests.cpp#L2977), and [`3d`](../../../modules/vulkan/pipeline/vktPipelineMultisampleImageTests.cpp#L2985). It verifies multisample image operations including sampling, storage reads/writes, standard sample positions, and 3D multisample images.

## Role

Implementation file. Each factory function creates a subgroup registered under `multisample` by the parent dispatcher.

## Source Code

- Primary source: [`vktPipelineMultisampleImageTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleImageTests.cpp#L1)
- Header: [`vktPipelineMultisampleImageTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleImageTests.hpp#L1)
- Base classes: [`vktPipelineMultisampleBase.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleBase.cpp#L1)

## Registration Path

Each factory function returns a subgroup added to the `multisample` group by `createMultisampleTests()`:

- [`createMultisampleSampledImageTests()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleImageTests.cpp#L2953) → `sampled_image`
- [`createMultisampleStorageImageTests()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleImageTests.cpp#L2960) → `storage_image`
- [`createMultisampleStandardSamplePositionTests()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleImageTests.cpp#L2967) → `standardsampleposition`
- [`createMultisampleSamplesMappingOrderTests()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleImageTests.cpp#L2975) → `samples_mapping_order`
- [`createMultisample3dImageTests()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleImageTests.cpp#L2983) → `3d`

**Variant coverage**: All variants. `samples_mapping_order` is conditional on `VK_EXT_sample_locations` support.

## Test Hierarchy

```text
sampled_image
└── {size_layer}
    └── {format}
        └── {sample_count}

storage_image
└── {size_layer}
    └── {format}
        └── {sample_count}

standardsampleposition
└── {format}
    └── {sample_count}

samples_mapping_order
└── {sample_count}

3d
└── {format}
    └── {sample_count}
```

## Test Families

| Family | Description |
|---|---|
| SampledImageTest | Verifies multisample image sampling produces correct resolved colors |
| StorageImageTest | Verifies multisample storage image read/write operations |
| StandardSamplePositionTest | Verifies standard sample positions match specification |
| SamplesMappingOrderTest | Verifies sample mapping order with VK_EXT_sample_locations |
| Image3dTest | Verifies 3D multisample image operations |

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| VkFormat | Loop | R8G8B8A8_UNORM, R32G32B32A32_SFLOAT, etc. |
| Sample count | Array | 2, 4, 8, 16 |
| Image size | Array | Various dimensions |
| Image type | Enum | 2D (most tests), 3D (3d subgroup) |
| PipelineConstructionType | Parameter | All variant types |

## Support/Feature Requirements

| Requirement | Context |
|---|---|
| `shaderStorageImageMultisample` | Required for storage_image tests |
| `standardSampleLocations` | Required for standardsampleposition tests |
| `VK_EXT_sample_locations` | Required for samples_mapping_order tests |

## Verification Methods

- **Pixel comparison**: Render using multisample image, resolve, compare against expected color
- **Storage image verification**: Write per-sample values to storage image, read back and compare
- **Sample position verification**: Verify sample positions match standard or programmable locations

## Notes

- The `samples_mapping_order` subgroup is only registered when `VK_EXT_sample_locations` is supported
- The `3d` subgroup tests 3D multisample images which require `shaderStorageImageMultisample` feature
