# Understanding Brief: conditional_rendering transform feedback

## One-Sentence Test Purpose

This test checks whether conditional rendering correctly controls transform-feedback draw commands across the supported draw-command variants.

## Background Knowledge

### Conditional rendering predicates

`VK_EXT_conditional_rendering` makes selected commands conditional on a 32-bit value in a buffer. A zero predicate discards affected commands and a nonzero predicate executes them. The predicate can be inverted with `VK_CONDITIONAL_RENDERING_INVERTED_BIT_EXT`.

Why it matters here:
- The test uses two occlusion-query results as predicates for separate transform-feedback sections.
- The command under test is inside a conditional-rendering block, while query copy and synchronization occur outside that block.

### Transform feedback and geometry streams

Transform feedback writes selected vertex-stage or geometry-stage outputs into buffers while transform feedback is active. A geometry shader can assign outputs to different streams, and the host can bind a separate buffer range for each stream.

Why it matters here:
- The geometry shader selects one stream from a push constant and emits one point to that stream.
- The test needs four transform-feedback buffers and four streams, so `geometryStreams`, `maxTransformFeedbackBuffers`, and `maxTransformFeedbackStreams` are checked.

## One Concrete Example

The representative `draw` case records two query-producing draws, then records four transform-feedback draws. The first query is expected to be zero and therefore suppresses its conditional section. The second query is expected to be nonzero and allows its conditional section. The four stream passes write values `1.0`, `2.0`, `3.0`, and `4.0` when their predicates allow execution.

Conceptually, the geometry shader has four output declarations:

```glsl
// Conceptual excerpt, normalized from the generated geometry shader.
layout(location = 0, stream = 0, xfb_offset = 0, xfb_stride = 4, xfb_buffer = 0) out float output1;
layout(location = 1, stream = 1, xfb_offset = 0, xfb_stride = 4, xfb_buffer = 1) out float output2;
layout(location = 2, stream = 2, xfb_offset = 0, xfb_stride = 4, xfb_buffer = 2) out float output3;
layout(location = 3, stream = 3, xfb_offset = 0, xfb_stride = 4, xfb_buffer = 3) out float output4;
```

## End-to-End Test Flow

