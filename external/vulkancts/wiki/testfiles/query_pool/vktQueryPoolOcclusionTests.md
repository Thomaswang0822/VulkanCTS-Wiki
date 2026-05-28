# Occlusion Query Tests

Tests for Vulkan occlusion query behavior under `query_pool`. This file documents the `occlusion_query` Level-3 group registered from [`vktQueryPoolTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L46) and implemented in [`vktQueryPoolOcclusionTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp).

## Source

- [`vktQueryPoolTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp)
- [`vktQueryPoolOcclusionTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp)

## Registration Hierarchy

```text
query_pool.occlusion_query
├── basic_conservative
├── basic_precise
├── stride_zero
├── stride_max
├── clear_attachments_only
├── clear_attachments_with_draw
├── blit
├── resolve
├── no_attachments_single_sample
└── no_attachments_multisample
```

In addition to the named cases above, [`QueryPoolOcclusionTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1691) registers a large number of matrix-generated test cases (functional matrix and stride/dstOffset matrix) as direct children of `occlusion_query`. These generated cases are documented in the Test Families section below.

## Summary

The `occlusion_query` group combines focused smoke tests, a large functional matrix, no-attachment coverage, clear-operation coverage, stride and destination-offset coverage, and a limited set of device-address-command variants. The tests exercise both conservative and precise occlusion queries, validate result retrieval through host reads and command-buffer copies, and check special paths such as host query reset, attachment clears, blits, resolves, and rendering without color attachments. The historical API test plan identifies exact occlusion query as mandatory pipeline-query coverage ([apitests.adoc](../../../../../doc/testspecs/VK/apitests.adoc#L427-L432)).

## Test Families

### basic_conservative — Conservative occlusion query smoke test

Registered in [`QueryPoolOcclusionTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1715) with `queryControlFlags = 0`. Uses the base vector with 64-bit results, `WAIT_QUEUE`, host-side `vkGetQueryPoolResults`, result-size stride, point-list rendering, and no availability field.

### basic_precise — Precise occlusion query smoke test

Registered in [`QueryPoolOcclusionTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1718) with `VK_QUERY_CONTROL_PRECISE_BIT`. Same base configuration as `basic_conservative` except for the precise flag.

### stride_zero — Zero-stride result smoke test

Registered in [`QueryPoolOcclusionTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1729). Tests result retrieval with stride set to zero.

### stride_max — Maximum-stride result smoke test

Registered in [`QueryPoolOcclusionTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1729). Tests result retrieval with a large stride value.

### clear_attachments_only — Clear-attachments smoke test (no draw)

Registered in [`QueryPoolOcclusionTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1734). Uses precise queries; validates occlusion behavior when only attachment clears are performed.

### clear_attachments_with_draw — Clear-attachments smoke test (with draw)

Registered in [`QueryPoolOcclusionTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1734). Uses precise queries; validates occlusion behavior when attachment clears are followed by a draw.

### blit — Post-render blit operation test

Registered in [`QueryPoolOcclusionTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1749). Uses precise queries; validates occlusion results after a blit operation.

### resolve — Post-render resolve operation test

Registered in [`QueryPoolOcclusionTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1749). Uses precise queries; validates occlusion results after a resolve operation.

### no_attachments_single_sample — No color attachment, single-sample path

Registered via [`addFunctionCaseWithPrograms()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1767). Uses [`noAttachmentsSupport()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1609), [`initNoAttachmentsPrograms()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1580), and [`noAttachmentsTest()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1629).

### no_attachments_multisample — No color attachment, multisample path

Registered via [`addFunctionCaseWithPrograms()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1767). Same infrastructure as the single-sample variant but with multisample rendering.

### Functional matrix — Combinatorial occlusion query tests

