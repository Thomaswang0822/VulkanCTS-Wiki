# vktSpvAsmMultipleShadersTests

## Overview

Tests for SPIR-V modules with multiple entry points (compute shaders). Verifies that two compute shader entry points in the same SPIR-V module can be correctly dispatched with different execution modes and interfaces.

## Role

Implementation file

## Source

- [vktSpvAsmMultipleShadersTests.cpp](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp)

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.multiple_shaders_extended
├── two_entry_points_execution_mode_id
└── two_entry_points_different_interfaces
```

## Test Families

### two_entry_points_execution_mode_id — Two entry points with OpExecutionModeId

Tests a SPIR-V module containing two compute entry points (`mainA` and `mainB`) that each have their own `OpExecutionModeId LocalSizeId` specification (local_size_x=2, local_size_y=3). Entry point `mainA` computes subtraction (v[12+id] = v[id] - v[6+id]), while `mainB` computes multiplication (v[18+id] = v[id] * v[6+id]). Both entry points share the same interface (single storage buffer).

Observed in `TestType::TWO_ENTRY_POINTS_EXECUTION_MODE_ID` at vktSpvAsmMultipleShadersTests.cpp#L49 and test creation at vktSpvAsmMultipleShadersTests.cpp#L455-L457.

### two_entry_points_different_interfaces — Two entry points with different interfaces

Tests a SPIR-V module containing two compute entry points (`mainA` and `mainB`) with different interfaces. `mainA` uses `gl_LocalInvocationIndex` and a single buffer, while `mainB` uses `gl_LocalInvocationId` and `gl_NumWorkGroups` with a second buffer. Entry point `mainA` computes addition (bufferA.v[12+idx] = bufferA.v[idx] + bufferA.v[6+idx]), while `mainB` computes multiplication with reversed indexing (bufferB.v[12+idxOut] = bufferB.v[idxIn] * bufferB.v[6+idxIn]).

Observed in `TestType::TWO_ENTRY_POINTS_DIFFERENT_INTERFACES` at vktSpvAsmMultipleShadersTests.cpp#L50 and test creation at vktSpvAsmMultipleShadersTests.cpp#L458-L460.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| TestType | `TWO_ENTRY_POINTS_EXECUTION_MODE_ID`, `TWO_ENTRY_POINTS_DIFFERENT_INTERFACES` | Type of multi-entry-point test |

## Support Requirements

- **VK_KHR_maintenance4** — required for `TWO_ENTRY_POINTS_EXECUTION_MODE_ID` test — vktSpvAsmMultipleShadersTests.cpp#L443-L444
- SPIR-V 1.5 build options — used for both test types — vktSpvAsmMultipleShadersTests.cpp#L239

## Verification Methods

- **Execution mode ID test**: After dispatching `mainB` then `mainA`, verifies buffer contents at indices 12-17 contain subtraction results and indices 18-23 contain multiplication results — vktSpvAsmMultipleShadersTests.cpp#L209-L217
- **Different interfaces test**: After dispatching `mainB` then `mainA`, verifies bufferA contains addition results and bufferB contains multiplication results with reversed indexing — vktSpvAsmMultipleShadersTests.cpp#L219-L229

## Notes

- `createMultipleShaderGroup` (the non-extended version) is in `vktSpvAsmInstructionTests.cpp`, not this file
- Both entry points share the same shader module but are dispatched via separate pipelines with different entry point names — vktSpvAsmMultipleShadersTests.cpp#L147-L178
- The execution order is `mainB` first, then `mainA` — vktSpvAsmMultipleShadersTests.cpp#L191-L199
