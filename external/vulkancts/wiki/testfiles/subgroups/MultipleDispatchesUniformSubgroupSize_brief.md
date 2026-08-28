# Understanding Brief: Multiple Dispatches with Uniform Subgroup Size

## One-Sentence Test Purpose

This test checks whether a compute dispatch that allows varying subgroup sizes still reports one `gl_SubgroupSize` value throughout that dispatch's command scope and forms the expected number of subgroups.

## Background Knowledge

### Command scope and varying subgroup size

A command scope instance contains the shader invocations produced by one command such as `vkCmdDispatch`. When a compute pipeline uses `VK_PIPELINE_SHADER_STAGE_CREATE_ALLOW_VARYING_SUBGROUP_SIZE_BIT_EXT`, Vulkan permits the implementation to choose a subgroup size instead of fixing it to the device's ordinary `subgroupSize`. The selected `SubgroupSize` must still be uniform within the command scope of a compute dispatch [interfaces.adoc](../../../../vulkan-docs/src/chapters/interfaces.adoc#L5199-L5231), [shaders.adoc](../../../../vulkan-docs/src/chapters/shaders.adoc#L3104-L3127), [pipelines.adoc](../../../../vulkan-docs/src/chapters/pipelines.adoc#L1419-L1428).

Why it matters here:

- The test issues a separate `vkCmdDispatch` for each local workgroup size. It checks uniformity within each dispatch, not equality between different dispatches.
- A subgroup size may be implementation-selected for this pipeline, but every subgroup participating in one compute command must report the same value.

### One report per subgroup

