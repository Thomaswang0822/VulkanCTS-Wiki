## Overview

**Core question:** When an input-attachment array of size 2*N* is filled so that exactly half of its entries are `VK_ATTACHMENT_UNUSED`, can a fragment shader still read the *N* active input attachments through the bindings that skip the unused slots?

[`vktRenderPassUnusedAttachmentSparseFillingTests.cpp`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L1) implements the `attachment_sparse_filling` test family. Each test case registers *N* active input attachments, builds a descriptor and subpass layout whose total attachment count is 2*N*, places *N* `VK_ATTACHMENT_UNUSED` entries between the active ones, and lets a fragment shader walk the active bindings. The shader counts how many descriptors it iterates and how many of them return a nonzero value, then stores both counters to a storage image the host reads back.

- The family appears under three rendering variants that all share this one implementation: `renderpasses.renderpass1`, `renderpasses.renderpass2`, and `renderpasses.dynamic_rendering` (with the `primary_cmd_buff`, `complete_secondary_cmd_buff`, `partial_secondary_cmd_buff`, and `graphics_pipeline_library` sub-roots).
- The behavioral axis is the active attachment count *N*, registered as the seven test case leaves `input_attachment_1`, `input_attachment_3`, `input_attachment_7`, `input_attachment_15`, `input_attachment_31`, `input_attachment_63`, and `input_attachment_127`.
- Each leaf must pass on its own; there is no aggregate pass condition.

## Background Knowledge

- **`VK_ATTACHMENT_UNUSED` as a hole, not an end marker.** In a `VkSubpassDescription` input attachment array, or in the `pColorAttachmentInputIndices` list consumed by `VkRenderingInputAttachmentIndexInfo` under dynamic rendering local read, an entry equal to `VK_ATTACHMENT_UNUSED` means "no attachment at this position," not "the array ends here." Active entries can sit at indices before and after an unused one. The [spec text](../../../../vulkan-docs/src/chapters/renderpass.adoc) states that if `pInputAttachments[i].attachment` is `VK_ATTACHMENT_UNUSED`, the application must not read from input attachment index *i*, but it does not require the unused entries to be contiguous or trailing.
- **Input attachment descriptor must be present even when the subpass slot is unused.** A `subpassLoad` in GLSL reads through a descriptor bound at a specific `InputAttachmentIndex`. The implementation under test must keep the descriptor-array layout sparse: it must not compact the active bindings together and renumber the indices, or the test would no longer exercise the "skip the holes" path.
- **Sparse filling in dynamic rendering.** Under `VK_KHR_dynamic_rendering_local_read`, there is no `pInputAttachments` array; instead, `VkRenderingInputAttachmentIndexInfo` maps color attachment indices to input attachment indices. Unused entries in `pColorAttachmentInputIndices` play the same hole role, and the attachment index can be anywhere in the `[0, 2*N* - 1]` range rather than being contiguous from zero as in the render-pass cases.

## Registration Hierarchy

```text
renderpasses.renderpass1.suballocation.attachment_sparse_filling
├── input_attachment_1
├── input_attachment_3
├── input_attachment_7
├── input_attachment_15
├── input_attachment_31
├── input_attachment_63
└── input_attachment_127
```

The same seven test case leaves are also registered under `renderpass2.suballocation.attachment_sparse_filling` and under each `dynamic_rendering.<cmd_buff_variant>.suballocation.attachment_sparse_filling` root. [`createRenderPassUnusedAttachmentSparseFillingTests`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L1047-L1064) constructs the family once for whichever `SharedGroupParams` the caller passes, so all six rendering roots reuse the identical implementation.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Active input attachment count *N* | `1`, `3`, `7`, `15`, `31`, `63`, `127` | Doubles to a total attachment count of `2`, `6`, `14`, `30`, `62`, `126`, `254`. The values follow the form `2^k - 1` for `k` from 1 to 7, so each step roughly doubles the descriptor array and the number of holes. | [`activeInputAttachmentCount` array](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L1053) |
| Total attachment count | `2 * N` | Fixed by the test: the input attachment array always has exactly as many unused slots as active slots. | [`generateInputAttachmentParams` call sites](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L102-L150) |
| Rendering variant | `renderpass1`, `renderpass2`, `dynamic_rendering` | Selects the legacy `VkRenderPass` path, the `VK_KHR_create_renderpass2` path, or the `VK_KHR_dynamic_rendering_local_read` path. All three reuse the same test logic through `SharedGroupParams`. | [`SharedGroupParams` dispatch](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L513-L522) and [`checkSupport`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L351-L374) |

