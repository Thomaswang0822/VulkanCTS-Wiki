# Occlusion Query Tests

Tests for Vulkan occlusion query behavior under `query_pool`. This file documents the `occlusion_query` Level-3 group registered from [`vktQueryPoolTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp:46) and implemented in [`vktQueryPoolOcclusionTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp).

## Source

- [`vktQueryPoolTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp)
- [`vktQueryPoolOcclusionTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp)

## Registration

| Item | Value |
|------|-------|
| Top-level parent | `query_pool` via [`createTests()`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp:59) |
| Level-3 group name | `occlusion_query` via [`QueryPoolOcclusionTests::QueryPoolOcclusionTests()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp:1686) |
| Child registration | [`queryPoolTests->addChild(new QueryPoolOcclusionTests(testCtx))`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp:46) |
| Group population | [`QueryPoolOcclusionTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp:1691) |

## Summary

The `occlusion_query` group combines focused smoke tests, a large functional matrix, no-attachment coverage, clear-operation coverage, stride and destination-offset coverage, and a limited set of device-address-command variants. The tests exercise both conservative and precise occlusion queries, validate result retrieval through host reads and command-buffer copies, and check special paths such as host query reset, attachment clears, blits, resolves, and rendering without color attachments.

## Test Hierarchy

```text
query_pool
└── occlusion_query
    ├── basic_conservative
    ├── basic_precise
    ├── stride_zero
    ├── stride_max
    ├── clear_attachments_only
    ├── clear_attachments_with_draw
    ├── blit
    ├── resolve
    ├── no_attachments_single_sample
    ├── no_attachments_multisample
    ├── <functional matrix>
    └── <stride / dstOffset matrix>
```

## Registered Families

### Basic tests

[`QueryPoolOcclusionTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp:1711) first registers two direct sanity cases:

| Test name | Key configuration |
|-----------|-------------------|
| `basic_conservative` | Conservative occlusion query (`queryControlFlags = 0`) |
| `basic_precise` | Precise occlusion query (`VK_QUERY_CONTROL_PRECISE_BIT`) |

These use the base vector initialized in [`QueryPoolOcclusionTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp:1693) with 64-bit results, `WAIT_QUEUE`, host-side `vkGetQueryPoolResults`, result-size stride, point-list rendering, and no availability field.

### Standalone stride and attachment-clear variants

Additional short families are registered immediately afterward:

| Family | Registered names | Notes |
|--------|------------------|-------|
| Result stride smoke tests | `stride_zero`, `stride_max` | Registered in [`QueryPoolOcclusionTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp:1721) |
| Clear-attachments smoke tests | `clear_attachments_only`, `clear_attachments_with_draw` | Use precise queries; registered in [`QueryPoolOcclusionTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp:1734) |
| Additional post-render operation tests | `blit`, `resolve` | Registered in [`QueryPoolOcclusionTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp:1749) |

### No-attachment function cases

The group then registers two function-style cases with generated programs through [`addFunctionCaseWithPrograms()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp:1767):

| Test name | Parameters |
|-----------|------------|
| `no_attachments_single_sample` | No color attachment, single-sample path |
| `no_attachments_multisample` | No color attachment, multisample path |

These cases use [`noAttachmentsSupport()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp:1609), [`initNoAttachmentsPrograms()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp:1580), and [`noAttachmentsTest()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp:1629).

### Functional matrix

The main body of [`QueryPoolOcclusionTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp:1771) generates a combinatorial matrix of named tests. Test names follow this pattern:

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
| Query control | `conservative`, `precise` | [`controlFlags`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp:1773) |
| Primitive topology | `points`, `triangles` | [`primitiveTopology`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp:1779) |
| Result size | `32`, `64` | [`resultSize`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp:1786) |
| Wait mode | `queue`, `query` | [`wait`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp:1792) |
| Results mode | `get`, `get_reset`, `get_create_reset`, `copy`, `copy_reset` | [`resultsMode`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp:1797) |
| Availability field | `without`, `with` | [`testAvailability`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp:1814) |
| Fragment discard variant | none, `_discard` | [`discardHalf`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp:1830) |

#### Matrix exclusions

The registration logic deliberately skips several invalid or unhelpful combinations:

- `WAIT_QUERY` together with `RESULTS_MODE_GET_RESET`, because a second result read after reset may not complete in finite time according to the comment in [`QueryPoolOcclusionTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp:1805).
- `RESULTS_MODE_COPY_RESET` without availability, because that mode specifically validates the cleared availability bit; see [`QueryPoolOcclusionTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp:1820).
- Point-list tests with `_discard`, because fragment discarding is not meaningful for one-pixel points; see [`QueryPoolOcclusionTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp:1848).

### Clear-operation and no-color-attachment functional variants

Inside the same functional loop, the file also registers dedicated variants for internal clear operations and for render passes without color attachments:

| Family | Naming pattern | Notes |
|--------|----------------|-------|
| Clear operations | `get_results_<control>_size_<bits>_wait_<mode>_without_availability_draw_<primitive>_clear_color` and `_clear_depth` | Registered in [`QueryPoolOcclusionTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp:1872) |
| No color attachments | `get_results_<control>_size_<bits>_wait_<mode>_without_availability_draw_<primitive>_no_color_attachments` | Registered in [`QueryPoolOcclusionTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp:1903) |

### Result-copy stride and destination-offset matrix

The final family in [`QueryPoolOcclusionTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp:1932) focuses on result-buffer layout handling. Test names follow this pattern:

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
| Stride value | `0`, `1×`, `2×`, `3×`, `4×`, `5×`, `13×`, `1024×` result size |

