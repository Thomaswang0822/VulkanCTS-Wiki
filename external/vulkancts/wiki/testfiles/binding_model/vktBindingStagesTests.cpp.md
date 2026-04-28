# Binding Stages Tests

Checks descriptor updates from different pipeline bind points with the same call for storage buffer, uniform buffer, and combined image sampler descriptors.

## Source

- [`vktBindingStagesTests.cpp`](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp)

## Verified Group Name

| Group | Availability | Evidence |
|-------|--------------|----------|
| `stages` | VK only | Created in [`vktBindingStagesTests.cpp:589`](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp:589); factory entry at [`vktBindingStagesTests.cpp:586`](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp:586) |

## Registration Path

```
binding_model → stages
```

## Test Hierarchy

The `stages` group is built directly and adds one case per descriptor type. Evidence starts at [`vktBindingStagesTests.cpp:592`](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp:592) and continues through [`vktBindingStagesTests.cpp:612`](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp:612).

## Parameter Dimensions

| Dimension | Observed values / source |
|-----------|--------------------------|
| Group construction | Verified by [`vktBindingStagesTests.cpp:589`](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp:589) |
| Generated families | Derived from arrays, loops, or child additions near [`vktBindingStagesTests.cpp:592`](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp:592) |
| Build availability | Root or nested registration determines whether the group is always present or guarded by `CTS_USES_VULKANSC` |

## Support / Feature Requirements

Support checks are implemented near [`vktBindingStagesTests.cpp:579`](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp:579). Requirements vary by selected case and extension path; this page records only the recurring gates visible in the inspected file.

## Verification Methods

Support requires maintenance6; cases verify descriptor updates across stage/bind-point combinations.

## Test Principles

- Keep descriptor binding/update behavior observable through shader execution or explicit API success checks.
- Vary one or more binding-model dimensions while preserving traceable generated names.
- Use feature/support gates to skip extension-dependent scenarios rather than broadening unsupported coverage.

## Notes

- This Level-3 page documents a registered test file. Helper-only files are not given separate pages.
