## One-Sentence Test Purpose

This test checks whether graphics pipeline stages match shader input and output variables that use SPIR-V `Component` decorations across several interface layouts, scalar widths, and stage sequences.

## Background Knowledge

### Location and Component assignment

A shader interface `Location` identifies a four-component slot. A `Component` decoration selects where a scalar or vector begins inside that slot. The [Vulkan interface rules](../../../../vulkan-docs/src/chapters/interfaces.adoc#L194-L248) assign one component slot to each 16-bit or 32-bit scalar component; a 64-bit scalar component consumes two consecutive component slots and can cross into the next location.

Why it matters here:
- The same location can carry several values only when their component ranges do not overlap.
- A producer and consumer must describe compatible occupied components for data to reach the fragment shader as intended.

### Graphics-stage interfaces

Vertex, tessellation-control, tessellation-evaluation, geometry, and fragment shaders exchange user-defined input and output variables. The test generator emits matching declarations at the selected location and component positions, then inserts pass-through stages when a flow includes tessellation or geometry.

Why it matters here:
- A failure can be exposed at the final color even when the mismatch occurs between earlier adjacent stages.
- Flat interpolation keeps the component-packed values discrete while the intermediate stages copy or combine them.

## One Concrete Example

The `vert_frag.loose_var.float32.single_location.scalar_vec3` test case leaf places a scalar at component 0 and a three-component vector at component 1 of one location. The vertex shader writes `0.125`, then `0.25`, `0.5`, and `1.0`; the fragment shader rebuilds `vec4(0.125, 0.25, 0.5, 1.0)` from its matching inputs. This is a simplified reading of the generator's [layout declarations](../../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L430-L454), [vertex writes](../../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L456-L520), and [fragment reconstruction](../../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L675-L717).

## End-to-End Test Flow

```text
[host] choose a flow, declaration mode, float width, location count, and component pattern
[host] generate GLSL for each shader stage and build a graphics pipeline
[host] render a six-vertex rectangle to a 16 x 16 floating-point color image
[device] carry the decorated interface values through the selected stage sequence
[device] fragment shader packs received values into dEQP_color
[host] copy the image to host-visible memory after submission completes
[host] compare every pixel exactly with (0.125, 0.25, 0.5, 1.0)
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The test generates one GLSL source per stage in the selected flow through `ShaderGen`. `genLayout()` emits loose variables or interface blocks, with the same `location` and `component` layout qualifiers on both sides of each interface. The flow selects `vert_frag`, `vert_geom_frag`, `vert_tesc_tese_frag`, or `vert_tesc_tese_geom_frag`.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Vertex buffer | Yes | Yes | Read by vertex shader | No | Supplies positions for two triangles. |
| `VK_FORMAT_R32G32B32A32_SFLOAT` color image | Yes | Yes, as the render-pass color attachment | Written by fragment output | Yes, after image-to-buffer copy | Makes the received interface values observable. |
| Host-visible result buffer | Yes | Yes, as transfer destination | Written by copy command | Yes | Supplies pixels to `verifyResult()`. |

## What Is Checked

`verifyResult()` scans every pixel and uses exact `Vec4` equality against `(0.125, 0.25, 0.5, 1.0)`. It reports the first mismatching coordinate and values. A pass therefore means the selected declarations and intervening stages preserved the generated component sequence through rendering.

## Behavior Parameter Identification

> **Behavior parameter:** stage-flow intermediate node
>
> **Candidate values:** `vert_frag`, `vert_geom_frag`, `vert_tesc_tese_frag`, `vert_tesc_tese_geom_frag`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `vert_frag` | Direct producer-to-consumer location/component matching or fragment reconstruction failure. |
| `vert_geom_frag` | Geometry-stage interface matching or pass-through failure, or a direct-path failure. |
| `vert_tesc_tese_frag` | Tessellation interface matching or interpolation compensation failure, or a direct-path failure. |
| `vert_tesc_tese_geom_frag` | Interaction among tessellation and geometry interface transfers, or a failure shared by shorter flows. |

## Important Variations and Special Cases

- `loose_var` and `in_block` both execute; `in_struct` is declared in the source enum but commented out of registration.
- Width `float16` requires `shaderFloat16` and `storageInputOutput16`; `float64` requires `shaderFloat64`.
- `single_location` uses one location, while `multiple_locations` creates an array extent of three. The generator cycles the starting location through 1 to 4.
- The nine component patterns are filtered so the seven scalar/`vec2`/`vec3` packing patterns run at 16 and 32 bits, while `scalar_scalar` and `vec2` cover 64-bit components.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Test registration and matrix generation | [`createShaderCompDecorLayoutMatchingTests()`](../../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L1172-L1249) | Defines every registered dimension and valid component-width combination. |
| Interface declaration generator | [`ShaderGen::genLayout()`](../../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L430-L454) | Emits the component-decorated declarations. |
| Execution and readback | [`iterate()`](../../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L968-L1057) | Renders, copies the image, waits, and returns pass or fail. |
| Specification rule | [Location and Component Assignment](../../../../vulkan-docs/src/chapters/interfaces.adoc#L194-L248) | Defines component-slot consumption and overlap rules. |

## Questions / Risk Points for User Audit

- Does the stage-flow axis make the distinction between direct and intermediate-stage coverage clear?
- Does the resource table make clear that the color image, not a shader storage buffer, is the observed result?
- Does the explanation avoid treating a final-pixel mismatch as proof of one specific implementation layer?

## Conversion Notes for Final Wiki Rewrite

- Retain the compact Location/Component explanation and the four-row failure mapping.
- Use the `vert_frag.loose_var.float32.single_location.scalar_vec3` case as the representative shader walkthrough.
- Keep the detailed generator and resource inventory in the final page's parameter, shader, runtime, and appendix sections rather than copying this teaching structure verbatim.
