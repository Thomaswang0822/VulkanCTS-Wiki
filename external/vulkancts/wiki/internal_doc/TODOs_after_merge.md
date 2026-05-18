# TODOs After Merge

## Purpose

Internal checklist for post-merge cleanup after merging upstream `main` into `merge_main_26-05-18`.

Goal: this file should preserve the Git-derived findings needed for Vulkan CTS wiki cleanup so we do not need to
re-run broad history comparisons to remember what must be handled.

## Evidence Baseline

- Merge branch: `merge_main_26-05-18`.
- Merge commit after conflict resolution: `5143e893129c68c70b09070b39c8240a95c2d121`.
- Merge commit parents:
  - local wiki parent: `d021ba9bba2698d6c6f975a9d4181367b0594958`
  - upstream main parent: `e6b2240610e7d1dcefd84c8c5c32f88306e05f87`
- Confirmed original common base: `634a3fc62d82c34de68c3b1add25e6b7f5777524`.
- Post-merge status was clean from `git status --short --branch`.
- `git diff --name-only --diff-filter=U` showed no unresolved conflicts after the merge commit.
- Only real merge conflict observed during merge was [external/.gitignore](../../../.gitignore), resolved by accepting
  upstream `main` side.
- Broad merge summary from `git show --stat --summary --format=fuller HEAD`:
  - `487 files changed`
  - `1256039 insertions(+)`
  - `1758911 deletions(-)`
- Vulkan-relevant pre-merge diff from base to `main`:
  - `189 files changed`
  - `31526 insertions(+)`
  - `25653 deletions(-)`
- Important scope rule from [SKILL.md](../../../../.agents/skills/wiki-analyzer/SKILL.md): factual wiki claims should be
  based on [external/vulkancts/](../../) and [apitests.adoc](../../../../doc/testspecs/VK/apitests.adoc). For this merge
  cleanup, the user narrowed practical impact checks to:
  - Vulkan source under [modules/vulkan](../modules/vulkan)
  - mustpass text files under [mustpass/main/vk-default](../mustpass/main/vk-default)
  - possibly a few other mustpass text files under [mustpass/main](../mustpass/main)

## Merge Conflict Resolution Already Done

- [x] Merge conflict in [external/.gitignore](../../../.gitignore) resolved.
- [x] Upstream `main` side accepted.
- [x] Merge commit completed successfully.
- [x] Post-merge conflict check showed no unresolved files.

## What Needs To Be Done

The merge itself is complete, and the remaining work is wiki-specific cleanup. Based on the Git diffs already
captured above, there are no added or deleted top-level Vulkan module directories under
[modules/vulkan](../modules/vulkan), so [README.md](../README.md) does not need new category rows or removed category
rows for this merge.

Most upstream changes outside Vulkan CTS source and Vulkan mustpass files do not affect the wiki content directly.
They should be ignored for this cleanup unless a later validation failure proves they affect our wiki tooling.

Changed Vulkan CTS modules whose categories are not started in [README.md](../README.md) also do not need immediate
wiki edits. Their source changes are already present on the merge branch, so when those categories are documented
later, the normal wiki-analyzer workflow will inspect the current source.

The immediate cleanup work is concentrated in three areas:

- [ ] Review completed wiki categories whose source files changed under [modules/vulkan](../modules/vulkan). These are
  listed in the next section with exact file paths. Update wiki pages only when the current source or mustpass files
  show that documented registration paths, test families, parameters, support gates, verification logic, or scope notes
  are stale.
- [ ] Check whether mustpass layout changes break [verify_registration_paths.py](../../../../.agents/skills/wiki-analyzer/scripts/verify_registration_paths.py), especially for categories whose mustpass files were renamed, moved, or deleted.
  Confirm this with validator runs before changing validator code.
- [x] Fix the [README.md](../README.md) tracker inconsistency. The progress table has 22 category rows marked
  done, and the statistics section now says `Completed Categories: 22/53`.

Mustpass layout changes that need attention:

- [renderpass.txt](../mustpass/main/vk-default/renderpass.txt) was deleted, while
  [renderpasses.txt](../mustpass/main/vk-default/renderpasses.txt) was modified.
