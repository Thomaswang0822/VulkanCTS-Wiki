# vktDynamicStateRSTests.cpp

## Overview

[`vktDynamicStateRSTests.cpp`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L1) implements the [`rs_state`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L1259) subgroup of the dynamic_state category. It tests dynamic rasterization state including depth bias, depth bias clamp, and line width, with both traditional vertex-shader and mesh-shader pipelines.

## Role

Implementation file.

## Source Code

- Primary source: [`vktDynamicStateRSTests.cpp`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L1)
- Shared base: [`DynamicStateBaseClass`](../../../modules/vulkan/dynamic_state/vktDynamicStateBaseClass.hpp#L43)
- Test case utilities: [`vktDynamicStateTestCaseUtil.hpp`](../../../modules/vulkan/dynamic_state/vktDynamicStateTestCaseUtil.hpp#L1)

## Registration Hierarchy

```text
dynamic_state.monolithic.rs_state
├── depth_bias
├── depth_bias_mesh              (non-VulkanSC only)
├── depth_bias_clamp
├── depth_bias_clamp_mesh        (non-VulkanSC only)
├── line_width
├── line_width_mesh              (non-VulkanSC only)
├── nonzero_depth_bias_constant
├── nonzero_depth_bias_constant_mesh  (non-VulkanSC only)
├── nonzero_depth_bias_clamp
└── nonzero_depth_bias_clamp_mesh     (non-VulkanSC only)
```

## Test Families

### depth_bias — Depth bias

[`depth_bias`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L1296) and [`depth_bias_mesh`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L1296) use [`DepthBiasParamTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L465). Tests dynamic depth bias via `vkCmdSetDepthBias`. Sets depth bias constant factor from `0.0f` to `-1.0f` between draws, verifying that the second draw passes the depth test due to the bias offset.

### depth_bias_mesh — Depth bias (mesh shader)

Mesh shader variant of `depth_bias`. See `depth_bias` above for test logic. Excluded on Vulkan SC builds.

### depth_bias_clamp — Depth bias clamp

[`depth_bias_clamp`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L1299) and [`depth_bias_clamp_mesh`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L1299) use [`DepthBiasClampParamTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L591). Tests dynamic depth bias with a large constant factor (`1000.0f`) and clamp (`0.005f`) via `vkCmdSetDepthBias`. Verifies that the clamp limits the effective bias, allowing the second draw to appear.

### depth_bias_clamp_mesh — Depth bias clamp (mesh shader)

Mesh shader variant of `depth_bias_clamp`. See `depth_bias_clamp` above for test logic. Excluded on Vulkan SC builds.

### line_width — Line width

[`line_width`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L1305) and [`line_width_mesh`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L1305) use [`LineWidthParamTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L707). Tests dynamic line width via `vkCmdSetLineWidth` using the device's maximum supported line width from `lineWidthRange[1]`.

### line_width_mesh — Line width (mesh shader)

Mesh shader variant of `line_width`. See `line_width` above for test logic. Excluded on Vulkan SC builds.

### nonzero_depth_bias_constant — Nonzero depth bias constant

[`nonzero_depth_bias_constant`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L1322) and [`nonzero_depth_bias_constant_mesh`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L1322) use [`DepthBiasNonZeroCase`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L827) / [`DepthBiasNonZeroInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L848). Tests that a nonzero depth bias constant factor (`16384.0f`) with zero clamp is actually applied. Uses push constants for depth values and verifies via exact float threshold comparison.

### nonzero_depth_bias_constant_mesh — Nonzero depth bias constant (mesh shader)

Mesh shader variant of `nonzero_depth_bias_constant`. See `nonzero_depth_bias_constant` above for test logic. Excluded on Vulkan SC builds.

### nonzero_depth_bias_clamp — Nonzero depth bias clamp

[`nonzero_depth_bias_clamp`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L1337) and [`nonzero_depth_bias_clamp_mesh`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L1337) use [`DepthBiasNonZeroCase`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L827) / [`DepthBiasNonZeroInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L848). Tests that a nonzero depth bias clamp (`0.125f`) with constant factor (`16384.0f`) is applied. Uses push constants for depth values and verifies via exact float threshold comparison.

### nonzero_depth_bias_clamp_mesh — Nonzero depth bias clamp (mesh shader)

Mesh shader variant of `nonzero_depth_bias_clamp`. See `nonzero_depth_bias_clamp` above for test logic. Excluded on Vulkan SC builds.

## Parameter Dimensions

| Parameter | Observed values / source |
|---|---|
| Pipeline construction type | Passed from parent group |
| Shader type | Vertex+Fragment vs. Mesh+Fragment ([`init()` loop at L1276](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L1276)) |
| Depth bias constant factor | `0.0f` → `-1.0f` ([`DepthBiasParamTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L533)), `1000.0f` → `0.0f` ([`DepthBiasClampParamTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L637)), `16384.0f` ([`DepthBiasNonZeroInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L818)) |
| Depth bias clamp | `0.005f` ([`DepthBiasClampParamTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L637)), `0.0f` or `0.125f` ([`DepthBiasNonZeroInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L818)) |
| Line width | Device maximum from `lineWidthRange[1]` ([`LineWidthParamTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L738)) |
| Render dimensions | 128x128 (base class), 8x8 ([`DepthBiasNonZeroInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L986)) |

## Support / Feature Requirements

| Test | Requirement | Check Function |
|---|---|---|
| depth_bias_clamp (vertex) | `DEVICE_CORE_FEATURE_DEPTH_BIAS_CLAMP` | [`checkDepthBiasClampSupport`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L1226) |
| line_width (vertex) | `DEVICE_CORE_FEATURE_WIDE_LINES` | [`checkWideLinesSupport`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L1231) |
| All mesh variants | `VK_EXT_mesh_shader` | [`checkMeshShaderSupport`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L1236) |
| depth_bias_clamp_mesh | depth bias clamp + mesh shader | [`checkDepthBiasClampAndMeshShaderSupport`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L1239) |
| line_width_mesh | wide lines + mesh shader | [`checkWideLinesAndMeshShaderSupport`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L1245) |
| nonzero_depth_bias_constant/clamp | Pipeline construction requirements | [`DepthBiasNonZeroCase::checkSupport()`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L880) |

## Verification Methods

### Fuzzy image comparison

[`DepthBiasParamTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L580), [`DepthBiasClampParamTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L696), and [`LineWidthParamTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L799) use `tcu::fuzzyCompare()` with threshold `0.05f`. A software reference frame is generated pixel-by-pixel and compared against the GPU-rendered color attachment.

### Float threshold comparison

[`DepthBiasNonZeroInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L1217) uses `tcu::floatThresholdCompare()` with threshold `0.0f` (exact match), comparing every pixel against the expected green color `(0,1,0,1)`. This works because the fragment shader only outputs color when the depth value falls within the expected range after bias.

## Test Principles Observed

- **Dynamic state override**: Tests set rasterization state dynamically and verify it overrides pipeline static state.
- **Depth bias mechanics**: Tests cover both the constant factor and clamp components of depth bias, including extreme values.
- **Nonzero bias validation**: The nonzero tests verify that large bias values are actually applied, not just accepted by the API.
- **Mesh shader parity**: Same test logic applied with both vertex-shader and mesh-shader pipelines.

## Notes / Uncertainties

- Mesh shader variants are excluded on Vulkan SC builds.
- The depth/stencil format is selected at runtime, preferring `VK_FORMAT_D24_UNORM_S8_UINT` with fallback to `VK_FORMAT_D32_SFLOAT_S8_UINT`.
