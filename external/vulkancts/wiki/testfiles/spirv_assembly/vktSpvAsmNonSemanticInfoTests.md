# vktSpvAsmNonSemanticInfoTests

## Overview

Tests for VK_KHR_shader_non_semantic_info, verifying that non-semantic extended instruction sets are correctly handled by the SPIR-V compiler, including basic usage, non-existing instruction sets, large instruction numbers, many parameters, various constant and non-constant parameter types, and instruction placement.

## Role

Implementation file

## Source

- [vktSpvAsmNonSemanticInfoTests.cpp](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmNonSemanticInfoTests.cpp)

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

Imports `NonSemantic.KHR.DebugInfo` extended instruction set and uses `OpExtInst` with a file string and the main function. Verifies the shader compiles and executes correctly with the non-semantic instruction present. Source: `vktSpvAsmNonSemanticInfoTests.cpp#L131-L137`.

### dummy_instruction_set — Tests non-existing instruction set

Imports a non-existing instruction set `NonSemantic.P.B.NonexistingSet` and uses `OpExtInst` with arbitrary instruction numbers (55, 99). The compiler should accept any non-semantic instruction set name and instruction number without error. Source: `vktSpvAsmNonSemanticInfoTests.cpp#L139-L150`.

### large_instruction_number — Tests large instruction numbers near uint::max

Uses instruction numbers near `UINT32_MAX` (4294967294 and 4294967290) to verify the compiler handles arbitrarily large instruction numbers in non-semantic extended instructions. Source: `vktSpvAsmNonSemanticInfoTests.cpp#L152-L160`.

### many_parameters — Tests many parameters (100) to a single OpExtInst

Passes 100 string parameters to a single `OpExtInst` call with instruction number 1234, verifying the compiler can handle a large number of parameters. Source: `vktSpvAsmNonSemanticInfoTests.cpp#L162-L174`.

### any_constant_type — Tests any type of constant parameter

Passes various constant types as parameters to `OpExtInst`: undef, int, uint, float, struct, vector, array, string, and matrix constants. Verifies the compiler accepts all constant types in non-semantic instructions. Source: `vktSpvAsmNonSemanticInfoTests.cpp#L176-L205`.

### any_constant_type_used — Tests constant parameters that are also used semantically

Same as `any_constant_type` but additionally uses the constant values in semantic operations (extracts, arithmetic, stores) to verify that constants used in non-semantic instructions can also be used in regular shader operations. Source: `vktSpvAsmNonSemanticInfoTests.cpp#L206-L221`.

### any_non_constant_type — Tests non-constant result IDs as parameters

Passes non-constant result IDs as parameters to `OpExtInst`, including: result of another `OpExtInst`, entry point, variables of different types, buffer/texture loads, arithmetic results, and logical/comparison results. Source: `vktSpvAsmNonSemanticInfoTests.cpp#L223-L257`.

### placement — Tests OpExtInst placement at various scopes

Verifies that non-semantic `OpExtInst` instructions can be placed at global scope (types/constants section), between function definitions, and within a function block. Source: `vktSpvAsmNonSemanticInfoTests.cpp#L259-L275`.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Test type | TT_BASIC, TT_NONEXISTING_INSTRUCTION_SET, TT_LARGE_INSTRUCTION_NUMBER, TT_MANY_PARAMETERS, TT_ANY_CONSTANT_TYPE, TT_ANY_CONSTANT_TYPE_USED, TT_ANY_NON_CONSTANT_TYPE, TT_PLACEMENT | The specific non-semantic info scenario being tested |

## Support Requirements

- `VK_KHR_shader_non_semantic_info` extension (checked in `checkSupport` at `vktSpvAsmNonSemanticInfoTests.cpp#L115-L118`)
- `SPV_KHR_non_semantic_info` SPIR-V extension

## Verification Methods

All tests use `SpvAsmComputeShaderInstance::iterate()` which runs the compute shader and verifies that input floats are copied to output correctly (pass-through shader). The non-semantic instructions are verified by the fact that the shader compiles and executes without error. Source: `vktSpvAsmNonSemanticInfoTests.cpp#L90-L93`.

## Notes

- The shader is essentially a pass-through (copies input to output) with non-semantic instructions added; the test verifies compilation/execution correctness rather than specific output values from the non-semantic instructions
