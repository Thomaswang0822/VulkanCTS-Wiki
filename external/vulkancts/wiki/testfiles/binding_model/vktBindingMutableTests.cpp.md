# Mutable Descriptor Tests

Covers `VK_EXT_mutable_descriptor_type` using single, array, mixed, multiple, and miscellaneous mutable/non-mutable descriptor configurations.

## Source

- [`vktBindingMutableTests.cpp`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp)

## Verified Group Name

| Group | Availability | Evidence |
|-------|--------------|----------|
| `mutable_descriptor` | VK only | Created in [`vktBindingMutableTests.cpp:3950`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L3950); factory entry at [`vktBindingMutableTests.cpp:3948`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L3948) |

## Registration Path

```
binding_model → mutable_descriptor
```

## Test Hierarchy

The group name is `mutable_descriptor`; it expands descriptor-set recipes and update/source/pool/access/stage variants. Evidence starts at [`vktBindingMutableTests.cpp:3992`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L3992) and continues through [`vktBindingMutableTests.cpp:4343`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L4343).

## Parameter Dimensions

| Dimension | Observed values / source |
|-----------|--------------------------|
| Group construction | Verified by [`vktBindingMutableTests.cpp:3950`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L3950) |
| Generated families | Derived from arrays, loops, or child additions near [`vktBindingMutableTests.cpp:3992`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L3992) |
| Build availability | Root or nested registration determines whether the group is always present or guarded by `CTS_USES_VULKANSC` |

## Support / Feature Requirements

Support checks are implemented near [`vktBindingMutableTests.cpp:2808`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L2808). Requirements vary by selected case and extension path; this page records only the recurring gates visible in the inspected file.

## Verification Methods

Support checks require mutable descriptor features and related descriptor features when selected; shaders verify resource access through mutable bindings.

## Test Principles

- Keep descriptor binding/update behavior observable through shader execution or explicit API success checks.
- Vary one or more binding-model dimensions while preserving traceable generated names.
- Use feature/support gates to skip extension-dependent scenarios rather than broadening unsupported coverage.

## Notes

- This Level-3 page documents a registered test file. Helper-only files are not given separate pages.
