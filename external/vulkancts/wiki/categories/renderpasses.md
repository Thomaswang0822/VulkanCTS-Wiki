## Overview

The `renderpasses` test category collects tests that check Vulkan render pass and dynamic rendering correctness across three rendering models: legacy render passes (Vulkan 1.0), render pass 2 (`VK_KHR_create_renderpass2`), and dynamic rendering (`VK_KHR_dynamic_rendering`).

## Background Knowledge

- **Three rendering models.** Vulkan offers three ways to structure a render pass instance. Legacy render passes (Vulkan 1.0, `RENDERING_TYPE_RENDERPASS_LEGACY`) use `VkRenderPass` objects with subpass descriptions, attachment references, and subpass dependencies. Render pass 2 (`VK_KHR_create_renderpass2`, `RENDERING_TYPE_RENDERPASS2`) uses `VkRenderPass2` with the same object model but an extended create-info chain. Dynamic rendering (`VK_KHR_dynamic_rendering`, `RENDERING_TYPE_DYNAMIC_RENDERING`) replaces render pass objects with `vkCmdBeginRendering` / `vkCmdEndRendering` and carries attachment and view-mask information in `VkRenderingInfo`. Most renderpasses test families run under all three models; a few are specific to one or two.
- **Rendering type routing via `GroupParams`.** Every implementation file in this category receives a `SharedGroupParams` struct that selects the rendering type, the synchronization type (legacy vs synchronization2), the pipeline construction type, and the secondary command buffer mode. The dispatcher `createRenderPassesTests()` builds one `GroupParams` per rendering variant and passes it into the shared `createRenderPassTestsInternal()` function, which routes each test family through the correct render-pass or dynamic-rendering code path. This is why most families appear under `renderpass1`, `renderpass2`, and each `dynamic_rendering.*` sub-variant with identical test case leaves but different recording paths.
- **Dynamic-rendering sub-variants.** Under `dynamic_rendering`, the same families are registered across four sub-variants that differ only in command buffer and pipeline construction: `primary_cmd_buff`, `partial_secondary_cmd_buff`, `complete_secondary_cmd_buff`, and `graphics_pipeline_library`. These sub-variants are non-SC only.

## Category Structure

```text
renderpasses
├── renderpass1
├── renderpass2
└── dynamic_rendering
    ├── primary_cmd_buff
    ├── partial_secondary_cmd_buff
    ├── complete_secondary_cmd_buff
    └── graphics_pipeline_library
```

Each rendering-type root holds a mix of directly-attached test families (for example `depth_stencil_write_conditions`, `dithering`, `fragment_density_map`) and an allocation subtree (`suballocation`, `dedicated_allocation`, `no_draws`) that carries the core `simple`, `formats`, `attachment`, `attachment_write_mask`, `attachment_allocation`, multisample, resolve, unused-attachment, and dependency families. The `dynamic_rendering` root additionally carries dynamic-rendering-specific families (`basic`, `random`, `unused_attachments`, `local_read`, `local_read_maint10`, `multiview_clear`). The visible Level-3 page count (29) is smaller than the full registered tree because one Level-3 page covers all rendering-type registrations of the same implementation file.

## How the Families Fit Together

The families share one theme: each verifies that a specific render-pass or dynamic-rendering mechanism produces correct framebuffer contents or correct host-visible feedback. They differ in which mechanism they target.

