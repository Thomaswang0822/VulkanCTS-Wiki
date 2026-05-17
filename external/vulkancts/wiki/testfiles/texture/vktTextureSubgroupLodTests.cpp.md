# vktTextureSubgroupLodTests.cpp

## Overview

Registers the `subgroup_lod` test group under the `texture` category. This group contains Amber-based tests that verify subgroup operations produce consistent LOD values across all invocations in a subgroup when using `textureLod`, `textureGrad`, and `texelFetch`.

## Role

Registration file

## Source Code

- [vktTextureSubgroupLodTests.cpp](../../../modules/vulkan/texture/vktTextureSubgroupLodTests.cpp#L38) - `populateSubgroupLodTests`
- [vktTextureSubgroupLodTests.cpp](../../../modules/vulkan/texture/vktTextureSubgroupLodTests.cpp#L59) - `createTextureSubgroupLodTests`

## Registration Hierarchy

```text
texture.subgroup_lod
├── texturelod (non-VulkanSC only)
├── texturegrad (non-VulkanSC only)
└── texelfetch (non-VulkanSC only)
```

## Test Families

### texturelod

Amber test case. Data directory: `texture/subgroup_lod`, file: `texture_lod.amber`. Verifies that subgroup operations produce consistent LOD values across all invocations in a subgroup when using `textureLod`.

### texturegrad

Amber test case. Data directory: `texture/subgroup_lod`, file: `texture_grad.amber`. Verifies that subgroup operations produce consistent LOD values across all invocations in a subgroup when using `textureGrad`.

### texelfetch

Amber test case. Data directory: `texture/subgroup_lod`, file: `texel_fetch.amber`. Verifies that subgroup operations produce consistent LOD values across all invocations in a subgroup when using `texelFetch`.

## Parameter Dimensions

None. All three tests are single Amber test cases with no parameterization.

## Support/Feature Requirements

No explicit `checkSupport` in C++ code. The entire `populateSubgroupLodTests` function body is wrapped in `#ifndef CTS_USES_VULKANSC` (line 40). On VulkanSC, `DE_UNREF(group)` is called and no tests are added (line 53).

## Verification Methods

Verification is entirely handled by the Amber scripts. No C++-side verification logic.

## Notes

- All three test cases are excluded on VulkanSC builds.
- The factory function `createTextureSubgroupLodTests` delegates to `createTestGroup(testCtx, "subgroup_lod", populateSubgroupLodTests)`.
