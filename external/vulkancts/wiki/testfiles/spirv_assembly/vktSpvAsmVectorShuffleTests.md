# vktSpvAsmVectorShuffleTests

## Overview

Tests for OpVectorShuffle with indices including -1 (undefined component), and long vector shuffle operations, using the Amber test framework.

## Role

Implementation file

## Source

- [vktSpvAsmVectorShuffleTests.cpp](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmVectorShuffleTests.cpp)

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.vector_shuffle
├── vector_shuffle
└── long_vector_shuffle
```

## Test Families

### vector_shuffle — Tests OpVectorShuffle with -1 indices

Tests OpVectorShuffle where some component indices are set to -1 (0xFFFFFFFF), which means the resulting component is undefined. Requires `VariablePointerFeatures.variablePointers`. Source: `vktSpvAsmVectorShuffleTests.cpp#L47-L48`.

### long_vector_shuffle — Tests OpVectorShuffle with long vectors

Tests OpVectorShuffle operations on long vectors (vectors with more than 4 components). Requires both `VariablePointerFeatures.variablePointers` and `ShaderLongVectorFeaturesEXT.longVector`. Source: `vktSpvAsmVectorShuffleTests.cpp#L49-L50`.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Vector type | standard (2-4 component), long (>4 component) | Whether standard or long vectors are used |

## Support Requirements

- `VariablePointerFeatures.variablePointers` (both tests)
- `ShaderLongVectorFeaturesEXT.longVector` (long_vector_shuffle only)
- Non-VulkanSC only (guarded by `#ifndef CTS_USES_VULKANSC`)

## Verification Methods

Verification is handled by the Amber test framework using `.amber` test files located in the `spirv_assembly/instruction/compute/vector_shuffle/` data subdirectory. Source: `vktSpvAsmVectorShuffleTests.cpp#L35-L63`.

## Notes

- All tests are Amber-based; the actual SPIR-V assembly and verification logic reside in external `.amber` files
- Non-VulkanSC only
- Only two test cases in this file
