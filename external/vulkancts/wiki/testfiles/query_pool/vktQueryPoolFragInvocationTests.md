# Fragment Invocation Query Tests

Tests for fragment-invocation-focused query behavior under `query_pool`. This page documents the `frag_invocations` Level-3 group registered from [`vktQueryPoolTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L53) and implemented in [`vktQueryPoolFragInvocationTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp).

## Source

- [`vktQueryPoolTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp)
- [`vktQueryPoolFragInvocationTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp)

## Registration

| Item | Value |
|------|-------|
| Top-level parent | `query_pool` via [`createTests()`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L59) |
| Level-3 group name | `frag_invocations` via [`createFragInvocationTests()`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L449) |
| Child registration | [`queryPoolTests->addChild(createFragInvocationTests(testCtx))`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L53) |
| Group population | [`createFragInvocationTests()`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L449) |
| Vulkan SC split | No registration-time Vulkan / Vulkan SC split is present in this file or in the parent add-child call |

## Summary

The `frag_invocations` group verifies that full-screen fragment-producing draws generate the expected query visibility and invocation behavior even when the fragment shader is trivially constant, fed by interpolated vertex color, or writing to a storage buffer via atomics. The group is split first by query type and then by primary versus secondary command buffer execution. For occlusion mode it checks exact sample counts. For fragment-invocation mode it checks that the reported count is at least a conservative lower bound, with a stricter bound for shader variants that prevent invocation merging. All cases also verify the rendered color buffer, and atomic-shader variants verify the storage-buffer counter exactly.

## Test Hierarchy

```text
query_pool
└── frag_invocations
    ├── occlusion
    │   ├── primary
    │   ├── primary_with_vertex_color
    │   ├── primary_with_atomic_counter
    │   ├── secondary
    │   ├── secondary_with_vertex_color
    │   └── secondary_with_atomic_counter
    └── frag_invs
        ├── primary
        ├── primary_with_vertex_color
        ├── primary_with_atomic_counter
        ├── secondary
        ├── secondary_with_vertex_color
        └── secondary_with_atomic_counter
```

The two query-type subgroups are created in the loop over [`QueryType`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L466), and the leaf cases are added in the nested loops over secondary-command-buffer mode and fragment-shader variant in [`createFragInvocationTests()`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L471).

## Registered Families

### Query-type split

[`getQueryTypeName()`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L52) maps the two query types to subgroup names:

| Enum | Group name | Vulkan query configuration |
|------|------------|----------------------------|
| `QueryType::OCCLUSION` | `occlusion` | `VK_QUERY_TYPE_OCCLUSION` with `VK_QUERY_CONTROL_PRECISE_BIT` in [`testInvocations()`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L237) |
| `QueryType::INVOCATIONS` | `frag_invs` | `VK_QUERY_TYPE_PIPELINE_STATISTICS` with `VK_QUERY_PIPELINE_STATISTIC_FRAGMENT_SHADER_INVOCATIONS_BIT` in [`testInvocations()`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L237) |

This split is the top-level organizational axis under `frag_invocations`.

### Command-buffer mode split

Within each query-type subgroup, the file registers one primary and one secondary recording mode:

| Boolean | Name stem | Behavior |
|---------|-----------|----------|
| `false` | `primary` | Render-pass commands are recorded directly in the primary command buffer |
| `true` | `secondary` | Draw commands are recorded in a secondary command buffer and executed from the primary buffer |

The naming is produced by [`(secondaryCase ? "secondary" : "primary")`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L475).

### Fragment-shader variants

Each command-buffer mode is expanded across three shader variants listed in [`fragShaderVariantCases`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L456):

| Variant enum | Name suffix | Shader behavior |
|--------------|-------------|-----------------|
| `FragShaderVariant::FLAT` | `""` | Fragment shader writes a constant blue color only |
| `FragShaderVariant::VERTEX_COLOR` | `_with_vertex_color` | Vertex shader outputs color and fragment shader writes interpolated vertex color |
| `FragShaderVariant::ATOMIC_COUNTER` | `_with_atomic_counter` | Fragment shader increments a storage-buffer atomic counter before writing color |

The programs are generated by [`initPrograms()`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L106).

## Parameter Dimensions

### Full case matrix

The complete leaf matrix is the Cartesian product of these dimensions:

| Dimension | Values | Naming / source |
|-----------|--------|-----------------|
| Query type | `occlusion`, `frag_invs` | [`getQueryTypeName()`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L52) |
| Command buffer mode | `primary`, `secondary` | [`createFragInvocationTests()`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L471) |
| Fragment shader variant | none, `_with_vertex_color`, `_with_atomic_counter` | [`fragShaderVariantCases`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L456) |

This yields `2 x 2 x 3 = 12` leaf cases.

### Rendering dimensions fixed across all cases

Several important execution parameters are constant across the whole file:

| Parameter | Value | Source |
|-----------|-------|--------|
| Framebuffer size | `64 x 64 x 1` | [`fbExtent`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L152) |
| Color format | `VK_FORMAT_R8G8B8A8_UNORM` | [`colorFormat`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L154) |
| Draw topology | `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST` | [`makeGraphicsPipeline()`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L274) |
| Geometry | One oversized triangle covering the framebuffer | Vertex data in [`vertices`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L172) |
| Expected color | Solid blue | [`getGeometryColor()`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L82) |
| Query count | `1` | [`VkQueryPoolCreateInfo`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L245) |

