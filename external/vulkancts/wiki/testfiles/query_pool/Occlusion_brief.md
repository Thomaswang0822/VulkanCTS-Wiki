## Purpose

This brief explains the `query_pool.occlusion_query` test family before the Level-3 rewrite. The implementation in [`vktQueryPoolOcclusionTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp) covers query recording, result retrieval, reset, result-buffer layout, and rendering variants. The dispatcher only attaches this test family to `query_pool`.

## Background Knowledge

### Occlusion query state

A Vulkan query pool stores asynchronous query state. An occlusion query measures samples that pass the configured tests while a query is active. The result can be read by the host with `vkGetQueryPoolResults` or copied by device commands with `vkCmdCopyQueryPoolResults`; the query also has an availability state. The Vulkan Queries chapter describes these states and both result paths.

### Conservative and precise control

`VK_QUERY_CONTROL_PRECISE_BIT` requests exact sample counts for occlusion queries when `occlusionQueryPrecise` is enabled. Without it, the implementation checks visibility rather than requiring one exact positive count, except that an expected zero remains an exact zero check. The `vkCmdBeginQuery` common-validity rules also require the precise feature for this flag and require graphics-capable command-pool support for occlusion queries.

### Result layout

Each result element can contain a 32-bit or 64-bit value, optionally followed by an availability value. `stride` advances between elements. The stride tests therefore exercise both API decoding and device writes into a destination buffer, including a destination offset and zero stride in the command-copy path.

## One Concrete Example

For `get_results_precise_size_64_wait_queue_without_availability_draw_triangles`, the test records three queries over three triangle scenes: a fully visible triangle, a partly occluded triangle, and a fully occluded triangle. The fragment shader writes a constant color; the geometry and depth positions, not shader data, produce the visibility differences. The host waits for the queue, reads two query results at a time for the basic path or three results for the matrix path, and compares them with the expected ranges from `validateResults()`.

## End-to-End Test Flow

```text
[host] choose one registered test vector
[host] create an occlusion query pool and graphics resources
[host] record reset, render-pass, query begin/end, draw, and optional clear/blit/resolve commands
[device] execute the vertex and fragment shaders and count passing samples while each query is active
[host] wait according to `WAIT_QUEUE`, `WAIT_QUERY`, or `WAIT_NONE`
[host] read results with `vkGetQueryPoolResults` or inspect a buffer written by `vkCmdCopyQueryPoolResults`
[host] check result values, availability, and post-reset state
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The regular matrix generates `vert` and `frag` GLSL programs in [`QueryPoolOcclusionTest::initPrograms()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1524-L1545). The fragment stage writes a constant color and optionally discards alternating pixels. The vertex stage passes input positions to `gl_Position` and sets `gl_PointSize` to `1.0`.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|---|---:|---:|---:|---:|---|
| Vertex buffer | yes | yes | read by vertex input | no | Selects visible, partial, and occluded geometry |
| Color/depth images and framebuffer | yes | yes | written by rendering | no | Defines sample coverage and depth testing |
| `VkQueryPool` | yes | yes through query commands | updated by query execution | yes | Stores value and availability for each query |
| Query-results buffer | yes, copy modes | yes | written by query-result copy | yes | Tests stride, availability placement, and destination offset |

## What Is Checked

- The basic path uses two queries, one around no draw work and one around a clear and/or draw, then checks exact results.
- The matrix path uses three query slots for all, partially occluded, and fully occluded geometry. Point-list results expect `3`, `1`, and `0`. Triangle results use the source-defined tolerance ranges, and `_discard` halves the expected covered area.
- Precise queries and zero expectations use bounded comparisons. Conservative positive cases only require a non-zero result.
- Availability must be non-zero when a result is expected to be ready. `WAIT_NONE` may leave it unavailable. `copy_reset` requires availability to be zero after the recorded reset and does not inspect the value.

## Behavior Parameter Identification

> **Behavior parameter:** result and visibility behavior group
>
> **Candidate values:** `basic_conservative`, `basic_precise`, result retrieval mode (`get`, `get_reset`, `get_create_reset`, `copy`, `copy_reset`), rendering variant (points, triangles, discard, clear, no color attachments, blit, resolve), and result layout variant (32/64-bit, availability, stride, destination offset, device address)

The final page should present the registered smoke cases and matrices as separate behavior groups. The primary semantic axis is the result and visibility behavior, while retrieval and layout dimensions explain how the same query observations are transported and reset.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `basic_conservative` | Basic query begin/end or conservative result retrieval does not report the required zero/non-zero observations. |
| `basic_precise` | Precise occlusion counting or precise-feature handling is incorrect. |
| `get`, `get_reset`, `get_create_reset` | Host result retrieval, host reset, or query-pool create-reset behavior is incorrect. |
| `copy`, `copy_reset` | Device-side result copy, copy reset, or result-buffer synchronization is incorrect. |
| points / triangles / `_discard` | Sample coverage, depth testing, primitive rasterization, or fragment discard handling is incorrect. |
| clear / no color attachments / blit / resolve | The tested render-pass or additional-operation path changes query accounting incorrectly. |
| 32/64-bit, availability, stride, destination offset, device address | Result element width, availability placement, stride addressing, offset handling, or the optional device-address copy path is incorrect. |

## Important Variations and Special Cases

- The functional matrix omits `WAIT_QUERY` with `get_reset` because the implementation would read again after reset and Vulkan permits that host call not to return in finite time.
- `copy_reset` is registered only with availability because the test checks the cleared availability bit.
- Point tests omit `_discard` because one-pixel points do not make halving fragment coverage meaningful.
- Zero stride appears only in the command-copy matrix and does not use the explicit destination-offset suffix.
- `_device_address` cases are sampled for copy modes in non-Vulkan-SC builds. Vulkan SC also omits the query-pool create-reset flag.
- The no-attachment function cases use a 2x2 framebuffer and a half-width scissor. They expect half the samples for one and four samples per pixel.

## Source Mapping

| Topic | Source link | Why it matters |
|---|---|---|
| Query pool creation | [`makeOcclusionQueryPool()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L54-L73) | Creates `VK_QUERY_TYPE_OCCLUSION` pools and shows Vulkan SC handling. |
| Test vector and enums | [`OcclusionQueryTestVector`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L329-L396) | Defines behavioral and layout dimensions. |
| Functional execution | [`OcclusionQueryTestInstance::iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L821-L942) | Shows submission, waits, copyback, and final status. |
| Result validation | [`validateResults()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1357-L1472) | Defines exact, tolerant, availability, and reset checks. |
| Registration matrix | [`QueryPoolOcclusionTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1691-L2040) | Defines names, exclusions, and device-address sampling. |
| Vulkan query semantics | [`Queries`](../../../../vulkan-docs/src/chapters/queries.adoc) | Defines asynchronous query state and result paths. |
| Begin-query validity | [`query_begin_common.adoc`](../../../../vulkan-docs/src/chapters/commonvalidity/query_begin_common.adoc) | Grounds precise-feature and graphics-queue constraints. |

## Questions / Risk Points for User Audit

- Is the split between visibility semantics and result transport clear?
- Are the three matrix query slots and their expected coverage easy to follow?
- Does the distinction between unavailable results and zero results remain clear?
- Is the no-color-attachment function case sufficiently separate from the main matrix?

## Conversion Notes for Final Wiki Rewrite

Keep Background Knowledge to query state, precise versus conservative semantics, and result layout. Use the three-query geometry as the concrete runtime explanation. Put the matrix dimensions in a compact table and copy the failure mapping table unchanged. Shader analysis is relevant because the generated fragment shader includes an optional discard branch; use the mandated analyzer/disassembler workflow for one exact triangle case. Keep the full source links in the appendix rather than leading with filenames.
