# [vktApiGranularityTests.cpp](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L1)

## Overview

Tests `vkGetRenderAreaGranularity` and `vkGetRenderingAreaGranularity` (`VK_KHR_maintenance5`). Verifies
that the returned granularity values are valid (at least `1x1`, consistent before and during a render
pass, and within device limits) across various attachment format combinations and render-pass modes.

## Role of File

Implementation-heavy. Contains all test logic, helper classes, and the registration function
[createGranularityQueryTests()](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L463-L593).

## Source Code

- Implementation: [vktApiGranularityTests.cpp](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L1)
- Header: [vktApiGranularityTests.hpp](../../../modules/vulkan/api/vktApiGranularityTests.hpp#L1)
- Parent registration: [vktApiTests.cpp](../../../modules/vulkan/api/vktApiTests.cpp#L114)

## Registration Hierarchy

```text
api.granularity
├── single
├── multi
├── random
├── in_render_pass
└── in_dynamic_render_pass (non-VulkanSC only)
```

The confirmed Level-3 root is `granularity`, which
[vktApiTests.cpp](../../../modules/vulkan/api/vktApiTests.cpp#L114) adds directly under `api`.
[createGranularityQueryTests()](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L463-L593)
creates that root group and registers exactly four unconditional direct children plus the
non-VulkanSC-only `in_dynamic_render_pass` child.

## Test Families

### single — Single-attachment granularity sweep

[createGranularityQueryTests()](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L531-L542)
registers one case per format under `single`, using one attachment of that format and
`TestMode::NO_RENDER_PASS`. [GranularityInstance](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L110)
then queries granularity before any render pass and validates the result.

### multi — Multiple attachments of the same format

[createGranularityQueryTests()](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L544-L552)
registers one case per format under `multi`, with a randomized attachment count from `2` to `10`
where every attachment uses the same format and extent.

### random — Primary format plus randomized mandatory-format attachments

[createGranularityQueryTests()](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L554-L567)
registers one case per format under `random`. Each case starts with one attachment of the primary
format, then appends `2-10` additional attachments chosen from the `mandatoryFormats` array at
[vktApiGranularityTests.cpp](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L477-L525).

### in_render_pass — Query during a traditional render pass

[createGranularityQueryTests()](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L570-L578)
registers one case per format under `in_render_pass` using `TestMode::USE_RENDER_PASS`.
[GranularityInstance::iterate()](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L282)
compares the pre-pass query result against the value observed during the render pass.

### in_dynamic_render_pass — Query during dynamic rendering (non-VulkanSC only)

[createGranularityQueryTests()](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L576-L589)
registers `in_dynamic_render_pass` only when `CTS_USES_VULKANSC` is not defined. These cases use
`TestMode::USE_DYNAMIC_RENDER_PASS`, which triggers the
`vkGetRenderingAreaGranularityKHR` path guarded by
[GranularityCase::checkSupport()](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L437-L454).

## Parameter Dimensions

| Dimension | Observed Values |
|---|---|
| Registration root | `api.granularity` |
| Direct child subgroup names | `single`, `multi`, `random`, `in_render_pass`, `in_dynamic_render_pass` (non-VulkanSC only) |
| TestMode | `NO_RENDER_PASS`, `USE_RENDER_PASS`, `USE_DYNAMIC_RENDER_PASS` |
| Format range | `VK_FORMAT_R4G4_UNORM_PACK8` through `VK_FORMAT_D32_SFLOAT_S8_UINT` (`1-55`) |
| Attachment count | `1` (`single`, `in_render_pass`, `in_dynamic_render_pass`), `2-10` (`multi` same-format attachments, `random` additional mandatory-format attachments plus the primary format) |
| Image dimensions | Randomized per attachment in the inclusive range `1-500` |
| Random seed | `215` |
| Mandatory formats array | 47 formats listed at [vktApiGranularityTests.cpp](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L477-L525) |

## Support / Feature Requirements

| Feature / Extension | Used By |
|---|---|
| `VK_KHR_maintenance5` | `in_dynamic_render_pass`, via [GranularityCase::checkSupport()](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L452-L453) |
| Color-attachment or depth/stencil-attachment format support | All tests, via [GranularityCase::checkSupport()](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L441-L450) |

## Verification Methods

- **Granularity validity**:
  [GranularityInstance::iterate()](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L282)
  checks that width and height are at least `1`.
- **Consistency check**:
  [GranularityInstance::iterate()](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L282)
  compares the pre-pass query result against the in-pass result for render-pass and dynamic-rendering
  modes.
- **Device limits check**:
  [GranularityInstance::iterate()](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L282)
  verifies granularity does not exceed `maxFramebufferWidth` and `maxFramebufferHeight`.
- **Format support skip**:
  [GranularityCase::checkSupport()](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L437-L450)
  throws `NotSupportedError` when an attachment format lacks both required optimal-tiling features.

## Test Principles Observed

- Spec compliance: verifies the guarantees made by `vkGetRenderAreaGranularity` and, for the dynamic
  rendering subgroup, `vkGetRenderingAreaGranularityKHR`.
- Format coverage: iterates over every `VkFormat` integer value from `1` through
  `VK_FORMAT_D32_SFLOAT_S8_UINT`.
- Consistency: granularity must not change between pre-pass and in-pass queries.
- Randomization: attachment counts, image dimensions, and random companion formats vary per case but
  remain deterministic because the generator uses seed `215`.
- VulkanSC divergence: `in_dynamic_render_pass` is not registered for VulkanSC builds.

## Notes / Uncertainties

- The factory function is named `createGranularityQueryTests`, but the registered root group name is
  `granularity`.
- The `random` subgroup uses the `mandatoryFormats` array as a pool for extra attachments, but the
  inspected code does not require every listed mandatory format to appear in every test case.
- `GranularityCase::checkSupport()` accepts a format when its optimal-tiling features include either
  color-attachment support or depth/stencil-attachment support because it rejects only the case where
  both bits are absent.
