## Overview

**Core question:** Do acceleration structures built on the GPU, on the CPU single-threaded, or on the CPU through `VK_KHR_deferred_host_operations` with a varying number of host worker threads all produce the same correct ray tracing hit/miss pattern?

- [vktRayTracingBuildTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp) implements the single test family `build` under the `ray_tracing_pipeline` test category.
- All leaves share one scene, one ray tracing pipeline, and one rgen/any-hit/miss/intersection shader set. What varies is the acceleration structure build path: device-side build (`gpu`), host-side single-threaded build (`cpu`), or host-side build deferred across N host worker threads (`cpuht_1` through `cpuht_max`).
- Each leaf builds a bottom-level/top-level acceleration structure pair on the selected path, traces one ray per pixel straight down the -z axis, and compares the resulting per-pixel hit/miss values against an expected pattern derived from geometry placement.
- The page explains the build-path axis, the AS-level scaling matrix, the AABB expansion tolerance in the result check, and what a failure of each build path points to.

## Background Knowledge

- **Acceleration structure build types.** `VK_KHR_acceleration_structure` defines `VK_ACCELERATION_STRUCTURE_BUILD_TYPE_DEVICE_KHR` (build recorded and executed on the device via command buffer) and `VK_ACCELERATION_STRUCTURE_BUILD_TYPE_HOST_KHR` (build performed by the host). The build type selects where the build work runs, not the resulting traversal semantics.
- **Deferred host operations.** `VK_KHR_deferred_host_operations` lets a host-side AS build be split across multiple host threads. The implementation partitions the build work and joins the worker threads. The `cpuht_N` leaves request N worker threads; `cpuht_max` requests `UINT32_MAX`, which the implementation maps to its own preferred thread count. A non-zero thread count is what turns a plain host build into a deferred host build.
- **Acceleration structure levels.** A bottom-level acceleration structure (BLAS) holds geometry (triangles or AABBs). A top-level acceleration structure (TLAS) holds instances that reference BLAS. The `level_*` intermediate nodes scale the count at exactly one of those three levels while holding the others small.
- **AABB expansion.** The Vulkan spec permits implementations to expand AABB geometries in an acceleration structure to mitigate precision issues, which can produce false-positive intersection reports. The test's result check tolerates this for AABB and mixed geometry types.

## Registration Hierarchy

```text
ray_tracing_pipeline.build
├── cpu
├── cpuht_1
├── cpuht_2
├── cpuht_3
├── cpuht_4
├── cpuht_8
├── cpuht_max
└── gpu
```

The eight direct children are registered by [createBuildTests](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L753-L798). Each child corresponds to one `(threadCount, deviceBuild)` pair: `gpu` is the only device-build child (`threadCount == 0, deviceBuild == true`); `cpu` is the host single-threaded child (`threadCount == 0, deviceBuild == false`); the `cpuht_*` children are host deferred-operation children with the named worker-thread count.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| AS build path | `gpu`, `cpu`, `cpuht_1`, `cpuht_2`, `cpuht_3`, `cpuht_4`, `cpuht_8`, `cpuht_max` | Selects the acceleration structure build type and, for host builds, the deferred-host worker-thread count. This is the primary behavioral axis. | [createBuildTests](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L753-L798) |
| AS scaling level | `level_primitives`, `level_geometries`, `level_instances` | Selects which AS level receives the large count: primitives per geometry, geometries per BLAS, or instances per TLAS. The other two levels stay at the small factor. | [buildTest tests array](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L643-L644) |
| Geometry type | `triangles`, `aabbs`, `mixed` | Selects BLAS geometry: triangle geometry only, AABB geometry only, or alternating triangle/AABB per instance. Mixed requires at least two instances so both types appear. | [TestType enum](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L61-L66) |
| Size | `4`, `16`, `64`, `256`, `1024` | Base image and grid dimension squared. Drives the largest-group count as `size*size/factor/factor`. Device builds skip sizes above 256. | [buildTest sizes array](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L644) |
| Factor | `1`, `4` | Inverse scaling: the large level gets `size*size/factor/factor`, the other two levels get `factor`. | [buildTest factors array](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L645) |
| SPIR-V target | `spirv1.4` | All generated shaders use `vk::SPIRV_VERSION_1_4`. | [ShaderBuildOptions](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L213) |

The test case leaf name encodes the geometry type and the three group counts as `triangles_<instances>_<geometries>_<squares>` (and likewise for `aabbs_`, `mixed_`), so the leaf name directly records the scaling configuration.

## Behavior Parameters

The primary behavioral axis is the acceleration structure build path. Each value is a direct child of `ray_tracing_pipeline.build` and selects a different `VK_ACCELERATION_STRUCTURE_BUILD_TYPE_KHR` and worker-thread configuration. The scene, shaders, and result check are identical across all values.

### gpu - device-side acceleration structure build

Builds both BLAS and TLAS with `VK_ACCELERATION_STRUCTURE_BUILD_TYPE_DEVICE_KHR`. The build is recorded into the command buffer via `cmdBuildAccelerationStructuresKHR` and executed on the device before the trace. This path never uses deferred host operations and requires no `VK_KHR_deferred_host_operations`. It is the baseline device path: if it fails, the device-side AS build or the shared trace pipeline is suspect. Device builds skip sizes above 256, so the `gpu` matrix is smaller than the `cpu`/`cpuht_*` matrices.

### cpu - host single-threaded acceleration structure build

Builds both BLAS and TLAS with `VK_ACCELERATION_STRUCTURE_BUILD_TYPE_HOST_KHR` and `workerThreadsCount == 0`, so deferred operation is disabled. The build runs entirely on the calling host thread. This path requires `accelerationStructureHostCommands` support. It is the baseline host path against which the deferred-threaded paths are compared.

### cpuht_1 through cpuht_max - host deferred-operation builds with N worker threads

Builds both BLAS and TLAS with `VK_ACCELERATION_STRUCTURE_BUILD_TYPE_HOST_KHR` and `deferredOperation == true`, requesting the named worker-thread count. `cpuht_1` through `cpuht_8` request 1, 2, 3, 4, and 8 threads respectively; `cpuht_max` requests `UINT32_MAX`, which the implementation resolves to its preferred thread count. This path requires both `VK_KHR_deferred_host_operations` and `accelerationStructureHostCommands`. It exercises whether the implementation correctly partitions the host build across worker threads and joins them before the trace. The AS data and expected results are identical to `cpu`; only the threading of the build differs.

## Shader Analysis

