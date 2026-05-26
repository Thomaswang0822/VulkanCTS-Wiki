# vktImageDepthStencilDescriptorTests ([source](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp))

## Overview

Tests that verify depth/stencil images can be used as descriptors in shader pipelines. The file covers various combinations of image layouts, depth/stencil formats, and access types (read-only attachment, input attachment, sampled image) for both graphics and compute pipelines. It validates that depth/stencil images can be bound as descriptors and that shader operations correctly read from or write through these descriptors.

## Role of File

Implementation file that registers the `depth_stencil_descriptor` test group and provides complete test implementations. Contains test case class, test instance class, and the factory function that populates the test hierarchy.

## Source Code

- Implementation: [vktImageDepthStencilDescriptorTests.cpp](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp)
- Header: [vktImageDepthStencilDescriptorTests.hpp](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.hpp)

## Registration Hierarchy

```text
image.depth_stencil_descriptor
├── depth_read_only_stencil_attachment_optimal
├── depth_attachment_stencil_read_only_optimal
├── depth_read_only_optimal
└── stencil_read_only_optimal
```

Evidence:
- `depth_stencil_descriptor` group created by [`createImageDepthStencilDescriptorTests()`](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L1589-L1759)
- Layout subgroups added at lines 1624-1757 with names derived from layout enum suffixes (e.g., `depth_read_only_stencil_attachment_optimal` from `VK_IMAGE_LAYOUT_DEPTH_READ_ONLY_STENCIL_ATTACHMENT_OPTIMAL`)
- Format subgroups created inside each layout group at lines 1632-1753
- Individual test cases added via `addTest` lambda at lines 1654-1662

## Test Families

### depth_read_only_stencil_attachment_optimal — Depth read-only, stencil attachment layout

Tests using `VK_IMAGE_LAYOUT_DEPTH_READ_ONLY_STENCIL_ATTACHMENT_OPTIMAL`. The depth aspect is read-only while stencil is read-write. Format subgroups iterate over all supported depth/stencil formats.

### depth_attachment_stencil_read_only_optimal — Depth attachment, stencil read-only layout

Tests using `VK_IMAGE_LAYOUT_DEPTH_ATTACHMENT_STENCIL_READ_ONLY_OPTIMAL`. The stencil aspect is read-only while depth is read-write. Format subgroups iterate over all supported depth/stencil formats.

### depth_read_only_optimal — Depth-only read-only layout

Tests using `VK_IMAGE_LAYOUT_DEPTH_READ_ONLY_OPTIMAL`. Only the depth aspect is accessible (read-only); stencil aspect is inaccessible. Format subgroups iterate over depth-only formats.

### stencil_read_only_optimal — Stencil-only read-only layout

Tests using `VK_IMAGE_LAYOUT_STENCIL_READ_ONLY_OPTIMAL`. Only the stencil aspect is accessible (read-only); depth aspect is inaccessible. Format subgroups iterate over stencil-only formats.

### Per-format test variations

Each format subgroup generates combinations of:
- **Access type for depth**: NONE, RO (read-only attachment), RW (read-write attachment)
- **Access type for stencil**: NONE, RO (read-only attachment), RW (read-write attachment)
- **Read-only access combinations for RO aspects**:
  - `DS_ATTACHMENT` - depth/stencil attachment read
  - `INPUT_ATTACHMENT` - input attachment read
  - `SAMPLED` - sampled image read
  - `DS_SAMPLED` - both attachment and sampled
  - `INPUT_SAMPLED` - both input attachment and sampled
- **Compute variants**: When a test is compute-compatible (uses only SAMPLED access), a `_compute` variant is added

## Parameter Dimensions

