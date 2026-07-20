# Understanding Brief: ray_tracing_pipeline.capture_replay

## One-Sentence Test Purpose

This test checks whether the implementation correctly captures opaque device addresses for shader binding table (SBT) buffers and acceleration structures (AS) during a first run, then replays those exact addresses during a second run, producing identical ray tracing results across the two phases.

## Background Knowledge

### Opaque capture/replay addresses

Vulkan lets an application query three kinds of opaque addresses that can be saved and later replayed:

- `vkGetBufferOpaqueCaptureAddress` returns an opaque address for a `VkBuffer` created with `VK_BUFFER_CREATE_DEVICE_ADDRESS_CAPTURE_REPLAY_BIT`.
- `vkGetDeviceMemoryOpaqueCaptureAddress` returns an opaque address for `VkDeviceMemory` allocated with `VK_MEMORY_ALLOCATE_DEVICE_ADDRESS_BIT` and a `VkMemoryOpaqueCaptureAddressAllocateInfo` chain carrying the captured address.
- `vkGetAccelerationStructureDeviceAddressKHR` returns the device address of a `VkAccelerationStructureKHR` created with `VK_ACCELERATION_STRUCTURE_CREATE_DEVICE_ADDRESS_CAPTURE_REPLAY_BIT_KHR`.

During replay, the application feeds the saved addresses back through the same `pNext` chains so the implementation recreates the buffer, memory, and acceleration structure at the same opaque addresses it used during capture.

Why it matters here:

- The SBT family relies on buffer opaque capture addresses for the raygen, miss, and hit SBT regions.
- The AS family relies on all three: the AS device address, the backing buffer opaque capture address, and the backing memory opaque capture address.

### Feature gates

Four distinct features gate this test:

- `bufferDeviceAddressCaptureReplay` (from `VK_KHR_buffer_device_address`) gates all cases.
- `rayTracingPipelineShaderGroupHandleCaptureReplay` gates the SBT family.
- `rayTracingPipelineShaderGroupHandleCaptureReplayMixed` gates only the `pipeline_before_captured` SBT case, where a non-captured pipeline is created before a captured one.
- `accelerationStructureCaptureReplay` gates the AS family.

### Capture/replay ordering for SBT handles

The SBT family tests three orderings between captured and non-captured pipelines. The spec allows implementations to require that captured and non-captured shader-group handles not coexist unless `rayTracingPipelineShaderGroupHandleCaptureReplayMixed` is supported. The three orderings exercise: a single captured pipeline, a captured pipeline followed by a non-captured one, and a non-captured pipeline followed by a captured one.

## One Concrete Example

Representative SBT case `ray_tracing_pipeline.capture_replay.shader_binding_tables.pipeline_single`:

```text
[host] capture phase (replay == false):
  - create rgen/miss/chit0..chit3 shader groups
  - create SBT buffers for raygen, miss, hit with
    VK_BUFFER_CREATE_DEVICE_ADDRESS_CAPTURE_REPLAY_BIT and
    VK_BUFFER_USAGE_SHADER_DEVICE_ADDRESS_BIT
  - call vkGetBufferOpaqueCaptureAddress on each SBT buffer,
    saving sbtSavedRaygenAddress / sbtSavedMissAddress / sbtSavedHitAddress
  - write targetLayer = 0 into the uniform buffer
  - cmdTraceRays over 8x8x1, writing per-pixel hit/miss values into layer 0
  - copy image to host-visible buffer

[host] replay phase (replay == true):
  - create a NEW pipeline with the same shaders
  - create SBT buffers at the saved opaque capture addresses
    (no CAPTURE_REPLAY bit, opaqueCaptureAddress passed in)
  - write targetLayer = 0 into the uniform buffer
  - cmdTraceRays over 8x8x1, writing into layer 0
  - copy image to host-visible buffer

[host] compare: every pixel of replay layer 0 must equal capture layer 0
```

The shader writes `2 * (shaderNdx + 1)` for a hit on SBT slot `shaderNdx`, and `1` for a miss. Identical per-pixel values between capture and replay prove the replayed SBT addresses resolve to the same shader-group handles.