The concrete stride list is defined in [`QueryPoolOcclusionTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp:1966).

#### Additional filtering in the stride matrix

The registration logic removes combinations that would not satisfy the intended buffer layout checks:

- It skips entries where the required element size exceeds the chosen non-zero stride; see [`QueryPoolOcclusionTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp:1986).
- Stride `0` is tested only with command-copy mode and never with the explicit destination-offset variant; see [`QueryPoolOcclusionTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp:1994).

### Device-address-command variants

For non-SC builds only, the stride matrix adds a limited number of `_device_address` cases when the result path uses copy operations. This is guarded by `#ifndef CTS_USES_VULKANSC` in [`QueryPoolOcclusionTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp:2019). The implementation intentionally samples only some combinations to control test-count growth; see the comment in [`QueryPoolOcclusionTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp:2024).

## Core Parameters and Behaviors

### Base parameter vector

The default configuration for generated tests is defined by `baseTestVector` in [`QueryPoolOcclusionTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp:1693).

| Field | Default value |
|------|---------------|
| Query type | `VK_QUERY_TYPE_OCCLUSION` through [`makeOcclusionQueryPool()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp:54) |
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

The rendering state is built by [`StateObjects::StateObjects()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp:105). Important execution variants include:

| Variant | Implementation detail |
|--------|------------------------|
| Standard render pass | Color + depth attachments |
| No-color-attachment mode | Depth-only render pass branch in [`StateObjects::StateObjects()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp:132) |
| Blit validation path | Source and destination transfer images allocated in [`StateObjects::StateObjects()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp:235) |
| Resolve validation path | 4× MSAA source image plus single-sample destination in [`StateObjects::StateObjects()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp:246) |

## Support Requirements

| Requirement | When needed | Source |
|------------|-------------|--------|
| `occlusionQueryPrecise` feature | Any `precise` test | [`QueryPoolOcclusionTest::checkSupport()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp:1491) |
| `VK_EXT_host_query_reset` + `hostQueryReset` feature | `RESULTS_MODE_GET_RESET` basic-instance path | [`QueryPoolOcclusionTest::checkSupport()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp:1497) |
| `VK_KHR_device_address_commands` | `_device_address` variants | [`QueryPoolOcclusionTest::checkSupport()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp:1488) |
| 4× sample-count support for `VK_FORMAT_R8G8B8A8_UNORM` transfer source usage | `resolve` variant | [`QueryPoolOcclusionTest::checkSupport()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp:1504) |

### Vulkan SC behavior

The file contains explicit `#ifndef CTS_USES_VULKANSC` handling in two places:

- Query-pool creation can use `VK_QUERY_POOL_CREATE_RESET_BIT_KHR` only in non-SC builds inside [`makeOcclusionQueryPool()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp:54).
- `_device_address` test registration is compiled out in SC builds in [`QueryPoolOcclusionTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp:2019).

As a result, Vulkan SC does not include the device-address-command sub-variants documented above.

## Verification Strategy

### Basic instance checks

The simpler cases use [`BasicOcclusionQueryTestInstance::iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp:468), which validates that the query result path behaves correctly for focused scenarios such as clear-attachments, blit/resolve side paths, and no-attachment rendering.

### Functional instance checks

The broader matrix uses [`OcclusionQueryTestInstance::iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp:821). Verification logic distinguishes between precise and conservative semantics:

| Query mode | Expected result rule |
|-----------|----------------------|
| Precise | Exact sample counts are compared for each query slot |
| Conservative | Non-zero visibility is sufficient for hit cases |
| Availability-enabled modes | Result buffers are interpreted with value + availability pairs |
| Reset-validation modes | Post-reset reads or copies must show cleared / unavailable state as appropriate |

The pass/fail helper for the core result comparison is implemented in the logic ending at [`vktQueryPoolOcclusionTests.cpp:1471`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp:1471), where conservative mode accepts any non-zero value for visible samples.

## Notes

- The group mixes regular `TestCase`-based registrations with function-style cases using [`addFunctionCaseWithPrograms()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp:1767).
- The file intentionally uses a much larger parameter matrix for general query semantics than for device-address-command coverage, keeping the latter sampled rather than exhaustive.
- No Level-2 category document is created here; this page documents only the Level-3 file represented by [`vktQueryPoolOcclusionTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp).
