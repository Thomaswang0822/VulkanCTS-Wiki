# vktRayQueryTraversalControlTests

This file registers `ray_query.traversal_control` tests for explicit generation and skipping of intersections. The group and child matrices are built in [vktRayQueryTraversalControlTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryTraversalControlTests.cpp#L2061-L2165).

## Source Files

| Role | Link |
|------|------|
| Implementation and registration | [vktRayQueryTraversalControlTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryTraversalControlTests.cpp#L2061-L2165) |

## Registration Hierarchy

```text
ray_query.traversal_control
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

### vertex_shader — Graphics vertex-stage traversal control

Uses the graphics pipeline source entry `vertex_shader` and combines it with `generate_intersection` and `skip_intersection` children and `triangles`/`aabbs` leaves [vktRayQueryTraversalControlTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryTraversalControlTests.cpp#L2071-L2129).

### tess_control_shader — Tessellation-control traversal control

Registered in the same shader-source array and gated by tessellation feature checks when selected [vktRayQueryTraversalControlTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryTraversalControlTests.cpp#L2071-L2074) and [vktRayQueryTraversalControlTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryTraversalControlTests.cpp#L1312-L1318).

### tess_evaluation_shader — Tessellation-evaluation traversal control

Uses the tessellation-evaluation source entry and the same generate/skip and geometry combinations [vktRayQueryTraversalControlTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryTraversalControlTests.cpp#L2071-L2075).

### geometry_shader — Geometry-stage traversal control

Registered through the graphics pipeline entry and gated by geometry-shader support [vktRayQueryTraversalControlTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryTraversalControlTests.cpp#L2075-L2079) and [vktRayQueryTraversalControlTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryTraversalControlTests.cpp#L1319-L1320).

### fragment_shader — Fragment-stage traversal control

Uses the fragment source entry and image-reference verification for generated or skipped hits [vktRayQueryTraversalControlTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryTraversalControlTests.cpp#L2080-L2084) and [vktRayQueryTraversalControlTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryTraversalControlTests.cpp#L674-L681).

### compute_shader — Compute-stage traversal control

Uses the compute pipeline source entry [vktRayQueryTraversalControlTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryTraversalControlTests.cpp#L2085-L2089).

### rgen_shader — Ray-generation traversal control

Ray-tracing pipeline source entries require `VK_KHR_ray_tracing_pipeline` when selected [vktRayQueryTraversalControlTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryTraversalControlTests.cpp#L2090-L2119) and [vktRayQueryTraversalControlTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryTraversalControlTests.cpp#L1334-L1340).

### isect_shader — Intersection-shader traversal control

Registered as a ray-tracing pipeline source in [vktRayQueryTraversalControlTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryTraversalControlTests.cpp#L2095-L2099).

### ahit_shader — Any-hit traversal control

Registered as a ray-tracing pipeline source in [vktRayQueryTraversalControlTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryTraversalControlTests.cpp#L2100-L2104).

### chit_shader — Closest-hit traversal control

Registered as a ray-tracing pipeline source in [vktRayQueryTraversalControlTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryTraversalControlTests.cpp#L2105-L2109).

### miss_shader — Miss-shader traversal control

Registered as a ray-tracing pipeline source in [vktRayQueryTraversalControlTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryTraversalControlTests.cpp#L2110-L2114).

### call_shader — Callable-shader traversal control

Registered as a ray-tracing pipeline source in [vktRayQueryTraversalControlTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryTraversalControlTests.cpp#L2115-L2119).

## Parameter Dimensions

Shader source, generated-vs-skipped intersection mode, and bottom geometry (`triangles`, `aabbs`) are explicit arrays in [vktRayQueryTraversalControlTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryTraversalControlTests.cpp#L2066-L2138).

## Support Requirements

Cases require acceleration-structure and ray-query functionality and feature bits [vktRayQueryTraversalControlTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryTraversalControlTests.cpp#L1297-L1310), with stage-specific tessellation, geometry, vertex-pipeline-store, and ray-tracing-pipeline gates [vktRayQueryTraversalControlTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryTraversalControlTests.cpp#L1312-L1340).

## Verification Methods

The verifier builds expected image layers for generated or skipped intersections and compares them with `tcu::intThresholdCompare` [vktRayQueryTraversalControlTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryTraversalControlTests.cpp#L580-L688). The instance reports pass or fail from the comparison result [vktRayQueryTraversalControlTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryTraversalControlTests.cpp#L2047-L2057).

## Test Principles

The cases isolate traversal-control operations by making expected hit values depend on whether generated intersections or skipped intersections are active for triangle and AABB geometry.
