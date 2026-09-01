# Understanding Brief: transform feedback primitive restart

## One-Sentence Test Purpose

This test checks whether indexed transform-feedback draws honor primitive restart and primitive topology when each state is supplied either by the graphics pipeline or by dynamic commands.

## Background Knowledge

### Indexed primitive assembly and restart

An indexed draw reads indices from the bound index buffer and groups them according to the active `VkPrimitiveTopology`. With primitive restart enabled, the special value for `VK_INDEX_TYPE_UINT16` is `0xFFFF`; encountering that value ends the current strip or other assembled primitive and starts the next one. Vulkan compares the index with the restart value before adding `vertexOffset` ([drawing](../../../../vulkan-docs/src/chapters/drawing.adoc#L48-L89)).

A triangle strip can therefore contain several runs separated by restart markers. An index list with restart disabled treats the same 16-bit value as an ordinary vertex index. This test uses both interpretations of one index buffer so the capture stream exposes whether the state changed at the intended draw boundary.

### Transform feedback and degenerate primitives

When transform feedback is active, the last pre-rasterization shader's outputs are assembled into primitives and appended to bound transform-feedback buffers. Vulkan permits an implementation to discard a primitive whose vertices contain equal positions before primitive assembly ([transform feedback](../../../../vulkan-docs/src/chapters/vertexpostproc.adoc#L42-L78)). The test therefore accepts a smaller capture count when its expected triangle is degenerate, but still checks every non-degenerate captured position.

The transform-feedback counter stores the byte position at which the next vertex data is written. Ending one capture and resuming it requires a transform-feedback counter write-to-read barrier ([`vkCmdBeginTransformFeedbackEXT`](../../../../vulkan-docs/src/chapters/vertexpostproc.adoc#L433-L487), [synchronization](../../../../vulkan-docs/src/chapters/synchronization.adoc#L1140-L1160)).

## One Concrete Example

The shared 16-bit index sequence is:

```text
0, 1, 65535, 9, 65535, 65535, 2000, 3000, 4000
```

With triangle-strip assembly and restart enabled, only `2000, 3000, 4000` forms a complete non-degenerate triangle. With triangle-list assembly and restart disabled, the nine indices form three triangles, and the shader maps the restart marker `65535` to `(-1,-1,-1,-1)` so that value can be captured without an out-of-range vertex fetch.

## End-to-End Test Flow

```text
[host] choose one of four static/dynamic state combinations
[host] create a host-visible uint16 index buffer containing three restart markers
[host] create a graphics pipeline, transform-feedback buffer, and 4-byte transform-feedback counter buffer
[host] bind the index and transform-feedback buffers
[host] begin transform feedback and draw the index buffer with strip/restart-enabled state
[device] run the vertex shader and capture assembled vertices
[host] for the three cases needing a second pipeline, end transform feedback, bind the other pipeline, and issue a counter write-to-read barrier
[host] resume transform feedback and draw with list/restart-disabled state
[host] restore strip/restart-enabled state and draw the third segment
[host] end transform feedback, wait for completion, invalidate the host-visible allocations, and inspect the counter and captured positions
[host] allow skipped degenerate triangles, require the exact remaining counter value and positions, then return pass, quality warning, or failure
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The case generates one GLSL vertex shader. It declares transform-feedback output for `gl_Position`, reads `gl_VertexIndex`, and substitutes `(-1.0,-1.0,-1.0,-1.0)` when the index equals the 16-bit restart marker. The four registration leaves reuse this shader ([`initPrograms`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L101-L116)).

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `indexBuffer` | yes | yes, as `VK_INDEX_TYPE_UINT16` | read by indexed draws | yes, only for test setup inspection if needed | Supplies the restart markers and vertex indices. |
| `xfbBuffer` | yes, host-visible | yes, binding 0 | written by transform feedback | yes | Stores the captured `gl_Position` values. |
| `xfbCounterBuffer` | yes, host-visible | yes, as the transform-feedback counter | written at each `vkCmdEndTransformFeedbackEXT` and read when capture resumes | yes | Tracks the byte offset across the three draw segments. |
| vertex shader module and graphics pipelines | yes | yes | executes vertex processing and input assembly | no | Connects the index interpretation to captured output. |

## What Is Checked

- The counter must not exceed `expectedResults.size() * sizeof(tcu::Vec4)`, which is the maximum expected capture size.
- The host compares each expected triangle with the next actual triangle. If an expected triangle has equal positions, the host may skip it because Vulkan permits degenerates to be discarded during transform feedback.
- Every non-degenerate expected triangle must match the captured `gl_Position` values exactly for its three vertices.
- The final counter must equal the expected byte count minus three `tcu::Vec4` values for each skipped degenerate triangle.
- A position mismatch or counter mismatch fails the case. A valid run that skips one or more degenerate triangles returns a quality warning; otherwise the case passes ([`iterate`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L352-L413)).

## Behavior Parameter Identification

> **Behavior parameter:** primitive restart and primitive topology state sourcing
>
> **Candidate values:** `dynamic_primitive_restart_dynamic_primitive_topology`, `dynamic_primitive_restart_static_primitive_topology`, `static_primitive_restart_dynamic_primitive_topology`, `static_primitive_restart_static_primitive_topology`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `dynamic_primitive_restart_dynamic_primitive_topology` | Incorrect interaction between `vkCmdSetPrimitiveRestartEnable`, `vkCmdSetPrimitiveTopology`, indexed primitive assembly, and transform-feedback capture. |
| `dynamic_primitive_restart_static_primitive_topology` | Dynamic primitive-restart state is not applied to the indexed draw or does not agree with the statically selected topology. |
| `static_primitive_restart_dynamic_primitive_topology` | Dynamic topology state is not applied to the indexed draw or does not agree with the pipeline's restart state. |
| `static_primitive_restart_static_primitive_topology` | Pipeline input-assembly primitive-restart or topology state is not honored during transform-feedback capture. |

## Important Variations and Special Cases

- The two boolean parameters form a complete 2x2 matrix. Each registration leaf changes whether primitive restart and primitive topology come from pipeline creation or dynamic commands ([`createTransformFeedbackPrimitiveRestartTests`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L426-L440)).
- When both states are dynamic, the test uses one pipeline and changes both states between draws. In the other three leaves, it uses pipeline A for strip/restart-enabled draws and pipeline B for list/restart-disabled draws, stopping and resuming transform feedback between pipeline binds ([`iterate`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L146-L237), [`iterate`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L293-L334)).
- The transform-feedback allocation includes 12 extra `tcu::Vec4` slots. The extra space lets the host inspect an oversized counter before copying the expected-size result array ([`iterate`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L264-L272), [`iterate`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L358-L365)).

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Parameter structure and support gates | [`PrimitiveRestartInstance::Params` and `checkSupport`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L48-L99) | Defines the two matrix dimensions and the required extensions. |
| Generated vertex shader | [`initPrograms`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L101-L116) | Defines the captured position for the restart marker. |
| Index data and pipeline state | [`iterate`, index and pipeline setup](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L118-L237) | Shows the uint16 marker, topologies, restart values, and dynamic-state list. |
| Draw sequence and counter barriers | [`iterate`, command recording](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L284-L347) | Shows the three draws and resume barriers. |
| Result checking | [`iterate`, validation and status](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L352-L413) | Defines counter bounds, degenerate handling, comparisons, and final status. |
| Registration and mustpass | [`createTransformFeedbackPrimitiveRestartTests`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L426-L440), [`transform-feedback.txt`](../../../mustpass/main/vk-default/transform-feedback.txt#L2169-L2172) | Confirms the four executable registration leaves. |
| Primitive restart semantics | [`drawing.adoc`](../../../../vulkan-docs/src/chapters/drawing.adoc#L48-L89) | Defines the special index, indexed-draw scope, and restart assembly behavior. |
| Transform-feedback capture semantics | [`vertexpostproc.adoc`](../../../../vulkan-docs/src/chapters/vertexpostproc.adoc#L42-L78) | Defines active capture and permitted degenerate-primitives discard. |

## Questions / Risk Points for User Audit

- Does the distinction between a pipeline-supplied state and a dynamically set state remain clear for all four leaves?
- Is the three-draw counter-resume sequence clear, including the barrier needed between `vkCmdEndTransformFeedbackEXT` and `vkCmdBeginTransformFeedbackEXT`?
- Is the `0xFFFF` marker's shader mapping clear enough to explain why the list draw can capture it safely?
- Should the quality-warning result for skipped degenerates be called out separately from a normal pass in reader-facing documentation?
- Are the spec references sufficient for the current Vulkan documentation revision, especially the transform-feedback permission to discard degenerate primitives?

## Conversion Notes for Final Wiki Rewrite

- Use the four exact registration leaves as the primary behavioral axis and copy the failure mapping table into the final page unchanged.
- Distill the background to indexed restart semantics and transform-feedback capture, including the degenerate-primitive exception.
- Use the static/static leaf as the representative shader path because it exposes the same generated vertex shader while keeping the pipeline state choices visible without dynamic-state commands.
- Keep the full matrix in the parameter table, explain the one-pipeline versus two-pipeline command sequence in runtime, and move detailed source navigation to the appendix.
- Include one shader walkthrough. The vertex shader is the only generated shader and its SPIR-V should be generated from the reconstructed GLSL with the default source-collection target.
