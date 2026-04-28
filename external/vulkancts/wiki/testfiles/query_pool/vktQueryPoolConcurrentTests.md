# Concurrent Query Tests

Tests for concurrent use of different Vulkan query types under `query_pool`. This page documents the `concurrent_queries` Level-3 group registered from [`vktQueryPoolTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L52) and implemented in [`vktQueryPoolConcurrentTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp).

## Source

- [`vktQueryPoolTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp)
- [`vktQueryPoolConcurrentTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp)

## Registration

| Item | Value |
|------|-------|
| Top-level parent | `query_pool` via [`createTests()`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L59) |
| Level-3 group name | `concurrent_queries` via [`QueryPoolConcurrentTests::QueryPoolConcurrentTests()`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L906) |
| Child registration | [`queryPoolTests->addChild(new QueryPoolConcurrentTests(testCtx))`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L52) |
| Group population | [`QueryPoolConcurrentTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L912) |

## Summary

The `concurrent_queries` group validates that a device can use more than one query type in the same workload without cross-interference. It combines occlusion, pipeline statistics, and timestamp queries around the same draw sequence and checks that each query pool reports results consistent with its own capture window. The group contains exactly two test cases: one centered on a primary command buffer and one centered on a secondary command buffer.

## Test Hierarchy

```text
query_pool
└── concurrent_queries
    ├── primary_command_buffer
    └── secondary_command_buffer
```

The two leaf registrations are performed in [`QueryPoolConcurrentTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L912).

## Registered Cases

### `primary_command_buffer`

This case is implemented by [`PrimaryCommandBufferConcurrentTestInstance`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L261). It records all query activity in a primary command buffer and validates concurrent operation of:

- occlusion queries;
- pipeline statistics queries using `VK_QUERY_PIPELINE_STATISTIC_FRAGMENT_SHADER_INVOCATIONS_BIT`;
- timestamp queries when supported.

The constructor creates one query pool per supported query type in [`PrimaryCommandBufferConcurrentTestInstance::PrimaryCommandBufferConcurrentTestInstance()`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L283), using `NUM_QUERIES_IN_POOL = 2` with slots for:

| Slot | Meaning |
|------|---------|
| `0` | `QUERY_INDEX_CAPTURE_EMPTY` |
| `1` | `QUERY_INDEX_CAPTURE_DRAWCALL` |

The enumeration and slot constants are defined in [`PrimaryCommandBufferConcurrentTestInstance`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L270).

### `secondary_command_buffer`

This case is implemented by [`SecondaryCommandBufferConcurrentTestInstance`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L527). It distributes the workload across a primary and a secondary command buffer, then verifies that concurrent query execution still behaves correctly.

It also adapts its occlusion-query behavior depending on whether inherited queries are supported. That support check is read from [`m_context.getDeviceFeatures().inheritedQueries`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L620).

## Query Types Covered

The file defines three candidate query types in [`QueryType`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L55):

| Enum entry | Vulkan query type | Notes |
|-----------|-------------------|-------|
| `QUERY_TYPE_OCCLUSION` | `VK_QUERY_TYPE_OCCLUSION` | Always considered supported by these tests |
| `QUERY_TYPE_PIPELINE_STATISTICS` | `VK_QUERY_TYPE_PIPELINE_STATISTICS` | Requires `pipelineStatisticsQuery` feature |
| `QUERY_TYPE_TIMESTAMP` | `VK_QUERY_TYPE_TIMESTAMP` | Requires queue-family `timestampValidBits > 0` |

For pipeline statistics pools, the test requests `VK_QUERY_PIPELINE_STATISTIC_FRAGMENT_SHADER_INVOCATIONS_BIT` in both constructors; see [`PrimaryCommandBufferConcurrentTestInstance::PrimaryCommandBufferConcurrentTestInstance()`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L323) and [`SecondaryCommandBufferConcurrentTestInstance::SecondaryCommandBufferConcurrentTestInstance()`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L588).

## Support Requirements

### Minimum concurrent-query capability

Both test cases use the shared [`QueryPoolConcurrentTest::checkSupport()`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L858). Rather than requiring all three query types, the test requires support for at least two distinct query types:

- occlusion is counted as always available for the purpose of this check;
- pipeline statistics contributes if `pipelineStatisticsQuery` is enabled;
- timestamp contributes if the universal queue family reports non-zero `timestampValidBits`.

If fewer than two query types are supported, the test throws `NotSupportedError`; see [`QueryPoolConcurrentTest::checkSupport()`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L871).

### Detailed requirements by feature

