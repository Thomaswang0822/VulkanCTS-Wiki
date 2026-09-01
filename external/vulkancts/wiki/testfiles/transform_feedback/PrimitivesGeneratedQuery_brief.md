# Understanding Brief: primitives_generated_query

## One-Sentence Test Purpose

This test checks whether `VK_QUERY_TYPE_PRIMITIVES_GENERATED_EXT` reports the primitives produced by the graphics pipeline, including its interaction with transform-feedback queries, query readback, stream selection, and concurrent query commands.

## Background Knowledge

### Primitives-generated and transform-feedback queries

A primitives-generated query counts primitives produced by the graphics pipeline before rasterization. A transform-feedback query reports transform-feedback stream results, including generated primitives and written primitives. The Vulkan query model stores results asynchronously in a query pool; the host can read them or a command can copy them to a buffer.

Why it matters here:
- The test can compare the primitives-generated count with the transform-feedback generated count while transform feedback is active.
- Rasterizer discard and fragment-output choices must not be mistaken for failure to generate primitives, because those operations occur after the relevant pre-rasterization stages.

### Streamed geometry and generated primitives

Geometry shaders can emit primitives to stream 0 or a nonzero stream with `EmitStreamVertex`, and `EndStreamPrimitive` closes the current primitive. A topology determines how many vertices form one primitive and how many primitives are formed from an input vertex count. Tessellation evaluation uses patch-list input and produces triangle primitives for the test's fixed tessellation levels.

Why it matters here:
- The test exercises default, stream 0, and stream 1 query indices, including cases where primitives-generated and transform-feedback queries use different streams.
- The host's expected values depend on topology assembly, not simply on the number of vertex shader invocations.

## One Concrete Example

Consider the representative path `dEQP-VK.transform_feedback.primitives_generated_query.get.queue_reset.32bit.geom.xfb.rast.triangle_list.pgq_default_xfb_default.single_draw.pqg_first.none`.

The generated geometry shader receives triangle-list primitives and emits three vertices as one triangle-strip primitive. It writes `vec4(42)` to the transform-feedback output and emits the primitive on the default stream:

```glsl
#version 450
layout(triangles) in;
layout(triangle_strip, max_vertices = 3) out;
layout(xfb_buffer = 0, xfb_offset = 0, xfb_stride = 16, location = 0, stream = 0) out vec4 xfb;
void main (void)
{
    xfb = vec4(42);
    gl_Position = gl_in[0].gl_Position;
    EmitVertex();
    gl_Position = gl_in[0].gl_Position;
    EmitVertex();
    gl_Position = gl_in[0].gl_Position;
    EmitVertex();
    EndPrimitive();
}
```

This is a reconstructed example of the source-generated branch in `PrimitivesGeneratedQueryTestCase::initPrograms()`. The host supplies 32 expected primitives, so the triangle-list input buffer contains 96 vertices. With one draw and one query, both the primitives-generated count and the transform-feedback generated count should be 32. Transform feedback writes 29 primitives because the test sets `primitivesWritten = primitivesGenerated - 3` for the buffer-size check.

## End-to-End Test Flow

```text
[host] choose read/reset/result-width/stage/XFB/rasterization/topology/stream/query-order parameters
[host] create 64x64 attachments when the rasterization case needs them, a host-visible vertex buffer, query pools, and optional transform-feedback/result buffers
[host] generate the vertex, optional tessellation, geometry, and fragment GLSL programs and create the graphics pipeline
[host] fill the vertex buffer for 32 expected primitives and flush it
[host] reset query pools with vkCmdResetQueryPool and a waited submission, or use vkResetQueryPool on the host
[host] record one or two draws, placing primitives-generated and transform-feedback query begin/end commands in the selected order; optionally add a draw before or after the active queries
[device] execute the selected graphics stages, generate primitives, optionally capture transform-feedback data, and update the active queries
[host] read query results with vkGetQueryPoolResults or copy them with vkCmdCopyQueryPoolResults, then wait for completion and invalidate copied allocations
[host] check generated counts, written counts, and requested availability values against the expected topology-dependent values
```

