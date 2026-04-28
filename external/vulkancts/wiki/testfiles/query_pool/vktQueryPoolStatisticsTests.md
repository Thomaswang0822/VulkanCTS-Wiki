# Statistics Query Tests

Tests for Vulkan pipeline statistics queries under `query_pool`. This page documents the `statistics_query` Level-3 group registered from [`vktQueryPoolTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp:47) and implemented in [`vktQueryPoolStatisticsTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp).

## Source

- [`vktQueryPoolTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp)
- [`vktQueryPoolStatisticsTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp)

## Registration

| Item | Value |
|------|-------|
| Top-level parent | `query_pool` via [`createTests()`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp:59) |
| Level-3 group name | `statistics_query` via [`QueryPoolStatisticsTests::QueryPoolStatisticsTests()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:6199) |
| Child registration | [`queryPoolTests->addChild(new QueryPoolStatisticsTests(testCtx))`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp:47) |
| Group population | [`QueryPoolStatisticsTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:6211) |

## Summary

The `statistics_query` group is a large matrix of pipeline statistics tests covering compute and graphics statistics, primary and secondary command buffer recording modes, inherited-query behavior, host reset and post-copy reset workflows, result retrieval via `vkGetQueryPoolResults` and `vkCmdCopyQueryPoolResults`, optional device-address-command paths, vertex-only rendering subsets, multiple-query scenarios, and combined-statistics scenarios.

## Top-Level Hierarchy

[`QueryPoolStatisticsTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:6211) registers these direct child groups:

```text
query_pool
└── statistics_query
    ├── compute_shader_invocations
    ├── input_assembly_vertices
    ├── input_assembly_primitives
    ├── vertex_shader_invocations
    ├── fragment_shader_invocations
    ├── geometry_shader_invocations
    ├── geometry_shader_primitives
    ├── clipping_invocations
    ├── clipping_primitives
    ├── tes_control_patches
    ├── tes_evaluation_shader_invocations
    ├── vertex_only
    │   ├── input_assembly_vertices
    │   ├── input_assembly_primitives
    │   └── vertex_shader_invocations
    ├── host_query_reset
    │   └── <mirrors most statistic groups>
    ├── reset_before_copy
    │   └── <mirrors most statistic groups>
    ├── reset_after_copy
    │   └── <mirrors most statistic groups>
    ├── multiple_queries
    └── multiple_geom_stats
```

The direct `addChild()` calls for these groups appear in [`QueryPoolStatisticsTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:9037).

## Shared Parameter Axes

Several families reuse the same parameter dimensions.

### Copy and result-layout modes

The main test generator defines the core result-transfer axes in [`QueryPoolStatisticsTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:6388):

| Dimension | Values | Naming |
|-----------|--------|--------|
| Copy type | `COPY_TYPE_GET`, `COPY_TYPE_CMD` | `""`, `cmdcopyquerypoolresults_` |
| Result bit width | 32-bit, 64-bit | `32bits_`, `64bits_` via [`bitPrefix()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:6204) |
| Destination offset | off, on | optional `dstoffset_` via [`bitPrefix()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:6204) |
| Stride type | valid, zero | `""`, `stride_zero_` |

The implementation skips `dstoffset` when the copy type is host-side `vkGetQueryPoolResults`, because that path does not use destination offsets; see [`QueryPoolStatisticsTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:6402).

### Reset workflows

Statistics tests are replicated across several query-reset strategies:

| Reset group | Reset mode | Meaning |
|-------------|------------|---------|
| base group | `RESET_TYPE_NORMAL` | Normal command-buffer reset / issue / read flow |
| `host_query_reset` | `RESET_TYPE_HOST` | Host-side query reset path |
| `reset_before_copy` | `RESET_TYPE_BEFORE_COPY` | Query reset occurs before copying results |
| `reset_after_copy` | `RESET_TYPE_AFTER_COPY` | Query reset occurs after copying results |

