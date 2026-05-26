# vktRenderPassLoadStoreOpNoneTests

## Source

[vktRenderPassLoadStoreOpNoneTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassLoadStoreOpNoneTests.cpp)

## Registration Hierarchy

```text
renderpasses.renderpass1.suballocation.load_store_op_none
```

Available under `renderpass1`, `renderpass2`, and dynamic-rendering `suballocation` subgroups (non-SC). Representative root shown for `renderpass1`. The root registration adds this group to every renderpasses suballocation group outside the rendering-type-specific switch ([vktRenderPassTests.cpp#L8564-L8569](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8564-L8569)); the source file creates the registered group at [L1534](../../../modules/vulkan/renderpass/vktRenderPassLoadStoreOpNoneTests.cpp#L1534).

## Test Families

### load_store_op_none — VK_ATTACHMENT_LOAD_OP_NONE / VK_ATTACHMENT_STORE_OP_NONE tests

Tests VK_ATTACHMENT_LOAD_OP_NONE_EXT / VK_ATTACHMENT_STORE_OP_NONE_EXT behavior with various attachment configurations. 55 test cases covering:

- **Color attachment tests**: Various load/store op combinations for color attachments (`color_load_op_load_store_op_none`, `color_load_op_none_store_op_dontcare`, `color_load_op_none_store_op_none`, `color_load_op_none_store_op_none_resolve`, `color_load_op_none_store_op_none_write_off`, `color_load_op_none_store_op_store`, `color_load_op_none_store_op_store_alphablend`)
- **Depth tests**: Separate depth load/store op combinations across 4 depth formats (D16_UNORM, D24_UNORM_S8_UINT, D32_SFLOAT, D32_SFLOAT_S8_UINT) with variants for load_op_load/store_op_none, load_op_none/store_op_dontcare, load_op_none/store_op_none_write_off, load_op_none/store_op_store
- **Stencil tests**: Separate stencil load/store op combinations across 4 stencil-capable formats with same op variants as depth
- **Depth/stencil combined tests**: Separate depth/stencil load/store op combinations with test enable/disable variants (stencil_test_off, stencil_write_off, depth_test_off, depth_write_off) across 3 combined depth/stencil formats

## Parameter Dimensions

| Dimension | Values |
|-----------|--------|
| Color load/store ops | NONE, LOAD, CLEAR, DONT_CARE combinations |
| Depth/stencil load/store ops | Separate depth/stencil ops with test enable/disable variants |
| Extension preference | KHR vs EXT alternating by format index |

## Support Requirements

| Requirement | Condition |
|-------------|-----------|
| VK_EXT_load_store_op_none or VK_KHR_load_store_op_none | Always ([L460-L468](../../../modules/vulkan/renderpass/vktRenderPassLoadStoreOpNoneTests.cpp#L460-L468)) |
| VK_KHR_create_renderpass2 | For renderpass2 ([L450](../../../modules/vulkan/renderpass/vktRenderPassLoadStoreOpNoneTests.cpp#L450)) |
| VK_KHR_dynamic_rendering | For dynamic rendering ([L455](../../../modules/vulkan/renderpass/vktRenderPassLoadStoreOpNoneTests.cpp#L455)) |
| VK_KHR_dynamic_rendering_local_read | When multiple subpasses ([L457](../../../modules/vulkan/renderpass/vktRenderPassLoadStoreOpNoneTests.cpp#L457)) |

## Verification

| Aspect | Method |
|--------|--------|
| LOAD_OP_NONE | Attachment retains pre-initialized values |
| STORE_OP_NONE | Attachment retains pre-render-pass values |
| LOAD_OP_LOAD / STORE_OP_STORE | Expected rendered values |
| Comparisons | tcu::floatThresholdCompare and pixel-level comparisons |
