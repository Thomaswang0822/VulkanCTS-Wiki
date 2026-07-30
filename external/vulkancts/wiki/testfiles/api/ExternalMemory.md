## Overview

**Core question:** can the implementation export Vulkan semaphore, fence, and device-memory handles to OS-native handles, re-import those handles into new Vulkan objects, and have the imported objects behave with the spec-required transference and permanence semantics?

- Source file covered: [`vktApiExternalMemoryTests.cpp`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L1).
- Test category: `api`. Test family: `external`. Intermediate nodes: `semaphore`, `memory`, `fence`.
- Core test idea: for every external handle type the implementation advertises, drive an export-import round-trip on a Vulkan semaphore, fence, or device-memory object, then verify that the imported object can be signaled/waited/bound and that any host-visible contents are coherent.
- The remaining sections cover the three intermediate nodes, the handle-type and permanence dimensions, what each round-trip checks, and what a failure of each one means.

## Background Knowledge

- **External handle types.** Vulkan exposes OS-native handles for semaphores, fences, and device memory through `VK_KHR_external_semaphore_*`, `VK_KHR_external_fence_*`, and `VK_KHR_external_memory_*` extensions. Handle kinds include POSIX file descriptors (`opaque_fd`, `sync_fd`, `dma_buf`), Windows handles (`opaque_win32`, `opaque_win32_kmt`), Android Hardware Buffer (`android_hardware_buffer`), Fuchsia Zircon handles (`zircon_event`, `zircon_vmo`), and Apple Metal handles (`mtlbuffer`, `mtltexture`). Each handle type is queried through `vkGetPhysicalDeviceExternal*Properties` before any test runs.
- **Transference: copy versus reference.** When a handle is exported, the transference mode controls whether the receiver gets a snapshot of the payload (`TRANSFERENCE_COPY`, used by `sync_fd`) or a reference to the same underlying synchronization object (`TRANSFERENCE_REFERENCE`, used by `opaque_fd`, `opaque_win32`, `opaque_win32_kmt`, `zircon_event`). Copy-transference handles may return a `-1` file descriptor when the payload is already consumed, so several tests accept that as a pass condition.
- **Permanence: temporary versus permanent.** Importing a handle either permanently attaches the external payload to the Vulkan object (`PERMANENCE_PERMANENT`) or only attaches it until the next signal/wait/reset (`PERMANENCE_TEMPORARY`). The import flags `VK_SEMAPHORE_IMPORT_TEMPORARY_BIT` and `VK_FENCE_IMPORT_TEMPORARY_BIT` select the temporary path. `sync_fd` only supports temporary import, so its `_permanent` cases are pruned by `isSupportedPermanence` rather than registered.
- **Dedicated versus suballocated external memory.** Some external memory handle types require a one-to-one correspondence between a `VkDeviceMemory` object and a single resource (`VK_EXTERNAL_MEMORY_FEATURE_DEDICATED_ONLY_BIT`). `VK_KHR_dedicated_allocation` provides the `VkMemoryDedicatedAllocateInfo` chain used for that path. The memory intermediate node runs both `suballocated` and `dedicated` branches per handle type and prunes the suballocated branch when a handle type advertises dedicated-only.

## Registration Hierarchy

```text
api.external
├── semaphore
├── memory
└── fence
```

