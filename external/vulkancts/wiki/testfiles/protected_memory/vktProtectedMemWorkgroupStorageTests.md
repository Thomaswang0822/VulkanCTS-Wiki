# vktProtectedMemWorkgroupStorageTests.cpp

## Overview

[`vktProtectedMemWorkgroupStorageTests.cpp`](../../../modules/vulkan/protected_memory/vktProtectedMemWorkgroupStorageTests.cpp#L370-L381) registers protected workgroup-storage tests under `workgroupstorage` with one child per shared-memory size.

## Role

Implementation file that registers tests.

## Source Code

- Primary source: [`vktProtectedMemWorkgroupStorageTests.cpp`](../../../modules/vulkan/protected_memory/vktProtectedMemWorkgroupStorageTests.cpp#L1)

## Registration Hierarchy

```text
protected_memory.workgroupstorage
├── memsize_1
├── memsize_4
├── memsize_5
├── memsize_60
├── memsize_101
└── memsize_503
```

## Test Families

### memsize_1 — 1 byte
Generated from the `sharedMemSizes` array.

### memsize_4 — 4 bytes
Generated from the `sharedMemSizes` array.

### memsize_5 — 5 bytes
Generated from the `sharedMemSizes` array.

### memsize_60 — 60 bytes
Generated from the `sharedMemSizes` array.

### memsize_101 — 101 bytes
Generated from the `sharedMemSizes` array.

### memsize_503 — 503 bytes
Generated from the `sharedMemSizes` array.

## Parameter Dimensions

The shared-memory sizes are exactly `{1, 4, 5, 60, 101, 503}` in [`sharedMemSizes`](../../../modules/vulkan/protected_memory/vktProtectedMemWorkgroupStorageTests.cpp#L374-L380).

## Support / Feature Requirements

Most cases call [`checkProtectedContextSupport()`](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L102-L124), which requires Vulkan 1.1 and the protected-memory feature when protected tests are enabled; several command-buffer variants also skip Vulkan SC secondary-command-buffer cases when the relevant property is absent.

## Verification Methods

[`validateResult()`](../../../modules/vulkan/protected_memory/vktProtectedMemWorkgroupStorageTests.cpp#L345-L363) samples expected texture values and validates the resulting image.

## Test Principles Observed

- The tests vary workgroup shared-memory size and compare shader output through image validation.

## Notes / Uncertainties

- Claims are limited to the inspected source and mustpass-observed registration paths.
