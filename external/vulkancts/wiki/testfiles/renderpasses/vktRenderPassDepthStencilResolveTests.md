# vktRenderPassDepthStencilResolveTests

## Source

[vktRenderPassDepthStencilResolveTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassDepthStencilResolveTests.cpp)

## Registration Hierarchy

```text
renderpasses.renderpass2.depth_stencil_resolve
├── image_2d_16_64_6
├── image_2d_17_1
├── image_2d_32_32
├── image_2d_49_13
├── image_2d_5_1
├── image_2d_8_32
└── misc
```

Registered under the `renderpass2` root group only. Registered group name: `"depth_stencil_resolve"` ([L2193](../../../modules/vulkan/renderpass/vktRenderPassDepthStencilResolveTests.cpp#L2193)).

## Test Families

### image_2d_32_32 — 32x32 2D image resolve tests

Main depth/stencil resolve tests for a 32x32 image with render area {0,0,32,32} and clear value {0.000f, 0x00}. Contains subgroups organized by sample count, then by format (with separate layout variants), then by resolve mode combination. Each leaf is a DSResolveTest iterating depth and stencil resolve modes.

### image_2d_8_32 — 8x32 2D image resolve tests

Resolve tests for an 8x32 image with render area {1,1,6,30} and clear value {0.123f, 0x01}. Same subgroup structure as image_2d_32_32.

### image_2d_49_13 — 49x13 2D image resolve tests

Resolve tests for a 49x13 image with render area {10,5,20,8} and clear value {1.000f, 0x05}. Same subgroup structure.

### image_2d_5_1 — 5x1 2D image resolve tests

Resolve tests for a 5x1 image with render area {0,0,5,1} and clear value {0.500f, 0x00}. Same subgroup structure.

### image_2d_17_1 — 17x1 2D image resolve tests

Resolve tests for a 17x1 image with render area {1,0,15,1} and clear value {0.789f, 0xfa}. Same subgroup structure.

### image_2d_16_64_6 — 16x64x6 layered 2D image resolve tests

Layered texture tests for a 16x64 image with 6 layers, render area {10,10,6,54}, and clear value {1.0f, 0x0}. Tests resolve behavior for multi-layered framebuffers starting at a non-zero layer. Contains subgroups by sample count, format, and resolve mode.

### misc — Miscellaneous depth/stencil resolve tests

Edge-case tests for property queries and non-present aspect behavior. Contains leaf tests:
- `properties` — Queries VkPhysicalDeviceDepthStencilResolveProperties and verifies reported values.
- `resolve_stencil_aspect_that_is_not_present` — Verifies render pass creation when resolving a stencil aspect that is not present in the format.
- `resolve_depth_aspect_that_is_not_present` — Verifies render pass creation when resolving a depth aspect that is not present in the format.

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
