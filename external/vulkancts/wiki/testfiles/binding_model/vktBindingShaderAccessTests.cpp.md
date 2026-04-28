# Shader Access Tests

Verifies descriptor visibility and shader access through primary/secondary command-buffer binding paths, descriptor update methods, descriptor types, shader stages, and descriptor input shapes.

## Source

- [`vktBindingShaderAccessTests.cpp`](../../../modules/vulkan/binding_model/vktBindingShaderAccessTests.cpp)

## Verified Group Name

| Group | Availability | Evidence |
|-------|--------------|----------|
| `shader_access` | VK + VKSC | Created in [`vktBindingShaderAccessTests.cpp:9865`](../../../modules/vulkan/binding_model/vktBindingShaderAccessTests.cpp:9865); factory entry at [`vktBindingShaderAccessTests.cpp:9724`](../../../modules/vulkan/binding_model/vktBindingShaderAccessTests.cpp:9724) |

## Registration Path

```
binding_model → shader_access
```

## Test Hierarchy

The file builds the `shader_access` group and expands bind location, bind command, update method, descriptor type, stage, and descriptor-dimension tables into cases. Vulkan SC excludes template and push update methods. Evidence starts at [`vktBindingShaderAccessTests.cpp:9726`](../../../modules/vulkan/binding_model/vktBindingShaderAccessTests.cpp:9726) and continues through [`vktBindingShaderAccessTests.cpp:9854`](../../../modules/vulkan/binding_model/vktBindingShaderAccessTests.cpp:9854).

## Parameter Dimensions

| Dimension | Observed values / source |
|-----------|--------------------------|
| Group construction | Verified by [`vktBindingShaderAccessTests.cpp:9865`](../../../modules/vulkan/binding_model/vktBindingShaderAccessTests.cpp:9865) |
| Generated families | Derived from arrays, loops, or child additions near [`vktBindingShaderAccessTests.cpp:9726`](../../../modules/vulkan/binding_model/vktBindingShaderAccessTests.cpp:9726) |
| Build availability | Root or nested registration determines whether the group is always present or guarded by `CTS_USES_VULKANSC` |

## Support / Feature Requirements

Support checks are implemented near [`vktBindingShaderAccessTests.cpp:3631`](../../../modules/vulkan/binding_model/vktBindingShaderAccessTests.cpp:3631). Requirements vary by selected case and extension path; this page records only the recurring gates visible in the inspected file.

## Verification Methods

Access is checked by rendering or dispatching shader programs that consume descriptors and compare generated output against expected data.

## Test Principles

- Keep descriptor binding/update behavior observable through shader execution or explicit API success checks.
- Vary one or more binding-model dimensions while preserving traceable generated names.
- Use feature/support gates to skip extension-dependent scenarios rather than broadening unsupported coverage.

## Notes

- This Level-3 page documents a registered test file. Helper-only files are not given separate pages.
