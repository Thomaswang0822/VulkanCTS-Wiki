# vktDynamicStateGeneralTests.cpp

## Overview

[`vktDynamicStateGeneralTests.cpp`](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L1) implements the [`general_state`](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L917) subgroup of the dynamic_state category. It tests general dynamic state behaviors including state switching, bind order, state persistence across pipeline binds, static stencil mask zero, and double static bind scenarios.

## Role

Implementation file.

## Source Code

- Primary source: [`vktDynamicStateGeneralTests.cpp`](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L1)
- Shared base: [`DynamicStateBaseClass`](../../../modules/vulkan/dynamic_state/vktDynamicStateBaseClass.hpp#L43)
- Test case utilities: [`vktDynamicStateTestCaseUtil.hpp`](../../../modules/vulkan/dynamic_state/vktDynamicStateTestCaseUtil.hpp#L1)

## Registration Hierarchy

```text
dynamic_state.monolithic.general_state
├── state_switch
├── state_switch_mesh              (non-VulkanSC only)
├── bind_order
├── bind_order_mesh                (non-VulkanSC only)
├── state_persistence             (non-mesh only)
├── static_stencil_mask_zero
└── double_static_bind            (non-shader-object only)
```

## Test Families

### state_switch — State switch

[`state_switch`](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L958) and [`state_switch_mesh`](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L958) use [`StateSwitchTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L60). Sets dynamic viewport, rasterization, blend, and depth/stencil states, then performs two draws with different scissors. Verifies that the dynamic scissor state change between draws produces the expected two-quadrant pattern.

### state_switch_mesh — State switch (mesh shader)

Mesh shader variant of `state_switch`. See `state_switch` above for test logic. Excluded on Vulkan SC builds.

### bind_order — Bind order

[`bind_order`](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L961) and [`bind_order_mesh`](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L961) use [`BindOrderTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L174). Same as state_switch but rebinds dynamic states in a different order (blend, rasterization, depth/stencil) before drawing. Verifies that the order of setting dynamic states does not affect the final rendering result.

### bind_order_mesh — Bind order (mesh shader)

Mesh shader variant of `bind_order`. See `bind_order` above for test logic. Excluded on Vulkan SC builds.

### state_persistence — State persistence

[`state_persistence`](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L966) uses [`StatePersistenceTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L296). Draws with two different pipelines (TRIANGLE_STRIP and TRIANGLE_LIST) using the same dynamic viewport/scissor state. Verifies that dynamic state persists across pipeline binds -- the first draw produces green in the top-left quadrant, the second produces blue in the bottom-right. Only available for non-mesh shader pipelines.

### static_stencil_mask_zero — Static stencil mask zero

[`static_stencil_mask_zero`](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L971) uses a function-style test case ([`staticStencilMaskZeroProgramsTest()`](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L519)). Uses `VK_DYNAMIC_STATE_STENCIL_WRITE_MASK` with static write mask = 0 and dynamic write mask = 0xFF. All fragments are discarded by the shader, so the stencil buffer should remain unchanged. Verifies via exact comparison of color, depth, and stencil buffers.

### double_static_bind — Double static bind

[`double_static_bind`](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L977) uses a function-style test case ([`doubleBindTest()`](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L824)). Uses `VK_DYNAMIC_STATE_VIEWPORT` with a "bad" static viewport and "good" static scissor. After binding the pipeline twice, the dynamic viewport override should take effect. Verifies via exact float threshold comparison that the entire framebuffer is filled with the expected color. Not available for shader object construction types.

## Parameter Dimensions

| Parameter | Observed values / source |
|---|---|
| Pipeline construction type | Passed from parent group |
| Shader type | Vertex+Fragment vs. Mesh+Fragment ([`init()` loop at L934](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L934)) |
| Dynamic states set | Viewport, rasterization, blend, depth/stencil (state_switch, bind_order, state_persistence); stencil write mask only (static_stencil_mask_zero); viewport only (double_static_bind) |
| Scissor configuration | Two scissors: `{0,0,W/2,H/2}` and `{W/2,H/2,W/2,H/2}` |
| Render dimensions | 128x128 |

## Support / Feature Requirements

| Test | Requirement | Check Function |
|---|---|---|
| state_switch, bind_order (vertex) | None | [`checkNothing`](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L461) |
| state_switch_mesh, bind_order_mesh | `VK_EXT_mesh_shader` | [`checkMeshShaderSupport`](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L455) |
| static_stencil_mask_zero | Pipeline construction requirements + depth/stencil format | [`checkStaticStencilMaskZeroSupport`](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L492) |
| double_static_bind | NOT shader object construction type | Guarded by [`!vk::isConstructionTypeShaderObject()`](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L975) |
| state_persistence | Not available for mesh shader | Guarded by [`if (!isMesh)`](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L963) |

## Verification Methods

### Fuzzy image comparison

[`StateSwitchTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L76), [`BindOrderTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L174), and [`StatePersistenceTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L374) use `tcu::fuzzyCompare()` with threshold `0.05f`. Software reference frames encode the expected two-quadrant patterns.

### Exact buffer comparison

[`staticStencilMaskZeroProgramsTest()`](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L519) performs three separate comparisons:
- Color: `tcu::floatThresholdCompare()` with threshold `(0,0,0,0)` — expects all fragments discarded (clear color).
- Depth: `tcu::dsThresholdCompare()` with threshold `0.0f` — expects depth unchanged.
- Stencil: `tcu::dsThresholdCompare()` with threshold `0.0f` — expects stencil unchanged at 0.

[`doubleBindTest()`](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L824) uses `tcu::floatThresholdCompare()` with threshold `(0,0,0,0)` — exact comparison.

## Test Principles Observed

- **Dynamic state switching**: Tests verify that changing dynamic state between draws produces the expected rendering.
- **Bind order independence**: The bind_order test verifies that the order of setting dynamic states does not affect the result.
- **State persistence across pipeline binds**: The state_persistence test verifies that dynamic state survives pipeline rebinds.
- **Static vs. dynamic interaction**: The static_stencil_mask_zero and double_static_bind tests verify edge cases where static and dynamic state values interact.

## Notes / Uncertainties

- Mesh shader variants are excluded on Vulkan SC builds.
- `double_static_bind` is excluded for shader object construction types.
- `state_persistence` has no mesh shader variant.
