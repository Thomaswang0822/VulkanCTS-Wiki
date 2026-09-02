## One-Sentence Test Purpose

This test checks whether `VK_EXT_device_generated_commands` can preprocess compute command sequences and execute them correctly when queue selection, sequence counts, and state command buffer placement vary.

## Background Knowledge

### Explicit preprocessing and execution

An indirect command layout describes tokens that turn buffer data into commands. With `VK_INDIRECT_COMMANDS_LAYOUT_USAGE_EXPLICIT_PREPROCESS_BIT_EXT`, `vkCmdPreprocessGeneratedCommandsEXT` prepares a preprocess buffer and `vkCmdExecuteGeneratedCommandsEXT` later consumes it with `isPreprocessed` set to `VK_TRUE`.

Why it matters here:
- A separate preprocessing step requires synchronization before execution.
- The test can put preprocessing and execution on the same queue family or transfer ownership between a universal queue and a compute queue.

### Sequence count and state command buffers

A sequence count buffer limits how many generated command sequences execute. A zero count leaves the corresponding output unchanged. The state command buffer supplies the descriptor and pipeline state used by preprocessing; the test also checks a state command buffer separate from the command buffer that records preprocessing.

## One Concrete Example

For `dEQP-VK.dgc.ext.compute.preprocess.parallel_preprocessing_compute_with_universal_exec_with_count_buffer`, the test prepares two generated command buffers. Each contains a push-constant value followed by `VkDispatchIndirectCommand` values `(1, 1, 1)`. The layout consumes the push constant and dispatches one compute workgroup. The first sequence is preprocessed on a compute queue and executed on a universal queue. The second sequence is preprocessed and executed on the compute queue. A count buffer contains one for each sequence.

The compute shader is reconstructed from `storePushConstantProgram`:

```glsl
#version 460
layout (local_size_x=1, local_size_y=1, local_size_z=1) in;
layout (set=0, binding=0, std430) buffer OutputBlock { uint value; } outputBuffer;
layout (push_constant, std430) uniform PushConstantBlock { uint value; } pc;
void main (void) { outputBuffer.value = pc.value; }
```

## End-to-End Test Flow

