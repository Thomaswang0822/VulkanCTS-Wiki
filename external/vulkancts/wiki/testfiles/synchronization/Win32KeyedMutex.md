# `vktSynchronizationWin32KeyedMutexTests`

## Brief

Legacy Vulkan Conformance Test (CTS) coverage for sharing resources between Vulkan and Direct3D 11 through Win32 keyed-mutex synchronization. The test group is registered at:

```text
synchronization.win32_keyed_mutex
```

It is a **legacy-only** group. It is not registered below `synchronization2` and does not test `VK_KHR_synchronization2` semantics.

The implementation creates a D3D11 device for the adapter matching the Vulkan physical device LUID, creates keyed-mutex-backed D3D11 resources, and imports those resources into Vulkan. Vulkan records a write operation and a read operation, with resource barriers around each operation. D3D11 copies or renders between the two shared resources while ownership is transferred with keyed mutex keys. After the second Vulkan submission, the test compares the bytes produced by the write operation with the bytes observed by the read operation.

Source: [vktSynchronizationWin32KeyedMutexTests.cpp](../../../modules/vulkan/synchronization/vktSynchronizationWin32KeyedMutexTests.cpp)

## Coverage

The test cases are generated from the operation and resource tables used by the synchronization framework. Each compatible write/read/resource combination is emitted under a group named:

```text
<write-operation>_<read-operation>/<resource><handle-suffix>
```

The source currently supplies these Win32 keyed-mutex resource shapes:

- Buffers: 16 KiB and 256 KiB.
- 2D color images: 128 × 128, single-sampled, with `R8_UNORM`, `R16_UINT`,
  `R8G8B8A8_UNORM`, `R16G16B16A16_UINT`, or `R32G32B32A32_SFLOAT`.

The operation tables select supported Vulkan write/read paths, including transfer operations, clears, and shader stages (compute, vertex, tessellation, geometry, and fragment), including indirect variants where supported. Unsupported pairs are omitted during test creation by `isResourceSupported`.

Each resource is tested with the handle form applicable to its type:

| Suffix | Buffer handle | Image handle |
| --- | --- | --- |
| `_nt` | Not available for D3D11 buffers | `VK_EXTERNAL_MEMORY_HANDLE_TYPE_D3D11_TEXTURE_BIT` |
| `_kmt` | `VK_EXTERNAL_MEMORY_HANDLE_TYPE_OPAQUE_WIN32_KMT_BIT` | `VK_EXTERNAL_MEMORY_HANDLE_TYPE_D3D11_TEXTURE_KMT_BIT` |

## Synchronization sequence

For each queue family, the test performs the following sequence:

1. Create two D3D11 resources with `D3D11_RESOURCE_MISC_SHARED_KEYEDMUTEX` and obtain their Win32 shared handles.
2. Import one handle into a Vulkan resource for the write operation and the other for the read operation. Use dedicated allocation information when Vulkan reports that it is required.
3. Submit the Vulkan write command buffer with `VkWin32KeyedMutexAcquireReleaseInfoKHR`:
   - acquire the Vulkan-write key (`KEYED_MUTEX_VK_WRITE`),
   - release ownership to D3D11 (`KEYED_MUTEX_DX_COPY`).
4. In D3D11, acquire the copy key. Copy the buffer, or render the source texture into the destination texture, then release the source with `KEYED_MUTEX_DONE` and the destination with `KEYED_MUTEX_VK_VERIFY`.
5. Submit the Vulkan read command buffer with keyed-mutex acquire/release info:
   - acquire `KEYED_MUTEX_VK_VERIFY`,
   - release the memory with `KEYED_MUTEX_DONE`.
6. Wait for the queue to become idle and compare the write-operation data with the read-operation data. A mismatch fails the test and logs the first differing byte plus bounded expected/actual data.

The instance is shared across queue-family iterations and collects validation messages after each iteration. The test returns `incomplete` until every queue family has been exercised.

## Validation

A test case requires:

- Device extensions `VK_KHR_external_memory_win32` and
  `VK_KHR_win32_keyed_mutex`.
- Instance extensions `VK_KHR_get_physical_device_properties2` and
  `VK_KHR_external_memory_capabilities`.
- `VK_KHR_external_memory`, `VK_KHR_dedicated_allocation`, and
  `VK_KHR_get_memory_requirements2` when they are not core in the selected API
  version.
- An importable external-memory configuration for the selected resource and
  handle type.
- A Vulkan physical-device LUID that is valid and matches a DXGI adapter.
- Windows support and the required D3D11/DXGI runtime libraries. Non-Windows
  builds throw `NotSupportedError`.
- Windows 8 or later for the NT texture handle form. The generated buffer cases use `VK_EXTERNAL_MEMORY_HANDLE_TYPE_OPAQUE_WIN32_KMT_BIT`, and the image KMT case uses `VK_EXTERNAL_MEMORY_HANDLE_TYPE_D3D11_TEXTURE_KMT_BIT`; those selected KMT cases are not gated by the Windows-version checks in `checkSupport`.
- Support for both selected synchronization operations, checked through their
  `OperationSupport` objects.

The test itself validates synchronization in two ways: it applies the framework's
write/read resource barriers and keyed-mutex ownership transfers, then checks the
resulting data byte-for-byte. Validation-layer messages are collected through the
custom Vulkan instance and included in the test result. Unsupported environments
are reported as not supported rather than as data mismatches.

## Compact contract

**Given** a Windows Vulkan implementation and a matching D3D11 adapter that
support the required external-memory and keyed-mutex functionality, **when** a
compatible generated case runs on each queue family, **then**:

1. Vulkan can import the D3D11 keyed-mutex resource using the selected NT or KMT
   handle type;
2. Vulkan write → D3D11 copy/render → Vulkan read ownership transfers complete
   with the specified keyed mutex keys and resource barriers; and
3. the read result equals the write result byte-for-byte, with no collected
   validation failure.

If prerequisites are absent, the case may be reported `NotSupported`; that is
not a conformance failure. A supported case fails on an exception, a validation
failure, an unsuccessful synchronization operation, or a data mismatch.

## Legacy registration

The page and test path intentionally remain under the legacy name
`synchronization.win32_keyed_mutex`. Keep this page separate from any future
`synchronization2` documentation or test migration.
