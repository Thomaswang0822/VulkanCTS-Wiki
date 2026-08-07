# Understanding Brief: Vertex Attribute Divisor Tests

## One-sentence purpose

This family proves that instance-rate vertex attributes advance according to divisor 0, 1, 2, or 16 across EXT/KHR extension paths, pipeline construction variants, draw commands, and first-instance values.

## Core idea

Binding 1 uses `VK_VERTEX_INPUT_RATE_INSTANCE` and feeds location 2. A divisor of `N` reuses an element for `N` instances; divisor 0 keeps one element for all instances. The shader also makes `gl_InstanceIndex` visible in position and red output, so both divisor advancement and first-instance handling affect pixels.

The source tests `instanceCount = 0, 1, 2, 4, 20`. `zero` uses first instance 0; `non_zero` uses 1, 3, 4, and 20. A non-zero first instance is deliberately observable in the shader's absolute-index color term.

## One concrete leaf

A representative path is:

```text
draw.renderpass.vertex_attribute_divisor.ext.static_pipeline.draw.non_zero.2
```

It requires `VK_EXT_vertex_attribute_divisor`, uses a statically-created divisor description of 2, calls `vkCmdDraw`, and repeats the draw for the five instance counts and four non-zero first-instance values. The same leaf name is generated under each dispatcher rendering/command-buffer scope that registers the family.

## End-to-end flow

```text
Select extension/pipeline/command/first-instance/divisor
  -> require selected features and extensions
  -> create 128x128 target, pipeline or shader objects, and layout
  -> prepare quad-grid, optional index/indirect/count, and instance-color buffers
  -> clear and record render-pass, dynamic-rendering, or secondary-buffer commands
  -> submit and read back the color image
  -> render the same inputs with rr::Renderer
  -> fuzzy-compare GPU and reference images
```

## Artifacts and bindings

- Generated GLSL programs are stored as `vert` and `frag`; shader-object mode consumes their SPIR-V binaries.
- The vertex push constant contains two floats: `firstInstance` and `instanceCount`.
- Location 0 reads per-vertex position; location 1 reads per-vertex base color; location 2 reads the divisor-controlled instance color.
- Indexed cases add a `uint32` index buffer. Indirect cases add draw-command records; count cases add a one-entry count buffer.
- The target is a single-layer 128x128 `VK_FORMAT_R8G8B8A8_UNORM` color image.

## What is checked

The reference renderer draws the same triangle strip geometry (indexed or non-indexed), with the same instance count and first instance. For its divisor-0 convention, the C++ reference setup substitutes `INT_MAX`; the Vulkan state itself remains the selected divisor. `tcu::fuzzyCompare` uses a threshold of `0.05`. A mismatch in any iteration fails the leaf.

## Parameter and support map

| Axis | Values | Main gate |
|---|---|---|
| Extension | `ext`, `khr` | Corresponding vertex-attribute-divisor extension |
| Pipeline | `static_pipeline`, `dynamic_pipeline`, `shader_objects` | Dynamic vertex input and shader-object functionality as selected |
| Command | direct, indexed, indirect, multi-draw, byte-count, indirect-count | Command-specific extension/features |
| First instance | `zero`, `non_zero` | `supportsNonZeroFirstInstance`; indirect also needs `drawIndirectFirstInstance` |
| Divisor | `0`, `1`, `2`, `16` | Zero-divisor or divisor feature where checked |

The source excludes `draw_indirect_byte_count` from Vulkan SC. Shader objects are registered only below dynamic-rendering groups. The dispatcher supplies render-pass plus five dynamic-rendering command-buffer modes; the nested-secondary modes are category-wide registration policy, not a divisor-specific algorithm.

## Failure interpretation

- Failures in `0` versus non-zero divisor leaves point to instance-rate divisor handling or the corresponding feature gate.
- Failures only in `non_zero` point to first-instance property/feature handling or indirect command records.
- Failures only in indexed leaves point to index-buffer binding or indexed command delivery.
- Failures only in indirect/count/multi/byte-count leaves point to that command's record, count, synchronization, or extension path.
- Failures only in dynamic pipeline or shader objects point to dynamic vertex-input/shader-object state setup.

## Source map

- [parameter enums and data model](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L48-L132)
- [pipeline and vertex input](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L279-L475)
- [iteration and reference comparison](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L478-L698)
- [draw dispatch and dynamic input](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L792-L911)
- [support checks and shaders](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L953-L1065)
- [registration](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L1070-L1198)

## Audit questions

- Is the page's registration path being read under the correct `renderpass` or `dynamic_rendering.<mode>` parent?
- Is a failure isolated to a divisor, first-instance, command, or pipeline dimension?
- Was the selected feature gate checked before treating a skipped case as an implementation failure?
