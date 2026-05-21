# vktTensorArrayAccess

## Overview

This test file validates tensor shader **array access** operations via the `GL_ARM_tensors` GLSL extension. It exercises the `tensorReadARM` and `tensorWriteARM` built-in functions with array-sized access (reading or writing multiple consecutive elements of the innermost dimension in a single call), across multiple formats, tilings, and array sizes.

## Role of file

`vktTensorArrayAccess.cpp` registers the `"array_access"` subgroup under the `dEQP-VK.tensor` parent group. It defines two pairs of test class templates (one for linear tiling, one for optimal tiling) that create a tensor and a storage buffer, then dispatch a compute shader performing array-sized tensor reads or writes, and finally verifies the results by comparing tensor data against buffer data element-by-element.

## Source code

- Test file: [vktTensorArrayAccess.cpp](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp)
- Shader generator: [vktTensorArrayAccessShaders.cpp](../../../modules/vulkan/tensor/shaders/vktTensorArrayAccessShaders.cpp)
- Shared utilities: [vktTensorTestsUtil.hpp](../../../modules/vulkan/tensor/vktTensorTestsUtil.hpp), [vktTensorTestsUtil.cpp](../../../modules/vulkan/tensor/vktTensorTestsUtil.cpp)

## Registration Hierarchy

