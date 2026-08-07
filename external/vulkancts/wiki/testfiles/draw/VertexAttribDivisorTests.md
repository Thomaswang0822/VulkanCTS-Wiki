## Overview

**Core question:** Do supported vertex-input and draw-command paths advance instance-rate attributes at the selected divisor and first-instance origin?

`vertex_attribute_divisor` checks instance-rate vertex input with the `VK_EXT_vertex_attribute_divisor` and `VK_KHR_vertex_attribute_divisor` extensions. It makes divisor behavior visible in a rendered image: a per-vertex quad-grid position/color stream is combined with a second, instance-rate color stream, and the GPU result is compared with an equivalent reference-renderer draw.

The implementation is one parameterized test family, not an Amber wrapper. Each leaf selects an extension spelling, pipeline construction method, draw command, first-instance mode, and divisor value.

## Background Knowledge

Vertex input rate controls whether an attribute advances per vertex or per instance. A vertex attribute divisor changes the instance-rate advancement interval. A divisor of zero reuses one element, while a nonzero divisor advances after the corresponding number of instances.

## Registration Hierarchy

- Implementation: [vktDrawVertexAttribDivisorTests.cpp](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp)
- Category dispatcher: [vktDrawTests.cpp](../../../modules/vulkan/draw/vktDrawTests.cpp)

The dispatcher registers this family through `createVertexAttributeDivisorTests()` for the ordinary draw groups. The direct render-pass path is:

```text
draw.renderpass.vertex_attribute_divisor
├── ext
└── khr
```

Each extension child expands into the pipeline, draw-command, first-instance, and divisor dimensions described below. The deeper generated leaves are intentionally flattened because the registration validator accepts only direct children in this tree.

For dynamic rendering, the family is registered below each command-buffer mode created by the dispatcher:

```text
draw.dynamic_rendering.<command_buffer_mode>.vertex_attribute_divisor
```

The modes are `primary_cmd_buff`, `partial_secondary_cmd_buff`, `complete_secondary_cmd_buff`, `nested_partial_secondary_cmd_buff`, and `nested_complete_secondary_cmd_buff`. `shader_objects` is emitted only when `useDynamicRendering` is true, so it is absent from the render-pass branch and present in the dynamic-rendering branches. The source dispatcher omits the whole dynamic-rendering tree in Vulkan SC builds.

## Parameter Dimensions and Observed Values

The source loops over these dimensions in this order:

| Dimension | Registered values |
|---|---|
| Extension | `ext`, `khr` |
| Pipeline | `static_pipeline`, `dynamic_pipeline`, `shader_objects` (dynamic rendering only) |
| Draw command | `draw`, `draw_indexed`, `draw_indirect`, `draw_indexed_indirect`, `draw_multi_ext`, `draw_multi_indexed_ext`, `draw_indirect_byte_count`, `draw_indirect_count`, `draw_indexed_indirect_count` |
| First instance | `zero`, `non_zero` |
| Divisor leaf | `0`, `1`, `2`, `16` |

`draw_indirect_byte_count` is excluded when `CTS_USES_VULKANSC` is defined. The command names map directly to the calls in `VertexAttributeDivisorInstance::draw()`. The `draw_multi_*` leaves require `VK_EXT_multi_draw`; indirect leaves require `VK_KHR_draw_indirect_count` according to the implementation's support check.

## Behavior Parameters

The primary behavior axes are extension spelling, pipeline delivery, draw command, first instance, and divisor. The same divisor contract is exercised across these delivery and command variants.

### Extension and pipeline delivery

`ext` and `khr` select the extension spelling. `static_pipeline` supplies divisor state at pipeline creation, while `dynamic_pipeline` sets vertex input immediately before the draw. `shader_objects` uses shader objects and dynamic vertex input and is limited to dynamic rendering.

### Draw command and instance origin

