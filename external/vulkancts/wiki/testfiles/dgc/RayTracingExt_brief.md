# Understanding Brief: DGC EXT ray-tracing tests

## One-Sentence Test Purpose

This test checks whether `VK_EXT_device_generated_commands` can generate and execute `VK_KHR_ray_tracing_pipeline` trace-ray commands while preserving execution-set selection, preprocessing, sequence order, shader binding table data, and ray-tracing shader results.

## Background Knowledge

### Device-generated command streams

A device-generated command layout describes fields in a host-provided command stream. This test layout can contain an execution-set token, a push-constant token, and a trace-rays token. `VK_INDIRECT_COMMANDS_LAYOUT_USAGE_EXPLICIT_PREPROCESS_BIT_EXT` separates command preprocessing from execution. `VK_INDIRECT_COMMANDS_LAYOUT_USAGE_UNORDERED_SEQUENCES_BIT_EXT` permits the implementation to process generated sequences in an order different from their stream order, so each sequence must identify its own data through the launch coordinates and push constant.

### Ray-tracing shader records and payloads

A ray-tracing pipeline selects raygen, miss, hit, and callable shader groups through shader binding table (SBT) regions. A `rayPayloadEXT` value travels from raygen to the selected miss or closest-hit shader. Closest-hit code also calls callable shaders through callable data. A shader record buffer (SRB) is storage associated with an SBT record, not a descriptor-buffer element; the test uses it to check that execution-set pipeline and SBT selection agree.

## One Concrete Example

The test divides a 16x16 logical image into two 16x8 dispatches. For one cell, raygen stores `gl_LaunchIDEXT` as its initial payload and traces a ray through the TLAS. A miss shader adds `(missIndex + 1u) * 1000000u` to the payload. A hit path adds `(chitIndex + 1u) * 100000u`, then callable shader 1 adds `2000` after callable shader 0 adds `1000`. The closest-hit shader records the final payload and the intersection shader records an attribute offset of `(isecIndex + 1u) * 10000u`.

The expected payload therefore distinguishes the selected miss or hit, the callable sequence, and the initial launch location without relying on a fixed shader invocation order.

## End-to-End Test Flow

```text
[host] choose four Boolean parameters: execution set, preprocess, unordered sequences, and compute queue
[host] create 16 BLAS objects from randomized triangle or AABB geometry and build one TLAS with 256 translated instances
[host] fill host-visible CellParams input and clear the CellOutput buffer
[host] create descriptors, a push-constant range, ray-tracing pipelines, SBT regions, and optional pipeline execution-set entries
[host] write two trace-ray records to the DGC stream, one for each 16x8 dispatch
[host] bind the initial pipeline and record optional vkCmdPreprocessGeneratedCommandsEXT
[host] execute the generated commands with vkCmdExecuteGeneratedCommandsEXT
[device] run raygen, traverse the TLAS, and invoke miss or intersection plus closest-hit and callable shaders
[device] write launch built-ins, ray built-ins, payloads, hit attributes, and SRB values to CellOutput
[host] wait for completion, invalidate the output allocation, and copy results back
[host] calculate the expected result for each of the 256 cells and return Pass or Fail
```

Preprocessing writes or prepares generated command state for a later execution. When the `preprocess` parameter is false, the test executes the same DGC stream without the preprocessed form. The test inserts `preprocessToExecuteBarrierExt` between preprocessing and execution. A shader-write to host-read barrier protects the output readback.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The test generates GLSL for two raygen shaders, two miss shaders, two closest-hit shaders, two intersection shaders, and two callable shaders. Each stage has a version without an SRB declaration and a version with `layout(shaderRecordEXT, std430)`. The generated programs require `GL_EXT_ray_tracing` and use `SPIRV_VERSION_1_4` build options.