```text
[host] select one of the nine registered draw command variants
[host] build the vertex, geometry, and fragment shader programs
[host] create a two-entry query result buffer and a 24-float transform-feedback buffer
[host] record two query draws, using draw index 2 and then draw index 1
[device] execute the query draws and produce two occlusion-query results
[host] copy the query results into the conditional-rendering buffer and add a transfer-to-conditional-rendering barrier
[host] for each stream, bind one six-float range, push the stream index, and begin conditional rendering
[device] begin transform feedback and execute the selected draw command if its query predicate permits it
[host] end transform feedback and conditional rendering, then add a transform-feedback-to-host barrier
[host] wait for the queue, invalidate the allocation, and inspect the query and transform-feedback buffers
[host] decide pass/fail from the query expectations and all 24 float values
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `AddProgramsDraw::init` adds `VertexFetch.vert`, `VertexFetch.geom`, `VertexFetchWritePoint.geom`, and `VertexFetch.frag` to the source collection.
- The vertex shader forwards position and color. The fragment shader writes the color. The geometry shader emits one point on the stream selected by the integer push constant and assigns that stream's transform-feedback output.
- The pipeline uses the point-list stream pipeline for transform feedback. The normal draw pipeline and the stream pipeline share the vertex and fragment stages.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Query pool | yes | yes | written by occlusion queries | copied to query buffer | Supplies the two predicates. |
| Query buffer | yes | yes | written by query-result copy and read by conditional rendering | yes | Holds two 32-bit predicate values. |
| Transform-feedback buffer | yes | yes | written by active transform feedback | yes | Holds four six-float stream ranges. |
| Vertex buffer | yes | yes | read by draw commands | no | Supplies positions, colors, and the draw-indexed data layout. |
| Index and indirect buffers | variant-dependent | variant-dependent | read by the selected command | no | Supply parameters for indexed, indirect, multi-draw, and count variants. |
| Geometry push constant | yes | yes | read by the geometry shader | no | Selects the stream and therefore the output value. |

## What Is Checked

- Query result 0 must equal zero. Query result 1 must be nonzero.
- The host checks all 24 transform-feedback floats. Indices `0..5` and `12..17` must be `0.0`; indices `6..11` must be `2.0`; and indices `18..23` must be `4.0`.
- The first mismatch returns a failing test status. A passing case returns `Pass` after all values match.

## Behavior Parameter Identification

> **Behavior parameter:** `transform_feedback` test family child, the draw command variant
>
> **Candidate values:** `draw`, `draw_indexed`, `draw_indirect`, `draw_indexed_indirect`, `draw_multi_ext`, `draw_multi_indexed_ext`, `draw_indirect_byte_count_ext`, `draw_indirect_count`, `draw_indexed_indirect_count`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `draw` | Conditional execution or transform-feedback handling for direct draws. |
| `draw_indexed` | Conditional execution or index-buffer handling for indexed draws. |
| `draw_indirect` | Conditional execution or indirect-parameter fetch for indirect draws. |
| `draw_indexed_indirect` | Conditional execution, index-buffer handling, or indexed indirect-parameter fetch. |
| `draw_multi_ext` | Conditional execution or `VK_EXT_multi_draw` handling. |
| `draw_multi_indexed_ext` | Conditional execution, index-buffer handling, or multi-indexed draw handling. |
| `draw_indirect_byte_count_ext` | Conditional execution or transform-feedback byte-count draw handling. |
| `draw_indirect_count` | Conditional execution or indirect-count draw handling. |
| `draw_indexed_indirect_count` | Conditional execution, index-buffer handling, or indexed indirect-count draw handling. |

## Important Variations and Special Cases

- All nine children use the same transform-feedback shader logic. The command child changes how the draw is issued and which supporting buffer is prepared.
- `draw_indirect_count` and `draw_indexed_indirect_count` require `VK_KHR_draw_indirect_count`.
- `draw_multi_ext` and `draw_multi_indexed_ext` require `VK_EXT_multi_draw`.
- `draw_indirect_byte_count_ext` additionally requires the `transformFeedbackDraw` property.
- Every case requires `VK_EXT_conditional_rendering`, `VK_EXT_transform_feedback`, the `conditionalRendering` feature, and `geometryStreams`. The implementation also requires at least four transform-feedback buffers and four streams.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Command names and test-family registration | [getDrawCommandTypeName() and init()](../../../modules/vulkan/conditional_rendering/vktConditionalTransformFeedbackTests.cpp#L64-L90) | Defines the nine direct children and attaches each child to the same implementation. |
| Capability checks | [checkSupport()](../../../modules/vulkan/conditional_rendering/vktConditionalTransformFeedbackTests.cpp#L131-L160) | Defines required extensions, features, command-specific requirements, and transform-feedback limits. |
| Draw dispatch | [recordDraw()](../../../modules/vulkan/conditional_rendering/vktConditionalTransformFeedbackTests.cpp#L386-L455) | Maps each behavior value to its Vulkan draw command. |
| Query and conditional-rendering flow | [iterate()](../../../modules/vulkan/conditional_rendering/vktConditionalTransformFeedbackTests.cpp#L457-L601) | Shows query setup, barriers, conditional rendering, transform feedback, and submission order. |
| Result check | [iterate() result validation](../../../modules/vulkan/conditional_rendering/vktConditionalTransformFeedbackTests.cpp#L603-L634) | Defines the exact query and 24-float pass conditions. |
| Generated shaders | [AddProgramsDraw::init()](../../../modules/vulkan/conditional_rendering/vktConditionalTransformFeedbackTests.cpp#L636-L714) | Defines the vertex, geometry, and fragment shader sources. |
| Shared conditional buffer creation | [createConditionalRenderingBuffer()](../../../modules/vulkan/conditional_rendering/vktConditionalRenderingTestUtil.cpp#L70-L121) | Documents host-visible and device-local conditional predicate buffers used by the category. |
| Conditional rendering semantics | [Conditional Rendering](../../../../vulkan-docs/src/chapters/drawing.adoc#drawing-conditional-rendering) | Defines zero and nonzero predicate behavior, inversion, active scope, and synchronization stage. |
| Transform-feedback synchronization | [transform-feedback access and stage rules](../../../../vulkan-docs/src/chapters/synchronization.adoc#synchronization-pipeline-stages) | Defines transform-feedback writes and the transform-feedback pipeline stage. |

## Questions / Risk Points for User Audit

- Does the direct-draw representative explain why the four stream ranges receive different expected values?
- Is the distinction between query predicate production and transform-feedback result checking clear?
- Should the final page include the full generated geometry shader walkthrough or keep the shader section shorter?
- Are the command-specific feature requirements visible without repeating the full capability helper?

## Conversion Notes for Final Wiki Rewrite

- Use `draw` as the representative path because it exercises the shared geometry shader without indirect-buffer setup.
- Keep the nine command children in the registration tree and make the command child the primary behavior axis.
- Distill conditional rendering and transform-feedback concepts into short prerequisite bullets; keep concrete query values and buffer ranges in the behavior and runtime sections.
- Copy the `### Failure Cause Mapping` table directly into the final page.
- Write fresh cause-analysis subsections for the shared predicate, transform-feedback capture, and command-specific draw paths.
- The final page needs one geometry-shader walkthrough. The vertex and fragment stages are support stages and can be described in `Additional Info` rather than shown as separate walkthrough stages.
