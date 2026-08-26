## Overview

**Core question:** Does an acceleration structure built indirectly, where the build range count, primitive offset, first vertex, and transform offset come from a GPU-filled buffer rather than host-supplied parameters, produce the same hit/miss pattern as an equivalent direct build, for triangles (indexed and non-indexed), AABBs, and instances?

- [vktRayTracingBuildIndirectTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp) implements the single test family `indirect_acceleration_structure` under the `ray_tracing_pipeline` test category.
- All leaves share one scene shape (a `SQUARE_SIZE x SQUARE_SIZE` grid of primitives spread across `depth` geometries), one ray tracing pipeline with rgen/closest-hit/miss/intersection shaders, and one per-pixel result check. What varies is whether the acceleration structure is built once (`build`) or built-then-updated (`update`), and which `VkAccelerationStructureBuildRangeInfoKHR` field the leaf exercises.
- Each leaf populates a device-side indirect buffer by running a small rgen shader that writes a `VkAccelerationStructureBuildRangeInfoKHR` struct (primitive count, primitive offset, first vertex, transform offset), then builds the BLAS/TLAS with that indirect buffer, traces one ray per pixel straight down the -z axis, and compares the resulting per-pixel hit/miss values against an expected pattern derived from geometry placement.
- The page explains the build-versus-update axis, the per-field parameter matrix, the indirect-buffer generation mechanism, the offset arithmetic that backs each field, and what a failure of each field points to.

## Background Knowledge

- **Indirect acceleration structure builds.** `VK_KHR_acceleration_structure` allows a build to read its build range parameters from a device buffer instead of a host pointer. When `setIndirectBuildParameters` is used, `vkCmdBuildAccelerationStructuresIndirectKHR` reads one `VkAccelerationStructureBuildRangeInfoKHR` per geometry from the indirect buffer. The struct fields are `primitiveCount`, `primitiveOffset`, `firstVertex`, and `transformOffset`. This test requires the `accelerationStructureIndirectBuild` feature.
- **Build range fields.** `primitiveCount` limits how many primitives of the geometry are built. `primitiveOffset` is a byte offset into the vertex or AABB data. `firstVertex` is a vertex-index offset for indexed triangle geometry. `transformOffset` is a byte offset into the transform-data buffer. A correct indirect build must honor each field exactly as a host-supplied direct build would.
- **Acceleration structure updates.** A build with `VK_BUILD_ACCELERATION_STRUCTURE_ALLOW_UPDATE_BIT_KHR` can be rebuilt in-place with `vkCmdBuildAccelerationStructuresKHR` using the `VK_BUILD_ACCELERATION_STRUCTURE_MODE_UPDATE_KHR` mode. The `update` leaves build an intentionally wrong structure first, then update it so the indirect fields point at the correct geometry.
- **AABB expansion.** The Vulkan spec permits implementations to expand AABB geometries in an acceleration structure to mitigate precision issues, which can produce false-positive intersection reports. The AABB result check tolerates this.

## Registration Hierarchy

```text
ray_tracing_pipeline.indirect_acceleration_structure
├── build
└── update
```

The two direct children are registered by [createBuildIndirectTests](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1254-L1401). The `addIndirectTests` helper is called twice: once with `doUpdate == false` for the `build` child, and once with `doUpdate == true` for the `update` child. Each call registers the same four geometry-type groups (`triangles_indexed`, `triangles_no_index`, `aabbs`, `instances`) and the same field-intermediate nodes (`primitive_count`, `primitive_offset`, `first_vertex`, `transform_offset`) under each applicable geometry type.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Build/update mode | `build`, `update` | Direct child of the test family. `build` builds the structure once indirectly. `update` builds an intentionally wrong structure first, then rebuilds it in-place via an indirect update. This is the primary behavioral axis. | [createBuildIndirectTests](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1392-L1398) |
| Geometry type | `triangles_indexed`, `triangles_no_index`, `aabbs`, `instances` | Selects which BLAS geometry type is built indirectly, or whether the TLAS instance buffer is built indirectly. `triangles_no_index` uses the base `RayTracingBuildIndirectTestInstance`; `triangles_indexed` adds an index buffer; `aabbs` overrides `iterate`; `instances` overrides both TLAS and BLAS init. | [addIndirectTests groups](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1258-L1261) |
| Build range field | `primitive_count`, `primitive_offset`, `first_vertex`, `transform_offset` | Intermediate node selecting which `VkAccelerationStructureBuildRangeInfoKHR` field the leaf varies. `instances` uses `primitive_count` and `primitive_offset` against the instance buffer. `first_vertex` and `transform_offset` apply only to triangle geometry. | [field group construction](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1263-L1381) |
| Primitive count leaf | `5`, `10`, `15`, `20`, `25` | `primitiveCount` value, stepping down by `SQUARE_SIZE` from `SQUARE_SIZE*SQUARE_SIZE`. Fewer primitives means the back of the grid is not built and must miss. | [primCount loop](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1272-L1283) |
| Primitive offset leaf | `8`, `16`, `24`, `32`, `40`, `48` | `primitiveOffset` byte value for BLAS, stepping by 8. | [primOffset loop](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1311-L1321) |
| Instance offset leaf | `16`, `32`, `48`, `64`, `80`, `96`, `112`, `128` | `instancesOffset` byte value for TLAS, stepping by 16. | [instance primOffset loop](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1333-L1338) |
| First vertex leaf | `1` through `8` | `firstVertex` value for indexed triangle geometry, stepping by 1. | [firstVert loop](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1347-L1355) |
| Transform offset leaf | `16`, `32`, `48`, `64`, `80`, `96`, `112`, `128` | `transformOffset` byte value for triangle geometry, stepping by 16. | [transformOffset loop](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1368-L1377) |
| Instance count leaf | `1`, `2`, `3`, `4` | `instancesCount` for TLAS `primitive_count`, with `maxInstancesCount` fixed at 4. | [instancesCount loop](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1294-L1299) |
| SPIR-V target | `spirv1.4` | All generated shaders use `vk::SPIRV_VERSION_1_4`. | [ShaderBuildOptions](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L173) |

## Behavior Parameters

The primary behavioral axis is the build/update mode. Each value is a direct child of `ray_tracing_pipeline.indirect_acceleration_structure` and selects whether the acceleration structure is built once indirectly or built-then-updated indirectly. The geometry type, the field-intermediate node, and the leaf values are identical across the two modes; only the `doUpdate` flag differs.

### build - single indirect acceleration structure build

Builds the BLAS and TLAS once, with the indirect buffer supplying the `VkAccelerationStructureBuildRangeInfoKHR` fields. The vertex/index/AABB/instance data is laid out in a single buffer with the correct data at the offset the indirect field points at, plus padding vertices to keep the build within the buffer range. This is the baseline indirect path: if it fails, the indirect build is not honoring the field, or the shared trace pipeline and result check are suspect.

### update - indirect build followed by in-place update

Builds an intentionally wrong structure first - the indirect fields point at padding or fake geometry - then rebuilds it in-place with `VK_BUILD_ACCELERATION_STRUCTURE_ALLOW_UPDATE_BIT_KHR` so the fields point at the correct geometry. The first build and the update both use the same indirect buffer; for non-indexed triangle, AABB, and instance geometry the update shifts the resolved buffer address by one data block, while for indexed triangle geometry the index buffer address is unchanged and the update instead replaces the vertex buffer content (removing the padding vertices the first build inserted) so the resolved indices land on real vertices. This path exercises whether an indirect update correctly re-reads the indirect fields and rebuilds the structure to match the updated data. The expected result is identical to `build`; only the two-phase build differs.

## Shader Analysis

This walkthrough follows the shader-visible dataflow in producer-before-consumer order. `wr-asb` writes the indirect BLAS build-range records; the trace ray-generation shader then consumes the TLAS built from those records. The closest-hit, miss, and AABB intersection stages are fixed result/traversal support stages and are summarized under `#### Additional Info`.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.ray_tracing_pipeline.indirect_acceleration_structure.build.triangles_no_index.primitive_count.5
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `build` | The acceleration structure is built once from a device-filled indirect range buffer; no in-place update is performed. |
| `triangles_no_index` | The BLAS uses non-indexed triangles, so the producer emits the same four-field record for each of the eight BLAS geometries. |
| `primitive_count.5` | `wr-asb` embeds `primitiveCount = 5`; `primitiveOffset`, `firstVertex`, and `transformOffset` are zero. Only the first five primitives are built. |
| `wr-asb` → trace `rgen` | The first shader produces the indirect records; after the host build, the trace shader launches the 5x5x8 probe grid and generates the hit/miss signal. |
| `spirv1.4` | `initProgramsHelper` applies `ShaderBuildOptions(..., SPIRV_VERSION_1_4, ...)` to every generated stage. |

#### Purpose

The producer shader exercises the device-written `VkAccelerationStructureBuildRangeInfoKHR` path, while the trace shader turns the resulting BLAS/TLAS contents into a deterministic hit/miss signal. Together they test that indirect `primitiveCount` is consumed as a primitive count rather than ignored, shifted, or interpreted as a byte offset.

#### Structural Design

| Stage | Dataflow | Observable role |
|-------|----------|-----------------|
| `wr-asb` raygen | Loop `i = 0..7`; construct `uvec4(5, 0, 0, 0)`; store record `i` | Produces eight contiguous indirect BLAS range records with a 16-byte `uvec4` stride. |
| Host AS build | `vkCmdBuildAccelerationStructuresIndirectKHR` reads the producer buffer | Resolves the four build-range fields for each geometry. |
| Trace raygen | Map `gl_LaunchIDEXT` to `(x, y, z)`; trace from `(x + 200z, y, 0.5)` along `-z` | Probes the corresponding scene cell. |
| Fixed hit/miss stages | Closest-hit writes `HIT`; miss writes `MISS` | Supplies the value compared with the host-generated expected pattern. |

