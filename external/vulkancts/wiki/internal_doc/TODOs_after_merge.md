# TODOs After Merge

Temporary tracker for the 2026-09 upstream sync. Do not treat this file as a durable merge history.

## Evidence Baseline

- Integration branch: `merge_main_26-09-04`.
- Merge commit: `d5e1620a698832983338f8a024733ccadf77db54` (`Merge branch 'main' into merge_main_26-09-04`).
- Local wiki parent: `d9deee7c26e57dd5e3806d76f63ccfc3e2d928db`.
- Upstream main parent: `cf7edb26d3be2d8763595ed08fdc41f3c1b1966f`.
- Upstream range to review: `e6b2240610e7d1dcefd84c8c5c32f88306e05f87..cf7edb26d3be2d8763595ed08fdc41f3c1b1966f`.
- Merge base: `e6b2240610e7d1dcefd84c8c5c32f88306e05f87`.
- Conflict status: no unresolved conflicts; the merge completed successfully.
- Current HEAD is the merge commit; no wiki refresh has been performed for this sync.
- Existing untracked inputs intentionally preserved: `external/vulkancts/wiki/internal_doc/git_diff_stat.txt` and `vkcts-wiki-pages/`.

## Operating Scope

- All category wiki pages are considered complete for this sync. Do not exclude a category merely because it was previously considered not-started.
- Review only the upstream Vulkan CTS source and mustpass evidence in the range above; do not use the aggregate repository diff as a proxy for wiki impact.
- Do not edit wiki pages in this phase. Each category item below remains pending until source/mustpass review proves either a minimal documentation update or a documented no-update decision.
- Treat `M` as a review signal, not proof that the page is stale. Update only registration hierarchy, test families, parameter dimensions, support gates, verification logic, scope/mustpass mapping, or source links that are shown stale by current evidence.
- For every reviewed category, record: decision (`update`/`no wiki update`), affected page(s), evidence inspected, validation result, and any unresolved source defect.
- Keep source, mustpass, specifications, existing wiki pages, and the Git index read-only during audit except for the eventual documentation edits authorized by the workflow.

## Immediate Structural Risks

- [~] Inspect the pipeline mustpass reshaping before category edits: structural inspection is complete, but the category refresh is still partial. `vk-default/pipeline` contains 95 added paths, 7 modified paths, and 1 deleted path; the `shader-object-unlinked-spirv` aggregate file was replaced by nested files. The current layout is present and contains 102 pipeline TXT files, including 99 files under construction-variant directories. Existing pipeline pages still need a complete source-to-page review.
- [x] Confirm recursive mustpass discovery and registration validation for `pipeline` and the shader-object-linked/unlinked variants. `verify_registration_paths.py pipeline` collected 452 paths and passed; the validator loaded the nested pipeline files. `verify_registration_paths.py shader_object` collected 83 paths and passed.
- [ ] Inspect newly added mustpass coverage: `image/store-load-consistency.txt`, `postmortem.txt`, `shader-object/m11-independent-sets.txt`, and `vksc-fraction-mandatory-tests.txt`.
- [ ] Check source/mustpass naming mappings: `renderpass` → `renderpasses`, `device_generated_commands` → `dgc`, `ray_tracing` → `ray_tracing_pipeline`, `modifiers` → `drm_format_modifiers`; also normalize hyphenated mustpass names such as `binding-model` and `query-pool`.
- [ ] Keep generated Vulkan/framework changes separate from user-facing category facts unless they change documented behavior or evidence links.

## Category Review Queue

Priority is an initial triage based on changed-path scale and visible add/delete/layout signals. It must be confirmed by reading the actual source and mustpass diffs.

### P0 — inspect first

- [ ] `api` — source `41` (A=6, M=35); mustpass `2` (M=2). Raw groups: `api`. Decision: pending.
  Source evidence:
  - `M` `external/vulkancts/modules/vulkan/api/CMakeLists.txt`
  - `A` `external/vulkancts/modules/vulkan/api/vktApiArrayTests.cpp`
  - `A` `external/vulkancts/modules/vulkan/api/vktApiArrayTests.hpp`
  - `M` `external/vulkancts/modules/vulkan/api/vktApiBlittingTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/api/vktApiBufferAndImageAllocationUtil.cpp`
  - `M` `external/vulkancts/modules/vulkan/api/vktApiBufferAndImageAllocationUtil.hpp`
  - `M` `external/vulkancts/modules/vulkan/api/vktApiBufferMarkerTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/api/vktApiBufferViewAccessTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/api/vktApiBufferViewCreateTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/api/vktApiCommandBuffersTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/api/vktApiCopiesAndBlittingUtil.cpp`
  - `M` `external/vulkancts/modules/vulkan/api/vktApiCopiesAndBlittingUtil.hpp`
  - `M` `external/vulkancts/modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/api/vktApiCopyBufferToImageTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp`
  - `M` `external/vulkancts/modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/api/vktApiCopyImageToBufferTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/api/vktApiCopyImageToImageTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/api/vktApiDebugUtilsTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/api/vktApiDescriptorPoolTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/api/vktApiDeviceInitializationTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/api/vktApiExternalMemoryTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/api/vktApiFeatureInfo.cpp`
  - `M` `external/vulkancts/modules/vulkan/api/vktApiFillBufferTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp`
  - `M` `external/vulkancts/modules/vulkan/api/vktApiFrameBoundaryTests.cpp`
  - `A` `external/vulkancts/modules/vulkan/api/vktApiGPAInterfaceTests.cpp`
  - `A` `external/vulkancts/modules/vulkan/api/vktApiGPAInterfaceTests.hpp`
  - `M` `external/vulkancts/modules/vulkan/api/vktApiGetMemoryCommitment.cpp`
  - `M` `external/vulkancts/modules/vulkan/api/vktApiImageClearingTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/api/vktApiImageCompressionControlTests.cpp`
  - `A` `external/vulkancts/modules/vulkan/api/vktApiMaintenance11Tests.cpp`
  - `A` `external/vulkancts/modules/vulkan/api/vktApiMaintenance11Tests.hpp`
  - `M` `external/vulkancts/modules/vulkan/api/vktApiObjectManagementTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/api/vktApiResolveTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/api/vktApiTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/api/vktApiUseAfterCopyTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/api/vktApiVersionCheck.cpp`
  Mustpass evidence:
  - `M` `external/vulkancts/mustpass/main/vk-default/api.txt`
  - `M` `external/vulkancts/mustpass/main/vksc-default/api.txt`
- [ ] `binding_model` — source `15` (A=4, M=11); mustpass `2` (M=2). Raw groups: `binding-model, binding_model`. Decision: pending.
  Source evidence:
  - `M` `external/vulkancts/modules/vulkan/binding_model/CMakeLists.txt`
  - `M` `external/vulkancts/modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp`
  - `A` `external/vulkancts/modules/vulkan/binding_model/vktBindingDescriptorHeapRandomTests.cpp`
  - `A` `external/vulkancts/modules/vulkan/binding_model/vktBindingDescriptorHeapRandomTests.hpp`
  - `M` `external/vulkancts/modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/binding_model/vktBindingDescriptorSetRandomTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp`
  - `A` `external/vulkancts/modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp`
  - `A` `external/vulkancts/modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.hpp`
  - `M` `external/vulkancts/modules/vulkan/binding_model/vktBindingModelTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/binding_model/vktBindingMutableTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/binding_model/vktBindingShaderAccessTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/binding_model/vktBindingStagesTests.cpp`
  Mustpass evidence:
  - `M` `external/vulkancts/mustpass/main/vk-default/binding-model.txt`
  - `M` `external/vulkancts/mustpass/main/vksc-default/binding-model.txt`
