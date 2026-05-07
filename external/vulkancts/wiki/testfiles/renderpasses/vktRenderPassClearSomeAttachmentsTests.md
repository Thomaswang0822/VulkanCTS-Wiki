# vktRenderPassClearSomeAttachmentsTests

## Source

- [vktRenderPassClearSomeAttachmentsTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassClearSomeAttachmentsTests.cpp)

## Registration

- **Path**: Added to `suballocation` subgroup (monolithic pipeline, secondary CB match)
- **Registered group name**: `"clear_some_attachments"` at [vktRenderPassClearSomeAttachmentsTests.cpp#L429](../../../modules/vulkan/renderpass/vktRenderPassClearSomeAttachmentsTests.cpp#L429)

## Role

Implementation file

## Test Families

### Clear only color

- **Pattern**: `clear_only_color`
- **Mode**: CLEAR_ONLY_COLOR

### Clear only depth

- **Pattern**: `clear_only_depth`
- **Mode**: CLEAR_ONLY_DEPTH

## Test Hierarchy

```
clear_some_attachments
|-- clear_only_color
+-- clear_only_depth
```

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
