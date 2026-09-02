## Understanding Goal

Explain how the NV compute smoke test turns a generated stream of indirect dispatches into a result that the host can check. The audit must distinguish the five registered dimensions: sequence count, command-buffer memory placement, command generation, preprocessing, and queue selection.

## Background Knowledge

A `VkDispatchIndirectCommand` contains the workgroup counts for one compute dispatch. The NV indirect-command layout in this test has one dispatch token, so the sequence count is also the number of generated dispatches.

The compute shader uses one atomic counter for each flattened workgroup index. Its local size is 64 invocations. Every invocation adds one to the counter for its workgroup, so one dispatch contributes 64 to each counter in its covered range.

## Test Mechanism

The host creates a deterministic pseudo-random list of `VkDispatchIndirectCommand` records. Each record selects a total workgroup count from 1 through 256 and places that count in one of `x`, `y`, or `z`; the other two dimensions remain 1. The generated command stream executes the records through `vkCmdExecuteGeneratedCommandsNV`.

The command data follows one of three paths:

| Registered choice | Command data path |
|---|---|
| `*_host_visible_from_host_*` | The host-visible initial buffer is also the indirect-command buffer. |
| `*_device_local_from_host_*` | The host fills a host-visible transfer source, then the command buffer copies it to a device-local indirect-command buffer and inserts a transfer-to-indirect-read barrier. |
| `*_device_local_from_compute_*` or `*_host_visible_from_compute_*` | The host fills a host-visible storage buffer. A one-workgroup `gen` compute dispatch copies the records to a second storage buffer that also has indirect-buffer usage. A compute-to-indirect-read barrier makes those writes available. The second buffer is device-local or host-visible according to the memory-placement choice. |

The generated-command layout contains a dispatch token. The test creates a `PreprocessBuffer` for the selected sequence count. Explicit variants call `vkCmdPreprocessGeneratedCommandsNV`, add the preprocess-to-execute barrier, and pass `VK_TRUE` to execution. Implicit variants skip the preprocess command and pass `VK_FALSE`.

The host selects either the context queue or a compute queue. It uses the matching queue-family index when it creates the command pool. A missing compute queue makes a compute-queue case unsupported.

## Behavior Parameter Identification

The primary behavioral axis is the registered five-dimensional variant. Each value changes the command stream or the path used to prepare and execute it.

| Dimension | Values | Behavioral effect |
|---|---|---|
| Sequence count | `4`, `1024` | Sets the number of indirect dispatch records and the `sequencesCount` value passed to `VkGeneratedCommandsInfoNV`. The `1024` variants also set `VK_INDIRECT_COMMANDS_LAYOUT_USAGE_UNORDERED_SEQUENCES_BIT_NV`. |
| Memory placement | `device_local`, `host_visible` | Selects the memory requirement for the destination command buffer. The initial host upload remains host-visible in every case. |
| Command generation | `from_host`, `from_compute` | Selects direct host data or the `gen` compute shader copy into the destination command buffer. |
| Preprocessing | `implicit_preprocess`, `explicit_preprocess` | Selects whether the host records `vkCmdPreprocessGeneratedCommandsNV` before execution. |
| Queue | `compute_queue`, `universal_queue` | Selects the dedicated compute queue and family, or the context queue and family. |

The exact registered values are the 32 direct children shown in the final page's registration tree. The source registration loop covers both sequence counts, both memory choices, both command-generation choices, both preprocessing choices, and both queue choices.

## What Failure Means

The host waits for the submission, invalidates the host-visible result allocation, and compares the returned 256 counters with values reconstructed from the same indirect command records. For each counter range, the host counts how many dispatches cover that workgroup index and expects that count multiplied by 64. A mismatch means that the generated execution or one of the preparation, synchronization, queue, or readback paths did not preserve this result contract.

### Failure Cause Mapping

| Behavior parameter value | Possible failure cause |
|---|---|
| `4` or `1024` sequence count | The implementation may execute the wrong number of sequences, use the wrong `sequencesCount`, or mishandle the unordered-sequence layout flag used by the `1024` variants. |
| `device_local` or `host_visible` | The destination command buffer may have incompatible memory or usage behavior, or the host-visible result readback may expose stale data. |
| `from_host` or `from_compute` | A host upload, transfer copy, or `gen` shader write may not produce the command records consumed by indirect execution. |
| `implicit_preprocess` or `explicit_preprocess` | Preprocessing may be omitted, performed with the wrong state, or not synchronized with execution. |
| `compute_queue` or `universal_queue` | Queue-family selection or submission synchronization may lead to incorrect generated dispatch execution. |

## Source Mapping

| Topic | Source link | Why it matters |
|---|---|---|
| Parameter structure and constants | [`SmokeTestParams`](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTests.cpp#L53-L64) | Defines the five dimensions, the unordered flag, the 64-invocation local size, and the 256-counter limit. |
| Shader generation | [`SmokeTestCase::initPrograms`](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTests.cpp#L128-L182) | Generates `comp` and the optional `gen` shader. |
| Support checks | [`SmokeTestCase::checkSupport`](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTests.cpp#L184-L195) | Requires NV DGC compute support, the Vulkan memory model, and a compute queue for queue-specific cases. |
| Command and memory setup | [`SmokeTestInstance::iterate`](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTests.cpp#L197-L359) | Selects the queue, creates the command layout and buffers, generates the records, and selects memory placement. |
| Preprocess and execution | [`SmokeTestInstance::iterate`](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTests.cpp#L407-L464) | Records command generation, barriers, preprocessing, execution, host visibility, and queue submission. |
| Result reconstruction and comparison | [`result verification`](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTests.cpp#L469-L549) | Builds expected counter ranges and reports mismatches. |
| Exact registration | [`createDGCComputeSmokeTests`](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTests.cpp#L554-L580) | Registers the 32 variants in `dgc.nv.compute.smoke`. |

## Questions / Risk Points for User Audit

- Does the distinction between the host-visible initial buffer and the selected destination command buffer remain clear?
- Does the page explain that `from_compute` adds a `gen` dispatch before DGC execution rather than changing the test shader?
- Does the result rule make clear why one covered workgroup contributes 64 to a counter?
- Does the page preserve all 32 registered paths and the special unordered flag for the `1024` variants?

## Conversion Notes for Final Wiki Rewrite

Carry the five-dimension table into `## Parameter Dimensions and Observed Values`. Explain memory placement as a path table rather than as a list of buffer declarations. Keep the result-range reconstruction and the two barriers in runtime behavior. The final page should use the exact `### Failure Cause Mapping` table above and write fresh cause analysis for generated dispatches, command preparation, preprocessing, queue selection, and result visibility.
