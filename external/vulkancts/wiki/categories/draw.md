## Overview

The `draw` test category collects Vulkan CTS tests that check draw-command behavior and the rendering state that determines their results. The category compares direct, indexed, indirect, instanced, multi-draw, rasterization, interpolation, shader-built-in, external-resource, and extension-specific behavior across render-pass and eligible dynamic-rendering command-buffer paths.

## Background Knowledge

- A Vulkan draw command consumes vertex and instance data through vertex-input bindings, attributes, indices, and draw parameters such as `firstVertex`, `firstIndex`, `baseVertex`, `firstInstance`, and `instanceCount`.
- A render pass and dynamic rendering establish attachment scope, load and store behavior, layouts, and subpass relationships. Secondary command buffers add recording and inheritance constraints.
- Rasterization state transforms primitives into fragments. Viewport, depth range, scissor, depth bias, point-size limits, discard rectangles, interpolation qualifiers, and line-rasterization state affect which values reach an attachment.
- Shader interfaces and built-ins carry values between stages. Several draw families generate shaders to test interpolation, `gl_Layer`, `gl_ViewportIndex`, helper invocations, sample-qualified inputs, and explicit vertex parameters.
- Many families use a readback image or buffer and compare it with a source-generated reference. A support skip means a prerequisite is unavailable; it is distinct from a failed result comparison.

## Category Structure

```text
draw
├── renderpass
└── dynamic_rendering
```

`renderpass` is present for Vulkan and Vulkan SC where supported. `dynamic_rendering` is a Vulkan-only root with `primary_cmd_buff`, `partial_secondary_cmd_buff`, `complete_secondary_cmd_buff`, `nested_partial_secondary_cmd_buff`, and `nested_complete_secondary_cmd_buff` variants. The dispatcher omits families whose implementation requires render-pass subpasses, Amber restrictions, or other explicitly excluded paths.

## How the Families Fit Together

The families share draw-category setup and readback conventions, but each isolates a different stage of the draw pipeline:

- **Command and input behavior** covers direct, indexed, instanced, indirect, concurrent, shader-visible draw parameters, multi-draw, and vertex attribute divisors.
- **Rasterization and depth behavior** covers viewport-height and depth-range transformations, depth clamping, depth bias, point-size clamping, scissors, discard rectangles, and non-line rasterization.
- **Shader interface and fragment behavior** covers differing and multiple interpolation, multisample linear interpolation, explicit vertex parameters, sample attributes, shader layer and viewport index, shader invocation, and output locations.
- **External and extension-heavy resources** covers Android hardware buffers and external-format resolve, while retaining the same category-level rendering and result-checking model.

The Level-3 pages explain the implementation-specific parameters and verdict rules. The dispatcher itself is represented here as category structure rather than as a separate implementation-bearing page.

## Level-3 Pages Navigation

