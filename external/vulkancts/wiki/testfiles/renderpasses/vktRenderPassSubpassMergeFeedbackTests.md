# vktRenderPassSubpassMergeFeedbackTests

## Source

[vktRenderPassSubpassMergeFeedbackTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassSubpassMergeFeedbackTests.cpp)

## Registration Hierarchy

```text
renderpasses.renderpass2.suballocation.subpass_merge_feedback
├── single_subpass
├── single_subpass_disallow_renderpass_merge
├── three_subpasses
├── three_subpasses_disallow_renderpass_merge
├── three_subpasses_disallow_subpass_merge
└── many_subpasses
```

Registered under `renderpasses.renderpass2.suballocation` only via [`createRenderPassSubpassMergeFeedbackTests`](../../../modules/vulkan/renderpass/vktRenderPassSubpassMergeFeedbackTests.cpp#L343). Added to `suballocationTestGroup` at [L8510](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8510). Returns `nullptr` for all other rendering types ([L346](../../../modules/vulkan/renderpass/vktRenderPassSubpassMergeFeedbackTests.cpp#L346)).

## Test Families

### single_subpass — Single subpass, no disallow

1 subpass with no merge disallow flags. Verifies merge status feedback for the simplest case ([L354-L362](../../../modules/vulkan/renderpass/vktRenderPassSubpassMergeFeedbackTests.cpp#L354-L362)).

### single_subpass_disallow_renderpass_merge — Single subpass, renderpass merge disallowed

1 subpass with renderpass merge disallowed. Verifies that `postMergeSubpassCount` equals original and the subpass has `VK_SUBPASS_MERGE_STATUS_DISALLOWED_EXT` ([L364-L372](../../../modules/vulkan/renderpass/vktRenderPassSubpassMergeFeedbackTests.cpp#L364-L372)).

### three_subpasses — Three subpasses, no disallow

3 subpasses with no merge disallow flags. Verifies merge feedback with multiple subpasses ([L374-L382](../../../modules/vulkan/renderpass/vktRenderPassSubpassMergeFeedbackTests.cpp#L374-L382)).

### three_subpasses_disallow_renderpass_merge — Three subpasses, renderpass merge disallowed

3 subpasses with renderpass merge disallowed. Verifies that `postMergeSubpassCount` equals original and each subpass has `VK_SUBPASS_MERGE_STATUS_DISALLOWED_EXT` ([L384-L392](../../../modules/vulkan/renderpass/vktRenderPassSubpassMergeFeedbackTests.cpp#L384-L392)).

### three_subpasses_disallow_subpass_merge — Three subpasses, subpass 1 merge disallowed

3 subpasses with subpass 1 merge disallowed. Verifies that the disallowed subpass retains its identity while others may merge ([L394-L402](../../../modules/vulkan/renderpass/vktRenderPassSubpassMergeFeedbackTests.cpp#L394-L402)).

### many_subpasses — 32 subpasses

32 subpasses with no disallow flags. Stress test for merge feedback with many subpasses ([L404-L412](../../../modules/vulkan/renderpass/vktRenderPassSubpassMergeFeedbackTests.cpp#L404-L412)).

**Verification** (applies to all cases, [lines 267-327](../../../modules/vulkan/renderpass/vktRenderPassSubpassMergeFeedbackTests.cpp#L267-L327)):

- When disallow: `postMergeSubpassCount` equals original, each subpass has `VK_SUBPASS_MERGE_STATUS_DISALLOWED_EXT`
- When allowed: `postMergeSubpassCount` <= `subpassCount`, single subpass has `NOT_MERGED_SINGLE_SUBPASS`, merged subpasses share `postMergeIndex`

## Support Requirements

| Requirement | Context |
|---|---|
| RENDERING_TYPE_RENDERPASS2 | Only runs for this rendering type; returns nullptr otherwise ([line 347](../../../modules/vulkan/renderpass/vktRenderPassSubpassMergeFeedbackTests.cpp#L347)) |
| VK_EXT_subpass_merge_feedback | Implicitly required |
