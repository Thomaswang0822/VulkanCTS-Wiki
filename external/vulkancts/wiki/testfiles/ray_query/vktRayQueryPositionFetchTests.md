# vktRayQueryPositionFetchTests

Triangle vertex-position fetch. The registered hierarchy comes from `createPositionFetchTests()` in [vktRayQueryPositionFetchTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryPositionFetchTests.cpp#L732-L837).

## Source Files

| Role | Link |
|------|------|
| Implementation and registration | [vktRayQueryPositionFetchTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryPositionFetchTests.cpp) |

## Registration Hierarchy

```text
ray_query.position_fetch
├── vertex_shader
├── compute_shader
└── rgen_shader
```

## Test Families

### vertex_shader — Registered child

This direct child is listed in the registration hierarchy and is covered by the parameter evidence below.

### compute_shader — Registered child

This direct child is listed in the registration hierarchy and is covered by the parameter evidence below.

### rgen_shader — Registered child

This direct child is listed in the registration hierarchy and is covered by the parameter evidence below.

## Parameter Dimensions

The registration crosses shader source, CPU/GPU build, 15 vertex formats, and flag masks [vktRayQueryPositionFetchTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryPositionFetchTests.cpp#L732-L837).

## Support / Feature Requirements

Cases require ray-query, acceleration-structure, `VK_KHR_ray_tracing_position_fetch`, supported vertex formats, host commands for CPU builds, and stage-specific gates [vktRayQueryPositionFetchTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryPositionFetchTests.cpp#L132-L186).

## Verification Methods

The test computes expected fetched vertex positions and fails when output vectors differ beyond tolerance [vktRayQueryPositionFetchTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryPositionFetchTests.cpp#L504-L516) and [vktRayQueryPositionFetchTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryPositionFetchTests.cpp#L693-L728).

## Test Principles

The file varies the registered dimensions while comparing shader-produced ray-query results against explicit CPU-side references or expected scalar/vector values.