The host creates one pipeline when `useExecutionSet` is false. It creates two pipelines when `useExecutionSet` is true, places them in a pipeline-based `VkIndirectExecutionSetEXT`, and puts the pipeline index in the execution-set token for each DGC sequence.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| 16 BLAS objects | yes | through TLAS instances | traversed | no | Each BLAS contains two geometries, with one active geometry and a selected closest primitive. |
| TLAS | yes | descriptor set binding 0 | traversed by `traceRayEXT` | no | Its 256 translated instances map each ray to one logical cell. |
| `CellParams` input buffer | yes | descriptor set binding 1 | read by all ray-tracing stages | no | Carries origin, transform, BLAS index, ray interval, flags, miss index, and expected geometry data. |
| `CellOutput` output buffer | yes | descriptor set binding 2 | written by all shader stages | yes | Stores the observations that the host compares with its model. |
| SBT regions | yes | passed through each `VkTraceRaysIndirectCommand2KHR` record | read by ray tracing | no | Select raygen, miss, hit, and callable records, with optional SRB data after each shader handle. |
| DGC buffer | yes | read by DGC preprocessing and execution | read by device-generated command processing | no | Contains optional execution-set indices, `offsetY`, and each `VkTraceRaysIndirectCommand2KHR`. |
| preprocess buffer | yes | passed to `DGCGenCmdsInfo` | written/read by DGC preprocessing and execution | no | Holds generated command state when explicit preprocessing is selected. |
| push constant `offsetY` | yes | pipeline layout | read by shaders | no | Maps the local 16x8 launch coordinates back to the full 16x16 cell array. |

## What Is Checked

The host checks all 256 `CellOutput` records. Checks include:

- raygen, miss, intersection, closest-hit, and callable `gl_LaunchIDEXT` and `gl_LaunchSizeEXT` values;
- initial and final ray payloads and the incoming/outgoing miss and closest-hit payloads;
- miss and hit world/object ray origins and directions, `gl_RayTminEXT`, `gl_RayTmaxEXT`, and `gl_IncomingRayFlagsEXT`;
- primitive, instance, custom-index, geometry-index, hit-kind, and hit-`T` values;
- object-to-world and world-to-object matrices in both the three-row and 3x4 built-in forms;
- intersection and closest-hit attributes;
- SRB data for raygen, the selected miss record, the selected hit record, and both callable records when the second SBT set is used.

Vector and floating-point comparisons use exact comparison where appropriate and a `1.0f / 256.0f` threshold for floating-point values. Any mismatch sets `fail`; the instance returns `tcu::TestStatus::fail("Fail; check log for details")`. If every record passes, it returns `tcu::TestStatus::pass("Pass")`.

## Behavior Parameter Identification

> **Behavior parameter:** registered test-family leaf, represented by four Boolean dimensions
>
> **Candidate values:** `no_execution_set`, `with_execution_set`, each with optional `_preprocess`, `_unordered`, and `_cq` suffixes

The four dimensions form the behavioral matrix. The primary axis is the execution path represented by the registered leaf, because each leaf changes how the same trace-ray work reaches execution: fixed pipeline or execution set, direct or preprocessed generation, ordered or unordered sequence processing, and graphics-capable or compute queue submission.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `no_execution_set` | Fixed-pipeline DGC binding, trace-ray command decoding, SBT selection, or ray-tracing shader result mismatch. |
| `no_execution_set_preprocess` | Explicit DGC preprocessing state or the preprocess-to-execute dependency is wrong. |
| `no_execution_set_unordered` | Unordered sequence handling does not preserve per-sequence push-constant and launch-coordinate interpretation. |
| `no_execution_set_preprocess_unordered` | The combined preprocessing and unordered-sequence path misgenerates or executes a sequence. |
| `no_execution_set_cq` | The generated trace-ray work or synchronization fails on a compute queue. |
| `no_execution_set_preprocess_cq` | Compute-queue preprocessing or its dependency before execution is wrong. |
| `no_execution_set_preprocess_unordered_cq` | The compute-queue path fails when preprocessing and unordered sequences are combined. |
| `no_execution_set_unordered_cq` | Compute-queue unordered sequence processing produces incorrect command or shader results. |
| `with_execution_set` | Pipeline execution-set selection, pipeline compatibility, or the selected pipeline's SBT/shader results are wrong. |
| `with_execution_set_preprocess` | Execution-set selection and explicit preprocessing do not produce the same intended trace-ray work. |
| `with_execution_set_unordered` | Execution-set selection or per-sequence data is wrong when sequence order is not fixed. |
| `with_execution_set_preprocess_unordered` | The combined execution-set, preprocessing, and unordered path is wrong. |
| `with_execution_set_cq` | Execution-set based trace-ray work fails on a compute queue. |
| `with_execution_set_preprocess_cq` | Execution-set preprocessing or compute-queue execution is wrong. |
| `with_execution_set_preprocess_unordered_cq` | The combined compute-queue path fails with an execution set, preprocessing, and unordered sequences. |
| `with_execution_set_unordered_cq` | Execution-set selection or per-sequence results are wrong on a compute queue with unordered sequences. |

