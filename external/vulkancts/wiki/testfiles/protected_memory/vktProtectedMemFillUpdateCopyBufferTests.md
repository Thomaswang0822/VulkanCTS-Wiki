# vktProtectedMemFillUpdateCopyBufferTests.cpp

## Overview

[`vktProtectedMemFillUpdateCopyBufferTests.cpp`](../../../modules/vulkan/protected_memory/vktProtectedMemFillUpdateCopyBufferTests.cpp#L616-L647) registers three buffer operation roots: `fill`, `update`, and `copy`. The canonical tree below documents `fill`; `update` and `copy` use the same direct type children.

## Role

Implementation file that registers tests.

## Source Code

- Primary source: [`vktProtectedMemFillUpdateCopyBufferTests.cpp`](../../../modules/vulkan/protected_memory/vktProtectedMemFillUpdateCopyBufferTests.cpp#L1)

## Registration Hierarchy

```text
protected_memory.buffer.fill
├── float_buffer
├── integer_buffer
└── unsigned_buffer
```

## Test Families

### float_buffer — Floating-point buffer cases
[`float_buffer`](../../../modules/vulkan/protected_memory/vktProtectedMemFillUpdateCopyBufferTests.cpp#L430-L434) is registered for fill, update, and copy operations.

### integer_buffer — Signed integer buffer cases
[`integer_buffer`](../../../modules/vulkan/protected_memory/vktProtectedMemFillUpdateCopyBufferTests.cpp#L522-L526) is registered for fill, update, and copy operations.

### unsigned_buffer — Unsigned integer buffer cases
[`unsigned_buffer`](../../../modules/vulkan/protected_memory/vktProtectedMemFillUpdateCopyBufferTests.cpp#L606-L610) is registered for fill, update, and copy operations.

## Parameter Dimensions

The file defines operation roots `fill`, `update`, and `copy` at [`vktProtectedMemFillUpdateCopyBufferTests.cpp`](../../../modules/vulkan/protected_memory/vktProtectedMemFillUpdateCopyBufferTests.cpp#L616-L647). Each type group contains primary/secondary command-buffer grandchildren and static/random cases; float static data includes a `test_device_address` case requiring `VK_KHR_device_address_commands`.

## Support / Feature Requirements

[`checkSupport()`](../../../modules/vulkan/protected_memory/vktProtectedMemFillUpdateCopyBufferTests.cpp#L104-L114) calls protected-context support and additionally requires `VK_KHR_device_address_commands` for device-address command cases.

## Verification Methods

[`iterate()`](../../../modules/vulkan/protected_memory/vktProtectedMemFillUpdateCopyBufferTests.cpp#L141-L335) validates the destination buffer with [`validateBuffer()`](../../../modules/vulkan/protected_memory/vktProtectedMemFillUpdateCopyBufferTests.cpp#L331-L335).

## Test Principles Observed

- One implementation file registers three sibling operation roots.
- The documented hierarchy tree intentionally uses one canonical root while the prose records the additional roots and their shared child shape.

## Notes / Uncertainties

- Claims are limited to the inspected source and mustpass-observed registration paths.