- [monolithic.txt](../mustpass/main/vk-default/pipeline/monolithic/monolithic.txt) now lives under nested
  `pipeline/monolithic/`.
- [shader-object-unlinked-spirv.txt](../mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/shader-object-unlinked-spirv.txt) now lives under nested `pipeline/shader-object-unlinked-spirv/`.
- [image/astc-sample.txt](../mustpass/main/vk-default/image/astc-sample.txt) was deleted.
- [vksc-default/image/astc-sample.txt](../mustpass/main/vksc-default/image/astc-sample.txt) was deleted.

Upstream also added implementation files inside existing not-started categories. They are recorded later in this file
for future category writing scope, but they do not require immediate wiki documentation in this merge cleanup.

## Completed Categories Requiring Review

These categories are marked done in [README.md](../README.md) and had upstream source changes under
[modules/vulkan](../modules/vulkan) from base `634a3fc62d82c34de68c3b1add25e6b7f5777524` to `main`.

### api

- Wiki entry: [api.md](../categories/api.md)
- Source directory: [api](../modules/vulkan/api)
- Upstream changed source files:
  - [vktApiBlittingTests.cpp](../modules/vulkan/api/vktApiBlittingTests.cpp)
  - [vktApiBufferMemoryRequirementsTests.cpp](../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp)
  - [vktApiDebugUtilsTests.cpp](../modules/vulkan/api/vktApiDebugUtilsTests.cpp)
  - [vktApiDescriptorPoolTests.cpp](../modules/vulkan/api/vktApiDescriptorPoolTests.cpp)
  - [vktApiDeviceAddressCommandsTests.cpp](../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp)
  - [vktApiDeviceInitializationTests.cpp](../modules/vulkan/api/vktApiDeviceInitializationTests.cpp)
  - [vktApiExtensionDuplicatesTests.cpp](../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp)
  - [vktApiExternalMemoryTests.cpp](../modules/vulkan/api/vktApiExternalMemoryTests.cpp)
  - [vktApiFeatureInfo.cpp](../modules/vulkan/api/vktApiFeatureInfo.cpp)
  - [vktApiFillBufferTests.cpp](../modules/vulkan/api/vktApiFillBufferTests.cpp)
  - [vktApiImageCompressionControlTests.cpp](../modules/vulkan/api/vktApiImageCompressionControlTests.cpp)
  - [vktApiMaintenance3Check.cpp](../modules/vulkan/api/vktApiMaintenance3Check.cpp)
  - [vktApiObjectManagementTests.cpp](../modules/vulkan/api/vktApiObjectManagementTests.cpp)
  - [vktApiUseAfterCopyTests.cpp](../modules/vulkan/api/vktApiUseAfterCopyTests.cpp)
  - [vktApiVersionCheck.cpp](../modules/vulkan/api/vktApiVersionCheck.cpp)
- Related mustpass changed:
  - [api.txt](../mustpass/main/vk-default/api.txt)
- TODO:
  - [x] Check whether any changed files alter documented test families, parameter sets, support checks, or verification logic.
  - [x] Re-run registration-path validation for `api` after any wiki updates.
- Review result:
  - Updated stale source facts in [vktApiBlittingTests.md](../testfiles/api/vktApiBlittingTests.md),
    [vktApiDeviceAddressCommandsTests.md](../testfiles/api/vktApiDeviceAddressCommandsTests.md),
    [vktApiFillBufferTests.md](../testfiles/api/vktApiFillBufferTests.md),
    [vktApiMaintenance3Check.md](../testfiles/api/vktApiMaintenance3Check.md), and
    [vktApiObjectManagementTests.md](../testfiles/api/vktApiObjectManagementTests.md).
  - Fixed validator hygiene/link issues in [vktApiCopyBufferToBufferTests.md](../testfiles/api/vktApiCopyBufferToBufferTests.md),
    [vktApiDescriptorPoolTests.md](../testfiles/api/vktApiDescriptorPoolTests.md),
    [vktApiImageClearingTests.md](../testfiles/api/vktApiImageClearingTests.md), and
    [vktApiUseAfterCopyTests.md](../testfiles/api/vktApiUseAfterCopyTests.md).
  - No content update was needed for the other changed source files after Git-diff review because their changes were
    mechanical helper-signature/plumbing changes or already-covered Vulkan SC compile-guard adjustments.
  - Validation passed for the `api` scope: category link validation reported all local wiki links valid, and
    registration validation checked 421 paths successfully.