The seed for hole placement is fixed at `DEFAULT_SEED = 31`, so the shuffle order is deterministic across runs for a given *N* and rendering variant.

## Behavior Parameters

The primary behavioral axis is the active input attachment count *N*. Every value exercises the same mechanism at increasing scale; the interesting question is not "does each leaf test a different property" but "does the implementation keep skipping holes correctly as the array grows toward the device limits."

### input_attachment_1, smallest sparse array

One active input attachment sits in a two-slot array alongside one `VK_ATTACHMENT_UNUSED` entry. This is the minimal case: the shader iterates one descriptor and expects its `subpassLoad` to return the cleared `(1, 1, 1, 1)` value, so `result.x` and `result.y` must both equal `1`.

### input_attachment_3 through input_attachment_127, growing the holes

Each larger leaf keeps the same ratio of half active and half unused, but stretches the descriptor array and the subpass input attachment list. The larger leaves are the ones that approach the device limits `maxPerStageDescriptorInputAttachments`, `maxPerStageResources`, and (for dynamic rendering) `maxColorAttachments`, so they are the ones most likely to expose descriptor-indexing or input-attachment-routing bugs that only appear at scale. The `input_attachment_127` leaf binds 254 attachment slots, the largest configuration the test generates.

### Why the count values are `2^k - 1`

The sequence `1, 3, 7, 15, 31, 63, 127` is chosen so each step roughly doubles the array while staying one short of a power of two. This keeps the total `2*N*` within typical device limits for as many steps as possible and produces evenly spaced coverage from the trivial case up to the practical maximum.

## Shader Analysis

The generated fragment shader is where the test makes its observation. [`InputAttachmentSparseFillingTest::initPrograms`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L301-L344) builds it from the same `generateInputAttachmentParams` output that the host-side descriptor and render-pass setup use, so the shader's binding and `input_attachment_index` decorations exactly mirror the sparse layout.

The shader does two independent counts per fragment and writes them to a `rg32ui` storage image:

- `result.x` is incremented once for every active binding the shader iterates, with no condition on the loaded value. It must equal *N*.
- `result.y` is incremented only when the loaded texel's `.x` is greater than zero. Because every active input image is cleared to `(1, 1, 1, 1)` before the draw, every active load should contribute, so `result.y` must also equal *N*.

The two counts let one test distinguish three outcomes: the shader saw the right number of descriptors but the wrong data (`result.x == N`, `result.y != N`), the shader saw the wrong number of descriptors entirely (`result.x != N`), or both counts are correct. No representative walkthrough is included because the generated shader is short, identical in structure across all leaves, and fully described by the count logic above.

## Runtime Execution and Result Checking

