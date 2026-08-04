## Overview

**Core question:** Does input assembly turn the selected indexed or non-indexed vertex stream into the intended primitives, including primitive-restart boundaries?

- [`vktPipelineInputAssemblyTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L242-L2350) implements `pipeline.*.input_assembly`.
- `primitive_topology` checks ten topology values with three index widths. The Vulkan-SC-excluded `primitive_restart` family checks restart placement and retained state, including indexed/non-indexed transitions.
- The ordinary families compare rendered output with `ReferenceRenderer`; `restart_mix` compares the readback image with fixed quadrant colors.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- `VkPipelineInputAssemblyStateCreateInfo::topology` determines how vertex inputs form points, lines, triangles, adjacency primitives, or patches. For indexed draws, primitive restart treats the reserved index value for the selected index type as a new assembly boundary. [Vulkan input assembly](../../../../vulkan-docs/src/chapters/drawing.adoc#L49-L89) defines the state, values, and list-topology restrictions.
- Restart affects indexed draws only. Vulkan compares an index with the restart value before adding `vertexOffset`; incomplete assembly before a restart is discarded. [Indexed drawing](../../../../vulkan-docs/src/chapters/drawing.adoc#L1238-L1268) defines that order.

## Registration Hierarchy

```text
pipeline.monolithic.input_assembly
├── primitive_topology
└── primitive_restart
```

[`createInputAssemblyTests()`](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L2340-L2350) registers the same source-owned family for each applicable pipeline-construction type. The inspected default mustpass files contain 196 `input_assembly` leaves for `monolithic` and 174 each for `fast_linked_library`, `pipeline_library`, `shader_object_linked_binary`, `shader_object_linked_spirv`, `shader_object_unlinked_binary`, and `shader_object_unlinked_spirv`. `primitive_restart` is compiled out for Vulkan SC.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test family | `primitive_topology`, `primitive_restart` | Selects basic topology assembly or restart behavior. | [`createInputAssemblyTests()`](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L2340-L2350) |
| Index type | `index_type_uint16`, `index_type_uint32`, `index_type_uint8` | Changes the encoded index width and reserved restart value. | [topology registration](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L1703-L1731) |
| Topology, basic family | 10 values from `POINT_LIST` through `TRIANGLE_STRIP_WITH_ADJACENCY` | Changes the assembly rule applied to the indexed vertices. | [`s_primitiveTopologies` use](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L1712-L1724) |
| Topology, restart family | 11 values; `DIVIDE` and `SECOND_PASS` use 6 list topologies | Separates ordinary restart coverage from fixed-vertex-count split-draw coverage. | [restart topology arrays](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L2189-L2206) |
| Restart mode | `NORMAL`, `NONE`, `ALL`, `DIVIDE`, `SECOND_PASS` | Changes where restart values occur, or uses an enabled-restart stream with no restart value. | [mode registration](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L2214-L2274) |
| `restart_mix` flags | `extraIndexedDraws`, `triangleList`, `dynamicTopology`, `largeNonIndexedDraw` | Changes draw ordering, topology source, and the size of the non-indexed draw. `largeNonIndexedDraw` requires `triangleList`. | [mix matrix](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L2313-L2331) |

## Behavior Parameters

The primary behavioral axis is the test family. Restart modes are important values within `primitive_restart` because they change the placement and lifetime condition being tested.

### `primitive_topology` - topology and index-width assembly

Each index-type branch registers the same ten topology leaves. The test generates matching vertex and index buffers, draws indexed primitives, and checks whether the image matches a software reference. Adjacency topologies require geometry shader support; `PATCH_LIST` requires tessellation shader support.

### `primitive_restart` - restart boundary placement

This family enables restart and inserts reserved values into generated index data. `NORMAL` uses restart primitives 1 and 5, `NONE` supplies no restart primitive, `ALL` inserts restart values at fixed primitive intervals, and `DIVIDE` or `SECOND_PASS` use the restricted list-topology array. The constructor records those placements before normal input-assembly execution. [`PrimitiveRestartTest`](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L702-L756)

### `restart_mix` - restart state across draw forms

The `restart_mix` intermediate node first draws indexed geometry with restart enabled, then draws a non-indexed quadrant without disabling restart. Some variants return to indexed draws; some select the final topology dynamically; the large variant uses a vertex count above the UINT16 restart value before its visible triangles. The expected image exposes state that leaks into non-indexed drawing or disappears before a later indexed draw. [`PrimitiveRestartMixTest::iterate()`](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L1834-L2184)

### `restart_disabled_*` - reserved index used as ordinary data

Monolithic Amber leaves set up each supported topology with restart disabled while an index has the reserved value. They check that the value does not create a boundary. [`restart_disabled_*` registration](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L2276-L2306)

## Shader Analysis

The shaders only pass vertex position and color through to the color attachment. Fixed-function input assembly determines topology and primitive restart, so a GLSL or SPIR-V walkthrough would not inspect the property under test. [`InputAssemblyTest::initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L296-L320) and [`PrimitiveRestartMixCase::initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L1811-L1831) show the pass-through programs. Shader analysis and disassembly are not applicable.

## Runtime Execution and Result Checking

- Ordinary cases generate vertex and index data, create a color attachment, bind the graphics pipeline and buffers, draw, and read the image back. The reference renderer receives the same primitive data and splits restart-enabled index streams at restart indices before rendering. [`InputAssemblyInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L1300-L1649)
- The ordinary comparison permits `UVec4(2, 2, 2, 2)` channel error and `IVec3(1, 1, 0)` position deviation. An image mismatch fails the case. [`comparison`](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L1641-L1649)
- `restart_mix` creates a 32 by 32 target divided into four colored quadrants. It issues the chosen indexed and non-indexed draws, copies the color image to a buffer, clears the reference quadrants that should have geometry, then requires an exact float comparison. [`result check`](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L2147-L2183)

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `primitive_topology` | Incorrect topology selection, index-width handling, vertex fetch, primitive assembly, rasterization, or image comparison path. |
| `primitive_restart.NORMAL` | The enabled restart boundary is ignored or applied at the wrong primitive boundary. |
| `primitive_restart.NONE` | A restart boundary is introduced even though this enabled-restart test supplies no restart index. |
| `primitive_restart.ALL` | Restart handling is incorrect when restart indices are inserted throughout the generated primitive stream. |
| `primitive_restart.DIVIDE` | The split draw path or restart boundary produces different geometry from the expected divided primitives. |
| `primitive_restart.SECOND_PASS` | Restart handling or state retained across the second draw pass is incorrect. |
| `restart_mix` | Primitive-restart state leaks into or is lost across indexed/non-indexed draws, topology changes, or a large non-indexed draw. |
| `restart_disabled_*` | A disabled restart state is treated as enabled, or the Amber setup/expected result is wrong. |

