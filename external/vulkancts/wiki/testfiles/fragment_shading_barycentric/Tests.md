## Overview

**Core question:** Do fragment shaders receive the correct per-vertex data and barycentric weights across primitive assembly, interpolation, shader stage, and pipeline construction variants?

- [`vktFragmentShadingBarycentricTests.cpp`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2642-L3149) registers and implements the `fragment_shading_barycentric` test category. Its two behavior families are `data` and `weights`.
- `data` reads `PerVertexKHR` inputs and checks that vertex-indexed values, optional interpolated values, and optional flat values agree with the test's expected mapping.
- `weights` uses barycentric built-ins to reconstruct a colored primitive and compares that image with a reference interpolation path.
- The same matrices run with monolithic graphics pipelines, `pipeline_library`, and `fast_linked_library`. The default mustpass contains exactly 20,991 test case leaves: 6,625 `data` leaves under each of the three construction roots and 372 `weights` leaves under each root.
- The page explains the parameter matrix, support gates, host/device checking, pruning, failure interpretation, and two representative generated fragment shaders.

## Background Knowledge

- **Barycentric weights.** A fragment's three weights describe its position relative to the primitive's three logical vertices. Vulkan defines `BaryCoordKHR` with perspective interpolation and `BaryCoordNoPerspKHR` with linear interpolation; point primitives use `(1,0,0)`, line primitives interpolate values for logical vertices 0 and 1, and polygon primitives interpolate the three vertex values. See [Barycentric Interpolation](../../../../vulkan-docs/src/chapters/primsrast.adoc#L2433-L2554) and [`BaryCoordKHR`](../../../../vulkan-docs/src/chapters/interfaces.adoc#L2077-L2102).
- **Per-vertex fragment inputs.** `PerVertexKHR` disables ordinary interpolation and exposes an array whose indices name the primitive's logical vertices. Missing vertices repeat the valid vertex with the highest index: indices 1 and 2 repeat index 0 for points, and index 2 repeats index 1 for lines. See [`PerVertexKHR`](../../../../vulkan-docs/src/chapters/primsrast.adoc#L2435-L2448) and [interpolation decorations](../../../../vulkan-docs/src/chapters/shaders.adoc#L2952-L2959).
- **Provoking vertex and primitive assembly.** The logical-to-original vertex mapping depends on topology and, for selected triangle topologies, the provoking vertex mode. The barycentric specification gives separate mappings for first and last provoking vertices and a property that can make odd triangle-strip ordering independent of the mode. See [the standard ordering table](../../../../vulkan-docs/src/chapters/primsrast.adoc#L2476-L2492), [the last-vertex table](../../../../vulkan-docs/src/chapters/primsrast.adoc#L2494-L2514), and [`triStripVertexOrderIndependentOfProvokingVertex`](../../../../vulkan-docs/src/chapters/limits.adoc#L4811-L4819).

## Registration Hierarchy

```text
fragment_shading_barycentric
├── data
├── weights
├── pipeline_library
└── fast_linked_library
```

`pipeline_library` and `fast_linked_library` each contain their own `data` and `weights` test families. The default root contains the monolithic equivalents. Registration and mustpass evidence is [`fragment-shading-barycentric.txt`](../../../mustpass/main/vk-default/fragment-shading-barycentric.txt#L1-L20991).

## Parameter Dimensions and Observed Values

The source arrays and nested loops define the matrix at [`createTests`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2642-L2738), with family-specific construction at [`data` registration](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2740-L2944) and [`weights` registration](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2946-L3144). The values below are registered names, not shorthand for unregistered combinations.

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Pipeline construction | monolithic root, `pipeline_library`, `fast_linked_library` | Selects the graphics pipeline construction path while retaining the same shader and checking logic. | [`constructionTypeCases[]`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2646-L2659) |
| Data behavior family | `data`, `weights` | Chooses per-vertex data validation or barycentric-weight image comparison. | [`TestType`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L66-L70), [`createInstance`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L1570-L1581) |
| Primitive topology | `point_list`, `line_list`, `line_strip`, `triangle_list`, `triangle_strip`, `triangle_fan`, `line_list_with_adjacency`, `line_strip_with_adjacency`, `triangle_list_with_adjacency`, `triangle_strip_with_adjacency` | Changes primitive assembly and the logical-to-original vertex mapping. | [`topologies[]`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2661-L2676), [ordering table](../../../../vulkan-docs/src/chapters/primsrast.adoc#L2476-L2492) |
| Data indexing | `static`, `dynamic` | Uses literal fragment indices or push-constant indices `pc.n[0..2]` when reading the per-vertex array. | [`dynamicIndexings[]`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2707-L2714), [`initDataPrograms`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L1913-L1919) |
| Data aggregate | `type`, `struct`, `array2` | Tests a scalar/vector value, a one-member structure, or a two-element array as the per-vertex input. | [`initDataPrograms`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L1864-L1888) |
| Data type | `float`, `vec2`, `vec3`, `vec4`, `double`, `dvec2`, `dvec3`, `dvec4`, `int`, `ivec2`, `ivec3`, `ivec4`, `uint`, `uvec2`, `uvec3`, `uvec4` | Changes scalar width, vector component count, declarations, and expected mask width. | [`dataTypes[]`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2693-L2698), [`getComponentCount`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L129-L137) |
| Data interpolation | `per_vertex`, `per_vertex_interp`, `per_vertex_flat` | Enables no extra input, a normally interpolated input, or a flat input whose value comes from the provoking vertex. | [`interpolationTypes[]`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2732-L2738), [`initDataPrograms`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L1974-L1981) |
| Clipping | `no_clip`, `clip` | The triangle-list-only clipped case moves vertices outside the viewport and uses a separate primitive formula. | [`clipVerticesSpecs[]`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2677-L2684), [`getDataPrimitiveFormula`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L1601-L1625) |
| Producer stage | `vertex_shader`, `mesh_shader` | Produces primitive vertices through fixed vertex input or `GL_EXT_mesh_shader` storage-buffer reads and emitted primitive indices. | [`useMeshShaderSpecs[]`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2685-L2692), [`generateDataMeshShader`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L1704-L1862) |
| Weights interpolation | `perspective`, `noperspective` | Selects `BaryCoordKHR` or `BaryCoordNoPerspKHR`, respectively. | [`initWeightPrograms`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2473-L2505), [built-in definitions](../../../../vulkan-docs/src/chapters/interfaces.adoc#L2077-L2102) and [linear built-in](../../../../vulkan-docs/src/chapters/interfaces.adoc#L2136-L2164) |
| Weights topology mode | `pipeline_topology_static`, `pipeline_topology_dynamic` | Uses the topology at pipeline creation or sets `VK_DYNAMIC_STATE_PRIMITIVE_TOPOLOGY` before the draw. | [`topologiesInPipeline[]`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2724-L2731), [`WeightTestInstance::iterate`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L1300-L1418) |
| Weights rotation | `0`, `85`, `95` | Rotates the colored primitive through the push-constant MVP matrix in static-topology cases. | [`rotations[]`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2723-L2723), [`WeightTestInstance::iterate`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L1311-L1313) |
| Weights sample mode | `single_sample`, `msaa_interpolate_at_centroid`, `msaa_interpolate_at_sample`, `msaa_interpolate_at_offset`, `msaa_centroid_qualifier`, `msaa_sample_qualifier` | Selects one sample or 4x MSAA and the GLSL/SPIR-V way the barycentric input is evaluated. | [`msaaCases[]`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2948-L2960), [`initWeightPrograms`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2592-L2638) |

## Behavior Parameters

The primary behavioral axis is the **test family**. `data` asks whether per-vertex inputs and their related interpolation forms carry the right values through primitive assembly. `weights` asks whether the fragment barycentric built-in produces the right interpolation coordinates. Pipeline construction, topology, stages, and feature-gated variants configure those two questions rather than replacing them.

### data: Per-vertex data propagation and interpolation

The generated producer assigns values derived from the vertex number. The fragment shader computes the expected original vertex indices using topology-specific formulas, reads `data[0]`, `data[1]`, and `data[2]` through `pervertexEXT`, and writes a bit mask. `per_vertex_interp` adds an ordinary interpolated input and accepts a floating-point tolerance; `per_vertex_flat` checks the provoking-vertex value. The implementation is in [`initDataPrograms`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L1864-L2148).

The `misc.pervertex_correctness` leaf uses two triangles and checks that `PerVertexKHR` data and a flat input remain correct across the primitive boundary. The `shader_combos` leaves add tessellation, geometry, or both, then carry the data through those stages before the fragment reads it. See [`initMiscDataPrograms`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2178-L2292), [`initMiscDataTessPrograms`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2200-L2292), and [`initMiscDataGeomPrograms`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2294-L2349).

### weights: Barycentric coordinate and interpolation behavior

The producer emits colored primitives. The reference fragment shader receives a conventional interpolated `in_color`; the test fragment shader receives `pervertexEXT in_color[]`, obtains `gl_BaryCoordEXT` or `gl_BaryCoordNoPerspEXT`, and evaluates `in_color[0] * bc.x + in_color[1] * bc.y + in_color[2] * bc.z`. Both images use the same render geometry and the host compares them. See [`initWeightPrograms`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2473-L2638).

Static-topology cases exercise rotations and all listed topologies. Dynamic-topology cases build a list-compatible pipeline topology, set the requested topology with `cmdSetPrimitiveTopology`, and omit mesh-shader combinations because Vulkan disallows dynamic primitive topology in a pre-rasterization mesh-shader pipeline. The registration loops show both decisions at [`weights` registration](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2972-L3138).

## Shader Analysis

These representative walkthroughs show the two different shader contracts. The first is a `data` fragment shader with a normal interpolated side input; the second is the central `weights` fragment shader. The source uses `SPIRV_VERSION_1_4` build options for these generated paths, so the disassembler artifacts below target `spirv1.4`.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.fragment_shading_barycentric.data.provoking_first.static.triangle_list.no_clip.type.vec3.per_vertex_interp.vertex_shader
```

| Parameter choice | Meaning in this representative case |
|------------------|--------------------------------------|
| `data` + `triangle_list` | The fragment's logical vertices map to consecutive groups of three source vertices. |
| `type.vec3` | Each per-vertex value has three scalar components, so the mask checks nine scalar values across three logical vertices. |
| `per_vertex_interp` | The shader checks both `PerVertexKHR` indexing and a regular interpolated `dataIntrp` input. |
| `provoking_first` + `static` | The flat path is disabled in this case; the index path uses literal `0`, `1`, and `2`. |

#### Purpose

This fragment shader checks that direct `PerVertexKHR` reads select the three triangle vertices and that a normal interpolated value agrees with the same barycentric combination.

#### Structural Design

| Phase | Shader operation | Expected result |
|------|------------------|-----------------|
| Identify primitive | Derive `p` from `gl_FragCoord` and select `3*p`, `3*p+1`, `3*p+2`. | Select the triangle covering the pixel. |
| Build expected values | Generate `eA`, `eB`, and `eC`, then flatten them into `e`. | Record the source-generated values for each logical vertex. |
| Read inputs | Read `data[0..2]` and `dataIntrp`. | Obtain the implementation's per-vertex and interpolated results. |
| Emit mask | Compare exact per-vertex values and compare interpolation within `0.001`. | A set bit records one matching scalar component. |

#### Shader Code

```glsl
#version 450
#extension GL_EXT_fragment_shader_barycentric : require

layout(location = 1) in vec3 dataIntrp;
layout(location = 0) out uvec4 out_color;
layout(location = 0) pervertexEXT in vec3 data[];

void main()
{
    const int w = 8;
    const int x = int(gl_FragCoord.x - 0.5f);
    const int y = int(gl_FragCoord.y - 0.5f);
    const int p = (x < y) ? 0 : 1;

    vec3 eA; { const int n = 1 + (3*p);   eA = vec3(n, 2*n, 4*n); }
    vec3 eB; { const int n = 1 + (3*p+1); eB = vec3(n, 2*n, 4*n); }
    vec3 eC; { const int n = 1 + (3*p+2); eC = vec3(n, 2*n, 4*n); }

    float e[9] = { eA.x,eA.y,eA.z,eB.x,eB.y,eB.z,eC.x,eC.y,eC.z };
    vec3 eIntrpV = vec3(eA * gl_BaryCoordEXT.x + eB * gl_BaryCoordEXT.y + eC * gl_BaryCoordEXT.z);
    float eIntrp[3] = { eIntrpV.x,eIntrpV.y,eIntrpV.z };

    vec3 vA = data[0];
    vec3 vB = data[1];
    vec3 vC = data[2];
    vec3 vIntrpV = dataIntrp;
    float vIntrp[3] = { vIntrpV.x,vIntrpV.y,vIntrpV.z };
    float v[9] = { vA.x,vA.y,vA.z,vB.x,vB.y,vB.z,vC.x,vC.y,vC.z };
    uvec4 mask = uvec4(0);

    for (int i = 0; i < 9; i++)
        if (e[i] == v[i])
            mask.x = mask.x | (1u << i);
    for (int i = 0; i < 3; i++)
        if (abs(eIntrp[i] - vIntrp[i]) < 0.001)
            mask.y = mask.y | (1u << i);
    out_color = mask;
}
```

#### Additional Info

- The checked-in generator emits the same data-flow shape but specializes aggregate type, dynamic indices, topology formulas, optional flat input, and mesh/vertex producer code from `TestParams`; this walkthrough fixes those choices to one executable path. See [`TestParams`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L107-L127) and [`initDataPrograms`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L1913-L2148).
- The source-generated `dataIntrp` declaration occupies a later location after the base input; location allocation accounts for aggregate size and double-width locations. See [`locationsPerInput`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2108-L2126).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Topology and provoking vertex | `getDataVertexFormula` changes which original values feed `eA/eB/eC`; last-provoking-vertex tables alter triangle strip and fan mappings. | [`getDataVertexFormula`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L1628-L1669), [last-vertex table](../../../../vulkan-docs/src/chapters/primsrast.adoc#L2494-L2514) |
| Dynamic indexing | Literal `0`, `1`, `2` become push-constant `pc.n[0]`, `pc.n[1]`, `pc.n[2]`. | [`dynamicIndexing`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L1913-L1919) |
| Aggregate and data type | `vec3` becomes a scalar/vector, `DataStruct`, or array suffix; scalarization and component count change the mask. | [`typePrefix/typeSuffix`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L1867-L1899) |
| Interpolation | `per_vertex_interp` adds `dataIntrp` and a tolerance comparison; `per_vertex_flat` adds a flat read selected by the provoking vertex. | [`fragShader` inputs and checks](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L1974-L2084) |
| Producer stage | Vertex input writes values using `gl_VertexIndex`; mesh shader code reads a storage buffer and emits `gl_MeshVerticesEXT` plus primitive indices. | [`vertex shader template`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L1938-L1967), [`data mesh shader`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L1704-L1862) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed GLSL from this walkthrough
- Stage: `frag`
- Target SPIRV version: `spirv1.4`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.4
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 242
; Schema: 0
               OpCapability Shader
               OpCapability FragmentBarycentricKHR
               OpExtension "SPV_KHR_fragment_shader_barycentric"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %gl_FragCoord %gl_BaryCoordEXT %data %dataIntrp %out_color
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 450
               OpSourceExtension "GL_EXT_fragment_shader_barycentric"
               OpName %main "main"
               OpName %x "x"
               OpName %gl_FragCoord "gl_FragCoord"
               OpName %y "y"
               OpName %p "p"
               OpName %n "n"
               OpName %eA "eA"
               OpName %n_0 "n"
               OpName %eB "eB"
               OpName %n_1 "n"
               OpName %eC "eC"
               OpName %e "e"
               OpName %eIntrpV "eIntrpV"
               OpName %gl_BaryCoordEXT "gl_BaryCoordEXT"
               OpName %eIntrp "eIntrp"
               OpName %vA "vA"
               OpName %data "data"
               OpName %vB "vB"
               OpName %vC "vC"
               OpName %vIntrpV "vIntrpV"
               OpName %dataIntrp "dataIntrp"
               OpName %vIntrp "vIntrp"
               OpName %v "v"
               OpName %mask "mask"
               OpName %i "i"
               OpName %i_0 "i"
               OpName %out_color "out_color"
               OpDecorate %gl_FragCoord BuiltIn FragCoord
               OpDecorate %gl_BaryCoordEXT BuiltIn BaryCoordKHR
               OpDecorate %data Location 0
               OpDecorate %data PerVertexKHR
               OpDecorate %dataIntrp Location 1
               OpDecorate %out_color Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
%_ptr_Function_int = OpTypePointer Function %int
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Input_v4float = OpTypePointer Input %v4float
%gl_FragCoord = OpVariable %_ptr_Input_v4float Input
       %uint = OpTypeInt 32 0
     %uint_0 = OpConstant %uint 0
%_ptr_Input_float = OpTypePointer Input %float
  %float_0_5 = OpConstant %float 0.5
     %uint_1 = OpConstant %uint 1
       %bool = OpTypeBool
      %int_0 = OpConstant %int 0
      %int_1 = OpConstant %int 1
      %int_3 = OpConstant %int 3
    %v3float = OpTypeVector %float 3
%_ptr_Function_v3float = OpTypePointer Function %v3float
      %int_2 = OpConstant %int 2
      %int_4 = OpConstant %int 4
     %uint_9 = OpConstant %uint 9
%_arr_float_uint_9 = OpTypeArray %float %uint_9
%_ptr_Function__arr_float_uint_9 = OpTypePointer Function %_arr_float_uint_9
%_ptr_Function_float = OpTypePointer Function %float
     %uint_2 = OpConstant %uint 2
%_ptr_Input_v3float = OpTypePointer Input %v3float
%gl_BaryCoordEXT = OpVariable %_ptr_Input_v3float Input
     %uint_3 = OpConstant %uint 3
%_arr_float_uint_3 = OpTypeArray %float %uint_3
%_ptr_Function__arr_float_uint_3 = OpTypePointer Function %_arr_float_uint_3
%_arr_v3float_uint_3 = OpTypeArray %v3float %uint_3
%_ptr_Input__arr_v3float_uint_3 = OpTypePointer Input %_arr_v3float_uint_3
       %data = OpVariable %_ptr_Input__arr_v3float_uint_3 Input
  %dataIntrp = OpVariable %_ptr_Input_v3float Input
     %v4uint = OpTypeVector %uint 4
%_ptr_Function_v4uint = OpTypePointer Function %v4uint
        %183 = OpConstantComposite %v4uint %uint_0 %uint_0 %uint_0 %uint_0
      %int_9 = OpConstant %int 9
%_ptr_Function_uint = OpTypePointer Function %uint
%float_0_00100000005 = OpConstant %float 0.00100000005
%_ptr_Output_v4uint = OpTypePointer Output %v4uint
  %out_color = OpVariable %_ptr_Output_v4uint Output
       %main = OpFunction %void None %3
          %5 = OpLabel
          %x = OpVariable %_ptr_Function_int Function
          %y = OpVariable %_ptr_Function_int Function
          %p = OpVariable %_ptr_Function_int Function
          %n = OpVariable %_ptr_Function_int Function
         %eA = OpVariable %_ptr_Function_v3float Function
        %n_0 = OpVariable %_ptr_Function_int Function
         %eB = OpVariable %_ptr_Function_v3float Function
        %n_1 = OpVariable %_ptr_Function_int Function
         %eC = OpVariable %_ptr_Function_v3float Function
          %e = OpVariable %_ptr_Function__arr_float_uint_9 Function
    %eIntrpV = OpVariable %_ptr_Function_v3float Function
     %eIntrp = OpVariable %_ptr_Function__arr_float_uint_3 Function
         %vA = OpVariable %_ptr_Function_v3float Function
         %vB = OpVariable %_ptr_Function_v3float Function
         %vC = OpVariable %_ptr_Function_v3float Function
    %vIntrpV = OpVariable %_ptr_Function_v3float Function
     %vIntrp = OpVariable %_ptr_Function__arr_float_uint_3 Function
          %v = OpVariable %_ptr_Function__arr_float_uint_9 Function
       %mask = OpVariable %_ptr_Function_v4uint Function
          %i = OpVariable %_ptr_Function_int Function
        %i_0 = OpVariable %_ptr_Function_int Function
         %16 = OpAccessChain %_ptr_Input_float %gl_FragCoord %uint_0
         %17 = OpLoad %float %16
         %19 = OpFSub %float %17 %float_0_5
         %20 = OpConvertFToS %int %19
               OpStore %x %20
         %23 = OpAccessChain %_ptr_Input_float %gl_FragCoord %uint_1
         %24 = OpLoad %float %23
         %25 = OpFSub %float %24 %float_0_5
         %26 = OpConvertFToS %int %25
               OpStore %y %26
         %28 = OpLoad %int %x
         %29 = OpLoad %int %y
         %31 = OpSLessThan %bool %28 %29
         %34 = OpSelect %int %31 %int_0 %int_1
               OpStore %p %34
         %37 = OpLoad %int %p
         %38 = OpIMul %int %int_3 %37
         %39 = OpIAdd %int %int_1 %38
               OpStore %n %39
         %43 = OpLoad %int %n
         %44 = OpConvertSToF %float %43
         %46 = OpLoad %int %n
         %47 = OpIMul %int %int_2 %46
         %48 = OpConvertSToF %float %47
         %50 = OpLoad %int %n
         %51 = OpIMul %int %int_4 %50
         %52 = OpConvertSToF %float %51
         %53 = OpCompositeConstruct %v3float %44 %48 %52
               OpStore %eA %53
         %55 = OpLoad %int %p
         %56 = OpIMul %int %int_3 %55
         %57 = OpIAdd %int %56 %int_1
         %58 = OpIAdd %int %int_1 %57
               OpStore %n_0 %58
         %60 = OpLoad %int %n_0
         %61 = OpConvertSToF %float %60
         %62 = OpLoad %int %n_0
         %63 = OpIMul %int %int_2 %62
         %64 = OpConvertSToF %float %63
         %65 = OpLoad %int %n_0
         %66 = OpIMul %int %int_4 %65
         %67 = OpConvertSToF %float %66
         %68 = OpCompositeConstruct %v3float %61 %64 %67
               OpStore %eB %68
         %70 = OpLoad %int %p
         %71 = OpIMul %int %int_3 %70
         %72 = OpIAdd %int %71 %int_2
         %73 = OpIAdd %int %int_1 %72
               OpStore %n_1 %73
         %75 = OpLoad %int %n_1
         %76 = OpConvertSToF %float %75
         %77 = OpLoad %int %n_1
         %78 = OpIMul %int %int_2 %77
         %79 = OpConvertSToF %float %78
         %80 = OpLoad %int %n_1
         %81 = OpIMul %int %int_4 %80
         %82 = OpConvertSToF %float %81
         %83 = OpCompositeConstruct %v3float %76 %79 %82
               OpStore %eC %83
         %89 = OpAccessChain %_ptr_Function_float %eA %uint_0
         %90 = OpLoad %float %89
         %91 = OpAccessChain %_ptr_Function_float %eA %uint_1
         %92 = OpLoad %float %91
         %94 = OpAccessChain %_ptr_Function_float %eA %uint_2
         %95 = OpLoad %float %94
         %96 = OpAccessChain %_ptr_Function_float %eB %uint_0
         %97 = OpLoad %float %96
         %98 = OpAccessChain %_ptr_Function_float %eB %uint_1
         %99 = OpLoad %float %98
        %100 = OpAccessChain %_ptr_Function_float %eB %uint_2
        %101 = OpLoad %float %100
        %102 = OpAccessChain %_ptr_Function_float %eC %uint_0
        %103 = OpLoad %float %102
        %104 = OpAccessChain %_ptr_Function_float %eC %uint_1
        %105 = OpLoad %float %104
        %106 = OpAccessChain %_ptr_Function_float %eC %uint_2
        %107 = OpLoad %float %106
        %108 = OpCompositeConstruct %_arr_float_uint_9 %90 %92 %95 %97 %99 %101 %103 %105 %107
               OpStore %e %108
        %110 = OpLoad %v3float %eA
        %113 = OpAccessChain %_ptr_Input_float %gl_BaryCoordEXT %uint_0
        %114 = OpLoad %float %113
        %115 = OpVectorTimesScalar %v3float %110 %114
        %116 = OpLoad %v3float %eB
        %117 = OpAccessChain %_ptr_Input_float %gl_BaryCoordEXT %uint_1
        %118 = OpLoad %float %117
        %119 = OpVectorTimesScalar %v3float %116 %118
        %120 = OpFAdd %v3float %115 %119
        %121 = OpLoad %v3float %eC
        %122 = OpAccessChain %_ptr_Input_float %gl_BaryCoordEXT %uint_2
        %123 = OpLoad %float %122
        %124 = OpVectorTimesScalar %v3float %121 %123
        %125 = OpFAdd %v3float %120 %124
               OpStore %eIntrpV %125
        %130 = OpAccessChain %_ptr_Function_float %eIntrpV %uint_0
        %131 = OpLoad %float %130
        %132 = OpAccessChain %_ptr_Function_float %eIntrpV %uint_1
        %133 = OpLoad %float %132
        %134 = OpAccessChain %_ptr_Function_float %eIntrpV %uint_2
        %135 = OpLoad %float %134
        %136 = OpCompositeConstruct %_arr_float_uint_3 %131 %133 %135
               OpStore %eIntrp %136
        %141 = OpAccessChain %_ptr_Input_v3float %data %int_0
        %142 = OpLoad %v3float %141
               OpStore %vA %142
        %144 = OpAccessChain %_ptr_Input_v3float %data %int_1
        %145 = OpLoad %v3float %144
               OpStore %vB %145
        %147 = OpAccessChain %_ptr_Input_v3float %data %int_2
        %148 = OpLoad %v3float %147
               OpStore %vC %148
        %151 = OpLoad %v3float %dataIntrp
               OpStore %vIntrpV %151
        %153 = OpAccessChain %_ptr_Function_float %vIntrpV %uint_0
        %154 = OpLoad %float %153
        %155 = OpAccessChain %_ptr_Function_float %vIntrpV %uint_1
        %156 = OpLoad %float %155
        %157 = OpAccessChain %_ptr_Function_float %vIntrpV %uint_2
        %158 = OpLoad %float %157
        %159 = OpCompositeConstruct %_arr_float_uint_3 %154 %156 %158
               OpStore %vIntrp %159
        %161 = OpAccessChain %_ptr_Function_float %vA %uint_0
        %162 = OpLoad %float %161
        %163 = OpAccessChain %_ptr_Function_float %vA %uint_1
        %164 = OpLoad %float %163
        %165 = OpAccessChain %_ptr_Function_float %vA %uint_2
        %166 = OpLoad %float %165
        %167 = OpAccessChain %_ptr_Function_float %vB %uint_0
        %168 = OpLoad %float %167
        %169 = OpAccessChain %_ptr_Function_float %vB %uint_1
        %170 = OpLoad %float %169
        %171 = OpAccessChain %_ptr_Function_float %vB %uint_2
        %172 = OpLoad %float %171
        %173 = OpAccessChain %_ptr_Function_float %vC %uint_0
        %174 = OpLoad %float %173
        %175 = OpAccessChain %_ptr_Function_float %vC %uint_1
        %176 = OpLoad %float %175
        %177 = OpAccessChain %_ptr_Function_float %vC %uint_2
        %178 = OpLoad %float %177
        %179 = OpCompositeConstruct %_arr_float_uint_9 %162 %164 %166 %168 %170 %172 %174 %176 %178
               OpStore %v %179
               OpStore %mask %183
               OpStore %i %int_0
               OpBranch %185
        %185 = OpLabel
               OpLoopMerge %187 %188 None
               OpBranch %189
        %189 = OpLabel
        %190 = OpLoad %int %i
        %192 = OpSLessThan %bool %190 %int_9
               OpBranchConditional %192 %186 %187
        %186 = OpLabel
        %193 = OpLoad %int %i
        %194 = OpAccessChain %_ptr_Function_float %e %193
        %195 = OpLoad %float %194
        %196 = OpLoad %int %i
        %197 = OpAccessChain %_ptr_Function_float %v %196
        %198 = OpLoad %float %197
        %199 = OpFOrdEqual %bool %195 %198
               OpSelectionMerge %201 None
               OpBranchConditional %199 %200 %201
        %200 = OpLabel
        %203 = OpAccessChain %_ptr_Function_uint %mask %uint_0
        %204 = OpLoad %uint %203
        %205 = OpLoad %int %i
        %206 = OpShiftLeftLogical %uint %uint_1 %205
        %207 = OpBitwiseOr %uint %204 %206
        %208 = OpAccessChain %_ptr_Function_uint %mask %uint_0
               OpStore %208 %207
               OpBranch %201
        %201 = OpLabel
               OpBranch %188
        %188 = OpLabel
        %209 = OpLoad %int %i
        %210 = OpIAdd %int %209 %int_1
               OpStore %i %210
               OpBranch %185
        %187 = OpLabel
               OpStore %i_0 %int_0
               OpBranch %212
        %212 = OpLabel
               OpLoopMerge %214 %215 None
               OpBranch %216
        %216 = OpLabel
        %217 = OpLoad %int %i_0
        %218 = OpSLessThan %bool %217 %int_3
               OpBranchConditional %218 %213 %214
        %213 = OpLabel
        %219 = OpLoad %int %i_0
        %220 = OpAccessChain %_ptr_Function_float %eIntrp %219
        %221 = OpLoad %float %220
        %222 = OpLoad %int %i_0
        %223 = OpAccessChain %_ptr_Function_float %vIntrp %222
        %224 = OpLoad %float %223
        %225 = OpFSub %float %221 %224
        %226 = OpExtInst %float %1 FAbs %225
        %228 = OpFOrdLessThan %bool %226 %float_0_00100000005
               OpSelectionMerge %230 None
               OpBranchConditional %228 %229 %230
        %229 = OpLabel
        %231 = OpAccessChain %_ptr_Function_uint %mask %uint_1
        %232 = OpLoad %uint %231
        %233 = OpLoad %int %i_0
        %234 = OpShiftLeftLogical %uint %uint_1 %233
        %235 = OpBitwiseOr %uint %232 %234
        %236 = OpAccessChain %_ptr_Function_uint %mask %uint_1
               OpStore %236 %235
               OpBranch %230
        %230 = OpLabel
               OpBranch %215
        %215 = OpLabel
        %237 = OpLoad %int %i_0
        %238 = OpIAdd %int %237 %int_1
               OpStore %i_0 %238
               OpBranch %212
        %214 = OpLabel
        %241 = OpLoad %v4uint %mask
               OpStore %out_color %241
               OpReturn
               OpFunctionEnd
```

</details>

### Representative Shader Walkthrough 2

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.fragment_shading_barycentric.weights.provoking_first.pipeline_topology_dynamic.single_sample.triangle_list.perspective.vertex_shader
```

| Parameter choice | Meaning in this representative case |
|------------------|--------------------------------------|
| `weights` + `triangle_list` | The test compares a barycentric reconstruction over a triangle. |
| `perspective` | The test shader reads `gl_BaryCoordEXT`, which maps to `BaryCoordKHR`. |
| `single_sample` | The generated GLSL reads `gl_BaryCoordEXT` directly, and the reference uses the corresponding perspective-interpolated color input. |
| `pipeline_topology_dynamic` | The pipeline is created with list-compatible topology and the requested topology is set dynamically before rendering. |

#### Purpose

This shader uses the three barycentric weights to reconstruct the per-vertex color. The host compares that output with a conventional interpolated reference image.

#### Structural Design

| Phase | Shader operation | Expected result |
|------|------------------|-----------------|
| Acquire weights | Read `gl_BaryCoordEXT`. | Get the fragment's perspective barycentric weights. |
| Acquire vertices | Read `in_color[0]`, `in_color[1]`, and `in_color[2]` through `PerVertexKHR`. | Get the colors assigned to the triangle's logical vertices. |
| Reconstruct | Sum each color times its matching weight. | Produce the same color as ordinary interpolation at the selected sample. |
| Store | Write `out_color`. | Produce the image checked against the reference. |

#### Shader Code

```glsl
#version 450
#extension GL_EXT_fragment_shader_barycentric : require

layout(location = 0) pervertexEXT in vec3 in_color[];
layout(location = 0) out vec4 out_color;

void main()
{
    vec3 bc = gl_BaryCoordEXT;
    out_color = vec4(in_color[0] * bc.x + in_color[1] * bc.y + in_color[2] * bc.z, 1.0f);
}
```

#### Additional Info

- The compact code block shows the default built-in path. For `msaa_interpolate_at_sample`, the generator substitutes `interpolateAtSample(gl_BaryCoordEXT, gl_SampleID)`; centroid and offset cases use their corresponding interpolation function. See [`MSAA subtype selection`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2592-L2607).
- `msaa_centroid_qualifier` and `msaa_sample_qualifier` use direct SPIR-V assembly because GLSL cannot add those qualifiers to `gl_BaryCoordEXT` or `gl_BaryCoordNoPerspEXT`. The generated assembly decorates the barycentric built-in with `Centroid` or `Sample`. See [`fragShaderTestSPIRV`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2519-L2586) and [`qualifier branches`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2608-L2618).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Perspective | `gl_BaryCoordEXT` becomes `gl_BaryCoordNoPerspEXT`; the corresponding built-in changes from perspective to linear interpolation. | [`baryCoordVariable`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2473-L2477), [built-in semantics](../../../../vulkan-docs/src/chapters/primsrast.adoc#L2534-L2550) |
| MSAA subtype | Function-call cases evaluate at centroid, sample, or offset; qualifier cases select SPIR-V `Centroid` or `Sample` decoration. | [`MSAA switch`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2592-L2623) |
| Topology | The producer geometry and the logical vertex order change for points, lines, triangles, strips, fans, and adjacency forms. | [`weight vertex generation`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L1001-L1248), [ordering table](../../../../vulkan-docs/src/chapters/primsrast.adoc#L2476-L2492) |
| Mesh producer | The vertex shader path uses vertex input; the mesh path reads a storage buffer and emits `gl_Primitive*IndicesEXT`. | [`generateWeightMeshShader`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2351-L2471), [`weight pipeline setup`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L1328-L1362) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed GLSL from this walkthrough
- Stage: `frag`
- Target SPIRV version: `spirv1.4`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.4
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 51
; Schema: 0
               OpCapability Shader
               OpCapability FragmentBarycentricKHR
               OpExtension "SPV_KHR_fragment_shader_barycentric"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %gl_BaryCoordEXT %out_color %in_color
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 450
               OpSourceExtension "GL_EXT_fragment_shader_barycentric"
               OpName %main "main"
               OpName %bc "bc"
               OpName %gl_BaryCoordEXT "gl_BaryCoordEXT"
               OpName %out_color "out_color"
               OpName %in_color "in_color"
               OpDecorate %gl_BaryCoordEXT BuiltIn BaryCoordKHR
               OpDecorate %out_color Location 0
               OpDecorate %in_color Location 0
               OpDecorate %in_color PerVertexKHR
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v3float = OpTypeVector %float 3
%_ptr_Function_v3float = OpTypePointer Function %v3float
%_ptr_Input_v3float = OpTypePointer Input %v3float
%gl_BaryCoordEXT = OpVariable %_ptr_Input_v3float Input
    %v4float = OpTypeVector %float 4
%_ptr_Output_v4float = OpTypePointer Output %v4float
  %out_color = OpVariable %_ptr_Output_v4float Output
       %uint = OpTypeInt 32 0
     %uint_3 = OpConstant %uint 3
%_arr_v3float_uint_3 = OpTypeArray %v3float %uint_3
%_ptr_Input__arr_v3float_uint_3 = OpTypePointer Input %_arr_v3float_uint_3
   %in_color = OpVariable %_ptr_Input__arr_v3float_uint_3 Input
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
     %uint_0 = OpConstant %uint 0
%_ptr_Function_float = OpTypePointer Function %float
      %int_1 = OpConstant %int 1
     %uint_1 = OpConstant %uint 1
      %int_2 = OpConstant %int 2
     %uint_2 = OpConstant %uint 2
    %float_1 = OpConstant %float 1
       %main = OpFunction %void None %3
          %5 = OpLabel
         %bc = OpVariable %_ptr_Function_v3float Function
         %12 = OpLoad %v3float %gl_BaryCoordEXT
               OpStore %bc %12
         %23 = OpAccessChain %_ptr_Input_v3float %in_color %int_0
         %24 = OpLoad %v3float %23
         %27 = OpAccessChain %_ptr_Function_float %bc %uint_0
         %28 = OpLoad %float %27
         %29 = OpVectorTimesScalar %v3float %24 %28
         %31 = OpAccessChain %_ptr_Input_v3float %in_color %int_1
         %32 = OpLoad %v3float %31
         %34 = OpAccessChain %_ptr_Function_float %bc %uint_1
         %35 = OpLoad %float %34
         %36 = OpVectorTimesScalar %v3float %32 %35
         %37 = OpFAdd %v3float %29 %36
         %39 = OpAccessChain %_ptr_Input_v3float %in_color %int_2
         %40 = OpLoad %v3float %39
         %42 = OpAccessChain %_ptr_Function_float %bc %uint_2
         %43 = OpLoad %float %42
         %44 = OpVectorTimesScalar %v3float %40 %43
         %45 = OpFAdd %v3float %37 %44
         %47 = OpCompositeExtract %float %45 0
         %48 = OpCompositeExtract %float %45 1
         %49 = OpCompositeExtract %float %45 2
         %50 = OpCompositeConstruct %v4float %47 %48 %49 %float_1
               OpStore %out_color %50
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- **Data setup:** The host generates topology-specific positions, creates a host-visible vertex or mesh storage buffer, renders to an `R32G32B32A32_UINT` image, copies the image into a host-visible result buffer, and invalidates the mapped range. Mesh cases bind the storage buffer and issue `cmdDrawMeshTasksEXT`; vertex cases bind the vertex buffer and issue `cmdDraw`. Dynamic indexing pushes `(0, 1, 2)` to the fragment stage. See [`DataTestInstance::iterate`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L811-L965).
- **Data checking:** Each of the `width * height` pixels must equal one expected `tcu::UVec4`. The mask encodes exact per-vertex matches in x, interpolated matches in y, and flat matches in z. Interpolated components use an absolute tolerance of `0.001` in the shader. A nonzero mismatch count logs the expected mask and retrieved image, then returns `Fail`. See [`DataTestInstance::verify`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L722-L773).
- **Weights setup:** The host creates reference and test images, an optional 4x multisampled image with resolve attachment, and two host-visible readback buffers. It renders the conventional reference fragment and barycentric test fragment with the same geometry, rotation matrix, and sample configuration. See [`WeightTestInstance::iterate`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L1289-L1451).
- **Weights checking:** `tcu::intThresholdCompare` compares the reference and result images with `tcu::UVec4(1, 1, 1, 1)`. The case returns `Pass` only when that comparison succeeds; otherwise it returns `Fail`. See [`WeightTestInstance::verify`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L1251-L1265) and [`weight result status`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L1453-L1456).
- **Dimensions:** Data uses 8x8 render targets. Weights uses 128x128 targets and a source slope of `16.0f`; the weight path rotates the geometry by `0`, `85`, or `95` degrees in static-topology cases. See [`test dimensions`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L101-L105) and [`weight vertex generation`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L1001-L1014).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `data` | Incorrect `PerVertexKHR` logical-to-original vertex mapping, provoking-vertex handling, interpolation of the optional inputs, aggregate/type interface handling, or a producer-stage interface mismatch. |
| `weights` | Incorrect `BaryCoordKHR`/`BaryCoordNoPerspKHR` values, sample/centroid/offset evaluation, topology assembly, or mismatch between barycentric and conventional interpolation. |
| `pipeline_library` or `fast_linked_library` construction | A graphics pipeline-library construction or link path fails to preserve the same shader interface or rasterization behavior as the monolithic path. |

### Cause Analysis

#### Per-vertex data propagation

**Possible failure symptoms:** One or more 8x8 pixels lacks an expected bit in the data mask. The x bits cover exact `PerVertexKHR` values; y records interpolated values; z records flat values.

**Possible implementation causes:** The observed symptom can result from a wrong topology-specific vertex mapping, a wrong last-provoking-vertex adjustment, an invalid stage-to-stage interface, or an incorrect interpolation/flat implementation. The test source and the barycentric ordering tables ground these mechanisms, but the test does not identify which implementation layer caused a particular mismatch; further driver, compiler, or hardware investigation is needed.

#### Barycentric weight reconstruction

**Possible failure symptoms:** The reconstructed color image differs from the conventional reference beyond the one-unit-per-channel threshold. Failures may be limited to MSAA sample locations, perspective versus noperspective geometry, or particular primitive topologies.

**Possible implementation causes:** The symptom can arise from incorrect barycentric coordinate generation, sample-location evaluation, primitive assembly, or shader lowering of `PerVertexKHR` and barycentric built-ins. The source comparison isolates the expected relationship, but a failing image alone cannot choose among those causes; source-level and implementation-level investigation is needed.

#### Pipeline-library construction

**Possible failure symptoms:** A case fails only under `pipeline_library` or `fast_linked_library`, while the analogous monolithic case passes, or the failure appears in the same data/weights mask or image comparison under a library root.

**Possible implementation causes:** The library creation, link, or final pipeline state may not preserve the tested fragment input decorations, provoking-vertex state, dynamic topology state, shader-stage interface, or render-pass output behavior. This is a construction-path hypothesis based on the controlled matrix; the exact defect still requires investigation.

## Case Pruning

### Requirement-based pruning

- Every case requires `VK_KHR_fragment_shader_barycentric` and `fragmentShaderBarycentric`. The test calls `checkPipelineConstructionRequirements` for the selected construction type. See [`checkSupport`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L1494-L1509) and [`fragmentShaderBarycentric`](../../../../vulkan-docs/src/chapters/features.adoc#L2498-L2522).
- `provoking_last` requires `VK_EXT_provoking_vertex` and `provokingVertexLast`; dynamic topology requires `VK_EXT_extended_dynamic_state` and `extendedDynamicState`; mesh cases require `VK_EXT_mesh_shader` and `meshShader`. See [`checkSupport`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L1510-L1541).
- Double and double-vector data require core `shaderFloat64`; tessellation and geometry shader-combo leaves require their corresponding core features. Sample interpolation-at-sample and interpolation-at-offset cases require sample-rate shading. See [`checkSupport`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L1543-L1567).
- `data` skips interpolated integer, unsigned-integer, and double data because those inputs must be flat. See [`data` pruning](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2790-L2803).
- Data clipping is implemented only for `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST`; other clipped topology combinations are omitted. See [`clip` pruning](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2764-L2773).
- Mesh producer cases are limited to point, line, and triangle lists. See [`data mesh pruning`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2805-L2816) and [`weights mesh pruning`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L3003-L3017).
- Weight dynamic-topology cases omit mesh shaders because a pre-rasterization mesh-shader pipeline cannot include `VK_DYNAMIC_STATE_PRIMITIVE_TOPOLOGY`; the source comments quote that Vulkan restriction. See [`dynamic weight pruning`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L3016-L3025).

### Design-based pruning

- The matrix intentionally separates `data` from `weights`: data cases stress `PerVertexKHR` transport and typed aggregates, while weights cases stress barycentric coordinates and interpolation positions.
- `weights` uses rotations only in the static-topology branch; dynamic-topology cases instead add the MSAA subtypes and test all line/triangle topologies that the loop classifies as testable. See [`weights branch split`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2972-L3060).
- `misc.pervertex_correctness` and `shader_combos` keep fixed topology and data shape because they target a specific per-vertex interface or stage-chain property rather than the regular matrix. See [`special data leaves`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2863-L2941).
- Although Vulkan defines barycentric values for point, line, and polygon primitives, the implementation's dynamic-topology weight loop deliberately accepts only line or triangle topologies; static-topology cases still include points. See [`testableTopology`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2985-L2994) and [the point, line, and polygon semantics](../../../../vulkan-docs/src/chapters/primsrast.adoc#L2534-L2554).

## Key Takeaways

- `data` validates the logical vertex array exposed by `PerVertexKHR`, not an ordinary interpolated input; its topology and provoking-vertex formulas mirror the Vulkan barycentric ordering rules.
- `weights` validates the built-in coordinates indirectly: if the barycentric-weighted per-vertex color does not match ordinary interpolation, the image comparison fails.
- Mesh, vertex, tessellation, geometry, MSAA, dynamic-topology, and pipeline-library cases change the producer or evaluation path while keeping the same observable contract.
- A skipped case means the selected implementation lacks a required feature or the combination is illegal or intentionally outside the matrix. A failed case means the rendered mask or image violated the specific comparison described above.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `createTests` and registration loops | [`createTests`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2642-L3149) | Defines the hierarchy, construction roots, parameter values, and pruning. |
| `TestParams` | [`TestParams`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L107-L127) | Names the state carried into shader generation, pipeline setup, and checking. |
| `checkSupport` | [`checkSupport`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L1494-L1567) | Defines requirement gates and NotSupported conditions. |
| `initDataPrograms` | [`initDataPrograms`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L1864-L2148) | Generates data producer and fragment shaders, expected values, and masks. |
| `initWeightPrograms` | [`initWeightPrograms`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2473-L2638) | Generates reference/test shaders and the SPIR-V qualifier variants. |
| Data instance and verifier | [`data iterate/verify`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L722-L965) | Builds the 8x8 render/readback path and exact mask check. |
| Weight instance and verifier | [`weight iterate/verify`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L1251-L1456) | Builds the reference/test images and threshold comparison. |
| Barycentric semantics | [Barycentric Interpolation](../../../../vulkan-docs/src/chapters/primsrast.adoc#L2433-L2554) | Defines `PerVertexKHR`, primitive ordering, and barycentric weight values. |
| Feature semantics | [`fragmentShaderBarycentric`](../../../../vulkan-docs/src/chapters/features.adoc#L2498-L2522) | Defines the feature's supported built-ins and decoration. |
| Mustpass coverage | [`fragment-shading-barycentric.txt`](../../../mustpass/main/vk-default/fragment-shading-barycentric.txt#L1-L20991) | Records the 20,991 default executable leaves. |

- **Validation results:** `verify_english_structure.py --files external/vulkancts/wiki/testfiles/fragment_shading_barycentric/Tests.md` passed; `verify_registration_paths.py --wiki-file external/vulkancts/wiki/testfiles/fragment_shading_barycentric/Tests.md` collected 5 paths and passed; `validate_wiki_links.py --wiki-dir external/vulkancts/wiki --files external/vulkancts/wiki/testfiles/fragment_shading_barycentric/Tests.md --repo-root . --verbose` passed with no broken links. The two representative `frag` artifacts compiled with `glslangValidator`, passed `spirv-val`, and disassembled with `spirv-dis` under `spirv1.4`; both report `; Version: 1.4`.
- **Risks:** The walkthrough shaders are reconstructed representatives. The generator has additional branches for all aggregate, topology, stage, MSAA, and pipeline choices; the variation table and source links identify those branches, but the page does not reproduce every generated shader.
- **Risks:** The source's `weights` MSAA qualifier cases use direct SPIR-V, while the second walkthrough's SPIR-V artifact comes from the compact reconstructed GLSL default path. The qualifier-specific assembly remains covered by the source reference and is not presented as the default artifact.
- **Risks:** A passing validator checks structure, registration paths, and links; it does not prove a device run passes. Device-specific failures still require CTS execution and implementation investigation.
