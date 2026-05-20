# vktSpvAsmSpirvVersionTests

## Overview

Tests that verify the SPIR-V version of compiled shader binaries matches the requested version, across all SPIR-V versions (1.0 through latest) and all shader stages (compute, vertex, fragment, geometry, tessellation control, tessellation evaluation).

## Role

Implementation file

## Source

- [vktSpvAsmSpirvVersionTests.cpp](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersionTests.cpp)

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.spirv_version
├── 1_0_compute
├── 1_1_compute
├── 1_2_compute
├── 1_3_compute
├── 1_4_compute
├── 1_5_compute
└── 1_6_compute

spirv_assembly.instruction.graphics.spirv_version
├── 1_0_fragment
├── 1_0_geometry
├── 1_0_tesselation_control
├── 1_0_tesselation_evaluation
├── 1_0_vertex
├── 1_1_fragment
├── 1_1_geometry
├── 1_1_tesselation_control
├── 1_1_tesselation_evaluation
├── 1_1_vertex
├── 1_2_fragment
├── 1_2_geometry
├── 1_2_tesselation_control
├── 1_2_tesselation_evaluation
├── 1_2_vertex
├── 1_3_fragment
├── 1_3_geometry
├── 1_3_tesselation_control
├── 1_3_tesselation_evaluation
├── 1_3_vertex
├── 1_4_fragment
├── 1_4_geometry
├── 1_4_tesselation_control
├── 1_4_tesselation_evaluation
├── 1_4_vertex
├── 1_5_fragment
├── 1_5_geometry
├── 1_5_tesselation_control
├── 1_5_tesselation_evaluation
├── 1_5_vertex
├── 1_6_fragment
├── 1_6_geometry
├── 1_6_tesselation_control
├── 1_6_tesselation_evaluation
└── 1_6_vertex
```

## Test Families

### SPIR-V version checks — Verifies compiled binary SPIR-V version matches request

For each SPIR-V version (1.0 through latest) and each applicable shader stage, a test case compiles a simple shader at the requested SPIR-V version and then checks that the compiled binary's SPIR-V version header matches the requested version. Compute shaders use a simple pass-through (negate input floats). Graphics shaders use a vertex-fragment pipeline with a test function that performs simple arithmetic. Source: `vktSpvAsmSpirvVersionTests.cpp#L376-L404`.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| SPIR-V version | 1_0, 1_1, 1_2, 1_3, 1_4, 1_5, 1_6 | The requested SPIR-V version |
| Operation | compute, vertex, tesselation_evaluation, tesselation_control, geometry, fragment | The shader stage being tested |

## Support Requirements

- Each test checks that the device/instance supports the requested SPIR-V version via `getMaxSpirvVersionForAsm` (`vktSpvAsmSpirvVersionTests.cpp#L276-L278`)
- Tessellation stages require `tessellationShader` feature
- Geometry stage requires `geometryShader` feature

## Verification Methods

The `isSpirVersionsAsRequested` function (`vktSpvAsmSpirvVersionTests.cpp#L182-L198`) iterates over all binaries in the collection and checks that each binary's SPIR-V version (extracted from the header) matches the requested version. For compute shaders, the `SpvAsmComputeSpirvVersionsInstance::iterate()` method also runs the shader and verifies output correctness. For graphics shaders, `runAndVerifyDefaultPipeline` is used.

## Notes

- Test names follow the pattern `{version}_{stage}`, e.g., `1_4_compute` or `1_6_fragment`
- SPIR-V versions > 1.3 use `StorageBuffer` storage class and `Block` decoration; versions ≤ 1.3 use `Uniform`/`BufferBlock`
- SPIR-V versions > 1.3 include `%indata %outdata` in the entry point interface (required by SPIR-V 1.4+)
