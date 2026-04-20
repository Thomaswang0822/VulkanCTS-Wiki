# vktApiCopiesAndBlittingTests.cpp

## Overview

Tests Vulkan copy and blit operations including buffer-to-buffer, buffer-to-image, image-to-image copies, and resolve operations.

## Source Code

[vktApiCopiesAndBlittingTests.cpp](../../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp)

## Test Hierarchy

```
copy_and_blit
├── core                           # Core copy/blit functionality
├── dedicated_allocation           # Tests with dedicated allocation
├── copy_commands2                 # Tests using VK_KHR_copy_commands2
├── sparse                         # Sparse binding tests
├── multiplane_transfer_queue      # Multiplane image transfer tests
├── dynamic_state_meta_ops         # Dynamic state during copy operations
├── copy_memory_indirect           # Indirect copy via VK_KHR_copy_memory_indirect
├── device_address                 # Device address-based copies
└── reinterpretation               # Format reinterpretation tests
```

## Test Families

### 1. core

**Purpose**: Core copy and blit functionality with suballocated memory.

**Sub-families** (from [line 232-239](../../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L232)):
- `image_to_image` - Image-to-image copy tests
- `image_to_buffer` - Image-to-buffer copy tests
- `buffer_to_image` - Buffer-to-image copy tests
- `buffer_to_buffer` - Buffer-to-buffer copy tests
- `buffer_to_depthstencil` - Buffer-to-depth/stencil copy tests
- `depthstencil_to_buffer` - Depth/stencil-to-buffer copy tests
- `resolve_image` - Image resolve tests
- `blitting` - Image blitting tests
- `use_after_copy` - Verify images usable after copy
- `memory_to_image_indirect` - Indirect memory-to-image copies
- `copy_buffer_to_buffer_offset` - Buffer offset copy tests

### 2. dedicated_allocation

**Purpose**: Same tests as `core` but with dedicated memory allocation.

### 3. copy_commands2

**Purpose**: Tests using `VK_KHR_copy_commands2` extension for extended copy commands.

### 4. sparse

**Purpose**: Copy tests with sparse binding memory.

### 5. copy_memory_indirect

**Purpose**: Indirect copy operations via `VK_KHR_copy_memory_indirect` extension.

### 6. device_address

**Purpose**: Copy operations using device addresses (buffer device address feature).

### 7. reinterpretation

**Purpose**: Format reinterpretation during copy operations.

## Parameter Dimensions

| Parameter | Values | Notes |
|-----------|--------|-------|
| **Allocation Kind** | SUBALLOCATED, DEDICATED | Memory allocation strategy |
| **Extension Flags** | 0, COPY_COMMANDS_2, SPARSE_BINDING, DEVICE_ADDRESS, INDIRECT_COPY | Feature flags |
| **Queue Selection** | Universal, ComputeOnly, TransferOnly | Queue type for operations |
| **Format** | Various (see individual test files) | Image/buffer formats |
| **Layout** | TRANSFER_SRC/DST_OPTIMAL, GENERAL | Image layout |
| **Tiling** | OPTIMAL, LINEAR | Image tiling mode |

## Key Source Files

This test file includes functionality from:

| File | Purpose |
|------|---------|
| [vktApiCopyImageToImageTests.cpp](../../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp) | Image-to-image copy tests |
| [vktApiCopyBufferToBufferTests.cpp](../../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp) | Buffer-to-buffer copy tests |
| [vktApiCopyImageToBufferTests.cpp](../../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp) | Image-to-buffer copy tests |
| [vktApiCopyBufferToImageTests.cpp](../../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp) | Buffer-to-image copy tests |
| [vktApiCopyBufferToDepthStencilTests.cpp](../../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp) | Buffer-to-depth/stencil tests |
| [vktApiCopyDepthStencilToBufferTests.cpp](../../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp) | Depth/stencil-to-buffer tests |
| [vktApiBlittingTests.cpp](../../../../modules/vulkan/api/vktApiBlittingTests.cpp) | Image blitting tests |
| [vktApiResolveTests.cpp](../../../../modules/vulkan/api/vktApiResolveTests.cpp) | Image resolve tests |
| [vktApiUseAfterCopyTests.cpp](../../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp) | Use-after-copy verification |

## Verification Methods

- **Content comparison**: Compare copied data against expected values
- **Image comparison**: Compare rendered output for depth/stencil tests
- **Format verification**: Ensure format-specific handling is correct
- **Layout transitions**: Verify proper layout transitions during copies

## Test Principles

1. **Comprehensive format coverage**: Test all supported formats for copy operations
2. **Queue compatibility**: Verify copies work on different queue types
3. **Memory handling**: Test both suballocated and dedicated memory
4. **Extension support**: Test extended copy command features
5. **Corner cases**: Test edge cases like empty regions, overlapping copies
