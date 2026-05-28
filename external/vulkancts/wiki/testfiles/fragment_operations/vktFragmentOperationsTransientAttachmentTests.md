# vktFragmentOperationsTransientAttachmentTests.cpp

## Overview

[`vktFragmentOperationsTransientAttachmentTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L1) implements the displayed `transient_attachment_bit` subgroup under [`fragment_operations`](../../categories/fragment_operations.md). The file verifies transient attachment load-store behavior for color, depth, and stencil attachments, crossed with lazily allocated and device-local memory-property selections.

## Role

Registration and implementation file. It owns the user-visible `transient_attachment_bit` subgroup and contains memory-type discovery, image and render-pass setup, input-attachment shader generation, support validation, and image comparison.

## Source Code

- Primary source: [`vktFragmentOperationsTransientAttachmentTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L1)
- Header: [`vktFragmentOperationsTransientAttachmentTests.hpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.hpp)

## Registration Hierarchy

```text
fragment_operations.transient_attachment_bit
├── color_load_store_op_test_lazy_bit
├── depth_load_store_op_test_lazy_bit
├── stencil_load_store_op_test_lazy_bit
├── color_load_store_op_test_local_bit
├── depth_load_store_op_test_local_bit
└── stencil_load_store_op_test_local_bit
```

Source: [`createTransientAttachmentTests()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L601-L627).

## Test Families

### Lazy-memory variants

The first three cases use `VK_MEMORY_PROPERTY_LAZILY_ALLOCATED_BIT` in the registration table at [`vktFragmentOperationsTransientAttachmentTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L612-L618):

- `color_load_store_op_test_lazy_bit`
- `depth_load_store_op_test_lazy_bit`
- `stencil_load_store_op_test_lazy_bit`

### Device-local variants

The remaining three cases use `VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT` in the same registration table at [`vktFragmentOperationsTransientAttachmentTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L616-L618):

- `color_load_store_op_test_local_bit`
- `depth_load_store_op_test_local_bit`
- `stencil_load_store_op_test_local_bit`

### Attachment-mode behavior

The attachment mode is carried by [`TestMode`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L56-L62):

- `MODE_COLOR`
- `MODE_DEPTH`
- `MODE_STENCIL`

The fragment shader reads the transient attachment as an input attachment with `subpassLoad()` or `usubpassInput` depending on mode in [`TransientAttachmentTest::initPrograms()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L252-L296).

## Parameter Dimensions

| Dimension | Observed values / source |
|---|---|
| Attachment mode | Color, depth, stencil in [`TestMode`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L56-L62) and the registration table at [`vktFragmentOperationsTransientAttachmentTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L612-L618) |
| Memory-property mode | `VK_MEMORY_PROPERTY_LAZILY_ALLOCATED_BIT` and `VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT` in the registration table at [`vktFragmentOperationsTransientAttachmentTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L612-L618) |
| Render size | `32 x 32` in the constructor arguments at [`vktFragmentOperationsTransientAttachmentTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L622-L623) |
| Test format | `VK_FORMAT_R8G8B8A8_UNORM`, `VK_FORMAT_D16_UNORM`, or supported stencil-capable format chosen in [`TransientAttachmentTest::checkSupport()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L307-L312) and mirrored in [`TransientAttachmentTestInstance`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L357-L365) |
| Image usage flags | Color path uses color-attachment plus transient plus input-attachment usage; depth-stencil paths use depth-stencil plus transient plus input-attachment usage in [`TransientAttachmentTestInstance`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L357-L361) |

## Support / Feature Requirements

[`TransientAttachmentTest::checkSupport()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L299-L329) derives memory-type indices matching the requested property flags via [`getMemoryTypeIndices()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L124-L134) and rejects the case when no such memory type exists at [`vktFragmentOperationsTransientAttachmentTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L314-L318). It also queries image-format properties for the transient attachment usage pattern at [`vktFragmentOperationsTransientAttachmentTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L320-L325) and rejects unsupported formats or zero sample-count support at [`vktFragmentOperationsTransientAttachmentTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L327-L328).

## Verification Methods

The fragment shader reads the transient attachment through an input attachment declaration at [`vktFragmentOperationsTransientAttachmentTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L281-L292). The test instance clears the transient attachment to mode-specific values: yellow for color, `0.5` depth for depth, and stencil value `128` for stencil at [`vktFragmentOperationsTransientAttachmentTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L521-L526). It then builds a reference image using the expected decoded output color at [`vktFragmentOperationsTransientAttachmentTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L576-L579) and compares rendered output with [`tcu::floatThresholdCompare()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L583-L584).

## Notes / Uncertainties

- This file is implementation-heavy but registers only six direct user-visible cases.
- The documented verification intentionally stays at the confirmed clear-value, input-attachment, and image-comparison level without inferring broader memory-allocation guarantees beyond the explicit support checks.