## End-to-End Test Flow

```text
[host] capture phase (runTest(replay=false)):
  - build descriptor set layout, pipeline layout, ray tracing pipeline
  - build bottom-level AS (checkerboard of triangles or AABBs)
  - build top-level AS, optionally copy/compact/serialize it
  - record opaque capture addresses for SBT buffers (SBT family)
    or for AS + backing buffer + backing memory (AS family)
  - clear 3D result image to 0xFF000000
  - write targetLayer=0, bind pipeline+descriptor set, cmdTraceRays 8x8x1
  - image layout + memory barriers, cmdCopyImageToBuffer, invalidate
[host] replay phase (runTest(replay=true)):
  - rebuild pipeline and SBT/AS at saved opaque addresses
  - clear 3D result image again
  - for SBT pipeline_single / AS: 1 pipeline, targetLayer=0
  - for SBT pipeline_after_captured: 2 pipelines, layer 0=captured, layer 1=non-captured
  - for SBT pipeline_before_captured: 2 pipelines, layer 0=non-captured, layer 1=captured
  - cmdTraceRays per pipeline, each writing its own layer
  - copy back all layers
[host] verifyImage: every replay layer must equal the capture layer pixel-for-pixel
[host] pass iff failures == 0
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `rgen`: one ray generation shader, shared by both families. Traces one ray per pixel into the top-level AS and stores the payload into a 3D `r32ui` image at the layer selected by a uniform buffer.
- `chit0`, `chit1`, `chit2`, `chit3`: four closest-hit shaders. Each writes `uvec4(2*(shaderNdx+1), 0, 0, 1)` to the ray payload. The SBT family uses all four; the AS family uses only `chit1`.
- `isect`: intersection shader for the AABB bottom-level geometry path. Reports an intersection at `t = 0.5` and zeroes the hit attribute.
- `miss`: writes `uvec4(1, 0, 0, 1)` to the ray payload.
- All shaders are generated as GLSL `#version 460 core` with `#extension GL_EXT_ray_tracing : require`, compiled to SPIR-V 1.4 via `vk::SPIRV_VERSION_1_4`.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| 3D `r32ui` storage image (`result`) | yes, `VK_IMAGE_USAGE_STORAGE_BIT \| TRANSFER_*` | yes, binding 1 | written by `rgen` via `imageStore` | yes, via `cmdCopyImageToBuffer` | Holds per-pixel per-layer hit/miss values; this is the pass/fail signal |
| Uniform buffer (`UniformParams{uint targetLayer}`) | yes, host-visible | yes, binding 0 | read by `rgen` | no | Selects which image layer each pipeline writes into, separating capture from replay output |
| Top-level AS | yes | yes, binding 2 | traversed by `traceRayEXT` | no | The ray tracing target; in the AS family it is the object whose address is captured/replayed |
| Bottom-level AS (checkerboard) | yes | yes (referenced by TLAS) | traversed indirectly | no | Provides the hit/miss pattern that distinguishes SBT slots |
| SBT buffers (raygen, miss, hit) | yes, with `DEVICE_ADDRESS_CAPTURE_REPLAY_BIT` in capture, at saved address in replay | yes, via `VkStridedDeviceAddressRegionKHR` | read by the ray tracing fixed function | no | The SBT family's captured/replayed object |
| Result buffer | yes, host-visible | yes, transfer dst | written by `cmdCopyImageToBuffer` | yes, `invalidateMappedMemoryRange` + `deMemcpy` | Copyback path for the pass/fail image |

## What Is Checked

- The device writes a per-pixel `uint32_t` into the 3D result image. Hit pixels carry `2*(shaderNdx+1)` from the selected closest-hit shader; miss pixels carry `1`.
- The host reads back every layer of the result image and compares replay layers against the capture layer pixel-for-pixel with no tolerance.
- For the SBT family, `pipeline_single` compares one replay layer; `pipeline_after_captured` and `pipeline_before_captured` compare two replay layers (one captured, one non-captured) against the single capture layer.
- For the AS family, one replay layer is compared against the capture layer.
- Pass condition: `failures == 0` across all compared pixels.