```text
[host] select a Method, CountBuffer, and StateCmdBuffer combination
[host] create two host-visible output buffers and initialize them to zero
[host] create descriptor sets, a compute pipeline, and a push-constant range
[host] create an explicit-preprocess indirect command layout with push-constant and dispatch tokens
[host] write two command streams containing one push constant and one (1, 1, 1) dispatch each
[host] allocate one preprocess buffer per sequence using queried EXT memory requirements
[host] write a count buffer for each sequence when the selected variant uses one
[host] record preprocessing for the first sequence and submit it, adding queue ownership barriers when queue families differ
[host] record execution of the first preprocessed sequence and preprocessing plus execution of the second sequence
[device] execute the compute shader, which copies the generated push constant to its output buffer
[host] wait for fences, invalidate the output allocations, and compare both values with the expected values
[host] report pass or fail
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `storePushConstantProgram` emits one compute GLSL source string. The shader copies its push-constant value to a storage buffer.
- The generated command layout contains a push-constant token at offset zero followed by a dispatch token. It uses `VK_INDIRECT_COMMANDS_LAYOUT_USAGE_EXPLICIT_PREPROCESS_BIT_EXT`.
- Each command stream contains four `uint32_t` values: the generated push constant and the three dispatch dimensions. The two streams use push constants `100` and `101`.
- The preprocess buffer size and alignment come from `vkGetGeneratedCommandsMemoryRequirementsEXT` through `PreprocessBufferExt`.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Two output buffers | yes | yes, as storage-buffer descriptors | compute shader writes one `uint32_t` per buffer | yes | They expose whether each generated dispatch executed with the expected push constant. |
| Two generated command buffers | yes | yes, through device addresses | preprocessing and execution read them | no | They contain the push-constant and dispatch token data. |
| Preprocess buffers | yes, when the queried size is nonzero | yes, through `VkGeneratedCommandsInfoEXT` | preprocessing writes them and execution reads them | no | They carry the result of explicit preprocessing. |
| Two sequence count buffers | only for count-buffer variants | yes, through `sequenceCountAddress` | generated-command processing reads them | no | They select one executed sequence or zero sequences. |
| Descriptor sets | yes | yes | the shader reads the bound output-buffer descriptor | no | Each generated execution writes to its own output buffer. |
| Push-constant range | yes | yes | the generated push-constant token supplies its value to the shader | no | It is the value checked through the output buffer. |

## What Is Checked

- The shader writes `i + 100` to output buffer `i` when the sequence count is nonzero.
- For `CountBuffer::YES_BUT_ZERO`, the expected value is zero because the generated dispatch does not execute.
- The host checks both output buffers after waiting for the preprocessing and execution fences. Any mismatch produces a failure with the buffer position, expected value, and observed value.

## Behavior Parameter Identification

> **Behavior parameter:** `Method` queue topology
>
> **Candidate values:** `universal`, `compute`, `compute_with_universal_exec`, `universal_with_compute_exec`

The method is the primary behavioral axis because it changes which queue performs preprocessing and which queue executes the generated commands. `CountBuffer` and `StateCmdBuffer` are secondary axes that modify sequence selection and command-buffer state placement across every method.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `universal` | Same universal queue path: generated command layout, preprocessing, synchronization, compute execution, or output validation. |
| `compute` | Same compute queue path: compute-queue command recording, preprocessing, synchronization, compute execution, or output validation. |
| `compute_with_universal_exec` | Cross-queue path with compute preprocessing and universal-queue execution: queue ownership transfer, cross-queue synchronization, generated command execution, or output validation. |
| `universal_with_compute_exec` | Cross-queue path with universal-queue preprocessing and compute execution: queue ownership transfer, cross-queue synchronization, generated command execution, or output validation. |

## Important Variations and Special Cases

- `CountBuffer::NO` omits sequence count buffers and uses a maximum and actual sequence count of one.
- `CountBuffer::YES` writes one to each count buffer but passes a fake maximum count of `100` when querying preprocessing memory requirements. The source comment ties this to `VUID-VkGeneratedCommandsInfoNV-sequencesCount-02917`.
- `CountBuffer::YES_BUT_ZERO` writes zero to each count buffer. The test still constructs and preprocesses the command information, but expects both output buffers to remain zero.
- `StateCmdBuffer::OTHER` records the descriptor and pipeline state in another command buffer before calling preprocessing. `StateCmdBuffer::SAME` records that state in the current command buffer.
- The four methods are `UNIVERSAL_QUEUE`, `COMPUTE_QUEUE`, `PREPROCESS_COMPUTE_EXECUTE_UNIVERSAL`, and `PREPROCESS_UNIVERSAL_EXECUTE_COMPUTE`. The latter two require a compute queue and exercise queue-family ownership barriers.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Parameter enums and support gate | [Method, StateCmdBuffer, CountBuffer, and checkDGCComputeAndQueueSupport](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTestsExt.cpp#L51-L95) | Defines the three dimensions and compute-queue requirement. |
| Compute shader generator | [storePushConstantProgram](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTestsExt.cpp#L97-L107) | Defines the shader and its push-constant to output-buffer behavior. |
| Test setup and generated command layout | [parallelPreprocessRun setup](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTestsExt.cpp#L125-L301) | Creates resources, pipeline, command streams, preprocess buffers, and command information. |
| Queue selection and ownership | [parallelPreprocessRun queue setup](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTestsExt.cpp#L304-L344) | Maps methods to preprocessing and execution queues. |
| Separate preprocessing and execution | [parallelPreprocessRun submissions](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTestsExt.cpp#L349-L494) | Shows fences, state command buffers, barriers, and submissions. |
| Result checking | [parallelPreprocessRun verification](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTestsExt.cpp#L496-L521) | Defines expected values and the failure result. |
| Registration matrix | [createDGCComputePreprocessTestsExt](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTestsExt.cpp#L526-L575) | Forms all 4 × 3 × 2 registered test cases. |
| EXT preprocessing semantics | [Vulkan device-generated commands specification](../../../../vulkan-docs/src/chapters/device_generated_commands/generatedcommands.adoc#L1827-L1918) | Defines preprocess-buffer requirements and EXT pipeline information. |
| Explicit preprocess and synchronization | [Vulkan layout usage and processing rules](../../../../vulkan-docs/src/chapters/device_generated_commands/generatedcommands.adoc#L326-L337) | Defines explicit preprocessing and the separate preprocessing pipeline. |

## Questions / Risk Points for User Audit

- Is `Method` the right primary behavioral axis, with `CountBuffer` and `StateCmdBuffer` treated as secondary axes?
- Should the failure mapping distinguish common failures from the two cross-queue ownership paths more explicitly?
- Is the reconstructed shader sufficient to explain the validation signal without a full shader walkthrough?
- Does the distinction between the state command buffer and the command buffer that records preprocessing remain clear?

## Conversion Notes for Final Wiki Rewrite

- Keep `Method` as the primary axis and present `CountBuffer` and `StateCmdBuffer` as secondary dimensions.
- Distill the explicit-preprocess mental model into a short Background Knowledge list; keep the concrete sequence in runtime execution.
- Use the concrete compute shader as one representative shader walkthrough. Generate its SPIR-V from the reconstructed GLSL with the CTS default SPIR-V target.
- Copy the `### Failure Cause Mapping` table directly into the final page. Write fresh Cause Analysis subsections for the four method values and the shared count/state mechanisms.
- Keep source links in a focused appendix and retain exact registration identifiers in the hierarchy and parameter tables.