The `concurrent` family uses a separate flow: it begins overlapping query types around direct or indirect draws, executes secondary command buffers where selected, and checks the resulting query values and a copied color image.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- The main generator emits a vertex shader, plus tessellation-control and tessellation-evaluation shaders for `tese`, a geometry shader for `geom`, and a fragment shader unless rasterizer discard is selected. The branch is in [`PrimitivesGeneratedQueryTestCase::initPrograms()`](../../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L1298-L1461).
- The geometry shader maps the selected input topology to an output topology and emits the selected number of vertices. Nonzero stream cases use `EmitStreamVertex` and `EndStreamPrimitive`; multiple streams can require two output primitive groups. See [`initPrograms()`](../../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L1373-L1437).
- The concurrent family generates a geometry shader with special output for triangle strips with adjacency and optional output on stream 0 before the selected PGQ/XFB stream. See [`ConcurrentPrimitivesGeneratedQueryTestCase::initPrograms()`](../../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L2450-L2606).
- The host creates a graphics pipeline using the selected shader stage and topology. [`makeGraphicsPipeline()`](../../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L892-L1043) supplies the generated shader modules and optional dynamic color-write state.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Host-visible vertex buffer | yes | yes | read by vertex input | no | Supplies enough vertices for 32 topology-dependent primitives. |
| Primitives-generated query pool | yes | through query commands | updated by the device | yes | Holds `VK_QUERY_TYPE_PRIMITIVES_GENERATED_EXT` results. |
| Transform-feedback query pool | yes, only with XFB | through query commands | updated by the device | yes | Provides generated and written counts for the cross-check. |
| Transform-feedback buffer | yes, only with XFB | yes | written by transform feedback | not directly | Gives the XFB query a capture target and determines the expected written capacity. |
| Query result buffer | yes, only for `copy` | yes as a transfer destination | written by query-result copy | yes | Receives results before host inspection. |
| Color attachment and view | yes, for rasterizing cases | yes through framebuffer | written by fragment operations | only in concurrent cases | Keeps ordinary rasterization and concurrent query paths executable. |
| Depth/stencil attachment and view | yes, for `_ds` rasterization cases | yes through framebuffer | used by the render pass | no | Exercises color-write-disabled cases with a depth/stencil attachment. |

## What Is Checked

- For each query index, the primitives-generated result equals `primitivesGenerated * drawCount`, where `primitivesGenerated` is 32 and `drawCount` is 1 or 2.
- When transform feedback is enabled, its generated count equals the same value and its written count equals `primitivesGenerated - 3`, which is 29.
- When availability is requested, each selected query's availability value equals 1.
- A mismatch returns a failing `tcu::TestStatus`; otherwise the main family returns `Counters OK`. The checks are in [`PrimitivesGeneratedQueryTestInstance::iterate()`](../../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L777-L870).

## Behavior Parameter Identification

> **Behavior parameter:** test family
>
> **Candidate values:** `get`, `copy`, `concurrent`

The `get` and `copy` families share the same query setup and counter contract but exercise different result paths. `concurrent` uses a distinct implementation and query-overlap scenarios, so the test family is the clearest primary behavioral axis for failure mapping.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `get` | Incorrect primitives-generated or transform-feedback query accounting, query reset/order handling, result-width or availability handling, or host `vkGetQueryPoolResults` interpretation. |
| `copy` | Incorrect query accounting or `vkCmdCopyQueryPoolResults` result layout, synchronization, stride, width, or availability handling. |
| `concurrent` | Incorrect interaction between overlapping query types, secondary command-buffer execution, pipeline-statistics queries, indirect draws, or stream-specific query state. |

## Important Variations and Special Cases

