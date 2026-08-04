## Overview

**Core question:** Does `VK_EXT_depth_range_unrestricted` produce the expected depth and color results when depth clear, viewport, or depth-bounds values lie outside `[0, 1]`?

- This page describes the `pipeline.<construction type>.depth_range_unrestricted` test family implemented by [`vktPipelineDepthRangeUnrestrictedTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineDepthRangeUnrestrictedTests.cpp#L1).
- The family varies where an unrestricted value enters fixed-function depth processing: the depth clear value, viewport minimum and maximum depth, depth bounds, or clipping behavior with depth clamping disabled.
- The host renders a reference image from the selected parameters and compares it with color and depth readback, so a failure is an observable mismatch rather than a shader-computation result.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- **Unrestricted depth values.** `VK_EXT_depth_range_unrestricted` permits depth-range-related values outside the ordinary `[0, 1]` interval in the states covered by this family. The cases use negative values and values greater than one for clear depth, viewport depth, and depth bounds.
- **Depth comparison and depth bounds.** A fragment can update attachments only after its depth comparison passes. When depth-bounds testing is enabled, the stored depth value must also lie within the selected bounds. `depthbounds` changes both the viewport range and bounds range, then observes the two stages of depth-buffer use.
- **Depth clamping.** With depth clamping enabled, out-of-range depth can be clamped instead of clipped. `depthclampingdisabled` turns that feature off and varies the vertex `w` coordinate to exercise clipping with unrestricted viewport depth values.

## Registration Hierarchy

```text
pipeline.monolithic.depth_range_unrestricted
├── clear_value
├── viewport
├── depthbounds
└── depthclampingdisabled
```

[`createDepthRangeUnrestrictedTests()`](../../../modules/vulkan/pipeline/vktPipelineDepthRangeUnrestrictedTests.cpp#L1375-L1530) creates this test family for the supplied `PipelineConstructionType`. The tree shows `pipeline.monolithic.depth_range_unrestricted` as a representative registration root. Its four direct children are intermediate nodes within that family; each intermediate node creates test-case leaves from its parameter loops.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Intermediate node | `clear_value`, `viewport`, `depthbounds`, `depthclampingdisabled` | Selects where the unrestricted range or disabled-clamping behavior is applied within the test family. | [`createDepthRangeUnrestrictedTests()`](../../../modules/vulkan/pipeline/vktPipelineDepthRangeUnrestrictedTests.cpp#L1397-L1530) |
| Depth format | `VK_FORMAT_D32_SFLOAT`, `VK_FORMAT_D24_UNORM_S8_UINT`, `VK_FORMAT_D16_UNORM` | Changes the depth attachment representation and its supported behavior. | [format array](../../../modules/vulkan/pipeline/vktPipelineDepthRangeUnrestrictedTests.cpp#L1379-L1383) |
| Depth compare operation | `VK_COMPARE_OP_GREATER`, `VK_COMPARE_OP_GREATER_OR_EQUAL`, `VK_COMPARE_OP_LESS`, `VK_COMPARE_OP_LESS_OR_EQUAL` | Controls whether a point passes the depth test in `viewport`, `depthbounds`, and `depthclampingdisabled`. | [compare-op array](../../../modules/vulkan/pipeline/vktPipelineDepthRangeUnrestrictedTests.cpp#L1385-L1390) |
| Clear depth | `2.0`, `-3.0`, `6.0`, `-7.0` | Supplies an out-of-range initial depth value. | [clear-value array](../../../modules/vulkan/pipeline/vktPipelineDepthRangeUnrestrictedTests.cpp#L1392-L1395) |
| Viewport depth range | `-2.0` to `2.0`, `-6.0` to `6.0`, `-12.0` to `12.0` | Selects symmetric unrestricted viewport minimum and maximum depth. | [viewport loop](../../../modules/vulkan/pipeline/vktPipelineDepthRangeUnrestrictedTests.cpp#L1448-L1455) |
| Viewport state mode | static; dynamic | Chooses whether viewport depth range is baked into pipeline state or set dynamically. | [viewport registration](../../../modules/vulkan/pipeline/vktPipelineDepthRangeUnrestrictedTests.cpp#L1450-L1455) |
| Depth-bounds range | `-2.0` to `2.0`, `-4.0` to `4.0`, `-8.0` to `8.0` | Selects symmetric unrestricted minimum and maximum bounds. | [depth-bounds loop](../../../modules/vulkan/pipeline/vktPipelineDepthRangeUnrestrictedTests.cpp#L1488-L1498) |
| Depth-bounds state mode | static; dynamic; dynamic viewport plus dynamic depth bounds | Separates static state from one or both dynamic commands. | [depth-bounds registration](../../../modules/vulkan/pipeline/vktPipelineDepthRangeUnrestrictedTests.cpp#L1493-L1498) |
| Vertex `w` coordinate | `2.0`, `6.0`, `12.0` | Varies clipping behavior when depth clamping is disabled. | [value arrays](../../../modules/vulkan/pipeline/vktPipelineDepthRangeUnrestrictedTests.cpp#L1392-L1395) and [disabled-clamping registration](../../../modules/vulkan/pipeline/vktPipelineDepthRangeUnrestrictedTests.cpp#L1508-L1530) |

## Behavior Parameters

The primary behavioral axis is the registered **intermediate node** below the `depth_range_unrestricted` test family. Each intermediate node changes the fixed-function state that accepts or responds to unrestricted depth values.

### `clear_value`: Out-of-range depth clears

These cases clear each selected depth format to `2.0`, `-3.0`, `6.0`, or `-7.0`. They use `VK_COMPARE_OP_LESS_OR_EQUAL`, static viewport/depth-bounds state, and disabled depth clamping. The reference path accounts for the fact that non-floating depth formats store the clear value clamped to `[0, 1]`.

### `viewport`: Unrestricted viewport depth range

These cases enable depth clamping, vary the selected depth format, comparison operation, and out-of-range clear value, and set the viewport range to one of three symmetric negative/positive intervals. Every range is tested as static pipeline state and as dynamic state.

### `depthbounds`: Unrestricted depth bounds

These cases enable both depth clamping and depth-bounds testing. They combine the same format, comparison, clear-value, and viewport choices with one of three symmetric depth-bounds ranges. The registration covers static state, dynamically set depth bounds, and dynamically set viewport plus depth bounds.

### `depthclampingdisabled`: Clipping without depth clamping

These cases disable depth clamping, vary the format, comparison operation, clear value, viewport range, and vertex `w` coordinate, and retain static viewport/depth-bounds state. They check that clipping and comparison remain correct when the viewport range is unrestricted but primitives are not depth-clamped.

## Shader Analysis

The shaders provide point position and color; they do not calculate the depth behavior being tested. [`DepthRangeUnrestrictedTest::initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineDepthRangeUnrestrictedTests.cpp#L1326-L1347) emits a vertex shader that assigns `gl_Position`, sets `gl_PointSize`, and forwards vertex color, plus a fragment shader that writes the forwarded color. Pipeline depth state, not shader arithmetic, determines the observed result, so no representative shader walkthrough or SPIR-V artifact is needed.

## Runtime Execution and Result Checking

- `DepthRangeUnrestrictedTest::checkSupport()` checks the selected pipeline construction type and whether the selected depth format supports `VK_FORMAT_FEATURE_DEPTH_STENCIL_ATTACHMENT_BIT`. It additionally requires `depthClamp` when depth clamping is enabled and `depthBounds` when depth-bounds testing is enabled. [`checkSupport()`](../../../modules/vulkan/pipeline/vktPipelineDepthRangeUnrestrictedTests.cpp#L1356-L1372) contains these gates.
- The ordinary instance owns color and depth images, views, a vertex buffer, render pass, command buffer, graphics pipeline, and shader modules. [`DepthRangeUnrestrictedTestInstance`](../../../modules/vulkan/pipeline/vktPipelineDepthRangeUnrestrictedTests.cpp#L413-L452) declares that setup.
- `iterate()` records the command buffer, submits it to the universal queue, waits, and invokes result verification. [`DepthRangeUnrestrictedTestInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineDepthRangeUnrestrictedTests.cpp#L838-L848) is the execution boundary.
- `verifyTestResult()` creates a `32` by `32` host reference image, clears it, evaluates the selected vertices and depth state, reads the device results, and reports either a color/depth mismatch or success. For non-floating depth formats it first clamps the reference clear depth to `[0, 1]`. [`DepthRangeUnrestrictedTestInstance::verifyTestResult()`](../../../modules/vulkan/pipeline/vktPipelineDepthRangeUnrestrictedTests.cpp#L850-L1025) implements the ordinary validation.
- `DepthBoundsRangeUnrestrictedTestInstance` has a second render pass and pipeline that preserve the first draw's depth contents. It renders and verifies the first scene, then runs the second draw because depth-bounds testing observes the depth-buffer data left by the first draw. [`DepthBoundsRangeUnrestrictedTestInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineDepthRangeUnrestrictedTests.cpp#L1094-L1110) begins this two-stage sequence.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `clear_value` | An out-of-range depth clear value is stored, clamped, or compared incorrectly for the selected depth format. |
| `viewport` | Static or dynamic viewport minimum/maximum depth outside `[0, 1]` is handled incorrectly, or the selected depth comparison is wrong. |
| `depthbounds` | Unrestricted depth-bounds values, dynamic depth-bounds state, retained depth data between draws, or depth comparison is handled incorrectly. |
| `depthclampingdisabled` | Primitives outside the clip range are clipped or compared incorrectly when depth clamping is disabled. |

### Cause Analysis

#### Out-of-range clear-value handling

**Possible failure symptoms:** A `clear_value` case reports a color or depth-buffer mismatch for one of the selected clear depths, possibly only for a normalized depth format or only for `D32_SFLOAT`.

**Possible implementation causes:** The implementation may store an unrestricted clear value incorrectly, clamp a floating format when it should retain the value, fail to clamp a non-floating format as the reference expects, or use the wrong cleared value during depth comparison.

#### Viewport depth-range state handling

**Possible failure symptoms:** A `viewport` case fails only for static or dynamic state, one range magnitude, or selected comparison operations.

**Possible implementation causes:** The implementation may clamp viewport minimum or maximum depth to the ordinary interval, reverse or otherwise apply the range incorrectly, or fail to make a dynamic viewport command override the pipeline state.

#### Depth-bounds state or retained-depth handling

**Possible failure symptoms:** A `depthbounds` case differs between its first and second draw, or only dynamic depth-bounds and combined dynamic-state variants fail.

**Possible implementation causes:** The implementation may apply unrestricted bounds incorrectly, use stale static bounds after a dynamic command, fail to retain the first draw's depth attachment contents, or evaluate depth comparison and depth-bounds testing in the wrong way.

#### Disabled-clamping clipping behavior

**Possible failure symptoms:** A `depthclampingdisabled` case fails only for a particular vertex `w` coordinate or viewport range.

**Possible implementation causes:** The implementation may clamp when depth clamping is disabled, clip an eligible point incorrectly, or combine clip-space `z` and `w` tests with the unrestricted viewport range incorrectly.

## Case Pruning

### Requirement-based pruning

- The selected depth format must support `VK_FORMAT_FEATURE_DEPTH_STENCIL_ATTACHMENT_BIT`.
- The selected pipeline construction type must pass `checkPipelineConstructionRequirements()`.
- `viewport` and `depthbounds` require the core `depthClamp` feature because those families enable depth clamping.
- `depthbounds` also requires the core `depthBounds` feature.
- The source excludes this family from Vulkan SC builds through `CTS_USES_VULKANSC` guards.

### Design-based pruning

- `clear_value` isolates clear behavior with `VK_COMPARE_OP_LESS_OR_EQUAL`, static viewport/depth-bounds state, and `w = 1.0` rather than multiplying it by every other state axis.
- `viewport` omits depth-bounds testing so it can isolate unrestricted viewport state.
- `depthbounds` uses a specialized two-draw instance because the second check depends on depth data written by the first draw.
- `depthclampingdisabled` keeps viewport/depth-bounds state static and disables depth-bounds testing, isolating clipping behavior as `w` varies.

## Key Takeaways

- The four registered intermediate nodes isolate unrestricted clear values, viewport depth ranges, depth bounds, and disabled-clamping behavior.
- The generated matrix combines three depth formats, four comparison operations where applicable, four clear values, three viewport magnitudes, three depth-bounds magnitudes, static/dynamic modes, and selected `w` values.
- The test uses pass-through shaders and point vertices; fixed-function depth processing is the implementation under test.
- Non-floating depth formats use a clamped `[0, 1]` clear value in the host reference, while floating formats retain the selected clear value.
- `depthbounds` requires two draw-and-verify stages because the second depth-bounds evaluation depends on depth-buffer contents from the first draw.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Parameter structure and generated names | [`DepthRangeUnrestrictedParam`](../../../modules/vulkan/pipeline/vktPipelineDepthRangeUnrestrictedTests.cpp#L70-L84) and [`generateTestName()`](../../../modules/vulkan/pipeline/vktPipelineDepthRangeUnrestrictedTests.cpp#L97-L120) | Defines the registered state fields and their case-name encoding. |
| Main instance resources | [`DepthRangeUnrestrictedTestInstance`](../../../modules/vulkan/pipeline/vktPipelineDepthRangeUnrestrictedTests.cpp#L413-L452) | Declares attachments, buffer, pipeline, command, and shader resources. |
| Ordinary execution | [`DepthRangeUnrestrictedTestInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineDepthRangeUnrestrictedTests.cpp#L838-L848) | Records, submits, waits, and starts validation. |
| Ordinary reference validation | [`DepthRangeUnrestrictedTestInstance::verifyTestResult()`](../../../modules/vulkan/pipeline/vktPipelineDepthRangeUnrestrictedTests.cpp#L850-L1025) | Builds the expected image and checks color/depth results. |
| Two-pass depth-bounds instance | [`DepthBoundsRangeUnrestrictedTestInstance`](../../../modules/vulkan/pipeline/vktPipelineDepthRangeUnrestrictedTests.cpp#L1028-L1110) | Preserves first-draw depth data and validates the two-stage path. |
| Programs and support checks | [`DepthRangeUnrestrictedTest`](../../../modules/vulkan/pipeline/vktPipelineDepthRangeUnrestrictedTests.cpp#L1306-L1372) | Emits shaders, selects the instance type, and enforces support requirements. |
| Family registration | [`createDepthRangeUnrestrictedTests()`](../../../modules/vulkan/pipeline/vktPipelineDepthRangeUnrestrictedTests.cpp#L1375-L1530) | Registers the four families and their parameter loops. |
