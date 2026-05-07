# [vktApiBufferViewAccessTests.cpp](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1)

## Overview

[`vktApiBufferViewAccessTests.cpp`](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1) implements the `api/buffer_view/access` subgroup. It is registered as a child of the `buffer_view` group in [`createBufferViewTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L78). The file tests buffer view data access through both graphics and compute pipelines, verifying that texel reads from buffer views produce correct values. It also includes all-format coverage tests using compute shaders.

## Role of File

Implementation-heavy test file for the `api/buffer_view/access` subgroup.

## Source Code

- Primary source: [vktApiBufferViewAccessTests.cpp](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1)
- Header: [vktApiBufferViewAccessTests.hpp](../../../modules/vulkan/api/vktApiBufferViewAccessTests.hpp#L1)
- Parent-category registration: [`createBufferViewTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L78) which is called from [`createApiTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L106) via `createTestGroup(testCtx, "buffer_view", createBufferViewTests)`

## Registration Path

```text
TestPackage::init / TestPackageSC::init
  api
  +-- createApiTests(apiTests)
      +-- createTestGroup(testCtx, "buffer_view", createBufferViewTests)
          +-- buffer_view
              +-- access/
                  +-- suballocation/
                  +-- dedicated_alloc/
                  +-- uniform_texel_buffer/
                  +-- storage_texel_buffer/
                  +-- uniform_storage_texel_buffer/  (not in Vulkan SC)
```

Evidence:
- `buffer_view` group created at [`createApiTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L106)
- `access` subgroup created at [`createBufferViewAccessTests()`](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1443)
- suballocation and dedicated_alloc subgroups at [`vktApiBufferViewAccessTests.cpp`](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1444)

## Test Hierarchy

```text
api
+-- buffer_view
    +-- access/
        +-- suballocation/
            +-- buffer_view_memory_test_complete_graphics
            +-- buffer_view_memory_test_complete_compute
            +-- buffer_view_memory_test_partial_offset0_graphics
            +-- buffer_view_memory_test_partial_offset0_compute
            +-- buffer_view_memory_test_partial_offset1_graphics
            +-- buffer_view_memory_test_partial_offset1_compute
        +-- dedicated_alloc/
            +-- buffer_view_memory_test_complete_with_buffer_dedicated_alloc_image_suballocated_graphics
            +-- ... (all buffer/image allocation and queue type combinations)
        +-- uniform_texel_buffer/
            +-- (per-format test cases)
        +-- storage_texel_buffer/
            +-- (per-format test cases)
        +-- uniform_storage_texel_buffer/  (excluded for Vulkan SC)
            +-- bind_as_uniform/
                +-- (per-format test cases)
            +-- bind_as_storage/
                +-- (per-format test cases)
```

Source: [`createBufferViewAccessTests()`](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1435).

## Test Families

### 1. Buffer view memory access through graphics and compute pipelines

The `suballocation` and `dedicated_alloc` subgroups at [`vktApiBufferViewAccessTests.cpp`](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1444) test buffer view data access. Each test case is parameterized by:

- buffer allocation kind (suballocated or dedicated)
- image allocation kind (suballocated or dedicated)
- queue type (graphics or compute)

Three test configurations are generated per combination at [`vktApiBufferViewAccessTests.cpp`](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1457):

- `buffer_view_memory_test_complete`: buffer size equals view size (512 elements)
- `buffer_view_memory_test_partial_offset0`: buffer is larger (4096 elements), view starts at offset 0
- `buffer_view_memory_test_partial_offset1`: buffer is larger (4096 elements), view starts at offset 128

[`BufferViewTestInstance`](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L106) extends [`MultiQueueRunnerTestInstance`](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L106) and uses either a graphics pipeline (vertex + fragment shader) or a compute pipeline to read from the buffer view and write results to an image, then copies the image to a host-visible buffer for verification.

### 2. All-format buffer view access tests

The `uniform_texel_buffer` and `storage_texel_buffer` subgroups at [`vktApiBufferViewAccessTests.cpp`](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1508) test buffer view access for a wide range of formats using compute shaders. [`BufferViewAllFormatsTestInstance`](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L864) populates a source buffer with a gradient pattern via [`populateSourceBuffer()`](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L938), then uses a compute shader to read from the buffer view at four sample positions and writes the results to a storage buffer for comparison.

