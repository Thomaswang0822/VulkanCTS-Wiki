# vktRenderPassRemainingArrayLayersTests

## Source

[vktRenderPassRemainingArrayLayersTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp)

## Registration

Added to root group (non-dynamic-rendering only).

Registered group name: `"remaining_array_layers"` ([L491](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L491))

## Test Families

```
remaining_array_layers
+-- RemainingArrayLayersTest
    Tests VK_REMAINING_ARRAY_LAYERS in image subresource ranges.
    +-- Layer tests
    |   Varying baseLayer and additionalLayers counts.
    +-- Framebuffer tests
        Single and multi-layer framebuffer configurations.
```

## Parameter Dimensions

| Dimension | Values |
|-----------|--------|
| Layer tests | {1,1,"1_1"}, {2,2,"2_2"}, {4,1,"4_1"}, {1,4,"1_4"} (baseLayer + additionalLayers) ([L493-L503](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L493-L503)) |
| Framebuffer tests | single_layer_fb, multi_layer_fb, multi_layer_fb_gl_layer ([L505-L514](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L505-L514)) |

## Support Requirements

| Requirement | Condition |
|-------------|-----------|
| VK_KHR_create_renderpass2 | For renderpass2 ([L476](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L476)) |
| VK_KHR_dynamic_rendering | For dynamic rendering ([L479](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L479)) |
| DEVICE_CORE_FEATURE_GEOMETRY_SHADER | When writeGlLayer is true ([L483](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L483)) |

## Verification

| Aspect | Method |
|--------|--------|
| Pixel values | Every pixel must be white (1.0, 1.0, 1.0, 1.0) across all layers and instances ([L385-L405](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L385-L405)) |
| Failure | tcu::TestStatus::fail if any pixel does not match |
