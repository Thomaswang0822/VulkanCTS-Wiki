# Understanding Brief: compute.basic / 64b_indexing / device_group — vktComputeBasicComputeShaderTests.cpp

This brief prepares a rewrite of the compute-category Level-3 page that covers the `basic`, `64b_indexing`, and `device_group` test families. The three families live in one source file because they share the same dispatch-side plumbing, buffer/image descriptor patterns, and compute-pipeline construction variants.

## One-Sentence Test Purpose

This file checks that compute pipelines correctly honor dispatch shape, workgroup memory and barrier semantics, storage-buffer and image side effects, large 64-bit indexing and untyped pointers, and device-group dispatch (including base offset and per-device index), across the pipeline, shader-object SPIR-V, and shader-object binary pipeline construction modes.

Core question: **does the driver turn each registered compute pipeline construction into observable shader behavior, where the side effects of dispatch, barriers, shared variables, workgroup size limits, large indexing, and device-group splits match the expected per-element values?**

## Background Knowledge

### One source file, three test families

The page covers three sibling families (`basic`, `64b_indexing`, `device_group`) that are all registered from one implementation file. This is a structural grouping, not a behavioral one: the families share dispatcher setup, descriptor-set, buffer, and pipeline-construction plumbing, but each family stresses a different facet of compute behavior.

- `basic` covers everyday compute execution: empty shaders and empty workgroups, max workgroup size limits, buffer-to-buffer inverts, read/write SSBO variations, local and command-buffer barriers, shared variables and atomics, image copies, image atomics, image barriers, compute-only queues, replicated composites, Amber regression cases, undefined values, and dispatch sequencing
  [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L5986-L6233).
- `64b_indexing` covers SSBOs whose total size exceeds the 32-bit element range and the untyped-pointer path
  [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L6237-L6265).
- `device_group` covers `cmdDispatchBase`, the maintenance5 variant of base dispatch, and the `gl_DeviceIndex` builtin used in a single shader that runs across physical devices
  [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L6268-L6284).

Why the grouping matters here:

- All three families feed into the same pipeline-construction variant mechanism (`pipeline`, `shader_object_spirv`, `shader_object_binary`) at the category dispatcher, but each family has its own shader-object exclusion rules
  [vktComputeTests.cpp](../../../modules/vulkan/compute/vktComputeTests.cpp#L48-L85).
- All three families pass through `ComputePipelineWrapper` for pipeline construction, which keeps test-instance code uniform
  [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L1311-L1314), and through `vk::ComputePipelineConstructionType` for shader-object gating.
- The reuse is a deliberate organization choice: page semantics should describe per-family behavior, not pipeline construction plumbing.

### Compute pipeline construction variants

The category dispatcher creates three roots (`pipeline`, `shader_object_spirv`, `shader_object_binary`) and runs the same `createChildren` for each. Each test class in this file takes a `vk::ComputePipelineConstructionType` parameter
[vktComputeTests.cpp](../../../modules/vulkan/compute/vktComputeTests.cpp#L48-L85). Some families explicitly skip the shader-object roots:

- The Amber regression cases inside `basic` are skipped when the construction type is a shader object, because Amber scripts target pipelines
  [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L6182-L6224).
- The replicated-composite family is non-VulkanSC and runs only when `!isComputePipelineConstructionTypeShaderObject(...)` is false.
- `64b_indexing` and `device_group` use the same construction-type parameter even though they are not pipeline-specific.

Why it matters here:

- A reader who searches for `compute.shader_object_spirv.basic.*` in mustpass will only see cases that the file allows on that root. The exclusion is a per-file design choice, not a category-wide rule.
- The construction-type parameter changes whether a pipeline object or a shader object is created, which can subtly change how barrier, dispatch, and descriptor code paths interact.

### Dispatch shape, local size, and workgroup count

Each `basic` test case is registered with explicit `tcu::IVec3` values for local size and work size, plus optional buffer count, buffer type, and bounds-check flag. The matrix explores combinations such as `local_size = (1,1,1)`, `(3,2,5)`, `(2,4,1)` paired with work counts that yield either single-invocation, single-workgroup, multi-invocation-per-group, or multi-group workloads
[vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L6000-L6124). The same compute-pipeline wrapper is used for pipeline-construction variants.

Why it matters here:

- The shapes test that `gl_NumWorkGroups`, `gl_WorkGroupSize`, and `gl_GlobalInvocationID` reach shader invocations as the compute-pipeline contract promises.
- Empty workgroup axes (size 0 on x, y, or z) verify that the implementation skips invocations cleanly while still producing correct buffer reads from surviving invocations
  [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L6000-L6012).
- Max local size tests intentionally use `maxComputeWorkGroupSize[axis]` and verify that the limit is honored and that the per-invocation storage buffer index does not exceed `maxStorageBufferRange`
  [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L4817-L4831).

### Compute-side barriers

The `basic` family distinguishes two barrier forms:

- **Local barriers** (within a workgroup) use `barrier()` and `memoryBarrierShared()` in the shader and do not require a `cmdPipelineBarrier` between dispatches
  [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L501-L612).
- **Command-buffer barriers** (cross-workgroup) require `cmdPipelineBarrier(PIPELINE_STAGE_COMPUTE_SHADER_BIT → PIPELINE_STAGE_HOST_BIT)` or other explicit barriers between dispatches to make shader writes visible to subsequent reads
  [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L6097-L6101).

Image barriers (`image_barrier_single`, `image_barrier_multiple`) use two compute shaders (`comp0` writes an `r32ui` storage image, `comp1` reads it and atomically adds the values) with a `cmdPipelineBarrier` between dispatches
[vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L2880-L2905).

Why it matters here:

- The two forms are not interchangeable. Local barriers cannot synchronize across dispatches or across workgroups.
- Image atomic operations across invocations in the same workgroup require a `memoryBarrierImage()` followed by a `barrier()` before the second invocations can `imageAtomicAdd` results that other invocations have just stored
  [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L2653-L2675).
- The check rule for barrier cases is always: host compares the post-dispatch buffer/image contents against the expected per-element formula.

### Shared memory and atomics

`shared_var_*` tests map each global invocation index to a per-workgroup slot in a `shared uint offsets[N]` array, write into a reversed slot order, apply `memoryBarrierShared()` + `barrier()`, and then read out in natural order
[vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L170-L199).

`shared_atomic_op_*` tests reset a shared counter to 0, apply the same barriers, then have each invocation `atomicAdd(count, 1u)` and write `oldVal + 1u` into the storage buffer. The host checks that `values[i] == i + 1` for every element
[vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L358-L386).

Why it matters here:

- Shared atomics and shared memory barriers are the canonical mechanism for intra-workgroup communication. They are not visible across workgroups.
- The tests deliberately choose per-invocation offsets that would collide if the barrier were missing, so a missing or weak barrier produces a clear mismatch in the host-side comparison.

### Large SSBO indexing and untyped pointers

`64b_indexing` allocates an 8 GB SSBO (512M elements of `UVec4`) and dispatches a shader that copies one element per invocation across a `(1024, 1, 1)` workgroup grid. The shader, descriptor type, and pipeline create flags depend on the test case:

- `copy_ssbo_64b` and `copy_ssbo_64b_bounds` use a pipeline create flag `VK_PIPELINE_CREATE_2_64_BIT_INDEXING_BIT_EXT` (set automatically when the buffer size exceeds `1 << 32`).
- `copy_ssbo_64b_bounds_local` adds a robust-buffer-access bounds test on the device side.
- `copy_ssbo_64b_execution_mode` uses the GLSL `#pragma shader_64bit_indexing` execution mode instead of the create flag.
- `untyped_pointers` uses a hand-written SPIR-V assembly fragment with `OpCapability UntypedPointersKHR`, `OpUntypedVariableKHR`, and `OpUntypedArrayLengthKHR`, and it sets `VK_PIPELINE_CREATE_2_64_BIT_INDEXING_BIT_EXT` on the pipeline.

All `64b_indexing` cases are non-VulkanSC and require either `VK_EXT_shader_64bit_indexing` (with `shader64BitIndexing`) or `VK_KHR_shader_untyped_pointers`
[vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L1311-L1333), [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L1857-L1862), [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L6237-L6265).

Why it matters here:

- The 8 GB buffer is bound through a 32-bit `uint` descriptor range (`offset + ndx`) but the GPU must perform arithmetic that wraps the 32-bit range. The pipeline create flag and the execution mode pragma both declare 64-bit indexing support, but they are independent code paths that an implementation must support.
- Untyped pointer support is a separate SPIR-V capability; the test compiles an inline SPIR-V module rather than GLSL, because untyped pointers are not exposed through standard GLSL.

### Device-group dispatch

The `device_group` family splits compute work across physical devices:

- `dispatch_base` and `dispatch_base_maintenance5` use `cmdDispatchBase` with explicit `(baseX, baseY, baseZ)` offsets and a partial workgroup count. The pipeline is created with `VK_PIPELINE_CREATE_DISPATCH_BASE`, except in the maintenance5 variant where the `VK_PIPELINE_CREATE_2_DISPATCH_BASE_BIT_KHR` create-flag2 is used instead. The shader uses a uniform buffer to pass the global grid size, so the per-device work counts remain correct regardless of which device executes each chunk
  [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L3276-L3557).
- `device_index` uses a single compute pipeline that reads `gl_DeviceIndex` from the GL_EXT_device_group extension and combines it with a uniform array of base offsets. The test iterates over all non-empty device masks and copies the SBO into a per-device check buffer for host inspection
  [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L3796-L4089).
- `indirect_after_base_dispatch` (in `basic`) chains `cmdDispatchBase` followed by `cmdDispatchIndirect` and verifies that the atomic counter holds the sum of both dispatches' invocations
  [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L3582-L3794).

Why it matters here:

- Device-group work splits are computed from `m_splitWorkSize.x()` per device and `m_localSize.{y,z}` within a device; the test asserts that `totalWorkloadSize == multiplyComponents(m_workSize)`, so a missing dispatch or a wrong device mask produces a clear size mismatch
  [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L3413-L3560).
- `device_index` allocates the SBO with `VK_MEMORY_ALLOCATE_DEVICE_MASK_BIT` and a device mask that includes every physical device, because the same memory is read by every device in the mask
  [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L3895-L3956).

### Replicated composites

`basic.replicated_composites_*` tests check the `shaderReplicatedComposites` extension. The shader declares a composite (`vec4`, `mat4`, `uint[3]`, nested `S[3]`/`SS[2]`, or a `coopmat`) and uses `#pragma use_replicated_composites` to ask the compiler to apply the optimization. Three instantiation modes are tested:

- `value`: regular local variable initialization.
- `constant`: `const` composite.
- `specconstant`: specialization-constant-driven composite.

Each test compares the storage-buffer contents against a host-known reference
[vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L5339-L5858).

Why it matters here:

- The COOPMAT variant additionally requires `VK_KHR_cooperative_matrix` plus a `VK_COMPONENT_TYPE_FLOAT16_KHR` subgroup-scope cooperative-matrix property.
- The shader uses `#pragma use_replicated_composites` and `#extension GL_EXT_spec_constant_composites`; without these the compiler cannot apply the replicated-composites optimization.

## One Concrete Example

Consider `compute.basic.copy_ssbo_single_invocation`. The host fills a 256-element `UVec4` input buffer with random `uint32_t` data, binds the input as `STORAGE_BUFFER` (binding 0) and an output buffer (binding 1) with usage `STORAGE_BUFFER_BIT | TRANSFER_SRC_BIT | TRANSFER_DST_BIT`. The output buffer is pre-filled with `0xBEBEBEBE` using `cmdFillBuffer` so that the test can detect missed writes. The shader is one invocation (`local_size = (1,1,1)`, workgroups `(1,1,1)`); it computes `numValuesPerInv = length / invocations`, derives its offset, and writes `~input[offset + ndx]` into `output[offset + ndx]` for each `ndx`. After dispatch, the host walks the output buffer and expects `output[i].x == ~input[i].x` and `output[i].y == 0`; the `.y == 0` check is implicitly satisfied because `UVec4` elements were initialized with only `x` set, and the shader does not write to `.y`. The same shape is repeated as `copy_ssbo_multiple_invocations` (`local_size = (1,1,1)`, `workgroups = (2,4,1)`) and `copy_ssbo_multiple_groups` (`local_size = (1,4,2)`, `workgroups = (2,2,4)`) to exercise multi-invocation and multi-group coordination
[vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L1336-L1390), [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L6042-L6053).

## End-to-End Test Flow

```text
[host] checkSupport — gate shader-object, shader64BitIndexing, robustness2, replicated composites, device group, etc.
[host] build descriptor set layout and pipeline with ComputePipelineWrapper
[host] create input/output (or input/image) buffers with required usage flags
[host] populate input (random, deterministic, or zero-initialized) and pre-fill output for missed-write detection
[host] record compute command buffer: bind pipeline, bind descriptors, barrier host→compute, cmdDispatch
[host] barrier compute→host (or compute→transfer for image copyback), submit and wait
[device] execute shader: write results into storage buffer or storage image
[host] copyback read or copy-buffer-to-host readback
[host] compare against expected per-element formula
```

For image atomic and image barrier cases the device step also uses an image-layout transition from `UNDEFINED` to `GENERAL` and an explicit `copyImageToBuffer` after dispatch. For the device-group cases the host step also iterates over `physDevMask` and `physDevIdx` to copy the SBO into a per-device check buffer.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- Inline GLSL compute shaders generated in `initPrograms(SourceCollections&)` for each test class:
  - Buffer-to-buffer inverts (UBO→SSBO and SSBO→SSBO) [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L1336-L1390).
  - Shared variable and shared atomic shaders [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L170-L199), [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L358-L386).
  - Max-workgroup-size shaders with `local_size_*_id = 0/1/2` specialization constants [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L4787-L4809).
  - Image atomic and image barrier shaders [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L2653-L2675), [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L2880-L2905).
  - Dispatch-base and device-index shaders using `#extension GL_EXT_device_group : require` [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L3339-L3365), [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L3844-L3871).
- Inline SPIR-V assembly for the untyped-pointer case [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L1865-L1901).
- Amber test scripts for the compute-only non-shader-object regression cases inside `basic` (`write_ssbo_array`, `atomic_barrier_sum_small`, `vec2_nclamp_nan_component`, `branch_past_barrier`, `float64_isnan_isinf`, `float16_isnan_isinf`, `webgl_spirv_loop`, `pk_immediate`, `pkadd_immediate`).
- Specialization constants for replicated composites and `max_local_size_*` tests.
- `VkSpecializationInfo` (compiled into the pipeline) for replicated-composites float values, cooperative-matrix rows/cols, and per-axis local sizes.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Input storage buffer (`STORAGE_BUFFER` or `UNIFORM_BUFFER`) | yes | yes | read | yes (filled by host, then invalidated) | Source of the values being copied/inverted |
| Output storage buffer (`STORAGE_BUFFER`) | yes | yes | write | yes | Receives shader output; pre-filled with sentinel value to detect missed writes |
| `r32ui` storage image (`image_atomic_op_*`, `image_barrier_*`) | yes | yes | imageStore / imageLoad / imageAtomicAdd | yes (copyImageToBuffer) | Image side-effect under test |
| `UVec4` input buffer for image atomic input | yes | yes | read | yes | Per-pixel sum values fed to `imageAtomicAdd` |
| Uniform buffer with grid size (device-group cases) | yes | yes | read | host writes | Passes global workgroup size to the device-group shader |
| Indirect dispatch buffer (`VK_BUFFER_USAGE_INDIRECT_BUFFER_BIT`) | yes | yes | n/a (read by cmdDispatchIndirect) | yes | Holds `VkDispatchIndirectCommand` for the second dispatch |
| Counter storage buffer (`indirect_after_base_dispatch`) | yes | yes | atomicAdd | yes | Verifies total invocations = base + indirect |
| `r32ui` storage image used as barrier relay (`image_barrier_*`) | yes | yes | comp0 writes, comp1 reads | yes (image copyback) | Exercises image-barrier dependence between two compute dispatches |
| Device-mask-allocated SBO (`device_index`) | yes | yes | write | yes (per-device copy) | Cross-device storage visible to all physical devices in the mask |
| Replicated-composites output buffer | yes | yes | write | yes | Reference for `use_replicated_composites` correctness |
| Compute-only secondary command buffer (`secondary_compute_only_queue`) | yes | yes | executes a compute pipeline | n/a | Tests secondary command buffers on a compute-only queue family |
| Shared `offsets[]` / `count` (GLSL `shared`) | n/a (shader only) | n/a | read/write | n/a | Intra-workgroup coordination via `barrier()` + `memoryBarrierShared()` |

## What Is Checked

The pass condition for nearly every case is a per-element buffer or image comparison:

- For buffer-to-buffer inverts the host expects `output[i].x == ~input[i].x` (or `0xBEBEBEBE` if the element is outside the descriptor range, used as the missed-write sentinel)
  [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L1614-L1628).
- For shared-variable cases the host expects `output[globalOffs + localOffs] == globalOffs + squared(workGroupSize - localOffs - 1)` [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L292-L308).
- For shared-atomic cases the host expects `output[i] == i + 1` (per-element index, since `atomicAdd(count, 1)` produces sequential values per invocation) [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L481-L497).
- For max-workgroup-size cases the host expects every SSBO slot to equal `1u` (each invocation writes its own slot)
  [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L4963-L4979).
- For image-atomic cases the host sums the per-pixel inputs and expects the image pixel value to match
  [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L2812-L2835).
- For device-group dispatch-base cases the host checks every buffer element after summing the total workload against `multiplyComponents(m_workSize)`
  [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L3559-L3569).
- For device-index cases the host copies the SBO into a per-device check buffer for each physical device in the mask and expects `bufferPtr[i] == constantValPerLoop + uniformInputData[4 * (physDevIdx + 1)]`
  [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L4072-L4085).
- For `indirect_after_base_dispatch` the host expects `counter == 1 + 3*3*1 == 10` [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L3780-L3793).
- For replicated-composites cases the host compares the buffer against the expected reference per composite type and instantiation mode [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L5792-L5856).
- For empty-workgroup cases the host expects exactly `1u` in the verification buffer, confirming that the second `cmdDispatch(1,1,1)` ran and that the empty-axis dispatch contributed no invocations [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L4684-L4696).
- For `concurrent_compute` the host expects both buffers to be inverted, but it also expects the high-priority fence to be already signalled when the low-priority fence completes (a queue-priority ordering check) [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L4495-L4513).

## Behavior Parameter Identification

> **Behavior parameter:** `test family` (the page covers `basic`, `64b_indexing`, `device_group` rooted in the same implementation file)
>
> **Candidate values:** `basic`, `64b_indexing`, `device_group`

If the identification is wrong the failure analysis below will need to be redone. The `test family` is chosen as the primary behavioral axis because each family changes the dispatch / memory / synchronization question, while sub-families (`empty_workgroup_*`, `max_local_size_*`, `replicated_composites_*`, etc.) operate as dimension-axes within `basic`.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `basic` | Wrong per-invocation mapping between global invocation ID and buffer element; missing or weak workgroup/barrier synchronization; missing barrier between host write and shader read (or between shader write and host read); wrong image layout transition or image barrier between dispatches; wrong max-workgroup-size specialization constants; pipeline construction (pipeline vs shader object) mishandling; Amber-script regressions; undefined-value propagation from struct assignments; wrong counter accumulation in dispatch-sequencing cases; queue-priority ordering mis-observed in concurrent_compute; missing `robustBufferAccess2` handling in bounds-check variants; replicated-composites compiler pass failing for one or more composite types; cooperative-matrix replicated-composites failing when `VK_COMPONENT_TYPE_FLOAT16_KHR` is not available. |
| `64b_indexing` | Buffer descriptor or arithmetic exceeding the 32-bit element range without the correct 64-bit indexing pipeline create flag or execution-mode pragma; `VK_EXT_shader_64bit_indexing` feature missing on the implementation; out-of-memory failure when allocating an 8 GB buffer; `VK_KHR_shader_untyped_pointers` capability not supported; pipeline create flag conflict between `VK_PIPELINE_CREATE_2_64_BIT_INDEXING_BIT_EXT` and the chosen pipeline construction mode. |
| `device_group` | `cmdDispatchBase` skipping a chunk of the workgrid; wrong per-device work distribution across `m_splitWorkSize`; uniform-buffer grid size not propagated correctly to the shader; maintenance5 create-flag2 path differing from the legacy `VK_PIPELINE_CREATE_DISPATCH_BASE` flag; `gl_DeviceIndex` builtin producing the wrong value per device; cross-device visibility not honored for the device-mask SBO; per-device readback missing a physical device in the mask; fence-based ordering between `cmdDispatchBase` and `cmdDispatchIndirect` violating expected completion order. |

## Important Variations and Special Cases

- **Shader-object exclusion** — The Amber regression cases inside `basic` and the entire `replicated_composites_*` family under `basic` are skipped when the construction type is a shader object
  [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L6154-L6224). This means `compute.shader_object_spirv.basic.write_ssbo_array` and `compute.shader_object_spirv.basic.replicated_composites_*` are not registered test cases; they exist only under `compute.pipeline.basic`.
- **Pipeline create-flag variants for 64-bit indexing** — `copy_ssbo_64b` uses the create flag, `copy_ssbo_64b_execution_mode` uses the GLSL pragma. Both must succeed, but they exercise different parts of the shader compiler and pipeline-creation code paths.
- **VulkanSC gating** — Replicated composites and `dispatch_base_maintenance5` are non-VulkanSC; everything else (including 64-bit indexing and dispatch base) runs under VulkanSC.
- **Bounds-check variants** — `copy_ssbo_bounds`, `copy_ssbo_64b_bounds`, and `copy_ssbo_64b_bounds_local` build a robust-buffer-access device (`getRobustDevice`) that returns zero for out-of-range reads. Without `robustBufferAccess2` the case is `NotSupportedError`
  [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L1322-L1333), [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L1420-L1427).
- **Compute-only queue secondary command buffers** — `secondary_compute_only_queue` creates a custom device with a queue family that has `VK_QUEUE_COMPUTE_BIT` but not `VK_QUEUE_GRAPHICS_BIT`, then records a secondary command buffer and executes it through the standard command buffer
  [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L5031-L5137).
- **`max_local_size_*` with specialization constants** — The shader uses `local_size_x_id = 0`, `local_size_y_id = 1`, `local_size_z_id = 2` and the host provides a specialization info with the chosen axis's max value
  [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L4792-L4809). The pipeline must consume the specialization constants before the workgroup size is fixed.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Test family registrations | [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L5986-L6285) | All three families are registered from one file |
| `BufferToBufferInvertTest` (SSBO/UBO) | [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L1222-L1638) | Core buffer-to-buffer copy/invert semantics, optional bounds check, optional 64-bit indexing flag |
| `SharedVarTest`, `SharedVarAtomicOpTest` | [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L123-L497) | Workgroup-shared memory and atomics |
| `EmptyWorkGroupCase` | [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L4553-L4696) | Empty workgroup axes |
| `MaxWorkGroupSizeTest` | [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L4698-L4980) | Maximum workgroup size limits |
| `SSBOBarrierTest` | [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L2361-L2605) | SSBO command-buffer barrier between dispatches |
| `ImageAtomicOpTest` | [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L2606-L2837) | Image atomics across invocations |
| `ImageBarrierTest` | [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L2838-L3083) | Image barrier across dispatches |
| `UntypedPointerTest` | [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L1840-L1944) | Inline SPIR-V untyped pointers + 64-bit indexing flag |
| `WriteToMultipleSSBOTest`, `InvertSSBOInPlaceTest`, `ReadUnboundSSBOTest` | [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L1640-L2359) | Multiple SSBO writes and SSBO read-while-bound |
| `ConcurrentCompute` | [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L4091-L4551) | Concurrent compute queue ordering |
| `ReplicatedCompositesTest` | [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L5339-L5858) | Replicated composites per composite type and instantiation mode |
| `DispatchBaseTest`, `DeviceIndexTest`, `SequentialDispatchTest` | [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L3276-L4089), [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L3582-L3794) | Device-group dispatch base, maintenance5 variant, device index, dispatch sequencing |
| `SecondaryCommandBufferComputeOnlyTest` | [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L5137-L5338) | Compute-only queue with secondary command buffers |
| `UndefinedValues` | [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L5861-L5982) | Defined/undefined values via struct assignment in a 1.2+ shader |
| `EmptyShaderTest` | [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L4982-L5029) | Empty shader dispatch smoke |
| Category dispatcher | [vktComputeTests.cpp](../../../modules/vulkan/compute/vktComputeTests.cpp#L48-L85) | `pipeline`/`shader_object_spirv`/`shader_object_binary` roots |

## Questions / Risk Points for User Audit

- Is the three-family grouping (`basic` + `64b_indexing` + `device_group` from one file) clear as a structural reason, not as a behavioral reason?
- Are the shader-object exclusions (Amber cases inside `basic`, replicated composites) documented at the right depth?
- Is the device-group pipeline create-flag distinction (`VK_PIPELINE_CREATE_DISPATCH_BASE` vs `VK_PIPELINE_CREATE_2_DISPATCH_BASE_BIT_KHR`) made clear?
- Is the relationship between `max_local_size_*` specialization constants and the chosen per-axis workgroup limit stated in the right level of detail?
- Are the concrete failure cause mappings for each family specific enough to be auditable against the source?

## Conversion Notes for Final Wiki Rewrite

- Distill the brief into `## Background Knowledge` (compact prerequisites) and `## Behavior Parameters` (one subsection per family with one paragraph each).
- Move the per-class source links into `## Source Reference Appendix`.
- Carry the `### Failure Cause Mapping` table above verbatim into the final page's `## Failure Meaning` → `### Failure Cause Mapping`.
- Write `### Cause Analysis` fresh; it should not copy the brief's notes.
- The representative shader walkthrough will use `compute.basic.copy_ssbo_single_invocation` because it is the canonical buffer-to-buffer case that exercises local size, workgroup count, descriptor layout, dispatch, barrier, and host readback. The SPIR-V will be generated from the reconstructed GLSL and verified through `shader-disassembler` to ensure the assembly `; Version:` header matches the target SPIR-V version.
- Read the relevant Vulkan spec chapters at `external/vulkan-docs/src/chapters/` for compute dispatch, workgroup semantics, and device-group dispatch. Note: the `external/vulkan-docs` tree is not present in the inspected checkout, so the brief and page must rely on source and registration evidence directly; if a spec-grounded claim cannot be made, the page should say so rather than guessing.