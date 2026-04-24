# [vktApiExternalMemoryTests.cpp](../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L1)

## Overview

Tests Vulkan external memory, semaphore, and fence sharing across process and API boundaries. The file validates that external handles (FD, Win32, Android Hardware Buffer, Zircon, Metal) can be exported, imported, and used correctly for semaphores, fences, and device memory objects.

## Role of File

Implementation-heavy. Contains all test logic, helper utilities, and registration in a single large source file (~5610 lines). The public entry point [createExternalMemoryTests()](../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5598) assembles the full test tree.

## Source Code

- Source: [vktApiExternalMemoryTests.cpp](../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L1)
- Header: [vktApiExternalMemoryTests.hpp](../../modules/vulkan/api/vktApiExternalMemoryTests.hpp#L1)
- Parent registration: `api` test group, child `external_memory` (non-VKSC only)

## Registration Path

```
api
 +-- external_memory
      +-- semaphore
      |    +-- sync_fd
      |    +-- opaque_fd
      |    +-- opaque_win32
      |    +-- opaque_win32_kmt
      |    +-- zircon_event
      +-- memory
      |    +-- opaque_fd
      |    +-- opaque_win32
      |    +-- opaque_win32_kmt
      |    +-- android_hardware_buffer
      |    +-- dma_buf
      |    +-- zircon_vmo
      |    +-- mtlbuffer
      |    +-- mtltexture
      +-- fence
           +-- sync_fd
           +-- opaque_fd
           +-- opaque_win32
           +-- opaque_win32_kmt
```

## Test Hierarchy

```
external_memory
 +-- semaphore
 |    +-- <handle_type>              (sync_fd, opaque_fd, opaque_win32, opaque_win32_kmt, zircon_event)
 |         +-- info_binary           -- query external semaphore properties
 |         +-- info_timeline         -- query external timeline semaphore properties
 |         +-- import_twice_temporary / permanent
 |         +-- reimport_temporary / permanent
 |         +-- import_multiple_times_temporary / permanent
 |         +-- signal_export_import_wait_temporary / permanent
 |         +-- signal_import_temporary / permanent
 |         +-- transference_temporary / permanent
 |         +-- import_signaled_temporary / permanent  (sync_fd only)
 |         +-- export_multiple_times_temporary / permanent  (fd handles only)
 |         +-- dup / dup2 / dup3 / send_over_socket  (fd handles only)
 |         +-- signal_wait_import / export_signal_import_wait / export_import_signal_wait  (reference transference only)
 |         +-- create_win32_temporary / permanent  (win32 handles only)
 +-- memory
 |    +-- <handle_type>              (opaque_fd, opaque_win32, opaque_win32_kmt, android_hardware_buffer, dma_buf, zircon_vmo, mtlbuffer, mtltexture)
 |         +-- suballocated
 |         |    +-- host_visible
 |         |    |    +-- import_twice
 |         |    |    +-- import_multiple_times
 |         |    |    +-- export_multiple_times  (fd handles only)
 |         |    |    +-- fd_properties  (dma_buf only)
 |         |    |    +-- create_win32  (win32 handles only)
 |         |    +-- device_only
 |         |         +-- (same sub-tests as host_visible)
 |         |    +-- buffer
 |         |    |    +-- info
 |         |    |    +-- maintenance5
 |         |    |    +-- bind_export_import_bind
 |         |    |    +-- export_bind_import_bind
 |         |    |    +-- export_import_bind_bind
 |         |    +-- image
 |         |         +-- info
 |         |         +-- bind_export_import_bind
 |         |         +-- export_bind_import_bind
 |         |         +-- export_import_bind_bind
 |         +-- dedicated
 |              +-- (same sub-structure as suballocated)
 |         +-- ahb_format_properties / ahb_format_properties_2  (android_hardware_buffer only)
 |              +-- image_formats
 |              |    +-- <format_name>  (per AHB format)
 |              +-- external_format_resolve
 |                   +-- <ahb_format_name>  (per AHB non-BLOB format)
 +-- fence
      +-- <handle_type>              (sync_fd, opaque_fd, opaque_win32, opaque_win32_kmt)
           +-- info
           +-- import_twice
           +-- reimport
           +-- signal_export_import_wait
           +-- import_signaled  (sync_fd only)
           +-- export_signal_import_wait
           +-- export_import_signal_wait
           +-- signal_import
           +-- fence_reset
           +-- signal_wait_import
           +-- export_multiple_times  (fd handles only)
           +-- import_multiple_times
           +-- transference
           +-- dup / dup2 / dup3 / send_over_socket  (fd handles only)
           +-- create_win32  (win32 handles only)
```

## Test Families

### Semaphore Family

Tests external semaphore handle export, import, and synchronization. Covers binary and timeline semaphore types across temporary and permanent permanence modes. Key test functions include [testSemaphoreQueries()](../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L819), [testSemaphoreImportTwice()](../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L959), [testSemaphoreSignalExportImportWait()](../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L1078), [testSemaphoreTransference()](../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L1450), and FD-specific tests like [testSemaphoreFdDup()](../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L1552). Uses compute shaders to ensure sufficient GPU work before exporting sync FD handles ([tuneWorkSizeYAndPrepareCommandBuffer()](../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L502)).

### Memory Family

Tests external memory handle export, import, and binding for buffers and images. Organized by allocation mode (suballocated vs dedicated) and visibility (host_visible vs device_only). Key test functions include [testMemoryImportTwice()](../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L3373), [testBufferBindExportImportBind()](../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L4005), [testImageBindExportImportBind()](../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L4352). Android Hardware Buffer tests include format property queries ([testAndroidHardwareBufferImageFormat()](../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L4793)) and external format resolve ([AhbExternalFormatResolveApiCase](../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5102)).

### Fence Family

Tests external fence handle export, import, and synchronization. Mirrors the semaphore family structure but for fences. Key test functions include [testFenceQueries()](../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L1943), [testFenceImportTwice()](../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L2041), [testFenceTransference()](../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L2603), and FD-specific tests like [testFenceFdDup()](../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L2711).

## Parameter Dimensions

| Dimension | Observed Values |
|---|---|
| Handle Type (Semaphore) | sync_fd, opaque_fd, opaque_win32, opaque_win32_kmt, zircon_event |
| Handle Type (Memory) | opaque_fd, opaque_win32, opaque_win32_kmt, android_hardware_buffer, dma_buf, zircon_vmo, mtlbuffer, mtltexture |
| Handle Type (Fence) | sync_fd, opaque_fd, opaque_win32, opaque_win32_kmt |
| Permanence | temporary, permanent |
| Semaphore Type | binary, timeline |
| Allocation Mode | suballocated, dedicated |
| Memory Visibility | host_visible, device_only |
| Resource Type | buffer, image |
| AHB Format | R8G8B8_UNORM, R8G8B8A8_UNORM, R5G6B5_UNORM_PACK16, R16G16B16A16_SFLOAT, A2B10G10R10_UNORM_PACK32, D16_UNORM, X8_D24_UNORM_PACK32, D24_UNORM_S8_UINT, D32_SFLOAT, D32_SFLOAT_S8_UINT, S8_UINT, R8_UNORM, R16_UINT, R16G16_UINT, R10X6G10X6B10X6A10X6_UNORM_4PACK16 |

## Support / Feature Requirements

- Platform-specific extensions required per handle type (e.g., `VK_KHR_external_semaphore_fd`, `VK_KHR_external_memory_win32`, `VK_ANDROID_external_memory_android_hardware_buffer`, `VK_EXT_external_memory_metal`, `VK_FUCHSIA_external_memory`)
- [checkSemaphoreSupport()](../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L387): queries `VK_EXTERNAL_SEMAPHORE_FEATURE_EXPORTABLE_BIT` and `IMPORTABLE_BIT`
- [checkFenceSupport()](../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L404): queries `VK_EXTERNAL_FENCE_FEATURE_EXPORTABLE_BIT` and `IMPORTABLE_BIT`
- [checkBufferSupport()](../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L420): queries `VK_EXTERNAL_MEMORY_FEATURE_EXPORTABLE_BIT`, `IMPORTABLE_BIT`, and checks `DEDICATED_ONLY_BIT`
- [checkImageSupport()](../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L448): same checks as buffer, plus format/tiling compatibility
- `VK_KHR_maintenance5` required for maintenance5 buffer query tests ([checkMaintenance5()](../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5263))
- `VK_KHR_dedicated_allocation` required for dedicated allocation tests
- `VK_KHR_sampler_ycbcr_conversion` and `VK_EXT_queue_family_foreign` required for AHB tests

## Verification Methods

- **Semaphore**: Signal-export-import-wait round-trip verification; transference mode checks (copy vs reference); FD validity checks (allow -1 for sync_fd when signaled) ([submitAtomicCalculationsAndGetSemaphoreNative()](../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L599))
- **Fence**: Signal-export-import-wait round-trip; fence reset verification; FD duplication and socket transfer verification ([submitAtomicCalculationsAndGetFenceNative()](../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L722))
- **Memory**: Host-visible memory content comparison via [writeHostMemory()](../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L121) and [checkHostMemory()](../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L133); buffer/image binding state verification after export-import
- **AHB**: Format property query validation; external format resolve draw support check ([AhbExternalFormatResolveApiInstance](../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5116))

## Test Principles Observed

- Platform-conditional compilation (FD-based tests on Unix/Android, Win32 handles on Windows, Zircon on Fuchsia, Metal on Apple)
- Support queries before each test via `checkSemaphoreSupport`, `checkFenceSupport`, `checkBufferSupport`, `checkImageSupport`
- Custom instance/device creation with required extensions ([createTestInstance()](../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L198), [createTestDevice()](../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L217))
- Random test data generation via [genTestData()](../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L146)

## Notes / Uncertainties

- The file is very large (~5610 lines) and covers three distinct Vulkan object types (semaphore, memory, fence) that could arguably be separate files
- FD-based tests use compute shaders to ensure sufficient execution time for valid FD export; the tuning loop targets >9ms execution ([tuneWorkSizeYAndPrepareCommandBuffer()](../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L574))
- AHB external format resolve tests use a custom TestCase/TestInstance subclass pair ([AhbExternalFormatResolveApiCase](../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5102)) rather than the function-case pattern used elsewhere
- The `createMemoryTests` overload without handle-type argument creates the parent "memory" group containing all handle-type subgroups ([createMemoryTests()](../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5578))
