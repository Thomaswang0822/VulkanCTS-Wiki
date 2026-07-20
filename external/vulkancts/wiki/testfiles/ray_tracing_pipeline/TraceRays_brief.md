# Understanding Brief: TraceRays (trace_rays_cmds / trace_rays_cmds_maintenance_1 / trace_rays_indirect2)

## One-Sentence Test Purpose

This test checks whether an implementation correctly dispatches a ray tracing pipeline through every `vkCmdTraceRays*` entry point - direct, indirect (CPU- or GPU-sourced dimensions), and indirect2 (CPU- or GPU-sourced shader binding tables plus dimensions) - producing identical hit/miss image results for the same scene and launch dimensions.

## Background Knowledge

### The four trace-rays dispatch variants and what each sources on the device

A ray tracing dispatch is launched by a command-buffer command. Vulkan provides a family of these commands that differ in which parameters the host provides directly versus which the device reads from a buffer at execution time:

- `vkCmdTraceRaysKHR` (direct): the host passes the four shader binding table (SBT) regions and the `width`/`height`/`depth` launch dimensions inline. Nothing is read indirectly.
- `vkCmdTraceRaysIndirectKHR` (indirect): the host passes the four SBT regions inline, but the launch dimensions are read by the device from a `VkTraceRaysIndirectCommandKHR` structure (only `width`, `height`, `depth`) at a buffer device address. Requires the `rayTracingPipelineTraceRaysIndirect` feature.
- `vkCmdTraceRaysIndirect2KHR` (indirect2): the host passes only a single buffer device address. The device reads a `VkTraceRaysIndirectCommand2KHR` structure that contains all four SBT regions *and* the launch dimensions. Requires the `rayTracingPipelineTraceRaysIndirect2` feature from `VK_KHR_ray_tracing_maintenance1`.

The spec states `vkCmdTraceRaysIndirect2KHR` "behaves similarly to `vkCmdTraceRaysIndirectKHR` except that shader binding table parameters as well as dispatch dimensions are read by the device from `indirectDeviceAddress` during execution," and that the members of `VkTraceRaysIndirectCommand2KHR` have the same meaning as the similarly named parameters of `vkCmdTraceRaysKHR`.

Why it matters here:
- The test's behavioral axis is exactly which command is used and where its parameters are sourced (host inline vs. device buffer).
- The indirect2 path is the only one where SBT addresses/sizes/strides are device-visible data rather than host-supplied command parameters, so it exercises device-side SBT parameter resolution.

### CPU-sourced versus GPU-sourced indirect parameters

For the indirect and indirect2 variants, the parameter buffer can be filled two ways:

- CPU-sourced: the host `deMemcpy`s the parameter struct into a host-visible indirect buffer and flushes. The device only reads it.
- GPU-sourced: the host writes the parameter values into a uniform buffer, then runs a compute shader (`compute_indirect_command`) that copies them into the indirect buffer (which is a storage buffer with a shader device address). A buffer memory barrier transitions the indirect buffer from `SHADER_WRITE` to `INDIRECT_COMMAND_READ` before the trace command.

Why it matters here:
- The GPU-sourced path adds a compute dispatch and a synchronization barrier into the command stream before the trace. It exercises whether the indirect command reads parameters that a prior compute shader wrote, with the correct availability/visibility.
- The GPU-sourced compute shader is also where maintenance1 / indirect2 SBT fields are copied field-by-field from the uniform buffer, which is relevant to the partial-copy variation.

### Null-dimension (zero-extent) dispatch

The dimension matrix includes `{0,0,0}` and single-zero cases like `{0,1,1}`, `{1,0,1}`, `{1,1,0}`. A zero in any dimension means no raygen invocations occur (a null trace). The test still allocates an 8x8x1 fallback image, clears it, and expects every pixel to remain at the clear value because no shader writes occurred. This checks that a zero-extent dispatch is a legal no-op rather than a crash or undefined write.

## One Concrete Example

Representative case: `dEQP-VK.ray_tracing_pipeline.trace_rays_cmds.indirect_cpu.8_8_8`.

The host builds a 3D chessboard of bottom-level acceleration structures (BLAS) over the 8x8x8 launch volume: a BLAS with a two-triangle quad exists at every `(x,y,z)` where `(x+y+z)` is odd; even cells have no geometry. A top-level AS (TLAS) instances those BLAS. The rgen shader shoots a ray straight down (`-z`) from `(x+0.5, y+0.5, z+0.5)`. Odd cells hit their quad and the closest-hit shader writes `kHitColorValue` (2); even cells miss and the miss shader writes `kMissColorValue` (1).

