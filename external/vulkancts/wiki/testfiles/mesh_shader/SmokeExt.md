## Overview

**Core question:** Can the EXT mesh-shader smoke paths produce the expected color or depth result under each registered construction method?

- This page covers `vktMeshShaderSmokeTestsEXT.cpp`, which registers `mesh_shader.ext.smoke`.
- The factory combines four construction groups with mesh-only, task-to-mesh, partial-output, gradient, shared-fragment, and depth-only cases.
- The cases exercise monolithic pipelines, graphics pipeline libraries, and shader objects while checking real rendered attachments.
- The default `vk-default` mustpass contains 67 leaves: 13 under `monolithic`, 21 under `optimized_lib`, 21 under `fast_lib`, and 12 under `shader_objects`.

## Background Knowledge

- A mesh shader explicitly sets its output vertex and primitive counts, writes mesh vertex and primitive-index built-ins, and supplies the geometry that the rasterizer consumes. It replaces the ordinary input-assembly and vertex-shader path.
- An optional task shader runs before the mesh shader and calls `EmitMeshTasksEXT` to launch mesh workgroups. A task shader that emits zero workgroups leaves its mesh shader unused.
- Graphics pipeline libraries assemble reusable pieces of graphics pipeline state, while shader objects represent independently bindable shader stages. These construction modes change how state is created and bound, but not the expected image.

## Registration Hierarchy