### binding_model

- Wiki entry: [binding_model.md](../categories/binding_model.md)
- Source directory: [binding_model](../modules/vulkan/binding_model)
- Upstream changed source files:
  - [vktBindingBufferDeviceAddressTests.cpp](../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp)
  - [vktBindingDescriptorBufferTests.cpp](../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp)
  - [vktBindingDescriptorHeapTests.cpp](../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp)
  - [vktBindingMutableTests.cpp](../modules/vulkan/binding_model/vktBindingMutableTests.cpp)
  - [vktBindingPushConstantBankTests.cpp](../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp)
  - [vktBindingUnusedInvalidDescriptorTests.cpp](../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp)
- Related mustpass changed:
  - [binding-model.txt](../mustpass/main/vk-default/binding-model.txt)
- TODO:
  - [ ] Review changed binding-model docs against current source and mustpass.

### draw

- Wiki entry: [draw.md](../categories/draw.md)
- Source directory: [draw](../modules/vulkan/draw)
- Upstream changed source files:
  - [vktDrawConcurrentTests.cpp](../modules/vulkan/draw/vktDrawConcurrentTests.cpp)
- TODO:
  - [ ] Check if the concurrency test documentation needs update.

### dynamic_state

- Wiki entry: [dynamic_state.md](../categories/dynamic_state.md)
- Source directory: [dynamic_state](../modules/vulkan/dynamic_state)
- Upstream changed source files:
  - [vktDynamicStateComputeTests.cpp](../modules/vulkan/dynamic_state/vktDynamicStateComputeTests.cpp)
- TODO:
  - [ ] Check whether compute dynamic-state support gates or test families changed.

### image

- Wiki entry: [image.md](../categories/image.md)
- Source directory: [image](../modules/vulkan/image)
- Upstream changed source files:
  - [vktImageDepthStencilSeparateTests.cpp](../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp)
  - [vktImageHostImageCopyTests.cpp](../modules/vulkan/image/vktImageHostImageCopyTests.cpp)
  - [vktImageMutableTests.cpp](../modules/vulkan/image/vktImageMutableTests.cpp)
  - [vktImageNonUniformOffsetSampleTests.cpp](../modules/vulkan/image/vktImageNonUniformOffsetSampleTests.cpp)
  - [vktImageTestsUtil.cpp](../modules/vulkan/image/vktImageTestsUtil.cpp)
  - [vktImageTestsUtil.hpp](../modules/vulkan/image/vktImageTestsUtil.hpp)
- Related mustpass changed:
  - [image/non-uniform-offset-sample.txt](../mustpass/main/vk-default/image/non-uniform-offset-sample.txt)
  - deleted [image/astc-sample.txt](../mustpass/main/vk-default/image/astc-sample.txt)
- TODO:
  - [ ] Determine whether deleted ASTC mustpass file affects any existing image wiki claims.
  - [ ] Review host image copy, mutable image, non-uniform offset sample, and depth/stencil docs.

### memory

- Wiki entry: [memory.md](../categories/memory.md)
- Source directory: [memory](../modules/vulkan/memory)
- Upstream changed source files:
  - [vktMemoryAddressBindingTests.cpp](../modules/vulkan/memory/vktMemoryAddressBindingTests.cpp)
  - [vktMemoryAllocationTests.cpp](../modules/vulkan/memory/vktMemoryAllocationTests.cpp)
  - [vktMemoryBindingTests.cpp](../modules/vulkan/memory/vktMemoryBindingTests.cpp)
  - [vktMemoryDeviceMemoryReportTests.cpp](../modules/vulkan/memory/vktMemoryDeviceMemoryReportTests.cpp)
  - [vktMemoryExternalMemoryHostTests.cpp](../modules/vulkan/memory/vktMemoryExternalMemoryHostTests.cpp)
  - [vktMemoryMappingTests.cpp](../modules/vulkan/memory/vktMemoryMappingTests.cpp)
