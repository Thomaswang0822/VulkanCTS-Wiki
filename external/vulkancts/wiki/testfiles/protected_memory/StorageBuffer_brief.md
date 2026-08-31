# Understanding Brief: StorageBuffer

## One-Sentence Test Purpose

This test checks whether protected storage buffers can be read, written, and updated atomically from fragment and compute shader stages under the selected protected-memory and pipeline-protection configuration.

## Background Knowledge

### Protected resources and protected queue operations

Vulkan separates protected device memory from unprotected device memory. Protected memory may be visible to device operations but must not be visible to the host. A protected buffer must use protected memory, and a protected command buffer must run on a protected-capable queue. The protected-memory rules permit protected-buffer access in framebuffer-space pipeline stages, the compute shader stage, and transfer operations. They also prohibit writing unprotected memory from protected queue operations when `protectedNoFault` is false ([protected memory](../../../../vulkan-docs/src/chapters/memory.adoc#L5566-L5654)).

Why it matters here:
- The SSBO result buffer is protected when the pipeline configuration selects protected execution, so the host validates it through the protected-memory framework rather than by directly mapping it.
- The input uniform buffer is unprotected and is copied into a protected buffer before shader execution for read and atomic cases. The copy and shader barriers keep the transfer-to-shader dependency explicit.
- `VK_PIPELINE_CREATE_PROTECTED_ACCESS_ONLY_BIT_EXT` and `VK_PIPELINE_CREATE_NO_PROTECTED_ACCESS_BIT_EXT` constrain where the pipeline may be recorded. The source only creates the flag combinations that match the selected pipeline-protection group.

### Shader storage buffers and atomic read-modify-write

A GLSL shader storage block exposes buffer memory to shader invocations. In this test, ordinary read and write shaders use a `uvec4` block member, while atomic shaders use four `uint` elements and apply one atomic operation to the element selected by the invocation ID. An atomic operation updates its target as one read-modify-write operation; the host computes the expected post-operation vector before execution.

Why it matters here:
- Read cases copy the input into a source SSBO and copy that value into the result SSBO in the shader.
- Write cases bind a uniform `uvec4` input and store it into the result SSBO.
- Atomic cases use one invocation per vector component in compute mode, so each invocation updates a distinct array element. The operation itself, rather than a race between invocations, is the property under test.

## One Concrete Example

Consider `dEQP-VK.protected_memory.ssbo.ssbo_read.default.none.compute.static.read_1`. The selected input is `uvec4(0, 0, 0, 0)`. The generated compute shader has a storage block at binding 0 for the result and a second storage block at binding 2 for the source:

```glsl
// Conceptual reconstruction of the generated compute shader.
layout(local_size_x = 1, local_size_y = 1, local_size_z = 1) in;
layout(set=0, binding=0, std140) buffer ProtectedTestBuffer {
    highp uvec4 protectedTestResultBuffer;
};
layout(set=0, binding=2, std140) buffer ProtectedTestBufferSource {
    highp uvec4 protectedTestBufferSource;
};
void main (void)
{
    protectedTestResultBuffer = protectedTestBufferSource;
}
```

The host first copies the input uniform buffer into the source SSBO. One compute invocation then copies the source member into the result member. The validator expects the result to equal the selected `uvec4`.

## End-to-End Test Flow

```text
[host] choose `SSBO_READ`, `SSBO_WRITE`, or `SSBO_ATOMIC`, a fragment or compute stage, static or random input, and protection parameters
[host] check protected-context support and request VK_EXT_pipeline_protected_access when the protected_access group is selected
[host] create the unprotected host-visible uniform buffer and protected or unprotected storage buffers according to the pipeline flags
[host] generate the stage-specific GLSL program and create descriptors at bindings 0, 1, and 2 as required by the selected test type
[host] record a transfer barrier and copy for read or atomic input initialization
[host] bind the pipeline and descriptor set, then draw four vertices or dispatch one workgroup, or four workgroups for an atomic compute case
[device] execute the shader and read, write, or atomically update the result storage buffer
[host] wait for the queue submission fence
[host] validate the result buffer against the `ValidationDataStorage<tcu::UVec4>` reference data
[host] return pass when `validateBuffer()` succeeds, otherwise return fail
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- For fragment cases, the test generates a fixed vertex shader that outputs `gl_VertexIndex` through `vIndex`, plus a fragment shader specialized for the selected SSBO operation.
- For compute cases, the test generates one `TestShader` with `local_size_x = local_size_y = local_size_z = 1`. The read and write templates use `uvec4`; the atomic template uses `uint protectedTestResultBuffer[4]` and substitutes the selected atomic call.
- `static` leaves use six `uvec4` inputs for read and write, while `random` leaves generate ten vectors from the command-line base seed. Atomic static leaves use four input vectors and atomic arguments; atomic random leaves generate ten input/argument pairs per operation.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `testUniform` | yes, host-visible and unprotected | yes, binding 1 for write/atomic setup and transfer source | read by transfer operations, not by the shader in the read path | no direct validation | Carries `m_testInput` into protected storage when needed. |
| `testBuffer` | yes, protected when `m_protectionMode` is enabled | yes, binding 0 | written by read/write/atomic shaders | yes, through `BufferValidator` | Stores the value whose protected access is tested. |
| `testBufferSource` | yes, with the selected protection mode | yes, binding 2 for read and atomic setup | read by read shaders; used as the copy destination for input initialization | no | Separates read-source storage from the result storage. |
| `colorImage` | yes, only for fragment execution | yes, as a color attachment | written by the fragment pipeline's fixed output | no | Supplies the graphics render target; the SSBO result remains the validation signal. |
| `ValidationDataStorage<tcu::UVec4>` | yes, host-side reference | no | no | compared by the host validator | Contains the expected result for the selected input and atomic operation. |

## What Is Checked

- Read and write cases compare the result SSBO with the selected `uvec4` input.
- Atomic cases compute an expected vector for `add`, `min`, `max`, `and`, `or`, `xor`, `exchange`, or `compswap`; component selection for compare-swap uses `swapNdx % 4`.
- The source returns `pass` only when `m_validator.validateBuffer()` succeeds. The shader's fragment color and the framework's fence indicate completion, but they are not the SSBO correctness oracle.

## Behavior Parameter Identification

> **Behavior parameter:** SSBO operation family
>
> **Candidate values:** `ssbo_read`, `ssbo_write`, `ssbo_atomic`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `ssbo_read` | Protected-buffer read visibility, source-to-result storage-buffer access, transfer-to-shader synchronization, or host reference setup does not produce the expected vector. |
| `ssbo_write` | Protected-buffer write access, uniform-to-storage-buffer data flow, shader-stage pipeline access, or host reference setup does not produce the expected vector. |
| `ssbo_atomic` | Atomic operation semantics, selected component/indexing, protected storage access, initialization synchronization, or host atomic reference calculation does not produce the expected vector. |

## Important Variations and Special Cases

- Fragment cases add a four-vertex point-list draw and a protected color image. Compute cases use one invocation per workgroup; atomic compute cases dispatch four workgroups so the four array elements are updated.
- `default` uses no `VK_EXT_pipeline_protected_access` request. `protected_access` requests that extension and is excluded from Vulkan SC builds.
- With `default`, nonzero pipeline protected-access flags are skipped. With `protected_access`, `none`, `protected_access_only`, and `no_protected_access` are generated on non-Vulkan-SC builds.
- The `no_protected_access` flag selects an unprotected `m_protectionMode`; the other flag values select protected mode. The test still retains the same SSBO operation and validation model.
- The eight atomic operations are `add`, `min`, `max`, `and`, `or`, `xor`, `exchange`, and `compswap`. Static and random cases vary inputs without changing the shader structure except for the substituted atomic call and argument values.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Operation and atomic-type enums | [`SSBOTestType` and `SSBOAtomicType`](../../../modules/vulkan/protected_memory/vktProtectedMemStorageBufferTests.cpp#L63-L80) | Defines the three operation families and eight atomic operations. |
| Shader generation | [`StorageBufferTestCase::initPrograms`](../../../modules/vulkan/protected_memory/vktProtectedMemStorageBufferTests.cpp#L271-L386) | Emits the fragment/compute declarations and operation bodies. |
| Protected support gate | [`checkSupport`](../../../modules/vulkan/protected_memory/vktProtectedMemStorageBufferTests.cpp#L230-L235) | Requests protected-context and optional pipeline-protected-access support. |
| Fragment execution | [`executeFragmentTest`](../../../modules/vulkan/protected_memory/vktProtectedMemStorageBufferTests.cpp#L389-L565) | Shows protected resources, barriers, draw submission, and validation. |
| Compute execution | [`executeComputeTest`](../../../modules/vulkan/protected_memory/vktProtectedMemStorageBufferTests.cpp#L568-L676) | Shows descriptor bindings, dispatch counts, submission, and validation. |
| Read/write registration | [`createReadStorageBufferTests` and `createWriteStorageBufferTests`](../../../modules/vulkan/protected_memory/vktProtectedMemStorageBufferTests.cpp#L864-L881) | Defines the `ssbo_read` and `ssbo_write` roots and six static inputs. |
| Atomic registration and reference values | [`createAtomicStorageBufferTests`](../../../modules/vulkan/protected_memory/vktProtectedMemStorageBufferTests.cpp#L884-L984) and [`calculateAtomicOpData`](../../../modules/vulkan/protected_memory/vktProtectedMemStorageBufferTests.cpp#L793-L860) | Defines atomic groups, inputs, random generation, and expected results. |
| Protection and pipeline flags | [`protectedAccess` and `flags`](../../../modules/vulkan/protected_memory/vktProtectedMemStorageBufferTests.cpp#L730-L750) | Defines build-dependent protection groups and pipeline flag values. |
| Protected memory semantics | [`Protected Memory`](../../../../vulkan-docs/src/chapters/memory.adoc#L5566-L5654) | Grounds the protected-memory and protected-queue explanation. |

## Questions / Risk Points for User Audit

- Does the distinction between the SSBO result buffer, source buffer, and host-visible uniform buffer remain clear?
- Is the `no_protected_access` mode described as unprotected without implying that all other pipeline flags are unprotected?
- Is the atomic dispatch explanation clear that compute invocations update distinct array elements in this CTS implementation?
- Should the final page include both fragment and compute walkthroughs, or is the compute read case sufficient as the representative shader path?
- Does the hierarchy tree expose the three implementation-bearing test families while leaving deeper generated dimensions to later sections?

## Conversion Notes for Final Wiki Rewrite

- Keep `ssbo_read`, `ssbo_write`, and `ssbo_atomic` as the primary behavior values because each selects a different shader template and validation rule.
- Distill the protected-memory model to the final page's Background Knowledge and keep detailed resource setup in Runtime Execution.
- Use the compute `ssbo_read` static case as the one representative shader walkthrough. It shows both storage-buffer declarations and the copy operation without adding the fragment render-target boilerplate.
- Keep the exact `### Failure Cause Mapping` table in the final page. Write `### Cause Analysis` afresh from the validation and synchronization behavior.
- Preserve the source links for shader generation, fragment/compute execution, registration, atomic reference calculation, and the Vulkan protected-memory rules.
