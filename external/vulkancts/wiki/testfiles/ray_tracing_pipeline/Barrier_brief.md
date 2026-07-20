# Understanding Brief: ray_tracing_pipeline.barrier

## One-Sentence Test Purpose

This test checks whether a `vkCmdPipelineBarrier` correctly synchronizes a writer stage and a reader stage when at least one of them is a ray tracing shader stage, across the three resource types `UNIFORM_BUFFER`, `STORAGE_BUFFER`, and `STORAGE_IMAGE`, and across the two barrier shapes `vkMemoryBarrier` and `vkBufferMemoryBarrier`/`vkImageMemoryBarrier`.

## Background Knowledge

### Pipeline barriers and execution/access dependencies

A `vkCmdPipelineBarrier` establishes two ordered dependencies on a command buffer: an execution dependency from a set of source pipeline stages to a set of destination pipeline stages, and a memory dependency from a set of source access flags to a set of destination access flags. The execution dependency guarantees that all source-stage work submitted before the barrier completes execution before any destination-stage work after the barrier begins. The memory dependency adds an availability operation that flushes source-stage writes from caches to device memory and an visibility operation that makes those writes visible to destination-stage reads. Without the memory dependency, the destination stage could observe stale or partial data even if execution ordering holds.

Two barrier shapes are exercised:

- `vkMemoryBarrier` (`BarrierType::GENERAL`): a global memory barrier that applies to all memory in the device. The test uses it without any buffer or image handle, so it flushes and makes visible every prior write that matches the source access mask.
- `vkBufferMemoryBarrier` and `vkImageMemoryBarrier` (`BarrierType::SPECIFIC`): a barrier scoped to a specific buffer or image subresource range. The test uses it for `UNIFORM_BUFFER`/`STORAGE_BUFFER` (buffer barrier) and for `STORAGE_IMAGE` (image barrier that also performs a layout transition).

Why it matters here:

- Ray tracing shader stages are represented by the single `VK_PIPELINE_STAGE_RAY_TRACING_SHADER_BIT_KHR` pipeline stage flag, regardless of which ray tracing shader stage (raygen, intersection, any-hit, closest-hit, miss, callable) is the actual writer or reader. The test's `getPipelineStage` helper collapses all six stages to this one bit, so the host barrier always names the same source or destination stage for any ray tracing case.
- `VK_ACCESS_SHADER_WRITE_BIT` is the writer access flag for every shader writer stage, including ray tracing stages, compute, and fragment. `VK_ACCESS_UNIFORM_READ_BIT` is used for UBO reads and `VK_ACCESS_SHADER_READ_BIT` for SSBO and storage image reads. `VK_ACCESS_TRANSFER_WRITE_BIT`/`VK_ACCESS_TRANSFER_READ_BIT` and `VK_ACCESS_HOST_WRITE_BIT`/`VK_ACCESS_HOST_READ_BIT` cover the non-shader paths.
- For `STORAGE_IMAGE`, the SPECIFIC barrier also transitions the image layout. The writer leaves the image in `VK_IMAGE_LAYOUT_GENERAL`; the reader expects `VK_IMAGE_LAYOUT_GENERAL` for shader reads or `VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL` for transfer reads. The image-memory barrier's `oldLayout`/`newLayout` pair performs that transition atomically with the availability/visibility operation.

### Ray tracing pipeline stage and acceleration structure dependency

Any case whose writer or reader is a ray tracing shader stage builds a top-level acceleration structure (TLAS) wrapping a single bottom-level acceleration structure (BLAS) and binds it at descriptor set 0, binding 1. The TLAS/BLAS pair is created and built on the same command buffer before `cmdTraceRaysKHR` is recorded. There is no explicit barrier between the AS build and the trace in this test; the implementation's AS build is serialized by `vkCmdBuildAccelerationStructuresKHR` ordering rules.

### Reader-side verification buffer

Every case uses a separate host-visible `verificationBuffer` (std430, `kBufferElements` uint32_t values). The reader stage writes the value it read from the barrier resource into `verificationBuffer.data[id1d]`. The host then scans the buffer and checks each entry equals `kValuesOffset + i`. This indirection lets the same host check cover every reader stage uniformly, including ray tracing, compute, fragment, transfer, and host.

