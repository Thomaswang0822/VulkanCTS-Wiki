# vktDynamicRenderingLocalReadMaint10Tests

## Source

[vktDynamicRenderingLocalReadMaint10Tests.cpp](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp)

## Registration Hierarchy

```text
renderpasses.dynamic_rendering.primary_cmd_buff.m10_feedback_loop
```

Registered under `primary_cmd_buff` only ([vktRenderPassTests.cpp#L8536](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8536)). The `m10_feedback_loop` group is created at [line 1713](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L1713). Contains 120 test cases as direct children; test case names include uppercase feedback-case suffixes (e.g., `_loop_Y`, `_loop_NN`) that are not parseable by the current validator's lowercase-only child name pattern.

## Test Families

Feedback loop tests combining VK_KHR_dynamic_rendering_local_read with VK_KHR_maintenance10. 120 test cases generated from parameter combinations.

**Test case naming pattern:** `{format}_samples_{count}_loop_{case}{_sample_{id}}{_general_layout}`

**Parameter Dimensions** ([lines 1726-1731](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L1726-L1731)):

- format: {R8G8B8A8_UNORM, D16_UNORM, S8_UINT, D24_UNORM_S8_UINT, D32_SFLOAT_S8_UINT}
- sampleCount: {1x, 4x}
- feedbackCase: 6 combinations of boolean vectors (color/depth/stencil loop flags: N, Y, NN, NY, YN, YY for color formats; Y only for depth/stencil formats)
- sampleId: {-1, 0, 1, 2, 3} (only for sampleCount=4)
- generalLayout: {false, true}

**Verification:**

- Color: `tcu::floatThresholdCompare`
- Depth: format-dependent thresholds
- Stencil: direct byte comparison

## Support / Feature Requirements

| Requirement | Context |
|---|---|
| VK_KHR_dynamic_rendering_local_read | [line 2455](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L2455) |
| VK_KHR_maintenance10 | [line 258](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L258) |
| VK_EXT_shader_stencil_export | Required for stencil aspect ([line 265](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L265)) |
| Vulkan 1.4 | `dynamicRenderingLocalReadDepthStencilAttachments` / `dynamicRenderingLocalReadMultisampledAttachments` |
