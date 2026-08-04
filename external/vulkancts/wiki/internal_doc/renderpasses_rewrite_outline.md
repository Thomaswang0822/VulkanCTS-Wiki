# renderpasses Rewrite Outline

## Scope

- Category: `renderpasses`
- Old Level-2 page: `external/vulkancts/wiki/categories/renderpasses.md`
- Old Level-3 directory: `external/vulkancts/wiki/testfiles/renderpasses/`
- Source category directory: `external/vulkancts/modules/vulkan/renderpass/`

## Page Count

- Old Level-3 pages found: 29
- Registration-only dispatcher pages to fold into Level-2: 0 (the dispatcher `createRenderPassesTests()` lives inside `vktRenderPassTests.cpp`, which also implements the `simple`, `formats`, `attachment`, `attachment_write_mask`, `attachment_allocation`, and `no_draw_clear_load_store` sub-variants and therefore is a hybrid implementation + dispatcher file rather than a pure registration-only file)
- Implementation-bearing Level-3 pages to rewrite: 29
- Counted rewrite files for batching: 29
  - 0 Understanding Briefs (no page in this category is pre-flagged for brief-driven rewriting in this outline; briefs may be added per page during inspection if a page proves non-mechanical)
  - 29 rewritten Level-3 pages

Rationale for no automatic briefs in the outline: although `renderpasses` is large and contains many feature-gated subfamilies (multisample, depth/stencil resolve, fragment density map, custom resolve, subpass merge feedback, multiview per-view, performance counters by region), each Level-3 page corresponds to a single self-contained implementation file with a clear functional theme. Whether a page needs an Understanding Brief is decided per-page during Phase 1 inspection; the outline only fixes the dispatcher decision and batch structure.

## Dispatcher Decision

- `vktRenderPassTests.cpp` should be rewritten because it has implementation in addition to registration. The file owns both the `createRenderPassesTests()` dispatcher entry point (at `vktRenderPassTests.cpp#L8692`) and the core sub-variants (`simple`, `formats`, `attachment`, `attachment_write_mask`, `attachment_allocation`, `no_draw_clear_load_store`) used by every rendering type and every `suballocation`/`dedicated_allocation`/`no_draws` intermediate node. Its Level-3 page must explain both responsibilities and must reference the related files only as `(registration only)` or `(delegated)`.
- Fold category-specific dispatcher facts into the rewritten Level-2 `renderpasses` page:
  - direct category tree across `renderpass1`, `renderpass2`, and `dynamic_rendering`, including the four dynamic-rendering sub-variants (`primary_cmd_buff`, `partial_secondary_cmd_buff`, `complete_secondary_cmd_buff`, `graphics_pipeline_library`);
  - subgroup names used by each implementation file (for example `multisample`, `multisample_resolve`, `sampleread`, `subpass_dependencies`, `unused_attachment`, `unused_clear_attachments`, `attachment_sparse_filling`, `clear_some_attachments`, `depth_stencil_resolve`, `depth_stencil_write_conditions`, `custom_resolve`, `fragment_density_map`, `sparserendertarget`, `load_store_op_none`, `dithering`, `remaining_array_layers`, `performance_counters_by_region`, `multiple_subpasses_multiple_command_buffers`, `multiview_per_view`, `subpass_merge_feedback`, `nested_command_buffers`, and the dynamic-rendering subgroups `basic`, `random`, `unused_attachments`, `local_read`, `local_read_maint10`, `m10_feedback_loop`, `depth_stencil_resolve`, `multiview_clear`);
  - source-to-family routing for each implementation file.

## Batch 1 — Core renderpass + load/store + allocation themes

Counted files: 8

| Old Level-3 page | Brief? | Reason |
|---|---:|---|
| `vktRenderPassTests.md` | No | Hybrid registration + core implementation file. Owns `simple`, `formats`, `attachment`, `attachment_write_mask`, `attachment_allocation`, `no_draw_clear_load_store` across `renderpass1`, `renderpass2`, and the four dynamic-rendering sub-variants. The page must explain the Software reference rendering method and the `suballocation`/`dedicated_allocation`/`no_draws` intermediate-node pattern. Direct rewrite. |
| `vktRenderPassUnusedAttachmentTests.md` | No | Implementation file for `unused_attachment`. Direct rewrite. |
| `vktRenderPassUnusedClearAttachmentTests.md` | No | Implementation file for `unused_clear_attachments` (monolithic only). Direct rewrite. |
| `vktRenderPassUnusedAttachmentSparseFillingTests.md` | No | Implementation file for `attachment_sparse_filling`. Direct rewrite. |
| `vktRenderPassLoadStoreOpNoneTests.md` | No | Implementation file for `load_store_op_none`; covers `VK_EXT_load_store_op_none` and `VK_KHR_load_store_op_none`. Direct rewrite. |
| `vktRenderPassClearSomeAttachmentsTests.md` | No | Implementation file for `clear_some_attachments` (monolithic only). Direct rewrite. |
| `vktRenderPassRemainingArrayLayersTests.md` | No | Implementation file for `remaining_array_layers`. Direct rewrite. |
| `vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.md` | No | Implementation file for `multiple_subpasses_multiple_command_buffers`. Direct rewrite. |

## Batch 2 — Multisample, depth/stencil, and resolve

Counted files: 8

