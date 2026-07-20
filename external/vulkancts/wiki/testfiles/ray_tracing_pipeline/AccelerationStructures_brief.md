# Understanding Brief: ray_tracing_pipeline.acceleration_structures family

## One-Sentence Test Purpose

This test family checks whether `VK_KHR_acceleration_structure` builds, copies,
compaction, serialization, updates, queries, host threading, instance culling,
cull masks, dynamic indexing, and empty-structure handling all produce a
top-level acceleration structure that ray tracing shaders traverse identically
to a freshly built reference, across a large matrix of build flags, vertex and
index formats, build types, and resource residency modes.

## Background Knowledge

### Top-level and bottom-level acceleration structures

A Vulkan ray tracing pipeline traverses a top-level acceleration structure
(TLAS) that references one or more bottom-level acceleration structures
(BLAS). Each BLAS holds geometry (triangles or AABBs). Each TLAS instance
references a BLAS, applies a 3x4 transform, and carries an
`instanceCustomIndex`, a `cullMask`, an `instanceShaderBindingTableRecordOffset`,
and `VkGeometryInstanceFlagsKHR` (face culling, opacity, triangle facing).

Why it matters here:
- Every subgroup in this family constructs a TLAS+BLAS pair and traces a ray
  through it. The result image pattern reflects whether traversal behaved
  correctly.
- The host-side `BottomLevelAccelerationStructure` and
  `TopLevelAccelerationStructure` builder helpers in `vkBuilderUtil` expose the
  build, copy, compact, serialize, deserialize, and update operations defined
  by `VK_KHR_acceleration_structure`.

### Build types and resource residency

`VkAccelerationStructureBuildTypeKHR` selects whether the build happens on the
host (`VK_ACCELERATION_STRUCTURE_BUILD_TYPE_HOST_KHR`) or via
`vkCmdBuildAccelerationStructuresKHR` on a queue
(`VK_ACCELERATION_STRUCTURE_BUILD_TYPE_DEVICE_KHR`). Host builds require the
`accelerationStructureHostCommands` feature. The `ResourceResidency`
dimension in this test switches between `TRADITIONAL` device-local buffers and
`SPARSE_BINDING` buffers backed by a sparse queue. Sparse binding is only
legal for device builds; the registration prunes host+sparse combinations.

### Build flags

`VkBuildAccelerationStructureFlagsKHR` controls tradeoffs and capabilities:
`PREFER_FAST_TRACE`, `PREFER_FAST_BUILD`, `LOW_MEMORY`, `ALLOW_UPDATE`,
`ALLOW_COMPACTION`. The `ALLOW_UPDATE` flag must be set for any in-place
refit. The `ALLOW_COMPACTION` flag must be set before
`vkCmdWriteAccelerationStructuresPropertiesKHR` can report the compacted size.

### Copy, compact, serialize

`vkCmdCopyAccelerationStructureKHR` performs a byte-for-byte copy.
`vkCmdCopyAccelerationStructureToMemoryKHR` and the inverse serialize and
deserialize a structure together with a header carrying compatibility UUIDs.
`vkCmdCopyAndCompactAccelerationStructureKHR` (or copy with a compacted size
query) produces a smaller equivalent structure. Compaction requires the source
to be built with `ALLOW_COMPACTION`. The test rebuilds the original,
performs the operation, and then traces the same ray pattern through the
resulting structure to confirm equivalence.

### Host deferred operations and threading

`VK_KHR_acceleration_structure` exposes deferred host operations
(`vkBuildAccelerationStructuresKHR`, `vkCopyAccelerationStructureKHR`,
`vkCopyAndCompactAccelerationStructureKHR`,
`vkSerializeAccelerationStructureKHR`,
`vkDeserializeAccelerationStructureKHR`) that take a
`VkDeferredOperationKHR`. The application can partition work across
`workerThreadsCount` host threads by calling
`vkDeferredOperationJoinKHR` from each thread. The `host_threading` subgroup
exercises this with 1, 2, 3, 4, 8, and `max` threads.

### Instance culling, cull mask, instance custom index

