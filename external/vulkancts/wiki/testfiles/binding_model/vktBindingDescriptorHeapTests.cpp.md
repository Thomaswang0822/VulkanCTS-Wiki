# Descriptor Heap Tests

Covers `VK_EXT_descriptor_heap` behavior across limits, basic descriptor access, dynamic indexing, binding mappings, heap switching, queues, invalidation, graphics, SPIR-V, non-packed and unaligned mappings.

## Source

- [`vktBindingDescriptorHeapTests.cpp`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp)

## Verified Group Name

| Group | Availability | Evidence |
|-------|--------------|----------|
| `descriptor_heap` | VK only | Created in [`vktBindingDescriptorHeapTests.cpp:14803`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14803); factory entry at [`vktBindingDescriptorHeapTests.cpp:14801`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14801) |

## Registration Path

```
binding_model → descriptor_heap
```

## Test Hierarchy

The group name is `descriptor_heap`; `populateDescriptorHeapTests` adds many focused subgroups such as `limit`, `basic`, `dynamic_indexing`, `binding_mapping`, `push_data`, `null_descriptor`, `graphics`, and `special_heap`. Evidence starts at [`vktBindingDescriptorHeapTests.cpp:12700`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L12700) and continues through [`vktBindingDescriptorHeapTests.cpp:14803`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14803).

## Parameter Dimensions

| Dimension | Observed values / source |
|-----------|--------------------------|
| Group construction | Verified by [`vktBindingDescriptorHeapTests.cpp:14803`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14803) |
| Generated families | Derived from arrays, loops, or child additions near [`vktBindingDescriptorHeapTests.cpp:12700`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L12700) |
| Build availability | Root or nested registration determines whether the group is always present or guarded by `CTS_USES_VULKANSC` |

## Support / Feature Requirements

Support checks are implemented near [`vktBindingDescriptorHeapTests.cpp:508`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L508). Requirements vary by selected case and extension path; this page records only the recurring gates visible in the inspected file.

## Verification Methods

Cases bind resource and sampler heaps, execute shader pipelines, and compare results; support checks gate descriptor-heap and selected extension features.

## Test Principles

- Keep descriptor binding/update behavior observable through shader execution or explicit API success checks.
- Vary one or more binding-model dimensions while preserving traceable generated names.
- Use feature/support gates to skip extension-dependent scenarios rather than broadening unsupported coverage.

## Notes

- This Level-3 page documents a registered test file. Helper-only files are not given separate pages.