#### Shader Code

##### Indirect BLAS-Range Producer (`wr-asb`) Shader

This is the exact source emitted by `initProgramsHelper` for `primitiveCount = 5`, `primitiveOffset = 0`, `firstVertex = 0`, `transformOffset = 0`, and `depth = 8`. `updateRayTracingGLSL` is an identity function in this tree.

```glsl
#version 460 core
#extension GL_EXT_ray_tracing : require
/// Binding 0 is the storage buffer later consumed as the indirect BLAS range-info array.
/// Each std140 uvec4 occupies 16 bytes, matching one VkAccelerationStructureBuildRangeInfoKHR record.
layout(set = 0, binding = 0, std140) writeonly buffer OutBuf
{
  uvec4 accelerationStructureBuildOffsetInfoKHR[8];
} b_out;

void main()
{
  /// Emit one indirect range record for every BLAS geometry.
  for (uint i = 0; i < 8; i++)
  {
    /// This representative leaf varies only primitiveCount; the other fields are zero.
    uint primitiveCount  = 5u;
    uint primitiveOffset = 0u;
    uint firstVertex     = 0u;
    uint transformOffset = 0u;

    b_out.accelerationStructureBuildOffsetInfoKHR[i] = uvec4(
      primitiveCount, primitiveOffset, firstVertex, transformOffset);
  }
}
```

##### Trace Ray-Generation Shader

This is the exact fixed `rgen` source from the same generator. The depth term separates the eight slices by `SQUARE_OFFSET_X * 2`, while x/y retain the grid coordinates.

```glsl
#version 460 core
#extension GL_EXT_ray_tracing : require
/// Payload is declared for the hit/miss stages; this shader does not read it after tracing.
layout(location = 0) rayPayloadEXT vec3 hitValue;
/// TLAS assembled from the indirectly built BLAS instances.
layout(set = 0, binding = 1) uniform accelerationStructureEXT topLevelAS;

void main()
{
  uint  rayFlags = 0;
  uint  cullMask = 0xFF;
  float tmin     = 0.0;
  float tmax     = 9.0;
  float x        = float(gl_LaunchIDEXT.x);
  x              += float(gl_LaunchIDEXT.z) * float(100) * 2.0f;
  float y        = float(gl_LaunchIDEXT.y);
  vec3  origin   = vec3(x, y, 0.5);
  vec3  direct   = vec3(0.0, 0.0, -1.0);
  /// One ray per launch ID; hit/miss writes the result image.
  traceRayEXT(topLevelAS, rayFlags, cullMask, 0, 0, 0, origin, tmin, direct, tmax, 0);
}
```

#### Additional Info

- `wr-asb` is the producer for BLAS geometries. The analogous `wr-ast` shader writes one record for the TLAS: `instancesCount` occupies `primitiveCount`, and `instancesOffset` occupies `primitiveOffset` [producer generation](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L171-L242).
- The trace rgen is fixed across `build` and `update`, all geometry types, and all field leaves. Closest-hit stores `uvec4(1,0,0,1)`, miss stores `uvec4(2,0,0,1)`, and AABB cases additionally use an intersection shader that calls `reportIntersectionEXT(1.5, 0)` [trace/result stage generation](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L243-L314).
- The producer literals vary with `CaseDef`; its loop bound remains `depth = 8`. The update path changes host-side AS build sequencing and geometry/address setup, not generated shader text [CaseDef](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L74-L89) [initProgramsHelper](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L171-L242).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|-----------------------------------------|----------|
| Build range field/value | `wr-asb` keeps the same declarations and loop but embeds the selected `primitiveCount`, `primitiveOffset`, `firstVertex`, and `transformOffset` literals. `wr-ast` embeds the instance count/offset variant. | [initProgramsHelper](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L171-L242) |
| Geometry type | The three BLAS groups share the `wr-asb` producer shape; `instances` uses the single-record `wr-ast` variant. The trace rgen is unchanged. | [geometry-group registration](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1256-L1387) |
| Build/update mode | No generated shader changes; only the host AS build sequence and geometry/address setup change. | [update build sequence](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L615-L624) |
| Launch dimensions | The trace rgen uses `gl_LaunchIDEXT` directly. Fixed `width = height = 5`, `depth = 8` changes invocation count, not shader structure. | [CaseDef dimensions](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L74-L89) |

#### SPIR-V

