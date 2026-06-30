# Understanding Brief: memory_model.message_passing / vktMemoryModelMessagePassing.cpp

This brief prepares a future rewrite of the message-passing-related Vulkan CTS memory-model page. It is intentionally
explanation-first and uses the source code as the primary authority.

## One-Sentence Test Purpose

This test checks whether shader-visible memory writes become correctly available and visible through release/acquire
synchronization, across different scopes, storage classes, shader stages, and transitive visibility chains.

Core question: **if one invocation publishes a payload and signals a guard, can another invocation that observes the guard
reliably observe the payload value that should have happened before it?**

## Background Knowledge

### Payload and guard

The generated shader uses two conceptual variables, generated in the regular shader path around the payload write, guard
synchronization, and final check
[vktMemoryModelMessagePassing.cpp](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L749-L1004):

- **Payload**: the data being protected. Each invocation writes its own coordinate/value and later reads its partner's
  payload.
- **Guard**: the synchronization flag. An invocation writes or atomically updates its own guard after making its payload
  available, and its partner reads or atomically updates that guard before reading the payload.

Why it matters here:

- The payload is the actual correctness observation.
- The guard is not the tested data; it is the synchronization channel that should order the payload access.
- A case can place payload and guard in different storage classes, such as buffers, images, workgroup memory, or physical
  storage buffers.

### Release/acquire, availability, and visibility

The test is built around release/acquire synchronization:

- A **release** operation/fence on the writer side should publish earlier payload writes.
- An **acquire** operation/fence on the reader side should make those writes visible before the reader loads the payload.
- With the Vulkan memory model extension path, ordinary noncoherent `message_passing` visibility checks add explicit
  availability/visibility semantics: `gl_SemanticsMakeAvailable` on release and `gl_SemanticsMakeVisible` on acquire. The
  `write_after_read` variant asks a different timing question and does not use this simplified noncoherent flag rule in the same
  way [vktMemoryModelMessagePassing.cpp](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L468-L479).

Why it matters here:

- The host does not inspect the payload contents directly; the shader checks whether release/acquire made the right payload
  value observable.
- Some sync forms put the semantics on `memoryBarrier`, while others put them directly on atomic operations.
- Noncoherent message-passing cases are extension-mode only because the shader emits Vulkan memory model semantics.

### Scope

The scope selects which invocations can synchronize with each other:

| Scope | Partnering idea in the generated shader |
|-------|------------------------------------------|
| `device` / `queuefamily` | Compute and vertex paths pair a global invocation with the opposite global invocation in the whole test grid; fragment paths use stage-specific tile coordinates and mirror within the derived group tile. |
| `workgroup` | Pair local invocation `(x,y)` with `(DIM-1-x,DIM-1-y)` inside the same workgroup. |
| `subgroup` | Pair lanes with a subgroup XOR shuffle; inactive partner lanes are skipped. |

Why it matters here:

- Scope changes both the memory semantics (`gl_ScopeDevice`, `gl_ScopeQueueFamily`, `gl_ScopeWorkgroup`,
  `gl_ScopeSubgroup`) and the partner-coordinate computation.
- Workgroup memory can only be used meaningfully in compute cases, so the generator prunes non-compute workgroup-memory
  combinations.

### Skipped race instances

The shader often sets `skip` when a reader did not observe its partner's guard as signaled
[vktMemoryModelMessagePassing.cpp](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L850-L973). This is not a
failure by itself. It means that particular racing interleaving did not exercise the ordering edge.

Why it matters here:

- The test repeats the shader many times to increase the chance of observing useful interleavings.
- A failure is only recorded when synchronization says the payload should be visible (`!skip`) but the payload value is
  wrong.
- Subgroup cases also skip/return when the partner lane is inactive, because subgroup shuffles would otherwise be
  undefined.

### Storage classes and real resources