```text
mesh_shader.ext.smoke
├── monolithic
├── optimized_lib
├── fast_lib
└── shader_objects
```

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Pipeline construction | `monolithic`, `optimized_lib`, `fast_lib`, `shader_objects` | Selects the pipeline, graphics-pipeline-library, or shader-object setup used by the case. | [createMeshShaderSmokeTestsEXT](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTestsEXT.cpp#L2547-L2635) |
| Triangle and task path | `mesh_shader_triangle`, `mesh_shader_triangle_rasterization_disabled`, `mesh_task_shader_triangle`, `task_only_shader_triangle` | Covers direct mesh output, discard, task payload and launch, and a task that emits no mesh workgroups. | [triangle registrations](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTestsEXT.cpp#L2568-L2574) |
| Partial output | `partial_usage`, `partial_usage_without_compaction` | Changes whether unused vertices precede the used vertices in a variable-sized mesh output. | [partial registration](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTestsEXT.cpp#L2576-L2583) |
| Gradient shading rate | `fullscreen_gradient`, `fullscreen_gradient_fs2x1`, `fullscreen_gradient_fs2x2` | Selects the default 1x1 path or a per-primitive fragment shading rate. | [gradient registrations](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTestsEXT.cpp#L2585-L2593) |
| Shared fragment path | `shared_frag_library*`, `shared_frag_shader*` | Varies `gl_Layer` versus `gl_PrimitiveID`, draw order, and an extra fragment input across library and shader-object paths. | [shared registrations](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTestsEXT.cpp#L2596-L2610) |
| Depth geometry and position assignment | `depth_only_points`, `depth_only_triangles`, with optional `_position_components` | Selects point or triangle output and whole-vector versus component-by-component `gl_Position` writes. | [depth registrations](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTestsEXT.cpp#L2613-L2628) |

## Behavior Parameters

The primary behavioral axis is the registered test-case leaf. The construction group is a cross-cutting setup dimension; the leaves change the shader stages, generated output, or result check.

### Triangle and task leaves: basic output and launch behavior

`mesh_shader_triangle` emits one blue triangle from mesh shader workgroup output. `mesh_shader_triangle_rasterization_disabled` uses the same mesh path but omits the fragment shader, so no fragment output reaches the attachment and the clear color must remain. `mesh_task_shader_triangle` passes a triangle index through `taskPayloadSharedEXT`, emits one mesh workgroup per task, and renders two triangles. `task_only_shader_triangle` calls `EmitMeshTasksEXT(0u, 0u, 0u)`, so the paired mesh shader must not run and the attachment must remain clear. The builders and host checks are in [the triangle cases](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTestsEXT.cpp#L222-L634).

### Partial output leaves: used and unused mesh outputs

`partial_usage` emits selected front triangles and a full-screen background triangle using buffer data, per-primitive data, and push constants. `partial_usage_without_compaction` reserves 64 extra vertices before the used vertices. Both paths test `SetMeshOutputsEXT` with counts that depend on the workgroup's remaining triangle count. The host reference starts with a red and blue background, then replaces selected pixels with deterministic per-primitive blue values. See [PartialUsageCase](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTestsEXT.cpp#L999-L1545).

### Gradient leaves: interpolation and fragment shading rate

`fullscreen_gradient` uses the default 1x1 fragment size. The `fs2x1` and `fs2x2` leaves write a per-primitive shading-rate value and check the resulting 2x1 or 2x2 blocks. The mesh shader emits a fullscreen quad as two triangles and assigns colors that encode the pixel coordinates, making interpolation and block behavior visible. See [gradient generation and checking](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTestsEXT.cpp#L637-L997).

### Shared fragment leaves: layer and primitive identity

The `shared_frag_library*` leaves share a fragment shader library between a classic vertex pipeline and a mesh pipeline. The `shared_frag_shader*` leaves use the same idea with shader objects. Layer variants write classic geometry to layer 1 and mesh geometry to layer 2, then select colors with `gl_Layer`. Primitive-ID variants render the two draws into separate two-pixel-high framebuffers and use `gl_PrimitiveID`. `mesh_first` reverses draw order, and `extra_input` adds a location-0 multiplier input. See [SharedFragLibraryCase](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTestsEXT.cpp#L1547-L2265).

### Depth leaves: point and triangle coverage

`depth_only_points` and `depth_only_triangles` create one primitive per pixel from deterministic random depth values. The optional `_position_components` form writes each `gl_Position` component separately instead of assigning the complete vector. The depth test uses `VK_COMPARE_OP_LESS`, clears to 1.0, and compares the copied `D16_UNORM` image to the generated depth reference. See [depth-only execution](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTestsEXT.cpp#L2267-L2543).

## Shader Analysis

The following walkthrough uses the direct mesh-only triangle path because it is the smallest generated shader that still exercises EXT mesh output assembly, descriptor reads, and per-primitive data flow. The source was reconstructed from `MeshOnlyTriangleCase::initPrograms`; its SPIR-V artifact was compiled, validated, and disassembled with the shader-disassembler workflow using the source helper's SPIR-V 1.4 target.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.mesh_shader.ext.smoke.monolithic.mesh_shader_triangle
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `monolithic` | Builds one graphics pipeline containing the mesh and fragment stages. |
| `mesh_shader_triangle` | Dispatches one mesh workgroup, reads three indexed coordinates, and outputs one blue triangle. |
| `VK_EXT_mesh_shader` | Enables the EXT mesh GLSL built-ins and mesh execution model. |

#### Purpose

The mesh stage must produce one valid triangle from its declared output arrays. The fragment stage forwards the per-primitive blue color, so the host can check the complete mesh-to-framebuffer path.

#### Structural Design

| Phase | Shader operation | Observable result |
|-------|------------------|-------------------|
| Configure output | `SetMeshOutputsEXT(3u, 1u)` | Three vertices and one triangle are active. |
| Color the primitive | Store blue in `triangleColor[0]` | The fragment shader receives the expected per-primitive value. |
| Write vertices | First three local invocations read `ib.indices` and `cb.coords` | `gl_MeshVerticesEXT` receives the triangle positions. |
| Write topology | Invocation 0 stores `uvec3(0, 1, 2)` | The rasterizer has one triangle to draw. |

#### Shader Code

```glsl
#version 450
#extension GL_EXT_mesh_shader : enable

// We will actually output a single triangle and most invocations will do no work.
layout(local_size_x=8, local_size_y=4, local_size_z=4) in;
layout(triangles) out;
layout(max_vertices=256, max_primitives=256) out;

// Unique vertex coordinates.
layout (set=0, binding=0) uniform CoordsBuffer {
    vec4 coords[3];
} cb;
// Unique vertex indices.
layout (set=0, binding=1, std430) readonly buffer IndexBuffer {
    uint indices[3];
} ib;

// Triangle color.
layout (location=0) out perprimitiveEXT vec4 triangleColor[];

void main ()
{
    /// The mesh workgroup publishes exactly three vertices and one triangle.
    SetMeshOutputsEXT(3u, 1u);
    triangleColor[0] = vec4(0.0, 0.0, 1.0, 1.0);

    const uint vertexIndex = gl_LocalInvocationIndex;
    if (vertexIndex < 3u)
    {
        const uint coordsIndex = ib.indices[vertexIndex];
        gl_MeshVerticesEXT[vertexIndex].gl_Position = cb.coords[coordsIndex];
    }
    if (vertexIndex == 0u)
    {
        gl_PrimitiveTriangleIndicesEXT[0] = uvec3(0, 1, 2);
    }
}
```

#### Additional Info

- The source creates host-visible coordinate and index buffers. The mesh shader sees them at descriptor bindings 0 and 1; the fragment shader has no descriptor inputs.
- The host supplies `(-1,-1)`, `(-1,3)`, and `(3,-1)` as clip-space coordinates and dispatches one mesh workgroup with `cmdDrawMeshTasksEXT(1u, 1u, 1u)`.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Task stage | The representative has no task shader. `mesh_task_shader_triangle` adds a task payload and launches two mesh workgroups; `task_only_shader_triangle` emits zero workgroups. | [task and mesh builders](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTestsEXT.cpp#L289-L420) |
| Fragment stage | The rasterization-disabled sibling omits the fragment module and expects the clear color; the mesh output code remains the same. | [triangle runtime](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTestsEXT.cpp#L574-L634) |
| Construction type | The shader source remains the same while pipeline construction changes among monolithic, library, and shader-object-supported paths. | [construction factory](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTestsEXT.cpp#L2547-L2635) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `mesh`
- Target SPIRV version: `spirv1.4`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.4
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 72
; Schema: 0
               OpCapability MeshShadingEXT
               OpExtension "SPV_EXT_mesh_shader"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint MeshEXT %main "main" %triangleColor %gl_LocalInvocationIndex %ib %gl_MeshVerticesEXT %cb %gl_PrimitiveTriangleIndicesEXT
               OpExecutionMode %main LocalSize 8 4 4
               OpExecutionMode %main OutputVertices 256
               OpExecutionMode %main OutputPrimitivesEXT 256
               OpExecutionMode %main OutputTrianglesEXT
               OpSource GLSL 450
               OpSourceExtension "GL_EXT_mesh_shader"
               OpName %main "main"
               OpName %triangleColor "triangleColor"
               OpName %vertexIndex "vertexIndex"
               OpName %gl_LocalInvocationIndex "gl_LocalInvocationIndex"
               OpName %coordsIndex "coordsIndex"
               OpName %IndexBuffer "IndexBuffer"
               OpMemberName %IndexBuffer 0 "indices"
               OpName %ib "ib"
               OpName %gl_MeshPerVertexEXT "gl_MeshPerVertexEXT"
               OpMemberName %gl_MeshPerVertexEXT 0 "gl_Position"
               OpMemberName %gl_MeshPerVertexEXT 1 "gl_PointSize"
               OpMemberName %gl_MeshPerVertexEXT 2 "gl_ClipDistance"
               OpMemberName %gl_MeshPerVertexEXT 3 "gl_CullDistance"
               OpName %gl_MeshVerticesEXT "gl_MeshVerticesEXT"
               OpName %CoordsBuffer "CoordsBuffer"
               OpMemberName %CoordsBuffer 0 "coords"
               OpName %cb "cb"
               OpName %gl_PrimitiveTriangleIndicesEXT "gl_PrimitiveTriangleIndicesEXT"
               OpDecorate %triangleColor Location 0
               OpDecorate %triangleColor PerPrimitiveEXT
               OpDecorate %gl_LocalInvocationIndex BuiltIn LocalInvocationIndex
               OpDecorate %_arr_uint_uint_3 ArrayStride 4
               OpDecorate %IndexBuffer Block
               OpMemberDecorate %IndexBuffer 0 NonWritable
               OpMemberDecorate %IndexBuffer 0 Offset 0
               OpDecorate %ib NonWritable
               OpDecorate %ib Binding 1
               OpDecorate %ib DescriptorSet 0
               OpDecorate %gl_MeshPerVertexEXT Block
               OpMemberDecorate %gl_MeshPerVertexEXT 0 BuiltIn Position
               OpMemberDecorate %gl_MeshPerVertexEXT 1 BuiltIn PointSize
               OpMemberDecorate %gl_MeshPerVertexEXT 2 BuiltIn ClipDistance
               OpMemberDecorate %gl_MeshPerVertexEXT 3 BuiltIn CullDistance
               OpDecorate %_arr_v4float_uint_3 ArrayStride 16
               OpDecorate %CoordsBuffer Block
               OpMemberDecorate %CoordsBuffer 0 Offset 0
               OpDecorate %cb Binding 0
               OpDecorate %cb DescriptorSet 0
               OpDecorate %gl_PrimitiveTriangleIndicesEXT BuiltIn PrimitiveTriangleIndicesEXT
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
     %uint_3 = OpConstant %uint 3
     %uint_1 = OpConstant %uint 1
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
   %uint_256 = OpConstant %uint 256
%_arr_v4float_uint_256 = OpTypeArray %v4float %uint_256
%_ptr_Output__arr_v4float_uint_256 = OpTypePointer Output %_arr_v4float_uint_256
%triangleColor = OpVariable %_ptr_Output__arr_v4float_uint_256 Output
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
    %float_0 = OpConstant %float 0
    %float_1 = OpConstant %float 1
         %19 = OpConstantComposite %v4float %float_0 %float_0 %float_1 %float_1
%_ptr_Output_v4float = OpTypePointer Output %v4float
%_ptr_Function_uint = OpTypePointer Function %uint
%_ptr_Input_uint = OpTypePointer Input %uint
%gl_LocalInvocationIndex = OpVariable %_ptr_Input_uint Input
       %bool = OpTypeBool
%_arr_uint_uint_3 = OpTypeArray %uint %uint_3
%IndexBuffer = OpTypeStruct %_arr_uint_uint_3
%_ptr_StorageBuffer_IndexBuffer = OpTypePointer StorageBuffer %IndexBuffer
         %ib = OpVariable %_ptr_StorageBuffer_IndexBuffer StorageBuffer
%_ptr_StorageBuffer_uint = OpTypePointer StorageBuffer %uint
%_arr_float_uint_1 = OpTypeArray %float %uint_1
%gl_MeshPerVertexEXT = OpTypeStruct %v4float %float %_arr_float_uint_1 %_arr_float_uint_1
%_arr_gl_MeshPerVertexEXT_uint_256 = OpTypeArray %gl_MeshPerVertexEXT %uint_256
%_ptr_Output__arr_gl_MeshPerVertexEXT_uint_256 = OpTypePointer Output %_arr_gl_MeshPerVertexEXT_uint_256
%gl_MeshVerticesEXT = OpVariable %_ptr_Output__arr_gl_MeshPerVertexEXT_uint_256 Output
%_arr_v4float_uint_3 = OpTypeArray %v4float %uint_3
%CoordsBuffer = OpTypeStruct %_arr_v4float_uint_3
%_ptr_Uniform_CoordsBuffer = OpTypePointer Uniform %CoordsBuffer
         %cb = OpVariable %_ptr_Uniform_CoordsBuffer Uniform
%_ptr_Uniform_v4float = OpTypePointer Uniform %v4float
     %uint_0 = OpConstant %uint 0
     %v3uint = OpTypeVector %uint 3
%_arr_v3uint_uint_256 = OpTypeArray %v3uint %uint_256
%_ptr_Output__arr_v3uint_uint_256 = OpTypePointer Output %_arr_v3uint_uint_256
%gl_PrimitiveTriangleIndicesEXT = OpVariable %_ptr_Output__arr_v3uint_uint_256 Output
     %uint_2 = OpConstant %uint 2
         %66 = OpConstantComposite %v3uint %uint_0 %uint_1 %uint_2
%_ptr_Output_v3uint = OpTypePointer Output %v3uint
     %uint_8 = OpConstant %uint 8
     %uint_4 = OpConstant %uint 4
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_8 %uint_4 %uint_4
       %main = OpFunction %void None %3
          %5 = OpLabel
%vertexIndex = OpVariable %_ptr_Function_uint Function
%coordsIndex = OpVariable %_ptr_Function_uint Function
               OpSetMeshOutputsEXT %uint_3 %uint_1
         %21 = OpAccessChain %_ptr_Output_v4float %triangleColor %int_0
               OpStore %21 %19
         %26 = OpLoad %uint %gl_LocalInvocationIndex
               OpStore %vertexIndex %26
         %27 = OpLoad %uint %vertexIndex
         %29 = OpULessThan %bool %27 %uint_3
               OpSelectionMerge %31 None
               OpBranchConditional %29 %30 %31
         %30 = OpLabel
         %37 = OpLoad %uint %vertexIndex
         %39 = OpAccessChain %_ptr_StorageBuffer_uint %ib %int_0 %37
         %40 = OpLoad %uint %39
               OpStore %coordsIndex %40
         %46 = OpLoad %uint %vertexIndex
         %51 = OpLoad %uint %coordsIndex
         %53 = OpAccessChain %_ptr_Uniform_v4float %cb %int_0 %51
         %54 = OpLoad %v4float %53
         %55 = OpAccessChain %_ptr_Output_v4float %gl_MeshVerticesEXT %46 %int_0
               OpStore %55 %54
               OpBranch %31
         %31 = OpLabel
         %56 = OpLoad %uint %vertexIndex
         %58 = OpIEqual %bool %56 %uint_0
               OpSelectionMerge %60 None
               OpBranchConditional %58 %59 %60
         %59 = OpLabel
         %68 = OpAccessChain %_ptr_Output_v3uint %gl_PrimitiveTriangleIndicesEXT %int_0
               OpStore %68 %66
               OpBranch %60
         %60 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- Each case checks support before creating the instance. The common helper requires `VK_EXT_mesh_shader` and the selected task/mesh feature bits; the pipeline wrapper then checks the requirements for the selected construction type.
- Triangle, gradient, partial-usage, and shared-fragment cases create color attachments, record mesh-task draws, transition or copy the attachment to a host-visible buffer, and invalidate the allocation before reading it.
- The basic triangle uses an 8x8 `VK_FORMAT_R8G8B8A8_UNORM` attachment and an exact zero threshold. The ordinary path must be solid blue; discard and zero-task paths must preserve `(0, 0, 0, 1)`.
- Partial usage renders selected front triangles and then a background triangle. It compares the copied image with a generated reference using a color threshold of `0.005f`.
- Gradient checking treats each shading-rate block as uniform and requires the block color to equal one of the reference pixels in that block. A block that crosses the diagonal between the two primitives may be non-uniform by design.
- Shared fragment cases copy every framebuffer layer and compare each pixel to the expected layer or primitive color. They bind the appropriate pipeline or shader stages, including a second draw with the other pre-rasterization path.
- Depth-only cases draw `32` workgroups across a `64x32` `D16_UNORM` attachment; each workgroup handles one full row. They copy depth to a host-visible buffer and compare it with the deterministic depth reference using `0.000025f`.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `mesh_shader_triangle` | Mesh output assembly, descriptor reads, or basic color attachment handling is wrong. |
| `mesh_shader_triangle_rasterization_disabled` | Mesh output assembly, descriptor reads, fragment-stage omission, or unchanged color attachment handling is wrong. |
| `mesh_task_shader_triangle` | Task payload propagation, task-to-mesh launch count, or mesh output/color handling is wrong. |
| `task_only_shader_triangle` | Zero-workgroup task behavior, task launch handling, or unchanged color attachment handling is wrong. |
| `partial_usage` / `partial_usage_without_compaction` | Variable mesh output counts, per-primitive data, push-constant addressing, or the active-versus-unused output distinction is wrong. |
| `fullscreen_gradient` | Mesh interpolation or gradient color generation is wrong. |
| `fullscreen_gradient_fs2x1` / `fullscreen_gradient_fs2x2` | Mesh interpolation, primitive shading-rate output, or fragment-shading-rate block behavior is wrong. |
| `shared_frag_library*` / `shared_frag_shader*` | Shared fragment-stage interfaces, `gl_Layer` or `gl_PrimitiveID`, pipeline-library linking, or shader-object rebinding is wrong. |
| `depth_only_points` / `depth_only_triangles` | Point/triangle mesh output, depth coordinates, depth testing/writes, or depth attachment checking is wrong. |
| `depth_only_points_position_components` / `depth_only_triangles_position_components` | Point/triangle mesh output, depth coordinates, depth testing/writes, component-wise position assignment, or depth attachment checking is wrong. |

### Cause Analysis

#### Mesh output or basic attachment handling

**Possible failure symptoms:** The triangle image differs from the expected blue pixels, or the rasterization-disabled variant changes pixels that should remain at the clear color.

**Possible implementation causes:** The implementation may mishandle EXT mesh output counts, descriptor-backed coordinate/index reads, primitive indices, fragment-stage omission, or color attachment writes. The source and the mesh-shader specification define the expected data flow, but a more specific fault location requires implementation investigation.

#### Task launch and payload handling

**Possible failure symptoms:** The two-triangle task path does not produce the expected image, or the task-only path changes the clear attachment.

**Possible implementation causes:** Task payload sharing, `EmitMeshTasksEXT` launch dimensions, or suppression of a mesh shader after a zero launch may be mishandled. The test does not distinguish compiler, device, and host causes further than the observed image.

#### Variable mesh output and partial usage

**Possible failure symptoms:** Selected pixels have the wrong red/blue values, the background is visible where a front triangle should be, or unused vertices affect the result.

**Possible implementation causes:** The implementation may mishandle workgroup-dependent `SetMeshOutputsEXT` counts, indexed reads from the vertex and primitive buffers, push-constant values, or the distinction between active and unused output vertices. Source inspection grounds these candidate mechanisms; the exact implementation cause needs investigation.

#### Gradient and fragment shading rate

**Possible failure symptoms:** A gradient block is not uniform when it should be, or its color is not one of the reference colors for that block.

**Possible implementation causes:** The implementation may mishandle mesh-to-fragment interpolation, per-primitive shading-rate built-ins, or fragment shading-rate block selection. The source check allows diagonal boundary blocks to vary, so failures outside that allowance indicate a different problem.

#### Shared fragment interfaces and construction

**Possible failure symptoms:** A layer or primitive-ID framebuffer contains the wrong color for one or more pixels.

**Possible implementation causes:** Graphics pipeline library linking, shared fragment-stage interfaces, `gl_Layer`/`gl_PrimitiveID` handling, shader-object stage rebinding, or dynamic graphics state may be incorrect. The Vulkan specification links these observations to the relevant interface and construction rules, but source-level investigation is needed to identify the failing implementation component.

#### Depth output and comparison

**Possible failure symptoms:** One or more copied depth pixels differ from the deterministic reference beyond `0.000025f`.

**Possible implementation causes:** The implementation may mishandle point or triangle mesh output, clip-space depth, depth-test/write ordering, or vector versus component assignments to `gl_Position`. The test's threshold accounts for `D16_UNORM` quantization; a failure beyond it requires source-level investigation.

## Case Pruning

### Requirement-based pruning

- Every case requires the EXT mesh-shader support checked by `checkTaskMeshShaderSupportEXT`, with task support required for task-emitting paths and mesh support required for mesh paths.
- `fullscreen_gradient_fs2x1` and `fullscreen_gradient_fs2x2` require `primitiveFragmentShadingRateMeshShader`; the 1x1 gradient does not.
- Shared `gl_PrimitiveID` cases require the core geometry-shader feature because glslang emits the Geometry capability for that fragment shader.
- Shared layer cases require `VK_EXT_shader_viewport_index_layer` before Vulkan 1.2, or Vulkan 1.2 `shaderOutputLayer` when the equivalent API version is 1.2 or newer.
- Each construction type is checked with `checkPipelineConstructionRequirements`. The required graphics-pipeline-library or shader-object functionality therefore controls whether that case can run.

### Design-based pruning

- The factory does not add the ordinary triangle, partial, or gradient children under `shader_objects`; that group receives the depth-only leaves and the eight `shared_frag_shader*` variants present in the default mustpass.
- `shared_frag_library*` uses library construction only for `optimized_lib` and `fast_lib`; monolithic has no shared-library variants, while shader objects use the corresponding `shared_frag_shader*` names.
- The source creates 2x2x2 combinations of `primitiveID`, `meshFirst`, and `extraInput` for each non-monolithic construction type. The names retain only the suffixes for enabled values.
- The depth family intentionally keeps both primitive shapes and both position-assignment forms for all four construction types.

## Key Takeaways

- The EXT smoke family checks both the mesh shader execution model and the API mechanisms used to construct and bind it.
- Task emission controls whether mesh workgroups run. A task shader that emits zero workgroups is checked through an unchanged clear attachment, not through a mesh result.
- `partial_usage` stresses output counts and unused output slots, while the gradient and depth families make interpolation, shading-rate blocks, and depth writes observable in images.
- Shared fragment cases use the same fragment logic with classic and mesh pre-rasterization stages, exposing interface and construction mismatches through layer or primitive colors.
- The default mustpass coverage is asymmetric by design: 13 monolithic leaves, 21 each for the two library modes, and 12 shader-object leaves.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Smoke registration factory | [createMeshShaderSmokeTestsEXT](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTestsEXT.cpp#L2547-L2635) | Defines the four direct construction children and their generated leaves. |
| Triangle case support, programs, and runtime | [triangle cases](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTestsEXT.cpp#L222-L634) | Implements mesh-only, task-to-mesh, and zero-task paths, including color checks. |
| Gradient generator and result scan | [gradient path](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTestsEXT.cpp#L637-L997) | Emits the coordinate gradient and checks shading-rate blocks. |
| Partial usage generator and renderer | [partial usage](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTestsEXT.cpp#L999-L1545) | Uses variable mesh output counts, two descriptor sets, and push constants. |
| Shared fragment generator and renderer | [shared fragment path](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTestsEXT.cpp#L1547-L2265) | Covers graphics pipeline libraries, shader objects, layer, primitive ID, and draw order. |
| Depth-only generator and runner | [depth-only path](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTestsEXT.cpp#L2267-L2543) | Generates point/triangle output and compares copied depth. |
| Common support and build options | [vktMeshShaderUtil.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L111-L141) | Supplies EXT feature checks and the minimum SPIR-V 1.4 mesh build target. |
| Default mustpass coverage | [mesh-shader.txt](../../../mustpass/main/vk-default/mesh-shader.txt) | Contains the 67 exact EXT smoke leaves. |
| Mesh shader specification | [VK_EXT_mesh_shader](../../../../vulkan-docs/src/proposals/VK_EXT_mesh_shader.adoc) | Defines the task and mesh shader stages and their output model. |
| Graphics pipeline library specification | [VK_EXT_graphics_pipeline_library](../../../../vulkan-docs/src/appendices/VK_EXT_graphics_pipeline_library.adoc) | Defines the library pieces and linking used by shared fragment cases. |
| Shader object specification | [VK_EXT_shader_object](../../../../vulkan-docs/src/appendices/VK_EXT_shader_object.adoc) | Defines independently created and bound stages used by `shared_frag_shader*`. |
