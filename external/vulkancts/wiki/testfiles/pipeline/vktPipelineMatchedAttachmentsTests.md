# vktPipelineMatchedAttachmentsTests.cpp

## Overview

[`vktPipelineMatchedAttachmentsTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMatchedAttachmentsTests.cpp#L1) implements the [`matched_attachments`](../../../modules/vulkan/pipeline/vktPipelineMatchedAttachmentsTests.cpp#L257) topic group. It verifies pipeline creation with matched input and color attachments (same image, different layout references) does not crash.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineMatchedAttachmentsTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMatchedAttachmentsTests.cpp#L1)
- Header: [`vktPipelineMatchedAttachmentsTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineMatchedAttachmentsTests.hpp#L1)

## Registration Path

[`createMatchedAttachmentsTests()`](../../../modules/vulkan/pipeline/vktPipelineMatchedAttachmentsTests.cpp#L1) returns the `matched_attachments` group, attached under each variant root by `createChildren()`.

**Variant coverage**: All variants (VulkanSC only). Excluded for shader object (input attachments not supported with dynamic rendering).

## Test Hierarchy

```text
matched_attachments
├── cache                  (with pipeline cache)
└── no_cache               (without pipeline cache)
```

## Test Families

### 1. cache / no_cache

Creates a graphics pipeline with a render pass that has two matched attachments (one color, one input) and verifies pipeline creation succeeds without crash. Tests both with and without pipeline cache.

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| usePipelineCache | bool | true (cache), false (no_cache) |

## Verification Methods

Pass-by-completion: test passes as long as `createGraphicsPipeline` did not crash ([line 234](../../../modules/vulkan/pipeline/vktPipelineMatchedAttachmentsTests.cpp#L234)).

## Notes / Uncertainties

- This is a minimal test file (~260 lines) targeting a specific regression scenario
- No pixel-level verification; only verifies pipeline creation succeeds