`subgroupElect()` selects one invocation from each subgroup. The shader lets only that invocation write, so each subgroup produces one record without multiple invocations racing on the same slot. `gl_SubgroupID` identifies the subgroup within the workgroup, and `gl_NumSubgroups` gives the number of subgroups in that workgroup [shaders.adoc](../../../../vulkan-docs/src/chapters/shaders.adoc#L3463-L3471), [interfaces.adoc](../../../../vulkan-docs/src/chapters/interfaces.adoc#L3891-L3916), [interfaces.adoc](../../../../vulkan-docs/src/chapters/interfaces.adoc#L4955-L4981).

Why it matters here:

- Every nonzero result-buffer entry should represent one subgroup.
- If a workgroup has local size `L` and the reported subgroup size is `S`, the expected record count is `ceil(L / S)`.

## One Concrete Example

The only executable test case is `dEQP-VK.subgroups.multiple_dispatches.uniform_subgroup_size`. Consider its pipeline variant with specialization constant `local_size_x_id = 0` set to `8`.

The following GLSL is reconstructed from `MultipleDispatchesUniformSubgroupSize::initPrograms`; comments beginning with `///` explain the test-facing role of each part.

```glsl
#version 450
#extension GL_KHR_shader_subgroup_basic : enable
#extension GL_KHR_shader_subgroup_vote : enable
#extension GL_KHR_shader_subgroup_ballot : enable

/// Binding 0 is a host-visible storage buffer cleared before this dispatch.
/// One elected invocation per subgroup writes that subgroup's reported size.
layout(std430, binding = 0) buffer Outputs { uint sizes[]; };

/// Specialization constant 0 supplies the X local workgroup size for each pipeline variant.
layout(local_size_x_id = 0) in;

void main()
{
    if (subgroupElect())
    {
        /// This test dispatches one workgroup, so gl_WorkGroupID.x is zero.
        /// gl_SubgroupID therefore selects a unique record for each subgroup.
        sizes[gl_WorkGroupID.x * gl_NumSubgroups + gl_SubgroupID] = gl_SubgroupSize;
    }
}
```

For example, if the implementation chooses subgroup size `4`, the eight invocations form two subgroups. Two elected invocations write `4`, and the host expects exactly `ceil(8 / 4) = 2` nonzero entries. If the implementation chooses subgroup size `8`, one elected invocation writes `8`, and the expected count is one. The test accepts either result because it checks command-scope uniformity rather than requiring a particular subgroup size.

## End-to-End Test Flow

```text
[host] reject the case if subgroupSizeControl is unsupported
[host] generate one compute shader with specialization-controlled local_size_x
[host] allocate one host-visible storage buffer sized for the maximum possible subgroup count
[host] create pipeline variants for local sizes 1, 2, 4, ... up to maxComputeWorkGroupSize[0]
[host] begin one command buffer for the selected local size and clear the result buffer to zero
[host] apply a transfer-write to shader-write buffer barrier
[host] bind the matching pipeline and descriptor set, then record vkCmdDispatch(1, 1, 1)
[device] form subgroups for the one local workgroup
[device] elect one invocation per subgroup and write gl_SubgroupSize at that subgroup's index
[host] apply a shader-write to host-read memory barrier, submit, and wait
[host] invalidate the host-visible allocation and scan every nonzero report
[host] require all reports from this dispatch to match and require count = ceil(localSize / reportedSize)
[host] repeat the command-scope check for the next local-size pipeline
```

Each loop iteration records and submits one dispatch. The buffer clear prevents reports from an earlier command from being mistaken for reports from the current command [iterate](../../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L160-L241).

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `MultipleDispatchesUniformSubgroupSize::initPrograms` emits one GLSL 4.50 compute shader and requests SPIR-V 1.3 through `ShaderBuildOptions` [initPrograms](../../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L270-L291).
- `local_size_x_id = 0` maps the X local size to specialization constant ID `0`. The host creates one pipeline per power-of-two local size from `1` through `maxComputeWorkGroupSize[0]` [pipeline creation](../../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L115-L158).
- Every pipeline sets `VK_PIPELINE_SHADER_STAGE_CREATE_ALLOW_VARYING_SUBGROUP_SIZE_BIT_EXT`, which activates the varying-size behavior under test [pipeline stage](../../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L135-L155).

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Result storage buffer | yes | yes, descriptor binding `0` | written by one elected invocation per subgroup | yes | Holds one `gl_SubgroupSize` report per subgroup for the current dispatch. |
| Compute shader module | yes, from generated SPIR-V | yes, in each compute pipeline | executed | no | Implements subgroup election and size reporting. |
| Pipeline variants | yes | yes | select the specialized local size and allow varying subgroup size | no | Exercise a sequence of power-of-two workgroup sizes with the same shader logic. |
| Command buffer | yes | submitted to the universal queue | carries fill, barrier, dispatch, and visibility commands | no | Gives each tested local size its own dispatch command scope and ordered readback path. |

The result buffer contains `(maxLocalSize / minSubgroupSize + 1)` 32-bit entries. This covers the largest subgroup count implied by the tested local-size range, with one extra entry [result buffer allocation](../../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L77-L87).

## What Is Checked

For each specialized local size, the host checks the current dispatch independently:

- At least one nonzero report must exist. A zero-only buffer fails because subgroup size cannot be zero.
- Every nonzero report must equal the first nonzero report. A mismatch means `SubgroupSize` was not uniform in that command scope.
- The number of nonzero reports must equal `localSize / size`, rounded up. A mismatch means the shader did not produce exactly one report per subgroup under the subgroup partition implied by the reported size.
- Reports from different dispatches are not compared. Vulkan permits a pipeline that allows varying subgroup size to use different sizes in separate command scopes.

The host implements these checks in `MultipleDispatchesUniformSubgroupSizeInstance::iterate` [validation](../../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L196-L240).

## Behavior Parameter Identification

> **Behavior parameter:** fixed test case leaf
>
> **Candidate values:** `uniform_subgroup_size`

The test family has one executable leaf and no registered multi-value behavior axis. Power-of-two local sizes are runtime pipeline variants inside that leaf, so they belong in the parameter inventory rather than becoming separate behavior-parameter values.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `uniform_subgroup_size` | Non-uniform `SubgroupSize` within one compute command scope, incorrect subgroup formation or built-in reporting, missing subgroup reports, or a broken clear/synchronization/readback path. |

## Important Variations and Special Cases

- The local-size specialization values are `1, 2, 4, ...` through `maxComputeWorkGroupSize[0]`. They exercise workgroups smaller than, equal to, and potentially larger than an implementation-selected subgroup size.
- The final subgroup may contain fewer active invocations when the local size is not divisible by the selected subgroup size. The expected count uses ceiling division, so this partial subgroup is part of the accepted model.
- `VK_PIPELINE_SHADER_STAGE_CREATE_REQUIRE_FULL_SUBGROUPS_BIT_EXT` is not set. The test checks uniform subgroup size and subgroup count; it does not require every launched subgroup to be full.
- The source enables subgroup vote and ballot GLSL extensions as well as the basic extension, but the executable shader operation used for reporting is `subgroupElect()`.
- `external/vulkancts/mustpass/main/src/test-issues.txt` has no exclusion matching this test. The exact case appears in the default subgroup mustpass list [subgroups.txt](../../../mustpass/main/vk-default/subgroups.txt#L22567).

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Registered test category path | [vktSubgroupsTests.cpp](../../../modules/vulkan/subgroups/vktSubgroupsTests.cpp#L70-L80) | Attaches the `multiple_dispatches` test family under `subgroups`. |
| Executable test case registration | [createMultipleDispatchesUniformSubgroupSizeTests](../../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L301-L307) | Registers the `multiple_dispatches.uniform_subgroup_size` path. |
| Support gate | [checkSupport](../../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L262-L268) | Rejects devices without `subgroupSizeControl`. |
| Shader generation and SPIR-V target | [initPrograms](../../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L270-L291) | Emits the exact compute shader and selects SPIR-V 1.3. |
| Resources and pipeline variants | [iterate setup](../../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L61-L158) | Allocates the result buffer and creates specialized pipelines that allow varying subgroup size. |
| Dispatch, barriers, and validation | [iterate execution](../../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L160-L243) | Clears, dispatches, reads back, and checks uniformity plus subgroup count. |
| Command-scope definition | [shaders.adoc](../../../../vulkan-docs/src/chapters/shaders.adoc#L3104-L3127) | Defines the scope produced by one dispatch command. |
| Compute `SubgroupSize` rule | [interfaces.adoc](../../../../vulkan-docs/src/chapters/interfaces.adoc#L5199-L5231) | Requires compute `SubgroupSize` to be uniform with command scope when varying size is allowed. |
| Varying-size pipeline flag | [pipelines.adoc](../../../../vulkan-docs/src/chapters/pipelines.adoc#L1419-L1441) | Defines the pipeline flag used by every variant. |
| Default mustpass case | [subgroups.txt](../../../mustpass/main/vk-default/subgroups.txt#L22567) | Confirms the exact executable path. |

## Questions / Risk Points for User Audit

- Does the distinction between uniformity within one dispatch and permitted variation between dispatches read clearly?
- Is the single fixed behavior parameter preferable to treating internal local-size pipeline variants as a behavioral axis?
- Does the subgroup-count check make clear that it validates one elected report per subgroup rather than enforcing a required subgroup size?
- Are the result-buffer clear and both visibility barriers explained at the right depth?

No unresolved source, registration, mustpass, shader, or specification question changes the page semantics or representative walkthrough selection.

## Conversion Notes for Final Wiki Rewrite

- Keep command scope, varying subgroup size, and election as concise Background Knowledge prerequisites.
- Use `dEQP-VK.subgroups.multiple_dispatches.uniform_subgroup_size` for the representative shader walkthrough and preserve the exact shader emitted by `MultipleDispatchesUniformSubgroupSize::initPrograms`.
- Carry the fixed test case leaf conclusion into `## Behavior Parameters`; describe local sizes under parameter dimensions.
- Copy the `### Failure Cause Mapping` table above directly into the final page.
- Keep the repeated dispatch sequence, buffer clear, barriers, and independent per-dispatch checks in the runtime section.
- Move source navigation details to the final appendix and remove brief-only review scaffolding.