`VkGeometryInstanceFlagsKHR` carries `VK_GEOMETRY_INSTANCE_TRIANGLE_FACING_CULL_DISABLE_BIT_KHR`,
`VK_GEOMETRY_INSTANCE_TRIANGLE_FRONT_COUNTERCLOCKWISE_BIT_KHR`, and the
cull-disable bits. The ray's `cullMask` is AND-ed with the instance's
`mask`; only instances whose mask AND cullMask is nonzero are visited. The
shader `gl_InstanceCustomIndexEXT` reads the per-instance custom index, and
`gl_CullMaskEXT` (from `VK_KHR_ray_tracing_maintenance1`) reads the active
cullMask bits.

### Empty acceleration structures

The spec allows empty structures: a BLAS with no geometries, a BLAS or TLAS
with zero primitives, inactive triangles (NaN vertices that produce no
intersection), and inactive instances. A correct implementation traces such
structures as if no geometry exists. The `empty` subgroup verifies these
shapes against the same `CheckerboardConfiguration` and
`SingleTriangleConfiguration` shaders used by non-empty cases.

### Query pools and pipeline stage barriers

`VK_QUERY_TYPE_ACCELERATION_STRUCTURE_COMPACTED_SIZE_KHR` and
`VK_QUERY_TYPE_ACCELERATION_STRUCTURE_SERIALIZATION_SIZE_KHR` return per-handle
sizes. `VK_QUERY_TYPE_ACCELERATION_STRUCTURE_SERIALIZATION_BOTTOM_LEVEL_POINTERS_KHR`
returns the number of bottom-level pointers stored in a serialized TLAS.
`VK_KHR_ray_tracing_maintenance1` introduces the
`VK_PIPELINE_STAGE_2_ACCELERATION_STRUCTURE_COPY_BIT_KHR` and
`VK_ACCESS_2_SHADER_BINDING_TABLE_READ_BIT_KHR` pipeline stage and access
flags used to sequence AS copies and SBT reads against ray tracing dispatch.

## One Concrete Example

Representative case: `ray_tracing_pipeline.acceleration_structures.flags.traditional_structures.gpu_built.triangles.identical_instances.nopadding.fasttrace_0_0_0`.

This case builds a TLAS over an 8x8 checkerboard of triangle BLASes on the
device with `VK_BUILD_ACCELERATION_STRUCTURE_PREFER_FAST_TRACE_BIT_KHR`.
The raygen shader traces one ray per launch id into the TLAS. The
closest-hit shader writes `ivec4(2,0,0,1)` to the payload; the miss shader
writes `ivec4(1,0,0,1)`. The raygen shader stores the payload to a 2D
`r32i` storage image at `gl_LaunchIDEXT.xy`.

The host verifies a checkerboard pattern: positions where `(x + y) % 2 == 1`
must report `2` (a hit, because the BLAS at that cell exists) and positions
where `(x + y) % 2 == 0` must report `1` (a miss, because no BLAS was placed
there). The pattern matches the geometry construction in
`CheckerboardConfiguration::initBottomAccelerationStructures`.

