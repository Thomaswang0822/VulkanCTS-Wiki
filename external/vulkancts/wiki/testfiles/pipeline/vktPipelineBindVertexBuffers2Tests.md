# vktPipelineBindVertexBuffers2Tests.cpp

## Overview

[`vktPipelineBindVertexBuffers2Tests.cpp`](../../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp#L1) implements the [`bind_buffers_2`](../../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp#L1786) topic group and its nested subgroups. It verifies VK_KHR_dynamic_rendering and related functionality for `vkCmdBindVertexBuffers2`, testing dynamic vertex buffer binding with partial updates, stride changes, and size limits.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineBindVertexBuffers2Tests.cpp`](../../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp#L1)
- Header: [`vktPipelineBindVertexBuffers2Tests.hpp`](../../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.hpp#L1)

## Registration Path

[`createBindVertexBuffers2Tests()`](../../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp#L1785) returns the `bind_buffers_2` group and nested subgroups, attached under each variant root by `createChildren()`.

**Variant coverage**: All variants.

## Test Hierarchy

```text
bind_buffers_2
└── {test_case}
```

## Test Families

| Family | Description |
|---|---|
| BindVertexBuffers2Test | Verifies `vkCmdBindVertexBuffers2` with dynamic vertex buffer binding |

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| PipelineConstructionType | Parameter | All variant types |
| Binding count | Array | 1, 2, 4 |
| Stride | Array | Various vertex strides |
| Size | Array | Full, partial buffer sizes |
| Offset | Array | 0, non-zero offsets |

## Support/Feature Requirements

| Requirement | Context |
|---|---|
| `VK_KHR_dynamic_rendering` | Required for dynamic rendering tests |
| `VK_EXT_extended_dynamic_state` | Required for extended dynamic state tests |

## Verification Methods

- **Rendering verification**: Bind vertex buffers dynamically, render, compare against expected output
- **Partial update verification**: Verify that partial vertex buffer updates work correctly
- **Stride verification**: Verify that dynamic stride changes produce correct vertex data

## Notes

- The `bind_buffers_2` group and its nested subgroups are registered at the variant root level
