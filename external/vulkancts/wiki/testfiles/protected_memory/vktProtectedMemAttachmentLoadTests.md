# vktProtectedMemAttachmentLoadTests.cpp

## Overview

[`vktProtectedMemAttachmentLoadTests.cpp`](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentLoadTests.cpp#L216-L350) registers protected attachment load-op tests under `load_op` with static and randomized clear-value inputs.

## Role

Implementation file that registers tests.

## Source Code

- Primary source: [`vktProtectedMemAttachmentLoadTests.cpp`](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentLoadTests.cpp#L1)

## Registration Hierarchy

```text
protected_memory.attachment.load_op
├── static
└── random
```

## Test Families

### static — Fixed clear-value cases
[`static`](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentLoadTests.cpp#L316-L324) contains fixed reference data from the local `testData` array.

### random — Seeded random clear-value cases
[`random`](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentLoadTests.cpp#L326-L345) creates 10 cases from the command-line base seed.

## Parameter Dimensions

The direct children are `static` and `random`; random generation uses `testCount = 10` and `de::Random` seeded from the command line.

## Support / Feature Requirements

Most cases call [`checkProtectedContextSupport()`](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L102-L124), which requires Vulkan 1.1 and the protected-memory feature when protected tests are enabled; several command-buffer variants also skip Vulkan SC secondary-command-buffer cases when the relevant property is absent.

## Verification Methods

[`iterate()`](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentLoadTests.cpp#L114-L212) submits a protected command buffer and validates the resulting image through [`validateImage()`](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentLoadTests.cpp#L206-L211).

## Test Principles Observed

- The tests compare loaded attachment contents against expected sampled values after protected submission.
- Fixed and random inputs exercise the same validation path.

## Notes / Uncertainties

- Claims are limited to the inspected source and mustpass-observed registration paths.
