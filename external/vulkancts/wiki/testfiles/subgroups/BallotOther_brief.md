# Understanding Brief: `subgroups.ballot_other`

## One-Sentence Test Purpose

This test checks whether ballot-derived subgroup operations correctly interpret, count, scan, and search 128-bit ballot masks across supported shader stages and subgroup sizes.

## Background Knowledge

### Ballot masks and active invocations

A subgroup operation runs across invocations in one subgroup scope instance. A ballot operation collects one Boolean contribution from each participating invocation into a mask. Vulkan exposes ballot operations through the `GroupNonUniformBallot` capability when `VK_SUBGROUP_FEATURE_BALLOT_BIT` is supported.

The GLSL ballot mask is a `uvec4`, so it can hold 128 invocation bits. The actual subgroup may be smaller. Bits at or above `gl_SubgroupSize` do not represent invocations in that subgroup, and the test deliberately supplies masks that separate meaningful low bits from the unused high range.

Why it matters here:
- inverse and extract operations map an invocation index to one mask bit;
- count and scan operations must distinguish the whole mask from prefixes ending before or at the current invocation;
- least-significant-bit and most-significant-bit operations must return invocation indices, not bit counts.

### Reduction, inclusive scan, and exclusive scan

`subgroupBallotBitCount`, `subgroupBallotInclusiveBitCount`, and `subgroupBallotExclusiveBitCount` lower to the same SPIR-V ballot bit-count instruction with different group operations. Vulkan limits that instruction to `Reduce`, `InclusiveScan`, or `ExclusiveScan`.

For invocation `k`:
- a reduction counts all set bits in the ballot that belong to the subgroup;
- an inclusive scan counts set bits at indices from zero through `k`;
- an exclusive scan counts set bits at indices below `k`.

The one-element difference between inclusive and exclusive prefixes is the central boundary condition for those two test cases.

## One Concrete Example

The representative case is `dEQP-VK.subgroups.ballot_other.compute.subgroupballotbitcount`. Its compute shader constructs four checks and packs them into the low four bits of `tempResult`:

```glsl
/* Conceptual excerpt reconstructed from the generator. */
uvec4 allOnes = uvec4(0xFFFFFFFF);
uvec4 allZeros = uvec4(0);
uint SubgroupSize = gl_SubgroupSize;

tempResult |= SubgroupSize == subgroupBallotBitCount(allOnes) ? 0x1 : 0;
tempResult |= 0 == subgroupBallotBitCount(allZeros) ? 0x2 : 0;
tempResult |= 0 < subgroupBallotBitCount(subgroupBallot(true)) ? 0x4 : 0;
tempResult |= 0 == subgroupBallotBitCount(MAKE_HIGH_BALLOT_RESULT(SubgroupSize)) ? 0x8 : 0;
```

The all-ones mask must count exactly the active subgroup width, the all-zeros mask must count zero, the ballot of `true` must contain at least one participating invocation, and a mask beginning at `gl_SubgroupSize` must contribute no in-range bits. A successful invocation therefore writes `0xf`.

## End-to-End Test Flow

