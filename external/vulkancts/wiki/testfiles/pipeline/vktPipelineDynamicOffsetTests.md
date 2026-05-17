# vktPipelineDynamicOffsetTests.cpp

## Overview

[`vktPipelineDynamicOffsetTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L1) implements the [`dynamic_offset`](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L2372) topic group. It verifies dynamic descriptor offsets for uniform and storage buffer dynamic descriptors, testing various binding configurations, grouping strategies, and command buffer orderings.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineDynamicOffsetTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L1)
- Header: [`vktPipelineDynamicOffsetTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.hpp#L1)
- Shared helpers: [`ReferenceRenderer`](../../../modules/vulkan/pipeline/vktPipelineReferenceRenderer.cpp#L1)

## Registration Hierarchy

```text
pipeline.monolithic.dynamic_offset
├── graphics
├── compute (monolithic only)
└── combined_descriptors (monolithic only)
```

**Variant coverage**: All variants. The `compute` and `combined_descriptors` subgroups are monolithic only.

## Test Families

### graphics — Graphics pipeline dynamic offsets

Tests dynamic descriptor offsets in a graphics pipeline. Renders colored quads and verifies via image comparison. The subgroup hierarchy is organized by:

- **Grouping strategy**: `single_set`, `multiset`, `arrays`
  - **Descriptor type**: `uniform_buffer`, `storage_buffer`
    - **Command buffer count**: `numcmdbuffers_1`, `numcmdbuffers_2`
      - **Order**: `sameorder`, `reverseorder` (reverseorder only when numCmdBuffers >= 2)
        - **Descriptor set bindings**: `numdescriptorsetbindings_1`, `numdescriptorsetbindings_2` (limited to 1 when numCmdBuffers > 1)
          - **Dynamic bindings**: `numdynamicbindings_1`, `numdynamicbindings_2`
            - **Non-dynamic bindings**: `numnondynamicbindings_0`, `numnondynamicbindings_1`
              - **Bind command**: `bind`, `bind2` (bind2 uses `vkCmdBindDescriptorSets2KHR`, non-VulkanSC only)

### compute — Compute pipeline dynamic offsets (monolithic only)

Tests dynamic descriptor offsets in a compute pipeline. Writes to an output buffer and verifies values directly. Uses the same nested subgroup structure as `graphics` (grouping strategy, descriptor type, command buffer count, order, bindings).

### combined_descriptors — Mixed descriptor types (monolithic only)

Tests dynamic offsets with mixed descriptor types (UBO + SSBO) across both graphics and compute pipelines simultaneously. Contains two subgroups:

- **all_offsets**: Tests with all dynamic offsets varying. Leaf tests named `<order>_<offsets>_<pipeline>`.
- **single_offset**: Tests with a single dynamic offset varying. Leaf tests named `<order>_<offsets>_<pipeline>`.

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| GroupingStrategy | [Enum](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L71) | SINGLE_SET, MULTISET, ARRAYS |
| VkDescriptorType | [Array](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L2329) | UNIFORM_BUFFER_DYNAMIC, STORAGE_BUFFER_DYNAMIC |
| numCmdBuffers | [Array](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L2336) | 1, 2 |
| reverseOrder | [Array](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L2342) | false (sameorder), true (reverseorder) |
| numDescriptorSetBindings | [Array](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L2348) | 1, 2 |
| numDynamicBindings | [Array](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L2354) | 1, 2 |
| numNonDynamicBindings | [Array](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L2360) | 0, 1 |
| bind2 | [Array](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L2366) | false (bind), true (bind2, non-SC only) |

## Support / Feature Requirements

| Requirement | Condition | Line |
|---|---|---|
| `VK_KHR_maintenance6` | When `bind2 == true` | [793](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L793) |
| Pipeline construction requirements | Always | [791](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L791) |

## Verification Methods

- **Graphics**: `tcu::intThresholdPositionDeviationCompare()` with threshold UVec4(2,2,2,2) against reference renderer ([line 709](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L709))
- **Compute**: Direct buffer comparison against computed reference colors ([line 1338](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L1338))
- **Combined**: Dual verification: `tcu::floatThresholdCompare()` (threshold 0.01f) for image + `compareVectors()` (tolerance 0.01f) for SSBO ([line 2113](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L2113))

## Notes / Uncertainties

- `reverseorder` skipped when `numCmdBuffers < 2`; `numDescriptorSetBindings > 1` skipped when `numCmdBuffers > 1`
- `bind2` variant uses `vkCmdBindDescriptorSets2KHR` (VK_KHR_maintenance6), excluded on VulkanSC
