## Overview

**Core question:** Do `VK_KHR_acceleration_structure` builds, copies, compaction, serialization, updates, queries, host threading, instance culling, cull masks, dynamic indexing, and empty-structure handling all produce a top-level acceleration structure that ray tracing shaders traverse identically to a freshly built reference, across a large matrix of build flags, vertex and index formats, build types, and resource residency modes?

- [vktRayTracingAccelerationStructuresTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp) implements the `acceleration_structures` test family under the `ray_tracing_pipeline` test category.
- The file registers 17 direct children under `acceleration_structures`, each exercising a distinct acceleration-structure property: build flag combinations, vertex and index formats, copy and compact and serialize operations, host deferred-operation threading, SPIR-V function-argument calling conventions, instance triangle culling, cull masks, descriptor indexing, empty structures, instance custom indices, TLAS updates, device compatibility UUIDs, header bottom-level addresses, query pool results, pipeline-stage copies, BLAS updates, and complex realistic geometry.
- Most subgroups build a TLAS over a BLAS set, trace a ray per launch id into a 2D result image, and verify the image against an expected pattern. Three subgroups (`device_compability_khr`, `header_bottom_address`, `query_pool_results`) skip shader dispatch and validate host-side query or header data directly.
- The reader should expect the page to explain each subgroup's mechanism, the representative rgen shader shared by most subgroups, the per-subgroup validation path, and the failure each subgroup points to.

## Background Knowledge

- **TLAS and BLAS.** A ray tracing pipeline traverses a top-level acceleration structure (TLAS) that references one or more bottom-level acceleration structures (BLAS). Each BLAS holds geometry (triangles or AABBs). Each TLAS instance references a BLAS, applies a 3x4 transform, and carries an `instanceCustomIndex`, a `mask`, an `instanceShaderBindingTableRecordOffset`, and `VkGeometryInstanceFlagsKHR`.
- **Build types and resource residency.** `VkAccelerationStructureBuildTypeKHR` selects host (`VK_ACCELERATION_STRUCTURE_BUILD_TYPE_HOST_KHR`, requires `accelerationStructureHostCommands`) or device (`vkCmdBuildAccelerationStructuresKHR`) builds. The `ResourceResidency` dimension switches between `TRADITIONAL` device-local buffers and `SPARSE_BINDING` buffers backed by a sparse queue. Sparse binding is only legal for device builds; the registration prunes host+sparse combinations.
- **Build flags.** `VkBuildAccelerationStructureFlagsKHR` controls `PREFER_FAST_TRACE`, `PREFER_FAST_BUILD`, `LOW_MEMORY`, `ALLOW_UPDATE`, and `ALLOW_COMPACTION`. `ALLOW_UPDATE` is required for any in-place refit. `ALLOW_COMPACTION` must be set before `vkCmdWriteAccelerationStructuresPropertiesKHR` can report the compacted size.
- **Copy, compact, serialize.** `vkCmdCopyAccelerationStructureKHR` performs a byte-for-byte copy. `vkCmdCopyAccelerationStructureToMemoryKHR` and the inverse serialize and deserialize a structure with a header carrying compatibility UUIDs. Compaction produces a smaller equivalent structure and requires `ALLOW_COMPACTION` on the source.
- **Host deferred operations.** `vkBuildAccelerationStructuresKHR`, `vkCopyAccelerationStructureKHR`, `vkCopyAndCompactAccelerationStructureKHR`, `vkSerializeAccelerationStructureKHR`, and `vkDeserializeAccelerationStructureKHR` accept a `VkDeferredOperationKHR`. The application partitions work across host threads by calling `vkDeferredOperationJoinKHR` from each thread.
- **Instance culling, cull mask, instance custom index.** `VkGeometryInstanceFlagsKHR` carries triangle facing and cull-disable bits. The ray's `cullMask` is AND-ed with the instance's `mask`; only instances whose mask AND cullMask is nonzero are visited. `gl_InstanceCustomIndexEXT` reads the per-instance custom index, and `gl_CullMaskEXT` (from `VK_KHR_ray_tracing_maintenance1`) reads the active cullMask bits.
- **Empty acceleration structures.** The spec allows a BLAS with no geometries, a BLAS or TLAS with zero primitives, inactive triangles (NaN vertices producing no intersection), and inactive instances. A correct implementation traces these as if no geometry exists.
- **Query pools and pipeline stage barriers.** `VK_QUERY_TYPE_ACCELERATION_STRUCTURE_COMPACTED_SIZE_KHR`, `SERIALIZATION_SIZE_KHR`, and `SERIALIZATION_BOTTOM_LEVEL_POINTERS_KHR` return per-handle sizes and counts. `VK_KHR_ray_tracing_maintenance1` introduces `VK_PIPELINE_STAGE_2_ACCELERATION_STRUCTURE_COPY_BIT_KHR` and `VK_ACCESS_2_SHADER_BINDING_TABLE_READ_BIT_KHR` to sequence AS copies and SBT reads against ray tracing dispatch.

## Registration Hierarchy

```text
ray_tracing_pipeline.acceleration_structures
├── complex_geometry
├── copy_within_pipeline
├── device_compability_khr
├── dynamic_indexing
├── empty
├── flags
├── format
├── function_argument
├── header_bottom_address
├── host_threading
├── instance_index
├── instance_triangle_culling
├── instance_update
├── operations
├── query_pool_results
├── ray_cull_mask
└── update
```