- [ ] `compute` — source `7` (M=7); mustpass `2` (M=2). Raw groups: `compute`. Decision: pending.
  Source evidence:
  - `M` `external/vulkancts/modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/compute/vktComputeCooperativeMatrixTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/compute/vktComputeIndirectComputeDispatchTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/compute/vktComputeShaderBuiltinVarTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp`
  Mustpass evidence:
  - `M` `external/vulkancts/mustpass/main/vk-default/compute.txt`
  - `M` `external/vulkancts/mustpass/main/vksc-default/compute.txt`
- [ ] `data_graph` — source `22` (A=10, M=12); mustpass `1` (M=1). Raw groups: `data-graph, data_graph`. Decision: pending.
  Source evidence:
  - `M` `external/vulkancts/modules/vulkan/data_graph/CMakeLists.txt`
  - `M` `external/vulkancts/modules/vulkan/data_graph/tosa/vktDataGraphTosaReference.hpp`
  - `M` `external/vulkancts/modules/vulkan/data_graph/tosa/vktDataGraphTosaSpirv.cpp`
  - `M` `external/vulkancts/modules/vulkan/data_graph/tosa/vktDataGraphTosaSpirv.hpp`
  - `M` `external/vulkancts/modules/vulkan/data_graph/tosa/vktDataGraphTosaUtil.hpp`
  - `M` `external/vulkancts/modules/vulkan/data_graph/vktDataGraphBasicTests.cpp`
  - `A` `external/vulkancts/modules/vulkan/data_graph/vktDataGraphDescriptorBufferTests.cpp`
  - `A` `external/vulkancts/modules/vulkan/data_graph/vktDataGraphDescriptorBufferTests.hpp`
  - `A` `external/vulkancts/modules/vulkan/data_graph/vktDataGraphExternalMemoryTests.cpp`
  - `A` `external/vulkancts/modules/vulkan/data_graph/vktDataGraphExternalMemoryTests.hpp`
  - `A` `external/vulkancts/modules/vulkan/data_graph/vktDataGraphImageAliasingTests.cpp`
  - `A` `external/vulkancts/modules/vulkan/data_graph/vktDataGraphImageAliasingTests.hpp`
  - `M` `external/vulkancts/modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp`
  - `A` `external/vulkancts/modules/vulkan/data_graph/vktDataGraphSpecializationConstantsTests.cpp`
  - `A` `external/vulkancts/modules/vulkan/data_graph/vktDataGraphSpecializationConstantsTests.hpp`
  - `M` `external/vulkancts/modules/vulkan/data_graph/vktDataGraphTestProvider.cpp`
  - `M` `external/vulkancts/modules/vulkan/data_graph/vktDataGraphTestUtil.cpp`
  - `M` `external/vulkancts/modules/vulkan/data_graph/vktDataGraphTestUtil.hpp`
  - `M` `external/vulkancts/modules/vulkan/data_graph/vktDataGraphTests.cpp`
  - `A` `external/vulkancts/modules/vulkan/data_graph/vktDataGraphUpdateAfterBindTests.cpp`
  - `A` `external/vulkancts/modules/vulkan/data_graph/vktDataGraphUpdateAfterBindTests.hpp`
  Mustpass evidence:
  - `M` `external/vulkancts/mustpass/main/vk-default/data-graph.txt`
- [ ] `dgc` — source `13` (A=4, M=9); mustpass `1` (M=1). Raw groups: `device_generated_commands, dgc`. Decision: pending.
  Source evidence:
  - `M` `external/vulkancts/modules/vulkan/device_generated_commands/CMakeLists.txt`
  - `M` `external/vulkancts/modules/vulkan/device_generated_commands/vktDGCComputeConditionalTestsExt.cpp`
  - `M` `external/vulkancts/modules/vulkan/device_generated_commands/vktDGCComputeLayoutTestsExt.cpp`
  - `M` `external/vulkancts/modules/vulkan/device_generated_commands/vktDGCComputeMiscTestsExt.cpp`
  - `M` `external/vulkancts/modules/vulkan/device_generated_commands/vktDGCComputePreprocessTestsExt.cpp`
  - `M` `external/vulkancts/modules/vulkan/device_generated_commands/vktDGCGraphicsMiscTestsExt.cpp`
  - `A` `external/vulkancts/modules/vulkan/device_generated_commands/vktDGCRayTracingConditionalTestsExt.cpp`
  - `A` `external/vulkancts/modules/vulkan/device_generated_commands/vktDGCRayTracingConditionalTestsExt.hpp`
  - `M` `external/vulkancts/modules/vulkan/device_generated_commands/vktDGCRayTracingTestsExt.cpp`
  - `M` `external/vulkancts/modules/vulkan/device_generated_commands/vktDGCRayTracingTestsExt.hpp`
  - `A` `external/vulkancts/modules/vulkan/device_generated_commands/vktDGCStatQueryTestsExt.cpp`
  - `A` `external/vulkancts/modules/vulkan/device_generated_commands/vktDGCStatQueryTestsExt.hpp`
  - `M` `external/vulkancts/modules/vulkan/device_generated_commands/vktDGCTests.cpp`
  Mustpass evidence:
  - `M` `external/vulkancts/mustpass/main/vk-default/dgc.txt`
- [ ] `image` — source `12` (M=12); mustpass `8` (A=2, M=6). Raw groups: `image`. Decision: pending.
  Source evidence:
  - `M` `external/vulkancts/modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/image/vktImageAtomicOperationTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/image/vktImageCompressionTranscodingSupport.cpp`
  - `M` `external/vulkancts/modules/vulkan/image/vktImageGeneralLayoutTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/image/vktImageHostImageCopyTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/image/vktImageLoadStoreTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/image/vktImageLoadStoreTests.hpp`
  - `M` `external/vulkancts/modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/image/vktImageMutableTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/image/vktImageSizeTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/image/vktImageTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/image/vktImageTranscodingSupportTests.cpp`
  Mustpass evidence:
  - `M` `external/vulkancts/mustpass/main/vk-default/image/2d-array-compatible.txt`
  - `M` `external/vulkancts/mustpass/main/vk-default/image/atomic-operations.txt`
  - `M` `external/vulkancts/mustpass/main/vk-default/image/general-layout.txt`
  - `M` `external/vulkancts/mustpass/main/vk-default/image/mutable.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/image/store-load-consistency.txt`
  - `M` `external/vulkancts/mustpass/main/vksc-default/image/atomic-operations.txt`
  - `M` `external/vulkancts/mustpass/main/vksc-default/image/mutable.txt`
  - `A` `external/vulkancts/mustpass/main/vksc-default/image/store-load-consistency.txt`
