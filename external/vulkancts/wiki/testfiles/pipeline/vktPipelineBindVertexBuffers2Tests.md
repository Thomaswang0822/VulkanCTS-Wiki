# vktPipelineBindVertexBuffers2Tests.cpp

## Overview

[`vktPipelineBindVertexBuffers2Tests.cpp`](../../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp#L1) implements the [`bind_buffers_2`](../../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp#L1786) topic group and its nested subgroups. It verifies VK_KHR_dynamic_rendering and related functionality for `vkCmdBindVertexBuffers2`, testing dynamic vertex buffer binding with partial updates, stride changes, and size limits.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineBindVertexBuffers2Tests.cpp`](../../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp#L1)
- Header: [`vktPipelineBindVertexBuffers2Tests.hpp`](../../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.hpp#L1)

## Registration Hierarchy

```text
pipeline.monolithic.bind_buffers_2
├── single
├── separate
├── dynamic_stride (monolithic only)
└── maintenance5 (non-VulkanSC only)
```

Source: [`createCmdBindBuffers2Tests()`](../../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp#L1783).

## Test Families

### single — Single-bind vertex buffer stride and count tests

Tests `vkCmdBindVertexBuffers2` with all vertex buffers bound in a single call. Each stride variant (e.g., `stride_0_4_offset_0_0`, `stride_4_4_offset_0_0`, `stride_5_8_offset_15_22`, etc.) forms a subgroup containing leaf test cases for binding counts 1 through 4 (`count_1` through `count_4`).

### separate — Separate-bind vertex buffer stride and count tests

Tests `vkCmdBindVertexBuffers2` with vertex buffers bound in separate calls. Same internal structure as `single`, with stride subgroups containing count leaf test cases. Verifies that per-binding dynamic state changes work correctly when bindings are issued independently.

### dynamic_stride — Dynamic stride mismatch tests (monolithic only)

Tests dynamic stride mismatch behavior with `vkCmdBindVertexBuffers2`. Contains the `binding_stride_index_mismatch` test case, which verifies that stride mismatches between the pipeline and dynamic binding state are handled correctly. Only registered under the monolithic pipeline construction type.

### maintenance5 — VK_KHR_maintenance5 vertex buffer tests (non-VulkanSC only)

Tests added via [`createCmdBindVertexBuffers2Tests()`](../../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp#L1907) for VK_KHR_maintenance5 functionality. Contains two main subgroups: a topology-based group (with `triangle_list` and `triangle_strip` subgroups, each containing buffer-count and random-seed leaf cases) and a `robustness2` group (same topology structure with additional `whole_size`/`true_size` and `beyond_buffer`/`beyond_size` subgroups for robustness testing). Only registered on non-VulkanSC builds.

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| PipelineConstructionType | Parameter | All variant types |
| Binding mode | Struct | `single` (one bind call), `separate` (per-binding calls) |
| Stride/offset | Struct array | 7 stride+offset combinations |
| Binding count | Array | 1, 2, 3, 4 |
| Topology | Pair array | triangle_list, triangle_strip |
| Buffer count | Array | 5, 9 |
| Random seed | Array | 321, 432 (normal), 543, 654 (robustness) |
| Size mode | Pair array | whole_size, true_size |
| Beyond type | Pair array | beyond_buffer, beyond_size |

## Support / Feature Requirements

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
