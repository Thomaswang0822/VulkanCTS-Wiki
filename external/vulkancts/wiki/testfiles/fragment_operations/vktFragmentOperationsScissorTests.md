# vktFragmentOperationsScissorTests.cpp

## Overview

[`vktFragmentOperationsScissorTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L1) implements the displayed `scissor` subgroup registered under [`fragment_operations`](../../categories/fragment_operations.md). The file verifies fixed scissor clipping for point, line, and triangle draws, and delegates the nested `multi_viewport` subgroup to [`vktFragmentOperationsScissorMultiViewportTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L25-L28) and [`vktFragmentOperationsScissorTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L573-L576).

## Role

Registration and implementation file. It owns the `scissor` subgroup and combines direct draw-based clipping cases with a nested multi-viewport scissor family.

## Source Code

- Primary source: [`vktFragmentOperationsScissorTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L1)
- Header: [`vktFragmentOperationsScissorTests.hpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.hpp)
- Nested subgroup helper: [`vktFragmentOperationsScissorMultiViewportTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L1)

## Registration Hierarchy

```text
fragment_operations.scissor
├── points
├── lines
├── triangles
└── multi_viewport
```

Source: [`createScissorTests()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L581-L584) and [`createTestsInGroup()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L512-L576).

## Test Families

### `points` — scissor clipping of randomly generated points

The `points` child is created in [`vktFragmentOperationsScissorTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L512-L529). It registers three leaf cases:

- `inside`
- `partially_inside`
- `outside`

These cases pair different render and scissor areas while using [`TEST_PRIMITIVE_POINTS`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L62-L69) in the `CaseDef` table at [`vktFragmentOperationsScissorTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L516-L523).

### `lines` — scissor clipping of short and full-span lines

The `lines` child is created in [`vktFragmentOperationsScissorTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L531-L550). It registers:

- `inside`
- `partially_inside`
- `outside`
- `crossing`

The first three use [`TEST_PRIMITIVE_LINES`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L62-L69), while `crossing` uses [`TEST_PRIMITIVE_BIG_LINE`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L67-L68) through the table at [`vktFragmentOperationsScissorTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L535-L544).

### `triangles` — scissor clipping of small and full-span triangles

The `triangles` child is created in [`vktFragmentOperationsScissorTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L552-L571). It registers:

- `inside`
- `partially_inside`
- `outside`
- `crossing`

The first three use [`TEST_PRIMITIVE_TRIANGLES`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L62-L69), while `crossing` uses [`TEST_PRIMITIVE_BIG_TRIANGLE`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L67-L69) through the table at [`vktFragmentOperationsScissorTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L556-L565).

### `multi_viewport` — delegated nested subgroup

The `multi_viewport` child is not implemented in this file. It is added by calling [`createScissorMultiViewportTests()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L573-L576), which is documented separately in [`vktFragmentOperationsScissorMultiViewportTests.md`](vktFragmentOperationsScissorMultiViewportTests.md).

## Parameter Dimensions

| Dimension | Observed values / source |
|---|---|
| Primitive class | Points, lines, triangles, big line, big triangle in [`TestPrimitive`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L61-L69) |
| Coverage relation | `inside`, `partially_inside`, `outside`, `crossing` from the registration tables at [`vktFragmentOperationsScissorTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L516-L565) |
| Render area | `areaFull`, `areaCropped`, `areaCroppedMore`, `areaLeftHalf`, `areaRightHalf` at [`vktFragmentOperationsScissorTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L506-L510) |
| Vertex generation count | 50 points, 30 short lines, 20 small triangles in [`genVertices()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L183-L239) |
| Topology mapping | Point list, line list, triangle list in [`getTopology()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L241-L259) |

## Support Requirements

This file does not expose a dedicated `checkSupport()` gate in the inspected registration path. The pipeline is built with one viewport and one scissor rectangle in [`makeGraphicsPipeline()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L114-L175), so the documented direct cases rely on core graphics pipeline functionality rather than explicit extension checks in the inspected code.

## Verification Methods

The file includes [`tcuImageCompare.hpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L39-L42) and builds a reference path by drawing once with the full scissor, drawing once with the case scissor, then applying the case scissor to the full-scissor image in [`applyScissor()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L271-L286) and [`test()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L439-L491). Rendered output is compared with [`tcu::floatThresholdCompare()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L485-L488).

## Notes / Uncertainties

- This file is both a user-facing subgroup registration file and an implementation file.
- The direct evidence inspected here confirms the displayed subgroup names, parameter tables, support behavior, and image-comparison verification path for the single-viewport scissor cases.
