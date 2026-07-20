## Overview

**Core question:** Does `VK_EXT_opacity_micromap` resolve the correct opacity state for each subtriangle a ray hits, under every valid combination of opacity-forcing, culling, force-2-state, and disable-micromap flags?

This page covers the `opacity_micromap` test family registered from [vktRayTracingOpacityMicromapTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingOpacityMicromapTests.cpp#L818-L936):

- The family attaches an opacity micromap to a single triangle, traces one ray per subtriangle at the subtriangle centroid, and records which shader stage executed (miss, any-hit, or closest-hit) as the output mode.
- The host computes the expected output mode for each ray using the same micromap data and the same flag precedence rules the spec defines for traversal, then compares entry by entry.
- 120 direct children are registered, one per valid combination of nine test flags controlling opacity forcing, culling, force-2-state, and disable-micromap behavior. Each child has `map_value` and `special_index` subgroups that vary the micromap data source, format, subdivision level, and base triangle offset.
- The page explains the flag-based behavioral axis, the opacity resolution logic, the representative raygen shader, the host-side expected value computation, and what each failure mode means.

## Background Knowledge

- `VK_EXT_opacity_micromap` attaches a compact opacity lookup table to triangle geometry in a bottom-level acceleration structure. Each triangle references a micromap that subdivides it into `4^level` subtriangles. During traversal, the implementation looks up the opacity state of the hit subtriangle to decide whether to skip the any-hit shader (opaque), run it (non-opaque), or let the ray pass through (transparent).
- Four special index values represent opacity states: `FULLY_TRANSPARENT` (-1), `FULLY_OPAQUE` (-2), `FULLY_UNKNOWN_TRANSPARENT` (-3), `FULLY_UNKNOWN_OPAQUE` (-4). The two unknown states only exist in 4-state format.
- The test converts per-subtriangle data values to special index space using bitwise NOT, so data 0 maps to `FULLY_TRANSPARENT`, 1 to `FULLY_OPAQUE`, 2 to `FULLY_UNKNOWN_TRANSPARENT`, and 3 to `FULLY_UNKNOWN_OPAQUE`.
- Instance flags (`VK_GEOMETRY_INSTANCE_FORCE_OPAQUE_BIT_KHR`, `VK_GEOMETRY_INSTANCE_FORCE_NO_OPAQUE_BIT_KHR`, `VK_GEOMETRY_INSTANCE_FORCE_OPACITY_MICROMAP_2_STATE_EXT`, `VK_GEOMETRY_INSTANCE_DISABLE_OPACITY_MICROMAPS_EXT`) and ray flags (`gl_RayFlagsOpaqueEXT`, `gl_RayFlagsNoOpaqueEXT`, `gl_RayFlagsCullOpaqueEXT`, `gl_RayFlagsCullNoOpaqueEXT`, `gl_RayFlagsForceOpacityMicromap2StateEXT`) modify how the resolved opacity state is interpreted during traversal.
- Force-opaque and force-no-opaque are mutually exclusive at both instance and ray level. At most one of the four opacity ray flags can be set per ray.
- The pipeline is created with `VK_PIPELINE_CREATE_RAY_TRACING_OPACITY_MICROMAP_BIT_EXT` to enable the opacity micromap path.

## Registration Hierarchy

```text
ray_tracing_pipeline.opacity_micromap
├── NoFlags
├── cull_no_opaque_ray_flag
├── cull_opaque_ray_flag
├── disable_opacity_micromap_instance
├── disable_opacity_micromap_instance_cull_no_opaque_ray_flag
├── disable_opacity_micromap_instance_cull_opaque_ray_flag
├── disable_opacity_micromap_instance_force_2_state_instance
├── disable_opacity_micromap_instance_force_2_state_instance_cull_no_opaque_ray_flag
├── disable_opacity_micromap_instance_force_2_state_instance_cull_opaque_ray_flag
├── disable_opacity_micromap_instance_force_2_state_instance_force_2_state_ray_flag
├── disable_opacity_micromap_instance_force_2_state_instance_force_2_state_ray_flag_cull_no_opaque_ray_flag
├── disable_opacity_micromap_instance_force_2_state_instance_force_2_state_ray_flag_cull_opaque_ray_flag
├── disable_opacity_micromap_instance_force_2_state_instance_force_2_state_ray_flag_force_no_opaque_instance
├── disable_opacity_micromap_instance_force_2_state_instance_force_2_state_ray_flag_force_no_opaque_instance_cull_no_opaque_ray_flag
├── disable_opacity_micromap_instance_force_2_state_instance_force_2_state_ray_flag_force_no_opaque_instance_cull_opaque_ray_flag
├── disable_opacity_micromap_instance_force_2_state_instance_force_2_state_ray_flag_force_no_opaque_instance_no_opaque_ray_flag
├── disable_opacity_micromap_instance_force_2_state_instance_force_2_state_ray_flag_no_opaque_ray_flag
├── disable_opacity_micromap_instance_force_2_state_instance_force_no_opaque_instance
├── disable_opacity_micromap_instance_force_2_state_instance_force_no_opaque_instance_cull_no_opaque_ray_flag
├── disable_opacity_micromap_instance_force_2_state_instance_force_no_opaque_instance_cull_opaque_ray_flag
├── disable_opacity_micromap_instance_force_2_state_instance_force_no_opaque_instance_no_opaque_ray_flag
├── disable_opacity_micromap_instance_force_2_state_instance_no_opaque_ray_flag
├── disable_opacity_micromap_instance_force_2_state_ray_flag
├── disable_opacity_micromap_instance_force_2_state_ray_flag_cull_no_opaque_ray_flag
├── disable_opacity_micromap_instance_force_2_state_ray_flag_cull_opaque_ray_flag
├── disable_opacity_micromap_instance_force_2_state_ray_flag_force_no_opaque_instance
├── disable_opacity_micromap_instance_force_2_state_ray_flag_force_no_opaque_instance_cull_no_opaque_ray_flag
├── disable_opacity_micromap_instance_force_2_state_ray_flag_force_no_opaque_instance_cull_opaque_ray_flag
├── disable_opacity_micromap_instance_force_2_state_ray_flag_force_no_opaque_instance_no_opaque_ray_flag
├── disable_opacity_micromap_instance_force_2_state_ray_flag_no_opaque_ray_flag
├── disable_opacity_micromap_instance_force_no_opaque_instance
├── disable_opacity_micromap_instance_force_no_opaque_instance_cull_no_opaque_ray_flag
├── disable_opacity_micromap_instance_force_no_opaque_instance_cull_opaque_ray_flag
├── disable_opacity_micromap_instance_force_no_opaque_instance_no_opaque_ray_flag
├── disable_opacity_micromap_instance_no_opaque_ray_flag
├── force_2_state_instance
├── force_2_state_instance_cull_no_opaque_ray_flag
├── force_2_state_instance_cull_opaque_ray_flag
├── force_2_state_instance_force_2_state_ray_flag
├── force_2_state_instance_force_2_state_ray_flag_cull_no_opaque_ray_flag
├── force_2_state_instance_force_2_state_ray_flag_cull_opaque_ray_flag
├── force_2_state_instance_force_2_state_ray_flag_force_no_opaque_instance
├── force_2_state_instance_force_2_state_ray_flag_force_no_opaque_instance_cull_no_opaque_ray_flag
├── force_2_state_instance_force_2_state_ray_flag_force_no_opaque_instance_cull_opaque_ray_flag
├── force_2_state_instance_force_2_state_ray_flag_force_no_opaque_instance_no_opaque_ray_flag
├── force_2_state_instance_force_2_state_ray_flag_no_opaque_ray_flag
├── force_2_state_instance_force_no_opaque_instance
├── force_2_state_instance_force_no_opaque_instance_cull_no_opaque_ray_flag
├── force_2_state_instance_force_no_opaque_instance_cull_opaque_ray_flag
├── force_2_state_instance_force_no_opaque_instance_no_opaque_ray_flag
├── force_2_state_instance_no_opaque_ray_flag
├── force_2_state_ray_flag
├── force_2_state_ray_flag_cull_no_opaque_ray_flag
├── force_2_state_ray_flag_cull_opaque_ray_flag
├── force_2_state_ray_flag_force_no_opaque_instance
├── force_2_state_ray_flag_force_no_opaque_instance_cull_no_opaque_ray_flag
├── force_2_state_ray_flag_force_no_opaque_instance_cull_opaque_ray_flag
├── force_2_state_ray_flag_force_no_opaque_instance_no_opaque_ray_flag
├── force_2_state_ray_flag_no_opaque_ray_flag
├── force_no_opaque_instance
├── force_no_opaque_instance_cull_no_opaque_ray_flag
├── force_no_opaque_instance_cull_opaque_ray_flag
├── force_no_opaque_instance_no_opaque_ray_flag
├── force_opaque_instance
├── force_opaque_instance_cull_no_opaque_ray_flag
├── force_opaque_instance_cull_opaque_ray_flag
├── force_opaque_instance_disable_opacity_micromap_instance
├── force_opaque_instance_disable_opacity_micromap_instance_cull_no_opaque_ray_flag
├── force_opaque_instance_disable_opacity_micromap_instance_cull_opaque_ray_flag
├── force_opaque_instance_disable_opacity_micromap_instance_force_2_state_instance
├── force_opaque_instance_disable_opacity_micromap_instance_force_2_state_instance_cull_no_opaque_ray_flag
├── force_opaque_instance_disable_opacity_micromap_instance_force_2_state_instance_cull_opaque_ray_flag
├── force_opaque_instance_disable_opacity_micromap_instance_force_2_state_instance_force_2_state_ray_flag
├── force_opaque_instance_disable_opacity_micromap_instance_force_2_state_instance_force_2_state_ray_flag_cull_no_opaque_ray_flag
├── force_opaque_instance_disable_opacity_micromap_instance_force_2_state_instance_force_2_state_ray_flag_cull_opaque_ray_flag
├── force_opaque_instance_disable_opacity_micromap_instance_force_2_state_instance_force_2_state_ray_flag_no_opaque_ray_flag
├── force_opaque_instance_disable_opacity_micromap_instance_force_2_state_instance_no_opaque_ray_flag
├── force_opaque_instance_disable_opacity_micromap_instance_force_2_state_ray_flag
├── force_opaque_instance_disable_opacity_micromap_instance_force_2_state_ray_flag_cull_no_opaque_ray_flag
├── force_opaque_instance_disable_opacity_micromap_instance_force_2_state_ray_flag_cull_opaque_ray_flag
├── force_opaque_instance_disable_opacity_micromap_instance_force_2_state_ray_flag_no_opaque_ray_flag
├── force_opaque_instance_disable_opacity_micromap_instance_no_opaque_ray_flag
├── force_opaque_instance_force_2_state_instance
├── force_opaque_instance_force_2_state_instance_cull_no_opaque_ray_flag
├── force_opaque_instance_force_2_state_instance_cull_opaque_ray_flag
├── force_opaque_instance_force_2_state_instance_force_2_state_ray_flag
├── force_opaque_instance_force_2_state_instance_force_2_state_ray_flag_cull_no_opaque_ray_flag
├── force_opaque_instance_force_2_state_instance_force_2_state_ray_flag_cull_opaque_ray_flag
├── force_opaque_instance_force_2_state_instance_force_2_state_ray_flag_no_opaque_ray_flag
├── force_opaque_instance_force_2_state_instance_no_opaque_ray_flag
├── force_opaque_instance_force_2_state_ray_flag
├── force_opaque_instance_force_2_state_ray_flag_cull_no_opaque_ray_flag
├── force_opaque_instance_force_2_state_ray_flag_cull_opaque_ray_flag
├── force_opaque_instance_force_2_state_ray_flag_no_opaque_ray_flag
├── force_opaque_instance_force_opaque_ray_flag
├── force_opaque_instance_force_opaque_ray_flag_disable_opacity_micromap_instance
├── force_opaque_instance_force_opaque_ray_flag_disable_opacity_micromap_instance_force_2_state_instance
├── force_opaque_instance_force_opaque_ray_flag_disable_opacity_micromap_instance_force_2_state_instance_force_2_state_ray_flag
├── force_opaque_instance_force_opaque_ray_flag_disable_opacity_micromap_instance_force_2_state_ray_flag
├── force_opaque_instance_force_opaque_ray_flag_force_2_state_instance
├── force_opaque_instance_force_opaque_ray_flag_force_2_state_instance_force_2_state_ray_flag
├── force_opaque_instance_force_opaque_ray_flag_force_2_state_ray_flag
├── force_opaque_instance_no_opaque_ray_flag
├── force_opaque_ray_flag
├── force_opaque_ray_flag_disable_opacity_micromap_instance
├── force_opaque_ray_flag_disable_opacity_micromap_instance_force_2_state_instance
├── force_opaque_ray_flag_disable_opacity_micromap_instance_force_2_state_instance_force_2_state_ray_flag
├── force_opaque_ray_flag_disable_opacity_micromap_instance_force_2_state_instance_force_2_state_ray_flag_force_no_opaque_instance
├── force_opaque_ray_flag_disable_opacity_micromap_instance_force_2_state_instance_force_no_opaque_instance
├── force_opaque_ray_flag_disable_opacity_micromap_instance_force_2_state_ray_flag
├── force_opaque_ray_flag_disable_opacity_micromap_instance_force_2_state_ray_flag_force_no_opaque_instance
├── force_opaque_ray_flag_disable_opacity_micromap_instance_force_no_opaque_instance
├── force_opaque_ray_flag_force_2_state_instance
├── force_opaque_ray_flag_force_2_state_instance_force_2_state_ray_flag
├── force_opaque_ray_flag_force_2_state_instance_force_2_state_ray_flag_force_no_opaque_instance
├── force_opaque_ray_flag_force_2_state_instance_force_no_opaque_instance
├── force_opaque_ray_flag_force_2_state_ray_flag
├── force_opaque_ray_flag_force_2_state_ray_flag_force_no_opaque_instance
├── force_opaque_ray_flag_force_no_opaque_instance
└── no_opaque_ray_flag
```

Each direct child is a test flag mask name. Under each child, the registration adds a `map_value` subgroup (per-subtriangle data with 2-state and 4-state formats, levels 0 through 15) and a `special_index` subgroup (four special index values 0 through 3). The `NoFlags` child also adds `_non_zero_base` variants for every `map_value` level. The `special_index` subgroup forces subdivision level to 0 because the entire triangle uses one special index value.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test flag mask | 120 valid combinations of 9 flags | Controls opacity forcing, culling, force-2-state, and disable-micromap behavior. Each combination produces a different opacity resolution path. | [vktRayTracingOpacityMicromapTests.cpp#L834-L933](../../../modules/vulkan/ray_tracing/vktRayTracingOpacityMicromapTests.cpp#L834-L933) |
| Micromap data source | `map_value`, `special_index` | `map_value` uses per-subtriangle data from the micromap buffer. `special_index` uses a single special index for the entire triangle. | [vktRayTracingOpacityMicromapTests.cpp#L829-L832](../../../modules/vulkan/ray_tracing/vktRayTracingOpacityMicromapTests.cpp#L829-L832) |
| Micromap format | `2`, `4` | 2-state format uses 1 bit per subtriangle (opaque or transparent). 4-state format uses 2 bits, adding the two unknown states. Only used with `map_value`. | [vktRayTracingOpacityMicromapTests.cpp#L893-L927](../../../modules/vulkan/ray_tracing/vktRayTracingOpacityMicromapTests.cpp#L893-L927) |
| Subdivision level | `level_0` through `level_15` | Controls micromap subdivision depth. Level L produces `4^L` subtriangles and the same number of rays. Only used with `map_value`. | [vktRayTracingOpacityMicromapTests.cpp#L902-L925](../../../modules/vulkan/ray_tracing/vktRayTracingOpacityMicromapTests.cpp#L902-L925) |
| Special index | `0`, `1`, `2`, `3` | Selects which special index value the micromap uses. Maps to `~specialIndex`: 0 becomes `FULLY_TRANSPARENT`, 1 becomes `FULLY_OPAQUE`, 2 becomes `FULLY_UNKNOWN_TRANSPARENT`, 3 becomes `FULLY_UNKNOWN_OPAQUE`. Only used with `special_index`. | [vktRayTracingOpacityMicromapTests.cpp#L876-L887](../../../modules/vulkan/ray_tracing/vktRayTracingOpacityMicromapTests.cpp#L876-L887) |
| Non-zero base | enabled, disabled | When enabled, `baseTriangle = 1` with two triangles in the geometry; only the second triangle has a micromap. Only registered for `NoFlags`. | [vktRayTracingOpacityMicromapTests.cpp#L919-L924](../../../modules/vulkan/ray_tracing/vktRayTracingOpacityMicromapTests.cpp#L919-L924) |

## Behavior Parameters

The primary behavioral axis is the test flag mask, which controls how the resolved opacity state is interpreted during traversal. The 120 registered direct children are all valid combinations of nine flags. These flags cluster into seven behavioral categories. Each category tests a distinct opacity resolution mechanism; combinations test their interactions.

### NoFlags — baseline opacity resolution from micromap data

No opacity, culling, force-2-state, or disable flags are set. The implementation resolves each subtriangle's opacity state directly from the micromap data and runs the appropriate shader stage. This baseline verifies that the micromap build, data lookup, and subtriangle centroid intersection all work correctly without any flag-driven overrides.

### force_opaque — force geometry to be opaque

Set via `VK_GEOMETRY_INSTANCE_FORCE_OPAQUE_BIT_KHR` (instance) or `gl_RayFlagsOpaqueEXT` (ray flag). The resolved opacity state is forced to `FULLY_OPAQUE` for any subtriangle that is not `FULLY_TRANSPARENT`. The any-hit shader is skipped, and the closest-hit shader runs. Ray flags take precedence over instance flags. When both force-opaque instance and force-opaque ray flag are set, the behavior is the same as either alone.

### force_no_opaque — force geometry to be non-opaque

Set via `VK_GEOMETRY_INSTANCE_FORCE_NO_OPAQUE_BIT_KHR` (instance) or `gl_RayFlagsNoOpaqueEXT` (ray flag). The resolved opacity state is forced to `FULLY_UNKNOWN_OPAQUE` for any subtriangle that is not `FULLY_TRANSPARENT`, including `FULLY_OPAQUE` subtriangles, so the any-hit shader runs. This flag is mutually exclusive with force-opaque at both instance and ray level. Force-opaque and force-no-opaque ray flags are also mutually exclusive with the cull ray flags.

### cull_opaque — cull rays that hit opaque geometry

Set via `gl_RayFlagsCullOpaqueEXT`. The ray is culled (treated as a miss) when the resolved opacity is opaque, considering force-opaque instance flags but not force-no-opaque. The cull check happens before force-opaque or force-no-opaque ray flags are applied to the state. This flag is one of four mutually exclusive opacity ray flags.

### cull_no_opaque — cull rays that hit non-opaque geometry

Set via `gl_RayFlagsCullNoOpaqueEXT`. The ray is culled when the resolved opacity is not opaque, considering force-no-opaque instance flags. When force-opaque instance is set, the state is opaque, so cull-no-opaque does not cull. This flag is one of four mutually exclusive opacity ray flags.

### force_2_state — collapse 4-state unknowns to 2-state equivalents

Set via `VK_GEOMETRY_INSTANCE_FORCE_OPACITY_MICROMAP_2_STATE_EXT` (instance) or `gl_RayFlagsForceOpacityMicromap2StateEXT` (ray flag). After the micromap lookup, `FULLY_UNKNOWN_TRANSPARENT` becomes `FULLY_TRANSPARENT` and `FULLY_UNKNOWN_OPAQUE` becomes `FULLY_OPAQUE`. This collapse happens before force-opaque, force-no-opaque, and culling are applied. The flag affects 4-state format cases; 2-state cases have no unknown states to collapse.

### disable_opacity_micromap — bypass the micromap and use geometry opacity

Set via `VK_GEOMETRY_INSTANCE_DISABLE_OPACITY_MICROMAPS_EXT`. The micromap is bypassed entirely, and the geometry's own opacity is used. The test geometry is non-opaque (no `VK_GEOMETRY_OPAQUE_BIT_KHR` flag), so the any-hit shader runs. The bottom-level AS must be built with `VK_BUILD_ACCELERATION_STRUCTURE_ALLOW_DISABLE_OPACITY_MICROMAPS_EXT` for this flag to take effect. When the micromap is disabled, the resolved state starts as `FULLY_UNKNOWN_OPAQUE`, and force-opaque or force-no-opaque flags can still override it.

## Shader Analysis

The page uses one representative walkthrough because the raygen shader is the same across all cases; only the `flagsString` passed to `traceRayEXT` changes with the test flag mask. The any-hit, closest-hit, and miss shaders are fixed across all cases.

### Representative Shader Walkthrough 1

**CTS case:** `ray_tracing_pipeline.opacity_micromap.NoFlags.map_value.2.level_0`

**Source location:** [vktRayTracingOpacityMicromapTests.cpp#L163-L214](../../../modules/vulkan/ray_tracing/vktRayTracingOpacityMicromapTests.cpp#L163-L214)

**What this shader tests:** The raygen shader reads a ray origin from the origins SSBO, initializes the payload to `0xFFFFFFFF`, traces a ray downward through the triangle, and writes the payload result into the modes SSBO. With `NoFlags`, `flagsString` is `gl_RayFlagsNoneEXT`, so the implementation resolves opacity purely from the micromap data. With subdivision level 0, there is one subtriangle and one ray. The any-hit, closest-hit, or miss shader runs depending on the resolved opacity state, and the payload value (0, 1, or 2) records which stage executed.

**Shader-visible resources:**

- `%topLevelAS` (`accelerationStructureEXT`, set 0, binding 0): top-level acceleration structure with one instance.
- `%origins` (`RayOrigins`, set 0, binding 1, `std430`): SSBO with `vec4` ray origins, one per subtriangle.
- `%modes` (`OutputModes`, set 0, binding 2, `std430`): SSBO receiving `uint` output modes, one per ray.
- `%value` (`rayPayloadEXT`, location 0): `uint` payload set to `0xFFFFFFFF` before tracing, then overwritten by miss (0), any-hit (1), or closest-hit (2).
- `%gl_LaunchIDEXT` (`vec3 uint`, `BuiltIn LaunchIdKHR`): input built-in indexing the current ray.

**Reconstructed GLSL:**

```glsl
#version 460 core
#extension GL_EXT_ray_tracing : require
#extension GL_EXT_opacity_micromap : require
/// Ray payload: 0xFFFFFFFF before trace, 0 (miss), 1 (any-hit), or 2 (closest-hit) after.
layout(location=0) rayPayloadEXT uint value;
/// Top-level AS at binding 0; one instance with flag-dependent instance flags.
layout(set=0, binding=0) uniform accelerationStructureEXT topLevelAS;
/// Ray origins at binding 1; one vec4 per subtriangle centroid.
layout(set=0, binding=1, std430) buffer RayOrigins {
  vec4 values[1];
} origins;
/// Output modes at binding 2; one uint per ray.
layout(set=0, binding=2, std430) buffer OutputModes {
  uint values[1];
} modes;

void main()
{
  const uint  cullMask  = 0xFF;
  /// Origin comes from the SSBO, indexed by launch id.
  const vec3  origin    = origins.values[gl_LaunchIDEXT.x].xyz;
  const vec3  direction = vec3(0.0, 0.0, -1.0);
  const float tMin      = 0.0;
  const float tMax      = 2.0;
  value                 = 0xFFFFFFFF;
  /// NoFlags case: gl_RayFlagsNoneEXT. Other cases OR in force/cull flags here.
  traceRayEXT(topLevelAS, gl_RayFlagsNoneEXT, cullMask, 0, 0, 0, origin, tMin, direction, tMax, 0);
  modes.values[gl_LaunchIDEXT.x] = value;
}
```

**Any-hit shader (fixed across all cases):** Sets `value = 1` and calls `terminateRayEXT`, preventing the closest-hit shader from running.

**Closest-hit shader (fixed across all cases):** Sets `value = 2` only if `value != 1`, meaning the any-hit shader did not already run.

**Miss shader (fixed across all cases):** Sets `value = 0`.

Built with `glslangValidator -V --target-env spirv1.4 -S rgen`. Validated with `spirv-val --target-env spv1.4`. SPIR-V version 1.4, Bound 52. **Target SPIR-V environment:** `spirv1.4` (CTS build options target `vk::SPIRV_VERSION_1_4`).

**Parameter variation note:** When the test flag mask includes force-opaque, no-opaque, cull-opaque, cull-no-opaque, or force-2-state ray flags, the source generator ORs the corresponding `gl_RayFlags*EXT` constant into `flagsString` before passing it to `traceRayEXT`. The shader structure, resource layout, and payload logic are otherwise identical across all 120 flag combinations. For subdivision levels above 0, the `values` array size in both SSBOs grows to `4^level`, and the host writes one ray origin per subtriangle centroid.

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `rgen`
- Target SPIRV version: `spirv1.4`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.4
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 52
; Schema: 0
               OpCapability RayTracingKHR
               OpCapability RayTracingOpacityMicromapEXT
               OpExtension "SPV_EXT_opacity_micromap"
               OpExtension "SPV_KHR_ray_tracing"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint RayGenerationKHR %main "main" %origins %gl_LaunchIDEXT %value %topLevelAS %modes
               OpSource GLSL 460
               OpSourceExtension "GL_EXT_opacity_micromap"
               OpSourceExtension "GL_EXT_ray_tracing"
               OpName %main "main"
               OpName %origin "origin"
               OpName %RayOrigins "RayOrigins"
               OpMemberName %RayOrigins 0 "values"
               OpName %origins "origins"
               OpName %gl_LaunchIDEXT "gl_LaunchIDEXT"
               OpName %value "value"
               OpName %topLevelAS "topLevelAS"
               OpName %OutputModes "OutputModes"
               OpMemberName %OutputModes 0 "values"
               OpName %modes "modes"
               OpDecorate %_arr_v4float_uint_1 ArrayStride 16
               OpDecorate %RayOrigins Block
               OpMemberDecorate %RayOrigins 0 Offset 0
               OpDecorate %origins Binding 1
               OpDecorate %origins DescriptorSet 0
               OpDecorate %gl_LaunchIDEXT BuiltIn LaunchIdKHR
               OpDecorate %topLevelAS Binding 0
               OpDecorate %topLevelAS DescriptorSet 0
               OpDecorate %_arr_uint_uint_1 ArrayStride 4
               OpDecorate %OutputModes Block
               OpMemberDecorate %OutputModes 0 Offset 0
               OpDecorate %modes Binding 2
               OpDecorate %modes DescriptorSet 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v3float = OpTypeVector %float 3
%_ptr_Function_v3float = OpTypePointer Function %v3float
    %v4float = OpTypeVector %float 4
       %uint = OpTypeInt 32 0
     %uint_1 = OpConstant %uint 1
%_arr_v4float_uint_1 = OpTypeArray %v4float %uint_1
 %RayOrigins = OpTypeStruct %_arr_v4float_uint_1
%_ptr_StorageBuffer_RayOrigins = OpTypePointer StorageBuffer %RayOrigins
    %origins = OpVariable %_ptr_StorageBuffer_RayOrigins StorageBuffer
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_LaunchIDEXT = OpVariable %_ptr_Input_v3uint Input
     %uint_0 = OpConstant %uint 0
%_ptr_Input_uint = OpTypePointer Input %uint
%_ptr_StorageBuffer_v4float = OpTypePointer StorageBuffer %v4float
%_ptr_RayPayloadKHR_uint = OpTypePointer RayPayloadKHR %uint
      %value = OpVariable %_ptr_RayPayloadKHR_uint RayPayloadKHR
%uint_4294967295 = OpConstant %uint 4294967295
         %33 = OpTypeAccelerationStructureKHR
%_ptr_UniformConstant_33 = OpTypePointer UniformConstant %33
 %topLevelAS = OpVariable %_ptr_UniformConstant_33 UniformConstant
   %uint_255 = OpConstant %uint 255
    %float_0 = OpConstant %float 0
   %float_n1 = OpConstant %float -1
         %41 = OpConstantComposite %v3float %float_0 %float_0 %float_n1
    %float_2 = OpConstant %float 2
%_arr_uint_uint_1 = OpTypeArray %uint %uint_1
%OutputModes = OpTypeStruct %_arr_uint_uint_1
%_ptr_StorageBuffer_OutputModes = OpTypePointer StorageBuffer %OutputModes
      %modes = OpVariable %_ptr_StorageBuffer_OutputModes StorageBuffer
%_ptr_StorageBuffer_uint = OpTypePointer StorageBuffer %uint
       %main = OpFunction %void None %3
          %5 = OpLabel
     %origin = OpVariable %_ptr_Function_v3float Function
         %24 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_0
         %25 = OpLoad %uint %24
         %27 = OpAccessChain %_ptr_StorageBuffer_v4float %origins %int_0 %25
         %28 = OpLoad %v4float %27
         %29 = OpVectorShuffle %v3float %28 %28 0 1 2
               OpStore %origin %29
               OpStore %value %uint_4294967295
         %36 = OpLoad %33 %topLevelAS
         %38 = OpLoad %v3float %origin
               OpTraceRayKHR %36 %uint_0 %uint_255 %uint_0 %uint_0 %uint_0 %38 %float_0 %41 %float_2 %value
         %47 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_0
         %48 = OpLoad %uint %47
         %49 = OpLoad %uint %value
         %51 = OpAccessChain %_ptr_StorageBuffer_uint %modes %int_0 %48
               OpStore %51 %49
               OpReturn
               OpFunctionEnd
```

</details>## Runtime Execution and Result Checking

1. The host generates random micromap data using a per-case seed, sized to `triangleMicromapBytes * triangleCount` where `triangleCount` is 2 for non-zero-base cases and 1 otherwise.
2. The host builds the opacity micromap via `vkCmdBuildMicromapsEXT` with format `VK_OPACITY_MICROMAP_FORMAT_2_STATE_EXT` or `VK_OPACITY_MICROMAP_FORMAT_4_STATE_EXT` and the configured subdivision level. A memory barrier with `VK_PIPELINE_STAGE_2_MICROMAP_BUILD_BIT_EXT` to `VK_PIPELINE_STAGE_2_ACCELERATION_STRUCTURE_BUILD_BIT_KHR` separates the micromap build from the AS build.
3. The host builds the bottom-level AS with one triangle, attaching the micromap via `VkAccelerationStructureTrianglesOpacityMicromapEXT`. When `disable_opacity_micromap_instance` is in the flag mask, the BLAS is built with `VK_BUILD_ACCELERATION_STRUCTURE_ALLOW_DISABLE_OPACITY_MICROMAPS_EXT`.
4. The host builds the top-level AS with one instance carrying the instance flags derived from the test flag mask.
5. The host computes the expected output mode for each ray. The computation extracts the micromap data value (or uses the special index), converts to special index space, applies force-2-state collapse, determines culling, applies force-opaque or force-no-opaque, and maps the final state to 0, 1, or 2.
6. The host writes ray origins (subtriangle centroids computed by `calcSubtriangleCentroid`) to the origins SSBO and clears the modes SSBO to `0xFF`.
7. The host dispatches `vkCmdTraceRaysKHR` with `numRays = 4^subdivisionLevel` (or 1 for `special_index`).
8. A pipeline barrier transitions the output buffer from shader-write to host-read.
9. The host invalidates the mapped memory, reads the output buffer, and compares each entry against the expected mode. A mismatch logs the ray index, expected value, and found value, then fails the test.

## Failure Meaning

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

### Cause Analysis

#### `NoFlags` opacity state resolution failure

**Possible failure symptoms:** The output mode for one or more rays differs from the expected value. A ray that should have produced 2 (opaque, closest-hit) instead produces 1 (any-hit ran) or 0 (miss). A ray that should have produced 0 (transparent) instead produces 1 or 2. The mismatch pattern depends on the random micromap data and which subtriangles have which data values.

**Possible implementation causes:** The micromap build interpreted the data buffer with the wrong format or subdivision level, producing incorrect opacity states for some subtriangles. The traversal engine looked up the wrong subtriangle index for the ray hit, returning the opacity state of an adjacent subtriangle. The subtriangle centroid computation in the test host code and the traversal engine's subtriangle indexing disagree at higher subdivision levels. The bitwise NOT conversion between data values and special index space was applied incorrectly on the implementation side.

#### `force_opaque` forcing failure

**Possible failure symptoms:** A ray that should have produced 2 (opaque, closest-hit without any-hit) instead produces 1 (any-hit ran). This means the force-opaque flag did not suppress the any-hit shader. The failure appears only on subtriangles whose micromap data resolves to a non-opaque state, because opaque subtriangles already produce 2 without the flag.

**Possible implementation causes:** The driver did not propagate `VK_GEOMETRY_INSTANCE_FORCE_OPAQUE_BIT_KHR` or `gl_RayFlagsOpaqueEXT` into the traversal opacity resolution. The flag was applied after the any-hit shader dispatch decision instead of before. The force-opaque ray flag was ignored when the instance also had force-opaque set, due to a double-application bug.

#### `force_no_opaque` forcing failure

**Possible failure symptoms:** A ray that should have produced 1 (any-hit ran) instead produces 2 (closest-hit without any-hit). This means the force-no-opaque flag did not cause the any-hit shader to run on opaque subtriangles. The failure appears only on subtriangles whose micromap data resolves to opaque, because non-opaque subtriangles already run the any-hit shader.

**Possible implementation causes:** The driver did not propagate `VK_GEOMETRY_INSTANCE_FORCE_NO_OPAQUE_BIT_KHR` or `gl_RayFlagsNoOpaqueEXT` into the traversal opacity resolution. The flag was applied to the micromap state but the any-hit skip decision still used the original opaque state.

#### `cull_opaque` culling failure

**Possible failure symptoms:** A ray that should have produced 0 (miss, culled) instead produces 2 (closest-hit). This means the cull-opaque ray flag did not cull the ray when it hit opaque geometry. Conversely, a ray that should have produced 1 or 2 instead produces 0, meaning the flag culled a ray that hit non-opaque geometry.

**Possible implementation causes:** The traversal engine checked the cull-opaque flag against the raw micromap state instead of the state after force-opaque instance flag resolution. The cull check used the post-force-opaque-ray-flag state instead of the pre-force-opaque-ray-flag state, causing incorrect culling when both force-opaque instance and cull-opaque ray flag are set.

#### `cull_no_opaque` culling failure

**Possible failure symptoms:** A ray that should have produced 0 (miss, culled) instead produces 1 (any-hit). This means the cull-no-opaque ray flag did not cull the ray when it hit non-opaque geometry. Conversely, a ray that should have produced 2 instead produces 0, meaning the flag culled a ray that hit opaque geometry.

**Possible implementation causes:** The traversal engine checked the cull-no-opaque flag against the wrong state, not accounting for force-opaque instance flags that make the geometry opaque. The cull logic treated `FULLY_UNKNOWN_OPAQUE` as opaque when it should be treated as non-opaque for culling purposes.

#### `force_2_state` collapse failure

**Possible failure symptoms:** A 4-state case with `FULLY_UNKNOWN_TRANSPARENT` or `FULLY_UNKNOWN_OPAQUE` data produces the wrong output. `FULLY_UNKNOWN_TRANSPARENT` should collapse to `FULLY_TRANSPARENT` (output 0), but instead produces 1 (any-hit). `FULLY_UNKNOWN_OPAQUE` should collapse to `FULLY_OPAQUE` (output 2), but instead produces 1 (any-hit). The failure only appears with 4-state format because 2-state has no unknown values.

**Possible implementation causes:** The driver did not apply `VK_GEOMETRY_INSTANCE_FORCE_OPACITY_MICROMAP_2_STATE_EXT` or `gl_RayFlagsForceOpacityMicromap2StateEXT` during opacity resolution. The collapse was applied after culling or force-opaque instead of before, changing the intermediate state used by those later steps.

#### `disable_opacity_micromap` bypass failure

**Possible failure symptoms:** A ray that should have produced 1 (any-hit, because the geometry is non-opaque when the micromap is disabled) instead produces 0 or 2, meaning the micromap was not bypassed and its data was used. The failure pattern matches the `NoFlags` pattern because the micromap data is being applied when it should not be.

**Possible implementation causes:** The driver did not honor `VK_GEOMETRY_INSTANCE_DISABLE_OPACITY_MICROMAPS_EXT` during traversal. The BLAS was not built with `VK_BUILD_ACCELERATION_STRUCTURE_ALLOW_DISABLE_OPACITY_MICROMAPS_EXT`, so the disable flag had no effect. The disable flag was checked at the wrong stage of opacity resolution, after the micromap lookup had already determined the state.

## Case Pruning

### Requirement-based pruning

- All cases require `VK_KHR_acceleration_structure`, `VK_KHR_ray_tracing_pipeline`, and `VK_EXT_opacity_micromap` with the `micromap` feature enabled.
- `map_value` cases with 2-state format are pruned when the subdivision level exceeds `maxOpacity2StateSubdivisionLevel` reported by `VkPhysicalDeviceOpacityMicromapPropertiesEXT`.
- `map_value` cases with 4-state format are pruned when the subdivision level exceeds `maxOpacity4StateSubdivisionLevel`.
- `special_index` cases are not subject to subdivision level limits because they force subdivision level to 0.

### Design-based pruning

- Combinations with both `force_opaque_instance` and `force_no_opaque_instance` are pruned because the Vulkan spec forbids setting both instance opacity flags simultaneously.
- Combinations with more than one of `force_opaque_ray_flag`, `no_opaque_ray_flag`, `cull_opaque_ray_flag`, and `cull_no_opaque_ray_flag` are pruned because the spec allows at most one opacity ray flag per ray.
- The `_non_zero_base` variant is only registered for `NoFlags` because the base triangle offset is orthogonal to the flag combinations, and testing it once is sufficient.
- The `special_index` subgroup forces subdivision level to 0 and does not use 2-state or 4-state format subgroups, because the entire triangle uses one special index value.

## Key Takeaways

- The test verifies opacity micromap resolution by tracing one ray per subtriangle and recording which shader stage executed (miss, any-hit, or closest-hit) as the output mode. The host independently computes the expected mode and compares entry by entry.
- The 120 direct children test all valid combinations of nine flags across seven behavioral categories: baseline, force-opaque, force-no-opaque, cull-opaque, cull-no-opaque, force-2-state, and disable-micromap. Combinations verify that flag interactions follow the spec-defined precedence.
- The `map_value` subgroup tests per-subtriangle data across 2-state and 4-state formats and subdivision levels 0 through 15. The `special_index` subgroup tests the four special index values with subdivision level 0.
- The force-2-state collapse happens before force-opaque, force-no-opaque, and culling, so the order of operations matters for combined flag cases.
- The disable-micromap flag requires the BLAS to be built with `VK_BUILD_ACCELERATION_STRUCTURE_ALLOW_DISABLE_OPACITY_MICROMAPS_EXT`; without it, the flag has no effect.
- See `## Failure Meaning` for the distinction between the seven failure categories and their root causes.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `TestParams` struct and `TestFlagBits` enum | [vktRayTracingOpacityMicromapTests.cpp#L53-L81](../../../modules/vulkan/ray_tracing/vktRayTracingOpacityMicromapTests.cpp#L53-L81) | Defines the per-case parameters and the nine flag bits. |
| `checkSupport` | [vktRayTracingOpacityMicromapTests.cpp#L119-L156](../../../modules/vulkan/ray_tracing/vktRayTracingOpacityMicromapTests.cpp#L119-L156) | Feature requirements and subdivision level limit checks. |
| `initPrograms` rgen shader | [vktRayTracingOpacityMicromapTests.cpp#L163-L214](../../../modules/vulkan/ray_tracing/vktRayTracingOpacityMicromapTests.cpp#L163-L214) | Generates the raygen shader with flag-dependent `flagsString`. |
| `initPrograms` ah/ch/miss shaders | [vktRayTracingOpacityMicromapTests.cpp#L216-L257](../../../modules/vulkan/ray_tracing/vktRayTracingOpacityMicromapTests.cpp#L216-L257) | Generates the any-hit, closest-hit, and miss shaders. |
| `calcSubtriangleCentroid` | [vktRayTracingOpacityMicromapTests.cpp#L271-L323](../../../modules/vulkan/ray_tracing/vktRayTracingOpacityMicromapTests.cpp#L271-L323) | Computes the centroid of each subtriangle for ray origin placement. |
| Micromap build and AS setup | [vktRayTracingOpacityMicromapTests.cpp#L325-L541](../../../modules/vulkan/ray_tracing/vktRayTracingOpacityMicromapTests.cpp#L325-L541) | Builds the micromap, BLAS, and TLAS with micromap attachment. |
| Expected value computation | [vktRayTracingOpacityMicromapTests.cpp#L561-L651](../../../modules/vulkan/ray_tracing/vktRayTracingOpacityMicromapTests.cpp#L561-L651) | Host-side opacity resolution logic mirroring the spec. |
| Result verification | [vktRayTracingOpacityMicromapTests.cpp#L780-L812](../../../modules/vulkan/ray_tracing/vktRayTracingOpacityMicromapTests.cpp#L780-L812) | Reads output buffer and compares against expected modes. |
| `createOpacityMicromapTests` registration | [vktRayTracingOpacityMicromapTests.cpp#L818-L936](../../../modules/vulkan/ray_tracing/vktRayTracingOpacityMicromapTests.cpp#L818-L936) | Registers the 120 flag groups with `map_value` and `special_index` subgroups. |
