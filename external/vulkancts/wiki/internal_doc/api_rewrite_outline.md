# api Rewrite Outline

## Scope

- Category: `api`
- Old Level-2 page: `external/vulkancts/wiki/categories/api.md`
- Old Level-3 directory: `external/vulkancts/wiki/testfiles/api/`
- Source category directory: `external/vulkancts/modules/vulkan/api/`

## Page Count

- Old Level-3 pages found: 53
- Registration-only dispatcher pages to fold into Level-2: 2
- Implementation-bearing Level-3 pages to rewrite: 51
- Counted rewrite files for batching: 63
  - 11 Understanding Briefs
  - 51 rewritten Level-3 pages

## Dispatcher Decision

- `vktApiTests.cpp` should NOT be rewritten because it is registration-only. It assembles the 38 top-level groups into the `api` tree via `createApiTests()` and contains no test logic.
- `vktApiCopiesAndBlittingTests.cpp` should NOT be rewritten because it is registration-only. It dispatches the `copy_and_blit` family to 14 delegated implementation files via `addCopiesAndBlittingTests()` and friends.
- Fold category-specific dispatcher facts into the rewritten Level-2 `api` page:
  - direct category tree (38 top-level families);
  - the composite `buffer_view` group built locally in `vktApiTests.cpp`;
  - the `copy_and_blit` variant structure (core, dedicated_allocation, copy_commands2, sparse, multiplanar_xfer, dynamic_state, copy_memory_indirect, device_address, reinterpret) and its source-to-family routing to the 14 delegated files;
  - the 15 of 38 groups excluded from Vulkan SC via `#ifndef CTS_USES_VULKANSC`.

## Batch 1 — Foundational property and version checks

Counted files: 8

| Old Level-3 page | Brief? | Reason |
|---|---:|---|
| `vktApiVersionCheck.md` | No | Core mechanism is clear: validate device API version bound and proc-address resolution for core/extension functions. |
| `vktApiDriverPropertiesTests.md` | No | Property-value validation against spec minimums; direct rewrite. |
| `vktApiFeatureInfo.md` | No | Feature/property query reporting checks; direct rewrite. |
| `vktApiDeviceDrmPropertiesTests.md` | No | DRM property reporting checks; direct rewrite. |
| `vktApiDeviceInitializationTests.md` | No | Device creation configuration matrix; mechanism is clear. |
| `vktApiToolingInfoTests.md` | No | Tooling property query; direct rewrite. |
| `vktApiExtensionDuplicatesTests.md` | No | Extension deduplication contract; direct rewrite. |
| `vktApiGetDeviceProcAddrTests.md` | No | Proc-address resolution contract; direct rewrite. |

## Batch 2 — Maintenance checks and simple queries

Counted files: 8

| Old Level-3 page | Brief? | Reason |
|---|---:|---|
| `vktApiMaintenance3Check.md` | No | Property minimums and descriptor-set-layout support query; mechanism is clear. |
| `vktApiMaintenance6Check.md` | No | Maintenance6 property checks; direct rewrite. |
| `vktApiMaintenance7Tests.md` | No | Maintenance7 property checks; direct rewrite. |
| `vktApiFormatPropertiesExtendedKHRtests.md` | No | Extended format feature flags2 reporting; direct rewrite. |
| `vktApiPhysicalDeviceFormatPropertiesMaint5Tests.md` | No | Maintenance5 format properties; direct rewrite. |
| `vktApiGetMemoryCommitment.md` | No | Memory commitment query; direct rewrite. |
| `vktApiGranularityTests.md` | No | Submission granularity query; direct rewrite. |
| `vktApiImageCompressionControlTests.md` | No | Image compression control property reporting; direct rewrite. |

## Batch 3 — Buffer and buffer view families

Counted files: 8

| Old Level-3 page | Brief? | Reason |
|---|---:|---|
| `vktApiBufferTests.md` | No | Buffer creation/usage-flag/size matrix; pass/fail is creation and memory-requirement consistency. |
| `vktApiBufferMarkerTests.md` | No | Buffer marker write ordering; direct rewrite. |
| `vktApiBufferViewCreateTests.md` | No | Buffer view creation matrix; direct rewrite. |
| `vktApiBufferViewAccessTests.md` | No | Buffer view access pattern validation; direct rewrite. |
| `vktApiBufferMemoryRequirementsTests.md` | No | Memory requirement query consistency; direct rewrite. |
| `vktApiMemoryRequirementInvarianceTests.md` | No | Invariance of memory requirements across queries; direct rewrite. |
| `vktApiFillBufferTests.md` | No | Fill/update buffer byte-value verification; direct rewrite. |
| `vktApiNullHandleTests.md` | No | Null-handle API contract; direct rewrite. |

## Batch 4 — Object management and descriptor families

Counted files: 8

