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
| VK_QCOM_multiview_per_view_render_areas | Required by `render_areas` cases ([line 1135](../../../modules/vulkan/renderpass/vktRenderPassMultiviewPerViewTests.cpp#L1135)) |
| VK_QCOM_multiview_per_view_viewports | Required for `MULTI_QCOM` render-area cases and per-view viewport cases built with the QCOM path ([lines 205-207](../../../modules/vulkan/renderpass/vktRenderPassMultiviewPerViewTests.cpp#L205-L207), [lines 1137-1140](../../../modules/vulkan/renderpass/vktRenderPassMultiviewPerViewTests.cpp#L1137-L1140)) |
| VK_KHR_dynamic_rendering | Required only when the parameters use dynamic rendering ([lines 196-198](../../../modules/vulkan/renderpass/vktRenderPassMultiviewPerViewTests.cpp#L196-L198), [lines 1157-1158](../../../modules/vulkan/renderpass/vktRenderPassMultiviewPerViewTests.cpp#L1157-L1158)) |
| VK_KHR_create_renderpass2 | Required by these tests ([line 202](../../../modules/vulkan/renderpass/vktRenderPassMultiviewPerViewTests.cpp#L202), [line 1160](../../../modules/vulkan/renderpass/vktRenderPassMultiviewPerViewTests.cpp#L1160)) |
| VK_KHR_multiview | Required by these tests ([line 203](../../../modules/vulkan/renderpass/vktRenderPassMultiviewPerViewTests.cpp#L203), [line 1161](../../../modules/vulkan/renderpass/vktRenderPassMultiviewPerViewTests.cpp#L1161)) |
| DEVICE_CORE_FEATURE_GEOMETRY_SHADER | Required for `MULTI_GEOM` render-area cases, together with `multiviewGeometryShader` ([lines 1146-1151](../../../modules/vulkan/renderpass/vktRenderPassMultiviewPerViewTests.cpp#L1146-L1151)) |
| DEVICE_CORE_FEATURE_MULTI_VIEWPORT | Required for per-view viewport cases and for non-`SINGLE` render-area cases ([line 194](../../../modules/vulkan/renderpass/vktRenderPassMultiviewPerViewTests.cpp#L194), [lines 1154-1155](../../../modules/vulkan/renderpass/vktRenderPassMultiviewPerViewTests.cpp#L1154-L1155)) |
| Vulkan 1.2 | Required for non-QCOM viewport path and `MULTI_VERT` render-area cases ([lines 208-209](../../../modules/vulkan/renderpass/vktRenderPassMultiviewPerViewTests.cpp#L208-L209), [lines 1141-1144](../../../modules/vulkan/renderpass/vktRenderPassMultiviewPerViewTests.cpp#L1141-L1144)) |
