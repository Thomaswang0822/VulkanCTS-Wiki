# Understanding Brief: NV compute subgroup built-ins

## One-Sentence Test Purpose

This test checks whether compute-shader subgroup built-ins retain their specified values when a dispatch runs through either a normal compute pipeline or an NV device-generated command pipeline.

## Background Knowledge

### Subgroups inside a compute workgroup

A compute workgroup is divided into subgroups. Each invocation belongs to one subgroup and receives a subgroup-local invocation ID. The subgroup size is selected for the pipeline in this test, so a workgroup whose local size is `workgroupSize` contains `workgroupSize / subgroupSize` subgroups.

Why it matters here:
- `gl_NumSubgroups`, `gl_SubgroupID`, `gl_SubgroupSize`, and `gl_SubgroupInvocationID` describe that partition.
- The ballot masks encode ordering relative to the current `gl_SubgroupInvocationID`. Bits outside the actual subgroup size must remain zero.

### Subgroup ballot masks

The KHR subgroup ballot built-ins return a `uvec4` mask. Bit `i` describes the invocation with subgroup-local ID `i`. In this test, the expected masks are equality, greater-than-or-equal, greater-than, less-than-or-equal, and less-than comparisons with the current invocation ID.

Why it matters here:
- The shader can check the masks without relying on host-side knowledge of the implementation's subgroup layout.
- The same checks run for normal and generated-command execution, so a failure points to the observed subgroup values or to the path that launched the shader.

## One Concrete Example

For the conceptual case `workgroupSize = 64` and `subgroupSize = 32`, one dispatch launches 64 invocations and should produce two subgroups. An invocation with `gl_SubgroupInvocationID = 7` should report a subgroup ID in `[0, 1]`, a subgroup size of 32, and a mask pattern with zero bits below 7, the expected bit at 7, and the comparison-specific bits above 7. The shader writes one Boolean result for each check and each invocation.

## End-to-End Test Flow

```text
[host] choose workgroup size, subgroup size, pipeline mode, and queue mode
[host] check DGC, Vulkan 1.3, required subgroup-size, size-range, and queue support
[host] generate the compute GLSL with the selected local size and expected subgroup count
[host] create nine host-visible storage buffers and bind them at descriptor bindings 0 through 8
[host] create a normal compute pipeline or an NV DGC compute pipeline with the required subgroup size
[host] create an indirect-command layout and a host-visible command stream containing dispatch (1, 1, 1)
[host] prepare preprocessing for one sequence
[host] bind descriptors and either bind the normal pipeline or update the DGC pipeline indirect buffer
[host] execute the generated command sequence
[device] run the compute shader and write nine Boolean verification arrays
[host] wait for completion, read every output buffer, and compare every element with 1
[host] report pass or log each unexpected binding and position as a failure
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The test builds a `#version 460` compute shader from a C++ string. It enables `GL_KHR_shader_subgroup_basic` and `GL_KHR_shader_subgroup_ballot`, sets `local_size_x` to `totalInvocations`, and embeds the expected subgroup count and subgroup size. The build requests SPIR-V 1.6. The command stream contains a pipeline device address when `pipelineToken` is true, followed by dispatch dimensions `1, 1, 1`.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Nine storage buffers at bindings 0 through 8 | yes | yes | written | yes | They hold one Boolean check array each. |
| Indirect command buffer | yes | yes | read | no | It supplies the generated pipeline address when needed and the dispatch dimensions. |
| Preprocess buffer | yes | yes | written/read by DGC machinery | no | It stores preprocessing data for one generated-command sequence. |
| Pipeline and pipeline layout | yes | used by compute | used to execute the shader | no | The pipeline path is one of the tested dimensions. |

The nine output buffers correspond to `gl_NumSubgroups`, `gl_SubgroupID`, `gl_SubgroupSize`, `gl_SubgroupInvocationID`, `gl_SubgroupEqMask`, `gl_SubgroupGeMask`, `gl_SubgroupGtMask`, `gl_SubgroupLeMask`, and `gl_SubgroupLtMask`. The subgroup masks are shader values, not host-created subgroup objects.

