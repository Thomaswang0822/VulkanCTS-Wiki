# vktRasterizationOrderAttachmentAccessTests.cpp

## Overview

[`vktRasterizationOrderAttachmentAccessTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L1) implements the non-VulkanSC `rasterization_order_attachment_access` subgroup. It registers color, depth, and stencil attachment-order tests through [`createRasterizationOrderAttachmentAccessTests()`](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L1831-L1851).

## Role

Implementation file.

## Source Code

- Primary source: [`vktRasterizationOrderAttachmentAccessTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L1)
- Header: [`vktRasterizationOrderAttachmentAccessTests.hpp`](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.hpp#L35)

## Registration Hierarchy

```text
rasterization.rasterization_order_attachment_access
├── format_float
├── format_integer
├── depth
└── stencil
```

## Test Families

### format_float — Floating-point color attachment formats

`format_float` is created by [`createRasterizationOrderAttachmentAccessFormatTests()`](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L1802-L1817) with `integerFormat` false, then expands attachment-count prefixes `attachments_1_`, `attachments_4_`, and `attachments_8_` at [`vktRasterizationOrderAttachmentAccessTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L1805-L1828). Each attachment-count branch has sample-count children and leaf cases `multi_draw_barriers`, `multi_draw`, `multi_primitives`, `multi_instances`, and `all` from [`leafTestCreateParams[]`](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L1708-L1756).

### format_integer — Integer color attachment formats

`format_integer` follows the same attachment-count, sample-count, and leaf-case expansion as `format_float`, but is created with `integerFormat` true at [`vktRasterizationOrderAttachmentAccessTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L1810-L1817).

### depth — Depth attachment order

The `depth` direct child is created in [`createRasterizationOrderAttachmentAccessTests()`](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L1839-L1848) and populated by [`createRasterizationOrderAttachmentAccessTestVariations()`](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L1844-L1845). It varies sample counts 1, 2, 4, 8, 16, 32, and 64 at [`sampleCountValues[]`](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L1759-L1763) and uses the same five leaf overlap patterns.

### stencil — Stencil attachment order

The `stencil` direct child is created beside `depth` at [`vktRasterizationOrderAttachmentAccessTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L1839-L1849). It uses the same sample-count and leaf overlap-pattern generation through [`createRasterizationOrderAttachmentAccessTestVariations()`](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L1846-L1847).

## Parameter Dimensions

| Dimension | Observed values / source |
|---|---|
| Attachment class | `format_float`, `format_integer`, `depth`, and `stencil` at [`createRasterizationOrderAttachmentAccessTests()`](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L1835-L1849) |
| Color attachment count | 1, 4, and 8 from [`inputNum[]`](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L1805-L1826) |
| Sample count | 1, 2, 4, 8, 16, 32, and 64 at [`sampleCountValues[]`](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L1759-L1763) |
| Synchronization / overlap pattern | Explicit barriers, multi-draw, multi-primitives, multi-instances, and all-overlap cases at [`leafTestCreateParams[]`](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L1715-L1756) |

## Support / Feature Requirements

All cases require instance functionality `VK_KHR_get_physical_device_properties2` at [`AttachmentAccessOrderTestCase::checkSupport()`](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L832-L835). When explicit synchronization is not used, the test requires either `VK_ARM_rasterization_order_attachment_access` or `VK_EXT_rasterization_order_attachment_access` at [`vktRasterizationOrderAttachmentAccessTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L836-L841).

## Verification Methods

The inspected registration and support regions show that each leaf test is constructed as a depth, stencil, or color `AttachmentAccessOrder*TestCase` with explicit synchronization and overlap parameters at [`vktRasterizationOrderAttachmentAccessTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L1774-L1798). The specific result-comparison logic is implemented earlier in the same source file but was not exhaustively inspected for this page; therefore this page does not claim a particular comparison helper beyond the visible leaf-case construction and support checks.

## Test Principles Observed

- **Extension-vs-barrier contrast**: `multi_draw_barriers` uses explicit synchronization, while other overlap cases require rasterization-order attachment-access functionality when synchronization is not explicit.
- **Attachment-class coverage**: color float, color integer, depth, and stencil attachment paths are registered as separate direct children.
- **Sample-count sweep**: each variation function expands the same sample-count sequence from 1 to 64 samples.

## Notes / Uncertainties

- Verification details beyond case construction and support gating were not fully inspected in this run; claims here are limited to visible registration parameters and support checks.
