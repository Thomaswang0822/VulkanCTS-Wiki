# vktDynamicStateVPTests.cpp

## Overview

[`vktDynamicStateVPTests.cpp`](../../../modules/vulkan/dynamic_state/vktDynamicStateVPTests.cpp#L1) implements the [`vp_state`](../../../modules/vulkan/dynamic_state/vktDynamicStateVPTests.cpp#L461) subgroup of the dynamic_state category. It tests dynamic viewport and scissor state, including single viewport, single scissor, and multi-viewport array configurations with both traditional vertex-shader and mesh-shader pipelines.

## Role

Implementation file.

## Source Code

- Primary source: [`vktDynamicStateVPTests.cpp`](../../../modules/vulkan/dynamic_state/vktDynamicStateVPTests.cpp#L1)
- Shared base: [`DynamicStateBaseClass`](../../../modules/vulkan/dynamic_state/vktDynamicStateBaseClass.hpp#L43)
- Test case utilities: [`vktDynamicStateTestCaseUtil.hpp`](../../../modules/vulkan/dynamic_state/vktDynamicStateTestCaseUtil.hpp#L1)

## Registration Hierarchy

```text
dynamic_state.monolithic.vp_state
├── viewport
├── scissor
├── viewport_array
├── viewport_mesh          (non-VulkanSC only)
├── scissor_mesh           (non-VulkanSC only)
└── viewport_array_mesh    (non-VulkanSC only)
```

## Test Families

### viewport — Viewport dynamic state

[`viewport`](../../../modules/vulkan/dynamic_state/vktDynamicStateVPTests.cpp#L502) and [`viewport_mesh`](../../../modules/vulkan/dynamic_state/vktDynamicStateVPTests.cpp#L502) use [`ViewportParamTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateVPTests.cpp#L138). A double-sized viewport (`2*WIDTH x 2*HEIGHT`) is set dynamically via `vkCmdSetViewport`, with a full-size scissor. The test verifies that the oversized viewport clips correctly to the scissor/render area, producing a green quad in the top-right quadrant.

### scissor — Scissor dynamic state

[`scissor`](../../../modules/vulkan/dynamic_state/vktDynamicStateVPTests.cpp#L504) and [`scissor_mesh`](../../../modules/vulkan/dynamic_state/vktDynamicStateVPTests.cpp#L504) use [`ScissorParamTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateVPTests.cpp#L189). A normal viewport is set with a half-size scissor (`WIDTH/2 x HEIGHT/2`) via `vkCmdSetScissor`. The test verifies that the smaller scissor clips the rendering to the bottom-left quadrant.

### viewport_array — Viewport array dynamic state

[`viewport_array`](../../../modules/vulkan/dynamic_state/vktDynamicStateVPTests.cpp#L518) and [`viewport_array_mesh`](../../../modules/vulkan/dynamic_state/vktDynamicStateVPTests.cpp#L518) use [`ViewportArrayTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateVPTests.cpp#L239). Uses [`kNumViewports = 4`](../../../modules/vulkan/dynamic_state/vktDynamicStateVPTests.cpp#L245) viewports in a 2x2 grid with quarter-sized scissors. A geometry shader (non-mesh) or mesh shader assigns `gl_ViewportIndex`. The test verifies multi-viewport rendering produces a centered green square.

### viewport_mesh — Viewport dynamic state (mesh shader)

Mesh shader variant of `viewport`. See `viewport` above for test logic. Excluded on Vulkan SC builds.

### scissor_mesh — Scissor dynamic state (mesh shader)

Mesh shader variant of `scissor`. See `scissor` above for test logic. Excluded on Vulkan SC builds.

### viewport_array_mesh — Viewport array dynamic state (mesh shader)

Mesh shader variant of `viewport_array`. See `viewport_array` above for test logic. Excluded on Vulkan SC builds.

## Parameter Dimensions

| Parameter | Observed values / source |
|---|---|
| Pipeline construction type | Passed from parent group; controls monolithic vs. pipeline library vs. shader object |
| Shader type | Vertex+Fragment (non-mesh) vs. Mesh+Fragment ([`init()` loop at L479](../../../modules/vulkan/dynamic_state/vktDynamicStateVPTests.cpp#L479)) |
| Viewport configuration | Single oversized viewport ([`ViewportParamTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateVPTests.cpp#L151)), normal viewport ([`ScissorParamTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateVPTests.cpp#L202)), 4-viewport array ([`ViewportArrayTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateVPTests.cpp#L338)) |
| Scissor configuration | Full-size ([`ViewportParamTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateVPTests.cpp#L151)), half-size ([`ScissorParamTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateVPTests.cpp#L202)), quarter-size per viewport ([`ViewportArrayTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateVPTests.cpp#L338)) |
| Render dimensions | WIDTH=128, HEIGHT=128 (from base class) |

## Support / Feature Requirements

| Test | Requirement | Check Function |
|---|---|---|
| viewport, scissor | None | [`checkNothing`](../../../modules/vulkan/dynamic_state/vktDynamicStateVPTests.cpp#L453) |
| viewport_array | geometry shader + multi-viewport core features | [`checkGeometryAndMultiViewportSupport`](../../../modules/vulkan/dynamic_state/vktDynamicStateVPTests.cpp#L436) |
| viewport_mesh, scissor_mesh | `VK_EXT_mesh_shader` | [`checkMeshShaderSupport`](../../../modules/vulkan/dynamic_state/vktDynamicStateVPTests.cpp#L442) |
| viewport_array_mesh | multi-viewport core feature + `VK_EXT_mesh_shader` | [`checkMeshAndMultiViewportSupport`](../../../modules/vulkan/dynamic_state/vktDynamicStateVPTests.cpp#L447) |

## Verification Methods

All test instances use **fuzzy image comparison** via [`tcu::fuzzyCompare()`](../../../modules/vulkan/dynamic_state/vktDynamicStateVPTests.cpp#L127) with a threshold of `0.05f`:

1. Render the scene with dynamic viewport/scissor state set via `setDynamicStates()`.
2. Build a software reference frame via `buildReferenceFrame()`.
3. Read back the rendered image from the color attachment.
4. Compare rendered vs. reference using `tcu::fuzzyCompare()`.

The reference frame for each test encodes the expected clipped region:
- **ViewportParamTestInstance**: Green in the top-right quadrant (NDC [0,1]x[0,1]).
- **ScissorParamTestInstance**: Green in the bottom-left quadrant (NDC [-0.5,0]x[-0.5,0]).
- **ViewportArrayTestInstance**: Green in the center (NDC [-0.5,0.5]x[-0.5,0.5]).

## Test Principles Observed

- **Dynamic viewport overrides static state**: Tests set viewport/scissor dynamically and verify the rendering matches the expected clipped output.
- **Mesh shader parity**: The same test logic is applied with both vertex-shader and mesh-shader pipelines to ensure dynamic state works identically.
- **Multi-viewport coverage**: The viewport_array test exercises `vkCmdSetViewport` with multiple viewports and geometry/mesh shader viewport index selection.

## Notes / Uncertainties

- Mesh shader variants are excluded on Vulkan SC builds via `#ifndef CTS_USES_VULKANSC` guards.
- The `viewport_array` test uses a geometry shader for viewport index selection in the non-mesh variant, which requires both geometry shader and multi-viewport features.