## One Concrete Example

Concrete case: `ray_tracing_pipeline.barrier.ssbo.specific_barrier.from_rgen_to_chit`.

```text
[host] create std140 SSBO (kBufferElements=1024 uint32_t slots, padded as UVec4)
[host] create verificationBuffer (std430, 1024 uint32_t slots, host-visible)
[host] build TLAS wrapping a default BLAS, bind at set 0 binding 1 for both writer and reader pipelines
[host] record: raygen writer pipeline traces a 32x32 launch; the rgen shader writes
       ssbo.data[id1d] = id1d + 2048
[host] record: vkCmdPipelineBarrier(SRC=RAY_TRACING_SHADER_BIT, DST=RAY_TRACING_SHADER_BIT,
       SRC_ACCESS=SHADER_WRITE, DST_ACCESS=SHADER_READ, vkBufferMemoryBarrier on the SSBO)
[host] record: raygen+closest-hit reader pipeline traces a 32x32 launch; the rgen fires a ray
       that hits the BLAS, the closest-hit shader reads ssbo.data[id1d] and writes
       verificationBuffer.data[id1d] = read_value
[host] record: vkCmdPipelineBarrier(SRC=RAY_TRACING_SHADER_BIT, DST=HOST_BIT,
       SRC_ACCESS=SHADER_WRITE, DST_ACCESS=HOST_READ, vkBufferMemoryBarrier on verificationBuffer)
[host] submit and wait; invalidate verificationBuffer; for each i, assert
       verificationBuffer[i] == 2048 + i
```

The rgen writer and rgen reader shaders are independent pipelines with their own SBTs. The closest-hit reader shader runs because the rgen fires a downward ray into the default BLAS that `makeBottomLevelAccelerationStructure()` provides. The SSBO is the only state that crosses the two pipelines.

## End-to-End Test Flow

