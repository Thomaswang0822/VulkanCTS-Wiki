# vktPipelinePushDescriptorTests.cpp

## Overview

[`vktPipelinePushDescriptorTests.cpp`](../../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp#L1) implements the [`push_descriptor`](../../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp#L4810) topic group. It verifies `VK_KHR_push_descriptor` functionality across all descriptor types in both graphics and compute pipelines, including incremental updates and maintenance5/6 features.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelinePushDescriptorTests.cpp`](../../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp#L1)
- Header: [`vktPipelinePushDescriptorTests.hpp`](../../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.hpp#L1)
- Shared helpers: [`ReferenceRenderer`](../../../modules/vulkan/pipeline/vktPipelineReferenceRenderer.cpp#L1)

## Registration Hierarchy

```text
pipeline.monolithic.push_descriptor
├── graphics
└── compute (monolithic only)
```

**Variant coverage**: All variants. The `compute` subgroup is monolithic only. Input attachments are excluded for shader object (not supported with dynamic rendering).

## Test Families

### graphics — Graphics pipeline push descriptors

Verifies push descriptors with all descriptor types in graphics pipelines. Leaf tests follow the naming pattern `binding<N>_numcalls<M>_<descriptor_type>` where descriptor types include:

- **Buffer types**: uniform_buffer, storage_buffer (using `PushDescriptorBufferGraphicsTest`)
- **Image types**: combined_image_sampler, sampler, sampled_image, storage_image (using `PushDescriptorImageGraphicsTest`)
- **Texel buffer types**: uniform_texel_buffer, storage_texel_buffer (using `PushDescriptorTexelBufferGraphicsTest`)
- **Input attachment**: input_attachment (using `PushDescriptorInputAttachmentGraphicsTest`, excluded for shader object)

Additionally includes maintenance5 tests (monolithic only):
- `maintenance5_uniform_texel_buffer`
- `maintenance5_storage_texel_buffer`
- `maintenance5_uniform_buffer`

### compute — Compute pipeline push descriptors (monolithic only)

Verifies push descriptors with all descriptor types in compute pipelines. Leaf tests follow the same naming pattern as graphics. Additionally includes incremental update tests:

- `incremental_updates`: Verifies incremental push descriptor updates (push, update, push again)
- `incremental_updates_template`: Same as above using `VkDescriptorUpdateTemplateKHR`
- `incremental_updates_2`: Incremental updates using `vkCmdPushDescriptorSet2KHR`
- `incremental_updates_template_2`: Template-based incremental updates using `vkCmdPushDescriptorSet2KHR`

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| descriptorType | VkDescriptorType | 9 types: UBO, SSBO, combined image sampler, sampler, sampled image, storage image, uniform texel buffer, storage texel buffer, input attachment |
| binding | uint32_t | 0, 1, 3 |
| numCalls | uint32_t | 1, 2, 128 (storage buffer compute only) |
| useMaintenance5 | bool | true, false |
| useMaintenance6 | bool | true, false |

## Support / Feature Requirements

| Requirement | Condition |
|---|---|
| `VK_KHR_push_descriptor` | Always |
| `VK_KHR_maintenance5` | When `useMaintenance5 == true` |
| `VK_KHR_maintenance6` | When `useMaintenance6 == true` |
| Pipeline library extensions | When construction type is Library |
| `VK_EXT_shader_object` + features | When construction type is Shader Object |

## Verification Methods

- **Graphics**: `tcu::intThresholdPositionDeviationCompare()` against reference renderer (threshold UVec4(2,2,2,2))
- **Compute**: Direct SSBO output buffer comparison using `deMemCmp()`
- **Incremental updates**: SSBO value comparison against expected UBO+SSBO data
