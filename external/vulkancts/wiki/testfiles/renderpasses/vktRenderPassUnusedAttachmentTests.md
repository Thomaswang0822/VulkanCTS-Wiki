# vktRenderPassUnusedAttachmentTests

## Source

- [vktRenderPassUnusedAttachmentTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentTests.cpp)

## Registration

- **Path**: Added to `suballocation` subgroup within each top-level group
- **Registered group name**: `"unused_attachment"` at [vktRenderPassUnusedAttachmentTests.cpp#L1223](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentTests.cpp#L1223)

## Role

Implementation file

## Test Families

### Load/store op combinations

- **Pattern**: `loadop<OP>/storeop<OP>/stencilloadop<OP>/stencilstoreop<OP>`
- **Definition**: [vktRenderPassUnusedAttachmentTests.cpp#L1239-L1286](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentTests.cpp#L1239-L1286)

## Test Hierarchy

```
unused_attachment
+-- loadop<OP>
    +-- storeop<OP>
        +-- stencilloadop<OP>
            +-- stencilstoreop<OP>
```

## Parameter Dimensions

| Parameter | Values | Source |
|-----------|--------|--------|
| Load ops | {LOAD, CLEAR, DONT_CARE} | [vktRenderPassUnusedAttachmentTests.cpp#L1225](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentTests.cpp#L1225) |
| Store ops | {STORE, DONT_CARE} | [vktRenderPassUnusedAttachmentTests.cpp#L1228](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentTests.cpp#L1228) |
| Stencil load/store ops | Same ranges as above | - |

Note: Dynamic rendering starts stencil ops at DONT_CARE and skips DONT_CARE load/store ops.

## Support Requirements

Defined at [vktRenderPassUnusedAttachmentTests.cpp#L367-L375](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentTests.cpp#L367-L375):

- VK_KHR_create_renderpass2 for RENDERPASS2
- VK_KHR_dynamic_rendering_local_read for DYNAMIC_RENDERING

## Verification Methods

Defined at [vktRenderPassUnusedAttachmentTests.cpp#L1132-L1185](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentTests.cpp#L1132-L1185):

- Unused image: every pixel must match (0.1, 0.2, 0.3, 0.4) with tolerance 0.01
- Rendered image: center pixel must match (0.4, 0.6, 0.2, 1.0) with tolerance 0.01
- Exception: dynamic rendering with LOAD_OP_CLEAR + STORE_OP_STORE uses (0.5, 0.5, 0.5, 1.0)