The enum is declared in [`ResetType`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:76), and the mirrored group trees are allocated in [`QueryPoolStatisticsTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:6322), [`QueryPoolStatisticsTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:6343), and [`QueryPoolStatisticsTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:6364).

### Command buffer recording modes

Graphics and compute families frequently instantiate three recording styles:

| Mode | Enum | Meaning |
|------|------|---------|
| Primary | `PRIMARY` | Query begin/end in a primary command buffer |
| Secondary | `SECONDARY` | Query activity recorded in a secondary command buffer |
| Secondary inherited | `SECONDARY_INHERITED` | Query behavior validated with inherited state support |

The enum is declared in [`CommandBufferType`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:97). The helper lambda [`addChilds`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:6227) centralizes much of the graphics-case fan-out for these modes.

## Registered Statistic Families

### 1. `compute_shader_invocations`

The compute family is registered first in [`QueryPoolStatisticsTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:6406). It covers:

- primary, secondary, and secondary-inherited command-buffer forms;
- host-get and command-copy result retrieval;
- 32-bit and 64-bit result widths;
- optional compute-queue execution indicated by `_cq` suffix;
- optional zero-stride command-copy mode;
- host reset, reset-before-copy, and reset-after-copy variants;
- a sampled `_device_address` variant in non-SC builds.

Representative names include:

- `32bits_primary`
- `64bits_cmdcopyquerypoolresults_secondary_cq`
- `64bits_cmdcopyquerypoolresults_stride_zero_secondary_inherited`
- `64bits_cmdcopyquerypoolresults_secondary_device_address`

The actual test case templates are created through [`QueryPoolComputeStatsTest`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:6417).

### 2. `input_assembly_vertices`

The input-assembly-vertex counter group uses `VK_QUERY_PIPELINE_STATISTIC_INPUT_ASSEMBLY_VERTICES_BIT` and is built in [`QueryPoolStatisticsTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:6495). Coverage includes:

- primary, secondary, and secondary-inherited graphics paths;
- regular graphics and `vertex_only` mirrors;
- no-color-attachment cases for primary paths;
- clear-operation variants (`_clear_color`, `_clear_depth`);
- host reset, reset-before-copy, and reset-after-copy replicas;
- sampled `_device_address` variants in non-SC builds.

Representative names include:

- `32bits_primary`
- `64bits_cmdcopyquerypoolresults_secondary_clear_depth`
- `32bits_primary_with_no_color_attachments`
- `64bits_cmdcopyquerypoolresults_secondary_inherited`
- `32bits_cmdcopyquerypoolresults_primary_with_no_color_attachments_device_address`

### 3. `input_assembly_primitives`

The input-assembly-primitives group uses `VK_QUERY_PIPELINE_STATISTIC_INPUT_ASSEMBLY_PRIMITIVES_BIT` and is registered in [`QueryPoolStatisticsTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:6687). It expands the previous family across primitive topologies:

- `point_list`
- `line_list`
- `line_strip`
- `triangle_list`
- `triangle_strip`
- `triangle_fan`
- adjacency topologies
- `patch_list` with dedicated tessellation-specific loops

For non-patch topologies, names follow forms such as:

- `32bits_point_list`
- `64bits_cmdcopyquerypoolresults_triangle_strip_clear_color`
- `32bits_line_strip_with_no_color_attachments`
- `64bits_cmdcopyquerypoolresults_triangle_list_secondary_inherited`

For `patch_list`, the file adds tessellation-specific suffixes such as `_v4_p1`, `_v8_p2`, and `_v28_p3`, where the suffix encodes patch size and primitive count; see [`patchPrimitiveCombo`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:6964).

### 4. `vertex_shader_invocations`

