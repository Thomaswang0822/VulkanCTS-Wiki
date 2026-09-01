# Understanding Brief: Transform feedback simple tests

## One-Sentence Test Purpose

This test checks whether an implementation captures pre-rasterization shader outputs, resumes capture, consumes transform-feedback counters, reports stream-query results, and preserves those behaviors across three graphics-pipeline construction modes.

## Background Knowledge

### Transform-feedback capture and counters

When transform feedback is active, Vulkan appends decorated outputs from the last pre-rasterization shader stage to bound transform-feedback buffers. `XfbBuffer`, `Offset`, and `XfbStride` determine the destination and layout. An optional counter buffer records the append position so a later capture can resume or `vkCmdDrawIndirectByteCountEXT` can derive a vertex count.

Why it matters here:
- A correct shader result can still be stored at the wrong byte offset, stream, or buffer.
- Resume and indirect-draw cases depend on counter writes becoming visible before the next transform-feedback or indirect-read operation.

### Transform-feedback streams and queries

Geometry shaders can emit separate vertex streams. Indexed transform-feedback queries select one stream and return two counts: primitives written and primitives needed. The second count includes primitives that would have been written if the bound range had been large enough.

Why it matters here:
- Nonzero-stream cases distinguish stream routing from ordinary stream-zero capture.
- Query checks can fail even when the captured bytes appear correct because the counters form a separate observable result.

### Graphics pipeline libraries

The same generated cases run with a monolithic pipeline, fast-linked graphics pipeline libraries, and link-time-optimized graphics pipeline libraries. The construction mode changes pipeline assembly, not the transform-feedback contract.

Why it matters here:
- Matching results across the three roots checks that pipeline partitioning and linking preserve transform-feedback declarations and state.
- The monolithic root also owns a small set of cases that the generator deliberately omits from the GPL roots.

## One Concrete Example

For `dEQP-VK.transform_feedback.simple.basic_1_256`, the host binds one 256-byte transform-feedback range. A push constant supplies `start = 0`, and the vertex shader writes `idx_out = start + gl_VertexIndex` with a four-byte transform-feedback stride. The host draws 64 points, waits for transform-feedback writes to become host-readable, and checks that the buffer contains the sequence `0` through `63`.

The same shader template also supports split-buffer cases. For example, a four-part case binds four consecutive ranges in turn, changes `start` to each range's first `uint32_t` index, and expects one uninterrupted increasing sequence across the complete allocation.

## End-to-End Test Flow

