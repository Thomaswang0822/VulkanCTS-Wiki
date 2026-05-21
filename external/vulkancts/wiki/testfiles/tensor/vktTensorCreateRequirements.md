# vktTensorCreateRequirements

## Overview

This test file validates that tensor object creation and memory requirement queries behave correctly for the `VK_ARM_tensors` extension. It creates tensor objects across a range of formats and tiling modes, queries their memory requirements via `vkGetTensorMemoryRequirementsARM`, and verifies that the reported memory size is sane.

## Role of file

Registers the subgroup `creation_and_requirements` under `dEQP-VK.tensor`. The factory function [`createTensorCreateRequirementsTests`](../../../modules/vulkan/tensor/vktTensorCreateRequirements.cpp#L251-L258) creates a `tcu::TestCaseGroup` named `"creation_and_requirements"` and populates it with test cases for every combination of format and tiling via [`addCreateRequirementTests`](../../../modules/vulkan/tensor/vktTensorCreateRequirements.cpp#L239-L249).

## Source code link

[vktTensorCreateRequirements.cpp](../../../modules/vulkan/tensor/vktTensorCreateRequirements.cpp)

## Registration Hierarchy

```text
tensor.creation_and_requirements
├── linear_r8_uint
├── linear_r8_sint
├── linear_r16_uint
├── linear_r16_sint
├── linear_r32_uint
├── linear_r32_sint
├── linear_r64_uint
├── linear_r64_sint
├── optimal_r8_uint
├── optimal_r8_sint
├── optimal_r16_uint
├── optimal_r16_sint
├── optimal_r32_uint
├── optimal_r32_sint
├── optimal_r64_uint
└── optimal_r64_sint
```

## Test Families

### linear_r8_uint

Tests tensor creation and memory requirement query for `VK_FORMAT_R8_UINT` with `VK_TENSOR_TILING_LINEAR_ARM`. The test name is composed as `tensorTilingShortName(tiling) + "_" + tensorFormatShortName(format)` ([vktTensorCreateRequirements.cpp#L211](../../../modules/vulkan/tensor/vktTensorCreateRequirements.cpp#L211), [vktTensorTestsUtil.cpp#L204-L206](../../../modules/vulkan/tensor/vktTensorTestsUtil.cpp#L204-L206), [vktTensorTestsUtil.cpp#L221-L222](../../../modules/vulkan/tensor/vktTensorTestsUtil.cpp#L221-L222)).

### linear_r8_sint

Tests tensor creation and memory requirement query for `VK_FORMAT_R8_SINT` with `VK_TENSOR_TILING_LINEAR_ARM`.

### linear_r16_uint

Tests tensor creation and memory requirement query for `VK_FORMAT_R16_UINT` with `VK_TENSOR_TILING_LINEAR_ARM`.

### linear_r16_sint

Tests tensor creation and memory requirement query for `VK_FORMAT_R16_SINT` with `VK_TENSOR_TILING_LINEAR_ARM`.

### linear_r32_uint

Tests tensor creation and memory requirement query for `VK_FORMAT_R32_UINT` with `VK_TENSOR_TILING_LINEAR_ARM`.

### linear_r32_sint

Tests tensor creation and memory requirement query for `VK_FORMAT_R32_SINT` with `VK_TENSOR_TILING_LINEAR_ARM`.

### linear_r64_uint

Tests tensor creation and memory requirement query for `VK_FORMAT_R64_UINT` with `VK_TENSOR_TILING_LINEAR_ARM`.

### linear_r64_sint

Tests tensor creation and memory requirement query for `VK_FORMAT_R64_SINT` with `VK_TENSOR_TILING_LINEAR_ARM`.

### optimal_r8_uint

Tests tensor creation and memory requirement query for `VK_FORMAT_R8_UINT` with `VK_TENSOR_TILING_OPTIMAL_ARM`.

### optimal_r8_sint

Tests tensor creation and memory requirement query for `VK_FORMAT_R8_SINT` with `VK_TENSOR_TILING_OPTIMAL_ARM`.

### optimal_r16_uint

Tests tensor creation and memory requirement query for `VK_FORMAT_R16_UINT` with `VK_TENSOR_TILING_OPTIMAL_ARM`.

### optimal_r16_sint

Tests tensor creation and memory requirement query for `VK_FORMAT_R16_SINT` with `VK_TENSOR_TILING_OPTIMAL_ARM`.

### optimal_r32_uint

Tests tensor creation and memory requirement query for `VK_FORMAT_R32_UINT` with `VK_TENSOR_TILING_OPTIMAL_ARM`.

### optimal_r32_sint

Tests tensor creation and memory requirement query for `VK_FORMAT_R32_SINT` with `VK_TENSOR_TILING_OPTIMAL_ARM`.

### optimal_r64_uint

Tests tensor creation and memory requirement query for `VK_FORMAT_R64_UINT` with `VK_TENSOR_TILING_OPTIMAL_ARM`.

### optimal_r64_sint

Tests tensor creation and memory requirement query for `VK_FORMAT_R64_SINT` with `VK_TENSOR_TILING_OPTIMAL_ARM`.

## Parameter dimensions

Each test case is parameterized by two dimensions, iterated in [`addCreateRequirementTests`](../../../modules/vulkan/tensor/vktTensorCreateRequirements.cpp#L239-L249):

| Dimension | Values | Source |
|-----------|--------|--------|
| Format | `VK_FORMAT_R8_UINT`, `VK_FORMAT_R8_SINT`, `VK_FORMAT_R16_UINT`, `VK_FORMAT_R16_SINT`, `VK_FORMAT_R32_UINT`, `VK_FORMAT_R32_SINT`, `VK_FORMAT_R64_UINT`, `VK_FORMAT_R64_SINT` | [`getAllTestFormats()`](../../../modules/vulkan/tensor/vktTensorTestsUtil.cpp#L48-L56) |
| Tiling | `VK_TENSOR_TILING_LINEAR_ARM`, `VK_TENSOR_TILING_OPTIMAL_ARM` | [vktTensorCreateRequirements.cpp#L244](../../../modules/vulkan/tensor/vktTensorCreateRequirements.cpp#L244) |

This yields 8 formats x 2 tilings = 16 test cases total.

Within each test instance, the helper [`getMaxTensorParameters`](../../../modules/vulkan/tensor/vktTensorCreateRequirements.cpp#L55-L126) generates a list of `TensorParameters` that exercise the device's reported maximum limits:

- **Packed tensors**: For each dimension count from 1 to `maxTensorDimensionCount`, a packed tensor is constructed with dimensions filled up to `maxPerDimensionTensorElements`, capped by `maxTensorElements` and `maxTensorSize` ([vktTensorCreateRequirements.cpp#L66-L85](../../../modules/vulkan/tensor/vktTensorCreateRequirements.cpp#L66-L85)).
- **Non-packed (strided) tensors**: For linear tiling only, if the device supports non-packed tensors (`tensorNonPacked` feature), additional tensor configurations are generated with maximum strides. Each dimension has size 1, with the innermost stride set to `getFormatSize(format)` and outer strides set to the maximum allowed stride ([vktTensorCreateRequirements.cpp#L88-L123](../../../modules/vulkan/tensor/vktTensorCreateRequirements.cpp#L88-L123)).

## Support/feature requirements

- **Extension**: `VK_ARM_tensors` is required. Checked in [`TensorRequirementsTestCase::checkSupport`](../../../modules/vulkan/tensor/vktTensorCreateRequirements.cpp#L222-L230) via `ctx.requireDeviceFunctionality("VK_ARM_tensors")`.
- **Format support**: Each test case checks that the format/tiling combination supports `VK_FORMAT_FEATURE_2_TENSOR_SHADER_BIT_ARM` via [`formatSupportTensorFlags`](../../../modules/vulkan/tensor/vktTensorTestsUtil.cpp#L341-L363). If not supported, `TCU_THROW(NotSupportedError)` is raised in `checkSupport`, and the test instance also skips unsupported format/tiling combinations at runtime ([vktTensorCreateRequirements.cpp#L146-L149](../../../modules/vulkan/tensor/vktTensorCreateRequirements.cpp#L146-L149)).
- **Non-packed tensor feature**: The `tensorNonPacked` feature (queried via [`deviceSupportsNonPackedTensors`](../../../modules/vulkan/tensor/vktTensorTestsUtil.cpp#L365-L380)) gates whether strided tensor configurations are generated in [`getMaxTensorParameters`](../../../modules/vulkan/tensor/vktTensorCreateRequirements.cpp#L88). This is not a hard requirement; if unsupported, only packed tensors are tested.

## Verification methods

The test instance [`TensorRequirementsTestInstance::iterate`](../../../modules/vulkan/tensor/vktTensorCreateRequirements.cpp#L138-L199) performs the following verification for each `TensorParameters` entry:

1. **Tensor creation**: Creates a tensor via [`makeTensorDescription`](../../../modules/vulkan/tensor/vktTensorCreateRequirements.cpp#L152-L153) and [`makeTensorCreateInfo`](../../../modules/vulkan/tensor/vktTensorCreateRequirements.cpp#L154), then instantiates it with [`createTensorARM`](../../../modules/vulkan/tensor/vktTensorCreateRequirements.cpp#L155).

2. **Memory requirement query**: Calls `vkGetTensorMemoryRequirementsARM` to obtain `VkMemoryRequirements2` ([vktTensorCreateRequirements.cpp#L157-L164](../../../modules/vulkan/tensor/vktTensorCreateRequirements.cpp#L157-L164)).

3. **Memory type bits check**: Asserts that `memoryTypeBits` is non-zero. If zero, the test fails with `"No memory type bits set"` ([vktTensorCreateRequirements.cpp#L167-L169](../../../modules/vulkan/tensor/vktTensorCreateRequirements.cpp#L167-L169)).

4. **Memory size sanity check (linear tiling only)**: For `VK_TENSOR_TILING_LINEAR_ARM`, the test computes an expected minimum size and verifies that the reported `size` is at least that large ([vktTensorCreateRequirements.cpp#L174-L196](../../../modules/vulkan/tensor/vktTensorCreateRequirements.cpp#L174-L196)):
   - **Packed (no custom strides)**: `expectedSize = product(dimensions) * getFormatSize(format)` ([vktTensorCreateRequirements.cpp#L177-L181](../../../modules/vulkan/tensor/vktTensorCreateRequirements.cpp#L177-L181)).
   - **Non-packed (with custom strides)**: `expectedSize = strides[0] * dimensions[0]` ([vktTensorCreateRequirements.cpp#L184-L186](../../../modules/vulkan/tensor/vktTensorCreateRequirements.cpp#L184-L186)).
   - If `expectedSize > reported size`, the test fails with a diagnostic message ([vktTensorCreateRequirements.cpp#L189-L195](../../../modules/vulkan/tensor/vktTensorCreateRequirements.cpp#L189-L195)).

5. **No size assertion for optimal tiling**: For `VK_TENSOR_TILING_OPTIMAL_ARM`, no size check is performed because the implementation may use opaque layouts that exceed the raw data size ([vktTensorCreateRequirements.cpp#L173-L174](../../../modules/vulkan/tensor/vktTensorCreateRequirements.cpp#L173-L174)).

## Test principles

The test validates that the Vulkan driver correctly implements the tensor memory requirements query for the `VK_ARM_tensors` extension. The core principle is:

- **Creation succeeds**: Tensor objects can be created at the device's advertised maximum limits for element count, dimension count, per-dimension size, and (for linear tiling) stride values.
- **Memory requirements are sane**: The `vkGetTensorMemoryRequirementsARM` query returns at least one valid memory type and a size that is not smaller than the minimum required to store the tensor data (for linear tiling, where the layout is well-defined).
- **Boundary coverage**: By generating tensor configurations at the device's reported maximum limits, the test ensures that the implementation handles the full range of valid tensor parameters, not just small or trivial sizes.

## Notes/uncertainties

- The test does not verify that the reported memory size is *exactly* the expected size for linear tiling; it only checks that the reported size is *at least* the expected size. Implementations may report larger sizes due to alignment requirements ([vktTensorCreateRequirements.cpp#L189](../../../modules/vulkan/tensor/vktTensorCreateRequirements.cpp#L189)).
- For optimal tiling, no size validation is performed because the internal layout is implementation-defined. The test only verifies that the memory type bits are non-zero ([vktTensorCreateRequirements.cpp#L173-L174](../../../modules/vulkan/tensor/vktTensorCreateRequirements.cpp#L173-L174)).
- The maximum stride used for non-packed tensors is clamped to a minimum of 65536 (observed at [vktTensorCreateRequirements.cpp#L92](../../../modules/vulkan/tensor/vktTensorCreateRequirements.cpp#L92)) to avoid nonsensical stride values even if the implementation reports a very small `maxTensorStride`.
- The test does not allocate memory or bind it to the tensor; it only queries memory requirements. Memory allocation and binding correctness is tested elsewhere.
