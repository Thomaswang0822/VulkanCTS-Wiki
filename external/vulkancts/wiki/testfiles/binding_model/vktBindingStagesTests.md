# Binding Stages Tests

Checks descriptor updates from different pipeline bind points with the same call for storage buffer, uniform buffer, and combined image sampler descriptors.

## Source

- [`vktBindingStagesTests.cpp`](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp)

## Registration Hierarchy

```text
binding_model.stages
```

## Test Families

### stages — Update stages from different pipeline bind points

The `stages` group is built directly and adds one case per descriptor type. Evidence starts at [`vktBindingStagesTests.cpp:592`](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L592) and continues through [`vktBindingStagesTests.cpp:612`](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L612).

The group has no child subgroups. It contains three leaf test cases generated from a `DescriptorTypeTest` array ([`vktBindingStagesTests.cpp:592`](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L592)):

| Test case name | Descriptor type |
|----------------|-----------------|
| `storage_buffer` | `VK_DESCRIPTOR_TYPE_STORAGE_BUFFER` |
| `uniform_buffer` | `VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER` |
| `combined_image_sampler` | `VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER` |

VK only. Created in [`vktBindingStagesTests.cpp:589`](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L589); factory entry at [`vktBindingStagesTests.cpp:586`](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L586).

## Parameter Dimensions

| Dimension | Observed values / source |
|-----------|--------------------------|
| Group construction | Verified by [`vktBindingStagesTests.cpp:589`](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L589) |
| Generated families | Derived from arrays, loops, or child additions near [`vktBindingStagesTests.cpp:592`](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L592) |
| Build availability | Root or nested registration determines whether the group is always present or guarded by `CTS_USES_VULKANSC` |

## Support / Feature Requirements

Support checks are implemented near [`vktBindingStagesTests.cpp:579`](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L579). Requirements vary by selected case and extension path; this page records only the recurring gates visible in the inspected file.

## Verification Methods

Support requires maintenance6; cases verify descriptor updates across stage/bind-point combinations.

## Test Principles

- Keep descriptor binding/update behavior observable through shader execution or explicit API success checks.
- Vary one or more binding-model dimensions while preserving traceable generated names.
- Use feature/support gates to skip extension-dependent scenarios rather than broadening unsupported coverage.

## Notes

- This Level-3 page documents a registered test file. Helper-only files are not given separate pages.
