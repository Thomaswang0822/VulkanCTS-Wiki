## Overview

**Core question:** Does each descriptor-update method expose the intended top-level acceleration structure to ray-query and ray-tracing shaders in every registered stage?

- [`vktBindingDescriptorUpdateASTests.cpp`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp) implements the `acceleration_structure` branch of the `binding_model.descriptor_update` test family.
- The branch contains the `ray_query` and `ray_tracing` intermediate nodes. Both combine four descriptor-update methods with stage-specific pipelines and compare shader-observed hit distances with an analytical plane-intersection result.
- The default mustpass list contains 60 leaves: 48 for `ray_query` and 12 for `ray_tracing` ([mustpass inventory](../../../mustpass/main/vk-default/binding-model.txt#L10898-L10957)).

## Background Knowledge

For the shared concepts of descriptor writes and active state, see [Background Knowledge](../../categories/binding_model.md#background-knowledge) of the `binding_model` page.

- **Acceleration-structure descriptors.** A `VK_DESCRIPTOR_TYPE_ACCELERATION_STRUCTURE_KHR` descriptor can reference a top-level acceleration structure (TLAS), which is the starting point for traversal. Its instances refer to bottom-level acceleration structures containing geometry ([top-level acceleration structures](../../../../vulkan-docs/src/chapters/accelstructures.adoc#L127-L137)).
- **Ray query and pipeline ray tracing.** Ray query advances traversal inside the invoking shader and may run in any shader stage with `rayQuery` enabled. `traceRayEXT` transfers execution through shader groups in a ray-tracing pipeline with `rayTracingPipeline` enabled ([ray traversal entry points](../../../../vulkan-docs/src/chapters/raytraversal.adoc#L4-L24)).
- **Acceleration-structure descriptor writes.** A regular write supplies the handle through `VkWriteDescriptorSetAccelerationStructureKHR` in `VkWriteDescriptorSet::pNext` ([write structure rule](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3094-L3100), [source-data rule](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3161-L3167)). Update templates describe how to read equivalent descriptor data from host memory; push forms record the descriptor in command-buffer state ([update templates](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L4104-L4133), [template types](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L4179-L4209)).

## Registration Hierarchy

```text
binding_model.descriptor_update.acceleration_structure
├── ray_query
└── ray_tracing
```

The parent `descriptor_update` factory excludes this branch from Vulkan SC builds ([parent registration](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L1907-L1918)). The branch factory creates the two direct child intermediate nodes, then places update-method intermediate nodes and executable stage leaves below them ([branch registration](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L2566-L2662)).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Traversal mechanism | `ray_query`, `ray_tracing` | Selects direct query traversal or shader-group pipeline tracing. This is the primary behavioral axis. | [`TestType` and registration](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L60-L74), [`testTypes`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L2570-L2577) |
| Update method | `regular`, `with_template`, `with_push`, `with_push_template` | Supplies the same TLAS through a descriptor-set write, descriptor update template, push descriptor, or push-descriptor template. | [`UpdateMethod`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L66-L74), [`updateMethods`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L2578-L2591) |
| `ray_query` stage | `vert`, `tesc`, `tese`, `geom`, `frag`, `comp`, `rgen`, `ahit`, `chit`, `miss`, `sect`, `call` | Moves the same query body across graphics, compute, and ray-tracing stages. | [`pipelineStages`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L2592-L2610), [instance routing](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L2431-L2461) |
| `ray_tracing` stage | `rgen`, `chit`, `miss` | Selects the ray-pipeline stage that reads the descriptor under test. Hit and miss cases launch a second ray. | [stage pruning](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L2626-L2637), [ray-tracing programs](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L1958-L2097) |
| Execution extent | `16 x 16 x 1` | Produces one signed fixed-point hit-distance value for each of 256 positions. | [`TEST_WIDTH` / `TEST_HEIGHT`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L76-L80), [`TestParams`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L2639-L2650) |
| Result format | `VK_FORMAT_R32_SINT` | Stores the hit distance multiplied by `1048576` for exact host comparison. | [test parameters](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L2639-L2650), [verification](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L642-L723) |

Four update methods times 12 stages produce the 48 `ray_query` leaves. Four methods times three stages produce the 12 `ray_tracing` leaves. The default mustpass interval contains all 60 exact paths ([mustpass coverage](../../../mustpass/main/vk-default/binding-model.txt#L10898-L10957)).

## Behavior Parameters

The primary behavioral axis is the traversal mechanism selected by the `ray_query` or `ray_tracing` intermediate node. Update method and stage change how the descriptor reaches that mechanism and where it is consumed, but the two mechanism values change the shader operation and pipeline structure used to prove the descriptor contents.

### `ray_query`: Direct traversal in the selected shader stage

The selected stage declares set 0, binding 0 as `accelerationStructureEXT tlas`. It initializes a `rayQueryEXT`, advances traversal, reads the candidate triangle's `t`, and writes a fixed-point value to the result image. Graphics and compute cases invoke that code through their normal pipelines. Ray-stage cases use a service TLAS and shader binding tables to reach the selected stage, which then performs the same query through the descriptor under test ([query body](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L2283-L2315), [pipeline selection](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L2431-L2461)).

### `ray_tracing`: Pipeline trace through the descriptor under test

The selected `rgen`, `chit`, or `miss` stage invokes `traceRayEXT` with the TLAS at set 0, binding 0. A fixed closest-hit shader records the resulting `gl_HitTEXT`. The `chit` and `miss` variants first use a service TLAS to reach the selected stage, then launch the descriptor-under-test ray, so their pipeline recursion depth is two ([program construction](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L1958-L2097), [pipeline and recursion setup](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L2115-L2219)).

## Shader Analysis

The page uses two walkthroughs because `ray_query` performs inline traversal with `rayQueryProceedEXT`, while `ray_tracing` transfers execution through `traceRayEXT` and shader groups. The summaries after each representative shader cover the update-method and stage differences.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.binding_model.descriptor_update.acceleration_structure.ray_query.regular.comp
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `ray_query` | Uses an inline `rayQueryEXT` to traverse the updated TLAS. |
| `regular` | Writes set 0 with `vkUpdateDescriptorSets` before command recording. |
| `comp` | Provides the smallest complete invocation path: one compute invocation per result texel. |

#### Purpose

This shader proves that a regular acceleration-structure descriptor update supplies the TLAS used by compute-stage ray-query traversal. Its result encodes the triangle candidate distance for exact host comparison.

#### Structural Design

```mermaid
flowchart LR
    A[Set 0 TLAS descriptor] --> B[rayQueryInitializeEXT]
    B --> C[rayQueryProceedEXT loop]
    C --> D[Read candidate triangle t]
    D --> E[Convert t to fixed point]
    E --> F[Store R32_SINT result texel]
```

#### Shader Code

```glsl
#version 460
#extension GL_EXT_ray_query : require

/// Set 0 binding 0 is the acceleration-structure descriptor updated by the selected host update method.
layout(set = 0, binding = 0) uniform accelerationStructureEXT tlas;
/// Set 1 binding 0 is a 16 x 16 x 1 r32i storage image. Each invocation writes one fixed-point hit distance.
layout(set = 1, binding = 0, r32i) uniform iimage3D result;

void main()
{
  /// The host dispatches 16 x 16 x 1 workgroups; the default local size is one invocation per workgroup.
  ivec3       pos      = ivec3(gl_WorkGroupID);
  ivec3       size     = ivec3(gl_NumWorkGroups);
  const float mult     = 1048576.0f;
  uint        rayFlags = 0;
  uint        cullMask = 0xFF;
  float       tmin     = 0.0;
  float       tmax     = 9.0;
  vec3        origin   = vec3((float(pos.x) + 0.5f) / float(size.x), (float(pos.y) + 0.5f) / float(size.y), 0.0);
  vec3        direct   = vec3(0.0, 0.0, 1.0);
  int         value    = 0;
  rayQueryEXT rayQuery;

  /// Traversal starts from the descriptor under test and records the candidate triangle distance.
  rayQueryInitializeEXT(rayQuery, tlas, rayFlags, cullMask, origin, tmin, direct, tmax);

  while(rayQueryProceedEXT(rayQuery))
  {
    if (rayQueryGetIntersectionTypeEXT(rayQuery, false) == gl_RayQueryCandidateIntersectionTriangleEXT)
    {
      const float t = rayQueryGetIntersectionTEXT(rayQuery, false);
      value = int(round(mult * t));
    }
  }

  /// Host verification compares this integer against the analytically expected plane-intersection distance.
  imageStore(result, pos, ivec4(value, 0, 0, 0));
}
```

#### Additional Info

- `BindingAcceleratioStructureComputeTestInstance::initPrograms()` supplies this exact declaration and body structure with `SPIRV_VERSION_1_4`; the added `///` comments do not alter the compiled shader ([compute generator](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L1316-L1348)).
- The host dispatches `16 x 16 x 1` workgroups. The generated shader declares no explicit local size, so each workgroup contains one invocation ([dispatch](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L1361-L1368)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Update method | No shader change. Host code chooses descriptor-set update, template update, push update, or push-template update. | [shared update path](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L441-L575) |
| Graphics stage | The same query body uses stage-specific coordinates and helper stages to draw a `16 x 16` result. | [graphics shader generation](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L824-L1105) |
| Ray-tracing stage | The same query body uses `gl_LaunchIDEXT`; service shaders and a service TLAS invoke the selected ray stage. | [ray-stage generation](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L1473-L1683) |
| Traversal mechanism | `ray_tracing` replaces `rayQueryEXT` with `traceRayEXT` and uses shader groups, so it has a separate walkthrough. | [shader bodies](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L2283-L2328) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `comp`
- Target SPIRV version: `spirv1.4`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.4
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 99
; Schema: 0
               OpCapability Shader
               OpCapability RayQueryKHR
               OpExtension "SPV_KHR_ray_query"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_WorkGroupID %gl_NumWorkGroups %rayQuery %tlas %result
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 460
               OpSourceExtension "GL_EXT_ray_query"
               OpName %main "main"
               OpName %pos "pos"
               OpName %gl_WorkGroupID "gl_WorkGroupID"
               OpName %size "size"
               OpName %gl_NumWorkGroups "gl_NumWorkGroups"
               OpName %rayFlags "rayFlags"
               OpName %cullMask "cullMask"
               OpName %tmin "tmin"
               OpName %tmax "tmax"
               OpName %origin "origin"
               OpName %direct "direct"
               OpName %value "value"
               OpName %rayQuery "rayQuery"
               OpName %tlas "tlas"
               OpName %t "t"
               OpName %result "result"
               OpDecorate %gl_WorkGroupID BuiltIn WorkgroupId
               OpDecorate %gl_NumWorkGroups BuiltIn NumWorkgroups
               OpDecorate %tlas Binding 0
               OpDecorate %tlas DescriptorSet 0
               OpDecorate %result Binding 0
               OpDecorate %result DescriptorSet 1
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
      %v3int = OpTypeVector %int 3
%_ptr_Function_v3int = OpTypePointer Function %v3int
       %uint = OpTypeInt 32 0
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_WorkGroupID = OpVariable %_ptr_Input_v3uint Input
%gl_NumWorkGroups = OpVariable %_ptr_Input_v3uint Input
%_ptr_Function_uint = OpTypePointer Function %uint
     %uint_0 = OpConstant %uint 0
   %uint_255 = OpConstant %uint 255
      %float = OpTypeFloat 32
%_ptr_Function_float = OpTypePointer Function %float
    %float_0 = OpConstant %float 0
    %float_9 = OpConstant %float 9
    %v3float = OpTypeVector %float 3
%_ptr_Function_v3float = OpTypePointer Function %v3float
%_ptr_Function_int = OpTypePointer Function %int
  %float_0_5 = OpConstant %float 0.5
     %uint_1 = OpConstant %uint 1
    %float_1 = OpConstant %float 1
         %56 = OpConstantComposite %v3float %float_0 %float_0 %float_1
      %int_0 = OpConstant %int 0
         %59 = OpTypeRayQueryKHR
%_ptr_Private_59 = OpTypePointer Private %59
   %rayQuery = OpVariable %_ptr_Private_59 Private
         %62 = OpTypeAccelerationStructureKHR
%_ptr_UniformConstant_62 = OpTypePointer UniformConstant %62
       %tlas = OpVariable %_ptr_UniformConstant_62 UniformConstant
       %bool = OpTypeBool
      %false = OpConstantFalse %bool
%float_1048576 = OpConstant %float 1048576
         %91 = OpTypeImage %int 3D 0 0 0 2 R32i
%_ptr_UniformConstant_91 = OpTypePointer UniformConstant %91
     %result = OpVariable %_ptr_UniformConstant_91 UniformConstant
      %v4int = OpTypeVector %int 4
       %main = OpFunction %void None %3
          %5 = OpLabel
        %pos = OpVariable %_ptr_Function_v3int Function
       %size = OpVariable %_ptr_Function_v3int Function
   %rayFlags = OpVariable %_ptr_Function_uint Function
   %cullMask = OpVariable %_ptr_Function_uint Function
       %tmin = OpVariable %_ptr_Function_float Function
       %tmax = OpVariable %_ptr_Function_float Function
     %origin = OpVariable %_ptr_Function_v3float Function
     %direct = OpVariable %_ptr_Function_v3float Function
      %value = OpVariable %_ptr_Function_int Function
          %t = OpVariable %_ptr_Function_float Function
         %14 = OpLoad %v3uint %gl_WorkGroupID
         %15 = OpBitcast %v3int %14
               OpStore %pos %15
         %18 = OpLoad %v3uint %gl_NumWorkGroups
         %19 = OpBitcast %v3int %18
               OpStore %size %19
               OpStore %rayFlags %uint_0
               OpStore %cullMask %uint_255
               OpStore %tmin %float_0
               OpStore %tmax %float_9
         %35 = OpAccessChain %_ptr_Function_int %pos %uint_0
         %36 = OpLoad %int %35
         %37 = OpConvertSToF %float %36
         %39 = OpFAdd %float %37 %float_0_5
         %40 = OpAccessChain %_ptr_Function_int %size %uint_0
         %41 = OpLoad %int %40
         %42 = OpConvertSToF %float %41
         %43 = OpFDiv %float %39 %42
         %45 = OpAccessChain %_ptr_Function_int %pos %uint_1
         %46 = OpLoad %int %45
         %47 = OpConvertSToF %float %46
         %48 = OpFAdd %float %47 %float_0_5
         %49 = OpAccessChain %_ptr_Function_int %size %uint_1
         %50 = OpLoad %int %49
         %51 = OpConvertSToF %float %50
         %52 = OpFDiv %float %48 %51
         %53 = OpCompositeConstruct %v3float %43 %52 %float_0
               OpStore %origin %53
               OpStore %direct %56
               OpStore %value %int_0
         %65 = OpLoad %62 %tlas
         %66 = OpLoad %uint %rayFlags
         %67 = OpLoad %uint %cullMask
         %68 = OpLoad %v3float %origin
         %69 = OpLoad %float %tmin
         %70 = OpLoad %v3float %direct
         %71 = OpLoad %float %tmax
               OpRayQueryInitializeKHR %rayQuery %65 %66 %67 %68 %69 %70 %71
               OpBranch %72
         %72 = OpLabel
               OpLoopMerge %74 %75 None
               OpBranch %76
         %76 = OpLabel
         %78 = OpRayQueryProceedKHR %bool %rayQuery
               OpBranchConditional %78 %73 %74
         %73 = OpLabel
         %80 = OpRayQueryGetIntersectionTypeKHR %uint %rayQuery %int_0
         %81 = OpIEqual %bool %80 %uint_0
               OpSelectionMerge %83 None
               OpBranchConditional %81 %82 %83
         %82 = OpLabel
         %85 = OpRayQueryGetIntersectionTKHR %float %rayQuery %int_0
               OpStore %t %85
         %87 = OpLoad %float %t
         %88 = OpFMul %float %float_1048576 %87
         %89 = OpExtInst %float %1 Round %88
         %90 = OpConvertFToS %int %89
               OpStore %value %90
               OpBranch %83
         %83 = OpLabel
               OpBranch %75
         %75 = OpLabel
               OpBranch %72
         %74 = OpLabel
         %94 = OpLoad %91 %result
         %95 = OpLoad %v3int %pos
         %96 = OpLoad %int %value
         %98 = OpCompositeConstruct %v4int %96 %int_0 %int_0 %int_0
               OpImageWrite %94 %95 %98 SignExtend
               OpReturn
               OpFunctionEnd
```

</details>

### Representative Shader Walkthrough 2

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.binding_model.descriptor_update.acceleration_structure.ray_tracing.with_template.chit
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `ray_tracing` | Uses pipeline tracing and shader-group routing instead of inline ray query. |
| `with_template` | Updates the allocated descriptor set through one acceleration-structure template entry. |
| `chit` | A service ray invokes the selected closest-hit shader, which launches the descriptor-under-test ray. |

#### Purpose

This closest-hit shader proves that a template-updated acceleration-structure descriptor is visible to pipeline ray tracing. It launches a second ray through set 0; a fixed closest-hit shader stores that ray's hit distance.

#### Structural Design

```mermaid
flowchart LR
    A[Service TLAS ray] --> B[Selected closest-hit shader]
    B --> C[traceRayEXT through set 0 TLAS]
    C --> D[Secondary hit group]
    D --> E[Fixed closest-hit shader stores gl_HitTEXT]
    E --> F[R32_SINT result texel]
```

#### Shader Code

```glsl
#version 460
#extension GL_EXT_ray_tracing : require

/// The selected closest-hit stage is the shader whose descriptor access is under test.
layout(location = 0) rayPayloadInEXT vec3 hitValue;
hitAttributeEXT vec3 attribs;
/// Set 0 binding 0 is updated with the top-level acceleration structure by the selected host update method.
layout(set = 0, binding = 0) uniform accelerationStructureEXT topLevelAS;
/// Set 1 binding 0 is the common r32i output image. The fixed secondary closest-hit stage writes it.
layout(set = 1, binding = 0, r32i) uniform iimage3D result;

void main()
{
  ivec3       pos      = ivec3(gl_LaunchIDEXT);
  ivec3       size     = ivec3(gl_LaunchSizeEXT);
  uint        rayFlags = 0;
  uint        cullMask = 0xFF;
  float       tmin     = 0.0;
  float       tmax     = 9.0;
  vec3        origin   = vec3((float(gl_LaunchIDEXT.x) + 0.5f) / float(gl_LaunchSizeEXT.x), (float(gl_LaunchIDEXT.y) + 0.5f) / float(gl_LaunchSizeEXT.y), 0.0);
  vec3        direct   = vec3(0.0, 0.0, 1.0);

  /// Record offset 1 selects the fixed closest-hit group, which writes the observed hit distance.
  traceRayEXT(topLevelAS, rayFlags, cullMask, 1, 0, 1, origin, tmin, direct, tmax, 0);
}
```

#### Additional Info

- The fixed ray-generation shader traces the service TLAS in the -Z direction to invoke this selected closest-hit stage. The selected stage then traces the descriptor under test in the +Z direction ([selected-stage construction](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L1987-L2065)).
- The fixed `chit0` shader stays unchanged across `rgen`, `chit`, and `miss`; it contains the result-store body. Shader binding table record offset 1 routes the second ray to that group ([fixed output shader and group setup](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L1966-L2011), [SBT construction](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L2099-L2219)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Update method | No shader change. `with_template` reads one TLAS handle from template data; the other methods use their corresponding host or command-buffer update path. | [template construction and update](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L451-L486) |
| `rgen` | The selected ray-generation shader traces the descriptor under test without an outer service-ray hit. | [ray-generation branch](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L2013-L2038) |
| `miss` | A service ray invokes the selected miss shader, which launches the same second ray as this closest-hit case. | [miss branch](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L2068-L2092) |
| `chit` | Uses the two-level trace shown above and requires recursion depth two. | [recursion setup](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L2182-L2186) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `rchit`
- Target SPIRV version: `spirv1.4`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.4
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 75
; Schema: 0
               OpCapability RayTracingKHR
               OpExtension "SPV_KHR_ray_tracing"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint ClosestHitKHR %main "main" %gl_LaunchIDEXT %gl_LaunchSizeEXT %topLevelAS %hitValue %attribs %result
               OpSource GLSL 460
               OpSourceExtension "GL_EXT_ray_tracing"
               OpName %main "main"
               OpName %pos "pos"
               OpName %gl_LaunchIDEXT "gl_LaunchIDEXT"
               OpName %size "size"
               OpName %gl_LaunchSizeEXT "gl_LaunchSizeEXT"
               OpName %rayFlags "rayFlags"
               OpName %cullMask "cullMask"
               OpName %tmin "tmin"
               OpName %tmax "tmax"
               OpName %origin "origin"
               OpName %direct "direct"
               OpName %topLevelAS "topLevelAS"
               OpName %hitValue "hitValue"
               OpName %attribs "attribs"
               OpName %result "result"
               OpDecorate %gl_LaunchIDEXT BuiltIn LaunchIdKHR
               OpDecorate %gl_LaunchSizeEXT BuiltIn LaunchSizeKHR
               OpDecorate %topLevelAS Binding 0
               OpDecorate %topLevelAS DescriptorSet 0
               OpDecorate %result Binding 0
               OpDecorate %result DescriptorSet 1
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
      %v3int = OpTypeVector %int 3
%_ptr_Function_v3int = OpTypePointer Function %v3int
       %uint = OpTypeInt 32 0
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_LaunchIDEXT = OpVariable %_ptr_Input_v3uint Input
%gl_LaunchSizeEXT = OpVariable %_ptr_Input_v3uint Input
%_ptr_Function_uint = OpTypePointer Function %uint
     %uint_0 = OpConstant %uint 0
   %uint_255 = OpConstant %uint 255
      %float = OpTypeFloat 32
%_ptr_Function_float = OpTypePointer Function %float
    %float_0 = OpConstant %float 0
    %float_9 = OpConstant %float 9
    %v3float = OpTypeVector %float 3
%_ptr_Function_v3float = OpTypePointer Function %v3float
%_ptr_Input_uint = OpTypePointer Input %uint
  %float_0_5 = OpConstant %float 0.5
     %uint_1 = OpConstant %uint 1
    %float_1 = OpConstant %float 1
         %56 = OpConstantComposite %v3float %float_0 %float_0 %float_1
         %57 = OpTypeAccelerationStructureKHR
%_ptr_UniformConstant_57 = OpTypePointer UniformConstant %57
 %topLevelAS = OpVariable %_ptr_UniformConstant_57 UniformConstant
      %int_0 = OpConstant %int 0
%_ptr_IncomingRayPayloadKHR_v3float = OpTypePointer IncomingRayPayloadKHR %v3float
   %hitValue = OpVariable %_ptr_IncomingRayPayloadKHR_v3float IncomingRayPayloadKHR
%_ptr_HitAttributeKHR_v3float = OpTypePointer HitAttributeKHR %v3float
    %attribs = OpVariable %_ptr_HitAttributeKHR_v3float HitAttributeKHR
         %72 = OpTypeImage %int 3D 0 0 0 2 R32i
%_ptr_UniformConstant_72 = OpTypePointer UniformConstant %72
     %result = OpVariable %_ptr_UniformConstant_72 UniformConstant
       %main = OpFunction %void None %3
          %5 = OpLabel
        %pos = OpVariable %_ptr_Function_v3int Function
       %size = OpVariable %_ptr_Function_v3int Function
   %rayFlags = OpVariable %_ptr_Function_uint Function
   %cullMask = OpVariable %_ptr_Function_uint Function
       %tmin = OpVariable %_ptr_Function_float Function
       %tmax = OpVariable %_ptr_Function_float Function
     %origin = OpVariable %_ptr_Function_v3float Function
     %direct = OpVariable %_ptr_Function_v3float Function
         %14 = OpLoad %v3uint %gl_LaunchIDEXT
         %15 = OpBitcast %v3int %14
               OpStore %pos %15
         %18 = OpLoad %v3uint %gl_LaunchSizeEXT
         %19 = OpBitcast %v3int %18
               OpStore %size %19
               OpStore %rayFlags %uint_0
               OpStore %cullMask %uint_255
               OpStore %tmin %float_0
               OpStore %tmax %float_9
         %35 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_0
         %36 = OpLoad %uint %35
         %37 = OpConvertUToF %float %36
         %39 = OpFAdd %float %37 %float_0_5
         %40 = OpAccessChain %_ptr_Input_uint %gl_LaunchSizeEXT %uint_0
         %41 = OpLoad %uint %40
         %42 = OpConvertUToF %float %41
         %43 = OpFDiv %float %39 %42
         %45 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_1
         %46 = OpLoad %uint %45
         %47 = OpConvertUToF %float %46
         %48 = OpFAdd %float %47 %float_0_5
         %49 = OpAccessChain %_ptr_Input_uint %gl_LaunchSizeEXT %uint_1
         %50 = OpLoad %uint %49
         %51 = OpConvertUToF %float %50
         %52 = OpFDiv %float %48 %51
         %53 = OpCompositeConstruct %v3float %43 %52 %float_0
               OpStore %origin %53
               OpStore %direct %56
         %60 = OpLoad %57 %topLevelAS
         %61 = OpLoad %uint %rayFlags
         %62 = OpLoad %uint %cullMask
         %63 = OpLoad %v3float %origin
         %64 = OpLoad %float %tmin
         %65 = OpLoad %v3float %direct
         %66 = OpLoad %float %tmax
               OpTraceRayKHR %60 %61 %62 %uint_1 %uint_0 %uint_1 %63 %64 %65 %66 %hitValue
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The host creates a `16 x 16 x 1` `VK_FORMAT_R32_SINT` storage image, a host-visible transfer-destination buffer, one result-image descriptor set, and the acceleration-structure descriptor layout. Push cases mark set 0 with `VK_DESCRIPTOR_SET_LAYOUT_CREATE_PUSH_DESCRIPTOR_BIT_KHR` and do not allocate it ([shared setup](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L373-L439), [push-layout choice](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L304-L318)).
- The host creates a sloped square BLAS and TLAS. The plane's Z value varies from `2.0` to `4.0`, which gives each launch position a predictable hit distance ([geometry construction](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L588-L625)).
- `regular` calls `vkUpdateDescriptorSets`; `with_template` calls `vkUpdateDescriptorSetWithTemplate`; `with_push` records `vkCmdPushDescriptorSetKHR`; `with_push_template` records `vkCmdPushDescriptorSetWithTemplateKHR`. Source bookkeeping requires the executed-path count to equal one ([update selection](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L441-L486), [bind/push selection](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L511-L575)).
- The command buffer clears the result image, binds set 1, builds the acceleration structures, inserts a build-write to traversal-read barrier, and records the selected draw, dispatch, or ray trace. Ray-pipeline cases also build a service TLAS and shader binding tables to reach the selected stage ([common command path](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L488-L570), [ray-query service path](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L1685-L1823), [ray-tracing service path](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L2115-L2262)).
- After shader execution, a memory barrier makes shader writes available to transfer, and the host copies the image to the result buffer. It submits, waits, and invalidates mapped memory before reading ([copy and wait](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L561-L580)).
- For each pixel, the host derives the expected plane distance from the pixel center, multiplies it by `1048576`, and requires exact integer equality. Any mismatch returns `Fail` and logs coordinate, expected value, retrieved value, and mismatch grids ([verification](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L642-L723)).

## Failure Meaning

A failed leaf identifies a mismatch between the selected traversal mechanism, update method, stage, and the distance field observed by the host. The result does not isolate a driver, shader compiler, hardware, or CTS host-path defect on its own.

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `ray_query` | The updated acceleration-structure descriptor is not exposed to ray-query traversal in the selected stage, or the traversal/result path returns the wrong candidate distance. |
| `ray_tracing` | The updated acceleration-structure descriptor is not exposed to pipeline ray tracing in the selected stage, or recursive shader-group routing and hit-result recording produce the wrong distance. |

All values also depend on the selected `regular`, `with_template`, `with_push`, or `with_push_template` update method. A method-wide pattern can point to descriptor encoding, template interpretation, push-descriptor state, or command-recording errors shared by both traversal mechanisms.

### Cause Analysis

#### Ray-query descriptor exposure or candidate-distance failure

**Possible failure symptoms:** A `ray_query` leaf reports one or more retrieved fixed-point values that differ from the analytical sloped-plane values. A broad failure may affect every pixel; a stage- or position-specific defect may affect a subset of the image.

**Possible implementation causes:** The selected update method may encode, retain, or bind the wrong TLAS handle. The implementation may fail to expose set 0 in the selected stage, lower the ray-query operations to incorrect instructions, return the wrong candidate intersection type or distance, or lose the image write before copyback. Vulkan defines the TLAS descriptor as the traversal starting point and permits query traversal in any shader stage when supported ([TLAS role](../../../../vulkan-docs/src/chapters/accelstructures.adoc#L127-L137), [ray-query stage rule](../../../../vulkan-docs/src/chapters/raytraversal.adoc#L21-L24)). The mismatch pattern and failing update/stage variant narrow the investigation, but source-level investigation is needed to separate descriptor state, traversal, shader compilation, synchronization, and readback.

#### Pipeline ray-tracing descriptor exposure or shader-group/result failure

**Possible failure symptoms:** A `ray_tracing` `rgen`, `chit`, or `miss` leaf produces incorrect or zero fixed-point distances. The `chit` and `miss` variants may fail while `rgen` passes if the second trace, recursion, or shader-group route is defective.

**Possible implementation causes:** The descriptor update may provide the wrong TLAS to `traceRayEXT`, or pipeline layout and descriptor state may not reach the selected stage. Shader binding table group selection, the two-level trace used by `chit` and `miss`, hit-distance delivery through `gl_HitTEXT`, or the fixed output shader may instead be wrong. Vulkan requires shader execution to initiate traversal and treats the TLAS descriptor as its starting point ([traversal initiation](../../../../vulkan-docs/src/chapters/raytraversal.adoc#L4-L24), [TLAS role](../../../../vulkan-docs/src/chapters/accelstructures.adoc#L127-L137)). The host output cannot distinguish these mechanisms, so the failing path needs source-level investigation.

#### Shared descriptor-update method failure

**Possible failure symptoms:** Both `ray_query` and `ray_tracing` fail for one of `regular`, `with_template`, `with_push`, or `with_push_template`, often across several stages, while another update method passes.

**Possible implementation causes:** A regular write may mishandle the `VkWriteDescriptorSetAccelerationStructureKHR` `pNext` payload. A template path may read the acceleration-structure handle at the wrong offset or apply the wrong template type. A push path may fail to record set 0 descriptor state for the selected bind point or pipeline layout. The specification defines the acceleration-structure write source and separates descriptor-set templates from push-descriptor templates ([acceleration-structure source](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3161-L3167), [template type contract](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L4179-L4209)). A failure shared across methods may instead come from common AS build, synchronization, shader, or readback code and requires source-level investigation.

## Case Pruning

### Requirement-based pruning

- Every leaf requires `VK_KHR_acceleration_structure` and `VkPhysicalDeviceAccelerationStructureFeaturesKHR::accelerationStructure`. `ray_query` also requires `VK_KHR_ray_query` and `rayQuery`; `ray_tracing` requires `VK_KHR_ray_tracing_pipeline` and `rayTracingPipeline` ([base support checks](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L2355-L2389)).
- `ray_query` leaves placed in ray-tracing stages also require ray-tracing-pipeline support because the test needs a ray pipeline to invoke those stages ([ray-stage support check](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L1460-L1471)). Graphics-stage leaves apply their stage-specific tessellation or geometry feature checks ([graphics support](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L796-L822)).
- `with_template` requires `VK_KHR_descriptor_update_template`; `with_push` requires `VK_KHR_push_descriptor`; `with_push_template` requires both extensions ([update-method gates](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L2395-L2426)).
- `ray_tracing.chit` and `ray_tracing.miss` require `maxRayRecursionDepth >= 2`; unsupported devices skip those cases before pipeline creation ([recursion gate](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L1938-L1955)).
- The parent omits the complete branch from `CTS_USES_VULKANSC` builds ([parent registration](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L1911-L1916)).

### Design-based pruning

- `ray_query` covers all 12 registered stages because the query operation can execute inline wherever the source provides an invocation path.
- `ray_tracing` registers `rgen`, `chit`, and `miss`. The source marks those entries with `rayTracing = true` and skips all other stage entries for this mechanism ([stage table and filter](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L2592-L2637)).
- The shader walkthroughs use one compact compute query and one recursive closest-hit trace. Other update methods do not change shader text, while other stages preserve one of these two traversal mechanisms.

## Key Takeaways

- The 60 leaves check one TLAS descriptor through two different traversal mechanisms, four update methods, and the stages legal for each mechanism.
- `ray_query` reads candidate distance inline. `ray_tracing` uses shader-group routing, and its `chit` and `miss` cases launch a second ray before a fixed closest-hit stage records the distance.
- All paths converge on the same exact 256-value host oracle, so a passing case proves that the selected descriptor update led traversal to the expected sloped geometry.
- See `## Failure Meaning` to interpret failures by traversal mechanism and by update-method pattern.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Parent attachment | [`createDescriptorUpdateTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L1907-L1918) | Attaches the non-Vulkan-SC acceleration-structure branch. |
| Descriptor-layout helpers | [update-method helpers and layout flags](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L157-L213) | Distinguishes allocated descriptor sets from push-descriptor state. |
| Shared execution | [`BindingAcceleratioStructureTestInstance::iterate()`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L373-L586) | Creates resources, applies one update, executes, copies, and returns pass/fail. |
| Geometry and oracle | [AS creation and `verify()`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L588-L723) | Defines the sloped plane and exact expected distance field. |
| Graphics query path | [`BindingAcceleratioStructureGraphicsTestInstance`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L726-L1314) | Injects ray query into graphics stages and records the draw. |
| Compute query path | [`BindingAcceleratioStructureComputeTestInstance`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L1316-L1368) | Supplies the compact compute representative. |
| Ray-stage query path | [`BindingAcceleratioStructureRayTracingTestInstance`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L1370-L1842) | Runs ray query from six ray-tracing stages through a service pipeline. |
| Pipeline ray-tracing path | [`BindingAcceleratioStructureRayTracingRayTracingTestInstance`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L1844-L2281) | Implements selected-stage tracing, fixed output shaders, shader groups, SBTs, and service AS setup. |
| Generated shader bodies | [`getRayQueryShaderBodyText()` / `getRayTracingShaderBodyText()`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L2283-L2328) | Defines the two behavior mechanisms and their fixed-point stores. |
| Support and instance routing | [`BindingAccelerationStructureTestCase`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L2330-L2481) | Applies feature gates and selects the implementation for each leaf. |
| Branch registration | [`createDescriptorUpdateASTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L2566-L2662) | Generates the exact two-mechanism, four-method, stage matrix. |
| Mustpass evidence | [`binding-model.txt`](../../../mustpass/main/vk-default/binding-model.txt#L10898-L10957) | Confirms all 60 default mustpass leaves. |
| Normative descriptor updates | [Descriptor Set Updates](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L2900-L3167) | Defines descriptor writes and acceleration-structure source data. |
| Normative traversal model | [Ray Traversal](../../../../vulkan-docs/src/chapters/raytraversal.adoc#L4-L24) | Distinguishes query traversal from pipeline trace-ray execution. |