The test matrix uses names such as `buffer`, `image`, `workgroup`, and `physbuffer`, but they do not all map to the same
kind of host-created object.

| Storage class | Shader declaration style | Host-created/bound resource? |
|---------------|--------------------------|-------------------------------|
| `buffer` | SSBO at descriptor binding `0` or `1` | Yes, `BufferWithMemory` plus storage-buffer descriptor. |
| `image` | storage image at descriptor binding `0` or `1` | Yes, `ImageWithMemory`, image view, storage-image descriptor, `GENERAL` layout. |
| `workgroup` | GLSL `shared` object | No external host resource; initialized inside the shader. |
| `physbuffer` | buffer reference using a device address | Yes, `BufferWithMemory` with device-address usage; address passed by push constant. |

Why it matters here:

- `shared` variables in GLSL are generated shader objects, not descriptor-bound host resources.
- Physical storage buffers are real buffers but not descriptor-bound as payload/guard; the shader receives device addresses
  through push constants.

### Why transitive visibility is special

The regular `message_passing` cases are direct: one invocation releases, its partner acquires, then the partner reads the
payload. The separate transitive shader builder adds representative invocations, `sharedSkip`, and explicit availability /
visibility handoff paths
[vktMemoryModelMessagePassing.cpp](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L1032-L1349).

The `transitive` group tests a chain:

1. Every invocation writes payload.
2. Invocation `(0,0)` in each workgroup performs the device-scope release/availability through the guard.
3. Either the destination invocation acquires directly (`nontransvis`) or invocation `(0,0)` acquires and then uses
   workgroup synchronization to pass the visibility to the rest of the workgroup (`transvis`).
4. Each invocation reads its partner's payload.

This is special because the tested property is not only a direct release/acquire pair; it is whether availability and
visibility can be carried through a chain involving device scope and workgroup synchronization.

## One Concrete Example

### Regular `message_passing` example

Representative test name pattern from mustpass:

```text
dEQP-VK.memory_model.message_passing.core11.u32.coherent.fence_fence.atomicwrite.device.payload_local.buffer.guard_local.buffer.comp
```

Simplified behavior for this case:

1. Each compute invocation computes `bufferCoord` and `partnerBufferCoord` from global IDs.
2. It writes `payload.x[bufferCoord] = bufferCoord`.
3. It executes a release `memoryBarrier` for buffer storage.
4. It writes `guard.x[bufferCoord] = 1` with an atomic store.
5. It reads `guard.x[partnerBufferCoord]`.
6. If the partner guard was still `0`, it sets `skip = true` and does not judge this interleaving.
7. Otherwise, it executes an acquire `memoryBarrier`, loads `payload.x[partnerBufferCoord]`, and expects the value to equal
   `partnerBufferCoord`.
8. If the value is wrong, it writes `fail.x[bufferCoord] = 1`.

Conceptual GLSL, reconstructed from the generator:

```glsl
payload.x[bufferCoord] = bufferCoord;
memoryBarrier(gl_ScopeDevice, gl_StorageSemanticsBuffer, gl_SemanticsRelease);
atomicStore(guard.x[bufferCoord], uint(1), gl_ScopeDevice, 0, 0);
skip = atomicLoad(guard.x[partnerBufferCoord], gl_ScopeDevice, 0, 0) == 0;
memoryBarrier(gl_ScopeDevice, gl_StorageSemanticsBuffer, gl_SemanticsAcquire);
r = payload.x[partnerBufferCoord];
if (!skip && r != uint(partnerBufferCoord))
    fail.x[bufferCoord] = 1;
```

Important simplifications:

- The real generator changes qualifiers, semantics, atomic forms, storage class declarations, and coordinate mapping based
  on parameters.
- The actual payload write deliberately includes a dependency on the partner payload's high bit in some paths to prevent
  over-aggressive simplification while still normally writing `bufferCoord`.

### Transitive example

Representative test name pattern from mustpass:

