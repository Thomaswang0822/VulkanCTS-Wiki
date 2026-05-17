# Descriptor Combination Tests

Exercises combinations where descriptor-buffer and legacy descriptor mechanisms interact in the same command buffer or with capture replay and custom border color.

## Source

- [`vktBindingDescriptorCombinationTests.cpp`](../../../modules/vulkan/binding_model/vktBindingDescriptorCombinationTests.cpp)

## Registration Hierarchy

```text
binding_model.descriptor_combination
└── basic
```

## Test Families

### basic — Basic descriptor combination cases

The `basic` subgroup contains two named combination cases added to a `basic` child group at [`vktBindingDescriptorCombinationTests.cpp:676`](../../../modules/vulkan/binding_model/vktBindingDescriptorCombinationTests.cpp#L676). Evidence starts at [`vktBindingDescriptorCombinationTests.cpp:668`](../../../modules/vulkan/binding_model/vktBindingDescriptorCombinationTests.cpp#L668) and continues through [`vktBindingDescriptorCombinationTests.cpp:684`](../../../modules/vulkan/binding_model/vktBindingDescriptorCombinationTests.cpp#L684).

The two test cases are:

| Test case name | TestType enum | Source |
|----------------|---------------|--------|
| `descriptor_buffer_and_legacy_descriptor_in_command_buffer` | `DESCRIPTOR_BUFFER_AND_LEGACY_DESCRIPTOR_IN_COMMAND_BUFFER` | [`vktBindingDescriptorCombinationTests.cpp:670`](../../../modules/vulkan/binding_model/vktBindingDescriptorCombinationTests.cpp#L670) |
| `descriptor_buffer_capture_replay_with_custom_border_color` | `DESCRIPTOR_BUFFER_CAPTURE_REPLAY_WITH_CUSTOM_BORDER_COLOR` | [`vktBindingDescriptorCombinationTests.cpp:672`](../../../modules/vulkan/binding_model/vktBindingDescriptorCombinationTests.cpp#L672) |

## Parameter Dimensions

| Dimension | Observed values / source |
|-----------|--------------------------|
| Group construction | Verified by [`vktBindingDescriptorCombinationTests.cpp:691`](../../../modules/vulkan/binding_model/vktBindingDescriptorCombinationTests.cpp#L691) |
| Generated families | Derived from arrays, loops, or child additions near [`vktBindingDescriptorCombinationTests.cpp:668`](../../../modules/vulkan/binding_model/vktBindingDescriptorCombinationTests.cpp#L668) |
| Build availability | Root or nested registration determines whether the group is always present or guarded by `CTS_USES_VULKANSC` |

## Support / Feature Requirements

Support checks are implemented near [`vktBindingDescriptorCombinationTests.cpp:592`](../../../modules/vulkan/binding_model/vktBindingDescriptorCombinationTests.cpp#L592). Requirements vary by selected case and extension path; this page records only the recurring gates visible in the inspected file.

## Verification Methods

Support checks require the extension mix needed by each combination case; execution verifies the combined descriptor path works.

## Test Principles

- Keep descriptor binding/update behavior observable through shader execution or explicit API success checks.
- Vary one or more binding-model dimensions while preserving traceable generated names.
- Use feature/support gates to skip extension-dependent scenarios rather than broadening unsupported coverage.

## Notes

- This Level-3 page documents a registered test file. Helper-only files are not given separate pages.
