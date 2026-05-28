# vktRenderPassRemainingArrayLayersTests

## Source

[vktRenderPassRemainingArrayLayersTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp)

## Registration Hierarchy

```text
renderpasses.renderpass1.remaining_array_layers
├── single_layer_fb
├── multi_layer_fb
└── multi_layer_fb_gl_layer
```

Registered in renderpass1 and renderpass2 roots only (not dynamic rendering) via [`createRenderPassRemainingArrayLayersTests`](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L488). The guard at [L8596](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8596) excludes this group from `RENDERING_TYPE_DYNAMIC_RENDERING`.

## Test Families

### single_layer_fb — Single-layer framebuffer tests

Tests VK_REMAINING_ARRAY_LAYERS with a single-layer framebuffer configuration. Each child test varies baseLayer and additionalLayers counts: `{1,1,"1_1"}`, `{2,2,"2_2"}`, `{4,1,"4_1"}`, `{1,4,"1_4"}` ([L493-L503](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L493-L503)).

### multi_layer_fb — Multi-layer framebuffer tests

Tests VK_REMAINING_ARRAY_LAYERS with a multi-layer framebuffer configuration (without gl_Layer). Same layer parameter variations as single_layer_fb ([L505-L514](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L505-L514)).

### multi_layer_fb_gl_layer — Multi-layer framebuffer with gl_Layer tests

Tests VK_REMAINING_ARRAY_LAYERS with a multi-layer framebuffer using gl_Layer. Requires `DEVICE_CORE_FEATURE_GEOMETRY_SHADER` when `writeGlLayer` is true ([L483](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L483)). Same layer parameter variations ([L505-L514](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L505-L514)).

## Parameter Dimensions

| Dimension | Values |
|-----------|--------|
| Layer tests | {1,1,"1_1"}, {2,2,"2_2"}, {4,1,"4_1"}, {1,4,"1_4"} (baseLayer + additionalLayers) ([L493-L503](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L493-L503)) |
| Framebuffer tests | single_layer_fb, multi_layer_fb, multi_layer_fb_gl_layer ([L505-L514](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L505-L514)) |

## Support / Feature Requirements

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
