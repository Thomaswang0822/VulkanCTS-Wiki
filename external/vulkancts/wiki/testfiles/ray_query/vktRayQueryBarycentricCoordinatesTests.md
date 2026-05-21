# vktRayQueryBarycentricCoordinatesTests

Barycentric-coordinate reporting. The registered hierarchy comes from `createBarycentricCoordinatesTests()` in [vktRayQueryBarycentricCoordinatesTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryBarycentricCoordinatesTests.cpp#L381-L390).

## Source Files

| Role | Link |
|------|------|
| Implementation and registration | [vktRayQueryBarycentricCoordinatesTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryBarycentricCoordinatesTests.cpp) |

## Registration Hierarchy

```text
ray_query.barycentric_coordinates
└── compute
```

## Test Families

### compute — Registered child

This direct child is listed in the registration hierarchy and is covered by the parameter evidence below.

## Parameter Dimensions

The single `compute` case is registered with a deterministic seed [vktRayQueryBarycentricCoordinatesTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryBarycentricCoordinatesTests.cpp#L381-L390).

## Support Requirements

The case requires acceleration-structure and ray-query functionality [vktRayQueryBarycentricCoordinatesTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryBarycentricCoordinatesTests.cpp#L102-L106).

## Verification Methods

The test builds expected barycentric coordinates, reads the output buffer, and fails if any component differs beyond the threshold [vktRayQueryBarycentricCoordinatesTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryBarycentricCoordinatesTests.cpp#L353-L377).

## Test Principles

The file varies the registered dimensions while comparing shader-produced ray-query results against explicit CPU-side references or expected scalar/vector values.
