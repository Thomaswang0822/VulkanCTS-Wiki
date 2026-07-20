# Understanding Brief: ray_query acceleration_structures

## One-Sentence Test Purpose

This test checks that an inline ray query observes the same hit/miss checkerboard pattern across many valid ways of creating, building, copying, compacting, serializing, updating, indexing, and emptying a `VK_KHR_acceleration_structure`, including combinations of CPU and GPU builds, sparse and traditional residency, host-threaded deferred operations, face culling, and dynamic descriptor indexing.

## Background Knowledge

### Acceleration structures: TLAS, BLAS, and the two-level shape

Ray tracing needs a bounding-volume hierarchy (BVH) to skip primitives a ray does not intersect. `VK_KHR_acceleration_structure` provides a two-level BVH: a bottom-level acceleration structure (BLAS) is built from one object's triangles or AABBs in object space; a top-level acceleration structure (TLAS) is built from instances referencing those BLASes with per-instance transforms. A ray walks the TLAS, applies an instance transform, and descends into the referenced BLAS at each leaf. These definitions are in the Vulkan spec chapter "Acceleration Structures" (vendored at `external/vulkan-docs/src/chapters/accelstructures.adoc`, which is not checked out in this environment; the definitions above are also documented in the Khronos `VK_KHR_acceleration_structure` reference pages).

The test stresses two distinct points in the BVH pipeline:

- The build and AS object creation path: resident or sparse buffer memory, arrays-of-structures or arrays-of-pointers (AOP), generic or typed create flags, with or without optimization, update, compaction, or low-memory build flags. The combinations are registered by `addBasicBuildingTests` ([vktRayQueryAccelerationStructuresTests.cpp:3522-L3773](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L3522-L3773)).
- The post-build operation path: copy, compact, serialize, update, and update-in-place. The combinations are registered by `addOperationTestsImpl` ([vktRayQueryAccelerationStructuresTests.cpp:3975-L4168](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L3975-L4168)).

### Acceleration-structure build types

`VkAccelerationStructureBuildTypeKHR` controls where the build happens:

- `VK_ACCELERATION_STRUCTURE_BUILD_TYPE_HOST_KHR` builds on the CPU using `vkBuildAccelerationStructureKHR`; it requires `VkPhysicalDeviceAccelerationStructureFeaturesKHR::accelerationStructureHostCommands`.
- `VK_ACCELERATION_STRUCTURE_BUILD_TYPE_DEVICE_KHR` builds on the GPU through `vkCmdBuildAccelerationStructureKHR`.

The test registers both as a build-type dimension under `flags.<residency>.<shader_source>.{cpu_built,gpu_built}` and under several other families. The chosen build type changes descriptor layouts, command-buffer encoding, and the verification flow.

### Build flags

Four flag dimensions are crossed by the `flags` group:

- `optimizationTypes`: `0`, `fasttrace` (`PREFER_FAST_TRACE`), `fastbuild` (`PREFER_FAST_BUILD`).
- `updateTypes`: `0`, `update` (`ALLOW_UPDATE_BIT_KHR`).
- `compactionTypes`: `0`, `compaction` (`ALLOW_COMPACTION_BIT_KHR`).
- `lowMemoryTypes`: `0`, `lowmemory` (`LOW_MEMORY_BIT_KHR`).

The combination is encoded into one `flags` test name like `0_0_0_0`, `fasttrace_update_compaction_lowmemory`, etc.

### Operations

`OperationType` enumerates `OP_COPY`, `OP_COMPACT`, `OP_SERIALIZE`, `OP_UPDATE`, `OP_UPDATE_IN_PLACE`. `OperationTarget` selects `OT_TOP_ACCELERATION` or `OT_BOTTOM_ACCELERATION`. The `operations` group registers all combinations that the host threading test does not restrict to `OP_COPY`/`OP_SERIALIZE`.

### Host threading

`host_threading` reuses `addOperationTestsImpl` with a non-zero `workerThreads` parameter. When that parameter is set, the matrix is restricted to host-built ASes and to `OP_COPY` / `OP_SERIALIZE` operations, both of which support Vulkan deferred operations. The test then runs both single-threaded and multi-threaded CPU builds and compares both result buffers; the case passes only when both produce the same hit/miss checkerboard ([vktRayQueryAccelerationStructuresTests.cpp:2939-L2957](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L2939-L2957)).