Simplified rgen shader reconstruction:

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
  vec3  direction = vec3(0.0, 0.0, -1.0);
  hitValue        = ivec4(0, 0, 0, 0);
  traceRayEXT(topLevelAS, 0, 0xFFu, 0, 0, 0, origin, tmin, direction, tmax, 0);
  imageStore(result, ivec2(gl_LaunchIDEXT.xy), hitValue);
}
```

The `0xFFu` cullMask and the `0` ray flags are literal because this is a
`InstanceCullFlags::NONE`, non-cull-mask case. The same generator swaps the
cullMask literal for the per-case value when `useCullMask` is true and swaps
the ray-flags literal for `gl_RayFlagsCullBackFacingTrianglesEXT` when
`cullFlags` is not `NONE`.

## End-to-End Test Flow

```text
[host] choose TestParams (build type, build flags, formats, top/bottom type, operation, residency, etc.)
[host] create result image (r32i or r32f or rgba32ui) and host-visible readback buffer
[host] compile rgen/chit/ahit/miss/isect shaders; build RayTracingPipeline and SBT regions
[host] [bottom build] create BLASes, set build flags, set AOP/generic/unbounded, createAndBuild
[host] [bottom op]    if operation target is bottom: copy/compact/serialize/deserialize, swap to copy
[host] [top build]    create TLAS over the chosen BLAS set, set flags, createAndBuild
[host] [top op]       if operation target is top: copy/compact/serialize/deserialize/update, swap to copy
[host] write descriptor set with result image (binding 0) and TLAS handle (binding 1)
[host] vkCmdTraceRaysKHR with (width, height, 1)
[device] rgen traces one ray per launch id; chit/miss writes hitValue; rgen imageStores
[host] pipeline barrier: shader-write to transfer-read
[host] vkCmdCopyImageToBuffer; invalidate mapped memory
[host] testConfiguration->verifyImage compares each pixel against an expected pattern
[host] pass only if no failures (or, for complex_geometry, hit rate within tolerance)
```

For `host_threading` cases the run is duplicated: once single-threaded and
once with `workerThreadsCount`, both must pass. For `query_pool_results`
cases there is no shader dispatch: the test only compares query results
against `VkAccelerationStructureBuildSizesInfoKHR` reported by
`vkGetAccelerationStructureBuildSizesKHR`. For `device_compability_khr` and
`header_bottom_address` cases there is also no shader dispatch: they verify
UUID compatibility or address handling directly. For `copy_within_pipeline`
cases the test traces the same scene twice, once with the original BLAS and
once with the post-copy BLAS, then compares the two result images.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- GLSL `rgen`, `chit`, `ahit`, `miss`, `isect` shaders generated by
  `RayTracingASBasicTestCase::initPrograms` for the basic, format, culling,
  cull-mask, instance-index, instance-update, and update subgroups. Only the
  stages needed for the active `InstanceCustomIndexCase` are emitted.
- GLSL `rgen_depth`, `chit_depth`, `miss_depth` shaders for the
  `SingleTriangleConfiguration` path used by format and empty-AS tests; the
  closest-hit shader writes `gl_RayTmaxEXT` and the miss shader writes 0.
- GLSL `rgen_complex`, `chit_complex`, `miss_complex` for
  `complex_geometry`. The closest-hit shader packs
  `(1, floatBitsToUint(gl_HitTEXT), gl_PrimitiveID, gl_GeometryIndexEXT)`
  into a `rgba32ui` texel.
- GLSL `rgen`/`chit`/`miss` for `copy_within_pipeline` writing `vec4` color
  payloads (green for hit, red for miss).
- Hand-written SPIR-V assembly `rgen` for `function_argument` that wraps
  `traceRayEXT` in two function-call layers, one taking a bare
  `OpTypeAccelerationStructureKHR` value and one taking a pointer.
- Hand-written SPIR-V assembly `rgen` for `dynamic_indexing` that loads a TLAS
  handle from a runtime-sized SSBO of pointers, converts it via
  `OpConvertUToAccelerationStructureKHR`, and traces through it
  non-uniformly.
- `vk::ShaderBuildOptions` targets `SPIRV_VERSION_1_4` for the regular
  cases.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| 2D `r32i`/`r32f`/`rgba32ui` storage image (`result`) | yes | binding 0 | yes, written by `imageStore` | yes, copied to host buffer | Holds the per-pixel hit/miss result |
| TLAS handle | yes | binding 1 (`VK_DESCRIPTOR_TYPE_ACCELERATION_STRUCTURE_KHR`) | yes, read by `traceRayEXT` | no | Drives all ray traversal |
| BLASes | yes, with triangles or AABBs | referenced by TLAS | yes | no | Provides the geometry |
| Host-visible readback buffer | yes | transfer-destination | yes, written by `vkCmdCopyImageToBuffer` | yes | Holds the copied-back image data |
| Shader binding table | yes | SBT regions per stage | read by the ray tracing dispatch | no | Routes rgen/miss/hit groups |
| Query pool (compact/serial/pointer) | yes for `query_pool_results`, `operations` | n/a | written by `vkCmdWriteAccelerationStructuresPropertiesKHR` | yes via `vkGetQueryPoolResults` | Reports sizes/counts used to validate operations |
| Serial storage buffer | yes for `operations` serialize path | host or device | yes, written/read by serialize/deserialize | yes | Holds serialized AS bytes |
| Indirect command buffer | not used here | n/a | n/a | n/a | This family uses direct `vkCmdTraceRaysKHR` |

## What Is Checked

The pass condition depends on the subgroup:

- For shader-tracing subgroups (`flags`, `format`, `operations`,
  `host_threading`, `function_argument`, `instance_triangle_culling`,
  `ray_cull_mask`, `dynamic_indexing`, `empty`, `instance_index`,
  `instance_update`, `update`, `copy_within_pipeline`, `complex_geometry`):
  - The host calls `testConfiguration->verifyImage` and returns pass only if
    zero pixels mismatch the expected pattern.
  - `CheckerboardConfiguration` expects `(x + y) % 2 ? hitValue : 1`, where
    `hitValue` is `2` for the basic path, `INSTANCE_CUSTOM_INDEX_BASE + x + y`
    for `instance_index`, `cullMask & 0xFF` for `ray_cull_mask` hits, and
    `bitfieldReverse(cullMask & 0xFF)` for cull-mask misses.
  - `SingleTriangleConfiguration` and `UpdateableASConfiguration` compare
    against a host-rasterized reference image of a triangle using
    `tcu::floatThresholdCompare` with a 0.01 tolerance.
  - `ComplexGeometryConfiguration` checks the hit percentage against a
    per-model expected rate (e.g. 63% for icosphere) with a 0.5% tolerance,
    plus checks that primitive indices stay within the model triangle count.
  - `copy_within_pipeline` compares the result image of the post-copy BLAS
    against the pre-copy reference image, requiring exact equality.
- For non-shader subgroups:
  - `device_compability_khr` verifies that
    `vkGetDeviceAccelerationStructureCompatibilityKHR` returns
    `VK_ACCELERATION_STRUCTURE_COMPATIBILITY_COMPATIBLE_KHR` against the
    device's own UUIDs.
  - `header_bottom_address` verifies that a TLAS built with mixed
    identical/different instances has a header with the correct bottom-level
    pointer count and that the bottom-level device addresses are stable
    across rebuilds.
  - `query_pool_results` verifies that
    `vkGetQueryPoolResults` for compacted size, serialization size, and
    serialization bottom-level pointer count matches
    `VkAccelerationStructureBuildSizesInfoKHR` and the actual pointer count
    observed during serialization. The `availability_bit` variant also
    checks that availability bits are nonzero.

## Behavior Parameter Identification

> **Behavior parameter:** test family direct child (the registered subgroup
> name under `acceleration_structures`)
>
> **Candidate values:** `flags`, `format`, `operations`, `host_threading`,
> `function_argument`, `instance_triangle_culling`, `ray_cull_mask`,
> `dynamic_indexing`, `empty`, `instance_index`, `instance_update`,
> `device_compability_khr`, `header_bottom_address`,
> `query_pool_results`, `copy_within_pipeline`, `update`,
> `complex_geometry`

This family groups 17 subgroups rooted in the same source file
(`vktRayTracingAccelerationStructuresTests.cpp`). Each subgroup changes what
is being tested about acceleration structures: build flag combinations,
vertex/index formats, copy/compact/serialize operations, host threading,
function-argument calling conventions, instance culling, cull masks,
descriptor indexing, empty structures, instance custom indices, TLAS update
operations, compatibility queries, header/bottom address handling, query
pools, pipeline-stage AS copies, BLAS updates, and complex realistic
geometry.

## What Failure Means

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

## Important Variations and Special Cases

- The `flags` subgroup uses `de::ModCounter32` to set
  `bottomUnboundedCreation` and `topUnboundedCreation` on a rotating subset
  of cases rather than expanding the matrix. This keeps the case count
  bounded while still exercising unbounded-buffer creation.
- The `flags` subgroup adds `_device_address` variants on a small subset of
  cases that require `VK_KHR_device_address_commands`.
- The `host_threading` subgroup only exercises `OP_COPY` and `OP_SERIALIZE`
  for the deferred host operation path, because compaction is not exposed as
  a deferred host operation.
- The `empty` subgroup does not register an `INACTIVE_TRIANGLES` case for
  AABBs (NaN vertices apply only to triangles).
- The `update` subgroup prunes host-built `GEOMETRY_TRANSFORM` cases because
  that path is device-only.
- The `function_argument` subgroup is registered with
  `SingleTriangleConfiguration` and only the `cpu_built` and `gpu_built`
  build types under `traditional_structures` and `sparse_binding_structures`.
- The `complex_geometry` subgroup uses `ComplexGeometryConfiguration` with a
  per-model expected hit rate table; the verification is statistical, not
  per-pixel exact.
- `INSTANCE_CUSTOM_INDEX_BASE = 0x807f00u` is chosen so the most significant
  bit set in 24 bits catches implementations that sign-extend the instance
  custom index.
- `dynamic_indexing` uses an array of 500 TLAS descriptors and a runtime
  SSBO of TLAS device addresses. The shader traces through both paths
  (descriptor array and `OpConvertUToAccelerationStructureKHR`) and uses
  `atomicAdd` with prime offsets (2, 3, 5, 7) into a result buffer to
  verify each path was taken.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| `TestParams` struct | [vktRayTracingAccelerationStructuresTests.cpp#L183-L214](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L183-L214) | Defines the per-case parameter struct shared by all subgroups. |
| `CheckerboardConfiguration::verifyImage` | [vktRayTracingAccelerationStructuresTests.cpp#L733-L771](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L733-L771) | Host validation for the basic, flags, operations, culling, cull-mask, and instance-index subgroups. |
| `SingleTriangleConfiguration::verifyImage` | [vktRayTracingAccelerationStructuresTests.cpp#L970-L972](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L970-L972) | Host validation for the format and empty-AS subgroups. |
| `UpdateableASConfiguration::verifyImage` | [vktRayTracingAccelerationStructuresTests.cpp#L1183-L1220](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L1183-L1220) | Host validation for the update subgroup. |
| `ComplexGeometryConfiguration::verifyImage` | [vktRayTracingAccelerationStructuresTests.cpp#L1511-L1600](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L1511-L1600) | Hit-rate validation for the complex_geometry subgroup. |
| `RayTracingASBasicTestCase::initPrograms` | [vktRayTracingAccelerationStructuresTests.cpp#L1866-L2092](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L1866-L2092) | Generates the rgen/chit/ahit/miss/isect shaders used by most subgroups. |
| `RayTracingASFuncArgTestCase::initPrograms` | [vktRayTracingAccelerationStructuresTests.cpp#L2105-L2460](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L2105-L2460) | Hand-written SPIR-V rgen for the function_argument subgroup. |
| `RayTracingASComplexGeometryTestCase::initPrograms` | [vktRayTracingAccelerationStructuresTests.cpp#L1744-L1812](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L1744-L1812) | Generates the complex_geometry shaders. |
| `RayTracingASDynamicIndexingTestCase::initPrograms` | [vktRayTracingAccelerationStructuresTests.cpp#L3035-L3274](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L3035-L3274) | Hand-written SPIR-V rgen and chit for the dynamic_indexing subgroup. |
| `PipelineStageASCase::initPrograms` | [vktRayTracingAccelerationStructuresTests.cpp#L5026-L5077](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L5026-L5077) | Generates the copy_within_pipeline shaders. |
| `RayTracingASBasicTestInstance::runTest` | [vktRayTracingAccelerationStructuresTests.cpp#L2470-L2950](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L2470-L2950) | Builds BLAS/TLAS, performs the operation, dispatches `vkCmdTraceRaysKHR`, copies back. |
| `RayTracingASBasicTestInstance::iterateWithWorkers` | [vktRayTracingAccelerationStructuresTests.cpp#L2960-L2973](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L2960-L2973) | Single-thread and multi-thread validation for the host_threading subgroup. |
| `ASUpdateInstance::iterate` | [vktRayTracingAccelerationStructuresTests.cpp#L5729-L6057](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L5729-L6057) | Update-and-retrace flow for the update subgroup. |
| `QueryPoolResultsSizeInstance::iterate` | [vktRayTracingAccelerationStructuresTests.cpp#L4637-L4691](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L4637-L4691) | Compacted-size query validation. |
| `QueryPoolResultsPointersInstance::iterate` | [vktRayTracingAccelerationStructuresTests.cpp#L4693-L4815](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L4693-L4815) | Serialization bottom-level pointer count query validation. |
| `RayTracingDeviceASCompabilityKHRTestInstance::iterate` | [vktRayTracingAccelerationStructuresTests.cpp#L3692-L3976](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L3692-L3976) | `vkGetDeviceAccelerationStructureCompatibilityKHR` UUID check. |
| `RayTracingHeaderBottomAddressTestInstance::iterate` | [vktRayTracingAccelerationStructuresTests.cpp#L3978-L4112](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L3978-L4112) | TLAS header bottom-pointer verification. |
| `CopyBlasInstance::iterate` and `CopySBTInstance::iterate` | [vktRayTracingAccelerationStructuresTests.cpp#L5270-L5688](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L5270-L5688) | Pipeline-stage copy/compaction and SBT-read synchronization. |
| `addBasicBuildingTests` registration | [vktRayTracingAccelerationStructuresTests.cpp#L6058-L6279](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L6058-L6279) | Registers the `flags` subgroup. |
| `addOperationTestsImpl` registration | [vktRayTracingAccelerationStructuresTests.cpp#L6413-L6544](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L6413-L6544) | Registers the `operations` and `host_threading` subgroups. |
| `addEmptyAccelerationStructureTests` registration | [vktRayTracingAccelerationStructuresTests.cpp#L6785-L6891](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L6785-L6891) | Registers the `empty` subgroup. |
| `addQueryPoolResultsTests` registration | [vktRayTracingAccelerationStructuresTests.cpp#L7363-L7449](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L7363-L7449) | Registers the `query_pool_results` subgroup. |
| `createAccelerationStructuresTests` top-level registration | [vktRayTracingAccelerationStructuresTests.cpp#L7738-L7776](../../../modules/vulkan/ray_tracing/vktRayTracingAccelerationStructuresTests.cpp#L7738-L7776) | Creates the `acceleration_structures` group and attaches all 17 subgroups. |

## Questions / Risk Points for User Audit

- Is the core test purpose clear: one source file registers 17 subgroups
  that each exercise a distinct AS build, operation, or shader-traversal
  property?
- Is the host/device timeline understandable, including the cases where no
  shader dispatch happens (`device_compability_khr`, `header_bottom_address`,
  `query_pool_results`)?
- Are the per-subgroup expected values clear, especially the
  `INSTANCE_CUSTOM_INDEX_BASE = 0x807f00u` choice and the
  `bitfieldReverse` cull-mask expectation for misses?
- Is the representative walkthrough choice (the simplest
  `flags.traditional_structures.gpu_built.triangles.identical_instances.nopadding.fasttrace_0_0_0`
  case) appropriate, given that most subgroups reuse the same shader
  generator?
- Should the page mention every subgroup in `Behavior Parameters`, or only
  group them by mechanism (build, operation, shader-traversal, query-only)?
- The `complex_geometry` subgroup uses statistical hit-rate validation, not
  per-pixel exact comparison. Is that distinction preserved clearly enough?

## Conversion Notes for Final Wiki Rewrite

- Distill the Background Knowledge into a short unordered list in the final
  page's `## Background Knowledge`, focused on TLAS/BLAS, build types,
  build flags, copy/compact/serialize, deferred host operations, instance
  culling, cull mask, empty structures, and the maintenance1 pipeline-stage
  bits.
