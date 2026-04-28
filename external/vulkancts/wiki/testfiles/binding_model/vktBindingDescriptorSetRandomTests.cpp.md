# Descriptor Set Random Tests

Generates random descriptor-set layouts over descriptor-set count, indexing mode, descriptor-count limits, inline uniform blocks, update-after-bind, shader stage, input attachments, and seed.

## Source

- [`vktBindingDescriptorSetRandomTests.cpp`](../../../modules/vulkan/binding_model/vktBindingDescriptorSetRandomTests.cpp)

## Verified Group Name

| Group | Availability | Evidence |
|-------|--------------|----------|
| `descriptorset_random` | VK + VKSC, reduced stage set on VKSC | Created in [`vktBindingDescriptorSetRandomTests.cpp:3152`](../../../modules/vulkan/binding_model/vktBindingDescriptorSetRandomTests.cpp#L3152); factory entry at [`vktBindingDescriptorSetRandomTests.cpp:3150`](../../../modules/vulkan/binding_model/vktBindingDescriptorSetRandomTests.cpp#L3150) |

## Registration Path

```
binding_model → descriptorset_random
```

## Test Hierarchy

The group name is `descriptorset_random`; Vulkan-only stages include ray tracing, task, and mesh stages behind `CTS_USES_VULKANSC`. Evidence starts at [`vktBindingDescriptorSetRandomTests.cpp:3162`](../../../modules/vulkan/binding_model/vktBindingDescriptorSetRandomTests.cpp#L3162) and continues through [`vktBindingDescriptorSetRandomTests.cpp:3435`](../../../modules/vulkan/binding_model/vktBindingDescriptorSetRandomTests.cpp#L3435).

## Parameter Dimensions

| Dimension | Observed values / source |
|-----------|--------------------------|
| Group construction | Verified by [`vktBindingDescriptorSetRandomTests.cpp:3152`](../../../modules/vulkan/binding_model/vktBindingDescriptorSetRandomTests.cpp#L3152) |
| Generated families | Derived from arrays, loops, or child additions near [`vktBindingDescriptorSetRandomTests.cpp:3162`](../../../modules/vulkan/binding_model/vktBindingDescriptorSetRandomTests.cpp#L3162) |
| Build availability | Root or nested registration determines whether the group is always present or guarded by `CTS_USES_VULKANSC` |

## Support / Feature Requirements

Support checks are implemented near [`vktBindingDescriptorSetRandomTests.cpp:347`](../../../modules/vulkan/binding_model/vktBindingDescriptorSetRandomTests.cpp#L347). Requirements vary by selected case and extension path; this page records only the recurring gates visible in the inspected file.

## Verification Methods

Generated shaders and descriptor updates are executed and checked against expected resource usage.

## Test Principles

- Keep descriptor binding/update behavior observable through shader execution or explicit API success checks.
- Vary one or more binding-model dimensions while preserving traceable generated names.
- Use feature/support gates to skip extension-dependent scenarios rather than broadening unsupported coverage.

## Notes

- This Level-3 page documents a registered test file. Helper-only files are not given separate pages.
