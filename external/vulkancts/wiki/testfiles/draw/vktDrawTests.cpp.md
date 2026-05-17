# vktDrawTests.cpp

## Overview

[`vktDrawTests.cpp`](../../../modules/vulkan/draw/vktDrawTests.cpp#L1) is the root registration file for the draw category. It creates the top-level variant-root structure and dispatches to all topic-group registration functions via the shared [`createChildren()`](../../../modules/vulkan/draw/vktDrawTests.cpp#L70) dispatcher.

## Role

Registration / dispatcher file. Does not implement any test logic directly.

## Source Code

- Primary source: [`vktDrawTests.cpp`](../../../modules/vulkan/draw/vktDrawTests.cpp#L1)
- Header: [`vktDrawTests.hpp`](../../../modules/vulkan/draw/vktDrawTests.hpp#L1)
- Shared parameters: [`vktDrawGroupParams.hpp`](../../../modules/vulkan/draw/vktDrawGroupParams.hpp#L1)

## Registration Hierarchy

```text
draw
├── renderpass
└── dynamic_rendering (non-VulkanSC only)
```

Source: [`createTests()`](../../../modules/vulkan/draw/vktDrawTests.cpp#L126).

### Variant-Root Architecture

The draw category uses a variant-root structure with two top-level branches:

| Variant root | Mustpass file | Always present | Sub-variants |
|---|---|---|---|
| `renderpass` | `draw.txt` | Yes (VK + VKSC) | None |
| `dynamic_rendering` | `dynamic-rendering/` | No (VK only) | 5 sub-variants |

The `dynamic_rendering` branch further contains 5 sub-variants:

```text
draw.dynamic_rendering
├── primary_cmd_buff
├── partial_secondary_cmd_buff
├── complete_secondary_cmd_buff
├── nested_partial_secondary_cmd_buff
└── nested_complete_secondary_cmd_buff
```

Source: [`createTests()`](../../../modules/vulkan/draw/vktDrawTests.cpp#L126) through [`vktDrawTests.cpp#L199`](../../../modules/vulkan/draw/vktDrawTests.cpp#L199).

### SharedGroupParams

Each variant root and sub-variant is configured with a [`GroupParams`](../../../modules/vulkan/draw/vktDrawGroupParams.hpp#L1) struct controlling:

| Field | renderpass | primary_cmd_buff | partial_secondary_cmd_buff | complete_secondary_cmd_buff | nested_partial | nested_complete |
|---|---|---|---|---|---|---|
| `useDynamicRendering` | false | true | true | true | true | true |
| `useSecondaryCmdBuffer` | false | false | true | true | true | true |
| `secondaryCmdBufferCompletelyContainsDynamicRenderpass` | false | false | false | true | false | true |
| `nestedSecondaryCmdBuffer` | false | false | false | false | true | true |

## Topic-Group Registration Matrix

The shared dispatcher [`createChildren()`](../../../modules/vulkan/draw/vktDrawTests.cpp#L70) adds topic groups to each variant root. The following table shows each topic group's variant coverage:

| Topic group | Registration function | Renderpass | Dynamic rendering sub-variants | VKSC | Condition |
|---|---|---|---|---|---|
| `concurrent` | `ConcurrentDrawTests` | Yes | Not nested only | Available | — |
| `simple_draw` | `SimpleDrawTests` | Yes | Not nested only | Available | — |
| `indexed_draw` | `DrawIndexedTests` | Yes | Not nested only | Available | — |
| `indirect_draw` | `IndirectDrawTests` | Yes | Not nested only | Available | — |
| `basic_draw` | `createBasicDrawTests` | Yes | All (including nested) | Available | — |
| `instanced` | `InstancedTests` | Yes | Not nested only | Available | — |
| `shader_draw_parameters` | `ShaderDrawParametersTests` | Yes | Not nested only | Available | — |
| `negative_viewport_height` | `createNegativeViewportHeightTests` | Yes | Not nested only | Available | — |
| `zero_viewport_height` | `createZeroViewportHeightTests` | Yes | Not nested only | Available | — |
| `offscreen_viewport` | `createOffScreenViewportTests` | Yes | Not nested only | Available | — |
| `inverted_depth_ranges` | `createInvertedDepthRangesTests` | Yes | Not nested only | Available | — |
| `differing_interpolation` | `createDifferingInterpolationTests` | Yes | Not nested only | Available | — |
| `shader_layer` | `createShaderLayerTests` | Yes | Not nested only | Available | — |
| `shader_viewport_index` | `createShaderViewportIndexTests` | Yes | Not nested only | Available | — |
| `scissor` | `createScissorTests` | Yes | Not nested only | Available | — |
| `multiple_interpolation` | `createMultipleInterpolationTests` | Yes | Not nested only | Available | — |
| `linear_interpolation` | `createMultisampleLinearInterpolationTests` | Yes | Not nested only | Available | — |
| `discard_rectangles` | `createDiscardRectanglesTests` | Yes | Not nested only | Available | — |
| `explicit_vertex_parameter` | `createExplicitVertexParameterTests` | Yes | Not nested only | Available | — |
| `depth_clamp` | `createDepthClampTests` | Yes | Not nested only | Available | — |
| `multiple_clears_within_render_pass` | `MultipleClearsWithinRenderPassTests` | Yes | Not nested only | Available | — |
| `implicit_sample_shading` | `createSampleAttributeTests` | Yes | Not nested only | Available | — |
| `vertex_attribute_divisor` | `createVertexAttributeDivisorTests` | Yes | Not nested only | Available | — |
| `indirect_instanced` | `createIndirectInstancedTests` | Yes | Not nested only | Available | — |
| `multi_draw` | `createDrawMultiExtTests` | Yes | Not nested only | VK only | `!CTS_USES_VULKANSC` |
| `depth_bias` | `createDepthBiasTests` | Yes | No | VK only | `!CTS_USES_VULKANSC` and `!useDynamicRendering` |
| `output_location` | `createOutputLocationTests` | Yes | No | VK only | `!CTS_USES_VULKANSC` and `!useDynamicRendering` |
| `shader_invocation` | `createShaderInvocationTests` | Yes | No | VK only | `!CTS_USES_VULKANSC` and `!useDynamicRendering` |
| `ahb` | `createAhbTests` | Yes | No | VK only | `!CTS_USES_VULKANSC` and `!useDynamicRendering` |
| `non_line_with_params` | `createDrawNonLineTests` | Yes | No | VK only | `!CTS_USES_VULKANSC` and `!useDynamicRendering` |
| `ahb_external_format_resolve` | `createAhbExternalFormatResolveTests` | Yes | Not nested only | VK only | `!CTS_USES_VULKANSC` |
| `point_size_clamp` | `createDrawPointClampTests` | Yes | No | Available | Added directly to renderpass only |

Source: [`createChildren()`](../../../modules/vulkan/draw/vktDrawTests.cpp#L70) through [`vktDrawTests.cpp#L121`](../../../modules/vulkan/draw/vktDrawTests.cpp#L121).

## Notes

- "Not nested only" means the group is excluded from `nested_partial_secondary_cmd_buff` and `nested_complete_secondary_cmd_buff` sub-variants (gated by `!groupParams->nestedSecondaryCmdBuffer`).
- `basic_draw` is the only topic group present in ALL variants including nested ones.
- `point_size_clamp` is added directly to the `renderpass` group outside of `createChildren()`, so it only appears under `draw.renderpass`.
- No VK-only group appears in nested dynamic rendering sub-variants; all VK-only groups are gated by either `!useDynamicRendering` or `!nestedSecondaryCmdBuffer`.
