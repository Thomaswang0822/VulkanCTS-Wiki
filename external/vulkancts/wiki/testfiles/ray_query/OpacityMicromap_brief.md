# Understanding Brief: ray_query.opacity_micromap

## One-Sentence Test Purpose

This test checks whether `VK_EXT_opacity_micromap` correctly classifies each subtriangle of a unit triangle BLAS as transparent, non-opaque candidate, or opaque committed hit when an inline ray query traverses a TLAS whose BLAS geometry references a built (and optionally cloned or compacted) opacity micromap, under all combinations of micromap format (2-state or 4-state), special-index mode, subdivision level, force-opaque / force-2-state / disable-micromap instance and ray flags, base-triangle offset, and shader source stage.

## Background Knowledge

### Opacity micromap

An opacity micromap is a small lookup table attached to a triangle geometry inside a BLAS. Each entry classifies one subtriangle (a recursive barycentric subdivision of the parent triangle) with one of four special indices:

- `VK_OPACITY_MICROMAP_SPECIAL_INDEX_FULLY_TRANSPARENT_EXT` (`-1`): subtriangle is skipped, no candidate is reported.
- `VK_OPACITY_MICROMAP_SPECIAL_INDEX_FULLY_OPAQUE_EXT` (`-2`): subtriangle is opaque; the implementation auto-commits the candidate during `rayQueryProceedEXT`.
- `VK_OPACITY_MICROMAP_SPECIAL_INDEX_FULLY_UNKNOWN_OPAQUE_EXT` (`-4`): subtriangle behaves like a non-opaque triangle; a candidate is reported but is not auto-committed.
- `VK_OPACITY_MICROMAP_SPECIAL_INDEX_FULLY_UNKNOWN_TRANSPARENT_EXT` (`-3`): implementation may treat the subtriangle as transparent or as a non-opaque candidate.

Two storage formats exist: `VK_OPACITY_MICROMAP_FORMAT_2_STATE_EXT` packs one bit per subtriangle (transparent or opaque); `VK_OPACITY_MICROMAP_FORMAT_4_STATE_EXT` packs two bits per subtriangle (all four special indices). The subdivision level `L` produces `4^L` subtriangles. The CTS host encodes a per-subtriangle state `s` from the random data buffer, then maps it into the special-index space with a bitwise NOT (`~s`), so a stored `0` becomes `FULLY_TRANSPARENT` and a stored `1` becomes `FULLY_OPAQUE`.

Why it matters here:

- The shader never calls `rayQueryConfirmIntersectionEXT`. The implementation's choice of opacity state therefore determines whether the candidate is auto-committed (opaque), reported without commit (unknown-opaque), or never reported (transparent). The shader writes `0` for miss, `1` for non-opaque candidate, `2` for committed triangle hit.
- The host reproduces the same expected output code per ray using the same `~s` mapping and the same flag overrides, then compares.

### Per-ray opacity-state overrides

Five orthogonal flag sources override the per-subtriangle state during traversal:

- `VK_GEOMETRY_INSTANCE_FORCE_OPAQUE_BIT_KHR` (instance flag, `TEST_FLAG_BIT_FORCE_OPAQUE_INSTANCE`): forces the entire instance to behave as opaque.
- `gl_RayFlagsOpaqueEXT` (ray flag, `TEST_FLAG_BIT_FORCE_OPAQUE_RAY_FLAG`): forces the ray to treat geometry as opaque; overrides instance and geometry opaque bits.
- `VK_GEOMETRY_INSTANCE_DISABLE_OPACITY_MICROMAPS_EXT` (instance flag, `TEST_FLAG_BIT_DISABLE_OPACITY_MICROMAP_INSTANCE`): the BLAS must be built with `VK_BUILD_ACCELERATION_STRUCTURE_ALLOW_DISABLE_OPACITY_MICROMAPS_EXT`; traversal then treats the triangle as a normal triangle without consulting the micromap.
- `VK_GEOMETRY_INSTANCE_FORCE_OPACITY_MICROMAP_2_STATE_EXT` (instance flag, `TEST_FLAG_BIT_FORCE_2_STATE_INSTANCE`): clamps 4-state micromaps to 2-state, so unknown-opaque becomes opaque and unknown-transparent becomes transparent.
- `gl_RayFlagsForceOpacityMicromap2StateEXT` (ray flag, `TEST_FLAG_BIT_FORCE_2_STATE_RAY_FLAG`): same clamping as the instance flag, but driven from the ray.

