# vktSpvAsmIndexingTests

## Overview

Tests for SPIR-V Assembly indexing operations using `OpAccessChain`, `OpInBoundsAccessChain`, and `OpPtrAccessChain`. The compute group registers `input` with `struct` and `non16basealignment` children, while the graphics group registers `input`/`struct` and `output`/`component` coverage ([createIndexingComputeGroup()](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L761-L773), [createIndexingGraphicsGroup()](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L776-L788)).

## Role

Implementation file

## Source

- [vktSpvAsmIndexingTests.cpp](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L761)

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

Observed in [`createIndexingComputeGroup()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L761-L773).

#### struct — Struct-based indexing tests

Tests indexing into a deeply nested struct containing a 2D array of 4x4 matrices using OpAccessChain, OpInBoundsAccessChain, and OpPtrAccessChain. Indices are read from a selector buffer and converted to the desired bit size and sign. For compute, each test also has a `_64bit_indexing` variant (non-VulkanSC only).

Observed in [`addComputeIndexingStructTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L68-L293) and [`addGraphicsIndexingStructTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L295-L532).

#### non16basealignment — Non-16-byte base alignment indexing tests (compute only)

Tests indexing into a struct with non-16-byte-aligned array stride (18 floats per struct instance). Uses OpAccessChain and OpPtrAccessChain to sum all elements of the float array within each struct instance. Requires `VK_KHR_variable_pointers` extension.

Observed in [`addComputeIndexingNon16BaseAlignmentTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L597-L757).

### input (graphics) — Graphics input indexing tests

Contains `struct` sub-group for graphics pipeline input data indexing across all shader stages.

Observed in [`createIndexingGraphicsGroup()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L776-L788).

### output — Output component indexing tests (graphics only)

Tests indexing into output interface components using OpAccessChain. Uses a per-stage interface operation pattern with different indexing for vertex, fragment, tessellation, and geometry stages.

Observed in [`addGraphicsOutputComponentIndexingTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L534-L595).

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| ChainOp | `opaccesschain`, `opinboundsaccesschain`, `opptraccesschain` | Access-chain operation names from `chainOpTestNames` ([chainOpTestNames](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L60-L61)) |
| idxSize | 16, 32, 64 | Index integer bit widths from `idxSizes` ([idxSizes](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L60-L61)) |
| sign | unsigned (`_u`), signed (`_s`) | Signedness suffix generated in struct test names ([addComputeIndexingStructTests()](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L87-L95), [addGraphicsIndexingStructTests()](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L317-L325)) |
| 64bit_indexing | bool (non-VulkanSC only) | Whether to use 64-bit buffer indexing |

Test names follow the pattern `{chainOp}_{sign}{idxSize}` and may append `_64bit_indexing` for non-VulkanSC variants ([addComputeIndexingStructTests()](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L93-L95), [addComputeIndexingStructTests()](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L284-L288)).

For `non16basealignment` tests, only `opaccesschain` and `opptraccesschain` are tested ([addComputeIndexingNon16BaseAlignmentTests()](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L610-L612), [addComputeIndexingNon16BaseAlignmentTests()](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L729-L753)).

For `output` graphics coverage, the file creates a single `component` test across all stages ([addGraphicsOutputComponentIndexingTests()](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L588-L594)).

## Support Requirements

- **`shaderInt16`** — requested when `idxSize == 16` ([addComputeIndexingStructTests()](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L276-L280))
- **`shaderInt64`** — requested when `idxSize == 64` ([addComputeIndexingStructTests()](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L276-L280))
- **`VK_KHR_variable_pointers`** — requested for `OpPtrAccessChain` struct tests and non-16-base-alignment tests ([addComputeIndexingStructTests()](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L219-L231), [addComputeIndexingNon16BaseAlignmentTests()](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L700-L701))
- **`variablePointersStorageBuffer`** — requested for `OpPtrAccessChain` struct tests and non-16-base-alignment tests ([addComputeIndexingStructTests()](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L224-L230), [addComputeIndexingNon16BaseAlignmentTests()](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L700-L726))
- **`vertexPipelineStoresAndAtomics`** — requested for graphics struct tests ([addGraphicsIndexingStructTests()](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L507-L518))
- **`fragmentStoresAndAtomics`** — requested for graphics struct tests ([addGraphicsIndexingStructTests()](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L507-L518))
- SPIR-V extensions: `SPV_KHR_variable_pointers`, `SPV_KHR_storage_buffer_storage_class` for `OpPtrAccessChain` and non-16-base-alignment variants ([addComputeIndexingStructTests()](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L224-L227), [addComputeIndexingNon16BaseAlignmentTests()](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L735-L737))

## Verification Methods

- **Struct tests**: output buffer values are compared against CPU-computed expected values calculated by indexing input data with the same selector indices as the shader ([addComputeIndexingStructTests()](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L237-L244), [addGraphicsIndexingStructTests()](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L498-L505))
- **Non-16-base-alignment tests**: output is the sum of all float-array elements per struct instance, computed on CPU after floor-rounding inputs to avoid CPU/GPU rounding differences ([addComputeIndexingNon16BaseAlignmentTests()](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L703-L723))
- **Output component tests**: uses `GraphicsInterfaces` with input/output type specifications and `createTestsForAllStages` for per-stage verification ([addGraphicsOutputComponentIndexingTests()](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L588-L594))

## Notes

- The `_64bit_indexing` variants are guarded by `#ifndef CTS_USES_VULKANSC` in compute and graphics struct tests ([addComputeIndexingStructTests()](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L284-L288), [addGraphicsIndexingStructTests()](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L521-L527))
- `OpPtrAccessChain` uses `StorageBuffer` storage class and `Block` decoration, while `OpAccessChain`/`OpInBoundsAccessChain` use `Uniform` storage class and `BufferBlock` decoration ([addComputeIndexingStructTests()](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L204-L231))
- The `non16basealignment` tests use floor-rounded input data to avoid CPU/GPU rounding differences ([addComputeIndexingNon16BaseAlignmentTests()](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L703-L710))
