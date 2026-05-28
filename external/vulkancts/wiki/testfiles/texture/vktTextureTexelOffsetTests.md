# vktTextureTexelOffsetTests.cpp

## Overview

Registers the `texel_offset` test group under the `texture` category. This group contains an Amber-based test that validates texture fetch operations with explicit texel offsets correctly apply the offset when reading from the texture.

## Role

Registration file

## Source Code

- [vktTextureTexelOffsetTests.cpp](../../../modules/vulkan/texture/vktTextureTexelOffsetTests.cpp#L36) - `createTextureTexelOffsetTests`

## Registration Hierarchy

```text
texture.texel_offset
└── texel_offset (non-VulkanSC only)
```

## Test Families

### texel_offset

Amber test case. Data directory: `texture/texel_offset`, file: `texel_offset.amber`. Description: "A fragment shader that uses texture loads with an offset specified." Validates that texture fetch operations with explicit texel offsets correctly apply the offset when reading from the texture.

## Parameter Dimensions

None. Single Amber test case with no parameterization.

## Support / Feature Requirements

No explicit `checkSupport` in C++ code. The test is wrapped in `#ifndef CTS_USES_VULKANSC` (line 39). On VulkanSC, the group is created but left empty.

## Verification Methods

Verification is entirely handled by the Amber script. No C++-side verification logic.

## Notes

- The test is excluded on VulkanSC builds.
- The factory function creates a `TestCaseGroup(testCtx, "texel_offset")` at line 38 and adds the single Amber test case within the VulkanSC guard.