The direct, indexed, indirect, multi-draw, byte-count, and count-draw commands expose the divisor under different command-recording paths. `zero` and `non_zero` first-instance leaves test whether the instance origin is applied consistently.

### Divisor values

The registered divisor values are `0`, `1`, `2`, and `16`. The zero value reuses the same instance-rate attribute, while the nonzero values advance the attribute stream at different rates.

## Shader Analysis

The test renders to a 128x128 `VK_FORMAT_R8G8B8A8_UNORM` color image. A vertex buffer contains an 8x8 grid of quads. Binding 0 has `VK_VERTEX_INPUT_RATE_VERTEX` and a `VertexPositionAndColor` stride; locations 0 and 1 read position and base color. Binding 1 has `VK_VERTEX_INPUT_RATE_INSTANCE` and a `tcu::Vec4` stride; location 2 reads the divisor-controlled instance color.

For indexed commands, the source creates a 9x9 grid of shared vertices and a `uint32` index buffer containing six indices per quad. For indirect commands it creates either a `VkDrawIndirectCommand` or `VkDrawIndexedIndirectCommand`; count commands additionally use a count buffer containing one. The transform-feedback byte-count variant uses the vertex-data byte size as its count input.

Before each case is submitted, the image is transitioned, cleared to black with alpha 1, and synchronized for color-attachment use. The command is then recorded through a render pass, dynamic rendering, or the selected secondary-command-buffer arrangement.

### Shader and observable divisor behavior

The generated vertex shader uses locations 0, 1, and 2 and a two-float vertex push constant containing `firstInstance` and `instanceCount` (the listing below shows its behavior-relevant body):

```glsl
layout(location = 0) in vec4 in_position;
layout(location = 1) in vec4 in_color;
layout(location = 2) in vec4 in_color_2;
layout(push_constant) uniform TestParams {
    float firstInstance;
    float instanceCount;
} params;

void main() {
    gl_Position = in_position +
        vec4(float(gl_InstanceIndex - params.firstInstance) * 2.0 /
             params.instanceCount, 0.0, 0.0, 0.0);
    out_color = in_color +
        vec4(float(gl_InstanceIndex) / params.instanceCount, 0.0, 0.0, 1.0) +
        in_color_2;
}
```

The fragment shader copies the interpolated color to location 0. The position term separates instances horizontally; the red term exposes the absolute instance index, including a non-zero first instance; and `in_color_2` exposes when binding 1 advances. A divisor of 0 is passed to the Vulkan vertex-input divisor state unchanged. The test data allocates one instance color for divisor 0 and otherwise allocates enough entries for `(instanceCount + firstInstance + divisor - 1) / divisor` accesses.

Each leaf runs `instanceCount` values `0`, `1`, `2`, `4`, and `20`. `zero` runs only `firstInstance = 0`; `non_zero` runs `1`, `3`, `4`, and `20`. For a zero instance count, data preparation still allocates one geometric instance so buffer creation and reference setup remain valid, while the Vulkan draw itself receives zero.

## Runtime Execution and Result Checking

The generated vertex shader and reference renderer consume the same position, base-color, and divisor-controlled color streams. The GPU image is read back after the selected render path and compared with the reference image using the source fuzzy threshold.

### Pipeline variants

- `static_pipeline` puts the two binding descriptions, three attributes, and `VkVertexInputBindingDivisorDescription` into pipeline creation.
- `dynamic_pipeline` makes `VK_DYNAMIC_STATE_VERTEX_INPUT_EXT` dynamic and calls `vkCmdSetVertexInputEXT` immediately before the draw with the selected divisor.
- `shader_objects` creates vertex and fragment shader objects from the `vert` and `frag` binaries, binds them at draw time, sets the required default viewport/scissor state, and uses dynamic vertex input. This variant is only registered for dynamic rendering and is not compiled into Vulkan SC.

## Failure Meaning

### Failure Cause Mapping

