# vktSpvAsmSpirvVersion1p4Tests

## Overview

Tests for new features introduced in SPIR-V 1.4, including OpCopyLogical, OpPtrDiff, OpPtrEqual/OpPtrNotEqual, OpCopyMemory with access operands, workgroup/subgroup uniform load, NonWritable decoration on function/private variables, entry point variable listing, HLSL functionality features, loop controls, OpSelect on composite types, UConvert in OpSpecConstantOp, and integer wrap decorations.

## Role

Implementation file

## Source

- [vktSpvAsmSpirvVersion1p4Tests.cpp](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp)

## Registration Hierarchy

```text
spirv_assembly.instruction.spirv1p4
├── opcopylogical
├── opptrdiff
├── opptrequal
├── opptrnotequal
├── opcopymemory
├── uniformid
├── nonwritable
├── entrypoint
├── hlsl_functionality1
├── loop_control
├── opselect
├── uconvert
└── wrap
```

## Test Families

### opcopylogical — Tests OpCopyLogical instruction

Tests copying between types with different layouts: different matrix layouts, different matrix strides, nested arrays with different inner/outer strides, same array/struct with two IDs, and SSBO-to-UBO/UBO-to-SSBO copies. Source: `vktSpvAsmSpirvVersion1p4Tests.cpp#L160-L183`.

### opptrdiff — Tests OpPtrDiff instruction

Tests pointer difference computation within SSBO and workgroup storage, with variable pointers at different capability levels. Source: `vktSpvAsmSpirvVersion1p4Tests.cpp#L185-L196`.

### opptrequal — Tests OpPtrEqual instruction

Tests pointer equality comparisons against different SSBO/WG variables, null pointers, and with variable pointers stored in function/private variables. Source: `vktSpvAsmSpirvVersion1p4Tests.cpp#L198-L223`.

### opptrnotequal — Tests OpPtrNotEqual instruction

Tests pointer inequality comparisons with the same scenarios as opptrequal. Source: `vktSpvAsmSpirvVersion1p4Tests.cpp#L225-L250`.

### opcopymemory — Tests OpCopyMemory with access operands

Tests OpCopyMemory with different alignments and missing source/target access operands (new in SPIR-V 1.4). Source: `vktSpvAsmSpirvVersion1p4Tests.cpp#L252-L259`.

### uniformid — Tests workgroup and subgroup uniform load

Tests `OpGroupNonUniformAll`/`OpGroupNonUniformAny` and workgroup/subgroup uniform load results in various control flow scenarios. Source: `vktSpvAsmSpirvVersion1p4Tests.cpp#L261-L272`.

### nonwritable — Tests NonWritable decoration on function/private variables

Tests that NonWritable can decorate Function and Private variables (new in SPIR-V 1.4). Source: `vktSpvAsmSpirvVersion1p4Tests.cpp#L274-L285`.

### entrypoint — Tests entry point listing all module-scope variables

Tests that SPIR-V 1.4 entry points must list all module-scope variables statically used, across compute, vertex, fragment, geometry, and tessellation shader stages. Source: `vktSpvAsmSpirvVersion1p4Tests.cpp#L287-L327`.

### hlsl_functionality1 — Tests SPV_GOOGLE_hlsl_functionality1 features in SPIR-V 1.4

Tests CounterBuffer decoration, OpDecorateString, and OpMemberDecorateString (folded into SPIR-V 1.4). Source: `vktSpvAsmSpirvVersion1p4Tests.cpp#L329-L337`.

### loop_control — Tests SPIR-V 1.4 loop controls

Tests IterationMultiple, MaxIterations, MinIterations, PartialCount, and PeelCount loop controls. Source: `vktSpvAsmSpirvVersion1p4Tests.cpp#L339-L351`.

### opselect — Tests OpSelect on composite types

Tests OpSelect with arrays, structs, vectors with scalar selector (new in 1.4), SSBO/workgroup pointers, and nested arrays/structs. Source: `vktSpvAsmSpirvVersion1p4Tests.cpp#L353-L379`.

### uconvert — Tests UConvert in OpSpecConstantOp

Tests UConvert operations (extend/truncate/zero-extend) in OpSpecConstantOp with 16-bit and 64-bit integer types. Source: `vktSpvAsmSpirvVersion1p4Tests.cpp#L381-L399`.

### wrap — Tests NoSignedWrap/NoUnsignedWrap decorations

Tests that NoSignedWrap and NoUnsignedWrap decorations are accepted (folded into SPIR-V 1.4). Source: `vktSpvAsmSpirvVersion1p4Tests.cpp#L401-L408`.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Feature group | opcopylogical, opptrdiff, opptrequal, opptrnotequal, opcopymemory, uniformid, nonwritable, entrypoint, hlsl_functionality1, loop_control, opselect, uconvert, wrap | The SPIR-V 1.4 feature being tested |
| Shader stage | compute, vertex, fragment, geometry, tess_ctrl, tess_eval | Pipeline stage (entrypoint family) |
| Variable pointer level | SSBO only, full (SSBO + WG) | Variable pointer capability level |

## Support Requirements

- `VK_KHR_spirv_1_4` extension (added to all tests at `vktSpvAsmSpirvVersion1p4Tests.cpp#L98`)
- SPIR-V 1.4 assembly build options
- Various feature requirements per subgroup: `Features.geometryShader`, `Features.tessellationShader`, `VariablePointerFeatures.variablePointersStorageBuffer`, `VariablePointerFeatures.variablePointers`, `Features.shaderInt16`, `VK_KHR_16bit_storage`, `Features.shaderInt64`, `VK_KHR_workgroup_memory_explicit_layout`

## Verification Methods

All tests are Amber-based. Verification is handled by the Amber test framework using `.amber` test files located in the `spirv_assembly/instruction/spirv1p4/` data subdirectory (with subdirectories per feature group). Source: `vktSpvAsmSpirvVersion1p4Tests.cpp#L75-L120`.

## Notes

- Non-VulkanSC only
- All tests use Amber test framework with SPIR-V 1.4 build options
- VK_KHR_spirv_1_4 requires Vulkan 1.1, so many extensions promoted to core in Vulkan 1.1 do not need explicit requests
