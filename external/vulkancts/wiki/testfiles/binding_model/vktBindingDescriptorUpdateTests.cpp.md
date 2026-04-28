# Descriptor Update Tests

Covers descriptor update corner cases: empty bindings, samplerless writes, random descriptor updates, and a nested acceleration-structure update branch for Vulkan builds.

## Source

- [`vktBindingDescriptorUpdateTests.cpp`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp)

## Verified Group Name

| Group | Availability | Evidence |
|-------|--------------|----------|
| `descriptor_update` | VK + VKSC, with nested VK-only AS group | Created in [`vktBindingDescriptorUpdateTests.cpp:1909`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp:1909); factory entry at [`vktBindingDescriptorUpdateTests.cpp:1907`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp:1907) |

## Registration Path

```
binding_model → descriptor_update
```

## Test Hierarchy

The file creates `descriptor_update` and adds `empty_descriptor`, `samplerless`, `random`, and, outside `CTS_USES_VULKANSC`, `acceleration_structure`. Evidence starts at [`vktBindingDescriptorUpdateTests.cpp:1911`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp:1911) and continues through [`vktBindingDescriptorUpdateTests.cpp:1916`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp:1916).

## Parameter Dimensions

| Dimension | Observed values / source |
|-----------|--------------------------|
| Group construction | Verified by [`vktBindingDescriptorUpdateTests.cpp:1909`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp:1909) |
| Generated families | Derived from arrays, loops, or child additions near [`vktBindingDescriptorUpdateTests.cpp:1911`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp:1911) |
| Build availability | Root or nested registration determines whether the group is always present or guarded by `CTS_USES_VULKANSC` |

## Support / Feature Requirements

Support checks are implemented near [`vktBindingDescriptorUpdateTests.cpp:311`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp:311). Requirements vary by selected case and extension path; this page records only the recurring gates visible in the inspected file.

## Verification Methods

Cases validate successful descriptor-set operations and shader-visible results after updates.

## Test Principles

- Keep descriptor binding/update behavior observable through shader execution or explicit API success checks.
- Vary one or more binding-model dimensions while preserving traceable generated names.
- Use feature/support gates to skip extension-dependent scenarios rather than broadening unsupported coverage.

## Notes

- This Level-3 page documents a registered test file. Helper-only files are not given separate pages.
