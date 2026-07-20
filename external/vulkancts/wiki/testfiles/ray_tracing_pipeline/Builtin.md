## Overview

**Core question:** Do `VK_KHR_ray_tracing_pipeline` shader built-ins report the spec-required values for the current invocation, ray, geometry, and stage, and do host-supplied specialization constants reach ray tracing shaders through `VkSpecializationInfo`?

This page covers two test families registered from [vktRayTracingBuiltinTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L4753-L4861):

- `builtin` exercises every ray tracing built-in variable across six shader stages, two geometry types, multiple launch sizes, and ray/pipeline culling flag combinations. It also includes an `indirect` subfamily that repeats selected built-in checks through `vkCmdTraceRaysIndirectKHR`.
- `spec_constants` fixes the built-in to `LaunchIDEXT` and varies only the shader stage, replacing the literal `256` in the launch-id shader with two specialization constants supplied by the host.

Both families share the same source file and the same `CaseDef` parameter struct. The `spec_constants` family reuses the launch-id shader generator with spec-constant substitution enabled, so a single shader walkthrough covers both code paths.

## Background Knowledge

- `VK_KHR_ray_tracing_pipeline` defines six shader stages: raygen, closest-hit, any-hit, miss, intersection, and callable. Each stage has read-only built-in inputs from `GL_EXT_ray_tracing`.
- The host launches a ray tracing dispatch with `vkCmdTraceRaysKHR` (direct) or `vkCmdTraceRaysIndirectKHR` (indirect) using a launch extent `(width, height, depth)`. The implementation must populate built-ins with the values the spec defines for the current invocation and ray.
- Some built-ins are stage-specific. `gl_HitKindEXT` and `gl_HitTEXT` are only meaningful in any-hit, closest-hit, and intersection shaders. `gl_PrimitiveID`, `gl_InstanceID`, `gl_InstanceCustomIndexEXT`, and `gl_GeometryIndexEXT` are meaningful only in hit-group stages. `gl_WorldRayOriginEXT`, `gl_WorldRayDirectionEXT`, `gl_RayTminEXT`, and `gl_RayTmaxEXT` are also valid in miss shaders.
- `VkSpecializationInfo` can be attached per shader module when adding it to the `RayTracingPipeline` builder. The implementation must replace default specialization constant values with host-supplied data entries at pipeline creation time. The host-side data block is byte-offset addressed through `VkSpecializationMapEntry` records.
- `vkCmdTraceRaysIndirectKHR` reads the launch extent from a `VkTraceRaysIndirectCommand` stored in a buffer instead of taking width, height, and depth as direct command arguments.

## Registration Hierarchy

```text
ray_tracing_pipeline.builtin
├── geometryindexext
├── hitkindext
├── hittext
├── incomingrayflagsext
├── indirect
├── instancecustomindexext
├── instanceid
├── launchidext
├── launchsizeext
├── objectraydirectionext
├── objectrayoriginext
├── objecttoworld3x4ext
├── objecttoworldext
├── primitiveid
├── raytmaxext
├── raytminext
├── worldraydirectionext
├── worldrayoriginext
├── worldtoobject3x4ext
└── worldtoobjectext
ray_tracing_pipeline.spec_constants
├── ahit
├── call
├── chit
├── miss
├── rgen
└── sect
```