The vertex-shader-invocation family uses `VK_QUERY_PIPELINE_STATISTIC_VERTEX_SHADER_INVOCATIONS_BIT` and is registered in [`QueryPoolStatisticsTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:7203). Its structure closely parallels `input_assembly_primitives`, including:

- topology expansion across non-patch topologies;
- `vertex_only` mirrors;
- no-color-attachment variants for primary paths;
- clear-operation variants;
- host reset, reset-before-copy, and reset-after-copy mirrors;
- sampled `_device_address` variants in non-SC builds.

Representative names include:

- `32bits_triangle_list`
- `64bits_cmdcopyquerypoolresults_line_strip_clear_depth`
- `32bits_triangle_fan_with_no_color_attachments`
- `64bits_cmdcopyquerypoolresults_triangle_strip_secondary_inherited`
- `64bits_cmdcopyquerypoolresults_line_strip_with_no_color_attachments_device_address`

### 5. `fragment_shader_invocations`

The fragment-shader family uses `VK_QUERY_PIPELINE_STATISTIC_FRAGMENT_SHADER_INVOCATIONS_BIT` and is generated in [`QueryPoolStatisticsTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:7480). It differs slightly from earlier groups:

- there is no `vertex_only` mirror;
- so-called “no color attachments” cases use `CLEAR_SKIP` because fragment work can otherwise be skipped entirely; see the comment in [`QueryPoolStatisticsTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:7516);
- topology expansion still applies;
- `_device_address` variants are again sampled for non-SC command-copy reset-after-copy cases.

Representative names include:

- `32bits_point_list`
- `64bits_cmdcopyquerypoolresults_triangle_strip`
- `32bits_line_list_with_no_color_attachments`
- `64bits_cmdcopyquerypoolresults_point_list_device_address`

### 6. `geometry_shader_invocations`

This family uses `VK_QUERY_PIPELINE_STATISTIC_GEOMETRY_SHADER_INVOCATIONS_BIT` and is built in [`QueryPoolStatisticsTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:7698). Coverage includes:

- primary, secondary, and secondary-inherited variants;
- no-color-attachment primary cases;
- clear-operation variants;
- host reset, reset-before-copy, and reset-after-copy mirrors.

Representative names include:

- `32bits_triangle_list`
- `64bits_cmdcopyquerypoolresults_line_strip_clear_color`
- `32bits_triangle_fan_with_no_color_attachments`
- `64bits_cmdcopyquerypoolresults_triangle_list_secondary_inherited`

### 7. `geometry_shader_primitives`

This group uses `VK_QUERY_PIPELINE_STATISTIC_GEOMETRY_SHADER_PRIMITIVES_BIT` and is registered in [`QueryPoolStatisticsTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:7915). It mirrors the previous family but validates primitive counts emitted by the geometry stage.

Representative names include:

- `32bits_triangle_list`
- `64bits_cmdcopyquerypoolresults_triangle_strip_clear_depth`
- `32bits_line_list_with_no_color_attachments`
- `64bits_cmdcopyquerypoolresults_triangle_fan_secondary_inherited`

### 8. `clipping_invocations`

This family uses `VK_QUERY_PIPELINE_STATISTIC_CLIPPING_INVOCATIONS_BIT` and is generated in [`QueryPoolStatisticsTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:8131). Unlike several earlier families, it reuses the helper lambda [`addChilds`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:6227), so each logical case may fan out into paired `_geometry` and `_vertex` child tests for non-patch topologies, or tessellation-oriented children for patch-list topology.

Representative logical name stems include:

- `32bits_triangle_list`
- `64bits_cmdcopyquerypoolresults_patch_list_clear_color`
- `32bits_line_strip_with_no_color_attachments`

The actual leaf nodes append stage-specific suffixes such as `_geometry`, `_vertex`, `_tessellation`, or `_tessellation_geometry`; see [`addChilds`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:6227).

### 9. `clipping_primitives`

This family uses `VK_QUERY_PIPELINE_STATISTIC_CLIPPING_PRIMITIVES_BIT` and follows the same helper-driven structure in [`QueryPoolStatisticsTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:8335). It likewise expands into stage-specific leaf tests under each logical stem.

Representative logical name stems include:

- `32bits_triangle_list`
- `64bits_cmdcopyquerypoolresults_patch_list_clear_depth`
- `32bits_triangle_strip_with_no_color_attachments`

### 10. `tes_control_patches`

The tessellation-control family uses `VK_QUERY_PIPELINE_STATISTIC_TESSELLATION_CONTROL_SHADER_PATCHES_BIT` and is registered in [`QueryPoolStatisticsTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:8542). It covers:

