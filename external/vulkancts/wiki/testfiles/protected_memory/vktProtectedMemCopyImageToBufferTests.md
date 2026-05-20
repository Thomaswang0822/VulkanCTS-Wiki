# vktProtectedMemCopyImageToBufferTests.cpp

## Overview

[`vktProtectedMemCopyImageToBufferTests.cpp`](../../../modules/vulkan/protected_memory/vktProtectedMemCopyImageToBufferTests.cpp#L400-L405) registers protected image-to-buffer copy tests under `copy_image_to_float_buffer` with primary and secondary command-buffer groups.

## Role

Implementation file that registers tests.

## Source Code

- Primary source: [`vktProtectedMemCopyImageToBufferTests.cpp`](../../../modules/vulkan/protected_memory/vktProtectedMemCopyImageToBufferTests.cpp#L1)

## Registration Hierarchy

```text
protected_memory.buffer.copy_image_to_float_buffer
├── primary
└── secondary
```

## Test Families

### primary — Primary command buffer
[`primary`](../../../modules/vulkan/protected_memory/vktProtectedMemCopyImageToBufferTests.cpp#L390-L394) contains `static` and `random` grandchildren.

### secondary — Secondary command buffer
[`secondary`](../../../modules/vulkan/protected_memory/vktProtectedMemCopyImageToBufferTests.cpp#L400-L405) is registered from the same builder with secondary command buffers.

## Parameter Dimensions

Static and random cases are generated at [`vktProtectedMemCopyImageToBufferTests.cpp`](../../../modules/vulkan/protected_memory/vktProtectedMemCopyImageToBufferTests.cpp#L337-L388). Each case is emitted for default and `_protected_access` naming variants when pipeline-protected access is requested.

## Support / Feature Requirements

Support uses [`checkProtectedContextSupport(context, false, m_pipelineProtectedAccess)`](../../../modules/vulkan/protected_memory/vktProtectedMemCopyImageToBufferTests.cpp#L107-L110); protected-access variants request `VK_EXT_pipeline_protected_access` when constructing the instance.

## Verification Methods

[`iterate()`](../../../modules/vulkan/protected_memory/vktProtectedMemCopyImageToBufferTests.cpp#L139-L300) validates the destination buffer with [`validateBuffer()`](../../../modules/vulkan/protected_memory/vktProtectedMemCopyImageToBufferTests.cpp#L296-L300).

## Test Principles Observed

- The tests exercise protected copies from image contents into buffer-visible validation data.
- Pipeline-protected-access variants are visible in the generated case names, not as direct hierarchy children at this page root.

## Notes / Uncertainties

- Claims are limited to the inspected source and mustpass-observed registration paths.