##### Indirect BLAS-Range Producer (`wr-asb`) Shader

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `rgen` (`wr-asb` producer)
- Target SPIRV version: `spirv1.4`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.4
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 42
; Schema: 0
               OpCapability RayTracingKHR
               OpExtension "SPV_KHR_ray_tracing"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint RayGenerationKHR %main "main" %b_out
               OpSource GLSL 460
               OpSourceExtension "GL_EXT_ray_tracing"
               OpName %main "main"
               OpName %i "i"
               OpName %primitiveCount "primitiveCount"
               OpName %primitiveOffset "primitiveOffset"
               OpName %firstVertex "firstVertex"
               OpName %transformOffset "transformOffset"
               OpName %OutBuf "OutBuf"
               OpMemberName %OutBuf 0 "accelerationStructureBuildOffsetInfoKHR"
               OpName %b_out "b_out"
               OpDecorate %_arr_v4uint_uint_8 ArrayStride 16
               OpDecorate %OutBuf Block
               OpMemberDecorate %OutBuf 0 NonReadable
               OpMemberDecorate %OutBuf 0 Offset 0
               OpDecorate %b_out NonReadable
               OpDecorate %b_out Binding 0
               OpDecorate %b_out DescriptorSet 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
     %uint_0 = OpConstant %uint 0
     %uint_8 = OpConstant %uint 8
       %bool = OpTypeBool
     %uint_5 = OpConstant %uint 5
     %v4uint = OpTypeVector %uint 4
%_arr_v4uint_uint_8 = OpTypeArray %v4uint %uint_8
     %OutBuf = OpTypeStruct %_arr_v4uint_uint_8
%_ptr_StorageBuffer_OutBuf = OpTypePointer StorageBuffer %OutBuf
      %b_out = OpVariable %_ptr_StorageBuffer_OutBuf StorageBuffer
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_StorageBuffer_v4uint = OpTypePointer StorageBuffer %v4uint
      %int_1 = OpConstant %int 1
       %main = OpFunction %void None %3
          %5 = OpLabel
          %i = OpVariable %_ptr_Function_uint Function
%primitiveCount = OpVariable %_ptr_Function_uint Function
%primitiveOffset = OpVariable %_ptr_Function_uint Function
%firstVertex = OpVariable %_ptr_Function_uint Function
%transformOffset = OpVariable %_ptr_Function_uint Function
               OpStore %i %uint_0
               OpBranch %10
         %10 = OpLabel
               OpLoopMerge %12 %13 None
               OpBranch %14
         %14 = OpLabel
         %15 = OpLoad %uint %i
         %18 = OpULessThan %bool %15 %uint_8
               OpBranchConditional %18 %11 %12
         %11 = OpLabel
               OpStore %primitiveCount %uint_5
               OpStore %primitiveOffset %uint_0
               OpStore %firstVertex %uint_0
               OpStore %transformOffset %uint_0
         %31 = OpLoad %uint %i
         %32 = OpLoad %uint %primitiveCount
         %33 = OpLoad %uint %primitiveOffset
         %34 = OpLoad %uint %firstVertex
         %35 = OpLoad %uint %transformOffset
         %36 = OpCompositeConstruct %v4uint %32 %33 %34 %35
         %38 = OpAccessChain %_ptr_StorageBuffer_v4uint %b_out %int_0 %31
               OpStore %38 %36
               OpBranch %13
         %13 = OpLabel
         %39 = OpLoad %uint %i
         %41 = OpIAdd %uint %39 %int_1
               OpStore %i %41
               OpBranch %10
         %12 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

##### Trace Ray-Generation Shader

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `rgen` (trace consumer)
- Target SPIRV version: `spirv1.4`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.4
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 65
; Schema: 0
               OpCapability RayTracingKHR
               OpExtension "SPV_KHR_ray_tracing"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint RayGenerationKHR %main "main" %gl_LaunchIDEXT %topLevelAS %hitValue
               OpSource GLSL 460
               OpSourceExtension "GL_EXT_ray_tracing"
               OpName %main "main"
               OpName %rayFlags "rayFlags"
               OpName %cullMask "cullMask"
               OpName %tmin "tmin"
               OpName %tmax "tmax"
               OpName %x "x"
               OpName %gl_LaunchIDEXT "gl_LaunchIDEXT"
               OpName %y "y"
               OpName %origin "origin"
               OpName %direct "direct"
               OpName %topLevelAS "topLevelAS"
               OpName %hitValue "hitValue"
               OpDecorate %gl_LaunchIDEXT BuiltIn LaunchIdKHR
               OpDecorate %topLevelAS Binding 1
               OpDecorate %topLevelAS DescriptorSet 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
     %uint_0 = OpConstant %uint 0
   %uint_255 = OpConstant %uint 255
      %float = OpTypeFloat 32
%_ptr_Function_float = OpTypePointer Function %float
    %float_0 = OpConstant %float 0
    %float_9 = OpConstant %float 9
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_LaunchIDEXT = OpVariable %_ptr_Input_v3uint Input
%_ptr_Input_uint = OpTypePointer Input %uint
     %uint_2 = OpConstant %uint 2
  %float_100 = OpConstant %float 100
    %float_2 = OpConstant %float 2
     %uint_1 = OpConstant %uint 1
    %v3float = OpTypeVector %float 3
