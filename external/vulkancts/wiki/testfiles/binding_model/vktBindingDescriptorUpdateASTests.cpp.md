# Descriptor Update Acceleration Structure Tests

Documents the nested acceleration-structure descriptor update group under `descriptor_update`; it is registered by `vktBindingDescriptorUpdateTests.cpp`, not by the category root.

## Source

- [`vktBindingDescriptorUpdateASTests.cpp`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp)

## Verified Group Name

| Group | Availability | Evidence |
|-------|--------------|----------|
| `descriptor_update → acceleration_structure` | VK only nested group | Created in [`vktBindingDescriptorUpdateASTests.cpp:2568`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L2568); factory entry at [`vktBindingDescriptorUpdateASTests.cpp:2566`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L2566) |

## Registration Path

```
binding_model → descriptor_update → acceleration_structure
```

## Test Hierarchy

The group name is `acceleration_structure`; it expands ray-query and ray-tracing test types, descriptor update methods, and shader stages. Evidence starts at [`vktBindingDescriptorUpdateASTests.cpp:2570`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L2570) and continues through [`vktBindingDescriptorUpdateASTests.cpp:2660`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L2660).

## Parameter Dimensions

| Dimension | Observed values / source |
|-----------|--------------------------|
| Group construction | Verified by [`vktBindingDescriptorUpdateASTests.cpp:2568`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L2568) |
| Generated families | Derived from arrays, loops, or child additions near [`vktBindingDescriptorUpdateASTests.cpp:2570`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L2570) |
| Build availability | Root or nested registration determines whether the group is always present or guarded by `CTS_USES_VULKANSC` |

## Support / Feature Requirements

Support checks are implemented near [`vktBindingDescriptorUpdateASTests.cpp:2355`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L2355). Requirements vary by selected case and extension path; this page records only the recurring gates visible in the inspected file.

## Verification Methods

Support requires `VK_KHR_acceleration_structure`; ray-tracing paths require ray-tracing support. Cases write AS descriptors and validate shader/ray results.

## Test Principles

- Keep descriptor binding/update behavior observable through shader execution or explicit API success checks.
- Vary one or more binding-model dimensions while preserving traceable generated names.
- Use feature/support gates to skip extension-dependent scenarios rather than broadening unsupported coverage.

## Notes

- This Level-3 page documents a registered test file. Helper-only files are not given separate pages.
