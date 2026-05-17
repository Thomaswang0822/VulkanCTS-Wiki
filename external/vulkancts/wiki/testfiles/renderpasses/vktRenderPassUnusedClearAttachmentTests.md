# vktRenderPassUnusedClearAttachmentTests

## Source

- [vktRenderPassUnusedClearAttachmentTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassUnusedClearAttachmentTests.cpp)

## Registration Hierarchy

```text
renderpasses.renderpass1.suballocation.unused_clear_attachments
```

Registered under all rendering types (renderpass1, renderpass2, dynamic_rendering) within the `suballocation` subgroup, monolithic pipeline only. Registered group name: `"unused_clear_attachments"` at [vktRenderPassUnusedClearAttachmentTests.cpp#L1276](../../../modules/vulkan/renderpass/vktRenderPassUnusedClearAttachmentTests.cpp#L1276).

## Role

Implementation file

## Test Families

### Combination tests

Flat group of leaf test cases with no child subgroups. Test names follow the pattern `<combination>_<dsCase>_<used>`.

- **Definition**: [vktRenderPassUnusedClearAttachmentTests.cpp#L1278-L1339](../../../modules/vulkan/renderpass/vktRenderPassUnusedClearAttachmentTests.cpp#L1278-L1339)

## Parameter Dimensions

| Parameter | Values | Source |
|-----------|--------|--------|
| DepthStencilType | DEPTH_STENCIL_NONE, DEPTH_STENCIL_DEPTH_ONLY, DEPTH_STENCIL_STENCIL_ONLY, DEPTH_STENCIL_BOTH | [vktRenderPassUnusedClearAttachmentTests.cpp#L55-L62](../../../modules/vulkan/renderpass/vktRenderPassUnusedClearAttachmentTests.cpp#L55-L62) |
| Depth/stencil used | {false, true} | - |
| Color attachment counts | 0, 1, 4 | - |
| Color used combinations | All subsets via runCallbackOnCombination | - |

## Support Requirements

Defined at [vktRenderPassUnusedClearAttachmentTests.cpp#L271-L287](../../../modules/vulkan/renderpass/vktRenderPassUnusedClearAttachmentTests.cpp#L271-L287):

- VK_KHR_create_renderpass2 for RENDERPASS2
- VK_KHR_dynamic_rendering for DYNAMIC_RENDERING
- Format support checks

## Verification Methods

Defined at [vktRenderPassUnusedClearAttachmentTests.cpp#L1140-L1234](../../../modules/vulkan/renderpass/vktRenderPassUnusedClearAttachmentTests.cpp#L1140-L1234):

- Per-pixel color comparison with tolerance 0.01f
- Depth: tolerance 0.001f
- Stencil: exact comparison
