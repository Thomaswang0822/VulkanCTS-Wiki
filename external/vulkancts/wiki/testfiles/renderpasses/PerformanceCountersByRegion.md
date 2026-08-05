## Overview

**Core question:** When a render pass instance captures per-region performance counters via `VK_ARM_performance_counters_by_region`, does the implementation write counter values into the correct tile regions of the capture buffer, and do those values match the expected value for each region?

- This page covers the `performance_counters_by_region` test family in [`vktRenderPassPerformanceCountersByRegionTests.cpp`](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp). The family is created by [`createRenderPassPerformanceCountersByRegionTests()`](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1610-L1614) and attached under each rendering variant root (`renderpass1`, `renderpass2`, `dynamic_rendering`) at the rendering-type level.
- It registers a small matrix of test case leaves that combine one color format (`R8G8B8A8_UNORM`) with one or two attachment layers, each capturing a single counter named "Fragment warps".
- The core idea is to render a full-screen blue quad into a color attachment whose render pass instance has per-region performance counters enabled, then read back the counter buffer and check that each tile region's counter value matches the expected value for a complete region (or falls within `[1, expectedMax]` for a partial region), where the expected value scales with the layer index.
- The test also writes per-pixel device timestamps into an SSBO via `clockRealtimeEXT()` and checks that timestamps from different logical devices do not overlap, as a side-channel consistency check.

## Background Knowledge

- **Per-region performance counters.** `VK_ARM_performance_counters_by_region` lets an application request that the implementation capture performance counters per tile region during a render pass instance. The framebuffer is divided into regions of a fixed size reported by `VkPhysicalDevicePerformanceCounterPropertiesPerRegionARM`, and the implementation writes the requested counter values into a host-visible buffer laid out region-by-region ([VK_ARM_performance_counters_by_region.adoc](../../../../vulkan-docs/src/appendices/VK_ARM_performance_counters_by_region.adoc)).
- **Region layout.** The capture buffer is organized as a 2D grid of regions, with each region holding `maxPerRegionPerformanceCounters` uint32 values padded to `regionAlignment`. Rows are padded to `rowStrideAlignment`. This layout is reconstructed during verification to locate each region's counter values.
- **Complete vs partial regions.** The last row or column of regions may be partial if the framebuffer dimensions are not a multiple of the region size. The expected counter range differs for partial regions because they cover fewer pixels and therefore trigger fewer fragment invocations.

## Registration Hierarchy

```text
renderpasses.renderpass1.performance_counters_by_region
└── r8g8b8a8_unorm
```

The tree shows the `renderpass1` representative root. The same family is registered under `renderpasses.renderpass2.performance_counters_by_region` and under each `renderpasses.dynamic_rendering.*.performance_counters_by_region` root. Under each root, the single `r8g8b8a8_unorm` format node holds two leaves: `layers_1` and `layers_2` ([registration loop](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1581-L1606)). The family is non-SC and is guarded by `#ifndef CTS_USES_VULKANSC`.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Color format | `R8G8B8A8_UNORM` | The only format the test uses. It is a common UNORM color format sufficient to produce a full-screen blue quad. | [formats array](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1575-L1577) |
| Layer count | `1`, `2` | The number of attachment layers. Two layers add a geometry shader that routes draws to a second layer via `gl_Layer`, doubling the expected fragment work for the "Fragment warps" counter. | [layer loop](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1598-L1607) |
| Counter | "Fragment warps", regionMin=0, regionMax=0, fragment=256 | The single counter captured per region. Because both `regionMin` and `regionMax` are `0` and are offset by the same `fragment` value, the expected counter for a complete region is an exact value, not a range. | [counter config](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1587) |

## Behavior Parameters

The primary behavioral axis is the layer count. For each layer index, the host issues a separate draw of `3 * (layerIdx + 1)` vertices ([draw commands](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L951-L966)). Both the expected minimum and maximum for a complete region are set to `fragment * (layerIdx + 1)`, so complete regions are checked against an exact value — `256` for layer 0 and `512` for layer 1. Partial regions use a minimum of `1` and the same maximum.