## Important Variations and Special Cases

- Geometry is randomized with a fixed seed. A BLAS uses either four triangles or four AABBs, and only one of its two geometries is placed in the positive Z range. The other geometry cannot be hit by the +Z ray.
- A triangle's winding and the per-cell `rayFlags` select front/back-face culling or `kRayFlagsCullOpaqueEXT`. A cull result takes the miss path.
- The two SBT sets separate records without SRB data from records with host-generated `vec4` SRB data. With an execution set, the two sets correspond to two pipelines; without one, both sets belong to the single pipeline.
- The `_cq` variants request a compute queue with `context.getComputeQueue()`. Missing queue support is a support failure, not a functional result mismatch.
- The test uses `VK_KHR_ray_tracing_maintenance1` for the `traceRaysIndirect2` command support used by the DGC trace-rays token.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Parameters, support, and registration | `external/vulkancts/modules/vulkan/device_generated_commands/vktDGCRayTracingTestsExt.cpp#L333-L393`, `#L1993-L2010` | Defines the four Boolean dimensions, requirements, and exact registered leaves. |
| Generated shader declarations and payload updates | `external/vulkancts/modules/vulkan/device_generated_commands/vktDGCRayTracingTestsExt.cpp#L419-L845` | Defines ray payload, built-in, hit-attribute, callable-data, and SRB observations. |
| Acceleration structures and DGC setup | `external/vulkancts/modules/vulkan/device_generated_commands/vktDGCRayTracingTestsExt.cpp#L990-L1404` | Creates BLAS/TLAS resources, SBTs, execution sets, command streams, preprocessing, and execution. |
| Result model and failure return | `external/vulkancts/modules/vulkan/device_generated_commands/vktDGCRayTracingTestsExt.cpp#L1410-L1988` | Computes expected results and maps any mismatch to the CTS status. |
| DGC preprocessing and unordered semantics | `external/vulkan-docs/src/chapters/device_generated_commands/generatedcommands.adoc`, `external/vulkan-docs/src/chapters/synchronization.adoc` | Specifies command preprocessing, execution, and unordered sequence behavior. |
| Indirect2 trace-ray command | `external/vulkan-docs/src/chapters/raytracing.adoc#L424-L508` | Defines `VkTraceRaysIndirectCommand2KHR` and its device-read parameters. |

## Questions / Risk Points for User Audit

- Does the four-dimension behavioral axis read clearly as the reason for the sixteen registered leaves?
- Is the distinction between a pipeline execution set and an SBT's SRB data clear?
- Is the miss-versus-hit payload arithmetic sufficient to explain the result model without reproducing every shader?
- Should the final page include a generated shader walkthrough, or is the stage and payload summary enough for this DGC family?

## Conversion Notes for Final Wiki Rewrite

- Keep the final page's Background Knowledge to the DGC command-stream and ray-tracing payload concepts.
- Carry the four Boolean dimensions into the final parameter table and explain the registered suffix construction exactly.
- Preserve the Failure Cause Mapping table in the final page, then write Cause Analysis separately from this brief.
- Put the full output-field inventory in a compact validation table. Keep source navigation in the final appendix.
- The relevant spec evidence is `generatedcommands.adoc`, `synchronization.adoc`, and `raytracing.adoc`; use it to avoid treating preprocessing or unordered execution as a host-side ordering guarantee.
