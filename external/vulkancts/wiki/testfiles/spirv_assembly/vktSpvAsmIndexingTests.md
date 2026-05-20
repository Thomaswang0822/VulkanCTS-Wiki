# vktSpvAsmIndexingTests

## Overview

Tests for SPIR-V Assembly indexing operations using OpAccessChain, OpInBoundsAccessChain, and OpPtrAccessChain. Covers struct-based indexing with various integer sizes (16, 32, 64 bits) and signs, non-16-base-alignment indexing (compute only), and output component indexing (graphics only).

## Role

Implementation file

## Source

- [vktSpvAsmIndexingTests.cpp](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp)

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.indexing
└── input

spirv_assembly.instruction.graphics.indexing
├── input
└── output
```

## Test Families

### input (compute) — Compute input indexing tests

Contains `struct` and `non16basealignment` sub-groups for compute shader input data indexing.

Observed in `createIndexingComputeGroup()` at vktSpvAsmIndexingTests.cpp#L761-L774.

#### struct — Struct-based indexing tests

Tests indexing into a deeply nested struct containing a 2D array of 4x4 matrices using OpAccessChain, OpInBoundsAccessChain, and OpPtrAccessChain. Indices are read from a selector buffer and converted to the desired bit size and sign. For compute, each test also has a `_64bit_indexing` variant (non-VulkanSC only).

Observed in `addComputeIndexingStructTests()` at vktSpvAsmIndexingTests.cpp#L68-L293 and `addGraphicsIndexingStructTests()` at vktSpvAsmIndexingTests.cpp#L295-L532.

#### non16basealignment — Non-16-byte base alignment indexing tests (compute only)

Tests indexing into a struct with non-16-byte-aligned array stride (18 floats per struct instance). Uses OpAccessChain and OpPtrAccessChain to sum all elements of the float array within each struct instance. Requires `VK_KHR_variable_pointers` extension.

Observed in `addComputeIndexingNon16BaseAlignmentTests()` at vktSpvAsmIndexingTests.cpp#L597-L757.

### input (graphics) — Graphics input indexing tests

Contains `struct` sub-group for graphics pipeline input data indexing across all shader stages.

Observed in `createIndexingGraphicsGroup()` at vktSpvAsmIndexingTests.cpp#L776-L789.

### output — Output component indexing tests (graphics only)

Tests indexing into output interface components using OpAccessChain. Uses a per-stage interface operation pattern with different indexing for vertex, fragment, tessellation, and geometry stages.

Observed in `addGraphicsOutputComponentIndexingTests()` at vktSpvAsmIndexingTests.cpp#L534-L595.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| ChainOp | `opaccesschain`, `opinboundsaccesschain`, `opptraccesschain` | Access chain operation type |
| idxSize | 16, 32, 64 | Index integer bit width |
| sign | unsigned (`_u`), signed (`_s`) | Index integer signedness |
| 64bit_indexing | bool (non-VulkanSC only) | Whether to use 64-bit buffer indexing |

Test names follow the pattern: `{chainOp}_{sign}{idxSize}` (e.g., `opaccesschain_u32`, `opptraccesschain_s64_64bit_indexing`).

For `non16basealignment` tests, only `opaccesschain` and `opptraccesschain` are tested.

For `output` (graphics), only a single `component` test exists per stage.

## Support Requirements

- **shaderInt16** — required when `idxSize == 16` — vktSpvAsmIndexingTests.cpp#L277
- **shaderInt64** — required when `idxSize == 64` — vktSpvAsmIndexingTests.cpp#L279
- **VK_KHR_variable_pointers** — required for OpPtrAccessChain tests — vktSpvAsmIndexingTests.cpp#L230
- **variablePointersStorageBuffer** — required for OpPtrAccessChain tests — vktSpvAsmIndexingTests.cpp#L229
- **vertexPipelineStoresAndAtomics** — required for graphics struct tests — vktSpvAsmIndexingTests.cpp#L510
- **fragmentStoresAndAtomics** — required for graphics struct tests — vktSpvAsmIndexingTests.cpp#L511
- SPIR-V extensions: `SPV_KHR_variable_pointers`, `SPV_KHR_storage_buffer_storage_class` — for OpPtrAccessChain — vktSpvAsmIndexingTests.cpp#L226-L227

## Verification Methods

- **Struct tests**: Output buffer values are compared against CPU-computed expected values. The expected output is calculated by indexing into the input data using the same indices as the shader, following the struct layout — vktSpvAsmIndexingTests.cpp#L238-L244 (compute) and vktSpvAsmIndexingTests.cpp#L498-L505 (graphics)
- **Non-16-base-alignment tests**: Output is the sum of all float array elements per struct instance, computed on CPU using whole numbers to avoid rounding differences — vktSpvAsmIndexingTests.cpp#L717-L723
- **Output component tests**: Uses `GraphicsInterfaces` with input/output type specifications and `createTestsForAllStages` for per-stage verification — vktSpvAsmIndexingTests.cpp#L588-L594

## Notes

- The `_64bit_indexing` variants are guarded by `#ifndef CTS_USES_VULKANSC` — vktSpvAsmIndexingTests.cpp#L284-L288 (compute) and vktSpvAsmIndexingTests.cpp#L521-L527 (graphics)
- OpPtrAccessChain uses `StorageBuffer` storage class and `Block` decoration, while OpAccessChain/OpInBoundsAccessChain use `Uniform` storage class and `BufferBlock` decoration — vktSpvAsmIndexingTests.cpp#L207-L231
- The `non16basealignment` tests use floor-rounded input data to avoid CPU/GPU rounding differences — vktSpvAsmIndexingTests.cpp#L709
