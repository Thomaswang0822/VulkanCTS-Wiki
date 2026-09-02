# Understanding Brief: ComputeLayout

## One-Sentence Test Purpose

These tests check whether `VK_NV_device_generated_commands` applies compute indirect-command layout tokens for push constants, pipeline selection, and dispatch execution, including partial updates, pipeline-address alignment, compute-queue execution, and capture/replay addresses.

## Background Knowledge

### Device-generated command layouts

A `VkIndirectCommandsLayoutNV` describes the order and byte ranges of token data in an indirect command stream. Each generated sequence reads the fields at the offsets defined by the layout. In these tests, state tokens prepare the compute pipeline or push-constant state, and `VK_INDIRECT_COMMANDS_TOKEN_TYPE_DISPATCH` is always the final action token.

The layout therefore determines how the same stream bytes become Vulkan state. A push-constant token can cover all three values or selected overlapping ranges. A pipeline token consumes a `VkDeviceAddress` that identifies the pipeline metadata written with `vkCmdUpdatePipelineIndirectBufferNV`. The dispatch token consumes the following `VkDispatchIndirectCommand` fields.

### Compute dispatch and shader-visible state

The generated GLSL compute shader uses `local_size_x = 64`. For each invocation it calculates a flat workgroup index and writes one `uint` to a storage buffer. `dispatchOffset` selects the output region, `valueOffset` gives each dispatch a distinct value range, and `skipIndex` leaves one invocation at zero. The host compares the resulting buffer with the same formula.

## One Concrete Example

The registered case `dEQP-VK.dgc.nv.compute.layout.pipeline_push_dispatch_align4_cq` combines a pipeline token, a push-constant token, a dispatch token, 4-byte stream-offset alignment, and execution on the compute queue. The pipeline token selects one specialized compute pipeline for each sequence. The push-constant token supplies `dispatchOffset` and `skipIndex`; `valueOffset` is a specialization constant in that pipeline. The dispatch token then supplies the workgroup count.

The case is not testing an arbitrary command stream. It checks whether the declared token ranges and their byte layout cause each dispatch to see the values intended for its sequence.

## End-to-End Test Flow