The 17 direct children are created in [createAccelerationStructuresTests](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L7738-L7776). Each child expands into a multi-axis matrix of test case leaves through dedicated registration helpers (`addBasicBuildingTests`, `addOperationTestsImpl`, `addEmptyAccelerationStructureTests`, `addQueryPoolResultsTests`, `addComplexGeometryTests`, and others). The leaves vary build type, build flags, vertex and index formats, operation type and target, thread count, geometry type, and resource residency; they are too numerous to list in the tree and are documented in `## Parameter Dimensions and Observed Values` and `## Behavior Parameters`.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Subgroup (primary axis) | `flags`, `format`, `operations`, `host_threading`, `function_argument`, `instance_triangle_culling`, `ray_cull_mask`, `dynamic_indexing`, `empty`, `instance_index`, `instance_update`, `device_compability_khr`, `header_bottom_address`, `query_pool_results`, `copy_within_pipeline`, `update`, `complex_geometry` | Selects which AS property is exercised. Each subgroup changes what is being tested. | [createAccelerationStructuresTests](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L7738-L7776) |
| Build type | `gpu_built`, `cpu_built` | `VK_ACCELERATION_STRUCTURE_BUILD_TYPE_DEVICE_KHR` or `_HOST_KHR`. Host builds require `accelerationStructureHostCommands`. | [TestParams](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L183-L214) |
| Resource residency | `traditional_structures`, `sparse_binding_structures` | `TRADITIONAL` device-local buffers or `SPARSE_BINDING` buffers backed by a sparse queue. Sparse is device-only. | [addBasicBuildingTests](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L6058-L6279) |
| Bottom geometry type | `triangles`, `aabbs` | `BTT_TRIANGLES` (fixed-function hit) or `BTT_AABBS` (intersection shader hit). | [TestParams](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L183-L214) |
| Top test type | `identical_instances`, `different_instances` | `TTT_IDENTICAL_INSTANCES` (all instances share one BLAS) or `TTT_DIFFERENT_INSTANCES` (each instance has its own BLAS). | [TestParams](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L183-L214) |
| Build flags | `fasttrace_0_0_0`, `fastbuild_0_0_0`, `lowmemory_0_0_0`, `0_allowupdate_0_0`, `0_allowcompaction_0_0`, and combinations | Encodes `PREFER_FAST_TRACE`, `PREFER_FAST_BUILD`, `LOW_MEMORY`, `ALLOW_UPDATE`, `ALLOW_COMPACTION` as a 5-tuple suffix. | [addBasicBuildingTests](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L6058-L6279) |
| Padding | `nopadding`, `padding` | Whether vertex data is tightly packed or padded to `minAlign` boundaries. | [addBasicBuildingTests](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L6058-L6279) |
| Operation type | `OP_NONE`, `OP_COPY`, `OP_COMPACT`, `OP_SERIALIZE` | Selects copy, compaction, serialize-then-deserialize, or no post-build operation. | [addOperationTestsImpl](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L6413-L6544) |
| Operation target | `top_acceleration_structure`, `bottom_acceleration_structure` | Which AS level receives the copy, compact, or serialize operation. | [addOperationTestsImpl](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L6413-L6544) |
| Worker thread count | `1`, `2`, `3`, `4`, `8`, `max` | Number of host threads calling `vkDeferredOperationJoinKHR` for `host_threading`. | [addOperationTestsImpl](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L6413-L6544) |
| Vertex format | `VK_FORMAT_R32G32B32_SFLOAT`, `VK_FORMAT_R32G32B32A32_SFLOAT`, `VK_FORMAT_R16G16B16_SFLOAT`, `VK_FORMAT_R16G16B16_SNORM`, `VK_FORMAT_R16G16_SNORM`, and others | Varies the vertex data format for BLAS builds in `format`. | [format loop](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L6293-L6411) |
| Index format | `noflags`/`none`, `uint16`, `uint32` | Varies the index buffer format for BLAS builds in `format`. | [format loop](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L6293-L6411) |
| Empty AS case | `NO_GEOMETRIES`, `NO_PRIMITIVES`, `INACTIVE_TRIANGLES`, `INACTIVE_INSTANCES` | Selects the empty-structure shape for the `empty` subgroup. | [addEmptyAccelerationStructureTests](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L6785-L6891) |
| Complex geometry model | `ICOSPHERE`, `TERRAIN`, `TORUSKNOT`, `TRIANGLESOUP` | Selects the realistic geometry model for `complex_geometry`, each with a distinct expected hit rate. | [addComplexGeometryTests](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L7616-L7736) |
| Index type (complex) | `none`, `uint16`, `uint32` | Index buffer format for the complex geometry models. | [addComplexGeometryTests](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L7616-L7736) |

## Behavior Parameters

The primary behavioral axis is the direct child (subgroup) name under `acceleration_structures`. Each value changes what is being tested about acceleration structures. The remaining dimensions configure how hard each subgroup's mechanism is stressed.

### flags — Build flag combinations and resource residency

Exercises every combination of `PREFER_FAST_TRACE`, `PREFER_FAST_BUILD`, `LOW_MEMORY`, `ALLOW_UPDATE`, and `ALLOW_COMPACTION` across `gpu_built`/`cpu_built` and `traditional_structures`/`sparse_binding_structures` residency. The `CheckerboardConfiguration` verifies the hit/miss pattern. A rotating `de::ModCounter32` selects `bottomUnboundedCreation` and `topUnboundedCreation` on a subset of cases to exercise unbounded-buffer creation without exploding the case count. Evidence: [addBasicBuildingTests](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L6058-L6279).

### format — Vertex and index format handling

Varies vertex format (`R32G32B32_SFLOAT`, `R32G32B32A32_SFLOAT`, `R16G16B16_SFLOAT`, `R16G16B16_SNORM`, and others), index format (`uint16`, `uint32`), and `padding`/`nopadding` for a single triangle BLAS. The `SingleTriangleConfiguration` compares the ray-traced depth image against a host-rasterized reference using `tcu::floatThresholdCompare` with a 0.01 tolerance. Evidence: [format loop](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L6293-L6411).

### operations — Copy, compaction, and serialization

Applies `OP_COPY`, `OP_COMPACT`, or `OP_SERIALIZE` to the top or bottom AS after building, then traces the same ray pattern through the resulting structure. The test confirms that the derived structure traverses identically to the freshly built source. `OP_COMPACT` requires `ALLOW_COMPACTION` on the source and queries the compacted size first. Evidence: [addOperationTestsImpl](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L6413-L6544).

### host_threading — Deferred host operation threading

Exercises `vkBuildAccelerationStructuresKHR`, `vkCopyAccelerationStructureKHR`, `vkCopyAndCompactAccelerationStructureKHR`, and `vkSerializeAccelerationStructureKHR` through `VkDeferredOperationKHR` with 1, 2, 3, 4, 8, and `max` worker threads calling `vkDeferredOperationJoinKHR`. Each case runs twice: once single-threaded and once with the requested thread count, and both must pass. The test does not thread compaction as a deferred host operation, so `host_threading` only covers `OP_COPY` and `OP_SERIALIZE`. Evidence: [addOperationTestsImpl](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L6413-L6544).

### function_argument — SPIR-V calling convention for traceRayEXT

Uses hand-written SPIR-V assembly rgen shaders that wrap `OpTraceRayKHR` in two function-call layers: one taking a bare `OpTypeAccelerationStructureKHR` value and one taking a pointer. The test verifies that the implementation accepts both calling conventions. Registered with `SingleTriangleConfiguration` under `cpu_built` and `gpu_built` for both residency modes. Evidence: [RayTracingASFuncArgTestCase::initPrograms](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L2105-L2460).

### instance_triangle_culling — Instance triangle facing and cull flags

Varies `VkGeometryInstanceFlagsKHR` (`VK_GEOMETRY_INSTANCE_TRIANGLE_FACING_CULL_DISABLE_BIT_KHR`, `VK_GEOMETRY_INSTANCE_TRIANGLE_FRONT_COUNTERCLOCKWISE_BIT_KHR`) combined with `gl_RayFlagsCullBackFacingTrianglesEXT` in the rgen shader. The `CheckerboardConfiguration` verifies that the hit/miss pattern matches the expected culling behavior for each flag combination. Evidence: [addInstanceTriangleCullingTests](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L6640-L6757).

### ray_cull_mask — Cull mask filtering and gl_CullMaskEXT

Sets a per-instance `mask` and a per-ray `cullMask` so that only some instances are visited. The chit shader writes `cullMask & 0xFF` on hits and the miss shader writes `bitfieldReverse(cullMask & 0xFF)` on misses. Requires `VK_KHR_ray_tracing_maintenance1` for `gl_CullMaskEXT`. Evidence: [addInstanceRayCullMaskTests](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L7075-L7185).

### dynamic_indexing — Non-uniform TLAS descriptor indexing

Uses a hand-written SPIR-V rgen with a 500-element TLAS descriptor array and an SSBO of TLAS device addresses. The shader traces through both paths: non-uniform descriptor indexing of the array, and `OpConvertUToAccelerationStructureKHR` from an SSBO-loaded address. Results are accumulated with `atomicAdd` using prime offsets (2, 3, 5, 7) to verify each path was taken. Requires `VK_EXT_descriptor_indexing`. Evidence: [RayTracingASDynamicIndexingTestCase::initPrograms](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L3035-L3274).

### empty — Empty acceleration structure shapes