```text
[host] choose (resourceType, barrierType, writerStage, readerStage) from the registration loop,
       skipping combinations that do not involve any ray tracing stage, that would require
       host access to a storage image, or that would require a shader write to a UBO
[host] create the barrier resource:
       - UBO/SSBO: std140 buffer of kBufferElements UVec4 slots
       - STORAGE_IMAGE: 32x32 R32_UINT image
[host] create verificationBuffer (std430, host-visible)
[host] if either stage is a ray tracing stage, build a default BLAS and a one-instance TLAS
       inside the same command buffer
[host] record the writer:
       - HOST: fill the buffer directly and flush
       - TRANSFER: fill a staging buffer and cmdCopyBuffer / cmdCopyBufferToImage
       - RAYGEN/INTERSECT/ANY_HIT/CLOSEST_HIT/MISS/CALLABLE: build a ray tracing pipeline
         with the writer shader in the relevant stage, bind SBT, cmdTraceRaysKHR 32x32x1
       - COMPUTE: cmdDispatch 32x32x1
       - FRAGMENT: draw a full-screen quad
[host] record the main barrier:
       - GENERAL: vkMemoryBarrier(writerAccess, readerAccess)
       - SPECIFIC: vkBufferMemoryBarrier or vkImageMemoryBarrier on the resource, with
         oldLayout -> newLayout transition for the image case
       - source stage = getPipelineStage(writerStage)
       - dest stage = getPipelineStage(readerStage)
[host] record the reader:
       - HOST: handled after submit; invalidate the resource buffer and copy UVec4.x to uint32_t
       - TRANSFER: cmdCopyBuffer (with per-element regions for std140 -> std430) or
         cmdCopyImageToBuffer
       - RAYGEN/INTERSECT/ANY_HIT/CLOSEST_HIT/MISS/CALLABLE: build a second ray tracing
         pipeline with the reader shader, bind SBT, cmdTraceRaysKHR 32x32x1; the reader
         shader reads the resource and writes verificationBuffer
       - COMPUTE: cmdDispatch 32x32x1
       - FRAGMENT: draw a full-screen quad
[host] record the verification barrier (vkBufferMemoryBarrier on verificationBuffer,
       reader stage -> HOST, SHADER_WRITE/TRANSFER_WRITE -> HOST_READ)
[host] endCommandBuffer; submitCommandsAndWait
[host] invalidate verificationBuffer; for each i in [0, 1024):
       assert verificationBuffer[i] == kValuesOffset + i, else fail with the index and the
       mismatched values
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- Inline GLSL strings emitted by `BarrierTestCase::initPrograms`. Each case generates a writer shader and a reader shader. The shader body depends on the stage and resource type.
- For ray tracing writer or reader stages other than RAYGEN, an additional `writer_aux_rgen` or `reader_aux_rgen` is generated from the shared helper `getCommonRayGenerationShader()`. That helper fires one downward ray per launch invocation against the bound TLAS.
- For the CALLABLE stage, the aux rgen is generated inline (not the shared helper) and calls `executeCallableEXT(0, 0)`.
- For the FRAGMENT stage, an auxiliary vertex shader draws a full-screen quad.
- Build options: `SPIRV_VERSION_1_4` with `vulkanVersion` from the program collection, so the SPIR-V target environment is Vulkan 1.2 with SPIR-V 1.4.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Barrier resource: `UNIFORM_BUFFER` (`ubo`) | yes, std140, host-visible if writer or reader is HOST | yes, binding 0 | read by reader shader (UNIFORM_READ) | only if reader is HOST | The UBO is the resource that the writer produces and the reader consumes; UBOs cannot be written from shaders, so writer is restricted to HOST or TRANSFER. |
| Barrier resource: `STORAGE_BUFFER` (`ssbo`) | yes, std140, host-visible if writer or reader is HOST | yes, binding 0 | written by writer shader (SHADER_WRITE), read by reader shader (SHADER_READ) | only if reader is HOST | The SSBO is the most flexible resource: it allows every writer/reader stage combination including HOST. |
| Barrier resource: `STORAGE_IMAGE` (`simg`) | yes, 32x32 R32_UINT | yes, binding 0 via `VkImageView` | written by writer shader (SHADER_WRITE) or TRANSFER, read by reader shader (SHADER_READ) or TRANSFER | never (no HOST reader) | The image is the only resource that exercises image-memory barriers and layout transitions. HOST writer/reader is forbidden because the image is not host-visible. |
| `verificationBuffer` (std430 storage buffer) | yes, host-visible | yes, binding 2 if AS is bound else binding 1 | written by reader shader (SHADER_WRITE) or TRANSFER | yes, host reads after invalidation | The verification buffer is the readback channel for every reader stage. Every reader shader writes the value it observed into this buffer at `id1d`. |
| Top-level acceleration structure | yes, built on device | yes, binding 1 for ray tracing stages | read by `OpTraceRayKHR` | no | Needed for every ray tracing writer or reader stage. Wraps a single default BLAS. |
| Bottom-level acceleration structure | yes, built on device | yes, referenced by TLAS | read by traversal | no | The default BLAS provided by `makeBottomLevelAccelerationStructure()`; the aux rgen traces one downward ray per pixel that hits it. |
| Staging buffer (std140 or std430) | yes, host-visible | yes (TRANSFER_SRC) | no | yes (host fills and flushes) | Used only for TRANSFER writer to copy data into the barrier resource. |
| Vertex buffer (full-screen quad) | yes, host-visible | yes (VERTEX_BUFFER) | read by vertex shader | no | Used only for FRAGMENT writer or reader to drive the full-screen quad draw. |

## What Is Checked

- The host checks `verificationBuffer[i] == kValuesOffset + i` for every `i` in `[0, kBufferElements)` after the command buffer completes.
- The check is a host-side linear scan. The first mismatch fails the case with a message `"Unexpected value found at position <i>: found <value> and expected <expected>"`.
- The check is exact: there is no tolerance, no mask, and no aggregation across cases.
- The check catches both stale data (the writer's writes were not flushed or not made visible to the reader, so the reader observed zeros or pre-fill values) and corrupted data (the reader observed a partial write because the barrier did not enforce execution ordering).
- For STORAGE_IMAGE cases, the check additionally catches layout-transition mistakes: if the image was not in the layout the reader expects, the read returns undefined data and the verification fails.

## Behavior Parameter Identification

> **Behavior parameter:** `resourceType` (the direct child of `ray_tracing_pipeline.barrier`)
>
> **Candidate values:** `ubo`, `ssbo`, `simg`

The direct child of the test family is the resource type. It is the primary behavioral axis because it changes what is being tested in three ways simultaneously:

1. The descriptor type (`UNIFORM_BUFFER`, `STORAGE_BUFFER`, `STORAGE_IMAGE`) changes, which changes the reader access flag (`UNIFORM_READ` vs `SHADER_READ`) and the writer access flag possibilities.
2. The barrier shape for SPECIFIC changes: buffer-memory barrier for `ubo` and `ssbo`, image-memory barrier (with layout transition) for `simg`.
3. The set of legal writer/reader stage combinations changes: `ubo` forbids shader writers; `simg` forbids host writer/reader; `ssbo` allows every combination.

A secondary axis is `barrierType` (`memory_barrier` vs `specific_barrier`), which is the intermediate node below each resource type. It does not change the writer, reader, or resource, only the barrier shape used between them. It is documented in `## Parameter Dimensions and Observed Values` and `## Behavior Parameters` but is not the primary axis because it does not change the resource semantics.

