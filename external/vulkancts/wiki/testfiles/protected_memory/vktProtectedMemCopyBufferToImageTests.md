# vktProtectedMemCopyBufferToImageTests.cpp

## Overview

[`vktProtectedMemCopyBufferToImageTests.cpp`](../../../modules/vulkan/protected_memory/vktProtectedMemCopyBufferToImageTests.cpp#L1) registers protected image copy tests under `copy_buffer_to_image` with primary and secondary command-buffer groups.

## Role

Implementation file that registers tests.

## Source Code

- Primary source: [`vktProtectedMemCopyBufferToImageTests.cpp`](../../../modules/vulkan/protected_memory/vktProtectedMemCopyBufferToImageTests.cpp#L1)

## Registration Hierarchy

```text
protected_memory.image.copy_buffer_to_image
├── primary
└── secondary
```

## Test Families

### primary — Primary command buffer
[`primary`](../../../modules/vulkan/protected_memory/vktProtectedMemCopyBufferToImageTests.cpp#L385-L436) contains `static` and `random` generated children.

### secondary — Secondary command buffer
[`secondary`](../../../modules/vulkan/protected_memory/vktProtectedMemCopyBufferToImageTests.cpp#L385-L436) is registered from the same builder with secondary command-buffer parameters.

## Parameter Dimensions

Each command-buffer group contains fixed cases from local `testData` plus 10 random cases; the command-buffer group names come from [`getCmdBufferTypeStr()`](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L575-L584).

## Support / Feature Requirements

Most cases call [`checkProtectedContextSupport()`](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L102-L124), which requires Vulkan 1.1 and the protected-memory feature when protected tests are enabled; several command-buffer variants also skip Vulkan SC secondary-command-buffer cases when the relevant property is absent. The Vulkan SC secondary-command-buffer property check is visible at [`vktProtectedMemCopyBufferToImageTests.cpp`](../../../modules/vulkan/protected_memory/vktProtectedMemCopyBufferToImageTests.cpp#L95-L105).

## Verification Methods

[`iterate()`](../../../modules/vulkan/protected_memory/vktProtectedMemCopyBufferToImageTests.cpp#L128-L291) validates the destination image with [`validateImage()`](../../../modules/vulkan/protected_memory/vktProtectedMemCopyBufferToImageTests.cpp#L286-L291).

## Test Principles Observed

- The page documents the registered one-level split by command-buffer type.
- Static and random data paths share the same image-validation principle.

## Notes / Uncertainties

- Claims are limited to the inspected source and mustpass-observed registration paths.
