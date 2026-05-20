# vktSpvAsmPtrAccessChainTests

## Overview

SPIR-V Assembly Tests for OpPtrAccessChain with workgroup memory. Uses Amber test scripts to verify correct and incorrect ArrayStride decorations when using OpPtrAccessChain on workgroup memory with explicit layout.

## Role

Implementation file

## Source

- [vktSpvAsmPtrAccessChainTests.cpp](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmPtrAccessChainTests.cpp)

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.ptr_access_chain (non-VulkanSC only)
├── workgroup
└── workgroup_bad_stride
```

## Test Families

### workgroup — OpPtrAccessChain with correct ArrayStride decoration

Amber test that verifies OpPtrAccessChain works correctly with properly decorated ArrayStride on workgroup memory (`vktSpvAsmPtrAccessChainTests.cpp#L50`). Uses `VK_KHR_workgroup_memory_explicit_layout` extension and `VariablePointerFeatures.variablePointers` feature. The Amber script is located at `spirv_assembly/instruction/compute/ptr_access_chain/workgroup.amber`.

### workgroup_bad_stride — OpPtrAccessChain with incorrect ArrayStride decoration

Amber test that verifies behavior when OpPtrAccessChain is used with an incorrectly decorated ArrayStride on workgroup memory (`vktSpvAsmPtrAccessChainTests.cpp#L51`). This is a negative/validation test. The Amber script is located at `spirv_assembly/instruction/compute/ptr_access_chain/workgroup_bad_stride.amber`.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Stride correctness | correct, bad_stride | Whether ArrayStride decoration matches actual stride |

## Support Requirements

- **VariablePointerFeatures.variablePointers** feature
- **VK_KHR_workgroup_memory_explicit_layout** extension
- **VK_KHR_spirv_1_4** extension (SPIR-V 1.4 build options)
- **SPIR-V 1.4** assembly target
- Entire group is non-VulkanSC only (guarded by `#ifndef CTS_USES_VULKANSC`)

## Verification Methods

- Tests are implemented as Amber test scripts (`.amber` files) located in `external/vulkancts/data/vulkan/amber/spirv_assembly/instruction/compute/ptr_access_chain/`.
- Amber framework handles shader compilation, execution, and result verification based on the script's expectations.

## Notes

- This is a small file (~80 lines) that delegates all test logic to external Amber scripts.
- The `createTests` function (`vktSpvAsmPtrAccessChainTests.cpp#L35-L69`) creates Amber test cases and adds the required feature/extension requirements.
- The entire group is conditionally compiled under `#ifndef CTS_USES_VULKANSC`.