### Face-culling flags

`InstanceCullFlags` controls per-instance culling for triangles: `NONE`, `CULL_DISABLE`, `COUNTERCLOCKWISE` (use front-face = `gl_RayFlagsCullBackFacingTrianglesEXT` with counterclockwise winding), `ALL` (`CCW + CULL_DISABLE`). The `instance_triangle_culling` group registers all combinations with `BottomTestType::TRIANGLES`; the ray-query shader is generated with `gl_RayFlagsCullBackFacingTrianglesEXT` when `cullFlags != NONE` and `0` otherwise ([vktRayQueryAccelerationStructuresTests.cpp:1683-L1685](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L1683-L1685)).

### Dynamic descriptor indexing

`dynamic_indexing` provides one SPIR-V assembly test under each residency group. The shader builds a small `uvec2` array of TLAS device addresses plus an index buffer, and indexes the TLAS array with `nonuniformEXT(tlasIndex)` for some invocations and through a pointer dereference for others. The expected behavior is that all indexing paths produce the same checkerboard result. The shader is hand-written SPIR-V assembly because it needs to drive an SSBO-based pointer that the GLSL front-end cannot easily produce ([vktRayQueryAccelerationStructuresTests.cpp:3018-L3075](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L3018-L3075)).

### Function arguments

`function_argument` checks that an acceleration structure can be passed either as a pointer or as a bare value through a user-defined wrapper function before `rayQueryInitializeEXT`. The behavior under test is the SPIR-V lowering of an AS as a function parameter ([vktRayQueryAccelerationStructuresTests.cpp:2199-L2250](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L2199-L2250)).

### Empty ASes

`empty` covers five `EmptyAccelerationStructureCase` values: `NOT_EMPTY` (the default), `INACTIVE_TRIANGLES`, `INACTIVE_INSTANCES`, `NO_GEOMETRIES_BOTTOM` (zero `geometryCount`), `NO_PRIMITIVES_BOTTOM` (zero `primitiveCount`), `NO_PRIMITIVES_TOP`. For any non-empty case the verify path expects a checkerboard; for any empty case every cell is expected to be a miss ([vktRayQueryAccelerationStructuresTests.cpp:871-L901](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L871-L901)).

### Geometry and instances

`BottomTestType` selects between `TRIANGLES` and `AABBS`. `TopTestType` selects between `IDENTICAL_INSTANCES` (every instance references the same geometry) and `DIFFERENT_INSTANCES` (each instance transforms the same geometry). `useAOP` selects arrays-of-structures versus arrays-of-pointers for both BLAS and TLAS. These dimensions change the depth of the BVH and the construction flow but not the per-cell hit/miss pattern.

## One Concrete Example

Representative case: `dEQP-VK.ray_query.acceleration_structures.flags.traditional_structures.compute_shader.cpu_built.triangles.identical_instances.nopadding.0_0_0_0`.

The acceleration structure is built on the host; the BLAS has `BottomTestType::TRIANGLES`; the TLAS has `TopTestType::IDENTICAL_INSTANCES` (every instance references the same single geometry); no padding; no build flags set. The host builds one BLAS with one geometry (the eight-by-eight checkerboard quad `[1..width-1, 1..height-1]`) and a TLAS with multiple instances pointing at that one BLAS.

