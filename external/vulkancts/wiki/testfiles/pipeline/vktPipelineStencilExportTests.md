# vktPipelineStencilExportTests.cpp

## Overview

[`vktPipelineStencilExportTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineStencilExportTests.cpp#L1) implements the [`shader_stencil_export`](../../../modules/vulkan/pipeline/vktPipelineStencilExportTests.cpp#L636) topic group. It verifies VK_EXT_shader_stencil_export functionality, testing that fragment shaders can write to the stencil attachment using `gl_FragStencilRefEXT`.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineStencilExportTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineStencilExportTests.cpp#L1)
- Header: [`vktPipelineStencilExportTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineStencilExportTests.hpp#L1)

## Registration Hierarchy

```text
pipeline.monolithic.shader_stencil_export
├── s8_uint
├── d24_unorm_s8_uint
└── d32_sfloat_s8_uint
```

## Test Families

### s8_uint — Stencil export with S8_UINT format

Tests shader stencil export with the VK_FORMAT_S8_UINT depth/stencil format. Includes `op_replace` and `op_replace_early_and_late` (non-VulkanSC only) test cases.

### d24_unorm_s8_uint — Stencil export with D24_UNORM_S8_UINT format

Tests shader stencil export with the VK_FORMAT_D24_UNORM_S8_UINT depth/stencil format. Includes `op_replace` and `op_replace_early_and_late` (non-VulkanSC only) test cases.

### d32_sfloat_s8_uint — Stencil export with D32_SFLOAT_S8_UINT format

Tests shader stencil export with the VK_FORMAT_D32_SFLOAT_S8_UINT depth/stencil format. Includes `op_replace` and `op_replace_early_and_late` (non-VulkanSC only) test cases.

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| Stencil reference value | Array | Various stencil reference values |
| Depth/stencil format | Enum | D24_UNORM_S8_UINT, D32_SFLOAT_S8_UINT, etc. |
| PipelineConstructionType | Parameter | All variant types |

## Support / Feature Requirements

| Requirement | Context |
|---|---|
| `VK_EXT_shader_stencil_export` | Primary extension for all tests |

## Verification Methods

- **Stencil buffer comparison**: Render with shader stencil export, read back stencil buffer, compare against expected values
- **Reference value verification**: Verify that `gl_FragStencilRefEXT` correctly sets the stencil reference

## Notes

- The shader stencil export extension allows fragment shaders to dynamically set the stencil reference value
