# Understanding Brief: robustness buffer access

## One-Sentence Test Purpose

This test checks whether robust buffer access keeps out-of-bounds uniform, storage, and texel-buffer operations within the outcomes accepted by the CTS verifier across compute, vertex, and fragment shaders.

## Background Knowledge

### Descriptor range and backing allocation

A buffer descriptor or buffer view exposes a range of a memory-backed resource. An access can cross the declared range while remaining inside the backing allocation, or it can cross the allocation itself. The test covers both boundaries because they exercise different parts of robust access handling.

Why it matters here:
- Regular range cases make the exposed range smaller than the shader's access footprint.
- `out_of_alloc` cases place the access near the end of the input or output allocation.

### Allowed robust-access results

Robustness does not require every out-of-bounds read to return one fixed bit pattern. The CTS verifier accepts the bounded result set encoded by the implementation: zero, values traceable to the input buffer, and a restricted vector pattern for applicable out-of-bounds vector reads. Out-of-bounds writes must not introduce unrelated values outside the permitted memory range.

Why it matters here:
- A zero result can be valid and must not cause a false failure.
- A value outside the verifier's accepted set indicates that the access escaped the intended robustness guarantees.

## One Concrete Example

Consider `robustness.buffer_access.compute.scalar_copy.r32_uint.range_1_byte.oob_uniform_read`. The host fills the input with deterministic values, exposes a one-byte range, and dispatches one compute invocation. The generated shader reads scalar elements through a uniform-buffer declaration and writes the observations to an output storage buffer. The host then checks each output slot against the allowed in-bounds or out-of-bounds result set. This example is representative; the generator also emits vector, matrix, member-copy, and texel-buffer forms.

## End-to-End Test Flow

```text
[host] choose root mode, shader stage, access shape, format, range, and operation
[host] check required features and format capabilities
[host] create a robust-access device or enable the extension-specific mode
[host] fill input memory with deterministic values and output memory with 0xFF
[host] create buffer descriptors, texel-buffer views, or descriptor-heap resources
[host] generate and compile the selected GLSL stage
[host] record one compute dispatch or graphics draw, submit it, and wait
[device] execute in-bounds and out-of-bounds reads or writes
[device] store observable results in the output buffer
[host] invalidate mapped output memory and inspect every four-byte slot
[host] pass only if every slot matches the operation-specific accepted set
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The source builds GLSL for compute, vertex, or fragment execution. Non-texel variants generate uniform or storage blocks and copy a matrix, vector, vector member, or scalar. `texel_copy` uses `texelFetch` or `imageLoad`, and storage writes use `imageStore`. The selected format controls the scalar type and optional 64-bit extension declaration. The root mode changes feature and descriptor setup without replacing the core access expressions.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Input buffer or texel-buffer view | yes | yes | read | no | Supplies deterministic values and the range or allocation boundary crossed by read cases. |
| Output buffer or texel-buffer view | yes | yes | written | yes | Records read observations or exposes the effect of storage writes. |
| Descriptor set or descriptor heap | yes | yes | read by descriptor access | no | Selects conventional descriptor binding or `VK_EXT_descriptor_heap` coverage. |
| Vertex buffer | graphics cases only | yes | read | no | Supplies the small draw used to execute vertex or fragment cases. |
| Host-visible allocation mappings | yes | through bound resources | no direct shader access | yes | Let the host initialize inputs and inspect final output bytes. |

## What Is Checked

- In-bounds reads must reproduce the deterministic input value for the selected format.
- Out-of-bounds reads must match an accepted zero, input-derived, partial-access, or applicable vector result.
- Out-of-bounds writes must leave protected bytes unchanged or write only an accepted input-derived or zero value where the verifier permits a write.
- Bytes beyond the shader's intended output footprint must retain their initialized value unless the operation-specific rules permit a bounded result.
- The case returns `pass("All values OK")` only when every checked slot is valid; otherwise it returns `fail("Invalid value(s) found")`.

## Behavior Parameter Identification

> **Behavior parameter:** access operation subgroup
>
> **Candidate values:** `oob_uniform_read`, `oob_storage_read`, `oob_storage_write`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `oob_uniform_read` | Uniform-buffer or uniform-texel-buffer robust-read handling produced a value outside the accepted set, or corrupted an unrelated output slot. |
| `oob_storage_read` | Storage-buffer or storage-texel-buffer robust-read handling produced a value outside the accepted set, including an invalid partial or vector result. |
| `oob_storage_write` | A storage-buffer or storage-texel-buffer out-of-bounds write changed protected bytes or stored a value outside the verifier's permitted set. |

All values also depend on correct stage execution, descriptor or descriptor-heap setup, format handling, synchronization, and host readback.

## Important Variations and Special Cases

- `buffer_access` uses robust buffer access; `pipeline_robustness_buffer_access` enables `VK_EXT_pipeline_robustness`; `descriptor_heap_buffer_access` uses `VK_EXT_descriptor_heap` with buffer device addresses.
- `vertex`, `fragment`, and `compute` execute equivalent access patterns through different pipeline stages.
- `mat4_copy`, `vec4_copy`, `vec4_member_copy`, `scalar_copy`, and `texel_copy` vary access granularity and resource form.
- Byte ranges `range_1_byte`, `range_3_bytes`, `range_4_bytes`, and `range_32_bytes` expose full and partial accesses. Texel cases use `range_1_texel` and `range_3_texels`.
- `out_of_alloc` moves the access beyond backing memory rather than only beyond a descriptor range.
- Pipeline-robustness generation retains selected formats and omits `oob_storage_read` to avoid redundant coverage.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Shader generation | [GLSL builders](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L318-L699) | Defines non-texel and texel access expressions for all three stages. |
| Device and feature setup | [instance creation](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L721-L905) | Selects regular, pipeline-robustness, or descriptor-heap execution. |
| Resource setup | [test environments](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L918-L1536) | Creates ranges, allocations, bindings, descriptor heaps, draws, and dispatches. |
| Result validation | [`BufferAccessInstance::verifyResult()`](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L1634-L1851) | Defines the accepted values and final pass/fail decision. |
| Matrix registration | [`addBufferAccessTests()`](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L1930-L2095) | Generates stages, access shapes, formats, ranges, and operations. |
| Shared verification helpers | [robustness utilities](../../../modules/vulkan/robustness/vktRobustnessUtil.cpp#L166-L305) | Checks zero, input-derived values, vector patterns, and input initialization. |
| Registered mustpass examples | [`robustness.txt`](../../../mustpass/main/vk-default/robustness.txt#L42-L449) | Confirms regular `buffer_access` path components and generated leaves. |

## Questions / Risk Points for User Audit

- The page treats the access operation subgroup as the primary behavioral axis. The root mode, stage, access shape, format, and range remain matrix dimensions.
- A source-generated representative shader walkthrough and disassembly were not reconstructed during this recovery. The final page records this as unresolved rather than presenting a hand-written artifact as generated evidence.
- `through_pointers` appears in the registered `buffer_access` hierarchy but remains outside this implementation file's behavioral scope.

## Conversion Notes for Final Wiki Rewrite

- Keep the descriptor-range versus allocation-boundary distinction in Background Knowledge.
- Use one representative compute `scalar_copy` uniform-read case for a future shader-analyzer walkthrough, then cover stage, shape, format, and operation differences in a variation summary.
- Copy the Failure Cause Mapping table unchanged into the final page.
- Keep source navigation in the final appendix and retain the host verification rules in the runtime section.
