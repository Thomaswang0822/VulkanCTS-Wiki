# Renderpasses Category Progress Tracker

## Category Info
- **Category name**: renderpasses
- **Source directory**: `external/vulkancts/modules/vulkan/renderpass/`
- **Root registration file**: `vktRenderPassTests.cpp`
- **Root registration function**: `createRenderPassesTests()`
- **Registered group name**: `"renderpasses"`

## renderpass.txt vs renderpasses.txt
- `renderpasses.txt` is the **official** mustpass file (referenced in `vk-default.txt`)
- `renderpass.txt` is a **legacy/unused** file (NOT referenced in `vk-default.txt`)
- `renderpass.txt` contains `dEQP-VK.renderpass.*` paths from an older test structure
- `renderpass` is NOT a separate category; it's historical

## Top-Level Groups (Count: 3)

| # | Header File | Factory Function | Verified Group Name | Status |
|---|-------------|-----------------|---------------------|--------|
| 1 | (same file) | `createRenderPassTests()` | `renderpass1` | ⬜ |
| 2 | (same file) | `createRenderPass2Tests()` | `renderpass2` | ⬜ |
| 3 | (same file) | `createDynamicRenderingTests()` | `dynamic_rendering` | ⬜ |

Note: All three top-level groups are created within `vktRenderPassTests.cpp` itself, not in separate registration files. The included headers are for nested subgroups.

## Implementation Files (Included by Root Registration File)

### Shared Utilities (no Level-3 doc needed)
- `vktRenderPassTestsUtil.cpp/.hpp` - utility infrastructure
- `vktRenderPassGroupParams.hpp` - shared GroupParams struct

### VKSC + VK Files
| # | File | Creates Group | Verified Group Name | Level-3 Doc |
|---|------|--------------|---------------------|-------------|
| 1 | vktRenderPassMultisampleTests.cpp | suballocation subgroup | ⬜ | ⬜ |
| 2 | vktRenderPassMultisampleResolveTests.cpp | suballocation subgroup | ⬜ | ⬜ |
| 3 | vktRenderPassClearSomeAttachmentsTests.cpp | suballocation subgroup | ⬜ | ⬜ |
| 4 | vktRenderPassDepthStencilResolveTests.cpp | renderpass2 root | ⬜ | ⬜ |
| 5 | vktRenderPassPerformanceCountersByRegionTests.cpp | rendering root | ⬜ | ⬜ |
| 6 | vktRenderPassSampleReadTests.cpp | suballocation subgroup | ⬜ | ⬜ |
| 7 | vktRenderPassSubpassDependencyTests.cpp | suballocation subgroup | ⬜ | ⬜ |
| 8 | vktRenderPassUnusedAttachmentSparseFillingTests.cpp | suballocation subgroup | ⬜ | ⬜ |
| 9 | vktRenderPassUnusedAttachmentTests.cpp | suballocation subgroup | ⬜ | ⬜ |
| 10 | vktRenderPassUnusedClearAttachmentTests.cpp | suballocation subgroup | ⬜ | ⬜ |
| 11 | vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp | renderpass1 root | ⬜ | ⬜ |
| 12 | vktRenderPassRemainingArrayLayersTests.cpp | rendering root | ⬜ | ⬜ |
| 13 | vktRenderPassMultiviewPerViewTests.cpp | renderpass2/dynamic root | ⬜ | ⬜ |

### VK-Only Files (not available in VKSC)
| # | File | Creates Group | Verified Group Name | Level-3 Doc |
|---|------|--------------|---------------------|-------------|
| 14 | vktRenderPassFragmentDensityMapTests.cpp | rendering root | ⬜ | ⬜ |
| 15 | vktRenderPassSparseRenderTargetTests.cpp | suballocation subgroup | ⬜ | ⬜ |
| 16 | vktRenderPassLoadStoreOpNoneTests.cpp | suballocation subgroup | ⬜ | ⬜ |
| 17 | vktRenderPassDitheringTests.cpp | rendering root | ⬜ | ⬜ |
| 18 | vktDynamicRenderingTests.cpp | dynamic_rendering root | ⬜ | ⬜ |
| 19 | vktDynamicRenderingLocalReadTests.cpp | dynamic_rendering root | ⬜ | ⬜ |
| 20 | vktDynamicRenderingLocalReadMaint10Tests.cpp | dynamic_rendering root | ⬜ | ⬜ |
| 21 | vktRenderPassDepthStencilWriteConditionsTests.cpp | renderpass1 root | ⬜ | ⬜ |
| 22 | vktRenderPassSubpassMergeFeedbackTests.cpp | renderpass2 suballocation | ⬜ | ⬜ |
| 23 | vktDynamicRenderingRandomTests.cpp | dynamic_rendering root | ⬜ | ⬜ |
| 24 | vktDynamicRenderingUnusedAttachmentsTests.cpp | dynamic_rendering root | ⬜ | ⬜ |
| 25 | vktDynamicRenderingDepthStencilResolveTests.cpp | dynamic_rendering root | ⬜ | ⬜ |
| 26 | vktRenderPassNestedCommandBuffersTests.cpp | rendering root | ⬜ | ⬜ |
| 27 | vktRenderPassCustomResolveTests.cpp | all rendering types | ⬜ | ⬜ |
| 28 | vktDynamicRenderingMultiviewClearTests.cpp | dynamic_rendering root | ⬜ | ⬜ |

## Notes
- The `vktRenderPassTests.cpp` file itself contains the core test logic (simple, formats, attachment, attachment_write_mask, attachment_allocation) in addition to the registration/dispatch code
- All three top-level groups share the same `createRenderPassTestsInternal()` function with different `GroupParams`
- The `dynamic_rendering` group has 4 sub-variants: primary_cmd_buff, partial_secondary_cmd_buff, complete_secondary_cmd_buff, graphics_pipeline_library
