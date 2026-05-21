# vktRayQueryOpacityMicromapTests

Opacity micromap ray-query integration. The registered hierarchy comes from `createOpacityMicromapTests()` in [vktRayQueryOpacityMicromapTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryOpacityMicromapTests.cpp#L1267-L1275).

## Source Files

| Role | Link |
|------|------|
| Implementation and registration | [vktRayQueryOpacityMicromapTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryOpacityMicromapTests.cpp) |

## Registration Hierarchy

```text
ray_query.opacity_micromap
├── render
└── copy
```

## Test Families

### render — Registered child

This direct child is listed in the registration hierarchy and is covered by the parameter evidence below.

### copy — Registered child

This direct child is listed in the registration hierarchy and is covered by the parameter evidence below.

## Parameter Dimensions

`render` accesses opacity micromap formats through shader source, flags, map/special-index modes, subdivision level, and non-zero-base variants; `copy` iterates copy types, modes, levels, and a maintenance5 case [vktRayQueryOpacityMicromapTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryOpacityMicromapTests.cpp#L1070-L1264).

## Support Requirements

Cases require ray-query, acceleration-structure, and `VK_EXT_opacity_micromap`; maintenance5 variants require `VK_KHR_maintenance5`, and raygen requires ray-tracing-pipeline support [vktRayQueryOpacityMicromapTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryOpacityMicromapTests.cpp#L153-L193).

## Verification Methods

The test computes expected output modes, reads the output buffer, logs mismatches, and fails when unexpected values are found [vktRayQueryOpacityMicromapTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryOpacityMicromapTests.cpp#L788-L1065).

## Test Principles

The file varies the registered dimensions while comparing shader-produced ray-query results against explicit CPU-side references or expected scalar/vector values.
