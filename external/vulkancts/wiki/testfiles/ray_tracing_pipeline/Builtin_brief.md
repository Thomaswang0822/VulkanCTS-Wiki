# Understanding Brief: ray_tracing_pipeline builtin and spec_constants families

## One-Sentence Test Purpose

This test checks whether `VK_KHR_ray_tracing_pipeline` shader built-in variables
(`gl_LaunchIDEXT`, `gl_LaunchSizeEXT`, `gl_PrimitiveID`, `gl_InstanceID`,
`gl_InstanceCustomIndexEXT`, `gl_GeometryIndexEXT`, ray origin/direction, `gl_RayTminEXT`,
`gl_RayTmaxEXT`, `gl_IncomingRayFlagsEXT`, `gl_HitTEXT`, `gl_HitKindEXT`,
`gl_ObjectToWorldEXT`, `gl_WorldToObjectEXT`, and the 3x4 variants) report the values
the Vulkan ray tracing pipeline spec requires, and whether specialization constants
supplied to ray tracing shaders through `VkSpecializationInfo` are honored across all
six ray tracing stages.

## Background Knowledge

### Ray tracing pipeline stages and built-ins

`VK_KHR_ray_tracing_pipeline` introduces six shader stages: raygen, closest-hit,
any-hit, miss, intersection, and callable. Each stage has read-only built-in inputs
defined by `GL_EXT_ray_tracing` (for example `gl_LaunchIDEXT`, `gl_LaunchSizeEXT`,
`gl_WorldRayOriginEXT`, `gl_HitKindEXT`, `gl_ObjectToWorldEXT`). The host launches a
ray tracing dispatch with `vkCmdTraceRaysKHR` or `vkCmdTraceRaysIndirectKHR` using a
launch extent `(width, height, depth)`. The implementation must populate these
built-ins with the values defined by the spec for the current invocation and the
current ray.

Why it matters here:
- The test writes a shader-built-in value into a 3D `r32i` storage image at the
  position given by `gl_LaunchIDEXT`, then the host compares the image against an
  independently computed expected buffer.
- Some built-ins are stage-specific. `gl_HitKindEXT` and `gl_HitTEXT` are only
  meaningful in any-hit, closest-hit, and intersection shaders. `gl_PrimitiveID`,
`gl_InstanceID`, `gl_InstanceCustomIndexEXT`, and `gl_GeometryIndexEXT` are
meaningful only in hit-group stages. `gl_WorldRayOriginEXT`,
`gl_WorldRayDirectionEXT`, `gl_RayTminEXT`, and `gl_RayTmaxEXT` are also valid in
miss shaders.

### Specialization constants in ray tracing pipelines

A ray tracing pipeline is a single `VkPipeline` carrying multiple shader groups.
`VkSpecializationInfo` can be attached per shader module when adding it to the
`RayTracingPipeline` builder. The implementation must replace the default
specialization constant values with the host-supplied data entries at pipeline
creation time. The host-side data block is byte-offset addressed through
`VkSpecializationMapEntry` records.

Why it matters here:
- The `spec_constants` family uses two specialization constants,
  `layout(constant_id=0) const int factor1` and `layout(constant_id=1) const float factor2`,
  in the launch-id builtin shader. The host deliberately lays out the
  specialization data block with byte offsets and padding so the implementation
  must honor `VkSpecializationMapEntry` offset and size fields, not just the
  default constant values.

### Indirect trace rays

`vkCmdTraceRaysIndirectKHR` reads the launch extent from a `VkTraceRaysIndirectCommand`
stored in a buffer, instead of taking width/height/depth as direct command arguments.
The `builtin.indirect` subfamily repeats selected built-in checks using the indirect
trace path with a small fixed geometry set.

## One Concrete Example

Representative shader for `ray_tracing_pipeline.spec_constants.rgen`:

