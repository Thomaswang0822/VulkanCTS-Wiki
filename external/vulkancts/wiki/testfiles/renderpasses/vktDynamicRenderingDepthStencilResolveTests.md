# vktDynamicRenderingDepthStencilResolveTests

## Source

[vktDynamicRenderingDepthStencilResolveTests.cpp](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp)

## Registration

Added to dynamic_rendering root group (monolithic pipeline).

Registered group name: `"depth_stencil_resolve"` ([line 1930](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L1930))

## Test Families

```
depth_stencil_resolve
|-- samples_N
    |-- format[_separate_layouts]
        |-- depth_X_stencil_Y_testing_Z
```

**Parameter Dimensions** ([lines 1766-1916](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L1766-L1916)):

- sampleCount: {2, 4, 8, 16, 32, 64}
- format: 7 depth/stencil formats
- separateDepthStencilLayouts: {false, true} when format has both aspects
- depthResolveMode: {NONE, SAMPLE_ZERO, AVERAGE, MIN, MAX}
- stencilResolveMode: {NONE, SAMPLE_ZERO, MIN, MAX} (no AVERAGE for stencil)
- Push constant tests for depth-only formats

**Verification** ([lines 913](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L913), [997](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L997)):

- `verifyDepth()`: format-specific extraction, compared against `depthExpectedValue` table with epsilon `0.002f`
- `verifyStencil()`: byte-by-byte against `stencilExpectedValue` table

## Support Requirements

| Requirement | Context |
|---|---|
| VK_KHR_dynamic_rendering | [line 1199](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L1199) |
| VK_KHR_depth_stencil_resolve | [line 1200](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L1200) |
| DEVICE_CORE_FEATURE_SAMPLE_RATE_SHADING | [line 1202](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L1202) |
| DEVICE_CORE_FEATURE_GEOMETRY_SHADER | Required when `imageLayers > 1` |
| VK_KHR_separate_depth_stencil_layouts | Required for separate layouts |
| VkPhysicalDeviceDepthStencilResolveProperties | Checked for supported resolve modes |
