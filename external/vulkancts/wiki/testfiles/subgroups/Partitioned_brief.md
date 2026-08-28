# Understanding Brief: `subgroups.partitioned`

## One-Sentence Test Purpose

This test checks whether partitioned subgroup reductions and scans return the same values as ordinary subgroup arithmetic restricted to each selected partition, across supported shader execution families.

## Background Knowledge

### Partitions inside a subgroup

A Vulkan subgroup is a set of shader invocations that can exchange data through subgroup operations. A partition is a ballot mask selecting a subset of those invocations. `subgroupPartitionNV` gives invocations with equal keys the same partition mask, and a partitioned arithmetic operation applies only to the active invocations selected by that mask.

Why it matters here:
- the partition mask changes who contributes to a reduction or scan without creating a new Vulkan execution scope;
- bits for inactive invocations do not make those invocations contribute;
- reduce, inclusive scan, and exclusive scan have different result sets even when they use the same operator and partition.

### Reference through divergent execution

An ordinary subgroup arithmetic call normally includes the active invocations that execute it. The test uses divergent branches keyed by partition values, then invokes the corresponding ordinary subgroup operation inside each branch. That ordinary result is the reference for the partitioned result for the same active subset.

Why it matters here:
- the reference is produced independently from the partitioned arithmetic instruction;
- valid comparisons depend on inactive invocations being ignored;
- floating-point addition and multiplication use a tolerance because operation order is implementation-dependent.

## One Concrete Example

The executable leaf `dEQP-VK.subgroups.partitioned.compute.subgroupadd_float` is registered from the unsuffixed operation name `subgroupadd` plus the data format `float`. That leaf does not invoke GLSL `subgroupAdd` as its test subject. The builder maps its operation and scan selections to the partitioned name `subgroupPartitionedAddNV`, while ordinary `subgroupAdd` supplies reference values.

A simplified, reconstructed part of the compute shader is:

```glsl
uvec4 partitionBallot = subgroupPartitionNV(idhashFmt) & subgroupBallot(true);
float partitionedResult = subgroupPartitionedAddNV(data[gl_SubgroupInvocationID], partitionBallot);

if (idhashFmt == float(i)) {
    float subsetResult = subgroupAdd(data[gl_SubgroupInvocationID]);
    // Compare partitionedResult with subsetResult using the generated float tolerance.
}
```

This registered-to-invoked mapping is intentional:

| Registered leaf component | Source selection | Invoked operation under test | Reference operation |
|---------------------------|------------------|------------------------------|---------------------|
| `subgroupadd_float` | `OPERATOR_ADD` plus `SCAN_REDUCE` plus scalar `float` | `subgroupPartitionedAddNV` | `subgroupAdd` |

## End-to-End Test Flow

```text
[host] register an execution family, operation and scan form, data format, stage suffix where applicable, and optional required subgroup size
[host] reject unsupported subgroup features, formats, shader stages, extension features, or size-control combinations
[host] generate GLSL through initPrograms or initFrameBufferPrograms using getTestString
[host] create and initialize input data with nonzero values and create the R32_UINT result target
[host] create the selected compute, graphics, framebuffer, ray tracing, mesh, or task pipeline
[host] dispatch or draw using harness-selected dimensions and local sizes
[device] build full, singleton, hash-derived, and divergent hash-derived partitions
[device] compare each partitioned operation with an ordinary subgroup reference and set one bit per successful check
[device] write the accumulated 24-bit mask to the result buffer or framebuffer output
[host] wait, invalidate or copy back the result allocation, and scan every produced uint
[host] pass only when every checked uint is 0xFFFFFF, and repeat across required subgroup sizes when requested
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `getExtHeader` enables `GL_NV_shader_subgroup_partitioned`, subgroup arithmetic, subgroup ballot, and any extension needed by the selected data type.
- `getTestString` emits the same five semantic checks for every legal operator, scan form, and format combination: all-active, divergent all-active, singleton, hash partitions, and hash partitions inside divergent control flow.
- `initPrograms` inserts that body into common compute, graphics, ray tracing, mesh, or task shader shells. It selects SPIR-V 1.3 for ordinary compute and graphics paths and SPIR-V 1.4 for ray tracing and mesh paths.
- `initFrameBufferPrograms` builds the no-SSBO framebuffer-stage variants with SPIR-V 1.3.
- The compute harness supplies local sizes through specialization constants. Required-subgroup-size cases rebuild or execute over every supported power-of-two size from the reported minimum through maximum.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Input `data[]` buffer | yes | yes | read | no | Supplies nonzero scalar or vector operands indexed by `gl_SubgroupInvocationID`; compute-like and most pipeline paths use `std430`, while framebuffer paths use uniform-buffer storage. |
| `result[]` storage buffer | yes | yes | written | yes | Receives one `uint` pass mask per tested invocation for compute, graphics, ray tracing, mesh, and task paths. |
| `R32_UINT` framebuffer attachment and transfer buffer | yes | yes | attachment written, then copied | yes | Carries the same pass mask when the tested vertex, tessellation, or geometry stage cannot write an SSBO in the framebuffer-specific path. |
| Partition ballot values | no | no | generated and consumed in the shader | no | `subgroupPartitionNV` and `subgroupBallot` produce shader-local masks, not host-created resources. |
| Ray tracing acceleration structure and stage plumbing | yes | yes | traversed or used by the harness | no | Makes all supported ray tracing stages execute the common partitioned test body; it is not itself the property under test. |

## What Is Checked

- Bit `0x1` records agreement between one all-active partitioned operation and the corresponding ordinary subgroup operation.
- Bit `0x2` repeats that comparison under even/odd divergent control flow, checking that inactive invocations represented in the ballot do not contribute.
- Bit `0x4` records the singleton-partition result. Reduce and inclusive cases expect the invocation's own value; exclusive cases expect the operator identity.
- Bits produced by `0x4 << N` cover hash-derived partitions for `N` from 1 through 15.
- Bits produced by `0x20000 << N` cover hash-derived partitions inside outer divergent control flow for `N` from 1 through 6.
- Together these checks must set exactly `0xFFFFFF`. The host scans every result value, so one missing bit fails the test case.
- Integer and Boolean comparisons are exact. Floating add and multiply comparisons use generated type-dependent tolerances; floating min and max comparisons are exact after the helper's NaN-aware reference handling.

## Behavior Parameter Identification

> **Behavior parameter:** test family
>
> **Candidate values:** `graphics`, `compute`, `framebuffer`, `ray_tracing`, `mesh`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `graphics` | Partitioned subgroup arithmetic or result storage is incorrect in one or more enabled graphics pipeline stages. |
| `compute` | Partitioned subgroup arithmetic is incorrect in compute execution, potentially only for a required subgroup size or harness-selected local size. |
| `framebuffer` | Partitioned subgroup arithmetic or stage-to-framebuffer result transport is incorrect in a vertex, tessellation, or geometry framebuffer path. |
| `ray_tracing` | Partitioned subgroup arithmetic is incorrect in one or more supported programmable ray tracing stages, or the stage result is not returned correctly. |
| `mesh` | Partitioned subgroup arithmetic is incorrect in mesh or task execution, potentially only for a required subgroup size. |

## Important Variations and Special Cases

- The operation axis has 21 forms: seven operators across reduce, inclusive scan, and exclusive scan. Floating formats exclude bitwise operators; Boolean formats include only bitwise operators.
- `getAllFormats` supplies scalar and vector integer, floating-point, and Boolean types, including extended 8-bit, 16-bit, 64-bit, and long-vector variants when available. Ray tracing deliberately uses a smaller format set.
- Compute and mesh each register ordinary and `_requiredsubgroupsize` cases. Mesh adds `_mesh` or `_task`. Framebuffer adds one of `_vertex`, `_tess_control`, `_tess_eval`, or `_geometry`.
- The entire `partitioned` test family is absent from Vulkan SC builds because both its include and its registration call are guarded by `CTS_USES_VULKANSC`.
- No partitioned-specific entry appears in `mustpass/main/src/test-issues.txt`; this is evidence only that the current issue exclusion file does not suppress this family.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Registered tree and leaf construction | [`createSubgroupsPartitionedTests`](../../../modules/vulkan/subgroups/vktSubgroupsPartitionedTests.cpp#L526-L704) | Creates the five direct children, legal operation and format combinations, stage suffixes, and required-size variants. |
| Registered-to-invoked name mapping | [`getOpTypeName` and `getOpTypeNamePartitioned`](../../../modules/vulkan/subgroups/vktSubgroupsPartitionedTests.cpp#L168-L176) | Separates unsuffixed registered/reference operation names from `subgroupPartitioned*NV` names. |
| Generated semantic checks | [`getTestString`](../../../modules/vulkan/subgroups/vktSubgroupsPartitionedTests.cpp#L186-L308) | Emits all partition scenarios, reference operations, comparisons, and the 24-bit pass mask. |
| Program builders and SPIR-V targets | [`initFrameBufferPrograms` and `initPrograms`](../../../modules/vulkan/subgroups/vktSubgroupsPartitionedTests.cpp#L310-L333) | Chooses the common shader shell and SPIR-V 1.3 or 1.4 build target. |
| Support checks | [`supportedCheck`](../../../modules/vulkan/subgroups/vktSubgroupsPartitionedTests.cpp#L335-L401) | Enforces partitioned support, formats, stages, extended storage, extension features, and size control. |
| Runtime dispatch selection | [`noSSBOtest` and `test`](../../../modules/vulkan/subgroups/vktSubgroupsPartitionedTests.cpp#L403-L519) | Routes each registered family to the relevant common harness. |
| Compute shader shell and resource declarations | [`getBufferDeclarations` and `initStdPrograms`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L1373-L1434) | Shows how `data[]`, `result[]`, offsets, specialization constants, and generated test text become a compute shader. |
| Host result predicate | [`check` and `checkComputeOrMesh`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L2640-L2663) | Requires every produced value to equal the supplied `0xFFFFFF` reference. |
| Subgroup scan naming and comparisons | [`getScanOpName`](../../../modules/vulkan/subgroups/vktSubgroupsScanHelpers.cpp#L39-L79) and [`getCompare`](../../../modules/vulkan/subgroups/vktSubgroupsScanHelpers.cpp#L304-L349) | Produces operation names and exact or tolerance-based comparison expressions. |
| Vulkan subgroup and arithmetic semantics | [`shaders.adoc`](../../../../vulkan-docs/src/chapters/shaders.adoc#L3220-L3247) and [`shaders.adoc`](../../../../vulkan-docs/src/chapters/shaders.adoc#L3447-L3511) | Defines subgroup scope, group operations, reductions, and inclusive and exclusive scans. |
| NV partitioned feature contract | [`VK_NV_shader_subgroup_partitioned.adoc`](../../../../vulkan-docs/src/appendices/VK_NV_shader_subgroup_partitioned.adoc#L17-L36) | Connects the Vulkan feature bit to the GLSL and SPIR-V partitioned operation extensions. |
| Representative mustpass leaf | [`subgroups.txt`](../../../mustpass/main/vk-default/subgroups.txt#L22582) | Confirms `dEQP-VK.subgroups.partitioned.compute.subgroupadd_float`. |

## Questions / Risk Points for User Audit

- The behavior axis is the five registered execution families because each changes pipeline construction, result transport, and stage coverage. Operation, scan, and format remain important matrix dimensions rather than the primary page-level behavior axis.
- The representative leaf name is easy to misread: `subgroupadd_float` is registered, but `subgroupPartitionedAddNV` is the operation being tested and `subgroupAdd` is the reference.
- The full 24-bit mask checks several semantic scenarios at once. A failed host value identifies a shader check failure, but the common callback does not decode which bit was missing.
- Ray tracing and graphics helpers can execute several supported stages. A family-level failure may need the CTS log and stage-specific rerun to identify the affected stage.

## Conversion Notes for Final Wiki Rewrite

- Use `dEQP-VK.subgroups.partitioned.compute.subgroupadd_float` for the representative shader walkthrough.
- Use exact source file `external/vulkancts/modules/vulkan/subgroups/vktSubgroupsPartitionedTests.cpp` and exact builder `initPrograms`; expand its call to the common `subgroups::initStdPrograms` compute branch.
- Distill subgroup partitions and divergent ordinary subgroup references into the final Background Knowledge section.
- Keep the registration-to-invocation distinction prominent in the parameter table and walkthrough.
- Copy the `### Failure Cause Mapping` table above directly into the final page.
- Keep detailed helper and source navigation in the final appendix.
