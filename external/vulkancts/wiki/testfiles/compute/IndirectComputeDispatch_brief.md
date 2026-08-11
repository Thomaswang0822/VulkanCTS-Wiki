# Understanding Brief: compute.pipeline.indirect_dispatch — vktComputeIndirectComputeDispatchTests.cpp

This brief prepares a rewrite of the `indirect_dispatch` Level-3 page implemented by `vktComputeIndirectComputeDispatchTests.cpp`. The file owns two subgroups (`upload_buffer`, `gen_in_compute`) that exercise the same dispatch parameter matrix through two different command-buffer construction paths.

## One-Sentence Test Purpose

This test checks whether compute pipelines correctly honor dispatch parameters supplied through `vkCmdDispatchIndirect` (with both uploaded and compute-generated indirect command buffers) under varying offsets, multi-dispatch sequences, empty commands, compute-only queues, and device-address-based dispatch variants.

## Background Knowledge

### Two flavors, one parameter matrix

The page covers two intermediate nodes (`upload_buffer`, `gen_in_compute`) under `compute.pipeline.indirect_dispatch`. The two flavors share the exact same `s_dispatchCases` parameter matrix declared in [`createIndirectComputeDispatchTests`](../../../modules/vulkan/compute/vktComputeIndirectComputeDispatchTests.cpp#L842-L872), so the only structural difference between them is *how* the indirect command buffer is populated before each dispatch. Both flavors register a base case and a `_compute_only_queue` variant for every entry in `s_dispatchCases`, and non-VulkanSC builds also add a `_device_address` variant that uses `vkCmdDispatchIndirect2KHR` instead of `vkCmdDispatchIndirect`. The matrix alternates device-address variants between `upload_buffer` and `gen_in_compute` based on `(ndx % 2) == (computePipelineConstructionType % 2)` so each pipeline-construction type registers roughly half of the device-address cases under each subgroup [`vktComputeIndirectComputeDispatchTests.cpp#L899-L917`](../../../modules/vulkan/compute/vktComputeIndirectComputeDispatchTests.cpp#L899-L917).

Why it matters here:

- The reader who only looks at one subgroup will miss the device-address parity rule; it lives in the registration loop, not in either subgroup's instance code.
- The shared matrix means the parameter dimension discussion belongs to *both* subgroups; the only behavioral difference between them is the buffer-filling mechanism.

### `vkCmdDispatchIndirect` and the `VkDispatchIndirectCommand` layout

`vkCmdDispatchIndirect` reads three `uint32_t` values (`groupCountX`, `groupCountY`, `groupCountZ`) from a buffer whose usage flag is `VK_BUFFER_USAGE_INDIRECT_BUFFER_BIT`. The host-side test applies the same layout to its result-block pre-fill so the same shader can compare the dispatched `gl_NumWorkGroups` against the host-known command triplet [`vktComputeIndirectComputeDispatchTests.cpp#L210-L213`](../../../modules/vulkan/compute/vktComputeIndirectComputeDispatchTests.cpp#L210-L213), [`vktComputeIndirectComputeDispatchTests.cpp#L421-L437`](../../../modules/vulkan/compute/vktComputeIndirectComputeDispatchTests.cpp#L421-L437). The constant `INDIRECT_COMMAND_OFFSET = 3 * sizeof(uint32_t)` is exactly the stride between back-to-back indirect commands in the `multi_dispatch` and `multi_dispatch_reuse_command` cases.

Why it matters here:

- Every test case carries an offset relative to the start of the indirect buffer. The smallest offset is `0` and the largest is `(1 << 20) + 12`, which forces the buffer size to either include enough leading bytes (`small_offset`) or scale up to two megabytes (`large_offset`).
- The shader reads `gl_NumWorkGroups` (a `uvec3` built-in) and atomically adds `1` to a per-result-block counter when that triplet matches the host-known triplet. A correct execution produces `numPassed == workGroupSize.product() * numWorkGroups.product()`.

### Compute-to-indirect synchronization barrier

`gen_in_compute` does not upload the indirect command buffer from the host; it dispatches a small compute shader that writes the triplets into the indirect buffer and then needs the indirect-command consumer to see those writes. The barrier required by the Vulkan spec for that handoff is `VkBufferMemoryBarrier` from `VK_ACCESS_SHADER_WRITE_BIT` (compute writes the indirect buffer) to `VK_ACCESS_INDIRECT_COMMAND_READ_BIT`, with `VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT` as the source stage and `VK_PIPELINE_STAGE_DRAW_INDIRECT_BIT` as the destination stage [`vktComputeIndirectComputeDispatchTests.cpp#L751-L768`](../../../modules/vulkan/compute/vktComputeIndirectComputeDispatchTests.cpp#L751-L768).

Why it matters here:

- This is the *only* nontrivial synchronization in the page. `upload_buffer` does not need it because the host flushes the indirect buffer allocation directly with `vk::flushAlloc` before recording the dispatch.
- A driver that omits the buffer memory barrier between the generator dispatch and the indirect dispatch will likely execute the indirect dispatch with stale or zero triplets, which the verification loop would see as `numPassed == 0` instead of the expected count.

### Pipeline construction variant

The category dispatcher runs every child factory under three roots (`pipeline`, `shader_object_spirv`, `shader_object_binary`) [`vktComputeTests.cpp#L48-L85`](../../../modules/vulkan/compute/vktComputeTests.cpp#L48-L85). The shader-object roots are non-VulkanSC. The instance code uses `vk::ComputePipelineWrapper` for the verifier pipeline, which lets the same test instance run under any pipeline construction type.

Why it matters here:

- The device-address alternation rule `(ndx % 2) == (computePipelineConstructionType % 2)` is the only place where the construction type affects which tests are registered. The `checkSupport` helper `checkShaderObjectRequirements` is called regardless, so a missing shader-object feature would skip the case under the shader-object roots.
- `gen_in_compute` additionally builds its generator pipeline with `makeComputePipeline` rather than the wrapper because the generator pipeline only runs once per case.

### Compute-only queue families

Each base case in `s_dispatchCases` is duplicated as a `<case>_compute_only_queue` variant. The `_compute_only_queue` variant requires a queue family that has `VK_QUEUE_COMPUTE_BIT` but not `VK_QUEUE_GRAPHICS_BIT`, and the host builds a custom device that exposes that queue family alongside the universal queue family [`vktComputeIndirectComputeDispatchTests.cpp#L88-L206`](../../../modules/vulkan/compute/vktComputeIndirectComputeDispatchTests.cpp#L88-L206), [`vktComputeIndirectComputeDispatchTests.cpp#L661-L681`](../../../modules/vulkan/compute/vktComputeIndirectComputeDispatchTests.cpp#L661-L681). The device-address variant additionally checks `VK_KHR_device_address_commands` [`vktComputeIndirectComputeDispatchTests.cpp#L683-L684`](../../../modules/vulkan/compute/vktComputeIndirectComputeDispatchTests.cpp#L683-L684).

Why it matters here:

- The custom device path is gated to VulkanSC through `CTS_USES_VULKANSC` because VulkanSC may not have a separate non-graphics compute queue family.
- A device that has only one queue family supporting compute (the universal family) would fail `checkSupport` for the `_compute_only_queue` variant and throw `NotSupportedError`.

### Device-address dispatch variant

The non-VulkanSC `_device_address` variant uses `vkCmdDispatchIndirect2KHR` instead of `vkCmdDispatchIndirect`. The buffer must additionally carry `VK_BUFFER_USAGE_SHADER_DEVICE_ADDRESS_BIT` and `MemoryRequirement::DeviceAddress`, and the indirect buffer device address is queried through `getBufferDeviceAddress`. The `VkDispatchIndirect2InfoKHR` struct adds `addressRange` and `addressFlags` fields, and the test exercises several `addressFlags` values based on the registered workgroup size: `VK_ADDRESS_COMMAND_UNKNOWN_STORAGE_BUFFER_USAGE_BIT_KHR` is always set, plus `VK_ADDRESS_COMMAND_UNKNOWN_TRANSFORM_FEEDBACK_BUFFER_USAGE_BIT_KHR` when `workGroupSize.x() > 1` and `VK_ADDRESS_COMMAND_FULLY_BOUND_BIT_KHR` when `workGroupSize.y() > 1` [`vktComputeIndirectComputeDispatchTests.cpp#L471-L532`](../../../modules/vulkan/compute/vktComputeIndirectComputeDispatchTests.cpp#L471-L532).

Why it matters here:

- The `addressFlags` selection is the only test-side decision that varies per registered case for the device-address variant. The validation contract is identical to the non-device-address variant.

## One Concrete Example

Consider `compute.pipeline.indirect_dispatch.upload_buffer.single_invocation`. The host allocates an indirect buffer of size `INDIRECT_COMMAND_OFFSET = 12` bytes with usage `INDIRECT_BUFFER_BIT | STORAGE_BUFFER_BIT`, writes `1` into each of `data[0]`, `data[1]`, `data[2]`, then flushes the allocation and records `vkCmdDispatchIndirect(cmdBuffer, indirectBuffer, 0)`. The verifier shader runs with `local_size = (1,1,1)`, dispatches `gl_NumWorkGroups == (1,1,1)`, sees the per-block `expectedGroupCount = (1,1,1)` match, and atomically increments the per-block counter to `1`. The host then reads back the result buffer and expects `numPassed == 1 * (1*1*1) == 1`. The same shape is repeated as `multiple_groups` (one workgroup of `(2,3,5)` workgroups with `(1,1,1)` local size, expected count `30`), `multiple_groups_multiple_invocations` (one workgroup of `(1,2,3)` workgroups with `(2,3,1)` local size, expected count `18`), and so on through the matrix. `gen_in_compute` uses the same matrix but the indirect buffer is populated by a generated compute shader that writes the same triplets at the same offsets; the difference is only the barrier between the generator and the indirect dispatch.

## End-to-End Test Flow

```text
[host] checkSupport — gate compute-only queue family, device-address commands, shader-object requirements
[host] build indirect buffer with INDIRECT_BUFFER_BIT | STORAGE_BUFFER_BIT (and SHADER_DEVICE_ADDRESS_BIT for device-address variant)
[host] pre-fill result buffer with expected triplets and 0 in numPassed slots
[device] (gen_in_compute only) run generator compute shader; bind descriptor set for indirect buffer; cmdDispatch(1,1,1)
[device] (gen_in_compute only) cmdPipelineBarrier(COMPUTE_SHADER -> DRAW_INDIRECT, SHADER_WRITE -> INDIRECT_COMMAND_READ)
[host] bind compute pipeline; allocate descriptor sets; bind descriptor sets in a loop
[device] (or upload_buffer host) fill the indirect buffer with the command triplet for each case
[device] record vkCmdDispatchIndirect or vkCmdDispatchIndirect2KHR
[device] cmdPipelineBarrier(COMPUTE_SHADER -> HOST, SHADER_WRITE -> HOST_READ) on result buffer
[host] submit and wait; invalidate result buffer; walk every result block
[host] expect numPassed == workGroupSize.product() * numWorkGroups.product() for every block
```

For the `_compute_only_queue` variant the host additionally builds a custom device with a separate queue family and routes `cmdDispatchIndirect` (and the optional `cmdDispatchIndirect2KHR`) through the compute-only queue.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- Inline GLSL compute shader `indirect_dispatch_<case>_verify` specialized with `LOCAL_SIZE_X/Y/Z` from the registered workgroup size [`vktComputeIndirectComputeDispatchTests.cpp#L624-L654`](../../../modules/vulkan/compute/vktComputeIndirectComputeDispatchTests.cpp#L624-L654).
- Inline GLSL compute shader `indirect_dispatch_<case>_generate` for `gen_in_compute` only. The shader has hard-coded `local_size = (1,1,1)` and emits one `writeCmd(offset, uvec3)` call per registered dispatch command, where the `offset` argument is the byte offset divided by `sizeof(uint32_t)` and the `uvec3` triplet is the registered `numWorkGroups` [`vktComputeIndirectComputeDispatchTests.cpp#L790-L830`](../../../modules/vulkan/compute/vktComputeIndirectComputeDispatchTests.cpp#L790-L830).
- `ComputePipelineWrapper` instance for the verifier pipeline; `makeComputePipeline` for the generator pipeline (gen_in_compute only).

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Result storage buffer (one block per command) | yes | yes | atomicAdd on `numPassed` per invocation | yes | Carries the per-command shader-side validation signal |
| Indirect command buffer (upload_buffer) | yes | yes | n/a (host-filled; `flushAlloc`) | yes | Holds the `VkDispatchIndirectCommand` triplets consumed by `vkCmdDispatchIndirect` |
| Indirect command buffer (gen_in_compute) | yes | yes | write by generator shader; read by indirect dispatch | yes | Holds triplets written by compute shader and consumed by indirect dispatch in the same command buffer |
| Indirect command buffer (device_address variant) | yes | yes | same as above but with `VK_BUFFER_USAGE_SHADER_DEVICE_ADDRESS_BIT` | yes | Backed by a device address for `VkDispatchIndirect2InfoKHR::addressRange` |
| Compute-only queue | yes | yes | submits the indirect dispatch | n/a | Used by the `_compute_only_queue` variant |
| Descriptor set with `STORAGE_BUFFER` binding 0 | yes | yes | read/write result buffer | n/a | The verifier shader's only binding |
| Generator descriptor set (gen_in_compute only) | yes | yes | write indirect buffer | n/a | The generator shader's only binding |

## What Is Checked

The pass condition for every case is the same per-result-block check:

- The host walks `dispatchCommands.size()` blocks of `resultBlockSize` bytes.
- For each block, the host reads the pre-filled `expectedGroupCount = (groupCountX, groupCountY, groupCountZ)` triplet and the shader-incremented `numPassed` counter.
- The expected `numPassed` is `workGroupSize.product() * numWorkGroups.product()` [`vktComputeIndirectComputeDispatchTests.cpp#L557-L590`](../../../modules/vulkan/compute/vktComputeIndirectComputeDispatchTests.cpp#L557-L590).
- A mismatch logs `ERROR: got invalid result for invocation <i>: got numPassed = <v>, expected <v>` and the test returns `QP_TEST_RESULT_FAIL`.

The `empty_command` case is special: it dispatches `(0,0,0)` workgroups, so the verifier shader does not execute at all. The expected `numPassed` is `0`, and the host accepts `0 == 0`.

## Behavior Parameter Identification

> **Behavior parameter:** `subgroup flavor` (the registered subgroup under `compute.pipeline.indirect_dispatch`)
>
> **Candidate values:** `upload_buffer`, `gen_in_compute`

If the identification is wrong, the failure analysis below will need to be redone. The flavor is chosen as the primary behavioral axis because it determines the command-buffer construction mechanism (host upload vs compute generation) and therefore the only nontrivial synchronization (the compute-to-indirect barrier). The `_compute_only_queue` and `_device_address` modifiers live inside the parameter dimension table; they are secondary axes, not flavors.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `upload_buffer` | Wrong `VkDispatchIndirectCommand` layout interpretation; offset into the indirect buffer misread; result block pre-fill mismatch; missing `flushAlloc` after host fill; compute-to-host `cmdPipelineBarrier` failing to make shader atomic writes visible; missing descriptor set bind between dispatches; descriptor type or range mismatch on the result buffer; pipeline construction (pipeline vs shader object) mishandling; queue family selector picking the wrong queue; `vkCmdDispatchIndirect2KHR` path failing when `_device_address` modifier is set. |
| `gen_in_compute` | Missing `VkBufferMemoryBarrier` from `SHADER_WRITE` to `INDIRECT_COMMAND_READ` between the generator dispatch and the indirect dispatch; wrong source or destination stage on the compute-to-indirect barrier; generator shader writing triplets at wrong offsets; generator shader local size or descriptor layout mismatch; result-block pre-fill mismatch on the host; compute-to-host `cmdPipelineBarrier` failing; pipeline construction mishandling; queue family selector picking the wrong queue for the `_compute_only_queue` modifier; `vkCmdDispatchIndirect2KHR` path failing when `_device_address` modifier is set. |

## Important Variations and Special Cases

- **`empty_command` is a zero-dispatch smoke test.** The triplet is `(0,0,0)` and the expected `numPassed` is `0`; the shader does not run but the host check still exercises the indirect-dispatch code path. A driver that fails to honor a `(0,0,0)` dispatch (for example, by treating it as an error) would fail this case even though it is also exercised in `multiple_groups`.
- **`multi_dispatch_reuse_command` repeats offsets.** Several offsets (`0`, `104`, `52`) appear twice; the test expects the same triplet to be honored twice. A driver that incorrectly treats each indirect dispatch as a strict sequence (and refuses to reuse a previous offset) would fail this case.
- **`_device_address` alternates between subgroups.** `(ndx % 2) == (computePipelineConstructionType % 2)` decides whether a `_device_address` case lands in `upload_buffer` or `gen_in_compute` [`vktComputeIndirectComputeDispatchTests.cpp#L907-L916`](../../../modules/vulkan/compute/vktComputeIndirectComputeDispatchTests.cpp#L907-L916). For each pipeline-construction type, roughly half of the device-address variants land in each subgroup.
- **`_compute_only_queue` always runs alongside the base case.** Every entry in `s_dispatchCases` produces both a base case and a `_compute_only_queue` case under both flavors.
- **Buffer alignment.** The result buffer size is rounded up to `minStorageBufferOffsetAlignment`, so the offset arithmetic on the host side does not need to handle unaligned blocks [`vktComputeIndirectComputeDispatchTests.cpp#L215-L227`](../../../modules/vulkan/compute/vktComputeIndirectComputeDispatchTests.cpp#L215-L227).

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Test case matrix | [vktComputeIndirectComputeDispatchTests.cpp#L842-L872](../../../modules/vulkan/compute/vktComputeIndirectComputeDispatchTests.cpp#L842-L872) | Shared `s_dispatchCases` array used by both flavors |
| Registration loop | [vktComputeIndirectComputeDispatchTests.cpp#L874-L921](../../../modules/vulkan/compute/vktComputeIndirectComputeDispatchTests.cpp#L874-L921) | Both flavors, plus `_compute_only_queue` and `_device_address` modifiers |
| Uploaded buffer fill | [vktComputeIndirectComputeDispatchTests.cpp#L326-L349](../../../modules/vulkan/compute/vktComputeIndirectComputeDispatchTests.cpp#L326-L349) | Host writes triplets, then `flushAlloc` |
| Compute-generated buffer fill | [vktComputeIndirectComputeDispatchTests.cpp#L717-L769](../../../modules/vulkan/compute/vktComputeIndirectComputeDispatchTests.cpp#L717-L769) | Generator shader + compute-to-indirect barrier |
| Dispatch loop | [vktComputeIndirectComputeDispatchTests.cpp#L466-L538](../../../modules/vulkan/compute/vktComputeIndirectComputeDispatchTests.cpp#L466-L538) | Descriptor bind + `cmdDispatchIndirect` (or `cmdDispatchIndirect2KHR`) |
| Result verification | [vktComputeIndirectComputeDispatchTests.cpp#L557-L590](../../../modules/vulkan/compute/vktComputeIndirectComputeDispatchTests.cpp#L557-L590) | Per-block `numPassed == expected` check |
| `checkSupport` | [vktComputeIndirectComputeDispatchTests.cpp#L661-L688](../../../modules/vulkan/compute/vktComputeIndirectComputeDispatchTests.cpp#L661-L688) | Compute-only queue, device-address commands, shader-object requirements |
| Verifier shader generation | [vktComputeIndirectComputeDispatchTests.cpp#L624-L654](../../../modules/vulkan/compute/vktComputeIndirectComputeDispatchTests.cpp#L624-L654) | `indirect_dispatch_<case>_verify` shader template |
| Generator shader generation | [vktComputeIndirectComputeDispatchTests.cpp#L790-L830](../../../modules/vulkan/compute/vktComputeIndirectComputeDispatchTests.cpp#L790-L830) | `indirect_dispatch_<case>_generate` shader template |
| Custom compute-only device | [vktComputeIndirectComputeDispatchTests.cpp#L88-L206](../../../modules/vulkan/compute/vktComputeIndirectComputeDispatchTests.cpp#L88-L206) | Builds a custom device for the `_compute_only_queue` variant |
| Category dispatcher | [vktComputeTests.cpp#L48-L85](../../../modules/vulkan/compute/vktComputeTests.cpp#L48-L85) | `pipeline`/`shader_object_spirv`/`shader_object_binary` roots |

## Questions / Risk Points for User Audit

- Is the `upload_buffer` vs `gen_in_compute` distinction clear enough that a reader does not conflate the two flavors?
- Is the compute-to-indirect `VkBufferMemoryBarrier` described at the right level of detail (source stage, destination stage, source/dest access masks)?
- Are the `_compute_only_queue` and `_device_address` modifiers explained as secondary axes rather than as new flavors?
- Is the `empty_command` zero-dispatch smoke test acknowledged as the special case it is, instead of being lumped with `multiple_groups`?
- Is the `multi_dispatch_reuse_command` offset reuse explained well enough that a reader does not interpret the duplicate offsets as a bug?

## Conversion Notes for Final Wiki Rewrite

- Distill the brief's Background Knowledge into a compact `## Background Knowledge` section that captures only the prerequisites the reader needs (indirect command layout, compute-to-indirect barrier semantics, compute-only queue requirement, device-address variant).
- Move the per-class source links into `## Source Reference Appendix`.
- Carry the `### Failure Cause Mapping` table above verbatim into the final page's `## Failure Meaning` → `### Failure Cause Mapping`.
- Write `### Cause Analysis` fresh; it should not copy the brief's notes.
- The representative shader walkthrough will use the verifier shader from `compute.pipeline.indirect_dispatch.upload_buffer.single_invocation` because it is the canonical read-and-compare shape, and the SPIR-V will be generated from the reconstructed GLSL and verified through `shader-disassembler` to ensure the assembly `; Version:` header matches the target SPIR-V version.
- The `external/vulkan-docs` tree is not present in the inspected checkout, so any spec-grounded claims (compute-to-indirect barrier stages, `vkCmdDispatchIndirect` triplet layout, `VK_KHR_device_address_commands` flags) rely on the CTS source as authoritative; if a spec-grounded claim cannot be made, the page should say so rather than guess.