## Behavior Parameter Identification

> **Behavior parameter:** direct child (intermediate node) of `ray_tracing_pipeline.capture_replay`
>
> **Candidate values:** `shader_binding_tables`, `acceleration_structures`

Sub-axes that configure each value:

- Within `shader_binding_tables`, the `testType` axis selects the capture/replay ordering: `pipeline_single`, `pipeline_after_captured`, `pipeline_before_captured`.
- Within `acceleration_structures`, four configuration axes combine: `operationType` (`building`, `copy`, `compaction`, `serialization`), `buildType` (`cpu_built`, `gpu_built`), `operationTarget` (`top_acceleration_structure`, `bottom_acceleration_structure`), and `bottomTestType` (`triangles`, `aabbs`).

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `shader_binding_tables` (`pipeline_single`) | The implementation did not honor the replayed SBT buffer opaque capture addresses for the raygen, miss, or hit regions, or did not preserve shader-group handle data at those addresses when the SBT was recreated without the capture-replay create flag. |
| `shader_binding_tables` (`pipeline_after_captured`) | The implementation did not correctly isolate a captured pipeline from a subsequently created non-captured pipeline, leaking or corrupting shader-group handle state across the two pipelines. |
| `shader_binding_tables` (`pipeline_before_captured`) | The implementation did not support mixed captured/non-captured shader-group handles (`rayTracingPipelineShaderGroupHandleCaptureReplayMixed`), or did not correctly replay SBT addresses when a non-captured pipeline was created first. |
| `acceleration_structures` (`building`) | The implementation did not honor the replayed AS device address, backing buffer opaque capture address, or backing memory opaque capture address when building an AS from scratch at the captured addresses. |
| `acceleration_structures` (`copy`) | The implementation did not preserve the captured addresses through a `vkCmdCopyAccelerationStructureKHR` operation, producing a copy AS at the replayed address that does not match the original. |
| `acceleration_structures` (`compaction`) | The implementation did not preserve the captured addresses through a compaction copy, or returned an incorrect compacted size from the query pool, producing a compacted AS that does not match the original. |
| `acceleration_structures` (`serialization`) | The implementation did not preserve the captured addresses through serialize-then-deserialize, or produced a serialized blob that does not round-trip to an identical AS. |
| `acceleration_structures` (`cpu_built`) | The host-side AS build path (`VK_ACCELERATION_STRUCTURE_BUILD_TYPE_HOST_KHR`) did not honor the replayed addresses, gated by `accelerationStructureHostCommands`. |
| `acceleration_structures` (`gpu_built`) | The device-side AS build path did not honor the replayed addresses, or the query pool results used for compaction/serialization sizing were read back incorrectly. |
| `acceleration_structures` (`top`/`bottom` target) | The replayed address handling failed specifically for the AS level selected as the copy/compact/serialize target. |
| `acceleration_structures` (`triangles`/`aabbs`) | The replayed address handling failed for a specific bottom-level geometry type, including the intersection shader path used for AABBs. |

## Important Variations and Special Cases