- [ ] `image_processing` — source `11` (A=4, M=7); mustpass `1` (M=1). Raw groups: `image-processing, image_processing`. Decision: pending.
  Source evidence:
  - `M` `external/vulkancts/modules/vulkan/image_processing/CMakeLists.txt`
  - `M` `external/vulkancts/modules/vulkan/image_processing/vktImageProcessingApiTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/image_processing/vktImageProcessingBase.cpp`
  - `M` `external/vulkancts/modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp`
  - `A` `external/vulkancts/modules/vulkan/image_processing/vktImageProcessingBoxFilterSamplingTests.cpp`
  - `A` `external/vulkancts/modules/vulkan/image_processing/vktImageProcessingBoxFilterSamplingTests.hpp`
  - `M` `external/vulkancts/modules/vulkan/image_processing/vktImageProcessingTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/image_processing/vktImageProcessingTestsUtil.cpp`
  - `M` `external/vulkancts/modules/vulkan/image_processing/vktImageProcessingTestsUtil.hpp`
  - `A` `external/vulkancts/modules/vulkan/image_processing/vktImageProcessingWeightImageSamplingTests.cpp`
  - `A` `external/vulkancts/modules/vulkan/image_processing/vktImageProcessingWeightImageSamplingTests.hpp`
  Mustpass evidence:
  - `M` `external/vulkancts/mustpass/main/vk-default/image-processing.txt`
- [ ] `memory` — source `18` (A=10, M=8); mustpass `2` (M=2). Raw groups: `memory`. Decision: pending.
  Source evidence:
  - `M` `external/vulkancts/modules/vulkan/memory/CMakeLists.txt`
  - `M` `external/vulkancts/modules/vulkan/memory/vktMemoryAddressBindingTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/memory/vktMemoryAllocationTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/memory/vktMemoryBindingTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/memory/vktMemoryDeviceMemoryReportTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/memory/vktMemoryMappingTests.cpp`
  - `A` `external/vulkancts/modules/vulkan/memory/vktMemoryOpaqueAndDmaImageTests.cpp`
  - `A` `external/vulkancts/modules/vulkan/memory/vktMemoryOpaqueAndDmaImageTests.hpp`
  - `A` `external/vulkancts/modules/vulkan/memory/vktMemoryPipelineBarrierComputeTests.cpp`
  - `A` `external/vulkancts/modules/vulkan/memory/vktMemoryPipelineBarrierComputeTests.hpp`
  - `A` `external/vulkancts/modules/vulkan/memory/vktMemoryPipelineBarrierGraphicsTests.cpp`
  - `A` `external/vulkancts/modules/vulkan/memory/vktMemoryPipelineBarrierGraphicsTests.hpp`
  - `A` `external/vulkancts/modules/vulkan/memory/vktMemoryPipelineBarrierTestUtils.cpp`
  - `A` `external/vulkancts/modules/vulkan/memory/vktMemoryPipelineBarrierTestUtils.hpp`
  - `M` `external/vulkancts/modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp`
  - `A` `external/vulkancts/modules/vulkan/memory/vktMemoryPipelineBarrierTransferTests.cpp`
  - `A` `external/vulkancts/modules/vulkan/memory/vktMemoryPipelineBarrierTransferTests.hpp`
  - `M` `external/vulkancts/modules/vulkan/memory/vktMemoryTests.cpp`
  Mustpass evidence:
  - `M` `external/vulkancts/mustpass/main/vk-default/memory.txt`
  - `M` `external/vulkancts/mustpass/main/vksc-default/memory.txt`
