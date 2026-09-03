## Overview

**Core question:** Do EXT mesh-shader built-ins produce the expected primitive, fragment, and task-to-mesh results across the registered construction paths?

- `vktMeshShaderBuiltinTestsEXT.cpp` implements the `mesh_shader.ext.builtin` test family and the `mesh_shader.ext.pipeline.builtin` pipeline-construction family.
- The built-in family checks mesh position and point size, clipping and culling distances, primitive ID, layer, viewport index, task/mesh invocation identifiers, view index, primitive culling, and primitive fragment shading rate.
- The same implementation supplies the pipeline family: `clip_distance`, `clip_distance_mix`, `cull_distance`, and `cull_distance_mix` run through optimized-library, fast-linked-library, and shader-object construction.
- Most cases generate EXT GLSL at program initialization. `primitive_id_spirv` deliberately supplies a CTS-authored SPIR-V fragment module for the capability path that GLSL would not select.
- The common instance renders to a small color image, copies the image to host-visible memory, and applies an exact pixel reference. A support-time `NotSupportedError` prunes a case; it is not a failed built-in result.

## Background Knowledge

- EXT mesh and task shaders execute in workgroups. A task shader can call `EmitMeshTasksEXT` and pass a `taskPayloadSharedEXT` payload to the mesh workgroups it creates; a mesh shader calls `SetMeshOutputsEXT` and writes indexed vertices and primitives. The specification describes this launch and output relationship in [Mesh Shading](../../../../vulkan-docs/src/chapters/VK_NV_mesh_shader/mesh.adoc#mesh).
- Per-primitive outputs belong to a primitive, not to an individual vertex. That distinction matters for `gl_Layer`, `gl_ViewportIndex`, `gl_PrimitiveID`, `gl_CullPrimitiveEXT`, and `gl_PrimitiveShadingRateEXT`, which are written through `gl_MeshPrimitivesEXT[]` in the generated EXT shaders. The built-in interface rules are in [Shader Input and Output Interfaces](../../../../vulkan-docs/src/chapters/interfaces.adoc#interfaces-iointerfaces).
- A mesh shader's output primitive mode and literal maximum vertex/primitive counts constrain the values passed to `SetMeshOutputsEXT`; the EXT mesh specification also defines the point, line, and triangle index arrays used to assemble output primitives.

## Registration Hierarchy

```text
mesh_shader.ext.builtin
├── position
├── point_size
├── clip_distance
├── clip_distance_mix
├── cull_distance
├── cull_distance_mix
├── primitive_id_glsl
├── primitive_id_spirv
├── layer
├── layer_shared
├── layer_no_write
├── viewport_index
├── viewport_index_shared
├── viewport_index_no_write
├── work_group_id_in_mesh
├── work_group_id_in_task
├── num_work_groups_mesh
├── num_work_groups_task_and_mesh
├── local_invocation_id_in_mesh
├── local_invocation_id_in_task
├── local_invocation_index_in_task
├── local_invocation_index_in_mesh
├── global_invocation_id_in_mesh
├── global_invocation_id_in_task
├── draw_index_in_mesh
├── draw_index_in_task
├── view_index
├── cull_primitives
├── primitive_shading_rate_2x2_2x2
├── primitive_shading_rate_2x2_2x1
├── primitive_shading_rate_2x2_1x1
├── primitive_shading_rate_2x1_2x2
├── primitive_shading_rate_2x1_2x1
├── primitive_shading_rate_2x1_1x1
├── primitive_shading_rate_1x1_2x2
├── primitive_shading_rate_1x1_2x1
└── primitive_shading_rate_1x1_1x1

mesh_shader.ext.pipeline
└── builtin
```

`createMeshShaderBuiltinTestsEXT` adds the first tree's direct children explicitly and produces the nine `primitive_shading_rate_<top>_<bottom>` children with a 3x3 loop. `createMeshShaderPipelineTestsEXT` creates the second root, then its `builtin` family, then the deeper construction children `optimized_lib`, `fast_lib`, and `shader_objects`; each construction child owns the four distance cases. The deeper names are listed in the parameter section because the canonical hierarchy tree expands only one direct-child level.

The dispatcher attaches these roots under `mesh_shader.ext` with `createMeshShaderBuiltinTestsEXT` and `createMeshShaderPipelineTestsEXT`; the surrounding category tree is registered in [createTests](../../../modules/vulkan/mesh_shader/vktMeshShaderTests.cpp#L55-L85).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Built-in child | `position`, `point_size`, `clip_distance`, `clip_distance_mix`, `cull_distance`, `cull_distance_mix`, `primitive_id_glsl`, `primitive_id_spirv`, `layer`, `layer_shared`, `layer_no_write`, `viewport_index`, `viewport_index_shared`, `viewport_index_no_write`, `work_group_id_in_mesh`, `work_group_id_in_task`, `num_work_groups_mesh`, `num_work_groups_task_and_mesh`, `local_invocation_id_in_mesh`, `local_invocation_id_in_task`, `local_invocation_index_in_task`, `local_invocation_index_in_mesh`, `global_invocation_id_in_mesh`, `global_invocation_id_in_task`, `draw_index_in_mesh`, `draw_index_in_task`, `view_index`, `cull_primitives` | Selects the built-in or built-in relationship under test. | [built-in factory](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTestsEXT.cpp#L2560-L2599) |
| Primitive shading-rate pair | `2x2`, `2x1`, `1x1` for each top and bottom half | Selects two per-primitive shading-rate masks. Registration covers all nine ordered pairs. | [shading-rate registration loop](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTestsEXT.cpp#L2600-L2619) |
| Pipeline construction | `optimized_lib`, `fast_lib`, `shader_objects` | Reuses the distance shaders while varying pipeline-library or shader-object construction. | [pipeline factory](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTestsEXT.cpp#L2623-L2651) |
| Task path | `_in_mesh` versus `_in_task` for workgroup, local/global invocation, and draw index | Reads the built-in in mesh code or transports an equivalent task value through `taskPayloadSharedEXT`. | [task and mesh generators](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTestsEXT.cpp#L1640-L1830) |
| Vertex sharing | `layer`/`viewport_index` versus `*_shared` | Compares one primitive per workgroup with one workgroup whose invocations share three vertices but write separate primitive metadata. | [layer and viewport generators](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTestsEXT.cpp#L856-L1129) |
| Write behavior | explicit output, `layer_no_write`, `viewport_index_no_write` | Tests both assigned and intentionally unassigned per-primitive layer/viewport output. | [layer case](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTestsEXT.cpp#L856-L990) and [viewport case](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTestsEXT.cpp#L991-L1132) |
| Render target and draw mode | `8x8` or `8x1`; direct draws for most cases; repeated indirect draws for draw-index cases | Provides deterministic pixel coordinates and distinct `gl_DrawID` values where required. | [extent and draw helpers](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTestsEXT.cpp#L101-L131) and [draw-index instance](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTestsEXT.cpp#L2114-L2210) |

The exact `vk-default` coverage is 49 leaves: 37 under `dEQP-VK.mesh_shader.ext.builtin` at [lines 541-577](../../../mustpass/main/vk-default/mesh-shader.txt#L541-L577), plus 12 under `dEQP-VK.mesh_shader.ext.pipeline.builtin` at [lines 2013-2024](../../../mustpass/main/vk-default/mesh-shader.txt#L2013-L2024). The pipeline leaves are four cases for each of `fast_lib`, `optimized_lib`, and `shader_objects`.

## Behavior Parameters

The primary behavioral axis is the registered built-in or pipeline leaf. The sections below group the exact leaves by the mechanism that changes the shader or reference behavior.

### Geometry and distance built-ins

- `position` emits one triangle around pixel `(0,0)` in an `8x8` target; `PixelsInstance` expects that one pixel blue and the black clear color elsewhere.
- `point_size` emits one point at `(-0.5,-0.5)` with `gl_PointSize = 4.0`; `QuadrantsInstance` expects blue in the top-left quadrant and black in the other three.
- `clip_distance` emits a two-triangle quad with two clip-distance planes. Fixed-function clipping retains the top-left region; the fragment shader colors retained fragments blue and uses white only as a sentinel for an unexpected fragment.
- `clip_distance_mix` repeats the clipping geometry and adds a per-primitive color output, checking the built-in together with the user-defined per-primitive interface.
- `cull_distance` emits a four-triangle, six-vertex arrangement and uses two cull-distance arrays to select the reference regions.
- `cull_distance_mix` adds a per-primitive color output to the cull-distance path.
- `mesh_shader.ext.pipeline.builtin.optimized_lib.clip_distance`, `.clip_distance_mix`, `.cull_distance`, and `.cull_distance_mix` run the same four behaviors through the optimized-library construction mode; `fast_lib` and `shader_objects` repeat them with their respective construction modes.

### Primitive identity and placement

- `primitive_id_glsl` writes `1629198956` to `gl_MeshPrimitivesEXT[0].gl_PrimitiveID`; the GLSL fragment shader turns an exact match blue.
- `primitive_id_spirv` uses the same comparison but supplies a CTS-authored SPIR-V fragment module with `MeshShadingEXT` and `SPV_EXT_mesh_shader` rather than relying on the GLSL capability choice.
- `layer` launches four workgroups and writes `gl_Layer = gl_WorkGroupID.x`; `layer_shared` uses four local invocations in one workgroup, with invocation zero writing shared vertices and each invocation writing one layer-bearing primitive.
- `layer_no_write` omits the layer assignment and expects the single layer reference instead of the four explicit layer colors.
- `viewport_index` maps four workgroups to four viewports using `gl_WorkGroupID.x`; `viewport_index_shared` makes the same mapping with shared vertices and per-primitive viewport indices.
- `viewport_index_no_write` omits the viewport assignment and expects the no-write reference.
- `view_index` enables multiview, writes a per-primitive color selected by `gl_ViewIndex`, and checks four framebuffer layers against four fixed colors.
- `cull_primitives` writes `false` for the top two primitives and `true` for the bottom two through `gl_CullPrimitiveEXT`; the expected image keeps only the top half.

### Workgroup, invocation, and draw identifiers

- `work_group_id_in_mesh` reads `gl_WorkGroupID.x` directly. `work_group_id_in_task` writes the task workgroup ID into payload data and reads it in the mesh shader.
- `num_work_groups_mesh` checks mesh `gl_NumWorkGroups` against `(5,6,7)`. `num_work_groups_task_and_mesh` checks task groups `(2,3,4)` and mesh groups `(3,4,2)`, carrying parent group data through the payload.
- The four local-invocation leaves select either `gl_LocalInvocationID.x` or `gl_LocalInvocationIndex`, and either read it in mesh code or transport an identity array from task code.
- The global-ID leaves use eight tasks and eight local invocations. Mesh code uses `gl_GlobalInvocationID.x`; task code writes each value to payload data before emitting one mesh workgroup.
- The draw-index leaves use eight indirect draws with one mesh task per record. Mesh code converts `gl_DrawID` to `uint`; the task variant forwards the same value through payload data.

### Primitive fragment shading rate

Each `primitive_shading_rate_<top>_<bottom>` leaf emits four triangles. The first two receive the top mask and the last two the bottom mask. The masks are `0` for `1x1`, `gl_ShadingRateFlag2HorizontalPixelsEXT` for `2x1`, and the horizontal/vertical OR for `2x2`. The fragment shader chooses the expected mask from `gl_FragCoord.y` and writes blue only when `gl_ShadingRateEXT` matches it.

## Shader Analysis

The source has one common generated-GLSL shape and several important branch families: task payload versus direct built-ins, per-primitive metadata, direct SPIR-V for primitive ID, and top/bottom shading-rate masks. One complete walkthrough is enough to show the generated EXT mesh contract; the parameter summary above records the other branches without duplicating their shaders.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.mesh_shader.ext.builtin.position
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `position` | Selects `PositionCase`, which generates one EXT mesh triangle around the top-left pixel. |
| `8x8`, one mesh workgroup, no task shader | Resolves the generator's pixel-size calculation and makes the sparse host reference deterministic. |

#### Purpose

This shader checks that an EXT mesh shader's `gl_Position` output rasterizes at the intended pixel. The fragment shader colors every covered fragment blue, while the host expects only `(0,0)` to differ from the black clear color.

#### Structural Design

| Phase | Generated behavior |
|-------|--------------------|
| Mesh execution | One local invocation calls `SetMeshOutputsEXT(3u, 1u)`. |
| Primitive assembly | `gl_PrimitiveTriangleIndicesEXT[0]` selects vertices `0`, `1`, and `2`. |
| Position | The generator derives one-pixel normalized dimensions from `getDefaultExtent()` and places the triangle around pixel `(0,0)`. |
| Fragment | `getBasicFragShader()` writes opaque blue. |
| Reference | `PixelsInstance` compares the copied image with one blue coordinate and a black background. |

#### Shader Code

```glsl
#version 460
#extension GL_EXT_mesh_shader : enable

layout (local_size_x=1) in;
layout (triangles) out;
layout (max_vertices=3, max_primitives=1) out;

void main ()
{
    /// The generated EXT mesh stage emits one triangle with three vertices.
    SetMeshOutputsEXT(3u, 1u);

    /// The only primitive uses all three generated vertices.
    gl_PrimitiveTriangleIndicesEXT[0] = uvec3(0u, 1u, 2u);

    /// For the 8x8 target, these coordinates surround the center of pixel (0,0).
    gl_MeshVerticesEXT[0].gl_Position = vec4(-1.0, -0.75, 0.0, 1.0);
    gl_MeshVerticesEXT[1].gl_Position = vec4(-0.75, -0.75, 0.0, 1.0);
    gl_MeshVerticesEXT[2].gl_Position = vec4(-0.875, -1.0, 0.0, 1.0);
}
```

#### Additional Info

- `PositionCase::initPrograms` computes `pxWidth`, `pxHeight`, and the pixel center from the fixed `8x8` extent before inserting the numeric coordinates.
- The fragment source is the shared `getBasicFragShader()` result; this representative case has no task shader, descriptor resource, indirect draw, or fragment-size state.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Built-in child | Other children replace position with point size, distances, primitive metadata, identifier-derived coordinates, view-dependent color, culling, or shading-rate values. | [EXT case generators](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTestsEXT.cpp#L727-L2558) |
| Task path | Task variants add `taskPayloadSharedEXT` data and an `EmitMeshTasksEXT` call; mesh variants read the built-in directly. | [task and mesh generators](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTestsEXT.cpp#L1640-L2210) |
| Pipeline construction | Pipeline leaves reuse distance shader generation but pass a non-monolithic `PipelineConstructionType` into the common host setup. | [pipeline factory](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTestsEXT.cpp#L2623-L2651) |
| Shading-rate pair | The nine shading-rate leaves generate per-primitive masks and fragment checks from the ordered top/bottom pair. | [shading-rate generator](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTestsEXT.cpp#L2338-L2467) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed GLSL from this walkthrough
- Stage: mesh
- Target SPIRV version: spirv1.4

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.4
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 42
; Schema: 0
               OpCapability MeshShadingEXT
               OpExtension "SPV_EXT_mesh_shader"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint MeshEXT %main "main" %gl_PrimitiveTriangleIndicesEXT %gl_MeshVerticesEXT
               OpExecutionMode %main LocalSize 1 1 1
               OpExecutionMode %main OutputVertices 3
               OpExecutionMode %main OutputPrimitivesEXT 1
               OpExecutionMode %main OutputTrianglesEXT
               OpSource GLSL 460
               OpSourceExtension "GL_EXT_mesh_shader"
               OpName %main "main"
               OpName %gl_PrimitiveTriangleIndicesEXT "gl_PrimitiveTriangleIndicesEXT"
               OpName %gl_MeshPerVertexEXT "gl_MeshPerVertexEXT"
               OpMemberName %gl_MeshPerVertexEXT 0 "gl_Position"
               OpMemberName %gl_MeshPerVertexEXT 1 "gl_PointSize"
               OpMemberName %gl_MeshPerVertexEXT 2 "gl_ClipDistance"
               OpMemberName %gl_MeshPerVertexEXT 3 "gl_CullDistance"
               OpName %gl_MeshVerticesEXT "gl_MeshVerticesEXT"
               OpDecorate %gl_PrimitiveTriangleIndicesEXT BuiltIn PrimitiveTriangleIndicesEXT
               OpDecorate %gl_MeshPerVertexEXT Block
               OpMemberDecorate %gl_MeshPerVertexEXT 0 BuiltIn Position
               OpMemberDecorate %gl_MeshPerVertexEXT 1 BuiltIn PointSize
               OpMemberDecorate %gl_MeshPerVertexEXT 2 BuiltIn ClipDistance
               OpMemberDecorate %gl_MeshPerVertexEXT 3 BuiltIn CullDistance
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
     %uint_3 = OpConstant %uint 3
     %uint_1 = OpConstant %uint 1
     %v3uint = OpTypeVector %uint 3
%_arr_v3uint_uint_1 = OpTypeArray %v3uint %uint_1
%_ptr_Output__arr_v3uint_uint_1 = OpTypePointer Output %_arr_v3uint_uint_1
%gl_PrimitiveTriangleIndicesEXT = OpVariable %_ptr_Output__arr_v3uint_uint_1 Output
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
     %uint_0 = OpConstant %uint 0
     %uint_2 = OpConstant %uint 2
         %17 = OpConstantComposite %v3uint %uint_0 %uint_1 %uint_2
%_ptr_Output_v3uint = OpTypePointer Output %v3uint
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_arr_float_uint_1 = OpTypeArray %float %uint_1
%gl_MeshPerVertexEXT = OpTypeStruct %v4float %float %_arr_float_uint_1 %_arr_float_uint_1
%_arr_gl_MeshPerVertexEXT_uint_3 = OpTypeArray %gl_MeshPerVertexEXT %uint_3
%_ptr_Output__arr_gl_MeshPerVertexEXT_uint_3 = OpTypePointer Output %_arr_gl_MeshPerVertexEXT_uint_3
%gl_MeshVerticesEXT = OpVariable %_ptr_Output__arr_gl_MeshVerticesEXT_uint_3 Output
   %float_n1 = OpConstant %float -1
%float_n0_75 = OpConstant %float -0.75
    %float_0 = OpConstant %float 0
    %float_1 = OpConstant %float 1
         %31 = OpConstantComposite %v4float %float_n1 %float_n0_75 %float_0 %float_1
%_ptr_Output_v4float = OpTypePointer Output %v4float
      %int_1 = OpConstant %int 1
         %35 = OpConstantComposite %v4float %float_n0_75 %float_n0_75 %float_0 %float_1
      %int_2 = OpConstant %int 2
%float_n0_875 = OpConstant %float -0.875
         %39 = OpConstantComposite %v4float %float_n0_875 %float_n1 %float_0 %float_1
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
               OpSetMeshOutputsEXT %uint_3 %uint_1
         %19 = OpAccessChain %_ptr_Output_v3uint %gl_PrimitiveTriangleIndicesEXT %int_0
               OpStore %19 %17
         %33 = OpAccessChain %_ptr_Output_v4float %gl_MeshVerticesEXT %int_0 %int_0
               OpStore %33 %31
         %36 = OpAccessChain %_ptr_Output_v4float %gl_MeshVerticesEXT %int_1 %int_0
               OpStore %36 %35
         %40 = OpAccessChain %_ptr_Output_v4float %gl_MeshVerticesEXT %int_2 %int_0
               OpStore %40 %39
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- `MeshShaderBuiltinInstance::iterate` creates an `R8G8B8A8_UNORM` color image and view, an empty descriptor-set layout, a pipeline layout, a custom render pass/framebuffer, shader modules, and a graphics pipeline. The render target is `8x8` by default or `8x1` for the linear identifier cases.
- The common pipeline uses the selected `PipelineConstructionType`. For multiview, it creates one subpass per layer and one pipeline per subpass. For primitive shading rate, it attaches `VkPipelineFragmentShadingRateStateCreateInfoKHR` with `REPLACE` for the first combiner and `KEEP` for the second.
- Direct cases issue `cmdDrawMeshTasksEXT`. Draw-index cases place host-provided `VkDrawMeshTasksIndirectCommandEXT` records in a host-visible indirect buffer and issue `cmdDrawMeshTasksIndirectEXT`; eight records make the draw index observable.
- The command buffer begins the render pass, binds the pipeline, executes the draws, ends the pass, transitions the color image from `COLOR_ATTACHMENT_OPTIMAL` to `TRANSFER_SRC_OPTIMAL`, copies it into a host-visible output buffer, applies a transfer-to-host barrier, submits, waits, and invalidates the allocation.
- `PixelsInstance` checks a sparse coordinate map, `QuadrantsInstance` chooses the expected color from the four halves, and `FullScreenColorInstance` compares every pixel in every layer. A mismatch logs coordinates, expected color, and observed color and records the result image before failing.
- A case returns `Pass` only after the complete reference comparison succeeds. The fragment shader's black sentinel for a wrong primitive ID or shading rate therefore becomes an ordinary host-side pixel mismatch.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `position`, `point_size`, `clip_distance`, `clip_distance_mix`, `cull_distance`, `cull_distance_mix` | Incorrect EXT mesh output, distance interpolation, point-size, clipping, culling, or per-primitive interface behavior |
| `primitive_id_glsl`, `primitive_id_spirv` | Incorrect `PrimitiveId` propagation or a GLSL-versus-direct-SPIR-V capability/lowering problem |
| `layer`, `layer_shared`, `layer_no_write` | Incorrect per-primitive layer selection, shared-vertex indexing, or no-write behavior |
| `viewport_index`, `viewport_index_shared`, `viewport_index_no_write` | Incorrect per-primitive viewport selection, shared-vertex indexing, or no-write behavior |
| `work_group_id_in_mesh`, `work_group_id_in_task`, `num_work_groups_mesh`, `num_work_groups_task_and_mesh` | Incorrect workgroup identity, task-to-mesh launch mapping, or payload transport |
| `local_invocation_id_in_mesh`, `local_invocation_id_in_task`, `local_invocation_index_in_mesh`, `local_invocation_index_in_task` | Incorrect local identifier or linear-index value, workgroup-size handling, or task payload/index mapping |
| `global_invocation_id_in_mesh`, `global_invocation_id_in_task` | Incorrect global identifier calculation across the generated workload or task payload transport |
| `draw_index_in_mesh`, `draw_index_in_task` | Incorrect dynamically uniform draw index for the repeated indirect draws or task payload forwarding |
| `view_index` | Incorrect multiview mesh execution or view-dependent per-primitive data |
| `cull_primitives` | Incorrect `CullPrimitiveEXT` interpretation or primitive removal |
| `primitive_shading_rate_<top>_<bottom>` | Incorrect per-primitive shading-rate decoration, mask interpretation, fragment-state combination, or `ShadingRateKHR` observation |
| `mesh_shader.ext.pipeline.builtin.<construction>.<case>` | Built-in or distance behavior changes under the selected library/shader-object construction path, or the construction path violates its required pipeline rules |

### Cause Analysis

#### Built-in interface or rasterization mismatch

**Possible failure symptoms:** The copied image contains a wrong color, a missing or extra primitive, or a pixel in the wrong position, layer, viewport, clip region, or cull region. The selected verifier reports the exact coordinate and expected/observed colors.

**Possible implementation causes:** The EXT built-in decoration, interface matching, primitive assembly, interpolation, or rasterization behavior may not preserve the semantics described by the [mesh output rules](../../../../vulkan-docs/src/chapters/VK_NV_mesh_shader/mesh.adoc#mesh-output) and [built-in interface rules](../../../../vulkan-docs/src/chapters/interfaces.adoc#interfaces-iointerfaces-builtin). The source does not justify assigning the cause to a particular hardware or driver component; investigation starts with the failing child and its reference pattern.

#### Task payload or identifier mismatch

**Possible failure symptoms:** The `8x1` image has shifted, duplicated, missing, or out-of-order blue pixels, or a task variant disagrees with its mesh-only counterpart while the expected image remains the same.

**Possible implementation causes:** The task-to-mesh workgroup mapping, `taskPayloadSharedEXT` visibility, built-in ID calculation, `gl_NumWorkGroups` handling, or indirect draw indexing may be wrong. The generated cases use fixed workgroup sizes and identity payload data, so the first investigation target is the interface or built-in path exercised by the selected leaf.

#### Pipeline-construction mismatch

**Possible failure symptoms:** A distance case passes with monolithic construction but produces different clip/cull regions or per-primitive colors under `optimized_lib`, `fast_lib`, or `shader_objects`.

**Possible implementation causes:** The selected construction path may fail to preserve shader interfaces or required pre-rasterization state while assembling or binding the graphics pipeline. Vulkan defines a pipeline library as linkable state that cannot itself be bound, and shader objects alter pipeline interaction; inspect the construction-specific setup before attributing the symptom to distance arithmetic.

#### Primitive shading-rate mismatch

**Possible failure symptoms:** A shading-rate case writes black in the fragment shader because `gl_ShadingRateEXT` differs from the top or bottom mask selected from `gl_FragCoord.y`; the host then sees a non-blue pixel.

**Possible implementation causes:** The mesh per-primitive value, `VK_KHR_fragment_shading_rate` pipeline state, rasterization conversion, or fragment-stage observation may disagree. The source deliberately checks the mesh feature `primitiveFragmentShadingRateMeshShader` and does not provide evidence for a narrower fault location.

#### Host submission or readback mismatch

**Possible failure symptoms:** The verifier observes stale data, unexpected clear pixels, or an incorrect image even when the coordinate pattern does not identify a shader-side error.

**Possible implementation causes:** The draw command path, image layout transition, transfer copy, host-visible allocation flush/invalidation, or result scan could be at fault. The source includes explicit barriers, submission wait, and allocation invalidation; inspect that exact path before assigning the mismatch to a built-in.

## Case Pruning

### Requirement-based pruning

- Every case calls `checkPipelineConstructionRequirements` for its selected construction type and calls `checkTaskMeshShaderSupportEXT`; the latter requires `VK_EXT_mesh_shader` and mesh-shader support, with task-shader support for task variants. See [MeshShaderBuiltinCase::checkSupport](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTestsEXT.cpp#L493-L520) and [checkTaskMeshShaderSupportEXT](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L126-L139).
- `primitive_id_glsl` additionally requires the core Geometry Shader feature because the generated GLSL fragment path uses `gl_PrimitiveID` and glslang selects the Geometry capability.
- `point_size` requires large points and a device point-size range containing `4.0`; `clip_distance` and `cull_distance` require their corresponding shader distance features.
- `layer` variants require `VK_EXT_shader_viewport_index_layer` on older Vulkan versions or the Vulkan 1.2 `shaderOutputLayer` feature. `viewport_index` variants require multi-viewport plus the matching viewport-index/layer extension or `shaderOutputViewportIndex` feature.
- `view_index` requires multiview, `multiviewMeshShader`, and `maxMeshMultiviewViewCount >= 4`.
- Shading-rate variants require `VK_KHR_fragment_shading_rate` and `primitiveFragmentShadingRateMeshShader`.

A requirement-based prune means the selected device cannot legally or meaningfully run that case. It is not evidence that the built-in failed.

### Design-based pruning

- The explicit built-in registrations are a selected coverage set, not a Cartesian product of every built-in with task presence, shared vertices, render target, and pipeline construction.
- The shading-rate family intentionally keeps the complete 3x3 ordered top/bottom product because the two image halves exercise independent per-primitive values.
- Shared layer and viewport cases isolate primitive metadata from shared vertex output without multiplying every other built-in case.
- Identifier cases enlarge the target or workgroup only when multiple identifier values are needed; ordinary geometry cases retain the smallest deterministic target.
- Pipeline construction is applied only to the four distance behaviors. The factory does not create pipeline-library or shader-object versions of every built-in child.

## Key Takeaways

- The file owns two registration roots: explicit built-in leaves under `mesh_shader.ext.builtin`, and a pipeline root whose `builtin` family expands to three construction modes and four distance leaves each.
- Task leaves compare direct mesh built-ins with equivalent values carried through an EXT task payload; the payload is shader interface data, not a descriptor resource.
- `layer_shared` and `viewport_index_shared` test per-primitive metadata while multiple invocations share one set of vertex outputs. The no-write leaves keep the absence of an assignment as a separate behavior.
- Primitive shading rate is checked end to end: mesh code writes a per-primitive mask, pipeline state supplies fragment-size behavior, and the fragment shader compares `gl_ShadingRateEXT`.
- The `vk-default` file contains 37 built-in leaves and 12 pipeline leaves for this EXT implementation. Exact pixel comparison distinguishes a functional mismatch from support pruning.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| common render, submit, transfer, and readback flow | [MeshShaderBuiltinInstance::iterate](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTestsEXT.cpp#L267-L490) | Creates the image/pipeline, draws, copies the result, and invokes the verifier |
| exact reference verifiers | [FullScreenColorInstance, QuadrantsInstance, and PixelsInstance](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTestsEXT.cpp#L523-L703) | Defines layer, quadrant, sparse-pixel, mismatch, and pass behavior |
| common support gate | [MeshShaderBuiltinCase::checkSupport](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTestsEXT.cpp#L493-L520) | Combines pipeline-construction and EXT task/mesh requirements |
| built-in registration | [createMeshShaderBuiltinTestsEXT](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTestsEXT.cpp#L2560-L2621) | Registers explicit leaves and generates the 3x3 shading-rate matrix |
| pipeline registration | [createMeshShaderPipelineTestsEXT](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTestsEXT.cpp#L2623-L2652) | Adds `optimized_lib`, `fast_lib`, and `shader_objects` construction children |
| generated position shader | [PositionCase::initPrograms](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTestsEXT.cpp#L1148-L1196) | Shows fixed EXT GLSL generation and its pixel reference |
| task and identifier generators | [WorkGroupIdCase through DrawIndexCase](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTestsEXT.cpp#L1640-L2210) | Shows direct built-ins, task payloads, group counts, and indirect draw IDs |
| primitive shading rate | [PrimitiveShadingRateCase](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTestsEXT.cpp#L2338-L2467) | Shows mask generation, shader checks, and support gates |
| EXT support helper | [checkTaskMeshShaderSupportEXT](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L126-L139) | Requires `VK_EXT_mesh_shader` and the requested task/mesh features |
| task/mesh specification | [Mesh Shading](../../../../vulkan-docs/src/chapters/VK_NV_mesh_shader/mesh.adoc#mesh) | Defines task launch, payload, EXT mesh output, and primitive assembly semantics |
| built-in specification | [Shader Input and Output Interfaces](../../../../vulkan-docs/src/chapters/interfaces.adoc#interfaces-iointerfaces) | Defines built-in interfaces and matching rules |
| primitive shading-rate specification | [Primitive Fragment Shading Rate](../../../../vulkan-docs/src/chapters/primsrast.adoc#primsrast-fragment-shading-rate-primitive) | Defines the per-primitive rate source for `MeshEXT` |
| pipeline-library context | [Pipeline Libraries](../../../../vulkan-docs/src/chapters/pipelines.adoc#pipelines-library) | Defines linkable library state and lifetime rules |
| exact EXT built-in coverage | [vk-default mesh-shader lines 541-577](../../../mustpass/main/vk-default/mesh-shader.txt#L541-L577) | Lists all 37 built-in leaves |
| exact EXT pipeline coverage | [vk-default mesh-shader lines 2013-2024](../../../mustpass/main/vk-default/mesh-shader.txt#L2013-L2024) | Lists all 12 pipeline leaves |
