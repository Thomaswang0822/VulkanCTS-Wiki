## Overview

**Core question:** Does the primitives-generated query report the primitives produced by the graphics pipeline in every supported query and transform-feedback arrangement?

- The implementation and registration for `dEQP-VK.transform_feedback.primitives_generated_query` live in [`vktPrimitivesGeneratedQueryTests.cpp`](../../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L2608-L3065).
- The test family has three direct children: `get`, `copy`, and `concurrent`.
- `get` reads query pools with `vkGetQueryPoolResults`; `copy` copies results with `vkCmdCopyQueryPoolResults`; `concurrent` checks overlapping query types, secondary command buffers, pipeline statistics, and indirect draws.
- The main matrix compares `VK_QUERY_TYPE_PRIMITIVES_GENERATED_EXT` with transform-feedback query results when transform feedback is enabled. It varies shader stage, topology, stream, reset and readback method, rasterization state, query ordering, draw count, and availability reporting.

## Background Knowledge

- A primitives-generated query counts primitives produced by the graphics pipeline. Rasterization and fragment output happen later, so a discarded rasterizer or an empty fragment shader does not by itself imply a zero primitives-generated result.
- A transform-feedback query reports results for a selected transform-feedback stream. The result includes the number of primitives generated and the number written to transform-feedback buffers. Geometry shaders can select streams with `EmitStreamVertex` and close a primitive with `EndStreamPrimitive`.
- Query results are asynchronous. Vulkan stores them in query pools, and the host can read them or a command can copy them to a buffer. An availability value indicates that a result is ready for use.

## Registration Hierarchy

```text
transform_feedback.primitives_generated_query
├── get
├── copy
└── concurrent
```

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Query read path | `get`, `copy` | Selects host query-pool reads or device-side query-result copies. | [`readTypes`](../../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L2610-L2620) |
| Query reset path | `queue_reset`, `host_reset` | Selects `vkCmdResetQueryPool` or `vkResetQueryPool`. | [`resetTypes`](../../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L2622-L2632) |
| Result width | `32bit`, `64bit`, `pgq_32bit_xfb_64bit`, `pgq_64bit_xfb_32bit` | Exercises default, 64-bit, and mixed-width result layouts. | [`resultTypes`](../../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L2634-L2648) |
| Shader stage | `vert`, `tese`, `geom` | Places the last relevant pre-rasterization stage in the vertex, tessellation evaluation, or geometry shader path. | [`shaderStages`](../../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L2650-L2662) |
| Transform feedback | `no_xfb`, `xfb` | Enables the PGQ-only path or the PGQ/XFB result comparison. | [`transformFeedbackStates`](../../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L2664-L2673) |
| Rasterization case | `no_rast`, `rast`, `empty_frag`, `no_attachment`, `color_write_disable_static`, `color_write_disable_static_ds`, `color_write_disable_dynamic`, `color_write_disable_dynamic_ds` | Separates primitive generation from later rasterization and attachment behavior. | [`rastCases`](../../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L2675-L2703) |
| Topology | `point_list`, `line_list`, `line_strip`, `triangle_list`, `triangle_strip`, `triangle_fan`, `line_list_with_adjacency`, `line_strip_with_adjacency`, `triangle_list_with_adjacency`, `triangle_strip_with_adjacency`, `patch_list` | Changes primitive assembly and the number of vertices needed for 32 generated primitives. | [`topologies`](../../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L2705-L2738) |
| Query streams | `default`, `0`, `1` for PGQ and XFB | Selects default or indexed query commands and, for geometry shaders, stream emission. | [`streamIndices`](../../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L2740-L2749) |
| Command-buffer draw count | `single_draw`, `two_draws` | Checks one or two draws inside the active query range. | [`cmdBufCases`](../../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L2751-L2761) |
| Query count | one query or `_2_queries` | Checks one query slot or two independently validated slots. | [`queryCountCases`](../../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L2763-L2771) |
| Query order | `pqg_first`, `xfbq_first` | Changes which query begins first when both query types are active. | [`queryOrderCases`](../../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L2773-L2783) |
| Outside draw | `none`, `before`, `after` | Places an extra draw outside the active query interval or omits it. | [`outsideDrawCases`](../../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L2785-L2797) |
| Availability | absent or `_with_availability` | Requests and validates the availability result where the generator permits it. | [`testGenerator()`](../../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L2902-L2953) |
| Concurrent test type | `two_xfbq_inside_pgq`, `pgq_secondary_cmd_buffers`, `pipeline_statistics_1`, `pipeline_statistics_2`, `pipeline_statistics_3` | Selects the concurrent query scenario. | [`concurrentTestTypeCases`](../../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L2989-L3000) |
| Concurrent draw path | `draw`, `indirect` | Uses direct or indirect drawing in the concurrent family. | [`drawTypeCases`](../../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L3002-L3009) |

