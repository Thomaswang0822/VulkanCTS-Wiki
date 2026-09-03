## Overview

**Core question:** Does an implementation that exposes `VK_EXT_mesh_shader` report legal property values and execute mesh or task shaders at the boundary sizes derived from those values?

- [`vktMeshShaderPropertyTestsEXT.cpp`](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTestsEXT.cpp#L2429-L2543) registers the `properties` test family and implements its limit, payload, shared-memory, multiview, layer, output-count, output-component, and output-memory checks.
- The source contains one query-only child, `limits`, and shader-backed children that use device properties to choose legal specialization-constant sizes and output budgets.
- The Vulkan default mustpass contains 30 exact leaves for this family at [`mesh-shader.txt`](../../../mustpass/main/vk-default/mesh-shader.txt#L2025-L2054).

## Background Knowledge

- `VkPhysicalDeviceMeshShaderPropertiesEXT` reports task and mesh workgroup dimensions, payload and shared-memory budgets, output counts, output components, layers, multiview count, and output-allocation granularities. The structure is queried as part of the physical-device properties chain. See [`VkPhysicalDeviceMeshShaderPropertiesEXT`](../../../../vulkan-docs/src/chapters/limits.adoc#L2325-L2469).
- Mesh output storage depends on effective scalar attributes, maximum vertex and primitive counts, view-dependent attributes, and the per-vertex and per-primitive allocation granularities. Vulkan defines the calculation in [`Mesh Shader Output`](../../../../vulkan-docs/src/chapters/VK_NV_mesh_shader/mesh.adoc#L150-L198).
- Multiview mesh rendering needs both the core `multiview` feature and `multiviewMeshShader`. The feature dependency appears in [`features.adoc`](../../../../vulkan-docs/src/chapters/features.adoc#L1860-L1900).

## Registration Hierarchy

```text
mesh_shader.ext.properties
├── limits
├── task_payload_size
├── task_shared_memory_size
├── task_payload_and_shared_memory_size
├── max_view_index
├── max_output_layers
├── max_mesh_output_primitives_256
├── max_mesh_output_vertices_256
├── max_mesh_output_primitives_512
├── max_mesh_output_vertices_512
├── max_mesh_output_primitives_1024
├── max_mesh_output_vertices_1024
├── max_mesh_output_primitives_2048
├── max_mesh_output_vertices_2048
├── max_mesh_output_components
├── mesh_payload_size
├── mesh_shared_memory_size
├── mesh_payload_and_shared_memory_size
├── max_mesh_output_size_without_payload_per_primitive_no_view_index
├── max_mesh_output_size_without_payload_per_primitive_view_index_in_frag
├── max_mesh_output_size_without_payload_per_primitive_view_index_in_mesh_and_frag
├── max_mesh_output_size_without_payload_per_vertex_no_view_index
├── max_mesh_output_size_without_payload_per_vertex_view_index_in_frag
├── max_mesh_output_size_without_payload_per_vertex_view_index_in_mesh_and_frag
├── max_mesh_output_size_with_payload_per_primitive_no_view_index
├── max_mesh_output_size_with_payload_per_primitive_view_index_in_frag
├── max_mesh_output_size_with_payload_per_primitive_view_index_in_mesh_and_frag
├── max_mesh_output_size_with_payload_per_vertex_no_view_index
├── max_mesh_output_size_with_payload_per_vertex_view_index_in_frag
└── max_mesh_output_size_with_payload_per_vertex_view_index_in_mesh_and_frag
```

The `mesh_shader` test category reaches this family through its `ext` branch and the `properties` test family. The factory creates `limits` first, then the explicit payload/shared-memory and fixed-property children, the primitive/vertex count loops, and the 18-case output-size matrix in [`createMeshShaderPropertyTestsEXT`](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTestsEXT.cpp#L2429-L2543). The mustpass file confirms the 30 executable leaves listed above.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Query validation | `limits` | Checks EXT property minima and the maximum permitted output granularities. | [`limitsRun`](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTestsEXT.cpp#L2345-L2425) |
| Task payload/shared-memory mode | `task_payload_size`, `task_shared_memory_size`, `task_payload_and_shared_memory_size` | Selects payload only, shared memory only, or a combined task-stage allocation. | [`taskPayloadShMemCases`](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTestsEXT.cpp#L2438-L2452) |
| Fixed mesh property probes | `max_view_index`, `max_output_layers`, `max_mesh_output_components` | Exercises multiview indexing, layered output, or the maximum interface-component budget. | [`MaxViewIndexCase`](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTestsEXT.cpp#L530-L802), [`MaxOutputLayersCase`](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTestsEXT.cpp#L804-L1016), [`MaxMeshOutputComponentsCase`](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTestsEXT.cpp#L1293-L1556) |
| Primitive output count | `max_mesh_output_primitives_256`, `_512`, `_1024`, `_2048` | Uses points and a fragment SSBO flag for each requested primitive. | [`limitPrimVertCases`](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTestsEXT.cpp#L2457-L2475) |
| Vertex output count | `max_mesh_output_vertices_256`, `_512`, `_1024`, `_2048` | Uses one point per output vertex and a wide framebuffer so each vertex reaches a distinct fragment coordinate. | [`MaxMeshOutputPrimVertCase::initPrograms`](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTestsEXT.cpp#L1122-L1197) |
| Mesh payload/shared-memory mode | `mesh_payload_size`, `mesh_shared_memory_size`, `mesh_payload_and_shared_memory_size` | Selects mesh payload only, shared memory only, or both. `mesh_payload_size` combines the two payload-related limits rather than naming one property field. | [`meshPayloadShMemCases`](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTestsEXT.cpp#L2480-L2493) |
| Output payload mode | `_without_payload`, `_with_payload` | Removes or adds a task payload and changes the available mesh output budget. | [`meshOutputPayloadCases`](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTestsEXT.cpp#L2496-L2503) |
| Output location qualifier | `_per_primitive`, `_per_vertex` | Allocates the generated `uvec4` interface block per primitive or per vertex, using the corresponding granularity. | [`locationTypeCases`](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTestsEXT.cpp#L2505-L2512) |
| View-index dependency | `_no_view_index`, `_view_index_in_frag`, `_view_index_in_mesh_and_frag` | Selects no view-dependent values, fragment-only view dependence, or view dependence in both mesh and fragment shaders. | [`multiviewCases`](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTestsEXT.cpp#L2514-L2522) |
| Output-size matrix | 18 combinations of the preceding three dimensions | Derives payload bytes and interface locations from the queried output-memory, payload, component, and granularity properties, then fills the budget with a 96-point mesh output. | [`MaxMeshOutputSizeCase::getParamsFromContext`](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTestsEXT.cpp#L1900-L1989) |

The EXT property block groups the dimensions by stage: task and mesh workgroup total counts, per-axis workgroup counts, invocation counts, and per-axis local sizes; task payload/shared-memory limits; mesh shared-memory, payload/shared-memory, output-memory, and payload/output-memory limits; output components, vertices, primitives, layers, and multiview count; and per-vertex/per-primitive output granularities. `limits` checks the task fields only when `features.taskShader` is true and the mesh fields only when `features.meshShader` is true. It checks minima from the Vulkan table, while both output granularities use the source's maximum checks.

The EXT required values include task and mesh workgroup invocation minima of `128`, workgroup-size minima of `(128,128,128)`, payload/shared-memory minima of `16384`, `32768`, and `28672` bytes as applicable, output-memory minima of `32768` and `48128` bytes, `128` output components, `256` output vertices and primitives, `8` output layers, and output granularities no greater than `32`. The complete table is in [`limits.adoc`](../../../../vulkan-docs/src/chapters/limits.adoc#L6873-L6902).

## Behavior Parameters

The primary behavioral axis is the registered test case leaf. Each leaf selects either a direct query or a shader-backed boundary property. The output-size leaves have three secondary dimensions: payload mode, location qualifier, and view-index dependency.

### `limits` | property-range query

`limitsRun` checks only fields relevant to enabled task and mesh features. It applies minimum checks to workgroup counts, invocations, sizes, memory, output components, vertices, primitives, and layers. It applies maximum checks to `meshOutputPerVertexGranularity` and `meshOutputPerPrimitiveGranularity`.

### `task_payload_size`, `task_shared_memory_size`, and `task_payload_and_shared_memory_size` | task-stage allocation

The source derives element counts from `maxTaskPayloadSize`, `maxTaskSharedMemorySize`, `maxTaskPayloadAndSharedMemorySize`, and the mesh payload constraints. The `PAYLOAD` variant uses payload and sets shared-memory elements to zero. The `SHARED_MEMORY` variant does the reverse. The `BOTH` variant divides the combined budget between both allocations, limited by each individual maximum.

The generated task shader fills `taskPayloadSharedEXT` with `i + 2000`. When shared memory is selected, invocations write `i * 2 + 1000`, synchronize, update reversed indices, synchronize again, and let invocation zero check for `i * 3 + 1000`. The mesh shader checks the payload and emits no primitives.

### `max_view_index` | maximum usable multiview count

The case uses the smaller of `maxMeshMultiviewViewCount` and `32` as its view count. The mesh shader emits one triangle. The fragment shader writes `gl_ViewIndex + 1` into the red channel. The host reads every pixel in every view and expects `(view + 1, 0, 0, 1)`. A device that advertises more than 32 views receives a quality warning after the capped probe passes.

### `max_output_layers` | layered mesh output

The case chooses the usable layer count as the minimum of `maxFramebufferLayers`, `maxMeshOutputLayers`, the image-format array-layer limit, and `maxMeshWorkGroupCount[0]`. It launches one mesh workgroup per layer, writes `gl_Layer = gl_WorkGroupID.x`, and expects the read-back layer `z` to contain `z + 1` in red.

### `max_mesh_output_primitives_256`, `_512`, `_1024`, and `_2048` | primitive count

The mesh shader uses `layout (points) out`, sets `max_primitives` to the selected count, and writes one point index per primitive. For this variant, `gl_PrimitiveID` identifies the output flag that the fragment shader sets to `1`. The host requires every flag to equal `1`.

### `max_mesh_output_vertices_256`, `_512`, `_1024`, and `_2048` | vertex count

The mesh shader emits the selected number of point vertices and maps each vertex to one pixel in a wide framebuffer. The fragment shader uses `gl_FragCoord.x` to set the corresponding SSBO flag. The support check limits the request by both vertex and primitive limits because point output consumes one primitive per vertex.

### `max_mesh_output_components` | interface component budget

The case subtracts one location for `gl_Position` from `maxMeshOutputComponents / 4` and uses the remaining locations as a specialization constant. The mesh shader writes a per-primitive `uvec4` array. The fragment shader compares every received vector with the encoded expected value and writes blue only when all locations match.

### `mesh_payload_size`, `mesh_shared_memory_size`, and `mesh_payload_and_shared_memory_size` | mesh-stage allocation

These variants derive payload and shared-memory element counts from the mesh-stage properties. A selected payload is written by the task shader and checked by the mesh shader. A selected shared array is written, updated across barriers, and checked by mesh invocation zero. The mesh-only shared-memory case has no task shader.

### `max_mesh_output_size_*` | output-memory boundary

Each output-size case emits `96` points and specializes `payloadElements` and `locationCount`. The source reserves the built-in `gl_Position` and `gl_PointSize` storage, rounds the point count by the chosen output granularity, and divides view-independent or view-dependent output according to the selected view mode. The mesh shader writes encoded `uvec4` values. The fragment shader checks the interface and writes blue for success.

## Shader Analysis

The output-size cases use generated mesh and fragment shaders, and their output-memory calculation is the page's central shader-backed behavior. One walkthrough covers the no-payload, per-primitive, no-view-index branch. The other output-size branches change declarations or value expressions and are summarized afterward.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.mesh_shader.ext.properties.max_mesh_output_size_without_payload_per_primitive_no_view_index
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `without_payload` | Leaves `payloadElements` at zero and uses the mesh output-memory limit without task payload storage. |
| `per_primitive` | Declares `LocationBlock` with the `perprimitiveEXT` qualifier and uses `meshOutputPerPrimitiveGranularity`. |
| `no_view_index` | Keeps output values independent of `gl_ViewIndex`, so the output-memory formula uses one view. |
| `locationCount` | Specializes the number of `uvec4` locations derived from output-memory and component limits. |

#### Purpose

The mesh shader fills the available output-memory shape with per-primitive interface values. The fragment shader confirms that the values survive mesh-to-fragment transport at every generated location.

#### Structural Design

| Phase | Operation | Observable result |
|-------|-----------|-------------------|
| Output allocation | `SetMeshOutputsEXT(96u, 96u)` emits 96 point primitives and vertices. | The test exercises the selected output count and granularity. |
| Interface write | Each point writes `locationCount` encoded `uvec4` values to `loc[pointIdx]`. | Each primitive carries a distinct value for every location. |
| Rasterization | Point positions spread across a 96-pixel-wide framebuffer. | Each point reaches a known fragment coordinate. |
| Interface check | The fragment shader reconstructs the expected values and chooses blue or black. | Blue means all interface values matched. |

#### Shader Code

```glsl
#version 450
#extension GL_EXT_mesh_shader : enable

/// One mesh invocation emits the complete fixed test output.
layout (local_size_x=1, local_size_y=1, local_size_z=1) in;
layout (points) out;
layout (max_vertices=96, max_primitives=96) out;

/// Built-in output storage participates in the output-memory calculation.
out gl_MeshPerVertexEXT {
    vec4 gl_Position;
    float gl_PointSize;
} gl_MeshVerticesEXT[];

/// The host specializes this array length from EXT output properties.
layout (constant_id=1) const uint locationCount = 1u;
struct LocationBlock {
    uvec4 elements[locationCount];
};
/// Per-primitive locations use the primitive allocation granularity.
layout (location=0) out perprimitiveEXT LocationBlock loc[];

void main (void) {
    SetMeshOutputsEXT(96u, 96u);
    /// With no task payload, payloadOK remains true and the generator still uses its success offset.
    bool payloadOK = true;
    const uint payloadOffset = (payloadOK ? 10u : 0u);
    const uint compOffset = 0u;
    for (uint pointIdx = 0u; pointIdx < 96u; ++pointIdx) {
        const float xCoord = ((float(pointIdx) + 0.5) / float(96u)) * 2.0 - 1.0;
        gl_MeshVerticesEXT[pointIdx].gl_Position = vec4(xCoord, 0.0, 0.0, 1.0);
        gl_MeshVerticesEXT[pointIdx].gl_PointSize = 1.0f;
        gl_PrimitivePointIndicesEXT[pointIdx] = pointIdx;
        for (uint elemIdx = 0u; elemIdx < locationCount; ++elemIdx) {
            const uint baseVal = 200000000u + 100000u * pointIdx + 1000u * elemIdx + payloadOffset;
            loc[pointIdx].elements[elemIdx] = uvec4(baseVal + 1u + compOffset, baseVal + 2u + compOffset, baseVal + 3u + compOffset, baseVal + 4u + compOffset);
        }
    }
}
```

#### Additional Info

- The original generator initializes `payloadOK` to `true` even when no task payload is present, so this no-payload branch still uses `payloadOffset = 10u`; the fragment shader expects the same offset.
- The fragment shader reads the matching flat per-primitive `LocationBlock`, compares each `uvec4`, and writes blue on success. The host compares the copied image with blue at every pixel.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|-----------------------------------------|----------|
| Payload mode | `_with_payload` adds a task shader, specializes `payloadElements`, checks `taskPayloadSharedEXT`, and uses payload offset `10u` when the check succeeds. | [`MaxMeshOutputSizeCase::initPrograms`](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTestsEXT.cpp#L2001-L2044) |
| Location qualifier | `_per_vertex` removes `perprimitiveEXT` and uses the per-vertex allocation granularity. | [`locationQualifier`](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTestsEXT.cpp#L2001-L2006) |
| View-index mode | Fragment-only mode enables multiview in the fragment shader; mesh-and-fragment mode also enables it in the mesh shader and offsets values by `4 * gl_ViewIndex`. | [`viewIndexInMesh`](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTestsEXT.cpp#L2046-L2052), [`multiViewExt`](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTestsEXT.cpp#L2089-L2092) |
| Derived location count | `locationCount` is computed from output bytes, built-in output storage, granularity, view factor, and the component limit. | [`MaxMeshOutputSizeCase::getParamsFromContext`](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTestsEXT.cpp#L1920-L1989) |

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
; Bound: 118
; Schema: 0
               OpCapability MeshShadingEXT
               OpExtension "SPV_EXT_mesh_shader"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint MeshEXT %main "main" %gl_MeshVerticesEXT %gl_PrimitivePointIndicesEXT %loc
               OpExecutionMode %main LocalSize 1 1 1
               OpExecutionMode %main OutputVertices 96
               OpExecutionMode %main OutputPrimitivesEXT 96
               OpExecutionMode %main OutputPoints
               OpSource GLSL 450
               OpSourceExtension "GL_EXT_mesh_shader"
               OpName %main "main"
               OpName %payloadOK "payloadOK"
               OpName %payloadOffset "payloadOffset"
               OpName %pointIdx "pointIdx"
               OpName %xCoord "xCoord"
               OpName %gl_MeshPerVertexEXT "gl_MeshPerVertexEXT"
               OpMemberName %gl_MeshPerVertexEXT 0 "gl_Position"
               OpMemberName %gl_MeshPerVertexEXT 1 "gl_PointSize"
               OpName %gl_MeshVerticesEXT "gl_MeshVerticesEXT"
               OpName %gl_PrimitivePointIndicesEXT "gl_PrimitivePointIndicesEXT"
               OpName %elemIdx "elemIdx"
               OpName %locationCount "locationCount"
               OpName %baseVal "baseVal"
               OpName %LocationBlock "LocationBlock"
               OpMemberName %LocationBlock 0 "elements"
               OpName %loc "loc"
               OpName %payloadElements "payloadElements"
               OpDecorate %gl_MeshPerVertexEXT Block
               OpMemberDecorate %gl_MeshPerVertexEXT 0 BuiltIn Position
               OpMemberDecorate %gl_MeshPerVertexEXT 1 BuiltIn PointSize
               OpDecorate %gl_PrimitivePointIndicesEXT BuiltIn PrimitivePointIndicesEXT
               OpDecorate %locationCount SpecId 1
               OpDecorate %loc Location 0
               OpDecorate %loc PerPrimitiveEXT
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
               OpDecorate %payloadElements SpecId 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %bool = OpTypeBool
%_ptr_Function_bool = OpTypePointer Function %bool
       %true = OpConstantTrue %bool
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
    %uint_10 = OpConstant %uint 10
     %uint_0 = OpConstant %uint 0
    %uint_96 = OpConstant %uint 96
      %float = OpTypeFloat 32
%_ptr_Function_float = OpTypePointer Function %float
  %float_0_5 = OpConstant %float 0.5
   %float_96 = OpConstant %float 96
    %float_2 = OpConstant %float 2
    %float_1 = OpConstant %float 1
    %v4float = OpTypeVector %float 4
%gl_MeshPerVertexEXT = OpTypeStruct %v4float %float
%_arr_gl_MeshPerVertexEXT_uint_96 = OpTypeArray %gl_MeshPerVertexEXT %uint_96
%_ptr_Output__arr_gl_MeshPerVertexEXT_uint_96 = OpTypePointer Output %_arr_gl_MeshPerVertexEXT_uint_96
%gl_MeshVerticesEXT = OpVariable %_ptr_Output__arr_gl_MeshPerVertexEXT_uint_96 Output
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
    %float_0 = OpConstant %float 0
%_ptr_Output_v4float = OpTypePointer Output %v4float
      %int_1 = OpConstant %int 1
%_ptr_Output_float = OpTypePointer Output %float
%_arr_uint_uint_96 = OpTypeArray %uint %uint_96
%_ptr_Output__arr_uint_uint_96 = OpTypePointer Output %_arr_uint_uint_96
%gl_PrimitivePointIndicesEXT = OpVariable %_ptr_Output__arr_uint_uint_96 Output
%_ptr_Output_uint = OpTypePointer Output %uint
%locationCount = OpSpecConstant %uint 1
%uint_200000000 = OpConstant %uint 200000000
%uint_100000 = OpConstant %uint 100000
  %uint_1000 = OpConstant %uint 1000
     %v4uint = OpTypeVector %uint 4
%_arr_v4uint_locationCount = OpTypeArray %v4uint %locationCount
%LocationBlock = OpTypeStruct %_arr_v4uint_locationCount
%_arr_LocationBlock_uint_96 = OpTypeArray %LocationBlock %uint_96
%_ptr_Output__arr_LocationBlock_uint_96 = OpTypePointer Output %_arr_LocationBlock_uint_96
        %loc = OpVariable %_ptr_Output__arr_LocationBlock_uint_96 Output
     %uint_1 = OpConstant %uint 1
     %uint_2 = OpConstant %uint 2
     %uint_3 = OpConstant %uint 3
     %uint_4 = OpConstant %uint 4
%_ptr_Output_v4uint = OpTypePointer Output %v4uint
     %v3uint = OpTypeVector %uint 3
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
%payloadElements = OpSpecConstant %uint 1
       %main = OpFunction %void None %3
          %5 = OpLabel
  %payloadOK = OpVariable %_ptr_Function_bool Function
%payloadOffset = OpVariable %_ptr_Function_uint Function
   %pointIdx = OpVariable %_ptr_Function_uint Function
     %xCoord = OpVariable %_ptr_Function_float Function
    %elemIdx = OpVariable %_ptr_Function_uint Function
    %baseVal = OpVariable %_ptr_Function_uint Function
               OpStore %payloadOK %true
         %13 = OpLoad %bool %payloadOK
         %16 = OpSelect %uint %13 %uint_10 %uint_0
               OpStore %payloadOffset %16
               OpSetMeshOutputsEXT %uint_96 %uint_96
               OpStore %pointIdx %uint_0
               OpBranch %19
         %19 = OpLabel
               OpLoopMerge %21 %22 None
               OpBranch %23
         %23 = OpLabel
         %24 = OpLoad %uint %pointIdx
         %25 = OpULessThan %bool %24 %uint_96
               OpBranchConditional %25 %20 %21
         %20 = OpLabel
         %29 = OpLoad %uint %pointIdx
         %30 = OpConvertUToF %float %29
         %32 = OpFAdd %float %30 %float_0_5
         %34 = OpFDiv %float %32 %float_96
         %36 = OpFMul %float %34 %float_2
         %38 = OpFSub %float %36 %float_1
               OpStore %xCoord %38
         %44 = OpLoad %uint %pointIdx
         %47 = OpLoad %float %xCoord
         %49 = OpCompositeConstruct %v4float %47 %float_0 %float_0 %float_1
         %51 = OpAccessChain %_ptr_Output_v4float %gl_MeshVerticesEXT %44 %int_0
               OpStore %51 %49
         %52 = OpLoad %uint %pointIdx
         %55 = OpAccessChain %_ptr_Output_float %gl_MeshVerticesEXT %52 %int_1
               OpStore %55 %float_1
         %59 = OpLoad %uint %pointIdx
         %60 = OpLoad %uint %pointIdx
         %62 = OpAccessChain %_ptr_Output_uint %gl_PrimitivePointIndicesEXT %59
               OpStore %62 %60
               OpStore %elemIdx %uint_0
               OpBranch %64
         %64 = OpLabel
               OpLoopMerge %66 %67 None
               OpBranch %68
         %68 = OpLabel
         %69 = OpLoad %uint %elemIdx
         %71 = OpULessThan %bool %69 %locationCount
               OpBranchConditional %71 %65 %66
         %65 = OpLabel
         %75 = OpLoad %uint %pointIdx
         %76 = OpIMul %uint %uint_100000 %75
         %77 = OpIAdd %uint %uint_200000000 %76
         %79 = OpLoad %uint %elemIdx
         %80 = OpIMul %uint %uint_1000 %79
         %81 = OpIAdd %uint %77 %80
         %82 = OpLoad %uint %payloadOffset
         %83 = OpIAdd %uint %81 %82
               OpStore %baseVal %83
         %90 = OpLoad %uint %pointIdx
         %91 = OpLoad %uint %elemIdx
         %92 = OpLoad %uint %baseVal
         %94 = OpIAdd %uint %92 %uint_1
         %95 = OpIAdd %uint %94 %uint_0
         %96 = OpLoad %uint %baseVal
         %98 = OpIAdd %uint %96 %uint_2
         %99 = OpIAdd %uint %98 %uint_0
        %100 = OpLoad %uint %baseVal
        %102 = OpIAdd %uint %100 %uint_3
        %103 = OpIAdd %uint %102 %uint_0
        %104 = OpLoad %uint %baseVal
        %106 = OpIAdd %uint %104 %uint_4
        %107 = OpIAdd %uint %106 %uint_0
        %108 = OpCompositeConstruct %v4uint %95 %99 %103 %107
        %110 = OpAccessChain %_ptr_Output_v4uint %loc %90 %int_0 %91
               OpStore %110 %108
               OpBranch %67
         %67 = OpLabel
        %111 = OpLoad %uint %elemIdx
        %112 = OpIAdd %uint %111 %int_1
               OpStore %elemIdx %112
               OpBranch %64
         %66 = OpLabel
               OpBranch %22
         %22 = OpLabel
        %113 = OpLoad %uint %pointIdx
        %114 = OpIAdd %uint %113 %int_1
               OpStore %pointIdx %114
               OpBranch %19
         %21 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- Every shader-backed case calls [`checkTaskMeshShaderSupportEXT`](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L126-L139), which requires `VK_EXT_mesh_shader` and whichever task and mesh stages that case uses. The source also requires `vertexPipelineStoresAndAtomics` for payload/shared-memory result buffers and `fragmentStoresAndAtomics` for primitive and vertex output-count cases.
- `limits` uses the same extension and mesh-feature gate, then checks values returned by `context.getMeshShaderFeaturesEXT()` and `context.getMeshShaderPropertiesEXT()`. A property below a required minimum or above an allowed granularity is a conformance failure through `TCU_FAIL`, not a support skip.
- Payload and shared-memory cases derive element counts from queried byte limits. The generated shaders use 128 local invocations, write known sequences, synchronize shared-memory operations with `memoryBarrierShared()` and `barrier()`, and store `sharedOK` and `payloadOK` in a host-visible storage buffer.
- Layer and output-size cases create color attachments and copy them to host-visible verification buffers after a transfer barrier. The host compares every pixel with the expected layer, view, or success color.
- Primitive and vertex output-count cases write one flag per expected output to an SSBO. The host scans every flag and fails when any flag differs from `1`.
- Graphics submissions use `vkCmdDrawMeshTasksEXT`. A task shader appears only when the selected case needs task payload or task shared memory. The output-size task path uses one task workgroup and the mesh path emits the 96-point output.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `limits` | The implementation reported an EXT property below a required minimum or above an allowed granularity maximum. |
| `task_payload_size` | Task payload allocation or task-to-mesh payload transport failed at the size derived from the reported limits. |
| `task_shared_memory_size` | Task-stage shared-memory allocation, barriers, or value updates failed at the derived size. |
| `task_payload_and_shared_memory_size` | The combined task payload/shared-memory budget or either data path failed. |
| `max_view_index` | Multiview rendering or `gl_ViewIndex` output failed for the tested view count. |
| `max_output_layers` | Layered mesh output, framebuffer-layer selection, or `gl_Layer` handling failed at the usable layer count. |
| `max_mesh_output_primitives_256`, `max_mesh_output_primitives_512`, `max_mesh_output_primitives_1024`, `max_mesh_output_primitives_2048` | After support checks pass, primitive output/indexing failed at the requested count; a count above the advertised limit is a support skip, not a failure. |
| `max_mesh_output_vertices_256`, `max_mesh_output_vertices_512`, `max_mesh_output_vertices_1024`, `max_mesh_output_vertices_2048` | After support checks pass, vertex output/rasterization failed at the requested count; a count above the advertised vertex or primitive limit is a support skip, not a failure. |
| `max_mesh_output_components` | Mesh output-component allocation or per-primitive interface transport failed at the derived location count. |
| `mesh_payload_size` | The mesh payload/output or payload/shared-memory budget did not support the generated payload path. |
| `mesh_shared_memory_size` | Mesh-stage shared-memory allocation, barriers, or value updates failed at the derived size. |
| `mesh_payload_and_shared_memory_size` | The combined mesh payload/shared-memory budget or either data path failed. |
| `max_mesh_output_size_without_payload_per_primitive_no_view_index` | The selected payload, output location, view-index dependency, or output-memory calculation did not produce the expected interface values and color. |
| `max_mesh_output_size_without_payload_per_primitive_view_index_in_frag` | The selected payload, output location, view-index dependency, or output-memory calculation did not produce the expected interface values and color. |
| `max_mesh_output_size_without_payload_per_primitive_view_index_in_mesh_and_frag` | The selected payload, output location, view-index dependency, or output-memory calculation did not produce the expected interface values and color. |
| `max_mesh_output_size_without_payload_per_vertex_no_view_index` | The selected payload, output location, view-index dependency, or output-memory calculation did not produce the expected interface values and color. |
| `max_mesh_output_size_without_payload_per_vertex_view_index_in_frag` | The selected payload, output location, view-index dependency, or output-memory calculation did not produce the expected interface values and color. |
| `max_mesh_output_size_without_payload_per_vertex_view_index_in_mesh_and_frag` | The selected payload, output location, view-index dependency, or output-memory calculation did not produce the expected interface values and color. |
| `max_mesh_output_size_with_payload_per_primitive_no_view_index` | The selected payload, output location, view-index dependency, or output-memory calculation did not produce the expected interface values and color. |
| `max_mesh_output_size_with_payload_per_primitive_view_index_in_frag` | The selected payload, output location, view-index dependency, or output-memory calculation did not produce the expected interface values and color. |
| `max_mesh_output_size_with_payload_per_primitive_view_index_in_mesh_and_frag` | The selected payload, output location, view-index dependency, or output-memory calculation did not produce the expected interface values and color. |
| `max_mesh_output_size_with_payload_per_vertex_no_view_index` | The selected payload, output location, view-index dependency, or output-memory calculation did not produce the expected interface values and color. |
| `max_mesh_output_size_with_payload_per_vertex_view_index_in_frag` | The selected payload, output location, view-index dependency, or output-memory calculation did not produce the expected interface values and color. |
| `max_mesh_output_size_with_payload_per_vertex_view_index_in_mesh_and_frag` | The selected payload, output location, view-index dependency, or output-memory calculation did not produce the expected interface values and color. |

### Cause Analysis

#### Property query outside the required range

**Possible failure symptoms:** `limits` logs one or more property names with values below the minimum or above the maximum and then fails.

**Possible implementation causes:** The physical-device property chain returned a value outside the EXT limits table, or the implementation supplied an inconsistent feature/property combination. The exact query path needs source-level investigation if the reported value cannot be reproduced independently.

#### Unsupported stage or multiview feature

**Possible failure symptoms:** The test returns `NotSupportedError` before shader execution when `VK_EXT_mesh_shader`, a required task or mesh feature, `multiview`, or `multiviewMeshShader` is unavailable.

**Possible implementation causes:** The device does not expose the feature required by that registered case. This result is a support skip, not evidence that the property value or shader behavior failed.

#### Payload or shared-memory validation failure

**Possible failure symptoms:** The host-visible result buffer contains `sharedOK` or `payloadOK` different from `1`, after the generated task or mesh shaders ran.

**Possible implementation causes:** The selected stage may have allocated the wrong payload/shared-memory size, transported task payload incorrectly, or mishandled shared-memory writes, barriers, or visibility. The generated shader and failing stage need source-level investigation for a more specific cause.

#### Output count, layer, view, or interface mismatch

**Possible failure symptoms:** The host finds a wrong SSBO flag, unexpected layer/view pixel, black output-size pixel, or a component value that differs from the expected encoding.

**Possible implementation causes:** Mesh output count or index generation, `gl_Layer`, `gl_ViewIndex`, output allocation, or mesh-to-fragment interface transport produced a wrong value. The source check identifies the observable mismatch but does not assign the defect to hardware, compiler, or host without further investigation.

#### Common submission and readback failure

**Possible failure symptoms:** Several unrelated cases return untouched or incorrect buffer values, or image comparisons fail at their first copied pixel.

**Possible implementation causes:** Descriptor binding, pipeline construction, command submission, shader-write barriers, image-to-buffer transfer, host invalidation, or result decoding may have failed in the shared runtime path. Cross-case comparison helps separate this cause from one property-specific failure.

## Case Pruning

### Requirement-based pruning

- The common helper skips a case when `VK_EXT_mesh_shader` is unavailable or when the selected task or mesh feature is not present.
- Multiview cases require `multiview`, `multiviewMeshShader`, and a sufficient `maxMeshMultiviewViewCount`. The `max_view_index` probe caps execution at 32 views and returns a quality warning when the advertised count exceeds that cap.
- Output-count cases skip when the requested count exceeds the relevant output property. Vertex cases also use `maxMeshOutputPrimitives` because point output needs one primitive per vertex.
- Output-count cases skip when the calculated output bytes exceed `maxMeshOutputMemorySize`.
- These skips mean the current implementation cannot support the selected legal shader shape. In contrast, `limits` uses `TCU_FAIL` for an exposed property outside Vulkan's required range.

### Design-based pruning

- The source uses the fixed primitive and vertex counts `256`, `512`, `1024`, and `2048`; it does not generate every value between them.
- The output-size matrix has 18 leaves from two payload modes, two location qualifiers, and three view-index modes. The dimensions cover changes to the output-memory equation and shader interface without duplicating ordinary values.
- The source derives payload and location counts from device properties rather than attempting to allocate every advertised maximum independently. It reserves built-in output storage and respects granularity and view factors.
- The `mesh_payload_size` name intentionally represents the intersection of payload-related constraints; the source comment notes that it has no single corresponding property field.
- `max_view_index` uses at most 32 views so the read-back image and render-pass view mask remain bounded. A larger device value is reported through the quality-warning result instead of adding more registered leaves.

## Key Takeaways

- The `properties` family has 30 exact mustpass leaves. `limits` checks the property contract; the remaining leaves use the queried limits to drive executable boundary probes.
- Task payload, shared memory, output counts, layers, components, and output-memory size use different shader and host checks. A single generic pass rule would hide those distinctions.
- A missing required feature or an unsupported derived shape skips the case. A property reported outside the Vulkan-required range fails the limits case.
- The output-size matrix tests the interaction between payload bytes, built-in output storage, location qualifiers, allocation granularity, and view-dependent attributes.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| EXT property registration | [`createMeshShaderPropertyTestsEXT`](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTestsEXT.cpp#L2429-L2543) | Builds the `properties` family and all 30 leaves. |
| EXT support helper | [`checkTaskMeshShaderSupportEXT`](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L126-L139) | Requires the extension and selected task/mesh features. |
| Query-only limits check | [`limitsRun`](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTestsEXT.cpp#L2345-L2425) | Validates required minima and granularity maxima. |
| Task payload and shared memory | [`TaskPayloadShMemSizeCase`](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTestsEXT.cpp#L84-L527) | Generates task/mesh shaders and checks payload and shared-memory result flags. |
| View and layer checks | [`MaxViewIndexInstance::iterate`](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTestsEXT.cpp#L675-L802), [`MaxOutputLayersInstance::iterate`](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTestsEXT.cpp#L877-L1016) | Validates `gl_ViewIndex` and `gl_Layer` through image readback. |
| Output count and components | [`MaxMeshOutputPrimVertCase`](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTestsEXT.cpp#L1018-L1291), [`MaxMeshOutputComponentsCase`](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTestsEXT.cpp#L1293-L1556) | Implements count, output-component, and SSBO/image checks. |
| Mesh payload and shared memory | [`MeshPayloadShMemSizeCase`](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTestsEXT.cpp#L1558-L1812) | Tests mesh-stage allocation combinations and optional task payload. |
| Output-size derivation and shaders | [`MaxMeshOutputSizeCase`](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTestsEXT.cpp#L1820-L2343) | Derives specialization constants and generates the output-size matrix. |
| EXT property definitions | [`VkPhysicalDeviceMeshShaderPropertiesEXT`](../../../../vulkan-docs/src/chapters/limits.adoc#L2325-L2469) | Defines the queried task and mesh limits. |
| Required EXT ranges | [`EXT mesh-shader limits`](../../../../vulkan-docs/src/chapters/limits.adoc#L6873-L6902) | Lists required minima and granularity maxima. |
| Mesh output formula | [`Mesh Shader Output`](../../../../vulkan-docs/src/chapters/VK_NV_mesh_shader/mesh.adoc#L150-L198) | Defines the output-memory calculation used by the source. |
| Multiview feature dependency | [`Mesh shader features`](../../../../vulkan-docs/src/chapters/features.adoc#L1860-L1900) | Defines the `multiviewMeshShader` dependency on `multiview`. |
| Default mustpass coverage | [`mesh-shader.txt`](../../../mustpass/main/vk-default/mesh-shader.txt#L2025-L2054) | Lists all 30 exact EXT property paths. |
