# vktSpvAsmUboMatrixPaddingTests

## Overview

Tests UBO matrix padding for a `mat2x2` array, verifying that shader code reads padded uniform-buffer matrix data and writes the four matrix components to an output buffer ([compute setup](../../../modules/vulkan/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.cpp#L46-L146), [graphics setup](../../../modules/vulkan/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.cpp#L149-L273)).

## Role

Implementation file

## Source

- [vktSpvAsmUboMatrixPaddingTests.cpp](../../../modules/vulkan/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.cpp#L278)

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

Reads an array of 128 `mat2x2` values from a UBO with `ArrayStride 32`, `ColMajor`, and `MatrixStride 16`, then writes the individual float components to an output buffer ([decorations](../../../modules/vulkan/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.cpp#L62-L73), [load/store sequence](../../../modules/vulkan/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.cpp#L110-L125)). Input data is generated as two `vec4` values per matrix, where the first carries `(x, y, 0, 0)` and the second carries `(z, w, 0, 0)` for the expected output `vec4` ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.cpp#L129-L146)).

### mat2x2_vert/tessc/tesse/geom/frag (graphics) — Tests mat2x2 UBO padding in graphics shaders

Uses equivalent UBO and output-buffer decorations for graphics shader stages, with the test function looping over all 128 elements and copying the four matrix components into the output buffer ([decorations](../../../modules/vulkan/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.cpp#L178-L202), [loop and writes](../../../modules/vulkan/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.cpp#L204-L250)). The registered stage cases are vertex, tessellation control, tessellation evaluation, geometry, and fragment ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.cpp#L254-L273)).

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Shader stage | compute, vertex, tessellation control, tessellation evaluation, geometry, fragment | Compute registers `mat2x2`; graphics registers `mat2x2_vert`, `mat2x2_tessc`, `mat2x2_tesse`, `mat2x2_geom`, and `mat2x2_frag` ([compute](../../../modules/vulkan/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.cpp#L139-L146), [graphics](../../../modules/vulkan/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.cpp#L254-L273)) |
| Matrix type | `mat2x2` | The source defines `%mat2v2float` / `%mat2v2f` and arrays of that matrix type ([compute](../../../modules/vulkan/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.cpp#L96-L100), [graphics](../../../modules/vulkan/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.cpp#L183-L186)) |
| Element count | 128 | Both compute and graphics paths use 128 data points ([compute](../../../modules/vulkan/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.cpp#L49-L50), [graphics](../../../modules/vulkan/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.cpp#L151-L153)) |
| Padding layout | `ArrayStride 32`, `MatrixStride 16`, `ColMajor` | Matrix padding and layout decorations under test ([compute](../../../modules/vulkan/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.cpp#L67-L71), [graphics](../../../modules/vulkan/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.cpp#L196-L200)) |

## Support Requirements

- **Compute**: the file sets no special feature or extension fields for the compute `mat2x2` case beyond its SPIR-V assembly and resource declarations ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.cpp#L139-L146)).
- **Graphics vertex/tessellation/geometry**: `vertexPipelineStoresAndAtomics` is enabled before creating vertex, tessellation, and geometry cases ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.cpp#L254-L268)).
- **Graphics fragment**: `fragmentStoresAndAtomics` is enabled before creating the fragment case ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.cpp#L270-L273)).
- Tessellation and geometry stage availability is handled by `createTestForStage` for the corresponding stage cases; this file passes `VK_SHADER_STAGE_TESSELLATION_CONTROL_BIT`, `VK_SHADER_STAGE_TESSELLATION_EVALUATION_BIT`, and `VK_SHADER_STAGE_GEOMETRY_BIT` at registration time ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.cpp#L259-L268)).

## Verification Methods

Both compute and graphics tests compare the output `vec4` buffer against expected output data populated on the CPU. The input UBO contains each matrix's four expected components `(x, y, z, w)` spread across two padded `vec4` rows, and the shader writes them into one output `vec4` per element ([compute data and outputs](../../../modules/vulkan/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.cpp#L129-L146), [graphics data and resources](../../../modules/vulkan/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.cpp#L163-L174)).

## Notes

- The compute UBO uses `Block` decoration with `ColMajor` and `MatrixStride 16` for the `mat2x2` member ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.cpp#L67-L73)).
- The graphics output buffer uses `BufferBlock`, while the input UBO uses `Block` ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.cpp#L191-L202)).
- Input data is constructed so that matrix column/row accesses recover `(x, y, z, w)` from two padded `vec4` values ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.cpp#L129-L137), [graphics source](../../../modules/vulkan/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.cpp#L163-L171)).
