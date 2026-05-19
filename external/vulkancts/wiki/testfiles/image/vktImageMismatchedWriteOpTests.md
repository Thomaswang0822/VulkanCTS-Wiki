# [vktImageMismatchedWriteOpTests.cpp](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L1)

## Overview

[`vktImageMismatchedWriteOpTests.cpp`](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L1) is an implementation-heavy Level-3 file for the `image.mismatched_write_op` subtree. It covers Vulkan [`OpImageWrite`](https://registry.khronos.org/SPIR-V/specs/unified1/OpenGL.html OpImageWrite) operations where the source data has a different vector size or signedness/type than the target image format. The tests validate that implementations correctly handle these mismatched write scenarios and produce expected results.

## Role of File

- **Role:** implementation-heavy test file.
- **Primary source:** [`vktImageMismatchedWriteOpTests.cpp`](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L1).
- **Registration context inspected:**
  - [`vktImageTests.cpp`](../../../modules/vulkan/image/vktImageTests.cpp) for placement under the top-level `image` category.
  - [`createImageWriteOpTests()`](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L1065-L1127) for the Level-3 root `image.mismatched_write_op` and its exact direct children.

## Source Code

- Implementation: [vktImageMismatchedWriteOpTests.cpp](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L1)
- Header: [vktImageMismatchedWriteOpTests.hpp](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.hpp#L1)
- Parent registration: [vktImageTests.cpp](../../../modules/vulkan/image/vktImageTests.cpp)

## Registration Hierarchy

```text
image.mismatched_write_op
├── mismatched_vector_sizes
└── mismatched_signedness_and_type
```

The confirmed Level-3 root is `image.mismatched_write_op`, created by [`createImageWriteOpTests()`](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L1065-L1127). The exact direct children are `mismatched_vector_sizes` and `mismatched_signedness_and_type`.

## Test Families

### mismatched_vector_sizes �?OpImageWrite with mismatched vector component counts

Covers the `mismatched_vector_sizes` direct child registered by [`createImageWriteOpTests()``](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L1084). This group tests scenarios where data is written to an image using a vector with fewer components than the image format expects.

The [`MismatchedVectorSizesTest`](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L87-L104) class generates SPIR-V assembly shaders that construct vectors of various sizes (scalar, vec2, vec3, vec4, vec5) and write them to images with different format requirements.

Test cases are generated for all formats in [`allFormats[]`](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L459-L502) with vector source widths from 1 to 5 (or 4 for VulkanSC), where the source width is greater than or equal to the format's channel count.

### mismatched_signedness_and_type �?OpImageWrite with mismatched signedness and type

Covers the `mismatched_signedness_and_type` direct child registered by [`createImageWriteOpTests()``](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L1085). This group tests scenarios where source data has different signedness or numeric type than the target image format.

The [`MismatchedSignednessAndTypeTest`](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L106-L116) class generates test cases that write data between formats within the same channel class (e.g., float-to-float, uint-to-uint, sint-to-sint) but potentially with different bit depths or specific format variants.

## Parameter Dimensions

| Dimension | Observed values / construction | Evidence |
|---|---|---|
| Level-3 direct children | `mismatched_vector_sizes`, `mismatched_signedness_and_type` | [`createImageWriteOpTests()``](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L1082-L1085) |
| Formats tested | 45 formats across float, unorm, snorm, sint, uint, and 64-bit variants | [`allFormats[]`](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L459-L502) |
| Vector source widths | 1 (scalar), 2 (vec2), 3 (vec3), 4 (vec4), 5 (vec5) | [`sourceWidth loop`](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L1111-L1120) |
| Texture dimensions | Width varies by test case (12 to 60 pixels), Height varies (8 to 40 pixels) | [`Params`](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L61-L67), generated per format combination |
| Image type | 2D only | [`VK_IMAGE_TYPE_2D`](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L281) |
| Image usage | `VK_IMAGE_USAGE_STORAGE_BIT`, `VK_IMAGE_USAGE_TRANSFER_SRC_BIT`, `VK_IMAGE_USAGE_TRANSFER_DST_BIT` | [`StorageImage2D`](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L274-L275) |
| Channel classes | Floating-point, signed integer, unsigned integer, signed fixed-point, unsigned fixed-point | [`findFormatsByChannelClass()``](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L504-L514) |
| Buffer types | vec4, ivec4, uvec4, dvec4 (for 64-bit formats) | [`makeBufferFormat()``](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L556-L559) |
| 64-bit integer formats | `VK_FORMAT_R64_SINT`, `VK_FORMAT_R64_UINT` | [`allFormats[]`](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L500-L501) |
| Vector size limit | 5 (Vulkan), 4 (VulkanSC) due to longVector feature | [`largestWidth`](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L1107-L1110) |

## Support / Feature Requirements

Observed support gates and extension-dependent coverage include:

| Feature / Extension | When it applies | Evidence |
|---|---|---|
| `shaderInt64` | Required for 64-bit integer formats | [`checkSupport()``](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L566-L571) |
| `VK_EXT_shader_image_atomic_int64` | Required for 64-bit integer format operations | [`checkSupport()``](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L572-L573) |
| `VK_KHR_variable_pointers` | Required for all tests | [`checkSupport()``](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L576) |
| `VK_KHR_storage_buffer_storage_class` | Required for all tests | [`checkSupport()``](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L577) |
| `longVector` feature (EXT) | Required for sourceWidth == 5 tests | [`checkSupport()``](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L785-L788) |
| `SPV_EXT_shader_image_int64` | Required for 64-bit integer SPIR-V operations | [`getProgramCodeAndVariables()``](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L756-L759) |
| `SPV_EXT_long_vector` | Required for 5-component vector tests | [`getProgramCodeAndVariables()``](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L761-L769) |
| `VK_FORMAT_FEATURE_STORAGE_IMAGE_BIT` | Required for all tests | [`checkSupport()``](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L582-L585) |
| Transfer support | Required for upload/download operations | [`checkSupport()``](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L587-L591) |

## Verification Methods

- **Pixel comparison for mismatched_vector_sizes:** The [`MismatchedVectorSizesTestInstance::compare()``](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L1025-L1053) function compares only the components used by the image format, using integer threshold comparison for integer formats and epsilon comparison (0.0005f) for floating-point formats.
- **Data round-trip verification:** Tests upload source data to an image, execute a compute shader that reads and re-writes the data, then download and compare against the original source.
- **Epsilon-based float comparison:** Floating-point comparisons use `EPSILON_COMPARE` with a small epsilon value.
- **Integer threshold comparison:** Integer formats compare with a threshold of 0 (exact match).

## Test Principles Observed

- **Vector size mismatch tests write smaller vectors to larger-format images.** For example, writing a scalar or vec2 to an RGBA format image. The missing components are implicitly filled or zero-initialized by the SPIR-V implementation.
- **Signedness tests operate within the same channel class.** Tests verify behavior when writing between formats that share the same channel class (e.g., different float formats, different uint formats) rather than across classes.
- **SPIR-V is generated directly rather than using GLSL.** Tests use hand-written SPIR-V assembly with [`StringTemplate`](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L602-L779) to precisely control vector construction and OpImageWrite operations.
- **64-bit formats use different buffer representations.** When `is64BitIntegerFormat()` is true, the buffer format uses 64-bit channel types (slong/ulong/double).
- **Image dimensions vary based on source width.** The texture height is calculated as `8 * (6 - sourceWidth + 1)` to ensure the test covers various texel patterns within the allocated buffer space.
- **Data patterns avoid overflow during testing.** The `populate()` function uses incremental patterns that wrap around within the format's valid range rather than hitting maximum/minimum values that could cause overflow confusion.

## Notes / Uncertainties

- The `mismatched_signedness_and_type` tests use a `compare()` function that always returns `true`, indicating these tests may verify shader compilation and execution rather than specific numeric results.
- The 64-bit integer format loop in `mismatched_vector_sizes` explicitly skips tests when either the target format or source width involves 64-bit integers (lines 1096-1097).
- For VulkanSC, the maximum vector width is limited to 4 instead of 5, reflecting the lack of `longVector` feature support in that context.
- Tests use storage buffers rather than push constants to provide source data to the shader, enabling larger test data sets.
