## Overview

**Core question:** Do pipeline-statistics queries report the expected work and result state across recording, reset, and retrieval paths?

- This page covers `statistics_query`, implemented by [`vktQueryPoolStatisticsTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp), under the `query_pool` test category.
- The family creates `VK_QUERY_TYPE_PIPELINE_STATISTICS` pools for compute, input-assembly, shader, clipping, and tessellation counters.
- It varies command-buffer mode, result transport, record width, reset timing, and selected graphics or compute work.
- The source also contains separate multi-counter and multiple-geometry-statistics cases.

## Background Knowledge

A pipeline-statistics query pool selects one or more `VkQueryPipelineStatisticFlagBits` at creation. Vulkan writes results in the selected-bit order. [Pipeline Statistics Queries](../../../../vulkan-docs/src/chapters/queries.adoc#queries-pipestats) defines the query type and selected counters.

A result request can use 32-bit or 64-bit integers. `VK_QUERY_RESULT_WITH_AVAILABILITY_BIT` appends an availability integer after each query's result values; its width matches the requested result width. The specification describes this per-query layout and the meaning of a zero availability value in [Pipeline Statistics Queries](../../../../vulkan-docs/src/chapters/queries.adoc#queries-pipestats).

With `VK_QUERY_RESULT_PARTIAL_BIT`, an unavailable query can return an intermediate value between zero and its final value. Without that flag, unavailable result values are undefined. See [partial results](../../../../vulkan-docs/src/chapters/queries.adoc#queries-pipestats).

## Registration Hierarchy

```text
query_pool.statistics_query
├── compute_shader_invocations
├── input_assembly_vertices
├── input_assembly_primitives
├── vertex_shader_invocations
├── fragment_shader_invocations
├── geometry_shader_invocations
├── geometry_shader_primitives
├── clipping_invocations
├── clipping_primitives
├── tes_control_patches
├── tes_evaluation_shader_invocations
├── vertex_only
├── host_query_reset
├── reset_before_copy
├── reset_after_copy
├── multiple_queries
└── multiple_geom_stats
```

[`QueryPoolStatisticsTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp#L6211) creates these 17 direct intermediate nodes. [`query-pool.txt`](../../../mustpass/main/vk-default/query-pool.txt) contains 17,769 registered leaves below `dEQP-VK.query_pool.statistics_query`; the tree above is therefore a compact view of a much larger generated matrix.

## Parameter Dimensions and Observed Values

| Dimension | Values or groups | Effect on the check |
|---|---|---|
| Statistic | Compute; input assembly vertices and primitives; vertex, fragment, geometry, clipping, and tessellation counters | Selects the count expected from the submitted work. |
| Command-buffer mode | `primary`, `secondary`, `secondary_inherited` | Changes where commands are recorded and whether inheritance information is used. |
| Result transport | `vkGetQueryPoolResults`, `vkCmdCopyQueryPoolResults`, and selected `vkCmdCopyQueryPoolResultsToMemoryKHR` paths | Changes the destination and decoding route. |
| Result layout | 32-bit or 64-bit values, optional availability, destination offset, valid or zero stride | Changes record size, placement, and decoding. |
| Reset workflow | Normal, host reset, reset before copy, reset after copy | Determines whether CTS expects a completed value or an unavailable result. |
| Work shape | Compute group and local sizes; graphics topology, stage configuration, clear operation, and repeated draws | Supplies the expected count or lower bound. |

The general generator iterates host-get and command-copy modes, 32-bit and 64-bit results, and destination-offset choices. It suppresses destination-offset cases for host retrieval because that API has no destination-offset parameter. It permits zero stride only for command copies. See [`QueryPoolStatisticsTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp#L6388).

The standard graphics repeat vector is `{1, 3, 5, 8, 15, 24}`. The test uses it to check scalable counter behavior rather than treating one draw as evidence for all counts. See [`QueryPoolStatisticsTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp#L6225).

### Counter families: selected pipeline statistics

The ordinary direct intermediate nodes name the requested statistic. `compute_shader_invocations` dispatches a compute workload. The graphics nodes cover input assembly, vertex, fragment, geometry, clipping, tessellation-control, and tessellation-evaluation statistics. `vertex_only` is a reduced-pipeline subset for input-assembly and vertex counters.

Topology expands the graphics cases across point, line, triangle, adjacency, and patch-list forms. Patch-list cases enable tessellation and add patch-size and primitive-count variants. Geometry and tessellation paths use their own expected counts because their counters measure different pipeline stages.

### Command-buffer modes: placement and inheritance

`PRIMARY` records the test in a primary command buffer. `SECONDARY` moves part of the work into a secondary command buffer. `SECONDARY_INHERITED` also supplies inherited pipeline-statistics information through `VkCommandBufferInheritanceInfo`. The source's `beginSecondaryCommandBuffer()` sets that inheritance field before secondary recording. See [`beginSecondaryCommandBuffer()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp#L400).

### Result transport: host reads, copies, and records

Host retrieval uses `vkGetQueryPoolResults`; command-copy cases use `vkCmdCopyQueryPoolResults`. The source decodes both paths into shared result-vector forms. `cmdCopyQueryPoolResults()` selects the buffer command or, when a device address is supplied in non-SC builds, `vkCmdCopyQueryPoolResultsToMemoryKHR`. See [`cmdCopyQueryPoolResults()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp#L264).

For availability records, the source uses `(value, availability)` pairs. A requested destination offset leaves a sentinel-filled record before the copied result. The reset-buffer verifier fails if that preceding record changes. See [`StatisticQueryTestInstance::verifyUnavailable()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp#L589).

### Reset workflows: result lifetime

The base families reset the pool in the command buffer before issuing the query. `host_query_reset` resets from the host, `reset_before_copy` resets after query completion commands but before the copy, and `reset_after_copy` copies first and resets afterward. The final two modes exercise copy ordering and unavailable-query reporting separately.

## Behavior Parameters

The behavioral axes are the selected statistic, command-buffer mode, reset workflow, and result layout. Topology and stage configuration determine an expected count, but they do not change the query protocol.

### Normal and reset-after-copy: completed result

For a normal workflow, CTS resets, begins the query, submits work, ends the query, waits, and reads the counter. Reset-after-copy adds a command-buffer copy before the reset, then checks the copied completed value. Compute cases require an exact invocation total. Many graphics cases use an expected minimum because rasterization and stage behavior can make a conservative bound more suitable.

### Host reset: completed then unavailable

Host-reset cases first read a completed value with availability enabled. CTS requires the expected value and a nonzero availability field. It then calls `vkResetQueryPool`, requests the result without wait or partial flags, and requires `VK_NOT_READY` with availability zero. The source retains the prior value in the local result storage and checks that the unavailable call did not overwrite it. See [`ComputeInvocationsTestInstance::executeTest()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp#L881).

### Reset before copy: unavailable copy record

These cases end the query, reset it in the command buffer, then copy the result with 64-bit values and availability. The expected copied availability is zero. The test also checks any destination-offset sentinel, so a correct availability value cannot hide a mispositioned copy.

### Multiple queries and multiple geometry statistics

`multiple_queries` enables input-assembly vertex and primitive statistics plus either fragment or vertex invocations. It combines partial and wait flags, host retrieval or command copying, destination offset, and selected zero-stride cases. The generator omits partial-plus-wait combinations because a query intentionally left unissued could wait indefinitely, and it omits zero stride for partial multi-query copies. See [`QueryPoolStatisticsTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp#L8942).

`multiple_geom_stats` has eight leaves: host get or copy, availability off or on, and inheritance off or on. It enables both geometry-shader invocations and geometry-shader primitives, checks each result item against a lower bound, then checks the rendered color image. See [`MultipleGeomStatsTestInstance::iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp#L4901).

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.query_pool.statistics_query.compute_shader_invocations.32bits_cmdcopyquerypoolresults_primary
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `compute_shader_invocations` | Creates a query pool for `VK_QUERY_PIPELINE_STATISTIC_COMPUTE_SHADER_INVOCATIONS_BIT` and compares its result with the exact dispatched invocation count. |
| `32bits` | Copies one query result as a 32-bit value; this choice changes query-result layout, not the shader's `uint` storage-buffer elements. |
| `cmdcopyquerypoolresults` | Retrieves the completed result with `vkCmdCopyQueryPoolResults` and `VK_QUERY_RESULT_WAIT_BIT`. |
| `primary` | Records the reset, query, dispatch, result copy, and barriers directly in a primary command buffer. |
| `compute_0` | Uses local size `(2, 2, 2)` and workgroup count `(2, 2, 2)`, producing exactly 64 compute invocations. |

#### Purpose

The compute shader supplies a precisely countable dispatch for the compute-invocation statistic while writing a unique linear index from every invocation to a host-checked storage buffer. The query result and buffer contents therefore check the counter and the workload independently.

#### Structural Design

| Phase | Shader or host-visible effect |
|-------|-------------------------------|
| Dispatch geometry | `2 × 2 × 2` workgroups, each containing `2 × 2 × 2` local invocations, produce 64 global invocations. |
| Index flattening | The shader scales global Y and Z coordinates by the complete lower-dimensional dispatch extents, then sums X, Y, and Z contributions into a linear index. |
| Workload proof | Invocation `index` adds `index` to `sb_out.values[index]`; CTS clears the buffer first and later requires element `n` to equal `n`. |
| Statistic proof | The query surrounds the dispatch, and CTS separately requires the copied query value to equal 64. |

#### Shader Code

```glsl
#version 450
/// Eight local invocations run in each workgroup; the host dispatches 2 x 2 x 2 workgroups.
layout (local_size_x = 2, local_size_y = 2, local_size_z = 2) in;

/// Descriptor set 0, binding 0 is a host-visible storage buffer cleared before each dispatch.
/// Its runtime array has one uint slot for every invocation in the largest generated variant.
layout(binding = 0) writeonly buffer Output {
    uint values[];
} sb_out;

void main (void) {
    /// Convert the 3D global invocation coordinate into independent X, Y, and Z
    /// contributions using the complete dispatch extents of the lower dimensions.
    uvec3 indexUvec3 = uvec3 (gl_GlobalInvocationID.x,
                              gl_GlobalInvocationID.y * gl_NumWorkGroups.x * gl_WorkGroupSize.x,
                              gl_GlobalInvocationID.z * gl_NumWorkGroups.x * gl_NumWorkGroups.y * gl_WorkGroupSize.x * gl_WorkGroupSize.y);
    uint index = indexUvec3.x + indexUvec3.y + indexUvec3.z;

    /// The cleared destination makes the final value at each unique slot equal its index.
    sb_out.values[index] += index;
}
```

#### Additional Info

- `QueryPoolComputeStatsTest` always generates and executes three programs. This walkthrough uses primary shader `compute_0`; `compute_1` and `compute_2` retain the same buffer/indexing body but use different local-size and workgroup-size decompositions, each totaling 63 invocations. See [`QueryPoolComputeStatsTest` construction](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp#L3976) and [`initPrograms()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp#L4033).
- CTS clears the storage buffer before each program, dispatches while the query is active, requires the copied query result to equal the local-size/workgroup-size product, and then checks every buffer element against its index. See [`ComputeInvocationsTestInstance::executeTest()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp#L748).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Generated program (`compute_0`, `compute_1`, `compute_2`) | Only the `layout(local_size_*)` values vary: `(2,2,2)`, `(1,1,1)`, and `(3,7,3)`. Their matching dispatch group counts are `(2,2,2)`, `(3,7,3)`, and `(1,1,1)`, so the expected query totals are 64, 63, and 63. | [`QueryPoolComputeStatsTest` parameter arrays](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp#L3976) |
| Result width (`32bits` / `64bits`) | No shader change; this controls `VkQueryResultFlags` and copied query-record width. | [`executeTest()` result-copy setup](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp#L795) |
| Retrieval (`getquerypoolresults` / `cmdcopyquerypoolresults`) | No shader change; the completed query is read through the host API or copied to a buffer by command. | [`executeTest()` result retrieval](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp#L861) |
| Recording mode (`primary` / secondary variants) | The generated compute programs are unchanged; the variant changes which command buffer records or inherits the query/dispatch work. | [`QueryPoolComputeStatsTest` case construction](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp#L6417) |
| Reset, destination-offset, stride, compute-queue, and device-address variants | These alter query lifecycle, result placement, queue selection, or copy command selection without changing the generated shader body. | [`QueryPoolComputeStatsTest` parameters](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp#L3967) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `comp`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 60
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_GlobalInvocationID %gl_NumWorkGroups
               OpExecutionMode %main LocalSize 2 2 2
               OpSource GLSL 450
               OpName %main "main"
               OpName %indexUvec3 "indexUvec3"
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
               OpName %gl_NumWorkGroups "gl_NumWorkGroups"
               OpName %index "index"
               OpName %Output "Output"
               OpMemberName %Output 0 "values"
               OpName %sb_out "sb_out"
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %gl_NumWorkGroups BuiltIn NumWorkgroups
               OpDecorate %_runtimearr_uint ArrayStride 4
               OpDecorate %Output BufferBlock
               OpMemberDecorate %Output 0 NonReadable
               OpMemberDecorate %Output 0 Offset 0
               OpDecorate %sb_out NonReadable
               OpDecorate %sb_out Binding 0
               OpDecorate %sb_out DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
     %v3uint = OpTypeVector %uint 3
%_ptr_Function_v3uint = OpTypePointer Function %v3uint
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
     %uint_0 = OpConstant %uint 0
%_ptr_Input_uint = OpTypePointer Input %uint
     %uint_1 = OpConstant %uint 1
%gl_NumWorkGroups = OpVariable %_ptr_Input_v3uint Input
     %uint_2 = OpConstant %uint 2
%_ptr_Function_uint = OpTypePointer Function %uint
%_runtimearr_uint = OpTypeRuntimeArray %uint
     %Output = OpTypeStruct %_runtimearr_uint
%_ptr_Uniform_Output = OpTypePointer Uniform %Output
     %sb_out = OpVariable %_ptr_Uniform_Output Uniform
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_Uniform_uint = OpTypePointer Uniform %uint
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_2 %uint_2 %uint_2
       %main = OpFunction %void None %3
          %5 = OpLabel
 %indexUvec3 = OpVariable %_ptr_Function_v3uint Function
      %index = OpVariable %_ptr_Function_uint Function
         %14 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %15 = OpLoad %uint %14
         %17 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_1
         %18 = OpLoad %uint %17
         %20 = OpAccessChain %_ptr_Input_uint %gl_NumWorkGroups %uint_0
         %21 = OpLoad %uint %20
         %22 = OpIMul %uint %18 %21
         %24 = OpIMul %uint %22 %uint_2
         %25 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_2
         %26 = OpLoad %uint %25
         %27 = OpAccessChain %_ptr_Input_uint %gl_NumWorkGroups %uint_0
         %28 = OpLoad %uint %27
         %29 = OpIMul %uint %26 %28
         %30 = OpAccessChain %_ptr_Input_uint %gl_NumWorkGroups %uint_1
         %31 = OpLoad %uint %30
         %32 = OpIMul %uint %29 %31
         %33 = OpIMul %uint %32 %uint_2
         %34 = OpIMul %uint %33 %uint_2
         %35 = OpCompositeConstruct %v3uint %15 %24 %34
               OpStore %indexUvec3 %35
         %38 = OpAccessChain %_ptr_Function_uint %indexUvec3 %uint_0
         %39 = OpLoad %uint %38
         %40 = OpAccessChain %_ptr_Function_uint %indexUvec3 %uint_1
         %41 = OpLoad %uint %40
         %42 = OpIAdd %uint %39 %41
         %43 = OpAccessChain %_ptr_Function_uint %indexUvec3 %uint_2
         %44 = OpLoad %uint %43
         %45 = OpIAdd %uint %42 %44
               OpStore %index %45
         %52 = OpLoad %uint %index
         %53 = OpLoad %uint %index
         %55 = OpAccessChain %_ptr_Uniform_uint %sb_out %int_0 %52
         %56 = OpLoad %uint %55
         %57 = OpIAdd %uint %56 %53
         %58 = OpAccessChain %_ptr_Uniform_uint %sb_out %int_0 %52
               OpStore %58 %57
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

1. CTS creates a pipeline-statistics query pool with the requested statistic bit or bit set.
2. It records the relevant reset, query begin, workload, query end, optional result copy, and barriers in primary or secondary command buffers.
3. It submits the primary command buffer and waits for completion.
4. It obtains results from host memory or the copied host-visible buffer.
5. It applies the mode-specific check: exact value, lower bound, availability state, result code, record placement, or image output.

Compute validation compares the query result with the product of local and group dimensions, then checks every storage-buffer element. See [`ComputeInvocationsTestInstance::executeTest()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp#L878).

The multi-statistic validator decodes each query's enabled statistic bits in bit order. It requires availability after a waited non-partial request, rejects available values below the expected minimum, and bounds unavailable partial values by the expected maximum. See [`VertexShaderMultipleQueryTestInstance::checkResult()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp#L4545).

## Failure Meaning

### Failure Cause Mapping

| Observed failure | Check that reports it | What it points to |
|---|---|---|
| Exact compute count differs | Compute result comparison | Wrong compute-statistic accounting or result retrieval. |
| Graphics value is below its minimum | Per-statistic graphics validation | The selected stage did not contribute the expected work, or result decoding selected the wrong item. |
| Waited result has zero availability | Multi-query availability check | Completion or availability reporting is incorrect. |
| Host reset returns another status or nonzero availability | Host-reset validation | Host query reset or unavailable-result behavior is incorrect. |
| Reset-before-copy record is available | Reset-buffer validation | Reset and copy ordering is incorrect. |
| Offset sentinel changes | Destination-offset validation | The command copy wrote at the wrong location. |
| Geometry count passes but image differs | Geometry image comparison | The draw path itself did not produce the expected output. |

### Cause Analysis

#### Pipeline counter or result-state mismatch

**Possible failure symptoms:**

A pipeline counter mismatch does not identify a single driver component. The source distinguishes exact workloads from lower-bound graphics cases because counters reflect the selected stage and pipeline behavior. A failure must therefore be interpreted against the queried statistic, active stages, topology, and result flags.

**Possible implementation causes:**

Availability and reset failures have narrower meaning. The Vulkan specification says availability zero means the result is not yet available, and specifies the layout that follows each query's result values. The host-reset and reset-before-copy branches directly test those rules. A destination-offset failure is a data-placement failure even if the copied counter itself looks correct.

## Case Pruning

The source intentionally prunes invalid or redundant combinations:

### Requirement-based pruning

- `_device_address` cases are sampled rather than exhaustive and are excluded by `#ifndef CTS_USES_VULKANSC`;

### Design-based pruning

- host retrieval does not receive destination-offset variants;
- zero stride appears only in command-copy configurations;
- reset-after-copy exists only where a command copy occurs;
- partial-plus-wait multiple-query cases are skipped to avoid an indefinitely unavailable query;
- partial multi-query cases skip zero stride;
- point-mode isoline tessellation cases are skipped to limit the matrix.

These are source-level matrix decisions, not missing mustpass entries. The mustpass file still records the generated leaves that remain after pruning.

## Key Takeaways

- `statistics_query` verifies both pipeline counting and query-result protocol behavior.
- The main behavioral axes are statistic selection, recording mode, reset timing, and result-record layout.
- The result checks cover completed values, unavailable states, availability fields, copied-buffer placement, and selected independent workload outputs.
- Feature gates separate unsupported hardware configurations from failures in supported paths.

## Source Reference Appendix

- [Statistics-query implementation and generator](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp#L6199)
- [Common statistics and host-reset support checks](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp#L505)
- [Query-pool construction and result helpers](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp#L177)
- [Canonical mustpass entries](../../../mustpass/main/vk-default/query-pool.txt)
- [Vulkan query result retrieval rules](../../../../vulkan-docs/src/chapters/queries.adoc#queries-pipestats)
