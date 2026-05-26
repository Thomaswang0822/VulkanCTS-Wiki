# Renderpasses

## Overview

The renderpasses category tests Vulkan render pass functionality across three rendering models: legacy render passes (Vulkan 1.0), render pass 2 (VK_KHR_create_renderpass2), and dynamic rendering (VK_KHR_dynamic_rendering). It validates attachment management, subpass dependencies, multisample operations, depth/stencil resolve, fragment density maps, custom resolve, and numerous extension interactions. The historical Vulkan API test plan provides concise multipass background for this category by calling out data-flow configurations over target formats, target counts, load/store operations, resolve behavior, and dependencies ([`apitests.adoc`](../../../../doc/testspecs/VK/apitests.adoc#L302-L308)).

## Registration Entry Point

- **Function**: `createRenderPassesTests()` in [vktRenderPassTests.cpp](../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8692)
- **Registered group name**: `"renderpasses"` in [vktTestPackage.cpp](../../modules/vulkan/vktTestPackage.cpp#L1355)

## Top-Level Groups

| Group | Registration Path | Rendering Type |
|-------|-------------------|----------------|
| renderpass1 | `renderpasses.renderpass1` | RENDERING_TYPE_RENDERPASS_LEGACY |
| renderpass2 | `renderpasses.renderpass2` | RENDERING_TYPE_RENDERPASS2 |
| dynamic_rendering | `renderpasses.dynamic_rendering` | RENDERING_TYPE_DYNAMIC_RENDERING |

## Subgroup Structure

```
renderpasses/
  renderpass1/                                     (RENDERING_TYPE_RENDERPASS_LEGACY)
    depth_stencil_write_conditions
    multiple_subpasses_multiple_command_buffers
    custom_resolve
    remaining_array_layers
    performance_counters_by_region
    dithering
    fragment_density_map
    nested_command_buffers
    suballocation/
      simple / formats / attachment / attachment_write_mask / attachment_allocation
      sampleread / multisample / unused_attachment
      unused_attachment_sparse_filling / subpass_dependencies
      multisample_resolve / load_store_op_none
      unused_clear_attachments / clear_some_attachments
      sparse_render_target
    dedicated_allocation/
      (same sub-groups as suballocation)
    no_draws/
      no_draw_clear_load_store

  renderpass2/                                     (RENDERING_TYPE_RENDERPASS2)
    multiview_per_view
    depth_stencil_resolve
    custom_resolve
    remaining_array_layers
    performance_counters_by_region
    dithering
    fragment_density_map
    nested_command_buffers
    suballocation/
      (same as renderpass1, plus subpass_merge_feedback)
    dedicated_allocation/
      (same as suballocation)
    no_draws/
      no_draw_clear_load_store

  dynamic_rendering/                               (RENDERING_TYPE_DYNAMIC_RENDERING)
    primary_cmd_buff/
      depth_stencil_resolve / random / basic
      unused_attachments / local_read / local_read_maint10
      custom_resolve / multiview_per_view / multiview_clear
      performance_counters_by_region
      suballocation/ (same pattern, some exclusions)
      dedicated_allocation/
      no_draws/
    partial_secondary_cmd_buff/
      unused_attachments / local_read / custom_resolve
      performance_counters_by_region
      suballocation/ (secondary CB cases only)
      dedicated_allocation/
    complete_secondary_cmd_buff/
      depth_stencil_resolve
      performance_counters_by_region
      suballocation/
      dedicated_allocation/
    graphics_pipeline_library/
      depth_stencil_resolve
      performance_counters_by_region
      suballocation/ (limited set)
      dedicated_allocation/
```

Note: `dynamic_rendering` and its subgroups are excluded under Vulkan SC builds. Some subgroups are conditionally excluded based on pipeline construction type, secondary command buffer usage, and rendering type.

## File Inventory

### Registration / Dispatcher Files

| File | Role | Level-3 Doc |
|------|------|-------------|
| [vktRenderPassTests.cpp](../../modules/vulkan/renderpass/vktRenderPassTests.cpp) | Root registration + core test implementations | [vktRenderPassTests.md](../testfiles/renderpasses/vktRenderPassTests.md) |

### Implementation Files

| File | Registered Group | Rendering Types | Level-3 Doc |
|------|-----------------|-----------------|-------------|
| [vktRenderPassMultisampleTests.cpp](../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp) | `multisample` | All | [vktRenderPassMultisampleTests.md](../testfiles/renderpasses/vktRenderPassMultisampleTests.md) |
| [vktRenderPassMultisampleResolveTests.cpp](../../modules/vulkan/renderpass/vktRenderPassMultisampleResolveTests.cpp) | `multisample_resolve` | All | [vktRenderPassMultisampleResolveTests.md](../testfiles/renderpasses/vktRenderPassMultisampleResolveTests.md) |
| [vktRenderPassSampleReadTests.cpp](../../modules/vulkan/renderpass/vktRenderPassSampleReadTests.cpp) | `sampleread` | All | [vktRenderPassSampleReadTests.md](../testfiles/renderpasses/vktRenderPassSampleReadTests.md) |
| [vktRenderPassSubpassDependencyTests.cpp](../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp) | `subpass_dependencies` | All | [vktRenderPassSubpassDependencyTests.md](../testfiles/renderpasses/vktRenderPassSubpassDependencyTests.md) |
| [vktRenderPassUnusedAttachmentTests.cpp](../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentTests.cpp) | `unused_attachment` | All | [vktRenderPassUnusedAttachmentTests.md](../testfiles/renderpasses/vktRenderPassUnusedAttachmentTests.md) |
| [vktRenderPassUnusedClearAttachmentTests.cpp](../../modules/vulkan/renderpass/vktRenderPassUnusedClearAttachmentTests.cpp) | `unused_clear_attachments` | All (monolithic) | [vktRenderPassUnusedClearAttachmentTests.md](../testfiles/renderpasses/vktRenderPassUnusedClearAttachmentTests.md) |
| [vktRenderPassUnusedAttachmentSparseFillingTests.cpp](../../modules/vulkan/renderpass/vktRenderPassUnusedAttachmentSparseFillingTests.cpp) | `attachment_sparse_filling` | All | [vktRenderPassUnusedAttachmentSparseFillingTests.md](../testfiles/renderpasses/vktRenderPassUnusedAttachmentSparseFillingTests.md) |
| [vktRenderPassClearSomeAttachmentsTests.cpp](../../modules/vulkan/renderpass/vktRenderPassClearSomeAttachmentsTests.cpp) | `clear_some_attachments` | All (monolithic) | [vktRenderPassClearSomeAttachmentsTests.md](../testfiles/renderpasses/vktRenderPassClearSomeAttachmentsTests.md) |
| [vktRenderPassDepthStencilResolveTests.cpp](../../modules/vulkan/renderpass/vktRenderPassDepthStencilResolveTests.cpp) | `depth_stencil_resolve` | RP2 | [vktRenderPassDepthStencilResolveTests.md](../testfiles/renderpasses/vktRenderPassDepthStencilResolveTests.md) |
| [vktRenderPassDepthStencilWriteConditionsTests.cpp](../../modules/vulkan/renderpass/vktRenderPassDepthStencilWriteConditionsTests.cpp) | `depth_stencil_write_conditions` | RP1 | [vktRenderPassDepthStencilWriteConditionsTests.md](../testfiles/renderpasses/vktRenderPassDepthStencilWriteConditionsTests.md) |
| [vktRenderPassCustomResolveTests.cpp](../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp) | `custom_resolve` | RP1, RP2, Dynamic | [vktRenderPassCustomResolveTests.md](../testfiles/renderpasses/vktRenderPassCustomResolveTests.md) |
| [vktRenderPassFragmentDensityMapTests.cpp](../../modules/vulkan/renderpass/vktRenderPassFragmentDensityMapTests.cpp) | `fragment_density_map` | All (monolithic) | [vktRenderPassFragmentDensityMapTests.md](../testfiles/renderpasses/vktRenderPassFragmentDensityMapTests.md) |
| [vktRenderPassSparseRenderTargetTests.cpp](../../modules/vulkan/renderpass/vktRenderPassSparseRenderTargetTests.cpp) | `sparserendertarget` | All (monolithic) | [vktRenderPassSparseRenderTargetTests.md](../testfiles/renderpasses/vktRenderPassSparseRenderTargetTests.md) |
| [vktRenderPassLoadStoreOpNoneTests.cpp](../../modules/vulkan/renderpass/vktRenderPassLoadStoreOpNoneTests.cpp) | `load_store_op_none` | All | [vktRenderPassLoadStoreOpNoneTests.md](../testfiles/renderpasses/vktRenderPassLoadStoreOpNoneTests.md) |
| [vktRenderPassDitheringTests.cpp](../../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp) | `dithering` | All (monolithic) | [vktRenderPassDitheringTests.md](../testfiles/renderpasses/vktRenderPassDitheringTests.md) |
| [vktRenderPassRemainingArrayLayersTests.cpp](../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp) | `remaining_array_layers` | RP1, RP2 | [vktRenderPassRemainingArrayLayersTests.md](../testfiles/renderpasses/vktRenderPassRemainingArrayLayersTests.md) |
| [vktRenderPassPerformanceCountersByRegionTests.cpp](../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp) | `performance_counters_by_region` | All | [vktRenderPassPerformanceCountersByRegionTests.md](../testfiles/renderpasses/vktRenderPassPerformanceCountersByRegionTests.md) |
| [vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp](../../modules/vulkan/renderpass/vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp) | `multiple_subpasses_multiple_command_buffers` | RP1 | [vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.md](../testfiles/renderpasses/vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.md) |
| [vktRenderPassMultiviewPerViewTests.cpp](../../modules/vulkan/renderpass/vktRenderPassMultiviewPerViewTests.cpp) | `multiview_per_view` | RP2, Dynamic | [vktRenderPassMultiviewPerViewTests.md](../testfiles/renderpasses/vktRenderPassMultiviewPerViewTests.md) |
| [vktRenderPassSubpassMergeFeedbackTests.cpp](../../modules/vulkan/renderpass/vktRenderPassSubpassMergeFeedbackTests.cpp) | `subpass_merge_feedback` | RP2 | [vktRenderPassSubpassMergeFeedbackTests.md](../testfiles/renderpasses/vktRenderPassSubpassMergeFeedbackTests.md) |
| [vktRenderPassNestedCommandBuffersTests.cpp](../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp) | `nested_command_buffers` | All (monolithic) | [vktRenderPassNestedCommandBuffersTests.md](../testfiles/renderpasses/vktRenderPassNestedCommandBuffersTests.md) |
| [vktDynamicRenderingTests.cpp](../../modules/vulkan/renderpass/vktDynamicRenderingTests.cpp) | `basic` | Dynamic | [vktDynamicRenderingTests.md](../testfiles/renderpasses/vktDynamicRenderingTests.md) |
| [vktDynamicRenderingLocalReadTests.cpp](../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp) | `local_read` | Dynamic | [vktDynamicRenderingLocalReadTests.md](../testfiles/renderpasses/vktDynamicRenderingLocalReadTests.md) |
| [vktDynamicRenderingLocalReadMaint10Tests.cpp](../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadMaint10Tests.cpp) | `m10_feedback_loop` | Dynamic | [vktDynamicRenderingLocalReadMaint10Tests.md](../testfiles/renderpasses/vktDynamicRenderingLocalReadMaint10Tests.md) |
| [vktDynamicRenderingDepthStencilResolveTests.cpp](../../modules/vulkan/renderpass/vktDynamicRenderingDepthStencilResolveTests.cpp) | `depth_stencil_resolve` | Dynamic | [vktDynamicRenderingDepthStencilResolveTests.md](../testfiles/renderpasses/vktDynamicRenderingDepthStencilResolveTests.md) |
| [vktDynamicRenderingRandomTests.cpp](../../modules/vulkan/renderpass/vktDynamicRenderingRandomTests.cpp) | `random` | Dynamic | [vktDynamicRenderingRandomTests.md](../testfiles/renderpasses/vktDynamicRenderingRandomTests.md) |
| [vktDynamicRenderingUnusedAttachmentsTests.cpp](../../modules/vulkan/renderpass/vktDynamicRenderingUnusedAttachmentsTests.cpp) | `unused_attachments` | Dynamic | [vktDynamicRenderingUnusedAttachmentsTests.md](../testfiles/renderpasses/vktDynamicRenderingUnusedAttachmentsTests.md) |
| [vktDynamicRenderingMultiviewClearTests.cpp](../../modules/vulkan/renderpass/vktDynamicRenderingMultiviewClearTests.cpp) | `multiview_clear` | Dynamic | [vktDynamicRenderingMultiviewClearTests.md](../testfiles/renderpasses/vktDynamicRenderingMultiviewClearTests.md) |

### Utility Files (no Level-3 doc)

| File | Purpose |
|------|---------|
| [vktRenderPassTestsUtil.cpp](../../modules/vulkan/renderpass/vktRenderPassTestsUtil.cpp) | Shared render pass test utilities |
| [vktRenderPassGroupParams.hpp](../../modules/vulkan/renderpass/vktRenderPassGroupParams.hpp) | SharedGroupParams, RenderingType, SynchronizationType enums |

## Cross-File Recurring Test Families

| Theme | Files Involved | Description |
|-------|---------------|-------------|
| Attachment format/count | vktRenderPassTests.cpp | Core `simple`, `formats`, `attachment` groups test across 47+ color and 5 DS formats |
| Multisample | MultisampleTests, MultisampleResolveTests, SampleReadTests | Sample count iteration, resolve, and per-sample read |
| Depth/stencil resolve | DepthStencilResolveTests, DynamicRenderingDepthStencilResolveTests | Resolve mode iteration across formats and sample counts |
| Unused attachments | UnusedAttachmentTests, UnusedClearAttachmentTests, UnusedAttachmentSparseFillingTests, DynamicRenderingUnusedAttachmentsTests | Various patterns of unused attachments |
| Subpass dependencies | SubpassDependencyTests | External, implicit, self, and inter-subpass dependencies |
| Fragment density map | FragmentDensityMapTests | Static/deferred/dynamic FDM with offset variants; density_formula subgroup verifies spec version 3 texel-size formula (renderpass2 and dynamic_rendering only) |
| Custom resolve | CustomResolveTests | VK_EXT_custom_resolve across all rendering types; single_sample_clear test verifies no unnecessary clear of single-sample attachment (dynamic_rendering only) |
| Dynamic rendering local read | DynamicRenderingLocalReadTests, DynamicRenderingLocalReadMaint10Tests | Input attachment mapping and feedback loops |

## Cross-File Recurring Parameter Dimensions

| Dimension | Values | Files |
|-----------|--------|-------|
| RenderingType | RENDERPASS_LEGACY, RENDERPASS2, DYNAMIC_RENDERING | All (via GroupParams) |
| AllocationKind | SUBALLOCATED, DEDICATED | vktRenderPassTests.cpp |
| Sample counts | {2, 4, 8, 16, 32, 64} | Multisample, DS Resolve, SampleRead |
| Color formats | 47-50 formats | Multisample, MultisampleResolve, Formats |
| Depth/stencil formats | D16_UNORM, X8_D24, D32_SFLOAT, S8_UINT, D16_UNORM_S8_UINT, D24_UNORM_S8_UINT, D32_SFLOAT_S8_UINT | DS Resolve, Write Conditions, Custom Resolve |
| Load/Store ops | CLEAR, LOAD, DONT_CARE / STORE, DONT_CARE, NONE | Formats, UnusedAttachment, LoadStoreOpNone |
| Resolve modes | SAMPLE_ZERO, AVERAGE, MIN, MAX, NONE | DS Resolve (RP2 and Dynamic) |
| Pipeline construction | MONOLITHIC, FAST_LINKED_LIBRARY, SHADER_OBJECT | CustomResolve, DynamicRendering |
| Secondary command buffer | Inline, Partial secondary, Complete secondary | vktRenderPassTests.cpp (Dynamic sub-variants) |

## Cross-File Recurring Support Requirements

| Requirement | Files |
|-------------|-------|
| VK_KHR_create_renderpass2 | Most files (for RENDERPASS2 type) |
| VK_KHR_dynamic_rendering | Most files (for DYNAMIC_RENDERING type) |
| VK_KHR_dynamic_rendering_local_read | Multisample, SampleRead, SubpassDependency, UnusedAttachment, SparseFilling, LocalRead |
| VK_KHR_depth_stencil_resolve | DepthStencilResolveTests, DynamicRenderingDepthStencilResolveTests |
| VK_EXT_fragment_density_map / VK_EXT_fragment_density_map2 | FragmentDensityMapTests |
| VK_EXT_fragment_density_map spec version >= 3 | FragmentDensityMapTests (density_formula tests) |
| VK_EXT_custom_resolve | CustomResolveTests |
| VK_EXT_load_store_op_none / VK_KHR_load_store_op_none | LoadStoreOpNoneTests |
| VK_EXT_legacy_dithering | DitheringTests |
| VK_EXT_subpass_merge_feedback | SubpassMergeFeedbackTests |
| VK_EXT_nested_command_buffer / VK_KHR_maintenance7 | NestedCommandBuffersTests |
| VK_EXT_dynamic_rendering_unused_attachments | DynamicRenderingUnusedAttachmentsTests, DynamicRenderingTests |
| VK_KHR_dynamic_rendering_local_read | DynamicRenderingLocalReadTests, DynamicRenderingLocalReadMaint10Tests |
| VK_QCOM_multiview_per_view_render_areas / VK_QCOM_multiview_per_view_viewports | MultiviewPerViewTests |
| VK_ARM_performance_counters_by_region | PerformanceCountersByRegionTests |
| VK_EXT_shader_demote_to_helper_invocation | DepthStencilWriteConditionsTests |
| VK_KHR_shader_terminate_invocation | DepthStencilWriteConditionsTests |
| VK_EXT_shader_stencil_export | DepthStencilWriteConditionsTests, CustomResolveTests, LocalReadMaint10Tests |
| DEVICE_CORE_FEATURE_SAMPLE_RATE_SHADING | SampleRead, DS Resolve, FragmentDensityMap |
| DEVICE_CORE_FEATURE_GEOMETRY_SHADER | MultisampleResolve (multi-layer), SubpassDependency (self-dep), RemainingArrayLayers |
| DEVICE_CORE_FEATURE_INDEPENDENT_BLEND | vktRenderPassTests (attachment_write_mask) |

## Cross-File Recurring Verification Methods

| Method | Files | Description |
|--------|-------|-------------|
| Software reference rendering | vktRenderPassTests.cpp | Compute reference via renderReferenceValues, compare with verifyDepthAttachment/verifyStencilAttachment/pixel comparison |
| tcu::floatThresholdCompare | Most files | Threshold-based floating-point image comparison |
| tcu::intThresholdCompare | MultisampleResolve | Integer image comparison |
| tcu::dsThresholdCompare | MultiviewPerView, DynamicRenderingUnusedAttachments, DynamicRenderingMultiviewClear | Depth/stencil threshold comparison |
| Shader-internal validation | SampleRead, SparseFilling | Shader outputs pass/fail indicator; compared against expected constant |
| Properties/feedback query | SubpassMergeFeedback, DepthStencilResolve (misc) | Verify queried properties or merge feedback match expected |
| Expected value table lookup | DynamicRenderingDepthStencilResolve | Pre-computed depth/stencil values indexed by resolve mode and sample count |

## Notes

- The source directory is named `renderpass` (singular) but the registered group name is `renderpasses` (plural).
- A legacy mustpass file `renderpass.txt` previously existed in the mustpass directory but was **not referenced** by the main mustpass configuration (`vk-default.txt`) and has since been removed. Only `renderpasses.txt` is the official mustpass file.
- The `dynamic_rendering` group has four sub-variants (primary_cmd_buff, partial_secondary_cmd_buff, complete_secondary_cmd_buff, graphics_pipeline_library) that share the same `createRenderPassTestsInternal()` function with different GroupParams.
- Many test groups are conditionally excluded based on rendering type, pipeline construction type, secondary command buffer usage, and Vulkan SC builds.
