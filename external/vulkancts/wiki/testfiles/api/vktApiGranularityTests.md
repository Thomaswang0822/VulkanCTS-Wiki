# [vktApiGranularityTests.cpp](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L1)

## Overview

Tests vkGetRenderAreaGranularity and vkGetRenderingAreaGranularity (VK_KHR_maintenance5). Verifies that the returned granularity values are valid (at least 1x1, consistent before and during a render pass, and within device limits) across various attachment format combinations and render pass modes.

## Role of File

Implementation-heavy. Contains all test logic, helper classes, and the registration function [createGranularityQueryTests()](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L463).

## Source Code

- Implementation: [vktApiGranularityTests.cpp](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L1)
- Header: [vktApiGranularityTests.hpp](../../../modules/vulkan/api/vktApiGranularityTests.hpp#L1)
- Parent registration: [vktApiTests.cpp](../../../modules/vulkan/api/vktApiTests.cpp#L114)

## Registration Path

```
api
  +-- granularity
```

## Test Hierarchy

```
granularity
  +-- single
  |     +-- <format_name>                  [one attachment per format 1..55]
  +-- multi
  |     +-- <format_name>                  [multiple attachments of same format]
  +-- random
  |     +-- <format_name>                  [one attachment + random mandatory formats]
  +-- in_render_pass
  |     +-- <format_name>                  [granularity queried inside render pass]
  +-- in_dynamic_render_pass               [non-SC]
        +-- <format_name>                  [granularity queried inside dynamic render pass]
```

## Test Families

### Single Attachment Granularity

[GranularityInstance](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L86) with TestMode::NO_RENDER_PASS creates a single attachment of each format from VK_FORMAT_R4G4_UNORM_PACK8 through VK_FORMAT_D32_SFLOAT_S8_UINT and queries the render area granularity. Verifies that the granularity is at least 1x1 and within device limits.

### Multiple Attachments of Same Format

Tests granularity with multiple attachments of the same format. The number of attachments is randomized between 2 and 10.

### Random Mixed Attachments

Tests granularity with one primary format attachment plus random mandatory format attachments. The number of additional attachments is randomized between 2 and 10.

### In Render Pass

Tests granularity queried inside a traditional render pass (TestMode::USE_RENDER_PASS). Verifies that the granularity is consistent before and during the render pass.

### In Dynamic Render Pass (non-SC)

Tests granularity queried inside a dynamic render pass (TestMode::USE_DYNAMIC_RENDER_PASS) using vkGetRenderingAreaGranularity from VK_KHR_maintenance5. Verifies consistency with pre-pass granularity.

## Parameter Dimensions

| Dimension | Observed Values |
|---|---|
| TestMode | NO_RENDER_PASS, USE_RENDER_PASS, USE_DYNAMIC_RENDER_PASS |
| Format range | VK_FORMAT_R4G4_UNORM_PACK8 through VK_FORMAT_D32_SFLOAT_S8_UINT (formats 1-55) |
| Attachment count | 1 (single), 2-10 (multi, random) |
| Image dimensions | 1-500 (randomized per attachment) |
| Mandatory formats | 45 formats listed at [lines 477-525](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L477) |

## Support / Feature Requirements

| Feature / Extension | Used By |
|---|---|
| VK_KHR_maintenance5 | in_dynamic_render_pass (uses vkGetRenderingAreaGranularity) |
| Color attachment feature | All color format tests |
| Depth/stencil attachment feature | All depth/stencil format tests |

## Verification Methods

- **Granularity validity**: [GranularityInstance::iterate()](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L282) checks that granularity.width >= 1 and granularity.height >= 1
- **Consistency check**: Pre-pass granularity must equal in-pass granularity
- **Device limits check**: Granularity must not exceed maxFramebufferWidth and maxFramebufferHeight
- **Format support skip**: [GranularityCase::checkSupport()](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L437) skips tests if the format does not support color or depth/stencil attachment features

## Test Principles Observed

- Spec compliance: verifies the guarantees made by vkGetRenderAreaGranularity
- Format coverage: iterates over all formats from 1 to D32_SFLOAT_S8_UINT
- Consistency: granularity must not change between pre-pass and in-pass queries
- Randomization: attachment counts and dimensions are randomized for variety
- SC divergence: dynamic render pass tests are excluded for Vulkan SC

## Notes / Uncertainties

- The factory function is named `createGranularityQueryTests` but the group name is `granularity`
- The format iteration range is 1 to VK_FORMAT_D32_SFLOAT_S8_UINT (format index 55), which covers most common formats but may not include all extended formats
- The random seed is fixed at 215, so the test is deterministic
- The `in_dynamic_render_pass` group uses VK_KHR_maintenance5's vkGetRenderingAreaGranularity, which takes a VkRenderingAreaInfoKHR instead of a VkRenderPass
