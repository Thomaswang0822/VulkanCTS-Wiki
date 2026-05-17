# vktRenderPassMultiviewPerViewTests

## Source

[vktRenderPassMultiviewPerViewTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassMultiviewPerViewTests.cpp)

## Registration Hierarchy

```text
renderpasses.renderpass2.multiview_per_view
├── viewports
└── render_areas
```

Registered in renderpass2 and dynamic_rendering roots (non-SC) via [`createRenderPassMultiviewPerViewTests`](../../../modules/vulkan/renderpass/vktRenderPassMultiviewPerViewTests.cpp#L1810). Not registered under renderpass1.

## Test Families

### viewports — Per-view viewport attributes

Tests per-view viewport attributes with multiview ([lines 1820-1835](../../../modules/vulkan/renderpass/vktRenderPassMultiviewPerViewTests.cpp#L1820-L1835)).

**Parameter Dimensions:**

- dynamic viewport: NO / YES / YES_COUNT
- dynamic scissor: NO / YES / YES_COUNT
- viewport diff flags: 4 values
- multi-pass: 2

Total: 72 cases

**Verification:**

- Color: `tcu::floatThresholdCompare`
- Depth: `tcu::dsThresholdCompare`

### render_areas — Per-view render areas

Tests per-view render areas with VK_QCOM_multiview_per_view_render_areas ([lines 1838-1858](../../../modules/vulkan/renderpass/vktRenderPassMultiviewPerViewTests.cpp#L1838-L1858)).

**Parameter Dimensions:**

- viewport type: SINGLE / MULTI_QCOM / MULTI_GEOM / MULTI_VERT
- subpass load op: 2 values
- multisample load op: 3 values
- multi-pass: 2

**Verification:**

- `tcu::floatThresholdCompare` with zero threshold per layer

## Support Requirements

| Requirement | Context |
|---|---|
| VK_QCOM_multiview_per_view_render_areas | [line 1121](../../../modules/vulkan/renderpass/vktRenderPassMultiviewPerViewTests.cpp#L1121) |
| VK_QCOM_multiview_per_view_viewports | Required for MULTI_QCOM ([line 1125](../../../modules/vulkan/renderpass/vktRenderPassMultiviewPerViewTests.cpp#L1125)) |
| VK_KHR_dynamic_rendering | Core dependency |
| VK_KHR_create_renderpass2 | Core dependency |
| VK_KHR_multiview | Core dependency |
| DEVICE_CORE_FEATURE_GEOMETRY_SHADER | Required for MULTI_GEOM |
| DEVICE_CORE_FEATURE_MULTI_VIEWPORT | Required for non-SINGLE |
| Vulkan 1.2 | Required for MULTI_VERT |