- TODO:
  - [ ] Review changed memory docs for support-gate or parameter updates.

### pipeline

- Wiki entry: [pipeline.md](../categories/pipeline.md)
- Source directory: [pipeline](../modules/vulkan/pipeline)
- Upstream changed source files:
  - [vktPipelineBindVertexBuffers2Tests.cpp](../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp)
  - [vktPipelineBlendTests.cpp](../modules/vulkan/pipeline/vktPipelineBlendTests.cpp)
  - [vktPipelineDualBlendTests.cpp](../modules/vulkan/pipeline/vktPipelineDualBlendTests.cpp)
  - [vktPipelineExtendedDynamicStateTests.cpp](../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateTests.cpp)
  - [vktPipelineLibraryTests.cpp](../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp)
  - [vktPipelineMultisampleResolveMaint10Tests.cpp](../modules/vulkan/pipeline/vktPipelineMultisampleResolveMaint10Tests.cpp)
  - [vktPipelineMultisampleShaderFragmentMaskTests.cpp](../modules/vulkan/pipeline/vktPipelineMultisampleShaderFragmentMaskTests.cpp)
  - [vktPipelineNoPositionTests.cpp](../modules/vulkan/pipeline/vktPipelineNoPositionTests.cpp)
  - [vktPipelineNoQueuesTests.cpp](../modules/vulkan/pipeline/vktPipelineNoQueuesTests.cpp)
  - [vktPipelinePushDescriptorTests.cpp](../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp)
  - [vktPipelineRenderToImageTests.cpp](../modules/vulkan/pipeline/vktPipelineRenderToImageTests.cpp)
  - [vktPipelineShaderModuleIdentifierTests.cpp](../modules/vulkan/pipeline/vktPipelineShaderModuleIdentifierTests.cpp)
  - [vktPipelineTimestampTests.cpp](../modules/vulkan/pipeline/vktPipelineTimestampTests.cpp)
- Related mustpass changed:
  - [pipeline/fast-linked-library.txt](../mustpass/main/vk-default/pipeline/fast-linked-library.txt)
  - [pipeline-library.txt](../mustpass/main/vk-default/pipeline/pipeline-library.txt)
  - renamed nested [monolithic.txt](../mustpass/main/vk-default/pipeline/monolithic/monolithic.txt)
  - renamed nested [shader-object-unlinked-spirv.txt](../mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/shader-object-unlinked-spirv.txt)
- TODO:
  - [ ] Validate that the pipeline registration adapter still finds nested mustpass files.
  - [ ] Review changed pipeline Level-3 pages.

### query_pool

- Wiki entry: [query_pool.md](../categories/query_pool.md)
- Source directory: [query_pool](../modules/vulkan/query_pool)
- Upstream changed source files:
  - [vktQueryPoolDiscardTests.cpp](../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp)
  - [vktQueryPoolOcclusionTests.cpp](../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp)
- TODO:
  - [ ] Review query discard and occlusion docs.

### rasterization

- Wiki entry: [rasterization.md](../categories/rasterization.md)
- Source directory: [rasterization](../modules/vulkan/rasterization)
- Upstream changed source files:
  - [vktRasterizationTests.cpp](../modules/vulkan/rasterization/vktRasterizationTests.cpp)
- TODO:
  - [ ] Review rasterization root registration or implementation claims.

### renderpasses

- Wiki entry: [renderpasses.md](../categories/renderpasses.md)
- Source directory: [renderpass](../modules/vulkan/renderpass)
- Upstream changed source files:
  - [vktRenderPassCustomResolveTests.cpp](../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp)
  - [vktRenderPassDitheringTests.cpp](../modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp)
  - [vktRenderPassFragmentDensityMapTests.cpp](../modules/vulkan/renderpass/vktRenderPassFragmentDensityMapTests.cpp)
  - [vktRenderPassMultiviewPerViewTests.cpp](../modules/vulkan/renderpass/vktRenderPassMultiviewPerViewTests.cpp)
  - [vktRenderPassPerformanceCountersByRegionTests.cpp](../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp)
  - [vktRenderPassSubpassDependencyTests.cpp](../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp)