```text
dEQP-VK.memory_model.transitive.noncoherent.fence_fence.payload_nonlocal.buffer.guard_nonlocal.image.transvis
```

Simplified behavior for a `transvis` case:

1. Every compute invocation writes its own payload.
2. A workgroup control barrier makes payload writes available inside the workgroup side of the chain.
3. Only local invocation `(0,0)` performs the device-scope release/availability and signals its guard.
4. In `transvis`, local invocation `(0,0)` also acquires the partner workgroup's guard with
   `gl_SemanticsMakeVisible`, stores the result into `sharedSkip`, and then synchronizes with the rest of the workgroup.
5. The rest of the workgroup copies `skip = sharedSkip` and then reads the partner payload.
6. If `!skip`, every invocation expects its partner payload value to match `partnerBufferCoord`.

Conceptual GLSL, reconstructed from the generator:

```glsl
payload.x[bufferCoord] = bufferCoord;
controlBarrier(gl_ScopeWorkgroup, gl_ScopeWorkgroup,
               gl_StorageSemanticsBuffer | gl_StorageSemanticsShared,
               gl_SemanticsAcquireRelease | gl_SemanticsMakeAvailable);

if (all(equal(gl_LocalInvocationID.xy, ivec2(0,0)))) {
    memoryBarrier(gl_ScopeDevice,
                  gl_StorageSemanticsBuffer | gl_StorageSemanticsImage,
                  gl_SemanticsRelease | gl_SemanticsMakeAvailable);
    imageAtomicStore(guard, imageCoord, uint(1), gl_ScopeDevice, 0, 0);

    skip = imageAtomicLoad(guard, partnerImageCoord00, gl_ScopeDevice, 0, 0) == 0;
    memoryBarrier(gl_ScopeDevice,
                  gl_StorageSemanticsBuffer | gl_StorageSemanticsImage,
                  gl_SemanticsAcquire | gl_SemanticsMakeVisible);
    sharedSkip = skip;
}

controlBarrier(gl_ScopeWorkgroup, gl_ScopeWorkgroup,
               gl_StorageSemanticsBuffer | gl_StorageSemanticsShared,
               gl_SemanticsAcquireRelease | gl_SemanticsMakeVisible);
skip = sharedSkip;
r = payload.x[partnerBufferCoord];
if (!skip && r != uint(partnerBufferCoord))
    fail.x[bufferCoord] = 1;
```

The material difference from regular `message_passing` is the workgroup relay: a single invocation may perform the
visibility-making acquire, then the result is distributed to the workgroup before payload reads.

## End-to-End Test Flow

The host-side setup is shared by the main generated cases, while the device-side middle of the flow differs between
`message_passing`, `write_after_read`, and `transitive`. The high-level timeline below follows the template's `[host]` /
`[device]` format and uses sub-steps for the three shader flows. Registration and pruning are built in
[createTests()](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L2060-L2415), shader generation happens in
[initPrograms()](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L368-L1030) and
[initProgramsTransitive()](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L1032-L1349), and runtime execution
is handled by the host loop
[vktMemoryModelMessagePassing.cpp](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L1356-L2018).