```glsl
#version 460 core
#extension GL_EXT_ray_tracing : require
layout (constant_id=0) const highp int factor1   = 1;
layout (constant_id=1) const highp float factor2 = 2.0;
layout(set = 0, binding = 0, r32i) uniform iimage3D result;

void main()
{
  ivec3 p = ivec3(gl_LaunchIDEXT);
  ivec3 v = ivec3(gl_LaunchIDEXT);
  int   r = v.x + factor1 * (v.y + int(factor2) * v.z) + 1;
  ivec4 c = ivec4(r, 0, 0, 1);
  imageStore(result, p, c);
}
```

The host supplies `factor1 = 256` and `factor2 = 256.0f` through a
`VkSpecializationInfo` whose data block contains deliberate byte offsets and padding.
The expected image value at `(x, y, z)` is `x + 256 * (y + 256 * z) + 1`, identical
to the literal-256 form used by the matching `builtin.launchidext.rgen_*` case. The
`spec_constants` variant therefore exercises the same launch-id builtin through the
specialization constant substitution path rather than through hardcoded literals.

## End-to-End Test Flow

```text
[host] choose TestCase parameters (builtin id, stage, geometry type, sizes, ray flags, spec-constants flag)
[host] for indirect cases: build bottom/top acceleration structures with fixed geometry and instance offsets
[host] for direct cases: build bottom/top acceleration structures sized from squaresGroupCount, geometriesGroupCount, instancesGroupCount
[host] allocate 3D r32i storage image (direct cases) or storage buffer (indirect cases) for results
[host] compile ray tracing shaders; attach VkSpecializationInfo when useSpecConstants is true
[host] build RayTracingPipeline with raygen, miss, hit group, and optional intersection/callable shaders
[host] build shader binding table regions for each group
[host] clear result image to DEFAULT_UINT_CLEAR_VALUE; layout transition to GENERAL
[host] vkCmdTraceRaysKHR (direct) or vkCmdTraceRaysIndirectKHR (indirect) with (width, height, raysDepth)
[device] rgen invokes traceRayEXT; closest-hit/any-hit/intersection/miss/callable write the selected builtin into result
[host] pipeline barrier: shader-write to transfer-read
[host] vkCmdCopyImageToBuffer (direct) or already host-visible buffer (indirect)
[host] invalidate mapped memory; scan result entries against expected buffer
[host] pass only if every entry matches expected value (within FIXED_POINT_ALLOWED_ERROR for float-builtins)
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- GLSL `rgen` shader. For `builtin.launchidext.*` and `builtin.launchsizeext.*`,
  the shader writes `v.x + 256 * (v.y + 256 * v.z) + 1` to the result image. For
  `spec_constants.*` the `256` literals are replaced by `factor1` and
  `int(factor2)`, both supplied through specialization constants.
- GLSL `chit`, `ahit`, `miss`, `sect`, and `call` shaders. Each shader writes the
  selected builtin value into the result image at `gl_LaunchIDEXT`.
- Passthrough shaders (`getHitPassthrough`, `getMissPassthrough`,
  `getIntersectionPassthrough`) for stages that are present but not the stage
  under test.
- For `builtin.incomingrayflagsext.*`, a generated `rgen` shader that picks a ray
  flag combination per launch ID and a custom intersection shader that reports a
  hit kind chosen from the front-face/back-face flag.
- For `builtin.indirect.*`, a separate `RayTracingIndirectTestCase` builder
  generates `rgen`, `chit`, `ahit`, `miss`, and `sect` shaders that store
  `gl_PrimitiveID`, `gl_InstanceID`, `gl_InstanceCustomIndexEXT`, ray transform
  matrices, `gl_RayTminEXT`/`gl_RayTmaxEXT`, `gl_IncomingRayFlagsEXT`, or
  `gl_HitKindEXT` into a structured storage buffer instead of a 3D image.
- `vk::ShaderBuildOptions` targets `SPIRV_VERSION_1_4` for the regular cases.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| 3D `r32i` storage image (`result`) | yes | binding 0 | yes, written by `imageStore` | yes, copied to host buffer | Holds the per-invocation builtin value for direct cases |
| Top-level acceleration structure | yes | binding 1 (descriptor type `VK_DESCRIPTOR_TYPE_ACCELERATION_STRUCTURE_KHR`) | yes, read by `traceRayEXT` | no | Drives ray traversal for hit/miss/intersection stages |
| Bottom-level acceleration structure(s) | yes, with triangles or AABBs | referenced by TLAS | yes | no | Provides geometry for the selected builtin |
| Host-visible readback buffer | yes | transfer-destination | yes, written by `vkCmdCopyImageToBuffer` | yes | Used by host validation for direct cases |
| Indirect command buffer | yes for `builtin.indirect.*` | indirect-buffer source | read by `vkCmdTraceRaysIndirectKHR` | no | Supplies launch dimensions for the indirect path |
| Structured result buffer | yes for `builtin.indirect.*` | storage buffer binding 0 | yes, written by hit-group shaders | yes | Holds per-stage results for indirect verification |
| Shader binding table | yes | SBT regions per stage | read by the ray tracing dispatch | no | Routes raygen/miss/hit/callable groups |

## What Is Checked

- Each result image entry must equal the expected value computed by the host. The
  host has a separate expected-value generator for every builtin id:
  - `LaunchIDEXT`: `x + 256 * (y + 256 * z) + 1`.
  - `LaunchSizeEXT`: `width + 256 * (height + 256 * depth) + 1`, identical for
    every launch ID.
  - `PrimitiveID`: `pos % squaresGroupCount`.
  - `InstanceID`: `pos / (squaresGroupCount * geometriesGroupCount)`.
  - `InstanceCustomIndexEXT`: `2 * InstanceID` because the host sets
    `instanceCustomIndex = 2 * instanceId`.
  - `GeometryIndexEXT`: `(pos / squaresGroupCount) % geometriesGroupCount`.
  - `IncomingRayFlagsEXT`: bit-OR of the ray flags the host selected for that
    launch ID, with `DEFAULT_UINT_CLEAR_VALUE` substituted when the chosen flags
    cull the geometry for the stage under test.
  - `HitKindEXT`: `0xFEu` or `0xFFu` for triangles depending on geometry index,
    `0x7Eu` for AABBs, with `DEFAULT_UINT_CLEAR_VALUE` for any-hit on opaque
    geometry.
  - `HitTEXT`, `RayTminEXT`, `RayTmaxEXT`: float values derived from the
    ray-primitive distance, encoded as fixed-point through `FIXED_POINT_DIVISOR`
    and compared with `FIXED_POINT_ALLOWED_ERROR`.
  - `WorldRayOriginEXT`/`WorldRayDirectionEXT`/`ObjectRayOriginEXT`/`ObjectRayDirectionEXT`:
    vector values written across four image slices and compared in fixed-point form.
  - `ObjectToWorldEXT`/`WorldToObjectEXT`/3x4 variants: matrix values laid out
    across 16 image slices and compared in fixed-point form, with translation
    columns set from per-instance offsets.
- Indirect cases verify per-stage result counters in a structured result buffer:
  - `indices`: every ray reports the expected `primitiveId`, `instanceId`, and
    `instanceCustomIndex`.
  - `transforms`: miss, closest-hit, any-hit, and (for AABB) intersection results
    must each be `1`, set by the shader after a `fuzzy_check` against the
    expected world/object ray origin, direction, and transform matrices.
  - `t_min_max`: same per-stage counter pattern for `gl_RayTminEXT`/`gl_RayTmaxEXT`.
  - `incoming_flag`: per-stage counters must fall inside host-computed min/max
    ranges that depend on opacity, skip-closest-hit, and geometry type.
  - `hit_kind`: per-stage counters must equal `1` for both `chit` and `ahit`.

## Behavior Parameter Identification

> **Behavior parameter:** test family
>
> **Candidate values:** `builtin`, `spec_constants`

The page covers two test families rooted in the same source file. Each family
changes what is being tested:

- `builtin` varies the built-in id, the shader stage, the geometry type, the
  launch dimensions, and (for `incomingrayflagsext`) the ray/pipeline culling
  flags. It also includes an `indirect` subfamily that exercises the same
  built-ins through `vkCmdTraceRaysIndirectKHR`.
- `spec_constants` fixes the built-in to `LaunchIDEXT` and the launch dimensions
  to `256x256x1`, then varies only the shader stage. The host supplies
  specialization constants so that `factor1` and `factor2` replace the literal
  `256` used in the matching `builtin.launchidext` cases.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `builtin` | A ray tracing shader built-in returned a value other than what the spec requires for the current invocation, ray, geometry, or stage. Includes the `indirect` subfamily where the failure also implicates the indirect trace path or the structured result buffer verification. |
| `spec_constants` | The implementation did not substitute the host-supplied specialization constant values into the launch-id shader for the selected ray tracing stage, or the specialization data byte-offset layout was not honored. |

## Important Variations and Special Cases

- `builtin.incomingrayflagsext` is the most parameter-heavy subfamily. It varies
  geometry type (triangles or AABBs), per-ray skip flags (`raynoskipflags`,
  `rayskiptriangles`, `rayskipaabbs`), pipeline skip flags
  (`pipelinenoskipflags`, `pipelineskiptriangles`, `pipelineskipaabbs`),
  geometry opacity, and face orientation. It also has a `misc` subgroup that uses
  `VK_KHR_maintenance5` (`pipelineCreateFlags2`) to set the same skip-triangles
  and skip-AABBs flags through the maintenance5 path.
- Culling-flag combinations that skip both triangles and AABBs are pruned because
  the spec forbids that combination.
- `SkipTrianglesKHR` is mutually exclusive with `CullBackFacingTrianglesKHR` and
  `CullFrontFacingTrianglesKHR`, so triangle-ray-flag-skip cases without a
  matching pipeline skip flag are also pruned.
- `HitTEXT` and `RayTmaxEXT` expected values differ across stages: the miss
  shader sees the original `tmax` passed to `traceRayEXT`, the closest-hit
  shader sees the closest-hit distance, the any-hit shader sees the current
  primitive distance, and the intersection shader sees the closest reported
  distance so far.
- The `builtin.indirect.*` subfamily uses a different test instance
  (`RayTracingIndirectTestInstance`), a structured result buffer instead of a 3D
  image, and shader-side `fuzzy_check` helpers for transform and t-min/max
  verification.
- The `spec_constants` family forces `id == TEST_ID_LAUNCH_ID_EXT` and asserts
  that specialization constants are only used in that id. The host
  `SpecConstantsHelper` deliberately misaligns the two constant values inside the
  data block to test offset handling.
- The `useMaintenance5` flag in `incomingrayflagsext.misc.*` switches the
  pipeline creation flag path from `VkPipelineCreateFlags` to
  `VkPipelineCreateFlags2` through `setCreateFlags2(translateCreateFlag(...))`.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| `CaseDef` and `TestId` enum | [vktRayTracingBuiltinTests.cpp#L59-L135](../../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L59-L135) | Defines the per-case parameter struct and the builtin id enumeration. |
| Ray tracing passthrough shaders | [vktRayTracingBuiltinTests.cpp#L345-L384](../../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L345-L384) | Provides hit/miss/intersection passthrough shaders used when those stages are not the stage under test. |
| `initPrograms` for launch-id / launch-size with and without spec constants | [vktRayTracingBuiltinTests.cpp#L386-L598](../../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L386-L598) | Generates the rgen/ahit/chit/miss/sect/call shaders for launch-id and launch-size, with spec-constant variants. |
| `initPrograms` for scalar/vector/matrix/flags builtins | [vktRayTracingBuiltinTests.cpp#L599-L1185](../../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L599-L1185) | Generates shaders for primitive/instance/geometry indices, ray params, transforms, and incoming-ray-flags. |
| `runTest` direct case execution | [vktRayTracingBuiltinTests.cpp#L1777-L1931](../../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L1777-L1931) | Builds pipeline and SBT, dispatches `vkCmdTraceRaysKHR`, copies image to host buffer. |
| Expected-value generators | [vktRayTracingBuiltinTests.cpp#L1985-L2366](../../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L1985-L2366) | Computes per-builtin expected int/float/vector/matrix buffers used by host validation. |
| Validation routines | [vktRayTracingBuiltinTests.cpp#L2368-L2608](../../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L2368-L2608) | Per-pixel comparison against expected buffer with fixed-point tolerance for float builtins. |
| `iterate` direct instance | [vktRayTracingBuiltinTests.cpp#L2610-L2624](../../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L2610-L2624) | Dispatches to the right validator and returns pass/fail. |
| `SpecConstantsHelper` | [vktRayTracingBuiltinTests.cpp#L1735-L1775](../../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L1735-L1775) | Builds the deliberately misaligned specialization info block. |
| `RayTracingIndirectTestCase::initPrograms` | [vktRayTracingBuiltinTests.cpp#L2866-L3383](../../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L2866-L3383) | Generates the indirect-trace shaders for indices/transforms/t_min_max/incoming_flag/hit_kind. |
| `RayTracingIndirectTestInstance::iterate` | [vktRayTracingBuiltinTests.cpp#L4062-L4172](../../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L4062-L4172) | Builds indirect command buffer, dispatches `vkCmdTraceRaysIndirectKHR`, validates. |
| `RayTracingIndirectTestInstance::verifyResults` | [vktRayTracingBuiltinTests.cpp#L3946-L4060](../../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L3946-L4060) | Per-id structured-buffer verification. |
| `createBuiltinTests` registration | [vktRayTracingBuiltinTests.cpp#L4753-L4807](../../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L4753-L4807) | Registers the `builtin` family and its 19 builtin subgroups plus `indirect`. |
| `createSpecConstantTests` registration | [vktRayTracingBuiltinTests.cpp#L4809-L4861](../../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L4809-L4861) | Registers the `spec_constants` family with one leaf per stage. |
| Stages array | [vktRayTracingBuiltinTests.cpp#L4174-L4182](../../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L4174-L4182) | Names the six stage leaves `rgen`, `ahit`, `chit`, `sect`, `miss`, `call`. |

## Questions / Risk Points for User Audit

- Is the core test purpose clear: built-in correctness plus specialization-constant
  substitution, with an indirect-trace subfamily for selected builtins?
- Is the host/device timeline understandable, including the difference between
  the 3D-image path used by direct cases and the structured-buffer path used by
  indirect cases?
- Are the generated GLSL artifacts distinguished from real GPU resources, and is
  the role of the passthrough shaders clear?
- Is the `builtin.indirect.*` subfamily correctly described as part of the
  `builtin` family rather than as a separate family?
- The `spec_constants` family only covers `LaunchIDEXT`. Is that scope correctly
  reflected, or should the page also mention that the same shader generator
  supports spec constants for `LaunchSizeEXT` even though the registered family
  only uses `LaunchIDEXT`?
- Is the choice of `ray_tracing_pipeline.spec_constants.rgen` as the
  representative shader walkthrough appropriate, given that it exercises both
  tested families in a single shader?

## Conversion Notes for Final Wiki Rewrite

- The brief's Background Knowledge should be distilled to a short unordered list
  in the final page's `## Background Knowledge`, similar to the
  `MessagePassing.md` pilot.
- The `### Failure Cause Mapping` table above will be copied verbatim into the
  final page's `## Failure Meaning` section.
- The concrete example becomes the representative shader walkthrough for the
  `spec_constants.rgen` case. The matching `builtin.launchidext.rgen_*` case uses
  the same shader with literal `256` instead of specialization constants, so a
  single walkthrough is enough; the difference is summarized in a parameter
  variation note.
- The two test families are the primary behavioral axis for `## Behavior
  Parameters`. Within `builtin`, the registered builtin ids and the
  `indirect` subfamily are mentioned as a secondary axis through the parameter
  dimensions table, not as separate subsections.
- The structured-buffer verification for `builtin.indirect.*` is described in
  `## Runtime Execution and Result Checking` rather than as a separate
  walkthrough, because it shares the same shader structure as the direct cases
  but writes to a different resource.
- The host-side `SpecConstantsHelper` misalignment detail belongs in
  `## Runtime Execution and Result Checking` because it is host behavior, not
  shader behavior.
