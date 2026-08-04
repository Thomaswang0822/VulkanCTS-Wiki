# Understanding Brief: input attribute offsets

## One-Sentence Test Purpose

This source checks that Vulkan vertex fetch reaches the intended attribute bytes when a vertex buffer is bound at each non-aligned byte offset supported by its attribute width, with packed, padded, and overlapping storage plus static and dynamic vertex-input state.

## Background Knowledge

### Vertex-input addressing

A vertex-input binding supplies the bound buffer offset and stride. An attribute description supplies its binding, format, and element-relative offset. The test chooses `attributeOffset()` so that the sum of binding and attribute offsets starts each attribute at the intended byte position. `vec2` has an 8-byte attribute size, and `vec4` has a 16-byte size.

### Dynamic vertex input

Static cases place the binding and attribute descriptions in the pipeline. Dynamic cases mark `VK_DYNAMIC_STATE_VERTEX_INPUT_EXT` and send equivalent `VkVertexInputBindingDescription2EXT` and `VkVertexInputAttributeDescription2EXT` through `cmdSetVertexInputEXT` before the draw. The shader source does not change between those state choices.

## One Concrete Example

```text
dEQP-VK.pipeline.monolithic.input_attribute_offset.vec2.offset_0.overlapping.no_memory_offset.dynamic
```

This leaf binds the buffer with offset zero, describes a `VK_FORMAT_R32G32B32A32_SFLOAT` attribute whose attribute offset is zero, and sets the description dynamically. Storage contains adjacent `vec2` values; the vertex shader receives a `vec4`, uses `.xy` as position, and turns the fetched `.zw` into the expected `0.0, 1.0`. The extra trailing `vec2(0.0f, 0.0f)` keeps the final `vec4` fetch within the buffer.

## End-to-End Test Flow

```text
[host] select construction type, vec2 or vec4, binding offset, stride case, memory-offset choice, and static or dynamic state
[host] create and fill a host-visible vertex buffer; bind its memory with an optional aligned memory offset
[host] create a 4 by 4 color attachment, render pass, graphics pipeline, and command buffer
[device] fetch attributes using the bound-buffer offset, attribute offset, format, and stride; vertex shader forms positions
[device] fragment shader writes opaque blue for every covered pixel
[host] copy the attachment, wait, invalidate the allocation, and compare all pixels with opaque blue at zero tolerance
```

## Generated Test Artifacts and Bound Resources

| Resource or artifact | Host setup | Device use | Why it matters |
|---|---|---|---|
| Vertex buffer and allocation | Builds bytes with leading offset, selected layout, and optional memory offset | Vertex fetch reads it | Separates buffer binding, attribute, and memory offsets. |
| Binding and attribute descriptions | Uses `bindingStride()`, format, and `attributeOffset()` | Vertex-input state consumes them | Defines the address and type of the fetch. |
| Generated vertex shader | Selects `vec2`, `vec4`, or overlapping `vec4` input | Reads location 0 | Makes malformed `.zw` overlap data observable. |
| Generated fragment shader and color attachment | Creates an `R8G8B8A8_UNORM` target | Writes blue, then copies it | Supplies the host-visible result. |

## What Is Checked

The test renders one triangle per pixel of a 4 by 4 attachment. It compares the copied attachment to `getDefaultColor()` (`Vec4(0.0f, 0.0f, 1.0f, 1.0f)`) with `tcu::floatThresholdCompare` and threshold `Vec4(0.0f)`. A pass therefore requires exact opaque blue output.

## Behavior Parameter Identification

> **Behavior parameter:** `strideCase`
>
> **Candidate values:** `PACKED`, `PADDED`, `OVERLAPPING`

`strideCase` changes the physical relationship between neighboring attribute records. `OVERLAPPING` exists only for `vec2`; the other dimensions locate that layout at each binding/memory offset and select static or dynamic state.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `PACKED` | Attribute address computation, bound-buffer offset handling, format interpretation, or static/dynamic state setup selects the wrong bytes. |
| `PADDED` | Stride calculation or padding skip is wrong, or the implementation uses attribute width rather than declared stride for a later vertex. |
| `OVERLAPPING` | A four-component fetch from adjacent `vec2` records is incomplete, reads the wrong neighboring bytes, or the `.zw` validation path receives unexpected values. |

## Important Variations and Special Cases

- The factory creates 8 `vec2` byte-offset groups and 16 `vec4` groups. Each `vec2` offset has three layouts, two memory-offset choices, and static/dynamic leaves; each `vec4` offset omits `OVERLAPPING`. The source therefore registers 224 leaves for a construction root.
- The current `vk-default` pipeline mustpass configuration includes all 224 `input_attribute_offset` leaves under `monolithic`.
- `checkSupport()` checks the requested pipeline construction. Dynamic cases require `VK_EXT_vertex_input_dynamic_state`. When `VK_KHR_portability_subset` is present, unsupported stride alignments are skipped.

## Source Mapping

| Topic | Source link | Why it matters |
|---|---|---|
| Parameters and buffer layout | [`TestParams` and `buildVertexBufferData()`](../../../modules/vulkan/pipeline/vktPipelineInputAttributeOffsetTests.cpp#L117-L220) | Defines offset compensation, stride, padding, and overlap storage. |
| Generated shaders | [`initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineInputAttributeOffsetTests.cpp#L329-L358) | Defines the location-0 inputs and overlap check. |
| Runtime and result oracle | [`InputAttributeOffsetInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineInputAttributeOffsetTests.cpp#L360-L507) | Creates state, draws, copies output, and compares it. |
| Registration | [`createInputAttributeOffsetTests()`](../../../modules/vulkan/pipeline/vktPipelineInputAttributeOffsetTests.cpp#L511-L563) | Defines all parameter combinations and names. |
| Mustpass evidence | [`monolithic.txt`](../../../mustpass/main/vk-default/pipeline/monolithic/monolithic.txt) | Contains 224 selected leaves. |

## Questions / Risk Points for User Audit

- `OVERLAPPING` deliberately declares a `vec4` shader input while storing adjacent `vec2` records. It checks a legal fetch range, not an out-of-bounds read.
- The source’s `attributeOffset()` compensates for `bindingOffset`; the registered `offset_N` name denotes the buffer binding offset rather than the computed attribute-description offset.

## Conversion Notes for Final Wiki Rewrite

- Use `strideCase` as the behavior axis and retain the three-row failure mapping.
- Include one representative overlap shader walkthrough; the static/dynamic distinction belongs to host state setup.
- State the complete 224-leaf monolithic mustpass count and separate it from the source’s construction-type parameter.
