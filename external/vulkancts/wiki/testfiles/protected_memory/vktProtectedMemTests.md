# vktProtectedMemTests.cpp

## Overview

[`vktProtectedMemTests.cpp`](../../../modules/vulkan/protected_memory/vktProtectedMemTests.cpp#L50-L104) is the protected-memory category dispatcher. It creates the root group from the supplied category name and adds attachment, image, buffer, SSBO, interaction, workgroup-storage, and stack branches.

## Role

Registration / dispatcher file.

## Source Code

- Primary source: [`vktProtectedMemTests.cpp`](../../../modules/vulkan/protected_memory/vktProtectedMemTests.cpp#L1)

## Registration Hierarchy

```text
protected_memory
├── attachment
├── image
├── buffer
├── ssbo
├── interaction
├── workgroupstorage
└── stack
```

## Test Families

### attachment — Attachment operations
[`attachment`](../../../modules/vulkan/protected_memory/vktProtectedMemTests.cpp#L54-L60) contains `load_op` and `clear_op` children.

### image — Image operations
[`image`](../../../modules/vulkan/protected_memory/vktProtectedMemTests.cpp#L62-L70) contains copy, blit, clear-color, buffer-to-image, and shader image access children.

### buffer — Buffer operations
[`buffer`](../../../modules/vulkan/protected_memory/vktProtectedMemTests.cpp#L73-L80) contains fill, update, copy, and image-to-buffer children.

### ssbo — Storage-buffer shader operations
[`ssbo`](../../../modules/vulkan/protected_memory/vktProtectedMemTests.cpp#L83-L89) contains read, write, and atomic children.

### interaction — External interaction tests
[`interaction`](../../../modules/vulkan/protected_memory/vktProtectedMemTests.cpp#L92-L98) contains WSI outside Vulkan SC and YCbCr conversion tests.

### workgroupstorage — Workgroup storage
[`workgroupstorage`](../../../modules/vulkan/protected_memory/vktProtectedMemTests.cpp#L101) is registered directly under the category.

### stack — Stack storage
[`stack`](../../../modules/vulkan/protected_memory/vktProtectedMemTests.cpp#L102) is registered directly under the category.

## Parameter Dimensions

This dispatcher does not define per-case parameter matrices; it delegates to implementation files included at [`vktProtectedMemTests.cpp`](../../../modules/vulkan/protected_memory/vktProtectedMemTests.cpp#L30-L43).

## Support / Feature Requirements

No support checks are implemented in the dispatcher; implementation files call the protected-context helpers.

## Verification Methods

No verification logic is implemented in the dispatcher; implementation files perform image, buffer, or WSI/YCbCr validation.

## Test Principles Observed

- The file separates category structure from implementation logic using factory functions and locally assembled branch groups.
- The WSI branch is conditionally excluded from Vulkan SC builds by the [`CTS_USES_VULKANSC`](../../../modules/vulkan/protected_memory/vktProtectedMemTests.cpp#L94-L96) guard.

## Notes / Uncertainties

- Claims are limited to the inspected source and mustpass-observed registration paths.
