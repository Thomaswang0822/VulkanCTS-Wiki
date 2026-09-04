## Overview

**Core question:** Do host and device matrix conversion commands preserve cooperative-vector matrix values across registered layouts and component types?

- This page covers the implementation-bearing `layoutconvert` and `typeconvert` test families from `vktCooperativeVectorMatrixTests.cpp`.
- `layoutconvert` starts with row-major data, passes it through two selected layouts, and returns to row-major storage. It checks readable row-major and column-major results for exact value preservation.
- `typeconvert` starts with generated row-major values, converts through an implementation-dependent inferencing-optimal layout, and returns to row-major FP16 or FP32 storage. It compares the result with a CPU reference quantized to the selected component type.
- Each family has `host` and `device` branches. The host branch calls `vkConvertCooperativeVectorMatrixNV`; the device branch records `vkCmdConvertCooperativeVectorMatrixNV` with device addresses.
- The tests use generated matrix bytes and host-visible memory. They do not generate shader source, so this page has no shader walkthrough.

## Background Knowledge

- **Matrix layouts:** Row-major storage places each row's elements consecutively, while column-major storage does the same for columns. `inferencingOptimal` and `trainingOptimal` are implementation-dependent layouts that applications reach through the conversion commands. For either optimal layout, the API ignores the corresponding stride. ([Vulkan matrix-layout semantics](../../../../vulkan-docs/src/chapters/shaders.adoc#L4319-L4367))
- **Component conversion:** FP16, FP32, E4M3, and E5M2 use different floating-point encodings. Vulkan permits conversion between FP16 or FP32 and supported lower-precision floating-point types with round-to-nearest-even rounding. ([component types](../../../../vulkan-docs/src/chapters/shaders.adoc#L4100-L4147), [conversion rules](../../../../vulkan-docs/src/chapters/shaders.adoc#L4361-L4398))
- **Advertised support:** Implementations report supported cooperative-vector matrix interpretations through `vkGetPhysicalDeviceCooperativeVectorPropertiesNV`; the test checks those properties before execution. ([layout support check](../../../../vulkancts/modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L117-L158), [type support check](../../../../vulkancts/modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L551-L599))

## Registration Hierarchy

```text
cooperative_vector
├── layoutconvert
└── typeconvert
```

The page combines both direct test families because the same source file implements the two forms of `VkConvertCooperativeVectorMatrixInfoNV` conversion. Deeper address-mode, component-type, layout, and type-pair axes are described below rather than expanded in the hierarchy.

## Parameter Dimensions and Observed Values

| Dimension | Registered values or observed values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test family | `layoutconvert`, `typeconvert` | Selects layout-only checking or component-type conversion checking. | [`createChildren`](../../../../vulkancts/modules/vulkan/cooperative_vector/vktCooperativeVectorTests.cpp#L37-L50) |
| Address mode | `host`, `device` | Selects the host API call or a recorded device command. | [layout registrations](../../../../vulkancts/modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L445-L448), [type registrations](../../../../vulkancts/modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L866-L869) |
| Layout source type | `float16`, `float32`, `uint8`, `sint8`, `floate4m3`, `floate5m2` | Selects the element width and value representation for `layoutconvert`. | [`layoutconvert` cases](../../../../vulkancts/modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L424-L436) |
| Intermediate layout pair | `rowMajor`, `colMajor`, `inferencingOptimal`, `trainingOptimal` | Selects the first and second destination layouts in the three-step layout chain. | [`layoutconvert` cases](../../../../vulkancts/modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L438-L486) |
| Type pair | `float32tofloat16`, `float32tofloate4m3`, `float32tofloate5m2`, `float16tofloat16`, `float16tofloate4m3`, `float16tofloate5m2`, `floate4m3tofloat16`, `floate4m3tofloate4m3`, `floate5m2tofloat16`, `floate5m2tofloate5m2` | Selects the source type and the intermediate destination type for `typeconvert`. | [`typeconvert` cases](../../../../vulkancts/modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L844-L864) |
| Layout dimensions | `1` through `32` rows and `1` through `32` columns | Exercises rectangular matrices and recomputes standard-layout strides for each size. | [layout iteration](../../../../vulkancts/modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L224-L240) |

The default mustpass list contains 144 `layoutconvert` cases and 20 `typeconvert` cases. The layout count is reduced from the apparent Cartesian product because FP8 cases cannot use row-major or column-major intermediate destinations. ([default mustpass layout cases](../../../../vulkancts/mustpass/main/vk-default/cooperative-vector.txt#L6555-L6698), [default mustpass type cases](../../../../vulkancts/mustpass/main/vk-default/cooperative-vector.txt#L53543-L53562))

## Behavior Parameters

The primary behavioral axis is the test family. The address mode and the deeper component/layout axes change how the same conversion contract is exercised; they do not change the page's two main questions.

### `layoutconvert`: preserve values while changing matrix layout

The test initializes a row-major matrix with a fixed-seed sequence of random values. For each matrix size, it creates three destination regions separated by 64-byte alignment and converts through the two registered intermediate layouts before returning to row-major storage. Standard-layout strides are rounded up to a 16-byte multiple; optimal-layout strides are zero because the Vulkan specification ignores them.

After the conversion chain, the test reads each intermediate result that has row-major or column-major layout. For a row-major result it reads element `(i, j)` from row `i`; for a column-major result it reads row `i` from column `j`. It compares floating-point values and integer values with exact equality against the source matrix. Optimal layouts are not read as ordinary arrays: the final row-major conversion supplies the readable result.

For FP8 layout cases, the API permits an FP8 destination only in an optimal layout, so registration restricts both intermediate destinations to `inferencingOptimal` or `trainingOptimal`. The final conversion uses FP16 so the result is readable in row-major storage. ([layout registration and pruning](../../../../vulkancts/modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L450-L486), [FP8 destination-layout requirement](../../../../vulkan-docs/src/chapters/shaders.adoc#L4390-L4398))

### `typeconvert`: preserve values through component quantization

The test generates a one-row matrix large enough to cover the source representation. For 8-bit and 16-bit source elements it writes every possible bit pattern. For FP32 it writes a patterned first half and seeded random values for the remainder. It first queries the required size of the inferencing-optimal destination with `dstData` unset.

The test then converts the row-major source to the selected intermediate component type in inferencing-optimal layout, and converts that result to a readable row-major destination. The final destination type is FP16 for 8-bit or 16-bit source element sizes and FP32 for a 32-bit source. For each element, the host stores the source value into a temporary object using the selected intermediate type, reads that quantized value back as the reference, and compares it with the final output. It treats two NaN values as equal. ([type conversion setup](../../../../vulkancts/modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L606-L656), [type conversion check](../../../../vulkancts/modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L819-L839))

## Shader Analysis

These tests have no shader walkthrough. Source inspection shows that `layoutconvert` and `typeconvert` call the Vulkan host or command-buffer matrix-conversion entry points directly, then inspect host-visible buffer contents. No generated GLSL, HLSL, or SPIR-V participates in the behavior being checked, so a shader walkthrough would describe a path that the tests do not execute. The source-backed exception status is recorded here; no shader artifact is invented.

## Runtime Execution and Result Checking

- The host allocates a host-visible storage buffer with transfer and shader-device-address usage. It requests cached, coherent, device-address memory first and falls back to host-visible device-address memory if the stronger allocation is unsupported.
- `layoutconvert` puts the initial matrix at offset 128. Each subsequent matrix begins at the previous region's end rounded up to a 64-byte boundary. `typeconvert` places the source at offset zero, the optimal result immediately after the source, and the final result after the queried optimal size.
- A host case sets `srcData.hostAddress` and `dstData.hostAddress` and calls `vkConvertCooperativeVectorMatrixNV` for each conversion.
- A device case sets device addresses and records `vkCmdConvertCooperativeVectorMatrixNV`. The layout family inserts a barrier after each recorded conversion. The type family inserts the barrier after the first conversion before recording the second. The barrier uses `VK_PIPELINE_STAGE_2_CONVERT_COOPERATIVE_VECTOR_MATRIX_BIT_NV` and orders transfer writes before later commands. ([device conversion and synchronization](../../../../vulkancts/modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L295-L329), [type device path](../../../../vulkancts/modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L745-L809))
- The test flushes the allocation, ends and submits the command buffer, waits for completion, invalidates the allocation, and reads the results. A mismatch sets `QP_TEST_RESULT_FAIL`; successful API calls alone do not make a case pass.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `layoutconvert` | Incorrect row/column stride or element placement; incorrect conversion to or from an implementation-dependent optimal layout; host/device conversion or synchronization failure. |
| `typeconvert` | Incorrect lower-precision encoding or rounding; unsupported component-type conversion; incorrect optimal-layout storage or final readback. |

### Cause Analysis

#### Layout conversion or synchronization

**Possible failure symptoms:** A checked row-major or column-major element differs from the source value after one of the three conversions. A device case can show the same mismatch when the recorded conversion's writes are not visible before the next operation or before host readback.

**Possible implementation causes:** The source requires the standard-layout stride to exceed the row or column length and be a multiple of the element size. It also requires 64-byte-aligned device addresses for the command form. A failure can therefore indicate incorrect interpretation of `srcLayout`, `dstLayout`, or their strides, incorrect handling of the implementation-dependent optimal layout, or a synchronization problem around `VK_PIPELINE_STAGE_2_CONVERT_COOPERATIVE_VECTOR_MATRIX_BIT_NV`. The source and specification support these as investigation areas; the test does not identify a more specific implementation location. ([layout and stride semantics](../../../../vulkan-docs/src/chapters/shaders.adoc#L4331-L4359), [device command synchronization](../../../../vulkan-docs/src/chapters/shaders.adoc#L4440-L4479))

#### Component conversion or quantized readback

**Possible failure symptoms:** One or more final FP16 or FP32 row-major values differs from the CPU value quantized to the selected intermediate type. The check accepts matching NaNs but rejects other mismatches.

**Possible implementation causes:** The conversion may have encoded a lower-precision value incorrectly, used rounding other than the specified round-to-nearest-even rule, mishandled an advertised type pair, or stored/retrieved the value incorrectly through the inferencing-optimal layout. The source and specification establish the conversion and support contract, but they do not justify assigning the fault to a particular hardware, driver, compiler, or host component without further investigation. ([type conversion semantics](../../../../vulkan-docs/src/chapters/shaders.adoc#L4361-L4398), [CPU reference comparison](../../../../vulkancts/modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L821-L839))

## Case Pruning

### Requirement-based pruning

- Both test cases require Vulkan 1.1 and the `cooperativeVector` feature.
- Both query `VkCooperativeVectorPropertiesNV` and skip a case when no cooperative-vector properties are reported or when the relevant matrix interpretation is not advertised. For `layoutconvert`, `float32` is accepted even when it is not listed; for `typeconvert`, a non-`float32` source and the intermediate destination type must be advertised, while `float32` is allowed by the API fallback.
- Standard row-major and column-major strides must satisfy the specification's size and alignment requirements. Device command addresses must be valid device addresses and 64-byte aligned. ([conversion valid usage](../../../../vulkan-docs/src/chapters/shaders.adoc#L4296-L4314), [device valid usage](../../../../vulkan-docs/src/chapters/shaders.adoc#L4461-L4479))

### Design-based pruning

- `layoutconvert` fixes the first and final layouts to row-major and selects two intermediate layouts. That shape lets the test compare readable standard layouts while still requiring a round trip through either optimal layout.
- FP8 layout cases exclude any row-major or column-major intermediate layout because the source explicitly documents that FP8 cannot be written to those destinations. The final slot uses FP16 for those cases.
- `typeconvert` fixes the source to a one-row matrix and the first conversion's destination to inferencing-optimal layout. It then fixes the final result to a row-major FP16 or FP32 matrix so the host can inspect every converted element.

## Key Takeaways

- `layoutconvert` checks logical matrix values across standard and implementation-dependent layouts; it does not assume that an optimal layout has a directly readable byte order.
- `typeconvert` checks the value produced by component quantization, so the correct reference is the CPU value encoded through the selected intermediate type.
- Host and device cases share the conversion description but use different address unions and execution paths. Device cases also depend on the conversion-stage memory dependency.
- The registered mustpass cases cover 144 layout conversions and 20 type conversions, with FP8 layout combinations deliberately restricted by the source.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Category dispatch | [`createChildren`](../../../../vulkancts/modules/vulkan/cooperative_vector/vktCooperativeVectorTests.cpp#L37-L50) | Registers the two direct families under `cooperative_vector`. |
| Layout test factory | [`createCooperativeVectorMatrixLayoutTests`](../../../../vulkancts/modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L424-L494) | Defines layout, type, address-mode, and pruning axes. |
| Layout test execution | [`CooperativeVectorLayoutTestInstance::iterate`](../../../../vulkancts/modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L165-L411) | Generates matrix bytes, performs conversions, synchronizes device work, and checks values. |
| Type test factory | [`createCooperativeVectorMatrixTypeConversionTests`](../../../../vulkancts/modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L844-L886) | Defines the ten registered type pairs and two address modes. |
| Type test execution | [`CooperativeVectorTypeConversionTestInstance::iterate`](../../../../vulkancts/modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L606-L839) | Queries optimal size, generates representations, converts data, and checks quantized values. |
| Component helpers | [`getComponentTypeInfo` and float classification](../../../../vulkancts/modules/vulkan/cooperative_vector/vktCooperativeVectorUtils.cpp#L34-L73) | Supplies component widths and identifies floating-point formats. |
| Package registration | [`cooperative_vector` root](../../../../vulkancts/modules/vulkan/vktTestPackage.cpp#L1397-L1399) | Places the category in the Vulkan test package. |
| Mustpass entries | [`cooperative-vector.txt`](../../../../vulkancts/mustpass/main/vk-default/cooperative-vector.txt#L6555-L6698) | Confirms the 144 registered layout paths. |
| Mustpass entries | [`cooperative-vector.txt`](../../../../vulkancts/mustpass/main/vk-default/cooperative-vector.txt#L53543-L53562) | Confirms the 20 registered type-conversion paths. |
| Vulkan conversion API | [`vkConvertCooperativeVectorMatrixNV`](../../../../vulkan-docs/src/chapters/shaders.adoc#L4272-L4316) and [`VkConvertCooperativeVectorMatrixInfoNV`](../../../../vulkan-docs/src/chapters/shaders.adoc#L4319-L4401) | Defines size queries, addresses, types, dimensions, layouts, strides, rounding, and valid usage. |
| Device conversion API | [`vkCmdConvertCooperativeVectorMatrixNV`](../../../../vulkan-docs/src/chapters/shaders.adoc#L4440-L4479) | Defines the device command and its conversion-stage synchronization. |