| Requirement | Needed for | Source |
|------------|------------|--------|
| `pipelineStatisticsQuery` feature | Pipeline-statistics query participation | [`PrimaryCommandBufferConcurrentTestInstance::PrimaryCommandBufferConcurrentTestInstance()`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L293) and [`SecondaryCommandBufferConcurrentTestInstance::SecondaryCommandBufferConcurrentTestInstance()`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L558) |
| Queue-family `timestampValidBits > 0` | Timestamp query participation | [`PrimaryCommandBufferConcurrentTestInstance::PrimaryCommandBufferConcurrentTestInstance()`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L300) and [`SecondaryCommandBufferConcurrentTestInstance::SecondaryCommandBufferConcurrentTestInstance()`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L565) |
| `inheritedQueries` feature | Inherited occlusion behavior in `secondary_command_buffer` | Read in [`SecondaryCommandBufferConcurrentTestInstance::iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L620) |

### Vulkan SC behavior

Unlike the occlusion and statistics files, this file does not register any non-SC-only `_device_address` variants or use `#ifndef CTS_USES_VULKANSC` to split the hierarchy. The documented group names therefore remain the same conceptually across Vulkan and Vulkan SC, subject only to the runtime support conditions above.

## Rendering and Shader Setup

Both test cases use a common render setup built by [`StateObjects::StateObjects()`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L92):

- a color attachment and depth attachment;
- a graphics pipeline with vertex and fragment shaders;
- a simple vertex buffer containing one triangle.

The two shader programs are registered in [`QueryPoolConcurrentTest::initPrograms()`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L880):

| Shader | Behavior |
|--------|----------|
| Vertex shader | Pass-through position and point-size setup |
| Fragment shader | Writes color and discards alternating fragments based on `gl_FragCoord` parity |

That fragment discard pattern ensures that occlusion and fragment-invocation counters observe meaningful non-zero activity while still exercising partial coverage.

## Primary Command Buffer Flow

[`PrimaryCommandBufferConcurrentTestInstance::iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L333) follows this sequence:

1. Allocate a primary command buffer.
2. Reset all supported query pools.
3. Begin a render pass.
4. Begin the “empty” occlusion and pipeline-statistics captures in slot `0`.
5. End slot `0` and begin the draw-call captures in slot `1`.
6. Issue a triangle draw.
7. Write a timestamp into slot `1` if timestamp queries are supported.
8. End slot `1` for occlusion and pipeline-statistics pools.
9. Submit, wait, and read back query results.

The transitions from empty capture to draw capture occur in [`PrimaryCommandBufferConcurrentTestInstance::iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L375) and [`PrimaryCommandBufferConcurrentTestInstance::iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L382).

## Secondary Command Buffer Flow

[`SecondaryCommandBufferConcurrentTestInstance::iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L614) splits work between two command buffers.

### Secondary recording

The secondary command buffer:

- binds the graphics pipeline and vertex buffer;
- optionally begins and ends the draw-call occlusion query locally when inherited queries are not used;
- begins and ends the pipeline-statistics draw-call query;
- writes a timestamp for the draw-call slot;
- records the draw call itself.

This behavior is recorded in [`SecondaryCommandBufferConcurrentTestInstance::iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L630).

### Primary recording

The primary command buffer:

- resets all supported query pools;
- records the empty capture for occlusion and pipeline statistics in slot `0`;
- if inherited queries are supported, begins the draw-call occlusion query in the primary command buffer before executing the secondary command buffer;
- begins the render pass with `VK_SUBPASS_CONTENTS_SECONDARY_COMMAND_BUFFERS`;
- executes the secondary command buffer;
- ends inherited occlusion capture afterward when applicable.

This sequencing is implemented in [`SecondaryCommandBufferConcurrentTestInstance::iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L676).

### Inheritance setup

The helper [`beginSecondaryCommandBuffer()`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L598) begins the secondary buffer with explicit inheritance information. The inheritance struct sets:

- the render pass and framebuffer;
- `occlusionQueryEnable` according to the device `inheritedQueries` feature;
- zero query flags and zero pipeline-statistics inheritance mask.

The inheritance info is assembled in [`SecondaryCommandBufferConcurrentTestInstance::iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L633).

## Verification Rules

### Occlusion and pipeline-statistics pools

Both test instances read back occlusion and pipeline-statistics results as 64-bit values with [`vkGetQueryPoolResults`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L425) and [`vkGetQueryPoolResults`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L746).

The verification rule is the same in both cases:

| Query slot | Expected outcome |
|-----------|------------------|
| Empty slot (`0`) | Result must be `0` |
| Draw-call slot (`1`) | Result must be non-zero |

This logic appears in [`PrimaryCommandBufferConcurrentTestInstance::iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L445) and [`SecondaryCommandBufferConcurrentTestInstance::iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L767).

### Timestamp pool

Timestamp queries are read back with `VK_QUERY_RESULT_WITH_AVAILABILITY_BIT` in both test instances; see [`PrimaryCommandBufferConcurrentTestInstance::iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L475) and [`SecondaryCommandBufferConcurrentTestInstance::iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L797).

The expected rule is intentionally asymmetric:

| Query slot | Expected value | Expected availability |
|-----------|----------------|-----------------------|
| Empty slot (`0`) | `0` | `0` |
| Draw-call slot (`1`) | non-zero | non-zero |

Additionally, the test expects the call itself to return `VK_NOT_READY`, because one timestamp query in the pool was never written and therefore remains unavailable. This is checked in [`PrimaryCommandBufferConcurrentTestInstance::iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L802) and again in [`SecondaryCommandBufferConcurrentTestInstance::iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L802).

## Notes

- Each test uses exactly two query slots per pool, making the distinction between an intentionally empty capture and an active draw capture explicit.
- The pipeline-statistics portion measures fragment shader invocations only, which keeps the concurrent case focused while still overlapping meaningfully with occlusion and timestamp activity.
- The group does not enumerate separate Vulkan / Vulkan SC subgroup names; support differences are handled through runtime capability checks rather than registration-time branching.
- This page documents only the Level-3 file represented by [`vktQueryPoolConcurrentTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp).
