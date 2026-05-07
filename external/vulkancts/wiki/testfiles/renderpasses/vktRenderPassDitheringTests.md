# vktRenderPassDitheringTests

## Source

[vktRenderPassDitheringTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp)

## Registration

Added to root group (monolithic pipeline, non-SC).

Registered group name: `"dithering"` ([L1359](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L1359))

## Test Families

```
dithering
+-- DitheringTest
    Tests VK_EXT_legacy_dithering extension behavior.
    +-- v1
    |   Revision 1 of the extension.
    +-- v2
        Revision 2 (dynamic rendering only).
```

## Parameter Dimensions

| Dimension | Values |
|-----------|--------|
| Format combinations | Single, pairs, triples from testFormats array ([L1182-L1256](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L1182-L1256)) |
| Render areas | Edges, corners, random offsets |
| Depth/stencil tests | format x stencil values (3) x depth values (3) x compare ops (2) ([L1264-L1306](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L1264-L1306)) |
| Blend tests | srcAlpha and additive blending per format ([L1310-L1333](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L1310-L1333)) |

## Support Requirements

| Requirement | Condition |
|-------------|-----------|
| VK_EXT_legacy_dithering | Always ([L287](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L287)) |
| VK_KHR_create_renderpass2 | For renderpass2 ([L281](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L281)) |
| VK_KHR_dynamic_rendering | For dynamic rendering ([L285](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L285)) |
| VK_KHR_maintenance5 | For some format support ([L303](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L303)) |

## Verification

| Aspect | Method |
|--------|--------|
| Dithered values | Within one ULP of expected values |
| Depth/stencil | Dithering does not affect depth/stencil buffer |
| Blend | Dithering works correctly with alpha and additive blending |
