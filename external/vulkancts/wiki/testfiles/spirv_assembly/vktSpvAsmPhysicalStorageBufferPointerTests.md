# vktSpvAsmPhysicalStorageBufferPointerTests

## Overview

SPIR-V Assembly Tests for PhysicalStorageBuffer pointers. Tests copying data between source and destination buffers using physical storage buffer addresses passed via push constants or SSBOs, exercising [`PhysicalStorageBufferAddresses`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L402), [`OpConvertUToPtr`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L655-L658), and [`OpSelect`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L660-L661) on physical storage buffer pointers.

## Role

Implementation file

## Source

- [vktSpvAsmPhysicalStorageBufferPointerTests.cpp](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L742)

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.physical_storage_buffer
├── push_constants
├── push_constants_function
└── addrs_in_ssbo
```

## Test Families

### push_constants — Physical buffer addresses via push constants (inline loop)

Passes source and destination buffer device addresses through a push constant struct with [`src`, `dst`, `cnt`, and `use_fun`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L544-L550). The shader uses [`PhysicalStorageBuffer64`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L400-L405), loads the physical buffer pointers from push constants, and takes the inline loop path when [`use_fun`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L500-L515) is false. The registered case is [`push_constants`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L749).

### push_constants_function — Physical buffer addresses via push constants (function call)

Uses the same push-constant shader as [`push_constants`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L395-L531), but sets [`use_fun`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L567-L568) to true so the shader calls [`%cpbuffs`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L460-L485) to copy through PhysicalStorageBuffer pointer parameters. The registered case is [`push_constants_function`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L750).

### addrs_in_ssbo — Physical buffer addresses stored in an SSBO

Passes buffer device addresses through an SSBO where addresses are stored both as PhysicalStorageBuffer pointers and as 64-bit unsigned integers. The shader loads pointer fields and integer address fields from the SSBO, uses [`OpConvertUToPtr`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L653-L658), and uses [`OpSelect`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L660-L661) to choose between pointer-based and uint-based address representations. The source comment states the purpose is to show that both PhysicalStorageBuffer and 64-bit integer values can coexist in one array-like data structure passed as 64-bit integers by the application. The registered case is [`addrs_in_ssbo`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L751).

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Pass method | [`PUSH_CONSTANTS`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L57), [`PUSH_CONSTANTS_FUNCTION`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L58), [`ADDRESSES_IN_SSBO`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L59) | How buffer addresses are communicated to the shader |
| Element count | [`64`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L758-L759) | Number of int32 elements to copy |

## Support / Feature Requirements

- [`VK_KHR_get_physical_device_properties2`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L316-L319) instance extension for feature queries.
- [`bufferDeviceAddress`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L320-L323) support checked through `isBufferDeviceAddressSupported()`.
- [`shaderInt64`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L325-L328) feature for the `ADDRESSES_IN_SSBO` variant.
- [`PhysicalStorageBufferAddresses`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L401-L405) SPIR-V capability/extension in the push-constant shader and the corresponding capability in the SSBO shader.
- [`SPIR-V 1.4`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L529-L530) assembly build options.

## Verification Methods

- Source buffers are initialized with sequential values via [`TypedBuffer::iota()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L564-L565) for push constants and [`TypedBuffer::iota()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L723-L724) for the SSBO variant.
- Destination buffers are zeroed before dispatch in both variants.
- After shader execution, destination buffer contents are compared against source buffer contents using [`std::equal`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L580) for push constants and [`std::equal`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L737) for the SSBO variant.
- The test passes when all elements match; otherwise the test returns failure from the comparison expression.

## Notes

- The [`PassMethod`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L55-L60) enum defines the three methods registered by [`createPhysicalStorageBufferTestGroup()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L742-L760).
- The [`TestParams`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L62-L66) struct holds the pass method and element count.
- The [`ut::Buffer`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L73-L102) and [`ut::TypedBuffer`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L104-L120) helper classes manage buffer creation with optional device address support.
