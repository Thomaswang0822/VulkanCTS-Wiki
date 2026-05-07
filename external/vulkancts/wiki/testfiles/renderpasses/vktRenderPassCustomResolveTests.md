# vktRenderPassCustomResolveTests

## Source

[vktRenderPassCustomResolveTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp)

## Registration

Added to renderpass1, renderpass2, and dynamic_rendering root groups (non-SC, no secondary CB or partial secondary CB).

Registered group name: `"custom_resolve"` ([L5777](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L5777))

## Test Families

```
custom_resolve
+-- CustomResolveCase
|   Tests custom resolve using VK_EXT_custom_resolve with various
|   resolve types and attachment configurations.
+-- FragmentRegionCase
|   Fragment density map region interactions with custom resolve.
+-- FDMCase
|   Fragment density map variant tests for custom resolve.
+-- Sub-groups
    +-- simple_average
    +-- simple_fixed
    +-- simple_sample_2
    +-- complex configurations
```

## Parameter Dimensions

| Dimension | Values |
|-----------|--------|
| Pipeline construction types | MONOLITHIC, FAST_LINKED_LIBRARY, SHADER_OBJECT_UNLINKED_SPIRV ([L5786-L5790](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L5786-L5790)) |
| Depth/stencil formats | 7 formats ([L5792-L5800](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L5792-L5800)) |
| Resolve types | AVERAGE, FIXED_VALUE, SELECTED_SAMPLE |
| Attachment configurations | Various color/depth/stencil attachment setups |

## Support Requirements

| Requirement | Condition |
|-------------|-----------|
| customResolve feature | From VkCustomResolveFeaturesEXT ([L593](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L593)) |
| dynamicRenderingLocalRead feature | ([L605](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L605)) |
| VK_EXT_dynamic_rendering_unused_attachments | When unused attachments present ([L665](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L665)) |
| VK_EXT_shader_stencil_export | When stencil aspect used ([L691](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L691)) |
| Format and sample count support | Runtime checks |

## Verification

| Aspect | Method |
|--------|--------|
| Color | tcu::floatThresholdCompare with format-adaptive thresholds ([L3465](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L3465)) |
| Depth/stencil | tcu::dsThresholdCompare ([L3410](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L3410)) |
| sRGB formats | Thresholds widened by 2x ([L3462](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L3462)) |