```text
tensor.array_access
├── r16_sint_linear_shape_13_17_19_23_array_read_array_size_2
├── r16_sint_linear_shape_13_17_19_23_array_read_array_size_3
├── r16_sint_linear_shape_13_17_19_23_array_read_array_size_4
├── r16_sint_linear_shape_13_17_19_23_array_read_array_size_max
├── r16_sint_linear_shape_13_17_19_23_array_write_array_size_2
├── r16_sint_linear_shape_13_17_19_23_array_write_array_size_3
├── r16_sint_linear_shape_13_17_19_23_array_write_array_size_4
├── r16_sint_linear_shape_13_17_19_23_array_write_array_size_max
├── r16_sint_optimal_shape_13_17_19_23_array_read_array_size_2
├── r16_sint_optimal_shape_13_17_19_23_array_read_array_size_3
├── r16_sint_optimal_shape_13_17_19_23_array_read_array_size_4
├── r16_sint_optimal_shape_13_17_19_23_array_read_array_size_max
├── r16_sint_optimal_shape_13_17_19_23_array_write_array_size_2
├── r16_sint_optimal_shape_13_17_19_23_array_write_array_size_3
├── r16_sint_optimal_shape_13_17_19_23_array_write_array_size_4
├── r16_sint_optimal_shape_13_17_19_23_array_write_array_size_max
├── r16_uint_linear_shape_13_17_19_23_array_read_array_size_2
├── r16_uint_linear_shape_13_17_19_23_array_read_array_size_3
├── r16_uint_linear_shape_13_17_19_23_array_read_array_size_4
├── r16_uint_linear_shape_13_17_19_23_array_read_array_size_max
├── r16_uint_linear_shape_13_17_19_23_array_write_array_size_2
├── r16_uint_linear_shape_13_17_19_23_array_write_array_size_3
├── r16_uint_linear_shape_13_17_19_23_array_write_array_size_4
├── r16_uint_linear_shape_13_17_19_23_array_write_array_size_max
├── r16_uint_optimal_shape_13_17_19_23_array_read_array_size_2
├── r16_uint_optimal_shape_13_17_19_23_array_read_array_size_3
├── r16_uint_optimal_shape_13_17_19_23_array_read_array_size_4
├── r16_uint_optimal_shape_13_17_19_23_array_read_array_size_max
├── r16_uint_optimal_shape_13_17_19_23_array_write_array_size_2
├── r16_uint_optimal_shape_13_17_19_23_array_write_array_size_3
├── r16_uint_optimal_shape_13_17_19_23_array_write_array_size_4
├── r16_uint_optimal_shape_13_17_19_23_array_write_array_size_max
├── r32_sint_linear_shape_13_17_19_23_array_read_array_size_2
├── r32_sint_linear_shape_13_17_19_23_array_read_array_size_3
├── r32_sint_linear_shape_13_17_19_23_array_read_array_size_4
├── r32_sint_linear_shape_13_17_19_23_array_read_array_size_max
├── r32_sint_linear_shape_13_17_19_23_array_write_array_size_2
├── r32_sint_linear_shape_13_17_19_23_array_write_array_size_3
├── r32_sint_linear_shape_13_17_19_23_array_write_array_size_4
├── r32_sint_linear_shape_13_17_19_23_array_write_array_size_max
├── r32_sint_optimal_shape_13_17_19_23_array_read_array_size_2
├── r32_sint_optimal_shape_13_17_19_23_array_read_array_size_3
├── r32_sint_optimal_shape_13_17_19_23_array_read_array_size_4
├── r32_sint_optimal_shape_13_17_19_23_array_read_array_size_max
├── r32_sint_optimal_shape_13_17_19_23_array_write_array_size_2
├── r32_sint_optimal_shape_13_17_19_23_array_write_array_size_3
├── r32_sint_optimal_shape_13_17_19_23_array_write_array_size_4
├── r32_sint_optimal_shape_13_17_19_23_array_write_array_size_max
├── r32_uint_linear_shape_13_17_19_23_array_read_array_size_2
├── r32_uint_linear_shape_13_17_19_23_array_read_array_size_3
├── r32_uint_linear_shape_13_17_19_23_array_read_array_size_4
├── r32_uint_linear_shape_13_17_19_23_array_read_array_size_max
├── r32_uint_linear_shape_13_17_19_23_array_write_array_size_2
├── r32_uint_linear_shape_13_17_19_23_array_write_array_size_3
├── r32_uint_linear_shape_13_17_19_23_array_write_array_size_4
├── r32_uint_linear_shape_13_17_19_23_array_write_array_size_max
├── r32_uint_optimal_shape_13_17_19_23_array_read_array_size_2
├── r32_uint_optimal_shape_13_17_19_23_array_read_array_size_3
├── r32_uint_optimal_shape_13_17_19_23_array_read_array_size_4
├── r32_uint_optimal_shape_13_17_19_23_array_read_array_size_max
├── r32_uint_optimal_shape_13_17_19_23_array_write_array_size_2
├── r32_uint_optimal_shape_13_17_19_23_array_write_array_size_3
├── r32_uint_optimal_shape_13_17_19_23_array_write_array_size_4
├── r32_uint_optimal_shape_13_17_19_23_array_write_array_size_max
├── r64_sint_linear_shape_13_17_19_23_array_read_array_size_2
├── r64_sint_linear_shape_13_17_19_23_array_read_array_size_3
├── r64_sint_linear_shape_13_17_19_23_array_read_array_size_4
├── r64_sint_linear_shape_13_17_19_23_array_read_array_size_max
├── r64_sint_linear_shape_13_17_19_23_array_write_array_size_2
├── r64_sint_linear_shape_13_17_19_23_array_write_array_size_3
├── r64_sint_linear_shape_13_17_19_23_array_write_array_size_4
├── r64_sint_linear_shape_13_17_19_23_array_write_array_size_max
├── r64_sint_optimal_shape_13_17_19_23_array_read_array_size_2
├── r64_sint_optimal_shape_13_17_19_23_array_read_array_size_3
├── r64_sint_optimal_shape_13_17_19_23_array_read_array_size_4
├── r64_sint_optimal_shape_13_17_19_23_array_read_array_size_max
├── r64_sint_optimal_shape_13_17_19_23_array_write_array_size_2
├── r64_sint_optimal_shape_13_17_19_23_array_write_array_size_3
├── r64_sint_optimal_shape_13_17_19_23_array_write_array_size_4
├── r64_sint_optimal_shape_13_17_19_23_array_write_array_size_max
├── r64_uint_linear_shape_13_17_19_23_array_read_array_size_2
├── r64_uint_linear_shape_13_17_19_23_array_read_array_size_3
├── r64_uint_linear_shape_13_17_19_23_array_read_array_size_4
├── r64_uint_linear_shape_13_17_19_23_array_read_array_size_max
├── r64_uint_linear_shape_13_17_19_23_array_write_array_size_2
├── r64_uint_linear_shape_13_17_19_23_array_write_array_size_3
├── r64_uint_linear_shape_13_17_19_23_array_write_array_size_4
├── r64_uint_linear_shape_13_17_19_23_array_write_array_size_max
├── r64_uint_optimal_shape_13_17_19_23_array_read_array_size_2
├── r64_uint_optimal_shape_13_17_19_23_array_read_array_size_3
├── r64_uint_optimal_shape_13_17_19_23_array_read_array_size_4
├── r64_uint_optimal_shape_13_17_19_23_array_read_array_size_max
├── r64_uint_optimal_shape_13_17_19_23_array_write_array_size_2
├── r64_uint_optimal_shape_13_17_19_23_array_write_array_size_3
├── r64_uint_optimal_shape_13_17_19_23_array_write_array_size_4
├── r64_uint_optimal_shape_13_17_19_23_array_write_array_size_max
├── r8_sint_linear_shape_13_17_19_23_array_read_array_size_2
├── r8_sint_linear_shape_13_17_19_23_array_read_array_size_3
├── r8_sint_linear_shape_13_17_19_23_array_read_array_size_4
├── r8_sint_linear_shape_13_17_19_23_array_read_array_size_max
├── r8_sint_linear_shape_13_17_19_23_array_write_array_size_2
├── r8_sint_linear_shape_13_17_19_23_array_write_array_size_3
├── r8_sint_linear_shape_13_17_19_23_array_write_array_size_4
├── r8_sint_linear_shape_13_17_19_23_array_write_array_size_max
├── r8_sint_optimal_shape_13_17_19_23_array_read_array_size_2
├── r8_sint_optimal_shape_13_17_19_23_array_read_array_size_3
├── r8_sint_optimal_shape_13_17_19_23_array_read_array_size_4
├── r8_sint_optimal_shape_13_17_19_23_array_read_array_size_max
├── r8_sint_optimal_shape_13_17_19_23_array_write_array_size_2
├── r8_sint_optimal_shape_13_17_19_23_array_write_array_size_3
├── r8_sint_optimal_shape_13_17_19_23_array_write_array_size_4
├── r8_sint_optimal_shape_13_17_19_23_array_write_array_size_max
├── r8_uint_linear_shape_13_17_19_23_array_read_array_size_2
├── r8_uint_linear_shape_13_17_19_23_array_read_array_size_3
├── r8_uint_linear_shape_13_17_19_23_array_read_array_size_4
├── r8_uint_linear_shape_13_17_19_23_array_read_array_size_max
├── r8_uint_linear_shape_13_17_19_23_array_write_array_size_2
├── r8_uint_linear_shape_13_17_19_23_array_write_array_size_3
├── r8_uint_linear_shape_13_17_19_23_array_write_array_size_4
├── r8_uint_linear_shape_13_17_19_23_array_write_array_size_max
├── r8_uint_optimal_shape_13_17_19_23_array_read_array_size_2
├── r8_uint_optimal_shape_13_17_19_23_array_read_array_size_3
├── r8_uint_optimal_shape_13_17_19_23_array_read_array_size_4
├── r8_uint_optimal_shape_13_17_19_23_array_read_array_size_max
├── r8_uint_optimal_shape_13_17_19_23_array_write_array_size_2
├── r8_uint_optimal_shape_13_17_19_23_array_write_array_size_3
├── r8_uint_optimal_shape_13_17_19_23_array_write_array_size_4
└── r8_uint_optimal_shape_13_17_19_23_array_write_array_size_max
```