## Behavior Parameters

The primary behavioral axis is the registered test family. The families share the same primitives-generated property but exercise different result and query-command arrangements.

### get: host query-pool readback

The `get` family reads the query pools with `vkGetQueryPoolResults`, using `VK_QUERY_RESULT_WAIT_BIT` and the selected result width and availability flags. It tests reset timing, query ordering, stream indexing, and the effect of draws that fall inside or outside the active query range.

### copy: device-side query-result copy

The `copy` family uses `vkCmdCopyQueryPoolResults` to write query results into host-visible transfer-destination buffers. A transfer-to-host barrier precedes host inspection, so failures can indicate either incorrect counters or an incorrect copied result layout and synchronization path.

### concurrent: overlapping query scenarios

The `concurrent` family uses a separate test instance and geometry shader. It covers two transform-feedback queries inside one primitives-generated query, a primitives-generated query in a secondary command buffer, and three pipeline-statistics arrangements. Each scenario has direct and indirect draw cases, uses geometry shaders, and excludes patch lists.

## Shader Analysis

The shader code is generated from the selected stage and topology. The walkthrough below uses the geometry shader because it makes stream selection, primitive emission, and transform-feedback capture visible in one representative case.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.transform_feedback.primitives_generated_query.get.queue_reset.32bit.geom.xfb.rast.triangle_list.pgq_default_xfb_default.single_draw.pqg_first.none
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `32bit`, `get`, `queue_reset` | The host reads one 32-bit result per query with `vkGetQueryPoolResults`; a separate waited command buffer resets both pools first. |
| `geom`, `triangle_list`, `single_draw` | The geometry shader receives triangles and emits a three-vertex triangle strip. One draw should generate 32 primitives. |
| `xfb`, `pgq_default`, `xfb_default`, `pqg_first` | Both query types monitor the default stream, transform feedback is active, and the primitives-generated query begins before the transform-feedback query. |
| `rast`, `none` | The test uses a color attachment and no draw outside the active query interval. The fragment result does not determine the primitive count. |

#### Purpose

This shader supplies a fixed primitive-emission path for comparing the primitives-generated count with the transform-feedback generated count. It also writes a transform-feedback output so the host can check the transform-feedback written-count path.

#### Structural Design

| Phase | Shader action | Query meaning |
|-------|---------------|---------------|
| Input | Read one input triangle through `gl_in`. | The input topology determines the geometry-shader invocation. |
| Capture value | Assign `vec4(42)` to the transform-feedback output. | Each emitted vertex has a defined captured value. |
| Emit | Copy `gl_in[0].gl_Position` to the output three times, call `EmitVertex()` after each copy, then call `EndPrimitive()`. | Three vertices form one output triangle strip primitive. |

#### Shader Code

```glsl
#version 450
layout(triangles) in;
layout(triangle_strip, max_vertices = 3) out;
/// The output is captured to transform-feedback buffer 0 with a 16-byte stride.
layout(xfb_buffer = 0, xfb_offset = 0, xfb_stride = 16, location = 0, stream = 0) out vec4 xfb;
void main (void)
{
    /// The host does not inspect this payload directly, but it makes the captured output defined.
    xfb = vec4(42);
    /// Emit three vertices so the output primitive assembly creates one triangle.
    gl_Position = gl_in[0].gl_Position;
    EmitVertex();
    gl_Position = gl_in[0].gl_Position;
    EmitVertex();
    gl_Position = gl_in[0].gl_Position;
    EmitVertex();
    EndPrimitive();
}
```

#### Additional Info

- The source-generated branch emits the same position three times for this representative topology. The host's vertex-buffer generator still supplies input data for 32 expected primitives.
- The source sets `primitivesWritten` to `primitivesGenerated - 3`, so the XFB written-count expectation for this case is 29 even though the generated-count expectation is 32.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Shader stage | `vert` uses `gl_Position` directly, `tese` adds tessellation-control and tessellation-evaluation stages, and `geom` selects input and output layouts. | [`initPrograms()`](../../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L1298-L1437) |
| Topology | Geometry input and output layout strings and the emitted vertex count change with topology; patch lists use tessellation evaluation instead. | [`topologyData`](../../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L250-L294) |
| Stream selection | Nondefault streams replace `EmitVertex` and `EndPrimitive` with indexed stream operations; multiple streams can add a second output group. | [`initPrograms()`](../../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L1373-L1437) |
| Transform feedback | XFB adds the decorated output and capture value. The query-only branch omits those declarations. | [`initPrograms()`](../../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L1300-L1325) |
| Rasterization case | Rasterizer discard omits the fragment shader; other cases select an empty or writing fragment shader, while the pre-rasterization shader remains the source of generated primitives. | [`initPrograms()`](../../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L1440-L1461) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `geom`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 35
; Schema: 0
               OpCapability Geometry
               OpCapability TransformFeedback
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Geometry %main "main" %xfb %_ %gl_in
               OpExecutionMode %main Xfb
               OpExecutionMode %main Triangles
               OpExecutionMode %main Invocations 1
               OpExecutionMode %main OutputTriangleStrip
               OpExecutionMode %main OutputVertices 3
               OpSource GLSL 450
               OpName %main "main"
               OpName %xfb "xfb"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpMemberName %gl_PerVertex 2 "gl_ClipDistance"
               OpMemberName %gl_PerVertex 3 "gl_CullDistance"
               OpName %_ ""
               OpName %gl_PerVertex_0 "gl_PerVertex"
               OpMemberName %gl_PerVertex_0 0 "gl_Position"
               OpMemberName %gl_PerVertex_0 1 "gl_PointSize"
               OpMemberName %gl_PerVertex_0 2 "gl_ClipDistance"
               OpMemberName %gl_PerVertex_0 3 "gl_CullDistance"
               OpName %gl_in "gl_in"
               OpDecorate %xfb Location 0
               OpDecorate %xfb Offset 0
               OpDecorate %xfb XfbBuffer 0
               OpDecorate %xfb XfbStride 16
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpMemberDecorate %gl_PerVertex 2 BuiltIn ClipDistance
               OpMemberDecorate %gl_PerVertex 3 BuiltIn CullDistance
               OpDecorate %_ XfbBuffer 0
               OpDecorate %_ XfbStride 16
               OpDecorate %gl_PerVertex_0 Block
               OpMemberDecorate %gl_PerVertex_0 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex_0 1 BuiltIn PointSize
               OpMemberDecorate %gl_PerVertex_0 2 BuiltIn ClipDistance
               OpMemberDecorate %gl_PerVertex_0 3 BuiltIn CullDistance
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Output_v4float = OpTypePointer Output %v4float
        %xfb = OpVariable %_ptr_Output_v4float Output
   %float_42 = OpConstant %float 42
         %11 = OpConstantComposite %v4float %float_42 %float_42 %float_42 %float_42
       %uint = OpTypeInt 32 0
     %uint_1 = OpConstant %uint 1
%_arr_float_uint_1 = OpTypeArray %float %uint_1
%gl_PerVertex = OpTypeStruct %v4float %float %_arr_float_uint_1 %_arr_float_uint_1
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%gl_PerVertex_0 = OpTypeStruct %v4float %float %_arr_float_uint_1 %_arr_float_uint_1
     %uint_3 = OpConstant %uint 3
%_arr_gl_PerVertex_0_uint_3 = OpTypeArray %gl_PerVertex_0 %uint_3
%_ptr_Input__arr_gl_PerVertex_0_uint_3 = OpTypePointer Input %_arr_gl_PerVertex_0_uint_3
      %gl_in = OpVariable %_ptr_Input__arr_gl_PerVertex_0_uint_3 Input
%_ptr_Input_v4float = OpTypePointer Input %v4float
       %main = OpFunction %void None %3
          %5 = OpLabel
               OpStore %xfb %11
         %26 = OpAccessChain %_ptr_Input_v4float %gl_in %int_0 %int_0
         %27 = OpLoad %v4float %26
         %28 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %28 %27
               OpEmitVertex
         %29 = OpAccessChain %_ptr_Input_v4float %gl_in %int_0 %int_0
         %30 = OpLoad %v4float %29
         %31 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %31 %30
               OpEmitVertex
         %32 = OpAccessChain %_ptr_Input_v4float %gl_in %int_0 %int_0
         %33 = OpLoad %v4float %32
         %34 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %34 %33
               OpEmitVertex
               OpEndPrimitive
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The main instance uses 64 by 64 color images for rasterizing cases and optional 64 by 64 depth/stencil images for `_ds` cases. It allocates a host-visible vertex buffer sized from the selected topology's vertex-count function.
- The host fixes `primitivesGenerated` at 32. It allocates enough vertex data for the topology and makes the transform-feedback buffer large enough for `primitivesGenerated - 3` written primitives, with a four-float vertex payload.
- Each query slot gets a primitives-generated query. XFB cases also get a transform-feedback-stream query and one transform-feedback buffer per query slot. The command buffer begins the selected queries, binds transform-feedback buffers, begins transform feedback, executes one or two draws, and ends them in the selected order.
- Queue reset records `vkCmdResetQueryPool` in a separate command buffer and waits for that submission before result access. Host reset calls `vkResetQueryPool` after command recording and before submission.
- `get` calls `vkGetQueryPoolResults` with `VK_QUERY_RESULT_WAIT_BIT`, the selected width, and optional `VK_QUERY_RESULT_WITH_AVAILABILITY_BIT` before waiting for the submission fence. `copy` records `vkCmdCopyQueryPoolResults`, adds a transfer-to-host barrier, waits for the fence, invalidates the host allocations, and reads the copied bytes.
- For each query index, the host expects the PGQ generated count and, when enabled, the XFB generated count to equal `32 * drawCount`. It expects the XFB written count to equal 29. Requested availability values must equal 1. A passing main-family case returns `Counters OK`.
- The concurrent instance creates a 16 by 17 color target, uses geometry shaders, and validates the query-specific results after direct or indirect draw execution. Its setup and checks are in [`ConcurrentPrimitivesGeneratedQueryTestInstance::iterate()`](../../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L1557-L2115).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `get` | Incorrect primitives-generated or transform-feedback query accounting, query reset or order handling, result-width or availability handling, or host `vkGetQueryPoolResults` interpretation. |
| `copy` | Incorrect query accounting or `vkCmdCopyQueryPoolResults` result layout, synchronization, stride, width, or availability handling. |
| `concurrent` | Incorrect interaction between overlapping query types, secondary command-buffer execution, pipeline-statistics queries, indirect draws, or stream-specific query state. |

### Cause Analysis

#### Query accounting and primitive assembly

**Possible failure symptoms:** The PGQ result differs from `32 * drawCount`, or the XFB generated result differs from the same expected value. The failure can be limited to a topology, shader stage, or stream selection.

**Possible implementation causes:** The graphics pipeline may assemble the selected topology incorrectly, count primitives at the wrong pipeline point, or associate an indexed query with the wrong transform-feedback stream. The source derives expected counts from topology assembly and uses geometry shader emission for stream cases, while the Vulkan specification places transform feedback before later vertex post-processing. A source-level investigation is needed to separate implementation and shader-compilation causes.

#### Transform-feedback written count

**Possible failure symptoms:** PGQ and XFB generated counts pass, but `xfbWritten` is not 29, or the transform-feedback query result does not match the selected stream.

**Possible implementation causes:** The implementation may count captured primitives incorrectly, apply the stream or buffer mapping incorrectly, or mishandle the transform-feedback buffer range. The test binds a transform-feedback buffer and decorates a four-float output with a 16-byte stride, so the failure concerns capture accounting rather than the PGQ count alone.

#### Query result readback and availability

**Possible failure symptoms:** A result retrieved by `get` or copied by `copy` contains the wrong width, value, layout, or availability bit. A case can fail before the counter comparison if the host sees an availability value other than 1.

**Possible implementation causes:** The query-result command or host readback path may mishandle `VK_QUERY_RESULT_64_BIT`, mixed PGQ/XFB widths, result stride, `VK_QUERY_RESULT_WITH_AVAILABILITY_BIT`, or transfer-to-host visibility. The test uses a waited result flag for host reads and an explicit transfer-to-host barrier for copied results, so a failure after those synchronization points needs source-level investigation of the corresponding API path.

#### Concurrent query state

**Possible failure symptoms:** Only a `concurrent` case fails, especially one involving nested XFB queries, a secondary command buffer, pipeline statistics, or an indirect draw.

**Possible implementation causes:** The implementation may mishandle query state across overlapping query types, command-buffer execution boundaries, indirect draw parameters, or the pipeline-statistics query configuration. The concurrent source adds feature and inherited-query checks, but the observed symptom alone does not identify a driver, hardware, compiler, or host cause.

## Case Pruning

### Requirement-based pruning

- Every case requires `VK_EXT_primitives_generated_query`, `VK_EXT_transform_feedback`, and the `primitivesGeneratedQuery` feature. Rasterizer-discard cases additionally require `primitivesGeneratedQueryWithRasterizerDiscard`.
- Host-reset cases require `VK_EXT_host_query_reset`. XFB cases require the transform-feedback feature and `transformFeedbackQueries` property.
- Geometry stages and adjacency topologies require the geometry-shader core feature. Tessellation evaluation cases require the tessellation-shader core feature.
- Nonzero PGQ streams require `primitivesGeneratedQueryWithNonZeroStreams`; the selected stream indices must also fit `maxTransformFeedbackStreams`. Color-write-disable cases require `VK_EXT_color_write_enable` and its `colorWriteEnable` feature.
- A depth/stencil rasterization case needs an optimal-tiling depth/stencil attachment format with `VK_FORMAT_FEATURE_DEPTH_STENCIL_ATTACHMENT_BIT`. The implementation tries `VK_FORMAT_D32_SFLOAT_S8_UINT` and then `VK_FORMAT_D24_UNORM_S8_UINT`.
- Concurrent cases require the corresponding pipeline-statistics and inherited-query support checked by [`ConcurrentPrimitivesGeneratedQueryTestCase::checkSupport()`](../../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L2397-L2447).

### Design-based pruning

- Mixed result widths are generated only with transform feedback, because the mixed values describe PGQ and XFB results together.
- Patch lists pair only with tessellation evaluation; non-patch topologies pair with vertex or geometry stages. Adjacency topologies pair only with geometry shaders.
- Nondefault streams are tested only with geometry shaders. XFB stream variants are omitted when transform feedback is disabled.
- `xfbq_first` is omitted without XFB because there is no transform-feedback query to begin first.
- Availability cases are limited to line-list, triangle-list, and patch-list topologies, the discard, ordinary rasterization, and no-attachment rasterization cases, and the single-draw command-buffer case.
- Color-write, empty-fragment, no-attachment, and depth/stencil variants are restricted to the basic 32-bit `get` plus queue-reset combination. The generator labels these cases as uninteresting outside that combination and omits the larger cross-product by design.
- Concurrent cases exclude patch lists and fix the shader stage to geometry. `two_xfbq_inside_pgq` selects XFB stream 1; the other concurrent types do not enable an XFB stream.

## Key Takeaways

- PGQ must follow the number of primitives generated by the selected topology and draw count, independent of whether later rasterization writes a fragment.
- XFB cases compare PGQ with the XFB generated count and separately check the captured written count of 29.
- The matrix tests both result access routes and both query reset routes, then adds width, availability, ordering, stream, and command-buffer variations around them.
- The source prunes combinations that lack the required stage, stream, feature, or meaningful behavior. The mustpass file contains the resulting registered leaves rather than the unfiltered Cartesian product.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test registration | [`createPrimitivesGeneratedQueryTests()`](../../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L3062-L3065) | Registers the `primitives_generated_query` test category. |
| Matrix construction | [`testGenerator()`](../../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L2608-L3057) | Defines direct children, parameter names, concurrent groups, and pruning. |
| Main support checks | [`PrimitivesGeneratedQueryTestCase::checkSupport()`](../../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L1243-L1295) | Checks extensions, features, properties, stages, streams, and attachments. |
| Main shader generation | [`PrimitivesGeneratedQueryTestCase::initPrograms()`](../../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L1298-L1461) | Generates vertex, tessellation, geometry, and fragment shader sources. |
| Main execution and validation | [`PrimitivesGeneratedQueryTestInstance::iterate()`](../../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L314-L871) | Creates resources, records queries and draws, reads results, and checks counters. |
| Topology formulas | [`topologyData`](../../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L250-L294) | Maps topology to primitive size and vertex/primitive count functions. |
| Concurrent support | [`ConcurrentPrimitivesGeneratedQueryTestCase::checkSupport()`](../../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L2397-L2447) | Checks support for concurrent query configurations. |
| Concurrent shaders | [`ConcurrentPrimitivesGeneratedQueryTestCase::initPrograms()`](../../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L2450-L2606) | Generates the concurrent geometry and related shader sources. |
| Concurrent registration | [`concurrentGroup`](../../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L2989-L3057) | Registers concurrent query types and direct or indirect draw cases. |
| Query semantics | [Vulkan Queries chapter](https://docs.vulkan.org/spec/latest/chapters/queries.html) | Describes query pools, asynchronous results, host reads, copies, and availability. |
| Transform feedback semantics | [Vulkan Fixed-Function Vertex Post-Processing chapter](https://docs.vulkan.org/spec/latest/chapters/vertexpostproc.html) | Describes transform-feedback placement and primitive capture. |
| Feature enablement | [Vulkan Features chapter](https://docs.vulkan.org/spec/latest/chapters/features.html) | Describes supported features and device enablement. |
| Registration evidence | [`transform-feedback.txt`](../../../mustpass/main/vk-default/transform-feedback.txt#L2173-L110038) | Confirms registered `primitives_generated_query` paths in the default mustpass set. |