For this `indirect_cpu` leaf, the host writes `{width=8, height=8, depth=8}` into a host-visible indirect buffer (a `VkTraceRaysIndirectCommandKHR`), flushes it, then records `vkCmdTraceRaysIndirectKHR` with the SBT regions passed inline and the indirect buffer's device address. After submit, the host copies the r32ui 3D image to a host-visible buffer and checks each voxel: odd `(x+y+z)` must be 2, even must be 1.

The same scene and same 8_8_8 dimensions are exercised by the `direct` and `indirect_gpu` leaves of `trace_rays_cmds`, and (via the extended struct) by the `trace_rays_cmds_maintenance_1` leaves. All must produce the identical chessboard result.

## End-to-End Test Flow

Two flow shapes exist, one per test class. They share the chessboard scene and the result-checking logic.

```text
[host] choose traceType (DIRECT/INDIRECT_CPU/INDIRECT_GPU/INDIRECT2_CPU/INDIRECT2_GPU) and dimensions
[host] build chessboard BLAS grid + TLAS over the launch volume
[host] create r32ui 3D result image, clear to kClearColorValue (0xFF)
[host] build ray tracing pipeline: rgen (group 0), chit (group 1), miss (group 2); build 3 SBT regions
[host] (INDIRECT2 only) fill VkTraceRaysIndirectCommand2KHR SBT fields from the SBT region addresses
[host] (CPU-sourced) memcpy parameter struct into host-visible indirect buffer, flush
[host] (GPU-sourced) write params into UBO, record compute dispatch that copies UBO -> indirect storage buffer
[device] (GPU-sourced) compute shader writes indirect buffer
[host/device] barrier: indirect buffer SHADER_WRITE -> INDIRECT_COMMAND_READ
[device] record the matching vkCmdTraceRays* command (direct / indirect / indirect2)
[device] rgen traces rays; chit writes 2 on hit, miss writes 1 on miss; imageStore into 3D image
[host] barrier + cmdCopyImageToBuffer to host-visible result buffer
[host] scan every voxel: expect 2 for odd (x+y+z), 1 for even, or 0xFF clear for null dimensions
[host] pass if failures == 0
```

The `trace_rays_indirect2` flow adds two extra dimensions: a partial-copy style (the compute shader copies only some SBT fields, the rest are pre-filled by the host) and a submit-queue choice (graphics or compute queue family). Its `makeIndirectStructAndFlush` splits the full `VkTraceRaysIndirectCommand2KHR` across the uniform buffer and the indirect buffer for the partial-copy GPU case, so the compute shader assembles only part of the struct and the host pre-writes the rest.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- Inline GLSL rgen shader: traces one ray per launch ID straight down, stores the payload into a `uimage3D` at `gl_LaunchIDEXT`.
- Inline GLSL chit shader: writes `uvec4(kHitColorValue,0,0,1)` (2) into the ray payload.
- Inline GLSL miss shader: writes `uvec4(kMissColorValue,0,0,1)` (1) into the ray payload.
- Inline GLSL compute shader `compute_indirect_command`: only generated for GPU-sourced variants. Copies the parameter struct from a uniform buffer into a storage buffer. For `trace_rays_cmds_maintenance_1` and `trace_rays_indirect2` it also copies the extended SBT fields. The `trace_rays_indirect2` version adds a `push_constant uint full` that selects full-copy (copy all 12 SBT fields) versus partial-copy (copy only a subset, leaving the rest host-pre-filled).
- All shaders built with `vk::SPIRV_VERSION_1_4`.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| 3D r32ui result image | yes | yes (storage image, binding 0) | written by rgen via `imageStore` | yes, copied to buffer | Carries the hit/miss result per voxel |
| TLAS + chessboard BLAS grid | yes | yes (acceleration structure, binding 1) | read by rgen `traceRayEXT` | no | Provides the hit/miss geometry pattern |
| rgen/hit/miss SBT regions | yes | yes (device addresses) | read by the trace command | no | Selects the shaders; indirect2 reads these from the parameter struct on the device |
| indirect buffer | yes | yes (indirect + shader device address; storage for GPU-sourced) | read by trace command; written by compute for GPU-sourced | no (host-visible for CPU-sourced) | Holds `VkTraceRaysIndirectCommand[KH]R` / `Command2KHR` consumed by the trace |
| uniform buffer (GPU-sourced only) | yes | yes (UBO, binding 0 of compute set) | read by compute shader | no | Source of parameter values the compute shader copies into the indirect buffer |
| host-visible result buffer | yes | yes (transfer dst) | written by `cmdCopyImageToBuffer` | yes | Host scans this for pass/fail |
| compute pipeline + descriptor set (GPU-sourced only) | yes | yes | runs the copy shader | no | Bridges host params to the device-readable indirect buffer |

