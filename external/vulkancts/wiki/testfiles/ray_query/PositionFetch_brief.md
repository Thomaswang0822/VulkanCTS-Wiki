# Understanding Brief: ray_query.position_fetch

## One-Sentence Test Purpose

This test checks whether `VK_KHR_ray_tracing_position_fetch` correctly returns the triangle vertex positions stored in a BLAS, in object space, when invoked through `rayQueryGetIntersectionTriangleVertexPositionsEXT` across 15 vertex formats, CPU and GPU BLAS builds, an optional non-identity instance transform, and three shader stages.

## Background Knowledge

### `VK_KHR_ray_tracing_position_fetch`

The extension adds a shader built-in, `rayQueryGetIntersectionTriangleVertexPositionsEXT(rq, committed, outputVal)`, that returns the three vertex positions of the triangle whose intersection the ray query is currently visiting. The positions are returned in object space, not world space. A driver that applies the instance transform to the returned positions would be incorrect. The Vulkan spec chapter "Ray Tracing Position Fetch" defines this behavior; the spec sources live at `external/vulkan-docs/src/chapters/` (not vendored in this checkout).

Why it matters here:

- The host stores the original triangle vertices in a BLAS, builds a TLAS instance over it (with or without a non-identity transform), and then asks the shader to fetch the candidate triangle's vertex positions.
- The host's expected output is the original triangle vertices, regardless of the instance transform. The `instance_transform` flag value is what distinguishes the object-space-fetch proof from the basic-fetch proof.
- The BLAS must be built with `VK_BUILD_ACCELERATION_STRUCTURE_ALLOW_DATA_ACCESS_KHR` for position fetch to be legal. The host sets that flag in every leaf ([vktRayQueryPositionFetchTests.cpp:480](../../../modules/vulkan/ray_query/vktRayQueryPositionFetchTests.cpp#L480)).

### Vertex format coverage

`VK_KHR_acceleration_structure` defines a list of mandatory and optional vertex formats a BLAS may use. Position fetch must work for any format the implementation supports as a BLAS vertex buffer. The test crosses 15 formats: 6 mandatory (`R32G32_SFLOAT`, `R32G32B32_SFLOAT`, `R16G16_SFLOAT`, `R16G16B16A16_SFLOAT`, `R16G16_SNORM`, `R16G16B16A16_SNORM`) and 9 additional (`R8G8_SNORM`, `R8G8B8_SNORM`, `R8G8B8A8_SNORM`, `R16G16B16_SNORM`, `R16G16B16_SFLOAT`, `R32G32B32A32_SFLOAT`, `R64G64_SFLOAT`, `R64G64B64_SFLOAT`, `R64G64B64A64_SFLOAT`). `checkAccelerationStructureVertexBufferFormat` gates each format against the implementation's supported list before the leaf runs.

### Multi-triangle scene for 3-component sfloat formats

For sfloat formats with at least 3 used channels, the host builds 4 geometries, each with 4 triangles (16 triangles total). One chosen triangle sits at `z = 0`; the other 15 sit at `z = 10 + N` for varying `N`. Only the chosen triangle is on the ray's path. The chosen geometry and triangle indices are randomized with a seed derived from `(buildType, vertexFormat, testFlagMask)`. For all other formats, the host builds a single triangle at `z = 0`. This split exercises the implementation's ability to fetch the candidate triangle's positions when the BLAS contains many candidate triangles at different depths.

### Tolerance comparison

The host compares each fetched position to the original triangle vertex. The comparison uses `dot(diff, diff) < 1e-5`, where `diff = expected - fetched`. The threshold is a squared-length comparison, so the effective length tolerance is `sqrt(1e-5) ~ 0.00316`. The threshold is loose enough for the lowest-precision format tested (`R8G8B8_SNORM`, with 8-bit signed normalized components), and tight enough to detect a wrong-triangle fetch, an instance-transform-applied fetch, or a precision regression.

## One Concrete Example

The `compute_shader.gpu_built.r32g32b32_sfloat.NoFlags` leaf reconstructs as the following compute shader (host-generated, source literal at [vktRayQueryPositionFetchTests.cpp:198-L274](../../../modules/vulkan/ray_query/vktRayQueryPositionFetchTests.cpp#L198-L274)):

```glsl
#version 460 core
#extension GL_EXT_ray_query : require
#extension GL_EXT_ray_tracing_position_fetch : require

layout(set=0, binding=0) uniform accelerationStructureEXT topLevelAS;
layout(set=0, binding=1, std430) buffer RayOrigins {
  vec4 values[1];
} origins;
layout(set=0, binding=2, std430) buffer OutputPositions {
  vec4 values[3];
} modes;

layout(local_size_x=128, local_size_y=1, local_size_z=1) in;

void main()
{
  uint index = gl_LocalInvocationID.x;
  while (index < 1) {
    const uint  cullMask  = 0xFF;
    const vec3  origin    = origins.values[index].xyz;
    const vec3  direction = vec3(0.0, 0.0, -1.0);
    const float tMin      = 0.0f;
    const float tMax      = 2.0f;
    rayQueryEXT rq;
    rayQueryInitializeEXT(rq, topLevelAS, gl_RayFlagsNoneEXT, cullMask, origin, tMin, direction, tMax);
    while (rayQueryProceedEXT(rq)) {
      if (rayQueryGetIntersectionTypeEXT(rq, false) == gl_RayQueryCandidateIntersectionTriangleEXT) {
        vec3 outputVal[3];
        rayQueryGetIntersectionTriangleVertexPositionsEXT(rq, false, outputVal);
        for (int i=0; i<3; i++) {
           modes.values[3*index+i] = vec4(outputVal[i], 0);
        }
      }
    }
    index += 128;
  }
}
```

The host dispatches `1 x 1 x 1` workgroups with `local_size_x = 128`, so 128 invocations run, but only invocation 0 enters the `while (index < 1)` loop. The single ray starts at `(0.25, 0.25, 1.0)` and travels `(0, 0, -1)` over `t in [0, 2]`, hitting a triangle at `z = 0`. The shader fetches the three candidate triangle vertex positions and writes them to `modes.values[0..2]`. The host reads those three `vec4`s back and compares each `xyz` to the original triangle vertices `(0,0,0)`, `(1,0,0)`, `(0,1,0)` under the `1e-5` squared-length tolerance.

## End-to-End Test Flow

```text
[host] choose shaderSourceType, buildType, vertexFormat, testFlagMask
[host] checkSupport: gate extensions, features, vertex format, stage
[host] build BLAS with ALLOW_DATA_ACCESS_KHR flag
       - multipleTriangles path (sfloat 3+ channels): 4 geometries x 4 triangles, chosen one at z=0, rest at z=10+N
       - singleTriangle path: 1 geometry x 1 triangle at z=0
[host] build TLAS with 1 instance, transform = identity OR notQuiteIdentity (scales 0.98, 0.97, 0.99)
[host] allocate origins buffer with 1 vec4 = (0.25, 0.25, 1.0, 0.0)
[host] allocate output positions buffer with 3 vec4s, prefilled with 0xFF bytes
[host] update descriptor set: b0 = TLAS, b1 = origins buffer, b2 = output positions buffer
[host] dispatch:
       - vertex_shader: cmdDraw(128 points) inside an empty render pass
       - compute_shader: cmdDispatch(1, 1, 1) with local_size_x=128
       - rgen_shader: cmdTraceRaysKHR(128, 1, 1)
[device] invocation 0 enters the per-ray loop, initializes rayQueryEXT, proceeds to triangle candidate
[device] fetches 3 candidate vertex positions via rayQueryGetIntersectionTriangleVertexPositionsEXT(rq, false, outputVal)
[device] writes them to modes.values[0..2]
[host] barrier (SHADER_WRITE -> HOST_READ), submit, wait
[host] invalidate, memcpy output buffer to host vector of 3 vec4s
[host] for each of 3 expected vertices: compute diff = expected - fetched.xyz, require dot(diff, diff) < 1e-5
[host] return pass/fail
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- One GLSL shader per leaf, generated by `PositionFetchCase::initPrograms` ([vktRayQueryPositionFetchTests.cpp:192-L275](../../../modules/vulkan/ray_query/vktRayQueryPositionFetchTests.cpp#L192-L275)). Three stage variants exist (`vert`, `comp`, `rgen`), all sharing a `sharedHeader` and a `mainLoop`. The shader binary is identical across all 180 leaves; only the host-side parameters differ.
- Build options: `vk::ShaderBuildOptions(usedVulkanVersion, SPIRV_VERSION_1_4, 0u, true)` ([vktRayQueryPositionFetchTests.cpp:194](../../../modules/vulkan/ray_query/vktRayQueryPositionFetchTests.cpp#L194)).
- `updateRayTracingGLSL` is an identity passthrough in this CTS version, so the reconstructed GLSL is the GLSL the host feeds to `glslangValidator`.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `topLevelAS` (TLAS over a single BLAS instance) | yes | yes (descriptor b0) | read by `rayQueryInitializeEXT` | no | The traversed scene; instance transform varies per leaf |
| BLAS (1 or 16 triangles in the chosen vertex format, built with `ALLOW_DATA_ACCESS_KHR`) | yes, built in `iterate()` | yes (referenced by TLAS instance) | traversed by the ray query | no | Stores the vertex positions the test fetches |
| `origins` buffer (1 `vec4`, host-visible, `STORAGE_BUFFER`) | yes, prefilled with `(0.25, 0.25, 1.0, 0.0)` | yes (descriptor b1) | read by shader | no | Single ray origin; the host fixes the direction and t-range in the shader |
| `modes` (output positions) buffer (3 `vec4`s, host-visible, `STORAGE_BUFFER`) | yes, prefilled with `0xFF` bytes | yes (descriptor b2) | written by shader | yes, after `invalidateAlloc` | Receives the three fetched vertex positions; the host scans it under tolerance |
| Graphics-only: empty render pass + framebuffer | yes | yes | n/a | no | Required to bind the vertex-shader pipeline; no attachments |
| Ray-tracing-only: shader binding table | yes | yes | read by `cmdTraceRaysKHR` | no | Drives the rgen shader execution |

## What Is Checked

- The shader writes three `vec4` values to `modes.values[0..2]`, one per candidate triangle vertex.
- The host reads the buffer back, takes the `.xyz` of each entry, and compares it to the original triangle vertex `(0,0,0)`, `(1,0,0)`, `(0,1,0)`.
- The comparison is `dot(expected - fetched, expected - fetched) < 1e-5`. The threshold is a squared-length comparison.
- The check runs once per leaf (one ray per leaf). A failure on any of the three vertices fails the leaf with a message naming the expected and observed values.
- Pass condition: all three vertices satisfy the tolerance ([vktRayQueryPositionFetchTests.cpp:701-L716](../../../modules/vulkan/ray_query/vktRayQueryPositionFetchTests.cpp#L701-L716)).

## Behavior Parameter Identification

> **Behavior parameter:** `testFlagMask` (the registered leaf-name token that selects whether the TLAS instance has a non-identity transform)
>
> **Candidate values:** `NoFlags`, `instance_transform`

Both values share one shader binary, one BLAS layout (per format), and one build type per leaf. The only difference is whether the TLAS instance transform is the identity matrix or the `notQuiteIdentityMatrix3x4` matrix that scales by `(0.98, 0.97, 0.99)`. The expected output is the original triangle vertices in both cases because position fetch returns object-space positions. A failure under `instance_transform` but not under `NoFlags` (for the same shader source, build type, and format) localizes the bug to object-space handling.

Secondary axes:

- **Shader source** (`vertex_shader`, `compute_shader`, `rgen_shader`): a configuration dimension. The same shader body runs in three stages; the difference is the stage-specific feature gate, dispatch mechanism, and `index` derivation. A failure on only one shader source points at stage-specific descriptor wiring or feature gating.
- **Build type** (`cpu_built`, `gpu_built`): a configuration dimension. The BLAS build runs on the host or on the device. A failure on only one build type points at the build encoder for that path.
- **Vertex format** (15 listed `VkFormat`s): a configuration dimension. Each format exercises a different vertex-data encoding. A failure on only one format points at the format-specific decoding in the BLAS or the position-fetch readback.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `NoFlags` | Position fetch returned wrong vertex positions for the chosen vertex format, build type, or shader source. Points at format decoding, BLAS storage, multi-triangle selection, or stage-specific descriptor wiring. |
| `instance_transform` | Position fetch applied the instance transform to the returned positions instead of returning object-space positions. Points at the implementation applying world-space transform to the fetched vertices. |
| (both values, same format and build type and shader source) | The implementation does not support position fetch for this combination. Points at format decoding, BLAS storage with `ALLOW_DATA_ACCESS_KHR`, or the position-fetch code path itself. |
| (both values, same format, both build types, all shader sources) | The implementation does not handle this vertex format at all in the position-fetch path. |

## Important Variations and Special Cases

- **Multi-triangle scene (sfloat 3+ channel formats).** For `R32G32B32_SFLOAT`, `R16G16B16A16_SFLOAT`, `R32G32B32A32_SFLOAT`, `R16G16B16_SFLOAT`, `R64G64B64_SFLOAT`, `R64G64B64A64_SFLOAT`, the BLAS contains 4 geometries x 4 triangles (16 triangles total). One chosen triangle sits at `z = 0` and is hit by the ray; the other 15 sit at `z = 10..25`. The chosen geometry and triangle indices are randomized by a seed derived from `(buildType, vertexFormat, testFlagMask)`. The expected output is still the original 2D triangle vertices. This variation tests that the implementation fetches positions from the correct triangle, not just the first one in the BLAS.
- **Single-triangle scene (other formats).** For 2-channel sfloat formats (`R32G32_SFLOAT`, `R16G16_SFLOAT`, `R64G64_SFLOAT`) and all SNORM formats, the BLAS contains a single triangle at `z = 0`. The Z value is irrelevant because these formats cannot store the Z component meaningfully (or it would be normalized to 0).
- **Instance transform matrix.** The `notQuiteIdentityMatrix3x4` is `diag(0.98, 0.97, 0.99)` with zero translation. It is non-identity in every component to make a world-space-fetch bug produce a measurable diff. The expected output ignores the matrix because position fetch returns object-space positions.
- **Dispatch count.** All three stages dispatch 128 invocations, but only invocation 0 enters the per-ray loop because `numRays = 1` and the loop increment is `kNumThreadsAtOnce = 128`. The other 127 invocations do nothing. This is a host-side artifact of the test harness, not a tested property.
- **`VK_BUILD_ACCELERATION_STRUCTURE_ALLOW_DATA_ACCESS_KHR`.** Every BLAS is built with this flag because position fetch requires it. A driver that rejects this flag, or that silently drops it during the build, would fail every leaf.
- **Output buffer pre-fill.** The host prefills `modes.values[0..2]` with `0xFF` bytes. If the shader fails to write at all, the host reads `0xFFFFFFFF` and the tolerance check fails. This is a defensive check, not a tested property.
- **Random seed.** `getRandomSeed()` packs `(buildType, vertexFormat, testFlagMask)` into a `uint32_t`. The seed drives the multi-triangle `chosenGeom` and `chosenTri` selection. The same leaf reproduces across runs because the seed is deterministic.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| `TestParams` struct and `getRandomSeed` | [vktRayQueryPositionFetchTests.cpp:80-L92](../../../modules/vulkan/ray_query/vktRayQueryPositionFetchTests.cpp#L80-L92) | Defines the per-leaf parameters and the seed derivation. |
| `PositionFetchCase::checkSupport` | [vktRayQueryPositionFetchTests.cpp:132-L190](../../../modules/vulkan/ray_query/vktRayQueryPositionFetchTests.cpp#L132-L190) | Extension, feature, format, and stage gates. |
| `PositionFetchCase::initPrograms` | [vktRayQueryPositionFetchTests.cpp:192-L275](../../../modules/vulkan/ray_query/vktRayQueryPositionFetchTests.cpp#L192-L275) | The shared shader source for vert, comp, rgen. |
| `PositionFetchInstance::iterate` (BLAS / TLAS build, dispatch, copyback, verify) | [vktRayQueryPositionFetchTests.cpp:409-L728](../../../modules/vulkan/ray_query/vktRayQueryPositionFetchTests.cpp#L409-L728) | End-to-end host flow. |
| Geometry and instance setup (multi-triangle path, instance transform) | [vktRayQueryPositionFetchTests.cpp:431-L490](../../../modules/vulkan/ray_query/vktRayQueryPositionFetchTests.cpp#L431-L490) | The scene the ray queries. |
| Expected-output fill and tolerance check | [vktRayQueryPositionFetchTests.cpp:504-L516](../../../modules/vulkan/ray_query/vktRayQueryPositionFetchTests.cpp#L504-L516), [L693-L728](../../../modules/vulkan/ray_query/vktRayQueryPositionFetchTests.cpp#L693-L728) | The pass/fail rule. |
| `createPositionFetchTests` registration | [vktRayQueryPositionFetchTests.cpp:732-L840](../../../modules/vulkan/ray_query/vktRayQueryPositionFetchTests.cpp#L732-L840) | The 3 x 2 x 15 x 2 leaf matrix. |

## Questions / Risk Points for User Audit

- Is the framing of `testFlagMask` as the primary behavioral axis correct, given that the shader body is identical across all leaves and the format dimension is the largest? An alternative is to make `vertex format` the primary axis with 15 subsections, but that would be very long.
- Is the multi-triangle scene explanation clear? The 4 x 4 layout and the randomized chosen triangle are the test's main mechanism for catching wrong-triangle fetches.
- Should the page emphasize the object-space semantics of position fetch up front, or leave it to the `instance_transform` subsection?
- The tolerance `1e-5` squared length is loose for `R32G32B32_SFLOAT` and tight for `R8G8B8_SNORM`. Should the page call out the per-format precision implications, or treat the tolerance as a single threshold?
- The page mentions three shader sources but the shader body is identical. Is it clear that the shader source dimension is configuration, not behavior?

## Conversion Notes for Final Wiki Rewrite

- Distill the brief's Background Knowledge to a short bullet list: `VK_KHR_ray_tracing_position_fetch` semantics, `ALLOW_DATA_ACCESS_KHR` flag, multi-triangle scene, tolerance comparison.
- Use the `compute_shader.gpu_built.r32g32b32_sfloat.NoFlags` leaf as the single representative shader walkthrough. Compute is the simplest pipeline, `R32G32B32_SFLOAT` exercises the multi-triangle path, and `NoFlags` is the basic-fetch proof.
- Carry the `### Failure Cause Mapping` table verbatim into `## Failure Meaning`.
- The brief's "Important Variations and Special Cases" feeds the `## Behavior Parameters` subsections and `## Case Pruning`. The multi-triangle scene becomes a Behavior Parameters subsection under `NoFlags` (and stays relevant under `instance_transform`).
- The shader source, build type, and vertex format dimensions become rows in `## Parameter Dimensions and Observed Values`, not Behavior Parameters subsections.
- Source-mapping table becomes the basis of `## Source Reference Appendix`.