%_ptr_Function_v3float = OpTypePointer Function %v3float
  %float_0_5 = OpConstant %float 0.5
   %float_n1 = OpConstant %float -1
         %50 = OpConstantComposite %v3float %float_0 %float_0 %float_n1
         %51 = OpTypeAccelerationStructureKHR
%_ptr_UniformConstant_51 = OpTypePointer UniformConstant %51
 %topLevelAS = OpVariable %_ptr_UniformConstant_51 UniformConstant
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_RayPayloadKHR_v3float = OpTypePointer RayPayloadKHR %v3float
   %hitValue = OpVariable %_ptr_RayPayloadKHR_v3float RayPayloadKHR
       %main = OpFunction %void None %3
          %5 = OpLabel
   %rayFlags = OpVariable %_ptr_Function_uint Function
   %cullMask = OpVariable %_ptr_Function_uint Function
       %tmin = OpVariable %_ptr_Function_float Function
       %tmax = OpVariable %_ptr_Function_float Function
          %x = OpVariable %_ptr_Function_float Function
          %y = OpVariable %_ptr_Function_float Function
     %origin = OpVariable %_ptr_Function_v3float Function
     %direct = OpVariable %_ptr_Function_v3float Function
               OpStore %rayFlags %uint_0
               OpStore %cullMask %uint_255
               OpStore %tmin %float_0
               OpStore %tmax %float_9
         %23 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_0
         %24 = OpLoad %uint %23
         %25 = OpConvertUToF %float %24
               OpStore %x %25
         %27 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_2
         %28 = OpLoad %uint %27
         %29 = OpConvertUToF %float %28
         %31 = OpFMul %float %29 %float_100
         %33 = OpFMul %float %31 %float_2
         %34 = OpLoad %float %x
         %35 = OpFAdd %float %34 %33
               OpStore %x %35
         %38 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_1
         %39 = OpLoad %uint %38
         %40 = OpConvertUToF %float %39
               OpStore %y %40
         %44 = OpLoad %float %x
         %45 = OpLoad %float %y
         %47 = OpCompositeConstruct %v3float %44 %45 %float_0_5
               OpStore %origin %47
               OpStore %direct %50
         %54 = OpLoad %51 %topLevelAS
         %55 = OpLoad %uint %rayFlags
         %56 = OpLoad %uint %cullMask
         %57 = OpLoad %v3float %origin
         %58 = OpLoad %float %tmin
         %59 = OpLoad %v3float %direct
         %60 = OpLoad %float %tmax
               OpTraceRayKHR %54 %55 %56 %uint_0 %uint_0 %uint_0 %57 %58 %59 %60 %hitValue
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

### Indirect buffer generation

- Before the build, two small rgen shaders run on the device to fill the indirect buffers. `wr-asb` writes one `VkAccelerationStructureBuildRangeInfoKHR` per BLAS geometry into a storage buffer, baking `primitiveCount`, `primitiveOffset`, `firstVertex`, and `transformOffset` from the case's `CaseDef` [initProgramsHelper wr-asb](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L174-L211). `wr-ast` writes a single struct for the TLAS, baking `instancesCount` and `instancesOffset` [initProgramsHelper wr-ast](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L212-L242).
- The indirect buffers are created with `VK_BUFFER_USAGE_STORAGE_BUFFER_BIT | VK_BUFFER_USAGE_SHADER_DEVICE_ADDRESS_BIT` and are host-visible. `prepareBuffer` builds a one-group ray tracing pipeline, records `cmdTraceRays(1,1,1)`, and submits it to fill the buffer [prepareBuffer](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L933-L999).
- The BLAS indirect buffer holds `geometriesGroupCount` structs and the TLAS indirect buffer holds one struct, both with stride `sizeof(VkAccelerationStructureBuildRangeInfoKHR)` [initIndirectBottomAccelerationStructure](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1173-L1182) [initIndirectTopAccelerationStructure](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1163-L1171).

### Geometry layout and offset arithmetic

- The scene is a `SQUARE_SIZE x SQUARE_SIZE` grid of primitives. Each primitive covers one cell. A deterministic rule (`primId % 7 == 5`) marks certain cells as miss cells by placing their geometry out of the ray path [isMissTriangle](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L59-L63).
- For `primitive_count`, only the first `primitiveCount` primitives are built. Cells whose linear index `n >= primitiveCount` must miss, so the expected value is `MISS` for them [primitive_count loop](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1272-L1283).
- For `primitive_offset`, the vertex or AABB data is laid out with the real geometry at a byte offset into the buffer. The test negates the offset when setting the buffer address (`setVertexBufferAddressOffset(-m_data.primitiveOffset)`) so the resolved address lands on the real geometry, and adds padding primitives behind it to keep the build in range [non-indexed BLAS offset](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L572-L603) [AABB BLAS offset](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L766-L795).
- For `first_vertex`, the indexed triangle geometry is laid out with fake triangles before the real vertices, and the index values are shifted by `firstVertexReminder` so the resolved `firstVertex` lands on the correct vertices [indexed BLAS firstVertex](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L657-L687).
- For `transform_offset`, the transform-data buffer is laid out with the real transform at a byte offset, and `setTransformBufferAddressOffset(-m_data.transformOffset)` resolves the address [transform offset](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L571) [transform offset loop](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1368-L1377).
- For `instances`, the TLAS holds `2 * maxInstancesCount + 1` instance slots. Only the first `instancesCount` instances are built via the indirect `primitiveCount`, and the real instances are placed at a byte offset resolved by negating `instancesOffset` [instances TLAS](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L831-L875).