- The `### Failure Cause Mapping` table above will be copied verbatim into
  the final page's `## Failure Meaning` section.
- The concrete rgen example becomes the representative shader walkthrough
  for the `flags.traditional_structures.gpu_built.triangles.identical_instances.nopadding.fasttrace_0_0_0`
  case. The chit and miss shaders are tiny and only carry the literal
  payload value; they are summarized in the walkthrough body rather than
  given separate SPIR-V blocks.
- The 17 subgroups are the primary behavioral axis for `## Behavior
  Parameters`. They are too many to expand verbosely, so each subsection
  stays to one or two sentences identifying the mechanism and the
  validation path.
- Per-subgroup expected-value details and the
  `INSTANCE_CUSTOM_INDEX_BASE` rationale belong in
  `## Runtime Execution and Result Checking` rather than in
  `## Behavior Parameters`.
- Non-shader subgroups (`device_compability_khr`,
  `header_bottom_address`, `query_pool_results`) are mentioned in
  `## Behavior Parameters` and `## Runtime Execution and Result Checking`
  but do not get a shader walkthrough.
- The `### Cause Analysis` is written fresh during the final rewrite, with
  one `####` subsection per distinct failure mechanism (build-flag
  traversal, vertex format, copy/compact/serialize, host threading,
  function-argument SPIR-V, instance culling, cull mask, dynamic
  indexing, empty AS, instance custom index, TLAS update, compatibility
  UUID, header address, query pool, pipeline-stage copy, BLAS update,
  complex geometry).