The `external` test family is registered by [`createExternalMemoryTests()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5597-L5606) and attached to the `api` test category by [`vktApiTests.cpp#L117`](../../../modules/vulkan/api/vktApiTests.cpp#L117). The three intermediate nodes are added by [`createSemaphoreTests()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5389-L5406), [`createMemoryTests()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5577-L5593), and [`createFenceTests()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5267-L5277). The registered group name is `external`, not `external_memory`; the source-file suffix is historical.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Synchronization object | `semaphore`, `memory`, `fence` | Selects which Vulkan object type drives the export-import round-trip. Each is a separate intermediate node with its own handle-type and case matrix. | [`createExternalMemoryTests()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5597-L5606) |
| Semaphore handle type | `sync_fd`, `opaque_fd`, `opaque_win32`, `opaque_win32_kmt`, `zircon_event` | One intermediate node per `VkExternalSemaphoreHandleTypeFlagBits`. Each routes to platform-specific export/import calls and implies a transference mode. | [`createSemaphoreTests()` overload](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5389-L5406) |
| Fence handle type | `sync_fd`, `opaque_fd`, `opaque_win32`, `opaque_win32_kmt` | One intermediate node per `VkExternalFenceHandleTypeFlagBits`. Same platform routing as semaphores but for `VkFence`. | [`createFenceTests()` overload](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5267-L5277) |
| Memory handle type | `opaque_fd`, `opaque_win32`, `opaque_win32_kmt`, `android_hardware_buffer`, `dma_buf`, `zircon_vmo`, `mtlbuffer`, `mtltexture` | One intermediate node per `VkExternalMemoryHandleTypeFlagBits`. Memory also carries dedicated/suballocated and host-visible/device-only subdimensions. | [`createMemoryTests()` overload](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5408-L5575) |
| Permanence | `temporary`, `permanent` | Selects the import flag bits `VK_*_IMPORT_TEMPORARY_BIT` or zero. Pruned per handle type by `isSupportedPermanence`; `sync_fd` only retains `temporary`. | [`permanences` array](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5282-L5286) |
| Semaphore type | `binary`, `timeline` | Used in `info_*` query leaves only; selects `VK_SEMAPHORE_TYPE_BINARY` or `VK_SEMAPHORE_TYPE_TIMELINE` for `VkSemaphoreTypeCreateInfo`. | [`semaphoreTypes` array](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5287-L5294) |
| Allocation mode (memory) | `suballocated`, `dedicated` | Selects whether `VkMemoryDedicatedAllocateInfo` is chained. Suballocated is pruned when the handle type advertises `DEDICATED_ONLY_BIT`. | [`createMemoryTests()` handle overload](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5413-L5417) |
| Memory visibility (memory) | `host_visible`, `device_only` | Selects a host-visible memory type or any memory type. Host-visible cases round-trip test data through `writeHostMemory` / `checkHostMemory`. | [`createMemoryTests()` handle overload](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5419-L5423) |
| Resource type (memory) | `buffer`, `image` | Selects `vkBindBufferMemory` or `vkBindImageMemory` round-trip. Each registers `info`, `bind_export_import_bind`, `export_bind_import_bind`, `export_import_bind_bind`. | [`createMemoryTests()` handle overload](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5464-L5497) |
| AHB format properties query | `ahb_format_properties`, `ahb_format_properties_2` | Selects `VkAndroidHardwareBufferFormatPropertiesANDROID` or the `...2ANDROID` chain with `VkFormatFeatureFlags2`. | [`createMemoryTests()` AHB branch](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5502-L5572) |
| AHB external format resolve | one leaf per `AndroidHardwareBufferInstance::Format` except `BLOB` | Each leaf queries `VK_ANDROID_external_format_resolve` support for one AHB format. | [`external_format_resolve` group](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5552-L5569) |

The full matrix produces 549 registered test case leaves: 108 under `semaphore`, 350 under `memory`, and 91 under `fence`.

## Behavior Parameters

The primary behavioral axis is the intermediate node. Each value of the axis changes which Vulkan object type drives the export-import round-trip and which round-trip variants are exercised.

### semaphore: External semaphore handle export, import, and synchronization

Tests external semaphore handle export, import, and synchronization across `sync_fd`, `opaque_fd`, `opaque_win32`, `opaque_win32_kmt`, and `zircon_event`. Per handle type, the matrix generates `info_<binary|timeline>` query leaves plus, for each supported permanence, `import_twice_*`, `reimport_*`, `import_multiple_times_*`, `signal_export_import_wait_*`, `signal_import_*`, and `transference_*`. `sync_fd` adds `import_signaled_*`; FD handle types add `export_multiple_times_*`, `dup_*`, `dup2_*`, `dup3_*`, and `send_over_socket_*`; Win32 handle types add `create_win32_*`. Reference-transference handle types add `signal_wait_import_*`, `export_signal_import_wait_*`, and `export_import_signal_wait_*`. The shared body is built by [`createSemaphoreTests(testCtx, externalType)`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5279-L5387). Export-from-signaled semaphore cases use a compute workload through [`submitAtomicCalculationsAndGetSemaphoreNative()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L598-L680) to ensure the queue is busy long enough for a valid FD to be produced.

### memory: External device-memory handle export, import, and binding

Tests external device-memory handle export, import, and binding across `opaque_fd`, `opaque_win32`, `opaque_win32_kmt`, `android_hardware_buffer`, `dma_buf`, `zircon_vmo`, `mtlbuffer`, and `mtltexture`. Per handle type, the matrix generates `suballocated` and `dedicated` branches, each with `host_visible` and `device_only` subbranches. The host-visible subbranch registers `import_twice`, `import_multiple_times`, and (for FD handle types) `dup`, `dup2`, `dup3`, `send_over_socket`, `export_multiple_times`, plus `fd_properties` for `dma_buf` and `create_win32` for Win32 handle types. Each dedicated branch also registers `buffer` and `image` intermediate nodes with `info`, `maintenance5` (buffer only), `bind_export_import_bind`, `export_bind_import_bind`, and `export_import_bind_bind`. The `android_hardware_buffer` branch also registers `ahb_format_properties` and `ahb_format_properties_2`, each with `image_formats` and `external_format_resolve` intermediate nodes. The shared body is built by [`createMemoryTests(testCtx, externalType)`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5408-L5575). Host-visible cases write and read back test data through [`writeHostMemory()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L121-L131) and [`checkHostMemory()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L133-L144).

### fence: External fence handle export, import, and synchronization

Tests external fence handle export, import, and synchronization across `sync_fd`, `opaque_fd`, `opaque_win32`, and `opaque_win32_kmt`. Per handle type, the matrix registers `info` plus, for each supported permanence, `import_twice_*`, `reimport_*`, `import_multiple_times_*`, `signal_export_import_wait_*`, `signal_import_*`, `reset_*`, and `transference_*`. `sync_fd` adds `import_signaled_*`; FD handle types add `export_multiple_times_*`, `dup_*`, `dup2_*`, `dup3_*`, and `send_over_socket_*`; Win32 handle types add `create_win32_*`. Reference-transference handle types add `signal_wait_import_*`, `export_signal_import_wait_*`, and `export_import_signal_wait_*`. The shared body is built by [`createFenceTests(testCtx, externalType)`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L4548-L4645). Signaled-export fence cases use the same compute workload pattern through [`submitAtomicCalculationsAndGetFenceNative()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L721-L802) so that the fence is signaled before FD export.

## Shader Analysis

No shader is part of the tested behavior. A small compute shader is generated by [`initProgramsToGetNativeFd()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L870-L890) and dispatched by `submitAtomicCalculationsAndGetSemaphoreNative` and `submitAtomicCalculationsAndGetFenceNative`, but its only role is to keep the queue busy long enough for `sync_fd` export to return a valid file descriptor. The shader's atomic-add workload is not inspected or validated. No `### Representative Shader Walkthrough` subsection is therefore created.

## Runtime Execution and Result Checking

The host-side flow is shared across the three intermediate nodes; the differences are which Vulkan object is exported and which final operation is checked.

Common host setup:

- Build a custom instance with `VK_KHR_external_semaphore_capabilities`, `VK_KHR_external_memory_capabilities`, and/or `VK_KHR_external_fence_capabilities` as needed, through [`createTestInstance()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L198-L215).
- Build a custom device with the matching `VK_KHR_external_semaphore_*`, `VK_KHR_external_fence_*`, and/or `VK_KHR_external_memory_*` device extensions, plus `VK_KHR_dedicated_allocation` when the dedicated branch is exercised and `VK_KHR_sampler_ycbcr_conversion` plus `VK_EXT_queue_family_foreign` for AHB, through [`createTestDevice()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L217-L366).
- Query `vkGetPhysicalDeviceExternal*Properties` for the handle type and throw `NotSupportedError` if `EXPORTABLE_BIT` or `IMPORTABLE_BIT` is missing ([`checkSemaphoreSupport()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L386-L401), [`checkFenceSupport()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L403-L417), [`checkBufferSupport()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L419-L445), [`checkImageSupport()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L447-L481)).

Semaphore and fence round-trips:

- Create an exportable `VkSemaphore` or `VkFence` with the handle type in the `pNext` chain.
- Submit a compute workload that signals the semaphore or fence, then call `vkGetSemaphoreFdKHR` / `vkGetFenceFdKHR` / the Win32 / Zircon / AHB / Metal equivalent to obtain a `NativeHandle`. For copy-transference handle types, a returned `-1` file descriptor is accepted as a pass when the signaled event has already been consumed ([`vktApiExternalMemoryTests.cpp#L675-L678`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L675-L678)).
- Create a second semaphore or fence and import the handle with the permanence-selected import flag.
- Submit a wait on the imported object (semaphore) or call `vkWaitForFences` (fence); `VK_CHECK` wraps the call so a non-`VK_SUCCESS` return fails the case.
- `transference_*` cases also drive the signal/wait sequences that distinguish copy from reference semantics, as enumerated in [`testSemaphoreTransference()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L1449-L1549) and [`testFenceTransference()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L2602-L2708).
- `dup_*`, `dup2_*`, `dup3_*`, and `send_over_socket_*` cases duplicate or transfer the FD before importing it; the wait on the imported object must still succeed.
- `reset_*` (fence only) resets the imported fence and confirms it can be signaled and waited again.

Memory round-trips:

- Create an external buffer or image, query its memory requirements, allocate exportable `VkDeviceMemory`, optionally chain `VkMemoryDedicatedAllocateInfo`, and bind it.
- For host-visible cases, write test data generated by [`genTestData()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L146-L157) through [`writeHostMemory()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L121-L131) before export.
- Export the memory handle and, for AHB, re-query the memory type bits from `vkGetAndroidHardwareBufferPropertiesANDROID` to satisfy VUID `VkMemoryAllocateInfo-memoryTypeIndex-02385`.
- Create a second buffer or image, import the handle into a new `VkDeviceMemory` through `importMemory` or `importDedicatedMemory`, and bind it.
- For host-visible cases, [`checkHostMemory()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L133-L144) maps the imported memory and compares bytes against the original test data; a mismatch calls `TCU_FAIL("Memory contents don't match")`. The `import_twice` case also verifies that writes through one imported mapping are visible through the other mapping.
- `bind_export_import_bind`, `export_bind_import_bind`, and `export_import_bind_bind` differ in whether binding happens before export, before import, or only after import, exercising each ordering the spec permits.
- The AHB `image_formats` intermediate node queries `vkGetAndroidHardwareBufferFormatPropertiesANDROID` (or the `...2` variant) for each listed format and validates that the implementation's reported format features and external format resolve behavior conform to the rules in `VK_ANDROID_external_memory_android_hardware_buffer` and `VK_ANDROID_external_format_resolve`. The `external_format_resolve` intermediate node is implemented by [`AhbExternalFormatResolveApiInstance::iterate()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5167-L5260).

Final pass/fail condition: every case returns `tcu::TestStatus::pass("Pass")` on success. Any `VK_CHECK` failure, `TCU_FAIL`, `TCU_CHECK` failure, or unexpected `vk::Error` exception produces `tcu::TestStatus::fail`. `NotSupportedError` is reported as skip, not fail.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `semaphore` | Handle export/import round-trip failure; transference or permanence mishandling; FD duplication or socket transfer failure; Win32 handle creation path failure |
| `memory` | Handle export/import/binding failure; host-visible memory content incoherency; buffer or image bind-after-import failure; AHB format-property or external-format-resolve query failure |
| `fence` | Handle export/import round-trip failure; transference or permanence mishandling; fence reset semantics failure; FD duplication or socket transfer failure; Win32 handle creation path failure |

All three intermediate nodes also share two cross-cutting causes: missing platform or extension support that was not detected by the support query, and incorrect `VkExternal*Properties` advertisement that lets the test proceed against an unsupported handle type.

### Cause Analysis

#### Handle export/import round-trip failure

**Possible failure symptoms:** `vkGetSemaphoreFdKHR`, `vkGetFenceFdKHR`, `vkGetMemoryFdKHR`, or the Win32 / Zircon / AHB / Metal equivalent returns a non-`VK_SUCCESS` result; the imported semaphore cannot be waited on; the imported fence never becomes signaled; `vkWaitForFences` times out; or the case fails inside `VK_CHECK` during the import call.

**Possible implementation causes:** the driver advertises exportable and importable bits through `vkGetPhysicalDeviceExternal*Properties` but the underlying handle allocation or import path is broken for that handle type; the OS-level handle is closed prematurely because the driver's ownership transfer does not match the platform convention; the import operation does not honor the `pNext` chain that selects the handle type; or copy-transference handles are treated as reference-transference (or vice versa), so the imported payload is in the wrong state. Source-level investigation is needed for any case that fails inside the platform export/import helper, since those paths live in `vktExternalMemoryUtil` rather than this test file.

#### Transference and permanence mishandling

**Possible failure symptoms:** `transference_*` cases hang, time out, or fail `VK_CHECK` on a wait operation; `signal_wait_import_*`, `export_signal_import_wait_*`, or `export_import_signal_wait_*` cases fail because the imported object observes a signal that should not yet be visible, or fails to observe a signal that should be visible; temporary-import cases keep the payload attached after a signal/wait/reset, so a subsequent operation observes stale state.

**Possible implementation causes:** for copy-transference handle types (`sync_fd`), the driver leaks payload state across signal/wait boundaries or returns a stale FD after the payload is consumed; for reference-transference handle types (`opaque_fd`, `opaque_win32`, `opaque_win32_kmt`, `zircon_event`), the driver does not propagate signal and wait operations between the original and imported handles; for temporary imports, the driver does not restore the original payload when the temporary payload is consumed. The expected semantics are defined by `VK_KHR_external_semaphore` and `VK_KHR_external_fence`; a divergence between the implementation's transference advertisement in `VkExternal*Properties` and its actual runtime behavior is a conformance failure.

#### FD duplication and socket transfer failure

**Possible failure symptoms:** `dup_*`, `dup2_*`, `dup3_*`, or `send_over_socket_*` cases fail because the duplicated or transferred FD cannot be imported, or because the imported object cannot be waited on; `VK_CHECK` reports a bad file descriptor; or the case hangs on wait.

**Possible implementation causes:** the OS-level `dup`, `dup2`, `dup3`, or `SCM_RIGHTS` socket send returns an invalid FD; the driver's import path closes the FD it received, breaking the duplicate held by the test; or the driver does not accept a duplicated FD because it expects the original FD handle. These cases are platform-specific and run only on Unix and Android; failures outside those platforms indicate a test-environment issue rather than a Vulkan conformance issue.

#### Win32 handle creation path failure

**Possible failure symptoms:** `create_win32_*` cases fail during `vkCreateSemaphore` or `vkCreateFence` with `VkImportSemaphoreWin32HandleInfoKHR` or `VkImportFenceWin32HandleInfoKHR` in the `pNext` chain; `VK_CHECK` reports `VK_ERROR_INVALID_EXTERNAL_HANDLE_KHR`; or the created object cannot be signaled or waited on.

**Possible implementation causes:** the driver does not accept `VkSemaphoreCreateFlagBits` together with the Win32 import chain, the `pNext` chain is constructed with a mismatched handle type, or the underlying `HANDLE` is not duplicated correctly across process handle tables. These cases run only on Windows; failures outside Windows indicate a test-environment issue.

#### Host-visible memory content incoherency

**Possible failure symptoms:** `host_visible` memory cases fail inside [`checkHostMemory()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L133-L144) with `TCU_FAIL("Memory contents don't match")`; the original test data is not visible through the imported mapping; writes through one imported mapping are not visible through another mapping in `import_twice`; or `vkInvalidateMappedMemoryRanges` returns `VK_SUCCESS` but the mapped range still contains stale data.

**Possible implementation causes:** the driver does not flush or invalidate the correct memory range when the same backing memory is exposed through multiple `VkDeviceMemory` objects; the host-visible memory type chosen by `getExportedMemoryTypeIndex` does not provide host-coherent access for the imported handle; or the implementation does not map the imported handle to the same host virtual address range as the original. The expected behavior follows from `VK_KHR_external_memory` and the host visibility rules in the Vulkan memory model.

#### Buffer or image bind-after-import failure

**Possible failure symptoms:** `bind_export_import_bind`, `export_bind_import_bind`, or `export_import_bind_bind` cases fail at `vkBindBufferMemory` or `vkBindImageMemory` with `VK_ERROR_INVALID_EXTERNAL_HANDLE_KHR` or `VK_ERROR_OUT_OF_DEVICE_MEMORY`; or the bind succeeds but a subsequent operation on the second resource fails.

**Possible implementation causes:** the driver requires the resource to be created with a specific external handle bit but the test created it without; the imported memory's `memoryTypeBits` do not match the second resource's requirements and the AHB re-query path was not taken; or the dedicated-allocation requirement was not honored when the handle type advertised `DEDICATED_ONLY_BIT`. The ordering variants exist to expose bind-before-export, export-before-bind, and import-before-bind ordering bugs.

#### AHB format-property or external-format-resolve query failure

**Possible failure symptoms:** `ahb_format_properties` or `ahb_format_properties_2` `image_formats` leaves return a format feature set that contradicts the minimum required by `VK_ANDROID_external_memory_android_hardware_buffer`; `external_format_resolve` leaves return `tcu::TestStatus::fail("No draw support")` or `tcu::TestStatus::fail("Depth/stencil must be supported through Vulkan Format mapping")`; or `vkGetAndroidHardwareBufferPropertiesANDROID` returns zero `memoryTypeBits`.

**Possible implementation causes:** the driver reports a `VkFormat` mapping for an AHB format that does not support the format features the spec requires; the driver fails to populate `VkAndroidHardwareBufferFormatResolvePropertiesANDROID::colorAttachmentFormat` for a format that requires external format resolve; or the driver maps a depth/stencil AHB format to a Vulkan format that lacks the attachment features the spec requires for depth/stencil support through Vulkan Format mapping. These cases are gated by `VK_ANDROID_external_memory_android_hardware_buffer` and `VK_ANDROID_external_format_resolve` and run only on Android.

#### Fence reset semantics failure

**Possible failure symptoms:** `reset_*` fence cases fail at `vkResetFences` with `VK_ERROR_INVALID_EXTERNAL_HANDLE_KHR`, or the reset fence cannot be signaled and waited again after a temporary import; `VK_CHECK` reports a non-signaled fence after the second wait.

**Possible implementation causes:** the driver treats the temporary import payload as permanent, so `vkResetFences` does not restore the original fence payload; or the driver's reset path does not handle the imported handle's ownership transfer correctly. The expected behavior is defined by `VK_KHR_external_fence`: a temporary import is detached once the fence is signaled, after which the fence must behave as if no import had occurred.

## Case Pruning

### Requirement-based pruning

- **Platform-specific compilation.** FD-based handle types (`sync_fd`, `opaque_fd`, `dma_buf`) and the `dup_*`, `dup2_*`, `dup3_*`, `send_over_socket_*` cases compile only on `DE_OS_ANDROID` or `DE_OS_UNIX`. Win32 handle types and `create_win32_*` cases compile only on `DE_OS_WIN32`. Zircon handle types compile only on Fuchsia. Metal handle types compile only on Apple platforms. AHB cases compile only on Android. The platform guards are in [`vktApiExternalMemoryTests.cpp#L51-L63`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L51-L63) and the FD-specific test bodies.
- **Per-handle-type support query.** Each case calls `vkGetPhysicalDeviceExternal*Properties` for its handle type and throws `NotSupportedError` when `EXPORTABLE_BIT` or `IMPORTABLE_BIT` is missing ([`checkSemaphoreSupport()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L386-L401), [`checkFenceSupport()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L403-L417), [`checkBufferSupport()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L419-L445), [`checkImageSupport()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L447-L481)).
- **Dedicated-only handle types.** When `VK_EXTERNAL_MEMORY_FEATURE_DEDICATED_ONLY_BIT` is set, `checkBufferSupport` and `checkImageSupport` throw `NotSupportedError` for the `suballocated` branch, leaving only the `dedicated` branch registered path exercised.
- **Extension requirements.** `VK_KHR_dedicated_allocation` (plus `VK_KHR_get_memory_requirements2`) is required for dedicated-allocation memory cases; `VK_KHR_sampler_ycbcr_conversion` and `VK_EXT_queue_family_foreign` are required for AHB; `VK_KHR_maintenance5` is required for the buffer `maintenance5` leaf ([`checkMaintenance5()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5262-L5265)); `VK_ANDROID_external_format_resolve` and `VK_KHR_format_feature_flags2` are required for the AHB `external_format_resolve` and `ahb_format_properties_2` leaves respectively ([`AhbExternalFormatResolveApiCase::checkSupport()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5147-L5156)).
- **Portability subset events.** `transference_*`, `signal_export_import_wait_*`, and `export_import_signal_wait_*` cases call [`checkEvent()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L4533-L4538) directly and are skipped when `VK_KHR_portability_subset` advertises `events == VK_FALSE`. The `checkSupport`-gated cases (`import_twice_*`, `reimport_*`, `import_multiple_times_*`, `signal_import_*`, and the FD-only family) inherit the same check only on copy-transference handle types.
- **Vulkan SC exclusion.** The whole `external` test family is excluded from Vulkan SC by the `#ifndef CTS_USES_VULKANSC` guard in [`vktApiTests.cpp#L116-L118`](../../../modules/vulkan/api/vktApiTests.cpp#L116-L118).

### Design-based pruning

- **`sync_fd` permanence.** `isSupportedPermanence` returns false for `PERMANENCE_PERMANENT` on `sync_fd`, so only `_temporary` cases are registered for that handle type. The mustpass reflects this: every `api.external.fence.sync_fd.*` and `api.external.semaphore.sync_fd.*` leaf carries the `_temporary` suffix.
- **FD-only cases.** `dup_*`, `dup2_*`, `dup3_*`, `send_over_socket_*`, and `export_multiple_times_*` are registered only for `sync_fd` and `opaque_fd` handle types because Win32, Zircon, and AHB handles do not have file-descriptor equivalents. The guard is at [`vktApiExternalMemoryTests.cpp#L5350-L5370`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5350-L5370) (semaphores) and [`vktApiExternalMemoryTests.cpp#L4608-L4628`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L4608-L4628) (fences).
- **Win32-only `create_win32_*` cases.** `create_win32_*` is registered only for `opaque_win32` and `opaque_win32_kmt` handle types because that creation path is the Win32 equivalent of the FD dup/socket family.
- **Reference-transference cases.** `signal_wait_import_*`, `export_signal_import_wait_*`, and `export_import_signal_wait_*` are registered only when `getHandelTypeTransferences(externalType) == TRANSFERENCE_REFERENCE`, since copy-transference handles do not support the export-then-signal-then-import ordering.
- **`dma_buf` `fd_properties` leaf.** `fd_properties` is registered only for `dma_buf` because it queries `vkGetMemoryFdPropertiesKHR`, which is meaningful only for that handle type ([`vktApiExternalMemoryTests.cpp#L5455-L5459`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5455-L5459)).
- **AHB-only `ahb_format_properties` intermediate nodes.** The `ahb_format_properties` and `ahb_format_properties_2` intermediate nodes are registered only for `android_hardware_buffer`, since no other handle type carries an external format ([`vktApiExternalMemoryTests.cpp#L5502-L5572`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5502-L5572)).
- **`BLOB` excluded from `external_format_resolve`.** `external_format_resolve` iterates over every `AndroidHardwareBufferInstance::Format` except `BLOB`, since BLOB is a non-renderable format that has no color attachment to resolve ([`vktApiExternalMemoryTests.cpp#L5560-L5561`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5560-L5561)).

## Key Takeaways

- The registered group name is `external`, not `external_memory`; the source filename and `createExternalMemoryTests` entry point retain the historical suffix.
- Each intermediate node exercises a distinct Vulkan object type, but the three share the same handle-type and permanence matrix and the same export-import round-trip shape.
- Copy-transference handle types (`sync_fd`) return a `-1` file descriptor when the payload is already consumed; several cases accept that as a pass condition rather than retrying.
- `sync_fd` only supports temporary import, so no `_permanent` leaves exist for that handle type in the mustpass.
- Memory cases distinguish themselves from semaphore and fence cases by the host-visible content coherency check and the three bind-ordering variants; a failure in `bind_export_import_bind` versus `export_bind_import_bind` versus `export_import_bind_bind` localizes an ordering bug in the driver's bind path.
- The AHB branch is the only handle-type branch that registers format-property query intermediate nodes, and it is the only path that exercises `VK_ANDROID_external_format_resolve`.
- See `## Failure Meaning` for the failure-cause analysis; the symptoms there are the observable signals a driver bug produces in this test family.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Public entry point | [`createExternalMemoryTests()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5597-L5606) | Assembles the `external` group from the three intermediate nodes. |
| Parent registration | [`vktApiTests.cpp#L117`](../../../modules/vulkan/api/vktApiTests.cpp#L117) | Attaches `external` to the `api` test category. |
| Header | [`vktApiExternalMemoryTests.hpp`](../../../modules/vulkan/api/vktApiExternalMemoryTests.hpp#L1) | Declares the public entry point. |
| Semaphore registration | [`createSemaphoreTests(testCtx)`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5389-L5406) and [`createSemaphoreTests(testCtx, externalType)`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5279-L5387) | Build the semaphore intermediate node and its per-handle-type intermediate nodes. |
| Memory registration | [`createMemoryTests(testCtx)`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5577-L5593) and [`createMemoryTests(testCtx, externalType)`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5408-L5575) | Build the memory intermediate node and its per-handle-type, dedicated/suballocated, host-visible/device-only, buffer/image, and AHB intermediate nodes. |
| Fence registration | [`createFenceTests(testCtx)`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5267-L5277) and [`createFenceTests(testCtx, externalType)`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L4548-L4645) | Build the fence intermediate node and its per-handle-type intermediate nodes. |
| Custom instance and device | [`createTestInstance()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L198-L215), [`createTestDevice()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L217-L366) | Add the external capabilities and external handle extensions required by each case. |
| Support queries | [`checkSemaphoreSupport()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L386-L401), [`checkFenceSupport()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L403-L417), [`checkBufferSupport()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L419-L445), [`checkImageSupport()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L447-L481), [`checkEvent()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L4533-L4538), [`checkMaintenance5()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5262-L5265) | Per-case requirement pruning. |
| Compute workload for FD export | [`submitAtomicCalculationsAndGetSemaphoreNative()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L598-L680), [`submitAtomicCalculationsAndGetFenceNative()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L721-L802), [`initProgramsToGetNativeFd()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L870-L890) | Keep the queue busy so `sync_fd` export returns a valid FD. |
| Host-visible memory check | [`writeHostMemory()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L121-L131), [`checkHostMemory()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L133-L144), [`genTestData()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L146-L157) | Memory-content round-trip and coherency check. |
| Representative semaphore tests | [`testSemaphoreSignalExportImportWait()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L1077-L1120), [`testSemaphoreTransference()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L1449-L1549) | Show the round-trip and transference patterns. |
| Representative fence tests | [`testFenceSignalExportImportWait()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L2158-L2201), [`testFenceTransference()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L2602-L2708), [`testFenceReset()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L2369-L2443) | Show the round-trip, transference, and reset patterns. |
| Representative memory tests | [`testMemoryImportTwice()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L3372-L3457), [`testBufferBindExportImportBind()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L4004-L4063) | Show the host-visible coherency and bind-ordering patterns. |
| AHB external format resolve | [`AhbExternalFormatResolveApiInstance::iterate()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L5167-L5260) | Implements the AHB-only format-property query intermediate nodes. |
| External-memory utilities | [`vktExternalMemoryUtil.hpp`](../../../modules/vulkan/util/vktExternalMemoryUtil.hpp#L1) | Defines `Permanence`, `Transference`, `getHandelTypeTransferences`, `isSupportedPermanence`, and the platform `NativeHandle` operations. |