| Failing behavior axis | Possible implementation cause |
|---|---|
| Divisor `0`, `1`, `2`, or `16` | Incorrect instance-rate advancement, divisor state, or attribute fetch. |
| Nonzero first instance | Incorrect first-instance handling or indirect command interpretation. |
| Static versus dynamic pipeline | Incorrect pipeline vertex-input state or dynamic vertex-input command. |
| Direct, indexed, indirect, multi-draw, or count command | Command-record encoding, count-buffer handling, index handling, or divisor state propagation. |
| Shader-object path | Shader-object binding, dynamic vertex input, or dynamic-rendering setup. |

### Cause Analysis

#### Attribute advancement

**Possible failure symptoms:** The rendered image differs from the reference in instance-dependent position or color.

**Possible implementation causes:** The implementation may advance the instance-rate binding at the wrong interval, ignore divisor zero semantics, apply the wrong first-instance base, or use an incorrect attribute offset.

#### Command and pipeline delivery

**Possible failure symptoms:** Only one pipeline or draw-command family fails while the same divisor values pass elsewhere.

**Possible implementation causes:** The selected pipeline state, dynamic vertex-input command, indirect record, count buffer, multi-draw record, or shader-object binding may not carry the divisor configuration correctly.

## Case Pruning

### Requirement-based pruning

Cases are skipped when the selected extension, dynamic state, shader-object, multi-draw, indirect-count, transform-feedback, or dynamic-rendering requirement is unavailable.

### Design-based pruning

Vulkan SC excludes the byte-count and dispatcher paths that are guarded out by the source.

### Support gates

`checkSupport()` requires the selected divisor extension (`VK_EXT_vertex_attribute_divisor` or `VK_KHR_vertex_attribute_divisor`). It checks `supportsNonZeroFirstInstance` for non-zero first-instance cases, `drawIndirectFirstInstance` for non-zero indirect cases, `vertexAttributeInstanceRateDivisor` for divisor 1, and `vertexAttributeInstanceRateZeroDivisor` for divisor 0. It also gates dynamic vertex input, shader objects, multi-draw, indirect-count functionality, and dynamic rendering according to the selected dimensions. The byte-count command additionally requires transform feedback, `transformFeedback`, and `transformFeedbackDraw`, and is not available in Vulkan SC.

### Verification

For every `(instanceCount, firstInstance)` pair, the implementation constructs an `rr::Renderer` reference using the same vertex data, colors, indices when applicable, and divisor-controlled attribute stream. The reference uses `INT_MAX` for the divisor-0 input because of the reference renderer's divisor convention; this is an implementation detail of the reference setup, while the Vulkan divisor remains 0.

The rendered GPU image is read back from the color target and compared to the reference with `tcu::fuzzyCompare(..., 0.05f, ...)`. Any mismatch across the loop is recorded and causes the leaf to fail with `Unexpected results in output buffers`; otherwise the leaf returns `Pass`.

## Key Takeaways

- The family varies extension spelling, pipeline delivery, draw command, first instance, and divisor value.
- The shader exposes divisor behavior through instance-dependent position and color, and the host compares the result with a reference renderer.
- Support skips are distinct from image-comparison failures and reflect the selected command or feature requirements.

## Source Reference Appendix

- Parameters and helper classification: [lines 48-132](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L48-L132)
- Pipeline and vertex-input setup: [lines 279-475](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L279-L475)
- Iteration, command recording, and image comparison: [lines 478-698](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L478-L698)
- Test data and draw-command dispatch: [lines 700-911](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L700-L911)
- Support checks and GLSL binaries: [lines 953-1065](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L953-L1065)
- Family registration loops: [lines 1070-1198](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L1070-L1198)

### Scope boundary

Shared render-pass, dynamic-rendering, and secondary-command-buffer placement belongs to the draw category dispatcher and shared draw infrastructure. This page documents how the divisor family uses those modes; it does not duplicate their category-wide registration policy.
