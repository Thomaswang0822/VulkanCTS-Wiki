# vktDynamicRenderingDepthStencilResolveTests

## Source

[vktDynamicRenderingDepthStencilResolveTests.cpp](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp)

## Registration Hierarchy

```text
renderpasses.dynamic_rendering.primary_cmd_buff.depth_stencil_resolve
├── samples_16
├── samples_2
├── samples_32
├── samples_4
├── samples_64
└── samples_8
```

Registered under all four dynamic rendering intermediate groups: `primary_cmd_buff`, `partial_secondary_cmd_buff`, `complete_secondary_cmd_buff`, and `graphics_pipeline_library` ([vktRenderPassTests.cpp#L8527](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8527)). The `depth_stencil_resolve` group is created at [line 1930](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L1930).

## Test Families

### samples_2 — 2x MSAA depth/stencil resolve

### samples_4 — 4x MSAA depth/stencil resolve

### samples_8 — 8x MSAA depth/stencil resolve

### samples_16 — 16x MSAA depth/stencil resolve

### samples_32 — 32x MSAA depth/stencil resolve

### samples_64 — 64x MSAA depth/stencil resolve

Each sample group contains format subgroups (e.g., `d16_unorm`, `d24_unorm_s8_uint`, `d32_sfloat_s8_uint`, `d16_unorm_s8_uint`, `d32_sfloat`, `s8_uint`, `d24_unorm`), which in turn contain individual resolve-mode test cases named `depth_{mode}_stencil_{mode}_testing_{aspect}`.

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

## Support / Feature Requirements

| Requirement | Context |
|---|---|
| VK_KHR_dynamic_rendering | [line 1199](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L1199) |
| VK_KHR_depth_stencil_resolve | [line 1200](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L1200) |
| DEVICE_CORE_FEATURE_SAMPLE_RATE_SHADING | [line 1202](../../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp#L1202) |
| DEVICE_CORE_FEATURE_GEOMETRY_SHADER | Required when `imageLayers > 1` |
| VK_KHR_separate_depth_stencil_layouts | Required for separate layouts |
| VkPhysicalDeviceDepthStencilResolveProperties | Checked for supported resolve modes |
