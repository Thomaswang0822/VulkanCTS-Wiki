# vktSpvAsmRelaxedWithForwardReferenceTests

## Overview

Tests for SPIR-V relaxed extended instruction handling with forward references, specifically verifying that `OpExtInstWithForwardRefsKHR` works correctly with the `SPV_KHR_relaxed_extended_instruction` extension.

## Role

Implementation file

## Source

- [vktSpvAsmRelaxedWithForwardReferenceTests.cpp](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmRelaxedWithForwardReferenceTests.cpp)

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.relaxed_with_forward_reference
└── static_method_shader
```

## Test Families

### static_method_shader — Tests forward references in HLSL debug info

Tests a shader compiled from HLSL with DXC using `-fspv-debug=vulkan-with-source` flag. The shader contains a class `A` with a static method, which generates `OpExtInstWithForwardRefsKHR` instructions in the SPIR-V output because `DebugTypeFunction` and `DebugFunction` instructions reference each other (the function type references the composite type, and the composite type references the function). The test verifies that the SPIR-V compiler correctly handles these forward references when the `SPV_KHR_relaxed_extended_instruction` extension is enabled. Source: `vktSpvAsmRelaxedWithForwardReferenceTests.cpp#L126-L294`.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Shader variant | `static_method_shader` | Only one test case defined in this file |

## Support Requirements

- `VK_KHR_shader_non_semantic_info` extension (`vktSpvAsmRelaxedWithForwardReferenceTests.cpp#L109`)
- `VK_KHR_shader_relaxed_extended_instruction` extension (`vktSpvAsmRelaxedWithForwardReferenceTests.cpp#L110`)
- SPIR-V 1.6 (`vktSpvAsmRelaxedWithForwardReferenceTests.cpp#L54`)

## Verification Methods

Uses `SpvAsmComputeShaderInstance::iterate()` which runs the compute shader and verifies the pass-through behavior (input floats copied to output). The primary verification is that the shader with forward references compiles and executes without error. Source: `vktSpvAsmRelaxedWithForwardReferenceTests.cpp#L81-L84`.

## Notes

- The embedded SPIR-V shader was compiled from HLSL using DXC with `-T cs_6_0 -fspv-target-env=vulkan1.3 -fspv-debug=vulkan-with-source -spirv -Od`
- The forward reference pattern: `%35` (DebugTypeFunction) references `%37` (DebugTypeComposite) which is defined later, and `%38` (DebugFunction) also references `%37` before it is defined
