# Understanding Brief: `subgroups.basic`

## One-Sentence Test Purpose

This test checks whether basic subgroup election and barrier operations produce the expected per-subgroup result across supported shader stages, resource classes, and required subgroup sizes.

## Background Knowledge

### Subgroup scope and basic operations

A subgroup is a set of shader invocations that can communicate and synchronize efficiently. Vulkan permits subgroup scope as both an execution scope and a memory scope for barriers. The basic operation set includes election, control barriers, memory barriers, and atomics; election returns true only for the active invocation with the lowest id.

Why it matters here:
- `subgroupElect()` selects the invocation that writes the reference value.
- The barrier variants determine which execution or memory dependency should make that value observable to the other active invocations in the subgroup.

### Execution synchronization versus memory dependencies

A control barrier synchronizes execution and includes memory semantics. A memory barrier establishes the specified memory dependency but is not itself a host command or a workgroup-wide rendezvous. The GLSL subgroup operations used here lower to subgroup-scoped SPIR-V operations.

Why it matters here:
- `subgroupBarrier()` is the broad control-barrier case.
- The memory-barrier variants narrow the exercised memory class to all memory, buffer memory, workgroup `shared` memory, or image memory.

## One Concrete Example

For `dEQP-VK.subgroups.basic.compute.subgroupbarrier_requiredsubgroupsize`, the compute shader assigns each subgroup a slot in `tempBuffer`. The elected invocation writes the host-provided `value`, every active invocation executes `subgroupBarrier()`, and then all invocations read the same slot into their result element. The host runs this case at every supported power-of-two required subgroup size and expects every result element to equal the reference value.

## End-to-End Test Flow

