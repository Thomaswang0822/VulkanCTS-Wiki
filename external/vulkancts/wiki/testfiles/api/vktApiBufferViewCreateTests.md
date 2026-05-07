# [vktApiBufferViewCreateTests.cpp](../../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L1)

## Overview

[`vktApiBufferViewCreateTests.cpp`](../../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L1) implements the `api/buffer_view/create` subgroup. It is registered as a child of the `buffer_view` group in [`createBufferViewTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L78). The file tests buffer view creation for all core Vulkan formats under both uniform and storage texel buffer usage, with both suballocated and dedicated allocation strategies.

## Role of File

Implementation-heavy test file for the `api/buffer_view/create` subgroup.

## Source Code

- Primary source: [vktApiBufferViewCreateTests.cpp](../../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L1)
- Header: [vktApiBufferViewCreateTests.hpp](../../../modules/vulkan/api/vktApiBufferViewCreateTests.hpp#L1)
- Parent-category registration: [`createBufferViewTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L78) which is called from [`createApiTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L106) via `createTestGroup(testCtx, "buffer_view", createBufferViewTests)`

## Registration Path

```text
TestPackage::init / TestPackageSC::init
  api
  +-- createApiTests(apiTests)
      +-- createTestGroup(testCtx, "buffer_view", createBufferViewTests)
          +-- buffer_view
              +-- create/
                  +-- suballocation/
                  +-- dedicated_alloc/
```

Evidence:
- `buffer_view` group created at [`createApiTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L106)
- `create` subgroup created at [`createBufferViewCreateTests()`](../../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L399)
- suballocation and dedicated_alloc subgroups created at [`vktApiBufferViewCreateTests.cpp`](../../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L404)

## Test Hierarchy

```text
api
+-- buffer_view
    +-- create/
        +-- suballocation/
            +-- uniform/
                +-- (per-core-format test cases)
            +-- storage/
                +-- (per-core-format test cases)
        +-- dedicated_alloc/
            +-- uniform/
                +-- (per-core-format test cases)
            +-- storage/
                +-- (per-core-format test cases)
```

Source: [`createBufferViewCreateTests()`](../../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L390).

## Test Families

### 1. Buffer view creation across formats and allocation strategies

[`createBufferViewCreateTests()`](../../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L390) creates a `create` group with two allocation-strategy subgroups: `suballocation` at [`vktApiBufferViewCreateTests.cpp`](../../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L406) and `dedicated_alloc` at [`vktApiBufferViewCreateTests.cpp`](../../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L408). Within each, two usage subgroups are created: `uniform` and `storage` at [`vktApiBufferViewCreateTests.cpp`](../../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L413). Each usage subgroup iterates over all core Vulkan formats from `VK_FORMAT_UNDEFINED + 1` through `VK_CORE_FORMAT_LAST` at [`vktApiBufferViewCreateTests.cpp`](../../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L415).

Each test case creates a buffer, allocates memory, and creates a buffer view with the specified format, offset, and range. The test also creates a second "complete" buffer view spanning the entire buffer at [`vktApiBufferViewCreateTests.cpp`](../../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L363).

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Allocation kind | `ALLOCATION_KIND_SUBALLOCATED`, `ALLOCATION_KIND_DEDICATED` in [`AllocationKind`](../../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L47) |
| Usage type | `VK_BUFFER_USAGE_UNIFORM_TEXEL_BUFFER_BIT`, `VK_BUFFER_USAGE_STORAGE_TEXEL_BUFFER_BIT` at [`vktApiBufferViewCreateTests.cpp`](../../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L393) |
| Format range | `VK_FORMAT_UNDEFINED + 1` through `VK_CORE_FORMAT_LAST` at [`vktApiBufferViewCreateTests.cpp`](../../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L415) |
| Buffer view range | `VK_WHOLE_SIZE` at [`vktApiBufferViewCreateTests.cpp`](../../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L392) |
| Buffer size | `3 * 5 * 7 * 64` bytes at [`vktApiBufferViewCreateTests.cpp`](../../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L323) |

## Support / Feature Requirements

- each test case checks format support via [`BufferViewTestCase::checkSupport()`](../../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L120), which verifies that the format supports the required buffer feature flag
- dedicated allocation cases require `VK_KHR_dedicated_allocation` at [`vktApiBufferViewCreateTests.cpp`](../../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L130)

## Verification Methods

- buffer view creation tests verify that `vkCreateBufferView` succeeds without throwing an error at [`vktApiBufferViewCreateTests.cpp`](../../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L352)
- buffer creation and memory allocation are verified to succeed at [`vktApiBufferViewCreateTests.cpp`](../../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L159)
- memory requirement size is verified to be at least as large as the requested buffer size at [`vktApiBufferViewCreateTests.cpp`](../../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L172)

## Test Principles Observed

- Systematic format coverage across all core Vulkan formats
- Both uniform and storage texel buffer usage are tested
- Both suballocated and dedicated allocation strategies are covered
- Format support is checked before testing to skip unsupported formats

## Notes / Uncertainties

- The test creates a buffer of size `3 * 5 * 7 * 64` bytes but uses `VK_WHOLE_SIZE` as the buffer view range at [`vktApiBufferViewCreateTests.cpp`](../../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L392), so the view covers the entire buffer.
- The "complete" buffer view created at [`vktApiBufferViewCreateTests.cpp`](../../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L363) uses the actual buffer size rather than `VK_WHOLE_SIZE`, providing an alternative creation path.
