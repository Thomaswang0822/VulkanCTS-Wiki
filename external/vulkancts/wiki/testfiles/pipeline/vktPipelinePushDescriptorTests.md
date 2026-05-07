# vktPipelinePushDescriptorTests.cpp

## Overview

[`vktPipelinePushDescriptorTests.cpp`](../../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp#L1) implements the [`push_descriptor`](../../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp#L4810) topic group. It verifies `VK_KHR_push_descriptor` functionality across all descriptor types in both graphics and compute pipelines, including incremental updates and maintenance5/6 features.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelinePushDescriptorTests.cpp`](../../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp#L1)
- Header: [`vktPipelinePushDescriptorTests.hpp`](../../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.hpp#L1)
- Shared helpers: [`ReferenceRenderer`](../../../modules/vulkan/pipeline/vktPipelineReferenceRenderer.cpp#L1)

## Registration Path

[`createPushDescriptorTests()`](../../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp#L4770) returns the `push_descriptor` group, attached under each variant root by `createChildren()`.

**Variant coverage**: All variants (VulkanSC only for push_descriptor). Compute sub-group is monolithic only. Input attachments excluded for shader object.

## Test Hierarchy

```text
push_descriptor
├── graphics
│   ├── binding<N>_numcalls<M>_<descriptor_type>   (buffer, image, texel buffer, input attachment)
│   ├── maintenance5_uniform_texel_buffer           (monolithic only)
│   ├── maintenance5_storage_texel_buffer           (monolithic only)
│   └── maintenance5_uniform_buffer                 (monolithic only)
└── compute                                         (monolithic only)
    ├── binding<N>_numcalls<M>_<descriptor_type>
    ├── incremental_updates                         (monolithic only)
    ├── incremental_updates_template                (monolithic only)
    ├── incremental_updates_2                       (monolithic only)
    └── incremental_updates_template_2              (monolithic only)
```

## Test Families

### 1. Buffer Graphics / Compute

Verifies push descriptors with uniform/storage buffers. Graphics uses reference renderer comparison; compute uses direct SSBO comparison.

### 2. Image Graphics / Compute

Verifies push descriptors with combined image sampler, sampler, sampled image, and storage image types.

### 3. Texel Buffer Graphics / Compute

Verifies push descriptors with uniform/storage texel buffers.

### 4. Input Attachment Graphics

Verifies push descriptors with input attachments in graphics pipelines. Excluded for shader object (not supported with dynamic rendering).

### 5. Incremental Updates Compute

Verifies incremental push descriptor updates (push, update, push again) in compute pipelines. Includes template and maintenance6 variants.

### 6. Maintenance5

Tests VK_KHR_maintenance5 features with push descriptors. Monolithic only.

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
