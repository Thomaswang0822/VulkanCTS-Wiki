# vktPipelineMultisampleShaderBuiltInTests.cpp

## Overview

[`vktPipelineMultisampleShaderBuiltInTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderBuiltInTests.cpp#L1) implements the [`multisample_shader_builtin`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderBuiltInTests.cpp#L2231) topic group. It verifies multisample shader built-in variables including `gl_SampleID`, `gl_SamplePosition`, `gl_SampleMask`, and image write/sample operations using these built-ins.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineMultisampleShaderBuiltInTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderBuiltInTests.cpp#L1)
- Header: [`vktPipelineMultisampleShaderBuiltInTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderBuiltInTests.hpp#L1)
- Base classes: [`vktPipelineMultisampleBase.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleBase.cpp#L1)

## Registration Path

[`createMultisampleShaderBuiltinTests()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderBuiltInTests.cpp#L2230) returns the `multisample_shader_builtin` group, attached under each variant root by `createChildren()`.

**Variant coverage**: Not shader-object, VK only. Input attachments are not supported for dynamic rendering/shader objects.

## Test Hierarchy

```text
multisample_shader_builtin
├── sample_id
├── sample_position
│   ├── distribution
│   └── correctness
├── sample_mask
│   ├── pattern
│   ├── bit_count_zero
│   ├── bit_count_max
│   ├── correct_bit
│   └── write
├── image_write_sample              (conditional: graphicsPipelineLibrary support)
│   └── {sample_count}_samples
└── write_sample_mask               (conditional: graphicsPipelineLibrary support)
    └── {sample_count}_samples
```

## Test Families

| Family | Description |
|---|---|
| MSCaseSampleID | Verifies `gl_SampleID` returns correct sample index per invocation |
| MSCaseSamplePosDistribution | Verifies `gl_SamplePosition` values are distributed across the pixel |
| MSCaseSamplePosCorrectness | Verifies `gl_SamplePosition` values match expected sample locations |
| MSCaseSampleMaskPattern | Verifies `gl_SampleMaskIn` reflects the correct coverage pattern |
| MSCaseSampleMaskBitCount | Verifies `gl_SampleMaskIn` has correct bit count for zero/max masks |
| MSCaseSampleMaskCorrectBit | Verifies `gl_SampleMaskIn` bits correspond to covered samples |
| MSCaseSampleMaskWrite | Verifies writing to `gl_SampleMaskOut` correctly masks output samples |
| WriteSampleTest | Verifies per-sample image writes using `gl_SampleID` |
| WriteSampleMaskTest | Verifies per-sample writes using `gl_SampleMask` |

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| Image size | Array | 128x128, 256x256, 512x512 |
| Sample count | Array | 2, 4, 8, 16 (full set) |
| PipelineConstructionType | Parameter | All variant types |

## Support/Feature Requirements

| Requirement | Context |
|---|---|
| `sampleRateShading` | Core feature required for all shader built-in tests |
| `graphicsPipelineLibrary` | Required for `image_write_sample` and `write_sample_mask` subgroups |

## Verification Methods

- **Pixel value check**: Render with shader built-ins, read back resolved image, compare against expected values
- **Distribution check**: Verify `gl_SamplePosition` values span the expected range across samples
- **Bit pattern check**: Verify `gl_SampleMaskIn/Out` bits match expected coverage
- **Per-sample image write**: Verify that per-sample writes using `gl_SampleID` produce correct results in a storage image

## Notes

- The `image_write_sample` and `write_sample_mask` subgroups are only added when the implementation supports graphics pipeline library
- This file is excluded from shader-object variants because input attachments are not supported for dynamic rendering/shader objects
