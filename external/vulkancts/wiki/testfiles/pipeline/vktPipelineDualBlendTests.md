# vktPipelineDualBlendTests.cpp

## Overview

[`vktPipelineDualBlendTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineDualBlendTests.cpp#L1) implements the [`multi_attachments`](../../../modules/vulkan/pipeline/vktPipelineDualBlendTests.cpp#L1762) nested subgroup under the `dual_source` group of the pipeline category. It verifies dual-source blending across 4 simultaneous color attachments, comparing dual-source blend results against a generic (non-dual-source) reference pipeline.

## Role

Implementation file. Nested subgroup under [`vktPipelineBlendTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineBlendTests.cpp#L1).

## Source Code

- Primary source: [`vktPipelineDualBlendTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineDualBlendTests.cpp#L1)
- Header: [`vktPipelineDualBlendTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineDualBlendTests.hpp#L1)
- Shared blend support: [`vktPipelineBlendTestsCommon.cpp`](../../../modules/vulkan/pipeline/vktPipelineBlendTestsCommon.cpp#L1)

## Registration Path

This file contributes the subgroup created by [`addDualBlendMultiAttachmentTests()`](../../../modules/vulkan/pipeline/vktPipelineDualBlendTests.cpp#L1), which is called by [`createBlendTests()`](../../../modules/vulkan/pipeline/vktPipelineBlendTests.cpp#L2989) and added under the `dual_source` group. The full registration path is `pipeline.<variant>.blend.dual_source.multi_attachments`.

**Variant coverage**: All variants (via parent blend group). Non-VulkanSC only.

## Test Hierarchy

```text
dual_source                              (parent: vktPipelineBlendTests.cpp)
└── multi_attachments
    ├── r4g4_unorm_pack8
    ├── r4g4b4a4_unorm_pack16
    ├── r5g6b5_unorm_pack16
    ├── ...                               (all formats from getBlendFormats())
    └── r10x6g10x6b10x6a10x6_unorm_4pack16
```

Source: [`addDualBlendMultiAttachmentTests()`](../../../modules/vulkan/pipeline/vktPipelineDualBlendTests.cpp#L1).

## Test Families

### 1. multi_attachments

Tests dual-source blending across 4 simultaneous color attachments. Each test case corresponds to one blendable format. Internally, each case iterates over many blend-state combinations (src/dst color/alpha factors and blend ops) to verify that dual-source blending on attachment 0 produces results consistent with a generic (non-dual-source) pipeline rendering to all 4 attachments.

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| VkFormat | [`getBlendFormats()`](../../../modules/vulkan/pipeline/vktPipelineBlendTestsCommon.cpp#L42) | ~38 non-integer, uncompressed formats |
| PipelineConstructionType | Factory parameter | Monolithic, fast-linked library, or shader object |
| DualSourceFlags (blend mask) | [`BlendAttachmentStateGenerator`](../../../modules/vulkan/pipeline/vktPipelineDualBlendTests.cpp#L954) | Fixed to `dstColorFactor \| dstAlphaFactor` |
| Blend factors | [`getBlendFactors()`](../../../modules/vulkan/pipeline/vktPipelineDualBlendTests.cpp#L72) | All VkBlendFactor values with SRC1 substitutions |
| Blend ops | [`getBlendOps()`](../../../modules/vulkan/pipeline/vktPipelineDualBlendTests.cpp#L136) | All VkBlendOp values (add, sub, rsub, min, max) |
| ATTACHMENT_COUNT | Constant | 4 color attachments |

## Support / Feature Requirements

| Requirement | Where | Line |
|---|---|---|
| `dualSrcBlend` device feature | `checkSupport` | [883](../../../modules/vulkan/pipeline/vktPipelineDualBlendTests.cpp#L883) |
| `independentBlend` device feature | Device creation | [1714](../../../modules/vulkan/pipeline/vktPipelineDualBlendTests.cpp#L1714) |
| `maxFragmentOutputAttachments` >= 4 | `checkSupport` | [877](../../../modules/vulkan/pipeline/vktPipelineDualBlendTests.cpp#L877) |
| `VK_EXT_shader_object` (shader object variant) | `checkSupport` | [888](../../../modules/vulkan/pipeline/vktPipelineDualBlendTests.cpp#L888) |
| `VK_EXT_color_write_enable` (shader object variant) | `checkSupport` | [889](../../../modules/vulkan/pipeline/vktPipelineDualBlendTests.cpp#L889) |
| Supported blend format | `checkSupport` | [894](../../../modules/vulkan/pipeline/vktPipelineDualBlendTests.cpp#L894) |
| Supported transfer format | `checkSupport` | [897](../../../modules/vulkan/pipeline/vktPipelineDualBlendTests.cpp#L897) |
| Pipeline construction requirements | `checkSupport` | [873](../../../modules/vulkan/pipeline/vktPipelineDualBlendTests.cpp#L873) |

## Verification Methods

**Cross-pipeline comparison** strategy ([line 1249](../../../modules/vulkan/pipeline/vktPipelineDualBlendTests.cpp#L1249)):

1. **Generic pipeline draw**: Renders to all 4 attachments using non-dual-source blend factors (SRC1 factors replaced with SRC equivalents). Results stored in `m_genericAttachments` buffers.

2. **Dual-source pipeline draw**: Renders to only attachment 0 using actual dual-source blend factors (SRC1_COLOR/SRC1_ALPHA). Results stored in `m_dualAttachments` buffers.

3. **Buffer comparison** ([`compareBuffers`](../../../modules/vulkan/pipeline/vktPipelineDualBlendTests.cpp#L1619)): Pixel-by-pixel comparison using `tcu::ConstPixelBufferAccess` with format-aware threshold. For each pixel, absolute per-channel difference must be below threshold.

4. **Zero-buffer check** ([`isBufferZero`](../../../modules/vulkan/pipeline/vktPipelineDualBlendTests.cpp#L1611)): If the destination buffer is all zeros after the generic draw, the iteration is skipped with `QUALITY_WARNING` because the blend state yields zero.

## Test Principles Observed

- **Cross-pipeline equivalence**: Dual-source results are verified by comparing against a generic pipeline that produces the same mathematical result without dual-source blending
- **Multi-attachment coverage**: Tests 4 simultaneous attachments to verify dual-source blending works correctly in the presence of multiple render targets
- **Zero-result detection**: Skips trivially-zero blend states with a quality warning rather than reporting a false pass

## Notes / Uncertainties

- This file is guarded by `#ifndef CTS_USES_VULKANSC` in the parent
- The `independentBlend` feature is required for the multi-attachment test setup
