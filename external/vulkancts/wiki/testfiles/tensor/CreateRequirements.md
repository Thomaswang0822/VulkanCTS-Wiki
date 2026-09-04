## Overview

**Core question:** Can an implementation create the requested ARM tensor shapes and report memory requirements that cover their data?

- This page covers the `tensor.creation_and_requirements` test family created by `vktTensorCreateRequirements.cpp` and attached to the `tensor` test category by `vktTensorTests.cpp`.
- The family registers one test case for each pair of eight integer formats and two tilings. The registered names are `linear_<format>` and `optimal_<format>`; the mustpass file contains 16 entries.
- Each test queries the device tensor limits, builds greedy limit-oriented packed shapes for every supported rank, and adds maximum-stride linear shapes when `tensorNonPacked` is supported.
- For every generated shape, the test creates a `VkTensorARM`, calls `vkGetTensorMemoryRequirementsARM`, and checks that the returned memory type mask is nonzero. Linear tensors also get a lower-bound size check.
- The family has no shader, dispatch, memory binding, or data-result behavior. It checks resource creation and the memory-requirements query itself.

## Background Knowledge

- **Tensor description.** `VkTensorDescriptionARM` supplies a tensor's tiling, one-component `VkFormat`, rank (`dimensionCount`), per-dimension element counts (`pDimensions`), optional byte strides (`pStrides`), and usage flags. The Vulkan specification defines the dimensions' product as the tensor element count and uses the description in `VkTensorCreateInfoARM`.
- **Linear and optimal tiling.** `VK_TENSOR_TILING_LINEAR_ARM` lays elements out using the tensor's byte strides. `VK_TENSOR_TILING_OPTIMAL_ARM` leaves the layout to the implementation and requires `pStrides` to be `NULL`.
- **Packed tensors and strides.** A packed tensor uses the element size as its innermost stride, with each outer stride equal to the next stride multiplied by the next dimension. A linear tensor may provide other positive, element-size-aligned strides when the `tensorNonPacked` feature is enabled.
- **Memory requirements.** `vkGetTensorMemoryRequirementsARM` returns a `VkMemoryRequirements2` containing the allocation size, alignment, and compatible memory-type bits for an existing tensor. This page uses the type mask and size fields; it does not allocate or bind the returned memory.

## Registration Hierarchy

```text
tensor.creation_and_requirements
├── linear_r16_sint
├── linear_r16_uint
├── linear_r32_sint
├── linear_r32_uint
├── linear_r64_sint
├── linear_r64_uint
├── linear_r8_sint
├── linear_r8_uint
├── optimal_r16_sint
├── optimal_r16_uint
├── optimal_r32_sint
├── optimal_r32_uint
├── optimal_r64_sint
├── optimal_r64_uint
├── optimal_r8_sint
└── optimal_r8_uint
```

