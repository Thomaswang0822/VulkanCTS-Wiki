# vktRayQueryAccelerationStructuresTests

This file registers `ray_query.acceleration_structures` tests covering AS build flags, vertex/index formats, copy/compaction/serialization operations, host-threaded operations, function arguments, instance culling/update, dynamic indexing, and empty structures. The top-level children are added in [vktRayQueryAccelerationStructuresTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L4744-L4768).

## Source Files

| Role | Link |
|------|------|
| Implementation and registration | [vktRayQueryAccelerationStructuresTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L4744-L4768) |

## Registration Hierarchy

```text
ray_query.acceleration_structures
├── flags
├── format
├── operations
├── host_threading
├── function_argument
├── instance_triangle_culling
├── instance_update
├── dynamic_indexing
└── empty
```

## Test Families

### flags — Build flags and geometry/instance combinations

`flags` is registered by `addBasicBuildingTests` and combines traditional/sparse residency, fragment/compute/closest-hit sources, CPU/GPU build, triangle/AABB bottoms, identical/different instance tops, padding, optimization/update/compaction/low-memory flags, generic creation variants, and selected device-address-command variants [vktRayQueryAccelerationStructuresTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L3522-L3773).

### format — Vertex and index formats

`format` crosses residency, shader source, CPU/GPU build, 15 listed vertex formats, padding, and three index formats [vktRayQueryAccelerationStructuresTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L3776-L3972).

### operations — Copy, compaction, serialization, and related operations

`operations` is registered by [vktRayQueryAccelerationStructuresTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L4753-L4755) and populated by `addOperationTestsImpl` through operation-type and operation-target groups visible in [vktRayQueryAccelerationStructuresTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L4087-L4168).

### host_threading — Host-threaded operations

`host_threading` wraps operation tests under thread-count groups `1`, `2`, `3`, `4`, `8`, and `max` [vktRayQueryAccelerationStructuresTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L4176-L4190).

### function_argument — AS as function arguments

`function_argument` uses acceleration structures as function arguments, crossing residency and CPU/GPU build types [vktRayQueryAccelerationStructuresTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L4193-L4263).

### instance_triangle_culling — Instance triangle culling combinations

Registered by [vktRayQueryAccelerationStructuresTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L4759-L4760); inspected groups include residency, shader source, build type, and index format [vktRayQueryAccelerationStructuresTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L4382-L4447).

### instance_update — Instance-index update variants

Registered by [vktRayQueryAccelerationStructuresTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L4761-L4762); inspected groups cross residency, build type, and operation type [vktRayQueryAccelerationStructuresTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L4489-L4537).

### dynamic_indexing — Dynamic indexing of acceleration structures

`dynamic_indexing` creates one `dynamic_indexing` leaf under each residency group [vktRayQueryAccelerationStructuresTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L4540-L4569).

### empty — Empty acceleration structures

`empty` crosses residency, shader source, build type, index type, and five empty-structure cases (`inactive_triangles`, `inactive_instances`, `no_geometries_bottom`, `no_primitives_top`, `no_primitives_bottom`) [vktRayQueryAccelerationStructuresTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L4572-L4741).

## Parameter Dimensions

Important dimensions include resource residency, shader source/pipeline, host/device build type, geometry type, top-level instance pattern, padding, build flags, vertex/index formats, operation type/target, host thread count, and empty-structure mode; these dimensions are visible in the family builders cited above.

## Support Requirements

Common support requires ray-query and acceleration-structure functionality; selected device-address-command variants require `VK_KHR_device_address_commands` [vktRayQueryAccelerationStructuresTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L1605-L1612). Stage-specific tessellation, geometry, ray-tracing-pipeline, and vertex-pipeline-store gates are checked in [vktRayQueryAccelerationStructuresTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L1613-L1645). Host-built cases require `accelerationStructureHostCommands`, vertex formats are checked for AS vertex-buffer support, and sparse-residency cases require `sparseBinding` [vktRayQueryAccelerationStructuresTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L1648-L1665).

## Verification Methods

Graphics, compute, and ray-tracing configurations build reference images and compare result buffers with `tcu::intThresholdCompare` [vktRayQueryAccelerationStructuresTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L871-L900) and [vktRayQueryAccelerationStructuresTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L1149-L1181). Function-argument checks count failures in result buffers and return fail when any are found [vktRayQueryAccelerationStructuresTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L3502-L3516).

## Test Principles

The file stresses that ray queries observe equivalent hit/miss behavior across many valid acceleration-structure creation, update, copy, and representation choices.
