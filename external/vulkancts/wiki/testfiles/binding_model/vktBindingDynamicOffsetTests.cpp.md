# Dynamic Offset Tests

Checks dynamic descriptor offset behavior, including Amber shader-reuse tests and push-constant-driven two-pipeline scenarios.

## Source

- [`vktBindingDynamicOffsetTests.cpp`](../../../modules/vulkan/binding_model/vktBindingDynamicOffsetTests.cpp)

## Verified Group Name

| Group | Availability | Evidence |
|-------|--------------|----------|
| `dynamic_offset` | VK only | Created in [`vktBindingDynamicOffsetTests.cpp:425`](../../../modules/vulkan/binding_model/vktBindingDynamicOffsetTests.cpp:425); factory entry at [`vktBindingDynamicOffsetTests.cpp:423`](../../../modules/vulkan/binding_model/vktBindingDynamicOffsetTests.cpp:423) |

## Registration Path

```
binding_model → dynamic_offset
```

## Test Hierarchy

The `dynamic_offset` group adds two Amber tests and generated two-pipeline cases over separate offsets, push-constant ordering, shared layout, and different-set choices. Evidence starts at [`vktBindingDynamicOffsetTests.cpp:392`](../../../modules/vulkan/binding_model/vktBindingDynamicOffsetTests.cpp:392) and continues through [`vktBindingDynamicOffsetTests.cpp:418`](../../../modules/vulkan/binding_model/vktBindingDynamicOffsetTests.cpp:418).

## Parameter Dimensions

| Dimension | Observed values / source |
|-----------|--------------------------|
| Group construction | Verified by [`vktBindingDynamicOffsetTests.cpp:425`](../../../modules/vulkan/binding_model/vktBindingDynamicOffsetTests.cpp:425) |
| Generated families | Derived from arrays, loops, or child additions near [`vktBindingDynamicOffsetTests.cpp:392`](../../../modules/vulkan/binding_model/vktBindingDynamicOffsetTests.cpp:392) |
| Build availability | Root or nested registration determines whether the group is always present or guarded by `CTS_USES_VULKANSC` |

## Support / Feature Requirements

Support checks are implemented near [`vktBindingDynamicOffsetTests.cpp:86`](../../../modules/vulkan/binding_model/vktBindingDynamicOffsetTests.cpp:86). Requirements vary by selected case and extension path; this page records only the recurring gates visible in the inspected file.

## Verification Methods

Cases validate that dynamic offsets select the intended buffer regions across pipeline reuse patterns.

## Test Principles

- Keep descriptor binding/update behavior observable through shader execution or explicit API success checks.
- Vary one or more binding-model dimensions while preserving traceable generated names.
- Use feature/support gates to skip extension-dependent scenarios rather than broadening unsupported coverage.

## Notes

- This Level-3 page documents a registered test file. Helper-only files are not given separate pages.
