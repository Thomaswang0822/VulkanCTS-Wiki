# vktRayQueryStressTests

Stress scenes for ray queries. The registered hierarchy comes from `createRayQueryStressTests()` in [vktRayQueryStressTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryStressTests.cpp#L474-L572).

## Source Files

| Role | Link |
|------|------|
| Implementation and registration | [vktRayQueryStressTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryStressTests.cpp) |

## Registration Hierarchy

```text
ray_query.stress
├── vertex_shader
├── tess_control_shader
├── tess_evaluation_shader
├── geometry_shader
├── fragment_shader
├── compute_shader
├── rgen_shader
├── rgen_rt_shader
├── isect_shader
├── ahit_shader
├── chit_shader
├── miss_shader
└── call_shader
```

## Test Families

### vertex_shader — Registered child

This direct child is listed in the registration hierarchy and is covered by the parameter evidence below.

### tess_control_shader — Registered child

This direct child is listed in the registration hierarchy and is covered by the parameter evidence below.

### tess_evaluation_shader — Registered child

This direct child is listed in the registration hierarchy and is covered by the parameter evidence below.

### geometry_shader — Registered child

This direct child is listed in the registration hierarchy and is covered by the parameter evidence below.

### fragment_shader — Registered child

This direct child is listed in the registration hierarchy and is covered by the parameter evidence below.

### compute_shader — Registered child

This direct child is listed in the registration hierarchy and is covered by the parameter evidence below.

### rgen_shader — Registered child

This direct child is listed in the registration hierarchy and is covered by the parameter evidence below.

### rgen_rt_shader — Registered child

This direct child is listed in the registration hierarchy and is covered by the parameter evidence below.

### isect_shader — Registered child

This direct child is listed in the registration hierarchy and is covered by the parameter evidence below.

### ahit_shader — Registered child

This direct child is listed in the registration hierarchy and is covered by the parameter evidence below.

### chit_shader — Registered child

This direct child is listed in the registration hierarchy and is covered by the parameter evidence below.

### miss_shader — Registered child

This direct child is listed in the registration hierarchy and is covered by the parameter evidence below.

### call_shader — Registered child

This direct child is listed in the registration hierarchy and is covered by the parameter evidence below.

## Parameter Dimensions

Each direct child is a shader source and contains `triangles` and `aabbs` leaves; non-ray-tracing pipelines adjust ray size to a power-of-two-derived value [vktRayQueryStressTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryStressTests.cpp#L474-L572).

## Support Requirements

Cases require acceleration-structure and ray-query functionality, with tessellation, geometry, vertex-pipeline-store, and ray-tracing-pipeline gates where selected [vktRayQueryStressTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryStressTests.cpp#L128-L176).

## Verification Methods

The test builds expected primitive ID/intersection data and fails if result data mismatches expected output [vktRayQueryStressTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryStressTests.cpp#L326-L380) and [vktRayQueryStressTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryStressTests.cpp#L439-L469).

## Test Principles

The file varies the registered dimensions while comparing shader-produced ray-query results against explicit CPU-side references or expected scalar/vector values.
