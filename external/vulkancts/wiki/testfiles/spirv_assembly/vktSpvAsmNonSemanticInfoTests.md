# vktSpvAsmNonSemanticInfoTests

## Overview

Tests for [`VK_KHR_shader_non_semantic_info`](../../../modules/vulkan/spirv_assembly/vktSpvAsmNonSemanticInfoTests.cpp#L64), verifying that non-semantic extended instruction sets are handled by the SPIR-V assembly path through basic usage, non-existing instruction-set names, large instruction numbers, many parameters, constant and non-constant parameter types, and instruction placement.

## Role

Implementation file

## Source

- [vktSpvAsmNonSemanticInfoTests.cpp](../../../modules/vulkan/spirv_assembly/vktSpvAsmNonSemanticInfoTests.cpp#L319)

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.non_semantic_info
├── basic
├── dummy_instruction_set
├── large_instruction_number
├── many_parameters
├── any_constant_type
├── any_constant_type_used
├── any_non_constant_type
└── placement
```

## Test Families

### basic — Minimal test of basic non-semantic info functionality

Imports [`NonSemantic.KHR.DebugInfo`](../../../modules/vulkan/spirv_assembly/vktSpvAsmNonSemanticInfoTests.cpp#L122) extended instruction set and uses [`OpExtInst`](../../../modules/vulkan/spirv_assembly/vktSpvAsmNonSemanticInfoTests.cpp#L136) with a file string and the main function. The registered case is [`basic`](../../../modules/vulkan/spirv_assembly/vktSpvAsmNonSemanticInfoTests.cpp#L330).

### dummy_instruction_set — Tests non-existing instruction set

Imports [`NonSemantic.P.B.NonexistingSet`](../../../modules/vulkan/spirv_assembly/vktSpvAsmNonSemanticInfoTests.cpp#L142) and uses [`OpExtInst`](../../../modules/vulkan/spirv_assembly/vktSpvAsmNonSemanticInfoTests.cpp#L145-L147) with instruction numbers 55 and 99. The registered case is [`dummy_instruction_set`](../../../modules/vulkan/spirv_assembly/vktSpvAsmNonSemanticInfoTests.cpp#L331).

### large_instruction_number — Tests large instruction numbers near uint::max

Uses instruction numbers near [`UINT32_MAX`](../../../modules/vulkan/spirv_assembly/vktSpvAsmNonSemanticInfoTests.cpp#L156-L158) to verify the compiler handles large instruction numbers in non-semantic extended instructions. The registered case is [`large_instruction_number`](../../../modules/vulkan/spirv_assembly/vktSpvAsmNonSemanticInfoTests.cpp#L332).

### many_parameters — Tests many parameters (100) to a single OpExtInst

Passes 100 string parameters to a single [`OpExtInst`](../../../modules/vulkan/spirv_assembly/vktSpvAsmNonSemanticInfoTests.cpp#L162-L173) call with instruction number 1234, verifying the compiler can handle a large number of parameters. The registered case is [`many_parameters`](../../../modules/vulkan/spirv_assembly/vktSpvAsmNonSemanticInfoTests.cpp#L333).

### any_constant_type — Tests any type of constant parameter

Passes constant types as parameters to [`OpExtInst`](../../../modules/vulkan/spirv_assembly/vktSpvAsmNonSemanticInfoTests.cpp#L176-L203): undef, int, uint, float, struct, vector, array, string, and matrix constants. The registered case is [`any_constant_type`](../../../modules/vulkan/spirv_assembly/vktSpvAsmNonSemanticInfoTests.cpp#L334).

### any_constant_type_used — Tests constant parameters that are also used semantically

Starts from the same constant-parameter setup as [`any_constant_type`](../../../modules/vulkan/spirv_assembly/vktSpvAsmNonSemanticInfoTests.cpp#L176-L203) but additionally uses the constants in semantic operations such as composite extracts, arithmetic, conversion, and store operations. The registered case is [`any_constant_type_used`](../../../modules/vulkan/spirv_assembly/vktSpvAsmNonSemanticInfoTests.cpp#L335).

### any_non_constant_type — Tests non-constant result IDs as parameters

Passes non-constant result IDs as parameters to [`OpExtInst`](../../../modules/vulkan/spirv_assembly/vktSpvAsmNonSemanticInfoTests.cpp#L223-L257), including another extended-instruction result, entry point, variables, buffer and texture loads, arithmetic results, and logical/comparison results. The registered case is [`any_non_constant_type`](../../../modules/vulkan/spirv_assembly/vktSpvAsmNonSemanticInfoTests.cpp#L336).

### placement — Tests OpExtInst placement at various scopes

Places non-semantic [`OpExtInst`](../../../modules/vulkan/spirv_assembly/vktSpvAsmNonSemanticInfoTests.cpp#L259-L275) instructions in the types/constants area, between function definitions, and inside a function block. The registered case is [`placement`](../../../modules/vulkan/spirv_assembly/vktSpvAsmNonSemanticInfoTests.cpp#L337).

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Test type | [`TT_BASIC`](../../../modules/vulkan/spirv_assembly/vktSpvAsmNonSemanticInfoTests.cpp#L42), [`TT_NONEXISTING_INSTRUCTION_SET`](../../../modules/vulkan/spirv_assembly/vktSpvAsmNonSemanticInfoTests.cpp#L43), [`TT_LARGE_INSTRUCTION_NUMBER`](../../../modules/vulkan/spirv_assembly/vktSpvAsmNonSemanticInfoTests.cpp#L44), [`TT_MANY_PARAMETERS`](../../../modules/vulkan/spirv_assembly/vktSpvAsmNonSemanticInfoTests.cpp#L45), [`TT_ANY_CONSTANT_TYPE`](../../../modules/vulkan/spirv_assembly/vktSpvAsmNonSemanticInfoTests.cpp#L46), [`TT_ANY_CONSTANT_TYPE_USED`](../../../modules/vulkan/spirv_assembly/vktSpvAsmNonSemanticInfoTests.cpp#L47), [`TT_ANY_NON_CONSTANT_TYPE`](../../../modules/vulkan/spirv_assembly/vktSpvAsmNonSemanticInfoTests.cpp#L48), [`TT_PLACEMENT`](../../../modules/vulkan/spirv_assembly/vktSpvAsmNonSemanticInfoTests.cpp#L49) | The specific non-semantic info scenario being tested |

## Support Requirements

- [`VK_KHR_shader_non_semantic_info`](../../../modules/vulkan/spirv_assembly/vktSpvAsmNonSemanticInfoTests.cpp#L115-L118) device extension.
- [`SPV_KHR_non_semantic_info`](../../../modules/vulkan/spirv_assembly/vktSpvAsmNonSemanticInfoTests.cpp#L64) SPIR-V extension is requested through the compute shader specification.

## Verification Methods

All tests use [`SpvAsmComputeShaderInstance::iterate()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmNonSemanticInfoTests.cpp#L90-L93), which runs the compute shader specification. The shader copies input floats to output after inserting the selected non-semantic instructions, so successful compilation and execution preserve the pass-through output path from the generated shader body.

## Notes

- The shader initializes input and output float buffers with matching values in [`getComputeShaderSpec()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmNonSemanticInfoTests.cpp#L52-L69); the selected non-semantic instructions are injected before the final output store.
