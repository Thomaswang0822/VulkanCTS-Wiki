## Overview

**Core question:** Do the NV compute get-info queries return stable pipeline addresses and consistent generated-command memory requirements for equivalent inputs? The tests query Vulkan state and compare the returned values. They do not execute generated commands.

## Background Knowledge

`vkGetGeneratedCommandsMemoryRequirementsNV` reports the memory `size`, `alignment`, and `memoryTypeBits` required for a generated-command layout and sequence count. A generated-command layout describes the tokens in the indirect command stream. Pipeline device addresses identify pipeline state, while capture/replay addresses must remain stable when the feature is enabled.

## Registration Hierarchy

```text
dgc.nv.compute.get_info
├── constant_cmd_memory_requirements_basic_case
├── constant_cmd_memory_requirements_basic_case_with_pipeline
├── constant_cmd_memory_requirements_ignore_unordered_flag
├── constant_cmd_memory_requirements_increase_count
├── constant_cmd_memory_requirements_max_sequence_count
├── constant_pipeline_capture_replay_address
├── constant_pipeline_device_address
└── constant_pipeline_memory_requirements
```

The root and its eight direct children are registered by [createDGCComputeGetInfoTests](../../../modules/vulkan/device_generated_commands/vktDGCComputeGetInfoTests.cpp#L382-L415). The corresponding NV paths are listed in [dgc.txt](../../../mustpass/main/vk-default/dgc.txt).

## Parameter Dimensions and Observed Values

The source registers individual cases rather than a cross-product. Their observed dimensions are:

| Dimension | Values | Effect |
|---|---|---|
| Query family | `constant_pipeline_memory_requirements`, `constant_pipeline_device_address`, `constant_pipeline_capture_replay_address` | Selects the pipeline query and comparison. |
| Command-memory case | `basic_case`, `basic_case_with_pipeline`, `increase_count`, `max_sequence_count`, `ignore_unordered_flag` | Selects the layout and the second-query variation. |
| Sequence count | `1024u`, `maxIndirectSequenceCount`, or twice the initial count | Tests a fixed bound, the device limit, or nondecreasing size after increasing the bound. |
| Layout variation | Dispatch, pipeline plus dispatch, push constant plus dispatch, or an unordered layout | Changes the tokens and usage flags passed to the memory-requirements query; the basic dispatch layout also uses the explicit-preprocess usage flag. |

## Behavior Parameters

### Constant pipeline memory requirements

`constant_pipeline_memory_requirements` calls `vkGetPipelineIndirectMemoryRequirementsNV` three times for the same compute-pipeline create information: once without the chained buffer-info structure, once with a `VkComputePipelineIndirectBufferInfoNV` chain that the specification says to ignore, and once without the chain again. The returned `size`, `alignment`, and `memoryTypeBits` must match, and the ignored structure must not be modified.

### Constant pipeline device address

`constant_pipeline_device_address` obtains the compute pipeline's indirect device address through `vkGetPipelineIndirectDeviceAddressNV` and compares it with the address saved when the DGC pipeline helper created that pipeline. The two addresses must match.

### Constant pipeline capture/replay address

`constant_pipeline_capture_replay_address` creates one capture pipeline, saves the indirect device address returned for it, then creates a second pipeline with that capture address supplied and compares the recreated pipeline's address with the saved one.

### Command memory requirements

The five command-memory cases call `vkGetGeneratedCommandsMemoryRequirementsNV` twice. The basic case uses a dispatch token. The pipeline variant adds a pipeline token. The increase-count case doubles `maxSequencesCount`; its required size may grow or stay equal, but must not shrink. The maximum-count case uses `maxIndirectSequenceCount`. The unordered-flag case changes only the layout's unordered-sequences usage flag. Except for the permitted size increase, `size`, `alignment`, and `memoryTypeBits` must remain equal.

## Shader Analysis

`initBasicProgram` and `initBasicProgramCmd` provide the compute shader used when a selected case creates a compute pipeline; the shader's descriptor interface also matches the pipeline layout built for those cases. The shader declares a storage buffer at set `0`, binding `0`, and uses a `64 x 1 x 1` local size. The command-memory increase case also provides a one-word push-constant range. The shader is fixed pipeline plumbing: these tests do not dispatch it or inspect its buffer output, so its arithmetic is outside the tested behavior. This page has no representative shader walkthrough because the shader does not participate in the checked behavior.

## Runtime Execution and Result Checking

- The factory assigns `checkDGCComputeSupport` to ordinary pipeline cases and `checkDGCComputeCaptureReplaySupport` to the capture/replay case. Command-memory cases select basic or pipeline support according to whether they use a pipeline token. Unsupported requirements skip the case through these callbacks.
- For command-memory cases, the test creates a compute pipeline and pipeline layout only when the selected layout needs an actual pipeline handle; `basic_case_with_pipeline` instead tests a layout containing a pipeline token without constructing a compute pipeline. The pipeline-query cases create the pipeline layout and, where needed, a compute pipeline or compute-pipeline create information for their queries. Each case performs the relevant NV property or address query and compares the result with the expected second observation: the same pipeline create-information query, the same pipeline's saved indirect address, the recreated pipeline's capture/replay address, or a second generated-command memory-requirements query. The pipeline-memory case also checks that its ignored `VkComputePipelineIndirectBufferInfoNV` input remains unchanged.
- A mismatch returns `tcu::TestStatus::fail` and logs the compared memory-requirements records where applicable. A successful comparison returns `pass("Pass")`.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `constant_pipeline_memory_requirements` | The implementation returns different pipeline memory requirements for identical inputs. |
| `constant_pipeline_device_address` | The implementation returns an unstable compute pipeline device address. |
| `constant_pipeline_capture_replay_address` | The implementation returns an unstable capture/replay address for the same pipeline. |
| `constant_cmd_memory_requirements_basic_case` | The memory-requirements query is unstable for a basic dispatch layout. |
| `constant_cmd_memory_requirements_basic_case_with_pipeline` | The query handles the pipeline token or its pipeline state inconsistently. |
| `constant_cmd_memory_requirements_increase_count` | The required size decreases after `maxSequencesCount` increases, or alignment or memory type bits change. |
| `constant_cmd_memory_requirements_max_sequence_count` | The query is inconsistent at the device-reported maximum sequence count. |
| `constant_cmd_memory_requirements_ignore_unordered_flag` | The otherwise matching layout produces different requirements when the unordered-sequences flag is added. |

### Cause Analysis

#### Pipeline address stability

**Possible failure symptoms:** A repeated pipeline-address query returns different addresses for the same pipeline.

**Possible implementation causes:** The implementation may not preserve the address associated with the same pipeline. The failure does not identify the responsible layer, so source-level investigation is needed.

#### Memory-requirements stability

**Possible failure symptoms:** A repeated or varied memory-requirements query changes `size`, `alignment`, or `memoryTypeBits` unexpectedly.

**Possible implementation causes:** The implementation may handle layout tokens, sequence counts, or usage flags inconsistently. The failure does not identify the responsible layer, so source-level investigation is needed.

## Case Pruning

### Requirement-based pruning

Support callbacks gate compute DGC support, pipeline support, and capture/replay support before the test body runs. The maximum-count case reads `maxIndirectSequenceCount`; the other count cases use the source's fixed values and have no additional source-level pruning.

### Design-based pruning

The registration table contains only the eight listed leaves. The source does not generate a cross-product of layouts, pipeline forms, flags, and sequence counts. The shared shader is compiled only to construct the required compute pipeline and contributes no independent test dimension.

## Key Takeaways

- The family tests NV get-info queries and pipeline address stability; it does not execute generated command streams.
- The command-memory increase case requires nondecreasing size, while the other repeated queries require equal `size`, `alignment`, and `memoryTypeBits`.
- Support checks skip unsupported devices rather than treating missing optional features as failures.
- Shader code is fixed plumbing for pipeline construction, not a tested output path.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Test registration | [createDGCComputeGetInfoTests](../../../modules/vulkan/device_generated_commands/vktDGCComputeGetInfoTests.cpp#L382-L415) | Registers `dgc.nv.compute.get_info` and all eight direct children. |
| Compute get-info implementation | [vktDGCComputeGetInfoTests.cpp](../../../modules/vulkan/device_generated_commands/vktDGCComputeGetInfoTests.cpp#L48-L377) | Defines shader setup, support checks, queries, and comparisons. |
| Header declaration | [vktDGCComputeGetInfoTests.hpp](../../../modules/vulkan/device_generated_commands/vktDGCComputeGetInfoTests.hpp#L29-L34) | Declares the test-group factory. |
| Mustpass coverage | [dgc.txt](../../../mustpass/main/vk-default/dgc.txt) | Lists the NV compute get-info paths. |