Total: 128 tests (8 formats x 2 tilings x 4 array sizes x 2 access variants).

## Test Families

### array_access

The sole test family registered by this file. The factory function `createArrayAccessTests` creates the group at [vktTensorArrayAccess.cpp#L767-L778](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L767-L778). It invokes the template function `addTensorArrayTests<T>` four times with types `uint64_t`, `uint32_t`, `uint16_t`, and `uint8_t` at [vktTensorArrayAccess.cpp#L772-L775](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L772-L775). Each instantiation iterates over the formats returned by `getTestFormats<T>()` and creates test cases for both linear and optimal tiling with all array sizes.

The test name is constructed by `paramsToString(params, variant) + "_array_size_" + (arraySize == 0 ? "max" : de::toString(arraySize))` at [vktTensorArrayAccess.cpp#L112-L113](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L112-L113) (linear) and [vktTensorArrayAccess.cpp#L234-L235](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L234-L235) (optimal), which expands to the pattern `{format}_{tiling}_shape_{dims}_{access_variant}_array_size_{N|max}`.

## Parameter dimensions

| Dimension | Values | Source |
|-----------|--------|--------|
| Format | `r8_uint`, `r8_sint`, `r16_uint`, `r16_sint`, `r32_uint`, `r32_sint`, `r64_uint`, `r64_sint` | [vktTensorTestsUtil.cpp#L116-L157](../../../modules/vulkan/tensor/vktTensorTestsUtil.cpp#L116-L157) |
| Tiling | `linear`, `optimal` | [vktTensorArrayAccess.cpp#L723](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L723), [vktTensorArrayAccess.cpp#L732](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L732) |
| Shape | `{13, 17, 19, 23}` (rank 4) | [vktTensorArrayAccess.cpp#L715](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L715) |
| Strides | `{}` (empty, implying packed/implicit strides) | [vktTensorArrayAccess.cpp#L723](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L723), [vktTensorArrayAccess.cpp#L732](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L732) |
| Array size | `2`, `3`, `4`, `0` (0 resolves to implementation max at runtime) | [vktTensorArrayAccess.cpp#L719](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L719), [vktTensorArrayAccess.cpp#L742](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L742) |
| Access variant | `ARRAY_READ`, `ARRAY_WRITE` | [vktTensorArrayAccess.cpp#L725-L727](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L725-L727), [vktTensorArrayAccess.cpp#L733-L736](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L733-L736) |

The total element count for shape `{13, 17, 19, 23}` is 13 x 17 x 19 x 23 = 96,577 elements.

## Support/feature requirements

All test cases share a common `checkSupport` method. The linear tiling variant is at [vktTensorArrayAccess.cpp#L134-L168](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L134-L168); the optimal tiling variant is at [vktTensorArrayAccess.cpp#L256-L297](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L256-L297). The checks are:

1. **Extension**: `VK_ARM_tensors` must be supported ([vktTensorArrayAccess.cpp#L136](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L136), [vktTensorArrayAccess.cpp#L258](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L258)).
2. **Dimension count**: Tensor rank (4) must not exceed `maxTensorDimensionCount` from `VkPhysicalDeviceTensorPropertiesARM` ([vktTensorArrayAccess.cpp#L140-L143](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L140-L143), [vktTensorArrayAccess.cpp#L262-L265](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L262-L265)).
3. **Shader tensor access**: `deviceSupportsShaderTensorAccess()` must return true ([vktTensorArrayAccess.cpp#L145-L148](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L145-L148), [vktTensorArrayAccess.cpp#L267-L270](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L267-L270)).
4. **Compute stage access**: `deviceSupportsShaderStagesTensorAccess(context, VK_SHADER_STAGE_COMPUTE_BIT)` must return true ([vktTensorArrayAccess.cpp#L149-L152](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L149-L152), [vktTensorArrayAccess.cpp#L272-L275](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L272-L275)).
5. **Format/tiling flags**: `formatSupportTensorFlags(context, format, tiling, VK_FORMAT_FEATURE_2_TENSOR_SHADER_BIT_ARM)` must return true ([vktTensorArrayAccess.cpp#L153-L157](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L153-L157), [vktTensorArrayAccess.cpp#L277-L281](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L277-L281)).
6. **Array length**: `m_arraySize` must not exceed `maxTensorShaderAccessArrayLength` ([vktTensorArrayAccess.cpp#L159-L162](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L159-L162), [vktTensorArrayAccess.cpp#L288-L291](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L288-L291)).
7. **Access size**: `m_arraySize * getFormatSize(format)` must not exceed `maxTensorShaderAccessSize` ([vktTensorArrayAccess.cpp#L164-L167](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L164-L167), [vktTensorArrayAccess.cpp#L293-L296](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L293-L296)).
8. **Non-packed tensors** (optimal tiling only): If the tensor is not packed, `deviceSupportsNonPackedTensors()` must return true ([vktTensorArrayAccess.cpp#L283-L286](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L283-L286)). This check is absent in the linear tiling variant because linear tensors with empty strides are implicitly packed.

The `array_size_max` tests pass `0` as the array size at registration time ([vktTensorArrayAccess.cpp#L742](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L742)). The actual max array size is resolved at runtime by `calculateMaxArraySizeSupported()` at [vktTensorArrayAccess.cpp#L68-L77](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L68-L77), which computes `min(maxTensorShaderAccessSize / elementSize, maxTensorShaderAccessArrayLength)`.

## Verification methods

Both linear and optimal tiling test instances use the same verification strategy:

1. **Element-by-element comparison**: After the compute shader executes, the test compares every tensor element against the corresponding buffer element. If any mismatch is found, the test fails with a message identifying the index and both values ([vktTensorArrayAccess.cpp#L482-L492](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L482-L492) for linear, [vktTensorArrayAccess.cpp#L696-L705](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L696-L705) for optimal).

2. **ARRAY_READ variant**: The tensor is pre-filled with known data via `StridedMemoryUtils::fill()` and uploaded. The buffer is cleared. The shader reads from the tensor using `tensorReadARM` with an array and writes to the buffer. Verification confirms the buffer matches the original tensor data ([vktTensorArrayAccess.cpp#L365-L372](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L365-L372)).

3. **ARRAY_WRITE variant**: The buffer is pre-filled with known data. The tensor is cleared. The shader reads from the buffer and writes to the tensor using `tensorWriteARM` with an array. The tensor is then downloaded and compared against the buffer data ([vktTensorArrayAccess.cpp#L374-L378](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L374-L378)).

## Test principles

The tests validate that the `tensorReadARM` and `tensorWriteARM` GLSL built-in functions correctly handle array-sized access to tensor elements along the innermost dimension. The core principle is:

- A rank-4 tensor of shape `{13, 17, 19, 23}` is created with a specific format and tiling.
- A compute shader is dispatched with workgroups sized to cover the entire tensor. The dispatch dimensions are `(ceil(23 / arraySize), 13*17*19, 1)`, where `23` is the innermost dimension and `arraySize` is the number of consecutive elements accessed per invocation ([vktTensorArrayAccess.cpp#L430-L435](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L430-L435)).
- Each shader invocation computes coordinates for the outer dimensions from `gl_GlobalInvocationID.y` and for the innermost dimension from `gl_GlobalInvocationID.x * arraySize` ([vktTensorArrayAccessShaders.cpp#L64-L78](../../../modules/vulkan/tensor/shaders/vktTensorArrayAccessShaders.cpp#L64-L78)).
- The shader declares a local array `tmp[arraySize]` and calls either `tensorReadARM(tens, coords, tmp)` or `tensorWriteARM(tens, coords, tmp)` ([vktTensorArrayAccessShaders.cpp#L82-L113](../../../modules/vulkan/tensor/shaders/vktTensorArrayAccessShaders.cpp#L82-L113)).
- Boundary clamping is applied in the shader: the loop `for (int i = 0; (i < arraySize) && (coord + i < size); ++i)` ensures that out-of-bounds elements at the end of the innermost dimension are not read or written ([vktTensorArrayAccessShaders.cpp#L92-L96](../../../modules/vulkan/tensor/shaders/vktTensorArrayAccessShaders.cpp#L92-L96), [vktTensorArrayAccessShaders.cpp#L99-L103](../../../modules/vulkan/tensor/shaders/vktTensorArrayAccessShaders.cpp#L99-L103)).

For **optimal tiling**, an additional staging linear tensor is used for data upload/download via `cmdCopyTensorARM`, since optimal tensors are not host-visible. The optimal tensor is initialized by copying from the staging linear tensor before the compute dispatch ([vktTensorArrayAccess.cpp#L616-L638](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L616-L638)), and after the write variant, the result is copied back to the staging tensor for readback ([vktTensorArrayAccess.cpp#L655-L676](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L655-L676)).

The `array_size_max` tests use `arraySize = 0` at registration, which resolves to the implementation's maximum supported array access size at runtime via `calculateMaxArraySizeSupported()` ([vktTensorArrayAccess.cpp#L68-L77](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L68-L77)). This function computes `min(maxTensorShaderAccessSize / elementSize, maxTensorShaderAccessArrayLength)`, ensuring the test stays within the device's reported limits.

## Notes/uncertainties

- The shape `{13, 17, 19, 23}` is a fixed prime-based shape chosen to exercise non-power-of-two dimensions, observed in the inspected file at [vktTensorArrayAccess.cpp#L715](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L715). The rationale for these specific primes is not documented in the source.
- The `array_size_max` tests cannot generate shader source at build time because the max array size depends on the physical device. The `initPrograms` method handles this by returning early if no physical device is available via the `ContextManager` ([vktTensorArrayAccess.cpp#L174-L188](../../../modules/vulkan/tensor/vktTensorArrayAccess.cpp#L174-L188)), deferring shader generation until a device context is available.
- The `TensorArrayReadWriteTestCase` (linear) and `OptimalTensorArrayReadWriteTestCase` (optimal) are nearly identical in structure, with the key difference being that the optimal variant adds a non-packed tensor support check in `checkSupport` and uses a staging linear tensor for data transfer in `iterate`.
- The `AccessVariant` enum values `ARRAY_READ` and `ARRAY_WRITE` map to the test name suffixes `array_read` and `array_write` respectively, as defined in the `operator<<` overload at [vktTensorTestsUtil.cpp#L272-L294](../../../modules/vulkan/tensor/vktTensorTestsUtil.cpp#L272-L294).
