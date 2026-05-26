# vktPipelineSamplerTests.cpp

## Overview

[`vktPipelineSamplerTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineSamplerTests.cpp#L1) implements the [`sampler`](../../../modules/vulkan/pipeline/vktPipelineSamplerTests.cpp#L3179) topic group. It verifies sampler state behavior including filters, reduction modes, mipmap modes, LOD, address modes, border colors, exact sampling, border swizzle, and max LOD bias. This is a concrete implementation match for the historical API test-plan sampler-state objectives ([`apitests.adoc`](../../../../../doc/testspecs/VK/apitests.adoc#L549-L558)).

## Role

Implementation file. Also dispatches to [`vktPipelineSamplerBorderSwizzleTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineSamplerBorderSwizzleTests.cpp#L1) for border swizzle tests.

## Source Code

- Primary source: [`vktPipelineSamplerTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineSamplerTests.cpp#L1)
- Header: [`vktPipelineSamplerTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineSamplerTests.hpp#L1)
- Nested subgroup: [`vktPipelineSamplerBorderSwizzleTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineSamplerBorderSwizzleTests.cpp#L1)
- Shared instance: [`vktPipelineImageSamplingInstance.cpp`](../../../modules/vulkan/pipeline/vktPipelineImageSamplingInstance.cpp#L1)

## Registration Hierarchy

```text
pipeline.monolithic.sampler
├── view_type (monolithic, shader_object_unlinked_spirv only)
├── exact_sampling
├── separate_stencil_usage
├── border_swizzle (non-VulkanSC, monolithic, shader_object_unlinked_spirv only)
└── max_sampler_lod_bias
```

Source: [`createSamplerTests()`](../../../modules/vulkan/pipeline/vktPipelineSamplerTests.cpp#L3174).

## Test Families

### view_type — Sampler filter/reduce/mipmap/address mode tests (monolithic, shader_object_unlinked_spirv only)

Tests sampler state across all view types (1d, 1d_array, 2d, 2d_array, 3d, cube, cube_array, plus 1d/2d unnormalized). Each view type contains format subgroups, which in turn contain subgroups for mag_filter (NEAREST, LINEAR), min_filter (NEAREST, LINEAR), mag_reduce and min_reduce (WEIGHTED_AVERAGE, MIN, MAX with component mappings), mipmap (NEAREST, LINEAR with LOD configurations), and address_modes (all VkSamplerAddressMode combinations with border colors including custom).

### exact_sampling — Pixel-exact sampling verification

Verifies pixel-exact sampling with NEAREST filter at edge positions. Tests across formats with gradient/solid_color, normalized/unnormalized coordinates, and centered/edge_left/edge_right positions.

### separate_stencil_usage — Separate stencil usage sampling

Same test structure as `view_type` but with `VK_EXT_separate_stencil_usage` enabled (`separateStencilUsage=true`).

### border_swizzle — Border color swizzle (non-VulkanSC, monolithic, shader_object_unlinked_spirv only)

Tests `VK_EXT_border_color_swizzle` behavior. Delegated to [`vktPipelineSamplerBorderSwizzleTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineSamplerBorderSwizzleTests.cpp#L1).

### max_sampler_lod_bias — Max sampler LOD bias limit

Tests `maxSamplerLodBias` limit via sampler bias, minLod, shader LOD, shader bias, and `VK_EXT_image_view_min_lod`. Subgroups include `sampler_bias`, `sampler_minlod`, `shader_lod`, `shader_bias`, and `view_minlod`.

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