Verifies four empty-structure shapes: `NO_GEOMETRIES` (BLAS with `geometryCount = 0`), `NO_PRIMITIVES` (BLAS or TLAS with `primitiveCount = 0`), `INACTIVE_TRIANGLES` (NaN vertices producing no intersection, triangles only), and `INACTIVE_INSTANCES`. The test confirms the implementation traces these as if no geometry exists, using `CheckerboardConfiguration` and `SingleTriangleConfiguration`. Evidence: [addEmptyAccelerationStructureTests](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L6785-L6891).

### instance_index — Instance custom index reporting

Verifies that `gl_InstanceCustomIndexEXT` reports `INSTANCE_CUSTOM_INDEX_BASE + x + y` in the selected stage (rgen, chit, ahit, or isect). The constant `INSTANCE_CUSTOM_INDEX_BASE = 0x807f00u` is chosen so the most significant bit set in 24 bits catches implementations that sign-extend the instance custom index. Evidence: [addInstanceIndexTests](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L6892-L6986).

### instance_update — TLAS update operations

Exercises `OP_UPDATE`, `OP_UPDATE_IN_PLACE`, and `OP_UPDATE_UNINITIALIZED` against a source TLAS. The test rebuilds the TLAS with updated instance data and confirms the traversal matches a fresh rebuild. Uses `UpdateableASConfiguration` with `tcu::floatThresholdCompare` validation. Evidence: [addInstanceUpdateTests](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L6987-L7073).

### device_compability_khr — Device compatibility UUID check

Verifies that `vkGetDeviceAccelerationStructureCompatibilityKHR` returns `VK_ACCELERATION_STRUCTURE_COMPATIBILITY_COMPATIBLE_KHR` when comparing the device's own UUIDs against a serialized header. No shader dispatch happens; the test validates the UUID and version-info header directly. Evidence: [RayTracingDeviceASCompabilityKHRTestInstance::iterate](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L3692-L3976).

### header_bottom_address — Serialized TLAS header pointer verification

Verifies that a TLAS built with mixed identical/different instances has a serialized header with the correct bottom-level pointer count, and that the bottom-level device addresses are stable across rebuilds. No shader dispatch; the test inspects the serialized header directly. Evidence: [RayTracingHeaderBottomAddressTestInstance::iterate](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L3978-L4112).

### query_pool_results — Query pool size and pointer validation

Verifies that `vkGetQueryPoolResults` for `ACCELERATION_STRUCTURE_COMPACTED_SIZE_KHR`, `ACCELERATION_STRUCTURE_SERIALIZATION_SIZE_KHR`, and `ACCELERATION_STRUCTURE_SERIALIZATION_BOTTOM_LEVEL_POINTERS_KHR` returns values consistent with `VkAccelerationStructureBuildSizesInfoKHR` and the actual serialization output. The `availability_bit` variant also checks that availability bits are nonzero. No shader dispatch. Evidence: [addQueryPoolResultsTests](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L7363-L7449).

### copy_within_pipeline — Pipeline-stage AS copy synchronization

Traces the same scene twice: once with the original BLAS and once with a BLAS copied using `VK_PIPELINE_STAGE_2_ACCELERATION_STRUCTURE_COPY_BIT_KHR`, with SBT reads sequenced through `VK_ACCESS_2_SHADER_BINDING_TABLE_READ_BIT_KHR`. The test compares the two result images for exact equality. Requires `VK_KHR_ray_tracing_maintenance1` and `VK_KHR_synchronization2`. Evidence: [CopyBlasInstance::iterate](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L5270-L5688).

### update — BLAS in-place refit

Updates a BLAS in place by replacing vertices, indices, transform, geometry transform, or by making a triangle degenerate. The test retraces after the update and confirms the result matches a fresh rebuild. An optional compaction-after-update path verifies that compaction does not corrupt the updated structure. Host-built `GEOMETRY_TRANSFORM` cases are pruned because that path is device-only. Evidence: [ASUpdateInstance::iterate](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L5729-L6057).

### complex_geometry — Realistic geometry at scale

Traces rays into realistic geometry models (icosphere, terrain, torusknot, trianglesoup) across 3 index types and 4 build flags. The `ComplexGeometryConfiguration` checks the hit percentage against a per-model expected rate (63% for icosphere, 36% for terrain, 45% for torusknot, 31% for trianglesoup) with a 0.5% tolerance, and verifies that reported primitive indices stay within the model triangle count. Validation is statistical, not per-pixel exact. Evidence: [addComplexGeometryTests](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L7616-L7736).

## Shader Analysis

This page uses one representative walkthrough. Most subgroups (`flags`, `format`, `operations`, `host_threading`, `instance_triangle_culling`, `ray_cull_mask`, `empty`, `instance_index`, `instance_update`, `update`, `copy_within_pipeline`, `complex_geometry`) share the same `RayTracingASBasicTestCase::initPrograms` shader generator, which emits rgen, chit, ahit, miss, and isect shaders driven by the `instanceCustomIndexCase`, `cullFlags`, `cullMask`, and `useCullMask` parameters. The `function_argument` and `dynamic_indexing` subgroups use hand-written SPIR-V assembly rgen shaders that exercise distinct SPIR-V calling-convention and descriptor-indexing mechanisms; they are summarized in their `## Behavior Parameters` subsections rather than given separate walkthroughs, because the basic rgen already covers the shared trace-and-store pattern. The chit and miss shaders are tiny constant writers (`ivec4(2,0,0,1)` for chit, `ivec4(1,0,0,1)` for miss), so they are summarized in the walkthrough body rather than given separate SPIR-V blocks.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
ray_tracing_pipeline.acceleration_structures.flags.traditional_structures.gpu_built.triangles.identical_instances.nopadding.fasttrace_0_0_0
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `flags` | Tests build flag combinations; this leaf uses `PREFER_FAST_TRACE` only. |
| `traditional_structures` | Device-local buffers, no sparse binding. |
| `gpu_built` | `vkCmdBuildAccelerationStructuresKHR` on a queue. |
| `triangles` | Triangle BLAS geometry (fixed-function hit, no intersection shader). |
| `identical_instances` | All TLAS instances share one BLAS. |
| `nopadding` | Vertex data is tightly packed. |
| `fasttrace_0_0_0` | `PREFER_FAST_TRACE` set; no `PREFER_FAST_BUILD`, `LOW_MEMORY`, or `ALLOW_UPDATE`/`ALLOW_COMPACTION`. |
| `instanceCustomIndexCase = NONE` | rgen stores the payload; chit writes `ivec4(2,0,0,1)`, miss writes `ivec4(1,0,0,1)`. |
| `cullFlags = NONE` | rgen passes `0` as ray flags. |
| `cullMask = 0xFFu` | rgen passes `0xFFu`; all instances are visited. |

#### Purpose

This rgen shader drives one ray per launch id of the 8x8 dispatch. Each ray traces straight down the negative Z axis into the checkerboard TLAS. The chit shader writes `2` into the payload on a hit; the miss shader writes `1`. The rgen stores the payload into a 2D `r32i` storage image at `gl_LaunchIDEXT.xy`. The host verifies a checkerboard pattern: positions where `(x + y) % 2 == 1` must report `2` (hit, because the BLAS at that cell exists) and positions where `(x + y) % 2 == 0` must report `1` (miss, because no BLAS was placed there).

#### Structural Design

