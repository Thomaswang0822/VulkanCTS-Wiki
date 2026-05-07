# vktRenderPassSubpassMergeFeedbackTests

## Source

[vktRenderPassSubpassMergeFeedbackTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassSubpassMergeFeedbackTests.cpp)

## Registration

Added to renderpass2 suballocation subgroup (non-SC).

Registered group name: `"subpass_merge_feedback"` ([line 352](../../../modules/vulkan/renderpass/vktRenderPassSubpassMergeFeedbackTests.cpp#L352))

## Test Families

```
subpass_merge_feedback
|-- SubpassMergeFeedbackTest
    |-- single_subpass
    |-- single_subpass_disallow_renderpass_merge
    |-- three_subpasses
    |-- three_subpasses_disallow_renderpass_merge
    |-- three_subpasses_disallow_subpass_merge
    |-- many_subpasses
```

### SubpassMergeFeedbackTest

Tests VK_EXT_subpass_merge_feedback by verifying merge status feedback ([lines 354-413](../../../modules/vulkan/renderpass/vktRenderPassSubpassMergeFeedbackTests.cpp#L354-L413)).

**Parameter Dimensions:**

| Case | Description |
|---|---|
| single_subpass | 1 subpass, no disallow |
| single_subpass_disallow_renderpass_merge | 1 subpass, renderpass merge disallowed |
| three_subpasses | 3 subpasses, no disallow |
| three_subpasses_disallow_renderpass_merge | 3 subpasses, renderpass merge disallowed |
| three_subpasses_disallow_subpass_merge | 3 subpasses, subpass 1 merge disallowed |
| many_subpasses | 32 subpasses |

**Verification** ([lines 267-327](../../../modules/vulkan/renderpass/vktRenderPassSubpassMergeFeedbackTests.cpp#L267-L327)):

- When disallow: `postMergeSubpassCount` equals original, each subpass has `VK_SUBPASS_MERGE_STATUS_DISALLOWED_EXT`
- When allowed: `postMergeSubpassCount` <= `subpassCount`, single subpass has `NOT_MERGED_SINGLE_SUBPASS`, merged subpasses share `postMergeIndex`

## Support Requirements

| Requirement | Context |
|---|---|
| RENDERING_TYPE_RENDERPASS2 | Only runs for this rendering type; returns nullptr otherwise ([line 347](../../../modules/vulkan/renderpass/vktRenderPassSubpassMergeFeedbackTests.cpp#L347)) |
| VK_EXT_subpass_merge_feedback | Implicitly required |