```text
[host] select one generated test type, pipeline construction mode, and its dimensions
[host] reject unsupported feature, stage, stream, stride, or output-limit combinations
[host] build the required pre-rasterization shaders and pipeline or shader objects
[host] allocate transform-feedback buffers plus any counter, query-result, vertex, or image resources
[host] record capture, resume, query, indirect-draw, or stream-routing commands for the selected case
[device] execute the last pre-rasterization stage and append decorated outputs while transform feedback is active
[device] update counter buffers and query slots where the case requests them
[device] optionally consume captured data or a counter in a later draw
[host] wait, invalidate mapped memory or read the rendered image, and compare the observed result with the case-specific reference
[host] return pass only when every checked byte, primitive count, availability value, or pixel matches
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `TransformFeedbackTestCase::initPrograms()` selects among generated vertex, geometry, tessellation, and fragment shaders according to `TestType` and topology.
- The common `basic` and `resume` vertex shader writes an increasing `uint` sequence to transform-feedback buffer 0. Its push constant changes the first value without changing the shader binary.
- Built-in, multistream, holes, maximum-output-component, depth-clip-control, backward-dependency, and shader-object cases use separate source branches because they change output declarations or stage dataflow.
- `basic_triangles` loads CTS-authored SPIR-V assembly directly rather than generated GLSL.
- Pipeline construction uses `PIPELINE_CONSTRUCTION_TYPE_MONOLITHIC`, `PIPELINE_CONSTRUCTION_TYPE_FAST_LINKED_LIBRARY`, or `PIPELINE_CONSTRUCTION_TYPE_LINK_TIME_OPTIMIZED_LIBRARY`.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Transform-feedback buffer(s) | yes | yes | device writes | yes | Hold captured shader outputs and expose offset, stride, stream, resume, and overflow errors. |
| Transform-feedback counter buffer | yes, in counter-driven cases | yes | device writes and may later read | sometimes | Carries the append byte count into resume or indirect drawing. |
| Query pool and optional result buffer | yes, in query cases | yes | device writes query results; copy variants write a result buffer | yes | Expose primitives-written, primitives-needed, availability, width, copy, get, and reset behavior. |
| Vertex buffer sourced from prior capture | yes, in dependency cases | yes | device writes during capture and later reads as vertex input | no direct host scan in the image path | Tests synchronization from transform-feedback output back to earlier pipeline consumers. |
| Color image and readback allocation | yes, in rendering checks | yes | device writes the image | yes | Makes counter-derived draw counts or captured vertex data visible as pixels. |
| Push constants | yes | yes | device reads | no | Supply start indices and case-specific draw geometry without descriptors. |

## What Is Checked

- Buffer-oriented cases compare every expected word or vertex component after a transform-feedback-to-host barrier. The common sequence verifier requires `tfData[i] == i`.
- Resume cases require later capture to append at the counter-selected position rather than overwrite earlier data.
- Winding, line/triangle, built-in, holes, and maximum-component cases use specialized reference layouts because byte order depends on primitive assembly or declared transform-feedback offsets.
- Indirect and backward-dependency cases compare a rendered image with a reference image after the captured byte count or captured vertex data drives a later draw.
- Query cases compare primitives-written and primitives-needed values, with variants for 32-bit or 64-bit results, host retrieval or command-buffer copy, zero stride, availability, host reset, and multiple streams.
- A case passes only after all checks owned by its selected `TestType` succeed.

## Behavior Parameter Identification

> **Behavior parameter:** `behavioral group` (registered test case prefix or closely related prefix set)
>
> **Candidate values:** `capture_and_resume`, `builtins_and_topology`, `indirect_and_dependency`, `queries`, `streams`, `layout_and_binding`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `capture_and_resume` | Transform-feedback activation, binding ranges, append offsets, counter resume, or basic output capture is wrong. |
| `builtins_and_topology` | The implementation captures built-in outputs or assembles and orders point, line, triangle, or tessellated primitives incorrectly. |
| `indirect_and_dependency` | Counter-to-indirect or transform-feedback-to-vertex-input synchronization, counter offsets, byte-count conversion, or the resulting draw is wrong. |
| `queries` | Stream selection, primitives-written/needed accounting, result width, availability, copy/get, or reset handling is wrong. |
| `streams` | Geometry-stream routing, simultaneous stream capture, rasterization-stream selection, or per-stream output storage is wrong. |
| `layout_and_binding` | Transform-feedback holes, output-component limits, same-location stream outputs, or shader-object rebinding preserves the wrong layout or binding state. |

## Important Variations and Special Cases

- The generator registers 7,894 `simple` cases and 7,886 cases under each GPL root in the inspected mustpass file. The monolithic-only device-address-command variants and `shader_object_rebind` account for the eight-case difference.
- Basic matrices use buffer counts `{1, 2, 4, 8}` and total buffer sizes `{256, 512, 131072}` bytes. Point-size variants add `_ptsz` where the generator can emit both forms.
- Indirect cases use byte strides `{16, 244, 508, 1004, 2036}` and deliberately exclude the combination that uses both a counter offset and a counter-buffer offset.
- Query generation uses stream IDs `{0, 1, 3, 6, 14}`, source vertex counts `{6, 61, 127, 251, 509}`, topology-adjusted counts, and both 32-bit and 64-bit results.
- Stream families use nonzero stream IDs `{1, 3, 6, 14}`. Some require geometry shaders or `transformFeedbackRasterizationStreamSelect`.
- Point-list cases without tessellation or geometry must write point size, so the generator omits the illegal no-point-size variant.
- Requirement checks reject unsupported pipeline construction, transform feedback, multiview, indirect drawing, device-address commands, geometry or tessellation stages, large points, host query reset, shader objects, excessive strides, and excessive captured component counts.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Transform-feedback semantics | [`vertexpostproc.adoc`](../../../../vulkan-docs/src/chapters/vertexpostproc.adoc#L40-L160) | Defines capture stage, activation, append behavior, counter resume, stride, and output layout. |
| Transform-feedback queries | [`queries.adoc`](../../../../vulkan-docs/src/chapters/queries.adoc#L2515-L2546) | Defines primitives-written/needed accounting and query result retrieval. |
| Counter-driven drawing | [`drawing.adoc`](../../../../vulkan-docs/src/chapters/drawing.adoc#L1949-L1959) | Requires synchronization between counter writes and indirect reads. |
| Graphics pipeline library linking | [`pipelines.adoc`](../../../../vulkan-docs/src/chapters/pipelines.adoc#L713-L722) | Distinguishes fast linking from link-time optimization. |
| Category registration | [`createTests()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackTests.cpp#L36-L53) | Registers the same simple factory for all three construction modes. |
| Parameters and instance routing | [`TestParameters` and `createInstance()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackSimpleTests.cpp#L126-L204) and [`createInstance()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackSimpleTests.cpp#L4497-L4595) | Connect generated dimensions and test types to runtime implementations. |
| Feature and limit gates | [`TransformFeedbackTestCase::checkSupport()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackSimpleTests.cpp#L4597-L4724) | Lists requirement-based pruning. |
| Shader generation | [`TransformFeedbackTestCase::initPrograms()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackSimpleTests.cpp#L4726-L6153) | Generates the stage programs and transform-feedback declarations. |
| Main test matrices | [`createTransformFeedbackSimpleTests()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackSimpleTests.cpp#L6455-L7002) | Generates capture, topology, indirect, query, and special cases. |
| Stream and layout matrices | [`createTransformFeedbackStreamsSimpleTests()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackSimpleTests.cpp#L7004-L7239) | Generates stream, multiquery, holes, and output-limit cases. |
| Root names | [`createTransformFeedbackSimpleTests()` factory](../../../modules/vulkan/transform_feedback/vktTransformFeedbackSimpleTests.cpp#L7264-L7276) | Maps construction modes to the three registered roots. |
| Mustpass roots | [`transform-feedback.txt`](../../../mustpass/main/vk-default/transform-feedback.txt#L110039-L133704) | Confirms current executable paths and root counts. |

## Questions / Risk Points for User Audit

- Does the six-value behavioral grouping give enough detail without pretending that thousands of generated leaves form a single flat parameter?
- Is one common `basic_1_256` shader walkthrough sufficient when later families change stages and declarations but retain the same capture model?
- The page can summarize specialized runtime checks, but each `TestType` owns distinct commands and references. Should a later audit request more detail for any one specialized prefix?

## Conversion Notes for Final Wiki Rewrite

- Use `dEQP-VK.transform_feedback.simple.basic_1_256` for the representative shader walkthrough because it exposes the common output declaration, push constant, capture command sequence, and full buffer verification path.
- Keep transform-feedback append/counter semantics, query counters, and pipeline-library construction as concise Background Knowledge bullets.
- Carry the six behavioral-group values into `## Behavior Parameters` and copy the failure mapping table unchanged.
- Present the large generator inventory as a parameter table and grouped behavior subsections rather than listing thousands of leaves.
- Keep source navigation in the appendix. Preserve only host/device details needed to understand buffer checks, image checks, and query comparisons.
