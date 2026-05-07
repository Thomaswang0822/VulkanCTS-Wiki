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

## Registration Path

[`createMultisampleTests()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleTests.cpp#L7247) returns the `multisample` (or `multisample_with_fragment_shading_rate`) group, attached under each variant root by `createChildren()`.

**Variant coverage**: All variants. Called twice — once with `useFragmentShadingRate=false` (group name `multisample`) and once with `useFragmentShadingRate=true` (group name `multisample_with_fragment_shading_rate`).

## Test Hierarchy

```text
multisample
├── raster_samples
│   └── {depth,depth_sparse,stencil,stencil_sparse,color,...}
├── raster_samples_consistency
├── min_sample_shading
│   └── {minSampleShading_value}
│       └── {sample_count}
├── sample_mask
│   └── {sampleMask_value}
│       └── {primitive_type,sparse_variants}
├── alpha_to_one
│   └── {sample_count}
├── alpha_to_coverage
│   └── {alpha_opaque,alpha_translucent,alpha_invisible,sparse_variants}
├── alpha_to_coverage_no_color_attachment
│   └── {sample_count}
├── alpha_to_coverage_color_unused_attachment
│   └── {sample_count}
├── sample_rate_alpha_to_coverage
├── sampled_image                          (from vktPipelineMultisampleImageTests.cpp)
├── 3d                                     (from vktPipelineMultisampleImageTests.cpp)
├── storage_image                          (from vktPipelineMultisampleImageTests.cpp)
├── standardsampleposition                 (from vktPipelineMultisampleImageTests.cpp)
├── samples_mapping_order                  (from vktPipelineMultisampleImageTests.cpp)
├── shader_fragment_mask                   (from vktPipelineMultisampleShaderFragmentMaskTests.cpp)
├── mixed_attachment_samples               (from vktPipelineMultisampleMixedAttachmentSamplesTests.cpp)
├── multisampled_render_to_single_sampled  (from vktPipelineMultisampledRenderToSingleSampledTests.cpp)
├── misc                                   (from vktPipelineMultisampledRenderToSingleSampledTests.cpp)
├── resolve                                (from vktPipelineMultisampleResolveRenderAreaTests.cpp)
│   └── renderpass_renderarea
├── sample_mask_with_depth_test
├── m10_resolve                            (from vktPipelineMultisampleResolveMaint10Tests.cpp, conditional)
├── conservative                           (VK_EXT_conservative_rasterization)
├── compatible_render_pass
├── variable_rate                          (VK_KHR_fragment_shading_rate, conditional)
├── mixed_count_rate                       (VK_KHR_fragment_shading_rate, conditional)
└── z_export                               (VK_EXT_shader_stencil_export, conditional)
```

## Test Families

| Family | Description |
|---|---|
| RasterizationSamplesTest | Verifies correct rendering at each supported sample count (1–16) for color, depth, and stencil aspects |
| RasterSamplesConsistencyTest | Verifies that multisample rendering produces consistent results across sample counts |
| MinSampleShadingTest | Verifies `minSampleShading` behavior with sample rate shading enabled |
| SampleMaskTest | Verifies `sampleMask` correctly masks samples for different primitive types |
| AlphaToOneTest | Verifies `alphaToOneEnable` replaces fragment alpha with 1.0 |
| AlphaToCoverageTest | Verifies `alphaToCoverageEnable` converts fragment alpha to coverage mask |
| AlphaToCoverageNoColorAttachmentTest | Verifies alpha-to-coverage without a color attachment |
| AlphaToCoverageColorUnusedAttachmentTest | Verifies alpha-to-coverage with unused color attachment |
| SampleRateAlphaToCoverageCase | Verifies sample-rate shading combined with alpha-to-coverage |
| VariableRateTestCase | Verifies fragment shading rate interaction with multisampling |
| SampleMaskWithConservativeTest | Verifies sample mask behavior with conservative rasterization |

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| VkSampleCountFlagBits | Loop | 1, 2, 4, 8, 16 |
| minSampleShading | Loop | 0.0, 0.5, 1.0 (and intermediate values) |
| sampleMask | Loop | 0x0–0xFFFF (bit patterns) |
| Alpha mode | Enum | opaque, translucent, invisible |
| Primitive topology | Enum | triangle, line, point |
| GeometryType | Enum | TRIANGLE, LINE, POINT |
| Fragment shading rate | Conditional | 1x1, 1x2, 2x1, 2x2, etc. |
| PipelineConstructionType | Parameter | All variant types |
| useFragmentShadingRate | Bool | false (multisample), true (multisample_with_fragment_shading_rate) |

## Support/Feature Requirements

| Requirement | Context |
|---|---|
| `sampleRateShading` | Core feature for min sample shading and interpolation tests |
| `alphaToOne` | Core feature for alpha-to-one tests |
| `VK_EXT_conservative_rasterization` | Conservative rasterization tests |
| `VK_KHR_fragment_shading_rate` | Variable rate and mixed count rate tests |
| `VK_EXT_shader_stencil_export` | Z-export tests |
| `VK_EXT_post_depth_coverage` | Post-depth coverage sample mask tests |
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
- Some subgroups are conditionally registered based on extension support
