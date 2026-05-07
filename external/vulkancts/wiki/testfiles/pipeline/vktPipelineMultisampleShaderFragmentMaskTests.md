# vktPipelineMultisampleShaderFragmentMaskTests.cpp

## Overview

[`vktPipelineMultisampleShaderFragmentMaskTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderFragmentMaskTests.cpp#L1) implements the [`shader_fragment_mask`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderFragmentMaskTests.cpp#L1401) topic group under `multisample`. It verifies VK_AMD_shader_fragment_mask functionality, testing access to fragment mask data in compressed multisample surfaces.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineMultisampleShaderFragmentMaskTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderFragmentMaskTests.cpp#L1)
- Header: [`vktPipelineMultisampleShaderFragmentMaskTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderFragmentMaskTests.hpp#L1)

## Registration Path

[`createMultisampleShaderFragmentMaskTests()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderFragmentMaskTests.cpp#L1399) returns the `shader_fragment_mask` group, added to the `multisample` group by `createMultisampleTests()`.

**Variant coverage**: All variants (conditional on VK_AMD_shader_fragment_mask support).

## Test Hierarchy

```text
shader_fragment_mask
└── {sample_count}
    └── {source_type}
```

## Test Families

| Family | Description |
|---|---|
| Fragment mask test | Verifies that fragment mask data accessed via VK_AMD_shader_fragment_mask matches expected values from FMASK |

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| Sample count | Array | 2, 4, 8 |
| Source type | Enum | Various texture source configurations |
| PipelineConstructionType | Parameter | All variant types |

## Support/Feature Requirements

| Requirement | Context |
|---|---|
| `VK_AMD_shader_fragment_mask` | Primary extension for all tests |

## Verification Methods

- **FMASK comparison**: Compare fragments fetched via FMASK against ordinary texel fetch to verify fragment mask correctness
- **Compute shader verification**: Use compute shader to read fragment mask data and compare against expected values

## Notes

- Uses a singleton device pattern due to extension-specific device configuration requirements
- The extension is AMD-specific and may not be available on all implementations