```text
[host] choose operation, execution path, shader stage, and required-subgroup-size mode
[host] check subgroup, stage, operation, and optional size-control support
[host] generate the selected shaders with initPrograms or initFrameBufferPrograms
[host] create and initialize result, temporary, reference-value, and optional image resources
[host] build the pipeline; for required-size cases, select one supported power-of-two subgroup size
[host] dispatch, draw, trace rays, or launch mesh tasks through the shared subgroup helpers
[device] elect one active invocation or perform the selected barrier operation
[device] write a per-invocation result to an SSBO or framebuffer attachment
[host] wait, invalidate/read mapped output, and invoke the path-specific result callback
[host] pass only if all required runs and all checked output elements match the callback's rule
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `initPrograms` selects SPIR-V 1.3 for compute and graphics paths and SPIR-V 1.4 for ray-tracing and mesh paths. It routes compute and mesh cases through `initComputeOrMeshPrograms`; other all-stage cases use `subgroups::initStdPrograms`.
- `initFrameBufferPrograms` builds the no-SSBO framebuffer path with SPIR-V 1.3. Some fixed passthrough stages are embedded as SPIR-V assembly while the tested barrier stages are generated as GLSL where applicable.
- Compute and mesh shaders use specialization IDs 0, 1, and 2 for local size.
- Required-subgroup-size cases rebuild or execute the pipeline for every supported power-of-two size in the device's advertised range.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `result[]` | yes | yes | written | yes | Stores one value per executed invocation for host validation. |
| `tempBuffer[]` | yes | yes | read/write | no direct validation | Carries the elected invocation's reference value for generic, buffer, and control-barrier cases. |
| `value` | yes | yes | read | yes, as callback reference data | Supplies a nonzero reference value that results must match. |
| `tempImage` | yes | yes | read/write for image cases | no direct validation | Exercises the image-memory barrier variant with an `r32ui` storage image. |
| `tempShared[]` | no; shader-local | no descriptor binding | read/write | no | Exercises workgroup `shared` storage in compute and mesh shaders. |
| framebuffer color attachment | yes | yes | written | yes | Carries no-SSBO path results for a single graphics stage. |
| per-stage counters and IDs | yes where used | yes | atomic read/write | yes where callback needs them | Distinguish subgroups and count elected invocations in all-stage graphics/ray-tracing paths. |

## What Is Checked

- Compute and mesh election cases expect every invocation's result to be `1`, because the helper ballot must count exactly one elected invocation per subgroup.
- Compute and mesh barrier cases expect every result element to equal the nonzero host-provided reference value.
- All-stage graphics and ray-tracing election callbacks accept only `42` or `13` and compare the number of elected markers with the atomic subgroup count.
- All-stage barrier callbacks require every output value to equal the host reference.
- Framebuffer callbacks decode color components that carry the observed value, reference value, election marker, and pre-barrier value; they reject zero/unmatched results according to the resource variant.
- A required-size test passes only after every supported power-of-two subgroup size in the advertised range passes.

## Behavior Parameter Identification

> **Behavior parameter:** operation test case leaf stem
>
> **Candidate values:** `subgroupelect`, `subgroupbarrier`, `subgroupmemorybarrier`, `subgroupmemorybarrierbuffer`, `subgroupmemorybarriershared`, `subgroupmemorybarrierimage`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `subgroupelect` | Election or active-invocation handling does not produce exactly one elected invocation per subgroup, or the result/count transport is wrong. |
| `subgroupbarrier` | Subgroup execution synchronization or the associated memory dependency does not make the elected write visible before peer reads. |
| `subgroupmemorybarrier` | The general subgroup-scoped memory dependency does not make the elected write visible through the exercised resource path. |
| `subgroupmemorybarrierbuffer` | The buffer-memory subgroup dependency or buffer access path does not preserve the elected write for peer reads. |
| `subgroupmemorybarriershared` | The workgroup `shared`-memory subgroup dependency or shared-memory access path does not preserve the elected write for peer reads. |
| `subgroupmemorybarrierimage` | The image-memory subgroup dependency, storage-image access, or image result path does not preserve the elected write for peer reads. |

## Important Variations and Special Cases

- Execution paths are `graphics`, `compute`, `framebuffer`, `ray_tracing`, and `mesh`; ray tracing and mesh are excluded from Vulkan SC builds.
- `subgroupmemorybarriershared` is registered only for compute and mesh because shader `shared` memory is unavailable in the other tested paths.
- Compute and mesh register both ordinary and `_requiredsubgroupsize` forms. Mesh names also include `_mesh` or `_task`.
- Framebuffer cases select one shader stage at a time. `subgroupelect_fragment` is intentionally not registered; the source says it is not tested but does not explain why.
- Non-election, non-compute paths require ballot support because the generated shader elects one invocation, assigns a subgroup ID with an atomic counter, then broadcasts it.
- The required-size sweep changes pipeline subgroup size, not the shader's correctness rule.
- The current main `test-issues.txt` has no exclusion matching `subgroups.basic`; its only subgroup entry applies to `subgroup_uniform_control_flow.*partial*`.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Operation and case definition | [`OpType` and `CaseDefinition`](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L43-L60) | Defines the operation, stage, and required-size dimensions. |
| Framebuffer shader builder | [`initFrameBufferPrograms`](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L317-L1410) | Generates the single-stage no-SSBO shader paths. |
| Compute/mesh shader generator | [`initComputeOrMeshPrograms`](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L1611-L1758) | Emits the representative compute shader templates and mesh/task variants. |
| Main program builder | [`initPrograms`](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L1760-L1786) | Selects the SPIR-V target and routes each stage set. |
| Support checks | [`supportedCheck`](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L1788-L1845) | Enforces operation, stage, extension, and size-control requirements. |
| Runtime and callbacks | [`test`](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L1922-L2188) | Selects helper paths, resources, callbacks, and required-size loops. |
| Registration | [`createSubgroupsBasicTests`](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L2196-L2314) | Constructs exact hierarchy and test names. |
| Shared ballot helper | [`getSharedMemoryBallotHelper`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L867-L895) | Explains how compute election counts one winner using shared memory. |
| Compute/mesh result scan | [`checkComputeOrMesh`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L2655-L2663) | Reduces the invocation grid to an element-wise reference check. |
| Required-size execution helper | [`makeComputeOrMeshTestRequiredSubgroupSize`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L3762-L4064) | Creates, submits, reads back, and checks compute/mesh runs. |
| Mustpass representative case | [`subgroups.txt`](../../../mustpass/main/vk-default/subgroups.txt#L18372-L18383) | Proves the exact compute leaves, including the selected walkthrough case. |
| Subgroup and basic operation semantics | [`shaders.adoc`](../../../../vulkan-docs/src/chapters/shaders.adoc#L3220-L3247) and [`shaders.adoc`](../../../../vulkan-docs/src/chapters/shaders.adoc#L3447-L3474) | Defines subgroup scope, group operations, election, and barriers. |
| Required subgroup size | [`pipelines.adoc`](../../../../vulkan-docs/src/chapters/pipelines.adoc#L1503-L1549) | Defines the pipeline field and its power-of-two range constraints. |
| Advertised subgroup support | [`limits.adoc`](../../../../vulkan-docs/src/chapters/limits.adoc#L1305-L1353) | Defines supported stages, operations, and the basic feature bit. |

## Questions / Risk Points for User Audit

- Is the operation test case leaf stem the right primary behavior parameter for comparing failure meaning across this broad family?
- Does the distinction between control synchronization and memory dependencies remain clear without overclaiming the exact GLSL-to-SPIR-V memory semantics?
- Is the framebuffer color-channel encoding explained at enough depth for this family-level page?
- The source itself gives no reason for omitting framebuffer `subgroupelect_fragment`; this remains a documented design uncertainty rather than an inferred rule.

## Conversion Notes for Final Wiki Rewrite

- Use `dEQP-VK.subgroups.basic.compute.subgroupbarrier_requiredsubgroupsize` as the representative shader walkthrough.
- Use exact builder `initPrograms`; follow its compute branch into `initComputeOrMeshPrograms` during reconstruction.
- Keep the operation test case leaf stem as the behavior parameter and preserve the Failure Cause Mapping table verbatim.
- Distill subgroup scope, election, barrier, and required-size semantics into short prerequisite bullets.
- Move builder/helper inventories into the source appendix and retain the required-size loop in runtime/pruning sections.
