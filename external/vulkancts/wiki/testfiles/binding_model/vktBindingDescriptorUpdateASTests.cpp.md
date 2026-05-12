# Descriptor Update Acceleration Structure Tests

Documents the nested acceleration-structure descriptor update group under `descriptor_update`; it is registered by `vktBindingDescriptorUpdateTests.cpp`, not by the category root.

## Source

- [`vktBindingDescriptorUpdateASTests.cpp`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp)

## Registration Hierarchy

```text
binding_model.descriptor_update.acceleration_structure
├── ray_query
└── ray_tracing
```

The group is created at [`vktBindingDescriptorUpdateASTests.cpp:2568`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L2568); factory entry at [`vktBindingDescriptorUpdateASTests.cpp:2566`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L2566). This is a VK-only nested group under `descriptor_update`.

## Test Families

### ray_query — Ray-query acceleration-structure descriptor updates

Tests descriptor update behavior for acceleration structures accessed via ray queries. Each test type group expands over update methods and pipeline stages.

Update method subgroups (added at [`vktBindingDescriptorUpdateASTests.cpp:2620`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L2620)):

| Subgroup | Update method |
|----------|---------------|
| `regular` | `UPDATE_METHOD_NORMAL` |
| `with_template` | `UPDATE_METHOD_WITH_TEMPLATE` |
| `with_push` | `UPDATE_METHOD_WITH_PUSH` |
| `with_push_template` | `UPDATE_METHOD_WITH_PUSH_TEMPLATE` |

Under each update method, pipeline stage test cases are generated (at [`vktBindingDescriptorUpdateASTests.cpp:2626`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L2626)) for all stages: `vert`, `tesc`, `tese`, `geom`, `frag`, `comp`, `rgen`, `ahit`, `chit`, `miss`, `sect`, `call`.

### ray_tracing — Ray-tracing acceleration-structure descriptor updates

Tests descriptor update behavior for acceleration structures accessed via ray tracing pipelines. Only pipeline stages with `rayTracing = true` are included (at [`vktBindingDescriptorUpdateASTests.cpp:2636`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L2636)): `rgen`, `chit`, `miss`.

Update method subgroups are the same as for `ray_query`:

| Subgroup | Update method |
|----------|---------------|
| `regular` | `UPDATE_METHOD_NORMAL` |
| `with_template` | `UPDATE_METHOD_WITH_TEMPLATE` |
| `with_push` | `UPDATE_METHOD_WITH_PUSH` |
| `with_push_template` | `UPDATE_METHOD_WITH_PUSH_TEMPLATE` |

## Parameter Dimensions

| Dimension | Observed values / source |
|-----------|--------------------------|
| Group construction | Verified by [`vktBindingDescriptorUpdateASTests.cpp:2568`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L2568) |
| Generated families | Derived from arrays, loops, or child additions near [`vktBindingDescriptorUpdateASTests.cpp:2570`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L2570) |
| Build availability | Root or nested registration determines whether the group is always present or guarded by `CTS_USES_VULKANSC` |

## Support / Feature Requirements

Support checks are implemented near [`vktBindingDescriptorUpdateASTests.cpp:2355`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L2355). Requirements vary by selected case and extension path; this page records only the recurring gates visible in the inspected file.

## Verification Methods

Support requires `VK_KHR_acceleration_structure`; ray-tracing paths require ray-tracing support. Cases write AS descriptors and validate shader/ray results.

## Test Principles

- Keep descriptor binding/update behavior observable through shader execution or explicit API success checks.
- Vary one or more binding-model dimensions while preserving traceable generated names.
- Use feature/support gates to skip extension-dependent scenarios rather than broadening unsupported coverage.

## Notes

- This Level-3 page documents a registered test file. Helper-only files are not given separate pages.
