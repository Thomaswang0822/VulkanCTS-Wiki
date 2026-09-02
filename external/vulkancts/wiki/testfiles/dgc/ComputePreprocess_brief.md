# Understanding Brief: dgc.nv.compute.preprocess

## One-Sentence Test Purpose

This test checks whether parallel preprocessing produces executable device-generated compute commands with the selected count-buffer, queue, and zero-count behavior.

## Background Knowledge

### Preprocessing and indirect command execution

Device-generated commands separate command generation from command execution. A preprocess operation prepares generated commands in a preprocess buffer; a later execution operation consumes that prepared state. The execution count can come from the recorded sequence count or from a count buffer, so zero is a meaningful execution case.

Why it matters here:
- The test compares preprocessing and execution when they use different queues.
- The count-buffer variants check that the execution count controls how many generated commands run.
- A zero count should produce no generated work while still completing the legal command flow.

### Queue submissions and buffer visibility

A queue submission orders commands on one queue. When a preprocess buffer or result buffer crosses queue boundaries, the test must establish the required synchronization and ownership state before the next queue reads it. The Vulkan device-generated-commands rules define the command-buffer and preprocessing constraints; the implementation and helper code show how this test exercises them.

## One Concrete Example

A representative case records a generated compute sequence, preprocesses it, submits the preprocess work, then executes the prepared sequence and reads a result buffer. The count-buffer form supplies the sequence count from a buffer. The zero-count form supplies zero, so the test checks the resulting buffer without expecting generated compute work to update it.

## End-to-End Test Flow

```text
[host] select a preprocess method, count-buffer mode, queue arrangement, and zero-count mode
[host] create generated-command, preprocess, count, and result buffers
[host] record the generated compute sequence and its preprocess operation
[host] submit preprocessing and establish any required queue synchronization
[host] submit execution, using the selected count source
[device] preprocess and execute the generated commands
[device] write the result buffer for commands that execute
[host] wait, read the result buffer, and compare it with the expected values
[host] decide pass/fail from the result comparison
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The implementation builds the generated compute command sequence and selects the preprocess and execution configuration from the registered test case. The source does not make a separate shader artifact the behavioral axis; the observable result comes from execution of the generated compute commands.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Generated-command/preprocess storage | yes | yes | yes | no | Carries the generated sequence and prepared state. |
| Count buffer | yes, in count-buffer cases | yes | read | no | Supplies the execution count, including zero. |
| Result buffer | yes | yes | written | yes | Provides the pass/fail observation. |

## What Is Checked

The host reads the result buffer after execution and compares its values with the reference. Count-buffer cases use the count stored in the count buffer; zero-count cases must not require generated commands to produce nonzero result updates. Queue variants must preserve the same observable result after the required synchronization.

## Behavior Parameter Identification

> **Behavior parameter:** registered test family
>
> **Candidate values:** `parallel_preprocessing_compute`, `parallel_preprocessing_compute_with_count_buffer`, `parallel_preprocessing_compute_with_count_buffer_zero_count`, `parallel_preprocessing_compute_with_universal_exec`, `parallel_preprocessing_compute_with_universal_exec_with_count_buffer`, `parallel_preprocessing_compute_with_universal_exec_with_count_buffer_zero_count`, `parallel_preprocessing_universal`, `parallel_preprocessing_universal_with_compute_exec`, `parallel_preprocessing_universal_with_compute_exec_with_count_buffer`, `parallel_preprocessing_universal_with_compute_exec_with_count_buffer_zero_count`, `parallel_preprocessing_universal_with_count_buffer`, `parallel_preprocessing_universal_with_count_buffer_zero_count`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `parallel_preprocessing_compute` | Preprocessing or compute-queue execution does not produce the expected result. |
| `parallel_preprocessing_compute_with_count_buffer` | Count-buffer execution or preprocessing fails for a nonzero count. |
| `parallel_preprocessing_compute_with_count_buffer_zero_count` | Zero count does not suppress generated execution or leaves an unexpected result. |
| `parallel_preprocessing_compute_with_universal_exec` | Compute preprocessing followed by universal-queue execution does not preserve the expected result. |
| `parallel_preprocessing_compute_with_universal_exec_with_count_buffer` | Count-buffer execution across the selected queue path fails for a nonzero count. |
| `parallel_preprocessing_compute_with_universal_exec_with_count_buffer_zero_count` | Zero-count execution across the selected queue path behaves incorrectly. |
| `parallel_preprocessing_universal` | Universal-queue preprocessing or execution does not produce the expected result. |
| `parallel_preprocessing_universal_with_compute_exec` | Universal preprocessing followed by compute-queue execution does not preserve the expected result. |
| `parallel_preprocessing_universal_with_compute_exec_with_count_buffer` | Count-buffer execution after universal preprocessing fails for a nonzero count. |
| `parallel_preprocessing_universal_with_compute_exec_with_count_buffer_zero_count` | Zero-count execution after universal preprocessing behaves incorrectly. |
| `parallel_preprocessing_universal_with_count_buffer` | Universal-queue count-buffer execution fails for a nonzero count. |
| `parallel_preprocessing_universal_with_count_buffer_zero_count` | Universal-queue zero-count execution behaves incorrectly. |

## Important Variations and Special Cases

- `compute` and `universal` identify the queue used for preprocessing; the `with_compute_exec` and `with_universal_exec` forms identify the execution queue.
- `with_count_buffer` changes the execution-count source. The zero-count suffix tests the boundary value rather than a positive generated sequence.
- The implementation keeps the registered combinations explicit; this page does not treat unregistered cross-products as test cases.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Registration and case construction | [vktDGCComputePreprocessTests registration](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTests.cpp#L502-L560) | Defines the registered families and their parameter combinations. |
| Execution and result verification | [vktDGCComputePreprocessTests verification](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTests.cpp#L430-L491) | Shows command execution and host-side result checking. |
| DGC helper behavior | [device-generated-commands helpers](../../../modules/vulkan/device_generated_commands/) | Provides the helper implementation used by the test. |
| DGC specification | [Device-Generated Commands](../../../../vulkan-docs/src/chapters/device_generated_commands/generatedcommands.adoc) | Defines preprocessing and generated-command execution semantics. |

## Questions / Risk Points for User Audit

- Does the registered-family axis give the clearest comparison of queue, count-buffer, and zero-count behavior?
- Does the queue description distinguish preprocessing queue from execution queue for every registered name?
- Does the zero-count explanation match the source's exact result initialization and verification rule?
- Is a shader walkthrough required after confirming whether this implementation generates shader code as part of the tested behavior?

## Conversion Notes for Final Wiki Rewrite

- Keep the twelve registered direct children in one parseable hierarchy tree.
- Distill preprocessing, count-buffer, queue, and zero-count concepts into `Background Knowledge`, `Behavior Parameters`, and runtime sections.
- Copy the failure mapping table into the final page, then write fresh cause analysis.
- Add a shader walkthrough only if source inspection shows shader code is part of the tested behavior; if required, generate it through `shader-analyzer` and its `shader-disassembler` SPIR-V workflow.
