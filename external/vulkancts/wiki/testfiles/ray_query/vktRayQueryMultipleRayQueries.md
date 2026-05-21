# vktRayQueryMultipleRayQueries

Multiple simultaneous ray-query objects. The registered hierarchy comes from `createMultipleRayQueryTests()` in [vktRayQueryMultipleRayQueries.cpp](../../../modules/vulkan/ray_query/vktRayQueryMultipleRayQueries.cpp#L401-L470).

## Source Files

| Role | Link |
|------|------|
| Implementation and registration | [vktRayQueryMultipleRayQueries.cpp](../../../modules/vulkan/ray_query/vktRayQueryMultipleRayQueries.cpp) |

## Registration Hierarchy

```text
ray_query.multiple_ray_queries
├── vertex_shader
├── tess_control_shader
├── tess_evaluation_shader
├── geometry_shader
├── fragment_shader
├── compute_shader
├── rgen_shader
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

Each direct child is one shader source in the registration array [vktRayQueryMultipleRayQueries.cpp](../../../modules/vulkan/ray_query/vktRayQueryMultipleRayQueries.cpp#L401-L470).

## Support Requirements

Cases require acceleration-structure and ray-query functionality, with tessellation, geometry, vertex-pipeline-store, and ray-tracing-pipeline gates for relevant stages [vktRayQueryMultipleRayQueries.cpp](../../../modules/vulkan/ray_query/vktRayQueryMultipleRayQueries.cpp#L116-L161).

## Verification Methods

Expected results are computed in `computeExpectedResults()` and compared with result data, failing on any mismatch [vktRayQueryMultipleRayQueries.cpp](../../../modules/vulkan/ray_query/vktRayQueryMultipleRayQueries.cpp#L68-L77) and [vktRayQueryMultipleRayQueries.cpp](../../../modules/vulkan/ray_query/vktRayQueryMultipleRayQueries.cpp#L368-L397).

## Test Principles

The file varies the registered dimensions while comparing shader-produced ray-query results against explicit CPU-side references or expected scalar/vector values.
