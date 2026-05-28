# vktPipelineMultisampleTests.cpp

## Overview

[`vktPipelineMultisampleTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleTests.cpp#L1) implements the [`multisample`](../../../modules/vulkan/pipeline/vktPipelineMultisampleTests.cpp#L7256) topic group. It verifies core multisample state including rasterization samples, min sample shading, sample mask, alpha-to-coverage, alpha-to-one, and various multisample extensions. This is the primary dispatcher for multisample-related subgroups.

## Role

Registration and implementation file. Dispatches to multiple nested subgroup files for specialized multisample functionality.

## Source Code

- Primary source: [`vktPipelineMultisampleTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleTests.cpp#L1)
- Header: [`vktPipelineMultisampleTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleTests.hpp#L1)
- Base classes: [`vktPipelineMultisampleBase.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleBase.cpp#L1)
- Resolve base: [`vktPipelineMultisampleBaseResolve.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleBaseResolve.cpp#L1)
- Shared utilities: [`vktPipelineMultisampleTestsUtil.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleTestsUtil.cpp#L1)

## Registration Hierarchy

```text
pipeline.monolithic.multisample
├── raster_samples
├── raster_samples_consistency (non-VulkanSC only)
├── min_sample_shading
├── min_sample_shading_enabled
├── min_sample_shading_disabled
├── sample_mask
├── alpha_to_one
├── alpha_to_coverage
├── alpha_to_coverage_no_color_attachment
├── alpha_to_coverage_unused_attachment
├── sample_rate_a2c (non-VulkanSC only, no fragment shading rate)
├── sampled_image (non-VulkanSC only, no fragment shading rate)
├── 3d (non-VulkanSC only, no fragment shading rate)
├── storage_image (non-VulkanSC only, no fragment shading rate)
├── standardsampleposition (non-VulkanSC only, no fragment shading rate)
├── samples_mapping_order (non-VulkanSC only, no fragment shading rate)
├── shader_fragment_mask (non-VulkanSC only, no fragment shading rate)
├── resolve (non-VulkanSC only, no fragment shading rate)
├── multisampled_render_to_single_sampled (non-VulkanSC only)
├── misc (non-VulkanSC only)
├── sample_locations_ext (non-VulkanSC only)
├── std_sample_locations (non-VulkanSC only)
├── mixed_attachment_samples (non-VulkanSC only)
├── sample_mask_with_depth_test (non-VulkanSC only)
├── m10_resolve (non-VulkanSC only, no fragment shading rate)
├── conservative_with_full_coverage (non-shader-object only)
├── compatible_render_pass (non-shader-object only)
├── variable_rate
├── mixed_count
├── z_export (no fragment shading rate)
└── a2c_with_a2one (no fragment shading rate)
```

**Variant coverage**: All variants. The `multisample` group is registered once with `useFragmentShadingRate=false`, and again as `multisample_with_fragment_shading_rate` with `useFragmentShadingRate=true`. Some subgroups are conditionally registered based on variant and extension support.

## Test Families

### raster_samples — Rasterization sample count verification

Verifies correct rendering at each supported sample count (2-64) for color, depth, and stencil aspects. Contains per-sample-count subgroups (`samples_2` through `samples_64`) with leaf tests for each primitive type (triangle, line, point) and aspect (color, depth, stencil, depth_stencil), including sparse variants on non-VulkanSC.

### raster_samples_consistency — Rasterization sample consistency

Verifies that multisample rendering produces consistent results across sample counts. Non-VulkanSC only.

### min_sample_shading — Minimum sample shading (shader object)

Tests `minSampleShading` behavior with sample rate shading enabled for shader object construction type. Contains subgroups for each `minSampleShading` value (0.0, 0.25, 0.5, 0.75, 1.0), each with per-sample-count subgroups.

### min_sample_shading_enabled — Minimum sample shading enabled (non-shader-object)

Tests `minSampleShading` with sample rate shading explicitly enabled, for non-shader-object construction types. Uses `GEOMETRY_TYPE_OPAQUE_QUAD`.

### min_sample_shading_disabled — Minimum sample shading disabled (non-shader-object)

Tests `minSampleShading` with sample rate shading explicitly disabled, for non-shader-object construction types. Uses `GEOMETRY_TYPE_OPAQUE_QUAD`.

### sample_mask — Sample mask verification

Verifies `sampleMask` correctly masks samples for different primitive types. Contains subgroups for mask patterns (`mask_all_on`, `mask_all_off`, `mask_one`, `mask_random`), each with per-sample-count subgroups and per-primitive leaf tests, including sparse variants on non-VulkanSC.

### alpha_to_one — Alpha-to-one verification

Verifies `alphaToOneEnable` replaces fragment alpha with 1.0. Contains per-sample-count leaf tests (1-64), including sparse variants on non-VulkanSC.

### alpha_to_coverage — Alpha-to-coverage verification

Verifies `alphaToCoverageEnable` converts fragment alpha to coverage mask. Contains per-sample-count subgroups with leaf tests for opaque, translucent, invisible, and invisible_check_depth quad types, including sparse variants on non-VulkanSC.

### alpha_to_coverage_no_color_attachment — Alpha-to-coverage without color attachment

Verifies alpha-to-coverage without a color attachment. Contains per-sample-count subgroups with opaque and opaque_sparse leaf tests.

### alpha_to_coverage_unused_attachment — Alpha-to-coverage with unused color attachment

Verifies alpha-to-coverage with an unused color attachment (location 0 unused, alpha write controls coverage for location 1). Contains per-sample-count subgroups with opaque and invisible leaf tests, including sparse variants on non-VulkanSC.

### sample_rate_a2c — Sample-rate shading with alpha-to-coverage

Verifies sample-rate shading combined with alpha-to-coverage. Contains `static_a2c` and `dynamic_a2c` leaf tests. Non-VulkanSC only, not registered when fragment shading rate is used.

### sampled_image — Multisampled image sampling

Tests sampling from a multisampled image texture using `texelFetch`. Implemented in [`vktPipelineMultisampleImageTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleImageTests.cpp#L1). Non-VulkanSC only, not registered when fragment shading rate is used.

### 3d — 3D multisampled image tests

Tests multisampled 3D image textures. Implemented in [`vktPipelineMultisampleImageTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleImageTests.cpp#L1). Non-VulkanSC only, not registered when fragment shading rate is used.

### storage_image — Multisampled storage image tests

Tests load/store on multisampled rendered images (color attachment write, storage image, etc.). Implemented in [`vktPipelineMultisampleImageTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleImageTests.cpp#L1). Non-VulkanSC only, not registered when fragment shading rate is used.

### standardsampleposition — Standard sample position verification

Tests sampling from a multisampled image texture checking supersample positions. Implemented in [`vktPipelineMultisampleImageTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleImageTests.cpp#L1). Non-VulkanSC only, not registered when fragment shading rate is used.

### samples_mapping_order — Sample mapping order verification

Tests whether samples are mapped correctly in a multisampled image. Implemented in [`vktPipelineMultisampleImageTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleImageTests.cpp#L1). Non-VulkanSC only, limited to monolithic, fast-linked-library, and shader_object_unlinked_spirv variants.

### shader_fragment_mask — VK_AMD_shader_fragment_mask

Tests the `VK_AMD_shader_fragment_mask` extension. Implemented in [`vktPipelineMultisampleShaderFragmentMaskTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderFragmentMaskTests.cpp#L1). Non-VulkanSC only, not registered when fragment shading rate is used.

### resolve — Multisample resolve render area

Multisample resolve tests where a render area is less than an attachment size. Contains `renderpass_renderarea` subgroup. Implemented in [`vktPipelineMultisampleResolveRenderAreaTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveRenderAreaTests.cpp#L1). Non-VulkanSC only, not registered when fragment shading rate is used.

### multisampled_render_to_single_sampled — VK_EXT_multisampled_render_to_single_sampled

Tests multisampled rendering to single-sampled framebuffer attachments. Implemented in [`vktPipelineMultisampledRenderToSingleSampledTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L1). Non-VulkanSC only, limited to monolithic, fast-linked-library, and shader_object_unlinked_spirv variants.

### misc — Miscellaneous multisample tests

Additional multisample tests that leverage the multisampled-render-to-single-sampled code. Implemented in [`vktPipelineMultisampledRenderToSingleSampledTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L1). Non-VulkanSC only, same variant restrictions as `multisampled_render_to_single_sampled`.

### sample_locations_ext — VK_EXT_sample_locations

Tests the `VK_EXT_sample_locations` extension. Implemented in [`vktPipelineMultisampleSampleLocationsExtTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L1). Non-VulkanSC only.

### std_sample_locations — Standard sample locations

Tests standard sample locations via `VK_EXT_sample_locations`. Implemented in [`vktPipelineMultisampleSampleLocationsExtTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L1). Non-VulkanSC only, limited to monolithic, fast-linked-library, and shader_object_unlinked_spirv variants.

### mixed_attachment_samples — VK_AMD_mixed_attachment_samples

Tests a graphics pipeline with varying sample count per color and depth/stencil attachments. Implemented in [`vktPipelineMultisampleMixedAttachmentSamplesTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleMixedAttachmentSamplesTests.cpp#L1). Non-VulkanSC only.

### sample_mask_with_depth_test — Sample mask with depth test and post-depth coverage

Tests sample mask behavior with depth testing, including `VK_EXT_post_depth_coverage`. Contains per-sample-count leaf tests with and without post-depth coverage. Non-VulkanSC only.

### m10_resolve — Maintenance10 multisample resolve

Tests multisample resolve with `VK_KHR_maintenance1` features. Contains `resolve_cmd`, `render_pass_resolve`, and `dynamic_render_resolve` subgroups. Implemented in [`vktPipelineMultisampleResolveMaint10Tests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveMaint10Tests.cpp#L1). Non-VulkanSC only, limited to monolithic, fast-linked-library, and shader_object_unlinked_spirv variants, not registered when fragment shading rate is used.

### conservative_with_full_coverage — VK_EXT_conservative_rasterization

Tests sample mask behavior with conservative rasterization. Contains `overestimate` and `underestimate` subgroups, each with per-sample-count and per-config leaf tests. Non-shader-object only.

### compatible_render_pass — Compatible render pass

Tests multisample rendering with compatible render passes. Contains `static` and `dynamic` leaf tests. Non-shader-object only.

### variable_rate — Variable fragment shading rate in subpasses

Tests multisample variable rate in subpasses with `VK_KHR_fragment_shading_rate`. Generates combinations of sample counts across subpasses, including cases with non-empty framebuffers and unused attachments.

### mixed_count — Mixed sample count in empty subpass

Tests mixed sample counts in empty subpasses and framebuffers with `VK_KHR_fragment_shading_rate`. Generates combinations of framebuffer and empty subpass sample counts.

### z_export — VK_EXT_shader_stencil_export with alpha-to-coverage

Tests alpha-to-coverage combined with depth/stencil/mask writes in the fragment shader using `VK_EXT_shader_stencil_export`. Contains leaf tests for depth, stencil, sample_mask, and combined flags, with static/dynamic alpha-to-coverage and render pass variants. Not registered when fragment shading rate is used.

### a2c_with_a2one — Alpha-to-coverage with alpha-to-one

Tests the combination of alpha-to-coverage and alpha-to-one features, including dynamic variants and fragment depth export. Not registered when fragment shading rate is used.

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| VkSampleCountFlagBits | Loop | 1, 2, 4, 8, 16, 32, 64 |
| minSampleShading | Loop | 0.0, 0.25, 0.5, 0.75, 1.0 |
| sampleMask | Loop | 0x0-0xFFFF (bit patterns) |
| Alpha mode | Enum | opaque, translucent, invisible |
| Primitive topology | Enum | triangle, line, point, quad |
| GeometryType | Enum | TRIANGLE, LINE, POINT, QUAD |
| Fragment shading rate | Conditional | 1x1, 1x2, 2x1, 2x2, etc. |
| PipelineConstructionType | Parameter | All variant types |
| useFragmentShadingRate | Bool | false (multisample), true (multisample_with_fragment_shading_rate) |

## Support / Feature Requirements

| Requirement | Context |
|---|---|
| `sampleRateShading` | Core feature for min sample shading and interpolation tests |
| `alphaToOne` | Core feature for alpha-to-one tests |
| `VK_EXT_conservative_rasterization` | Conservative rasterization tests |
| `VK_KHR_fragment_shading_rate` | Variable rate and mixed count rate tests |
| `VK_EXT_shader_stencil_export` | Z-export tests |
| `VK_EXT_post_depth_coverage` | Post-depth coverage sample mask tests |
| `VK_EXT_sample_locations` | Sample location tests |
| `VK_AMD_shader_fragment_mask` | Shader fragment mask tests |
| `VK_AMD_mixed_attachment_samples` | Mixed attachment samples tests |
| `VK_EXT_multisampled_render_to_single_sampled` | Multisampled render to single sampled tests |
| `sparseBinding` / `sparseResidency2Samples` etc. | Sparse resource variants |

## Verification Methods

- **Pixel comparison**: Render to multisample framebuffer, resolve, compare resolved image against expected color values
- **Sample shading verification**: Compare sample-shaded image against non-sample-shaded image to confirm distinct per-sample values
- **Sample mask verification**: Compare test image against minimum sample mask reference image
- **Alpha verification**: Compare alpha-modified image against reference without alpha modification
- **Depth/stencil buffer check**: Read back depth/stencil buffer and verify expected values

## Notes

- This file is the central dispatcher for multisample subgroups; many subgroups are implemented in separate files
- The `multisample_with_fragment_shading_rate` variant repeats most tests with fragment shading rate enabled
- The `m10_resolve` subgroup is only added for monolithic, fast-linked-library, and shader_object_unlinked_spirv variants
- Some subgroups are conditionally registered based on extension support and construction type
