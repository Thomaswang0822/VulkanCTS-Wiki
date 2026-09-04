# Understanding Brief: cooperative-vector matrix conversion tests

## One-Sentence Test Purpose

This test checks whether `vkConvertCooperativeVectorMatrixNV` and `vkCmdConvertCooperativeVectorMatrixNV` preserve matrix values while changing cooperative-vector matrix layouts and component types through host and device paths.

## Background Knowledge

### Matrix layouts describe memory interpretation

Row-major storage places each row's elements consecutively; column-major storage does the same for columns. The `inferencingOptimal` and `trainingOptimal` layouts are implementation-dependent opaque arrangements. The Vulkan API supplies conversion commands to produce those arrangements, and ignores the stride field for either optimal layout. The conversion structure still carries the matrix dimensions, component types, source and destination layouts, and strides for standard layouts. See [the Vulkan matrix-layout description](../../../../vulkan-docs/src/chapters/shaders.adoc#L4319-L4367).

Why it matters here:
- A value can move to a different byte position when a layout changes, so the test must read row-major and column-major results with different index/stride rules.
- An optimal-layout result cannot be checked by treating its bytes as an ordinary row-major or column-major matrix; the test converts it back before comparing values.

### Component conversion is quantization, not a byte copy

`VK_COMPONENT_TYPE_FLOAT16_NV`, `VK_COMPONENT_TYPE_FLOAT_E4M3_NV`, and `VK_COMPONENT_TYPE_FLOAT_E5M2_NV` represent different floating-point precisions. The Vulkan specification permits conversion between 32-bit or 16-bit floating point and supported lower-precision floating-point types and requires round-to-nearest-even for that conversion. E4M3 and E5M2 use different exponent and mantissa widths. See [component-type semantics](../../../../vulkan-docs/src/chapters/shaders.adoc#L4100-L4147) and [conversion rules](../../../../vulkan-docs/src/chapters/shaders.adoc#L4361-L4398).

Why it matters here:
- The type-conversion test compares the final value with a value first quantized by the CTS helper, rather than comparing it directly with the original higher-precision value.
- The test's supported matrix types come from `vkGetPhysicalDeviceCooperativeVectorPropertiesNV`; implementations may advertise different combinations.

## One Concrete Example

For a layout case such as `dEQP-VK.cooperative_vector.layoutconvert.host.float16.rowMajor.colMajor`, the host starts with a rectangular FP16 matrix in row-major storage. It converts that data to column-major, then to the second selected layout, and finally back to row-major. A source element at logical position `(i, j)` is read from the column-major result at column `j`, row `i`; this is why the test uses `matrixOffsets[m] + j * matrixStrides[m]` and element index `i` for a column-major destination. The example is reconstructed from the source's indexing logic, not a separate shader case.

For a type case such as `dEQP-VK.cooperative_vector.typeconvert.host.float32tofloate4m3`, the test fills a 1-by-N FP32 row-major matrix, converts it to `inferencingOptimal` E4M3, and converts it to an FP32 row-major matrix for readback. For every element, the host computes the expected E4M3 value by storing the source float through the same CTS conversion helper and then compares that quantized value with the final output.

## End-to-End Test Flow

```text
[host] select a registered layout/type case and allocate one host-visible buffer
[host] generate matrix bytes and query the destination size for optimal-layout conversions
[host] set VkConvertCooperativeVectorMatrixInfoNV with dimensions, types, layouts, strides, and non-overlapping ranges
[host] call vkConvertCooperativeVectorMatrixNV for a host case
[host] or record vkCmdConvertCooperativeVectorMatrixNV with device addresses for a device case
[device] execute each recorded device conversion; the host conversion call executes the conversion operation directly
[host] flush, submit, wait, invalidate, and read the buffer
[host] compare readable layout results with source values, or compare type results with CPU-quantized references
[host] return pass only if every checked element matches
```

The device path inserts a dependency from `VK_PIPELINE_STAGE_2_CONVERT_COOPERATIVE_VECTOR_MATRIX_BIT_NV` and `VK_ACCESS_2_TRANSFER_WRITE_BIT` to later commands. Both paths submit and wait before invalidating the allocation and checking memory. These steps follow the implementation at [layout conversion](../../../../vulkancts/modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L261-L339) and [type conversion](../../../../vulkancts/modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L723-L817).

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The matrix page has no generated shader or SPIR-V artifact. The source calls the Vulkan matrix-conversion API directly and checks host-visible memory. The generated artifacts are matrix byte patterns and `VkConvertCooperativeVectorMatrixInfoNV` requests:

- Layout cases generate random FP or integer matrix elements with a fixed random seed, arrange four conversion slots, and vary the two intermediate layouts.
- Type cases generate every representable byte value for 8-bit and 16-bit sources, and a patterned plus random set for FP32 sources. They first query the optimal destination size with `dstData` unset.
- The final type-conversion destination is FP16 when the source element size is 1 or 2 bytes, and FP32 when the source element size is 4 bytes.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Host-visible storage buffer | yes | yes, through a device address on device cases | yes on device cases; host conversion writes through its host address | yes | Holds source and destination matrices at separately aligned offsets. |
| `VkConvertCooperativeVectorMatrixInfoNV` | yes | passed to the conversion command | yes, as conversion parameters | no | Describes source/destination addresses, byte sizes, types, dimensions, layouts, and strides. |
| Command buffer and memory barrier | yes | yes | records device conversion and orders later access | no | Exists only for device conversion; the barrier covers conversion writes before later commands. |
| CTS CPU reference storage | yes | no | no | no | Re-encodes a value in the destination component type for type-conversion comparison. |

The optimal-layout stride is zero in the requests because the specification ignores stride for non-row-major and non-column-major layouts. Standard-layout strides are rounded up to a 16-byte multiple. Matrix regions are separated by 64-byte alignment, and the initial layout region begins at offset 128.

## What Is Checked

- `layoutconvert` uses dimensions from 1 through 32 rows and 1 through 32 columns. After three conversions, it checks each intermediate result whose layout is row-major or column-major. Integer values must match exactly. Floating-point values must also match exactly; the source does not apply a tolerance.
- `typeconvert` uses a one-row matrix whose column count covers the source value set: `1 << (8 * srcElementSize)` for 8-bit and 16-bit sources, or `2 << 16` for FP32. It reads each final row-major result and compares it with a CPU value quantized to the selected intermediate destination type. NaNs compare as equal when both reference and output are NaN.
- A Vulkan call failure is reported through `VK_CHECK`; a value mismatch changes the test result to `QP_TEST_RESULT_FAIL`.

## Behavior Parameter Identification

> **Behavior parameter:** test family
>
> **Candidate values:** `layoutconvert`, `typeconvert`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `layoutconvert` | Incorrect row/column stride or element placement; incorrect conversion to or from an implementation-dependent optimal layout; host/device conversion or synchronization failure. |
| `typeconvert` | Incorrect lower-precision encoding or rounding; unsupported component-type conversion; incorrect optimal-layout storage or final readback. |

## Important Variations and Special Cases

- Each family has `host` and `device` registered branches. Host cases use `vkConvertCooperativeVectorMatrixNV` with host addresses. Device cases use `vkCmdConvertCooperativeVectorMatrixNV` with 64-byte-aligned device addresses.
- Layout conversion registers FP16, FP32, UINT8, SINT8, E4M3, and E5M2 source types. FP8 cases use only the two optimal layouts for intermediate results because the implementation cannot write FP8 to row-major or column-major destinations; the final slot is FP16 for FP8 input.
- Layout conversion's registration matrix has two independently selected intermediate layouts, with row-major as the source and final destination. The mustpass file contains 144 cases: 6 source types, 2 address modes, and 24 permitted layout pairs after FP8 pruning.
- Type conversion registers ten source/destination pairs and two address modes, for 20 mustpass cases. Its destination is always a readable FP16 or FP32 row-major matrix after the optimal-layout intermediate.
- Support checks require Vulkan 1.1, the `cooperativeVector` feature, at least one reported cooperative-vector property, and the relevant component interpretation. The specification likewise makes supported type combinations implementation-dependent.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Category registration | [vktCooperativeVectorTests.cpp#L37-L50](../../../../vulkancts/modules/vulkan/cooperative_vector/vktCooperativeVectorTests.cpp#L37-L50) | Registers `layoutconvert` and `typeconvert` under `cooperative_vector`. |
| Layout case matrix | [vktCooperativeVectorMatrixTests.cpp#L424-L494](../../../../vulkancts/modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L424-L494) | Defines types, layouts, host/device branches, and FP8 pruning. |
| Layout execution and checking | [vktCooperativeVectorMatrixTests.cpp#L165-L411](../../../../vulkancts/modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L165-L411) | Generates matrices, performs three conversions, synchronizes device work, and compares values. |
| Type case matrix | [vktCooperativeVectorMatrixTests.cpp#L844-L886](../../../../vulkancts/modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L844-L886) | Defines the ten type pairs and two address modes. |
| Type execution and checking | [vktCooperativeVectorMatrixTests.cpp#L606-L839](../../../../vulkancts/modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L606-L839) | Queries optimal size, generates source values, converts, and compares quantized output. |
| Data-type helpers | [vktCooperativeVectorUtils.cpp#L34-L73](../../../../vulkancts/modules/vulkan/cooperative_vector/vktCooperativeVectorUtils.cpp#L34-L73) | Defines widths, float classification, and FP8 component metadata. |
| Mustpass coverage | [cooperative-vector.txt#L6555-L6698](../../../../vulkancts/mustpass/main/vk-default/cooperative-vector.txt#L6555-L6698), [cooperative-vector.txt#L53543-L53562](../../../../vulkancts/mustpass/main/vk-default/cooperative-vector.txt#L53543-L53562) | Lists the registered layout and type conversion cases. |
| API semantics | [shaders.adoc#L4272-L4459](../../../../vulkan-docs/src/chapters/shaders.adoc#L4272-L4459) | Defines size queries, layouts, strides, types, rounding, and host/device command behavior. |

## Questions / Risk Points for User Audit

- Is the distinction between a readable standard layout and an opaque optimal layout clear?
- Is the host/device timeline clear without a shader walkthrough?
- Does the quantization example explain why the type test compares against a converted CPU value?
- Should the page call out that the source's layout comparisons use exact equality for floating-point values?
- Are the FP8 registration exclusions clear enough to avoid reading the type/layout tables as a full Cartesian product?

## Conversion Notes for Final Wiki Page

- Keep the layout-versus-type family comparison in the overview and behavior sections; do not split this source file into two pages.
- Distill the layout and component-type concepts into short page-local prerequisite bullets.
- Preserve the two concrete examples as compact explanations of indexing and quantized-reference checking, not as shader walkthroughs.
- Keep the host/device flow and resource table because conversion semantics use generated matrix bytes and explicit addresses rather than shader code.
- Copy the `### Failure Cause Mapping` table above directly into the final page. Write the final `### Cause Analysis` separately from the implementation and specification evidence.
- The source-backed shader role is no walkthrough: these tests exercise Vulkan matrix-conversion commands and host-memory checks, not generated shader code. Do not invent a shader exception or a shader walkthrough.