- Related mustpass changed:
  - deleted [renderpass.txt](../mustpass/main/vk-default/renderpass.txt)
  - modified [renderpasses.txt](../mustpass/main/vk-default/renderpasses.txt)
- TODO:
  - [ ] Confirm validator handles `renderpasses` rather than deleted `renderpass` file.
  - [ ] Review changed renderpass docs.

### shader_object

- Wiki entry: [shader_object.md](../categories/shader_object.md)
- Source directory: [shader_object](../modules/vulkan/shader_object)
- Upstream changed source files:
  - [vktShaderObjectApiTests.cpp](../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp)
  - [vktShaderObjectBinaryTests.cpp](../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp)
  - [vktShaderObjectBindingTests.cpp](../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp)
  - [vktShaderObjectMiscTests.cpp](../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp)
  - [vktShaderObjectRenderingTests.cpp](../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp)
- Related mustpass changed:
  - nested pipeline shader-object mustpass file moved to [shader-object-unlinked-spirv.txt](../mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/shader-object-unlinked-spirv.txt)
- TODO:
  - [ ] Validate shader-object registration adapter after mustpass move.
  - [ ] Review changed shader-object docs.

### synchronization

- Wiki entry: [synchronization.md](../categories/synchronization.md)
- Source directory: [synchronization](../modules/vulkan/synchronization)
- Upstream changed source files:
  - [vktGlobalPriorityQueueTests.cpp](../modules/vulkan/synchronization/vktGlobalPriorityQueueTests.cpp)
  - [vktGlobalPriorityQueueUtils.cpp](../modules/vulkan/synchronization/vktGlobalPriorityQueueUtils.cpp)
  - [vktSynchronizationBasicSemaphoreTests.cpp](../modules/vulkan/synchronization/vktSynchronizationBasicSemaphoreTests.cpp)
  - [vktSynchronizationCrossInstanceSharingTests.cpp](../modules/vulkan/synchronization/vktSynchronizationCrossInstanceSharingTests.cpp)
  - [vktSynchronizationInternallySynchronizedObjectsTests.cpp](../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp)
  - [vktSynchronizationInternallySynchronizedTests.cpp](../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedTests.cpp)
  - [vktSynchronizationOperationMultiQueueTests.cpp](../modules/vulkan/synchronization/vktSynchronizationOperationMultiQueueTests.cpp)
  - [vktSynchronizationSignalOrderTests.cpp](../modules/vulkan/synchronization/vktSynchronizationSignalOrderTests.cpp)
  - [vktSynchronizationSmokeTests.cpp](../modules/vulkan/synchronization/vktSynchronizationSmokeTests.cpp)
  - [vktSynchronizationTimelineSemaphoreTests.cpp](../modules/vulkan/synchronization/vktSynchronizationTimelineSemaphoreTests.cpp)
  - [vktSynchronizationWin32KeyedMutexTests.cpp](../modules/vulkan/synchronization/vktSynchronizationWin32KeyedMutexTests.cpp)
- TODO:
  - [ ] Review changed synchronization docs.
  - [ ] Also consider [synchronization2.md](../categories/synchronization2.md), because its Level-3 files share the same wiki folder.

### texture

- Wiki entry: [texture.md](../categories/texture.md)
- Source directory: [texture](../modules/vulkan/texture)
- Upstream changed source files:
  - [vktTextureTestUtil.cpp](../modules/vulkan/texture/vktTextureTestUtil.cpp)
- TODO:
  - [ ] Decide whether helper-only utility change affects any documented texture behavior.

### ycbcr

- Wiki entry: [ycbcr.md](../categories/ycbcr.md)
- Source directory: [ycbcr](../modules/vulkan/ycbcr)
- Upstream changed source files:
  - [vktYCbCrFormatTests.cpp](../modules/vulkan/ycbcr/vktYCbCrFormatTests.cpp)
  - [vktYCbCrUtil.cpp](../modules/vulkan/ycbcr/vktYCbCrUtil.cpp)
  - [vktYCbCrViewTests.cpp](../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp)
- Related mustpass changed:
  - [ycbcr.txt](../mustpass/main/vk-default/ycbcr.txt)