### Update path

- For `update`, the first build points the indirect field at padding or fake geometry. The `doUpdate` flag adds `VK_BUILD_ACCELERATION_STRUCTURE_ALLOW_UPDATE_BIT_KHR`, builds the wrong structure, then either adjusts the buffer address offset by one data block (non-indexed triangle, AABB, instances) or replaces the geometry via `updateGeometry` to remove the padding vertices (indexed triangle), and calls `build` again in update mode so the field resolves to the correct geometry [non-indexed update](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L615-L624) [indexed update](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L699-L742) [AABB update](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L800-L808) [instances update](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L860-L869).

### Trace and result copyback

- The result image is a 3D `r32ui` storage image sized `width x height x depth`. It is cleared to `(5,5,5,255)` and transitioned to `GENERAL` before the trace [runTest image setup](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1053-L1097).
- `cmdTraceRays` launches `width x height x depth` rays. Each raygen invocation traces one ray down -z into the TLAS; the closest-hit or miss shader writes the per-pixel result into the image [trace dispatch](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1125-L1127).
- After the trace, a `SHADER_WRITE` -> `TRANSFER_READ` barrier, `cmdCopyImageToBuffer`, and a `TRANSFER_WRITE` -> `HOST_READ` barrier move the image into a host-visible buffer [copyback](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1129-L1135).

### Per-pixel result check

- The host scans every pixel across all `depth` slices. The expected value is `HIT` for valid cells whose linear index `n` is not a miss cell and `n < primitiveCount`; otherwise `MISS` [iterate](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1195-L1209).
- For triangle geometry, a mismatched pixel always counts as a failure. For AABB geometry, a mismatched pixel is only a failure if the expected value was `HIT` and the observed value was not `HIT`; this tolerates implementation AABB expansion that reports a hit where the test expected a miss [AABB iterate](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1235-L1243).
- Pass condition: `failures == 0` [iterate pass/fail](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1211-L1214).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `build` | Indirect build did not honor a `VkAccelerationStructureBuildRangeInfoKHR` field (count or offset), so the built structure does not match the equivalent direct build and the hit/miss pattern is wrong. |
| `update` | Indirect update did not re-read the fields or did not rebuild the structure to match the updated data, so the post-update structure still reflects the intentionally wrong first build. |

All leaves share the indirect-buffer generation, the scene construction, the trace pipeline, and the per-pixel result check, so a failure common to both `build` and `update` for the same geometry type and field points at shared infrastructure (indirect buffer fill, geometry data layout, offset arithmetic, SBT, image copyback, expected-value rule) rather than an update-specific issue. A failure common to all fields for one geometry type points at that geometry type's BLAS or TLAS init path.

### Cause Analysis

#### Indirect build range field ignored or misapplied

**Possible failure symptoms:** A `build` leaf failure where the result image has mismatched pixels. The specific pattern depends on the field. A `primitive_count` failure shows hits where the back of the grid should have been unbuilt (cells with `n >= primitiveCount` report `HIT` instead of `MISS`), or misses across the whole grid if the count was applied to the wrong buffer region. A `primitive_offset` or `transform_offset` failure shows a shifted or empty hit pattern, because the resolved address landed on padding vertices, the wrong transform, or out-of-range memory. A `first_vertex` failure shows hits at wrong cells or a completely empty grid, because the resolved index stream pointed at fake vertices. A `primitive_offset` failure for `instances` shows the wrong number of instances or instances at wrong transforms. The failure count is nonzero.

**Possible implementation causes:** The indirect build reads `VkAccelerationStructureBuildRangeInfoKHR` from the device buffer supplied via `setIndirectBuildParameters`. A grounded investigation should check whether the driver resolved the indirect buffer's device address and stride correctly when recording `vkCmdBuildAccelerationStructuresIndirectKHR`, whether each field was read with the right type and units (`primitiveOffset` and `transformOffset` are byte offsets; `firstVertex` is a vertex index; `primitiveCount` is a primitive count), and whether the resolved vertex/index/AABB/instance/transform buffer addresses plus the field value landed inside the allocated buffer range. The spec ties indirect builds to the `accelerationStructureIndirectBuild` feature; if that feature is reported but the build ignores or misapplies a field, the cause is in the indirect build implementation. If `build` and `update` both fail at the same field and geometry type, the cause is shared offset arithmetic or data layout rather than the build path. If only one field fails, source-level investigation of that field's offset setup in the corresponding `initBottomAccelerationStructure` or `initTopAccelerationStructure` override is needed.