```text
[host] select one of six TestType values and the align4, computeQueue, and captureReplay dimensions
[host] generate four workgroup counts in the inclusive range 1..16 with a deterministic TestType-derived seed
[host] generate one SpecializationData record per dispatch: dispatchOffset, skipIndex, and valueOffset
[host] create a zeroed host-visible storage buffer and bind it at set 0, binding 0
[host] generate the compute GLSL source and create one pipeline or one specialized pipeline per dispatch
[host] build a VkIndirectCommandsLayoutNV with the selected state tokens and a final VK_INDIRECT_COMMANDS_TOKEN_TYPE_DISPATCH token
[host] encode token payloads and VkDispatchIndirectCommand values in a host-visible indirect buffer
[host] allocate the preprocess buffer and update indirect pipeline metadata when pipeline tokens are used
[host] bind the descriptor set and initial pipeline, push complementary state when applicable, and execute four sequences
[device] process each sequence's tokens, run 64-invocation workgroups, and write the output buffer
[host] make shader writes visible to host reads, invalidate the allocation, compare every output value, and return the test result
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `initPrograms()` emits one GLSL compute program named `comp`. Push-only cases declare `dispatchOffset`, `skipIndex`, and `valueOffset` as push constants. `pipeline_dispatch` declares all three as specialization constants. Pipeline-plus-push cases use push constants for `dispatchOffset` and `skipIndex`, with `valueOffset` as specialization constant.
- `SpecializationData` holds `dispatchOffset`, `skipIndex`, and `valueOffset` for each of the four sequences. Pipeline cases use each record to specialize a distinct `DGCComputePipeline`; push-only cases put the record into the indirect stream.
- `makeCommandsLayout()` selects the token arrangement. `PUSH_DISPATCH` and `COMPLEMENTARY_PUSH_DISPATCH` use one push-constant token followed by dispatch. `PARTIAL_PUSH_DISPATCH` uses two overlapping push-constant tokens followed by dispatch. `PIPELINE_DISPATCH` uses a pipeline token followed by dispatch. The two pipeline-plus-push types use a pipeline token, a push-constant token, and dispatch.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Host-visible output buffer | yes | yes, at descriptor set binding 0 | written by the compute shader | yes | Stores one `uint` per invocation for result checking. |
| Descriptor set and storage-buffer descriptor | yes | yes | used to locate the output buffer | no | Provides `set = 0, binding = 0` to the shader. |
| Indirect commands buffer | yes | read by generated-command execution | read during preprocessing and execution | no | Contains push-constant payloads, pipeline addresses, padding where required, and dispatch dimensions. |
| Compute pipeline or specialized pipeline set | yes | yes | selected or bound for generated dispatches | no | Supplies the compute shader and, for pipeline cases, per-sequence specialization values. |
| Preprocess buffer | yes | yes | written and read by generated-command processing | no | Stores implementation-defined preprocessing data. |
| Pipeline metadata and capture/replay addresses | yes for pipeline cases | updated through `vkCmdUpdatePipelineIndirectBufferNV` | read when a pipeline token is processed | no | Connects each pipeline token's device address with the selected compute pipeline. |

## What Is Checked

- The shader writes `valueOffset + (workGroupIndex << 10) + gl_LocalInvocationIndex` to `dispatchOffset + workGroupIndex * 64 + gl_LocalInvocationIndex`, unless `gl_LocalInvocationIndex == skipIndex`; the selected location must remain zero.
- The host checks all `totalNumWorkGroups * 64` output values. `totalNumWorkGroups` is the sum of the four generated workgroup counts.
- On a mismatch, the log records the flat output index, expected and actual values, dispatch index, workgroup index, invocation index, `skipIndex`, and `valueOffset`. The test returns `fail("Unexpected output values found; check log for details")`.
- The test returns `pass("Pass")` only if every checked value matches.

## Behavior Parameter Identification

> **Behavior parameter:** `TestType` registered test family
>
> **Candidate values:** `push_dispatch`, `complementary_push_dispatch`, `partial_push_dispatch`, `pipeline_dispatch`, `pipeline_push_dispatch`, `pipeline_complementary_push_dispatch`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `push_dispatch` | Push-constant token range or payload decoding was wrong; the dispatch token was decoded at the wrong stream offset. |
| `complementary_push_dispatch` | The externally pushed `valueOffset2` was applied at the wrong push-constant offset or combined with generated data incorrectly; dispatch data was decoded incorrectly. |
| `partial_push_dispatch` | One of the overlapping push-constant updates was applied at the wrong offset, size, or order. |
| `pipeline_dispatch` | The pipeline token selected the wrong specialized pipeline, its address was decoded incorrectly, or dispatch data was decoded incorrectly. |
| `pipeline_push_dispatch` | Pipeline selection, specialization of `valueOffset`, generated push-constant updates, or dispatch decoding was wrong. |
| `pipeline_complementary_push_dispatch` | Pipeline selection, generated push constants, or the externally pushed `valueOffset2` was applied at the wrong offset; dispatch data was decoded incorrectly. |

## Important Variations and Special Cases

- The `align4` dimension is present only for `pipeline_dispatch_align4` and `pipeline_push_dispatch_align4`. The support check requires `minIndirectCommandsBufferOffsetAlignment <= 4`. Without `align4`, the layout rounds each stream stride up to `sizeof(VkDeviceAddress)` so pipeline addresses retain native alignment.
- The `computeQueue` dimension adds the `_cq` suffix and selects the device's compute queue family and queue instead of the default queue. The generated work remains compute-only.
- `captureReplay` is present only for `pipeline_push_dispatch_capture_replay`. The support check requires pipeline switching and capture/replay support. The test first creates temporary pipelines to obtain indirect device addresses, then creates the active pipelines with those captured addresses.
- `complementary_push_dispatch` and `pipeline_complementary_push_dispatch` add `valueOffset2` as a host push constant outside the indirect stream. The offset is after the generated push data for the non-pipeline form and before it for the pipeline form, matching the shader declaration.
- `partial_push_dispatch` deliberately writes an incorrect first `skipIndex` value, then overwrites the overlapping middle and final values through two push-constant tokens. This exercises partial and overlapping updates rather than a single complete push.
- All cases use four sequences. The smoke tests cover dispatch-only layouts; this file adds state-token layouts that let each dispatch use distinct shader values and output regions.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Test types and matrix dimensions | [TestType and TestParams](../../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTests.cpp#L53-L110) | Defines the six behavior types and `align4`, `computeQueue`, and `captureReplay`. |
| Generated compute shader | [initPrograms()](../../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTests.cpp#L203-L273) | Emits push-constant and specialization-constant forms, the index calculation, and the skip condition. |
| Pipeline construction | [createPipelines()](../../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTests.cpp#L280-L388) | Creates single or per-sequence pipelines and capture/replay addresses. |
| Token layout construction | [makeCommandsLayout()](../../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTests.cpp#L390-L443) | Defines token order, push ranges, final dispatch token, and stream strides. |
| Indirect payload encoding | [makeIndirectCommands()](../../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTests.cpp#L445-L542) | Encodes push values, pipeline addresses, padding, and dispatch dimensions. |
| Runtime setup and execution | [iterate()](../../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTests.cpp#L545-L699) | Generates values, creates resources, preprocesses commands, binds state, and executes sequences. |
| Result scan | [result checking](../../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTests.cpp#L701-L747) | Defines expected values, diagnostics, and pass/fail status. |
| Registration | [createDGCComputeLayoutTests()](../../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTests.cpp#L752-L784) | Builds the nine registered NV families and `_cq` variants. |
| DGC support helper | [vktDGCUtil.cpp](../../../modules/vulkan/device_generated_commands/vktDGCUtil.cpp) | Supplies the common compute DGC support checks used by the case. |
| Vulkan DGC semantics | [Device-Generated Commands](../../../../vulkan-docs/src/chapters/device_generated_commands/generatedcommands.adoc#device-generated-commands) | Defines indirect layout tokens, preprocessing, pipeline updates, and generated execution. |
| Vulkan dispatch semantics | [Dispatching Commands](../../../../vulkan-docs/src/chapters/dispatch.adoc#dispatching-commands) | Defines indirect dispatch dimensions and compute workgroup execution. |

## Questions / Risk Points for User Audit

- Does the distinction between the six `TestType` values and the nine registered family names remain clear?
- Is the partial update case clear about why the first `skipIndex` payload is intentionally wrong?
- Is the 4-byte alignment case clear about stream stride versus the device address itself?
- Does the output formula explain why token decoding errors are visible in a per-dispatch comparison?
- Is the capture/replay sequence clear without implying that ordinary pipeline cases use captured addresses?

## Conversion Notes for Final Wiki Rewrite

- Use `TestType` as the primary behavioral axis, with one subsection for each of its six values.
- Keep the exact nine registered NV family names and their `_cq`, `_align4`, and capture/replay forms in the registration tree and parameter tables.
- Explain token order and stream encoding in `Behavior Parameters` and `Runtime Execution`, not in a source-inventory section.
- Carry this failure mapping table directly into the final page, then write fresh cause-analysis subsections.
- Include the generated shader's role and the output formula, but do not present a hand-written shader walkthrough as if it were a source file.