The third axis is the writer/reader stage pair, encoded in the test case leaf name `from_<writer>_to_<reader>`. It is the leaf generator and is covered in `## Parameter Dimensions and Observed Values`.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `ubo` | HOST or TRANSFER writer data was not made visible to the ray tracing (or other shader) reader stage; or the buffer-memory barrier used the wrong source/destination access mask; or the UBO read used `SHADER_READ` semantics where `UNIFORM_READ` was required; or the host fill did not flush before the barrier. |
| `ssbo` | Writer shader writes were not flushed (availability) or not made visible to the reader stage; or the buffer-memory barrier named the wrong pipeline stage; or for HOST reader, the host-read barrier was missing or used the wrong access mask; or for ray tracing reader, the closest-hit/any-hit/intersection shader did not run because the TLAS/BLAS setup was wrong (the read observed zeros). |
| `simg` | Image layout transition between writer and reader was wrong or missing; or the image-memory barrier's `oldLayout`/`newLayout` pair did not match the actual writer-final layout; or the writer's `imageStore` was not made visible to the reader's `imageLoad`; or for TRANSFER reader, the image was not transitioned to `TRANSFER_SRC_OPTIMAL`; or for TRANSFER writer, the image was not transitioned to `TRANSFER_DST_OPTIMAL` or `GENERAL` before the copy. |

All three resource types share the same verification path (verificationBuffer -> host scan), so a shared infrastructure failure (verificationBuffer missing its host-read barrier, host invalidation skipped, wrong element count) would surface identically across resource types and is distinguishable from a resource-type-specific failure by whether the mismatch appears in one resource type or all three.

## Important Variations and Special Cases

