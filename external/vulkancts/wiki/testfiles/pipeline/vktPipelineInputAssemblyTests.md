# vktPipelineInputAssemblyTests.cpp

## Overview

[`vktPipelineInputAssemblyTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L1) implements the [`input_assembly`](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L2340) topic group of the pipeline category. It verifies primitive topology rendering, primitive restart functionality, and mixed indexed/non-indexed draw behavior with primitive restart enabled.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineInputAssemblyTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L1)
- Header: [`vktPipelineInputAssemblyTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.hpp#L1)
- Shared helpers: [`ReferenceRenderer`](../../../modules/vulkan/pipeline/vktPipelineReferenceRenderer.cpp#L1)

## Registration Path

This file contributes the subgroup returned by [`createInputAssemblyTests()`](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L2340), which is attached under each variant root by [`createChildren()`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L1).

**Variant coverage**: All variants.

## Test Hierarchy

```text
input_assembly
├── primitive_topology
│   ├── index_type_uint16
│   │   ├── point_list
│   │   ├── line_list
│   │   ├── line_strip
│   │   ├── triangle_list
│   │   ├── triangle_strip
│   │   ├── triangle_fan
│   │   ├── line_list_with_adjacency
│   │   ├── line_strip_with_adjacency
│   │   ├── triangle_list_with_adjacency
│   │   └── triangle_strip_with_adjacency
│   ├── index_type_uint32
│   │   └── (same topologies)
│   └── index_type_uint8
│       └── (same topologies)
├── primitive_restart                      (non-VulkanSC)
│   ├── index_type_uint16
│   │   ├── <topology_name>               (RestartType::NORMAL)
│   │   ├── no_restart_<topology_name>    (RestartType::NONE)
│   │   ├── restart_all_<topology_name>   (RestartType::ALL)
│   │   ├── divide_draw_<topology_name>   (RestartType::DIVIDE)
│   │   └── second_pass_<topology_name>   (RestartType::SECOND_PASS)
│   ├── index_type_uint32
│   │   └── (same pattern)
│   ├── index_type_uint8
│   │   └── (same pattern)
│   ├── restart_disabled_*                (Amber tests, monolithic only)
│   └── restart_mix
│       ├── restart_mix
│       ├── restart_mix_extra_draw
│       ├── restart_mix_triangle_list
│       ├── restart_mix_extra_draw_triangle_list
│       ├── restart_mix_dynamic_topo
│       └── ... (combinatorial: extraDraw x triangleList x dynamicTopology x largeNonIndexedDraw)
└── (end)
```

Source: [`createInputAssemblyTests()`](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L2340).

## Test Families

### 1. primitive_topology

Verifies correct rendering of all 10 standard primitive topologies using indexed draws with each index type (uint16, uint32, uint8). Uses [`PrimitiveTopologyTest`](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L1) / [`InputAssemblyInstance`](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L1).

### 2. primitive_restart

Verifies primitive restart functionality across strip/list/fan/adjacency/patch topologies. Uses [`PrimitiveRestartTest`](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L1) / [`InputAssemblyInstance`](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L1). Includes list-type restart via `VK_EXT_primitive_topology_list_restart`. Five restart modes: NORMAL, NONE (restart disabled), ALL (all-primitive restart), DIVIDE (split draw), SECOND_PASS.

### 3. restart_mix

Verifies correct behavior when mixing indexed and non-indexed draws with primitive restart enabled. Uses [`PrimitiveRestartMixCase`](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L1). Tests extra indexed draws, triangle list vs strip, dynamic topology, and large non-indexed draws.

### 4. restart_disabled_* (Amber)

Verifies that when primitive restart is disabled, the restart index value does not cause a restart. Monolithic pipeline only.

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| VkPrimitiveTopology (topology tests) | [Array](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L210) | 10 topologies: POINT_LIST through TRIANGLE_STRIP_WITH_ADJACENCY |
| VkPrimitiveTopology (restart tests) | [Array](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L2189) | 11 topologies (adds PATCH_LIST; list types require `VK_EXT_primitive_topology_list_restart`) |
| VkPrimitiveTopology (mixed restart) | [Array](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L2199) | 6 list-type topologies (POINT_LIST through PATCH_LIST) |
| VkIndexType | [Loop](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L1708) | UINT16, UINT32, UINT8_EXT |
| RestartType | [Enum](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L62) | NORMAL, NONE, ALL, DIVIDE, SECOND_PASS |
| extraIndexedDraws | Loop | `false`, `true` |
| triangleList | Loop | `false`, `true` |
| dynamicTopology | Loop | `false`, `true` |
| largeNonIndexedDraw | Loop | `false`, `true` (only when triangleList=true) |

## Support / Feature Requirements

| Requirement | Where | Line |
|---|---|---|
| `VK_KHR_index_type_uint8` / `VK_EXT_index_type_uint8` (for UINT8 index type) | `InputAssemblyTest::checkSupport` | [244](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L244) |
| `DEVICE_CORE_FEATURE_GEOMETRY_SHADER` (for adjacency topologies) | `InputAssemblyTest::checkSupport` | [259](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L259) |
| `DEVICE_CORE_FEATURE_TESSELLATION_SHADER` (for PATCH_LIST) | `InputAssemblyTest::checkSupport` | [263](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L263) |
| `VK_KHR_portability_subset` / `triangleFans` (for TRIANGLE_FAN) | `InputAssemblyTest::checkSupport` | [274](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L274) |
| `VK_EXT_primitive_topology_list_restart` + `primitiveTopologyListRestart` feature (for list/patch topologies) | `PrimitiveRestartTest::checkSupport` | [769](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L769) |
| `primitiveTopologyPatchListRestart` feature (for PATCH_LIST specifically) | `PrimitiveRestartTest::checkSupport` | [774](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L774) |
| `VK_EXT_extended_dynamic_state` (when dynamicTopology=true) | `PrimitiveRestartMixCase::checkSupport` | [1805](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L1805) |

## Verification Methods

### primitive_topology and primitive_restart families

**Reference renderer comparison** (`tcu::intThresholdPositionDeviationCompare`) with threshold UVec4(2,2,2,2) and position deviation IVec3(1,1,0). Uses [`ReferenceRenderer`](../../../modules/vulkan/pipeline/vktPipelineReferenceRenderer.cpp#L1) (software rasterizer) with `ColorVertexShader`/`ColorFragmentShader` to produce a reference image. For restart-enabled tests, the reference renderer splits the index list at restart indices and draws each sub-range separately. [Line 1572](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L1572).

### restart_mix family

**Float threshold comparison** (`tcu::floatThresholdCompare`) with threshold Vec4(0.0). Constructs a reference image by clearing quadrants with expected colors, then compares. [Line 2178](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L2178).

### restart_disabled_* (Amber)

Delegated to Amber test runner.

## Test Principles Observed

- **Complete topology coverage**: All 10 standard primitive topologies are tested
- **Index type orthogonality**: Each topology is tested with all supported index types
- **Restart mode variety**: Five distinct restart modes exercise different code paths
- **Mixed draw validation**: `restart_mix` tests realistic scenarios where indexed and non-indexed draws are interleaved

## Notes / Uncertainties

- `primitive_restart` and `restart_mix` are excluded for VulkanSC (`#ifndef CTS_USES_VULKANSC`)
- Amber `restart_disabled_*` tests are monolithic only