| Old Level-3 page | Brief? | Reason |
|---|---:|---|
| `vktApiObjectManagementTests.md` | Yes | Large object-type x threading x allocation-callback matrix with per-subgroup exclusion rules; brief needed to map the behavioral axis and failure causes before rewrite. |
| `vktApiDescriptorSetTests.md` | Yes | Descriptor set layout/update/copy variant matrix with multiple update templates; brief needed to identify the behavioral axis and validation rules. |
| `vktApiDescriptorPoolTests.md` | No | Descriptor pool allocation and free contract; mechanism is clear. |
| `vktApiCommandBuffersTests.md` | No | Command buffer lifecycle/recording/submission; direct rewrite. |
| `vktApiPipelineTests.md` | No | Pipeline creation and cache contract; direct rewrite. |
| `vktApiExternalMemoryTests.md` | No | External memory handle import/export contract; direct rewrite. |

## Batch 5 — Copy and blit simple transfers and smoke

Counted files: 8

| Old Level-3 page | Brief? | Reason |
|---|---:|---|
| `vktApiCopyBufferToBufferTests.md` | No | Bit-exact buffer-to-buffer copy with offset/region matrix; verification is CPU reference comparison. |
| `vktApiCopyImageToBufferTests.md` | No | Image-to-buffer copy with format matrix; verification is CPU reference comparison. |
| `vktApiCopyBufferToImageTests.md` | No | Buffer-to-image copy with format matrix; verification is CPU reference comparison. |
| `vktApiCopyDepthStencilToBufferTests.md` | No | Depth/stencil-to-buffer copy with aspect selection; mechanism is clear. |
| `vktApiCopyMemoryIndirectTests.md` | No | Indirect copy memory command contract; direct rewrite. |
| `vktApiCopiesAndBlittingDynamicStateMetaOpsTests.md` | No | Copy combined with dynamic-state meta operations; direct rewrite. |
| `vktApiDSColorBitCopyTests.md` | No | Depth/stencil color-bit copy contract; direct rewrite. |
| `vktApiSmokeTests.md` | No | Smoke test coverage of core API paths; direct rewrite. |

## Batch 6 — Copy and blit complex transfers part 1

Counted files: 8

| Old Level-3 page | Brief? | Reason |
|---|---:|---|
| `vktApiCopyImageToImageTests.md` | Yes | Format-compatibility, layout-transition, compression, and copy-mode matrix; brief needed to map the behavioral axis and failure causes. |
| `vktApiCopyBufferToDepthStencilTests.md` | Yes | Separate aspect selection, stencil bias, and dual-source layout rules; brief needed to clarify the validation logic. |
| `vktApiCopyDepthStencilMSAATests.md` | Yes | MSAA sample-resolve copy logic with per-sample aspect handling; brief needed to explain the resolve mechanism. |
| `vktApiBlittingTests.md` | Yes | Scaling, filtering, and format-compatibility matrix for `vkCmdBlitImage`; brief needed to map the behavioral axis. |

## Batch 7 — Copy and blit complex transfers part 2

Counted files: 8

| Old Level-3 page | Brief? | Reason |
|---|---:|---|
| `vktApiResolveTests.md` | Yes | Multisample resolve with format and sample-count matrix; brief needed to explain the resolve verification. |
| `vktApiCopyMultiplaneImageTransferQueueTests.md` | Yes | Multiplane YCbCr format disassembly and transfer-queue copy; brief needed to explain plane-by-plane copy logic. |
| `vktApiCopiesAndBlittingReinterpretTests.md` | Yes | Format reinterpretation between compatible formats; brief needed to clarify compatibility rules and validation. |
| `vktApiUseAfterCopyTests.md` | Yes | Indirect semantic validation by consuming copied data in later shader/draw work; brief needed to explain the consume-after-copy mechanism. |

## Batch 8 — Image clearing, fragment output, and remaining families

Counted files: 7

| Old Level-3 page | Brief? | Reason |
|---|---:|---|
| `vktApiImageClearingTests.md` | Yes | Clear-color, format, layout, and allocation matrix for `vkCmdClearColorImage`/`ClearAttachments`; brief needed to map the behavioral axis and tolerance rules. |
| `vktApiFragmentShaderOutputTests.md` | No | Fragment shader output interface validation; direct rewrite. |
| `vktApiFrameBoundaryTests.md` | No | Frame boundary extension contract; direct rewrite. |
| `vktApiDeviceAddressCommandsTests.md` | No | Device address command contract; direct rewrite. |
| `vktApiPerformanceCountersByRegionTests.md` | No | Performance counter by region query; direct rewrite. |
| `vktApiDebugUtilsTests.md` | No | Debug utils messenger/callback contract; direct rewrite. |

## Level-3 Output Filenames

All rewritten Level-3 pages use the shortened CamelCase family/source suffix style, written to `external/vulkancts/wiki/testfiles/api/`:

