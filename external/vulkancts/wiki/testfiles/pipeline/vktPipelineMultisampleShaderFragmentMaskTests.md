# vktPipelineMultisampleShaderFragmentMaskTests.cpp

## Overview

[`vktPipelineMultisampleShaderFragmentMaskTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderFragmentMaskTests.cpp#L1) implements the [`shader_fragment_mask`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderFragmentMaskTests.cpp#L1401) topic group under `multisample`. It verifies VK_AMD_shader_fragment_mask functionality, testing access to fragment mask data in compressed multisample surfaces.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineMultisampleShaderFragmentMaskTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderFragmentMaskTests.cpp#L1)
- Header: [`vktPipelineMultisampleShaderFragmentMaskTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderFragmentMaskTests.hpp#L1)

## Registration Hierarchy

[`createMultisampleShaderFragmentMaskTests()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderFragmentMaskTests.cpp#L1399) returns the `shader_fragment_mask` group, added to the `multisample` group by `createMultisampleTests()`. All variants are conditional on VK_AMD_shader_fragment_mask support.

```text
pipeline.monolithic.multisample.shader_fragment_mask
├── samples_2
├── samples_4
├── samples_8
└── samples_16
```

## Test Families

### samples_2 — 2-sample fragment mask tests

Tests for multisample surfaces with 2 samples. Each source type subgroup (`image_2d`, `image_2d_array`, `subpass_input`) contains format-specific test cases for `r8g8b8a8_unorm`, `r32_uint`, and `r32_sint`. The `subpass_input` source is excluded for shader-object pipeline construction types.

### samples_4 — 4-sample fragment mask tests

Tests for multisample surfaces with 4 samples. Same source type and format structure as `samples_2`.

### samples_8 — 8-sample fragment mask tests

Tests for multisample surfaces with 8 samples. Same source type and format structure as `samples_2`.

### samples_16 — 16-sample fragment mask tests

Tests for multisample surfaces with 16 samples. Same source type and format structure as `samples_2`.

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| Sample count | Array | 2, 4, 8, 16 |
| Source type | Enum | image_2d, image_2d_array, subpass_input |
| Color format | Enum | R8G8B8A8_UNORM, R32_UINT, R32_SINT |
| PipelineConstructionType | Parameter | All variant types |

## Support / Feature Requirements

| Requirement | Context |
|---|---|
| `VK_AMD_shader_fragment_mask` | Primary extension for all tests |

## Verification Methods

- **FMASK comparison**: Compare fragments fetched via FMASK against ordinary texel fetch to verify fragment mask correctness
- **Compute shader verification**: Use compute shader to read fragment mask data and compare against expected values

## Notes

- Uses a singleton device pattern due to extension-specific device configuration requirements
- The extension is AMD-specific and may not be available on all implementations
