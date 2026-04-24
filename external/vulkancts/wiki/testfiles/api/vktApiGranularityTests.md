# [vktApiGranularityTests.cpp](../../modules/vulkan/api/vktApiGranularityTests.cpp#L1)

## Overview

Tests the `vkGetRenderAreaGranularity` and `vkGetRenderingAreaGranularity` APIs, which report the render area granularity for a given set of framebuffer attachments. The file validates that granularity values are consistent whether queried before or during a render pass, and that they satisfy spec-mandated constraints.

## Role of File

Implementation-heavy. Contains a full test class (`GranularityCase`/`GranularityInstance`) with Vulkan image creation, render pass setup, and three test modes covering legacy render passes, in-render-pass queries, and dynamic rendering.

## Source Code

- Implementation: [vktApiGranularityTests.cpp](../../modules/vulkan/api/vktApiGranularityTests.cpp#L1)
- Header: [vktApiGranularityTests.hpp](../../modules/vulkan/api/vktApiGranularityTests.hpp#L1)
- Parent registration: `createGranularityQueryTests()` declared at [L36](../../modules/vulkan/api/vktApiGranularityTests.hpp#L36)

## Registration Path

```
api
  +-- granularity
        +-- single
        +-- multi
        +-- random
        +-- in_render_pass
        +-- in_dynamic_render_pass   (non-VKSC only)
```

## Test Hierarchy

```
granularity
  +-- single
  |     +-- <format_name>  (one per VkFormat from 1..VK_FORMAT_D32_SFLOAT_S8_UINT)
  |           Single attachment with random dimensions.
  +-- multi
  |     +-- <format_name>  (one per VkFormat from 1..VK_FORMAT_D32_SFLOAT_S8_UINT)
  |           Multiple attachments of the same format with same random dimensions.
  +-- random
  |     +-- <format_name>  (one per VkFormat from 1..VK_FORMAT_D32_SFLOAT_S8_UINT)
  |           One primary format attachment + random mandatory-format attachments.
  +-- in_render_pass
  |     +-- <format_name>  (one per VkFormat from 1..VK_FORMAT_D32_SFLOAT_S8_UINT)
  |           Queries granularity inside an active render pass.
  +-- in_dynamic_render_pass  (non-VKSC only)
        +-- <format_name>  (one per VkFormat from 1..VK_FORMAT_D32_SFLOAT_S8_UINT)
              Queries granularity inside an active dynamic render pass.
```

## Test Families

### single

Tests `vkGetRenderAreaGranularity` with a single attachment of each format. Creates one image per format with random dimensions (1..500), builds a render pass, and queries granularity before the render pass begins (TestMode::NO_RENDER_PASS).

- Registered at [L541](../../modules/vulkan/api/vktApiGranularityTests.cpp#L541)

### multi

Tests granularity with multiple attachments sharing the same format and dimensions. Creates 2..10 identical attachments, builds a render pass, and queries granularity.

- Registered at [L551](../../modules/vulkan/api/vktApiGranularityTests.cpp#L551)

### random

Tests granularity with a mix of formats. Creates one attachment of the primary format plus 2..10 additional attachments using randomly selected mandatory formats, each with random dimensions.

- Registered at [L567](../../modules/vulkan/api/vktApiGranularityTests.cpp#L567)

### in_render_pass

Queries `vkGetRenderAreaGranularity` both before and inside an active render pass (between `beginRenderPass` and `endRenderPass`). Verifies that the granularity values are identical in both cases.

- TestMode: `USE_RENDER_PASS` at [L574](../../modules/vulkan/api/vktApiGranularityTests.cpp#L574)

### in_dynamic_render_pass (non-VKSC only)

Queries `vkGetRenderingAreaGranularity` (VK_KHR_maintenance5) both before and inside an active dynamic render pass (between `cmdBeginRendering` and `cmdEndRendering`). Verifies consistency.

- TestMode: `USE_DYNAMIC_RENDER_PASS` at [L578](../../modules/vulkan/api/vktApiGranularityTests.cpp#L578)
- Guarded by `#ifndef CTS_USES_VULKANSC` at [L576](../../modules/vulkan/api/vktApiGranularityTests.cpp#L576)

## Parameter Dimensions

| Dimension | Observed Values | Notes |
|-----------|----------------|-------|
| Format range | VK_FORMAT range 1..VK_FORMAT_D32_SFLOAT_S8_UINT | [L531](../../modules/vulkan/api/vktApiGranularityTests.cpp#L531) |
| Attachment dimensions | Random 1..500 per axis | [L528](../../modules/vulkan/api/vktApiGranularityTests.cpp#L528) |
| Multi attachment count | Random 2..10 | [L529](../../modules/vulkan/api/vktApiGranularityTests.cpp#L529) |
| Random extra formats | From mandatoryFormats array (46 entries) | [L477](../../modules/vulkan/api/vktApiGranularityTests.cpp#L477) |
| TestMode | NO_RENDER_PASS, USE_RENDER_PASS, USE_DYNAMIC_RENDER_PASS | [L57](../../modules/vulkan/api/vktApiGranularityTests.cpp#L57) |
| Random seed | 215 | [L475](../../modules/vulkan/api/vktApiGranularityTests.cpp#L475) |

## Support / Feature Requirements

| Requirement | Gate | Location |
|-------------|------|----------|
| Format support | `checkSupport` queries `getPhysicalDeviceFormatProperties`; throws NotSupportedError if format lacks `COLOR_ATTACHMENT_BIT` or `DEPTH_STENCIL_ATTACHMENT_BIT` | [L437](../../modules/vulkan/api/vktApiGranularityTests.cpp#L437) |
| VK_KHR_maintenance5 | Required for `USE_DYNAMIC_RENDER_PASS` mode | [L453](../../modules/vulkan/api/vktApiGranularityTests.cpp#L453) |

## Verification Methods

- **Granularity validity**: `granularity.width >= 1 && granularity.height >= 1` at [L393](../../modules/vulkan/api/vktApiGranularityTests.cpp#L393)
- **Pre/post consistency**: `prePassGranularity.width == granularity.width && prePassGranularity.height == granularity.height` at [L394](../../modules/vulkan/api/vktApiGranularityTests.cpp#L394)
- **Framebuffer limits**: `granularity.width <= maxFramebufferWidth && granularity.height <= maxFramebufferHeight` at [L395](../../modules/vulkan/api/vktApiGranularityTests.cpp#L395)

## Test Principles Observed

- **Invariance**: Granularity must be the same before and during a render pass
- **Spec compliance**: Granularity must be at least 1x1 and within framebuffer limits
- **Format coverage**: Iterates over all defined formats to maximize coverage

## Notes / Uncertainties

- The `checkSupport` method checks for both `VK_FORMAT_FEATURE_COLOR_ATTACHMENT_BIT` and `VK_FORMAT_FEATURE_DEPTH_STENCIL_ATTACHMENT_BIT` combined with OR at [L442](../../modules/vulkan/api/vktApiGranularityTests.cpp#L442), but depth/stencil formats typically only have `DEPTH_STENCIL_ATTACHMENT_BIT`. This may cause some depth/stencil formats to be incorrectly skipped if they lack `COLOR_ATTACHMENT_BIT`.
- The `mandatoryFormats` array at [L477](../../modules/vulkan/api/vktApiGranularityTests.cpp#L477) includes `VK_FORMAT_D16_UNORM` and `VK_FORMAT_D32_SFLOAT` but not `VK_FORMAT_S8_UINT` or combined depth-stencil formats.
- The framebuffer created in `initObjects` always has dimensions 1x1 at [L268](../../modules/vulkan/api/vktApiGranularityTests.cpp#L268), while the images may have larger random dimensions. This is valid since the render area granularity query depends on the render pass structure, not the framebuffer size.