- tessellation primitive modes `triangles`, `isolines`, and `quads`;
- optional point mode, except for isolines where point mode is skipped to reduce test count;
- regular, host reset, reset-before-copy, and reset-after-copy variants;
- primary, secondary, and secondary-inherited paths in the clear-operation section;
- no-color-attachment primary paths.

Representative names include:

- `32bits_tes_control_patches_triangles`
- `64bits_cmdcopyquerypoolresults_tes_control_patches_quads_point_mode`
- `32bits_tes_control_patches_with_no_color_attachments`
- `64bits_cmdcopyquerypoolresults_tes_control_patches_secondary_clear_color`
- `64bits_cmdcopyquerypoolresults_tes_control_patches_secondary_inherited`

### 11. `tes_evaluation_shader_invocations`

The tessellation-evaluation family uses `VK_QUERY_PIPELINE_STATISTIC_TESSELLATION_EVALUATION_SHADER_INVOCATIONS_BIT` and is generated alongside the previous family in [`QueryPoolStatisticsTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:8583). It mirrors the same primitive-mode and reset dimensions, and also contains a sampled `_device_address` variant in non-SC reset-after-copy command-copy mode.

Representative names include:

- `32bits_tes_evaluation_shader_invocations_triangles`
- `64bits_cmdcopyquerypoolresults_tes_evaluation_shader_invocations_quads_point_mode`
- `32bits_tes_evaluation_shader_invocations_with_no_color_attachments`
- `64bits_cmdcopyquerypoolresults_tes_evaluation_shader_invocations_secondary_clear_depth`
- `64bits_cmdcopyquerypoolresults_tes_evaluation_shader_invocations_with_no_color_attachments_device_address`

## Special Top-Level Subgroups

### `vertex_only`

The `vertex_only` subgroup is populated in [`QueryPoolStatisticsTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:9049). It mirrors only three statistics families:

- `input_assembly_vertices`
- `input_assembly_primitives`
- `vertex_shader_invocations`

These cases disable later graphics stages so that statistics can be validated in a reduced pipeline configuration.

### `host_query_reset`

The `host_query_reset` subgroup collects host-reset replicas of most major families; its assembly starts in [`QueryPoolStatisticsTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:9054).

### `reset_before_copy`

The `reset_before_copy` subgroup collects cases that copy statistics results after a reset-before-copy flow; group assembly starts in [`QueryPoolStatisticsTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:9067).

### `reset_after_copy`

The `reset_after_copy` subgroup collects cases where queries are reset after results have been copied; group assembly starts in [`QueryPoolStatisticsTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:9080).

## Additional Families

### `multiple_queries`

The `multiple_queries` subgroup is populated in [`QueryPoolStatisticsTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:8942). It validates combined statistics-query behavior when multiple query statistic bits are enabled at once.

Axes include:

| Dimension | Values |
|-----------|--------|
| Partial flag | absent, `VK_QUERY_RESULT_PARTIAL_BIT` |
| Wait flag | absent, `VK_QUERY_RESULT_WAIT_BIT` |
| Copy mode | host get, command copy, command copy with destination offset |
| Stride | valid, zero (command-copy only, and not for partial multi-query cases) |
| Statistics set | `input_assembly + primitives + fragment` or `input_assembly + primitives + vertex` |

Representative names include:

- `input_assembly_vertex_fragment`
- `input_assembly_vertex_fragment_partial_cmdcopy`
- `input_assembly_vertex_wait_cmdcopy_dstoffset`
- `input_assembly_vertex_cmdcopy_stride_zero`

The query flags assembled for this family are created in [`QueryPoolStatisticsTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:8983).

### `multiple_geom_stats`

The `multiple_geom_stats` subgroup is populated in [`QueryPoolStatisticsTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:9019). It registers exactly eight cases from the Cartesian product of:

