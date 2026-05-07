# vktPipelineStencilExportTests.cpp

## Overview

[`vktPipelineStencilExportTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineStencilExportTests.cpp#L1) implements the [`shader_stencil_export`](../../../modules/vulkan/pipeline/vktPipelineStencilExportTests.cpp#L636) topic group. It verifies VK_EXT_shader_stencil_export functionality, testing that fragment shaders can write to the stencil attachment using `gl_FragStencilRefEXT`.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineStencilExportTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineStencilExportTests.cpp#L1)
- Header: [`vktPipelineStencilExportTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineStencilExportTests.hpp#L1)

## Registration Path

[`createStencilExportTests()`](../../../modules/vulkan/pipeline/vktPipelineStencilExportTests.cpp#L634) returns the `shader_stencil_export` group, attached under each variant root by `createChildren()`.

**Variant coverage**: All variants.

## Test Hierarchy

```text
shader_stencil_export
└── {test_case}
```

## Test Families

| Family | Description |
|---|---|
| StencilExportTest | Verifies that fragment shader stencil export writes correct stencil values |

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| Stencil reference value | Array | Various stencil reference values |
| Depth/stencil format | Enum | D24_UNORM_S8_UINT, D32_SFLOAT_S8_UINT, etc. |
| PipelineConstructionType | Parameter | All variant types |

## Support/Feature Requirements

| Requirement | Context |
|---|---|
| `VK_EXT_shader_stencil_export` | Primary extension for all tests |

## Verification Methods

- **Stencil buffer comparison**: Render with shader stencil export, read back stencil buffer, compare against expected values
- **Reference value verification**: Verify that `gl_FragStencilRefEXT` correctly sets the stencil reference

## Notes

- The shader stencil export extension allows fragment shaders to dynamically set the stencil reference value
