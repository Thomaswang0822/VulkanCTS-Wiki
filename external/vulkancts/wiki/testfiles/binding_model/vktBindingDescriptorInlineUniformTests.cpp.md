# Inline Uniform Block Tests

Verifies inline uniform block descriptor writes and copies with different sizes and offsets.

## Source

- [`vktBindingDescriptorInlineUniformTests.cpp`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp)

## Verified Group Name

| Group | Availability | Evidence |
|-------|--------------|----------|
| `inline_uniform_blocks` | VK only | Created in [`vktBindingDescriptorInlineUniformTests.cpp:848`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp:848); factory entry at [`vktBindingDescriptorInlineUniformTests.cpp:846`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp:846) |

## Registration Path

```
binding_model → inline_uniform_blocks
```

## Test Hierarchy

The group name is `inline_uniform_blocks`; helper builders add write and copy cases such as size and nonzero-offset variants. Evidence starts at [`vktBindingDescriptorInlineUniformTests.cpp:766`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp:766) and continues through [`vktBindingDescriptorInlineUniformTests.cpp:850`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp:850).

## Parameter Dimensions

| Dimension | Observed values / source |
|-----------|--------------------------|
| Group construction | Verified by [`vktBindingDescriptorInlineUniformTests.cpp:848`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp:848) |
| Generated families | Derived from arrays, loops, or child additions near [`vktBindingDescriptorInlineUniformTests.cpp:766`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp:766) |
| Build availability | Root or nested registration determines whether the group is always present or guarded by `CTS_USES_VULKANSC` |

## Support / Feature Requirements

Support checks are implemented near [`vktBindingDescriptorInlineUniformTests.cpp:699`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp:699). Requirements vary by selected case and extension path; this page records only the recurring gates visible in the inspected file.

## Verification Methods

Support checks require inline uniform block functionality; cases validate shader-visible inline uniform data after writes or copies.

## Test Principles

- Keep descriptor binding/update behavior observable through shader execution or explicit API success checks.
- Vary one or more binding-model dimensions while preserving traceable generated names.
- Use feature/support gates to skip extension-dependent scenarios rather than broadening unsupported coverage.

## Notes

- This Level-3 page documents a registered test file. Helper-only files are not given separate pages.
