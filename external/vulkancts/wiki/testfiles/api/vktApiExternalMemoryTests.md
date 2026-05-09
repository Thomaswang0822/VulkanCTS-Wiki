# [vktApiExternalMemoryTests.cpp](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L1)

## Overview

Tests Vulkan external memory, semaphore, and fence sharing across process and API boundaries. The file validates that external handles (FD, Win32, Android Hardware Buffer, Zircon, Metal) can be exported, imported, and used correctly for semaphores, fences, and device memory objects.

## Role of File

Implementation-heavy. Contains all test logic, helper utilities, and registration in a single large source file (~5610 lines). The public entry point [createExternalMemoryTests()](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5598) assembles the full test tree.

## Source Code

- Source: [vktApiExternalMemoryTests.cpp](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L1)
- Header: [vktApiExternalMemoryTests.hpp](../../../modules/vulkan/api/vktApiExternalMemoryTests.hpp#L1)
- Parent registration: [vktApiTests.cpp](../../../modules/vulkan/api/vktApiTests.cpp#L117) adds `external` group to `api`

## Registration Hierarchy

```text
api.external
├── semaphore
├── memory
└── fence
```

The Level-3 root is the `external` subgroup registered by [createExternalMemoryTests()](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5598-L5606). Its exact direct child groups are `semaphore`, `memory`, and `fence`, registered by [createSemaphoreTests()](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5390-L5406), [createMemoryTests()](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5578-L5593), and [createFenceTests()](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5276-L5289).

## Test Families

### semaphore — External semaphore sharing

Tests external semaphore handle export, import, and synchronization. The direct child group is registered by [createSemaphoreTests()](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5390-L5406), which expands into handle-type subgroups such as `sync_fd`, `opaque_fd`, `opaque_win32`, `opaque_win32_kmt`, and `zircon_event`. Within each handle-type subgroup, the file generates binary and timeline property queries plus temporary and permanent import/export flows including reimport, repeated import, transference, and handle-type-specific cases such as sync-FD signaled import, FD duplication/socket transfer, reference-transference signal/wait flows, and Win32 creation paths as shown in [createSemaphoreTests()](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5291-L5387).

### memory — External device-memory sharing

Tests external memory handle export, import, and binding. The direct child group is registered by [createMemoryTests()](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5578-L5593), which expands into handle-type subgroups `opaque_fd`, `opaque_win32`, `opaque_win32_kmt`, `android_hardware_buffer`, `dma_buf`, `zircon_vmo`, `mtlbuffer`, and `mtltexture`. Each handle-type subgroup then registers `suballocated` and `dedicated` branches with `host_visible` and `device_only` visibility modes plus `buffer` and `image` binding/query groups in [createMemoryTests()](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5409-L5575). The Android Hardware Buffer branch additionally registers `ahb_format_properties` and `ahb_format_properties_2`, each containing `image_formats` and `external_format_resolve` subgroups in [vktApiExternalMemoryTests.cpp](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5503-L5572).

### fence — External fence sharing

Tests external fence handle export, import, and synchronization. The direct child group is registered by [createFenceTests()](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5276-L5289), which expands into handle-type subgroups `sync_fd`, `opaque_fd`, `opaque_win32`, and `opaque_win32_kmt`. Each handle-type subgroup then generates info, import/reimport, signal-export-import-wait, reset, transference, repeated export/import, FD duplication/socket transfer, and Win32-specific creation coverage in [createFenceTests()](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5192-L5274).

## Parameter Dimensions

| Dimension | Observed Values |
|---|---|
| Handle Type - Semaphore | sync_fd, opaque_fd, opaque_win32, opaque_win32_kmt, zircon_event |
| Handle Type - Memory | opaque_fd, opaque_win32, opaque_win32_kmt, android_hardware_buffer, dma_buf, zircon_vmo, mtlbuffer, mtltexture |
| Handle Type - Fence | sync_fd, opaque_fd, opaque_win32, opaque_win32_kmt |
| Permanence | temporary, permanent |
| Semaphore Type | binary, timeline |
| Allocation Mode | suballocated, dedicated |
| Memory Visibility | host_visible, device_only |
| Resource Type | buffer, image |
| AHB Format | R8G8B8_UNORM, R8G8B8A8_UNORM, R5G6B5_UNORM_PACK16, R16G16B16A16_SFLOAT, A2B10G10R10_UNORM_PACK32, D16_UNORM, X8_D24_UNORM_PACK32, D24_UNORM_S8_UINT, D32_SFLOAT, D32_SFLOAT_S8_UINT, S8_UINT, R8_UNORM, R16_UINT, R16G16_UINT, R10X6G10X6B10X6A10X6_UNORM_4PACK16 |

## Support / Feature Requirements

- Platform-specific extensions required per handle type (e.g., `VK_KHR_external_semaphore_fd`, `VK_KHR_external_memory_win32`, `VK_ANDROID_external_memory_android_hardware_buffer`)
- `VK_KHR_maintenance5` required for maintenance5 buffer query tests ([checkMaintenance5()](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5263))
- `VK_KHR_dedicated_allocation` required for dedicated allocation tests
- `VK_KHR_sampler_ycbcr_conversion` and `VK_EXT_queue_family_foreign` required for AHB tests
- Custom instance/device creation with required extensions ([createTestInstance()](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L198))

## Verification Methods

- Semaphore: Signal-export-import-wait round-trip verification; transference mode checks (copy vs reference)
- Fence: Signal-export-import-wait round-trip; fence reset verification; FD duplication and socket transfer verification
- Memory: Host-visible memory content comparison via [writeHostMemory()](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L121) and [checkHostMemory()](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L133); buffer/image binding state verification after export-import
- AHB: Format property query validation; external format resolve draw support check

## Test Principles Observed

- Platform-conditional compilation (FD-based tests on Unix/Android, Win32 handles on Windows, Zircon on Fuchsia, Metal on Apple)
- Support queries before each test
- Custom instance/device creation with required extensions
- Random test data generation via [genTestData()](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L146)

## Notes / Uncertainties

- The file is very large (~5610 lines) and covers three distinct Vulkan object types (semaphore, memory, fence) that could arguably be separate files
- FD-based tests use compute shaders to ensure sufficient execution time for valid FD export
- AHB external format resolve tests use a custom TestCase/TestInstance subclass pair rather than the function-case pattern used elsewhere
- The `createMemoryTests` overload without handle-type argument creates the parent `memory` group containing all handle-type subgroups ([createMemoryTests()](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5578-L5593))
- The group name is `external` as confirmed in [createExternalMemoryTests()](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5600), not `external_memory`