The oversized triangle coordinates `(-1,-1)`, `(3,-1)`, and `(-1,3)` ensure full coverage of the render area.

## Support Requirements

Support is centralized in [`checkSupport()`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L92).

| Requirement | Needed for | Source |
|------------|------------|--------|
| `inheritedQueries` core feature | Any `secondary*` case | [`checkSupport()`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L94) |
| `occlusionQueryPrecise` core feature | All `occlusion/*` cases | [`checkSupport()`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L97) |
| `pipelineStatisticsQuery` core feature | All `frag_invs/*` cases | [`checkSupport()`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L99) |
| `fragmentStoresAndAtomics` core feature | All `*_with_atomic_counter` cases | [`checkSupport()`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L102) |

### Optional fragment shading rate interaction

Fragment-invocation validation for the flat-shader case consults `VK_KHR_fragment_shading_rate` properties when that functionality is supported. Specifically, [`testInvocations()`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L383) uses `maxFragmentSize` to derive a lower bound for acceptable invocation counts. This is not a hard support requirement for registration, but it affects the minimum accepted result in `frag_invs/primary` and `frag_invs/secondary` without variant suffixes.

### Vulkan SC behavior

This file contains no `#ifndef CTS_USES_VULKANSC` hierarchy split and no non-SC-only test names. Any Vulkan SC differences therefore arise only from feature availability and command support at runtime, not from a different subgroup structure.

## Verification Methods

### Common rendering verification

Every case submits a render pass, copies the color attachment to a host-visible buffer, invalidates the allocation, and compares the framebuffer contents against the expected solid-color image using [`tcu::floatThresholdCompare()`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L440). The threshold is exactly zero in all channels, so any color mismatch fails the test.

### Query result verification

After execution, the test reads one 32-bit query result with [`getQueryPoolResults()`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L364). The expected rule depends on query type.

#### Occlusion subgroup

For the `occlusion` subgroup, the expected result is exact:

| Expected quantity | Value |
|------------------|-------|
| `pixelCount` | `64 x 64 x 1 = 4096` |

[`testInvocations()`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L405) requires the returned occlusion count to equal that exact pixel count, because the test uses a full-screen triangle and `VK_QUERY_CONTROL_PRECISE_BIT`.

#### Fragment-invocation subgroup

For the `frag_invs` subgroup, [`testInvocations()`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L370) requires the result to be at least a lower bound.

| Shader variant | Minimum accepted result |
|----------------|-------------------------|
| `primary` / `secondary` with flat shader | Framebuffer area divided by the implementation's maximum fragment-shading-rate tile size, derived from `maxFragmentSize` when `VK_KHR_fragment_shading_rate` is supported; otherwise the full pixel count |
| `*_with_vertex_color` | Full pixel count |
| `*_with_atomic_counter` | Full pixel count |

The special handling for the flat-shader case exists because implementations may reuse fragment-shader invocations when the shader computes identical values and does not write storage resources; see the explanatory comment in [`testInvocations()`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L376).

### Atomic-counter verification

For `*_with_atomic_counter` cases, the storage buffer is invalidated and read back after submission. [`testInvocations()`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L416) requires the atomic counter to equal the full pixel count exactly. This adds an independent check that storage writes were performed once per covered fragment.

## Execution Structure

### Primary-command-buffer path

When `secondary` is `false`, the primary command buffer performs all key steps directly:

1. Reset the query pool.
2. Begin the query.
3. Begin the render pass.
4. Bind pipeline, descriptor set when present, and vertex buffer.
5. Draw the full-screen triangle.
6. End the render pass and end the query.
7. Copy the color image to the host-visible buffer and synchronize to host access.

This path is implemented in the inline branch of [`testInvocations()`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L319).

### Secondary-command-buffer path

When `secondary` is `true`, the primary command buffer still owns the query begin/end and render-pass boundaries, but the actual draw commands are recorded in a secondary command buffer created with explicit inheritance information in [`VkCommandBufferInheritanceInfo`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L289). The inheritance struct sets:

- `occlusionQueryEnable` only for occlusion-query cases;
- `queryFlags` to the same precise/no-flags value used by the primary query;
- `pipelineStatistics` to the fragment-invocation statistic bit for `frag_invs` cases.

The primary buffer then executes the secondary buffer inside the render pass via [`cmdExecuteCommands`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L328).

## Notes

- The group is registered via [`addFunctionCaseWithPrograms()`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L477) rather than `TestCase` subclasses, so support checks, shader generation, and execution are all parameterized free functions.
- The query pool always contains a single slot, making each case a tightly scoped one-draw validation rather than a multi-query sequence.
- The `frag_invs` subgroup name is intentionally abbreviated in the source and must not be expanded when documenting the hierarchy, because it is the exact registered path component from [`getQueryTypeName()`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L57).
- This page documents only the Level-3 file represented by [`vktQueryPoolFragInvocationTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp).