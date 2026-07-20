# Understanding Brief: ray_tracing_pipeline.position_fetch

## One-Sentence Test Purpose

This test checks whether `gl_HitTriangleVertexPositionsEXT` returns the spec-required object-space vertex positions of the hit triangle for ray tracing pipeline hit shaders, across host and device acceleration structure builds, 15 vertex formats, and an optional non-identity instance transform.

## Background Knowledge

### VK_KHR_ray_tracing_position_fetch

The `VK_KHR_ray_tracing_position_fetch` extension adds the `HitTriangleVertexPositionsKHR` built-in (GLSL `gl_HitTriangleVertexPositionsEXT`), an array of three `vec3` values available in any-hit and closest-hit shaders. The positions are the object-space vertex coordinates of the hit primitive, taken from the bottom-level acceleration structure geometry. Instance transforms applied to the top-level acceleration structure do not affect these positions; the values returned are the unmodified object-space vertices.

Why it matters here:
- The test gates on `VkPhysicalDeviceRayTracingPositionFetchFeaturesKHR::rayTracingPositionFetch` and throws `NotSupportedError` when the feature bit is false.
- The bottom-level acceleration structure is built with `VK_BUILD_ACCELERATION_STRUCTURE_ALLOW_DATA_ACCESS_KHR`, which the spec requires to make position fetch data available to shaders.
- The `instance_transform` flag mask applies a non-identity instance matrix with diagonal `(0.98, 0.97, 0.99)`. Because the expected output positions are the unmodified triangle vertices, this flag specifically verifies that the implementation returns object-space, not world-space, positions.

### Acceleration structure build type

`VK_KHR_acceleration_structure` allows building the acceleration structure on the host (`VK_ACCELERATION_STRUCTURE_BUILD_TYPE_HOST_KHR`) or on the device (`VK_ACCELERATION_STRUCTURE_BUILD_TYPE_DEVICE_KHR`). The two paths use different build entry points and may store geometry data differently. Position fetch must work for both, so the test registers `cpu_built` and `gpu_built` direct children under `position_fetch`.

### Vertex format coverage

The acceleration structure vertex buffer may use any format supported by `VK_KHR_acceleration_structure` for triangle geometry. The test exercises 15 formats spanning `r8g8*snorm`, `r16g16*snorm`, `r16g16*sfloat`, `r32g32*sfloat`, and `r64g64*sfloat` families. The implementation must decode each format consistently between the AS build and the position fetch readback.

## One Concrete Example

Take the case `dEQP-VK.ray_tracing_pipeline.position_fetch.gpu_built.r32g32b32_sfloat.instance_transform`:

- The host creates one bottom-level AS with four geometries, each containing four triangles. Only the triangle at `(chosenGeom, chosenTri)` is placed at `z = 0`. The other 15 triangles sit at `z = 10 + N`, so the ray (origin `(0.25, 0.25, 1.0)`, direction `(0, 0, -1)`) only hits the chosen one.
- The top-level AS has one instance referencing the BLAS, transformed by the non-identity matrix with diagonal `(0.98, 0.97, 0.99)`.
- The raygen shader traces one ray against the top-level AS.
- The any-hit shader writes `gl_HitTriangleVertexPositionsEXT[0..2]` to even-indexed output slots and calls `terminateRayEXT`.
- The closest-hit shader writes the same three positions to odd-indexed output slots.
- The host expects all six output positions to equal the original triangle vertices `(0,0,0)`, `(1,0,0)`, `(0,1,0)`, within a squared-difference tolerance of `1e-5`.

This single case exercises position fetch through both hit shaders, the multi-geometry selection logic, the instance-transform object-space requirement, and the `r32g32b32_sfloat` format decoding path.

## End-to-End Test Flow

