# vktPipelineMultisampleShaderBuiltInTests.cpp

## Overview

[`vktPipelineMultisampleShaderBuiltInTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderBuiltInTests.cpp#L1) implements the [`multisample_shader_builtin`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderBuiltInTests.cpp#L2231) topic group. It verifies multisample shader built-in variables including `gl_SampleID`, `gl_SamplePosition`, `gl_SampleMask`, and image write/sample operations using these built-ins.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineMultisampleShaderBuiltInTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderBuiltInTests.cpp#L1)
- Header: [`vktPipelineMultisampleShaderBuiltInTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderBuiltInTests.hpp#L1)
- Base classes: [`vktPipelineMultisampleBase.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleBase.cpp#L1)

## Registration Hierarchy

```text
pipeline.monolithic.multisample_shader_builtin
├── sample_id
├── sample_position
├── sample_mask
├── image_write_sample (monolithic only)
└── write_sample_mask
```

## Test Families

### sample_id — gl_SampleID verification

Verifies that `gl_SampleID` returns the correct sample index per invocation. The fragment shader writes `gl_SampleID` to the red channel of the texture, and the test verifies that value N appears at sample index N of a multisample texture.

### sample_position — gl_SamplePosition verification

Contains two sub-tests:

- **distribution**: Verifies that `gl_SamplePosition` values are distributed across the pixel. Checks that positions are unique within the set of all sample positions of a pixel, that positions fall within the [0,1] interval, and that the distribution is uniform or almost uniform.
- **correctness**: Verifies that `gl_SamplePosition` values match expected sample locations. Confirms that varying values are sampled at the sample position by checking `fract(position_screen) == gl_SamplePosition`.

### sample_mask — gl_SampleMaskIn/Out verification

Contains five sub-tests:

- **pattern**: Verifies that `gl_SampleMaskIn` reflects the correct coverage pattern set by `pSampleMask` state. Confirms that `gl_SampleMaskIn AND ~(pSampleMask)` is zero.
- **bit_count**: Verifies that `gl_SampleMaskIn` has the correct bit count for the shading rate. The fragment shader is invoked numSamples times, and the bit count should depend on the shading rate.
- **bit_count_0_5**: Same as `bit_count` but with a 0.5 min sample shading rate.
- **correct_bit**: Verifies that `gl_SampleMaskIn` bits correspond to covered samples. In each invocation, the bit corresponding to `gl_SampleID` should be set in `gl_SampleMaskIn`.
- **write**: Verifies writing to `gl_SampleMaskOut` correctly masks output samples. Discards half of the samples using `gl_SampleMask` and expects half intensity on the resolved image.

### image_write_sample — Per-sample image write using gl_SampleID (monolithic only)

Verifies per-sample image writes using `gl_SampleID` with storage images. Uses compute pipelines to write to and verify a multisample storage image. Only available when `pipelineConstructionType` is monolithic. Contains per-sample-count test cases (2, 4, 8, 16 samples).

### write_sample_mask — Per-sample write using gl_SampleMask

Verifies per-sample writes using `gl_SampleMask` with a render pass containing two subpasses: one that writes to the color attachment with a sample mask, and one that reads back via input attachment to verify the result. Contains per-sample-count test cases (1, 2, 4, 8, 16 samples).

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| Image size | Array | 128x128, 137x191 |
| Sample count | Array | 2, 4, 8, 16, 32, 64 (full set); 2, 4, 8, 16, 32 (reduced set) |
| PipelineConstructionType | Parameter | All variant types |

## Support / Feature Requirements

| Requirement | Context |
|---|---|
| `sampleRateShading` | Core feature required for all shader built-in tests |
| `graphicsPipelineLibrary` | Required for `image_write_sample` and `write_sample_mask` subgroups |
| `shaderStorageImageMultisample` | Required for `image_write_sample` subgroup |

## Verification Methods

- **Pixel value check**: Render with shader built-ins, read back resolved image, compare against expected values
- **Distribution check**: Verify `gl_SamplePosition` values span the expected range across samples
- **Bit pattern check**: Verify `gl_SampleMaskIn/Out` bits match expected coverage
- **Per-sample image write**: Verify that per-sample writes using `gl_SampleID` produce correct results in a storage image

## Notes

- The `image_write_sample` subgroup is only added when `pipelineConstructionType` is monolithic
- The `write_sample_mask` subgroup is added for all pipeline construction types
- This file is excluded from shader-object variants because input attachments are not supported for dynamic rendering/shader objects
