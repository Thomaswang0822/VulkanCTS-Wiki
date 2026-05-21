# vktRayQueryProceduralGeometryTests

This file registers `ray_query.procedural_geometry`, a small family for ray queries against complex AABB/procedural geometry arrangements [vktRayQueryProceduralGeometryTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryProceduralGeometryTests.cpp#L495-L503).

## Source Files

| Role | Link |
|------|------|
| Implementation and registration | [vktRayQueryProceduralGeometryTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryProceduralGeometryTests.cpp#L495-L503) |

## Registration Hierarchy

```text
ray_query.procedural_geometry
├── object_behind_bounding_boxes
└── triangle_in_between
```

## Test Families

### object_behind_bounding_boxes — Object behind bounding boxes

Registered directly with `TestType::OBJECT_BEHIND_BOUNDING_BOX` [vktRayQueryProceduralGeometryTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryProceduralGeometryTests.cpp#L500-L501).

### triangle_in_between — Triangle placed between procedural geometry

Registered directly with `TestType::TRIANGLE_IN_BETWEEN` [vktRayQueryProceduralGeometryTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryProceduralGeometryTests.cpp#L502-L503).

## Parameter Dimensions

The visible registration dimension is the two explicit `TestType` cases above.

## Support Requirements

The cases require `VK_KHR_acceleration_structure`, `VK_KHR_ray_query`, and the ray-query feature bit [vktRayQueryProceduralGeometryTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryProceduralGeometryTests.cpp#L398-L403).

## Verification Methods

The test verifies the result buffer against a reference buffer and returns pass only when the comparison succeeds [vktRayQueryProceduralGeometryTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryProceduralGeometryTests.cpp#L209-L227).

## Test Principles

The family uses deliberately arranged procedural geometry to confirm the ray query reports the intended visible hit.