- [~] `pipeline` — source `37` (A=4, M=33); mustpass `103` (A=95, M=7, D=1). Raw groups: `pipeline`. Decision: partial update; do not consider this category complete. English files changed so far: `categories/pipeline.md`, `testfiles/pipeline/Cache.md`, `testfiles/pipeline/PrimitiveRestartIndex.md`, and `scripts/walkthrough_exceptions.py`. Added `gpl_collision` coverage to the cache page and documented the new `primitive_restart_index` family; no Chinese pages were modified. Validation passed so far: English structure for the two changed Level-3 pages, scoped links for the category page and two changed Level-3 pages, full pipeline registration paths (452 paths), shader-object registration paths (83 paths), and the wiki-writer unit suite (50 tests). Remaining findings: the upstream range also changes existing pipeline behavior/coverage that still requires page-by-page review, especially `InputAssembly.md`, `InputAttributeOffset.md`, `LegacyAttr.md`, `Library.md`, `Multisample.md`, `MultisampledRenderToSingleSampled.md`, `NoPosition.md`, `PushDescriptor.md`, `Timestamp.md`, `VertexInput.md`, `ExtendedDynamicState.md`, and related delegated pages. The current changes do not yet cover those findings.
  Source evidence:
  - `M` `external/vulkancts/modules/vulkan/pipeline/CMakeLists.txt`
  - `M` `external/vulkancts/modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp`
  - `M` `external/vulkancts/modules/vulkan/pipeline/vktPipelineBlendTests.cpp`
  - `A` `external/vulkancts/modules/vulkan/pipeline/vktPipelineCacheGplTests.cpp`
  - `A` `external/vulkancts/modules/vulkan/pipeline/vktPipelineCacheGplTests.hpp`
  - `M` `external/vulkancts/modules/vulkan/pipeline/vktPipelineCacheTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/pipeline/vktPipelineColorWriteEnableTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/pipeline/vktPipelineDerivativeTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/pipeline/vktPipelineDualBlendTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/pipeline/vktPipelineDualBlendTests.hpp`
  - `M` `external/vulkancts/modules/vulkan/pipeline/vktPipelineExtendedDynamicStateMiscTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/pipeline/vktPipelineExtendedDynamicStateTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/pipeline/vktPipelineInputAttributeOffsetTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/pipeline/vktPipelineLegacyAttrTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/pipeline/vktPipelineLibraryTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/pipeline/vktPipelineMultisampleImageTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/pipeline/vktPipelineMultisampleResolveRenderAreaTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/pipeline/vktPipelineMultisampleShaderFragmentMaskTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/pipeline/vktPipelineMultisampleTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/pipeline/vktPipelineNoPositionTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/pipeline/vktPipelineNoQueuesTests.cpp`
  - `A` `external/vulkancts/modules/vulkan/pipeline/vktPipelinePrimitiveRestartIndexTests.cpp`
  - `A` `external/vulkancts/modules/vulkan/pipeline/vktPipelinePrimitiveRestartIndexTests.hpp`
  - `M` `external/vulkancts/modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/pipeline/vktPipelineRenderToImageTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/pipeline/vktPipelineShaderModuleIdentifierTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/pipeline/vktPipelineStencilTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/pipeline/vktPipelineTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/pipeline/vktPipelineTimestampTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp`
  Mustpass evidence:
  - `M` `external/vulkancts/mustpass/main/vk-default/pipeline/fast-linked-library.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/attachment-feedback-loop-layout.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/bind-buffers-2.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/bind-point.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/blend-operation-advanced.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/blend.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/cache.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/color-write-enable-maxa.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/color-write-enable.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/creation-cache-control.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/creation-feedback.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/depth-range-unrestricted.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/depth.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/derivative.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/descriptor-limits.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/dynamic-control-points.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/dynamic-offset.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/dynamic-vertex-attribute.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/early-destroy.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/empty-fs.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/executable-properties.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/extended-dynamic-state.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/framebuffer-attachment.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/image-2d-view-3d-image.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/image-view.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/image.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/input-assembly.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/input-attribute-offset.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/interface-matching.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/logic-op-na-formats.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/logic-op.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/matched-attachments.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/max-varyings.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/misc.txt`
  - `M` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/monolithic.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/multisample-interpolation.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/multisample-shader-builtin.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/multisample-with-fragment-shading-rate.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/multisample.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/no-position.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/pipeline-binary.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/pipeline-cache.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/primitive-restart-index.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/push-constant.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/push-descriptor.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/render-to-image.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/sampler.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/shader-module-identifier.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/shader-stencil-export.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/sliced-view-of-3d-image.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/spec-constant.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/stencil.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/timestamp.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/vertex-input.txt`
  - `M` `external/vulkancts/mustpass/main/vk-default/pipeline/pipeline-library.txt`
  - `M` `external/vulkancts/mustpass/main/vk-default/pipeline/shader-object-linked-binary.txt`
  - `M` `external/vulkancts/mustpass/main/vk-default/pipeline/shader-object-linked-spirv.txt`
  - `M` `external/vulkancts/mustpass/main/vk-default/pipeline/shader-object-unlinked-binary.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/attachment-feedback-loop-layout.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/bind-buffers-2.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/bind-point.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/blend-operation-advanced.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/blend.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/cache.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/color-write-enable-maxa.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/color-write-enable.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/creation-feedback.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/depth-range-unrestricted.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/depth.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/descriptor-limits.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/dynamic-control-points.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/dynamic-offset.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/dynamic-vertex-attribute.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/early-destroy.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/empty-fs.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/extended-dynamic-state.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/framebuffer-attachment.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/image-2d-view-3d-image.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/image-view.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/image.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/input-assembly.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/input-attribute-offset.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/interface-matching.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/logic-op-na-formats.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/logic-op.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/max-varyings.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/misc.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/multisample-interpolation.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/multisample-with-fragment-shading-rate.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/multisample.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/no-position.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/primitive-restart-index.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/push-constant.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/push-descriptor.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/render-to-image.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/sampler.txt`
  - `D` `external/vulkancts/mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/shader-object-unlinked-spirv.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/shader-stencil-export.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/spec-constant.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/stencil.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/timestamp.txt`
  - `A` `external/vulkancts/mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/vertex-input.txt`
  - `M` `external/vulkancts/mustpass/main/vksc-default/pipeline/monolithic.txt`
- [ ] `query_pool` — source `1` (M=1); mustpass `2` (M=2). Raw groups: `query-pool, query_pool`. Decision: pending.
  Source evidence:
  - `M` `external/vulkancts/modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp`
  Mustpass evidence:
  - `M` `external/vulkancts/mustpass/main/vk-default/query-pool.txt`
  - `M` `external/vulkancts/mustpass/main/vksc-default/query-pool.txt`
- [ ] `ray_query` — source `8` (A=2, M=6); mustpass `1` (M=1). Raw groups: `ray-query, ray_query`. Decision: pending.
  Source evidence:
  - `M` `external/vulkancts/modules/vulkan/ray_query/CMakeLists.txt`
  - `M` `external/vulkancts/modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/ray_query/vktRayQueryBuiltinTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/ray_query/vktRayQueryMiscTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/ray_query/vktRayQueryOpacityMicromapTests.cpp`
  - `A` `external/vulkancts/modules/vulkan/ray_query/vktRayQueryOpacityMicromapTestsKHR.cpp`
  - `A` `external/vulkancts/modules/vulkan/ray_query/vktRayQueryOpacityMicromapTestsKHR.hpp`
  - `M` `external/vulkancts/modules/vulkan/ray_query/vktRayQueryTests.cpp`
  Mustpass evidence:
  - `M` `external/vulkancts/mustpass/main/vk-default/ray-query.txt`
- [ ] `ray_tracing_pipeline` — source `12` (A=2, M=10); mustpass `1` (M=1). Raw groups: `ray-tracing-pipeline, ray_tracing`. Decision: pending.
  Source evidence:
  - `M` `external/vulkancts/modules/vulkan/ray_tracing/CMakeLists.txt`
  - `M` `external/vulkancts/modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/ray_tracing/vktRayTracingLinearSweptSpheresTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/ray_tracing/vktRayTracingMiscTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/ray_tracing/vktRayTracingNullASTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/ray_tracing/vktRayTracingOpacityMicromapTests.cpp`
  - `A` `external/vulkancts/modules/vulkan/ray_tracing/vktRayTracingOpacityMicromapTestsKHR.cpp`
  - `A` `external/vulkancts/modules/vulkan/ray_tracing/vktRayTracingOpacityMicromapTestsKHR.hpp`
  - `M` `external/vulkancts/modules/vulkan/ray_tracing/vktRayTracingShaderExecutionReorderTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/ray_tracing/vktRayTracingTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp`
  Mustpass evidence:
  - `M` `external/vulkancts/mustpass/main/vk-default/ray-tracing-pipeline.txt`
- [ ] `renderpasses` — source `14` (A=2, M=12); mustpass `2` (M=2). Raw groups: `renderpass, renderpasses`. Decision: pending.
  Source evidence:
  - `M` `external/vulkancts/modules/vulkan/renderpass/CMakeLists.txt`
  - `M` `external/vulkancts/modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/renderpass/vktDynamicRenderingMultiviewClearTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/renderpass/vktDynamicRenderingTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/renderpass/vktRenderPassDitheringTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/renderpass/vktRenderPassFragmentDensityMapTests.cpp`
  - `A` `external/vulkancts/modules/vulkan/renderpass/vktRenderPassLowResolutionZTests.cpp`
  - `A` `external/vulkancts/modules/vulkan/renderpass/vktRenderPassLowResolutionZTests.hpp`
  - `M` `external/vulkancts/modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/renderpass/vktRenderPassTests.cpp`
  Mustpass evidence:
  - `M` `external/vulkancts/mustpass/main/vk-default/renderpasses.txt`
  - `M` `external/vulkancts/mustpass/main/vksc-default/renderpasses.txt`
- [ ] `robustness` — source `11` (M=11); mustpass `1` (M=1). Raw groups: `robustness`. Decision: pending.
  Source evidence:
  - `M` `external/vulkancts/modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/robustness/vktRobustnessBufferAccessTests.hpp`
  - `M` `external/vulkancts/modules/vulkan/robustness/vktRobustnessExtsTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/robustness/vktRobustnessTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/robustness/vktRobustnessUtil.cpp`
  - `M` `external/vulkancts/modules/vulkan/robustness/vktRobustnessUtil.hpp`
  - `M` `external/vulkancts/modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp`
  Mustpass evidence:
  - `M` `external/vulkancts/mustpass/main/vk-default/robustness.txt`
- [ ] `shader_object` — source `9` (A=2, M=7); mustpass `2` (A=1, M=1). Raw groups: `shader-object, shader_object`. Decision: pending.
  Source evidence:
  - `M` `external/vulkancts/modules/vulkan/shader_object/CMakeLists.txt`
  - `M` `external/vulkancts/modules/vulkan/shader_object/vktShaderObjectApiTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp`
  - `A` `external/vulkancts/modules/vulkan/shader_object/vktShaderObjectIndependentSetsTests.cpp`
  - `A` `external/vulkancts/modules/vulkan/shader_object/vktShaderObjectIndependentSetsTests.hpp`
  - `M` `external/vulkancts/modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/shader_object/vktShaderObjectTests.cpp`
  Mustpass evidence:
  - `A` `external/vulkancts/mustpass/main/vk-default/shader-object/m11-independent-sets.txt`
  - `M` `external/vulkancts/mustpass/main/vk-default/shader-object/rendering.txt`
- [ ] `spirv_assembly` — source `32` (A=2, M=30); mustpass `2` (M=2). Raw groups: `spirv-assembly, spirv_assembly`. Decision: pending.
  Source evidence:
  - `M` `external/vulkancts/modules/vulkan/spirv_assembly/CMakeLists.txt`
  - `M` `external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderCase.cpp`
  - `M` `external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderCase.hpp`
  - `M` `external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderTestUtil.cpp`
  - `M` `external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderTestUtil.hpp`
  - `M` `external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp`
  - `M` `external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmGraphicsShaderTestUtil.cpp`
  - `M` `external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmIntegerDotProductTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmNonSemanticInfoTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmOpSelectDifferentStridesTests.cpp`
  - `A` `external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmOpUndefTests.cpp`
  - `A` `external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmOpUndefTests.hpp`
  - `M` `external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmRelaxedWithForwardReferenceTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersionTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmTypeTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmUtils.hpp`
  - `M` `external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmVariableInitTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp`
  Mustpass evidence:
  - `M` `external/vulkancts/mustpass/main/vk-default/spirv-assembly.txt`
  - `M` `external/vulkancts/mustpass/main/vksc-default/spirv-assembly.txt`
- [ ] `texture` — source `6` (M=6); mustpass `2` (M=2). Raw groups: `texture`. Decision: pending.
  Source evidence:
  - `M` `external/vulkancts/modules/vulkan/texture/vktTextureCompressedFormatTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/texture/vktTextureFilteringExplicitLodTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/texture/vktTextureMipmapTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/texture/vktTextureSwizzleTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/texture/vktTextureTestUtil.cpp`
  - `M` `external/vulkancts/modules/vulkan/texture/vktTextureTestUtil.hpp`
  Mustpass evidence:
  - `M` `external/vulkancts/mustpass/main/vk-default/texture.txt`
  - `M` `external/vulkancts/mustpass/main/vksc-default/texture.txt`
- [ ] `video` — source `12` (M=12); mustpass `1` (M=1). Raw groups: `video`. Decision: pending.
  Source evidence:
  - `M` `external/vulkancts/modules/vulkan/video/CMakeLists.txt`
  - `M` `external/vulkancts/modules/vulkan/video/vktVideoBaseDecodeUtils.cpp`
  - `M` `external/vulkancts/modules/vulkan/video/vktVideoBaseDecodeUtils.hpp`
  - `M` `external/vulkancts/modules/vulkan/video/vktVideoCapabilitiesTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/video/vktVideoDecodeTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/video/vktVideoEncodeTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/video/vktVideoEncodeTestsAV1.cpp`
  - `M` `external/vulkancts/modules/vulkan/video/vktVideoFrameBuffer.cpp`
  - `M` `external/vulkancts/modules/vulkan/video/vktVideoFrameBuffer.hpp`
  - `M` `external/vulkancts/modules/vulkan/video/vktVideoProfilesValidationTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/video/vktVideoTestUtils.cpp`
  - `M` `external/vulkancts/modules/vulkan/video/vktVideoTestUtils.hpp`
  Mustpass evidence:
  - `M` `external/vulkancts/mustpass/main/vk-default/video.txt`
- [ ] `wsi` — source `18` (A=4, M=14); mustpass `1` (M=1). Raw groups: `wsi`. Decision: pending.
  Source evidence:
  - `M` `external/vulkancts/modules/vulkan/wsi/CMakeLists.txt`
  - `M` `external/vulkancts/modules/vulkan/wsi/vktWsiAcquireDrmDisplayTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/wsi/vktWsiColorSpaceTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/wsi/vktWsiDisplayControlTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/wsi/vktWsiDisplayTimingTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/wsi/vktWsiFullScreenExclusiveTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/wsi/vktWsiIncrementalPresentTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/wsi/vktWsiMaintenance1Tests.cpp`
  - `A` `external/vulkancts/modules/vulkan/wsi/vktWsiMultisampledRenderToSwapchainTests.cpp`
  - `A` `external/vulkancts/modules/vulkan/wsi/vktWsiMultisampledRenderToSwapchainTests.hpp`
  - `A` `external/vulkancts/modules/vulkan/wsi/vktWsiPreTransformTests.cpp`
  - `A` `external/vulkancts/modules/vulkan/wsi/vktWsiPreTransformTests.hpp`
  - `M` `external/vulkancts/modules/vulkan/wsi/vktWsiPresentIdWaitTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/wsi/vktWsiPresentTimingTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/wsi/vktWsiSharedPresentableImageTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/wsi/vktWsiSurfaceTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/wsi/vktWsiSwapchainTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/wsi/vktWsiTests.cpp`
  Mustpass evidence:
  - `M` `external/vulkancts/mustpass/main/vk-default/wsi.txt`
- [ ] `ycbcr` — source `7` (A=2, M=5); mustpass `2` (M=2). Raw groups: `ycbcr`. Decision: pending.
  Source evidence:
  - `M` `external/vulkancts/modules/vulkan/ycbcr/CMakeLists.txt`
  - `M` `external/vulkancts/modules/vulkan/ycbcr/vktYCbCrConversionTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/ycbcr/vktYCbCrFilteringTests.cpp`
  - `A` `external/vulkancts/modules/vulkan/ycbcr/vktYCbCrRenderAttachmentTests.cpp`
  - `A` `external/vulkancts/modules/vulkan/ycbcr/vktYCbCrRenderAttachmentTests.hpp`
  - `M` `external/vulkancts/modules/vulkan/ycbcr/vktYCbCrTests.cpp`
  Mustpass evidence:
  - `M` `external/vulkancts/mustpass/main/vk-default/ycbcr.txt`
  - `M` `external/vulkancts/mustpass/main/vksc-default/ycbcr.txt`

### P1 — inspect after P0

- [ ] `conditional_rendering` — source `7` (M=7); mustpass `0` (none). Raw groups: `conditional_rendering`. Decision: pending.
  Source evidence:
  - `M` `external/vulkancts/modules/vulkan/conditional_rendering/vktConditionalClearAttachmentTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/conditional_rendering/vktConditionalDispatchTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/conditional_rendering/vktConditionalDrawTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/conditional_rendering/vktConditionalDrawTests.hpp`
  - `M` `external/vulkancts/modules/vulkan/conditional_rendering/vktConditionalIgnoreTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/conditional_rendering/vktConditionalRenderingTestUtil.cpp`
  - `M` `external/vulkancts/modules/vulkan/conditional_rendering/vktConditionalTransformFeedbackTests.cpp`
  Mustpass evidence:
  - none
- [ ] `descriptor_indexing` — source `2` (M=2); mustpass `2` (M=2). Raw groups: `descriptor-indexing, descriptor_indexing`. Decision: pending.
  Source evidence:
  - `M` `external/vulkancts/modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp`
  Mustpass evidence:
  - `M` `external/vulkancts/mustpass/main/vk-default/descriptor-indexing.txt`
  - `M` `external/vulkancts/mustpass/main/vksc-default/descriptor-indexing.txt`
- [ ] `draw` — source `3` (M=3); mustpass `2` (M=2). Raw groups: `draw`. Decision: pending.
  Source evidence:
  - `M` `external/vulkancts/modules/vulkan/draw/vktDrawConcurrentTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/draw/vktDrawSampleAttributeTests.cpp`
  Mustpass evidence:
  - `M` `external/vulkancts/mustpass/main/vk-default/draw.txt`
  - `M` `external/vulkancts/mustpass/main/vksc-default/draw.txt`
- [ ] `drm_format_modifiers` — source `1` (M=1); mustpass `0` (none). Raw groups: `modifiers`. Decision: pending.
  Source evidence:
  - `M` `external/vulkancts/modules/vulkan/modifiers/vktModifiersTests.cpp`
  Mustpass evidence:
  - none
- [ ] `dynamic_state` — source `2` (M=2); mustpass `0` (none). Raw groups: `dynamic_state`. Decision: pending.
  Source evidence:
  - `M` `external/vulkancts/modules/vulkan/dynamic_state/vktDynamicStateComputeTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/dynamic_state/vktDynamicStateDiscardTests.cpp`
  Mustpass evidence:
  - none
- [ ] `fragment_shading_rate` — source `5` (M=5); mustpass `2` (M=2). Raw groups: `fragment-shading-rate, fragment_shading_rate`. Decision: pending.
  Source evidence:
  - `M` `external/vulkancts/modules/vulkan/fragment_shading_rate/vktAttachmentRateTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/fragment_shading_rate/vktFragmentShadingRateBasic.cpp`
  - `M` `external/vulkancts/modules/vulkan/fragment_shading_rate/vktFragmentShadingRateMiscTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/fragment_shading_rate/vktFragmentShadingRatePixelConsistency.cpp`
  - `M` `external/vulkancts/modules/vulkan/fragment_shading_rate/vktFragmentShadingRateTests.cpp`
  Mustpass evidence:
  - `M` `external/vulkancts/mustpass/main/vk-default/fragment-shading-rate.txt`
  - `M` `external/vulkancts/mustpass/main/vksc-default/fragment-shading-rate.txt`
- [ ] `geometry` — source `1` (M=1); mustpass `2` (M=2). Raw groups: `geometry`. Decision: pending.
  Source evidence:
  - `M` `external/vulkancts/modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp`
  Mustpass evidence:
  - `M` `external/vulkancts/mustpass/main/vk-default/geometry.txt`
  - `M` `external/vulkancts/mustpass/main/vksc-default/geometry.txt`
- [ ] `glsl` — source `0` (none); mustpass `2` (M=2). Raw groups: `glsl`. Decision: pending.
  Source evidence:
  - none
  Mustpass evidence:
  - `M` `external/vulkancts/mustpass/main/vk-default/glsl.txt`
  - `M` `external/vulkancts/mustpass/main/vksc-default/glsl.txt`
- [ ] `imageless_framebuffer` — source `1` (M=1); mustpass `2` (M=2). Raw groups: `imageless-framebuffer, imageless_framebuffer`. Decision: pending.
  Source evidence:
  - `M` `external/vulkancts/modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp`
  Mustpass evidence:
  - `M` `external/vulkancts/mustpass/main/vk-default/imageless-framebuffer.txt`
  - `M` `external/vulkancts/mustpass/main/vksc-default/imageless-framebuffer.txt`
- [ ] `memory_model` — source `1` (M=1); mustpass `0` (none). Raw groups: `memory_model`. Decision: pending.
  Source evidence:
  - `M` `external/vulkancts/modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp`
  Mustpass evidence:
  - none
- [ ] `mesh_shader` — source `3` (M=3); mustpass `1` (M=1). Raw groups: `mesh-shader, mesh_shader`. Decision: pending.
  Source evidence:
  - `M` `external/vulkancts/modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp`
  - `M` `external/vulkancts/modules/vulkan/mesh_shader/vktMeshShaderPropertyTestsEXT.cpp`
  - `M` `external/vulkancts/modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp`
  Mustpass evidence:
  - `M` `external/vulkancts/mustpass/main/vk-default/mesh-shader.txt`
- [ ] `multiview` — source `1` (M=1); mustpass `2` (M=2). Raw groups: `multiview`. Decision: pending.
  Source evidence:
  - `M` `external/vulkancts/modules/vulkan/multiview/vktMultiViewRenderTests.cpp`
  Mustpass evidence:
  - `M` `external/vulkancts/mustpass/main/vk-default/multiview.txt`
  - `M` `external/vulkancts/mustpass/main/vksc-default/multiview.txt`
- [ ] `protected_memory` — source `7` (M=7); mustpass `0` (none). Raw groups: `protected_memory`. Decision: pending.
  Source evidence:
  - `M` `external/vulkancts/modules/vulkan/protected_memory/vktProtectedMemContext.cpp`
  - `M` `external/vulkancts/modules/vulkan/protected_memory/vktProtectedMemContext.hpp`
  - `M` `external/vulkancts/modules/vulkan/protected_memory/vktProtectedMemUtils.cpp`
  - `M` `external/vulkancts/modules/vulkan/protected_memory/vktProtectedMemUtils.hpp`
  - `M` `external/vulkancts/modules/vulkan/protected_memory/vktProtectedMemWorkgroupStorageTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/protected_memory/vktProtectedMemWsiSwapchainTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/protected_memory/vktProtectedMemYCbCrConversionTests.cpp`
  Mustpass evidence:
  - none
- [ ] `reconvergence` — source `1` (M=1); mustpass `0` (none). Raw groups: `reconvergence`. Decision: pending.
  Source evidence:
  - `M` `external/vulkancts/modules/vulkan/reconvergence/vktReconvergenceTests.cpp`
  Mustpass evidence:
  - none
- [ ] `sparse_resources` — source `17` (M=17); mustpass `1` (M=1). Raw groups: `sparse-resources, sparse_resources`. Decision: pending.
  Source evidence:
  - `M` `external/vulkancts/modules/vulkan/sparse_resources/vktSparseResourcesBase.cpp`
  - `M` `external/vulkancts/modules/vulkan/sparse_resources/vktSparseResourcesBase.hpp`
  - `M` `external/vulkancts/modules/vulkan/sparse_resources/vktSparseResourcesBufferMemoryAliasing.cpp`
  - `M` `external/vulkancts/modules/vulkan/sparse_resources/vktSparseResourcesBufferRebind.cpp`
  - `M` `external/vulkancts/modules/vulkan/sparse_resources/vktSparseResourcesBufferSparseBinding.cpp`
  - `M` `external/vulkancts/modules/vulkan/sparse_resources/vktSparseResourcesBufferSparseResidency.cpp`
  - `M` `external/vulkancts/modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/sparse_resources/vktSparseResourcesImageBlockShapes.cpp`
  - `M` `external/vulkancts/modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp`
  - `M` `external/vulkancts/modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp`
  - `M` `external/vulkancts/modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp`
  - `M` `external/vulkancts/modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp`
  - `M` `external/vulkancts/modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp`
  - `M` `external/vulkancts/modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseBinding.cpp`
  - `M` `external/vulkancts/modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp`
  - `M` `external/vulkancts/modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.cpp`
  - `M` `external/vulkancts/modules/vulkan/sparse_resources/vktSparseResourcesTransferQueueTests.cpp`
  Mustpass evidence:
  - `M` `external/vulkancts/mustpass/main/vk-default/sparse-resources.txt`
- [ ] `ssbo` — source `4` (M=4); mustpass `0` (none). Raw groups: `ssbo`. Decision: pending.
  Source evidence:
  - `M` `external/vulkancts/modules/vulkan/ssbo/vktSSBOCornerCase.cpp`
  - `M` `external/vulkancts/modules/vulkan/ssbo/vktSSBOLayoutCase.cpp`
  - `M` `external/vulkancts/modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/ssbo/vktSSBOLayoutTests.cpp`
  Mustpass evidence:
  - none
- [ ] `synchronization` — source `15` (M=15); mustpass `2` (M=2). Raw groups: `synchronization`. Decision: pending.
  Source evidence:
  - `M` `external/vulkancts/modules/vulkan/synchronization/vktGlobalPriorityQueueTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/synchronization/vktGlobalPriorityQueueUtils.cpp`
  - `M` `external/vulkancts/modules/vulkan/synchronization/vktGlobalPriorityQueueUtils.hpp`
  - `M` `external/vulkancts/modules/vulkan/synchronization/vktSynchronizationBasicEventTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/synchronization/vktSynchronizationBasicSemaphoreTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/synchronization/vktSynchronizationCrossInstanceSharingTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/synchronization/vktSynchronizationOperation.cpp`
  - `M` `external/vulkancts/modules/vulkan/synchronization/vktSynchronizationOperation.hpp`
  - `M` `external/vulkancts/modules/vulkan/synchronization/vktSynchronizationOperationMultiQueueTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/synchronization/vktSynchronizationSignalOrderTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/synchronization/vktSynchronizationSmokeTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/synchronization/vktSynchronizationTimelineSemaphoreTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/synchronization/vktSynchronizationWin32KeyedMutexTests.cpp`
  Mustpass evidence:
  - `M` `external/vulkancts/mustpass/main/vk-default/synchronization.txt`
  - `M` `external/vulkancts/mustpass/main/vksc-default/synchronization.txt`
- [ ] `synchronization2` — source `0` (none); mustpass `2` (M=2). Raw groups: `synchronization2`. Decision: pending.
  Source evidence:
  - none
  Mustpass evidence:
  - `M` `external/vulkancts/mustpass/main/vk-default/synchronization2.txt`
  - `M` `external/vulkancts/mustpass/main/vksc-default/synchronization2.txt`
- [ ] `tessellation` — source `3` (M=3); mustpass `2` (M=2). Raw groups: `tessellation`. Decision: pending.
  Source evidence:
  - `M` `external/vulkancts/modules/vulkan/tessellation/vktTessellationMiscDrawTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/tessellation/vktTessellationMiscDrawTests.hpp`
  - `M` `external/vulkancts/modules/vulkan/tessellation/vktTessellationTests.cpp`
  Mustpass evidence:
  - `M` `external/vulkancts/mustpass/main/vk-default/tessellation.txt`
  - `M` `external/vulkancts/mustpass/main/vksc-default/tessellation.txt`
- [ ] `transform_feedback` — source `2` (M=2); mustpass `1` (M=1). Raw groups: `transform-feedback, transform_feedback`. Decision: pending.
  Source evidence:
  - `M` `external/vulkancts/modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/transform_feedback/vktTransformFeedbackSimpleTests.cpp`
  Mustpass evidence:
  - `M` `external/vulkancts/mustpass/main/vk-default/transform-feedback.txt`

### P2 — inspect for no-update or small update

- [ ] `amber` — source `2` (M=2); mustpass `0` (none). Raw groups: `amber`. Decision: pending.
  Source evidence:
  - `M` `external/vulkancts/modules/vulkan/amber/vktAmberTestCase.cpp`
  - `M` `external/vulkancts/modules/vulkan/amber/vktAmberTestCase.hpp`
  Mustpass evidence:
  - none
- [ ] `cooperative_vector` — source `1` (M=1); mustpass `0` (none). Raw groups: `cooperative_vector`. Decision: pending.
  Source evidence:
  - `M` `external/vulkancts/modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp`
  Mustpass evidence:
  - none
- [ ] `device_group` — source `1` (M=1); mustpass `0` (none). Raw groups: `device_group`. Decision: pending.
  Source evidence:
  - `M` `external/vulkancts/modules/vulkan/device_group/vktDeviceGroupRendering.cpp`
  Mustpass evidence:
  - none
- [ ] `info` — source `0` (none); mustpass `2` (M=2). Raw groups: `info`. Decision: pending.
  Source evidence:
  - none
  Mustpass evidence:
  - `M` `external/vulkancts/mustpass/main/vk-default/info.txt`
  - `M` `external/vulkancts/mustpass/main/vksc-default/info.txt`
- [ ] `postmortem` — source `11` (A=2, M=9); mustpass `1` (A=1). Raw groups: `postmortem`. Decision: pending.
  Source evidence:
  - `M` `external/vulkancts/modules/vulkan/postmortem/CMakeLists.txt`
  - `A` `external/vulkancts/modules/vulkan/postmortem/vktPostmortemCoreDeviceFaultTests.cpp`
  - `A` `external/vulkancts/modules/vulkan/postmortem/vktPostmortemCoreDeviceFaultTests.hpp`
  - `M` `external/vulkancts/modules/vulkan/postmortem/vktPostmortemDeviceFaultTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/postmortem/vktPostmortemDeviceLossTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/postmortem/vktPostmortemShaderTimeoutTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/postmortem/vktPostmortemTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/postmortem/vktPostmortemTests.hpp`
  - `M` `external/vulkancts/modules/vulkan/postmortem/vktPostmortemUseAfterFreeTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/postmortem/vktPostmortemUtil.cpp`
  - `M` `external/vulkancts/modules/vulkan/postmortem/vktPostmortemUtil.hpp`
  Mustpass evidence:
  - `A` `external/vulkancts/mustpass/main/vk-default/postmortem.txt`
- [ ] `rasterization` — source `1` (M=1); mustpass `0` (none). Raw groups: `rasterization`. Decision: pending.
  Source evidence:
  - `M` `external/vulkancts/modules/vulkan/rasterization/vktRasterizationDepthBiasControlTests.cpp`
  Mustpass evidence:
  - none
- [ ] `sc` — source `6` (M=6); mustpass `1` (M=1). Raw groups: `sc`. Decision: pending.
  Source evidence:
  - `M` `external/vulkancts/modules/vulkan/sc/vktApplicationParametersTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/sc/vktCommandPoolMemoryReservationTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/sc/vktDeviceObjectReservationTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/sc/vktFaultHandlingTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/sc/vktPipelineCacheSCTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/sc/vktPipelineIdentifierTests.cpp`
  Mustpass evidence:
  - `M` `external/vulkancts/mustpass/main/vksc-default/sc.txt`
- [ ] `shaderexecutor` — source `9` (M=9); mustpass `0` (none). Raw groups: `shaderexecutor`. Decision: pending.
  Source evidence:
  - `M` `external/vulkancts/modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/shaderexecutor/vktShaderCommonFunctionTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/shaderexecutor/vktShaderExecutor.cpp`
  - `M` `external/vulkancts/modules/vulkan/shaderexecutor/vktShaderExecutor.hpp`
  - `M` `external/vulkancts/modules/vulkan/shaderexecutor/vktShaderFConvertTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/shaderexecutor/vktShaderIntegerFunctionTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/shaderexecutor/vktShaderPackingFunctionTests.cpp`
  Mustpass evidence:
  - none
- [ ] `shaderrender` — source `7` (A=2, M=5); mustpass `0` (none). Raw groups: `shaderrender`. Decision: pending.
  Source evidence:
  - `M` `external/vulkancts/modules/vulkan/shaderrender/CMakeLists.txt`
  - `M` `external/vulkancts/modules/vulkan/shaderrender/vktShaderRender.cpp`
  - `M` `external/vulkancts/modules/vulkan/shaderrender/vktShaderRender.hpp`
  - `A` `external/vulkancts/modules/vulkan/shaderrender/vktShaderRenderHelperInvocationTests.cpp`
  - `A` `external/vulkancts/modules/vulkan/shaderrender/vktShaderRenderHelperInvocationTests.hpp`
  - `M` `external/vulkancts/modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp`
  Mustpass evidence:
  - none
- [ ] `subgroups` — source `16` (M=16); mustpass `0` (none). Raw groups: `subgroups`. Decision: pending.
  Source evidence:
  - `M` `external/vulkancts/modules/vulkan/subgroups/vktSubgroupsArithmeticTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/subgroups/vktSubgroupsBallotBroadcastTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/subgroups/vktSubgroupsBallotMasksTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/subgroups/vktSubgroupsBallotOtherTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/subgroups/vktSubgroupsBallotTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/subgroups/vktSubgroupsBuiltinMaskVarTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/subgroups/vktSubgroupsBuiltinVarTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/subgroups/vktSubgroupsClusteredTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/subgroups/vktSubgroupsPartitionedTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/subgroups/vktSubgroupsQuadTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/subgroups/vktSubgroupsShapeTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/subgroups/vktSubgroupsShuffleTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/subgroups/vktSubgroupsSizeControlTests.cpp`
  - `M` `external/vulkancts/modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp`
  - `M` `external/vulkancts/modules/vulkan/subgroups/vktSubgroupsVoteTests.cpp`
  Mustpass evidence:
  - none
- [ ] `tensor` — source `2` (M=2); mustpass `0` (none). Raw groups: `tensor`. Decision: pending.
  Source evidence:
  - `M` `external/vulkancts/modules/vulkan/tensor/vktTensorTestsUtil.cpp`
  - `M` `external/vulkancts/modules/vulkan/tensor/vktTensorTestsUtil.hpp`
  Mustpass evidence:
  - none
- [ ] `util` — source `3` (A=2, M=1); mustpass `0` (none). Raw groups: `util`. Decision: pending.
  Source evidence:
  - `M` `external/vulkancts/modules/vulkan/util/CMakeLists.txt`
  - `A` `external/vulkancts/modules/vulkan/util/vktIndependentSetsUtil.cpp`
  - `A` `external/vulkancts/modules/vulkan/util/vktIndependentSetsUtil.hpp`
  Mustpass evidence:
  - none

## Changed Source Outside a Category Page

- [ ] Review these root-level Vulkan module changes for cross-category impact; do not create a category decision from stat alone:
  - `M` `external/vulkancts/modules/vulkan/CMakeLists.txt`
  - `M` `external/vulkancts/modules/vulkan/vktBuildPrograms.cpp`
  - `M` `external/vulkancts/modules/vulkan/vktContextManager.cpp`
  - `M` `external/vulkancts/modules/vulkan/vktContextManager.hpp`
  - `M` `external/vulkancts/modules/vulkan/vktCustomInstancesDevices.cpp`
  - `M` `external/vulkancts/modules/vulkan/vktCustomInstancesDevices.hpp`
  - `M` `external/vulkancts/modules/vulkan/vktShaderLibrary.cpp`
  - `M` `external/vulkancts/modules/vulkan/vktTestCase.cpp`
  - `M` `external/vulkancts/modules/vulkan/vktTestCase.hpp`
  - `M` `external/vulkancts/modules/vulkan/vktTestGroupUtil.hpp`
  - `M` `external/vulkancts/modules/vulkan/vktTestPackage.cpp`
- [ ] Review these mustpass/framework-level changes for validator or global mapping impact:
  - `M` `external/vulkancts/mustpass/main/src/excluded-tests.txt`
  - `A` `external/vulkancts/mustpass/main/src/fraction-mandatory-tests-sc.txt`
  - `M` `external/vulkancts/mustpass/main/vk-default.txt`
  - `M` `external/vulkancts/mustpass/main/vk-fraction-mandatory-tests.txt`
  - `M` `external/vulkancts/mustpass/main/vksc-default.txt`
  - `A` `external/vulkancts/mustpass/main/vksc-fraction-mandatory-tests.txt`

These items are coordination/validator checks, not automatic requests for a new wiki page.

## Category Pages with No Paths in the Upstream Scope

The following existing category pages have no changed source/mustpass path under the scoped comparison. Record them as checked/no upstream-triggered review only after confirming the category mapping is not indirect:
- [ ] `clipping` — no direct path in `e6b2240610e7d1dcefd84c8c5c32f88306e05f87..cf7edb26d3be2d8763595ed08fdc41f3c1b1966f`.
- [ ] `depth` — no direct path in `e6b2240610e7d1dcefd84c8c5c32f88306e05f87..cf7edb26d3be2d8763595ed08fdc41f3c1b1966f`.
- [ ] `fragment_operations` — no direct path in `e6b2240610e7d1dcefd84c8c5c32f88306e05f87..cf7edb26d3be2d8763595ed08fdc41f3c1b1966f`.
- [ ] `fragment_shader_interlock` — no direct path in `e6b2240610e7d1dcefd84c8c5c32f88306e05f87..cf7edb26d3be2d8763595ed08fdc41f3c1b1966f`.
- [ ] `fragment_shading_barycentric` — no direct path in `e6b2240610e7d1dcefd84c8c5c32f88306e05f87..cf7edb26d3be2d8763595ed08fdc41f3c1b1966f`.
- [ ] `graphicsfuzz` — no direct path in `e6b2240610e7d1dcefd84c8c5c32f88306e05f87..cf7edb26d3be2d8763595ed08fdc41f3c1b1966f`.
- [ ] `ubo` — no direct path in `e6b2240610e7d1dcefd84c8c5c32f88306e05f87..cf7edb26d3be2d8763595ed08fdc41f3c1b1966f`.

Inventory check: `53` category pages found; `52` mapped categories have direct changed paths; `7` have none.

## Recommended Execution Order

1. [~] Pipeline mustpass layout/validator checks are structurally resolved and validated, but the pipeline category refresh remains partial; complete the remaining existing-page reviews before marking this item complete.
2. [ ] Review P0 categories in queue order, grouping only tightly coupled pairs: `ray_query` + `ray_tracing_pipeline`, `shader_object` + `pipeline`, and `synchronization` + `synchronization2`.
3. [ ] Review P1 categories and explicitly record no-update decisions where changes are mechanical.
4. [ ] Review P2 categories and all existing pages with no direct paths for indirect/global effects.
5. [ ] Run category-scoped link and registration validation after each edited batch; validate both members of shared-category groups.
6. [ ] Run the practical user-facing whole-wiki link sweep after all category decisions are complete.
7. [ ] Update `merge_update_log.md` with the concise durable sync entry.
8. [ ] Decide with the user whether this temporary tracker remains during review or is removed before final commit; do not delete it automatically.

## Completion Gate

- [ ] Every category queue item has an evidence-backed `update` or `no wiki update` decision.
- [ ] Every structural mustpass risk is resolved or explicitly deferred.
- [ ] Edited pages pass link validation and registration validation.
- [ ] User-facing global link sweep passes, with expected internal/non-user-facing findings identified separately.
- [ ] `merge_update_log.md` has the new sync entry.
- [ ] User has the final manual `git switch vkcts-wiki` / `git merge --no-ff merge_main_26-09-04` commands after review is complete.