| Step | rgen behavior | Meaning |
|------|---------------|---------|
| 1 | Read `gl_LaunchIDEXT.xy` and convert to a pixel-center origin `(x + 0.5, y + 0.5, 0.5)`. | Each of the 8x8 launch invocations traces one ray into the checkerboard AS. |
| 2 | Zero-initialize `hitValue` to `ivec4(0,0,0,0)`. | Ensures the payload has a known value before `traceRayEXT`. The chit or miss shader overwrites it. |
| 3 | Call `traceRayEXT(topLevelAS, 0, 0xFFu, 0, 0, 0, origin, tmin, direction, tmax, 0)`. | Traces a ray down the negative Z axis. Ray flags are `0` (no culling). CullMask is `0xFFu` (visit all instances). SBT offset, stride, and miss index are all `0`. |
| 4 | `imageStore(result, ivec2(gl_LaunchIDEXT.xy), hitValue)`. | Writes the chit or miss payload into the result image at the launch id position. |

The host builds the checkerboard in `CheckerboardConfiguration::initBottomAccelerationStructures`: one BLAS per cell where `(x + y) % 2 == 1`, with all instances sharing that single BLAS (`TTT_IDENTICAL_INSTANCES`). The `0xFFu` cullMask and the `0` ray flags are literal because this is a `InstanceCullFlags::NONE`, non-cull-mask case. The same generator swaps the cullMask literal for the per-case value when `useCullMask` is true and swaps the ray-flags literal for `gl_RayFlagsCullBackFacingTrianglesEXT` when `cullFlags` is not `NONE`.

#### Shader Code