- **Core attachment and load/store behavior** is covered by the `RenderPassTests` family, which uses a software reference renderer to compare every format, load/store operation, and allocation strategy. The unused-attachment, clear-some-attachments, remaining-array-layers, and load-store-op-none families each isolate one attachment-management edge case against the same reference-rendering baseline.
- **Multisample and resolve behavior** is covered by three families: `Multisample` writes per-sample values and reads them back, `MultisampleResolve` tests the resolve downsample step, and `SampleRead` validates per-sample input-attachment reads from inside the shader. Depth/stencil resolve extends the resolve concept to the depth/stencil aspect under render pass 2 and dynamic rendering.
- **Dependency and ordering behavior** is covered by `SubpassDependency`, which builds six dependency shapes (external, implicit, late-fragment-test, self-dependency, disjoint-channel, single-attachment) and checks that each orders work correctly.
- **Extension-specific behavior** is covered by families that target one extension: custom resolve, fragment density map, dithering, sparse render target, multiview per-view, subpass merge feedback, nested command buffers, performance counters by region, and the dynamic-rendering local-read and maintenance-10 feedback-loop families.
- **Dynamic rendering specifics** are covered by the `basic`, `random`, `unused_attachments`, and `multiview_clear` families, which exercise dynamic-rendering-only attachment, suspend/resume, and secondary-command-buffer interactions.

## Level-3 Pages Navigation