The `builtin` family has 20 direct children: 19 built-in id subgroups plus the `indirect` subfamily. The `indirect` subfamily expands to five leaves (`hit_kind`, `incoming_flag`, `indices`, `t_min_max`, `transforms`) that repeat selected built-in checks through the indirect trace path. The `spec_constants` family has six direct children, one per ray tracing stage.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Built-in id | `launchidext`, `launchsizeext`, `primitiveid`, `instanceid`, `instancecustomindexext`, `geometryindexext`, `worldrayoriginext`, `worldraydirectionext`, `objectrayoriginext`, `objectraydirectionext`, `raytminext`, `raytmaxext`, `hittext`, `hitkindext`, `incomingrayflagsext`, `objecttoworldext`, `worldtoobjectext`, `objecttoworld3x4ext`, `worldtoobject3x4ext` | Selects which built-in variable the shader writes to the result image. Each id has its own expected-value generator on the host. | [vktRayTracingBuiltinTests.cpp#L65-L92](../../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L65-L92) |
| Shader stage | `rgen`, `ahit`, `chit`, `miss`, `sect`, `call` | Selects which ray tracing stage writes the built-in value. Some built-ins are only valid in hit-group stages. | [vktRayTracingBuiltinTests.cpp#L4174-L4182](../../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L4174-L4182) |
| Geometry type | `triangles`, `aabs` | Changes the bottom-level acceleration structure between triangle geometry and AABB procedural geometry. Affects hit kind and intersection behavior. | [vktRayTracingBuiltinTests.cpp#L110-L135](../../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L110-L135) |
| Launch size | `32x32`, `64x64`, `256x256` | Varies the dispatch dimensions to exercise different launch id ranges. | [vktRayTracingBuiltinTests.cpp#L4753-L4807](../../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L4753-L4807) |
| Ray skip flags | `raynoskipflags`, `rayskiptriangles`, `rayskipaabbs` | Per-ray flags passed to `traceRayEXT`. Affects which geometry the ray intersects. | [vktRayTracingBuiltinTests.cpp#L599-L1185](../../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L599-L1185) |
| Pipeline skip flags | `pipelinenoskipflags`, `pipelineskiptriangles`, `pipelineskipaabbs` | Pipeline create flags `VK_PIPELINE_CREATE_RAY_TRACING_SKIP_TRIANGLES_BIT_KHR` and `VK_PIPELINE_CREATE_RAY_TRACING_SKIP_AABBS_BIT_KHR`. Affects traversal at the pipeline level. | [vktRayTracingBuiltinTests.cpp#L599-L1185](../../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L599-L1185) |
| Geometry opacity | `opaque`, `noopaque` | Controls whether geometry is opaque. Affects any-hit shader execution and incoming ray flags. | [vktRayTracingBuiltinTests.cpp#L599-L1185](../../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L599-L1185) |
| Face orientation | `frontface`, `backface` | Controls face culling. Affects `gl_HitKindEXT` and `gl_IncomingRayFlagsEXT`. | [vktRayTracingBuiltinTests.cpp#L599-L1185](../../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L599-L1185) |
| Indirect subfamily | `indices`, `transforms`, `t_min_max`, `incoming_flag`, `hit_kind` | Selects which built-in group the indirect trace path verifies through a structured result buffer. | [vktRayTracingBuiltinTests.cpp#L2866-L3383](../../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L2866-L3383) |
| Specialization constants | enabled, disabled | When enabled, the launch-id shader uses `factor1` and `factor2` instead of literal `256`. Only used with `LaunchIDEXT`. | [vktRayTracingBuiltinTests.cpp#L386-L420](../../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L386-L420) |
| Maintenance5 path | yes, no | When yes, `incomingrayflagsext.misc.*` uses `VkPipelineCreateFlags2` through `VK_KHR_maintenance5` instead of `VkPipelineCreateFlags`. | [vktRayTracingBuiltinTests.cpp#L599-L1185](../../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L599-L1185) |

## Behavior Parameters

The primary behavioral axis is the test family. The two families change what is being tested: `builtin` checks built-in variable correctness, while `spec_constants` checks specialization constant substitution.

### builtin — Ray tracing shader built-in value correctness

Each case selects one built-in id, one shader stage, one geometry type, and launch dimensions. The shader writes the built-in value into a 3D `r32i` storage image at the position given by `gl_LaunchIDEXT`. The host computes an independent expected buffer and compares every image entry against it.

The `indirect` subfamily repeats selected built-in checks through `vkCmdTraceRaysIndirectKHR` with a different test instance (`RayTracingIndirectTestInstance`), a structured storage buffer instead of a 3D image, and shader-side `fuzzy_check` helpers for transform and t-min/max verification.

The `incomingrayflagsext` subgroup is the most parameter-heavy subfamily. It varies geometry type, per-ray skip flags, pipeline skip flags, geometry opacity, and face orientation. A `misc` subgroup uses `VK_KHR_maintenance5` to set skip flags through `VkPipelineCreateFlags2`.

### spec_constants — Specialization constant substitution in ray tracing shaders

The family fixes the built-in to `LaunchIDEXT` and the launch dimensions to `256x256x1`, then varies only the shader stage. The host supplies `factor1 = 256` and `factor2 = 256.0f` through a `VkSpecializationInfo` whose data block contains deliberate byte offsets and padding. The expected image value at `(x, y, z)` is `x + 256 * (y + 256 * z) + 1`, identical to the literal-256 form used by the matching `builtin.launchidext` cases.

The `SpecConstantsHelper` misaligns the two constant values inside the data block so the implementation must honor `VkSpecializationMapEntry` offset and size fields to locate each constant.

## Shader Analysis

The page uses one representative walkthrough because the `spec_constants.rgen` shader exercises both tested families in a single shader. The matching `builtin.launchidext.rgen` case uses the same shader with literal `256` instead of specialization constants; that difference is covered in the parameter variation note below.

### Representative Shader Walkthrough 1

**CTS case:** `ray_tracing_pipeline.spec_constants.rgen`

**Source location:** [vktRayTracingBuiltinTests.cpp#L410-L425](../../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L410-L425)

**What this shader tests:** The raygen shader reads `gl_LaunchIDEXT`, computes `r = x + factor1 * (y + int(factor2) * z) + 1`, and stores the result into a 3D `r32i` storage image. The host supplies `factor1 = 256` and `factor2 = 256.0f` through `VkSpecializationInfo`. If the implementation fails to substitute these constants, the shader uses the default values `1` and `2.0`, producing a different result image that the host validation catches.

**Shader-visible resources:**

- `%result` (`iimage3D`, set 0, binding 0, `r32i`): 3D storage image, one texel per launch invocation. Written by `OpImageWrite` with `SignExtend`.
- `%gl_LaunchIDEXT` (`vec3 uint`, `BuiltIn LaunchIdKHR`): input built-in giving the current invocation coordinates.
- `%factor1` (`SpecId 0`, `int`, default 1): specialization constant supplied by host as 256.
- `%factor2` (`SpecId 1`, `float`, default 2.0): specialization constant supplied by host as 256.0.

**Reconstructed GLSL:**

```glsl
#version 460 core
#extension GL_EXT_ray_tracing : require
/// Spec constants supplied by host: factor1=256, factor2=256.0 at runtime.
/// Default values (1, 2.0) are overridden by VkSpecializationInfo at pipeline creation.
layout (constant_id=0) const highp int factor1   = 1;
layout (constant_id=1) const highp float factor2 = 2.0;
/// 3D r32i storage image at binding 0; one texel per launch invocation.
layout(set = 0, binding = 0, r32i) uniform iimage3D result;

void main()
{
  /// p selects the result texel for this invocation.
  ivec3 p = ivec3(gl_LaunchIDEXT);
  /// v is the tested builtin (LaunchIDEXT here); encoding matches builtin.launchidext cases.
  ivec3 v = ivec3(gl_LaunchIDEXT);
  /// r = x + factor1 * (y + int(factor2) * z) + 1; with host values this is x + 256*(y + 256*z) + 1.
  int   r = v.x + factor1 * (v.y + int(factor2) * v.z) + 1;
  ivec4 c = ivec4(r,0,0,1);
  imageStore(result, p, c);
}
```

Built with `glslangValidator -V --target-env spirv1.4 -S rgen`. Validated with `spirv-val --target-env spv1.4`. SPIR-V version 1.4, Bound 52. **Target SPIR-V environment:** `spirv1.4` (CTS build options target `vk::SPIRV_VERSION_1_4`).

**Parameter variation note:** When `useSpecConstants` is false (the `builtin.launchidext` cases), the source generator replaces `factor1` with the literal `256` and `int(factor2)` with the literal `256`. The specialization constant declarations are omitted entirely. The computation and image store are otherwise identical. The six stage variants (`ahit`, `chit`, `miss`, `sect`, `call`) for `spec_constants` use the same `updateImage` logic but receive the built-in value through different stage-specific mechanisms (`rayPayloadInEXT`, `callableDataInEXT`, or intersection reporting).

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
               OpExtension "SPV_KHR_ray_tracing"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint RayGenerationKHR %main "main" %gl_LaunchIDEXT %result
               OpSource GLSL 460
               OpSourceExtension "GL_EXT_ray_tracing"
               OpName %main "main"
               OpName %p "p"
               OpName %gl_LaunchIDEXT "gl_LaunchIDEXT"
               OpName %v "v"
               OpName %r "r"
               OpName %factor1 "factor1"
               OpName %factor2 "factor2"
               OpName %c "c"
               OpName %result "result"
               OpDecorate %gl_LaunchIDEXT BuiltIn LaunchIdKHR
               OpDecorate %factor1 SpecId 0
               OpDecorate %factor2 SpecId 1
               OpDecorate %result Binding 0
               OpDecorate %result DescriptorSet 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
      %v3int = OpTypeVector %int 3
%_ptr_Function_v3int = OpTypePointer Function %v3int
       %uint = OpTypeInt 32 0
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_LaunchIDEXT = OpVariable %_ptr_Input_v3uint Input
%_ptr_Function_int = OpTypePointer Function %int
     %uint_0 = OpConstant %uint 0
    %factor1 = OpSpecConstant %int 1
     %uint_1 = OpConstant %uint 1
      %float = OpTypeFloat 32
    %factor2 = OpSpecConstant %float 2
     %uint_2 = OpConstant %uint 2
      %int_1 = OpConstant %int 1
      %v4int = OpTypeVector %int 4
%_ptr_Function_v4int = OpTypePointer Function %v4int
      %int_0 = OpConstant %int 0
         %46 = OpTypeImage %int 3D 0 0 0 2 R32i
%_ptr_UniformConstant_46 = OpTypePointer UniformConstant %46
     %result = OpVariable %_ptr_UniformConstant_46 UniformConstant
       %main = OpFunction %void None %3
          %5 = OpLabel
          %p = OpVariable %_ptr_Function_v3int Function
          %v = OpVariable %_ptr_Function_v3int Function
          %r = OpVariable %_ptr_Function_int Function
          %c = OpVariable %_ptr_Function_v4int Function
         %14 = OpLoad %v3uint %gl_LaunchIDEXT
         %15 = OpBitcast %v3int %14
               OpStore %p %15
         %17 = OpLoad %v3uint %gl_LaunchIDEXT
         %18 = OpBitcast %v3int %17
               OpStore %v %18
         %22 = OpAccessChain %_ptr_Function_int %v %uint_0
         %23 = OpLoad %int %22
         %26 = OpAccessChain %_ptr_Function_int %v %uint_1
         %27 = OpLoad %int %26
         %30 = OpConvertFToS %int %factor2
         %32 = OpAccessChain %_ptr_Function_int %v %uint_2
         %33 = OpLoad %int %32
         %34 = OpIMul %int %30 %33
         %35 = OpIAdd %int %27 %34
         %36 = OpIMul %int %factor1 %35
         %37 = OpIAdd %int %23 %36
         %39 = OpIAdd %int %37 %int_1
               OpStore %r %39
         %43 = OpLoad %int %r
         %45 = OpCompositeConstruct %v4int %43 %int_0 %int_0 %int_1
               OpStore %c %45
         %49 = OpLoad %46 %result
         %50 = OpLoad %v3int %p
         %51 = OpLoad %v4int %c
               OpImageWrite %49 %50 %51 SignExtend
               OpReturn
               OpFunctionEnd
```

</details>## Runtime Execution and Result Checking

Direct cases (`builtin.*` except `indirect`):

1. The host builds bottom-level and top-level acceleration structures sized from `squaresGroupCount`, `geometriesGroupCount`, and `instancesGroupCount`.
2. The host allocates a 3D `r32i` storage image and clears it to `DEFAULT_UINT_CLEAR_VALUE`.
3. The host compiles ray tracing shaders, attaching `VkSpecializationInfo` when `useSpecConstants` is true.
4. The host builds the `RayTracingPipeline` with raygen, miss, hit group, and optional intersection or callable shaders, then builds shader binding table regions for each group.
5. The host dispatches `vkCmdTraceRaysKHR` with `(width, height, raysDepth)`.
6. The raygen shader invokes `traceRayEXT`. The selected stage writes the built-in value into the result image at `gl_LaunchIDEXT`.
7. A pipeline barrier transitions the image from shader-write to transfer-read.
8. The host copies the image to a host-visible buffer with `vkCmdCopyImageToBuffer` and invalidates mapped memory.
9. The host scans every entry against an independently computed expected buffer. Float built-ins use fixed-point encoding through `FIXED_POINT_DIVISOR` (1024 * 1024) with `FIXED_POINT_ALLOWED_ERROR` (4).

Indirect cases (`builtin.indirect.*`):

1. The host builds bottom-level and top-level acceleration structures with fixed geometry and instance offsets.
2. The host allocates a structured storage buffer instead of a 3D image.
3. The host builds an indirect command buffer holding a `VkTraceRaysIndirectCommand` with the launch dimensions.
4. The host dispatches `vkCmdTraceRaysIndirectKHR`.
5. Hit-group shaders write `gl_PrimitiveID`, `gl_InstanceID`, `gl_InstanceCustomIndexEXT`, ray transform matrices, `gl_RayTminEXT`, `gl_RayTmaxEXT`, `gl_IncomingRayFlagsEXT`, or `gl_HitKindEXT` into the structured buffer.
6. The host validates per-stage result counters. For `indices`, every ray must report the expected primitive, instance, and custom index. For `transforms`, `t_min_max`, `incoming_flag`, and `hit_kind`, per-stage counters must fall inside host-computed ranges or equal expected values.

Specialization constant setup (`spec_constants.*`):

The `SpecConstantsHelper` builds a `VkSpecializationInfo` whose data block places `factor1` and `factor2` at byte offsets with padding between them. Two `VkSpecializationMapEntry` records tell the implementation where each constant lives in the data block. If the implementation ignores the map entry offsets or sizes and reads the constants at wrong positions, the substituted values differ from 256, and the result image fails validation.

The `spec_constants` family forces `id == TEST_ID_LAUNCH_ID_EXT` and asserts that specialization constants are only used with that id. The host supplies `factor1 = 256` and `factor2 = 256.0f`, making the expected value `x + 256 * (y + 256 * z) + 1` at every launch id.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `builtin` | A ray tracing shader built-in returned a value other than what the spec requires for the current invocation, ray, geometry, or stage. Includes the `indirect` subfamily where the failure also implicates the indirect trace path or the structured result buffer verification. |
| `spec_constants` | The implementation did not substitute the host-supplied specialization constant values into the launch-id shader for the selected ray tracing stage, or the specialization data byte-offset layout was not honored. |

### Cause Analysis

#### `builtin` built-in value mismatch

**Possible failure symptoms:** One or more result image entries differ from the host-computed expected buffer. For direct cases, the mismatch appears in the 3D `r32i` image at specific `(x, y, z)` positions. For indirect cases, per-stage counters in the structured buffer fall outside expected ranges. The mismatch pattern depends on which built-in failed: scalar built-ins like `PrimitiveID` fail at specific launch positions tied to geometry layout, while vector or matrix built-ins fail across multiple image slices.

**Possible implementation causes:** The shader compiler generated incorrect code for reading a built-in variable. The driver populated the built-in with a wrong value for the current invocation, ray, geometry, or stage. The acceleration structure builder produced geometry or instance data that does not match what the test expects. For stage-specific built-ins, the driver allowed the variable in a stage where the spec does not define it, or returned garbage. For `HitTEXT` and `RayTmaxEXT`, the reported hit distance differs from the spec-required value because the closest-hit, any-hit, or intersection stage received a different `t` value than expected. For `IncomingRayFlagsEXT`, the driver did not set the ray flags that the test passed to `traceRayEXT`, or the pipeline skip flags did not propagate into the incoming flags. For the `indirect` subfamily, the indirect trace path supplied wrong launch dimensions or the structured buffer layout did not match the shader writes.

#### `spec_constants` substitution failure

**Possible failure symptoms:** The result image entries differ from the expected `x + 256 * (y + 256 * z) + 1` pattern. If the implementation used the default constant values (1 and 2.0) instead of the host-supplied values (256 and 256.0), the result would be `x + 1 * (y + 2 * z) + 1`, a much smaller value. If the implementation honored the constants but misread the byte offsets, the result would use corrupted or partially correct values.

**Possible implementation causes:** The pipeline creation code ignored the `VkSpecializationInfo` attached to the shader module and kept the default constant values. The implementation read the specialization data block at wrong byte offsets because it did not honor the `VkSpecializationMapEntry` offset and size fields, or it assumed contiguous layout without padding. The shader compiler folded the default constant values into the shader before specialization substitution had a chance to replace them.

## Case Pruning

### Requirement-based pruning

- The `misc` subgroup of `incomingrayflagsext` requires `VK_KHR_maintenance5` for the `VkPipelineCreateFlags2` path. Cases in this subgroup are only registered when the device supports that extension.
- Ray tracing pipeline cases require `VK_KHR_ray_tracing_pipeline` and `VK_KHR_acceleration_structure` feature support.
- Indirect trace cases require the indirect trace command feature.

### Design-based pruning

- Culling-flag combinations that skip both triangles and AABBs are pruned because the Vulkan spec forbids setting both `VK_PIPELINE_CREATE_RAY_TRACING_SKIP_TRIANGLES_BIT_KHR` and `VK_PIPELINE_CREATE_RAY_TRACING_SKIP_AABBS_BIT_KHR` simultaneously.
- `SkipTrianglesKHR` is mutually exclusive with `CullBackFacingTrianglesKHR` and `CullFrontFacingTrianglesKHR`. Triangle ray-flag-skip cases without a matching pipeline skip flag are pruned.
- The `spec_constants` family only covers `LaunchIDEXT`. The source generator supports spec constants for `LaunchSizeEXT` as well, but the registered family does not exercise that combination.
- The `spec_constants` family fixes launch dimensions to `256x256x1` and varies only the stage, avoiding redundant matrix expansion across launch sizes and geometry types.

## Key Takeaways

- The `builtin` family verifies that every ray tracing built-in reports the spec-required value for the current invocation, ray, geometry, and stage. The host computes expected values independently and compares against the 3D image (direct) or structured buffer (indirect).
- The `spec_constants` family verifies that `VkSpecializationInfo` substitutes host-supplied values into ray tracing shaders. It reuses the launch-id shader with `factor1` and `factor2` replacing literal `256`, so the same expected-value formula applies.
- The `indirect` subfamily is part of `builtin`, not a separate family. It repeats selected built-in checks through `vkCmdTraceRaysIndirectKHR` with structured buffer verification.
- Float built-ins (`HitTEXT`, `RayTminEXT`, `RayTmaxEXT`, ray origin/direction, transforms) use fixed-point encoding with `FIXED_POINT_DIVISOR = 1024 * 1024` and `FIXED_POINT_ALLOWED_ERROR = 4` during host comparison.
- The `SpecConstantsHelper` misaligns constant values in the data block to force `VkSpecializationMapEntry` offset handling.
- See `## Failure Meaning` for the distinction between built-in value mismatch and specialization constant substitution failure.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `CaseDef` and `TestId` enum | [vktRayTracingBuiltinTests.cpp#L59-L135](../../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L59-L135) | Defines the per-case parameter struct and the built-in id enumeration. |
| `RayTracingTestCase::initPrograms` for launch-id and launch-size | [vktRayTracingBuiltinTests.cpp#L386-L598](../../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L386-L598) | Generates the rgen, ahit, chit, miss, sect, and call shaders for launch-id and launch-size, with spec-constant variants. |
| `initPrograms` for scalar, vector, matrix, and flags built-ins | [vktRayTracingBuiltinTests.cpp#L599-L1185](../../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L599-L1185) | Generates shaders for primitive, instance, geometry indices, ray params, transforms, and incoming-ray-flags. |
| Passthrough shaders | [vktRayTracingBuiltinTests.cpp#L345-L384](../../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L345-L384) | Provides hit, miss, and intersection passthrough shaders for stages not under test. |
| `SpecConstantsHelper` | [vktRayTracingBuiltinTests.cpp#L1735-L1775](../../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L1735-L1775) | Builds the misaligned specialization info block. |
| `runTest` direct case execution | [vktRayTracingBuiltinTests.cpp#L1777-L1931](../../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L1777-L1931) | Builds pipeline and SBT, dispatches `vkCmdTraceRaysKHR`, copies image to host buffer. |
| Expected-value generators | [vktRayTracingBuiltinTests.cpp#L1985-L2366](../../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L1985-L2366) | Computes per-built-in expected int, float, vector, and matrix buffers used by host validation. |
| Validation routines | [vktRayTracingBuiltinTests.cpp#L2368-L2608](../../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L2368-L2608) | Per-pixel comparison against expected buffer with fixed-point tolerance for float built-ins. |
| `RayTracingIndirectTestCase::initPrograms` | [vktRayTracingBuiltinTests.cpp#L2866-L3383](../../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L2866-L3383) | Generates the indirect-trace shaders for indices, transforms, t_min_max, incoming_flag, and hit_kind. |
| `RayTracingIndirectTestInstance::verifyResults` | [vktRayTracingBuiltinTests.cpp#L3946-L4060](../../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L3946-L4060) | Per-id structured-buffer verification for the indirect subfamily. |
| `RayTracingIndirectTestInstance::iterate` | [vktRayTracingBuiltinTests.cpp#L4062-L4172](../../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L4062-L4172) | Builds indirect command buffer, dispatches `vkCmdTraceRaysIndirectKHR`, validates. |
| Stages array | [vktRayTracingBuiltinTests.cpp#L4174-L4182](../../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L4174-L4182) | Names the six stage leaves: rgen, ahit, chit, sect, miss, call. |
| `createBuiltinTests` registration | [vktRayTracingBuiltinTests.cpp#L4753-L4807](../../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L4753-L4807) | Registers the `builtin` family with 19 built-in subgroups plus `indirect`. |
| `createSpecConstantTests` registration | [vktRayTracingBuiltinTests.cpp#L4809-L4861](../../../modules/vulkan/ray_tracing/vktRayTracingBuiltinTests.cpp#L4809-L4861) | Registers the `spec_constants` family with one leaf per stage. |
| Category dispatcher | [vktRayTracingTests.cpp#L65-L104](../../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L65-L104) | Routes `builtin` and `spec_constants` to `createBuiltinTests` and `createSpecConstantTests`. |
| Common raygen shader | [vkRayTracingUtil.cpp#L118](../../../framework/vulkan/vkRayTracingUtil.cpp#L118) | Returns the standard raygen shader with `traceRayEXT` used by non-raygen-stage cases. |
