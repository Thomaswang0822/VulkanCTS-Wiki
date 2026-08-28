# Understanding Brief: `subgroups.ballot`

## One-Sentence Test Purpose

This test checks whether core and legacy subgroup ballot operations return results consistent with the predicates supplied by active invocations across each supported shader execution path.

## Background Knowledge

### Subgroup ballot semantics

A Vulkan subgroup is a set of shader invocations that can communicate efficiently. A ballot operation takes one Boolean predicate from each participating invocation and returns a mask that records those predicate values. The Vulkan specification describes ballot operations as group operations at subgroup scope, and `VK_SUBGROUP_FEATURE_BALLOT_BIT` advertises acceptance of SPIR-V modules with the `GroupNonUniformBallot` capability.

Why it matters here:
- The expected result depends on active subgroup invocations, not on every invocation in the enclosing workgroup or draw.
- `gl_SubgroupInvocationID` identifies the bit position associated with an invocation.
- A ballot of `false` must be zero, while a ballot of `true` or the all-nonzero input predicate must contain set bits for active invocations.

### Core and legacy ballot forms

The core path uses `subgroupBallot` and a four-component 32-bit mask. The legacy `VK_EXT_shader_subgroup_ballot` path enables `GL_ARB_shader_ballot`, uses `ballotARB`, and returns a 64-bit mask that maps to `OpSubgroupBallotKHR`. The extension appendix states that most of this extension was superseded by Vulkan 1.1 subgroup operations.

Why it matters here:
- Both forms implement the same predicate-to-mask idea, but they use different source types, extensions, and SPIR-V instructions.
- The legacy path additionally requires `VK_EXT_shader_subgroup_ballot` and 64-bit integer shader support.

## One Concrete Example

For `dEQP-VK.subgroups.ballot.compute.compute`, the compute shader performs three checks:

1. It compares `subgroupBallot(true)` with a mask independently assembled in shared memory using one atomic bit set per voting invocation.
2. It repeats that comparison for `data[gl_SubgroupInvocationID] != 0`. The host initializes every input element to a nonzero value, so each active invocation votes true.
3. It checks that `subgroupBallot(false)` is zero.

Each successful check contributes one bit to `tempResult`. The expected output is therefore `0x7` for every dispatched invocation.

## End-to-End Test Flow