```text
[host] select one ballot-derived operation, execution family, shader stage, and required-subgroup-size mode
[host] generate GLSL from initPrograms or initFrameBufferPrograms with operation-specific test code
[host] compile the selected stage and create the pipeline, descriptors, and output storage
[host] for required-size compute or mesh cases, iterate powers of two from minSubgroupSize through maxSubgroupSize
[host] dispatch, draw, trace rays, or execute a framebuffer path through the shared subgroup harness
[device] every tested invocation evaluates four operation-specific checks and builds tempResult
[device] write tempResult to an SSBO element, fragment output, or framebuffer output
[host] wait, make shader writes visible, invalidate mapped output memory, and inspect every produced scalar
[host] pass only when every inspected value equals 0xf for every exercised local size and required subgroup size
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- [`getTestString`](../../../modules/vulkan/subgroups/vktSubgroupsBallotOtherTests.cpp#L147-L276) emits the common mask setup and one of seven operation-specific check bodies.
- [`initPrograms`](../../../modules/vulkan/subgroups/vktSubgroupsBallotOtherTests.cpp#L290-L307) selects SPIR-V 1.3 for compute and graphics, or SPIR-V 1.4 for ray tracing and mesh stages, then delegates complete stage generation to `initStdPrograms`.
- [`initFrameBufferPrograms`](../../../modules/vulkan/subgroups/vktSubgroupsBallotOtherTests.cpp#L278-L288) uses SPIR-V 1.3 and delegates framebuffer-stage generation.
- Compute local sizes are specialization constants with IDs 0, 1, and 2. The shared helper combines them with the generated operation body.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Result storage buffer at set 0, binding 0 | yes | yes | device writes one `uint` per tested invocation | yes | Holds the four-bit success mask; every element must be `0xf`. |
| Framebuffer output for no-SSBO stage cases | yes | yes | device writes the scalar result through a stage output | yes | Carries the same `0xf` contract where an SSBO is not used. |
| GLSL ballot values such as `allOnes`, `allZeros`, and `subgroupBallot(true)` | no | no | shader-local values only | no | Supply controlled masks to the operation under test. |
| Compute local-size specialization constants | yes | pipeline configuration | read as execution configuration | no | Exercise the same shader over several workgroup shapes. |

No operation-specific input buffer is used. Expected values are generated in the shader from built-ins and constant masks.

## What Is Checked

Each shader invocation accumulates four independent check bits. The host does not recompute ballot results. It checks the device-generated verdict:

| Result bit | Check class | Required state |
|------------|-------------|----------------|
| `0x1` | all-ones or full-range reference | set |
| `0x2` | all-zeros or elected-invocation special case | set |
| `0x4` | live ballot result or range check | set |
| `0x8` | exhaustive or high-bit boundary check | set |

The final scalar must be `0xf`. Shared callbacks scan the complete output width, or the full compute or mesh invocation volume, and fail on the first value that differs.

## Behavior Parameter Identification

> **Behavior parameter:** operation test case leaf
>
> **Candidate values:** `subgroupinverseballot`, `subgroupballotbitextract`, `subgroupballotbitcount`, `subgroupballotinclusivebitcount`, `subgroupballotexclusivebitcount`, `subgroupballotfindlsb`, `subgroupballotfindmsb`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `subgroupinverseballot` | Incorrect mapping from the current invocation's index to its Boolean bit in a ballot mask. |
| `subgroupballotbitextract` | Incorrect extraction or indexing of one bit from the four-word ballot representation. |
| `subgroupballotbitcount` | Incorrect reduction count, especially at the actual subgroup-size boundary or for bits outside the subgroup. |
| `subgroupballotinclusivebitcount` | Incorrect inclusive prefix boundary or incorrect counting across `uvec4` word boundaries. |
| `subgroupballotexclusivebitcount` | Incorrect exclusive prefix boundary or incorrect counting across `uvec4` word boundaries. |
| `subgroupballotfindlsb` | Incorrect least-significant set-bit search or returned invocation index. |
| `subgroupballotfindmsb` | Incorrect most-significant set-bit search or returned invocation index. |

A failure in any value can also come from shader compilation or stage lowering, result-buffer addressing, synchronization and host visibility, or the shared stage harness. The failing path and result pattern are needed to separate operation semantics from shared infrastructure.

## Important Variations and Special Cases

- **Execution family:** the same seven operation leaves run under `compute`, `graphics`, `framebuffer`, `ray_tracing`, and `mesh`. Ray tracing and mesh are excluded from Vulkan SC builds.
- **Required subgroup size:** compute and mesh cases add `_requiredsubgroupsize` variants. The host tests every power-of-two size in the advertised range after checking subgroup-size-control support and stage eligibility.
- **Shader stage:** graphics and ray-tracing helpers exercise supported stages. Framebuffer leaves explicitly select vertex, tessellation control, tessellation evaluation, or geometry. Mesh leaves select mesh or task.
- **SPIR-V target:** ordinary compute, graphics, and framebuffer shaders use SPIR-V 1.3. Mesh and ray-tracing generation uses SPIR-V 1.4.
- **Undefined empty-mask search is avoided:** find-LSB and find-MSB do not validate an all-zero search result. Their second check handles the elected invocation specially and otherwise searches a nonempty ballot.
- **Issue exclusions:** the applicable Vulkan `test-issues.txt` contains no `ballot_other` exclusion. Its only subgroup entry concerns `subgroup_uniform_control_flow` partial cases.

These variations broaden stage and subgroup-size coverage without changing the primary behavioral axis, which remains the selected ballot-derived operation.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Operation enumeration and names | [`OpType` and `getOpTypeName`](../../../modules/vulkan/subgroups/vktSubgroupsBallotOtherTests.cpp#L41-L97) | Defines the seven exact behavioral values and registered leaf stems. |
| Generated operation checks | [`getTestString`](../../../modules/vulkan/subgroups/vktSubgroupsBallotOtherTests.cpp#L147-L276) | Defines every shader-side pass bit and boundary loop. |
| Representative compute builder | [`initPrograms`](../../../modules/vulkan/subgroups/vktSubgroupsBallotOtherTests.cpp#L290-L307) | Selects build options and delegates compute shader assembly. |
| Registration matrix | [`createSubgroupsBallotOtherTests`](../../../modules/vulkan/subgroups/vktSubgroupsBallotOtherTests.cpp#L458-L569) | Builds execution-family, stage, operation, and required-size paths. |
| Runtime selection and required-size loop | [`test`](../../../modules/vulkan/subgroups/vktSubgroupsBallotOtherTests.cpp#L381-L450) | Routes each family into the shared harness and iterates required subgroup sizes. |
| Compute shader assembly | [`initStdPrograms`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L1406-L1434) | Shows specialization-controlled local size, output addressing, and result write. |
| Host result validation | [`check` and `checkComputeOrMesh`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L2640-L2663) | Proves that every scalar must equal `0xf`. |
| Compute resource, dispatch, and readback flow | [`makeComputeOrMeshTestRequiredSubgroupSize`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L3762-L4063) | Creates the result buffer, binds it, dispatches, synchronizes, invalidates, and calls the checker. |
| Mustpass registration evidence | [`subgroups.txt`](../../../mustpass/main/vk-default/subgroups.txt#L18288-L18371) | Lists the executable `ballot_other` cases. |
| Vulkan ballot model | [`shaders.adoc`](../../../../vulkan-docs/src/chapters/shaders.adoc#L3447-L3523) | Defines subgroup group-operation scope and ballot behavior. |
| Ballot support capability | [`limits.adoc`](../../../../vulkan-docs/src/chapters/limits.adoc#L1428-L1453) | Connects `VK_SUBGROUP_FEATURE_BALLOT_BIT` to `GroupNonUniformBallot`. |
| Bit-count group-operation restriction | [`spirvenv.adoc`](../../../../vulkan-docs/src/appendices/spirvenv.adoc#L608-L611) | Limits ballot bit count to reduction, inclusive scan, and exclusive scan. |
| Subgroup-size control | [`VK_EXT_subgroup_size_control.adoc`](../../../../vulkan-docs/src/appendices/VK_EXT_subgroup_size_control.adoc#L24-L69) | Defines variable and required subgroup-size behavior used by variants. |

## Questions / Risk Points for User Audit

- Does treating the operation test case leaf as the primary behavioral axis match the intended review model?
- Is the distinction among reduction, inclusive scan, and exclusive scan clear enough to explain the expected per-invocation values?
- Is it clear that `0xf` is a device-generated four-check verdict rather than a host-computed ballot reference?
- Should stage-family details remain secondary parameter coverage rather than separate behavior subsections?
- No unresolved source or specification contradiction was found. The main diagnostic limitation is intentional: a shared `0xf` mismatch does not identify which check bit failed unless the observed scalar is inspected.

## Conversion Notes for Final Wiki Rewrite

- Use the operation test case leaf as `## Behavior Parameters`, preserving all seven values and their order.
- Use `dEQP-VK.subgroups.ballot_other.compute.subgroupballotbitcount` for the single representative walkthrough. Its source is `external/vulkancts/modules/vulkan/subgroups/vktSubgroupsBallotOtherTests.cpp`, and its confirmed builder is `initPrograms`.
- Distill ballot masks and count/scan boundaries into compact prerequisite bullets.
- Keep execution family, shader stage, required subgroup size, and SPIR-V target in the parameter matrix and pruning sections.
- Keep the runtime section focused on the shared result buffer, dispatch or draw path, visibility barrier, readback, and all-elements-equal-`0xf` check.
- Copy the `### Failure Cause Mapping` table above directly into the final page without changes.
- Move source navigation to the final appendix and keep issue-file inspection as a pruning note only.
