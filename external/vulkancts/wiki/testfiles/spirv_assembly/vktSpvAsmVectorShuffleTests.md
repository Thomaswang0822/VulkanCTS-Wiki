# vktSpvAsmVectorShuffleTests

## Overview

Tests for [`OpVectorShuffle`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/vector_shuffle/vector_shuffle.amber#L68-L70) with an undefined component index (`4294967295`) and long-vector shuffle operations using the Amber test framework.

## Role

Implementation file for the compute `vector_shuffle` group registered by [`createVectorShuffleGroup()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVectorShuffleTests.cpp#L68).

## Source

- [vktSpvAsmVectorShuffleTests.cpp](../../../modules/vulkan/spirv_assembly/vktSpvAsmVectorShuffleTests.cpp#L68)

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.vector_shuffle
├── vector_shuffle
└── long_vector_shuffle
```

## Test Families

### vector_shuffle — Tests OpVectorShuffle with -1 indices

Registers the [`vector_shuffle`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVectorShuffleTests.cpp#L46-L48) Amber case. The Amber source uses `OpUndef` and [`OpVectorShuffle ... 4294967295`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/vector_shuffle/vector_shuffle.amber#L58-L70), with [`VariablePointerFeatures.variablePointers`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/vector_shuffle/vector_shuffle.amber#L10-L12) required.

### long_vector_shuffle — Tests OpVectorShuffle with long vectors

Registers the [`long_vector_shuffle`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVectorShuffleTests.cpp#L49) Amber case. The Amber source requires [`ShaderLongVectorFeaturesEXT.longVector`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/vector_shuffle/long_vector_shuffle.amber#L10-L12), declares a six-component vector with [`OpTypeVectorIdEXT`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/vector_shuffle/long_vector_shuffle.amber#L38-L42), and shuffles it with [`OpVectorShuffle`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/vector_shuffle/long_vector_shuffle.amber#L66-L68).

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Vector type | standard 4-component vector in [`vector_shuffle.amber`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/vector_shuffle/vector_shuffle.amber#L38-L40), long 6-component vector in [`long_vector_shuffle.amber`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/vector_shuffle/long_vector_shuffle.amber#L38-L42) | Whether standard or long vectors are used |

## Support / Feature Requirements

- [`VariablePointerFeatures.variablePointers`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVectorShuffleTests.cpp#L46-L50) (both tests)
- [`ShaderLongVectorFeaturesEXT.longVector`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/vector_shuffle/long_vector_shuffle.amber#L10-L12) (long_vector_shuffle only)
- Non-VulkanSC only through the compile-time guard in [`createTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVectorShuffleTests.cpp#L35-L63).

## Verification Methods

Verification is handled by Amber cases created via [`createAmberTestCase()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVectorShuffleTests.cpp#L52-L58). The standard case probes an SSBO result of [`6.0`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/vector_shuffle/vector_shuffle.amber#L76-L84), and the long-vector case probes the shuffled six-float vector [`4.0 2.0 -3.0 9.0 7.0 1.0`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/vector_shuffle/long_vector_shuffle.amber#L72-L80).

## Notes

- All tests are Amber-based; the actual SPIR-V assembly and verification logic reside in [`vector_shuffle.amber`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/vector_shuffle/vector_shuffle.amber#L13-L84) and [`long_vector_shuffle.amber`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/vector_shuffle/long_vector_shuffle.amber#L14-L80).
- Non-VulkanSC only through the compile-time guard in [`createTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVectorShuffleTests.cpp#L35-L63).
- Only two test cases are registered in the local [`cases`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVectorShuffleTests.cpp#L46-L50) array.
