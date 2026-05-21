# vktTensorBool

## Overview

This file implements boolean logical operation tests for the `VK_ARM_tensors` extension. It verifies that tensor shader read/write operations correctly apply logical AND, OR, NOT, and XOR operators to `VK_FORMAT_R8_BOOL_ARM` tensors across various tiling modes, shapes, and stride configurations.

## Role of File

`vktTensorBool.cpp` registers the `"boolean"` subgroup under `dEQP-VK.tensor` via the factory function `createTensorBoolTests` ([vktTensorBool.cpp#L432-L439](../../../modules/vulkan/tensor/vktTensorBool.cpp#L432-L439)). It defines two classes:

- **`TensorBooleanOpTestCase`** ([vktTensorBool.cpp#L308-L366](../../../modules/vulkan/tensor/vktTensorBool.cpp#L308-L366)) -- the `TestCase` subclass responsible for support checking, shader generation, and test naming.
- **`TensorBooleanOpTestInstance`** ([vktTensorBool.cpp#L60-L78](../../../modules/vulkan/tensor/vktTensorBool.cpp#L60-L78)) -- the `TestInstance` subclass that executes the GPU compute pipeline and validates results on the CPU.

The helper `addTensorBoolTests` ([vktTensorBool.cpp#L370-L430](../../../modules/vulkan/tensor/vktTensorBool.cpp#L370-L430)) iterates over all parameter combinations and adds child test cases.

## Source Code Link

- Test file: [vktTensorBool.cpp](../../../modules/vulkan/tensor/vktTensorBool.cpp)
- Utility header: [vktTensorTestsUtil.hpp](../../../modules/vulkan/tensor/vktTensorTestsUtil.hpp)
- Utility implementation: [vktTensorTestsUtil.cpp](../../../modules/vulkan/tensor/vktTensorTestsUtil.cpp)
- Shader generator: [vktTensorBooleanShader.cpp](../../../modules/vulkan/tensor/shaders/vktTensorBooleanShader.cpp)

## Registration Hierarchy

```text
tensor.boolean
├── r8_bool_linear_shape_13_17_19_23_operator_and_apply_0
├── r8_bool_linear_shape_13_17_19_23_operator_and_apply_1
├── r8_bool_linear_shape_13_17_19_23_operator_not_apply_0
├── r8_bool_linear_shape_13_17_19_23_operator_not_apply_1
├── r8_bool_linear_shape_13_17_19_23_operator_or_apply_0
├── r8_bool_linear_shape_13_17_19_23_operator_or_apply_1
├── r8_bool_linear_shape_13_17_19_23_operator_xor_apply_0
├── r8_bool_linear_shape_13_17_19_23_operator_xor_apply_1
├── r8_bool_linear_shape_13_17_19_23_strides_11862_697_36_1_operator_and_apply_0
├── r8_bool_linear_shape_13_17_19_23_strides_11862_697_36_1_operator_and_apply_1
├── r8_bool_linear_shape_13_17_19_23_strides_11862_697_36_1_operator_not_apply_0
├── r8_bool_linear_shape_13_17_19_23_strides_11862_697_36_1_operator_not_apply_1
├── r8_bool_linear_shape_13_17_19_23_strides_11862_697_36_1_operator_or_apply_0
├── r8_bool_linear_shape_13_17_19_23_strides_11862_697_36_1_operator_or_apply_1
├── r8_bool_linear_shape_13_17_19_23_strides_11862_697_36_1_operator_xor_apply_0
├── r8_bool_linear_shape_13_17_19_23_strides_11862_697_36_1_operator_xor_apply_1
├── r8_bool_linear_shape_13_17_19_23_strides_7429_437_23_1_operator_and_apply_0
├── r8_bool_linear_shape_13_17_19_23_strides_7429_437_23_1_operator_and_apply_1
├── r8_bool_linear_shape_13_17_19_23_strides_7429_437_23_1_operator_not_apply_0
├── r8_bool_linear_shape_13_17_19_23_strides_7429_437_23_1_operator_not_apply_1
├── r8_bool_linear_shape_13_17_19_23_strides_7429_437_23_1_operator_or_apply_0
├── r8_bool_linear_shape_13_17_19_23_strides_7429_437_23_1_operator_or_apply_1
├── r8_bool_linear_shape_13_17_19_23_strides_7429_437_23_1_operator_xor_apply_0
├── r8_bool_linear_shape_13_17_19_23_strides_7429_437_23_1_operator_xor_apply_1
├── r8_bool_linear_shape_263_269_operator_and_apply_0
├── r8_bool_linear_shape_263_269_operator_and_apply_1
├── r8_bool_linear_shape_263_269_operator_not_apply_0
├── r8_bool_linear_shape_263_269_operator_not_apply_1
├── r8_bool_linear_shape_263_269_operator_or_apply_0
├── r8_bool_linear_shape_263_269_operator_or_apply_1
├── r8_bool_linear_shape_263_269_operator_xor_apply_0
├── r8_bool_linear_shape_263_269_operator_xor_apply_1
├── r8_bool_linear_shape_263_269_strides_269_1_operator_and_apply_0
├── r8_bool_linear_shape_263_269_strides_269_1_operator_and_apply_1
├── r8_bool_linear_shape_263_269_strides_269_1_operator_not_apply_0
├── r8_bool_linear_shape_263_269_strides_269_1_operator_not_apply_1
├── r8_bool_linear_shape_263_269_strides_269_1_operator_or_apply_0
├── r8_bool_linear_shape_263_269_strides_269_1_operator_or_apply_1
├── r8_bool_linear_shape_263_269_strides_269_1_operator_xor_apply_0
├── r8_bool_linear_shape_263_269_strides_269_1_operator_xor_apply_1
├── r8_bool_linear_shape_263_269_strides_282_1_operator_and_apply_0
├── r8_bool_linear_shape_263_269_strides_282_1_operator_and_apply_1
├── r8_bool_linear_shape_263_269_strides_282_1_operator_not_apply_0
├── r8_bool_linear_shape_263_269_strides_282_1_operator_not_apply_1
├── r8_bool_linear_shape_263_269_strides_282_1_operator_or_apply_0
├── r8_bool_linear_shape_263_269_strides_282_1_operator_or_apply_1
├── r8_bool_linear_shape_263_269_strides_282_1_operator_xor_apply_0
├── r8_bool_linear_shape_263_269_strides_282_1_operator_xor_apply_1
├── r8_bool_linear_shape_37_43_47_operator_and_apply_0
├── r8_bool_linear_shape_37_43_47_operator_and_apply_1
├── r8_bool_linear_shape_37_43_47_operator_not_apply_0
├── r8_bool_linear_shape_37_43_47_operator_not_apply_1
├── r8_bool_linear_shape_37_43_47_operator_or_apply_0
├── r8_bool_linear_shape_37_43_47_operator_or_apply_1
├── r8_bool_linear_shape_37_43_47_operator_xor_apply_0
├── r8_bool_linear_shape_37_43_47_operator_xor_apply_1
├── r8_bool_linear_shape_37_43_47_strides_2021_47_1_operator_and_apply_0
├── r8_bool_linear_shape_37_43_47_strides_2021_47_1_operator_and_apply_1
├── r8_bool_linear_shape_37_43_47_strides_2021_47_1_operator_not_apply_0
├── r8_bool_linear_shape_37_43_47_strides_2021_47_1_operator_not_apply_1
├── r8_bool_linear_shape_37_43_47_strides_2021_47_1_operator_or_apply_0
├── r8_bool_linear_shape_37_43_47_strides_2021_47_1_operator_or_apply_1
├── r8_bool_linear_shape_37_43_47_strides_2021_47_1_operator_xor_apply_0
├── r8_bool_linear_shape_37_43_47_strides_2021_47_1_operator_xor_apply_1
├── r8_bool_linear_shape_37_43_47_strides_2593_60_1_operator_and_apply_0
├── r8_bool_linear_shape_37_43_47_strides_2593_60_1_operator_and_apply_1
├── r8_bool_linear_shape_37_43_47_strides_2593_60_1_operator_not_apply_0
├── r8_bool_linear_shape_37_43_47_strides_2593_60_1_operator_not_apply_1
├── r8_bool_linear_shape_37_43_47_strides_2593_60_1_operator_or_apply_0
├── r8_bool_linear_shape_37_43_47_strides_2593_60_1_operator_or_apply_1
├── r8_bool_linear_shape_37_43_47_strides_2593_60_1_operator_xor_apply_0
├── r8_bool_linear_shape_37_43_47_strides_2593_60_1_operator_xor_apply_1
├── r8_bool_linear_shape_71693_operator_and_apply_0
├── r8_bool_linear_shape_71693_operator_and_apply_1
├── r8_bool_linear_shape_71693_operator_not_apply_0
├── r8_bool_linear_shape_71693_operator_not_apply_1
├── r8_bool_linear_shape_71693_operator_or_apply_0
├── r8_bool_linear_shape_71693_operator_or_apply_1
├── r8_bool_linear_shape_71693_operator_xor_apply_0
├── r8_bool_linear_shape_71693_operator_xor_apply_1
├── r8_bool_optimal_shape_13_17_19_23_operator_and_apply_0
├── r8_bool_optimal_shape_13_17_19_23_operator_and_apply_1
├── r8_bool_optimal_shape_13_17_19_23_operator_not_apply_0
├── r8_bool_optimal_shape_13_17_19_23_operator_not_apply_1
├── r8_bool_optimal_shape_13_17_19_23_operator_or_apply_0
├── r8_bool_optimal_shape_13_17_19_23_operator_or_apply_1
├── r8_bool_optimal_shape_13_17_19_23_operator_xor_apply_0
├── r8_bool_optimal_shape_13_17_19_23_operator_xor_apply_1
├── r8_bool_optimal_shape_263_269_operator_and_apply_0
├── r8_bool_optimal_shape_263_269_operator_and_apply_1
├── r8_bool_optimal_shape_263_269_operator_not_apply_0
├── r8_bool_optimal_shape_263_269_operator_not_apply_1
├── r8_bool_optimal_shape_263_269_operator_or_apply_0
├── r8_bool_optimal_shape_263_269_operator_or_apply_1
├── r8_bool_optimal_shape_263_269_operator_xor_apply_0
├── r8_bool_optimal_shape_263_269_operator_xor_apply_1
├── r8_bool_optimal_shape_37_43_47_operator_and_apply_0
├── r8_bool_optimal_shape_37_43_47_operator_and_apply_1
├── r8_bool_optimal_shape_37_43_47_operator_not_apply_0
├── r8_bool_optimal_shape_37_43_47_operator_not_apply_1
├── r8_bool_optimal_shape_37_43_47_operator_or_apply_0
├── r8_bool_optimal_shape_37_43_47_operator_or_apply_1
├── r8_bool_optimal_shape_37_43_47_operator_xor_apply_0
├── r8_bool_optimal_shape_37_43_47_operator_xor_apply_1
├── r8_bool_optimal_shape_71693_operator_and_apply_0
├── r8_bool_optimal_shape_71693_operator_and_apply_1
├── r8_bool_optimal_shape_71693_operator_not_apply_0
├── r8_bool_optimal_shape_71693_operator_not_apply_1
├── r8_bool_optimal_shape_71693_operator_or_apply_0
├── r8_bool_optimal_shape_71693_operator_or_apply_1
├── r8_bool_optimal_shape_71693_operator_xor_apply_0
└── r8_bool_optimal_shape_71693_operator_xor_apply_1
```

Total: 112 test cases.

## Test Families

### r8_bool_linear_shape_{dims}[_strides_{s}]_operator_{op}_apply_{v}

Tests with `VK_TENSOR_TILING_LINEAR_ARM`. Three stride variants are exercised for rank > 1 shapes:

1. **Implicit packed strides** -- empty strides vector, implying tightly packed layout ([vktTensorBool.cpp#L399-L403](../../../modules/vulkan/tensor/vktTensorBool.cpp#L399-L403)).
2. **Explicit packed strides** -- strides computed via `getTensorStrides(shape, elementSize)` ([vktTensorBool.cpp#L406-L411](../../../modules/vulkan/tensor/vktTensorBool.cpp#L406-L411)).
3. **Explicit non-packed (padded) strides** -- strides with padding of `13 * elementSize` added per dimension ([vktTensorBool.cpp#L414-L419](../../../modules/vulkan/tensor/vktTensorBool.cpp#L414-L419)).

For rank-1 (shape `{71693}`), only the implicit packed variant is generated since explicit strides are gated by `rank > 1` ([vktTensorBool.cpp#L406](../../../modules/vulkan/tensor/vktTensorBool.cpp#L406) and [vktTensorBool.cpp#L414](../../../modules/vulkan/tensor/vktTensorBool.cpp#L414)).

### r8_bool_optimal_shape_{dims}_operator_{op}_apply_{v}

Tests with `VK_TENSOR_TILING_OPTIMAL_ARM`. No explicit strides are provided for optimal tiling ([vktTensorBool.cpp#L422-L426](../../../modules/vulkan/tensor/vktTensorBool.cpp#L422-L426)). For optimal tiling, data is uploaded to a linear staging tensor first, then copied to the optimal tensor via `cmdCopyTensorARM` ([vktTensorBool.cpp#L183-L194](../../../modules/vulkan/tensor/vktTensorBool.cpp#L183-L194)). After compute, the result is copied back to the linear staging tensor for readback ([vktTensorBool.cpp#L222-L234](../../../modules/vulkan/tensor/vktTensorBool.cpp#L222-L234)).

## Parameter Dimensions

| Dimension | Values |
|-----------|--------|
| **Format** | `VK_FORMAT_R8_BOOL_ARM` only ([vktTensorBool.cpp#L379](../../../modules/vulkan/tensor/vktTensorBool.cpp#L379)) |
| **Tiling** | `VK_TENSOR_TILING_LINEAR_ARM`, `VK_TENSOR_TILING_OPTIMAL_ARM` |
| **Shapes** | `{71693}`, `{263, 269}`, `{37, 43, 47}`, `{13, 17, 19, 23}` ([vktTensorBool.cpp#L372-L377](../../../modules/vulkan/tensor/vktTensorBool.cpp#L372-L377)) |
| **Strides (linear)** | Implicit packed (empty), explicit packed, explicit non-packed with `13 * elementSize` padding per dimension ([vktTensorBool.cpp#L385-L392](../../../modules/vulkan/tensor/vktTensorBool.cpp#L385-L392)) |
| **Operators** | `AND`, `OR`, `NOT`, `XOR` ([vktTensorBool.cpp#L394](../../../modules/vulkan/tensor/vktTensorBool.cpp#L394)) |
| **Apply value** | `true` (1), `false` (0) -- the right-hand operand for AND/OR/XOR; unused for NOT ([vktTensorBool.cpp#L396](../../../modules/vulkan/tensor/vktTensorBool.cpp#L396)) |

The padded stride formula is `paddedStrides[rank - i] = paddedStrides[rank - i + 1] * shape[rank - i + 1] + 13 * elementSize` ([vktTensorBool.cpp#L391](../../../modules/vulkan/tensor/vktTensorBool.cpp#L391)), which intentionally introduces gaps between consecutive dimension slices.

## Support / Feature Requirements

The `checkSupport` method in `TensorBooleanOpTestCase` ([vktTensorBool.cpp#L325-L354](../../../modules/vulkan/tensor/vktTensorBool.cpp#L325-L354)) enforces:

1. **Extension**: `VK_ARM_tensors` must be supported ([vktTensorBool.cpp#L327](../../../modules/vulkan/tensor/vktTensorBool.cpp#L327)).
2. **Dimension count**: `m_parameters.rank()` must not exceed `maxTensorDimensionCount` from `VkPhysicalDeviceTensorPropertiesARM` ([vktTensorBool.cpp#L329-L332](../../../modules/vulkan/tensor/vktTensorBool.cpp#L329-L332)).
3. **Shader tensor access**: `deviceSupportsShaderTensorAccess(ctx)` must return true ([vktTensorBool.cpp#L334-L337](../../../modules/vulkan/tensor/vktTensorBool.cpp#L334-L337)).
4. **Compute stage access**: `deviceSupportsShaderStagesTensorAccess(ctx, VK_SHADER_STAGE_COMPUTE_BIT)` must return true ([vktTensorBool.cpp#L339-L342](../../../modules/vulkan/tensor/vktTensorBool.cpp#L339-L342)).
5. **Format feature**: The format `VK_FORMAT_R8_BOOL_ARM` with the given tiling must support `VK_FORMAT_FEATURE_2_TENSOR_SHADER_BIT_ARM` ([vktTensorBool.cpp#L344-L348](../../../modules/vulkan/tensor/vktTensorBool.cpp#L344-L348)).
6. **Non-packed tensors**: If strides are non-packed (`m_parameters.packed()` returns false), then `deviceSupportsNonPackedTensors(ctx)` must return true ([vktTensorBool.cpp#L350-L353](../../../modules/vulkan/tensor/vktTensorBool.cpp#L350-L353)).

## Verification Methods

Verification is performed entirely on the CPU inside `TensorBooleanOpTestInstance::iterate()` ([vktTensorBool.cpp#L80-L306](../../../modules/vulkan/tensor/vktTensorBool.cpp#L80-L306)):

1. **Input generation**: A `StridedMemoryUtils<uint8_t>` object fills the initial tensor data via `fill()` ([vktTensorBool.cpp#L117-L119](../../../modules/vulkan/tensor/vktTensorBool.cpp#L117-L119)).
2. **GPU execution**: The compute shader reads each element from the input tensor, applies the boolean operator, and writes the result to the output tensor ([vktTensorBooleanShader.cpp#L73-L108](../../../modules/vulkan/tensor/shaders/vktTensorBooleanShader.cpp#L73-L108)).
3. **CPU comparison**: After downloading the result, each element is compared against the expected value computed on the CPU ([vktTensorBool.cpp#L264-L303](../../../modules/vulkan/tensor/vktTensorBool.cpp#L264-L303)):
   - `AND`: `expected = initialTensorData[idx] && m_testValue`
   - `OR`: `expected = initialTensorData[idx] || m_testValue`
   - `XOR`: `expected = static_cast<bool>(initialTensorData[idx]) ^ m_testValue`
   - `NOT`: `expected = !initialTensorData[idx]`
4. **Failure reporting**: On mismatch, the test returns `tcu::TestStatus::fail` with the element index, expected value, and actual value ([vktTensorBool.cpp#L297-L300](../../../modules/vulkan/tensor/vktTensorBool.cpp#L297-L300)).

## Test Principles

The tests validate end-to-end correctness of boolean tensor operations through the `VK_ARM_tensors` pipeline:

1. **Shader tensor I/O**: The generated GLSL compute shader uses `GL_ARM_tensors` extension with `tensorARM<bool, N>` declarations and `tensorReadARM`/`tensorWriteARM` builtins ([vktTensorBooleanShader.cpp#L51-L52](../../../modules/vulkan/tensor/shaders/vktTensorBooleanShader.cpp#L51-L52) and [vktTensorBooleanShader.cpp#L76-L81](../../../modules/vulkan/tensor/shaders/vktTensorBooleanShader.cpp#L76-L81)).
2. **Coordinate mapping**: The shader computes N-dimensional tensor coordinates from `gl_GlobalInvocationID.x` by dividing by the product of higher dimension sizes ([vktTensorBooleanShader.cpp#L63-L71](../../../modules/vulkan/tensor/shaders/vktTensorBooleanShader.cpp#L63-L71)). The dispatch uses `(elements, 1, 1)` workgroups ([vktTensorBool.cpp#L209](../../../modules/vulkan/tensor/vktTensorBool.cpp#L209)).
3. **Tiling path divergence**: For optimal tiling, the test creates an additional linear staging tensor and uses `cmdCopyTensorARM` for upload/download with appropriate `VkTensorMemoryBarrierARM` pipeline barriers ([vktTensorBool.cpp#L107-L115](../../../modules/vulkan/tensor/vktTensorBool.cpp#L107-L115), [vktTensorBool.cpp#L181-L234](../../../modules/vulkan/tensor/vktTensorBool.cpp#L181-L234)). For linear tiling, direct host upload/download is used ([vktTensorBool.cpp#L121-L131](../../../modules/vulkan/tensor/vktTensorBool.cpp#L121-L131), download at [vktTensorBool.cpp#L253-L256](../../../modules/vulkan/tensor/vktTensorBool.cpp#L253-L256)).
4. **Stride coverage**: The three stride variants (implicit packed, explicit packed, explicit non-packed) ensure that both tightly packed and strided tensor memory layouts are exercised, with the non-packed variant intentionally introducing gaps to stress stride-aware access.
5. **NOT operator independence from apply value**: The `NOT` operator ignores `m_testValue` (it is a unary operator), but the test still generates both `apply_0` and `apply_1` variants for uniformity ([vktTensorBool.cpp#L284-L288](../../../modules/vulkan/tensor/vktTensorBool.cpp#L284-L288)).

## Notes / Uncertainties

- The `StridedMemoryUtils<uint8_t>::fill()` method generates initial data; the exact fill pattern (e.g., random vs. deterministic) is defined in the utility implementation and is not visible from this file alone.
- The `NOT` operator generates redundant `apply_0`/`apply_1` test variants since the apply value is unused for unary NOT. This appears intentional for parameter space uniformity observed in the inspected file.
- The padding constant `13` in the non-packed stride computation ([vktTensorBool.cpp#L391](../../../modules/vulkan/tensor/vktTensorBool.cpp#L391)) is a hardcoded arbitrary value chosen to create non-trivial stride gaps.
- The test name construction uses `paramsToString(parameters, op) + "_apply_" + de::toString(testValue)` ([vktTensorBool.cpp#L313](../../../modules/vulkan/tensor/vktTensorBool.cpp#L313)), where `de::toString(bool)` produces `"0"` or `"1"`.
- The `BooleanOperator` enum is defined in [vktTensorTestsUtil.hpp#L58-L64](../../../modules/vulkan/tensor/vktTensorTestsUtil.hpp#L58-L64) with values `AND`, `OR`, `NOT`, `XOR`.