The test crosses all 32 combinations of these five bits and registers one leaf per combination.

### Subtriangle centroid ray origin

The host computes a per-subtriangle centroid `calcSubtriangleCentroid(index, subdivisionLevel)` and fires a ray from `(centroid.x, centroid.y, 1.0)` along `(0, 0, -1)` with `tmin = 0` and `tmax = 2`. The unit triangle is at `z = 0`, so the ray hits the parent triangle at exactly one subtriangle. The shader dispatches `kNumThreadsAtOnce = 1024` invocations that stride through the `numRays` slots.

## One Concrete Example

The `render.compute_shader.NoFlags.map_value.2.level_0` case reconstructs as the following compute shader (host-generated from the source literal at [vktRayQueryOpacityMicromapTests.cpp:236-L309](../../../modules/vulkan/ray_query/vktRayQueryOpacityMicromapTests.cpp#L236-L309) with `subdivisionLevel = 0`, `mode = 2`, `testFlagMask = 0`):

```glsl
#version 460 core
#extension GL_EXT_ray_query : require
#extension GL_EXT_opacity_micromap : require

layout(set=0, binding=0) uniform accelerationStructureEXT topLevelAS;
layout(set=0, binding=1, std430) buffer RayOrigins {
  vec4 values[1];
} origins;
layout(set=0, binding=2, std430) buffer OutputModes {
  uint values[1];
} modes;

layout(local_size_x=128, local_size_y=1, local_size_z=1) in;

void main()
{
  uint index = gl_GlobalInvocationID.x;
  while (index < 1) {
    const uint  cullMask  = 0xFF;
    const vec3  origin    = origins.values[index].xyz;
    const vec3  direction = vec3(0.0, 0.0, -1.0);
    const float tMin      = 0.0f;
    const float tMax      = 2.0f;
    uint        outputVal = 0; // 0 for miss, 1 for non-opaque, 2 for opaque
    rayQueryEXT rq;
    rayQueryInitializeEXT(rq, topLevelAS, gl_RayFlagsNoneEXT, cullMask, origin, tMin, direction, tMax);
    while (rayQueryProceedEXT(rq)) {
      if (rayQueryGetIntersectionTypeEXT(rq, false) == gl_RayQueryCandidateIntersectionTriangleEXT) {
        outputVal = 1;
      }
    }
    if (rayQueryGetIntersectionTypeEXT(rq, true) == gl_RayQueryCommittedIntersectionTriangleEXT) {
      outputVal = 2;
    }
    modes.values[index] = outputVal;
    index += 1024;
  }
}
```

With `subdivisionLevel = 0` there is one subtriangle covering the entire parent triangle, so `numRays = 1`. The host fills `origins.values[0]` with the centroid `(1/3, 1/3, 1.0)` and reads back `modes.values[0]`. The expected value depends on the single bit the random data buffer chose for that one subtriangle: `0` -> transparent -> expected `0`, `1` -> opaque -> expected `2`.

## End-to-End Test Flow

```text
[host] choose shader stage (vertex / compute / rgen), testFlagMask (5 bits),
       useSpecialIndex, mode (2 or 4), subdivisionLevel (0..15), nonZeroBase,
       copyType (None / Clone / Compact), useMaintenance5
[host] seed = stored per-case constant; fill opacityMicromapData with random bytes
[host] build opacity micromap with cmdBuildMicromapsEXT into a device-local backing buffer
[host] if copyType != None: create a second micromap, cmdCopyMicromapEXT (CLONE),
       then barrier; Compact mode currently reuses CLONE
[host] attach the micromap to the BLAS triangle geometry via
       VkAccelerationStructureTrianglesOpacityMicromapEXT (indexType UINT32,
       baseTriangle = 1 if nonZeroBase else 0)
[host] build BLAS (with ALLOW_DISABLE_OPACITY_MICROMAPS_EXT when the disable flag is set)
[host] build TLAS with one instance carrying the per-instance opacity flags
[host] compute expectedOutputModes[index] per subtriangle:
         state = ~state-bit(s) (special_index space) or useSpecialIndex value
         apply force_2_state clamping if set
         if state != TRANSPARENT and force_opaque: state = OPAQUE
         else if state != OPAQUE: state = UNKNOWN_OPAQUE
         map: TRANSPARENT -> 0, UNKNOWN_OPAQUE -> 1, OPAQUE -> 2
[host] fill origins buffer with per-subtriangle centroids
[host] create output modes buffer, fill with 0xFF
[host] dispatch compute (8 workgroups x 128 = 1024 invocations),
       or draw graphics (1024 vertices), or traceRays (1024,1,1)
[device] per ray: rayQueryInitializeEXT(TLAS, rayFlags, 0xFF, origin, 0, (0,0,-1), 2)
[device] proceed loop: if a triangle candidate appeared, outputVal = 1
[device] if committed intersection == triangle: outputVal = 2
[device] write modes.values[index] = outputVal, stride += 1024
[host] barrier (SHADER_WRITE -> HOST_READ), invalidate allocation
[host] compare each modes[i] to expectedOutputModes[i], log per-ray mismatch
[host] return pass/fail
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- Per-stage inline GLSL program emitted by `OpacityMicromapCase::initPrograms` ([vktRayQueryOpacityMicromapTests.cpp:224-L310](../../../modules/vulkan/ray_query/vktRayQueryOpacityMicromapTests.cpp#L224-L310)). Three stage wrappers share one ray-query body fragment built by `mainLoop` and one shared header built by `sharedHeader`. The body varies only in the `flagsString` (one of `gl_RayFlagsNoneEXT`, `gl_RayFlagsOpaqueEXT`, optionally OR'd with `gl_RayFlagsForceOpacityMicromap2StateEXT`) and in the array length `numRays = 4^subdivisionLevel`.
- Compute wrapper uses `gl_GlobalInvocationID.x` and strides by `kNumThreadsAtOnce = 1024` ([vktRayQueryOpacityMicromapTests.cpp:296-L309](../../../modules/vulkan/ray_query/vktRayQueryOpacityMicromapTests.cpp#L296-L309)).
- Vertex wrapper uses `gl_VertexIndex.x` and runs inside an empty render pass with `rasterizerDiscardEnable = VK_TRUE` ([vktRayQueryOpacityMicromapTests.cpp:273-L283](../../../modules/vulkan/ray_query/vktRayQueryOpacityMicromapTests.cpp#L273-L283), [L422-L490](../../../modules/vulkan/ray_query/vktRayQueryOpacityMicromapTests.cpp#L422-L490)).
- Raygen wrapper uses `gl_LaunchIDEXT.x` and creates the ray tracing pipeline with `VK_PIPELINE_CREATE_RAY_TRACING_OPACITY_MICROMAP_BIT_EXT` (or the maintenance5 `setCreateFlags2` equivalent) ([vktRayQueryOpacityMicromapTests.cpp:284-L295](../../../modules/vulkan/ray_query/vktRayQueryOpacityMicromapTests.cpp#L284-L295), [L964-L967](../../../modules/vulkan/ray_query/vktRayQueryOpacityMicromapTests.cpp#L964-L967)).
- Build options: `vk::ShaderBuildOptions(usedVulkanVersion, SPIRV_VERSION_1_4, 0u, true)` ([vktRayQueryOpacityMicromapTests.cpp:226](../../../modules/vulkan/ray_query/vktRayQueryOpacityMicromapTests.cpp#L226)).

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `topLevelAS` (single-instance TLAS) | yes | yes (descriptor b0) | read by `rayQueryInitializeEXT` | no | The traversed scene |
| BLAS with one (or two, when `nonZeroBase`) unit triangle(s) plus opacity micromap binding | yes | yes (referenced by the TLAS instance) | traversed by the ray query | no | The geometry and its micromap under test |
| Opacity micromap (`VkMicromapEXT`) | yes, built via `cmdBuildMicromapsEXT` | yes (referenced through `VkAccelerationStructureTrianglesOpacityMicromapEXT`) | read during traversal | no | Carries the per-subtriangle opacity state |
| `origins` SSBO (`vec4[numRays]`) | yes | yes (descriptor b1) | read by the shader per ray | no | Per-ray origin at subtriangle centroid |
| `modes` SSBO (`uint[numRays]`) | yes | yes (descriptor b2) | written by the shader per ray | yes | Sole shader-visible output |
| Micromap data buffer (triangle array + index + data, `HostVisible | DeviceAddress`) | yes | yes (`MICROMAP_BUILD_INPUT_READ_ONLY_BIT_EXT | SHADER_DEVICE_ADDRESS_BIT`) | read by `cmdBuildMicromapsEXT` | no | Host-writable source for the micromap build |
| Micromap backing buffer (`Local | DeviceAddress`, `MICROMAP_STORAGE_BIT_EXT`) | yes | yes | written by build, read by traversal | no | Device-local storage for the built micromap |
| Micromap scratch buffer | yes | yes | written by build | no | Build scratch; not visible to traversal |
| Optional `copyMicromapBackingBuffer` (when `copyType != None`) | yes | yes | written by `cmdCopyMicromapEXT`, read by traversal | no | Backing for the cloned destination micromap |

## What Is Checked

- The device writes one `uint32_t` per ray into the `modes` SSBO. Each value is `0`, `1`, or `2`.
- The host reads back the entire SSBO and compares each entry to `expectedOutputModes[i]` ([vktRayQueryOpacityMicromapTests.cpp:1050-L1063](../../../modules/vulkan/ray_query/vktRayQueryOpacityMicromapTests.cpp#L1050-L1063)).
- Per-ray mismatches are logged as `"Ray <idx>: expected <ref> and found <res>"`.
- Pass condition: no mismatches across all `numRays` entries.

## Behavior Parameter Identification

> **Behavior parameter:** `render` vs `copy` test family
>
> **Candidate values:** `render`, `copy`

The two direct children of `ray_query.opacity_micromap` differ in what they exercise:

- `render` (registered by `addBasicTests`): exercises the micromap traversal path against all formats, special-index modes, subdivision levels, base-triangle offsets, shader stages, and all 32 combinations of the five opacity-related flags. The shader is the same body in three stage wrappers. This is the primary behavioral axis because it varies *what* the implementation must do for each subtriangle.
- `copy` (registered by `addCopyTests`): exercises the host-side clone / compact / maintenance5 paths. The shader is fixed to the compute `NoFlags` shape. This is the secondary axis because it varies *how* the micromap is produced, not what traversal does with it.

The secondary axes (shader stage, test flag mask, special-index use, mode, subdivision level, nonZeroBase, copy type, maintenance5) are configuration dimensions, not behavior parameters.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `render` (any leaf) | Micromap build encoded the wrong per-subtriangle state, or traversal did not consult the micromap, or the implementation misapplied one of the five opacity overrides (force-opaque instance / ray, disable micromap, force-2-state instance / ray), or the shader stage wrapper mis-dispatched its rays. |
| `render` (`map_value` leaves) | The host-computed reference and the device disagreed on the per-subtriangle state lookup. Indicates a packing bug in the 2-state (1 bit/subtriangle) or 4-state (2 bits/subtriangle) micromap data, or wrong bit ordering during traversal. |
| `render` (`special_index` leaves) | The special-index value (0..3 -> FULLY_TRANSPARENT, FULLY_OPAQUE, FULLY_UNKNOWN_TRANSPARENT, FULLY_UNKNOWN_OPAQUE) was not honored, or the bitwise-NOT encoding (`~specialIndex`) was misread. |
| `render` (`force_opaque_*` leaves) | A force-opaque instance or ray flag failed to override the per-subtriangle state, leaving a transparent or unknown subtriangle as a candidate or miss. |
| `render` (`disable_opacity_micromap_instance` leaves) | The `ALLOW_DISABLE_OPACITY_MICROMAPS_EXT` build flag or the per-instance disable flag was not honored, so traversal still consulted the micromap when it should have treated the triangle as a normal triangle. |
| `render` (`force_2_state_*` leaves) | A force-2-state instance or ray flag failed to clamp 4-state entries to 2-state, leaving an unknown-opaque subtriangle as a non-opaque candidate instead of an opaque committed hit (or an unknown-transparent as a candidate instead of a miss). |
| `render` (`non_zero_base` leaves) | The `baseTriangle` offset was not applied when indexing the micromap, so a multi-triangle BLAS read state from the wrong triangle's slot. |
| `render` (`rgen_shader` leaves) | The `VK_PIPELINE_CREATE_RAY_TRACING_OPACITY_MICROMAP_BIT_EXT` pipeline create flag (or its maintenance5 64-bit equivalent) was not honored, so the ray tracing pipeline did not consult the micromap during traversal. |
| `copy` (`Clone` / `Compact` / `maintenance5` leaves) | `cmdCopyMicromapEXT` produced a destination micromap that does not traversal-match the source, or the maintenance5 `VkBufferUsageFlags2CreateInfo` path produced a wrong-shape micromap data buffer. |

## Important Variations and Special Cases

- **`useSpecialIndex = true`.** The `indexBuffer` slot holds a single `uint32_t` set to `m_params.mode = ~specialIndex`. The test name token is `special_index.<0..3>`. The four values map to `FULLY_TRANSPARENT`, `FULLY_OPAQUE`, `FULLY_UNKNOWN_TRANSPARENT`, `FULLY_UNKNOWN_OPAQUE` after the bitwise NOT.
- **`useSpecialIndex = false` (`map_value`).** The `indexBuffer` slot is `0`, meaning each subtriangle reads its own state from the data buffer. The test name token is `map_value.<2|4>.level_<0..15>`.
- **`nonZeroBase = true`.** Only registered under `testFlagMask == 0` and `map_value`. The host builds a two-triangle BLAS and sets `baseTriangle = 1` so only the second triangle's micromap data is consulted. The first triangle's micromap bytes are still allocated and seeded but never read. Tests the `baseTriangle` offset path.
- **`copyType = CT_CLONE` and `CT_COMPACT`.** Both currently emit `VK_COPY_MICROMAP_MODE_CLONE_EXT` in `VkCopyMicromapInfoEXT`. The two registered groups share the same code path; the only difference is the test name. Source-level investigation is needed to confirm whether `CT_COMPACT` was intended to use `VK_COPY_MICROMAP_MODE_COMPACT_EXT` and whether that mode is implemented.
- **`useMaintenance5 = true`.** Only one leaf exists (`copy.misc.maintenance5`). The host replaces `VkBufferUsageFlags` with `VkBufferUsageFlags2CreateInfoKHR` on the micromap data buffer, scratch buffer, origins buffer, and output modes buffer. The pipeline create flag also moves to the 64-bit `setCreateFlags2` form for the rgen path; here it uses the compute path so the pipeline flag is not exercised.
- **`subdivisionLevel = 0`.** `numRays = 1`. The shader array length is `1`. This is the smallest case and is the representative walkthrough choice.
- **`subdivisionLevel = 15`.** `numRays = 4^15 = 2^30 = 1073741824`. The shader array length is `2^30`; the host allocates `4^15 * 4` bytes for the output modes SSBO (~4 GiB) and `4^15 * 16` bytes for the origins SSBO (~16 GiB). Devices with insufficient memory will fail at allocation. The test does not pre-check `maxMemoryAllocationCount` or per-allocation size limits; high-level leaves may be skipped by the runner for resource reasons.
- **Random seed.** Each leaf uses a monotonically increasing seed starting from `1614674687u` for `render` and `1614674688u` for `copy`. The same seed produces the same `opacityMicromapData`, so failures reproduce.
- **Per-stage descriptor binding.** The shader binds the TLAS at b0, the origins SSBO at b1, and the modes SSBO at b2 across all three stage wrappers. The compute and rgen paths use `cmdDispatch(8, 1, 1)` and `cmdTraceRaysKHR(1024, 1, 1)` respectively; the vertex path draws 1024 point vertices with `rasterizerDiscardEnable = VK_TRUE`.
- **Pipeline create flag for rgen.** `VK_PIPELINE_CREATE_RAY_TRACING_OPACITY_MICROMAP_BIT_EXT` is set unconditionally on the rgen pipeline. The flag tells the implementation that the ray tracing pipeline may consult opacity micromaps during traversal. Without it, an implementation is allowed to skip micromap processing and the test would fail.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| `TestParams` struct | [vktRayQueryOpacityMicromapTests.cpp:98-L110](../../../modules/vulkan/ray_query/vktRayQueryOpacityMicromapTests.cpp#L98-L110) | Defines every parameter the test crosses. |
| `TestFlagBits` enum and names | [vktRayQueryOpacityMicromapTests.cpp:68-L81](../../../modules/vulkan/ray_query/vktRayQueryOpacityMicromapTests.cpp#L68-L81) | The five opacity-related flag bits. |
| `CopyType` enum and names | [vktRayQueryOpacityMicromapTests.cpp:83-L96](../../../modules/vulkan/ray_query/vktRayQueryOpacityMicromapTests.cpp#L83-L96) | Clone / Compact copy modes. |
| `checkSupport` | [vktRayQueryOpacityMicromapTests.cpp:153-L217](../../../modules/vulkan/ray_query/vktRayQueryOpacityMicromapTests.cpp#L153-L217) | Extension and feature gates, plus per-leaf subdivision-level limit checks. |
| `initPrograms` (per-stage GLSL) | [vktRayQueryOpacityMicromapTests.cpp:224-L310](../../../modules/vulkan/ray_query/vktRayQueryOpacityMicromapTests.cpp#L224-L310) | Source literal for the shared header, main loop, and three stage wrappers. |
| `calcSubtriangleCentroid` | [vktRayQueryOpacityMicromapTests.cpp:323-L375](../../../modules/vulkan/ray_query/vktRayQueryOpacityMicromapTests.cpp#L323-L375) | Bit-twiddling subtriangle centroid generator used to seed `origins`. |
| Micromap build and copy | [vktRayQueryOpacityMicromapTests.cpp:530-L730](../../../modules/vulkan/ray_query/vktRayQueryOpacityMicromapTests.cpp#L530-L730) | `cmdBuildMicromapsEXT`, `cmdCopyMicromapEXT`, and the surrounding barriers. |
| Expected-output computation | [vktRayQueryOpacityMicromapTests.cpp:788-L863](../../../modules/vulkan/ray_query/vktRayQueryOpacityMicromapTests.cpp#L788-L863) | The host reference model: `~state` mapping, force-2-state clamping, force-opaque override, final state-to-output mapping. |
| Dispatch and copyback | [vktRayQueryOpacityMicromapTests.cpp:923-L1025](../../../modules/vulkan/ray_query/vktRayQueryOpacityMicromapTests.cpp#L923-L1025) | Stage-specific pipeline creation, dispatch, and `SHADER_WRITE -> HOST_READ` barrier. |
| Pass/fail scan | [vktRayQueryOpacityMicromapTests.cpp:1033-L1064](../../../modules/vulkan/ray_query/vktRayQueryOpacityMicromapTests.cpp#L1033-L1064) | Per-ray comparison and `TCU_FAIL` on mismatch. |
| `addBasicTests` (`render`) | [vktRayQueryOpacityMicromapTests.cpp:1071-L1209](../../../modules/vulkan/ray_query/vktRayQueryOpacityMicromapTests.cpp#L1071-L1209) | Registration: 3 stages x 32 flag masks x (special_index 0..3 or 2 modes x 16 levels x optional non_zero_base). |
| `addCopyTests` (`copy`) | [vktRayQueryOpacityMicromapTests.cpp:1211-L1265](../../../modules/vulkan/ray_query/vktRayQueryOpacityMicromapTests.cpp#L1211-L1265) | Registration: 2 copy types x 2 modes x 16 levels + 1 maintenance5 leaf. |
| `createOpacityMicromapTests` | [vktRayQueryOpacityMicromapTests.cpp:1267-L1278](../../../modules/vulkan/ray_query/vktRayQueryOpacityMicromapTests.cpp#L1267-L1278) | Top-level registration: `render` and `copy` direct children. |

## Questions / Risk Points for User Audit

- Is the `~state` bitwise-NOT encoding (so a stored `0` bit becomes `FULLY_TRANSPARENT` and a stored `1` bit becomes `FULLY_OPAQUE`) described correctly? The host code at [vktRayQueryOpacityMicromapTests.cpp:823](../../../modules/vulkan/ray_query/vktRayQueryOpacityMicromapTests.cpp#L823) does `state = ~state` after extracting the raw bits, and the special-index enum values are negative `int32_t` reinterpreted as `uint32_t`.
- The `CT_COMPACT` copy type currently uses `VK_COPY_MICROMAP_MODE_CLONE_EXT` at [vktRayQueryOpacityMicromapTests.cpp:701](../../../modules/vulkan/ray_query/vktRayQueryOpacityMicromapTests.cpp#L701). Is this intentional (no compaction mode exists for micromaps in this CTS version), or is it a bug that should be flagged? The test still passes today because both modes produce an identical copy.
- For `subdivisionLevel = 15`, `numRays = 2^30` and the `modes` SSBO is `4 * 2^30 = 4 GiB`. Is this allocation expected to succeed on common hardware, or should the page call out the memory pressure explicitly?
- The `disable_opacity_micromap_instance` flag requires the BLAS to be built with `VK_BUILD_ACCELERATION_STRUCTURE_ALLOW_DISABLE_OPACITY_MICROMAPS_EXT`. The test sets this flag conditionally at [vktRayQueryOpacityMicromapTests.cpp:754-L755](../../../modules/vulkan/ray_query/vktRayQueryOpacityMicromapTests.cpp#L754-L755). When the disable flag is set in `testFlagMask`, the expected-output code skips the micromap lookup entirely and treats the geometry as a normal opaque-or-non-opaque triangle. Is the page's description of this behavior accurate?
- The five flag bits include both instance and ray variants of force-opaque and force-2-state. When both are set, the test still expects the same single override. Does the page need to call out that the ray flag wins over the instance flag per the Vulkan spec?

## Conversion Notes for Final Wiki Rewrite

- Distill the Background Knowledge into a short bullet list: opacity micromap concept, four special indices and their traversal behavior, the `~state` bitwise-NOT encoding, the five opacity override flag sources.
- Use `render.compute_shader.NoFlags.map_value.2.level_0` as the single representative shader walkthrough. Compute is the simplest pipeline, `NoFlags` exercises the unmodified micromap path, mode 2 has the smallest bit-packing, and level 0 produces a one-ray shader that is straightforward to compile and disassemble.
- Carry the `### Failure Cause Mapping` table verbatim into `## Failure Meaning`. The `### Cause Analysis` subsections should group causes by mechanism: micromap build / data layout, override flag handling, special-index encoding, base-triangle offset, pipeline create flag, copy path, maintenance5 buffer flags.
- Source-mapping table becomes the basis of `## Source Reference Appendix` with the same entries.
- The `nonZeroBase`, `copyType = Compact`, `useMaintenance5`, and `subdivisionLevel = 15` notes should feed `## Behavior Parameters` and `## Case Pruning` rather than be copied wholesale.
- The page should explicitly state that `CT_COMPACT` reuses `VK_COPY_MICROMAP_MODE_CLONE_EXT` because the source does, and flag this as a source-level question rather than a test-design defect.