The counter is fixed to "Fragment warps" across all leaves, so the layer count is the only value that changes the expected counter value.

### layers_1: single-layer counter capture

The render pass instance has one color attachment layer. The fragment shader runs once per covered pixel, writes blue to the color attachment, and writes a device timestamp to the SSBO. Because both `regionMin` and `regionMax` are `0` and are offset by the same `fragment` value, the expected "Fragment warps" counter per complete region is an exact value of `256` ([counter range computation](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1248-L1262)).

### layers_2: two-layer counter capture with geometry shader routing

A geometry shader sets `gl_Layer` from the push constant to route the triangle to a chosen layer ([geometry shader](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1386-L1407)). The host issues a separate draw per layer index with `3 * (layerIdx + 1)` vertices ([draw commands](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L951-L966)), so layer 1 produces twice the fragment work of layer 0. The expected "Fragment warps" counter per complete region is an exact value of `512`, because the `fragment` value (256) is scaled by `layerIdx + 1`.

## Shader Analysis

The shaders are the instrument that produces fragment work for the counter to measure. They are not the behavior under test. The behavior is the per-region counter capture and buffer layout, which is fixed-function. No representative shader walkthrough is included for that reason.

The shader roles are:

- The vertex shader emits a full-screen triangle from `gl_VertexIndex` ([vertex shader](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1336-L1344)).
- The fragment shader writes blue `(0, 0, 1, 1)` to the color output and writes `clockRealtimeEXT()` into the SSBO at the fragment's linear index, so the host can check per-pixel device timestamps for cross-device overlap ([fragment shader](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1352-L1375)).
- The geometry shader (only for `layers_2`) sets `gl_Layer` from the push constant to route the triangle to the layer chosen by the host draw.

## Runtime Execution and Result Checking

Each test case creates three `PerformanceCountersByRegionContainer` instances (one per logical device used for the timestamp overlap check), sets up a color attachment in the selected format and layer count, records a render pass instance with per-region counters enabled, renders the full-screen quad, and reads back the counter buffer and color attachment.

Counter verification walks the region grid and computes the expected value for each region based on whether it is complete or partial and on the layer index ([counter verification](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1223-L1275)). For complete regions the minimum and maximum are both `fragment * (layerIdx + 1)`, so the check is exact. Partial regions use a minimum of at least `1` and the same scaled maximum.

Attachment verification checks that every pixel of every layer is blue `(0, 0, 1, 1)` within a `0.01` tolerance ([attachment check](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1313-L1344)).

Timestamp verification gathers per-region start and end timestamps from the SSBO and checks that timestamps from different logical devices do not overlap ([timestamp check](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1445-L1478)). All failures are collected in a `tcu::ResultCollector` and aggregated into the final pass/fail.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `layers_1` leaves | The single-layer counter value per region did not match the expected value `256` for a complete region (or fell outside `[1, 256]` for a partial region), meaning the implementation miscounted fragment warps or wrote the counter to the wrong region. |
| `layers_2` leaves | The two-layer counter value per region did not match the expected value `512` for a complete region (or fell outside `[1, 512]` for a partial region), meaning the per-layer draw routing or scaling was wrong. |
| Attachment check (any leaf) | The color attachment is not blue within tolerance, meaning the render did not cover the framebuffer or the color write was corrupted independent of the counter path. |
| Timestamp overlap check (any leaf) | Device timestamps from different logical devices overlapped, violating the extension's security model for concurrent workloads. |
| Any leaf (common cause) | Counter buffer layout, region stride, alignment, or mapping was wrong, so counter values were read from the wrong offsets. |

### Cause Analysis

#### Counter value outside expected range per region

**Possible failure symptoms:** A region's "Fragment warps" counter differs from the expected exact value for a complete region (256 for layer 0, 512 for layer 1), or falls outside `[1, expectedMax]` for a partial region. The failure is reported per layer via the result collector.

