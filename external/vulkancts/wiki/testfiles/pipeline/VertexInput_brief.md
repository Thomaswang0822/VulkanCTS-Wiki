# Understanding Brief: `pipeline.monolithic.vertex_input`

## One-Sentence Test Purpose

This test checks whether a graphics implementation fetches vertex-buffer data at the declared locations, bindings, offsets, formats, strides, and rates before the vertex shader consumes it.

## Background Knowledge

### Vertex input indirection

A vertex shader input uses a `location`; a `VkVertexInputAttributeDescription` maps that location to a binding, format, and byte offset, while a `VkVertexInputBindingDescription` supplies the stride and vertex or instance input rate. Vulkan defines this chain from shader location through binding to the buffer bound for the draw in [Fixed-Function Vertex Processing](../../../../vulkan-docs/src/chapters/fxvertex.adoc#L14-L38).

Why it matters here:
- The test can keep shader input declarations fixed while changing the buffer layout that supplies them.
- `VK_VERTEX_INPUT_RATE_VERTEX` advances with `gl_VertexIndex`; `VK_VERTEX_INPUT_RATE_INSTANCE` advances with `gl_InstanceIndex`.

### Format conversion and absent attributes

The declared vertex format controls the values delivered to the shader input. A format must support `VK_FORMAT_FEATURE_VERTEX_BUFFER_BIT`, and the attribute offset has a defined relationship to the binding stride ([attribute description rules](../../../../vulkan-docs/src/chapters/fxvertex.adoc#L370-L405)). With `VK_KHR_maintenance9`, an input location without an attribute description has the device-reported default vertex-attribute value; the `unbound_input` cases read that value rather than treating it as arbitrary data.

## One Concrete Example

The `misc.unused_binding_dynamic` test makes the contract small: each vertex record contains a position and color, but the pipeline also has an unused second binding description. The vertex shader reads `inPos` at location 0 and `inColor` at location 1, passes the color to the fragment shader, and four draws fill a 2x2 attachment with four distinct colors. In the dynamic variant, `vkCmdSetVertexInputEXT` supplies the same binding and attribute descriptions after the pipeline is bound. The expected four pixels prove that an unused binding does not disturb the locations the shader actually uses.

## End-to-End Test Flow

```text
[host] choose a registered family and its format, type, layout, or special-case parameters
[host] build binding and attribute descriptions, populate vertex buffers, and create shaders and a color attachment
[host] create static vertex-input state or enable VK_DYNAMIC_STATE_VERTEX_INPUT_EXT
[host] bind the pipeline and vertex buffers; dynamic cases call vkCmdSetVertexInputEXT
[device] calculate attribute addresses, convert buffer elements, and provide them to vertex-shader inputs
[device] vertex and fragment shaders produce the diagnostic image
[host] copy or read the color attachment and compare it with the family-specific reference image
[host] return pass only when the comparison succeeds
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

`VertexInputTest::initPrograms()` generates a vertex shader with declarations from the selected GLSL types and locations, then generates checks that count correctly converted components. A full match produces red for instance 0 and blue for instance 1; the fragment shader copies that diagnostic color to the attachment. `StrideChangeCase`, `UnusedBinding`, and `UnboundInput` build smaller fixed shaders for their focused flows.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|---|---:|---:|---:|---:|---|
| Vertex buffer(s) | yes | yes | read | no | Supply bytes whose layout and conversion are under test. |
| Binding and attribute descriptions | yes | pipeline or dynamic command state | used by fetch | no | Map shader locations to buffer bytes. |
| Color attachment | yes | yes | written | yes | Carries the observable result. |
| Generated shaders | yes | yes | read | no | Turn fetched values into image colors. |

## What Is Checked

The main matrix compares a red-left/blue-right reference image with the rendered attachment by `tcu::intThresholdPositionDeviationCompare`, using channel threshold `(2,2,2,2)` and position deviation `(1,1,0)`. `stride_change`, `unused_binding`, and `unbound_input` use exact `tcu::floatThresholdCompare` references. The last two build a 2x2 expected image; `unbound_input` derives the expected alpha from `defaultVertexAttributeValue`.

## Behavior Parameter Identification

> **Behavior parameter:** test family
>
> **Candidate values:** `single_attribute`, `multiple_attributes`, `max_attributes`, `component_mismatch`, `misc`, `legacy_vertex_attributes`, `srgb_vertex_formats`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `single_attribute` | Location-to-binding fetch, format conversion, or vertex/instance rate selection is incorrect. |
| `multiple_attributes` | Multi-binding mapping, interleaved or sequential placement, skipped locations, or out-of-order locations is incorrect. |
| `max_attributes` | Fetch or shader input handling does not scale to the advertised attribute limit. |
| `component_mismatch` | Legal 64-bit component conversion or the shader interface width is handled incorrectly. |
| `misc` | A stride update, unused binding, dynamic vertex-input state, or maintenance9 default attribute value is handled incorrectly. |
| `legacy_vertex_attributes` | The delegated legacy-attribute behavior is incorrect; see `vktPipelineLegacyAttrTests.md`. |
| `srgb_vertex_formats` | The delegated sRGB conversion behavior is incorrect; see `vktPipelineVertexInputSRGBTests.md`. |

## Important Variations and Special Cases

- `multiple_attributes` and `max_attributes` are not registered for shader-object construction types.
- `legacy_vertex_attributes` is registered only for monolithic and fast-linked-library construction types.
- `unused_binding` and `unbound_input` are added only for monolithic, fast-linked-library, and shader-object-unlinked-SPIR-V construction types; dynamic input requires `VK_EXT_vertex_input_dynamic_state` outside shader-object construction.
- `unbound_input` is not built for Vulkan SC and requires `VK_KHR_maintenance9`.
- Float16 cases require `shaderFloat16` and `storageInputOutput16`; double-format cases require `shaderFloat64`. All selected formats must expose `VK_FORMAT_FEATURE_VERTEX_BUFFER_BIT`.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Attribute/binding layout construction | [`VertexInputTest::createInstance()`](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L516-L693) | Builds descriptions, offsets, strides, and buffers. |
| Generated matrix shaders | [`VertexInputTest::initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L695-L720) | Creates the diagnostic vertex and fragment shaders. |
| Main image comparison | [`VertexInputInstance::verifyImage()`](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L1776-L1816) | Defines the pass/fail image check. |
| Focused misc cases | [`StrideChangeCase`, `UnusedBinding`, and `UnboundInput`](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L2277-L3050) | Define the stride, unused-binding, and absent-attribute flows. |
| Registration | [`createVertexInputTests()`](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L3096-L3123) | Registers the direct test-family paths and guards. |

## Questions / Risk Points for User Audit

- The representative walkthrough uses `unused_binding_dynamic`, because it exposes both static and dynamic vertex-input setup with a compact shader.
- `legacy_vertex_attributes` and `srgb_vertex_formats` are registration-only in this source file; their detailed behavior belongs to their own Level-3 pages.

## Conversion Notes for Final Wiki Rewrite

Distill the two prerequisite concepts into the Level-3 Background Knowledge section. Preserve the behavior-parameter conclusion and copy the Failure Cause Mapping table verbatim. Use the `unused_binding_dynamic` shader as the one representative walkthrough, then explain other shader generators as parameter variations rather than embedding several artifacts.
