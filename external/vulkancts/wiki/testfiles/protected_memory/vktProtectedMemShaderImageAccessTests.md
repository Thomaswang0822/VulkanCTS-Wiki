# vktProtectedMemShaderImageAccessTests.cpp

## Overview

[`vktProtectedMemShaderImageAccessTests.cpp`](../../../modules/vulkan/protected_memory/vktProtectedMemShaderImageAccessTests.cpp#L1251-L1400) registers shader image access tests under `access`, covering fragment and compute paths plus maintenance5-specific miscellaneous cases outside Vulkan SC.

## Role

Implementation file that registers tests.

## Source Code

- Primary source: [`vktProtectedMemShaderImageAccessTests.cpp`](../../../modules/vulkan/protected_memory/vktProtectedMemShaderImageAccessTests.cpp#L1)

## Registration Hierarchy

```text
protected_memory.image.access
├── fragment
├── compute
└── misc
```

## Test Families

### fragment — Fragment shader access
[`fragment`](../../../modules/vulkan/protected_memory/vktProtectedMemShaderImageAccessTests.cpp#L1255-L1264) is one shader-stage branch.

### compute — Compute shader access
[`compute`](../../../modules/vulkan/protected_memory/vktProtectedMemShaderImageAccessTests.cpp#L1255-L1264) is the second shader-stage branch.

### misc — Maintenance5 protected-access cases
[`misc`](../../../modules/vulkan/protected_memory/vktProtectedMemShaderImageAccessTests.cpp#L1389-L1399) is non-VulkanSC-only and contains maintenance5 protected/no-protected-access cases.

## Parameter Dimensions

The generated matrix includes shader stage, default/protected-access mode, pipeline flags, access types (`sampling`, `texelfetch`, `imageload`, `imagestore`, `imageatomics`), formats (`rgba8`, `r32i`, `r32ui`), and atomic-operation subgroups for atomics at [`vktProtectedMemShaderImageAccessTests.cpp`](../../../modules/vulkan/protected_memory/vktProtectedMemShaderImageAccessTests.cpp#L1255-L1379). Compute `imagestore` is skipped because it is already covered elsewhere.

## Support / Feature Requirements

[`checkSupport()`](../../../modules/vulkan/protected_memory/vktProtectedMemShaderImageAccessTests.cpp#L334-L340) calls protected-context support and requires `VK_KHR_maintenance5` for maintenance5 cases.

## Verification Methods

[`validateResult()`](../../../modules/vulkan/protected_memory/vktProtectedMemShaderImageAccessTests.cpp#L1227-L1245) builds sampled reference data and calls image validation.

## Test Principles Observed

- The file stresses protected image access through shader reads, writes, samples, fetches, and atomics.
- Pipeline-protected-access flags are modeled as generated subgroups below the one-level tree root.

## Notes / Uncertainties

- Claims are limited to the inspected source and mustpass-observed registration paths.