| Registered test family or area | Level-3 page | What to read there |
|--------------------------------|--------------|--------------------|
| `simple`, `formats`, `attachment`, `attachment_write_mask`, `attachment_allocation`, `no_draw_clear_load_store`; dispatcher `createRenderPassesTests()` | [RenderPassTests](../testfiles/renderpasses/RenderPassTests.md) | Software reference rendering method, allocation-intermediate-node pattern, and core load/store and format coverage |
| `unused_attachment` | [UnusedAttachment](../testfiles/renderpasses/UnusedAttachment.md) | Unreferenced attachment load/store suppression |
| `unused_clear_attachments` (monolithic) | [UnusedClearAttachment](../testfiles/renderpasses/UnusedClearAttachment.md) | `vkCmdClearAttachments` on `VK_ATTACHMENT_UNUSED` attachments |
| `attachment_sparse_filling` | [UnusedAttachmentSparseFilling](../testfiles/renderpasses/UnusedAttachmentSparseFilling.md) | Sparse input-attachment descriptor binding with unused holes |
| `load_store_op_none` | [LoadStoreOpNone](../testfiles/renderpasses/LoadStoreOpNone.md) | `VK_ATTACHMENT_LOAD_OP_NONE` / `STORE_OP_NONE` render-area behavior |
| `clear_some_attachments` (monolithic) | [ClearSomeAttachments](../testfiles/renderpasses/ClearSomeAttachments.md) | Selective `loadOp` clear vs load across multiple attachments |
| `remaining_array_layers` | [RemainingArrayLayers](../testfiles/renderpasses/RemainingArrayLayers.md) | `VK_REMAINING_ARRAY_LAYERS` in 2D-array views of 3D images |
| `multiple_subpasses_multiple_command_buffers` | [MultipleSubpassesMultipleCommandBuffers](../testfiles/renderpasses/MultipleSubpassesMultipleCommandBuffers.md) | Multi-subpass render pass split across two primary command buffers |
| `multisample` | [Multisample](../testfiles/renderpasses/Multisample.md) | Per-sample write and input-attachment readback |
| `multisample_resolve` | [MultisampleResolve](../testfiles/renderpasses/MultisampleResolve.md) | Average vs sample-zero resolve across sample-mask patterns |
| `sampleread` | [SampleRead](../testfiles/renderpasses/SampleRead.md) | Shader-internal per-sample input-attachment validation |
| `depth_stencil_resolve` (RP2) | [DepthStencilResolve](../testfiles/renderpasses/DepthStencilResolve.md) | `VK_KHR_depth_stencil_resolve` resolve-mode matrix |
| `depth_stencil_write_conditions` (RP1) | [DepthStencilWriteConditions](../testfiles/renderpasses/DepthStencilWriteConditions.md) | Helper-invocation depth/stencil write suppression |
| `custom_resolve` (RP1/RP2/Dynamic) | [CustomResolve](../testfiles/renderpasses/CustomResolve.md) | `VK_EXT_custom_resolve` shader-driven resolve |
| `depth_stencil_resolve` under dynamic_rendering | [DynamicRenderingDepthStencilResolve](../testfiles/renderpasses/DynamicRenderingDepthStencilResolve.md) | Pre-computed expected-value table lookup for dynamic-rendering resolve |
| `subpass_dependencies` | [SubpassDependency](../testfiles/renderpasses/SubpassDependency.md) | External, implicit, late-fragment-test, self-, disjoint-channel, and single-attachment dependencies |
| `basic` dynamic rendering | [DynamicRendering](../testfiles/renderpasses/DynamicRendering.md) | Basic dynamic rendering and shared `createRenderPassTestsInternal()` routing |
| `random` dynamic rendering | [DynamicRenderingRandom](../testfiles/renderpasses/DynamicRenderingRandom.md) | Randomized suspend/resume and secondary-command-buffer stress |
| `unused_attachments` dynamic rendering | [DynamicRenderingUnusedAttachments](../testfiles/renderpasses/DynamicRenderingUnusedAttachments.md) | `VK_EXT_dynamic_rendering_unused_attachments` pipeline-vs-instance mismatch |
| `local_read` dynamic rendering | [DynamicRenderingLocalRead](../testfiles/renderpasses/DynamicRenderingLocalRead.md) | `VK_KHR_dynamic_rendering_local_read` input-attachment mapping |
| `local_read_maint10` / `m10_feedback_loop` | [DynamicRenderingLocalReadMaint10](../testfiles/renderpasses/DynamicRenderingLocalReadMaint10.md) | `VK_KHR_maintenance10` feedback-loop layout |
| `multiview_clear` dynamic rendering | [DynamicRenderingMultiviewClear](../testfiles/renderpasses/DynamicRenderingMultiviewClear.md) | Multiview view-mask clear filtering |
| `fragment_density_map` | [FragmentDensityMap](../testfiles/renderpasses/FragmentDensityMap.md) | `VK_EXT_fragment_density_map` / FDM2 / FDM offset |
| `dithering` | [Dithering](../testfiles/renderpasses/Dithering.md) | `VK_EXT_legacy_dithering` one-ULP bound |
| `sparserendertarget` (monolithic) | [SparseRenderTarget](../testfiles/renderpasses/SparseRenderTarget.md) | Sparse resident color target across formats |
| `multiview_per_view` (RP2/Dynamic) | [MultiviewPerView](../testfiles/renderpasses/MultiviewPerView.md) | `VK_QCOM_multiview_per_view_render_areas` / viewports |
| `subpass_merge_feedback` (RP2) | [SubpassMergeFeedback](../testfiles/renderpasses/SubpassMergeFeedback.md) | `VK_EXT_subpass_merge_feedback` merge metadata query |
| `nested_command_buffers` (monolithic) | [NestedCommandBuffers](../testfiles/renderpasses/NestedCommandBuffers.md) | `VK_EXT_nested_command_buffer` inline-and-secondary mixing |
| `performance_counters_by_region` | [PerformanceCountersByRegion](../testfiles/renderpasses/PerformanceCountersByRegion.md) | `VK_ARM_performance_counters_by_region` per-tile counter capture |

## Category Notes

- The source directory is named `renderpass` (singular) but the registered group name is `renderpasses` (plural). The mustpass file is `renderpasses.txt`.
- `dynamic_rendering` and its four sub-variants are excluded under VulkanSC builds.
- `subpass_merge_feedback` is registered only under `renderpass2`; it returns `nullptr` for all other rendering types.
- `depth_stencil_write_conditions` is registered only under `renderpass1` and is excluded from VulkanSC.
- `multiview_per_view` is registered under `renderpass2` and `dynamic_rendering` but not under `renderpass1`.
- `depth_stencil_resolve` has separate implementation files for render-pass (`vktRenderPassDepthStencilResolveTests.cpp`) and dynamic-rendering (`vktDynamicRenderingDepthStencilResolveTests.cpp`); each has its own Level-3 page.
- `vktRenderPassTestsUtil.cpp` and `vktRenderPassGroupParams.hpp` are shared utilities without their own Level-3 pages; Level-3 pages reference them as supporting evidence for `GroupParams`, `RenderingType`, and `SynchronizationType`.
