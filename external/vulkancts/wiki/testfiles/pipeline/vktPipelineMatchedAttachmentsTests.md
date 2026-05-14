# vktPipelineMatchedAttachmentsTests.cpp

## Overview

[`vktPipelineMatchedAttachmentsTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMatchedAttachmentsTests.cpp#L1) implements the [`matched_attachments`](../../../modules/vulkan/pipeline/vktPipelineMatchedAttachmentsTests.cpp#L257) topic group. It verifies pipeline creation with matched input and color attachments (same image, different layout references) does not crash.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineMatchedAttachmentsTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMatchedAttachmentsTests.cpp#L1)
- Header: [`vktPipelineMatchedAttachmentsTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineMatchedAttachmentsTests.hpp#L1)

## Registration Hierarchy

```text
pipeline.monolithic.matched_attachments
├── cache
└── no_cache
```

## Test Families

### cache — Matched attachments with pipeline cache

Creates a graphics pipeline with a render pass that has two matched attachments (one color, one input) and verifies pipeline creation succeeds without crash. Uses a pipeline cache.

### no_cache — Matched attachments without pipeline cache

Creates a graphics pipeline with a render pass that has two matched attachments (one color, one input) and verifies pipeline creation succeeds without crash. Does not use a pipeline cache.

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| usePipelineCache | bool | true (cache), false (no_cache) |

## Verification Methods

Pass-by-completion: test passes as long as `createGraphicsPipeline` did not crash ([line 234](../../../modules/vulkan/pipeline/vktPipelineMatchedAttachmentsTests.cpp#L234)).

## Notes / Uncertainties

- This is a minimal test file (~260 lines) targeting a specific regression scenario
- No pixel-level verification; only verifies pipeline creation succeeds
- Input attachments are not supported with dynamic rendering, so these tests are excluded for shader-object variants