**Possible implementation causes:** The extension requires the implementation to divide the framebuffer into regions of the reported size and write each region's counter values into the capture buffer at the correct stride and alignment. A driver that uses the wrong region size, skips partial regions, or does not scale the counter by the actual fragment work can produce an out-of-range value. The layer-count scaling isolates whether the counter reflects the total fragment work across all layers or only one layer.

#### Counter buffer layout or region mapping wrong

**Possible failure symptoms:** Counter values appear shifted, duplicated, or zeroed across regions in a pattern that does not track framebuffer location.

**Possible implementation causes:** The capture buffer uses `regionAlignment` per region and `rowStrideAlignment` per row, both reported by the implementation. A driver that pads differently from what it reports, or that maps regions in a different order than row-major, produces a shifted layout. Source-level investigation is needed to distinguish a layout bug from a counter-value bug, since both manifest as out-of-range reads.

## Case Pruning

### Requirement-based pruning

- Every leaf requires `VK_ARM_performance_counters_by_region` with the `performanceCountersByRegion` feature enabled ([checkSupport](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1537-L1569)).
- `VK_KHR_buffer_device_address`, `VK_EXT_separate_stencil_usage`, and `VK_KHR_get_physical_device_properties2` are always required ([checkSupport](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1535-L1538)).
- `VK_KHR_shader_clock` with the `shaderDeviceClock` feature is required for the timestamp SSBO writes ([checkSupport](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1555-L1558)).
- The `renderpass2` root requires `VK_KHR_create_renderpass2`; the `dynamic_rendering` root requires `VK_KHR_dynamic_rendering` ([checkSupport](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1540-L1544)).
- The graphics pipeline library variant requires `VK_KHR_pipeline_library` or `VK_EXT_graphics_pipeline_library` with the `graphicsPipelineLibrary` feature ([checkSupport](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1546-L1552)).

### Design-based pruning

- Only `R8G8B8A8_UNORM` is tested because the counter capture is independent of the color format; one common UNORM format is sufficient to produce fragment work.
- Layer counts are limited to 1 and 2 because the layer count's only role is to scale the expected counter range; two values confirm the scaling.
- The counter is fixed to "Fragment warps" because it is a representative fragment-work counter available on the target implementation.

## Key Takeaways

- The test verifies that `VK_ARM_performance_counters_by_region` writes per-region counter values into the capture buffer at the correct layout and matching the expected value for each region.
- The layer count is the behavioral axis: two layers double the expected counter value via per-layer draws with increasing vertex counts.
- Complete and partial regions have different expected minima, because partial regions cover fewer pixels.
- A side-channel timestamp check verifies that device timestamps from different logical devices do not overlap, supporting the extension's concurrent-workload security model.
- See [Failure Meaning](#failure-meaning) for how counter range, buffer layout, and timestamp overlap map to distinct failure symptoms.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test family factory | [`createRenderPassPerformanceCountersByRegionTests`](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1610-L1614) | Creates the group and dispatches to `initTests`. |
| Registration loop | [`initTests`](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1581-L1606) | Generates the `r8g8b8a8_unorm.layers_{1,2}` leaves. |
| Counter verification | [per-region range check](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1223-L1275) | Walks the region grid and checks each counter value against the expected min/max. |
| Attachment verification | [color check](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1313-L1344) | Checks every pixel is blue within `0.01` tolerance. |
| Timestamp verification | [timestamp overlap check](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1445-L1478) | Gathers per-region timestamps and checks cross-device non-overlap. |
| Shader generation | [`Programs::init`](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1334-L1410) | Emits the vertex, fragment (with `clockRealtimeEXT`), and geometry (for `layers_2`) shaders. |
| Support checks | [`checkSupport`](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1535-L1569) | Requires the extension, its feature, buffer device address, shader clock, and rendering-type extensions. |
| Vulkan spec: per-region counters | [VK_ARM_performance_counters_by_region.adoc](../../../../vulkan-docs/src/appendices/VK_ARM_performance_counters_by_region.adoc) | Defines per-region performance counter capture, region layout, and the security model. |
