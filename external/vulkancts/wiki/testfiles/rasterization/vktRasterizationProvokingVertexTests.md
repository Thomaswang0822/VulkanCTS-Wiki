# vktRasterizationProvokingVertexTests.cpp

## Overview

[`vktRasterizationProvokingVertexTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationProvokingVertexTests.cpp#L1) implements the non-VulkanSC `provoking_vertex` subgroup registered by [`createProvokingVertexTests()`](../../../modules/vulkan/rasterization/vktRasterizationProvokingVertexTests.cpp#L1156-L1159). The group checks provoking-vertex conventions for flat-shaded drawing and transform-feedback preservation across multiple primitive topologies.

## Role

Implementation file.

## Source Code

- Primary source: [`vktRasterizationProvokingVertexTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationProvokingVertexTests.cpp#L1)
- Header: [`vktRasterizationProvokingVertexTests.hpp`](../../../modules/vulkan/rasterization/vktRasterizationProvokingVertexTests.hpp#L35)

## Registration Hierarchy

```text
rasterization.provoking_vertex
├── draw
└── transform_feedback
```

## Test Families

### draw — Flat-shaded provoking-vertex rendering

The `draw` group is one of the two `testTypes[]` registrations at [`vktRasterizationProvokingVertexTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationProvokingVertexTests.cpp#L1110-L1117). It registers `default`, `first`, `last`, and `per_pipeline` provoking-mode children at [`vktRasterizationProvokingVertexTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationProvokingVertexTests.cpp#L1073-L1093), with cases for line-list, line-strip, triangle-list, triangle-strip, triangle-fan, and adjacency topologies at [`vktRasterizationProvokingVertexTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationProvokingVertexTests.cpp#L1095-L1108).

### transform_feedback — Transform-feedback preservation

The `transform_feedback` group uses the same provoking modes except `default`, because default mode is skipped when `transformFeedback` is true at [`vktRasterizationProvokingVertexTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationProvokingVertexTests.cpp#L1123-L1127). It uses the same topology table and sets `transformFeedback` in the registered parameters at [`vktRasterizationProvokingVertexTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationProvokingVertexTests.cpp#L1131-L1144).

## Parameter Dimensions

| Dimension | Observed values / source |
|---|---|
| Test type | `draw` and `transform_feedback` at [`testTypes[]`](../../../modules/vulkan/rasterization/vktRasterizationProvokingVertexTests.cpp#L1110-L1117) |
| Provoking-vertex mode | `default`, `first`, `last`, `per_pipeline` at [`provokingVertexModes[]`](../../../modules/vulkan/rasterization/vktRasterizationProvokingVertexTests.cpp#L1073-L1093) |
| Primitive topology | Five non-adjacency and four adjacency topologies at [`topologies[]`](../../../modules/vulkan/rasterization/vktRasterizationProvokingVertexTests.cpp#L1095-L1108) |
| Render target | `VK_FORMAT_R8G8B8A8_UNORM` and `32x32` size in `Params` at [`vktRasterizationProvokingVertexTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationProvokingVertexTests.cpp#L1135-L1142) |

## Support / Feature Requirements

Adjacency topologies require geometry shader support at [`ProvokingVertexTestCase::checkSupport()`](../../../modules/vulkan/rasterization/vktRasterizationProvokingVertexTests.cpp#L202-L205). Transform-feedback tests require `VK_EXT_transform_feedback` at [`vktRasterizationProvokingVertexTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationProvokingVertexTests.cpp#L207-L208). Non-default modes require `VK_EXT_provoking_vertex`; additional feature/property checks cover transform-feedback preservation, triangle-fan preservation, `provokingVertexLast`, and `provokingVertexModePerPipeline` at [`vktRasterizationProvokingVertexTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationProvokingVertexTests.cpp#L210-L232). Triangle fans are rejected when portability subset reports no triangle-fan support at [`vktRasterizationProvokingVertexTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationProvokingVertexTests.cpp#L235-L241).

## Verification Methods

Transform-feedback variants verify captured vertices with [`verifyXfbBuffer()`](../../../modules/vulkan/rasterization/vktRasterizationProvokingVertexTests.cpp#L968-L985). Rendering variants build a solid-red reference surface and use exact memory comparison against the result image at [`vktRasterizationProvokingVertexTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationProvokingVertexTests.cpp#L988-L1002).

## Test Principles Observed

- **Mode coverage**: default, first-vertex, last-vertex, and per-pipeline provoking modes are separated into registered subgroups.
- **Topology breadth**: the same mode families are applied across non-adjacency and geometry-shader adjacency topologies.
- **Dual observation paths**: draw tests validate framebuffer color, while transform-feedback tests validate captured provoking-vertex behavior.

## Notes / Uncertainties

- The group is registered only on non-VulkanSC builds by the parent file at [`vktRasterizationTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationTests.cpp#L10294-L10299).
