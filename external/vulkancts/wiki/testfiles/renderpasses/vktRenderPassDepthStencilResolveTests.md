# vktRenderPassDepthStencilResolveTests

## Source

[vktRenderPassDepthStencilResolveTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassDepthStencilResolveTests.cpp)

## Registration

Added to `renderpass2` root group.

Registered group name: `"depth_stencil_resolve"` ([L2193](../../../modules/vulkan/renderpass/vktRenderPassDepthStencilResolveTests.cpp#L2193))

## Test Families

```
depth_stencil_resolve
+-- DSResolveTest
|   Main depth/stencil resolve tests iterating formats, sample counts,
|   resolve modes, image sizes, separate layouts, and unused resolve
|   attachment variants.
+-- MiscTestCase
    Edge-case tests for property queries and non-present aspect behavior.
    +-- PROPERTIES
    |   Queries VkPhysicalDeviceDepthStencilResolveProperties and verifies
    |   reported values.
    +-- RESOLVE_STENCIL_ASPECT_THAT_IS_NOT_PRESENT
    |   Verifies render pass creation when resolving a stencil aspect
    |   that is not present in the format.
    +-- RESOLVE_DEPTH_ASPECT_THAT_IS_NOT_PRESENT
        Verifies render pass creation when resolving a depth aspect
        that is not present in the format.
```

## Parameter Dimensions

| Dimension | Values |
|-----------|--------|
| Formats | D16_UNORM, X8_D24_UNORM_PACK32, D32_SFLOAT, S8_UINT, D16_UNORM_S8_UINT, D24_UNORM_S8_UINT, D32_SFLOAT_S8_UINT ([L1795](../../../modules/vulkan/renderpass/vktRenderPassDepthStencilResolveTests.cpp#L1795)) |
| Sample counts | {2, 4, 8, 16, 32, 64} |
| Resolve modes | SAMPLE_ZERO, AVERAGE, MIN, MAX, NONE |
| Separate depth/stencil layouts | boolean (when format has both aspects) |
| Unused resolve attachment | boolean |
| Sample mask | additional variant for SAMPLE_ZERO |

## Support Requirements

| Requirement | Condition |
|-------------|-----------|
| VK_KHR_depth_stencil_resolve | Always ([L1209](../../../modules/vulkan/renderpass/vktRenderPassDepthStencilResolveTests.cpp#L1209)) |
| DEVICE_CORE_FEATURE_SAMPLE_RATE_SHADING | Always ([L1207](../../../modules/vulkan/renderpass/vktRenderPassDepthStencilResolveTests.cpp#L1207)) |
| DEVICE_CORE_FEATURE_GEOMETRY_SHADER | When imageLayers > 1 ([L1211](../../../modules/vulkan/renderpass/vktRenderPassDepthStencilResolveTests.cpp#L1211)) |
| VK_KHR_separate_depth_stencil_layouts | When using separate layouts ([L1214](../../../modules/vulkan/renderpass/vktRenderPassDepthStencilResolveTests.cpp#L1214)) |

Additional runtime checks: supportedDepthResolveModes, supportedStencilResolveModes, independentResolve, independentResolveNone.

## Verification

| Aspect | Method |
|--------|--------|
| Depth | Float values compared against expected values derived from resolve mode and sample count |
| Stencil | uint8_t exact comparison |
| Color comparisons | tcu::floatThresholdCompare and pixel-level comparisons |
| PROPERTIES | Queries and verifies VkPhysicalDeviceDepthStencilResolveProperties fields |
| Non-present aspect | Verifies render pass creation behavior for missing depth/stencil aspects |