Reconstructed GLSL from the `initPrograms` literal [vktRayTracingAccelerationStructuresTests.cpp#L1899-L1927](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L1899-L1927):

```glsl
#version 460 core
#extension GL_EXT_ray_tracing : require
layout(location = 0) rayPayloadEXT ivec4 hitValue;
layout(r32i, set = 0, binding = 0) uniform iimage2D result;
layout(set = 0, binding = 1) uniform accelerationStructureEXT topLevelAS;

void main()
{
  float tmin      = 0.0;
  float tmax      = 1.0;
  vec3  origin    = vec3(float(gl_LaunchIDEXT.x) + 0.5f, float(gl_LaunchIDEXT.y) + 0.5f, 0.5);
  vec3  direction = vec3(0.0,0.0,-1.0);
  hitValue        = ivec4(0,0,0,0);
  traceRayEXT(topLevelAS, 0, 0xFFu, 0, 0, 0, origin, tmin, direction, tmax, 0);
  imageStore(result, ivec2(gl_LaunchIDEXT.xy), hitValue);
}
```

The chit shader writes `hitValue = ivec4(2,0,0,1)` and the miss shader writes `hitValue = ivec4(1,0,0,1)`. When `instanceCustomIndexCase` is not `NONE`, the rgen drops its `imageStore` and the selected stage (chit, ahit, or isect) writes `ivec4(gl_InstanceCustomIndexEXT, 0, 0, 1)` instead. When `useCullMask` is true, chit writes `ivec4(gl_CullMaskEXT, 0, 0, 1)` and miss writes `ivec4(bitfieldReverse(uint(gl_CullMaskEXT)), 0, 0, 1)`.

#### Additional Info

- The `rgen_depth` variant used by `format` and `empty` subgroups replaces the checkerboard ray with a `calculateOrigin` helper that spreads rays across a single triangle, uses `vec4`/`r32f` payload and image, and sets `tmax = 2.0`. The chit writes `gl_RayTmaxEXT` and miss writes `0.0`.
- The `complex_geometry` variant uses `rgba32ui` image and packs `(1, floatBitsToUint(gl_HitTEXT), gl_PrimitiveID, gl_GeometryIndexEXT)` into the texel.
- The `copy_within_pipeline` variant uses `vec4` payload with green for hit and red for miss.
- `vk::ShaderBuildOptions` targets `SPIRV_VERSION_1_4` for all generated shaders.

#### Parameter Variation Summary

| Parameter dimension | GLSL-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Build flags | No GLSL change. The host sets `VkBuildAccelerationStructureFlagsKHR` on the BLAS/TLAS builder. | [addBasicBuildingTests](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L6058-L6279) |
| Build type | No GLSL change. The host selects host or device build. | [TestParams](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L183-L214) |
| Resource residency | No GLSL change. The host allocates traditional or sparse-binding buffers. | [addBasicBuildingTests](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L6058-L6279) |
| Bottom geometry type | No GLSL change to rgen. AABB cases bind an `isect` intersection shader in the hit group. | [initPrograms](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L1866-L2092) |
| Instance custom index case | rgen drops its `imageStore`; the selected stage writes `gl_InstanceCustomIndexEXT` instead. | [initPrograms](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L1899-L1953) |
| Cull flags | rgen swaps `0` for `gl_RayFlagsCullBackFacingTrianglesEXT`. | [initPrograms](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L1917-L1919) |
| Cull mask | rgen swaps `0xFFu` for the per-case mask; chit/miss write `gl_CullMaskEXT` or `bitfieldReverse`. | [initPrograms](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L1893-L2034) |
| Operation type | No GLSL change. The host applies copy, compact, or serialize before tracing. | [addOperationTestsImpl](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L6413-L6544) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `rgen`
- Target SPIRV version: `spirv1.5`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.5
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 60
; Schema: 0
               OpCapability RayTracingKHR
               OpExtension "SPV_KHR_ray_tracing"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint RayGenerationKHR %main "main" %gl_LaunchIDEXT %hitValue %topLevelAS %result
               OpSource GLSL 460
               OpSourceExtension "GL_EXT_ray_tracing"
               OpName %main "main"
               OpName %tmin "tmin"
               OpName %tmax "tmax"
               OpName %origin "origin"
               OpName %gl_LaunchIDEXT "gl_LaunchIDEXT"
               OpName %direction "direction"
               OpName %hitValue "hitValue"
               OpName %topLevelAS "topLevelAS"
               OpName %result "result"
               OpDecorate %gl_LaunchIDEXT BuiltIn LaunchIdKHR
               OpDecorate %topLevelAS Binding 1
               OpDecorate %topLevelAS DescriptorSet 0
               OpDecorate %result Binding 0
               OpDecorate %result DescriptorSet 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
%_ptr_Function_float = OpTypePointer Function %float
    %float_0 = OpConstant %float 0
    %float_1 = OpConstant %float 1
    %v3float = OpTypeVector %float 3
%_ptr_Function_v3float = OpTypePointer Function %v3float
       %uint = OpTypeInt 32 0
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_LaunchIDEXT = OpVariable %_ptr_Input_v3uint Input
     %uint_0 = OpConstant %uint 0
%_ptr_Input_uint = OpTypePointer Input %uint
  %float_0_5 = OpConstant %float 0.5
     %uint_1 = OpConstant %uint 1
   %float_n1 = OpConstant %float -1
         %34 = OpConstantComposite %v3float %float_0 %float_0 %float_n1
        %int = OpTypeInt 32 1
      %v4int = OpTypeVector %int 4
%_ptr_RayPayloadKHR_v4int = OpTypePointer RayPayloadKHR %v4int
   %hitValue = OpVariable %_ptr_RayPayloadKHR_v4int RayPayloadKHR
      %int_0 = OpConstant %int 0
         %40 = OpConstantComposite %v4int %int_0 %int_0 %int_0 %int_0
         %41 = OpTypeAccelerationStructureKHR
%_ptr_UniformConstant_41 = OpTypePointer UniformConstant %41
 %topLevelAS = OpVariable %_ptr_UniformConstant_41 UniformConstant
   %uint_255 = OpConstant %uint 255
         %50 = OpTypeImage %int 2D 0 0 0 2 R32i
%_ptr_UniformConstant_50 = OpTypePointer UniformConstant %50
     %result = OpVariable %_ptr_UniformConstant_50 UniformConstant
     %v2uint = OpTypeVector %uint 2
      %v2int = OpTypeVector %int 2
       %main = OpFunction %void None %3
          %5 = OpLabel
       %tmin = OpVariable %_ptr_Function_float Function
       %tmax = OpVariable %_ptr_Function_float Function
     %origin = OpVariable %_ptr_Function_v3float Function
  %direction = OpVariable %_ptr_Function_v3float Function
               OpStore %tmin %float_0
               OpStore %tmax %float_1
         %21 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_0
         %22 = OpLoad %uint %21
         %23 = OpConvertUToF %float %22
         %25 = OpFAdd %float %23 %float_0_5
         %27 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_1
         %28 = OpLoad %uint %27
         %29 = OpConvertUToF %float %28
         %30 = OpFAdd %float %29 %float_0_5
         %31 = OpCompositeConstruct %v3float %25 %30 %float_0_5
               OpStore %origin %31
               OpStore %direction %34
               OpStore %hitValue %40
         %44 = OpLoad %41 %topLevelAS
         %46 = OpLoad %v3float %origin
         %47 = OpLoad %float %tmin
         %48 = OpLoad %v3float %direction
         %49 = OpLoad %float %tmax
               OpTraceRayKHR %44 %uint_0 %uint_255 %uint_0 %uint_0 %uint_0 %46 %47 %48 %49 %hitValue
         %53 = OpLoad %50 %result
         %55 = OpLoad %v3uint %gl_LaunchIDEXT
         %56 = OpVectorShuffle %v2uint %55 %55 0 1
         %58 = OpBitcast %v2int %56
         %59 = OpLoad %v4int %hitValue
               OpImageWrite %53 %58 %59 SignExtend
               OpReturn
               OpFunctionEnd
```

</details>## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `flags` | Build flags (`PREFER_FAST_TRACE`, `PREFER_FAST_BUILD`, `LOW_MEMORY`, `ALLOW_UPDATE`, `ALLOW_COMPACTION`), generic AS creation, arrays-of-pointers, or unbounded creation buffers produced a TLAS that traverses rays incorrectly. May also indicate `VK_KHR_device_address_commands` path or sparse-binding residency issues. |
| `format` | The implementation mishandled a vertex or index format (including `minAlign` misalignment, vertex padding, or 64-bit float formats), so the BLAS geometry does not match the host-rasterized reference triangle. |
| `operations` | `vkCmdCopyAccelerationStructureKHR`, compaction, or serialize/deserialize produced a TLAS or BLAS whose traversal differs from the freshly built source. May also indicate query-pool size reporting errors or sparse-binding residency issues. |
| `host_threading` | Deferred host operations with `vkDeferredOperationJoinKHR` across 1/2/3/4/8/`max` threads produced a structure different from the single-threaded build, or the implementation did not correctly partition work across the requested thread count. |
| `function_argument` | The SPIR-V `OpTraceRayKHR` did not accept a bare `OpTypeAccelerationStructureKHR` value (as opposed to a pointer load) as the first operand, or the function-call wrapper corrupted the AS argument. |
| `instance_triangle_culling` | `VkGeometryInstanceFlagsKHR` for `VK_GEOMETRY_INSTANCE_TRIANGLE_FACING_CULL_DISABLE_BIT_KHR` or `VK_GEOMETRY_INSTANCE_TRIANGLE_FRONT_COUNTERCLOCKWISE_BIT_KHR` did not produce the expected hit/miss pattern when combined with `gl_RayFlagsCullBackFacingTrianglesEXT`. |
| `ray_cull_mask` | The instance mask AND ray cullMask filtering did not match the spec, or `gl_CullMaskEXT` reported a wrong value in the hit/miss shader. Requires `VK_KHR_ray_tracing_maintenance1`. |
| `dynamic_indexing` | Non-uniform descriptor indexing of an array of TLAS handles, or `OpConvertUToAccelerationStructureKHR` from an SSBO-loaded device address, returned a wrong or invalid TLAS. Requires `VK_EXT_descriptor_indexing`. |
| `empty` | The implementation did not handle a BLAS with `geometryCount = 0`, a BLAS or TLAS with `primitiveCount = 0`, inactive triangles (NaN vertices), or inactive instances as if no geometry existed. |
| `instance_index` | `gl_InstanceCustomIndexEXT` reported a value other than `INSTANCE_CUSTOM_INDEX_BASE + x + y` in the selected stage (rgen, chit, ahit, or isect), or the host set the custom index incorrectly. |
| `instance_update` | TLAS update operations (`OP_UPDATE`, `OP_UPDATE_IN_PLACE`, `OP_UPDATE_UNINITIALIZED`) against a source TLAS produced a structure whose traversal differs from a fresh rebuild. |
| `device_compability_khr` | `vkGetDeviceAccelerationStructureCompatibilityKHR` did not return `COMPATIBLE_KHR` against the device's own UUIDs, or the version-info header was incorrectly formatted. |
| `header_bottom_address` | The serialized TLAS header's bottom-level pointer count or bottom-level device addresses did not match the actual BLAS set, or rebuilding a TLAS with mixed identical/different instances corrupted the header. |
| `query_pool_results` | `vkGetQueryPoolResults` for `ACCELERATION_STRUCTURE_COMPACTED_SIZE_KHR`, `ACCELERATION_STRUCTURE_SERIALIZATION_SIZE_KHR`, or `ACCELERATION_STRUCTURE_SERIALIZATION_BOTTOM_LEVEL_POINTERS_KHR` returned a value inconsistent with `vkGetAccelerationStructureBuildSizesKHR` or the actual serialization output. May also indicate availability-bit reporting errors. |
| `copy_within_pipeline` | A BLAS copy sequenced with `VK_PIPELINE_STAGE_2_ACCELERATION_STRUCTURE_COPY_BIT_KHR` or an SBT read sequenced with `VK_ACCESS_2_SHADER_BINDING_TABLE_READ_BIT_KHR` did not produce the same image as the reference, indicating a pipeline-stage or access-mask synchronization bug. Requires `VK_KHR_ray_tracing_maintenance1` and `VK_KHR_synchronization2`. |
| `update` | Updating a BLAS in place by replacing vertices, indices, transform, geometry transform, or by making a triangle degenerate did not produce the expected refit result, or the optional compaction-after-update path corrupted the structure. |
| `complex_geometry` | A realistic geometry model (icosphere, terrain, torusknot, trianglesoup) produced a hit rate outside the expected tolerance, or reported a primitive index outside the valid range, indicating build or traversal issues at scale. |

All shader-dispatch subgroups report failure through the same host-side image comparison. The shader never writes a fail flag; it writes the traversal-resolved per-pixel value, and the host compares it against the expected pattern. The three non-dispatch subgroups report failure through host-side query or header inspection.

### Cause Analysis

#### Build flag and resource residency traversal failures

**Possible failure symptoms:** A `flags` case fails `CheckerboardConfiguration::verifyImage`. Hit pixels report `1` (miss value) instead of `2`, or miss pixels report `2` (hit value) instead of `1`, or the pattern is scrambled. The failure may correlate with a specific build flag combination, a specific residency mode, or the unbounded-creation or device-address path.

**Possible implementation causes:** The build flags select internal build heuristics (fast-trace versus fast-build versus low-memory) and capabilities (allow-update, allow-compaction). A failure correlated with `PREFER_FAST_TRACE` but not `PREFER_FAST_BUILD` points to the fast-trace build path producing a structure with incorrect traversal. A failure only in `sparse_binding_structures` points to the sparse-binding residency path: the BLAS or TLAS backing buffer is allocated with sparse binding, and the implementation may not correctly resolve sparse-resident pages during build or traversal. A failure only on cases with `bottomUnboundedCreation` or `topUnboundedCreation` points to the unbounded-buffer creation path, where the build writes into a buffer sized larger than the final structure. The `_device_address` variants exercise `VK_KHR_device_address_commands`; a failure there points to the device-address-based build path.

#### Vertex and index format handling failures

**Possible failure symptoms:** A `format` case fails `SingleTriangleConfiguration::verifyImage`. The ray-traced depth image differs from the host-rasterized reference triangle beyond the 0.01 tolerance. The failure may correlate with a specific vertex format, index format, or the `padding` versus `nopadding` choice.

**Possible implementation causes:** The BLAS builder reads vertex data according to the `VkFormat` and stride. A failure with `R16G16B16_SNORM` but not `R32G32B32_SFLOAT` points to the normalized 16-bit format decoding path. A failure only with `padding` points to the stride and alignment handling: the host pads vertex data to `minAlign` boundaries, and the builder must honor the stride rather than assuming tight packing. A failure with `uint16` or `uint32` index format points to the index-decoding path. The 64-bit float format (`R32G32B32A32_SFLOAT`) exercises a wider vertex stride; a failure there points to stride handling for formats larger than the minimum.

#### Copy, compaction, and serialization operation failures

**Possible failure symptoms:** An `operations` case fails `CheckerboardConfiguration::verifyImage` after a copy, compaction, or serialize-then-deserialize operation, while the freshly built source passes. The post-operation structure traverses rays differently from the source.

**Possible implementation causes:** `OP_COPY` performs a byte-for-byte copy with `vkCmdCopyAccelerationStructureKHR`; a failure there points to the copy path not preserving the structure. `OP_COMPACT` queries the compacted size with `vkCmdWriteAccelerationStructuresPropertiesKHR`, allocates a smaller buffer, and copies with `vkCmdCopyAndCompactAccelerationStructureKHR`; a failure that appears only with compaction points to the compaction size query or the compaction copy itself. `OP_SERIALIZE` writes to a `SerialStorage` with `vkCmdCopyAccelerationStructureToMemoryKHR`, then deserializes with `vkCmdCopyMemoryToAccelerationStructureKHR`; a failure only with serialization points to the serialize or deserialize path, or to the compatibility UUID handling during deserialize. If the failure also appears in `query_pool_results`, the query-pool size reporting is suspect.

#### Host deferred operation threading failures

**Possible failure symptoms:** A `host_threading` case fails: the multi-threaded run produces a different structure than the single-threaded run, or both fail. The failure may correlate with a specific thread count.

**Possible implementation causes:** The host creates a `VkDeferredOperationKHR` and calls `vkDeferredOperationJoinKHR` from `workerThreadsCount` threads. The implementation partitions the deferred work across the joining threads. A failure where the single-threaded run passes but a specific multi-threaded count fails points to the work-partitioning logic: the implementation may not correctly split the build, copy, or serialize work across the requested thread count, or may have a race condition in the deferred-operation status reporting. A failure where all thread counts fail points to the deferred-operation path itself being broken, independent of threading. The `host_threading` subgroup only covers `OP_COPY` and `OP_SERIALIZE` because the test does not thread compaction as a deferred host operation.

#### SPIR-V function-argument calling convention failures

**Possible failure symptoms:** A `function_argument` case fails `SingleTriangleConfiguration::verifyImage`. The hand-written SPIR-V rgen wraps `OpTraceRayKHR` in two function-call layers, and the result image does not match the reference triangle.

**Possible implementation causes:** The SPIR-V `OpTraceRayKHR` takes the acceleration structure as its first operand. The test exercises two calling conventions: one passes a bare `OpTypeAccelerationStructureKHR` value loaded directly from the descriptor, the other passes a pointer to the AS and loads it inside the function. A failure in the bare-value path but not the pointer path (or vice versa) points to the implementation not correctly handling the AS value through a function-call boundary. The SPIR-V validator accepts both forms, but the implementation's SPIR-V to hardware lowering may only handle the direct-load form and not the function-argument form.

#### Instance culling and cull mask failures

**Possible failure symptoms:** An `instance_triangle_culling` or `ray_cull_mask` case fails `CheckerboardConfiguration::verifyImage`. The hit/miss pattern does not match the expected culling or mask behavior. For `ray_cull_mask`, the chit or miss shader writes a wrong `gl_CullMaskEXT` value.

**Possible implementation causes:** `instance_triangle_culling` varies `VkGeometryInstanceFlagsKHR` and `gl_RayFlagsCullBackFacingTrianglesEXT`. A failure where cull-disable cases pass but front-counterclockwise cases fail points to the triangle-winding-orientation handling. The instance's `VK_GEOMETRY_INSTANCE_TRIANGLE_FRONT_COUNTERCLOCKWISE_BIT_KHR` flips which face is front-facing, and the ray's `CullBackFacingTriangles` flag must respect that flip. `ray_cull_mask` ANDs the instance `mask` with the ray `cullMask`; a failure where an instance that should be visited is skipped (or vice versa) points to the mask-filtering logic. `gl_CullMaskEXT` reporting a wrong value points to the `VK_KHR_ray_tracing_maintenance1` builtin population path. The `bitfieldReverse` miss expectation catches implementations that store the cullMask in a different bit order.

#### Dynamic descriptor indexing failures

**Possible failure symptoms:** A `dynamic_indexing` case fails. The `atomicAdd` counters in the result buffer do not match the expected prime-offset pattern (2, 3, 5, 7), meaning one or both of the two indexing paths (descriptor array and `OpConvertUToAccelerationStructureKHR`) was not taken or returned a wrong TLAS.

**Possible implementation causes:** The rgen traces through two paths: non-uniform indexing into a 500-element TLAS descriptor array, and `OpConvertUToAccelerationStructureKHR` from an SSBO-loaded device address. A failure in the descriptor-array path points to the `VK_EXT_descriptor_indexing` non-uniform descriptor indexing lowering. A failure in the `OpConvertUToAccelerationStructureKHR` path points to the device-address-to-AS-handle conversion. The `atomicAdd` with prime offsets is how the test distinguishes which path was taken; if both paths fail, the issue is in the shared trace-and-store logic rather than in the indexing mechanism.

#### Empty acceleration structure handling failures

**Possible failure symptoms:** An `empty` case fails `CheckerboardConfiguration::verifyImage` or `SingleTriangleConfiguration::verifyImage`. The implementation traces the empty structure as if geometry exists (reporting hits where it should miss), or crashes during build or traversal.

**Possible implementation causes:** The spec allows four empty-structure shapes. `NO_GEOMETRIES` builds a BLAS with `geometryCount = 0`; a failure there points to the zero-geometry build path. `NO_PRIMITIVES` builds with `primitiveCount = 0`; a failure there points to the zero-primitive build path. `INACTIVE_TRIANGLES` uses NaN vertices that should produce no intersection; a failure there points to the NaN-vertex handling in the triangle intersection routine (the implementation may not correctly reject NaN-producing triangles). `INACTIVE_INSTANCES` uses instances that should be skipped; a failure there points to the instance-activation logic. `INACTIVE_TRIANGLES` is not registered for AABBs because NaN vertices apply only to triangles.

#### Instance custom index reporting failures

**Possible failure symptoms:** An `instance_index` case fails `CheckerboardConfiguration::verifyImage`. The chit, ahit, isect, or rgen shader writes a value other than `INSTANCE_CUSTOM_INDEX_BASE + x + y` to the result image.

**Possible implementation causes:** The host sets `instanceCustomIndex = INSTANCE_CUSTOM_INDEX_BASE + x + y` on each TLAS instance, where `INSTANCE_CUSTOM_INDEX_BASE = 0x807f00u`. The 24-bit instance custom index field has its most significant bit set to catch implementations that sign-extend the field. A failure where the written value is negative (or has the high bits set incorrectly) points to sign-extension of the 24-bit field. A failure where the written value is `x + y` without the base points to the implementation ignoring the `instanceCustomIndex` field and using `instanceId` instead. A failure only in one stage (e.g., ahit but not chit) points to the `gl_InstanceCustomIndexEXT` builtin not being populated correctly in that stage.

#### TLAS update and BLAS refit failures

**Possible failure symptoms:** An `instance_update` or `update` case fails `UpdateableASConfiguration::verifyImage` or `CheckerboardConfiguration::verifyImage`. The post-update structure traverses rays differently from a fresh rebuild. For `update`, the failure may correlate with a specific update dimension (vertices, indices, transform, geometry transform, degenerate triangle).

**Possible implementation causes:** `instance_update` exercises `OP_UPDATE`, `OP_UPDATE_IN_PLACE`, and `OP_UPDATE_UNINITIALIZED` on a TLAS. These reuse the existing TLAS allocation and update instance data in place. A failure where `OP_UPDATE` passes but `OP_UPDATE_IN_PLACE` fails points to the in-place update path not correctly invalidating stale internal data. `update` exercises BLAS refit by replacing vertices, indices, transforms, or making a triangle degenerate. The BLAS must have been built with `ALLOW_UPDATE`. A failure after a vertex replacement points to the refit not re-reading the new vertex data. A failure after making a triangle degenerate points to the refit not correctly removing the degenerate triangle from the traversal structure. The optional compaction-after-update path can fail if the compaction does not preserve the updated geometry.

#### Compatibility UUID and header address failures

**Possible failure symptoms:** A `device_compability_khr` or `header_bottom_address` case fails host-side validation. `vkGetDeviceAccelerationStructureCompatibilityKHR` does not return `COMPATIBLE_KHR`, or the serialized header's pointer count or addresses do not match the BLAS set.

**Possible implementation causes:** `device_compability_khr` compares the device's UUIDs against those in a serialized AS header. A failure where the device's own UUIDs do not match points to the UUID generation or reporting path, or to the header formatting. `header_bottom_address` inspects the serialized TLAS header's bottom-level pointer count and the bottom-level device addresses. A failure where the pointer count does not match the number of distinct BLASes points to the serialization header layout. A failure where the addresses are not stable across rebuilds points to the implementation not preserving the BLAS device addresses when the TLAS is rebuilt with the same instance set. Source-level investigation may be needed to distinguish a serialization bug from a header-parsing bug.

#### Query pool result failures

**Possible failure symptoms:** A `query_pool_results` case fails. `vkGetQueryPoolResults` returns a compacted size, serialization size, or serialization bottom-level pointer count that does not match `VkAccelerationStructureBuildSizesInfoKHR` or the actual serialization output. The `availability_bit` variant may report zero availability bits.

**Possible implementation causes:** The compacted size query must return a value less than or equal to the build size and greater than the minimum compacted size. A failure where the compacted size exceeds the build size points to the query-pool reporting path. The serialization size must account for the header, the structure data, and the bottom-level pointers. A failure where the serialization size is too small points to the size estimation not including all components. The serialization bottom-level pointer count must match the number of bottom-level ASes referenced by the TLAS. A failure where the count is wrong points to the pointer-count query path. The `availability_bit` variant checks that availability bits are nonzero after the query completes; a failure there points to the query-availability reporting path.

#### Pipeline-stage copy synchronization failures

**Possible failure symptoms:** A `copy_within_pipeline` case fails. The post-copy result image does not match the pre-copy reference image. The failure may appear only when the copy and the trace are in the same command buffer, or only when they are in different command buffers with a pipeline barrier between them.

**Possible implementation causes:** The BLAS copy is sequenced with `VK_PIPELINE_STAGE_2_ACCELERATION_STRUCTURE_COPY_BIT_KHR` and the SBT read is sequenced with `VK_ACCESS_2_SHADER_BINDING_TABLE_READ_BIT_KHR`. A failure where the post-copy trace reads stale BLAS data points to the pipeline-stage barrier not correctly waiting for the copy to complete. A failure where the SBT read returns stale handle data points to the access-mask barrier not correctly waiting for the SBT write to complete. Both require `VK_KHR_ray_tracing_maintenance1` and `VK_KHR_synchronization2`; a failure only on implementations that support those extensions points to the new pipeline-stage and access-flag handling.

#### Complex geometry traversal failures

**Possible failure symptoms:** A `complex_geometry` case fails `ComplexGeometryConfiguration::verifyImage`. The hit rate falls outside the 0.5% tolerance around the expected per-model rate (63% icosphere, 36% terrain, 45% torusknot, 31% trianglesoup), or a reported primitive index exceeds the model triangle count.

**Possible implementation causes:** The complex geometry models stress the BLAS build and traversal at a larger scale than the checkerboard. A failure where the hit rate is consistently lower than expected across all models points to a systematic traversal bug (e.g., rays missing triangles they should hit). A failure only with a specific model points to a geometry-specific build issue (e.g., the terrain model has many coplanar triangles that may stress the watertightness handling). A failure where primitive indices exceed the triangle count points to the `gl_PrimitiveID` reporting path or to the BLAS build corrupting the primitive index mapping. A failure that correlates with a specific build flag (e.g., `PREFER_FAST_BUILD` but not `PREFER_FAST_TRACE`) points to the fast-build heuristic producing a less accurate traversal structure. Source-level investigation may be needed to distinguish a build-quality issue from a traversal bug.

## Case Pruning

### Requirement-based pruning

- All cases require `VK_KHR_ray_tracing_pipeline` and `VK_KHR_acceleration_structure`, with `rayTracingPipeline == VK_TRUE` and `accelerationStructure == VK_TRUE`.
- `cpu_built` cases require `accelerationStructureHostCommands == VK_TRUE`.
- `sparse_binding_structures` cases require sparse-residency support and are pruned for host builds because sparse binding is only legal for device builds.
- `ray_cull_mask` cases require `VK_KHR_ray_tracing_maintenance1` for `gl_CullMaskEXT`.
- `dynamic_indexing` cases require `VK_EXT_descriptor_indexing` for non-uniform descriptor indexing.
- `copy_within_pipeline` cases require `VK_KHR_ray_tracing_maintenance1` and `VK_KHR_synchronization2` for the new pipeline-stage and access-flag bits.
- `function_argument` cases require the SPIR-V `OpTypeAccelerationStructureKHR` and `OpTraceRayKHR` capability, available with `VK_KHR_ray_tracing_pipeline`.
- `device_compability_khr` cases require serialization support.
- Device limits (max acceleration structure size, max geometry count, max instance count) are checked before execution; cases exceeding device limits are pruned.

### Design-based pruning

- The `flags` subgroup uses `de::ModCounter32` to set `bottomUnboundedCreation` and `topUnboundedCreation` on a rotating subset of cases rather than expanding the matrix. This keeps the case count bounded while still exercising unbounded-buffer creation. See [addBasicBuildingTests](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L6058-L6279).
- The `flags` subgroup adds `_device_address` variants on a small subset of cases that require `VK_KHR_device_address_commands`, rather than on every case.
- The `host_threading` subgroup only exercises `OP_COPY` and `OP_SERIALIZE` for the deferred host operation path, because the test does not thread compaction as a deferred host operation.
- The `empty` subgroup does not register an `INACTIVE_TRIANGLES` case for AABBs, because NaN vertices apply only to triangles. See [addEmptyAccelerationStructureTests](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L6785-L6891).
- The `update` subgroup prunes host-built `GEOMETRY_TRANSFORM` cases because that path is device-only.
- The `function_argument` subgroup is registered with `SingleTriangleConfiguration` and only the `cpu_built` and `gpu_built` build types under `traditional_structures` and `sparse_binding_structures`, rather than the full matrix.
- The `complex_geometry` subgroup uses a fixed set of 4 models with a statistical hit-rate validation, not per-pixel exact comparison, because the models are too large for per-pixel reference generation.

## Key Takeaways

- The 17 subgroups all root in one source file but test distinct AS properties. The subgroup name is the primary behavioral axis; the remaining dimensions configure how hard each mechanism is stressed.
- Most subgroups share the same `RayTracingASBasicTestCase::initPrograms` shader generator, which emits rgen, chit, ahit, miss, and isect shaders driven by `instanceCustomIndexCase`, `cullFlags`, `cullMask`, and `useCullMask`. The representative rgen walkthrough covers the shared trace-and-store pattern.
- Three subgroups (`device_compability_khr`, `header_bottom_address`, `query_pool_results`) skip shader dispatch and validate host-side query or header data directly. Their failure analysis is distinct from the shader-dispatch subgroups.
- `INSTANCE_CUSTOM_INDEX_BASE = 0x807f00u` is chosen so the most significant bit set in 24 bits catches implementations that sign-extend the instance custom index field.
- `complex_geometry` uses statistical hit-rate validation with a 0.5% tolerance, not per-pixel exact comparison, because the realistic geometry models are too large for per-pixel references.
- Failure analysis splits along the subgroup axis: build-flag and format handling, copy/compact/serialize operations, host threading, SPIR-V calling conventions, instance culling and cull masks, descriptor indexing, empty structures, instance indices, TLAS and BLAS updates, compatibility and header validation, query pools, pipeline-stage synchronization, and complex geometry at scale. See `## Failure Meaning` for the per-subgroup analysis.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `TestParams` struct | [vktRayTracingAccelerationStructuresTests.cpp#L183-L214](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L183-L214) | Defines the per-case parameter struct shared by all subgroups. |
| `CheckerboardConfiguration::verifyImage` | [vktRayTracingAccelerationStructuresTests.cpp#L733-L771](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L733-L771) | Host validation for basic, flags, operations, culling, cull-mask, and instance-index subgroups. |
| `SingleTriangleConfiguration::verifyImage` | [vktRayTracingAccelerationStructuresTests.cpp#L970-L972](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L970-L972) | Host validation for format and empty-AS subgroups. |
| `UpdateableASConfiguration::verifyImage` | [vktRayTracingAccelerationStructuresTests.cpp#L1183-L1220](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L1183-L1220) | Host validation for the update and instance_update subgroups. |
| `ComplexGeometryConfiguration::verifyImage` | [vktRayTracingAccelerationStructuresTests.cpp#L1511-L1600](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L1511-L1600) | Hit-rate validation for the complex_geometry subgroup. |
| `RayTracingASBasicTestCase::initPrograms` | [vktRayTracingAccelerationStructuresTests.cpp#L1866-L2092](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L1866-L2092) | Generates rgen, chit, ahit, miss, isect shaders used by most subgroups. |
| `RayTracingASFuncArgTestCase::initPrograms` | [vktRayTracingAccelerationStructuresTests.cpp#L2105-L2460](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L2105-L2460) | Hand-written SPIR-V rgen for the function_argument subgroup. |
| `RayTracingASDynamicIndexingTestCase::initPrograms` | [vktRayTracingAccelerationStructuresTests.cpp#L3035-L3274](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L3035-L3274) | Hand-written SPIR-V rgen and chit for the dynamic_indexing subgroup. |
| `PipelineStageASCase::initPrograms` | [vktRayTracingAccelerationStructuresTests.cpp#L5026-L5077](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L5026-L5077) | Generates the copy_within_pipeline shaders. |
| `RayTracingASComplexGeometryTestCase::initPrograms` | [vktRayTracingAccelerationStructuresTests.cpp#L1744-L1812](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L1744-L1812) | Generates the complex_geometry shaders. |
| `RayTracingASBasicTestInstance::runTest` | [vktRayTracingAccelerationStructuresTests.cpp#L2470-L2950](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L2470-L2950) | Builds BLAS and TLAS, applies the operation, dispatches, copies back. |
| `RayTracingASBasicTestInstance::iterateWithWorkers` | [vktRayTracingAccelerationStructuresTests.cpp#L2960-L2973](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L2960-L2973) | Single-thread and multi-thread validation for host_threading. |
| `ASUpdateInstance::iterate` | [vktRayTracingAccelerationStructuresTests.cpp#L5729-L6057](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L5729-L6057) | Update-and-retrace flow for the update subgroup. |
| `QueryPoolResultsSizeInstance::iterate` | [vktRayTracingAccelerationStructuresTests.cpp#L4637-L4691](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L4637-L4691) | Compacted-size query validation. |
| `QueryPoolResultsPointersInstance::iterate` | [vktRayTracingAccelerationStructuresTests.cpp#L4693-L4815](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L4693-L4815) | Serialization bottom-level pointer count query validation. |
| `RayTracingDeviceASCompabilityKHRTestInstance::iterate` | [vktRayTracingAccelerationStructuresTests.cpp#L3692-L3976](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L3692-L3976) | `vkGetDeviceAccelerationStructureCompatibilityKHR` UUID check. |
| `RayTracingHeaderBottomAddressTestInstance::iterate` | [vktRayTracingAccelerationStructuresTests.cpp#L3978-L4112](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L3978-L4112) | TLAS header bottom-pointer verification. |
| `CopyBlasInstance::iterate` and `CopySBTInstance::iterate` | [vktRayTracingAccelerationStructuresTests.cpp#L5270-L5688](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L5270-L5688) | Pipeline-stage copy and SBT-read synchronization. |
| `addBasicBuildingTests` | [vktRayTracingAccelerationStructuresTests.cpp#L6058-L6279](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L6058-L6279) | Registers the flags subgroup. |
| `addOperationTestsImpl` | [vktRayTracingAccelerationStructuresTests.cpp#L6413-L6544](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L6413-L6544) | Registers the operations and host_threading subgroups. |
| `addEmptyAccelerationStructureTests` | [vktRayTracingAccelerationStructuresTests.cpp#L6785-L6891](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L6785-L6891) | Registers the empty subgroup. |
| `addQueryPoolResultsTests` | [vktRayTracingAccelerationStructuresTests.cpp#L7363-L7449](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L7363-L7449) | Registers the query_pool_results subgroup. |
| `addComplexGeometryTests` | [vktRayTracingAccelerationStructuresTests.cpp#L7616-L7736](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L7616-L7736) | Registers the complex_geometry subgroup. |
| `createAccelerationStructuresTests` | [vktRayTracingAccelerationStructuresTests.cpp#L7738-L7776](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L7738-L7776) | Creates the acceleration_structures group and attaches all 17 subgroups. |