- TODO:
  - [ ] Review changed YCbCr docs and mustpass impact.

## Completed Categories Not Touched By Upstream Source Changes

No immediate post-merge content update is indicated from the source diff for these completed wiki categories:

- [info.md](../categories/info.md)
- [imageless_framebuffer.md](../categories/imageless_framebuffer.md)
- [image_processing.md](../categories/image_processing.md)
- [fragment_operations.md](../categories/fragment_operations.md)
- [clipping.md](../categories/clipping.md)
- [multiview.md](../categories/multiview.md)
- [geometry.md](../categories/geometry.md)

Caveat: if validator or mustpass changes reveal issues, some of these may still require mechanical link/path repairs.

## Affected Not-Started Categories

These upstream source changes are in categories that are not currently completed in [README.md](../README.md). No immediate
wiki content update is required, but future category work must use current source.

- [compute](../modules/vulkan/compute)
- [conditional_rendering](../modules/vulkan/conditional_rendering)
- [data_graph](../modules/vulkan/data_graph)
- [descriptor_indexing](../modules/vulkan/descriptor_indexing)
- [device_group](../modules/vulkan/device_group)
- [device_generated_commands](../modules/vulkan/device_generated_commands), tracked in wiki as `dgc`
- [fragment_shading_rate](../modules/vulkan/fragment_shading_rate)
- [mesh_shader](../modules/vulkan/mesh_shader)
- [postmortem](../modules/vulkan/postmortem)
- [protected_memory](../modules/vulkan/protected_memory)
- [ray_tracing](../modules/vulkan/ray_tracing), tracked in wiki as `ray_tracing_pipeline`
- [reconvergence](../modules/vulkan/reconvergence)
- [robustness](../modules/vulkan/robustness)
- [sc](../modules/vulkan/sc)
- [shaderexecutor](../modules/vulkan/shaderexecutor)
- [shaderrender](../modules/vulkan/shaderrender)
- [sparse_resources](../modules/vulkan/sparse_resources)
- [spirv_assembly](../modules/vulkan/spirv_assembly)
- [ssbo](../modules/vulkan/ssbo)
- [tensor](../modules/vulkan/tensor)
- [tessellation](../modules/vulkan/tessellation)
- [transform_feedback](../modules/vulkan/transform_feedback)
- [video](../modules/vulkan/video)
- [wsi](../modules/vulkan/wsi)

## New Files Inside Existing Not-Started Categories

These are not new top-level categories, but they may alter future writing scope:

- [vktDescriptorIndexingMiscTests.cpp](../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp)
- [vktDescriptorIndexingMiscTests.hpp](../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.hpp)
- [vktDGCGraphicsMultiviewTestsExt.cpp](../modules/vulkan/device_generated_commands/vktDGCGraphicsMultiviewTestsExt.cpp)
- [vktDGCGraphicsMultiviewTestsExt.hpp](../modules/vulkan/device_generated_commands/vktDGCGraphicsMultiviewTestsExt.hpp)
- [vktRayTracingAccelerationStructuresTestsModels.hpp](../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTestsModels.hpp)
- [vktRobustnessOOBAccessTests.cpp](../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp)
- [vktRobustnessOOBAccessTests.hpp](../modules/vulkan/robustness/vktRobustnessOOBAccessTests.hpp)
- [vktSSBOLayoutNestedUnsizedArraysTests.cpp](../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp)
- [vktSSBOLayoutNestedUnsizedArraysTests.hpp](../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.hpp)

## Mustpass Files Requiring Validator Attention