`tensor::createTests` adds this test family below the `tensor` test category. `addCreateRequirementTests` creates the 16 test-case leaves by iterating over the format list and the `linear` and `optimal` tiling values. The mustpass entries use the same paths.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Format | `VK_FORMAT_R8_UINT`, `VK_FORMAT_R8_SINT`, `VK_FORMAT_R16_UINT`, `VK_FORMAT_R16_SINT`, `VK_FORMAT_R32_UINT`, `VK_FORMAT_R32_SINT`, `VK_FORMAT_R64_UINT`, `VK_FORMAT_R64_SINT` | Selects the integer element type and its byte size: 1, 2, 4, or 8 bytes. The size affects the element-count limit derived from `maxTensorSize` and every linear stride and size calculation. | [getAllTestFormats](../../../modules/vulkan/tensor/vktTensorTestsUtil.cpp#L48-L56), [getFormatSize](../../../modules/vulkan/tensor/vktTensorTestsUtil.cpp#L80-L112) |
| Tiling | `VK_TENSOR_TILING_LINEAR_ARM`, `VK_TENSOR_TILING_OPTIMAL_ARM` | Selects whether the test supplies linear strides and checks a data-size lower bound, or lets the implementation choose an optimal layout without making a size assumption. | [tiling loop and test-case construction](../../../modules/vulkan/tensor/vktTensorCreateRequirements.cpp#L239-L247), [tensor description rules](../../../../vulkan-docs/src/chapters/resources.adoc#L13022-L13025) |
| Rank | `1` through the device's `maxTensorDimensionCount` | Produces one maximum packed shape for each rank supported by the current device. The test obtains the upper bound from `VkPhysicalDeviceTensorPropertiesARM`. | [rank loop](../../../modules/vulkan/tensor/vktTensorCreateRequirements.cpp#L63-L85), [tensor properties](../../../../vulkan-docs/src/chapters/limits.adoc#L5694-L5712) |
| Packed shape | One generated shape per rank, with the product bounded by `min(maxTensorElements, maxTensorSize / elementSize)` and each dimension bounded by `maxPerDimensionTensorElements` | Exercises creation near the element-count and byte-size limits while keeping the default linear layout packed. | [maximum packed-shape generation](../../../modules/vulkan/tensor/vktTensorCreateRequirements.cpp#L58-L85), [tensor creation limits](../../../../vulkan-docs/src/chapters/resources.adoc#L12819-L12844) |
| Non-packed linear shape | One generated shape per rank when `tensorNonPacked` is enabled; dimensions are all `1`, the innermost stride is the element size, and outer strides use the aligned maximum stride | Exercises large legal linear strides without applying a non-packed layout to optimal tiling. | [non-packed shape generation](../../../modules/vulkan/tensor/vktTensorCreateRequirements.cpp#L87-L123), [tensorNonPacked feature](../../../../vulkan-docs/src/chapters/features.adoc#L8042-L8044) |

The source does not register rank or shape names as additional mustpass path components. These values are generated inside each of the 16 registered test cases from the device's reported limits.

## Behavior Parameters

The primary behavioral axis is the registered format-and-tiling test case. Changing either value changes the tensor description presented to the implementation: the format changes element size, and the tiling changes whether the test supplies strides and applies the linear size invariant.

### `linear_r16_sint`: signed 16-bit linear tensors

The test creates signed 16-bit tensors with linear tiling. It covers maximum packed shapes at each supported rank and, when `tensorNonPacked` is enabled, one maximum-stride shape at each rank.

### `linear_r16_uint`: unsigned 16-bit linear tensors

The test creates unsigned 16-bit tensors with the same rank and stride generation as the signed 16-bit case. The format feature query and the linear size check use `VK_FORMAT_R16_UINT`.

### `linear_r32_sint`: signed 32-bit linear tensors

The test creates signed 32-bit tensors. Each generated packed shape uses four-byte elements, and a custom-stride shape uses an innermost stride of four bytes.

### `linear_r32_uint`: unsigned 32-bit linear tensors

The test creates unsigned 32-bit tensors and applies the linear memory-requirement check to the resulting tensor descriptions.

### `linear_r64_sint`: signed 64-bit linear tensors

The test creates signed 64-bit tensors. Their eight-byte element size reduces the number of elements that can fit within `maxTensorSize` and sets the innermost custom stride to eight bytes.

### `linear_r64_uint`: unsigned 64-bit linear tensors

The test creates unsigned 64-bit tensors and checks memory requirements for both generated packed and, when available, non-packed linear descriptions.

### `linear_r8_sint`: signed 8-bit linear tensors

The test creates signed 8-bit tensors. Their one-byte element size permits the largest element-count budget among the formats in this family, subject to the device limits.

### `linear_r8_uint`: unsigned 8-bit linear tensors

The test creates unsigned 8-bit tensors and checks that the returned requirements cover the packed and eligible maximum-stride linear layouts.

### `optimal_r16_sint`: signed 16-bit optimal tensors

The test creates signed 16-bit tensors with optimal tiling. It supplies no stride array and checks only the returned memory-type mask, because the implementation controls the optimal layout size.

### `optimal_r16_uint`: unsigned 16-bit optimal tensors

The test creates unsigned 16-bit optimal tensors across the generated ranks. The format support query selects the optimal-tiling feature mask for this format.

### `optimal_r32_sint`: signed 32-bit optimal tensors

The test creates signed 32-bit optimal tensors with implementation-selected layout. The element size still controls the generated maximum element budget.

### `optimal_r32_uint`: unsigned 32-bit optimal tensors

The test creates unsigned 32-bit optimal tensors and queries their memory requirements without imposing a packed-size equation on the returned allocation size.

### `optimal_r64_sint`: signed 64-bit optimal tensors

The test creates signed 64-bit optimal tensors. It uses the eight-byte format size when constructing maximum element-count shapes, but leaves the optimal memory footprint to the implementation.

### `optimal_r64_uint`: unsigned 64-bit optimal tensors

The test creates unsigned 64-bit optimal tensors and checks that the implementation reports at least one compatible memory type.

### `optimal_r8_sint`: signed 8-bit optimal tensors

The test creates signed 8-bit optimal tensors at every generated rank. It does not supply custom strides or compare the returned size with a packed data size.

### `optimal_r8_uint`: unsigned 8-bit optimal tensors

The test creates unsigned 8-bit optimal tensors and performs the same creation and memory-type requirement checks for the unsigned format.

## Shader Analysis

This test family contains no shader source and performs no shader operation. It creates `VkTensorARM` objects and queries their memory requirements on the host. There is no representative shader walkthrough or shader result to analyze.

## Runtime Execution and Result Checking

- `TensorRequirementsTestCase::checkSupport` requires the `VK_ARM_tensors` device functionality and the `VK_FORMAT_FEATURE_2_TENSOR_SHADER_BIT_ARM` feature for the selected format and tiling. The test uses this format feature as its support gate even though it does not execute a shader.
- `getMaxTensorParameters` reads `VkPhysicalDeviceTensorPropertiesARM` through `vkGetPhysicalDeviceProperties2`. It computes `maxElements` as the smaller of `maxTensorElements` and `maxTensorSize / elementSize`.
- For each rank from one through `maxTensorDimensionCount`, the packed generator fills dimensions greedily. It uses `maxPerDimensionTensorElements` for each dimension while more elements remain, then places the remainder in the next dimension.
- For eligible non-packed linear cases, the generator aligns a stride derived from `maxTensorStride` to the format size. It uses dimensions of `1`, assigns the element size to the innermost stride, and assigns the selected maximum stride to the outer strides.
- The host passes the selected tiling, format, dimensions, and optional strides to `makeTensorDescription`, then wraps that description in `VkTensorCreateInfoARM` with the utility `makeTensorCreateInfo`. The default usage value is zero.
- The test calls `createTensorARM`. For the resulting handle it fills `VkTensorMemoryRequirementsInfoARM::tensor`, initializes `VkMemoryRequirements2`, and calls `getTensorMemoryRequirementsARM`.
- Every generated case must return a nonzero `memoryRequirements.memoryTypeBits` mask. For linear tensors, the test calculates an expected lower bound: the product of dimensions times the element size for packed shapes, or `pStrides[0] * pDimensions[0]` for custom-stride shapes. The reported allocation size must be at least that value.
- The test returns pass after all generated descriptions satisfy these checks. It does not allocate memory, bind memory, submit commands, or inspect tensor contents.

## Failure Meaning

### Failure Cause Mapping

Each registered case exercises the same creation and query invariants; the format and tiling determine the generated descriptions and the linear-only size rule.

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `linear_r16_sint` | Tensor creation or memory-requirements reporting for signed 16-bit linear descriptions. |
| `linear_r16_uint` | Tensor creation or memory-requirements reporting for unsigned 16-bit linear descriptions. |
| `linear_r32_sint` | Tensor creation or memory-requirements reporting for signed 32-bit linear descriptions. |
| `linear_r32_uint` | Tensor creation or memory-requirements reporting for unsigned 32-bit linear descriptions. |
| `linear_r64_sint` | Tensor creation or memory-requirements reporting for signed 64-bit linear descriptions. |
| `linear_r64_uint` | Tensor creation or memory-requirements reporting for unsigned 64-bit linear descriptions. |
| `linear_r8_sint` | Tensor creation or memory-requirements reporting for signed 8-bit linear descriptions. |
| `linear_r8_uint` | Tensor creation or memory-requirements reporting for unsigned 8-bit linear descriptions. |
| `optimal_r16_sint` | Tensor creation or memory-requirements reporting for signed 16-bit optimal descriptions. |
| `optimal_r16_uint` | Tensor creation or memory-requirements reporting for unsigned 16-bit optimal descriptions. |
| `optimal_r32_sint` | Tensor creation or memory-requirements reporting for signed 32-bit optimal descriptions. |
| `optimal_r32_uint` | Tensor creation or memory-requirements reporting for unsigned 32-bit optimal descriptions. |
| `optimal_r64_sint` | Tensor creation or memory-requirements reporting for signed 64-bit optimal descriptions. |
| `optimal_r64_uint` | Tensor creation or memory-requirements reporting for unsigned 64-bit optimal descriptions. |
| `optimal_r8_sint` | Tensor creation or memory-requirements reporting for signed 8-bit optimal descriptions. |
| `optimal_r8_uint` | Tensor creation or memory-requirements reporting for unsigned 8-bit optimal descriptions. |

### Cause Analysis

#### Tensor creation or memory-requirements reporting

**Possible failure symptoms:** `vkCreateTensorARM` fails for a generated description, `memoryRequirements.memoryTypeBits` is zero, or a linear tensor reports an allocation size smaller than the test's expected lower bound. The test reports the explicit `No memory type bits set` message for the second condition and includes both sizes in the message for the linear size condition.

**Possible implementation causes:** A creation failure can reflect a mismatch between the implementation's accepted tensor formats, tilings, dimensions, strides, or enabled feature state and the advertised support. A zero memory-type mask means the implementation did not report any memory type compatible with a successfully created tensor, which conflicts with the requirements query contract. A too-small linear size would leave part of the packed data or the addressable strided range outside the reported allocation. The source and specification establish these checks, but they do not identify a more specific driver or hardware cause; that requires implementation-level investigation.

## Case Pruning

### Requirement-based pruning

- The device must provide `VK_ARM_tensors`; otherwise `checkSupport` rejects the test through `requireDeviceFunctionality("VK_ARM_tensors")`.
- The selected format and tiling must report `VK_FORMAT_FEATURE_2_TENSOR_SHADER_BIT_ARM` in the corresponding `linearTilingTensorFeatures` or `optimalTilingTensorFeatures` mask. A missing bit raises `NotSupportedError` with `Format not supported` rather than producing a failure result.
- The generated ranks and dimensions come from the device's `maxTensorDimensionCount`, `maxPerDimensionTensorElements`, `maxTensorElements`, and `maxTensorSize` properties. Those limits keep the descriptions within the tensor creation rules.
- Custom strides are generated only for linear tiling and only when `tensorNonPacked` is reported by `VkPhysicalDeviceTensorFeaturesARM`. Optimal tiling requires a null stride pointer, and the Vulkan specification requires `tensorNonPacked` for non-packed descriptions.

### Design-based pruning

- The format list contains only the eight signed and unsigned integer formats used by this family. Other formats recognized by utility code, including floating-point and boolean formats, are not registered here.
- The test creates one registered case for each format/tiling pair, then generates ranks and shapes inside that case instead of adding rank and shape components to the CTS path.
- Each rank receives one packed maximum shape. A linear case may receive one additional maximum-stride shape for that rank; optimal cases never receive custom-stride variants.
- The family stops after creation and requirements validation. Memory allocation, tensor-memory binding, transfer operations, shader access, and content validation belong to other tensor test families and are outside this page's test design.

## Key Takeaways

- `tensor.creation_and_requirements` covers 16 registered format/tiling cases for `R8`, `R16`, `R32`, and `R64` signed and unsigned integer formats.
- The cases generate ranks from one through the device limit and size their packed shapes against both the element-count and byte-size limits.
- Linear cases also test an eligible non-packed stride pattern and require the reported allocation size to cover the addressed range. Optimal cases check the memory-type mask without assuming an implementation-specific layout size.
- A skipped case means the extension or selected format feature is unavailable. A failure means the implementation created a tested tensor but returned unusable memory requirements, or violated the linear lower-bound check. See `## Failure Meaning` for the distinction.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Tensor category registration | [vktTestPackage.cpp#L1397-L1400](../../../modules/vulkan/vktTestPackage.cpp#L1397-L1400) | Adds the `tensor` root to the Vulkan CTS package. |
| Tensor category factory | [vktTensorTests.cpp#L37-L49](../../../modules/vulkan/tensor/vktTensorTests.cpp#L37-L49) | Adds `creation_and_requirements` and the other tensor test families below the category root. |
| Test-case factory and names | [vktTensorCreateRequirements.cpp#L239-L257](../../../modules/vulkan/tensor/vktTensorCreateRequirements.cpp#L239-L257) | Iterates over all formats and both tilings, then registers the exact intermediate test-case names. |
| Format inventory and sizes | [vktTensorTestsUtil.cpp#L48-L56](../../../modules/vulkan/tensor/vktTensorTestsUtil.cpp#L48-L56), [vktTensorTestsUtil.cpp#L80-L112](../../../modules/vulkan/tensor/vktTensorTestsUtil.cpp#L80-L112) | Defines the eight formats and their byte sizes. |
| Maximum shape generation | [vktTensorCreateRequirements.cpp#L55-L125](../../../modules/vulkan/tensor/vktTensorCreateRequirements.cpp#L55-L125) | Reads tensor properties and generates packed and eligible custom-stride descriptions for each rank. |
| Tensor description and create-info helpers | [vkObjUtil.cpp#L851-L887](../../../framework/vulkan/vkObjUtil.cpp#L851-L887) | Places tiling, format, dimensions, strides, and usage into the ARM tensor structures. |
| Support checks | [vktTensorCreateRequirements.cpp#L222-L229](../../../modules/vulkan/tensor/vktTensorCreateRequirements.cpp#L222-L229), [vktTensorTestsUtil.cpp#L341-L363](../../../modules/vulkan/tensor/vktTensorTestsUtil.cpp#L341-L363) | Requires `VK_ARM_tensors` and selects the format feature mask for the chosen tiling. |
| Creation and requirements validation | [vktTensorCreateRequirements.cpp#L138-L199](../../../modules/vulkan/tensor/vktTensorCreateRequirements.cpp#L138-L199) | Creates each tensor, queries `VkMemoryRequirements2`, and checks memory type bits and linear size. |
| Tensor property definitions | [limits.adoc#L5694-L5720](../../../../vulkan-docs/src/chapters/limits.adoc#L5694-L5720) | Defines the dimension, element-count, per-dimension, stride, and byte-size limits used by the generator. |
| Tensor description rules | [resources.adoc#L12995-L13108](../../../../vulkan-docs/src/chapters/resources.adoc#L12995-L13108) | Defines formats, ranks, stride semantics, packed tensors, and creation validity rules. |
| Memory requirements query | [resources.adoc#L9610-L9639](../../../../vulkan-docs/src/chapters/resources.adoc#L9610-L9639) | Defines `vkGetTensorMemoryRequirementsARM` and its tensor input structure. |
| Format feature masks | [formats.adoc#L3040-L3070](../../../../vulkan-docs/src/chapters/formats.adoc#L3040-L3070) | Defines the separate linear and optimal tensor feature masks and the shader feature bit used by the support gate. |
| Non-packed feature | [features.adoc#L8035-L8046](../../../../vulkan-docs/src/chapters/features.adoc#L8035-L8046) | Defines `tensorNonPacked`, which controls whether non-packed tensors may be created. |
| Mustpass entries | [tensor.txt#L745-L760](../../../mustpass/main/vk-default/tensor.txt#L745-L760) | Lists the 16 registered creation-and-requirements paths. |