```text
1. [host] register and generate case hierarchy
   1.1 create the `memory_model` root
   1.2 generate the regular `message_passing` and `write_after_read` parameter matrix
   1.3 generate the separate `transitive` matrix with fixed `u32` / compute / device-scope dimensions
   1.4 attach delegated `padding` and `shared` children

2. [host] prune unsupported or intentionally redundant cases
   2.1 require Vulkan / feature / subgroup / shader-stage / memory-type support
   2.2 prune invalid storage-class, scope, synchronization-form, and data-type combinations
   2.3 require availability/visibility-chain support for `transitive`

3. [host] generate shader program artifacts
   3.1 use the regular generator for `message_passing` and `write_after_read`
   3.2 use the transitive generator for `transitive`
   3.3 specialize runtime dimensions with `DIM` and `NUM_WORKGROUP_EACH_DIM`

4. [host] create and bind resources needed by this case
   4.1 create payload and guard buffers/images when the selected storage class needs host resources
   4.2 do not create descriptor-backed resources for `workgroup` payload/guard variables
   4.3 create the device-local fail buffer and host-visible copyback buffer
   4.4 pass physical-buffer payload/guard addresses through push constants when needed
   4.5 create compute or graphics pipeline state for the selected stage

5. [host] submit repeated work
   5.1 clear the fail buffer once before the repeated submissions
   5.2 for each submit and iteration, clear payload/guard resources that exist outside the shader
   5.3 barrier those clears to shader access
   5.4 dispatch compute work or draw vertex/fragment work
   5.5 barrier shader writes back toward transfer/copyback access

6. [device] execute the selected shader-side flow
   6.A regular `message_passing`
       6.A.1 write own payload
       6.A.2 release or make payload available through the chosen fence/atomic/control-barrier form
       6.A.3 signal own guard or participate in the control barrier
       6.A.4 observe partner guard; set `skip` if the partner signal was not observed
       6.A.5 if not skipped, acquire / make visible and read partner payload
       6.A.6 write fail buffer if the partner payload is not the expected partner coordinate
   6.B regular `write_after_read`
       6.B.1 read partner payload before the synchronization step
       6.B.2 synchronize through the same regular generator framework
       6.B.3 write own payload after the synchronization point
       6.B.4 write fail buffer if the early read saw a nonzero value
   6.C `transitive`
       6.C.1 all invocations write payload
       6.C.2 a workgroup barrier gathers payload availability toward local representative `(0,0)`
       6.C.3 the representative performs device-scope guard synchronization with the partner workgroup representative
       6.C.4 `nontransvis` lets destination invocations perform their own acquire/visibility step
       6.C.5 `transvis` lets the representative acquire/make visible and broadcast `sharedSkip` through workgroup memory
       6.C.6 each invocation reads partner payload and writes fail buffer if the chain was observed but payload is wrong

7. [host] copy and inspect results
   7.1 on the final submit, copy the fail buffer to host-visible memory
   7.2 invalidate/read the copyback allocation
   7.3 scan all fail-buffer entries
   7.4 fail the case if any entry is nonzero; log up to 256 failing invocation indices
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

| Artifact | Generated/loaded where | Role |
|----------|------------------------|------|
| Regular GLSL shader source | [MemoryModelTestCase::initPrograms()](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L368-L1030) | Implements `message_passing` and `write_after_read` cases across compute, vertex, and fragment stages. |
| Transitive GLSL shader source | [MemoryModelTestCase::initProgramsTransitive()](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L1032-L1349) | Implements compute-only availability/visibility-chain cases with `sharedSkip`. |
| Fragment helper vertex shader | Regular fragment-stage path | Draws a fullscreen triangle strip so the fragment shader can run over the test grid. |
| Specialization constants | Host pipeline setup | Set `DIM` and `NUM_WORKGROUP_EACH_DIM`; also define compute local size through local-size IDs. |
| Pipeline state | Host pipeline setup | Compute pipeline for compute cases; graphics pipeline for vertex/fragment cases. |
| Amber `permuted_index` cases | `createPermutedIndexTests` | Extra non-VulkanSC message-passing tests loaded from Amber files; adjacent to but separate from generated GLSL cases. |

Important distinction: GLSL `shared` payload/guard and `sharedSkip` are generated shader variables, not host-created Vulkan
resources.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Payload buffer | Yes, when payload storage is `buffer` | Yes, descriptor binding `0` | Written by owner invocation; read by partner | No | Main protected data in buffer-storage cases. |
| Payload image | Yes, when payload storage is `image` | Yes, descriptor binding `0` | Written/read with image operations | No | Tests image storage semantics and image memory barriers/layout. |
| Payload physical buffer | Yes, when payload storage is `physbuffer` | Yes, via device address push constant | Written/read through buffer reference | No | Tests physical storage buffer addressing with memory-model semantics. |
| Payload workgroup variable | No host object | No descriptor binding | Written/read inside compute workgroup | No | Tests shared/workgroup storage semantics; shader-generated only. |
| Guard buffer | Yes, when guard storage is `buffer` | Yes, descriptor binding `1` | Atomic store/load/exchange | No | Synchronization flag in buffer-storage cases. |
| Guard image | Yes, when guard storage is `image` | Yes, descriptor binding `1` | Image atomic store/load/exchange | No | Synchronization flag in image-storage cases. |
| Guard physical buffer | Yes, when guard storage is `physbuffer` | Yes, via device address push constant | Atomic operations through buffer reference | No | Tests physical-buffer guard synchronization. |
| Guard workgroup variable | No host object | No descriptor binding | Atomic operations inside compute workgroup | No | Workgroup-local synchronization flag; shader-generated only. |
| Fail buffer | Yes, always | Yes, descriptor binding `2` | Written with `1` on shader-detected failure | Copied then read | The only pass/fail data the host scans. |
| Copyback buffer | Yes, host-visible/cached if possible | Transfer destination only | Receives copied fail buffer | Yes | Makes fail-buffer results visible to the CPU. |
| Descriptor set | Yes | Yes | Provides buffer/image payload, guard, and fail bindings | No | Connects real resources to generated shader declarations. |
| Push constants | Yes, range size 16 | Yes | Supplies physical payload/guard addresses | No | Required because physical buffers are not descriptor-bound as SSBOs. |
| Images and image views | Yes, for image payload/guard | Yes through descriptors | Cleared, atomically accessed, loaded/stored | No | Need `GENERAL` layout and storage-image usage. |
| Pipeline | Yes | Yes | Executes generated shader | No | Selects compute, vertex, or fragment execution path. |

## What Is Checked

### Device-side checks

| Test family | Device-side pass condition |
|-------------|----------------------------|
| `message_passing` | If partner guard was observed (`!skip`), partner payload must equal `partnerBufferCoord`. |
| `write_after_read` | Initial read of partner payload before synchronized partner write must remain zero. |
| `transitive` | If the guard/visibility chain was observed (`!skip`), partner payload must equal `partnerBufferCoord`. |

The shader records failure by writing `fail.x[bufferCoord] = 1`.

### Host-side checks

The host:

- clears the fail buffer once before repeated execution;
- runs many iterations across four submissions;
- copies the fail buffer to a host-visible buffer only after the last submission;
- invalidates the allocation;
- scans `NUM_INVOCATIONS` entries;
- fails the case if any entry is nonzero.

There is no tolerance or partial success rule: one nonzero fail entry makes the case fail.

## What Failure Means

A failure usually means that an implementation allowed a shader invocation to observe the synchronization signal without
also observing the memory effects that should have been made available/visible by that signal.

Possible bug areas include:

- wrong shader compiler lowering for Vulkan memory model semantics;
- incorrect handling of release/acquire semantics on atomics or `memoryBarrier`/`controlBarrier`;
- missing `MakeAvailable` or `MakeVisible` behavior for noncoherent memory-model cases;
- incorrect scope handling, especially subgroup/workgroup/device differences;
- incorrect storage-class semantics for buffers, images, workgroup memory, or physical storage buffers;
- bad image atomic/load/store synchronization or image layout/access handling;
- incorrect handling of vertex/fragment shader stores and atomics;
- incorrect transitive availability/visibility-chain implementation.

For [`write_after_read`](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L795-L814), a failure has a different
meaning: the reader saw a partner payload write that should not have been visible before the synchronization confirmed the partner
had already performed its early read.

## Important Variations and Special Cases

### `message_passing` vs `write_after_read`

Both use the same broad parameter matrix, but the order of payload access changes:

- `message_passing`: write own payload, signal guard, observe partner guard, then read partner payload.
- `write_after_read`: read partner payload first, synchronize through guard, then write own payload only if the partner read
  has happened; the early read is expected to be zero.

This changes the bug being detected: `message_passing` detects missing visibility of a prior write, while
`write_after_read` detects an unexpected read-after-future-write observation.

### Sync forms

| Sync type | Shape |
|-----------|-------|
| `fence_fence` | Release `memoryBarrier`, guard atomic without semantics, acquire `memoryBarrier`. |
| `fence_atomic` | Release `memoryBarrier`, guard atomic load carries acquire semantics. |
| `atomic_fence` | Guard atomic store carries release semantics, acquire `memoryBarrier`. |
| `atomic_atomic` | Guard atomic store/load or exchange carries release/acquire semantics. |
| `control_barrier` | Control barrier performs acquire+release; no separate guard variable is used. |
| `control_and_memory_barrier` | Release memory barrier, invocation control barrier, acquire memory barrier; no separate guard variable is used. |

Control-barrier variants are pruned to compute and no larger than workgroup/subgroup-like mappings. Their generated test names
still carry guard-locality and guard-storage path components because the hierarchy is uniform, but only the first placeholder guard
combination is kept and no separate shader guard is declared for these forms.

### Coherence and API/memory-model mode

- `core11` cases use Vulkan 1.1 style behavior and prune noncoherent, queue-family, physical-buffer, 64-bit, and atomic-sync
  cases that require newer memory-model semantics.
- `ext` cases emit `#pragma use_vulkan_memory_model` and can use explicit memory scope/semantics.
- Noncoherent regular `message_passing` cases add `MakeAvailable`/`MakeVisible`; `write_after_read` uses the same regular shader
  generator but tests early-read timing rather than positive payload visibility, so the simplified noncoherent visibility rule does
  not apply identically. Noncoherent transitive cases use explicit availability/visibility in the chain-specific shader.

