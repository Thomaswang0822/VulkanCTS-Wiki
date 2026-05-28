# vktSpvAsmPtrAccessChainTests

## Overview

SPIR-V Assembly Tests for [`OpPtrAccessChain`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/ptr_access_chain/workgroup.amber#L80) with workgroup memory. The source registers two Amber scripts that compare correct and incorrect [`ArrayStride`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPtrAccessChainTests.cpp#L49-L51) decorations on workgroup pointers under explicit workgroup-memory layout requirements.

## Role

Implementation file

## Source

- [vktSpvAsmPtrAccessChainTests.cpp](../../../modules/vulkan/spirv_assembly/vktSpvAsmPtrAccessChainTests.cpp#L73)

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.ptr_access_chain
├── workgroup
└── workgroup_bad_stride
```

## Test Families

### workgroup — OpPtrAccessChain with correct ArrayStride decoration

Amber test that applies [`OpPtrAccessChain`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/ptr_access_chain/workgroup.amber#L77-L82) to workgroup memory with a correct [`ArrayStride 4`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/ptr_access_chain/workgroup.amber#L49-L50) decoration. The C++ source registers the [`workgroup`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPtrAccessChainTests.cpp#L49-L58) Amber case and uses data directory [`spirv_assembly/instruction/compute/ptr_access_chain`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPtrAccessChainTests.cpp#L73-L77).

### workgroup_bad_stride — OpPtrAccessChain with incorrect ArrayStride decoration

Amber test that applies [`OpPtrAccessChain`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/ptr_access_chain/workgroup_bad_stride.amber#L77-L82) with an incorrect [`ArrayStride 8`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/ptr_access_chain/workgroup_bad_stride.amber#L49-L50) decoration on the workgroup pointer type. The Amber script states this decoration should be ignored and probes the same output pattern as the correct-stride case. The C++ source registers the [`workgroup_bad_stride`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPtrAccessChainTests.cpp#L49-L58) Amber case.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Stride correctness | [`workgroup`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPtrAccessChainTests.cpp#L50), [`workgroup_bad_stride`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPtrAccessChainTests.cpp#L51) | Whether the workgroup pointer `ArrayStride` is correct or intentionally wrong |

## Support / Feature Requirements

- [`VariablePointerFeatures.variablePointers`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPtrAccessChainTests.cpp#L59) feature.
- [`VK_KHR_workgroup_memory_explicit_layout`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPtrAccessChainTests.cpp#L60) extension.
- [`VK_KHR_spirv_1_4`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPtrAccessChainTests.cpp#L40-L41) assembly option.
- [`SPIR-V 1.4`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPtrAccessChainTests.cpp#L40-L41) assembly target.
- Entire group is non-VulkanSC only, guarded by [`#ifndef CTS_USES_VULKANSC`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPtrAccessChainTests.cpp#L37-L68).

## Verification Methods

- Tests are implemented as Amber test scripts under [`external/vulkancts/data/vulkan/amber/spirv_assembly/instruction/compute/ptr_access_chain/`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/ptr_access_chain/workgroup.amber#L1).
- The correct-stride script initializes SSBO inputs, runs one compute dispatch, and probes the output buffer for the expected sequence [`1 2 3 ... 15 0`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/ptr_access_chain/workgroup.amber#L110-L120).
- The bad-stride script uses the same dispatch and output probe while documenting that the incorrect pointer stride decoration should be ignored.

## Notes

- The [`createTests`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPtrAccessChainTests.cpp#L35-L69) function creates Amber test cases and adds the required feature/extension requirements.
- The source maps Amber basenames to registered case names by appending [`.amber`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPtrAccessChainTests.cpp#L54-L58).
- The entire group is conditionally compiled under [`#ifndef CTS_USES_VULKANSC`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPtrAccessChainTests.cpp#L37-L68).
