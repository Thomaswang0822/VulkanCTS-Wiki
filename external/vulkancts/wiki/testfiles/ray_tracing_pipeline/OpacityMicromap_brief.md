# Understanding Brief: ray_tracing_pipeline opacity_micromap family

## One-Sentence Test Purpose

This test checks whether `VK_EXT_opacity_micromap` correctly resolves the opacity state of each subtriangle during ray traversal under all valid combinations of opacity-forcing, culling, force-2-state, and disable-micromap flags, using both per-subtriangle map data and special-index values, across 2-state and 4-state formats, subdivision levels 0 through 15, and non-zero base triangle variants.

## Background Knowledge

### Opacity micromap attachment

`VK_EXT_opacity_micromap` attaches a compact opacity lookup table to triangle geometry in a bottom-level acceleration structure. Each triangle references a micromap that subdivides it into subtriangles at a given subdivision level. During ray traversal, the implementation looks up the opacity state of the subtriangle the ray hits and uses it to decide whether to skip the any-hit shader (opaque), run the any-hit shader (non-opaque), or treat the triangle as transparent (ray passes through).

Why it matters here:
- The test builds a single triangle with a micromap attachment, then traces one ray per subtriangle at the subtriangle centroid. The resolved opacity state determines which shader stage runs (miss, any-hit, or closest-hit).
- The host independently computes the expected resolved state for each ray using the same micromap data and the same flag precedence rules, then compares the shader-reported result.

### Special index values

The opacity micromap extension defines four special index values used as opacity states throughout traversal and culling:

- `VK_OPACITY_MICROMAP_SPECIAL_INDEX_FULLY_TRANSPARENT_EXT` (-1): ray passes through, no hit.
- `VK_OPACITY_MICROMAP_SPECIAL_INDEX_FULLY_OPAQUE_EXT` (-2): opaque, any-hit shader skipped.
- `VK_OPACITY_MICROMAP_SPECIAL_INDEX_FULLY_UNKNOWN_TRANSPARENT_EXT` (-3): non-opaque, any-hit runs; only available in 4-state format.
- `VK_OPACITY_MICROMAP_SPECIAL_INDEX_FULLY_UNKNOWN_OPAQUE_EXT` (-4): non-opaque, any-hit runs; only available in 4-state format.

The test converts per-subtriangle data values to the special index space using bitwise NOT (`~state`), so data value 0 maps to `FULLY_TRANSPARENT`, 1 to `FULLY_OPAQUE`, 2 to `FULLY_UNKNOWN_TRANSPARENT`, and 3 to `FULLY_UNKNOWN_OPAQUE`.

### Opacity forcing and culling flags

Opacity resolution is influenced by instance flags, ray flags, and the micromap data:

- `VK_GEOMETRY_INSTANCE_FORCE_OPAQUE_BIT_KHR` and `gl_RayFlagsOpaqueEXT` force the geometry to be opaque, skipping the any-hit shader.
- `VK_GEOMETRY_INSTANCE_FORCE_NO_OPAQUE_BIT_KHR` and `gl_RayFlagsNoOpaqueEXT` force the geometry to be non-opaque, running the any-hit shader.
- `gl_RayFlagsCullOpaqueEXT` culls rays that hit opaque geometry.
- `gl_RayFlagsCullNoOpaqueEXT` culls rays that hit non-opaque geometry.
- Force-opaque and force-no-opaque are mutually exclusive at both instance and ray level. At most one of the four opacity ray flags (force-opaque, no-opaque, cull-opaque, cull-no-opaque) can be set per ray.

### Force-2-state and disable-micromap

- `VK_GEOMETRY_INSTANCE_FORCE_OPACITY_MICROMAP_2_STATE_EXT` and `gl_RayFlagsForceOpacityMicromap2StateEXT` collapse 4-state unknown values: `FULLY_UNKNOWN_TRANSPARENT` becomes `FULLY_TRANSPARENT`, and `FULLY_UNKNOWN_OPAQUE` becomes `FULLY_OPAQUE`.
- `VK_GEOMETRY_INSTANCE_DISABLE_OPACITY_MICROMAPS_EXT` bypasses the micromap entirely, falling back to the geometry's own opacity. The bottom-level AS must be built with `VK_BUILD_ACCELERATION_STRUCTURE_ALLOW_DISABLE_OPACITY_MICROMAPS_EXT` to allow this.

## One Concrete Example

Representative case: `ray_tracing_pipeline.opacity_micromap.NoFlags.map_value.2.level_0`

With subdivision level 0, there is one subtriangle (the whole triangle). The micromap uses 2-state format with one bit of data. The raygen shader traces one ray downward through the triangle centroid and writes the payload result into an output buffer.

Reconstructed raygen shader (simplified, `NoFlags` so `gl_RayFlagsNoneEXT`):

```glsl
#version 460 core
#extension GL_EXT_ray_tracing : require
#extension GL_EXT_opacity_micromap : require

layout(location=0) rayPayloadEXT uint value;

layout(set=0, binding=0) uniform accelerationStructureEXT topLevelAS;
layout(set=0, binding=1, std430) buffer RayOrigins {
  vec4 values[1];
} origins;
layout(set=0, binding=2, std430) buffer OutputModes {
  uint values[1];
} modes;

void main()
{
  const uint  cullMask  = 0xFF;
  const vec3  origin    = origins.values[gl_LaunchIDEXT.x].xyz;
  const vec3  direction = vec3(0.0, 0.0, -1.0);
  const float tMin      = 0.0;
  const float tMax      = 2.0;
  value                 = 0xFFFFFFFF;
  traceRayEXT(topLevelAS, gl_RayFlagsNoneEXT, cullMask, 0, 0, 0, origin, tMin, direction, tMax, 0);
  modes.values[gl_LaunchIDEXT.x] = value;
}
```

The any-hit shader sets `value = 1` and calls `terminateRayEXT`. The closest-hit shader sets `value = 2` only if the any-hit shader did not already run. The miss shader sets `value = 0`. So the output encodes which stage executed: 0 for miss, 1 for any-hit, 2 for closest-hit without any-hit.

## End-to-End Test Flow

```text
[host] generate random micromap data seeded by TestParams::seed
[host] build opacity micromap via vkCmdBuildMicromapsEXT with 2-state or 4-state format
[host] build bottom-level AS with one triangle, attaching the micromap via VkAccelerationStructureTrianglesOpacityMicromapEXT
[host] build top-level AS with one instance, applying instance flags from testFlagMask
[host] compute expected output mode per ray using the same micromap data and flag precedence
[host] write ray origins (subtriangle centroids) to origins SSBO
[host] dispatch vkCmdTraceRaysKHR with numRays = 4^subdivisionLevel
[device] raygen reads origin, calls traceRayEXT with ray flags from testFlagMask
[device] traversal resolves opacity from micromap; any-hit, closest-hit, or miss runs
[device] output buffer receives 0 (miss), 1 (any-hit), or 2 (closest-hit)
[host] invalidate and read output buffer
[host] compare each entry against expected output modes; fail on mismatch
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- Inline GLSL raygen shader: varies `flagsString` based on `testFlagMask`, and varies `numRays` array size based on `subdivisionLevel`.
- Inline GLSL any-hit, closest-hit, and miss shaders: fixed across all cases.
- SPIR-V target version: 1.4 (via `vk::SPIRV_VERSION_1_4`).

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `topLevelAS` | yes | yes | read by rgen | no | Top-level acceleration structure with one instance carrying instance flags. |
| `bottomLevelAS` | yes | yes | read by traversal | no | Bottom-level AS with one triangle and micromap attachment. |
| `micromap` | yes | yes | read by traversal | no | Opacity micromap built from random data; format and subdivision level vary per case. |
| `origins` SSBO | yes | yes (binding 1) | read by rgen | no | Ray origins, one per subtriangle centroid. |
| `modes` SSBO | yes | yes (binding 2) | written by rgen | yes | Output buffer receiving 0, 1, or 2 per ray. |
| `micromapDataBuffer` | yes | yes | read by micromap build | no | Host-visible buffer holding triangle array, index, and micromap data. |

## What Is Checked

The test compares the output modes buffer against a host-computed expected modes vector, entry by entry:

- 0 means the ray missed (transparent subtriangle or culled).
- 1 means the any-hit shader ran (non-opaque subtriangle).
- 2 means the closest-hit shader ran without any-hit (opaque subtriangle).

The host expected-value computation applies the same flag precedence and force-2-state collapse rules the spec defines for traversal. Any mismatch causes a `TCU_FAIL` with a per-ray log message.

## Behavior Parameter Identification

> **Behavior parameter:** `testFlagMask` flag category (the opacity/culling/force-2-state/disable flag combination)
>
> **Candidate values:** `NoFlags`, `force_opaque`, `force_no_opaque`, `cull_opaque`, `cull_no_opaque`, `force_2_state`, `disable_opacity_micromap`

The 120 registered direct children are all valid combinations of these flag categories. The categories group the combinations by mechanism. Secondary axes (`map_value` vs `special_index`, 2-state vs 4-state, subdivision level, non-zero base) are configuration dimensions documented in the parameter table, not the primary behavioral axis.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `NoFlags` | The implementation resolved the micromap opacity state incorrectly for the subtriangle the ray hit, or the micromap build produced wrong data. |
| `force_opaque` | The implementation did not force the geometry to be opaque when the instance or ray flag was set, or it incorrectly ran the any-hit shader. |
| `force_no_opaque` | The implementation did not force the geometry to be non-opaque when the instance or ray flag was set, or it incorrectly skipped the any-hit shader. |
| `cull_opaque` | The implementation did not cull the ray when the resolved opacity was opaque and the cull-opaque ray flag was set, or it culled a ray that should not have been culled. |
| `cull_no_opaque` | The implementation did not cull the ray when the resolved opacity was non-opaque and the cull-no-opaque ray flag was set, or it culled a ray that should not have been culled. |
| `force_2_state` | The implementation did not collapse `FULLY_UNKNOWN_TRANSPARENT` to `FULLY_TRANSPARENT` or `FULLY_UNKNOWN_OPAQUE` to `FULLY_OPAQUE` when the force-2-state instance or ray flag was set. |
| `disable_opacity_micromap` | The implementation did not bypass the micromap when the disable instance flag was set, or it used micromap opacity instead of the geometry's own opacity. |

## Important Variations and Special Cases

- `special_index` subgroup: When `useSpecialIndex` is true, the micromap uses a single special index value for the entire triangle (subdivision level forced to 0). The four leaf cases (0, 1, 2, 3) correspond to the four special index values via `~specialIndex`. This tests the special-index path separately from per-subtriangle data.
- `non_zero_base` variant: When `testFlagMask` is 0, an additional variant uses `baseTriangle = 1` with two triangles in the geometry, where only the second triangle has a micromap. This tests the `baseTriangle` offset in `VkAccelerationStructureTrianglesOpacityMicromapEXT`. The non-zero-base variant is only registered for `NoFlags` because the flag combinations are orthogonal to the base triangle offset.
- `map_value` subgroup: When `useSpecialIndex` is false, the micromap contains per-subtriangle data. The mode is 2 (1 bit per subtriangle) or 4 (2 bits per subtriangle). Subdivision levels 0 through 15 are exercised, producing 1 to 2^30 subtriangles.
- Subdivision level limit: `checkSupport` rejects cases where the subdivision level exceeds `maxOpacity2StateSubdivisionLevel` or `maxOpacity4StateSubdivisionLevel` reported by the device.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| `TestParams` struct and `TestFlagBits` enum | [vktRayTracingOpacityMicromapTests.cpp#L53-L81](../../../modules/vulkan/ray_tracing/vktRayTracingOpacityMicromapTests.cpp#L53-L81) | Defines the per-case parameters and the nine flag bits. |
| `checkSupport` | [vktRayTracingOpacityMicromapTests.cpp#L119-L156](../../../modules/vulkan/ray_tracing/vktRayTracingOpacityMicromapTests.cpp#L119-L156) | Feature requirements and subdivision level limit checks. |
| `initPrograms` rgen shader | [vktRayTracingOpacityMicromapTests.cpp#L163-L214](../../../modules/vulkan/ray_tracing/vktRayTracingOpacityMicromapTests.cpp#L163-L214) | Generates the raygen shader with flag-dependent `flagsString`. |
| `initPrograms` ah/ch/miss shaders | [vktRayTracingOpacityMicromapTests.cpp#L216-L257](../../../modules/vulkan/ray_tracing/vktRayTracingOpacityMicromapTests.cpp#L216-L257) | Generates the any-hit, closest-hit, and miss shaders. |
| `calcSubtriangleCentroid` | [vktRayTracingOpacityMicromapTests.cpp#L271-L323](../../../modules/vulkan/ray_tracing/vktRayTracingOpacityMicromapTests.cpp#L271-L323) | Computes the centroid of each subtriangle for ray origin placement. |
| Expected value computation | [vktRayTracingOpacityMicromapTests.cpp#L561-L651](../../../modules/vulkan/ray_tracing/vktRayTracingOpacityMicromapTests.cpp#L561-L651) | Host-side opacity resolution logic mirroring the spec. |
| Micromap build and AS setup | [vktRayTracingOpacityMicromapTests.cpp#L325-L541](../../../modules/vulkan/ray_tracing/vktRayTracingOpacityMicromapTests.cpp#L325-L541) | Builds the micromap, BLAS, and TLAS with micromap attachment. |
| Result verification | [vktRayTracingOpacityMicromapTests.cpp#L780-L812](../../../modules/vulkan/ray_tracing/vktRayTracingOpacityMicromapTests.cpp#L780-L812) | Reads output buffer and compares against expected modes. |
| `createOpacityMicromapTests` registration | [vktRayTracingOpacityMicromapTests.cpp#L818-L936](../../../modules/vulkan/ray_tracing/vktRayTracingOpacityMicromapTests.cpp#L818-L936) | Registers the 120 flag groups with map_value and special_index subgroups. |

## Questions / Risk Points for User Audit

- Is the opacity resolution precedence (ray flags override instance flags, force-opaque/no-opaque overrides micromap state) correctly captured?
- Is the force-2-state collapse logic (unknown transparent becomes transparent, unknown opaque becomes opaque) correct per spec?
- Is the non-zero-base variant only registered for `NoFlags` by design, not by oversight?
- Is the special-index convention (`~specialIndex` mapping 0 to transparent, 1 to opaque, 2 to unknown transparent, 3 to unknown opaque) consistent with the spec?

## Conversion Notes for Final Wiki Rewrite

- The concrete example becomes the representative shader walkthrough for the `NoFlags.map_value.2.level_0` case.
- The flag category grouping from `## Behavior Parameter Identification` becomes the `## Behavior Parameters` subsections.
- The `### Failure Cause Mapping` table is copied directly into the final page.
- The `### Cause Analysis` is written fresh during the rewrite, grounded in the host-side expected value computation and the shader logic.
- Source-mapping table becomes the source reference appendix.
- The brief's Background Knowledge is distilled into a concise bullet list for the final page.
