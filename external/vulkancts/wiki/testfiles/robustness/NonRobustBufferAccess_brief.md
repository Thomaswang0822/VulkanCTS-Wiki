# Understanding Brief: `robustness.non_robust_buffer_access`

## One-Sentence Test Purpose

This test checks that out-of-bounds buffer references in an unexecuted compute-shader branch do not affect values produced by the valid executed branch.

## Background Knowledge

### Dynamic branches and non-robust accesses

A shader invocation executes only the selected side of an `if` statement. These cases place invalid buffer index expressions in the unselected side; they do not rely on any defined result for an executed out-of-bounds access.

Why it matters here:
- The selected accesses stay within their buffers.
- Any output corruption indicates that the unselected path affected execution.

## One Concrete Example

In `unexecuted_oob_underflow`, the alternate input and output indices begin at `-128`. Runtime values from `data_in2` select the other branch, which reads valid input elements and writes valid output positions. The final output must still equal the complete interleaved sequence ([`unexecuted_oob_underflow.amber`](../../../data/vulkan/amber/non_robust_buffer_access/unexecuted_oob_underflow.amber#L26-L35), [`unexecuted_oob_underflow.amber`](../../../data/vulkan/amber/non_robust_buffer_access/unexecuted_oob_underflow.amber#L45-L76)).

## End-to-End Test Flow

```text
[host] register one Amber case for the overflow leaf and one for the underflow leaf
[host] create two input buffers, a branch-control buffer, an output buffer, and expected data
[host] bind the buffers to a GLSL compute pipeline
[host] dispatch 4 × 1 × 1 workgroups with four local invocations each
[device] use runtime control values to select valid buffer reads and writes
[device] leave overflow or underflow references in the unexecuted branch
[host] compare the complete output buffer with the expected interleaved sequence
[host] pass only if every element matches
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The C++ factory maps each registered leaf to an Amber file of the same name. Each file contains a GLSL 4.30 compute shader and Amber pipeline commands ([`vktNonRobustBufferAccessTests.cpp`](../../../modules/vulkan/robustness/vktNonRobustBufferAccessTests.cpp#L39-L54)).

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `data_in0` | yes | yes | read | no | Supplies one 512-element valid input sequence. |
| `data_in1` | yes | yes | read | no | Supplies the other 512-element valid input sequence. |
| `data_in2` | yes | yes | read | no | Makes branch selection depend on runtime data. |
| `data_out` | yes | yes | written | yes | Holds the 1024-element result checked by Amber. |
| `expected` | yes | no | no | yes | Defines the required interleaved output. |

## What Is Checked

- Amber dispatches the compute pipeline and compares all of `data_out` with `expected` using `EQ_BUFFER`.
- The expected result is the increasing 1024-element series obtained by interleaving the initialized input arrays.
- No tolerance or partial match is used ([`unexecuted_oob_overflow.amber`](../../../data/vulkan/amber/non_robust_buffer_access/unexecuted_oob_overflow.amber#L79-L105)).

## Behavior Parameter Identification

> **Behavior parameter:** test case leaf
>
> **Candidate values:** `unexecuted_oob_overflow`, `unexecuted_oob_underflow`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `unexecuted_oob_overflow` | Upper-bound references from an unselected branch affected valid reads, writes, or control flow. |
| `unexecuted_oob_underflow` | Negative references from an unselected branch affected valid reads, writes, or control flow. |

## Important Variations and Special Cases

- `unexecuted_oob_overflow` uses high alternate-path indices; `unexecuted_oob_underflow` begins alternate-path indices at `-128`.
- Both cases use the same resource sizes, branch-control data, workgroup configuration, and full-buffer verdict.
- The registration loop is omitted for Vulkan SC builds under `CTS_USES_VULKANSC` ([`vktNonRobustBufferAccessTests.cpp`](../../../modules/vulkan/robustness/vktNonRobustBufferAccessTests.cpp#L48-L55)).

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Registration and Amber mapping | [`vktNonRobustBufferAccessTests.cpp`](../../../modules/vulkan/robustness/vktNonRobustBufferAccessTests.cpp#L39-L58) | Defines both leaves and their Amber files. |
| Overflow behavior | [`unexecuted_oob_overflow.amber`](../../../data/vulkan/amber/non_robust_buffer_access/unexecuted_oob_overflow.amber#L1-L105) | Shows the shader, resources, dispatch, and check for upper-bound references. |
| Underflow behavior | [`unexecuted_oob_underflow.amber`](../../../data/vulkan/amber/non_robust_buffer_access/unexecuted_oob_underflow.amber#L1-L105) | Shows the corresponding negative-index case. |
| Registered mustpass paths | [`robustness.txt`](../../../mustpass/main/vk-default/robustness.txt#L13753-L13754) | Confirms both executable leaves. |

## Questions / Risk Points for User Audit

- Is the distinction between an unexecuted invalid reference and an executed out-of-bounds access explicit enough?
- Does the shared branch mechanism need a deeper shader walkthrough, or is the concise explanation sufficient for this two-case family?

## Conversion Notes for Final Wiki Rewrite

- Use the test case leaf as the behavior parameter.
- Carry the failure-cause mapping table unchanged into the final page.
- Keep the final page focused on branch selection, resource flow, and full-buffer equality; move source navigation to the appendix.
