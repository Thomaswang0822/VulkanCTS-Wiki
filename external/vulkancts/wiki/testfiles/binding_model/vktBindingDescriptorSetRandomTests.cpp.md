# Descriptor Set Random Tests

Generates random descriptor-set layouts over descriptor-set count, indexing mode, descriptor-count limits, inline uniform blocks, update-after-bind, shader stage, input attachments, and seed.

## Source

- [`vktBindingDescriptorSetRandomTests.cpp`](../../../modules/vulkan/binding_model/vktBindingDescriptorSetRandomTests.cpp)

## Registration Hierarchy

```text
binding_model.descriptorset_random
├── sets4
├── sets8
├── sets16
└── sets32
```

## Test Families

### sets4 — 4 descriptor sets

Random descriptor-set layout tests with 4 descriptor sets. Under this group, the following nested dimensions are iterated:

- **Indexing mode** (`noarray`, `constant`, `unifindexed`, `dynindexed`, `runtimesize`) — defined in `indexCases` near [`vktBindingDescriptorSetRandomTests.cpp:3173`](../../../modules/vulkan/binding_model/vktBindingDescriptorSetRandomTests.cpp#L3173)
- **UBO limit** (`noubo`, `ubolimitlow`, `ubolimithigh`) — defined in `uboCases` near [`vktBindingDescriptorSetRandomTests.cpp:3186`](../../../modules/vulkan/binding_model/vktBindingDescriptorSetRandomTests.cpp#L3186)
- **SSBO limit** (`nosbo`, `sbolimitlow`, `sbolimithigh`) — defined in `sboCases` near [`vktBindingDescriptorSetRandomTests.cpp:3195`](../../../modules/vulkan/binding_model/vktBindingDescriptorSetRandomTests.cpp#L3195)
- **Sampled image limit** (`nosampledimg`, `sampledimglow`, `sampledimghigh`) — defined in `sampledImgCases` near [`vktBindingDescriptorSetRandomTests.cpp:3213`](../../../modules/vulkan/binding_model/vktBindingDescriptorSetRandomTests.cpp#L3213)
- **Storage image/texel buffer** (`outimgonly`, `outimgtexlow`, `lowimgnotex`, `lowimgsingletex`, `storageimghigh`) — defined in `sImgTexCases` near [`vktBindingDescriptorSetRandomTests.cpp:3222`](../../../modules/vulkan/binding_model/vktBindingDescriptorSetRandomTests.cpp#L3222)
- **Inline uniform blocks** (`noiub`, `iublimitlow`, `iublimithigh`) — defined in `iubCases` near [`vktBindingDescriptorSetRandomTests.cpp:3240`](../../../modules/vulkan/binding_model/vktBindingDescriptorSetRandomTests.cpp#L3240)
- **Shader stage** (`comp`, `frag`, `vert`, plus `rgnv`, `rgen`, `sect`, `ahit`, `chit`, `miss`, `call`, `task`, `mesh` on non-VulkanSC) — defined in `stageCases` near [`vktBindingDescriptorSetRandomTests.cpp:3254`](../../../modules/vulkan/binding_model/vktBindingDescriptorSetRandomTests.cpp#L3254)
- **Update after bind** (`nouab`, `uab`) — defined in `uabCases` near [`vktBindingDescriptorSetRandomTests.cpp:3283`](../../../modules/vulkan/binding_model/vktBindingDescriptorSetRandomTests.cpp#L3283)
- **Input attachments** (`noia`, `ialimitlow`, `ialimithigh`) — defined in `iaCases` near [`vktBindingDescriptorSetRandomTests.cpp:3204`](../../../modules/vulkan/binding_model/vktBindingDescriptorSetRandomTests.cpp#L3204); only used in fragment stage

When using 4 sets with low descriptor counts, 10 random seeds are generated per combination; otherwise 1 seed. Leaf test cases are named by their seed number (0, 1, ...).

### sets8 — 8 descriptor sets

Same nested dimension structure as `sets4`, but with 8 descriptor sets. See `sets4` above for the full dimension list.

### sets16 — 16 descriptor sets

Same nested dimension structure as `sets4`, but with 16 descriptor sets. See `sets4` above for the full dimension list.

### sets32 — 32 descriptor sets

Same nested dimension structure as `sets4`, but with 32 descriptor sets. See `sets4` above for the full dimension list.

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
- Vulkan-only stages (ray tracing, task, mesh) are guarded by `CTS_USES_VULKANSC`; VKSC uses a reduced stage set (`comp`, `frag`, `vert` only). Evidence starts at [`vktBindingDescriptorSetRandomTests.cpp:3162`](../../../modules/vulkan/binding_model/vktBindingDescriptorSetRandomTests.cpp#L3162) and continues through [`vktBindingDescriptorSetRandomTests.cpp:3435`](../../../modules/vulkan/binding_model/vktBindingDescriptorSetRandomTests.cpp#L3435).
