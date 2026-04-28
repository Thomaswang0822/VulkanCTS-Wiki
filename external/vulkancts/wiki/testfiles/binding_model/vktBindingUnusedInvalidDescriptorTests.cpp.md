# Unused/Invalid Descriptor Tests

Checks that unused descriptors can remain unset/invalid where allowed and that copying from invalid descriptors behaves as expected for covered resource types.

## Source

- [`vktBindingUnusedInvalidDescriptorTests.cpp`](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp)

## Verified Group Name

| Group | Availability | Evidence |
|-------|--------------|----------|
| `unused_invalid_descriptor` | VK only | Created in [`vktBindingUnusedInvalidDescriptorTests.cpp:1285`](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp:1285); factory entry at [`vktBindingUnusedInvalidDescriptorTests.cpp:1283`](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp:1283) |

## Registration Path

```
binding_model → unused_invalid_descriptor
```

## Test Hierarchy

The `unused_invalid_descriptor` group contains `write/unused`, `write/invalid`, and `copy` branches over buffer and image resource types. Evidence starts at [`vktBindingUnusedInvalidDescriptorTests.cpp:1287`](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp:1287) and continues through [`vktBindingUnusedInvalidDescriptorTests.cpp:1351`](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp:1351).

## Parameter Dimensions

| Dimension | Observed values / source |
|-----------|--------------------------|
| Group construction | Verified by [`vktBindingUnusedInvalidDescriptorTests.cpp:1285`](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp:1285) |
| Generated families | Derived from arrays, loops, or child additions near [`vktBindingUnusedInvalidDescriptorTests.cpp:1287`](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp:1287) |
| Build availability | Root or nested registration determines whether the group is always present or guarded by `CTS_USES_VULKANSC` |

## Support / Feature Requirements

Support checks are implemented near [`vktBindingUnusedInvalidDescriptorTests.cpp:696`](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp:696). Requirements vary by selected case and extension path; this page records only the recurring gates visible in the inspected file.

## Verification Methods

Cases build descriptor sets containing unused or invalid descriptors and verify only used valid resources affect results.

## Test Principles

- Keep descriptor binding/update behavior observable through shader execution or explicit API success checks.
- Vary one or more binding-model dimensions while preserving traceable generated names.
- Use feature/support gates to skip extension-dependent scenarios rather than broadening unsupported coverage.

## Notes

- This Level-3 page documents a registered test file. Helper-only files are not given separate pages.