Shader code is not part of the tested behavior. The rgen, any-hit, miss, and intersection shaders are a fixed probe identical across all build-path and scaling leaves; they produce a per-pixel hit/miss value that the host compares against the expected pattern. The rgen shader is the shared [getCommonRayGenerationShader](../../../framework/vulkan/vkRayTracingUtil.cpp#L118-L138) helper, which traces one ray per launch ID straight down the -z axis into the TLAS. The any-hit shader writes `1` to the result image, the miss shader writes `2`, and the intersection shader reports an intersection for AABB geometry. No shader text varies with the build path or the AS scaling level, so no representative shader walkthrough is needed.

## Runtime Execution and Result Checking

### Scene construction

- The host builds a set of BLAS, one per instance. Each BLAS holds `geometriesGroupCount` geometries, and each geometry holds `squaresGroupCount` primitives. Each primitive covers one pixel cell of the `width x height` image. A deterministic walk (`startPos` advanced by `(n+13) % (width*height)`) places each primitive at a cell whose linear index `n` determines its z-face sign [initBottomAccelerationStructure](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L305-L351).
- Triangle primitives use three vertices per cell; AABB primitives use two opposite corners [geometryData fill](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L316-L343). The `mixed` type alternates triangle and AABB per instance [triangles flag](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L281-L282).
- A TLAS instances all BLAS with identity transforms. The instance SBT record offset is 0 for triangle instances and 1 for AABB instances, selecting the hit group with the intersection shader for AABBs [initTopAccelerationStructure](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L268-L290).

### Build path execution

- The `buildTest` registration passes the case's `deviceBuild` and `workerThreadsCount` into the `CaseDef`, and the instance's `runTest` uses those to set the build type and deferred-operation mode on every BLAS and the TLAS [runTest build setup](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L408-L528).
- BLAS are built through a `BottomLevelAccelerationStructurePool` that batches creation and build to stay under the device's `maxMemoryAllocationCount`. For host builds, the watchdog interval time limit is disabled around the BLAS batch build to avoid timeouts on low-clocked CPUs, then re-enabled [watchdog disable/enable](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L504-L516).
- The TLAS is created and built inside the command buffer for device builds, or on the host for host builds [createTopAccelerationStructure](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L292-L303).

### Trace and result copyback

- The result image is a 2D `r32ui` storage image sized to `width x height`. It is cleared to `(5,5,5,255)` and transitioned to `GENERAL` before the trace [image setup](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L466-L496).
- `cmdTraceRays` launches `width x height x 1` rays. Each raygen invocation traces one ray down -z into the TLAS; the any-hit or miss shader writes the per-pixel result into the image [trace dispatch](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L549-L550).
- After the trace, a `SHADER_WRITE` -> `TRANSFER_READ` barrier, `cmdCopyImageToBuffer`, and a `TRANSFER_WRITE` -> `HOST_READ` barrier move the image into a host-visible buffer [copyback](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L552-L565).

### Per-pixel result check

- The host scans every pixel. The expected value is `1` (any-hit) for cells whose linear index `n` is not divisible by 7, and `2` (miss) for cells where `n % 7 == 0` [validateBuffer](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L589-L627). The `n % 7 == 0` cells have z-face sign `+1`; the deterministic placement arranges them to miss the downward ray, while all other cells present a z `-1` face that the ray hits.
- For `triangles` geometry, a mismatched pixel always counts as a failure. For `aabbs` and `mixed` geometry, a mismatched pixel is only a failure if the observed value is not the any-hit value `1`; this tolerates implementation AABB expansion that reports a hit where the test expected a miss [AABB tolerance](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L606-L616).
- Pass condition: `failures == 0` [iterate](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L629-L637).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `gpu` | Device-side AS build (BLAS/TLAS) did not produce a structure that traverses to the expected hit/miss pattern, or the device build path's shared trace pipeline or SBT is broken. |
| `cpu` | Host single-threaded AS build did not produce a correct structure, or `accelerationStructureHostCommands` host build path has a correctness bug independent of threading. |
| `cpuht_1` through `cpuht_8` | Host deferred-operation build with the named worker-thread count did not produce a correct structure, pointing at deferred-operation work partitioning or thread-join synchronization for that thread count. |
| `cpuht_max` | Host deferred-operation build with the implementation's preferred (max) thread count did not produce a correct structure, pointing at deferred-operation scaling to many threads. |

All leaves share the scene construction, the trace pipeline, and the per-pixel result check, so a failure common to all build-path values points at shared infrastructure (geometry data, TLAS instance setup, SBT, image copyback, expected-value rule) rather than a build-path-specific issue.

### Cause Analysis

#### Device-side build correctness failure

**Possible failure symptoms:** A `gpu` leaf failure where the corresponding `cpu` leaf with the same scaling and geometry type passes. The result image has mismatched pixels: cells that should be `1` (hit) are `2` (miss) or the clear value, or vice versa, and the failure count is nonzero.

**Possible implementation causes:** The `gpu` path records the BLAS and TLAS builds into the command buffer and the device executes them. The traversal result depends on the device-built structure matching the host-built one. A grounded investigation should check whether the device build completed and was made visible to the trace (the build and trace are in the same command buffer), whether the BLAS geometry data uploaded to device buffers matches the host-side geometry used to compute expected values, and whether the TLAS instance SBT record offsets were set correctly for the device build. If `gpu` and `cpu` both fail at the same scaling, the cause is shared infrastructure, not the device build path. If only `gpu` fails and the host path passes, source-level investigation is needed.

#### Host single-threaded build correctness failure

**Possible failure symptoms:** A `cpu` leaf failure where the corresponding `gpu` leaf passes, or where `cpu` and all `cpuht_*` leaves fail together. Mismatched pixels in the result image with a nonzero failure count.

**Possible implementation causes:** The `cpu` path builds BLAS and TLAS on the host with `VK_ACCELERATION_STRUCTURE_BUILD_TYPE_HOST_KHR` and deferred operation disabled. It requires the `accelerationStructureHostCommands` feature. A grounded investigation should check whether the host build respected the same geometry data and instance configuration as the device path, and whether the host-built structure was made available to the device trace (the host-built TLAS handle is bound via the descriptor set before the trace). The spec ties host builds to `accelerationStructureHostCommands`; if that feature is reported but the host build is broken, the cause is in the host build implementation. If `cpu` passes but a `cpuht_*` leaf fails, the cause is deferred-operation-specific.

#### Deferred-host-operation threading failure

**Possible failure symptoms:** A `cpuht_N` or `cpuht_max` leaf failure where the `cpu` leaf with the same scaling and geometry type passes. Mismatched pixels with a nonzero failure count. The failure may appear only for specific thread counts.

**Possible implementation causes:** The `cpuht_*` paths enable deferred operation and request N worker threads. The implementation must partition the host build across the worker threads and join them so the completed structure is visible before the trace. A grounded investigation should check whether the deferred-operation join completed for the failing thread count, whether the partitioning produced a structure equivalent to the single-threaded build, and whether any per-thread scratch or allocation state leaked between threads. The spec states deferred host operations may be concurrent and the implementation must complete them before returning. If only some thread counts fail, the cause is thread-count-specific partitioning or join logic, and source-level investigation of the deferred-operation join path is needed.

#### Shared infrastructure failure

**Possible failure symptoms:** All build-path values for a given scaling and geometry type fail with the same pixel pattern, regardless of whether the build ran on the device, the host, or the host with threads.

**Possible implementation causes:** The scene construction, trace pipeline, SBT, result image clear and copyback, and the expected-value rule are identical across all build paths. A failure common to all paths points at this shared setup. A grounded investigation should check whether the deterministic primitive placement walk produced the expected z-face signs (the `n % 7 == 0` miss cells), whether the TLAS instance SBT record offsets match the hit-group layout, whether the rgen ray direction and tmax actually reach the geometry, and whether the per-pixel expected-value rule in `validateBuffer` matches the geometry placement. For `mixed` geometry, check that the AABB-expansion tolerance is applied correctly. Source-level inspection of `initBottomAccelerationStructure` and `validateBuffer` is needed to confirm the placement and expected-value correspondence.

## Case Pruning

### Requirement-based pruning

- All leaves require `VK_KHR_acceleration_structure` and `VK_KHR_ray_tracing_pipeline`, with the `rayTracingPipeline` and `accelerationStructure` feature bits set. If `accelerationStructure` is not set, the test throws `TestError` [checkSupport](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L186-L205).
- Host builds (`cpu` and all `cpuht_*`) additionally require `VK_KHR_deferred_host_operations` and `accelerationStructureHostCommands`; otherwise the test throws `NotSupportedError` [host build feature gate](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L202-L208). The `gpu` path does not require these.
- At instance time, the test checks ray tracing property limits: `maxPrimitiveCount`, `maxGeometryCount`, and `maxInstanceCount` must each cover the case's group counts, and the estimated memory allocation count (plus a 120-allocation margin) must stay under `maxMemoryAllocationCount`. Any shortfall throws `NotSupportedError` [checkSupportInInstance](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L570-L587).

### Design-based pruning

- Device builds skip sizes above 256 (`if (deviceBuild && sizes[sizesNdx] > 256) continue`), so the `gpu` matrix omits the 1024 size. This keeps device build time and scratch within practical limits [device size skip](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L656-L657).
- Cases where any group count would be zero are skipped (`squaresGroupCount == 0 || geometriesGroupCount == 0 || instancesGroupCount == 0`) [zero-count skip](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L679-L680).
- `mixed` geometry requires at least two instances, two geometries, and two squares per geometry, so that both triangle and AABB types actually appear. This is enforced by a stricter skip condition for the mixed loop [mixed minimum skip](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L743-L744).
- `workerThreadsCount` and `deviceBuild` are mutually exclusive: the registration asserts `!(threadCount != 0 && deviceBuild)`, so only the `gpu` child uses the device build and only the `cpu`/`cpuht_*` children use host builds [mutual exclusion assert](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L764).

## Key Takeaways

- The `build` family isolates the acceleration structure build path as the behavioral axis: device build (`gpu`), host single-threaded build (`cpu`), and host deferred-operation build with 1, 2, 3, 4, 8, or max worker threads (`cpuht_*`). The scene, shaders, and result check are identical across all paths.
- The `level_*` intermediate nodes and the size/factor matrix scale the AS at one level at a time, exercising large primitive counts, large geometry counts, and large instance counts against the implementation's property limits.
- The result check compares a deterministic hit/miss pattern derived from geometry placement; for AABB and mixed geometry it tolerates implementation AABB expansion that produces an extra hit, but not a miss where a hit was expected.
- A failure isolated to one build path points at that path's build or synchronization correctness; a failure common to all paths points at shared scene, pipeline, or check infrastructure. See `## Failure Meaning` for the per-path cause analysis.
- The host deferred-operation paths specifically test work partitioning and thread join correctness across the supported worker-thread counts, including the implementation-chosen max count.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `TestType` enum | [vktRayTracingBuildTests.cpp#L61-L66](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L61-L66) | Defines triangles, aabbs, mixed geometry types |
| `CaseDef` struct | [vktRayTracingBuildTests.cpp#L68-L79](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L68-L79) | Per-case parameters including build path and worker-thread count |
| `checkSupport` | [vktRayTracingBuildTests.cpp#L186-L205](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L186-L205) | Feature gates for acceleration structure, ray tracing pipeline, deferred host operations |
| `initPrograms` (ahit/miss/sect/rgen) | [vktRayTracingBuildTests.cpp#L211-L261](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L211-L261) | The fixed probe shaders, including the shared rgen helper |
| `initBottomAccelerationStructure` | [vktRayTracingBuildTests.cpp#L305-L351](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L305-L351) | Deterministic primitive placement and z-face sign rule |
| `initTopAccelerationStructure` | [vktRayTracingBuildTests.cpp#L268-L290](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L268-L290) | TLAS instance setup and SBT record offset selection |
| `runTest` | [vktRayTracingBuildTests.cpp#L408-L568](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L408-L568) | Build path execution, trace dispatch, and result copyback |
| `checkSupportInInstance` | [vktRayTracingBuildTests.cpp#L570-L587](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L570-L587) | Runtime property-limit and allocation-count pruning |
| `validateBuffer` | [vktRayTracingBuildTests.cpp#L589-L627](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L589-L627) | Per-pixel expected-value rule and AABB-expansion tolerance |
| `iterate` | [vktRayTracingBuildTests.cpp#L629-L637](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L629-L637) | Pass/fail condition |
| `buildTest` | [vktRayTracingBuildTests.cpp#L641-L751](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L641-L751) | Scaling-level, geometry-type, size, and factor matrix generation |
| `createBuildTests` | [vktRayTracingBuildTests.cpp#L753-L798](../../../modules/vulkan/ray_tracing/vktRayTracingBuildTests.cpp#L753-L798) | Registration of the eight build-path direct children |
| shared rgen shader helper | [vkRayTracingUtil.cpp#L118-L138](../../../framework/vulkan/vkRayTracingUtil.cpp#L118-L138) | Common ray generation shader tracing one ray per launch ID down -z |
