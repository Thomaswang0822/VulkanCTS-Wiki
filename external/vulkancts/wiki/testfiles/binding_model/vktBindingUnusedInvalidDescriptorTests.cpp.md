# Unused/Invalid Descriptor Tests

Checks that unused descriptors can remain unset/invalid where allowed and that copying from invalid descriptors behaves as expected for covered resource types.

## Source

- [`vktBindingUnusedInvalidDescriptorTests.cpp`](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp)

## Registration Hierarchy

```text
binding_model.unused_invalid_descriptor
├── write
└── copy
```

## Test Families

### write — Descriptor writes

Contains the `unused` and `invalid` sub-branches over buffer and image resource types. Evidence starts at [`vktBindingUnusedInvalidDescriptorTests.cpp:1287`](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp#L1287).

- **unused** ([`vktBindingUnusedInvalidDescriptorTests.cpp:1293`](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp#L1293)): Tests that unused descriptor bindings can remain unset without causing errors. Iterates over resource types `UNIFORM_BUFFER`, `STORAGE_BUFFER`, `SAMPLED_IMAGE`, `COMBINED_IMAGE_SAMPLER`, `STORAGE_IMAGE` with `addInvalidDescriptor = false`.

- **invalid** ([`vktBindingUnusedInvalidDescriptorTests.cpp:1312`](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp#L1312)): Tests that invalid descriptor bindings can coexist with valid ones without affecting results. Iterates over resource types `SAMPLED_IMAGE`, `COMBINED_IMAGE_SAMPLER`, `STORAGE_IMAGE` with `addInvalidDescriptor = true`.

### copy — Descriptor copy

Tests that copying from invalid descriptors behaves as expected. Iterates over resource types `UNIFORM_BUFFER`, `STORAGE_BUFFER`, `SAMPLED_IMAGE`, `COMBINED_IMAGE_SAMPLER`, `STORAGE_IMAGE` with `addInvalidDescriptor = false`. Evidence at [`vktBindingUnusedInvalidDescriptorTests.cpp:1336`](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp#L1336).

## Parameter Dimensions

| Dimension | Observed values / source |
|-----------|--------------------------|
| Group construction | Verified by [`vktBindingUnusedInvalidDescriptorTests.cpp:1285`](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp#L1285) |
| Generated families | Derived from arrays, loops, or child additions near [`vktBindingUnusedInvalidDescriptorTests.cpp:1287`](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp#L1287) |
| Build availability | Root or nested registration determines whether the group is always present or guarded by `CTS_USES_VULKANSC` |

## Support / Feature Requirements

Support checks are implemented near [`vktBindingUnusedInvalidDescriptorTests.cpp:696`](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp#L696). Requirements vary by selected case and extension path; this page records only the recurring gates visible in the inspected file.

## Verification Methods

Cases build descriptor sets containing unused or invalid descriptors and verify only used valid resources affect results.

## Test Principles

- Keep descriptor binding/update behavior observable through shader execution or explicit API success checks.
- Vary one or more binding-model dimensions while preserving traceable generated names.
- Use feature/support gates to skip extension-dependent scenarios rather than broadening unsupported coverage.

## Notes

- This Level-3 page documents a registered test file. Helper-only files are not given separate pages.
