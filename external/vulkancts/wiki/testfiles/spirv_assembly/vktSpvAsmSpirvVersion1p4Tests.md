# vktSpvAsmSpirvVersion1p4Tests

## Overview

Tests SPIR-V 1.4 feature groups registered by
[`createSpirvVersion1p4Group()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L124-L409),
including OpCopyLogical, pointer comparisons/differences, OpCopyMemory access operands, uniform IDs, NonWritable
function/private variables, SPIR-V 1.4 entry-point interface requirements, HLSL functionality, loop controls,
OpSelect cases, UConvert in OpSpecConstantOp, and integer wrap decorations.

## Role

Implementation file

## Source

- [vktSpvAsmSpirvVersion1p4Tests.cpp](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L124)

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

Tests copying between types with different layouts: different matrix layouts, different matrix strides, nested arrays with
different inner/outer strides, same array/struct with two IDs, and SSBO-to-UBO/UBO-to-SSBO copies. These cases are
registered in the [`opcopylogical`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L160-L183)
case group.

### opptrdiff — Tests OpPtrDiff instruction

Tests pointer difference computation within SSBO and workgroup storage, with variable-pointer requirements from
[`Varptr_ssbo`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L139-L140) and
[`Varptr_full`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L142-L143). The registered cases
are listed in the [`opptrdiff`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L185-L196)
case group.

### opptrequal — Tests OpPtrEqual instruction

Tests pointer equality comparisons against different SSBO/WG variables, null pointers, simple variable-pointer operands,
and variable pointers stored in function/private variables. The registered cases are listed in the
[`opptrequal`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L198-L223) case group.

### opptrnotequal — Tests OpPtrNotEqual instruction

Tests pointer inequality comparisons for the corresponding SSBO, workgroup, null, simple variable-pointer, and stored
pointer scenarios. The registered cases are listed in the
[`opptrnotequal`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L225-L250) case group.

### opcopymemory — Tests OpCopyMemory with access operands

Tests OpCopyMemory with different alignments, no source access operands, and no target access operands. The registered
cases are listed in the [`opcopymemory`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L252-L259)
case group.

### uniformid — Tests workgroup and subgroup uniform load

Tests workgroup/subgroup uniform load and compare results in active and nonuniform control-flow scenarios. The registered
cases are listed in the [`uniformid`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L261-L272)
case group.

### nonwritable — Tests NonWritable decoration on function/private variables

Tests that NonWritable can decorate Function and Private variables, including multiple variables and a non-entrypoint
function case. The registered cases are listed in the
[`nonwritable`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L274-L285) case group.

### entrypoint — Tests entry point listing all module-scope variables

Tests compute, fragment, geometry, tessellation-control, tessellation-evaluation, and vertex entry-point cases with push
constant, SSBO, UBO, or workgroup variables as registered in the
[`entrypoint`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L287-L327) case group.

### hlsl_functionality1 — Tests SPV_GOOGLE_hlsl_functionality1 features in SPIR-V 1.4

Tests CounterBuffer decoration, OpDecorateString, and OpMemberDecorateString as registered in the
[`hlsl_functionality1`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L329-L337) case group.

### loop_control — Tests SPIR-V 1.4 loop controls

Tests IterationMultiple, MaxIterations, MinIterations, PartialCount, and PeelCount loop controls as registered in the
[`loop_control`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L339-L351) case group.

### opselect — Tests OpSelect on composite types

Tests OpSelect with arrays, structs, nested arrays/structs, scalar/vector selectors, SSBO pointers, and workgroup pointers.
The workgroup-pointer cases use the extra
[`VK_KHR_workgroup_memory_explicit_layout`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L145-L147)
requirement. The registered cases are listed in the
[`opselect`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L353-L379) case group.

### uconvert — Tests UConvert in OpSpecConstantOp

Tests UConvert extend, truncate, and zero-extend cases involving 16-bit and 64-bit integer requirements. The registered
cases are listed in the [`uconvert`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L381-L399)
case group.

### wrap — Tests NoSignedWrap/NoUnsignedWrap decorations

Tests NoSignedWrap and NoUnsignedWrap decorations as registered in the
[`wrap`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L401-L407) case group.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Feature group | [`opcopylogical` through `wrap`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L160-L407) | The registered SPIR-V 1.4 feature group |
| Shader stage | [`compute`, `fragment`, `geometry`, `tess_con`, `tess_eval`, `vert`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L287-L325) | Pipeline stage prefixes used by the entrypoint family |
| Variable pointer level | [`Varptr_ssbo`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L139-L140), [`Varptr_full`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L142-L143), [`Varptr_full_explicitLayout`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L145-L147) | Variable-pointer requirement sets used by pointer families |

## Support / Feature Requirements

- All generated Amber test cases add [`VK_KHR_spirv_1_4`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L93-L99).
- All generated cases use SPIR-V 1.4 assembly build options through
  [`SpirVAsmBuildOptions`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L83-L84) and
  [`setSpirVAsmBuildOptions`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L113).
- Per-case requirements include [`Features.geometryShader`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L132-L135),
  [`Features.tessellationShader`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L136-L137),
  [`VariablePointerFeatures.variablePointersStorageBuffer`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L139-L140),
  [`VariablePointerFeatures.variablePointers`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L142-L143),
  [`Features.shaderInt16`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L148-L149),
  [`VK_KHR_16bit_storage`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L151-L154),
  [`Features.shaderInt64`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L155-L156), and
  [`VK_KHR_workgroup_memory_explicit_layout`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L145-L147).

## Verification Methods

All tests are Amber-based. The helper
[`addTestsForAmberFiles()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L75-L120) builds the
subdirectory path from each [`CaseGroup`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L56-L73),
creates each Amber test case with
[`cts_amber::createAmberTestCase`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L86-L91), adds
requirements, sets SPIR-V 1.4 assembly options, and adds the case to the group.

## Notes

- The test-generation helper is non-VulkanSC only through
  [`#ifndef CTS_USES_VULKANSC`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L75-L120).
- The source comments state that [`VK_KHR_spirv_1_4`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L93-L106)
  requires Vulkan 1.1 and therefore several promoted extensions do not need explicit test requirements.
