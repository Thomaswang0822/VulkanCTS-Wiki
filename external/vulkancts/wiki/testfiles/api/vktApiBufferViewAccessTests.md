# [vktApiBufferViewAccessTests.cpp](../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1)

## Overview

Tests Vulkan buffer view creation and data access through both graphics and compute pipelines. Validates that texel buffer data read through a `VkBufferView` produces correct values, covering various buffer sizes, view offsets, allocation strategies (suballocation vs. dedicated), and a wide range of texel buffer formats.

## Role of File

Implementation-heavy. Contains two test instance classes (`BufferViewTestInstance` and `BufferViewAllFormatsTestInstance`), their corresponding test case classes, shader program generation, and the test group construction via `createBufferViewAccessTests()`.

## Source Code

- Implementation: [vktApiBufferViewAccessTests.cpp](../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1)
- Header: [vktApiBufferViewAccessTests.hpp](../../modules/vulkan/api/vktApiBufferViewAccessTests.hpp#L1)
- Parent registration: `vktApiTests.cpp` creates an aggregator group `buffer_view` via `createBufferViewTests()`, which includes this file's `createBufferViewAccessTests()` as the `access` subgroup.

## Registration Path

```
api
  +-- buffer_view
        +-- access
              +-- suballocation
              |     +-- buffer_view_memory_test_complete_graphics
              |     +-- buffer_view_memory_test_complete_compute
              |     +-- buffer_view_memory_test_partial_offset0_graphics
              |     +-- buffer_view_memory_test_partial_offset0_compute
              |     +-- buffer_view_memory_test_partial_offset1_graphics
              |     +-- buffer_view_memory_test_partial_offset1_compute
              +-- dedicated_alloc
              |     +-- ... (same test patterns with dedicated allocation variants)
              +-- uniform_texel_buffer
              |     +-- <format_name>
              +-- storage_texel_buffer
              |     +-- <format_name>
              +-- uniform_storage_texel_buffer  (non-VKSC only)
                    +-- bind_as_uniform
                    |     +-- <format_name>
                    +-- bind_as_storage
                          +-- <format_name>
```

## Test Hierarchy

```
access
  +-- suballocation
  |     +-- buffer_view_memory_test_complete_<queue>
  |     +-- buffer_view_memory_test_partial_offset0_<queue>
  |     +-- buffer_view_memory_test_partial_offset1_<queue>
  +-- dedicated_alloc
  |     +-- buffer_view_memory_test_complete_with_<bufAlloc>_<imgAlloc>_<queue>
  |     +-- buffer_view_memory_test_partial_offset0_with_<bufAlloc>_<imgAlloc>_<queue>
  |     +-- buffer_view_memory_test_partial_offset1_with_<bufAlloc>_<imgAlloc>_<queue>
  +-- uniform_texel_buffer
  |     +-- <format>  (per format from bufferViewAccessFormats list)
  +-- storage_texel_buffer
  |     +-- <format>  (filtered by isSupportedImageLoadStore)
  +-- uniform_storage_texel_buffer  (non-VKSC only)
        +-- bind_as_uniform
        |     +-- <format>
        +-- bind_as_storage
              +-- <format>
```

## Test Families

### BufferView Memory Tests ([L105](../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L105))

`BufferViewTestInstance` creates a buffer with uniform texel data, creates a `VkBufferView` over it, and reads the data through either a graphics or compute pipeline. Three test configurations cover:
- **complete**: bufferSize=512, bufferViewSize=512, elementOffset=0 ([L1457](../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1457))
- **partial_offset0**: bufferSize=4096, bufferViewSize=512, elementOffset=0 ([L1472](../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1472))
- **partial_offset1**: bufferSize=4096, bufferViewSize=512, elementOffset=128 ([L1487](../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1487))

Each test runs twice with different data (factor=1 and factor=2) to verify buffer view data updates are visible ([L783](../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L783)). Uses `MultiQueueRunnerTestInstance` for queue selection.

### BufferView All Formats Tests ([L864](../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L864))

`BufferViewAllFormatsTestInstance` tests texel buffer access across a comprehensive list of formats from `formats::bufferViewAccessFormats`. Uses a compute pipeline to read 4 sample positions from the buffer view and writes results to a storage buffer. Verifies results against the source data with integer-exact comparison for int/uint formats and 1/255 tolerance for float formats ([L1227](../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1227)).

Three usage mode groups:
- **uniform_texel_buffer**: Buffer created with `VK_BUFFER_USAGE_UNIFORM_TEXEL_BUFFER_BIT`, read via `texelFetch` ([L1508](../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1508))
- **storage_texel_buffer**: Buffer created with `VK_BUFFER_USAGE_STORAGE_TEXEL_BUFFER_BIT`, read via `imageLoad` (filtered by [isSupportedImageLoadStore](../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1383)) ([L1509](../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1509))
- **uniform_storage_texel_buffer** (non-VKSC): Buffer created with both uniform and storage texel buffer usage, then bound as either uniform or storage via `VkBufferUsageFlags2CreateInfoKHR` (VK_KHR_maintenance5) ([L1554](../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1554))

## Parameter Dimensions

| Dimension | Values | Notes |
|---|---|---|
| Buffer allocation kind | suballocation, dedicated_alloc | Controls buffer memory allocation strategy |
| Image allocation kind | suballocation, dedicated_alloc | Controls color image memory allocation strategy |
| Pipeline type | graphics, compute | Graphics uses fragment shader; compute uses compute shader |
| Buffer size | 512, 4096 | Total buffer size in uint32 elements |
| Buffer view size | 512, 128 | View range in uint32 elements |
| Element offset | 0, 128 | View offset in uint32 elements |
| Texel buffer format | ~80+ formats from bufferViewAccessFormats | Includes R4G4 through R64G64B64A64 formats |
| Usage mode | uniform_texel_buffer, storage_texel_buffer, uniform_storage_texel_buffer | Determines create/bind usage flags and descriptor type |

## Support / Feature Requirements

| Requirement | Gate | Source |
|---|---|---|
| VK_KHR_dedicated_allocation | Required for dedicated allocation tests | Checked via [BufferDedicatedAllocation](../../modules/vulkan/api/vktApiBufferAndImageAllocationUtil.cpp#L70) |
| VK_KHR_maintenance5 | Required for bind_as_uniform / bind_as_storage sub-groups | [L928](../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L928) |
| VK_FORMAT_FEATURE_UNIFORM_TEXEL_BUFFER_BIT | Required for uniform texel buffer formats | [L921](../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L921) |
| VK_FORMAT_FEATURE_STORAGE_TEXEL_BUFFER_BIT | Required for storage texel buffer formats | [L1303](../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1303) |
| VK_KHR_maintenance5 (for A8_UNORM, A1B5G5R5) | Required for specific format support | [L1296](../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1296) |

## Verification Methods

- **BufferView Memory Tests**: After rendering/dispatching, the color image is copied to a host-visible result buffer. Pixel values at diagonal positions (i, i) are compared against `factor * (elementOffset + i)` ([L610](../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L610)). The test runs twice with different factors to verify data updates.
- **All Formats Tests**: A compute shader reads 4 fixed sample positions (6, 51, 42, 25) from the texel buffer and writes results to a storage buffer. For integer/unsigned formats, results must match exactly ([L1193](../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1193)); for float formats, tolerance is 1/255 ([L1227](../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1227)).

## Test Principles Observed

- **Format coverage**: Tests a comprehensive list of texel buffer formats covering UNORM, SNORM, UINT, SINT, USCALED, SSCALED, SFLOAT, and packed formats.
- **Allocation strategy coverage**: Tests both suballocated and dedicated allocation for buffers and images independently.
- **Offset and partial view coverage**: Tests buffer views that span the entire buffer and partial views with non-zero offsets.
- **Pipeline coverage**: Tests texel buffer reads through both graphics (fragment shader) and compute pipelines.
- **VK_KHR_maintenance5 coverage**: Tests the ability to create a buffer with combined usage flags and bind it as a different usage type via `VkBufferUsageFlags2CreateInfoKHR`.

## Notes / Uncertainties

- The `BufferViewTestInstance` extends `MultiQueueRunnerTestInstance` rather than the standard `TestInstance`, which enables queue-specific test execution ([L105](../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L105)).
- The `isSupportedImageLoadStore` function ([L1383](../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1383)) filters out formats that cannot be used with `imageLoad` in storage texel buffer mode, which is a subset of all formats.
- The `uniform_storage_texel_buffer` group is excluded on VKSC builds ([L1553](../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1553)).
- The source buffer data generation in `populateSourceBuffer` ([L938](../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L938)) uses a gradient/M-pattern/triangle-wave pattern designed to detect both large offset errors and small alignment errors.
- The `bufferViewAccessFormats` list is defined in the generated file `vkFormatLists.inl` and contains approximately 80+ formats.