| Old Level-3 page | Brief? | Reason |
|---|---:|---|
| `vktRenderPassMultisampleTests.md` | No | Implementation file for `multisample`. Direct rewrite. |
| `vktRenderPassMultisampleResolveTests.md` | No | Implementation file for `multisample_resolve`. Direct rewrite. |
| `vktRenderPassSampleReadTests.md` | No | Implementation file for `sampleread` (shader-internal validation). Direct rewrite. |
| `vktRenderPassDepthStencilResolveTests.md` | No | Implementation file for `depth_stencil_resolve` (RP2). Direct rewrite. |
| `vktRenderPassDepthStencilWriteConditionsTests.md` | No | Implementation file for `depth_stencil_write_conditions` (RP1); covers `VK_EXT_shader_demote_to_helper_invocation`, `VK_KHR_shader_terminate_invocation`, and `VK_EXT_shader_stencil_export`. Direct rewrite. |
| `vktRenderPassCustomResolveTests.md` | No | Implementation file for `custom_resolve` across RP1/RP2/Dynamic; `VK_EXT_custom_resolve` plus `single_sample_clear` for dynamic only. Direct rewrite. |
| `vktDynamicRenderingDepthStencilResolveTests.md` | No | Implementation file for `depth_stencil_resolve` under dynamic_rendering; pre-computed expected-value table lookup. Direct rewrite. |
| `vktRenderPassSubpassDependencyTests.md` | No | Implementation file for `subpass_dependencies`. Direct rewrite. |

## Batch 3 — Dynamic rendering families

Counted files: 7

| Old Level-3 page | Brief? | Reason |
|---|---:|---|
| `vktDynamicRenderingTests.md` | No | Implementation file for `basic` dynamic rendering. Direct rewrite. |
| `vktDynamicRenderingRandomTests.md` | No | Implementation file for `random` dynamic rendering. Direct rewrite. |
| `vktDynamicRenderingUnusedAttachmentsTests.md` | No | Implementation file for `unused_attachments`; covers `VK_EXT_dynamic_rendering_unused_attachments` and uses `tcu::dsThresholdCompare`. Direct rewrite. |
| `vktDynamicRenderingLocalReadTests.md` | No | Implementation file for `local_read`; covers `VK_KHR_dynamic_rendering_local_read` input-attachment mapping. Direct rewrite. |
| `vktDynamicRenderingLocalReadMaint10Tests.md` | No | Implementation file for `local_read_maint10` / `m10_feedback_loop`; covers `VK_KHR_maintenance10` feedback-loop layout. Direct rewrite. |
| `vktDynamicRenderingMultiviewClearTests.md` | No | Implementation file for `multiview_clear` dynamic rendering. Direct rewrite. |
| `vktRenderPassFragmentDensityMapTests.md` | No | Implementation file for `fragment_density_map`; covers `VK_EXT_fragment_density_map`, `VK_EXT_fragment_density_map2`, and the spec-version-3 `density_formula` subgroup. Direct rewrite. |

## Batch 4 — Extension-oriented families

Counted files: 6

| Old Level-3 page | Brief? | Reason |
|---|---:|---|
| `vktRenderPassDitheringTests.md` | No | Implementation file for `dithering`; `VK_EXT_legacy_dithering`. Direct rewrite. |
| `vktRenderPassSparseRenderTargetTests.md` | No | Implementation file for `sparserendertarget` (monolithic only). Direct rewrite. |
| `vktRenderPassMultiviewPerViewTests.md` | No | Implementation file for `multiview_per_view` (RP2 + Dynamic); covers `VK_QCOM_multiview_per_view_render_areas` and `VK_QCOM_multiview_per_view_viewports`. Direct rewrite. |
| `vktRenderPassSubpassMergeFeedbackTests.md` | No | Implementation file for `subpass_merge_feedback` (RP2); `VK_EXT_subpass_merge_feedback`. Direct rewrite. |
| `vktRenderPassNestedCommandBuffersTests.md` | No | Implementation file for `nested_command_buffers` (monolithic only); `VK_EXT_nested_command_buffer` + `VK_KHR_maintenance7`. Direct rewrite. |
| `vktRenderPassPerformanceCountersByRegionTests.md` | No | Implementation file for `performance_counters_by_region`; `VK_ARM_performance_counters_by_region`. Direct rewrite. |

## Level-2 Synthesis

After all batches finish and rewritten Level-3 pages stabilize:

- Rewrite `renderpasses.md` as the compact Level-2 category gateway.
- Include the folded dispatcher routing (rendering types, allocation kinds, pipeline-construction-type variants).
- Mark `dynamic_rendering` and its subgroups as non-VulkanSC-only.
- Route readers to the rewritten Level-3 pages.
- Avoid duplicating parameter matrices, support gates, and verification mechanics from Level-3 pages.
- After the ordinary Level-2 gateway sections are drafted, run the category Background Knowledge consolidation pass.

## Notes on Inspection Order

- The first Level-3 page inspected for this category should be `vktRenderPassTests.md` because it owns the dispatcher entry point and the core `simple`/`formats`/`attachment`/`attachment_write_mask`/`attachment_allocation`/`no_draw_clear_load_store` themes that every other file routes through the `suballocation`/`dedicated_allocation`/`no_draws` intermediate-node pattern.
- The `vktRenderPassTestsUtil.cpp` utility file and the `vktRenderPassGroupParams.hpp` parameter file do not have their own Level-3 pages; the rewritten Level-3 pages must reference them as supporting evidence when explaining `GroupParams`, `RenderingType`, and `SynchronizationType`.
- The dynamic-rendering families share the same `createRenderPassTestsInternal()` function with different `GroupParams`; the Level-3 page for `vktDynamicRenderingTests.md` must explain that the function is shared with the `suballocation`/`dedicated_allocation`/`no_draws` subtree under `dynamic_rendering`, while the dedicated dynamic-rendering files (`vktDynamicRenderingLocalReadTests.cpp`, etc.) own the subgroups unique to `dynamic_rendering`.
- The `vktRenderPassSubpassMergeFeedbackTests.cpp` group is registered only under `renderpass2`; this must be reflected accurately in its Level-3 page and in the Level-2 category tree.