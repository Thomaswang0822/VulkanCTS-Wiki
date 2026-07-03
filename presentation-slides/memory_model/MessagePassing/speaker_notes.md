# Draft Speaker Notes

## 01: MessagePassing Visibility Tests

- Core question: guard observed → payload visible?
- Scope reminder: not a full Vulkan memory model lecture.
- Timing: ~1 min.

## 02: Vulkan CTS: What and Why

- Conformance = official rule compatibility, not performance.
- Our angle: HLK is closed; Vulkan CTS is open-source learning material.
- Product pass means chip + driver + compiler + runtime + platform.

## 03: Wiki Work: Executable Spec → Readable Knowledge

- Emphasize: wiki is not just navigation; it is explanation-first documentation.
- Useful for: failure triage, group-level diagnosis, implementation planning.
- `Shader Analysis` is the bridge to the rest of this talk.

## 04: Focus for This Talk: `message_passing`

- `message_passing` is a family, not a single hand-written shader.
- Do not introduce payload/guard behavior too early here.
- Next: build vocabulary before stating the expected behavior.

## 05: Backgrounds Before the Walkthrough

- 4×8 tile is a mental model only; Vulkan term is shader invocation/subgroup.
- Familiar lane-read names: HLSL `WaveReadLaneAt`, GLSL `subgroupBroadcast`, CUDA `__shfl_sync`.
- Payload and guard are separate storage, not one variable.
- No swap-style temporary variable; communication is payload + guard.

## 06: Representative Case: The Path We Will Walk Through

- Chosen because it is a clean case: compute, `u32`, subgroup, buffer payload/guard.
- `DIM` is like CUDA blockDim.x/blockDim.y for a square block tile: local workgroup size is `DIM × DIM`.
- `NUM_WORKGROUP_EACH_DIM` is like CUDA gridDim.x/gridDim.y: number of workgroups along each 2D axis.
- Total launched shader invocations are `(DIM × NUM_WORKGROUP_EACH_DIM)²`, analogous to total CUDA threads in a 2D grid.
- `DIM = 31` is intentional: large but under common max workgroup invocation limits after `31² = 961`, and non-power-of-two dimensions catch indexing/synchronization bugs that a neat 32 or power-of-two layout might hide.
- `ext + noncoherent` means explicit MakeAvailable / MakeVisible semantics.
- Pages 07–10 stay inside this exact path.

## 07: Pairing Lanes, Locating Data

- Real pairing rule: `partner = gl_SubgroupInvocationID ^ (gl_SubgroupSize - 1)`.
- In the slide's simplified 32-lane case: partner is `31 - i`.
- Bindings: payload = 0, guard = 1, fail = 2.

## 08: Payload Before Guard, Check After Guard

- Key expected behavior is now safe to state.
- `skip` is not failure; it means the guard was not observed.
- This path has no full-group `barrier()` / CUDA-like `__syncthreads()`; progress is judged only when the peer guard is actually seen.
- Failure only when `!skip` and payload value is wrong.

## 09: Why the Guard Carries the Payload

- Writer side: Release + MakeAvailable.
- Reader side: Acquire + MakeVisible.
- Analogy:
  - write payload: you write a paper
  - release / MakeAvailable: you publish it to arXiv
  - acquire / MakeVisible: your reader downloads it from arXiv
  - read payload: the reader reads your paper
- `queuefamily` scope roughly means synchronization across queues from the same Vulkan queue family; broader than workgroup/subgroup, but not necessarily all queues/devices.
- Guarantee is bounded by both scope and storage semantics.

## 10: From Shader Observation to Host Verdict

- Host does not directly judge payload values; shader writes fail buffer.
- Fail buffer is cleared, shader runs many times, host scans for any nonzero entry.
- One nonzero entry fails the CTS case.

## 11: Same `message_passing` Family, Many Dimensions

- Fixed center: the same payload-before-guard claim.
- Varying axes: mode, type, sync form, operation, scope, storage, stage.
- This explains why mustpass has many similar-looking paths.

## 12: How `write_after_read` and `transitive` Differ

- `write_after_read`: early read must not see the later synchronized write.
- `transitive`: visibility can be carried through a representative + workgroup relay.
- These are contrast cases, not full new walkthroughs.

## 13: Other Test Families in `memory_model`

- `memory_model` is broader than release/acquire.
- First three families: visibility timing.
- `padding`: byte/layout preservation. `shared`: workgroup shared-memory value preservation.

## 14: Vulkan CTS Is Much Bigger Than `memory_model`

- 53 documented top-level Vulkan CTS categories in the wiki index.
- Area grouping is approximate, only for scale awareness.
- Message: this talk sampled one small region of a much larger suite.

## 15: Three Takeaways

- Visibility contract: guard observed → payload visible.
- CTS coverage: same rule tested across many dimensions.
- Wiki value: executable conformance logic becomes readable engineering knowledge.