- **`ubo` writer restriction.** The registration loop skips every UBO case whose writer is not HOST or TRANSFER because Vulkan does not allow shader writes to a `UNIFORM_BUFFER`. This is enforced by `if (resourceType == VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER && writerStage != Stage::HOST && writerStage != Stage::TRANSFER) continue;`. The remaining UBO cases pair a HOST or TRANSFER writer with a ray tracing reader (the only readers that satisfy the "at least one ray tracing stage" rule and are legal for a uniform buffer).
- **`simg` host restriction.** The registration loop skips every storage-image case whose writer or reader is HOST because the image is allocated with `MemoryRequirement::Any` (not host-visible) and there is no host readback path for images. This is enforced by `if (resourceType == VK_DESCRIPTOR_TYPE_STORAGE_IMAGE && (writerStage == Stage::HOST || readerStage == Stage::HOST)) continue;`.
- **`simg` layout transition.** For SPECIFIC barriers, the image-memory barrier transitions the image from its writer-final layout to `getOptimalReadLayout(readerStage)`. For shader readers this is `GENERAL`; for TRANSFER reader this is `TRANSFER_SRC_OPTIMAL`. For TRANSFER writer the writer-final layout depends on barrier type: `TRANSFER_DST_OPTIMAL` for SPECIFIC, `GENERAL` for GENERAL.
- **Callable stage uses a custom aux rgen.** Unlike the other ray tracing stages, the CALLABLE writer and reader generate their own aux rgen that calls `executeCallableEXT(0, 0)`. The shared helper is not used because it would not invoke the callable shader.
- **`Stage::CALLABLE` requires an acceleration structure.** The host's `needsAccelerationStructure` helper returns true for every ray tracing stage including CALLABLE, even though callable shaders do not trace rays. The TLAS/BLAS is built and bound for every ray tracing case for uniformity.
- **Fragment writer requires `fragmentStoresAndAtomics`.** The `checkSupport` method throws `NotSupportedError` if the feature is missing when the writer is FRAGMENT. This is the only feature-gated path in this test family.
- **Reader verification buffer binding.** When the reader is a ray tracing stage, the verification buffer is bound at binding 2 (binding 1 is reserved for the TLAS). When the reader is COMPUTE or FRAGMENT, it is bound at binding 1.
- **std140 to std430 conversion.** The barrier resource is std140 (one uint32_t per UVec4 slot). The verification buffer is std430 (compact uint32_t array). The TRANSFER reader performs per-element `VkBufferCopy` regions to skip the std140 padding. The HOST reader performs the conversion on the host after invalidating the resource buffer.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| `TestParams` struct and constraints | [vktRayTracingBarrierTests.cpp#L325-L342](../../../modules/vulkan/ray_tracing/vktRayTracingBarrierTests.cpp#L325-L342) | Defines the four test parameters: resource type, writer stage, reader stage, barrier type. |
| `getPipelineStage` stage mapping | [vktRayTracingBarrierTests.cpp#L113-L145](../../../modules/vulkan/ray_tracing/vktRayTracingBarrierTests.cpp#L113-L145) | Collapses every ray tracing stage to `VK_PIPELINE_STAGE_RAY_TRACING_SHADER_BIT_KHR`. |
| `getWriterAccessFlag` / `getReaderAccessFlag` | [vktRayTracingBarrierTests.cpp#L147-L206](../../../modules/vulkan/ray_tracing/vktRayTracingBarrierTests.cpp#L147-L206) | Maps each stage to its write/read access flag; UBO reads use `UNIFORM_READ`. |
| `initPrograms` writer shader generation | [vktRayTracingBarrierTests.cpp#L410-L620](../../../modules/vulkan/ray_tracing/vktRayTracingBarrierTests.cpp#L410-L620) | Generates the writer shader per stage and resource type. |
| `initPrograms` reader shader generation | [vktRayTracingBarrierTests.cpp#L622-L764](../../../modules/vulkan/ray_tracing/vktRayTracingBarrierTests.cpp#L622-L764) | Generates the reader shader per stage and resource type, including the verification buffer write. |
| `checkSupport` feature gates | [vktRayTracingBarrierTests.cpp#L771-L794](../../../modules/vulkan/ray_tracing/vktRayTracingBarrierTests.cpp#L771-L794) | Requires `VK_KHR_acceleration_structure`, `VK_KHR_ray_tracing_pipeline`, and `fragmentStoresAndAtomics` (FRAGMENT writer only). |
| `iterate` resource creation and writer recording | [vktRayTracingBarrierTests.cpp#L1264-L1545](../../../modules/vulkan/ray_tracing/vktRayTracingBarrierTests.cpp#L1264-L1545) | Builds the resource, AS, writer pipeline, and records writer commands. |
| Main barrier recording | [vktRayTracingBarrierTests.cpp#L1547-L1592](../../../modules/vulkan/ray_tracing/vktRayTracingBarrierTests.cpp#L1547-L1592) | Records the GENERAL or SPECIFIC barrier between writer and reader stages. |
| Reader recording and verification barrier | [vktRayTracingBarrierTests.cpp#L1594-L1694](../../../modules/vulkan/ray_tracing/vktRayTracingBarrierTests.cpp#L1594-L1694) | Records the reader commands and the verification-buffer host-read barrier. |
| Host verification scan | [vktRayTracingBarrierTests.cpp#L1723-L1745](../../../modules/vulkan/ray_tracing/vktRayTracingBarrierTests.cpp#L1723-L1745) | Linear scan of `verificationBuffer` with exact expected value. |
| Registration loop and pruning rules | [vktRayTracingBarrierTests.cpp#L1750-L1826](../../../modules/vulkan/ray_tracing/vktRayTracingBarrierTests.cpp#L1750-L1826) | Builds the three resource-type groups, two barrier-type groups, and applies the three skip rules. |
| Shared aux raygen helper | [vkRayTracingUtil.cpp#L118-L138](../../../framework/vulkan/vkRayTracingUtil.cpp#L118-L138) | `getCommonRayGenerationShader()` emits the aux rgen used by every non-raygen ray tracing writer/reader. |

## Questions / Risk Points for User Audit

- Is the resource-type-first behavioral axis the right choice, or should the page split by barrier type first? The registration loop nests barrier type inside resource type, so resource-type-first matches the registered tree.
- Is the per-stage shader write/access flag mapping correctly summarized? The page distills it into a table and points to the helper functions rather than restating every case.
- Is the std140-to-std430 conversion (TRANSFER reader per-element copy, HOST reader host-side transform) worth a dedicated callout in the final page, or is a brief mention in the runtime section enough?
- Is the layout transition for `simg` SPECIFIC barriers correctly described? The writer-final layout is `GENERAL` for shader writers and `TRANSFER_DST_OPTIMAL` (SPECIFIC) or `GENERAL` (GENERAL) for TRANSFER writer; the reader layout is `GENERAL` for shader readers and `TRANSFER_SRC_OPTIMAL` for TRANSFER reader.
- The page should pick a representative walkthrough case that exercises a ray tracing writer and a ray tracing reader over an SSBO with a SPECIFIC barrier, because that combination touches the most test machinery (TLAS/BLAS, ray tracing pipeline, SBT, buffer-memory barrier, verification buffer). `from_rgen_to_chit` is a good candidate: it uses two ray tracing pipelines (writer rgen, reader rgen+chit), the SSBO resource, and the SPECIFIC buffer barrier.

## Conversion Notes for Final Wiki Rewrite

- The final `## Background Knowledge` should be a short unordered list covering: pipeline barrier execution/access dependencies; the `vkMemoryBarrier` vs `vkBufferMemoryBarrier`/`vkImageMemoryBarrier` distinction; the single `VK_PIPELINE_STAGE_RAY_TRACING_SHADER_BIT_KHR` stage for all ray tracing sub-stages; the `UNIFORM_READ` vs `SHADER_READ` distinction for UBO vs SSBO reads; the layout transition role of image-memory barriers; the verification buffer readback pattern.
- The `### Failure Cause Mapping` table above should be copied directly into the final page's `### Failure Cause Mapping`.
- The concrete example (`from_rgen_to_chit` over SSBO with SPECIFIC barrier) should become the representative shader walkthrough. The reconstructed GLSL should be the writer rgen shader because it is the simplest shader that exercises the writer side; the reader chit shader is structurally similar and a brief note can describe its differences.
- The per-stage access flag and pipeline stage mappings should be summarized in a compact table in `## Parameter Dimensions and Observed Values` or `## Background Knowledge` rather than re-narrated.
- The host-flow detail (writer recording, main barrier, reader recording, verification barrier, host scan) belongs in `## Runtime Execution and Result Checking`.
- The pruning rules (no RT skip, no HOST image skip, no shader-write-UBO skip, `fragmentStoresAndAtomics` gate) belong in `## Case Pruning`.
- The brief's `## Important Variations and Special Cases` should be folded into `## Behavior Parameters` and `## Case Pruning` rather than kept as a separate section.