| Dimension | Values | Source |
|-----------|--------|--------|
| Image Format | D16_UNORM, X8_D24_UNORM_PACK32, D32_SFLOAT, S8_UINT, D16_UNORM_S8_UINT, D24_UNORM_S8_UINT, D32_SFLOAT_S8_UINT | [line 1593-1596](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L1593-L1596) |
| Image Layout | DEPTH_READ_ONLY_STENCIL_ATTACHMENT_OPTIMAL, DEPTH_ATTACHMENT_STENCIL_READ_ONLY_OPTIMAL, DEPTH_READ_ONLY_OPTIMAL, STENCIL_READ_ONLY_OPTIMAL | [line 1599-1604](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L1599-L1604) |
| Image Type | VK_IMAGE_TYPE_2D | [line 476](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L476) |
| Image Extent | 8x8x1 | [line 61](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L61) |
| Sample Count | VK_SAMPLE_COUNT_1_BIT | [line 752](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L752) |
| Color Format | VK_FORMAT_R8G8B8A8_UNORM | [line 66](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L66) |
| Depth Storage Format | VK_FORMAT_R32_SFLOAT | [line 71](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L71) |
| Stencil Storage Format | VK_FORMAT_R32_UINT | [line 76](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L76) |

## Support / Feature Requirements

| Requirement | Condition | Source |
|-------------|-----------|--------|
| VK_KHR_create_renderpass2 | Graphics tests | [line 460](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L460) |
| VK_KHR_maintenance10 | Compute tests | [line 465](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L465) |
| VK_KHR_format_feature_flags2 | Compute tests | [line 466](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L466) |
| VK_KHR_maintenance2 | DEPTH_READ_ONLY_STENCIL_ATTACHMENT_OPTIMAL and DEPTH_ATTACHMENT_STENCIL_READ_ONLY_OPTIMAL layouts | [line 87-88](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L87-88) |
| VK_KHR_separate_depth_stencil_layouts | DEPTH_READ_ONLY_OPTIMAL and STENCIL_READ_ONLY_OPTIMAL layouts | [line 92-93](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L92-93) |
| VK_FORMAT_FEATURE_2_DEPTH_COPY_ON_COMPUTE_QUEUE_BIT_KHR | Depth aspect in compute tests | [line 500-503](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L500-503) |
| VK_FORMAT_FEATURE_2_STENCIL_COPY_ON_COMPUTE_QUEUE_BIT_KHR | Stencil aspect in compute tests | [line 506-511](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L506-511) |
| Format support | vkGetPhysicalDeviceImageFormatProperties must succeed | [line 481-486](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L481-486) |

## Verification Methods

### Image comparison

Tests verify image contents by copying to host-visible buffers and comparing against reference data:
- **Color attachment**: Compared against expected pass color (green) or fail color (red) at [lines 1493-1501](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L1493-1501)
- **Depth buffer**: Compared using `tcu::dsThresholdCompare` with 0.1 threshold at [lines 1504-1522](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L1504-1522)
- **Stencil buffer**: Compared using `tcu::dsThresholdCompare` at [lines 1525-1543](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L1525-1543)
- **Storage images**: Depth aspect compared with `tcu::floatThresholdCompare` at [lines 1558-1563](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L1558-1563); stencil aspect compared with `tcu::intThresholdCompare` at [lines 1565-1578](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L1565-1578)

## Test Principles Observed

- **Descriptor binding validation**: Tests bind depth/stencil images as sampled images or input attachments and verify shader reads produce correct results
- **Layout compatibility**: Tests verify that each image layout correctly enables the intended aspect access patterns
- **Incompatibility detection**: Input attachment access is incompatible with depth/stencil attachment access when both aspects exist, as enforced by `incompatibleInputAttachmentAccess` at [lines 177-196](../../../modules/vulkan/image/vktImageDepthStencilDescriptorTests.cpp#L177-196)
- **Compute compatibility**: Only tests using only SAMPLED access can run on compute queues; input attachments and depth/stencil attachments require render pass context
- **Aspect separation**: Depth and stencil aspects can have independent access types based on the selected layout
- **Graphics pipeline dual-draw**: When stencil test is enabled, two draw calls are issued with different stencil reference values to verify test pass/fail behavior

## Notes / Uncertainties

- The test uses `VK_IMAGE_TILING_OPTIMAL` exclusively; linear tiling is not tested in this file
- Test naming follows pattern `{depth_access}_{depth_ro_accesses}_stencil_{stencil_access}_{stencil_ro_accesses}` or `{aspect}_{access}` for single-aspect formats
- Compute variants are named with `_compute` suffix and use different coordinate computation (gl_GlobalInvocationID vs gl_FragCoord)
- The file does not test separate depth/stencil framebuffer access features, which are covered in `vktImageDepthStencilSeparateTests`