## What Is Checked

- Every output buffer contains `totalInvocations` `uint` values.
- The shader stores `1` when its built-in or mask comparison succeeds and `0` otherwise.
- The host initializes all nine buffers to zero, copies each buffer back after a shader-write to host-read barrier, and requires every element in every buffer to equal `1`.
- The host logs the binding and element position for each mismatch and returns a failing test status if it finds any mismatch.

## Behavior Parameter Identification

> **Behavior parameter:** `subgroup_size`
>
> **Candidate values:** `16`, `32`, `64`, `128`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `16` | The implementation reports or evaluates subgroup built-ins or ballot masks incorrectly for 16-wide subgroups, or the selected pipeline and queue path does not preserve those values. |
| `32` | The implementation reports or evaluates subgroup built-ins or ballot masks incorrectly for 32-wide subgroups, or the selected pipeline and queue path does not preserve those values. |
| `64` | The implementation reports or evaluates subgroup built-ins or ballot masks incorrectly for 64-wide subgroups, or the selected pipeline and queue path does not preserve those values. |
| `128` | The implementation reports or evaluates subgroup built-ins or ballot masks incorrectly for 128-wide subgroups, or the selected pipeline and queue path does not preserve those values. |

## Important Variations and Special Cases

- `workgroupSize` and `subgroupSize` each use `16`, `32`, `64`, and `128`, but the test keeps only pairs where `subgroupSize <= workgroupSize`.
- Each retained size pair runs with `pipelineToken = false` and `true`. The first uses a normal compute pipeline. The second places the DGC compute pipeline device address in the generated command stream.
- Each pipeline mode runs on the universal queue and, with `_cq` appended to the test name, on the compute queue.
- A compute-queue case is supported only when `context.getComputeQueue()` succeeds. The test also requires Vulkan 1.3, a subgroup size within `minSubgroupSize` and `maxSubgroupSize`, and compute in `requiredSubgroupSizeStages`.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Parameter structure and support checks | [BuiltinParams and checkSubgroupSupport](../../../modules/vulkan/device_generated_commands/vktDGCComputeSubgroupTests.cpp#L50-L81) | Defines the four parameter dimensions and support gates. |
| Generated verification shader | [builtinVerificationProgram](../../../modules/vulkan/device_generated_commands/vktDGCComputeSubgroupTests.cpp#L83-L171) | Generates the subgroup built-in and mask checks. |
| Resources, command execution, and host check | [verifyBuiltins](../../../modules/vulkan/device_generated_commands/vktDGCComputeSubgroupTests.cpp#L173-L355) | Shows descriptor bindings, normal versus DGC pipeline setup, dispatch, barrier, and result validation. |
| Test-name generation and matrix | [createDGCComputeSubgroupTests](../../../modules/vulkan/device_generated_commands/vktDGCComputeSubgroupTests.cpp#L359-L388) | Registers the `builtins` test family and all retained variants. |
| Mustpass variants | [dgc.txt subgroup entries](../../../mustpass/main/vk-default/dgc.txt#L448-L487) | Records the 40 registered NV-style subgroup paths in the current mustpass file. |

## Questions / Risk Points for User Audit

- Does the distinction between subgroup-local IDs and workgroup-local indexing read clearly?
- Is the normal-pipeline versus DGC-pipeline distinction clear enough for the generated command stream?
- Are the nine output arrays and the all-elements-equal-to-1 rule sufficient to explain the result check?
- Should the brief call out any implementation-specific subgroup behavior beyond the Vulkan requirements used by the source?

## Conversion Notes for Final Wiki Rewrite

- Keep `subgroup_size` as the primary behavioral axis and retain the four-value failure mapping table.
- Distill the subgroup and ballot-mask explanations into short page-local background bullets.
- Use the generated shader, command stream, nine output buffers, barrier, and host scan as the page's execution narrative.
- Preserve all registered test names in the final page, while using the hierarchy tree only for the compact `dgc.nv.compute.subgroups` to `builtins` structure.
- The final page should explain the `subgroupSize > workgroupSize` design exclusion separately from support-based pruning.
