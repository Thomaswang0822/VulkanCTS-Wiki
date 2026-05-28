# tensor.dimension_query

## Overview

Tests that verify the correctness of querying tensor dimension sizes from within a compute shader using the `tensorSizeARM()` built-in function provided by the `GL_ARM_tensors` GLSL extension. Each test creates a tensor with a specific format, tiling, and shape, dispatches a compute shader that writes each dimension size to a storage buffer, and then validates on the host that the returned values match the expected dimensions.

## Role of file

[vktTensorDimensionQuery.cpp](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp) defines the `dimension_query` subgroup under `dEQP-VK.tensor`. It registers the factory function `createDimensionQueryTests` ([vktTensorDimensionQuery.cpp#L293-L301](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp#L293-L301)), which creates a `tcu::TestCaseGroup` named `"dimension_query"` and populates it with 80 test cases via `addDimensionQueriesTestCases` ([vktTensorDimensionQuery.cpp#L275-L289](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp#L275-L289)).

Two key classes are defined:

- **`TensorDimensionQueriesTestCase`** ([vktTensorDimensionQuery.cpp#L221-L273](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp#L221-L273)): The `TestCase` subclass responsible for support checking (`checkSupport`), shader program generation (`initPrograms`), and test instance creation (`createInstance`).
- **`TensorDimensionsQueriesTestInstance`** ([vktTensorDimensionQuery.cpp#L67-L90](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp#L67-L90)): The `TestInstance` subclass that performs the actual GPU execution and result validation in its `iterate()` method ([vktTensorDimensionQuery.cpp#L92-L219](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp#L92-L219)).

## Source code link

[vktTensorDimensionQuery.cpp](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp)

Supporting files:
- [vktTensorTestsUtil.hpp](../../../modules/vulkan/tensor/vktTensorTestsUtil.hpp) / [vktTensorTestsUtil.cpp](../../../modules/vulkan/tensor/vktTensorTestsUtil.cpp): shared tensor test utilities (`TensorParameters`, `getAllTestFormats`, `paramsToString`, support-query helpers)
- [vktTensorQueryDimensionsShaders.cpp](../../../modules/vulkan/tensor/shaders/vktTensorQueryDimensionsShaders.cpp): shader generation function `genShaderQueryDimensions`

## Registration Hierarchy

```text
tensor.dimension_query
├── r8_uint_linear_shape_1
├── r8_uint_linear_shape_2_1
├── r8_uint_linear_shape_4_2_1
├── r8_uint_linear_shape_8_4_2_1
├── r8_uint_linear_shape_4_8_16_2_1
├── r8_uint_optimal_shape_1
├── r8_uint_optimal_shape_2_1
├── r8_uint_optimal_shape_4_2_1
├── r8_uint_optimal_shape_8_4_2_1
├── r8_uint_optimal_shape_4_8_16_2_1
├── r8_sint_linear_shape_1
├── r8_sint_linear_shape_2_1
├── r8_sint_linear_shape_4_2_1
├── r8_sint_linear_shape_8_4_2_1
├── r8_sint_linear_shape_4_8_16_2_1
├── r8_sint_optimal_shape_1
├── r8_sint_optimal_shape_2_1
├── r8_sint_optimal_shape_4_2_1
├── r8_sint_optimal_shape_8_4_2_1
├── r8_sint_optimal_shape_4_8_16_2_1
├── r16_uint_linear_shape_1
├── r16_uint_linear_shape_2_1
├── r16_uint_linear_shape_4_2_1
├── r16_uint_linear_shape_8_4_2_1
├── r16_uint_linear_shape_4_8_16_2_1
├── r16_uint_optimal_shape_1
├── r16_uint_optimal_shape_2_1
├── r16_uint_optimal_shape_4_2_1
├── r16_uint_optimal_shape_8_4_2_1
├── r16_uint_optimal_shape_4_8_16_2_1
├── r16_sint_linear_shape_1
├── r16_sint_linear_shape_2_1
├── r16_sint_linear_shape_4_2_1
├── r16_sint_linear_shape_8_4_2_1
├── r16_sint_linear_shape_4_8_16_2_1
├── r16_sint_optimal_shape_1
├── r16_sint_optimal_shape_2_1
├── r16_sint_optimal_shape_4_2_1
├── r16_sint_optimal_shape_8_4_2_1
├── r16_sint_optimal_shape_4_8_16_2_1
├── r32_uint_linear_shape_1
├── r32_uint_linear_shape_2_1
├── r32_uint_linear_shape_4_2_1
├── r32_uint_linear_shape_8_4_2_1
├── r32_uint_linear_shape_4_8_16_2_1
├── r32_uint_optimal_shape_1
├── r32_uint_optimal_shape_2_1
├── r32_uint_optimal_shape_4_2_1
├── r32_uint_optimal_shape_8_4_2_1
├── r32_uint_optimal_shape_4_8_16_2_1
├── r32_sint_linear_shape_1
├── r32_sint_linear_shape_2_1
├── r32_sint_linear_shape_4_2_1
├── r32_sint_linear_shape_8_4_2_1
├── r32_sint_linear_shape_4_8_16_2_1
├── r32_sint_optimal_shape_1
├── r32_sint_optimal_shape_2_1
├── r32_sint_optimal_shape_4_2_1
├── r32_sint_optimal_shape_8_4_2_1
├── r32_sint_optimal_shape_4_8_16_2_1
├── r64_uint_linear_shape_1
├── r64_uint_linear_shape_2_1
├── r64_uint_linear_shape_4_2_1
├── r64_uint_linear_shape_8_4_2_1
├── r64_uint_linear_shape_4_8_16_2_1
├── r64_uint_optimal_shape_1
├── r64_uint_optimal_shape_2_1
├── r64_uint_optimal_shape_4_2_1
├── r64_uint_optimal_shape_8_4_2_1
├── r64_uint_optimal_shape_4_8_16_2_1
├── r64_sint_linear_shape_1
├── r64_sint_linear_shape_2_1
├── r64_sint_linear_shape_4_2_1
├── r64_sint_linear_shape_8_4_2_1
├── r64_sint_linear_shape_4_8_16_2_1
├── r64_sint_optimal_shape_1
├── r64_sint_optimal_shape_2_1
├── r64_sint_optimal_shape_4_2_1
├── r64_sint_optimal_shape_8_4_2_1
└── r64_sint_optimal_shape_4_8_16_2_1
```

## Test Families

### dimension_query

The sole test family in this file. It validates that the `tensorSizeARM()` GLSL built-in correctly reports each dimension of a tensor object when queried from a compute shader.

Each test case is a `TensorDimensionQueriesTestCase` ([vktTensorDimensionQuery.cpp#L221-L273](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp#L221-L273)) parameterized by:

- **Format** (`VkFormat`): one of 8 integer formats from `getAllTestFormats()` ([vktTensorTestsUtil.cpp#L48-L56](../../../modules/vulkan/tensor/vktTensorTestsUtil.cpp#L48-L56))
- **Tiling** (`VkTensorTilingARM`): `VK_TENSOR_TILING_LINEAR_ARM` or `VK_TENSOR_TILING_OPTIMAL_ARM`
- **Dimensions** (`TensorDimensions`): one of 5 shapes ([vktTensorDimensionQuery.cpp#L278](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp#L278))

The test case name is generated by `paramsToString(TensorParameters{format, tiling, dimension, {}})` ([vktTensorDimensionQuery.cpp#L226](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp#L226)), which produces names in the pattern `{format}_{tiling}_shape_{dims}` ([vktTensorTestsUtil.cpp#L232-L249](../../../modules/vulkan/tensor/vktTensorTestsUtil.cpp#L232-L249)).

## Parameter dimensions

The five tensor shapes used across all tests are defined at [vktTensorDimensionQuery.cpp#L278](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp#L278):

| Shape name in test path | TensorDimensions value | Rank | Total elements |
|-------------------------|------------------------|------|----------------|
| `1`                     | `{1}`                  | 1    | 1              |
| `2_1`                   | `{2, 1}`               | 2    | 2              |
| `4_2_1`                 | `{4, 2, 1}`            | 3    | 8              |
| `8_4_2_1`               | `{8, 4, 2, 1}`         | 4    | 64             |
| `4_8_16_2_1`            | `{4, 8, 16, 2, 1}`     | 5    | 1024           |

The 8 formats are ([vktTensorTestsUtil.cpp#L50-L53](../../../modules/vulkan/tensor/vktTensorTestsUtil.cpp#L50-L53)):

| Short name   | VkFormat              | Element size |
|-------------|------------------------|-------------|
| `r8_uint`   | `VK_FORMAT_R8_UINT`    | 1 byte      |
| `r8_sint`   | `VK_FORMAT_R8_SINT`    | 1 byte      |
| `r16_uint`  | `VK_FORMAT_R16_UINT`   | 2 bytes     |
| `r16_sint`  | `VK_FORMAT_R16_SINT`   | 2 bytes     |
| `r32_uint`  | `VK_FORMAT_R32_UINT`   | 4 bytes     |
| `r32_sint`  | `VK_FORMAT_R32_SINT`   | 4 bytes     |
| `r64_uint`  | `VK_FORMAT_R64_UINT`   | 8 bytes     |
| `r64_sint`  | `VK_FORMAT_R64_SINT`   | 8 bytes     |

Total: 8 formats x 2 tilings x 5 shapes = **80 test cases**.

## Support / Feature Requirements

The `checkSupport` method ([vktTensorDimensionQuery.cpp#L238-L261](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp#L238-L261)) performs five checks, each throwing `NotSupportedError` if the condition is not met:

1. **Extension availability**: `context.requireDeviceFunctionality("VK_ARM_tensors")` ([vktTensorDimensionQuery.cpp#L240](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp#L240)) -- the device must support the `VK_ARM_tensors` extension.

2. **Max dimension count**: The tensor's rank (number of dimensions) must not exceed `maxTensorDimensionCount` from `VkPhysicalDeviceTensorPropertiesARM` ([vktTensorDimensionQuery.cpp#L242-L245](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp#L242-L245)). This is queried via `getTensorPhysicalDeviceProperties()` ([vktTensorTestsUtil.cpp#L70-L73](../../../modules/vulkan/tensor/vktTensorTestsUtil.cpp#L70-L73)). Tests with rank 5 (shape `4_8_16_2_1`) may be skipped on implementations that report `maxTensorDimensionCount < 5`.

3. **Shader tensor access feature**: The `shaderTensorAccess` feature of `VkPhysicalDeviceTensorFeaturesARM` must be enabled ([vktTensorDimensionQuery.cpp#L247-L250](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp#L247-L250)), checked via `deviceSupportsShaderTensorAccess()` ([vktTensorTestsUtil.cpp#L382-L397](../../../modules/vulkan/tensor/vktTensorTestsUtil.cpp#L382-L397)).

4. **Compute shader stage support**: The `shaderTensorSupportedStages` property must include `VK_SHADER_STAGE_COMPUTE_BIT` ([vktTensorDimensionQuery.cpp#L252-L255](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp#L252-L255)), checked via `deviceSupportsShaderStagesTensorAccess()` ([vktTensorTestsUtil.cpp#L399-L412](../../../modules/vulkan/tensor/vktTensorTestsUtil.cpp#L399-L412)).

5. **Format-tiling compatibility**: The combination of format and tiling must support `VK_FORMAT_FEATURE_2_TENSOR_SHADER_BIT_ARM` ([vktTensorDimensionQuery.cpp#L257-L260](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp#L257-L260)), checked via `formatSupportTensorFlags()` ([vktTensorTestsUtil.cpp#L341-L363](../../../modules/vulkan/tensor/vktTensorTestsUtil.cpp#L341-L363)).

## Verification methods

Verification is performed on the host in `TensorDimensionsQueriesTestInstance::iterate()` ([vktTensorDimensionQuery.cpp#L92-L219](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp#L92-L219)):

1. A tensor is created with the test's format, tiling, dimensions, and usage `VK_TENSOR_USAGE_SHADER_BIT_ARM` ([vktTensorDimensionQuery.cpp#L102-L106](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp#L102-L106)).
2. A storage buffer of `rank * sizeof(uint32_t)` bytes is allocated and zeroed ([vktTensorDimensionQuery.cpp#L110-L123](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp#L110-L123)).
3. A compute shader is dispatched that calls `tensorSizeARM(tens, i)` for each dimension index `i` and writes the result to `data[i]` in the storage buffer ([vktTensorQueryDimensionsShaders.cpp#L57-L59](../../../modules/vulkan/tensor/shaders/vktTensorQueryDimensionsShaders.cpp#L57-L59)).
4. After a pipeline barrier and command buffer completion, the host reads back the buffer ([vktTensorDimensionQuery.cpp#L198-L216](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp#L198-L216)).
5. Each buffer element at index `element_idx` is compared against `m_dimensions[element_idx]`. A mismatch produces a `TestStatus::fail` with a diagnostic message; all matching produces `TestStatus::pass` ([vktTensorDimensionQuery.cpp#L204-L218](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp#L204-L218)).

## Test principles

The test validates the `tensorSizeARM()` GLSL built-in function from the `GL_ARM_tensors` extension. The principle is:

1. **Setup**: Create a tensor with known dimensions and a storage buffer of sufficient size.
2. **Shader execution**: A compute shader declares a `tensorARM<format, rank>` uniform and, for each dimension index `i` from 0 to `rank - 1`, calls `tensorSizeARM(tens, i)` and stores the result into a storage buffer at index `i`.
3. **Host validation**: After GPU execution, the host reads back the storage buffer and compares each value against the expected dimension size that was used to create the tensor.

The shader is generated by `genShaderQueryDimensions(rank, format)` ([vktTensorQueryDimensionsShaders.cpp#L40-L65](../../../modules/vulkan/tensor/shaders/vktTensorQueryDimensionsShaders.cpp#L40-L65)), which emits GLSL 450 with the `GL_ARM_tensors` and `GL_EXT_shader_explicit_arithmetic_types` extensions, declares the tensor and buffer bindings, and loops over dimension indices.

For linear tiling, strides are computed via `getTensorStrides()` ([vktTensorDimensionQuery.cpp#L79](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp#L79)); for optimal tiling, strides are left as the default empty value.

## Notes/uncertainties

- The test only covers integer formats (uint/sint at 8/16/32/64-bit widths). Floating-point and normalized formats are not tested for dimension queries, observed in the format list at [vktTensorTestsUtil.cpp#L50-L53](../../../modules/vulkan/tensor/vktTensorTestsUtil.cpp#L50-L53).
- The dimension query result is always written as `uint32_t` to the storage buffer regardless of the tensor's element format, since `tensorSizeARM()` returns the dimension extent (not a tensor element value). This is consistent with the shader code at [vktTensorQueryDimensionsShaders.cpp#L59](../../../modules/vulkan/tensor/shaders/vktTensorQueryDimensionsShaders.cpp#L59).
- Tests with 5-dimensional tensors (shape `4_8_16_2_1`) may be skipped on implementations with `maxTensorDimensionCount < 5`, as enforced by the support check at [vktTensorDimensionQuery.cpp#L242-L245](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp#L242-L245).
- The compute shader uses a single invocation (`local_size_x = 1, local_size_y = 1, local_size_z = 1`) since dimension queries do not require parallelism ([vktTensorQueryDimensionsShaders.cpp#L49](../../../modules/vulkan/tensor/shaders/vktTensorQueryDimensionsShaders.cpp#L49)).
- The `GL_EXT_shader_explicit_arithmetic_types` extension is required in the shader ([vktTensorQueryDimensionsShaders.cpp#L46](../../../modules/vulkan/tensor/shaders/vktTensorQueryDimensionsShaders.cpp#L46)) for the explicit-width integer types (`uint8_t`, `uint16_t`, `uint32_t`, `uint64_t`, `int8_t`, `int16_t`, `int32_t`, `int64_t`) used as the template argument to `tensorARM<format, rank>`, as determined by `getTensorFormat()` in [vktTensorShaderUtil.cpp#L39-L64](../../../modules/vulkan/tensor/shaders/vktTensorShaderUtil.cpp#L39-L64).
