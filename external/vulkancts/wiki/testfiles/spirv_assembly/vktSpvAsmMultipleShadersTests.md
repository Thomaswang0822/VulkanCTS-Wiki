# vktSpvAsmMultipleShadersTests

## Overview

Tests for SPIR-V modules with multiple compute entry points. Verifies that two compute shader entry points in the same SPIR-V module can be dispatched through separate pipelines ([`mainA` and `mainB`](../../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L147-L178)) with different execution modes and interfaces.

## Role

Implementation file

## Source

- [vktSpvAsmMultipleShadersTests.cpp](../../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L449)

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.multiple_shaders_extended
├── two_entry_points_execution_mode_id
└── two_entry_points_different_interfaces
```

## Test Families

### two_entry_points_execution_mode_id — Two entry points with OpExecutionModeId

Tests a SPIR-V module containing two compute entry points (`mainA` and `mainB`) that each have their own `OpExecutionModeId LocalSizeId` specification. Entry point `mainA` computes subtraction (`v[12+id] = v[id] - v[6+id]`), while `mainB` computes multiplication (`v[18+id] = v[id] * v[6+id]`), as verified in the result checks ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L209-L217)). Both entry points share the same interface (single storage buffer).

Observed in [`TestType::TWO_ENTRY_POINTS_EXECUTION_MODE_ID`](../../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L48-L54) and test creation at [`createMultipleShaderExtendedGroup`](../../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L455-L457).

### two_entry_points_different_interfaces — Two entry points with different interfaces

Tests a SPIR-V module containing two compute entry points (`mainA` and `mainB`) with different interfaces. `mainA` uses one buffer, while `mainB` uses a second buffer. Entry point `mainA` computes addition (`bufferA.v[12+idx] = bufferA.v[idx] + bufferA.v[6+idx]`), while `mainB` computes multiplication with reversed indexing (`bufferB.v[12+idxOut] = bufferB.v[idxIn] * bufferB.v[6+idxIn]`), as verified in the result checks ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L219-L229)).

Observed in [`TestType::TWO_ENTRY_POINTS_DIFFERENT_INTERFACES`](../../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L48-L54) and test creation at [`createMultipleShaderExtendedGroup`](../../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L458-L460).

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| TestType | `TWO_ENTRY_POINTS_EXECUTION_MODE_ID`, `TWO_ENTRY_POINTS_DIFFERENT_INTERFACES` | Type of multi-entry-point test |

## Support Requirements

- **[`VK_KHR_maintenance4`](../../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L441-L445)** — required for `TWO_ENTRY_POINTS_EXECUTION_MODE_ID` test
- [SPIR-V 1.5 build options](../../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L237-L239) — used for both test types

## Verification Methods

- **Execution mode ID test**: After dispatching `mainB` then `mainA`, verifies buffer contents at indices 12-17 contain subtraction results and indices 18-23 contain multiplication results ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L209-L217))
- **Different interfaces test**: After dispatching `mainB` then `mainA`, verifies `bufferA` contains addition results and `bufferB` contains multiplication results with reversed indexing ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L219-L229))

## Notes

- [`createMultipleShaderGroup`](../../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L5508-L5623) (the non-extended version) is in `vktSpvAsmInstructionTests.cpp`, not this file
- Both entry points share the same shader module but are dispatched via separate pipelines with different entry point names ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L147-L178))
- The execution order is `mainB` first, then `mainA` ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L191-L199))
