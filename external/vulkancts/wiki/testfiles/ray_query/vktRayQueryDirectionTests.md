# vktRayQueryDirectionTests

Direction vector length and rays starting inside AABBs. The registered hierarchy comes from `createDirectionLengthTests()` and `createInsideAABBsTests()` in [vktRayQueryDirectionTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryDirectionTests.cpp#L546-L681).

## Source Files

| Role | Link |
|------|------|
| Implementation and registration | [vktRayQueryDirectionTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryDirectionTests.cpp) |

## Registration Hierarchy

```text
ray_query
├── direction_length
└── inside_aabbs
```

## Test Families

### direction_length — Registered child

This direct child is listed in the registration hierarchy and is covered by the parameter evidence below.

### inside_aabbs — Registered child

This direct child is listed in the registration hierarchy and is covered by the parameter evidence below.

## Parameter Dimensions

The file registers `direction_length` for triangle/AABB geometry with generated scaling and rotation factors, and `inside_aabbs` for four ray-end positions with generated scaling and rotation factors [vktRayQueryDirectionTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryDirectionTests.cpp#L546-L681).

## Support / Feature Requirements

Cases require acceleration-structure and ray-query functionality [vktRayQueryDirectionTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryDirectionTests.cpp#L258-L262).

## Verification Methods

The instance reads a float result distance and compares it with the expected distance or zero, failing on mismatches [vktRayQueryDirectionTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryDirectionTests.cpp#L476-L503).

## Test Principles

The file varies the registered dimensions while comparing shader-produced ray-query results against explicit CPU-side references or expected scalar/vector values.
