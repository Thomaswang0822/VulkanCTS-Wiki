# vktRenderPassUnusedAttachmentSparseFillingTests

## Source

- [vktRenderPassUnusedAttachmentSparseFillingTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp)

## Registration Hierarchy

```text
renderpasses.renderpass1.suballocation.attachment_sparse_filling
├── input_attachment_1
├── input_attachment_3
├── input_attachment_7
├── input_attachment_15
├── input_attachment_31
├── input_attachment_63
└── input_attachment_127
```

Evidence:
- `attachment_sparse_filling` group created at [`createRenderPassUnusedAttachmentSparseFillingTests()`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L1051)
- Direct children added from [vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L1053-L1061](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L1053-L1061)

Note: The representative root uses `renderpass1`; the same topic group also appears under `renderpass2` and `dynamic_rendering`.

## Role

Implementation file

## Test Families

### input_attachment_1 — Sparse filling with 1 active input attachment

Tests that sparse filling of input attachment descriptors works correctly with 1 active input attachment out of 2 total attachments.

- **Definition**: [vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L1053-L1061](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L1053-L1061)

### input_attachment_3 — Sparse filling with 3 active input attachments

Tests that sparse filling of input attachment descriptors works correctly with 3 active input attachments out of 6 total attachments.

- **Definition**: [vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L1053-L1061](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L1053-L1061)

### input_attachment_7 — Sparse filling with 7 active input attachments

Tests that sparse filling of input attachment descriptors works correctly with 7 active input attachments out of 14 total attachments.

- **Definition**: [vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L1053-L1061](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L1053-L1061)

### input_attachment_15 — Sparse filling with 15 active input attachments

Tests that sparse filling of input attachment descriptors works correctly with 15 active input attachments out of 30 total attachments.

- **Definition**: [vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L1053-L1061](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L1053-L1061)

### input_attachment_31 — Sparse filling with 31 active input attachments

Tests that sparse filling of input attachment descriptors works correctly with 31 active input attachments out of 62 total attachments.

- **Definition**: [vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L1053-L1061](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L1053-L1061)

### input_attachment_63 — Sparse filling with 63 active input attachments

Tests that sparse filling of input attachment descriptors works correctly with 63 active input attachments out of 126 total attachments.

- **Definition**: [vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L1053-L1061](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L1053-L1061)

### input_attachment_127 — Sparse filling with 127 active input attachments

Tests that sparse filling of input attachment descriptors works correctly with 127 active input attachments out of 254 total attachments.

- **Definition**: [vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L1053-L1061](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L1053-L1061)

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
