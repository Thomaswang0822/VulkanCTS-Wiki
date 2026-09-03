## Overview

**Core question:** Do NV mesh and task shaders expose each selected built-in with the value that the following rasterization stages observe?

- This page covers `vktMeshShaderBuiltinTests.cpp`, which registers the `mesh_shader.nv.builtin` test family and implements 20 scalar/identifier built-in cases plus the nine primitive-shading-rate combinations.
- The tests generate small NV mesh/task/fragment programs, render to an `8x8` or `8x1` `R8G8B8A8_UNORM` target, copy the image to host memory, and compare exact pixels.
- The central variations are the built-in being exercised, whether a task shader supplies the mesh workgroup, whether vertices are shared between primitives, and the top/bottom fragment sizes for primitive shading rate.
- The page explains registration, support gates, generated shader behavior, host/reference checking, exact `vk-default` coverage, and why a failure points to a particular stage or interface.

## Background Knowledge

- A `MeshNV` shader executes as a workgroup and emits indexed vertices and primitives. An optional `TaskNV` shader emits mesh workgroups and can pass `PerTaskNV` values to them; without a task shader, the draw launches mesh workgroups directly. See [Mesh Shading](../../../../vulkan-docs/src/chapters/VK_NV_mesh_shader/mesh.adoc#mesh).
- NV mesh outputs have per-vertex and per-primitive scopes. `Position`, `PointSize`, `ClipDistance`, and `CullDistance` are vertex outputs; `Layer`, `ViewportIndex`, `PrimitiveId`, and `PrimitiveShadingRateKHR` identify emitted primitives. `PrimitiveIndicesNV` maps each primitive to entries in the vertex output arrays. The built-in definitions are in [Built-in Variables](../../../../vulkan-docs/src/chapters/interfaces.adoc#interfaces-builtin-variables).
- A primitive shading rate contributes to the fragment shading rate, while the fragment shader reads the resulting `ShadingRateKHR`. The NV mesh output and fragment-operation rules determine how the value reaches the fragment stage.

## Registration Hierarchy

```text
mesh_shader.nv.builtin
├── position
├── point_size
├── clip_distance
├── cull_distance
├── primitive_id_glsl
├── primitive_id_spirv
├── layer
├── layer_shared
├── viewport_index
├── viewport_index_shared
├── work_group_id_in_mesh
├── work_group_id_in_task
├── local_invocation_id_in_mesh
├── local_invocation_id_in_task
├── local_invocation_index_in_task
├── local_invocation_index_in_mesh
├── global_invocation_id_in_mesh
├── global_invocation_id_in_task
├── draw_index_in_mesh
├── draw_index_in_task
├── primitive_shading_rate_2x2_2x2
├── primitive_shading_rate_2x2_2x1
├── primitive_shading_rate_2x2_1x1
├── primitive_shading_rate_2x1_2x2
├── primitive_shading_rate_2x1_2x1
├── primitive_shading_rate_2x1_1x1
├── primitive_shading_rate_1x1_2x2
├── primitive_shading_rate_1x1_2x1
└── primitive_shading_rate_1x1_1x1
```

`createMeshShaderBuiltinTests` creates the `builtin` test family and adds the first 20 children explicitly. It then loops over the three `FragmentSize` values for the top and bottom halves, producing the nine remaining names. The category dispatcher routes this factory under `mesh_shader.nv.builtin`; the obsolete page is retained as a source-navigation aid.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Built-in behavior | `position`, `point_size`, `clip_distance`, `cull_distance`, `primitive_id_glsl`, `primitive_id_spirv`, `layer`, `viewport_index`, invocation identifiers, and draw index | Selects the value written or read by the generated shader and the matching host reference | [factory registration](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTests.cpp#L2041-L2068) |
| Task path | `_in_mesh` versus `_in_task` for workgroup, local/global invocation, and draw index | Chooses direct mesh built-ins or a `TaskNV` payload written by a task shader | [workgroup and invocation generators](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTests.cpp#L1373-L1759) |
| Vertex sharing | `layer`/`viewport_index` versus `layer_shared`/`viewport_index_shared` | Uses four workgroups with one primitive each, or one workgroup with four invocations sharing three vertices | [layer and viewport generators](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTests.cpp#L699-L956) |
| Primitive shading-rate top half | `2x2`, `2x1`, `1x1` | Selects the mask written to the first two triangles | [shading-rate loop and masks](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTests.cpp#L1785-L1791) |
| Primitive shading-rate bottom half | `2x2`, `2x1`, `1x1` | Selects the mask written to the last two triangles | [shading-rate loop](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTests.cpp#L2070-L2087) |
| Render target | `8x8` or `8x1`, one layer except layer tests | Gives the generators a deterministic pixel coordinate space | [extent helpers](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTests.cpp#L100-L124) |
| Draw mode | direct draw for most cases; repeated indirect draw for draw index | Makes `gl_DrawID` vary only in the draw-index family | [draw-index instance](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTests.cpp#L1745-L1758) |

The exact `vk-default` mustpass file contains 29 NV built-in leaves: `position`, `point_size`, `clip_distance`, and `cull_distance`, the two primitive-ID leaves, the two layer leaves, the two viewport leaves, ten local/global/workgroup/draw identifier leaves, and nine shading-rate leaves. It does not contain the EXT-only additions such as `view_index`, `num_work_groups_*`, `*_no_write`, or mixed distance cases. The authoritative list is [vk-default/mesh-shader.txt](../../../mustpass/main/vk-default/mesh-shader.txt#L27327-L27355).

## Behavior Parameters

The primary behavioral axis is the registered direct child. The following subsections group the 29 exact values by the mechanism they select.

### `position` — one-pixel position

The mesh shader emits a triangle around the center of the top-left pixel. The `PixelsInstance` expects only `(0,0)` to be blue and every other pixel to retain the black clear color.

### `point_size` — point rasterization

The mesh shader emits one point with `gl_PointSize = 4.0`. The `QuadrantsInstance` expects blue in the top-left quadrant and black elsewhere; support also checks large points and the device point-size range.

### `clip_distance` — vertex clipping

Two clip-distance planes retain only the top-left quadrant. The fragment shader checks both interpolated distances, while the host expects blue in that quadrant and black elsewhere.

### `cull_distance` — primitive culling

Two cull-distance arrays discard the lower quad and split the upper quad into blue and white halves. The host reference is blue, white, black, black by quadrant.

### `primitive_id_glsl` — GLSL fragment input

The mesh shader writes primitive ID `1629198956`; generated GLSL reads `gl_PrimitiveID` and turns an exact match blue. This path requires the core Geometry Shader feature because glslang uses the Geometry capability for that GLSL built-in.

### `primitive_id_spirv` — direct-SPIR-V fragment input

The mesh shader is the same, but the fragment program is a CTS-authored SPIR-V string whose capability is `MeshShadingNV` rather than `Geometry`. It checks the same integer and has the same blue reference.

### `layer` — one primitive per workgroup

Four workgroups each emit one triangle and write a layer from `gl_WorkGroupID.x`. The four-layer framebuffer is checked against four fixed colors.

### `layer_shared` — shared vertices with per-primitive layers

One workgroup uses four local invocations. Invocation zero writes the three shared vertices; each invocation writes its own primitive indices and layer. This isolates per-primitive layer output from vertex sharing.

### `viewport_index` — one primitive per viewport

Four workgroups write `gl_ViewportIndex` from `gl_WorkGroupID.x`. Four half-size viewports map to four expected quadrant colors.

### `viewport_index_shared` — shared vertices with per-primitive viewports

One workgroup and four local invocations share the vertices while writing four primitive viewport indices. The same four viewport colors verify that primitive metadata remains independent of shared vertex storage.

### `work_group_id_in_mesh` — direct mesh workgroup ID

Eight direct mesh workgroups each use `gl_WorkGroupID.x` as the one-pixel triangle number in an `8x1` target.

### `work_group_id_in_task` — task-provided workgroup ID

Eight task workgroups write their `gl_WorkGroupID.x` into `PerTaskNV` data, emit one mesh workgroup each, and the mesh shader uses the payload as its pixel number.

### `local_invocation_id_in_mesh` — direct vector local ID

An eight-invocation mesh workgroup uses `gl_LocalInvocationID.x` to choose one pixel and three output vertices per invocation.

### `local_invocation_id_in_task` — task payload for local ID

The task shader writes each local invocation number into `indexNumber[]`; the mesh shader reads the payload in its spawned workgroup and emits the matching pixel triangle.

### `local_invocation_index_in_task` — task payload for linear index

The task path uses `gl_LocalInvocationIndex` to fill and later consume an identity payload array, checking the linear-index built-in across the task-to-mesh interface.

### `local_invocation_index_in_mesh` — direct linear index

The mesh path uses `gl_LocalInvocationIndex` directly for pixel selection and for the per-invocation base vertex index.

### `global_invocation_id_in_mesh` — direct global ID

Eight draws of eight-invocation mesh workgroups use `gl_GlobalInvocationID.x` to address all 64 pixels in the `8x8`-equivalent linear workload.

### `global_invocation_id_in_task` — task payload for global ID

The task shader writes each `gl_GlobalInvocationID.x` to `PerTaskNV` data and the mesh shader uses that payload to address its output pixel.

### `draw_index_in_mesh` — direct draw ID

The test makes eight indirect draws, each with one task, and the mesh shader uses `uint(gl_DrawID)` to select one pixel in an `8x1` target.

### `draw_index_in_task` — task payload for draw ID

The task shader copies `uint(gl_DrawID)` and the target width into its payload; the mesh shader uses the copied draw ID to produce the same one-pixel-per-draw reference.

### `primitive_shading_rate_2x2_2x2` — coarse rate on both halves

The first two and last two primitives receive the `2x2` mask. The fragment shader expects the same mask above and below the midpoint.

### `primitive_shading_rate_2x2_2x1` — top `2x2`, bottom `2x1`

The top two primitives receive the combined horizontal/vertical mask and the bottom two receive the horizontal mask.

### `primitive_shading_rate_2x2_1x1` — top `2x2`, bottom `1x1`

The top primitives receive the combined mask and the bottom primitives receive zero.

### `primitive_shading_rate_2x1_2x2` — top `2x1`, bottom `2x2`

The top uses the horizontal mask and the bottom uses the combined mask.

### `primitive_shading_rate_2x1_2x1` — horizontal rate on both halves

Both halves use the horizontal mask.

### `primitive_shading_rate_2x1_1x1` — top `2x1`, bottom `1x1`

The top uses the horizontal mask and the bottom uses zero.

### `primitive_shading_rate_1x1_2x2` — top `1x1`, bottom `2x2`

The top uses zero and the bottom uses the combined mask.

### `primitive_shading_rate_1x1_2x1` — top `1x1`, bottom `2x1`

The top uses zero and the bottom uses the horizontal mask.

### `primitive_shading_rate_1x1_1x1` — native rate on both halves

Both halves use zero, the `1x1` contribution.

## Shader Analysis

The file has two materially different shader-production paths. The first walkthrough uses the generated GLSL position case, which shows the common NV mesh output shape. For this walkthrough, the reconstructed GLSL was compiled with `glslangValidator -V --target-env spirv1.0 -S mesh`, checked with `spirv-val --target-env spv1.0`, and expanded with `spirv-dis`; the full disassembly appears unchanged below. The primitive-ID and primitive-shading-rate cases use direct SPIR-V for special capability/decorations and are covered by the variation summary rather than duplicating large assembly blocks.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.mesh_shader.nv.builtin.position
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `position` | Selects the generator that emits one triangle around pixel `(0,0)` and uses `PixelsInstance`. |
| `8x8`, one mesh workgroup, no task shader | Makes the normalized position constants deterministic and leaves a black background for exact sparse comparison. |

#### Purpose

This shader checks that `gl_Position` written in an NV mesh shader is rasterized at the intended location. The host expects exactly one blue pixel and a black clear color everywhere else.

#### Structural Design

| Phase | Generated behavior |
|-------|--------------------|
| Output declaration | One local invocation emits triangles with three vertices and one primitive. |
| Primitive assembly | `PrimitiveCountNV` is one and `PrimitiveIndicesNV` is `0,1,2`. |
| Position | The generator derives pixel width/height from `8x8`, then emits three coordinates around the top-left pixel center. |
| Fragment | The common fragment shader writes opaque blue. |
| Reference | `PixelsInstance` compares the sparse pixel map against the copied image. |

#### Shader Code

```glsl
#version 460
#extension GL_NV_mesh_shader : enable

layout (local_size_x=1) in;
layout (triangles) out;
layout (max_vertices=3, max_primitives=1) out;

void main ()
{
    /// One mesh invocation emits one triangle covering only the top-left pixel of the 8x8 target.
    gl_PrimitiveCountNV = 1u;

    gl_PrimitiveIndicesNV[0] = 0;
    gl_PrimitiveIndicesNV[1] = 1;
    gl_PrimitiveIndicesNV[2] = 2;

    /// These values are the source generator's 8x8 result: two upper vertices at y=-0.75
    /// and a lower vertex at y=-1.0, with x spanning the first pixel's width.
    gl_MeshVerticesNV[0].gl_Position = vec4(-1.0, -0.75, 0.0, 1.0);
    gl_MeshVerticesNV[1].gl_Position = vec4(-0.75, -0.75, 0.0, 1.0);
    gl_MeshVerticesNV[2].gl_Position = vec4(-0.875, -1.0, 0.0, 1.0);
}
```

#### Additional Info

- The source computes these constants from `getDefaultExtent()` and the center of pixel `(0,0)`; the shown values are the resolved representative case.
- The fragment program is the shared `getBasicFragShader()` path and is not a second behavior axis for this case.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Built-in child | Other children replace the position output with point size, distances, per-primitive metadata, or invocation-derived coordinates | [case generators](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTests.cpp#L959-L1759) |
| Task path | Task variants add a `TaskData` `PerTaskNV` block and read payload values in the mesh shader | [task generators](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTests.cpp#L1393-L1547) |
| Shading-rate pair | The shading-rate cases use direct mesh SPIR-V and vary top/bottom integer masks, not this GLSL position source | [shading-rate generator](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTests.cpp#L1785-L2013) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed GLSL from this walkthrough
- Stage: mesh
- Target SPIRV version: spirv1.0

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 47
; Schema: 0
               OpCapability MeshShadingNV
               OpExtension "SPV_NV_mesh_shader"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint MeshNV %main "main" %gl_PrimitiveCountNV %gl_PrimitiveIndicesNV %gl_MeshVerticesNV
               OpExecutionMode %main LocalSize 1 1 1
               OpExecutionMode %main OutputVertices 3
               OpExecutionMode %main OutputPrimitivesEXT 1
               OpExecutionMode %main OutputTrianglesEXT
               OpSource GLSL 460
               OpSourceExtension "GL_NV_mesh_shader"
               OpName %main "main"
               OpName %gl_PrimitiveCountNV "gl_PrimitiveCountNV"
               OpName %gl_PrimitiveIndicesNV "gl_PrimitiveIndicesNV"
               OpName %gl_MeshPerVertexNV "gl_MeshPerVertexNV"
               OpMemberName %gl_MeshPerVertexNV 0 "gl_Position"
               OpMemberName %gl_MeshPerVertexNV 1 "gl_PointSize"
               OpMemberName %gl_MeshPerVertexNV 2 "gl_ClipDistance"
               OpMemberName %gl_MeshPerVertexNV 3 "gl_CullDistance"
               OpMemberName %gl_MeshPerVertexNV 4 "gl_PositionPerViewNV"
               OpMemberName %gl_MeshPerVertexNV 5 "gl_ClipDistancePerViewNV"
               OpMemberName %gl_MeshPerVertexNV 6 "gl_CullDistancePerViewNV"
               OpName %gl_MeshVerticesNV "gl_MeshVerticesNV"
               OpDecorate %gl_PrimitiveCountNV BuiltIn PrimitiveCountNV
               OpDecorate %gl_PrimitiveIndicesNV BuiltIn PrimitiveIndicesNV
               OpDecorate %gl_MeshPerVertexNV Block
               OpMemberDecorate %gl_MeshPerVertexNV 0 BuiltIn Position
               OpMemberDecorate %gl_MeshPerVertexNV 1 BuiltIn PointSize
               OpMemberDecorate %gl_MeshPerVertexNV 2 BuiltIn ClipDistance
               OpMemberDecorate %gl_MeshPerVertexNV 3 BuiltIn CullDistance
               OpMemberDecorate %gl_MeshPerVertexNV 4 BuiltIn PositionPerViewNV
               OpMemberDecorate %gl_MeshPerVertexNV 4 PerViewNV
               OpMemberDecorate %gl_MeshPerVertexNV 5 BuiltIn ClipDistancePerViewNV
               OpMemberDecorate %gl_MeshPerVertexNV 5 PerViewNV
               OpMemberDecorate %gl_MeshPerVertexNV 6 BuiltIn CullDistancePerViewNV
               OpMemberDecorate %gl_MeshPerVertexNV 6 PerViewNV
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_ptr_Output_uint = OpTypePointer Output %uint
%gl_PrimitiveCountNV = OpVariable %_ptr_Output_uint Output
     %uint_1 = OpConstant %uint 1
     %uint_3 = OpConstant %uint 3
%_arr_uint_uint_3 = OpTypeArray %uint %uint_3
%_ptr_Output__arr_uint_uint_3 = OpTypePointer Output %_arr_uint_uint_3
%gl_PrimitiveIndicesNV = OpVariable %_ptr_Output__arr_uint_uint_3 Output
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
     %uint_0 = OpConstant %uint 0
      %int_1 = OpConstant %int 1
      %int_2 = OpConstant %int 2
     %uint_2 = OpConstant %uint 2
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_arr_float_uint_1 = OpTypeArray %float %uint_1
     %uint_4 = OpConstant %uint 4
%_arr_v4float_uint_4 = OpTypeArray %v4float %uint_4
%_arr__arr_float_uint_1_uint_4 = OpTypeArray %_arr_float_uint_1 %uint_4
%gl_MeshPerVertexNV = OpTypeStruct %v4float %float %_arr_float_uint_1 %_arr_float_uint_1 %_arr_v4float_uint_4 %_arr__arr_float_uint_1_uint_4 %_arr__arr_float_uint_1_uint_4
%_arr_gl_MeshPerVertexNV_uint_3 = OpTypeArray %gl_MeshPerVertexNV %uint_3
%_ptr_Output__arr_gl_MeshPerVertexNV_uint_3 = OpTypePointer Output %_arr_gl_MeshPerVertexNV_uint_3
%gl_MeshVerticesNV = OpVariable %_ptr_Output__arr_gl_MeshPerVertexNV_uint_3 Output
   %float_n1 = OpConstant %float -1
%float_n0_75 = OpConstant %float -0.75
    %float_0 = OpConstant %float 0
    %float_1 = OpConstant %float 1
         %37 = OpConstantComposite %v4float %float_n1 %float_n0_75 %float_0 %float_1
%_ptr_Output_v4float = OpTypePointer Output %v4float
         %40 = OpConstantComposite %v4float %float_n0_75 %float_n0_75 %float_0 %float_1
%float_n0_875 = OpConstant %float -0.875
         %43 = OpConstantComposite %v4float %float_n0_875 %float_n1 %float_0 %float_1
     %v3uint = OpTypeVector %uint 3
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
               OpStore %gl_PrimitiveCountNV %uint_1
         %17 = OpAccessChain %_ptr_Output_uint %gl_PrimitiveIndicesNV %int_0
               OpStore %17 %uint_0
         %19 = OpAccessChain %_ptr_Output_uint %gl_PrimitiveIndicesNV %int_1
               OpStore %19 %uint_1
         %22 = OpAccessChain %_ptr_Output_uint %gl_PrimitiveIndicesNV %int_2
               OpStore %22 %uint_2
         %39 = OpAccessChain %_ptr_Output_v4float %gl_MeshVerticesNV %int_0 %int_0
               OpStore %39 %37
         %41 = OpAccessChain %_ptr_Output_v4float %gl_MeshVerticesNV %int_1 %int_0
               OpStore %41 %40
         %44 = OpAccessChain %_ptr_Output_v4float %gl_MeshVerticesNV %int_2 %int_0
               OpStore %44 %43
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- `MeshShaderBuiltinInstance::iterate` creates the target image, an image view, an empty descriptor-set layout, pipeline layout, render pass, framebuffer, shader modules, and a graphics pipeline. The optional fragment-size state uses `REPLACE` for the first combiner and `KEEP` for the second.
- Most cases issue `cmdDrawMeshTasksNV` with one or more direct commands. The draw-index cases create eight host-visible `VkDrawMeshTasksIndirectCommandNV` records and issue `cmdDrawMeshTasksIndirectNV`, so `gl_DrawID` advances across draws.
- The command buffer clears and renders, transitions the color image from color-attachment to transfer-source layout, copies it into a host-visible buffer, and inserts a transfer-to-host barrier before submission and wait.
- `PixelsInstance` compares every pixel with a sparse map; `QuadrantsInstance` derives the expected color from the half-width/half-height quadrant; `FullScreenColorInstance` compares every pixel in every layer. Any mismatch logs coordinates, expected value, and observed value, and the failing image is logged where implemented.
- A pass is an exact pixel/reference match. A support-time `NotSupportedError` is pruning, not a functional pass or failure.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `position`, `point_size`, `clip_distance`, `cull_distance` | Incorrect mesh output built-in propagation or rasterization behavior; child-specific point-size, clip, or cull feature/limit handling |
| `primitive_id_glsl`, `primitive_id_spirv` | Incorrect per-primitive `PrimitiveId` propagation, or a GLSL-versus-direct-SPIR-V capability/lowering issue |
| `layer`, `layer_shared` | Incorrect layer selection from per-primitive output, or failure to honor the required layer feature and four-layer framebuffer |
| `viewport_index`, `viewport_index_shared` | Incorrect per-primitive viewport selection or viewport-array feature behavior |
| `work_group_id_in_mesh`, `work_group_id_in_task` | Incorrect mesh workgroup identification, task payload transport, or task-to-mesh launch mapping |
| `local_invocation_id_in_mesh`, `local_invocation_id_in_task`, `local_invocation_index_in_mesh`, `local_invocation_index_in_task` | Incorrect local identifier or linear-index value, `WorkgroupSize` handling, or task payload/index mapping |
| `global_invocation_id_in_mesh`, `global_invocation_id_in_task` | Incorrect global identifier calculation across the eight task groups and eight local invocations, or task payload transport |
| `draw_index_in_mesh`, `draw_index_in_task` | Incorrect dynamically uniform `DrawIndex` for repeated indirect draws, or task payload forwarding |
| any `primitive_shading_rate_<top>_<bottom>` child | Incorrect per-primitive shading-rate decoration, mask interpretation, fragment-state combination, or fragment `ShadingRateKHR` observation |

### Cause Analysis

#### Built-in interface or rasterization mismatch

**Possible failure symptoms:** The copied image contains a wrong color, a missing primitive, an extra primitive, or a pixel in the wrong layer, viewport, clip region, or cull region. The exact symptom is reported by the selected pixel verifier.

**Possible implementation causes:** The shader interface decoration, interpolation, primitive assembly, or rasterization implementation may not preserve the NV built-in semantics described by the mesh and interface specification sections. The source does not identify a particular hardware or driver cause; investigation must begin with the failing child and its expected pixel pattern.

#### Task payload or invocation identity mismatch

**Possible failure symptoms:** One-pixel-per-workgroup images contain shifted, duplicated, or missing blue triangles, or the task and mesh variants disagree while the same reference remains expected.

**Possible implementation causes:** The task-to-mesh workgroup launch mapping, `PerTaskNV` payload visibility, or built-in ID calculation may be wrong. The source explicitly writes identity payloads and uses fixed local/workgroup sizes, so a mismatch isolates the interface or built-in path rather than an unspecified input resource.

#### Fragment shading-rate mismatch

**Possible failure symptoms:** A shading-rate child produces black pixels because `gl_ShadingRateEXT` does not equal the top or bottom mask selected from `gl_FragCoord.y`; the host then sees a non-blue pixel.

**Possible implementation causes:** The primitive output decoration, SPIR-V value, pipeline fragment-size combiner, or fragment-stage shading-rate observation may disagree. The implementation deliberately uses direct SPIR-V for the mesh stage and checks the `VK_KHR_fragment_shading_rate` functionality gate, but does not assign a more specific fault location.

#### Host submission or readback mismatch

**Possible failure symptoms:** The verifier observes unexpected clear pixels or stale/incorrect copied data even when shader output is not directly implicated by the coordinates.

**Possible implementation causes:** The draw command selection, image layout transition, transfer copy, host-visible allocation flush/invalidation, or result scan could be at fault. The source includes the required barriers and waits; a failure should be investigated against the exact command path before attributing it to the shader.

## Case Pruning

### Requirement-based pruning

- Every child uses `checkTaskMeshShaderSupportNV`, which requires `VK_NV_mesh_shader` and mesh-shader support; task variants additionally require the task-shader feature.
- `primitive_shading_rate_*` additionally requires `VK_KHR_fragment_shading_rate`.
- `primitive_id_glsl` requires the core Geometry Shader feature because the generated GLSL fragment path uses `gl_PrimitiveID`.
- `layer` and `layer_shared` require `VK_EXT_shader_viewport_index_layer` below Vulkan 1.2, or Vulkan 1.2's `shaderOutputLayer` feature.
- `viewport_index` and `viewport_index_shared` require multi-viewport plus the corresponding viewport-index-layer extension below Vulkan 1.2, or Vulkan 1.2's `shaderOutputViewportIndex` feature.
- `point_size` requires large points and a device point-size range containing `4.0`; clip and cull cases require their respective shader distance features.

These gates mean the implementation cannot legally or meaningfully run the selected case on the current device. A skipped case is not evidence that the built-in failed.

### Design-based pruning

- The first 20 children are fixed registrations; they are not a Cartesian product of every built-in with task, sharing, or render-target choices.
- The shading-rate family intentionally registers the full 3x3 top/bottom product, because the two halves exercise independent per-primitive contributions.
- The shared layer and viewport cases are paired with non-shared cases to cover the per-primitive/per-vertex indexing distinction without multiplying every other child.
- All cases use the smallest geometry and fixed extents needed to make the reference unambiguous. The task and global-ID cases enlarge the one-dimensional workload only when the identifier itself needs multiple values.

## Key Takeaways

- Registration is explicit for the built-in children and generated only for the nine shading-rate pairs; `vk-default` contains exactly 29 NV leaves.
- The task variants test the same conceptual identifiers through a `PerTaskNV` transport path, while mesh variants read the built-in directly.
- Shared layer and viewport cases are important because they test primitive metadata indexing separately from shared vertex output.
- Primitive shading rate is validated at both ends: the mesh writes a per-primitive mask and the fragment shader reads the resulting rate.
- Exact host pixel references make a failure concrete: a mismatch means the selected built-in or the command/interface/rasterization path did not produce the expected observable result; lack of support is pruned separately.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `MeshShaderBuiltinInstance::iterate` | [vktMeshShaderBuiltinTests.cpp#L170-L360](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTests.cpp#L170-L360) | common image, pipeline, submission, transfer, and readback flow |
| `FullScreenColorInstance`, `QuadrantsInstance`, `PixelsInstance` | [vktMeshShaderBuiltinTests.cpp#L387-L549](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTests.cpp#L387-L549) | exact reference and mismatch behavior |
| `PrimitiveIdCase` | [vktMeshShaderBuiltinTests.cpp#L551-L697](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTests.cpp#L551-L697) | GLSL versus direct-SPIR-V primitive-ID paths |
| `LayerCase` and `ViewportIndexCase` | [vktMeshShaderBuiltinTests.cpp#L699-L956](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTests.cpp#L699-L956) | shared/non-shared primitive metadata and feature gates |
| `PositionCase`, `PointSizeCase`, `ClipDistanceCase`, `CullDistanceCase` | [vktMeshShaderBuiltinTests.cpp#L958-L1347](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTests.cpp#L958-L1347) | generated geometry, distances, and limit checks |
| `triangleForPixel`, invocation and draw-index cases | [vktMeshShaderBuiltinTests.cpp#L1349-L1759](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTests.cpp#L1349-L1759) | identifier-to-pixel mapping and task payload generation |
| `PrimitiveShadingRateCase` | [vktMeshShaderBuiltinTests.cpp#L1761-L2037](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTests.cpp#L1761-L2037) | direct SPIR-V, masks, fragment check, and KHR gate |
| `createMeshShaderBuiltinTests` | [vktMeshShaderBuiltinTests.cpp#L2041-L2091](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTests.cpp#L2041-L2091) | complete registration hierarchy and 3x3 loop |
| `checkTaskMeshShaderSupportNV`, shading-rate helpers | [vktMeshShaderUtil.cpp#L34-L124](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L34-L124) | extension, feature, size, and SPIR-V mask helpers |
| NV mesh specification | [VK_NV_mesh_shader/mesh.adoc#mesh](../../../../vulkan-docs/src/chapters/VK_NV_mesh_shader/mesh.adoc#mesh) | task/mesh launch and output primitive rules |
| Built-in specification | [interfaces.adoc#interfaces-builtin-variables](../../../../vulkan-docs/src/chapters/interfaces.adoc#interfaces-builtin-variables) | identifier, layer, distance, primitive ID, and shading-rate semantics |
| `vk-default` coverage | [vk-default/mesh-shader.txt#L541-L577](../../../mustpass/main/vk-default/mesh-shader.txt#L541-L577) | exact 29 registered NV leaves |
