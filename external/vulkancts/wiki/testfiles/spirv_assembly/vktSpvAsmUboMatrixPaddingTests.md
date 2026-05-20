# vktSpvAsmUboMatrixPaddingTests

## Overview

Tests for UBO matrix padding, verifying that mat2x2 data stored in a uniform buffer with proper padding and strides is correctly read and written out by shaders.

## Role

Implementation file

## Source

- [vktSpvAsmUboMatrixPaddingTests.cpp](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.cpp)

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.ubo_padding
└── mat2x2

spirv_assembly.instruction.graphics.ubo_padding
├── mat2x2_vert
├── mat2x2_tessc
├── mat2x2_tesse
├── mat2x2_geom
└── mat2x2_frag
```

## Test Families

### mat2x2 (compute) — Tests mat2x2 UBO padding in compute shader

Reads an array of 128 `mat2x2` values from a UBO (with ArrayStride 32 and MatrixStride 16) and writes the individual float components to an output SSBO. The mat2x2 has ColMajor decoration with 16-byte matrix stride. Input data is generated as pairs of vec4 values where the first vec4 contains (x, y, 0, 0) and the second contains (z, w, 0, 0) of the expected output vec4. Source: `vktSpvAsmUboMatrixPaddingTests.cpp#L46-L147`.

### mat2x2_vert/tessc/tesse/geom/frag (graphics) — Tests mat2x2 UBO padding in graphics shaders

Same test logic as the compute variant but runs in vertex, tessellation control, tessellation evaluation, geometry, and fragment shader stages. The graphics test uses a for-loop in the test function to iterate over all 128 elements. Vertex/tessellation/geometry stages require `vertexPipelineStoresAndAtomics`; fragment stage requires `fragmentStoresAndAtomics`. Source: `vktSpvAsmUboMatrixPaddingTests.cpp#L149-L274`.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Shader stage | compute, vertex, tess_ctrl, tess_eval, geometry, fragment | The pipeline stage being tested |
| Matrix type | mat2x2 | Only mat2x2 is tested in this file |

## Support Requirements

- **Compute**: No special extensions beyond baseline
- **Graphics vertex/tess/geom**: `vertexPipelineStoresAndAtomics` feature
- **Graphics fragment**: `fragmentStoresAndAtomics` feature
- Tessellation stages require `tessellationShader` feature
- Geometry stage requires `geometryShader` feature

## Verification Methods

Both compute and graphics tests compare the output vec4 buffer against the expected output. The input UBO contains mat2x2 values where each matrix's four components (x, y, z, w) are spread across two vec4 rows with padding. The output buffer should contain the four components packed into a single vec4 per element. Source: `vktSpvAsmUboMatrixPaddingTests.cpp#L129-L146` (compute), `vktSpvAsmUboMatrixPaddingTests.cpp#L163-L173` (graphics).

## Notes

- The UBO uses `Block` decoration with `ColMajor` and `MatrixStride 16` for the mat2x2 member
- The SSBO output uses `BufferBlock` decoration with an array of vec4
- Input data is carefully constructed so that mat2x2 row 0 = (x, y) and row 1 = (z, w), with the output vec4 = (x, y, z, w)
