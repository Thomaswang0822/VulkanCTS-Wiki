# vktPrimitivesGeneratedQueryTests.cpp

## Overview

[`vktPrimitivesGeneratedQueryTests.cpp`](../../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L1) registers [`primitives_generated_query`](../../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L3062-L3065), checking `VK_EXT_primitives_generated_query` behavior with and without transform-feedback queries.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPrimitivesGeneratedQueryTests.cpp`](../../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L1)

## Registration Hierarchy

```text
transform_feedback.primitives_generated_query
├── concurrent
├── copy
└── get
```

## Test Families

### get / copy — Query readback modes

The main generator creates read groups for query-pool get/copy paths, reset types, result widths, shader stages, XFB enablement, rasterization modes, topologies, stream indices, command-buffer structure, query order, outside draws, query count, and availability-bit cases in [`testGenerator()`](../../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L2801-L2987).

### concurrent — Concurrent query scenarios

The `concurrent` group combines concurrent test types, result widths, topologies, and direct/indirect draw modes in [`concurrentGroup`](../../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L2989-L3057).

## Parameter Dimensions

Visible dimensions include read type, reset type, result type, shader stage, transform-feedback enablement, rasterization case, topology, PGQ and XFB stream indices, command-buffer case, query order, outside-draw placement, query count, availability bit, and concurrent query type.

## Support / Feature Requirements

[`PrimitivesGeneratedQueryTestCase::checkSupport()`](../../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L1243-L1295) requires `VK_EXT_primitives_generated_query`, `VK_EXT_transform_feedback`, the PGQ feature, rasterizer-discard support when needed, host query reset when selected, geometry/tessellation shader core features for selected stages/topologies, nonzero stream support, transform-feedback feature/query properties, and color-write-enable support for color-write-disable cases. Concurrent cases add pipeline-statistics and inherited-query requirements in [`ConcurrentPrimitivesGeneratedQueryTestCase::checkSupport()`](../../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L2397-L2447).

## Verification Methods

The test reads or copies query results and compares generated/written counters against expected primitive counts in the validation loop at [`iterate()`](../../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L777-L850).

## Test Principles Observed
- The category cross-checks primitives-generated-query results against transform-feedback query results where XFB is enabled.
- The matrix explicitly filters invalid stage/topology and stream combinations before registration.

## Notes / Uncertainties

- This page documents source-observed registration and verification behavior. The hierarchy tree lists the complete direct children of the documented registered group; generated cases inside those children are summarized in prose.
