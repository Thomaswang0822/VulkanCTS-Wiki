# vktSpvAsmRelaxedWithForwardReferenceTests

## Overview

Tests SPIR-V relaxed extended instruction handling with forward references, specifically verifying that
[`OpExtInstWithForwardRefsKHR`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRelaxedWithForwardReferenceTests.cpp#L235-L237)
works with the embedded [`SPV_KHR_relaxed_extended_instruction`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRelaxedWithForwardReferenceTests.cpp#L149-L150)
extension shader.

## Role

Implementation file

## Source

- [vktSpvAsmRelaxedWithForwardReferenceTests.cpp](../../../modules/vulkan/spirv_assembly/vktSpvAsmRelaxedWithForwardReferenceTests.cpp#L280)

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.relaxed_with_forward_reference
└── static_method_shader
```

## Test Families

### static_method_shader — Tests forward references in HLSL debug info

The single registered case is
[`static_method_shader`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRelaxedWithForwardReferenceTests.cpp#L289),
created under the
[`relaxed_with_forward_reference`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRelaxedWithForwardReferenceTests.cpp#L280-L293)
group. The embedded shader was compiled from HLSL with
[`-fspv-debug=vulkan-with-source`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRelaxedWithForwardReferenceTests.cpp#L126-L128)
and contains class [`A`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRelaxedWithForwardReferenceTests.cpp#L130-L144)
with a static method. The shader contains
[`OpExtInstWithForwardRefsKHR`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRelaxedWithForwardReferenceTests.cpp#L235-L236)
instructions because [`DebugTypeFunction`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRelaxedWithForwardReferenceTests.cpp#L235),
[`DebugFunction`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRelaxedWithForwardReferenceTests.cpp#L236), and
[`DebugTypeComposite`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRelaxedWithForwardReferenceTests.cpp#L237)
refer to each other before all operands are defined.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Shader variant | [`static_method_shader`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRelaxedWithForwardReferenceTests.cpp#L289) | Only one test case defined in this file |

## Support / Feature Requirements

- Requires [`VK_KHR_shader_non_semantic_info`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRelaxedWithForwardReferenceTests.cpp#L107-L110).
- Requires [`VK_KHR_shader_relaxed_extended_instruction`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRelaxedWithForwardReferenceTests.cpp#L107-L110).
- Builds the assembly with [`SPIRV_VERSION_1_6`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRelaxedWithForwardReferenceTests.cpp#L113-L116).

## Verification Methods

[`SpvAsmSpirvRelaxedForwardReferenceBasicInstance::iterate()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRelaxedWithForwardReferenceTests.cpp#L81-L84)
delegates to the common compute shader instance. The shader copies from
[`%input`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRelaxedWithForwardReferenceTests.cpp#L266-L267) to
[`%output`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRelaxedWithForwardReferenceTests.cpp#L269-L270), so the local
file-level verification is successful compilation and execution of the forward-reference shader through the compute harness.

## Notes

- The embedded SPIR-V shader was compiled from HLSL using
  [`dxc -T cs_6_0 -fspv-target-env=vulkan1.3 -fspv-debug=vulkan-with-source -spirv -Od`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRelaxedWithForwardReferenceTests.cpp#L126-L128).
- The forward reference pattern is that
  [`%35`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRelaxedWithForwardReferenceTests.cpp#L235) references
  [`%37`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRelaxedWithForwardReferenceTests.cpp#L237), and
  [`%38`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRelaxedWithForwardReferenceTests.cpp#L236) also references
  [`%37`](../../../modules/vulkan/spirv_assembly/vktSpvAsmRelaxedWithForwardReferenceTests.cpp#L237) before `%37` is defined.
