# Inline Uniform Block Tests

Verifies inline uniform block descriptor writes and copies with different sizes and offsets.

## Source

- [`vktBindingDescriptorInlineUniformTests.cpp`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp)

## Registration Hierarchy

```text
binding_model.inline_uniform_blocks
├── write_size_4
├── write_size_8
├── write_size_16
├── write_offset_nonzero
├── copy_size_4
├── copy_size_8
├── copy_size_16
├── copy_at_offset_nonzero
└── copy_from_offset_nonzero
```

VK only. Group created at [`vktBindingDescriptorInlineUniformTests.cpp:848`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L848); factory entry at [`vktBindingDescriptorInlineUniformTests.cpp:846`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L846). Helper builders add write and copy cases with size and nonzero-offset variants; evidence spans [`vktBindingDescriptorInlineUniformTests.cpp:766`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L766) through [`vktBindingDescriptorInlineUniformTests.cpp:850`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L850).

## Test Families

### write_size_4 — Write 4-byte inline uniform block

Writes 4 bytes to an inline uniform block descriptor at binding 0, set 0. Source: [`vktBindingDescriptorInlineUniformTests.cpp:772-774`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L772).

### write_size_8 — Write 8-byte inline uniform block

Writes 8 bytes to an inline uniform block descriptor at binding 0, set 0. Source: [`vktBindingDescriptorInlineUniformTests.cpp:778-781`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L778).

### write_size_16 — Write 16-byte inline uniform block

Writes 16 bytes to an inline uniform block descriptor at binding 0, set 0. Source: [`vktBindingDescriptorInlineUniformTests.cpp:786-788`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L786).

### write_offset_nonzero — Write at nonzero offset

Writes 8 bytes at offset 4 within a 16-byte inline uniform block descriptor at binding 0, set 0. Source: [`vktBindingDescriptorInlineUniformTests.cpp:793-796`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L793).

### copy_size_4 — Copy 4-byte inline uniform block

Copies 4 bytes between two inline uniform block descriptors (set 0, bindings 0 and 1). Source: [`vktBindingDescriptorInlineUniformTests.cpp:806-809`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L806).

### copy_size_8 — Copy 8-byte inline uniform block

Copies 8 bytes between two inline uniform block descriptors (set 0, bindings 0 and 1). Source: [`vktBindingDescriptorInlineUniformTests.cpp:813-817`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L813).

### copy_size_16 — Copy 16-byte inline uniform block

Copies 16 bytes between two inline uniform block descriptors (set 0, bindings 0 and 1). Source: [`vktBindingDescriptorInlineUniformTests.cpp:820-825`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L820).

### copy_at_offset_nonzero — Copy to nonzero destination offset

Copies 8 bytes from offset 0 of a 16-byte source descriptor to offset 4 of a 16-byte destination descriptor (set 0, bindings 0 and 1). Source: [`vktBindingDescriptorInlineUniformTests.cpp:828-833`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L828).

### copy_from_offset_nonzero — Copy from nonzero source offset

Copies 8 bytes from offset 4 of a 16-byte source descriptor to offset 0 of a 16-byte destination descriptor (set 0, bindings 0 and 1). Source: [`vktBindingDescriptorInlineUniformTests.cpp:836-841`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L836).

## Parameter Dimensions

| Dimension | Observed values / source |
|-----------|--------------------------|
| Group construction | Verified by [`vktBindingDescriptorInlineUniformTests.cpp:848`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L848) |
| Generated families | Derived from arrays, loops, or child additions near [`vktBindingDescriptorInlineUniformTests.cpp:766`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L766) |
| Build availability | Root or nested registration determines whether the group is always present or guarded by `CTS_USES_VULKANSC` |

## Support / Feature Requirements

Support checks are implemented near [`vktBindingDescriptorInlineUniformTests.cpp:699`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L699). Requirements vary by selected case and extension path; this page records only the recurring gates visible in the inspected file.

## Verification Methods

Support checks require inline uniform block functionality; cases validate shader-visible inline uniform data after writes or copies.

## Test Principles

- Keep descriptor binding/update behavior observable through shader execution or explicit API success checks.
- Vary one or more binding-model dimensions while preserving traceable generated names.
- Use feature/support gates to skip extension-dependent scenarios rather than broadening unsupported coverage.

## Notes

- This Level-3 page documents a registered test file. Helper-only files are not given separate pages.