```text
[host] select the core or legacy ballot form, shader execution path, and optional required subgroup size
[host] reject unsupported subgroup, ballot, stage, extension, int64, ray tracing, mesh, or subgroup-size-control cases
[host] generate GLSL through initPrograms, or use direct SPIR-V assembly for framebuffer cases
[host] create a nonzero uint input buffer and a uint result target
[host] bind descriptors, create the selected pipeline, and submit dispatch or draw work
[device] evaluate true, input-derived, and false ballot predicates
[device] write a three-bit result value for each tested invocation
[host] wait, make shader writes visible, invalidate host mappings, and inspect result data
[host] pass only when every checked result equals 0x7
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `initPrograms` selects SPIR-V 1.3 for compute and graphics cases, and SPIR-V 1.4 for ray tracing and mesh cases.
- `getExtHeader` chooses `GL_KHR_shader_subgroup_ballot` for the core path or `GL_ARB_shader_ballot` plus its required support extensions for the legacy path.
- `getBodySource` emits the three ballot checks. Compute and mesh paths compare the implementation ballot with an independent shared-memory construction. Other generated paths check whether true predicates produce a nonzero mask and `false` produces zero.
- `initStdPrograms` wraps that body in stage-specific GLSL, descriptor declarations, index calculation, and result writes.
- `initFrameBufferPrograms` supplies CTS-authored SPIR-V 1.3 assembly for the vertex, geometry, tessellation control, or tessellation evaluation framebuffer path.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `result` storage buffer or framebuffer output | yes | yes | written | yes | Stores the `0x7` success code for every tested invocation. |
| `data` buffer | yes | yes | read | not for the ballot decision | Contains nonzero `uint` values indexed by `gl_SubgroupInvocationID`. |
| `superSecretComputeShaderHelper` shared array | no | shader-local | read and written | no | Independently builds a reference ballot for compute-like paths using shared atomics. |
| Required subgroup size pipeline state | yes, in required-size cases | pipeline state | controls execution | no | Repeats compute and mesh testing over supported power-of-two subgroup sizes. |

## What Is Checked

- The device writes a three-bit result per tested invocation.
- Bit `0x1` covers the all-true predicate.
- Bit `0x2` covers the input-derived predicate, which is true because input elements are nonzero.
- Bit `0x4` covers the all-false predicate and is set only when its ballot mask is zero.
- Compute and mesh paths require the core or legacy ballot result to equal the independently assembled shared-memory mask for the true predicates.
- Graphics, ray tracing, and framebuffer paths require true-predicate ballot masks to be nonzero and the false-predicate mask to be zero.
- Host callbacks pass only if every scanned value equals `0x7`.

## Behavior Parameter Identification

> **Behavior parameter:** `execution path`
>
> **Candidate values:** `compute`, `graphics`, `framebuffer`, `ray_tracing`, `mesh`
>
> **Second behavior parameter:** `ballot interface`
>
> **Candidate values:** `core`, `ext_shader_subgroup_ballot`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `compute` | Incorrect subgroup ballot mask, shared-memory reference construction, compute specialization/local-size handling, or compute result write/readback. |
| `graphics` | Incorrect ballot behavior in one or more supported graphics stages, stage-specific result indexing, or graphics SSBO result handling. |
| `framebuffer` | Incorrect ballot instruction behavior in the selected vertex-pipeline stage, direct SPIR-V handling, or framebuffer output/readback. |
| `ray_tracing` | Incorrect ballot behavior in one or more supported ray tracing stages, stage-specific result writes, or ray tracing pipeline execution. |
| `mesh` | Incorrect ballot or shared-memory reference behavior in task/mesh execution, local-size or required-subgroup-size handling, or mesh result write/readback. |

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `core` | Incorrect lowering or execution of `subgroupBallot` / `OpGroupNonUniformBallot`, or incorrect reporting of core ballot support. |
| `ext_shader_subgroup_ballot` | Incorrect lowering or execution of `ballotARB` / `OpSubgroupBallotKHR`, 64-bit mask handling, or incorrect extension and `shaderInt64` support behavior. |

## Important Variations and Special Cases

- `compute_requiredsubgroupsize` and the corresponding mesh cases repeat execution for every supported power-of-two size from `minSubgroupSize` through `maxSubgroupSize`. They require subgroup size control, compute full subgroups, and stage support for required subgroup sizes.
- The ordinary compute and mesh cases run several local-size shapes, including sizes smaller than, equal to, and not neatly aligned with the default subgroup size.
- `graphics.graphic` exercises every graphics stage in which the implementation reports subgroup support.
- `ray_tracing.test` similarly covers the supported ray tracing subgroup stages and is absent from Vulkan SC.
- The legacy branch has compute, graphics, framebuffer, and mesh coverage, but no legacy ray tracing case.
- The framebuffer path differs structurally because it uses direct SPIR-V assembly and a uniform input buffer instead of the standard generated SSBO shader path.
- `test-issues.txt` contains no ballot-specific exclusion. Its only subgroup entry concerns partial `subgroup_uniform_control_flow` cases.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Registration and case matrix | [`createSubgroupsBallotTests`](../../../modules/vulkan/subgroups/vktSubgroupsBallotTests.cpp#L1019-L1160) | Defines every direct child and executable ballot path. |
| Generated shader selection | [`initPrograms`](../../../modules/vulkan/subgroups/vktSubgroupsBallotTests.cpp#L809-L828) | Selects extensions, body text, helper text, stages, and SPIR-V target. |
| Ballot body | [`getBodySource`](../../../modules/vulkan/subgroups/vktSubgroupsBallotTests.cpp#L770-L807) | Defines the three result bits and compute-like comparison rule. |
| Shared-memory reference ballot | [`getSharedMemoryBallotHelper`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L867-L895) | Independently constructs the core mask with subgroup-scoped shared atomics. |
| Standard shader wrappers | [`initStdPrograms`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L1406-L1675) | Supplies declarations, stage wrappers, indexing, and result writes. |
| Support gates | [`supportedCheck`](../../../modules/vulkan/subgroups/vktSubgroupsBallotTests.cpp#L830-L889) | Enforces subgroup, ballot, stage, extension, int64, and optional feature requirements. |
| Runtime routing | [`test`](../../../modules/vulkan/subgroups/vktSubgroupsBallotTests.cpp#L920-L1012) | Chooses compute, mesh, graphics, and ray tracing helpers and resources. |
| Result callbacks | [`check` and `checkComputeOrMesh`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L2640-L2663) | Require every observed value to equal `0x7`. |
| Registered mustpass leaves | [`subgroups.txt`](../../../mustpass/main/vk-default/subgroups.txt#L12088-L12110) | Confirms the executable paths included in the default mustpass set. |
| Subgroup and ballot semantics | [`shaders.adoc`](../../../../vulkan-docs/src/chapters/shaders.adoc#L3220-L3247) and [`shaders.adoc`](../../../../vulkan-docs/src/chapters/shaders.adoc#L3447-L3523) | Defines subgroups, group operations, and ballot behavior. |
| Feature and size properties | [`limits.adoc`](../../../../vulkan-docs/src/chapters/limits.adoc#L1326-L1353), [`limits.adoc`](../../../../vulkan-docs/src/chapters/limits.adoc#L1428-L1453), and [`limits.adoc`](../../../../vulkan-docs/src/chapters/limits.adoc#L1492-L1536) | Grounds support and required-subgroup-size claims. |
| Legacy ballot extension | [`VK_EXT_shader_subgroup_ballot.adoc`](../../../../vulkan-docs/src/appendices/VK_EXT_shader_subgroup_ballot.adoc#L21-L79) | Defines legacy mask communication and GLSL-to-SPIR-V mapping. |

## Questions / Risk Points for User Audit

- Is the two-axis behavior model, execution path plus ballot interface, the clearest way to organize this multi-family page?
- Is the difference between exact shared-memory mask comparison and nonzero/zero checking clear enough?
- Does the framebuffer explanation make clear that it uses CTS-authored direct SPIR-V rather than generated GLSL?
- Should the final page keep all execution paths in one compact behavior section, or expand only the compute path used by the representative walkthrough?

All technical questions that affect the representative selection and validation claims were resolved from source, mustpass, helper, and specification evidence. No unresolved semantic blocker remains.

## Conversion Notes for Final Wiki Rewrite

- Use `dEQP-VK.subgroups.ballot.compute.compute` as the representative shader walkthrough because it exercises the core ballot form and the independent shared-memory mask oracle.
- Preserve the two behavior axes exactly: `execution path` and `ballot interface`.
- Copy the `### Failure Cause Mapping` tables unchanged into the final page.
- Distill subgroup and ballot background to the minimum concepts needed for the behavior and failure sections.
- Keep generated wrapper and runtime helper details in the source appendix unless they explain mask construction, result encoding, or case pruning.
