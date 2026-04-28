# Descriptor Combination Tests

Exercises combinations where descriptor-buffer and legacy descriptor mechanisms interact in the same command buffer or with capture replay and custom border color.

## Source

- [`vktBindingDescriptorCombinationTests.cpp`](../../../modules/vulkan/binding_model/vktBindingDescriptorCombinationTests.cpp)

## Verified Group Name

| Group | Availability | Evidence |
|-------|--------------|----------|
| `descriptor_combination` | VK only | Created in [`vktBindingDescriptorCombinationTests.cpp:691`](../../../modules/vulkan/binding_model/vktBindingDescriptorCombinationTests.cpp:691); factory entry at [`vktBindingDescriptorCombinationTests.cpp:689`](../../../modules/vulkan/binding_model/vktBindingDescriptorCombinationTests.cpp:689) |

## Registration Path

```
binding_model → descriptor_combination
```

## Test Hierarchy

The group name is `descriptor_combination`; the `basic` subgroup contains two named combination cases. Evidence starts at [`vktBindingDescriptorCombinationTests.cpp:668`](../../../modules/vulkan/binding_model/vktBindingDescriptorCombinationTests.cpp:668) and continues through [`vktBindingDescriptorCombinationTests.cpp:684`](../../../modules/vulkan/binding_model/vktBindingDescriptorCombinationTests.cpp:684).

## Parameter Dimensions

| Dimension | Observed values / source |
|-----------|--------------------------|
| Group construction | Verified by [`vktBindingDescriptorCombinationTests.cpp:691`](../../../modules/vulkan/binding_model/vktBindingDescriptorCombinationTests.cpp:691) |
| Generated families | Derived from arrays, loops, or child additions near [`vktBindingDescriptorCombinationTests.cpp:668`](../../../modules/vulkan/binding_model/vktBindingDescriptorCombinationTests.cpp:668) |
| Build availability | Root or nested registration determines whether the group is always present or guarded by `CTS_USES_VULKANSC` |

## Support / Feature Requirements

Support checks are implemented near [`vktBindingDescriptorCombinationTests.cpp:592`](../../../modules/vulkan/binding_model/vktBindingDescriptorCombinationTests.cpp:592). Requirements vary by selected case and extension path; this page records only the recurring gates visible in the inspected file.

## Verification Methods

Support checks require the extension mix needed by each combination case; execution verifies the combined descriptor path works.

## Test Principles

- Keep descriptor binding/update behavior observable through shader execution or explicit API success checks.
- Vary one or more binding-model dimensions while preserving traceable generated names.
- Use feature/support gates to skip extension-dependent scenarios rather than broadening unsupported coverage.

## Notes

- This Level-3 page documents a registered test file. Helper-only files are not given separate pages.