#### Indirect update not re-reading fields or not rebuilding

**Possible failure symptoms:** An `update` leaf failure where the corresponding `build` leaf with the same geometry type and field passes. The result image reflects the intentionally wrong first build rather than the corrected geometry: cells that should be `HIT` are `MISS` (or vice versa), or the whole grid is empty because the first build pointed at padding or fake geometry and the update did not move it. The failure count is nonzero.

**Possible implementation causes:** The `update` path sets `VK_BUILD_ACCELERATION_STRUCTURE_ALLOW_UPDATE_BIT_KHR` on the first build, then calls `build` again in `VK_BUILD_ACCELERATION_STRUCTURE_MODE_UPDATE_KHR` after either adjusting the buffer address offset (non-indexed triangle, AABB, instances) or replacing the geometry via `updateGeometry` to remove the padding vertices (indexed triangle). The update must re-read the indirect fields and rebuild the structure so the traversal result matches the corrected data. A grounded investigation should check whether the update re-read the indirect buffer at all or reused the first build's resolved parameters, whether the updated buffer address offset (or replaced geometry, for indexed triangle) was applied before the update build, and whether the update mode produced a structure equivalent to a fresh build. The spec states an update rebuilds the structure in-place using the same size and flags; if the implementation treats an indirect update as a no-op or fails to re-resolve the indirect parameters, the post-update structure stays wrong. If `build` passes but `update` fails, the cause is update-path-specific and source-level investigation of the update sequence in the corresponding `initBottomAccelerationStructure` or `initTopAccelerationStructure` override is needed.

#### Shared infrastructure failure

**Possible failure symptoms:** Both `build` and `update` fail for the same geometry type and field with the same pixel pattern, or all fields fail for one geometry type regardless of the field value.

**Possible implementation causes:** The indirect-buffer fill (`wr-asb`/`wr-ast`), the scene construction, the trace pipeline, the SBT, the result image clear and copyback, and the expected-value rule are identical across `build` and `update` and across fields. A failure common to both modes points at this shared setup. A grounded investigation should check whether the `wr-asb`/`wr-ast` rgen shader wrote the `VkAccelerationStructureBuildRangeInfoKHR` struct with the correct field values, whether the indirect buffer's device address was passed correctly to `setIndirectBuildParameters`, whether the deterministic miss-cell placement (`primId % 7 == 5`) produced the expected z-offsets, and whether the per-pixel expected-value rule in `iterate` matches the geometry placement. For `instances`, check that the TLAS instance count and offset arithmetic in `RayTracingBuildInstances::initTopAccelerationStructure` produced the expected valid-instance set. Source-level inspection of `initProgramsHelper` and `iterate` is needed to confirm the indirect-buffer and expected-value correspondence.

## Case Pruning

### Requirement-based pruning

- All leaves require `VK_KHR_acceleration_structure` and `VK_KHR_ray_tracing_pipeline`, with the `accelerationStructure` and `rayTracingPipeline` feature bits set. If either is not set, the test throws `NotSupportedError` [checkSupport](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L519-L529).
- All leaves additionally require `accelerationStructureIndirectBuild`; otherwise the test throws `NotSupportedError` [indirect build feature gate](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L531-L533).
- At instance time, the test checks ray tracing property limits: `maxPrimitiveCount` must cover the case's `primitiveCount`, `maxGeometryCount` must cover `geometriesGroupCount`, and `maxInstanceCount` must cover `instancesCount`. Any shortfall throws `NotSupportedError` [checkSupportInInstance](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1147-L1161).

### Design-based pruning

- `first_vertex` and `transform_offset` are registered only under `triangles_indexed` and `triangles_no_index`, because those fields are triangle-geometry-specific. `aabbs` and `instances` do not receive those field groups [field group registration](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1341-L1381).
- `instances` uses `primitive_count` (instance count) and `primitive_offset` (instance offset) against the TLAS instance buffer, not the BLAS primitive fields, so its field-intermediate nodes have instance-specific semantics [instances field loops](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1288-L1300) [instance primOffset loop](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1326-L1339).
- The `primitive_count` leaf values step downward from the full grid (`SQUARE_SIZE * SQUARE_SIZE`) by `SQUARE_SIZE`, so the smallest count (`SQUARE_SIZE`) leaves most of the grid unbuilt and must miss. This confirms that `primitiveCount` is honored, rather than only testing a full build [primCount loop](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1272-L1273).

## Key Takeaways

