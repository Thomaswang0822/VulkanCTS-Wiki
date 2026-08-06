## One-Sentence Test Purpose

This test checks fragment-related query results for a full-frame draw in both occlusion and fragment-invocation modes, including primary and secondary command-buffer execution and shader variants that either permit or prevent invocation reuse.

## Background Knowledge

- An occlusion query counts samples that pass the relevant tests. With `VK_QUERY_CONTROL_PRECISE_BIT`, this page expects the exact covered-sample count.
- Pipeline statistics queries count selected pipeline events. `VK_QUERY_PIPELINE_STATISTIC_FRAGMENT_SHADER_INVOCATIONS_BIT` counts fragment-shader invocations, which can differ from covered pixels when an implementation legally reuses invocations for a statically identical, side-effect-free fragment shader.
- A secondary command buffer inherits query state from the primary command buffer. The inheritance fields must match the query type and the render pass in which the draw executes.

## One Concrete Example

The representative case is `query_pool.frag_invocations.frag_invs.primary_with_vertex_color`. The host creates a `64 x 64 x 1` framebuffer, records one oversized triangle, begins a pipeline-statistics query, draws the triangle with the primary command buffer, and reads the query result after submission. The vertex shader passes a color to the fragment shader, so the fragment shader writes an interpolated input rather than a compile-time constant. The result must be at least `4096`, and the copied color image must match blue exactly.

## End-to-End Test Flow

```text
[host] select query type, command-buffer mode, and fragment-shader variant
[host] generate the vertex and fragment GLSL programs
[host] create the framebuffer, graphics pipeline, vertex buffer, and one-slot query pool
[host] create and initialize the storage buffer and descriptor set for atomic variants
[host] record query reset, query begin, render pass, and the full-frame draw
[device] execute the draw and update the query and any atomic counter
[host] copy the color image to a host-visible buffer, synchronize, wait for submission, and read the query result
[host] compare the query result and color image; read back the atomic counter when selected
[host] return pass or failure status
```

For a secondary case, the primary command buffer owns query and render-pass boundaries. A secondary command buffer records the draw with `VkCommandBufferInheritanceInfo`, and the primary executes it inside the render pass.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

`initPrograms()` emits GLSL `#version 460` vertex and fragment shaders. The vertex shader always writes `gl_Position`. The `VERTEX_COLOR` variant adds location 1 input and location 0 output in the vertex shader, plus the matching fragment input. The `ATOMIC_COUNTER` variant adds a storage-buffer block at set 0, binding 0 and performs `atomicAdd(cb.counter, 1u)` before writing the color.

The graphics pipeline uses `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST`, one color attachment with `VK_FORMAT_R8G8B8A8_UNORM`, and one query slot. The three vertices `(-1,-1)`, `(3,-1)`, and `(-1,3)` cover the complete framebuffer.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Color image and readback buffer | yes | yes | fragment shader writes the image; transfer writes the buffer | yes | checks the rendered blue result |
| Vertex buffer | yes | yes | vertex stage reads it | no | supplies the covering triangle and variant colors |
| One-slot query pool | yes | yes through commands | query machinery writes the result | yes | supplies the occlusion or invocation count |
| Atomic storage buffer | only for atomic variants | yes at set 0, binding 0 | fragment shader atomically increments it | yes | checks one storage write per covered pixel |

## What Is Checked

- `occlusion` creates `VK_QUERY_TYPE_OCCLUSION` with `VK_QUERY_CONTROL_PRECISE_BIT` and requires the result to equal `64 * 64 * 1 = 4096`.
- `frag_invs` creates `VK_QUERY_TYPE_PIPELINE_STATISTICS` with `VK_QUERY_PIPELINE_STATISTIC_FRAGMENT_SHADER_INVOCATIONS_BIT`. The vertex-color and atomic variants require at least `4096`. The flat variant uses `64 / maxFragmentSize.width` multiplied by `64 / maxFragmentSize.height` and depth, with each dimension clamped to at least 1. Without `VK_KHR_fragment_shading_rate`, the fallback maximum is `1 x 1`, so the lower bound is `4096`.
- The color readback uses `tcu::floatThresholdCompare()` with a zero threshold in every channel, so the result must equal solid blue exactly.
- Atomic variants require the host-read counter to equal `4096` exactly.

## Behavior Parameter Identification

> **Behavior parameter:** query family and shader variant, with command-buffer mode as an execution axis
>
> **Candidate values:** `occlusion`, `frag_invs`; `FLAT`, `VERTEX_COLOR`, `ATOMIC_COUNTER`; `primary`, `secondary`

## Important Variations and Special Cases

- The flat fragment shader computes the same color everywhere and writes no storage resource. The source therefore applies a lower bound for `frag_invs`, allowing invocation reuse. Vertex-color and atomic variants make the shader result or side effects depend on each fragment, so they use the full-pixel lower bound.
- Secondary cases require inherited queries. Their inheritance data enables occlusion queries only for `occlusion` and selects the fragment-statistics bit only for `frag_invs`.
- `occlusionQueryPrecise` gates occlusion cases, `pipelineStatisticsQuery` gates `frag_invs`, and `fragmentStoresAndAtomics` gates atomic variants. `inheritedQueries` gates every secondary case. Fragment shading rate support is optional and changes only the flat-case lower-bound calculation.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Registration | [`createFragInvocationTests()`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L449-L485) | defines the two families and 12 leaves |
| Query names and parameters | [`QueryType`, `FragShaderVariant`, and `TestParams`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L46-L80) | identifies exact parameter values |
| Feature gates | [`checkSupport()`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L92-L104) | defines per-case requirements |
| Shader generation | [`initPrograms()`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L106-L131) | defines flat, vertex-color, and atomic shader behavior |
| Query setup and inheritance | [`testInvocations()`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L237-L330) | defines query type, flags, and primary/secondary recording |
| Result checks | [`testInvocations()`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L363-L442) | defines bounds, counter, and color checks |
| Registration entrypoint | [`vktQueryPoolTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L42-L55) | attaches `frag_invocations` to `query_pool` |
| Vulkan query semantics | [`query_begin_common.adoc`](../../../../vulkan-docs/src/chapters/commonvalidity/query_begin_common.adoc), [`query_results_common.adoc`](../../../../vulkan-docs/src/chapters/commonvalidity/query_results_common.adoc) | spec validity and result retrieval context |

## Questions / Risk Points for User Audit

- The flat `frag_invs` lower bound follows the implementation's source comment and optional `VK_KHR_fragment_shading_rate` property. It is a CTS policy bound, not a general claim that the Vulkan specification mandates this minimum.
- The source has no separate Vulkan SC hierarchy branch for this family.

## Conversion Notes for Final Wiki Rewrite

Use the vertex-color case as the shader walkthrough anchor. Explain the flat-case lower-bound exception and the atomic side-effect variant in the parameter and failure sections rather than duplicating full walkthroughs.
