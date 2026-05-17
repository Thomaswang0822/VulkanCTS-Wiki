# vktRenderPassDitheringTests

## Source

[vktRenderPassDitheringTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp)

## Registration Hierarchy

```text
renderpasses.renderpass1.dithering
└── v1
```

Registered in all three rendering-type roots (renderpass1, renderpass2, dynamic_rendering) via [`createRenderPassDitheringTests`](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L1356). Monolithic pipeline only. Under `dynamic_rendering`, an additional child `v2` is present ([L1361](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L1361)).

## Test Families

### v1 — Revision 1 dithering tests

Created via [`createDitheringRevision1GroupTests`](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L1344). Always present. Contains three subgroups:

- **base** — Ensures dithering works and values are within one ULP. Tests single formats, pairs, and triples from the testFormats array ([L1182-L1256](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L1182-L1256)).
- **depth_stencil** — Depth/stencil tests ensuring dithering works with depth/stencil and does not affect depth/stencil buffer. Format x stencil values (3) x depth values (3) x compare ops (2) ([L1264-L1306](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L1264-L1306)).
- **blend** — Blend tests with srcAlpha and additive blending per format ([L1310-L1333](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L1310-L1333)).

### v2 — Revision 2 dithering tests (dynamic rendering only)

Created via [`createDitheringRevision2GroupTests`](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L1350). Only added under dynamic rendering ([L1361](../../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp#L1361)). Contains the same three subgroups as v1 (base, depth_stencil, blend) with `revision2 = true`.

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
