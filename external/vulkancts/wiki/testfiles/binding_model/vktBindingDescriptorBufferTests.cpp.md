# Descriptor Buffer Tests

Covers `VK_EXT_descriptor_buffer` in traditional, sparse-binding, and sparse-residency descriptor-buffer resource residency modes.

## Source

- [`vktBindingDescriptorBufferTests.cpp`](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp)

## Verified Group Name

| Group | Availability | Evidence |
|-------|--------------|----------|
| `descriptor_buffer` | VK only | Created in [`vktBindingDescriptorBufferTests.cpp:7899`](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L7899); factory entry at [`vktBindingDescriptorBufferTests.cpp:7897`](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L7897) |

## Registration Path

```
binding_model → descriptor_buffer
```

## Test Hierarchy

The `descriptor_buffer` group contains `traditional_buffer`, `sparse_binding_buffer`, and `sparse_residency_buffer`, each populated with basic, single, multiple, max, push, robustness, capture-replay, mutable, and YCbCr scenarios where applicable. Evidence starts at [`vktBindingDescriptorBufferTests.cpp:7879`](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L7879) and continues through [`vktBindingDescriptorBufferTests.cpp:7892`](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L7892).

## Parameter Dimensions

| Dimension | Observed values / source |
|-----------|--------------------------|
| Group construction | Verified by [`vktBindingDescriptorBufferTests.cpp:7899`](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L7899) |
| Generated families | Derived from arrays, loops, or child additions near [`vktBindingDescriptorBufferTests.cpp:7879`](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L7879) |
| Build availability | Root or nested registration determines whether the group is always present or guarded by `CTS_USES_VULKANSC` |

## Support / Feature Requirements

Support checks are implemented near [`vktBindingDescriptorBufferTests.cpp:2351`](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L2351). Requirements vary by selected case and extension path; this page records only the recurring gates visible in the inspected file.

## Verification Methods

Cases build descriptor-buffer layouts, bind descriptor buffers, execute shaders, and compare outputs; support checks gate descriptor-buffer and selected descriptor features.

## Test Principles

- Keep descriptor binding/update behavior observable through shader execution or explicit API success checks.
- Vary one or more binding-model dimensions while preserving traceable generated names.
- Use feature/support gates to skip extension-dependent scenarios rather than broadening unsupported coverage.

## Notes

- This Level-3 page documents a registered test file. Helper-only files are not given separate pages.
