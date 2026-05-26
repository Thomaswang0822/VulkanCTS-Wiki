# vktFragmentOperationsScissorMultiViewportTests.cpp

## Overview

[`vktFragmentOperationsScissorMultiViewportTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L1) implements the nested `multi_viewport` subgroup beneath [`fragment_operations.scissor`](./vktFragmentOperationsScissorTests.md). The file verifies that each viewport-scissor pair clips its own fullscreen quad correctly when multiple viewports are active.

## Role

Registration and implementation file for a nested subgroup. It is not a root `fragment_operations` child, but it does register user-visible cases under `fragment_operations.scissor.multi_viewport`.

## Source Code

- Primary source: [`vktFragmentOperationsScissorMultiViewportTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L1)
- Header: [`vktFragmentOperationsScissorMultiViewportTests.hpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.hpp)
- Parent subgroup file: [`vktFragmentOperationsScissorTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L573-L576)

## Registration Hierarchy

```text
fragment_operations.scissor.multi_viewport
├── scissor_1
├── scissor_2
├── scissor_3
├── scissor_4
├── scissor_5
├── scissor_6
├── scissor_7
├── scissor_8
├── scissor_9
├── scissor_10
├── scissor_11
├── scissor_12
├── scissor_13
├── scissor_14
├── scissor_15
└── scissor_16
```

Source: [`createScissorMultiViewportTests()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L442-L450).

## Test Families

### `scissor_1` through `scissor_16` — viewport-count sweep

[`createScissorMultiViewportTests()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L442-L450) loops `numViewports` from `1` through [`MIN_MAX_VIEWPORTS`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L61-L64), registering one case per count through `addFunctionCaseWithPrograms()`. The case names are formed as `scissor_` plus the viewport count at [`vktFragmentOperationsScissorMultiViewportTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L446-L448).

## Parameter Dimensions

| Dimension | Observed values / source |
|---|---|
| Viewport count | 1 through 16 from the registration loop at [`vktFragmentOperationsScissorMultiViewportTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L446-L448) |
| Guaranteed viewport floor | `MIN_MAX_VIEWPORTS = 16` in [`vktFragmentOperationsScissorMultiViewportTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L61-L64) |
| Scissor layout | Grid-arranged rectangles generated from `numScissors` and `renderSize` in [`generateScissors()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L131-L161) |
| Color palette size | Up to 16 predefined colors in [`generateColors()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L163-L177) |
| Primitive expansion model | One input point emits a fullscreen quad in the geometry shader built by [`initPrograms()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L219-L260) |

## Support Requirements

[`checkSupport()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L431-L438) requires both `geometryShader` and `multiViewport` core features, and rejects implementations whose `maxViewports` limit is below [`MIN_MAX_VIEWPORTS`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L61-L64). The pipeline setup uses one viewport and one scissor rectangle per requested viewport count in [`makeGraphicsPipeline()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L94-L129).

## Verification Methods

The file generates a reference image by clearing the render target and then clearing each scissor subregion to its expected color in [`generateReferenceImage()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L179-L197). Rendered output is compared with [`tcu::floatThresholdCompare()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L422-L425).

## Notes / Uncertainties

- This file is implementation-heavy despite registering only one nested subgroup name.
- The visible shader design uses `gl_ViewportIndex = gl_PrimitiveIDIn` in the geometry shader so each emitted fullscreen quad maps to a distinct viewport-scissor pair at [`vktFragmentOperationsScissorMultiViewportTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L236-L256).