- Result widths include `32bit`, `64bit`, `pgq_32bit_xfb_64bit`, and `pgq_64bit_xfb_32bit`. Mixed widths are generated only when transform feedback is enabled.
- The main family covers `vert`, `tese`, and `geom`. Patch lists are paired with tessellation evaluation; adjacency topologies and nondefault streams are paired with geometry shaders.
- Rasterization cases include discard, ordinary rasterization, empty fragment shader, no attachment, and static or dynamic color-write disablement. Availability cases are limited to selected topologies, rasterization cases, and single-draw command-buffer cases.
- The query reset dimension selects queue reset through `vkCmdResetQueryPool` or host reset through `vkResetQueryPool`. The read dimension selects host `get` or device-side `copy`.
- Concurrent cases cover `two_xfbq_inside_pgq`, `pgq_secondary_cmd_buffers`, and `pipeline_statistics_1` through `pipeline_statistics_3`, each with `draw` and `indirect` variants.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Main generator and pruning | [`testGenerator()`](../../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L2608-L2987) | Defines names, parameter values, and intentional exclusions. |
| Main feature checks | [`PrimitivesGeneratedQueryTestCase::checkSupport()`](../../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L1243-L1295) | Defines extension, feature, property, and stage requirements. |
| Main shader generation | [`PrimitivesGeneratedQueryTestCase::initPrograms()`](../../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L1298-L1461) | Defines generated shader stages and stream emission. |
| Main host execution | [`PrimitivesGeneratedQueryTestInstance::iterate()`](../../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L314-L871) | Defines resources, query commands, synchronization, readback, and checks. |
| Concurrent support and shaders | [`ConcurrentPrimitivesGeneratedQueryTestCase`](../../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L2376-L2606) | Defines concurrent feature requirements and generated stages. |
| Concurrent registration | [`concurrentGroup`](../../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L2989-L3057) | Defines the five concurrent test-family leaves and draw modes. |
| Vulkan query semantics | [Queries chapter](https://docs.vulkan.org/spec/latest/chapters/queries.html) | Defines asynchronous query pools, host reads, device copies, and query result availability. |
| Transform feedback semantics | [Fixed-Function Vertex Post-Processing chapter](https://docs.vulkan.org/spec/latest/chapters/vertexpostproc.html) | Defines transform-feedback placement and primitive capture behavior. |
| Feature enablement | [Features chapter](https://docs.vulkan.org/spec/latest/chapters/features.html) | Defines the need to enable supported fine-grained features at device creation. |
| Registration evidence | [`transform-feedback.txt`](../../../mustpass/main/vk-default/transform-feedback.txt#L2173-L110038) | Contains the registered `primitives_generated_query` paths, including `get`, `copy`, and `concurrent`. |

## Questions / Risk Points for User Audit

- Should the final page use `get`, `copy`, and `concurrent` as the sole behavior-axis values, or should it split the main matrix by read mode and treat `concurrent` separately?
- Is the representative geometry shader sufficient, or should the final page also show the tessellation evaluation branch because patch-list behavior is a distinct stage path?
- The source names the mixed result type `pgq_32bit_xfb_64bit` and `pgq_64bit_xfb_32bit`; the final page calls these mixed-width cases.
- The mustpass file is generated and contains a very large range. The source generator is the authority for pruning semantics, while the mustpass file confirms registered paths.

## Conversion Notes for Final Wiki Rewrite

- Distill the query-pool and transform-feedback concepts into a short page-local `Background Knowledge` section.
- Use one geometry-shader walkthrough for a concrete XFB comparison case. Generate its SPIR-V with `shader-disassembler`; do not hand-write assembly.
- Keep the full dimension inventory in `Parameter Dimensions and Observed Values`, then explain `get`, `copy`, and `concurrent` under `Behavior Parameters`.
- Copy the `### Failure Cause Mapping` table directly into the final page, then write fresh `### Cause Analysis` subsections.
- Put detailed source links in `Source Reference Appendix`; keep the final narrative focused on what the query results mean and how the host validates them.