| Old page | New page |
|---|---|
| `vktApiVersionCheck.md` | `VersionCheck.md` |
| `vktApiDriverPropertiesTests.md` | `DriverProperties.md` |
| `vktApiFeatureInfo.md` | `FeatureInfo.md` |
| `vktApiDeviceDrmPropertiesTests.md` | `DeviceDrmProperties.md` |
| `vktApiDeviceInitializationTests.md` | `DeviceInitialization.md` |
| `vktApiToolingInfoTests.md` | `ToolingInfo.md` |
| `vktApiExtensionDuplicatesTests.md` | `ExtensionDuplicates.md` |
| `vktApiGetDeviceProcAddrTests.md` | `GetDeviceProcAddr.md` |
| `vktApiMaintenance3Check.md` | `Maintenance3Check.md` |
| `vktApiMaintenance6Check.md` | `Maintenance6Check.md` |
| `vktApiMaintenance7Tests.md` | `Maintenance7.md` |
| `vktApiFormatPropertiesExtendedKHRtests.md` | `FormatPropertiesExtendedKHR.md` |
| `vktApiPhysicalDeviceFormatPropertiesMaint5Tests.md` | `PhysicalDeviceFormatPropertiesMaint5.md` |
| `vktApiGetMemoryCommitment.md` | `GetMemoryCommitment.md` |
| `vktApiGranularityTests.md` | `Granularity.md` |
| `vktApiImageCompressionControlTests.md` | `ImageCompressionControl.md` |
| `vktApiBufferTests.md` | `Buffer.md` |
| `vktApiBufferMarkerTests.md` | `BufferMarker.md` |
| `vktApiBufferViewCreateTests.md` | `BufferViewCreate.md` |
| `vktApiBufferViewAccessTests.md` | `BufferViewAccess.md` |
| `vktApiBufferMemoryRequirementsTests.md` | `BufferMemoryRequirements.md` |
| `vktApiMemoryRequirementInvarianceTests.md` | `MemoryRequirementInvariance.md` |
| `vktApiFillBufferTests.md` | `FillBuffer.md` |
| `vktApiNullHandleTests.md` | `NullHandle.md` |
| `vktApiObjectManagementTests.md` | `ObjectManagement.md` |
| `vktApiDescriptorSetTests.md` | `DescriptorSet.md` |
| `vktApiDescriptorPoolTests.md` | `DescriptorPool.md` |
| `vktApiCommandBuffersTests.md` | `CommandBuffers.md` |
| `vktApiPipelineTests.md` | `Pipeline.md` |
| `vktApiExternalMemoryTests.md` | `ExternalMemory.md` |
| `vktApiCopyBufferToBufferTests.md` | `CopyBufferToBuffer.md` |
| `vktApiCopyImageToBufferTests.md` | `CopyImageToBuffer.md` |
| `vktApiCopyBufferToImageTests.md` | `CopyBufferToImage.md` |
| `vktApiCopyDepthStencilToBufferTests.md` | `CopyDepthStencilToBuffer.md` |
| `vktApiCopyMemoryIndirectTests.md` | `CopyMemoryIndirect.md` |
| `vktApiCopiesAndBlittingDynamicStateMetaOpsTests.md` | `CopiesAndBlittingDynamicStateMetaOps.md` |
| `vktApiDSColorBitCopyTests.md` | `DSColorBitCopy.md` |
| `vktApiSmokeTests.md` | `Smoke.md` |
| `vktApiCopyImageToImageTests.md` | `CopyImageToImage.md` |
| `vktApiCopyBufferToDepthStencilTests.md` | `CopyBufferToDepthStencil.md` |
| `vktApiCopyDepthStencilMSAATests.md` | `CopyDepthStencilMSAA.md` |
| `vktApiBlittingTests.md` | `Blitting.md` |
| `vktApiResolveTests.md` | `Resolve.md` |
| `vktApiCopyMultiplaneImageTransferQueueTests.md` | `CopyMultiplaneImageTransferQueue.md` |
| `vktApiCopiesAndBlittingReinterpretTests.md` | `CopiesAndBlittingReinterpret.md` |
| `vktApiUseAfterCopyTests.md` | `UseAfterCopy.md` |
| `vktApiImageClearingTests.md` | `ImageClearing.md` |
| `vktApiFragmentShaderOutputTests.md` | `FragmentShaderOutput.md` |
| `vktApiFrameBoundaryTests.md` | `FrameBoundary.md` |
| `vktApiDeviceAddressCommandsTests.md` | `DeviceAddressCommands.md` |
| `vktApiPerformanceCountersByRegionTests.md` | `PerformanceCountersByRegion.md` |
| `vktApiDebugUtilsTests.md` | `DebugUtils.md` |

## Level-2 Synthesis

After all batches finish and rewritten Level-3 pages stabilize:

- Rewrite `api.md` as the compact Level-2 category gateway.
- Include folded dispatcher information for both `vktApiTests.cpp` (root) and `vktApiCopiesAndBlittingTests.cpp` (nested), since both are registration-only.
- Route readers to the 51 rewritten Level-3 pages via the navigation table.
- The `copy_and_blit` family is represented by 14 rewritten Level-3 pages; the Level-2 navigation table groups them under a `copy_and_blit` heading and notes the shared allocation/queue/extension variant structure.
- Avoid duplicating detailed parameter matrices, verification mechanics, and source appendices from Level-3 pages.
- After the ordinary Level-2 gateway sections are drafted, run the category Background Knowledge consolidation pass.