The main body of [`QueryPoolOcclusionTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1771) generates a combinatorial matrix of named tests. Test names follow this pattern:

```text
<results_mode>_results_<control>_size_<32|64>_wait_<queue|query>_<with|without>_availability_draw_<points|triangles>[_discard]
```

Representative examples include:

- `get_results_conservative_size_32_wait_queue_without_availability_draw_points`
- `copy_results_precise_size_64_wait_query_with_availability_draw_triangles_discard`
- `get_create_reset_results_precise_size_64_wait_queue_without_availability_draw_triangles`

The matrix dimensions are:

| Dimension | Values | Registration source |
|-----------|--------|---------------------|
| Query control | `conservative`, `precise` | [`controlFlags`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1773) |
| Primitive topology | `points`, `triangles` | [`primitiveTopology`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1779) |
| Result size | `32`, `64` | [`resultSize`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1786) |
| Wait mode | `queue`, `query` | [`wait`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1792) |
| Results mode | `get`, `get_reset`, `get_create_reset`, `copy`, `copy_reset` | [`resultsMode`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1797) |
| Availability field | `without`, `with` | [`testAvailability`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1814) |
| Fragment discard variant | none, `_discard` | [`discardHalf`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1830) |

#### Matrix exclusions

The registration logic deliberately skips several invalid or unhelpful combinations:

- `WAIT_QUERY` together with `RESULTS_MODE_GET_RESET`, because a second result read after reset may not complete in finite time according to the comment in [`QueryPoolOcclusionTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1805).
- `RESULTS_MODE_COPY_RESET` without availability, because that mode specifically validates the cleared availability bit; see [`QueryPoolOcclusionTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1820).
- Point-list tests with `_discard`, because fragment discarding is not meaningful for one-pixel points; see [`QueryPoolOcclusionTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1848).

### Clear-operation and no-color-attachment functional variants

Inside the same functional loop, the file also registers dedicated variants for internal clear operations and for render passes without color attachments:

| Family | Naming pattern | Notes |
|--------|----------------|-------|
| Clear operations | `get_results_<control>_size_<bits>_wait_<mode>_without_availability_draw_<primitive>_clear_color` and `_clear_depth` | Registered in [`QueryPoolOcclusionTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1872) |
| No color attachments | `get_results_<control>_size_<bits>_wait_<mode>_without_availability_draw_<primitive>_no_color_attachments` | Registered in [`QueryPoolOcclusionTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1903) |

### Result-copy stride and destination-offset matrix

The final family in [`QueryPoolOcclusionTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1932) focuses on result-buffer layout handling. Test names follow this pattern:

```text
<results_mode>_results_size_<32|64>_stride_<N>_<with|without>_availability[_dstoffset]
```

The dimensions are:

| Dimension | Values |
|-----------|--------|
| Results mode | `get`, `get_reset`, `copy`, `copy_reset` |
| Result size | `32`, `64` |
| Availability field | `without`, `with` |
| Destination offset suffix | none, `_dstoffset` |
| Stride value | `0`, `1x`, `2x`, `3x`, `4x`, `5x`, `13x`, `1024x` result size |

The concrete stride list is defined in [`QueryPoolOcclusionTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1966).

#### Additional filtering in the stride matrix

The registration logic removes combinations that would not satisfy the intended buffer layout checks:

- It skips entries where the required element size exceeds the chosen non-zero stride; see [`QueryPoolOcclusionTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1986).
- Stride `0` is tested only with command-copy mode and never with the explicit destination-offset variant; see [`QueryPoolOcclusionTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1994).

### Device-address-command variants

For non-SC builds only, the stride matrix adds a limited number of `_device_address` cases when the result path uses copy operations. This is guarded by `#ifndef CTS_USES_VULKANSC` in [`QueryPoolOcclusionTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L2019). The implementation intentionally samples only some combinations to control test-count growth; see the comment in [`QueryPoolOcclusionTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L2024).

## Core Parameters and Behaviors

### Base parameter vector

