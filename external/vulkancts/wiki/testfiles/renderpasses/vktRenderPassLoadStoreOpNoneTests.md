# vktRenderPassLoadStoreOpNoneTests

## Source

[vktRenderPassLoadStoreOpNoneTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassLoadStoreOpNoneTests.cpp)

## Registration

Added to `suballocation` subgroup (non-SC).

Registered group name: `"load_store_op_none"` ([L1534](../../../modules/vulkan/renderpass/vktRenderPassLoadStoreOpNoneTests.cpp#L1534))

## Test Families

```
load_store_op_none
+-- LoadStoreOpNoneTest
    Tests VK_ATTACHMENT_LOAD_OP_NONE_EXT / VK_ATTACHMENT_STORE_OP_NONE_EXT
    behavior with various attachment configurations.
    +-- Color attachment tests
    |   Various load/store op combinations for color attachments.
    +-- Depth/stencil tests
        Separate depth/stencil load/store op combinations with
        test enable/disable variants.
```

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
