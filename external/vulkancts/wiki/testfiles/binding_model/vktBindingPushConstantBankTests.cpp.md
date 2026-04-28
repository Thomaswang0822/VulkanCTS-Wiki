# Push Constant Bank Tests

Tests NV push-constant bank behavior both with ordinary push constants and descriptor-heap push data integration.

## Source

- [`vktBindingPushConstantBankTests.cpp`](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp)

## Verified Group Name

| Group | Availability | Evidence |
|-------|--------------|----------|
| `push_constant_bank` | VK only | Created in [`vktBindingPushConstantBankTests.cpp:1388`](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L1388); factory entry at [`vktBindingPushConstantBankTests.cpp:1386`](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L1386) |

## Registration Path

```
binding_model → push_constant_bank
```

## Test Hierarchy

The `push_constant_bank` group has `basic` and `descriptor_heap` subgroups; generated cases vary compute/graphics use, bank count, and member offsets. Evidence starts at [`vktBindingPushConstantBankTests.cpp:1391`](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L1391) and continues through [`vktBindingPushConstantBankTests.cpp:1400`](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L1400).

## Parameter Dimensions

| Dimension | Observed values / source |
|-----------|--------------------------|
| Group construction | Verified by [`vktBindingPushConstantBankTests.cpp:1388`](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L1388) |
| Generated families | Derived from arrays, loops, or child additions near [`vktBindingPushConstantBankTests.cpp:1391`](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L1391) |
| Build availability | Root or nested registration determines whether the group is always present or guarded by `CTS_USES_VULKANSC` |

## Support / Feature Requirements

Support checks are implemented near [`vktBindingPushConstantBankTests.cpp:1145`](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L1145). Requirements vary by selected case and extension path; this page records only the recurring gates visible in the inspected file.

## Verification Methods

Cases validate shader-visible push-constant bank data after command recording and descriptor-heap related push-data paths.

## Test Principles

- Keep descriptor binding/update behavior observable through shader execution or explicit API success checks.
- Vary one or more binding-model dimensions while preserving traceable generated names.
- Use feature/support gates to skip extension-dependent scenarios rather than broadening unsupported coverage.

## Notes

- This Level-3 page documents a registered test file. Helper-only files are not given separate pages.