- [api.txt](../mustpass/main/vk-default/api.txt)
- [binding-model.txt](../mustpass/main/vk-default/binding-model.txt)
- [compute.txt](../mustpass/main/vk-default/compute.txt)
- [descriptor-indexing.txt](../mustpass/main/vk-default/descriptor-indexing.txt)
- [dgc.txt](../mustpass/main/vk-default/dgc.txt)
- [glsl.txt](../mustpass/main/vk-default/glsl.txt)
- [image/non-uniform-offset-sample.txt](../mustpass/main/vk-default/image/non-uniform-offset-sample.txt)
- [mesh-shader.txt](../mustpass/main/vk-default/mesh-shader.txt)
- [pipeline/fast-linked-library.txt](../mustpass/main/vk-default/pipeline/fast-linked-library.txt)
- [pipeline/monolithic/monolithic.txt](../mustpass/main/vk-default/pipeline/monolithic/monolithic.txt)
- [pipeline/pipeline-library.txt](../mustpass/main/vk-default/pipeline/pipeline-library.txt)
- [pipeline/shader-object-unlinked-spirv/shader-object-unlinked-spirv.txt](../mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/shader-object-unlinked-spirv.txt)
- [ray-tracing-pipeline.txt](../mustpass/main/vk-default/ray-tracing-pipeline.txt)
- [renderpasses.txt](../mustpass/main/vk-default/renderpasses.txt)
- [robustness.txt](../mustpass/main/vk-default/robustness.txt)
- [ssbo.txt](../mustpass/main/vk-default/ssbo.txt)
- [transform-feedback.txt](../mustpass/main/vk-default/transform-feedback.txt)
- [ycbcr.txt](../mustpass/main/vk-default/ycbcr.txt)
- [vksc-default/api.txt](../mustpass/main/vksc-default/api.txt)
- [vksc-default/binding-model.txt](../mustpass/main/vksc-default/binding-model.txt)
- [vksc-default/descriptor-indexing.txt](../mustpass/main/vksc-default/descriptor-indexing.txt)
- [vksc-default/glsl.txt](../mustpass/main/vksc-default/glsl.txt)
- [vksc-default/image/non-uniform-offset-sample.txt](../mustpass/main/vksc-default/image/non-uniform-offset-sample.txt)
- [vksc-default/pipeline/monolithic.txt](../mustpass/main/vksc-default/pipeline/monolithic.txt)
- [vksc-default/robustness.txt](../mustpass/main/vksc-default/robustness.txt)
- [vksc-default/ssbo.txt](../mustpass/main/vksc-default/ssbo.txt)

Deleted mustpass files observed:

- [image/astc-sample.txt](../mustpass/main/vk-default/image/astc-sample.txt)
- [renderpass.txt](../mustpass/main/vk-default/renderpass.txt)
- [vksc-default/image/astc-sample.txt](../mustpass/main/vksc-default/image/astc-sample.txt)

## Recommended Execution Order

- [ ] Validate [verify_registration_paths.py](../../../../.agents/skills/wiki-analyzer/scripts/verify_registration_paths.py) on a small set of high-risk categories:
  - `renderpasses`
  - `pipeline`
  - `shader_object`
  - `image`
- [ ] Fix validator discovery if nested or renamed mustpass files break validation.
- [x] Correct [README.md](../README.md) statistics if no contrary counting rule is intended.
- [ ] Review completed categories in decreasing risk order:
  - [ ] [pipeline](../categories/pipeline.md)
  - [x] [api](../categories/api.md)
  - [ ] [synchronization](../categories/synchronization.md) and [synchronization2](../categories/synchronization2.md)
  - [ ] [image](../categories/image.md)
  - [ ] [renderpasses](../categories/renderpasses.md)
  - [ ] [binding_model](../categories/binding_model.md)
  - [ ] [memory](../categories/memory.md)
  - [ ] [shader_object](../categories/shader_object.md)
  - [ ] [ycbcr](../categories/ycbcr.md)
  - [ ] [query_pool](../categories/query_pool.md)
  - [ ] [draw](../categories/draw.md)
  - [ ] [dynamic_state](../categories/dynamic_state.md)
  - [ ] [rasterization](../categories/rasterization.md)
  - [ ] [texture](../categories/texture.md)
- [ ] For each reviewed category, update only facts proven from current source or mustpass files.
- [x] Run category-scoped link validation with [validate_wiki_links.py](../../../../.agents/skills/wiki-analyzer/scripts/validate_wiki_links.py) for every edited category so far (`api` passed).
- [x] Re-run registration-path validation for every edited category so far (`api` passed).
- [ ] Before final commit, decide whether this internal TODO file is temporary and should be removed, because [SKILL.md](../../../../.agents/skills/wiki-analyzer/SKILL.md) says internal coordination artifacts should not be committed.
