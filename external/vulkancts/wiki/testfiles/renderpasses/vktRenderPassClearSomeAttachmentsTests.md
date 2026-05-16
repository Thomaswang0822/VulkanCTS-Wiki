# vktRenderPassClearSomeAttachmentsTests

## Source

- [vktRenderPassClearSomeAttachmentsTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassClearSomeAttachmentsTests.cpp)

## Registration Hierarchy

```text
renderpasses.renderpass1.suballocation.clear_some_attachments
├── clear_only_color
└── clear_only_depth
```

Registered under all rendering types (renderpass1, renderpass2, dynamic_rendering) within the `suballocation` subgroup, monolithic pipeline only. Registered group name: `"clear_some_attachments"` at [vktRenderPassClearSomeAttachmentsTests.cpp#L429](../../../modules/vulkan/renderpass/vktRenderPassClearSomeAttachmentsTests.cpp#L429).

## Role

Implementation file

## Test Families

### clear_only_color — Clear only color attachment

- **Mode**: CLEAR_ONLY_COLOR
- Has a color attachment with loadOp = CLEAR and storeOp = STORE, a depth attachment with loadOp = LOAD and storeOp = STORE, and uses VkRenderPassBeginInfo to clear only the color attachment.

### clear_only_depth — Clear only depth attachment

- **Mode**: CLEAR_ONLY_DEPTH
- Has a depth attachment with loadOp = CLEAR and storeOp = STORE, a color attachment with loadOp = LOAD and storeOp = STORE, and uses VkRenderPassBeginInfo to clear only the depth attachment.

## Parameter Dimensions

| Parameter | Values | Source |
|-----------|--------|--------|
| TestMode | CLEAR_ONLY_COLOR, CLEAR_ONLY_DEPTH | [vktRenderPassClearSomeAttachmentsTests.cpp#L38-L42](../../../modules/vulkan/renderpass/vktRenderPassClearSomeAttachmentsTests.cpp#L38-L42) |
| Color format | VK_FORMAT_R8G8B8A8_UNORM (fixed) | - |
| Depth/stencil format | D24_UNORM_S8_UINT or D32_SFLOAT_S8_UINT (auto-selected) | - |
| Image size | 8x8 (fixed) | - |

## Support Requirements

Defined at [vktRenderPassClearSomeAttachmentsTests.cpp#L409-L417](../../../modules/vulkan/renderpass/vktRenderPassClearSomeAttachmentsTests.cpp#L409-L417):

- VK_KHR_create_renderpass2 for RENDERPASS2
- VK_KHR_dynamic_rendering for DYNAMIC_RENDERING

## Verification Methods

Defined at [vktRenderPassClearSomeAttachmentsTests.cpp#L250-L281](../../../modules/vulkan/renderpass/vktRenderPassClearSomeAttachmentsTests.cpp#L250-L281):

- 4 sample pixels at (0,0), (2,2), (4,4), (6,6) with epsilon 0.05f
- Expected values depend on test mode and which attachment was cleared