## What Is Checked

- Every voxel of the 3D result image is compared on the host against an expected value derived from `(x + y + z) % 2`: odd cells expect `kHitColorValue` (2), even cells expect `kMissColorValue` (1).
- For null-dimension cases (any of width/height/depth is 0), the image is the 8x8x1 fallback cleared to `kClearColorValue` (0xFF), and every voxel must remain 0xFF because no raygen ran.
- The check is a per-voxel equality comparison; the test fails with a `failures` count if any voxel mismatches.
- For `trace_rays_indirect2`, the pass message also reports the BLAS allocation count (`N allocations`), confirming the batched acceleration structure pool path.
- Each leaf is checked independently; results are not aggregated across leaves.

## Behavior Parameter Identification

> **Behavior parameter:** `traceType` (the dispatch command variant and parameter source), realized as the test family plus its direct child nodes
>
> **Candidate values:** `direct`, `indirect_cpu`, `indirect_gpu` (in `trace_rays_cmds`); `indirect2_cpu`, `indirect2_gpu` (in `trace_rays_cmds_maintenance_1`); and the `trace_rays_indirect2` family which cross-multiplies `indirect_cpu`/`indirect_gpu` with `full_copy`/`partial_copy` and `submit_graphics`/`submit_compute`.

The primary behavioral axis is which `vkCmdTraceRays*` command is used and where its parameters are sourced (host inline, CPU-filled device buffer, or GPU-filled device buffer). The `trace_rays_indirect2` family adds two secondary axes (copy style and submit queue) that are part of the same dispatch-path theme.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `direct` | The direct `vkCmdTraceRaysKHR` dispatch with host-supplied SBT regions and dimensions did not produce the expected hit/miss chessboard; points at SBT region setup, pipeline binding, or the rgen/chit/miss shader path itself. |
| `indirect_cpu` | `vkCmdTraceRaysIndirectKHR` did not read the host-written `VkTraceRaysIndirectCommandKHR` dimensions correctly, or the host flush of the indirect buffer was incomplete. |
| `indirect_gpu` | The compute shader that fills the indirect buffer did not write the dimensions, or the `SHADER_WRITE` -> `INDIRECT_COMMAND_READ` barrier did not make the write available/visible to the trace command. |
| `indirect2_cpu` | `vkCmdTraceRaysIndirect2KHR` did not correctly resolve the SBT regions and dimensions from the host-written `VkTraceRaysIndirectCommand2KHR`, or the extended struct fields were laid out / flushed incorrectly. |
| `indirect2_gpu` | The compute shader did not copy the extended SBT fields into the indirect storage buffer, or the barrier before the indirect2 trace did not cover the full struct, or device-side SBT address resolution from the struct failed. |
| `trace_rays_indirect2` partial_copy | The split source (host pre-fills some fields, compute copies others) produced an incomplete or inconsistent `VkTraceRaysIndirectCommand2KHR`, so device-side SBT resolution used wrong fields. |
| `trace_rays_indirect2` submit_graphics / submit_compute | The indirect2 trace on a non-default queue family (graphics or compute) did not execute or did not synchronize correctly, or the requested queue family was not selected properly. |

All leaves share the chessboard scene and the per-voxel equality check, so a failure common to all variants of one family points at shared infrastructure (AS build, SBT construction, image copyback) rather than the dispatch-specific path.

## Important Variations and Special Cases

