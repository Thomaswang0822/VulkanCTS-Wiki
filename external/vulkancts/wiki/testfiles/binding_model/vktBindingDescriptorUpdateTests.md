# Descriptor Update Tests

Covers descriptor update corner cases: empty bindings, samplerless writes, random descriptor updates, and a nested acceleration-structure update branch for Vulkan builds.

The historical Vulkan API test plan identifies descriptor updates as a binding-model objective ([`apitests.adoc`](../../../../../doc/testspecs/VK/apitests.adoc#L281-L289)); current source and mustpass remain authoritative for exact behavior.

## Source

- [`vktBindingDescriptorUpdateTests.cpp`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp)

## Registration Hierarchy

```text
binding_model.descriptor_update
├── empty_descriptor
├── samplerless
├── random
└── acceleration_structure (VK only)
```

## Test Families

### empty_descriptor — Empty descriptor update tests

Created in [`vktBindingDescriptorUpdateTests.cpp:141`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L141). Contains a single test case `uniform_buffer` that verifies descriptor update behavior with empty bindings. The test should always pass, confirming that updating an empty descriptor does not cause errors.

### samplerless — Samplerless write tests

Created in [`vktBindingDescriptorUpdateTests.cpp:885`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L885). Tests descriptor write operations on samplerless descriptor types. Generated from a combinatorial sweep over descriptor types (`sampled_img`, `storage_img`, `input_attachment`), pointer cases (`sampler_zero`, `sampler_one`, `sampler_destroyed`), descriptor set indices (0, 1), layout variants, and pipeline types (graphics, compute).

### random — Random descriptor update tests

Created in [`vktBindingDescriptorUpdateTests.cpp:1898`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L1898). Updates descriptors randomly between draws. Contains two test cases: `uniform_buffer_graphics` (graphics pipeline) and `uniform_buffer_compute` (compute pipeline).

### acceleration_structure — Acceleration structure update tests (VK only)

Created in [`vktBindingDescriptorUpdateASTests.cpp:2568`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L2568). Nested under `#ifndef CTS_USES_VULKANSC` guard at [`vktBindingDescriptorUpdateTests.cpp:1914`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L1914). Tests descriptor update behavior with acceleration structures. This group is excluded from Vulkan SC builds.

## Parameter Dimensions

| Dimension | Observed values / source |
|-----------|--------------------------|
| Group construction | Verified by [`vktBindingDescriptorUpdateTests.cpp:1909`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L1909) |
| Generated families | Derived from arrays, loops, or child additions near [`vktBindingDescriptorUpdateTests.cpp:1911`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L1911) |
| Build availability | Root or nested registration determines whether the group is always present or guarded by `CTS_USES_VULKANSC` |

## Support / Feature Requirements

Support checks are implemented near [`vktBindingDescriptorUpdateTests.cpp:311`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L311). Requirements vary by selected case and extension path; this page records only the recurring gates visible in the inspected file.

## Verification Methods

Cases validate successful descriptor-set operations and shader-visible results after updates.

## Test Principles

- Keep descriptor binding/update behavior observable through shader execution or explicit API success checks.
- Vary one or more binding-model dimensions while preserving traceable generated names.
- Use feature/support gates to skip extension-dependent scenarios rather than broadening unsupported coverage.

## Notes

- This Level-3 page documents a registered test file. Helper-only files are not given separate pages.
