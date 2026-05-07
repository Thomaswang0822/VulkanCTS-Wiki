# vktPipelineSamplerTests.cpp

## Overview

[`vktPipelineSamplerTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineSamplerTests.cpp#L1) implements the [`sampler`](../../../modules/vulkan/pipeline/vktPipelineSamplerTests.cpp#L3179) topic group. It verifies sampler state behavior including filters, reduction modes, mipmap modes, LOD, address modes, border colors, exact sampling, border swizzle, and max LOD bias.

## Role

Implementation file. Also dispatches to [`vktPipelineSamplerBorderSwizzleTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineSamplerBorderSwizzleTests.cpp#L1) for border swizzle tests.

## Source Code

- Primary source: [`vktPipelineSamplerTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineSamplerTests.cpp#L1)
- Header: [`vktPipelineSamplerTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineSamplerTests.hpp#L1)
- Nested subgroup: [`vktPipelineSamplerBorderSwizzleTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineSamplerBorderSwizzleTests.cpp#L1)
- Shared instance: [`vktPipelineImageSamplingInstance.cpp`](../../../modules/vulkan/pipeline/vktPipelineImageSamplingInstance.cpp#L1)

## Registration Path

[`createSamplerTests()`](../../../modules/vulkan/pipeline/vktPipelineSamplerTests.cpp#L3174) returns the `sampler` group, attached under each variant root by `createChildren()`.

**Variant coverage**: All variants. Full `view_type` subtree and `border_swizzle` only for monolithic/shader_object_unlinked_spirv.

## Test Hierarchy

```text
sampler
├── view_type                            (genAllTests only)
│   └── {1d,1d_unnormalized,1d_array,2d,2d_unnormalized,2d_array,3d,cube,cube_array}
│       └── format/<format>
│           ├── mag_filter/{nearest,linear}
│           ├── min_filter/{nearest,linear}
│           ├── mag_reduce/<component_mapping>/{average,min,max}
│           ├── min_reduce/<component_mapping>/{average,min,max}
│           ├── mipmap/{nearest,linear}/lod/<lod_cases>
│           └── address_modes/<address_mode_cases>
├── exact_sampling
│   └── <format>/{gradient,solid_color}/{normalized,unnormalized}/{centered,edge_left,edge_right}
├── separate_stencil_usage
│   └── (same as view_type with separateStencilUsage=true)
├── border_swizzle                       (non-VulkanSC, genAllTests only)
└── max_sampler_lod_bias
    ├── sampler_bias / sampler_minlod / shader_lod / shader_bias / view_minlod
```

## Test Families

### 1. mag_filter / min_filter

Tests VK_FILTER_NEAREST and VK_FILTER_LINEAR for magnification and minification.

### 2. mag_reduce / min_reduce

Tests VK_SAMPLER_REDUCTION_MODE (WEIGHTED_AVERAGE, MIN, MAX) with component mappings.

### 3. mipmap / lod

Tests VK_SAMPLER_MIPMAP_MODE_NEAREST/LINEAR with minLod/maxLod/mipLodBias combinations.

### 4. address_modes

Tests all VkSamplerAddressMode combinations with border colors including custom.

### 5. exact_sampling

Verifies pixel-exact sampling with NEAREST filter at edge positions.

### 6. separate_stencil_usage

Same as view_type but with VK_EXT_separate_stencil_usage.

### 7. border_swizzle

VK_EXT_border_color_swizzle tests (non-VulkanSC).

### 8. max_sampler_lod_bias

Tests maxSamplerLodBias limit via sampler bias, minLod, shader LOD, shader bias, and VK_EXT_image_view_min_lod.

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| SamplerViewType | Custom class | 9 variants (7 standard + 1d/2d unnormalized) |
| VkFormat | Array | ~80+ formats |
| VkFilter | Enum | NEAREST, LINEAR |
| VkSamplerReductionMode | Enum | WEIGHTED_AVERAGE, MIN, MAX |
| ComponentMapping | Array | 5 mappings |
| VkSamplerMipmapMode | Enum | NEAREST, LINEAR |
| LOD configs | Struct array | 7 configs |
| Address mode configs | Struct array | ~30 configs |
| LodBiasCase | Enum | SAMPLER_BIAS, SAMPLER_MINLOD, SHADER_LOD, SHADER_BIAS, VIEW_MINLOD |

## Verification Methods

- **Filter/LOD/Mipmap/Address**: `ImageSamplingInstance` renders textured quad, compares against reference with format-aware thresholds
- **Exact Sampling**: Pixel-exact comparison (no threshold tolerance)
- **Max Sampler LOD Bias**: Fills each mip level with distinct color, samples at maxSamplerLodBias, verifies accessed mip level with threshold 0.005

## Notes / Uncertainties

- Unnormalized coordinates have reduced test coverage (no min_filter, no mipmap, limited address modes)
- Cube/cube_array have no address_modes tests
- Compressed formats skip min_filter/min_reduce (noise causes false positives)