- **Null-dimension dispatch.** The dimension matrix includes `{0,0,0}` and the three single-zero permutations. These expect the clear value everywhere. They are present in both `trace_rays_cmds` and `trace_rays_cmds_maintenance_1`. This does not change the core model; it adds a "zero launch is a legal no-op" check.
- **Maintenance1 extended struct.** The `trace_rays_cmds_maintenance_1` family uses `VkTraceRaysIndirectCommand2KHR` and `vkCmdTraceRaysIndirect2KHR` but keeps the same chessboard scene and dimension matrix as `trace_rays_cmds`. The difference is purely that SBT regions are sourced on the device rather than passed inline.
- **Partial-copy style.** Only in `trace_rays_indirect2`. The compute shader copies only a subset of the 12 SBT fields (driven by the `full` push constant); the host pre-fills the rest via `makeIndirectStructAndFlush` with `source=false`. This stresses that `vkCmdTraceRaysIndirect2KHR` reads each field from wherever it ends up in the unified struct, regardless of who wrote it.
- **Submit-queue axis.** Only in `trace_rays_indirect2`. The trace is submitted to either a graphics or compute queue family selected by `getQueueFamilyIndexAtExact`. `checkSupport` throws `NotSupportedError` if the exact queue family is absent. This adds a queue-selection requirement on top of the dispatch path.
- **Batched BLAS pool.** `trace_rays_indirect2` uses `BottomLevelAccelerationStructurePool` with batched create/build and reports the allocation count in the pass message. This is a resource-construction variation, not a dispatch-behavior variation.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| `TraceType` enum | [vktRayTracingTraceRaysTests.cpp#L60-L67](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L60-L67) | Defines the five dispatch variants |
| `TestParams` / `TestParams2` | [vktRayTracingTraceRaysTests.cpp#L69-L82](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L69-L82) | Parameter structs for the two test classes |
| rgen / chit / miss shaders | [vktRayTracingTraceRaysTests.cpp#L364-L414](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L364-L414) | The chessboard ray-tracing shaders |
| compute_indirect_command (maintenance1) | [vktRayTracingTraceRaysTests.cpp#L298-L361](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L298-L361) | GPU-sourced struct copy shader with extended fields |
| compute_indirect_command (indirect2) | [vktRayTracingTraceRaysTests.cpp#L934-L997](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L934-L997) | GPU-sourced struct copy with full/partial push constant |
| checkSupport (cmds + maintenance1) | [vktRayTracingTraceRaysTests.cpp#L254-L293](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L254-L293) | Feature gates for indirect and indirect2 |
| checkSupport (indirect2) | [vktRayTracingTraceRaysTests.cpp#L898-L929](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L898-L929) | Maintenance1 + indirect2 + queue family support |
| dispatch command selection | [vktRayTracingTraceRaysTests.cpp#L776-L791](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L776-L791) | Picks `cmdTraceRays` / `cmdTraceRaysIndirect` / `cmdTraceRaysIndirect2KHR` by `traceType` |
| per-voxel result check | [vktRayTracingTraceRaysTests.cpp#L827-L842](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L827-L842) | Expected-value rule and failures counter |
| indirect2 partial-copy struct split | [vktRayTracingTraceRaysTests.cpp#L1060-L1121](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L1060-L1121) | `makeIndirectStructAndFlush` full vs partial field split |
| indirect2 queue selection | [vktRayTracingTraceRaysTests.cpp#L146-L179](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L146-L179) | `getQueueFamilyIndexAtExact` for graphics/compute queue |
| registration: trace_rays_cmds | [vktRayTracingTraceRaysTests.cpp#L1459-L1502](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L1459-L1502) | `createTraceRaysTests` |
| registration: trace_rays_cmds_maintenance_1 | [vktRayTracingTraceRaysTests.cpp#L1504-L1549](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L1504-L1549) | `createTraceRaysMaintenance1Tests` |
| registration: trace_rays_indirect2 | [vktRayTracingTraceRaysTests.cpp#L1551-L1593](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L1551-L1593) | `createTraceRays2Tests` |

## Questions / Risk Points for User Audit

- Is the core test purpose (every `vkCmdTraceRays*` variant must produce the same chessboard) clear?
- Is the distinction between CPU-sourced (host memcpy + flush) and GPU-sourced (compute shader + barrier) indirect parameters understandable?
- Is the indirect2 partial-copy split (host pre-fills some SBT fields, compute copies the rest) explained at the right depth?
- Are the null-dimension cases correctly characterized as "legal no-op, expect clear value everywhere"?
- Is the submit-queue axis (graphics vs compute) scoped to `trace_rays_indirect2` only?

All audit questions above are resolved by inspected source and mustpass evidence, so this brief proceeds directly to the Level-3 rewrite.

## Conversion Notes for Final Wiki Rewrite

- The brief's `### Failure Cause Mapping` table should be copied directly into the final page's `## Failure Meaning` -> `### Failure Cause Mapping`.
- The behavior-parameter axis (`traceType` realized as test family + child nodes) carries into `## Behavior Parameters`; the three test families become the subsection grouping, with the `trace_rays_indirect2` secondary axes (copy style, submit queue) noted as additional dimensions in `## Parameter Dimensions and Observed Values`.
- The brief's beginner-friendly `Background Knowledge` should be distilled into a short prerequisite list (dispatch variants, CPU/GPU sourcing, null dimensions), not copied verbatim.
- The concrete example (`indirect_cpu.8_8_8`) is a good candidate for the representative shader walkthrough since the rgen/chit/miss shaders are identical across all variants; the dispatch command differs only on the host side.
- Source-mapping table becomes the focused source appendix.
- The `### Cause Analysis` is written fresh during the rewrite, not carried from this brief.
