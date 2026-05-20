# vktProtectedMemStackTests.cpp

## Overview

[`vktProtectedMemStackTests.cpp`](../../../modules/vulkan/protected_memory/vktProtectedMemStackTests.cpp#L409-L421) registers protected shader stack-storage tests under `stack` with one child per stack-memory size.

## Role

Implementation file that registers tests.

## Source Code

- Primary source: [`vktProtectedMemStackTests.cpp`](../../../modules/vulkan/protected_memory/vktProtectedMemStackTests.cpp#L1)

## Registration Hierarchy

```text
protected_memory.stack
├── stacksize_32
├── stacksize_64
├── stacksize_128
├── stacksize_256
└── stacksize_512
```

## Test Families

### stacksize_32 — 32 bytes
Generated from the `stackMemSizes` array.

### stacksize_64 — 64 bytes
Generated from the `stackMemSizes` array.

### stacksize_128 — 128 bytes
Generated from the `stackMemSizes` array.

### stacksize_256 — 256 bytes
Generated from the `stackMemSizes` array.

### stacksize_512 — 512 bytes
Generated from the `stackMemSizes` array.

## Parameter Dimensions

The stack sizes are exactly `{32, 64, 128, 256, 512}` in [`stackMemSizes`](../../../modules/vulkan/protected_memory/vktProtectedMemStackTests.cpp#L414-L420).

## Support / Feature Requirements

[`checkSupport()`](../../../modules/vulkan/protected_memory/vktProtectedMemStackTests.cpp#L116-L124) calls protected-context support and checks that `maxComputeWorkGroupInvocations` is sufficient for the image dimensions.

## Verification Methods

[`validateResult()`](../../../modules/vulkan/protected_memory/vktProtectedMemStackTests.cpp#L385-L402) samples expected texture values and validates the image.

## Test Principles Observed

- The shader comments state that each invocation validates a particular byte element on stack memory.
- The result is still observed through image validation rather than direct stack inspection.

## Notes / Uncertainties

- Claims are limited to the inspected source and mustpass-observed registration paths.
