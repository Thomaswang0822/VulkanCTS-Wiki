# vktPipelineDynamicOffsetTests.cpp

## Overview

[`vktPipelineDynamicOffsetTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L1) implements the [`dynamic_offset`](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L2372) topic group. It verifies dynamic descriptor offsets for uniform and storage buffer dynamic descriptors, testing various binding configurations, grouping strategies, and command buffer orderings.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineDynamicOffsetTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L1)
- Header: [`vktPipelineDynamicOffsetTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.hpp#L1)
- Shared helpers: [`ReferenceRenderer`](../../../modules/vulkan/pipeline/vktPipelineReferenceRenderer.cpp#L1)

## Registration Path

[`createDynamicOffsetTests()`](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L2310) returns the `dynamic_offset` group, attached under each variant root by `createChildren()`.

**Variant coverage**: All variants. Compute and combined_descriptors sub-groups are monolithic only.

## Test Hierarchy

```text
dynamic_offset
├── graphics                              (all construction types)
│   ├── single_set
│   │   ├── uniform_buffer
│   │   │   ├── numcmdbuffers_1/sameorder/numdescriptorsetbindings_<N>/numdynamicbindings_<N>/numnondynamicbindings_<N>/bind[2]
│   │   │   └── numcmdbuffers_2/sameorder|reverseorder/...
│   │   └── storage_buffer
│   │       └── (same structure)
│   ├── multiset
│   │   └── (same structure)
│   └── arrays
│       └── (same structure)
├── compute                               (monolithic only)
│   └── (same nested structure as graphics)
└── combined_descriptors                  (monolithic only)
    ├── all_offsets
    │   └── <order>_<offsets>_<pipeline>
    └── single_offset
        └── <order>_<offsets>_<pipeline>
```

## Test Families

### 1. graphics

Tests dynamic descriptor offsets in a graphics pipeline. Renders colored quads and verifies via image comparison.

### 2. compute

Tests dynamic descriptor offsets in a compute pipeline. Writes to an output buffer and verifies values directly. Monolithic only.

### 3. combined_descriptors

Tests dynamic offsets with mixed descriptor types (UBO + SSBO) across both graphics and compute pipelines simultaneously. Monolithic only.

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
