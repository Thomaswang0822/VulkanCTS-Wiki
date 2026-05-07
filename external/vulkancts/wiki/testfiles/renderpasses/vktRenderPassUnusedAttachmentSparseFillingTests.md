# vktRenderPassUnusedAttachmentSparseFillingTests

## Source

- [vktRenderPassUnusedAttachmentSparseFillingTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp)

## Registration

- **Path**: Added to `suballocation` subgroup within each top-level group
- **Registered group name**: `"attachment_sparse_filling"` at [vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L1051](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L1051)

## Role

Implementation file

## Test Families

### Input attachment sparse filling

- **Pattern**: `input_attachment_<N>` for N in {1, 3, 7, 15, 31, 63, 127}
- **Definition**: [vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L1053-L1061](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L1053-L1061)

## Test Hierarchy

```
attachment_sparse_filling
|-- input_attachment_1
|-- input_attachment_3
|-- input_attachment_7
|-- input_attachment_15
|-- input_attachment_31
|-- input_attachment_63
+-- input_attachment_127
```

## Parameter Dimensions

| Parameter | Values | Source |
|-----------|--------|--------|
| Active input attachment counts | {1, 3, 7, 15, 31, 63, 127} | [vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L1053-L1061](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L1053-L1061) |
| Total attachment count | 2 * activeInputAttachmentCount | - |

## Support Requirements

Defined at [vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L351-L374](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L351-L374):

- VK_KHR_create_renderpass2 for RENDERPASS2
- VK_KHR_dynamic_rendering_local_read for DYNAMIC_RENDERING
- maxColorAttachments, maxPerStageDescriptorInputAttachments, maxPerStageResources limits

## Verification Methods

Defined at [vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L1017-L1043](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L1017-L1043):

- R32G32_UINT output: both channels must equal activeInputAttachmentCount
- Shader counts total and active attachments; both must match expected