The shader, reconstructed from [`RayQueryASBasicTestCase::initPrograms`'s compute wrapper at vktRayQueryAccelerationStructuresTests.cpp:2252-L2270](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L2252-L2270) and the triangle ray-query body at [vktRayQueryAccelerationStructuresTests.cpp:1677-L1694](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L1677-L1694):

```glsl
#version 460 core
#extension GL_EXT_ray_query : require
layout(r32ui, set = 0, binding = 0) uniform uimage3D result;
layout(set = 0, binding = 1) uniform accelerationStructureEXT rqTopLevelAS;

void main()
{
    vec3  origin   = vec3(float(gl_GlobalInvocationID.x) + 0.5,
                          float(gl_GlobalInvocationID.y) + 0.5, 0.5);
    uvec4 hitValue = uvec4(0, 0, 0, 0);

    rayQueryEXT rq;
    rayQueryInitializeEXT(rq, rqTopLevelAS, 0, 0xFF, origin, 0.0, vec3(0.0, 0.0, -1.0), 1.0);
    if (rayQueryProceedEXT(rq))
    {
        if (rayQueryGetIntersectionTypeEXT(rq, false) == gl_RayQueryCandidateIntersectionTriangleEXT)
        {
            hitValue.y = 1;
            hitValue.x = 1;
        }
    }
    imageStore(result, ivec3(gl_GlobalInvocationID.xy, 0), uvec4(hitValue.x, 0, 0, 0));
    imageStore(result, ivec3(gl_GlobalInvocationID.xy, 1), uvec4(hitValue.y, 0, 0, 0));
}
```

The hit pattern from [`ComputeConfiguration::verifyImage`](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L871-L901): every cell where `(x + y) % 2 != 0` is expected to write `(1, 1)`; the rest stays at `(0, 0)`. When `emptyASCase != NOT_EMPTY`, the entire image is expected to be `(0, 0)`.

## End-to-End Test Flow

```text
[host] select residency, shader source, build type, geometry type, instance pattern, padding, four build flags, optional create-generic suffix, optional device_address_commands suffix
[host] iterate until the resulting flags.name is the leaf name
[host] checkSupport: require ray-query, acceleration-structure, ray-tracing-pipeline, host-commands (host build), sparseBinding (sparse residency); check vertex format support
[host] allocate a 3D R32_UINT result image (8x8x2) and host-visible readback buffer
[host] build TLAS (cpu_built or gpu_built). For host cases use vkBuildAccelerationStructureKHR; for device cases encode the build in a command buffer and submit
[host] if operation != OP_NONE: copy / compact / serialize / update / update-in-place the relevant AS first
[host] if workerThreads > 0: also build the AS again on N worker threads, with deferred operations enabled for COPY/SERIALIZE
[host] bind the result image (b0) and the ray-query TLAS (b1); for ray-tracing stages also bind the regular TLAS (b1) and ray-query TLAS (b2)
[host] dispatch / draw / trace; shader runs rayQueryInitializeEXT, rayQueryProceedEXT, and (for non-empty cases) updates hitValue when a triangle candidate appears
[host] vkCmdCopyImageToBuffer into the readback buffer
[host] build an 8x8x2 reference image: every (x,y) where (x+y)%2 != 0 is (1,1); for empty AS every cell is (0,0)
[host] tcu::intThresholdCompare with threshold UVec4(0). If workerThreads > 0 also compare the multi-threaded CPU-built result buffer against the same reference and require both runs to pass.
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- Inline GLSL for graphics (vert/vert_vid/tesc/tese/geom/frag), compute (`comp_*`), and ray-tracing pipeline stages (rgen/isect/ahit/chit/miss/call). The per-stage shader wrapper is selected by `m_data.shaderSourcePipeline` at [vktRayQueryAccelerationStructuresTests.cpp:1717-L2198](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L1717-L2198).
- SPIR-V assembly for `function_argument` (a wrapper-function SPIR-V file is generated at [vktRayQueryAccelerationStructuresTests.cpp:2252-L2498](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L2252-L2498)) and for `dynamic_indexing` (an SPIR-V file with `nonuniformEXT` indexing at [vktRayQueryAccelerationStructuresTests.cpp:3070-L3342](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L3070-L3342)).
- A `vk::ShaderBuildOptions` set with `SPIRV_VERSION_1_4` is used for the GLSL branches ([vktRayQueryAccelerationStructuresTests.cpp:1669](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L1669)); the SPIR-V branches use `vk::SpirVAsmBuildOptions` with the same target.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| result image (`uimage3D r32ui`, 8x8x2, b0) | yes | yes | written by `imageStore` | copied to buffer | layer 0 = committed-type `(1)`; layer 1 = candidate-found `(1)`; otherwise `(0)` |
| ray-query TLAS (b1 in compute/graphics; b2 in ray-tracing) | yes | yes | traversed | no | the AS the inline ray query traces against |
| regular TLAS (ray-tracing stages only, b1) | yes | yes | walked by `traceRayEXT` | no | drives entry into a hit shader which then issues a ray query against b2 |
| BLAS(es) referenced by TLAS instances | yes | folded into TLAS | traversed indirectly | no | source of the candidate intersections |
| result readback buffer (`TRANSFER_DST`, host-visible) | yes | yes | `vkCmdCopyImageToBuffer` writes it | yes | host scans it for `verifyImage` |

## What Is Checked

- For each generated leaf case, the shader writes per-cell `(hitValue.x, hitValue.y)`. For `emptyASCase == NOT_EMPTY` the host expects `(1,1)` at every `(x, y)` with `(x + y) % 2 != 0` and `(0,0)` elsewhere; for any other empty case every cell expects `(0,0)`. The instance passes when `tcu::intThresholdCompare` with threshold `UVec4(0)` reports no failure ([vktRayQueryAccelerationStructuresTests.cpp:682-L910](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L682-L910), [L1149-L1181](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L1149-L1181)).
- For `host_threading`, both the single-threaded build result and the multi-threaded build result must individually pass against the same reference; the case passes only when both succeed ([vktRayQueryAccelerationStructuresTests.cpp:2944-L2956](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L2944-L2956)).
- For `function_argument`, the host counts result-buffer deviations from the expected per-cell set `(2, 3, 5, 7)` and fails when any deviation appears ([vktRayQueryAccelerationStructuresTests.cpp:3503-L3515](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L3503-L3515)).
- For `instance_update`, the test re-builds the TLAS with a different number of instances and checks that the traced geometry count matches.

## Behavior Parameter Identification

> **Behavior parameter:** the `flags` sub-test's `optimizationTypes × updateTypes × compactionTypes × lowMemoryTypes × paddingType × createGenericParams × (vertex format)` matrix is the largest behavioral axis. Other families register independent axes (`operationType × operationTarget` for `operations`, `workerThreads` for `host_threading`, `function-arg-pointer-vs-bare` for `function_argument`, `cullFlags × topType × indexFormat` for `instance_triangle_culling`, `operationType` for `instance_update`, `tlasIndex` array indexing for `dynamic_indexing`, `emptyASCase` for `empty`).
>
> **Candidate values:** `flags` produces a finite set of named leaf cases encoded by `<optimization>_<update>_<compaction>_<lowMemory>[_suffix][_device_address]`; the other families each have a small fixed matrix documented in `## Behavior Parameters` of the final page.

## What Failure Means

### Failure Cause Mapping

| If this family or value fails | Possible failure cause(s) |
|--------------------------------|---------------------------|
| `flags` | BLAS or TLAS build went wrong under one or more of the build-flag combinations or feature gates (`sparseBinding`, host/gpu build, vertex formats, AOP vs AoS, AABB vs triangles, identical vs different instances). |
| `format` | A vertex or index format selected for the BLAS vertex buffer is not supported, or the format produced different geometry from the format-specific reference image. |
| `operations` (`copy` / `compaction` / `serialization`) | A copy, compact, or serialize operation produced a destination AS that traces a different hit/miss pattern from the source. |
| `host_threading` | Multi-threaded CPU build (via Vulkan deferred operations) produced a different AS than the single-threaded build, indicating a thread-safety bug in the host build or in the deferred-operation path. |
| `function_argument` | Passing an AS as a bare value (instead of a pointer) through a wrapper function misbehaved; the per-cell expected-number-of-misses count does not match. |
| `instance_triangle_culling` | The ray-query back-face culling flag (`gl_RayFlagsCullBackFacingTrianglesEXT`) plus the per-instance culling flag and per-vertex winding did not produce the expected hit pattern. |
| `instance_update` | `OP_UPDATE` or `OP_UPDATE_IN_PLACE` produced a TLAS that traverses to the wrong geometry. |
| `dynamic_indexing` | Indexing the TLAS array through `nonuniformEXT(tlasIndex)` or through an SSBO pointer produced a different hit/miss result. |
| `empty` (`NOT_EMPTY` excluded; covers all five empty cases) | An empty acceleration structure (zero geometry/primitives count, inactive triangles/instances) is not treated as empty during traversal. |

## Important Variations and Special Cases

- **Build-flag encoding.** Names like `0_0_0_0_topgeneric_device_address` chain four flag tokens and an optional create-generic suffix and a device-address suffix. The same case name appears in `[flags...].{0|fasttrace|fastbuild}.{0|update}.{0|compaction}.{0|lowmemory}[_suffix]` for padding and generic-creation axes ([vktRayQueryAccelerationStructuresTests.cpp:3701-L3706](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L3701-L3706)).
- **Sparse-binding and host-build are mutually exclusive.** The `if (buildType == HOST && residency == SPARSE_BINDING) continue;` rule appears in every group that crosses build type and residency, including `flags`, `format`, `operations`, `function_argument`, `instance_triangle_culling`, `instance_update`, `dynamic_indexing`, and `empty` ([vktRayQueryAccelerationStructuresTests.cpp:3695-L3699](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L3695-L3699) and the per-builder analogs).
- **Device-address-commands subset.** Only a small subset of `flags` cases additionally creates a `_device_address` leaf, gated on `!unboundedCreationBottom && !unboundedCreationTop && gpu_built && bottomNdx == topNdx && paddingTypeIdx == optimizationNdx && compactionNdx == lowMemoryNdx && paddingTypeIdx == lowMemoryNdx` ([vktRayQueryAccelerationStructuresTests.cpp:3746-L3756](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L3746-L3756)).
- **Operations restricted to host + COPY/SERIALIZE for host_threading.** When `workerThreads > 0`, `addOperationTestsImpl` keeps only `OP_COPY` and `OP_SERIALIZE`, and only `VK_ACCELERATION_STRUCTURE_BUILD_TYPE_HOST_KHR` builds ([vktRayQueryAccelerationStructuresTests.cpp:4098-L4111](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L4098-L4111)). Other operations are excluded because Vulkan deferred operations are well defined only for those two.
- **Dynamic-indexing uses hand-written SPIR-V.** The shader is a SPIR-V assembly source with `SPV_EXT_descriptor_indexing` and `SPV_KHR_ray_query` extensions ([vktRayQueryAccelerationStructuresTests.cpp:3070-L3075](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L3070-L3075)). The expected outcome is a specific atomic-increment pattern (`2`, `3`, `5`, `7` summed across the four `result.value[nonuniformEXT(...)]` slots) rather than the canonical checkerboard.
- **Per-stage graphics variants.** The graphics `initPrograms` path emits a `vert_vid` shader that writes `vertexIndex` as a vertex output, so that tessellation and geometry stages can index the result image by primitive ([vktRayQueryAccelerationStructuresTests.cpp:1734-L1771](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L1734-L1771)).

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Enums (`BottomTestType`, `TopTestType`, `OperationTarget`, `OperationType`, `InstanceCullFlags`, `EmptyAccelerationStructureCase`) and `TestParams` | [vktRayQueryAccelerationStructuresTests.cpp:87-L205](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L87-L205) | Defines every behavioral parameter the test crosses. |
| `RayQueryASBasicTestCase::checkSupport` | [vktRayQueryAccelerationStructuresTests.cpp:1606-L1665](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L1606-L1665) | AS feature gates, host-command gates, vertex-format support, sparse-binding check, stage-specific gates. |
| `RayQueryASBasicTestCase::initPrograms` (per-stage GLSL wrapper) | [vktRayQueryAccelerationStructuresTests.cpp:1667-L2198](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L1667-L2198) | The per-stage shader body that splices the per-`BottomTestType` ray-query fragment. |
| `RayQueryASFuncArgTestCase::initPrograms` (SPIR-V wrapper function) | [vktRayQueryAccelerationStructuresTests.cpp:2199-L2498](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L2199-L2498) | The hand-written SPIR-V that calls `rayQueryInitializeEXT` through a wrapper function taking a bare AS. |
| `RayQueryASDynamicIndexingTestCase::initPrograms` (SPIR-V with nonuniformEXT indexing) | [vktRayQueryAccelerationStructuresTests.cpp:3018-L3342](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L3018-L3342) | The hand-written SPIR-V for the dynamic-indexing test. |
| `GraphicsConfiguration::verifyImage`, `ComputeConfiguration::verifyImage`, `RayTracingConfiguration::verifyImage` | [vktRayQueryAccelerationStructuresTests.cpp:682-L690](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L682-L690), [L871-L901](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L871-L901), [L1149-L1181](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L1149-L1181) | Reference image builder per pipeline, `tcu::intThresholdCompare` checks. |
| `RayQueryASBasicTestInstance::iterateNoWorkers` / `iterateWithWorkers` | [vktRayQueryAccelerationStructuresTests.cpp:2929-L2971](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L2929-L2971) | The host's per-thread orchestration, including the multi-threaded deferred-operation path. |
| `addBasicBuildingTests` | [vktRayQueryAccelerationStructuresTests.cpp:3522-L3773](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L3522-L3773) | Registers `flags`. |
| `addVertexIndexFormatsTests` | [vktRayQueryAccelerationStructuresTests.cpp:3776-L3972](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L3776-L3972) | Registers `format`. |
| `addOperationTestsImpl` and `addOperationTests` | [vktRayQueryAccelerationStructuresTests.cpp:3975-L4174](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L3975-L4174) | Registers `operations` (and is reused by `host_threading`). |
| `addHostThreadingOperationTests` | [vktRayQueryAccelerationStructuresTests.cpp:4176-L4190](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L4176-L4190) | Adds thread-count groups `1`, `2`, `3`, `4`, `8`, `max` to `host_threading`. |
| `addFuncArgTests` | [vktRayQueryAccelerationStructuresTests.cpp:4193-L4263](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L4193-L4263) | Registers `function_argument`. |
| `addInstanceTriangleCullingTests` | [vktRayQueryAccelerationStructuresTests.cpp:4266-L4448](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L4266-L4448) | Registers `instance_triangle_culling`. |
| `addInstanceUpdateTests` | [vktRayQueryAccelerationStructuresTests.cpp:4450-L4538](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L4450-L4538) | Registers `instance_update`. |
| `addDynamicIndexingTests` | [vktRayQueryAccelerationStructuresTests.cpp:4540-L4570](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L4540-L4570) | Registers `dynamic_indexing`. |
| `addEmptyAccelerationStructureTests` | [vktRayQueryAccelerationStructuresTests.cpp:4572-L4742](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L4572-L4742) | Registers `empty` with five empty-AS cases. |
| `createAccelerationStructuresTests` | [vktRayQueryAccelerationStructuresTests.cpp:4744-L4768](../../../modules/vulkan/ray_query/vktRayQueryAccelerationStructuresTests.cpp#L4744-L4768) | Top-level registration. |
| Vulkan spec: acceleration structures | `external/vulkan-docs/src/chapters/accelstructures.adoc` | TLAS/BLAS split; build types, build flags, copy/compact/serialize. Not vendored in this checkout. |

## Questions / Risk Points for User Audit

- The build-flag matrix has many thousands of leaves; this page treats the `flags` matrix structurally rather than enumerating leaves. Is that the right level of abstraction, or should the page list the four flag values and their combinations explicitly?
- The brief uses TLAS/BLAS definitions from the Khronos reference manual rather than from the vendored spec (because `external/vulkan-docs` is not present). Should the final page also cite spec lines, or leave the prose grounded in CTS-source observations and the public reference?
- For the empty-AS family, the brief groups all five cases under one cause ("An empty acceleration structure is not treated as empty"). Would it be clearer to split into the five cases, with a per-case failure symptom?
- For dynamic indexing, the expected outcome is a specific atomic-add pattern (`2 + 3 + 5 + 7` summed over four buffer slots) rather than the checkerboard. The page should preserve this detail because it is the only output the case checks.
- The representative walkthrough path was selected from `flags`, not from `dynamic_indexing` or `function_argument`, because those use SPIR-V assembly instead of generated GLSL. If a SPIR-V walkthrough would be more distinctive for the page, that path can be added as a second walkthrough.

## Conversion Notes for Final Wiki Rewrite

- Carry `## Behavior Parameter Identification` into `## Behavior Parameters`. The page should have one subsection per family because each family defines a distinct axis.
- Carry `### Failure Cause Mapping` into the page's `### Failure Cause Mapping` verbatim.
- Distill `## Background Knowledge` into the page's `## Background Knowledge` list without beginner scaffolding. Use Vulkan/CTS terms directly.
- The shader walkthrough should use the `flags.traditional_structures.compute_shader.cpu_built.triangles.identical_instances.nopadding.0_0_0_0` case (or another simple leaf from `flags`) because that path uses generated GLSL and supports `shader-analyzer` cleanly.
- Move the full operations dimension and per-stage verification matrix to `## Runtime Execution and Result Checking` as compact tables; this keeps `## Failure Meaning` focused.
- The dispatch verification for `host_threading` is unique to that family; it deserves its own short note inside `## Runtime Execution and Result Checking`.
