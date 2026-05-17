# vktDynamicStateCBTests.cpp

## Overview

[`vktDynamicStateCBTests.cpp`](../../../modules/vulkan/dynamic_state/vktDynamicStateCBTests.cpp#L1) implements the [`cb_state`](../../../modules/vulkan/dynamic_state/vktDynamicStateCBTests.cpp#L212) subgroup of the dynamic_state category. It tests dynamic color blend state, specifically dynamic blend constants set via `vkCmdSetBlendConstants`.

## Role

Implementation file.

## Source Code

- Primary source: [`vktDynamicStateCBTests.cpp`](../../../modules/vulkan/dynamic_state/vktDynamicStateCBTests.cpp#L1)
- Shared base: [`DynamicStateBaseClass`](../../../modules/vulkan/dynamic_state/vktDynamicStateBaseClass.hpp#L43)
- Test case utilities: [`vktDynamicStateTestCaseUtil.hpp`](../../../modules/vulkan/dynamic_state/vktDynamicStateTestCaseUtil.hpp#L1)

## Registration Hierarchy

```text
dynamic_state.monolithic.cb_state
├── blend_constants
└── blend_constants_mesh    (non-VulkanSC only)
```

## Test Families

### blend_constants — Blend constants

[`blend_constants`](../../../modules/vulkan/dynamic_state/vktDynamicStateCBTests.cpp#L233) and [`blend_constants_mesh`](../../../modules/vulkan/dynamic_state/vktDynamicStateCBTests.cpp#L241) use [`BlendConstantsTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateCBTests.cpp#L49). A full-screen quad is drawn with green vertex colors onto a white background, with blending enabled using `VK_BLEND_FACTOR_CONSTANT_COLOR` and `VK_BLEND_FACTOR_CONSTANT_ALPHA` as destination blend factors. Dynamic blend constants `(0.33, 0.1, 0.66, 0.5)` are set via [`setDynamicBlendState()`](../../../modules/vulkan/dynamic_state/vktDynamicStateCBTests.cpp#L132). The test verifies the blended output matches the expected color derived from the blend operation.

### blend_constants_mesh — Blend constants (mesh shader)

Mesh shader variant of `blend_constants`. See `blend_constants` above for test logic. Excluded on Vulkan SC builds.

## Parameter Dimensions

| Parameter | Observed values / source |
|---|---|
| Pipeline construction type | Passed from parent group |
| Shader type | Vertex+Fragment vs. Mesh+Fragment |
| Blend constants | `(0.33f, 0.1f, 0.66f, 0.5f)` set via [`setDynamicBlendState()`](../../../modules/vulkan/dynamic_state/vktDynamicStateCBTests.cpp#L132) |
| Blend configuration | `SRC_ALPHA * CONSTANT_COLOR + CONSTANT_ALPHA` ([L78-L80](../../../modules/vulkan/dynamic_state/vktDynamicStateCBTests.cpp#L78)) |
| Topology | `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP` |
| Render dimensions | 128x128 (from base class) |

## Support / Feature Requirements

| Test | Requirement | Check Function |
|---|---|---|
| blend_constants | Pipeline construction requirements only | `NoSupport0` |
| blend_constants_mesh | `VK_EXT_mesh_shader` | [`checkMeshShaderSupport()`](../../../modules/vulkan/dynamic_state/vktDynamicStateCBTests.cpp#L202) |

## Verification Methods

**Fuzzy image comparison** via [`tcu::fuzzyCompare()`](../../../modules/vulkan/dynamic_state/vktDynamicStateCBTests.cpp#L190) with threshold `0.05f`:

1. Render a full-screen quad with green vertex color, blending against a white background using dynamic blend constants.
2. Build a software reference frame: black background with expected blended color `(0.33, 1.0, 0.66, 1.0)` in the quad region.
3. Read back the rendered image and compare against the reference.

The expected color is derived from the blend operation: with source green `(0,1,0,1)` and blend constants `(0.33, 0.1, 0.66, 0.5)`, the result is `src_alpha * src_color + constant_color * (1 - src_alpha)`.

## Test Principles Observed

- **Dynamic blend constants override**: The test verifies that dynamically set blend constants are used in the blend operation, not the pipeline's static blend constants.
- **Mesh shader parity**: The same test logic is applied with both vertex-shader and mesh-shader pipelines.

## Notes / Uncertainties

- Mesh shader variant is excluded on Vulkan SC builds.
- This is a focused test file covering only blend constants; other color blend dynamic states are not tested here.