```text
[host] choose buildType, vertexFormat, testFlagMask from registered case parameters
[host] derive seed from (buildType, vertexFormat, testFlagMask); seed picks chosenGeom and chosenTri when multipleTriangles is true
[host] build bottom-level AS with 1 or 4 geometries; each geometry has 1 or 4 triangles; only chosen triangle at z=0, rest at z=10+N; build flag ALLOW_DATA_ACCESS_KHR; build on host or device per buildType
[host] build top-level AS with 1 instance; instance transform is non-identity when INSTANCE_TRANSFORM flag is set, identity otherwise
[host] allocate origins buffer (1 vec4) with (0.25, 0.25, 1.0, 0.0); allocate output positions buffer (6 vec4), cleared to 0xFF
[host] build ray tracing pipeline with rgen, miss, and geometryCount hit groups (each hit group has ah + ch)
[host] build shader binding tables for raygen, miss, and hit groups
[host] vkCmdTraceRaysKHR with numRays=1
[device] rgen: traceRayEXT from origin along (0,0,-1)
[device] traversal: hit chosen triangle at z=0
[device] any-hit: write gl_HitTriangleVertexPositionsEXT[0..2] to even slots, then terminateRayEXT
[device] closest-hit: write gl_HitTriangleVertexPositionsEXT[0..2] to odd slots
[host] pipeline barrier: SHADER_WRITE -> HOST_READ
[host] invalidate output allocation, read back 6 vec4 values
[host] for each of 6 expected positions, compute dot(expected - actual, expected - actual); fail if >= 1e-5
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The test generates four GLSL shader strings in `PositionFetchCase::initPrograms`:

- `rgen`: raygen shader. Declares `layout(location=0) rayPayloadEXT int value`, the three descriptor bindings, and traces one ray from `origins.values[gl_LaunchIDEXT.x].xyz` along `(0,0,-1)` with `tMin=0`, `tMax=2`.
- `miss`: miss shader. Writes the sentinel `vec4(123.0, 456.0, 789.0, 0.0)` to all six output slots for the current launch id, so a miss forces a validation failure.
- `ah`: any-hit shader. Writes `gl_HitTriangleVertexPositionsEXT[i]` to `modes.values[6*gl_LaunchIDEXT.x + 2*i]` for `i=0..2`, then calls `terminateRayEXT`.
- `ch`: closest-hit shader. Writes `gl_HitTriangleVertexPositionsEXT[i]` to `modes.values[6*gl_LaunchIDEXT.x + 2*i + 1]` for `i=0..2`.

All four shaders use `#extension GL_EXT_ray_tracing : require` and `#extension GL_EXT_ray_tracing_position_fetch : require`. The shaders are identical across all 60 cases; only host-side AS construction and parameter setup vary.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `topLevelAS` (binding 0, acceleration structure) | yes | yes (descriptor set binding 0) | read by rgen traceRayEXT | no | Traversal input; carries instance transform when flag is set |
| `origins` (binding 1, SSBO, 1 vec4) | yes, filled with (0.25, 0.25, 1.0, 0.0) | yes (descriptor set binding 1) | read by rgen | no | Ray origin for traceRayEXT |
| `modes` (binding 2, SSBO, 6 vec4) | yes, cleared to 0xFF | yes (descriptor set binding 2) | written by ah, ch, miss | yes, after barrier and invalidate | Holds the six fetched positions; host validates against expected triangle vertices |
| Bottom-level AS | yes, built with ALLOW_DATA_ACCESS_KHR | used internally by traversal | read by traversal and position fetch | no | Stores triangle geometry in the format under test; ALLOW_DATA_ACCESS_KHR is required for position fetch |

## What Is Checked

- The host reads six `vec4` output values from `modes` after invalidating the allocation.
- For each output `i`, the host computes `diff = expectedOutputPositions[i] - outVec3` and `len = dot(diff, diff)`.
- Pass condition: `len < 1e-5` for all six entries.
- The expected values are the original triangle vertices `(0,0,0)`, `(1,0,0)`, `(0,1,0)`, each appearing twice (once from AH, once from CH), regardless of the instance transform or vertex format.
- The check is performed per-case; there is no aggregation across cases.

## Behavior Parameter Identification

> **Behavior parameter:** `buildType` (the direct child of `position_fetch`)
>
> **Candidate values:** `cpu_built`, `gpu_built`

The build type is the primary behavioral axis because it is the only registered dimension that selects a different implementation code path for the acceleration structure build. The vertex format and flag mask are configuration dimensions: they change how geometry is stored and whether an instance transform is applied, but the property under test (position fetch returns object-space vertices) is the same.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `cpu_built` | The host-build acceleration structure path stored geometry in a form that position fetch cannot read back, the host build did not honor `ALLOW_DATA_ACCESS_KHR`, or position fetch returned wrong object-space vertices for host-built AS. Format-specific decoding failures also surface here. |
| `gpu_built` | The device-build acceleration structure path stored geometry in a form that position fetch cannot read back, the device build did not honor `ALLOW_DATA_ACCESS_KHR`, or position fetch returned wrong object-space vertices for device-built AS. |

Both build types share the shader code, descriptor setup, ray origin, expected-value computation, and host comparison loop. A failure common to both build types points at shared infrastructure: the position fetch built-in implementation, vertex format decoding, instance-transform object-space handling, or the host validation logic.

## Important Variations and Special Cases

