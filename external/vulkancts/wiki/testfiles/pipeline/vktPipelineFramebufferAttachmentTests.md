# vktPipelineFramebufferAttachmentTests.cpp

## Overview

[`vktPipelineFramebufferAttachmentTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineFramebufferAttachmentTests.cpp#L1) implements the [`framebuffer_attachment`](../../../modules/vulkan/pipeline/vktPipelineFramebufferAttachmentTests.cpp#L2104) topic group. It verifies framebuffer attachment behavior including size-mismatched attachments, no-attachment rendering, unused attachments, different attachment sizes, and feedback loop scenarios.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineFramebufferAttachmentTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineFramebufferAttachmentTests.cpp#L1)
- Header: [`vktPipelineFramebufferAttachmentTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineFramebufferAttachmentTests.hpp#L1)

## Registration Hierarchy

```text
pipeline.monolithic.framebuffer_attachment
```

All test cases are registered directly under this group as leaf tests (no intermediate subgroups). Test names follow patterns such as `{viewtype}_{sizeString}`, `no_attachments`, `unused_attachment`, `diff_attachments_{1d|2d}_{sizeString}`, `resolve_input_same_attachment`, and `multi_attachments_not_exported_{2d}_{sizeString}`.

## Test Families

### Size-mismatch attachments

Renders to framebuffer with attachment images strictly larger than the render area. 6 view types x 4 size ratios x single/multi-sample. Test names follow the pattern `{viewtype}_{sizeString}` with optional `_ms` suffix for multisample variants.

### No attachments

Renders with zero color attachments; fragment shader writes via `imageStore()` to a storage image. Test names: `no_attachments` and `no_attachments_ms`.

### Unused attachment

Creates render pass with VK_ATTACHMENT_UNUSED color attachment reference. Pass-by-completion. Monolithic and shader_object_unlinked_spirv only. Test name: `unused_attachment`.

### Different attachment sizes

Multiple color attachments (3) with different sizes. Verifies no leaking between render target clears. Test names follow the pattern `diff_attachments_{1d|2d}_{sizeString}` with optional `_ms` suffix.

### Resolve + input same attachment

Uses same image as both input attachment and resolve target. Not supported with shader object / dynamic rendering. Test name: `resolve_input_same_attachment`.

### Multi-attachments not exported

Multiple attachments where some are not declared in the fragment shader. Verifies unused attachments retain their clear color. Test names follow the pattern `multi_attachments_not_exported_{2d}_{sizeString}` with optional `_ms` suffix.

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| VkImageViewType | Loop | 6 types (1d through cube_array) |
| Size ratios | Array | 4 ratios (32vs64, 32vs48, 32vs39, 19vs32) |
| Multisample | bool | single-sample, multi-sample (4x) |
| MultiAttachmentsTestType | [Enum](../../../modules/vulkan/pipeline/vktPipelineFramebufferAttachmentTests.cpp#L75) | NONE, DIFFERENT_SIZES, NOT_EXPORTED |

## Support / Feature Requirements

| Requirement | Condition |
|---|---|
| `DEVICE_CORE_FEATURE_FRAGMENT_STORES_AND_ATOMICS` | No-attachment cases |
| `geometryShader` or `tessellationShader` | No-attachment (uses gl_PrimitiveID) |
| `DEVICE_CORE_FEATURE_SAMPLE_RATE_SHADING` | Multisample no-attachment (uses gl_SampleID) |

## Verification Methods

- **Size-mismatch, no-attachments, different-sizes, not-exported**: `tcu::intThresholdCompare` with threshold UVec4(1) ([line 650](../../../modules/vulkan/pipeline/vktPipelineFramebufferAttachmentTests.cpp#L650))
- **Unused attachment**: Pass-by-completion ([line 1782](../../../modules/vulkan/pipeline/vktPipelineFramebufferAttachmentTests.cpp#L1782))