| Registered test family or area | Level-3 page | What to read there |
|---|---|---|
| `basic_draw` | [BasicDrawTests.md](../testfiles/draw/BasicDrawTests.md) | Direct and indexed draw parameters, topology, and command-buffer variants. |
| `simple_draw` | [SimpleTest.md](../testfiles/draw/SimpleTest.md) | Fixed triangle-list and triangle-strip rendering and image comparison. |
| `indexed_draw` | [IndexedTest.md](../testfiles/draw/IndexedTest.md) | Index types, offsets, base vertex, and indexed instancing. |
| `instanced` | [InstancedTests.md](../testfiles/draw/InstancedTests.md) | Instance count, first instance, and instance-rate input behavior. |
| `indirect_draw` | [IndirectTest.md](../testfiles/draw/IndirectTest.md) | Indirect command records, generated commands, count buffers, and synchronization. |
| `indirect_instanced` | [IndirectInstancedTests.md](../testfiles/draw/IndirectInstancedTests.md) | Indirect commands combined with instancing and command counts. |
| `concurrent` | [ConcurrentTests.md](../testfiles/draw/ConcurrentTests.md) | Interleaved compute and graphics work and observable synchronization. |
| `shader_draw_parameters` | [ShaderDrawParametersTests.md](../testfiles/draw/ShaderDrawParametersTests.md) | Shader-visible base vertex, base instance, and draw index. |
| `depth_clamp` | [DepthClampTests.md](../testfiles/draw/DepthClampTests.md) | Depth clamping, depth formats, and clipping behavior. |
| `inverted_depth_ranges` | [InvertedDepthRangesTests.md](../testfiles/draw/InvertedDepthRangesTests.md) | Inverted viewport depth ranges with and without clamping. |
| `negative_viewport_height`, `zero_viewport_height`, `offscreen_viewport` | [NegativeViewportHeightTests.md](../testfiles/draw/NegativeViewportHeightTests.md) | Negative and zero viewport heights and offscreen viewport placement. |
| `depth_bias` | [DepthBiasTests.md](../testfiles/draw/DepthBiasTests.md) | Depth-bias factors, dynamic state, and depth comparison. |
| `point_size_clamp` | [PointClampTests.md](../testfiles/draw/PointClampTests.md) | Device point-size limits and oversized point behavior. |
| `scissor` | [ScissorTests.md](../testfiles/draw/ScissorTests.md) | Static and dynamic scissors applied to draws and clears. |
| `discard_rectangles` | [DiscardRectanglesTests.md](../testfiles/draw/DiscardRectanglesTests.md) | Inclusive and exclusive discard rectangles and scissor interaction. |
| `multiple_clears_within_render_pass` | [MultipleClearsWithinRenderPass.md](../testfiles/draw/MultipleClearsWithinRenderPass.md) | Ordered load, clear, draw, blending, depth, and attachment results. |
| `output_location` | [OutputLocationTests.md](../testfiles/draw/OutputLocationTests.md) | Amber output arrays, formats, precision, and output-location shuffling. |
| `shader_invocation` | [ShaderInvocationTests.md](../testfiles/draw/ShaderInvocationTests.md) | Helper invocations, demotion, subgroup quad operations, atomics, and memory model behavior. |
| `differing_interpolation` | [DifferingInterpolationTests.md](../testfiles/draw/DifferingInterpolationTests.md) | Qualifier mismatch between vertex outputs and fragment inputs. |
| `multiple_interpolation` | [MultipleInterpolationTests.md](../testfiles/draw/MultipleInterpolationTests.md) | Multiple interpolation qualifiers across variables, blocks, arrays, and samples. |
| `linear_interpolation` | [MultisampleLinearInterpolationTests.md](../testfiles/draw/MultisampleLinearInterpolationTests.md) | Multisample interpolation offsets and explicit sample interpolation. |
| `explicit_vertex_parameter` | [ExplicitVertexParameterTests.md](../testfiles/draw/ExplicitVertexParameterTests.md) | AMD barycentric interpolation and explicit vertex parameters. |
| `implicit_sample_shading` | [SampleAttributeTests.md](../testfiles/draw/SampleAttributeTests.md) | Implicit sample shading triggered by sample-qualified inputs and built-ins. |
| `shader_layer` | [ShaderLayerTests.md](../testfiles/draw/ShaderLayerTests.md) | Layered rendering and `gl_Layer` output from shader stages. |
| `shader_viewport_index` | [ShaderViewportIndexTests.md](../testfiles/draw/ShaderViewportIndexTests.md) | `gl_ViewportIndex`, multiple viewports, and stage-specific behavior. |
| `non_line_with_params` | [NonLineTests.md](../testfiles/draw/NonLineTests.md) | Non-line primitives under line-rasterization modes. |
| `multi_draw` | [MultiExtTests.md](../testfiles/draw/MultiExtTests.md) | `VK_EXT_multi_draw`, mosaic and overlapping workloads, and draw identity. |
| `ahb` | [AhbTests.md](../testfiles/draw/AhbTests.md) | Android hardware-buffer import, layered rendering, and readback. |
| `ahb_external_format_resolve` | [AhbExternalFormatResolveTests.md](../testfiles/draw/AhbExternalFormatResolveTests.md) | External-format resolve, YUV decoding, AHB readback, and subpass input attachments. |
| `vertex_attribute_divisor` | [VertexAttribDivisorTests.md](../testfiles/draw/VertexAttribDivisorTests.md) | Extension variants, divisor values, command forms, and instance-rate attributes. |

## Category Notes

The registration-only dispatcher `vktDrawTests.cpp` is folded into this page. Shared utility files provide common image, buffer, create-info, command-recording, and group-parameter infrastructure and are not separate Level-3 test families. The exact registration leaves and profile-specific inclusion remain source and mustpass responsibilities documented by each Level-3 page.

The category has two important scope boundaries. First, nested dynamic-rendering variants intentionally contain only the families selected by the dispatcher, notably the basic family. Second, Vulkan SC and platform-specific Android hardware-buffer paths have explicit compile-time or support gates. A missing path in one profile should not be interpreted as a missing implementation in the source.