### Storage-class pruning

The generator intentionally avoids invalid or redundant cases:

- workgroup memory is compute-only and does not vary local/nonlocal memory allocation;
- physical storage buffers require buffer-device-address support;
- 64-bit and float atomic testing is limited mostly to `atomic_atomic`;
- 64-bit/f64 image combinations are limited or skipped due to unsupported image atomic formats;
- control-barrier cases do not use guard storage, so only the first guard-locality/storage placeholder is kept.

### Shader stage differences

- Compute cases dispatch a two-dimensional grid of workgroups.
- Vertex cases draw a point cloud and may use rasterizer discard.
- Fragment cases draw a fullscreen quad/strip path and return early for helper invocations.

The core memory-model question is the same, but coordinate mapping and pipeline setup differ.

### Mustpass coverage

The `vk-default` mustpass file includes generated `message_passing`, `write_after_read`, and `transitive` entries. It shows
that `transitive` appears after `shared` entries in the file and includes both `nontransvis` and `transvis` variants.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Package-level registration | [vktTestPackage.cpp](../../../modules/vulkan/vktTestPackage.cpp#L1368-L1379) | Shows `memory_model` is added as a Vulkan CTS root child. |
| Vulkan SC registration | [vktTestPackage.cpp](../../../modules/vulkan/vktTestPackage.cpp#L1413-L1447) | Shows the same `memory_model` factory is also registered for Vulkan SC builds. |
| Factory declaration | [vktMemoryModelTests.hpp](../../../modules/vulkan/memory_model/vktMemoryModelTests.hpp#L30-L35) | Declares the memory-model group factory. |
| Case parameters and support gates | [vktMemoryModelMessagePassing.cpp](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L58-L121), [vktMemoryModelMessagePassing.cpp](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L181-L365) | Defines the test dimensions and feature/memory requirements. |
| Regular shader generation | [vktMemoryModelMessagePassing.cpp](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L368-L1030) | Generates `message_passing` and `write_after_read` GLSL. |
| Regular payload/guard/check logic | [vktMemoryModelMessagePassing.cpp](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L749-L1004) | Shows payload writes/reads, guard synchronization, `skip`, and fail writes. |
| Transitive shader generation | [vktMemoryModelMessagePassing.cpp](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L1032-L1349) | Generates compute-only availability/visibility-chain GLSL. |
| Host resource and pipeline setup | [vktMemoryModelMessagePassing.cpp](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L1356-L1852) | Creates buffers, images, descriptors, push constants, and pipelines. |
| Runtime submission and result scan | [vktMemoryModelMessagePassing.cpp](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L1854-L2018) | Clears resources, dispatches/draws repeatedly, copies fail buffer, and scans failures. |
| Amber permuted-index side group | [vktMemoryModelMessagePassing.cpp](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L2020-L2055) | Adds extra non-VulkanSC message-passing Amber tests. |
| Generated test hierarchy and pruning | [vktMemoryModelMessagePassing.cpp](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L2060-L2415) | Builds `message_passing`, `write_after_read`, `transitive`, `padding`, and `shared` groups. |
| Mustpass message-passing examples | [memory-model.txt](../../../mustpass/main/vk-default/memory-model.txt#L1-L21) | Shows concrete `message_passing` test names. |
| Mustpass transitive examples | [memory-model.txt](../../../mustpass/main/vk-default/memory-model.txt#L8470-L8490) | Shows concrete `transitive` `nontransvis`/`transvis` entries. |
| Mustpass write-after-read examples | [memory-model.txt](../../../mustpass/main/vk-default/memory-model.txt#L9046-L9046) | Shows `write_after_read` entries begin after transitive coverage in the inspected file. |

## Questions / Risk Points for User Audit

- [x] Keep both shader examples in the final wiki page: one regular `message_passing` walkthrough and one additional
  `transitive` walkthrough, because the transitive shader uses a materially different generator and control-flow structure.
- [x] Keep `write_after_read` as a variation of the regular message-passing subgroup, not as a third full walkthrough, because it
  shares the regular shader generator
  [vktMemoryModelMessagePassing.cpp](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L368-L1030).
- [x] The `skip` explanation is important and should remain prominent: skipped interleavings are not failures; failures only occur
  when the guard or transitive chain was observed but the expected payload rule did not hold.
- [ ] Audit whether the final wording should quote more exact `nontransvis` versus `transvis` control-flow details from the
  transitive generator
  [vktMemoryModelMessagePassing.cpp](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L1273-L1327).
- [ ] Verify mustpass line anchors before publishing a final wiki page, because generated lists may shift.

## Conversion Notes for Final Wiki Rewrite

- Keep the one-sentence purpose as the final page's short problem statement.
- Distill the background into a compact prerequisite list: payload/guard, release/acquire, scope, storage class, `skip`, and
  transitive availability/visibility chains.
- Preserve one regular `message_passing` walkthrough and one additional `transitive` walkthrough.
- Make the reconstructed GLSL in both walkthroughs longer and effectively complete, following the generated structure from
  [initPrograms()](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L368-L1030) and
  [initProgramsTransitive()](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L1032-L1349), rather than using
  only the short conceptual snippets from this brief.
- Preserve the resource table in a more formal final-wiki style because it directly addresses generated-artifact vs real
  Vulkan-resource confusion.
- Keep `write_after_read` as a variation of the regular message-passing subgroup because it shares the regular shader generator;
  explain the changed read/write timing without making it a separate walkthrough.
- Move detailed pruning rules and feature gates into a source-mapping or parameter-summary section rather than the main
  narrative.
- Do not copy the beginner-focused prose verbatim into the final page; convert it to the Level-3 wiki style.
