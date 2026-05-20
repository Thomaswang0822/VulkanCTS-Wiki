# vktSpvAsmPhysicalStorageBufferPointerTests

## Overview

SPIR-V Assembly Tests for PhysicalStorageBuffer pointers. Tests copying data between source and destination buffers using physical storage buffer addresses passed via push constants or SSBOs. Exercises the PhysicalStorageBufferAddresses capability, OpConvertUToPtr, and OpSelect on physical storage buffer pointers.

## Role

Implementation file

## Source

- [vktSpvAsmPhysicalStorageBufferPointerTests.cpp](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp)

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.physical_storage_buffer
├── push_constants
├── push_constants_function
└── addrs_in_ssbo
```

## Test Families

### push_constants — Physical buffer addresses via push constants (inline loop)

Passes source and destination buffer device addresses through push constants and copies data using an inline loop in the compute shader (`vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L395-L581`). The shader uses `PhysicalStorageBuffer64` memory model and `OpAccessChain` into PhysicalStorageBuffer pointers. The push constant struct contains `{uint64_t src, uint64_t dst, int32_t cnt, int32_t use_fun}` where `use_fun` is set to 0 (false) for this test, meaning the inline loop path is taken.

### push_constants_function — Physical buffer addresses via push constants (function call)

Same as push_constants but `use_fun` is set to 1 (true), causing the shader to use a function call (`OpFunctionCall`) to perform the copy (`vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L395-L581`). The function receives PhysicalStorageBuffer pointer parameters and iterates through elements.

### addrs_in_ssbo — Physical buffer addresses stored in an SSBO

Passes buffer device addresses through an SSBO where addresses are stored both as PhysicalStorageBuffer pointers and as 64-bit unsigned integers (`vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L583-L738`). The shader uses `OpConvertUToPtr` to convert the uint64 addresses to PhysicalStorageBuffer pointers, and `OpSelect` to choose between the pointer-based and uint-based address representations. This test verifies that both PhysicalStorageBuffer and 64-bit integer values can coexist in the same array.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Pass method | PUSH_CONSTANTS, PUSH_CONSTANTS_FUNCTION, ADDRESSES_IN_SSBO | How buffer addresses are communicated to the shader |
| Element count | 64 | Number of int32 elements to copy (fixed) |

## Support Requirements

- **VK_KHR_get_physical_device_properties2** instance extension (for feature queries)
- **bufferDeviceAddress** feature (checked via `isBufferDeviceAddressSupported()`)
- **shaderInt64** feature (required for ADDRESSES_IN_SSBO variant)
- **PhysicalStorageBufferAddresses** SPIR-V capability
- **SPV_KHR_physical_storage_buffer** SPIR-V extension
- **SPIR-V 1.4** (used in shader assembly build options)

## Verification Methods

- Source buffer is initialized with sequential values via `TypedBuffer::iota()`.
- Destination buffer is zeroed before the shader runs.
- After shader execution, destination buffer contents are compared byte-by-byte against source buffer contents using `std::equal(src.begin(), src.end(), dst.begin())` (`vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L580` for push_constants, `vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L737` for SSBO variant).
- Test passes if all elements match; fails otherwise.

## Notes

- The `PassMethod` enum (`vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L55-L60`) defines three methods, but only three test cases are created (one per method).
- The `TestParams` struct (`vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L62-L66`) holds the pass method and element count.
- The `ut::Buffer` and `ut::TypedBuffer` helper classes (`vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L73-L293`) manage buffer creation with optional device address support.
