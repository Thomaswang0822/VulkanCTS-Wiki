# vktRenderPassUnusedAttachmentTests

## Source

- [vktRenderPassUnusedAttachmentTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentTests.cpp)

## Registration Hierarchy

```text
renderpasses.renderpass1.suballocation.unused_attachment
├── loadopclear
├── loadopdontcare
└── loadopload
```

Evidence:
- `unused_attachment` group created at [`createRenderPassUnusedAttachmentTests()`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentTests.cpp#L1223)
- Direct children are per-load-op subgroups added from [vktRenderPassUnusedAttachmentTests.cpp#L1239-L1286](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentTests.cpp#L1239-L1286)

Note: The representative root uses `renderpass1`; the same topic group also appears under `renderpass2` and `dynamic_rendering` (with some exclusions for DONT_CARE ops).

## Role

Implementation file

## Test Families

### loadopclear — Unused attachment tests with LOAD_OP_CLEAR

Tests unused attachments when the load operation is `VK_ATTACHMENT_LOAD_OP_CLEAR`. Each test configures a combination of store op, stencil load op, and stencil store op for the unused attachment.

- **Pattern**: `loadopclear/storeop<OP>/stencilloadop<OP>/stencilstoreop<OP>`
- **Definition**: [vktRenderPassUnusedAttachmentTests.cpp#L1239-L1286](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentTests.cpp#L1239-L1286)

### loadopdontcare — Unused attachment tests with LOAD_OP_DONT_CARE

Tests unused attachments when the load operation is `VK_ATTACHMENT_LOAD_OP_DONT_CARE`. Each test configures a combination of store op, stencil load op, and stencil store op for the unused attachment.

- **Pattern**: `loadopdontcare/storeop<OP>/stencilloadop<OP>/stencilstoreop<OP>`
- **Definition**: [vktRenderPassUnusedAttachmentTests.cpp#L1239-L1286](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentTests.cpp#L1239-L1286)
- Excluded for `RENDERING_TYPE_DYNAMIC_RENDERING` (DONT_CARE load/store ops skipped)

### loadopload — Unused attachment tests with LOAD_OP_LOAD

Tests unused attachments when the load operation is `VK_ATTACHMENT_LOAD_OP_LOAD`. Each test configures a combination of store op, stencil load op, and stencil store op for the unused attachment.

- **Pattern**: `loadopload/storeop<OP>/stencilloadop<OP>/stencilstoreop<OP>`
- **Definition**: [vktRenderPassUnusedAttachmentTests.cpp#L1239-L1286](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentTests.cpp#L1239-L1286)

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
