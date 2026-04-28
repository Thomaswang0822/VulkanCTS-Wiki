# Buffer Device Address Tests

Exercises buffer device address loads, conversions, pointer storage, layouts, shader stages, capture/replay stress, and memory-model access-chain cases.

## Source

- [`vktBindingBufferDeviceAddressTests.cpp`](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp)

## Verified Group Name

| Group | Availability | Evidence |
|-------|--------------|----------|
| `buffer_device_address` | VK + VKSC, with Vulkan-only capture-replay details | Created in [`vktBindingBufferDeviceAddressTests.cpp:2224`](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L2224); factory entry at [`vktBindingBufferDeviceAddressTests.cpp:2222`](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L2222) |

## Registration Path

```
binding_model → buffer_device_address
```

## Test Hierarchy

The group name is `buffer_device_address`; generated hierarchy spans descriptor-set count, pointer depth, base buffer type, conversion mode, storage mode, buffer topology, layout, stage, and offset. Evidence starts at [`vktBindingBufferDeviceAddressTests.cpp:2232`](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L2232) and continues through [`vktBindingBufferDeviceAddressTests.cpp:2385`](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L2385).

## Parameter Dimensions

| Dimension | Observed values / source |
|-----------|--------------------------|
| Group construction | Verified by [`vktBindingBufferDeviceAddressTests.cpp:2224`](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L2224) |
| Generated families | Derived from arrays, loops, or child additions near [`vktBindingBufferDeviceAddressTests.cpp:2232`](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L2232) |
| Build availability | Root or nested registration determines whether the group is always present or guarded by `CTS_USES_VULKANSC` |

## Support / Feature Requirements

Support checks are implemented near [`vktBindingBufferDeviceAddressTests.cpp:173`](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L173). Requirements vary by selected case and extension path; this page records only the recurring gates visible in the inspected file.

## Verification Methods

Cases require buffer-device-address functionality and compare shader-visible loaded/stored values or stress capture/replay behavior.

## Test Principles

- Keep descriptor binding/update behavior observable through shader execution or explicit API success checks.
- Vary one or more binding-model dimensions while preserving traceable generated names.
- Use feature/support gates to skip extension-dependent scenarios rather than broadening unsupported coverage.

## Notes

- This Level-3 page documents a registered test file. Helper-only files are not given separate pages.
