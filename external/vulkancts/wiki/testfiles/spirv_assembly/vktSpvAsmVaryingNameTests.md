# vktSpvAsmVaryingNameTests

## Overview

Tests that the mapping of varyings between vertex and fragment shaders is based on [`Location 0`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVaryingNameTests.cpp#L88-L91) rather than [`OpName`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVaryingNameTests.cpp#L54-L59), verifying that varying data passes correctly regardless of whether OpNames match, differ, or are absent.

## Role

Implementation file for the graphics `varying_name` group registered by [`createVaryingNameGraphicsGroup()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVaryingNameTests.cpp#L234).

## Source

- [vktSpvAsmVaryingNameTests.cpp](../../../modules/vulkan/spirv_assembly/vktSpvAsmVaryingNameTests.cpp#L234)

## Registration Hierarchy

```text
spirv_assembly.instruction.graphics.varying_name
├── names_match
├── names_differ
└── no_names
```

## Test Families

### names_match — Tests varying with matching OpNames in vertex and fragment shaders

The vertex shader outputs a float value of [`1.0`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVaryingNameTests.cpp#L111-L119) at [`Location 0`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVaryingNameTests.cpp#L88-L91) with `OpName %dataOut "data"`, and the fragment shader reads it at [`Location 0`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVaryingNameTests.cpp#L141-L143) with `OpName %dataIn "data"`; the wrapper is [`createShadersNamesMatch()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVaryingNameTests.cpp#L175-L178).

### names_differ — Tests varying with different OpNames in vertex and fragment shaders

The vertex shader uses `OpName %dataOut "dataOut"` while the fragment shader uses `OpName %dataIn "dataIn"`, supplied by [`createShadersNamesDiffer()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVaryingNameTests.cpp#L180-L183), while both variables keep the same Location decorations.

### no_names — Tests varying with no OpNames in either shader

Neither the vertex shader output variable nor the fragment shader input variable receives an OpName string because [`createShadersNoNames()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVaryingNameTests.cpp#L185-L188) passes empty names to `createShaders()`, which emits no `opNameVert` or `opNameFrag` text for empty inputs.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Name scenario | [`names_match`, `names_differ`, `no_names`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVaryingNameTests.cpp#L238-L240) | How OpName is applied to the varying in vertex and fragment shaders |

## Support Requirements

- [`VK_KHR_storage_buffer_storage_class`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVaryingNameTests.cpp#L214-L215) extension
- [`fragmentStoresAndAtomics`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVaryingNameTests.cpp#L214) feature

## Verification Methods

Each test creates a vertex-fragment pipeline in [`addGraphicsVaryingNameTest()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVaryingNameTests.cpp#L190-L230). The vertex shader stores `1.0` into `%dataOut`, the fragment shader loads `%dataIn` and stores it to `dataOutput`, and the expected SSBO is [`1.0f`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVaryingNameTests.cpp#L202-L218). Execution and comparison use [`runAndVerifyDefaultPipeline`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVaryingNameTests.cpp#L226-L228).

## Notes

- Graphics-only test registered by [`createVaryingNameGraphicsGroup()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVaryingNameTests.cpp#L234-L245) with no compute variant in this file.
- The test demonstrates that SPIR-V `OpName` text is varied while [`Location 0`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVaryingNameTests.cpp#L88-L91) remains constant between shader stages.
- All three registered cases use the same Location 0 for the varying; only the OpName inputs in the [`params`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVaryingNameTests.cpp#L238-L240) differ.
