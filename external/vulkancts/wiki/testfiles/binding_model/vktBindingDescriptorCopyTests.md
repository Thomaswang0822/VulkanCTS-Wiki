# Descriptor Copy Tests

Verifies descriptor copying for compute, graphics, graphics update-after-bind, and miscellaneous immutable-sampler cases.

The historical Vulkan API test plan's descriptor-creation, shader-access, and update objectives provide high-level binding-model context for descriptor-copy scenarios ([`apitests.adoc`](../../../../../doc/testspecs/VK/apitests.adoc#L281-L297)); current source and mustpass remain authoritative for exact behavior.

## Source

- [`vktBindingDescriptorCopyTests.cpp`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp)

## Registration Hierarchy

```text
binding_model.descriptor_copy
├── compute
├── graphics
├── graphics_uab
└── misc
```

Group `descriptor_copy` (VK + VKSC, with Vulkan-only inline-uniform variations) is created in [`vktBindingDescriptorCopyTests.cpp:3758`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L3758); factory entry at [`vktBindingDescriptorCopyTests.cpp:3754`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L3754).

## Test Families

### compute — Compute pipeline descriptor copy

Created at [`vktBindingDescriptorCopyTests.cpp:3760`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L3760). Populated by [`createTestsForAllDescriptorTypes`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L3766) with `PIPELINE_TYPE_COMPUTE`, which iterates over descriptor types and generates per-type copy scenarios.

### graphics — Graphics pipeline descriptor copy

Created at [`vktBindingDescriptorCopyTests.cpp:3761`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L3761). Populated by [`createTestsForAllDescriptorTypes`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L3767) with `PIPELINE_TYPE_GRAPHICS` (update-after-bind disabled), which iterates over descriptor types and generates per-type copy scenarios.

### graphics_uab — Graphics pipeline descriptor copy with update-after-bind

Created at [`vktBindingDescriptorCopyTests.cpp:3763`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L3763). Populated by [`createTestsForAllDescriptorTypes`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L3768) with `PIPELINE_TYPE_GRAPHICS` and update-after-bind enabled (`true`), which iterates over descriptor types and generates per-type copy scenarios.

### misc — Miscellaneous immutable-sampler copy tests

Created at [`vktBindingDescriptorCopyTests.cpp:3764`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L3764). Contains `CopyImmutableSamplerCase` tests generated from a loop over sampler counts (`1u`, `4u`) and buffer-first ordering (`false`, `true`), producing test names like `copy_immutable_sampler_<count>_images[_buffer_first]`. Evidence at [`vktBindingDescriptorCopyTests.cpp:3770`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L3770) through [`vktBindingDescriptorCopyTests.cpp:3778`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L3778).

## Parameter Dimensions

| Dimension | Observed values / source |
|-----------|--------------------------|
| Group construction | Verified by [`vktBindingDescriptorCopyTests.cpp:3758`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L3758) |
| Generated families | Derived from arrays, loops, or child additions near [`vktBindingDescriptorCopyTests.cpp:3760`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L3760) |
| Build availability | Root or nested registration determines whether the group is always present or guarded by `CTS_USES_VULKANSC` |

## Support / Feature Requirements

Support checks are implemented near [`vktBindingDescriptorCopyTests.cpp:2595`](../../../modules/vulkan/binding_model/vktBindingDescriptorCopyTests.cpp#L2595). Requirements vary by selected case and extension path; this page records only the recurring gates visible in the inspected file.

## Verification Methods

Cases copy descriptors, execute the target pipeline, and verify resources are observed from the copied bindings.

## Test Principles

- Keep descriptor binding/update behavior observable through shader execution or explicit API success checks.
- Vary one or more binding-model dimensions while preserving traceable generated names.
- Use feature/support gates to skip extension-dependent scenarios rather than broadening unsupported coverage.

## Notes

- This Level-3 page documents a registered test file. Helper-only files are not given separate pages.
