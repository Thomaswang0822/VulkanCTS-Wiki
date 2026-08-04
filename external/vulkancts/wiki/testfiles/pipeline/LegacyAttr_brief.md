# Understanding Brief: `pipeline.monolithic.vertex_input.legacy_vertex_attributes`

## One-sentence test purpose

This family checks whether the dynamic vertex-input path fetches legacy attribute data with the requested format, stride, and offsets, then exposes the result to a shader input with a selected numeric type. The test compares that result with a CTS host reference.

## Background knowledge

### Dynamic vertex input

A graphics pipeline can declare `VK_DYNAMIC_STATE_VERTEX_INPUT_EXT` and provide an empty static vertex-input state. Before drawing, `vkCmdSetVertexInputEXT` supplies binding descriptions and attribute descriptions. A binding gives the stride and input rate; an attribute maps a shader location to a binding, `VkFormat`, and byte offset. `VK_EXT_legacy_vertex_attributes` adds arbitrary buffer alignments, arbitrary strides, and binding component types that differ from shader input numeric types; it is usable only with dynamic vertex input ([extension description](../../../../vulkan-docs/src/appendices/VK_EXT_legacy_vertex_attributes.adoc#L19-L31)). Vulkan describes this dynamic command and its required state in [Dynamic Vertex Input](../../../../vulkan-docs/src/chapters/fxvertex.adoc#L258-L270) and defines the address inputs used for vertex fetch in [Vertex Input Address Calculation](../../../../vulkan-docs/src/chapters/fxvertex.adoc#L1076-L1130).

### Format conversion and shader type

The test deliberately separates the vertex format from the shader declaration. It supplies a vertex attribute as a selected `VkFormat`, then declares the corresponding shader input as `float` or `vecN`, `int` or `ivecN`, or `uint` or `uvecN`. The expected result comes from CTS host-side decoding of the input bytes according to the selected format and stride, then expanding each used component to 32 bits. The fragment stage writes the value it received into a storage buffer, so the host can compare fetched values rather than infer them only from rendered color.

### Strides and offsets

The binding stride selects the distance between source records. The attribute offset shifts the attribute inside each record, while the allocation memory offset shifts the bound data in memory. The single-binding matrix includes zero, one-byte, natural-format-size, and `2 * formatSize - 1` strides. These cases exercise data reuse, overlapping records, aligned records, and a nonstandard larger stride. The family avoids offset cases that would still be aligned when all channels are eight bits wide.

## One concrete example

A `single_binding` leaf can use `VK_FORMAT_R32_SFLOAT`, shader type `float`, a stride equal to the format size, and zero attribute and memory offsets. The test creates 16 random source values and a position buffer with 16 point locations. It installs dynamic descriptions for position at location 0 and the test data at location 1. The vertex shader passes the `float` unchanged to the fragment shader, which writes one value at index `int(gl_FragCoord.x)` of a storage buffer. The host's `getOutputData()` decoder produces the expected 16 32-bit values from the input bytes and compares them with the storage-buffer readback.

## End-to-end test flow

```text
[host] choose format, shader type, stride, attribute offset, and memory offset
[host] generate deterministic input bytes and decode a reference vector with getOutputData()
[host] allocate, fill, and flush position and test-data vertex buffers
[host] create an SSBO per tested binding and clear it to zero
[host] create shaders and a graphics pipeline with VK_DYNAMIC_STATE_VERTEX_INPUT_EXT
[host] bind buffers and SSBOs, install dynamic descriptions, and draw 16 points
[device] fetch and convert attributes, pass them through the vertex interface, and write them from the fragment shader
[host] copy the color image, invalidate color and SSBO allocations, then compare both observations
```

## Generated test artifacts and bound resources

| Resource or artifact | Host setup | Device use | Host readback | Purpose |
|---|---:|---:|---:|---|
| `vert` | generated from the binding list | vertex stage | no | Receives position at location 0 and one input per tested binding. |
| `frag` | generated from the binding list | fragment stage | no | Writes blue to the color attachment and stores each interpolated input in an SSBO. |
| Position vertex buffer | filled and flushed | vertex fetch | no | Places 16 point primitives across the framebuffer. |
| One data vertex buffer per test binding | random bytes filled and flushed | vertex fetch | no | Supplies data with the selected format, stride, and offsets. |
| One storage buffer per test binding | zero-filled and flushed | fragment shader write | yes | Captures values received by the shader. |
| `VK_FORMAT_R8G8B8A8_UNORM` image | created as color attachment and transfer source | attachment write | yes | Confirms the point primitives rendered. |

## What is checked

The source makes two independent observations. First, it expects every pixel in the 16 by 1 color target to be opaque blue and compares the copied image with a zero threshold. Second, it compares each SSBO value with the host-generated reference. Fixed-point and floating-point channel classes use a per-component threshold derived from format bit width; signed and unsigned integer channels require exact 32-bit equality. A failure in the color image means the draw did not produce the expected geometry or color. A failure in an SSBO means the captured attribute value did not match the selected conversion and address calculation, subject to the end-to-end localization limits below.

## Behavior parameter identification

> **Behavior parameter:** intermediate node
>
> **Candidate values:** `single_binding`, `multi_binding`

`single_binding` changes one test-data binding across a broad format, shader-type, stride, and offset matrix. `multi_binding` uses three data bindings at once and applies the same attribute and memory-offset choices to the curated tuple. The registered leaves below each intermediate node provide the concrete parameter combinations.

## What failure means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `single_binding` | Vertex fetch may use an incorrect format conversion, stride, attribute offset, allocation offset, or shader input type; the shader-to-SSBO path or host comparison may also be wrong. |
| `multi_binding` | The implementation may handle one binding correctly but associate one of the three simultaneous bindings, locations, formats, strides, or SSBO destinations incorrectly; shader-to-SSBO capture and host comparison remain possible fault paths. |

## Important variations and special cases

- The factory registers 1,336 `single_binding` leaves and 24 `multi_binding` leaves in each of the monolithic and fast-linked-library mustpass lists.
- `single_binding` iterates a source list of 58 formats, three candidate shader formats, a deduplicated stride set, and binary attribute and allocation offsets. Source filtering removes selected redundant or unsuitable reinterpretation combinations.
- `multi_binding` uses three curated three-format tuples, normal or one-byte strides, and binary attribute and allocation offsets.
- Every case requires `fragmentStoresAndAtomics`, `VK_EXT_vertex_input_dynamic_state`, `VK_EXT_legacy_vertex_attributes`, selected pipeline-construction support, and `VK_FORMAT_FEATURE_VERTEX_BUFFER_BIT` for each tested format. Cases with a three-component attribute also require `VK_EXT_scalar_block_layout`.
- The parent only adds this nested subgroup for monolithic and fast-linked-library construction ([parent registration](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L3111-L3120)).

## Source mapping

| Topic | Source link | Why it matters |
|---|---|---|
| Parameters and expected-value decoder | [`BindingParams` and `getOutputData()`](../../../modules/vulkan/pipeline/vktPipelineLegacyAttrTests.cpp#L66-L242) | Defines the configurable address inputs and host reference conversion. |
| Input generation and support gates | [`genInputData()` and `checkSupport()`](../../../modules/vulkan/pipeline/vktPipelineLegacyAttrTests.cpp#L245-L363) | Rejects unstable float values and requires extensions, features, and format support. |
| Generated shaders | [`initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineLegacyAttrTests.cpp#L365-L413) | Generates the vertex interface and fragment SSBO stores. |
| Runtime and comparisons | [`LegacyVertexAttributesInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineLegacyAttrTests.cpp#L415-L809) | Allocates resources, records commands, and validates color plus captured values. |
| Matrix registration | [`createLegacyVertexAttributesTests()`](../../../modules/vulkan/pipeline/vktPipelineLegacyAttrTests.cpp#L833-L1071) | Registers `single_binding` and `multi_binding` leaves. |
| Parent routing | [`createVertexInputTests()`](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L3111-L3120) | Registers `legacy_vertex_attributes` only for the two construction types. |

## Questions / risk points for user audit

- The storage-buffer result observes vertex fetch, format conversion, shader interfaces, fragment execution, SSBO writes, synchronization, and host comparison. A mismatch does not uniquely assign the defect to vertex fetch.
- The color result confirms that the point draw rendered blue but does not validate the fetched test-data value by itself.
- The source requires the extension by name but the local Vulkan-Docs checkout does not contain the extension's normative appendix text. This brief uses the source and the local dynamic-vertex-input chapter for the documented runtime contract.

## Conversion notes for final wiki rewrite

Keep the Failure Cause Mapping table byte-for-byte identical in the final page. Include a representative generated one-binding shader pair and fresh SPIR-V disassembly. State the complete factory matrix and the source-level pruning conditions without listing every registered leaf.
