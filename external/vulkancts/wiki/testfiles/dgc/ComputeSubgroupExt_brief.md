# Understanding Brief: EXT compute subgroup builtins

## One-Sentence Test Purpose

This test checks whether an EXT device-generated compute dispatch preserves Vulkan subgroup built-in values and subgroup masks for selected workgroup and subgroup sizes.

## Background Knowledge

### Subgroups inside a compute workgroup

A compute workgroup is divided into subgroups for SIMD-style execution. Each invocation has a subgroup ID and invocation ID. The subgroup also provides a size and masks that describe the current invocation's position. A required subgroup size requests a specific size for the compute shader, subject to device limits and compute-stage support.

Why it matters here:
- The shader uses `gl_NumSubgroups`, `gl_SubgroupID`, `gl_SubgroupSize`, and `gl_SubgroupInvocationID` to derive expected relationships.
- The ballot masks `gl_SubgroupEqMask`, `gl_SubgroupGeMask`, `gl_SubgroupGtMask`, `gl_SubgroupLeMask`, and `gl_SubgroupLtMask` must contain the expected bits within the subgroup and zero bits beyond it.

### EXT device-generated compute commands

`VK_EXT_device_generated_commands` lets an application describe a command sequence with tokens, place token data in a buffer, and ask Vulkan to generate and execute the command. This test uses a dispatch token and, for one mode, an execution-set pipeline token. Preprocessing uses a separate buffer. The host waits for completion before it reads the output buffers.

## One Concrete Example

For `dEQP-VK.dgc.ext.compute.subgroups.builtins.workgroup_size_32_subgroup_size_16_normal_pipeline`, the generated compute shader has `local_size_x=32`, and the normal compute pipeline requests subgroup size 16. Each invocation writes nine boolean checks to nine storage buffers. The checks cover the number of subgroups, subgroup and invocation IDs, subgroup size, and the five subgroup masks. A correct run writes `1` for every check.

## End-to-End Test Flow

