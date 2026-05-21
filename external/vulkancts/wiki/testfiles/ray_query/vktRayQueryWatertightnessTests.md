# vktRayQueryWatertightnessTests

This file registers `ray_query.watertightness` tests that check no-miss and single-hit behavior across shader stages and geometry types [vktRayQueryWatertightnessTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryWatertightnessTests.cpp#L2251-L2344).

## Source Files

| Role | Link |
|------|------|
| Implementation and registration | [vktRayQueryWatertightnessTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryWatertightnessTests.cpp#L2251-L2344) |

## Registration Hierarchy

```text
ray_query.watertightness
├── nomiss
└── singlehit
```

## Test Families

### nomiss — No ray should miss

The `nomiss` test type is registered first and is crossed with shader stages and `triangles`/`aabbs` geometry [vktRayQueryWatertightnessTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryWatertightnessTests.cpp#L2275-L2290).

### singlehit — Exactly one hit

The `singlehit` test type is registered second; AABB geometry is skipped for this family [vktRayQueryWatertightnessTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryWatertightnessTests.cpp#L2279-L2282) and [vktRayQueryWatertightnessTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryWatertightnessTests.cpp#L2333-L2334).

## Parameter Dimensions

The matrix includes two test types, twelve shader-stage names (`vert` through `call`), and triangle/AABB geometry, with the single-hit AABB skip noted above [vktRayQueryWatertightnessTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryWatertightnessTests.cpp#L2257-L2290).

## Support Requirements

Cases require acceleration-structure and ray-query functionality and delegate stage-specific support to pipeline check functions [vktRayQueryWatertightnessTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryWatertightnessTests.cpp#L2154-L2169) and [vktRayQueryWatertightnessTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryWatertightnessTests.cpp#L2182-L2203).

## Verification Methods

`nomiss` fails if any result value is non-positive, while `singlehit` expects every result value to equal one [vktRayQueryWatertightnessTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryWatertightnessTests.cpp#L1876-L1888) and [vktRayQueryWatertightnessTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryWatertightnessTests.cpp#L1928-L1944). The instance returns pass/fail from that verifier [vktRayQueryWatertightnessTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryWatertightnessTests.cpp#L2123-L2128).

## Test Principles

The tests use repeated ray-query outcomes to catch cracks or duplicate hits in edge-sensitive geometry traversal.