- **Resource setup.** The constructor at [`InputAttachmentSparseFillingTestInstance`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L376-L723) creates *N* `R8G8B8A8_UNORM` input images with views, one `R32G32_UINT` output image with a view, and one host-visible output buffer sized to the render extent.
- **Descriptor layout.** Binding 0 is the output storage image; bindings 1 through *N* are the active input attachments, declared in the sparse order produced by `generateInputAttachmentParams`. The layout never contains a binding for an unused slot. [`DescriptorSetLayoutBuilder`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L558-L568)
- **Render pass or dynamic rendering setup.** For the render-pass variants, the subpass lists `2*N*` input attachment references, half of them `VK_ATTACHMENT_UNUSED`. For dynamic rendering, the same sparse pattern is delivered through `VkRenderingInputAttachmentIndexInfo`. [`createRenderPass`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L923-L1004) and [`createCommandBufferDynamicRendering`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L757-L865)
- **Pre-render commands.** [`preRenderCommands`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L867-L905) clears the output image to `(0, 0)` and every input image to `(1, 1, 1, 1)`, then transitions each input image to the layout the fragment shader will read it through: `GENERAL` for the render-pass variants, or `RENDERING_LOCAL_READ_KHR` (or `GENERAL` for the `complete_secondary_cmd_buff` sub-variant) for dynamic rendering.
- **Draw.** A single fullscreen triangle draws the fragment shader once per pixel. [`drawCommands`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L907-L915)
- **Copyback and check.** [`postRenderCommands`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L917-L921) copies the output image to the host-visible buffer. [`verifyImage`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L1017-L1043) scans every pixel and fails with `"Wrong attachment count"` if `result.x != N` or with `"Wrong active attachment count"` if `result.y != N`.

The pass condition is exact: both channels of every pixel must equal *N*. There is no tolerance and no aggregation across leaves.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `input_attachment_1` | Minimal sparse routing: a single `VK_ATTACHMENT_UNUSED` entry next to one active input attachment breaks descriptor binding, subpass input attachment routing, or the dynamic-rendering index map. |
| `input_attachment_3` through `input_attachment_127` | Any of the minimal causes, plus scale-sensitive descriptor indexing, input attachment routing, or limit handling that only appears as the array grows toward `maxPerStageDescriptorInputAttachments`, `maxPerStageResources`, or `maxColorAttachments`. |

All leaves share the same descriptor setup, shader, and verification path, so a failure that appears at every *N* points at the shared sparse-routing machinery rather than at a count-specific path.

### Cause Analysis

#### Incorrect descriptor or subpass routing of unused slots

**Possible failure symptoms:** `result.x` differs from *N*, meaning the shader iterated the wrong number of active bindings. Depending on the bug, `result.y` may differ as well.

**Possible implementation causes:** The driver may compact the descriptor array and renumber `InputAttachmentIndex` decorations, map a `VK_ATTACHMENT_UNUSED` subpass entry to a real attachment (or vice versa), or apply the `VkRenderingInputAttachmentIndexInfo` color-to-input map incorrectly. Any of these would let the shader load from the wrong texel or skip a binding, changing the iteration count. Source-level investigation of the selected leaf is needed to tell descriptor-set construction from subpass-description handling as the fault location.

#### Active input attachment returns the wrong data

**Possible failure symptoms:** `result.x == N` but `result.y != N`. The shader saw every active binding but at least one `subpassLoad` did not return the cleared `(1, 1, 1, 1)` value.

**Possible implementation causes:** The cleared input image contents may not have reached the fragment shader through the sparse routing, the input image layout transition may have discarded or aliased the cleared data, or the implementation may have routed an active binding to an uninitialized or wrong attachment. Because the shader only checks `.x > 0`, a partial or blended value would still pass or fail depending on whether the red channel survived. The host cannot tell from `result.y` alone which binding was wrong; source-level inspection of the descriptor update and image transition for the failing leaf is needed.

#### Limit or feature handling at large *N*

**Possible failure symptoms:** Only the larger leaves (`input_attachment_63`, `input_attachment_127`) fail, or a leaf fails during pipeline creation or draw submission rather than at verification.

**Possible implementation causes:** The implementation may misreport or mis-enforce `maxPerStageDescriptorInputAttachments`, `maxPerStageResources`, or `maxColorAttachments`, or may handle the dynamic-rendering local-read path differently at high attachment counts. [`checkSupport`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L351-L374) is supposed to skip leaves that exceed the device's reported limits, so a failure here after the support check passed suggests the reported limit and the actual handling disagree. Confirming this requires checking the device's reported limits against the failing leaf's `2*N*` total.

