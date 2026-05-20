# vktSpvAsmVaryingNameTests

## Overview

Tests that the mapping of varyings between vertex and fragment shaders is based on location index rather than OpName, verifying that varying data passes correctly regardless of whether OpNames match, differ, or are absent.

## Role

Implementation file

## Source

- [vktSpvAsmVaryingNameTests.cpp](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmVaryingNameTests.cpp)

## Registration Hierarchy

```text
spirv_assembly.instruction.graphics.varying_name
├── names_match
├── names_differ
└── no_names
```

## Test Families

### names_match — Tests varying with matching OpNames in vertex and fragment shaders

The vertex shader outputs a float value of 1.0 at Location 0 with `OpName %dataOut "data"`, and the fragment shader reads it at Location 0 with `OpName %dataIn "data"`. Verifies that the varying is correctly passed when both shaders use the same name. Source: `vktSpvAsmVaryingNameTests.cpp#L175-L178`.

### names_differ — Tests varying with different OpNames in vertex and fragment shaders

The vertex shader uses `OpName %dataOut "dataOut"` while the fragment shader uses `OpName %dataIn "dataIn"`. Verifies that the varying is correctly passed despite the name mismatch, confirming that location-based matching is used. Source: `vktSpvAsmVaryingNameTests.cpp#L180-L183`.

### no_names — Tests varying with no OpNames in either shader

Neither the vertex shader's output variable nor the fragment shader's input variable has an OpName decoration. Verifies that the varying is correctly passed without any name information, confirming pure location-based matching. Source: `vktSpvAsmVaryingNameTests.cpp#L185-L188`.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Name scenario | names_match, names_differ, no_names | How OpName is applied to the varying in vertex and fragment shaders |

## Support Requirements

- `VK_KHR_storage_buffer_storage_class` extension
- `fragmentStoresAndAtomics` feature

## Verification Methods

Each test creates a vertex-fragment pipeline where the vertex shader writes a float value of 1.0 to an output varying at Location 0, and the fragment shader reads it from the corresponding input and stores it to an SSBO. The output buffer is verified to contain the value 1.0. Uses `runAndVerifyDefaultPipeline` for graphics pipeline execution and verification. Source: `vktSpvAsmVaryingNameTests.cpp#L190-L230`.

## Notes

- Graphics-only test (no compute variant)
- The test demonstrates that SPIR-V OpName is purely decorative and does not affect varying matching between shader stages
- All three test cases use the same Location 0 for the varying; only the OpName decorations differ
