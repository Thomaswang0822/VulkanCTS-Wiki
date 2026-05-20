# vktProtectedMemAttachmentClearTests.cpp

## Overview

[`vktProtectedMemAttachmentClearTests.cpp`](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentClearTests.cpp#L404-L410) registers protected attachment clear-op tests under `clear_op` and splits them by primary and secondary command-buffer type.

## Role

Implementation file that registers tests.

## Source Code

- Primary source: [`vktProtectedMemAttachmentClearTests.cpp`](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentClearTests.cpp#L1)

## Registration Hierarchy

```text
protected_memory.attachment.clear_op
├── primary
└── secondary
```

## Test Families

### primary — Primary command buffer
[`primary`](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentClearTests.cpp#L395-L398) contains `static` and `random` grandchildren.

### secondary — Secondary command buffer
[`secondary`](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentClearTests.cpp#L395-L409) contains the same one-level shape and is guarded for Vulkan SC support in `checkSupport`.

## Parameter Dimensions

Each command-buffer group contains fixed cases from `testData` and 10 random cases created at [`vktProtectedMemAttachmentClearTests.cpp`](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentClearTests.cpp#L364-L392).

## Support / Feature Requirements

Most cases call [`checkProtectedContextSupport()`](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L102-L124), which requires Vulkan 1.1 and the protected-memory feature when protected tests are enabled; several command-buffer variants also skip Vulkan SC secondary-command-buffer cases when the relevant property is absent.

## Verification Methods

[`iterate()`](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentClearTests.cpp#L115-L261) submits protected work and validates the resulting image at [`vktProtectedMemAttachmentClearTests.cpp`](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentClearTests.cpp#L256-L261).

## Test Principles Observed

- The same clear validation is exercised through primary and secondary command buffers.
- The registered group names come from [`getCmdBufferTypeStr()`](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L575-L584).

## Notes / Uncertainties

- Claims are limited to the inspected source and mustpass-observed registration paths.
