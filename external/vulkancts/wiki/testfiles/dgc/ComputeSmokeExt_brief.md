# Understanding Brief: EXT compute smoke tests

## One-Sentence Test Purpose

This test checks whether `VK_EXT_device_generated_commands` executes compute dispatch sequences correctly when command data comes from the host or a compute shader, with optional preprocessing and queue choices.

## Background Knowledge

### Generated compute commands

A DGC layout describes how the implementation interprets each sequence in an indirect buffer. This test uses one dispatch token, so each sequence is one `VkDispatchIndirectCommand` containing `x`, `y`, and `z` workgroup counts. `vkCmdExecuteGeneratedCommandsEXT` uses the layout and the buffer device address to execute those sequences.

### Preprocessing and synchronization

Explicit preprocessing records work needed before generated commands execute. The EXT specification separates preprocessing from execution and requires synchronization between them. The test compares no preprocessing, preprocessing with the main command buffer as state, and preprocessing with a separate state command buffer.

### Queue and memory scope

The compute shader increments a storage-buffer counter with `gl_ScopeQueueFamily` and acquire-release, make-available, and make-visible semantics. The test can submit on the universal queue or an available compute queue. The queue choice changes where the work runs, not the expected counter values.

## One Concrete Example

Suppose four generated sequences dispatch 22, 7, 53, and 30 workgroups. Each workgroup has 64 local invocations, and each invocation increments the counter for its flattened workgroup index. Counters `[0, 7)` receive `256`, `[7, 22)` receive `192`, `[22, 30)` receive `128`, `[30, 53)` receive `64`, and the rest remain zero. The actual case generates dimensions pseudorandomly from its parameter tuple and checks the corresponding ranges.

## End-to-End Test Flow

```text
[host] select sequence count, indirect-buffer memory, command source, preprocess mode, and queue
[host] generate one dispatch command per sequence and initialize the 256-entry result buffer to zero
[host] create the one-token DGC layout and preprocess buffer
[host] write commands to a host-visible source buffer
[host] optionally copy commands to device-local indirect memory, or bind source and destination for the generator shader
[host] record the generator dispatch or transfer and synchronize it with indirect command reads
[host] bind the fixed compute pipeline and descriptor set for the result buffer
[host] optionally preprocess generated commands in the main or separate state command buffer
[device] execute generated dispatch sequences from the indirect buffer
[device] atomically increment result counters for each flattened workgroup index
[host] synchronize shader writes with host reads, submit, wait, and copy the result buffer back
[host] reconstruct expected coverage ranges and decide pass or fail
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `comp` is inline GLSL with local size 64. It computes a flattened workgroup index and atomically increments `atomicCounters.value[index]`.
- `gen` is present only for `from_compute`. One workgroup copies the host-initialized command records into the indirect destination buffer.
- The indirect layout has compute shader stages and one `VK_INDIRECT_COMMANDS_TOKEN_TYPE_DISPATCH_EXT` token. `DGCGenCmdsInfo` has `VK_NULL_HANDLE` for `indirectExecutionSet`, so no execution-set pipeline or shader selection occurs.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|---|---|---|---|---|---|
| Initial command buffer | yes | yes for `gen`, or copied by transfer | read by `gen` or transfer | no | Holds host-generated `VkDispatchIndirectCommand` records. |
| Indirect command buffer | yes | consumed by DGC, and bound as `gen` output when needed | read by generated dispatch processing, optionally written by `gen` | no | Supplies dispatch dimensions. |
| `resultsBuffer` | yes, host-visible | `comp` binding 0 | atomically written by `comp` | yes | Records dispatch coverage. |
| Preprocess buffer | yes | passed to DGC preprocess/execute calls | written/read by DGC implementation | no | Stores explicit preprocessing state. |
| Compute pipeline and descriptor sets | yes | yes | pipeline executes `comp`; descriptors expose buffers | no | Keeps shader behavior fixed while the matrix changes command setup. |

## What Is Checked

- The host counts how many generated dispatches have a total workgroup count at or above each boundary.
- Each counter range must equal `64 * number_of_dispatches_covering_that_index`.
- Entries after the largest generated dispatch count must remain zero.
- The host performs the complete check after queue completion. A mismatch fails the case and logs all indirect commands and all result entries.

## Behavior Parameter Identification

> **Behavior parameter:** indirect-command preparation and execution path
>
> **Candidate values:** `from_host`, `from_compute`, `no_preprocess`, `preprocess_state_same`, `preprocess_state_separate`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `from_host` | Host initialization, transfer, device-address use, or DGC interpretation of host-provided command records. |
| `from_compute` | Generator shader writes, storage bindings, compute-to-indirect synchronization, or consumption of shader-produced command records. |
| `no_preprocess` | Implicit DGC preparation or direct generated execution. |
| `preprocess_state_same` | Explicit preprocessing with main-command-buffer state or its synchronization with execution. |
| `preprocess_state_separate` | Explicit preprocessing with separate state command-buffer state or its synchronization with execution. |

## Important Variations and Special Cases

- `host_visible` and `device_local` describe the indirect-command destination. The host-visible initial buffer exists in every case; device-local `from_host` variants add a transfer, and `from_compute` variants add a generator destination.
- `4` and `1024` are the only sequence counts. The `unordered` layout flag is set only for `1024`; the specification says it is ignored for compute because compute sequences are already unordered.
- The execution set is always absent. This is deliberate: the smoke test checks dispatch execution and result coverage with one fixed compute pipeline.

## Source Mapping

| Topic | Source link | Why it matters |
|---|---|---|
| Parameters and registration | [`vktDGCComputeSmokeTestsExt.cpp#L53-L73`](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTestsExt.cpp#L53-L73) | Defines matrix fields and preprocess modes. |
| Shader generation | [`vktDGCComputeSmokeTestsExt.cpp#L117-L193`](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTestsExt.cpp#L117-L193) | Defines counter updates and compute-side command copying. |
| Buffer paths | [`vktDGCComputeSmokeTestsExt.cpp#L285-L373`](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTestsExt.cpp#L285-L373) | Defines buffer and transfer paths. |
| DGC execution | [`vktDGCComputeSmokeTestsExt.cpp#L450-L494`](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTestsExt.cpp#L450-L494) | Defines null execution set, preprocessing, barriers, and execution. |
| Result check | [`vktDGCComputeSmokeTestsExt.cpp#L496-L579`](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTestsExt.cpp#L496-L579) | Defines expected ranges and failure logging. |
| Specification semantics | [`generatedcommands.adoc#L23-L29`](../../../../vulkan-docs/src/chapters/device_generated_commands/generatedcommands.adoc#L23-L29), [`generatedcommands.adoc#L326-L337`](../../../../vulkan-docs/src/chapters/device_generated_commands/generatedcommands.adoc#L326-L337) | Defines preprocess synchronization and unordered compute behavior. |

## Questions / Risk Points for User Audit

- Is the distinction between command-data generation (`from_host` versus `from_compute`) and DGC preprocessing clear?
- Is it clear that `indirectExecutionSet` is always `VK_NULL_HANDLE` and that the bound compute pipeline is fixed?
- Does the counter-range example make the aggregate result check understandable?

## Conversion Notes for Final Wiki Rewrite

- Keep the final page focused on the preparation-path behavior axis and use the parameter table for the remaining matrix dimensions.
- Retain the counter-range example in concise form, then explain the source-generated `comp` shader and host-side range reconstruction.
- Carry the failure-cause mapping table directly into `## Failure Meaning` on the final page.
- Keep execution-set absence explicit because it prevents readers from attributing the matrix to pipeline-selection behavior.