- The `indirect_acceleration_structure` family isolates the indirect build path as the behavioral axis: a single indirect build (`build`) versus an indirect build followed by an in-place update (`update`). The geometry type, the build range field, and the leaf values are identical across both modes.
- The per-field matrix exercises each `VkAccelerationStructureBuildRangeInfoKHR` field independently (`primitiveCount`, `primitiveOffset`, `firstVertex`, and `transformOffset`) against triangles (indexed and non-indexed), AABBs, and instances, so a failure can be attributed to a specific field and geometry type.
- The indirect buffer is filled on the device by two rgen shaders, so the test covers the full device-side indirect path: GPU writes the build range info, the driver reads it during `vkCmdBuildAccelerationStructuresIndirectKHR`, and the result is compared against an expected pattern derived from geometry placement.
- The result check compares a deterministic hit/miss pattern; for AABB geometry it tolerates implementation AABB expansion that produces an extra hit, but not a miss where a hit was expected.
- A failure isolated to `build` points at the indirect build not honoring a field; a failure isolated to `update` points at the update not re-reading the fields; a failure common to both points at shared indirect-buffer or scene infrastructure. See `## Failure Meaning` for the per-mode cause analysis.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `CaseDef` struct | [vktRayTracingBuildIndirectTests.cpp#L74-L89](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L74-L89) | Per-case parameters: primitive count, offsets, first vertex, instance counts, doUpdate |
| `isMissTriangle` | [vktRayTracingBuildIndirectTests.cpp#L59-L63](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L59-L63) | Deterministic miss-cell placement rule |
| `initProgramsHelper` | [vktRayTracingBuildIndirectTests.cpp#L171-L315](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L171-L315) | Generated rgen/chit/miss/rint shaders, including the indirect-buffer writer shaders |
| `RayTracingBuildIndirectTestInstance` | [vktRayTracingBuildIndirectTests.cpp#L398-L427](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L398-L427) | Base instance: non-indexed triangle BLAS, TLAS, indirect buffer setup, iterate |
| `RayTracingBuildTrianglesIndexed` | [vktRayTracingBuildIndirectTests.cpp#L441-L451](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L441-L451) | Indexed triangle BLAS override with first_vertex and index buffer offset |
| `RayTracingBuildAABBs` | [vktRayTracingBuildIndirectTests.cpp#L453-L463](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L453-L463) | AABB BLAS override with AABB-tolerant iterate |
| `RayTracingBuildInstances` | [vktRayTracingBuildIndirectTests.cpp#L465-L479](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L465-L479) | Instance TLAS/BLAS override with instance count and offset |
| `checkSupport` | [vktRayTracingBuildIndirectTests.cpp#L518-L534](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L518-L534) | Feature gates for acceleration structure, ray tracing pipeline, indirect build |
| `initTopAccelerationStructure` (base) | [vktRayTracingBuildIndirectTests.cpp#L536-L555](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L536-L555) | Base TLAS init with indirect build parameters |
| `initBottomAccelerationStructure` (base) | [vktRayTracingBuildIndirectTests.cpp#L557-L632](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L557-L632) | Non-indexed triangle BLAS with primitive/first-vertex/transform offset arithmetic |
| `initBottomAccelerationStructure` (indexed) | [vktRayTracingBuildIndirectTests.cpp#L634-L750](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L634-L750) | Indexed triangle BLAS with first_vertex and index buffer offset |
| `initBottomAccelerationStructure` (AABBs) | [vktRayTracingBuildIndirectTests.cpp#L752-L817](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L752-L817) | AABB BLAS with primitive offset arithmetic |
| `initTopAccelerationStructure` (instances) | [vktRayTracingBuildIndirectTests.cpp#L819-L878](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L819-L878) | Instance TLAS with count and offset arithmetic |
| `initBottomAccelerationStructure` (instances) | [vktRayTracingBuildIndirectTests.cpp#L880-L931](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L880-L931) | Instance BLAS shared by the instances group |
| `prepareBuffer` | [vktRayTracingBuildIndirectTests.cpp#L933-L999](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L933-L999) | Device-side indirect buffer fill via one-group rgen trace |
| `runTest` | [vktRayTracingBuildIndirectTests.cpp#L1001-L1145](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1001-L1145) | AS build, trace dispatch, and result copyback |
| `checkSupportInInstance` | [vktRayTracingBuildIndirectTests.cpp#L1147-L1161](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1147-L1161) | Runtime property-limit pruning |
| `iterate` (base) | [vktRayTracingBuildIndirectTests.cpp#L1184-L1215](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1184-L1215) | Per-pixel expected-value rule and pass/fail condition |
| `iterate` (AABBs) | [vktRayTracingBuildIndirectTests.cpp#L1217-L1250](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1217-L1250) | AABB-expansion-tolerant result check |
| `addIndirectTests` | [vktRayTracingBuildIndirectTests.cpp#L1256-L1387](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1256-L1387) | Per-geometry-type and per-field matrix generation |
| `createBuildIndirectTests` | [vktRayTracingBuildIndirectTests.cpp#L1254-L1401](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1254-L1401) | Registration of the build and update direct children |