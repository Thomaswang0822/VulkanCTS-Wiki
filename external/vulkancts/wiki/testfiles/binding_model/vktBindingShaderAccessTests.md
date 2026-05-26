# Shader Access Tests

Verifies descriptor visibility and shader access through primary/secondary command-buffer binding paths, descriptor update methods, descriptor types, shader stages, and descriptor input shapes.

The historical Vulkan API test plan lists shader access through varied descriptor layouts as a binding-model objective ([`apitests.adoc`](../../../../../doc/testspecs/VK/apitests.adoc#L281-L289)); current source and mustpass remain authoritative for exact behavior.

## Source

- [`vktBindingShaderAccessTests.cpp`](../../../modules/vulkan/binding_model/vktBindingShaderAccessTests.cpp)

## Registration Hierarchy

```text
binding_model.shader_access
├── primary_cmd_buf
└── secondary_cmd_buf
```

Group created at [`vktBindingShaderAccessTests.cpp:9865`](../../../modules/vulkan/binding_model/vktBindingShaderAccessTests.cpp#L9865); factory entry at [`vktBindingShaderAccessTests.cpp:9724`](../../../modules/vulkan/binding_model/vktBindingShaderAccessTests.cpp#L9724). Available for VK + VKSC.

## Test Families

### primary_cmd_buf — Descriptor binding in primary command buffer

Tests where descriptor sets are bound in a primary command buffer. Under this group the hierarchy expands by bind command (`bind` / `bind2`), then by descriptor update method, descriptor type, shader stage, and descriptor-dimension shape.

- **Bind commands**: `bind` (vkCmdBindDescriptorSets) and `bind2` (vkCmdBindDescriptorSets2) ([`vktBindingShaderAccessTests.cpp:9860-9863`](../../../modules/vulkan/binding_model/vktBindingShaderAccessTests.cpp#L9860-L9863))
- **Update methods**: normal (empty name, direct write), `with_template`, `with_push`, `with_push_template` (template and push methods excluded under Vulkan SC via `CTS_USES_VULKANSC`) ([`vktBindingShaderAccessTests.cpp:9737-9750`](../../../modules/vulkan/binding_model/vktBindingShaderAccessTests.cpp#L9737-L9750))
- **Descriptor types**: `sampler_mutable`, `sampler_immutable`, `combined_image_sampler_mutable`, `combined_image_sampler_immutable`, `storage_image`, `uniform_texel_buffer`, `storage_texel_buffer`, `uniform_buffer`, `storage_buffer`, `uniform_buffer_dynamic`, `storage_buffer_dynamic` ([`vktBindingShaderAccessTests.cpp:9757-9778`](../../../modules/vulkan/binding_model/vktBindingShaderAccessTests.cpp#L9757-L9778))
- **Shader stages**: `no_access`, `vertex`, `tess_ctrl`, `tess_eval`, `geometry`, `fragment`, `compute`, `vertex_fragment` ([`vktBindingShaderAccessTests.cpp:9785-9843`](../../../modules/vulkan/binding_model/vktBindingShaderAccessTests.cpp#L9785-L9843))
- **Descriptor-dimension shapes**: `single_descriptor`, `multiple_contiguous_descriptors`, `multiple_discontiguous_descriptors`, `multiple_arbitrary_descriptors`, `descriptor_array` ([`vktBindingShaderAccessTests.cpp:9848-9854`](../../../modules/vulkan/binding_model/vktBindingShaderAccessTests.cpp#L9848-L9854))
- **Multiple descriptor sets**: each stage group also contains `multiple_descriptor_sets` and `multiple_discontiguous_descriptor_sets` subgroups (except for push-descriptor update methods, which only support a single descriptor set layout) ([`vktBindingShaderAccessTests.cpp:9894-9898`](../../../modules/vulkan/binding_model/vktBindingShaderAccessTests.cpp#L9894-L9898))

### secondary_cmd_buf — Descriptor binding in secondary command buffer

Tests where descriptor sets are bound in a secondary command buffer. The hierarchy mirrors `primary_cmd_buf` but only shader stages that support secondary command buffers are included (i.e., `compute` is excluded because `supportsSecondaryCmdBufs` is `false` for that stage) ([`vktBindingShaderAccessTests.cpp:9890`](../../../modules/vulkan/binding_model/vktBindingShaderAccessTests.cpp#L9890)).

Otherwise the same bind-command, update-method, descriptor-type, and descriptor-dimension expansion applies as documented under `primary_cmd_buf`.

## Parameter Dimensions

| Dimension | Observed values / source |
|-----------|--------------------------|
| Group construction | Verified by [`vktBindingShaderAccessTests.cpp:9865`](../../../modules/vulkan/binding_model/vktBindingShaderAccessTests.cpp#L9865) |
| Generated families | Derived from arrays, loops, or child additions near [`vktBindingShaderAccessTests.cpp:9726`](../../../modules/vulkan/binding_model/vktBindingShaderAccessTests.cpp#L9726) |
| Build availability | Root or nested registration determines whether the group is always present or guarded by `CTS_USES_VULKANSC` |

## Support / Feature Requirements

Support checks are implemented near [`vktBindingShaderAccessTests.cpp:3631`](../../../modules/vulkan/binding_model/vktBindingShaderAccessTests.cpp#L3631). Requirements vary by selected case and extension path; this page records only the recurring gates visible in the inspected file.

## Verification Methods

Access is checked by rendering or dispatching shader programs that consume descriptors and compare generated output against expected data.

## Test Principles

- Keep descriptor binding/update behavior observable through shader execution or explicit API success checks.
- Vary one or more binding-model dimensions while preserving traceable generated names.
- Use feature/support gates to skip extension-dependent scenarios rather than broadening unsupported coverage.

## Notes

- This Level-3 page documents a registered test file. Helper-only files are not given separate pages.