| Dimension | Values |
|-----------|--------|
| Result retrieval | `get`, `copy` |
| Availability field | off, on |
| Inheritance | off, on |

Resulting registered names are:

- `get`
- `get_with_availability`
- `get_and_inheritance`
- `get_with_availability_and_inheritance`
- `copy`
- `copy_with_availability`
- `copy_and_inheritance`
- `copy_with_availability_and_inheritance`

These cases are implemented by [`MultipleGeomStatsTestCase`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:4761).

## Support Requirements

### Common statistics-query support

All statistics tests require `pipelineStatisticsQuery`; this is enforced by [`commonCheckSupport()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:505).

| Requirement | When needed | Source |
|------------|-------------|--------|
| `pipelineStatisticsQuery` feature | All `statistics_query` cases | [`commonCheckSupport()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:505) |
| `VK_EXT_host_query_reset` + `hostQueryReset` feature | `RESET_TYPE_HOST` cases | [`commonCheckSupport()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:512) |
| `inheritedQueries` feature | Secondary-inherited compute and graphics variants | [`QueryPoolComputeStatsTest::checkSupport()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:4015) and related graphics checks such as [`vktQueryPoolStatisticsTests.cpp:4682`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:4682) |
| Queue family with requested capabilities | `_cq` compute cases | [`QueryPoolComputeStatsTest::checkSupport()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:4022) |
| `VK_KHR_device_address_commands` | `_device_address` variants | [`QueryPoolComputeStatsTest::checkSupport()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:4029) and graphics equivalent in [`vktQueryPoolStatisticsTests.cpp:5839`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:5839) |

### Vulkan SC behavior

The file contains several non-SC-only registrations guarded by `#ifndef CTS_USES_VULKANSC`, notably for sampled `_device_address` variants and some extension capability declarations. As a result:

- `_device_address` cases documented on this page are not part of Vulkan SC builds.
- The ordinary statistics families remain present, but SC excludes those non-SC-only command paths.

Representative non-SC guard sites appear in [`QueryPoolStatisticsTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:6467), [`QueryPoolStatisticsTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:6534), [`QueryPoolStatisticsTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:7624), and [`QueryPoolStatisticsTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:8676).

## Verification Approach

### Query pool creation and result transport

Pipeline-statistics query pools are created through [`makeQueryPool()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:425). Result transport paths include:

- host reads through overloaded [`GetQueryPoolResultsVector()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:180);
- buffer-copy reads through [`cmdCopyQueryPoolResults()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:264);
- copied-buffer decoding through overloaded [`cmdCopyQueryPoolResultsVector()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:287).

### Correlation- and expectation-based validation

The file does not use a single universal expected-value rule. Instead, each instance type validates the statistic appropriate for its shader stage or pipeline shape. For example:

- compute tests derive expected invocation totals from dispatched workgroup sizes;
- graphics tests compare counts against known draw-repeat vectors such as [`sixRepeats`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:6225);
- combined-statistics tests validate multi-flag result layout and availability semantics;
- some scenarios use correlation-based reasoning through [`calculatePearsonCorrelation()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:439) to check linear relationships between expected draw scaling and observed counters.

### Secondary-command-buffer inheritance handling

The helper [`beginSecondaryCommandBuffer()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:400) sets inheritance state including `pipelineStatistics` bits. This is central to `secondary_inherited` cases, where query inheritance support must be present and correctly interpreted by the implementation.

## Notes

- The file is one of the largest query-pool registrars and intentionally relies on nested loops instead of manually enumerated lists.
- For clipping statistics, logical stems often expand into multiple stage-specific leaf tests through [`addChilds`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:6227), so the visible hierarchy is wider than the top-level names alone suggest.
- Some `_device_address` registrations are intentionally sampled instead of exhaustive to keep the suite size manageable; the source comments explicitly note this in several places, such as [`QueryPoolStatisticsTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp:6468).
- This page documents only the Level-3 file represented by [`vktQueryPoolStatisticsTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp).