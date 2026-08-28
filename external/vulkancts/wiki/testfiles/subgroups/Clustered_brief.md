# Understanding Brief: `subgroups.clustered`

## One-Sentence Test Purpose

This test checks whether clustered subgroup add, multiply, minimum, maximum, AND, OR, and XOR produce the reference result for each consecutive power-of-two cluster across supported data types and shader stages.

## Background Knowledge

### Clustered subgroup operations

A subgroup is a set of shader invocations that can exchange data and perform collective operations. A clustered operation divides that subgroup into consecutive partitions. Each partition has a power-of-two invocation count known when the pipeline is created, and an invocation receives the collective result for its own partition. The Vulkan specification permits add, multiply, minimum, maximum, AND, OR, and XOR for this operation class [shaders.adoc#L3543-L3552](../../../../vulkan-docs/src/chapters/shaders.adoc#L3543-L3552).

Why it matters here:

- The expected value depends on the invocation's cluster, not on the whole subgroup.
- The test emits one call for each power-of-two cluster size from 1 through 128 and executes calls whose cluster size does not exceed `gl_SubgroupSize`.

### Active invocation mask and independent reference calculation

The shader takes `subgroupBallot(true)` before it checks the clustered result. It then computes a reference value by visiting the active invocation bits in each cluster and applying the matching scalar or vector operation. This creates an independent in-shader reference instead of trusting another clustered collective.

## One Concrete Example

The executable case `dEQP-VK.subgroups.clustered.compute.subgroupclusteredadd_uint` selects compute execution, unsigned 32-bit scalar data, and `subgroupClusteredAdd`. For cluster size 4, invocation 6 belongs to the consecutive cluster containing invocation IDs 4 through 7. The shader computes:

```glsl
// Simplified from the generated cluster-size-4 block.
uint op = subgroupClusteredAdd(data[gl_SubgroupInvocationID], 4u);
uint ref = uint(0);
for (uint index = 4u; index < 8u; ++index)
{
    if (subgroupBallotBitExtract(mask, index))
        ref = ref + data[index];
}
if (op != ref)
    tempResult = false;
```

The generated shader repeats this check for every consecutive four-invocation cluster and for the other supported power-of-two cluster sizes.

## End-to-End Test Flow

```text
[host] select operation, data type, stage family, and required-subgroup-size mode
[host] reject unsupported subgroup, clustered-operation, format, stage, or size-control combinations
[host] initialize nonzero input values for up to 128 subgroup invocations
[host] compile the generated stage program with SPIR-V 1.3, or SPIR-V 1.4 for ray tracing and mesh stages
[host] create stage-specific output and input resources, pipelines, and descriptors
[host] dispatch, draw, or trace work through the shared subgroup harness
[device] ballot active invocations and run every legal power-of-two clustered operation
[device] calculate the same operation over each cluster from the input array
[device] write 1 when every clustered result matches, otherwise write 0
[host] read the result buffer or framebuffer output and require every checked value to equal 1
```

Required-subgroup-size compute and mesh cases repeat the execution for each power-of-two size from the device's reported minimum through maximum.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- [`getTestSrc`](../../../modules/vulkan/subgroups/vktSubgroupsClusteredTests.cpp#L115-L159) generates the ballot, all cluster-size blocks, the operation-specific identity and reference expression, and the final `tempRes` assignment.
- [`initPrograms`](../../../modules/vulkan/subgroups/vktSubgroupsClusteredTests.cpp#L171-L186) passes that body to the common stage builder. It requests SPIR-V 1.3 for compute and ordinary graphics stages, and SPIR-V 1.4 for ray tracing and mesh stages.
- [`initFrameBufferPrograms`](../../../modules/vulkan/subgroups/vktSubgroupsClusteredTests.cpp#L161-L169) builds the framebuffer variants with SPIR-V 1.3.
- Compute and mesh local sizes use specialization IDs 0, 1, and 2 in the common [`initStdPrograms`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L1406-L1461) wrapper.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Input `data[]` buffer | yes | yes | read | no | Supplies one nonzero scalar or vector per possible subgroup invocation for both the collective and reference calculation. |
| Result SSBO for compute, graphics, mesh, and ray tracing paths | yes | yes | write | yes | Stores `1` or `0` for each tested invocation. |
| Framebuffer-path input UBO | yes | yes | read | no | Supplies the same input array where the tested graphics stage cannot use the ordinary SSBO path. |
| `R32_UINT` color target and transfer buffer | yes | yes | write and copy | yes | Carries framebuffer-stage `tempRes` values back to the host. |
| Ballot mask | no | no | shader-local read/write | no | Records active subgroup invocations for the independent reference calculation. |

## What Is Checked

- Each shader invocation starts with `tempResult = true` and changes it to false if any legal cluster-size result differs from the independently accumulated reference.
- Integer, Boolean, and floating-point minimum and maximum comparisons are exact. Integer and Boolean add, multiply, and bitwise comparisons are exact.
- Floating-point add and multiply use the tolerance emitted by [`getCompare`](../../../modules/vulkan/subgroups/vktSubgroupsScanHelpers.cpp#L304-L348), with larger limits for subgroup size 128 and for 16-bit floating point.
- The device writes `1` only if all emitted checks pass. Shared callbacks [`check`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L2640-L2653) and [`checkComputeOrMesh`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L2655-L2663) reject any checked output value other than `1`.

## Behavior Parameter Identification

> **Behavior parameter:** clustered operation
>
> **Candidate values:** `subgroupClusteredAdd`, `subgroupClusteredMul`, `subgroupClusteredMin`, `subgroupClusteredMax`, `subgroupClusteredAnd`, `subgroupClusteredOr`, `subgroupClusteredXor`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `subgroupClusteredAdd` | Incorrect clustered partitioning or add reduction for the selected type, cluster size, or stage. |
| `subgroupClusteredMul` | Incorrect clustered partitioning or multiply reduction for the selected type, cluster size, or stage. |
| `subgroupClusteredMin` | Incorrect clustered partitioning, minimum reduction, signedness, or floating-point minimum handling. |
| `subgroupClusteredMax` | Incorrect clustered partitioning, maximum reduction, signedness, or floating-point maximum handling. |
| `subgroupClusteredAnd` | Incorrect clustered partitioning or component-wise Boolean/integer AND reduction. |
| `subgroupClusteredOr` | Incorrect clustered partitioning or component-wise Boolean/integer OR reduction. |
| `subgroupClusteredXor` | Incorrect clustered partitioning or component-wise Boolean/integer XOR reduction. |

A failure in any row can also come from incorrect active-lane ballot handling, input/result transport, or host readback in the selected stage harness.

## Important Variations and Special Cases

- The source registers scalar and vector formats for signed integers, unsigned integers, floating point, double precision, Boolean values, 8-bit and 16-bit extended types, and long vectors where available.
- Floating-point formats do not pair with bitwise operations. Boolean formats pair only with bitwise operations. These exclusions keep each generated operation legal and meaningful.
- `compute` and `mesh` add `_requiredsubgroupsize` leaves. The host repeats those cases across the supported required subgroup size range.
- `framebuffer` covers vertex, tessellation control, tessellation evaluation, and geometry stages through a UBO plus color-output path.
- `ray_tracing` and `mesh` are absent from Vulkan SC registration. The ray tracing format set is also narrower than the general format set.
- `test-issues.txt` contains no exclusion for `subgroups.clustered` [test-issues.txt#L1-L27](../../../mustpass/main/src/test-issues.txt#L1-L27).

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Clustered body generator | [`getTestSrc`](../../../modules/vulkan/subgroups/vktSubgroupsClusteredTests.cpp#L115-L159) | Emits every cluster-size call and its independent reference loop. |
| Program builders | [`initFrameBufferPrograms` and `initPrograms`](../../../modules/vulkan/subgroups/vktSubgroupsClusteredTests.cpp#L161-L186) | Select stage wrappers and SPIR-V targets. |
| Support checks | [`supportedCheck`](../../../modules/vulkan/subgroups/vktSubgroupsClusteredTests.cpp#L188-L254) | Defines subgroup, clustered feature, format, stage, and size-control requirements. |
| Runtime routing | [`noSSBOtest` and `test`](../../../modules/vulkan/subgroups/vktSubgroupsClusteredTests.cpp#L256-L377) | Routes cases through framebuffer, compute, graphics, ray tracing, or mesh helpers. |
| Registration matrix | [`createSubgroupsClusteredTests`](../../../modules/vulkan/subgroups/vktSubgroupsClusteredTests.cpp#L384-L566) | Registers stage families, operations, formats, pruning, and required-size variants. |
| Operation helpers | [`vktSubgroupsScanHelpers.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsScanHelpers.cpp#L39-L348) | Supplies operation names, identities, reference expressions, and comparisons. |
| Result callbacks | [`check` and `checkComputeOrMesh`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L2640-L2663) | Require every read-back value to equal 1. |
| Vulkan clustered semantics | [`shaders.adoc`](../../../../vulkan-docs/src/chapters/shaders.adoc#L3543-L3552) | Defines consecutive power-of-two partitions and supported operations. |
| Clustered capability bit | [`limits.adoc`](../../../../vulkan-docs/src/chapters/limits.adoc#L1461-L1463) | Connects `VK_SUBGROUP_FEATURE_CLUSTERED_BIT` to the SPIR-V clustered capability. |
| Mustpass representative leaf | [`vk-default/subgroups.txt`](../../../mustpass/main/vk-default/subgroups.txt#L18606) | Confirms the representative compute add case is present in current mustpass data. |

## Questions / Risk Points for User Audit

- Is the clustered operation the right primary behavioral axis, with stage family, format, cluster size, and required subgroup size treated as secondary dimensions?
- Does the concrete cluster-size-4 example make the consecutive partition rule clear?
- Does the resource table distinguish the ordinary SSBO path from the framebuffer UBO and color-output path?
- The exact failing cluster size is not written to a diagnostic buffer. Failure localization therefore depends on the case path, stage, format, host log for required subgroup size, and further source-level investigation.

## Conversion Notes for Final Wiki Rewrite

- Use `dEQP-VK.subgroups.clustered.compute.subgroupclusteredadd_uint` for the representative compute walkthrough.
- Keep clustered partition semantics and the active-mask reference method as short Background Knowledge bullets.
- Carry the clustered operation axis into `## Behavior Parameters` and copy the Failure Cause Mapping table without edits.
- Move source navigation to the appendix and keep the stage-specific resource and readback differences in the runtime section.
- Reconstruct the compute shader from `initPrograms`, `getTestSrc`, and the common `initStdPrograms` wrapper, then generate its SPIR-V 1.3 artifact with the CCVDO workflow.