## Case Pruning

### Requirement-based pruning

- [`checkSupport`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L351-L374) requires `VK_KHR_create_renderpass2` for the `renderpass2` variant and `VK_KHR_dynamic_rendering_local_read` for the dynamic-rendering variant.
- The same function throws `NotSupportedError` when `2*N*` exceeds `maxColorAttachments` (dynamic rendering only), `maxPerStageDescriptorInputAttachments`, or `maxPerStageResources`. On devices with low limits, the larger leaves are skipped rather than failed.
- Unsupported variants cause a skip through the CTS support check, not a failed verification.

### Design-based pruning

- The active attachment counts are fixed at `1, 3, 7, 15, 31, 63, 127`. No other counts are generated, so there is no per-leaf configuration matrix beyond the rendering variant chosen by the parent group.
- The total attachment count is always exactly `2*N*`. The test does not cover other ratios of active-to-unused entries.

## Key Takeaways

- The family tests one property at seven scales: an input attachment array that mixes active entries with `VK_ATTACHMENT_UNUSED` holes must still let the shader read every active entry through its original descriptor binding.
- The fragment shader's two independent counts turn one run into three distinguishable outcomes: wrong descriptor count, right count but wrong data, or full pass.
- All three rendering variants (legacy render pass, `renderpass2`, and dynamic rendering with local read) share one implementation, so a failure scoped to one variant points at variant-specific routing (`pInputAttachments` versus `VkRenderingInputAttachmentIndexInfo`) rather than at the shared shader or verification logic.
- The larger leaves are deliberately sized to approach the device limits, so a failure that only appears at `input_attachment_63` or `input_attachment_127` is more likely a limit or scale-sensitive routing bug than a logic error in the minimal case.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Family registration | [`createRenderPassUnusedAttachmentSparseFillingTests`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L1047-L1064) | Creates `attachment_sparse_filling` and adds the seven `input_attachment_*` test case leaves. |
| Sparse layout generator | [`generateInputAttachmentParams`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L102-L150) | Produces the `VK_ATTACHMENT_UNUSED` hole pattern differently for render-pass and dynamic-rendering variants; drives the shader, descriptor, and subpass setup. |
| Shader generation | [`InputAttachmentSparseFillingTest::initPrograms`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L301-L344) | Builds the fragment shader whose `result.x` / `result.y` counts are the pass condition. |
| Support and limits | [`InputAttachmentSparseFillingTest::checkSupport`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L351-L374) | Gates the three rendering variants and skips leaves that exceed device limits. |
| Resource and pipeline setup | [`InputAttachmentSparseFillingTestInstance` constructor](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L376-L723) | Creates input/output images, descriptor set, render pass or dynamic-rendering state, and pipeline. |
| Render-pass construction | [`createRenderPass`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L923-L1004) | Builds the subpass with `2*N*` input attachment references, half unused. |
| Dynamic-rendering construction | [`createCommandBufferDynamicRendering`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L757-L865) | Records the sparse `VkRenderingInputAttachmentIndexInfo` and the three secondary-command-buffer variants. |
| Verification | [`verifyImage`](../../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp#L1017-L1043) | Scans every output pixel and compares both channels against *N*. |
| `VK_ATTACHMENT_UNUSED` semantics | [`renderpass.adoc` input attachment rules](../../../../vulkan-docs/src/chapters/renderpass.adoc) | Defines what an unused entry means in `pInputAttachments`. |
| Dynamic-rendering index mapping | [`VkRenderingInputAttachmentIndexInfo` and `vkCmdSetRenderingInputAttachmentIndices`](../../../../vulkan-docs/src/chapters/interfaces.adoc) | Defines the sparse color-to-input map used by the dynamic-rendering variant. |