- The `pipeline_before_captured` SBT case is the only one that requires `rayTracingPipelineShaderGroupHandleCaptureReplayMixed`. The other two SBT cases only require `rayTracingPipelineShaderGroupHandleCaptureReplay`.
- The AS family uses `VK_ACCELERATION_STRUCTURE_CREATE_DEVICE_ADDRESS_CAPTURE_REPLAY_BIT_KHR` on every AS it creates, including copies, compactions, and deserialized ASes. The capture flag is set on both the original and the derived AS.
- For the AS family, when `operationTarget` is `top_acceleration_structure`, the bottom-level ASes use a single shared BLAS with `TTT_DIFFERENT_INSTANCES` (instances differ by transform matrix). When `operationTarget` is `bottom_acceleration_structure`, the bottom-level ASes use `TTT_IDENTICAL_INSTANCES` (one BLAS per checkerboard cell). This pairing keeps the copy/compact/serialize target as the only AS that changes between capture and replay.
- The AS family's `gpu_built` path needs a host-side `getQueryPoolResults` round trip when compaction or serialization is requested, because the compacted/serialized sizes are needed before the copy/deserialize can be allocated.
- The AABB bottom geometry uses an intersection shader that reports `t = 0.5` regardless of ray origin, so the hit result is deterministic and independent of the AABB's actual bounds.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| `TestParams` struct | [vktRayTracingCaptureReplayTests.cpp#L157-L168](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L157-L168) | Captures testType, operationTarget, operationType, buildType, bottomType, topType, width/height, and the test configuration pointer. |
| `checkSupport` feature gates | [vktRayTracingCaptureReplayTests.cpp#L904-L950](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L904-L950) | Maps each test type to the Vulkan feature it requires. |
| `initPrograms` shader generation | [vktRayTracingCaptureReplayTests.cpp#L952-L1027](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L952-L1027) | Generates the rgen, chit0..3, isect, and miss shaders shared by both families. |
| SBT capture phase | [vktRayTracingCaptureReplayTests.cpp#L390-L433](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L390-L433) | Creates SBT buffers with the capture-replay bit and records opaque capture addresses. |
| SBT replay phase | [vktRayTracingCaptureReplayTests.cpp#L434-L577](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L434-L577) | Recreates SBT buffers at saved addresses for each testType ordering. |
| AS build/copy/compact/serialize | [vktRayTracingCaptureReplayTests.cpp#L1163-L1523](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L1163-L1523) | Drives the AS operation matrix and records/replays opaque capture addresses. |
| `verifyImage` (SBT) | [vktRayTracingCaptureReplayTests.cpp#L579-L597](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L579-L597) | Pixel-by-pixel comparison of replay layers against the capture layer. |
| `verifyImage` (AS) | [vktRayTracingCaptureReplayTests.cpp#L828-L844](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L828-L844) | Single-layer comparison for the AS family. |
| SBT family registration | [vktRayTracingCaptureReplayTests.cpp#L1614-L1643](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L1614-L1643) | Registers `pipeline_single`, `pipeline_after_captured`, `pipeline_before_captured`. |
| AS family registration | [vktRayTracingCaptureReplayTests.cpp#L1645-L1727](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L1645-L1727) | Registers the operationType x buildType x operationTarget x bottomTestType matrix. |
| Category root registration | [vktRayTracingCaptureReplayTests.cpp#L1729-L1739](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L1729-L1739) | Creates the `capture_replay` group and attaches the two direct children. |

## Questions / Risk Points for User Audit

- Is the primary behavioral axis (direct child: SBT vs AS) the right choice, given that the two children exercise different captured object types?
- Is the failure cause mapping for the AS family too coarse? It lists one cause per configuration axis value, but several could collapse into "address replay not honored" depending on how the implementation factors the work.
- The AABB intersection shader reports `t = 0.5` unconditionally. Is that worth calling out as a special case in the final page, or is it just test scaffolding?
- The `cpu_built` AS path requires `accelerationStructureHostCommands`. Should this be a requirement-based pruning note or a behavior parameter note?

## Conversion Notes for Final Wiki Rewrite

- The brief's Background Knowledge should be distilled into a short unordered list covering opaque capture addresses, the four feature gates, and the SBT capture/replay ordering rule.
- The concrete SBT `pipeline_single` example should become the representative shader walkthrough, since the rgen shader is shared by both families and the SBT case is the simplest capture/replay path.
- The AS family's operation matrix should be presented as a parameter dimensions table, not as separate behavior parameter subsections, because the operationType/buildType/operationTarget/bottomTestType axes configure the same core mechanism rather than changing what is being tested.
- The failure cause mapping table can be carried over directly, then collapsed in `### Cause Analysis` into a smaller number of distinct mechanism groups (SBT address replay, SBT pipeline ordering, AS address replay, AS operation preservation, AS build path, host-side reference/copyback).
- The `cpu_built`/`gpu_built` and `top`/`bottom` and `triangles`/`aabbs` distinctions belong in Case Pruning (requirement-based) and Parameter Dimensions, not in Cause Analysis, unless a specific failure mode is tied to them.