The default configuration for generated tests is defined by `baseTestVector` in [`QueryPoolOcclusionTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1693).

| Field | Default value |
|------|---------------|
| Query type | `VK_QUERY_TYPE_OCCLUSION` through [`makeOcclusionQueryPool()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L54) |
| Result size | 64-bit |
| Wait mode | `WAIT_QUEUE` |
| Results mode | `RESULTS_MODE_GET` |
| Initial stride | `sizeof(uint64_t)` |
| Availability field | disabled |
| Primitive topology | `VK_PRIMITIVE_TOPOLOGY_POINT_LIST` |
| Fragment discard | disabled |
| Destination buffer offset | disabled |
| Clear operation | `CLEAR_NOOP` |
| No color attachments | disabled |
| Device-address commands | disabled |
| Stride mode | `STRIDE_RESULT_SIZE` |
| Clear-attachments mode | `CLEAR_ATTACHMENTS_NONE` |
| Additional operation | `ADDITIONAL_OP_NONE` |

### Rendering setup

The rendering state is built by [`StateObjects::StateObjects()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L105). Important execution variants include:

| Variant | Implementation detail |
|--------|------------------------|
| Standard render pass | Color + depth attachments |
| No-color-attachment mode | Depth-only render pass branch in [`StateObjects::StateObjects()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L132) |
| Blit validation path | Source and destination transfer images allocated in [`StateObjects::StateObjects()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L235) |
| Resolve validation path | 4x MSAA source image plus single-sample destination in [`StateObjects::StateObjects()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L246) |

## Support / Feature Requirements

| Requirement | When needed | Source |
|------------|-------------|--------|
| `occlusionQueryPrecise` feature | Any `precise` test | [`QueryPoolOcclusionTest::checkSupport()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1491) |
| `VK_EXT_host_query_reset` + `hostQueryReset` feature | `RESULTS_MODE_GET_RESET` basic-instance path | [`QueryPoolOcclusionTest::checkSupport()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1497) |
| `VK_KHR_device_address_commands` | `_device_address` variants | [`QueryPoolOcclusionTest::checkSupport()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1488) |
| 4x sample-count support for `VK_FORMAT_R8G8B8A8_UNORM` transfer source usage | `resolve` variant | [`QueryPoolOcclusionTest::checkSupport()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1504) |

### Vulkan SC behavior

The file contains explicit `#ifndef CTS_USES_VULKANSC` handling in two places:

- Query-pool creation can use `VK_QUERY_POOL_CREATE_RESET_BIT_KHR` only in non-SC builds inside [`makeOcclusionQueryPool()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L54).
- `_device_address` test registration is compiled out in SC builds in [`QueryPoolOcclusionTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L2019).

As a result, Vulkan SC does not include the device-address-command sub-variants documented above.

## Verification Strategy

### Basic instance checks

The simpler cases use [`BasicOcclusionQueryTestInstance::iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L468), which validates that the query result path behaves correctly for focused scenarios such as clear-attachments, blit/resolve side paths, and no-attachment rendering.

### Functional instance checks

The broader matrix uses [`OcclusionQueryTestInstance::iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L821). Verification logic distinguishes between precise and conservative semantics:

| Query mode | Expected result rule |
|-----------|----------------------|
| Precise | Exact sample counts are compared for each query slot |
| Conservative | Non-zero visibility is sufficient for hit cases |
| Availability-enabled modes | Result buffers are interpreted with value + availability pairs |
| Reset-validation modes | Post-reset reads or copies must show cleared / unavailable state as appropriate |

The pass/fail helper for the core result comparison is implemented in the logic ending at [`vktQueryPoolOcclusionTests.cpp:1471`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1471), where conservative mode accepts any non-zero value for visible samples.

## Notes

- The group mixes regular `TestCase`-based registrations with function-style cases using [`addFunctionCaseWithPrograms()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1767).
- The file intentionally uses a much larger parameter matrix for general query semantics than for device-address-command coverage, keeping the latter sampled rather than exhaustive.
- The page documents only the Level-3 file represented by [`vktQueryPoolOcclusionTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp); the category-level summary is maintained separately in [query_pool.md](../../categories/query_pool.md).
