# vktDynamicRenderingLocalReadMaint10Tests

## Source

[vktDynamicRenderingLocalReadMaint10Tests.cpp](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp)

## Registration

Added to dynamic_rendering root group (no secondary CB).

Registered group name: `"m10_feedback_loop"` ([line 1713](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L1713))

## Test Families

```
m10_feedback_loop
|-- Feedback loop tests combining DRLR with maintenance10
```

**Parameter Dimensions** ([lines 1726-1731](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L1726-L1731)):

- format: {R8G8B8A8_UNORM, D16_UNORM, S8_UINT, D24_UNORM_S8_UINT, D32_SFLOAT_S8_UINT}
- sampleCount: {1x, 4x}
- feedbackCase: 6 combinations of boolean vectors
- sampleId: {-1, 0, 1, 2, 3}
- generalLayout: {false, true}

**Verification:**

- Color: `tcu::floatThresholdCompare`
- Depth: format-dependent thresholds
- Stencil: direct byte comparison

## Support Requirements

| Requirement | Context |
|---|---|
| VK_KHR_dynamic_rendering_local_read | [line 2455](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L2455) |
| VK_KHR_maintenance10 | [line 258](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L258) |
| VK_EXT_shader_stencil_export | Required for stencil aspect ([line 265](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp#L265)) |
| Vulkan 1.4 | `dynamicRenderingLocalReadDepthStencilAttachments` / `dynamicRenderingLocalReadMultisampledAttachments` |
