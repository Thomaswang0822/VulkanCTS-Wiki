## Overview

**Core question:** Does the implementation return correct subpass-merge feedback when an application requests it through `VK_EXT_subpass_merge_feedback`, with and without merge-disallow controls?

- This page covers the `subpass_merge_feedback` test family implemented in [vktRenderPassSubpassMergeFeedbackTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassSubpassMergeFeedbackTests.cpp).
- The family is registered only under `renderpasses.renderpass2.suballocation.subpass_merge_feedback`, because the test group factory [createRenderPassSubpassMergeFeedbackTests](../../../modules/vulkan/renderpass/vktRenderPassSubpassMergeFeedbackTests.cpp#L343) returns `nullptr` for every rendering type other than `RENDERING_TYPE_RENDERPASS2` ([L346-L349](../../../modules/vulkan/renderpass/vktRenderPassSubpassMergeFeedbackTests.cpp#L346-L349)).
- The factory is attached to the `suballocation` intermediate node in the renderpass2 dispatcher branch of [vktRenderPassTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8508-L8510).
- Each test case creates a render pass with `VK_EXT_subpass_merge_feedback` feedback create-info structures in the `pNext` chain, then reads back the feedback written by the implementation during `vkCreateRenderPass2` and checks it against the expected invariants.
- The test performs no draw calls and runs no shaders. The correctness contract is entirely about the merge-feedback metadata returned at render-pass creation time.

## Background Knowledge

- **Subpass merging.** Some implementations, notably tile-based renderers, can execute two or more render-pass subpasses as a single on-chip pass. The Vulkan specification allows implementations to merge one or more subpasses ([renderpass.adoc](../../../../vulkan-docs/src/chapters/renderpass.adoc#L1845-L1847)). When subpasses are merged, the physical subpass index (the index into the post-merge set) differs from the original subpass index.
- **Merge feedback create-info.** The `VK_EXT_subpass_merge_feedback` extension adds two feedback structures. `VkRenderPassCreationFeedbackCreateInfoEXT` chains off `VkRenderPassCreateInfo2` and reports `postMergeSubpassCount`, the number of physical subpasses after merging. `VkRenderPassSubpassFeedbackCreateInfoEXT` chains off each `VkSubpassDescription2` and reports per-subpass `VkRenderPassSubpassFeedbackInfoEXT`: a `subpassMergeStatus` enum, a description string, and a `postMergeIndex` ([renderpass.adoc](../../../../vulkan-docs/src/chapters/renderpass.adoc#L8298-L8362)).
- **Merge-disallow control.** `VkRenderPassCreationControlEXT` can be chained off either `VkRenderPassCreateInfo2` or `VkSubpassDescription2`. When its `disallowMerging` is `VK_TRUE` on the render pass, the implementation disables merging for the entire render pass. When chained off a subpass, it disables merging that subpass with the previous one ([renderpass.adoc](../../../../vulkan-docs/src/chapters/renderpass.adoc#L8271-L8293)). A subpass blocked this way must report `VK_SUBPASS_MERGE_STATUS_DISALLOWED_EXT`.
- **Merge status values.** Besides `MERGED` and `DISALLOWED`, the implementation may report reasons why a subpass was not merged, such as `NOT_MERGED_SINGLE_SUBPASS` (only one subpass in the render pass) or `NOT_MERGED_UNSPECIFIED` ([renderpass.adoc](../../../../vulkan-docs/src/chapters/renderpass.adoc#L8364-L8415)).

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

All six cases are registered as direct test case leaves under the `subpass_merge_feedback` test family ([L354-L413](../../../modules/vulkan/renderpass/vktRenderPassSubpassMergeFeedbackTests.cpp#L354-L413)). The mustpass lists record the same six leaves under `dEQP-VK.renderpasses.renderpass2.suballocation.subpass_merge_feedback` ([renderpasses.txt](../../../mustpass/main/vk-default/renderpasses.txt#L79568-L79573)).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| `subpassCount` | `1`, `3`, `32` | Controls how many subpasses the render pass contains. One subpass probes the single-subpass invariant; three covers the common multi-subpass case; thirty-two stresses the implementation with many subpasses and feedback structures. | [L358-L410](../../../modules/vulkan/renderpass/vktRenderPassSubpassMergeFeedbackTests.cpp#L358-L410) |
| `disallowMergeRenderpass` | `false`, `true` | When `true`, a `VkRenderPassCreationControlEXT` with `disallowMerging = VK_TRUE` is chained off `VkRenderPassCreateInfo2`, forcing every subpass to report `VK_SUBPASS_MERGE_STATUS_DISALLOWED_EXT`. | [L230-L240](../../../modules/vulkan/renderpass/vktRenderPassSubpassMergeFeedbackTests.cpp#L230-L240) |
| `disallowMergeSubPass1` | `false`, `true` | When `true`, a `VkRenderPassCreationControlEXT` with `disallowMerging = VK_TRUE` is chained off subpass `1` only. Subpass `1` must report `DISALLOWED`; other subpasses may merge. | [L165-L176](../../../modules/vulkan/renderpass/vktRenderPassSubpassMergeFeedbackTests.cpp#L165-L176) |

## Behavior Parameters

The primary behavioral axis is the test case leaf. Each leaf fixes a combination of the three dimensions above, and that combination determines both the merge-control configuration and the verification rule applied to the feedback. The six leaves fall into three groups.

### Merge allowed, no disallow controls

- **`single_subpass`:** One subpass, no disallow flags. Verifies the single-subpass invariant: the sole subpass must report `VK_SUBPASS_MERGE_STATUS_NOT_MERGED_SINGLE_SUBPASS_EXT` and `postMergeSubpassCount` must not exceed the original count ([L267-L327](../../../modules/vulkan/renderpass/vktRenderPassSubpassMergeFeedbackTests.cpp#L267-L327)).
- **`three_subpasses`:** Three subpasses, no disallow flags. Verifies the general invariants for an uncontrolled multi-subpass render pass. Merged subpasses must share a `postMergeIndex` with the previous subpass; non-merged subpasses must have a distinct `postMergeIndex` ([L311-L326](../../../modules/vulkan/renderpass/vktRenderPassSubpassMergeFeedbackTests.cpp#L311-L326)).
- **`many_subpasses`:** Thirty-two subpasses, no disallow flags. Same invariants as `three_subpasses`, applied to a larger render pass to stress feedback-structure handling ([L404-L412](../../../modules/vulkan/renderpass/vktRenderPassSubpassMergeFeedbackTests.cpp#L404-L412)).

### Render-pass-level merge disallow

- **`single_subpass_disallow_renderpass_merge`:** One subpass with `disallowMerging` on the render pass. Verifies that `postMergeSubpassCount` equals the original count, the subpass reports `VK_SUBPASS_MERGE_STATUS_DISALLOWED_EXT`, and its `postMergeIndex` differs from any neighbor ([L267-L287](../../../modules/vulkan/renderpass/vktRenderPassSubpassMergeFeedbackTests.cpp#L267-L287)).
- **`three_subpasses_disallow_renderpass_merge`:** Three subpasses with `disallowMerging` on the render pass. Every subpass must report `DISALLOWED`, `postMergeSubpassCount` must equal the original count, and every adjacent pair must have distinct `postMergeIndex` values ([L267-L287](../../../modules/vulkan/renderpass/vktRenderPassSubpassMergeFeedbackTests.cpp#L267-L287)).

### Subpass-level merge disallow

- **`three_subpasses_disallow_subpass_merge`:** Three subpasses with `disallowMerging` on subpass `1` only. Subpass `1` must report `DISALLOWED`; subpasses `0` and `2` are not controlled and may report `MERGED` or a not-merged reason, subject to the same `postMergeIndex` invariants as the uncontrolled cases ([L302-L326](../../../modules/vulkan/renderpass/vktRenderPassSubpassMergeFeedbackTests.cpp#L302-L326)).

## Shader Analysis

This test has no shaders. No shader code is part of the tested behavior: the test never records a command buffer, never draws, and never dispatches. All validation runs on the host against the feedback structures written during render-pass creation.

## Runtime Execution and Result Checking

The test instance entry point is `SubpassMergeFeedbackTestInstance::iterate`, which calls [createRenderPassAndVerify](../../../modules/vulkan/renderpass/vktRenderPassSubpassMergeFeedbackTests.cpp#L125-L330).

- For each subpass `i` from `0` to `subpassCount - 1`, the host builds an attachment description, a color attachment reference, and an input attachment reference. Subpasses after the first reference the previous subpass's attachment as an input attachment, and a `VkSubpassDependency2` links each consecutive pair ([L138-L228](../../../modules/vulkan/renderpass/vktRenderPassSubpassMergeFeedbackTests.cpp#L138-L228)).
- The host allocates a `VkRenderPassSubpassFeedbackInfoEXT` per subpass, initialized with `subpassMergeStatus = VK_SUBPASS_MERGE_STATUS_MERGED_EXT`, an empty description, and `postMergeIndex = 0` ([L178-L183](../../../modules/vulkan/renderpass/vktRenderPassSubpassMergeFeedbackTests.cpp#L178-L183)). It then chains a `VkRenderPassSubpassFeedbackCreateInfoEXT` off each subpass description, pointing at the per-subpass feedback info and (when needed) at a per-subpass merge-control structure ([L186-L211](../../../modules/vulkan/renderpass/vktRenderPassSubpassMergeFeedbackTests.cpp#L186-L211)).
- A `VkRenderPassCreationControlEXT` with `disallowMerging` is chained off the render-pass create-info when `disallowMergeRenderpass` is set, together with a `VkRenderPassCreationFeedbackCreateInfoEXT` pointing at a single `VkRenderPassCreationFeedbackInfoEXT` ([L230-L262](../../../modules/vulkan/renderpass/vktRenderPassSubpassMergeFeedbackTests.cpp#L230-L262)).
- The render pass is created with `vkCreateRenderPass2` (through `RenderPassCreateInfo2::createRenderPass`). After the call returns, the implementation has written `postMergeSubpassCount` into the render-pass feedback info and a `subpassMergeStatus`, `description`, and `postMergeIndex` into each subpass feedback info ([L264](../../../modules/vulkan/renderpass/vktRenderPassSubpassMergeFeedbackTests.cpp#L264)).
- The host then runs one of two verification branches depending on whether render-pass-level merging was disallowed ([L267-L327](../../../modules/vulkan/renderpass/vktRenderPassSubpassMergeFeedbackTests.cpp#L267-L327)).

| Feedback field | Checked when disallowed | Checked when allowed |
|----------------|-------------------------|----------------------|
| `postMergeSubpassCount` | Must equal original `subpassCount` | Must be less than or equal to original `subpassCount` |
| `subpassMergeStatus` (each subpass) | Must be `VK_SUBPASS_MERGE_STATUS_DISALLOWED_EXT` | Subpass `0` with `subpassCount == 1` must be `VK_SUBPASS_MERGE_STATUS_NOT_MERGED_SINGLE_SUBPASS_EXT`; subpass `1` under `disallowMergeSubPass1` must be `DISALLOWED` |
| `postMergeIndex` (adjacent pairs) | Must be distinct between neighbors | `MERGED` subpasses must share the previous subpass's `postMergeIndex`; non-merged subpasses must have a distinct `postMergeIndex` |

Any check failure returns `tcu::TestStatus::fail`. If all checks pass, the case returns `tcu::TestStatus::pass` ([L329](../../../modules/vulkan/renderpass/vktRenderPassSubpassMergeFeedbackTests.cpp#L329)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `single_subpass` | Single-subpass status mismatch or `postMergeSubpassCount` overflow. |
| `single_subpass_disallow_renderpass_merge` | Render-pass-level disallow not honored, or `postMergeSubpassCount` not preserved under disallow. |
| `three_subpasses` | General merge invariants violated: merged subpasses not sharing a `postMergeIndex`, or non-merged subpasses sharing one. |
| `three_subpasses_disallow_renderpass_merge` | Render-pass-level disallow not honored across multiple subpasses, or adjacent `postMergeIndex` values not distinct. |
| `three_subpasses_disallow_subpass_merge` | Per-subpass disallow not honored on subpass `1`, or remaining subpasses violating merge invariants. |
| `many_subpasses` | General merge invariants violated at scale, or feedback-structure handling fails with many subpasses. |

All cases share a common structural dependency: they depend on the implementation correctly writing the `pNext`-chained feedback structures during `vkCreateRenderPass2`. If those structures are left uninitialized or overwritten incorrectly, every case in the group can fail.

### Cause Analysis

#### Single-subpass status mismatch or postMergeSubpassCount overflow

**Possible failure symptoms:** For `single_subpass`, the host check fails because the sole subpass's `subpassMergeStatus` is not `VK_SUBPASS_MERGE_STATUS_NOT_MERGED_SINGLE_SUBPASS_EXT`, or because `postMergeSubpassCount` is greater than the original `subpassCount` ([L291-L300](../../../modules/vulkan/renderpass/vktRenderPassSubpassMergeFeedbackTests.cpp#L291-L300)).

**Possible implementation causes:** A single-subpass render pass has nothing to merge with. The Vulkan specification defines `NOT_MERGED_SINGLE_SUBPASS` for exactly this case ([renderpass.adoc](../../../../vulkan-docs/src/chapters/renderpass.adoc#L8408-L8410)). Reporting `MERGED` here, or reporting a `postMergeSubpassCount` that grows, would indicate the implementation's merge decision logic produced a result the specification does not allow.

#### Render-pass-level disallow not honored, or postMergeSubpassCount not preserved under disallow

**Possible failure symptoms:** For `single_subpass_disallow_renderpass_merge` and `three_subpasses_disallow_renderpass_merge`, the host check fails because `postMergeSubpassCount` does not equal the original `subpassCount`, because at least one subpass does not report `VK_SUBPASS_MERGE_STATUS_DISALLOWED_EXT`, or because two adjacent subpasses share a `postMergeIndex` ([L267-L287](../../../modules/vulkan/renderpass/vktRenderPassSubpassMergeFeedbackTests.cpp#L267-L287)).

**Possible implementation causes:** When `VkRenderPassCreationControlEXT::disallowMerging` is `VK_TRUE` on the render pass, the implementation must disable merging for the entire render pass, and the specification says all subpass statuses are then set to `DISALLOWED` ([renderpass.adoc](../../../../vulkan-docs/src/chapters/renderpass.adoc#L8286-L8289), [renderpass.adoc](../../../../vulkan-docs/src/chapters/renderpass.adoc#L8373-L8379)). A failure here points to the implementation not propagating the render-pass-level control into its merge decision, or not preserving the original subpass count when merging is forbidden.

#### General merge invariants violated

**Possible failure symptoms:** For `three_subpasses` and `many_subpasses`, the host check fails because a subpass reporting `VK_SUBPASS_MERGE_STATUS_MERGED_EXT` has a `postMergeIndex` that differs from the previous subpass's `postMergeIndex`, or because a subpass reporting any non-merged status shares the previous subpass's `postMergeIndex` ([L311-L326](../../../modules/vulkan/renderpass/vktRenderPassSubpassMergeFeedbackTests.cpp#L311-L326)).

**Possible implementation causes:** The physical subpass index (`postMergeIndex`) is defined in the specification as the index into the set of subpasses that remain after merge operations ([renderpass.adoc](../../../../vulkan-docs/src/chapters/renderpass.adoc#L1845-L1856)). Two merged subpasses must map to the same physical index, and a subpass that was not merged with the previous one must not share it. A violation means the implementation's merge decision and its `postMergeIndex` assignment are inconsistent. Source-level investigation would be needed to determine whether the fault is in the merge decision itself or in the index computation reported back through the feedback structure.

#### Per-subpass disallow not honored, or remaining subpasses violating merge invariants

**Possible failure symptoms:** For `three_subpasses_disallow_subpass_merge`, the host check fails because subpass `1` does not report `VK_SUBPASS_MERGE_STATUS_DISALLOWED_EXT` despite the per-subpass control, or because subpasses `0` and `2` violate the `postMergeIndex` consistency rules ([L302-L326](../../../modules/vulkan/renderpass/vktRenderPassSubpassMergeFeedbackTests.cpp#L302-L326)).

**Possible implementation causes:** The per-subpass `VkRenderPassCreationControlEXT` with `disallowMerging = VK_TRUE` must disable merging that specific subpass with the previous one ([renderpass.adoc](../../../../vulkan-docs/src/chapters/renderpass.adoc#L8290-L8293)). A failure means the implementation did not honor the subpass-scoped control. If the failure is instead on subpass `0` or `2`, the cause is the same general merge-invariant inconsistency described above.

## Case Pruning

### Requirement-based pruning

- Every case requires both `VK_KHR_create_renderpass2` (for `vkCreateRenderPass2` and the create-info v2 structures) and `VK_EXT_subpass_merge_feedback`. These are checked in [checkSupport](../../../modules/vulkan/renderpass/vktRenderPassSubpassMergeFeedbackTests.cpp#L105-L112).
- The entire test family is pruned for `RENDERING_TYPE_RENDERPASS_LEGACY` and `RENDERING_TYPE_DYNAMIC_RENDERING`, because the factory returns `nullptr` unless the rendering type is `RENDERING_TYPE_RENDERPASS2` ([L346-L349](../../../modules/vulkan/renderpass/vktRenderPassSubpassMergeFeedbackTests.cpp#L346-L349)). This is why the family appears only under `renderpasses.renderpass2.suballocation` and not under the legacy or dynamic-rendering subtrees.

### Design-based pruning

- The test family covers three subpass counts (`1`, `3`, `32`) and three disallow configurations (none, render-pass-level, subpass-level). Not every combination is registered. The registered six cases pair each subpass count with a meaningful disallow configuration, avoiding redundant combinations. For example, `disallowMergeSubPass1` is exercised only with three subpasses, because subpass `1` does not exist when `subpassCount` is `1`.
- `many_subpasses` is registered only with no disallow, because its purpose is to stress the general invariants at scale rather than to test a new control combination.

## Key Takeaways

- The `subpass_merge_feedback` family is registered exclusively under `renderpasses.renderpass2.suballocation`, because the factory returns `nullptr` for every other rendering type.
- The test has no shaders and no draw calls. It validates the `pNext`-chained feedback structures that `vkCreateRenderPass2` writes when `VK_EXT_subpass_merge_feedback` is used.
- The verification rule splits cleanly into two branches: when render-pass-level merging is disallowed, every subpass must report `DISALLOWED` and the post-merge count must be preserved; otherwise, the general merge invariants apply, with special handling for the single-subpass and per-subpass-disallow cases.
- The `postMergeIndex` consistency checks are the core invariant: merged subpasses share the previous subpass's index, and non-merged subpasses do not.
- See `## Failure Meaning` for what each leaf's failure points to.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test family factory | [createRenderPassSubpassMergeFeedbackTests](../../../modules/vulkan/renderpass/vktRenderPassSubpassMergeFeedbackTests.cpp#L343) | Returns `nullptr` unless rendering type is `RENDERING_TYPE_RENDERPASS2`; registers the six test case leaves. |
| Dispatcher attachment | [vktRenderPassTests.cpp#L8508-L8510](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8508-L8510) | Adds the family to `suballocationTestGroup` inside the `RENDERING_TYPE_RENDERPASS2` branch. |
| Test parameters | [TestParams](../../../modules/vulkan/renderpass/vktRenderPassSubpassMergeFeedbackTests.cpp#L60-L65) | Defines the three dimensions: `subpassCount`, `disallowMergeRenderpass`, `disallowMergeSubPass1`. |
| Support checks | [checkSupport](../../../modules/vulkan/renderpass/vktRenderPassSubpassMergeFeedbackTests.cpp#L105-L112) | Requires `VK_KHR_create_renderpass2` and `VK_EXT_subpass_merge_feedback`. |
| Render-pass and feedback construction | [createRenderPassAndVerify](../../../modules/vulkan/renderpass/vktRenderPassSubpassMergeFeedbackTests.cpp#L125-L330) | Builds attachment, subpass, dependency, control, and feedback structures, creates the render pass, and runs verification. |
| Disallowed-merge verification | [L267-L287](../../../modules/vulkan/renderpass/vktRenderPassSubpassMergeFeedbackTests.cpp#L267-L287) | Verification branch for `disallowMergeRenderpass = true`. |
| Allowed-merge verification | [L289-L327](../../../modules/vulkan/renderpass/vktRenderPassSubpassMergeFeedbackTests.cpp#L289-L327) | Verification branch for the remaining cases, including single-subpass and per-subpass-disallow handling. |
| Mustpass entries | [renderpasses.txt#L79568-L79573](../../../mustpass/main/vk-default/renderpasses.txt#L79568-L79573) | Lists the six `dEQP-VK.renderpasses.renderpass2.suballocation.subpass_merge_feedback.*` leaves in the default mustpass. |
| Specification: merge feedback chapter | [renderpass.adoc](../../../../vulkan-docs/src/chapters/renderpass.adoc#L8267-L8416) | Defines `VkRenderPassCreationControlEXT`, the feedback create-info structures, and the `VkSubpassMergeStatusEXT` enum values. |