### Cause Analysis

#### Topology, index, or ordinary assembly failure

**Possible failure symptoms:** The reference and readback images differ, with missing, extra, or incorrectly connected colored primitives.

**Possible implementation causes:** The test changes `VkPrimitiveTopology`, index width, and indexed input while keeping the shaders pass-through. A failure can come from vertex fetch, topology selection, primitive assembly, rasterization, or the image comparison/readback path; the comparison alone does not localize the fault.

#### Restart boundary or restart-disabled failure

**Possible failure symptoms:** Geometry before or after a restart boundary is absent, joined to the wrong primitive, or appears in an enabled-restart `NONE` case that supplies no restart index. The Amber disabled-restart cases can also fail if they treat the reserved value as a boundary.

**Possible implementation causes:** Vulkan requires the restart comparison before `vertexOffset` is added and restarts assembly after discarding an incomplete primitive. Errors can therefore arise from restart-value comparison, index-width handling, list-restart feature/state handling, or primitive assembly after the boundary. [Vulkan indexed drawing](../../../../vulkan-docs/src/chapters/drawing.adoc#L1255-L1268)

#### Mixed-draw state failure

**Possible failure symptoms:** A `restart_mix` quadrant has the wrong color, including missing non-indexed geometry, unintended bottom-right coverage, or missing later indexed geometry.

**Possible implementation causes:** The test leaves restart enabled while changing draw form and may change primitive topology dynamically. It can expose incorrect command-state tracking between `cmdDrawIndexed` and `cmdDraw`, failure to apply the dynamic topology, or an implementation that mishandles the large non-indexed vertex count. Source-level investigation is needed to distinguish those causes from a color copyback failure.

## Case Pruning

### Requirement-based pruning

`index_type_uint8` requires `VK_KHR_index_type_uint8` or `VK_EXT_index_type_uint8`. Adjacency and patch topologies require geometry and tessellation shader features, respectively. On implementations that expose `VK_KHR_portability_subset`, triangle-fan cases also require the `triangleFans` feature. List and patch restart cases require `VK_EXT_primitive_topology_list_restart` and its matching feature bits; patch restart additionally needs `primitiveTopologyPatchListRestart`. `restart_mix` requires `VK_EXT_extended_dynamic_state` when topology is dynamic and requires `VK_EXT_primitive_topology_list_restart` for triangle-list variants. [`support checks`](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L242-L282) [`restart support`](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L758-L784) [`mix support`](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L1799-L1809)

### Design-based pruning

`POINT_LIST` has no `ALL` restart case. `DIVIDE` and `SECOND_PASS` use only list topologies with fixed vertices per primitive. `largeNonIndexedDraw` is excluded unless `triangleList` is true. `primitive_restart` and `restart_mix` do not exist in Vulkan SC because the registration is inside `#ifndef CTS_USES_VULKANSC`; Amber disabled-restart leaves are intentionally monolithic-only.

## Key Takeaways

- The family separates basic assembly coverage from restart-boundary and mixed-draw state coverage.
- The three index-type branches test the same topology behavior while changing encoded index width and restart value.
- `restart_mix` checks command-state lifetime through an observable four-quadrant image, rather than only checking an isolated indexed draw.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Common support and shader setup | [`InputAssemblyTest::checkSupport()` and `initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L242-L320) | Defines support gates and pass-through shader setup. |
| Basic topology registration | [`createPrimitiveTopologyTests()`](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L1703-L1731) | Registers the topology leaves for each index type. |
| Restart modes and requirements | [`PrimitiveRestartTest`](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L702-L784) | Defines restart index placement and list-restart gates. |
| Restart and mixed-draw registration | [`createPrimitiveRestartTests()`](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L2186-L2336) | Registers ordinary restart, Amber, and `restart_mix` leaves. |
| Ordinary image comparison | [`InputAssemblyInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L1300-L1649) | Renders and compares the reference image. |
| Mixed-draw execution | [`PrimitiveRestartMixTest::iterate()`](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L1834-L2184) | Records draw order and exact quadrant comparison. |