```text
[host] choose workgroup size, subgroup size, pipeline-token mode, and queue
[host] reject unsupported Vulkan, DGC, subgroup-size, or queue combinations
[host] generate the compute shader and compile it to SPIR-V 1.6
[host] create nine host-visible storage buffers and bind them at bindings 0 through 8
[host] create a normal compute pipeline or an EXT DGC compute pipeline with the required subgroup size
[host] create a layout containing an optional compute-pipeline token followed by a dispatch token
[host] write the pipeline index when needed and write dispatch dimensions (1, 1, 1) to the generated-command buffer
[host] create a preprocess buffer for one sequence
[host] bind descriptors and the selected pipeline, execute generated commands, add a shader-write to host-read barrier, and submit
[device] execute 32, 64, or 128 local invocations in the selected subgroup arrangement
[device] write one result per invocation to each of the nine output buffers
[host] wait for the queue, read every output buffer, and compare every value with `1`
[host] return pass only when all values match
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

`builtinVerificationProgram` builds one compute GLSL source string for each parameter combination. The shader sets `local_size_x` to the selected workgroup size, enables `GL_KHR_shader_subgroup_basic` and `GL_KHR_shader_subgroup_ballot`, and uses `ShaderBuildOptions` with SPIR-V 1.6. The command stream contains an optional pipeline index followed by dispatch dimensions `1, 1, 1`.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Nine storage buffers | yes | yes, bindings 0 through 8 | device writes one boolean per invocation | yes | one buffer records each subgroup built-in or mask check |
| Descriptor set and layout | yes | yes | device uses it to find the nine buffers | no | maps each verification buffer to its shader binding |
| Generated-command buffer | yes | yes by device address | DGC reads it | no | carries the optional pipeline index and dispatch token data |
| Preprocess buffer | yes | yes by device address | preprocessing writes or consumes its state | no | stores preprocessing data for one generated-command sequence |

The GLSL `verification[]` arrays view the nine storage buffers. They do not add host allocations.

## What Is Checked

The shader writes `1` when a check passes and `0` otherwise. It checks that:

- `gl_NumSubgroups` equals `totalInvocations / subgroupSize`.
- `gl_SubgroupID` and `gl_SubgroupInvocationID` stay in their valid ranges.
- `gl_SubgroupSize` equals the requested subgroup size.
- Each mask has the expected less-than, equal, and greater-than bit pattern for the current invocation. Bits outside `gl_SubgroupSize` must stay clear.

The host scans all nine buffers and every invocation entry. It logs the binding and position for each value other than `1`, then fails the test if it finds a mismatch.

## Behavior Parameter Identification

> **Behavior parameter:** pipeline and queue execution mode
>
> **Candidate values:** `normal_pipeline`, `dgc_pipeline`, `normal_pipeline_cq`, `dgc_pipeline_cq`

The workgroup and subgroup sizes define the subgroup arithmetic. These four registered suffix combinations choose whether the same compute behavior runs through a normal or DGC pipeline and through the default or compute queue. The source creates these modes as independent case dimensions.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `normal_pipeline` | Required subgroup-size or subgroup-built-in behavior in the normal compute pipeline path; common shader, descriptor, or result-readback validation |
| `dgc_pipeline` | The EXT execution-set, pipeline token, generated dispatch, preprocessing, or DGC compute pipeline path; common subgroup-built-in validation |
| `normal_pipeline_cq` | The normal pipeline path when submitted to the compute queue; queue selection or common subgroup-built-in validation |
| `dgc_pipeline_cq` | The DGC pipeline and generated-dispatch path when submitted to the compute queue; queue selection or common subgroup-built-in validation |

## Important Variations and Special Cases

The registration loop uses invocation counts `16`, `32`, `64`, and `128` for both workgroup and subgroup sizes. It keeps only subgroup sizes no larger than the workgroup size, so legal size pairs form a triangular matrix. Each legal pair uses both pipeline modes and both queue modes.

The test requests Vulkan 1.3 or newer. It requires compute-stage support for required subgroup sizes. It accepts only supported power-of-two subgroup sizes within `minSubgroupSize` and `maxSubgroupSize`. These checks remove unsupported cases before shader execution.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Parameter structure and support checks | [BuiltinParams and checkSubgroupSupport](../../../modules/vulkan/device_generated_commands/vktDGCComputeSubgroupTestsExt.cpp#L49-L84) | Defines the size, pipeline, queue, and support dimensions. |
| Generated verification shader | [builtinVerificationProgram](../../../modules/vulkan/device_generated_commands/vktDGCComputeSubgroupTestsExt.cpp#L86-L174) | Emits subgroup built-in and mask checks. |
| DGC execution and result scan | [verifyBuiltins](../../../modules/vulkan/device_generated_commands/vktDGCComputeSubgroupTestsExt.cpp#L176-L351) | Creates resources, executes generated commands, and checks all outputs. |
| Registration matrix | [createDGCComputeSubgroupTestsExt](../../../modules/vulkan/device_generated_commands/vktDGCComputeSubgroupTestsExt.cpp#L356-L384) | Registers the exact EXT paths and pruning rule. |
| DGC execution model | [Vulkan device-generated commands](../../../../vulkan-docs/src/chapters/device_generated_commands/generatedcommands.adoc#device-generated-commands) | Grounds layout, preprocessing, and execution terminology. |

## Questions / Risk Points for User Audit

- Is the pipeline and queue execution mode the right primary behavior axis for failure mapping?
- Is the distinction between the generated-command buffer and the preprocess buffer clear?
- Should the final page include a full shader walkthrough for the representative normal-pipeline case?

## Conversion Notes for Final Wiki Rewrite

- Distill the subgroup execution model into a short page-local prerequisite list.
- Keep the exact registered `builtins` hierarchy and generated case-name dimensions in the final page.
- Copy the failure mapping table into `## Failure Meaning` unchanged.
- Explain the normal and DGC pipeline paths together, then identify the DGC token and preprocessing differences.
- Use one representative generated GLSL walkthrough. Keep the full SPIR-V artifact in the walkthrough and place source links in the appendix.
