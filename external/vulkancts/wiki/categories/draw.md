# Draw Tests

## Overview

The [`draw`](../../modules/vulkan/draw/vktDrawTests.cpp#L126) category tests Vulkan draw commands and their interactions with rendering state. It verifies that draw parameters (vertex input, instancing, indexing, indirect buffers) are respected, that viewport and scissor transformations produce correct results, and that extension-gated features (discard rectangles, vertex attribute divisor, multi-draw, AHB external format) integrate correctly with the draw pipeline.

As stated in the [test plan](../../../../doc/testspecs/VK/apitests.adoc#L674): "Draw command tests verify that all draw parameters are respected (including vertex input state) and various draw call sizes work correctly."

## Registration Entry Point

The category is rooted in [`createTests()`](../../modules/vulkan/draw/vktDrawTests.cpp#L126), which creates two direct children under `draw`:

```text
draw
├── renderpass                              (VK + VKSC)
└── dynamic_rendering                       (VK only)
```

Source: [`createTests()`](../../modules/vulkan/draw/vktDrawTests.cpp#L126).

## Variant-Root Architecture

Unlike most categories where each source file registers under one flat group, the draw category uses a two-axis structure:

- **Variant root axis**: `renderpass` (always present) and `dynamic_rendering` (VK only, with 5 sub-variants)
- **Topic group axis**: Content groups registered under each variant root by [`createChildren()`](../../modules/vulkan/draw/vktDrawTests.cpp#L70)

### Variant Root to Mustpass Mapping

Both variant roots are in the **same** `draw.txt` mustpass file:

| Variant root | Mustpass file | Sub-variants |
|---|---|---|
| `renderpass` | `draw.txt` | None |
| `dynamic_rendering` | `draw.txt` | `primary_cmd_buff`, `partial_secondary_cmd_buff`, `complete_secondary_cmd_buff`, `nested_partial_secondary_cmd_buff`, `nested_complete_secondary_cmd_buff` |

### SharedGroupParams

Each variant is configured with [`GroupParams`](../../modules/vulkan/draw/vktDrawGroupParams.hpp#L1) controlling rendering mode and command buffer usage:

| Parameter | renderpass | primary_cmd_buff | partial_secondary | complete_secondary | nested_partial | nested_complete |
|---|---|---|---|---|---|---|
| `useDynamicRendering` | false | true | true | true | true | true |
| `useSecondaryCmdBuffer` | false | false | true | true | true | true |
| `secondaryCmdBufferCompletelyContainsDynamicRenderpass` | false | false | false | true | false | true |
| `nestedSecondaryCmdBuffer` | false | false | false | false | true | true |

## Topic-Group Registration Matrix

The following table shows each topic group's variant coverage, verified against [`createChildren()`](../../modules/vulkan/draw/vktDrawTests.cpp#L70).

| Topic group | Condition | VKSC | Level-3 doc |
|---|---|---|---|
| `basic_draw` | All variants (including nested) | Available | [vktBasicDrawTests.cpp](../testfiles/draw/vktBasicDrawTests.md) |
| `simple_draw` | Not nested | Available | [vktDrawSimpleTest.cpp](../testfiles/draw/vktDrawSimpleTest.md) |
| `concurrent` | Not nested | Available | [vktDrawConcurrentTests.cpp](../testfiles/draw/vktDrawConcurrentTests.md) |
| `indexed_draw` | Not nested | Available | [vktDrawIndexedTest.cpp](../testfiles/draw/vktDrawIndexedTest.md) |
| `indirect_draw` | Not nested | Available | [vktDrawIndirectTest.cpp](../testfiles/draw/vktDrawIndirectTest.md) |
| `instanced` | Not nested | Available | [vktDrawInstancedTests.cpp](../testfiles/draw/vktDrawInstancedTests.md) |
| `shader_draw_parameters` | Not nested | Available | [vktDrawShaderDrawParametersTests.cpp](../testfiles/draw/vktDrawShaderDrawParametersTests.md) |
| `negative_viewport_height` | Not nested | Available | [vktDrawNegativeViewportHeightTests.cpp](../testfiles/draw/vktDrawNegativeViewportHeightTests.md) |
| `zero_viewport_height` | Not nested | Available | [vktDrawNegativeViewportHeightTests.cpp](../testfiles/draw/vktDrawNegativeViewportHeightTests.md) |
| `offscreen_viewport` | Not nested | Available | [vktDrawNegativeViewportHeightTests.cpp](../testfiles/draw/vktDrawNegativeViewportHeightTests.md) |
| `inverted_depth_ranges` | Not nested | Available | [vktDrawInvertedDepthRangesTests.cpp](../testfiles/draw/vktDrawInvertedDepthRangesTests.md) |
| `differing_interpolation` | Not nested | Available | [vktDrawDifferingInterpolationTests.cpp](../testfiles/draw/vktDrawDifferingInterpolationTests.md) |
| `shader_layer` | Not nested | Available | [vktDrawShaderLayerTests.cpp](../testfiles/draw/vktDrawShaderLayerTests.md) |
| `shader_viewport_index` | Not nested | Available | [vktDrawShaderViewportIndexTests.cpp](../testfiles/draw/vktDrawShaderViewportIndexTests.md) |
| `scissor` | Not nested | Available | [vktDrawScissorTests.cpp](../testfiles/draw/vktDrawScissorTests.md) |
| `multiple_interpolation` | Not nested | Available | [vktDrawMultipleInterpolationTests.cpp](../testfiles/draw/vktDrawMultipleInterpolationTests.md) |
| `linear_interpolation` | Not nested | Available | [vktDrawMultisampleLinearInterpolationTests.cpp](../testfiles/draw/vktDrawMultisampleLinearInterpolationTests.md) |
| `discard_rectangles` | Not nested | Available | [vktDrawDiscardRectanglesTests.cpp](../testfiles/draw/vktDrawDiscardRectanglesTests.md) |
| `explicit_vertex_parameter` | Not nested | Available | [vktDrawExplicitVertexParameterTests.cpp](../testfiles/draw/vktDrawExplicitVertexParameterTests.md) |
| `depth_clamp` | Not nested | Available | [vktDrawDepthClampTests.cpp](../testfiles/draw/vktDrawDepthClampTests.md) |
| `multiple_clears_within_render_pass` | Not nested | Available | [vktDrawMultipleClearsWithinRenderPass.cpp](../testfiles/draw/vktDrawMultipleClearsWithinRenderPass.md) |
| `implicit_sample_shading` | Not nested | Available | [vktDrawSampleAttributeTests.cpp](../testfiles/draw/vktDrawSampleAttributeTests.md) |
| `vertex_attribute_divisor` | Not nested | Available | [vktDrawVertexAttribDivisorTests.cpp](../testfiles/draw/vktDrawVertexAttribDivisorTests.md) |
| `indirect_instanced` | Not nested | Available | [vktDrawIndirectInstancedTests.cpp](../testfiles/draw/vktDrawIndirectInstancedTests.md) |
| `multi_draw` | Not nested, VK only | N/A | [vktDrawMultiExtTests.cpp](../testfiles/draw/vktDrawMultiExtTests.md) |
| `depth_bias` | Renderpass-only, VK only | N/A | [vktDrawDepthBiasTests.cpp](../testfiles/draw/vktDrawDepthBiasTests.md) |
| `output_location` | Renderpass-only, VK only | N/A | [vktDrawOutputLocationTests.cpp](../testfiles/draw/vktDrawOutputLocationTests.md) |
| `shader_invocation` | Renderpass-only, VK only | N/A | [vktDrawShaderInvocationTests.cpp](../testfiles/draw/vktDrawShaderInvocationTests.md) |
| `ahb` | Renderpass-only, VK only | N/A | [vktDrawAhbTests.cpp](../testfiles/draw/vktDrawAhbTests.md) |
| `non_line_with_params` | Renderpass-only, VK only | N/A | [vktDrawNonLineTests.cpp](../testfiles/draw/vktDrawNonLineTests.md) |
| `ahb_external_format_resolve` | Not nested, VK only | N/A | [vktDrawAhbExternalFormatResolveTests.cpp](../testfiles/draw/vktDrawAhbExternalFormatResolveTests.md) |
| `point_size_clamp` | Renderpass-only | Available | [vktDrawPointClampTests.cpp](../testfiles/draw/vktDrawPointClampTests.md) |

## File Inventory

### Registration Files

| File | Role |
|---|---|
| [`vktDrawTests.cpp`](../../modules/vulkan/draw/vktDrawTests.cpp#L1) | Root dispatcher; creates variant roots and delegates to `createChildren()` |

### Implementation Files

| File | Topic group(s) |
|---|---|
| [`vktBasicDrawTests.cpp`](../../modules/vulkan/draw/vktBasicDrawTests.cpp#L1) | `basic_draw` |
| [`vktDrawSimpleTest.cpp`](../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L1) | `simple_draw` |
| [`vktDrawConcurrentTests.cpp`](../../modules/vulkan/draw/vktDrawConcurrentTests.cpp#L1) | `concurrent` |
| [`vktDrawIndexedTest.cpp`](../../modules/vulkan/draw/vktDrawIndexedTest.cpp#L1) | `indexed_draw` |
| [`vktDrawIndirectTest.cpp`](../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L1) | `indirect_draw` |
| [`vktDrawInstancedTests.cpp`](../../modules/vulkan/draw/vktDrawInstancedTests.cpp#L1) | `instanced` |
| [`vktDrawShaderDrawParametersTests.cpp`](../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp#L1) | `shader_draw_parameters` |
| [`vktDrawShaderInvocationTests.cpp`](../../modules/vulkan/draw/vktDrawShaderInvocationTests.cpp#L1) | `shader_invocation` |
| [`vktDrawNegativeViewportHeightTests.cpp`](../../modules/vulkan/draw/vktDrawNegativeViewportHeightTests.cpp#L1) | `negative_viewport_height`, `zero_viewport_height`, `offscreen_viewport` |
| [`vktDrawInvertedDepthRangesTests.cpp`](../../modules/vulkan/draw/vktDrawInvertedDepthRangesTests.cpp#L1) | `inverted_depth_ranges` |
| [`vktDrawDifferingInterpolationTests.cpp`](../../modules/vulkan/draw/vktDrawDifferingInterpolationTests.cpp#L1) | `differing_interpolation` |
| [`vktDrawShaderLayerTests.cpp`](../../modules/vulkan/draw/vktDrawShaderLayerTests.cpp#L1) | `shader_layer` |
| [`vktDrawShaderViewportIndexTests.cpp`](../../modules/vulkan/draw/vktDrawShaderViewportIndexTests.cpp#L1) | `shader_viewport_index` |
| [`vktDrawScissorTests.cpp`](../../modules/vulkan/draw/vktDrawScissorTests.cpp#L1) | `scissor` |
| [`vktDrawMultipleInterpolationTests.cpp`](../../modules/vulkan/draw/vktDrawMultipleInterpolationTests.cpp#L1) | `multiple_interpolation` |
| [`vktDrawMultisampleLinearInterpolationTests.cpp`](../../modules/vulkan/draw/vktDrawMultisampleLinearInterpolationTests.cpp#L1) | `linear_interpolation` |
| [`vktDrawDiscardRectanglesTests.cpp`](../../modules/vulkan/draw/vktDrawDiscardRectanglesTests.cpp#L1) | `discard_rectangles` |
| [`vktDrawExplicitVertexParameterTests.cpp`](../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L1) | `explicit_vertex_parameter` |
| [`vktDrawDepthClampTests.cpp`](../../modules/vulkan/draw/vktDrawDepthClampTests.cpp#L1) | `depth_clamp` |
| [`vktDrawMultipleClearsWithinRenderPass.cpp`](../../modules/vulkan/draw/vktDrawMultipleClearsWithinRenderPass.cpp#L1) | `multiple_clears_within_render_pass` |
| [`vktDrawSampleAttributeTests.cpp`](../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L1) | `implicit_sample_shading` |
| [`vktDrawVertexAttribDivisorTests.cpp`](../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L1) | `vertex_attribute_divisor` |
| [`vktDrawOutputLocationTests.cpp`](../../modules/vulkan/draw/vktDrawOutputLocationTests.cpp#L1) | `output_location` |
| [`vktDrawDepthBiasTests.cpp`](../../modules/vulkan/draw/vktDrawDepthBiasTests.cpp#L1) | `depth_bias` |
| [`vktDrawAhbTests.cpp`](../../modules/vulkan/draw/vktDrawAhbTests.cpp#L1) | `ahb` |
| [`vktDrawAhbExternalFormatResolveTests.cpp`](../../modules/vulkan/draw/vktDrawAhbExternalFormatResolveTests.cpp#L1) | `ahb_external_format_resolve` |
| [`vktDrawMultiExtTests.cpp`](../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L1) | `multi_draw` |
| [`vktDrawPointClampTests.cpp`](../../modules/vulkan/draw/vktDrawPointClampTests.cpp#L1) | `point_size_clamp` |
| [`vktDrawNonLineTests.cpp`](../../modules/vulkan/draw/vktDrawNonLineTests.cpp#L1) | `non_line_with_params` |
| [`vktDrawIndirectInstancedTests.cpp`](../../modules/vulkan/draw/vktDrawIndirectInstancedTests.cpp#L1) | `indirect_instanced` |

### Utility / Helper Files

These files provide shared infrastructure and do not register tests directly:

| File | Purpose |
|---|---|
| [`vktDrawBaseClass.cpp`](../../modules/vulkan/draw/vktDrawBaseClass.cpp#L1) | Base test class with common draw setup |
| [`vktDrawBufferObjectUtil.cpp`](../../modules/vulkan/draw/vktDrawBufferObjectUtil.cpp#L1) | Buffer object creation and management helpers |
| [`vktDrawCreateInfoUtil.cpp`](../../modules/vulkan/draw/vktDrawCreateInfoUtil.cpp#L1) | Create-info struct builders |
| [`vktDrawGroupParams.hpp`](../../modules/vulkan/draw/vktDrawGroupParams.hpp#L1) | Shared `GroupParams` struct for variant configuration |
| [`vktDrawImageObjectUtil.cpp`](../../modules/vulkan/draw/vktDrawImageObjectUtil.cpp#L1) | Image object creation and management helpers |
| [`vktDrawTestCaseUtil.hpp`](../../modules/vulkan/draw/vktDrawTestCaseUtil.hpp#L1) | Test case utility declarations |

## Cross-File Recurring Themes

### Draw Command Coverage

The category systematically covers all Vulkan draw commands: `vkCmdDraw`, `vkCmdDrawIndexed`, `vkCmdDrawIndirect`, `vkCmdDrawIndexedIndirect`, `vkCmdDrawIndirectCount`, `vkCmdDrawIndexedIndirectCount`, and the multi-draw extensions (`VK_EXT_multi_draw`). Each draw command is tested across multiple primitive topologies, vertex counts, and instancing configurations.

### Viewport and Depth Range Transformations

Multiple topic groups test viewport-related behavior: negative viewport height (Y-flip), zero viewport height, off-screen viewports, inverted depth ranges, and depth clamping. These verify the coordinate transformation pipeline from clip space through viewport transform to framebuffer coordinates.

### Interpolation Qualifiers

Three topic groups cover interpolation: `differing_interpolation` (mismatching qualifiers), `multiple_interpolation` (simultaneous qualifiers), and `linear_interpolation` (multisample linear interpolation with `interpolateAtOffset`/`interpolateAtSample`). The `explicit_vertex_parameter` group tests AMD's manual barycentric interpolation.

### Dynamic Rendering Compatibility

The variant-root structure ensures that draw functionality works correctly under both renderpass-based and dynamic rendering modes, including secondary command buffer scenarios. Some groups (amber tests, subpass-dependent tests) are restricted to renderpass-only mode.

## Cross-File Recurring Parameter Dimensions

| Dimension | Observed in | Values |
|---|---|---|
| Primitive topology | basic_draw, instanced, indirect_draw, indexed_draw | All 10 `VkPrimitiveTopology` values |
| Instance count | instanced, indirect_instanced, multi_draw | 0–20, firstInstance offsets |
| Sample count | multiple_interpolation, linear_interpolation, explicit_vertex_parameter | 1, 2, 4, 8, 16, 32, 64 |
| Vertex/instance divisor | vertex_attribute_divisor, instanced | 0, 1, 2, 16 |
| Dynamic rendering mode | All topic groups | Renderpass vs dynamic rendering with 5 command buffer configurations |

## Cross-File Recurring Support Requirements

| Requirement | Topic groups |
|---|---|
| `VK_KHR_maintenance1` | negative_viewport_height, zero_viewport_height, offscreen_viewport |
| `VK_KHR_maintenance5` | basic_draw, indexed_draw |
| `VK_KHR_dynamic_rendering` | All dynamic_rendering variant tests |
| `VK_EXT_discard_rectangles` | discard_rectangles |
| `VK_EXT_vertex_attribute_divisor` / `VK_KHR_vertex_attribute_divisor` | vertex_attribute_divisor, instanced |
| `VK_EXT_multi_draw` | multi_draw |
| `VK_EXT_depth_range_unrestricted` | inverted_depth_ranges, depth_clamp |
| `VK_EXT_depth_clamp_control` | depth_clamp |
| `VK_AMD_shader_explicit_vertex_parameter` | explicit_vertex_parameter |
| `VK_EXT_shader_demote_to_helper_invocation` | shader_invocation |
| `VK_ANDROID_external_memory_android_hardware_buffer` | ahb |
| `VK_ANDROID_external_format_resolve` | ahb_external_format_resolve |
| `largePoints` feature | point_size_clamp |
| `multiDrawIndirect` feature | indirect_draw, indirect_instanced, multi_draw |

## Cross-File Recurring Verification Methods

| Method | Topic groups |
|---|---|
| Fuzzy image comparison (`tcu::fuzzyCompare`) | simple_draw, concurrent, basic_draw, instanced, ahb |
| Integer threshold comparison (`tcu::intThresholdCompare`) | ahb_external_format_resolve |
| Software reference renderer (`rr::Renderer`) | basic_draw, indexed_draw, indirect_draw, indirect_instanced |
| Amber test framework | shader_invocation, output_location, depth_bias, basic_draw (misc) |
| Atomic counter verification | implicit_sample_shading |
| Two-pass rendering comparison | differing_interpolation, non_line_with_params |