- **`multipleTriangles` path.** When the vertex format has at least three used channels and is `sfloat` (6 of 15 formats), the test builds four geometries with four triangles each. Only one triangle sits at `z=0`; the other 15 sit at `z=10+N`. This exercises multi-geometry selection and ensures position fetch returns the correct triangle's vertices, not a neighbor's. The seed-derived `chosenGeom` and `chosenTri` make the choice deterministic per case.
- **`instance_transform` flag mask.** The non-identity instance matrix has diagonal `(0.98, 0.97, 0.99)`. The expected output remains the original triangle vertices, so this flag specifically tests that position fetch returns object-space, not world-space, positions.
- **`NoFlags` flag mask.** The instance matrix is identity. Position fetch should still return the original vertices; this is the baseline.
- **Hit group count.** The pipeline registers `geometryCount` hit groups (1 or 4). When `multipleTriangles` is true, four hit groups exist even though only one geometry contains the hit triangle. The shader binding table must be sized accordingly.
- **Miss sentinel.** The miss shader writes `(123, 456, 789, 0)` to all six slots. If the ray misses (for example because the chosen triangle was not actually at `z=0`), the sentinel values fail the `1e-5` tolerance check immediately.
- **`r64g64*sfloat` formats.** These 64-bit float formats are not mandatory; the test includes them as additional formats and gates them through `checkAccelerationStructureVertexBufferFormat` in `checkSupport`.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| `TestParams` and `TestFlagBits` | [vktRayTracingPositionFetchTests.cpp#L55-L75](../../../modules/vulkan/ray_tracing/vktRayTracingPositionFetchTests.cpp#L55-L75) | Defines the per-case parameter struct, flag bits, and the seed derivation. |
| `checkSupport` | [vktRayTracingPositionFetchTests.cpp#L113-L138](../../../modules/vulkan/ray_tracing/vktRayTracingPositionFetchTests.cpp#L113-L138) | Gates on the three KHR extensions, the position-fetch feature bit, host-commands for CPU build, and vertex format support. |
| `initPrograms` | [vktRayTracingPositionFetchTests.cpp#L140-L223](../../../modules/vulkan/ray_tracing/vktRayTracingPositionFetchTests.cpp#L140-L223) | Generates the rgen, miss, ah, and ch shader strings. Identical for all 60 cases. |
| `iterate` AS build | [vktRayTracingPositionFetchTests.cpp#L236-L324](../../../modules/vulkan/ray_tracing/vktRayTracingPositionFetchTests.cpp#L236-L324) | Builds BLAS with 1 or 4 geometries, sets ALLOW_DATA_ACCESS_KHR, applies instance transform, builds TLAS. |
| `iterate` pipeline and trace | [vktRayTracingPositionFetchTests.cpp#L416-L480](../../../modules/vulkan/ray_tracing/vktRayTracingPositionFetchTests.cpp#L416-L480) | Builds pipeline with geometryCount hit groups, dispatches vkCmdTraceRaysKHR with numRays=1. |
| `iterate` verification | [vktRayTracingPositionFetchTests.cpp#L490-L522](../../../modules/vulkan/ray_tracing/vktRayTracingPositionFetchTests.cpp#L490-L522) | Reads back 6 vec4, compares with dot(diff,diff) < 1e-5 tolerance. |
| `createPositionFetchTests` registration | [vktRayTracingPositionFetchTests.cpp#L529-L609](../../../modules/vulkan/ray_tracing/vktRayTracingPositionFetchTests.cpp#L529-L609) | Registers cpu_built/gpu_built, 15 vertex formats, and NoFlags/instance_transform leaves. |
| Category dispatcher | [vktRayTracingTests.cpp#L98](../../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L98) | Adds `position_fetch` to the `ray_tracing_pipeline` test category. |
| Mustpass evidence | [ray-tracing-pipeline.txt](../../../mustpass/main/vk-default/ray-tracing-pipeline.txt) | All 60 leaves listed in the default ray-tracing-pipeline mustpass. |

## Questions / Risk Points for User Audit

- Is the build type the correct primary behavioral axis, or should the flag mask (NoFlags vs instance_transform) be treated as a co-equal axis because it tests the object-space requirement specifically?
- Is the `1e-5` squared-difference tolerance correctly described as a squared-difference check, not an absolute-value check?
- Is the multi-geometry path correctly attributed only to the 6 sfloat formats with 3+ used channels?
- Are the r64g64*sfloat formats correctly described as additional (non-mandatory) formats?

## Conversion Notes for Final Wiki Rewrite

- The representative shader walkthrough should use the any-hit shader from `gpu_built.r32g32b32_sfloat.instance_transform` because that case exercises the multi-geometry path, the instance-transform object-space requirement, and the any-hit position fetch plus `terminateRayEXT` in a single case. The rgen and ch GLSL should be shown for context, but only the ah SPIR-V needs to be inlined as the primary walkthrough.
- The brief's `### Failure Cause Mapping` table should be copied directly into the final page's `### Failure Cause Mapping`.
- The `buildType` axis should drive `## Behavior Parameters` with `### cpu_built` and `### gpu_built` subsections.
- The vertex format and flag mask dimensions belong in `## Parameter Dimensions and Observed Values`, not in `## Behavior Parameters`.
- The brief's `Background Knowledge` should be distilled into a short bullet list in the final page, not copied verbatim.
- The source mapping table becomes the `## Source Reference Appendix` in the final page.
