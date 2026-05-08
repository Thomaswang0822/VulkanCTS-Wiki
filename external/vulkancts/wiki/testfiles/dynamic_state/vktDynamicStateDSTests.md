# vktDynamicStateDSTests.cpp

## Overview

[`vktDynamicStateDSTests.cpp`](../../../modules/vulkan/dynamic_state/vktDynamicStateDSTests.cpp#L1) implements the [`ds_state`](../../../modules/vulkan/dynamic_state/vktDynamicStateDSTests.cpp#L1264) subgroup of the dynamic_state category. It tests dynamic depth/stencil state, including depth bounds and stencil parameters (compare mask, write mask, reference), with both traditional vertex-shader and mesh-shader pipelines.

## Role

Implementation file.

## Source Code

- Primary source: [`vktDynamicStateDSTests.cpp`](../../../modules/vulkan/dynamic_state/vktDynamicStateDSTests.cpp#L1)
- Shared base: [`DynamicStateBaseClass`](../../../modules/vulkan/dynamic_state/vktDynamicStateBaseClass.hpp#L43)
- Test case utilities: [`vktDynamicStateTestCaseUtil.hpp`](../../../modules/vulkan/dynamic_state/vktDynamicStateTestCaseUtil.hpp#L1)

## Registration Path

This file contributes the [`DynamicStateDSTests`](../../../modules/vulkan/dynamic_state/vktDynamicStateDSTests.cpp#L1262) group (named `"ds_state"`), which is attached under each pipeline construction type subgroup by [`createChildren()`](../../../modules/vulkan/dynamic_state/vktDynamicStateTests.cpp#L52).

## Test Hierarchy

```text
ds_state
├── depth_bounds_1
├── depth_bounds_2
├── stencil_params_basic_1          (non-VulkanSC only)
├── stencil_params_basic_2          (non-VulkanSC only)
├── stencil_params_advanced
├── depth_bounds_1_mesh             (non-VulkanSC only)
├── depth_bounds_2_mesh             (non-VulkanSC only)
├── stencil_params_basic_1_mesh     (non-VulkanSC only)
├── stencil_params_basic_2_mesh     (non-VulkanSC only)
└── stencil_params_advanced_mesh    (non-VulkanSC only)
```

Source: [`DynamicStateDSTests::init()`](../../../modules/vulkan/dynamic_state/vktDynamicStateDSTests.cpp#L1274).

## Test Families

### 1. Depth bounds (parametric)

[`depth_bounds_1`](../../../modules/vulkan/dynamic_state/vktDynamicStateDSTests.cpp#L1305) and [`depth_bounds_1_mesh`](../../../modules/vulkan/dynamic_state/vktDynamicStateDSTests.cpp#L1305) use [`DepthBoundsParamTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateDSTests.cpp#L504). Tests dynamic depth bounds `[0.5f, 0.75f]` set via `vkCmdSetDepthBounds`. Verifies that only geometry within the depth bounds range passes the depth bounds test.

### 2. Depth bounds (pre-filled)

[`depth_bounds_2`](../../../modules/vulkan/dynamic_state/vktDynamicStateDSTests.cpp#L1307) and [`depth_bounds_2_mesh`](../../../modules/vulkan/dynamic_state/vktDynamicStateDSTests.cpp#L1307) use [`DepthBoundsTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateDSTests.cpp#L630). Pre-fills the depth buffer with varying depth values, then applies static depth bounds `[0.3f, 0.9f]`. Verifies that only pixels with depth values within the bounds are rendered.

### 3. Stencil parameters (basic)

[`stencil_params_basic_1`](../../../modules/vulkan/dynamic_state/vktDynamicStateDSTests.cpp#L1310) and [`stencil_params_basic_2`](../../../modules/vulkan/dynamic_state/vktDynamicStateDSTests.cpp#L1313) use [`StencilParamsBasicTestCase`](../../../modules/vulkan/dynamic_state/vktDynamicStateDSTests.cpp#L1050). Tests dynamic stencil compare mask, write mask, and reference values via `vkCmdSetStencilCompareMask`, `vkCmdSetStencilWriteMask`, and `vkCmdSetStencilReference`. Two configurations:
- basic_1: writeMask=`0x0D`, readMask=`0x06`, expectedValue=`0x05`, expectedColor=blue
- basic_2: writeMask=`0x06`, readMask=`0x02`, expectedValue=`0x05`, expectedColor=green

### 4. Stencil parameters (advanced)

[`stencil_params_advanced`](../../../modules/vulkan/dynamic_state/vktDynamicStateDSTests.cpp#L1317) and [`stencil_params_advanced_mesh`](../../../modules/vulkan/dynamic_state/vktDynamicStateDSTests.cpp#L1317) use [`StencilParamsAdvancedTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateDSTests.cpp#L1109). Uses two draws with different stencil parameters and `VK_COMPARE_OP_NOT_EQUAL`, verifying that the stencil state changes correctly between draws.

## Parameter Dimensions

| Parameter | Observed values / source |
|---|---|
| Pipeline construction type | Passed from parent group |
| Shader type | Vertex+Fragment vs. Mesh+Fragment ([`init()` loop at L1281](../../../modules/vulkan/dynamic_state/vktDynamicStateDSTests.cpp#L1281)) |
| Depth bounds range | `[0.5f, 0.75f]` (parametric), `[0.3f, 0.9f]` (pre-filled) |
| Stencil write mask | `0x0D`, `0x06`, `0x0E` |
| Stencil compare mask | `0x06`, `0x02`, `0xFF` |
| Stencil reference | `0x05`, `0x0E`, `0x0F` |
| Depth/stencil format | Runtime-selected: `VK_FORMAT_D24_UNORM_S8_UINT` or `VK_FORMAT_D32_SFLOAT_S8_UINT` |
| Render dimensions | 128x128 |

## Support / Feature Requirements

| Test | Requirement | Check Function |
|---|---|---|
| depth_bounds_1/2 (vertex) | `DEVICE_CORE_FEATURE_DEPTH_BOUNDS` | [`checkDepthBoundsSupport`](../../../modules/vulkan/dynamic_state/vktDynamicStateDSTests.cpp#L1246) |
| depth_bounds_1/2 (mesh) | depth bounds + `VK_EXT_mesh_shader` | [`checkDepthBoundsAndMeshShaderSupport`](../../../modules/vulkan/dynamic_state/vktDynamicStateDSTests.cpp#L1252) |
| All mesh variants | `VK_EXT_mesh_shader` | [`checkMeshShaderSupport`](../../../modules/vulkan/dynamic_state/vktDynamicStateDSTests.cpp#L1045) |
| stencil_params_advanced (vertex) | None | [`checkNothing`](../../../modules/vulkan/dynamic_state/vktDynamicStateDSTests.cpp#L1041) |

## Verification Methods

All test instances use **fuzzy image comparison** via `tcu::fuzzyCompare()` with threshold `0.05f`:

- [`DepthBoundsParamTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateDSTests.cpp#L619): Reference expects green for pixels within depth bounds, blue otherwise.
- [`DepthBoundsTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateDSTests.cpp#L883): Reference marks pixels green where pre-filled depth values fall within bounds.
- [`StencilParamsBasicTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateDSTests.cpp#L1030): Reference expects the entire framebuffer to be the expected color if stencil compare passes.
- [`StencilParamsAdvancedTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateDSTests.cpp#L1235): Reference expects green in the center rectangle and blue in the outer region.

## Test Principles Observed

- **Dynamic depth bounds override**: Tests set depth bounds dynamically and verify they override pipeline static state.
- **Stencil mask/reference dynamics**: Tests verify that dynamically set stencil compare mask, write mask, and reference values are correctly applied.
- **Multi-draw stencil state changes**: The advanced test verifies that stencil state can be changed between draws within the same command buffer.
- **Mesh shader parity**: Same test logic applied with both vertex-shader and mesh-shader pipelines.

## Notes / Uncertainties

- Mesh shader variants and `stencil_params_basic_1`/`stencil_params_basic_2` are excluded on Vulkan SC builds.
- The depth/stencil format is selected at runtime with fallback logic.
