# Descriptor Copy Tests

Verifies descriptor copying for compute, graphics, graphics update-after-bind, and miscellaneous immutable-sampler cases.

## Source

- [`vktBindingDescriptorCopyTests.cpp`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp)

## Verified Group Name

| Group | Availability | Evidence |
|-------|--------------|----------|
| `descriptor_copy` | VK + VKSC, with Vulkan-only inline-uniform variations | Created in [`vktBindingDescriptorCopyTests.cpp:3758`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp:3758); factory entry at [`vktBindingDescriptorCopyTests.cpp:3754`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp:3754) |

## Registration Path

```
binding_model → descriptor_copy
```

## Test Hierarchy

The `descriptor_copy` group contains `compute`, `graphics`, `graphics_uab`, and `misc`; helper functions add per-descriptor-type copy scenarios. Evidence starts at [`vktBindingDescriptorCopyTests.cpp:3760`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp:3760) and continues through [`vktBindingDescriptorCopyTests.cpp:3784`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp:3784).

## Parameter Dimensions

| Dimension | Observed values / source |
|-----------|--------------------------|
| Group construction | Verified by [`vktBindingDescriptorCopyTests.cpp:3758`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp:3758) |
| Generated families | Derived from arrays, loops, or child additions near [`vktBindingDescriptorCopyTests.cpp:3760`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp:3760) |
| Build availability | Root or nested registration determines whether the group is always present or guarded by `CTS_USES_VULKANSC` |

## Support / Feature Requirements

Support checks are implemented near [`vktBindingDescriptorCopyTests.cpp:2595`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp:2595). Requirements vary by selected case and extension path; this page records only the recurring gates visible in the inspected file.

## Verification Methods

Cases copy descriptors, execute the target pipeline, and verify resources are observed from the copied bindings.

## Test Principles

- Keep descriptor binding/update behavior observable through shader execution or explicit API success checks.
- Vary one or more binding-model dimensions while preserving traceable generated names.
- Use feature/support gates to skip extension-dependent scenarios rather than broadening unsupported coverage.

## Notes

- This Level-3 page documents a registered test file. Helper-only files are not given separate pages.