### 3. Uniform-storage texel buffer dual-usage tests

The `uniform_storage_texel_buffer` subgroup at [`vktApiBufferViewAccessTests.cpp`](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1554) (excluded for Vulkan SC) tests buffers created with both `VK_BUFFER_USAGE_UNIFORM_TEXEL_BUFFER_BIT` and `VK_BUFFER_USAGE_STORAGE_TEXEL_BUFFER_BIT`, then bound as either uniform or storage texel buffer. This tests `VK_KHR_maintenance5` functionality where the bind usage may differ from the create usage via [`VkBufferUsageFlags2CreateInfoKHR`](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1039).

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Buffer allocation kind | `ALLOCATION_KIND_SUBALLOCATION`, `ALLOCATION_KIND_DEDICATED` in [`AllocationKind`](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L62) |
| Image allocation kind | `ALLOCATION_KIND_SUBALLOCATION`, `ALLOCATION_KIND_DEDICATED` at [`vktApiBufferViewAccessTests.cpp`](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1444) |
| Queue type | graphics, compute at [`vktApiBufferViewAccessTests.cpp`](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1441) |
| Buffer/view size combinations | complete (512/512), partial_offset0 (4096/512), partial_offset1 (4096/512 with offset 128) at [`vktApiBufferViewAccessTests.cpp`](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1457) |
| Texel buffer usage | uniform, storage at [`vktApiBufferViewAccessTests.cpp`](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1508) |
| Format list | `formats::bufferViewAccessFormats` at [`vktApiBufferViewAccessTests.cpp`](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1522) |
| Dual-usage bind mode | bind_as_uniform, bind_as_storage at [`vktApiBufferViewAccessTests.cpp`](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1558) |

## Support / Feature Requirements

- format support is checked via [`BufferViewAllFormatsTestCase::checkSupport()`](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1289), which verifies `VK_FORMAT_FEATURE_STORAGE_TEXEL_BUFFER_BIT` for storage cases
- `VK_KHR_maintenance5` is required for dual-usage bind tests at [`vktApiBufferViewAccessTests.cpp`](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L928)
- `VK_FORMAT_A8_UNORM_KHR` and `VK_FORMAT_A1B5G5R5_UNORM_PACK16_KHR` require `VK_KHR_maintenance5` at [`vktApiBufferViewAccessTests.cpp`](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1296)
- `uniform_storage_texel_buffer` subgroup is excluded for Vulkan SC at [`vktApiBufferViewAccessTests.cpp`](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1553)

## Verification Methods

- graphics pipeline tests render a full-screen quad using the buffer view in the fragment shader, copy the result to a buffer, and compare pixel values against expected values in [`BufferViewTestInstance::checkResult()`](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L591)
- compute pipeline tests dispatch a compute shader that reads from the buffer view and writes to a storage image, then copies to a buffer for comparison
- all-format tests use [`BufferViewAllFormatsTestInstance::checkResult()`](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1193) for integer formats and [`checkResultFloat()`](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1227) for floating-point formats, comparing against source buffer data with appropriate thresholds
- the test runs twice with different data factors (1 and 2) to verify that buffer view contents update correctly at [`vktApiBufferViewAccessTests.cpp`](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L793)

## Test Principles Observed

- Test both graphics and compute pipeline access paths for buffer views
- Cover complete and partial buffer view configurations with different offsets
- Verify data correctness by comparing shader output against known input data
- Test dual-usage buffers that can be bound as either uniform or storage texel buffer
- Use multiple data passes to verify that buffer view contents update correctly

## Notes / Uncertainties

- The `isSupportedImageLoadStore()` function at [`vktApiBufferViewAccessTests.cpp`](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1383) filters out formats that cannot be used with `imageLoad`/`imageStore` in the storage texel buffer cases; the exact set of supported formats depends on the format's texture format order and type.
- The `formats::bufferViewAccessFormats` list used for all-format tests is defined in [`vkFormatLists.hpp`](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L41) and was not inspected.
- The `MultiQueueRunnerTestInstance` base class is used for the graphics/compute pipeline tests; its implementation details are not inspected here.
