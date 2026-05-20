# Mutable Descriptor Tests

Covers `VK_EXT_mutable_descriptor_type` using single, array, mixed, multiple, and miscellaneous mutable/non-mutable descriptor configurations.

## Source

- [`vktBindingMutableTests.cpp`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp)

## Registration Hierarchy

```text
binding_model.mutable_descriptor
├── single
├── single_nonmutable
├── one_array
├── multiple_arrays
├── multiple_arrays_mixed
├── single_and_array
├── multiple
└── misc
```

## Test Families

### single — Single mutable descriptor

Basic tests with a single mutable descriptor. Created at [`vktBindingMutableTests.cpp:3993`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L3993), added to the main group at [`vktBindingMutableTests.cpp:4056`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L4056).

Contains subgroups per basic descriptor type (sampler, combined image sampler, sampled image, storage image, uniform texel buffer, storage texel buffer, uniform buffer, storage buffer, input attachment, acceleration structure), an `all_mandatory` subgroup iterating all mandatory mutable types, and a `switches` subgroup that verifies switching from any descriptor type to any other.

Each subgroup is further expanded by `createMutableTestVariants` with stage variants (compute, vertex, tessellation control/eval, geometry, fragment, ray tracing).

### single_nonmutable — Single non-mutable descriptor

Cases with a single non-mutable descriptor, providing basic checks to verify copying to non-mutable bindings works. Created at [`vktBindingMutableTests.cpp:4061`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L4061), added at [`vktBindingMutableTests.cpp:4076`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L4076).

Contains subgroups per basic descriptor type, each expanded by `createMutableTestVariants` with reduced stages (compute, vertex, fragment, ray gen).

### one_array — One array of mutable descriptors

Tests using a single array of mutable descriptors. Created in the `arrayCountGroups` loop at [`vktBindingMutableTests.cpp:4104`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L4104), added at [`vktBindingMutableTests.cpp:4188`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L4188).

Each array group is subdivided by unbounded/constant-size and aliasing/no-aliasing combinations. Descriptors rotate through mandatory mutable types. Uses compute-only stages.

### multiple_arrays — Multiple arrays of mutable descriptors

Tests using multiple arrays of mutable descriptors. Created in the `arrayCountGroups` loop at [`vktBindingMutableTests.cpp:4106`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L4106), added at [`vktBindingMutableTests.cpp:4188`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L4188).

Subdivided by unbounded/constant-size and aliasing/no-aliasing. Each binding rotates through mandatory mutable types independently. Uses compute-only stages.

### multiple_arrays_mixed — Multiple arrays of mutable and non-mutable descriptors

Tests using multiple arrays of mutable descriptors mixed with arrays of non-mutable ones. Created in the `arrayCountGroups` loop at [`vktBindingMutableTests.cpp:4108`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L4108), added at [`vktBindingMutableTests.cpp:4188`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L4188).

Non-mutable array bindings are interleaved with mutable ones. Subdivided by unbounded/constant-size and aliasing/no-aliasing. Uses compute-only stages.

### single_and_array — Single mutable binding followed by an array

Cases with a single mutable binding followed by an array of mutable bindings. The array uses a single type beyond the mandatory ones. Created at [`vktBindingMutableTests.cpp:4194`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L4194), added at [`vktBindingMutableTests.cpp:4257`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L4257).

Subgroups per non-mandatory basic descriptor type (excluding input attachment and mandatory types), each subdivided by aliasing/no-aliasing. Uses compute-only stages.

### multiple — Several mutable non-array bindings

Cases with several mutable non-array bindings. Created at [`vktBindingMutableTests.cpp:4262`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L4262), added at [`vktBindingMutableTests.cpp:4293`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L4293).

Contains two subgroups:
- `mutable_only` — Only mutable bindings, each with a different rotated type order.
- `mixed` — Mutable bindings interleaved with non-mutable bindings.

Uses compute-only stages.

### misc — Corner cases

Corner-case tests for mutable descriptor type out-of-range scenarios. Created at [`vktBindingMutableTests.cpp:4298`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L4298), added at [`vktBindingMutableTests.cpp:4342`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L4342).

Generates tests named `mutable_type_out_of_range_<numNonMutDescs><numMutDescs>` by varying the count of non-mutable uniform buffer descriptors (0-2) and mutable storage buffer descriptors (1-2). Mutable descriptors are placed at the end to make them out-of-range.

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
