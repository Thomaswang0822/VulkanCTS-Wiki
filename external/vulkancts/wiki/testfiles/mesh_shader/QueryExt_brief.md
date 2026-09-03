# Understanding Brief: EXT Mesh Shader Query Tests

## One-Sentence Test Purpose

This test checks whether EXT mesh-shader drawing, mesh primitive queries, and task/mesh pipeline-statistics queries report results with the required reset, retrieval, availability, inheritance, and multiview behavior.

## Background Knowledge

### Query state and retrieval

A Vulkan query has an availability state and numerical result storage. `vkCmdResetQueryPool` or `vkResetQueryPool` makes it unavailable and leaves its numerical value undefined. `vkCmdEndQuery` makes the result available. Applications can retrieve the result through `vkCmdCopyQueryPoolResults` or `vkGetQueryPoolResults` [query operation](../../../../vulkan-docs/src/chapters/queries.adoc#queries-operation).

Why it matters here:

- `VK_QUERY_RESULT_WAIT_BIT` waits for prior writes to the requested query, while a non-waiting host read may return `VK_NOT_READY`.
- `VK_QUERY_RESULT_PARTIAL_BIT` permits an intermediate value for an unavailable query, and `VK_QUERY_RESULT_WITH_AVAILABILITY_BIT` appends a 32-bit or 64-bit availability value after each query result.

### Mesh query counters and multiview

`VK_QUERY_TYPE_MESH_PRIMITIVES_GENERATED_EXT` counts mesh-shader primitives that reach the fragment stage. Pipeline-statistics bits count task-shader and mesh-shader invocations. Under multiview, one active query consumes one query index per enabled view; the implementation may distribute counts between those indices, but their sum must equal the total over all views [mesh shader queries](../../../../vulkan-docs/src/chapters/queries.adoc#queries-mesh-shader), [multiview query operation](../../../../vulkan-docs/src/chapters/queries.adoc#queries-operation).

Why it matters here:

- The host checks one or two query pools depending on the selected query combination.
- Multiview validation sums both per-view slots instead of requiring a particular distribution.

## One Concrete Example

The exact default-mustpass case

```text
dEQP-VK.mesh_shader.ext.query.all_queries.triangles.no_reset.get.wait.indirect_with_count_draw.64bit.with_availability.multiple_blocks.mesh_only.inside_rp.multi_view.with_secondary
```

uses all three counters. The test records indirect-count mesh draws in three blocks of 10, 20, and 30 draws. Each draw launches four mesh workgroups; each workgroup runs 40 mesh invocations and emits 32 triangles. The two-view render pass causes each query pool to expose two query slots. The host retrieves 64-bit results and availability values with `vkGetQueryPoolResults` and `VK_QUERY_RESULT_WAIT_BIT`, sums the two views, then applies the source's accepted range from the single-view count through twice that count. Vulkan independently permits implementation-dependent distribution between the two query slots but requires their sum to represent all views.

## End-to-End Test Flow

```text
[host] choose one registered combination and generate fragment, mesh, and optional task shaders
[host] create color image/readback buffer, graphics pipeline, query pools, and optional indirect buffers
[host] reset every query slot in a separate primary command buffer and wait for completion
[host] begin the selected queries inside or around the render pass, in the primary or secondary command buffer
[device] execute direct, indirect, or indirect-count mesh draws grouped by the selected block sequence
[device] render one 32-pixel row per mesh workgroup and update the active query counters
[host/device] optionally reset before retrieval, copy query results, or request them with vkGetQueryPoolResults
[host] wait for the submission fence, verify every rendered layer, parse 32-bit or 64-bit query items, and check availability and counter ranges
[host] for host-reset cases, reset completed queries and verify that each availability value becomes zero
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

`MeshQueryCase::initPrograms` generates:

- a fragment shader that writes blue for view 0 and blue-green for view 1;
- a mesh shader specialized for points, lines, or triangles, image height, task presence, and a push constant containing the preceding draw count;
- a task shader only for `task_mesh`, with a fixed task payload and a pseudorandom permutation of the two emitted mesh workgroups across X, Y, and Z;
- SPIR-V 1.4 through `getMinMeshEXTBuildOptions`. Generated SPIR-V must come from the compile, validate, and disassemble workflow; it must not be edited by hand.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Color image | yes | yes, framebuffer attachment | mesh-generated primitives render into it | yes, through a verification buffer | Proves that all selected draw blocks ran and that both multiview layers were addressed. |
| Verification buffer | yes | yes, transfer destination | receives the color-image copy | yes | Supplies exact host-visible pixels for the rendering check. |
| Primitive query pool | when `PRIMITIVES` is selected | yes, query commands | counts primitives | yes | Holds `VK_QUERY_TYPE_MESH_PRIMITIVES_GENERATED_EXT` results. |
| Pipeline-statistics query pool | when task or mesh statistics are selected | yes, query commands | counts selected stage invocations | yes | Holds task and/or mesh counters in pipeline-statistic bit order. |
| Query-results buffer | for `copy` only | yes, transfer destination | receives copied query data | yes | Tests `vkCmdCopyQueryPoolResults`. |
| Indirect command buffer | for indirect draw forms | yes, indirect input | read by draw commands | no | Stores randomized X/Y/Z mesh-task group counts. |
| Indirect count buffer | for `indirect_with_count_draw` only | yes, indirect input | supplies each draw-block count | no | Limits each indirect-count call to its registered block size. |
| Push constant | yes | yes | read by mesh stage | no | Maps `gl_DrawID` within each block to the global output row. |
| Task payload and `currentCol` | no | shader-local | task/mesh stages read or write them | no | Routes task dispatch indices and allocates output columns within a mesh workgroup. |

## What Is Checked

- The color image must match the exact expected color in every pixel and view layer. A no-draw case must retain the clear color.
- For a completed waiting query, primitive count must fall within the source's accepted range from the single-view expected count through that count times the number of views. Task and mesh invocation counters use the same source-defined rule. Vulkan independently permits implementation-dependent distribution among per-view query slots and requires their sum to represent all views.
- Without `WAIT_BIT`, the accepted lower bound is zero because the requested partial result may be intermediate. `vkGetQueryPoolResults` may return `VK_NOT_READY`.
- After `reset_before` or a post-completion host reset, numerical results are ignored because reset makes them undefined; requested availability values must be zero.
- With `WAIT_BIT` and no preceding reset, requested availability values must be nonzero.

## Behavior Parameter Identification

> **Behavior parameter:** `query combination` (first intermediate node below `mesh_shader.ext.query`)
>
> **Candidate values:** `no_queries`, `prim_query`, `task_invs_query`, `mesh_invs_query`, `all_stats_query`, `all_queries`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `no_queries` | Mesh draw, render-pass, secondary-command-buffer, or image verification failure independent of query accounting. |
| `prim_query` | Mesh primitive query creation, primitive counting, reset/retrieval, or selected draw/control path failure. |
| `task_invs_query` | Task invocation statistics, task-to-mesh execution, reset/retrieval, or selected draw/control path failure. |
| `mesh_invs_query` | Mesh invocation statistics, reset/retrieval, or selected draw/control path failure. |
| `all_stats_query` | Combined task/mesh statistic ordering or sizing, either stage counter, reset/retrieval, or selected draw/control path failure. |
| `all_queries` | Coordination of separate primitive and statistics pools, result offsets/sizing, any selected counter, reset/retrieval, or selected draw/control path failure. |

Shared failures can also come from incorrect 32/64-bit parsing, availability handling, wait/partial semantics, multiview aggregation, or query inheritance.

## Important Variations and Special Cases

- Query combination selects no pool, one primitive pool, one statistics pool with one or two counters, or both pool types. `no_queries` retains the drawing control case without requiring `meshShaderQueries`.
- Geometry changes both shader topology and vertices per primitive. The full query matrix uses triangles. Points and lines retain only a reduced direct-draw subset that adds primitive-query topology coverage.
- `no_reset`, `host_reset`, `reset_before`, and `reset_after` distinguish ordinary retrieval, post-completion host reset, reset before retrieval, and command reset after an in-command copy.
- `copy` records `vkCmdCopyQueryPoolResults`; `get` calls `vkGetQueryPoolResults`, before waiting on the submission fence when possible.
- `no_wait` sets `VK_QUERY_RESULT_PARTIAL_BIT`; `wait` sets `VK_QUERY_RESULT_WAIT_BIT`. Result size and availability independently add `VK_QUERY_RESULT_64_BIT` and `VK_QUERY_RESULT_WITH_AVAILABILITY_BIT`.
- Draw blocks are empty, `{10}`, or `{10,20,30}`. Draw commands are direct, indirect, or indirect with count. Task mode changes each draw from four mesh workgroups to two task workgroups, each emitting two mesh workgroups.
- `include_rp` begins and ends the query outside the render pass; `inside_rp` keeps it inside. With a secondary command buffer, `include_rp` exercises inherited pipeline-statistics queries, while `inside_rp` records begin/end and draws in the secondary buffer.
- `multi_view` enables two views and requires the query to begin and end inside the render pass. The host sums both query indices.
- The exact `vk-default` list contains 24,680 leaves from line 2063 through line 26742 of `mesh-shader.txt`: 8 `no_queries`, 4,560 each for `prim_query` and `all_queries`, and 5,184 each for the three statistics-only combinations.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Parameters, result flags, sizes, and offsets | [parameter model](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L177-L338) | Defines all runtime dimensions and packed result layout. |
| Shader generation | [`MeshQueryCase::initPrograms`](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L399-L530) | Generates geometry, rows, task payload, and view-color behavior. |
| Support gates | [`MeshQueryCase::checkSupport`](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L537-L564) | Requires mesh/task, query, inherited-query, host-reset, and multiview capabilities as needed. |
| Draw recording | [`recordDraws`](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L575-L677) | Implements direct, indirect, indirect-count, and block behavior. |
| Result semantics | [availability and counter verification](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L731-L807) | Defines how reset, wait, and partial results affect checking. |
| Query execution | [`MeshQueryInstance::iterate`](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L870-L1380) | Creates pools/resources, records four command-buffer arrangements, retrieves results, and checks image/query data. |
| Registration and pruning | [`createMeshShaderQueryTestsEXT`](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L1387-L1690) | Defines the exact hierarchy and all design exclusions. |
| Exact default coverage | [`vk-default` query block](../../../mustpass/main/vk-default/mesh-shader.txt#L2063-L26742) | Contains all 24,680 registered query leaves included in the default mustpass. |
| Query specification | [Vulkan queries chapter](../../../../vulkan-docs/src/chapters/queries.adoc#queries-operation) | Defines query state, retrieval, availability, wait/partial, inheritance, and multiview behavior. |
| Mesh query feature | [`meshShaderQueries`](../../../../vulkan-docs/src/chapters/features.adoc#features-meshShaderQueries) | Defines support for primitive and task/mesh statistics query forms. |

## Questions / Risk Points for User Audit

- Is query combination the clearest primary behavioral axis, with the remaining 12 dimensions treated as execution and retrieval specialization?
- Is the distinction between `reset_before` undefined numerical values and zero availability clear?
- Is the implementation-defined multiview distribution explained without implying a fixed per-view result?
- Is one mesh-shader walkthrough enough, given that query behavior itself is host-side and shader variation is limited to geometry, task presence, image height, and multiview color?

No unresolved source or specification issue blocks the final rewrite.

## Conversion Notes for Final Wiki Rewrite

- Use one representative walkthrough for the mesh-only, triangle, multiple-block indirect-count path. It exposes draw indexing, workgroup count, primitive count, and rendered rows without duplicating the optional task stage.
- Keep query state and multiview aggregation as the final page's local prerequisites. Move detailed source navigation to the appendix.
- Carry the query-combination values into `## Behavior Parameters` and copy the `### Failure Cause Mapping` table unchanged.
- Explain retrieval and validation in the runtime section because query behavior is controlled and checked mainly by host commands.
