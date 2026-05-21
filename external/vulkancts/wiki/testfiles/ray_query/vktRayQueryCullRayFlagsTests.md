# vktRayQueryCullRayFlagsTests

This file registers `ray_query.ray_flags` tests for ray-query flag behavior, including opacity, terminate-on-first-hit, face culling, and geometry skipping [vktRayQueryCullRayFlagsTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryCullRayFlagsTests.cpp#L2112-L2256).

## Source Files

| Role | Link |
|------|------|
| Implementation and registration | [vktRayQueryCullRayFlagsTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryCullRayFlagsTests.cpp#L2112-L2256) |

## Registration Hierarchy

```text
ray_query.ray_flags
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

### vertex_shader — Vertex-stage ray flags

Registered as a graphics source and crossed with the ray-flag test groups in [vktRayQueryCullRayFlagsTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryCullRayFlagsTests.cpp#L2117-L2171).

### tess_control_shader — Tessellation-control ray flags

Registered with the tessellation-control source and subject to tessellation feature checks [vktRayQueryCullRayFlagsTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryCullRayFlagsTests.cpp#L2123-L2125) and [vktRayQueryCullRayFlagsTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryCullRayFlagsTests.cpp#L1260-L1265).

### tess_evaluation_shader — Tessellation-evaluation ray flags

Registered with the tessellation-evaluation source [vktRayQueryCullRayFlagsTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryCullRayFlagsTests.cpp#L2123-L2125).

### geometry_shader — Geometry-stage ray flags

Registered with the geometry source and gated by geometry-shader support [vktRayQueryCullRayFlagsTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryCullRayFlagsTests.cpp#L2126-L2130) and [vktRayQueryCullRayFlagsTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryCullRayFlagsTests.cpp#L1267-L1268).

### fragment_shader — Fragment-stage ray flags

Registered with the fragment source [vktRayQueryCullRayFlagsTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryCullRayFlagsTests.cpp#L2131-L2135).

### compute_shader — Compute-stage ray flags

Registered with the compute source [vktRayQueryCullRayFlagsTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryCullRayFlagsTests.cpp#L2136-L2140).

### rgen_shader — Ray-generation ray flags

Ray-tracing pipeline source requiring `VK_KHR_ray_tracing_pipeline` when selected [vktRayQueryCullRayFlagsTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryCullRayFlagsTests.cpp#L2141-L2170) and [vktRayQueryCullRayFlagsTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryCullRayFlagsTests.cpp#L1282-L1288).

### isect_shader — Intersection-shader ray flags

Registered as an intersection shader source [vktRayQueryCullRayFlagsTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryCullRayFlagsTests.cpp#L2146-L2150).

### ahit_shader — Any-hit ray flags

Registered as an any-hit shader source [vktRayQueryCullRayFlagsTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryCullRayFlagsTests.cpp#L2151-L2155).

### chit_shader — Closest-hit ray flags

Registered as a closest-hit shader source [vktRayQueryCullRayFlagsTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryCullRayFlagsTests.cpp#L2156-L2160).

### miss_shader — Miss-shader ray flags

Registered as a miss shader source [vktRayQueryCullRayFlagsTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryCullRayFlagsTests.cpp#L2161-L2165).

### call_shader — Callable-shader ray flags

Registered as a callable shader source [vktRayQueryCullRayFlagsTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryCullRayFlagsTests.cpp#L2166-L2170).

## Parameter Dimensions

The file crosses shader source, four flag families (`opacity`, `terminate_on_first_hit`, `face_culling`, `skip_geometry`), triangle/AABB bottom geometry where nonempty flag lists exist, and concrete ray flag values [vktRayQueryCullRayFlagsTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryCullRayFlagsTests.cpp#L2173-L2245).

## Support Requirements

Cases require acceleration-structure and ray-query functionality and feature bits [vktRayQueryCullRayFlagsTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryCullRayFlagsTests.cpp#L1245-L1258), with stage-specific tessellation, geometry, vertex-pipeline-store, and ray-tracing-pipeline gates [vktRayQueryCullRayFlagsTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryCullRayFlagsTests.cpp#L1260-L1288).

## Verification Methods

The verifier derives expected hit results for four square regions and compares the result image with `tcu::intThresholdCompare` [vktRayQueryCullRayFlagsTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryCullRayFlagsTests.cpp#L679-L747). The instance maps comparison failure to test failure [vktRayQueryCullRayFlagsTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryCullRayFlagsTests.cpp#L2102-L2108).

## Test Principles

The cases encode opaque/non-opaque and front/back-facing regions so that each ray flag has a visible expected hit or miss pattern.
